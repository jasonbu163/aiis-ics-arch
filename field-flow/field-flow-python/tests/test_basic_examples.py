"""FF-005：正式CLI/配置与自身Fixture的有界案例矩阵；原身份只生成一次。"""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

import pytest
from snap7 import Client
from field_flow.config import load
from field_flow.infrastructure.s7_int_pdu import request, validate
from field_flow.infrastructure.state import inspect
from tests.fixtures.runtime import Fixture

PROJECT = Path(__file__).resolve().parents[1]
CLI = Path(sys.executable).parent / "field-flow"
START = time.monotonic()


@pytest.fixture(scope="module")
def evidence():
    supplied = os.environ.get("FF005_EVIDENCE_ROOT")
    root = Path(supplied) if supplied else Path(tempfile.mkdtemp(prefix="ff-005-r1-python-", dir="/private/tmp"))
    if supplied:
        root.mkdir(parents=True, exist_ok=True)
        assert not list(root.iterdir()), "use a new empty FF005_EVIDENCE_ROOT"
    print(json.dumps({"ff005_evidence": str(root)}))
    return root


def cli(args, directory, label):
    command = [str(CLI), *map(str, args)]
    out = subprocess.run(command, cwd=PROJECT, capture_output=True, timeout=4)
    (directory/(label+".stdout")).write_bytes(out.stdout)
    (directory/(label+".stderr")).write_bytes(out.stderr)
    return {"command": command, "exit_code": out.returncode, "stdout": out.stdout.decode(), "stderr": out.stderr.decode()}


def wait_for(predicate, parent, seconds=8):
    end = time.monotonic()+seconds
    while not predicate():
        assert parent.poll() is None, "product exited before observation"
        assert time.monotonic() < end, "bounded observation deadline"
        time.sleep(.01)


def absent(pid):
    assert isinstance(pid, int) and pid > 0
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False



def assert_no_forced_driver_stop(rows):
    """解析真实JSON字段；不让空白格式或已消失PID掩盖强收。"""
    assert not any(row.get("event") == "forced_driver_stop" or
                   row.get("had_forced_driver_stop") is True for row in rows), "forced driver cleanup"
    reaped = [row for row in rows if row.get("event") == "driver_process_reaped"]
    assert all(row.get("exit_code") == 0 for row in reaped), "driver did not exit normally"


def test_forced_driver_stop_json_formats():
    for separators in ((",", ":"), (", ", ": ")):
        for row in ({"event": "forced_driver_stop"},
                    {"event": "stop_joined", "had_forced_driver_stop": True},
                    {"event": "driver_process_reaped", "exit_code": -15}):
            decoded = json.loads(json.dumps(row, separators=separators))
            with pytest.raises(AssertionError):
                assert_no_forced_driver_stop([decoded])
        harmless = [{"event": "stop_joined", "had_forced_driver_stop": False},
                    {"event": "driver_process_reaped", "exit_code": 0},
                    {"event": "diagnostic", "message": "forced_driver_stop"}]
        assert_no_forced_driver_stop([json.loads(json.dumps(row, separators=separators)) for row in harmless])


def memory(seed=None):
    """仅准备/停止后的独立核验窗口；不计入产品IO。"""
    client = Client()
    try:
        client.connect("127.0.0.1", 0, 1, tcp_port=32102)
        if seed is not None:
            validate(client.iso_exchange_buffer(request(2, 1, 0, seed)), 2, 5)
        return b"".join(validate(client.iso_exchange_buffer(request(i+3, 1, i*2)), i+3, 4).value.to_bytes(2, "big", signed=True) for i in range(8)).hex()
    finally:
        client.disconnect()


