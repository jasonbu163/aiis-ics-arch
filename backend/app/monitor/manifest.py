"""
文件路径: /backend/app/monitor/manifest.py
功能描述: Monitor 模块注册元数据
主要功能:
    - 声明监控数据 API 路由入口
    - 声明监控数据模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=('app.monitor.models:PlcDbBlockRawSnapshot',),
    error_codes=('monitor.mapping_unauthenticated', 'monitor.mapping_forbidden', 'monitor.mapping_invalid_sample', 'monitor.mapping_sample_id_conflict', 'monitor.mapping_value_conflict', 'monitor.mapping_sample_time_conflict', 'monitor.mapping_observation_time_conflict', 'monitor.mapping_parent_not_found', 'monitor.mapping_parent_mismatch', 'monitor.mapping_delete_forbidden', 'monitor.mapping_unavailable', 'monitor.mapping_internal_error'),
    name="monitor",
    enabled=True,
    order=35,
    routers=("app.monitor.api.routes:router", "app.monitor.api.process_curve_samples:router"),
    models_package="app.monitor.models",
    permissions=("monitor", "monitor-business-read", "monitor-curve-read", "monitor-curve-ingest"),
)
