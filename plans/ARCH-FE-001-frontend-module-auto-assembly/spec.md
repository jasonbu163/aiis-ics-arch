# ARCH-FE-001 Frontend Module Auto Assembly — PM Spec

Task ID: ARCH-FE-001  
Revision: r3
Status: owner_approved
Owner Role: PM  
Allowed Writers: PM, Human Owner  
Handoff: Human Owner approved exact r3; Development may start within §10 allowlist

Task Namespace: aiis-ics-arch  
Classification: root  
Capability: Frontend manifest-driven route, navigation, locale and access-filter assembly  
Owner: frontend-js module framework  
Blocked By: ARCH-001  
Target Version: deferred; exact SemVer is decided only after implementation, compatibility verification, fresh-context QA and Human Owner final acceptance, before any separate release action  
Acceptance Chain Reference: ARCH-FE-001 PM spec -> ARCH-001 owner acceptance -> immutable Core baseline -> baseline audit -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context QA checklist.md -> Human Owner final acceptance -> separate version/release decision  
Execution Mode: agent_team_same_session  
Created: 2026-08-08  
Updated: 2026-09-07

Revision History:

- `r3`：基于已接受的 `v1.0.0` 复核，明确 system 为不可禁用的必需 Core 模块；旧 manifest
  保留全局标题 key 兼容，新格式采用模块内标题 key。其余范围、角色级 allowlist 与版本延后决定不变。
  Human Owner 本轮仅授权修订 spec，不构成 Development 批准。
- `r1`：在 Core 拆分前固定 route、navigation、locale 与 access-filter 统一装配方向，并将 Development
  阻塞在 `ARCH-001` 和首个稳定基线之后。
- `r2`：Human Owner 明确暂不固定版本号；本 Revision 将稳定的 `src/app/<module>` 结构、Core-only
  升级边界、模块新增/删除行为、build-time 重启/重建语义、权限提供者边界、角色级 allowlist、风险与
  rollback 固定为后续执行依据。精确 SemVer 延后到实现、兼容性验证、fresh-context QA 和 Human Owner
  final acceptance 之后决定。

## 1. PM 结论

`ARCH-FE-001` 是独立于 `ARCH-001` 的前端架构能力任务。它把当前已经存在的 route manifest 与
module-local locale 自动发现扩展为可复用的模块装配合同，使符合规范的
`frontend-js/src/app/<module>/` 在不修改共享 router、MainLayout 或全局 locale 汇总文件的情况下，
可以按 manifest 决定是否启用、注册路由并生成侧边栏导航。

本任务不承担去 Vibe L2 化、staging 清理或首个 Core 基线提取。`ARCH-001` 只需删除旧业务模块在共享
文件中的残留并形成可构建的 system/Core 壳；不得提前实现本 spec。

本任务是接受后的 Core 基线上新增的前端装配能力，不是业务模块结构迁移。精确版本号不是 Development
输入，也不在本 PM 阶段预先承诺；只有实现、compatibility tests 和 fresh-context Verification 完成后，
Human Owner 才在独立版本/发布决定中确定 SemVer。

## 2. 启动前置 gate

Development 必须同时满足：

1. `aiis-ics-arch::ARCH-001` 已完成 fresh-context QA 和 Human Owner final acceptance；
2. 首个 Core 的 immutable baseline identifier 已记录；它可以是 accepted source record、commit 或后续
   单独批准的 tag，不要求本 spec 现在固定版本号；
3. PM 基于该 baseline 重新检查本 spec 的文件路径、manifest 现状和 allowlist；
4. 如 baseline 与本 Revision 有 material drift，先形成新 Revision；
5. Human Owner 对最终 Revision 使用精确批准语句。

现在创建 r3 只用于固定 PM 范围，不能据此创建 `tasks.md`、`checklist.md` 或修改 frontend 源码。

## 3. 当前事实

当前 frontend-js 已具备：

- `src/router/index.js` 通过 `import.meta.glob('../app/*/manifest.js')` 自动发现模块 routes；
- `src/locales/index.js` 通过 `import.meta.glob('../app/*/locales/*.json')` 自动合并模块 locale；
- route guard 按 `meta.pageId`、`requiresAdmin` 和用户页面访问列表 fail closed；
- 模块手册已经明确 `src/app/<module>` 的垂直目录所有权。

