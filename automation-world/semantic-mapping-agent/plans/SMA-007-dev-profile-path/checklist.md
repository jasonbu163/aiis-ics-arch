Task ID: SMA-007
Revision: r1
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification
Handoff: Verification -> Human Owner 最终验收
Workflow Mode: STD

# SMA-007 r1 独立验证：首轮 QA

## 候选与边界

- 独立 Verification 在 fresh context 读取项目根契约、根及 AW/SMA 双语 README/PLAN、canonical workflow、完整获批规格及 Development 交接，并按 `project-governance`、`rust-runtime`、`desktop-tauri` 复核。本记录是合同验证，不声称平台 ACL、强制路由或 Human Owner 验收。
- Human Owner 于 2026-11-16（Asia/Shanghai）批准本 Revision；精确批准后 `spec.md` SHA-256 `a1279b219a3f0c54b74c2b015ba1ce09c66c0020eea902b78500105416b4cc77`；`developer_handoff` 的 `tasks.md` SHA-256 `d691ff2dd0f83356de7e1ea425076281690d440d71214d63657ec7ee6929dd4d`。
- 正式交付工作树 HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`；七项任务候选的 HEAD 内容 SHA-256 均与 `tasks.md` 的 before 列一致，实际工作树七项 SHA-256 均与 after 列一致。七文件完整 `git diff` 的 SHA-256 为 `8a8fc5300480a42dd779d5b580952788f511999186d2dbd100923c4d4e7c5f7f`。工作树还含其他任务的既有并行差异；本轮不将其归为 SMA-007。
- 验证环境：macOS Darwin arm64，UID 501，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。Rust 测试用精确选择的离线/锁定目标；`SMA_ENV_FILE` 为任务合成文件，`SMA_HTTP_ENABLED=false`，`SMA_BACKEND_BASE_URL` 为空，`TMPDIR` 和 `CARGO_TARGET_DIR` 指向任务临时根。隔离 target 是 SMA 现有 target 的 APFS clone，并非正式源码工作树的更改；Cargo 对正式工作树执行检查。无真实 `.env`、`.local/dev`、默认或已有用户 profile、其他应用数据的读取或写入。

## 验收矩阵

| AC | 结果 | 独立证据与限制 |
| --- | --- | --- |
| AC01 | 通过 | 交付代码中的定向 Rust 测试及额外隔离 probe 验证 `.local/dev`、`./.local/dev`、等价绝对路径、普通 `.env` 缺失时相对进程值以合成工程根为基准；子进程更换 cwd 并放置不同 `.env` 后仍选择合成工程根。无目录创建。 |
| AC02 | 通过 | 定向测试和额外 probe 验证显式选择的合成文件父目录锚定文件及进程相对值、非空进程值优先、空白回退、首个重复 profile 键及空值时隔离默认替身。HTTP/Backend 定向子进程覆盖所选文件、进程覆盖、显式关闭和空文件默认关闭；无网络请求。 |
| AC03 | **失败** | 空、相对、缺失、非普通文件和符号链接配置文件；`..`、无效 UTF-8、profile 上级符号链接和非目录组件均在合成 fixture 中拒绝，不向目标/默认替身写入。普通及显式 mode `000` 不可读文件返回 `SMA_ENV_FILE_READ_FAILED`。但规格 §2.3 的变量拒绝与不可用路径的准入/错误合同分别被 B1、B2 违反。Windows 原生路径分支未运行。 |
| AC04 | 通过 | `startup_path_uses_one_root_for_storage_logs_and_preferences` 使用合成目录实际创建 SQLite、JSONL 日志和启动偏好；更新至 revision 1 并重开比较完整 snapshot 和偏好字节；另一隔离库为 revision 0，未读到首处内容。独立定向 `v1_mapping_survives_and_legacy_segment_is_inert_and_preserved` 验证旧 v1 偏好读取不改字节并显式保存惰性旧段。此证据不覆盖用户已有 profile。 |
| AC05 | **失败** | `package.json` 的 `tauri` 脚本指向 Tauri CLI，`pnpm ... exec tauri dev --help` 退出 0；`tauri.conf.json` 仍指定 `beforeDevCommand=pnpm run dev`、`devUrl=http://127.0.0.1:15192`；`main.rs -> app::run -> configuration_profile` 静态链及 locked offline Cargo 全目标装配编译通过。未启动桌面应用。示例保持 HTTP false 与空 Backend 地址，但中英文 README 的位置/示例存在 B3。 |

