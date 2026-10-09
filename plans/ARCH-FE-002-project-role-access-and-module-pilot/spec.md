Task ID: ARCH-FE-002
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已直接授权 r4 恢复既有品牌能力并将宿主机权限收敛到当前模块测试；Development 按 r4 allowlist 实施，保留 r2/r3 QA 历史，developer_handoff 后 fresh-context Verification 复核 r4

Task Namespace: aiis-ics-arch
Classification: root
Capability: 项目构建期的 supervisor/operator 页面权限配置与首批模块接入验证
Owner: frontend-js Core 模块框架
Related Task: ARCH-FE-001
Depends On: ARCH-FE-001 当前已实现的 Registry 合同；本次 Owner 批准解除 002 启动 gate，001 final acceptance 独立待记录
Acceptance Chain Reference: ARCH-FE-002 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Execution Mode: agent_team_same_session
Created: 2026-09-28
Updated: 2026-10-08

# r4 当前批准范围：品牌功能恢复与当前模块测试配置

Human Owner 指出旧前端 Logo 配置、对齐与三段光晕能力尚未恢复，并明确要求“这些功能要补充
回来的”。本 r4 仅恢复冻结 JavaScript 旧版的既有通用能力，不设计新的品牌系统。另已明确授权：
“意思...其他模块没有被移入...已经有保留旧的配置...帮我把env调整为当前有的模块页面来测试可以吗？”
该决定允许收敛当前宿主机两角色授权；旧 JSON 已在 README 保留，严格 unknown-page 校验不改。
本节为当前实施权威；下文 r2/r3 范围、证据和批准是历史参考，不扩大 r4 allowlist。r2/r3 QA
记录保留，不自动成为 r4 verdict；Execution Mode 沿用 `agent_team_same_session`。

## R4-BRAND-001：恢复冻结版本的通用品牌配置

- 来源固定 `/Users/jason/Desktop/DreamCode/vibe-l2-front-end/frontend-next-js/src/config/brand.js`
  和 `src/components/shell/BrandLogo.vue`。只移植通用逻辑，现有登录页/MainLayout 消费者保持当前
  结构，通过现有 BrandLogo 入口恢复功能，不重写 UI 或 auth。
- 消费五项已有 env：`VITE_BRAND_LOGO_FILE`、`VITE_BRAND_LOGO_ALIGN`、
  `VITE_BRAND_GLOW_LEFT`、`VITE_BRAND_GLOW_CENTER`、`VITE_BRAND_GLOW_RIGHT`。
- 只从已打包 `src/assets/brand/*` glob 按文件名解析 Logo；拒绝带 `/`、反斜杠或路径穿越的
  值，不允许任意 URL/绝对路径。缺失、无效或不存在文件回退中性 `demo-organization-logo.svg`。
  可迁入审核通过的旧通用 demo SVG；禁止迁入 `2020-logo.png` 等客户资产或客户身份。
  旧 SVG 如仅含 NEXO 通用 demo 身份可作为公共 fallback；img alt 沿用 i18n `common.systemTitle`。
  README 明确配置的文件必须在源码 assets 中存在并在 build 时打包，不能只把图片放到 dist。
- 对齐支持 `left`、`center`、`right`，默认 center；三段独立光晕支持 `light`、`high-light`、
  `accent`、`none`，沿用历史 `hight-light` -> `high-light` 别名。默认 left light、center/right
  accent，大小写/空白规范化及无效值回退沿用旧合同。组件按自然比例 contain、对齐及 ResizeObserver
  更新布局，沿用 Core 已存在的主题光晕变量，不改变全局主题。五项配置在隔离 fixture 可观测。
- 双语 README 从未使用品牌 key 的描述更新为受支持配置用途、允许值与 fallback；四 env 英文
  说明同步。两个 `.example` 可新增/完善五项品牌 key 的中性安全默认值；实际文件的五项品牌
  值与其他非权限值必须保持不变。Dockerfile 如需独立 image build 传入五变量，仅增加对应
  ARG/ENV 中性默认，不修改现有发布拓扑或依赖。
  真实 Docker dev 文件如原本没有品牌 key，不强制新增；仅 example 新增安全默认。

