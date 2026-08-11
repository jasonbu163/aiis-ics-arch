"""
文件路径: /backend/common/schema_base.py
功能描述: 统一的 Pydantic Schema 基类与跨端命名转换工具
主要功能:
    - 提供 snake_case 到 camelCase 的别名生成器
    - 统一前后端 Schema 的序列化/反序列化配置
"""
from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """将 snake_case 字段名转换为 camelCase。"""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class ApiSchema(BaseModel):
    """统一 API Schema，负责跨端 camelCase 别名。"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
