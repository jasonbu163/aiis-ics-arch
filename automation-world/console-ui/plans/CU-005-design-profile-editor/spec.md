Task ID: CU-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved CU-005 r1 on 2026-10-16 (Asia/Shanghai); 命名 Development 可按本 Revision 的 allowlist 实施
Task Namespace: aiis-ics-arch
Classification: root
Capability: CU 有限样式参数编辑、本地草稿与公共 JSON 方案确定性生成 CSS
Owner: Console UI
Acceptance Chain Reference: CU-005 r1 / Human Owner 范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: CU-001; CU-002; CU-003; CU-004（背景及实现基线关联，不继承批准、状态或验收）
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-005：样式方案编辑与生成

## 1. 目标与依据

为 CU 现有“参数预览”入口增加有限样式编辑、即时预览和本地草稿；导出公共 JSON 样式方案，再由显式工程命令更新固定公共 JSON/CSS，供后续 DAA/SMA 独立接入。

Human Owner 于 2026-10-16（Asia/Shanghai）提出：

> 完成后再落 CU-005 spec，做样式参数编辑、本地草稿保存和公共 JSON 方案生成 CSS，供 DAA、SMA 引用。

本任务只处理 UI 配色、间距、圆角和表格密度，不处理样例业务数据 CRUD、PLC/SQLite 配置或拖拽低代码。该指示在草案创建时只授权草案，当时尚未获得精确 CU-005 r1 实施批准；Human Owner 于 2026-10-16 明确批准本 r1，当前交命名 Development 实施。

草案创建时已读取 CU-004 完整 bundle 及其14个实现/说明文件：当时 CU-004 r1 为 qa_passed、AC1–AC6 通过，Human Owner 最终验收 pending。本轮 Human Owner 于 2026-10-16（Asia/Shanghai）已明确验收 CU-004 r1，上述草案时点事实保留。工作台根布局与 body Teleport 弹层各有 `.aw-ui[data-aw-theme]` 作用域；基线当时未保存样式草稿或生成方案。CU 为 ESM，现有 TypeScript 支持 JSON 导入；Rust 只启动窗口，无文件/业务 IPC，package 无 `@tauri-apps/api`。草案阶段仅新建 spec；本次仅机械记录批准，未实施、测试、构建或启动。

## 2. 范围与需求

### R1. 固定首版字段与默认值

公共方案结构固定为 `schemaVersion: 1`、`themes.light`、`themes.dark` 和 `shared`，所有下列字段必填；不提供任意 token、CSS、脚本、路径或自定义字段。
`themes.light` / `themes.dark` 各有以下9个颜色字段，只接受 `#RRGGBB`，导出规范化为小写。默认值直接迁移当前主题定义：

| 颜色字段 | 映射 token | light 默认 | dark 默认 |
| --- | --- | --- | --- |
| background | `--agent-bg` | `#f3f6f8` | `#111820` |
| surface | `--agent-surface` | `#ffffff` | `#18222c` |
| surfaceMuted | `--agent-surface-muted` | `#edf3f7` | `#202c37` |
| text | `--agent-text` | `#17212b` | `#e6edf2` |
| textMuted | `--agent-text-muted` | `#5a6875` | `#a4b1bd` |
| border | `--agent-border` | `#cbd6de` | `#334452` |
| accent | `--agent-accent` | `#0891b2` | `#22d3ee` |
| accentStrong | `--agent-accent-strong` | `#0e7490` | `#67e8f9` |
| onAccent | `--agent-on-accent` | `#f7feff` | `#06212a` |

以下 `shared` 字段在明暗间共用；数值为有限整数，JSON 只保存数值，生成时添加 px：

| 字段 | 允许值 / 单位 | 默认 | 真实使用面 |
| --- | --- | --- | --- |
| cardPaddingPx | 12–32 / px | 24 | 公共卡片 body 内边距；compact 为 `max(8, 值-6)` |
| actionGapPx | 4–24 / px | 12 | `.aw-form-actions` 动作间距 |
| cardRadiusPx | 8–28 / px | 20 | `--agent-card-radius`；compact 为 `max(4, 值-4)`，包含现有弹窗 |
| controlRadiusPx | 4–20 / px | 14 | `--agent-control-radius`；small 为 `max(2, 值-4)`，用于现有操作按钮 |
| tableDensity | `standard` / `compact` | standard | `.aw-data-table` 单元格垂直 padding 分别为 8 / 4px |