当前尚未具备：

- `MainLayout.vue` 当前只硬编码 Core system 菜单、图标和 `pageId` group；
- router、menu 与 locale 各自发现，缺少一个可复用、可验证的 normalized module registry；
- manifest 没有正式的 `enabled` 和 navigation schema；
- disabled module 不能以统一合同同时退出 route、menu、default redirect 和 module locale；
- 新模块仍需修改共享 MainLayout，尚未达到“只写模块目录即可接入”的目标。

2026-09-07 baseline audit：`ARCH-001 r3` checklist 已为 `owner_accepted`；immutable baseline 为
annotated `v1.0.0`，peeled commit 为 `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`。
当前 `main` 为 `d85604a88ade5a6c86e77abaafa96de267515479`，与该 tag 的差异仅为六个发布验收文档，
`frontend-js/` 无差异。现有写入路径适用；Registry、离线示例和测试为计划新增路径。
本轮只读复核未运行构建。Development 启动前仍需核对实际基线是否变化。

两项规则偏差由本 r3 收敛：壳层依赖 system 提供的 `system.*` / `user.*` 语言包；旧 system manifest
使用全局 `breadcrumb.*` 标题。另有默认跳转只检查 pageId、未检查 requiresAdmin 的现状，继续在既有
统一权限过滤范围内处理。

### 3.1 稳定模块结构与 Core 边界

以下结构作为本任务的稳定输入，不在本任务重新设计：

```text
frontend-js/src/app/<module>/
├── api/                       # 模块 API facade 与可选诊断 mock
├── views/<page>/index.vue     # 页面入口
├── components/                # 可选模块内复用组件
├── locales/<locale>.json      # 模块文案
└── manifest.js                # route/menu/permission metadata
```

- 本任务不移动、重命名或重构业务模块的 `api/views/components/locales`，也不修改业务页面和业务 API；
- `frontend-js/src/app/moduleManifest.js` 与 `moduleRegistry.js` 是共享 composition infrastructure，虽位于
  `src/app/`，但不是 `src/app/<module>/` 业务模块；
- `system` 只补充 canonical manifest/locale 合同，`aiis_demo` 只作为默认关闭、无外部 I/O 的离线样例；
- `system` 是不可禁用、不可删除的必需 Core 模块；其 `system.*` / `user.*` 文案继续供公共壳层使用，
  不迁移账号 UI 或语言包。下文模块禁用/删除语义仅适用于可选模块。
- 其他业务模块继续归 consuming project 或 modules 仓，不进入本任务 write scope；
- 新合同生效后，模块只需在自己的目录内提供完整 manifest；共享 Core 不再为具体模块添加硬编码入口。

## 4. 成功目标

完成后应满足：

1. 新规范模块只需新增或复制 `src/app/<module>/`，不修改共享 router、MainLayout、权限解析器或全局
   locale loader；
2. 单一 normalized registry 同时提供 active manifests、routes、navigation model 和 active module
   names；
3. 可选模块 `enabled: false` 时不进入 route、menu、default redirect 或 module locale messages；
4. 新增一个完整可选模块目录后，经 dev server restart 可进入 route、menu、default redirect 候选与 module
   locale；删除整个模块目录后，上述四个 consumer 不留共享代码残余；production 始终需要重新 build；
5. 新格式 manifest 的 navigation 信息完全由模块拥有，共享布局不包含任何业务模块名、业务路径或
   业务 `pageId`；
6. menu/route 通过 consumer-supplied access provider 按 `pageId` 与 `requiresAdmin` 过滤；manifest 不声明
   role grants，前端隐藏不替代 backend API authorization；
7. 首版 navigation 固定为 `module group -> route leaf` 两级模型；无可访问 leaf 时不显示 group；
8. 旧 manifest 未声明新字段时仍保留原 route/locale 行为，不强迫现有项目一次性升级业务模块；
9. 模块重复 name、route name、path、pageId、locale namespace 或非法 schema 在 build/test 阶段明确失败；
10. 默认关闭的 `aiis_demo` 证明模块结构和 enabled gate，不连接 API、DB、PLC 或其他外部 I/O；
11. production build 和独立 module-registry contract tests 通过；
12. 兼容性 verdict 形成并完成 fresh-context QA 与 Human Owner final acceptance 后再决定精确 SemVer，
    本任务不创建 tag、release branch 或 hosted release。

