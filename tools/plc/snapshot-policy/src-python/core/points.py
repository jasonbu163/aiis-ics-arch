"""
文件路径: /tools/plc/snapshot-policy/src-python/core/points.py
功能描述: 从 plc_points.yaml 加载 PLC 点位合同
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from core.models import PlcPoint


def load_points(config_path: Path) -> list[PlcPoint]:
    if not config_path.exists():
        raise FileNotFoundError(f"PLC config not found: {config_path}")

    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(config, dict) or not config:
        raise ValueError(f"PLC config is empty or invalid: {config_path}")

    points: list[PlcPoint] = []
    for plc_key, plc_config in config.items():
        if not isinstance(plc_config, dict):
            continue
        plc_metadata = {key: value for key, value in plc_config.items() if key != "groups"}
        groups = (plc_config or {}).get("groups") or []
        for group in groups:
            if not isinstance(group, dict):
                continue
            db_number = int(group["db_number"])
            group_name = str(group.get("name") or f"DB{db_number}")
            group_metadata = {key: value for key, value in group.items() if key != "points"}
            for raw_point in group.get("points") or []:
                points.append(normalize_point(raw_point, str(plc_key), db_number, group_name, plc_metadata, group_metadata))

    if not points:
        raise ValueError(f"PLC config has no points: {config_path}")
    return points


def normalize_point(
    point: dict[str, Any],
    plc_key: str,
    db_number: int,
    group_name: str,
    plc_metadata: dict[str, Any],
    group_metadata: dict[str, Any],
) -> PlcPoint:
    data_type = str(point.get("type") or "").strip()
    offset = int(point.get("offset") or 0)
    bit = int(point["bit"]) if data_type == "Bool" and point.get("bit") is not None else None
    return PlcPoint(
        name=str(point.get("name") or point.get("source_name") or f"DB{db_number}_{offset}"),
        db_number=db_number,
        group_name=group_name,
        data_type=data_type,
        offset=offset,
        bit=bit,
        plc_key=plc_key,
        source_name=str(point.get("source_name") or ""),
        desc=str(point.get("desc") or ""),
        plc_metadata=dict(plc_metadata),
        group_metadata=dict(group_metadata),
        point_metadata=dict(point),
    )