## 失败项：返回 Development

### B1：Windows 风格环境变量未拒绝

规格 §2.3 要求 profile 拒绝变量。当前 `src-tauri/src/config/mod.rs:177` 的字面量检查只检查 `$`、`~`、`<`、`>`。在 macOS 的合成根 `/private/tmp/sma007-qa.ndUDFb/percent-variable`，将实际 `SelectedEnv`、`resolve_profile` 与 `validate_profile_path` 从交付文件原样抽取并调用：

```rust
resolve_profile(None, Some("%TEMP%/profile".into()), &root, || Ok(root.join("default")))
```

实际返回 `Ok(ResolvedProfile("/private/tmp/sma007-qa.ndUDFb/percent-variable/%TEMP%/profile"))`，预期为带 `SMA_PROFILE_DIR` 和原因的错误。验证未继续创建此目录。`%TEMP%` 是 Windows 环境变量写法，当前检查不识别该形式；Windows 的 `Path` 分支及原生运行未在本机执行，因此 Windows 结论是源码判断，不冒充 Windows 运行证据。

### B2：不可写 profile 的父目录在准入后触发日志初始化 panic

规格 §2.3 要求选择本机可用路径、准入失败时在初始化 profile 文件前以选择键和原因报错。合成根中创建 `locked/` 并设 Unix mode `0555`，以进程值 `locked/new-profile` 调用与 B1 相同的实际路径解析函数；它返回 `Ok(ResolvedProfile(.../locked/new-profile))`。在相同权限下 `create_dir_all(.../locked/new-profile/logs)` 返回 `PermissionDenied`。进一步将交付 `logging.rs` 原样装入隔离 probe，并调用 `logging::init(&profile, &defaults)`，实际发生：

```text
initializing rolling file appender failed: InitError { context: "failed to create log directory", source: Os { code: 13, kind: PermissionDenied, message: "Permission denied" } }
```

调用触发 panic 而非带 `SMA_PROFILE_DIR` 的可定位准入错误。probe 捕获 panic，确认不可写目标和默认替身均未生成；随后仅恢复**合成 fixture**权限以便后续资源管理。此证据不涉及用户路径。

### B3：路径说明与双语示例未满足获批文档合同

`README.md:41` 称 `.local/dev` 与 `./.local/dev` “both refer to the selected `.env` directory”，字面指向配置文件所在目录本身；代码及中文 README 均以其作为**基准**，实际结果是该目录下的 `.local/dev`。规格 §2.5 要求 SMA 中英文 README 与 `.env.example` 展示 `./.local/dev` 和有效绝对路径写法；两份 README 目前只展示相对赋值，虽说明已有绝对路径可继续使用，但没有绝对赋值示例。`.env.example` 本身展示两种写法。此项影响使用者推导实际目录和与获批规格逐项对照。

## 命令与结果

以下命令均在 SMA 工程目录，涉及 profile 的命令均使用上述隔离环境。退出码是本轮实际结果。

| 检查 | 结果 |
| --- | --- |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` | 退出 0。 |
| `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests -- --test-threads=1` | 退出 0；5 项通过，内部 cwd/HTTP 子进程通过；包含真实合成 SQLite/日志/偏好读写与重开。 |
| `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --test startup_cleanup_tests v1_mapping_survives_and_legacy_segment_is_inert_and_preserved -- --exact` | 退出 0；1 项通过。该目标仅运行明确指定测试，未运行同文件的 loopback 监听测试。 |
| `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --all-targets` | 退出 0；编译普通 Rust 二进制和测试目标，未运行或打开窗口。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false exec tauri dev --help` | 退出 0；仅查询 CLI 帮助，不启动 dev server 或应用。 |
| `TMPDIR=<任务临时根>/tmp pnpm --config.verify-deps-before-run=false --config.update-notifier=false build --outDir <任务临时根>/frontend-dist --configLoader runner` | 退出 0；`vue-tsc --noEmit` 与 Vite 构建通过。外部 outDir 不自动清空、依赖 PURE 注释位置及 >500 kB chunk 为构建警告。输出位于新建任务临时根。 |
| `rustc --test --edition=2021 <任务临时根>/probe.rs ...` 后执行五项隔离 probe | 退出 101；3 通过、2 失败，精确失败为 B1/B2。代码由当前候选 `config/mod.rs` 原样抽取核心解析函数，并在临时根构造夹具；并非将复制结果替代交付源码。 |
| 同一 Rust probe 单独运行 `unreadable_env_files_are_rejected_without_profile_writes` | 退出 0；1 通过，普通与显式不可读文件均拒绝，默认/选择目录不存在。 |
| `rustc --test` 独立组合交付 `logging.rs` 与抽取的路径函数，再运行 `actual_logger_after_profile_permission_admission` | 退出 0；1 项通过，测试的预期正是捕获 B2 的 panic，不能理解为 B2 通过。使用本机已缓存的锁定依赖 rlib。 |
| 触达七文件 `git diff --check`；两份 README、规格及开发记录的相对路径链接检查 | 均退出 0；20 个本地路径链接存在，未检查远程链接或锚点。 |

