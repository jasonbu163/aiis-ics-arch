"""
File Path: /tools/plc/s7-virtual-plc/tests/test_strict_tsap.py
Description: Strict COTP called-TSAP validation tests
Main Features:
    - Verifies COTP CR called-TSAP parsing accepts valid parameter layouts
    - Verifies malformed or mismatched TSAP handshakes are rejected before DB reads
"""
from __future__ import annotations

from pathlib import Path
import socket
import sys
import time
import unittest

import snap7
from snap7.error import S7ConnectionError
from snap7.type import SrvArea


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from core.strict_server import StrictTsapServer, parse_called_tsap  # noqa: E402


def _connection_request(*parameters: bytes) -> bytes:
    body = b"\xe0\x00\x00\x00\x01\x00" + b"".join(parameters)
    return bytes([len(body)]) + body


def _parameter(code: int, value: bytes) -> bytes:
    return bytes([code, len(value)]) + value


def _truncated_called_tsap_request() -> bytes:
    body = b"\xe0\x00\x00\x00\x01\x00\xc2\x02\x01"
    return bytes([len(body)]) + body


def _tpkt(payload: bytes) -> bytes:
    return b"\x03\x00" + (len(payload) + 4).to_bytes(2, byteorder="big") + payload


class COTPCalledTsapTests(unittest.TestCase):
    def test_parser_accepts_called_tsap_with_reordered_parameters_and_arbitrary_c1(self) -> None:
        request = _connection_request(
            _parameter(0xC2, b"\x01\x01"),
            _parameter(0xC1, b"\x12\x34"),
            _parameter(0xC0, b"\x0a"),
        )

        self.assertEqual(parse_called_tsap(request), 0x0101)

    def test_parser_rejects_missing_or_malformed_called_tsap(self) -> None:
        invalid_requests = (
            _connection_request(_parameter(0xC1, b"\x01\x00")),
            _connection_request(_parameter(0xC2, b"\x01")),
            _connection_request(_parameter(0xC2, b"\x01\x01"), _parameter(0xC2, b"\x01\x01")),
            _truncated_called_tsap_request(),
            bytes([17]) + _connection_request(_parameter(0xC2, b"\x01\x01"))[1:],
        )

        for request in invalid_requests:
            with self.subTest(request=request.hex()):
                with self.assertRaises(ValueError):
                    parse_called_tsap(request)

    def test_matching_tsap_can_read_registered_db_area(self) -> None:
        server, port, reads, rejections = self._start_server()
        client = snap7.client.Client()
        try:
            client.connect("127.0.0.1", 0, 1, tcp_port=port)
            self.assertEqual(bytes(client.db_read(1, 0, 2)), b"\x12\x34")
            self.assertGreaterEqual(len(reads), 1)
            self.assertEqual(rejections, [])
        finally:
            self._disconnect(client)
            server.destroy()

    def test_mismatched_tsap_is_rejected_before_any_db_read(self) -> None:
        server, port, reads, rejections = self._start_server()
        try:
            for rack, slot in ((0, 2), (1, 1)):
                client = snap7.client.Client()
                with self.subTest(rack=rack, slot=slot):
                    with self.assertRaises(S7ConnectionError):
                        client.connect("127.0.0.1", rack, slot, tcp_port=port)
                self._disconnect(client)
            deadline = time.monotonic() + 1
            while len(rejections) < 2 and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertEqual(reads, [])
            self.assertEqual(rejections, [(0x0101, 0x0102), (0x0101, 0x0121)])
        finally:
            server.destroy()

    def test_malformed_called_tsap_receives_no_confirm_or_db_read(self) -> None:
        server, port, reads, rejections = self._start_server()
        try:
            malformed_request = _connection_request(_parameter(0xC1, b"\x01\x00"))
            with socket.create_connection(("127.0.0.1", port), timeout=1) as client:
                client.settimeout(1)
                client.sendall(_tpkt(malformed_request))
                self.assertEqual(client.recv(1), b"")

            deadline = time.monotonic() + 1
            while len(rejections) < 1 and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertEqual(reads, [])
            self.assertEqual(rejections, [(0x0101, None)])
        finally:
            server.destroy()

    @staticmethod
    def _start_server() -> tuple[StrictTsapServer, int, list[object], list[tuple[int, int | None]]]:
        reads: list[object] = []
        rejections: list[tuple[int, int | None]] = []
        server = StrictTsapServer(0x0101, on_tsap_rejected=lambda expected, received: rejections.append((expected, received)))
        server.register_area(SrvArea.DB, 1, bytearray(b"\x12\x34"))
        server.set_read_events_callback(reads.append)
        server.start(tcp_port=0)
        assert server.server_socket is not None
        return server, server.server_socket.getsockname()[1], reads, rejections

    @staticmethod
    def _disconnect(client: snap7.client.Client) -> None:
        try:
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
