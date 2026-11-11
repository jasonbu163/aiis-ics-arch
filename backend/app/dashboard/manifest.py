"""旧生产首页退出路由；保留其独立统计模型及数据。"""
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name='dashboard', enabled=False, order=85, core_contract='aiis.backend-module/v1',
    requires=(), model_requires=('plan',), exports=(), error_codes=(), routers=(),
    models_package='app.dashboard.models', permissions=('dashboard',),
)
