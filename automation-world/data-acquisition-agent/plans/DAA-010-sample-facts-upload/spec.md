Task ID: DAA-010
Revision: r5
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 DAA-010 r5 实施及第 6 节两轮 Mac 隔离运行。主-DAA 交 Development 实施和自检，先完成 Mac 受控链路，Windows 原生验证后续实测。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 按完整 DB 样本上报新采集事实、断网补传、可靠确认和本地运维
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本稿第 5 至 8 节与 Development Lifecycle Workflow
Depends On: ARCH-ACQ-003 r2 已验收 provider 范围及本稿第 2 节锁定的开发合同
Related Task: ARCH-ACQ-001, ARCH-BE-012, DAA-007, DAA-008, DAA-011
Created: 2026-11-10 Asia/Shanghai

# DAA 按完整 DB 样本上报

## 1. 本轮目标

复用现有采集、双 SQLite 保存机制和界面组件。DAA 先在本地保存完整采集轮，再按一份 DB 样本一个 POST 发送。实时发送和补传共用样本身份、正文和回执规则。用户从「上报与存储」页查看运行状态、处理异常和管理本地存储，并可配置服务地址及上报接口路径。

Human Owner 已确认本会话草图的界面和接口配置方向。此前 dev 的少量旧验证样本本轮不补传，PLC、DB 和点表可以按常规界面重新配置。第 3 节规定同目录存储兼容和历史保护，第 6 节的测试 profile 仅供隔离验证。产品面向 macOS 与 Windows，先完成 Mac 受控真实链路，后续由 Owner 在 Windows 测试机实测。Human Owner 对 r5 的范围批准见第 8 节。

