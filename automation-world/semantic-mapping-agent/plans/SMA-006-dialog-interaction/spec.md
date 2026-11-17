Task ID: SMA-006
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Human Owner 审阅 SMA-006 r1 弹窗交互首批范围与验收标准
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 弹窗首批问题 #7、#8 和 #9，编辑反馈、关闭防误操作与正文滚动
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-004
Related Task: SMA-005

# SMA-006 弹窗交互首批修正

## 1. 目标与依据

用户在目标 API、映射值规则、映射配置三个编辑框内可以看见并修正错误，误点遮罩不会丢失输入，阅读长内容时仍可看见标题和操作区。首批对应 **#7 报错在遮罩后**、**#8 遮罩关闭丢输入**和 **#9 长弹窗整框滚动**，基于 [SMA-004 r1 已验收配置流程](../SMA-004-local-configuration/checklist.md#owner-acceptance-r1) 与 [SMA-001 总规格](../SMA-001-cu-integration-and-scope-cleanup/spec.md)。

DAA 点位编辑把错误放在表单内，提交中约束关闭操作。离开编辑前的丢弃确认、上报确认的固定标题与操作区也可参照。SMA 继续使用自己的数据、表单和文案。 [DAA 点位编辑](../../../data-acquisition-agent/src/app/plc/views/points/index.vue) · [DAA 离开编辑确认](../../../data-acquisition-agent/src/App.vue) · [DAA 长确认框样式](../../../data-acquisition-agent/src/styles/app.css)

## 2. 首批范围

### R1 在发生错误的表单内反馈（#7）

- 三个编辑框的新增与编辑流程都在框内显示本次校验或保存失败。已知字段错误标出出错项，例如目标 API 的 body JSON、值规则的值数组或映射必填项。表单级错误和配置版本冲突放在框内可见区域，说明如何修正，遇版本冲突提示先核对最新配置再重试。错误通过键盘和辅助技术可感知。
- 校验、预检、IPC 保存失败或版本冲突后保留输入与本次编辑上下文，窗口不关闭。带旧版本的保存不得改写较新的配置。反馈只对应本次表单与提交，重开或切换编辑项时清除旧的提交反馈。提交成功后沿用现有关闭与刷新行为。

### R2 防止误关和重复提交（#8）

- 三个编辑框均忽略遮罩点击。刚打开或修改后回到初始值的表单可通过取消、关闭键或 Esc 直接关闭。已有改动时，这三个动作进入应用内的丢弃确认。默认「继续编辑」保留原输入、当前项及表单焦点。明确选择「丢弃」才关闭，取消或丢弃的配置写入次数为 0。
- 提交等待中禁用重复提交及取消、关闭键和 Esc。提交失败后恢复可操作性，保留表单与本次错误。确认框在当前主题弹层内，Esc 或返回继续编辑只结束确认，关闭编辑框后焦点回到打开它的按钮。

### R3 长内容仅滚动正文（#9）

标题、可用的关闭键和底部操作区保持可见。弹窗正文独立纵向滚动，表格和长内容在自身容器内处理溢出。宽度随内容选择，短确认窄于普通表单，有多列的配置、材料与批量预览可用较宽的版式。各类弹窗宽度受视口约束并保留两侧空隙。窗口收窄时标题、长文案和按钮可换行，页面和弹窗框体均不出现横向滚动。

| 现有 `ElDialog` 形态 | 首批处理 |
| --- | --- |
| 目标 API 编辑，含新增 | 框内错误与关闭规则。多列表单按内容分区，正文滚动 |
| 目标 API 删除，含批量 | 短确认布局和现有动作回归 |
| API 材料选择 | 宽表局部横滚，主操作区始终可见 |
| 映射值规则编辑，含新增及已选来源编辑 | 框内错误与关闭规则。普通表单正文滚动 |
| 值规则草稿移除 | 短确认布局和现有动作回归 |
| 映射配置编辑，含新增及草稿编辑 | 框内错误与关闭规则。参数表与预览留在正文内 |
| 批量操作 | 核对目标 API、映射值规则和映射配置三个入口。长清单留在正文，已有取消与可用的应用操作在底部 |

## 3. 复用与写入边界

采用 SMA 现有 Element Plus `ElDialog`、`#sma-overlays` 主题作用域和 CU `ConsoleActionButton`、现有主题变量及操作行样式。弹窗结构、业务校验反馈和关闭策略由 SMA 维护。后续 Development 与 Verification 按 `frontend-ui`、`i18n-workflow` 执行。 [SMA 主题容器](../../src/App.vue) · [CU 公共出口](../../../console-ui/src/ui/index.ts)

