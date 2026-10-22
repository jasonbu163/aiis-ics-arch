"""仅自建产品父进程/driver的崩溃、实例锁和真实停止证据。"""
import asyncio
from dataclasses import asdict, replace
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import yaml
from field_flow.infrastructure import state
from tests.fixtures.support import Harness, eventually, io_config


def lines(path):
    result = []
    for line in path.read_text().splitlines():
        try: result.append(json.loads(line))
        except json.JSONDecodeError: pass
    return result


def alive(pid):
    try: os.kill(pid, 0); return True
    except ProcessLookupError: return False


async def deaths():
    h = Harness("process-death"); parents = []; outputs = []; children = []
    c = replace(io_config(h.c), flows=(replace(h.c.flows[0], interval_ms=100),))
    configuration = h.root/"config.yaml"; configuration.write_text(yaml.safe_dump(asdict(c)))
    def spawn(name):
        out = h.root/(name+"-stdout.txt"); stream = out.open("wb"); outputs.append(stream)
        cmd = [sys.executable, "-m", "field_flow", "run", "--config", str(configuration), "--state-dir", str(h.root/name), "--execute"]
        parent = subprocess.Popen(cmd, stdout=stream, stderr=subprocess.STDOUT); parents.append(parent)
        return parent, out, cmd
    try:
        for which in ("child", "parent"):
            directory = h.root/which; state.init(directory, "execute", c.instance_id)
            h.fixture.command("applied-before-"+which); h.fixture.fault = "hold_ack"; before = h.fixture.writes
            parent, out, cmd = spawn(which)
            await eventually(lambda: h.fixture.writes == before+1, 4)
            child = next(r["pid"] for r in lines(out) if r.get("event") == "driver_ready")
            children.append(child)
            if which == "child":
                os.kill(child, signal.SIGKILL)
                await eventually(lambda: state.inspect(directory)["counts"].get("unknown", 0) == 1, 3)
                h.fixture.fault = ""; parent.send_signal(signal.SIGTERM)
                await eventually(lambda: parent.poll() is not None, 4)
                assert parent.returncode == 1 and not alive(child)
                assert not any(r.get("event") == "shutdown_complete" for r in lines(out))
                assert any(r.get("event") == "driver_process_reaped" and r.get("result") == "fault_cleanup" for r in lines(out))
                h.report.append({"case": which, "parent_pid": parent.pid, "driver_pid": child, "parent_exit": parent.returncode, "command": cmd, "stdout": str(out)})
            else:
                start = time.monotonic(); parent.kill(); parent.wait(timeout=1)
                lock = os.open(directory/"instance.lock", os.O_RDWR)
                observed = False
                try:
                    if alive(child):
                        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        except BlockingIOError: observed = True
                    await eventually(lambda: not alive(child), .5)
                    ended_ms = (time.monotonic()-start)*1000
                    assert ended_ms <= 500 and observed, "inherited lock was not observed during parent_lost window"
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                finally: os.close(lock)
                h.fixture.fault = ""
                h.report.append({"case": "parent_lost", "parent_pid": parent.pid, "driver_pid": child, "parent_exit": parent.returncode,
                                 "driver_ended_ms": ended_ms, "lock_blocked_until_child_end": observed, "command": cmd, "stdout": str(out)})
            assert h.fixture.writes-before == 1
            restart = await h.open(which, c, new=False, flows=False)
            for _ in range(10):
                try: await h.iteration(restart)
                except Exception as exc: assert str(exc) == "target_unknown"
                else: raise AssertionError("unknown accepted")
            await h.close_run(restart, False)
            assert state.inspect(directory)["counts"] == {"unknown": 1} and h.fixture.writes-before == 1
        # Product composition root receives a real SIGTERM and closes before its normal declarations.
        state.init(h.root/"normal", "execute", c.instance_id); h.fixture.command("normal-stop")
        parent, out, cmd = spawn("normal")
        await eventually(lambda: state.inspect(h.root/"normal")["counts"].get("confirmed", 0) == 1, 4)
        parent.send_signal(signal.SIGTERM); await eventually(lambda: parent.poll() is not None, 4)
        assert parent.returncode == 0
        rows = lines(out); child = next(r["pid"] for r in rows if r.get("event") == "driver_ready")
        assert not alive(child) and rows[-1]["event"] == "shutdown_complete"
        assert next(i for i,r in enumerate(rows) if r.get("event") == "driver_process_reaped") < next(i for i,r in enumerate(rows) if r.get("event") == "resources_released")
        h.report.append({"case": "normal-composition-stop", "parent_pid": parent.pid, "driver_pid": child, "parent_exit": 0, "command": cmd, "stdout": str(out)})
    finally:
        for parent in parents:
            if parent.poll() is None:
                parent.terminate()
                try: parent.wait(timeout=3)
                except subprocess.TimeoutExpired: parent.kill(); parent.wait(timeout=1)
        for stream in outputs: stream.close()
        for child in children:
            if alive(child): os.kill(child, signal.SIGKILL)
        await h.close()
