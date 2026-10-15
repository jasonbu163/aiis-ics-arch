"""本批回迁源码的有界legacy稳定key闭包；新模块使用自己domain/data_keys。"""
from enum import StrEnum

class PlanObservationStatus(StrEnum):
    """Plan owner observation states for field-linked production intent."""

    PLANNED = "planned"
    OBSERVED = "observed"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class PerformanceObservationStatus(StrEnum):
    """PLC 观察到的实绩当前状态。"""

    IN_PRODUCTION = "in_production"
    NOT_IN_PRODUCTION = "not_in_production"
    UNKNOWN = "unknown"

class PerformanceRecordSource(StrEnum):
    """实绩记录的首次来源。"""

    UNPLANNED_PLC = "unplanned_plc"
    MANUAL_ENTRY = "manual_entry"
    SPLIT_GENERATED = "split_generated"
    MERGE_GENERATED = "merge_generated"

class PerformanceEffectiveWeightSource(StrEnum):
    """实绩当前有效卷重来源。"""

    COLLECTED_WEIGHT = "collected_weight"
    MANUAL_OVERRIDE_WEIGHT = "manual_override_weight"
    SPLIT_GENERATED = "split_generated"
    MERGE_GENERATED = "merge_generated"

class PerformanceTransformType(StrEnum):
    """实绩卷材业务变换类型。"""

    SPLIT = "split"
    MERGE = "merge"

class PerformanceTransformStatus(StrEnum):
    """实绩卷材业务变换状态。"""

    COMMITTED = "committed"

class PerformanceLineageRole(StrEnum):
    """实绩卷材谱系边角色。"""

    SOURCE = "source"
    TARGET = "target"

class PerformanceCurrentOperabilityStatus(StrEnum):
    """实绩当前可操作状态。"""

    OPERABLE = "operable"
    CONSUMED_BY_SPLIT = "consumed_by_split"
    CONSUMED_BY_MERGE = "consumed_by_merge"
    LINEAGE_UNAVAILABLE = "lineage_unavailable"

class PerformanceLineageErrorCode(StrEnum):
    """实绩卷材谱系业务错误码。"""

    PERFORMANCE_NOT_FOUND = "performance_not_found"
    PERFORMANCE_TRANSFORM_NOT_FOUND = "performance_transform_not_found"
    PERFORMANCE_EFFECTIVE_WEIGHT_REQUIRED = "performance_effective_weight_required"
    PERFORMANCE_INSUFFICIENT_AVAILABLE_WEIGHT = "performance_insufficient_available_weight"
    PERFORMANCE_TRANSFORM_INVALID_CARDINALITY = "performance_transform_invalid_cardinality"
    PERFORMANCE_TRANSFORM_REQUIRES_FULL_SOURCE = "performance_transform_requires_full_source"
    PERFORMANCE_LINEAGE_DOUBLE_ROLE = "performance_lineage_double_role"
    PERFORMANCE_LINEAGE_CYCLE = "performance_lineage_cycle"

class PerformanceDurationSource(StrEnum):
    """实绩总用时派生来源。"""

    MANUAL_TIME = "manual_time"
    PLC_OBSERVED = "plc_observed"
    UNAVAILABLE = "unavailable"

class QualityGradeKey(StrEnum):
    """质量等级稳定 key。"""

    EXCELLENT = "excellent"
    FIRST_CLASS = "firstClass"
    QUALIFIED = "qualified"
    PENDING = "pending"

class DowntimeReasonKey(StrEnum):
    """停机原因稳定 key。"""

    SCHEDULED = "scheduled"
    COIL_CHANGE = "coilChange"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    OTHER = "other"

class ProductionTargetType(StrEnum):
    """生产目标类型稳定 key。"""

    OUTPUT = "output"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"

class PeriodType(StrEnum):
    """周期类型稳定 key。"""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class DefectLevelKey(StrEnum):
    """缺陷等级稳定 key。"""

    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class MaintenanceTypeKey(StrEnum):
    """维保类型稳定 key。"""

    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    HYDRAULIC = "hydraulic"
    THERMAL = "thermal"
    SURFACE = "surface"
    COOLING = "cooling"
    LIFTING = "lifting"
    ROUTINE = "routine"
    LEVEL_1 = "level1"
    LEVEL_2 = "level2"
    LEVEL_3 = "level3"

class DepartmentStatus(StrEnum):
    """部门状态稳定 key。"""

    ACTIVE = "active"
    INACTIVE = "inactive"

