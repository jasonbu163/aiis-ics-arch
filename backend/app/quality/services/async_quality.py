"""
文件路径: /backend/app/quality/services/async_quality.py
功能描述: 质量模块异步业务服务
主要功能:
    - 查询并计算 SPC 数据与统计指标
"""
import datetime
import math
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.quality.crud.async_quality import quality_crud
from app.quality.models.quality import QualitySPCMeasurement
from settings import settings


SPC_ITEM_SPECS = {
    "thickness": {"mean": Decimal("2.5000"), "usl": Decimal("2.5500"), "lsl": Decimal("2.4500"), "step": Decimal("0.0060")},
    "width": {"mean": Decimal("1250.0000"), "usl": Decimal("1255.0000"), "lsl": Decimal("1245.0000"), "step": Decimal("0.7000")},
    "tensile": {"mean": Decimal("520.0000"), "usl": Decimal("560.0000"), "lsl": Decimal("480.0000"), "step": Decimal("5.2000")},
    "yield": {"mean": Decimal("360.0000"), "usl": Decimal("395.0000"), "lsl": Decimal("325.0000"), "step": Decimal("4.5000")},
    "hardness": {"mean": Decimal("180.0000"), "usl": Decimal("210.0000"), "lsl": Decimal("150.0000"), "step": Decimal("3.0000")},
    "elongation": {"mean": Decimal("28.0000"), "usl": Decimal("35.0000"), "lsl": Decimal("21.0000"), "step": Decimal("0.9000")},
}


class QualityService:
    """质量业务编排层。"""

    async def get_spc_data(
        self,
        db: AsyncSession,
        item: str,
        grade: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        if settings.BACKEND_MOCK_ENABLED:
            await self._ensure_seed_spc_measurements(db)
        measurements = await quality_crud.list_spc_measurements(db, item, grade, start_date, end_date)
        return [self._spc_measurement_to_dict(measurement) for measurement in measurements]

    async def get_spc_stats(
        self,
        db: AsyncSession,
        item: str,
        grade: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        subgroup_size: int = 5,
    ) -> dict[str, Decimal]:
        if settings.BACKEND_MOCK_ENABLED:
            await self._ensure_seed_spc_measurements(db)
        measurements = await quality_crud.list_spc_measurements(db, item, grade, start_date, end_date)
        return self._calculate_spc_stats(item, measurements, subgroup_size)

    def _spc_measurement_to_dict(self, measurement: QualitySPCMeasurement) -> dict[str, Any]:
        return {
            "id": measurement.id,
            "coil_no": measurement.coil_no,
            "grade": measurement.grade,
            "item": measurement.item,
            "value": measurement.value,
            "time": measurement.measured_at,
            "operator": measurement.operator,
            "is_normal": measurement.is_normal,
        }

    def _calculate_spc_stats(
        self, item: str, measurements: list[QualitySPCMeasurement], subgroup_size: int
    ) -> dict[str, Decimal]:
        spec = SPC_ITEM_SPECS.get(item, SPC_ITEM_SPECS["thickness"])
        usl = spec["usl"]
        lsl = spec["lsl"]

        if not measurements:
            return {
                "cp": Decimal("0"),
                "cpk": Decimal("0"),
                "sigma": Decimal("0"),
                "defect_rate": Decimal("0"),
                "mean": spec["mean"],
                "ucl": spec["mean"],
                "lcl": spec["mean"],
                "usl": usl,
                "lsl": lsl,
            }

        values = [float(measurement.value) for measurement in measurements]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        calc_sigma = math.sqrt(variance)

        cp = (float(usl) - float(lsl)) / (6 * calc_sigma) if calc_sigma > 0 else 0
        cpu = (float(usl) - mean) / (3 * calc_sigma) if calc_sigma > 0 else 0
        cpl = (mean - float(lsl)) / (3 * calc_sigma) if calc_sigma > 0 else 0
        cpk = min(cpu, cpl)

        abnormal_count = sum(1 for measurement in measurements if not measurement.is_normal)
        defect_rate = (abnormal_count / len(measurements)) * 100 if measurements else 0

        a2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577}
        subgroup_count = len(values) // subgroup_size
        subgroup_means = []
        subgroup_ranges = []

        for i in range(subgroup_count):
            subgroup = values[i * subgroup_size:(i + 1) * subgroup_size]
            subgroup_means.append(sum(subgroup) / len(subgroup))
            subgroup_ranges.append(max(subgroup) - min(subgroup))

        overall_mean = sum(subgroup_means) / len(subgroup_means) if subgroup_means else mean
        mean_range = sum(subgroup_ranges) / len(subgroup_ranges) if subgroup_ranges else 0
        ucl = overall_mean + a2.get(subgroup_size, 0.577) * mean_range
        lcl = overall_mean - a2.get(subgroup_size, 0.577) * mean_range

        return {
            "cp": round(Decimal(str(cp)), 3),
            "cpk": round(Decimal(str(cpk)), 3),
            "sigma": round(Decimal(str(calc_sigma)), 4),
            "defect_rate": round(Decimal(str(defect_rate)), 3),
            "mean": round(Decimal(str(mean)), 4),
            "ucl": round(Decimal(str(ucl)), 4),
            "lcl": round(Decimal(str(lcl)), 4),
            "usl": usl,
            "lsl": lsl,
        }

    async def _ensure_seed_spc_measurements(self, db: AsyncSession) -> None:
        total = await db.scalar(select(func.count()).select_from(QualitySPCMeasurement))
        if total:
            return

        base_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        grades = ["TA1", "TA2", "TA3", "TC4"]
        operators = ["operator-1", "operator-2", "operator-3", "operator-4"]

        for item, spec in SPC_ITEM_SPECS.items():
            for index in range(96):
                wave = Decimal(str(math.sin(index / 5) * 1.8))
                drift = Decimal(index % 9 - 4) / Decimal("4")
                value = spec["mean"] + spec["step"] * (wave + drift)
                is_abnormal = index in {18, 47, 78}
                if is_abnormal:
                    value = spec["usl"] + spec["step"] * Decimal("2") if index != 47 else spec["lsl"] - spec["step"] * Decimal("2")

                db.add(QualitySPCMeasurement(
                    coil_no=f"SPC{item[:2].upper()}{index + 1:05d}",
                    grade=grades[index % len(grades)],
                    item=item,
                    value=value.quantize(Decimal("0.0001")),
                    operator=operators[index % len(operators)],
                    measured_at=base_time - datetime.timedelta(hours=(96 - index) * 2),
                    is_normal=not is_abnormal,
                ))

        await db.commit()


quality_service = QualityService()
