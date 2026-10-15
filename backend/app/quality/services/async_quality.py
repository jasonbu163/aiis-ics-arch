"""
文件路径: /backend/app/quality/services/async_quality.py
功能描述: 质量模块异步业务服务
主要功能:
    - 编排质量检验与缺陷记录业务流程
    - 查询并计算 SPC 数据与统计指标
"""
import datetime
import math
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.quality.crud.async_quality import quality_crud
from app.quality.models.quality import QualityDefectRecord, QualityInspection, QualitySPCMeasurement
from app.quality.schemas.quality_in import DefectRecordCreate, QualityInspectionCreate, QualityInspectionUpdate
from common.data_keys import normalize_defect_level, normalize_quality_grade
from common.error_codes import ErrorCode
from common.exceptions import BusinessException
from settings import settings


QUALITY_JUDGMENT_LABEL_ALIASES = {
    "合格": "qualified",
    "不合格": "unqualified",
    "让步接收": "concession",
    "待复检": "recheck",
}

SPC_ITEM_SPECS = {
    "thickness": {"mean": Decimal("2.5000"), "usl": Decimal("2.5500"), "lsl": Decimal("2.4500"), "step": Decimal("0.0060")},
    "width": {"mean": Decimal("1250.0000"), "usl": Decimal("1255.0000"), "lsl": Decimal("1245.0000"), "step": Decimal("0.7000")},
    "tensile": {"mean": Decimal("520.0000"), "usl": Decimal("560.0000"), "lsl": Decimal("480.0000"), "step": Decimal("5.2000")},
    "yield": {"mean": Decimal("360.0000"), "usl": Decimal("395.0000"), "lsl": Decimal("325.0000"), "step": Decimal("4.5000")},
    "hardness": {"mean": Decimal("180.0000"), "usl": Decimal("210.0000"), "lsl": Decimal("150.0000"), "step": Decimal("3.0000")},
    "elongation": {"mean": Decimal("28.0000"), "usl": Decimal("35.0000"), "lsl": Decimal("21.0000"), "step": Decimal("0.9000")},
}


def normalize_quality_judgment(value: str | None) -> str | None:
    if value is None:
        return None
    return QUALITY_JUDGMENT_LABEL_ALIASES.get(value, value)