## 5. Manifest 装配合同（release version deferred）

推荐的新模块 manifest 形态：

```js
export default {
  name: 'sample',
  enabled: true,
  order: 90,
  navigation: {
    titleKey: 'sample.navigation.title',
    icon: 'Menu'
  },
  routes: [
    {
      path: 'sample/list',
      name: 'SampleList',
      component: () => import('./views/list/index.vue'),
      meta: {
        titleKey: 'sample.list.title',
        pageId: 'sample.list',
        navigation: {
          visible: true,
          order: 10,
          icon: 'List'
        }
      }
    }
  ]
}
```

固定语义：

- `name`：与目录名一致的稳定 module ID；
- `enabled`：新模板必须显式声明 boolean；可选模块的 `false` 完全退出活动装配；
- 为保持向后兼容，旧 manifest 缺少 `enabled` 时按当前行为视为启用；非 boolean 值必须失败；
- `system` canonical manifest 必须显式 `enabled: true`；完整应用装配中缺失 system 或声明
  `enabled: false` 必须在 build/test 校验时明确失败，不得静默恢复或继续构建残缺壳层。
  system 必需性只属于 Core 装配约束，不豁免任何页面权限过滤，也不授权业务菜单硬编码；
- `order`：模块、路由和菜单的稳定排序事实，不作为权限或启用开关；
- `navigation`：可选。缺少时 route/locale 继续注册，但不会自动生成侧边栏 group；
- `navigation.titleKey` 必须指向模块自己的 locale namespace；
- route `meta.navigation.visible === true` 才生成菜单 leaf，避免详情页或参数路由被意外展示；
- 带动态参数的 route 不得声明 `visible: true`；详情/编辑 workflow 继续可路由但不进入菜单；
- 首版只生成两级导航；本任务不从 path、route name 或页面文件名猜测更深层菜单树；
- `icon` 是可选 presentation hint；未知图标使用通用 fallback，不要求修改共享 icon registry；
- `pageId` 是前端页面访问 key，不授予 backend API 权限；
- 新格式 manifest 的 module/route title key 必须归该模块拥有的 namespace，并在中英文 module
  locale 中存在；重复 namespace 必须明确失败；
- 为确定标题校验边界，未声明 `enabled`、模块 `navigation` 或 route `meta.navigation` 新字段的
  manifest 按旧格式处理：保留原有全局 title key（例如 `breadcrumb.*`），按双语全局与模块消息的
  实际解析结果校验，不因 key 不在模块 namespace 而拒绝。声明任一上述新字段即采用新格式标题规则；
- manifest 必须静态、无副作用，不调用 API、不启动 timer、不读取数据库或修改运行时状态。

## 6. 装配数据流

```text
src/app/*/manifest.js
  -> discover
  -> normalize + validate + stable sort
  -> active module registry
       ├── router routes + default authenticated redirect
       ├── sidebar navigation model
       └── active module names -> module locale filter
```

共享层只消费 normalized output。router、MainLayout 和 locale loader 不得分别复制 manifest 解析、排序
或 enabled 判断。

这是 Vite build-time/source-assembly 合同，不是运行时插件系统：新增或删除模块文件后，本地开发以重启
dev server 作为稳定发现边界；正式环境必须重新 build 和交付 dist。`enabled: false` 只保证模块不注册到
route/menu/default redirect/messages，不代表源码未被打包扫描，也不是安全隔离或授权边界。

## 7. 权限与安全边界

- Backend authorization 继续是安全权威；menu/route gate 只负责页面可见性和导航体验；
- Core 只消费通用 access provider，例如 `hasPageAccess(pageId)` 与当前用户的 admin 判定；它不把
  `VITE_ROLE_PAGE_ACCESS_JSON`、固定角色表或某个 backend 响应写死为唯一权限来源；
- consumer 可以从 backend 返回的权限结果或项目配置构造 access provider；缺失、未知或损坏输入继续
  fail closed；
