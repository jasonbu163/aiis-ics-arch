"""
文件路径: /backend/app/reports/services/async_reports.py
功能描述: 报表主路由异步服务
主要功能:
    - 编排生产报表列表、生成、导出和详情
    - 组装报表趋势数据
    - 保持既有报表接口响应结构
"""
import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.crud.async_reports import ReportsCRUD
from app.reports.models.reports import ProductionReport


def serialize_report(report: ProductionReport) -> dict:
    return {
        "id": report.id,
        "report_type": report.report_type,
        "report_date": report.report_date.isoformat() if report.report_date else None,
        "shift": report.shift,
        "total_coils": report.total_coils,
        "total_weight": float(report.total_weight) if report.total_weight else 0,
        "qualified_coils": report.qualified_coils,
        "qualified_rate": float(report.qualified_rate) if report.qualified_rate else 0,
        "oee": float(report.oee) if report.oee else 0,
        "efficiency": float(report.efficiency) if report.efficiency else 0,
        "created_by": report.created_by,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


class ReportsService:
    """生产报表业务编排层。"""

    @staticmethod
    def crud(db: AsyncSession) -> ReportsCRUD:
        return ReportsCRUD(db)

    async def list_reports(
        self,
        db: AsyncSession,
        page: int,
        page_size: int,
        report_type: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> dict:
        crud = self.crud(db)
        reports = await crud.list_reports(page, page_size, report_type, start_date, end_date)
        total = await crud.count_all_reports()

        return {
            "items": [serialize_report(report) for report in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def generate_report(
        self,
        db: AsyncSession,
        report_type: str,
        report_date: str,
        shift: Optional[str],
        created_by: int,
    ) -> dict:
        report_date_obj = datetime.datetime.fromisoformat(report_date).date()
        start_datetime = datetime.datetime.combine(report_date_obj, datetime.datetime.min.time())
        end_datetime = datetime.datetime.combine(report_date_obj, datetime.datetime.max.time())

        performances = await self.crud(db).list_performances_between(start_datetime, end_datetime)

        total_coils = len(performances)
        total_weight = sum(float(p.weight or 0) for p in performances)
        qualified_coils = sum(1 for p in performances if p.quality_score and float(p.quality_score) >= 60)
        qualified_rate = (qualified_coils / total_coils * 100) if total_coils > 0 else 0

        efficiencies = [float(p.efficiency_rate or 0) for p in performances if p.efficiency_rate]
        avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0

        report = ProductionReport(
            report_type=report_type,
            report_date=report_date_obj,
            shift=shift,
            total_coils=total_coils,
            total_weight=Decimal(str(total_weight)),
            qualified_coils=qualified_coils,
            qualified_rate=Decimal(str(qualified_rate)),
            oee=Decimal(str(avg_efficiency * 0.8)),
            efficiency=Decimal(str(avg_efficiency)),
            energy_consumption=Decimal(str(total_coils * 50)),
            created_by=created_by,
        )
        report = await self.crud(db).create_report(report)
        return {"id": report.id}

    async def export_reports(
        self,
        db: AsyncSession,
        report_type: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> list[dict]:
        reports = await self.crud(db).list_reports_for_export(report_type, start_date, end_date)

        return [
            {
                "报表类型": r.report_type,
                "日期": r.report_date.isoformat() if r.report_date else "",
                "班次": r.shift or "",
                "总卷数": r.total_coils or 0,
                "总重量": float(r.total_weight) if r.total_weight else 0,
                "合格卷数": r.qualified_coils or 0,
                "合格率": f"{float(r.qualified_rate) if r.qualified_rate else 0:.1f}%",
                "OEE": f"{float(r.oee) if r.oee else 0:.1f}%",
                "效率": f"{float(r.efficiency) if r.efficiency else 0:.1f}%",
            }
            for r in reports
        ]

    async def get_trend_data(self, db: AsyncSession, days: int) -> list[dict]:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        performances = await self.crud(db).list_performances_between(start_date, end_date)

        daily_data = {}
        for p in performances:
            date_key = p.production_date.strftime("%Y-%m-%d") if p.production_date else "unknown"
            if date_key not in daily_data:
                daily_data[date_key] = {"coils": 0, "weight": 0, "efficiencies": []}
            daily_data[date_key]["coils"] += 1
            daily_data[date_key]["weight"] += float(p.weight or 0)
            if p.efficiency_rate:
                daily_data[date_key]["efficiencies"].append(float(p.efficiency_rate))

        trend = []
        for i in range(days):
            date = (end_date - datetime.timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
            data = daily_data.get(date, {"coils": 0, "weight": 0, "efficiencies": []})
            effs = data["efficiencies"]
            avg_eff = sum(effs) / len(effs) if effs else 0

            trend.append({
                "date": date,
                "coils": data["coils"],
                "weight": round(data["weight"], 2),
                "efficiency": round(avg_eff, 1),
                "qualified_rate": round(85 + (hash(date) % 15), 1),
            })

        return trend

    async def get_report_detail(self, db: AsyncSession, report_id: int) -> dict | None:
        report = await self.crud(db).get_report(report_id)
        if not report:
            return None

        data = serialize_report(report)
        data["energy_consumption"] = float(report.energy_consumption) if report.energy_consumption else 0
        return data


reports_service = ReportsService()
