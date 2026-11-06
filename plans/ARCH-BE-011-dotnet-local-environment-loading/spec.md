Task ID: ARCH-BE-011
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 待 Human Owner 批准精确 r2；只读数据库核对按独立授权记录，不授权实现、真实 secrets 写入或现库共写
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: C# 后端原生 appsettings/User Secrets 配置与配置一次后直接运行的开发体验
Owner: AIIS ICS Architecture Backend
Acceptance Chain Reference: 本 spec 第 10 节；PM -> Human Owner 精确 r2 批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Related Task: ARCH-BE-007, ARCH-BE-008
Created: 2026-11-05
Updated: 2026-11-05

# C# 后端原生配置与开发启动体验

## 1. 目标、修订与当前事实

用户已安装 SDK 10.0.403，提供的日志显示 API locked restore/build 成功；随后未提供数据库配置，启动时得到 `database_configuration_invalid`。本错误来自 typed Options 校验，先于实际数据库连接，不证明 MySQL 已被尝试连接或不可用。

用户现在明确选择：“按 .NET 原生方式来，把之前的 .env 改造规格调整为 appsettings.json + User Secrets，配置一次后直接 dotnet run。也先只读核对一下能否复用我现有的 Python MySQL 开发库。”该选择授权修订草案及指定只读核对，不等于已批准本文精确 r2 的软件范围。

r1 的 dotenv 方案从未批准、从未实施，由本 r2 替代。主协调已将 r1 完整字节保存为非权威 [历史附件](evidence/spec-r1-superseded.md)，SHA256 为 `42ee4cae54b3ef9ee0d7dfaffa5714624f8fe3e557602aca741772453ccfbc5d`；附件保留当时 draft 元数据，不形成并行执行权威。Task ID 和任务目录保持不变。

现有 [Program.cs](../../backend-dotnet/Program.cs) 使用 `WebApplication.CreateBuilder(args)`，已具备原生 JSON、环境变量与命令行配置来源；[API 项目](../../backend-dotnet/AIIS.Backend.Api.csproj) 尚无 UserSecretsId，也没有本任务的 Development 启动 profile。[默认配置](../../backend-dotnet/appsettings.json) 的数据库连接为空，绑定 `127.0.0.1:18108`。

目标：项目固定非秘密 UserSecretsId 与默认 Development HTTP profile；用户自行保存一次 `Database:ConnectionString` 后，在 `backend-dotnet` 直接 `dotnet run` 即可再次启动。生产环境继续使用原生外部配置，不依赖开发 secrets。

本任务不改写 [ARCH-BE-008](../ARCH-BE-008-csharp-backend-plan-slice/spec.md) 的批准、失败历史或 QA2 结论，也不把其隔离库验证扩大为现有开发库已被采用。

## 2. 范围与文件所有权

### 2.1 当前阶段

PM 只写本 `spec.md`；主协调只机械同步根/模块八份 PLAN/catalog 的本任务 r2 draft 行，并持久记录单独授权的只读数据库观察。未创建 tasks/checklist，不进入代码、依赖或真实配置修改。

### 2.2 r2 获批后的实现 allowlist

下列路径相对仓库根；只允许与本任务直接相关的最小修改：

| 路径 | 允许变化 |
| --- | --- |
| `backend-dotnet/AIIS.Backend.Api.csproj` | 添加固定 UserSecretsId；必要的无秘密复制元数据审查，不增加包 |
| `backend-dotnet/Properties/launchSettings.json` | 唯一默认 Development HTTP profile，无连接串/密码/秘密 |
| `backend-dotnet/Program.cs` | 仅已知配置失败的最小受控诊断；保持原生 CreateBuilder 与薄入口 |
| `backend-dotnet/Configuration/StartupConfiguration.cs` | 若诊断需要，唯一最小 helper；不是新配置加载器/提供器 |
| `backend-dotnet/Configuration/BackendOptions.cs` | 仅配置诊断所需适配；原必填/绑定/超时校验不放宽 |
| `backend-dotnet/tests/AIIS.Backend.Tests/Configuration/NativeConfigurationTests.cs` | 原生来源、profile、隔离 secrets、优先级与生产回归 |
| `backend-dotnet/tests/AIIS.Backend.Tests/Contracts/HttpTests.cs` | 新启动语义所需的最小既有配置/进程回归适配 |
| `backend-dotnet/README.md`、`backend-dotnet/README.zh-CN.md` | 用户一次配置、普通运行、原生优先级、错误定位与数据库核对边界 |
| `backend-dotnet/CODE_INDEX.md`、根 `CODE_INDEX.md` | 仅实际新增文件/入口的准确索引 |
| 本任务 `tasks.md` / `checklist.md` / `evidence/` | 相应角色分阶段形成真实记录，evidence 只保存必要脱敏输出 |

