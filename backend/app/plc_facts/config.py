"""模块本地默认关闭设置；仅消费公共dotenv路径解析器。"""
import json
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import resolve_env_file
from .error_codes import FactsError

class FactsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=resolve_env_file(), extra='ignore')
    PLC_FACTS_ENABLED: bool = False
    PLC_FACTS_PLC_IDS_JSON: str = '[]'
    PLC_FACTS_STORAGE_PROFILE: str = 'unadopted'
    PLC_FACTS_CURSOR_HMAC_KEY: str = ''

    def admit(self, plc_ids):
        try:
            scope = json.loads(self.PLC_FACTS_PLC_IDS_JSON)
            if not isinstance(scope,list) or len(scope)>256 or any(not isinstance(x,str) or not x or x.strip()!=x for x in scope):
                raise ValueError()
        except (ValueError,TypeError):
            raise FactsError('scope_rejected',403) from None
        if not self.PLC_FACTS_ENABLED or not scope or not set(plc_ids) <= set(scope):
            raise FactsError('scope_rejected',403)
        import re
        if self.PLC_FACTS_STORAGE_PROFILE != 'mysql84_shanghai_v1' or not re.fullmatch('[0-9a-f]{64}',self.PLC_FACTS_CURSOR_HMAC_KEY):
            raise FactsError('not_ready',503)

@lru_cache
def get_settings():
    return FactsSettings()
