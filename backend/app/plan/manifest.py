"""通用计划模块注册与公开的计划同步接口。"""
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name='plan', enabled=True, order=30, core_contract='aiis.backend-module/v1',
    requires=('task',), model_requires=('performance',),
    exports=('app.plan.models:Plan', 'app.plan.services.async_workflow:lock_plan',
             'app.plan.services.async_workflow:upsert_plan', 'app.plan.services.async_workflow:plan_wire',
             'app.plan.services.async_workflow:sync_plan'),
    error_codes=(), routers=('app.plan.api.routes:router',),
    models_package='app.plan.models', permissions=('plan',),
)