## 结论、限制与后续 gate

- **Verdict: `qa_failed`**。AC01、AC02、AC04 通过；AC03、AC05 失败。B1–B3 返回 Development 按已批准 r1 返工，补充定向覆盖并形成新的精确 `developer_handoff`；之后必须启动新的 fresh-context Verification，对修复及相关回归独立复验。此轮没有未解决的环境 blocker，失败并非 `qa_blocked`。
- 本轮未运行完整 Rust 测试套件中无关的 loopback 测试，未做原生 GUI、Windows 主机或打包验证；普通启动证据限于 CLI 帮助、配置/调用链检查、离线前端构建和 Rust 普通装配编译。未发真实 GET、POST，未监听 HTTP，未接外部 API、真实设备或部署。SMA-005 的原生 GET 留给 Human Owner；POST 未授权，SMA-006 仍是草案。QA 不能代替 Human Owner 最终验收。
- Verification 自有 `/private/tmp/sma007-qa.ndUDFb` 保存合成探针、fixture、target clone 和前端构建；Development 的 `/private/tmp/sma007-dev.cdLuXx` 是另一个已交接资源。本文件已保留失败复现输入和关键输出，不以临时路径为唯一证据。Verification 不执行资源回收；协调者在完成返工、复验及 Human Owner 最终决定后，核对用途与占用，按任务资源规则回收自有临时根。

---

# SMA-007 r1 独立验证：第二轮 QA（rework-1）

## 候选、独立性与环境

