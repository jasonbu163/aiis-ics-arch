Task ID: ARCH-BE-011
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 待 Human Owner 批准精确 r1；未进入 Development，不授权读取真实配置或采用现有数据库
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: C# 后端自有 .env 自动加载、配置优先级与脱敏启动诊断
Owner: AIIS ICS Architecture Backend
Acceptance Chain Reference: 本 spec 第 10 节；PM -> Human Owner 精确 r1 批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Related Task: ARCH-BE-007, ARCH-BE-008
Created: 2026-11-05
Updated: 2026-11-05

# C# 后端本地环境文件加载与启动配置体验

## 1. 目标与当前事实

用户已手动安装 SDK 10.0.403，提供的终端日志显示 API locked restore/build 成功；随后直接执行 `dotnet run --project AIIS.Backend.Api.csproj --no-build`，在启动配置校验中得到 `database_configuration_invalid`。用户希望像 Python 后端一样把配置保存在 `.env`，不必每次手动 export，并询问能否复用 Python 的 MySQL 开发库。

源码依据是 [薄入口](../../backend-dotnet/Program.cs)、[typed Options](../../backend-dotnet/Configuration/BackendOptions.cs)、[默认配置](../../backend-dotnet/appsettings.json) 和 [当前运行说明](../../backend-dotnet/README.zh-CN.md)：连接默认空，Server/Database/UserID/Password 任一缺失或连接串不可解析均拒绝启动；该错误先于实际 MySQL 连接，不证明数据库不可用。

[ARCH-BE-008 r1](../ARCH-BE-008-csharp-backend-plan-slice/spec.md) 首期明确不引入 dotenv，已有独立 QA2 仍仅覆盖其隔离学习切片。本任务是独立配置体验修复，不改写 008 的历史范围、失败或验收结论，也不继承它的数据库运行批准。

目标体验：用户自行在 C# 目录配置一次 `.env` 后，正常进入该目录运行 `dotnet run --project AIIS.Backend.Api.csproj` 即可加载；外部进程环境与命令行配置仍可覆盖文件。当前只形成 PM 草案，以下软件、测试和运行项均待精确批准。

## 2. 范围与文件所有权

### 2.1 当前 PM 阶段

PM 只写本 `spec.md`。不提前创建 `tasks.md`、`checklist.md` 或任何实现。主协调可在根与模块的 PLAN/catalog 双语索引中仅新增本任务 draft 行；不得覆盖并行 DAA 或其他任务修改。

### 2.2 r1 获批后的实现 allowlist

下列路径均相对仓库根；只允许为本任务所需的最小修改：

| 路径 | 允许变化 |
| --- | --- |
| `backend-dotnet/Program.cs` | 调用最小加载入口、处理已知配置启动失败；保持薄入口 |
| `backend-dotnet/Configuration/LocalEnvironment.cs` | 唯一新增 dotenv 加载/配置诊断 helper，不建立通用配置框架 |
| `backend-dotnet/Configuration/BackendOptions.cs` | 仅配置诊断所需的最小适配；现有必填、超时与绑定校验不放宽 |
| `backend-dotnet/AIIS.Backend.Api.csproj` | 单个 dotenv 包引用；明确环境文件不复制到 build/publish 输出 |
| `backend-dotnet/Directory.Packages.props` | 仅新增 dotenv.net 精确版本 |
| `backend-dotnet/packages.lock.json`、`backend-dotnet/tests/AIIS.Backend.Tests/packages.lock.json` | 仅新包及其必要传递图的真实 restore 结果 |
| `backend-dotnet/.env.example`、`backend-dotnet/.gitignore` | 无秘密示例；仅放行示例，保留真实 `.env*` 忽略规则 |
| `backend-dotnet/tests/AIIS.Backend.Tests/Configuration/LocalEnvironmentTests.cs` | 配置来源、优先级、字面值与脱敏的有意义回归 |
| `backend-dotnet/tests/AIIS.Backend.Tests/Contracts/HttpTests.cs` | 新启动语义所需的最小既有配置/进程回归适配 |
| `backend-dotnet/README.md`、`backend-dotnet/README.zh-CN.md` | 本机 SDK、配置一次后启动、优先级、错误定位与数据库边界 |
| `backend-dotnet/CODE_INDEX.md`、根 `CODE_INDEX.md` | 仅新增实际文件/入口的准确索引 |
| 本任务 `tasks.md` / `checklist.md` / `evidence/` | 分阶段由相应角色形成真实记录，evidence 只保存必要脱敏输出 |