## R4-ACCESS-001：按 Owner 明确授权调整当前宿主机测试权限

- `frontend-js/.env` 的 supervisor/operator 活动新数组改为原授权与当前启用、非 admin-only
  leaf pageId 的交集；保持各自原顺序，不从未授权页面补授予。已确认 supervisor 20 -> 3：
  `dashboard.home`、`plan.list`、`system.user`；operator 14 -> 2：`dashboard.home`、`plan.list`。
  最终以原数组顺序写入，operator 继续是 supervisor 子集。
- `.env.docker.dev` 原两数组 0/0 保持 0/0，不扩权；README 的旧 20/14 历史 JSON 以及 Docker
  历史对象保持等值，不删除或覆盖记录。其他 env 活动 key/value，包括 mock、API、品牌设置不变。
- 不放宽 unknown/disabled/admin-only/子集规则，不迁六模块，003 仍仅后续范围说明。
  真实 `.env` 权限 checker、dev 启动和临时输出 build 应通过；不得据此宣称真实 backend 或
  登录业务已验证，不擅启 mock。UI 品牌矩阵使用公开隔离 fixture，不连接真实后端。

## r4 精确 allowlist 与角色边界

- 源码：`frontend-js/src/config/brand.js`、`frontend-js/src/components/shell/BrandLogo.vue`、
  `frontend-js/src/assets/brand/demo-organization-logo.svg`。
- 如直接 Node 导入 `import.meta.glob` 阻碍有意义单元验证，可新增薄纯 helper
  `frontend-js/src/config/brandOptions.js` 解析 env/文件名/align/glow/fallback；优先简单实现，
  不要求为单次复用创建复杂抽象。
- 检查：`frontend-js/tests/module-registry/` 下品牌解析测试；`frontend-js/package.json` 仅在
  必须时接入 test script，不改 dependency/devDependency 或锁文件。临时公开 env、build、
  browser fixture 与证据使用 `/private/tmp`。
- 配置/说明：`frontend-js/README.md`、`README.zh-CN.md`、`.env`、`.env.docker.dev`、
  `.env.example`、`.env.docker.dev.example`、`frontend-js/Dockerfile`（仅五品牌 ARG/ENV）、
  根 `CODE_INDEX.md`（仅新增品牌配置/资源真实结构对应索引）。真实 env 继续 ignored，不提交。
- PM 只写 spec；Development 更新 tasks 当前 r4 元数据，保留 r2/r3 开发历史；交接后新的
  fresh-context Verification 更新 checklist 当前 r4 元数据，保留 r2/r3 QA verdict/证据。
  主协调者仅机械同步已有授权的本任务索引。不改其他任务、后端、DB、设备、Compose、Nginx、
  global theme、login/MainLayout、权限实现或其他模块，不进行 Git 发布与生产部署。

## r4 验收标准

- **AC-r4-001**：品牌解析正反例覆盖文件名存在、缺失、未知、无效路径/URL/穿越及中性 fallback；
  alignment 三值、无效值默认、glow 四值/三段及历史 alias/大小写空白规范化通过。
- **AC-r4-002**：隔离 build 与 browser 证明现有登录和壳层 BrandLogo 读到五项配置，Logo
  自然比例与 left/center/right 对齐可观测，三段 glow 与 none/alias 正常；不白屏、不引入客户资产。
- **AC-r4-003**：两真实 env 迁移前后按 key/checksum 比对，允许差异仅宿主机两角色数组；
  intersection 保留顺序，sup3/op2，Docker0/0，其他值（含五品牌值）相等；旧 README JSON
  等值保留，四 env 英文说明，模板默认安全，双语说明/链接一致。
- **AC-r4-004**：真实 `.env` 权限 checker（development/production）、dev 有限启动与临时
  输出 build 通过；其 mock/API 值未修改，不测试真实登录/API。`pnpm check:modules`、
  `pnpm test:modules`、相关品牌测试及 `git diff --check` 记录真实结果；未安装依赖，未迁六模块。
