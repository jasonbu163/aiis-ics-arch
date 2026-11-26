"""
文件路径: /backend/app/energy/manifest.py
功能描述: 能耗模块注册元数据
主要功能:
    - 声明能耗模块 API 路由入口
    - 声明能耗模块模型包入口
    - 为后端模块自动注册试点提供 manifest
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=(),
    error_codes=(
        "energy.pricing_item_exists", "energy.pricing_item_missing", "energy.pricing_item_disabled",
        "energy.pricing_unit_in_use", "energy.pricing_item_invalid",
    ),
    name="energy",
    enabled=True,
    order=90,
    routers=("app.energy.api.routes:router",),
    models_package="app.energy.models",
    permissions=("energy-price-read", "energy-price-manage"),
)
