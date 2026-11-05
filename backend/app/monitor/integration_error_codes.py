"""匿名集成稳定模块错误；不改变旧认证错误或全局响应。"""
from enum import StrEnum


class IntegrationError(StrEnum):
    SCOPE_REJECTED = "monitor.integration_scope_rejected"
    PARENT_NOT_FOUND = "monitor.integration_parent_not_found"
    EVENT_CONFLICT = "monitor.integration_event_conflict"
    VALUE_CONFLICT = "monitor.integration_value_conflict"
    OBSERVATION_TIME_CONFLICT = "monitor.integration_observation_time_conflict"
    PARENT_MISMATCH = "monitor.integration_parent_mismatch"
    PAYLOAD_TOO_LARGE = "monitor.integration_payload_too_large"
    MEDIA_TYPE = "monitor.integration_media_type"
    INVALID_REQUEST = "monitor.integration_invalid_request"
    NOT_READY = "monitor.integration_not_ready"
    UNAVAILABLE = "monitor.integration_unavailable"
    COMMIT_UNKNOWN = "monitor.integration_commit_unknown"
    INTERNAL_ERROR = "monitor.integration_internal_error"
