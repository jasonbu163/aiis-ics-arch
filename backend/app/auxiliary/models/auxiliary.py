"""
文件路径: /backend/app/auxiliary/models/auxiliary.py
功能描述: 辅助管理数据库模型定义
主要功能:
    - 定义班组模型
    - 定义班次模型
    - 定义停机记录模型
    - 定义排班规则模型
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, IntPk, Timestamp, UpdatedAt


class ShiftTeam(Base):
    """班组模型"""

    __tablename__ = "shift_teams"

    id: Mapped[IntPk]
    team_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="班组名称")
    leader: Mapped[Optional[str]] = mapped_column(String(50), comment="班组长")
    members: Mapped[int] = mapped_column(default=0, comment="成员数量")
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment="联系电话")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    shifts: Mapped[List["Shift"]] = relationship(back_populates="team")


class Shift(Base):
    """班次模型"""

    __tablename__ = "shifts"

    id: Mapped[IntPk]
    team_id: Mapped[int] = mapped_column(ForeignKey("shift_teams.id"), nullable=False, index=True, comment="班组ID")
    date: Mapped[datetime] = mapped_column(Date, nullable=False, comment="日期")
    day_leader: Mapped[Optional[str]] = mapped_column(String(50), comment="白班负责人")
    night_leader: Mapped[Optional[str]] = mapped_column(String(50), comment="夜班负责人")
    day_members: Mapped[Optional[str]] = mapped_column(String(500), comment="白班成员")
    night_members: Mapped[Optional[str]] = mapped_column(String(500), comment="夜班成员")
    remark: Mapped[Optional[str]] = mapped_column(String(500), comment="备注")

    created_at: Mapped[Timestamp]

    team: Mapped["ShiftTeam"] = relationship(back_populates="shifts")


class StopRecord(Base):
    """停机记录模型"""

    __tablename__ = "stop_records"

    id: Mapped[IntPk]
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="开始时间")
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="结束时间")
    duration: Mapped[Optional[int]] = mapped_column(comment="持续时间(分钟)")
    shift: Mapped[Optional[str]] = mapped_column(String(50), comment="班次")
    operator: Mapped[Optional[str]] = mapped_column(String(50), comment="操作员")
    reason: Mapped[Optional[str]] = mapped_column(String(500), comment="停机原因")
    stop_type: Mapped[Optional[str]] = mapped_column(String(50), comment="停机类型")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态")
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]


class ShiftRule(Base):
    """排班规则模型"""

    __tablename__ = "shift_rules"

    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(50), default="default", comment="规则名称")
    shift_mode: Mapped[str] = mapped_column(String(20), default="two_shift", comment="班制类型")
    cycle_name: Mapped[str] = mapped_column(String(50), default="四班三运转", comment="轮班周期")
    day_shift_start: Mapped[str] = mapped_column(String(20), default="08:00", comment="白班开始时间")
    day_shift_end: Mapped[str] = mapped_column(String(20), default="20:00", comment="白班结束时间")
    middle_shift_start: Mapped[Optional[str]] = mapped_column(String(20), comment="中班开始时间")
    middle_shift_end: Mapped[Optional[str]] = mapped_column(String(20), comment="中班结束时间")
    night_shift_start: Mapped[str] = mapped_column(String(20), default="20:00", comment="夜班开始时间")
    night_shift_end: Mapped[str] = mapped_column(String(20), default="08:00", comment="夜班结束时间")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]
