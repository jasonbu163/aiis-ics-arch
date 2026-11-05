"""daa-local/v2原材料的静态typed结构；未知静态字段拒绝。"""
from decimal import Decimal
import re
from typing import Annotated, Literal
from pydantic import ConfigDict, Field, StrictBool, StrictInt, StrictStr, BeforeValidator, model_validator, WithJsonSchema
from common.schema_base import ApiSchema, to_camel
from ..retention import wire

def identifier(v):
    if not isinstance(v,str) or not 1<=len(v.encode('utf-8'))<=128 or v.strip()!=v or any(ord(c)<32 or ord(c)==127 for c in v):
        raise ValueError('invalid identifier')
    return v

def sequence(v):
    if not isinstance(v,str) or not re.fullmatch('[1-9][0-9]*',v) or int(v)>9223372036854775806: raise ValueError('invalid sequence')
    return v
Id=Annotated[StrictStr,BeforeValidator(identifier)]
Seq=Annotated[StrictStr,BeforeValidator(sequence)]
Time=Annotated[StrictStr,BeforeValidator(wire)]
Hash=Annotated[StrictStr,Field(pattern=r'^sha256:[0-9a-f]{64}$')]
Number=Annotated[Decimal,WithJsonSchema({'type':'number'})]
Value=StrictBool|StrictInt|Number|StrictStr|None

class StrictSchema(ApiSchema):
    model_config=ConfigDict(alias_generator=to_camel,
                            populate_by_name=False,extra='forbid',validate_default=True)

class Address(StrictSchema):
    offset: Annotated[StrictInt,Field(ge=0,le=65535)]
    bit: Annotated[StrictInt,Field(ge=0,le=7)]|None
    confirmed: StrictBool
    origin: StrictStr
    reason: StrictStr

class Definition(StrictSchema):
    id: Id
    plc_id: Id
    db_id: Id
    source_path: Annotated[StrictStr,Field(max_length=2048)]
    name: Annotated[StrictStr,Field(max_length=512)]
    name_mode: Literal['pending','auto_path','auto_address','manual']|None=None
    data_type: StrictStr
    comment: Annotated[StrictStr,Field(max_length=4096)]
    enabled: StrictBool
    group_id: Id|None
    address: Address|None

    @model_validator(mode='after')
    def optional_name_mode(self):
        if 'name_mode' in self.model_fields_set and self.name_mode is None: raise ValueError('nameMode must be a known enum when present')
        return self

class PointFact(StrictSchema):
    definition: Definition
    value: Value
    observed_at: Time
    quality: Literal['good','bad']
    reason: Annotated[StrictStr,Field(min_length=1,max_length=128)]|None

class Payload(StrictSchema):
    schema_version: Literal[2]
    sample_id: Id
    cycle_id: Id
    instance_id: Id
    plc_id: Id
    source_generation: Id
    source_seq: Seq
    group_id: Id
    revision: Id
    db_number: Annotated[StrictInt,Field(ge=1,le=65535)]
    origin: Annotated[StrictStr,Field(min_length=1,max_length=64)]
    started_at: Time
    finished_at: Time
    saved_at: Time
    points: dict[Id,PointFact]

class Read(StrictSchema):
    db_number: Annotated[StrictInt,Field(ge=1,le=65535)]
    start: Annotated[StrictInt,Field(ge=0,le=65535)]
    size: Annotated[StrictInt,Field(ge=1,le=65536)]
    started_at: Time
    finished_at: Time
    duration_ms: Annotated[StrictInt,Field(ge=0,le=9007199254740991)]
    quality: Literal['good','bad']

class ManifestSample(StrictSchema):
    sample_id: Id
    db_number: Annotated[StrictInt,Field(ge=1,le=65535)]
    sha256: Annotated[StrictStr,Field(pattern=r'^[0-9a-f]{64}$')]

class CycleManifest(StrictSchema):
    schema_version: Literal[2]
    cycle_id: Id
    plc_id: Id
    source_generation: Id
    source_seq: Seq
    group_id: Id
    revision: Id
    started_at: Time
    finished_at: Time
    saved_at: Time
    expected_point_ids: list[Id]
    reads: list[Read]
    samples: list[ManifestSample]
