"""匿名集成稳定模块错误；不改变旧认证错误或全局响应。"""
from enum import StrEnum


class IntegrationError(StrEnum):
    SCOPE_REJECTED = "equipment.integration_scope_rejected"
    PARENT_NOT_FOUND = "equipment.integration_parent_not_found"
    EVENT_CONFLICT = "equipment.integration_event_conflict"
    VALUE_CONFLICT = "equipment.integration_value_conflict"
    OBSERVATION_TIME_CONFLICT = "equipment.integration_observation_time_conflict"
    PARENT_MISMATCH = "equipment.integration_parent_mismatch"
    PAYLOAD_TOO_LARGE = "equipment.integration_payload_too_large"
    MEDIA_TYPE = "equipment.integration_media_type"
    INVALID_REQUEST = "equipment.integration_invalid_request"
    NOT_READY = "equipment.integration_not_ready"
    UNAVAILABLE = "equipment.integration_unavailable"
    COMMIT_UNKNOWN = "equipment.integration_commit_unknown"
    INTERNAL_ERROR = "equipment.integration_internal_error"
