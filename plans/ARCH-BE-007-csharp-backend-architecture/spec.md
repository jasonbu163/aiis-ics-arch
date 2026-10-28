Task ID: ARCH-BE-007
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 待 Human Owner 审阅精确 ARCH-BE-007 r1；本次仅交付设计草案，未授权 C# 软件实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 参考现有 FastAPI Backend 的独立 C# 后端架构设计与分阶段替代合同
Owner: AIIS ICS Architecture Backend
Acceptance Chain Reference: 本 spec 第 17 节；PM -> Human Owner 精确 Revision 批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Related Task: ARCH-MULTI-001, ARCH-MULTI-002, ARCH-BE-005, ARCH-BE-006, FF-003
Created: 2026-10-28
Updated: 2026-10-28

# C# 后端架构设计与逐步替代路线

## 1. 目标与已确认方向

本设计将当前 FastAPI Backend 的职责分层映射到 C# 生态，固定 FastEndpoints、EF Core/MySQL、DTO 校验、模块组织和逐步替代路线，作为后续有边界实施任务的设计依据。本次交付只有文档，不创建 C# 工程或实现接口。

Human Owner 已明确以下方向：

1. FastAPI 继续承担当前正式功能与交付，新业务不因 C# 学习而停止。
2. C# 首期以学习和固定架构为主，先实现少量完整业务切片；成熟后可独立承担 MES 对接，后续逐模块达到 Python 后端的业务能力，主要后端逐步转为 C#。
3. Python 与 C# 是可独立运行、按场景选择的后端实现。C# 自己拥有 API、校验、Service、事务、ORM 和 MySQL 读写，不固定放在 FastAPI 前面，不通过调用 FastAPI 代替自己的 ORM。
4. MES 由对方负责；本方负责产线侧 Backend、FF 和必要界面，业务数据库选用 MySQL。
5. 当前优先关注计划、实绩和实时显示相关能力。模块是否首期实现、实现哪些路由，由后续切片任务明确，不全量复制当前后端。
6. C# 首期不做登录认证。本设计不删除、不放宽现有 Python 认证，也不宣称两版本已完全等价。

“先用 FastAPI 顶着”表示 C# 某能力未完成或未验证时，正式调用方继续使用 Python 的完整能力；不是 C# 接口借用 FastAPI 完成数据库访问。

## 2. 本次范围与写入边界

### 2.1 文档 allowlist

| 路径 | 归属及允许变更 |
| --- | --- |
| 本 spec.md | PM 创建及修订本设计、需求、验收口径和真实审批记录 |
| [根 PLAN.md](../../PLAN.md)、[PLAN.zh-CN.md](../../PLAN.zh-CN.md) | 主协调只新增或同步 ARCH-BE-007 索引行 |
| [plans/README.md](../README.md)、[README.zh-CN.md](../README.zh-CN.md) | 主协调只新增或同步本 bundle 行，诚实注明后续角色文档尚未创建 |

本次不创建 tasks.md、checklist.md、第二份 docs 设计正文或 backend-dotnet 目录；不修改 ROADMAP、AGENTS、CODE_INDEX、已有任务正文、应用源码、测试、依赖、锁文件、真实配置、数据库或现场设备。已有 DAA、DS、FF 等并行改动必须保留。

### 2.2 明确排除

本次不安装 SDK/NuGet、不生成项目或 migration、不运行构建/服务、不创建监听端口、不执行 Docker、数据库迁移、数据补写、PLC 读写、部署、Git refs、commit/push。后续软件实施、真实环境采用和现场切换各自需要独立、精确范围。

首期软件范围还排除登录、JWT、RBAC、用户管理、管理员 bootstrap、远程 schema-maintenance、CA gate-token 等平台能力；不恢复 Celery、Redis、Beat、Flower、Python Worker 或旧工业命令合同。新任务不得以本设计为依据把这些现有 Python 安全边界匿名开放。

## 3. 当前基线与设计参考

本节是 2026-10-28 对工作树的只读源码核对，不是 C# 实现或运行证明。核对时 HEAD 为 1fa1ce50a521ebd51c2c43389db011a76f2d74bf；实际实施前仍需重新固定切片源码与合同，不以该 HEAD 代替当前工作树核对。