- 非 admin 用户只有 access provider 允许对应 `pageId` 时才看到和访问 route；
- `requiresAdmin` route 即使 pageId 命中也只允许 admin；
- 模块 manifest 不声明 role grants，不自动扩权，也不修改账号/bootstrap 机制；
- disabled module 的 route 不得通过手工 URL 或 default redirect 访问；
- consumer 中残留的 orphan pageId grant 不得重新创建已删除模块的 route/menu；checker 可以报告残留，
  但本任务不自动修改 consumer 权限政策；
- menu 自动发现不得变成运行时远程代码加载或模块市场。

## 8. Compatibility rules

本任务以向后兼容的新能力为设计目标，但不预先固定 release number：

- 旧 manifest 的 `name/order/routes/meta` 继续有效；
- 缺少 `enabled` 时保持现有启用行为；
- 缺少 `navigation` 时不自动产生 menu，但 route/locale 行为不变；
- 旧格式的全局标题 key 继续有效；升级为新格式时同步把标题声明迁入模块 namespace，保留既有
  route name/path/pageId。system 在本任务内完成该标题升级，公共壳层原有文案 key 保持可用；
- 现有项目可逐模块补充 navigation 元数据，不要求一次性升级所有业务模块；
- Core system module 与 `aiis_demo` 必须在本任务内采用完整新合同，作为 canonical 示例；
- 删除模块只自动清除 Registry 的 Core consumers；其他模块中显式存在的 import、QuickLink、业务跳转
  或 API 依赖属于跨模块依赖，必须由 owning module 处理，Registry 不静默改写；
- 若实现要求旧 manifest 全部立即改写、改变既有 route/pageId 或删除 compatibility 行为，必须停止并
  重新评估兼容性和 SemVer，不能继续宣称兼容 minor upgrade。

## 9. 明确不做

- 不修改 backend、数据库、Alembic、seed、Control Agent、tools 或 contracts；
- 不实现 backend module registry 或跨前后端统一 manifest；
- 不自动生成或授予 role/page/API permissions；
- 不实现运行时启停 UI、远程模块下载、zip/plugin 安装或热插拔；
- 不实现任意深度菜单树、拖拽排序、用户自定义菜单或 per-project theme；
- 不自动改写其他模块中的显式 import、QuickLink、route push 或业务依赖；
- 不重做认证、账号 UI、MainLayout 其他视觉交互或响应式设计；
- 不连接真实 API/DB/PLC，不运行 Docker，不修改 Compose；
- 不修改 accepted Core baseline，不创建任何版本 tag、release branch 或 hosted release；
- 不修改 `ARCH-001` 的 spec/tasks/checklist、实现文件或 verdict；
- 不顺手清理 `ARCH-001` 遗留，发现基线未收敛时回到其 owner。

## 10. 角色级精确 write allowlist

本 r3 PM 阶段只允许写本 `spec.md`。它不授权创建 Development/Verification 文档或修改任何源码。

前置 gate 和 Human Owner exact Revision approval 完成后，Development 只可写：

- `frontend-js/src/app/moduleManifest.js`（新建：纯 normalize/validate）
- `frontend-js/src/app/moduleRegistry.js`（新建：Vite discovery 和 normalized exports）
- `frontend-js/src/router/index.js`
- `frontend-js/src/layouts/MainLayout.vue`
- `frontend-js/src/components/navigation/ModuleNavigation.vue`（仅实现通用菜单渲染时可新建）
- `frontend-js/src/locales/index.js`
- `frontend-js/src/config/permissions.js`
- `frontend-js/src/store/user.js`
- `frontend-js/src/main.js`（仅通用 icon fallback/注册确有需要时）
- `frontend-js/src/app/system/manifest.js`
- `frontend-js/src/app/system/locales/en-US.json`
- `frontend-js/src/app/system/locales/zh-CN.json`
- `frontend-js/src/app/system/locales/user.en-US.json`
- `frontend-js/src/app/system/locales/user.zh-CN.json`
- `frontend-js/src/app/aiis_demo/**`（新建；默认关闭、无外部 I/O）
- `frontend-js/src/app/README.md`
- `frontend-js/src/app/README.zh-CN.md`
- `frontend-js/scripts/check-module-manifests.mjs`（新建；无第三方依赖）
- `frontend-js/tests/module-registry/**`（新建；纯 contract fixtures/tests）
- `frontend-js/package.json`（仅新增验证 scripts，不改 dependency/version）
- `frontend-js/README.md`
- `frontend-js/README.zh-CN.md`
- `frontend-js/PLAN.md`
- `frontend-js/PLAN.zh-CN.md`
- `CODE_INDEX.md`（仅同步本任务新增/移动的真实源码结构）
- `plans/ARCH-FE-001-frontend-module-auto-assembly/tasks.md`

