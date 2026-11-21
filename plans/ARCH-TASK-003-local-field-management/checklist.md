Task ID: ARCH-TASK-003
Revision: r2
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Human Owner 已完成精确 r2 最终验收
Updated: 2026-11-21 Asia/Shanghai

# 独立验证 QA1

**结论为 qa_failed。** 新增本地字段与共享字段重名时，后端安全拒绝写入，两个管理页面都丢失了后端给出的具体原因。R03 要求保留草稿并显示校验失败原因。当前候选需返工。

## QA1-F01 · 本地字段保存时丢失可纠正的校验原因

1. 在隔离配置中预置共享键 `sharedFixture`，以管理员分别为 plan 和 performance 选取空槽 25，添加同名本地键。两个请求均命中真实 FastAPI PUT 路由。HTTP 422，`errorCode=task.invalid_request`，`details={"field":"changes.name","reason":"duplicate_field_name"}`。
2. 在正式源码构建的 Chrome 页面中重放该 422 信封。计划中文页面实际显示「输入的字段、类型或必填值有误。」；实绩英文页面实际显示「A field, type or required value is invalid.」。两个弹窗都保留了草稿 `sharedFixture`，均未指出应更换与共享定义重名的稳定键。
3. 归因于 [错误提示选择逻辑](../../frontend-js/src/app/plan/views/shared-fields/index.vue) 的 `reportFailure`。它仅查询 `shared.reasons.<reason>` 后回落到 `errors.invalid_request`。两模块中英语料均缺 `duplicate_field_name`。同类的保留键也由后端返回 `invalid_field_name`。涉及 [字段校验](../../backend/app/task/services/async_fields.py)、AC05 及 R03。复验应覆盖实际原因的双语显示、两模块和草稿保留。

## 候选与环境

- 在 fresh context 读取批准的 [spec.md](spec.md)、[tasks.md](tasks.md)、工作树代码、任务前态和测试。QA 仓内唯一写入为本文件。交付树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。
- 从 tasks.md 解析 31 行清单，以原始字节核对全部文件和带末尾 LF 的清单摘要。整体 SHA-256 为 `cc4a56a71bd2c1a7c78e7cb88032419f3967d0fc40cee5ff0545488ad6398985`。Development 前态目录内的 76 个文件中，28 个差异均在清单内，另 48 个逐字节相同。前态未收录 MySQL 测试文件和两个新增前端源文件；MySQL 文件以清单及执行结果定位。该比对不覆盖全仓其他并行工作的历史。
- Darwin arm64，Python 3.13.3（项目 backend/.venv），Node v22.19.0，pnpm 11.11.0，无头 Chrome。独立构建与合成 HTTP 浏览器夹具在 `/private/tmp/arch-task003-qa.rgXGML`，前态及原浏览器夹具在 `/private/tmp/arch-task003-dev.gEWwCN`。QA 扩展了浏览器夹具用于错误与列宽验证。API 通过 ASGI 与隔离数据库单独执行，浏览器请求使用合成数据。
- QA 专属 native MySQL 8.4.6 位于 `127.0.0.1:57641`，UUID 为 `1369f5d2-e550-11f1-bc49-258f5c22978e`，测试逐例确认 UTC 偏移 28800 秒并只建、清理随机 `task003_qa_<hex>` schema。受限环境第一次连接收到 EPERM，放行该回环目标后复验成功。凭据由私有环境文件提供。

## 验收矩阵

