Task ID: ARCH-TASK-003
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: fresh-context Verification
Updated: 2026-11-21 Asia/Shanghai

## r1 历史证据

以下完整保留 r1 Development 交接及返工记录。当前 r2 候选与复验边界记录于文末。

Task ID: ARCH-TASK-003
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: fresh-context Verification
Updated: 2026-11-21 Asia/Shanghai

# ARCH-TASK-003 r1 实施与自检

## 实施与授权

[批准规格](spec.md)记录 Human Owner 对精确 r1 的批准。实现直接写入正式交付工作树。起始工作树已有 ARCH-TASK-002、后续共享页 DIRECT 风格和其他任务改动。本任务保留这些既有改动。未创建分支或发布 ref。

| 实施项 | 范围与可检查结果 |
| --- | --- |
| R01、AC01–AC02 | 两个列表保留原管理员按钮与显示条件，分别导航到隐藏的管理员路由 /plan/local-fields、/performance/local-fields。返回原列表，沿用原本机筛选、分页、列宽并重读列表与字段配置。保留原菜单和默认入口。 |
| R02–R05、AC03–AC06、AC11 | 三组复用当前共享页和单项/批量编辑组件。按 scope 决定数据、提示、显示和写入项。本地页分别保存本机表宽。计划组没有实绩归属，实绩组仅自动/人工，无共享回写。新增占用槽拦截使用完整当前组，未知提交保留草稿和身份，仅重读权威配置。保留历史规格引用的 TaskConfigDialog 源码，当前两个正常列表入口已移除旧弹窗调用。 |
| AC07–AC11 | 新增一个管理员本地批删入口。严格校验 module/scope，在单例锁内复用现有历史与使用证据检查。一次发布快照并提交，响应按请求排序。保持旧 GET、PUT、单删和共享批删。配置模型、表结构、历史及 Alembic 没有本任务变更。 |
| AC12 | 同步两组页面说明、双语 API 合同、实际 OpenAPI 操作与合成请求。完成下方使用项目工具链及隔离浏览器、MySQL 的自检。 |

## Development 自检

| 命令或证据 | 实际结果 |
| --- | --- |
| 后端仓库已同步的锁定环境，`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py` | 92 通过，退出 0。包含本地批删 28 项，覆盖两组、1/2/100 项、完整身份、跨组同槽、隔离、权限、使用保护和全批状态保持；已注册 16 个合同路径与合成例真实响应通过。 |
| 从协调者提供的专属 dev 参数加载后，以同一项目解释器执行 `-m pytest -q -p no:cacheprovider tests_mysql/test_generic_task_shared_batch.py -k local` | 26 通过、13 deselected，退出 0。MySQL 8.4.6，回环 57644，UTC+08:00，夹具核对确切 UUID、版本、时差，创建和在 finally 清理随机 task003_dev schema。24 个用例确认真实 task_field_config_state 锁等待及两种顺序，覆盖两个模块的创建、更新、配置保存、单删、共享批删和对侧本地批删。两例物理提交前故障保留完整配置及历史，未访问现有库。 |
| 前端 `node --test tests/module-registry/generic-task.test.mjs` | 14 通过，退出 0。含两组占用槽、跨页选择、未知提交重读、未重放、作用域路由和本机列宽隔离。 |
| 前端 `node scripts/check-page-access.mjs --check --mode development`、production 同命令；`pnpm check:modules` | 均退出 0，dev/prod 角色配置合法，双语装配 29 条路由。仓库已有 pnpm check:access 脚本未传 mode，初跑退出 2；改用该脚本的文档参数，未更改通用包装脚本。 |
| 前端 `pnpm test:modules` | 最终 95/98 通过，退出 1。开工前在同一正式树已执行，94/97 通过、同三项菜单顺序断言失败。名称为 admin, supervisor, operator and unknown share route/menu/default decisions，actual source preserves Core route identity, shell locales and default-disabled demo，以及 five adapted modules retain order, owned bilingual titles and current visible leaves。现有 monitor 能耗顺序差异不属本任务。新增两条本地路由已加入相关预期。 |
| 前端 `pnpm build --outDir /private/tmp/arch-task003-dev.gEWwCN/dist --emptyOutDir` | 退出 0，已有 vendor chunk 体积提示。以此正式源码构建产物验证页面。 |
| `node /private/tmp/arch-task003-dev.gEWwCN/browser.cjs` | Chrome + Playwright Core，localhost 临时静态站点，拦截合成 HTTP，退出 0。计划中文浅色 1440px、实绩英文深色 390px，验证真实列表按钮、隐藏入口和通过历史/重载直达。核对占用槽无 PUT、空槽新增、Esc 不写入、动列重读、草稿取消、跨页勾选与对象准确的新批删路径。两条共享入口只显示共享定义。未登录、supervisor、operator、unknown 实际都无法直接进入两条本地页面。查看双语言截图，窄屏通过壳层现有按钮收起导航。未连接真实业务 API。 |
| Python AST、JSON、Markdown 本地路径、空白、候选摘要 | 38 个相关文档本地路径及 31 个候选文本文件检查通过，退出 0。没有模型或迁移文件进入候选。 |

