"""
文件路径: /backend/app/reports/manifest.py
功能描述: 报表模块注册元数据
主要功能:
    - 声明当前已暴露的报表模块路由入口
    - 声明报表模块模型包入口
    - 保持既有路由暴露面不变
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=('auxiliary', 'plan', 'performance'),
    exports=(),
    error_codes=(),
    name="reports",
    enabled=True,
    order=80,
    routers=(
        "app.reports.api.routes:router",
        "app.reports.api.routes:assessment_router",
        "app.reports.api.routes:efficiency_router",
        "app.reports.api.routes:print_router",
        "app.reports.api.routes:target_router",
    ),
    models_package="app.reports.models",
    permissions=("reports",),
)
