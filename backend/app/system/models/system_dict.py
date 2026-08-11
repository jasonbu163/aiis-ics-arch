"""
文件路径: /backend/app/system/models/system_dict.py
功能描述: 系统字典数据模型定义
主要功能:
    - 使用 SQLAlchemy 2.0 现代风格 (Mapped, mapped_column, relationship)
"""
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, IntPk, Timestamp, UpdatedAt


class SysDict(Base):
    """系统字典"""

    __tablename__ = "sys_dicts"

    id: Mapped[IntPk]
    dict_type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    dict_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    items: Mapped[List["SysDictItem"]] = relationship("SysDictItem", back_populates="dict", cascade="all, delete-orphan")


class SysDictItem(Base):
    """字典项"""

    __tablename__ = "sys_dict_items"

    id: Mapped[IntPk]
    dict_id: Mapped[int] = mapped_column(ForeignKey("sys_dicts.id"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    sort: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[Timestamp]

    dict: Mapped["SysDict"] = relationship("SysDict", back_populates="items")
