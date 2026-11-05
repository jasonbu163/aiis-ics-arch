"""A0 严格 JSON、八 typed DTO 与跨语言摘要向量；不连接数据库。"""
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
import hashlib
import json

import pytest
from pydantic import ValidationError
from common.integration.canonical import canonical_bytes, integration_digests
from common.integration.envelope import source_time, shanghai_time, validate_source_clock
from common.integration.http import strict_json, IntegrationPayloadError
from app.equipment.schemas.integration import TemperatureRequest, DriveRequest, ProductionParameterRequest
from app.performance.schemas.integration import ProductionObservationRequest, ProcessTemperatureRequest, ProcessTensionRequest, ProcessSpeedRequest
from app.monitor.schemas.integration import ProcessCurveRequest

pytestmark = pytest.mark.no_db
REQUESTS = (TemperatureRequest, DriveRequest, ProductionParameterRequest, ProductionObservationRequest,
            ProcessTemperatureRequest, ProcessTensionRequest, ProcessSpeedRequest, ProcessCurveRequest)
RESOURCES = ("temperature", "drive", "production_parameters", "production_observation",
             "process_temperature", "process_tension", "process_speed", "process_curve")


def example(index=1):
    data = {"equipmentId": "line-demo", "sampledAt": "2026-11-04T10:00:00.123+08:00", "quality": "good"}
    if index == 0:
        data.update({f"zone{n}{mode}": Decimal("199.5") for n in range(1, 6) for mode in ("Set", "Act")})
    elif index == 1:
        data["tv"] = Decimal("0.1")
    elif index == 2:
        data.update(coilNo="0", weight=0)
    elif index == 3:
        data.update(observationStatus="in_production", coilNo="0", weight=0)
    elif index in (4, 5, 6):
        data["recordTime"] = data.pop("sampledAt")
        data.update(coilNo="0", zone="zone-1")
        data[{4: "setTemp", 5: "setTension", 6: "setSpeed"}[index]] = 0
    else:
        data["z6TempAct"] = 0
    return {"contractVersion": "aiis.business-integration/v1", "producerId": "sma-demo", "eventId": "event-1",
            "mappingId": "mapping", "mappingRevision": "r1", "sourceRefs": [{"kind": "external_event",
            "sourceId": "源_x", "sourceEventId": "event"}], "data": data}


@pytest.mark.parametrize("index", range(8))
def test_eight_explicit_schemas_and_missing_zero(index):
    request = REQUESTS[index].model_validate(example(index))
    assert request.data.equipment_id == "line-demo"
    assert request.data.quality == "good"
    assert "sample_id" not in type(request.data).model_fields
    assert request.data.model_fields_set == set(
        field for field, definition in type(request.data).model_fields.items()
        if definition.alias in example(index)["data"])


@pytest.mark.parametrize("payload", [b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}', b'{"n":NaN}',
    b'{"n":Infinity}', b'{"n":1e999999}', b'{"n":0e-999999}', b'{"n":"\xff"}', b'{"n":"\\ud800"}', b'[]'])
def test_raw_json_rejects_unsafe_values(payload):
    with pytest.raises(IntegrationPayloadError) as error:
        strict_json(payload)
    assert error.value.status == 422


def test_raw_size_depth_and_original_decimal():
    assert strict_json(b'{"n":123456789.1234567891}')["n"] == Decimal("123456789.1234567891")
    for body in (b'{' + b' ' * 65536 + b'}', b'{"a":' + b'[' * 12 + b'0' + b']' * 12 + b'}', b'{"a":' + b'[' * 2000 + b'0' + b']' * 2000 + b'}'):
        with pytest.raises(IntegrationPayloadError) as error:
            strict_json(body)
        assert error.value.status == 413


@pytest.mark.parametrize("index", range(8))
@pytest.mark.parametrize("mutation", ("unknown", "snake", "null", "bool", "string", "version", "identity"))
def test_all_schemas_reject_invalid_inputs(index, mutation):
    payload = example(index)
    measurement = next(key for key in payload["data"] if key not in
                       {"equipmentId", "sampledAt", "quality", "recordTime", "coilNo", "zone", "observationStatus"})
    if mutation == "unknown": payload["data"]["handler"] = "sql"
    if mutation == "snake": payload["data"]["equipment_id"] = payload["data"].pop("equipmentId")
    if mutation in {"null", "bool", "string"}: payload["data"][measurement] = {"null": None, "bool": True, "string": "0"}[mutation]
    if mutation == "version": payload["contractVersion"] = "v2"
    if mutation == "identity": payload["producerId"] = " sma-demo"
    with pytest.raises(ValidationError):
        REQUESTS[index].model_validate(payload)