- 本轮为 Development rework-1 完成之后的新 fresh-context Verification；重新读取根及 AW/SMA 规则、双语 README/PLAN、canonical workflow、完整 bundle、实际实现与 diff，并按 `project-governance`、`rust-runtime`、`desktop-tauri` 验证。上方 QA1 原文及 B1–B3 保留。本轮仅写此 checklist，合同不声称平台 ACL 或强制路由。
- 批准的 `spec.md` SHA-256 `a1279b219a3f0c54b74c2b015ba1ce09c66c0020eea902b78500105416b4cc77`；最新 rework-1 `tasks.md` SHA-256 `da62ab0ea6e42963cb02701aa09cec7799f3fd1f4799fc32767e10a73e2003fd`；本轮写入前 QA1 checklist SHA-256 `3f490f020a49f295480d26e92863535d084f9aacf210c6cb5bc62f2ed3f3c9db`。
- 正式交付树 HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`。七项当前 SHA-256 逐项等于 rework-1 交接 after，依次为 `.env.example` `f16f164a71f86229943886e30c7288ca2ae32f1a4fb5676e238c5a85dfb509d0`、`README.md` `8aca75a4c084b217160e5189167beefb3930f0da84cc94891a11595e6a7e7afb`、`README.zh-CN.md` `701a73d7e7104bdd7ec9ac00919d8988bcad3b96e2d3fd4f9aca33f4a798fd30`、`config/mod.rs` `156757fff6738ffee76d4d5c7aff078aab8174b8fe44359709b8492d645167ca`、`app.rs` `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b`、`logging.rs` `d41fff70cb775bc6c090c5f3847085cecdf89ee616c08b0e59b20ddfcc291d8c`、`runtime_startup.rs` `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b`。七文件从 HEAD 的当前完整 diff SHA-256 为 `a9f0b44e96bea02adea84eb0b04882fc1aeaf5a6ae7825d2e06577ee444e1be6`；HEAD 七文件逐项与首次交接的 before 一致。工作树有其他任务既存并行差异，不能将其全部归给 SMA-007。
- macOS Darwin 24.6.0 arm64，UID 501，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。以正式源码执行定向 Cargo 命令，`--offline --locked`；`SMA_ENV_FILE` 指向本轮空合成文件，`SMA_PROFILE_DIR` 为空，`SMA_HTTP_ENABLED=false`，`SMA_BACKEND_BASE_URL` 为空；`TMPDIR` 与 `CARGO_TARGET_DIR` 指向本轮专用 `/private/tmp/sma007-qa2.jp6ARc`，target 是现有构建缓存的 APFS clone。未读取或写入真实默认或用户 `.env`、`.local/dev`、profile、其他应用数据；未启动 GUI、监听网络或发 GET/POST。

## QA1 返工项处置

- **B1 原复现已关闭，仍需处理 F1。** 正式源码定向测试验证进程值及文件值的 `%TEMP%/profile` 拒绝，进程 `%APPDATA%` 和 `%ProgramFiles(x86)%` 也拒绝；本轮独立探针再次验证 `%TEMP%/profile` 返回 `SMA_PROFILE_DIR_LITERAL_REQUIRED`，普通 `100%/profile` 获接受。不同于所选值中的变量标记，F1 涉及已有基准/系统路径被误判。
- **B2 原始 0555 与日志 panic 复现已关闭，但准入仍有 F2。** 正式源码定向测试验证 0555 目录及其未创建子目录被 `SMA_PROFILE_DIR_NOT_WRITABLE` 拒绝，0666 上级被 `SMA_PROFILE_DIR_NOT_SEARCHABLE` 拒绝；另以已通过解析的 profile 中的普通文件 `logs` 触发真实 rolling appender 初始化失败，确认返回包含 `SMA_PROFILE_DIR_LOGGING_UNAVAILABLE` 的错误、无 panic、无配置库或启动偏好文件。F2 的真实不可写权限组合未被这个测试覆盖。
- **B3 已关闭。** 中英文 README 均有 `SMA_PROFILE_DIR=./.local/dev` 和绝对路径赋值，明确结果是所选 `.env` 目录**下的** `.local/dev`，且写明进程优先、显式文件基准、失败核对；`.env.example` 包含两种示例，HTTP 默认 false、Backend 为空。

## 新发现：返回 Development

### F1：已有配置文件基准或默认应用数据路径被当作变量

`src-tauri/src/config/mod.rs:153–172` 先把相对选择拼到所选文件的父目录，`177–180` 又对**整个拼接后绝对路径**执行变量标记检查；`235–242` 对没有 profile 覆盖、由应用提供的默认路径也执行同样的字面检查。规格 §2.1–2.3 要求绝对可读普通配置文件有效、普通相对选择以其父目录为基准，以及两处为空时使用既有应用数据目录。

在任务自有临时根中创建真实目录 `%EXISTING%` 和其下普通文件 `selected.env`，文件内容为 `SMA_PROFILE_DIR=./.local/dev`。从当前交付 `config/mod.rs` 原样抽取 `SelectedEnv`、`validate_profile_path`、`contains_windows_variable` 和 `resolve_profile`，以该文件绝对路径为 selector 调用：

```rust
resolve_profile(Some(selected_env.into()), None, &root, || Ok(root.join("default")))
```

实际为 `Err("SMA_PROFILE_DIR_LITERAL_REQUIRED")`，而所选值只是普通相对字面路径，预期为该真实文件父目录下的 `.local/dev`。将同一个普通相对值放在进程选择、文件中放另一值，实际同样被拒绝；非空进程值不能按合同相对所选文件定位。另以两处无值调用 `resolve_profile(None, None, &root, || Ok(root.join("real$literal")))`，实际也返回相同错误，而该绝对路径是注入的系统默认路径替身，并非用户输入变量。本项不要求接受所选值本身的 `%TEMP%`，该值应继续拒绝。上述是 macOS 合成字面目录和注入替身的实测，不冒充 Windows 或真实用户目录验证。

### F2：当前用户无法写入的 0557 目录仍通过 profile 准入

在本轮临时根创建当前 UID 拥有的 `locked`，设置 Unix mode `0557`：owner 无写位、other 有写位。以当前用户调用 `create_dir(locked/actual-io)` 实际返回 `Permission denied (os error 13)`。同一目录、同一权限下，用从当前交付源码原样抽取的 resolver 调用：

```rust
resolve_profile(None, Some("locked/new-profile".into()), &root, || Ok(root.join("default")))
```

实际为 `Ok(ResolvedProfile(.../locked/new-profile))`；预期在日志、SQLite 与启动偏好初始化前以带 `SMA_PROFILE_DIR` 及原因的错误拒绝。原因是 `config/mod.rs:212–215` 只看 `permissions().readonly()`；此模式存在 other 写位所以它为 false，但当前进程按 owner 权限实际不可写。探针在断言前恢复了**合成目录**原权限，随后检查不存在 `actual-io`、`new-profile`、`logs`、`configuration.sqlite3`、`runtime-startup.json` 或默认替身。不要将仅检查所有写位是否全零等同于当前用户的实际可用性。ACL、不同文件系统与 Windows 的权限语义不由本机这一个 mode 测试证明。

## 本轮验收矩阵

| AC | 结果 | 本轮证据 |
| --- | --- | --- |
| AC01 | 通过 | 正式源码定向测试覆盖普通合成根下 `.local/dev`、`./.local/dev`、等价绝对值、缺失普通文件时的相对进程值，以及不同 cwd 和无关 cwd 下 `.env`。 |
| AC02 | **失败** | 一般合成路径下文件/进程优先、空白及默认替身、HTTP/Backend 来源与默认关闭均由正式测试通过；F1 表明合法所选文件父目录及合法默认替身含特定字面字符时，相对值或默认选择被错误拒绝。 |
| AC03 | **失败** | 一般无效 selector、上级路径、变量、非目录与符号链接，以及 0555/0666 和真实日志失败均通过相应定向断言；F2 中本机实际不可写目录仍通过准入。Windows 分支未原生运行。 |
| AC04 | 通过 | 正式定向测试在同一合成绝对根实际写入并重开 SQLite revision 1、完整 snapshot、JSONL 日志和启动偏好；另一合成 profile 为 revision 0。另一个精确 v1 测试验证加载不改原始偏好字节、保存保留惰性旧段。无真实用户数据。 |
| AC05 | **失败** | B3 的双语示例、路径文字及示例默认值已修正；Tauri CLI help、配置/调用链和 Cargo 全目标编译通过。但 F1 使 README 所述的选定文件父目录语义对合法基准不总成立。按授权未打开应用，CLI help/编译不能证明 GUI 或原生手工启动。 |

## 本轮命令与结果

以下工作目录为 SMA 工程根；Cargo 测试与检查均使用上面的合成选择、离线锁文件及本轮临时目录。

| 命令或检查 | 结果 |
| --- | --- |
| `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests -- --test-threads=1` | 退出 0，7 项通过；内部 cwd/HTTP 子进程各通过。该测试调用正式配置、SQLite、日志和偏好实现。 |
| `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --test startup_cleanup_tests v1_mapping_survives_and_legacy_segment_is_inert_and_preserved -- --exact` | 退出 0，1 项通过、2 项未选；不运行该文件中的其他测试。 |
| `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --all-targets` | 退出 0；只编译，未启动桌面。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`、七候选 `git diff --check` | 均退出 0。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false exec tauri dev --help` | 退出 0；只显示 CLI 帮助，无 dev server。 |
| 独立抽取当前生产 resolver 的 `rustc --edition=2021 --test .../resolver_probe2.rs` 与 `QA_DIR=<任务根>/repeat .../resolver_probe2 --test-threads=1 --nocapture` | 编译退出 0；执行退出 101，1 项通过、4 项失败：F1 文件相对值、进程相对值、默认替身各 1 项，F2 owner 目录不可写 1 项；所选 `%TEMP%` 拒绝与字面单个 `%` 接受 1 项通过。抽取段及具体调用已在上方列出，临时 probe 不代替正式树或其测试。第一次编译 probe 时环境变量只对前一命令生效，导致查找 `/resolver_probe.rs` 退出 1；更正命令后才得到上述结果，该错误不属于产品缺陷。 |
| 双语 README、spec、tasks 的相对路径链接检查 | 退出 0，21 条本地路径存在；未验证远程链接和锚点。 |

## Verdict 与 handoff

**Verdict: `qa_failed`。** F1 和 F2 是本次精确 r1 范围内的可复现实现缺陷，返回 Development 返工；返工应保留 QA1/QA2 历史、记录新的精确候选和自检，再由新的 fresh-context Verification 独立复验，之后才交 Human Owner 最终验收。没有环境 blocker；不能把本结论写成 `qa_passed` 或 Human Owner 验收。SMA-005 GET 留给 Human Owner 手工执行，POST 未授权，SMA-006 继续是草案。

本轮没有运行广泛 Rust HTTP 旧 fixture、原生 GUI、Windows 主机、打包、真实网络、设备或业务投递。原有 profile 和并行任务未由本轮修改。本文件保存关键输入、实际结果和 source hash，不以临时文件作为唯一证据；`/private/tmp/sma007-qa2.jp6ARc` 含合成 probe、fixture 与 target clone，留待协调者在完成后续复验和 Human Owner 决定、核对无占用及证据依赖后按任务资源规则回收。


---

# SMA-007 r1 独立验证：第三轮 QA（rework-2）

## 候选、边界与独立性

- 本轮为 Development rework-2 交接后的新 fresh-context Verification，独立读取根及 AW/SMA 契约与双语 README/PLAN、canonical workflow、完整 3MD bundle、交付源码、七文件 diff 与现有 Development/QA 输出；采用 `project-governance`、`rust-runtime`、`desktop-tauri` 并检查触达源码文件头。Verification 在仓库内只更新本 checklist；本 profile 为 `contract_only`，不声称平台 ACL 或强制路由。
- Human Owner 于 2026-11-16（Asia/Shanghai）批准 **SMA-007 r1**。规格 SHA-256 `a1279b219a3f0c54b74c2b015ba1ce09c66c0020eea902b78500105416b4cc77`；最新 `tasks.md` SHA-256 `3d5e0a71b051887558c68022ad4de75981689faf23ec48350462a85205586691`；本轮写入前 checklist SHA-256 `15f5544edae60f7c2595105b4cec14b94c5e9118374ee917b4d9f0296996cc9a`。QA1、QA2 的正文及失败记录保持原文，仅更新文件首部当前状态与 handoff。
- 正式交付树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；七项工作树 SHA-256 均等于 `developer_handoff rework-2` 的 after，HEAD 七项内容亦逐项等于首次交接的 before。七文件 `git diff --binary` SHA-256 为 `a5e007d512fc8b5f1d742336d82ed6cc0618444012247c05f91d665296f0f9f4`。本轮验证候选：

| SMA 工程相对路径 | SHA-256 |
| --- | --- |
| `.env.example` | `f16f164a71f86229943886e30c7288ca2ae32f1a4fb5676e238c5a85dfb509d0` |
| `README.md` | `8aca75a4c084b217160e5189167beefb3930f0da84cc94891a11595e6a7e7afb` |
| `README.zh-CN.md` | `701a73d7e7104bdd7ec9ac00919d8988bcad3b96e2d3fd4f9aca33f4a798fd30` |
| `src-tauri/src/config/mod.rs` | `4c8765155af5d236c8c605c46382b8a9119360b29afcb490ef6b39bd73a7e9fe` |
| `src-tauri/src/app.rs` | `b7dd80984eb25a97ea0129bb393a2b1c82437349ec9150f4e4aa2891c0be316b` |
| `src-tauri/src/infrastructure/logging.rs` | `d41fff70cb775bc6c090c5f3847085cecdf89ee616c08b0e59b20ddfcc291d8c` |
| `src-tauri/src/config/runtime_startup.rs` | `f26d611f1bd96110ff2fd7889f3c3e4cfafaa75c1de57e28ff14d6f90f20e46b` |

工作树另有并行任务改动，不能全部归因于本任务；根 `CODE_INDEX.md` 的可见 diff 是其他 backend/frontend observation 条目，本轮未改。AW 双语 README 对 SMA profile 仍有仅绝对路径的旧描述，不属于本任务批准的七文件范围；以本任务精确候选和 SMA 双语 README 为本次验证面，不在此更改其他项目文件。

- 本轮环境：macOS Darwin 24.6.0 arm64，UID 501，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。工作目录为正式 SMA 工程；测试目标为正式源码，Cargo `--offline --locked`，`SMA_ENV_FILE` 指向本轮空合成文件，`SMA_PROFILE_DIR` 为空，`SMA_HTTP_ENABLED=false`，`SMA_BACKEND_BASE_URL` 为空，`TMPDIR`、`CARGO_TARGET_DIR` 指向 `/private/tmp/sma007-qa3.XDfAjP`。target 由 SMA 现有 target 以 `cp -cR` 克隆，仅为编译缓存；探针、合成配置、日志和数据库只在该临时根。

## 先前失败项的独立复验

- **B1、F1 关闭。** 正式源码先对实际选中的进程/文件 profile 字面值检查 `$`、`~`、`<...>`、`%...%` 和 `..`，之后才以文件父目录拼接；系统默认替身不被误作为选择值重新做变量检查。另用本轮独立 Rust probe 从候选 `config/mod.rs` 原样抽取 `ResolvedProfile` 至 `resolve_profile` 的生产段，在真实合成父目录 `base$literal/~arch<ive>%EXISTING%/custom.env` 验证文件值 `./.local/dev`、空白进程回退、进程值 `./from-process` 以及含 `$`、`%...%`、`~`、`<...>` 的注入默认替身均按约定解析；实际选择 `%TEMP%/foo`、`$HOME/foo`、`~/foo`、`<foo>`、`../escape` 和文件 `%TEMP%/profile` 均返回带 `SMA_PROFILE_DIR` 的错误；普通单独 `%` 保持可用。相对目标和默认替身没有被创建。
- **B2、F2 关闭。** 本轮 probe 在当前 UID 拥有的合成 `0557` 上级下直接 `create_dir`，得到 `PermissionDenied`；同权限时，选择该目录本身及其不存在子目录均返回 `SMA_PROFILE_DIR_NOT_WRITABLE`，已经存在且可写的子目录成功解析，并以独立文件写入/删除探针证明该子目录当前确实可写。之后检查受拒目标与默认替身无 `configuration.sqlite3`、`logs`、`runtime-startup.json`。正式源码测试还覆盖 `0555`、`0666` 与文件中相对路径。正式日志测试在已解析的合成 profile 中以普通文件占据 `logs`，观察到 `SMA_PROFILE_DIR_LOGGING_UNAVAILABLE` 错误而非 panic，且无数据库或偏好文件。
- **B3 关闭。** SMA 双语 README 和 `.env.example` 均展示 `./.local/dev` 与绝对赋值；两份 README 将结果明确描述为所选文件所在目录**下的** `.local/dev`，说明相对值基准、进程优先、已有绝对路径和错误核对。示例的 HTTP 为 `false`、Backend 为空。

## 验收矩阵

| AC | 结果 | 本轮证据与实际边界 |
| --- | --- | --- |
| AC01 | 通过 | 正式 Rust 9 项测试覆盖普通合成根的 `.local/dev`、`./.local/dev`、等价绝对值、普通文件缺失时的进程相对值、不同 cwd 与无关 cwd 的 `.env`。仅使用合成根。 |
| AC02 | 通过 | 正式测试覆盖显式合成文件、进程/文件优先、首个重复 profile 键、空白回退及注入默认替身；HTTP/Backend 文件和进程优先、显式关闭与默认关闭由隔离子进程验证。独立 probe 额外关闭 F1；无网络请求。 |
| AC03 | 通过 | 正式测试及独立 probe 验证空、相对、缺失、非普通文件、符号链接或不可读 selector，非法字面值、`..`、无效编码、非目录和 profile 上级 symlink，及当前用户真实不可写权限。错误可定位 `SMA_ENV_FILE` 或 `SMA_PROFILE_DIR`，抽查选择目录、symlink 目标、默认替身无三类 app 输出。`app.rs` 调用链在日志、配置库、偏好及窗口前解析 profile 并传播错误；logger 初始化失败有显式错误。Windows 写法的执行仅为源码检查，未做 Windows 原生测试。 |
| AC04 | 通过 | 正式测试在同一合成绝对根实际写入并重开 SQLite revision 1、完整 snapshot、日志及 v1 启动偏好；第二合成 profile 读不到首处配置。单独 v1 偏好测试确认读取保持原字节、显式保存保留惰性旧段，缺失时读取不创建。正常投递门禁见下方。 |
| AC05 | 通过（按获批离线边界） | 双语说明和示例匹配；`package.json` 的 `tauri` 指向 Tauri CLI，`tauri.conf.json` 保持 `beforeDevCommand=pnpm run dev` 与 `devUrl=http://127.0.0.1:15192`；CLI `dev --help` 和锁定全目标编译通过。未启动 GUI、dev server 或原生应用，不能把这些证据说成窗口启动或平台打包实测。 |

