Task ID: SMA-007
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development rework-2 -> fresh-context Verification
Workflow Mode: STD

# SMA-007 开发记录

## 实施计划

1. 在现有启动链解析所选文件与 profile，复用同一绝对根给配置库、日志和启动偏好。
2. 更新 SMA 的中英文启动说明和默认关闭的环境示例，保持原 HTTP/Backend 读取行为。
3. 在任务专用临时目录运行路径、存储和构建自检，记录精确候选后交独立验证。

## 已实施

- 启动先验证普通或显式 `SMA_ENV_FILE`，使用简单字面量读取文件中的第一个 `SMA_PROFILE_DIR`。非空进程值优先，文件值其次，两者为空使用原 Tauri 应用数据目录。相对值锚定所选文件父目录，`.` 路径组件归一，未修改原 HTTP/Backend 的 dotenvy 读取和进程优先语义。
- 在启动写入前拒绝无效文件、上级路径、非目录组件和已有符号链接。启动只生成一个 `ResolvedProfile`，实际装配将它用于 SQLite、日志和 Tauri 托管的启动偏好路径。日志初始化接收启动时的原有默认值，测试传入合成默认值。
- `.env.example` 保留空 profile 的原默认选择并展示相对和绝对例子；中英文 README 写明优先级、选择基准及现有路径的使用。SMA-005 页面和 SMA-006 草案未改。

## Development 自检

macOS Darwin arm64，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。当前目录为 SMA 工程，Cargo 使用仓库锁文件和已有缓存，所有路径夹具位于自有 `/private/tmp/sma007-dev.cdLuXx` 或其子目录。

| 命令或检查 | 结果与边界 |
| --- | --- |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` | 最终退出 0。首次格式检查报告新代码需格式化，按项目 rustfmt 格式化四个触达的 Rust 文件后复查通过。 |
| `SMA_ENV_FILE=/private/tmp/sma007-dev.cdLuXx/fixture.env SMA_HTTP_ENABLED=false SMA_BACKEND_BASE_URL='' TMPDIR=/private/tmp/sma007-dev.cdLuXx cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests -- --test-threads=1` | 最终退出 0，5 项通过。覆盖相对和绝对路径、首项键、空白和进程优先级、选择其他文件、cwd 子进程、HTTP 默认/覆盖、路径拒绝、SQLite/日志/启动偏好同根、重开和另一隔离库。 |
| 同上定向测试的首次运行 | 退出 101，4 通过、1 失败。已有普通文件的子路径当时返回 `SMA_PROFILE_DIR_UNAVAILABLE`。将检查顺序调整为从根到叶后，返回明确的 `SMA_PROFILE_DIR_NOT_DIRECTORY`，上述最终运行通过。首次运行的失败夹具仍在任务临时根内。 |
| 同样设置隔离环境后运行 `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --test startup_cleanup_tests v1_mapping_survives_and_legacy_segment_is_inert_and_preserved -- --exact` | 退出 0，1 项通过，覆盖 v1 偏好原字节读取、旧段保留与显式保存。 |
| 同样设置隔离环境后运行 `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --all-targets` | 退出 0，包含正常二进制装配和测试目标编译。未启动窗口。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false check` | 退出 0。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false test` | 退出 0，20 项通过。Vite 为内存 middleware，HTTP 和 IPC 使用进程内替身。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false build --outDir /private/tmp/sma007-dev.cdLuXx/frontend-dist` | 退出 0。Vite 提示外部 outDir 不自动清空、依赖 PURE 注释及 chunk 大于 500 kB。该 outDir 为本任务新目录。 |
| 触达文件 `git diff --check`，README、规格及开发记录相对路径链接检查 | 退出 0，四份文档 20 条本地路径链接存在。 |

Windows 盘符相对和根相对路径使用 `Path` 的平台组件规则并有 `#[cfg(windows)]` 断言；本机为 macOS，该分支未在 Windows 运行。Tauri 正常入口及现有 `pnpm tauri dev` 配置保持，Rust 全目标已编译；本轮按 Owner 指示没有启动桌面窗口，也没有发真实 GET、POST 或监听 HTTP。原生 GET 和 SMA-005 的人工步骤留给 Human Owner。

