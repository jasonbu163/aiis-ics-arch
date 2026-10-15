"""
文件路径: /backend/app/performance/services/async_split.py
功能描述: 分卷业务逻辑服务层
主要功能:
    - 分卷 CRUD 操作封装
    - 母卷查询
    - 分卷号自动生成
    - 创建分卷时自动生成子卷实绩
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from sqlalchemy.orm import selectinload
from app.performance.models.performance import Performance, Split
from app.performance.schemas.performance_in import SplitCreate, SplitUpdate


class SplitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        parent_coil_no: Optional[str] = None
    ) -> Dict[str, Any]:
        query = select(Split).options(
            selectinload(Split.performance)
        )
        
        conditions = []
        if parent_coil_no:
            conditions.append(Performance.coil_no.ilike(f"%{parent_coil_no}%"))
        
        if conditions:
            query = query.join(Performance).where(and_(*conditions))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Split.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        splits = result.scalars().all()
        
        return {
            "items": splits,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_by_id(self, split_id: int) -> Optional[Split]:
        query = select(Split).options(
            selectinload(Split.performance)
        ).where(Split.id == split_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: SplitCreate) -> Split:
        perf_result = await self.db.execute(
            select(Performance).where(Performance.id == data.performance_id)
        )
        parent_perf = perf_result.scalar_one_or_none()
        
        if not parent_perf:
            raise ValueError("母卷实绩不存在")
        if parent_perf.plan_id is None or parent_perf.weight is None:
            raise ValueError("无计划 PLC 观察实绩不可分卷")
        
        split = Split(**data.model_dump())
        self.db.add(split)
        
        parent_perf.is_split = True
        self.db.add(parent_perf)
        
        child_perf = Performance(
            plan_id=parent_perf.plan_id,
            coil_no=data.split_no,
            parent_coil_no=parent_perf.coil_no,
            grade=parent_perf.grade,
            spec=data.spec,
            weight=data.weight,
            total_length=parent_perf.total_length,
            diameter=parent_perf.diameter,
            density=parent_perf.density,
            production_date=parent_perf.production_date,
            is_split=False,
            remark=f"来源于母卷分卷: {parent_perf.coil_no}"
        )
        self.db.add(child_perf)
        
        await self.db.commit()
        await self.db.refresh(split)
        await self.db.refresh(parent_perf)
        
        return split

    async def update(
        self,
        split_id: int,
        data: SplitUpdate
    ) -> Optional[Split]:
        split = await self.get_by_id(split_id)
        if not split:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(split, field, value)
        
        await self.db.commit()
        await self.db.refresh(split)
        return split

    async def delete(self, split_id: int) -> bool:
        split = await self.get_by_id(split_id)
        if not split:
            return False
        
        await self.db.delete(split)
        await self.db.commit()
        return True

    async def get_parent_coils(self) -> List[Dict[str, Any]]:
        query = select(Performance).where(
            Performance.parent_coil_no == Performance.coil_no,
            Performance.plan_id.is_not(None),
            Performance.weight.is_not(None),
        ).order_by(Performance.created_at.desc())
        
        result = await self.db.execute(query)
        performances = result.scalars().all()
        
        parent_coils = []
        for perf in performances:
            parent_coils.append({
                "id": perf.id,
                "coil_no": perf.coil_no,
                "grade": perf.grade,
                "spec": perf.spec or '-',
                "weight": float(perf.weight),
                "remaining_weight": float(perf.weight)
            })
        
        return parent_coils

    async def generate_split_no(self, performance_id: int) -> str:
        query = select(Performance).where(Performance.id == performance_id)
        result = await self.db.execute(query)
        performance = result.scalar_one_or_none()
        
        if not performance:
            raise ValueError("实绩不存在")
        
        coil_no = performance.coil_no
        
        count_query = select(func.count()).where(
            Split.performance_id == performance_id
        )
        count_result = await self.db.execute(count_query)
        count = count_result.scalar()
        
        split_index = count + 1
        if split_index <= 2:
            split_no = f"{coil_no}-{split_index}"
        else:
            letter = chr(64 + split_index - 2)
            split_no = f"{coil_no}-{letter}"
        
        return split_no