原有 `appsettings.json` 的非秘密默认和空连接串保持；没有实际非秘密差异就不新增 `appsettings.Development.json`。若确需新增开发 JSON 或调整默认，先回 PM 明确文件与差异，不在实现中自由扩大来源。

`Directory.Packages.props`、两个 `packages.lock.json`、NuGet 源与 SDK 版本不在写入 allowlist；本 r2 不增加任何新包，不写 dotenv loader、`.env.example` 或自制解析器，不因旧 r1 引入锁图变更。

主协调机械索引：根 `PLAN.*`、根 `plans/README.*`、`backend-dotnet/PLAN.*`、`backend-dotnet/plans/README.*` 共八份，仅本任务行；不建立第二份任务正文。

### 2.3 排除项

不修改 Python、API/DTO/业务事务/实体映射/时间、数据库 schema、根 AGENTS、Docker、认证、Swagger UI、后台宿主或其他运行时。没有真实数据库写入、迁移、账号/权限修改、时区修改、现库共写、生产采用或发布/部署授权。

Agent 不读取、创建或修改用户真实 User Secrets，不把 Python `.env` 自动导入 C#，不将秘密写入 tracked JSON、launchSettings、源码、Git、build/publish 输出。用户真实 `.env` 仅主协调的本次限定只读审计可按第 5 节访问，不进入软件实现验证。

## 3. 原生配置与启动合同

### 3.1 固定 ID 与非秘密文件

1. API csproj 固定非秘密 `<UserSecretsId>aiis-ics-arch-backend-dotnet-dev</UserSecretsId>`，同一工程后续复用该 ID；教程不要求用户每次 `user-secrets init` 生成随机 ID 或修改 csproj。
2. `appsettings.json` 保存现有地址、模块开关、时区、超时、日志等非秘密默认；`Database:ConnectionString` 保持空值。密码由用户自行在 User Secrets 中设置。
3. 已有 Web SDK 与原生 CreateBuilder 自动处理 Development 的 User Secrets；不手动调用另一套 AddUserSecrets，不添加外部配置库，不复制 secrets 到工程目录。
4. User Secrets 是开发机上的用户级 JSON 配置，隔离于源码且不是加密保险箱；生产 secrets 来源仍由部署环境管理，不能把开发 secrets 当作部署工件。

### 3.2 唯一默认 Development profile

`Properties/launchSettings.json` 只定义一个名为 `AIIS.Backend.Api` 的 `commandName=Project` profile：HTTP `http://127.0.0.1:18108`，`launchBrowser=false`，并设置 `ASPNETCORE_ENVIRONMENT=Development` 与 `DOTNET_ENVIRONMENT=Development`。不配置 HTTPS，不生成或信任开发证书，不包含数据库配置。

从 `backend-dotnet` 直接运行 `dotnet run` 应自动选择该 profile，确实进入 Development 并加载固定 ID 的 secrets。首次加入 UserSecretsId 后必须重建程序集；首次直接 `dotnet run` 可自动编译，不能使用修改前的 `--no-build` 产物代替。

launch profile 是开发工具注入规则，其中设置的环境名称会覆盖同名继承值；它与应用配置的优先级是不同层次。需要保留外部运行环境时可使用 `--no-launch-profile`；在受控清除环境名称后，无 profile 的默认环境仍是 Production。

