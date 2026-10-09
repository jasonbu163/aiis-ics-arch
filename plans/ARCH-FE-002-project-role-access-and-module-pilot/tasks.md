Task ID: ARCH-FE-002
Revision: r4
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: r4 品牌功能恢复与当前模块测试配置完成；真实 checker/dev/build 及公开品牌矩阵通过，交 fresh-context Verification；r2/r3 开发与 QA 历史不自动继承为 r4 verdict

# r2/r3 Development 历史证据（完整保留）

Task ID: ARCH-FE-002
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: r3 README 双语配置说明及四 env 英文注释完成；活动 key/value checksum 相同，历史 JSON 移入 README，交 fresh-context Verification；r2 QA 历史保留不自动继承

# r2 Development 历史证据（完整保留）

Task ID: ARCH-FE-002
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: ARCH-FE-002 r2 源码与原样配置迁移完成，自检记录后交接 fresh-context Verification；实际宿主机未知页面授权阻塞如实保留

# Development 计划

1. 纯 `src/config/pageAccess.js` 统一两个数组、子集与 Registry pageId 校验；dev/build 与显式 checker 共用 Vite loadEnv → Node 正反例、mode/local/process 覆盖测试。
2. dashboard/plan manifest 首批适配，审核依赖、公开安全、跨模块入口与双语文案 → manifest checker、literal i18n 检查、隔离 build/browser。
3. 两份公开模板、Dockerfile 和双语稳定文档同步；实际旧配置按 r2 原样迁移 → 脱敏计数、diff、链接检查。

# 边界与基线

- 精确批准 spec r2；只写其 allowlist，不写 spec/checklist/PLAN，不部署、不 Docker 操作、不 Git 写、不 backend。
- `pageAccess.js` 是 spec 指定纯 helper；Node checker 复用它与 manifest loader。
- 真实 `.env` 旧 supervisor 20/operator 14（子集成立），部分页面未迁入；按批准 r2 原样迁移，保留未知授权。fixture 通过不代表真实 env 可启动。
- 其他六模块不迁入，aiis_demo 继续关闭。Dashboard 引用 plan 组件/文案时记录理由或收回当前 namespace。

# DEV self-check

## 源码与审计

- `src/config/pageAccess.js` 校验两数组、pageId schema/重复、子集、活动 leaf/disabled/admin-only；旧 key 活动存在即报迁移错误。
- `permissions.js` 复用纯 helper 与统一 Registry；user store 原 provider 无需修改。checker `check-page-access.mjs` 按 mode 复用 Vite loadEnv，vite config 在 dev/build 开始前检查。
- dashboard/plan 保留 route name/path/pageId，新增 enabled/navigation/visible；组顺序 10/20，system 80，demo 关闭。
- 原 dashboard 引用缺失 performance 温度标题、错误提示使用 plan 文案，以及 plan 引用不存在 common.saveError，已收回模块自有双语 key。dashboard RecentPlans 复用 plan 字段文案/PlanStatusTag：它表达同一计划业务对象，两个 pilot 同时存在，理由记录于 app README。
- dashboard 快捷链接与查看计划入口用活动 Registry 和当前 access provider 过滤。不存在的 performance/monitor/equipment 及未授权 plan 入口不显示，不迁入这三个模块。
- 浏览器发现 plan mock `materialStatus=ready` 未定义：调整模块诊断值为既有 `degreasing`，动态材料状态加 te fallback，未知后端值显示原值；未改真实 API/字段映射。
- 双模块 import 只依赖仓库已有公共组件、theme/user store、utils/request/echarts、mock diagnostic 和互相的计划状态组件；无新增依赖。源内容搜索未发现客户公司名、真实 IP/URL、密钥或账号。模块 mock 有 FRONTEND_MOCK 标识和通用示例字段，不是客户真实记录。
- dashboard API 为 `/dashboard/*` GET；plan `/plans`、XLSX 与 `/plans/linkage/performances/*` facade 保留。核心后端不提供/迁移这些业务接口，业务 CRUD/XLSX/关联真实可用性未验证，不作为本次 build/browser 结论。