## 本轮命令与结果

以下命令在 SMA 工程根执行。除格式和 CLI 帮助外，Cargo 均使用上述显式合成环境；输出和 fixture 均在本轮临时根。

| 命令或检查 | 结果 |
| --- | --- |
| `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib config::startup_path_tests -- --test-threads=1 --nocapture` | 退出 0；9 项通过，另含 cwd 的 2 个和 HTTP/Backend 的 4 个隔离子进程，均通过。打印本机 0557 fixture 当前进程可创建目录为 `false`。 |
| `rustc --edition=2021 --test /private/tmp/sma007-qa3.XDfAjP/probe.rs -o /private/tmp/sma007-qa3.XDfAjP/probe`；`QA_ROOT=/private/tmp/sma007-qa3.XDfAjP/probe-fixtures /private/tmp/sma007-qa3.XDfAjP/probe --test-threads=1 --nocapture` | 编译及执行均退出 0；独立 3 项通过。probe 原样抽取当前候选生产解析段并使用与正式测试不同的合成参数；具体输入、权限观察和断言见上文，并补充 selector、不可读文件、非目录和 symlink 拒绝无 app 输出。 |
| `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --test startup_cleanup_tests v1_mapping_survives_and_legacy_segment_is_inert_and_preserved -- --exact` | 退出 0；1 项通过、2 项未选。 |
| `SMA_002_GATE_CHILD=1 SMA_002_FIXTURE_URL=http://fixture.invalid ... cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --test startup_cleanup_tests disabled_gate_blocks_saved_mapping_before_http -- --exact` | `SMA_HTTP_ENABLED=false` 和 `true` 各运行一次，均退出 0、各 1 项通过。直接选择该测试的无监听子进程分支；没有运行原测试的 listener 父分支。源码复核 manual/start/resume 的 command/service 在 client、spawn、远端读取之前拒绝，旧 startup 偏好不能授权正常投递。 |
| `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --all-targets`；`cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` | 均退出 0；check 是编译，未运行桌面。 |
| `TMPDIR=/private/tmp/sma007-qa3.XDfAjP/tmp pnpm --config.verify-deps-before-run=false --config.update-notifier=false exec tauri dev --help` | 退出 0，只查询帮助，无 dev server。 |
| 七候选 `git diff --check`；README 两份及 bundle 三份相对路径检查 | 均退出 0；22 个本地路径存在，未验证外链或锚点。 |