- **AC-r4-005**：变更在精确 allowlist 内，r2/r3 完整历史保留，r4 fresh-context verdict
  独立记录；真实 API、生产部署、001 final acceptance 和 Owner 最终验收不被冒称完成。

风险与回退：旧 Logo 文件在 Core 不存在时使用中性 fallback，不以客户资产解决；权限配置
收敛是 Owner 本轮明确决定，历史 JSON 保留以供未来模块迁入后人工重新授权。品牌修复出错仅
回退本轮品牌变更及已授权配置差异，不自动扩大访问、不绕过权限校验；生产回退需另行授权。

批准记录：2026-10-08 Human Owner 本轮直接要求补回上述既有功能，并明确要求将 env 调整为
当前模块页面测试；本精确 r4 为 `owner_approved`。此前“不清理”保留要求在当前两角色活动
数组交集调整范围被本轮授权覆盖，旧记录仍保留；未授予其他 env 值修改或批量迁模块权限。

# r3 历史批准范围：文档与配置注释收尾

本 r3 是 r2 已通过 QA 后的 documentation/config-comment-only 修订。r2 实现及 QA 记录保留，
不将 r2 `qa_passed` 自动继承为 r3 的 verdict 或 Human Owner 最终验收。下文 r2 的目标、功能
合同、allowlist、AC 和风险是历史基线参考；本节限定 r3 的新增实施范围并优先于历史注释保留规则。

## R3-DOC-001：配置用途说明与英文注释

- 在 `frontend-js/README.md` / `README.zh-CN.md` 逐项说明前端 env 配置用途，覆盖四文件中
  现有活动 key 的含义、适用场景、公开构建值边界、权限 pageId/子集语义、开发重启与正式重新构建。
  说明宿主机 dev/build 共用 `.env`，Docker dev 继续使用 `.env.docker.dev`，Vite 覆盖优先级。
- `frontend-js/.env`、`.env.docker.dev` 及其两份 `.example` 的说明统一为英文；可整理说明，
  不改 key、活动值、授权成员或其他设置。README 中文版 prose 保持中文，英文版保持英文。

## R3-DOC-002：将指定历史权限记录移入 README

- 用户本轮明确允许移除正式 env 中 ARCH-FE-002 历史说明行和旧
  `VITE_ROLE_PAGE_ACCESS_JSON` 注释行；这仅覆盖此前“不清理”授权中这两类历史注释的保留要求。
  不删除其他活动设置、不删除 env 文件、不恢复旧 key 活动消费。
- 将用户本轮明确提供的旧角色 JSON 作为历史参考记录到前端 README 双语 pair；它只包含 pageId，
  明示历史记录不参与当前读取，不建议直接恢复已未迁入页面的授权。两文档使用相同 JSON 内容。
  如两个正式 env 均有不同旧注释对象，按场景标识分别保留对应历史对象，不能用一份覆盖另一份。
- 当前两项活动新数组保持不变，真实 host 配置的 unknown-page 阻断和 Docker dev 空授权边界
  继续保留。禁止把真实地址、其他私有配置或密钥搬入 README；不复制整份真实 env。

## r3 精确 allowlist 与角色边界

- Development 只修改 `frontend-js/README.md`、`frontend-js/README.zh-CN.md`、
  `frontend-js/.env`、`frontend-js/.env.docker.dev`、`frontend-js/.env.example`、
  `frontend-js/.env.docker.dev.example`，以及本任务 `tasks.md`。
- 两真实 env 继续 Git ignored，绝不提交。不新增 production env，不修改源码、依赖、Dockerfile、
  Compose、Nginx、其他任务或文档。主协调者如需同步本任务索引，按已存在事实机械同步。
- PM 仅写本 spec；Development 在 tasks 更新当前 r3 元数据并保留 r2 完整开发证据；新
  fresh-context Verification 在 checklist 更新 r3 元数据，保留 r2 verdict/证据并添加独立 r3
  检查，不提前创建 QA 结果。最终验收仍由 Human Owner 记录。