| 当前参考面 | 已确认事实及对 C# 的影响 |
| --- | --- |
| [Backend README](../../backend/README.zh-CN.md)、[Backend PLAN](../../backend/PLAN.zh-CN.md) | 当前正式后端是 FastAPI/SQLAlchemy/Alembic；已有公共能力与历史 gate 不构成 C# 已支持证明 |
| [模块 Registry](../../backend/app/module_registry.py)、[App 模块说明](../../backend/app/README.zh-CN.md) | 普通模块通过静态 manifest opt-in；路由启用不创建表；user/control_agent 仍是显式边界 |
| [Plan 模型](../../backend/app/plan/models/plan.py)、[Schema](../../backend/app/plan/schemas/plan.py)、[Service](../../backend/app/plan/services/async_service.py) | Plan 围绕唯一 coil_no，包含 Numeric 精度、校验、计划/实绩关联和 XLSX 用例；不能把整个模块等同于一条 MES 上料接口 |
| [Performance 模型](../../backend/app/performance/models/performance.py)、[观测输入](../../backend/app/performance/schemas/production_observation_in.py) | 包含实绩、过程样本、唯一键、来源身份和 users 外键；新观测区分缺字段及显式 null，不能机械复制为普通 nullable DTO |
| [Monitor 说明](../../backend/app/monitor/README.zh-CN.md)、[实时 Service](../../backend/app/monitor/services/async_realtime.py) | raw/latest 是项目无关事实；当前有 hasSnapshot、quality、collectedAt、stale 等含义，不等于已具备客户实时业务模型 |
| [公共 Schema](../../backend/common/schema_base.py)、[响应组件](../../backend/common/response.py) | camelCase 与递归响应序列化已有代码；SuccessResponse 和 StandardResponse 的形状不同，分页也存在既有结构，不能一律换成框架默认响应 |
| [数据库依赖](../../backend/database/session_async.py) | get_db 在 yield 后仍会 commit/异常 rollback；C# 采用明确 Service 提交边界，不能把依赖清理提交照搬为新标准或宣称旧源码已全部符合目标分层 |
| [HTTP mapping 时间规则](../../backend/app/performance/mapping_domain.py)、[Monitor 时间查询](../../backend/app/monitor/README.zh-CN.md) | 既有 HTTP 观测路径仍归一为无时区 UTC 并输出 Z；根 AGENTS 的新上海时间合同不等于旧路径和历史数据已整改 |
| [实绩下推 Service](../../backend/app/performance/services/async_performance.py) | 当前 push_down 创建 completed 记录，没有实际 MES HTTP 发送；不能当作可靠 MES 投递和回执能力的已实现依据 |

[ARCH-MULTI-001](../ARCH-MULTI-001-versioned-stack-roadmap/spec.md) 和 [ARCH-MULTI-002](../ARCH-MULTI-002-three-worlds-diagram-sync/spec.md) 提供方向背景；本设计不继承其范围批准、QA 或 Owner 验收。ARCH-BE-005/006 作为当前业务模块及 HTTP 观测参考，不自动扩展本任务范围。

[FF-003](../../field-flow/plans/FF-003-csharp-runtime-demo01/spec.md) 是独立 C# 现场运行时任务，与本后端的进程、源码、依赖和验收不同；同用 C# 不构成相互依赖，也不把 FF 的 PLC 驱动放进 Backend。

## 4. 独立后端关系与职责

两种实现的目标调用链分别为：

~~~text
前端 / MES / FF -> Python API -> Python Service -> SQLAlchemy -> MySQL
前端 / MES / FF -> C# API     -> C# Service     -> EF Core    -> MySQL
~~~

这是可按模块、环境或场景选择的实现关系，不是要求调用方同时向两版本发送业务写入，也不是固定的 C# -> FastAPI -> MySQL 网关链。学习阶段使用独立 MySQL 数据库；复用既有表的生产采用须先通过第 12 节的切换门槛。

| 责任 | Owner |
| --- | --- |
| 计划、实绩、业务关联、状态、业务事务和业务查询 | 被选定的 Backend 模块 Service |
| PLC 连接、采集、现场事件、PLC 写入及执行核实 | 独立 FF；后续 AW 接替另立任务 |
| MES 请求/响应报文适配、来源身份、投递与回执状态 | MesIntegration 与对应业务模块协作 |
| 资料补录、业务操作、实时显示 | 必要前端；不拥有最终业务规则或业务真相 |
| 业务数据、投递记录和实际处理结果的持久真相 | MySQL 中由相应模块拥有的数据 |

API 请求处理不得轮询 PLC。MES 工艺汇总上报频率与本地实时采集/显示频率分别定义，不能用“完工只上报一次”推导本地无需实时数据。

## 5. 技术栈与 Python 对应关系

| Python 参考职责 | C# 设计 | 保留的合同 |
| --- | --- | --- |
| FastAPI / APIRouter | ASP.NET Core + FastEndpoints Endpoint | URL、HTTP 方法、输入来源、状态码、响应含义 |
| Pydantic In / Out / Query / Page | 分角色 Request / Response / Query / Page DTO | 必填、可空、缺省、查询、分页和输出字段 |
| Pydantic validators | FastEndpoints Validator<T> / FluentValidation；跨状态规则进入 Service/Domain | 字段边界校验与业务校验分层 |
| Pydantic alias / JSON | System.Text.Json + 明确绑定/序列化配置及必要转换器 | camelCase、数值表示、时间、枚举、缺测 |
| SQLAlchemy Model | EF Core Entity + 显式实体映射 | 表名、列名、类型、精度、约束和关系 |
| AsyncSession / Session | 短生命周期 DbContext；后台宿主另建 scope | 生命周期、事务和资源释放 |
| CRUD | 模块 Persistence 查询/持久化代码 | 参数化查询、筛选排序、无隐式业务提交 |
| Service / Domain | Services / Domain | 用例编排、状态规则、事务边界 |
| manifest / Registry | 模块本地 ModuleManifest + 显式启动组合 | opt-in、稳定模块 ID、启用/依赖校验和无导入副作用 |
| common response / exception | Common 响应、业务异常与错误码组件 | 最终 JSON 与 HTTP 行为，而非类名 |
| pydantic-settings / settings | ASP.NET Core Configuration + typed Options | 显式来源、启动校验、秘密不入库/日志 |
| Alembic | 现有表仍由 Alembic 管理；EF Migrations 仅作为未来工具对应 | 每张表只有一个 schema 变更权威 |
| OpenAPI | FastEndpoints.OpenApi；交互 UI 单独选择 | 已启用路由与实际 DTO 合同一致 |