| 路径相对 SMA | 后续产品写入范围 |
| --- | --- |
| `src/app/twin-facts/components/{TargetApiConfigurationPanel,MappingValueRulesPanel,MappingConfigurationsPanel,MappingBatchOperationsDialog,TwinJsonContractPanel}.vue`、`src/app/twin-facts/components/ConfigurationEditorDialog.vue`（如需复用三个编辑框外壳） | 弹窗装配、操作及反馈。`MappingConfigurationsPanel.vue` 只改弹窗，列表运行状态归 SMA-005 |
| `src/app/twin-facts/store/{targetApiConfiguration,mappingValueRules,mappingConfigurations}.ts` | 按需明确当前编辑器的保存结果、错误归属和提交中状态。沿用资源校验、版本与持久化合同 |
| `src/app/styles/{shell,responsive}.css`、`src/app/twin-facts/locales/{zh-CN,en-US}.json`、`tests/local-configuration.test.mjs`、`tests/dialog-interaction.test.mjs` | 弹层局部样式、对称文案与定向回归 |

缩小样式影响面，页面、CU 公共源码、DAA、配置 API 和 Rust 持久化按现有实现提供契约。批量操作、删除、恢复和预览保留其业务语义。既有列表的列宽拖拽和重置继续可用。SMA-005 与本任务可独立批准，建议先接好页面变更再编辑重叠文件，避免合并时相互覆盖。

## 4. 验收标准

| ID | 操作与通过标准 |
| --- | --- |
| AC01 | 分别在目标 API 输入非法 body JSON、在值规则输入非法数组、在映射漏掉必填项再保存。错误在对应框内可见且可定位，输入仍在。用另一写入先推进版本，再提交已打开表单，冲突提示可见，当前输入和较新配置都保留。打开另一项时无旧错误。合规修改只提交一次，成功后关闭并更新列表。 |
| AC02 | 在三个编辑框分别试遮罩、取消、关闭键和 Esc。遮罩不关闭。无改动可直接关闭。有改动时确认会阻止关闭，继续编辑保留输入和焦点，明确丢弃后重新打开显示已保存值或新增默认内容。对未保存的新建及已有条目分别检查零写入。 |
| AC03 | 延迟一次已有保存命令的返回，重复点击或按回车只发出一次提交。等待中退出操作不能关闭表单。令此提交失败后，原输入、错误和可操作控件仍可见。通过键盘关闭编辑框后，焦点正确返回到触发按钮。 |
| AC04 | 在 `1280×800` 和 `1024×720` 实际检查上表七类，批量操作三个入口均可打开。用至少 10 条参数或多行 JSON、宽表及长中文/英文内容，滚动正文至底部，观察标题、可用的关闭键和底部动作的位置。横向滚动限于宽表或代码区域，表底和操作可达。确认与材料选择的既有行为用隔离数据复核。 |
| AC05 | 明、暗与中文、英文下检查可读性、按钮层级、提示与焦点，至少在一个正常 Tauri 窗口复现带参数的长编辑框和有改动时的关闭流程。弹窗打开、关闭和布局切换均不改变配置合同或投递门禁。 |

后续使用可丢弃 SMA profile、合成配置和受控保存响应执行。候选以 `pnpm check`、`pnpm test`、`pnpm build`、差异与链接检查交接。窗口尺寸以 [Tauri 配置](../../src-tauri/tauri.conf.json) 为准。

## 5. 后续与交接

- 第二批 **#10 统一删除及恢复确认**与 **#12 结构化预览**。先保留现有删除确认和整包恢复步骤，页内 OpenAPI、恢复及已保存映射预览不迁入弹窗。现有批量弹窗只改本批布局，分组内容留待 #12。第三批 **#11 材料选择筛选**沿用材料页现有思路另定范围。
- 主要回归风险是异步反馈串到其他表单、关闭时误丢输入或页脚移动后破坏原确认动作。失败候选由 Development 修复或撤回本次前端差异。真实 profile、发布和 GET→POST 交付另列范围。
- 2026-11-14（Asia/Shanghai）形成 r1 草案，交 Human Owner 审阅。范围批准后进入 Development，交接后由独立 Verification 执行第 4 节。