## 已执行自检（2026-10-08）

- `pnpm --dir frontend-js check:modules`: exit 0；活动 dashboard/plan/system，5 route records、3菜单组。
- `pnpm --dir frontend-js test:modules`: exit 0；18组通过。初次预期序列因 leaf order 改变失败已修正；literal key 测试发现并修复以上缺失键；扩展 Vite config 负例 fixture 缺 config copy 后补齐并最终通过。
- 测试覆盖 missing/malformed/non-array/non-string/非法/duplicate、unknown/disabled/admin-only、旧 key、operator 不在 supervisor；三角色和未知角色 route/menu/default；双语 literal keys；shared env、local、mode、mode.local、process优先级；实际 Vite dev/build/自定义mode 在未知进程覆盖时均 exit 1。
- `/private/tmp/arch-fe002-dev-fixture` 公共隔离 env、源码复制与已安装 node_modules 链接：`pnpm --config.verify-deps-before-run=false run build --outDir /private/tmp/arch-fe002-dist`: exit 0，2192 modules transformed。默认 fixture pnpm build 曾因链接的依赖状态触发自动 install 并网络失败/no TTY exit1；仅在临时fixture禁用状态检查，不安装依赖，不修改项目锁/config。
- 隔离 build 有既有大 chunk 和外部 outDir 提示；不当作部署产物。最终模块文案修正后已重建 exit0，详见下方记录。
- 隔离 dev 127.0.0.1:5194 首次 sandbox listen EPERM exit1，获工具审批后启动成功；协调者正在承担三角色双语浏览器验证，使用 mock，不连真实后端。
- `node frontend-js/scripts/check-page-access.mjs` 与 `node frontend-js/scripts/check-module-manifests.mjs`: exit0，仅帮助，不读取env。
- 双语稳定文档本地 Markdown target 检查：12个目标存在；`git diff --check`: exit0。
- 迁移前 `pnpm --dir frontend-js check:access --mode development` 与真实env `pnpm --dir frontend-js build --outDir /private/tmp/arch-fe002-real-env-blocked`: exit1，明确 retired legacy key。迁移后结果见下方，不能据隔离 fixture 宣称真实env绿色。

## 当前交接状态

- 源码、配置迁移、隔离构建与浏览器角色矩阵已完成 Development self-check；精确 handoff 见末节，fresh-context Verification 待独立执行。

## Configuration migration result

- Approved r2 migration completed in ignored `.env` and `.env.docker.dev`; original legacy lines retained as comments. Other settings unchanged. No permission membership or ordering was removed or expanded.
- Counts before/after: host supervisor 20/operator 14; Docker dev 0/0. Postcheck compares active arrays to original commented JSON, equal including order; git check-ignore still confirms both files ignored.
- After migration: host check:access development, pnpm dev (5195), and pnpm build (temporary output) each exit 1 for unknown pageId. This is the expected preserved-grant boundary until 003 or explicit Owner adjustment.
- check:access --mode docker.dev exits 0, arrays 0/0; this uses Vite mode precedence and is not Docker runtime evidence. No production env file added.
- Final fixture build after pilot fixes: exit 0, 2192 modules, /private/tmp/arch-fe002-dist-final, log /private/tmp/arch-fe002-build.log.
- Configuration migration is complete. Browser matrix evidence and precise Developer handoff are recorded below.

## Development-owned changed files

