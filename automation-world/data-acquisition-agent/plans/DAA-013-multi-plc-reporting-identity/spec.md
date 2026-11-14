Task ID: DAA-013
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 DAA-013 r1 按 STD 实施。交 Development 按第 3、4 节实施与自检。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 一台 DAA 为多台本机 PLC 分别保存完整上报身份，并通过同一队列逐份上报
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本稿第 4、5 节及 Development Lifecycle Workflow
Depends On: 当前 DAA `plc-facts/v2` 单样本上报和 ARCH-ACQ-004 r2 的本地绑定基线
Related Task: DAA-010, DAA-012, ARCH-ACQ-004
Created: 2026-11-13 Asia/Shanghai

# DAA 多 PLC 上报身份

## 1. 目标与基线

一台 DAA 可对多台已配置本机 PLC 分别填写后端登记的 `plcId`、`instanceId` 和 `sourceGeneration`。上报设置中可看到各台 PLC 及其各自的三项参数和本机已生效的 DB。一次保存全部绑定，随后通过原有「开始 / 继续」逐份发送所有符合条件的样本。两台 PLC 可以填写相同或不同的 `instanceId`。

当前设置界面按本机 PLC 切换编辑，整个 profile 共用 `instanceId`。修改实例会清除其他绑定的代次，粘贴要求旧 `dbNumbers` 覆盖本机 DB。SQLite 的 `reporting_generations` 已为每个 `(plc_id, source_generation)` 保存实例与本机 PLC 归属，`reporting_bindings` 已保存当前指向，`reporting_cycles` 已能记录采集轮开始时捕获的完整三项。样本 POST 和回执本来就是逐样本合同。 [上报设置](../../src/components/console/FactsDeliveryDialog.vue) · [本地结构](../../src-tauri/src/infrastructure/local_store/schema.rs) · [样本账本](../../src-tauri/src/infrastructure/local_store/sample_upload.rs) · [v2 开发合同](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json)

