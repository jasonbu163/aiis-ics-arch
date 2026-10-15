"""
文件路径: /backend/app/project/services/__init__.py
功能描述: 项目模块 Service 导出
主要功能:
    - 导出异步项目业务服务
"""
from app.project.services.async_project import project_service

__all__ = ["project_service"]
