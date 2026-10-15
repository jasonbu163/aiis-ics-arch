"""
文件路径: /backend/app/hr/manifest.py
功能描述: HR 模块注册元数据
主要功能:
    - 声明 HR 基础与子业务路由入口
    - 声明 HR 模块模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=(),
    error_codes=(),
    name="hr",
    enabled=False,
    order=50,
    routers=(
        "app.hr.api.routes:router",
        "app.hr.api.routes:department_router",
        "app.hr.api.routes:employee_router",
        "app.hr.api.routes:attendance_router",
        "app.hr.api.routes:recruitment_router",
    ),
    models_package="app.hr.models",
    permissions=("hr",),
)