| 项 | QA1 观察 |
| --- | --- |
| AC01 | 真实两个列表按钮进入各自管理路由，返回后重新读取配置和列表。两个模块均恢复筛选 BROWSER-KEEP、第 2 页、每页 10 条、任务号列宽 255px，并显示新增动态列。历史前进、后退、刷新通过。未登录、supervisor、operator、unknown 直达两个本地路由和两个共享路由时被重定向。API 对未登录返回 401，对上述三个已登录非管理员返回 403。 |
| AC02 | Registry 29 条路由、9 组，两条新路由隐藏且具有 requiresAdmin；原共享入口分别显示共享定义。角色配置两种模式均通过，默认入口和可见菜单与前态核对。全套中三个既有 monitor 排序断言仍失败，见下。 |
| AC03 | 两组主表只显示本组，含停用、双语名称拆列、固定右侧操作。计划无归属，实绩有归属。源码及专项核对筛选、空态、错误和刷新。Chrome 走过中文浅色 1440px 和英文深色 390px 两条流程，包括键盘 Esc 取消。未穷举每个屏幕与语言组合。 |
| AC04 | 24/25 项夹具、20 条默认、页大小 10/20/50/100、跨页选择和修订变更清选核对。桌面真实拖动两个模块各自主表及批量表的字段键列，主表刷新后恢复已存宽度；批量表使用独立键，分别重置清除本表偏好。列表列宽随返回恢复。应用重启恢复以浏览器重新加载及 localStorage 实现覆盖。 |
| AC05 | **失败 QA1-F01**。两组完整字段集合中的停用、被筛掉槽位，以同名或异名新增均阻止 PUT 并保留草稿；另一 scope 同槽可新增。新增、不可变身份、单项、跨页编辑只提交变化、顺序显式 null 的公共实现及测试核对。共享重名后端拒绝正确，界面丢失具体原因。 |
| AC06 | 计划无实绩设置；实绩仅 automated/manual，自动归属关闭实绩编辑；两组不发共享回写。显示设置、无变化与业务设置各自的版本／修订规则及停用后的历史数据保护由专项回归覆盖。 |
| AC07 | 两组各 1、2、100 项成功，实际 HTTP 返回身份顺序、完整响应、单次快照和修订，未选和对侧组保留。浏览器一次本地批删只带当前模块选中的槽 1、21。原 GET/PUT/单删及 shared 批删专项回归通过。 |
| AC08 | 对两组核对未登录、非管理员、坏 module、shared、跨模块或混组、重复、空、超限、额外键、非法类型、错误身份及旧修订；422/404/409 含合同错误信息，全组保留。共享批删依旧限定 shared_sync。 |
| AC09 | 两组分别混合可删项、已用、停用已用、无值已用、历史 dispatch、缺使用或版本证据，改变请求顺序，检查错误位置及整组状态、版本和记录数量。历史数据中完全不可观察的损坏沿用规格限制。 |
| AC10 | 真实 MySQL 24 组双向并发情形，两个模块分别与业务创建、更新、配置保存、单删、共享批删、对侧本地批删竞争，夹具观察到配置首锁等待。另 2 组提交前故障核对全量回滚，共 26 通过。 |
| AC11 | 已知冲突和保护拒绝保留相应目标。两页在 Chrome 分别注入新增和单项编辑的 503 commit_unknown，观察权威重读后的不存在或属性不符、保存被禁、草稿保留和写次数不增；专项还覆盖批量编辑未知结果、本地批删丢响应、重读失败和重试只读。 |
| AC12 | 定向后端、MySQL、前端专项、装配、构建完成；合同与实际注册的 16 条路径及合成响应有回归，相关 Markdown 路径可解析，两个模块中英文键树对称，CODE_INDEX 包含新增源。全套前端保留已定位旧失败。 |

## 命令与结果

