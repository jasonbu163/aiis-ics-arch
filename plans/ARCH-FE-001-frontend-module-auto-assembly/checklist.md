# ARCH-FE-001 独立 Verification

Task ID: ARCH-FE-001
Revision: r3
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: 第二轮 fresh-context Verification 通过 r3；交 Human Owner final acceptance，第一轮失败历史保留于 §1–5

以下 §1–5 为第一轮 qa_failed 的原始历史；当前有效 verdict 与第二轮证据见 §6。

## 1. 验证依据与对象

- 日期：2026-09-07；Execution Mode: `agent_team_same_session`。
- Verification 由 coordinator 在 Development `developer_handoff` 后独立派发；未继承 Development 对话推理。
  读取 approved r3 spec、tasks、实现、diff、测试和仓库契约；profile 为 contract_only，不宣称平台 ACL。
- 验证目标：`HEAD=d85604a88ade5a6c86e77abaafa96de267515479` 上的当前未提交 r3 工作树。
  `v1.0.0^{}` 复核为 `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`；ARCH-001 checklist 为 `owner_accepted`。
- 完整读取根 AGENTS/README/PLAN、frontend README/PLAN、模块 README pairs、任务三文件现存内容、
  verification profile 与 lifecycle workflow；使用 project-governance、frontend-ui/FRAMEWORK、
  i18n-workflow、code-document-indexer 规范审核，未修改实现、spec、tasks 或索引。
- `git status --short --untracked-files=all` 显示 Development 集合与 tasks §3 一致，全部属于 spec §10
  allowlist；另有 PM 的 spec diff。QA 唯一仓库写入是本 checklist。

## 2. 环境与独立执行证据

环境：macOS、Node `v22.19.0`、pnpm `11.11.0`，复用既有安装依赖。QA 没有再次安装依赖；
`pnpm install --frozen-lockfile` 的安装事实来自 Development 记录，不冒称 QA 独立执行。

| 命令 / 检查 | 独立结果 |
| --- | --- |
| frontend-js 内 `pnpm --config.verify-deps-before-run=false test:modules` | exit 0；12 tests、12 pass、0 fail |
| `git diff --check` | exit 0 |
| `git diff --exit-code HEAD -- frontend-js/pnpm-lock.yaml` | exit 0 |
| Node 对比 HEAD/current package version、dependencies、devDependencies | exit 0；三者均一致；package diff 只新增验证 scripts |
| `rsync -a --exclude='/.env*' --exclude='/dist' frontend-js/ /private/tmp/arch-fe-r3-qa.h5fAh0/` | exit 0；QA 自己创建隔离副本，不复用 DEV 构建产物 |
| Node 检查副本根 `.env*` 名称 + 源码逐文件字节比对 | exit 0；没有 `.env*`；87 个非依赖/非 dist 文件与当前源码相同 |
| 副本 `pnpm --config.verify-deps-before-run=false build` | exit 0；prebuild active=[system]、routes=2、groups=1；Vite 1577 modules，2.19s |
| 仅副本把 system `enabled: true` 改 false，执行同一 build | 预期 exit 1；`Required module must declare enabled: true: system`，未启动 Vite；随后恢复副本 true |
| Node `loadRegistry` + 实际 Vue I18n 切换 | exit 0；en-US: System / User Management / Profile；zh-CN: 系统设置 / 用户管理 / 个人资料 |
| 独立 Node + 已安装 Vue Router memory history 对抗探针 | exit 0 完成观察；复现下列三项实现缺陷，不能据命令 exit 0 判定通过 |

副本恢复后重新逐文件比对通过；按相对路径及字节累计的源码 SHA256：
`7704afa7cc5977bf46a7d02a214dbed2e103fe44f927bea5e010655df43d4a69`。
Vite 保留 500 kB chunk 警告（Element Plus 1,048.64 kB）；未改变打包策略。

## 3. 阻断项与重现

### QA-001 — P1：合法 legacy 可选参数被拒绝，破坏已承诺的 route 兼容