## 精确候选与交接

正式工作树基准 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。以下 31 个文件为该候选的完整当前内容，含其文件内在本任务之前已经存在的差异。以仓库根为基准，可提取下列校验段运行 `shasum -a 256 -c`。整体摘要以这段按当前顺序、UTF-8、LF 且最后一行含换行的文本计算。

整体 SHA-256 为 `cc4a56a71bd2c1a7c78e7cb88032419f3967d0fc40cee5ff0545488ad6398985`。

```text
c2e60e91076408aed0979db59b0c14d8195ca570df157a63efdff61191e6bad2  CODE_INDEX.md
76095235033a52cc6448eab881b1857bad29af63c9ae6099caa01c5cdf4b4a21  backend/app/task/api/routes.py
a5d90250afa9be3dafb7e9b6d1c4f3f89ca44bbdc09f1ddbd805a7f872934af2  backend/app/task/schemas/fields.py
fc2e0cfd49de9f2499e40d7f37eadfb4025ad2cd4ca0ea6b61269c272a6fa4d3  backend/app/task/services/async_fields.py
53eccc6b5af2e8469ddb0d07c364c47cf8166c860e29e5aec379150b17cef517  backend/tests/test_generic_task_flow.py
96d4095632129893726b1737354b2e678b004e193d1521ded8146f7f5929df4c  backend/tests_mysql/test_generic_task_shared_batch.py
8110eff16221d96e804fb94c817538a2ab1e44f64e1aa998de44118d77637963  contracts/published/http-api/generic-task-workflow-v2/README.md
fc547caf318b1648ec7dd84846d5cfac57f39de04df1453d855b862865dc8543  contracts/published/http-api/generic-task-workflow-v2/README.zh-CN.md
773e224e05214e65f74c64383daae692459a16bd35bdebe1934cf3ef769575e0  contracts/published/http-api/generic-task-workflow-v2/examples/requests.json
90ee158b187630b024436260b97a867d7d6b7e17b9eb272c29e30d352d8b73d7  contracts/published/http-api/generic-task-workflow-v2/openapi.json
b120830216c6aa02769934852b3bc954f6193bbf0a096f35cb8f0ce629e86b34  docs/generic-plan-performance-guide.md
105bb0c6e081518d8ddee0494fb73ba3562b43e0c5b3ef73058d939af25dfbbf  docs/generic-plan-performance-guide.zh-CN.md
81af944ca69433ca26e196dfefd4ee7814d5dd548793d0aba42ffba032e3302d  frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md
c6d1e87945c6e5574299d9d607480c55adefa7e0cdac4a974ab117c91ef9b1d9  frontend-js/README.md
dd56e3fab35abdac4eb5d101a353ab37ee7accdc38450c7cc3bc8416d17e3da4  frontend-js/README.zh-CN.md
2398c13d49e53f4c45d93b83407441a6586ebd46688eee98c38dd5bc587ddf36  frontend-js/src/app/performance/locales/en-US.json
6577248c30b82d2cf5ed9251726d27fe5e9a68fd910dca2f1da17827ac115e62  frontend-js/src/app/performance/locales/zh-CN.json
d0530fcf9f36723984e56d3f66d406f08ab7cda38e965d1d91061c0a1a7e6887  frontend-js/src/app/performance/manifest.js
fc762677e830aef0e837bc5bbf7c95af0418589267a26d272c05f0005d0a3d93  frontend-js/src/app/plan/api/index.js
97d7acc9f3057afd2d232fc5883cab5f116c893faf308c52ccdd5b9412521bd6  frontend-js/src/app/plan/components/TaskFieldEditor.vue
0e7e9a5a1108799be9e655abf67932cbd5677c930bd2e33b944920bc24e8cd29  frontend-js/src/app/plan/components/TaskPage.vue
8932f3a5b3afe29f28530ae3909ba8f652cc2e4d25d82f48e4a1cb8812ac0179  frontend-js/src/app/plan/components/fieldSettings.js
4ea57e7af26cd03cc026a40bea6f57651c5a20363242f5a78f15188291e5d503  frontend-js/src/app/plan/locales/en-US.json
e0c81b3a427de97be74757cbdd8455651e8ee62654bfa54d91134a40ef59c544  frontend-js/src/app/plan/locales/zh-CN.json
52d8732dd33a046f97305186e1c241db4e66627fe437d8dc23072f1b8777e3e5  frontend-js/src/app/plan/manifest.js
3bdcdbd0e4c4d7f5bd1f4c20629fc2a7065fa8f9ca1ed642af13b5d00b8d8c0c  frontend-js/src/app/plan/views/local-fields/index.vue
78257b9997055db8eb5a0a0409dd8931c12833d8fb2b24e9e4dd64f4098f3d48  frontend-js/src/app/plan/views/shared-fields/SharedFieldForm.vue
8a581003e17ff219ec9a30f0d132bc57debfe7e9dc1a68a7e4c5af0caa4e429d  frontend-js/src/app/plan/views/shared-fields/index.vue
f2c2de326e405ab2ef46606e575eccc563e20d4065437c70b24313435a3cb03c  frontend-js/tests/module-registry/generic-task.test.mjs
b0e1da59b1c22cdf4e5075a8a2d18065f61f2b798aea8ced76e4d94cc89679de  frontend-js/tests/module-registry/page-access.test.mjs
7ba91fb66fcfefcb6a5062def50fbccdd1a12d17cedf0d1a96918b1947e9071f  frontend-js/tests/module-registry/registry.test.mjs
```

