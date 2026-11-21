Task ID: ARCH-FE-006
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_governance
Capability: frontend-js 跨模块页面及弹窗设计指导
Owner: frontend-js Core 前端设计基线
Acceptance Chain Reference: 本规格范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: AIIS::FUI-002

# frontend-js 跨模块设计指导

## 1. 目标与事实

将 Human Owner 在本会话中确认的交互预览整理进 [DESIGN.md](../../frontend-js/DESIGN.md) 和 [DESIGN.zh-CN.md](../../frontend-js/DESIGN.zh-CN.md)。文档服务于计划管理、数据采集、设备状态、过程监控等多模块的后续界面设计与生成。示例体现结构和视觉层级，具体字段、数据源和交互以所属业务需求为准。

当前双语 DESIGN 仅提供简短的基线描述。可参照 [计划列表](../../frontend-js/src/app/plan/components/TaskPage.vue)、[过程采集记录与指标列设置](../../frontend-js/src/app/equipment/components/observations/RecordList.vue)、[过程配置管理](../../frontend-js/src/app/monitor/views/observations/admin.vue)、[通用按钮](../../frontend-js/src/components/common/ActionButton.vue) 和 [主题样式](../../frontend-js/src/styles/theme.css)。计划列表的标题帮助使用 Element Plus Tooltip。过程数据管理的两个弹窗局部标题使用 16px / 590 / 1.35，而当前全局 standard-form-dialog 基础标题仍为 24px / 760。本次指导面向后续新建或重构，不把已确认的预览当作当前全局组件已实现的事实。

Human Owner 已认可本会话交互方案并要求写入文档。起草时该认可体现内容方向；此后对精确 r1 的批准见第 6 节。交互原型位于本次会话独立预览中，非持久仓库合同，不作为文档的长期链接或业务数据事实。

## 2. 范围和设计决定

1. 页面“二栏 / 三栏”指主卡从上到下的二段 / 三段，不是横向分栏。二段依次为标题与整卡操作、主体内容。三段在两者之间增加独立筛选或工具区。选择由工作区内容决定，同一数据的局部视图切换可在当前卡头或工具区完成。筛选区与内容区水平边距对齐，窄屏换行，宽表保留横向滚动。
2. 同页存在至少两个当前可访问的并列独立工作区，切换会成组更换下方标题、操作、筛选或内容时，在主卡上方使用紧凑的类别切换卡。只有一个可访问工作区时直接展示主卡。类别切换与表内筛选各司其职，上卡可搭配二段或三段主卡。
3. 主卡第一段标题及帮助居左，整卡状态靠右并位于右侧按钮组左边。状态只在对应事实存在时显示，以文字和语义色表达。多状态时默认显示优先级最高的一项，提供展开箭头及状态详情；单个状态无需展开。状态详情使用主题中性色实底、细边框、轻阴影、小号标题、分隔行和可读状态。鼠标悬停、键盘或点按可查看详情，并可关闭，布局窄时仍可访问。
4. 卡头操作以纯文字按钮为默认，有刷新时置于按钮组最右。卡头与筛选工具区使用项目共享大按钮，当前样式为 40px 高；表格操作列使用居中排布的共享小按钮，当前样式为 24px 高。主操作与次要操作采用既有语义和主题，不把个别模块动作或固定配色硬编码为跨业务流程要求。
5. Tooltip 参照计划列表和 Element Plus 的现有主题。标题旁的帮助触发项默认从左下方展开；工具按钮短提示优先在上方展示，空间不足时可避让。描述辅助术语、时间或操作含义，必要信息直接可见。支持悬停与键盘聚焦，并为触屏提供可访问方式，Escape 关闭。用主题适配明暗模式。
6. 弹窗从上到下至少三段。第一段标题居左，与主卡标题字号字重统一，整窗操作可选并靠右，刷新最右。第二段为表单、详情、表格等内容。最后一段右对齐取消与保存；纯查看只提供关闭。需要独立筛选或工具区时使用四段，第二段工具、第三段内容、第四段页脚。工具与内容边距对齐，内容过长时内容区滚动且标题和页脚保持可达；批量编辑的筛选、翻页和刷新保留未保存草稿。取消不提交，保存按相应业务合同处理。
7. 文档明确使用 theme.css token、现有共享组件与 frontend-ui skill 的适用边界，描述明暗主题、键盘和窄屏要点。项目级设计优先于 shared skill 默认设计语言。现有页面逐步按各自后续获批范围处理。

