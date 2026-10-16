Task ID: CU-006
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved CU-006 r1 on 2026-10-16 (Asia/Shanghai); 命名 Development 可按本 Revision 的7文件 allowlist 实施
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: CU 参数页可视颜色编辑与同屏实时样式预览
Owner: Console UI
Acceptance Chain Reference: CU-006 r1 / Human Owner 范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: CU-005; CU-004（实现基线关联，不继承批准、状态或验收）
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-006：可视颜色编辑与同屏预览

## 1. 目标与依据

让 CU 参数页直接表达“左边调参数、右边看效果”：颜色有色块、拾色器和 HEX 输入，编辑模式与预览模式一致，滚动调参时仍能看到真实样例及即时反馈。

Human Owner 于 2026-10-16（Asia/Shanghai）要求：

> 可以，补上色块、拾色器和同屏实时预览，左边调参数、右边看效果。先落 CU-006 spec，只改 CU，其他 Agent 不动，验证能构建、能启动和编辑预览流程即可，不做全量回归。

草案创建时上述指示只授权起草，当时尚未获得精确 r1 实施批准。Human Owner 于 2026-10-16（Asia/Shanghai）明确批准 CU-006 r1，当前交命名 Development 实施；本次仅机械记录批准。CU-005 当前为 qa_passed、AC1–AC7 通过，Human Owner 最终验收仍 pending，本任务不代为接受 CU-005。
只读源码基线：DesignProfileEditor 同时列出18个 HEX 输入，样例需要切换导航；可编辑非当前宿主 palette，任一非法值保留最近有效方案而错误位于底部。Workbench 已有单一 theme、有效方案及 previewVariables，PageSamples 已接收 theme/previewVariables 并同步 Teleport；可直接复用，无需修改公共层或新增预览组件。

## 2. 范围与需求

### R1. 参数页左右布局

- 只重排现有 parameters 入口：桌面左栏为样式编辑，右栏为常驻实时预览。已有标题/色调/compact 小样例收为次级区域，保留其事件；其他导航入口和整体壳层不重做。
- 右栏组合既有参数卡片和私有 PageSamples，直接使用公共卡片、按钮及原生 Element Plus 表格/表单/弹窗。通过参数页私有 CSS 将 PageSamples 在预览栏内排为单列，不修改其源码或复制样例逻辑。
- 桌面向下调参时预览仍可见，右栏超过可视高度时允许区内滚动，并保留可见模式/有效性提示；不得被固定顶栏遮挡。可用宽度不足时自然上下排列，解除桌面粘性/高度限制，输入和预览不被挤成不可操作窄列。
- 所有展示继续标识设计样例，业务数据仅留在原内存预览，不新增业务功能。

### R2. 颜色控件与明确的编辑模式

- 参数区明确显示“正在编辑/预览：日间 / 夜间”，只展开当前模式的9个颜色字段，共享间距/圆角/密度仍只有一份。提供显式日间/夜间切换，直接更新 Workbench 现有宿主 theme；与顶栏切换使用同一状态和既有 `cu.theme` 持久化，不新增独立编辑主题。
- 两套 palette 的值分别保留；用户显式切换模式才更换编辑和预览 palette，输入颜色不自动切主题。locale 仍归宿主，新增说明、控件标签、状态及反馈均走对称双语资源。
- 每个颜色字段提供色块、Element Plus ElColorPicker 和现有 HEX 输入，三者绑定同一方案字段；仅六位 `#RRGGBB`，不启用 alpha。继续使用 CU-005 的 PALETTE_FIELDS、normalizeProfile、公共默认和映射，不扩 schema、字段、取值或依赖，不另存默认值。
- 有效编辑立即在右栏生效，无需保存、导出或重启。暂时非法的 HEX 保留最近有效方案，字段附近显示具体反馈，当前可见处提示“修改尚未应用/正在展示最近有效方案”并指出相关模式/字段；保存/导出保持禁用，修正后恢复即时预览。反馈不得只藏在长表单底部。

### R3. 真实样例及弹层作用域