## r3 验收标准

- **AC-r3-001**：修改前后四份 env 的活动 key/value 规范化 checksum 相等；两真实文件仍
  Git ignored，数组内容与顺序相等。checksum 证据不回显私有值；无活动旧 key，无新增配置来源。
- **AC-r3-002**：指定历史说明和旧 key 注释从正式 env 移除，原旧 JSON 的角色数组成员与顺序
  在 README 历史记录中等值保留；双语记录相同，不含真实地址或其他 env 值。
- **AC-r3-003**：四份 env 的自然语言说明均英文且语义一致；README pair 对所有现有活动 key
  的用途、场景和重启/构建边界覆盖完整，本地文档链接与 `git diff --check` 通过。
- **AC-r3-004**：仅授权文件注释/文档变更；源码行为和权限不变，r2 开发及 QA 历史保留；
  r3 fresh-context QA verdict 独立记录。真实业务 API、部署、001 final acceptance 继续不在范围。

风险与回退：注释误改活动值会改变项目行为，必须以修改前 checksum 与逐 key 对比发现；如检查
失败仅修正本轮注释编辑，不借机调整权限。历史 JSON 丢失以修改前受控读取记录核对并恢复到
README。无生产部署、Git 写操作或数据库动作授权。

批准依据：Human Owner 本轮直接追加“002 文档/注释收尾”授权，明确要求前端 README 双语解释
每个配置、四份 env 注释统一英文、移走正式 env 的 ARCH-FE-002 历史注释及旧 key 注释并在
README 保留用户提供的旧角色 JSON，活动新数组不变。该授权构成本精确 r3 的 `owner_approved`，
无需再次询问；仅记录已授权收尾，不扩展功能或清理范围。

# r2 历史基线与批准记录（以下保留供审计，不扩大 r3 allowlist）

# 目标与当前依据

使用同一份可复用前端源码，按项目构建各自的 `dist`。模块是否参与路由装配继续由模块
`manifest.js` 的 `enabled` 决定；已启用页面对非 admin 角色的可见性由项目构建配置决定。
首批以工作区现有的 `dashboard` 与 `plan` 两个目录验证旧模块的 manifest 适配和
双语菜单装配，不将“粘贴目录”当作完成验收。

2026-09-28 历史只读基线（不作为 r2 当前 Git 状态）：当时 `frontend-js/src/app/dashboard/` 与 `plan/` 是用户已复制的未跟踪
目录；`pnpm check:modules` 因 dashboard 仍引用不存在的 `breadcrumb.dashboard` 而 exit 1，
浏览器 `http://localhost:5190/` 控制台出现相同 Registry 异常并显示空白页。plan manifest 还引用
旧 `breadcrumb.planList`、`nav.plan`。现有 `src/config/permissions.js` 仅解析
`VITE_ROLE_PAGE_ACCESS_JSON`，不保证 operator 权限是 supervisor 的子集。`frontend-js/` 已跟踪
`.env.example`、`.env.docker.dev.example` 两份模板；真实 `.env`、`.env.docker.dev` 被 Git 忽略。
当前 prod Compose 只读挂载宿主机预构建 `dist`，前端没有独立的 prod env 模板。

2026-10-08 r2 当前依据：本 Revision 写入前 `git status --short` 为空，dashboard/plan 已在
跟踪基线内，仍保留上述旧 manifest 标题键；“未跟踪目录”只作为 r1 历史。主协调者不回显真实
env 的检查确认：本地 `.env` 旧配置含 supervisor 20 项、operator 14 项，operator 是 supervisor
子集；`.env.docker.dev` 的旧对象为空。多数授权属于尚未迁入的六个模块，当前 Registry 只有
dashboard/plan/system 的四个 pageId。用户要求不要清理，因此完整保留角色数组与其他设置迁移，
不能为了校验通过删除未知授权、清空权限或自动扩权。未知 pageId 严格校验将使这份 `.env` 在
003 迁回模块或 Owner 明确调整授权前拒绝 dev/build；这是已知配置兼容边界。公开隔离 fixture
可以验证实现，不能据此宣称真实配置通过。ARCH-FE-001 final acceptance 尚未记录，本次批准只
解除 002 的启动 gate。

