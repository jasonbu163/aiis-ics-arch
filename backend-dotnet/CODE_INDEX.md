# C# Backend Source Index

Topology only; [README](README.md) explains runtime contracts, [root task](../plans/ARCH-BE-008-csharp-backend-plan-slice/tasks.md) owns evidence.

## Program.cs

- [Program.cs](Program.cs) — 薄入口：配置/日志/静态模块/唯一 scoped Context；启动不连接或改变数据库。

## Configuration

- [Configuration/BackendOptions.cs](Configuration/BackendOptions.cs) — typed 配置只从显式配置源读取；连接错误不包含原始字符串。

## Common

- [Common/Contracts/ApiResponse.cs](Common/Contracts/ApiResponse.cs) — 成功与错误信封；timestamp 只表示响应生成的 Unix 毫秒。
- [Common/Errors/DatabaseErrors.cs](Common/Errors/DatabaseErrors.cs) — 只对命名唯一键的 1062 判冲突；其他数据库失败保留明确分类。
- [Common/Errors/ErrorBoundary.cs](Common/Errors/ErrorBoundary.cs) — 统一异常信封与 requestId；保留稳定事件，绝不回显异常/正文/连接串。
- [Common/Errors/PlanException.cs](Common/Errors/PlanException.cs) — 共享稳定错误键与业务异常；不携带请求正文、SQL 或连接秘密。
- [Common/Modules/ModuleRegistry.cs](Common/Modules/ModuleRegistry.cs) — 静态模块组合只校验元数据；重复 ID、缺依赖、路由冲突启动失败。
- [Common/Serialization/CreatePlanJson.cs](Common/Serialization/CreatePlanJson.cs) — 单一平面创建合同的严格 JSON binder：检测重复键、缺失/null、Unicode 与无损 Decimal。
- [Common/Serialization/ExactDecimal.cs](Common/Serialization/ExactDecimal.cs) — 原始十进制文本先无损归一化并检查存储边界，绝不先转 double/有损 decimal。
- [Common/Serialization/PlanOpenApi.cs](Common/Serialization/PlanOpenApi.cs) — 文档适配真实绑定合同：Decimal为number|string，列明手动绑定的分页/过滤参数。
- [Common/Time/BusinessTime.cs](Common/Time/BusinessTime.cs) — 无时区 MySQL DATETIME 明确解释为上海日历；输出固定秒精度和 offset。

## Infrastructure

- [Infrastructure/Logging/BackendLogging.cs](Infrastructure/Logging/BackendLogging.cs) — 紧凑 JSON Lines stdout + 10MiB/5 文件滚动；不输出异常正文或 SQL 参数。
- [Infrastructure/Persistence/PlanDbContext.cs](Infrastructure/Persistence/PlanDbContext.cs) — 每请求 scoped EF Context；模型组装不打开连接、不创建表、不播种。

## app/Plan

- [app/Plan/Contracts/CreatePlanIn.cs](app/Plan/Contracts/CreatePlanIn.cs) — 计划创建 DTO；所有客户端省略默认由此明确提供，持久实体与 DTO 分离。
- [app/Plan/Contracts/PlanOut.cs](app/Plan/Contracts/PlanOut.cs) — 完整输出：Decimal 固定 scale 字符串，日历时间由共享上海工具转换。
- [app/Plan/Contracts/PlanQueryIn.cs](app/Plan/Contracts/PlanQueryIn.cs) — 查询参数按精确整数和已检查的 offset 绑定；未知键忽略。
- [app/Plan/Domain/PlanRules.cs](app/Plan/Domain/PlanRules.cs) — 纯卷号规则：精确列举 Python str.strip 空白，校验副本但保存原值。
- [app/Plan/Endpoints/CreatePlanEndpoint.cs](app/Plan/Endpoints/CreatePlanEndpoint.cs) — 创建入口仅绑定严格 DTO、调用 Service 并返回信封，无 SQL 或事务控制。
- [app/Plan/Endpoints/GetPlanEndpoint.cs](app/Plan/Endpoints/GetPlanEndpoint.cs) — ID 不使用路由 int constraint，以便格式和范围错误统一收敛到 422。
- [app/Plan/Endpoints/ListPlansEndpoint.cs](app/Plan/Endpoints/ListPlansEndpoint.cs) — 分页与过滤入参解析后交 Service，Endpoint 不访问数据库。
- [app/Plan/ModuleManifest.cs](app/Plan/ModuleManifest.cs) — 唯一 plan 模块声明：三个 Endpoint、一个 Service 和一个 Entity。
- [app/Plan/Persistence/PlanEntity.cs](app/Plan/Persistence/PlanEntity.cs) — 唯一 plans 实体：25 个显式列，无导航或数据库默认。
- [app/Plan/Persistence/PlanEntityConfiguration.cs](app/Plan/Persistence/PlanEntityConfiguration.cs) — plans 显式 SQL 类型、列名和四个命名索引；不声明 server defaults 或迁移。
- [app/Plan/Persistence/PlanQueries.cs](app/Plan/Persistence/PlanQueries.cs) — 只负责参数化查询和添加实体，不提交事务、不操作 HTTP。
- [app/Plan/Services/PlanService.cs](app/Plan/Services/PlanService.cs) — 创建事务唯一 owner：预查、一次 DB 时间、显式默认、保存和确认提交。
- [app/Plan/Validators/CreatePlanValidator.cs](app/Plan/Validators/CreatePlanValidator.cs) — FluentValidation 负责 DTO 的业务/存储范围；JSON 形状由严格 binder 验证。

