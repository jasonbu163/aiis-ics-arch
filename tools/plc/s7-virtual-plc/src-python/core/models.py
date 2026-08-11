"""
文件路径: /tools/plc/s7-virtual-plc/src-python/core/models.py
功能描述: S7 虚拟 PLC 工具的点位、DB 内存区和仿真规则模型
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


PROFILE_COLUMNS = [
    "enabled",
    "db_number",
    "group_name",
    "name",
    "source_name",
    "type",
    "offset",
    "bit",
    "desc",
    "mode",
    "min_value",
    "max_value",
    "fixed_value",
    "hold_seconds",
    "period_seconds",
    "sequence_values",
]
MODE_OPTIONS = ["fixed", "random_range", "wave", "sequence", "now"]
NUMERIC_TYPES = {"USInt", "Int", "UInt", "Word", "DInt", "UDInt", "Real"}

TYPE_SIZES = {
    "Bool": 1,
    "USInt": 1,
    "Int": 2,
    "UInt": 2,
    "Word": 2,
    "DInt": 4,
    "UDInt": 4,
    "Real": 4,
    "String": 256,
    "Date_And_Time": 8,
}


@dataclass
class VirtualPoint:
    """Normalized point definition loaded from plc_points.yaml."""

    name: str
    data_type: str
    offset: int
    db_number: int
    group_name: str
    bit: int = 0
    length: int | None = None
    source_name: str = ""
    desc: str = ""


@dataclass
class VirtualDbArea:
    """In-memory DB area registered into the S7 server."""

    db_number: int
    memory: bytearray
    points: list[VirtualPoint] = field(default_factory=list)


@dataclass
class SequenceStep:
    value: Any
    duration_seconds: float


@dataclass
class SimulationRule:
    """Validated in-memory simulation rule loaded from the XLSX profile."""

    enabled: bool
    mode: str
    min_value: float | None = None
    max_value: float | None = None
    fixed_value: Any = None
    hold_seconds: float = 1.0
    period_seconds: float = 60.0
    sequence_values: list[SequenceStep] = field(default_factory=list)
