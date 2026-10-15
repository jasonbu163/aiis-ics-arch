Task ID: ARCH-AW-001
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner accepted ARCH-AW-001 r1 on 2026-10-14; coordinator to synchronize indexes and close out
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# 独立验证记录

验证日期：2026-10-14。实际命名 Verification 在 fresh context 接收精确 r1 handoff，未继承 Development 对话推理；独立读取根 AGENTS、README/PLAN pair、verification.toml、canonical workflow、完整 spec/tasks、当前实现、diff 和可用日志。角色 profile 是 `contract_only`，不代表平台 ACL 或强制路由。

本轮遵循 spec §9 的 Human Owner 最新口径：确认工程迁入后可构建、独立启动、必要来源与配置隔离，SMA 映射 runtime 在位。QA 亲自执行定向静态核验，复核已有 DEV 构建／原生证据；没有重新构建、运行测试、启动应用或验收临时 UI。适用 shared skills：aiis、project-governance、desktop-tauri、rust-runtime、frontend-ui、i18n-workflow、code-document-indexer；未扩大验证矩阵。

## 对象与环境

- 本仓 `main` dirty working tree，HEAD `363b297bffe65e020108f5504766b4fb1ec3b381`；DTB `main` HEAD `a87c107c10e8d9d9d3e389e357b50d203d2aebf7`，TSS 子目录 status 无输出。全仓其他 dirty 内容与并发 ARCH-BE-005 不归本任务。
- macOS / Darwin arm64；Node `v22.19.0`、pnpm `11.11.0`、Cargo `1.89.0`。QA 的 Python `3.9.6` 仅用于读取、哈希和 JSON 核验，未用作项目运行环境或安装依赖。
- 读取时 spec SHA256 `af9f33f6c42e4a9744987fa57a11ab7deea66c35fa6e8de1c52e0a87717e7145`；tasks SHA256 `289dfe0b13aa38129bf14f5518a67c79391fd6be104e5af31b6d2affe01ea43b`。批准状态 `owner_approved`，实施状态 `developer_handoff`，Task ID / Revision 一致。

## 验收结果

| AC | 结果与证据 |
| --- | --- |
| AC1 | 通过。tasks 的 CA 158、TSS 278、SMA copy/exclude 278、freeze 158、最终 486 项清单完整读取，均与对应临时 JSON 一致；原 TSS 当前 278 项哈希全部相同。来源、排除及 ignored 保全记录存在；新副本未纳入来源真实配置／客户工件。 |
| AC2–3 | 通过。原 `control-agent/` 已迁出；158 项来源匹配本仓 HEAD，只有四份 README/PLAN 说明改变，其余 154 文件字节相同。当前 CA 158 项匹配 freeze，清单 digest 为 `a30495875a1dff6cdc4dc0008b0b7cc07a576fcc40bb8e994e833bfacd759648`。tasks receipt 05:40:37 UTC 先于 DAA 复制 05:41:04 UTC；迁后全新 target 构建和原生 IPC 证据可用。 |
| AC4 | 通过。DAA 独立工程、采集/诊断源码和既有 headless 入口保留；独立 debug 构建与 51 passed / 1 ignored 的 DEV 日志存在，headless 门禁拒绝及关闭结果记录在 tasks。README 明示旧 raw/latest 实现及新 AW API 尚未接入。 |
| AC5 | 通过。SMA `domain/mapping_runtime/`、`services/mapping_runtime/` 与 app.rs 的 manual/API-first runtime command 注册存在；SQL infrastructure、legacy Projection/service_mapping 目录已排除。DEV 纯计算／本地夹具结果为 8 Simulation、11 continuous Mapping、2 manual Mapping 和 2 前端隔离/组包测试通过。此项不等于完整 TSS 功能验收。 |
| AC6 | 通过。QA 读取三个 package/Tauri/Vite 身份与端口，符合 r1；DEV 六端口证据为各自 HTTP 200、产品 title 正确、重复占用 exit 1。CA preview 使用文档化的 `pnpm preview --strictPort`，冻结源码原配置保留；DAA/SMA 源配置均 strict。 |
| AC7–8 | 通过。QA 核对 DAA/SMA 自身根或显式 ENV_FILE、独立 PROFILE_DIR 实现；DEV 自身 cwd、src-tauri 和污染父目录临时 cwd 的证据明确未拾取旧变量/profile。native 日志的临时 profile 分离、数据库/PLC 关闭与 SMA auto-start=false 一致；原 TSS 哈希不变。退出和六端口释放复用 DEV 记录。 |
| AC9 | 通过。QA 复核现有三份 .app 的 Info.plist 身份及 native JSON Lines；CA/DAA snapshot 显示 DB 关闭、PLC sample 未执行；SMA preferences 两 auto-start=false，OpenAPI 拒绝事件为 `SMA_EXTERNAL_IO_DISABLED`。分别/同时窗口、IPC、逐个退出且其他实例继续运行的观察归 DEV tasks §原生与配置隔离实证，QA 未重新操作原生 UI，也未把浏览器结果当原生证明。 |
| AC10 | 通过。三份 native-build 日志均含 Vite 完成、Cargo `Finished`、新应用路径与 bundle 完成；CA 迁后 49 passed / 1 ignored，DAA 51 passed / 1 ignored，SMA 上述回归通过。独立工程不依赖原 CA/TSS checkout；SMA 帮助已局部化，DEV 链接检查无缺失。 |
| AC11 | 通过。已读 AW 双语 README/PLAN/catalog 及两新工程 README；唯一 bundle 指向根 plans，当前工程初始化与未来 S1/API/闭环/shared UI/SQLite/现场 gate 有区分。CODE_INDEX 包含 AW 三工程；根机械索引由主协调在本 verdict 形成后同步。 |
| AC12 | 通过。本轮仅写本 checklist。最终清单 digest `2fbf09a4d61fce4a2da2bd5e374e8db5b66c0f0400632384b8217811379693c8` 可复算；当前 485/486 文件匹配，唯一差异 CODE_INDEX.md 是主协调确认的并发 ARCH-BE-005 共享文档更新，AW 索引仍在，无运行源码漂移。未覆盖其他任务、修改实现或代替 Human Owner 接受。 |

