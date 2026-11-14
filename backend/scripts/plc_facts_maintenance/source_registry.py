"""显式预览和导入旧 PLC 来源文件到已迁移的独立登记表。"""
import hashlib
import json
from pathlib import Path
import sys
import time


def configure_parser(subs):
    parser = subs.add_parser('import-sources')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan', action='store_true')
    mode.add_argument('--apply', action='store_true')
    for name in ('target-alias', 'schema', 'expected-server-uuid', 'expected-schema-revision',
                 'operation-approval', 'confirmed-by', 'source-file'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--expected-source-sha256')
    parser.add_argument('--generation-file')
    parser.add_argument('--confirm')
    parser.add_argument('--output-log', type=Path)
    export = subs.add_parser('export-sources')
    for name in ('target-alias', 'schema', 'expected-server-uuid', 'expected-schema-revision',
                 'operation-approval', 'confirmed-by', 'restore-alias', 'restore-schema', 'restore-server-uuid',
                 'output-file'):
        export.add_argument('--' + name, required=True)


def export_main(args, backend):
    """只读数据库并独占创建仓外私有文件；不更改目标或输出登记正文到日志。"""
    import os
    sys.path.insert(0, str(backend))
    try:
        if not args.operation_approval.strip() or not args.confirmed_by.strip():
            raise ValueError('approval and confirmer required')
        path = Path(args.output_file)
        parent = path.parent.resolve(strict=True)
        if not path.is_absolute() or parent.is_relative_to(backend.parent.resolve()) or path.exists() or path.is_symlink():
            raise ValueError('new private output file required')
        from dotenv import dotenv_values
        for file in (backend / '.env', Path(__file__).parent / '.env'):
            if file.exists():
                for key, value in dotenv_values(file).items():
                    if value is not None:
                        os.environ.setdefault(key, value)
        from app.plc_facts.v2_config import LEGACY_REVISION, V2Settings, load_profile
        from app.plc_facts.services.sync_source_registry_import import export
        from settings import settings
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from sqlalchemy.pool import NullPool
        target = load_profile(V2Settings())['target']
        expected = {'alias':args.target_alias, 'schema':args.schema, 'serverUuid':args.expected_server_uuid,
                    'schemaRevision':args.expected_schema_revision}
        if target != expected:
            raise ValueError('target mismatch')
        restore = {'alias':args.restore_alias, 'schema':args.restore_schema,
                   'serverUuid':args.restore_server_uuid, 'schemaRevision':LEGACY_REVISION}
        engine = create_engine(settings.SYNC_DATABASE_URL, poolclass=NullPool,
                               connect_args={'connect_timeout':2,'read_timeout':2,'write_timeout':2})
        try:
            with Session(engine, expire_on_commit=False, autoflush=False) as db:
                result = export(db, target, restore)
                db.rollback()
        finally:
            engine.dispose()
        raw = (json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
        fd = os.open(parent / path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({'event':'export-complete','status':'ok','sha256':hashlib.sha256(raw).hexdigest(),
                          'summary':result['summary']}, ensure_ascii=False))
        return 0
    except Exception:
        print(json.dumps({'event':'export-failed','status':'failed','errorCode':'acquisition_sources.export_failed'}))
        return 1


def main(args, backend):
    started = time.monotonic()

    def output(event, **data):
        line = json.dumps({'event': event, 'action': args.action, 'targetAlias': args.target_alias,
                           'schema': args.schema, 'elapsedMs': int((time.monotonic() - started) * 1000),
                           **data}, separators=(',', ':'), ensure_ascii=False)
        print(line)
        if args.output_log:
            with args.output_log.open('a', encoding='utf-8') as stream:
                stream.write(line + '\n')

    output('start', apply=args.apply)
    sys.path.insert(0, str(backend))
    from app.plc_facts.services.sync_source_registry_import import ImportCommitUnknown
    try:
        from dotenv import dotenv_values
        import os
        from pydantic_settings import BaseSettings, SettingsConfigDict
        class ToolSettings(BaseSettings):
            model_config = SettingsConfigDict(env_file=(backend / '.env', Path(__file__).parent / '.env'), extra='ignore')
            PLC_FACTS_MAINTENANCE_ENABLED: bool = False

        if not args.operation_approval.strip() or not args.confirmed_by.strip():
            raise ValueError('approval and confirmer required')
        source = Path(args.source_file)
        if not source.is_absolute() or source.is_symlink() or source.resolve().is_relative_to(backend.parent):
            raise ValueError('private source required')
        payload = source.read_bytes()
        if len(payload) > 1024 * 1024:
            raise ValueError('source too large')
        source_hash = hashlib.sha256(payload).hexdigest()
        generation_hash = None
        generation_payload = None
        if args.generation_file:
            generation_file = Path(args.generation_file)
            if not generation_file.is_absolute() or generation_file.is_symlink() or generation_file.resolve().is_relative_to(backend.parent):
                raise ValueError('private generation export required')
            generation_payload = generation_file.read_bytes()
            if len(generation_payload) > 16 * 1024 * 1024:
                raise ValueError('generation export too large')
            generation_hash = hashlib.sha256(generation_payload).digest()
        if args.apply:
            expected = f'IMPORT:{args.target_alias}:{args.schema}:{args.expected_server_uuid}:{source_hash}'
            if generation_hash is not None:
                expected += ':' + generation_hash.hex()
            if (not ToolSettings().PLC_FACTS_MAINTENANCE_ENABLED or args.confirm != expected
                    or args.expected_source_sha256 != source_hash):
                raise ValueError('explicit confirmation and preview digest required')
        for file in (backend / '.env', Path(__file__).parent / '.env'):
            if file.exists():
                for key, value in dotenv_values(file).items():
                    if value is not None:
                        os.environ.setdefault(key, value)
        from app.plc_facts.v2_config import V2Settings, _unique_pairs, load_profile, parse_profile
        from app.plc_facts.services.sync_source_registry_import import run
        from settings import settings
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from sqlalchemy.pool import NullPool
        profile = parse_profile(json.loads(payload.decode('utf-8'), object_pairs_hook=_unique_pairs))
        exported = json.loads(generation_payload.decode('utf-8'), object_pairs_hook=_unique_pairs) if generation_payload is not None else None
        target = load_profile(V2Settings())['target']
        expected_target = {'alias': args.target_alias, 'schema': args.schema,
                           'serverUuid': args.expected_server_uuid, 'schemaRevision': args.expected_schema_revision}
        if target != expected_target:
            raise ValueError('target mismatch')
        engine = create_engine(settings.SYNC_DATABASE_URL, poolclass=NullPool,
                               connect_args={'connect_timeout': 2, 'read_timeout': 2, 'write_timeout': 2})
        with Session(engine, expire_on_commit=False, autoflush=False) as db:
            try:
                result = run(db, target, profile, bytes.fromhex(source_hash), args.apply, exported, generation_hash)
            finally:
                try:
                    db.rollback()
                except Exception:
                    pass
                engine.dispose()
        output('commit' if args.apply else 'dry-run', result=result)
        output('complete', status='ok')
        return 0
    except ImportCommitUnknown:
        output('commit-unknown', status='unknown', errorCode='acquisition_sources.import_commit_unknown',
               nextAction='Run the same import-sources --plan with the original source and target; inspect the initialization marker and current summary before retrying.')
        output('complete', status='unknown')
        return 2
    except Exception:
        output('failed', status='failed', errorCode='acquisition_sources.import_failed')
        output('complete', status='failed')
        return 1
