Task ID: ARCH-TASK-002
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: fresh-context Verification QA2 after QA1 rework
Updated: 2026-11-20 Asia/Shanghai

# ARCH-TASK-002 r1 Development 实施与自检

## 授权和实施

[批准规格](spec.md)记录了 2026-11-20 Human Owner 对精确 Revision r1 的批准。实施写入正式交付工作树。没有创建候选分支或发布 ref。保留此前 DIRECT 的计划、实绩列表调整，保留同区及仓库其他工作中的变更。

- 两个共享字段入口保留现有路由及权限，读取同一配置切片。主表客户端查询、状态及归属筛选、每页默认 20、跨页勾选和独立本机列宽。刷新修订变化时清除选择。新增、单项编辑、批量草稿和删除确认分别采用现有设计组件。两个本地字段弹窗继续执行原逻辑。
- 共享字段 PUT 仅提交实际变化。现有单删接口保留。新增管理员 POST 批删，复用单项历史保护、现有配置首锁和失败信封；全批通过后只发布一份快照，保持调用顺序和原子提交。无数据库模型、DDL、Alembic、业务历史迁移变更。
- 保存和删除的未知结果重新读取当前配置，并保留提交涉及的身份及草稿。保存核对权威字段值与该次提交属性是否相符；删除核对字段当前是否存在。界面不会把当前状态归因为先前请求，也不自动重复写入。拒绝时若有已证实的阻塞位置，使用当前界面语言显示具体字段及原因。
- 同步双语文案、HTTP 文档和注册路由生成的 OpenAPI 切片、合成请求、使用说明及源码索引条目。

## Development 自检

| 验证命令或方式 | 实际结果 |
| --- | --- |
| 后端项目锁定环境，`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py` | 64 通过，退出 0。包含实际 HTTP 业务信封、1/2/100 个字段、权限、修订、坏身份、受保护排列、历史不一致、单删兼容、版本推进、已有合同路径/响应及合成文档对照。首次执行发现私有辅助函数扩签后旧测试未传参，已修正并复跑。默认沙盒中 `uv run --offline --no-sync` 因用户 uv 缓存的 `.git` 访问被拒，改用已同步的仓库 `.venv`，未改依赖。 |
| 在协调者提供的一次性 native MySQL 实例中加载 dev 私有参数，后端执行 `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests_mysql/test_generic_task_shared_batch.py` | 13 通过，退出 0。MySQL 8.4.6、+28800、回环高端口，夹具校验 UUID/时区/精确版本后使用随机 `task002_dev_*` schema。检查 `performance_schema.data_lock_waits` 的真实配置行锁等待，覆盖与计划/实绩创建或有效更新、PUT 配置保存及单删各自的两个竞争次序，并验证注入的提交前回滚。逐测试清理临时 schema，未访问既有数据库。 |
| `node --test tests/module-registry/generic-task.test.mjs` | 12 通过，退出 0。覆盖两个管理员入口、原有列表/本地设置回归、25 项筛选分页和跨页选择、PUT 仅 submit 变更、显式 null、未知提交处理及保护错误定位。 |
| `pnpm check:modules` | 退出 0，27 条路由及双语模块装配通过。 |
| `pnpm test:modules` | 96 项中 93 通过，3 失败，退出 1。失败为改动前已经复现的监控/设备顺序断言，测试名称为 `admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`、`five adapted modules retain order, owned bilingual titles and current visible leaves`。本任务定向用例全通过，未触达其他模块。 |
| `pnpm build --outDir /private/tmp/arch-task002-build --emptyOutDir` | 退出 0。既有 vendor chunk 大小提示，无构建错误。 |
| `node /private/tmp/arch-task002-browser/verify.cjs` | Playwright Core + Chrome，构建产物走正式路由，HTTP 在浏览器内以合成配置拦截。计划中文/浅色 1440px、实绩英文/深色 375px 均通过。检查分页、跨页勾选两项、批量编辑弹窗内行数及列宽提示、删除二次确认、首个保护字段的语言和 identity、批删成功、搜索和只保存单行差异；无页面脚本错误或页面横向溢出。375px 下用应用既有按钮收起侧栏。浏览器据实际任务源码构建，未连接真实 API。 |
| Python AST 编译、相对 Markdown 链接、示例 JSON 解析、`git diff --check` | 21 个 Python 文件、24 个本地文档链接及候选 JSON 检查通过，退出 0。 |

