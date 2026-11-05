"""完整成功/终结拒绝/unknown输出合同；原Map键不做递归改名。"""
from typing import Literal
from pydantic import Field
from .source import StrictSchema, Id, Hash, Time

class Position(StrictSchema):
    commit_serial: str
    ordinal: int=Field(ge=0,le=32)

class CycleOut(StrictSchema):
    cycle_id: Id
    cycle_digest: Hash
    complete: bool
    quality_good: bool
    received_parts: int
    expected_parts: int

class PartResult(StrictSchema):
    sample_id: Id
    part: int
    parts: int
    source_sha256: Hash
    content_digest: Hash
    outcome: Literal['created','duplicate']
    original_outcome: Literal['created','duplicate']
    confirmation: Literal['created','duplicate','historical_committed']
    source_sample_complete: bool
    position: Position
    latest_advanced_point_ids: list[Id]
    expires_at: Time
    value_readable: bool

class ReceiptData(StrictSchema):
    contract_version: Literal['plc-facts/v1']='plc-facts/v1'
    digest_profile: Literal['pf-json/v1']='pf-json/v1'
    instance_id: Id
    batch_id: Id
    request_digest: Hash
    receipt_id: str
    status: Literal['committed']='committed'
    persistence: Literal['committed']='committed'
    new_facts_committed: bool
    outcome: Literal['created','duplicate']
    original_outcome: Literal['created','duplicate']
    confirmation: Literal['facts_committed']='facts_committed'
    commit_serial: str|None
    committed_at: Time
    proof_expires_at: Time
    results: list[PartResult]
    cycles: list[CycleOut]

class HistoricalProof(StrictSchema):
    sample_id: Id
    part: int
    content_digest: Hash
    source_sha256: Hash
    position: Position
    proof_expires_at: Time

class Diagnosis(StrictSchema):
    sample_id: Id
    part: int
    diagnosis: Literal['eligible','duplicate_proven','expired_unproven','conflict','source_rejected']
    historical_proof: HistoricalProof|None=None

class FailureData(StrictSchema):
    contract_version: Literal['plc-facts/v1']|None=None
    instance_id: Id|None=None
    batch_id: Id|None=None
    request_digest: Hash|None=None
    receipt_id: str|None=None
    recorded_at: Time|None=None
    persistence: Literal['none','rejection_recorded','unknown']
    new_facts_committed: bool|None
    retryable: bool
    retirement_allowed: bool
    rejection_token: str|None=None
    rejection_expires_at: Time|None=None
    diagnostics: list[Diagnosis]=Field(default_factory=list)
    requires_resync: bool|None=None
    lost_from: Position|None=None
    lost_through: Position|None=None
    earliest_recoverable_cursor: str|None=None

class ReceiptOut(StrictSchema):
    code: Literal[200]=200
    message: Literal['success']='success'
    data: ReceiptData

class FailureOut(StrictSchema):
    code: Literal[403,409,410,413,415,422,429,503,500]
    message: str
    error_code: str
    data: FailureData