主协调机械同步范围：根 `PLAN.*`、根 `plans/README.*`、`backend-dotnet/PLAN.*`、`backend-dotnet/plans/README.*` 共八份索引，仅本任务行；不另建模块任务正文。

### 2.3 排除项

不修改 Python、业务 API/DTO/事务/时间/实体映射、数据库 schema、真实 `.env`、根 AGENTS、Docker 或其他运行时。不增加认证、Swagger UI、后台进程、打包入口、第二套数据库键或环境配置编辑页面。

不创建、读取、复制或覆盖用户真实 `.env`，不打印连接串，不自动复用 `backend/.env`，不将真实文件纳入 Git、build 或 publish。用户自行填写其配置；Agent 验证只使用任务自有合成文件。

## 3. 固定配置合同

### 3.1 位置、时序与语法

1. 普通源码启动统一先进入 `backend-dotnet`；唯一环境文件为当前工作目录下精确的 `.env`。加载发生在 `WebApplication.CreateBuilder(args)` 捕获默认环境配置之前。
2. 不向父级、仓库根、Python 目录或可执行文件其他位置探测；不加载 `.env.local`、环境层叠文件或用户目录配置。测试可显式使用任务自有工作目录与合成 `.env`。
3. 沿用 `Database__ConnectionString`；ASP.NET Core 的 `__` 映射为 `Database:ConnectionString`。不增加 `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE` 兼容层。
4. 使用成熟库读取 UTF-8 的单文件 KEY=VALUE，支持空行、整行注释及成对引号。禁止变量展开、父级探测、环境层叠和 shell 执行；不手写另一套 dotenv 解析器。
5. 文件引号外的格式空白按库规则处理，密码内部的空格、`#`、`$`、反斜线和连接串分号必须按所声明引号语法保留。分号属于 MySQL 连接串值时，还须遵守 MySql.Data 的值引用语法。
6. `.env.example` 只示范一个 `Database__ConnectionString` 键，默认空值；连接串格式与占位说明写在注释和双语 README，不附可用账号、库或密码。

### 3.2 优先级与兼容性

配置优先级固定为：**命令行 > 已存在的进程环境变量 > 本地 `.env` > 既有 appsettings 文件**；不改变 ASP.NET Core 同类来源内部的既有规则。

- 现有环境变量不得被 `.env` 覆盖，包含显式空字符串；空环境变量继续进入原校验并明确失败，不偷偷使用文件值。
- `.env` 不存在但外部配置完整时正常启动；缺失且配置不完整时拒绝启动。
- 文件存在但读取失败、库抛出解析错误时，受控失败；不得静默当作文件不存在。连接串语法/必填非法由原 typed Options 校验拒绝。
- 不承诺库未定义的 dotenv 扩展语法；不增加命令替换、跨行插值或环境文件级联。
- 加载只影响当前应用进程，不修改父 shell、全局 PATH、用户 SDK 配置或系统持久环境。
- 现有模块开关、上海业务时区、五秒超时和仅 `127.0.0.1` HTTP 绑定规则保持原样。

### 3.3 诊断

已知本地文件读取/解析失败与数据库配置校验失败应退出非零并输出可解析 JSON Lines 的稳定诊断，不再仅抛出长堆栈使用户无法定位配置来源。

诊断只允许事件/错误 key、配置键名、缺失字段名和文件存在状态；可提示配置源为 `.env` 或进程环境，不回显任何配置值、连接串、密码、文件原始行或异常正文。其他编程错误不伪装成数据库配置错误。

固定诊断 key：`configuration_invalid` 事件；文件错误 `local_environment_invalid`；数据库配置错误沿用 `database_configuration_invalid`；已知上述失败进程退出码为 `1`。

运行诊断沿用稳定机器 key，双语 README 解释修复步骤；若实施确需新增面向用户的自然语言文案，必须按 i18n-workflow 对称管理，不借机建立新 UI/本地化框架。

## 4. 工具链与依赖

