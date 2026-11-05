"""三种读取模式的typed输出闭包。"""
from typing import Literal
from pydantic import Field
from .source import StrictSchema, Id, Hash, Time, PointFact
from .receipt_out import Position,CycleOut

class Projection(StrictSchema):
    source_sha256: Hash
    sample_id: Id
    cycle_id: Id
    instance_id: Id
    plc_id: Id
    source_generation: Id
    source_seq: str
    group_id: Id
    config_revision: Id
    db_number: int
    origin: str
    started_at: Time
    finished_at: Time
    saved_at: Time
    part: int
    parts: int
    points: dict[Id,PointFact]
    expires_at: Time

class FactItem(StrictSchema):
    kind: Literal['fact']='fact'
    position: Position
    source_sha256: Hash
    content_digest: Hash
    projection_digest: Hash
    projection: Projection
    cycle: CycleOut

class GapItem(StrictSchema):
    kind: Literal['gap']='gap'
    position: Position
    reason: Literal['raw_expired','raw_unavailable']
    instance_id: Id
    plc_id: Id
    source_generation: Id
    source_seq: str
    cycle_id: Id
    sample_id: Id
    part: int
    point_ids: list[Id]
    source_sha256: Hash
    content_digest: Hash
    observed_from: Time
    observed_to: Time
    expired_at: Time

class OriginalItem(StrictSchema):
    kind: Literal['original']='original'
    position: Position
    instance_id: Id
    plc_id: Id
    sample_id: Id
    source_sha256: Hash
    payload_utf8: str
    source_sample_complete: bool
    expires_at: Time

class SourceRef(StrictSchema):
    instance_id: Id
    source_generation: Id
    source_seq: str
    config_revision: Id
    definition_digest: Hash
    sample_id: Id
    part: int
    cycle_id: Id
    group_id: Id

class LatestPoint(PointFact):
    expires_at: Time
    source: SourceRef

class LatestDb(StrictSchema):
    plc_id: Id
    db_number: int
    points: dict[Id,LatestPoint]

class Coverage(StrictSchema):
    complete: Literal[False]=False
    meaning: Literal['receipt_feed_only_not_source_completeness']='receipt_feed_only_not_source_completeness'
    unknown_before_serial: str

class ReadBase(StrictSchema):
    contract_version: Literal['plc-facts/v1']='plc-facts/v1'
    digest_profile: Literal['pf-json/v1']='pf-json/v1'
    as_of: Time
    has_more: bool
    coverage: Coverage

class ChangesData(ReadBase):
    mode: Literal['changes']='changes'
    items: list[FactItem|GapItem]
    next_cursor: str
    snapshot_high_serial: str
    scanned_through: Position
    scan_budget_reached: bool
    baseline: Literal['explicit_tail']|None
    omitted_through: str|None=None

class RangeData(ReadBase):
    mode: Literal['range']='range'
    items: list[FactItem|GapItem|OriginalItem]
    next_page_cursor: str|None
    snapshot_high_serial: str
    scanned_through: Position
    scan_budget_reached: bool

class LatestData(ReadBase):
    mode: Literal['latest']='latest'
    items: list[LatestDb]
    next_page_cursor: str|None
    binding_revision: str

class ReadOut(StrictSchema):
    code: Literal[200]=200
    message: Literal['success']='success'
    data: ChangesData|RangeData|LatestData
