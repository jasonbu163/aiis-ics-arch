"""FF-001 r3 有限公开API预检；保存证据/自然回收之后才断言错误操作必须拒绝。"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import platform
import sqlite3
import sys
import time
from snap7 import Client
from tests.fixtures.public_api import Fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    args.evidence_dir.mkdir()  # Must be a new task-owned directory.
    fixture = Fixture()
    started = time.monotonic()
    try:
        result = fixture.write()
        print(json.dumps({"stage":"api_result", "result":result}),flush=True)
    finally:
        closed = fixture.close()
    source = Path(inspect.getfile(Client))
    writes = [row for row in fixture.records if row["writevar"]]
    assert len(writes) == 1
    evidence = {"task": "FF-001", "revision": "r3", "case": "matching-ref-wrong-function",
                "implementation": "python public API candidate precheck only; runtime/state/T3 not implemented",
                "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
                "python_snap7": importlib.metadata.version("python-snap7"),
                "sqlite3_version": sqlite3.sqlite_version,
                "client_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "result": result, "actual_writevar_count": len(writes), "protocol": fixture.records,
                "closed": closed, "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
                "neighbors_preserved": closed["memory_hex"] == "002a" + "a5" * 14}
    target = args.evidence_dir / "python-api-preflight.json"
    target.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence), flush=True)
    assert not result["returned_success"], "AC15: wrong operation ACK must not be accepted as write success"


if __name__ == "__main__":
    main()
