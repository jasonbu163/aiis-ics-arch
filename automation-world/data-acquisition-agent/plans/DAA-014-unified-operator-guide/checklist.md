Task ID: DAA-014
Revision: r1
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: Human Owner 已最终验收 DAA-014 r1 文档
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-014 r1 独立文档核验 · QA1

**结论：`qa_failed`。** AC01 的停采上报步骤不能按文档从单个未冻结样本详情核对上报身份，并将一类可在显式确认后改用新目标的待发送样本写成目标已固定。AC03 的现行入口和历史锚点静态可达；新找回的 DAA-010 r5 英文原文尚未纳入仓内恢复路径。无环境阻断，具体返工见下。

## 1. 验证输入与范围

2026-11-14（Asia/Shanghai），命名 Verification `/root/daa014_verification` 在 fresh context 接收 r1，独立阅读根和最近作用域项目规则、README/PLAN/任务目录、已安装角色 TOML、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、完整交接 bundle、正式树差异及相关源码/历史。使用 `project-governance`、`aiis`，按界面和 API 表面用 `frontend-ui`、`i18n-workflow`、`backend-arch` 复核。角色 profile 是 `contract_only`；模型和 effort 仅按 TOML 配置可读。

| 输入 | 独立核准结果 |
| --- | --- |
| 正式树 | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `fd999224a8756feda314a33148304b4bf3461876`。其他任务的未提交文件不归入本任务。 |
| [Human Owner 批准的 spec](spec.md) | SHA-256 `f34640c33b162851c8534e29b6793a81e9af638ef3eaf506575ddb878e0d736d` |
| [Development handoff](tasks.md#5-变更文件与-developer_handoff) | SHA-256 `b926f0bc7974b48f036533d3ebad6dbd5d9be0a9aa49569512141a632d9e7dee`；§5 的 25 份文件逐一匹配，包含四份历史快照。本任务精确交付见清单，Git HEAD 不代替交付摘要。 |

## 2. 验收与发现

| 验收项 | 独立结论 |
| --- | --- |
| AC01 | **失败，F-001、F-002。** 双语简明 README 都进入各自语言的统一手册；两手册章节、六个启动/读取代码块涉及的对应命令及主要 DAA/Web 标签一致。合成示例的 `MinimalImport`、`MinimalPayload` 和三叶类型匹配仓内夹具，按标准布局是 DB21 8 字节（BOOL 0.0、INT 2、REAL 4），DS 另有建模/显式加载说明，DAA 配置保存/激活与连接/采集各有入口。并行验收明确在两项仍运行时核对新 `sampleId` 的确认与计数增长，再暂停和核实回执/历史。 |
| AC02 | **通过，限静态。** 手册每台本机 PLC 各有一行、各填三项；不同 PLC 可用相同或不同的实例 ID，上报用 PLC ID 不可重复。Web 的接入参数复制三标识，DAA 粘贴只填三项，页面 DB 来自活动本机配置，逐 PLC 开关不停止采集。通用指南集中解释登记/接管/删除、两表、第三方 POST、补传和最新值及完整历史 GET；DAA 专属流程留在手册。现行 [管理路由](../../../../backend/app/plc_facts/api/source_registry.py#L81)、[准入](../../../../backend/app/plc_facts/crud/async_source_registry.py#L14)、[提交与读取](../../../../backend/app/plc_facts/services/async_v2.py#L29) 与 [v2 合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) 对应：按三标识准入、`sourceType` 为标签、DB 属样本；提交后匹配回执，历史独立于登记按有效期读取，最新值受活跃来源及逐点采样顺序约束。 |
| AC03 | **部分通过，F-003。** 按 spec §5 和 tasks §2 转交，两项手测及调试在旧入口退役前已收尾。四条 B/C 旧路径都先指向同语言新手册；日常 README 和适用引用已退出旧操作流程，双语现行入口可达。旧 `#L5/#L40/#L82/#L86/#L97/#L102`、`#m01-launch/#m01新配置及来源交接` 和双语第 6 节入口静态可解析；原行号以各自精确版本为准。仓内四快照均匹配；DAA-007 双语 HEAD 原件、DAA-008 r4、DAA-011 QA1/QA2、DAA-013 QA4 英文及 DAA-010 r5 中文经独立重算。DAA-010 英文新找回证据尚未持久化。 |
| AC04 | **通过，限文档检验范围。** 25 项清单全是获批文档与证据；对比受触达的已跟踪文档，交付是文档收敛和链接变更，PLAN/目录中的其他任务差异属共享树既有工作，不把全树差异归入本任务。Development 的命令、结果和限制见 tasks §4；本轮独立检查见下。手测来自 Human Owner 转交，产品、配置和运行资源未操作。 |

### F-001 · 未冻结样本详情不能核对逐条上报身份

[英文 §4 第 1–5 步](../../USER_GUIDE.md#L68)与[中文对应步骤](../../USER_GUIDE.zh-CN.md#L68)要求在「本地历史」或「上报记录 → 查看样本」选一份绑定后样本，并核对采样时的上报实例、PLC 和代次。按同一步的回退路径，保存绑定、短采后暂停，而且此前上报一直停止，新样本仍未冻结。这时 [runtime.rs](../../src-tauri/src/infrastructure/local_store/runtime.rs#L195) 将三项独立存入 `reporting_cycles`，[原样本正文](../../src-tauri/src/infrastructure/local_store/runtime.rs#L107)仍是本机实例、PLC 和代次；[详情 IPC](../../src-tauri/src/infrastructure/local_store/runtime.rs#L325) 只有已有 `sample_uploads` 行才返回 `sampleUpload` 上报身份，[查看样本组件](../../src/components/console/LocalSampleDetail.vue#L35)按此有条件显示。[投递详情查询](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L100)在该情形仅有本机 PLC 等信息，正文和原目标为空。

[开始/继续确认框](../../src/console/composables/useLocalAcquisitionConsole.ts#L174)真实可核对本次 URL、合同以及[去重后的待传/活动来源与 DB](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L417)，不将某一 `sampleId` 映射到某行。返工应分别写清本机样本可见字段、发送前核对的全部来源和当前 URL、冻结或已尝试记录可见的逐条原信息、收到回执后的逐条核对。Web 历史明确用冻结请求中的**上报用 PLC ID**（合成例 `PLC-A`），本机名称 `DEV-PLC-A` 或本机 PLC ID 不能代用。无法核对目标和来源时停在确认前。

### F-002 · 区分未尝试与已尝试记录的目标规则

[两种语言 §4 第 2 步](../../USER_GUIDE.zh-CN.md#L69)将“已冻结或尝试”一并写为原目标保留。[显式确认实现](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L138)可对 `prepared` 且 `attempt=0` 的记录更新目标 URL，正文和身份保持；确已尝试且未确认的记录有原目标约束，未知结果的单条换址另走[同目标确认入口](../../src/components/console/FactsDeliveryDialog.vue#L69)。按 R02 区分这两种状态，避免操作者把未尝试记录看成固定向旧地址发送。

### F-003 · DAA-010 r5 英文精确候选缺少持久恢复路径

[历史追溯表](tasks.md#3-旧指南历史追溯)准确说明交接当时英文尚未定位；固定 Git 及四快照中的其他版本均不能代用。本轮协调者从原 DAA-010 工具证据恢复英文，Verification 重算 `34,534` 字节、SHA-256 `2302cb15f374b9f29d4bda8715f69f8ce6d0323f6c37a8729208e4292d1ba35a`，与[原暂停清单](../DAA-010-sample-facts-upload/tasks.md#L246)匹配。与仓内 DAA-013 QA5 英文从 `m01-launch` 起后缀逐字节相等；差异仅在前文四个统一差异段。仓内可复现的精确证据仍缺这一版，不能把新恢复出的临时文件当长期路径。返工可在四快照上限内用既有快照及可重建的最小反向差异提供追溯；旧任务状态和证据记录不改写。其余旧文件的追溯结论不受该缺口影响。

## 3. 命令与证据

macOS 15.7.7 / Darwin arm64，Git 2.50.1、Python 3.9.6、zsh 5.9，均从仓根执行；脚本经 stdin，未安装依赖。

| 实际检查 | 结果 |
| --- | --- |
| `git rev-parse HEAD`、`git branch --show-current`、`git --no-optional-locks status --porcelain=v1 --untracked-files=all`；`python3 -B -` 解析 tasks §5 并重算 SHA-256；`git --no-optional-locks diff --check HEAD -- <18 份已跟踪交付文档>` | exit 0；批准后 spec、exact tasks 及 25/25 摘要匹配。18 份 tracked 文档无空白错误，3 份新现行文档行尾合格；四历史证据按原字节验摘要。 |
| `python3 -B -` 扫描仓内相对链接、标题及显式锚点；`rg` 反查原 B/C 文件引用 | exit 0；23 份文档共 331 处相对引用和 29 处历史 checklist 入链均静态可达，另查旧指南锚点使用及日常推荐路径。历史原件内部链接仍按原目录解释；未验证浏览器渲染或历史版本内容等同于旧入口当前行号。 |
| `python3 -B -` 提取 shell/JSON，逐块调用 `/bin/zsh -n` | exit 0；双语 README 和手册的四个启动块、通用指南两个读取块均语法通过，两个 JSON 样例的合同、实例、样本与回执匹配。只解析，无命令执行。 |
| `python3 -B -` 对照实际两语 locale、合成 DB/UDT、Tauri 配置和锁文件，并读合同 OpenAPI | exit 0；两语各六节，主要控件标签均存在；三点、正常 Tauri S7 feature、pnpm 锁文件可定位；开发合同一条无 Bearer POST 和五条无 Bearer GET，来源管理 GET/POST/PATCH 为已认证入口（删除走 PATCH）。 |
| `git show fd999224a8756feda314a33148304b4bf3461876:<原 B/C 路径>` 与 `python3 -B -` 内存复原并计算 SHA-256 | exit 0；阶段 B 原件及 DAA-011 QA2 双语均匹配 tasks §3；按 DAA-011 checklist 的提示行和后缀重建 DAA-008 r4（23,039 / 20,583 字节）、逆向三行重建 DAA-011 QA1、从 QA5 逆向两处重建 DAA-013 QA4 英文、应用 tasks 的差异重建 DAA-010 r5 中文（30,728 字节，复核 L40/L97），皆匹配各自原摘要。未写临时复原文件。 |
| `git log --all --format=%H -- <旧英文路径>`，重算两份 Git 版本/四快照；`shasum -a 256 /private/tmp/daa014-daa010-en-_u1kus0d/STAGE_C_GUIDE.md` | exit 0；仓内版本不匹配旧 DAA-010 英文摘要；协调者新取回副本匹配，见 F-003。 |

## 4. 限制、资源与交接

[tasks §2](tasks.md#2-human-owner-手测转交) 所记 Human Owner Mac/dev 手测：停采时处理 6 份待发送和 1 份未知，统计 `0/0/0/7`；并行时确认数已经增长，停采并排空后 `0/0/0/31`。两次抽查 `committed/created` 与 Web 同份 `sampleId` 的点值、质量一致；Owner 暂停两项并选择保留 31 条样本。这是转交的观察，本次独立 QA 未重新构建、启动、采集、发 HTTP 或访问配置、MySQL、SQLite、设备及样本。DAA-010 r5 独立 `qa_failed`、Windows 原生、完整阶段 C、实际部署/生产等边界维持各自 gate。

Verification 只写本 checklist，未创建任何临时文件、环境、分支或 worktree，未清理资源。tasks §4 所列两处先前协调者恢复目录在本轮路径检查时已不存在；新增英文恢复目录 `/private/tmp/daa014-daa010-en-_u1kus0d` 归协调者，需保留至仓内已可以按原摘要精确复现、独立复验完成且无剩余依赖，再由协调者按资源规则核对后收尾。

返工交回 Development：修正双语步骤并在本任务范围内固化目前的英文恢复证据，记录新交付摘要和必要文档自检后重新 handoff。保留本轮失败记录，经新的 fresh-context Verification 复验再交 Human Owner。

## Human Owner 最终验收

待独立复验通过后由 Human Owner 决定。

# DAA-014 r1 独立文档复验 · QA2

**结论：`qa_passed`，限 DAA-014 r1 文档。** AC01–AC04 通过；QA1 的 F-001、F-002、F-003 均关闭，无 blocker。上文 QA1 原失败及发现保留，当前状态以上方元数据和本节为准。

2026-11-14（Asia/Shanghai），命名 Verification `/root/daa014_qa2` 在新的 fresh context 独立读取消费仓规则、作用域 README/PLAN、Verification TOML、canonical workflow、完整 bundle、正式工作树和差异；按 `project-governance`、`aiis` 复核，界面与 provider 对照使用 `frontend-ui`、`i18n-workflow`、`backend-arch`，并追到现行 Rust 存储和投递判断。角色为 `contract_only`。正式树 `main`，HEAD `fd999224a8756feda314a33148304b4bf3461876`，macOS 15.7.7 arm64 / Git 2.50.1 / Python 3.9.6 / zsh 5.9。

| 验证输入 | 独立核对 |
| --- | --- |
| 获批 [spec](spec.md) | SHA-256 `f34640c33b162851c8534e29b6793a81e9af638ef3eaf506575ddb878e0d736d`。 |
| [返工 handoff](tasks.md#6-qa1-返工与英文历史原文) | SHA-256 `0d34b37abbc66de3565a6e5ba67147d00b27cd0f1a11f309c875af525dcc0693`；交接时现行 25/25 逐项匹配。原 §1–5 字节摘要仍为 `b926f0bc7974b48f036533d3ebad6dbd5d9be0a9aa49569512141a632d9e7dee`；两清单之间仅双语手册 2 项变动，23 项字节不变。 |
| 接手时 QA1 checklist | SHA-256 `972ddaff594b417ef2f006ba90d13d18a6c51289889885f9f5b70af52ba1e247`；保留原 QA1 正文，只有顶端当前状态和 handoff 更新，并追加 QA2。 |

| 验收项 | 独立复验 |
| --- | --- |
| AC01 / F-001 | **通过，关闭。** [英文 §4](../../USER_GUIDE.md#4-manual-check-one-send-backlog-with-collection-paused)与[中文 §4](../../USER_GUIDE.zh-CN.md#4-手测一停采后发送积压)先从本机样本核对 ID、PLC、DB、时间、值和质量。原采样正文保存本机身份，上报身份另存 `reporting_cycles`；无 `sample_uploads` 行时详情没有逐条上报身份。[开始/继续确认框](../../src/console/composables/useLocalAcquisitionConsole.ts#L174)展示当前 URL、合同，以及由[积压和活动配置去重得到的来源与 DB 集合](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L417)，没有逐条 `sampleId` 映射。手册要求核不清即取消；发送后从冻结请求核对上报身份，验证匹配 `instanceId`、`sampleId` 的可靠回执，且 [Web 历史](../../../../frontend-js/src/app/acquisition-data/views/history/index.vue#L26)按上报用 PLC ID（例 `PLC-A`）及 DB、采集时段核对同一 `sampleId`。双语 §2 合成采集流程和 §5 并行手测、暂停及查看步骤仍成立。 |
| AC01 / F-002 | **通过，关闭。** 双语 §4、§6 把已冻结 `prepared` 且 `attempt=0` 的样本与已尝试样本分开。[显式确认更新](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L138)对该状态只改 URL，不改身份、正文；选择既有冻结件要求其目标一致。已尝试未确认记录保留原目标；仅结果未知的单条样本走[同一目标确认](../../src/components/console/FactsDeliveryDialog.vue#L69)和[重绑校验](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L371)，部署配置须能证实同一逻辑 provider 和数据库，连通或 GET 不作证明。 |
| AC02 | **通过，限静态。** 双语手册各 PLC 独立保存三标识与上报开关，显示的 DB 来自活动本机采集配置；共用指南说明 Web 管理、单样本 POST 和可靠回执。重新核对 [准入](../../../../backend/app/plc_facts/crud/async_source_registry.py#L14)、[提交服务](../../../../backend/app/plc_facts/services/async_v2.py#L29)及 v2 合同：三标识匹配，`sourceType` 为标签，DB 属样本；提交后回执，最新值按活跃来源和逐点顺序，未过期历史独立于登记。 |
| AC03 / F-003 | **通过，关闭。** 四条旧 B/C 入口先到各自语言的新手册，日常入口与受影响的旧链接可达；旧行号不充当原文，其他历史版本追溯沿用 QA1 已核对且字节不变的证据。只从仓内两份 QA5 快照分别应用 tasks §3 中文 / §6 英文的零上下文差异，内存重建 `STAGE_C_GUIDE.zh-CN.md` 30,728 字节、SHA-256 `0fe51b3153c115b146c50d86a7333475ff1fc139ae8ab8903a105b518bbff4e1`，`STAGE_C_GUIDE.md` 34,534 字节、SHA-256 `2302cb15f374b9f29d4bda8715f69f8ce6d0323f6c37a8729208e4292d1ba35a`，均匹配 [DAA-010 r5 原暂停清单](../DAA-010-sample-facts-upload/tasks.md#L246)。中文原行 40/97 和英文 M01 锚点可定位；仍仅四份完整历史快照。 |
| AC04 | **通过，限文档。** 返工未扩大范围。DEV 自检与本轮独立检查分列；共享工作树其他源码、测试和任务的改动不归入本次交付。 |

独立命令均在仓根执行：`git --no-optional-locks status --porcelain`、`git rev-parse HEAD` 和 `git --no-optional-locks diff --check HEAD -- <18 个已跟踪交付文档>`（exit 0）；`python3 -B -` 从两份交接清单逐项核对摘要、行尾、24 份文档中 355 个仓内链接及锚点（0 缺失），检查双语六节并以 `/bin/zsh -n` 解析 6 个 shell 块，解析两份匹配的请求/回执 JSON（exit 0；未执行示例）。另一段 `python3 -B -` 逐段验证统一差异的行号、旧字节和增删行数，在内存重建两份 DAA-010 原文并对照原任务摘要（exit 0）。JSON 检验首次误把字段写成 `contract`，核对合同后改用 `contractVersion` 复跑通过。未使用或生成临时证据。

两次 Mac/dev 手测仍是 [Human Owner 观察的转交](tasks.md#2-human-owner-手测转交)。本轮没有构建、启动或停用应用与服务、运行 HTTP、访查实际 profile、SQLite、MySQL 或 PLC，也未操作 Owner 保留的 31 条样本。DAA-010 r5 独立 `qa_failed`、Windows 原生、完整阶段 C、实际采用及部署保持各自 gate。

只修改本 checklist。新手册及历史复现不依赖 `/private/tmp/daa014-daa010-en-_u1kus0d`；Verification 未读取该目录的原文或执行清理。独立复验后，协调者转交：该目录仅含本任务英文恢复文件，其摘要与原记录一致，已核对归属、权限、挂载及占用并移除单文件和空目录（exit 0）。Verification 只复查该路径及原 QA1 中列出的另外两处恢复目录均不存在（`python3 -B -`，exit 0）。无待留存的任务临时证据。下一 gate：Human Owner 对 DAA-014 r1 文档作最终验收。

### QA2 后索引同步复核

协调者在 verdict 后同步 DAA 的 PLAN 及 plans 目录双语索引。以同步前独立读取的字节为基线，`python3 -B -` 逐行比较并重算 SHA-256（exit 0）：四份均只变更第 9 行 DAA-014 r1 状态和链接，标记 `qa_passed`、待 Human Owner 最终验收，spec、tasks、checklist 三个链接均可达。其余行逐字节相同；这四处是交接摘要之后的机械状态同步，不改变本轮实质交付。

| DAA 索引 | 交接时 SHA-256 | 同步后 SHA-256 |
| --- | --- | --- |
| `PLAN.md` | `ec8438c49f7d935869e81a15ed6c2a8cda0a809609319ba074c257cab527ae6a` | `ae4f32917e49a2cec28461d817aa9d10dbb79ca2b0c58b0f0ecbde8d6e38f61b` |
| `PLAN.zh-CN.md` | `f4577eb4d5ae0b9019c19e23081156469011b2a247989d82581a1387f54aac79` | `3244a42a32356b1a6fdf3c87213f24fc70fa92a3dd2b51f2820d7de301cd3bd1` |
| `plans/README.md` | `048623bcdd94147635fbaa744be8bc587a94bc9b1b2051ccf8a00d518310ba85` | `c62034f75e5823d10fd678b8ea7e89819bb42c596d7bc54fb4ce7c5a131f45c5` |
| `plans/README.zh-CN.md` | `6f07d38991cd2e313d7561bb7575d1a1cfa11b765e10b7d9e10b4824bc1e6a2f` | `66a0dea03ac0ed348dcb4267ee5561db61220441bea59284f67e4c9d927fbc01` |

## Human Owner 最终验收 · DAA-014 r1

2026-11-14（Asia/Shanghai），Human Owner 明确验收 DAA-014 r1。

> 验收 DAA-014 r1，统一手册和采集数据指南符合要求。

本次验收范围为 DAA-014 r1 文档，包括双语统一手册、采集数据通用指南和已获批的旧入口及历史追溯处理。状态为 `owner_accepted`，保留 QA1 失败与 QA2 通过的原始记录。登记前 checklist SHA-256 为 `72fde39dc68537a74073302b0db774977386601e9e8f050de75e9f5855c6b4ff`。spec 和返工 tasks 的摘要仍与 QA2 记录一致。

DAA-014 基线记录在 [QA2 交接清单](tasks.md#返工后的精确交接清单)。验收登记时，共享树四份 DAA README 和使用手册已包含 DAA-015 的并行增量，现行摘要与 [DAA-015 文件清单](../DAA-015-startup-automation-and-workbench/tasks.md#4-文件摘要)所列新摘要一致。彻底删除旧入口、Windows 单页与英文通用采集指南属于后续文档范围。DAA-010 r5、Windows 原生验证及阶段 C 各有验收记录。

### 最终验收索引同步

协调者在验收登记后同步四份 DAA 索引。Verification 以同步前字节为基线，经 `python3 -B -` 逐行比较并重算 SHA-256（exit 0），每份只改第 10 行的 DAA-014 r1 记录。该行保留 QA2、记载 2026-11-14 最终验收，状态为 `owner_accepted`。spec、tasks、checklist 链接目标均存在，包含 DAA-015 在内的其余行逐字节相同。

| DAA 索引 | 同步前 SHA-256 | 同步后 SHA-256 |
| --- | --- | --- |
| `PLAN.md` | `44eedaf67dba36d461cc281686c092e0848398f97fed6bdb6ad49403eef2bb6f` | `f99881ff94fad51cc0a08090dfb12ab68eb96141ffceec05461047f06ae5b935` |
| `PLAN.zh-CN.md` | `539399972d7a377741b254ddfb10f7c6907d9042cc1e24d317461b9a94616782` | `dc6fe13907a4bf7da4db2dc5ed049fb32b04f9d8d8b615af5cda28125302249d` |
| `plans/README.md` | `9b24746684da956772a1d72e2eb2a04a81b5bf9f5baf6179181c7b42f32e7b86` | `d36bf2ba9e69716e7931f1b51ce402a82dbf73117f2c9723518e93ce6764a54d` |
| `plans/README.zh-CN.md` | `db0d295eaf1475000832d431dd29310acfcbdc2040770f40231f099d4f786bff` | `39a741ba6c6cce040bca71406f5b3f34c1ab57be36fb594d5e6bcbfb8f87832a` |
