Task ID: ARCH-OBS-006
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Acceptance Chain Reference: [已批准 r1](spec.md) → 本记录 → fresh-context Verification → Human Owner 最终验收
Handoff: 正式共享工作树已实施并完成开发自检，交协调者发起独立验证

# ARCH-OBS-006 r1 实施与交接

## 已批准范围与交付标识

Human Owner 于 2026-11-23 批准的 [r1](spec.md) SHA-256 为 `d146f31bbb33a0235f1a18ee31027d1e22f46b9e2e560e6a5eb1422abe0a601b`。实际交付为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 上的未提交变更，基线 HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。共享工作树含其他任务未提交改动，以下列表与实际 diff 共同限定本次交接。

| 范围 | 文件及交付内容 |
| --- | --- |
| 后端 | `backend/app/equipment_observation/api/routes.py`、`schemas.py`、`services/reads.py`、`services/configuration.py`。新增同权限的默认上下文 GET，按已启用数值系列的历史槽位筛选，授权数据中按 `observed_at, id` 逆序选取，返回真实的八小时边界。只读响应增加 `hasCurves`，用于区分未配置可用系列与当前条件无样本。最近任务建议取选定来源最近 100 条合格样本去重。系列线型存既有 JSON，旧客户端省略线型时保留仍存在指标的原设置。 |
| 设备状态 | `frontend-js/src/app/equipment/views/observations/cards.vue`。四页沿用配置和现有读接口。查询与刷新分离，保留独立时钟展开、双语提示、布尔中性标签与缺测提示。真实时间来自有值指标的 `observedAt`；缺测项不复用快照时间。 |
| 过程监控 | `frontend-js/src/app/monitor/views/observations/curves.vue`、`frontend-js/src/app/monitor/components/observations/CurveChart.vue`、`frontend-js/src/app/monitor/views/observations/admin.vue`、`frontend-js/src/app/monitor/api/observations.js`。历史默认跟随最近可绘制样本，手动查询后固定条件，现有图卡支持多区域及独立图例，无有效点不画空轴。配置表单只增加逐系列实线／虚线选择。 |
| 双语 | `frontend-js/src/app/{equipment,monitor}/locales/{zh-CN,en-US}.json`。补齐自动刷新、筛选、时间、空态、图例与线型等本任务文案。 |
| 测试 | `backend/tests/test_equipment_observation_r10_flow.py`、`frontend-js/tests/module-registry/equipment-observation-columns.test.mjs`。扩展原有隔离测试覆盖默认上下文、旧客户端兼容、微秒曲线、显示与条件竞态。 |
| 手册 | `docs/equipment-status-process-monitoring-guide.md`、`docs/equipment-status-process-monitoring-guide.zh-CN.md`。更新曲线线型、默认查询和实时卡片操作。 |

本次未新增源码文件或模块，现有 CODE_INDEX 的模块结构条目仍适用。未启动 Docker、未连接真实库写入或迁移、未手动重载用户服务，也未提交、发布或部署。

## DEV self-check

| 检查 | 实际结果 |
| --- | --- |
| `uv run --frozen --offline --no-sync pytest -q -m no_db tests/test_equipment_observation_r10_flow.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r8.py tests/test_observation_write_sources.py tests/test_observation_receipt_separation.py tests/test_observation_retirement.py` | 退出 0，106 项通过。隔离 HTTP 通过权限、两种空态、同刻、零值、微秒端点、选定来源过滤、旧线型保护等断言。锚点数据包含 140 条样本，其中 128 条为较新但未命中启用曲线的包。 |
| MySQL 方言 SQL 编译及隔离查询计划 | 测试确认使用 JSON 数值类型条件、`observed_at DESC, id DESC` 和 `LIMIT 1`。SQLite 同形时间索引 `EXPLAIN QUERY PLAN` 报告使用 `ix_obs_history_equipment_time_v2`。SQLite JSON 函数用测试适配模拟 MySQL 类型名和标量提取。未连接真实 MySQL，不能把静态 MySQL SQL 审查或 SQLite 查询计划说成 MySQL 运行时 EXPLAIN，也不能对现场高频规模作吞吐承诺。 |
| `pnpm check:modules` | 退出 0，29 routes、9 groups。 |
| `node --test tests/module-registry/equipment-observation*.test.mjs` | 退出 0，24 项通过，包含默认时间精度、迟到默认请求不能覆盖手动查询、图例开关、同刻／缺测数据与设备卡片时钟显示。 |
| `pnpm test:modules` | 退出 1，107 项中 104 项通过，3 项失败与协调者在同基线 clean HEAD（99 项中 96 项通过）得到的用例一致。失败用例为 `admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`、`five adapted modules retain order, owned bilingual titles and current visible leaves`。未改这些期望。 |
| `VITE_API_BASE_URL=/api/v1 pnpm build --outDir <任务临时路径> --emptyOutDir` | 退出 0，Vite 提示已有大 vendor chunk。 |
| Chrome 与真实 HTTP 读取链路 | 临时构建通过一次性 FastAPI 环回 fixture 提供，使用实际观测路由和内存 SQLite 数据，身份为合成账号。检查七个正式页面、全授权来源选中新样本、精确八小时时间和微秒边界、已有线型、图例开关在刷新后保留、两种过程空态、设备筛选、Enter 展开、布尔 `false` 与文本 `"false"` 区别、刷新保留展开、中文桌面和英文深色 390px 窄屏。Chrome 退出 0。没有复用用户服务。 |
| 格式和内容 | 允许范围 `git diff --check` 退出 0；双语键对称和两份手册本地链接通过。 |

