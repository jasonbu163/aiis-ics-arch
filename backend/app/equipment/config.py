"""单设备温控scope的模块本地懒配置；不缓存跨应用实例。"""
from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import resolve_env_file
from app.equipment.temperature_sample_domain import validate_identifier
from app.equipment.error_codes import TemperatureError
from common.exceptions import BusinessException


class TemperatureConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore", frozen=True)
    EQUIPMENT_TEMPERATURE_PILOT_ID: str = ""

    def allowed_equipment(self, requested=None):
        try:
            key = validate_identifier(self.EQUIPMENT_TEMPERATURE_PILOT_ID)
        except ValueError:
            raise BusinessException(TemperatureError.FORBIDDEN, code=403) from None
        if requested is not None and requested != key:
            raise BusinessException(TemperatureError.FORBIDDEN, code=403)
        return key


def get_temperature_config(request: Request):
    if not hasattr(request.app.state, "equipment_temperature_config"):
        request.app.state.equipment_temperature_config = TemperatureConfig(_env_file=resolve_env_file())
    return request.app.state.equipment_temperature_config