- `CODE_INDEX.md`
- `INITIALIZATION.md`
- `INITIALIZATION.zh-CN.md`
- `frontend-js/.env.docker.dev.example`
- `frontend-js/.env.example`
- `frontend-js/Dockerfile`
- `frontend-js/README.md`
- `frontend-js/README.zh-CN.md`
- `frontend-js/package.json`
- `frontend-js/scripts/check-page-access.mjs`
- `frontend-js/src/app/README.md`
- `frontend-js/src/app/README.zh-CN.md`
- `frontend-js/src/app/dashboard/components/QuickLinks.vue`
- `frontend-js/src/app/dashboard/components/RecentPlans.vue`
- `frontend-js/src/app/dashboard/components/TemperatureTrendChart.vue`
- `frontend-js/src/app/dashboard/locales/en-US.json`
- `frontend-js/src/app/dashboard/locales/zh-CN.json`
- `frontend-js/src/app/dashboard/manifest.js`
- `frontend-js/src/app/dashboard/views/home/index.vue`
- `frontend-js/src/app/plan/api/mock.js`
- `frontend-js/src/app/plan/components/PlanFormDialog.vue`
- `frontend-js/src/app/plan/locales/en-US.json`
- `frontend-js/src/app/plan/locales/zh-CN.json`
- `frontend-js/src/app/plan/manifest.js`
- `frontend-js/src/app/plan/views/list/index.vue`
- `frontend-js/src/config/pageAccess.js`
- `frontend-js/src/config/permissions.js`
- `frontend-js/tests/module-registry/page-access.test.mjs`
- `frontend-js/tests/module-registry/registry.test.mjs`
- `frontend-js/vite.config.js`
- `plans/ARCH-FE-002-project-role-access-and-module-pilot/tasks.md`

Ignored local configuration: `frontend-js/.env`, `frontend-js/.env.docker.dev` (permission migration only; not tracked). PM/coordinator spec and index changes are outside Development ownership.

## Browser DEV self-check (coordinator-provided, not QA)

- Surface: CUA browser at isolated `http://127.0.0.1:5194/`, public mock configuration. Only temporary fixture auth role was changed between roles; production auth source remained unchanged. No real backend/credentials were used.
- Admin: root redirects to `/dashboard/home`; Chinese sidebar groups are dashboard, plan, system in order. English dashboard and plan list render; clicking plan reaches the expected heading. Direct `/system/dict` renders Mapping Settings.
- Supervisor: temporary fixture auth role supervisor, logout and login; English sidebar Dashboard/Plan, no System. Plan click and Chinese language switch work. Direct `/system/dict` returns to dashboard.
- Operator: temporary fixture auth role operator, logout and login; Chinese sidebar dashboard only; direct `/plan/list` returns to dashboard. English switch shows Dashboard/Operator.
- Plan mock material status displays Degreasing after the fix instead of a leaked translation key. Parent is additionally collecting console/disabled-demo evidence; the Node regression already confirms the default-disabled module has no registered route/menu for all roles.
- These are Development self-check observations, not fresh-context Verification or Owner acceptance. Real API data, mutations, XLSX and plan-performance linkage remain unverified.

## Precise Developer handoff

- Task: ARCH-FE-002, exact approved Revision r2, shared working tree on main; no Git add/commit/push/tag. PM spec and coordinator task-index updates are distinct from Development implementation.
- Completed: strict two-array configuration and mode-aware dev/build validation; dashboard/plan manifest/menu onboarding and own bilingual keys; filtered cross-module entry links; original ignored permission configuration preserved and migrated; public templates/Dockerfile, paired stable documentation and source index synchronized.
- DEV checks: module checker exit0; 18 Node test groups exit0; final isolated pnpm build exit0; bare checker help and 12 local doc link targets checked; diff --check exit0; public mock browser role/language matrix passed as recorded above.
- Expected remaining runtime limitation: preserved host grants include not-yet-migrated modules, so real dev/build each exit1 for unknown pageId. Docker env effective values validate 0/0 without starting Docker. This meets the r2 preserve-and-report contract and must not be called a usable host configuration yet.
- Verification handoff: review the exact changed files listed above, r2 AC matrix, tests/mode overrides and browser evidence independently; only Verification writes checklist.md. No Owner final acceptance is recorded by Development.
- Resources retained for review: `/private/tmp/arch-fe002-dev-fixture` (current auth fixture role operator), dev session 19192 on 5194; temporary builds `/private/tmp/arch-fe002-dist` and `/private/tmp/arch-fe002-dist-final`; logs `/private/tmp/arch-fe002-tests.log`, `/private/tmp/arch-fe002-build.log`; migration script `/private/tmp/arch-fe002-migrate-config.py` contains no env values. No deployment artifacts in the repository were produced.

