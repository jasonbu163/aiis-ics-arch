"""
文件路径: /backend/app/system/schemas/system_dict.py
功能描述: 系统字典数据验证模型定义
主要功能:
    - 定义字典创建、更新、响应的数据结构
    - 定义字典项创建、更新、响应的数据结构
"""
import datetime
from typing import List, Optional

from common.schema_base import ApiSchema


class SysDictBase(ApiSchema):
    dict_type: str
    dict_name: str
    description: Optional[str] = None
    status: str = "active"


class SysDictCreate(SysDictBase):
    pass


class SysDictUpdate(ApiSchema):
    dict_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SysDictResponse(SysDictBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class SysDictItemBase(ApiSchema):
    dict_id: int
    label: str
    value: str
    sort: int = 0
    status: str = "active"
    remark: Optional[str] = None


class SysDictItemCreate(SysDictItemBase):
    pass


class SysDictItemUpdate(ApiSchema):
    label: Optional[str] = None
    value: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class SysDictItemResponse(SysDictItemBase):
    id: int
    created_at: datetime.datetime
