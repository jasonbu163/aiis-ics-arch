"""显式CLI init/fixture/run/inspect的两模式实际启动；自身进程全部wait。"""
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from field_flow.infrastructure.state import inspect
from tests.test_matched_ack_gate import independent_read


def main():
    root = Path(tempfile.mkdtemp(prefix="ff-001-r1-r4-python-cli-smoke-", dir="/private/tmp"))
    fixture_out = (root/"fixture-stdout.txt").open("wb")
    fixture_cmd = [sys.executable, "-m", "tests.fixtures", "--config", "config/loopback.yaml", "--evidence-dir", str(root/"fixture")]
    fixture = subprocess.Popen(fixture_cmd, stdout=fixture_out, stderr=subprocess.STDOUT)
    records, children = [], []
    try:
        end = time.monotonic()+4
        while '"fixture_ready"' not in (root/"fixture-stdout.txt").read_text():
            assert time.monotonic() < end and fixture.poll() is None
            time.sleep(.005)
        for mode in ("dry_run", "execute"):
            directory = root/mode
            cmd = [sys.executable, "-m", "field_flow", "state", "init", "--synthetic", "--mode", mode, "--state-dir", str(directory), "--instance-id", "ff-python-demo01"]
            result = subprocess.run(cmd, capture_output=True, timeout=3)
            assert result.returncode == 0; records.append({"command": cmd, "exit_code": result.returncode, "stdout": result.stdout.decode()})
            cmd = [sys.executable, "-m", "field_flow", "run", "--config", "config/loopback.yaml", "--state-dir", str(directory)] + (["--execute"] if mode == "execute" else [])
            output = root/(mode+"-stdout.txt")
            with output.open("wb") as stream:
                parent = subprocess.Popen(cmd, stdout=stream, stderr=subprocess.STDOUT); children.append(parent)
                end = time.monotonic()+4
                while not inspect(directory)["counts"].get("confirmed" if mode == "execute" else "simulated", 0):
                    assert time.monotonic() < end and parent.poll() is None
                    time.sleep(.005)
                start = time.monotonic(); parent.send_signal(signal.SIGTERM); parent.wait(timeout=15)
                assert parent.returncode == 0
            cmd_inspect = [sys.executable, "-m", "field_flow", "state", "inspect", "--state-dir", str(directory)]
            result = subprocess.run(cmd_inspect, capture_output=True, timeout=3); assert result.returncode == 0
            records.append({"command": cmd, "parent_pid": parent.pid, "exit_code": parent.returncode, "shutdown_ms": (time.monotonic()-start)*1000,
                            "inspect_command": cmd_inspect, "inspect_exit": result.returncode, "state": inspect(directory, True), "stdout": str(output)})
        assert independent_read() == 42
        fixture.send_signal(signal.SIGTERM); fixture.wait(timeout=8); assert fixture.returncode == 0
        report = json.loads((root/"fixture/report.json").read_text())
        assert report["writes"] == 1 and report["memory_hex"] == "002a"+"a5"*14
        (root/"report.json").write_text(json.dumps({"commands": records, "fixture_command": fixture_cmd, "fixture_pid": fixture.pid, "fixture_exit": fixture.returncode,
                                                  "fixture": report}, indent=2)+"\n")
        print(json.dumps({"evidence": str(root/"report.json")}))
        return 0
    finally:
        for child in [*children, fixture]:
            if child.poll() is None:
                child.terminate()
                try: child.wait(timeout=3)
                except subprocess.TimeoutExpired: child.kill(); child.wait(timeout=1)
        fixture_out.close()


if __name__ == "__main__": raise SystemExit(main())
