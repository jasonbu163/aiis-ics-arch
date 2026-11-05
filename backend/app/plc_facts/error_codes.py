"""事实命名空间错误与脱敏结构化失败；不改变Core异常合同。"""
from enum import StrEnum
from common.exceptions import BusinessException

class ErrorCode(StrEnum):
    SCOPE_REJECTED = "plc_facts.scope_rejected"
    SOURCE_REJECTED = "plc_facts.source_rejected"
    BATCH_CONTENT_CONFLICT = "plc_facts.batch_content_conflict"
    SAMPLE_CONTENT_CONFLICT = "plc_facts.sample_content_conflict"
    CYCLE_CONTENT_CONFLICT = "plc_facts.cycle_content_conflict"
    BINDING_CONFLICT = "plc_facts.binding_conflict"
    SAMPLE_EXPIRED = "plc_facts.sample_expired"
    PROOF_EXPIRED = "plc_facts.proof_expired"
    CURSOR_EXPIRED = "plc_facts.cursor_expired"
    CURSOR_GAP = "plc_facts.cursor_gap"
    PARENT_PROOF_EXPIRED = "plc_facts.parent_proof_expired"
    BATCH_ADMISSION_EXPIRED = "plc_facts.batch_admission_expired"
    PAYLOAD_TOO_LARGE = "plc_facts.payload_too_large"
    MEDIA_TYPE = "plc_facts.media_type"
    INVALID_REQUEST = "plc_facts.invalid_request"
    DIGEST_MISMATCH = "plc_facts.digest_mismatch"
    CURSOR_MISMATCH = "plc_facts.cursor_mismatch"
    BUSY = "plc_facts.busy"
    NOT_READY = "plc_facts.not_ready"
    UNAVAILABLE = "plc_facts.unavailable"
    COMMIT_OUTCOME_UNKNOWN = "plc_facts.commit_outcome_unknown"
    CLOCK_INVALID = "plc_facts.clock_invalid"
    CAPACITY_EXCEEDED = "plc_facts.capacity_exceeded"
    INTERNAL_ERROR = "plc_facts.internal_error"

class FactsError(BusinessException):
    def __init__(self, suffix, status=422, data=None):
        super().__init__(ErrorCode('plc_facts.' + suffix), code=status)
        self.data = data or dict(persistence='none', newFactsCommitted=False, retryable=status in (429,503),
                                 retirementAllowed=False, diagnostics=[])