## developer_handoff

交接 SMA-007 r1，批准规格 SHA-256 `a1279b219a3f0c54b74c2b015ba1ce09c66c0020eea902b78500105416b4cc77`。正式交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，以下 7 项为本任务源码和说明的精确未提交候选。路径相对 SMA 工程，左右分别为任务开始前与交接时 SHA-256。

| 路径 | before | after |
| --- | --- | --- |
| `.env.example` | `36479d07ca936e42cdceb792cac00b462c67b8c5a33e1c4743a295fff1c95f4c` | `ee8544a02e42f91cea4a95737a144c346e650d4f0f34867dde46d7c18c4d71f0` |
| `README.md` | `b72b64cefefb5176c5ead6a660ba1fabd3b32c18310327b7e060872be3d0748c` | `160db0ff3ecf147f87b203776a9f3020eeab110149507d0c22c70c9f4ff83fa1` |
| `README.zh-CN.md` | `3e18d8f186d8f9e6c2c023945c07931423a31407ac208162f195e240348e7033` | `5b2166f9f46ee6537285e4c0c37c19f4f219471f97d51885e10360b9cc71ff85` |
| `src-tauri/src/config/mod.rs` | `ab7e6725b83146c3b451f207c4843f120bdee8f998f30c24b92a7d663bb52e4c` | `70107ef84d21d833a94cc2454c7be6b90f67d3d1617a74dd2bdf039adc825d18` |
| `src-tauri/src/app.rs` | `d9636997572a0ab47e36e5da02ec98eb7822c8561c52435d5bf55d39b946ae92` | `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b` |
| `src-tauri/src/infrastructure/logging.rs` | `3e5c5a1073a6243e584a32f1a5ce33af659fdb74ef10c39ee38df736cee8d761` | `0ce51e1a56f38674c504e924810648b01e47510cf6df85ef61acd379d447bc7b` |
| `src-tauri/src/config/runtime_startup.rs` | `9d03f6d0d8ef948b16c2d36a4d29d8542898cb2e463d0f006184122f26511a3e` | `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b` |

任务专用 `/private/tmp/sma007-dev.cdLuXx` 包含合成环境文件、前端构建、首次失败夹具及工具临时文件，交独立验证核对后由主协调按归属和证据依赖回收。Cargo 使用 SMA 既有忽略的共享 `src-tauri/target` 缓存，未删除。没有本任务常驻进程、独立 worktree 或分支。真实 `.env`、默认和已有 profile、DAA/DS 数据及服务未触达。

## rework-1 开发记录

首轮独立验证的 B1–B3 见 [checklist](checklist.md)，其当时 SHA-256 为 `3f490f020a49f295480d26e92863535d084f9aacf210c6cb5bc62f2ed3f3c9db`。本段保留首次交接和检查历史，以下交接候选替代上方首次 after 列用于复验。

- B1 增加 Windows `%TEMP%` 一类成对变量标记识别，文件值和进程值均在写入前拒绝。单独作为路径字面的 `%` 继续允许。成对的非空百分号标记按变量处理。
- B2 在解析时检查已有路径组件的可遍历性及最近现有目录的只读状态。日志采用原有每日轮转和文件名前缀，通过 fallible builder 将真实初始化错误转为包含 `SMA_PROFILE_DIR` 的错误。测试先通过路径解析，再以合成的 `logs` 文件阻止日志目录创建，核对返回错误、无 panic、无数据库或偏好文件。
- B3 中英文 README 均给出相对和绝对赋值，明确结果位于所选 `.env` 目录之下。示例继续将 HTTP 设置为 false、Backend 与默认 profile 留空。

