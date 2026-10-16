"""温控样本局部错误；不扩充Core全局错误owner。"""
from enum import StrEnum


class TemperatureError(StrEnum):
    UNAUTHENTICATED = "equipment.temperature_unauthenticated"
    FORBIDDEN = "equipment.temperature_forbidden"
    INVALID_SAMPLE = "equipment.temperature_invalid_sample"
    SAMPLE_ID_CONFLICT = "equipment.temperature_sample_id_conflict"
    SAMPLE_TIME_CONFLICT = "equipment.temperature_sample_time_conflict"
    UNAVAILABLE = "equipment.temperature_unavailable"
    INTERNAL_ERROR = "equipment.temperature_internal_error"