Pydantic 对应的是“DTO + 运行时校验 + 绑定 + 序列化”组合，不是 EF Entity，也不是只写一个有类型的 C# class。DTO 类型声明本身不证明非空、范围、跨字段和 wire contract 已等价。

采用 EF Core 和 MySQL Provider 生态，但本 r1 不锁定未经 restore/build 的精确版本组合。.NET 10 LTS 可作为候选；FastEndpoints、EF Core、Provider、数据库服务端和目标 OS 的精确稳定版本及锁文件归 S1 实施前门槛。不得为追随最高版本引入 preview 依赖。

MySQL 官方 Provider 与 Pomelo 是不同候选，版本不能混配或同时装成双 Provider；例如 Pomelo 9 稳定发布对应 EF Core 9，不能因应用目标为 .NET 10 就宣称它支持 EF Core 10。Provider 选择以官方兼容表和本项目切片验证共同决定，第 18 节保留来源。

## 6. 模块结构与依赖方向

### 6.1 设计目录

以下仅为未来目录设计，不代表目录或项目已经创建。首轮一个 API 应用项目即可；测试项目按真实验证需要创建，不预设微服务、多数据库、CQRS、消息总线或多层空接口。

~~~text
backend-dotnet/
├── Program.cs
├── Common/
│   ├── Contracts/              响应、分页、错误合同
│   ├── Errors/                 业务异常与错误映射
│   └── Time/                   业务时间边界与格式规则
├── Configuration/              typed Options 与启动校验
├── Infrastructure/
│   ├── Persistence/            DbContext、连接与共享映射装配
│   ├── Http/                   外部 HTTP 客户端基础
│   └── Logging/                JSON Lines 输出与日志装配
└── app/
    ├── Plan/
    ├── Performance/
    ├── Monitor/
    └── MesIntegration/
        ModuleManifest.cs
        Endpoints/
        Contracts/
        Validators/
        Services/
        Domain/
        Persistence/            需要持久化时才创建
~~~

每个真实业务模块沿用模块内分层；示意树在 MesIntegration 下展开一套结构，不要求四个模块一开始全部建立空目录。EF Entity 和实体映射放所属模块 Persistence，Domain 放不依赖 HTTP/EF 的规则；模块外 Infrastructure 装配 DbContext 和外部客户端。不要同时在多处维护同一 Entity 或表映射。

| 层 | 可以承担 | 禁止承担 |
| --- | --- | --- |
| Endpoints | 绑定请求、调用 Validator、注入 Service、输出合同 | SQL、事务控制、复杂业务规则、PLC 通信 |
| Contracts / Validators | 请求响应结构、字段及跨字段形状校验 | 数据库写入、业务状态切换、网络调用 |
| Services | 用例编排、业务规则、事务、幂等决策和结果 | 依赖 FastEndpoints Endpoint、HttpContext 或手工拼传输 JSON |
| Domain | 稳定状态、身份及纯规则 | EF DbContext、HTTP、PLC 驱动、环境文件 |
| Persistence | Entity、实体映射、查询与变更跟踪；SaveChanges 由 Service 控制 | 自行决定业务完成、提交跨用例事务 |
| Infrastructure | 连接池、HTTP 客户端、日志和外部错误转换 | 绕过所属 Service 修改其他模块业务状态 |
| Program.cs | 加载配置、校验、装配模块、启动 | DTO、SQL、业务实现、隐式 migration/seed |

plan、performance、monitor 三个稳定模块 ID 对应现有 Python owner。MesIntegration 是拟新增的对接 owner，稳定 ID 设计为 mes_integration，便于与后续 Python package 命名对应；当前 Python 尚无该模块，不能列为已经存在的实现。C# namespace/目录可使用 MesIntegration，路由名称另按接口合同确定。数据库列继续显式映射既有 snake_case，JSON 继续遵循合同。仅有一处使用的逻辑不提前抽成公共框架。

### 6.2 模块注册

每个模块本地声明唯一 manifest，包含稳定 ID、enabled、顺序、依赖和其 Endpoint/Service/Entity 出口；组合根只装配合法 manifest。与 FastEndpoints 自动 Endpoint 发现结合时，必须让 disabled 模块在路由注册前被过滤，不能只从 OpenAPI 隐藏。路由冲突、重复模块 ID 和缺少依赖应在启动失败并输出脱敏定位。

模块启用只控制 API 组合，不能创建/删除表、seed、开启采集或执行网络连接；改变模块拓扑后重启采用，不做热卸载。首期不注册 user、auth、CA 授权或 schema-maintenance 的匿名替代接口。

Plan/Performance 当前互有 model_requires。C# 不据此制造相互注入的 Service 循环，也不把相互引用当成必须一起完整迁移；必要只读引用及跨模块事务在切片 spec 明确，写入仍经所属业务 Service。

## 7. DTO、校验与 API 合同

### 7.1 DTO 与 Entity 分离

一个用例分别定义创建、更新、查询和输出 DTO；不把数据库 Entity 直接作为入参/出参，不让调用方修改 ID、来源回执、保存时间或内部状态。普通字段校验由 Validator 执行，唯一性、状态转换、业务关联及并发结果由 Service 与数据库约束共同保证。

选择一个接口时，先从对应 Python Schema、路由、Service、实际序列化和测试形成合同对照。需逐项固定：

