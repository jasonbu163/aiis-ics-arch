Task ID: DAA-018
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 DAA-018 r4、ARCH-PLC-001 r8 及收尾衔接 -> Development 文档交接 -> fresh-context Verification 独立文档核对 -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 点位中英文显示名与事实隔离的有界证据收尾
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立履行 STD；本 r4 和相关设计分别精确范围批准后，Development、fresh-context Verification 和 Human Owner 最终验收各自记录。
Related Task: aiis-ics-arch::ARCH-PLC-001 r8; device-simulator::DS-004; aiis-ics-arch::DAA-017 r5; aiis-ics-arch::DAA-019; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: Human Owner 已在同一决定中分别精确批准 DAA-018 r4、ARCH-PLC-001 r8 及二者收尾衔接；各任务不继承彼此的 QA 或最终验收。

# DAA-018 r4：双语显示名及上报证据的有界收尾（范围已批准）

## 1. 目标与范围

Human Owner 要求按 STD 利用已完成的人工操作、真实上报与历史记录收尾，不再重复测试，保留历史和现有数据。本 r4 仅整理现有 DAA 本机双语显示、特定真实 v2 样本上报和原 r3 证据、缺口及风险，供独立文档复核和 Human Owner 决定是否接受**明确列出的有限范围及遗留风险**。本 r4 不是新一轮产品开发，也不是对原 r3 各项产品验收整体通过的声明。

r3 的双语配置、原子预览、样本和上报保护合同仍为设计背景；本次以 §4 的文档收尾标准替代将 r3 全部未完成实测作为本轮必做条件，未证明之处必须保留为未证明，不以修订把它们追认为通过。精确批准 r4 的收尾范围不同于接受风险或最终验收；本任务历史 QA 和其他任务的结论均不随本 r4 改变。