- 位置：`frontend-js/src/app/moduleManifest.js:91`。
- `path: 'legacy/:id?'` 是已安装 Vue Router 可解析的 route；独立 `router.resolve('/legacy')` 与
  `router.resolve('/legacy/42')` 都返回 `Optional`。Registry 却抛出
  `[module-registry] Invalid route path: legacy/:id?`，因为把参数修饰符 `?` 一概当非法字符。
- 影响：原有详情/编辑可选参数 route 即使不进入菜单，也不能通过新 checker / prebuild。
  违反 §8 legacy compatibility、AC-003/004；当前不能给出兼容 minor recommendation。
- 返工：保留合法 Vue Router 参数语法与隐藏参数 route 的权限/导航行为；增加正向回归，并继续拒绝真正非法 URL/schema。

### QA-002 — P2：空默认子路由的冲突检测被整体跳过

- 位置：`frontend-js/src/app/moduleManifest.js:97-98`。
- 同一父路径 `legacy` 下，两个子记录都声明 `path: ''`，各自拥有不同 name/pageId，Registry 接受，
  产生 `First -> /legacy` 与 `Second -> /legacy` 两个同 URL leaf。
- 父记录与唯一默认子记录共用 URL 是合法结构，但不能因此豁免所有空路径 sibling；此处违反 AC-007。
- 返工：保留父子默认 route 的合法共用路径，同时拒绝重复默认 leaf，加入负向测试。

### QA-003 — P2：父 alias 派生的子路径没有进入全局冲突集合

- 位置：`frontend-js/src/app/moduleManifest.js:103-106,115`。
- `base` 父记录有 `alias: '/shortcut'`，子记录 `list` 名称为 `Aliased`；另一个 direct route 为
  `shortcut/list`，名称为 `Direct`。Registry 接受二者；Vue Router 实际解析 `/shortcut/list`
  得到 `Aliased`，但 `resolve({ name: 'Direct' }).fullPath` 也为 `/shortcut/list`。
- 影响：菜单/default path 可以指向不同记录实际占据的 URL，造成错误页面/拒绝访问；不代表 backend 授权被绕过。
  违反 AC-007 的 path collision gate。
- 返工：把嵌套 alias 派生路径纳入冲突分析，保留不冲突的 aliases，增加跨模块同类负向回归。

可在 frontend-js 中执行以下无 I/O fixture（Node stdin，未写仓库测试文件）重现：

```js
import { createModuleRegistry } from './src/app/moduleManifest.js'
import { createRouter, createMemoryHistory } from 'vue-router'
const assemble = routes => createModuleRegistry(
  { '/app/legacy/manifest.js': { default: { name: 'legacy', routes } } },
  {}, { 'en-US': {}, 'zh-CN': {} }, { requiredModules: [] })
const router = routes => createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: routes }] })
const optional = [{ path: 'legacy/:id?', name: 'Optional', component: {}, meta: { pageId: 'legacy.detail' } }]
console.log(router(optional).resolve('/legacy').name, router(optional).resolve('/legacy/42').name)
try { assemble(optional) } catch (e) { console.log(e.message) }
const empty = [{ path: 'legacy', component: {}, children: [
  { path: '', name: 'First', component: {}, meta: { pageId: 'legacy.first' } },
  { path: '', name: 'Second', component: {}, meta: { pageId: 'legacy.second' } }
] }]
console.log(assemble(empty).routeRecords.map(r => [r.name, r.path]))
const alias = [{ path: 'base', alias: '/shortcut', component: {}, children: [
  { path: 'list', name: 'Aliased', component: {}, meta: { pageId: 'legacy.a' } }
] }, { path: 'shortcut/list', name: 'Direct', component: {}, meta: { pageId: 'legacy.b' } }]
console.log(assemble(alias).routeRecords.map(r => [r.name, r.path]))
console.log(router(alias).resolve('/shortcut/list').name, router(alias).resolve({ name: 'Direct' }).fullPath)
```

