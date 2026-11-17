Task ID: DAA-016
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 交 Development 按获批的 DAA-016 r1 实施与自检
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 旧文档入口退役、Windows 原生验证记录单和通用采集数据指南英文配对
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本稿 §4 和 Development Lifecycle Workflow
Related Task: DAA-007, DAA-008, DAA-010, DAA-011, DAA-013, DAA-014, DAA-015, ARCH-ACQ-004, ARCH-ACQ-005
Created: 2026-11-14 Asia/Shanghai

# DAA 文档收尾

[DAA-014 r1 终验](../DAA-014-unified-operator-guide/checklist.md#human-owner-最终验收--daa-014-r1)已接受统一手册及当时的通用指南。此次拟物理删除四个简短入口、补一份中文 Windows 原生验证记录单、补齐通用指南的英文配对。

**已批准的影响。** 当前有 38 条历史直链指向两份阶段 C 短入口，另有冻结快照中按原目录解释的相对链接。四个旧地址删除后，这些旧直链在当前分支无法直接打开。r1 保留历史记录和证据的原字节，并在本任务的 Development 记录提供一张追溯表。部分过渡版本只有已记录的 SHA-256 和观察，现有依据尚未确认可取回完整原文。若要求历史链接继续可点击，可保留相应短入口供历史跳转，由 PM 据此调整删除范围后再送审。

## 1. 需求

1. **R01 旧入口。** 删除 DAA 根目录的四个短入口。现行操作使用对应语言的 `USER_GUIDE`。实施前比对四个短页与 DAA-014 QA2 交接摘要；若他人已修改或新的候选仍依赖旧路径，先协调归属。按 §2 保留历史定位和短页本身的验收字节。
2. **R02 Windows 记录单。** 新增一份独立中文 `WINDOWS_NATIVE_VALIDATION.zh-CN.md`，供 Human Owner 后续在 Windows 10/11 x64 实机填写，目前状态为「待验证」。普通 PowerShell 操作沿用 `pnpm install --frozen-lockfile` 和 `pnpm tauri dev`，说明所需项目工具链、原生依赖、精确候选及受控模拟端和后端；复用统一手册的配置和手测章节。启动前显式选择新的独立绝对 `DAA_PROFILE_DIR` 并核对实际选中目录，避免使用现有 `.local/dev`、默认目录、配置、库及现有 31 条样本。简要列出新 profile 和配置激活、同一 profile 的独占锁、正常关闭/重开、采集及离线积压/恢复上报，按同一 `sampleId` 核对匹配的已提交回执及 Web 历史。将发送与确认之间退出、SQLite 写入期间的热 journal 分列，给出受控前置条件和停止、保全及未测记录方式。保留系统版本、候选、合成环境、步骤实测结果和脱敏证据位置的留空栏。现有 [DAA-010 AC08 及 §7](../DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续)继续定义后续原生验证。
3. **R03 英文通用指南。** 逐节配对现有中文八节，保留流程图、字段与时间语义、来源登记/接管/删除、后端两表、第三方请求及匹配回执、常见错误和 GET 示例。核对现行 [PLC facts v2](../../../../contracts/published/http-api/plc-facts-v2/README.md)、[数据 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev-r4.json)、[管理 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json)及实际 Web 标签。适用目标按每台 PLC 的 `plcId`、`instanceId`、`sourceGeneration` 准入；`sourceType` 为展示标签，DB 为样本内容和查询条件。区分开发 POST/GET 免 Bearer 与管理员来源管理，区分逐点最新值、完整历史与可靠提交回执；保留实际目标采用边界。两语首部互链；中文仅补语言切换和原第 7 节锚点别名 `7-从采集到上报核对一份样本`，供旧引用导航。英文现行入口直达英文版。

## 2. 历史引用

下表是起草时已核对的引用范围。Development 在本任务 `tasks.md` 中按原记录、原锚点和候选列一张可点击的追溯表，指向已验证的固定 Git 版本、快照或恢复说明。表下保留四份删除前短页的原文与 SHA-256，供复核 DAA-014 已验收的短页和撤回时取用。

| 原记录 | 旧引用与可用定位 |
| --- | --- |
| DAA-007 | 冻结 r1 规格有两条按原目录解释的阶段 B 试行稿链接；原路径和摘要保留。阶段 B 可定位版本由 [DAA-014 §3](../DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)的固定 Git 对象及 SHA-256 确认；早期试行稿只在摘要匹配后标为精确原文。 |
| DAA-008、DAA-011 | 共 20 条直链，包括 M01、`#L5`、`#L82`、`#L86`。沿用 [DAA-014 §3](../DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)中的 Git 版本及原文恢复方法，保留 QA1 与 QA2 的版本区别。 |
| DAA-010 | checklist 有 3 条直链，含 `#L40`、`#L97` 和中文第 6 节。原 r5 暂停候选的两份原文用 [DAA-014 §3 与 §6](../DAA-014-unified-operator-guide/tasks.md#6-qa1-返工与英文历史原文)的 QA5 快照和各自差异重建，核对 [r5 原摘要](../DAA-010-sample-facts-upload/tasks.md#L246)。后续复验沿原任务交接识别其精确候选，若其余清单版本未核实则标明缺口。现行操作指向统一手册，旧 r5 allowlist 和 r6 待批附录仍由原任务管理。 |
| DAA-013、ARCH-ACQ-004 | 分别 3、12 条直链，含英文 `#L102`、双语第 6 节和全文链接。QA4 英文及 QA5 双语用 [DAA-014 §3](../DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)的精确版本定位。 |
| 尚无已核对全文的过渡版本 | ARCH-ACQ-004 r4 首轮 QA 的双语候选、其 r2 QA6/QA7 文档交接中的其它候选及 DAA-013 更早交接，按各自 [ARCH-ACQ-004 核验](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md)与 [DAA-013 交接](../DAA-013-multi-plc-reporting-identity/tasks.md)的观察和摘要定位；只在原 SHA-256 匹配后列为可恢复。 |
| 冻结证据 | DAA-014 四份历史快照中的语言互链按快照原目录解释。所有旧任务的规格、交接、核验、验收、摘要和冻结证据保持原字节，历史引用保留原含义。 |

## 3. 写入范围

| 操作 | 精确范围 |
| --- | --- |
| 删除 | DAA 根目录的 `STAGE_C_GUIDE.md`、`STAGE_C_GUIDE.zh-CN.md`、`JOINT_TEST_GUIDE.md`、`JOINT_TEST_GUIDE.zh-CN.md`。 |
| 新增 | DAA 根目录的 `WINDOWS_NATIVE_VALIDATION.zh-CN.md`、仓库 `docs/acquisition-data-guide.md`。 |
| 链接及索引 | `docs/acquisition-data-guide.zh-CN.md` 仅语言切换及历史锚点别名；`docs/README.md` 与 `docs/README.zh-CN.md` 仅指南索引项；DAA 的 `README.md` 与 `README.zh-CN.md` 仅新增 Windows 记录单链接及英文 README 更新通用指南链接；DAA 的 `USER_GUIDE.md` 与根 `PLAN.md` 仅把原通用指南链接换成英文地址。保全 DAA-015 等并行段落。 |
| 任务记录 | 本任务三文件；由协调者按真实状态同步 DAA 的 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` 中 DAA-016 的行，文档退役后可从这些索引进入追溯表。 |

范围限 Markdown。现有配置、profile、31 条样本及其它历史数据均予保全。软件和合同变更、Windows 实机运行、新增测试套件、服务启停、HTTP 操作、数据库、设备、风险豁免、部署及发布分别按所属任务处理。回退只恢复本任务删除前的四份短页并撤销本任务文档增量，保留并行修改。

## 4. 验收与交接

| 编号 | 通过标准 |
| --- | --- |
| AC01 | 四个短路径不存在，现行导航和新增链接可达。以 38 条旧历史直链为明确例外，冻结快照按原位置语义解释。独立核对追溯表、原字节及版本摘要；列明缺少已核对全文的版本及其记录位置。DAA-010 r5 的历史样本指南恢复须区分中英原文、原行号与后续现行文档，重建结果与原暂停清单一致。 |
| AC02 | Windows 记录单可以按步骤准备、操作、核对并记录通过、失败、阻塞或未测；记录仍为待验证。两次 Mac/dev 手测按 DAA-014 原记录引用；[DAA-010 r5 的独立 `qa_failed`](../DAA-010-sample-facts-upload/checklist.md#独立验证-qa2)、首次目录替换问题、Windows AC08 及阶段 C 保留各自状态。 |
| AC03 | 两语八节、图、表、关键示例和界面入口对照一致，技术细节与当前合同相符；中英互链、当前索引、Windows 入口及中文第 7 节旧锚点可达。 |
| AC04 | Development 记录定向文档差异及历史链接检查、两语和合同对照、代码块静态检查。fresh-context Verification 对精确交接独立复核差异和上述标准；文档验收仅需静态核验。 |

2026-11-14（Asia/Shanghai），Human Owner 明确批准 DAA-016 r1。批准前草案 SHA-256 为 `e1cc7e413ea304555cb968cbc0a4017476afc859f5133eb5602649bd3ea459cd`。

> 批准 DAA-016 r1，删除旧文件，接受旧历史链接失效，按规格补充 Windows 验证文档和采集指南英文版。不要过度设计。

交 Development 按本规格实施与自检，使用 `project-governance`、`aiis`，Windows 操作说明按 `desktop-tauri` 和 `rust-runtime` 核对，英文术语和 provider 说明按 `i18n-workflow` 和 `backend-arch` 对照。Development 交接精确差异、自检和追溯依据后，由新的 fresh-context Verification 独立核验，再交 Human Owner 最终文档验收。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
