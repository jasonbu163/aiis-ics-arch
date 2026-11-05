Task ID: ARCH-BE-008
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已明确批准 ARCH-BE-008 r1 的 A+B；交命名 Development（agent_type=development，任务名 csharp_backend_dev，由主协调启动）按获批范围创建 tasks 并实施，完成后交新 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: backend-dotnet 首期 Plan 创建、按 ID 查询及分页列表的完整 MySQL 业务切片
Owner: AIIS ICS Architecture Backend
Acceptance Chain Reference: 本 spec 第 16 节；独立 PM -> Human Owner 精确范围与运行批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Related Task: ARCH-BE-007, ARCH-BE-005, FF-003
Created: 2026-10-28
Updated: 2026-10-28

# C# 后端首期 Plan 业务切片实施规格

## 1. 目标与当前授权

Human Owner 已批准 [ARCH-BE-007 r1 架构设计](../ARCH-BE-007-csharp-backend-architecture/spec.md)，并于 2026-10-28 明确批准 ARCH-BE-008 r1 的 A+B 进入 Dev：首期工程放根目录 backend-dotnet、数据库使用 MySQL，完成计划创建、详情及分页列表，并用本 spec 的专属可丢弃 MySQL 验证，首期不做登录认证；开发完成后交独立 Verification。

本任务将 S1 收敛为 Plan 创建、按 ID 查询、分页列表三条业务 API，贯穿 DTO -> Validator -> FastEndpoints Endpoint -> Service -> EF Core -> MySQL -> 真实响应。C# 自己落库，不代理 Python；FastAPI 继续原有正式功能和交付，不在本任务被停用或修改。

ARCH-BE-008 是独立的软件切片 capability 与批准链，仅与 007 相关，不继承 007 的设计批准。当前状态 owner_approved，精确 r1 的 A+B 已获独立明确批准；由命名 Development 按本 spec 创建 tasks、backend-dotnet 及专属环境并实施。PM 本轮仅记录批准与交接，不创建这些文件或资源，不预填实施或验证结果。

首期不实现完整计划 CRUD、XLSX、实绩关联、MES 发送、PLC 操作、Projection、用户/登录/JWT/RBAC/API key 或生产采用。单切片通过不代表整个 Python Backend、既有登录前端或 MES/FF 已可切换。

## 2. 阶段与操作批准边界

| 阶段 | 获批后允许的工作 | 独立边界 |
| --- | --- | --- |
| 当前 PM | 本 spec；007 真实批准记录；主协调同步四个根索引 | 仅文档，无任何软件实施或运行 |
| A 源码与本机依赖准备 | 第 5 节源码/测试/文档；任务私有 SDK；固定 NuGet restore/lock/build；无数据库的规则、序列化、注册和输入失败测试 | 必须先明确批准 008 r1 的 A；不启动 Docker、不应用 fixture DDL、不连接任何业务库 |
| B 专属可丢弃 MySQL 验证 | 第 11 节唯一资源上的 Docker pull/up/stop/start/down、test-only fixture DDL、合成数据、独立 API 启动及 MySQL 测试 | 根契约要求 Docker/数据库具体动作另行明确批准；可在审阅本 r1 时一次明确批准 A+B，也可只批准 A |
| C 真实采用 | 共享/客户数据库、已有服务切换、网络暴露、MES/PLC、部署 | 完全排除；A/B 批准、QA 或任务验收均不授权 |

若只批准 A，Development 可以完成源码和无库检查，但必须将 B 标为未执行，不能宣称完整 MySQL 闭环通过或用 InMemory/SQLite 代替 B。未明确提及 B 的“批准进入 Dev”不自动授权 Docker、数据库 DDL 或测试数据写入。

第 16 节保留原 A/B 审阅口径并记录真实决定。Human Owner 已明确批准本 r1 的 A+B；下列命令和测试仍是待 Development 实际执行并记录结果的计划，批准本身不表示已运行或通过。

## 3. 来源权威与冻结基线

以当前 Python 源码和 d2f4a6b8c0e2 的 plans 结构作为代表性参考；本 spec 中明确冻结的三接口合同与差异，是 C# 首期实施权威。Python 的其他路由/Schema 不因同属 Plan 就进入范围。

| 来源 | SHA256（2026-10-28 只读核对） |
| --- | --- |
| [Plan Model](../../backend/app/plan/models/plan.py) | 53d37fa5659fe5959008ec9725aa33c7db1b1b5153884667f77d6bd880d5665b |
| [Plan Schema](../../backend/app/plan/schemas/plan.py) | e331588f506f6d407c3c54e6216c8b64f0d19453fba872a6e1e332158a8eb58f |
| [Plan API](../../backend/app/plan/api/routes.py) | b0d7de2c3bb37c7f1e75469fe225e46141cd28c7143b196c8c9381c0dd6ac8cf |
| [Plan Service](../../backend/app/plan/services/async_service.py) | 867edcdf7e958e6132abc24d9de394f1e96c5ad8eda9da8b655b79b4b18351f3 |
| [Plan CRUD](../../backend/app/plan/crud/async_crud.py) | 64f0b283f3177a8e333413a5dd78d3ea161cb7fe0d0e740d609ae089fd03dbc1 |
| [Plan Domain](../../backend/app/plan/domain.py) | 09b4b198165f3c1ad7aa894430b1419bd43eef7350150c110e72417a409f675d |
| [d2 plans migration](../../backend/alembic/versions/20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py) | 806b008ebc4d232326db9967132a5bdb5d507518dca96017592ed80e00d056eb |
| [公共响应](../../backend/common/response.py) | 65949365deb1a4cbf884355ff8345f6e541cdee53a35a5ffda4200b077249456 |

另参考 [Schema 基类](../../backend/common/schema_base.py)、[错误注册](../../backend/core/registrar.py)、[数据库依赖](../../backend/database/session_async.py)、[模块 Registry](../../backend/app/module_registry.py) 和根 AGENTS 的时间合同。当前只核对源文件，不声称启动了 Python 或 C#。进入 Dev 时重新核对上述来源；实质合同漂移返回 PM，不能默默沿用旧哈希或扩大切片。

## 4. 固定的稳定候选组合

本表冻结一个待验证组合，避免 Dev 再自由选择框架、Provider 或测试生态。版本来自主协调于 2026-10-28 核对的官方页面/包元数据；尚未 restore/build/MySQL 实测。

