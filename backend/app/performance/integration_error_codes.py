"""匿名集成稳定模块错误；不改变旧认证错误或全局响应。"""
from enum import StrEnum


class IntegrationError(StrEnum):
    SCOPE_REJECTED = "performance.integration_scope_rejected"
    PARENT_NOT_FOUND = "performance.integration_parent_not_found"
    EVENT_CONFLICT = "performance.integration_event_conflict"
    VALUE_CONFLICT = "performance.integration_value_conflict"
    OBSERVATION_TIME_CONFLICT = "performance.integration_observation_time_conflict"
    PARENT_MISMATCH = "performance.integration_parent_mismatch"
    PAYLOAD_TOO_LARGE = "performance.integration_payload_too_large"
    MEDIA_TYPE = "performance.integration_media_type"
    INVALID_REQUEST = "performance.integration_invalid_request"
    NOT_READY = "performance.integration_not_ready"
    UNAVAILABLE = "performance.integration_unavailable"
    COMMIT_UNKNOWN = "performance.integration_commit_unknown"
    INTERNAL_ERROR = "performance.integration_internal_error"