| 返工检查 | 结果 |
| --- | --- |
| `SMA_ENV_FILE=/private/tmp/sma007-dev.cdLuXx/fixture.env SMA_HTTP_ENABLED=false SMA_BACKEND_BASE_URL='' TMPDIR=/private/tmp/sma007-dev.cdLuXx cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests -- --test-threads=1` | 最终退出 0，7 项通过。新增 `%TEMP%` 等进程与文件值、字面单个百分号、0555 目录本身和其未创建子目录、0666 不可遍历目录，以及日志目录文件冲突的错误返回。 |
| 返工首次定向运行 | 退出 101，6 项通过、1 项失败。0666 上级导致检查子路径时提前返回 `SMA_PROFILE_DIR_UNAVAILABLE`。把可遍历检查移到每个已有路径组件处后返回 `SMA_PROFILE_DIR_NOT_SEARCHABLE`，最终运行通过。 |
| 同样设置隔离环境后运行 `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --all-targets` | 退出 0。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`、`git diff --check` | 均退出 0。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false exec tauri dev --help` | 退出 0，仅显示 CLI 帮助。 |
| 双语 README 两种赋值、环境示例默认值和文档相对路径检查 | 退出 0，4 份文档共 21 个本地链接路径存在。 |

返工仅触达 Rust 配置和日志及三份说明，前端文件未改。首次候选的前端 20 项模拟测试、类型检查和构建结果见上文，本轮没有重复运行。权限位检查覆盖本机合成模式；其他文件系统或 ACL 的实际初始化错误由日志 builder 返回，具体权限语义取决于运行平台。Windows 路径分支未在 Windows 实机运行。

## developer_handoff rework-1

批准规格与 HEAD 没有改变。以下 7 项为正式交付树的最新候选，路径相对 SMA 工程。before 列为首次 developer_handoff 的 after，after 列为本次返工候选 SHA-256。相对任务开始时的原始 before 见上表。

| 路径 | before | after |
| --- | --- | --- |
| `.env.example` | `ee8544a02e42f91cea4a95737a144c346e650d4f0f34867dde46d7c18c4d71f0` | `f16f164a71f86229943886e30c7288ca2ae32f1a4fb5676e238c5a85dfb509d0` |
| `README.md` | `160db0ff3ecf147f87b203776a9f3020eeab110149507d0c22c70c9f4ff83fa1` | `8aca75a4c084b217160e5189167beefb3930f0da84cc94891a11595e6a7e7afb` |
| `README.zh-CN.md` | `5b2166f9f46ee6537285e4c0c37c19f4f219471f97d51885e10360b9cc71ff85` | `701a73d7e7104bdd7ec9ac00919d8988bcad3b96e2d3fd4f9aca33f4a798fd30` |
| `src-tauri/src/config/mod.rs` | `70107ef84d21d833a94cc2454c7be6b90f67d3d1617a74dd2bdf039adc825d18` | `156757fff6738ffee76d4d5c7aff078aab8174b8fe44359709b8492d645167ca` |
| `src-tauri/src/app.rs` | `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b` | `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b` |
| `src-tauri/src/infrastructure/logging.rs` | `0ce51e1a56f38674c504e924810648b01e47510cf6df85ef61acd379d447bc7b` | `d41fff70cb775bc6c090c5f3847085cecdf89ee616c08b0e59b20ddfcc291d8c` |
| `src-tauri/src/config/runtime_startup.rs` | `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b` | `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b` |

任务临时根仍为 `/private/tmp/sma007-dev.cdLuXx`，新增定向测试自行清理成功夹具，返工首次失败夹具随任务根保留。无新常驻进程、分支或 worktree，未运行桌面、监听器或实际网络请求。交新的 fresh-context Verification。

## rework-2 开发记录

第二轮独立验证的 F1 和 F2 见 [checklist](checklist.md)，其返工前 SHA-256 为 `15f5544edae60f7c2595105b4cec14b94c5e9118374ee917b4d9f0296996cc9a`。上方首次及 rework-1 交接和检查记录保留，以下最新交接候选用于复验。

- F1 在选择的 profile 字面值拼接所选文件父目录之前检查变量和占位符。已选择的环境文件父目录与系统提供的默认路径保留原字面字符，最终绝对路径仍检查路径结构、符号链接和目录权限。测试覆盖文件值与进程相对值、含 `%EXISTING%`、`$`、`~` 和占位符字符的实际合成基准、注入的默认路径，以及显式 `%TEMP%` 继续被拒绝。
- F2 以最近已存在目录的实际进程权限替代所有用户写入位的聚合判断。macOS 和 Linux 使用 `faccessat` 与 `AT_EACCESS` 检查有效身份的搜索和写入权限。Windows 使用目录句柄权限检查。已有可搜索但不可写上级下的可写子目录按子目录本身判定。fallible 日志初始化继续处理随后的文件系统错误。