## 4. AC 审核

| AC | 结果 |
| --- | --- |
| AC-001 | 通过：exact r3 approval、基线、角色 allowlist 与 developer_handoff gate 可核对 |
| AC-002 | 通过：单一纯 Registry 规范化，Vite discovery 唯一；router/menu/i18n 消费 output |
| AC-003/004 | 不通过完整兼容条件：四 consumer 普通 fixture 与 enabled/system gate 通过，但 QA-001 阻断 legacy route |
| AC-005 | 通过：共享变更移除具体菜单/pageId 硬编码；壳层 system/user 文案按 r3 保留 |
| AC-006 | 已测基本 provider 矩阵通过：admin、page grant、requiresAdmin、unknown/malformed、disabled/orphan；未做浏览器登录/真实服务授权验证 |
| AC-007 | 不通过：简单重复 name/path/pageId/namespace/schema/title 负向通过，但 QA-002/003 漏检实际 path 碰撞 |
| AC-008 | 通过：system 必需、route name/path/pageId 两条兼容；system/user 双语原文件保留，实际 I18n 切换通过 |
| AC-009 | 通过源码/构建：aiis_demo 默认 false、页面无外部 I/O、使用双语；不声称 disabled 源码不被扫描 |
| AC-010 | 手册结构/ownership/restart/rebuild/复制删除步骤齐全；兼容和冲突承诺尚受上述实现缺陷阻断 |
| AC-011 | 既有 12 tests/checker/build、dependency/lock gate 通过；扩展对抗矩阵失败，不代表整体实现合格 |
| AC-012/015 | 通过本轮 diff/操作审计：未超出允许前端结构，无其他业务实现迁移，无外部系统/Git 写入 |
| AC-013 | 通过角色证据：本独立 checklist 记录真实 qa_failed；不能用 tasks self-check 代替 QA |
| AC-014 | 通过边界：未发布精确版本；兼容性结论暂不成立，SemVer 待修复、重新 QA 与 Human Owner acceptance |

## 5. Verdict、限制与下一 gate

正式 verdict：`qa_failed`。Development 修复三项后更新其 tasks 与 handoff，由 coordinator 启动新的
fresh-context Verification；保留本轮失败历史和回归证据。没有修复任何源码，不擅自扩大 r3 allowlist。

未运行浏览器、mounted menu DOM/点击、桌面/窄屏截图、真实登录；检测到确定缺陷后返回返工，不将这些
未执行项包装为通过。后续 QA 仍应补足实际菜单验证。未读取真实 `.env`，未运行 backend/API/DB/PLC/CA、
Docker、发布或任何 Git/GitHub 写操作。产物只在上述 QA `/private/tmp` 副本。

Human Owner final acceptance：pending；本 verdict 不授权发布、部署、版本 refs 或生产操作。

## 6. 第二轮 fresh-context Verification（2026-09-07）

### 6.1 对象、独立性与角色边界

- 当前正式 verdict：`qa_passed`；仅针对批准的 `aiis-ics-arch::ARCH-FE-001 r3` 源码装配范围。
- coordinator 在 tasks §7 重新 `developer_handoff` 后启动全新 Verification 上下文；本执行者是显式
  指派 Verification 职责的子 Agent，不宣称命名 custom role 激活或平台 ACL，也不继承 Development 推理。
- 完整读取根 AGENTS/README/PLAN pairs、frontend README/PLAN 与 app README pairs、r3 三文件、
  verification profile、lifecycle workflow；按 project-governance、frontend-ui/FRAMEWORK、
  i18n-workflow、code-document-indexer 只审不修。
- 独立复核 HEAD 仍为 `d85604a88ade5a6c86e77abaafa96de267515479`，tag peeled commit 仍为
  `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`；ARCH-001 为 `owner_accepted`。
- `git status --short --untracked-files=all` 逐路径对照 spec §10：Development diff/新增文件均在精确
  allowlist 内，另有 PM spec 和 QA checklist；未发现 backend、其他业务模块、Compose、版本或 lock 变更。
  本轮唯一仓库写入为 checklist；QA 临时 fixture 不改变仓库源码。

