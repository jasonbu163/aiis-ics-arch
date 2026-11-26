Task ID: ARCH-ENERGY-002
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 隔离候选、补丁与自检证据移交 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-ENERGY-002 r1 实施与开发自检

Human Owner 于 2026-11-25（Asia/Shanghai）明确批准「批准 ARCH-ENERGY-002 r1，按 STD 启动 Development。」获批 [r1 规格](spec.md) 的 SHA-256 为 `7c1daf6fee1a97760d9d9beb2834e4d405ba8bad533a6bfc4ebea1aaa81671f3`。Development 已读取项目契约、canonical workflow、任务 bundle、前后端最近模块文档及相关源码，使用 `backend-arch`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`。浏览器检查使用 Playwright 和已安装 Chrome。

## 实施

- 新增独立 `energy_curve_group_configs` 配置表及四个登录 Bearer 入口。管理操作沿用管理员检查及当前表计范围。统计读取沿用 `energy-consumption-read` 和可读表计，只列出启用组。PATCH 锁住曲线组行，以当前字段合并提交内容，并完整替换请求中的有序曲线数组。保存校验一个表计、一个采样组、已有数值指标、指标唯一和同图量纲／单位。指标的写入停用状态独立于历史展示。
- 配置管理保留表计管理、表计指标配置、写入登记及原默认入口，新增曲线设置。下卡提供表计／关键词筛选和本机列宽。曲线编辑采用紧凑三段式弹窗，支持中英文标题回退，配置原引用保留供排查。组键沿用现有标识规则并固定。点段和字面百分号的 PATCH 编码在合同中列出。
- 统计页保留手动默认模式、现有样本分页和后端汇总。选组按保存顺序展示启用曲线，第一条有效启用线决定汇总。缺项保留断点，数值 0 可见，同刻点使用共享组件的散点层。选组的图表使用可选缩放与精度显示，过程调用保留原默认行为。曲线组与手动查询各自处理读取失败，迟到请求按选择和生命周期失效。
- 新迁移 `af6d8b2c4e90` 是 `9e0c5d41b7a2` 的唯一后继。执行时以 `ENERGY_CURVE_EXPECTED_SCHEMA`、`ENERGY_CURVE_EXPECTED_SERVER_UUID` 显式核对目标，检查准确前驱及表计和指标依赖，再增加一张空的 InnoDB 表。迁移禁止直接删除新表的 downgrade，应用回退保留配置表。日常请求使用能耗现有数据库身份校验和实际表结构，未加入全库 revision 门槛。
- 同步 [双语能耗曲线合同](../../contracts/published/http-api/energy-curve-groups-v1/README.zh-CN.md)、OpenAPI、相关前后端 README 和 `CODE_INDEX.md`。

## Development 自检

| 验收点 | 本次证据 |
| --- | --- |
| AC01 配置与权限 | 实际 Chrome 使用隔离 MySQL 和 FastAPI 登录账号，完成新增、保存、重新打开、编辑、启停、表计／关键词筛选和重置。拖动使首列从 165px 增至 243px，切换工作区和重载均保留 243px，重置恢复 165px。确认既有三项入口及表计指标默认。运营账号管理读与越权读取返回 403，统计列表按角色和表计范围过滤。 |
| AC02 表单与布局 | 四个分组、实线／虚线、调整顺序、曲线及组开关保存再读一致。遮罩取消前后回查无提交。1440×900、1024×768 与中／英文、浅／深色 8 种组合实测，长表单独立滚动，标题和页脚始终可达。 |
| AC03 数据范围 | 已停用写入的 `standby` 保留历史曲线和读数。浏览器拒绝重复指标与混合物理量／单位，后端验证非法引用和相同缺省单位。变更合成指标单位后统计提示配置不可用，管理弹窗提示修复并保留原引用。验证 401、403、404、409、422、503 信封。 |
| AC04 选组与汇总 | 实际图表按保存顺序展示虚／实线。瞬时量显示 `7.00 kW` 及既有原因，区间量显示 `5.00 kWh`，累计量与真实后端一致显示「累计读数下降」，时段用量为空。切换图例未改变汇总指标。 |
| AC05 手动查询 | 空曲线列表与合成 503 情形仍可按表计查询、加载实际两页样本、重试与恢复默认。旧手动统计的范围校验、延迟定义、多页请求、切组、页面离开和零值用例继续通过。 |
| AC06 样本与并发 | 实际 ECharts 实例核对零、缺测断点、同刻点图层、小数位和滚轮缩放。延迟的累计汇总在切换区间量后送达，区间量仍保持显示。两会话独立。MySQL 同键并发新增得到 200／409，同组三个部分更新在锁内合并并保留完整序列。 |
| AC07 迁移与回归 | 一次性 MySQL 8.4.6 用实际 Alembic 入口拒绝错误 UUID。预置带标记的模拟中断表后拒绝继续，原标记和前驱版本保留；移除该合成标记表后成功升级。仅新增空配置表，旧表计、能耗与过程数据依赖未引入跨域外键。逐项核对能耗指标、样本、回执及实时／过程历史；新配置表为空仍可手工查询。合成无关后继后曲线读取、保存、公有 GET、登记与原 POST 合同继续通过，回退保护保留曲线配置。 |
| AC08 工程交付 | 隔离候选完成模块合同检查、Vite 构建、聚焦测试、实际注册 OpenAPI 校验与 10 条新增中英文 Markdown 链接核对。候选相对正式工作树的补丁待独立验证和获批采用后整合。 |

## 命令与结果

- 候选 `backend/`，载入任务目录 `fixture.env` 的合成参数后，运行 `uv run --no-sync pytest -q tests/test_energy_curve_groups.py tests/test_energy_meters.py tests/test_energy_registered_ingest.py tests/test_energy_public_reads.py tests/test_equipment_observation_r10_flow.py tests/test_openapi_router_tags.py -k 'not test_openapi_contains_only_public_core_operation_tags and not test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean'`。**40 通过、2 未选择**，包含发布 OpenAPI 与运行时路径及 schema 一致性、四方法 Energy 标签及 Bearer。既有 SQLite 时间适配弃用提示 1 项。正式基线复验第一个排除项，确认既有 `Quality - Defects` tag 断言失败；第二项依赖冻结 C2 和历史 Git 来源，隔离候选的默认环境无该 Git 元数据和历史 backend 入口。
- 候选 `backend/` 运行 `uv run --no-sync alembic heads`，唯一 head 为 `af6d8b2c4e90`。同一工具链载入专用库闸门后以 `PYTHONPATH=. uv run --no-sync pytest -q tests_mysql/test_energy_curve_groups_mysql.py tests_mysql/test_energy_meters_mysql.py tests_mysql/test_energy_registered_ingest_mysql.py tests_mysql/test_energy_public_reads_mysql.py` 执行，**4 通过**。专用容器使用本机镜像 `mysql:8.4.6`，绑定随机回环端口 `53798`，多套合成 schema 完成后由夹具清理。
- 候选 `frontend-js/` 使用 `pnpm_config_verify_deps_before_run=false npm_config_update_notifier=false`，两类合成角色页面权限均为 `["monitor.energy"]`，执行 `pnpm run build --outDir /private/tmp/aiis-energy002-r1.brHaWJ/dist-r1 --emptyOutDir`。模块检查通过，10 组、32 路由，Vite 构建成功，保留既有大 chunk 提示。用同一锁定依赖执行 `pnpm exec node --test tests/module-registry/{energy-curve-groups,energy-write-sources,equipment-observation,equipment-observation-columns}.test.mjs`，**36 通过**；`pnpm run test:modules` 得 **123 通过、2 失败**，失败名称与正式基线 **120 通过、2 失败** 相同，分别为 `admin, supervisor, operator and unknown share route/menu/default decisions` 和 `actual source preserves Core route identity, shell locales and default-disabled demo`。
- `node /private/tmp/aiis-energy002-r1.brHaWJ/browser-check.mjs` 退出 0。Chrome 加载候选生产构建，真实认证及业务接口由任务独占 Uvicorn `127.0.0.1:54573` 和专用 MySQL 提供。503 及迟到响应场景由 Playwright 控制单条请求。交接目录保留日志和 11 张合成页面截图。
- 在候选根运行 `python3 /private/tmp/aiis-energy002-r1.brHaWJ/curve-link-check.py`，10 条链接存在，发布 OpenAPI JSON 可解析。在正式工作树执行 `git apply --check --whitespace=error-all /private/tmp/aiis-energy002-r1.brHaWJ/ARCH-ENERGY-002-r1.patch` 通过。

## 精确交接与采用边界

正式工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。候选根目录为 `/private/tmp/aiis-energy002-r1.brHaWJ/candidate`，基于正式工作树 3,994 个文件的快照，保留原有工作树变更。交接包含 33 个实现及合同文件，其中新增 14 个，更新 19 个。全部路径及前后 SHA-256 在 TSV 中给出。正式仓库此次写入仅为本 `tasks.md`。

| 工件（均位于 `/private/tmp/aiis-energy002-r1.brHaWJ`） | SHA-256 |
| --- | --- |
| `ARCH-ENERGY-002-r1.patch` | `49dde2571d416bed576904855a52b85f7ca8dd855fe0653cdbcec2b5cb141c4e` |
| `ARCH-ENERGY-002-r1.sha256.tsv` | `c85d929afd8fdd01b57f4e2cc52ec6d0d952737df13a03ebb20adae252ea0273` |
| `ARCH-ENERGY-002-r1-dist.sha256` | `ffd81b3c692041e5e8cd26eb2d2574beaec60d63b3e0b3c135268ca1d0d49656` |
| `browser-check.log` | `287add084560029bbe9413a54bc88d93e7193ea9e3c1cd34e607e1cd5713b38d` |
| `backend-scoped.log` | `d9b2a560a6ff44aa17695fade851f031254492dddbbb2d0030e90b37eba711b8` |
| `mysql-scoped.log` | `f4f72638ebe6abcca235a9a085faa733d39ba651bfd4eab4788d8fb3e5ecb559` |

交 fresh-context Verification 核验该精确 r1 工作树及补丁。正式源码待整合，真实 dev 尚不能使用本变更。应用候选前，协调者需在采用获独立授权后核对目标身份与前驱、备份真实库、执行迁移，再整合与验证正式工作树和实际启动入口。当前真实库、已运行服务和外部设备均未执行变更。无 Git 提交或推送。

## 临时资源收尾

Chrome 会话已退出，测试 Uvicorn 已关闭，一次性 MySQL 容器 `aiis-energy002-r1-brHaWJ` 已停止并回收。任务根目录下候选、补丁、构建、合成夹具、日志及截图保留，以便独立 Verification 复验和后续精确采用。协调者在独立证据落盘并完成候选整合，或转存正式保留补丁后回收任务目录。

## 2026-11-25 本机 dev 采用与正式源码交接

Human Owner 于 2026-11-25（Asia/Shanghai）批准「批准备份本机 `3307` dev 库，从 `9e0c5d41b7a2` 迁移到 `af6d8b2c4e90`，并整合、验证 ARCH-ENERGY-002 r1。」同一获批 r1 的范围和验收沿用 [spec.md](spec.md)。协调者执行备份、迁移、整合及正式入口检查，本段由 Development 核对证据并补记。上文是整合前的候选交接，原始字节 SHA-256 为 `415aa0f756bd4a7946512eec0a0774624d4b604604126894130822f32005e9b5`。

### 备份、精确迁移与整合

- 本机回环 `127.0.0.1:3307/industrial_level_2_system` 为既有 MySQL 8.4.6 dev 库。协调者先核对库名、实例身份与唯一前驱，使用 `mysqldump --single-transaction` 备份，再核对备份摘要与前驱。备份位于 `/private/tmp/aiis-energy002-dev-backup.Uhk8JT/dev-before-af6d8b2c4e90.sql`，大小 358442 字节，目录权限 `0700`，文件权限 `0600`，SHA-256 为 `19b7779ffce4a29f576b3d28e25e732e5a51e21041518f3ee36ef8ab2887edca`。备份已核对完成标志、前驱标记和原有 69 张表的覆盖范围。本轮完成的是备份检查，恢复演练未执行。
- 协调者使用已独立核对的候选脚本执行准确的 Alembic `upgrade af6d8b2c4e90`，成功后才整合源码。数据库从 `9e0c5d41b7a2` 变为 `af6d8b2c4e90`，新增 `energy_curve_group_configs` 一张表，0 行、0 外键。原有 69 张表的 DDL 逐项相同。前后 8 个计数一致，`energy_meters`、`energy_metric_configs`、`energy_consumption_main`、`energy_write_sources`、`energy_ingest_receipts` 各 0 行，`equipment_main` 5 行，`monitor_main` 23 行，`quality_main` 2 行。
- 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 `main` HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，r1 已整合至未提交工作树。应用的是上文已独立核对的原补丁。其 33 个文件（14 新增、19 更新）逐项符合上文交接 TSV 的候选 SHA-256，`git diff --check` 与 `git apply --reverse --check --whitespace=error-all <scratch>/ARCH-ENERGY-002-r1.patch` 均退出 0。正式源码的 `uv run --no-sync alembic heads` 返回唯一 head `af6d8b2c4e90`。

正式整合文件按所属目录列在下表。表内路径均相对于首列目录。

| 目录 | 文件 |
| --- | --- |
| 仓库根 | `CODE_INDEX.md` |
| `backend/alembic/versions/` | `20261125_1400_af6d8b2c4e90_energy_curve_groups.py` |
| `backend/app/equipment_observation/` | `README.md`、`README.zh-CN.md`、`api/energy_curve_contract.py`、`api/routes.py`、`crud/__init__.py`、`crud/async_energy_curve_groups.py`、`models/__init__.py`、`models/energy_curve_group.py`、`services/async_energy_curve_groups.py` |
| `backend/tests/` | `test_energy_curve_groups.py`、`test_openapi_router_tags.py` |
| `backend/tests_mysql/` | `test_energy_curve_groups_mysql.py`、`test_energy_registered_ingest_mysql.py` |
| `contracts/` | `README.md`、`README.zh-CN.md` |
| `contracts/published/http-api/energy-curve-groups-v1/` | `README.md`、`README.zh-CN.md`、`openapi.json` |
| `frontend-js/` | `README.md`、`README.zh-CN.md` |
| `frontend-js/src/app/energy/` | `api/observations.js`、`components/EnergyCurveGroups.vue`、`components/energyCurveGroups.js`、`locales/en-US.json`、`locales/zh-CN.json`、`views/admin.vue`、`views/consumption.vue` |
| `frontend-js/src/app/monitor/components/observations/` | `CurveChart.vue` |
| `frontend-js/tests/module-registry/` | `energy-curve-groups.test.mjs`、`energy-write-sources.test.mjs`、`equipment-observation-columns.test.mjs` |

### 正式工作树自检与本机服务

以下 `<scratch>` 为 `/private/tmp/aiis-energy002-r1.brHaWJ`。备份和迁移分别在 `backend/` 运行 `UV_CACHE_DIR=<scratch>/uv-cache uv run --no-sync python -B <scratch>/adopt-dev.py <backup|migrate> <备份目录> <补丁路径> <补丁 SHA-256> <TSV 路径> <TSV SHA-256>`，两次均退出 0。原补丁与 TSV 的 SHA-256 见上文工件表。

- 在正式 `backend/` 执行下列 SQLite 聚焦回归，退出 0。41 项通过、2 项未选择，1 条既有 SQLite 时间适配弃用提示。第一个排除项为正式基线既有的 `Quality - Defects` 标签断言失败，第二个为依赖冻结 C2 与历史 Git 来源的测试。

  ```sh
  UV_CACHE_DIR=<scratch>/uv-cache PYTHONDONTWRITEBYTECODE=1 TESTING=True MYSQL_PORT=1 uv run --no-sync --env-file <scratch>/fixture.env pytest -p no:cacheprovider -q tests/test_energy_curve_groups.py tests/test_energy_meters.py tests/test_energy_registered_ingest.py tests/test_energy_public_reads.py tests/test_equipment_observation_r10_flow.py tests/test_monitor_frontend_permissions.py tests/test_openapi_router_tags.py -k 'not test_openapi_contains_only_public_core_operation_tags and not test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean'
  ```

- 在正式 `frontend-js/` 运行 `pnpm --config.verify-deps-before-run=ignore run build --outDir <scratch>/formal-dist --emptyOutDir`，退出 0，模块合同检查通过（10 组、32 路由），保留大 chunk 提示。使用正式项目配置，未覆盖 Vite 变量。`pnpm --config.verify-deps-before-run=ignore exec node --test tests/module-registry/{energy-curve-groups,energy-write-sources,equipment-observation,equipment-observation-columns}.test.mjs` 退出 0，36 项通过。`pnpm --config.verify-deps-before-run=ignore run test:modules` 退出 1，123 项通过、2 项失败，失败项与变更前正式基线相同，见上文。
- 既有 `8000` 后端和 `5190` Vite 前端服务自动加载正式源码，无需手动重启。协调者在 `backend/` 运行 `UV_CACHE_DIR=<scratch>/uv-cache uv run --no-sync python -B <scratch>/verify-formal-dev.py`，退出 0。实际健康与 Swagger 返回 200，运行 OpenAPI 中四个曲线方法均归 Energy 且声明 Bearer。经两个端口的 API 路径，已登录的管理配置读取与统计配置读取均为 200，未登录的相同读取均为 401。表计、指标、登记、实时、过程、质量、公有能耗 GET 与采集数据的 13 个只读回归端点均为 200。
- Playwright 在 `5190` 实际浏览器入口验证 PC 1440×900 浅色及平板横屏 1024×768 深色。配置管理显示四个上方入口，统计默认「按表计查询」，曲线配置和表计均为空。管理与统计读取成功，浏览器尝试业务写入 0 次。本机 dev 入口可打开并处理空配置状态，带表计的实际保存与绘图已在上文隔离环境验证，本轮本机 dev 检查只读。生产部署与现场设备操作未执行。

### 补充交给 fresh-context Verification

复核 ARCH-ENERGY-002 r1 正式工作树的 33 个后像、唯一迁移 head、获批 `3307` dev 迁移结果及 `8000`／`5190` 实际启动入口。候选补丁与 TSV 身份沿用上文。此次新增证据在 `<scratch>`，保留至独立核对并记录结论。

| 证据 | SHA-256 |
| --- | --- |
| `dev-migration-result.json` | `3922353b96ca061d533cde12ee5edb68d84b897e0d5878596c7d1ca025e065ba` |
| `formal-integration-result.json` | `8746356bf44624a53171eafe0ec0e82fe5ab03b51e6caa91e6774857756da525` |
| `dev-http-browser-result.json` | `3e3f17971096b9422f6e75f16241fd69dee683d10ebc74b9bade99e0ac2d9a21` |
| `formal-backend-scoped.log` | `0b03ec6efd22b7cf936ff1b02541f1153ea3a7f904d236e30b226883be7a45fd` |
| `formal-frontend-scoped.log` | `51da9842b3a5d20ce03363e41385d73928afcabb0d2285dffb469c46dd927516` |
| `formal-frontend-build.log` | `0f725ca3e2af6507943d9711b2d8291be0e5dc33d9ff7aa632362b3694658b70` |
| `formal-frontend-all.log` | `ed6c943086680fe5a1264ef39276ca41cd734efe9e509bebf98ea3934080379f` |

本次 Development 补记仅写入本文件，原 [独立验证记录](checklist.md) 保留以供 Verification 接续。迁移、整合和实际入口检查完成后，AC08 正式环境结论待独立复核，Human Owner 最终验收待定。

### 本轮临时资源

正式入口检查的 Playwright 浏览器已关闭，原任务隔离服务的回收情况见上文。本轮尚保留 `<scratch>` 内的候选、补丁、构建、脚本和证据，待独立结论落盘、必要证据持久化且无运行或后续依赖后由协调者回收。`/private/tmp/aiis-energy002-dev-backup.Uhk8JT/` 中的受限备份及校验摘要另行保留，待 Human Owner 确认无恢复需要后回收。