def scenario(root, case, mode, value=42, variant="value", seed=None):
    started = time.monotonic()
    directory = root/f"{case}-{mode}-{variant}-{value}-{seed}"
    directory.mkdir()
    config = PROJECT/"config"/("loopback.yaml" if case == "basic01" else case+".yaml")
    c = load(config)
    init = cli(["state", "init", "--synthetic", "--mode", mode, "--state-dir", directory/"state", "--instance-id", c.instance_id], directory, "init")
    assert init["exit_code"] == 0
    fixture = Fixture()
    parent = None
    report = {"case": case, "mode": mode, "variant": variant, "init": init, "config": str(config), "result": "failed"}
    output = (directory/"product.jsonl").open("wb")
    error = (directory/"product.stderr").open("wb")
    try:
        if seed is not None:
            memory(seed)
        preparation = fixture.snapshot()
        if variant != "idle":
            fixture.command("ff005-command", value)
            if variant == "invalid":
                fixture.body["value"] = "42"
            if variant == "expired":
                fixture.body["issued_at_ms"] -= 2000
                fixture.body["expires_at_ms"] = fixture.body["issued_at_ms"]+1000
        original = dict(fixture.body)
        if variant == "unknown":
            fixture.delay = .3
        if variant == "read_error":
            fixture.fault = "short_data"
        command = [str(CLI), "run", "--config", str(config), "--state-dir", str(directory/"state")] + (["--execute"] if mode == "execute" else [])
        parent = subprocess.Popen(command, cwd=PROJECT, stdout=output, stderr=error)
        report.update(command=command, product_pid=parent.pid, fixture_pid=fixture.server.pid, input=original, preparation=preparation)
        if variant == "unknown":
            wait_for(lambda: fixture.gets == 1, parent)
            fixture.fault = "short_data"
            wait_for(lambda: fixture.writes == 1, parent)
            fixture.fault = ""
            wait_for(lambda: inspect(directory/"state")["counts"].get("unknown") == 1, parent)
            before = fixture.reads
            wait_for(lambda: fixture.reads >= before+10, parent)
        allowed = variant == "value" and not (case == "basic03" and (value <= 0 or value > 100)) and not (case == "basic02" and seed == 0)
        many = allowed and value == 42
        key = "confirmed" if mode == "execute" else "simulated"
        if variant == "read_error":
            wait_for(lambda: fixture.reads >= 2, parent)
        elif case == "basic02":
            wait_for(lambda: fixture.reads-preparation["reads"] >= (11 if many else 3), parent)
        else:
            wait_for(lambda: fixture.gets >= (11 if many else 3), parent)
        if case == "basic02" and seed != 0 and variant not in ("read_error", "unknown") and not (allowed and mode == "execute"):
            wait_for(lambda: fixture.gets >= (11 if many else 3), parent)
        if allowed:
            wait_for(lambda: inspect(directory/"state")["counts"].get(key) == 1, parent)
        product = fixture.snapshot()
        state = inspect(directory/"state")
        assert fixture.body == original, "identity/timestamps must remain unchanged"
        assert state["counts"] == ({"unknown": 1} if variant == "unknown" else {key: 1} if allowed else {})
        assert product["writes"]-preparation["writes"] == int((allowed and mode == "execute") or variant == "unknown")
        if case == "basic02":
            reads = product["reads"]-preparation["reads"]
            assert reads >= (2 if variant == "read_error" else 11 if many else 3)
            if seed == 0:
                assert product["gets"] == 0
            elif variant == "read_error":
                assert product["gets"] == 0
            elif mode == "execute" and (allowed or variant == "unknown"):
                assert product["gets"] == 1
            else:
                assert product["gets"] >= 3
            # 首个产品协议操作必须是读，准备操作另外计数。
            trace = product["trace"][len(preparation["trace"]):]
            assert next(row["operation"] for row in trace if row["operation"] in (4, 5)) == 4
        report.update(product_window=product, state_before_stop=state)
        parent.send_signal(signal.SIGTERM)
        parent.wait(timeout=16)
        assert parent.returncode == (1 if variant in ("unknown", "read_error") else 0)
        output.close(); error.close()
        text = (directory/"product.jsonl").read_text()
        rows = [json.loads(line) for line in text.splitlines()]
        assert_no_forced_driver_stop(rows)
        driver_reaps = [row for row in rows if row.get("event") == "driver_process_reaped"]
        assert driver_reaps, "driver reap proof missing"
        if variant in ("unknown", "read_error"):
            assert '"shutdown_incomplete"' in text
            if variant == "unknown":
                assert inspect(directory/"state")["counts"] == {"unknown": 1}
        else:
            assert '"shutdown_complete"' in text and '"resources_released"' in text
            assert 'fault_cleanup' not in text
        if variant in ("invalid", "expired", "read_error"):
            assert 'recovering' in text and 'guard_false' not in text
        elif variant != "unknown":
            assert 'recovering' not in text and '"blocked"' not in text
        pids = {parent.pid, fixture.server.pid}
        for row in rows:
            if isinstance(row.get("pid"), int):
                pids.add(row["pid"])
        assert absent(parent.pid)
        inspected = cli(["state", "inspect", "--state-dir", directory/"state"], directory, "inspect")
        assert inspected["exit_code"] == 0
        fixture.fault = ""
        verified = memory()
        expected = value if allowed and mode == "execute" or variant == "unknown" else (seed if seed is not None else -23131)
        assert verified == expected.to_bytes(2, "big", signed=True).hex()+"a5"*14
        closed = fixture.close(); fixture = None
        assert all(absent(pid) for pid in pids)
        report.update(inspect=inspected, independent_memory_hex=verified, fixture_close=closed, product_exit=parent.returncode, reaped_pids=sorted(pids), driver_reaps=driver_reaps, had_forced_driver_stop=False, unknown_ack_fault="short_data" if variant == "unknown" else None, result="passed")
    finally:
        if parent and parent.poll() is None:
            report["forced_cleanup"] = True
            parent.terminate()
            try: parent.wait(timeout=16)
            except subprocess.TimeoutExpired: parent.kill(); parent.wait(timeout=2)
        if fixture is not None:
            report["fixture_close"] = fixture.close()
        output.close(); error.close()
        report["elapsed_seconds"] = time.monotonic()-started
        (directory/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    assert report["elapsed_seconds"] <= 45 and time.monotonic()-START <= 600


def test_basic01_cli(evidence):
    for mode in ("dry_run", "execute"):
        scenario(evidence, "basic01", mode)
        scenario(evidence, "basic01", mode, variant="idle")


def test_basic02_cli(evidence):
    for mode in ("dry_run", "execute"):
        scenario(evidence, "basic02", mode)
        scenario(evidence, "basic02", mode, variant="idle")
        scenario(evidence, "basic02", mode, variant="invalid")
        scenario(evidence, "basic02", mode, variant="expired")
        scenario(evidence, "basic02", mode, variant="read_error")
        for seed in (-1, 0):
            scenario(evidence, "basic02", mode, seed=seed)
    scenario(evidence, "basic02", "execute", variant="unknown")


def test_basic03_cli(evidence):
    for mode in ("dry_run", "execute"):
        for value in (-1, 0, 1, 42, 100, 101):
            scenario(evidence, "basic03", mode, value)
        for variant in ("idle", "invalid", "expired"):
            scenario(evidence, "basic03", mode, variant=variant)
