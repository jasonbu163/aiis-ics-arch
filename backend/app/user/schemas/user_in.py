"""
文件路径: /backend/app/user/schemas/user_in.py
功能描述: 用户输入 Schema 定义
主要功能:
    - 用户创建入参
    - 用户更新入参
    - 用户基础字段定义
"""
from pydantic import Field

from common.schema_base import ApiSchema


class UserBase(ApiSchema):
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="operator")
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(ApiSchema):
    name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None


class UserPasswordReset(ApiSchema):
    new_password: str | None = None
