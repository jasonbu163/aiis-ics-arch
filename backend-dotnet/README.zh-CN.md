# C# Plan 首期学习切片

English：[README.md](README.md)。范围权威：[ARCH-BE-008 r1](../plans/ARCH-BE-008-csharp-backend-plan-slice/spec.md)；实际实施与证据：[tasks](../plans/ARCH-BE-008-csharp-backend-plan-slice/tasks.md)。

本工程是独立 ASP.NET Core API，经 EF Core 直接写 MySQL，首期只做三个 Plan 操作、无登录。Python 继续既有交付；这不表示已有鉴权前后端可切换，也不授权共享/真实数据库、部署、MES 或 PLC。

## 固定工具链

SDK **10.0.403** / net10.0 / runtime **10.0.14**；FastEndpoints/OpenApi8.3.0、FluentValidation12.1.1、EF Core/Relational10.0.14、Oracle MySql.EntityFrameworkCore10.0.12 / MySql.Data26.10.0、Serilog.AspNetCore10.0.0 / File7.0.0 / Compact3.0.0。测试使用 Test SDK18.11.0、MSTest4.5.2、MVC Testing10.0.14。精确直接版本归 [Directory.Packages.props](Directory.Packages.props)，两个项目分别保留锁文件；global.json 禁止 roll-forward/preview，NuGet.Config 清除继承源、仅官方 nuget.org。

新建私有 `/private/tmp/arch-be008-sdk-<随机后缀>/`，SDK 放 sdk/，CLI 与 NuGet 缓存分别放 cli-home/、nuget-packages/、nuget-http-cache/，不复用其他任务可写工具链、不改全局 PATH 或用户 SDK。获批 macOS arm64 [官方 SDK 归档](https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.403/dotnet-sdk-10.0.403-osx-arm64.tar.gz) 解压前先用 [官方 metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json) SHA512 核验；实际哈希/下载命令归根任务。

所有项目命令从本目录运行：

```bash
cd /path/to/aiis-ics-arch/backend-dotnet
export BE008_TOOL_ROOT=/private/tmp/arch-be008-sdk-<nonce>
export BE008_DOTNET="$BE008_TOOL_ROOT/sdk/dotnet"
export DOTNET_CLI_HOME="$BE008_TOOL_ROOT/cli-home"
export NUGET_PACKAGES="$BE008_TOOL_ROOT/nuget-packages"
export NUGET_HTTP_CACHE_PATH="$BE008_TOOL_ROOT/nuget-http-cache"
export DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_CLI_TELEMETRY_OPTOUT=1
"$BE008_DOTNET" --version
"$BE008_DOTNET" restore AIIS.Backend.Api.csproj --configfile NuGet.Config --locked-mode
"$BE008_DOTNET" restore tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --configfile NuGet.Config --locked-mode
"$BE008_DOTNET" build AIIS.Backend.Api.csproj --no-restore
"$BE008_DOTNET" test tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --no-restore --filter 'TestCategory!=MySQL'
```

