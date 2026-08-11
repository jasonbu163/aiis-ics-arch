"""
文件路径: /tools/plc/s7-virtual-plc/src-python/core/loader.py
功能描述: 从 plc_points.yaml 加载虚拟 DB 区和点位定义
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from core.models import TYPE_SIZES, VirtualDbArea, VirtualPoint


def point_size(point: dict[str, Any]) -> int:
    data_type = str(point.get("type", "")).strip()
    return int(point.get("length") or TYPE_SIZES.get(data_type, 1))


def load_plc_config(config_path: Path, plc_key: str) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"PLC config not found: {config_path}")

    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(config, dict) or not config:
        raise ValueError(f"PLC config is empty or invalid: {config_path}")
    if plc_key not in config:
        raise ValueError(f"PLC key not found: {plc_key}")

    plc_config = config[plc_key] or {}
    if not isinstance(plc_config, dict):
        raise ValueError(f"PLC config is invalid under key: {plc_key}")
    return plc_config


def load_virtual_areas(config_path: Path, plc_key: str) -> dict[int, VirtualDbArea]:
    plc_config = load_plc_config(config_path, plc_key)

    groups = plc_config.get("groups") or []
    if not groups:
        raise ValueError(f"PLC config has no groups under key: {plc_key}")

    area_sizes: dict[int, int] = {}
    pending_points: dict[int, list[VirtualPoint]] = {}

    for group in groups:
        db_number = int(group["db_number"])
        group_start = int(group.get("start") or 0)
        group_size = int(group.get("size") or 0)
        group_name = str(group.get("name") or f"DB{db_number}")
        area_sizes[db_number] = max(area_sizes.get(db_number, 0), group_start + group_size)

        for point in group.get("points") or []:
            data_type = str(point.get("type", "")).strip()
            offset = int(point.get("offset") or 0)
            end_offset = offset + point_size(point)
            area_sizes[db_number] = max(area_sizes.get(db_number, 0), end_offset)
            pending_points.setdefault(db_number, []).append(
                VirtualPoint(
                    name=str(point.get("name") or point.get("source_name") or f"DB{db_number}_{offset}"),
                    data_type=data_type,
                    offset=offset,
                    db_number=db_number,
                    group_name=group_name,
                    bit=int(point.get("bit") or 0),
                    length=int(point["length"]) if point.get("length") else None,
                    source_name=str(point.get("source_name") or ""),
                    desc=str(point.get("desc") or ""),
                )
            )

    areas: dict[int, VirtualDbArea] = {}
    for db_number, size in sorted(area_sizes.items()):
        if size <= 0:
            continue
        areas[db_number] = VirtualDbArea(
            db_number=db_number,
            memory=bytearray(size),
            points=pending_points.get(db_number, []),
        )
    return areas