- 默认方案保持当前视觉；不改字体、侧栏/顶栏布局、44px 顶栏工具控件或八组件 API。圆形/胶囊工具控件的固定圆角不纳入编辑。
- accent 还派生既有 accent-soft、accent-surface、sidebar-active-bg、card-border-hover、table-row-hover，保留当前 light/dark 各自透明度。Element Plus 映射引用这些 token，不另存一套颜色。
- 状态色、装饰玻璃表面/阴影、其余固定 token 和结构尺寸继续归固定 CSS；不变成隐藏编辑项。默认值只由公共 JSON 拥有，校验/映射模块拥有范围及派生规则，不能在 UI 再写一套默认值。

### R2. 参数编辑与作用域预览

- 在现有参数入口组合私有 `DesignProfileEditor.vue`，优先使用 Element Plus 的有限颜色/数值/选择控件；保留已有设计样例和壳层，不新增通用属性引擎。
- 明暗配色分别编辑，共享字段只保留一份。有效修改即时作用于现有卡片、按钮及 PageSamples 的表格、表单、弹窗/下拉；无效输入显示双语校验反馈，不能保存或导出。
- 通过同一纯映射结果给工作台根 `.aw-ui` 和 PageSamples 独立 Teleport 主题容器提供预览变量；切换宿主 theme 时两处同步。不得只改根，也不得向 html/body 写全局变量。
- 宿主 theme/locale 仍由现有控件管理；编辑另一套 palette 不隐式改变宿主选择。样例业务数据仍仅在内存中；文案与反馈进入对称 zh-CN/en-US locale。

### R3. CU 本地草稿与公共方案分离

- 首次打开从编译时公共默认 JSON 初始化，不自动应用草稿。提供显式“保存草稿”“恢复草稿”“重置为公共默认”及清楚反馈，草稿只使用 `cu.design-profile.draft.v1`。
- 保存前完整校验；恢复只读取该 key 并同样校验。缺失、损坏或不支持的草稿安全回到公共默认并提示；存储读写失败不伪称成功。重置只删除该草稿 key 并恢复默认，不清除全部 storage，不改变 `cu.theme` / `cu.locale`。
- 草稿仅属于当前 CU WebView/浏览器存储环境，不跨 origin 同步，DAA/SMA/consumer 不读取。保存草稿不修改公共 JSON/CSS，也不触发文件写入或发布。
- UI 导出校验后的规范 JSON，通过可复制文本或浏览器下载至少一种已有 Web 能力交给用户；明确“导出后仍需工程导入”。不为此增加原生文件命令、IPC、fs 插件权限或 GUI 源码编辑器。

### R4. 单一公共方案与受控生成

- `src/ui/styles/design-profile.json` 是一套公共默认方案的唯一人工维护源；`src/ui/styles/design-profile.generated.css` 是确定性派生产物，注明不可手改，不带时间戳/机器路径。
- `src/ui/design-profile.js` 是无文件/存储/应用副作用的纯校验、规范化及 token/CSS 映射逻辑，供浏览器和 Node 共同调用；配套 `.d.ts` 提供当前 TypeScript 所需声明，不复制校验规则，不新增依赖。
- `theme.css` 保留固定 token 与 Element Plus 映射，移走本方案拥有的默认/派生值；`styles/index.css` 按固定主题、生成方案、组件样式顺序引用。组件 CSS 真正消费间距/圆角/密度变量，不能只生成未使用变量，不能保留第二份手工可编辑默认值。
- 新增单一 Node 入口 `scripts/design-profile.mjs`，固定输出锚定自身 CU 工程，不受 cwd/输入文件中的路径影响；只接受下表模式，不接受任意输出路径。所有 schema 类型、版本、必填字段、未知字段、颜色、数值范围及枚举先完整校验，再生成全部目标内容。

| 命令（CU 目录） | 行为 |
| --- | --- |
| `pnpm design:profile` / `pnpm design:profile --help` | 只显示帮助，不读取默认输入、不写入 |
| `pnpm design:profile --import /absolute/path/profile.json` | 显式读取输入，校验/规范化后更新固定公共 JSON 与生成 CSS |
| `pnpm design:profile --generate` | 校验固定公共 JSON，只重新生成固定 CSS |
| `pnpm design:profile --check` | 只读校验公共 JSON，并比较期望 CSS 与当前文件；缺失/stale 返回非零并给出恢复命令 |

- 无效输入必须零目标写入，保持现有有效 JSON/CSS。I/O 失败返回非零、说明可能的不一致及恢复路径；采用必要的单文件安全替换，不建立跨文件事务框架或承诺两文件原子性。stale 时显式 `--generate` 恢复，公共 JSON 损坏时从本任务有效备份恢复后再生成。
- CU `pnpm build` 前置只读 `--check`，不偷偷生成、导入草稿或应用变更；不改变现有 dev/preview/native 启动命令。规范 JSON/CSS 使用固定字段/规则顺序和 LF，同输入重复生成字节一致。

### R5. 独立消费与说明

