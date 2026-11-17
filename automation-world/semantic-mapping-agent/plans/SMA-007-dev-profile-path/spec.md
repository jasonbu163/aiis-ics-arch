Task ID: SMA-007
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development 实施获批的 SMA-007 r1 路径对齐，交接后由独立 Verification 核验
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: SMA 源码启动时开发 profile 的相对和绝对路径对齐
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-004

# SMA 开发 profile 路径对齐

## 1. 目标与依据

SMA 源码开发可在本应用根 `.env` 中设置 `SMA_PROFILE_DIR=./.local/dev`，然后从 SMA 工程目录运行 `pnpm tauri dev`。目标是沿用 DAA、DS 的路径选择习惯，各应用仍使用独立目录和各自的文件格式。

| 参考 | 当前行为 |
| --- | --- |
| DAA [Rust 解析](../../../data-acquisition-agent/src-tauri/src/config/mod.rs)、[使用手册](../../../data-acquisition-agent/USER_GUIDE.zh-CN.md) | 普通启动读取本应用根 `.env`，可用绝对 `DAA_ENV_FILE` 指定文件。非空进程值先于文件值，两种来源的相对 profile 都相对所选文件的目录。 |
| DS [Rust 解析](../../../device-simulator/src-tauri/src/config/bootstrap.rs)、[路径准入](../../../device-simulator/runtime/src/config/profile.rs)、[使用手册](../../../device-simulator/USER_GUIDE.zh-CN.md) | 普通启动相对本应用根 `.env` 所在目录解析。`.local/dev` 与 `./.local/dev` 选择同一目录。 |
| SMA [当前解析](../../src-tauri/src/config/mod.rs)、[装配](../../src-tauri/src/app.rs)、[日志](../../src-tauri/src/infrastructure/logging.rs)、[启动偏好](../../src-tauri/src/config/runtime_startup.rs) | 普通 `.env` 已用于读取 HTTP 与 Backend 设置，profile 只看进程中的绝对值。配置库、日志和启动偏好当前各自取路径。本项基于 [SMA-004 r1 的最终验收](../SMA-004-local-configuration/checklist.md#owner-acceptance-r1)。 |

## 2. 路径合同

1. **选择配置文件。** 普通源码入口选取 `automation-world/semantic-mapping-agent/.env`。普通文件缺失时按无文件值处理，基准仍为 SMA 工程根。进程可用 `SMA_ENV_FILE` 指向另一个绝对、可读的常规文件。显式选择为空、相对、缺失、不可读，或最终文件是符号链接时，启动报错。已存在但不可读或类型不对的普通 `.env` 同样报错。启动过程只读取选中的文件。
2. **选择 profile。** 非空进程 `SMA_PROFILE_DIR` 优先，其次为所选文件中的非空同名值，两处均为空或未设置时使用 SMA 既有 Tauri 应用数据目录。文件中的 profile 键使用简单的 `KEY=VALUE` 字面值，支持一层成对引号，重复键第一项生效。两种来源的相对路径都以所选文件所在目录为基准，与进程当前目录无关。`.local/dev`、`./.local/dev` 和指向同一处的有效绝对路径解析到同一位置。既有有效绝对路径可直接继续使用。
3. **无效选择显式失败。** 有效覆盖值须为本机可用的绝对路径或普通相对字面路径。拒绝无效编码、变量或 `~`/占位符、`..` 路径段、Windows 盘符相对或根相对写法，以及 profile 或其现有上级路径中的符号链接、现有非目录路径组件。空白值作为未设置处理。路径准入失败时应能从启动错误定位选择键和原因，并在初始化配置库、日志、启动偏好等 profile 文件前停止。允许选择尚未创建、父路径有效且可用的目录。
4. **同一个绝对根。** 启动时解析一次，把同一个结果用于 `configuration.sqlite3`、`logs/` 中既有运行日志及 `runtime-startup.json` 的读写。库的 schema、revision、已存在配置、日志格式和启动偏好语义沿用原合同。旧自动启动偏好仍受现有运行准入限制。HTTP 和 Backend 设置沿用原来源和优先级，HTTP 仍默认关闭，所选文件仍对两项设置有效。环境 Backend 地址继续只作现有提示。
5. **示例和启动。** SMA 中英文 README 与 `.env.example` 展示 `./.local/dev` 及有效绝对路径写法，交代优先级、相对路径基准、现有 profile 如何继续使用和失败如何核对。已有 `.env` 先由使用者核对，示例默认 HTTP 关闭并保留空 Backend 地址。正常启动命令仍为 `pnpm tauri dev`。

## 3. 实施边界

精确批准后，候选文件边界以 SMA 工程目录为根。

| 路径 | 目的 |
| --- | --- |
| `src-tauri/src/config/mod.rs`、`src-tauri/src/app.rs` | 路径选择、拒绝顺序和启动装配 |
| `src-tauri/src/infrastructure/logging.rs`、`src-tauri/src/config/runtime_startup.rs` | 接收同一绝对根并保留各自持久化行为 |
| 上述模块内的 Rust 测试，或确有必要时新增一个 `src-tauri/tests/profile_startup_tests.rs` | 隔离验证路径选择及三类文件的实际路径 |
| `.env.example`、`README.md`、`README.zh-CN.md` | 源码启动示例及兼容说明 |

DAA、DS、共享 CU、SMA-005 页面、SMA-006 弹窗、SMA 产品身份与端口、运行门禁、SQLite schema、依赖、打包和 WebView 的 `sma.*` 界面偏好均在范围外。本路径只管 Rust 本机文件。真实配置与历史、实际默认数据目录和已有用户 profile 受保护，禁止本任务运行写入、删除、复制、迁移或重建。安装版的 `.env` 发现、发布部署和业务投递另立范围。

## 4. 验收标准

| AC | 可观察结果 |
| --- | --- |
| AC01 | 在自有临时 SMA 工程根中，用 `.env` 测试 `.local/dev`、`./.local/dev` 及等价绝对路径，结果同一绝对目录。改变调用进程工作目录，或在当前/上级目录放不同 `.env`，结果仍一致。普通 `.env` 缺失时，相对进程值仍锚定测试中的 SMA 工程根。 |
| AC02 | 把 `SMA_ENV_FILE` 指向另一个临时目录内的文件。相对文件值和进程值各自锚定所选文件父目录，非空进程值胜出，空白进程值让文件生效，两处均为空取原默认路径的隔离替身。只有所选文件提供 HTTP/Backend 文件值，设置优先级、显式 HTTP 关闭和未配置时的默认关闭结果符合现有行为。 |
| AC03 | 以临时夹具测试无效显式配置文件、`..`、非目录路径组件及 profile/上级符号链接。启动给出错误，选择目录、符号链接目标及默认替身均无配置库、日志或启动偏好写入。可在宿主验证的路径情形与仅有跨平台源码检查的情形分别记录。 |
| AC04 | 在隔离目录核对同一绝对根下实际三类路径。用合成 SQLite 配置和既有 v1 启动偏好重新加载，确认 revision、内容和偏好保留，日志使用同一根目录。另一个隔离 profile 读不到第一处配置。原 `.env`、默认路径及其他应用的目录不进入测试。 |
| AC05 | 从 SMA 工程目录的现有入口复核 `pnpm tauri dev` 仍可使用。两种语言的 README 和示例文件能推导出相同的实际位置与优先级，默认示例可离线使用。 |

可使用临时路径、隔离存储及 Rust 装配测试取证，默认分支使用注入的临时绝对路径或纯路径断言。路径验收全程离线，无需启动用户桌面应用或发 GET、POST。Development 与独立 Verification 整理具体命令、文件位置、拒绝前无写入的证据及平台限制。SMA-005 的应用内保存、GET 测试及重开由 Human Owner 手工操作。

## 5. 风险与交接

已经在 SMA `.env` 填过 `SMA_PROFILE_DIR` 的使用者须先核对有效选择。改选空目录会得到另一份配置。原有数据留在原目录，回退时重新指向原有效绝对路径。交接前在隔离目录覆盖路径优先级与无效选择，避免把配置落到预期外的位置。

- 2026-11-16（Asia/Shanghai）形成 SMA-007 r1 草案，待 Human Owner 批准。批准后由 Development 按 `desktop-tauri` 与 `rust-runtime` 实施并交接，再由独立 Verification 核验第 4 节。

## 6. Human Owner 批准

Human Owner 于 2026-11-16（Asia/Shanghai）批准 SMA-007 r1。

> 好的，批准 SMA-007 r1，先把 .local/dev 的绝对和相对路径跟 DAA、DS 对齐，完成后做独立验证。对齐后我自己测 SMA-005 的 GET，POST 先不做，SMA-006 继续保留草案。

获批的 r1 草案 SHA-256 为 `22ef2c9072924e629069994346c34575cccd37628ad124c6fcb229a257b89815`。
