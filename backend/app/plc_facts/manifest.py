"""事实模块 v2 声明；模块启用不代表匿名准入或数据库已采用。"""
from app.module_registry import ModuleManifest
manifest=ModuleManifest(name='plc_facts',enabled=True,order=36,core_contract='aiis.backend-module/v1',
    requires=(),model_requires=(),exports=(),permissions=('plc-facts-read',),error_codes=('plc_facts.v2.invalid_credential', 'plc_facts.v2.scope_rejected', 'plc_facts.v2.sample_content_conflict', 'plc_facts.v2.expired_unconfirmed', 'plc_facts.v2.payload_too_large', 'plc_facts.v2.media_type', 'plc_facts.v2.invalid_request', 'plc_facts.v2.not_ready', 'plc_facts.v2.commit_outcome_unknown', 'plc_facts.v2.not_found'),
    routers=('app.plc_facts.api.v2:router',),models_package='app.plc_facts.models')
