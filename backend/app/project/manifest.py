"""
文件路径: /backend/app/project/manifest.py
功能描述: 项目模块注册元数据
主要功能:
    - 声明项目模块 API 路由入口
    - 声明项目模块模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=(),
    error_codes=(),
    name="project",
    enabled=True,
    order=110,
    routers=("app.project.api.routes:router",),
    models_package="app.project.models",
    permissions=("project",),
)
