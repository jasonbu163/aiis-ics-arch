Task ID: DAA-009
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> /root -> Human Owner 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 点位列表展示当次只读单点诊断的进度和结果
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-009 r1 独立范围批准、Development、fresh-context QA / Verification、Human Owner 最终验收
Related Task: aiis-ics-arch::DAA-008

# DAA 单点诊断反馈

## 1. 背景与目标

「单点诊断」使用已激活配置和已建立的连接，对所选点位做一次只读读取，帮助核对活动地址、解码值和质量。这次读取不会追加正式采集样本。Owner 报告点击后界面一直显示「处理中」，并要求先修这个问题，暂停后续联调。

现有点位按钮调用通用 `control`，它丢弃提交回执并写入通用 `pending` 提示。现有 1 Hz 快照已有带 `operationId` 的终态，但点位页没有跟踪它。主协调使用当前 Vue owner 与内存 IPC 替身复现了同一操作已完成、通用提示仍为 `pending`。诊断和快照合同依据见 [点位页](../../src/app/plc/views/points/index.vue)、[前端 owner](../../src/console/composables/useLocalAcquisitionConsole.ts)、[运行时诊断](../../src-tauri/src/services/local_supervisor.rs)、[点位解码](../../src-tauri/src/services/local_scheduler.rs)。

## 2. 需求

- **R01 同页反馈。** 点击行内「单点诊断」立即打开紧凑、可关闭的 Element Plus 弹窗，显示所选点位、操作用途和等待状态。该操作的反馈只进入弹窗。保持现有活动版本、已确认地址和连接准入，由运行时决定是否可读。点位启用、分组和周期采集不新增诊断门槛。
- **R02 对应本次点击。** 每次明确点击最多发一个现有 `daa_diagnose_point` IPC，请求绑定点击时的 `plcId`、`pointId` 和 `expectedActiveRevision`。识别回执中的 `operationId` 与即时终态，等待中的结果只从现有快照匹配本次 ID、PLC 和 `diagnose` 动作。结果绑定该次活动版本及点位。关闭或离开点位页即清理本次等待，晚到的回执或结果不重新开窗或影响另一次点击。
- **R03 显示读数。** 由匹配操作的 `result.points[DB 号][pointId]` 取点位事实。品质为 `good` 且实际值存在时，展示读数（含 `false`、`0`）、活动版 DB/偏移/位地址和类型、质量、实际观测时间。复用上海时间格式 `YYYY-MM-DD HH:mm:ss`，缺失用占位。读数地址与类型取回执中的 `definition`，不以草稿行补齐。
- **R04 可辨认的结束状态。** 区分提交拒绝、操作受阻/失败、已完成但点位读取或解码失败、缺少可用结果及界面等待超时。优先展示现有可本地化的原因（例如未连接、队列繁忙或解码失败）。点击后最多等待 15 秒，覆盖回执和快照两段；超时文案说明界面未在时限内收到结果。等待中阻止重复提交；超时、关闭及晚到结果均不触发重发、取消运行时或改变设备状态。
- **R05 轻量实现。** 沿用现有 Console 反馈容器、1 Hz 快照和动作按钮。诊断以外的通用通知、连接测试、连接/采集控制、点位草稿保存及激活沿用原行为。文案使用现有 PLC 模块中英文键和适用的共享原因标签。

## 3. 验收标准

| 编号 | 可核验结果 |
| --- | --- |
| AC01 | 点位行点击一次立即看到有点位标识的可关闭弹窗，只发送一次原 IPC，通用「处理中」提示不由本动作触发。快速重复点击不重复提交。 |
| AC02 | 内存 IPC 夹具给出 `pending` 回执及对应 `applied` 快照，分别验证 `false`、`0` 与活动地址/类型、质量和上海观测时间。夹具草稿地址与活动定义不同，显示仍取活动定义。 |
| AC03 | 即时 `blocked`、未连接 `failed`、IPC 拒绝、`applied` 携 `bad_read` / `bad_decode` 和缺失点位结果都终止等待，显示相应原因或缺失提示。 |
| AC04 | 无回执或仅 `pending` 的夹具在 15 秒界面期限结束。错误操作 ID、旧结果、其他 PLC/点位、关闭及离页后的晚到回执/快照不串单、不重开弹窗。随后一次明确点击可独立诊断。 |
| AC05 | 核对双语键及占位符、状态和错误映射，使用 DAA 现有依赖运行聚焦的内存 IPC 回归与 `pnpm build`。核对原点位编辑和通用控制入口及差异白名单，记录命令、退出码与验证边界。 |

## 4. 写入范围与保护

批准后，Development 仅可改动以下实现面，路径相对 DAA 目录：

- `src/app/plc/views/points/index.vue`
- `src/console/composables/useLocalAcquisitionConsole.ts`，限于单点诊断路径
- `src/services/localAcquisition.ts`，仅在需要时补既有 IPC 的前端类型
- `src/app/plc/locales/zh-CN.json`
- `src/app/plc/locales/en-US.json`
- `tests/point-editing.test.mjs`，限于诊断回归及其所需内存替身

`tasks.md` 和 `checklist.md` 分别在实际角色到达对应 gate 后创建。DAA 的双语 PLAN 和 plans 目录只由主协调机械同步任务索引。除这些角色文档和索引外，以此精确列表审计差异。

本任务限前端展示。排除 Rust、Tauri IPC 合同、依赖/构建配置、真实 `.env`、profile、SQLite、采集历史、PLC、DS、Backend、发布部署及阶段 B/C 重跑。`DAA-008 r4` 的 B01 联调保持暂停，已冻结候选、原始哈希和证据单独保留。本修复不启动、停止或重启既有应用/服务，不更换 B01 候选或继续后续步骤。

## 5. 风险、回退与交接

- 采用本次操作 ID、活动版本与点位绑定，以及独立的前端截止时间，避免误取旧值或无限等待。若当前开发窗口启用了热更新，前端源码变更可能刷新 UI。保留变更前相关源码哈希，并分开记载 B01 证据与本任务差异。
- 源码交付以正式 DAA 工作树为准。需要隔离验证时，只用既有工具链和内存 IPC 替身，验证产物放临时目录，核对正式交付源码与验证候选一致。回退只涉及本任务前端差异，执行回退另行批准。
- Development 和 Verification 采用 `frontend-ui`、`i18n-workflow`，并按 `backend-arch` 的状态及错误码规则消费现有 IPC。范围批准后由 Development 记录自检和精确交付差异。fresh-context Verification 独立复核 AC01–AC05 后交 Owner 最终验收。

<a id="owner-scope-approval"></a>

## 6. Human Owner 范围批准

2026-11-10（Asia/Shanghai）PM 形成 r1 草案，待 Human Owner 精确批准。

> 批准 aiis-ics-arch::DAA-009 r1，按 spec 修复单点诊断反馈并做内存 IPC 回归和前端构建。DAA-008 r4 B01 及后续联调继续暂停。