唯一新增直接依赖固定为 **dotenv.net 4.2.0**，来源为 [官方 NuGet 包页](https://www.nuget.org/packages/dotenv.net/4.2.0)，页面声明目标 .NET Standard 2.0。元数据不证明本工程已经 restore/build；兼容性必须由 Development 与独立 Verification 实测。

库选项须显式设置文件路径、保留已有环境、关闭 probe/cascade/variable expansion；不得依赖可能改变的默认值。本 r1 不允许静默改用其他包或版本，失败先回 PM 修订 Revision。

SDK 仍为 10.0.403 / net10.0，现有其他直接包、Provider 和 NuGet 官方源不变。允许使用用户已安装的精确系统 SDK，无需再下载 SDK；执行前核对实际绝对路径、版本和架构。

Agent 的 CLI/NuGet 缓存、合成文件、日志和结果须使用新建任务私有 `/private/tmp/arch-be011-<随机后缀>/`，不复用 008/FF/其他任务可写环境，不修改用户环境。禁止生成/信任开发证书，保留关闭遥测的验证设置。

## 5. Python 数据库复用的准确边界

源码层面 Python/C# 都映射 `plans`，当前 C# 对应 25 列和四个命名索引；共享同一个 MySQL 实例没有语言障碍。是否能共用现有数据库，还须核对真实 schema revision、列/索引/约束、权限、collation、历史时间与有效 writer，不能由源码对齐直接推断。

C# 创建当前要求实际 server/session 时区为 `+08:00` 或 `Asia/Shanghai` 且实际偏移 28800 秒，并将无时区 DATETIME 解释为上海日历；本任务不修改该检查或迁移历史时间。

Python [settings.py](../../backend/settings.py) 使用自己的环境文件解析和 `MYSQL_*` 键，构造 SQLAlchemy 的 `mysql+aiomysql://` / `mysql+pymysql://` URL。C# 接收 MySql.Data 的 `Server=...;Database=...;User ID=...;Password=...` 连接串；不能直接复制 Python `.env` 或把其 URL 当作 C# 连接串。

本 r1 不连接或只读探查现有开发库，不创建数据库/账号，不执行 DDL/迁移/业务 SQL，不开启双后端共写。现库核对与采用需要独立明确范围；本任务通过也不表示该数据库已被验证可直接复用。

## 6. 编号需求

| ID | 需求 | 位置 |
| --- | --- | --- |
| R01 | C# 自有单文件自动加载、来源隔离和普通 dotnet run 入口 | 2、3.1 |
| R02 | 精确配置优先级、缺文件兼容和原校验不放宽 | 3.2 |
| R03 | 成熟解析库、密码字面值保持及固定依赖/工具链 | 3.1、4 |
| R04 | 配置失败有稳定脱敏诊断和明确非零退出 | 3.3 |
| R05 | 示例/真实文件/构建交付隔离，双语使用说明与准确索引 | 2、3.1 |
| R06 | 数据库复用只说明能力与未验证边界，不隐含真实采用 | 5 |
| R07 | 无数据库的独立验证、精确交接与自有资源收尾 | 7、8、10 |

## 7. 验收标准

| AC | 必需结果与证据 | 需求 |
| --- | --- | --- |
| AC01 | 元数据/精确批准/allowlist 合法；旧 007/008 正文与任务外 dirty 保全，后续角色分阶段产生 | R05、R07 |
| AC02 | 固定 SDK/唯一新包真实 restore/build 成功，双锁一致；其他直接版本未变，API 未包含测试源码/真实环境文件 | R03、R05 |
| AC03 | 合成 `.env` 单独提供完整连接配置；从任务自有工作目录运行正式交付 DLL，health/OpenAPI 成功，无数据库连接 | R01、R07 |
| AC04 | 无 `.env` + 完整外部环境仍成功；无文件且缺配置、空/不可解析连接配置均受控失败/exit1 | R02、R04 |
| AC05 | 相互冲突的合成 appsettings、`.env`、外部环境及 CLI 逐级证明精确优先级；外部显式空值不被文件覆盖 | R02 |
| AC06 | 引号、密码内部空格/`#`/`$`/反斜线/分号按声明格式解析后逐字相等；无插值或命令执行，不把测试秘密打印到日志 | R03 |
| AC07 | 任务合成父目录/同级 Python 风格 `.env` 与层叠文件均不被读取；只读指定 cwd 的精确 `.env` | R01 |
| AC08 | 合成读取失败/库解析异常与数据库校验失败均有稳定 JSON Lines 诊断；随机测试秘密/完整连接串/原始行/异常正文无匹配 | R04 |
| AC09 | Git 忽略真实 `.env*`、仅示例可跟踪；MSBuild item/copy 元数据或受控临时输出证明真实环境文件不进入 build/publish | R05 |
| AC10 | 既有必要非 MySQL 配置/模块/HTTP 回归通过；三业务 API、无认证、loopback、时区/超时/DDL 边界不变 | R02、R06、R07 |
| AC11 | README pair 提供 cp 示例后自行填写、直接 dotnet run、优先级/错误修复与同实例/同库边界；CODE_INDEX 与实际结构一致 | R01、R05、R06 |
| AC12 | DEV 精确候选/命令/退出码/失败/资源进入 tasks；新 fresh Verification 独立验证并记录 verdict，Owner 终验仍单独进行 | R07 |

## 8. 实施与验证边界

批准后 Development 创建 tasks 并先复现缺配置错误，再实现最小加载与诊断；普通源码启动不要求手工 export。业务规则、SQL/表、登录和打包机制不进入范围。

只允许官方源新依赖 restore、必要 build、纯配置测试及既有 `TestCategory!=MySQL` 回归。首次新增包可更新双锁，随后必须 locked restore 验证；所有实际命令/退出码记录在 tasks。

专属本地进程 smoke 仅在新任务目录写合成 `.env` 和非秘密 appsettings，使用正式工作树编译 DLL 的绝对路径；仅请求 `/health`、`/openapi/v1.json`，不调用任何数据库业务 API。测试须使用明确合成连接和受控进程环境，不继承用户数据库配置。

最多同时一个任务自有 loopback HTTP 进程，使用临时空闲端口并记录 PID/退出；不得抢占默认 18108 或停止未知进程。健康成功只证明配置与进程，不证明数据库可用。

不得运行 Docker、MySQL 客户端、数据库 category、迁移、seed 或网络数据库连接；不连接用户 Python 后端、不运行其测试。所需 Win/Linux/生产/现场验证仍排除。

必要构建/测试结果、脱敏诊断与源码候选哈希持久化到本任务；进程/端口无依赖且证据归档后，主协调仅回收本任务自有临时目录。真实配置、数据库和他人资源始终保留。

## 9. 风险与回退

| 风险 | 控制与回退 |
| --- | --- |
| dotenv 默认展开/覆盖改变密码或部署配置 | 显式关闭展开/探测/层叠，外部环境优先，字面值与优先级回归 |
| 文件失败异常回显秘密 | 只输出稳定 key/配置字段/存在状态，随机合成秘密私下比对 stdout/stderr/持久日志 |
| 配置改进被误当作现库可直接采用 | 只做无库验证，README 保留同库 schema/时间/权限/writer 核对门槛 |
| 包或精确 SDK 无法实际恢复/构建 | 保留真实失败，回 PM 新 Revision，不自动换包/版本 |

软件回退只撤回本任务实现与新依赖，保留用户自行维护的 `.env`，继续使用原外部进程环境方式；不删除配置/数据，不修改 Python 或恢复数据库快照。

## 10. 批准、角色与当前交接

2026-11-05：用户提出环境文件自动加载及开发库复用问题；主协调交实际命名 `agent_type=pm` / `csharp_env_pm` 形成独立 r1。该请求和既有 008 批准均不等于已批准本精确 r1。

PM 配置入口为 [.codex/agents/pm.toml](../../.codex/agents/pm.toml)；配置 model/effort 不是独立运行遥测。当前只有 PM 成文，不存在本任务 Development self-check、QA 或 Owner 最终验收。

Human Owner 可审阅并明确：**“批准 ARCH-BE-011 r1，实施 C# 自有 .env 自动加载与脱敏配置诊断，按规格做无数据库验证；现有数据库采用另行确认。”**

批准后主协调实际调用命名 Development；真实 developer_handoff 后调用新的 `agent_type=verification, fork_turns="none"`，提供批准 spec、tasks、精确候选/diff/锁/命令及限制；最终由 Human Owner 接受。范围、版本、优先级或数据库边界实质变化先回 PM 新 Revision。

本阶段使用 aiis、project-governance；后续 Development 使用 backend-arch、code-document-indexer；如新增自然语言文案使用 i18n-workflow。没有前端、Celery、Docker、PLC 或应用打包范围。

## 11. 成文检查与来源

本文件只记录设计与验收口径，应用兼容性和软件验证尚未执行。PM 成文检查结果由下方记录补充，不升级为独立 QA。

- 官方依据：[dotenv.net 4.2.0](https://www.nuget.org/packages/dotenv.net/4.2.0)、[ASP.NET Core 配置与优先级](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)。前者作为候选依赖/选项来源，后者作为既有配置提供器规则来源，均不证明本工程已运行通过。
- 本次只形成新 spec；根/模块索引由主协调机械同步。未读取真实环境文件、执行 NuGet/应用/MySQL/Docker 或修改用户配置。
- PM 实际成文自检：`python3` 标准库内联文本检查退出 0；必需元数据、7 项需求、12 项 AC、7 个本地链接、唯一 Task ID、围栏/尾空白及后续角色文件尚不存在均通过。仅检查文档，不运行应用。
- 限定 `git diff --check -- plans/ARCH-BE-011-dotnet-local-environment-loading/spec.md` 退出 0；因本文件尚未跟踪，另以上述直接文本检查覆盖新文件空白，不以空 diff 推断内容已验证。
