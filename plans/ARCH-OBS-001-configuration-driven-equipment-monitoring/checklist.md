Task ID: ARCH-OBS-001
Revision: r7
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r7 QA3 交 Human Owner 对精确隔离候选作最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r7 §9.5 R7-AC01–07

# r7 QA3 独立验证

2026-11-11（Asia/Shanghai）。命名 `verification` 以 fresh context 接收 [r7 QA2 返工交接](tasks.md#r7-qa2-返工-development-交接)。按根与最近作用域的工程契约、canonical lifecycle workflow、角色合同和任务三文件核验，采用 `project-governance`、`aiis`、`backend-arch`、`frontend-ui` 与 `i18n-workflow`。本轮复验三处 Vue 差异，使用与 DEV、QA2 分离的合成实例运行 HTTP、SQL 和 Chrome。经字节对照确认适用的 QA1／QA2 独立证据在下文引用。角色权责为 `contract_only`。 [Human Owner 批准](spec.md#r7-acceptance)

## QA3 候选与隔离环境

| 对象 | 证据 |
| --- | --- |
| 获批规格 | SHA-256 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。批准原话「批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证」。 |
| 精确交接 | `tasks.md` SHA-256 `13599c36c486980da5880c353b9b91aaef1e61795b9af83d16b6b7a592421911`，新段自第 470 行起。原 49388 字节前缀 SHA-256 `157ccac9ceb5b9ae9482f7070161d9779075bd1e79346311fa77de201df68bc4`。 |
| 冻结基线与正式候选 | `runtime/arch-obs-001-r7/baseline` 为 HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 的获批补充源码，888 文件树 SHA-256 `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f`。`runtime/arch-obs-001-r7/source` 为 924 文件候选，有序 `sha256  相对路径\n` 摘要 `a54e4a777e728ffef3d4a7a14e0d74ca0b93c1111eb18ccae15e8cb495a4c7bf`。全部 57 个基线差异逐项符合 §9.4。 |
| 重建与 QA2 差异 | [canonical 补丁](evidence/r7-source.patch) SHA-256 `d753328ceeb32cdd2cbd5387e221e14376403ef6024ea9cc0cf7adf7f5b00e46`，[清单](evidence/r7-source-baseline.json) SHA-256 `df0145272f56505929e63e1c2a4c77d13b84acc88cead36359de5224f4f6d5e1`。使用冻结副本分别应用 [QA2 补丁](../../runtime/arch-obs-001-r7/output/qa2-source/r7-source.patch) 与当前补丁，逐项重建匹配各自 924 文件。与 QA2 相比，仅设备共用 `RecordList.vue`、设备 `views/observations/admin.vue`、过程 `views/observations/admin.vue` 三个获准文件变化。复核列仅改变显示，名称／标题的表头随单元格语言选择，原 `prop`、保存路径及列宽键保留。其他 921 文件与 QA2 逐字节一致，包含后端、迁移、合同、权限装配、词典和测试。 |
| QA3 专属数据库 | MySQL 8.4.6，`aiis-arch-obs-001-r7-qa`，`127.0.0.1:13396`，`arch_obs_r7_qa`，专属账号 `arch_obs_r7_qa_app`。走读前 SQL 实测 UUID `bfbc0a82-dda1-11f1-a9fe-ba45c7e74587`、会话偏移 28800 秒、revision `5f7a9c1e3b26`。协调者的该目标预检为 0 表，迁移日志显示空库显式升级，末段为 `4e6a8b0d2f14 → 5f7a9c1e3b26`。独立 SQL 查得七张 r7 表。DEV 和 QA1／QA2 目标与证据见下方历史。 |
| QA3 实际 Web 与 API | Web `127.0.0.1:15396`，FastAPI `127.0.0.1:18396`。两端初次默认沙箱探测退出 7，经允许的本机回环访问均返回 200。`lsof` 实查两个监听进程的 cwd 分别为交付候选的 `frontend-js/` 和 `backend/`。由协调者用隔离 profile 启动 `python main.py` 和 `pnpm exec vite --host 127.0.0.1 --port 15396 --strictPort`，Web mock 关闭。独立 Chrome 从正常登录入口发起业务请求，相关响应与 MySQL 的新行一致。 |
| 工具 | macOS 15.7.7 arm64、Apple Git 2.50.1、uv 0.7.8、CPython 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.39、Playwright 1.64.0-alpha-1789764292000。 |

## QA3 验收结果

| 验收项 | 结果与证据 |
| --- | --- |
| R7-AC01 源码与隔离 | **通过 §9.5 的可复核性要求。** 哈希、冻结基线重建、57 个允许差异、运行目录、隔离目标、回收与实际构建均可核对。两项后端和四项前端旧断言的失败保留，见命令记录。 |
| R7-AC02 迁移和兼容 | **通过。** QA3 新库通过当前 head 和七表核对，v2 新写与观察写读取实测成功。已重建的 QA2 与当前候选的后端、迁移、旧合同字节一致。带数据升级、旧／新 profile 各自匹配、错配拒绝、旧 typed 数据及回执、受控维护和只撤七表的隔离降级采用原独立证据。QA3 未重复降级。 [QA2](#r7-qa2-独立验证) · [QA1](#r7-qa1-独立验证) |
| R7-AC03 接入合同 | **通过。** QA3 实际调用两身份的指标发现 GET、最简第三方及完整合成 SMA 信封的两路 POST。四条新回执和槽位对应见下。错误或停用凭据、越权、显式 `null`、坏质量、禁用指标、字段及类型负例采用相同后端的 QA2 独立 HTTP 证据。 [QA2](#r7-qa2-独立验证) |
| R7-AC04 任务证据 | **通过。** QA3 两份新合成事实实际通过 v2 HTTP 接收，任务点原值与 API、MySQL、Web 任务号均为文本 `000042`，有两次各自的来源证据。换单、迟到 A、B 缺组、空闲／未知／过期／错绑、伪造引用和前导零卷号使用相同实现的 QA2 独立证据。 [QA2](#r7-qa2-独立验证) |
| R7-AC05 数据与重试 | **通过。** QA3 同一实时行从第三方覆盖到合成 SMA，历史分别追加，四回执持久，第三方原事件实时重放返回相同回执。MySQL 证实独立槽位和布尔 `false`。旧包、冲突、同源去重、断连重放、独立补投、首用锁、100 槽上限及数值 `0` 的实库证据来自相同后端的 QA2。 [QA2](#r7-qa2-独立验证) |
| R7-AC06 页面与权限 | **通过。** QA2 两项返工缺陷在 Chrome 关闭。两种详情、三张配置表的中英表头及内容一致，历史两种标记和空值按语言显示，采集质量独立，实际 PATCH、详情与列表 GET 和 MySQL 均保留原枚举。六处受影响列均验证拖拽、双语间保留、重开／刷新及复位。温控卡片与曲线用新数据复跑。其余卡片／曲线页、两条产线、既有及退役入口、管理员设备约束、编辑白名单和读／机器角色拒绝由 QA2 的独立 Chrome／HTTP／SQL 证据与本轮字节差异共同支撑。 [QA3 浏览器结果](../../runtime/arch-obs-001-r7/output/playwright/qa3-browser-result.json) · [QA2](#r7-qa2-独立验证) |
| R7-AC07 交接与复跑 | **通过。** 用 `000042` 将新的合成事实、请求、回执、MySQL 值与 Web 对照。重读双语走读与机器合同，SMA 独立读身份、`plc-facts-read`、PLC/DB `readScopes`、两路观察写 Bearer、SMA-004 产品投递、DAA-010 和精确 provider 审批与联调步骤均有入口。 [中文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.zh-CN.md#后续-sma-取数和-daa-联调前置条件) · [英文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.md#prerequisites-for-future-sma-reads-and-daa-integration) |

## QA3 Chrome 返工复验

Chrome 通过 `/login` 登录隔离管理员，真实登录 POST 返回 200。Playwright 脚本退出 0，8 组检查通过，0 pageerror。管理页用 `000042` 筛选后读取实际 API，按返回记录 ID 对照表格行。截图在对应表头、卡片、曲线或弹窗可见时采集，设置 `animations: 'disabled'`，同一状态连续两张 PNG 字节一致后保留，并目视复核全部 14 张。JSON SHA-256 `ed0fd9b94e78109b0c6de0efb8bd921e8f38f562416360e52353664b8c8ec750`，内含每张 PNG 的 SHA-256。 [浏览器结果](../../runtime/arch-obs-001-r7/output/playwright/qa3-browser-result.json)

| 表面 | 中文表头／单元格 | 英文表头／单元格 | 实际列宽 px |
| --- | --- | --- | --- |
| 指标配置 | 中文名称／实际温度 | English name／Actual temperature | 180 → 240 → 180 |
| 卡片配置 | 中文标题／加热区 1 | English title／Heating Zone 1 | 190 → 250 → 190 |
| 曲线配置 | 中文标题／加热区 1 | English title／Heating Zone 1 | 220 → 280 → 220 |
| 实时快照详情 | 中文名称／实际温度 (°C) | English name／Actual temperature (°C) | 180 → 240 → 180 |
| 过程历史详情 | 中文名称／实际温度 (°C) | English name／Actual temperature (°C) | 180 → 240 → 180 |
| 过程历史列表 | 复核标记／异常、已复核、空白 | Review flag／Abnormal、Reviewed、空白 | 130 → 190 → 130 |

各配置表用稳定 `nameZh`／`titleZh` 偏好键，详情用各自 `nameZh`，历史列表用 `reviewMark`。拖动后通过语言切换及重载页面或重开详情保持中间宽度，恢复默认后 DOM 宽度复位且对应本机键清除。两详情的 `quality=good` 分别显示为「采集质量／正常」与「Source quality／Good」。 [实时详情中文](../../runtime/arch-obs-001-r7/output/playwright/qa3-latest-detail-zh.png) · [历史详情英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-history-detail-en.png) · [指标配置英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-metrics-en.png) · [卡片配置中文](../../runtime/arch-obs-001-r7/output/playwright/qa3-cards-zh.png) · [曲线配置英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-curves-en.png)

中文下拉保存了历史行 4 的 `abnormal` 和行 3 的 `reviewed`。两次 PATCH 均为 HTTP 200、`application/json`，请求和响应 `reviewMark` 保持英文枚举，重新读列表及打开详情均保留。未标记对照行 2 的 GET 为 `null`。SQL 对三行读回 `NULL`、`reviewed`、`abnormal`，各行的 `quality` 均为 `good`，采集槽位与回执 ID 与对应样本一致。 [历史列表中文](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-history-marks-zh.png) · [历史列表英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-history-marks-en.png)

## QA3 合成任务 000042 走读

在候选 `backend/` 执行 `uv run --offline --frozen --no-sync python ../contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18396`，以私有合成凭据运行并退出 0。走读仅使用 Python 标准库。该次命令未传隔离项目环境位置，uv 创建了无项目依赖的临时 `.venv`，交协调者回收。运行中 API 使用协调者单独准备的锁定项目环境。走读脚本以 200 验证两份 v2 事实、两种身份的历史指标发现、四次 POST、实时重放和卡片／曲线／详情读回。两份事实均为 `plc-01/DB42`，绑定点 `point-active-task-no` 为 `"000042"`。以专属 MySQL 客户端执行只读事务，对照四个回执、任务证据与值表行。

| 来源 | 两路请求及绑定任务点证据 | MySQL 回执与值 |
| --- | --- | --- |
| 第三方 | 原事件 `vendor-1794383023214123`，证据样本 `demo-external-1794383023214123`，原时刻 `2026-11-11T15:43:32.000000+08:00`。实时省略质量和固定接入字段，历史显式 `quality=good`。两路实测／设定均为 811.2／815.0。 | 实时／历史均 `stored`，回执 ID 5／6，结果行 1／3。实时重放响应等于原回执。历史槽位 `{"07":811.2,"08":815.0}`。 |
| 合成 SMA | 完整信封事件 `demo-latest-1794383023214123`／`demo-history-1794383023214123` 共用样本 `demo-sma-1794383023214123` 和原时刻 `2026-11-11T15:43:42.000000+08:00`。 | 两路均 `stored`，回执 ID 7／8，结果行 1／4。实时覆盖行 1 后槽位 `{"01":812.2,"02":815.0,"03":false}`，历史行 4 追加 `{"07":812.2,"08":815.0}`。 |

Chrome 的当前任务为 `000042`，炉区 1 卡片读取 812.2／815.0。截图时合成采样已超过陈旧阈值，卡片显示 `Stale`。过程曲线查询使用同一任务号，实际温度序列读出 811.2／812.2，设定温度 815.0。两份走读间的缺样在 ECharts 两个序列均有 `null`，`connectNulls=false`，共用一个 °C 纵轴。 [温控卡片](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-temperature-card.png) · [温度曲线](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-temperature-curve.png)

## QA3 命令与已知测试结果

| 检查 | 结果 |
| --- | --- |
| `shasum -a 256`、内联 `python3` 文件树与清单比对、冻结副本 `git apply --check --whitespace=error` 及 `git apply --whitespace=error` | 退出 0。重建 QA2 和当前候选，两个 924 文件树各自完全一致。QA1 补丁及候选清单也匹配存档摘要。设备 131、过程 209 个双语键逐项对称。 |
| `node --test tests/module-registry/equipment-observation.test.mjs` | 退出 0，2 通过。覆盖四卡片和三历史页装配、受限管理路由及历史缺样断点。 |
| `pnpm_config_verify_deps_before_run=false pnpm check:modules` | 退出 0，28 路由、10 分组。初次未禁用依赖预检，pnpm 的尝试重装因无 TTY 中止，退出 1。 |
| `pnpm_config_verify_deps_before_run=false pnpm build --outDir <QA3 私有目录>/qa3-dist` | 在显式隔离页面授权 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='["equipment.temperature","monitor.temperature"]'`、`VITE_OPERATOR_PAGE_ACCESS_JSON='[]'` 和 mock 关闭条件下退出 0，转换 2314 模块。保留外部 outDir 和大 chunk 提示。首次缺少两个页面授权环境变量，构建按既有配置校验退出 1。 |
| `pnpm_config_verify_deps_before_run=false pnpm test:modules` | 退出 1，53 通过、4 失败。仍为 `page-access.test.mjs` 第 37、139 行与 `registry.test.mjs` 第 249、299 行的旧路由、访问清单或可见叶子断言，涉及已按 §9.1 退役的 `monitor.realtime`。 |
| QA2 受影响后端八文件 `pytest -q -p no:cacheprovider -m no_db` | QA2 退出 1，133 通过、3 跳过、2 失败。本轮后端及测试字节一致，未重跑该套件。两项失败为 `test_business_integration_migration.py::test_exact_chained_64_71_75_stages_and_four_table_parity` 的旧迁移文件数量，以及 `test_legacy_acquisition_retirement.py::test_single_head_and_metadata_retire_only_nine_tables` 的旧 metadata 全集。六项旧断言的更改均超出 §9.4 的既有测试允许范围，保留失败结果。 |
| Playwright `node <QA3 私有目录>/qa3-browser.mjs`、走读和 `mysql --defaults-extra-file=<QA3 私有 client.cnf> --batch --raw --skip-column-names` | 均退出 0。私有脚本及设置文件中的凭据未输出。SQL 验证限 `START TRANSACTION READ ONLY` 后查询 `metric_ingest_receipts`、两值表及 `INFORMATION_SCHEMA.TABLES`。可核查结果保留在本节、走读与浏览器证据中。 |

## QA3 收尾与 handoff

协调者按本轮归属停止专属 API 与 Vite，退出码分别为 0 与 1（SIGINT），`lsof` 确认两个端口无监听。核对容器 ID `9e4289b11f2ed9878e57177d53ceaab5ae2f75bb920408b8368e7e569db86f55`、任务／轮次标签、端口、SQL UUID 和 schema 后，协调者执行 `docker stop --timeout 5 <精确 ID>`、`docker rm <精确 ID>`、`docker volume rm aiis-arch-obs-001-r7-qa-db`，均退出 0。协调者复查任务标签匹配的容器与卷均已不存在，13395／13396／18395／18396／15395／15396 均无监听。QA3 私有凭据、日志和生成目录交协调者按归属收尾。验收证据保留在隔离交付源码、冻结基线、两份 canonical 源码证据、QA1／QA2 补丁与清单、QA3 14 张 PNG 及 JSON 和本记录中。

**ARCH-OBS-001 r7 QA3 为 `qa_passed`，覆盖 R7-AC01–07。** QA2 的两项本地化缺陷已关闭，无待返工或阻塞的 r7 验收项。两项后端与四项前端旧断言失败继续作为已知测试限制。交 Human Owner 对树摘要 `a54e4a777e728ffef3d4a7a14e0d74ca0b93c1111eb18ccae15e8cb495a4c7bf` 的隔离候选作最终验收，目前待决定。

本结论覆盖合成 v2 HTTP、第三方直连和合成 SMA 完整信封，以及隔离 Web 和 MySQL。实际 SMA 产品取数与投递、DAA、PLC、真实 profile、现有运行环境采用、性能和长时运行、源码整合、部署和发布各依后续批准验证。3307／8000／5190 不在本轮操作范围。原 QA2 断连重放证据覆盖客户端未知结果，数据库提交层故障注入未执行。

## r7 QA2 与更早独立验证记录

以下标记之间逐字节保留 QA3 写入前的 checklist 全部 74241 字节，SHA-256 `e1b7255f8360fd4273e8def8309b1601bdb65670b048eade849ea6fae85a4967`。

<!-- ARCH-OBS-001-r7-qa2-checklist-history-begin -->
Task ID: ARCH-OBS-001
Revision: r7
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r7 QA2 的 R7-AC06 管理界面本地化缺陷返回 Development，后续交 fresh-context Verification 复验
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r7 §9.5 R7-AC01–07

# r7 QA2 独立验证

2026-11-11（Asia/Shanghai）。以实际命名 `verification`、fresh context 接收 [r7 QA1 返工交接](tasks.md#r7-qa1-返工-development-交接)。依据 [Human Owner 对 r7 §9 的精确批准](spec.md#r7-acceptance)，在任务指定的隔离源码和 QA 实例上复验。按根与最近作用域工程契约、canonical lifecycle workflow、角色合同和任务三文件执行，使用 `project-governance`、`aiis`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`。角色权限为 `contract_only`。

## 候选与环境

| 对象 | 本轮证据 |
| --- | --- |
| 批准规格 | SHA-256 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。批准原话「批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证」。 |
| 返工交接 | `tasks.md` SHA-256 `157ccac9ceb5b9ae9482f7070161d9779075bd1e79346311fa77de201df68bc4`，返工记录从第 414 行起。 |
| 冻结基线 | `runtime/arch-obs-001-r7/baseline`，来源 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，888 文件的有序 SHA-256 树摘要 `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f`。 |
| 正式隔离候选 | `runtime/arch-obs-001-r7/source`，924 文件的有序 SHA-256 树摘要 `82d8af23ebd68b56b88ee0dc9fcbfad806eb78446dacf4ec80d4f92bfbf2eada`。逐项扫描目录并核对文件摘要，57 个基线差异符合 §9.4。相对 QA1 仅返工交接列出的 11 个获准文件变化。 |
| 差异重建 | [canonical 补丁](evidence/r7-source.patch) SHA-256 `ff25fe4907deec1491dd7022dcaf81c8a00aba83c41b8b997504f63e009f02f4`，[清单](evidence/r7-source-baseline.json) SHA-256 `54e70feb81f36c7b0826c195d9a43ee982a965de0cc9459db3e51e1469b6015f`。冻结副本上 `git apply --check --whitespace=error` 和 `git apply --whitespace=error` 均退出 0，重建的 924 文件逐项匹配。QA1 的原补丁和清单各自哈希仍分别为 `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb` 和 `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10`。 [QA1 源码证据原件](../../runtime/arch-obs-001-r7/output/qa1-source/) |
| QA 隔离 | 实查 MySQL 8.4.6、`aiis-arch-obs-001-r7-qa`、`127.0.0.1:13396`、`arch_obs_r7_qa`、专用账号 `arch_obs_r7_qa_app`、UUID `01c83fe8-dd98-11f1-bbe4-d675dcc2c00b`、会话偏移 +28800 秒。复用 QA1 降级后带合成事实的库，由 `4e6a8b0d2f14` 升至 `5f7a9c1e3b26`，确认七张 r7 表。FastAPI `127.0.0.1:18396`，Vite `127.0.0.1:15396`。新增清洗、传动授权和间隔，以及只准入第一线的 admin 对照，均使用仓库外 QA 私有合成配置。 |
| DEV 隔离 | [Development 交接](tasks.md#r7-development-交接)记录 MySQL 8.4.6、`127.0.0.1:13395`、`arch_obs_r7_dev`、UUID `c9a8a3ed-dd91-11f1-8e90-e27dd38db63b`、+08:00、API 18395、Web 15395，空库至新 head、受控降级和再升级。DEV 的测试为其自检，本轮独立测试使用 QA 目标。 |
| 工具与收尾 | macOS 15.7.7 arm64、uv 0.7.8、锁定 Python 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.39 与 Playwright。Verification 停止 QA API/Web，`lsof` 确认 18396、15396 无监听。协调者核对精确 ID、标签和端口后已停止并删除 DEV/QA 两个任务容器及 `aiis-arch-obs-001-r7-dev-db`、`aiis-arch-obs-001-r7-qa-db` 卷，操作退出 0，复核 13395、13396、18395、18396、15395、15396 均无监听，也无本轮任务容器或卷。 |

## 验收结果

| 验收项 | 独立结果 |
| --- | --- |
| R7-AC01 源码与隔离 | **通过 §9.5 的可复核性要求。** 候选、基线、补丁、真实启动目录、允许差异、两轮隔离与回收、静态检查和构建均有可复核结果。受影响套件仍有后端 2 项、前端 4 项失败，见下表。实际新增七表和旧页面退役符合 r7，六项旧断言仍然失败。 |
| R7-AC02 迁移和兼容 | **通过。** QA1 的空库起步、旧/新匹配读写、错配及未知版本拒绝、维护计划和仅撤七表的降级证据保留。本轮独立重验带合成旧事实的 QA 库升至新 head、七表存在、新 profile 的 v2 写读和 typed 写入，以及 QA1 的 typed 事件重放返回原记录的 `duplicate`。新写分别为 `qa2-compat-new` 和 `qa2-typed-new`，typed 记录及回执 ID 3。相关采集、兼容性及迁移实现与 QA1 字节相同。 |
| R7-AC03 接入合同 | **通过。** QA2 两身份实际发现、两目标写入和 MySQL 数据对应；第三方可省略字段，显式空实时质量保存为 `unknown`，SMA 缺完整信封拒绝。缺凭据/无效、停用/越权、媒体类型、超长、禁用指标、类型、历史白名单及坏/空质量按独立行为用例复测，历史缺省质量的域用例通过。 |
| R7-AC04 任务证据 | **通过。** 新合成 `QA2-A` 到 `QA2-B` 换单、B 单缺组、晚到 A 按原任务和六位小数原采集时间留存。空闲、过期、错点、未知、伪造引用或原时刻及未获证明的第三方任务被按合同处理。生产实库及 Chrome 均保留文本卷号 `000042`。 |
| R7-AC05 数据与重试 | **通过。** 独立 HTTP/MySQL 验证新建、覆盖同 ID、`stale`、事件冲突、同源历史 `already_stored` 和两目标分开确认。A 单实时成功后历史仍为 0，历史客户端发送后关闭连接，读取到已入库的 1 条，再重放返回该行，实时回执不变。100 槽占满、停用仍占位、超限 422、重复绑定 409，首用后类型/单位更新拒绝，启停保留首用时间。实库保存 JSON 数字 `0`、布尔 `false` 和卷号字符串。 |
| R7-AC06 页面与权限 | **失败。** QA1 的曲线引用、两类详情采集质量和详情设备范围三项均关闭。实际 Chrome 的四卡片、三个带值曲线页、第二条产线、两类分页列表、管理字段编辑、拖拽和重置、入口与角色行为均按下述证据验证。另发现管理页面本地化缺陷，详见返工项。 |
| R7-AC07 交接与复跑 | **通过。** `000042` 的两份合成 v2 事实、第三方省略版与 SMA 完整信封、四次回执、库值及页面相互对应。双语走读及机器合同明确 SMA 独立登录的 `plc-facts-read` 和按 PLC/DB 的 `readScopes`，观察写 Bearer 另授设备/组/目标/指标权限。写明 SMA-004 产品 GET→POST、ARCH-ACQ-001、精确 ARCH-BE-012 provider/合同及隔离独立 QA 与 Owner 验收、精确 DAA-010 批准及新隔离 profile。联调按每个 PLC/DB 对照 SQLite 原样本和冻结请求、后端历史和 latest、回执和 SQLite 持久确认，再核对 SMA 映射和两路观察写入。 [中文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.zh-CN.md#后续-sma-取数和-daa-联调前置条件) · [英文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.md#prerequisites-for-future-sma-reads-and-daa-integration) |

## 命令与结果

| 命令或方法 | 本轮观察 |
| --- | --- |
| 候选 `backend/` 的 `uv run --offline --frozen --no-sync alembic upgrade 4e6a8b0d2f14:5f7a9c1e3b26 --sql`，守卫 QA 目标后的 `alembic upgrade 5f7a9c1e3b26` | 均退出 0。离线 DDL 和数据库都核对七表。通过私有环境运行候选 `python main.py`。 |
| `uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider tests_mysql/test_equipment_observation_mysql.py` | 退出 0，**5 passed**。测试自身先核验 round/UUID/端口/schema/账号/时区/revision。实测双向竞争同指标行锁、曲线保存等待后拒绝布尔引用、类型修改等待后拒绝已提交的曲线引用。另独立通过 HTTP 对启用曲线、停用曲线、启用组内的停用序列逐项 PATCH，均为 409 `equipment_observation.curve_items`，读取类型仍是 `number`，清除引用后 PATCH 200 可变为 `boolean`。 |
| 两组实际设备范围对照 | 用限 `line-01` 的管理员，允许范围的详情（实时 10、历史 8）GET 200。第二条线的真实记录（实时 4、历史 2）和不存在的 999999999，在两类 GET/PATCH 的四个组合均返回 HTTP 404、`application/json` 及逐组相同的响应体 `equipment_observation.not_found`。显式请求第二线的列表均为 403。拒绝前后的第二线有序 SQL 行导出 SHA-256 均为 `98a11060abb9ccb3187563268ed91c2b433149713e426cf0eceb14e147916d98`。 |
| `uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db` 受影响后端八个测试文件，按 QA1 同组 | 所有 bootstrap、mock 和 projection 开关关闭后退出 1，**133 passed、3 skipped、2 failed**。业务迁移测试 `test_exact_chained_64_71_75_stages_and_four_table_parity` 固定 11 个迁移文件，候选为 12。旧采集退役测试 `test_single_head_and_metadata_retire_only_nine_tables` 仍断言旧 metadata 表全集。首跑留有 QA supervisor bootstrap 开关，旧隔离守卫测试额外失败，关闭后已通过。 |
| `pnpm check:modules`、`pnpm build --outDir <QA 私有构建目录>`、`node --test tests/module-registry/equipment-observation.test.mjs` | 均退出 0。28 路由、10 组、新定向用例 2 passed。沿用候选已装锁定依赖，设置 `pnpm_config_verify_deps_before_run=false` 禁止依赖预检尝试重装，构建保留已有大 chunk 提示。 |
| `pnpm test:modules` | 退出 1，**53 passed、4 failed**。原 `page-access.test.mjs` 第 37、139 行和 `registry.test.mjs` 第 249、299 行固定旧 `monitor.realtime`、访问清单或叶子集合。QA1 已证实冻结基线的对应后端旧断言和 Web 断言通过。两项后端与四项前端旧断言的修改超出 §9.4 的精确旧测试范围，保留现状。 |
| Python AST、JSON、Markdown 和 i18n 检查 | 候选 27 个变更 Python 文件解析通过。三条 OpenAPI 路径及全部内部 `$ref`、请求向量和示例 profile JSON 通过解析。设备 131 个和过程 209 个 locale 键的双语集合一致。11 个变更 Markdown 检查 266 个相对链接和锚点，新增失效 0。81 个缺失都来自冻结子集原有的 `CODE_INDEX.md` 外部模块目标，基线已有相同缺项。新索引的代码路径存在。 |
| 候选 Web 和真实 Chrome | `pnpm exec vite --host 127.0.0.1 --port 15396 --strictPort` 代理到 18396。Playwright 10 组脚本断言通过，0 pageerror。实际拖拽两类列表均为 150→231 px，刷新恢复 231 px，重置 150 px。普通 supervisor 登录可读温控，管理页被拒，直接请求管理 API 为 403，机器凭据为 401。两种管理详情的实际 GET 和保存响应为 `quality=good`，DOM 在中英文分别出现「采集质量／正常」和「Source quality／Good」。最新备注和历史备注／`reviewed` 均实际 PATCH 200，重新打开保留。 [独立浏览器 DOM 与接口结果](../../runtime/arch-obs-001-r7/output/playwright/qa2-browser-result.json) |

浏览器结果 JSON SHA-256 `72e1ed6a218c45194147d19f1777c2baa27f71c31014cb299ce2867b7b4e5c92`。部分详情 PNG 采于进入动画，仅显示底层列表，曲线 PNG 也处于初始绘制。详情及曲线值以实际 DOM、ECharts option 与 HTTP 数据记录判定。缺测断点的回归由 QA1 证据与本轮定向模块用例支持。

## 合成任务 000042 的请求、回执和显示

在 QA 候选从 `backend/` 运行 `python ../contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18396`（使用锁定 uv 和 QA 合成凭据），退出 0。实测两份 v2 事实均在 `plc-01/DB42`，`point-active-task-no` 的值为 `"000042"`。下列回执和槽位由 MySQL 只读查询确认。

| 来源 | 两路请求及任务证据 | 回执和库值 |
| --- | --- | --- |
| 第三方 | 原事件 `vendor-1794381796282315`，任务点关联 v2 样本 `demo-external-1794381796282315`，原时刻 `2026-11-11T15:23:05.000000+08:00`。实时为最简请求，历史明确提供 `quality=good`。两路均报实测 811.2、设定 815.0。 | 目标 `latest`、`history` 均 `stored`，回执 ID 17、18，值表行 10、7。实时重放返回同一回执。历史槽位 `{"07":811.2,"08":815.0}`。 |
| 合成 SMA | 完整信封使用 `demo-latest-1794381796282315` 和 `demo-history-1794381796282315`，两者共用 `demo-sma-1794381796282315` 和原时刻 `2026-11-11T15:23:15.000000+08:00`，任务点及数值引用来自已入库事实。 | 两路均 `stored`，回执 ID 19、20，值表行 10、8。较新样本覆盖同一实时行，槽位 `{"01":812.2,"02":815.0,"03":false}`，历史独立追加 `{"07":812.2,"08":815.0}`。 |

同一轮合成清洗 36.5、传动 48.75 分别实写 latest 槽 01 和 history 槽 07，来源样本分别为 `qa2-group-cleaning-1794381791699658`、`qa2-group-drive-1794381791699659`。生产槽位为 `{"01":"000042","02":0,"03":false}`。Chrome 的四个设备页读回上述生产、清洗、传动、温控值。历史温度两序列共用一条 °C 轴，清洗和传动各一条 Hz 轴。第二产线在同一温控页显示 `000043 / 727.0`。 [温控设备页](../../runtime/arch-obs-001-r7/output/playwright/qa2-task-000042-temperature.png) · [曲线和卡片读值](../../runtime/arch-obs-001-r7/output/playwright/qa2-browser-result.json)

## R7-AC06 返工项

1. **历史列表的复核值未本地化。** QA2 实际 Chrome 将 `000042` 温控记录标为已复核并保存，切换中文后，历史列表「复核标记」仍显示内部枚举 `reviewed`。共用组件对该列直接显示 `reviewMark`，该组件的详情下拉与现有字典已有「已复核」和「异常」。按 §9.1、R13 和根 AGENTS §5，普通管理列表也需用中英文显示复核状态，并与采集质量列区分。复验应涵盖中文「已复核／异常」、英文「Reviewed／Abnormal」及未标记状态，保存继续使用既有键。 [实际中文历史列表](../../runtime/arch-obs-001-r7/output/playwright/qa2-task-000042-history-detail-zh.png) · [列表列定义](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/components/observations/RecordList.vue#L28)
2. **英文名称和标题列的表头与数据语言不符。** 静态对照模板和英文 locale 后确认，两类详情共用表以及指标配置表固定表头 `nameZh`（Chinese name），英文时单元格取 `nameEn`。卡片和曲线配置表固定表头 `titleZh`（Chinese title），英文时单元格取 `titleEn`。这些列的表头需准确描述当前展示的名称或标题，复验两种语言下的对应表头及单元格，同时检查既有列宽偏好。此项依据模板与词典，QA2 的浏览器脚本未断言这些表头。 [共用详情](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/components/observations/RecordList.vue#L47) · [指标配置](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/views/observations/admin.vue#L14) · [卡片配置](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/views/observations/admin.vue#L49) · [曲线配置](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/monitor/views/observations/admin.vue#L14) · [英文词典](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/locales/en-US.json#L108)

## Verdict 与 handoff

**ARCH-OBS-001 r7 QA2 为 `qa_failed`。** 原 QA1 四项均已关闭。R7-AC06 本轮发现的两处管理页面本地化问题返回 Development，按同一获准范围固定新候选后交 fresh-context Verification。Human Owner 最终验收待后续 QA。两项后端和四项前端旧断言失败仍需在交接中可见。

本轮实际操作限于批准的隔离 MySQL、API、Web 以及合成事实和请求。现场 PLC、DAA、SMA 产品取数和投递、真实 profile、3307／8000／5190、生产采用、性能与长时运行、整合、发布和部署均未验证。断连用例验证发送方未知结果及回执重放，未注入数据库提交层故障。必要 SQL、HTTP 和命令证据已固化于本记录。保留隔离候选、冻结基线、源码补丁与清单、QA1 原证据及脱敏浏览器产物供复验和 Owner 审核，复验新建同一批准范围内的独立 QA 目标。私有 QA/DEV 凭据、日志和构建目录由协调者按归属收尾，结论无需依赖其保留。

## r7 QA1 与更早独立验证记录

以下标记之间保留 QA2 写入前的 checklist 全部 57315 字节，SHA-256 `3d9c5c749e35de3b596bacef9dbd5cc74e0c798c9232fb847f707dd4c1e35aca`。

<!-- ARCH-OBS-001-r7-qa1-checklist-history-begin -->
Task ID: ARCH-OBS-001
Revision: r7
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r7 QA1 实现与交接说明缺口返回 Development 返工，复验通过后由 Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r7 §9.5 R7-AC01–07

# r7 QA1 独立验证

2026-11-11（Asia/Shanghai）。以 `verification` 命名角色、fresh context 接收精确的 r7 交接。独立读取根及最近作用域的 AGENTS、README／PLAN、canonical workflow、Verification TOML、任务三文件、候选源码、补丁和 DEV 证据。按 `project-governance`、`aiis`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 复核。独立轮次使用自己的合成数据与凭据。角色权责为 `contract_only`。 [批准规格](spec.md#r7-acceptance) · [Development 交接](tasks.md#r7-development-交接)

## 精确候选与环境

| 对象 | 独立核对 |
| --- | --- |
| 批准规格 | SHA-256 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。Human Owner 原话「批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证」。 |
| Development 交接 | SHA-256 `21bfb30971cdaa3268cbf200b6a6e28691b9ec92f98e7efa5bb933990bb488f8`。最初接收的摘要为 `41512d35b31aeb33e841abf715efa95e07316926b7906d70d56aa5c283b2e078`。Development 随后同步顶层 r7 元数据。当前 r7 交接从第 306 行起，候选与补丁摘要未变。独立确认旧 23232 字节历史仍匹配 `8e64a7398d552dde18baf242e15274648b0e9b4eaa0a3bf26737387f1740dca3`。 |
| 正式隔离源码候选 | `runtime/arch-obs-001-r7/source`。924 文件的路径排序 `sha256  path\n` 树摘要 `e7db1a69d1f083bb1a89fd0504ad2e7554ef40c26624b9f7fbd930e7824b4402`。 |
| 冻结基线 | `runtime/arch-obs-001-r7/baseline`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。888 文件树摘要 `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f`。ARCH-ACQ-003 r2 QA2 已验收清单与冻结补充的 53 个路径逐项匹配。 |
| 公开差异 | [补丁](evidence/r7-source.patch) SHA-256 `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb`，[清单](evidence/r7-source-baseline.json) SHA-256 `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10`。逐项匹配 57 个差异与 §9.4。对冻结基线临时副本执行 `git apply --check --whitespace=error` 和 `git apply --whitespace=error` 均退出 0，重建的 924 文件逐项匹配。 |
| QA 隔离目标 | MySQL `8.4.6`，`aiis-arch-obs-001-r7-qa`，`127.0.0.1:13396`，专属账号及 schema `arch_obs_r7_qa`，UUID `01c83fe8-dd98-11f1-bbe4-d675dcc2c00b`，会话偏移 `28800` 秒。FastAPI `127.0.0.1:18396`，Vite `127.0.0.1:15396`。迁移前实查 0 表。 |
| DEV 隔离目标 | 交接记录的 `127.0.0.1:13395`，schema `arch_obs_r7_dev`，UUID `c9a8a3ed-dd91-11f1-8e90-e27dd38db63b`，API `18395`、Web `15395`，空库 → 新 revision → 受控降级与再升级。该轮为 Development 自检。 |
| 工具链和资源 | macOS 15.7.7 arm64、uv 0.7.8、Python 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.39、Playwright。后端以 `uv run --offline --frozen --no-sync` 读取现有锁定依赖，Web 用候选的锁定依赖。QA 账号和 profile 使用仓库外专属目录。QA API／Vite 已停止，`lsof` 核对 18396／15396 无监听。两轮独立 MySQL 和卷保留供返工后复验，QA 库最后为旧 revision。保留候选、冻结基线、补丁和下列脱敏证据；协调者在复验不再依赖时核对归属并回收。 |

## 验收结果

| 验收项 | 独立结果 |
| --- | --- |
| R7-AC01 源码与隔离 | 源码、补丁、环境及回收状态均可复核。离线 DDL、manifest 预检、构建和本轮新增用例通过。受影响套件仍有 2 项后端、4 项前端失败，冻结基线的同组断言通过，详见下文。 |
| R7-AC02 迁移和兼容 | 通过。空 QA 库升级到 `4e6a8b0d2f14`，以旧 profile 写读 v2 样本，写入 typed 温控数据及回执，维护只读计划成功。带样本升级到 `5f7a9c1e3b26`，旧四表按行导出逐字节一致，仅增七表。旧 profile／新 revision 与未知 profile revision 的 v2 写、v2 读、typed 写均返回 503。新 revision 上旧 profile 的维护计划退出 1，新 profile 的计划退出 0。新 profile 的 v2 写读及 typed 写入通过，重放旧 typed 事件返回同一回执记录及合同规定的 `duplicate`。最后仅降级 r7，表集合恢复且旧四表逐字节一致。 |
| R7-AC03 接入合同 | 通过。第三方与合成 SMA 均成功通过发现 GET 和两目标 POST。无效或无凭据 401，停用和越权 403，超长／错媒体类型 413／415，禁用指标、非法类型、历史空值／坏质量和 SMA 信封缺字段的 HTTP 响应均为 422；历史缺省质量由 domain 用例验证拒绝。实时显式空质量保存为 `unknown`；发现仅列当前授权与启用键，历史采用白名单。 |
| R7-AC04 任务证据 | 通过。由 v2 HTTP 接收合成事实，切 B 后只显示 B 的缺测，晚到 A 存在 A 单，按 A 查询保留六位小数与 +08:00。绑定点缺失、过期、空闲分别验证，错点或无法证明的第三方任务及 SMA 伪造引用、错误原时刻被拒绝。生产样本的卷号 `"000042"` 读回保留前导零。 |
| R7-AC05 数据与重试 | 通过。真实 MySQL 观察新建、覆盖同 ID、`stale` 回执、冲突 409、同源历史 `already_stored`、两目标各自回执。A 实时提交后历史仍为 0；独立历史请求发完即关闭连接且不读取响应，历史变为 1，重放返回该同一行，实时回执保持原值。实测 100 槽余量 0，禁用仍占位，第 101 槽 422、重复绑定 409，首用后类型／单位变更 409，槽位停启保留首次使用时间。 |
| R7-AC06 页面与权限 | **失败。** 真实 Chrome 核对四卡片、三曲线、双语、两个管理列表的编辑、列宽、入口与普通读者权限；两条合成产线复用同一页面。发现曲线引用类型不变量、两个详情的采集质量和详情设备范围三个缺陷，见下文。 |
| R7-AC07 交接与复跑 | **失败。** 实际走读与 MySQL、页面对应通过。交付说明没有写清后续 SMA 取数身份，也没有给出 DAA-010 的联调范围和前置条件。 |

## 独立命令与脱敏证据

- 候选后端以 `uv run --offline --frozen --no-sync alembic upgrade 4e6a8b0d2f14:5f7a9c1e3b26 --sql` 生成七张新增表，退出 0。对专属 QA 实例依次运行 `alembic upgrade 4e6a8b0d2f14`、`alembic upgrade 5f7a9c1e3b26`、`alembic downgrade 4e6a8b0d2f14`，均退出 0。旧阶段合成事件 `qa-compat-old`、`qa-typed-old`，新阶段 `qa-compat-new`、`qa-typed-new`，两个 typed 回执分别引用记录 1、2。迁移前后 `plc_facts_history`、`plc_facts_latest`、`equipment_temperature_samples`、`equipment_integration_receipts` 的有序行导出 SHA-256 同为 `fa480d7441bed7f20994dba6540cbf1ade7aa7c906e06742cac51aa2235d67c8`，后续读写后降级前后同为 `71fb0aae94a87298ff34439f758104d78bb5f3796fb01a6299715e80a11f738e`。空库链分段执行，在旧 revision 装配样本后续升。维护执行 `python scripts/plc_facts_maintenance/main.py cleanup-v2 --plan`，明确 alias、UUID、schema、revision 与批准引用，两个匹配 profile 均回报 0 候选，错配拒绝；无 `--apply`。
- 在候选 `backend/` 显式 `python main.py --maintenance bootstrap-users` 建立合成账号，然后 `python main.py` 运行 API。受影响后端 `pytest -q -p no:cacheprovider -m no_db --basetemp=<私有目录>/candidate-pytest` 覆盖 `test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_acquisition_facts_migration.py`、`test_business_integration_migration.py`、`test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_equipment_observation_domain.py`，结果 **133 passed、3 skipped、2 failed**，退出 1。三个 skip 对应需专属 ACQ-003 夹具的旧实库用例，以及固定候选的 BE-003 和 BE-012 B 两个历史用例；另以目标 UUID/schema/端口/账户和轮次 ACK 运行 `pytest -q -p no:cacheprovider tests_mysql/test_equipment_observation_mysql.py`，**2 passed**，退出 0。
- 候选前端 `pnpm check:modules` 退出 0，注册 28 routes、10 groups。`pnpm build --outDir <私有目录>/frontend-dist` 使用显式 supervisor/operator 页面清单，退出 0，保留既有大 chunk 提示。`pnpm test:modules` **53 passed、4 failed**，退出 1。以同依赖运行冻结基线的两个相关后端断言，**2 passed**；冻结基线 `node --test tests/module-registry/{page-access,registry}.test.mjs`，**21 passed**。候选设备与过程 locale 分别 128／209 个键，双语集合一致；三条新 OpenAPI 路径、全部内部引用及样例 JSON 解析通过，变更行的 40 个本地文件链接有效。
- 实际运行 `python ../contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18396`，退出 0。第二次走读的第三方 v2 样本 `demo-external-1794380100142868` 于 `2026-11-11T14:54:49.000000+08:00`，两路 `stored` 回执行 ID 分别 1、6。SMA 合成客户端的 v2 样本 `demo-sma-1794380100142868` 于 `2026-11-11T14:54:59.000000+08:00`，两路 `stored` 回执行 ID 分别 1、7。按 `metric_ingest_receipts` 查询的两个 caller 的各自两路 `task_evidence` 分别指向各自同一采集样本和 `point-active-task-no`。数据库实际温控快照槽位 `{"01":812.2,"02":815.0,"03":false}`，SMA 历史 `{"07":812.2,"08":815.0}`，第三方历史 `{"07":811.2,"08":815.0}`。生产快照为 `{"01":"000042","02":0,"03":false}`。第二产线使用 `plc-qa-02/DB77/qa-other-task` 和独立历史规则，任务 `000043` 的温控快照 `727/730/false`、历史仅 `{"07":727}`。两个调用者的 HTTP 凭据均为合成私有凭据。
- 真实 Chrome 访问候选 `pnpm exec vite --host 127.0.0.1 --port 15396 --strictPort`。四个设备页实际渲染，包括跨页线速度 0、活动 false、缺测和陈旧；温控页切换第二产线显示 `000043 / 727.0`。三过程曲线页面有 ECharts canvas，清洗和传动展示本轮配置的空序列；温度组仅一条 °C 纵轴、两序列且缺采样时插入 null；读取 `000042` 的 `811.2/812.2` 和 `815.0`。最新和历史两张表各完成实际拖拽 `150 → 231 px`、刷新恢复 `231 px` 和重置 `150 px`。两条备注实际 PATCH 200，重新打开仍在；历史标记为 `reviewed`。普通 supervisor 可读温控、无法进入管理页，直接 HTTP 管理操作 403；机器凭据管理操作 401。能耗和采集数据入口可用，退役路径重定向且无菜单入口。浏览器未捕获 pageerror。 [浏览器证据](../../runtime/arch-obs-001-r7/output/playwright/qa-browser-result.json) · [温控](../../runtime/arch-obs-001-r7/output/playwright/qa-task-000042-temperature.png) · [曲线](../../runtime/arch-obs-001-r7/output/playwright/qa-task-000042-temperature-history.png) · [历史详情](../../runtime/arch-obs-001-r7/output/playwright/qa-task-000042-history-detail.png)

## 缺陷与待处理的回归断言

1. **R7-AC06／R11，已启用曲线可保留布尔指标。** 管理员 POST 创建未首次入库的 Hz 数值指标 `qaCurveMutation`，将其加入启用的传动曲线 `qa-mutation`。随后 PATCH `/api/v1/equipment/metric-configs/qaCurveMutation`，发送 `{"valueType":"boolean"}`，候选返回 HTTP 200 并将类型改为 `boolean`。GET `/api/v1/monitor/curve-configs?category=drive` 仍显示该启用序列。R11 要求已登记的数值型指标，更新入口需维持该条件。 [指标更新实现](../../runtime/arch-obs-001-r7/source/backend/app/equipment_observation/services/configuration.py#L54)
2. **R7-AC06／R13，两类详情缺采集质量。** Chrome 打开 `000042` 温控的实时和历史详情，详情 API 与保存响应均含 `quality: good`。两个 dialog 的 `Source quality` 文本计数均为 0。列表有质量列，详情包含来源、指标、备注及历史复核标记，仍缺规格要求的采集质量。 [共用详情模板](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/components/observations/RecordList.vue#L33)
3. **R7-AC06／§9.1，管理详情先按全局 ID 查记录。** 用私有 profile 将 admin 的设备范围限制为 `line-01`，GET 和 PATCH 实际存在且越权的第二产线快照 `5` 和历史 `4` 均返回 403，同类不存在的 `99999999` 均返回 404，显式设备越权列表返回 403。详情通过 `db.get(model, identity)` 后才检查设备，违反服务端先限制设备再查询的要求，并可据响应区分越权记录是否存在。 [详情实现](../../runtime/arch-obs-001-r7/source/backend/app/equipment_observation/services/reads.py#L145)
4. **R7-AC07，后续取数和联调交接缺项。** 双语走读、机器合同和 r7 handoff 说明了后续真实 SMA 产品、DAA 接线与实际启用分别批准，但没有规定后续 SMA 取数身份／读范围，也没有指出 DAA-010 联调的范围、前置条件和与本轮合成 HTTP 验证的接口。该条需补交接说明。 [中文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.zh-CN.md#r7-walkthrough) · [机器合同](../../runtime/arch-obs-001-r7/source/contracts/published/http-api/equipment-observation-v1/README.zh-CN.md)
5. **R7-AC01，候选现有套件六项回归断言失败。** `test_business_integration_migration.py::test_exact_chained_64_71_75_stages_and_four_table_parity` 固定 11 个迁移文件，候选为 12。`test_legacy_acquisition_retirement.py::test_single_head_and_metadata_retire_only_nine_tables` 的旧元数据全集断言因新增七表失败。Web 的 `page-access.test.mjs` 第 37、139 行及 `registry.test.mjs` 第 249、299 行断言旧 `monitor.realtime`、访问清单或原可见叶子集合。真实路由已按 §9.1 退役，真实迁移仅增七表。这六项仍为失败测试，涉及的旧断言或文件超出 §9.4 当前授权的既有测试改动范围，保留原样；任何扩大范围由 PM 和 Human Owner 处理。

## Verdict 和 handoff

**`qa_failed`。** R7-AC06 的三个实现问题与 R7-AC07 的交接说明缺项返回 Development。返工交接应固定新候选摘要、保留本轮记录，并以 fresh-context Verification 重查变更及相关验收。r7 的 Human Owner 最终验收仍待后续 QA 结果。

本轮使用合成 v2 HTTP、合成 SMA 完整信封及第三方 HTTP。未运行真实 SMA 产品、DAA、PLC 或真实 profile，未访问 3307／8000／5190。网络断开覆盖客户端未知结果及重放，未注入 MySQL 提交层故障。生产采用、性能、长时间运行、发布、合并和部署仍需各自授权及验证。

## r6 及更早独立验证历史

下列标记之间为 r7 追加前的原文件 42053 字节，SHA-256 `e70ee2bf4b110eee84e5385d898fa1dea155debbc6ce44783ce03d972f9baab5`，原文逐字节保留。

<!-- ARCH-OBS-001-r6-checklist-history-begin -->
Task ID: ARCH-OBS-001
Revision: r6
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: ARCH-OBS-001 r6 §7.4 D-06 文档交 Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r6 §7.4 D-06

# D-06 Verification

2026-11-11（Asia/Shanghai）。fresh-context Verification 独立读取根工程契约、双语 README 和 PLAN、最近作用域索引、完整任务 bundle、双语指南、编辑前差异及 DEV 自检。按 [r6 §7.4 D-06 文档范围](spec.md#r6-d-06-第三方与-sma-接入说明)和 [D-06 Development 交接](tasks.md#d-06-developer-handoff)核验当前工作树候选。交付路径为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，分支 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。静态核验环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1 和系统 Python 3.9.6。

| 候选 | 核验 SHA-256 |
| --- | --- |
| [r6 规格](spec.md) | `ea288e72715f4e29f6ec0f30431954935f23e3b1990538fc5624aa6eae32f25a` |
| [Development 记录](tasks.md) | `8e64a7398d552dde18baf242e15274648b0e9b4eaa0a3bf26737387f1740dca3` |
| [英文审阅稿](../../docs/equipment-status-process-monitoring.md) | `ac7970c856038a9cc289a167da714ca287d92c93ebeb5c5a0d951553185ac799` |
| [中文审阅稿](../../docs/equipment-status-process-monitoring.zh-CN.md) | `0b005b6b1077187438518830c4d4fea44eb5a8df3d8ace0c4dda6fcd807ec194` |

## D-06 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D06-AC01 字段规则 | 通过 | SMA 每次发送完整信封，包括可预先配置的固定字段和真实 `plc_fact` 来源。第三方每次提供 `external_event`、稳定的 `sourceEventId`、采样时已确认的 `taskNo`、带偏移的原 `sampledAt` 及至少一项准入指标。接入绑定补齐 `producerId`、`sourceId`、成对的 `mappingId` 和 `mappingRevision`，协议缺省为 `aiis.metric-ingest/v1`。仅单设备单组固定身份可省略设备与组，多设备或多组必须提供两项。第三方实时的 `quality` 省略或显式 `null` 均记为 `unknown`，历史必须据实明确提供 `good`。缺测指标省略键，指标值 `null` 导致整包拒绝，`0` 和 `false` 保留。两稿说明系统管理字段的边界并链接规格。 [字段规则](spec.md#third-party-ingest-fields) |
| D06-AC02 权限与发现 | 通过 | GET 必传 `equipmentId`、`groupKey` 与 `target`，需要已认证、启用并获准写入该设备、组和目标的集成身份。未认证为 `401`，已认证但停用或越权为 `403`，均不返回定义。获准但没有可写指标时，`definitions` 为空。指标准入、目标启用槽位与组归属取交集，历史再取设备和组的白名单。返回指标键、类型和可选单位，已存值及内部槽位不返回。业务读和管理员入口分别校验，POST 重新校验准入。 [发现 GET](spec.md#指标发现示例) |
| D06-AC03 最简请求与回执 | 通过 | 两个示例使用获准双目标且绑定固定设备、组和来源的同一身份，共用 `vendor-sample-42`、原任务 `000042`、原时间 `2026-11-11T09:30:00.123+08:00` 和数字指标 `furnaceZone1Actual`。历史比实时多显式 `quality: "good"`。两条 POST 路径与九段原 JSON 保留，完整 SMA 请求仍各有投递号和任务号点位证据。第三方来源事件号跨目标及重试稳定，投递 `eventId` 按目标区分，调用方可显式复用或始终省略。既有回执按其映射信息核对规范化内容，映射版本更新后仍可返回原结果，内容变化则冲突。两稿均链接字段规则和两个样例。 [最简实时请求](spec.md#third-party-latest-example) · [最简历史请求](spec.md#third-party-history-example) |
| D06-AC04 文档边界 | 通过 | r6 软件设计仍为 `draft`。核验前，与 D-05 对照的本任务差异为 PM 规格、双语指南及 Development 交接。D-01 至 D-05 的规格授权与验收正文和 Development 历史保留，原 QA 历史已归档于下方。六份索引的 ARCH-OBS-001 行在 QA 写入前仍对应 D-05，交协调者按本结论同步对应行。双语根 PLAN 和任务目录另有 ARCH-ACQ-003 的并行验收更新。 |

## D-06 命令与结果

| 命令或方法 | 实测结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`git diff --cached --quiet`、`shasum -a 256` | 退出 0。工作树、暂存区状态及四项候选摘要符合交接。五份任务相关文档为工作树未跟踪文件，内容用编辑前副本核对。 |
| `diff -u` 逐文件对读，内联 `python3` 用 `hashlib.sha256` 和字节比对核对 11 个编辑前路径 | 正文比较退出 1，符合预期差异。首次将并行索引更新一并断言为字节相同，退出 1。复核后按 ARCH-OBS-001 行及 ARCH-ACQ-003 差异分开比较，退出 0。四份 D-05 对照摘要匹配原核验记录，D-01 至 D-05 授权和验收正文、D-05 至更早的 DEV 正文、QA 写入前的历史 checklist 均保留。 |
| 内联 `python3` 用 `json.loads` 检查围栏并比对字段、标量类型和时间偏移 | 退出 0。11 段 JSON 均可解析，无重复键或非 JSON 数值。九段原 JSON 逐字节一致。两个新请求满足固定接入的最少键集合，历史指标在 GET 示例的可写集合内。 |
| 内联 `python3` 核对相对路径、显式 ID、Unicode 标题锚点、双语规格链接及 Mermaid 源码 | 首次链接检查的 `Counter` 比较在 Python 3.9 退出 1，改用多重集差后退出 0。两稿各 39 个本地链接，规格 12 个、DEV 10 个、历史 QA 58 个、六份索引相关行 14 个，写入前共 172 个本地链接解析成功。两稿的规格链接集合一致，旧链接和显式锚点保留，两段 Mermaid 源码逐字节一致。 |
| `git diff --no-index --check -- <编辑前文件> <候选文件>`、`git diff --check -- <六份索引>` | 四项候选空白检查均退出 1，符合预期内容差异，且无空白错误输出。索引空白检查退出 0。 |

## D-06 结论与交接

**ARCH-OBS-001 r6 §7.4 D-06 文档为 `qa_passed`。** D06-AC01 至 D06-AC04 全部通过。无阻塞和返工项。交 Human Owner 对上述精确候选作 D-06 文档最终验收，当前待验收。

本轮核验限于工作树中的 Markdown、样例、相对链接及图表源码。Mermaid 渲染和外链可用性未验证。凭据选型、正式 OpenAPI、代码、数据库、HTTP 运行行为及现场启用属于后续范围。两份通用任务讨论稿是既有本地链接依赖。编辑前副本由协调者管理，关键结论与候选摘要已记录，QA 无需另保留临时产物。

## 历史 Verification 记录（r6 D-05 及更早修订）

> Task ID: ARCH-OBS-001
> Revision: r6
> Status: qa_passed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: ARCH-OBS-001 r6 §7.4 D-05 文档交 Human Owner 最终验收
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r6 §7.4 D-05

# D-05 Verification

2026-11-09（Asia/Shanghai）。fresh-context Verification 独立对读根工程契约及作用域索引、完整任务 bundle、双语审阅稿、编辑前差异及 DEV 自检，依据 [r6 §7.4 D-05 文档授权](spec.md#r6-d-05-完整方案审阅稿)和 [D-05 Development 交接](tasks.md#d-05-developer-handoff)核验。候选位于 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 `main` 工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。静态检查环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1 和 Python 3.9.6。

| 候选 | 核验 SHA-256 |
| --- | --- |
| [r6 规格](spec.md) | `b7ffda29b0ecb1631998ecff7611e54a76e5f88dcfcd0b2e368d23e7a7206512` |
| [Development 记录](tasks.md) | `cbbc9dd5a6f1c5d0508e63bbc3759a6e0a510831e97e51dfb590ae37ee918dfe` |
| [英文审阅稿](../../docs/equipment-status-process-monitoring.md) | `c1af519d2eb5846fa9d70fea89002f116d77478a8e8393124729a40a228af2c7` |
| [中文审阅稿](../../docs/equipment-status-process-monitoring.zh-CN.md) | `4154d8df6cc66b6fc87a1017bd114c504199253b3bb83e1f49b9b5dd9c3686a7` |

## D-05 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D05-AC01 原理与表 | 通过 | 两张值表定义固定列、候选 MySQL 类型、主键、唯一键与索引。实时唯一键为 `(equipment_id, task_no, group_key)`，较新样本替换采集字段时保留行 `id` 和备注。历史独立追加，以原任务、设备、组、采集时间和样本身份去重，任务索引为 `(task_no, sampled_at, id)`。两稿都说明共用指标登记、每目标每组各 100 个逻辑槽位、各表的 `local_values JSON`、首次成功存值锁定、停用仍占位及恢复原关联。回执按目标、生产者和事件区分。 [表定义](spec.md#33-本地槽位与物理表) |
| D05-AC02 接口与样例 | 通过 | 发现 GET 返回当前获准的键、类型及可选单位，历史受白名单限制。两条 POST 共用 `aiis.metric-ingest/v1`，路径区分目标。温控示例共用任务 `000042`、原帧 `sample-42`、任务号点位证据及 `2026-11-07T09:30:00.123+08:00`，各用独立事件号。历史发现的两个数字与历史请求一致。实时另含布尔就绪。按绑定核对实际 JSON 槽位，实时 `01/02/03`、历史 `07/08`、生产组卷号和状态 `01/02`。回执样例的 `recordId` 为字符串，两路各自持久确认与重试。两稿区分 SMA、业务读用户和管理员入口。 [发现、写入与回执](spec.md#5-sma-指标发现和写入接口) · [查询及配置](spec.md#4-前端查询和管理接口) |
| D05-AC03 任务与卷号 | 通过 | `task_no` 是固定业务字段，`id` 标识单行。`values.coilNo` 是可选字符串指标，前导零 `"000042"` 经样例落库映射保留。返工用新任务号，迟到样本仍归采样时任务，历史按任务查询和稳定分页。四页卡片、三页曲线、单位规则和独立永久历史留存保留。后端对两个管理列表核验登录、admin 及设备访问范围，实时仅备注，历史仅备注及与采集质量分开的管理标记。 [任务与换单](spec.md#32-任务归属和换单) · [管理权限](spec.md#43-实时快照与过程历史管理) |
| D05-AC04 新建与交付范围 | 通过 | 首版从空库及获准写入开始，依次定稿合同和合成样本、建设后端、并行开发前端与 SMA、隔离验证，首次现场启用另批。两稿互链并链接 r6 规格。D-01 至 D-04 原授权和验收段逐字节匹配 r5，历史角色记录可恢复。相对编辑前的 D-05 变更限于规格、两稿及角色记录，六份索引在 QA 写入前保持原摘要，交协调者同步对应行。 [首次启用与顺序](spec.md#71-首次启用与数据起点) |

## 命令与结果

| 命令或方法 | 实测结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256`、`git diff --cached --quiet` | 退出 0。分支、HEAD、四项候选摘要匹配，暂存区无差异。 |
| 内联 `python3` 使用 `json.loads` 解析 JSON 并按键、类型和目标投影槽位 | 退出 0。九段 JSON 围栏及五份内联槽位对象通过。r5 的登记、卡片、卡片项响应和曲线示例保持原字节，两条温控上报只替换示例任务号。 |
| 内联 `python3` 核对相对路径、显式 ID、Unicode 标题锚点和 Mermaid 连线 | 退出 0。双语稿各 33 个本地链接，其中各 30 个带锚点。每稿六个旧入口加两个新入口，六条 Mermaid 连线与 r5 一致。QA 写入前，双语稿、三份角色文档和六份索引的相关行共 147 个本地链接均解析成功。 |
| `diff -u`、`git diff --no-index --check`（编辑前后四项候选）及 `git diff --check`（六份索引） | `diff -u` 退出 1，符合预期内容变化。四项候选空白检查均退出 1，输出为空。索引空白检查退出 0。 |
| `git diff --binary HEAD -- .` 排除 11 个文档路径、`git ls-files --others --exclude-standard -z` 及内联 `python3` 对照基线 | 原聚合比较退出 1。交接后，另一个任务更新 DAA 的双语 Stage C 手册及 DAA-008 的 `tasks.md`。当前范围外跟踪差异 SHA-256 为 `8cdf5c020d2956aa88583c47ac069e67d6e2b4ec21a28bdec14efeaacb3a43d9`。用已有手册原文和 DAA-008 记录的 129,501 字节原前缀，经管道运行 `git diff --no-index --binary` 重建这三份文档的原差异。重建比较退出 0，聚合 SHA-256 与基线 `f1e02a2d24c691777bb0238ba77b59e5ece7ed65ba20140f6b213332967b0ecb` 一致。范围外未跟踪仍为同六条路径，其中四份原字节一致，两份通用任务讨论稿有同期更新，当前所需锚点均可解析。基线清单 SHA-256 为 `e5b9abffbf1d65be1606c124f58b5677713ed1c774d446f0db38f2a1aa7e63ed`。 |
| 内联 `python3` 对照历史字节并去除旧元数据的引用前缀 | 退出 0。规格 D-01 至 D-04 授权及验收段 SHA-256 为 `74b96043dbec1f1f82c1321fc40971232af338d88cf084ebbf2bebf7b5561479`。恢复的 r5 Development 摘要为 `b06257104f812b7ce497ed59fc0cc4beb97470e37105d52854d1ce2965f203b7`。下方 r5 QA 历史可恢复至原摘要 `2693750db155673c791806bbe71dcb143a57e2142f8766485a74af1da46f8010`，原 r4 与 r3 摘要也匹配。 |

## D-05 结论与交接

**ARCH-OBS-001 r6 §7.4 D-05 文档为 `qa_passed`。** D05-AC01 至 D05-AC04 全部通过，无阻塞或返工项。交 Human Owner 对上述候选作 D-05 文档最终验收，当前待验收。D-01 至 D-04 的结论归原候选和角色记录。

本轮证据限于 Markdown、JSON、Mermaid 源码和工作树。`command -v mmdc` 退出 1，Mermaid 图形未渲染。本轮依据 §7.4 的局部文档授权，旧整包检查器的整体软件批准条件不适用于本轮。软件方案仍为 `draft`，DDL、OpenAPI 发布、实施、运行及现场采用按各自范围审批。两份通用任务讨论稿为本地链接依赖。关键证据已写入本节，编辑前对照由协调者管理，QA 无需保留临时产物。

## 历史 Verification 记录（r5 D-04 及更早修订）

> Task ID: ARCH-OBS-001
> Revision: r5
> Status: qa_passed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: ARCH-OBS-001 r5 §7.4 D-04 文档交 Human Owner 最终验收
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r5 §7.4 D-04

# D-04 Verification

2026-11-09（Asia/Shanghai）。fresh-context Verification 独立读取根工程契约、双语 README 与 PLAN、最近作用域索引、完整任务 bundle、双语指南、编辑前差异及 DEV 自检。按 [r5 §7.4 D-04 文档授权](spec.md#r5-d-04-从零开始的总体方案讨论稿)和 [D-04 Development 交接](tasks.md#d-04-developer-handoff)核验。

## D-04 候选与环境

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1、Python 3.9.6。以下 SHA-256 与精确交接一致。

| 工作树文件 | SHA-256 |
| --- | --- |
| [规格](spec.md) | `cc1a481afc4b250e04e4daa33fcb6a29ae56531093fb9bb2d79e5a2fad295bf6` |
| [Development 记录](tasks.md) | `b06257104f812b7ce497ed59fc0cc4beb97470e37105d52854d1ce2965f203b7` |
| [英文讨论稿](../../docs/equipment-status-process-monitoring.md) | `6b5ad2a36f60cc2ed7b7816c74aa0378d2be4daf4374a127a039014aa2ffe88d` |
| [中文讨论稿](../../docs/equipment-status-process-monitoring.zh-CN.md) | `2e6723a2e1ccf9e461654dfdbce053f038aa1e7310c6e590cd3e642d0d5a8e8e` |

## D-04 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D04-AC01 首次启用 | 通过 | 先装配配置、从空库开始，首次获准后开启写入准入。首份验证通过且归属已确认任务的样本建立该组快照，首份同时符合历史白名单及选样条件的样本追加历史。无合格样本时实时呈空态或缺测，历史为空。换到 B 单后，符合条件的迟到 A 单样本仍按原任务与原采集时间处理。现行范围已移除旧数据兼容、迁移、切换和采集时间下界。 [首次启用](spec.md#71-首次启用与数据起点) · [任务归属](spec.md#32-任务归属和换单) |
| D04-AC02 项目预设 | 通过 | 三份正文均有生产参数、清洗、温控、传动四页卡片与温度、传动、清洗三页曲线组预设。双语标题和绑定对应，生产参数单指标卡片与固定卷号及卷状态分开。炉区 1 登记并贯通实际温度 810.2 °C、设定温度 815.0 °C、可选布尔就绪与共用单位的历史曲线，就绪值只进入实时。 [四页卡片](spec.md#2-设备状态四页) · [炉区指标与响应](spec.md#41-卡片配置和响应) · [三页曲线](spec.md#42-过程监控曲线组) |
| D04-AC03 共用规则 | 通过 | `metricKey` 稳定，写入保留 JSON 标量类型。可选共用单位用于标题或共用纵轴，值区只显示值。历史按独立白名单及间隔选样并永久保存。PLC 现场任务号证据随原采样保留，SMA 一次映射，分实时覆盖与历史追加两路并独立确认及重试。后端校验两个管理列表的权限，实时只改备注且覆盖保留备注，历史只改备注及管理标记。接口与 JSON 保持在规格内。 [SMA 合同](spec.md#5-sma-指标发现和写入接口) · [管理编辑边界](spec.md#43-实时快照与过程历史管理) |
| D04-AC04 顺序与范围 | 通过 | 双语指南互链并链接 r5 规格。顺序为合同和合成样本、后端、前端与 SMA 并行、空库受控验证，首次现场验证及启用另按真实产线批准。四项候选及 QA 记录是核验范围内的差异，六个索引在核验时仍对应编辑前对照，交协调者按结论同步对应行。历史授权和原角色证据已核对。 [实施与验证顺序](spec.md#72-首版实施与验证顺序) |

## D-04 命令与结果

| 命令或方法 | 实测结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256`、`git diff --cached --quiet` | 退出 0。分支、HEAD、四项候选摘要匹配，暂存区无差异。 |
| `diff -u` 对读规格和双语指南，内联 `python3` 字节比较、`git diff --binary HEAD -- . <排除 11 个文档路径>` 及 `git ls-files --others --exclude-standard -z` | `diff -u` 退出 1，预期正文有差异。Python 退出 0。QA 写入前，11 个对照路径只变动候选表中的四项。范围外跟踪差异的 SHA-256 为 `f1e02a2d24c691777bb0238ba77b59e5ece7ed65ba20140f6b213332967b0ecb`。范围外六个未跟踪文件的路径及内容摘要均与基线匹配，包括 DAA 的两份批准对照、两份 profile 源码和两份通用任务讨论稿。基线清单 SHA-256 为 `bc4b66f0dce2c0a1dabbebb3705e25f67ee8a82c8d3acb0629abc063ab274cdc`。 |
| 内联 `python3` 按相对路径、显式 ID 和 Markdown 标题解析链接 | 退出 0。每稿 25 个本地链接、22 个带锚点链接，均可解析。各保留六个阅读锚点，核对五个新增及三个替换目标。规格、Development、历史 checklist 及六个索引对应行的本地链接均可解析。初次检查仅以指南文件名匹配索引行，补充任务目录匹配后重跑通过。 |
| 内联 `python3` 使用 `json.loads` 严格解析并比对六段围栏，核对 Mermaid 源码和预设表 | 退出 0。登记和两路上报示例与 r4 逐字节相同，卡片、响应与曲线示例仅标题变化。两路共享 `JOB-20261107-001`、`sample-42`、采样任务点位、映射和带 `+08:00` 的原采集时间，`eventId` 各自独立。两路温度为 JSON 数字，布尔就绪仅实时，响应分开保留 `label` 和 `unit`。两稿各四页卡片、三页曲线及六条连线，Mermaid 源码保留原字节。 |
| `git diff --no-index --check -- <编辑前副本> <当前文件>`、`git diff --check -- <六份索引>` | 四项候选的前后比较各退出 1，输出为空。六份索引检查退出 0。 |
| 内联 `python3` 对照规格历史段并去除旧角色元数据的引用前缀后比较 SHA-256 | 退出 0。D-01 至 D-03 的规格授权及验收段原字节保留，SHA-256 为 `8917f42bd212d4c604ae503072e3c4ca0cd682d02916ea1db6469905136fd527`。恢复的 r4 `tasks.md` 与原摘要 `d9f2290baeaad1c57cd653739ec6d2afd66515daa602c9aeb340a0a01176560d` 一致，下方 r4 历史核验记录可恢复至原摘要 `bdeb52c71f4341f00f57fed736df6b19df401d2719590ca9cdaf33ab4ec869fb`。r3 历史核验的原摘要 `42464b8c1774bf6e3211619f84286d26add9c28f93bb9bfdba08c6b1ae82750e` 也匹配。 |

## D-04 结论与交接

**ARCH-OBS-001 r5 §7.4 D-04 文档为 `qa_passed`，D04-AC01 至 D04-AC04 全部通过。** 无阻塞或返工项。交 Human Owner 对四项精确候选作 D-04 文档最终验收，当前待验收。D-01 的 Owner 验收与 D-02、D-03 的文档 QA 保留在各自历史记录。

本轮采用 §7.4 局部文档验收。旧整包检查器按整体软件批准流程检查。r5 软件方案为 `draft`，构建、运行、数据库和现场操作属于后续范围。Mermaid 核验限于源码，`command -v mmdc` 退出 1。两份既有通用任务讨论稿须随工作树供本地链接解析。关键证据已记在本节，编辑前临时对照由协调者管理，QA 无需保留临时产物。

## 历史 Verification 记录（r4 D-03 与 r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r4
> Status: qa_passed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: ARCH-OBS-001 r4 §7.4 D-03 文档交 Human Owner 最终验收
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r4 §7.4 D-03

# D-03 Verification

2026-11-09（Asia/Shanghai）。fresh-context Verification 独立读取根工程契约、双语 README 和 PLAN、最近作用域的索引、完整任务 bundle、双语指南、编辑前差异及 DEV 自检。核验范围以 [r4 §7.4 D-03 文档授权](spec.md#r4-d-03-任务归属和管理列表讨论稿)及 [D-03 Development 交接](tasks.md#d-03-developer-handoff)为准。r4 软件方案处于 `draft`。

## D-03 候选与环境

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。macOS 15.7.7（arm64）、Apple Git 2.50.1、系统 Python 3.9.6 用于本地文档静态检查。四项 SHA-256 均与交接一致，候选取自工作树。

| 文件 | SHA-256 |
| --- | --- |
| [spec.md](spec.md) | `5e8e9d7ffe670187afb142f5665525810313b69484384324a82df23832c0a8e3` |
| [tasks.md](tasks.md) | `d9f2290baeaad1c57cd653739ec6d2afd66515daa602c9aeb340a0a01176560d` |
| [英文指南](../../docs/equipment-status-process-monitoring.md) | `5f9d498808d9589ef1a6d4785f78da8636cf28baae9276ee02a0a14490733e2a` |
| [中文指南](../../docs/equipment-status-process-monitoring.zh-CN.md) | `fcd73dd295dc555170d0d855895478b8db40ec1a837c78f629c9b616ce4d0a47` |

## D-03 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D03-AC01 任务归属 | 通过 | 规范化时去首尾空格并将英文字母大写，项目内任务号唯一，库内用 `task_no`，API 用 `taskNo`。PLC 在开工或换单时更新 `activeTaskNo`，DAA 在采样时留存可核验证据。按设备、任务和组定位快照，卡片只读现场确认的当前任务。现场从 A 切到 B 后，晚到的 A 单仅影响 A 单快照，符合规则的历史仍按 A 单和原采集时间追加并可按原任务查询。B 单缺组显示缺测，现场空闲和任务归属不明各有空态。 [任务归属与换单](spec.md#32-任务归属和换单) · [中文数据流](../../docs/equipment-status-process-monitoring.zh-CN.md#data-flow) · [英文数据流](../../docs/equipment-status-process-monitoring.md#data-flow) |
| D03-AC02 SMA 两路 | 通过 | 一次映射的同源样本按独立周期和指标集合组成实时覆盖与历史追加，历史按组白名单独立选样。各目标使用独立的稳定事件身份和持久回执，分别确认及按原身份重试。六段 JSON 可解析，其中两路写入共享 `sample-42`、采样任务点位证据、映射版本、`JOB-20261107-001` 和带 `+08:00` 的原采集时间，分别使用 `temperature-42-latest` 与 `temperature-42-history`。两路温度均为 JSON 数字，布尔就绪值仅出现在实时。 [采样策略](spec.md#31-首版采样组与历史指标) · [写入示例和回执](spec.md#5-sma-指标发现和写入接口) |
| D03-AC03 管理列表 | 通过 | 实时快照列表归设备状态，过程历史列表归过程监控，入口仅向 admin 显示。两表按任务号、设备或产线及组筛选，历史另按采集时段筛选，后端分页。固定列为任务号、设备、组、采集时间及数据状态，详情按配置显示指标名称、单位和采集值。后端对列表、详情和编辑校验登录、admin 和设备访问范围，并拒绝编辑白名单外字段。实时仅可改备注，SMA 更新同一快照的采集字段时保留备注。历史可编辑备注及异常、已复核标记，管理标记与采集质量独立，原始值更正另立后续范围。 [管理接口](spec.md#43-实时快照与过程历史管理) · [中文管理列表](../../docs/equipment-status-process-monitoring.zh-CN.md#admin-lists) · [英文管理列表](../../docs/equipment-status-process-monitoring.md#admin-lists) |
| D03-AC04 文档与历史证据 | 通过 | 两稿逐节对读一致，保留原链接和阅读锚点，新增 D-03 范围、任务归属、管理接口及管理列表入口。接口与 JSON 仍由规格维护。可选共用单位、标题和数值分工、曲线纵轴、上海时区、切换时间下界及永久历史留存的口径可核对。候选差异仅在规格、Development 记录及双语指南。D-01、D-02 的授权段逐字节保留，两份 r3 角色记录的旧元数据去掉引用前缀后均可与原文件逐字节比对。 |

## D-03 命令与结果

| 命令或方法 | 结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256 <四项候选>`、`git diff --cached --quiet` | 均退出 0，工作树身份及摘要匹配，暂存区无变更。 |
| `diff -u <编辑前副本> <工作树文件>`、内联 `python3` 字节比较 | 规格和两稿差异均在 D-03 方案内。编辑前 11 路径中，QA 写入前仅上表四项内容变化，六份索引字节一致。r3 的两个授权段一致。去除历史元数据的引用前缀后，旧 `tasks.md` SHA-256 为 `23ce97cc466c0be4ccf0ad2d66f310b3ee194ff13c8285f3c97a58bd649f714e`，旧 `checklist.md` 为 `42464b8c1774bf6e3211619f84286d26add9c28f93bb9bfdba08c6b1ae82750e`，均与编辑前副本一致。 |
| `git diff --binary HEAD -- . <11 项文档路径排除>`、`git ls-files --others --exclude-standard -z`、内联 `python3` SHA-256 核对 | 退出 0。文档范围外的跟踪文件差异 SHA-256 为 `f1e02a2d24c691777bb0238ba77b59e5ece7ed65ba20140f6b213332967b0ecb`，范围外六个未跟踪文件的路径及摘要均与编辑前基线一致。 |
| 内联 `python3` 解析相对路径、显式锚点及 Unicode 标题、校对 Mermaid 源码和 `json.loads` | 退出 0。每稿 23 个本地链接（20 个带锚点）、6 个阅读锚点、6 条 Mermaid 连线。三份角色文档与六份索引相关行的本地链接可解析。六段 JSON 均通过解析，前四段和 r3 逐字节一致，写入示例的内容差异限于共享映射 ID、任务号和采样任务点位证据。首次链接检查使用了 Python 3.9 不支持的 `Counter` 比较，改用多重集差后重跑通过。 |
| `git diff --no-index --check -- <编辑前副本> <当前文件>`、`git diff --check -- <六份索引>` | 规格、两稿和两份角色记录相对编辑前各退出 1，表示有内容差异，输出为空。索引空白检查退出 0。 |

## D-03 结论与交接

**ARCH-OBS-001 r4 §7.4 D-03 文档为 `qa_passed`，D03-AC01 至 D03-AC04 全部通过。** 无阻塞或返工项。交 Human Owner 对本节四项精确候选作 D-03 文档最终验收。D-01 的 Owner 验收及 D-02 的文档 QA 见下方历史记录，D-02 仍待 Owner 验收。

验证限于本地静态文档、样例和工作树。两份既有通用任务讨论稿是本地链接依赖。Mermaid 复核限于源码（`command -v mmdc` 退出 1）。软件构建、运行、数据库及现场验证属于后续独立审批。旧整包检查器要求规格整体为 `owner_approved`，本轮采用 §7.4 的局部文档验收口径。关键证据已记在本节，编辑前对照由协调者管理，QA 无需保留临时产物。

## 历史 Verification 记录（r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r3
> Status: owner_accepted
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: Human Owner 已最终验收 r3 §7.4 D-01 文档
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r3 §7.4 D-01

# D-01 设备状态与过程监控讨论稿独立验收

2026-11-07（Asia/Shanghai）。本轮由 fresh-context Verification 独立读取根工程契约、双语 README 和 PLAN、最近作用域的文档索引、[r3 规格](spec.md)、[Development 交接](tasks.md)、两份指南及工作树差异。依据 [r3 §7.4](spec.md#74-长期阅读指南) 记录的 Human Owner 授权验证 D01-AC01 至 D01-AC04。r3 软件方案处于 `draft`，软件验收项 AC01 至 AC07 归后续独立审批的范围。

## 候选与环境

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。本地 macOS 15.7.7（arm64）、Apple Git 2.50.1、Python 3.9.6。以下 SHA-256 均与交接值相符。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `c5b49be944d3ae40abd72ac77967b529afa6a449e0cf608a415872e486310391` |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md` | `b694674ef4a3a28df1c3b0ce491dc5631b5efe007dbcfe6321cdf46e777d1d2f` |
| `docs/equipment-status-process-monitoring.md` | `738441be2a54cef103e714e03c6ae9ebb89e7b4debf31f393332aedba8c361b6` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `345fa0b94197ef14cb0bbc916ca3d0916f775ecb98ea008c9601162dc3d05041` |
| `docs/README.md` | `a74d088ca1802bc1906a929004cb73bc8c3a6adb19a66d4579f5b957ee17a673` |
| `docs/README.zh-CN.md` | `9bc039d9b9dc5c2261f6682485ff2facb623afee43c3d8b931ef09abf6d5c87a` |
| `docs/generic-task-workflow-discussion.md`（既有链接目标） | `b0913d0fe16627b9d7bbe1043b8b602ccee312b08915a70a68ed628fc7032fff` |
| `docs/generic-task-workflow-discussion.zh-CN.md`（既有链接目标） | `2e55a70064945d4836f4204bb7f9a7dba2151d3c76b78156aa88ca7416f39439` |

## 验收检查

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| D01-AC01 文档与链接 | 通过 | 两稿互链，并各自链接文档目录、r3 规格及 §7.4。双语索引新增行均可到达两份指南。两稿开头一致标明 D-01 讨论稿范围、软件草案状态和后续审批。42 个相对链接目标解析成功，其中 32 个有锚点。[中文稿](../../docs/equipment-status-process-monitoring.zh-CN.md) · [英文稿](../../docs/equipment-status-process-monitoring.md) · [中文索引](../../docs/README.zh-CN.md#索引) · [英文索引](../../docs/README.md#index) |
| D01-AC02 管理员配置 | 通过 | 两稿均先登记炉区 1 的 `furnaceZone1Actual` 和 `furnaceZone1Set`，再配置四页共用的卡片和温度历史曲线组。卡片支持设置双语标题、启用、排序、唯一的有序指标及逐项开关，每卡最多 10 个启用指标。曲线组对同一对 °C 指标配置有序、可独立启用的两条序列，按原采集时间查询已存样本，缺样时留空。[中文卡片](../../docs/equipment-status-process-monitoring.zh-CN.md#latest-cards) · [中文曲线](../../docs/equipment-status-process-monitoring.zh-CN.md#history-curves) · [英文卡片](../../docs/equipment-status-process-monitoring.md#latest-cards) · [英文曲线](../../docs/equipment-status-process-monitoring.md#history-curves) |
| D01-AC03 上报与留存 | 通过 | 两稿用稳定指标键表示同一次来源采样中的独立标量。实时按设备和采样组整份替换并防旧包覆盖，历史按产线和组独立选样、追加并永久保留。历史白名单和采样间隔归采样策略，曲线启用、隐藏及编辑只影响展示。两路各有投递身份与持久回执，历史重试由回执去重。[中文数据流](../../docs/equipment-status-process-monitoring.zh-CN.md#data-flow) · [英文数据流](../../docs/equipment-status-process-monitoring.md#data-flow) |
| D01-AC04 权威边界 | 通过 | 两稿将管理与查询路径、字段及 JSON 示例交给 r3 §4、§4.1、§4.2 和 §5，正文保留概念及两项指标键示例。逐字节复核确认 D-01 候选为两份新指南、两条索引新增行和 Development 记录。本 checklist 的结论限于 D-01。[配置接口与示例](spec.md#4-前端查询和管理接口) · [SMA 接口与示例](spec.md#5-sma-指标发现和写入接口) · [Development 交接](tasks.md#developer-handoff) |

## 命令与结果

| 命令或方法 | 结果 |
| --- | --- |
| `git symbolic-ref --short HEAD`、`git rev-parse HEAD`、`shasum -a 256`（上表八项） | 均退出 0，分支、HEAD 和八项摘要与交接一致。 |
| 独立 `python3` 内联检查相对路径、Unicode 标题锚点和显式 `id` | 退出 0。每稿 19 个链接、5 个阅读入口，新增索引行各 2 个链接。两稿引用相同的 11 个规格目标，并各自解析对应语言通用任务讨论稿的 `field-config-alignment`。 |
| 独立 `python3` 解析 r3 的 JSON 围栏并比较 Mermaid 源码的边 | 退出 0。r3 的 6 个 JSON 示例均可解析，炉区指标键贯穿卡片、响应、曲线和两路上报。实时示例额外携带布尔就绪值，两路原采集时间一致、事件身份不同。两稿的 Mermaid 各有 6 条边，均将事实经 SMA 分流至快照和历史。 |
| `git diff -- docs/README.md docs/README.zh-CN.md` 和独立 `python3` 字节比较 | 均退出 0。每份索引删除 D-01 单行后，所得 SHA-256 与 Development 编辑前摘要一致。再移除对应既有通用讨论稿索引行后，与 `git show HEAD:<path>` 的字节完全一致。两个通用讨论稿文件的摘要与交接值一致。 |
| `git diff --cached --quiet`、`git diff --check -- docs/README.md docs/README.zh-CN.md` | 均退出 0。暂存区无变更，索引差异无空白错误。 |
| `git diff --no-index --check -- /dev/null "$guide"`（两稿各一次） | 均退出 1，表示与空文件存在差异，输出均为空。两稿各 73 行。 |
| `sed -n '42,89p' plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md \| bash` | 退出 0，交接所附 DEV 静态检查重跑得到 42 个解析成功的链接。独立检查结果见本表其他行。 |
| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh .`（写入本记录前） | 退出 1。对本 bundle，检查器要求整份 `spec.md` 为 `owner_approved`，并要求根双语任务目录列出已存在的 `tasks.md`、以固定词标记当时尚未创建的 `checklist.md`。§7.4 是局部批准，根任务目录记录的是 r3 软件草案。D-01 以 §7.4 的授权和验收项判定。 |

## 原独立 QA 结论与交接

**D-01 `qa_passed`，D01-AC01 至 D01-AC04 全部通过。** 当前无 D-01 阻塞或返工项，交 Human Owner 对该文档切片作最终验收，当前为待验收。

链接结论以当前交付工作树为准，两份通用任务讨论稿仍是既有未跟踪链接依赖。交接记录的临时快照目录经检查已不存在，复核依据为工作树文件、摘要及本记录。

`command -v mmdc` 退出 1，Mermaid 复核限于源码，图形渲染未实测。软件构建、运行测试、数据库与现场验证归各自后续审批范围。

## Human Owner 最终验收

2026-11-07（Asia/Shanghai），Human Owner 在会话中确认。

> 这份讨论稿可以验收了。接下来按 r3 把首版实施拆一下吧，前端、后端和 SMA 分别要做什么，先做哪块、怎么验收？先定实施顺序，不改代码。

**ARCH-OBS-001 r3 §7.4 D-01 为 `owner_accepted`。** 验收对象是 `main` 工作树（HEAD `bcafa89fa31bdf62329bced89baebc193323a739`）中本记录「候选与环境」所列的双语讨论稿和对应的两条索引新增行。登记前用 `python3` 核对 `spec.md`、`tasks.md`、双语讨论稿及双语文档索引的六项 SHA-256，均与原 QA 记录一致，退出 0。原 `qa_passed` 记录的 SHA-256 为 `2e46fef791708a465a529322c64d5fbdf9194bfca2a205982d2f53c30a20a92f`，原 QA 结论与证据保留。

两份既有通用任务讨论稿在原 QA 后内容摘要已变化，`rg` 核对两份目标均保有 `field-config-alignment` 锚点。它们是 D-01 的外部文档链接依赖，表中摘要仍对应原 QA 时点。本次为终验登记及候选身份核对。

后续请求为只读梳理首版实施顺序。r3 软件方案仍处于 `draft`，实施和现场采用各按对应范围审批。

## D-02 Verification

2026-11-07（Asia/Shanghai）。独立 fresh-context Verification 按 [r3 §7.4 D-02 授权](spec.md#r3-d-02-单位规则补充)和 [D-02 Development 交接](tasks.md#d-02-developer-handoff)复核单位规则补充。文件顶部状态与前 8,597 字节的记录归 D-01 原候选，保留其 `owner_accepted`。r3 软件方案为 `draft`。

### D-02 候选

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1、Python 3.9.6。

| 文件 | SHA-256 |
| --- | --- |
| `spec.md` | `55c168a7120af682e98af4246fb0d8c192492d8d7830d7dddc14be379fe3d3a3` |
| `tasks.md` | `23ce97cc466c0be4ccf0ad2d66f310b3ee194ff13c8285f3c97a58bd649f714e` |
| `docs/equipment-status-process-monitoring.md` | `939db98596e85464552c8250d0322e659af923216becba83063d3a1e9c4400e3` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `9c032abe5be2f04acf6b05d2c9404eae425841938a01ac07379f3da7b639d22e` |

### D-02 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D02-AC01 | 通过 | 规格 §3、§4.1 和两稿 §1–2 一致。中英文名称独立保存，共用可留空的 `unit`。指标项标题组合为「实际温度（°C）」或「Actual temperature (°C)」，留空或省略单位时仅显示名称。值区只显示格式化值，两稿均以 `810.2` 为例。 |
| D02-AC02 | 通过 | 规格 §4.2 和两稿 §3 都按同一物理量和单位组织曲线组。同单位序列共用纵轴时标注一次单位，留空或省略单位时纵轴省去单位标注。 |
| D02-AC03 | 通过 | 规格 §5 和两稿 §4 一致。SMA 按 `metricKey` 上报原类型的 JSON 标量，实时快照和历史追加使用同一登记业务单位。两条拟定 POST 路径保持原样，响应示例分别保留 `label` 和 `unit`。六段 JSON 逐字节匹配编辑前摘要，两路温度均为 JSON 数字，实时就绪值为布尔值。 |
| D02-AC04 | 通过 | 两稿仍以规格 §4、§4.1、§4.2、§5 为接口和示例入口。两稿各 19 个链接，双语索引行各 2 个链接，共 42 个本地目标解析成功，含 32 个带锚点链接。逆向比对还原三个 D-01 正文摘要，双语索引仍匹配原候选摘要。D-02 正文差异限于单位说明及对应验收，角色记录为追加。 |

### D-02 命令与结果

- `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256` 均退出 0，分支、HEAD 和四项候选摘要匹配。`git diff --cached --quiet` 退出 0。
- `git apply --reverse --check <D-02 对照 diff>` 退出 0。独立 `python3` 在内存中按 hunk 逆向还原双语正文各 4 段及规格 6 段，三个摘要均匹配 D-01 候选表，退出 0。D-01 的规格授权区（去尾部空白）、Development 前 7,255 字节及原 checklist 前 8,597 字节的 SHA-256 分别为 `2f62127c7744fc4fa19490d16789f43a8d8663bda121e0c9e6a27325aadec78b`、`b694674ef4a3a28df1c3b0ce491dc5631b5efe007dbcfe6321cdf46e777d1d2f`、`6cec7377c6b8956c7896cf8e6958a75578be4107b7ee9245f982ec04167a9663`，匹配对应历史基线。
- 独立 `python3` 使用 `hashlib.sha256`、`json.loads` 核对六段围栏的原字节及标量类型，用 `pathlib` 核对本地路径、显式锚点和 Unicode 标题锚点，退出 0。两稿各自的 `field-config-alignment` 依赖在当前工作树可解析。
- `git diff --check -- PLAN.md PLAN.zh-CN.md docs/README.md docs/README.zh-CN.md plans/README.md plans/README.zh-CN.md` 退出 0。四份未跟踪候选分别运行 `git diff --no-index --check -- /dev/null <文件>`，均退出 1，输出为空，差异来自文件存在。
- `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh .` 退出 1。对本 bundle，检查器要求整份规格为 `owner_approved`，且目录链接须精确使用无锚点 `checklist.md`。实际局部批准和 D-01 验收由 §7.4 与 checklist 记录，双语目录的 D-01 锚点有效。本次以 D-02 局部批准和实测链接判定。

### D-02 结论与交接

**D-02 `qa_passed`。** D02-AC01 至 D02-AC04 全部通过，无阻塞或返工项。交 Human Owner 对本节所列候选的 D-02 文档补充作最终验收，当前待验收。

验证限于本地 Markdown、JSON 和工作树。`command -v mmdc` 退出 1，原 Mermaid 源码经差异核验，图形渲染留在文档检查范围之外。软件构建、运行、数据库与现场验证归各自后续审批。两份通用任务讨论稿及 DAA 同期工作属于独立变更。必要复核证据为工作树候选、本节摘要和保留的 D-01 记录，验证无须保留临时产物。
<!-- ARCH-OBS-001-r6-checklist-history-end -->
<!-- ARCH-OBS-001-r7-qa1-checklist-history-end -->
<!-- ARCH-OBS-001-r7-qa2-checklist-history-end -->
