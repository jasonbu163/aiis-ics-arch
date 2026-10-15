"""
文件路径: /backend/app/dashboard/services/__init__.py
功能描述: Dashboard Service 导出
主要功能:
    - 导出看板异步业务服务
"""
from app.dashboard.services.async_dashboard import DashboardService, dashboard_service

__all__ = ["DashboardService", "dashboard_service"]
