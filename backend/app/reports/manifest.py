"""旧卷材报表及其旧模型退出运行时装配。"""
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name='reports', enabled=False, order=80, core_contract='aiis.backend-module/v1',
    requires=(), model_requires=('auxiliary','plan','performance'), exports=(), error_codes=(), routers=(),
    models_package=None, permissions=('reports',),
)