## 精确候选与交接

工作树基准 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`，候选为下列 22 个文件的完整工作树内容，包含那些文件先于本任务存在的内容。文件逐项 SHA-256 校验从仓库根运行 `shasum -a 256 -c`，或将该校验段同顺序保存为 UTF-8/LF 文件后核对整体摘要。未提交及不属于候选的其他差异继续保留。

合并校验段 SHA-256 为 `6eee086cb4505d8c9a0bd8b8bd8cc82e7b6597850de6264f6802a09addcd9028`。

```text
cb345aa58a2a966f48e3542b16d8a8ef1d5876f640014fc371c584743f01c770  CODE_INDEX.md
3162af249511448c2b73e1905f13b666564f40948e01840ac777a38f95ce640c  backend/app/task/api/routes.py
d6407d8c2ab4fd2ab5f6fe98883bf98394616727d9c151613cd934bbd679fa27  backend/app/task/schemas/fields.py
584ff90cc16791b543078ea71015d7f535b669255f10ffd2a724e9e72ae0799b  backend/app/task/services/async_fields.py
c487f25146550d01b26bb38d36884e18dc14998898216703f3e4e783b2dcf921  backend/tests/test_generic_task_flow.py
3d64d0888f280a45687d3fbe89cbc58ecf98e38327063b6b177045a9773fd700  backend/tests_mysql/test_generic_task_shared_batch.py
460992a5361a9c400feda7bec2d8df4b95f726251aaa0a8a299b2ea68f8cdb7b  contracts/published/http-api/generic-task-workflow-v2/README.md
f583baed345f77db6cf2a830e37108d59b4dec1d586390d4be1c144811c3b133  contracts/published/http-api/generic-task-workflow-v2/README.zh-CN.md
b1ec95998da164aceab1f0fbc4bd4e54459bc3886d1919a66b0dfed9480fb275  contracts/published/http-api/generic-task-workflow-v2/examples/requests.json
940fdb28bf879971cf4c91872fda6575d6d8b0a83f90c6d738630e52f0697c61  contracts/published/http-api/generic-task-workflow-v2/openapi.json
f59496513fba39ee11f2bb9515035c1ae477d1a03acbeae75535809660c8d289  docs/generic-plan-performance-guide.md
627f318bc2ecf590253b085e7f0224c8323af2c5b17e0326e6d6b4314b192492  docs/generic-plan-performance-guide.zh-CN.md
fc25cc29e78b6dddc3f9578b82b5629119983688833a406e3f86386346eaebd4  frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md
9d1fb8b3cb08e23cf80bb8d0dc2ee3999aee36c65cd1e06c5d73e8aedc0c27aa  frontend-js/src/app/performance/locales/en-US.json
7b638bda7460f815b59c6f8912365709fb905a9fffbe2ce54a7e7f1cb6e5df03  frontend-js/src/app/performance/locales/zh-CN.json
1971f6dd7ea75dc6ddc46bdfb20694eaacda44e12c1e5e07de622c788f829122  frontend-js/src/app/plan/api/index.js
819490ae223dae52cfb4147b1c24af4d843595e14051ddfbd8efbcc8ef2c5ac0  frontend-js/src/app/plan/components/TaskFieldEditor.vue
93a420473753a19afea509402bd57eef3fcd12caf5c1e4a0ec86fd260eac33e0  frontend-js/src/app/plan/locales/en-US.json
ea7eb3a1de385233e59c033b3444c650b6b3294df66f30b55474188004e9ee5b  frontend-js/src/app/plan/locales/zh-CN.json
8cb9380e27d779503fc0d13c08fd353f96fdaed7218dfdd57769276130c02281  frontend-js/src/app/plan/views/shared-fields/SharedFieldForm.vue
56c49fee68b5c7bb225780595bf041d668f42d71c0f42fa7099ff985e98ce71e  frontend-js/src/app/plan/views/shared-fields/index.vue
472210f72060370fa853715ec8668b402b6ec039285ea1d2674f273e2bee8c28  frontend-js/tests/module-registry/generic-task.test.mjs
```

`developer_handoff`：请由 fresh-context Verification 独立复跑已批准 r1 的 AC01–AC11，在 QA 专属 native MySQL 实例复核 AC09。Dev 自检不构成 QA 或 Human Owner 最终验收。需要留意的已知风险见规格第 6 节，并复核三项仓库已有的前端监控顺序失败不来自当前候选。

构建、浏览器夹具及图片归本任务，QA 可能暂用作为开发对照，目录为 `/private/tmp/arch-task002-build`、`/private/tmp/arch-task002-browser`，及本任务构建和前端测试的两份 `/private/tmp/arch-task002-*.log`。这些目录和日志不是独立 QA 证据，由协调者在 QA 无依赖后清理。一次性 dev、QA MySQL 进程和私有参数由协调者创建和收尾。未执行既有 dev/生产数据写入、服务切换、Docker 启停、发布或现场操作。

## QA1 返工及 QA2 交接

[QA1](checklist.md) 的 AC05 报告指出，新增草稿手动选中已存在的共享槽位并沿用原字段身份时，旧保存路径会调用现有 PUT 并覆盖原设置。本次 r1 返工只改共享主表保存入口、计划和实绩的双语文案及对应回归测试。新增在构造 PUT 前拦截当前共享组的任一已占槽位，显示具体槽位提示并保留草稿。该检查涵盖启用和停用字段，也不依赖当前筛选或页码。真实空槽可继续提交。同号本地槽位和已有共享字段的合法编辑仍按既有规则处理；在配置读取后被其他客户端占用的空槽仍由原修订号校验拒绝。后端、数据库、API 合同和局部字段管理均未修改。

| 返工自检 | 结果 |
| --- | --- |
| 前端 `node --test tests/module-registry/generic-task.test.mjs` | 13 通过、退出 0。两入口均覆盖停用共享槽同名和异名零 PUT、原字段和版本保持、草稿保留、同号本地槽不占用共享槽、合法编辑差异 PUT，以及 stale revision 保留草稿。 |
| `pnpm check:modules` 和 `pnpm build --outDir /private/tmp/arch-task002-rework-build --emptyOutDir` | 均退出 0，27 条路由装配和构建通过，原 vendor chunk 体积提示存在。 |
| `pnpm test:modules` | 退出 1，94/97 通过，仅 QA1 对照确认的三项既有 monitor 顺序断言失败。 |
| `node /private/tmp/arch-task002-browser/verify-rework.cjs` | Chrome 在本次构建的计划中文浅色 1440px 及实绩英文深色 375px 正常路由均通过。使用合成 HTTP 响应，复现同名和异名占用槽的阻止情况，确认零 PUT 且草稿、定义与修订保持。真实空槽 26 一次 PUT 成功，有效槽 27 模拟并发修订冲突后保留草稿并禁重复提交。初次浏览器路径的分页、跨页勾选、批量编辑和删除，以及原字段单项保存也在新构建中通过。 |
| 后端锁定环境 `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py` | 64 通过、退出 0。候选的后端和 MySQL 夹具文件摘要与 QA1 交接一致，本轮未重复运行 MySQL，供 fresh-context QA2 独立复验。 |
| `git diff --check`、逐项 SHA-256 | 退出 0；与首轮交接对照只有预计的 6 个前端文件变化。 |

新候选仍在同一正式工作树。保留前面的 QA1 候选校验段，QA2 只针对以下完整校验段。合并校验段 SHA-256 为 `6ce3c9c994f40238359e06e35303650c4cc43fdf1c310dad86a77799e628a52d`。

```text
cb345aa58a2a966f48e3542b16d8a8ef1d5876f640014fc371c584743f01c770  CODE_INDEX.md
3162af249511448c2b73e1905f13b666564f40948e01840ac777a38f95ce640c  backend/app/task/api/routes.py
d6407d8c2ab4fd2ab5f6fe98883bf98394616727d9c151613cd934bbd679fa27  backend/app/task/schemas/fields.py
584ff90cc16791b543078ea71015d7f535b669255f10ffd2a724e9e72ae0799b  backend/app/task/services/async_fields.py
c487f25146550d01b26bb38d36884e18dc14998898216703f3e4e783b2dcf921  backend/tests/test_generic_task_flow.py
3d64d0888f280a45687d3fbe89cbc58ecf98e38327063b6b177045a9773fd700  backend/tests_mysql/test_generic_task_shared_batch.py
460992a5361a9c400feda7bec2d8df4b95f726251aaa0a8a299b2ea68f8cdb7b  contracts/published/http-api/generic-task-workflow-v2/README.md
f583baed345f77db6cf2a830e37108d59b4dec1d586390d4be1c144811c3b133  contracts/published/http-api/generic-task-workflow-v2/README.zh-CN.md
b1ec95998da164aceab1f0fbc4bd4e54459bc3886d1919a66b0dfed9480fb275  contracts/published/http-api/generic-task-workflow-v2/examples/requests.json
940fdb28bf879971cf4c91872fda6575d6d8b0a83f90c6d738630e52f0697c61  contracts/published/http-api/generic-task-workflow-v2/openapi.json
f59496513fba39ee11f2bb9515035c1ae477d1a03acbeae75535809660c8d289  docs/generic-plan-performance-guide.md
627f318bc2ecf590253b085e7f0224c8323af2c5b17e0326e6d6b4314b192492  docs/generic-plan-performance-guide.zh-CN.md
fc25cc29e78b6dddc3f9578b82b5629119983688833a406e3f86386346eaebd4  frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md
c14e8185d369997fbb026dc2db0af0e194d8cfec497c9ba0a41ef5d238df5e3f  frontend-js/src/app/performance/locales/en-US.json
b1b167eca2819af01a375379912be620954fdb82ff43d6831f38f9eea4d9ac77  frontend-js/src/app/performance/locales/zh-CN.json
1971f6dd7ea75dc6ddc46bdfb20694eaacda44e12c1e5e07de622c788f829122  frontend-js/src/app/plan/api/index.js
819490ae223dae52cfb4147b1c24af4d843595e14051ddfbd8efbcc8ef2c5ac0  frontend-js/src/app/plan/components/TaskFieldEditor.vue
857ef64a3f6ea45019faa3be440b3030ce8ab25bade8cedc109575860027bb1a  frontend-js/src/app/plan/locales/en-US.json
7122aa63524bd0ac5806b0b3dd22ad9c4902f17322dc75347fa39b4437b9abac  frontend-js/src/app/plan/locales/zh-CN.json
8cb9380e27d779503fc0d13c08fd353f96fdaed7218dfdd57769276130c02281  frontend-js/src/app/plan/views/shared-fields/SharedFieldForm.vue
b0523ff028e2d21247659a254a4eeb7b373b02fe408132becc6be049157cd5a7  frontend-js/src/app/plan/views/shared-fields/index.vue
d22b83381c155cc4001172db503304e1b511a86a2a116f998d46c17d81fb0ed7  frontend-js/tests/module-registry/generic-task.test.mjs
```

`developer_handoff`：请以最新候选启动 fresh-context Verification QA2，重点关闭 QA1 的 AC05，并核对原 AC01–AC11 和前后候选的证据差异。本次新增临时文件为 `/private/tmp/arch-task002-rework-build`、对应 build/tests 日志和原 browser 目录中以 `rework-` 或 `verify-rework` 命名的自检文件。协调者按前述规则收尾。无发布、部署、现有数据库写入或现场操作。
