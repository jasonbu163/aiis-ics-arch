# ARCH-FE-001 Development 记录

Task ID: ARCH-FE-001
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: QA-001/002/003 已返工并通过 15 组 self-check；请启动新的 fresh-context Verification 复核

## 1. 执行依据与边界

- Human Owner 已精确批准 r3；执行模式 `agent_team_same_session`。
- 本执行者为 coordinator 明确指派 Development 职责的子 Agent，读取 development profile；不宣称命名角色工具激活或平台 ACL。
- 基线 `HEAD=d85604a88ade5a6c86e77abaafa96de267515479`，`v1.0.0^{}` 为 `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`；ARCH-001 checklist 为 owner_accepted。
- 启动时唯一 dirty 文件是 PM 的 spec.md，保留该变更；Development 只写 spec §10 Development allowlist，不写 spec/checklist/root PLAN/catalog。
- Git/GitHub 写操作仍归 Human Owner；无 backend、API、DB、Docker 或 PLC 操作。

## 2. 实施顺序

1. DEV-001（AC-002/003/004/007/008）：纯 Registry 规范化、校验、排序、双语 namespace 与标题合同；Vite 单一发现入口。
2. DEV-002（AC-005/006）：router、menu、locale、default redirect 统一消费 Registry 与注入 access provider。
3. DEV-003（AC-008/009/015）：system manifest 保留 route/name/pageId，离线默认关闭 aiis_demo。
4. DEV-004（AC-003/007/011）：无依赖 checker、Node contract matrix、隔离真实 .env 的生产构建。
5. DEV-005（AC-010/013/014）：双语手册、允许的前端索引与 CODE_INDEX；记录 compatibility 和正式 handoff。

## 3. 实施事实

- DEV-001 完成：`moduleManifest.js` 单一 normalize/validate/sort；`moduleRegistry.js` 单一 Vite discovery。
  同一 Registry 输出 active modules、原结构 routes、递归 effective routeRecords、两级 navigation 与活动文案。
  disabled 可选模块退出四个 consumer；required system 缺失/非 true 启用状态均失败。
- DEV-002 完成：router 按活动 route record、登录状态和统一 access helper 判定；菜单、默认入口使用同一
  helper。保留 Vue Router 嵌套、alias、redirect，effective leaf 继承父 metadata；默认入口跳过 redirect、
  容器与参数路由。损坏 provider 和角色输入 fail closed，不授予 backend/API 权限。
- DEV-003 完成：system 声明新 navigation 与已有模块标题 key，原 system/user 文案文件无需修改；新增
  默认关闭的 aiis_demo 离线页面及双语文案，无 API、timer、DB、PLC 或外部 I/O。
- DEV-004 完成：Node checker 与 15 个合同测试组（首轮 12，QA 返工增加 3）；`prebuild` 在实际 `pnpm build` 前执行同一 checker。
  不修改 build 原脚本、dependency、version 或 lock。
- DEV-005 完成：双语模块手册包含从零创建/复制/禁用/删除、权限 provider、mock facade、legacy/new title
  合同、dev restart 与 production rebuild；同步允许的 frontend README/PLAN 和 CODE_INDEX。

### 精确 Development 文件

```text
CODE_INDEX.md
frontend-js/PLAN.md
frontend-js/PLAN.zh-CN.md
frontend-js/README.md
frontend-js/README.zh-CN.md
frontend-js/package.json
frontend-js/scripts/check-module-manifests.mjs
frontend-js/src/app/README.md
frontend-js/src/app/README.zh-CN.md
frontend-js/src/app/moduleManifest.js
frontend-js/src/app/moduleRegistry.js
frontend-js/src/app/system/manifest.js
frontend-js/src/app/aiis_demo/manifest.js
frontend-js/src/app/aiis_demo/locales/en-US.json
frontend-js/src/app/aiis_demo/locales/zh-CN.json
frontend-js/src/app/aiis_demo/views/example/index.vue
frontend-js/src/components/navigation/ModuleNavigation.vue
frontend-js/src/config/permissions.js
frontend-js/src/layouts/MainLayout.vue
frontend-js/src/locales/index.js
frontend-js/src/router/index.js
frontend-js/src/store/user.js
frontend-js/tests/module-registry/registry.test.mjs
plans/ARCH-FE-001-frontend-module-auto-assembly/tasks.md
```

另有 PM 先存的 spec.md diff，不归 Development 写入。未写 root PLAN/catalog、checklist、其他模块或来源仓。

## 4. 首轮 Development self-check（2026-09-07；返工结果见 §7）

