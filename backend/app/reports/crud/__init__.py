"""
文件路径: /backend/app/reports/crud/__init__.py
功能描述: 报表 CRUD 导出
主要功能:
    - 导出效率统计 CRUD
"""
from app.reports.crud.async_efficiency import EfficiencyCRUD
from app.reports.crud.async_assessment import AssessmentCRUD
from app.reports.crud.async_print import PrintCRUD
from app.reports.crud.async_quality import ReportsQualityCRUD
from app.reports.crud.async_reports import ReportsCRUD
from app.reports.crud.async_target import TargetCRUD

__all__ = ["EfficiencyCRUD", "ReportsCRUD", "AssessmentCRUD", "PrintCRUD", "TargetCRUD", "ReportsQualityCRUD"]
