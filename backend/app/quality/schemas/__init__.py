"""
文件路径: /backend/app/quality/schemas/__init__.py
功能描述: 质量模块 Schema 导出
主要功能:
    - 导出 SPC 数据结构并保留既有查询类型
"""
from app.quality.schemas.quality_out import SPCDataPoint, SPCStats
from app.quality.schemas.quality_query import QualityQueryParams

__all__ = ["SPCDataPoint", "SPCStats", "QualityQueryParams"]
