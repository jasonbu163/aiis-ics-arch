Task ID: ARCH-TASK-004
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: fresh-context Verification
Updated: 2026-11-23 Asia/Shanghai

# 实施与 DEV 自检

根据 [获批准的 r1](spec.md) 在正式工作树实施。验收条件见规格第 6 节；本文件记录 Development 的操作和实际观察。

## 实施

- [TaskPage.vue](../../frontend-js/src/app/plan/components/TaskPage.vue) 在打开记录时立即显示目标和加载状态。主记录、必要配置、实绩补建用的可选计划配置、保存结果和加载标志均按打开意图归属。关闭、退出路由、卸载、新建计划和重新打开会使前一个意图失效。取消时立即失效，关闭动画使用已有内容淡出，异步 `closed` 或 `update:modelValue` 事件不参与父组件状态写入。当前失败保留重试或草稿，旧响应不能影响后续对话框。
- 详情分为基本信息、业务字段和时间信息。标题区按当前权限提供编辑或补建。取消回到原记录的只读详情，当前保存成功关闭并刷新列表。已有目标继续锁定，补建保持现有计划配置、表单及提交合同。
- [字段管理弹窗](../../frontend-js/src/app/plan/views/shared-fields/index.vue) 和 [单字段表单](../../frontend-js/src/app/plan/views/shared-fields/SharedFieldForm.vue) 按作用域分组，单项删除确认展示目标并提示核对 MES、SMA 等外部引用。单项可滚动区域只在正文，标题和操作留在上下两区。保存差量、删除目标、保护、修订冲突及结果未知核对沿用既有处理。批量路径不应用单项外壳、按钮、文案或报错滚动。
- 计划、实绩各自的中文和英文 locale 增加对应 `workflow.dialog` 文案。源码结构没有新文件，因此无需更新 `CODE_INDEX.md`。

## 边界核对

开工前读取根/前端项目说明、开发流程、批准规格及现有相关代码。目录中当时只有 spec，无本任务旧 tasks 或 checklist。按 frontend-ui 和 i18n-workflow 实现，按 AIIS 路由只读核对后端配置、详情和写入合同。前端使用已有的本地时间格式和 API 模块，运行本任务构建没有调用后端、数据库、外部接口或部署。交付 diff 限定在下述 8 个前端文件与本记录。工作树开工已有导航、样式、配置界面与文档的并行改动，本次保留这些改动。使用 HEAD 作为提交基线，交付是未提交的正式工作树候选。

## 实际验证

Darwin arm64，Node v22.19.0，pnpm 11.11.0，Chrome 157.0.8103.79，Playwright 1.64.0-alpha-1789764292000。浏览器通过 localhost CDP 连接临时 Chrome，并拦截文件和 API 请求，静态内容从正式工作树构建产物返回，写入请求只由内存夹具记录。无真实业务数据。默认沙盒启动 Chrome 两次均退出 134，随后经自动评审允许临时 Chrome 和 localhost 连接，浏览器可运行。

| 工作目录与命令 | DEV 结果 |
| --- | --- |
| `frontend-js` · `pnpm exec node --test tests/module-registry/generic-task.test.mjs` | 22 项通过，退出 0。新增 deferred 时序检查及双语键检查。 |
| `frontend-js` · `pnpm check:modules` | 29 路由、9 组通过，退出 0。 |
| `frontend-js` · `pnpm test:modules` | 103 通过、3 失败，退出 1。失败名称与协调端开工基线 96 通过、3 失败一致，均涉及 monitor 菜单顺序。 |
| `frontend-js` · `pnpm build --outDir /private/tmp/arch-task004-dev/final-dist --emptyOutDir` | 退出 0。Vite 提示部分产物块大于 500 kB。 |
| 仓库根 · `node /private/tmp/arch-task004-dev/browser.mjs` | 最终构建退出 0。8 个详情场景、48 个单项弹窗场景，另验证两个列表错误重试、四个字段路由的新增请求、单项未知结果核对及批量外壳隔离。捕获 20 个合成写请求，7 张截图，页面 JS 异常 0。 |
| 仓库根 · `git diff --check` 及任务 Markdown 本地链接 | 退出 0。两任务文档共 10 个本地相对链接及所带锚点通过；交付清单 8 个文件全部通过 SHA-256 核对。 |

模块全量失败名称

- admin, supervisor, operator and unknown share route/menu/default decisions
- actual source preserves Core route identity, shell locales and default-disabled demo
- five adapted modules retain order, owned bilingual titles and current visible leaves

## 验收覆盖

