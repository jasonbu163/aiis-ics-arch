"""本工程专属driver子进程/匿名IPC；同步库唯一执行线程及总deadline回收。"""
from __future__ import annotations
import asyncio
from dataclasses import asdict
import fcntl
import json
import os
from pathlib import Path
import socket
import struct
import sys
import threading
import time
from field_flow.domain import Failure, canonical, identity, now_ms, require, Clock
from field_flow.infrastructure.s7_int_pdu import request, validate, ValidatedRead, ValidatedWriteAck


def encode(message):
    raw = canonical(message).encode()
    require(len(raw) <= 4092, "ipc_length")
    return struct.pack(">I", len(raw)) + raw


def receive(peer):
    def exact(n):
        body = bytearray()
        while len(body) < n:
            part = peer.recv(n - len(body))
            require(bool(part), "ipc_closed")
            body.extend(part)
        return body
    length = int.from_bytes(exact(4), "big")
    require(0 < length <= 4092, "ipc_length")
    return json.loads(exact(length))


class Gate:
    def __init__(self, directory):
        self.path = Path(directory) / ("gate-" + identity())
        self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        os.write(self.fd, b"1")
        self.mode = b"1"

    def close(self, stopping=False):
        target = b"2" if stopping else b"0"
        if self.mode == b"2" or self.mode == target:
            return
        end = time.monotonic() + .05
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                require(time.monotonic() < end, "stop_gate_deadline")
                time.sleep(.001)
        try:
            os.pwrite(self.fd, target, 0)
            self.mode = target
        finally:
            fcntl.flock(self.fd, fcntl.LOCK_UN)

    def dispose(self):
        os.close(self.fd)


def child(control_fd, life_fd, log_fd, lock_fd):
    # Keep inherited lock FD alive until actual process termination; child never opens SQLite.
    control, life, log = socket.socket(fileno=control_fd), socket.socket(fileno=life_fd), socket.socket(fileno=log_fd)
    normal = threading.Event()

    def watch():
        try:
            life.recv(1)
        except OSError:
            pass
        if not normal.is_set():
            time.sleep(.05)  # finite observation window retains inherited writer lock; still <=500ms.
            os._exit(70)  # parent_lost fault abort; can interrupt a synchronous stuck driver.

    watcher = threading.Thread(target=watch, name="ff-parent-liveness")
    watcher.start()
    log.setblocking(False)
    client, gate_fd, boot, exit_code = None, None, None, 0

    def child_log(event, **context):
        try:
            log.send(encode({"event": event, "pid": os.getpid(), **context}))
        except OSError:
            pass  # bounded diagnostic channel only; authoritative parent records call/result.

    try:
        control.settimeout(3)
        boot = receive(control)
        require(boot["kind"] == "bootstrap", "ipc_schema")
        gate_fd = os.open(boot["gate"], os.O_RDWR | os.O_NOFOLLOW)
        from snap7 import Client
        client = Client()
        p = boot["plc"]
        child_log("connecting")
        client.connect(p["host"], p["rack"], p["slot"], tcp_port=p["port"])
        reference = boot["reference_seed"]
        write_clock = Clock()
        control.sendall(encode({"kind": "ready", "nonce": boot["nonce"], "generation": boot["generation"]}))
        control.settimeout(None)
        while True:
            job = receive(control)
            require(job["generation"] == boot["generation"], "ipc_identity")
            if job["operation"] == "stop":
                break
            result = {"kind": "result", "request_id": job["request_id"], "generation": boot["generation"], "reference": reference}
            # Internal tests can hold this one call before its start gate, not a second work queue.
            while boot.get("barrier") and Path(boot["barrier"]).exists() and os.pread(gate_fd, 1, 0) == b"1":
                time.sleep(.002)
            fcntl.flock(gate_fd, fcntl.LOCK_EX)
            try:
                clock_valid = True
                if job["operation"] == "write":
                    try:
                        write_clock.check()
                    except Failure:
                        clock_valid = False
                        child_log("clock_invalid")
                remaining = job["deadline"] - time.monotonic()
                expired = remaining < .4 or (job.get("expires_at_ms") is not None and
                          (now_ms() >= job["expires_at_ms"] or job["issued_at_ms"] > now_ms()+1000 or now_ms() - job["issued_at_ms"] > job["input_max_age_ms"]))
                if not clock_valid or os.pread(gate_fd, 1, 0) == b"2" or (job["operation"] == "write" and os.pread(gate_fd, 1, 0) != b"1") or expired:
                    result.update(error="expired" if expired else "canceled", started=False)
                    control.sendall(encode(result))
                    continue
                control.sendall(encode({**result, "kind": "started"}))
            finally:
                fcntl.flock(gate_fd, fcntl.LOCK_UN)
            try:
                payload = request(reference, job["db"], job["offset"], job.get("value") if job["operation"] == "write" else None)
                response = client.iso_exchange_buffer(payload)  # exactly one send/exchange per dispatched job
                checked = validate(response, reference, 5 if job["operation"] == "write" else 4)
                if isinstance(checked, ValidatedWriteAck):
                    result["ack"] = {"reference": checked.reference, "operation": checked.operation}
                else:
                    result["read"] = {"reference": checked.reference, "value": checked.value}
                result["retire"] = reference == 65535
                control.sendall(encode(result))
                if reference == 65535:
                    break
                reference += 1
            except Exception as exc:
                result.update(error=str(exc) if isinstance(exc, Failure) else "plc_io_error", started=True)
                control.sendall(encode(result))
                break  # first error retires session; late ACK never consumed by a later job.
    except (Exception, KeyboardInterrupt):
        exit_code = 1
    finally:
        if client is not None:
            try:
                client.disconnect()
            except Exception:
                exit_code = 1
        child_log("client_closed")
        normal.set()
        life.shutdown(socket.SHUT_RD)
        watcher.join()
        remaining = [t.name for t in threading.enumerate() if t is not threading.main_thread()]
        child_log("threads_joined", remaining_threads=remaining[:8])
        if remaining:
            exit_code = 1
        if gate_fd is not None:
            os.close(gate_fd)
        for peer in (control, life, log):
            peer.close()
        os.close(lock_fd)
    return exit_code


