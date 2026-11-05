# 后端模块公共合同 v1

[English version](MODULE_CONTRACT.md)

`aiis.backend-module/v1` 是在已验证Core源码与uv.lock版本上的Python源码合同。合规模块放入
`app/<module>/`，显式声明依赖、另行获准执行Alembic增量并重启后，可发现API、metadata和权限声明。
它不安装依赖、不建表、seed、授权账号或启用writer。user/control_agent仍显式装配。
可信Python import可执行任意代码；预检是规范检查，不是沙箱。

## 公共Python入口

机器真相为[module_contract.py](module_contract.py)的CORE_CONTRACT、PUBLIC_SYMBOLS和有界legacy清单。
测试锁定现有签名、字段与wire语义；私有helper/实现文件不是扩展点，破坏性变化需新合同版本及独立批准。

| 入口 | 支持范围 |
| --- | --- |
| app.module_registry | ModuleManifest |
| database | Base、TimestampMixin、IntPk、Timestamp、UpdatedAt；get_db/get_db_session、get_sync_db/get_sync_db_context/create_sync_session既有签名与调用方Session归属 |
| common.schema_base | ApiSchema、to_camel |
| common.response | SuccessResponse、StandardResponse、serialize_api_data；既有信封、别名、分页形状 |
| common.exceptions / core.deps | BusinessException；get_current_user、get_current_active_admin、require_permissions |
| 显式user类型 | app.user.models.user:User、app.user.schemas.user_out:UserResponse；只读类型，不公开任意user CRUD |
| common.log / settings | log_event、logger；新模块只读取settings.BACKEND_MOCK_ENABLED及纯路径helper resolve_env_file |
| 可选CRUD | common.async_crud_base:BaseService、common.sync_crud_base:SyncBaseCRUD；既有get/list/create/update/delete及不commit语义 |
| 可选Projection | projection.registry的ProjectionHandlerDescriptor、ProjectionHandlerInput、ProjectionHandlerGroupIdentity、ProjectionInvocationContext；本地同步声明，不公开runner/runtime内部 |

API只用异步Session；本地Projection只用调用方同步Session，保留business/cursor/audit同事务。
模块不得持有全局Session、依赖engine内部或读取私有Settings。第三方包必须已在消费方获批锁文件/环境内。
common.data_keys、15个补回全局错误、既有lineage错误和两个schema维护错误仅为本批旧owner的有界兼容。
精确符号和归属列在机器清单；未来模块状态/规则放自有domain/data_keys，错误用自有StrEnum及
`sample.invalid_value`等稳定命名空间，不向Core追加业务枚举或错误。
预检沿实际BusinessException错误参数追踪literal import、别名、薄重导出、局部literal赋值及工厂实际调用参数。具体枚举注解可辅助提供来源，但调用点可定位枚举时不要求注解。枚举类名不决定错误语义；普通领域状态StrEnum只有用作业务错误时才参与错误声明。实际错误值与manifest声明必须一致，并校验owner命名空间及Core/其他owner碰撞。只有源码及调用点仍无法定位具体StrEnum时才以error-source阻断；泛型或无参数注解本身不导致拒绝，不新增类名/文件名/注解强制合同。

BusinessException接收Core ErrorCode与非空字符串值StrEnum，裸str/数值Enum是编程错误；保留
error_code/code/message、HTTP200业务失败及code/message/data:null/errorCode，旧snake_case key不变。

## Manifest声明

保持api/models/schemas/crud/services/mocks/seeds七包和薄入口；manifest只用literal keyword，
不为发现导入Service、不执行运行工作。英文pair提供完整最小示例，所有字段语义相同。

- core_contract精确为aiis.backend-module/v1；旧未变化manifest默认v1并诊断legacy_default。
- requires声明直接Service/handler/函数、DTO和纯key依赖；提供方存在、兼容且enabled。
  runtime缺失/关闭/self/重复/环路阻断并报告链；order只保持(order,name)，不变依赖排序。
- model_requires声明model包、FK/relationship闭包，以及API/CRUD/Service任意文件直接引用的公开ORM Model。
  分类追踪原SQLAlchemy映射class及同class薄重导出，不能凭消费者目录或Model名称猜测。
  提供方须有manifest/models_package/export，但其API可以disabled；不因此取得API、DDL或writer权限。
  若同时显式声明requires，仍受enabled限制。双向metadata关系可有环，真实Python循环不豁免。
  字符串relationship按限定原映射class解析；SQLAlchemy模块后缀/裸类名须唯一定位。同名歧义明确阻断，不由后扫描owner覆盖；薄重导出的同一Model保留原定义归属。
