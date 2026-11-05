"""v1公共符号、五声明字段与统一StrEnum业务失败合同。"""
from dataclasses import fields
from enum import Enum, StrEnum
import inspect

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from app.module_contract import CORE_CONTRACT, PUBLIC_SYMBOLS
from app.module_registry import ModuleManifest, resolve_import_path
from common.error_codes import ErrorCode
from common.exceptions import BusinessException
from common.response import SuccessResponse, serialize_api_data
from common.schema_base import ApiSchema
from core.registrar import register_exception_handlers

pytestmark = pytest.mark.no_db


class ProbeError(StrEnum):
    INVALID = "admission_probe.invalid_value"


def test_contract_version_symbols_and_manifest_defaults():
    assert CORE_CONTRACT == "aiis.backend-module/v1"
    manifest = ModuleManifest("probe")
    assert manifest.core_contract == CORE_CONTRACT
    for field in ("requires", "model_requires", "exports", "error_codes"):
        assert getattr(manifest, field) == ()
    assert set(f.name for f in fields(ModuleManifest)) == {"name", "enabled", "order", "routers", "models_package", "permissions", "core_contract", "requires", "model_requires", "exports", "error_codes"}
    for module, symbols in PUBLIC_SYMBOLS.items():
        for symbol in symbols:
            assert resolve_import_path(f"{module}:{symbol}") is not None
    assert tuple(inspect.signature(BusinessException).parameters) == ("error_code", "code", "message")


@pytest.mark.parametrize("value", ["probe.invalid", "", 1, Enum("Invalid", {"VALUE": 1}).VALUE])
def test_programming_errors_are_rejected(value):
    with pytest.raises(TypeError):
        BusinessException(value)


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [ErrorCode.USER_NOT_FOUND, ProbeError.INVALID])
async def test_core_and_module_business_error_share_wire_response(error):
    app = FastAPI()
    register_exception_handlers(app)
    @app.get("/failure")
    def failure():
        raise BusinessException(error)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        response = await client.get("/failure")
    assert response.status_code == 200
    assert response.json() == dict(code=400, message=error.value, data=None, errorCode=error.value)


def test_camel_case_success_contract():
    class Data(ApiSchema):
        stable_key: str
    result = SuccessResponse(data={"nested_items": [Data(stable_key="active")]})
    wire = result.model_dump(mode="json")
    assert wire["code"] == 200 and wire["message"] == "success"
    assert isinstance(wire["timestamp"], int)
    assert wire["data"] == {"nestedItems": [{"stableKey": "active"}]}


def test_integration_public_surface_and_private_boundary(tmp_path):
    from app.module_preflight import check_source, ModulePreflightError
    from tests.module_admission_fixtures import generate_core_profile, add_probe
    from common.integration.canonical import DIGEST_PROFILE, canonical_bytes, integration_digests
    from common.integration.envelope import CONTRACT_VERSION, validate_source_clock
    assert DIGEST_PROFILE == "bi-json/v1"
    assert CONTRACT_VERSION == "aiis.business-integration/v1"
    assert tuple(inspect.signature(integration_digests).parameters) == ("envelope", "resource", "parent_record_id")
    assert tuple(inspect.signature(validate_source_clock).parameters) == ("value", "database_now")
    assert canonical_bytes({"point_id": "原样"}) == '{"point_id":"原样"}'.encode()
    profile = generate_core_profile(tmp_path / "integration-core")
    add_probe(profile)
    domain = profile / "app/admission_probe/domain.py"
    domain.write_text('from common.integration.canonical import canonical_bytes\nACTIVE = "active"\ndef valid_label(value): return bool(canonical_bytes(value))\n')
    check_source(profile)
    domain.write_text('from common.integration.canonical import hashlib\nACTIVE = "active"\ndef valid_label(value): return True\n')
    with pytest.raises(ModulePreflightError, match="private-core"):
        check_source(profile)


def test_temperature_env_helper_is_only_additive_public_setting(tmp_path):
    from pathlib import Path
    from app.module_preflight import check_source, ModulePreflightError
    from tests.module_admission_fixtures import generate_core_profile, add_probe
    assert PUBLIC_SYMBOLS["settings"] == ("settings.BACKEND_MOCK_ENABLED", "resolve_env_file")
    profile=generate_core_profile(tmp_path/"core")
    add_probe(profile)
    domain=profile/"app/admission_probe/domain.py"
    domain.write_text('from settings import resolve_env_file\nACTIVE = "active"\ndef valid_label(value): return bool(value.strip())\n')
    check_source(profile)
    domain.write_text('from settings import settings\nACTIVE = settings.MYSQL_PASSWORD\ndef valid_label(value): return bool(value.strip())\n')
    with pytest.raises(ModulePreflightError,match="private-setting"):
        check_source(profile)


def test_business_time_public_pure_symbols_and_private_rejection(tmp_path):
    from app.module_preflight import check_source, ModulePreflightError
    from tests.module_admission_fixtures import generate_core_profile, add_probe
    expected=("StorageProbe","AdoptionContext","parse_adoption_manifest","validate_adoption_probe","to_storage_time","to_legacy_time")
    assert PUBLIC_SYMBOLS["common.integration.storage"]==expected
    profile=generate_core_profile(tmp_path/"business-time-core")
    add_probe(profile)
    domain=profile/"app/admission_probe/domain.py"
    domain.write_text('from common.integration.storage import StorageProbe, AdoptionContext, parse_adoption_manifest, validate_adoption_probe, to_storage_time, to_legacy_time\nACTIVE="active"\ndef valid_label(value): return bool(value)\n')
    check_source(profile)
    domain.write_text('from common.integration.storage import SCHEMA_REVISION\nACTIVE="active"\ndef valid_label(value): return bool(value)\n')
    with pytest.raises(ModulePreflightError,match="private-core"):
        check_source(profile)
