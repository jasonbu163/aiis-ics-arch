"""模块HTTP映射错误，保持Core错误枚举不变。"""
from enum import StrEnum

class MappingError(StrEnum):
    UNAUTHENTICATED = "monitor.mapping_unauthenticated"
    FORBIDDEN = "monitor.mapping_forbidden"
    INVALID_SAMPLE = "monitor.mapping_invalid_sample"
    SAMPLE_ID_CONFLICT = "monitor.mapping_sample_id_conflict"
    VALUE_CONFLICT = "monitor.mapping_value_conflict"
    SAMPLE_TIME_CONFLICT = "monitor.mapping_sample_time_conflict"
    OBSERVATION_TIME_CONFLICT = "monitor.mapping_observation_time_conflict"
    PARENT_NOT_FOUND = "monitor.mapping_parent_not_found"
    PARENT_MISMATCH = "monitor.mapping_parent_mismatch"
    DELETE_FORBIDDEN = "monitor.mapping_delete_forbidden"
    UNAVAILABLE = "monitor.mapping_unavailable"
    INTERNAL_ERROR = "monitor.mapping_internal_error"
