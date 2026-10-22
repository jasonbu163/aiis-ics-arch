"""Python自身有限HTTP/S7夹具；真实Server、透传故障、有限trace和实际join。"""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import multiprocessing as mp
import select
import socket
import threading
import time
from field_flow.domain import now_ms
from tests.fixtures.public_api import bind, exact


class IntMemory(bytearray):
    """自有合成DB只接纳完整2byte INT；原Server仍未修改且会先截断越界写。"""
    def __setitem__(self, key, value):
        if not isinstance(key, slice):
            raise ValueError("synthetic INT requires a full two-byte slice")
        start, stop, step = key.indices(len(self))
        if step != 1 or stop-start != 2 or len(value) != 2 or start+2 > len(self):
            raise ValueError("synthetic INT outside complete registered range")
        super().__setitem__(key, value)


def server_child(pipe):
    from snap7 import Server
    from snap7.type import SrvArea
    memory = IntMemory([0xa5]*16)
    server = Server(log=False)
    # Public registration retains this owned bytearray subtype; no private Server/transport hook.
    server.register_area(SrvArea.DB, 1, memory)
    try:
        server.start_to("127.0.0.1", 32103); pipe.send({"ready": True})
        while True:
            try: command = pipe.recv()
            except EOFError: break
            if command == "snapshot": pipe.send({"memory_hex": memory.hex()})
            elif command == "stop": break
    finally:
        server.stop()
        remaining = [t.name for t in threading.enumerate() if t is not threading.main_thread()]
        pipe.send({"remaining_threads": remaining}); pipe.close()
        assert not remaining


def frame(peer):
    header = exact(peer, 4)
    length = int.from_bytes(header[2:4], "big")
    assert header[:2] == b"\x03\x00" and 4 <= length <= 65535
    return header + exact(peer, length-4)