| 组件 | 固定候选 |
| --- | --- |
| SDK / 目标框架 | .NET SDK 10.0.403，net10.0；对应运行时 10.0.14 |
| API | FastEndpoints 8.3.0 |
| OpenAPI | FastEndpoints.OpenApi 8.3.0；Microsoft.AspNetCore.OpenApi 10.0.14 |
| 校验 | FluentValidation 12.1.1 |
| ORM | Microsoft.EntityFrameworkCore 10.0.14；Microsoft.EntityFrameworkCore.Relational 10.0.14 |
| MySQL Provider / Driver | Oracle MySql.EntityFrameworkCore 10.0.12；MySql.Data 26.10.0 |
| 日志 | Serilog.AspNetCore 10.0.0；Serilog.Sinks.File 7.0.0；Serilog.Formatting.Compact 3.0.0 |
| 测试 | Microsoft.NET.Test.Sdk 18.11.0；MSTest.TestFramework 4.5.2；MSTest.TestAdapter 4.5.2 |
| API 测试宿主 | Microsoft.AspNetCore.Mvc.Testing 10.0.14，仅测试项目引用 |
| B 数据库 | 官方 mysql:8.4.6，记录实际镜像 digest/架构；不得静默换版本或第三方镜像 |

不安装 Pomelo、EF Design/迁移工具、SQLite、Dapper、MediatR、消息队列、认证或 UI 包。OpenAPI 只交付 JSON，不额外引入 Scalar/Swagger UI。显式直接依赖精确版本，传递依赖由首次 restore 生成锁文件后以 locked mode 核验，不使用浮动版本、preview、忽略包降级告警或强行跨主版本。

任何 SDK、直接依赖、Provider 或数据库版本更换，或发现元数据与 restore/build 不兼容，先回 PM 修订精确 Revision，不在任务执行中自行替换。首次锁定实际传递依赖、同版本 API 写法适配不构成版本变更，但必须记录。

当前只读环境记录为 Darwin arm64、PATH 无 dotnet。A 可在新建的 /private/tmp/arch-be008-sdk-<随机后缀>/ 私有目录准备 10.0.403 osx-arm64 官方 SDK，并用官方 SHA512 校验归档；记录下载 URL、哈希和实际版本。只通过任务变量 BE008_DOTNET 使用，不改全局 PATH、shell 配置、用户 SDK 或其他工程环境，不复用 FF-003 的可写工具链。

global.json 固定 sdk.version=10.0.403、rollForward=disable、allowPrerelease=false；缺少该 SDK 时失败，不自动使用其他已安装版本。以 BE008_TOOL_ROOT 指向上述新建的任务私有根，SDK 放入其 sdk/，DOTNET_CLI_HOME、NUGET_PACKAGES、NUGET_HTTP_CACHE_PATH 分别显式指向其 cli-home/、nuget-packages/、nuget-http-cache/，不写默认用户缓存或其他工程状态。NuGet.Config 清除继承的包源，只声明官方 https://api.nuget.org/v3/index.json；所有 restore 显式使用该文件。API 与测试项目各自保留精确 packages.lock.json，后续使用 locked mode。

## 5. 文件 allowlist 与工程形态

### 5.1 当前 PM 写入

PM 只写本 spec 及 007 状态/批准记录；主协调只同步根 PLAN pair 和 plans/README pair 的 007/008 行。当前不写下表任何软件文件。

### 5.2 A 获批后的实现面