| 项目 | 对齐要求 |
| --- | --- |
| 绑定 | path/query/body/header 的来源、名称、大小写及 alias 接受规则；不依赖框架猜测 |
| 缺字段/null/默认 | 三种状态分别定义；更新时未提供不覆盖，显式 null 按该字段合同接受或拒绝，不能把 0/空串当缺失 |
| 类型 | 非法类型、布尔冒充数字、字符串数值、溢出、NaN/Infinity 的接受/拒绝行为显式验证 |
| Decimal/FLOAT | 持久精度、舍入或拒绝规则、JSON number/string 表示按目标切片确认；不把所有数值一律转 double |
| 枚举 | 稳定英文 key；输出不使用 C# 枚举数字或中文展示值 |
| 嵌套结构 | camelCase 在 DTO、字典、数组与响应 data 内一致；动态业务标识不因盲目改 key 受损 |
| 时间 | 第 10 节的语义、offset、精度和自然日；不要依赖主机时区 |
| 分页 | page/pageSize、默认值、上限、排序稳定性、total/空集合，以及选中 Python 路由的实际包装结构 |
| 错误 | HTTP status、业务 code、errorCode 和字段错误结构；不以自然语言 message 作机器判断 |

既有 HTTP 观测采用严格 camelCase、拒绝未知字段、保留 model_fields_set，并将部分显式 null 拒绝；普通 Plan Schema 的行为不同。新 C# 只能按选定接口定义差异，不能声称“采用同一校验库”即可全部兼容。

### 7.2 响应与文档

内部 API 的目标公共成功信封为 code/message/data，业务失败还需稳定 errorCode；既有 SuccessResponse 的 timestamp、历史分页及错误路径是否保留必须在切片台账锁定。已被调用方依赖的形状不能在迁移时静默更换。

外部 MES 可能要求 code/msg 等不同报文，由 MesIntegration 映射；不要改全局内部信封去迁就一个对方协议。新外部 API 尊重 HTTP 语义；兼容旧 API 的 HTTP 200 + 业务 code 等行为逐接口记录，不把全部异常统一成成功。

FastEndpoints 的绑定失败、Validator 失败、业务异常和系统异常统一经过本项目错误映射；不能让默认错误 JSON 与成功信封形成未说明的第二合同。OpenAPI 显示实际启用的接口、字段必填/可空、错误、分页和已知认证差异；交互 UI 只用于接口调试，不等同于业务前端已接通。

## 8. EF Core、MySQL 与事务

采用短生命周期、按请求或明确业务单元创建的 DbContext；同一实例不并发执行查询，不注册为全局单例，不跨请求保存追踪 Entity。查询优先 async 并传递取消信号；纯读使用投影及需要时的 AsNoTracking，避免无边界 Include、导航循环和返回整张大表。

Service 是业务提交与回滚的唯一边界，Persistence 不自行 SaveChanges/commit 来决定业务完成。一个数据库业务动作及其幂等回执在同一 DbContext/事务完成；简单单次提交可使用 SaveChanges 的事务语义，多步原子用例显式事务。跨网络/MES/PLC 不宣称与 MySQL 构成原子事务。

数据库映射须逐项核对表/列名、ID、自增、字符集/collation、二进制业务键、可空、默认值、索引/唯一约束、外键/删除行为、DECIMAL(p,s)、FLOAT 和 DATETIME 精度。不能依赖 EF convention 自动给旧表改名、扩宽或建立级联删除。

数据库唯一约束负责并发兜底；预查询不能代替唯一约束。已提交成功前不返回“已完成”，提交结果未知时记录明确的未确认结果，不通过盲重试把同一业务效果再执行一次。对同 sampleId/请求身份的重放、不同内容冲突及并发竞争沿所属切片合同处理。

用户已确认 MySQL。首期不同时引入 MSSQL/PostgreSQL/SQLite 业务库兼容层；隔离学习库也不能用 EF InMemory 或 SQLite 测试结果代替 MySQL 精度、锁、事务和约束验证。

## 9. Schema 权威与首期无认证

### 9.1 Schema 权威

现有共享业务表继续由获批 Alembic/schema-maintenance 任务管理，C# 只做 Entity 映射和获准业务访问。C# 普通启动、模块注册、首次请求均不得执行 EnsureCreated、Migrate、DDL、seed、补用户或修改 migration history。

EF Migrations 是 Alembic 在 C# 生态中的工具对应，不表示首期要运行第二套迁移。若未来新建独立学习 schema 或把某个 schema 的维护权交给 EF，需另立任务明确表集合、唯一维护方、历史基线、迁移/回退及数据保留；同一张表不能同时由 Alembic 和 EF Migrations 管理。

从现库反向生成模型只能作为候选材料，需人工审核和差异检查，不是建立新 schema 真相的动作。表数、旧后台宿主、Projection、权限表和所有业务模块都不是首期必须复制的清单。

### 9.2 首期无认证的准确含义

C# 首期不实现登录/登出、JWT、刷新 token、账号、角色和权限；不生成可用默认账号，不伪造 current-user/admin，也不移除 Python 的认证依赖。

学习实例默认仅供本机或明确隔离环境使用，首期允许的 API 必须是实施 spec 显式列出的业务切片；不能为了“和 Python 一样”把 user、维护、授权执行等敏感接口匿名注册。未来承担真实 MES 接口时，其调用来源、网络暴露与对方接入要求单独确认，本设计不增加一种未被要求的认证实现。