## Browser runtime rework before handoff

- Coordinator console inspection reproduced an ECharts 6 radarLayout TypeError on initial dashboard load: indicators were empty while two empty radar series were submitted before asynchronous data arrived. `dashboard/components/OEERadarChart.vue` now clears/skips plotting at zero dimensions and uses notMerge when real indicators arrive. Only the pilot component changed; shared echarts utilities remained unchanged.
- Element Plus rejected empty tag types for normal/unknown priorities. `plan/components/PlanPriorityTag.vue` now uses primary for normal and info for unknown, preserving the numeric fallback label.
- Files added to the Development change list: `frontend-js/src/app/dashboard/components/OEERadarChart.vue`, `frontend-js/src/app/plan/components/PlanPriorityTag.vue`.
- Post-fix Node tests: 18 groups exit0; isolated build `/private/tmp/arch-fe002-dist-radar-fixed`: exit0, 2192 modules; log `/private/tmp/arch-fe002-build-radar-fixed.log`; final diff --check exit0 after fixing whitespace in the changed radar line.
- Handoff paused (`in_progress`) for coordinator's browser reload/console check of these fixes. Earlier handoff section describes the prepared handoff, not an active Verification handoff yet.

## Final handoff confirmation (2026-10-08)

- Coordinator post-fix browser reload after 03:52:00 UTC found no new errors in that log window; dashboard metrics and production trend rendered. Direct `/aiis_demo/example` for operator returned to dashboard (module stays disabled).
- Development browser evidence: `/private/tmp/arch-fe002-browser-dev.md` (coordinator collected). Existing non-blocking warnings include Element Plus radio label deprecation and transient `system.roles.` translation during logout; these shared/legacy surfaces were recorded without expanding implementation scope.
- App README pairs clarify direct vite build bypasses the package prebuild hook but still runs Vite-config Registry/access validation.
- Exact r2 Development handoff is now active: `developer_handoff`. No required Development step remains within r2; runtime unknown-grant restriction, real API non-verification and Owner acceptance remain distinct. Independent Verification may now create checklist.md. Final source changes include the two runtime rework components above; the current working-tree source is the handoff target.

# r3 Development self-check 与精确 handoff（2026-10-08）

## 批准与范围

- 完整读取当前获批 spec r3、既有 tasks r2 与独立 checklist r2 `qa_passed`。r3 当前仅 documentation/config-comment-only；r2 QA 不自动成为 r3 verdict，Human Owner 最终验收仍独立。
- 只改 `frontend-js/README.md` / `README.zh-CN.md`、`.env`、`.env.docker.dev`、`.env.example`、`.env.docker.dev.example` 与本 tasks。真实 env 仍 ignored；不改源码、依赖、Dockerfile、Compose、Nginx、其他任务或索引。
- 按 Owner 明确收尾授权移除真实 env 中 ARCH-FE-002 历史说明及旧 key 注释；不清理其他活动设置，不删除文件，不修改角色授权。

## 实施内容

- README pair 逐项说明 13 个现有活动 key 及可选 `VITE_OPEN_BROWSER`：API base、Vite dev proxy、dev port、request timeout、mock、两角色数组、演示账号提示和五项旧 brand 设置。
- 明确 dev/build 共用 `.env`，Docker dev 使用 `.env.docker.dev`，Vite mode/local/process 覆盖优先级；公开构建值不能放密钥，开发改值重启，正式消费值改动重建 dist，单独重启 Nginx 不能改变已有 bundle。
- `VITE_BRAND_LOGO_FILE/ALIGN/GLOW_LEFT/CENTER/RIGHT` 的活动原行保留；README 只记录原注释意图及 logo 路径/align/glow 模式、旧 hight-light 拼写别名。当前 Core 无消费者，因此不生效；不宣称接受 alias 或渲染支持，不把 brand key 添加到 example。可选 OPEN_BROWSER 仅说明，不新增活动 key。
- 四 env 每 key 使用短英文用途注释，同 key 文字一致；brand 注释准确注明 retained legacy / unused current Core。原活动行保持原文，所有活动 key/value 不变。
- 原旧权限 JSON 只含 Owner 获准的公开 pageIds：宿主机 supervisor 20/operator 14（成员顺序不变），Docker 历史 `{}`。双语 README 分场景保留相同对象，说明纯历史不读取、不建议直接恢复尚未迁入的授权；没有搬入任何真实地址或其他私有 env 值。
- README 原“旧行可留 env 注释”的表述同步为 README 历史节归档，真实 env 不再含指定历史说明/旧变量注释。活动配置继续只有两个新数组，unknown-page 阻断及 Docker 空授权边界不变。

