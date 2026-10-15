"""
文件路径: /backend/app/project/crud/__init__.py
功能描述: 项目模块 CRUD 导出
主要功能:
    - 导出项目、任务、里程碑异步 CRUD 实例
"""
from app.project.crud.async_project import async_crud_project, async_crud_project_milestone, async_crud_project_task

__all__ = ["async_crud_project", "async_crud_project_task", "async_crud_project_milestone"]
