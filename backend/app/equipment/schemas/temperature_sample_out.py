"""稳定投递结果与完整新样本读回；不暴露receipt/actor身份。"""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import field_serializer
from common.schema_base import ApiSchema
from app.equipment.temperature_sample_domain import TEMPERATURE_FIELDS, json_number, utc_milliseconds


class TemperatureSampleResult(ApiSchema):
    record_id: int
    equipment_id: str
    sample_id: str
    sampled_at: datetime
    outcome: Literal["created", "duplicate"]

    @field_serializer("sampled_at")
    def source_time(self, value):
        return utc_milliseconds(value)


class TemperatureSampleOut(ApiSchema):
    record_id: int
    equipment_id: str
    sampled_at: datetime
    quality: Literal["good"]
    zone1_set: Decimal
    zone1_act: Decimal
    zone2_set: Decimal
    zone2_act: Decimal
    zone3_set: Decimal
    zone3_act: Decimal
    zone4_set: Decimal
    zone4_act: Decimal
    zone5_set: Decimal
    zone5_act: Decimal
    created_at: datetime

    @field_serializer("sampled_at", "created_at")
    def utc_time(self, value):
        return utc_milliseconds(value)

    @field_serializer(*TEMPERATURE_FIELDS)
    def number(self, value):
        return json_number(value)


class TemperatureSamplesOut(ApiSchema):
    equipment_id: str
    items: list[TemperatureSampleOut]
