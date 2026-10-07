Task ID: ARCH-FE-002
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 等待 Human Owner 核对三套前端 env 的含义、首批模块范围并精确批准 r1；不得据此开始 Development

Task Namespace: aiis-ics-arch
Classification: root
Capability: 项目构建期的 supervisor/operator 页面权限配置与首批模块接入验证
Owner: frontend-js Core 模块框架
Related Task: ARCH-FE-001
Blocked By: ARCH-FE-001 Human Owner final acceptance
Acceptance Chain Reference: ARCH-FE-002 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Execution Mode: agent_team_same_session
Created: 2026-09-28
Updated: 2026-09-28

# 目标与当前依据

使用同一份可复用前端源码，按项目构建各自的 `dist`。模块是否参与路由装配继续由模块
`manifest.js` 的 `enabled` 决定；已启用页面对非 admin 角色的可见性由项目构建配置决定。
首批以工作区现有、尚未跟踪的 `dashboard` 与 `plan` 两个目录验证旧模块的 manifest 适配和
双语菜单装配，不将“粘贴目录”当作完成验收。

2026-09-28 只读基线：当前 `frontend-js/src/app/dashboard/` 与 `plan/` 是用户已复制的未跟踪
目录；`pnpm check:modules` 因 dashboard 仍引用不存在的 `breadcrumb.dashboard` 而 exit 1，
浏览器 `http://localhost:5190/` 控制台出现相同 Registry 异常并显示空白页。plan manifest 还引用
旧 `breadcrumb.planList`、`nav.plan`。现有 `src/config/permissions.js` 仅解析
`VITE_ROLE_PAGE_ACCESS_JSON`，不保证 operator 权限是 supervisor 的子集。`frontend-js/` 已跟踪
`.env.example`、`.env.docker.dev.example` 两份模板；真实 `.env`、`.env.docker.dev` 被 Git 忽略。
当前 prod Compose 只读挂载宿主机预构建 `dist`，前端没有独立的 prod env 模板。

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
4. 迁移旧 `VITE_ROLE_PAGE_ACCESS_JSON` 时不得同时接受新旧来源或静默沿用旧值。旧变量残留应给出
   明确迁移错误；实际项目构建必须显式核对新数组。记录此配置合同变更的兼容性结论，不在本任务
   决定版本号或发布 Git refs。
5. 权限检查提供可重复的显式入口，并接入 `pnpm build` 前置检查；保留现有裸调用 manifest checker
   只显示帮助、默认不读取 `.env` 的边界。测试用公开占位 env 或 `/private/tmp` 夹具，不回显真实
   env 内容。

## R2：三种前端配置场景

本 r1 暂按“宿主机开发、Docker dev、生产宿主机构建”理解用户所说的三套 env；这是待 Human Owner
确认的 PM 假设，不把 backend 的三份 env 模板混入前端角色权限。

| 场景 | 公开模板 | 实际值与读取位置 |
| --- | --- | --- |
| 宿主机开发 | `frontend-js/.env.example` | Git 忽略的 `frontend-js/.env`；Vite dev 启动时读取 |
| Docker dev | `frontend-js/.env.docker.dev.example` | Git 忽略的 `frontend-js/.env.docker.dev`；现有 Compose `env_file` 注入 |
| 生产宿主机构建 | 新增 `frontend-js/.env.production.example` | 部署方私有 `frontend-js/.env.production`；Vite production build 读取，交付结果为 `dist` |

三份公开模板使用相同的两个新 key、空数组安全默认值和一致的语义；移除旧 key。真实 env 不进入
Git 或任务证据，PM 阶段不读取、不改写。Development 若获批，只能在明确允许的实际 env 中按 key
迁移并保留其他值；生产真实值由部署方确认。`frontend-js/Dockerfile` 的独立镜像构建 ARG/ENV 也需
同步新 key，但根 prod Compose 继续采用宿主机预构建 `dist`，不因本任务切换交付拓扑。
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
   r1 批量复制。这一边界也等待 Human Owner 对“所有模块”的本次范围作最终确认。

# 精确 Development 写入候选 allowlist

仅在 r1 经 Human Owner 精确批准且前述待确认假设得到确认后，Development 可按本 spec 修改：

- `frontend-js/src/config/permissions.js`、`frontend-js/src/store/user.js`，以及为权限校验所必需
  的 `frontend-js/scripts/`、`frontend-js/tests/module-registry/` 和 `frontend-js/package.json`。
- `frontend-js/src/app/dashboard/`、`frontend-js/src/app/plan/` 内经公开安全审核允许保留的文件；
  必要的共享组件只在新的 PM Revision 精确列路径后修改。
- `frontend-js/.env.example`、`frontend-js/.env.docker.dev.example`、新增的
  `frontend-js/.env.production.example`、`frontend-js/Dockerfile`；实际忽略 env 的 key 迁移仅按
  §R2 的部署方边界处理，绝不提交。
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

- **AC-001**：三份公开前端 env 模板与 Dockerfile 构建入口使用两项新 key，旧 key 无活动消费；
  宿主机 dev、Docker dev、production build 的读取路径及重启/重建语义在双语文档中一致。
- **AC-002**：operator 配置严格为 supervisor 子集；非法 JSON/schema、重复/未知/未启用/admin-only
  pageId、残留旧变量明确失败；合法空数组不授予非 admin 页面，未知角色 fail closed。
- **AC-003**：admin、supervisor、operator 对相同 Registry 的 route/menu/default 决策一致；
  `enabled: false` 的模块对三种角色均无可访问路由或菜单，`enabled: true` 不自动创建菜单或 API 权限。
- **AC-004**：dashboard/plan 经审核符合公开架构仓边界，双语 title、route identity、菜单顺序、
  页面依赖通过 checker/test/build；浏览器不再因 Registry 标题校验白屏，菜单点击与直接 URL
  按三角色矩阵验证。业务 API 未验证的范围单独列明。
- **AC-005**：保留 `pnpm check:modules`、`pnpm test:modules`、`pnpm build` 的实际退出码；新增权限
  校验的正反例、双语文档链接与 `git diff --check` 通过。fresh-context Verification 独立复核，
  Human Owner 最终验收另行记录。

# 风险、回退与未授权边界

- 旧 env 切换新 key 是配置兼容性变化；失败时恢复上一份已审核构建与对应配置，不通过临时给
  operator 扩权来绕过校验。旧配置不可与新配置并存为两个运行来源。
- `enabled: false` 只退出正常前端消费者；不保证源码不被扫描/打包，不构成安全隔离。客户收到
  前端 bundle 后，页面可见性不能充当功能保密或后端 API 授权。
- 本任务不执行 Docker `up/down/build`、数据库写入、生产构建交付、Nginx 重启/重建、Git
  add/commit/push/tag 或版本发布。实际生产部署和真实账号/API 验证另行授权并记录证据。
- 本 spec 为 PM draft；“三套 env”文件对应和其余六模块是否纳入同一 Revision 仍待用户回答。
  若答案改变范围、allowlist、风险或验收，PM 必须先出新 Revision，不能直接进入 Development。

# 修订与批准记录

- 2026-09-28：Human Owner 要求“落 spec，三套 env 也要同步跟进”；形成 r1 PM 草案。
  尚无 Development 批准、tasks.md、checklist.md 或实施证据。
