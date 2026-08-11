"""
文件路径: /backend/app/user/schemas/user_out.py
功能描述: 用户输出 Schema 定义
主要功能:
    - 用户响应结构
    - 用户状态派生字段
"""
from datetime import datetime

from pydantic import ConfigDict

from app.user.schemas.user_in import UserBase


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    status: str = "active"

    @classmethod
    def model_validate(cls, obj):
        instance = super().model_validate(obj)
        instance.status = "active" if obj.is_active else "inactive"
        return instance