DAA-007 r2 的受控 S7 → SQLite 是本地采集基线。DAA-008 的 `plc-facts/v1`、旧 `/batches`、B-RUN-01 与其回执按历史合同留存。DAA-011 r1 双语指南核验和 r3 Development 的候选、自检及暂停保持各自记录。 [根级路线](../../../../plans/ARCH-ACQ-001-acquisition-data-coordination/spec.md) · [DAA-007 验收](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-008 记录](../DAA-008-reliable-facts-upload/checklist.md) · [DAA-011 记录](../DAA-011-dev-manual-refresh/checklist.md) · [r3 Development 记录](tasks.md#scope-review--human-owner-clarification-2026-11-12)

## 2. 提供方与开发合同

**R01** 沿用 r3 已获准的前置调整。ARCH-ACQ-003 r2 于 2026-11-11 验收 QA2 核对的 provider、合同及指定 dev 交付，40 文件清单 SHA-256 为 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。验收后后端按独立 DIRECT 调整开发合同，样本 POST 和五个 GET 免 Bearer。r5 使用下列经摘要复核的合同和源码增量。ARCH-BE-012 r4 仍为 `qa_blocked`，其原隔离 B 矩阵、清理、容量及终验仍归原任务。 [ARCH-ACQ-003 验收](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) · [ARCH-BE-012 独立验证](../../../../plans/ARCH-BE-012-simplified-plc-facts/checklist.md) · [v2 开发说明](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)

| 工件 | SHA-256 |
| --- | --- |
| [开发 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json) | `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2` |
| [r2 请求 Schema](../../../../contracts/published/http-api/plc-facts-v2/schema-acquisition-r2.json) | `7d39fa01ef75c1bcd3606b638baf42df7c97d5d34a4a51379a6e172810cae806` |
| [r2 样本和回执向量](../../../../contracts/published/http-api/plc-facts-v2/vectors-acquisition-r2.json) | `f7aca00e02d4722d8d53a056d4a1e803313231180ebf19d899ef7b734da4b63d` |

源码基线 HEAD `fd999224a8756feda314a33148304b4bf3461876`。开发 OpenAPI 尚未跟踪，以下相对 `backend/app/plc_facts/` 的文件包含未提交增量。记录隔离运行实际文件清单与摘要，合同实质漂移时交 PM 修订。

| 路径 | SHA-256 |
| --- | --- |
| `api/v2.py` | `2c9e36d2dfafe9dc9d5851ad619625687102e4ba35a8c57075ee83ed94dd8dce` |
| `manifest.py` | `8f9c8f41cd429ea2d38353913bce6d45240d534f5128ac073dceea3f845268ef` |
| `services/async_v2.py` | `3823fc37f62241dc1eb048bd57b8ddad435789852cccb57850148abd88c4eee1` |
| `v2_config.py` | `8ca146e2d8613779cefd4b7326ced0c3895524bc087acab7c2c1b9a0a3bfd636` |
| `v2_domain.py` | `cd1d769220121a8d224fc744c728586c52a3582ef44e982d785ffa7bfc8c9ed4` |

后端登记实际实例、PLC、DB 和来源代次，按登记生成 `sourceType`。DAA 核对当前 profile 的实例、PLC、DB 和代次，实际登记由运行目标管理。五个 GET 的 `readScopes` 用于只读核对。免 Bearer 只用于本文已界定的开发目标。

## 3. 需求

### R02 完整 DB 样本与独立限额

- 同一 PLC/DB 的上报启用点来自同组同周期，以采集轮持久保存的配置上下文证明完整。同轮多个 DB 仍整体保存，每个 DB 各自提交和确认。保留原实例、样本 ID、PLC/DB、来源代次、十进制字符串序号、组和配置版本，点位保留稳定 ID、类型、值、质量和原 `observedAt`。失败或缺测点按 v2 提交 `bad`、`null` 与原原因。
- 在配置及实际激活路径按 DB 校验 1–512 点，发送前校验实际 UTF-8 JSON 正文至多 524288 B。支持满足独立 S7 和存储预算的同组两个 DB（400 点、512 点）。超限、跨组、完整性不足或不可无损编码的已保存样本原样保留，显示原因并停止该样本发送。S7 读段、读取总字节/时限、本地完整轮编码和物理容量分别限额。
- 草稿保存诊断、导入预览 readiness、激活/回滚、actor 装载与重开使用相应 profile 的同一预算策略。旧 profile 继续使用其已核验的本地采集规则，具备新版上报能力时应用新版 DB 检查。沿用已有解析、草稿诊断与确认行为。

### R03 实时、补传与可靠回执

- 以持久化边界区分启用新版能力前的旧样本与本轮候选新采集样本。后者从本地采集事务提交后进入待传，显式启动上报前及断网期间均可排队。旧样本和 v1 证据原样留存，从既有历史或诊断入口可查。旧样本不进入 v2 队列及四项状态统计，v1 ACK 不计入 v2 已确认。新版上报的选取、转换和回收均不得自动处理这些旧记录。
- 首次发送前持久记录样本原身份、`plc-facts/v2`、实际 UTF-8 正文和摘要、完整目标 URL。发出请求前记录尝试及该次实际目的地址，网络等待在 SQLite 写事务外。使用单 worker、有界派发和退避，持续采集时积压也有发送机会。暂停停止新派发，在途回执按原尝试结算。重开时采集和上报均停止，恢复由用户显式操作。
- 仅接受来自匹配尝试的可信 HTTP 200、`code=200`、`message=success`、`status=committed`、`outcome=created|duplicate`，同时核对合同、实例、样本 ID、请求绑定。有效回执和 v2 确认同一事务落盘。GET、网络探测和旧回执不能生成 v2 确认。
- 断网、超时、丢回执、进程中断、回执不可核、本地确认未落盘和 `503 commit_outcome_unknown` 保持未确认，按 R07 绑定规则重发同身份、同字节。`503 not_ready` 有界退避，`403 scope_rejected` 暂停受影响来源。`409/410/413/415/422` 保留原样本和诊断，停止该样本自动重试。每点的到期以原观察时间加三个上海自然月再减 24 小时计算，整份取最早。逾期仍无可靠回执时显示需处理。
- 运行中的退避使用单调时钟，重开用持久记录有界重建。核对墙钟双向跳变时的等待行为，以及后到样本可补入历史、逐点最新值维持较新序号的行为。

### R04 现有 SQLite 复用、容量与兼容

- 沿用正常 `pnpm tauri dev` 和既有 profile 选择规则。在所选目录继续使用 `config.sqlite`、`runtime.sqlite` 及原样本、配置和序号机制。先核对 config2/runtime2、runtime3 的账本与打开条件，优先复用原结构及同一路径可验证的兼容能力。开发记录说明实际支持的旧版及对应路径。新版上报的必要表、索引或字段确实无法安全复用时，实施面可设计局部、版本可识别的 SQLite 兼容变更，并用合成库验证。变更应保留已支持库的配置、样本原文、序号、引用与历史回执，维持本地采集及历史查看。
- 支持原位调整的已知 schema 须在原锁及已有校验约束下验证失败/中断后的重开、数据一致性和旧二进制打开行为。记录启动/恢复路径和退回到已知可开版本的实际条件。遇到未证可兼容的旧结构、未知 schema、缺库、身份、时间或完整性问题，保留原库并清楚提示可用能力及原因。按已验证的安全规则提供本地能力或在业务写入前拒绝。用户可按原有正常入口另选路径并重新配置，但适用的现有库不强制另建目录。范围以新版上报所需兼容为限，历史搬迁、重放和全矩阵旧库改造另议。
- 容量统计覆盖已保存样本、请求、回执、索引和恢复预留。保留既有告警、停采及恢复行为。未发送、未知、需处理的本轮样本受保护。符合保留策略且已确认、已核对引用的记录才可按既有规则回收。此范围不含删除旧测试样本或用清理换取兼容。
- 以依赖审查为基础收敛未交接的 r3 候选。退出本任务新增的专用 profile 迁入 CLI、模块、专用测试、入口与现行操作步骤。复用仍服务普通启动、实际账本、恢复或界面的有效代码，保全既有与并行工作。 [本地 SQLite 说明](../../src-tauri/src/infrastructure/local_store/README.zh-CN.md)

### R05 macOS 与 Windows

- 使用现有 Tauri/Rust、SQLite、HTTP 和 Snap7 入口，目标为 macOS 与 Windows 10/11 x64。正常入口支持本平台绝对路径、独占锁、配置保存、启停、重开和补传。修改面发现的 Windows 路径、构建或锁兼容缺陷应修复。工具链可用时记录 Windows 目标检查的实际结果，Windows 原生结论按第 7 节跟踪。
- 保持 macOS 已有 sealed 校验及已证原生恢复条件。Windows 继续使用其本机可验证的锁与打开机制，碰到超出现有已证恢复路径的热 journal 时保留原件并提示。Windows 普通重开、发送与确认之间退出、SQLite 写入期间热 journal 分别核验。若热 journal 阻塞本轮必须的重开和补传，修复并重测相应场景后方可验收。

### R06 「上报与存储」与操作说明

- 复用当前页面及公共组件。上报运行区直接展示运行/暂停状态、实际完整上报地址、最近一次有效回执、开始/暂停/继续、设置，以及按样本去重的待发送、结果未知、需处理、已确认数。计数由原生运行状态产生，历史 v1 确认单独展示。真实来源异常、网络故障和容量告警直接可见，并可进入相关样本或详情。
- 上报记录按样本显示原采集时刻、PLC/DB、上报状态和说明，可按状态筛选并查看样本及投递详情。保留本地容量、空间告警、现有存储策略与保存能力、采样历史筛选分页及点值/质量详情。日志和技术诊断可折叠。一般说明按现有模式支持鼠标、键盘与触控。原采集、保存和确认时间可区分，界面显示上海时间到秒，详情保留原精度。
- 复用窄窗布局及公共表格的最小列宽、拖拽、横滚、稳定字段本机记忆与恢复默认。中英 i18n 对称。无原生桥接时说明可用性。草图的「预览场景」属于演示，正式页面使用真实状态，省略演示切换器、旧批次操作和手填序号窗口。
- 双语 `STAGE_C_GUIDE` 和触达 README 说明正常启动、服务地址及端口、默认路径及完整 URL、异机后端地址、来源登记、启停及恢复、状态说明和存储边界。保留的后端 GET 诊断按实际服务目标及第 2 节相应 GET 合同读取，受独立 `readScopes` 控制。仅有自定义 POST 路径时无法推导 GET 地址，提示该诊断不可用，保留本地详情及 POST 回执核对。无需增加五套 GET 设置。文档按各角色实际证据表述 Mac 与 Windows 的验证进度，保留旧合同历史段落及 DAA-011 原验收。

### R07 可配置的上报地址与变更处理

- 「上报设置」提供两个可编辑字段「后端服务地址（含端口）」与「上报接口路径」。服务地址接受 `http(s)://主机[:端口]`，可将 `http://127.0.0.1:8000` 作为示例。后端在异机时填写运行后端的机器地址，`127.0.0.1` 指运行 DAA 的本机。路径预填 `/api/v1/integration/plc-facts/samples`，允许部署方提供兼容路径。在编辑时预览拼好的完整 URL，保存后运行区显示实际地址。协议、样本 JSON 与回执均按第 2 节 `plc-facts/v2`，不因路径可编辑而改变。地址输入只含协议、主机和端口，路径解析和规范化不得改变目标 origin。拒绝凭据、查询串、片段和可替换 origin 的路径，保持 TLS 校验，禁用重定向和环境代理绕行。配置使用既有 CAS；发送间隔继续默认 5 秒，可设 1–3600 秒，仅影响上报。
- 保存设置不触发网络、采集或派发。更换完整 URL 时暂停派发并核对新地址的实际来源登记，旧在途回执只按其原尝试结算。已核实尚无发送尝试的新版样本可在显式继续后随当前目标投递，保留原样本身份，已冻结正文沿用原字节。已尝试且未确认的样本保留原尝试、完整 URL、原字节及状态，无关合格样本仍可继续。
- 如果只是同一后端的端口、主机别名或路由变更，用户可在设置或待确认详情核对旧、新 URL。用实际部署配置确认两者通向同一个 provider 逻辑目标和同一数据库，并核对来源登记。现行 HTTP 合同不提供可信库身份，通达、相同版本、相同 PLC 名称或 GET 读回不足以单独确认。核对后给用户一次明确的继续入口，记录原、新 URL 及这次确认，将后续尝试绑定新 URL，以原身份、原字节重发；仍凭有效回执完成确认。若不能确认同一目标，保持相关样本可见、可诊断，允许恢复原地址继续或留待核对。不同数据库或来源换代的未决请求不可自动改投。

## 4. 精确实施范围

以下相对 `automation-world/data-acquisition-agent/`。变更限于满足 R01–R07 和相关回归。

| 改动面 | 允许路径 |
| --- | --- |
| 配置预算与 v2 domain | `src-tauri/src/domain/mod.rs`、`src-tauri/src/domain/local_configuration.rs`、`src-tauri/src/domain/local_delivery.rs`、`src-tauri/src/domain/sample_upload.rs` |
| 正常配置和导入 readiness | `src-tauri/src/infrastructure/local_store/configuration.rs`、`src-tauri/src/services/local_configuration.rs`、`src-tauri/src/infrastructure/tia_source.rs`、`src-tauri/src/infrastructure/tia_source/reconcile.rs`。限预算和 readiness 调用链。 |
| HTTP、SQLite 及启动 | `src-tauri/src/infrastructure/facts_http.rs`、`src-tauri/src/infrastructure/local_store/mod.rs`、`src-tauri/src/infrastructure/local_store/schema.rs`、`src-tauri/src/infrastructure/local_store/profile_contract.rs`、`src-tauri/src/infrastructure/local_store/capacity.rs`、`src-tauri/src/infrastructure/local_store/runtime.rs`、`src-tauri/src/infrastructure/local_store/delivery.rs`、`src-tauri/src/infrastructure/local_store/sample_upload.rs`、`src-tauri/src/lib.rs` |
| 运行及 IPC | `src-tauri/src/services/local_delivery.rs`、`src-tauri/src/services/local_activation.rs`、`src-tauri/src/services/local_supervisor.rs`、`src-tauri/src/services/local_scheduler.rs`、`src-tauri/src/services/local_queries.rs`、`src-tauri/src/commands/local_delivery.rs` |
| 退出专用迁入实现 | `src-tauri/src/bin/daa-prepare-sample-upload-profile.rs`、`src-tauri/src/infrastructure/local_store/sample_upload_profile.rs` 仅清理本任务新增文件。`src-tauri/Cargo.toml` 仅撤出对应 bin 声明。在表列入口与测试中清理专用引用。 |
| 页面、桥接和文案 | `src/app/collection/views/storage/index.vue`、`src/app/runtime/views/overview/index.vue`（上报摘要）、`src/components/console/FactsDeliveryPanel.vue`、`src/components/console/FactsDeliveryDialog.vue`、`src/components/console/LocalHistoryPanel.vue`、`src/components/console/LocalSampleDetail.vue`、`src/console/composables/useLocalAcquisitionConsole.ts`、`src/services/factsDelivery.ts`、`src/services/localAcquisition.ts`、`src/styles/app.css`、`src/locales/zh-CN/common.json`、`src/locales/en-US/common.json`、`src/app/collection/locales/zh-CN.json`、`src/app/collection/locales/en-US.json` |
| 定向 Rust 回归 | `src-tauri/src/infrastructure/facts_http_tests.rs`、`src-tauri/src/infrastructure/local_store/delivery_tests.rs`、`src-tauri/src/infrastructure/local_store/profile_contract_tests.rs`、`src-tauri/src/infrastructure/local_store/sample_upload_tests.rs`、`src-tauri/src/services/local_delivery_tests.rs`、`src-tauri/src/infrastructure/local_store/time_contract_tests.rs`、`src-tauri/src/infrastructure/local_store/tests.rs`、`src-tauri/src/infrastructure/local_store/source_import_tests.rs`、`src-tauri/src/infrastructure/local_store/point_naming_tests.rs`。后两处仅为受触达旧库测试匹配实际版本的合成夹具，保留原保护断言。 |
| 定向 UI 回归 | `tests/facts-delivery.test.mjs`、`tests/sample-details.test.mjs`、`tests/time-and-history-preferences.test.mjs` |
| 双语文档与结构索引 | `STAGE_C_GUIDE.md`、`STAGE_C_GUIDE.zh-CN.md`、`README.md`、`README.zh-CN.md`、`src-tauri/src/infrastructure/local_store/README.md`、`src-tauri/src/infrastructure/local_store/README.zh-CN.md`。仓库根 `CODE_INDEX.md` 只同步实际变动的 DAA 条目，保全并行改动。 |
| 角色记录 | 本 bundle 的 `tasks.md` 和 `checklist.md` 分别由实际 Development、fresh-context Verification 按各自门槛维护。 |

Development 与 Verification 按改动面使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`，涉及 PLC 点位定义及读取预算时按 `plc-point-mapping`，实际结构变化使用 `code-document-indexer`。隔离 provider 与 Docker 操作使用 `backend-arch`、`docker-expert`、`docker-project-ops` 的适用部分。沿用锁定 Cargo、pnpm 和 uv。合成夹具、临时配置、源码副本、测试日志和代理只落于第 6 节自有目录或对应 Windows 临时根。正式 provider、公开合同、Alembic 源码、DS/SMA/Web 实现、真实设备、现有环境、生产安全策略、部署、发布及 Git 写入各走所属范围。

## 5. 验收标准

| 编号 | 可核对结果 |
| --- | --- |
| AC01 合同与来源 | 第 2 节固定候选经隔离 HTTP 接收 v2 POST、免 Bearer。登记的 `daa` 来源通过，错误实例/PLC/DB/代次被拒绝。所用 GET 能在独立 `readScopes` 范围核对。 |
| AC02 同组多 DB 与双限额 | 从正常配置保存、导入 readiness、激活、采样到重开，核对同组 400 与 512 点两个 DB、原完整点集和失败/缺测点，且两份可独立确认。跨组或 513 点拦截，旧规则仍适用的入口另验 256/257。受控向量 524288 B 可提交，超 1 B 的已保存样本留存且零 POST。另验独立 S7 和本地容量预算。 |
| AC03 断网、重开与确认 | 覆盖发送前离线、服务端提交后丢回执、标记尝试后退出、本地确认写入失败。重开停态，显式继续后核对 SQLite 中原身份、采集时间、正文 SHA 和请求 URL，`duplicate` 可原子确认，历史只有一份。 |
| AC04 错误和运行交错 | 错回执、非当前合同及 `503` 均无虚假确认，实测 `403/409/410/413/415/422` 的正确处置。暂停、修改配置、切换来源及原尝试迟到回执不会串用请求、证据或确认。 |
| AC05 顺序、公平和退避 | 新样本先到、同流较旧有效样本后到，历史按原时间可读，逐点最新值不回退。持续采样时积压有发送机会。模拟运行中双向墙钟跳变和重开，量测单调等待和有界重建。 |
| AC06 SQLite 复用和保护 | 用正常入口建立空合成 profile，记录实际 schema 和停采停传行为。用合成 config2/runtime2、runtime3 证明所支持的原路径打开和必要兼容策略，未证支持的结构走保全和提示路径。比对配置、样本原文/身份、序号、历史凭证和引用。任何必要结构变更另验锁、中断恢复和旧二进制行为。旧样本及 v1 凭证原样留存和可查，v2 队列与统计均排除旧样本。容量停采、恢复及未确认保护可复验。 |
| AC07 Mac 原生完整链路与页面 | 原生 Tauri 上配置并读取受控环回 S7 设备，至少一条新合成样本可逐项对账 S7、SQLite、v2 POST、回执和独立 MySQL，读回最新值和历史。断开目标期间样本继续落盘，恢复后以原身份补传并读回。实际界面核对上报状态/统计、筛选详情、存储配置与历史、异常、帮助、列宽、窄窗、中英及双语指南。 |
| AC08 Windows 原生验证 | 在 Owner 后续提供的 Windows 10/11 x64 实机用精确候选、普通入口和合成数据，记录系统版本/架构及构建，验证路径、配置激活、独占锁、重开、断网补传、发送与确认之间退出、热 journal 边界及实际页面。源码/交叉检查或 Mac 实测分别记录。 |
| AC09 自定义完整 URL | UI 与 IPC 核对默认路径、实时拼接、单改端口及单改路径、保存/重开持久化、非法输入和保存无隐式发送。用第 6 节同一 provider 的自有代理换端口及兼容路径，证明未发送样本可走新地址，已尝试未确认样本在明确核对后用原身份/正文获得可靠回执，历史仍唯一。未核对或不兼容目标无误投。核对旧、新尝试 URL、迟到回执以及其他合格样本仍可发送。保留的 GET 诊断使用自己的读取路由，无法读回时清楚提示且无确认。 |

运行受影响的 Cargo fmt/锁定测试、pnpm build、Node 定向回归及本地文档链接检查，记录实际命令、退出码和限制。对照 r3 Development 记录的全量 HEAD `109 pass / 13 fail / 2 ignored` 与候选 `126 pass / 16 fail / 2 ignored` 定位受影响回归。按实际新旧 schema 语义处理 r3 的 4 项新失败，历史失败逐项确认与记录，保留有效断言。r5 造成的相关回归解决后方可交接。 [Development 自检与基线比较](tasks.md)

## 6. Mac 隔离真实链路与 Docker 操作

第 4 节源码范围和本节运行可分别授权。软件范围批准后可先实现及做合成自检。第 6 节运行在候选就绪、自检通过、具体操作已批准且预检通过后执行。Verification 在 `developer_handoff` 后用自己的资源复验。

| 所属轮次 | MySQL 容器 | 专属卷 | bridge 网络 | 独立空 schema | 环回端口 MySQL / FastAPI / 故障及别名代理 |
| --- | --- | --- | --- | --- | --- |
| Development | `daa010-r5-dev-mysql` | `daa010-r5-dev-mysql-data` | `daa010-r5-dev-net` | `daa010_r5_dev` | `33317 / 38117 / 38217` |
| fresh Verification | `daa010-r5-qa-mysql` | `daa010-r5-qa-mysql-data` | `daa010-r5-qa-net` | `daa010_r5_qa` | `33318 / 38118 / 38218` |

1. 使用本机 Docker 引擎做只读预检，确认本轮资源名、私有目录及所有使用端口可用，核对精确镜像 `mysql:8.4.6`。镜像缺失时允许一次拉取这个 tag，记录实际 ID/摘要。资源有冲突或无法证明归属时停在预检。使用 `docker network create`、`docker volume create`、`docker run` 建表列独立资源。容器只挂自己的卷，只发布 `127.0.0.1:<本轮 MySQL 端口>:3306`，使用 `--default-time-zone=+08:00` 和独立临时账号。为本任务新建的资源记录其实际 ID、端口和归属。
2. 每轮使用 `/private/tmp/daa010-r5-dev-private` 或 `/private/tmp/daa010-r5-qa-private`，目录权限 0700、私有配置和凭据 0600。用 HEAD 与第 2 节锁定增量组装脱敏 provider 副本，核对源码、摘要、import 路径和锁定 uv 环境。清除继承的数据库/后端设置，FastAPI 和 Alembic 只读取本轮私有 .env 及 provider profile。写入前确认本轮容器、网络、卷、环回端口、MySQL 8.4.6、实际 server UUID、空 schema、账号权限、上海会话时间及候选 Alembic head `5f7a9c1e3b25`。按现有 `ACQ_RETIREMENT_*`、`ACQ_FACTS_*` 和 `TASK_CUTOVER_*` 的目标校验执行迁移，只作用于本轮表列 schema，并复核实际 revision。provider profile 绑定该 UUID、schema、revision、合成实例/PLC/DB/代次及读范围。
3. 在所列环回端口启动 provider、按需启动本轮代理。代理仅转发到本轮 provider，用于测试断网、提交后丢回执及同后端端口/路径切换。用本轮配置核对别名前后的逻辑目标与实际库。验证真实 POST、回执、GET 读回及只读 SQL 对账，故障仅作用于本轮进程、样本或数据库。错误目标和未核对目标的测试用本轮代理或合成响应观察无误投。每轮使用自己的 DAA、DS、凭据、schema、进程及夹具。
4. 原生 DAA 使用本轮独立绝对 `DAA_PROFILE_DIR` 和隔离 env，覆盖空测试目录与适用的同目录合成旧库。端口 `15191` 可用时用普通 `pnpm tauri dev`。需要替代端口时，仅在本轮临时源码副本使用 Development `15193` 或 Verification `15194`，预检通过后保留正常入口链并记录差异。使用仓内 DS 或等价的既有 S7 模拟器，显式使用本轮独立 `DS_PROFILE_DIR`、合成设备、环回 S7 `35117`（DEV）或 `35118`（QA）。DS 界面临时端口为 `15195`（DEV）或 `15196`（QA），只改临时副本。AC07 同时要求原生 UI、环回 S7 和后端对账，其他大点数或故障场景可另用合成夹具经过真实 SQLite 与 worker 验证。
5. 记录准确候选清单、端口与目标核验、命令和退出码、冻结正文摘要、回执、账本与后端核对及故障结果。完成本轮即关闭所属的 Tauri、DS、代理与 provider 进程。持久证据已保存且生命周期条件满足后，由协调者以核对的资源 ID 仅对本轮新建资源执行 `docker stop`、`docker rm`、`docker volume rm`、`docker network rm`，回收符合条件的自有临时材料。记录实际清理与保留理由。两轮证据不依赖随后可清理的目录。

本节授权限于表列合成资源及操作。既有 `.local/dev`、后端 `:8000`、MySQL `:3307`、已存在的容器/卷/网络、用户数据和 Docker Compose `up/down/build` 属于其他运行范围。候选、目标或环境达不到条件时记录受阻的验收项，按实际参数处理新的授权。

## 7. 交接、实际采用和 Windows 后续

获批后实际 Development 按第 4 节实施并记录自检，以精确交付工作树、diff、命令/证据、风险和资源清单交接。临时运行副本的有效源码变更须整合至交付树并核对，端口替代等隔离差异独立记录。fresh-context Verification 对同一交付候选独立核验，给出可复查的 Mac 结论及 Windows 待验项。Human Owner 可以先接受 Mac 受控范围。主-DAA 交付不依赖 Mac 路径的 Windows 操作说明，Owner 在可用的 Windows 机上执行 AC08，Verification 复核真实结果后进入对应验收。

实际采用时另具具体运行单，列明选择的 profile、实际进程和启停窗口、后端地址及逻辑目标、来源登记、允许试发的新样本、读回、停止条件和回退。如涉及现有 SQLite 兼容变更，运行单应核对该真实库的版本、原路径/锁、必要备份与回退条件。若候选已记录新序号或发送，先保留并核对新证据，再决定实际回退，避免覆盖原库或重用序号。现有 `.local/dev`、当前 dev 后端和实际数据维持其现有授权边界。旧 dev 测试样本本次无需补传，任何后续真实旧样本操作须明确另批。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)

## 8. Revision 与 Human Owner 范围批准

r3 的真实批准、原稿和 r1/r2 记录在下方留存。r4 是未获批准的草案，其前置正文原始 SHA-256 与原文记录见历史。r5 收敛为复用原有采集与本地存储、必要的同目录兼容、已确认界面及可配置完整上报地址，保留 Mac 优先和 Windows 待实测边界。批准记录如下。

### Human Owner 范围批准

2026-11-12（Asia/Shanghai），Human Owner 在当前承接会话明确批准 DAA-010 r5 的源码实施和第 6 节所列 Mac 隔离运行。获批草案的 SHA-256 为 `2a5df34ab76b3bbf13fe07a00f384200ea6938dac5c2dbb4bb530f34288b9caa`。

**批准原文**

> 批准 DAA-010 r5 按 STD 实施第 2–5 节及第 7 节，按已确认界面、服务地址与上报接口路径配置方式调整 DAA，复用现有采集和本地存储，完成新版实时上报、补传和回执确认。批准第 6 节所列两轮 Mac 合成隔离运行及专属 Docker/MySQL 8.4.6 操作，含缺失时拉取指定镜像、联调、故障测试和自有资源回收。Windows 原生验证后续实测，现有 .local/dev、现有 dev 后端及真实数据操作另批具体运行单。

**审批前备选的分批措辞（历史记录）**

> 批准 DAA-010 r5 按 STD 实施第 2–5 节及第 7 节。第 6 节 Mac 隔离运行和 Docker 操作另批，现有 dev 和真实数据操作仍另批。

> 批准 DAA-010 r5 第 6 节两轮 Mac 合成隔离运行及所列专属 Docker/MySQL 8.4.6 操作，含缺失时拉取指定镜像、联调、故障测试和自有资源回收。启动仍以对应候选与预检通过为条件。

<details>
<summary>r4 未批准草案前置正文（历史）</summary>

此处留存原 r4 前置正文。归档前完整 r4 spec SHA-256 为 `04d5f0bc86591e846bbe75b603cacce639e2a920b72e5b12dd24f7eaebbd473f`，其原有 r3/r2/r1 历史接续保留。

> Task ID: DAA-010
> Revision: r4
> Status: draft
> Owner Role: PM
> Allowed Writers: PM, Human Owner
> Handoff: 主-DAA 转 Human Owner 审阅 r4 实施范围与第 6 节隔离 Docker 操作。实施获批后交 Development，先完成 Mac 受控链路，Windows 原生证据后续补齐。
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Task Namespace: aiis-ics-arch
> Classification: root
> Capability: DAA 按完整 DB 样本上报新采集事实、断网补传、可靠确认和本地运维
> Owner: Automation World / Data Acquisition Agent
> Acceptance Chain Reference: 本稿第 5 至 8 节与 Development Lifecycle Workflow
> Depends On: ARCH-ACQ-003 r2 已验收 provider 范围及本稿第 2 节锁定的开发合同
> Related Task: ARCH-ACQ-001, ARCH-BE-012, DAA-007, DAA-008, DAA-011
> Created: 2026-11-10 Asia/Shanghai
>
> # DAA 按完整 DB 样本上报
>
> ## 1. 本轮目标
>
> DAA 先在本地 SQLite 保存完整采集轮，再以一份 DB 样本为单位上报。新采集数据在断网、后端未就绪或响应丢失时继续保存在本地，恢复后沿用原采样身份逐份补传。通过「上报与存储」页查看、启停和核对投递，并交付双语操作说明。
>
> 2026-11-12（Asia/Shanghai），Human Owner 确认此前 dev 的少量旧验证样本无需补传，已有 PLC、DB 和点表可以重新配置。r4 使用明确选定的新空 profile。原 `.local/dev` 和其他既有 profile 继续保全。新采集样本的离线队列保存在同一个新版 profile，断网恢复和重开均不需要搬库。Human Owner 同时要求应用能在 Windows 运行，现阶段先完成 Mac 链路，之后由 Owner 在 Windows 测试机执行原生核验。
>
> DAA-007 r2 的受控 DS → SQLite 是本地采集基线。DAA-008 的 `plc-facts/v1`、旧 `/batches`、B-RUN-01 和回执，及 DAA-011 r1 的双语指南验证均保留各自的历史证据。r3 尚未交接，Development 的暂停、改动和自检按其原记录追溯。 [根级路线](../../../../plans/ARCH-ACQ-001-acquisition-data-coordination/spec.md) · [DAA-007 验收](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-008 记录](../DAA-008-reliable-facts-upload/checklist.md) · [DAA-011 记录](../DAA-011-dev-manual-refresh/checklist.md) · [r3 Development 记录](tasks.md#scope-review--human-owner-clarification-2026-11-12)
>
> ## 2. 提供方与开发合同
>
> **R01** 沿用 r3 已获准的前置调整。ARCH-ACQ-003 r2 于 2026-11-11 验收 QA2 核对的 provider、合同及指定 dev 交付，40 文件清单 SHA-256 为 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。验收后后端按独立 DIRECT 调整开发合同，样本 POST 和五个 GET 免 Bearer。r4 使用下列工作树中的合同和源码增量。ARCH-BE-012 r4 仍为 `qa_blocked`，其原隔离 B 矩阵、清理、容量及终验仍归原任务。 [ARCH-ACQ-003 验收](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) · [ARCH-BE-012 独立验证](../../../../plans/ARCH-BE-012-simplified-plc-facts/checklist.md) · [v2 开发说明](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
>
> | 工件 | SHA-256 |
> | --- | --- |
> | [开发 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json) | `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2` |
> | [r2 请求 Schema](../../../../contracts/published/http-api/plc-facts-v2/schema-acquisition-r2.json) | `7d39fa01ef75c1bcd3606b638baf42df7c97d5d34a4a51379a6e172810cae806` |
> | [r2 样本和回执向量](../../../../contracts/published/http-api/plc-facts-v2/vectors-acquisition-r2.json) | `f7aca00e02d4722d8d53a056d4a1e803313231180ebf19d899ef7b734da4b63d` |
>
> 源码基线 HEAD `fd999224a8756feda314a33148304b4bf3461876`。开发 OpenAPI 尚未跟踪，以下相对 `backend/app/plc_facts/` 的文件包含未提交增量。记录隔离运行实际文件清单与摘要，合同实质漂移时交 PM 修订。
>
> | 路径 | SHA-256 |
> | --- | --- |
> | `api/v2.py` | `2c9e36d2dfafe9dc9d5851ad619625687102e4ba35a8c57075ee83ed94dd8dce` |
> | `manifest.py` | `8f9c8f41cd429ea2d38353913bce6d45240d534f5128ac073dceea3f845268ef` |
> | `services/async_v2.py` | `3823fc37f62241dc1eb048bd57b8ddad435789852cccb57850148abd88c4eee1` |
> | `v2_config.py` | `8ca146e2d8613779cefd4b7326ced0c3895524bc087acab7c2c1b9a0a3bfd636` |
> | `v2_domain.py` | `cd1d769220121a8d224fc744c728586c52a3582ef44e982d785ffa7bfc8c9ed4` |
>
> 后端登记实际实例、PLC、DB 和来源代次，按登记生成 `sourceType`。DAA 核对当前 profile 的实例、PLC、DB 和代次，实际登记由运行目标管理。五个 GET 的 `readScopes` 用于只读核对。免 Bearer 只用于本文已界定的开发目标。
>
> ## 3. 需求
>
> ### R02 完整 DB 样本和独立限额
>
> - 同一 PLC、DB 的上报启用点须同组同周期，以该轮持久保存的配置上下文证明完整。多个 DB 可同轮原子保存，各自用 `POST /api/v1/integration/plc-facts/samples` 提交和确认。保持原 `instanceId`、`sampleId`、PLC、DB、`sourceGeneration`、十进制字符串 `sourceSeq`、组和配置版本，以及稳定点 ID、类型、值、质量、原 `observedAt`。失败或缺测点留在完整点集，按 v2 提交 `bad`、`null` 与原原因。
> - v4 按 DB 校验 1–512 点，实际 UTF-8 JSON 正文至多 524288 B。跨组、超点数、无法证明完整或不能无损编码时显示原因。采集轮已保存的样本留在本地，超限不裁剪、不拆分、不发送。S7 分段、读段/总字节/时限、本地完整轮编码和物理容量分别约束。v4 必须经实际配置和激活入口支持同组两个 DB 的 400 点和 512 点。已知旧版本继续适用旧组 256 点、轮编码和读取规则。
> - 从已验证的 runtime 版本取得预算策略，统一用于草稿读取和保存诊断、激活/回滚、导入候选预览 readiness、actor 安装和完整账本重开。旧草稿的带诊断保存语义保留。导入继续使用既有解析、结构拒绝和确认条件。
>
> ### R03 新采集数据的实时、补传与可靠确认
>
> - SQLite 提交后才选择待传样本。首次发送前持久化原身份、规范化目标、协议、实际 UTF-8 字节及摘要，并先记录发送尝试。显式启传，单 worker 有界派发。实时与补传共用入口和回执，持续采集期间历史待传也能得到发送机会。网络等待在 SQLite 写事务外。暂停后停止新派发，已在途响应按原绑定结算。
> - 仅在同一请求上下文收到可信的 HTTP 200、`code=200`、`message=success`、`status=committed`、`outcome=created|duplicate` 且合同、实例、样本 ID 匹配时，同事务保存回执和 v2 确认。设置保存或历史读回不会生成确认。v1 状态和回执作为历史证据，不能成为新 v2 样本确认或清理的依据。
> - 断网、超时、丢回执、进程中断、回执不可信、本地确认未落盘及 `503 commit_outcome_unknown` 保持未确认，重试同目标、同身份、同字节。`503 not_ready` 按有界退避等待。`403 scope_rejected` 暂停受影响来源。`409`、`410`、`413/415/422` 保留样本和诊断，停止该样本自动重试。到期按原点观察时间加三个上海自然月减 24 小时，样本取最早，按合同和后端反馈判定。后端已提交但逾期未获回执时，仍显示需处理。
> - 有界退避在进程持续运行时使用单调时钟。重开按持久记录有界重建等待，初始采集和上报均停止，由用户显式继续。测试运行中墙钟向前、向后大幅变化，核对相同等待不会提前发送或无限延后，并验证重开后的间隔恢复。上海业务时间与单调等待分别核对，前一版 v1 测试不计作本轮 v2 证据。
> - 保存后端地址及高级频率继续使用 CAS，默认 5 秒，范围 1–3600 秒，仅影响发送。地址、合同或来源变化时暂停相关投递，冻结请求保持原绑定。拒绝 URL 内凭据、重定向及环境代理绕行。当前来源与目标核对通过才可派发，换源或换目标不得改写旧身份。
>
> ### R04 新空 profile、保留与旧入口
>
> - 以显式绝对 `DAA_PROFILE_DIR` 选定新的空目录，通过普通 `pnpm tauri dev` 初始化 config2/runtime4。采集配置由 DAA UI 重新录入或走已有 TIA 导入。生成新实例身份和来源代次，保存配置、激活、连接、启采与启传仍是显式操作。
> - v4 在 runtime SQLite 持久化单份请求、状态和回执，继续使用本地样本原文/配置上下文和单轮完整保存。容量计入待传事实、冻结请求、回执、索引及恢复预留。容量告警、停采及恢复可诊断。只有符合保留策略且确认、引用均已核对的记录才可正常回收。未确认、未知或需处理样本继续受保护。
> - 新版识别 config2/runtime2、runtime3 的版本及本地历史边界，提示以独立新目录使用 v2 上报。旧 profile 的保护以无自动升级、无重置或清理、无旧 HTTP 派发为可核对结果。兼容诊断或既有历史读取保持只读，无法满足只读条件时在业务写入前拒绝。旧版打开 v4 应安全拒绝。未知 schema、单库、身份或时间不符按严格准入处理。
> - 收敛 r3 未交付改动。移除本任务专为旧 profile 迁入新增的 CLI、专用模块、入口、测试和现行文档步骤。普通 v4 初始化、有效投递账本、旧版本只读保护、受控恢复及历史证据继续按实际依赖维护。v4 是否保留空的 v1 表由 Development 按最小变更决定，以账本独立和保留保护验收。收尾只处理确认属于本任务且无运行、核验或历史证据依赖的临时资源。 [本地 SQLite 说明](../../src-tauri/src/infrastructure/local_store/README.zh-CN.md)
>
> ### R05 macOS 与 Windows 目标
>
> - 产品使用现有 Tauri/Rust、SQLite、HTTP 和 Snap7 入口，目标为 macOS 与 Windows 10/11 x64。普通 Windows 启动应能在本机绝对路径初始化新 v4 profile、读取、保存和启停，并完成离线队列补传及重开。共享业务路径和基本验证夹具使用本平台绝对临时目录。发现明显 Windows 编译、路径、锁或运行阻碍时在相应改动面修复。Windows 原生证据由第 7 节跟踪。
> - macOS 现有 sealed 核验规则及已证明的原生恢复条件继续适用。Windows 的正常空库路径使用已知 unsealed 校验和 profile 锁，遇到不具备现行恢复条件的真实热 journal 应保全并清楚报错。普通重开、发送间隙进程退出与 SQLite 正在写入时的热 journal 是不同故障场景。若 Windows 原生验证发现热 journal 阻塞本轮所需的重开及补传，修复并重测后才能通过对应 Windows 项。保留日志及队列证据，使用平台支持的恢复路径。
>
> ### R06 「上报与存储」与双语说明
>
> - 主区显示运行状态、待传、结果未知、需处理和已确认数，提供开始/继续、暂停和设置。按样本去重，来源和错误可核对。设置展示后端地址与高级频率。历史 v1 投递只在可用的旧资料诊断中展示。
> - 保留真实本地用量/容量设置与告警、本地历史筛选分页、样本点值和投递详情。日志和诊断默认折叠，说明以有可访问名称的问号供悬浮、键盘焦点和触控打开。实际错误直接显示。普通工作流移除旧批次、人工序号窗口和复杂证明摘要。
> - 时间按上海显示到秒并保留原精度。普通数据列复用最小宽、拖拽、横滚、稳定字段本机记忆和恢复默认。中英 i18n 对称。浏览器无桥预览显示真实可用性。
> - 双语 `STAGE_C_GUIDE` 和触达 README 写明新空 profile、常规启动、离线/继续、开发免 Bearer、登记与读回。以各角色真实证据写入 Mac 和 Windows 的状态，保留 DAA-011 原手册证据和旧合同历史段落。
>
> ## 4. 精确实施范围
>
> 以下相对 `automation-world/data-acquisition-agent/`。只改与 R01–R06、原生验证与退出迁入有关的路径。
>
> | 改动面 | 允许路径 |
> | --- | --- |
> | 配置预算与 v2 domain | `src-tauri/src/domain/mod.rs`、`src-tauri/src/domain/local_configuration.rs`、`src-tauri/src/domain/local_delivery.rs`、`src-tauri/src/domain/sample_upload.rs` |
> | 正常配置和导入 readiness | `src-tauri/src/infrastructure/local_store/configuration.rs`、`src-tauri/src/services/local_configuration.rs`、`src-tauri/src/infrastructure/tia_source.rs`、`src-tauri/src/infrastructure/tia_source/reconcile.rs`。只传递当前版本预算和 readiness，保持点表解析、候选结构、原确认规则。 |
> | HTTP、SQLite 及启动 | `src-tauri/src/infrastructure/facts_http.rs`、`src-tauri/src/infrastructure/local_store/mod.rs`、`src-tauri/src/infrastructure/local_store/schema.rs`、`src-tauri/src/infrastructure/local_store/profile_contract.rs`、`src-tauri/src/infrastructure/local_store/capacity.rs`、`src-tauri/src/infrastructure/local_store/runtime.rs`、`src-tauri/src/infrastructure/local_store/delivery.rs`、`src-tauri/src/infrastructure/local_store/sample_upload.rs`、`src-tauri/src/lib.rs` |
> | 运行及 IPC | `src-tauri/src/services/local_delivery.rs`、`src-tauri/src/services/local_activation.rs`、`src-tauri/src/services/local_supervisor.rs`、`src-tauri/src/services/local_scheduler.rs`、`src-tauri/src/services/local_queries.rs`、`src-tauri/src/commands/local_delivery.rs` |
> | 退出专属迁入实现 | `src-tauri/src/bin/daa-prepare-sample-upload-profile.rs`、`src-tauri/src/infrastructure/local_store/sample_upload_profile.rs` 仅清理本任务新增文件。`src-tauri/Cargo.toml` 仅撤出对应 bin 声明。`src-tauri/src/lib.rs`、`src-tauri/src/infrastructure/local_store/mod.rs` 和测试仅撤出专属入口/引用。 |
> | 页面、桥接和文案 | `src/app/collection/views/storage/index.vue`、`src/app/runtime/views/overview/index.vue`（上报摘要）、`src/components/console/FactsDeliveryPanel.vue`、`src/components/console/FactsDeliveryDialog.vue`、`src/components/console/LocalHistoryPanel.vue`、`src/components/console/LocalSampleDetail.vue`、`src/console/composables/useLocalAcquisitionConsole.ts`、`src/services/factsDelivery.ts`、`src/services/localAcquisition.ts`、`src/styles/app.css`、`src/locales/zh-CN/common.json`、`src/locales/en-US/common.json`、`src/app/collection/locales/zh-CN.json`、`src/app/collection/locales/en-US.json` |
> | 定向 Rust 回归 | `src-tauri/src/infrastructure/facts_http_tests.rs`、`src-tauri/src/infrastructure/local_store/delivery_tests.rs`、`src-tauri/src/infrastructure/local_store/profile_contract_tests.rs`、`src-tauri/src/infrastructure/local_store/sample_upload_tests.rs`、`src-tauri/src/services/local_delivery_tests.rs`、`src-tauri/src/infrastructure/local_store/time_contract_tests.rs`、`src-tauri/src/infrastructure/local_store/tests.rs`。本地回归按真实版本安排夹具。保留旧 ACK、引用、容量和回收断言，新增用真实 v2 确认的覆盖。Windows 普通空库、锁和队列测试使用平台自有临时目录，Unix 凭据特有用例单列。 |
> | 定向 UI 回归 | `tests/facts-delivery.test.mjs`、`tests/sample-details.test.mjs`、`tests/time-and-history-preferences.test.mjs` |
> | 双语文档与结构索引 | `STAGE_C_GUIDE.md`、`STAGE_C_GUIDE.zh-CN.md`、`README.md`、`README.zh-CN.md`、`src-tauri/src/infrastructure/local_store/README.md`、`src-tauri/src/infrastructure/local_store/README.zh-CN.md`。仓库根 `CODE_INDEX.md` 仅同步本次真实 DAA 源码结构，保全并行改动。 |
> | 角色记录 | 本 bundle 的 `tasks.md` 和 `checklist.md` 分别由实际 Development、fresh-context Verification 按门槛维护。 |
>
> Development 和 Verification 按改动面用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`，源码结构变化用 `code-document-indexer`。隔离后端与 Docker 按 `backend-arch` 和适用 Docker 项目规则。使用项目锁定 Cargo、pnpm、uv 工具链。合成夹具、临时配置/源码副本、测试日志和代理只落于第 6 节自有目录或对应 Windows 自有临时根。正式 provider、合同、迁移脚本、业务库、DS/SMA、真实 PLC、部署、版本发布和 Git 写入由各自范围管理。
>
> ## 5. 验收标准
>
> | 编号 | 可核对结果 |
> | --- | --- |
> | AC01 合同与来源 | 同字节 provider 通过真实隔离 HTTP 收到 v2 POST、免 Bearer。登记 `daa` 来源正常提交，错误实例/PLC/DB/代次拒绝，`readScopes` 读回范围独立可核对。 |
> | AC02 同组多 DB 与双限额 | 从正常保存/导入 readiness、激活、采样到重开，核对同组 400 和 512 点两个 DB、各自完整点集及失败/缺测点。一个 DB 暂时失败时另一个可独立确认。跨组或 513 点被诊断和拦截，旧版 256/257 及独立 S7、存储预算另验。受控向量实发 UTF-8 524288 B 可提交，超 1 B 的原样本留存且无 POST。 |
> | AC03 断网、重开和确认 | 用新 profile 采样并在断网时看到 SQLite 待传。覆盖发送前离线、提交后丢回执、发送标记后退出、确认写入失败。停止态重开，显式继续，核对原样本身份、时间、原字节和目标，`duplicate` 可靠确认且后端历史仅一份。 |
> | AC04 错误及换源 | 错回执、非当前合同和 `503` 无虚假确认。实测 `403/409/410/413/415/422` 的正确处置。变更设置、暂停在途、切换来源及收到迟到回执时，原绑定、队列和回执不串用。 |
> | AC05 顺序、公平和退避 | 先提交新样本再补较旧有效样本，历史按原时间保留，逐点最新值不倒退。持续采样时待传能获得发送机会。模拟运行中双向墙钟跳变与重开，量测单调等待和有界重建。 |
> | AC06 新空库与保护 | 正常空 profile 建 config2/runtime4 并停采停传。v4 再开、锁占用、容量停采与恢复及未确认/引用保留可核对。用合成 v2/v3 比较旧库、回执和队列，验证无旧协议派发或旧数据自动清理、转换。旧二进制拒绝 v4，异常 profile 保留。 |
> | AC07 Mac 原生采集与上报 | 通过原生 Tauri 界面在自有新 profile 正常配置、连接并采集受控的环回 S7 模拟设备。至少一条合成样本可从 S7 → DAA → SQLite → v2 POST → 隔离 provider/MySQL 一路对账并读回。断开上报目标期间继续本地采样，恢复后用原身份和时间补传并读回。验证设置、开始/暂停、运行/队列/诊断/错误、容量、历史详情、列宽、中英切换及问号交互。双语指南可按步骤操作。 |
> | AC08 Windows 原生核验 | 后续在 Owner 可用的 Windows 10/11 x64 实机，以精确交付候选走常规入口，记录实际系统版本/架构及构建结果。验证新 profile、保存激活、并发锁、正常关闭/重开、断网/恢复、发送标记后与本地确认之间的退出、回执核对和实际界面。记录热 journal 处理及未覆盖场景。源码检查、交叉编译或 Mac 实测均不能代替该项。 |
>
> 开发自检和独立 QA 运行受影响的 Cargo fmt/锁定测试、pnpm build、Node 定向回归、文档链接检查，记录实际命令和退出码。r3 Development 的可复用证据按候选差异核对。原记录的全量 HEAD `109 pass / 13 fail / 2 ignored` 与 r3 `126 pass / 16 fail / 2 ignored` 作为比较基线。r3 四项新增失败为三项旧 ACK 夹具和一项空库版本断言，应按新旧语义解决。HEAD 复现的旧导入、命名、YAML 等失败逐项记录影响、证据与剩余风险，保持原有效断言。r4 新增失败须定位并处理后才能交接相关范围。 [Development 自检与基线比较](tasks.md)
>
> ## 6. Mac 隔离真实链路与 Docker 操作
>
> 第 4 节实施与本节 Docker 操作可分别批准。软件范围获批后可先完成实现和合成自检。启动本节真实链路需要候选就绪、定向自检完成、Docker 操作获批及运行预检通过。独立 QA 在 `developer_handoff` 后使用自身资源复验。
>
> | 所属轮次 | 新建 MySQL 容器 | 新建专属卷 | 新建 bridge 网络 | 独立空 schema | MySQL / FastAPI / 故障代理 |
> | --- | --- | --- | --- | --- | --- |
> | Development | `daa010-r4-dev-mysql` | `daa010-r4-dev-mysql-data` | `daa010-r4-dev-net` | `daa010_r4_dev` | `127.0.0.1:33317 / 38117 / 38217` |
> | fresh Verification | `daa010-r4-qa-mysql` | `daa010-r4-qa-mysql-data` | `daa010-r4-qa-net` | `daa010_r4_qa` | `127.0.0.1:33318 / 38118 / 38218` |
>
> 1. 使用当前本机 Docker 引擎，先以只读检查确认两套名称和对应端口未占用，并核对精确镜像 `mysql:8.4.6`。镜像缺失时，本节批准可覆盖一次精确镜像拉取，记录实际 ID/摘要。存在冲突或无法证明资源归属时停在预检。按轮次仅创建表列网络、卷和容器，容器只挂该专属卷，发布 `127.0.0.1:<该轮 MySQL 端口>:3306`，设置 `--default-time-zone=+08:00`。只用独立生成的临时账号和独立 schema。操作包括 `docker network create`、`docker volume create`、`docker run` 和已列资源的后续核对及清理。
> 2. 每轮使用 `/private/tmp/daa010-r4-dev-private` 或 `/private/tmp/daa010-r4-qa-private`，目录权限 0700、私有配置和凭据 0600。源码副本从 HEAD 与第 2 节固定增量组装，复核摘要、import 路径和锁定 uv 环境。清除继承的后端与数据库设置，FastAPI 和 Alembic 从脱敏候选读取专用 `.env` 和仓外 provider profile。禁止从真实 `backend/.env`、用户资料或 Git 凭据取得设置。写入前核对 Docker 所属容器、卷、网络、环回端口、MySQL 8.4.6、该容器实际 server UUID、空 schema、账号范围、上海会话时间及 Alembic head `5f7a9c1e3b25`。现有 Alembic 的 `ACQ_RETIREMENT_*`、`ACQ_FACTS_*` 与 `TASK_CUTOVER_*` 目标参数只取该轮实测值，保持各迁移原有前驱、空表和身份检查。仅对表列 schema 执行迁移并复核 revision。provider profile 绑定实际 UUID、schema、revision、合成实例/PLC/DB/代次及读范围。具体启动命令和迁移预检实测由本轮 Development 记录。
> 3. 分别在上述环回端口启动 provider、按需启动本轮故障代理。使用实际候选的 SQLite 和发送 worker，合成新样本走真实 HTTP/回执及只读 SQL 对账。注入断网、丢响应和重开只作用于本轮进程/目标。记录命令、退出码、候选摘要、目标核验、冻结正文 SHA、回执、SQLite/后端核对和恢复结果。Development 和 Verification 各用自己的 profile、凭据、schema、进程及夹具记录。
> 4. 原生 Tauri UI 使用本轮新 profile 和隔离 env。端口 `15191` 可用时使用普通 `pnpm tauri dev`。若被现有运行占用，只在本轮临时副本将 UI 启动口改为 Development `15193` 或 Verification `15194`，预检后按相同入口链启动并记录差异。用仓库 DS 或等价的现有 S7 模拟器完成 AC07 的真实环回采集。DS 使用本轮独立 `DS_PROFILE_DIR`，显式启动合成实例，S7 仅监听环回 `35117`（DEV）或 `35118`（QA）。DS 界面临时启动口为 `15195`（DEV）或 `15196`（QA），只改临时副本并预检。400/512 点与故障等补充场景可使用现有夹具经 SQLite 和真实发送 worker 核验。AC07 需要原生 UI、真实环回 S7 和后端对账三类证据，缺少对应环境则记录 blocker。设备与来源完全合成。
> 5. 结束相应轮次后关闭本任务启动的 Tauri、DS、故障代理与 provider 进程。持久证据、交接与核验可复现后，由协调者按生命周期确认归属和依赖，对表列两个资源集执行 `docker stop`、`docker rm`、`docker volume rm` 和 `docker network rm`，并回收可清理的自有临时材料。记录保留项与实际清理。已有服务、卷、镜像和资料不属于本节操作面。
>
> 本节请求的授权限于表列合成资源及明确操作。Docker Compose `up/down/build`、既有容器和本机现有 `:3307` / `:8000` 不在其中。若需更换具体运行资源，先按实际参数核对授权。Mac 受控范围通过条件包含实际隔离 provider/MySQL、原生 UI 与 S7 环回。缺独立目标或候选未就绪时登记对应 blocker。
>
> ## 7. 交接、实际采用和 Windows 后续
>
> r4 范围获批后由实际 Development 在第 4 节实施并记录自检。Mac 受控范围达到要求后，Development 交接精确候选、diff、命令/证据、环境限制和资源清单，由 fresh-context Verification 对同一候选独立核验。QA 与 Owner 可先核对并接受 **Mac 受控范围**。Windows 原生 AC08 作为独立待验证项保留，未取得证据时整体 Windows 结论和跨平台最终验收继续待定。主-DAA 提供不依赖 Mac 路径的 Win 操作步骤，Owner 后续在其实际测试机取得精确候选证据，由 Verification 核对实际覆盖。开发/验证中发现现有批准范围无法容纳的实质改动时回 PM。
>
> 现有 dev 采用有单独的实际操作门槛。若需接入现有后端，先提供具体的新空 profile、实际进程与端口、启停窗口、后端身份/来源登记和允许试发的新样本范围。现有 `.local/dev`、旧配置和资料须保全，现有后端操作、真实样本 POST、部署及现场设备动作按各自明确运行单执行。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
>
> ## 8. Revision 与拟请批准
>
> `r1`、`r2` 的范围和 `r3` 的 2026-11-12 明确批准、原稿、日期及精确摘要收录于下方历史。`r4` 于 2026-11-12（Asia/Shanghai）按 Owner 澄清移出旧 dev 数据及配置迁入，保留新采集样本的离线补传，新增 Windows 目标、Mac 优先验收、必要配置调用路径和可核对的隔离 Docker 操作。当前为草案，待精确批准。
>
> 两项决定可分别确认，亦可使用下列一句同时批准。
>
> > 批准 DAA-010 r4 按 STD 实施及受控验证第 2 至 5 节和第 7 节，包含新空 profile、样本上报、macOS 与 Windows 10/11 x64 目标及 Mac 真实隔离链路，并批准第 6 节两轮专属 Docker/MySQL 8.4.6 操作，包含镜像缺失时的精确拉取、合成联调和所列资源回收。Windows 原生验收待后续实测，现有 dev 按第 7 节另批运行单。
>

</details>

<details>
<summary>r3 获批规格、范围批准及 r1/r2 历史</summary>

> Task ID: DAA-010
> Revision: r3
> Status: owner_approved
> Owner Role: PM
> Allowed Writers: PM, Human Owner
> Handoff: Human Owner 已批准 DAA-010 r3 前置调整、实施及隔离验证。交 Development 执行获批范围，现有 dev 采用及旧样本实发按第 6 节另批。
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Task Namespace: aiis-ics-arch
> Classification: root
> Capability: DAA 以完整 DB 样本为单位实时上报、补传和可靠确认，提供本地运维界面
> Owner: Automation World / Data Acquisition Agent
> Acceptance Chain Reference: 本稿第 5 至 7 节与 Development Lifecycle Workflow
> Depends On: ARCH-ACQ-003 r2 已验收的 provider 范围及第 2 节固定的开发合同，前置调整待 Human Owner 批准
> Related Task: ARCH-ACQ-001, ARCH-BE-012, DAA-007, DAA-008, DAA-011
> Created: 2026-11-10 Asia/Shanghai
>
> # DAA 按完整 DB 样本上报
>
> ## 1. 目标与基线
>
> DAA 先将采集轮保存到本地 SQLite，再按一个 PLC、一个 DB、一次采样的完整样本上报。实时和断网补传共用入口、身份、正文和确认规则。本轮同时交付「上报与存储」页和双语操作指南。
>
> Human Owner 已选定把此前 `.local/dev` 的本地验证样本纳入新版补传。讨论时观察到 11 条 `pending`，实际清单和状态以获准窗口的闭库盘点为准。r3 交付筛选、无损迁入、发送及对账能力，隔离核验使用合成数据。第 6 节是这批旧样本在现有 dev 的实际采用和核对步骤。
>
> DAA-007 r2 已验收的受控 DS → SQLite 是本地基线。DAA-008 的 `plc-facts/v1`、旧 `/batches`、B-RUN-01 和原回执属于历史合同。DAA-011 r1 的双语手册核验保留原候选和结论。主-DAA 负责本任务的 STD 交接。 [根级路线](../../../../plans/ARCH-ACQ-001-acquisition-data-coordination/spec.md) · [主-DAA](codex://threads/01a143e5-5616-76c0-9df7-13b487bc9c26) · [DAA-007 验收](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-008 记录](../DAA-008-reliable-facts-upload/checklist.md) · [DAA-011 记录](../DAA-011-dev-manual-refresh/checklist.md)
>
> ## 2. 开工前置与交接
>
> **R01 提请批准本次前置调整。** r2 要求先完成 ARCH-BE-012 r4 的隔离独立验证及最终验收。现有事实如下。
>
> | 依据 | 可用于 r3 的范围 |
> | --- | --- |
> | ARCH-ACQ-003 r2 | 2026-11-11（Asia/Shanghai）已获 Human Owner 最终验收。覆盖 QA2 核验的 provider、合同与指定 dev 交付，当时目标 Alembic revision 为 `4e6a8b0d2f14`。验收对应 40 文件清单 SHA-256 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。验收记录明确把 DAA 的新版上传、补传和确认移交本任务。 |
> | 当前开发合同 | 上述验收之后，后端按当次 DIRECT 调整样本 POST 和五个 GET，均无需 Bearer。下表是当前开发工作树的实际工件。当前 OpenAPI 为未跟踪文件，相关 provider 源码有未提交改动，属于验收后的增量。 |
> | ARCH-BE-012 r4 | 整体仍 `qa_blocked`。已有 A 独立源码核验与指定 dev 功能验证。双轮隔离 B、其完整故障与兼容矩阵、清理与 30 分钟容量验证、Human Owner 最终验收继续由 BE-012 跟进。 |
>
> 本次提议由 **ARCH-ACQ-003 r2 已验收的 provider 范围和下列开发合同**承接 DAA-010 的开工前置，经 Owner 明确批准后启动 r3 Development 和本任务隔离核验。ARCH-BE-012 的整体门槛不再阻挡这两项 r3 工作，其未完范围和风险继续记在原任务。后端 DIRECT 仅适用于该次后端调整，DAA-010 继续使用 STD。根路线的阶段结论仍由其所属任务核对。 [ARCH-ACQ-003 验收](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) · [ARCH-BE-012 独立验证](../../../../plans/ARCH-BE-012-simplified-plc-facts/checklist.md) · [当前开发说明](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
>
> | 工件 | SHA-256 |
> | --- | --- |
> | [开发 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json) | `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2` |
> | [r2 请求 Schema](../../../../contracts/published/http-api/plc-facts-v2/schema-acquisition-r2.json) | `7d39fa01ef75c1bcd3606b638baf42df7c97d5d34a4a51379a6e172810cae806` |
> | [r2 样本和回执向量](../../../../contracts/published/http-api/plc-facts-v2/vectors-acquisition-r2.json) | `f7aca00e02d4722d8d53a056d4a1e803313231180ebf19d899ef7b734da4b63d` |
>
> 草案核对时的工作树 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`。下列 `backend/app/plc_facts/` 文件的摘要固定与开发合同有关的未提交增量。真实核验须以同字节候选启动并留存准确运行清单。
>
> | 相对 `backend/app/plc_facts/` 的路径 | SHA-256 |
> | --- | --- |
> | `api/v2.py` | `2c9e36d2dfafe9dc9d5851ad619625687102e4ba35a8c57075ee83ed94dd8dce` |
> | `manifest.py` | `8f9c8f41cd429ea2d38353913bce6d45240d534f5128ac073dceea3f845268ef` |
> | `services/async_v2.py` | `3823fc37f62241dc1eb048bd57b8ddad435789852cccb57850148abd88c4eee1` |
> | `v2_config.py` | `8ca146e2d8613779cefd4b7326ced0c3895524bc087acab7c2c1b9a0a3bfd636` |
> | `v2_domain.py` | `cd1d769220121a8d224fc744c728586c52a3582ef44e982d785ffa7bfc8c9ed4` |
>
> 主-DAA 交接时核对这些工件、后端候选和使用的运行环境。若协议、准入、回执或风险实质漂移，受影响工作回到 PM 修订。当前开发免凭据只适用于第 5 节受控目标及第 6 节另批的开发目标。`readScopes` 的各组 PLC/DB 条目取并集用于读回，写入准入仍由后端的实例、活跃来源和 DB 登记决定。
>
> ## 3. 需求
>
> ### R02 单 DB 完整样本和限额
>
> - 普通 DAA 采集轮继续原子提交本地 SQLite。每个 DB 形成独立样本、独立 `POST /api/v1/integration/plc-facts/samples` 和独立回执。同一 PLC/DB 的全部上报启用点须来自同一个采集组和周期，按采样时不可变配置确认。组可同时采集多个 DB，也可在同一轮分段读取 S7。保留失败和缺测点及其实际观察时间和原因。同 DB 跨组、跨轮或跨时间的片段保持原样，禁止拼成一份完整样本。
> - 正文为 UTF-8 `application/json`，编码为 identity，`contractVersion=plc-facts/v2`。用原 `instanceId`、`sampleId`、`plcId`、`dbNumber`、`sourceGeneration`、十进制字符串 `sourceSeq`、`groupId` 和原配置版本 `configRevision`。点按稳定 `pointId` 提交类型、值、质量和原 `observedAt`，`bad` 带 `null` 和原因。按合同无损映射类型和值，保留原始数值、布尔、缺失语义和时间精度。后端以登记决定 `sourceType`，请求不传该字段。
> - 启用上报或采用采集配置前按 DB 检查组、周期和 1–512 点。发送前检查最终 UTF-8 正文不超过 524288 B。无法证明完整、超限或无法无损映射的已保存样本保留原文、标记需处理并显示原因，零 POST、零裁剪。v4 的采集组 256 点门槛和本地单轮编码预算按 DB 样本粒度调整，须支持同组同轮 400 点与 512 点两个 DB 的合成用例。S7 读段、总字节、读时限、内存、完整轮持久化和本地磁盘继续有各自上限，预算扩大时同步核对物理写入预留及容量门禁。旧 profile 的本地规则按打开矩阵保留。
>
> ### R03 投递账本、结果和恢复
>
> - 第一次发送前，从已经提交的样本一次生成正文并在同一 runtime SQLite 持久保存实际 UTF-8 字节、摘要、样本身份、合同和固定目标。网络等待在写事务外。发送前先持久记录尝试。单 worker 有界选择候选并保留历史发送机会，重试使用固定目标和原字节。启动或重开停采停传，显式开始或继续才可派发。暂停阻止新的派发，已经发出的请求仍可能提交，按原绑定持久化有效回执或保留未知结果。
> - 只接受同一冻结请求的可信响应。校验媒体类型及格式、HTTP 200、`code=200`、`message=success`、`data.status=committed`、`outcome=created|duplicate`、`contractVersion`、`instanceId` 与 `sampleId`，并核对固定目标和请求上下文。有效回执和该样本 v2 已确认状态在同一事务写入。GET、HTTP 状态或本地日志均不能生成确认。旧 v1 回执留在原账本，单独显示协议和历史确认。
> - 区分未发送、已发结果未知、需处理和 v2 已确认。断网、超时、响应不可核、进程中断、本地确认未持久化、`503 commit_outcome_unknown` 均保留未确认及冻结材料，按有界退避重试。`503 not_ready` 保留队列并等待目标恢复。`403 scope_rejected` 暂停受影响来源，核对登记。`409 sample_content_conflict`、`410 expired_unconfirmed`、`413`、`415`、`422` 保留材料、记录原因并停止该样本自动重试。遇到非当前合同的响应，例如旧目标要求认证或路径不符，提示目标／协议不匹配，禁止协议降级。
> - 每点到期以原 `observedAt` 加三个上海自然月再减 24 小时，整份取最早截止，最终按后端时间和回执判定。已过期或确认未知的记录继续受本地未确认保护。待处理材料、在途正文和回执计入容量。保留有界诊断与 ACK 恢复预留，容量不足触发现有暂停和恢复条件。可以对满足本地保留及引用规则的已确认样本执行正常维护。
> - 设置保存继续使用 CAS，只配置后端地址和高级发送间隔，默认 5 秒，合法范围 1–3600 秒。该间隔只管上报。显式启动前核对规范化目标、合同和后端登记的来源。地址、合同或来源变化须暂停受影响投递，保留旧绑定和未决证据。禁用 HTTP 重定向和环境代理绕行，拒绝 URL 内凭据。已冻结的行只能在原目标与来源重新核对后继续，禁止改投、重编号或替换历史代次。同一 URL 背后的服务替换由运行窗口核对，回执本身不携带库的物理身份。
>
> ### R04 旧样本纳入范围
>
> 以第 6 节获批的 `.local/dev` 双库快照为边界，对截至快照的待传样本逐份核对。原 `payload`、SHA、manifest、配置上下文、点值、各时间、采样序号、采集组和代次保持可比对。备选样本仅按当时生效的上下文证明同 DB 点集完整，当前点表不能回填缺失历史。新 v2 正文从原样本无损构造一次并冻结。原 v1 正文不作为 v2 HTTP 请求复用。
>
> | 旧样本状态 | 在 r3 中的处置 |
> | --- | --- |
> | 待传且可证明从未发出 v1 请求 | 逐份验证 R02 与当前登记，合格则列入 v2 待传。若存在旧冻结请求，保留原正文和全部关联，须确认每个关联片、批次及其父子记录均无发送尝试。只见 `pending` 或缺少回执不足以作判断。 |
> | v1 已确认或部分已确认 | 保留原确认和原样本。完整 v1 ACK 仍显示历史 v1 确认。部分已确认列为需处理并供人工对账。均不计入 v2 已确认或默认 v2 重发。 |
> | v1 已尝试、在途、结果未知、证据不足或状态有冲突 | 保留并标明待对账原因及原请求、已知回执、关联样本，不自动改投。经所属旧合同证据核清且满足纳入条件的样本才可纳入经确认的补传清单。需要另作重放决定的记录继续停在需处理。 |
> | 原样本已过期、完整性无证、来源不匹配、点数或字节超限 | 保留原件，记录逐样本原因，显示在历史详情并供核对。禁止用新 ID、新代次、现时采样时间或分片绕过。 |
>
> ### R05 本地 schema、备份及版本打开矩阵
>
> 采用独立迁入目的地。普通启动按现有 `DAA_PROFILE_DIR` 规则选 profile，新空 profile 建 config2/runtime4。v4 在同一 runtime 持久保存独立 v2 投递状态、正文和回执，保留旧数据模型和 v1 账本的证据语义。配置 SQLite 仍为 v2。新旧样本仍使用已有原样本格式。原 profile 保持原路径、版本与文件身份。
>
> | profile / 条件 | r3 普通启动 | 显式准备 v4 |
> | --- | --- | --- |
> | 新空 profile | 初始化 config2/runtime4，停采停传，目标未配置。 | 无旧数据可迁。 |
> | 合法、冷态 unsealed config2/runtime2 | 继续本地采集与历史，无上传、无投递 DDL。 | 原锁下核验并只读提取一致双库。保留原配置和历史，用无 v1 投递账本的已知 schema 与候选来源证明核对未发送。 |
> | 合法、冷态 unsealed config2/runtime3 | 继续本地能力，可查旧投递。禁止 v1 派发和把 v1 状态重置或转成 v2 ACK。 | 原锁下核验并只读提取一致双库，逐份盘点旧 v1 全部关联。 |
> | 合法、冷态 sealed config2/runtime3 | 在原路径按原身份/凭据、DDL 和完整账本校验后提供本地能力及历史。 | 先在原路径按原身份取得锁并校验。将一致双库和受保护材料作为迁入来源，复制件不能冒充可运行的原 sealed profile。v4 目的地按自己的实际路径及 inode 建立和验证新的凭据，原凭据、marker 与文件身份留存。 |
> | 已有 config2/runtime4 | r3 按其精确 DDL、身份、时间及凭据规则打开并恢复 v2 未决记录。旧 binary 拒绝 runtime4。 | 已完成的目的地和部分失败的目录均不能被准备入口覆盖。 |
> | 占用、非洁净、hot journal、未知版本/UTC、缺库、身份或凭据不符、意外 WAL/SHM | 遵守已有严格启动和 sealed 精确原生恢复规则。未核验的恢复分支拒绝业务写入。 | 准备入口拒绝并报告原因。旧库先用其已验证的原路径/原版本恢复到可证明的洁净状态。禁止删 journal、marker 或绕过锁，不将异常降级为 unsealed。 |
>
> 准备入口只接受显式绝对源、目标路径，不使用默认 profile，不运行采集或 HTTP。无参数只显示帮助。实际闭库后在原 profile 锁下以只读方式对身份、时间、schema、完整性、外键、原始字节、历史引用和待决账本校验。生成受保护的一致双库备份及摘要，在新目录分阶段准备 v4，保留原配置、来源档案、草稿/active revision、`instanceId`、每 PLC `sourceGeneration` 和 `next_seq`，保存原样本原字节及旧投递材料。数据复制方式由 Development 选择，须证明锁定的一致性和零原库写入。
>
> v4 只在目的地完整校验后可见，失败产物明确不可启动，重试不得覆盖来源或已发布目的地。源路径或目标被另一进程占用时拒绝。锁后再次核对路径和身份。容量预算含备份、staging、journal 和恢复空间，失败时保留现场和可审计摘要。保留原 profile 与备份供回退，只有经证明可重开的精确版本配对才可启动。新的冻结正文、旧 v1 ledger 或引用不得因超限、确认未知或切换而提前清理。 [本地 SQLite 现行合同](../../src-tauri/src/infrastructure/local_store/README.zh-CN.md)
>
> ### R06 「上报与存储」和操作手册
>
> 1. 页面先显示上报运行状态和待传、结果未知、需处理、已确认的样本数，提供开始/继续、暂停与设置。计数按样本去重，显示其协议或从详情查旧 v1 历史确认，v1 确认不计入 v2 已确认。设置中显示后端地址与高级频率。来源实例、PLC/DB、代次及准入核对材料从设置或诊断可查，普通操作不要求填写序号窗口或复杂摘要。
> 2. 显示真实本地用量、上限与容量告警，保留本地存储的保留天数/容量设置及既有保存、应用语义。保留可筛选分页的本地历史主表，从样本进入采集原值/质量和投递详情。能核对采集、保存、投递及确认时间，页面按上海时间显示到秒，原值和原精度可在详情核对。
> 3. 日志、原文摘要、投递诊断和旧批次记录放进默认折叠的诊断或详情。一般说明放入带可访问名称的问号，支持鼠标悬浮、键盘焦点与触控打开。实际错误、需处理原因和容量告警直接显示。移除普通工作流的旧批次投递操作、手填人工序号窗口及复杂证明摘要，保留只读历史诊断。沿用一套 runtime 状态和公共列宽逻辑，普通列拖拽、最小宽、横滚、本机按稳定字段记忆及恢复默认。中英文 i18n 同步，浏览器无桥预览不得假保存、假上报或访问后端。
> 4. 更新 `STAGE_C_GUIDE.md` / `STAGE_C_GUIDE.zh-CN.md`，写明隔离 profile、旧样本盘点/迁入、上报与恢复、当前 dev 免机器 Bearer、来源登记及 `readScopes` 读回规则，并解释现有 dev 采用门槛。DAA-011 r1 原验证仍针对当时的精确文档。
>
> ## 4. 允许实施的文件
>
> 以下路径均相对 `automation-world/data-acquisition-agent/`，特别注明仓库根的路径除外。只批准与 R01–R06 直接相关的变更。
>
> | 改动面 | 精确路径 |
> | --- | --- |
> | 样本、配置及 v2 协议 | `src-tauri/src/domain/mod.rs`、`src-tauri/src/domain/local_configuration.rs`、`src-tauri/src/domain/local_delivery.rs`、`src-tauri/src/domain/sample_upload.rs`（可新增）、`src-tauri/src/infrastructure/facts_http.rs` |
> | SQLite 和冷态准备入口 | `src-tauri/src/infrastructure/local_store/mod.rs`、`src-tauri/src/infrastructure/local_store/schema.rs`、`src-tauri/src/infrastructure/local_store/profile_contract.rs`、`src-tauri/src/infrastructure/local_store/capacity.rs`、`src-tauri/src/infrastructure/local_store/runtime.rs`、`src-tauri/src/infrastructure/local_store/delivery.rs`、`src-tauri/src/infrastructure/local_store/sample_upload.rs`（可新增）、`src-tauri/src/infrastructure/local_store/sample_upload_profile.rs`（可新增）、`src-tauri/src/bin/daa-prepare-sample-upload-profile.rs`（可新增）、`src-tauri/Cargo.toml`（仅必要的 bin 入口声明） |
> | 运行、设置和 IPC | `src-tauri/src/lib.rs`、`src-tauri/src/services/local_delivery.rs`、`src-tauri/src/services/local_activation.rs`、`src-tauri/src/services/local_supervisor.rs`、`src-tauri/src/services/local_scheduler.rs`、`src-tauri/src/services/local_queries.rs`、`src-tauri/src/commands/local_delivery.rs` |
> | DAA 页面、桥接及文案 | `src/app/collection/views/storage/index.vue`、`src/app/runtime/views/overview/index.vue`（只涉及上报摘要）、`src/components/console/FactsDeliveryPanel.vue`、`src/components/console/FactsDeliveryDialog.vue`、`src/components/console/LocalHistoryPanel.vue`、`src/components/console/LocalSampleDetail.vue`、`src/console/composables/useLocalAcquisitionConsole.ts`、`src/services/factsDelivery.ts`、`src/services/localAcquisition.ts`、`src/styles/app.css`、`src/locales/zh-CN/common.json`、`src/locales/en-US/common.json`、`src/app/collection/locales/zh-CN.json`、`src/app/collection/locales/en-US.json` |
> | 定向回归 | `src-tauri/src/infrastructure/facts_http_tests.rs`、`src-tauri/src/infrastructure/local_store/delivery_tests.rs`、`src-tauri/src/infrastructure/local_store/profile_contract_tests.rs`、`src-tauri/src/infrastructure/local_store/sample_upload_tests.rs`（可新增）、`src-tauri/src/services/local_delivery_tests.rs`、`tests/facts-delivery.test.mjs`、`tests/sample-details.test.mjs`、`tests/time-and-history-preferences.test.mjs` |
> | 双语文档及必要结构索引 | `STAGE_C_GUIDE.md`、`STAGE_C_GUIDE.zh-CN.md`、`README.md`、`README.zh-CN.md`、`src-tauri/src/infrastructure/local_store/README.md`、`src-tauri/src/infrastructure/local_store/README.zh-CN.md`。仓库根 `CODE_INDEX.md` 仅同步本次实际结构变更的 DAA 条目，保全并行修改。 |
> | 角色记录 | `plans/DAA-010-sample-facts-upload/tasks.md` 由 Development 在范围批准后写入。`plans/DAA-010-sample-facts-upload/checklist.md` 由 fresh-context Verification 在实际交接后写入。两者仅引用实际证据，必要脱敏证据按角色归档。 |
>
> Development 及 Verification 按范围选用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`，实际变动源码结构时用 `code-document-indexer`。Rust/Cargo、pnpm 与验证用 provider 的 uv 依赖沿用项目锁定版本。允许在 `/private/tmp/daa010-r3-*` 自有目录内准备合成 fixture、临时配置、验证副本及有界证据。后端源码、公开合同、正式配置和 Alembic 由所属任务管理。本任务排除真实 PLC、SMA、Web 采集页、旧后端资源及历史处置、生产安全变更、部署、发布、Git 写入和外部发送。
>
> ## 5. 验收标准
>
> | 编号 | 可核对结果 |
> | --- | --- |
> | AC01 依赖与入口 | 记录 Owner 对 r3 前置调整的明确批准，对照第 2 节摘要启动同一 provider 候选。确认 DAA 只调用 v2 样本 POST，免 Bearer。以登记的 `daa` 来源提交，错实例、PLC/DB、代次的样本被拒绝。验证 `readScopes` 独立控制读回范围。 |
> | AC02 完整性及双限额 | 同组同轮用 400 点和 512 点两个 DB，含失败或缺测点，对账原始 SQLite 和 HTTP 原值、原身份、采样时间。两个 POST 分别确认，一份失败时另一份仍可成功。单 DB 513 点和跨组/周期在配置预检拦截。用受控向量核对实际 UTF-8 字节数 524288 B 可提交，524289 B 的已保存样本零 POST、保留原文并显示需处理。另测点数合规但超本地读取或存储预算。 |
> | AC03 断网、重启、丢回执 | 在发送前离线、后端提交后丢回执、发送标记后中断、本地确认写入失败或进程终止处分别注入故障。重开停态，继续后同一身份、目标和正文 SHA 对得上，收到 `duplicate` 也可原子确认，后端同身份只保留一条历史。 |
> | AC04 拒绝、来源与目标变更 | 错身份回执、错误 outcome、无效响应及 `503` 均无虚假确认。实测 `409`、`410`、`403` 及 `413/415/422` 的处置，覆盖已提交但到期后仍无回执。来源换代、地址保存、暂停与在途交错时不改投、不自动恢复、不混淆回执或状态，其他合格样本可正常推进。 |
> | AC05 迟到与公平 | 新样本先到、同流较旧样本后到。历史按原采样时间可读，逐点最新值仍为较新序号。持续产生实时样本时，合格旧样本仍能在有界重试与容量条件内获调度。 |
> | AC06 旧样本与账本 | 用合成旧库覆盖待传且未发、已冻结未发、v1 完整/部分已确认、已尝试或结果未知、证据缺失、过期和不完整。迁入前后逐样本对账身份、原字节、上下文、原 v1 正文/回执和类别数量。只有合格旧样本生成 v2 正文并确认，重复准备/重启无重复身份或重置状态。 |
> | AC07 profile 安全与容量 | 实测 R05 矩阵，含旧/新 binary、unsealed/原路径 sealed、搬移/复制的 sealed、锁占用、路径身份变化、半成品、容量不足和故障中断后的重试。比对原双库及相关证据摘要，证明来源无业务写入、旧版本仍可在原路径打开、v4 存量配置和身份序号保全。覆盖备份恢复演练、v4 再开、容量停采及恢复，并证明未确认材料受保护。 |
> | AC08 页面与正常入口 | 用原生 DAA 或同等可操作的隔离运行核对「上报与存储」的实际 Rust 数据和操作、设置后无隐式发送、状态及诊断、表格列宽和中英文。通过常规 Tauri 启动链打开隔离 profile，若以隔离端口替代，记录环境差异。核对两份指南的步骤、文案及本地相对链接。 |
>
> Development 与独立 Verification 各用一份独立、可丢弃的合成 DAA profile，分别核对 SQLite 与实际 HTTP。真实接口核验使用固定的 provider 候选、独立测试 schema/凭据、合成来源、仅环回端口和独立 MySQL 8.4.6 数据，锁定 uv 环境。记录端口、临时数据根、候选摘要、目标核验、命令/退出码、故障触发点、请求摘要、回执、SQLite 与读回结果。允许在专用隔离数据上执行必要的初始化、迁移、合成写入、只读对账及关闭本任务启动的进程。需要 Docker `up/down/build` 时，按项目契约提交具体容器、端口、卷、数据和回收动作另批。现有 dev 库或既有容器不能替代隔离。仅 stub/mock 的证据不能满足真实 HTTP/MySQL 验收。
>
> 在 DAA 根运行 `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`、`cargo test --manifest-path src-tauri/Cargo.toml --locked`、`pnpm build` 及受影响的 Node 定向回归。记录实际所用的普通 `pnpm tauri dev` 启动链、隔离配置和原生操作。缺少可复现 provider、独立数据目标或其他必要条件时，对应验收登记为阻塞并说明解除条件。重要证据归 `tasks.md` 和 `checklist.md`，临时路径仅作证据附件。
>
> ## 6. 现有 dev 的采用和旧样本实发
>
> 本节保留 Human Owner 选定的旧样本补传目标。第 5 节隔离通过后，主-DAA 提交一份具体运行单请 Human Owner 批准，包含现有 `.local/dev` 的规范路径、目标 v4 路径、候选摘要、实际进程和停采停传窗口、备份路径、后端 API/库身份和版本、允许的登记来源/PLC/DB、试发清单、读回、停止条件和回退。后端交接材料记载当前本机 dev 由 8000 API 使用 3307 MySQL，后续迁移 revision 为 `5f7a9c1e3b25`，只作届时核对的候选线索。实际 UUID、schema、revision、来源和读取范围须在窗口内确认。
>
> 1. 在批准窗口显式停采停传、闭库并确认进程退出，取得原 profile 独占锁。核对实际版本/凭据、各类样本和完整备份。列出截至本次快照可迁入、旧 v1 已确认、需对账与其余需处理的样本及原因。核对 v4 候选，配置和点表随候选迁入。
> 2. 经批准在应用现有 `.env` 或显式进程 profile 参数中选中新的 v4，仍用正常 `pnpm tauri dev`。保留 `instanceId`、`sourceGeneration` 和 `next_seq`，新采样从已核对的下一个序号继续。切换后旧 profile 原路径只读留存，旧进程或旧启动项退出运行，旧、新 profile 不能同时使用同一来源身份采集或上报。若无法证明单活或后端未登记原身份，暂停并报需处理，禁止更改历史样本身份来取得准入。
> 3. 以已获准清单中的合格样本小批起步，显式开启上报。按 `sampleId` 和原时间核对原库、v4 冻结字节与回执及后端历史/最新值，汇总实际可补、已确认、结果未知、需处理和旧 v1 对账项。若后端登记、目标身份、发送证据或样本清单变化，先停止受影响投递并重新核对。真实 MySQL 写入只能经批准的样本 POST，后端管理与来源登记动作在运行单逐项列明。
> 4. 回退前先停止 v4 采集与派发，保存 v4 新样本、冻结正文、回执、源序号进度和未知结果，逐项核对后端已提交范围。若 v4 已分配新序号或产生发送，不能仅切回旧 `.env` 或覆盖备份。须由 Owner 决定用已核对的兼容版本继续，或另行批准数据和序号对账后的回退操作。
>
> 现有 dev 的停机、备份、迁入、配置切换、后端登记和真实样本 POST 由此运行单具体授权。第 5 节独立验收只对 r3 候选及隔离环境作结论。真实补传完成与否按本节的实际对账记录追踪。
>
> ## 7. 风险、交接和批准
>
> - 当前免 Bearer provider 为后续开发增量，尚未获得与 ARCH-ACQ-003 r2 相同范围的独立验收。来源登记是协议准入，依赖运行目标隔离及 Owner 批准的信任边界。隔离核验用于确认 DAA 所用实际合同，BE-012 的完整隔离、故障、清理和容量证据仍待原任务处理。
> - 历史样本可能已过期、失去完整上下文、仍存在旧请求未知结果或与当前活跃来源不符。实际可补传数量只能在批准窗口核账，选择旧样本并不等于每份都能取得 v2 回执。
> - 旧 profile 和 v4 候选共享来源身份。上线窗口的单活、原件保留、备份核对和回退对账是实际采用条件。缺少条件就保持停传并保留数据。
> - 协调者按 PM → Human Owner 精确范围批准 → Development `tasks.md` 和自检 → `developer_handoff` → fresh-context Verification `checklist.md` → Human Owner 对精确候选最终验收交接。Development 报告交付工作树、diff、运行入口、限制与临时资源。现有 dev 采用及对账按第 6 节继续单独追踪。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
>
> **拟请 Human Owner 批准的原文**
>
> > 批准 DAA-010 r3 按 STD 实施及隔离验证。批准第 2 节前置调整，以 ARCH-ACQ-003 r2 已验收的 provider 范围和本稿锁定的开发免 Bearer 合同开工。批准第 3 至 5 节的 DAA 源码、旧样本兼容和隔离合成验证。现有 .local/dev、现有 dev 后端及实际旧样本补传，按第 6 节另批具体运行单。
>
> ## 8. Revision 记录
>
> - `r1` 于 2026-11-10（Asia/Shanghai）建立草案，等后端验收交接。
> - `r2` 于 2026-11-10（Asia/Shanghai）补充完整 DB、组/周期、512 点与 512 KiB 和原隔离要求，保留当时以 ARCH-BE-012 整体验收为前置的记录。
> - `r3` 于 2026-11-11（Asia/Shanghai）提请调整开工基线并固定开发合同、实现路径、旧样本迁入、UI、隔离验收和实际采用边界。当前待 Human Owner 审阅批准。
>
> ### Human Owner 范围批准
>
> 2026-11-12（Asia/Shanghai），Human Owner 在当前承接会话明确批准 DAA-010 r3。获批草案的 SHA-256 为 `f0791a7060a36febc05e166d1374e57bfecb105a436a2cfbc882d2125cf3352c`。
>
> > 批准 DAA-010 r3 按 STD 实施及隔离验证。批准第 2 节前置调整，以 ARCH-ACQ-003 r2 已验收的 provider 范围和本稿锁定的开发免 Bearer 合同开工。批准第 3 至 5 节的 DAA 源码、旧样本兼容和隔离合成验证。现有 .local/dev、现有 dev 后端及实际旧样本补传，按第 6 节另批具体运行单。
>
> <details>
> <summary>r2 原稿及其中的 r1 记录（历史）</summary>
>
>
> > Task ID: DAA-010
> > Revision: r2
> > Status: draft
> > Owner Role: PM
> > Allowed Writers: PM, Human Owner
> > Handoff: 待 ARCH-BE-012 新版后端通过受控独立核验并获 Human Owner 最终验收，再由本会话交主-DAA 核定并请求批准 DAA-010 精确 Revision
> > Workflow Mode: STD
> > Execution Mode: agent_team_same_session
> > Task Namespace: aiis-ics-arch
> > Classification: root
> > Capability: DAA 以完整 DB 样本为单位上报事实、断网补传和可靠确认
> > Owner: Automation World / Data Acquisition Agent
> > Acceptance Chain Reference: 本稿第 7 节与 Development Lifecycle Workflow
> > Depends On: aiis-ics-arch::ARCH-BE-012 新版后端交付及第 2 节交接门槛
> > Related Task: aiis-ics-arch::ARCH-ACQ-001, aiis-ics-arch::DAA-007, aiis-ics-arch::DAA-008
> > Created: 2026-11-10 Asia/Shanghai
> >
> > # DAA 按完整 DB 样本上报
> >
> > ## 1. 目标与基线
> >
> > 将 DAA 已提交到本地 SQLite 的完整 DB 样本，通过一个新版事实写入接口上报。断网时继续按本地存储规则采集和排队。恢复后，同一份样本沿用原身份补传，只有取得并持久保存该样本的可靠提交回执才显示已确认。
> >
> > 本任务是根级统筹的第 2 项，保有独立的范围、实现和验收链。本会话起草，正式交接后的生命周期由「主-DAA」协调。当前为草案，处于等待第 1 项后端交付的阶段。 [根级统筹规格](../../../../plans/ARCH-ACQ-001-acquisition-data-coordination/spec.md) · [主-DAA](codex://threads/01a143e5-5616-76c0-9df7-13b487bc9c26)
> >
> > DAA-007 r2 的验收基线是受控 DS 读取至本地 SQLite。DAA-008 r4 的批准和 B-RUN-01 记录属于旧 `plc-facts/v1` 合同。按原任务各自范围解释它们的联调结果和留存资源。 [DAA-007 最终验收](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-008 r4](../DAA-008-reliable-facts-upload/spec.md#r4-b01-f7-owner-approval) · [DAA-008 开发记录](../DAA-008-reliable-facts-upload/tasks.md) · [DAA-008 验证记录](../DAA-008-reliable-facts-upload/checklist.md)
> >
> > ## 2. 开工前置与交接
> >
> > **R01 后端先完成。** 第 1 项 ARCH-BE-012 的新版 provider 及机器可读合同必须定版，在明确获准的隔离环境通过该精确交付范围的独立验证，并取得 Human Owner 最终验收。交接至少包括合同工件及版本或摘要、同一候选的源码标识和可复现启动条件、目标和来源准入核对材料、请求及成功／重复／失败回执样例、合同限额、到期和顺序规则、对应的验证与验收入口。手册或讨论给出的候选接口只用于审阅。 [后端规格](../../../../plans/ARCH-BE-012-simplified-plc-facts/spec.md)
> >
> > 主-DAA 收到并核对交接后，由 PM 将实际合同标识、准确文件清单、profile/schema 兼容矩阵和验证范围固化到本任务待批 Revision。Human Owner 批准该精确 Revision 后才进入 DAA Development。交接缺项、合同漂移或后端尚未验收时，停在相应门槛。真实环境采用、实际启停和隔离操作参数各走对应批准。
> >
> > ## 3. 编号需求
> >
> > **R02 一份完整 DB 样本对应一个 POST。** 每个 POST 只提交一个来源、一个 PLC、一个 DB 在同一次采样形成的一份样本。完整点集按采样时生效的配置版本确定，包含该 PLC 和 DB 的全部上报启用点。v2 首版要求同一 PLC 和 DB 的全部上报启用点属于同一个采集组并共用一个采集周期。启用新版上报或变更其采集配置前检查归属与周期，诊断并阻止不符合规则的配置用于新版上报。同一 DB 在不同组或不同时刻的记录按原样保留，禁止拼接成一份样本。一个组可以覆盖多个 DB，同轮继续在 SQLite 原子保存，每个 DB 分别 POST、由后端独立提交并取得对应回执。
> >
> > DAA 可在一次采样内继续分段读取 S7。从已提交的 SQLite 原样本构造请求，保留实例、来源代次、PLC、DB、采集组、配置版本、稳定样本和点位身份、源端采样顺序、各点实际采集时间、值及质量。失败或缺测点仍在点集中，按合同记录质量和原因。
> >
> > **R03 单入口、上报限额与不可变补传。** 实时发送和历史补传可以采用不同调度优先级，共用 ARCH-BE-012 的唯一事实写入接口和样本身份。新版上报去掉整轮／分片证明、多层摘要、人工填报序号窗口和长期批次回执。新版 profile 的上报限额改为逐 DB 样本校验。每份样本包含 1–512 个点，实际编码的 UTF-8 JSON 正文最多 512 KiB（524288 B）。配置预检逐 DB 核对启用点数，发送前按最终正文字节数校验。超限或无法无损表达的已保存样本原样留存，标记需处理并显示原因，禁止裁点、拆分或发送该样本。
> >
> > 按新版样本粒度调整当前采集组 256 点门禁及旧封装的编码预算，使其支持符合新版合同且通过独立读取与容量门禁的样本。保留本地同轮原子性，并分别约束 S7 读段数、读取总字节、读时限及 SQLite 单轮存储和整体容量。后端接受的点数和正文字节上限只定义 HTTP 准入。首次发送前持久绑定当前目标、合同版本、样本身份和冻结正文。重试使用同一绑定和同一正文。
> >
> > **R04 提交回执及恢复。** 只有能与原目标、协议版本、样本身份和内容对应，并按 provider 合同证明该样本已提交的响应，才允许在同一 SQLite 事务保存确认凭据及更新样本投递状态。同内容重复的成功回执按相同规则验证。HTTP 状态、日志、界面刷新和查到相似事实都不能独立作为确认。网络中断、丢回执、响应无效、进程中断或本地确认失败时，保留待传或结果未知状态，按有界退避重试原样本。合同拒绝、同身份异内容冲突、目标不符或已过后端保留窗口而无法证明原提交时，保留可诊断的未确认状态，按结果停止相关样本或目标的自动重试。后端过期以原观察时间为准，最多三个上海自然月，补传沿用原截止时间。
> >
> > **R05 SQLite 生命周期与容量。** 只有后续精确 Revision 明确支持的 profile/schema 可以启用新版上报。首轮验证使用新建可丢弃的隔离 profile。既有 `config.sqlite`、`runtime.sqlite`、旧队列和留档依原版本管理。普通启动及进程重开时采集和上报意图均为停止。恢复可重试队列后，由用户显式开始或继续上报。沿用 profile 锁、本地串行写入、有限在途请求、容量门禁和可恢复空间预留。上报等待期间释放 SQLite 写事务。按有界方式选择待传样本，在目标恢复且容量允许时，历史待传取得发送机会。过期或待处理样本继续受本地未确认保护，已确认材料仅按本地保留规则及依赖引用回收。既有 profile 的迁移、重绑或历史重放属于另批范围。
> >
> > **R06 目标绑定与状态。** 操作人员按批准范围保存一个后端目标和上报设置。合法目标、来源准入及启用条件由最终合同和交接明确，保存本身不发送、不连接、不启采。目标或合同变化时暂停相关投递，核对未确认样本，避免自动改投、协议降级或重置身份。UI 复用工作台和「上报与存储」页，只调整实际所需的设置和诊断。区分待传、结果未知、需处理和已确认，保持中英文键对称。原采集、保存及后端确认各有时间语义，依上海时间合同展示和保存。日志应有界且足以定位样本与错误，真实目标敏感信息、凭据及原始现场数据留在所属环境。
> >
> > ## 4. 范围与候选改动面
> >
> > 本任务只负责 DAA 的新版事实适配。批准前将以下候选范围缩成精确文件清单。
> >
> > - `src-tauri/` 中的投递域、HTTP adapter、SQLite 投递状态、重试和恢复，以及新版 profile 所需的同 DB 点位归属预检、按 DB 的点数和正文字节检查、本地编码预算适配。既有配置、历史和未决队列按原版本管理，存量配置调整或迁移另行批准。
> > - DAA 的上报 IPC 和相关页面、状态与双语文案，以及对应的受控 fixture、测试和应用文档。新空 profile 如需新 schema，审批前列明具体初始化与打开矩阵。
> > - 后端 provider、Web 采集数据模块、Projection 清退、SMA 和永久业务入库各归所属任务。现场 PLC、真实部署、默认或既有 profile 的采用、真实数据库操作、旧联调资源和历史数据处置、发布和外部发送均另行批准。
> >
> > 实施时按改动面使用 `rust-runtime`。涉及 Tauri 壳或启动配置时叠加 `desktop-tauri`，触达 Vue 页面及文案时使用 `frontend-ui` 和 `i18n-workflow`。项目工具链沿用锁定的 Cargo 与 pnpm。
> >
> > ## 5. 验收标准
> >
> > | 验收 | 可核对结果 |
> > | --- | --- |
> > | AC01 开工顺序 | 可追溯 ARCH-BE-012 的精确机器合同、隔离验证、最终验收与交接。任一前置缺失时无 DAA 实现写入。DAA 开工和联调另有本任务的精确批准。 |
> > | AC02 原样本与单入口 | 使用同一来源、同一 PLC、同组同轮的两个 DB 样本，观察同一写入口收到两个 POST，每个 POST 含一份 DB 样本。对照本地与后端的值、点位、各点实际采集时间、稳定身份及失败或缺测点的质量和原因。让一个 DB 的投递暂时失败，另一个 DB 可独立提交和确认。实时与补传走同一入口。 |
> > | AC03 断网、丢回执与重启 | 用受控故障分别观察发送前断网、后端提交后丢回执、本地确认前中断。重开停传，显式继续后请求仍对应原目标、原身份和内容。后端仅保存一份同身份样本，DAA 取得可验证的回执后才原子确认。 |
> > | AC04 不误确认 | 错样本回执、无效响应、同身份异内容、未准入或错目标、不能证明原提交的过期样本均未被标成成功。重试有界，未确认样本和诊断可核对。 |
> > | AC05 迟到与保留 | 验证同一来源先提交较新样本，再补传仍在窗口内的较旧样本。后端历史按原采集时间可查，相关点位最新值保持较新样本。超期未确认记录不会因后端到期自动从 DAA 删除。 |
> > | AC06 本地隔离和容量 | 比较新空测试 profile 启动前后及持久状态，核对既有版本在获准副本中的打开行为。配置和历史原材料保留，未批准旧 profile 的转换在业务写入前被拦截。容量受限时可诊断且无未确认数据丢失或虚假 ACK。 |
> > | AC07 真实链路证据 | 使用获准的合成样本、新隔离 profile 和 ARCH-BE-012 已验收候选，核对真实 HTTP 请求/回执、本地确认和后端最新/历史。记录精确版本、复现实验、退出码、证据索引和资源收尾。受控端到端证据、静态检查和旧联调结果各自记载。 |
> > | AC08 DB 粒度与限额 | 对照已验收的后端机器合同，在合成隔离 profile 中同组同轮采集两个 DB（分别为 400 点和 512 点，且符合独立的读取、存储及正文预算），两份样本分别走真实 HTTP 并取得回执。单 DB 513 点在配置预检被拦截，实际 UTF-8 正文超过 524288 B 的已保存样本留为需处理，两者均无截断、拆分或 POST。验证同 DB 跨组（含不同周期）的配置在启用新版上报前被诊断，原配置和原样本保留且无拼接。另用点数合规但超读取预算的用例核对读取门禁仍有效。 |
> >
> > 执行前明确隔离启动、故障注入、读账、终止和回收的权限边界。拟执行格式检查、锁定依赖下的针对性 Rust 测试、UI 改动时的前端构建，以及另批的受控 HTTP 验证。证据按角色落入本任务的 `tasks.md` 与 `checklist.md`，避免依赖临时路径作为唯一依据。
> >
> > ## 6. 风险与回退
> >
> > | 风险 | 约束与处理 |
> > | --- | --- |
> > | 合同未定或运行候选不一致 | 以第 2 节交接核对为开工条件，发生差异暂停并回到 PM。 |
> > | 存量同 DB 跨组或编码超限 | 新版启用前诊断配置不符，逐样本核对正文上限。留存原记录和待处理诊断，存量配置调整另批。 |
> > | 本地认为失败时后端可能已提交 | 保留原请求材料和未确认状态，通过原身份恢复。到期而无法证明时记录需处理。 |
> > | 切换目标或二进制导致队列误用 | 先停止派发并保留原 profile、队列及必要证据。仅在独立确认的兼容 profile 上使用原版本。已有新版未决样本的迁移和旧二进制打开新版 profile 都需另行验证和批准。 |
> > | 受控积压耗尽容量 | 触发既有停采／恢复门禁，显示实际容量和待处理状态。恢复须有明确容量依据，避免以删除未确认材料腾空间。 |
> >
> > ## 7. 待决项与 Revision 记录
> >
> > - 后端交付后固定请求、回执、错误、限额和目标准入的实际合同引用。按候选列明新版 profile/schema、独立的本地编码和容量预算、交付文件以及精确的隔离联调范围。
> > - 由根任务跟踪 SMA 是否需要逐份消费和历史提交顺序。DAA 只消费后端已定稿的事实写入合同。若该决策改变请求或回执，重新走本任务范围审批。
> > - `r1` 于 2026-11-10（Asia/Shanghai）起草，等待第 2 节交接与精确范围批准。后续顺序为 PM → Human Owner → Development → fresh-context QA / Verification → Human Owner 最终验收。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
> > - `r2` 于 2026-11-10（Asia/Shanghai）按已确认的设计方向补充单 PLC／单 DB／单 POST、完整点集、采集组与周期约束、512 点与 512 KiB 双限额及隔离核验。本稿继续等待第 2 节交接，由主-DAA 核定实施 Revision 后请求精确范围批准。
>
> </details>

</details>

## DAA-010 r6 待审草案

2026-11-12（Asia/Shanghai），PM 提请 Human Owner 审阅。工作流为 STD。本附录为待批准提案，顶部生效范围仍为 r5。以上 r5 原文件的 101915 字节完整保留，SHA-256 为 `e63c4909027a097e258ab0e812515ad4f4dcf0ddc2266e765e1802075ad5e27c`。r5 QA2 的 `qa_failed` 和 F-R5-QA2-001 见[独立记录](checklist.md#独立验证-qa2)。

### 1. 拟修订范围

r6 在 R04 明示一项已知限制，修订 AC06、AC07、AC09 的 Mac 取证边界和 r5 第 6 节后续复验的运行范围。正常首次启动仍自动建库，继续使用原采集、本地双 SQLite、v2 实时上报、补传、回执及服务地址和路径配置。既有库按 r5 的准入、保全和已证兼容边界处理。r6 拟交付 QA1 返工后的候选，本轮产品源码、依赖、测试和正式运行配置的新增写入范围为空。

**需要 Owner 明确决定的已知限制。** Mac 首次启动时，若其他有权限的本机进程恰好在 DAA 创建新目录之后、首次读取其身份之前，把它换成另一个空目录，当前候选可能在替代目录初始化双 SQLite 并封存。QA2 用含两份 SQLite 和哨兵数据的合成目录做了同一时序的对照，结果为拒绝，文件字节和哨兵保持原样。该结论仅覆盖已测对照。r6 拟由 Owner 明确接受前述空目录场景作为本次 Mac 受控验收的已知限制。发现仍为未修，保留 r5 失败证据。正常首启、独占锁、旧库拒绝或保全、中断后重开、容量保护及其他现有数据保护要求继续纳入核对。[发现与对照](checklist.md#f-r5-qa2-001-首次创建期间替换的空目录被封存为新-profile)

### 2. 候选和证据

- **Owner 操作与 Development 原生证据。** QA1 返工前，Owner 在隔离 Mac 原生窗口完成受控 S7 采集、正常上报及停机恢复后的补传。记录共 17 条合成 DB71 样本，9 条正常确认，8 条在 provider 停机时落盘，恢复后以原身份及请求内容确认。Development 核对了 SQLite、v2 POST 和回执、MySQL 与独立 GET。原生设置、存储及历史等仅按当时实测条目取证。[原生记录与交接](tasks.md#developer_handoff--daa-010-r5)
- **QA2 独立证据。** QA1 返工涉及 `profile_contract.rs`、`profile_contract_tests.rs`、`sample_upload_tests.rs`。交付树 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876` 加 DAA 候选，QA2 核对的 47 项交付清单 SHA-256 为 `23ea1cf05f18efdbd0625885f81d4e39275da8892d7cb8d195c22111d37167ca`。QA2 独立验了返工后普通首次启动、合成旧库和锁、合同与 provider、构建及组件测试。Cargo 全量为 151 通过、4 失败、2 忽略，四项失败在 HEAD 对照中也出现。按原记录保留各命令结果及限制。[返工范围及摘要](tasks.md#r5-development-rework-after-qa1) · [独立记录](checklist.md#独立验证-qa2)
- **可关联性。** 获批后 Development 重新记录本轮精确工作树、受控文件的实际 SHA-256 和返工前后生产差异，并交接现有材料。fresh-context Verification 独立核对采集、SQLite、HTTP/上报、界面等相关文件摘要或可复查差异，明确哪些既有证据适用于当前候选。已回收的临时日志、原始清单和夹具按持久记录的可核对程度使用。无法建立候选关联的观察保留为历史证据，关键证据缺口通过本节限定的定向复验补齐，仍缺则逐项记待验。QA2 合同与自动化结果仅复用于可证实一致的相关实现及合同。前一候选的原生实测来源始终标为 Owner 操作与 Development 对账。

### 3. Mac 独立复验和验收边界

1. **普通首启与重开（AC06）。** fresh QA 在最初不存在的合成路径用正常 `pnpm tauri dev` 启动，核对自动建 config2/runtime4、实例一致、采集和上报均停、零发送，退出后以同一目录重开。复核 QA2 已有旧库、独占锁、中断重开、旧 v1 回执及容量保护的独立证据，按已证边界记结果。第 1 节的空目录替换例外仅在 Owner 明确批准后适用。
2. **上报接口与设置（AC01–05、AC09）。** 对当前候选复跑现有 `v2_loopback_posts_original_utf8_to_sample_path_without_bearer` 和 `retries_keep_original_bytes_and_only_matching_receipt_confirms`，分别确认默认及兼容路径收到原字节、没有 Bearer，以及只有精确匹配的回执才确认原样本。核对普通设置中地址、端口和路径拼接，分开改端口与路径、保存及重开，确认非法输入被拒绝，设置保存不触发发送。较大点集与限额、拒绝或错误响应、结果未知、保序与重试，以及同后端重绑和未核对目标拦截，按 QA2 实际 provider/代理及 SQLite、worker、UI 测试的层级复核。区分客户端、worker、provider 和原生窗口证据。仍缺的正常场景可在本轮现有回环和合成测试内做定向核验。超 1 字节的本地已保存样本零 POST、发送与确认之间退出等，只在已有材料与候选关联或定向复验可证时记为已证。
3. **原生链路与页面（AC07）。** r6 拟以返工前 Owner 与 Development 的 17 条原生链路记录、独立审阅及返工后候选的前两项定向复验，支持本次 Mac 受控范围的验收。用户无需再次配置 DS、导入点表或重跑全链。fresh QA 核对原生页面能打开并展示真实停态与设置，用原生记录、UI 自动化和本轮少量操作分别记录状态、详情、存储历史和双语等覆盖。列宽跨重启和由原生界面切换实际后端端口及路径的联调，按各自现有证据与未独立复测项记录。结论必须写明“返工后候选的原生 S7 → DAA → provider/MySQL 全链本轮未独立重跑”。仍需原生全链独立实测的结论作为单列后续项，不能写入本轮通过项。
4. **交接及最终决定。** Verification 按上述范围写入实际命令、证据来源、结果和待验项。与普通路径或数据保护有关的新失败仍按 STD 交回 Development。缺关键材料且在本范围内无法复核时记录准确缺口，不能用 Owner 操作记录冒充独立复验。只有 fresh-context QA 给出适用本轮精确范围的结论后，才进入 Owner 的 Mac 受控范围最终验收。

### 4. 本轮复验资源

批准后允许一次 fresh Verification 的 Mac 合成复验，限 `/private/tmp/daa010-r6-qa-private` 下的自有源码副本、私有 env、SQLite、构建、夹具和输出。先确认目录不存在且环回端口 `15197` 空闲，冲突时停在预检。普通入口只在私有副本的 `package.json`、`vite.config.ts`、`src-tauri/tauri.conf.json` 一致替换开发端口为 `15197`，保留 Snap7 feature 和原启动链路。用空的私有 `DAA_ENV_FILE`、绝对合成 `DAA_PROFILE_DIR`、清理继承设置的环境以及私有临时和构建目录。回环 HTTP 用现有锁定测试的系统分配临时端口。复核实际资源归属，记录证据后关闭自有进程，协调者按 workflow 核对和回收自有临时资源。

本轮复验使用 QA2 已有的独立 provider/MySQL 结果，新增运行范围限本地原生 DAA 和现有回环测试。若仍需新的 DS、provider 或 Docker 联调，先把具体缺口报 Owner，另行确定操作单。Windows 10/11 x64 原生 AC08 仍待实机证据。实际 `.local/dev`、现有 dev 后端、现场数据与实际试用按 r5 第 7 节另批具体运行单。CU-009 由所属任务处理。

### 5. 审阅和批准

本稿待 Owner 审阅。若明确批准，PM 登记精确 Revision 和批准原文，Development 以 r6 核对候选和差异并重新交接，fresh-context Verification 再核验。按范围使用 `aiis`、`project-governance`、`desktop-tauri`、`rust-runtime`，涉及界面核对时使用 `frontend-ui` 和 `i18n-workflow`。[Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)

> 批准 DAA-010 r6 按 STD 使用 QA1 返工后的候选，保留首次自动建库和现有上报功能。明确接受第 1 节所列首次建库时空目录被替换的已知限制，作为本次 Mac 受控验收的例外。保留 r5 QA2 失败记录。批准第 2 至 4 节的证据审阅和一次 Mac 合成隔离复验。用户已完成的 17 条原生实测无需重做，返工后原生 S7 全链未独立复测须明确记录。Windows 原生后续实测，实际 dev 和真实数据另批具体运行单。
