"""
文件路径: /backend/app/user/models/token_blacklist.py
功能描述: Token 黑名单数据模型定义
主要功能:
    - 定义 Token 黑名单表结构
    - 支持用户登出时将 Token 加入黑名单
    - 记录 Token 过期时间
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database import Base


class TokenBlacklist(Base):
    """Token 黑名单模型"""
    __tablename__ = "token_blacklist"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

