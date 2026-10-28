Task ID: DS-001
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner accepted DS-001 r1 and the current DS delivery on 2026-10-27; acceptance-only closeout recorded in section 9; independent QA remains explicitly waived for this task
Owner Final Acceptance: owner_accepted, 2026-10-27 (Asia/Shanghai), section 9
Workflow Mode: STD
Workflow Exception: Human Owner explicitly replaces independent QA for this task with Development self-check, a text-only bilingual user guide and Human Owner manual acceptance; not a complete standard STD verification chain
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: independent_fix
Capability: 点位策略表格与安全批量草稿编辑、初值输入修复和必要易用性整改
Owner: Device Simulator
Acceptance Chain Reference: DS-001 r1 PM -> Human Owner scope approval -> Development self-check and text guide -> Human Owner manual acceptance
Related Task: aiis-ics-arch::ARCH-AW-005 r5; aiis-ics-arch::ARCH-AW-004 r2

# DS点位策略表格与易用性整改

## 1. 当前授权与记录边界

2026-10-23（Asia/Shanghai），Human Owner先同意整理本spec；当时仅为草案准备授权。随后同日已明确批准本精确DS-001 r1，原话与批准草案指纹见§8。**当前范围gate已通过，交Development按本spec实施、必要自检及纯文字手册，再交Owner人工验收；本任务不单独运行QA。** PM本次仅登记批准，不代实施、测试或创建tasks/checklist。

