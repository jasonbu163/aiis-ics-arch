"""
文件路径: /backend/app/system/manifest.py
功能描述: System 模块注册元数据
主要功能:
    - 声明系统字典 API 路由入口
    - 声明 Projection mapping 控制面 API 路由入口
    - 声明系统字典模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    name="system",
    enabled=True,
    order=25,
    routers=(
        "app.system.api.routes:router",
        "app.system.api.routes:dict_item_router",
        "app.system.api.projection_mapping:router",
    ),
    models_package="app.system.models",
    permissions=("system-dict", "projection-mapping", "projection-mapping-manage"),
)