ARCH-ACQ-004 r2 的隔离 QA 提供本地兼容基线。本稿起草时，该任务 r3 草案 R3-05 采用 profile 共用 `instanceId`。本稿按 Human Owner 最新要求采用每台 PLC 独立填写完整三项。r3 的拟定服务端准入已按单条 PLC 登记匹配三项。跨任务的 Web 说明、文档及联合验收口径由各自协调者对齐。DAA 本轮可使用现有样本合同和隔离合成回执完成，后端 r3 实施、采用及联调另由所属会话负责。 [ARCH-ACQ-004 草案](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/spec.md#3-webdaa-与说明同步) · [r2 独立验证](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md)

## 2. 需求

**R01 逐台填写、粘贴和查看。** 复用「上报与存储 → 上报设置 → 上报来源」。用紧凑的列表表单展示活动配置中的本机 PLC，每台一行，显示本机 PLC 名称、完整三项及其已生效 DB。在现有最小窗口内保持行内布局，必要时可横向滚动查看和编辑字段。根据活动配置中启用点所属的 DB 显示实际编号。暂不在活动配置中的已保存绑定也显示，用原本机 PLC ID 和空 DB 状态兜底。绑定以稳定本机 PLC ID 定位，同名也能区分。保留全局服务地址、路径、间隔与现有保存动作。每台三项可手填，也可将对应 Web 接入参数粘贴到该行，填入草稿后再保存。粘贴接受 `{"instanceId":"daa-01","plcId":"PLC-A","sourceGeneration":"gen-1"}`，兼容附带旧 `dbNumbers` 的对象，仅取三项，DB 列表以本机活动配置为准。取消保留原设置，粘贴失败保留全部草稿字段。

**R02 设置校验与持久化。** 新设置的每条绑定携带本机 PLC ID 及独立三项。全空代表未绑定，部分填写禁止保存并指明该 PLC。沿用 v2 三标识校验（1–128 UTF-8 字节、禁止首尾空白及 ASCII 控制字符、精确保留大小写和原始字节）。每个本机 PLC 最多一条绑定，同一 `plcId` 不能被两台本机 PLC 同时绑定，不同 `plcId` 可以复用同一实例或代次字符串。同一个已使用的 `(plcId, sourceGeneration)` 继续受已有实例、本机 PLC 与序号连续性约束。为同一 `plcId` 更换实例时需该 PLC 的新代次。复用设置版本校验和单次 SQLite 事务，过期版本、非法绑定或事务失败保留此前整组配置。改一台或粘贴到一行只影响该台，重开后读回所有绑定。保存延续当前停传与显式开始的语义，按原路径结算在途回执。

**R03 从采集轮到发送确认。** 新一轮开始时，以当前轮的本机 PLC 获取已保存的三项，并随完整采集轮持久化。跨设置保存的在途采集轮沿用开始时捕获的绑定。一个 PLC/DB 样本一个 `plc-facts/v2` POST，经现有单 worker、有界队列、重试及逐样本回执结算。选择、填写或查看某一行只影响设置界面，开始和继续作用于全部合格来源。现有 settings 与 source IPC 随端到端类型读取并保存逐台实例。开始 / 继续和现有同目标核对使用设置版本与完整来源集合，每条确认含 `instanceId`、`plcId`、`dbNumber`、`sourceGeneration`，覆盖当前活动绑定及合格历史待传来源。去掉确认文案中的单一全局实例，保留完整目标与合同。过期或不完整的确认仍拒绝发送。确认是操作者对照实际目标登记的动作。

**R04 旧配置和待传数据保护。** 首选直接复用 runtime4 的 `reporting_bindings`、`reporting_generations` 及 `reporting_cycles`，逐绑定查验实际实例与本机归属，同时更新 `full_check` 旧全局实例校验。已合法保存的共用实例配置可从对应代次记录读出每台完整三项，直接保留各自身份，无需重填。暂不在活动配置中的已保存绑定同样参与完整设置读回，保存其他行时保全。复用 config2/runtime4、既有锁、凭据、指纹和已知前驱准入路径，本稿允许的增量限既有结构内的读取、校验和设置写入。若确有新增 DDL、版本或 profile 迁移的必要，提出具体缺口和兼容影响，由 PM 修订范围。旧 runtime2/3 沿既有准入保留本地采集与历史边界，不在原地开启 v2。

- 原有无 `reporting_cycles` 标记的前驱样本继续按原身份和资格处理。带全空标记的仅本地样本仍仅本地。已有上报标记的样本使用采样时的原三项。保存新绑定后，按所属 PLC 的新身份处理后续采样。配置版本、历史样本、原序号、观察时间、冻结请求正文、摘要、已结算回执与历史尝试原样保全。
- 未冻结待传可以尚无目标与正文，首次发送仍依原规则冻结。已尝试或结果未知的样本不得因本轮设置保存、重开或继续而改投或重编码。只有匹配原尝试、合同、实例、样本及原绑定的有效 `committed` / `created|duplicate` 回执才能确认。旧身份已失去准入时按现有错误路径保留待核对记录。显式同目标重绑仍由原核对流程控制，本稿不扩大其适用条件。

## 3. 实施范围与风险

以下路径相对于 `automation-world/data-acquisition-agent/`。批准范围限 R01–R04 的必要改动。

| 归属 | 实施允许文件 |
| --- | --- |
| 设置与确认 | `src/components/console/FactsDeliveryDialog.vue`、`src/console/composables/useLocalAcquisitionConsole.ts`、`src/services/factsDelivery.ts`、`src/locales/{en-US,zh-CN}/common.json`、`src/styles/app.css`（仅上报设置或确认布局） |
| 本地 IPC、设置与校验 | `src-tauri/src/commands/local_delivery.rs`、`src-tauri/src/domain/sample_upload.rs`、`src-tauri/src/services/local_delivery.rs`、`src-tauri/src/infrastructure/local_store/sample_upload.rs`。改动限逐 PLC 身份读取、保存、校验及来源确认。 |
| 定向回归 | `tests/facts-delivery.test.mjs`、`src-tauri/src/services/local_delivery_tests.rs`、`src-tauri/src/infrastructure/local_store/{sample_upload_tests,tests}.rs`，以及独立临时合成夹具 |
| 用户说明 | `STAGE_C_GUIDE.md`、`STAGE_C_GUIDE.zh-CN.md` 中当前 v2 上报设置和核对步骤。与 ARCH-ACQ-004 协调同段写入归属。 |
| 任务记录 | 本任务 `tasks.md` 由 Development 创建，`checklist.md` 由 fresh-context Verification 创建。协调者按实际阶段维护 DAA PLAN 和任务目录索引。 |

复用现有采集和活动配置、SQLite 账本、样本合同、目标设置、上报启停及现有诊断。后端、Web 登记流程和发布合同由 ARCH-ACQ-004 维护。本稿排除新登记或查询接口、DB 授权配置、额外开关、新队列、批量发送、采集驱动调整、容量及重试政策改造、共享 UI 组件改造和依赖调整。DAA-010 r5 总体仍按 QA2 `qa_failed` 记录，首次建库发现 F-R5-QA2-001、r6 待审例外及原生联调归原任务。DAA-012 r1 的独立 `qa_passed` 与待 Owner 终验也按原记录处理。 [DAA-010 验证](../DAA-010-sample-facts-upload/checklist.md#独立验证-qa2) · [DAA-012 验证](../DAA-012-startup-warning-cleanup/checklist.md#human-owner-最终验收)

**并行与运行。** 记录正式源码树起点及并行差异。与 ARCH-ACQ-004 协调重叠的设置界面、文案、测试和指南，同一处由明确归属的角色修改并按小块审计。Development 和 QA 在各自 `/private/tmp` 下用合成 profile、独立构建目录及空闲回环端口验证。现有 Vite `15191` 由用户使用，保留其运行及端口，验证使用独立实例或构建。整合前核对是否有原生进程正使用该源码或 Vite。若整合会触发用户进程重启，保持候选隔离至可安全整合的时点。若热更新可能出现新旧 IPC 混用，验证其拒绝误保存和误发送，或在现有运行方允许的安全时点整合。临时验证的有效变更须回到正式工作树并核对实际候选差异。既有 `.local/dev`、默认或其他用户 profile、私有 `.env`、当前待处理样本及已有服务均排除在本轮运行范围。实际采用、启停现有服务、真实补传、MySQL、真实后端或设备操作及发布另行明确批准。

**兼容与回退。** 在合成配置上记录新版读取旧单实例格式，以及旧程序或等效旧准入路径面对新设置的行为。若旧版本无法表达混合实例，验证它在业务写入和发送前安全拒绝，保留原配置和队列。回退只使用已证兼容的版本和数据副本，无法安全回退时保留原始数据并前向修复。Windows 10/11 x64 原生验证留给 Human Owner 后续实测。开发验收只记实际可复现的隔离范围。

## 4. 验收

| 编号 | 可复核结果 |
| --- | --- |
| AC01 逐台配置与布局 | 用真实构建的设置界面和合成 IPC 配置本机 A、B。A 手填、B 分别用三项 JSON 和带旧 `dbNumbers` 的 JSON 粘贴，且本机 DB 以活动配置为准。两台 PLC 各有一行可检查完整身份，编辑 B 或粘贴失败不会串改 A。覆盖取消、三项部分填写、非法标识、重复 `plcId`。中英文切换，最长 128 UTF-8 字节标识和当前 960 × 640 最小窗口下，字段可检查，保存、关闭及确认可操作。 |
| AC02 同异实例、持久化与确认 | 同一 runtime4 profile 保存两台不同实例，再验证两台可用相同实例和相同代次字符串（不同 `plcId`）。保存后重开，逐台身份与 DB 可核对。只修改一台并重开，另一台及暂不活动的已保存绑定均保留。过期设置版本、同 PLC 旧代次换实例和错误确认被拒绝。设置及来源 IPC、开始及继续提交完整来源集合，每条含对应实例，包含合格的历史待传来源，保存本身零新派发。 |
| AC03 多来源逐样本回执 | 用 Rust 真实采样持久化与既有 worker 接隔离回环 HTTP，A、B 各至少一个 DB，并让一台覆盖两个 DB。一次显式开始后各合格样本分别 POST。核对请求对应的 PLC、DB、实例、代次、样本 ID、序号与有效回执，错实例或错样本回执不能确认另一条记录。至少一份结果未知样本恢复时复用原字节并取得匹配回执。未绑定轮留在本地。 |
| AC04 旧库与冻结材料 | 用旧合法共用实例的合成 SQLite（含前驱无标记、仅本地、有上报标记的样本），以及未冻结待传、已冻结未发送、尝试后未知和已确认各态验证重开与编辑。核对原标识、样本 ID、序号、原文、已有目标、冻结正文摘要及回执。配置生效前已开始的采集轮使用旧绑定，后续新轮用新绑定。迟到回执只结算原尝试。抽查已支持 runtime2/3 本地读取与 v2 限制、旧版准入对不同实例设置的结果和数据保全。 |
| AC05 正式候选与边界 | 用项目锁定的 pnpm/Cargo 跑 Vue/IPC 定向测试、`pnpm build`、`cargo fmt --check`、锁定的 Rust 定向测试与 `git diff --check`，记录实际命令、环境、退出码、候选差异及原有失败。核对双语当前操作步骤、allowlist、未触达用户服务和 profile。独立验证区分 Vue/合成 IPC、Rust/真实 SQLite、回环 HTTP 与 Windows、真实目标的证据边界。 |

## 5. 修订、批准与交接

2026-11-13（Asia/Shanghai），PM 提交 r1 待审，提出复用现有来源代次记录以及按本机 PLC 紧凑列表编辑的方案。当时为 `draft`。Development 加载 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 的适用部分，使用已锁定工具链，先对齐并行编辑与候选基线。Development 在 `tasks.md` 交付精确工作树、改动、自检与剩余限制。fresh-context Verification 按相同 Revision 和候选独立复核，将结论交 Human Owner 最终验收。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)

同日，Human Owner 对上报设置草图回复「界面可以，我接受」，确认本机 PLC 每台一行，三项参数可按行独立填写或粘贴，并确认 R01 的三参数 JSON 示例。当时实施范围仍待精确批准。

审阅时提供的建议批准用语

> 批准 DAA-013 r1 按 STD 实施每台本机 PLC 独立填写和保存 `plcId`、`instanceId`、`sourceGeneration`，复用现有上报设置、SQLite 和逐样本队列。批准第 3 节允许范围和第 4 节隔离合成验证。实际 dev profile、待处理样本、现有服务、后端和设备操作另行批准。

2026-11-13（Asia/Shanghai），Human Owner 批准下列精确任务与修订。获批草案 SHA-256 为 `9dbf962eb7518f3d2787a507ca5c7dfa4028d904eed9eb22b3e2e116bbbce9b0`。批准原文如下。

> 还是STD吧，批准 DAA-013 r1

交 Development 执行第 3、4 节。验证使用临时合成 SQLite 与隔离回环 HTTP。Docker、MySQL、真实后端和现有 `.local/dev` 排除在本轮运行范围。