- 根布局、右侧预览和 body Teleport 弹层使用同一最近有效 profile 与当前 theme；不建立另一套假样式，不向 html/body 写全局变量。
- 样例应能实际看到配色、卡片/按钮圆角、卡片内边距、动作间距和表格密度；保留原编辑弹窗/下拉用途。拾色器 popup 必须继承当前宿主主题及有效变量，避免被 ConsoleCard overflow 或预览滚动容器裁剪；具体最小挂载方式由 Development 按现有 Element Plus 能力确定。
- 颜色字段附简短用途说明。特别说明 surface 作用于 Element Plus 控件、表格基础表面和弹层，surfaceMuted 用于浅表面/工具区，强调颜色用于按钮/高亮；既有卡片装饰背景、玻璃和阴影仍固定。不把 surface 偷绑到卡片背景，也不修改公共主题来制造“全部表面都跟随”的效果。
- 八公共组件 API、侧栏、顶栏整体及44px工具控件保持；所有样式调整限于参数页私有布局、颜色编辑行和本任务拾色弹层范围。

### R4. 保留草稿与生成边界

- 保留 CU-005 的显式 save/restore/reset/export 与事件和反馈，不新增存储 key、不自动恢复草稿，不改变 `cu.theme` / `cu.locale` 的宿主归属。
- 操作区和反馈清楚可达；持续说明“即时预览无需保存，草稿不是公共发布”。无效值禁用原因在当前编辑上下文可见。
- 公共 JSON 唯一源、纯校验/映射、生成 CSS 和 Node CLI 流程保持原合同；GUI 不改公共文件，不新增原生文件/IPC能力。CU README pair 仅补充新的编辑方式、模式关系、预览用途和草稿边界。

## 3. 精确写入 allowlist

以下相对 `automation-world/console-ui/`，仅 Human Owner 批准精确 r1 后生效；实施/说明范围合计7个文件：

| 责任面 | 允许路径与限制 |
| --- | --- |
| 参数页组合 | `src/workbench/Workbench.vue`，仅左右栏、现有样例复用、单一 theme 事件及有效方案传递 |
| 可视编辑器 | `src/workbench/DesignProfileEditor.vue`，仅色块/ElColorPicker/HEX、当前 palette、就近反馈及既有草稿操作区重排 |
| 私有样式 | `src/workbench/workbench.css`，仅参数页响应式/滚动布局、颜色编辑行和拾色弹层的局部样式 |
| CU 文案 | `src/locales/en-US/workbench.json`、`src/locales/zh-CN/workbench.json`，仅本任务对称文案及必要既有说明修正 |
| CU 说明 | `README.md`、`README.zh-CN.md`，仅新的使用方式及边界 |
| 本任务文档 | 当前 spec 归 PM；批准后本目录 tasks 归 Development；developer_handoff 后 checklist 归 fresh-context Verification |
| CU 机械索引 | `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`，仅主协调同步本任务真实状态/链接/下一 gate |

除此以外不写入。PageSamples 源码、新 DesignProfilePreview 文件、公共 src/ui 组件/JS/声明/schema/默认 JSON/generated CSS/样式出口、CLI、package/依赖/锁/Vite/TypeScript、Rust/Tauri/main/App/端口/生成文件、consumer 全部文件、根/AW 文档/CODE_INDEX、历史任务 bundles、其他 Agent/backend/frontend-js、真实配置及 Git refs 均不在范围。确有必要扩大时先回 PM 新 Revision 并重新批准。

## 4. 验收与验证上限

