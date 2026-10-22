"""固定请求/INT边界、逐长度截断、逐字段拒绝；不替代真实协议gate。"""
import pytest
from field_flow.domain import Failure
from field_flow.infrastructure.s7_int_pdu import request, validate, ValidatedRead, ValidatedWriteAck


def read_response(value=42):
    return bytes.fromhex("3203000000020002000600000401ff040010") + value.to_bytes(2, "big", signed=True)


WRITE = bytes.fromhex("3203000000020002000100000501ff")


def test_requests_and_ints():
    assert request(2, 1, 0).hex() == "320100000002000e00000401120a10020002000184000000"
    for value in (-32768, -1, 0, 42, 32767):
        encoded = request(2, 1, 0, value)
        assert len(encoded) == 30 and encoded[-2:] == value.to_bytes(2, "big", signed=True)
        proof = validate(read_response(value), 2, 4)
        assert isinstance(proof, ValidatedRead) and proof.value == value
    assert isinstance(validate(WRITE, 2, 5), ValidatedWriteAck)
    assert request(65535, 65535, 65534)[-3:] == (65534*8).to_bytes(3, "big")
    for args in ((1, 1, 0), (65536, 1, 0), (2, 0, 0), (2, 1, 65535), (2, 1, 0, True), (2, 1, 0, -32769), (2, 1, 0, 32768), (2, 1, 0, 42.0)):
        with pytest.raises(Failure): request(*args)


def test_truncations_and_fields():
    for response, op in ((read_response(), 4), (WRITE, 5)):
        for n in range(len(response)):
            with pytest.raises(Failure): validate(response[:n], 2, op)
        for i in range(18 if op == 4 else 15):
            wrong = bytearray(response); wrong[i] ^= 1
            with pytest.raises(Failure): validate(wrong, 2, op)
        for size in (len(response)+1, 4096, 4097, 65528):
            with pytest.raises(Failure): validate(response+bytes(size-len(response)), 2, op)