Production/Staging 不自动加载开发 User Secrets；直接执行 DLL/生产入口也不自动套用开发 profile，不在代码中把默认环境强制改为 Development。

### 3.3 原生优先级与键

应用配置从高到低为：**命令行 > 进程环境变量 > User Secrets（仅 Development）> appsettings.{Environment}.json > appsettings.json > host fallback**，保留 .NET 原生行为。

User Secrets 中沿用 `Database:ConnectionString`；外部环境变量沿用 `Database__ConnectionString`。不增加 Python `MYSQL_*` 兼容键，不自定义统一 env 文件。

已有外部配置可覆盖开发 secrets，CLI 可覆盖外部配置；显式空值仍进入原 typed Options 校验，不悄悄回退到较低优先级秘密。现有上海时区、五秒超时和 loopback 绑定校验不放宽。

### 3.4 一次配置教程

README 应说明：项目已固定 ID，不必先执行 init；用户在 API 工程目录自行执行一次如下模板，将占位内容替换为自己的开发连接信息：

```bash
dotnet user-secrets set 'Database:ConnectionString' '<MySql.Data格式的开发连接串>' --project AIIS.Backend.Api.csproj
dotnet run
```

教程说明 secrets 持久保存在当前用户的工程专属存储，新终端/新进程仍可使用；不以 `user-secrets list` 打印真实配置作为常规验证。连接串需遵守 MySql.Data 的分号、引号和特殊字符规则，不复制 SQLAlchemy URL。

## 4. 最小启动诊断与工具链

保留已知数据库配置错误的受控诊断：事件 `configuration_invalid`、错误 key `database_configuration_invalid`、已知失败退出码 `1`；只允许配置键名、缺失字段名、当前环境名称及“Development 可使用 User Secrets”的来源提示。

不输出密码、完整连接串、secrets 文件正文、原始异常正文或长堆栈；未知编程错误不伪装成配置缺失。运行诊断沿用稳定机器 key，双语 README 解释修复；如新增自然语言终端文案，使用 i18n-workflow 对称管理。

SDK 仍为用户已安装的 10.0.403 / net10.0；核对实际路径/版本/架构后使用，不下载新 SDK、不改 PATH/用户工具配置。现有全部直接依赖及双锁保持不变。

Agent 验证使用新建 `/private/tmp/arch-be011-native-<随机后缀>/` 的 CLI/NuGet 缓存、合成 secrets、日志与结果；关闭证书生成/遥测，不复用 008/FF/其他任务环境。

## 5. 现有 Python MySQL 的只读核对

### 5.1 独立授权与访问范围

用户已明确授权主协调“先只读核对”现有 Python MySQL 开发库。该授权独立于本文未来实现 gate；PM 本身不连接数据库、不读取真实配置，也不把它解释为现库采用或 C# 写入授权。

主协调可受控读取 `backend/.env` 中现有应用账号的目标信息，以该应用账号只读连接；不使用 root/维护账号，不输出密码、完整连接串、环境文件正文或原始业务记录。

只允许版本、schema revision、表列/索引/约束、server/session 时区、账号权限等元数据 SELECT/SHOW 与必要的脱敏聚合；允许仅为保护查询设置只读事务特征，结束 ROLLBACK/CLOSE。不执行 DDL/DML、迁移、seed、时区/其他全局或会话配置修改、C# 业务接口请求，不写用户 secrets。公开记录只使用目标别名与必要结论，不保存真实地址、库名、账号或业务值。

### 5.2 观察与结论

主协调于 2026-11-05 完成已授权只读审计，目标别名 `python_host_development_config`；[脱敏持久证据](evidence/mysql-readonly-audit-2026-11-05.json) SHA256 为 `a3e5408bb83891a90f561fce68bd634f3eaa921454baecfb8a8985774140a03b`。以下是本轮实际观察，不是 Development/QA 或 C# 运行证明：