# 决定与范围

## R1：角色页面权限合同

1. 用两个 JSON 数组构建值替代旧角色对象：
   `VITE_SUPERVISOR_PAGE_ACCESS_JSON` 与 `VITE_OPERATOR_PAGE_ACCESS_JSON`。元素是 manifest 的
   `meta.pageId`，不是路由 URL、模块名或 API permission；示例值默认均为 `[]`。
2. 有效权限满足 `operator ⊆ supervisor`。配置解析必须拒绝非数组、非字符串/非法 pageId、重复
   pageId、operator 独有 pageId、未知或未启用的 pageId，以及 `requiresAdmin: true` 的 pageId。
   缺失或损坏配置不得扩权；构建前应明确失败并指出变量与 pageId，而不是静默补给 supervisor。
3. `admin` 是代码内置角色，不在两个 env 数组中配置；它可访问已启用模块的有效页面。侧栏只展示
   manifest 标记为可见的 leaf；页面还须有 `pageId`。未知角色 fail closed。前端权限只影响菜单、
   路由与默认入口，不代替 backend API 授权。
4. 按用户“旧配置一起改造，不要清理”授权，仅保留两个新变量作为活动来源；就地迁移实际 env，
   保留文件、其他设置、原 supervisor/operator 数组的成员与顺序。旧 key 原行可注释为历史，
   不活动消费；活动旧 key 残留明确报迁移错误，不同时接受新旧来源。旧对象缺少某角色时对应
   新数组为 `[]`。非法旧 JSON/schema、新旧活动值冲突或其他未知角色不能静默丢弃，应记录脱敏
   blocker。不得为满足子集规则给 supervisor 增项；未知 pageId 原值保留，由校验明确报错。
   记录配置兼容性，不在本任务决定版本号或发布 Git refs。
5. 提供可重复的显式权限 checker，通过 `vite.config.js` 接入 dev/build 对应 mode 的有效 env
   校验；宿主机文件、mode/local 文件和进程覆盖遵循 Vite 优先级，不能只检查固定 `.env` 后让
   其他模式绕过。可用独立纯 helper 统一浏览器和 Node 的解析/schema/Registry 校验。保留裸调用
   manifest checker 仅显示帮助、不默认读 `.env` 的边界；新 checker 裸调用同样仅显示帮助。
   测试用公开 env 或 `/private/tmp` 夹具，不回显真实 env 内容。

## R2：开发与构建共用配置

Human Owner 已确定宿主机开发与正式构建共用 `.env`，不新增 `.env.production` 或其模板。

| 场景 | 公开模板 | 实际值与读取位置 |
| --- | --- | --- |
| 宿主机开发与正式构建 | `frontend-js/.env.example` | Git 忽略的 `frontend-js/.env`；Vite dev/build 启动时读取 |
| Docker dev | `frontend-js/.env.docker.dev.example` | Git 忽略的 `frontend-js/.env.docker.dev`；现有 Compose `env_file` 注入 |

两份公开模板使用相同新 key、空数组安全默认值和一致语义；旧 key 可留注释历史，不活动消费。
用户已有忽略文件 `.env`、`.env.docker.dev` 的旧权限也在本次迁移授权内，保留文件、其他值与
原授权，不清理、不提交、不回显真实 env。证据只记录 key、计数、校验结果与限制；公开模板不
复刻真实权限或地址。若现有 mode/local 或进程变量覆盖值，检查影响但不擅自清理。
`frontend-js/Dockerfile` 独立镜像构建 ARG/ENV 同步新 key；prod Compose 继续宿主机预构建 dist。
`pnpm build` 使用 Vite production 模式，读取共用 `.env` 并按 Vite 规则叠加已有 mode/local 文件
和进程覆盖。构建前核对 API 地址并关闭 mock/演示账号；fixture 构建不当作交付产物。
`VITE_*` 是公开构建值，不能放密钥；修改 env 后须重新构建，单独重启 Nginx 不会改变已有 dist。
挂载目录内更新并核对 `index.html` 后刷新；若替换整个 `dist` 目录，按现有部署说明重新创建
frontend 容器以重新绑定。本任务只更新操作说明，不执行部署或 Docker 操作。

