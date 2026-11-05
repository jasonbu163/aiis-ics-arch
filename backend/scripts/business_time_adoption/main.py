"""有限业务时间只读调查/计划/复核CLI；裸入口只help，不隐式读取env或连接目标。"""
from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
import time


def emit(event, **fields):
    print(json.dumps(dict(event=event, **fields), ensure_ascii=False, sort_keys=True))


def digest(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read_json(path):
    if not path or not Path(path).is_absolute():
        raise ValueError("explicit absolute JSON path required")
    with Path(path).open("rb") as stream:
        raw=stream.read(1048577)
    if len(raw)>1048576:
        raise ValueError("report exceeds limit")
    return json.loads(raw)


def parser():
    result=argparse.ArgumentParser(description="Read-only fixed business-time inspect/plan/verify; no apply or SQL proxy")
    result.add_argument("operation", nargs="?", choices=("inspect", "plan", "verify"))
    result.add_argument("--module", choices=("equipment", "performance", "monitor"))
    result.add_argument("--env-file", help="Explicit tool target env, absolute path; no backend dotenv fallback")
    result.add_argument("--output", help="Explicit absolute private JSON report path")
    result.add_argument("--inspection-report")
    result.add_argument("--classification-report")
    result.add_argument("--source-revision")
    return result


def config(path):
    """CLI/env precedence: explicit file plus dedicated process keys; no backend settings import."""
    import os
    if not path or not Path(path).is_absolute():
        raise ValueError("explicit absolute target env required")
    allowed={"BUSINESS_TIME_DB_HOST","BUSINESS_TIME_DB_PORT","BUSINESS_TIME_DB_USER","BUSINESS_TIME_DB_PASSWORD","BUSINESS_TIME_DB_SCHEMA"}
    values={}
    for line in Path(path).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value=line.partition("=")
        if not separator or key not in allowed:
            raise ValueError("unknown tool configuration")
        values[key]=value.strip().strip("\"'")
    values.update({key:os.environ[key] for key in allowed if key in os.environ})
    if set(values)!=allowed or any(not value for value in values.values()):
        raise ValueError("incomplete target configuration")
    return values


def load_owner(module):
    # Only declared module exports; no arbitrary Python path, SQL or column selector.
    from importlib import import_module
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
    import ast
    # Read literal exports without composing backend Settings or reading backend dotenv.
    tree=ast.parse((Path(__file__).resolve().parents[2]/"app"/module/"manifest.py").read_text())
    call=next(node.value for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="manifest" for t in node.targets))
    exports=ast.literal_eval(next(keyword.value for keyword in call.keywords if keyword.arg=="exports"))
    prefix="app."+module
    profile_export=prefix+".integration_storage:BUSINESS_TIME_COLUMN_PROFILE"
    probe_export=prefix+".crud.sync_integration:probe_storage"
    if profile_export not in exports or probe_export not in exports:
        raise ValueError("owner maintenance export unavailable")
    profile=import_module(prefix+".integration_storage").BUSINESS_TIME_COLUMN_PROFILE
    probe=import_module(prefix+".crud.sync_integration").probe_storage
    return profile,probe