| ID | 对应需求 | 最小可复核结果 |
| --- | --- | --- |
| AC1 | R1/R2 | 同轮真实 UI 可见左编辑/右样例；代表性色块、拾色器与 HEX 值一致，合法颜色立即影响真实预览，不需保存/导出/重启 |
| AC2 | R2/R3 | 显式切日间/夜间后编辑模式与预览一致、两 palette 值分别保留；根/预览/Teleport 同源；代表性查看一个拾色器 popup 和样例弹窗，主题正确且无裁剪，不做逐字段弹层矩阵 |
| AC3 | R2–R4 | 间距、圆角、表格密度各一项代表性修改可见；一个非法 HEX 有就近和当前可见反馈，保留最近有效样式并禁用保存/导出，修正后恢复；一次正常保存/恢复确认重排未丢事件，不重测既有草稿异常流程 |
| AC4 | R1 | 一次桌面滚动观察确认调参时右侧预览仍可见；一个窄窗观察确认上下排列、输入/按钮/样例可用，无需尺寸矩阵 |
| AC5 | R1–R4 | CU `pnpm build` 通过现有只读 check、类型和 Vite 构建；当前主机 `pnpm tauri dev` 原生启动一次并记录 window/ready，AC1–AC4 可用同次服务的浏览器观察，明确区分原生启动与浏览器交互证据 |
| AC6 | R1–R4/治理 | 精确增量限于7文件及角色文档/机械索引；公共方案/生成/组件与其他工程未变，CU locale 对称、README pair 合同/链接一致，任务状态诚实 |

Development 保护拟改文件起点和本轮改动的 UI 偏好/草稿恢复依据，结束恢复，不覆盖不明草稿或并发工作，不以 HEAD 全量差异归因。实际命令、退出码、关键观察/少量截图及限制写入 tasks；临时材料优先 `/private/tmp`，只关闭本任务进程/tab。
fresh-context Verification 独立审阅精确 r1、任务增量和真实输出/截图，仅对疑点或缺失复查，不重复完整构建/启动/编辑流程。QA 通过后仍待 Human Owner 最终验收。

不追加 consumer 构建/独立引用、CU-005 CLI或草稿异常/坏稿VM全套、字段/主题矩阵、全量回归、Cargo/native包装/跨平台、长GUI轮询、其他Agent或现场验证。当前 PM 不运行上述应用验证。

## 5. 风险、恢复与 handoff

- 主要风险为粘性布局与 overflow 裁剪、编辑模式误导、非法输入反馈不明显；以参数页局部布局、单一 host theme、同源有效方案及代表性观察收敛，不改变公共设计合同。
- 回退仅按保护起点撤销本任务7文件增量，恢复原参数页组合；先核对并发归属，不整体 git restore CU。回退方案不提供当前执行回退授权。
- 排除新方案字段/默认色、开放固定玻璃/阴影编辑、公共组件重做、低代码/主题市场、业务数据保存、DAA/SMA接入、原生文件编辑、发布部署和 Git/GitHub 写入；这些后续另立范围。

PM 使用 aiis / project-governance；技术实现与验证交 frontend-ui、i18n-workflow、desktop-tauri（既有启动路径）对应角色，源码说明遵循现有风格。

Human Owner 于 **2026-10-16（Asia/Shanghai）**明确批准 **CU-006 r1**，原话：

> 可以，批准 CU-006 r1，按 spec 开始实施。只改 CU，其他 Agent 不动，验证能构建、能启动和编辑预览流程即可，不做全量回归。

下一 gate 为命名 Development 创建 tasks，按已批准 r1 实施并交接 fresh-context Verification，最后 Human Owner 最终验收。主协调仅同步 CU 四索引，不代为接受 CU-005。本 profile 为 contract_only，完整 bundle、串行交接及 diff 审计是必要控制，不宣称平台 ACL或强制路由。

| 日期 | Revision | 记录 |
| --- | --- | --- |
| 2026-10-16 | r1 | PM 创建 draft；仅新 spec，未实施/构建/启动/浏览器验证，未创建 tasks/checklist；精确范围批准 pending |
| 2026-10-16 | r1 | Human Owner 明确批准 CU-006 r1；仅机械记录批准与 Development handoff，r1 范围、7文件 allowlist、AC 和草稿历史保留，未实施或追加测试 |

依据：[根 AGENTS](../../../../AGENTS.md)、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、[CU PLAN](../../PLAN.md)、[CU-005 完整 bundle 入口](../CU-005-design-profile-editor/spec.md)。