| 检查面 | 实际观察与限度 |
| --- | --- |
| 实例与表 | MySQL 8.4.6；plans 为 InnoDB / utf8mb4_0900_ai_ci |
| 列与索引 | 25 列的类型/长度/DECIMAL 精度/可空/自增均匹配 C#；PRIMARY 与四命名索引全匹配，无额外列/索引 |
| schema revision | 当前 Alembic 标识 e4f6a8b0c2d4；未由此宣称全库已到最新 revision |
| 查询与历史 | SELECT 25 个预期列 LIMIT 0 成功；plans 当时无行，不能验证历史时间或业务数据解释 |
| 权限元数据 | 应用账号直接 grants 在匹配 scope 显示 SELECT/INSERT 与 ALL PRIVILEGES；未实际 INSERT，角色 grants 未展开，不能据此宣称最小权限或写入已通过 |
| 时区与时钟 | session/global time_zone 均为 SYSTEM，system_time_zone 为 CST；当前实际偏移 28800 秒，即 +08:00 |
| 保全 | 仅现有应用配置字段，未选维护账号；只读事务结束 ROLLBACK/CLOSE；真实 env 前后哈希一致，无业务行输出，无真实 User Secrets 读写 |

**复用判断：表结构满足作为 C# 候选目标的条件，但当前不能直接宣称完整创建链可用。** C# 的现有 Create guard 要求 server/session 字符串均为 `+08:00` 或 `Asia/Shanghai`，即使实际偏移已是 +08:00，仍会拒绝本次观察到的 `SYSTEM`。这是结合源码与元数据的推断，未发 C# 请求实证；不能把它描述成数据库实际偏移错误。

该兼容点只列为后续精确修订/采用条件，本 r2 不默认更改 MySQL 全局时区、不绕过 guard、不迁移历史时间、不放开共写。当前 PyMySQL 元数据 SELECT 不代替 C# MySql.Data/EF 的实际连接、读写、事务、并发与有效 writer 核对；同实例复用可行与同库已接受是不同结论。

失败历史在证据中保留：首次沙箱连接 2003 失败；网络执行后的临时 helper 列名正则漏数字，在读元数据后断言失败；只修临时 helper 后完整审计退出 0。helper 失败不归因于数据库结构不兼容。触发器仅限应用账号可见范围，不能把未见记录当作全权限审计。

主协调已按 [只读审计资源记录](evidence/readonly-audit-resources.json) 完成连接 ROLLBACK/CLOSE、同步 helper 退出与 9 份自有临时文件回收，并核验私有审计目录不存在；必要观察已持久化。该收尾不操作用户配置、真实 User Secrets、数据库内容或任务外资源。

Python [settings.py](../../backend/settings.py) 的 `MYSQL_*` 键生成 `mysql+aiomysql://` / `mysql+pymysql://` URL；C# 使用 MySql.Data `Server=...;Database=...;User ID=...;Password=...` 连接串。配置可以指向经确认的相同目标，但格式不能直接照搬。

## 6. 编号需求

| ID | 需求 | 位置 |
| --- | --- | --- |
| R01 | 原生 appsettings + 稳定 UserSecretsId，一次保存配置后直接运行 | 3.1、3.4 |
| R02 | 唯一默认 Development HTTP profile，首次重新编译且生产默认不改变 | 3.2 |
| R03 | 原生优先级、现有环境/CLI 兼容及开发 secrets 环境边界 | 3.3 |
| R04 | 已知配置错误稳定脱敏诊断，原校验不放宽 | 4 |
| R05 | 真实 secrets 与源码/构建隔离，最小双语说明与准确索引，无新包/锁图 | 2、3、4 |
| R06 | 已授权只读现库观察、复用推断与实际采用边界清楚分离 | 5 |
| R07 | 合成 secrets 隔离验证、跨进程恢复、精确角色交接与资源收尾 | 7、8、10 |

## 7. 验收标准

