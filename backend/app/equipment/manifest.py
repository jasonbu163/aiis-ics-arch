"""
文件路径: /backend/app/equipment/manifest.py
功能描述: 设备模块注册元数据
主要功能:
    - 声明设备管理 API 路由入口
    - 声明设备模块模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    core_contract="aiis.backend-module/v1",
    requires=(),
    model_requires=(),
    exports=(),
    error_codes=('equipment.mapping_unauthenticated', 'equipment.mapping_forbidden', 'equipment.mapping_invalid_sample', 'equipment.mapping_sample_id_conflict', 'equipment.mapping_value_conflict', 'equipment.mapping_sample_time_conflict', 'equipment.mapping_observation_time_conflict', 'equipment.mapping_parent_not_found', 'equipment.mapping_parent_mismatch', 'equipment.mapping_delete_forbidden', 'equipment.mapping_unavailable', 'equipment.mapping_internal_error', "equipment.temperature_unauthenticated", "equipment.temperature_forbidden",
                 "equipment.temperature_invalid_sample", "equipment.temperature_sample_id_conflict",
                 "equipment.temperature_sample_time_conflict", "equipment.temperature_unavailable",
                 "equipment.temperature_internal_error"),
    name="equipment",
    enabled=True,
    order=40,
    routers=("app.equipment.api.routes:router", "app.equipment.api.temperature_samples:router", "app.equipment.api.mapping_samples:router", "app.equipment.api.temperature_dashboard:router"),
    models_package="app.equipment.models",
    permissions=("equipment", "equipment-temperature-read", "equipment-temperature-ingest", "equipment-mapping-read", "equipment-mapping-ingest"),
)
