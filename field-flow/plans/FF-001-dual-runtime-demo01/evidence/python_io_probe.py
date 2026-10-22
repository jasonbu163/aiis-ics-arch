"""FF-001 r1 驱动预检：纯透传 S7 ACK 分段延迟，子进程 server 正常退出。"""
import importlib.metadata
import inspect
import json
import multiprocessing as mp
import socket
import sys
import threading
import time
from snap7 import Client, Server
from snap7.type import Parameter, SrvArea

HOST = "127.0.0.1"

def server_child(pipe):
    memory = bytearray([0xA5] * 16)
    server = Server(log=False)
    server.register_area(SrvArea.DB, 1, memory)
    server.start_to(HOST, 32103)
    pipe.send({"ready": True})
    try:
        while True:
            command = pipe.recv()
            if command == "snapshot":
                pipe.send(list(memory))
            elif command == "stop":
                break
    finally:
        server.stop()
        # 实际检查线程，而非仅依赖 stop 返回；父进程仍须 join 子进程。
        alive = [t.name for t in threading.enumerate() if t is not threading.main_thread()]
        pipe.send({"remaining_threads": alive})
        pipe.close()
        assert not alive, alive


def exact(peer, n):
    result = b""
    while len(result) < n:
        part = peer.recv(n - len(result))
        if not part:
            raise EOFError()
        result += part
    return result


def frame(peer):
    header = exact(peer, 4)
    assert header[:2] == b"\x03\x00"
    length = int.from_bytes(header[2:4], "big")
    assert 4 <= length <= 4096
    return header + exact(peer, length - 4)


def assert_port_available(port):
    with socket.socket() as peer:
        peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer.bind((HOST, port))
        peer.listen(1)


def main():
    for port in (32102, 32103):
        assert_port_available(port)
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe()
    process = ctx.Process(target=server_child, args=(child,), name="ff001-python-s7-preflight")
    process.start()
    child.close()
    assert parent.poll(5) and parent.recv()["ready"]
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, 32102))
    listener.listen(1)
    listener.settimeout(10)
    mode = sys.argv[1] if len(sys.argv) > 1 else "segmented_ack"
    assert mode in ("segmented_ack", "stale_ack", "segmented_read")
    observations = {"sessions": 0, "write_requests": 0, "probe_mode": mode, "stale_frames": 0, "read_requests": 0}
    errors = []

    def proxy():
        try:
            with listener:
                incoming, _ = listener.accept()
                with incoming, socket.create_connection((HOST, 32103), timeout=10) as outgoing:
                    incoming.settimeout(10)
                    observations["sessions"] += 1
                    previous_response = None
                    while True:
                        request = frame(incoming)
                        outgoing.sendall(request)
                        response = frame(outgoing)
                        is_write = len(request) > 17 and request[7:9] == b"\x32\x01" and request[17] == 5
                        is_read = len(request) > 17 and request[7:9] == b"\x32\x01" and request[17] == 4
                        if is_read:
                            observations["read_requests"] += 1
                        if is_write:
                            observations["write_requests"] += 1
                        if is_write or (is_read and mode == "segmented_read"):
                            if is_write and mode == "segmented_read":
                                incoming.sendall(response)
                                continue
                            observations["request_pdu_ref"] = request[11:13].hex()
                            observations["ack_pdu_ref"] = response[11:13].hex()
                            observations["ack_header_error_hex"] = response[17:19].hex()
                            observations["ack_status_hex"] = response[-1:].hex()
                            # 真正 server ACK 已收到；只延迟字节或复制旧真响应，不改协议数据。
                            if mode in ("segmented_ack", "segmented_read"):
                                time.sleep(3)
                                incoming.sendall(response[:4])
                                time.sleep(3)
                                incoming.sendall(response[4:])
                            else:
                                assert previous_response is not None
                                for _ in range(3):
                                    incoming.sendall(previous_response)
                                    observations["stale_frames"] += 1
                                    time.sleep(0.05)
                                incoming.sendall(response)
                        else:
                            incoming.sendall(response)
                            previous_response = response
        except EOFError:
            pass
        except Exception as exc:
            errors.append(repr(exc))

    thread = threading.Thread(target=proxy, name="ff001-tpkt-preflight-proxy")
    thread.start()
    client = Client(timeout=0.5, connection_timeout=0.5)
    for param in (Parameter.PingTimeout, Parameter.SendTimeout, Parameter.RecvTimeout):
        client.set_param(param, 500)
    try:
        client.connect(HOST, 0, 1, tcp_port=32102)
        observations["socket_timeout_seconds"] = client.connection.socket.gettimeout()
        observations["stored_recv_timeout_ms"] = client.get_param(Parameter.RecvTimeout)
        start = time.monotonic()
        result = client.db_write(1, 4, bytearray(b"\x00\x2A"))
        observations["write_elapsed_ms"] = round((time.monotonic() - start) * 1000)
        observations["write_result"] = result
        if mode == "segmented_read":
            start = time.monotonic()
            observations["read_value_hex"] = client.db_read(1, 4, 2).hex()
            observations["read_elapsed_ms"] = round((time.monotonic() - start) * 1000)
    finally:
        client.disconnect()
        thread.join(12)
        parent.send("snapshot")
        assert parent.poll(3)
        observations["server_memory_hex"] = bytes(parent.recv()).hex()
        parent.send("stop")
        assert parent.poll(8)
        observations.update(parent.recv())
        process.join(8)
        observations["proxy_joined"] = not thread.is_alive()
        observations["server_exitcode"] = process.exitcode
        observations["server_process_joined"] = not process.is_alive()
        observations["proxy_errors"] = errors
        parent.close()
    for port in (32102, 32103):
        assert_port_available(port)
    observations.update({
        "ports_released": [32102, 32103],
        "package": "python-snap7",
        "version": importlib.metadata.version("python-snap7"),
        "client_constructor": str(inspect.signature(Client)),
        "client_connect": str(inspect.signature(Client.connect)),
        "contract_io_hard_cap_ms": 5000,
        "contract_scheduling_allowance_ms": 500,
    })
    print(json.dumps(observations, sort_keys=True), flush=True)
    assert observations["write_requests"] == 1 and observations["sessions"] == 1
    assert observations["server_memory_hex"] == "a5a5a5a5002aa5a5a5a5a5a5a5a5a5a5"
    assert observations["proxy_joined"] and observations["server_process_joined"]
    assert observations["server_exitcode"] == 0 and not errors
    measured = observations["read_elapsed_ms"] if mode == "segmented_read" else observations["write_elapsed_ms"]
    assert measured <= 5500, "FF-001 R04 synchronous IO hard cap violated"

if __name__ == "__main__":
    main()
