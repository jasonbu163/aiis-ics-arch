"""
文件路径: /backend/database/base.py
功能描述: SQLAlchemy 2.0 现代 ORM 基类配置
主要功能:
    - 提供类型安全的 Mapped 基类
    - 定义通用字段模板 (int_pk, timestamp, updated_at)
    - 自动生成蛇形表名
"""
import re
from datetime import datetime
from typing import Any, Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

# --- 通用类型注解模板 (SQLAlchemy 2.0 风格) ---
# 主键 ID
IntPk = Annotated[int, mapped_column(primary_key=True, index=True, autoincrement=True)]
# 常用字符串模板
Str50 = Annotated[str, mapped_column(nullable=False)]
Str100 = Annotated[str, mapped_column(nullable=False)]
Str255 = Annotated[str, mapped_column(nullable=False)]
# 时间戳
Timestamp = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]
# 自动更新的时间戳
UpdatedAt = Annotated[datetime, mapped_column(
    DateTime(timezone=True), 
    server_default=func.now(), 
    default=func.now(),
    onupdate=func.now()
)]

class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 ORM 基类
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动将类名转换为蛇形表名"""
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name

    def to_dict(self) -> dict[str, Any]:
        """将模型实例转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

class TimestampMixin:
    """时间戳混入类"""
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

__all__ = [
    "Base",
    "TimestampMixin",
    "IntPk",
    "Timestamp",
    "UpdatedAt",
]

