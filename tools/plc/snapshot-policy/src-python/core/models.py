"""
文件路径: /tools/plc/snapshot-policy/src-python/core/models.py
功能描述: PLC 快照 raw/latest payload 范围策略工具的数据模型
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


POLICY_COLUMNS = [
    "db_number",
    "group_name",
    "name",
    "source_name",
    "type",
    "offset",
    "bit",
    "desc",
    "raw_enabled",
    "raw_policy",
    "latest_enabled",
    "reason",
]

POLICY_OPTIONS = ["every_sample", "on_change", "hourly"]


@dataclass(frozen=True)
class PlcPoint:
    """Normalized PLC point loaded from plc_points.yaml."""

    name: str
    db_number: int
    group_name: str
    data_type: str
    offset: int
    bit: int | None = None
    plc_key: str = ""
    source_name: str = ""
    desc: str = ""
    plc_metadata: dict[str, Any] = field(default_factory=dict)
    group_metadata: dict[str, Any] = field(default_factory=dict)
    point_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SnapshotPolicyRow:
    """Validated policy row from the review workbook."""

    point: PlcPoint
    raw_enabled: bool
    raw_policy: str
    latest_enabled: bool
    reason: str