- exports用本owner精确module:attribute字符串。跨owner必须用公开入口，私有CRUD/实现import定位失败。
  同class重导出不增加表或owner。disabled的runtime依赖inactive；Service export只静态验证存在，
  不eager import该Service；metadata与Model export仍加载/验证。
- error_codes为本owner稳定错误值，匹配本地StrEnum并与Core/其他owner核对唯一性；legacy同一枚举不重复claim。

没有manifest即跳过；内部import/错误声明不吞掉。空/未知/disabled grants保留WARNING+ignore，声明权限
不授权账号。user/control_agent不能成为普通requires目标。现有成功信封/camelCase与认证HTTP语义保持。

## 预检和冲突

```bash
uv run python -m app.module_preflight --help
uv run python -m app.module_preflight --project-root /private/tmp/public-backend --check-only
```

裸入口只帮助。源码检查不导入settings/App/database，不DDL或连接外部；检查literal/相对import、声明路径、
Model/FK/关系、公共Core符号及Settings访问。动态业务import/exec不在保证内并失败。
诊断只含stage/module/location/identifier/other owner，不输出秘密配置。
正常发现共用检查；ready前对象检查拒绝重复router、Model/Table、permission、error和最终method/path，
覆盖显式Core/框架路由。参数名不同仍同形；不同method、静态/current与/{id}可依原顺序共存。
不顺序覆盖或静默跳过；metadata加载不执行migration。

## 可复现源码profiles

[fixture生成器](../tests/module_admission_fixtures.py)从不可变C0
363b297bffe65e020108f5504766b4fb1ec3b381叠加五个窄合同patch，以及r3 system manifest/import和C0 monitor
manifest overlay构造C2。C0公开占位snapshot policy仅为测试配置，monitor事实路由/模型仍来自C0，无真实env。
C2保留14表并运行原Core sanitization断言；core-files.json记录来源/overlay SHA256并冻结。
E只加入admission_probe（独立15表）和admission_summary（组合16表）、显式合成revision及自有key/错误/权限，
Core指纹不变。F是本任务58表完整回迁profile，保护旧16表并新增42表后继。
这些数字是各fixture预期，不是全仓永久表数或中央模块allowlist。

```bash
uv run python tests/module_admission_fixtures.py --profile C2 --output /private/tmp/module-C2
uv run python tests/module_admission_fixtures.py --profile E --summary --output /private/tmp/module-E
uv run python tests/module_admission_fixtures.py --profile F --output /private/tmp/module-F
```

A/no_db使用公开显式进程配置、项目既有uv环境及生成器拒绝DB连接guard。源码组合、mock、recorder/offline SQL
和前端合成fixture不证明真实持久化；采用前仍需独立批准的可丢弃MySQL8.4.6迁移/API/约束/回滚证据。
Docker、数据库动作、部署、真实设备与发布分别经过后续gate。


## 模块本地运行配置

`settings.resolve_env_file() -> Path`是唯一加法公开helper：源码计算backend同目录.env，冻结计算可执行同目录.env（既有Docker入口为/app/.env）。函数本身只算路径；导入settings模块仍有原模块级Settings初始化，不能宣称整个import无env副作用，也不公开其他私有Settings字段。

获批equipment scope归其本地BaseSettings及懒依赖。显式参数优先process env、process优先选定dotenv；测试明确合成文件或_env_file=None，不建立跨应用缓存或import时配置实例。helper不是设备目录、授权或新配置平台。真实env采用/重启及MySQL验证仍经独立运行gate。

BE003调用generate_full_profile须显式传profile_name="BE003", expected_table_count=60, target_revision="e4f6a8b0c2d4"；新全树副本不能冒称冻结BE005 F/58。C2/E原14/15/16保证和断言保持。


## 匿名集成原语

A0只公开 `module_contract.PUBLIC_SYMBOLS` 中有限的 `common.integration` 符号。业务字段、模块StrEnum错误、SQL及生命周期仍归模块。版本常量为 `CONTRACT_VERSION="aiis.business-integration/v1"`、`DIGEST_PROFILE="bi-json/v1"`。

