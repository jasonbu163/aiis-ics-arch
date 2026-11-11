"""任务字段、资格和错误命名空间的模块装配。"""
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name='task', enabled=True, order=25, core_contract='aiis.backend-module/v1',
    requires=(), model_requires=(), models_package='app.task.models', permissions=(),
    routers=('app.task.api.routes:router',),
    exports=('app.task.models.fields:FieldConfigState', 'app.task.models.fields:FieldDefinition',
             'app.task.domain:task_number', 'app.task.domain:identifier', 'app.task.domain:local_time',
             'app.task.domain:wire_time', 'app.task.domain:encode_value', 'app.task.domain:decode_value',
             'app.task.domain:value_patch', 'app.task.domain:merge_values', 'app.task.domain:decode_values',
             'app.task.domain:slot_key', 'app.task.domain:invalid',
             'app.task.errors:TaskError', 'app.task.errors:TaskErrorCode',
             'app.task.eligibility:admit', 'app.task.eligibility:target_mapping',
             'app.task.eligibility:get_profile', 'app.task.eligibility:admit_read_target',
             'app.task.http:TaskRoute', 'app.task.http:actor', 'app.task.http:authorize',
             'app.task.http:commit', 'app.task.http:response', 'app.task.http:audit_event',
             'app.task.schemas.fields:Envelope', 'app.task.schemas.fields:ErrorEnvelope', 'app.task.schemas.fields:TaskDateTime',
             'app.task.services.async_fields:config_state', 'app.task.services.async_fields:definitions'),
    error_codes=('task.unauthenticated','task.forbidden','task.not_found','task.state_conflict',
                 'task.field_version_conflict','task.config_revision_conflict','task.observation_conflict',
                 'task.dispatch_conflict','task.action_request_conflict','task.plan_supplement_required',
                 'task.invalid_request','task.unavailable','task.commit_unknown'),
)
