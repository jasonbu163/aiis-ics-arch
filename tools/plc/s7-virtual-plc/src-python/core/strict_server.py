"""
File Path: /tools/plc/s7-virtual-plc/src-python/core/strict_server.py
Description: Strict COTP called-TSAP Snap7 server adapter
Main Features:
    - Validates the COTP C2 called-TSAP parameter before accepting a client
    - Reuses python-snap7 DB request handling after a matching handshake
"""
from __future__ import annotations

import logging
import socket
import threading
from collections.abc import Callable
from typing import Tuple

from snap7.server import Server, ServerISOConnection


logger = logging.getLogger(__name__)

CalledTsapRejectionCallback = Callable[[int, int | None], None]


def parse_called_tsap(data: bytes) -> int:
    """Return the sole two-byte COTP C2 called-TSAP value from a CR payload."""
    if len(data) < 7:
        raise ValueError("COTP CR is too short")
    if data[0] != len(data) - 1:
        raise ValueError("COTP CR length indicator does not match payload")
    if data[1] != ServerISOConnection.COTP_CR:
        raise ValueError("COTP PDU is not a connection request")

    called_tsap: int | None = None
    index = 7
    while index < len(data):
        if index + 2 > len(data):
            raise ValueError("COTP CR parameter header is truncated")
        parameter_code = data[index]
        parameter_length = data[index + 1]
        value_start = index + 2
        value_end = value_start + parameter_length
        if value_end > len(data):
            raise ValueError("COTP CR parameter value is truncated")

        if parameter_code == 0xC2:
            if parameter_length != 2:
                raise ValueError("COTP CR called TSAP must contain exactly two bytes")
            if called_tsap is not None:
                raise ValueError("COTP CR must contain exactly one called TSAP")
            called_tsap = int.from_bytes(data[value_start:value_end], byteorder="big")
        index = value_end

    if called_tsap is None:
        raise ValueError("COTP CR is missing the called TSAP")
    return called_tsap


class StrictServerISOConnection(ServerISOConnection):
    """Server ISO connection that accepts only one configured called TSAP."""

    def __init__(
        self,
        client_socket: socket.socket,
        expected_called_tsap: int,
        on_tsap_rejected: CalledTsapRejectionCallback,
    ) -> None:
        super().__init__(client_socket)
        self.expected_called_tsap = expected_called_tsap
        self.on_tsap_rejected = on_tsap_rejected

    def _parse_cotp_cr(self, data: bytes) -> bool:
        try:
            received_called_tsap = parse_called_tsap(data)
        except ValueError:
            self.on_tsap_rejected(self.expected_called_tsap, None)
            return False

        if received_called_tsap != self.expected_called_tsap:
            self.on_tsap_rejected(self.expected_called_tsap, received_called_tsap)
            return False
        return super()._parse_cotp_cr(data)


class StrictTsapServer(Server):
    """python-snap7 server that replaces only the ISO connection factory."""

    def __init__(
        self,
        expected_called_tsap: int,
        *,
        on_tsap_rejected: CalledTsapRejectionCallback | None = None,
    ) -> None:
        super().__init__()
        if not 0 <= expected_called_tsap <= 0xFFFF:
            raise ValueError("expected called TSAP must be between 0x0000 and 0xFFFF")
        self.expected_called_tsap = expected_called_tsap
        self.on_tsap_rejected = on_tsap_rejected or self._log_tsap_rejection

    def _log_tsap_rejection(self, expected_called_tsap: int, received_called_tsap: int | None) -> None:
        received = (
            f"0x{received_called_tsap:04X}"
            if received_called_tsap is not None
            else "missing_or_malformed"
        )
        logger.warning(
            "tsap_rejected expected_called_tsap=0x%04X received_called_tsap=%s",
            expected_called_tsap,
            received,
        )

    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        """Use the python-snap7 request loop after strict ISO negotiation succeeds."""
        try:
            connection = StrictServerISOConnection(
                client_socket,
                self.expected_called_tsap,
                self.on_tsap_rejected,
            )
            if not connection.accept_connection():
                logger.debug("Strict ISO connection rejected for %s", address)
                return

            logger.info("ISO connection established with %s", address)
            while self.running:
                try:
                    request_data = connection.receive_data()
                    response_data = self._process_request(request_data, address)
                    if response_data:
                        connection.send_data(response_data)
                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError):
                    logger.info("Client %s disconnected", address)
                    break
                except Exception as exc:
                    logger.error("Error handling client %s: %s", address, exc)
                    break
        except Exception as exc:
            logger.error("Client handler error for %s: %s", address, exc)
        finally:
            try:
                client_socket.close()
            except OSError:
                pass

            with self.client_lock:
                current_thread = threading.current_thread()
                if current_thread in self.clients:
                    self.clients.remove(current_thread)
                self.client_count = max(0, self.client_count - 1)

            logger.info("Client %s handler finished", address)