| 入口 | 公共签名 / 行为 |
| --- | --- |
| `envelope` | `IntegrationSchema`、`IntegrationEnvelope[DataT]`、`Identifier`、`SourceTime`、`BUSINESS_TIMEZONE`；严格camelCase、禁止未知字段，来源引用为有限判别类型。 |
| `envelope` | `identifier(value, maximum=128)`、`source_time(value)`、`shanghai_time(value)`、`fact_time(value)`、`validate_source_clock(value, database_now)`；上海业务毫秒，引用保留必要小数秒精度，DB时钟必须显式注入。 |
| `canonical` | `canonical_bytes(value) -> bytes`；精确JSON number、UTF-8字节排序，不改键。格式化前限制256位有效数字/绝对指数1000以拒绝极端值；DTO继续收窄实际存储域。 |
| `canonical` | `integration_digests(envelope, resource, parent_record_id=None) -> (requestDigest, businessDigest)`；data键集表达字段存在，业务对象为 `{resource,parentRecordId,data}`。引用按规范字节排序；非过程父为null。FLOAT32采用实际binary32的精确十进制，不依赖默认float打印。 |
| `http` | `strict_json(body) -> dict`、`IntegrationPayloadError(status,suffix)`、`IntegrationRoute`、`MAX_BODY_BYTES=65536`、`MAX_DEPTH=12`；原文Decimal、重复键拒绝、有界流读取及局部脱敏HTTP错误壳。模块子类声明owner/error enum；响应前完整退出yield依赖。 |
| `receipt` | `IntegrationReceipt`、`receipt_response(receipt, replay=False) -> bytes`；显式稳定字段、保留首次结果，重放仅改变outcome为duplicate。须在可靠commit后调用并使用显式JSON响应；纯函数本身不能证明数据库提交。 |

子模块其他导入/helper均私有。原语不导入业务表，不实现动态handler/通用CRUD平台，旧 `serialize_api_data` 不变。新接口实施前须定义typed data、存在/单位/时间、业务/投递键、两摘要、原子事务、稳定ACK/恢复、保留和认证/准入；破坏语义变更需新主版本。规范例子及向量见 [ARCH-BE-010](../../plans/ARCH-BE-010-anonymous-business-integration/spec.md)与[开发记录](../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md)。

各owner使用本地 `{EQUIPMENT,PERFORMANCE,MONITOR}_INTEGRATION_{ENABLED,EQUIPMENT_IDS_JSON,PRODUCER_IDS_JSON,STORAGE_PROFILE}`，默认False / `[]` / `[]` / `unadopted`；设备scope最多256个精确标识。显式构造优先process env，再选定dotenv，再默认；每应用懒固定独立配置。A0始终在DB访问前对合格准入返回模块 `integration_not_ready`，配置字符串不证明G-T。没有获批migration的Model只是准备，不能把本切片部署成已启用业务provider。

独立命名的 `BE010-A0` 公开fixture有68张metadata表、84项公开示例配置（原72项完整原文前缀加12项默认关闭配置）。`target_revision=null` 与 `schema_state=models_only_unadopted_no_migration` 明确尚未实现新migration。冻结C2/E/F/BE003/BE006 fixture及断言保持，不以其历史固定数量冒充本profile。


## 有界业务时间源码接面（BE010 r2）

`common.integration.storage` 精确公开 `StorageProbe`、`AdoptionContext`、`parse_adoption_manifest(value,module)`、`validate_adoption_probe(manifest,probe)`、`to_storage_time(value,basis)`、`to_legacy_time(value,basis)`。均为纯函数/值，不访问配置、文件、SQL、Session或目标。各owner仅通过自身manifest为只读维护工具export `integration_storage:BUSINESS_TIME_COLUMN_PROFILE` 与 `crud.sync_integration:probe_storage(db)`；async探针不跨模块公开。探针使用传入会话固定读取UUID/schema/revision/UTC时钟，不创建/提交会话，revision采用共享锁current read。

`IntegrationSuccess[ReceiptT]` 提供typed code/message/data信封。八路请求、具体回执、有限HTTP错误类型仍归owner。新模块自选data及状态规则，不必复制这八类资源或固定时间列。

历史A0 fixture继续标识为 `BE010-A0`（68 metadata/84项/models-only），重建其配置/schema面时排除BE009及新迁移；运行实现源码仍来自当前树。当前源码命名 `BE010-r2-A`：应用表按71→75接链，公开example共91项（旧69+BE006 3+A0 12+BE009 4+采用路径3）。`source_ready_unadopted`只表示源码状态；真实目标采用、schema迁移、数据库/Docker/B及Owner接受仍是独立gate。
