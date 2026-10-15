"""
文件路径: /backend/app/project/models/project.py
功能描述: 项目、任务与里程碑数据库模型定义
主要功能:
    - 定义项目管理相关表结构
    - 使用 SQLAlchemy 2.0 现代风格
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """项目主表"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    progress: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    owner: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    tasks: Mapped[List["ProjectTask"]] = relationship(
        "ProjectTask", back_populates="project", cascade="all, delete-orphan"
    )
    milestones: Mapped[List["ProjectMilestone"]] = relationship(
        "ProjectMilestone", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectTask(Base, TimestampMixin):
    """项目任务表"""

    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="todo", index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", index=True)

    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    assignee: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")


class ProjectMilestone(Base, TimestampMixin):
    """项目里程碑表"""

    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reached: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    reached_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="milestones")