环境：macOS、Node v22.19.0、pnpm 11.11.0；只验证源码/本地 fixture。以下均为 Development self-check，
不能代替 fresh-context QA。

| 检查与实际命令 | 结果 / AC |
| --- | --- |
| `git rev-parse HEAD 'v1.0.0^{}'`；读取 ARCH-001 checklist | exit 0；基线见 §1，前置 gate 已满足（AC-001） |
| `pnpm install --frozen-lockfile`（批准的网络重试） | exit 0；既有 lock，85 packages，未改 dependency/version/lock（AC-011） |
| `pnpm --config.verify-deps-before-run=false test:modules` | exit 0；12 tests、12 pass、0 fail（AC-002/003/004/006/007/008/009/011/015） |
| `node scripts/check-module-manifests.mjs` | exit 0；只显示帮助 |
| `node scripts/check-module-manifests.mjs --check` | exit 0；active=[system], routes=2, groups=1 |
| 临时副本 `pnpm --config.verify-deps-before-run=false build` | exit 0；prebuild 先通过，Vite 1577 modules，最终构建 2.18s（AC-011） |
| 临时副本将 system enabled 改 false 后运行同一 build | 预期 exit 1；`Required module must declare enabled: true: system`；未进入 Vite，随后恢复副本 true |
| Node `createI18n` 对实际 Registry 切换 en-US/zh-CN | exit 0；英文 System / User Management / Profile；中文 系统设置 / 用户管理 / 个人资料 |
| `git diff --exit-code HEAD -- frontend-js/pnpm-lock.yaml`；Node 对比 HEAD/current package dependency/version | exit 0；无版本、依赖或 lock 漂移 |
| `git diff --check`；Node 校验六份触达双语文档的相对链接 | exit 0；无 whitespace/link 错误（AC-010） |
| `rg -n 'system\.user\|system\.projection-mapping\|/system/user\|/system/dict\|aiis_demo'` 对共享 router/layout/locales/config/store 的同等 alternation 扫描 | 无命中（rg exit 1，正常负向结果）；公共账号 UI 的 system/user 文案按 r3 保留（AC-005） |

合同矩阵覆盖：四 consumer add/remove/disabled；system 必需且仍受权限过滤；legacy named export、全局
标题、原路由数组默认顺序；new-field 标题规则；active legacy 不可依赖 disabled namespace；嵌套 route、
redirect 父节点、alias 与 inherited requiresAdmin；admin/授权/未知/损坏 provider；group/leaf、隐藏详情页、
空 group、图标 fallback；重复模块/route name/规范化 path/pageId/namespace（含 global collision）；非法
enabled/navigation/order/flag、可见动态 route、缺失双语 key；underscore 模块权限 key；当前 Core route
兼容表、system/user 壳层文案与 MainLayout literal key 实际解析。

### 构建隔离与实际限制

- 验证副本：`/private/tmp/arch-fe-r3.R829xG`，构建产物在其 `dist/`；用
  `rsync -a --exclude='/.env*' --exclude='/dist' frontend-js/ /private/tmp/arch-fe-r3.R829xG/` 创建/同步，
  复用当前已安装依赖；Node 检查确认副本根目录没有 `.env*`。真实项目 `.env` 未读取/改写，仓库没有新 dist。
- pnpm 11 本机设置在运行脚本前自动检查依赖。初次 `pnpm test:modules` 触发自动安装后因 sandbox DNS
  失败（exit 1），转为上述已批准的 frozen install；直接 Node runner 首轮也已通过。
  复制 node_modules 后普通 `pnpm build` 试图自动 purge，并因无 TTY 退出 1；使用仅本次 CLI 的
  `--config.verify-deps-before-run=false` 复用已锁定依赖，未修改项目/个人 pnpm 配置。
- 首次临时同步误用全层级 dist exclude，导致 Vite 依赖内部 dist 缺失；仅副本构建失败。改为根目录
  anchored exclude 后重同步，最终构建通过；未删除或回滚用户源码。
- Vite 保留 vendor chunk 大于 500 kB 的警告（约 1,048.64 kB uncompressed）；未在本任务调整打包策略。
- `enabled: false` 证明不注册，并不声称 demo 源码/懒加载 chunk 不进入构建扫描。
- 已做真实 Vue Router memory route 行为、Vue I18n 双语切换和 production 编译；未启动浏览器 UI、真实登录
  或连接后台。菜单视觉/点击的独立审核留给 Verification，不冒称端到端环境通过。