class Driver:
    def __init__(self, state, plc, generation, gate):
        self.state, self.plc, self.generation, self.gate = state, plc, generation, gate
        self.process = self.control = self.life = self.logs = self.log_task = None
        self.forced, self.next_ref, self.started = False, 2, False
        self.reaped, self.fault = False, False

    @classmethod
    async def spawn(cls, state, plc, generation, gate, deadline, seed=2, barrier=None):
        driver = cls(state, plc, generation, gate)
        driver.next_ref = seed
        a, b = socket.socketpair()
        live_a, live_b = socket.socketpair()
        log_a, log_b = socket.socketpair(type=socket.SOCK_DGRAM)
        for peer in (a, b, log_a, log_b):
            peer.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
            peer.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
        driver.control, driver.life, driver.logs = a, live_a, log_a
        a.setblocking(False); log_a.setblocking(False)
        nonce = identity()
        try:
            driver.process = await asyncio.create_subprocess_exec(sys.executable, "-m", "field_flow.driver_process", str(b.fileno()), str(live_b.fileno()), str(log_b.fileno()), str(state.lock_fd), pass_fds=(b.fileno(), live_b.fileno(), log_b.fileno(), state.lock_fd), stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            b.close(); live_b.close(); log_b.close()
            driver.log_task = asyncio.create_task(driver._log_loop())
            await driver._event(deadline-.4, "driver_spawn", target_id=plc.id, pid=driver.process.pid, generation=generation)
            await driver._send({"kind": "bootstrap", "nonce": nonce, "generation": generation, "plc": asdict(plc), "gate": str(gate.path), "reference_seed": seed, "barrier": str(barrier) if barrier else None}, deadline - .4)
            result = await driver._receive(deadline - .4)
            require(result == {"kind": "ready", "nonce": nonce, "generation": generation}, "ipc_identity")
            await driver._event(deadline-.4, "driver_ready", target_id=plc.id, pid=driver.process.pid, generation=generation)
            return driver
        except BaseException:
            if driver.process is not None:
                try:
                    await driver.force(deadline, "connect_deadline_or_error")
                except Failure as error:
                    error.driver = driver
                    raise
            else:
                for peer in (a, live_a, log_a):
                    peer.close()
            raise Failure("driver_connect") from None
        finally:
            for peer in (b, live_b, log_b):
                peer.close()

    async def _log_loop(self):
        try:
            while True:
                data = await asyncio.get_running_loop().sock_recv(self.logs, 4101)
                if not data:
                    break
                require(4 < len(data) <= 4100 and int.from_bytes(data[:4], "big") == len(data)-4, "ipc_log_length")
                row = json.loads(data[4:])
                try:
                    await self.state.event("driver_child_event", pid=row["pid"], result=row["event"], remaining_threads=row.get("remaining_threads"))
                except Failure:
                    pass
        except (asyncio.CancelledError, OSError):
            pass

    async def _send(self, message, end):
        require(time.monotonic() < end, "driver_deadline")
        await asyncio.wait_for(asyncio.get_running_loop().sock_sendall(self.control, encode(message)), end-time.monotonic())

    async def _receive(self, end):
        async def exact(n):
            result = bytearray()
            while len(result) < n:
                part = await asyncio.get_running_loop().sock_recv(self.control, n-len(result))
                require(bool(part), "ipc_closed"); result.extend(part)
            return result
        async def one():
            n = int.from_bytes(await exact(4), "big")
            require(0 < n <= 4092, "ipc_length")
            return json.loads(await exact(n))
        require(time.monotonic() < end, "driver_deadline")
        return await asyncio.wait_for(one(), end-time.monotonic())

    async def _event(self, end, event, **values):
        try:
            await asyncio.wait_for(self.state.event(event, **values), max(.001, end-time.monotonic()))
        except (Failure, asyncio.TimeoutError):
            self.state._bad()

    async def _reap(self, end):
        if self.reaped:
            return
        require(time.monotonic() < end, "driver_cleanup_incomplete")
        await asyncio.wait_for(self.process.wait(), end-time.monotonic())
        if self.log_task is not None:
            self.log_task.cancel()
            await self.log_task
            self.log_task = None
        for peer in (self.control, self.life, self.logs):
            peer.close()
        self.reaped = True
        await self._event(end, "driver_process_reaped", pid=self.process.pid, result="fault_cleanup" if self.forced or self.fault or self.process.returncode else "normal", exit_code=self.process.returncode)

    async def force(self, end, reason):
        self.forced = True
        self.state.had_forced_driver_stop = True
        if self.process.returncode is None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(self.process.wait(), max(.001, min(.2, end-time.monotonic())))
            except asyncio.TimeoutError:
                self.process.kill()
        try:
            await self._reap(end)
            await self._event(end, "forced_driver_stop", pid=self.process.pid, error_key=reason, result="fault_cleanup")
        except (asyncio.TimeoutError, Failure):
            raise Failure("driver_cleanup_incomplete") from None

    async def call(self, operation, flow_id, db, offset, end, intent=None, request_id=None):
        request_id = request_id or identity()
        message = {"operation": operation, "flow_id": flow_id, "db": db, "offset": offset, "generation": self.generation,
                   "request_id": request_id, "deadline": end}
        if intent:
            message.update(value=intent.value, issued_at_ms=intent.issued_at_ms, expires_at_ms=intent.expires_at_ms, input_max_age_ms=intent.input_max_age_ms)
        self.started = False
        try:
            await self._send(message, end-.4)
            result = await self._receive(end-.4)
            require(result.get("request_id") == request_id and result.get("generation") == self.generation and result.get("reference") == self.next_ref, "ipc_identity")
            if result["kind"] == "started":
                self.started = True
                if operation == "write":
                    await self._event(end-.4, "driver_call_started", flow_id=flow_id, request_id=request_id, pid=self.process.pid, generation=self.generation)
                result = await self._receive(end-.4)
                require(result.get("request_id") == request_id and result.get("generation") == self.generation and result.get("reference") == self.next_ref and result.get("kind") == "result", "ipc_identity")
            require(result.get("kind") == "result", "ipc_schema")
            if "error" in result:
                if result.get("started"):
                    self.fault = True
                    await self._reap(end-.4)
                raise Failure(result["error"])
            checked = result.get("ack" if operation == "write" else "read")
            require(type(checked) is dict and checked.get("reference") == self.next_ref, "ipc_proof")
            if operation == "write":
                require(set(checked) == {"reference", "operation"} and checked["operation"] == 5, "ipc_proof")
                proof = object.__new__(ValidatedWriteAck)
                object.__setattr__(proof, "reference", self.next_ref); object.__setattr__(proof, "operation", 5)
            else:
                require(set(checked) == {"reference", "value"} and type(checked["value"]) is int and -32768 <= checked["value"] <= 32767, "ipc_proof")
                proof = object.__new__(ValidatedRead)
                object.__setattr__(proof, "reference", self.next_ref); object.__setattr__(proof, "value", checked["value"])
            self.next_ref += 1
            if result.get("retire"):
                await self._reap(end-.4)
            return proof, result.get("retire", False), request_id
        except Failure:
            raise
        except (asyncio.TimeoutError, OSError, ValueError, KeyError):
            await self.force(end, "driver_deadline_or_ipc")
            raise Failure("forced_driver_stop") from None

    async def close(self, end):
        if self.process.returncode is not None:
            if self.process.returncode != 0:
                self.forced = True
                self.state.had_forced_driver_stop = True
            await self._reap(end)
            if self.forced:
                await self._event(end, "forced_driver_stop", pid=self.process.pid, error_key="child_exit", result="fault_cleanup")
            return
        try:
            await self._send({"operation": "stop", "generation": self.generation}, end-.4)
            await self._reap(end-.4)
            require(self.process.returncode == 0, "driver_exit")
        except (asyncio.TimeoutError, OSError, Failure):
            await self.force(end, "stop_deadline")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(2)
    raise SystemExit(child(*(int(x) for x in sys.argv[1:])))
