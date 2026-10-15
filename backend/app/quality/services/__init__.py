"""
文件路径: /backend/app/quality/services/__init__.py
功能描述: 质量模块 Service 导出
主要功能:
    - 导出质量业务服务实例
"""
from app.quality.services.async_quality import quality_service

__all__ = ["quality_service"]