| 返工检查 | 结果 |
| --- | --- |
| `SMA_ENV_FILE=/private/tmp/sma007-dev.cdLuXx/fixture.env SMA_HTTP_ENABLED=false SMA_BACKEND_BASE_URL='' TMPDIR=/private/tmp/sma007-dev.cdLuXx cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests -- --test-threads=1` | 退出 0，9 项通过。覆盖 F1 的基准、默认与显式值，以及 F2 的 0557 当前用户、目录本身、尚未创建子目录和已有可写子目录。 |
| 上述环境下单独运行 `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests::startup_path_checks_effective_user_and_allows_writable_existing_child -- --exact --nocapture` | 退出 0。本机 UID 501 对自有 0557 合成目录创建探针返回不可写，解析器对目录自身和新子目录均拒绝，已有可写子目录被接受，检查后无配置、日志或偏好文件。测试也按实际权限处理管理员具备写入能力的情况，本轮未以管理员身份运行。 |
| 同样设置隔离环境后运行 `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --all-targets` | 退出 0，正式源码的 macOS 普通入口和测试目标通过编译。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`、7 个交付文件 `git diff --check` | 均退出 0。 |
| 两份 README、规格和开发记录的本地路径链接检查 | 退出 0，22 个路径存在。 |

本机只安装 `aarch64-apple-darwin` Rust target。Linux 的 `faccessat` 常量对照了锁定依赖中的平台定义，Windows 的目录访问标志对照了本机缓存的 Windows 平台定义，两者均未在目标平台编译或运行。其他非 macOS/Linux/Windows 目标会返回 `SMA_PROFILE_DIR_UNSUPPORTED_PLATFORM`。这些平台证据边界交独立验证记录。

## developer_handoff rework-2

批准规格 SHA-256 `a1279b219a3f0c54b74c2b015ba1ce09c66c0020eea902b78500105416b4cc77`，正式交付树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。下表 before 为 rework-1 after，after 为本次正式工作树的最新候选。初始 before 和先前两轮候选保留在上方。

| 路径 | before | after |
| --- | --- | --- |
| `.env.example` | `f16f164a71f86229943886e30c7288ca2ae32f1a4fb5676e238c5a85dfb509d0` | `f16f164a71f86229943886e30c7288ca2ae32f1a4fb5676e238c5a85dfb509d0` |
| `README.md` | `8aca75a4c084b217160e5189167beefb3930f0da84cc94891a11595e6a7e7afb` | `8aca75a4c084b217160e5189167beefb3930f0da84cc94891a11595e6a7e7afb` |
| `README.zh-CN.md` | `701a73d7e7104bdd7ec9ac00919d8988bcad3b96e2d3fd4f9aca33f4a798fd30` | `701a73d7e7104bdd7ec9ac00919d8988bcad3b96e2d3fd4f9aca33f4a798fd30` |
| `src-tauri/src/config/mod.rs` | `156757fff6738ffee76d4d5c7aff078aab8174b8fe44359709b8492d645167ca` | `4c8765155af5d236c8c605c46382b8a9119360b29afcb490ef6b39bd73a7e9fe` |
| `src-tauri/src/app.rs` | `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b` | `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b` |
| `src-tauri/src/infrastructure/logging.rs` | `d41fff70cb775bc6c090c5f3847085cecdf89ee616c08b0e59b20ddfcc291d8c` | `d41fff70cb775bc6c090c5f3847085cecdf89ee616c08b0e59b20ddfcc291d8c` |
| `src-tauri/src/config/runtime_startup.rs` | `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b` | `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b` |

沿用任务自有 `/private/tmp/sma007-dev.cdLuXx`，成功测试的合成 profile 已清理，既有失败夹具和构建保留至独立复验后的资源核对。没有新常驻进程、分支或 worktree，未启动 GUI、监听器或真实 GET/POST。交新的 fresh-context Verification。
