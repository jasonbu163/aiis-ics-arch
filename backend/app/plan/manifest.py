"""
文件路径: /backend/app/plan/manifest.py
功能描述: Plan 模块注册元数据
主要功能:
    - 声明计划管理 API 路由入口
    - 声明计划管理模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=('performance',),
    exports=('app.plan.models:Plan',),
    error_codes=(),
    name="plan",
    enabled=True,
    order=30,
    routers=("app.plan.api.routes:router",),
    models_package="app.plan.models",
    permissions=("plan",),
)
