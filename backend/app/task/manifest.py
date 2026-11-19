"""任务字段配置与共享合同的模块装配。"""
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name='task', enabled=True, order=25, core_contract='aiis.backend-module/v1',
    requires=(), model_requires=(), models_package='app.task.models', permissions=(),
    routers=('app.task.api.routes:router',),
    exports=('app.task.crud.async_records:require_row', 'app.task.crud.async_records:task_page',
             'app.task.crud.async_records:task_query',
             'app.task.domain:apply_changes', 'app.task.domain:base_wire', 'app.task.domain:business_now',
             'app.task.domain:invalid', 'app.task.domain:item_patch', 'app.task.domain:local_time',
             'app.task.domain:matching_target', 'app.task.domain:merge_values', 'app.task.domain:record_items',
             'app.task.domain:slot_key', 'app.task.domain:task_number', 'app.task.domain:wire_time',
             'app.task.errors:TaskError', 'app.task.errors:TaskErrorCode',
             'app.task.http:TaskRoute', 'app.task.http:actor', 'app.task.http:audit_event',
             'app.task.http:authorize', 'app.task.http:commit', 'app.task.http:response', 'app.task.http:retired',
             'app.task.schemas.fields:Envelope', 'app.task.schemas.fields:ErrorEnvelope', 'app.task.schemas.fields:TaskDateTime',
             'app.task.schemas.workflow:Outcome', 'app.task.schemas.workflow:Page', 'app.task.schemas.workflow:ProductionStatus',
             'app.task.schemas.workflow:QueryFilters', 'app.task.schemas.workflow:Record', 'app.task.schemas.workflow:Upsert',
             'app.task.services.async_fields:current_config', 'app.task.services.async_fields:record_use'),
    error_codes=('task.unauthenticated', 'task.forbidden', 'task.not_found', 'task.target_conflict',
                 'task.config_revision_conflict', 'task.field_in_use', 'task.endpoint_retired',
                 'task.invalid_request', 'task.unavailable', 'task.commit_unknown'),
)
