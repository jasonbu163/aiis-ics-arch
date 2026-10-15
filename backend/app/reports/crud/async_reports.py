"""
文件路径: /backend/app/reports/crud/async_reports.py
功能描述: 报表主路由异步 CRUD
主要功能:
    - 查询生产报表列表和详情
    - 查询报表生成和趋势所需实绩数据
    - 创建生产报表记录
"""
import datetime

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.performance.models import Performance
from app.reports.models.reports import ProductionReport


class ReportsCRUD:
    """生产报表数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def build_report_query(self, report_type: str | None, start_date: str | None, end_date: str | None):
        query = select(ProductionReport).order_by(desc(ProductionReport.report_date))

        if report_type:
            query = query.where(ProductionReport.report_type == report_type)
        if start_date:
            query = query.where(ProductionReport.report_date >= datetime.datetime.fromisoformat(start_date).date())
        if end_date:
            query = query.where(ProductionReport.report_date <= datetime.datetime.fromisoformat(end_date).date())

        return query

    async def list_reports(
        self,
        page: int,
        page_size: int,
        report_type: str | None,
        start_date: str | None,
        end_date: str | None,
    ):
        query = self.build_report_query(report_type, start_date, end_date)
        result = await self.db.execute(query.offset((page - 1) * page_size).limit(page_size))
        return result.scalars().all()

    async def count_all_reports(self) -> int:
        result = await self.db.execute(select(func.count(ProductionReport.id)))
        return result.scalar() or 0

    async def list_reports_for_export(self, report_type: str | None, start_date: str | None, end_date: str | None):
        query = self.build_report_query(report_type, start_date, end_date)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_performances_between(self, start_datetime: datetime.datetime, end_datetime: datetime.datetime):
        result = await self.db.execute(
            select(Performance).where(
                and_(
                    Performance.production_date >= start_datetime,
                    Performance.production_date <= end_datetime,
                )
            )
        )
        return result.scalars().all()

    async def create_report(self, report: ProductionReport) -> ProductionReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report(self, report_id: int):
        result = await self.db.execute(select(ProductionReport).where(ProductionReport.id == report_id))
        return result.scalar_one_or_none()
