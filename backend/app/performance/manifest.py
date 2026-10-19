"""
文件路径: /backend/app/performance/manifest.py
功能描述: 实绩模块注册元数据
主要功能:
    - 声明实绩管理 API 路由入口
    - 声明分卷管理 API 路由入口
    - 声明实绩模块模型包入口
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=('plan',),
    exports=('app.performance.models:Performance',),
    error_codes=('performance.mapping_unauthenticated', 'performance.mapping_forbidden', 'performance.mapping_invalid_sample', 'performance.mapping_sample_id_conflict', 'performance.mapping_value_conflict', 'performance.mapping_sample_time_conflict', 'performance.mapping_observation_time_conflict', 'performance.mapping_parent_not_found', 'performance.mapping_parent_mismatch', 'performance.mapping_delete_forbidden', 'performance.mapping_unavailable', 'performance.mapping_internal_error'),
    name="performance",
    enabled=True,
    order=30,
    routers=(
        "app.performance.api.mapping_observations:router",
        "app.performance.api.process_samples:router",
        "app.performance.api.routes:router",
        "app.performance.api.lineage_routes:transform_router",
        "app.performance.api.lineage_routes:performance_lineage_router",
        "app.performance.api.split_routes:router",
    ),
    models_package="app.performance.models",
    permissions=("performance", "performance-mapping-read", "performance-mapping-ingest"),
)
