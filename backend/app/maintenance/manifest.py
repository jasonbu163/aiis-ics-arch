"""
文件路径: /backend/app/maintenance/manifest.py
功能描述: 维保模块注册元数据
主要功能:
    - 声明维保基础与记录路由入口
    - 声明维保模块模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=(),
    error_codes=(),
    name="maintenance",
    enabled=True,
    order=60,
    routers=(
        "app.maintenance.api.routes:router",
        "app.maintenance.api.routes:maintenance_router",
        "app.maintenance.api.routes:maintenance_log_router",
    ),
    models_package="app.maintenance.models",
    permissions=("maintenance",),
)
