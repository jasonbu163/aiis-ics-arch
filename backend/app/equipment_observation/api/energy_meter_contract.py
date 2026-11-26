"""管理员表计定义创建与部分更新请求。"""
from typing import Annotated

from pydantic import Field

from ..schemas import Input


MeterId = Annotated[str, Field(min_length=1, max_length=64)]
MeterName = Annotated[str, Field(min_length=1, max_length=128)]


class CreateEnergyMeter(Input):
    meter_id: MeterId
    name_zh: MeterName
    name_en: MeterName
    read_roles: list[str] = Field(default_factory=lambda: ["admin"])


class PatchEnergyMeter(Input):
    meter_id: MeterId
    name_zh: MeterName | None = None
    name_en: MeterName | None = None
    read_roles: list[str] | None = None


class EnergyMeterData(Input):
    meter_id: MeterId
    name_zh: MeterName
    name_en: MeterName
    read_roles: list[str]


class EnergyMeterResponse(Input):
    code: int
    message: str
    data: EnergyMeterData


class EnergyMeterListResponse(Input):
    code: int
    message: str
    data: list[EnergyMeterData]


class EnergyMeterError(Input):
    code: int
    message: str
    data: None
    error_code: str


METER_READ_ERRORS = {401: {"description": "Missing or invalid user Bearer"},
                     403: {"description": "Administrator permission required"},
                     503: {"description": "Energy data unavailable", "model": EnergyMeterError}}
METER_CHANGE_ERRORS = {**METER_READ_ERRORS, 422: {"description": "Invalid request", "model": EnergyMeterError}}
