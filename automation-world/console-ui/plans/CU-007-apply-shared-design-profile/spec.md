Task ID: CU-007
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact CU-007 r1 on 2026-10-16 (Asia/Shanghai); PM -> Development for approved implementation and bounded verification
Task Namespace: aiis-ics-arch
Classification: root
Capability: Apply the current CU design profile to fixed shared source files in local source-development mode
Owner: Console UI
Acceptance Chain Reference: CU-007 r1 / Human Owner scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
Related Task: CU-005; CU-006 (independent capability; no inherited approval or acceptance)
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-007 r1：应用到公共样式

## 1. 请求与基线

2026-10-16（Asia/Shanghai），Human Owner 原话：

> 好的，把这部分做完，是不是就可以真正去做一个agent了？

“这部分”承接已讨论的“应用到公共样式”入口：在 CU 调好参数后，通过一次明确点击更新唯一公共 JSON 并生成共享 CSS。草案创建时只授权形成草案，当时尚未批准精确 r1 实施；不据此创建 Agent 业务任务。后续精确批准见历史。

CU-001–006 已由 Human Owner 验收。[CU-005](../CU-005-design-profile-editor/spec.md) 提供唯一公共 JSON、纯校验/映射、CLI 和本地草稿；[CU-006](../CU-006-live-design-preview/spec.md) 提供同屏编辑预览。完整关联 bundle 的原批准、实施、独立 QA 与最终接受历史保持原位。既有 DIRECT 密度下拉宽度修复也属于受保护基线。

当前 GUI 仅编辑内存、保存 CU 草稿及导出文本；CLI 才能写公共源。Vite 开发服务为 15193、preview 为 14193，Rust 仅启动窗口。**本任务首版仅支持本机源码开发模式（`pnpm dev` / `pnpm tauri dev`）；preview 与已打包应用没有源码写入通道。**

## 2. 编号需求

- **R1 — 明确应用动作。** 参数编辑器新增“应用到公共样式”，提交点击时的完整有效方案（light、dark、shared），沿用既有唯一 `normalizeProfile`、`profileJSON`、`profileCSS`。无效编辑禁用应用；应用中防重复提交并保持提交快照，成功/失败清楚反馈。不自动应用、不自动保存草稿；保存/恢复/重置/导出及 `cu.theme`、`cu.locale` 归属不变。
- **R2 — 开发模式边界。** 通过 CU 私有 Vite `configureServer` 中间件提供通道，不新增服务、端口、Rust 命令、原生文件权限或依赖。仅本机开发通道可用时启用按钮；production/preview 不注册端点，界面禁用并说明可导出 JSON 后显式 CLI 导入。开发模式限制及修改公共源码的含义必须在按钮附近显著说明。
- **R3 — 固定公共源与共用 I/O。** 从既有 CLI 抽出 CU 私有 Node helper；GUI 中间件和 CLI 共用固定目标读取、完整校验/生成及单文件临时替换逻辑。目标只为本 CU `src/ui/styles/design-profile.json` 与 `design-profile.generated.css`，由 helper 自身位置锚定，不接受客户端输出路径、外部工程目录、任意 CSS/脚本或其他文件。JSON 仍是唯一人工维护源，CSS 仍由其确定性派生；原公共样式出口不变。
- **R4 — 保持 CLI 合同。** 裸入口/`--help` 仍只帮助、无默认读写；`--import /absolute/path/profile.json`、`--generate`、`--check` 语义保留。`pnpm build` 继续只读 check，不隐式生成或应用草稿。Node helper 无导入时 I/O；仅开发插件的 JS 配套最小 `.d.ts` 供现有 Vite TS 配置导入，不扩大 tsconfig 或依赖。
- **R5 — 限定请求保护。** 私有端点固定为 `/__cu/design-profile`，在 Vite 通用 CORS/static 中间件之前处理且不向后透传该端点的拒绝请求：
  - 仅接受实际 loopback socket 来路（包括 IPv4 映射形式），不信任转发头；Host 只允许本地 `localhost` / `127.0.0.1` / `[::1]` 与既有 15193。
  - 仅 GET 获取当前两文件版本及本次开发进程随机会话 token，POST 显式应用；不开放跨域 CORS，拒绝 OPTIONS/其他方法。GET 要求自定义同源请求头，若带 Origin 则须匹配；POST 要求匹配本地同源 Origin 及会话 token。拒绝外部或 null Origin，不把 token 写入磁盘、文档或日志。
  - POST 仅 `application/json`，按实际接收字节限制为 64 KiB，body 只含 `profile`、`expectedRevision`。先完整解析、校验并生成 JSON/CSS，再触达目标写入；请求保护或 schema 失败均零目标写入。
