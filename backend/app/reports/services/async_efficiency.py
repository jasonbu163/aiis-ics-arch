"""
文件路径: /backend/app/reports/services/async_efficiency.py
功能描述: 报表效率统计异步服务
主要功能:
    - 加载效率统计数据集
    - 计算 OEE、产量、停机和趋势数据
    - 生成效率统计接口响应数据
"""
import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auxiliary.models import StopRecord
from app.performance.models import Performance
from app.plan.models import Plan
from app.reports.crud.async_efficiency import EfficiencyCRUD
from common.data_keys import DowntimeReasonKey, normalize_downtime_reason


SHIFT_LABELS = ("白班", "中班", "夜班")
SHIFT_KEY_LABELS = {
    "dayShift": "白班",
    "middleShift": "中班",
    "nightShift": "夜班",
    "day": "白班",
    "middle": "中班",
    "night": "夜班",
}
DEFAULT_STOP_TYPE_KEYS = tuple(item.value for item in DowntimeReasonKey)


def infer_shift_label(target_time: Optional[datetime.datetime]) -> str:
    if not target_time:
        return "白班"

    hour = target_time.hour
    if 8 <= hour < 16:
        return "白班"
    if 16 <= hour < 24:
        return "中班"
    return "夜班"


def as_day(value: datetime.date | datetime.datetime) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    return value


def normalize_shift_label(shift: Optional[str]) -> Optional[str]:
    if not shift:
        return None
    return SHIFT_KEY_LABELS.get(shift, shift)


def normalize_stop_type(stop_type: Optional[str]) -> str:
    normalized = normalize_downtime_reason(stop_type)
    if normalized in DEFAULT_STOP_TYPE_KEYS:
        return normalized
    return DowntimeReasonKey.OTHER.value


def parse_stat_range(start_date: Optional[str], end_date: Optional[str], default_days: int = 7):
    today = datetime.datetime.now().date()
    end_day = datetime.datetime.fromisoformat(end_date).date() if end_date else today
    start_day = datetime.datetime.fromisoformat(start_date).date() if start_date else end_day - datetime.timedelta(days=default_days - 1)

    if start_day > end_day:
        start_day, end_day = end_day, start_day

    return (
        datetime.datetime.combine(start_day, datetime.datetime.min.time()),
        datetime.datetime.combine(end_day, datetime.datetime.max.time()),
        start_day,
        end_day,
    )


def round_metric(value: float, digits: int = 1) -> float:
    return round(float(value or 0), digits)


def calc_change(current: float, previous: float) -> float:
    if not previous:
        return 0.0
    return round_metric((current - previous) / previous * 100)


