"""一次性PLC facts维护CLI；裸运行/--help在加载settings或DB前退出。"""
import argparse
import json
import os
from pathlib import Path
import sys
import time


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    subs=p.add_subparsers(dest='action')
    sub=subs.add_parser('cleanup-v2')
    mode=sub.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan',action='store_true'); mode.add_argument('--apply',action='store_true')
    for name in ('target-alias','schema','expected-server-uuid','expected-schema-revision','operation-approval','confirmed-by'):
        sub.add_argument('--'+name,required=True)
    sub.add_argument('--confirm')
    sub.add_argument('--output-log',type=Path)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.plc_facts_maintenance.source_registry import configure_parser
    configure_parser(subs)
    return p


def main(argv=None):
    p=parser(); args=p.parse_args(argv)
    if not args.action: p.print_help(); return 0
    # Import only after explicit command/target; these commands all need separate runtime approval.
    backend=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(backend))
    if args.action in ('import-sources', 'export-sources'):
        print(json.dumps({'event': 'legacy-source-command', 'status': 'failed',
                          'message': 'Use the frozen r2 maintenance source before the r3 migration.'}))
        return 1
    from pydantic_settings import BaseSettings,SettingsConfigDict
    class ToolSettings(BaseSettings):
        model_config=SettingsConfigDict(env_file=(backend/'.env',Path(__file__).resolve().parent/'.env'),extra='ignore')
        PLC_FACTS_MAINTENANCE_ENABLED: bool=False
    tool=ToolSettings()
    apply=bool(getattr(args,'apply',False))
    expected='APPLY:cleanup-v2:'+args.target_alias+':'+args.schema+':'+args.expected_server_uuid+':'+args.expected_schema_revision
    started=time.monotonic()
    def output(event,**data):
        line=json.dumps(dict(event=event,targetAlias=args.target_alias,schema=args.schema,action=args.action,elapsedMs=int((time.monotonic()-started)*1000),**data),ensure_ascii=False,separators=(',',':'))
        print(line)
        if args.output_log:
            with args.output_log.open('a',encoding='utf-8') as stream: stream.write(line+'\n')
    output('start',apply=apply)
    try:
        if any(not value.strip() for value in (args.operation_approval,args.confirmed_by)):
            raise ValueError('approval and confirmer are required')
        if apply and (not tool.PLC_FACTS_MAINTENANCE_ENABLED or args.confirm!=expected): raise ValueError('explicit maintenance enable and exact confirmation required')
        # Tool dotenv overrides backend dotenv; process env retains highest precedence for credentials.
        from dotenv import dotenv_values
        merged={}
        for file in (backend/'.env',Path(__file__).resolve().parent/'.env'):
            if file.exists(): merged.update({k:v for k,v in dotenv_values(file).items() if v is not None})
        for k,v in merged.items(): os.environ.setdefault(k,v)
        from app.plc_facts.v2_config import V2Settings,load_profile
        from app.plc_facts.services.sync_v2_maintenance import run
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from sqlalchemy.pool import NullPool
        from settings import settings
        target=load_profile(V2Settings())['target']
        expected_target={'alias':args.target_alias,'schema':args.schema,'serverUuid':args.expected_server_uuid,'schemaRevision':args.expected_schema_revision}
        if target!=expected_target: raise ValueError('target mismatch')
        engine=create_engine(settings.SYNC_DATABASE_URL,poolclass=NullPool,
                             connect_args={'connect_timeout':2,'read_timeout':2,'write_timeout':2})
        db=Session(engine,expire_on_commit=False,autoflush=False)
        try:
            result=run(db,target,apply)
        finally:
            try:
                db.close()
            finally:
                engine.dispose()
        output('commit' if apply else 'dry-run',result=result)
        output('complete',status='ok'); return 0
    except Exception:
        # No traceback, SQL, DSN, values, source context or token in terminal evidence.
        output('failed',status='failed',errorCode='plc_facts.maintenance_failed')
        output('complete',status='failed'); return 1

if __name__=='__main__': raise SystemExit(main())