class QualityService:
    """质量业务编排层。"""

    async def list_inspections(
        self,
        db: AsyncSession,
        page: int,
        page_size: int,
        coil_no: str | None = None,
        grade: str | None = None,
        quality_grade: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        if settings.BACKEND_MOCK_ENABLED:
            await self._ensure_seed_inspections(db)
        items, total = await quality_crud.list_inspections(
            db, page, page_size, coil_no, grade, quality_grade, start_date, end_date
        )
        for item in items:
            item.quality_grade = normalize_quality_grade(item.quality_grade)
            item.judgment = normalize_quality_judgment(item.judgment)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def create_inspection(
        self, db: AsyncSession, quality_data: QualityInspectionCreate, inspector: str
    ) -> QualityInspection:
        quality = QualityInspection(
            coil_no=quality_data.coil_no,
            grade=quality_data.grade,
            spec=quality_data.spec,
            weight=quality_data.weight,
            start_time=quality_data.start_time,
            end_time=quality_data.end_time,
            operator=quality_data.operator,
            shift=quality_data.shift,
            quality_items=quality_data.quality_items,
            judgment=normalize_quality_judgment(quality_data.judgment),
            quality_grade=normalize_quality_grade(quality_data.quality_grade),
            comment=quality_data.comment,
            inspector=quality_data.inspector or inspector,
            inspect_time=quality_data.inspect_time or datetime.datetime.now(),
            coil_images=quality_data.coil_images,
        )

        await quality_crud.create_inspection(db, quality)

        if quality_data.defects:
            for defect_data in quality_data.defects:
                db.add(self._build_defect(quality.id, defect_data))

        await db.commit()

        created = await quality_crud.get_inspection_with_defects(db, quality.id)
        if not created:
            raise BusinessException(ErrorCode.QUALITY_INSPECTION_NOT_FOUND)
        return created

    async def get_inspection(self, db: AsyncSession, quality_id: int) -> QualityInspection:
        quality = await quality_crud.get_inspection_with_defects(db, quality_id)
        if not quality:
            raise BusinessException(ErrorCode.QUALITY_INSPECTION_NOT_FOUND)
        return quality

    async def update_inspection(
        self, db: AsyncSession, quality_id: int, quality_data: QualityInspectionUpdate
    ) -> QualityInspection:
        quality = await quality_crud.get_inspection(db, quality_id)
        if not quality:
            raise BusinessException(ErrorCode.QUALITY_INSPECTION_NOT_FOUND)

        update_data = quality_data.model_dump(exclude_unset=True, exclude={"defects"})
        if "quality_grade" in update_data:
            update_data["quality_grade"] = normalize_quality_grade(update_data["quality_grade"])
        if "judgment" in update_data:
            update_data["judgment"] = normalize_quality_judgment(update_data["judgment"])
        for key, value in update_data.items():
            setattr(quality, key, value)

        if quality_data.defects is not None:
            old_defects = await quality_crud.list_defects_by_inspection(db, quality_id)
            for defect in old_defects:
                await quality_crud.delete_defect(db, defect)
            for defect_data in quality_data.defects:
                db.add(self._build_defect(quality_id, defect_data))

        await db.commit()

        updated = await quality_crud.get_inspection_with_defects(db, quality_id)
        if not updated:
            raise BusinessException(ErrorCode.QUALITY_INSPECTION_NOT_FOUND)
        return updated

    async def delete_inspection(self, db: AsyncSession, quality_id: int) -> None:
        quality = await quality_crud.get_inspection(db, quality_id)
        if not quality:
            raise BusinessException(ErrorCode.QUALITY_INSPECTION_NOT_FOUND)
        await quality_crud.delete_inspection(db, quality)
        await db.commit()

    async def list_defects(self, db: AsyncSession, page: int, page_size: int) -> dict[str, Any]:
        items, total = await quality_crud.list_defects(db, page, page_size)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def add_defect(self, db: AsyncSession, quality_id: int, defect_data: DefectRecordCreate) -> QualityDefectRecord:
        quality = await quality_crud.get_inspection(db, quality_id)
        if not quality:
            raise BusinessException(ErrorCode.QUALITY_INSPECTION_NOT_FOUND)

        defect = await quality_crud.create_defect(db, self._build_defect(quality_id, defect_data))
        await db.commit()
        return defect

    async def delete_defect(self, db: AsyncSession, quality_id: int, defect_id: int) -> None:
        defect = await quality_crud.get_defect(db, quality_id, defect_id)
        if not defect:
            raise BusinessException(ErrorCode.QUALITY_DEFECT_NOT_FOUND)
        await quality_crud.delete_defect(db, defect)
        await db.commit()

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

    def _build_defect(self, quality_id: int, defect_data: DefectRecordCreate) -> QualityDefectRecord:
        return QualityDefectRecord(
            inspection_id=quality_id,
            position=defect_data.position,
            defect_type=defect_data.defect_type,
            level=normalize_defect_level(defect_data.level),
            length=defect_data.length,
            description=defect_data.description,
            image_url=defect_data.image_url,
        )

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

    async def _ensure_seed_inspections(self, db: AsyncSession) -> None:
        total = await db.scalar(select(func.count()).select_from(QualityInspection))
        if total:
            return

        base_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        samples = [
            ("QL202605001", "SPHC", "2.0*1250*C", "22.3000", "excellent", "qualified", "张工", "dayShift"),
            ("QL202605002", "DX51D", "1.5*1250*C", "15.8000", "firstClass", "qualified", "李工", "middleShift"),
            ("QL202605003", "TC11", "3.0*1215*C", "19.5000", "qualified", "qualified", "王工", "nightShift"),
            ("QL202605004", "SPCC", "2.5*1000*C", "20.1000", "pending", "recheck", "赵工", "dayShift"),
            ("QL202605005", "TA2", "3.77*1215*C", "23.8000", "firstClass", "concession", "陈工", "middleShift"),
            ("QL202605006", "HG12233", "1.2*1000*C", "7.0000", "unqualified", "unqualified", "刘工", "nightShift"),
            ("QL202605007", "SPHC", "3.0*1250*C", "25.5000", "excellent", "qualified", "周工", "dayShift"),
            ("QL202605008", "DC01", "1.8*1200*C", "18.7000", "qualified", "qualified", "吴工", "middleShift"),
            ("QL202605009", "SPCC", "2.5*1250*C", "20.5000", "firstClass", "qualified", "孙工", "nightShift"),
            ("QL202605010", "DX51D", "1.2*1000*C", "12.4000", "pending", "recheck", "郑工", "dayShift"),
            ("QL202605011", "SPHC", "2.0*1000*C", "21.2000", "qualified", "qualified", "钱工", "middleShift"),
            ("QL202605012", "TA1", "1.0*1000*C", "9.3000", "excellent", "qualified", "冯工", "nightShift"),
        ]

        for index, (coil_no, grade, spec, weight, quality_grade, judgment, inspector, shift) in enumerate(samples):
            inspect_time = base_time - datetime.timedelta(hours=index * 5)
            start_time = inspect_time - datetime.timedelta(hours=7)
            inspection = QualityInspection(
                coil_no=coil_no,
                grade=grade,
                spec=spec,
                weight=Decimal(weight),
                start_time=start_time,
                end_time=start_time + datetime.timedelta(hours=6, minutes=25),
                operator=f"operator-{index % 4 + 1}",
                shift=shift,
                quality_items=[
                    {
                        "item": "surfaceQuality",
                        "standard": "noVisibleDefect",
                        "actualValue": "normal" if judgment != "unqualified" else "scratch",
                        "result": "qualified" if judgment != "unqualified" else "unqualified",
                    },
                    {
                        "item": "thicknessDeviation",
                        "standard": "withinTolerance",
                        "actualValue": f"{0.01 * ((index % 5) - 2):+.2f}mm",
                        "result": "qualified",
                    },
                ],
                judgment=judgment,
                quality_grade=normalize_quality_grade(quality_grade),
                comment="quality-test-data",
                inspector=inspector,
                inspect_time=inspect_time,
                coil_images=[],
            )
            db.add(inspection)
            await db.flush()

            if judgment in {"unqualified", "recheck", "concession"}:
                db.add(QualityDefectRecord(
                    inspection_id=inspection.id,
                    position="outer",
                    defect_type="scratch" if judgment == "unqualified" else "wave",
                    level="severe" if judgment == "unqualified" else "normal",
                    length=Decimal("120.00") if judgment == "unqualified" else Decimal("40.00"),
                    description="quality-test-data",
                ))

        await db.commit()

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
