"""
文件路径: /backend/app/schema_maintenance/manifest.py
功能描述: Schema maintenance 模块注册元数据
主要功能:
    - 声明补齐缺失表维护 API 路由
    - 保持 no-UI operational capability 与业务 maintenance 模块隔离
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    name="schema_maintenance",
    enabled=True,
    order=95,
    routers=("app.schema_maintenance.api.routes:router",),
    models_package=None,
    permissions=(),
)
