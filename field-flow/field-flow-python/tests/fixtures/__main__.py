"""显式本机夹具命令；无参/help只读自身locale，不创建服务。"""
import json
from pathlib import Path
import signal
import sys
import threading
from field_flow.cli import locale
from field_flow.config import load
from tests.fixtures.runtime import Fixture


def main():
    if not sys.argv[1:] or sys.argv[1:] == ["--help"]:
        print(locale("en-US")["fixture_help"]); return 0
    args = sys.argv[1:]
    if len(args) != 4 or args[0] != "--config" or args[2] != "--evidence-dir":
        return 2
    c = load(args[1])
    if [(p.host, p.port) for p in c.plcs] != [("127.0.0.1", 32102)]: return 2
    root = Path(args[3]); root.mkdir()
    if any(f.target.db_number != 1 or f.target.db_size_bytes != 16 or f.target.byte_offset+2 > 16 for f in c.flows): return 2
    fixture = Fixture(); done = threading.Event()
    from field_flow.domain import identity
    fixture.command("fixture-"+identity(), 42)
    fixture.body["source_id"] = c.flows[0].source_id
    for sig in (signal.SIGINT, signal.SIGTERM): signal.signal(sig, lambda *_: done.set())
    print(json.dumps({"event": "fixture_ready", "implementation": "python"}), flush=True)
    try: done.wait()
    finally: (root/"report.json").write_text(json.dumps(fixture.close(), indent=2)+"\n")
    return 0


if __name__ == "__main__": raise SystemExit(main())
