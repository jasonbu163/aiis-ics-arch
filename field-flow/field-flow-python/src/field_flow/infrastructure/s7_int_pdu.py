"""R15单item/2字节DB INT；公开raw返回后4096cap，严格关联正ACK。"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack, unpack
from field_flow.domain import Failure, integer, require


@dataclass(frozen=True, init=False)
class ValidatedRead:
    reference: int
    value: int

    def __new__(cls):
        raise TypeError("validator-owned result")


@dataclass(frozen=True, init=False)
class ValidatedWriteAck:
    reference: int
    operation: int

    def __new__(cls):
        raise TypeError("validator-owned result")


def request(reference, db, offset, value=None):
    integer(reference, 2, 65535, "s7_request")
    integer(db, 1, 65535, "s7_request")
    integer(offset, 0, 65534, "s7_request")
    operation = 4 if value is None else 5
    if value is not None:
        integer(value, -32768, 32767, "s7_request")
    header = pack(">BBHHHH", 0x32, 1, 0, reference, 14, 0 if operation == 4 else 6)
    parameter = bytes([operation, 1, 0x12, 0x0a, 0x10, 2]) + pack(">HHB", 2, db, 0x84) + (offset*8).to_bytes(3, "big")
    return bytearray(header + parameter + (b"" if operation == 4 else b"\x00\x04\x00\x10" + pack(">h", value)))


def validate(response, reference, operation):
    # Library owns receive/allocation (single-frame max65528); cap is AFTER return.
    require(type(response) in (bytearray, bytes) and len(response) <= 4096, "s7_invalid_response")
    expected = 20 if operation == 4 else 15
    require(operation in (4, 5) and len(response) == expected, "s7_invalid_response")
    require(response[:4] == b"\x32\x03\x00\x00", "s7_invalid_response")
    require(response[4:6] == reference.to_bytes(2, "big"), "s7_reference_mismatch")
    require(response[10:12] == b"\x00\x00", "s7_remote_error")
    require(response[6:10] == pack(">HH", 2, 6 if operation == 4 else 1) and
            response[12:14] == bytes([operation, 1]), "s7_invalid_response")
    require(response[14] == 0xff, "s7_remote_error")
    if operation == 4:
        require(response[15:18] == b"\x04\x00\x10", "s7_invalid_response")
        result = object.__new__(ValidatedRead)
        object.__setattr__(result, "value", unpack(">h", response[18:20])[0])
    else:
        result = object.__new__(ValidatedWriteAck)
        object.__setattr__(result, "operation", 5)
    object.__setattr__(result, "reference", reference)
    return result