需要 actor_user_id 或 users 外键的动作须在实施前分类：可空且语义允许时保留真实来源为空；必须有用户身份的动作首期不纳入。不得插入假管理员、关闭外键、删用户字段或把任意用户 ID 当作无认证兼容手段。

因此首期只能主张已选业务切片的限定等价，不能主张已登录前端、角色策略、审计身份或全部后端可直接切换。未来认证能力以独立任务补齐；用户此次“首期不做”不等于永久删除该平台能力。

## 10. 时间合同与既有差异

新设计遵循根 AGENTS：业务及存储时区 Asia/Shanghai；MySQL 业务日历时间保存上海本地 DATETIME，保留原有精度；普通业务 API 输出明确 +08:00。UTC/其他 offset 的外部日历输入在边界转换一次；Unix 时间戳、耗时和单调时钟按自身语义处理。

API DTO 可用 DateTimeOffset 表达带 offset 的外部时间，持久层将其按统一业务时区转换为明确的上海本地 DATETIME，读出再恢复 +08:00；具体转换器由公共 Time 边界统一提供，禁止每个模块散落 AddHours(8) 或把无时区数据库值按主机本地时间猜测。

至少区分事件发生、采集、接收、保存、实际更新和界面刷新时间。缺少真实日历时间保留缺失；读取/刷新不冒充 updatedAt。持久化系统时间优先沿已声明数据库时间来源；部署核验数据库时区，配置本机进程 TZ 不能代替数据库合同。

当前 Python mapping_domain 已将来源时间规范化为无时区 UTC，并在查询输出 Z。迁移该切片前必须确认该字段已有数据时区，再选择明确的新接口/字段版本或独立批准的整改方案：新增上海域保持与旧 UTC 域可辨识，或显式迁移后统一。禁止 C# 将旧 UTC DATETIME 直接解释成上海时间，禁止同字段混存两种时区，也禁止把全表加八小时当作本设计的默认实施。

实施前的对照必须覆盖跨上海零点、跨自然日查询、毫秒、缺时间、显式 offset 以及历史域；若未解决，相关切片不得被记为迁移等价。此设计记录差异，不修改 Python 或历史数据。

## 11. MES 对接、实绩和 FF

MesIntegration 承担对方报文的 Endpoint/客户端适配、来源标识、组包以及投递/回执状态；计划、实绩和监控状态通过对应模块 Service 写入。MES DTO 不直接成为数据库 Entity，也不把 PLC DB 编号/offset 当成业务身份。

入站接收、业务落库、待发送、MES 处理确认以及 PLC 实际执行确认是不同事实。HTTP 成功只按明确合同表示已接收或已处理；不能将 transport 200 自动解释为设备完成，也不能沿用当前 push_down 的本地 completed 记录去宣称真实 MES 投递成功。

需要异步/重试的对接必须先持久保存请求身份、规范化内容或指纹、目标、投递状态和回执关联；执行宿主、重试上限、结果未知核实、积压和人工恢复归后续切片 spec。可用明确的集成执行宿主处理，不能在本任务恢复旧 Worker 体系或无界后台轮询；不在数据库事务中等待 PLC/MES 长耗时动作。

FF 继续拥有现场连接和执行；将设备事实或事件经 Backend API 交给所属 Service。同一业务效果只选择 Python、C# 或后续被授权执行方中的一个有效 writer。切换前核对尚未确认事件、已提交回执及进度；双进程各有一张本地表并不自动形成跨进程幂等或互斥。

计划/工单/卷/批次之间的关系、MES 上下行方向、工艺汇总/状态事件/电耗/质量报文的详细字段与频率须由具体业务任务确认。未冻结项不在公共架构仓伪造为已批准合同，也不复制客户会议文件或真实产线数据。三块看板不自动等于三个新 Backend 模块。

## 12. 分阶段替代路线

| 阶段 | 交付目标与当前正式实现 | 准入/退出条件 |
| --- | --- | --- |
| S0 设计 | 本 r1 固定架构与替代合同；正式功能继续 FastAPI | Human Owner 审阅精确设计；不创建或运行软件 |
| S1 隔离学习切片 | 单独获批后创建最小 C# API 应用，以无用户身份依赖的 Plan 创建/查询作为候选，贯穿 DTO/Validator/Service/EF/MySQL；Python 继续正式交付 | 精确路由/表/字段、稳定版本组合、隔离 MySQL、合同/事务测试通过；候选不是当前实施授权 |
| S2 独立场景试点 | 选择已确认的一组 MES 或业务 API，由 C# 自己完成业务和落库；Python 继续其他正式功能 | 冻结接口与 schema、来源与幂等、真实调用边界、已知差异；独立验证后另行批准采用 |
| S3 按模块替代 | 按业务依赖交接 Plan/Performance/Monitor 等模块，已有前端/MES/FF 选择相应入口 | 每个模块通过同一基线数据/用例的等价检查，完成 writer 交接、回退和调用方验证；未补齐认证的受保护场景不得虚报等价 |
| S4 C# 为主 | 大部分已验收 Backend 能力由 C# 承担，Python 按仍有需要的场景保留 | 具体模块台账全部关闭或由 Owner 明确接受差异；Python 下线/数据迁移/部署另行授权 |

