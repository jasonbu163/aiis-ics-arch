"""
文件路径: /backend/app/system/models/__init__.py
功能描述: 系统模块数据库模型导出
主要功能:
    - 导出系统字典和字典项模型
    - 导出 Projection 映射控制面模型
"""
from app.system.models.system_dict import SysDict, SysDictItem
from app.system.models.projection_mapping import (
    ProjectionMappingAuditEvent,
    ProjectionMappingBinding,
    ProjectionMappingRevision,
    ProjectionMappingSet,
    ProjectionRuntimeAuditEvent,
    ProjectionRuntimeCursor,
)

__all__ = [
    "SysDict",
    "SysDictItem",
    "ProjectionMappingAuditEvent",
    "ProjectionMappingBinding",
    "ProjectionMappingRevision",
    "ProjectionMappingSet",
    "ProjectionRuntimeAuditEvent",
    "ProjectionRuntimeCursor",
]