class EmployeeStatus(StrEnum):
    """员工状态稳定 key。"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LEFT = "left"

class AttendanceStatus(StrEnum):
    """考勤状态稳定 key。"""

    NORMAL = "normal"
    LATE = "late"
    ABSENT = "absent"
    LEAVE = "leave"

class RecruitmentStatus(StrEnum):
    """招聘状态稳定 key。"""

    OPEN = "open"
    CLOSED = "closed"
    PAUSED = "paused"

QUALITY_GRADE_LABEL_ALIASES = {
    "优等品": QualityGradeKey.EXCELLENT.value,
    "一等品": QualityGradeKey.FIRST_CLASS.value,
    "合格品": QualityGradeKey.QUALIFIED.value,
    "待复检": QualityGradeKey.PENDING.value,
}

DOWNTIME_REASON_LABEL_ALIASES = {
    "计划停机": DowntimeReasonKey.SCHEDULED.value,
    "换卷时间": DowntimeReasonKey.COIL_CHANGE.value,
    "换卷": DowntimeReasonKey.COIL_CHANGE.value,
    "换辊": DowntimeReasonKey.COIL_CHANGE.value,
    "设备故障": DowntimeReasonKey.EQUIPMENT.value,
    "原料不足": DowntimeReasonKey.MATERIAL.value,
    "待料": DowntimeReasonKey.MATERIAL.value,
    "质量问题": "qualityIssue",
    "quality_issue": "qualityIssue",
    "其他": DowntimeReasonKey.OTHER.value,
}

TARGET_TYPE_LABEL_ALIASES = {
    "产量": ProductionTargetType.OUTPUT.value,
    "质量": ProductionTargetType.QUALITY.value,
    "效率": ProductionTargetType.EFFICIENCY.value,
}

PERIOD_TYPE_LABEL_ALIASES = {
    "日": PeriodType.DAY.value,
    "天": PeriodType.DAY.value,
    "周": PeriodType.WEEK.value,
    "月": PeriodType.MONTH.value,
    "季度": PeriodType.QUARTER.value,
    "年": PeriodType.YEAR.value,
    "年度": PeriodType.YEAR.value,
}

DEFECT_LEVEL_LABEL_ALIASES = {
    "轻微": DefectLevelKey.MINOR.value,
    "低": DefectLevelKey.MINOR.value,
    "一般": DefectLevelKey.MAJOR.value,
    "中": DefectLevelKey.MAJOR.value,
    "严重": DefectLevelKey.CRITICAL.value,
    "高": DefectLevelKey.CRITICAL.value,
    "致命": DefectLevelKey.CRITICAL.value,
}

MAINTENANCE_TYPE_LABEL_ALIASES = {
    "机械设备": MaintenanceTypeKey.MECHANICAL.value,
    "加工设备": MaintenanceTypeKey.MECHANICAL.value,
    "开卷设备": MaintenanceTypeKey.MECHANICAL.value,
    "卷取设备": MaintenanceTypeKey.MECHANICAL.value,
    "电气设备": MaintenanceTypeKey.ELECTRICAL.value,
    "液压系统": MaintenanceTypeKey.HYDRAULIC.value,
    "热处理设备": MaintenanceTypeKey.THERMAL.value,
    "表面处理设备": MaintenanceTypeKey.SURFACE.value,
    "冷却设备": MaintenanceTypeKey.COOLING.value,
    "水泵系统": MaintenanceTypeKey.COOLING.value,
    "起重设备": MaintenanceTypeKey.LIFTING.value,
    "日常保养": MaintenanceTypeKey.ROUTINE.value,
    "一级保养": MaintenanceTypeKey.LEVEL_1.value,
    "二级保养": MaintenanceTypeKey.LEVEL_2.value,
    "三级保养": MaintenanceTypeKey.LEVEL_3.value,
}

DEPARTMENT_STATUS_LABEL_ALIASES = {
    "启用": DepartmentStatus.ACTIVE.value,
    "正常": DepartmentStatus.ACTIVE.value,
    "停用": DepartmentStatus.INACTIVE.value,
    "禁用": DepartmentStatus.INACTIVE.value,
}

EMPLOYEE_STATUS_LABEL_ALIASES = {
    "在职": EmployeeStatus.ACTIVE.value,
    "启用": EmployeeStatus.ACTIVE.value,
    "正常": EmployeeStatus.ACTIVE.value,
    "停用": EmployeeStatus.INACTIVE.value,
    "禁用": EmployeeStatus.INACTIVE.value,
    "离职": EmployeeStatus.LEFT.value,
}

ATTENDANCE_STATUS_LABEL_ALIASES = {
    "正常": AttendanceStatus.NORMAL.value,
    "出勤": AttendanceStatus.NORMAL.value,
    "迟到": AttendanceStatus.LATE.value,
    "缺勤": AttendanceStatus.ABSENT.value,
    "请假": AttendanceStatus.LEAVE.value,
}

RECRUITMENT_STATUS_LABEL_ALIASES = {
    "开放": RecruitmentStatus.OPEN.value,
    "招聘中": RecruitmentStatus.OPEN.value,
    "关闭": RecruitmentStatus.CLOSED.value,
    "已关闭": RecruitmentStatus.CLOSED.value,
    "暂停": RecruitmentStatus.PAUSED.value,
}

def normalize_target_type(value: str | None) -> str | None:
    """将目标类型兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return TARGET_TYPE_LABEL_ALIASES.get(value, value)