S1 可以调整首个切片，但必须重新明确其合同和边界；“少量完整切片”不是创建全部路由后返回假成功。S2 不要求先补齐整个 Python 后端，也不引入永久前置网关。业务功能可分期等价，语言不改变业务数据 owner。

### 12.1 等价与差异台账

后续每个切片任务至少维护以下列，不在本 spec 预填通过结果：

| 维度 | 当前设计要求 |
| --- | --- |
| 来源基线 | Python 源码/合同版本、数据库 schema revision、C# 候选及测试输入 |
| 路由与数据 | 方法/路径、DTO、错误、分页、数值、时间、关联、空态、状态转换 |
| 持久化 | 表/约束/事务、并发、回执、重放、保存后的读回与副作用 |
| 已知差异 | 首期无认证、未迁移接口、时间旧域、未接通的 MES/设备行为逐项列出 |
| 运行责任 | 本场景有效 writer、调用方入口、旧后台/Projection 是否停用、进度与未确认项 |
| 验收 | Development 自检、fresh Verification、Human Owner 与独立运行/现场 gate 分开 |

### 12.2 切换与回退

先完成隔离对照，再冻结被交接的模块写入范围，核对未确认请求、回执与消费进度，停用旧有效 writer 后启用新实现并核对实际调用方。不要让两版本同时消费同一现场事件来证明等价；需要影子比较时只读或使用隔离数据。

业务回退优先保留 schema 和全部已接收数据，停止新 writer、核对未确认结果后恢复已验证旧实现。回退不是清表、删回执、重置 unknown 或自动执行 schema downgrade；无法兼容的数据/状态须先制定显式恢复方案。

## 13. 配置、日志与可运维性

配置使用 typed Options，至少覆盖绑定地址/端口、MySQL 连接与池/超时、模块开关、业务时区、日志路径/级别、外部 HTTP 目标与超时。公开示例只用占位符；进程环境覆盖约定的文件来源，秘密由环境/受控秘密来源提供，不读取其他工程 .env，不复制 Python 的真实连接串。

启动先校验必填和范围，不在普通启动迁移/seed。健康信息区分进程存活、配置就绪、数据库可用及业务采集新鲜度；探针查询不得改变数据或使用 UI 刷新时刻制造新鲜度。具体 hosting、打包和现场后台运行验收另立任务。

日志采用 JSON Lines stdout 与持久日志，保留稳定 event、request/correlation ID、模块、业务/样本身份、结果、耗时、错误 key 和必要状态变化。覆盖启动/关闭、请求、校验失败、业务失败、事务失败、幂等重放/冲突、MES 投递与回执状态；高频只读按层级或采样控制噪声。无登录时记录真实来源/进程上下文，不编造操作者。

密码、token、Authorization、完整连接串、完整报文和客户数据不能进入默认日志。HTTP/数据库调用具备明确超时、取消及资源释放；调用取消不能抹掉已经提交或结果未知的业务事实。

## 14. 编号需求

| ID | 需求 | 设计位置 |
| --- | --- | --- |
| R01 | 本次仅交付可审阅的中文架构 spec 及最小索引，保持 draft 与角色边界 | 1、2、17 |
| R02 | FastAPI 继续正式交付，C# 是独立直接落库的后端，逐步替代 | 1、4、12 |
| R03 | 使用 FastEndpoints、EF Core/MySQL、DTO/FluentValidation/JSON 组合，版本配套验证 | 5、18 |
| R04 | 单 API 项目、业务模块内分层、薄入口、模块 opt-in 与无副作用注册 | 6 |
| R05 | DTO/Entity 分离，字段/缺失/null/枚举/数值/分页/错误/OpenAPI 以合同对齐 | 7 |
| R06 | DbContext 生命周期、串行实例使用、Service 事务和唯一约束/幂等 | 8 |
| R07 | 既有表 Alembic 单一 schema 权威，禁止普通启动 DDL/seed 和双迁移管理 | 9.1 |
| R08 | C# 首期无登录认证，不降级 Python 安全边界，不伪造用户或绕过外键 | 9.2 |
| R09 | 新时间合同上海化，显式记录旧 UTC 差异及独立整改门槛 | 10 |
| R10 | Backend/FF/MES 分工，持久状态与各层确认含义分开 | 4、11 |
| R11 | 客户接口细节另行确认，公共仓只固定通用结构与边界 | 2、11 |
| R12 | 替代路线、限定等价、唯一 writer、切换与保留数据回退 | 12 |
| R13 | typed 配置、JSON Lines 日志、秘密保护和有界外部调用 | 13 |
| R14 | 设计验收与未来运行验证分开，检查可复现且不夸大证据 | 15、17 |

## 15. 验收标准与未来验证

### 15.1 本设计文档的可检查标准