## R3：dashboard/plan 首批模块

1. 对工作区现有两个模块先作公开安全、依赖、API 与跨模块引用审计；如含客户专有规则、真实地址、
   未获准公开的内容或需要 backend 迁移，停止源码迁入并由 PM 修订范围，不以 mock 构建通过代替
   真实业务可用性。
2. 两个 manifest 使用模块自己拥有的双语标题键；保留既有 route name/path/pageId，新增显式
   `enabled: true`、模块 `navigation`、可见 leaf 与稳定顺序（dashboard 10、plan 20）。不得修改
   共享 router、MainLayout 或全局 locale 汇总来为这两个模块写硬编码入口。
3. 两个模块的页面、API facade、locales 与通用组件依赖须通过 build 和浏览器验证；真实后端 API
   不在本任务提供或修改。无 backend fixture 时须把页面编译/导航通过与业务数据不可用分开记录。
4. 其他旧项目模块（`auxiliary`、`equipment`、`maintenance`、`monitor`、`performance`、`quality`）
   只列候选清单；它们的逐模块公开安全审核、业务 API 对齐及迁入另立精确 Revision/任务，不在本
   r2 批量复制；后续预留 ARCH-FE-003，002 不创建或实施 003。保留默认关闭的 aiis_demo，作为
   新模块接入参考与关闭模块验证夹具。

# 精确 Development 写入候选 allowlist

Human Owner 已批准下列 r2 范围，Development 可按本 spec 修改：

- `frontend-js/src/config/permissions.js`、`frontend-js/src/config/pageAccess.js`（独立纯 helper，
  等价职责命名在 tasks 明示）、`frontend-js/src/store/user.js`、`frontend-js/vite.config.js`，
  及权限校验必需的 `frontend-js/scripts/`、`frontend-js/tests/module-registry/`、
  `frontend-js/package.json`。package.json 只同步校验 scripts，不修改依赖或锁文件。
- 公开隔离 env、浏览器三角色 fixture 与测试产物限 `/private/tmp`；允许路由/API 拦截模拟只读
  数据，不读写真实业务后端，不把 fixture 写入正式业务代码。
- `frontend-js/src/app/dashboard/`、`frontend-js/src/app/plan/` 内经公开安全审核允许保留的文件；
  必要的共享组件只在新的 PM Revision 精确列路径后修改。
- `frontend-js/.env.example`、`frontend-js/.env.docker.dev.example`、`frontend-js/Dockerfile`，
  以及 Git 忽略的 `frontend-js/.env`、`frontend-js/.env.docker.dev`；后两项只迁移旧角色权限，
  保留其他配置与授权原值，绝不提交。不新增生产 env 文件。
- `frontend-js/src/app/README.md`、`frontend-js/src/app/README.zh-CN.md`、
  `frontend-js/README.md`、`frontend-js/README.zh-CN.md`、
  `INITIALIZATION.md`、`INITIALIZATION.zh-CN.md` 中与本合同直接相关的说明；真实文件结构变化
  才同步 `CODE_INDEX.md`。
- 本任务的 `plans/ARCH-FE-002-project-role-access-and-module-pilot/tasks.md` 由 Development 创建；
  `checklist.md` 仅由交接后的独立 Verification 创建。根与 frontend 的 PLAN pairs、根任务目录
  README pairs 只维护本任务索引状态。

不改 backend 权限/API/数据库、其他模块、Compose、Nginx 配置、依赖锁文件、真实设备、发布 refs 或
客户项目仓；不覆盖当前工作树中 ARCH-DOCKER-002 与其他任务的已有改动。

# 验收标准