## 亲自执行与复用证据

QA 亲自执行：`git rev-parse HEAD`、两个仓库 `git branch --show-current`、DTB `git status --short -- twin-state-studio`；`python3 -B` 读取完整 tasks 并解析五组清单、逐文件 SHA256、对 CA 来源执行 `git show HEAD:control-agent/<path>`、复算清单 digest、读取 package/Tauri/Vite/config/app.rs、解析现有日志与 .app Info.plist。定向核验完成；首次最终清单的严格一致断言因共享 CODE_INDEX 差异退出 1，识别并获主协调确认后按该唯一已知并发差异重核退出 0，未修文件。`git diff --check` 无输出，通过。

复用 DEV 真实命令及退出结果：三工程 `pnpm build` / `cargo fmt ... --check` / `cargo test ... --locked`，以及各自 `CARGO_TARGET_DIR=<临时 target> pnpm tauri build --debug --bundles app --config <临时 incognito.json>` 均记录 exit 0。QA 读取的原始日志包括 `ca-after-app-build.log`、`daa-native-build.log`、`sma-native-build.log`、`ca-after-test.log`、`daa-test.log`、`sma-test.log`、`sma-ui-isolation-test.log`、各 own/temporary/final-native.log 和 `ports-results.json`；结果与 tasks 摘要一致。这些是 DEV 已运行结果，不能表述为 QA 亲自重跑。

## 限制、资源与 verdict

- **Verdict：qa_passed。Blocker：无。** 未发现阻断本 r1 工程迁移、构建或独立启动的实现 failure；无需退回 Development。
- 只确认当前 macOS debug 工程基线。旧 UI 后续调整；完整 TSS 产品功能、签名安装包、Windows/Linux、release、长期现场可靠性、真实 PLC/DB/Backend/Target、业务闭环均未验收。SQLite、AW 新 API、shared UI 仍属后续任务。
- 全仓旧 governance checker 的历史多 Revision/catalog 兼容问题已有 spec 记录，本轮未重跑或修复。ScreenCaptureKit -3812 为 DEV 截图工具限制；已有 AX/IPC/窗口证据保留。QA 的 `pgrep` 被当前环境拒绝（sysmond 不可用），故不把它写成独立进程释放证明；本轮未启动任何运行资源，退出事实依据 DEV 记录。
- `/private/tmp/ARCH-AW-001-r1-development/` 的日志、清单、临时 profile 与 debug target 保留供 Human Owner 审阅；关键事实已回写 tasks/checklist，不以临时文件作为唯一记录。QA 不清理资源。

## Human Owner 最终验收

Human Owner final acceptance：**owner_accepted，2026-10-14**。Human Owner 实际原话：

> 可以，ARCH-AW-001 r1 验收通过，更新状态收尾就行，不用再追加测试了。

本轮仅机械记录该最终验收，未追加测试、构建、哈希检查、应用或 UI 操作；原 `qa_passed` verdict、证据及上述未验证边界保持不变。现有临时证据保留供尚未提交的工作树追溯，不做删除；索引由主协调同步。该验收不授予发布、部署、Git/GitHub 推送、数据库或现场操作权限。
