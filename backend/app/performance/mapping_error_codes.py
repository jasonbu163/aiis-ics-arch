"""模块HTTP映射错误，保持Core错误枚举不变。"""
from enum import StrEnum

class MappingError(StrEnum):
    UNAUTHENTICATED = "performance.mapping_unauthenticated"
    FORBIDDEN = "performance.mapping_forbidden"
    INVALID_SAMPLE = "performance.mapping_invalid_sample"
    SAMPLE_ID_CONFLICT = "performance.mapping_sample_id_conflict"
    VALUE_CONFLICT = "performance.mapping_value_conflict"
    SAMPLE_TIME_CONFLICT = "performance.mapping_sample_time_conflict"
    OBSERVATION_TIME_CONFLICT = "performance.mapping_observation_time_conflict"
    PARENT_NOT_FOUND = "performance.mapping_parent_not_found"
    PARENT_MISMATCH = "performance.mapping_parent_mismatch"
    DELETE_FORBIDDEN = "performance.mapping_delete_forbidden"
    UNAVAILABLE = "performance.mapping_unavailable"
    INTERNAL_ERROR = "performance.mapping_internal_error"