| 工作位置与命令 | 实际结果 |
| --- | --- |
| backend，`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py` | 92 passed，exit 0。另独立调用 SQLite 夹具和真实路由，验证两组同名字段的上述完整 422 详情。 |
| backend，载入任务 QA 的 `qa/test.env` 后运行 `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests_mysql/test_generic_task_shared_batch.py -k local` | 26 passed，13 deselected，exit 0。 |
| frontend-js，`node --test tests/module-registry/generic-task.test.mjs`、`pnpm check:modules`、`node scripts/check-page-access.mjs --check --mode development` 和 production | 14 passed；装配、角色合同均 exit 0。 |
| frontend-js，`pnpm test:modules` | 95/98，exit 1。对照开工前 94/97 日志，三项标题和 monitor.energy / monitor/consumption 排序差异一致。分别为 “admin, supervisor, operator and unknown share route/menu/default decisions”、 “actual source preserves Core route identity, shell locales and default-disabled demo”、 “five adapted modules retain order, owned bilingual titles and current visible leaves”。 |
| frontend-js，`pnpm build --outDir /private/tmp/arch-task003-qa.rgXGML/dist --emptyOutDir` | 正式树独立构建，exit 0，既有 chunk 体积提示。 |
| QA 临时目录，`node browser.cjs`、`node extended.cjs`、`node widths.cjs` | 均 exit 0。extended 明确观测并记录了 QA1-F01 的两种错误文案；该脚本正常退出仅代表取证完成。 |

## 交接与资源

请 Development 在同一批准范围内修正 QA1-F01，记录新候选清单并重新交给 fresh-context Verification。Human Owner 最终验收待后续 QA。随机测试 schema 已由夹具清理，浏览器及 QA 静态服务已退出。上述两个临时目录及专属实例目录 `/private/tmp/arch-task-003-r1-mysql.AwLToi` 暂供返工复验；协调者在确认无后续依赖后收尾。上述记录足以在临时日志回收后识别候选、失败及复验条件。

## 独立验证 QA2

**ARCH-TASK-003 r1 为 `qa_passed`，QA1-F01 已关闭，交 Human Owner 最终验收。** 本轮在 fresh context 复核两次交接清单，正式树 HEAD 与 QA1 相同。最新 31 项逐字节 SHA-256 全部匹配，带结尾 LF 的清单摘要为 `c06904501318a613b5947dffce0c8c52361cc3d38e29d25d288a5f969e5267ca`。两清单路径及顺序相同；变化限于两模块各两份语料、共享管理页和专项测试，其余 25 项含后端、合同、列表、管理路由和编辑组件的摘要完全相同。

### AC05 与 QA1-F01 的复验

- 从空的 SQLite 内存夹具经真实 FastAPI 路由创建共享字段和两组本地字段。两组分别在空槽 25 提交共享重名、当前本地重名、保留键、含连字符的非法键和超长键。10 次 PUT 均返回 422、`task.invalid_request`、`changes.name`，前两类的 reason 为 `duplicate_field_name`，后三类为 `invalid_field_name`。逐次比较两个模块 GET 的完整配置以及定义、版本快照、使用证据表行数，均相同。每组用原修订改成合法键后成功保存，各推进修订一次。
- 正式树独立生产构建后，以 Chrome 对两个本地路由各跑中、英两种语言。浏览器回放上项实际捕获的 HTTP 错误信封，连续测试共享重名、同组重名、保留键；四种组合均显示对应原因，并保留键、槽位和中英文名称。每次重试仍带原修订 11，修正后只接受一次写入，弹窗关闭，列表重新取数后可见新增列。中文使用 1440px 浅色，英文使用 390px 深色。经两个原共享入口在四种组合提交保留键，仍走 shared 保存并显示该页既有双语回退文案。
- 浏览器使用合成 HTTP，API 另经真实 ASGI/SQLite 与 MySQL 验证。未将分层结果表述为浏览器直连数据库。复核源码 `reportFailure` 的新增分支只在本地保存及 invalid_request 时取本地原因；删除、共享页和提交未知仍走各自既有分支。

### 其余验收项及执行记录

