"""
文件路径: /backend/app/reports/services/async_target.py
功能描述: 目标设定异步服务
主要功能:
    - 编排目标列表、创建、更新和删除
    - 计算目标达成率
"""
import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from common.data_keys import (
    ProductionTargetType,
    normalize_period_type,
    normalize_target_type,
)
from app.reports.crud.async_target import TargetCRUD
from app.reports.models.reports import PerformanceTarget


def serialize_target(target: PerformanceTarget) -> dict:
    return {
        "id": target.id,
        "targetType": normalize_target_type(target.target_type),
        "targetValue": float(target.target_value) if target.target_value else 0,
        "periodType": normalize_period_type(target.period_type),
        "periodStart": target.period_start.isoformat() if target.period_start else None,
        "periodEnd": target.period_end.isoformat() if target.period_end else None,
        "department": target.department,
        "createdBy": target.created_by,
        "createdAt": target.created_at.isoformat() if target.created_at else None,
    }


class TargetService:
    """目标设定业务编排层。"""

    @staticmethod
    def crud(db: AsyncSession) -> TargetCRUD:
        return TargetCRUD(db)

    async def list_targets(
        self,
        db: AsyncSession,
        page: int,
        page_size: int,
        target_type: Optional[str],
        period_type: Optional[str],
    ) -> dict:
        crud = self.crud(db)
        targets = await crud.list_targets(page, page_size, target_type, period_type)
        total = await crud.count_all_targets()
        return {
            "items": [serialize_target(target) for target in targets],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def create_target(
        self,
        db: AsyncSession,
        target_type: str,
        target_value: float,
        period_type: str,
        period_start: str,
        period_end: str,
        department: Optional[str],
        created_by: int,
    ) -> dict:
        target = PerformanceTarget(
            target_type=normalize_target_type(target_type) or target_type,
            target_value=Decimal(str(target_value)),
            period_type=normalize_period_type(period_type) or period_type,
            period_start=datetime.date.fromisoformat(period_start),
            period_end=datetime.date.fromisoformat(period_end),
            department=department,
            created_by=created_by,
        )
        target = await self.crud(db).create_target(target)
        return serialize_target(target)

    async def update_target(
        self,
        db: AsyncSession,
        target_id: int,
        target_value: Optional[float],
        period_start: Optional[str],
        period_end: Optional[str],
        department: Optional[str],
    ) -> dict | None:
        target = await self.crud(db).get_target(target_id)
        if not target:
            return None

        if target_value is not None:
            target.target_value = Decimal(str(target_value))
        if period_start:
            target.period_start = datetime.date.fromisoformat(period_start)
        if period_end:
            target.period_end = datetime.date.fromisoformat(period_end)
        if department is not None:
            target.department = department

        target = await self.crud(db).save_target(target)
        return serialize_target(target)

    async def delete_target(self, db: AsyncSession, target_id: int) -> bool:
        target = await self.crud(db).get_target(target_id)
        if not target:
            return False
        await self.crud(db).delete_target(target)
        return True

    async def get_target_achievement(self, db: AsyncSession, target_id: int) -> dict | None:
        target = await self.crud(db).get_target(target_id)
        if not target:
            return None

        performances = await self.crud(db).list_performances_between(target.period_start, target.period_end)
        target_type = normalize_target_type(target.target_type)

        if target_type == ProductionTargetType.OUTPUT.value:
            actual_value = sum(float(p.output_quantity or 0) for p in performances)
        elif target_type == ProductionTargetType.QUALITY.value:
            qualified = sum(float(p.qualified_quantity or 0) for p in performances)
            total = sum(float(p.output_quantity or 0) for p in performances)
            actual_value = (qualified / total * 100) if total > 0 else 0
        elif target_type == ProductionTargetType.EFFICIENCY.value:
            efficiencies = [float(p.efficiency_rate or 0) for p in performances if p.efficiency_rate]
            actual_value = sum(efficiencies) / len(efficiencies) if efficiencies else 0
        else:
            actual_value = 0

        achievement_rate = (actual_value / float(target.target_value) * 100) if target.target_value else 0
        return {
            "targetValue": float(target.target_value),
            "actualValue": round(actual_value, 2),
            "achievementRate": round(achievement_rate, 1),
            "periodStart": target.period_start.isoformat(),
            "periodEnd": target.period_end.isoformat(),
        }


target_service = TargetService()
