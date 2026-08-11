"""
文件路径: /tools/plc/point-mapping/src-python/converter/converter.py
功能描述: TIA DB 点表到 PLC YAML 配置的项目级转换工具
主要功能:
    - 读取 TIA 导出的 Excel 多 sheet 点表
    - 默认生成 tools/plc/point-mapping/outputs/plc_points.yaml 点位合同
    - 优先读取 DB配置 sheet，保留 offset、bit、TIA 访问诊断信息和原始变量名信息
    - 使用 DB号 + 原始名称 / Struct 路径 + 类型生成稳定点位 key
"""
from __future__ import annotations

from collections import Counter
from numbers import Number
import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from source_parser.tia import SourceRowSpec, expand_block_rows, normalize_type_name, parse_tia_sources


TOOL_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = TOOL_ROOT.parents[2]
DEFAULT_INPUT_PATH = TOOL_ROOT / "inputs" / "DB.xlsx"
DEFAULT_OUTPUT_PATH = TOOL_ROOT / "outputs" / "plc_points.yaml"

SUPPORTED_TYPES = {
    "Bool",
    "Int",
    "DInt",
    "Real",
    "String",
    "UInt",
    "USInt",
    "UDInt",
    "Word",
}

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
}

REQUIRED_COLUMNS = {"名称", "数据类型", "偏移量"}
CONFIG_SHEET_NAME = "DB配置"
CONFIG_COLUMNS = {"sheet_name", "db_number"}
TIA_ACCESSIBLE_COLUMN = "从HMI/OPC UA/Web API可访问"
TIA_WRITABLE_COLUMN = "从HMI/OPC UA/Web API可写"

GROUP_NAME_MAP = {
    "过程数据": "Process_Data",
    "配方数据": "Recipe_Data",
}

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SOURCE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or str(value).strip() == ""


def _address_name(db_number: int, byte_offset: int, bit_offset: int | None, data_type: str) -> str:
    if bit_offset is not None:
        return f"DB{db_number}_B{byte_offset}_{bit_offset}_{data_type}"
    return f"DB{db_number}_B{byte_offset}_{data_type}"


def _is_legal_source_path(source_path: tuple[str, ...]) -> bool:
    return bool(source_path) and all(SOURCE_SEGMENT_RE.fullmatch(segment) for segment in source_path)


def _new_point_name(
    source_path: tuple[str, ...],
    db_number: int,
    byte_offset: int,
    bit_offset: int | None,
    data_type: str,
) -> tuple[str, str, str]:
    if _is_legal_source_path(source_path):
        middle = "_".join(source_path)
        return f"DB{db_number}_{middle}_{data_type}", "semantic_path", "legal_source_path"
    return (
        _address_name(db_number, byte_offset, bit_offset, data_type),
        "address_fallback",
        "invalid_source_path",
    )


def _safe_group_name(raw_name: str, db_number: int) -> str:
    mapped = GROUP_NAME_MAP.get(raw_name)
    if mapped:
        return mapped
    if IDENTIFIER_RE.match(raw_name):
        return raw_name
    return f"DB{db_number}"


def _parse_sheet_metadata(sheet_name: str) -> tuple[int, str] | None:
    match = re.search(r"(?:^|[-_\s])DB\s*(\d+)(?:$|[-_\s])", sheet_name, re.IGNORECASE)
    if not match:
        return None
    db_number = int(match.group(1))
    raw_group_name = sheet_name[: match.start()].strip(" -_") or f"DB{db_number}"
    return db_number, _safe_group_name(raw_group_name, db_number)


def _is_point_sheet(frame: pd.DataFrame) -> bool:
    return REQUIRED_COLUMNS.issubset(set(frame.columns))


def _parse_offset(offset_value: Any, data_type: str) -> tuple[int, int | None] | None:
    if _is_blank(offset_value):
        return None
    offset_text = str(offset_value).strip()
    if data_type == "Bool" and "." in offset_text:
        byte_text, bit_text = offset_text.split(".", 1)
        return int(float(byte_text)), int(float(bit_text))
    return int(float(offset_text)), None


def _normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if _is_blank(value):
        return None
    if isinstance(value, Number):
        number = float(value)
        if number == 1.0:
            return True
        if number == 0.0:
            return False
    text = str(value).strip().lower()
    if text in {"true", "1", "1.0", "yes"}:
        return True
    if text in {"false", "0", "0.0", "no"}:
        return False
    return None


def _normalize_enabled(value: Any) -> bool:
    normalized = _normalize_bool(value)
    return True if normalized is None else normalized


