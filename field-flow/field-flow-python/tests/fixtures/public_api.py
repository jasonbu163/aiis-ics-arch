"""FF-001 r3：仅自身127.0.0.1 S7 Server/透传代理，有限候选公开API复核。"""
from __future__ import annotations
import multiprocessing as mp
import socket
import threading
import time
from snap7 import Client, Server
from snap7.type import SrvArea

HOST = "127.0.0.1"


def server_child(pipe):
    memory = bytearray([0xA5] * 16)
    server = Server(log=False)
    server.register_area(SrvArea.DB, 1, memory)
    try:
        server.start_to(HOST, 32103)
        pipe.send({"ready": True})
        while True:
            try:
                command = pipe.recv()
            except EOFError:
                break
            if command == "snapshot":
                pipe.send({"memory_hex": memory.hex()})
            elif command == "stop":
                break
    finally:
        server.stop()
        remaining = [t.name for t in threading.enumerate() if t is not threading.main_thread()]
        pipe.send({"remaining_threads": remaining})
        pipe.close()
        assert not remaining, remaining


def client_child(pipe):
    client = Client()
    try:
        client.connect(HOST, 0, 1, tcp_port=32102)
        pipe.send({"ready": True})
        while True:
            command = pipe.recv()
            if command == "stop":
                break
            assert command == "write"
            started = time.monotonic()
            try:
                value = client.db_write(1, 0, bytearray(b"\x00\x2a"))
                pipe.send({"api": "Client.db_write", "returned_success": True,
                           "return_value": value, "last_error": client.get_last_error(),
                           "duration_ms": round((time.monotonic() - started) * 1000, 3)})
            except Exception as exc:
                pipe.send({"api": "Client.db_write", "returned_success": False,
                           "error_type": type(exc).__name__, "error": str(exc),
                           "duration_ms": round((time.monotonic() - started) * 1000, 3)})
    finally:
        client.disconnect()
        pipe.close()


def exact(peer, count):
    output = bytearray()
    while len(output) < count:
        chunk = peer.recv(count - len(output))
        if not chunk:
            raise EOFError()
        output.extend(chunk)
    return bytes(output)


def frame(peer):
    header = exact(peer, 4)
    length = int.from_bytes(header[2:4], "big")
    if header[:2] != b"\x03\x00" or not 4 <= length <= 4096:
        raise ValueError("invalid finite fixture frame")
    return header + exact(peer, length - 4)


def bind(port):
    peer = socket.socket()
    peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        peer.bind((HOST, port))
        peer.listen(1)
        return peer
    except BaseException:
        peer.close()
        raise


class Fixture:
    def __init__(self):
        self.context = mp.get_context("spawn")
        self.listener = bind(32102)
        check = bind(32103)
        check.close()
        self.server_pipe, child_pipe = self.context.Pipe()
        self.server = self.context.Process(target=server_child, args=(child_pipe,))
        self.server.start()
        child_pipe.close()
        assert self.server_pipe.poll(3), "server ready deadline"
        assert self.server_pipe.recv() == {"ready": True}
        self.stop = threading.Event()
        self.sockets = []
        self.records = []
        self.error = None
        self.thread = threading.Thread(target=self.proxy, name="ff-own-s7-proxy")
        self.thread.start()
        self.client_pipe, child_pipe = self.context.Pipe()
        self.client = self.context.Process(target=client_child, args=(child_pipe,))
        self.client.start()
        child_pipe.close()
        if not self.client_pipe.poll(2.6):
            self.cleanup_fault(self.client)
            raise AssertionError("client overall connect deadline")
        assert self.client_pipe.recv() == {"ready": True}

    @staticmethod
    def cleanup_fault(child):
        if child.is_alive():
            child.terminate()
            child.join(0.2)
        if child.is_alive():
            child.kill()
            child.join(0.2)
        assert not child.is_alive(), "owned child cleanup incomplete"
        child.join()

    def proxy(self):
        try:
            self.listener.settimeout(0.1)
            while not self.stop.is_set():
                try:
                    front, _ = self.listener.accept()
                    break
                except socket.timeout:
                    continue
            else:
                return
            with front, socket.create_connection((HOST, 32103), timeout=1) as back:
                front.settimeout(1)
                self.sockets.extend([front, back])
                while not self.stop.is_set():
                    try:
                        request = frame(front)
                    except (EOFError, OSError):
                        break
                    back.sendall(request)
                    try:
                        response = frame(back)
                    except EOFError:
                        if request[5] == 0x80:
                            break
                        raise
                    is_write = request[7:9] == b"\x32\x01" and request[17] == 5
                    sent = bytearray(response)
                    if is_write:
                        # Only S7 ACK function; preserve ref/error/count/status/data.
                        assert response[19:22] == b"\x05\x01\xff"
                        sent[19] = 4
                    self.records.append({"writevar": is_write, "request_hex": request.hex(),
                                         "original_response_hex": response.hex(),
                                         "sent_response_hex": sent.hex(),
                                         "request_ref_hex": request[11:13].hex(),
                                         "original_response_ref_hex": response[11:13].hex(),
                                         "sent_response_ref_hex": sent[11:13].hex(),
                                         "request_function": request[17] if is_write else None,
                                         "original_function": response[19] if is_write else None,
                                         "sent_function": sent[19] if is_write else None})
                    front.sendall(sent)
        except BaseException as exc:
            self.error = repr(exc)

    def write(self):
        self.client_pipe.send("write")
        if not self.client_pipe.poll(4.6):
            self.cleanup_fault(self.client)
            return {"returned_success": False, "error": "overall_deadline", "forced_cleanup": True}
        return self.client_pipe.recv()

    def close(self):
        self.server_pipe.send("snapshot")
        assert self.server_pipe.poll(1)
        memory = self.server_pipe.recv()
        self.client_pipe.send("stop")
        self.client.join(5)
        if self.client.is_alive():
            self.cleanup_fault(self.client)
            raise AssertionError("client failed natural exit")
        self.stop.set()
        for peer in self.sockets:
            try:
                peer.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        self.listener.close()
        self.thread.join(2)
        assert not self.thread.is_alive()
        self.server_pipe.send("stop")
        self.server.join(5)
        if self.server.is_alive():
            self.cleanup_fault(self.server)
            raise AssertionError("server failed natural exit")
        assert self.server_pipe.poll(1)
        server_close = self.server_pipe.recv()
        self.server_pipe.close()
        self.client_pipe.close()
        for port in [32102, 32103]:
            check = bind(port)
            check.close()
        assert self.client.exitcode == self.server.exitcode == 0
        assert self.error is None, self.error
        return {**memory, "client_pid": self.client.pid, "server_pid": self.server.pid,
                "client_exitcode": self.client.exitcode, "server_exitcode": self.server.exitcode,
                "server_close": server_close, "proxy_joined": True, "ports_rebound": [32102, 32103]}
