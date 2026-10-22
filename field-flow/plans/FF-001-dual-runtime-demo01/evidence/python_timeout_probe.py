"""FF-001 r1 候选驱动预检：真实 loopback 静默 COTP，非 runtime 实现。"""
import importlib.metadata
import json
import socket
import threading
import time
import sys
from snap7 import Client
from snap7.type import Parameter

# 固定获批端口；冲突立即失败，绝不换端口或杀占用者。
listener = socket.socket()
listener.bind(("127.0.0.1", 32102))
listener.listen(1)
listener.settimeout(8)
finished = threading.Event()
observations = {}

def silence_peer():
    with listener:
        peer, address = listener.accept()
        with peer:
            peer.settimeout(8)
            observations["cotp_request_bytes"] = len(peer.recv(1024))
            observations["peer_loopback"] = address[0] == "127.0.0.1"
            finished.wait(7)

thread = threading.Thread(target=silence_peer, name="ff001-preflight-silent-peer")
thread.start()
client = Client()
client.set_param(Parameter.PingTimeout, 500)
client.set_param(Parameter.SendTimeout, 500)
client.set_param(Parameter.RecvTimeout, 500)
start = time.monotonic()
try:
    client.connect("127.0.0.1", 0, 1, tcp_port=32102)
    observations["result"] = "unexpected_connection_success"
except Exception as exc:
    observations["result"] = type(exc).__name__
    observations["error"] = str(exc)
finally:
    observations["connect_elapsed_ms"] = round((time.monotonic() - start) * 1000)
    client.disconnect()
    finished.set()
    thread.join(timeout=2)
observations.update({
    "package": "python-snap7",
    "version": importlib.metadata.version("python-snap7"),
    "python": sys.version.split()[0],
    "python_executable": sys.executable,
    "configured_ping_ms": 500,
    "configured_send_ms": 500,
    "configured_recv_ms": 500,
    "contract_connect_hard_cap_ms": 3000,
    "contract_scheduling_allowance_ms": 500,
    "peer_thread_joined": not thread.is_alive(),
})
# 允许 TIME_WAIT；独立 bind+listen 确认无监听者残留。
check = socket.socket()
check.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    check.bind(("127.0.0.1", 32102))
    check.listen(1)
    observations["port_released"] = True
finally:
    check.close()
print(json.dumps(observations, sort_keys=True))
# 预检断言合同，失败保留真实退出码。
assert observations["connect_elapsed_ms"] <= 3500, "FF-001 R04 connect budget violated"
assert observations["peer_thread_joined"] and observations["port_released"]
