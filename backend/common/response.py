"""
文件路径: /backend/common/response.py
功能描述: 共享响应模型
主要功能:
    - 提供统一的 API 响应格式
    - 统一响应 data 内部字段的 camelCase 序列化
    - SuccessResponse / ErrorResponse / PaginatedResponse 响应模型
"""
from collections.abc import Mapping
from pydantic import BaseModel, Field, field_serializer
from typing import Generic, TypeVar, Any
from datetime import datetime

from common.schema_base import to_camel

T = TypeVar('T')


def serialize_api_data(value: Any) -> Any:
    """递归序列化 API data，兜住 data: Any 导致的别名丢失。"""
    if isinstance(value, BaseModel):
        value = value.model_dump(by_alias=True)
    if isinstance(value, Mapping):
        return {
            to_camel(key) if isinstance(key, str) else key: serialize_api_data(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [serialize_api_data(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_api_data(item) for item in value]
    return value


class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Any | None = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))

    @field_serializer("data")
    def serialize_data(self, data: Any) -> Any:
        return serialize_api_data(data)


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

    @field_serializer("items")
    def serialize_items(self, items: list[Any]) -> list[Any]:
        return serialize_api_data(items)


class SuccessResponse(BaseModel):
    """成功响应"""
    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))

    @field_serializer("data")
    def serialize_data(self, data: Any) -> Any:
        return serialize_api_data(data)


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: str | None = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))


class StandardResponse(BaseModel, Generic[T]):
    """工业级统一响应模型 (对齐 backend-arch 规范)"""
    code: int = 200
    message: str = "success"
    data: T | None = None

    @field_serializer("data")
    def serialize_data(self, data: T | None) -> Any:
        return serialize_api_data(data)


__all__ = [
    "ResponseModel",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "StandardResponse",
    "serialize_api_data",
]