## DEV 自检证据

| 检查 | 实际结果 |
| --- | --- |
| 规范化四 env 活动 key/value SHA256 前后对比及逐 key digest | exit0；四文件相同，角色数组和顺序相同；证据仅 key 与 digest，不输出真实值 |
| 当前活动数组与 README 旧历史角色数组比对 | exit0；宿主机 20/14 成员及顺序相同；Docker 历史 `{}` 与原空对象保存一致 |
| README pair JSON 历史对象 | exit0；两对象分别等值，未混合 host/Docker 场景 |
| 四 env 自然语言注释 ASCII / 英文及真实 env 指定历史注释不存在 | exit0；同 key 注释一致，无活动旧 key，无新增配置来源 |
| README pair 对所有当前活动 key 和可选 OPEN_BROWSER 覆盖 | exit0；13+1 项完整，brand 未消费说明明确 |
| frontend 源码/现有配置工具链文件前后 SHA256 | exit0；96 文件相同，r3 没有行为变更 |
| README pair 本地 Markdown target 检查 | exit0；6 个本地目标存在 |
| `git check-ignore frontend-js/.env frontend-js/.env.docker.dev` | exit0；两真实 env 仍被忽略 |
| `git diff --check` | exit0 |

- 脱敏证据：`/private/tmp/arch-fe002-r3-before.json` 与 `/private/tmp/arch-fe002-r3-after.json` 包含相同活动配置/逐 key checksum 与 source checksum；不保存真实 env 值或全文件副本。QA 可独立重新计算当前 key/value 与 before 比较。
- 临时检查脚本 `/private/tmp/arch-fe002-r3-check.py` 最终 exit0；首次检查脚本误用非 multiline 正则读取整文件，造成空映射假失败，修正为逐行读取后验证通过，未改产品配置值。
- 编辑脚本 `/private/tmp/arch-fe002-r3-edit.py` 无真实 env 值，仅配置用途描述及白名单 pageId-only 历史处理；未复制真实地址/密钥。
- 本轮没有运行 build/browser/API/Docker，注释与文档范围通过 checksum/JSON/links/diff 足够验证；r2 功能证据仍保留。

## r3 Developer handoff

- 精确对象：ARCH-FE-002 owner-approved r3，当前共享 main 未提交工作树；仅上述七个允许文件的新注释/文档改动。
- Development self-check 通过，`developer_handoff`；fresh-context Verification 可按 AC-r3-001～004 独立复核并更新 checklist 当前 r3 元数据，保留 r2 verdict/证据。
- 真实 host 配置仍含未迁入 pageId，因此不能据本轮文档收尾宣称 dev/build 可运行。真实业务 API、部署、Git 发布、001 final acceptance 均不在本轮范围。
- 不授予 QA verdict 或 Human Owner acceptance；r3 verdict 由独立 Verification 记录，最终验收由 Human Owner 决定。

# r4 Development self-check 与精确 handoff（2026-10-09）

## 批准与执行范围

- 完整读取 owner-approved ARCH-FE-002 r4、既有 tasks 与 r2/r3 checklist；只实施 r4 当前 allowlist。Owner 明确授权补回冻结前端五项品牌功能，并将真实宿主机授权过滤到当前页面测试；不是未经批准清理原记录。
- 冻结来源固定 `vibe-l2-front-end/frontend-next-js/src/config/brand.js` 与 `src/components/shell/BrandLogo.vue`；仅移植通用逻辑。原 demo SVG 审核为无外部引用的 NEXO 通用身份路径，未复制客户 `2020-logo.png` 或其他图片。
- 写入前保存脱敏逐 key hash、README 原历史 JSON hash 和源码基线；未复制整份真实 env/私有值到证据。r2/r3 的历史全文以上保留，QA checklist 由独立 Verification 更新。