def normalize_period_type(value: str | None) -> str | None:
    """将周期类型兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return PERIOD_TYPE_LABEL_ALIASES.get(value, value)

def normalize_quality_grade(value: str | None) -> str | None:
    """将质量等级兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return QUALITY_GRADE_LABEL_ALIASES.get(value, value)

def normalize_downtime_reason(value: str | None) -> str | None:
    """将停机原因/类型兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return DOWNTIME_REASON_LABEL_ALIASES.get(value, value)

def normalize_defect_level(value: str | None) -> str | None:
    """将缺陷等级兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return DEFECT_LEVEL_LABEL_ALIASES.get(value, value)

def normalize_maintenance_type(value: str | None) -> str | None:
    """将维保类型兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return MAINTENANCE_TYPE_LABEL_ALIASES.get(value, value)

def normalize_department_status(value: str | None) -> str | None:
    """将部门状态兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return DEPARTMENT_STATUS_LABEL_ALIASES.get(value, value)

def normalize_employee_status(value: str | None) -> str | None:
    """将员工状态兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return EMPLOYEE_STATUS_LABEL_ALIASES.get(value, value)

def normalize_attendance_status(value: str | None) -> str | None:
    """将考勤状态兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return ATTENDANCE_STATUS_LABEL_ALIASES.get(value, value)

def normalize_recruitment_status(value: str | None) -> str | None:
    """将招聘状态兼容值归一化为稳定英文 key。"""
    if value is None:
        return None
    return RECRUITMENT_STATUS_LABEL_ALIASES.get(value, value)

def target_type_storage_values(value: str | None) -> tuple[str, ...]:
    """返回兼容查询同一目标类型所需的历史值和稳定 key。"""
    normalized = normalize_target_type(value)
    if normalized is None:
        return ()
    values = {normalized}
    values.update(label for label, key in TARGET_TYPE_LABEL_ALIASES.items() if key == normalized)
    if value:
        values.add(value)
    return tuple(values)

def period_type_storage_values(value: str | None) -> tuple[str, ...]:
    """返回兼容查询同一周期类型所需的历史值和稳定 key。"""
    normalized = normalize_period_type(value)
    if normalized is None:
        return ()
    values = {normalized}
    values.update(label for label, key in PERIOD_TYPE_LABEL_ALIASES.items() if key == normalized)
    if value:
        values.add(value)
    return tuple(values)

def quality_grade_storage_values(value: str | None) -> tuple[str, ...]:
    """返回兼容查询同一质量等级所需的历史值和稳定 key。"""
    normalized = normalize_quality_grade(value)
    if normalized is None:
        return ()
    values = {normalized}
    values.update(label for label, key in QUALITY_GRADE_LABEL_ALIASES.items() if key == normalized)
    if value:
        values.add(value)
    return tuple(values)

def maintenance_type_storage_values(value: str | None) -> tuple[str, ...]:
    """返回兼容查询同一维保类型所需的历史值和稳定 key。"""
    normalized = normalize_maintenance_type(value)
    if normalized is None:
        return ()
    values = {normalized}
    values.update(label for label, key in MAINTENANCE_TYPE_LABEL_ALIASES.items() if key == normalized)
    if value:
        values.add(value)
    return tuple(values)

def recruitment_status_storage_values(value: str | None) -> tuple[str, ...]:
    """返回兼容查询同一招聘状态所需的历史值和稳定 key。"""
    normalized = normalize_recruitment_status(value)
    if normalized is None:
        return ()
    values = {normalized}
    values.update(label for label, key in RECRUITMENT_STATUS_LABEL_ALIASES.items() if key == normalized)
    if value:
        values.add(value)
    return tuple(values)