| AC | 必需结果与证据 | 需求 |
| --- | --- | --- |
| AC01 | r2 元数据/精确批准/allowlist 合法，r1 原字节历史附件可复核；旧 007/008 与任务外 dirty 保全 | R05、R07 |
| AC02 | SDK/全部直接包/双锁不变，locked restore/build 与必要非 MySQL 回归通过；无 dotenv 包/loader/示例引入 | R01、R05 |
| AC03 | API 编译产物包含固定 UserSecretsId；唯一默认 profile 实际进入 Development，原生 provider 自动读取任务合成 secrets | R01、R02 |
| AC04 | 合成 secrets 用原生命令设置一次，结束首进程后另起新进程仍可自动读取；不重复 set/export，health/OpenAPI 均成功 | R01、R07 |
| AC05 | 相互冲突的合成 appsettings、secrets、外部环境及 CLI 逐级证明原生优先级；显式空值不被低优先级值覆盖 | R03 |
| AC06 | `--no-launch-profile` 且无环境名称时确为 Production，不读开发 secrets；外部有效连接仍可启动；Staging 同样不读 secrets | R02、R03 |
| AC07 | 无 secrets/缺连接、空值/不可解析连接受控失败/exit1，诊断帮助区分配置来源与数据库连接失败，无任何秘密泄漏 | R04 |
| AC08 | 实际解析的测试 secrets 路径在新任务私有根；父用户 secrets 不读不写；合成空格/引号/`#`/`$`/分号值持久恢复保持原貌 | R05、R07 |
| AC09 | tracked appsettings/profile 无秘密；构建项/复制元数据证明真实 secrets 不进入 build/publish；没有自动导入 Python env 的代码 | R05 |
| AC10 | 正式交付源码/DLL验证，仅 smoke health/OpenAPI；三业务API、无认证、loopback、时区/超时/DDL边界不变 | R04、R07 |
| AC11 | README pair 提供固定 ID 下的一次 set、直接 run、首次重建、原生优先级/Production 行为与复用前条件，链接本 spec 的只读观察且不复制为第二证据面，索引准确 | R01、R02、R05、R06 |
| AC12 | 本次现库只读审计与未来无库软件验证证据分别记录；DEV tasks/新 fresh QA checklist/Owner终验不相互替代 | R06、R07 |

## 8. 未来实现验证与资源隔离

精确 r2 批准后 Development 创建 tasks；先复现缺配置失败，再固定 ID/profile 与最小诊断。普通开发命令不要求每次 export；不实现其他配置框架或数据库采用逻辑。

只允许固定官方源 locked restore、必要 build、纯原生配置测试及 `TestCategory!=MySQL` 回归；不新增包，不更新锁文件来掩盖漂移。首轮必须重建以生成固定 ID 的程序集元数据。

验证只写合成 User Secrets：所有相关 CLI、`dotnet test`/测试宿主及应用子进程均设置任务私有 `APPDATA`，利用 .NET 原生路径解析隔离 stores；已有 WebApplicationFactory 的 Development 默认也必须被该隔离覆盖。不得重设 HOME、用户全局环境或真实 secrets。写入前必须证明 CLI 与应用解析目标均位于私有根，若无法证明则停止写入并记录 blocker，不回退到真实用户路径。

测试进程使用受控环境，移除继承的数据库配置和环境名称，仅注入明确合成值；应用启动不连接数据库，仅访问 `/health`、`/openapi/v1.json`。配置成功不等于数据库可用。

默认 profile 的实际 `dotnet run` 验证可用应用 CLI 覆盖为任务空闲 loopback 端口，记录 profile/env 与实际 PID；最多一个任务 API，不抢占 18108、不停未知进程。也可直接运行正式交付 DLL 验证 Production 语义，不使用临时源码副本代替交付。

Development/Verification 不继承本次现库只读授权去跑 MySQL category、数据库客户端或业务接口；不连接 Python 服务，不执行 Docker、DDL/DML、迁移、seed 或账号/时区变更。其他 OS、生产/现场与长期运行验证排除。

