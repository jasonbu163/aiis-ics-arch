"""CLI空目录无副作用、严格配置/来源时间与只读状态边界。"""
from dataclasses import asdict
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import pytest
from field_flow.config import parse
from field_flow.domain import Clock, Failure, parse_input, now_ms
from field_flow.infrastructure.state import init, inspect
from tests.test_matched_ack_gate import config


def test_help_and_init():
    root = Path(tempfile.mkdtemp(prefix="ff-001-r1-r4-python-cli-", dir="/private/tmp"))
    for args in ([], ["--lang", "zh-CN", "--help"], ["--lang", "en-US", "--help"]):
        result = subprocess.run([sys.executable, "-m", "field_flow", *args], cwd=root, capture_output=True, timeout=3)
        assert result.returncode == 0 and not list(root.iterdir())
    for args in (["unknown"], ["run"], ["run", "--config", "missing", "--state-dir", "missing"], ["--lang", "xx"], ["state", "init", "--synthetic"]):
        assert subprocess.run([sys.executable, "-m", "field_flow", *args], cwd=root, capture_output=True, timeout=3).returncode == 2
        assert not list(root.iterdir())
    init(root/"state", "execute", "test")
    before = (root/"state/state.sqlite").read_bytes()
    with pytest.raises(Failure): init(root/"state", "execute", "test")
    assert before == (root/"state/state.sqlite").read_bytes()
    assert inspect(root/"state")["meta"]["implementation"] == "python"


def test_config_rejections():
    data = asdict(config()); data["plcs"] = list(data["plcs"]); data["flows"] = list(data["flows"])
    mutations = [lambda d: d.update(extra=1), lambda d: d.pop("http"), lambda d: d.update(schema_version=True),
        lambda d: d["plcs"].append(copy.deepcopy(d["plcs"][0])),
        lambda d: d["plcs"].append({**d["plcs"][0], "id": "alias"}),
        lambda d: d["flows"].append({**d["flows"][0], "id": "overlap"}),
        lambda d: d["plcs"][0].update(host="localhost"), lambda d: d["plcs"][0].update(port=0),
        lambda d: d["plcs"][0].update(io_timeout_ms="5000"), lambda d: d["plcs"][0].update(io_timeout_ms=5001),
        lambda d: d["plcs"][0].update(queue_capacity=17), lambda d: d.update(shutdown_timeout_ms=10000),
        lambda d: d["http"].update(connect_timeout_ms=1501), lambda d: d["http"].update(total_timeout_ms=100),
        lambda d: d["flows"][0].update(kind="demo02"), lambda d: d["flows"][0].update(id="bad.dot"),
        lambda d: d["flows"][0]["target"].update(byte_offset=15), lambda d: d["flows"][0]["target"].update(type="BOOL"),
        lambda d: d["flows"].append("invalid"), lambda d: d["flows"][0].update(get_url="http://user:pass@localhost/")]
    for change in mutations:
        bad = copy.deepcopy(data); change(bad)
        with pytest.raises(Failure): parse(bad)


def test_time_and_input():
    c = config(); wall = now_ms()
    good = dict(schema_version=1, source_id="demo01-feed", ready=True, command_id="test", value=42, issued_at_ms=wall, expires_at_ms=wall+5000)
    for changes in ({"ready": 1}, {"value": True}, {"value": 42.0}, {"value": "42"}, {"value": 32768}, {"value": -32769},
                    {"issued_at_ms": wall+2000}, {"expires_at_ms": wall-1}, {"expires_at_ms": wall+60001}, {"source_id": "other"}, {"extra": 1}):
        with pytest.raises(Failure): parse_input({**good, **changes}, c.flows[0], c.plcs[0])
    assert parse_input(good, c.flows[0], c.plcs[0]).value == 42
    clock = Clock()
    with pytest.raises(Failure, match="clock_invalid"): clock.check(wall-2000)
    with pytest.raises(Failure, match="clock_invalid"): clock.check(now_ms())


def test_state_identity_lock_and_no_implicit_schema():
    import asyncio
    import sqlite3
    from field_flow.infrastructure.state import State
    root = Path(tempfile.mkdtemp(prefix="ff-001-r1-r4-python-state-", dir="/private/tmp"))
    async def scenario():
        with pytest.raises(Failure): await State.open(root/"missing", "execute", "test")
        assert not (root/"missing").exists()
        init(root/"actual", "execute", "test")
        first = await State.open(root/"actual", "execute", "test")
        with pytest.raises(Failure, match="state_locked"): await State.open(root/"actual", "execute", "test")
        import time
        await first.close(time.monotonic()+2)
        for mode, instance in (("dry_run", "test"), ("execute", "other")):
            with pytest.raises(Failure, match="state_identity"): await State.open(root/"actual", mode, instance)
        db = sqlite3.connect(root/"actual/state.sqlite"); db.execute("UPDATE store_meta SET schema_version=2"); db.commit(); db.close()
        before = (root/"actual/state.sqlite").read_bytes()
        with pytest.raises(Failure, match="state_identity"): await State.open(root/"actual", "execute", "test")
        assert (root/"actual/state.sqlite").read_bytes() == before
    asyncio.run(scenario())