- **R6 — 冲突与 HMR。** 客户端首次建立通道时记录两公共文件的内容版本，应用时提交该 `expectedRevision`；写入前重新核对，不在点击时无条件刷新版本以掩盖外部更新。版本不符返回冲突，提示先导出当前编辑、刷新核对后重试，不盲重试或静默覆盖。开发进程内串行执行写操作；私有客户端模块在内存保留应用 pending/结果及必要页面恢复状态，使 JSON/CSS 引起的本次 HMR 不吞掉成功反馈或把参数页切走。刷新/重新启动使用更新后的公共默认；不增加 storage key 或持久回执。
- **R7 — 诚实失败与共享边界。** 两目标分别安全替换，可在目标旁使用本次唯一临时文件并清理；不承诺两文件事务。I/O 部分失败必须报失败及恢复步骤：检查两目标，必要时恢复有效 JSON，再执行 `--generate` / `--check` 并刷新。CU 根、真实样例及 Teleport 继续使用同一有效方案与宿主主题。消费者继续通过既有公共 CSS 出口消费；各宿主以后自行同步源码、刷新开发态或重新构建，已安装二进制需重构建分发，不依赖 CU 在线。本任务不接入 DAA/SMA。

## 3. 精确实现 allowlist

以下路径均相对 `automation-world/console-ui/`；仅批准后由 Development 按职责实施，不要求为凑清单制造修改。

| 路径 | 唯一允许用途 |
| --- | --- |
| `vite.config.ts` | 注册私有开发插件；保留既有 Vue、host、端口及构建配置 |
| `scripts/design-profile.mjs` | 薄 CLI 入口复用固定 I/O helper，保留原命令合同 |
| `scripts/shared-design-profile.js`（新增） | 固定公共目标、版本核对、校验/生成及替换的 Node helper |
| `scripts/shared-design-profile-dev.js`（新增） | 开发中间件、请求保护、会话及进程内写入串行化 |
| `scripts/shared-design-profile-dev.d.ts`（新增） | 仅声明 Vite 插件工厂类型，适配现有 TS 配置 |
| `src/workbench/useSharedDesignProfile.ts`（新增） | CU 私有通道调用、pending/结果和必要 HMR 内存状态 |
| `src/workbench/Workbench.vue` | 仅接线应用状态与参数页 HMR 保持，不重排壳层 |
| `src/workbench/DesignProfileEditor.vue` | 新应用按钮、模式限制、校验/提交/结果反馈；保留原操作 |
| `src/locales/en-US/workbench.json` | 新增操作与限制/失败/冲突/恢复的英文文案 |
| `src/locales/zh-CN/workbench.json` | 对称中文键与文案 |
| `README.md` | 新操作、开发模式、helper 职责、恢复及宿主构建责任 |
| `README.zh-CN.md` | 对称中文使用与结构说明 |
| `src/ui/styles/design-profile.json` | 固定应用/验证目标；不借本任务重新设计默认视觉 |
| `src/ui/styles/design-profile.generated.css` | 上项确定性派生目标，不手工维护 |

