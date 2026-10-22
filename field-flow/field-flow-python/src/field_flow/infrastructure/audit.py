"""父状态线程唯一JSONL审计writer；完整行、轮转、sync与失败反馈。"""
import datetime
import json
import os
from pathlib import Path
import stat
from field_flow.domain import Failure, require


def event_line(run_id, instance, event, **context):
    row = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "event": event,
           "implementation": "python", "run_id": run_id, "instance_id": instance,
           **dict.fromkeys(("flow_id", "target_id", "command_id", "request_id", "state", "old", "new", "result", "error_key"), ""),
           "duration_ms": 0, **context}
    data = (json.dumps(row, separators=(",", ":"), ensure_ascii=True)+"\n").encode()
    require(len(data) <= 4096, "audit_size")
    return data


class Audit:
    def __init__(self, directory, run_id, instance):
        self.path = Path(directory) / "runtime.jsonl"
        self.run_id, self.instance = run_id, instance
        self.limit, self.failed, self.fd = 5 * 1024 * 1024, False, None
        self._open()
        os.set_blocking(1, False)

    def _open(self):
        self.fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NONBLOCK | os.O_NOFOLLOW, 0o600)
        require(stat.S_ISREG(os.fstat(self.fd).st_mode), "audit_file")

    def emit(self, event, **context):
        try:
            if event == getattr(self, "_test_fail_event", None):
                self.failed = True
            require(not self.failed, "audit_persist")
            stdout = context.pop("_stdout", True)
            data = event_line(self.run_id, self.instance, event, **context)
            if os.fstat(self.fd).st_size + len(data) > self.limit:
                os.close(self.fd); self.fd = None
                for n in range(4, 0, -1):
                    old = self.path if n == 1 else Path(str(self.path) + f".{n-1}")
                    if old.exists():
                        os.replace(old, str(self.path) + f".{n}")
                self._open()
            require(os.write(self.fd, data) == len(data), "audit_persist")
            os.fsync(self.fd)
            if stdout:
                require(os.write(1, data) == len(data), "audit_stdout")
            return data
        except (OSError, Failure):
            self.failed = True
            raise Failure("audit_persist") from None

    def close(self):
        if self.fd is not None:
            os.close(self.fd); self.fd = None
