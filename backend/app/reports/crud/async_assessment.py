"""
文件路径: /backend/app/reports/crud/async_assessment.py
功能描述: 评估管理异步 CRUD
主要功能:
    - 查询评估列表和统计数据
    - 查询单个评估记录
    - 创建和更新评估记录
"""
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.models.reports import Assessment


class AssessmentCRUD:
    """评估管理数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def build_list_query(self, employee_name: str | None, assessment_type: str | None):
        query = select(Assessment).order_by(desc(Assessment.assessment_date))
        if employee_name:
            query = query.where(Assessment.employee_name.like(f"%{employee_name}%"))
        if assessment_type:
            query = query.where(Assessment.assessment_type == assessment_type)
        return query

    async def list_assessments(self, page: int, page_size: int, employee_name: str | None, assessment_type: str | None):
        query = self.build_list_query(employee_name, assessment_type)
        result = await self.db.execute(query.offset((page - 1) * page_size).limit(page_size))
        return result.scalars().all()

    async def count_all_assessments(self) -> int:
        result = await self.db.execute(select(func.count(Assessment.id)))
        return result.scalar() or 0

    async def get_assessment(self, assessment_id: int):
        result = await self.db.execute(select(Assessment).where(Assessment.id == assessment_id))
        return result.scalar_one_or_none()

    async def create_assessment(self, assessment: Assessment) -> Assessment:
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def save_assessment(self, assessment: Assessment) -> Assessment:
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def list_all_assessments(self):
        result = await self.db.execute(select(Assessment))
        return result.scalars().all()
