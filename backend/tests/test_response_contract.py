"""No-DB tests for shared response and schema serialization contracts."""

import pytest

from app.system.schemas.system_dict import SysDictResponse
from common.response import StandardResponse, SuccessResponse


pytestmark = pytest.mark.no_db


def _assert_envelope(payload: dict) -> None:
    assert set(payload) >= {"code", "message", "data"}
    assert isinstance(payload["code"], int)
    assert isinstance(payload["message"], str)


def test_success_and_standard_response_keep_the_common_envelope():
    success = SuccessResponse(data={"ok": True}).model_dump()
    standard = StandardResponse(data={"ok": True}).model_dump()
    for payload in (success, standard):
        _assert_envelope(payload)
        assert payload["code"] == 200
        assert payload["data"] == {"ok": True}


def test_response_data_and_system_schema_use_camel_case_aliases():
    payload = SuccessResponse(
        data={"created_at": "2026-08-09T00:00:00", "page_size": 20}
    ).model_dump()
    assert "createdAt" in payload["data"]
    assert "pageSize" in payload["data"]
    schema = SysDictResponse(
        id=1,
        dict_type="status",
        dict_name="Status",
        created_at="2026-08-09T00:00:00",
    ).model_dump(by_alias=True)
    assert "dictType" in schema
    assert "createdAt" in schema