### 6.2 独立命令与证据

环境：macOS、Node `v22.19.0`、pnpm `11.11.0`；复用已安装依赖，未重新安装或添加依赖。
frozen install 事实仍只引用 tasks 的 Development 安装记录，不冒称本轮独立安装。

| 命令 / 检查 | 本轮结果 |
| --- | --- |
| frontend-js 内 `pnpm --config.verify-deps-before-run=false test:modules` | exit 0；15 tests / 15 pass / 0 fail |
| `node scripts/check-module-manifests.mjs` 与 `node scripts/check-module-manifests.mjs --check` | 均 exit 0；裸调用只有帮助；check 为 active=[system]、routes=2、groups=1 |
| `git diff --check`；`git diff --exit-code HEAD -- frontend-js/pnpm-lock.yaml` | 均 exit 0 |
| Node 对比 HEAD/current package 的 version、dependencies、devDependencies | exit 0；全部相同；package diff 仅新增验证 scripts |
| Node 逐路径匹配 spec Development allowlist、检查六份 frontend/app 双语文档相对链接、共享入口业务 route/pageId 残留扫描 | exit 0；无越界、断链或具体业务路由/pageId 残留；保留已获批的 system/user 壳层翻译引用 |
| `rsync -a --exclude='/.env*' --exclude='/dist' frontend-js/ /private/tmp/arch-fe-r3-qa2.Gd1NNc/` | exit 0；独立 QA 副本，不采用 DEV dist 作为构建证据 |
| Node 对当前源码、QA 副本及 DEV `/private/tmp/arch-fe-r3.R829xG` 逐文件字节比对 | exit 0；87 个非依赖/非根 dist/非根 .env 文件一致；QA 根目录无 `.env*` |
| QA 副本 `pnpm --config.verify-deps-before-run=false build` | exit 0；prebuild 通过，Vite 1577 modules，2.26s |
| 仅 QA 副本将 system enabled 改 false 后执行同一 build | 预期 exit 1；`Required module must declare enabled: true: system`；未进入 Vite，随后恢复副本 true |
| Node stdin 独立 Vue Router memory-history 正反向探针 | exit 0；三项返工及扩展的相关合法结构通过，见 §6.3 |
| 实际 ModuleNavigation SFC 编译 + Vue custom-renderer 离线挂载 + 实际 Registry/I18n | exit 0；EN/ZH 响应切换、admin 两 leaf、授权用户一 leaf、未知 provider 零 group，通过；边界见 §6.4 |

源码按相对路径及文件字节累计 SHA256：
`138bdfbba4ef58c8527638b78c0fee244a6f05412c6fa3de6304cbf54daac4a8`。
Vite 仍有 vendor chunk 大于 500 kB 的警告（Element Plus 1,048.64 kB）；不是 build failure。

本轮验证工具修正也保留：首次比对/依赖审计命令误在无 `.git` 的 QA 副本执行，Node 因 git show
退出 1（内部 git exit 128）；该次不计通过，改在实际 frontend-js 重跑后上述 87-file/依赖审计通过。
首次挂载探针直接 import `@vue/compiler-sfc` 退出 1，因为 pnpm 未在项目根暴露该传递依赖；改用已安装
Vue 的 `vue/compiler-sfc` 公共入口后成功，没有安装依赖。shell 偶有 `/bin/ps: Operation not permitted`
启动提示，不影响已列 Node/pnpm 检查的实际退出码。

### 6.3 第一轮缺陷闭环与 AC 审核