@pytest.mark.parametrize("raw, canonical, digest", [
    (b'{"z":-0.0,"n":1e0}', b'{"n":1,"z":0}', "11beb7b10beec1509e9c51e46aaa2445ba87a6134074c358144a087207082403"),
])
def test_frozen_simple_vector(raw, canonical, digest):
    assert canonical_bytes(strict_json(raw)) == canonical
    # Exact expected hash is stored in tasks before implementation; direct bytes are the authority.
    assert hashlib.sha256(canonical).hexdigest() == digest


def test_float32_exact_vector_presence_and_metadata_boundaries():
    payload = example()
    request = DriveRequest.model_validate(payload)
    assert canonical_bytes({"n": request.data.tv}) == b'{"n":0.100000001490116119384765625}'
    original = integration_digests(request, "drive")
    variant = deepcopy(payload); variant.update(eventId="event-2", mappingRevision="r2")
    changed = integration_digests(DriveRequest.model_validate(variant), "drive")
    assert original[0] != changed[0] and original[1] == changed[1]
    variant = deepcopy(payload); variant["data"]["km"] = 0
    assert integration_digests(DriveRequest.model_validate(variant), "drive")[1] != original[1]
    assert integration_digests(request, "drive", 101) != original
    variant = deepcopy(payload); variant["data"]["sampledAt"] = "2026-11-04T02:00:00.123Z"
    assert integration_digests(DriveRequest.model_validate(variant), "drive") == original
    variant["sourceRefs"].append({"kind": "plc_fact", "instanceId": "i", "plcId": "p", "sampleId": "s", "pointId": "原_点", "observedAt": "2026-11-04T02:00:00.123456789Z"})
    forward = DriveRequest.model_validate(variant)
    variant["sourceRefs"].reverse()
    assert integration_digests(forward, "drive") == integration_digests(DriveRequest.model_validate(variant), "drive")
    assert forward.source_refs[-1].observed_at == "2026-11-04T10:00:00.123456789+08:00"
    variant["sourceRefs"].append(deepcopy(variant["sourceRefs"][0]))
    with pytest.raises(ValidationError): DriveRequest.model_validate(variant)


@pytest.mark.parametrize("index, field, value", [(0,"zone1Set",Decimal("1.00000000001")),
    (0,"zone1Set",Decimal("1e20")), (1,"tv",Decimal("1e-46")), (1,"tv",Decimal("3.5e38")),
    (2,"weight",-1), (3,"weight",Decimal("1000000")), (3,"density",Decimal("1.0001")),
    (4,"duration",Decimal("0.1")), (5,"setTension",-1), (6,"setSpeed",Decimal("0.001")),
    (7,"z6TempAct",Decimal("1.5")), (7,"z6TempAct",2147483648)])
def test_technical_numeric_domains(index, field, value):
    payload = example(index); payload["data"][field] = value
    with pytest.raises(ValidationError): REQUESTS[index].model_validate(payload)


def test_temperature_exact_decimal_does_not_require_binary64_roundtrip():
    payload = example(0)
    payload["data"]["zone1Set"] = Decimal("123456789.1234567891")
    request = TemperatureRequest.model_validate(payload)
    assert request.data.zone1_set == Decimal("123456789.1234567891")
    assert b'123456789.1234567891' in canonical_bytes(request.model_dump(by_alias=True, exclude_unset=True))


def test_production_status_and_process_order():
    payload = example(3); payload["data"] = {"equipmentId":"line-demo", "quality":"good", "sampledAt":"2026-11-04T10:00:00+08:00", "observationStatus":"unknown", "coilNo":None}
    ProductionObservationRequest.model_validate(payload)
    payload["data"]["weight"] = 0
    with pytest.raises(ValidationError): ProductionObservationRequest.model_validate(payload)
    for index, values in [(4, {"minTemp":2, "maxTemp":1}), (5, {"minTension":2, "avgTension":1}), (6, {"avgSpeed":2,"maxSpeed":1})]:
        payload = example(index); payload["data"].update(values)
        with pytest.raises(ValidationError): REQUESTS[index].model_validate(payload)