| 验收项 | QA2 证据 |
| --- | --- |
| AC01–AC04 | 四组浏览器流程重跑列表入口与返回、筛选与页码恢复、跨页勾选、共享入口、刷新与历史导航，以及两个本地路由的直达权限。装配和角色合同通过。拖拽、重置与恢复的详细边界沿用同一列宽组件及偏好逻辑的 QA1 实测，见上方 AC04。 |
| AC06–AC09 | 返工未改变表单、保存合同和事务实现。重新执行后端 92 项、前端专项 15 项；结合上方 QA1 逐项矩阵核对权限、归属、版本、批删顺序、历史保护及整批状态。 |
| AC10 | 同一 QA 专属 native MySQL 8.4.6 实例，回环 57641，UUID 和上海时差由夹具在建随机 schema 前检查。重跑 24 个锁序竞争和 2 个物理提交前回滚用例，逐例清理 schema。 |
| AC11 | 复跑前端专项及事务回归，含未知提交后的权威重读与重试；QA1 的 Chrome 注入证据见上方 AC11。 |
| AC12 | 检查合同、示例、Markdown 本地链接、两模块中英文键树、工作树清单与构建入口。前端全套仍有下述三项开工前即存在的失败。 |

环境沿用 QA1 的 Darwin arm64、项目 backend/.venv、Node v22.19.0、pnpm 11.11.0 和无头 Chrome。下列 QA2 临时命令中的 `$Q` 为 `/private/tmp/arch-task003-qa2.bwY6bv`。

| 工作目录及命令 | 结果 |
| --- | --- |
| backend，`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py`；同解释器执行 `$Q/probe.py` | 92 passed；独立 API 拒绝及原修订重试探针通过，均 exit 0。 |
| backend，加载 QA 私有参数后运行上述 pytest 入口并指定 `tests_mysql/test_generic_task_shared_batch.py -k local` | 首次受回环访问限制，放行后 26 passed、13 deselected，exit 0。 |
| frontend-js，`node --test tests/module-registry/generic-task.test.mjs`、`pnpm check:modules`、`node scripts/check-page-access.mjs --check --mode development` 及 production | 专项 15/15；装配 29 个路由、9 组；两种模式角色检查通过，均 exit 0。 |
| frontend-js，`pnpm test:modules` | 96/99，exit 1。与开工前及 QA1 的日志核对，失败仍为上列三项 monitor 菜单排序断言。 |
| frontend-js，`pnpm build --outDir "$Q/rework-dist" --emptyOutDir`；`node "$Q/browser.cjs"`、`node "$Q/shared.cjs"` | 构建及两套浏览器脚本均 exit 0，构建保留已有 chunk 大小提示。Chrome 回环静态服务在放行后实际运行。 |
| 根目录，`git diff --check`、Python 清单/文档链接及 JSON 键树核对 | 通过；交接前再次核验全部 31 文件。 |

仓内本轮只更新本 checklist。QA2 脚本、构建、捕获的合成数据响应和日志在上述临时目录，浏览器与临时静态服务已退出。QA1、Development 和 QA2 的证据目录及专属实例现可由协调者按任务归属清理。最终验收由 Human Owner 决定。

## ARCH-TASK-003 r2 独立验证

**结论为 `qa_passed`，交 Human Owner 最终验收。** 本轮在 fresh context 中核对了批准规格、Development 交接、前态及正式交付树。HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。重新计算带末尾 LF 的 11 项 SHA-256 清单得到 `fa55ce9774c3dadc69085c6ca5a3c8d9d27c5c5c5c5ee87844e24a386c872712`。r1 QA2 的 31 项清单摘要为 `c06904501318a613b5947dffce0c8c52361cc3d38e29d25d288a5f969e5267ca`，与开工前清单逐项吻合；当前 11 项分别属于两个 manifest、TaskPage、三个测试和五份文档，其余 20 项仍匹配 r1 QA2。仓内本轮只写入本 checklist。