首次获批 restore 使用 `--use-lock-file`，其后 locked-mode。根 API csproj 明确排除 tests/** 的 Compile/Content/None；测试包只由测试工程引用。

## 显式启动与配置

```bash
export Database__ConnectionString='Server=127.0.0.1;Port=<approved-port>;Database=<approved-database>;User ID=<insert-select-user>;Password=<private-password>'
"$BE008_DOTNET" run --project AIIS.Backend.Api.csproj --no-build
```

上面只是占位示例，不是可用凭据。.NET 不自动读 .env；只给当前进程设置明确环境，不能复制其他项目真实配置。连接默认空且启动校验失败；连接和命令超时固定5秒。只绑定 loopback HTTP，默认 `http://127.0.0.1:18108`，BusinessTimeZone 固定 Asia/Shanghai。B 的专属数据库 server/session 使用 +08:00，创建时检查实际日历偏移与时区，不由应用修改未知数据库配置。

`Modules__Plan__Enabled=false` 重启后从实际注册和 OpenAPI 同时移除三个接口。静态 manifest 拒绝重复 ID、缺依赖、路由冲突；注册不连接数据库。FastEndpoints 同进程多宿主存在注册缓存，disabled 测试使用真实独立进程，符合“重启采用”合同。`/health` 仅进程存活，`/openapi/v1.json` 仅 JSON 文档、无 JWT scheme/交互 UI；除此与三条业务 API 无其他入口。

日志 stdout 与 `logs/backend-*.jsonl` 均为紧凑 JSON Lines，10MiB 轮转、保留5文件，host关闭处置并flush。LoggingOptions__Directory 可指定日志目录。稳定事件保留 requestId、校验/事务/提交结果与成功 planId；不记录正文、SQL参数、口令或连接串。正常读取不制造日志噪声，失败仍记录。

## 三条 API 与合同

| 方法 | 路径 | 行为 |
| --- | --- | --- |
| POST | `/api/v1/plans` | 提交确认后 HTTP200 和完整 PlanOut |
| GET | `/api/v1/plans/{id}` | 正Int32 ID；存在200、不存在404、非法422 |
| GET | `/api/v1/plans` | page默认1，pageSize默认20、范围1–100；四过滤参数 |

最小创建输入：

```json
{"coilNo":"EXAMPLE-001","grade":"G","spec":"S","weight":"1.2300","thickness":"0.123","width":"10.00"}
```

21输入字段及默认/长度/精度详见[批准字段表](../plans/ARCH-BE-008-csharp-backend-plan-slice/spec.md#6-创建-dto-的精确合同)。只收区分大小写的 camelCase 平面JSON；未知/重复属性、snake_case、错误类型和非法Unicode均422，仅 remark 可null。Decimal接受Invariant数字或字符串/指数语法，先按原始文本无损检查非零超scale位，多余尾零允许；优先级只收整数token。字符串长度按Unicode标量；卷号原样保存，Python strip仅作用于校验副本。

成功壳 code/message/data/timestamp，message固定success。PlanOut25字段；Decimal为固定4/3/2位字符串；DB DATETIME(0)按上海日历输出 `YYYY-MM-DDTHH:mm:ss+08:00`，读取不更新updatedAt；响应timestamp是Unix毫秒。列表data为items/total/page/pageSize/totalPages；固定created_at DESC,id DESC，空页保留真实总数，offset超Int32为422。coilNo参数化LIKE包含，保留%/_通配语义；grade/materialStatus/status按数据库collation等值；空串不筛选，未知query（含priority/sort）忽略。

错误壳 code/message/data=null/errorCode/timestamp，可附仅field/rule的errors：422 plan_invalid_request / plan_invalid_coil_no；409 plan_coil_already_exists；404 plan_not_found；503 plan_database_unavailable / plan_write_outcome_unknown；500 plan_internal_error。非application/json为415与plan_invalid_request；未知路径/不支持方法保持基础404/405，不实现更新/删除/XLSX/维护/鉴权入口。

## 持久化与明确差异

每请求一个scoped DbContext，只映射plans25列和四命名索引；Service唯一拥有SaveChanges/commit/rollback。创建依次做参数化canonical预查、同连接一次DB CURRENT_TIMESTAMP、显式补齐默认与相同时间、INSERT并确认commit。不执行EnsureCreated/Migrate/DDL/seed；既有schema权威仍Alembic，[plans.sql](tests/infra/plans.sql)仅专属空测试库的显式fixture。

相同原始卷号并发由ix_plans_coil_no保证一个成功/一个冲突；顺序ASCII大小写/首尾空格变体由DB lower(trim(...))预查冲突。非ASCII casefold/collation只限固定测试条件，不承诺所有Unicode等价；原始字面不同、canonical相同且原unique未覆盖的并发**不保证原子唯一**。不新增canonical列/索引、advisory lock、表或exactly-once宣称；跨请求翻页也不是快照。

与Python的明确差异：无认证；严格camelCase/extra/null/type/存储边界；HTTP语义状态与统一错误；success文案；上海offset；同秒ID稳定排序。Python鉴权、schema与旧UTC域不改；不是wire/drop-in等价替换。

真实COMMIT ACK丢失没有模拟或实证。尝试提交但无法确认时503 plan_write_outcome_unknown，不盲重试、不承诺回滚；客户端丢响应后先按卷号和内容只读核实。可靠幂等/回执属于后续任务。

## 专属可丢弃 MySQL B

只允许已明确批准的资源：project aiis-arch-be008、container aiis-arch-be008-mysql、network aiis-arch-be008-net、volume aiis-arch-be008-mysql-data、官方mysql:8.4.6、127.0.0.1:13388、库arch_be008_plan。三类资源均带task/runId；未知同名资源/端口占用立即停止，不换名/端口/旧库。

```bash
# 先具备明确B批准，以及上方固定私有SDK环境。
BE008_RUN_ROOT=$(mktemp -d /private/tmp/arch-be008-run-XXXXXXXX)
chmod 700 "$BE008_RUN_ROOT"
tests/scripts/run-mysql-tests.sh prepare --run-root "$BE008_RUN_ROOT"
tests/scripts/run-mysql-tests.sh test --run-root "$BE008_RUN_ROOT"
```

裸脚本仅帮助。prepare要求新空owned0700目录，生成0600随机凭据，核对固定资源、版本、空schema、时区后，仅应用plans fixture并授app INSERT/SELECT；独立fixture账号仅用于本库合成测试安排，不读根env。test再核对manifest/labels，执行真实MySQL category并保留独立SELECT；测试含明确stop/start恢复，不用全局prune/build或他项目。

证据持久化后，由主协调核对归属及API/PID/端口依赖，带 `BE008_COORDINATOR_CLEANUP_CONFIRMED=<manifest-runId>` 显式运行cleanup，验证三资源消失。Verification只核对记录，交协调回收；fresh QA另起新空实例。SDK/缓存/日志/秘密目录逐一列明用途与后续依赖，无依赖后再回收。实际失败历史、资源和handoff归根tasks；源码/构建/测试不代表QA、Owner最终验收或生产就绪。