[ARCH-PLC-001 r8](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 是对应的父设计收尾草案，本 r4 形成时该草案 SHA-256 为 `a0fdfabbaeebdd95f8bc39fd9f2a0c3b974c13ec5a6b15fe39b6b834aba0eac3`。Human Owner 已在同一决定中分别精确批准该父设计 r8、本任务 r4 及版本衔接，见 §6；父任务的批准不是从本任务自动继承。父设计、DS、DAA-019 和本任务分别记录批准、交接、独立 QA 与最终验收。

## 2. 现有证据及其来源

1. **Human Owner 人工报告。** Human Owner 报告在 DAA `.local/dev` 完成中英文切换和 `display_name` 显示，反馈成功。该项按用户本人对本次本机操作的报告使用；本 PM 没有亲历，既不是新的 Development 实测，也不是新的独立 QA。此报告不补造未报告的编辑、取消、保存/重开、列宽或其他交互结果。
2. **协调者的本机只读核对。** 协调者报告，经用户授权只读对照同一配置的 DAA 与后端 v2 样本 `seq 91–103` 共 13 条：每条在本机均有可靠匹配的 `status=committed` 回执，`outcome` 为 `created` 或 `duplicate`，正文与回执 SHA 校验有效；MySQL `plc_facts_history` 的 13 条来源身份、请求 SHA 及所核点名/类型/值/质量与对应样本一致。`plc_facts_latest` 的 3 点质量为 `good`，最新 seq 为 103；对应来源绑定匹配。该配置至少一个点的中英显示名均非空；13 份实际上传正文均未见显示名字段或对应中英文显示名文本；后端保存的点集未见 display 类字段，所核点字段和值一致，但未对其任意字段的字符串做通用搜索。同一时段 DS 日志无 `WARN` / `ERROR`。这些是**协调者报告的该次本机、同一配置、特定样本与时段**的观察；本 PM 未亲自检查应用、日志或数据库，不能扩大为所有旧版本、v2 分支、异常或时间范围均已验证。
3. **历史独立证据。** [r3 checklist](checklist.md) 记载 QA1 为 `qa_failed`，F-QA1-001 曾复现普通保存绕过双语预览；QA2 对返工在其所覆盖的独立负例中不再复现，整体仍为 `qa_blocked`。原 QA1 / QA2 保留，不能称本任务原 r3 已通过。QA2 原记载的 fake `Capture` transport 对旧 `NeverSent` 样本转 v2、新样本及冻结重试的覆盖，是当时独立合成证据，不是本次 13 条真实上报的观察，也不证明后续组合候选或全部异常。相关 [Development 记录](tasks.md) 和 QA 记载分别保留其执行者、候选、环境、命令、结果和限制。
4. **旧 v1 本地构造与外发边界。** 原 r3 允许的 test-only 旧 v1 冻结正文保留完整 `contextUtf8`，因此可含双语显示名；这是本地合成构造，不是已发生外发或旧 v1 零泄露证明。生产账本的本地重构/完整性校验不能整体称为 test-only。不得启用旧 v1 外发或裁剪、重算旧 context / 正文 / SHA 来抹去事实；若将来拟启用旧 v1 发送须另经设计及批准。

该协调者观察可追溯本机会话 `~/.codex/sessions/2026/11/16/rollout-2026-11-16T09-24-47-01a1e1f4-eb7e-74d2-b055-3696e1a855ec.jsonl`：约第 28239–28242 行为样本、回执和 MySQL 对照，约第 28257–28260 行为双语排除核对，行号可能变化，应按内容定位。该会话可能包含私人信息；仅保留脱敏来源定位和必要结论，禁止将原始业务正文、点值、地址、身份或凭据复制入仓。后续可依据现存会话脱敏核对并持久记录其来源；若记录不可访问，不得声称已独立复核该原文或补造证据。

## 3. 未验证项、风险和资源

- 原 r3 DA18-04：旧的**普通 native** 程序面对含 `pointDisplayNames` 的新配置是否安全拒绝、无误采且不误建空库仍未验证。先前旧 `local-validation` 测试入口的拒绝不能替代普通 native；QA2 只证明所测读取调用零写，已有启动/关闭事件和日志写入不能说成整个进程或 profile 零写。
- 原 r3 DA18-01/02/07–09：最终候选原生编辑、取消及相关影响、顶栏语言完整行为、表格列宽拖动、跨重启保持、恢复默认和原有功能回归未完成独立原生验证。用户已报告的语言切换只覆盖其实际报告范围；Node/合成测试和旧 incognito 窗口观察不能补成正式原生完整通过。
- 原 r3 的真实隔离事件及其影响仍未知：候选退出后的 CUA 可能重新启动或绑定默认真实 profile，路径、可能的启动/退出及其他写入和受影响数据均未确认。继续保留 [tasks](tasks.md) 和 [checklist](checklist.md) 原始事件、QA1 `qa_failed`、QA2 `qa_blocked` 和各次探针，不得称该事件零写或自行恢复、扫描、复制、清理及回滚疑似真实资料。
- 此次 13 条真实 v2 上报不能倒证旧普通程序兼容、所有 v2 外发分支、旧样本与冻结/重试的实际网络行为、未知回执、其他异常、Windows/VM、真实 PLC、长稳或生产/现场采用。各历史合成检查仅覆盖原记录所述条件。
- 用户已明确要求删除的旧任务临时工件已清理；原始临时文件无法再复核。历史文档摘要仍是当时的记录，不把已删除工件写成可取得或重新生成；不得为本轮找回、复制或重新生成它们。

## 4. r4 文档收尾验收标准

| 编号 | 可独立核对的文档标准 |
| --- | --- |
| D18C-01 | 列明精确 Task ID / Revision、r1–r3 已批准事实、r3 QA1 `qa_failed` 和 QA2 `qa_blocked`；保留 F-QA1-001 的原失败与 QA2 受限复验、事故和全部历史，不将其改写成全项通过或 Owner 已接受。 |
| D18C-02 | 区分 Human Owner 在 `.local/dev` 的语言切换 / `display_name` 自报、Development 自检、既有独立 QA 和协调者本机只读核对；不将任何转述冒充当前角色亲见或完整产品 QA。 |
| D18C-03 | 如实记录 §2 的 13 条 seq、逐条可靠回执和 SHA、MySQL history 对照、latest 3 点、双语非空与上报正文/后端点集的观察及同一时段 DS 日志边界；记录样本、配置、时间及观察者的限制，脱敏定位可追溯的现存记录。 |
| D18C-04 | 分开历史 fake transport 对旧未发送样本、新样本和冻结重试的独立证据与本次真实 v2 样本；保留 test-only 旧 v1 本地正文可能含双语及不得启用其外发的边界，不声称所有外发分支或历史数据均已证明。 |
| D18C-05 | 明确列出旧普通 native 安全拒绝 / 无误采 / 无空库、最终原生编辑、列宽跨重启 / 复位等尚未独立完成的项及隔离事件未知影响；注明旧临时工件已清理、不可从原件复核，不以真实样本或人工切换补齐缺口。 |
| D18C-06 | 根据现存任务记录及可取得的经授权会话记录完成脱敏文档交接，记录实际已核对和未核对的证据、缺失或不可访问资料及精确限制；不重跑产品测试或构建，不访问应用、GUI、IPC、profile、数据库、PLC，不发送上报、不要求用户重新操作。 |
| D18C-07 | fresh-context Verification 独立核对本 r4、Development 交接、现存角色记录及允许的文档 diff；证据不一致或无法满足本 r4 标准时如实给出 `qa_failed` / `qa_blocked`。若文档 `qa_passed`，只表示本次收尾记录通过，不代表 r3 所有 DA18-01–10、旧 native、全部产品功能或生产通过。 |
| D18C-08 | 准确记录 ARCH-PLC-001 r8、DAA-018 r4 与版本衔接各自真实的 Human Owner 范围批准状态；不将范围批准、历史独立 QA 或文档复核直接记为风险接受及 Human Owner 最终验收。 |

## 5. 写入范围、执行与 handoff

本 PM 只修订本 `spec.md`。Human Owner 已对 `aiis-ics-arch::DAA-018 r4`、`aiis-ics-arch::ARCH-PLC-001 r8` 及版本衔接作出精确范围批准（见 §6）；Development 可更新本任务既有 [tasks.md](tasks.md)，根据既有记录整理证据来源、脱敏定位、实际未运行项、风险及文档自检并形成 `developer_handoff`；之后由 fresh-context Verification 独立核对，并仅更新本任务既有 [checklist.md](checklist.md) 的 r4 文档核对和 verdict。保留原 r3 角色文件的全部历史事实、原时点 Revision / 状态和旧批准、失败、阻塞、事故及证据；如更新顶层元数据，应先记录原文件 SHA 与原元数据，不覆盖或伪造历史结论。

Development 和 Verification 的本轮写入仅限各自上述角色文件；PM / Human Owner 的范围与批准记录归本 spec。协调者可在其权限和适用批准下进行必要的索引机械同步。任何代码、测试、构建、手册、运行配置、用户数据、历史或其他任务均不属于本 r4 角色写入范围；本轮不启动应用、访问数据库或发送新请求。已有脏工作树和并行变更按所属任务保留，不因收尾撤销或归因。

本 r4 仅需 `aiis` 与 `project-governance` 处理项目方法、证据收尾与角色边界；后续文档角色按实际触达面加载适用 shared skill。若重新打开产品实现、原生验证、设备或上报工作，须由 PM 形成新的精确范围并路由 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 等适用专项角色与 skill，经 Human Owner 另行批准；此处不授权技术执行。角色为 contract_only，不代表平台 ACL 或强制路由。

## 6. Human Owner 精确范围批准

Human Owner 在协调者列明整组精确草案及版本衔接后明确回复：

> 批准这组收尾草案

该决定在同一次明确批准 `aiis-ics-arch::DAA-018 r4`、`aiis-ics-arch::ARCH-PLC-001 r8`、`device-simulator::DS-004 r3`、`device-simulator::DS-005 r3`、`aiis-ics-arch::DAA-019 r3` 及其版本衔接；每项的批准分别生效，不由父任务或子任务互相继承。Human Owner 审阅的本 r4 草案 SHA-256 为 `92eb1b76a83e5b84bca267d5511b291f60f98481292504b4096bc3fbd21a15dd`。§1 所载父 r8 的草案 SHA 是本 r4 形成时的历史事实；父任务的批准详情归其自身 spec。

本决定批准的是本 r4 既定的文档收尾范围，并非风险接受、独立 QA 通过或最终验收。原 r3 QA1 `qa_failed`、QA2 `qa_blocked`、未验证项和隔离事件未知影响保持；当前没有 r4 Development handoff、r4 QA verdict 或 Human Owner 最终验收。Development 可按 §5 进行文档交接，之后由 fresh-context Verification 独立审阅，Human Owner 再单独决定最终验收。

## 附录：已批准 DAA-018 r3 完整原文及全部历史

以下围栏首行之后至闭合围栏之前为写前 r3 的完整原始 UTF-8 字节，含原末尾换行及嵌套的 r2、r1 原文；写前 SHA-256 为 `bd27de086ade327ccabe33b1ee3669bffb8b3be8f54698b27ff3160ff7749895`。其中历史时态、批准、allowlist 与命令仅记录各自时点，不构成本 r4 的批准或执行范围。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DAA-018
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: DAA-018 r3 实施范围和 ARCH-PLC-001 r4 设计范围及版本衔接已获 Human Owner 精确批准 -> Development 保留 r1/r2 事实并继续 -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 点位中英文显示名，保持采样与现有上报合同
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立履行 STD，不继承其他任务的实施批准、QA 或最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r4; device-simulator::DS-004 r1; aiis-ics-arch::DAA-017 r2; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: aiis-ics-arch::ARCH-PLC-001 r4 精确设计批准；DS-003 / DAA-017 在本任务及 DS-004 均完成 STD 最终验收后才启动实施；此前下游开工时序已由 2026-11-17 的 Owner 后续决定调整，见下方顺序衔接说明。

# DAA-018：点位中英文显示名与事实隔离

## 1. 状态与边界

Human Owner 于 2026-11-17（Asia/Shanghai）要求先统一 DS、DAA 点位中英文显示名，再做导出导入；显示名跟随顶栏语言，未设置留空，DAA 上报不带显示名，当时要求暂不改代码。[ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获 Human Owner 批准；父设计 r4 的对应验收修订已获 Human Owner 精确批准；本任务 r1 实施范围曾获 Human Owner 批准；Development 在改代码前发现原批准文件范围无法覆盖单次原子编辑，已如实记录阻塞。Human Owner 已精确批准 r2 实施范围及版本衔接；r2 开发中发现旧批次上下文与双语验收冲突，Human Owner 已精确批准 r3 实施范围及父设计衔接。r1/r2 批准历史保留，最终验收仍待独立验证后决定。本任务 owner 为 DAA，独立走 STD；与 DS-004 分别完成独立 QA 和 Human Owner 最终验收后，才能启动各自另批的 DS-003 / DAA-017 实施。

只增加 DAA 本地点位双语显示名的编辑、配置存储及既有采样/上报兼容；既有 `Point.name` 仍为稳定程序名，原 `Point.comment` 仍是独立注释。禁止从程序名、路径、comment 或另一语言猜测/复制/翻译；不修改 JSON 导入导出、DS/FF/CA、后端、公开合同、SQLite 物理 schema、已有 profile/现场设备。DAA-017 后续负责目录中的 description 与 comment 的明确预览及映射，本任务不把 comment 冒充显示名。


### 后续 Owner 决定：JSON 任务顺序衔接

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

该决定精确批准 ARCH-PLC-001 r5 设计、DS-003 r4 与 DAA-017 r4 实施及顺序调整。本文此前记录的“两个双语基础均最终验收后才审批、启动 JSON 实施”是当时有效的下游门槛；自本次决定起，DS-003 r4 和 DAA-017 r4 可依各自已批准规格开展 Development，不再等待两个双语基础最终验收。原门槛文字保留用于历史追溯。本任务自身实施范围、文件白名单、验收和风险不变，原失败历史保留，当前独立 QA 仍为 qa_blocked，Human Owner 最终验收未发生；任何 JSON QA 均不能冒充本任务通过。互通测试仅在各自已授权 .local/dev 范围进行，不能影响既有数据或真实设备。

## 2. 配置和用户体验

1. 当前 [DAA Point](../../src-tauri/src/domain/local_configuration.rs) 没有语言化显示名；`name` 和 `comment` 不能借来冒充它。拟在现有 schema_version 1 配置顶层增加可省略映射 `pointDisplayNames`，键为**本地点 UUID**，值是严格对象 `{"zh-CN":"...","en-US":"..."}`；每键恰为字符串、各 ≤256 UTF-8 字节，缺一个键、null、非字符串或额外键拒绝。配置缺整个映射/该点项视为两语言均 `""`，显式保存时两值都空可省略该项及空映射；任一非空保存两个键。合法 Unicode 字符及首尾空格原样保留，不隐式翻译或清洗。整个映射和单项为 null 均非法；读取时若兼容允许空映射或两键均空，不能触发自动写回。
2. 点位列表保留技术 `name`，另列出顶栏当前语言对应值；该语言空时为空白或明确未设置占位，不回退任何其他字段。点位编辑同时展示中英文输入和原有独立 comment；编辑、清空任何一侧不得修改另一侧、name、comment、地址、ID、组或启用。切换顶栏语言仅改变显示，不写配置、ETag、激活版本或样本；取消和未确认编辑不写。所有界面提示中英文齐全，原有点表按公共列宽能力处理。
3. 键必须为当前配置中唯一存在的本地点 UUID，不能指向其他 PLC 的不存在点、已删除点或无效 ID；一个点只对应一项。现有同 ID 的 DB/UDT 复导、改名、地址及分组修改保留两语言。显式删除点/DB/PLC 时，在相应草稿/来源变更事务中仅移除其映射，其他点、旧 revision 和样本不变；点 ID 被替换或重绑时不得悄悄把旧点名称附到新身份，必须通过原流程明确预览和用户确认。保存和导入不能绕开 `protect_derived` 或原有点/来源校验。
4. 保存沿用草稿 CAS 和显式激活流程；UI 语言和未完成编辑不触发保存。配置容量含新增元数据：超限返回明确错误，原草稿、source 和版本不动，不截断文字或丢映射。实际用户现有 profile 的读写、复制和迁移均未授权。

### 2.1 r2：单点命名预览与双语编辑的同一事务

实际路径是点位页 `applyLocalPoint` → `stagePointEdit` / `confirmNames` → `daa_preview_point_names` / `daa_confirm_point_names` → `local_point_naming.rs::candidate` → `save_candidate`。`PointPatch` / `NameRequest` 当前 `deny_unknown_fields` 且没有双语字段；普通 `daa_save_draft` 受 `protect_derived` 保护，不能绕过技术名预览。若先保存技术名再单独保存双语字段，并发或失败可能只提交其中一部分。本 r2 仅将原有单点命名预览扩展至同一双语修改，不新增第二种保存入口。

- 单点 `edit` 的 `PointPatch` 可选 `displayNames` 闭合对象含 `zh-CN` 与 `en-US` 两字符串，长度及空值规则沿用 §2。**字段缺失表示不修改**原双语值，确保旧客户端请求兼容；对象存在时两个值为本次明确输入，`""` 表示清空对应语言，两者均空时按 §2 省略该项。显式 null、缺一个语言键、非字符串、未知键及超长值拒绝；不能把 null 当缺省或从技术名/comment/另一语言推测。既有 `generate` 的选择和禁止 patch 规则保持。
- 服务端只对原请求选中的同 PLC 单点，在克隆的 `Configuration.pointDisplayNames` 中应用值，与技术名、comment、地址及组等原 patch 构造**同一个候选**；Point/PointFact 结构、样本及外发字段仍不增加显示名。原身份、来源、命名、地址、组、容量及 `protect_derived` 规则不得弱化；既有服务端命名预览可使用其受控候选提交路径，不开放绕过预览的普通保存或使用 ETag/无关字段暗传显示名。
- 可选字段须纳入服务端原 `inputDigest`、单次 token、当前 ETag、300 秒有效期和缓存候选比较；确认时重算请求摘要、核对 token/有效期及 ETag，重新生成含双语的候选并比较，仅通过后调用一次原有 `save_candidate` CAS。字段缺失的旧请求保持其原序列化/摘要和行为；任一双语字段输入、选择、草稿或 ETag 变化使旧预览失效，伪造/篡改/过期 token、跨 PLC 点和不可确认候选均拒绝，不得拆两次 CAS 或先提交技术名。
- 点编辑器打开后的预览、语言切换、取消及已知提交前失败均不写本次点编辑；已知容量/校验/CAS 失败保持原草稿与名字。既有“保存草稿并编辑”可在打开编辑器前由用户明确保存先前未保存的其他草稿，本 r2 不改变该先行行为，也不把这次先行保存冒称编辑取消零写。若提交回执未知，沿现有未知结果处理先重读草稿/ETag 后再决定，不能谎称一定零写或盲目重试。

## 3. 样本、上报和版本安全

目前 [local_scheduler](../../src-tauri/src/services/local_scheduler.rs) 以 `point.clone()` 形成 `PointFact.definition`，而 [facts_wire](../../src-tauri/src/domain/facts_wire.rs) 的 `definition_check` 对 Point 定义严格闭合。因此本设计**不向 Point 或 PointFact 添加显示名字段**，配置级映射通过本地点 ID 关联；不得放宽严格字段验证，也不得把显示名混进 `name`、`comment`、value、quality 或任意输出字段。

配置 revision 的完整 context 可以包含 `pointDisplayNames`；当前所有**产品实际可达的外发正文**不得包含新增的中英文显示名或把它们混入 name/value/comment 等字段。v2 Point 使用原有程序 `name`，其正文原本没有 `comment`，不能为了测试新增；本地 PointFact.definition 的 comment 独立保持。已保存并激活新配置可产生新的 configRevision、时间、样本 ID、上下文 SHA 和原有摘要字段，不能要求新旧样本全文相同。

### 3.1 r3：历史 v1 兼容与实际外发区分

Development 用自有合成测试复现 `commit_cycle → build_delivery_cycle → freeze_cycle`：历史 v1 `Cycle.contextUtf8` 包含完整配置原文，新配置若有双语值，测试构造的 v1 本地冻结正文会包含两种 sentinel。该测试没有证明发生真实外发。只读源码表明：`local_store/delivery.rs` 的 `build_delivery_cycle`、`freeze_cycle`、`next_delivery_ready`，`local_store/mod.rs` 的旧发送选取以及 `facts_http.rs` 的旧 `Transport::post` 均由 `#[cfg(test)]` 控制；普通 `local_delivery.rs` 只在 runtime4 经 `next_sample_upload_ready` / `post_sample` 发送 plc-facts/v2，runtime3 的 start/resume 被拒。产品源码中 `facts_wire::build_cycle` 和 `schema.rs` 仍可用于既有旧账本的**本地重构/完整性校验**，不能将它们整体称为 test-only 或删除。

**Human Owner 已批准的最小方案**：保留历史 v1 完整上下文与原合同，明确 DA18-06 的“不含显示名”针对产品实际可达的外发；对 test-only 旧构造链，保留合成正例并如实验证其完整 context 与原摘要，承认本地构造正文可能含显示名，不把它冒充已对外发送或记录成旧 v1 零泄露通过。不得启用或暴露旧批次网络发送；将来若要启用任何旧 v1 发送，须另立设计并先解决显示名外发、来源摘要、原始上下文完整性及历史兼容，取得独立批准。

产品 v2 必须验证全部可达发送分支：既包括本次新采样，也包括依据既有 `legacy_status` 被确认从未发送的旧样本按原规则构造的新 v2 正文、既有 v2 冻结与重试；对各自可执行场景以互不相同且不在程序名/注释/值中的中文、英文 sentinel 捕获模拟 transport 正文，保证新增显示名及其内容不出现在任何外发字段，程序名/值及原合同字段的存在/缺失语义不变。不符合旧样本重发准入的状态仍按原有复核/阻断行为处理；不得重发既有 v1 冻结正文或改动其状态来绕过。

保留本地旧冻结/排队正文、完整 `contextUtf8`、上下文和请求哈希、历史 revision、样本与回执的原 bytes/SHA；继续保留生产账本重构、完整性校验和本地只读查询。禁止删除双语字段、裁剪上下文后重算旧摘要、伪造原始配置或修改旧公开合同来使测试通过。只读 IPC 或本地合成冻结与外发分开记录，不声称用户现有历史正文从未包含同字串，也不扫描或改写真实 profile。

**父设计 gate：** [ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) §7.1.1 原文字面要求检查历史批次/冻结且确认显示名不出现；本 r3 是对该验收边界的实质修订；父设计 ARCH-PLC-001 r4 与本 r3 的验收及 DAA 活动版本衔接已获 Human Owner 精确批准。Development 可按 r3 继续，但不把 r2 未满足验收标为通过；DS-004 独立任务不因本提案改动。

配置 v1 与两库物理 schema 不变，仅新增可省略配置字段。旧数据读取不能重写原 payload/SHA；`deny_unknown_fields` 意味旧二进制可能拒绝带新字段的配置，必须在停机隔离副本验证安全拒绝且不误创建空库、不执行错误采集。新旧程序、容量和上下文验证没有真实结果前均是待证设计；若需要放宽 PointFact 键集、改变旧上报契约、DDL/已用 profile 迁移或复制真实数据，停止并回 PM 另行批准。

## 4. r3 已批准的 Development 文件 allowlist

以 `automation-world/data-acquisition-agent/` 为根；花括号只展开列出的名字。r2 相比 r1 仅增加下表中的 `src-tauri/src/domain/point_naming.rs` 与 `src-tauri/src/services/local_point_naming.rs`，供单点命名预览原子整合；本 r3 已获 Human Owner 精确批准；文件 allowlist 与 r2 相同。发现额外文件需要写入先回 PM。PM 阶段只写本 spec，后续角色按各自 gate 行事。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 配置、来源复导 | `src-tauri/src/domain/{local_configuration.rs,source_import.rs,point_naming.rs}`；`src-tauri/src/services/{local_configuration.rs,local_point_naming.rs}`；`src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}` | `src-tauri/src/infrastructure/local_store/point_display_names_tests.rs` |
| 用户界面与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | 无 |
| 样本和上报测试 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`；`src-tauri/src/services/local_delivery_tests.rs`；`tests/{point-editing.test.mjs,facts-delivery.test.mjs}` | `tests/point-display-names.test.mjs` |
| 文档 | `src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `CODE_INDEX.md`（实际结构变化时依仓库契约） |
| STD 角色记录 | 本 spec 仅 PM/Owner | 批准后 Development 创建 `tasks.md`；handoff 后独立 Verification 创建 `checklist.md` |

不得修改 `Point` 事实结构、`facts_wire::definition_check` 或公共上报合同，亦不改 DDL、`schema.rs`、依赖/锁、`.env`、其他任务或真实 profile。若现有 Point 编辑 UI 分散在其他文件，超出白名单先回 PM。新增列沿用公共表格工具：普通列拖拽、最小宽、横向滚动、稳定键隔离、刷新/切页/重启恢复和恢复默认；功能列可固定，本机偏好不进业务配置。

## 5. 验收标准（均未执行）

| 编号 | 可验证通过标准 |
| --- | --- |
| DA18-01 | 新点双语默认空；中英文独立设置、只填一侧、清空、保存/重开均保持精确 Unicode；缺失映射正确显示空，错误键/null/类型/超 256 UTF-8 字节被拒绝。 |
| DA18-02 | 顶栏切换仅显示当前语言，空值不回退 name/comment/另一语言；切换和取消不改变 ETag、草稿、版本或样本。编辑框的 comment 值与双语均可独立维护。 |
| DA18-03 | 点 ID 一一关联；同身份复导、改名、分组和地址修改保留双语；新增/删除/DB 或 PLC 删除、ID 改变及并发操作无跨点污染、孤儿或历史改写。原来源、树、leaf 和命名校验不变。 |
| DA18-04 | 新程序零写读取含旧版本和样本的自有合成 profile；旧程序面对带 pointDisplayNames 的新配置安全拒绝而不误采、不建空库；两库 schema 与所有旧 payload/SHA 保持，不能以空 profile 冒称兼容。 |
| DA18-05 | 构造不同中文/英文/原 comment 的采样，原样本 PointFact 定义键不变，原校验和 manifest/context 引用通过；旧样本、历史、冻结/排队和 ACK bytes/SHA 不变。新 revision/context 允许不同，不能伪称新旧 bytes 相等。 |
| DA18-06 | 产品实际可达的 v2 发送路径逐一捕获模拟 transport 正文：新采样、既有冻结/重试，以及符合 `legacy_status` 从未发送条件的旧样本新生成 v2；两语言 sentinel 不进入任何外发字段，`name`/value 不变且 v2 本来无 comment，已尝试/待复核等旧状态按原准入处理。产品相关 feature/入口源码及构建核验旧 v1 新建批次、冻结和网络发送为 test-only，runtime3 start/resume 拒绝，不能以 v2 测试冒称旧 v1 可外发的零泄露通过；无真实 POST。 |
| DA18-10 | 在自有合成 profile 的 test-only 旧 v1 构造中验证 contextUtf8 按原合同含完整配置及双语 sentinel，原摘要和冻结正文自洽；明确记录仅本地测试、未外发。生产账本的只读重构校验和历史旧冻结/回执 bytes/SHA 保持，不能裁剪、重算或绕开；若出现产品可达的旧 v1 发送路径则阻断并回 PM。 |
| DA18-07 | 中文英文原生点表、编辑框、语言切换、列宽拖动/恢复和旧功能回归；隔离环境真实记录 Rust/Node/类型检查与构建结果，不外推其他平台或现场。 |
| DA18-08 | 同一单点同时改技术名、中英文和已有允许字段，预览与确认使用一个候选和一次 CAS；结果全成或已知提交前失败全不变，名字不串点/PLC。缺少新字段的旧请求和批量 generate 原行为、命名/来源/地址校验均保持。 |
| DA18-09 | 空串单侧/双侧清空、缺省保留及 null/缺键/未知键/超 256 UTF-8 字节负例；伪造或篡改任一双语值/摘要/token、过期、过期 ETag、并发编辑、取消与已知提交前失败均拒绝且不写本次编辑；结果未知先重读。测试覆盖编辑器打开前已有“保存草稿并编辑”的先行保存边界，防止错误计为取消后的写入。 |

## 6. 执行、回退及 handoff

本 r3 和父 ARCH-PLC-001 r4 验收/版本衔接经 Human Owner 精确批准后 Development 才可继续并更新既有 `tasks.md`（保留 r1/r2 阻塞和批准历史），使用自有新合成 profile、停机的合成旧版本副本及隔离构建目录完成自检并交付正式源码；fresh-context Verification 独立创建 checklist，Human Owner 最终验收另行决定。示例检查：`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names -- --test-threads=1`、`node --test tests/point-display-names.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`；`CARGO_TARGET_DIR`/`RUN_DIR` 指向隔离临时目录。按实际路径记录命令、退出码、系统、候选和未执行项；不使用真实数据库、设备、网络或用户联调 profile。

若旧二进制不能安全拒绝含新元数据的配置、产品实际 v2 外发包含显示名、发现产品可达旧 v1 发送入口、严格事实链/容量/旧账本校验不兼容，停止并回 PM；不得以清除字段、恢复旧网络发送或改写历史绕过。回退只用经验证的停机合成副本/原备份；真实 profile 备份、恢复、迁移另行授权。DS-003 / DAA-017 均依赖本任务及 DS-004 完成包括 Human Owner 最终验收的 STD，另行审批后才实施。

PM 使用 `aiis`、`project-governance`、`plc-point-mapping`；后续 Development 按触达使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，Verification 以 fresh context 独立复核。自检/QA 均不自动批准生产或现场行为。

## 7. r1 Human Owner 实施范围批准记录（历史）

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 DS-004 r1 和 DAA-018 r1 的实施范围。请按 STD 先完成两端双语显示名的开发和独立验证，导出、导入功能暂不实施。

此决定批准本任务 `DAA-018 r1` 的精确实施范围，批准前完整草案 SHA256 为 `2adc3ae0f61ee6b37bf1ba111d6f26e2f7e844f64a1512b5b5c4e68319cbbd79`；允许按本规格开展 Development 自检及 fresh-context Verification。该批准不代表 Human Owner 最终验收，不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布；两项基础任务各自完成 STD 最终验收后，导出/导入仍须独立精确批准。

## 8. r2 修订与批准记录（历史）

**本节保留 r2 当时的批准及状态，不代表 r3 已批准。**

2026-11-17（Asia/Shanghai）Development 在 r1 批准后、修改代码前记录 `dev_blocked`：原文件 allowlist 未包含命名预览 DTO 与服务，无法让单点双语修改和技术名共用受控候选与单次 CAS。本 r2 仅增加 §4 两个现有文件及 §2.1、DA18-08/09 所述与之直接对应的合同、验收与失败风险；保留 r1 的其余需求、验收、文件范围、上报/历史/设备边界。Human Owner 已精确批准 r2 实施范围及版本衔接；Development 可按 r2 继续，仍需 fresh-context 独立验证和 Human Owner 最终验收，DS-004 独立推进不受此阻塞。


### r2 实施范围批准及版本衔接

2026-11-17（Asia/Shanghai），Human Owner 在交互问题中明确回复：

> 批准 DAA-018 r2 及版本衔接

该决定批准本任务 `aiis-ics-arch::DAA-018 r2` 的精确实施范围，并确认 r2 作为父设计中 DAA 双语基础的活动实施版本；用户审阅的 r2 草案 SHA256 为 `58c4aade878dbed5bbb19f0c4b13cf96fcb29d1e339f3df796b5027b659aa52b`。r1 的批准和开发阻塞历史保持；r2 仍需 Development、fresh-context Verification 和 Human Owner 最终验收。只有 DAA-018 r2 与 DS-004 各自完成最终验收后，才能进入分别另行批准的导出/导入实施；本批准不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布。


## 9. r3 已批准决策与保留范围

本草案提出按实际外发可达性解释“不上报显示名”，同时承认 test-only 旧 v1 构造正文中的完整上下文可包含显示名。它是对 r2 DA18-06 及父设计 §7.1.1 的**明确验收调整**；Human Owner 已精确批准 DAA-018 r3 实施范围、ARCH-PLC-001 r4 设计范围及活动版本衔接，但这不是 QA 结论或最终验收。若未来要求 test-only v1 构造正文也不含显示名，现行完整 context、摘要和配置版本约束下不能以静默脱敏达成，应停止并另拟经批准的存储/合同兼容设计；本提案不声称所有技术方案均已穷尽。

除 DA18-06 已批准的修订与新增 DA18-10 外，沿用 r2 的原子命名预览、DA18-01–05/07–09、文件 allowlist、双语 UI、旧配置和样本保护；不改 DS、公开合同、数据库 DDL、真实 profile 或设备，不新增导出/导入或其他上报功能。r2 代码候选已有改动和开发进度由 Development 的 tasks 真实记录，PM 不回退；r3 和父设计 r4 已获范围批准及衔接，Development 可按 r3 继续；既有候选不等于通过。

### r3 实施范围与父设计衔接批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确回复：

> 批准两份规格及版本衔接

该决定精确批准 `aiis-ics-arch::DAA-018 r3` 的实施范围、`aiis-ics-arch::ARCH-PLC-001 r4` 的设计范围及两者版本衔接。用户审阅的 DAA-018 r3 草案 SHA256 为 `7f8761c47d04eb5a6162c58aaeb07d920fd68d2cda99cc654be73febede3005a`，ARCH r4 草案 SHA256 为 `e5b5cfa9cbfc0556aea79089c81af0d012f6213b75dc87e03af0669cd8ef6d90`。Development 可按 r3 继续，须保留 r1/r2 事实，随后 fresh-context Verification 和 Human Owner 最终验收仍为独立 gate；不授权 JSON 导出/导入、真实 profile、DDL、现场设备或发布。

## 附录 A：已批准 r2 完整原文（含 r1 历史）

写前完整 r2 SHA256：`9d02dbdc03310c4c758c20a833c1f69778ea312ccfe7d42b0bb582389bd7def6`。下方围栏首行之后至闭合围栏之前是原始 UTF-8 字节，保留原末尾换行、r2 批准和嵌套 r1 原文；历史批准不自动延伸至 r3。

~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DAA-018
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: DAA-018 r2 实施范围及版本衔接已获 Human Owner 精确批准 -> Development 更新既有 tasks.md 并保留 r1 阻塞历史 / developer_handoff -> fresh-context Verification checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 点位中英文显示名，保持采样与现有上报合同
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立履行 STD，不继承其他任务的实施批准、QA 或最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r3; device-simulator::DS-004 r1; aiis-ics-arch::DAA-017 r2; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: aiis-ics-arch::ARCH-PLC-001 r3 精确设计批准；DS-003 / DAA-017 在本任务及 DS-004 均完成 STD 最终验收后才启动实施

# DAA-018：点位中英文显示名与事实隔离

## 1. 状态与边界

Human Owner 于 2026-11-17（Asia/Shanghai）要求先统一 DS、DAA 点位中英文显示名，再做导出导入；显示名跟随顶栏语言，未设置留空，DAA 上报不带显示名，当时要求暂不改代码。[ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获 Human Owner 批准；本任务 r1 实施范围曾获 Human Owner 批准；Development 在改代码前发现原批准文件范围无法覆盖单次原子编辑，已如实记录阻塞。Human Owner 已精确批准 r2 实施范围及版本衔接；r1 批准仅针对 r1，r2 最终验收仍待独立验证后决定。本任务 owner 为 DAA，独立走 STD；与 DS-004 分别完成独立 QA 和 Human Owner 最终验收后，才能启动各自另批的 DS-003 / DAA-017 实施。

只增加 DAA 本地点位双语显示名的编辑、配置存储及既有采样/上报兼容；既有 `Point.name` 仍为稳定程序名，原 `Point.comment` 仍是独立注释。禁止从程序名、路径、comment 或另一语言猜测/复制/翻译；不修改 JSON 导入导出、DS/FF/CA、后端、公开合同、SQLite 物理 schema、已有 profile/现场设备。DAA-017 后续负责目录中的 description 与 comment 的明确预览及映射，本任务不把 comment 冒充显示名。

## 2. 配置和用户体验

1. 当前 [DAA Point](../../src-tauri/src/domain/local_configuration.rs) 没有语言化显示名；`name` 和 `comment` 不能借来冒充它。拟在现有 schema_version 1 配置顶层增加可省略映射 `pointDisplayNames`，键为**本地点 UUID**，值是严格对象 `{"zh-CN":"...","en-US":"..."}`；每键恰为字符串、各 ≤256 UTF-8 字节，缺一个键、null、非字符串或额外键拒绝。配置缺整个映射/该点项视为两语言均 `""`，显式保存时两值都空可省略该项及空映射；任一非空保存两个键。合法 Unicode 字符及首尾空格原样保留，不隐式翻译或清洗。整个映射和单项为 null 均非法；读取时若兼容允许空映射或两键均空，不能触发自动写回。
2. 点位列表保留技术 `name`，另列出顶栏当前语言对应值；该语言空时为空白或明确未设置占位，不回退任何其他字段。点位编辑同时展示中英文输入和原有独立 comment；编辑、清空任何一侧不得修改另一侧、name、comment、地址、ID、组或启用。切换顶栏语言仅改变显示，不写配置、ETag、激活版本或样本；取消和未确认编辑不写。所有界面提示中英文齐全，原有点表按公共列宽能力处理。
3. 键必须为当前配置中唯一存在的本地点 UUID，不能指向其他 PLC 的不存在点、已删除点或无效 ID；一个点只对应一项。现有同 ID 的 DB/UDT 复导、改名、地址及分组修改保留两语言。显式删除点/DB/PLC 时，在相应草稿/来源变更事务中仅移除其映射，其他点、旧 revision 和样本不变；点 ID 被替换或重绑时不得悄悄把旧点名称附到新身份，必须通过原流程明确预览和用户确认。保存和导入不能绕开 `protect_derived` 或原有点/来源校验。
4. 保存沿用草稿 CAS 和显式激活流程；UI 语言和未完成编辑不触发保存。配置容量含新增元数据：超限返回明确错误，原草稿、source 和版本不动，不截断文字或丢映射。实际用户现有 profile 的读写、复制和迁移均未授权。

### 2.1 r2：单点命名预览与双语编辑的同一事务

实际路径是点位页 `applyLocalPoint` → `stagePointEdit` / `confirmNames` → `daa_preview_point_names` / `daa_confirm_point_names` → `local_point_naming.rs::candidate` → `save_candidate`。`PointPatch` / `NameRequest` 当前 `deny_unknown_fields` 且没有双语字段；普通 `daa_save_draft` 受 `protect_derived` 保护，不能绕过技术名预览。若先保存技术名再单独保存双语字段，并发或失败可能只提交其中一部分。本 r2 仅将原有单点命名预览扩展至同一双语修改，不新增第二种保存入口。

- 单点 `edit` 的 `PointPatch` 可选 `displayNames` 闭合对象含 `zh-CN` 与 `en-US` 两字符串，长度及空值规则沿用 §2。**字段缺失表示不修改**原双语值，确保旧客户端请求兼容；对象存在时两个值为本次明确输入，`""` 表示清空对应语言，两者均空时按 §2 省略该项。显式 null、缺一个语言键、非字符串、未知键及超长值拒绝；不能把 null 当缺省或从技术名/comment/另一语言推测。既有 `generate` 的选择和禁止 patch 规则保持。
- 服务端只对原请求选中的同 PLC 单点，在克隆的 `Configuration.pointDisplayNames` 中应用值，与技术名、comment、地址及组等原 patch 构造**同一个候选**；Point/PointFact 结构、样本及外发字段仍不增加显示名。原身份、来源、命名、地址、组、容量及 `protect_derived` 规则不得弱化；既有服务端命名预览可使用其受控候选提交路径，不开放绕过预览的普通保存或使用 ETag/无关字段暗传显示名。
- 可选字段须纳入服务端原 `inputDigest`、单次 token、当前 ETag、300 秒有效期和缓存候选比较；确认时重算请求摘要、核对 token/有效期及 ETag，重新生成含双语的候选并比较，仅通过后调用一次原有 `save_candidate` CAS。字段缺失的旧请求保持其原序列化/摘要和行为；任一双语字段输入、选择、草稿或 ETag 变化使旧预览失效，伪造/篡改/过期 token、跨 PLC 点和不可确认候选均拒绝，不得拆两次 CAS 或先提交技术名。
- 点编辑器打开后的预览、语言切换、取消及已知提交前失败均不写本次点编辑；已知容量/校验/CAS 失败保持原草稿与名字。既有“保存草稿并编辑”可在打开编辑器前由用户明确保存先前未保存的其他草稿，本 r2 不改变该先行行为，也不把这次先行保存冒称编辑取消零写。若提交回执未知，沿现有未知结果处理先重读草稿/ETag 后再决定，不能谎称一定零写或盲目重试。

## 3. 样本、上报和版本安全

目前 [local_scheduler](../../src-tauri/src/services/local_scheduler.rs) 以 `point.clone()` 形成 `PointFact.definition`，而 [facts_wire](../../src-tauri/src/domain/facts_wire.rs) 的 `definition_check` 对 Point 定义严格闭合。因此本设计**不向 Point 或 PointFact 添加显示名字段**，配置级映射通过本地点 ID 关联；不得放宽严格字段验证，也不得把显示名混进 `name`、`comment`、value、quality 或任意输出字段。

配置 revision 的完整 context 可以包含 `pointDisplayNames`，但实际外发正文不能包含显示名：验证当前 `sample_upload` 的 plc-facts/v2 单样本 body、`facts_wire` 的历史分批/冻结正文及可触达的旧采集/快照上报路径；分别核对实际请求 body 与原合同及字段原有的存在/缺失语义：v2 Point 使用原有程序 `name`，其正文原本没有 `comment`，不能为了测试新增；本地 PointFact.definition 的 comment 独立保持，历史 batch 若原本携带 comment 则按原行为保留。其他字段、结构和含义不变。新配置按原流程保存/激活后可正常生成新的 `configRevision`、时间、样本 ID、上下文 SHA 和其既有摘要字段，故不能要求新旧样本/上报全文或字节相等；历史 batch 的 `contextSha256` 是原有摘要字段，不包含名称明文，可随配置上下文变化；仅显示名变化时 Point 定义集摘要应维持原有计算语义，原来源准入/确认规则不被绕过。验收比较旧记录不被改写及新记录的合同语义，而非忽略实际 revision。

使用隔离 profile 证明旧样本、manifest、configuration_context、历史 revision、冻结/排队上报和回执的 bytes/SHA 不变；旧数据可读，新配置产生的新本地 PointFact 和 manifest 通过既有 `definition_check`、样本构造、对应上下文及上报路径验证，分别用不同的中文、英文和 comment sentinel 检查两种显示名没有泄漏或混进其他字段。可用受控假的 transport 捕获实际候选正文，禁止网络发送；如旧路径不可运行，必须明确 blocked/not_run，不以 v2 成功冒称其他路径成功。

配置 v1 与两库物理 schema 不变，仅新增可省略配置字段。旧数据读取不能重写原 payload/SHA；`deny_unknown_fields` 意味旧二进制可能拒绝带新字段的配置，必须在停机隔离副本验证安全拒绝且不误创建空库、不执行错误采集。新旧程序、容量和上下文验证没有真实结果前均是待证设计；若需要放宽 PointFact 键集、改变旧上报契约、DDL/已用 profile 迁移或复制真实数据，停止并回 PM 另行批准。

## 4. r2 已批准的 Development 文件 allowlist

以 `automation-world/data-acquisition-agent/` 为根；花括号只展开列出的名字。r2 相比 r1 仅增加下表中的 `src-tauri/src/domain/point_naming.rs` 与 `src-tauri/src/services/local_point_naming.rs`，供单点命名预览原子整合；本 r2 已获 Human Owner 精确批准。发现额外文件需要写入先回 PM。PM 阶段只写本 spec，后续角色按各自 gate 行事。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 配置、来源复导 | `src-tauri/src/domain/{local_configuration.rs,source_import.rs,point_naming.rs}`；`src-tauri/src/services/{local_configuration.rs,local_point_naming.rs}`；`src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}` | `src-tauri/src/infrastructure/local_store/point_display_names_tests.rs` |
| 用户界面与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | 无 |
| 样本和上报测试 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`；`src-tauri/src/services/local_delivery_tests.rs`；`tests/{point-editing.test.mjs,facts-delivery.test.mjs}` | `tests/point-display-names.test.mjs` |
| 文档 | `src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `CODE_INDEX.md`（实际结构变化时依仓库契约） |
| STD 角色记录 | 本 spec 仅 PM/Owner | 批准后 Development 创建 `tasks.md`；handoff 后独立 Verification 创建 `checklist.md` |

不得修改 `Point` 事实结构、`facts_wire::definition_check` 或公共上报合同，亦不改 DDL、`schema.rs`、依赖/锁、`.env`、其他任务或真实 profile。若现有 Point 编辑 UI 分散在其他文件，超出白名单先回 PM。新增列沿用公共表格工具：普通列拖拽、最小宽、横向滚动、稳定键隔离、刷新/切页/重启恢复和恢复默认；功能列可固定，本机偏好不进业务配置。

## 5. 验收标准（拟议，均未执行）

| 编号 | 可验证通过标准 |
| --- | --- |
| DA18-01 | 新点双语默认空；中英文独立设置、只填一侧、清空、保存/重开均保持精确 Unicode；缺失映射正确显示空，错误键/null/类型/超 256 UTF-8 字节被拒绝。 |
| DA18-02 | 顶栏切换仅显示当前语言，空值不回退 name/comment/另一语言；切换和取消不改变 ETag、草稿、版本或样本。编辑框的 comment 值与双语均可独立维护。 |
| DA18-03 | 点 ID 一一关联；同身份复导、改名、分组和地址修改保留双语；新增/删除/DB 或 PLC 删除、ID 改变及并发操作无跨点污染、孤儿或历史改写。原来源、树、leaf 和命名校验不变。 |
| DA18-04 | 新程序零写读取含旧版本和样本的自有合成 profile；旧程序面对带 pointDisplayNames 的新配置安全拒绝而不误采、不建空库；两库 schema 与所有旧 payload/SHA 保持，不能以空 profile 冒称兼容。 |
| DA18-05 | 构造不同中文/英文/原 comment 的采样，原样本 PointFact 定义键不变，原校验和 manifest/context 引用通过；旧样本、历史、冻结/排队和 ACK bytes/SHA 不变。新 revision/context 允许不同，不能伪称新旧 bytes 相等。 |
| DA18-06 | 截获实际 v2 单样本、历史批次/冻结和可触达的旧采集/快照上报构造路径，逐路径验证既有字段及其存在/缺失语义：v2 body 的 `name`/value 原样且没有 comment；本地 comment 独立保持，旧 batch 如按原合同带 comment 则保留；两个显示名 sentinel 不出现在任何外发字段中，无真实 POST。不可达路径明确标记未测。 |
| DA18-07 | 中文英文原生点表、编辑框、语言切换、列宽拖动/恢复和旧功能回归；隔离环境真实记录 Rust/Node/类型检查与构建结果，不外推其他平台或现场。 |
| DA18-08 | 同一单点同时改技术名、中英文和已有允许字段，预览与确认使用一个候选和一次 CAS；结果全成或已知提交前失败全不变，名字不串点/PLC。缺少新字段的旧请求和批量 generate 原行为、命名/来源/地址校验均保持。 |
| DA18-09 | 空串单侧/双侧清空、缺省保留及 null/缺键/未知键/超 256 UTF-8 字节负例；伪造或篡改任一双语值/摘要/token、过期、过期 ETag、并发编辑、取消与已知提交前失败均拒绝且不写本次编辑；结果未知先重读。测试覆盖编辑器打开前已有“保存草稿并编辑”的先行保存边界，防止错误计为取消后的写入。 |

## 6. 执行、回退及 handoff

本 r2 经 Human Owner 精确批准后 Development 才可继续并更新既有 `tasks.md`（保留 r1 阻塞历史），使用自有新合成 profile、停机的合成旧版本副本及隔离构建目录完成自检并交付正式源码；fresh-context Verification 独立创建 checklist，Human Owner 最终验收另行决定。示例检查：`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names -- --test-threads=1`、`node --test tests/point-display-names.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`；`CARGO_TARGET_DIR`/`RUN_DIR` 指向隔离临时目录。按实际路径记录命令、退出码、系统、候选和未执行项；不使用真实数据库、设备、网络或用户联调 profile。

若旧二进制不能安全拒绝含新元数据的配置，或严格事实链、容量、旧上传链不兼容，停止并回 PM，不以清除字段或改写历史绕过。回退只用经验证的停机合成副本/原备份；真实 profile 备份、恢复、迁移另行授权。DS-003 / DAA-017 均依赖本任务及 DS-004 完成包括 Human Owner 最终验收的 STD，另行审批后才实施。

PM 使用 `aiis`、`project-governance`、`plc-point-mapping`；后续 Development 按触达使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，Verification 以 fresh context 独立复核。自检/QA 均不自动批准生产或现场行为。

## 7. r1 Human Owner 实施范围批准记录（历史）

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 DS-004 r1 和 DAA-018 r1 的实施范围。请按 STD 先完成两端双语显示名的开发和独立验证，导出、导入功能暂不实施。

此决定批准本任务 `DAA-018 r1` 的精确实施范围，批准前完整草案 SHA256 为 `2adc3ae0f61ee6b37bf1ba111d6f26e2f7e844f64a1512b5b5c4e68319cbbd79`；允许按本规格开展 Development 自检及 fresh-context Verification。该批准不代表 Human Owner 最终验收，不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布；两项基础任务各自完成 STD 最终验收后，导出/导入仍须独立精确批准。

## 8. r2 修订与批准 gate

2026-11-17（Asia/Shanghai）Development 在 r1 批准后、修改代码前记录 `dev_blocked`：原文件 allowlist 未包含命名预览 DTO 与服务，无法让单点双语修改和技术名共用受控候选与单次 CAS。本 r2 仅增加 §4 两个现有文件及 §2.1、DA18-08/09 所述与之直接对应的合同、验收与失败风险；保留 r1 的其余需求、验收、文件范围、上报/历史/设备边界。Human Owner 已精确批准 r2 实施范围及版本衔接；Development 可按 r2 继续，仍需 fresh-context 独立验证和 Human Owner 最终验收，DS-004 独立推进不受此阻塞。


### r2 实施范围批准及版本衔接

2026-11-17（Asia/Shanghai），Human Owner 在交互问题中明确回复：

> 批准 DAA-018 r2 及版本衔接

该决定批准本任务 `aiis-ics-arch::DAA-018 r2` 的精确实施范围，并确认 r2 作为父设计中 DAA 双语基础的活动实施版本；用户审阅的 r2 草案 SHA256 为 `58c4aade878dbed5bbb19f0c4b13cf96fcb29d1e339f3df796b5027b659aa52b`。r1 的批准和开发阻塞历史保持；r2 仍需 Development、fresh-context Verification 和 Human Owner 最终验收。只有 DAA-018 r2 与 DS-004 各自完成最终验收后，才能进入分别另行批准的导出/导入实施；本批准不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布。

## 附录 A：已批准 r1 完整原文（历史）

写前完整 r1 SHA256：`107cd65850290950387958b539b8eddb685afd01650e7cc077acde268ededcb5`。下方围栏首行之后至闭合围栏之前是原始 UTF-8 字节，保留原末尾换行和 Human Owner 批准原话；该批准只针对 r1。

~~~~~~~~~~~~~~~~markdown
Task ID: DAA-018
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: DAA-018 r1 实施范围已获 Human Owner 批准 -> Development tasks.md / developer_handoff -> fresh-context Verification checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 点位中英文显示名，保持采样与现有上报合同
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立履行 STD，不继承其他任务的实施批准、QA 或最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r3; device-simulator::DS-004 r1; aiis-ics-arch::DAA-017 r2; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: aiis-ics-arch::ARCH-PLC-001 r3 精确设计批准；DS-003 / DAA-017 在本任务及 DS-004 均完成 STD 最终验收后才启动实施

# DAA-018：点位中英文显示名与事实隔离

## 1. 状态与边界

Human Owner 于 2026-11-17（Asia/Shanghai）要求先统一 DS、DAA 点位中英文显示名，再做导出导入；显示名跟随顶栏语言，未设置留空，DAA 上报不带显示名，当时要求暂不改代码。[ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获 Human Owner 批准；本任务 r1 实施范围已获 Human Owner 批准；之前 r2 设计批准是历史事实，最终验收仍待独立验证后决定。本任务 owner 为 DAA，独立走 STD；与 DS-004 分别完成独立 QA 和 Human Owner 最终验收后，才能启动各自另批的 DS-003 / DAA-017 实施。

只增加 DAA 本地点位双语显示名的编辑、配置存储及既有采样/上报兼容；既有 `Point.name` 仍为稳定程序名，原 `Point.comment` 仍是独立注释。禁止从程序名、路径、comment 或另一语言猜测/复制/翻译；不修改 JSON 导入导出、DS/FF/CA、后端、公开合同、SQLite 物理 schema、已有 profile/现场设备。DAA-017 后续负责目录中的 description 与 comment 的明确预览及映射，本任务不把 comment 冒充显示名。

## 2. 配置和用户体验

1. 当前 [DAA Point](../../src-tauri/src/domain/local_configuration.rs) 没有语言化显示名；`name` 和 `comment` 不能借来冒充它。拟在现有 schema_version 1 配置顶层增加可省略映射 `pointDisplayNames`，键为**本地点 UUID**，值是严格对象 `{"zh-CN":"...","en-US":"..."}`；每键恰为字符串、各 ≤256 UTF-8 字节，缺一个键、null、非字符串或额外键拒绝。配置缺整个映射/该点项视为两语言均 `""`，显式保存时两值都空可省略该项及空映射；任一非空保存两个键。合法 Unicode 字符及首尾空格原样保留，不隐式翻译或清洗。整个映射和单项为 null 均非法；读取时若兼容允许空映射或两键均空，不能触发自动写回。
2. 点位列表保留技术 `name`，另列出顶栏当前语言对应值；该语言空时为空白或明确未设置占位，不回退任何其他字段。点位编辑同时展示中英文输入和原有独立 comment；编辑、清空任何一侧不得修改另一侧、name、comment、地址、ID、组或启用。切换顶栏语言仅改变显示，不写配置、ETag、激活版本或样本；取消和未确认编辑不写。所有界面提示中英文齐全，原有点表按公共列宽能力处理。
3. 键必须为当前配置中唯一存在的本地点 UUID，不能指向其他 PLC 的不存在点、已删除点或无效 ID；一个点只对应一项。现有同 ID 的 DB/UDT 复导、改名、地址及分组修改保留两语言。显式删除点/DB/PLC 时，在相应草稿/来源变更事务中仅移除其映射，其他点、旧 revision 和样本不变；点 ID 被替换或重绑时不得悄悄把旧点名称附到新身份，必须通过原流程明确预览和用户确认。保存和导入不能绕开 `protect_derived` 或原有点/来源校验。
4. 保存沿用草稿 CAS 和显式激活流程；UI 语言和未完成编辑不触发保存。配置容量含新增元数据：超限返回明确错误，原草稿、source 和版本不动，不截断文字或丢映射。实际用户现有 profile 的读写、复制和迁移均未授权。

## 3. 样本、上报和版本安全

目前 [local_scheduler](../../src-tauri/src/services/local_scheduler.rs) 以 `point.clone()` 形成 `PointFact.definition`，而 [facts_wire](../../src-tauri/src/domain/facts_wire.rs) 的 `definition_check` 对 Point 定义严格闭合。因此本设计**不向 Point 或 PointFact 添加显示名字段**，配置级映射通过本地点 ID 关联；不得放宽严格字段验证，也不得把显示名混进 `name`、`comment`、value、quality 或任意输出字段。

配置 revision 的完整 context 可以包含 `pointDisplayNames`，但实际外发正文不能包含显示名：验证当前 `sample_upload` 的 plc-facts/v2 单样本 body、`facts_wire` 的历史分批/冻结正文及可触达的旧采集/快照上报路径；分别核对实际请求 body 与原合同及字段原有的存在/缺失语义：v2 Point 使用原有程序 `name`，其正文原本没有 `comment`，不能为了测试新增；本地 PointFact.definition 的 comment 独立保持，历史 batch 若原本携带 comment 则按原行为保留。其他字段、结构和含义不变。新配置按原流程保存/激活后可正常生成新的 `configRevision`、时间、样本 ID、上下文 SHA 和其既有摘要字段，故不能要求新旧样本/上报全文或字节相等；历史 batch 的 `contextSha256` 是原有摘要字段，不包含名称明文，可随配置上下文变化；仅显示名变化时 Point 定义集摘要应维持原有计算语义，原来源准入/确认规则不被绕过。验收比较旧记录不被改写及新记录的合同语义，而非忽略实际 revision。

使用隔离 profile 证明旧样本、manifest、configuration_context、历史 revision、冻结/排队上报和回执的 bytes/SHA 不变；旧数据可读，新配置产生的新本地 PointFact 和 manifest 通过既有 `definition_check`、样本构造、对应上下文及上报路径验证，分别用不同的中文、英文和 comment sentinel 检查两种显示名没有泄漏或混进其他字段。可用受控假的 transport 捕获实际候选正文，禁止网络发送；如旧路径不可运行，必须明确 blocked/not_run，不以 v2 成功冒称其他路径成功。

配置 v1 与两库物理 schema 不变，仅新增可省略配置字段。旧数据读取不能重写原 payload/SHA；`deny_unknown_fields` 意味旧二进制可能拒绝带新字段的配置，必须在停机隔离副本验证安全拒绝且不误创建空库、不执行错误采集。新旧程序、容量和上下文验证没有真实结果前均是待证设计；若需要放宽 PointFact 键集、改变旧上报契约、DDL/已用 profile 迁移或复制真实数据，停止并回 PM 另行批准。

## 4. 已批准的 Development 文件 allowlist

以 `automation-world/data-acquisition-agent/` 为根；花括号只展开列出的名字。发现额外文件需要写入先回 PM。PM 阶段只写本 spec，后续角色按各自 gate 行事。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 配置、来源复导 | `src-tauri/src/domain/{local_configuration.rs,source_import.rs}`；`src-tauri/src/services/local_configuration.rs`；`src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}` | `src-tauri/src/infrastructure/local_store/point_display_names_tests.rs` |
| 用户界面与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | 无 |
| 样本和上报测试 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`；`src-tauri/src/services/local_delivery_tests.rs`；`tests/{point-editing.test.mjs,facts-delivery.test.mjs}` | `tests/point-display-names.test.mjs` |
| 文档 | `src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `CODE_INDEX.md`（实际结构变化时依仓库契约） |
| STD 角色记录 | 本 spec 仅 PM/Owner | 批准后 Development 创建 `tasks.md`；handoff 后独立 Verification 创建 `checklist.md` |

不得修改 `Point` 事实结构、`facts_wire::definition_check` 或公共上报合同，亦不改 DDL、`schema.rs`、依赖/锁、`.env`、其他任务或真实 profile。若现有 Point 编辑 UI 分散在其他文件，超出白名单先回 PM。新增列沿用公共表格工具：普通列拖拽、最小宽、横向滚动、稳定键隔离、刷新/切页/重启恢复和恢复默认；功能列可固定，本机偏好不进业务配置。

## 5. 验收标准（拟议，均未执行）

| 编号 | 可验证通过标准 |
| --- | --- |
| DA18-01 | 新点双语默认空；中英文独立设置、只填一侧、清空、保存/重开均保持精确 Unicode；缺失映射正确显示空，错误键/null/类型/超 256 UTF-8 字节被拒绝。 |
| DA18-02 | 顶栏切换仅显示当前语言，空值不回退 name/comment/另一语言；切换和取消不改变 ETag、草稿、版本或样本。编辑框的 comment 值与双语均可独立维护。 |
| DA18-03 | 点 ID 一一关联；同身份复导、改名、分组和地址修改保留双语；新增/删除/DB 或 PLC 删除、ID 改变及并发操作无跨点污染、孤儿或历史改写。原来源、树、leaf 和命名校验不变。 |
| DA18-04 | 新程序零写读取含旧版本和样本的自有合成 profile；旧程序面对带 pointDisplayNames 的新配置安全拒绝而不误采、不建空库；两库 schema 与所有旧 payload/SHA 保持，不能以空 profile 冒称兼容。 |
| DA18-05 | 构造不同中文/英文/原 comment 的采样，原样本 PointFact 定义键不变，原校验和 manifest/context 引用通过；旧样本、历史、冻结/排队和 ACK bytes/SHA 不变。新 revision/context 允许不同，不能伪称新旧 bytes 相等。 |
| DA18-06 | 截获实际 v2 单样本、历史批次/冻结和可触达的旧采集/快照上报构造路径，逐路径验证既有字段及其存在/缺失语义：v2 body 的 `name`/value 原样且没有 comment；本地 comment 独立保持，旧 batch 如按原合同带 comment 则保留；两个显示名 sentinel 不出现在任何外发字段中，无真实 POST。不可达路径明确标记未测。 |
| DA18-07 | 中文英文原生点表、编辑框、语言切换、列宽拖动/恢复和旧功能回归；隔离环境真实记录 Rust/Node/类型检查与构建结果，不外推其他平台或现场。 |

## 6. 执行、回退及 handoff

本 r1 经 Human Owner 精确批准后 Development 才创建 `tasks.md`，使用自有新合成 profile、停机的合成旧版本副本及隔离构建目录完成自检并交付正式源码；fresh-context Verification 独立创建 checklist，Human Owner 最终验收另行决定。示例检查：`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names -- --test-threads=1`、`node --test tests/point-display-names.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`；`CARGO_TARGET_DIR`/`RUN_DIR` 指向隔离临时目录。按实际路径记录命令、退出码、系统、候选和未执行项；不使用真实数据库、设备、网络或用户联调 profile。

若旧二进制不能安全拒绝含新元数据的配置，或严格事实链、容量、旧上传链不兼容，停止并回 PM，不以清除字段或改写历史绕过。回退只用经验证的停机合成副本/原备份；真实 profile 备份、恢复、迁移另行授权。DS-003 / DAA-017 均依赖本任务及 DS-004 完成包括 Human Owner 最终验收的 STD，另行审批后才实施。

PM 使用 `aiis`、`project-governance`、`plc-point-mapping`；后续 Development 按触达使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，Verification 以 fresh context 独立复核。自检/QA 均不自动批准生产或现场行为。

## 7. Human Owner 实施范围批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 DS-004 r1 和 DAA-018 r1 的实施范围。请按 STD 先完成两端双语显示名的开发和独立验证，导出、导入功能暂不实施。

此决定批准本任务 `DAA-018 r1` 的精确实施范围，批准前完整草案 SHA256 为 `2adc3ae0f61ee6b37bf1ba111d6f26e2f7e844f64a1512b5b5c4e68319cbbd79`；允许按本规格开展 Development 自检及 fresh-context Verification。该批准不代表 Human Owner 最终验收，不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布；两项基础任务各自完成 STD 最终验收后，导出/导入仍须独立精确批准。
~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