## tests

- [tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj](tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj) — MSTest HTTP/MySQL tests.
- [tests/AIIS.Backend.Tests/Contracts/HttpTests.cs](tests/AIIS.Backend.Tests/Contracts/HttpTests.cs) — 真实路由宿主的无库输入失败、模块开关与 OpenAPI 测试。
- [tests/AIIS.Backend.Tests/Contracts/LoggingTests.cs](tests/AIIS.Backend.Tests/Contracts/LoggingTests.cs) — 实际日志解析、10MiB 轮转与五文件保留；输出写入专属临时根，不改变项目依赖。
- [tests/AIIS.Backend.Tests/Domain/InputTests.cs](tests/AIIS.Backend.Tests/Domain/InputTests.cs) — 纯规则/序列化测试，覆盖精度、Unicode、缺失与显式 null。
- [tests/AIIS.Backend.Tests/Fixtures/ApiFactory.cs](tests/AIIS.Backend.Tests/Fixtures/ApiFactory.cs) — 测试专用 HTTP 宿主：固定源码根和显式测试配置，无生产测试钩子。
- [tests/AIIS.Backend.Tests/Fixtures/MySqlFixture.cs](tests/AIIS.Backend.Tests/Fixtures/MySqlFixture.cs) — 真实 MySQL 测试仅消费显式 run-root，并核对任务标签/loopback/固定库与版本。
- [tests/AIIS.Backend.Tests/Persistence/MySqlTests.cs](tests/AIIS.Backend.Tests/Persistence/MySqlTests.cs) — B 专属 MySQL 集成测试：真实 HTTP/EF/Driver/独立 SELECT，不用 InMemory/SQLite。
- [tests/AIIS.Backend.Tests/packages.lock.json](tests/AIIS.Backend.Tests/packages.lock.json) — Exact resolved dependency graph.
- [tests/infra/mysql.compose.yml](tests/infra/mysql.compose.yml) — Owned disposable mysql8.4.6 resources.
- [tests/infra/plans.sql](tests/infra/plans.sql) — Frozen test-only 25-column plans schema.
- [tests/scripts/run-mysql-tests.sh](tests/scripts/run-mysql-tests.sh) — Explicit prepare/test/coordinator cleanup.

## Project and documentation

- [.gitignore](.gitignore) — Owned output and secret exclusions.
- [AIIS.Backend.Api.csproj](AIIS.Backend.Api.csproj) — Root API project; tests globs excluded.
- [Directory.Packages.props](Directory.Packages.props) — Exact central direct versions.
- [NuGet.Config](NuGet.Config) — Official source only.
- [PLAN.md](PLAN.md) — Module documentation / root task index.
- [PLAN.zh-CN.md](PLAN.zh-CN.md) — Module documentation / root task index.
- [README.md](README.md) — Module documentation / root task index.
- [README.zh-CN.md](README.zh-CN.md) — Module documentation / root task index.
- [appsettings.json](appsettings.json) — Non-secret loopback defaults.
- [global.json](global.json) — Fixed SDK; no roll-forward/preview.
- [packages.lock.json](packages.lock.json) — Exact resolved dependency graph.
- [plans/README.md](plans/README.md) — Module documentation / root task index.
- [plans/README.zh-CN.md](plans/README.zh-CN.md) — Module documentation / root task index.
