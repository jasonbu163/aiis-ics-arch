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
    for action in ('status','adopt','cleanup'):
        sub=subs.add_parser(action)
        if action!='status':
            mode=sub.add_mutually_exclusive_group(required=True)
            mode.add_argument('--plan',action='store_true'); mode.add_argument('--apply',action='store_true')
        for name in ('target-alias','schema','expected-schema-revision','expected-storage-epoch','operation-approval','confirmed-by'):
            sub.add_argument('--'+name,required=True)
        sub.add_argument('--expected-adoption-id')
        sub.add_argument('--confirm')
        sub.add_argument('--output-log',type=Path)
        if action=='adopt':
            sub.add_argument('--revalidate-schema-only',action='store_true')
            for name in ('plc-id','instance-id','source-generation','config-revision','context-sha256'): sub.add_argument('--'+name)
            sub.add_argument('--context-file',type=Path)
            for name in ('expected-binding-revision','seq-from','old-seq-through'): sub.add_argument('--'+name,type=int)
            sub.add_argument('--retention-months',type=int,default=3)
            sub.add_argument('--max-value-bytes',type=int,default=1073741824)
            sub.add_argument('--max-proof-rows',type=int,default=1000000)
    return p


def main(argv=None):
    p=parser(); args=p.parse_args(argv)
    if not args.action: p.print_help(); return 0
    # Import only after explicit command/target; these commands all need separate runtime approval.
    backend=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(backend))
    from pydantic_settings import BaseSettings,SettingsConfigDict
    class ToolSettings(BaseSettings):
        model_config=SettingsConfigDict(env_file=(backend/'.env',Path(__file__).resolve().parent/'.env'),extra='ignore')
        PLC_FACTS_MAINTENANCE_ENABLED: bool=False
    tool=ToolSettings()
    apply=bool(getattr(args,'apply',False)); expected='APPLY:'+args.action+':'+args.target_alias+':'+args.schema+':'+args.expected_storage_epoch
    started=time.monotonic()
    def output(event,**data):
        line=json.dumps(dict(event=event,targetAlias=args.target_alias,schema=args.schema,action=args.action,elapsedMs=int((time.monotonic()-started)*1000),**data),ensure_ascii=False,separators=(',',':'))
        print(line)
        if args.output_log:
            with args.output_log.open('a',encoding='utf-8') as stream: stream.write(line+'\n')
    output('start',apply=apply)
    try:
        if apply and (not tool.PLC_FACTS_MAINTENANCE_ENABLED or args.confirm!=expected): raise ValueError('explicit maintenance enable and exact confirmation required')
        # Tool dotenv overrides backend dotenv; process env retains highest precedence for credentials.
        from dotenv import dotenv_values
        merged={}
        for file in (backend/'.env',Path(__file__).resolve().parent/'.env'):
            if file.exists(): merged.update({k:v for k,v in dotenv_values(file).items() if v is not None})
        for k,v in merged.items(): os.environ.setdefault(k,v)
        from app.plc_facts.services.sync_maintenance import execute,MaintenanceOptions
        kwargs={k:v for k,v in vars(args).items() if k not in ('plan','confirm','output_log','context_file','apply')}
        if getattr(args,'context_file',None):
            if args.context_file.stat().st_size>1024*1024: raise ValueError('context too large')
            kwargs['context_utf8']=args.context_file.read_text(encoding='utf-8')
        result=execute(MaintenanceOptions(apply=apply,**kwargs))
        output('commit' if apply else 'dry-run',result=result)
        output('complete',status='ok'); return 0
    except Exception:
        # No traceback, SQL, DSN, values, source context or token in terminal evidence.
        output('failed',status='failed',errorCode='plc_facts.maintenance_failed')
        output('complete',status='failed'); return 1

if __name__=='__main__': raise SystemExit(main())