## 改动文件与内容

- `frontend-js/src/config/brand.js`：Vite glob 只读取已打包 `src/assets/brand/*`，导出五 key 解析结果供现有 BrandLogo 使用。
- `frontend-js/src/config/brandOptions.js`：薄纯 helper 用于有意义 Node 验证，限制只按文件名查找本地资产；缺失/未知/路径/URL/穿越回退中性 demo。对齐 left/center/right 默认 center；三段 glow 支持 light/high-light/accent/none、空白/大小写规范化和 hight-light 别名，默认 light/accent/accent。
- `frontend-js/src/components/shell/BrandLogo.vue`：沿冻结旧组件恢复自然比例 contain、三段 glow 和 ResizeObserver；img alt 沿用 `common.systemTitle`，消费者 login/MainLayout 和全局 theme 不变。
- `frontend-js/src/assets/brand/demo-organization-logo.svg`：仅通用 fallback SVG，路径 header 同步当前 frontend-js；无客户资产。
- `frontend-js/tests/module-registry/brand-options.test.mjs`：文件名存在/不存在/缺失/非法路径和 URL，alignment 三值/invalid/default，三段四值/别名/规范化/default 的 Node 合同矩阵。既有 test:modules glob 已自动包含，不改 package.json 或依赖。
- `frontend-js/.env`：原数组与当前活动非 admin-only leaf pageId 取交集；保持原顺序，supervisor 20→3（dashboard.home、plan.list、system.user），operator 14→2（dashboard.home、plan.list）。仅这两 key 值变化，其余五品牌/mock/API/全部设置逐 key hash 相同。
- `frontend-js/.env.docker.dev`：原 0/0 不变，无品牌 key 也不强制新增。两真实 env 继续 Git ignored，品牌相关用途注释改为当前已支持语义，英文注释保持。
- `frontend-js/.env.example` / `.env.docker.dev.example`：增加五品牌 key 中性默认及短英文说明；无真实地址/客户资产，原权限安全空数组不变。
- `frontend-js/Dockerfile`：仅五品牌 ARG/ENV 默认增加 demo SVG、center、light/accent/accent，不改拓扑、依赖或执行 Docker。
- `frontend-js/README.md` / `README.zh-CN.md`：品牌段由 unused 更新为实际支持值、默认/安全资源回退/历史 alias/主题语义/打包要求；当前活动权限改写为3/2及Docker0/0，原历史20/14 JSON与Docker{}逐块 hash 相同。
- `CODE_INDEX.md`：仅新增真实品牌配置、组件、资源、测试入口索引。
- 本 `tasks.md` 当前 r4 元数据及本节。未改 spec/checklist、权限 helper、其他六模块、backend、DB、Compose、Nginx、login/MainLayout、global theme；无 Git 写与部署。

## DEV 实测与结果