def _load_db_config(workbook: dict[str, pd.DataFrame]) -> dict[str, tuple[int, str]]:
    config_frame = workbook.get(CONFIG_SHEET_NAME)
    if config_frame is None or not CONFIG_COLUMNS.issubset(set(config_frame.columns)):
        return {}

    config: dict[str, tuple[int, str]] = {}
    for _, row in config_frame.iterrows():
        sheet_name = row.get("sheet_name")
        db_number = row.get("db_number")
        if _is_blank(sheet_name) or _is_blank(db_number) or not _normalize_enabled(row.get("enabled")):
            continue

        sheet_key = str(sheet_name).strip()
        number = int(float(str(db_number).strip()))
        raw_group_name = row.get("group_name")
        raw_db_name = row.get("db_name")
        if _is_blank(raw_group_name):
            raw_group_name = raw_db_name if not _is_blank(raw_db_name) else sheet_key

        config[sheet_key] = (number, _safe_group_name(str(raw_group_name).strip(), number))
    return config


def _load_source_db_config(workbook: dict[str, pd.DataFrame]) -> dict[str, tuple[str, bool]]:
    config_frame = workbook.get(CONFIG_SHEET_NAME)
    if config_frame is None or "sheet_name" not in config_frame.columns:
        return {}

    config: dict[str, tuple[str, bool]] = {}
    for _, row in config_frame.iterrows():
        sheet_name = row.get("sheet_name")
        if _is_blank(sheet_name):
            continue
        sheet_key = str(sheet_name).strip()
        raw_db_name = row.get("db_name")
        db_name = str(raw_db_name).strip() if not _is_blank(raw_db_name) else sheet_key
        config[sheet_key] = (db_name, _normalize_enabled(row.get("enabled")))
    return config


def _collect_source_comparable_rows(frame: pd.DataFrame) -> list[tuple[int, int, str, str]]:
    rows: list[tuple[int, int, str, str]] = []
    for frame_index, row in frame.iterrows():
        name = row.get("名称")
        data_type = row.get("数据类型")
        if _is_blank(name) or _is_blank(data_type):
            continue
        rows.append(
            (
                int(frame_index),
                int(frame_index) + 2,
                str(name).strip().strip('"'),
                normalize_type_name(data_type),
            )
        )
    return rows


def _build_source_path_lookup(
    workbook: dict[str, pd.DataFrame],
    db_source_path: str | Path | None,
    udt_source_path: str | Path | None,
) -> dict[tuple[str, int], tuple[str, ...]]:
    if not db_source_path and not udt_source_path:
        return {}

    model = parse_tia_sources(
        Path(db_source_path) if db_source_path else None,
        Path(udt_source_path) if udt_source_path else None,
    )
    configs = _load_source_db_config(workbook)
    lookup: dict[tuple[str, int], tuple[str, ...]] = {}

    for sheet_name, frame in workbook.items():
        if sheet_name == CONFIG_SHEET_NAME or not _is_point_sheet(frame):
            continue
        db_name, enabled = configs.get(sheet_name, (sheet_name, True))
        if not enabled:
            continue

        block = model.db_blocks.get(db_name) or model.db_blocks.get(sheet_name)
        if block is None:
            raise ValueError(f"{sheet_name}: DATA_BLOCK not found for DB name {db_name!r}")

        source_rows, source_warnings = expand_block_rows(block, model.udt_types)
        if source_warnings:
            raise ValueError(f"{sheet_name}: {source_warnings[0]}")
        _fill_source_lookup(sheet_name, frame, source_rows, lookup)

    return lookup


def _fill_source_lookup(
    sheet_name: str,
    frame: pd.DataFrame,
    source_rows: list[SourceRowSpec],
    lookup: dict[tuple[str, int], tuple[str, ...]],
) -> None:
    workbook_rows = _collect_source_comparable_rows(frame)
    if len(source_rows) != len(workbook_rows):
        raise ValueError(
            f"{sheet_name}: source row count {len(source_rows)} != workbook row count {len(workbook_rows)}"
        )

    for source_row, workbook_row in zip(source_rows, workbook_rows, strict=True):
        frame_index, excel_row, workbook_name, workbook_type = workbook_row
        if source_row.name != workbook_name:
            raise ValueError(
                f"{sheet_name}!{excel_row}: expected name {source_row.name!r} from {'.'.join(source_row.path)}, got {workbook_name!r}"
            )
        if normalize_type_name(source_row.data_type) != normalize_type_name(workbook_type):
            raise ValueError(
                f"{sheet_name}!{excel_row}: {workbook_name!r} expected type {source_row.data_type!r}, got {workbook_type!r}"
            )
        lookup[(sheet_name, frame_index)] = source_row.path


