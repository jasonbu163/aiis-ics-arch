"""严格camelCase完整样本输入，不接受缺测、补零或别名覆盖。"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict
from common.schema_base import ApiSchema, to_camel
from app.equipment.temperature_sample_domain import normalize_number, normalize_sampled_at, validate_identifier

TemperatureNumber = Annotated[Decimal, BeforeValidator(normalize_number)]
Identifier = Annotated[str, BeforeValidator(validate_identifier)]
SourceTime = Annotated[datetime, BeforeValidator(normalize_sampled_at)]


class TemperatureSampleIn(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sample_id: Identifier
    sampled_at: SourceTime
    quality: Literal["good"]
    zone1_set: TemperatureNumber
    zone1_act: TemperatureNumber
    zone2_set: TemperatureNumber
    zone2_act: TemperatureNumber
    zone3_set: TemperatureNumber
    zone3_act: TemperatureNumber
    zone4_set: TemperatureNumber
    zone4_act: TemperatureNumber
    zone5_set: TemperatureNumber
    zone5_act: TemperatureNumber