| 验收项 | 独立验证观察 |
| --- | --- |
| R2-AC01 | 用正式源码独立生产构建启动 Chrome。计划、实绩两个展开的侧栏均依次显示列表、本地字段管理、共享字段管理。点击第二项进入对应模块原有 local-fields URL，菜单高亮。中、英文面包屑及主卡标题正确，表中可见对应本地样例、无共享样例。直接重载后内容恢复。 |
| R2-AC02 | 给 supervisor 和 operator 两种临时测试身份授权两个列表，两模块侧栏均仅显示列表；直达两本地和两共享 URL 均返回获准列表。未知角色和未登录分别直达四个 URL 都回到登录页。 |
| R2-AC03 | 两个列表旧按钮均已移除。点击现有返回按钮后各自重读配置与列表；输入框恢复 KEEP-R2，HTTP 查询为第 2 页、每页 10 条，重新渲染的任务号列实测 255px。前进、后退和重载均到达预期路由。该探针预置已保存的列表偏好。 |
| R2-AC04 | 中文浅色 1440px、英文深色 390px 分别覆盖两个模块；窄屏沿用收起侧栏的操作，主卡标题在视口内，页面无横向溢出。管理员测试身份默认进入 /plan/list。装配得到 29 条路由、9 组。仓库两模式角色配置与浏览器临时 grants 分开核验。 |
| R2-AC05 | 另用扩展 Chrome 脚本逐一从两个本地和两个共享入口打开新增字段弹窗并用 Esc 取消，两种语言均通过。共享页只显示共享样例。管理页、编辑组件、语料、字段 API 及后端实现均匹配 r1 QA2。沿用上方 r1 AC03–06 的编辑、槽位和版本证据，AC07–10 的接口、保护及 MySQL 并发证据，AC11 的提交未知与草稿证据。本轮接口响应由合成 HTTP 提供，无数据库连接或部署。 |
| R2-AC06 | 专项、构建、两模式角色检查及装配通过。五份指南的入口与页面一致，本地 Markdown 文件链接可解析。交接前重算 31 项字节摘要均符合相应 revision。全套模块测试中的既有失败如下。 |

环境为 Darwin arm64、Node v22.19.0、pnpm 11.11.0、无头 Google Chrome。下文 `$Q` 指 QA 临时目录 `/private/tmp/arch-task003-r2-qa.xC3jqS`。Development 前态与原脚本在 `/private/tmp/arch-task003-r2-dev.88kY7u`。

| 命令（前端命令从 frontend-js 执行） | 结果 |
| --- | --- |
| `node --test tests/module-registry/generic-task.test.mjs`；`pnpm check:modules` | 15/15；装配通过，均 exit 0。 |
| `node scripts/check-page-access.mjs --check --mode development` 及 production | 两次 exit 0，各读取 supervisor 3 项、operator 2 项。 |
| `pnpm test:modules` | 96/99，exit 1。与开工前 baseline.log 对照，三项失败均为上方 QA1 命令记录所列的 monitor 路由及菜单排序断言，标题和 monitor 差异相同。 |
| `pnpm build --outDir "$Q/dist" --emptyOutDir` | exit 0，保留现有 chunk 大小提示。进程内使用 /api/v1、关闭前端 mock 和演示登录并给两个测试普通角色授两个列表权限。临时构建 index.html 摘要为 `067cfcf0c6e452317276ce44e3ce7b7451b30835ec4ea110be7afb7e0938f859`。 |
| `node "$Q/sidebar.cjs"` 与 `node "$Q/dialogs.cjs"` | 首次受限回环监听返回 EPERM，放行后两套均 exit 0。前者复用已审阅的开发夹具，后者增加四页弹窗进入与取消检查。 |
| 根目录 `git diff --check`、Python 原始字节摘要和相对路径检查 | 均通过。 |

独立浏览器及回环服务已退出，日志、四张截图、脚本及构建仅供本次 QA 取证。协调者可在交接后回收上述两个本任务临时目录。无 r2 blocker，Human Owner 最终验收待决定。

### Human Owner 最终验收 · ARCH-TASK-003 r2

2026-11-21（Asia/Shanghai），Human Owner 刷新页面后实测确认，并明确决定：

> 好的，我刷新看了，计划和实绩的『本地字段管理』都在侧栏正确的位置，顶部按钮也没了。ARCH-TASK-003 r2 最终验收通过。

Verification 据此登记精确 r2 为 `owner_accepted`。本条仅记录 Human Owner 对该修订的最终验收。
