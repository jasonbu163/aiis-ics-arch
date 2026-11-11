Task ID: DAA-011
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 aiis-ics-arch::DAA-011 r1，交 Development 按本规格更新中英文手册
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 项目开发环境人工操作指南与历史联调入口的校正
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本稿第 6 节与 Development Lifecycle Workflow
Related Task: aiis-ics-arch::DAA-007, aiis-ics-arch::DAA-008, aiis-ics-arch::DAA-010, aiis-ics-arch::ARCH-ACQ-003
Created: 2026-11-11 Asia/Shanghai

# DAA 项目 dev 手动操作指南校正

## 1. 目标与依据

两份阶段 C 手册仍把 B-RUN-01 的 M01 放在开头并写成当前步骤。把项目 dev 的人工操作放在首段，保留 B-RUN-01 的历史过程及证据。用户可从现在的 DS 和 DAA 源码入口直接完成一轮本地采集核对，并能辨认新版上报的接续条件。

- DAA-007 r2 的受控 DS 采集已获验收。DAA-008 r4 的 B-RUN-01 是旧 `plc-facts/v1` 运行记录，使用专用 relay `18281`。历史记录包含首次可靠确认，按 DAA-008 原范围解释。 [阶段 B 验收](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [旧联调记录](../DAA-008-reliable-facts-upload/tasks.md)
- 当前 DAA HTTP 适配器仍使用 `plc-facts/v1` 的 `/batches`。ARCH-ACQ-003 r2 的 `plc-facts/v2` provider 已验收，指定项目 dev 使用 MySQL `3307`、API `8000`、Web `5190`。DAA-010 仍为草案，接入与端到端验收由 DAA-010 承接。 [DAA 当前适配器](../../src-tauri/src/infrastructure/facts_http.rs) · [后端验收及交接入口](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) · [新版 provider 合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) · [DAA-010 草案](../DAA-010-sample-facts-upload/spec.md)
- 本机若有 ARCH-ACQ-003 r2 的操作交接材料，可用 `backend/data/maintenance-evidence/arch-acq003-r2-dev3307/DAA-010-provider-handoff.zh-CN.md` 交叉核对。手册的 provider 链接以已跟踪的合同及验收记录为入口。

## 2. 编号需求

- **R01 当前入口。** 在中英文现有手册开头增加项目 dev 路径和顺序。正文区分 `database-only` 加 backend/frontend 源码运行，以及 Human Owner 已启动的项目 dev Compose。列清 API `8000`、MySQL `3307`、Web `5190` 和模拟 PLC `31281` 的用途，遇到实际端口覆盖时按已启动项目配置核对。数据库和服务初始化链接到项目既有文档。
- **R02 本地采集。** 给出一台模拟 PLC、一个 DB、三个点的最短操作。每个桌面应用使用各自项目根 `.env` 选择各自 `.local/dev`，空 profile 先创建根目录，启动命令统一 `pnpm tauri dev`。说明继承的选择变量优先级、首次空列表、既有兼容 profile 复用，以及应保留的 `.local` 配置、样本和归档。手册可展示项目内相对位置和绝对路径模板，真实 `.env` 内容和凭据留在本机。
- **R03 上报接续。** 当前可执行步骤停在 DS → DAA → SQLite。新版接续小节说明 DAA-010 完成适配且获准联调后，向项目 dev API 的 `POST /api/v1/integration/plc-facts/samples` 写一个完整 DB 样本，实时和补传共用接口。列出登记来源、机器凭据、可靠提交回执与 Web 实时数据及采集历史的核对入口。实际接口参数和故障用例引用 DAA-010 与已验收的 provider 合同。
- **R04 历史与双语。** 将旧手册正文放在显眼标记的“历史记录 · DAA-008 B-RUN-01”区，明确其原地址、命令和资源用于追溯。保存 `m01-launch` 等已有锚点、历史命令、核验数据与留存约束。替换正文最上方过时的“当前执行 M01”提示，两种语言的当前步骤、历史定位和后续边界保持一致。

## 3. 中文操作稿

1. **项目 dev。** 日常人工联调用已启动的 `database-only` MySQL、项目 backend 和 frontend 源码。若这套环境需要启动源码进程，在各自目录执行 `uv run run.py` 和 `pnpm dev`。已启动项目 dev Compose 时，沿用该栈。按实际环境核对默认地址，后端 `http://127.0.0.1:8000`，Web `http://127.0.0.1:5190`，MySQL `127.0.0.1:3307`。 [宿主机源码开发与 database-only](../../../../INITIALIZATION.zh-CN.md#宿主机源码开发与-database-only) · [项目 dev Compose](../../../../INITIALIZATION.zh-CN.md#源码开发栈)
2. **启动 DS 和 DAA。** DAA 的 `.env` 将 `DAA_PROFILE_DIR` 指向本项目 `automation-world/data-acquisition-agent/.local/dev` 的绝对路径，DS 的 `.env` 将 `DS_PROFILE_DIR` 指向本项目 `automation-world/device-simulator/.local/dev` 的绝对路径。新空目录先在对应模块执行 `mkdir -p .local/dev`，两个终端标签各在对应模块执行 `pnpm tauri dev`。若曾导出 `DAA_ENV_FILE`、`DAA_PROFILE_DIR` 或 `DS_PROFILE_DIR`，先检查对应终端是否仍选中了旧目录。空 profile 的实例和 PLC 列表初始为空，已有 dev 配置可复用。保留 `.local` 下的其他 profile、历史和归档，切换时仅选择单独的目标目录。 [DAA 启动与存储](../../README.zh-CN.md) · [DS 启动与存储](../../../device-simulator/README.zh-CN.md)
3. **DS 建一台模拟 PLC。** 在“配置中心 → 实例”新增 `DEV-PLC-A`，S7 `127.0.0.1:31281`，rack `0`、slot `1`，Calling TSAP `256`、Called TSAP `257`。在“DB 点位”同时选择样例文件，只选 `MinimalImport`，填 DB 号 `21`，确认标准地址及点位命名，核对 DB 长度 `8`。启用 DB 和三点，允许客户端读取，选择“保持”和“无写入 owner”，关闭写入，显式确认三个初值 `false`、`0`、`12.5`。保存草稿，保存为版本，停机加载该版本并在工作台启动。 [minimal.db](../../src-tauri/tests/fixtures/source-import-minimal/minimal.db) · [minimal.udt](../../src-tauri/tests/fixtures/source-import-minimal/minimal.udt)
4. **DAA 采几秒。** 在“PLC 配置”添加并启用同一 S7 端点。在“点位与采集组配置”导入同一文件对并填 DB `21`，预览标准布局偏移并确认。核对 `payload.ready` 为 BOOL `0.0`，`payload.count` 为 INT `2`，`payload.temperature` 为 REAL `4`。三个点启用并分到同一个 `1000 ms` 采集组，保存草稿并激活配置。在工作台连接、开始采集约 5 秒、暂停，到“上报与存储 → 本地历史”查询 DB21，打开一份样本核对三点值和质量。上报保持停止。
5. **等新版接入后再核上报。** DAA-010 适配并明确联调范围后，按新版合同在同一项目 dev 后端登记测试来源与机器凭据。用 API `8000` 上报，取得匹配的 `committed` 回执（`created` 或 `duplicate`），再登录 Web `5190` 的“采集数据 → 实时数据”和“采集历史”核对。正常投递、断网补传、回执丢失后的原字节重试及重启恢复由 DAA-010 的独立联调验证。 [新版 provider 合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)

## 4. 写入范围与回退

- 正式交付文件仅 `automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md` 和 `automation-world/data-acquisition-agent/STAGE_C_GUIDE.md`。以实施开始时两份手册的当前工作树内容为基线，保留并行改动，记录文档候选差异。
- 本任务角色记录限定于 `plans/DAA-011-dev-manual-refresh/{spec,tasks,checklist}.md`。协调方所需的机械索引限定于 DAA 的 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` 中本任务一行或链接，状态须与本任务证据一致。
- 排除运行代码、测试源码、用户配置、SQLite/卷/数据库、API 调用、Docker 或桌面运行操作，以及历史 profile/资源清理。DAA-008 记录、DAA-010 规格与实现、其他任务记录均属各自范围。文档回退只逆转本任务增量，保留实施前已有改动。

## 5. 验收标准

| 编号 | 通过标准 |
| --- | --- |
| AC01 | 双语手册首屏标明当前可运行的是本地采集。两种项目 dev 运行方式、默认端口的用途、各自 `.env` 选择、空目录初始化、`pnpm tauri dev` 与归档保留含义一致。 |
| AC02 | 对照现有源码及样例静态走读单 PLC 步骤，核对端点、DB 号、三点类型和地址、分组周期、版本加载/激活、查询点和值。无需新建 profile、启动 DS 或重跑阶段 B。 |
| AC03 | 新版接续只作为 DAA-010 后续条件。公开合同、验收记录和项目启动说明链接可达，路径、机器凭据、回执和 Web 核对入口与接受的 provider 一致。 |
| AC04 | B-RUN-01 的原历史地址、历史正文和既有锚点完整；跨语言、相对链接、可复制命令语法和改动边界通过独立文档核验。 |

## 6. 交接与 Revision

Human Owner 批准精确 r1 后，Development 按 `project-governance` 与项目 STD 制作两份文档增量，记录自检与交接。fresh-context Verification 对照两份手册、旧正文基线和 repo 权威文档，核对链接、命令、双语与写入范围并出具 checklist。交付进入 Human Owner 最终验收；阶段 C 和资源清理沿各自的任务处理。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)

| Revision | 记录 |
| --- | --- |
| r1 | 2026-11-11（Asia/Shanghai），Human Owner 精确批准文档范围，交 Development。 |

### r1 精确范围批准

2026-11-11（Asia/Shanghai），本任务协调方转交 Human Owner 的批准原话：

> 批准 aiis-ics-arch::DAA-011 r1，按 spec 更新 DAA 中英文操作手册并做独立文档核验

批准对象为登记前的完整 r1 草案，已核对 SHA-256 `d5bfd02d436daa32ac3e7c7d4bb31bb0f78df8e84109cb6903ed0b086fb86db2`。本次登记包含批准状态、记录与交接。Development、独立文档核验及 Human Owner 最终验收按第 6 节接续。
