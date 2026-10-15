"""
文件路径: /backend/app/reports/crud/async_print.py
功能描述: 打印标签异步 CRUD
主要功能:
    - 查询可打印实绩列表和详情
    - 创建打印记录
"""
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.performance.models import Performance
from app.reports.models.reports import PrintRecord


class PrintCRUD:
    """打印标签数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_performances(self, page: int, page_size: int):
        result = await self.db.execute(
            select(Performance)
            .order_by(desc(Performance.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all()

    async def count_performances(self) -> int:
        result = await self.db.execute(select(func.count(Performance.id)))
        return result.scalar() or 0

    async def get_performance(self, performance_id: int):
        result = await self.db.execute(select(Performance).where(Performance.id == performance_id))
        return result.scalar_one_or_none()

    async def create_print_records(self, records: list[PrintRecord]) -> None:
        for record in records:
            self.db.add(record)
        await self.db.commit()