## 3. 写入边界与关联

本任务的实现面只允许修改 frontend-js/DESIGN.md 和 frontend-js/DESIGN.zh-CN.md。英文与中文覆盖相同决策和条件。不得修改业务代码、组件、样式、模板、配置、依赖、数据库或现有页面。

本规格由 PM 维护。获批后 Development 可创建本任务 tasks.md 并记录证据；交接后 fresh-context Verification 创建 checklist.md。协调者按既有流程机械同步根 PLAN、frontend-js/PLAN 与对应双语 task catalog，只记录已发生事实，不触及无关行。

共享 frontend-ui skill 的通用文档在独立任务 AIIS::FUI-002 实施。两任务互为相关项，各自具备范围批准和验收，不借由关联转移批准或 QA 状态。

## 4. 验收

| 编号 | 可检查结果 |
| --- | --- |
| AC01 | DESIGN 双语内容都覆盖二段 / 三段、上卡出现条件及其组合，示例可跨模块使用。 |
| AC02 | 双语均交代卡头标题、状态、按钮顺序，多状态优先摘要及展开层，纯文字和刷新最右，40px / 24px 与共享组件的对应关系。 |
| AC03 | 双语均描述计划列表式 Tooltip 的位置、内容边界、主题和悬停 / 聚焦 / 触屏 / Escape。 |
| AC04 | 双语均覆盖弹窗三段 / 四段、同主卡标题、可选头部动作和刷新顺序、底部按钮、滚动与批量草稿。 |
| AC05 | 文档明确适用方向和现状差异，未把预览数据、虚构状态或既有局部覆盖写成当前全局已实现能力；不把此文档任务扩展成 UI 改造。 |
| AC06 | 逐段核对中英文一致性，检查新旧相对链接，运行 git diff --check，审查改动范围并记录命令与结果。仅文档变更不新增测试或运行前端构建，必要限制据实记录。 |

## 5. 风险与交接

主要风险是把设计目标误写成现有代码能力，或将某个配置页的业务筛选细节泛化到所有模块。Development 应以本规格和共享主题 / 组件为事实依据，并在文档中区分未来采用与当前实现。若需要实现状态组件、修改基础弹窗样式或推广到已存在页面，应另定范围，不在本次实施。

本任务涉及前端设计指导，Development 遵循 frontend-ui；文档写入与角色交接遵循项目 workflow。Verification 在 fresh context 核对正文、双语、范围、链接和真实记录。QA 通过后仍由 Human Owner 作最终验收。

## 6. r1 范围批准

建议批准语：

> 批准 ARCH-FE-006 r1 和 AIIS::FUI-002 r1，按两份规格分别更新 frontend-js 双语设计指导和 frontend-ui 共享 skill 文档，并进行独立验证。

Human Owner 对精确 r1 的批准原话：

> 批准 ARCH-FE-006 r1 和 FUI-002 r1。按这版整理进 frontend-js 的双语 DESIGN，并同步到 frontend-ui skill。只动文档和 skill，不改业务代码。

批准前本规格的 SHA-256 为 4e4185b125f6b13e889d49de548fda3aefcc01843ea2b7bab1c0ddb9d93c2553。上述批准对 r1 的范围、验收和写入清单不作变更。交实际命名 Development 按本规格实施并记录自检与 developer_handoff，再由 fresh-context 命名 Verification 独立核验。范围批准不代表 QA 或 Human Owner 最终验收。