交 fresh-context Verification 独立复验 AC01–AC12。Development 自检不构成 QA verdict 或 Human Owner 最终验收。

临时源码前态快照、构建、浏览器夹具与两张截图及测试日志位于任务专属 /private/tmp/arch-task003-dev.gEWwCN。候选证据已写入本文件。该目录可保留到独立验证无依赖后，由协调者清理。一次性 native MySQL 实例和私有参数由协调者创建与正常收尾。无既有 dev/生产数据、服务切换、部署、Docker 启停、发布或现场操作。

## QA1-F01 返工及 QA2 交接

[QA1-F01](checklist.md#qa1-f01--本地字段保存时丢失可纠正的校验原因) 已在同一 r1 范围内返工。本地两页收到保存接口的 task.invalid_request 时，优先按后端实际返回的 duplicate_field_name 或 invalid_field_name 显示中英文提示。重复键提示说明本模块的本地字段和共享字段均不能重名，未将该通用错误码推断成某一具体共享定义。保留原草稿，用户修改后可再次使用当前修订提交。修订冲突、删除、未知结果、共享页既有回退及后台接口均保持原实现。

| 返工自检 | 结果 |
| --- | --- |
| 前端 `node --test tests/module-registry/generic-task.test.mjs` | 15/15 通过，退出 0。新增测试覆盖计划与实绩各中、英文，重名和保留键两种实际的 422 信封，草稿和修订保持，修正后可提交。 |
| 前端 `pnpm check:modules` 与 `pnpm build --outDir /private/tmp/arch-task003-dev.gEWwCN/rework-dist --emptyOutDir` | 均退出 0，29 条路由和双语装配通过。仍有已有 vendor chunk 提示。 |
| `node /private/tmp/arch-task003-dev.gEWwCN/rework-browser.cjs` | 真实路由、合成 HTTP、Chrome 执行退出 0。计划中文 1440px、实绩英文 390px 分别在空槽 25 提交共享同名键和保留键，在原弹窗观测到对应双语说明、名称/槽位/中英文值及配置版本保持。修正键后保存成功。原权限、占用槽拦截、选择、批删和返回列表均复跑。 |
| 重新运行 `pnpm test:modules` | 96/99 通过、退出 1。余三项为原候选已确认存在的 monitor 排序断言。首次重跑曾另出现工作树其他任务的设备测试缺少 QuestionFilled stub，后独立设备测试 17/17 与全量复跑均通过该项，未改设备代码。 |
| 后端 `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py -k 'local_batch_delete_validation_and_authority or revision_rules or candidate_examples'` | 3 通过、77 deselected，退出 0。后端及 MySQL 文件与 QA1 候选逐字节一致，本轮未改变事务或数据库。 |
| `git diff --check`、候选校验 | 退出 0。比较原清单只有前端共享管理页面、计划和实绩双语文案及前端专项共 6 个文件的完整内容变化。 |

QA1 校验段及结论保留。正式树基准 HEAD 及清单算法同上，交由 fresh-context Verification 复验以下 31 文件。最新清单的 SHA-256 为 `c06904501318a613b5947dffce0c8c52361cc3d38e29d25d288a5f969e5267ca`。

```text
c2e60e91076408aed0979db59b0c14d8195ca570df157a63efdff61191e6bad2  CODE_INDEX.md
76095235033a52cc6448eab881b1857bad29af63c9ae6099caa01c5cdf4b4a21  backend/app/task/api/routes.py
a5d90250afa9be3dafb7e9b6d1c4f3f89ca44bbdc09f1ddbd805a7f872934af2  backend/app/task/schemas/fields.py
fc2e0cfd49de9f2499e40d7f37eadfb4025ad2cd4ca0ea6b61269c272a6fa4d3  backend/app/task/services/async_fields.py
53eccc6b5af2e8469ddb0d07c364c47cf8166c860e29e5aec379150b17cef517  backend/tests/test_generic_task_flow.py
96d4095632129893726b1737354b2e678b004e193d1521ded8146f7f5929df4c  backend/tests_mysql/test_generic_task_shared_batch.py
8110eff16221d96e804fb94c817538a2ab1e44f64e1aa998de44118d77637963  contracts/published/http-api/generic-task-workflow-v2/README.md
fc547caf318b1648ec7dd84846d5cfac57f39de04df1453d855b862865dc8543  contracts/published/http-api/generic-task-workflow-v2/README.zh-CN.md
773e224e05214e65f74c64383daae692459a16bd35bdebe1934cf3ef769575e0  contracts/published/http-api/generic-task-workflow-v2/examples/requests.json
90ee158b187630b024436260b97a867d7d6b7e17b9eb272c29e30d352d8b73d7  contracts/published/http-api/generic-task-workflow-v2/openapi.json
b120830216c6aa02769934852b3bc954f6193bbf0a096f35cb8f0ce629e86b34  docs/generic-plan-performance-guide.md
105bb0c6e081518d8ddee0494fb73ba3562b43e0c5b3ef73058d939af25dfbbf  docs/generic-plan-performance-guide.zh-CN.md
81af944ca69433ca26e196dfefd4ee7814d5dd548793d0aba42ffba032e3302d  frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md
c6d1e87945c6e5574299d9d607480c55adefa7e0cdac4a974ab117c91ef9b1d9  frontend-js/README.md
dd56e3fab35abdac4eb5d101a353ab37ee7accdc38450c7cc3bc8416d17e3da4  frontend-js/README.zh-CN.md
b130372d1791ed7afa93d088a25d1f5187fe6dfc449975ba8b9846bc905c83c0  frontend-js/src/app/performance/locales/en-US.json
4bac30e9e0946fe06961543adcc7cf6aa18393f8e078943d3c5ed623a60946b9  frontend-js/src/app/performance/locales/zh-CN.json
d0530fcf9f36723984e56d3f66d406f08ab7cda38e965d1d91061c0a1a7e6887  frontend-js/src/app/performance/manifest.js
fc762677e830aef0e837bc5bbf7c95af0418589267a26d272c05f0005d0a3d93  frontend-js/src/app/plan/api/index.js
97d7acc9f3057afd2d232fc5883cab5f116c893faf308c52ccdd5b9412521bd6  frontend-js/src/app/plan/components/TaskFieldEditor.vue
0e7e9a5a1108799be9e655abf67932cbd5677c930bd2e33b944920bc24e8cd29  frontend-js/src/app/plan/components/TaskPage.vue
8932f3a5b3afe29f28530ae3909ba8f652cc2e4d25d82f48e4a1cb8812ac0179  frontend-js/src/app/plan/components/fieldSettings.js
3d0f106d5b44511a03bf64e6ad6ac56673efa85cf61c66a210b04874a8fd074c  frontend-js/src/app/plan/locales/en-US.json
e2f8af1c87a1f162285ff72d9170d5d4a2aa43622eec0be28347b781a71aedbd  frontend-js/src/app/plan/locales/zh-CN.json
52d8732dd33a046f97305186e1c241db4e66627fe437d8dc23072f1b8777e3e5  frontend-js/src/app/plan/manifest.js
3bdcdbd0e4c4d7f5bd1f4c20629fc2a7065fa8f9ca1ed642af13b5d00b8d8c0c  frontend-js/src/app/plan/views/local-fields/index.vue
78257b9997055db8eb5a0a0409dd8931c12833d8fb2b24e9e4dd64f4098f3d48  frontend-js/src/app/plan/views/shared-fields/SharedFieldForm.vue
c43e79693aafe2a22b9947ec697e073105bac0c983ea43bd5f8a77999abda7f2  frontend-js/src/app/plan/views/shared-fields/index.vue
ea38bb55278ac78a7f01d11052664663ace7fa0f6b8dba100e482f68518d5906  frontend-js/tests/module-registry/generic-task.test.mjs
b0e1da59b1c22cdf4e5075a8a2d18065f61f2b798aea8ced76e4d94cc89679de  frontend-js/tests/module-registry/page-access.test.mjs
7ba91fb66fcfefcb6a5062def50fbccdd1a12d17cedf0d1a96918b1947e9071f  frontend-js/tests/module-registry/registry.test.mjs
```

返工构建、浏览器验证脚本、候选清单、截图和测试日志在同一个 Development 暂存目录下新增 rework 前缀产物。无新增常驻服务，由协调者在独立验证不再需要时同目录回收。

## ARCH-TASK-003 r2 实施、自检与交接

### 实施范围

Human Owner 已批准 [r2 精确规格](spec.md#计划与实绩本地字段管理-r2)，仅把两个本地字段管理入口从列表顶部迁至各自侧栏。生产源码变化限于两份模块 manifest 和共用 TaskPage。模块 Registry 现有 route 归一化按声明的 order 排序，现有 ModuleNavigation 渲染 Registry 子项，MainLayout 使用同一 titleKey 生成面包屑。两个菜单使用既有双语 fieldSettings 标题、Setting 图标、order 15，保持列表 order 10、共享字段 order 20。原 URL、route name、pageId、模块 props 和 requiresAdmin 保留。TaskPage 移除入口按钮及因此未使用的路由和图标引用。两模块管理页面、返回与列表重新加载、后端、数据库表、模型、迁移和公开 API 合同无 r2 变化。

同步两个 README、字段快速指南和两份计划/实绩用户指南中的入口说明。三个测试文件仅调整本地字段路由顺序、角色及可见项预期，其他模块预期保持。交付在当前正式工作树，HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。未启动正式系统、修改既有登录状态或操作数据库。

### Development 自检记录

| 命令与方法 | 结果 |
| --- | --- |
| 前端 `node --test tests/module-registry/generic-task.test.mjs` | 15/15 通过，退出 0。回归两个模块的 URL、菜单顺序、双语标题键、按钮移除、管理员访问及本地和共享字段管理逻辑。 |
| 前端 `pnpm check:modules`；`node scripts/check-page-access.mjs --check --mode development` 以及 production | 29 条路由、9 个组装配通过，两模式角色配置校验通过，均退出 0。 |
| 前端 `pnpm test:modules` | 实施前及改动后均 96/99、退出 1。失败标题完全一致，均为已有 monitor 路由/菜单顺序差异，分别为 “admin, supervisor, operator and unknown share route/menu/default decisions”、“actual source preserves Core route identity, shell locales and default-disabled demo”、“five adapted modules retain order, owned bilingual titles and current visible leaves”。现行监控菜单顺序不在 r2 范围。 |
| 前端 `pnpm build --outDir <临时目录>/dist --emptyOutDir` | 退出 0。保留已有 vendor chunk 大小提示。浏览器验证构建以进程变量使用 /api/v1、关闭 mock 与演示登录，两普通测试角色临时有计划和实绩两个列表 grant。未改项目环境文件或正式构建目录。 |
| `node /private/tmp/arch-task003-r2-dev.88kY7u/sidebar.cjs` | Chrome + Playwright Core，临时静态回环服务和合成 HTTP，退出 0。两模块各在中文浅色 1440px 与英文深色 390px 下验证菜单顺序及 active、无重复按钮、标题与面包屑、现有 URL、准确定义范围和直接重载。核对后退、前进与返回，两个列表恢复任务号筛选、第二页、每页 10 条及 255px 列宽，向合成服务重新读取配置和列表。兼验原共享菜单仅显示共享定义。窄屏在保留现有侧栏行为的前提下通过收起侧栏检查内容可见。supervisor、operator、未知角色和未登录均不能直达两模块本地及共享管理页。 |
| `git diff --check`；本地文档链接、候选和前态清单检查 | 空白检查通过，30 个本地路径有效。r1 QA2 先前 31 文件在 r2 开工前全数匹配；r2 只改变下列 11 个文件，其余 20 个与 r1 QA2 字节一致。 |

### 精确候选

下列 11 项是 r2 变更文件的完整当前内容，包含既有工作树更改。文件清单按 UTF-8、LF、末尾含换行的格式计算 SHA-256，为 `fa55ce9774c3dadc69085c6ca5a3c8d9d27c5c5c5c5ee87844e24a386c872712`。从仓库根可将下列校验段交给 `shasum -a 256 -c`，另与 r1 QA2 的 31 项清单核对未触达文件。

```text
91c942cd3f7a250b253a7b41d4a33c223e45eb3c1cc6ff425737c2c78cf78fcb  docs/generic-plan-performance-guide.md
31bf8da4ae936c86abf049db77449a259ac500f90691f04cac7be45daef67790  docs/generic-plan-performance-guide.zh-CN.md
0d0151bcaab835c435a41ce59ffc22ecdbc908d62f19afc800bd07d129a89c4b  frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md
5a61ee593336e92215a21761e7326ad7af1c5a1f6df8956452eff3d7f6d45f4f  frontend-js/README.md
53aeddc90b5ce4239ef7fb5b41b2f349a12ace746b1c45e9bacc3800379415b8  frontend-js/README.zh-CN.md
08a4d7183e20f6b188c020ee7d273b51557e22e3dceca5fcb69110d2e5033bef  frontend-js/src/app/performance/manifest.js
02bfbd40d3bf786b2cc5f8603fa1aac902e6542a7801be416c8afd972311de11  frontend-js/src/app/plan/components/TaskPage.vue
3141954e45ddd06beb7e9a4dc79d4e2d28a94b0a085ba962aaf343ea082d9b28  frontend-js/src/app/plan/manifest.js
bf875d6da2f81eb81027a7cdc2e73177aa3b0bc95e7e4cc5615c7e8bb404ab54  frontend-js/tests/module-registry/generic-task.test.mjs
c4ad16af108773fb5b0eab2880305a5e8472e9850ad820928fec1eb72429e2bc  frontend-js/tests/module-registry/page-access.test.mjs
77fac5851eee9211e41589b625cdfc19147cb24117fa767bdd14c5ffb27259a0  frontend-js/tests/module-registry/registry.test.mjs
```

交 fresh-context Verification 核对精确 r2 文件并独立执行 R2-AC01 至 R2-AC06。后端与数据库变更未纳入 r2，本轮未运行后端及数据库写入验证。临时构建、前后测试日志、浏览器脚本和合成界面截图仅位于 /private/tmp/arch-task003-r2-dev.88kY7u，启动的回环进程已由夹具退出。该目录用于 QA 对照，待 Verification 无依赖后由协调者回收。Development 自检不构成独立验证或最终验收。