平台源码核对：锁定 `libc 0.2.186` 缓存中的 macOS `AT_FDCWD=-2`、`AT_EACCESS=0x0010` 和 Linux `AT_FDCWD=-100`、`AT_EACCESS=0x0200` 与候选常量一致；`winapi 0.3.9` 平台定义中的 `FILE_ADD_FILE=0x0002`、`FILE_ADD_SUBDIRECTORY=0x0004`、`FILE_TRAVERSE=0x0020`、`FILE_FLAG_BACKUP_SEMANTICS=0x02000000` 与 Windows 分支一致。Linux/Windows 的目录访问、ACL、挂载及盘符/根相对路径行为均未在对应目标编译或运行；本机仅有 `aarch64-apple-darwin` Rust target。该核对不是跨平台运行证明。

## Verdict 与 handoff

**Verdict: `qa_passed`。** AC01–AC05 在获批的离线验证边界内通过；QA1 的 B1–B3 和 QA2 的 F1–F2 均已按上述证据关闭，本轮无新增实现缺陷或环境 blocker。此结论只适用于上表精确 rework-2 候选，交 Human Owner 做最终验收，QA 不等于 Human Owner 接受。

未读取或写入用户真实 `.env`、`.local/dev`、默认或已有 profile、其他应用目录；未启动 GUI、监听器、实际 GET/POST、设备或部署。SMA-005 的 GET 由 Human Owner 自测，POST 未授权，SMA-006 仍为草案。未执行平台打包或完整含网络 fixture 的测试套件，也未在本轮运行可能读取工程 `.env` 的前端构建；这些不是对上述实际动作的成功声明。

Verification 自有 `/private/tmp/sma007-qa3.XDfAjP` 留存合成 probe、fixtures 与 target clone；上述记录保留了关键输入和结果，不以临时文件为唯一证据。Verification 不执行资源回收；由协调者在 Human Owner 决定后核对归属、占用与证据依赖，按 canonical workflow 回收任务自有资源，勿影响其他任务及真实数据。
