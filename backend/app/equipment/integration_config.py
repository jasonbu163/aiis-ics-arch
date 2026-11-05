"""默认关闭、空准入与未采用配置；每应用懒加载，不构成真实身份认证。"""
import json
from pathlib import Path
from common.integration.storage import parse_adoption_manifest
from app.equipment.integration_storage import FIXED_COLUMNS
from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict
from common.exceptions import BusinessException
from common.integration.envelope import identifier
from settings import resolve_env_file
from app.equipment.integration_error_codes import IntegrationError


class IntegrationConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore", frozen=True)
    EQUIPMENT_INTEGRATION_ENABLED: bool = False
    EQUIPMENT_INTEGRATION_EQUIPMENT_IDS_JSON: str = "[]"
    EQUIPMENT_INTEGRATION_PRODUCER_IDS_JSON: str = "[]"
    EQUIPMENT_INTEGRATION_STORAGE_PROFILE: str = "unadopted"
    EQUIPMENT_INTEGRATION_ADOPTION_FILE: str = ""

    def require_ready(self, equipment_id, producer_id):
        try:
            devices = json.loads(self.EQUIPMENT_INTEGRATION_EQUIPMENT_IDS_JSON)
            producers = json.loads(self.EQUIPMENT_INTEGRATION_PRODUCER_IDS_JSON)
            for values in (devices, producers):
                if not isinstance(values, list) or not values:
                    raise ValueError("empty or invalid scope")
                for key in values:
                    identifier(key)
            if len(devices) > 256:
                raise ValueError("device scope too large")
            if not self.EQUIPMENT_INTEGRATION_ENABLED or equipment_id not in devices or producer_id not in producers:
                raise ValueError("scope rejected")
        except (ValueError, TypeError):
            raise BusinessException(IntegrationError.SCOPE_REJECTED, code=403) from None
        adoption = self.adoption()
        if adoption is None:
            raise BusinessException(IntegrationError.NOT_READY, code=503)
        return adoption

    def adoption(self):
        """默认旧路径无文件IO；误配拒绝，不能偷偷回退UTC。"""
        profile = self.EQUIPMENT_INTEGRATION_STORAGE_PROFILE
        filename = self.EQUIPMENT_INTEGRATION_ADOPTION_FILE
        if profile == "unadopted" and not filename:
            return None
        try:
            if profile != "shanghai-v1" or not filename or not Path(filename).is_absolute():
                raise ValueError("adoption required")
            # 有界读取，拒绝重复key/非JSON/过大文件，不记录内容。
            from common.integration.http import strict_json
            with Path(filename).open("rb") as stream:
                document = strict_json(stream.read(65537))
            manifest=parse_adoption_manifest(document, "equipment")
            from app.equipment.integration_storage import FIXED_COLUMN_DIGEST
            if manifest["fixedColumnDigest"]!=FIXED_COLUMN_DIGEST:
                raise ValueError("fixed column mismatch")
            return manifest
        except Exception:
            raise BusinessException(IntegrationError.NOT_READY, code=503) from None



def get_integration_config(request: Request):
    if not hasattr(request.app.state, "equipment_integration_config"):
        request.app.state.equipment_integration_config = IntegrationConfig(_env_file=resolve_env_file())
    return request.app.state.equipment_integration_config