| 路径 | 允许内容 |
| --- | --- |
| backend-dotnet/AIIS.Backend.Api.csproj、global.json、Directory.Packages.props、NuGet.Config、packages.lock.json、appsettings.json、.gitignore | 单 API 项目、固定 SDK/包、仅官方 nuget.org 源、非秘密配置默认、忽略自有 bin/obj/logs/TestResults/秘密 |
| backend-dotnet/Program.cs | 配置、日志、依赖、模块、错误映射、health/OpenAPI、启动；保持薄入口 |
| backend-dotnet/Common/Contracts/*.cs、Errors/*.cs、Time/*.cs、Modules/*.cs、Serialization/*.cs | 本切片必需的响应/错误、上海时间、静态模块装配和严格 DTO 序列化；不建通用业务框架 |
| backend-dotnet/Configuration/*.cs、Infrastructure/Persistence/*.cs、Infrastructure/Logging/*.cs | typed Options、唯一 scoped DbContext、MySQL 连接和 JSON Lines 装配 |
| backend-dotnet/app/Plan/ModuleManifest.cs、Endpoints/*.cs、Contracts/*.cs、Validators/*.cs、Services/*.cs、Domain/*.cs、Persistence/*.cs | 仅三接口、PlanEntity/映射、规则、事务和查询 |
| backend-dotnet/tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj、packages.lock.json、*.cs、Contracts/*.cs、Domain/*.cs、Persistence/*.cs、Fixtures/*.cs | 一个 MSTest 项目；合同、规则及 B MySQL 验证，无生产测试钩子/通用故障注入框架 |
| backend-dotnet/tests/fixtures/*.json、tests/infra/plans.sql、tests/infra/mysql.compose.yml、tests/scripts/run-mysql-tests.sh | 合成合同快照、test-only 单表 fixture、专属 MySQL 编排与显式 prepare/test/cleanup 子命令；A 只写和静态检查，B 才运行 |
| backend-dotnet/README.md、README.zh-CN.md、PLAN.md、PLAN.zh-CN.md、CODE_INDEX.md、plans/README.md、plans/README.zh-CN.md | 模块双语说明/索引、三接口使用、A/B 命令、候选版本/限制；唯一任务正文仍在根 008 bundle，不复制成第二份 spec |
| 根 README.md / README.zh-CN.md、CODE_INDEX.md | 仅增加 backend-dotnet 入口与准确“首期学习切片”说明，不改既有模块内容或宣称全量替换 |
| 本目录 tasks.md / checklist.md / evidence/ | 分别在真实批准后由 Development、developer_handoff 后由 fresh Verification 形成；evidence 仅实际脱敏产物 |
| 根 PLAN pair、plans/README pair | 主协调同步本 008 的真实阶段/证据/下一 gate，不改其他任务事实 |

API .csproj 位于 backend-dotnet 根，必须显式排除 tests/** 的 Compile/Content/None 项，防止默认递归 glob 把测试源码、配置和资源编进 API；测试项目只通过 ProjectReference 引用 API。不得把业务文件堆入 Program.cs，也不生成空 Performance/Monitor/MesIntegration 模块、通用 Repository/IUnitOfWork 或 Worker 工程。

backend-dotnet 内的 PLAN/catalog 可以索引同一根 008 bundle；不得另建同 ID 任务正文或在模块目录伪造新批准。新增关键源码按现有项目风格保留中文头部说明，结构变化仅更新上表允许的 CODE_INDEX。

### 5.3 排除

不修改 backend/、frontend-js/、automation-world/、field-flow/、根 AGENTS/ROADMAP、真实 env、根 Docker 文件和既有 migration。B 的运行数据/SDK/凭据在专属临时根，不进入 Git；不提交构建输出、镜像、客户数据或秘密。不创建更新/删除计划、执行计划、导入导出、用户、实绩、MES、PLC、CA 授权或 schema-maintenance API。

## 6. 创建 DTO 的精确合同

仅接受 Content-Type application/json 的单个平面对象。采用明确 camelCase、区分大小写；未知/重复属性、snake_case、嵌套代替标量、非法 Unicode、非有限数字拒绝。Python 普通 Plan Schema 仍接受字段名 alias 且可能忽略 extra，这是本切片明确的严格边界差异，不修 Python。

| JSON 字段 | 必填/省略默认 | 接受与数据库范围 |
| --- | --- | --- |
| coilNo | 必填 | string，原始长度 1–50；第 6.1 节卷号规则 |
| grade | 必填 | string，长度 1–20；不 trim、不新增“不得全空格”的业务规则 |
| spec | 必填 | string，长度 1–50；原样保存 |
| weight | 必填 | 非负 Decimal，DECIMAL(12,4)，最大 99999999.9999 |
| thickness | 必填 | 非负 Decimal，DECIMAL(10,3)，最大 9999999.999 |
| width | 必填 | 大于 0 的 Decimal，DECIMAL(10,2)，最大 99999999.99 |
| materialStatus | 省略为 special | string，长度 0–20；不擅自收窄为 enum |
| density | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| entryLength | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| uncoiler1Tension | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| exitTension | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| process1Tension | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| entryLoopTension | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| exitLoopTension | 省略为 0 | 非负 Decimal，DECIMAL(10,2) |
| entryUnitTension | 省略为 0 | 非负 Decimal，DECIMAL(12,4) |
| entryLoopUnitTension | 省略为 0 | 非负 Decimal，DECIMAL(12,4) |
| processUnitTension | 省略为 0 | 非负 Decimal，DECIMAL(12,4) |
| exitLoopUnitTension | 省略为 0 | 非负 Decimal，DECIMAL(12,4) |
| exitUnitTension | 省略为 0 | 非负 Decimal，DECIMAL(12,4) |
| priority | 省略为 5 | JSON integer，1–10，不接受 bool、字符串或小数 |
| remark | 省略或 null 为 null | string，长度 0–500，原样保存 |

除 remark 外所有字段显式 null 均拒绝，不能把缺失、null、0 和空串混为一类。Decimal 接受 JSON number 或可完整解析的十进制字符串，统一 InvariantCulture，不接受本地化千分位/小数分隔符，禁止 bool、空字符串、NaN/Infinity、溢出或精度损失。以数值检验 scale：超过列 scale 的非零小数拒绝，不让数据库静默舍入；仅多余尾零可接受。其余 DECIMAL(10,2)/(12,4) 上界与同型字段一致。

Decimal 字符串语法固定如下：允许首尾 ASCII 空格、Tab、CR、LF；移除这些首尾空白后，允许可选前导 + 或 -、以点为小数分隔符的十进制有效数和可选 e/E 指数，指数可带 + 或 - 且至少一位 ASCII 数字。有效数必须至少有一位数字，可为 12、12.、12.30 或 .30；字符串可有前导零。示例“ +001.2300e+1 ”可解析后再检验列精度；1e2 这种合法 JSON number 同样允许。空字符串、仅符号/点、内部空白、千分分组/逗号、货币符号、括号负数或 Unicode 数字字形均拒绝，不使用 CurrentCulture 或带 AllowThousands 的 NumberStyles.Number。

精度校验必须基于原始数字文本或可证明无损的规范化值；decimal.TryParse 成功不证明没有舍掉超过可表示精度的尾数，不能先经 double/decimal 静默舍入后再检查 scale。针对原始非零超 scale 位和过长有效数字保留拒绝用例。

字符串长度按 Unicode 标量字符数核对，避免把 C# UTF-16 code unit 数当作数据库/Python字符数；不接受无法存入 utf8mb4 的无效代理字符。首轮不改变输入显示值，日志不回显整份 DTO。

调用方不能提交 id、status、createdAt、updatedAt；它们属于未知属性，返回输入错误。所有省略默认由 DTO/Service 显式补齐，不能期待现表有数据库 DEFAULT。

### 6.1 卷号与重复语义

卷号不要求只含英文数字，不新增业务格式正则。与 Python 代表性规则一致：先对校验副本去除 Python strip 意义的首尾空白，结果不能为空，校验副本中不得含 U+0000–001F 或 U+007F；保存原始 coilNo，不修剪或改大小写。首尾空白的处理与控制字符检查顺序必须由对照用例覆盖，不直接把 FluentValidation.NotEmpty 或 C# Trim 当作完全等价。

顺序创建预查使用参数化的数据库 lower(trim(coil_no)) 语义，保留“可识别的大小写/首尾空格变体已存在则冲突”的行为。Python 输入 casefold 与 C#/.NET/数据库完整 Unicode 大小写折叠并非天然等价：首期只承诺已列 ASCII 代表例和数据库既有 collation 下的判定，不为此手写通用 Unicode casefold 表，也不拒绝所有非 ASCII 卷号来掩盖差异。

数据库最终唯一边界仍是既有 ix_plans_coil_no。并发只承诺相同原始卷号及该唯一键覆盖的竞争：两次同时创建应形成一条记录、一个成功、一个冲突。对于原始字符串不同但 trim/lower 后相同、且现有唯一键未覆盖的并发情况，本任务不承诺原子 canonical 唯一；不新增 GET_LOCK、锁框架、canonical 列/索引或表，不修 Python。该限制在 README、tasks/checklist 和最终交付中保持可见，不能宣称全场景 exactly-once。

## 7. 三条 API 与输出

| 方法/路径 | 行为 |
| --- | --- |
| POST /api/v1/plans | 使用第 6 节 DTO；事务提交确认后返回 HTTP 200 和完整 PlanOut |
| GET /api/v1/plans/{id} | id 为 1–2147483647 的整数；按 ID 查询，存在 HTTP 200，不存在 404；格式/范围非法 422 |
| GET /api/v1/plans | 第 7.1 节过滤/分页；HTTP 200，空结果不伪造数据 |

业务响应保留 code/message/data/timestamp；timestamp 是 Unix 毫秒响应生成时刻，不是业务时间字段，不机械转东八区。

PlanOut 包含第 6 节全部业务字段和 id、status、createdAt、updatedAt。id/priority 为 JSON number；status 新建固定 planned；remark 缺失时输出 null；Decimal 输出固定 scale 的 JSON string：weight/五个单位张力 4 位、thickness 3 位、width/density/entryLength/五个普通张力 2 位。创建结果和随后 GET 必须一致，禁止经 double 破坏精度。

createdAt/updatedAt 为 YYYY-MM-DDTHH:mm:ss+08:00，保留源 DATETIME(0) 秒精度；创建时两者相等。GET 不刷新 updatedAt。成功 message 固定 success，避免代码散落中文展示文案；当前 Python 创建 message 的“创建成功”不作为机器协议，属于已说明差异。

成功信封与列表 data 示例（示意省略完整 PlanOut，不允许实现时省略字段）：

~~~json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "pageSize": 20,
    "totalPages": 0
  },
  "timestamp": 1793116800000
}
~~~

### 7.1 列表合同

page 默认 1，pageSize 默认 20，分别要求正整数和 1–100；页码/offset 用检查过的算术，offset 超出 Int32 支持范围返回 422，不溢出后查询。页码超过实际页数返回空 items，保留真实 total、totalPages。

可选查询为 coilNo、grade、materialStatus、status，与 Python 实际列表路由一致；不添加未被路由使用的 priority/sort 参数。空字符串按未筛选处理；coilNo 使用参数化 LIKE 的包含模式，与现有 SQLAlchemy contains 的 %/_ 通配语义一致；其他三项按数据库 collation 等值过滤。未知 query key 忽略，不拼接 SQL 标识或任意排序表达式。

排序固定 created_at DESC、id DESC，后者是对同秒记录的明确稳定 tie-breaker；Python 当前仅按 created_at DESC，这是已说明改进。count 与列表顺序执行，不在同一个 DbContext 并发查询；本切片不承诺多次翻页期间对并发插入形成跨请求快照。

### 7.2 错误合同

错误统一为 code/message/data/errorCode/timestamp，data=null，message 使用稳定 errorCode；字段校验可附 errors 数组，每项只含 field 和稳定 rule key，不返回秘密、SQL或原始异常。未知路由/不支持方法不生成假业务成功。

| HTTP/code | errorCode | 精确触发 |
| --- | --- | --- |
| 422 | plan_invalid_request | JSON、字段类型/必填/null/未知/重复属性、存储精度、ID/分页边界错误 |
| 422 | plan_invalid_coil_no | 卷号校验副本为空或含禁止控制字符 |
| 409 | plan_coil_already_exists | 顺序 canonical 预查命中，或 MySQL 1062 且命名唯一键 ix_plans_coil_no 冲突 |
| 404 | plan_not_found | 合法 ID 不存在 |
| 503 | plan_database_unavailable | 连接失败/已知未提交的数据库不可用；不得返回成功 |
| 503 | plan_write_outcome_unknown | 已尝试提交但无法确认结果；不盲重试、不假报已回滚 |
| 500 | plan_internal_error | 非预期或不能归类的错误；细节只在脱敏日志 |

当前 Python 重复业务异常可为 HTTP 200 + code 400，404 可为 detail 形状，部分输入依赖 Pydantic/数据库默认行为；C# 首期使用本节统一错误与语义状态码，明确不是完整 wire/drop-in 等价。绑定失败必须收敛至本节，不能漏出 FastEndpoints 默认的另一种错误 JSON。

非 application/json 请求返回 415 与同一错误信封的 plan_invalid_request；未知路径404、已存在路径的不支持方法405按基础HTTP路由语义处理，不伪装成已经实现的业务动作。

## 8. 仅映射 plans 表

PlanEntity 显式映射 plans 和第 6 节 snake_case 列，不引入导航属性、Performance/User Entity 或其他表。id 映射 INT AUTO_INCREMENT 主键；status VARCHAR(20) NOT NULL；priority SMALLINT NOT NULL；remark VARCHAR(500) NULL；created_at/updated_at DATETIME(0) NOT NULL。其他列的类型、长度和 Decimal 精度按第 6 节及 d2 plans 片段逐项一致。

保留命名索引 ix_plans_coil_no UNIQUE(coil_no)、ix_plans_id、ix_plans_priority、ix_plans_status。表使用 InnoDB，fixture 固定 utf8mb4/utf8mb4_0900_ai_ci 作为本次测试条件；不宣称任意现库 collation 的行为已经验证。

重要：Python Model 的 default=func.now()、default=0/special/planned 是客户端表达式/默认，并不表示 d2 表已带 server DEFAULT。test-only plans.sql 不给业务列或时间列额外添加 DEFAULT、generated canonical 列、触发器、CHECK 或 FK；只保留源结构及测试数据库环境必需的 engine/charset/collation。

既有共享表的 schema 权威仍是 Alembic。C# 启动/注册/请求不执行 EnsureCreated、Migrate、DDL 或 seed；本任务不引入 EF Migrations。B fixture 是核对源表片段后的独立一次性测试材料，只能在第 11 节空且归属明确的测试库显式应用，不形成第二套现库迁移图。

## 9. Service、事务与时间

每个请求一个 scoped DbContext；不设单例，不在同实例并发操作，不跨请求缓存 Entity。列表/详情使用 AsNoTracking 或直接投影；Endpoint 不访问 SQL，Persistence 不提交事务，业务 Service 是 SaveChanges/Commit/Rollback 的唯一 owner。

创建按以下固定顺序：

1. Validator 完成形状/范围校验，Service 复核卷号业务规则。
2. 同一连接/业务事务中做 canonical 顺序预查；命中即返回 409。
3. 从该数据库连接查询一次 CURRENT_TIMESTAMP，已通过 B 前置检查确认数据库日历时间为上海时间；显式赋 created_at、updated_at 同一值，并补齐 DTO/Service 的所有客户端默认。
4. 添加 PlanEntity，SaveChanges，提交确认后构造完整 PlanOut。读取生成 ID/数值时不得丢失声明精度。
5. 已知失败回滚并释放上下文；仅命名 ix_plans_coil_no 的 1062 归冲突，其他异常不笼统当重复。提交不确定按第 7.2 节处理。

不靠 HasDefaultValueSql 省略现表非空时间列。公共 Time 边界把无时区 DATETIME 明确解释为上海业务日历并输出 +08:00，不按访问电脑时区猜测，也不在各模块 AddHours(8)。本切片没有外部业务时间写入、历史时间迁移或更新 API。

数据库运行参数在 B 的专属实例设置上海时间；应用需检查实际 CURRENT_TIMESTAMP/UTC_TIMESTAMP 关系与 session/server 时区，不由 API 启动硬改未知数据库时区。Python 旧 UTC mapping 与本表无混写；本任务不连接或迁移该域。

POST 不增加幂等请求表：相同卷号重复请求返回冲突，不宣称返回首次结果的幂等 API。若客户端在提交后丢失响应，需用只读查询核实同卷号/内容，不能自动新建第二条；真正的可靠投递/幂等回执属于后续接口任务。

## 10. 模块、配置、日志与无认证

只实现稳定 ID plan 的本地 ModuleManifest 与显式组合，列明三种 Endpoint、Service 和唯一 Entity。enabled=false 时三条路由从实际注册和 OpenAPI 同时消失；需要重启采用，不仅隐藏文档。配置/manifest/Entity 组合不打开数据库或产生 DDL/seed。重复模块 ID、依赖缺失和路由冲突启动失败，验证可用测试内的局部假 manifest，不增加虚假业务模块。

typed Options 明确：默认监听 http://127.0.0.1:18108；Database:ConnectionString 默认空、来自显式环境变量 Database__ConnectionString；Modules:Plan:Enabled 默认 true；BusinessTimeZone 固定 Asia/Shanghai；数据库命令超时 5 秒、连接超时 5 秒；日志目录默认本工程 logs。非法/缺失连接配置在启动校验失败，不回显连接串。测试可注入专属配置，不能扫描父目录/其他工程 .env。

appsettings.json 如为上述非秘密默认所需，可随 Configuration 文件交付，必须只含无秘密选项；.NET 不自动读取 .env，本任务不增加 dotenv 包。README 使用明确的进程环境设置，公开示例只用占位符。连接使用本任务非 root 的 INSERT/SELECT 账号。

基础 GET /health 仅表示进程存活，不检查/写入数据库，不宣称业务就绪；GET /openapi/v1.json 公开实际文档，不生成 JWT 安全方案或交互 UI。除三条业务 API 和这两个基础入口外不添加其他功能入口。

日志使用固定 Serilog 组件输出紧凑 JSON Lines stdout 和持久滚动文件，单文件上限 10 MiB、保留 5 个文件；正常关闭 flush/dispose。记录稳定事件名、requestId、module=plan、结果、耗时、错误 key、创建成功后的 planId；保留启动/关闭、校验失败、业务冲突、事务失败/未知结果。读取日志按级别控制，不记录原始正文、密码、完整连接串、用户假身份或 SQL 参数敏感值。

首期无登录、JWT、RBAC、用户表、假 admin 或额外 API key；也不把已有 Python 鉴权关掉。只在本机/专属测试环境使用，不监听 0.0.0.0，不改既有前端/MES/FF 地址。真实外部接入和部署不在 A/B 内。

## 11. B 阶段专属 MySQL 资源与 DDL

### 11.1 可一次审阅的资源清单

| 资源 | 唯一范围 |
| --- | --- |
| Docker Compose project | aiis-arch-be008 |
| 官方镜像 | mysql:8.4.6；本轮实际 digest 与架构写入 tasks/checklist，不替换已有项目镜像 |
| container / network / volume | aiis-arch-be008-mysql / aiis-arch-be008-net / aiis-arch-be008-mysql-data |
| 归属标识 | 三类资源均带 task=ARCH-BE-008 及本轮 runId 标签，校验任务归属和本轮清单后才操作 |
| MySQL 发布地址 | 仅 127.0.0.1:13388 -> container:3306，不暴露 LAN |
| 数据库 | 仅 arch_be008_plan，空且本轮创建；禁止 aiis_ics_architecture、现有 *_test 或其他项目库 |
| 账号 | 本轮临时 root/fixture 管理凭据；arch_be008_app 仅本库 INSERT/SELECT，不作账户系统用户 |
| API 地址 | Development 手工 smoke 最多一个 127.0.0.1:18108；测试 HTTP 宿主优先 in-process |
| 临时根 | /private/tmp/arch-be008-run-<随机后缀>/；私有凭据/环境、SDK或包缓存路径、日志和运行清单分开记录 |

所有名字/端口均是未来候选资源，不表示当前已存在或可占用。运行前发现同名容器/卷/网络、端口占用、数据库非空或归属不一致立即停止；不抢占、不杀未知进程、不自动换端口或改连旧库。确需变更资源合同回 PM 修订。

### 11.2 B 可批准的具体操作

B 的明确批准仅覆盖：拉取上述官方镜像；用 tests/infra/mysql.compose.yml 新建这组 MySQL 容器/网络/卷和空 arch_be008_plan；设置本实例上海数据库时区、utf8mb4 和固定 collation；生成本轮强随机凭据；显式应用唯一 plans.sql；仅本库创建/授权 arch_be008_app；对合成计划执行 INSERT/SELECT 和必要的测试 fixture 安排/清理；启动/停止本任务 API；对本任务 MySQL 做一次明确断线/恢复场景；按第 15 节释放确认归属的资源。

允许 Docker pull/up、限定 container 的 stop/start 和限定 project 的 down/卷网络清理，不允许 Docker build、全局 prune、其他项目 up/down 或扫描真实业务配置。若 Docker 未运行，记录 blocker，不擅自安装/启动/重配宿主 Docker。

生成凭据的文件只保存在新临时根，权限限制为本用户，不打印凭据或将其放进命令历史/仓库/完整 docker inspect 输出。公开 Compose 不含固定可用口令；使用显式 --env-file 或安全的本轮配置来源，不读取根 .env。仅过滤检查所需 labels/ports，不输出容器完整 Environment。

### 11.3 Fixture 防误用与每轮证据

schema 应用器必须显式接受本轮专属连接与 run manifest，先核对 loopback/13388、数据库精确名、任务资源标签、服务器版本和空 schema；任一不匹配拒绝执行。不得允许任意 DSN、自动 DROP 非空库或使用 backend/tests 的共享破坏性 conftest。

plans.sql 从第 3 节 d2 的 plans 片段人工核对生成；测试辅助应对列名/类型/可空/default/四个索引形成结构断言，且确认只有 plans 一张业务表。原迁移中其他 41 表不进入 fixture，fixture不写 alembic_version，不调用整个 Python migration 图。

test-only 管理连接可为明确测试用例安排合成行及清理其自有数据；API 账号不能 DELETE/DDL。不得用应用启动 seed 造数据。每轮至少记录：候选源码/锁文件哈希、SDK/包版本、镜像 digest/架构、runId/资源名、脱敏连接目标、表结构摘要、请求与响应关键断言、独立 MySQL SELECT 回读、失败/并发结果、退出码及进程/资源收尾。

Development 和新 fresh-context Verification 分别取得自己的真实证据；需要新空实例时由主协调核实并释放上一轮自有资源后再准备，不能把上一轮数据库内容或 Development 结论当作 fresh QA 结果。Verification 不自行回收资源，按角色记录后交主协调收尾。

## 12. Development 顺序与命令

本节为已获批 r1 的 Development 执行顺序；由命名 Development 创建 tasks.md 并实际执行，PM 不代执行或预填结果。

1. 核对精确批准范围/A/B、来源哈希、dirty allowlist 与 SDK 官方校验值，记录 tools/env，不触达 Python 的真实配置。
2. 创建最小 API/测试项目、固定版本和锁文件，确保测试文件不被 API glob 包含。
3. 实现模块组合、配置/JSON Lines/响应错误/上海时间；先完成纯规则、DTO、序列化和 disabled 路由测试。
4. 实现 PlanEntity/显式映射、查询与 Service 事务、三 Endpoint 和 OpenAPI；不添加其他模块或 DDL。
5. A 自检通过后，如 B 已明确获批则创建本任务资源、应用 fixture 并完成第 14 节真实 MySQL 验证；未获批或失败则如实保持未完成。
6. 更新双语说明、索引和 CODE_INDEX，形成精确 Development handoff：批准 Revision、修改清单/候选哈希、命令/退出码、A/B 结果、已知差异和资源清单。其后交新 fresh Verification。

所有 dotnet 命令 cwd 必须为 backend-dotnet，让自身 global.json 生效；BE008_TOOL_ROOT 是已按第 4 节建立并核验归属的新私有工具链根，BE008_DOTNET 是其 sdk/ 下可执行文件的绝对路径，不更改系统 PATH。准备阶段先创建权限为 0700 的工具链根及缓存子目录，再执行以下命令；实际命令/日志由执行角色逐条记录。

~~~bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet
export DOTNET_CLI_HOME="$BE008_TOOL_ROOT/cli-home"
export NUGET_PACKAGES="$BE008_TOOL_ROOT/nuget-packages"
export NUGET_HTTP_CACHE_PATH="$BE008_TOOL_ROOT/nuget-http-cache"
"$BE008_DOTNET" --version
"$BE008_DOTNET" restore AIIS.Backend.Api.csproj --configfile NuGet.Config --use-lock-file
"$BE008_DOTNET" restore tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --configfile NuGet.Config --use-lock-file
"$BE008_DOTNET" restore AIIS.Backend.Api.csproj --configfile NuGet.Config --locked-mode
"$BE008_DOTNET" restore tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --configfile NuGet.Config --locked-mode
"$BE008_DOTNET" build AIIS.Backend.Api.csproj --no-restore
"$BE008_DOTNET" test tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --no-restore --filter "TestCategory!=MySQL"
~~~

B 的脚本使用显式 prepare/test/cleanup 子命令和 --run-root，裸入口只显示帮助，不启动 Docker/读默认凭据。prepare 前完成第 11 节检查；test 最终调用同一固定 SDK 的 MSTest MySQL category 并收集 SELECT 回读。cleanup 只有在主协调核实归属与证据持久化后执行，不通过 trap 无条件删资源。任何 B 命令都不能在只批准 A 时执行。

## 13. 编号需求

| ID | 需求 | 位置 |
| --- | --- | --- |
| R01 | 当前只落文档；007批准与008独立draft/A/B批准清楚分开 | 1、2、16 |
| R02 | 根 backend-dotnet 独立单API+测试项目，固定稳定候选和锁文件 | 4、5 |
| R03 | 源码层分明，模块真实启停、无隐式连接/DDL/seed | 5、8、10 |
| R04 | 21字段创建DTO的必填、默认、null、长度和Decimal合同固定 | 6 |
| R05 | 保留原始卷号、代表性canonical预查，唯一竞争及已知并发限制明确 | 6.1、9 |
| R06 | 三路由、ID、筛选、稳定分页、空态和完整PlanOut真实工作 | 7 |
| R07 | 公共响应/错误、Decimal字符串、上海时间和Python差异透明 | 7、9 |
| R08 | 仅映射plans源结构，所有client默认显式提供，Alembic权威不变 | 3、8 |
| R09 | scoped DbContext串行使用、Service提交、失败/提交未知处理 | 9 |
| R10 | typed配置、本机绑定、JSON Lines持久日志、秘密保护、无认证 | 10 |
| R11 | B专属MySQL/Docker/fixture资源与权限精确、拒绝真实/未知环境 | 2、11 |
| R12 | 合同/规则与真实MySQL回读、失败、并发/断线证据分层 | 12、14 |
| R13 | 顺序Dev、自检handoff、新fresh QA、真实批准与资源收尾 | 12、15、16 |

## 14. 验收与 fresh Verification 矩阵

独立 Verification 读取已批准008、Development tasks、精确候选/锁文件、diff、A/B批准记录与命令结果；使用不继承 Development 推理的 fresh context。下面都是未来验收，当前没有通过结果。

| AC | 必需检查/预期 | 映射/阶段 |
| --- | --- | --- |
| AC01 | PM文档状态、精确批准及allowlist合法；B未批准不运行，A通过不能冒充完整完成 | R01、R11；当前/A/B |
| AC02 | 固定SDK及全部直接依赖restore/lock/build通过，无preview/浮动/替代Provider；global.json禁止roll-forward，CLI/NuGet缓存归任务私有根且来源明确；API不包含tests源码/资源 | R02；A |
| AC03 | Plan enabled时只有3业务路由；disabled后真实404且OpenAPI不含Plan；health仅liveness，无认证/维护/额外模块 | R03、R10；A |
| AC04 | 所有必填逐个省略、非remark显式null、错误类型、未知/重复属性、snake_case、非法Unicode返回422且无写库 | R04、R07；A/B |
| AC05 | 最小合法创建补齐全部默认，非零可选字段完整往返；输出包含25字段，随后GET相同，SELECT回读一条 | R04、R06；B |
| AC06 | Decimal边界/多余尾零可接受，超上界/非零超scale/NaN/Infinity/bool拒绝；string固定scale，DB值无double损失 | R04、R07、R08；A/B |
| AC07 | 空白卷号/内部控制拒绝；原始首尾空格/大小写显示不改；ASCII变体顺序重复409，Unicode差异如实列明 | R05；A/B |
| AC08 | 相同原始卷号并发POST：1成功+1冲突+SELECT仅1条；named unique错误精确识别并回滚，不宣称canonical跨字面原子唯一 | R05、R09；B |
| AC09 | GET合法ID存在200、不存在404；0/负数/非整数/溢出422；未实现更新/删除/XLSX不返回假成功 | R06、R07；A/B |
| AC10 | 空列表形状正确；页长/页数边界、超末页和同秒id降序稳定；四筛选真实生效，不增加priority/sort功能 | R06；B |
| AC11 | 包含引号/SQL片段的查询仍参数化；%/_按已声明LIKE语义；无注入、DDL或越表效果 | R06、R08；B |
| AC12 | fixture结构对上源plans：25列/原类型/nullable/无业务server defaults/四索引；只有plans，无Performance/User/alembic/EF历史表 | R08、R11；A/B |
| AC13 | 创建两个时间来自同一次DB CURRENT_TIMESTAMP，DATETIME秒精度、输出+08:00；读不更新时间；不同进程TZ仍按上海 | R07、R08、R09；A/B |
| AC14 | 利用实际重复唯一键失败及已拒绝输入核对失败请求未新增脏行、原记录不变、上下文可释放；不为单INSERT切片添加第二业务动作、生产failpoint或故障注入框架 | R09；B |
| AC15 | 专属MySQL明确断线时请求503、无假成功/泄露，恢复后继续真实创建/查询；随后重启本任务API，原计划可读回，启动前后无新行/DDL | R09、R11；B |
| AC16 | 使用INSERT/SELECT应用账号运行；正常启动/请求前后schema和行数无隐式DDL/seed；配置错误启动失败且不回显连接串 | R03、R10、R11；A/B |
| AC17 | JSON Lines stdout/文件均可解析、请求ID关联、错误/成功planId可追踪；轮转和flush、秘密脱敏检查通过 | R10；A/B |
| AC18 | README pair/索引/CODE_INDEX准确，Python差异/限制和所有退出码保留；候选与实际运行入口一致 | R12、R13；A/B |
| AC19 | 新fresh Verification拥有独立证据，未替代Owner最终验收；资源清单/归属/保留或清理结果真实，无任务外资源操作 | R11、R12、R13；B/收尾 |

完整切片通过要求 A+B 必需项全部通过；只能执行 A、SDK/网络/容器不可用、B未获授权、真实MySQL失败或关键证据缺失时，不得写 qa_passed/完整闭环通过。不得以 EF InMemory、SQLite、Mock API 或单纯编译代替 B。

范围限定的 Python 对照台账至少包括：相同业务字段/默认、既有表类型；明确差异为无认证、严格camelCase/extra/null/存储边界及priority类型校验、统一错误状态/信封、成功message、上海offset时间和id稳定排序；canonical非ASCII/跨字面并发限制保留。首期不增加sampleId、receipt/outbox表、通用幂等框架或提交断包代理；提交结果未知保留明确处理边界，不声称已经实证真实COMMIT ACK丢失。未来接入既有前端/真实业务库需另任务关闭这些差异。

## 15. 风险、回退与资源收尾

本次 PM 阶段不创建运行资源；主协调的临时文档审计目录不作为唯一持久证据。未来 A/B 的所有临时目录、SDK、缓存、端口、PID、容器/网络/卷和数据必须在 tasks handoff 列明归属、用途、证据依赖及清理触发。

| 风险 | 控制与回退 |
| --- | --- |
| 候选包元数据可兼容但实际构建/Provider行为失败 | 保留真实失败，回 PM 改版本，不换生态逃避；Python继续正式交付 |
| 把client defaults误当server DEFAULT | fixture对照d2；显式补齐；不改现库/fixture默认掩盖问题 |
| canonical并发缺口或Unicode折叠不同 | 不扩大保证、不增加锁/索引；独立业务整改后再评估生产 |
| 测试连到真实库或复用旧资源 | 固定loopback/资源标签/数据库名/空schema校验，任一异常拒绝；不扫真实env |
| 首期无认证被误当可替换已登录前端 | 仅本机学习和专属测试，保持Python认证/入口与数据不动 |
| 提交结果未知被当失败自动再写 | 503明确结果未知、先只读核实，不抹掉可能提交的数据 |

软件回退仅停止本任务进程并弃用候选，不删除或重置 Python 业务数据。A/B 完成后，主协调先持久保存必要脱敏结果与候选哈希，再核对归属/运行与证据依赖，按 B 批准仅释放本任务资源：停止/清理专属API和MySQL、卷/网络、临时凭据及不再依赖的SDK/缓存。不得全局prune或处理其他项目资源。

需要保留以供 QA/后续任务使用的资源记录路径、原因和清理时点；Verification只核对并记录，主协调实施回收。未获B授权时不运行cleanup去“帮忙清理”任何同名资源。非秘密必要证据进入 tasks/checklist及真实evidence，不能仅留在会消失的/private/tmp。

## 16. 审批页与角色 handoff

### 16.1 当前真实记录

| 日期 | 事件 | 状态 |
| --- | --- | --- |
| 2026-10-28 | Human Owner批准007r1设计，要求首期MySQL完整切片、根backend-dotnet、无登录；明确实施spec出来后再批准Dev | 只授权PM形成008草案，不是008r1/A/B批准 |
| 2026-10-28 | 命名pm形成本008r1 | draft；无tasks/checklist/工程、安装或运行证据 |
| 2026-10-28 | Human Owner 明确批准：“批准 ARCH-BE-008 r1 的 A+B，进入 Dev。按 spec 创建根目录 backend-dotnet，完成计划创建、详情和分页列表，并用专属可丢弃 MySQL 验证，首期不做登录认证。开发完成后交独立 Verification。” | owner_approved；精确 r1 的 A+B 范围与第 11 节专属操作获批，交命名 Development；不是 QA 或最终验收 |

获批草案 SHA256 为 dbee5432e3c610fb3342118f15b9f95225a9ae31739a19a7a205c525a8373b5c。本轮只记录真实批准、当前状态与 handoff，r1 的 API、版本、资源、范围、R/AC 实质不变，不升 r2。R01 的 draft/成文阶段措辞与第 17 节原检查结果保留为历史事实，不据此撤销本次明确批准或推断软件已完成。

本任务选定 agent_type=pm；角色配置来源 [.codex/agents/pm.toml](../../.codex/agents/pm.toml)，不把配置model/effort当作独立运行遥测。主协调只同步机械索引，不代替PM/Development/Verification事实owner。

### 16.2 可审阅的一次批准口径

Human Owner 可明确选择：

- “批准 ARCH-BE-008 r1 的 A+B：允许第5节源码/依赖/SDK准备，以及第11节列明的本机专属 mysql:8.4.6 容器、网络、卷、空库、test-only plans fixture DDL/合成数据测试、专属API和确认归属后的清理；不涉及任何共享/真实库、MES/PLC、生产或部署。”
- 或“只批准 ARCH-BE-008 r1 的 A，B等待另行批准。”此时后续必须诚实保留B未执行和完整闭环未完成。

上述两项保留为原审阅选项；已发生的明确决定是第 16.1 节的 r1 A+B 批准。不得从沉默、007批准或泛泛“继续”推导B授权。范围、版本、资源、API合同、验收或风险实质变化均返回PM新Revision并重新批准。

精确批准已发生，交命名 Development（agent_type=development，任务名 csharp_backend_dev，由主协调实际启动）按本 spec 创建 tasks、实施和自检；真实 developer_handoff 后新 fresh Verification 创建 checklist，最终由 Human Owner 接受。这里不声称 Development 已启动或完成；文档成文检查不是独立 QA，A/B 技术验证也不是现场/生产证明。

适用skill：本PM任务用aiis、project-governance与backend-arch技术参考；后续Dev使用backend-arch、code-document-indexer、i18n-workflow（API稳定message/error key及任何新增展示文案）。B新增Compose/环境运行时还需docker-project-ops与docker-expert，测试辅助脚本按独立工程工具边界审阅，不使用backend/scripts环境。包装、前端、PLC和其他runtime skill不因本任务自动进入范围。

## 17. PM 成文检查与官方依据

### 17.1 检查边界

以下为 2026-10-28 首稿 draft 阶段的 PM/主协调成文检查，保留原结果；其后真实 A+B 批准见第 16.1 节。这些检查不是 Development 自检、独立 Verification 或最终验收。

| 检查与边界 | 真实结果 |
| --- | --- |
| PM：python3 标准库内联文本检查；仅读取两个 spec、引用路径与源文件 | 退出 0；007 为 owner_approved/r1，008 为 draft/r1；必需元数据、章节连续、R/AC 唯一且引用有效、围栏闭合、无尾空白；两 spec 合计 39 个本地 Markdown 链接存在，008 的 8 个来源 SHA256 与当前文件匹配 |
| PM：ast.parse 读取 PlanBase 和 Plan 类，不导入或启动应用 | 退出 0；PlanBase 的 21 个输入字段按 camelCase 与第 6 节逐项同序，Plan 的 25 个 mapped_column 与单表切片边界吻合 |
| 主协调：007 与用户批准的原始 r1 候选 SHA256 efa08166cf32d29203472bf530000951b039f652498fb990edf6daf68ade6f73 比较 | 第 1–16 节、第 18 节逐字节不变；只更新 Status、Handoff 与第 17 节真实审批/当前阶段记录，无实质设计或 AC 改写 |
| 主协调：四个根索引与本次开始前窄范围字节快照比较 | 每份仅更新 007 一行并新增 008 一行；从前后版本去除两任务对应行后逐字节一致，既有并行索引内容全保留 |
| PM/主协调：下列限定路径 git diff --check；未跟踪 spec 另作文本空白检查 | 退出 0；未创建 backend-dotnet 或两任务的 tasks.md/checklist.md |
| 主协调：下列全库治理检查前后增量比较 | 初查因英文 007 索引缺少 checker 要求的 pending 表述出现 4 条新诊断，已只修订该任务行的真实待办措辞；复查与修改前均退出 1、各 320 行诊断，内容多重集一致，最终新增诊断 0；全库治理未通过 |

PM 内联辅助检查曾因 Markdown 编号匹配规则和 AST 类名假设不符而退出 1；修正辅助检查后重跑退出 0。这些是成文检查脚本的修正记录，不是业务运行或 QA 结论。

~~~bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch
git diff --check -- plans/ARCH-BE-007-csharp-backend-architecture/spec.md plans/ARCH-BE-008-csharp-backend-plan-slice/spec.md PLAN.md PLAN.zh-CN.md plans/README.md plans/README.zh-CN.md
bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch
~~~

文本检查以第 3 节的文件路径/SHA 表及本 spec 的 R01–R13、AC01–AC19 为输入；链接相对各自 spec 解析，只读取存在性。索引保全检查以任务行剔除后的字节比较为准，治理增量以诊断行多重集比较，不能用单独退出码或 grep 数量代替结果。

上述 draft 成文检查时未创建 backend-dotnet，未安装 SDK、restore/build、启动 Docker/API/MySQL 或执行 DDL/软件测试，B 资源名/端口和版本表当时为待批准候选。其后 Human Owner 已明确批准 008 r1 的 A+B，实际执行结果由 Development 记录；fresh Verification 与 Owner 最终验收仍待真实发生。

### 17.2 官方版本与技术来源

以下由主协调于2026-10-28核对，当前仅页面/依赖元数据证据：

1. [.NET 10官方下载](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)：固定SDK10.0.403/osx-arm64及官方SHA512获取入口。
2. [FastEndpoints](https://www.nuget.org/packages/FastEndpoints)、[OpenApi](https://www.nuget.org/packages/FastEndpoints.OpenApi)、[FluentValidation](https://www.nuget.org/packages/FluentValidation)、[Microsoft OpenAPI](https://www.nuget.org/packages/Microsoft.AspNetCore.OpenApi)：候选版本及依赖元数据。
3. [EF Core](https://www.nuget.org/packages/Microsoft.EntityFrameworkCore)、[Relational](https://www.nuget.org/packages/Microsoft.EntityFrameworkCore.Relational)、[Oracle Provider](https://www.nuget.org/packages/MySql.EntityFrameworkCore)、[MySql.Data](https://www.nuget.org/packages/MySql.Data)：net10候选依赖，不混Pomelo。
4. [Test SDK](https://www.nuget.org/packages/Microsoft.NET.Test.Sdk)、[MSTest Framework](https://www.nuget.org/packages/MSTest.TestFramework)、[MSTest Adapter](https://www.nuget.org/packages/MSTest.TestAdapter)、[MVC Testing](https://www.nuget.org/packages/Microsoft.AspNetCore.Mvc.Testing/10.0.14)：仅测试项目用途。
5. [Serilog ASP.NET Core](https://www.nuget.org/packages/Serilog.AspNetCore)、[File Sink](https://www.nuget.org/packages/Serilog.Sinks.File)、[Compact JSON](https://www.nuget.org/packages/Serilog.Formatting.Compact)：固定JSON Lines方案。
6. [FastEndpoints校验](https://fast-endpoints.com/docs/validation)、[OpenAPI文档](https://fast-endpoints.com/docs/openapi-documents)、[EF DbContext](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/)：组件职责及生命周期参考。

依赖元数据不证明实际组合已构建或MySQL行为正确；只有按本spec后续真实执行的结果才能关闭相应验收项。