- 无 Git/GitHub 写入、Docker、DB、backend API、PLC 或 CA 操作（AC-012）。

## 5. Compatibility 与版本建议

| route name | path（前后相同） | pageId（前后相同） |
| --- | --- | --- |
| SystemUser | system/user | system.user |
| SystemProjectionMapping | system/dict | system.projection-mapping |

旧 manifest 缺 enabled 默认启用，缺 navigation 不生成菜单，具名 export 和全局标题继续可用；同序
routes 保持源码数组顺序。嵌套/redirect/alias 未被两级导航模型排除；无 pageId 的 legacy records 可以
转交 Vue Router，但不会成为权限授予/默认入口依据。system 仅迁入原有模块标题，不改 route identity。

Development compatibility recommendation：目标为向后兼容的功能增强，可在 fresh QA 与 Human Owner
最终验收后考虑 minor 发布。此处不决定任何精确版本，不创建 tag/release，也不宣称已发布（AC-014）。

## 6. 交接与返工记录

- 本轮 self-review 修正：保留同序 legacy route 顺序；校验 active legacy 标题不依赖 disabled namespace；
  保留嵌套路由、无 component/meta 的 redirect parent 和 alias，并增加真实 memory router 回归。
- handoff target：r3 approved spec + 当前 `HEAD=d85604a88ade5a6c86e77abaafa96de267515479` 上述未提交
  Development 文件集合。没有实现 commit，不混同 PM spec diff；临时验证副本仅供复现。
- 下一 gate：coordinator 显式启动 fresh-context Verification，独立复核实现/测试/边界并唯一创建
  `checklist.md`。Human Owner final acceptance 与任何版本发布继续待独立决定。

## 7. QA 第一轮返工（2026-09-07）

依据：完整读取独立 checklist 的 `qa_failed`；保留 QA-001/002/003 及其失败证据，Development 不修改
checklist。返工先切回 `implementation_in_progress`，下列验证完成后重新 `developer_handoff`。

| 发现 | Development 重现与修正 |
| --- | --- |
| QA-001 可选参数被误拒绝 | 重现 `legacy/:id?` 抛 Invalid route path；参数 token 中的 ?/*/+ 和自定义正则不再当作静态 query/hash。新增真实 Vue Router resolve `/legacy`、`/legacy/42` 均匹配 Optional 的正向，权限可访问但不进入菜单/default；普通 query/hash 非法 path 仍拒绝。 |
| QA-002 重复空 sibling 漏检 | 重现两个 `path: ''` leaf 被接受；路径注册现在记录 owner，仅祖先与其默认空子节点可共用 URL，同父重复空 sibling 明确失败。新增实际 Router 对唯一默认子节点的解析，以及重复 sibling 两个 name 同 URL 的负向证据。 |
| QA-003 父 alias 派生冲突漏检 | 重现 `/shortcut/list` alias child 与 Direct 共用 URL；规范化递归传递父 canonical/alias paths，所有派生子路径进入同一全局冲突集合。新增两种父 alias 的真实解析正向，以及跨模块 direct route 冲突负向。 |

本轮改动：`moduleManifest.js`、`tests/module-registry/registry.test.mjs`、本 tasks，另将允许的 frontend
PLAN pair 的测试数量同步为 15。没有改 spec/checklist/锁文件/外部系统；精确实现集合仍同 §3。

返工验证：

- 改前 Node stdin QA fixture 重现：QA-001 抛错、QA-002/003 被接受；exit 0 只是探针完成，不代表通过。
- `pnpm --config.verify-deps-before-run=false test:modules`：最终 exit 0，15 tests / 15 pass / 0 fail。
  首次新增测试有一个把参数修饰符后续静态文本误当 query 的断言失败，已移除该不符合 Vue Router
  兼容语义的断言；保留普通静态 query/hash 非法 path 负向，未收窄 legacy 参数语法。
- 用 §4 的 rsync 命令重新同步当前源码到 `/private/tmp/arch-fe-r3.R829xG`（仍排除根 `.env*`）。
- 副本 `pnpm --config.verify-deps-before-run=false build`：exit 0，prebuild active=[system]、2 routes、
  1 group；Vite 1577 modules；vendor chunk 大小警告仍在，不代表构建失败。
- `git diff --check` 和已修改 JS 的 `node --check`：exit 0。

本次只提交 Development 修复事实；第一轮正式 QA verdict 仍为 `qa_failed`，必须等待新的 fresh-context
Verification 重验后才能形成新 verdict。SemVer recommendation、最终验收与发布继续待后续 gate。