Owner明确提出：“你可以吧qa这部分变成生成操作手册，我也要核对操作步骤。有问题我再一个个反馈。”按[canonical workflow“例外”](../../../../.codex/workflows/development-lifecycle-workflow.md#例外)，本任务保留PM、精确范围审批和Development必要自检，取消独立QA轮次，由Owner按手册核对并明确最终验收。

此安排只适用于DS-001，不是DIRECT、第四种默认模式或长期workflow修改；手册和自检均不记作qa_passed。

精确r1现已获批，Development接手后创建本目录tasks.md，记录实施、自检、纯文字手册交接及Owner反馈/返工；不伪造Verification checklist。PM在本spec批准/验收记录区引用实际Owner决定与对应tasks段落；spec合法状态仍为owner_approved，最终接受只由Owner真实原话确认。主协调据此同步本地PLAN的聚合状态，注明“独立QA未执行（Owner本任务例外）”。

任务唯一管理入口是[DS PLAN](../../PLAN.md)及其[任务目录](../README.md)。旧[005 r5](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)及[004 r2](../../../../plans/ARCH-AW-004-ds-detailed-design/spec.md)只作关联历史，不迁移/复制其bundle，不继承范围批准、QA通过或Owner接受。

## 2. 只读起点与本次交付

起点HEAD为`1fa1ce50a521ebd51c2c43389db011a76f2d74bf`，PM起点git status clean；后续判断以实际工作树为准，不覆盖并行变化。

- 旧005产品candidate306a09d5有独立技术QA历史，Owner最终验收未完；其记录与本任务接受链分别保留。
- 2026-10-22手册操作发现非零初值真实键入后回退；PolicyEditor初值和fixedValue都有同类change绑定，fixed须一并核查/修复，不能把同类风险写成已实测失败。
- 当前策略页按层级/DB/点选择编辑；没有本任务要求的点位策略表格或多选赋值。现有六模式为hold/fixed/ramp/sine/random/toggle。
- 当前版本选择仅在空选择时跟随latest；共享布局/命名弹层始终呈现命名列；点表编辑/删除缺少同类ds-actions容器。
- 旧手册附录B仍半成品，已有7张图是历史资料；Owner已取消本次截图交付，不新增图片，不自动删除历史原件。

本次只改变前端配置编辑与必要提示，继续使用现有workspace、稳定point ID、保存IPC及Rust校验。Rust仍是唯一运行时owner；批量不是运行值写入，不建立后台队列、第二runtime或新IPC。

## 3. 编号需求与交互决定

### R1. 策略页以点位表格为主

先选择一个PLC实例，再在独立筛选区域多选其DB；不选DB表示当前PLC全部DB。切实例重置DB筛选。表格按DB号、DB稳定ID分组，再按地址/点ID稳定排序。

DB名、点名、类型和结构地址只读，修改结构仍去DB点位页，不在策略表里新增结构入口。

每点显示有效模式、规则参数摘要、有效初值、唯一写方、逐属性继承来源及初值/策略确认状态。行来自同一配置草稿，不复制点实体或另造数据。明确标记“当前配置草稿”；不能拿旧loaded快照冒充草稿有效策略，也不能把前端预览当成服务端已确认。

有效值展示沿既有实例→DB→不重叠region→point逐属性覆盖及类型默认值。小型展示/编辑辅助只能解释既有语义；无效/无法判定者显示问题，服务端原校验仍为最终准入，不在前端重新实现规则执行器。

### R2. 单点弹窗与层级继承

单点“编辑策略”弹窗复用PolicyEditor，保持六种mode、现有rules/读写权限/初值能力。弹窗先编辑副本，明确保留或取消；取消不改草稿。

继续提供已有实例/DB/region上层策略入口及region能力，作为次级入口，不因表格整改丢失继承功能或把所有点隐式改成显式覆盖。

### R3. 选择范围明确且不串实例

最左列复选框；表头全选定义为**当前PLC、当前DB筛选结果的全部点，含所有分页**，显示已选N及筛选总数。

翻页保留选择；切实例或改变DB筛选立即清空选择，关闭过期批量编辑。空结果/零选择不能提交。

提交使用稳定point ID，不以行号/页码/名称定位。弹窗打开后实例、筛选、点集或有关草稿基线改变，拒绝陈旧提交并提示重开；不得把旧选择移到另一个PLC。

### R4. 批量字段三态与全量预校验

批量表单每个可改属性默认“不修改”；“统一设置”与“恢复继承”是不同动作。未启用属性不参与patch；0/false/空字符串与不修改/null继承不能混同。

规则按现有Rule整体语义构造，不能把不同mode的残留参数盲合并。

仅对选中point层覆盖操作，不修改其DB/region/实例父策略、结构、名称或未选点。混合类型只允许全部选中点均兼容的设置；列明不兼容点、DB、类型和原因，不静默跳过/转换类型。BOOL的toggle、数值规则、字符串fixed等沿既有类型/范围/规则限制；只改读取权限时不得要求其它未改初值相同。

先在临时候选中计算全部变化并校验，再一次性更新本地草稿；任一项失败则全不改，不生成部分草稿或逐点保存。默认取消不改；全“不修改”是无操作，不产生新版本。

后续保存失败保留待修草稿与错误，不冒充已持久化或已加载。

### R5. 联动、确认与运行边界

切mode所需owner/写权限/rule联动必须在提交前逐项可见，展示修改前后及影响点数；不能悄悄开放写入或把手工owner变成持续规则owner。用户取消则包括联动在内全部不改；只提交选中字段与已明确展示的必要联动，其它字段保留。

恢复继承只清相关point属性覆盖，不清无关属性；展示恢复后的来源和值。修改初值/策略使相应确认按现有规则失效，显式“保存并确认所选初值/策略”只确认所选点，不自动确认未选点或结构地址。不得在前端伪造确认摘要。

编辑→保留草稿→保存不可变候选→停止后预览/加载→显式启动保持分开。批量编辑/保存不调用运行值写入、自动apply或start；即使实例正在服务，编辑草稿也不改变其loaded值。

### R6. 修复真实初值及fixed输入

正常键入、删除重填、Tab/鼠标失焦、切点和保存后重新选择时，合法输入保留。修initial及同类fixedValue绑定，不能只让旧自动driver同步派发input/change绕过。

保留必要编辑缓冲/错误，未完成数字不能被静默回填或转成0。

BOOL false、数值0都合法；INT非零7、REAL非零20.5及fixed非零12作为回归例，连同负数/非法输入按真实类型边界检查。输入过程允许临时文本，提交时校验；非法值明确阻断保留/确认/保存而不丢用户原文本。继承/null与显式值的开关保持可区分。

### R7. 点表操作间距

DB点位表编辑/删除复用ds-actions的8px gap和足够宽操作列，窄屏可有序换行，不能按钮粘连/覆盖。允许只读核对本allowlist内相邻同类操作区，仅修实际发现的同类缺陷并在tasks列明；不重做其它页面、公共CU外观或整套布局。

### R8. 清楚展示保存与加载版本

保存成功后提示最新保存版本和当前实例selected/loaded版本，标记尚未加载。提供明确选最新动作；默认尚未人工选择时可跟随latest，一旦用户明确选择历史版本则保留选择并提示它不是最新，不在后台覆盖。

预览加载前能核对实际选中版本；保存、加载、启动仍分离。

### R9. 人工地址预览只展示相关事实

PointNamePreviewDialog按preview.kind区分布局与命名。人工布局不再展示无关空命名表/误导的暂无数据；展示目标DB、长度、当前候选点地址/类型及人工理由等可从现有preview.workspace/details取得的核对信息，缺数据如实提示，不编造校验结果。命名预览继续显示真实命名行；确认/取消及token/ETag流程保持。

### R10. 纯文字双语操作手册

更新既有USER_GUIDE双语，按“页面→按钮→填写示例→确认→预期→错误恢复”逐步写；先手工DB31三点（BOOL0.0/INT2/REAL4、长度8），再固定Alpha/Beta/Measure多DB/UDT导入。只读输入为`automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-multi-db/multi.db`和同目录`types.udt`，只选Alpha/Beta映射DB71/88、Beta显式选择Measure闭包，不改样例。沿用既有地址/命名与DS初值边界；例值不是产品拓扑约束，不把TIA赋值或RETAIN当DS保值。

加入单点编辑、DB多选/清空、全筛选含分页、批量不修改/统一设置/恢复继承、模式联动、混合类型失败且草稿不变、旧版与最新版选择、保存/停机加载/启动、非零初值与fixed输入核对。旧“仅逐点/尚无批量”及输入限制文字按实际修复结果更新；未完成Owner步骤明确待核对，不能写成已运行通过。

取消本次截图及自动点图流程；手册正文不依赖截图才能完成操作，既有7图及来源文件保留为历史，不新增、不删除。同步DS README双语和DS详细设计的相应操作入口/现状说明，不借此扩设计范围。

### R11. 必要自检与Owner逐项反馈

Development完成一次`pnpm build`（现脚本已含vue-tsc），及少量纯函数输入/选择/patch兼容性用例，不新装测试框架。普通真人键入、桌面保存及运行值观察由Owner按手册核对；不再CUA逐步自动点击/取图，不重复三窗，不重跑S7/16连接/性能/资源矩阵。

tasks逐项区分“DEV检查结果”“Owner待操作”“Owner反馈及修复后核对”“独立QA未执行”。Owner反馈只修本范围且复核受影响项；实质增量/超allowlist先回PM修订并取得精确批准。此例外不替代整体Stage B或未来另批DAA–DS联调所需独立核验与Owner接受。

## 4. 精确写入面与保护面

D=`automation-world/device-simulator`；下表全部为D相对路径，不含隐式递归或同名其它目录。PM当前只写本spec。未来实现须先获精确r1批准；列为可改不表示必须全部修改。

| 路径 | 批准后用途/限制 |
| --- | --- |
| `src/app/simulator/views/policies/index.vue` | 策略表格、PLC/DB筛选、分页选择、单点弹窗与原层级入口。 |
| `src/app/simulator/components/PolicyEditor.vue` | initial/fixed输入及必要联动展示/提交。 |
| `src/app/simulator/components/PolicyBatchDialog.vue`（新增） | 有界批量表单/影响预览/取消；不承载运行时。 |
| `src/app/simulator/policyEditing.ts`（新增） | 小型纯函数：草稿有效策略展示、类型兼容、三态patch/全量预校验；非新业务runtime。 |
| `src/app/simulator/views/points/index.vue` | 点表操作间距，现有确认入口必要文字；不改结构业务。 |
| `src/app/simulator/views/instances/index.vue` | 最新/历史版本选择与selected/loaded提示。 |
| `src/app/simulator/components/PointNamePreviewDialog.vue` | layout/names相关内容分支。 |
| `src/components/console/ConfigRevisionBar.vue`、`src/console/composables/useDeviceSimulator.ts` | 必要草稿提交、编辑未完成保护及版本展示状态；现有IPC调用不变。 |
| `src/styles/app.css` | 本任务筛选、表格、批量弹窗及操作间距的必要局部布局。 |
| `src/app/simulator/locales/zh-CN.json`、`src/app/simulator/locales/en-US.json` | 新增/修改文案键对称。 |
| `tests/policy-editing.test.mjs`（新增） | 最小既有Node/TypeScript通道的纯函数用例；不引框架/依赖或旧UI驱动。 |
| `USER_GUIDE.md`、`USER_GUIDE.zh-CN.md`、`README.md`、`README.zh-CN.md` | 纯文字步骤与工程入口。 |
| `CODE_INDEX.md`（新增） | 仅新辅助/组件/用例的真实结构导航。 |
| `plans/DS-001-policy-table-and-usability/spec.md` | PM范围/批准/Owner决定引用；不属Development写面。 |
| `plans/DS-001-policy-table-and-usability/tasks.md`（批准后创建） | Development实施/自检/手册与Owner反馈事实。 |

仓库根`docs/AIIS_DS_Detailed_Design.md`、`docs/README.md`、`docs/README.zh-CN.md`只作本整改操作说明/手册导航同步，Development可在批准后改对应段落；不改004或005 bundle。草案形成后的12个导航入口由主协调机械同步：D的README/PLAN/plans README双语6件、根PLAN/plans README双语4件、automation-world的PLAN双语2件，仅动DS相关行/入口。当前PM不写导航；此安排不授权Development随意改根/AW，DS PLAN仍为唯一任务管理入口。

**保护**：`runtime/`、`native/`、`src-tauri/`及SQLite schema/数据；`src/services/deviceSimulator.ts`现有IPC facade/DTO；package/Node/Cargo/锁/构建配置；CU/DAA/shared core及fixtures；旧tests UI驱动；旧005 spec/tasks/checklist/证据；历史截图/原件。不能为UI新增IPC或改Rust来绕现有验证，若现有合同确实不足，记录具体缺口回PM。

**排除**：Excel导入/导出/模板，旧simulation_profile.xlsx直接导入，sequence新mode，通用表格框架，产品新页面/权限模型/协议，真实PLC/真实用户profile修改，DAA–DS读取至SQLite联调，阶段C、Backend、发布/安装/签名/Git refs及邮件通知。

## 5. 轻量验收口径（待实施及Owner核对）

下列AC是待验证标准，不是当前通过结论；DEV纯函数/构建结果不替Owner桌面操作。手册必须让Owner无需自行推导隐藏步骤即可逐项核对。

| AC | 对应需求 | 可核验结果 |
| --- | --- | --- |
| AC01 | R1 | 选一个PLC；不选DB见其全部点，多选DB仅见所选DB范围；按DB分组/稳定排序，结构地址只读。 |
| AC02 | R1–R2 | 表格显示草稿有效模式/参数/初值/owner、逐属性来源及确认；单点六模式可编辑，原上层入口仍可用。 |
| AC03 | R3 | 11个合成点、每页10时全选N=11；翻页仍选11；改DB筛选/PLC清零，提交稳定ID不串实例。 |
| AC04 | R4 | 三态patch区分不修改/设置/继承；单改clientRead保留其它属性、结构和未选点；全不修改无操作。 |
| AC05 | R4 | BOOL+INT批量toggle或不兼容初值明确逐点原因；包含一个非法项时整个草稿不变，无跳过或部分成功。 |
| AC06 | R3–R5 | 空选、陈旧基线、取消均不变；同类型合法批量一次更新全部选中点，父策略/别实例保持。 |
| AC07 | R5 | mode/owner/权限联动提交前可见；恢复继承可核来源；确认只作用选中初值/策略，不伪造证明或改运行值。 |
| AC08 | R6 | Owner普通键入INT7/REAL20.5/fixed12及false/0，失焦、保留、保存重新选择仍在；非法文本有错且不能提交。 |
| AC09 | R7 | DB点表编辑/删除间距8px、操作列足宽，常用窗口不重叠；相邻修复只列真实发现项。 |
| AC10 | R8 | 保存后看得出latest与loaded不同；无明确历史选择可跟最新，明确选旧版不被自动改选，加载预览版本清楚。 |
| AC11 | R9 | DB31人工布局预览显示长度8/三点地址核对，无空命名误导；真正命名预览仍有真实行和确认/取消。 |
| AC12 | R10 | 双语文字手册完整覆盖手工三点→Alpha/Beta/Measure导入及单点/筛选/批量/冲突/继承/版本步骤，无新截图要求。 |
| AC13 | R10 | README/docs入口可达；旧限制仅在修复事实成立后更新；7图和旧005历史保留，待Owner步骤诚实标注。 |
| AC14 | R11 | 一次pnpm build含vue-tsc成功；小用例记录真实命令/退出码及覆盖，不安装依赖、不跑旧协议或自动CUA矩阵。 |
| AC15 | R11 | tasks自检与Owner反馈分列；无QA verdict/checklist；Owner明确最终接受才标接受，不转移旧005或联调接受权。 |
| AC16 | R1–R11 | diff仅批准allowlist，Rust/native/IPC/schema/deps/共享来源/旧证据无改动；未保存/保存/加载/启动边界保持。 |

## 6. 开发自检、人工手册与交接顺序

1. Owner批准精确r1后，Development读完整spec，创建tasks并核当前工作树，不覆盖其它任务。
2. 先修PolicyEditor真实输入，再做草稿辅助/策略表格/批量；依次收口间距、版本、地址预览和双语提示。
3. 复用现有Node/TypeScript通道跑少量纯函数断言：11点跨页集合、三态patch、false/0、混合类型全失败/草稿不变、未选字段/取消/基线变化。允许最小test文件，不改package脚本或添加依赖；无真实输入证明则留给Owner，不能冒称模拟真人已通过。
4. 在D执行一次`pnpm build`，记录环境/exit code；只有失败修复或后续相关代码变化才补必要复核，不机械扩大矩阵。
5. 交纯文字双语手册及受影响项清单，由Owner使用自有隔离合成profile人工核对真实输入、保存/加载、启动观察及导入；不用真实用户库，不运行DAA客户端。端口例30102/30103若被占用先报事实，不kill他人。
6. Owner逐项反馈→Development仅修受影响范围并记自检/待复核；最终Owner明确接受→PM如实记录链接、主协调同步DS PLAN。没有独立QA，不造检查通过的第四事实面。

本次无新运行时或新自动化基础设施；不重跑普通启动三窗/S7/16连接/性能/资源矩阵。Owner正常使用中的启动/关闭是手册步骤，不是要求其重复验证固定轮次。未来DAA–DS联合测试仍另批并按其独立核验合同执行。

## 7. 风险、回退与未决项

- **批量误伤**：三态字段、稳定ID、前后预览、一次草稿提交；异常保持原草稿，取消不保存。用户已保存后可显式选旧版本按原停机流程恢复，不自动回滚或删除SQLite。
- **继承/权限歧义**：逐属性来源与联动可见；前端辅助若无法与现有校验一致则阻断该提交并回PM，禁止偷偷放宽Rust合同。
- **无独立QA的残余风险**：Owner已明确选择本任务替代安排，并于2026-10-23批准精确r1；DEV自检与手册不覆盖独立核验，不能宣称技术/协议重新接受。
- **输入验证盲区**：小用例只证明纯函数；真实键入/焦点/保存由Owner核对。若需超allowlist改变壳/IPC/runtime，先修订范围，不能借修UI扩后端。
- **回退**：只回退本任务可识别前端/文档差异，先保全未保存意图；不reset工作树、不回退他人内容，不改旧005记录或真实配置。
- 当前没有等待技术研究的选型项；全选/批量失败/继承/版本选择均已作推荐决定。精确r1范围及本任务例外已获Owner批准；后续gate为真实实施、必要开发自检、文字手册交接及Owner人工验收。

## 8. Skill路由与批准记录

PM已消费aiis/project-governance和实际pm角色；Development按前端面使用frontend-ui（含相应框架/设计指引）、i18n-workflow，新增文件/结构导航使用code-document-indexer。desktop-tauri/rust-runtime只作既有边界参考，本任务不授权改壳/Rust；发现需触及时先回PM。不激活Verification，不为例外改长期AGENTS/workflow或checker。

| 日期 | 决定 | 记录与下一gate |
| --- | --- | --- |
| 2026-10-23 | Owner同意准备DS-001 r1，并明确手册替代独立QA、本人逐项反馈 | 草案阶段历史；同日精确批准见下行。 |
| 2026-10-23（Asia/Shanghai） | Human Owner明确批准精确DS-001 r1 | 批准草案SHA `569cbe1482b01b8db0753bedf4dabf02c262909e5304e73973b640288e807cab`；本协调会话直接用户批准，当前交Development，最终验收待发生。 |
| 2026-10-23 | Development已交接 | [本地tasks交接记录](tasks.md#8-developer-handoff)为developer_handoff；实施及必要自检事实见该记录，当前交Owner按纯文字手册人工核对。 |
| 2026-10-27（Asia/Shanghai） | Human Owner最终验收DS当前版本，明确更新DS-001及005 r5并收尾 | 真实决定及收尾见§9；本任务聚合状态为owner_accepted，独立QA未执行，不填qa_passed或继承旧验收。 |

Human Owner本轮批准逐字原话：

> 可以，批准 DS-001 r1 spec。按范围完成策略表格、DB 筛选、单点和批量编辑、初值输入及间距整改，同步纯文字操作手册。只做必要开发自检，我按手册人工验收，不再单独跑 QA。DAA–DS SQLite 联调另批，阶段 C 暂不开展。

本批准授权后续按范围实施，不表示已实现、自检通过或最终接受。

PM草案阶段的格式/本地链接/需求AC覆盖及写面自检记录保留。本次仅行政登记真实批准，已批准技术范围、R1–R11、AC01–AC16、allowlist和例外风险均不变；不运行UI、构建、协议、测试或QA，不创建tasks/checklist。

<a id="owner-acceptance-ds001"></a>
## 9. Human Owner最终验收与收尾（2026-10-27）

本协调会话Human Owner直接确认：

> 可以，DS 当前版本验收通过，更新 DS-001 和 ARCH-AW-005 r5 的状态并完成收尾，不再追加功能或重跑整套 QA。DAA–DS 的 S7 读取至 SQLite 联调另批，阶段 C 暂不开展。

据此，**DS-001 r1聚合状态为owner_accepted**。spec的合法范围状态保留owner_approved；[tasks](tasks.md)保留Development原始交接、自检及当时待核对项，不倒填逐条人工操作结果。本段由当前主协调代录Human Owner真实决定，不是新的PM、Development或独立Verification结果，也不创建checklist。本任务“必要开发自检＋纯文字手册＋Owner人工验收”的例外保持。

接受对象为本工程当前交付版本：DS-001策略表格、DB筛选、单点/批量编辑、初值输入与间距整改、双语纯文字手册，以及本会话另行批准的DIRECT反馈修正（策略弹层、时间/版本提示和13处公共表格）。DIRECT修正仍按各次会话交付，不倒称属于r1最初allowlist或旧005独立QA的原候选。ARCH-AW-005 r5的最终接受另见其[Owner验收记录](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)。本次只同步验收和索引，保持原代码、权限、协议、schema及依赖不变。

### 收尾与保留资源

- DS-001 Development未创建临时源码副本、worktree、数据库、监听或原生测试进程；已生成的dist和既有node_modules/target/gen用于正常启动及另批联调，保留，不作为临时垃圾清除。
- 13表格DIRECT自检的临时Vite 15196服务及独立浏览器页已在其交付时关闭；本轮只读复核15196、14194未见listener。合成表格图及历史七图保留为证据/历史资料，不冒充原生运行证明。
- 当前15194存在本工程Vite开发服务，已只读核对PID、argv及cwd；该服务不是本轮创建，保留其运行和用户配置/日志。未要求Owner关窗，未向该进程发送信号。
- 历史G0目录仍不存在，原件和失败记录继续保留；005历史证据及临时资源依赖见其验收收尾记录，不批量清理用户或其它任务资源。
- 本轮必要核对仅为验收状态、Markdown本地链接/JSON格式、git diff空白及源码未变检查；没有追加功能、构建、原生操作或整套QA。具体执行结果由本轮协调交付记录报告。

本次最终验收只关闭DS本轮交付；DAA–DS的S7读取至SQLite联调及其核验/验收另批、归DAA任务管理，阶段B整体不随DS验收自动关闭，阶段C暂不开展。没有发布、部署、Git refs或真实设备操作授权。