禁止修改 `pnpm-lock.yaml`、其他业务模块、root version/changelog、backend、Compose、Git 或来源仓。确需
新增依赖、路径或 acceptance surface 时停止并形成新 Revision。

`developer_handoff` 后，fresh-context Verification 唯一可新建/写入：

- `plans/ARCH-FE-001-frontend-module-auto-assembly/checklist.md`

Verification 不修改 Development 源码或 `tasks.md`；发现问题时记录 verdict 并回交 Development。

## 11. 验证矩阵

至少记录：

1. `pnpm install --frozen-lockfile`；
2. 纯 normalize/validate contract tests；
3. duplicate module/name/path/pageId/locale namespace、非法 enabled/navigation、动态 route 可见、navigation
   titleKey 在中英文模块 locale 中缺失的负向测试；
4. enabled module 同时进入 route/menu/locale/default redirect 的正向测试；
5. disabled 可选模块同时退出上述四个 consumer 的负向测试；完整应用装配缺失 system 或禁用 system
   时校验失败，正常 system 保持壳层所需双语文案的测试；
6. fixture 中新增完整可选模块后进入四个 consumer、删除该模块后四处同时退出的 add/remove 测试；
7. legacy manifest 缺少 enabled/navigation、使用全局标题 key 的 compatibility 测试；新格式使用
   模块标题 key 的正向测试，以及使用全局标题 key 或缺少模块双语标题的负向测试；
8. admin、access provider 已授权非 admin、未授权/未知用户的 menu/route/default filter 测试；
9. 两级 group/leaf、无可访问 leaf 隐藏 group、缺失/未知 icon fallback 测试；
10. orphan pageId grant 不得重建已删除模块 route/menu 的测试；
11. `aiis_demo enabled=false` 的源码和构建证据；
12. production `pnpm build`；模块手册明确 dev restart 与 production rebuild；
13. 残留扫描：共享 router/layout/locales/config/store 不包含具体业务模块名、业务 path 或业务 pageId；
14. 变更前后 route name/path/pageId compatibility 清单与 SemVer recommendation；
15. 不执行 Docker、Git/GitHub、数据库、PLC/CA 操作。

如当前 package scripts 不含 test，可使用 Node 内建 test runner 或无第三方依赖 checker；不得为本任务
引入完整测试框架。

## 12. Acceptance Criteria

| ID | 验收条件 |
| --- | --- |
| AC-001 | 前置 gate、Revision、Execution Mode、角色级 allowlist 和 3MD handoff 一致。 |
| AC-002 | manifest 只有一套 normalize/validate/sort 逻辑，router/menu/locale 不复制规则。 |
| AC-003 | enabled=true/legacy-enabled 模块按合同注册；可选模块 enabled=false 或物理删除时同时退出 route/menu/default redirect/module locale；完整应用缺失 system 或禁用 system 必须校验失败。 |
| AC-004 | navigation 缺失保持 route/locale 兼容；显式 navigation 自动生成稳定排序的 group/leaf。 |
| AC-005 | 共享 MainLayout/router/locales/config/store 不含具体业务模块名、业务路径或业务 pageId。 |
| AC-006 | menu/route/default filter 通过 consumer-supplied access provider 对 admin、授权用户、未授权/未知用户 fail closed；manifest 不授予权限，backend authorization 权威未改变。 |
| AC-007 | duplicate name/route/path/pageId/locale namespace、非法 manifest、动态可见 route 和缺失双语 title key 在 build/test 前明确失败；旧格式允许全局标题 key，新格式要求模块内标题 key，按 §5 判定。 |
| AC-008 | system 是不可禁用的必需 Core 模块，采用完整新合同及模块内标题；既有 route name/path/pageId 保持兼容，壳层依赖的 system/user 双语文案保持可用。 |
| AC-009 | `aiis_demo` 默认关闭、无 API/DB/PLC/外部 I/O，并可作为离线复制模板。 |
| AC-010 | 模块手册明确稳定目录、route/menu/locale/mock/permission ownership、legacy compatibility、跨模块依赖边界、dev restart、production rebuild 和离线接入/删除步骤。 |
| AC-011 | 不新增 dependency、不修改 pnpm lock；contract tests、checker 和 production build 通过。 |
| AC-012 | 没有修改 ARCH-001、其他业务模块、backend/Compose/Git/version tag，也没有运行 Docker 或外部系统。 |
| AC-013 | `tasks.md` 记录实际事实，fresh-context `checklist.md` 独立复核并给出正式 verdict。 |
| AC-014 | Human Owner final acceptance 前不宣称任何精确版本已实现或发布；compatibility verdict 只提供 SemVer recommendation，tag/release 属于独立决定。 |
| AC-015 | `src/app/<module>` 结构保持稳定；除 system contract 与默认关闭 aiis_demo 外，没有迁移或修改业务模块实现。 |

