"""
文件路径: /backend/app/quality/crud/__init__.py
功能描述: 质量模块 CRUD 导出
主要功能:
    - 导出质量检验与缺陷记录异步 CRUD 实例
"""
from app.quality.crud.async_quality import quality_crud

__all__ = ["quality_crud"]
