"""模块HTTP映射错误，保持Core错误枚举不变。"""
from enum import StrEnum

class MappingError(StrEnum):
    UNAUTHENTICATED = "equipment.mapping_unauthenticated"
    FORBIDDEN = "equipment.mapping_forbidden"
    INVALID_SAMPLE = "equipment.mapping_invalid_sample"
    SAMPLE_ID_CONFLICT = "equipment.mapping_sample_id_conflict"
    VALUE_CONFLICT = "equipment.mapping_value_conflict"
    SAMPLE_TIME_CONFLICT = "equipment.mapping_sample_time_conflict"
    OBSERVATION_TIME_CONFLICT = "equipment.mapping_observation_time_conflict"
    PARENT_NOT_FOUND = "equipment.mapping_parent_not_found"
    PARENT_MISMATCH = "equipment.mapping_parent_mismatch"
    DELETE_FORBIDDEN = "equipment.mapping_delete_forbidden"
    UNAVAILABLE = "equipment.mapping_unavailable"
    INTERNAL_ERROR = "equipment.mapping_internal_error"