## 13. 风险、rollback 与 deferred decisions

主要风险与控制：

- 自动菜单误暴露详情页：只有显式 `visible: true` 的非动态 route 可生成 leaf；
- 权限来源与 Core 耦合：Core 只消费 access provider，不固定角色表或唯一配置来源；
- disabled 被误解为安全隔离：文档和测试只声明“不注册”，不声明“不打包”或授权隔离；
- locale/title/icon 漂移：checker 与 contract tests 覆盖双语 key、namespace 和 fallback；
- `ARCH-001` baseline 漂移：Development 前强制 baseline audit；material drift 回到 PM 新 Revision。

Rollback 边界：

- Development/QA 失败时保持未发布状态，并将 verdict 记录为 `dev_blocked|qa_failed|qa_blocked`；
- 如需撤销实现，只能在独立授权下把本任务 allowlist 内文件恢复到 immutable Core baseline；不得修改
  `ARCH-001` verdict、恢复业务硬编码菜单或通过双轨 manual registry 掩盖失败；
- 本任务不执行 Git/tag/release，因而 rollback 不包含远端、部署或生产动作。

Deferred decisions：

- 精确 SemVer、tag/release 名称与发布日期；
- Development 启动时再次核对 §3 已记录的 immutable baseline 与实际源码；
- baseline audit 发现的非实质路径调整。若路径、范围、风险、allowlist 或 AC 实质变化，必须新 Revision。

## 14. Stop conditions

出现以下情况立即停止：

- Development 启动时 `ARCH-001` 尚未 owner_accepted，或 immutable Core baseline 尚未记录；
- 需要在共享层重新硬编码业务模块；
- 需要修改 backend 权限或自动授予 role/page/API grants；
- 需要依赖运行时远程加载、动态 eval 或模块市场；
- 需要改变既有 route name/path/pageId；
- 实现出现破坏性兼容变化却仍宣称兼容 minor upgrade；
- 需要新增依赖、修改 lock、Compose、Docker、Git/GitHub 或 allowlist 外文件；
- 需要同时清理 `ARCH-001` 未完成的 staging/旧品牌问题。

## 15. 当前状态与后续批准

本 r3 已获 Human Owner 精确批准，当前为 `owner_approved`。PM 修订轮没有修改
`ARCH-001`、frontend 源码、root PLAN 或其他 task bundle。

`ARCH-001` owner acceptance、immutable Core baseline 与本轮 baseline audit 已记录于 §3。
本次 spec 修订授权不等于 Development 批准。Human Owner 的精确 Development 批准语句为：

```text
批准 aiis-ics-arch::ARCH-FE-001 r3，按 spec 精确范围和角色级 allowlist 开始 Development；Git/GitHub 写操作继续由 Human Owner 手工执行。
```

Human Owner approval recorded: 2026-09-07。

批准原文：`批准 aiis-ics-arch::ARCH-FE-001 r3，按 spec 精确范围和角色级 allowlist 开始 Development；Git/GitHub 写操作继续由 Human Owner 手工执行。`

Development 现在可创建 `tasks.md` 并在 §10 allowlist 内实施；`checklist.md` 仍只能由
developer_handoff 后的独立 fresh-context Verification 创建。
