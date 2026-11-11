"""
文件路径: /backend/app/monitor/models/monitor.py
功能描述: Control Agent 现场事实与采集状态模型

本文件只保留跨项目可复用的 raw/latest/collector 事实层。
HMI、温度、能耗、过程曲线和生产实绩等业务语义由项目仓库自行建模。
"""
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database import Base


class MonitorCollectorState(Base):
    """Control Agent collector 心跳与采集指标；后端只读。"""

    __tablename__ = "monitor_collector_states"

    collector_key: Mapped[str] = mapped_column(String(80), primary_key=True)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    worker_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mode: Mapped[str] = mapped_column(String(30), nullable=False, default="mock")
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    target_interval_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    last_sample_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    buffered_failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dropped_sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_buffered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_replay_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_collect_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_write_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_loop_delay_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
