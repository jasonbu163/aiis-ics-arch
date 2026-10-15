"""
File Path: /backend/app/plan/domain.py
Description: Pure Plan-domain rules used by API and import/linkage services.
Main Features:
    - Canonical coil number normalization
    - Plan observation status policy
    - XLSX field contract shared by template, import, and export
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from common.data_keys import PlanObservationStatus


PLAN_OBSERVABLE_STATUSES = {
    PlanObservationStatus.PLANNED.value,
    PlanObservationStatus.OBSERVED.value,
}


@dataclass(frozen=True)
class PlanXlsxColumn:
    key: str
    header: str
    aliases: tuple[str, ...]
    required: bool
    example: Any


PLAN_XLSX_COLUMNS: tuple[PlanXlsxColumn, ...] = (
    PlanXlsxColumn("coil_no", "coilNo", ("coil_no", "coilNo", "料卷号", "卷号"), True, "B650001"),
    PlanXlsxColumn("grade", "grade", ("grade", "steelGrade", "钢种", "牌号"), True, "Q235"),
    PlanXlsxColumn("spec", "spec", ("spec", "规格"), True, "10.5*1500"),
    PlanXlsxColumn("weight", "weight", ("weight", "plannedWeight", "重量"), True, Decimal("25.0000")),
    PlanXlsxColumn("thickness", "thickness", ("thickness", "厚度"), True, Decimal("10.500")),
    PlanXlsxColumn("width", "width", ("width", "宽度"), True, Decimal("1500.00")),
    PlanXlsxColumn(
        "material_status",
        "materialStatus",
        ("material_status", "materialStatus", "物料状态"),
        False,
        "special",
    ),
    PlanXlsxColumn("density", "density", ("density", "密度"), False, Decimal("0")),
    PlanXlsxColumn("entry_length", "entryLength", ("entry_length", "entryLength", "入口长度"), False, Decimal("0")),
    PlanXlsxColumn(
        "uncoiler1_tension",
        "uncoiler1Tension",
        ("uncoiler1_tension", "uncoiler1Tension", "开卷机1张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "exit_tension",
        "exitTension",
        ("exit_tension", "exitTension", "出口张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "process1_tension",
        "process1Tension",
        ("process1_tension", "process1Tension", "工艺段1张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "entry_loop_tension",
        "entryLoopTension",
        ("entry_loop_tension", "entryLoopTension", "入口活套张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "exit_loop_tension",
        "exitLoopTension",
        ("exit_loop_tension", "exitLoopTension", "出口活套张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "entry_unit_tension",
        "entryUnitTension",
        ("entry_unit_tension", "entryUnitTension", "入口单位张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "entry_loop_unit_tension",
        "entryLoopUnitTension",
        ("entry_loop_unit_tension", "entryLoopUnitTension", "入口活套单位张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "process_unit_tension",
        "processUnitTension",
        ("process_unit_tension", "processUnitTension", "工艺单位张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "exit_loop_unit_tension",
        "exitLoopUnitTension",
        ("exit_loop_unit_tension", "exitLoopUnitTension", "出口活套单位张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn(
        "exit_unit_tension",
        "exitUnitTension",
        ("exit_unit_tension", "exitUnitTension", "出口单位张力"),
        False,
        Decimal("0"),
    ),
    PlanXlsxColumn("priority", "priority", ("priority", "优先级"), False, 5),
    PlanXlsxColumn("remark", "remark", ("remark", "备注"), False, ""),
)


def canonicalize_coil_no(value: object) -> str | None:
    """Normalize a coil number for matching without changing display storage."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.casefold()


def is_valid_coil_no(value: object) -> bool:
    """Validate display coil number while preserving its original storage value."""
    text = str(value or "").strip()
    return bool(text) and not any(ord(char) < 32 or ord(char) == 127 for char in text)


def ensure_same_canonical_coil(left: object, right: object) -> bool:
    left_canonical = canonicalize_coil_no(left)
    right_canonical = canonicalize_coil_no(right)
    return left_canonical is not None and left_canonical == right_canonical


def is_observable_plan_status(status: str | None) -> bool:
    return status in PLAN_OBSERVABLE_STATUSES


def normalize_xlsx_header(value: object) -> str:
    return str(value or "").strip().casefold()


def decimal_cell_value(value: object) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