必要脱敏结果/命令退出码/失败/源码候选哈希持久化后，主协调核对无 PID/端口/证据依赖，仅回收本任务自有缓存与合成 secrets。真实用户 secrets、真实 env、数据库和他人资源始终保留。

## 9. 风险与回退

| 风险 | 控制与回退 |
| --- | --- |
| 只添加 ID 却复用旧 DLL，或环境实际是 Production | 首次重新 build；实际默认 profile/原生 provider 与跨进程恢复验证 |
| launch profile 与外部环境优先级被混为一谈 | 分开说明环境名称注入与应用配置来源；无 profile 的生产语义独立验证 |
| 配置/日志或测试路径泄露/污染真实 secrets | 只用隔离 APPDATA/合成 stores，先验路径归属；无真实 secrets list，私下秘密比对脱敏 |
| 只读现库结构匹配被当成安全共写证明 | 明确只读观察与未验证业务/历史/writer边界，不执行写入采用 |

回退仅撤回本任务 ID/profile/诊断变更，保留用户自行维护的 User Secrets，恢复原外部环境方式；不删除真实秘密/数据、不改 Python，也不执行数据库恢复。

## 10. 审批历史、角色与交接

| 日期 | 真实事件 | 当前含义 |
| --- | --- | --- |
| 2026-11-05 | PM 形成 r1 dotenv 草案 | 未批准、未实施；完整字节附件已归档，由 r2 替代 |
| 2026-11-05 | 用户明确改用原生 appsettings + User Secrets，并授权先只读核对 Python MySQL 开发库 | 授权修订本 r2 和指定只读审计，不是对未见过的精确 r2 软件范围批准 |
| 2026-11-05 | 主协调完成单独授权的只读现库审计，实际命名 PM `agent_type=pm` / `csharp_env_pm` 据脱敏证据修订本文 | r2 draft；只读观察已记录，仍等待 Human Owner 精确软件范围批准 |

PM 配置入口 [.codex/agents/pm.toml](../../.codex/agents/pm.toml)；配置 model/effort 不作为独立运行遥测。PM 只维护 spec，不代写 Development/QA 事实。

建议精确批准口径：**“批准 ARCH-BE-011 r2，实施原生 appsettings + User Secrets 与默认 Development 启动体验，按规格做隔离无数据库验证；现库共写和真实采用另行确认。”**

批准后主协调实际调用命名 Development；真实 handoff 后以 `agent_type=verification, fork_turns="none"` 启动新的独立 Verification，再交 Human Owner 最终验收。版本、范围、优先级、真实秘密或数据库边界实质变化先回 PM 新 Revision。

本阶段使用 aiis、project-governance；后续实施使用 backend-arch、code-document-indexer，新增自然语言文案使用 i18n-workflow。没有前端、Celery、Docker、PLC 或生产打包范围。

## 11. 来源与成文检查

- 原生配置依据：[ASP.NET Core 配置](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)、[开发 User Secrets](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets)、[dotnet run 与 profile](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-run)。
- 隔离测试方案参考 [.NET User Secrets PathHelper 源码](https://github.com/dotnet/runtime/blob/main/src/libraries/Microsoft.Extensions.Configuration.UserSecrets/src/PathHelper.cs)：读取 APPDATA/HOME 的原生规则；具体 SDK10.0.403 的 CLI/应用实际路径仍须后续验证，不把源码推断当作已运行证据。
- 当前只完成 PM r2 修订与主协调已授权只读观察的记录；PM 本身未连接数据库。没有 Development、QA 或软件通过结论。
- PM 实际成文检查：`python3` 标准库内联文本检查退出 0；r2/draft 元数据、7 项需求/12 项 AC、9 个本地链接、r1 附件与审计证据 SHA256、围栏/空白、后续角色文件缺席及无新依赖写入要求均通过。仅检查文档与脱敏附件。
- 限定 `git diff --check -- plans/ARCH-BE-011-dotnet-local-environment-loading/spec.md` 退出 0；新文件空白另由直接文本检查覆盖。上述成文检查不升级为软件、C# 数据库功能或现库采用验证。