| AC | 文档验收标准 | 需求 |
| --- | --- | --- |
| AC01 | 仅新 spec 与四个对应索引允许变化，无软件/配置/schema/客户材料新增 | R01、R11 |
| AC02 | 元数据为 ARCH-BE-007/r1/draft；角色文档按阶段产生，未推断精确批准或 QA | R01 |
| AC03 | 两条独立调用链明确，C# 可直接经 ORM 写 MySQL，没有固定前置网关依赖 | R02 |
| AC04 | Python -> C# 职责对照覆盖 API、Schema、校验、JSON、ORM、Session、Service、注册及 migration | R03 |
| AC05 | 稳定版本组合是未来门槛，MySQL Provider 不混配，未声称 restore/build/生产支持 | R03、R14 |
| AC06 | 目录仅为设计，模块分层/依赖/薄 Program 和 disabled 路由语义明确 | R04 |
| AC07 | DTO/Entity 分离；缺字段/null、数值表示、时间、错误和分页差异有明确对照要求 | R05 |
| AC08 | DbContext 非单例/同实例不并发、Service 提交边界和数据库并发约束明确 | R06 |
| AC09 | Alembic 继续拥有既有表；普通启动 EnsureCreated/Migrate/DDL/seed 和双管理同表被排除 | R07 |
| AC10 | 首期无登录/JWT/RBAC/用户管理，Python 认证和 users 外键不被伪造或绕过 | R08 |
| AC11 | 上海时间、事件/采集/保存含义和既有 UTC 源码差异均被记录，不要求盲迁历史 | R09 |
| AC12 | Backend 不轮询 PLC；FF-003 与本 C# Backend 分别归属，MES/DB/设备确认不混淆 | R10 |
| AC13 | 当前 push_down 的有限行为、工单/卷/批次未定以及本地实时/MES汇总差异明确 | R10、R11 |
| AC14 | S0-S4 均说明交付及准入，完整业务切片优先，未来主要使用 C# 的目标保留 | R02、R12 |
| AC15 | 台账覆盖已知认证/时间/未迁移差异；切换有有效 writer 和未确认请求交接 | R12 |
| AC16 | 业务回退保存已收数据与回执，schema downgrade/真实切换另行批准 | R07、R12 |
| AC17 | 配置、日志、脱敏、超时/取消和无伪造操作者的约束可查 | R13 |
| AC18 | 本次成文自检、未来软件验证、独立 QA 与 Owner gate 清楚分离，链接可解析 | R14 |

### 15.2 后续实施最小验证矩阵

下表是未来实施验收门槛，本次不执行，也不预填通过：

| 验证面 | 最小用例与证据 |
| --- | --- |
| 工程与模块 | 精确稳定依赖 restore/build；启用/停用路由和 OpenAPI；冲突/缺依赖启动失败 |
| 输入/输出合同 | 正常、非法类型、缺字段、显式 null、默认值、未知/重复字段、枚举、嵌套 JSON、分页/错误 |
| MySQL 映射 | 真实隔离 MySQL 的读写回读、精度/字符/时间/约束/外键/删除行为，启动前后无隐式 DDL/seed |
| 事务 | 成功提交、多步失败回滚、并发唯一键竞争、提交确认丢失后的可核实结果 |
| 幂等 | 同身份同内容重放、不同内容冲突、重复投递、重启后回执/进度保持 |
| 时间 | 上海自然日边界、显式 offset、毫秒、缺时间、历史 UTC 域不误解释 |
| 业务与替代 | 同一隔离数据与请求比较 Python/C# 数据结果、状态和错误；已知差异逐项列明 |
| MES/FF | 使用获批本地夹具核对请求/回执含义；真实 MES/PLC/现场托管另有授权和证据 |

构建、接口测试、隔离 MySQL、本地夹具、真实设备、长稳、部署和 Human Owner 接受是不同证据层；一项通过不代替其他层。

## 16. 风险与待确定项

| 风险/问题 | 处理与解除条件 |
| --- | --- |
| 把框架默认行为当作 Python 合同 | 每个迁移切片固定真实请求/响应和持久化对照；未测字段列为未支持 |
| Provider 主版本不兼容或新文档混有 preview | S1 前固定稳定组合及官方来源，经过 restore/build 和 MySQL 切片验证 |
| 双版本同时写相同业务、回执不同步 | 切换前明确有效 writer、身份、消费进度、未确认结果与回退，不能靠不同进程各自去重 |
| 无登录切片依赖用户身份或前端现有权限 | 选择无身份依赖切片，受保护动作延期；未来认证单独范围 |
| 旧 UTC 数据被误读为上海、数值或 collation 行为变化 | 先盘点数据合同，差异整改/迁移独立批准；不盲改历史 |
| 只搬路由而未实现 MES 投递/回执或业务事务 | 用完整切片及实际持久化/回执用例验收，不用假成功占位 |
| 客户待确认内容被写成公共合同 | 工单/卷/批次、方向、字段与频率归消费项目业务任务，公共架构不代做业务决定 |

开放项保留为后续任务的精确输入：首个切片最终路由/表集合；精确 .NET/FastEndpoints/EF/Provider 版本及目标 MySQL 版本；现有时间域整改方案；MES 接口方向/字段/回执含义；真实采用的网络接入条件；每个模块未来认证、数据与 writer 交接顺序。这些开放项不阻止审阅当前架构，但在相应实施门槛前必须关闭。

## 17. 审批、角色 handoff 与本次检查

### 17.1 真实审批历史

| 日期 | 事件 | 本任务状态及边界 |
| --- | --- | --- |
| 2026-10-28 | Human Owner 要求参考现有 FastAPI 落 C# 架构 spec，先只改文档，C# 首期不做登录 | 授权形成 PM 草案；尚未看见并批准精确 ARCH-BE-007 r1 |
| 2026-10-28 | 命名 pm 角色形成此 r1 | draft；无 Development、独立 Verification 或 Owner 最终验收结果 |

PM 配置入口为 [.codex/agents/pm.toml](../../.codex/agents/pm.toml)，本次选择 agent_type=pm。该 TOML 的 gpt-6.1-sol/max 是配置证据，不作为独立观测到的运行模型/effort 遥测。

