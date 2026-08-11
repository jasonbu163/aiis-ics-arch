"""
文件路径: /tools/plc/s7-virtual-plc/src-python/core/runtime.py
功能描述: S7 虚拟 PLC 内存刷新和值写入逻辑
"""
from __future__ import annotations

import hashlib
import math
import time
from datetime import datetime
from typing import Any

from snap7.util import set_bool, set_dint, set_dt, set_int, set_real, set_string

from core.models import NUMERIC_TYPES, TYPE_SIZES, SimulationRule, VirtualDbArea, VirtualPoint
from core.profile import default_simulated_value, profile_key


def apply_numeric_type(point: VirtualPoint, value: float) -> int | float:
    if point.data_type == "Real":
        return round(float(value), 2)
    if point.data_type == "USInt":
        return max(0, min(255, int(round(value))))
    if point.data_type in {"UInt", "Word"}:
        return max(0, min(65535, int(round(value))))
    if point.data_type == "UDInt":
        return max(0, min(4294967295, int(round(value))))
    return int(round(value))


def stable_unit_interval(seed_text: str) -> float:
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def simulated_value(point: VirtualPoint, rule: SimulationRule, tick: int, started_at: float) -> Any:
    if not rule.enabled:
        return None
    elapsed = max(0.0, time.time() - started_at)
    if rule.mode == "fixed":
        return rule.fixed_value
    if rule.mode == "random_range":
        bucket = int(elapsed // max(rule.hold_seconds, 0.1))
        factor = stable_unit_interval(f"{profile_key(point)}:{bucket}")
        assert rule.min_value is not None and rule.max_value is not None
        return apply_numeric_type(point, rule.min_value + (rule.max_value - rule.min_value) * factor)
    if rule.mode == "wave":
        assert rule.min_value is not None and rule.max_value is not None
        center = (rule.min_value + rule.max_value) / 2
        amplitude = (rule.max_value - rule.min_value) / 2
        value = center + amplitude * math.sin((elapsed / max(rule.period_seconds, 0.1)) * math.tau)
        return apply_numeric_type(point, value)
    if rule.mode == "sequence":
        total_duration = sum(step.duration_seconds for step in rule.sequence_values)
        cursor = elapsed % total_duration
        for step in rule.sequence_values:
            if cursor < step.duration_seconds:
                return step.value
            cursor -= step.duration_seconds
        return rule.sequence_values[-1].value
    if rule.mode == "now":
        return datetime.now()
    return default_simulated_value(point, tick, started_at)


def write_value(memory: bytearray, point: VirtualPoint, value: Any) -> None:
    offset = point.offset
    data_type = point.data_type

    if data_type == "Bool":
        set_bool(memory, offset, point.bit, bool(value))
    elif data_type == "Int":
        set_int(memory, offset, int(value))
    elif data_type == "DInt":
        set_dint(memory, offset, int(value))
    elif data_type in {"UInt", "Word"}:
        memory[offset:offset + 2] = int(value).to_bytes(2, byteorder="big", signed=False)
    elif data_type == "USInt":
        memory[offset] = int(value) & 0xFF
    elif data_type == "UDInt":
        memory[offset:offset + 4] = int(value).to_bytes(4, byteorder="big", signed=False)
    elif data_type == "Real":
        set_real(memory, offset, float(value))
    elif data_type == "String":
        max_chars = max(1, min((point.length or TYPE_SIZES["String"]) - 2, 254))
        set_string(memory, offset, str(value)[:max_chars], max_chars)
    elif data_type == "Date_And_Time":
        set_dt(memory, offset, value if isinstance(value, datetime) else datetime.now())


def refresh_areas(
    areas: dict[int, VirtualDbArea],
    rules: dict[str, SimulationRule],
    tick: int,
    started_at: float,
) -> dict[str, Any]:
    updated = 0
    skipped = 0
    unsupported: dict[str, int] = {}
    sample_values: list[str] = []

    for area in areas.values():
        for point in area.points:
            try:
                rule = rules[profile_key(point)]
                value = simulated_value(point, rule, tick, started_at)
                if value is None:
                    skipped += 1
                    continue
                write_value(area.memory, point, value)
                updated += 1
                if len(sample_values) < 5:
                    sample_values.append(f"DB{point.db_number}.{point.name}={value}")
            except Exception:
                unsupported[point.data_type] = unsupported.get(point.data_type, 0) + 1

    return {
        "updated": updated,
        "skipped": skipped,
        "unsupported": unsupported,
        "samples": sample_values,
    }
