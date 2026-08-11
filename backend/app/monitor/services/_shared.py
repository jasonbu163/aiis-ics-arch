"""
文件路径: /backend/app/monitor/services/_shared.py
功能描述: Monitor 查询 Service 内部时间辅助函数
主要功能:
    - 统一时间序列化
    - 统一运行状态 stale 判断
"""
from datetime import datetime


def iso_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def is_stale(updated_at: datetime | None, stale_seconds: int = 10) -> bool:
    if updated_at is None:
        return True
    now = datetime.now(updated_at.tzinfo) if updated_at.tzinfo else datetime.now()
    return (now - updated_at).total_seconds() > stale_seconds