本次停在设计审阅 gate。精确设计批准不等于软件开工、数据库采用或部署授权。后续若整理/核验本设计，仍按文档 allowlist 和角色权威推进；若进入 C# 工程或接口实施，须建立明确切片、源码 allowlist、依赖、数据库及验证范围的独立实施任务，再按 PM -> Human Owner -> Development -> fresh-context Verification -> Human Owner 推进。

适用 skill：本设计使用 aiis、project-governance，并参考 backend-arch 和跨语言结构标准。后续后端实施继续使用 backend-arch；新增用户可见文案使用 i18n-workflow；源码/结构变化使用 code-document-indexer；若涉及打包、前端或现场 runtime，再进入相应 skill，不因为本架构草案就启动这些范围。

### 17.2 PM 成文检查记录

本节只记录 PM 草案成文检查，不是 Development 自检、独立 QA 或验收。主协调的机械索引检查也不升级为独立 Verification。

- 已只读核对第 3 节引用的当前源码、模块/数据库/认证边界和根治理入口；ARCH-BE-007 写入前未发现既有同 ID spec。成文后执行下列搜索，只返回本 spec，退出 0：

~~~bash
rg -l --glob spec.md '^Task ID: ARCH-BE-007$' plans backend field-flow automation-world
~~~

| 检查者与方法 | 实际结果及边界 |
| --- | --- |
| PM：Agent 辅助 Python 的只读内联文本检查 | 退出 0；必需元数据合法，章节 1–18 连续，25 个本地 Markdown 链接存在，R01–R14/AC01–AC18 唯一且引用有效，围栏闭合、无尾空白；仅形成 spec，未创建 tasks/checklist/backend-dotnet |
| 主协调：同范围的元数据/链接/编号/空白及阶段检查 | 退出 0；结果同上。只检查 Markdown 与文件存在性，不执行应用代码 |
| 主协调：逐文件比较索引写入前后的字节内容 | 四份索引各新增一条本任务 draft 行；剔除该唯一新增行后，各文件与本次写入前内容逐字节一致，保留已有并行修改 |
| 主协调：下方限定路径 diff 检查 | 退出 0；spec 为未跟踪新文件，另由 PM/主协调的文本检查覆盖其空白，不能仅靠 git diff 推断新文件已经检查 |
| 主协调：下方全库治理 checker 的修改前后比较 | 两次均退出 1，诊断均 320 行，诊断内容多重集一致、新增诊断 0；全库检查未通过，既有诊断不在本任务整改范围 |

主协调实际限定 diff 命令：

~~~bash
git diff --check -- plans/ARCH-BE-007-csharp-backend-architecture/spec.md PLAN.md PLAN.zh-CN.md plans/README.md plans/README.zh-CN.md
~~~

主协调实际全库治理命令：

~~~bash
bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch
~~~

内联文本检查的复现口径为：按行解析唯一元数据；提取 Markdown 链接并相对本 spec 解析本地目标；比较声明的需求/AC 集合及其引用；检查围栏配对和逐行尾空白；核对后续角色文件及 C# 工程目录未形成。索引保全检查须在写入前保留各索引字节快照，再去除本任务新增行作等值比较；不能拿 Git HEAD 代替已有 dirty 内容。

当前未运行 C# restore/build、API、数据库、Docker、PLC、部署或现场验证；未发生 Development handoff、fresh-context Verification 或 Human Owner 精确 Revision 批准。这些检查只证明本次文档结构、链接与索引保全，不能记为软件验证、独立 QA 或架构已获最终接受。

## 18. 官方技术来源与核验边界

以下是主协调于 2026-10-28 核对的官方资料，用于技术职责和版本选择规则；网页资料不是本项目已安装、构建或运行的证据：

1. [FastEndpoints Get Started](https://fast-endpoints.com/docs/get-started)：Request/Endpoint/Response 及 Endpoint 装配。
2. [FastEndpoints Validation](https://fast-endpoints.com/docs/validation)：Validator<T> 使用 FluentValidation；当前框架提供相应发现/集成能力，具体版本行为需随锁定版本验证。
3. [FastEndpoints OpenAPI Documents](https://fast-endpoints.com/docs/openapi-documents)：当前 FastEndpoints.OpenApi 基于 Microsoft.AspNetCore.OpenApi；生成文档与 Scalar/Swagger UI 分开，不把历史 Swagger/NSwag 方案当成唯一当前默认。
4. [EF Core DbContext](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/)：短生命周期工作单元、配置和同实例不得并发操作。
5. [EF Core Database Providers](https://learn.microsoft.com/en-us/ef/core/providers/)：Provider 与 EF 主版本兼容规则。
6. [MySQL Connector/NET EF Core Support](https://dev.mysql.com/doc/connector-net/en/connector-net-entityframework-core.html)：官方兼容表；页面含未来/preview 说明，不能据此默认引入预发布依赖。
7. [Pomelo MySQL Provider](https://github.com/PomeloFoundation/Pomelo.EntityFrameworkCore.MySql)：官方 release/兼容矩阵，与 Oracle Provider 分别评估。
8. [EF Core Migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/)：迁移工具概念；不改变本项目现有表的 Alembic 权威。

本 spec 的技术选择属于设计，精确软件支持矩阵与性能/现场能力仍待相应独立实施验证。