| 条目 | DEV 观察 |
| --- | --- |
| AC01 | 两模块分别控制 A 的记录、必要配置成功和失败，B 的身份、字段和加载状态归 B。最新失败时无可操作旧记录且重试恢复。 |
| AC02 | 控制 A 的可选计划配置晚于 B 成功/失败，覆盖 B 已有计划、配置成功或失败、权限不足和缺少计划访问权。失败时仍可读当前实绩。 |
| AC03 | deferred 测试覆盖关闭、路由离开、卸载、重开、详情与新建计划双向切换。Chrome 检查 Esc 后出现离场动画并在该动画期间点开 B，随后 A 响应不覆盖 B。 |
| AC04 | 两模块记录取消零写入、重复保存只发一次、同一草稿失败保留、成功关闭刷新。覆盖 A 保存成功或失败晚于打开 B、晚于路由离开、晚于 B 已开始保存。 |
| AC05 | 实际 setup 检查 admin、supervisor、operator 和无权角色；捕获计划、实绩和补建提交。覆盖已有/空目标、自动/人工、不可清空、数值零、布尔 false，不发送越权或未变更字段。 |
| AC06 | Chrome 两列表均查看、编辑、保存和取消；实绩额外检查补建，普通详情检查固定项、启用动态字段、空值、0、false 和上海时间。检查标题 16px/590、三段、双列/单列、滚动、键盘、按钮间距及普通关闭后的焦点恢复。覆盖中文浅色和英文深色 1280 × 730，中文深色和英文浅色 375 × 590。 |
| AC07 | Chrome 四个管理路由检查新增、编辑和单行删除；验证三种作用域的分组、不可变项、目标身份、外部映射提示和拒绝原因。槽位占用和归属合同另由专项覆盖。浏览器捕获正确 scope 的新增及单项标签差量请求。 |
| AC08 | 专项复跑修订冲突、结果未知、响应丢失、权威重读和保护的既有回归；Chrome 进入四个管理路由的批量编辑/删除，核对没有单项类名，单项变更仍使用对应 scope 和原 API；编辑遇到结果未知时保留草稿、单次写入、权威重读并显示核对结果。 |
| AC09 | 当前正式工作树执行专项、manifest、全量、双语对称、隔离构建、浏览器及 diff 核对。全量基线差异如上。 |

## 交付候选与限制

- 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，基线 HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。获批 `spec.md` SHA-256 `6a26a2d58ef7359307fb1c1d01996a96e7b19964addce3422dd85542aef07863`；实现文件清单字节（含末尾 LF）的 SHA-256 为 `24965760b7fda3c11818bf50315d2c5249d7aede85b864da700c92970b0e00fa`。
- 前端的失效保护约束界面副作用。已发出的保存服务端仍可能提交。全局会话过期处理、接口与数据权限保持现有合同。Chrome 观察基于合成权限与业务夹具，真实系统、设备、数据库和部署未纳入本轮执行。
- 开发自有资源在 `/private/tmp/arch-task004-dev/`，含构建、浏览器脚本、截图、日志和源文件清单，提供给独立验证作为可选参考。独立验证和最终验收所需证据已概括在本记录，临时文件在无验证及验收依赖后由协调端回收。专属的临时 Chrome 进程已停止，未占用回环端口。

```text
711429435a733d5eac4d32afabdca33e91b9e42a02c5a5f295fa846dcd046065  frontend-js/src/app/performance/locales/en-US.json
6e7c1d0b2d5a54b5682a8cad6633497206fd117018c3e07fbc1586a874b5c83d  frontend-js/src/app/performance/locales/zh-CN.json
de3c02f32c4ded5e44d7bed34bab5b4c35c350d65d3deb2b91075290c8b03134  frontend-js/src/app/plan/components/TaskPage.vue
de2ce1f8cdd4bf2def0cdfc91672f6cb40da3fad46c01658b1f8efc0bb062ccf  frontend-js/src/app/plan/locales/en-US.json
5c473e367140f696f0212b1ab4d134f24be2f2526baffdde92911cb18a124981  frontend-js/src/app/plan/locales/zh-CN.json
1e591f1cbee44fb316230d16703e81f7643236efe02c5e142bcf2a3ce65a235d  frontend-js/src/app/plan/views/shared-fields/SharedFieldForm.vue
84c8ac528353448d850c10c73b6aac4cec71124f6e6abb042938903a91f7d4b7  frontend-js/src/app/plan/views/shared-fields/index.vue
470e88f00b09b79ce7db84f9b197af264c5056cfcab44b1a8cf2de779e65a11c  frontend-js/tests/module-registry/generic-task.test.mjs
```