| 检查 / 命令 | 退出码与证据 |
| --- | --- |
| `node /private/tmp/arch-fe002-r4-env.mjs` | 0；host两数组取 Registry 有效 leaf 交集，20/14→3/2；其他 key hash 相同，Docker unchanged |
| `pnpm --dir frontend-js check:access --mode development` | 0；supervisor3/operator2 |
| `pnpm --dir frontend-js check:access --mode production` | 0；supervisor3/operator2 |
| `pnpm --dir frontend-js check:modules` | 0；dashboard/plan/system，5 records、3 groups |
| `pnpm --dir frontend-js test:modules` | 0；21组全部通过，含3组品牌解析矩阵；日志 `/private/tmp/arch-fe002-r4-tests.log` |
| `pnpm --dir frontend-js build --outDir /private/tmp/arch-fe002-r4-real-dist` | 0；2195模块，真实.env值读取，未修改mock/API值。仅临时输出，非部署产物；既有chunk/outDir提示保留 |
| 真实有限 dev：`pnpm --config.verify-deps-before-run=false dev --host 127.0.0.1 --port 5195`（frontend-js目录） | Vite ready192ms；获监听审批后session89071立即Ctrl-C，正常人工停止包装exit130。只验证启动，不打开页面/登录/API；一次性verify-deps override避免pnpm依赖状态自动安装，不改项目配置或依赖 |
| 公开隔离 `pnpm --config.verify-deps-before-run=false run build --mode center --outDir /private/tmp/arch-fe002-r4-isolated-dist` | 0；已装依赖链接，未安装；fixture排除真实env，日志 `/private/tmp/arch-fe002-r4-isolated-build.log` |
| `python3 /private/tmp/arch-fe002-r4-check.py` | 0；实际逐key仅host两数组不同，brand等其它值相同；原历史JSON hash相同、sup3/op2原顺序；四env英文说明、五模板/Docker默认及文档目标通过；94个不在本轮品牌变更内的源码/工具链基线文件相同 |
| `git check-ignore frontend-js/.env frontend-js/.env.docker.dev` | 0；两真实文件仍忽略 |
| `git diff --check` | 0 |

写入前 `/private/tmp/arch-fe002-r4-env-before.json` 为逐 key SHA256 与 README 历史块 SHA256；
迁移后 `/private/tmp/arch-fe002-r4-env-after.json`，收尾后 `/private/tmp/arch-fe002-r4-env-final.json`；
`/private/tmp/arch-fe002-r4-source-before.json` 为源码基线。均无真实值/地址/整份 env。QA 可独立重算。

## Development 浏览器证据（由主协调者实测，不是 QA）

- 当前工具无 CUA/browser，按 frontend-testing-debugging skill 的可用替代路径使用项目外已安装 Playwright 和系统Chrome headless；sandbox listen/browser限制按工具审批处理，未装项目依赖。
- 主协调者自建公开 `/private/tmp/arch-fe002-r4-browser-fixture`，center5196、left5197、right5198；阻止所有非loopback请求，仅public mock，不使用真实env/后端凭据。
- Desktop1280×800、mobile390×844；自然图片300×150、contain160×80，224px容器内left/center/right偏移0/32/64。存在资产、路径拒绝与missing filename回退均正确；hight-light空白/大小写别名为high-light，三段光晕含none映射正确，light主题隐藏/dark显示grid。
- mock admin登录后sidebar图片加载，移动端图片可见；每context零pageerror/console error。转场禁用后协调者目视夜间登录与壳层截图，Logo/glow正常无白屏。
- `node /private/tmp/arch-fe002-r4-browser.cjs`: exit0。证据 `/private/tmp/arch-fe002-r4-browser-dev.md`、`browser-result.json`；截图同前缀 `center-light.png`、`center-dark.png`、`left-light.png`、`left-dark.png`、`right-light.png`、`right-dark.png`、`mobile.png`、`shell.png`。
- 此前本人临时fixture监听工具审批长时间等待并被中断；已保留进度，恢复后未重做已完成源码/权限。协调者接手浏览器fixture；真实build与有限dev如上已完成，无持续真实dev服务。

## 精确 r4 Developer handoff

- ARCH-FE-002 owner-approved r4，当前共享 main 未提交工作树，状态 `developer_handoff`；只以上allowlist写入。
- r4 AC所需 DEV checker/tests、真实有限dev/临时build、隔离build/browser、脱敏配置差异/历史保存、doc/diff检查通过。按scope独立fresh-context Verification复核后更新checklist，r2/r3历史verdict保留而非继承。
- 可测试当前前端启动与构建；没有验证真实登录/业务API/CRUD/XLSX/设备，不进行生产部署、Docker操作或Git发布。不将DEV结果授予QA verdict、Owner final acceptance或001 final acceptance。
- 保留/private/tmp所有review证据；parent拥有三个公开browserfixture服务器，可供QA复核后由创建者停止，实际env仍用户原文件。本人真实5195启动服务已经停止。
