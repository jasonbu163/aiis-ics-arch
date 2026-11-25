"""
文件路径: /backend/app/quality/manifest.py
功能描述: 质量模块注册元数据
主要功能:
    - 声明任务质量结果和 SPC 路由入口
    - 声明质量模块模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=(),
    error_codes=(
        "quality.unauthenticated", "quality.forbidden", "quality.not_found", "quality.target_conflict",
        "quality.config_revision_conflict", "quality.invalid_request", "quality.unavailable",
        "quality.commit_unknown", "quality.task_no_conflict",
    ),
    name="quality",
    enabled=True,
    order=100,
    routers=(
        "app.quality.api.results:router",
        "app.quality.api.routes:router",
    ),
    models_package="app.quality.models",
    permissions=("quality",),
)