def inspect_target(module, filename, source_revision):
    values=config(filename)
    profile,probe=load_owner(module)
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import URL
    from sqlalchemy.orm import Session
    engine=create_engine(URL.create("mysql+pymysql",username=values["BUSINESS_TIME_DB_USER"],password=values["BUSINESS_TIME_DB_PASSWORD"],
        host=values["BUSINESS_TIME_DB_HOST"],port=int(values["BUSINESS_TIME_DB_PORT"]),database=values["BUSINESS_TIME_DB_SCHEMA"]),pool_pre_ping=False)
    try:
        with Session(engine,autoflush=False) as db:
            # Transaction read-only is an explicit tool boundary, not a global session TZ change.
            db.execute(text("SET TRANSACTION READ ONLY"))
            target=probe(db)
            columns={}
            for table, fields in profile["columns"].items():
                metadata=list(db.execute(text("SELECT COLUMN_NAME, DATA_TYPE, DATETIME_PRECISION, COLUMN_DEFAULT, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table"),{"table":table}).mappings())
                by_name={row["COLUMN_NAME"]:dict(row) for row in metadata}
                if any(field not in by_name for field in fields):
                    raise ValueError("fixed target column missing")
                # Fixed owner identifiers only; no caller-supplied SQL/table/column names.
                rows=db.execute(text("SELECT id, "+", ".join(fields)+" FROM "+table+" ORDER BY id")).mappings()
                checksums={field:sha256() for field in fields}
                counts={field:{"rows":0,"nulls":0} for field in fields}
                for row in rows:
                    for field in fields:
                        value=row[field]
                        counts[field]["rows"]+=1
                        counts[field]["nulls"]+=int(value is None)
                        encoded=json.dumps([row["id"],value.isoformat() if hasattr(value,"isoformat") else value],separators=(",",":")).encode()
                        checksums[field].update(len(encoded).to_bytes(8,"big")+encoded)
                for field in fields:
                    columns[table+"."+field]=dict(counts[field],digest="sha256:"+checksums[field].hexdigest(),metadata=by_name[field],basis="unknown")
            db.rollback()
            return dict(version="business-time-inspection/v1",module=module,sourceRevision=source_revision,
                target=dict(serverUuid=target.server_uuid,schema=target.schema,schemaRevision=target.schema_revision),
                utcNow=target.utc_now.isoformat(),fixedColumnDigest=profile["digest"],columns=columns,state="candidate")
    finally:
        engine.dispose()


def plan(inspection, classification):
    if inspection.get("state")!="candidate" or classification.get("version")!="business-time-classification/v1":
        raise ValueError("invalid candidate/classification report")
    supplied=classification.get("columns",{})
    if set(supplied)!=set(inspection["columns"]):
        raise ValueError("classification must cover all fixed columns")
    unknown=[]
    for key,source in supplied.items():
        if source.get("basis") not in ("utc_wall","shanghai_wall","known_offset","unknown") or source.get("coveredRows")!=inspection["columns"][key]["rows"] or not source.get("evidenceRef"):
            raise ValueError("incomplete source coverage")
        if source["basis"]=="unknown":
            unknown.append(key)
    return dict(version="business-time-plan/v1",module=inspection["module"],target=inspection["target"],
        fixedColumnDigest=inspection["fixedColumnDigest"],inspectionDigest=digest(inspection),classificationDigest=digest(classification),
        unknownColumns=unknown,adoptionEligible=False,state="candidate",
        nextGate="separately approved data-only conversion, exact row/key/pair proofs, compatibility and Owner adoption approval")


def main(argv=None):
    argparser=parser()
    args=argparser.parse_args(argv)
    if args.operation is None:
        argparser.print_help()
        return 0
    started=time.monotonic()
    emit("business_time_started",operation=args.operation,module=args.module)
    try:
        if not args.module or not args.output or not Path(args.output).is_absolute() or not args.source_revision:
            raise ValueError("module/source revision/absolute output required")
        if args.operation=="plan":
            report=plan(read_json(args.inspection_report),read_json(args.classification_report))
        else:
            report=inspect_target(args.module,args.env_file,args.source_revision)
            if args.operation=="verify":
                previous=read_json(args.inspection_report)
                if previous.get("target")!=report["target"] or previous.get("fixedColumnDigest")!=report["fixedColumnDigest"]:
                    raise ValueError("verification target/profile mismatch")
                report["comparison"]={key:dict(beforeDigest=previous["columns"][key]["digest"],afterDigest=value["digest"],rowsPreserved=previous["columns"][key]["rows"]==value["rows"]) for key,value in report["columns"].items()}
                report["adoptionEligible"]=False
                report["nextGate"]="time basis cannot be inferred from numeric timestamps; independent compatibility and Owner adoption approval required"
        if report.get("module")!=args.module:
            raise ValueError("report owner mismatch")
        with Path(args.output).open("x") as stream:
            json.dump(report,stream,ensure_ascii=False,sort_keys=True,indent=2,default=str)
            stream.write("\n")
        emit("business_time_complete",operation=args.operation,module=args.module,state="candidate",reportDigest=digest(report),elapsedSeconds=round(time.monotonic()-started,3))
        return 0
    except Exception:
        emit("business_time_failed",operation=args.operation,module=args.module,errorCode="business_time.invalid_or_unavailable",elapsedSeconds=round(time.monotonic()-started,3))
        return 1


if __name__=="__main__":
    sys.exit(main())
