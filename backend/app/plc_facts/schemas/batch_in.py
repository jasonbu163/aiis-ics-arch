"""固定版本batch、原材料字符串和不可变传输片清单。"""
from typing import Annotated, Literal
from pydantic import Field, StrictInt, StrictStr
from .source import StrictSchema, Id, Hash, Time

class Parent(StrictSchema):
    batch_id: Id
    request_digest: Hash
    rejection_token: StrictStr

class TransportPart(StrictSchema):
    part: Annotated[StrictInt,Field(ge=1,le=16)]
    point_ids: list[Id]
    content_digest: Hash

class TransportSample(StrictSchema):
    sample_id: Id
    db_number: Annotated[StrictInt,Field(ge=1,le=65535)]
    source_sha256: Hash
    parts: list[TransportPart]

class CycleIn(StrictSchema):
    cycle_id: Id
    manifest_utf8: StrictStr
    manifest_sha256: Hash
    context_utf8: StrictStr
    context_sha256: Hash
    transport_manifest: list[TransportSample]

class SamplePartIn(StrictSchema):
    sample_id: Id
    cycle_id: Id
    part: Annotated[StrictInt,Field(ge=1,le=16)]
    parts: Annotated[StrictInt,Field(ge=1,le=16)]
    point_ids: list[Id]
    payload_utf8: StrictStr
    source_sha256: Hash
    content_digest: Hash

class BatchIn(StrictSchema):
    contract_version: Literal['plc-facts/v1']
    source_profile: Literal['daa-local/v2']
    digest_profile: Literal['pf-json/v1']
    instance_id: Id
    batch_id: Id
    batch_created_at: Time
    request_digest: Hash
    parent: Parent|None
    cycles: list[CycleIn]
    samples: list[SamplePartIn]
