"""
文件路径: /tools/plc/point-mapping/src-python/validation/struct_validation.py
功能描述: 校验 XLSX 点位表与 TIA DB/UDT 结构的一致性
主要功能:
    - 读取 DB配置 并定位对应 DATA_BLOCK
    - 对比 Struct / UDT / Array 展开后的完整工作簿行序列
    - 输出 JSON Lines 友好的诊断摘要
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from source_parser.tia import (
    SourceRowSpec,
    TiaSourceModel,
    expand_block_rows,
    normalize_type_name,
    parse_tia_sources,
)


CONFIG_SHEET_NAME = "DB配置"
REQUIRED_COLUMNS = {"名称", "数据类型", "偏移量"}


@dataclass(frozen=True)
class WorkbookDbConfig:
    sheet_name: str
    db_name: str
    enabled: bool


@dataclass(frozen=True)
class WorkbookRow:
    excel_row: int
    name: str
    data_type: str


@dataclass
class StructValidationResult:
    applied: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    samples: dict[str, list[str]] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_event_payload(self) -> dict[str, Any]:
        return {
            "applied": self.applied,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "summary": self.summary,
            "samples": self.samples,
        }


def validate_workbook_source_context(
    workbook_path: Path,
    db_source_path: Path | None,
    udt_source_path: Path | None,
) -> StructValidationResult:
    model = parse_tia_sources(db_source_path, udt_source_path)
    workbook = pd.read_excel(workbook_path, sheet_name=None)
    configs = _load_db_config(workbook)
    result = StructValidationResult(applied=True)
    totals = {
        "db_blocks": len(model.db_blocks),
        "udt_types": len(model.udt_types),
        "sheets_checked": 0,
        "source_rows": 0,
        "workbook_rows": 0,
        "matched_rows": 0,
        "struct_rows": 0,
        "udt_instance_rows": 0,
        "array_rows": 0,
        "nested_leaf_rows": 0,
    }
    nested_samples: list[str] = []

    for sheet_name, frame in workbook.items():
        if sheet_name == CONFIG_SHEET_NAME or not REQUIRED_COLUMNS.issubset(set(frame.columns)):
            continue
        config = configs.get(sheet_name, WorkbookDbConfig(sheet_name, sheet_name, True))
        if not config.enabled:
            continue
        block = model.db_blocks.get(config.db_name) or model.db_blocks.get(sheet_name)
        if block is None:
            result.errors.append(f"{sheet_name}: DATA_BLOCK not found for DB name {config.db_name!r}")
            continue
        if block.optimized_access is True:
            result.errors.append(f"{sheet_name}: DATA_BLOCK {block.name!r} has optimized access enabled")
        elif block.optimized_access is None:
            result.warnings.append(f"{sheet_name}: DATA_BLOCK {block.name!r} has no S7_Optimized_Access marker")

        source_rows, source_warnings = expand_block_rows(block, model.udt_types)
        for warning in source_warnings:
            result.errors.append(f"{sheet_name}: {warning}")
        workbook_rows = _collect_workbook_rows(frame)
        _compare_rows(sheet_name, source_rows, workbook_rows, result)

        totals["sheets_checked"] += 1
        totals["source_rows"] += len(source_rows)
        totals["workbook_rows"] += len(workbook_rows)
        totals["matched_rows"] += min(len(source_rows), len(workbook_rows))
        totals["struct_rows"] += sum(1 for row in source_rows if row.kind == "struct")
        totals["udt_instance_rows"] += sum(1 for row in source_rows if row.kind == "udt")
        totals["array_rows"] += sum(1 for row in source_rows if row.kind in {"array", "array_element"})
        totals["nested_leaf_rows"] += sum(1 for row in source_rows if len(row.path) >= 3 and row.kind in {"scalar", "array_element"})
        nested_samples.extend(_nested_path_samples(source_rows, limit=5 - len(nested_samples)))

    result.summary = totals
    result.samples = {
        "errors": result.errors[:8],
        "warnings": result.warnings[:8],
        "nested_paths": nested_samples[:5],
    }
    return result


def _load_db_config(workbook: dict[str, pd.DataFrame]) -> dict[str, WorkbookDbConfig]:
    frame = workbook.get(CONFIG_SHEET_NAME)
    if frame is None or "sheet_name" not in frame.columns:
        return {}

    configs: dict[str, WorkbookDbConfig] = {}
    for _, row in frame.iterrows():
        sheet_name = row.get("sheet_name")
        if _is_blank(sheet_name):
            continue
        sheet_key = str(sheet_name).strip()
        db_name = row.get("db_name")
        enabled = _normalize_enabled(row.get("enabled"))
        configs[sheet_key] = WorkbookDbConfig(
            sheet_name=sheet_key,
            db_name=str(db_name).strip() if not _is_blank(db_name) else sheet_key,
            enabled=enabled,
        )
    return configs


def _collect_workbook_rows(frame: pd.DataFrame) -> list[WorkbookRow]:
    rows: list[WorkbookRow] = []
    for row_index, row in frame.iterrows():
        name = row.get("名称")
        data_type = row.get("数据类型")
        if _is_blank(name) or _is_blank(data_type):
            continue
        rows.append(
            WorkbookRow(
                excel_row=int(row_index) + 2,
                name=str(name).strip().strip('"'),
                data_type=normalize_type_name(data_type),
            )
        )
    return rows


def _compare_rows(
    sheet_name: str,
    source_rows: list[SourceRowSpec],
    workbook_rows: list[WorkbookRow],
    result: StructValidationResult,
) -> None:
    if len(source_rows) != len(workbook_rows):
        result.errors.append(
            f"{sheet_name}: source row count {len(source_rows)} != workbook row count {len(workbook_rows)}"
        )

    pair_count = min(len(source_rows), len(workbook_rows))
    for index in range(pair_count):
        expected = source_rows[index]
        actual = workbook_rows[index]
        if expected.name != actual.name:
            result.errors.append(
                f"{sheet_name}!{actual.excel_row}: expected name {expected.name!r} from {'.'.join(expected.path)}, got {actual.name!r}"
            )
            continue
        if normalize_type_name(expected.data_type) != normalize_type_name(actual.data_type):
            result.errors.append(
                f"{sheet_name}!{actual.excel_row}: {actual.name!r} expected type {expected.data_type!r}, got {actual.data_type!r}"
            )


def _nested_path_samples(source_rows: list[SourceRowSpec], limit: int) -> list[str]:
    if limit <= 0:
        return []
    samples: list[str] = []
    for row in source_rows:
        if len(row.path) < 3 or row.kind not in {"scalar", "array_element"}:
            continue
        samples.append(".".join(row.path))
        if len(samples) >= limit:
            break
    return samples


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or str(value).strip() == ""


def _normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if _is_blank(value):
        return None
    text = str(value).strip().casefold()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _normalize_enabled(value: Any) -> bool:
    normalized = _normalize_bool(value)
    return True if normalized is None else normalized