| 项目 | 第二轮独立结果 |
| --- | --- |
| QA-001 | closed：`legacy/:id?` 的 `/legacy`、`/legacy/42` 均解析为 Detail；另测可选自定义数字正则、`*`/`+` 重复参数；保留可访问而不进入菜单/default；静态 query/hash 仍拒绝 |
| QA-002 | closed：父 route + 唯一默认空 child 保留；进一步测试带两条父 aliases 的嵌套唯一空 child，三个 URL 均解析到 Default；同父两个空 sibling 明确抛 Duplicate route path |
| QA-003 | closed：父 aliases 派生 descendant URL 冲突拒绝；进一步测父多 alias + 中间相对子 alias，`shortcut/section/list`、`alt/area/list`、`base/area/list` 与 direct route 均在两种输入顺序下拒绝；无冲突结构仍通过 |
| AC-001/013 | 通过：exact approval、基线、r3、Execution Mode、角色边界和本次独立 re-handoff/checklist 均可核对；最终验收未代签 |
| AC-002 | 通过：单一纯 normalize/validate/sort 与 Vite discovery，router/menu/i18n 消费相同 Registry；Node checker 只负责输入读取 |
| AC-003/004 | 通过：现有矩阵 add/remove/disabled 同时影响四 consumer；system 必需性及 prebuild 负向通过；legacy、无 navigation、稳定排序及返工 route 兼容通过 |
| AC-005/006 | 通过源码/离线矩阵：共享具体业务 menu/pageId 硬编码移除；provider/admin/requiresAdmin/unknown/malformed/orphan 过滤一致，不授予 backend 权限；mounted 菜单权限响应通过 |
| AC-007 | 通过：重复 name/route/path/pageId/namespace、非法 schema、动态可见 route、双语 key 与新旧 title 规则；原 QA-002/003 漏检已关闭 |
| AC-008/009 | 通过：两条 system route name/path/pageId 保持不变；system/user 双语仍解析；aiis_demo 默认 false、无外部 I/O，未迁移账号 UI |
| AC-010 | 通过：双语手册包含稳定结构、从零/复制/禁用/删除、API facade/mock/permission 归属、legacy 与跨模块依赖边界、dev restart、production rebuild；相对链接检查通过 |
| AC-011 | 通过：15 tests、checker、隔离 production build；没有 dependency/version/lock 修改 |
| AC-012/015 | 通过 diff/操作审计：模块垂直结构保持；无其他业务实现迁移，无 backend/Compose/Git/version 修改或外部系统操作 |
| AC-014 | 通过边界：兼容测试支持功能性 minor recommendation，但不固定精确 SemVer；不代表任何版本已发布 |

### 6.4 Acceptance Audit、限制与下一 gate

- 本轮覆盖源码装配、静态检查、真实 Vue Router memory resolve、离线权限与语言响应、生产编译。
  mounted 检查实际编译并挂载当前 `ModuleNavigation.vue`，使用当前 Registry 与 Vue I18n，在
  `nextTick` 后验证 EN/ZH 文本、两级 group/leaf index 与权限变化；真实 icons 也由现有包提供。
- custom-renderer 是内存 host；Element Plus `ElSubMenu/ElMenuItem/ElIcon` 外壳为保留 slots/attrs 的
  测试 stub。它不是浏览器 DOM、Element Plus 点击/展开集成、CSS 布局或桌面/窄屏截图验收。
  未运行真实浏览器、完整 MainLayout mount、登录或真实后端授权流程，不把这些未运行项写为通过。
  本 r3 不重做视觉/响应式；本 verdict 限定于其源码装配 AC，不宣称端到端或现场 UI 验收完成。
- 未读取真实 `.env`，没有 API/DB/PLC/CA、Docker、Git/GitHub 写操作、发布或部署；验证产物只在
  `/private/tmp/arch-fe-r3-qa2.Gd1NNc`，实际工作树未产生 dist。临时 system 禁用 fixture 已恢复。
- 第一轮正式 `qa_failed` 和 QA-001/002/003 证据完整保留；本节的第二轮 `qa_passed` 是当前有效 QA verdict。
- 下一 gate：Human Owner final acceptance（pending）。精确版本与发布、部署、Git refs 和真实环境操作
  仍需单独批准；本 Verification 无权最终接受或授权这些动作。
