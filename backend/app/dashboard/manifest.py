"""
文件路径: /backend/app/dashboard/manifest.py
功能描述: Dashboard 模块注册元数据
主要功能:
    - 声明 Dashboard 模块 API 路由入口
    - 声明 Dashboard 模块模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=('plan',),
    exports=(),
    error_codes=(),
    name="dashboard",
    enabled=True,
    order=85,
    routers=("app.dashboard.api.routes:router",),
    models_package="app.dashboard.models",
    permissions=("dashboard",),
)