- 现有 consumer 源码原样通过公共样式出口消费生成 CSS，用其现有表格/表单/弹窗证明独立引用；不增加编辑器或草稿逻辑，不导入私有 workbench，也不增加公共组件出口。
- 更新 CU 与 consumer README pair，说明字段/单位/默认责任、预览/草稿/公共源的区别、导出→显式导入→生成/check 流程及故障恢复。
- DAA/SMA 本任务不接入、不改代码/依赖。后续独立接入公共样式后，各宿主以自身开发配置或重新构建同步；已安装桌面二进制需重构建及分发，运行不依赖 CU 在线，不承诺实时热更新。

## 3. 精确写入 allowlist

以下全部相对 `automation-world/console-ui/`，仅 Human Owner 批准精确 r1 后生效：

| 责任面 | 允许路径与限制 |
| --- | --- |
| 私有编辑器与预览 | 新增 `src/workbench/DesignProfileEditor.vue`；`src/workbench/Workbench.vue`，仅参数组合/草稿状态与根预览；`src/workbench/PageSamples.vue`，仅接收预览变量并同步弹层；`src/workbench/workbench.css`，仅编辑器布局 |
| CU 文案 | `src/locales/en-US/workbench.json`、`src/locales/zh-CN/workbench.json`，仅本任务对称文案及必要说明修正 |
| 公共方案与纯逻辑 | 新增 `src/ui/styles/design-profile.json`、`src/ui/styles/design-profile.generated.css`、`src/ui/design-profile.js`、`src/ui/design-profile.d.ts`，分别为默认源、派生 CSS 和共享校验/映射及声明 |
| 公共样式 | `src/ui/styles/theme.css`、`src/ui/styles/components.css`、`src/ui/styles/index.css`，仅 R1/R4 的 token 归属、真实绑定和新增 CSS 引用 |
| 命令 | 新增 `scripts/design-profile.mjs`；`package.json` 仅新增 `design:profile` script 及 build 的只读 check 前置，依赖不变 |
| 稳定说明 | `README.md`、`README.zh-CN.md`、`examples/source-consumer/README.md`、`examples/source-consumer/README.zh-CN.md`，仅 R5 教程及当前边界 |
| 本任务与索引 | 当前 spec 归 PM；批准后本目录 tasks 归 Development，developer_handoff 后 checklist 归 fresh-context Verification；`PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` 仅主协调机械同步本任务状态/链接/下一 gate |

除此以外不写入。八组件源码、`src/ui/index.ts`/`types.ts`、App/main、src/app README、consumer 源码/locale/package/config、依赖/锁文件、TypeScript/Vite、Rust/Tauri/capabilities/端口/生成 schema、根/AW 文档/CODE_INDEX、历史 bundles、其他 Agent/backend/frontend-js、真实配置与 Git refs 均禁写。确需扩大范围时先回 PM 新 Revision 并重新批准。

## 4. 验收与验证上限

| ID | 对应需求 | 最小可复核结果 |
| --- | --- | --- |
| AC1 | R1/R2 | 默认方案保持当前视觉、八组件 API 和 44px 顶栏；有限字段与范围符合合同，代表性配色/间距/圆角/密度修改确实影响预览，light/dark 分别保留值，根与弹窗/下拉同步 |
| AC2 | R2/R3 | 一轮聚焦观察验证有效编辑、无效值拒绝、导出 JSON、保存后刷新并显式恢复、重置及坏草稿回退；只触达版本化草稿 key，theme/locale 偏好及公共 JSON/CSS 不因草稿操作改变 |
| AC3 | R1/R4 | 一个有效临时方案可显式导入；一个非法方案被拒且两目标不变；帮助无读写，stale check 非零且不写，显式 generate 可恢复，同输入连续生成字节一致；预览和生成共用校验/映射 |
| AC4 | R4 | CU `pnpm build` 一次通过只读方案一致性检查、类型检查和 Vite 构建；最终公共默认/生成 CSS 一致，build 不读 CU 草稿或隐式修复文件 |
| AC5 | R2/R3 | 当前主机现有 `pnpm tauri dev` 原生启动一次，保留窗口/ready 日志；同轮浏览器可完成编辑/草稿及代表性明暗/中英、弹层观察，明确区别原生启动与浏览器交互证据 |
| AC6 | R4/R5 | CU 停止后 consumer `pnpm build` + `pnpm preview` 独立引用一次；既有公共入口包含生成 CSS，现有表格/表单/弹窗随宿主主题正确，consumer 不读 CU 草稿、不需 CU 在线 |
| AC7 | R1–R5/治理 | 精确增量限于 allowlist，JSON/固定 CSS/派生产物责任无重叠；CU 双语键、四 README 合同及相对链接一致，任务元数据和索引真实 |