## 已知边界与资源

八小时仅限定时间宽度，现有查询保留原始点与缺口。大体量的生产性能取决于实际负载及 MySQL 查询计划，未通过本轮合成验证声明。首次默认上下文和历史查询是两次只读请求，新到样本由下一次刷新展示。实时仍为整包覆盖。

开发专属临时路径 `/private/tmp/arch-obs-006-browser`、`arch-obs-006-build.pidbna*`、`arch-obs-006-release-build.zQB4df*`、`arch-obs-006-uv`、`arch-obs-006-registry*`、`arch-obs-006-ui-tests.log` 已回收。临时 HTTP 服务进程 33583 已终止，关闭的 Chrome context 及删除的临时路径不是交接所需证据。

## developer_handoff

在上述正式工作树按 [批准规格 AC01–AC08](spec.md#7-验收标准) 和文件范围复核。建议独立重跑专项测试、检查当前源变更与并行工作边界，使用独立的合成浏览器与 HTTP 环境。DEV 自检没有独立 Verification verdict，也未替代 Human Owner 验收。

## QA1 返修和重新交接

批准版本仍为 ARCH-OBS-006 r1。QA1 在 [独立验证记录](checklist.md) 中退回 AC04 两项缺陷。此次返修只变更以下源码与专项测试。其余交付范围见上节。

| 文件 | 实际变更 | Git blob |
| --- | --- | --- |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | 相同范围的在途默认发现共用一个请求。改变范围时可开始新请求，已有竞态保护继续丢弃旧结果。只有用户选择或清空会改变下一次默认发现的显式来源，自动回填只更新筛选栏显示。 | `8058bcb2bbc3a1a2cf8ed0ecd8af5c1cde69385f` |
| `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | 增加重复恢复默认、不同条件抢占，以及清空后连续全局发现两项回归。 | `2ce95df31d0e6b924e958ce04c44abf28bf7c6f3` |

| 检查 | 实际结果 |
| --- | --- |
| `node --test --test-name-pattern='process page discovers' tests/module-registry/equipment-observation-columns.test.mjs` | 返修前两项新断言失败，12 次操作发出 12 个请求，二次全局恢复实际限定为 `newest`。返修后退出 0，3/3（含两个子用例）。 |
| `pnpm check:modules` 与 `node --test tests/module-registry/equipment-observation*.test.mjs` | 均退出 0，29 routes、9 groups，专项 26/26。 |
| `pnpm test:modules` | 退出 1，106/109 通过。三项失败名称与上节所列 clean HEAD 基线一致。 |
| `VITE_API_BASE_URL=/api/v1 pnpm build --outDir /private/tmp/arch-obs-006-qa1-final-build --emptyOutDir` | 退出 0。Vite 报告既有 vendor chunk 体积提示。 |
| Chrome 验证 QA1 两条路径 | 真实生产构建渲染温度曲线页，浏览器拦截并提供合成 HTTP 响应。保持首个默认请求在途时点击「恢复默认」12 次，只发出一个默认 GET。显式选 B 后按 B 查询，清空后全局发现 A，再次恢复默认时全局发现 B。脚本退出 0。真实 FastAPI 及权限覆盖见首次 DEV self-check，本次没有重新运行后端。 |
| `git diff --check -- frontend-js/src/app/monitor/views/observations/curves.vue frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | 退出 0。 |

返修使用的临时构建、Chrome 上下文及输出已回收。未连接用户正在运行的服务，未操作真实数据或设备。

### developer_handoff · QA2

交接对象为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 内的未提交候选，HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，批准 spec SHA-256 `d146f31bbb33a0235f1a18ee31027d1e22f46b9e2e560e6a5eb1422abe0a601b`。候选包含首次交接范围和上表两项返修，工作树中的并行改动依首次范围排除。请独立复验 AC04 两项及当前候选的 AC01–AC08，尤其是 QA1 尚待浏览器复核的场景。

## QA2 返修和重新交接

此次修复 r1 的 AC02 F03 与 AC05 F04，保留前两次交接的其余实现。F03 的 Tooltip 改以外层容器作为触发器，时钟按钮保留自己独立的 `aria-expanded`、双语名称与原生键盘操作。F04 只在 600px 及以下的三个过程曲线页应用局部布局。展开时导航区移到内容上方，限高且可滚动，收起时继续使用现有浮动菜单。离开曲线页后恢复项目原布局。没有修改共享布局组件、路由、侧栏状态、后端或接口。

| 返修文件 | Git blob |
| --- | --- |
| `frontend-js/src/app/equipment/views/observations/cards.vue` | `21827475c3578c60e56aeef1ec99b7bb9dee8d4e` |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | `57d7e58978a124bab9725fffd4aef066a4cd6d06` |
| `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | `d738ee970918c5d5da8f4d30182c8eabdcba15c1` |

| DEV 检查 | 实际结果 |
| --- | --- |
| `node --test tests/module-registry/equipment-observation*.test.mjs` | 退出 0，26/26。现有设备渲染用例模拟 Tooltip 对触发元素的属性覆盖，复核时钟按钮展开及收起；QA1 两项回归仍通过。 |
| `pnpm check:modules` | 退出 0，29 routes、9 groups。 |
| `pnpm test:modules` | 退出 1，106/109 通过。失败三项仍与首次交接所列 clean HEAD 基线一致。 |
| `VITE_API_BASE_URL=/api/v1 pnpm build --outDir /private/tmp/obs006-devqa3.jQVzYu/dist --emptyOutDir` | 退出 0，有既有 vendor chunk 体积提示。 |
| Chrome 生产构建，正式设备页 | 隔离合成 HTTP 响应。中英两种语言均验证实际按钮 `aria-expanded` 的 false → true → false，鼠标悬停和键盘聚焦独立显示 Tooltip，Enter、Space 和点击可操作，其他卡不联动。英文场景验证自动刷新后仍保持展开。 |
| Chrome 生产构建，正式温度曲线页 | 英文深色 390×950，首次进入保留默认展开导航。导航高度 150px，画布宽 298px，根文档宽 390px。两区域各 289 个跨日数据点，实际悬停显示 `2026-11-22 22:36:40` 和两个系列的值 123。图例开关、收起和重新打开导航均通过。从导航跳到设备生产参数页后，侧栏恢复 236px 原布局。 |
| Chrome 生产构建，QA1 回归 | 同范围连续按恢复默认 12 次仅发一个在途 GET。选择来源、清空、全局发现 A、再次全局发现 B 均通过。脚本退出 0。 |
| 范围差异检查 | 三个返修文件的 `git diff --check` 退出 0。 |

本轮浏览器拦截了 HTTP 请求，无真实数据或设备访问。后端代码未变化，实际 HTTP 路由及内存 SQLite 证据见首次自检和独立记录。任务临时构建、浏览器上下文及合成输入已回收。

### developer_handoff · QA3

交接对象是正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交候选。HEAD 仍为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，已批准规格 SHA-256 仍为 `d146f31bbb33a0235f1a18ee31027d1e22f46b9e2e560e6a5eb1422abe0a601b`。范围以首次交接表和本节三项 blob 为准，排除并行工作。请独立验证 F03、F04 和 F01、F02，并按已批准规格记录 AC01–AC08。

# ARCH-OBS-006 r2 实施与交接

Revision: r2
Status: developer_handoff
Owner Role: Development

本节记录已批准 [r2](spec.md) 的实施。以上 r1 开发及返修记录保留。正式工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，当前批准 spec SHA-256 `436244bcd110fafc32276414bc41d65a286f773cd3515721919be41cbd398f62`。交接为未提交候选。

## r2 交付内容

- 复用现有历史默认上下文 GET，增加可省略的 `taskNo` 参数。服务在授权来源和原有可绘制条件内按规范化任务号过滤，再按 `observed_at DESC, id DESC` 选取锚点。返回结构、源权限和可绘制判定沿用 r1。
- 曲线页单独展示用户选择的来源范围和标题栏实际结果来源。任务输入支持直接输入并查询，也可从现有建议中选择。自动范围不会限制下一次任务发现，手工完整范围优先。输入不完整、非法或倒置时保留当前已应用条件。任务发现成功后固定已应用来源、任务和范围，刷新保留精确端点。
- 保持原共享状态标签、自动刷新开关与图表交互。使用请求代次丢弃迟到结果，同条件在途发现共用请求。空结果、曲线未配置、权限错误和目标不可用分别反馈。

| 文件 | 正式候选 Git blob |
| --- | --- |
| `backend/app/equipment_observation/api/routes.py` | `ab6743ddb56090e7084513796b78cf118a398e5d` |
| `backend/app/equipment_observation/services/reads.py` | `9d9d048ea210625799ac4c3382a264cb28f13b49` |
| `backend/tests/test_equipment_observation_r10_flow.py` | `6db4274cddcb1b42ddd0cc1c375d041c2109d1d5` |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | `0880b85919ecb9b94946222974eb2aa2667d1894` |
| `frontend-js/src/app/monitor/locales/en-US.json` | `0d8aa066104dad68e593d12267b9548c85660082` |
| `frontend-js/src/app/monitor/locales/zh-CN.json` | `f7498258e13f5e8a643ad997d050158166f6551d` |
| `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | `8270714f65dbc1f808538c37073fb041ce17272a` |
| `docs/equipment-status-process-monitoring-guide.md` | `a1b7aeb70dddabca59c93f7159c7531bd23afff5` |
| `docs/equipment-status-process-monitoring-guide.zh-CN.md` | `744e5cfceefa35f93b473af6a2cfee2dde0c1153` |

未新增项目源码文件，索引中的模块结构仍适用。API 客户端现有参数透传足以承载 `taskNo`。

## r2 DEV self-check

| 检查 | 实际结果 |
| --- | --- |
| 隔离后端专项 | 用任务专属 `UV_CACHE_DIR` 执行 `uv run --frozen --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_equipment_observation_r10_flow.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r8.py tests/test_observation_write_sources.py tests/test_observation_receipt_separation.py tests/test_observation_retirement.py`。退出 0，106 项通过，1 条 SQLite datetime adapter 既有弃用警告。包括旧任务、授权交集、0 和 unknown、同刻、微秒、无数据、非法输入和 503。 |
| 查询 SQL 与索引 | 正式 SQLAlchemy 查询用 MySQL 方言编译，任务号等值条件在排序和 LIMIT 前，保留来源与数值条件。隔离 SQLite 对跨两来源的带任务查询命中同形 `ix_obs_history_task_time_v2`，未带任务的单来源查询命中 `ix_obs_history_equipment_time_v2`。现有迁移已声明两个索引。本轮未测量 MySQL 运行时计划或现场吞吐。 |
| 前端专项 | `node --test tests/module-registry/equipment-observation*.test.mjs` 退出 0，27/27。包括 12 次重复任务查询合并、较迟结果不覆盖新结果或草稿、恢复默认来源、错误后重试同一任务和手工未填全时保留结果。 |
| 模块检查与生产构建 | `pnpm check:modules` 退出 0，29 routes、9 groups。`VITE_API_BASE_URL=/api/v1 pnpm build --outDir /private/tmp/obs006-r2-dev.iEGoQj/dist --emptyOutDir` 退出 0，既有 vendor chunk 体积提示。 |
| 全量前端模块 | `pnpm test:modules` 退出 1，107/110 通过。仍只有 r1 已与 clean HEAD 对照的三个基线失败，用例名称相同。 |
| Chrome 157.0.8103.79 与实际 HTTP | 生产构建由独立 uvicorn 随机环回端口同源提供，使用 FastAPI 正式观测路由、合成身份与内存 SQLite，目标 guard 和 MySQL JSON 语义用夹具适配。首次来源 Line、任务 LATEST。实际输入 ` older-b ` 后直接查询，在 Second 找到 OLDER-B，端点 `2026-11-21T22:00:00.654321+08:00` 和 `2026-11-22T06:00:00.654321+08:00` 原样请求，历史值为 `[0, 1.25, 2.5, 3.75]`，包含两端和同刻点。手动刷新和开启轮询继续使用该 `to`。切任务到 OLDER-C 改用自己的锚点。选择与自动结果来源相同的 Line 后查询仅限 Line，空结果无曲线，清除选择后重新发现 Second。 |
| Chrome 手动时间及兼容 | 手打 `2026-11-21 23:30:00` 至 `2026-11-22 05:30:00` 只发曲线 GET，保留手选时间与实际来源。仅清空一端、起止倒置均展示错误且不发请求。清空整个范围后再次按任务定位。恢复默认、区域选择及图例切换通过。浏览器脚本退出 0。环回实际 HTTP 另验证 401、403、422。并发竞态控制见前端专项。 |
| 格式与 i18n | r2 文件 `git diff --check` 退出 0，观测模块中英文 locale 键对称。 |

## developer_handoff · r2

独立 Verification 请核对本节的九个文件指纹与已批准规格，区分 r1 交付、并行 DIRECT 变更和 r2 差异，按 R2-AC01–R2-AC07 验证。DEV 无现场、真实 MySQL 或 PLC 证据。未触达数据库 schema、迁移、历史业务数据、用户服务、Docker 或提交。任务自有环回服务、Chrome 上下文和 `/private/tmp/obs006-r2-dev.iEGoQj` 工件已回收。
