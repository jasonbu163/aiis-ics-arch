"""
文件路径: /backend/app/plan/crud/async_crud.py
功能描述: 计划管理异步 CRUD 层（供 FastAPI 使用）
主要功能:
    - 异步数据库操作封装（纯手写，不依赖 sqlalchemy_crud_plus）
"""
from collections.abc import Sequence
from typing import Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.plan.domain import canonicalize_coil_no
from app.plan.models import Plan


class AsyncCRUDPlan:
    """计划管理异步 CRUD 层"""

    @staticmethod
    async def get_by_id(db: AsyncSession, plan_id: int) -> Plan | None:
        """根据 ID 获取计划"""
        result = await db.execute(
            select(Plan).where(Plan.id == plan_id)
        )
        return result.scalar_one_or_none()

    
    @staticmethod
    async def get_by_id_with_lock(db: AsyncSession, plan_id: int) -> Plan | None:
        """根据 ID 获取计划（带行锁）"""
        result = await db.execute(
            select(Plan).where(Plan.id == plan_id).with_for_update()
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_coil_no(db: AsyncSession, coil_no: str) -> Plan | None:
        """根据料卷号获取计划"""
        result = await db.execute(
            select(Plan).where(Plan.coil_no == coil_no)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_canonical_coil_no(
        db: AsyncSession,
        coil_no: object,
        *,
        with_lock: bool = False,
    ) -> Sequence[Plan]:
        """按 canonical 料卷号查找计划，保留原始显示值。"""
        canonical_coil_no = canonicalize_coil_no(coil_no)
        if canonical_coil_no is None:
            return []

        query = select(Plan).where(func.lower(func.trim(Plan.coil_no)) == canonical_coil_no)
        if with_lock:
            query = query.with_for_update()
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def exists_by_canonical_coil_no(db: AsyncSession, coil_no: object) -> bool:
        """检查 canonical 料卷号是否已存在。"""
        return bool(await AsyncCRUDPlan.list_by_canonical_coil_no(db, coil_no))

    @staticmethod
    async def get_by_status(db: AsyncSession, status: str) -> Sequence[Plan]:
        """根据状态获取计划列表"""
        result = await db.execute(
            select(Plan).where(Plan.status == status)
        )
        return result.scalars().all()

    @staticmethod
    async def exists_by_coil_no(db: AsyncSession, coil_no: str) -> bool:
        """检查料卷号是否已存在"""
        result = await db.execute(
            select(Plan).where(Plan.coil_no == coil_no)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def list_for_export(
        db: AsyncSession,
        *,
        plan_ids: list[int] | None = None,
        coil_no: str | None = None,
        grade: str | None = None,
        material_status: str | None = None,
        status: str | None = None,
    ) -> list[Plan]:
        """获取 XLSX 导出计划列表。"""
        query = select(Plan)
        if plan_ids:
            query = query.where(Plan.id.in_(plan_ids))
        if coil_no:
            query = query.where(Plan.coil_no.contains(coil_no))
        if grade:
            query = query.where(Plan.grade == grade)
        if material_status:
            query = query.where(Plan.material_status == material_status)
        if status:
            query = query.where(Plan.status == status)
        query = query.order_by(desc(Plan.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_list_with_filters(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        coil_no: str | None = None,
        grade: str | None = None,
        material_status: str | None = None,
        status: str | None = None
    ) -> dict[str, Any]:
        """
        获取计划列表（带筛选和分页）

        Returns:
            dict: 包含 items, total, page, page_size, total_pages
        """
        query = select(Plan)

        # 应用筛选条件
        if coil_no:
            query = query.where(Plan.coil_no.contains(coil_no))
        if grade:
            query = query.where(Plan.grade == grade)
        if material_status:
            query = query.where(Plan.material_status == material_status)
        if status:
            query = query.where(Plan.status == status)        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        offset = (page - 1) * page_size
        query = query.order_by(desc(Plan.created_at)).offset(offset).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    
    @staticmethod
    async def create(db: AsyncSession, plan_data) -> Plan:
        """创建计划"""
        # 将 Pydantic 模型转换为字典
        if hasattr(plan_data, 'model_dump'):
            data = plan_data.model_dump()
        elif hasattr(plan_data, 'dict'):
            data = plan_data.dict()
        else:
            data = plan_data
        
        plan = Plan(**data)
        db.add(plan)
        await db.flush()
        await db.refresh(plan)
        return plan

    
    @staticmethod
    async def update(db: AsyncSession, plan_id: int, plan_data) -> Plan | None:
        """更新计划"""
        # 获取现有计划
        plan = await AsyncCRUDPlan.get_by_id(db, plan_id)
        if not plan:
            return None
        
        # 将 Pydantic 模型转换为字典
        if hasattr(plan_data, 'model_dump'):
            data = plan_data.model_dump(exclude_unset=True)
        elif hasattr(plan_data, 'dict'):
            data = plan_data.dict(exclude_unset=True)
        else:
            data = plan_data
        
        # 更新字段
        for key, value in data.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        
        await db.flush()
        await db.refresh(plan)
        return plan

    
    @staticmethod
    async def delete(db: AsyncSession, plan_id: int) -> bool:
        """删除计划(软删除) 
        - 实际业务中可能需要改为状态更新而非物理删除，将计划状态plan.status改为 'deleted'
        """
        plan = await AsyncCRUDPlan.get_by_id(db, plan_id)
        if not plan:
            return False
        
        plan.status = 'deleted'
        await db.flush()
        await db.refresh(plan)
        return True


# 导出实例
async_crud_plan = AsyncCRUDPlan()