def test_time_precision_and_injected_database_clock():
    local = source_time("2026-11-04T02:00:00.123000Z")
    assert shanghai_time(local) == "2026-11-04T10:00:00.123+08:00"
    assert shanghai_time(source_time("1990-06-01T00:00:00Z")) == "1990-06-01T08:00:00.000+08:00"
    assert shanghai_time(source_time("1000-01-01T00:00:00+08:00")) == "1000-01-01T00:00:00.000+08:00"
    assert validate_source_clock(local + timedelta(minutes=5), local)
    with pytest.raises(ValueError): validate_source_clock(local + timedelta(minutes=5, milliseconds=1), local)
    for value in ["2026-11-04T10:00:00", "2026-11-04T02:00:00.1230001Z", "2026-11-04T10:00:00+24:00"]:
        with pytest.raises(ValueError): source_time(value)


def test_independently_constructed_complete_digest_vector():
    payload = example()
    payload["data"]["tv"] = 0
    assert integration_digests(DriveRequest.model_validate(payload), "drive") == (
        'sha256:8ce846b2554fb5a2d0e74c9c70da5be7aa9bfa2d528c69f76a81b8784dd83f58',
        'sha256:b045713d63eea8316ec0e81cb6054ede59d15efec94cacf587bb33d5adb81a5a')


# Exact integer construction of the two sides of |F-N|*1e6 <= |N| for F=2^-149.
# Each N has 256 significand digits; expectations use Fraction, never a larger Decimal context.
def float_precision_vectors():
    from fractions import Fraction
    numerator=10**306
    upper_denominator=2**149*999999
    lower_denominator=2**149*1000001
    upper_outside=-(-numerator//upper_denominator)
    lower_outside=numerator//lower_denominator
    return [(Decimal(f'{upper_outside}e-300'),False),(Decimal(f'{upper_outside-1}e-300'),True),
            (Decimal(f'{lower_outside}e-300'),False),(Decimal(f'{lower_outside+1}e-300'),True)]


@pytest.mark.parametrize('owner',('equipment','performance','monitor'))
@pytest.mark.parametrize('precision',(6,28,50,200,400))
def test_float_256_digit_error_boundary_uses_exact_integer_ratio(owner,precision):
    from decimal import localcontext
    from fractions import Fraction
    from importlib import import_module
    helper=import_module(f'app.{owner}.integration_domain').float_number
    F=Fraction(1,2**149)
    for positive,permitted in float_precision_vectors():
        assert len(positive.as_tuple().digits)==256
        for value in (positive,positive.copy_negate()):
            number=Fraction(value);stored=F if value>0 else -F
            assert (abs(stored-number)*1000000<=abs(number))==permitted
            with localcontext()as context:
                context.prec=precision
                if permitted:assert Fraction(helper(value))==stored
                else:
                    with pytest.raises(ValueError):helper(value)
    with localcontext()as context:
        context.prec=precision
        assert helper(Decimal('-0'))==0
        assert helper(Decimal('3.4028234663852886e38'))==Decimal.from_float(__import__('struct').unpack('!f',bytes.fromhex('7f7fffff'))[0])
        with pytest.raises(ValueError):helper(Decimal('1e-46'))


@pytest.mark.parametrize('index,field',((1,'tv'),(7,'lineSpeedSet')))
async def test_float_exact_precision_boundary_is_rejected_before_unadopted_gate(index,field,monkeypatch):
    from core.registrar import create_app
    from tests.test_business_integration_api import PATHS,OWNERS
    from httpx import AsyncClient,ASGITransport
    from importlib import import_module
    owner=OWNERS[index];prefix=owner.upper()+'_INTEGRATION_'
    for key,value in {'ENABLED':'True','EQUIPMENT_IDS_JSON':'["line-demo"]','PRODUCER_IDS_JSON':'["sma-demo"]','STORAGE_PROFILE':'unadopted','ADOPTION_FILE':''}.items():monkeypatch.setenv(prefix+key,value)
    async def denied():pytest.fail('session entered before numeric/adoption validation')
    monkeypatch.setattr(import_module(f'app.{owner}.api.integration'),'get_db_session',denied)
    app=create_app(testing=True)
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture')as client:
        for number,permitted in float_precision_vectors():
            body=example(index);body['data'][field]=number
            raw=canonical_bytes(body);assert len(raw)<65536
            response=await client.post('/api/v1/integration/'+PATHS[index],content=raw,headers={'content-type':'application/json'})
            assert response.status_code==(503 if permitted else 422)
            assert response.json()['errorCode']==owner+('.integration_not_ready'if permitted else'.integration_invalid_request')
