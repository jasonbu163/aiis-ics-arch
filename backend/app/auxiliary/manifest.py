"""公共能源价格切片的无副作用注册声明。"""
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=('app.auxiliary.models:StopRecord',),
    error_codes=('auxiliary.not_found', 'auxiliary.conflict'),
    name="auxiliary", enabled=True, order=60,
    routers=("app.auxiliary.api.routes:router",),
    models_package="app.auxiliary.models",
    permissions=("auxiliary",),
)
