"""本模块单业务设备scope，每应用首次懒固定；缺省关闭。"""
from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import resolve_env_file
from app.performance.mapping_domain import identifier
from app.performance.mapping_error_codes import MappingError
from common.exceptions import BusinessException

class MappingConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore", frozen=True)
    PERFORMANCE_MAPPING_INGEST_ID: str = ""

    def allowed_equipment(self, requested):
        try:
            key = identifier(self.PERFORMANCE_MAPPING_INGEST_ID)
        except ValueError:
            raise BusinessException(MappingError.FORBIDDEN, code=403) from None
        if requested != key:
            raise BusinessException(MappingError.FORBIDDEN, code=403)
        return key

def get_mapping_config(request: Request):
    if not hasattr(request.app.state, "performance_mapping_config"):
        request.app.state.performance_mapping_config = MappingConfig(_env_file=resolve_env_file())
    return request.app.state.performance_mapping_config