class Fixture:
    def __init__(self):
        try:
            self._start()
        except BaseException:
            if hasattr(self, "stop"): self.stop.set()
            if getattr(self, "http_thread", None) and self.http_thread.is_alive():
                self.http.shutdown(); self.http_thread.join(2)
            if hasattr(self, "http"): self.http.server_close()
            if hasattr(self, "listener"): self.listener.close()
            if getattr(self, "server", None) and self.server.pid:
                if self.server.is_alive():
                    try: self.pipe.send("stop")
                    except (EOFError, OSError): pass
                    self.server.join(.5)
                if self.server.is_alive(): self.server.terminate(); self.server.join(.2)
                if self.server.is_alive(): self.server.kill(); self.server.join(.2)
                assert not self.server.is_alive(), "fixture startup cleanup incomplete"
            raise

    def _start(self):
        self.stop = threading.Event()
        self.fault, self.delay, self.status, self.content_type = "", 0, 200, "application/json"
        self.body = {"schema_version": 1, "source_id": "demo01-feed", "ready": False, "command_id": None,
                     "value": None, "issued_at_ms": None, "expires_at_ms": None}
        self.trace, self.sockets, self.threads, self.errors = [], [], [], []
        self.trace_bytes = 0
        self.writes = self.reads = self.sessions = self.gets = self.closed_sessions = 0
        self.listener = bind(32102)
        check = bind(32103); check.close()
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                fixture.gets += 1
                body, status, kind, delay = fixture.body, fixture.status, fixture.content_type, fixture.delay
                if fixture.stop.wait(delay):
                    return
                raw = body if isinstance(body, bytes) else json.dumps(body).encode()
                try:
                    self.send_response(status); self.send_header("Content-Type", kind); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
                except (OSError, BrokenPipeError):
                    pass

            def log_message(self, *_):
                pass

        self.http = ThreadingHTTPServer(("127.0.0.1", 32880), Handler)
        self.http.daemon_threads = False
        self.server_epochs = []
        self.start_server()
        self.http_thread = threading.Thread(target=self.http.serve_forever, kwargs={"poll_interval": .02}, name="ff-fixture-http")
        self.proxy_thread = threading.Thread(target=self._accept, name="ff-fixture-proxy")
        self.http_thread.start(); self.proxy_thread.start()

    def start_server(self):
        context = mp.get_context("spawn")
        self.pipe, child_pipe = context.Pipe()
        self.server = context.Process(target=server_child, args=(child_pipe,))
        self.server.start(); child_pipe.close()
        assert self.pipe.poll(3) and self.pipe.recv() == {"ready": True}

    def stop_server(self):
        self.pipe.send("snapshot"); assert self.pipe.poll(1)
        memory = self.pipe.recv()
        self.pipe.send("stop"); self.server.join(4)
        assert not self.server.is_alive() and self.server.exitcode == 0
        assert self.pipe.poll(1); closed = self.pipe.recv(); self.pipe.close()
        assert closed["remaining_threads"] == []
        row = {**memory, **closed, "pid": self.server.pid, "exit_code": self.server.exitcode}
        self.server_epochs.append(row)
        return row

    def command(self, command_id, value=42, ttl=30000):
        wall = now_ms()
        self.body = {"schema_version": 1, "source_id": "demo01-feed", "ready": True, "command_id": command_id,
                     "value": value, "issued_at_ms": wall, "expires_at_ms": wall+ttl}
        return dict(self.body)

    def _record(self, row):
        assert len(self.trace) < 2000, "finite fixture trace limit"
        self.trace_bytes += len(json.dumps(row))
        assert self.trace_bytes <= 2*1024*1024, "finite fixture trace byte limit"
        self.trace.append(row)

    def _accept(self):
        self.listener.settimeout(.05)
        while not self.stop.is_set():
            try:
                front, _ = self.listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            t = threading.Thread(target=self._proxy, args=(front,), name="ff-fixture-s7-session")
            self.threads.append(t); t.start()

    def _held(self, peer):
        while not self.stop.wait(.005):
            if select.select([peer], [], [], 0)[0]:
                try:
                    if not peer.recv(4096):
                        break
                except OSError:
                    break

    def _proxy(self, front):
        self.sessions += 1
        self.sockets.append(front)
        try:
            with front, socket.create_connection(("127.0.0.1", 32103), timeout=1) as back:
                self.sockets.append(back); front.settimeout(10); back.settimeout(10)
                previous = {4: None, 5: None}
                while not self.stop.is_set():
                    req = frame(front)
                    op = req[17] if req[7:9] == b"\x32\x01" and len(req) > 17 else 0
                    fault = self.fault
                    if fault == "silent_cotp" and op == 0:
                        self._held(front); break
                    if fault == "disconnect":
                        break
                    back.sendall(req)
                    try:
                        original = frame(back)
                    except EOFError:
                        if len(req) > 5 and req[5] == 0x80:
                            break
                        raise
                    if op == 5:
                        self.writes += 1
                    if op == 4:
                        self.reads += 1
                    sent = bytearray(original)
                    prior_same, prior_other = previous.get(op), previous.get(5 if op == 4 else 4)
                    if op in (4, 5):
                        previous[op] = req[11:13]
                    if fault and op in (4, 5):
                        if fault in ("ref0", "ref1"):
                            sent[11 if fault == "ref0" else 12] ^= 1
                        elif fault in ("oldref", "otherref"):
                            sent[11:13] = prior_same if fault == "oldref" else prior_other
                        elif fault == "function":
                            sent[19] = 5 if op == 4 else 4
                        elif fault in ("id", "rosctr", "reserved0", "reserved1", "global0", "global1", "count", "item", "transport", "bits", "param_length", "data_length"):
                            index = {"id": 7, "rosctr": 8, "reserved0": 9, "reserved1": 10, "global0": 17, "global1": 18, "count": 20, "item": 21, "transport": 22, "bits": 24, "param_length": 14, "data_length": 16}[fault]
                            sent[index] ^= 1
                        elif fault == "short_header":
                            sent = sent[:15]
                        elif fault == "short_data":
                            sent = sent[:-1]
                        elif fault == "empty":
                            sent = sent[:7]
                        elif fault == "extra":
                            sent += b"\x00"
                        elif fault.startswith("payload"):
                            sent = sent[:7] + bytes(int(fault[7:]))
                        elif fault == "late_correct":
                            sent[19] = 4
                        if fault != "max_short":
                            sent[2:4] = len(sent).to_bytes(2, "big")
                    if fault == "max_short" and op in (4, 5):
                        sent = bytearray(b"\x03\x00\xff\xff\x02\xf0\x80\x32")
                    self._record({"operation": op, "fault": fault, "request_hex": req.hex(), "original_response_hex": original.hex(),
                                  "sent_response_hex": sent.hex(), "previous_same_ref": prior_same.hex() if prior_same else None,
                                  "previous_other_ref": prior_other.hex() if prior_other else None})
                    if fault == "hold_ack" and op == 5:
                        self._held(front); break
                    if fault == "max_short" and op in (4, 5):
                        front.sendall(sent)
                        self._held(front); break
                    if fault == "split" and op in (4, 5):
                        if self.stop.wait(3): break
                        front.sendall(sent[:7])
                        if self.stop.wait(3): break
                        front.sendall(sent[7:]); break
                    if fault == "slow" and op in (4, 5):
                        for byte in sent:
                            if self.stop.wait(.3): break
                            front.sendall(bytes([byte]))
                        break
                    if fault == "stale" and op in (4, 5):
                        sent[12] ^= 1
                        for _ in range(60):
                            if self.stop.wait(.1): break
                            front.sendall(sent)
                        break
                    front.sendall(sent)
                    if fault == "late_correct" and op == 5:
                        if self.stop.wait(.02): break
                        front.sendall(original)
        except (EOFError, OSError):
            pass
        except BaseException as exc:
            self.errors.append(repr(exc))
        finally:
            self.closed_sessions += 1

    def snapshot(self):
        self.pipe.send("snapshot"); assert self.pipe.poll(1)
        return {**self.pipe.recv(), "writes": self.writes, "reads": self.reads, "gets": self.gets,
                "sessions": self.sessions, "closed_sessions": self.closed_sessions, "trace": list(self.trace), "server_pid": self.server.pid}

    def close(self):
        snapshot = self.snapshot()
        self.stop.set(); self.http.shutdown(); self.http_thread.join(2); self.http.server_close()
        self.listener.close(); self.proxy_thread.join(2)
        for peer in self.sockets:
            try:
                peer.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        for t in self.threads:
            t.join(2); assert not t.is_alive()
        close = self.stop_server()
        assert not self.http_thread.is_alive() and not self.proxy_thread.is_alive() and not self.errors, self.errors
        for port in (32102, 32103, 32880):
            peer = bind(port); peer.close()
        return {**snapshot, "server_exit": self.server.exitcode, "server_close": close, "server_epochs": self.server_epochs, "proxy_threads_joined": len(self.threads), "ports_rebound": [32102, 32103, 32880]}