本轮 PM 只写本 `spec.md`。批准后 Development 自建本 bundle 的 `tasks.md`，fresh-context Verification 自建 `checklist.md`，不预建空证据。主协调仅机械同步 CU 的 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`；它们不属于 Development 实现面。

CU 无本地 CODE_INDEX，新增私有 helper 的职责/入口精确登记于 README pair；不新建空索引或扩改未收 CU 子结构的根 CODE_INDEX。禁止修改 `workbench.css`（含既有 150px 修复）、PageSamples、公共八组件/API、`src/ui/index.ts`/types、纯 schema/映射、其他公共样式、main/App、package/锁文件、tsconfig、Rust/Tauri、端口、consumer、根/AW 文档、历史 bundle、其他 Agent/backend/frontend-js、真实配置或 Git refs。

## 4. 有限验收与证据

| ID | 验收标准 |
| --- | --- |
| **AC1 / R1–R7** | 精确增量符合 allowlist；源码审阅确认共用纯规则/固定 I/O、开发专用端点与保护、版本冲突拒绝、CLI 原合同及 build 只读 check。两语言键/文档一致，公共 schema/API/默认视觉及 DIRECT 修复保持。 |
| **AC2 / R3–R4** | 最终 CU 执行一次 `pnpm build` 成功，含现有生成一致性检查、类型检查及 Vite 构建；不追加 consumer 独立构建。 |
| **AC3 / R1–R3、R6–R7** | 当前主机一次 `pnpm tauri dev` 的 window-created/ready 证据；同次服务一次代表性真实 GUI 编辑→明确应用，两个固定文件实际变为规范 JSON/匹配 CSS，同屏效果保留、成功反馈跨本次 HMR 可见，刷新采用更新后的公共默认。原生启动日志与浏览器交互分开记录，不冒称原生 WebView 内交互。 |
| **AC4 / R5–R6** | 一条 schema 非法或保护不通过的请求被拒绝，前后两目标内容摘要相同；其余保护及冲突分支定向源码审阅即可，不扩为攻击/并发矩阵。 |
| **AC5 / 治理与恢复** | 验证前把两公共文件备份到 `/private/tmp` 并记录本轮输出摘要；验证后仅在当前文件仍属于本轮输出时恢复原默认并保持 JSON/CSS 一致。保留原草稿/偏好和其他未提交修改；遇并发更改停止覆盖并如实交接。Development 记录真实命令/退出码/有限观察，独立 QA 审阅精确 diff、输出与截图，仅疑点或缺失才复查。 |

验证上限为能构建、能启动和一次公共应用流程，加一条拒绝请求；CLI 抽取主要核对合同及 build check，不重复 CU-005 CLI/草稿异常矩阵。无需全量回归、全主题字段/组合矩阵、consumer 全套、Cargo/native 打包、跨平台、长 GUI 轮询、其他 Agent、数据库/PLC/现场或发布部署。PM 本轮不执行上述应用验证。

## 5. 风险、角色与下一 gate

- 开发端口仍绑定 `0.0.0.0`，私有写入口必须先完成 R5 保护才可启用；不可将“仅开发态”当作无保护文件写入授权。preview/打包形态禁用行为由构建分支与插件注册边界审阅，不追加打包验证。
- 乐观版本核对与进程内串行化不等于跨进程锁；本机 CLI/手工公共文件编辑应串行，冲突先保留编辑并刷新核对。双文件 I/O 部分失败使用明确恢复命令，不建设事务或权限平台。
- Development 写前保护当前 dirty/untracked 基线，按本轮起点记录增量；回退仅撤销本任务代码并按归属恢复有效公共文件，禁止从 HEAD 全量恢复或覆盖并发修改。
- 适用 `aiis` / `project-governance`；Development/Verification 按改动使用 `frontend-ui`（既有界面/主题优先）、`i18n-workflow`、`desktop-tauri`（既有启动与开发/打包边界），新增关键源码遵循 `code-document-indexer` 的文件说明要求而不扩大索引范围。无需 Rust runtime、后端或 PLC skill。
- 角色合同为 `contract_only`：PM 只定义本 spec；精确 r1 获 Human Owner 范围批准后才交 Development；随后 fresh-context QA / Verification，最后由 Human Owner 验收。实质范围/allowlist/AC/风险变化回 PM 新 Revision，不推断 ACL、强制路由或团队运行状态。
- 排除安装版任意项目目录写入、原生文件管理器、自动发布/云同步、主题市场、schema 新字段、公共组件重构、Agent 业务/DAA/SMA 接入及其他 Agent 工作；后续 CU 随实际 Agent 需求另行演进。

**当前交接：Development 按已批准 CU-007 r1 创建 tasks.md、实施并完成上述有限验证；下一 gate 为 developer_handoff 后的 fresh-context QA / Verification，最终接受仍由 Human Owner 决定。**

## 6. 历史

- 2026-10-16（Asia/Shanghai）：PM 基于当前已验收 CU-005/006、现有 CLI/Vite/编辑器事实创建 r1 draft；本轮仅文档草案，不把方向同意当作精确实施批准。未创建 tasks/checklist，未构建、启动或操作浏览器。
- 2026-10-16（Asia/Shanghai）：Human Owner 明确批准精确 CU-007 r1；PM 仅机械记录 owner_approved 并交 Development，r1 范围、allowlist、AC 与风险不变，未追加测试。批准原话：

  > 可以，批准 CU-007 r1，按 spec 开始实施。只改 CU，其他 Agent 不动，先支持源码开发模式。验证能构建、能启动和编辑后应用到公共样式的流程即可，不做全量回归。