- **AC-001**：两份公开模板与 Dockerfile 使用两项新 key，旧 key 无活动消费；宿主机 dev/build
  共用 `.env`，Docker dev 沿用 `.env.docker.dev`，不新增生产 env；读取、覆盖及重启/重建语义
  在双语文档一致。真实旧授权和其他设置保留迁移，以脱敏计数核对，不删除未迁入页面授权。
- **AC-002**：operator 配置严格为 supervisor 子集；非法 JSON/schema、重复/未知/未启用/admin-only
  pageId、残留旧变量明确失败；合法空数组不授予非 admin 页面，未知角色 fail closed。
- **AC-003**：admin、supervisor、operator 对相同 Registry 的 route/menu/default 决策一致；
  `enabled: false` 的模块对三种角色均无可访问路由或菜单，`enabled: true` 不自动创建菜单或 API 权限。
- **AC-004**：dashboard/plan 经审核符合公开架构仓边界，双语 title、route identity、菜单顺序、
  页面依赖通过 checker/test/build；浏览器不再因 Registry 标题校验白屏，菜单点击与直接 URL
  按三角色矩阵验证。业务 API 未验证的范围单独列明。
- **AC-005**：保留 `pnpm check:modules`、`pnpm test:modules`、`pnpm build` 实际退出码；权限正反例、
  dev/build 模式与覆盖测试、双语链接及 `git diff --check` 通过。公开隔离配置 build/browser
  通过与真实 `.env` 未知页面阻塞分开记录；fresh-context Verification 独立复核，Owner 最终
  验收另行记录。aiis_demo 继续默认关闭。

# 风险、回退与未授权边界

- 旧 env 切换新 key 是配置兼容性变化；失败时恢复上一份已审核构建与对应配置，不通过临时给
  operator 扩权来绕过校验。旧配置不可与新配置并存为两个运行来源。
- `enabled: false` 只退出正常前端消费者；不保证源码不被扫描/打包，不构成安全隔离。客户收到
  前端 bundle 后，页面可见性不能充当功能保密或后端 API 授权。
- 本任务不执行 Docker `up/down/build`、数据库写入、生产构建交付、Nginx 重启/重建、Git
  add/commit/push/tag 或版本发布。实际生产部署和真实账号/API 验证另行授权并记录证据。
- r2 已获批准进入 Development；未授权扩大模块范围、删除配置或自动改变权限成员。真实 env
  未迁入 pageId 阻塞必须如实保留；解除需 003 完成或 Owner 明确提供调整授权。001 final
  acceptance 仍独立，本次批准不冒充其验收。
- Development 按 frontend-ui、i18n-workflow、code-document-indexer 合同实施；客户专有内容、
  范围外共享组件或实质验收变化须停止受影响写入，返回 PM 新 Revision 与 Human Owner 批准。

# 修订与批准记录

- 2026-09-28：Human Owner 要求“落 spec，三套 env 也要同步跟进”；形成 r1 PM 草案。
  尚无 Development 批准、tasks.md、checklist.md 或实施证据。
- 2026-10-08：Human Owner 确定宿主机开发与正式 build 共用 `.env`，不新增 `.env.production`；
  Docker dev 保留 `.env.docker.dev`；六个后续模块预留 003，demo 保留。r1 三份模板假设、
  未跟踪基线及启动 blocker 由 r2 取代，保留历史。
- 2026-10-08：Human Owner 原文：“改造的时候，旧配置一起改造，不要清理。批准002，并进入dev”。
  r2 将已讨论决定与原文批准落盘为 `owner_approved`，进入 Development；只授予 002 r2 配置
  迁移、源码及验证，不授予 001 final acceptance、生产部署或发布。
- 2026-10-08：r2 已完成 Development handoff 与独立 QA，checklist verdict 为 `qa_passed`，
  Human Owner final acceptance 仍待记录；原证据保持历史事实。
- 2026-10-08：Human Owner 追加授权上述 r3 文档与配置注释收尾，形成 `owner_approved` r3。
  允许移走明确指定历史注释并在 README 保留旧角色 JSON，活动新数组和全部其他值不变。