AC2 验证方法说明：正常编辑、无效值拒绝、导出、保存后刷新并显式恢复、重置及主题弹层采用真实 UI 聚焦观察。若当前 UI 工具不提供存储注入能力，坏草稿与存储失败分支可补充使用当前真实组件 handler 在最小隔离 VM 中执行的证据；仅替换存储环境，保留实际校验、公共默认和回退/反馈路径，不复制重写 handler，不增加生产测试开关或写状态后门。仍须证明坏草稿回到公共默认并提示、存储失败不伪称成功，以及原有 key/偏好/公共文件隔离要求。tasks/checklist 必须分别注明浏览器观察与隔离执行的方法、真实源码来源和结果；Verification 独立核对补充证据与当前 handler 的对应关系，不将 VM 执行写成浏览器坏草稿观察。此为证据组合说明，R2/R3 与 AC2 的结果要求不变，不构成新的 Human Owner 批准或 QA verdict。

Development 写前保护拟改文件起点；验证用临时方案/坏草稿及恢复材料放 `/private/tmp`，保存原公共 JSON/CSS 和该 CU 草稿 key 后再验证，结束恢复，不覆盖既有或并发改动。临时公共方案恢复后再形成最终构建/引用证据；实际命令、退出码、环境、关键事实与恢复结果写入 tasks，不能只留临时路径。

fresh-context Verification 审阅精确 r1、tasks、当前源码/任务增量及上述证据，仅对疑点或缺失项复查，不因角色分离重复完整构建/启动。只关闭本任务创建的进程/tab；原生启动无法完成时如实记录阻塞。

不做全量回归、字段/主题组合矩阵、其他 Agent/现场验证、Cargo 全套、额外 native 包装、跨平台或长 GUI 轮询；不新增泛型测试框架。QA 通过仍待 Human Owner 最终验收。

## 5. 风险、回退与延后

- 手工 CSS 与 JSON 双事实源、预览与生成规则分叉、弹层遗漏变量是主要风险；用单一源、纯共享逻辑、只读一致性检查及代表性观察收敛，不建设配置平台。
- 本地存储可能损坏/不可用，颜色合法也可能降低对比度；提供上述回退/反馈，配色取舍交 Human Owner 审阅，不增加自动配色或全量无障碍审计。
- 回退只处理本任务实际增量及草稿 key，按写前有效副本恢复公共方案/样式，核对并发归属；不以 HEAD 全量归因、不整体 git restore CU，不把回退策略当当前执行授权。
- 延后 GUI 直接写公共源码、原生文件编辑器、任意 CSS/脚本、主题市场、多方案/云同步、低代码拖拽、业务数据保存、DAA/SMA 实际集成、npm/发布部署与 Git/GitHub 操作。

## 6. Handoff 与修订记录

PM 使用 aiis / project-governance。Development 与 Verification 按表面加载 frontend-ui（主题/Element Plus/工程规则）、i18n-workflow、desktop-tauri（既有启动路径）；新增源码头部说明按需 code-document-indexer，根索引禁写。Node 命令属于 CU 自身构建链，不迁入根 tools 或 backend/scripts，不加载无关后端/PLC/Rust runtime 实现规范。

Human Owner 于 **2026-10-16（Asia/Shanghai）**明确批准 **CU-005 r1**，本任务批准原话：

> 批准 CU-005 r1，按 spec 开始实施，只改 CU，其他 Agent 不动。验证能构建、能启动、能引用，以及编辑、草稿保存和 CSS 生成流程即可，不做全量回归。

下一 gate：命名 Development 创建 tasks，按已批准 r1 实施并交接 fresh-context 命名 Verification，最后 Human Owner 验收。主协调只机械同步 CU 双语索引。本 profile 为 contract_only，串行 handoff、完整 bundle 与 diff 审计是必要控制，不宣称平台 ACL、强制路由或完整团队激活；实质变化须新 Revision 并重新批准。

| 日期 | Revision | 记录 |
| --- | --- | --- |
| 2026-10-16 | r1 | PM 创建 draft；仅新 spec，未实施/测试/构建/启动，未创建 tasks/checklist；精确范围批准 pending，文档链接与索引由主协调检查 |
| 2026-10-16 | r1 | Human Owner 明确批准 CU-005 r1；仅机械记录批准与 Development handoff，r1 范围、allowlist、AC 和草稿历史保留，未实施或追加测试 |
| 2026-10-16 | r1 | PM 澄清 AC2 的真实 UI 与实际 handler 隔离异常分支证据边界；需求、验收结果、allowlist 和批准状态不变，未实施或运行验证 |

依据：[根 AGENTS](../../../../AGENTS.md)、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、[CU PLAN](../../PLAN.md)、[CU-004 完整 bundle 入口](../CU-004-page-design-samples/spec.md)。