def calc_percentage(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round_metric(numerator / denominator * 100)


def performance_running_hours(performance: Performance) -> float:
    if not performance.start_time or not performance.end_time or performance.end_time <= performance.start_time:
        return 0.0
    return (performance.end_time - performance.start_time).total_seconds() / 3600


def stop_duration_hours(stop_record: StopRecord) -> float:
    if stop_record.duration:
        return float(stop_record.duration) / 60
    if stop_record.start_time and stop_record.end_time and stop_record.end_time > stop_record.start_time:
        return (stop_record.end_time - stop_record.start_time).total_seconds() / 3600
    return 0.0


def performance_output(performance: Performance) -> float:
    value = float(performance.output_quantity or 0)
    return value if value > 0 else 1.0


def qualified_output(performance: Performance) -> float:
    value = float(performance.qualified_quantity or 0)
    if value > 0:
        return value
    return 1.0 if float(performance.quality_score or 0) >= 60 else 0.0


def calculate_period_metrics(performances: list[Performance], stop_records: list[StopRecord], planned_hours: float):
    processed_coils = len(performances)
    running_hours = sum(performance_running_hours(perf) for perf in performances)
    downtime = sum(stop_duration_hours(stop) for stop in stop_records)

    actual_output = sum(performance_output(perf) for perf in performances)
    qualified = sum(qualified_output(perf) for perf in performances)
    defect = max(actual_output - qualified, 0)

    efficiency_values = [float(perf.efficiency_rate) for perf in performances if perf.efficiency_rate is not None]
    performance_pct = round_metric(sum(efficiency_values) / len(efficiency_values)) if efficiency_values else 0.0

    theoretical_output = actual_output / (performance_pct / 100) if performance_pct > 0 else actual_output
    speed_loss = max(theoretical_output - actual_output, 0)
    availability = calc_percentage(running_hours, planned_hours)
    quality = calc_percentage(qualified, actual_output)
    oee = round_metric(availability * performance_pct * quality / 10000)

    return {
        "plannedTime": round_metric(planned_hours),
        "runningTime": round_metric(running_hours),
        "downtime": round_metric(downtime),
        "processedCoils": processed_coils,
        "availability": availability,
        "performance": performance_pct,
        "quality": quality,
        "oee": oee,
        "theoreticalOutput": round_metric(theoretical_output),
        "actualOutput": round_metric(actual_output),
        "speedLoss": round_metric(speed_loss),
        "totalOutput": round_metric(actual_output),
        "qualifiedOutput": round_metric(qualified),
        "defectOutput": round_metric(defect),
    }


def build_efficiency_groups(
    performances: list[Performance],
    stop_records: list[StopRecord],
    start_day: datetime.date,
    end_day: datetime.date,
    group_by: str,
    shift_filter: Optional[str],
):
    grouped_performances: dict[tuple, list[Performance]] = {}
    grouped_stops: dict[tuple, list[StopRecord]] = {}

    for perf in performances:
        perf_day = as_day(perf.production_date)
        perf_shift = infer_shift_label(perf.start_time)
        key = (perf_day, perf_shift) if group_by == "shift" else (perf_day,)
        grouped_performances.setdefault(key, []).append(perf)

    for stop in stop_records:
        stop_day = stop.start_time.date()
        stop_shift = infer_shift_label(stop.start_time)
        key = (stop_day, stop_shift) if group_by == "shift" else (stop_day,)
        grouped_stops.setdefault(key, []).append(stop)

    items = []
    trend = []
    current_day = start_day
    active_shifts = [shift_filter] if shift_filter else list(SHIFT_LABELS)

    while current_day <= end_day:
        day_key = (current_day,)
        daily_metrics = calculate_period_metrics(
            grouped_performances.get(day_key, []),
            grouped_stops.get(day_key, []),
            24.0,
        )
        trend.append({
            "date": current_day.isoformat(),
            "availability": daily_metrics["availability"],
            "performance": daily_metrics["performance"],
            "quality": daily_metrics["quality"],
            "oee": daily_metrics["oee"],
        })

        if group_by == "day":
            if daily_metrics["processedCoils"] or daily_metrics["downtime"]:
                items.append({
                    "date": current_day.isoformat(),
                    **{key: value for key, value in daily_metrics.items() if key not in {"theoreticalOutput", "actualOutput", "speedLoss", "totalOutput", "qualifiedOutput", "defectOutput"}},
                })
        else:
            for shift_name in active_shifts:
                shift_key = (current_day, shift_name)
                metrics = calculate_period_metrics(
                    grouped_performances.get(shift_key, []),
                    grouped_stops.get(shift_key, []),
                    8.0,
                )
                if metrics["processedCoils"] or metrics["downtime"]:
                    items.append({
                        "date": current_day.isoformat(),
                        "shift": shift_name,
                        **{key: value for key, value in metrics.items() if key not in {"theoreticalOutput", "actualOutput", "speedLoss", "totalOutput", "qualifiedOutput", "defectOutput"}},
                    })
        current_day += datetime.timedelta(days=1)

    return items, trend


def build_downtime_analysis(stop_records: list[StopRecord]):
    distribution = {key: 0.0 for key in DEFAULT_STOP_TYPE_KEYS}
    for stop in stop_records:
        distribution[normalize_stop_type(stop.stop_type)] += stop_duration_hours(stop)

    return [
        {"name": name, "value": round_metric(value)}
        for name, value in distribution.items()
        if value > 0
    ]


async def load_efficiency_dataset(
    db: AsyncSession,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    shift: Optional[str] = None,
):
    crud = EfficiencyCRUD(db)
    performances = await crud.list_performances(start_dt, end_dt)
    if shift:
        performances = [perf for perf in performances if infer_shift_label(perf.start_time) == shift]

    stop_records = await crud.list_stop_records(start_dt, end_dt)
    if shift:
        stop_records = [record for record in stop_records if infer_shift_label(record.start_time) == shift]

    return performances, stop_records


async def build_efficiency_response(
    db: AsyncSession,
    start_date: Optional[str],
    end_date: Optional[str],
    shift: Optional[str],
    group_by: str = "day",
):
    shift = normalize_shift_label(shift)
    start_dt, end_dt, start_day, end_day = parse_stat_range(start_date, end_date)
    performances, stop_records = await load_efficiency_dataset(db, start_dt, end_dt, shift)
    planned_hours = ((end_day - start_day).days + 1) * (8 if shift else 24)
    summary = calculate_period_metrics(performances, stop_records, float(planned_hours))
    items, trend = build_efficiency_groups(performances, stop_records, start_day, end_day, group_by, shift)

    summary_payload = {
        "totalRunningTime": summary["runningTime"],
        "downtime": summary["downtime"],
        "processedCoils": summary["processedCoils"],
        "oee": summary["oee"],
        "availability": summary["availability"],
        "performance": summary["performance"],
        "quality": summary["quality"],
        "plannedTime": summary["plannedTime"],
        "actualTime": summary["runningTime"],
        "downtimeLoss": summary["downtime"],
        "theoreticalOutput": summary["theoreticalOutput"],
        "actualOutput": summary["actualOutput"],
        "speedLoss": summary["speedLoss"],
        "totalOutput": summary["totalOutput"],
        "qualifiedOutput": summary["qualifiedOutput"],
        "defectOutput": summary["defectOutput"],
    }

    return {
        "summary": summary_payload,
        "items": items,
        "trend": trend,
        "downtimeAnalysis": build_downtime_analysis(stop_records),
    }


async def build_efficiency_overview_response(
    db: AsyncSession,
    start_date: Optional[str],
    end_date: Optional[str],
    shift: Optional[str],
):
    shift = normalize_shift_label(shift)
    current_start_dt, current_end_dt, current_start_day, current_end_day = parse_stat_range(start_date, end_date)
    current_perfs, current_stops = await load_efficiency_dataset(db, current_start_dt, current_end_dt, shift)
    current_planned_hours = ((current_end_day - current_start_day).days + 1) * (8 if shift else 24)
    current_metrics = calculate_period_metrics(current_perfs, current_stops, float(current_planned_hours))

    period_days = (current_end_day - current_start_day).days + 1
    previous_end_day = current_start_day - datetime.timedelta(days=1)
    previous_start_day = previous_end_day - datetime.timedelta(days=period_days - 1)
    previous_start_dt = datetime.datetime.combine(previous_start_day, datetime.datetime.min.time())
    previous_end_dt = datetime.datetime.combine(previous_end_day, datetime.datetime.max.time())
    previous_perfs, previous_stops = await load_efficiency_dataset(db, previous_start_dt, previous_end_dt, shift)
    previous_planned_hours = period_days * (8 if shift else 24)
    previous_metrics = calculate_period_metrics(previous_perfs, previous_stops, float(previous_planned_hours))

    return {
        "totalRunningTime": current_metrics["runningTime"],
        "runningTimeChange": calc_change(current_metrics["runningTime"], previous_metrics["runningTime"]),
        "oee": current_metrics["oee"],
        "oeeChange": calc_change(current_metrics["oee"], previous_metrics["oee"]),
        "processedCoils": current_metrics["processedCoils"],
        "coilsChange": calc_change(current_metrics["processedCoils"], previous_metrics["processedCoils"]),
        "downtime": current_metrics["downtime"],
        "downtimeChange": calc_change(current_metrics["downtime"], previous_metrics["downtime"]),
    }


async def ensure_efficiency_test_plan(db: AsyncSession) -> Plan:
    result = await db.execute(
        select(Plan)
        .where(Plan.coil_no.like("EFFTEST-PLAN-%"))
        .order_by(Plan.id.asc())
        .limit(1)
    )
    plan = result.scalar_one_or_none()
    if plan:
        return plan

    plan = Plan(
        coil_no=f"EFFTEST-PLAN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        grade="SPHC",
        spec="2.0*1250*C",
        weight=Decimal("22.0000"),
        thickness=Decimal("2.000"),
        width=Decimal("1250.00"),
        material_status="special",
        density=Decimal("7.85"),
        entry_length=Decimal("1420.00"),
        uncoiler1_tension=Decimal("12.00"),
        exit_tension=Decimal("18.00"),
        process1_tension=Decimal("16.00"),
        entry_loop_tension=Decimal("10.00"),
        exit_loop_tension=Decimal("10.00"),
        entry_unit_tension=Decimal("1.2500"),
        entry_loop_unit_tension=Decimal("1.1000"),
        process_unit_tension=Decimal("1.4000"),
        exit_loop_unit_tension=Decimal("1.1000"),
        exit_unit_tension=Decimal("1.3000"),
        status="completed",
        priority=5,
        remark="效率统计测试数据计划",
    )
    db.add(plan)
    await db.flush()
    return plan


async def generate_efficiency_test_data(
    db: AsyncSession,
    start_date: Optional[str],
    end_date: Optional[str],
    shift: Optional[str] = None,
):
    shift = normalize_shift_label(shift)
    start_dt, end_dt, start_day, end_day = parse_stat_range(start_date, end_date)
    plan = await ensure_efficiency_test_plan(db)
    now_key = datetime.datetime.now().strftime("%H%M%S")
    shift_windows = [
        ("白班", 8, 6),
        ("中班", 16, 6),
        ("夜班", 0, 5),
    ]

    await db.execute(
        delete(Performance).where(
            and_(
                Performance.production_date >= start_day,
                Performance.production_date <= end_day,
                Performance.remark == "efficiency-test-data",
            )
        ).execution_options(synchronize_session=False)
    )
    await db.execute(
        delete(StopRecord).where(
            and_(
                StopRecord.start_time <= end_dt,
                StopRecord.end_time >= start_dt,
                StopRecord.reason == "效率统计测试数据",
            )
        ).execution_options(synchronize_session=False)
    )

    performance_count = 0
    stop_count = 0
    current_day = start_day
    while current_day <= end_day:
        day_index = (current_day - start_day).days
        for shift_name, start_hour, run_hours in shift_windows:
            if shift and shift_name != shift:
                continue

            start_time = datetime.datetime.combine(current_day, datetime.time(hour=start_hour))
            end_time = start_time + datetime.timedelta(hours=run_hours, minutes=20 + day_index % 20)
            coil_no = f"EFFTEST-{current_day.strftime('%Y%m%d')}-{shift_name}-{now_key}"
            quality_score = Decimal(str(92 - (day_index % 3) * 2))
            performance_rate = Decimal(str(86 + (day_index % 4) * 2))
            output_quantity = Decimal("1.0000")
            qualified_quantity = Decimal("1.0000") if quality_score >= 90 else Decimal("0.9000")

            db.add(Performance(
                plan_id=plan.id,
                coil_no=coil_no,
                parent_coil_no=coil_no,
                grade="SPHC",
                spec="2.0*1250*C",
                weight=Decimal(str(20 + day_index % 5)).quantize(Decimal("0.0001")),
                total_length=Decimal("1420.00"),
                diameter=Decimal("1250.00"),
                density=Decimal("7.850"),
                production_date=current_day,
                start_time=start_time,
                end_time=end_time,
                output_quantity=output_quantity,
                qualified_quantity=qualified_quantity,
                efficiency_rate=performance_rate,
                quality_score=quality_score,
                is_split=False,
                remark="efficiency-test-data",
            ))
            performance_count += 1

            stop_minutes = 18 + (day_index % 4) * 6
            stop_start = end_time + datetime.timedelta(minutes=12)
            stop_end = stop_start + datetime.timedelta(minutes=stop_minutes)
            stop_type = [
                DowntimeReasonKey.COIL_CHANGE.value,
                DowntimeReasonKey.EQUIPMENT.value,
                DowntimeReasonKey.MATERIAL.value,
                DowntimeReasonKey.SCHEDULED.value,
            ][day_index % 4]
            db.add(StopRecord(
                start_time=stop_start,
                end_time=stop_end,
                duration=stop_minutes,
                shift=shift_name,
                operator="system",
                reason="效率统计测试数据",
                stop_type=stop_type,
                status="completed",
            ))
            stop_count += 1
        current_day += datetime.timedelta(days=1)

    await db.commit()
    return {
        "performanceCount": performance_count,
        "stopRecordCount": stop_count,
        "startDate": start_dt.date().isoformat(),
        "endDate": end_dt.date().isoformat(),
    }


async def ensure_efficiency_seed_data(
    db: AsyncSession,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    shift: Optional[str] = None,
) -> None:
    start_day = start_dt.date()
    end_day = end_dt.date()
    real_perf_result = await db.execute(
        select(Performance.id)
        .where(
            and_(
                Performance.production_date >= start_day,
                Performance.production_date <= end_day,
                or_(Performance.remark.is_(None), Performance.remark != "efficiency-test-data"),
            )
        )
        .limit(1)
    )
    if real_perf_result.scalar_one_or_none():
        return

    real_stop_result = await db.execute(
        select(StopRecord.id)
        .where(
            and_(
                StopRecord.start_time <= end_dt,
                func.coalesce(StopRecord.end_time, StopRecord.start_time) >= start_dt,
                or_(StopRecord.reason.is_(None), StopRecord.reason != "效率统计测试数据"),
            )
        )
        .limit(1)
    )
    if real_stop_result.scalar_one_or_none():
        return

    expected_days = (end_day - start_day).days + 1
    expected_rows = expected_days * 3
    test_perf_count = await db.scalar(
        select(func.count())
        .select_from(Performance)
        .where(
            and_(
                Performance.production_date >= start_day,
                Performance.production_date <= end_day,
                Performance.remark == "efficiency-test-data",
            )
        )
    )
    test_stop_count = await db.scalar(
        select(func.count())
        .select_from(StopRecord)
        .where(
            and_(
                StopRecord.start_time <= end_dt,
                func.coalesce(StopRecord.end_time, StopRecord.start_time) >= start_dt,
                StopRecord.reason == "效率统计测试数据",
            )
        )
    )
    if test_perf_count == expected_rows and test_stop_count == expected_rows:
        return

    await generate_efficiency_test_data(db, start_day.isoformat(), end_day.isoformat(), None)