def _build_point(row: pd.Series, db_number: int, source_path: tuple[str, ...] | None = None) -> dict[str, Any] | None:
    raw_name = str(row["名称"]).strip()
    data_type = str(row["数据类型"]).strip()
    if raw_name == "Static" or data_type not in SUPPORTED_TYPES:
        return None

    offset = _parse_offset(row["偏移量"], data_type)
    if offset is None:
        return None

    byte_offset, bit_offset = offset
    point_name, _strategy, _reason = _new_point_name(
        source_path or (raw_name,),
        db_number,
        byte_offset,
        bit_offset,
        data_type,
    )
    point: dict[str, Any] = {
        "name": point_name,
        "source_name": raw_name,
        "type": data_type,
        "offset": byte_offset,
    }
    if bit_offset is not None:
        point["bit"] = bit_offset
    if data_type == "String":
        point["length"] = TYPE_SIZES["String"]

    comment = row.get("注释")
    if not _is_blank(comment):
        point["desc"] = str(comment).strip()
    elif point["name"] != raw_name:
        point["desc"] = raw_name

    tia_accessible = _normalize_bool(row.get(TIA_ACCESSIBLE_COLUMN))
    if tia_accessible is not None:
        point["tia_accessible"] = tia_accessible
    tia_writable = _normalize_bool(row.get(TIA_WRITABLE_COLUMN))
    if tia_writable is not None:
        point["tia_writable"] = tia_writable

    return point


def _group_size(points: list[dict[str, Any]]) -> int:
    if not points:
        return 0
    max_end = 0
    for point in points:
        point_size = int(point.get("length") or TYPE_SIZES.get(point["type"], 1))
        max_end = max(max_end, int(point["offset"]) + point_size)
    return max_end


def _resolve_global_name_collisions(groups: list[dict[str, Any]]) -> None:
    points_by_name: Counter[str] = Counter()
    for group in groups:
        for point in group["points"]:
            points_by_name[str(point["name"])] += 1

    duplicate_names = {name for name, count in points_by_name.items() if count > 1}
    if not duplicate_names:
        return

    for group in groups:
        db_number = int(group["db_number"])
        for point in group["points"]:
            if point["name"] not in duplicate_names:
                continue
            point["name"] = _address_name(
                db_number,
                int(point["offset"]),
                point.get("bit"),
                str(point["type"]),
            )
            if "desc" not in point and point.get("source_name"):
                point["desc"] = point["source_name"]

    resolved_counts: Counter[str] = Counter()
    for group in groups:
        for point in group["points"]:
            resolved_counts[str(point["name"])] += 1
    unresolved = sorted(name for name, count in resolved_counts.items() if count > 1)
    if unresolved:
        raise ValueError(f"duplicate generated PLC point names after address fallback: {unresolved[:20]}")


def convert_excel_to_yaml(
    file_path: str | Path,
    yaml_path: str | Path,
    plc_ip: str = "127.0.0.1",
    rack: int = 0,
    slot: int = 1,
    db_source_path: str | Path | None = None,
    udt_source_path: str | Path | None = None,
) -> dict[str, Any]:
    """读取 TIA Excel 点表并生成 collector 使用的 YAML 配置。"""
    workbook = pd.read_excel(file_path, sheet_name=None)
    db_config = _load_db_config(workbook)
    source_path_lookup = _build_source_path_lookup(workbook, db_source_path, udt_source_path)
    groups: list[dict[str, Any]] = []

    for sheet_name, frame in workbook.items():
        if sheet_name == CONFIG_SHEET_NAME:
            continue
        sheet_metadata = db_config.get(sheet_name) or _parse_sheet_metadata(sheet_name)
        if sheet_metadata is None or not _is_point_sheet(frame):
            continue
        db_number, group_name = sheet_metadata
        points: list[dict[str, Any]] = []
        for _, row in frame.iterrows():
            if _is_blank(row.get("名称")) or _is_blank(row.get("数据类型")):
                continue
            source_path = source_path_lookup.get((sheet_name, int(row.name)))
            point = _build_point(row, db_number, source_path)
            if point:
                points.append(point)

        groups.append({
            "name": group_name,
            "db_number": db_number,
            "start": 0,
            "size": _group_size(points),
            "point_count": len(points),
            "points": points,
        })

    _resolve_global_name_collisions(groups)
    point_count = sum(len(group["points"]) for group in groups)

    yaml_structure = {
        "PLC_1": {
            "ip": plc_ip,
            "port": 102,
            "rack": rack,
            "slot": slot,
            "point_count": point_count,
            "groups": groups,
        }
    }

    output_path = Path(yaml_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file_obj:
        yaml.safe_dump(
            yaml_structure,
            file_obj,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    return yaml_structure
