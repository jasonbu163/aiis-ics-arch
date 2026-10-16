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
