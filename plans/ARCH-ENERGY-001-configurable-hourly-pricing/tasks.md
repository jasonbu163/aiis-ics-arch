Task ID: ARCH-ENERGY-001
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 精确 r2 隔离候选、补丁及自检证据交接 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-ENERGY-001 r2 实施与开发自检

Human Owner 于 2026-11-25（Asia/Shanghai）批准「继续 001，批准 001任务 按std启动dev」。[批准规格](spec.md) 的 SHA-256 为 `446c014bfc6d3a52d34d41296010bd641b8e950e38981640659996545e62695e`。Development 读取根契约、最近作用域文档、任务包与相关实现，应用 `backend-arch`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`。真实浏览器自检使用 Playwright 与已安装的 Chrome。

## 实施

- 能耗配置管理新增「单价项目配置」，沿用表计指标默认入口。管理员可查询、新增、编辑和启停。项目键去首尾空白后唯一、保存后固定。至少填写一种语言名称，界面可回退到另一语言。项目已有价格时单位锁定。三个内置项目沿用原名称、单位和双语展示。
- 能耗单价沿用 `/auxiliary/price`。现价、录入及历史按配置生成。缺值用「—」，真实零显示为「0」。停用项目在实际有记录的查询范围仍可查看。历史列偏好使用稳定项目键，支持拖拽、刷新恢复、重置与横向滚动。详情显示项目金额、记录及修改时间、操作者和备注。录入支持部分保存、总备注与逐项备注，区分省略和清除。成功后用实际事件日期分别刷新现价和历史。
- 新 API 沿用登录 Bearer 与独立价格读写权限，配置写入另查管理员。新旧写入在一个事务中锁定涉及的项目与小时，保留项目小时身份及创建时间。旧 GET 从同一价格事实生成完整三价，保留旧行 ID、事件和操作人，继承项修改时间参与旧视图的实际更新时间。旧历史总数及分页使用同一数据库查询快照。
- 显式 MySQL 后继 `7cb6e40f3d19` 接在 `af6d8b2c4e90` 后，创建项目、项目小时记录、兼容小时元数据。用固定 `+08:00` 存储从已验收 UTC 来源导入的时间瞬间，继承原规范小时键与 IANA 重复小时规则。迁移导入三项、保留旧 ID，并逐行核对金额、备注、actor 和各时间字段。两个旧来源表保留原样。
- 采用前核对确定的 MySQL schema、server UUID、精确前驱、UTC 时区来源、观测读取、备份及停写窗口。迁移只在 `ENERGY_PRICING_EXPECTED_SCHEMA`、`ENERGY_PRICING_EXPECTED_SERVER_UUID` 和 `ENERGY_PRICING_WRITE_WINDOW=<schema>:<server-uuid>:UTC` 匹配时执行。失败保留可检查的 DDL，结构及数据可对账时可重跑。原状数据允许受控 downgrade，出现新写入后需保护完整新表并在隔离恢复副本对账旧投影。实际采用与回退说明见[后端模块](../../backend/app/energy/README.zh-CN.md)，HTTP 形状见[双语合同及 OpenAPI](../../contracts/published/http-api/energy-pricing-v1/README.zh-CN.md)。

## Development 自检

| 验收范围 | 实测结果 |
| --- | --- |
| AC01 项目配置 | Chrome 使用真实登录和 MySQL 创建、查询及编辑合成工业用水，保持项目键并切换启停。中英文标签、原单位和名称回退经过浏览器与价格页测试。非管理员的配置写入为 403，已记录项目改单位为 422。 |
| AC02 动态价格页 | 启用即出现现价卡、录价字段、历史列。所选日无水价或完全空白时仍保留表头。仅录水价 0 后切回实际事件日，其他价格与完整旧 GET 相同。停用后当前卡和录入字段消失，有历史记录的日仍显示该项目。PC 四卡等宽并与历史卡左右对齐，增加九个合成项目后换行且表格可横向滚动。项目历史列从 162px 拖至 224px，刷新保留 224px，重置回 162px。详情可查备注、操作者及修改时间。 |
| AC03 新 API | MySQL 夹具的实际应用路由与签名 Bearer 覆盖 401、403、409、422，读写分权、非法数字和精度、显式零、未来日期、停用及不存在项目、总备注和每项备注的保留与清除。空日期、无记录项目、不同页与越界页均对照独立列集合。 |
| AC04 三价兼容 | 三个旧 HTTP 方法保持原形状、数值和身份。完整旧行逐字段比对，合成 ID 22、72、85 保留。空价格库先写单项时旧 current 返回 null，补齐后可生成完整组。自定义项目单写保持旧三价与时间，显式总备注更新才改变兼容备注。 |
| AC05 并发、补录与原子性 | MySQL 同小时相同项目、不同项目与新旧 POST 交错均验证。较早小时修正更新后续需要继承的兼容项及真实修改时间，较晚明确写入继续保留。故障触发器令第二项写入失败后，首项及小时元数据均回滚。 |
| AC06 迁移、时间与回退 | MySQL 8.4.6 在空价格和含旧价的前驱夹具执行真实 Alembic。错误 UUID 与冲突暂存结构拒绝，模拟导入中断保留前驱、空暂存结构可重跑。旧来源逐行保留；覆盖上海跨日、1991 年重复小时、非上海宿主进程及年 1000 协议边界。合成无关后继后价格与设备实时、过程曲线、能耗样本（含公开读取）继续工作。原状降级与重新升级成功，含新数据的直接降级拒绝；在独立临时表运行旧三价 UTC 回投并逐行核对。 |
| AC07 对话框和工程 | 实际入口验证两个录入弹窗的分组、遮罩取消不发请求、标题页脚可达及右侧按钮不重叠。长价格表单正文滚动时标题和页脚位置固定。1440×900、1024×768 与中英文、明暗主题共 8 个组合均验证，保留两弹窗共 16 张截图。编译、模块装配、构建、发布合同匹配和相对链接通过。 |
| AC08 源码交付 | 正式基线的 41 个实现路径逐项比对，补丁可应用，隔离副本实际应用后逐一匹配候选字节的 SHA-256。正式工作树仅写本任务记录，候选待独立 Verification 与后续采用。 |

## 实际命令、结果与限制

- 后端候选执行 `uv run --no-sync pytest -p no:cacheprovider -m no_db -q tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_openapi_router_tags.py -k 'not test_openapi_contains_only_public_core_operation_tags and not test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean'`，退出 0，**113 通过、2 未选**。前者为既有 Quality tag 断言，后者需要冻结 C2 的 Git 历史，候选按任务隔离未复制 .git。发布合同及历史时间边界最终专项 `-k 'test_published_pricing_openapi or test_pricing_revision_layout or test_real_service_asgi_checks_derived_hour'` 退出 0，**7 通过**，包含新增的 OpenAPI 六路认证和数据结构比对。
- 通过专用回环 MySQL 及明确夹具身份，在候选后端以 `TZ=America/Los_Angeles PYTHONPATH=. uv run --no-sync pytest -q -x -p no:cacheprovider tests_mysql/test_energy_pricing_mysql.py tests_mysql/test_energy_curve_groups_mysql.py tests_mysql/test_energy_meters_mysql.py tests_mysql/test_energy_registered_ingest_mysql.py tests_mysql/test_energy_public_reads_mysql.py` 执行，退出 0，**6 通过**。MySQL 8.4.6 来自本机镜像，仅绑定回环随机端口 64076。该结果包含两种单价前驱夹具，其余四个为曲线、表计、登记和公开读取。
- `uv run --no-sync alembic heads` 返回唯一 head `7cb6e40f3d19`，`uv run --no-sync python -m compileall -q` 检查触达的后端目录与文件，退出 0。公开合同的两个示例用实际 Pydantic schema 解析，退出 0。
- 候选前端运行 `pnpm --config.verify-deps-before-run=ignore run check:modules`，退出 0，为 10 组、32 路由。相同依赖下 `pnpm --config.verify-deps-before-run=ignore run build --outDir /private/tmp/aiis-energy001-r2-dev.qci1x4kb/dist --emptyOutDir` 退出 0，有既有的 Vite 大块提示。模块套件 `TZ=America/Los_Angeles pnpm --config.verify-deps-before-run=ignore run test:modules` 退出 1，**121 通过、2 失败**，失败名称与正式基线一致，分别为 `admin, supervisor, operator and unknown share route/menu/default decisions` 和 `actual source preserves Core route identity, shell locales and default-disabled demo`。基线 123 通过与候选 121 通过的差异来自将原 10 个固定三价页面用例替换为 8 个动态项目用例，时间、精度、保存、竞态及失败语义继续覆盖。
- `node /private/tmp/aiis-energy001-r2-dev.qci1x4kb/browser-check.mjs` 退出 0。Chrome 通过候选的正式 `uv run --no-sync run.py` 和 `pnpm … run dev` 入口登录合成账号。该后端绑定 `127.0.0.1:18101`，Vite 绑定 `127.0.0.1:15191` 并代理同源 API。这次浏览器使用 America/Los_Angeles 时区。
- 正式工作树的 `git apply --check --whitespace=error-all <patch>` 退出 0。补丁在私有临时基线副本实际应用，41 个结果逐一对照 SHA-256，18 个新增 Markdown 相对链接及修改的 JSON 校验通过。无 Git commit 或推送。

## 精确交接

正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD `9c30258358f169792d4cd0faeae3b80a41b43b81`。候选 `/private/tmp/aiis-energy001-r2-dev.qci1x4kb/candidate`，基于正式工作树当时的 3,984 个源文件快照，包含原有未提交源码。以下为 41 个批准路径，其中 15 个新增，26 个修改。

| 目录 | 文件 |
| --- | --- |
| 仓库根 | `CODE_INDEX.md` |
| `backend/` | `README.md`、`README.zh-CN.md` |
| `backend/alembic/versions/` | `20261125_1800_7cb6e40f3d19_configurable_energy_pricing.py` |
| `backend/app/energy/` | `README.md`、`README.zh-CN.md`、`manifest.py`、`pricing.py`、`api/energy_price.py`、`api/energy_pricing.py`、`api/routes.py`、`crud/async_energy_price.py`、`models/__init__.py`、`models/energy_pricing.py`、`schemas/energy_price.py`、`schemas/energy_pricing.py`、`services/async_energy_price.py`、`services/async_energy_pricing.py` |
| `backend/tests/` | `test_energy_price_api.py`、`test_energy_price_migration.py`、`test_energy_price_service.py` |
| `backend/tests_mysql/` | `test_energy_pricing_mysql.py`、`test_energy_registered_ingest_mysql.py`（共享隔离夹具参数） |
| `contracts/` | `README.md`、`README.zh-CN.md` |
| `contracts/published/http-api/energy-pricing-v1/` | `README.md`、`README.zh-CN.md`、`examples/item.json`、`examples/price.json`、`openapi.json` |
| `frontend-js/` | `README.md`、`README.zh-CN.md` |
| `frontend-js/src/app/energy/` | `api/pricing.js`、`components/EnergyPriceItems.vue`、`components/energyPricing.js`、`locales/en-US.json`、`locales/zh-CN.json`、`views/admin.vue`、`views/price.vue` |
| `frontend-js/tests/module-registry/` | `energy-write-sources.test.mjs`、`price-page.test.mjs` |

以下工件均在 `/private/tmp/aiis-energy001-r2-dev.qci1x4kb`。

| 工件 | SHA-256 |
| --- | --- |
| `ARCH-ENERGY-001-r2.patch` | `62387124ef7758e101ffd6d68a847ee379b1a395f2d931af72adfbbf99a3656a` |
| `ARCH-ENERGY-001-r2.sha256.tsv` | `274e6d3b376e46d078fe7e00f901bf487a779fc9539e85426695b2fbf2b68cb3` |
| `ARCH-ENERGY-001-r2-dist.sha256` | `dd2859db727896629353ac8dabe7cccb3ae5b9ca3b468a750dd14a3d1924bc7b` |
| `ARCH-ENERGY-001-r2-evidence.sha256` | `18002ea726b0c4ace4a61792a20ce151c5bf815f3bad9a391210b07808e3883c` |
| `evidence/mysql-development.log` | `9253a9411067dc6812df0ee890050f6846f8ee0529acbbb123526edc214cc714` |
| `evidence/browser-check.log` | `c5b7b1e0c6baf742a49b2b8d7c1892c1e2db176949e9e601cb99bf22db80c8ea` |

本次交接对应隔离验证环境。正式源码等候协调者在独立验证后整合。真实 dev 的迁移及运行采用需由 Human Owner 就目标、恢复备份、停写窗口和服务切换另行授权。目前正式服务继续使用既有代码及数据库。本次未操作真实或共享数据库、已运行的正式服务以及发布部署。附带风险为旧格式仅能承载完整三价投影，切换后的自定义项目及部分写入需要保留完整数据库备份。

## 临时资源收尾

任务专属 Chrome 会话、Uvicorn、Vite 和 MySQL 8.4.6 容器已关闭并回收，确认 18101、15191、64076 无监听。已回收合成连接环境、验证缓存、临时 SQL 恢复副本及浏览器调试工件。候选、补丁、摘要、构建、浏览器复验脚本、结果及 16 张合成截图保留在任务临时根目录，供独立 Verification 及采用前字节核对。独立证据落盘并完成整合或保留可恢复补丁后，由协调者回收目录。

## QA1-01 返工与第二次 Development 交接

同一获批 Revision `ARCH-ENERGY-001 r2`。规格 SHA-256 仍为 `446c014bfc6d3a52d34d41296010bd641b8e950e38981640659996545e62695e`。原交接与独立验证记录保留。此次处理 [QA1-01](checklist.md)。

- `backend/alembic/versions/20261125_1800_7cb6e40f3d19_configurable_energy_pricing.py` 的暂存结构校验现比较声明与 MySQL 反射后实际承担自增的列。缺少 `AUTO_INCREMENT` 且仍为 BIGINT 主键的暂存表会在导入和推进版本之前拒绝。现有唯一索引集合校验继续生效。迁移仍为 `7cb6e40f3d19`，前驱仍为 `af6d8b2c4e90`。
- `backend/tests_mysql/test_energy_pricing_mysql.py` 新增实际 MySQL 回归。以有历史的前驱和空小时元数据暂存表验证两种冲突。缺失自增属性或额外唯一索引时，Alembic 退出非零，前驱版本、暂存表 DDL、暂存数据和两个旧来源表原样保留。恢复正确结构后重跑成功，旧 ID 22、72、85 和九个项目价格正确导入。经应用的 Bearer `POST /api/v1/energy/pricing/hours` 第一次写入新小时，返回 200，生成大于 85 的新 ID，旧 current 继承出的三价为 0.9123、3.0123、999999.9999。

### 本轮自检

- 新增回归先对原迁移运行 `uv run --no-sync pytest -p no:cacheprovider -q tests_mysql/test_energy_pricing_mysql.py -k test_staged_hour_meta_requires_auto_increment_and_no_extra_uniqueness`，退出 1。明确复现异常暂存表被成功升级，导致应拒绝的断言失败。证据为 `evidence/mysql-before-fix.log`。
- 修复后用专属 MySQL 8.4.6 回环夹具运行 `TZ=America/Los_Angeles PYTHONPATH=. uv run --no-sync pytest -p no:cacheprovider -q -x tests_mysql/test_energy_pricing_mysql.py tests_mysql/test_energy_curve_groups_mysql.py tests_mysql/test_energy_meters_mysql.py tests_mysql/test_energy_registered_ingest_mysql.py tests_mysql/test_energy_public_reads_mysql.py`，退出 0，**7 通过**。包含新回归和既有的价格、观测、表计、曲线及公开读取回归。
- `uv run --no-sync pytest -p no:cacheprovider -m no_db -q` 执行 `test_energy_price_api.py`、`test_energy_price_service.py`、`test_energy_price_migration.py`、`test_equipment_observation_r10_flow.py`、`test_openapi_router_tags.py`，排除上文同一全局 Quality tag 与冻结 C2 历史检查，退出 0，**140 通过、2 未选**，有一项 SQLite 时间适配弃用提示。最终迁移专项 `uv run --no-sync pytest -p no:cacheprovider -m no_db -q tests/test_energy_price_migration.py` 退出 0，**4 通过**。Alembic 单一 head 确认及两个返工文件编译均退出 0。
- 正式树执行 `git apply --check --whitespace=error-all`，退出 0。在独立临时副本应用完整修正补丁后，41 个文件与交付清单的 SHA-256 一致。对照初次候选只有迁移文件及上述 MySQL 测试的候选字节变化。前端及应用运行代码沿用初次交接，本轮验证使用实际注册 API，浏览器与前端构建证据沿用原记录。

### 修正交接

正式工作树基线 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。请 fresh-context Verification 核对以下修正版本，候选为 `/private/tmp/aiis-energy001-r2-dev-rework.6tt419eh/candidate`。原始候选及原补丁继续保留，以便追溯 QA1。

| 修正工件（同一临时根目录） | SHA-256 |
| --- | --- |
| `ARCH-ENERGY-001-r2.patch` | `3ab47215aa201ec6e56e95624171a53d4895e6be548cbb0738edc0c19049310f` |
| `ARCH-ENERGY-001-r2.sha256.tsv` | `c50a13c237ee5b534bafeb811644adf99e119887fa7b88079f5ef6f15040ea1d` |
| `ARCH-ENERGY-001-r2-evidence.sha256` | `d44011d3d1d586a6995b45b4f3f22f00b3000db0f9bf74dca408c13576f0ff9e` |

Development 在正式工作树只追加本记录。正式源码及目标运行状态待独立 Verification 和后续采用。真实 dev 迁移和服务切换仍须由 Human Owner 另行授权。

返工专属 MySQL 及合成 schema 已回收，确认回环端口 53763 无监听。已回收合成环境文件、测试缓存及补丁核对副本。修正候选、两份清单、完整补丁和验证日志保留至独立复验及整合或补丁归档完成。

## 2026-11-25 本机 dev 采用与正式源码交接

Human Owner 于 2026-11-25（Asia/Shanghai）明确批准「批准在本机 3307 dev 库采用 ARCH-ENERGY-001 r2。」具体操作包括核对精确前驱、备份、暂停价格写入、迁移和旧数据对账、整合正式源码、恢复本机后端，以及在 5190 只读检查。业务试写由 Human Owner 执行。协调者执行采用操作，本段由 Development 核对证据并补记。同一获批 r2 的范围沿用 [spec.md](spec.md)。持久操作证据 SHA-256 为 `806ea8a9eda8fe2ed30eaa3ecc71f38840e52a08e1add3bf6ccf6355333e6090`。[本机采用证据](evidence/r2-dev-adoption.json)

### 备份、迁移与源码整合

- 目标为本机 `127.0.0.1:3307/industrial_level_2_system`，MySQL 8.4.6，前驱 `af6d8b2c4e90`。首次用宿主机 9.3.0 客户端备份时，因目标缺少 `INFORMATION_SCHEMA.LIBRARIES` 收到 MySQL 1109，`mysqldump` 退出 2。协调者在任何迁移开始前恢复旧服务。再次核对目标身份与前驱后，停止旧后端，给 `energy_price_hours` 和 `energy_prices` 持有数据库 READ 锁，使用目标同版本的容器内 8.4.6 客户端执行同一逻辑备份。
- 核对备份完成标记、`af6d8b2c4e90` 版本标记、全部 70 张表的覆盖，以及原小时价格 3 行与追加归档 1 行。备份为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/data/dev-backups/arch-energy-001-r2-9yepf7io/dev-before-7cb6e40f3d19.sql`，大小 590958 字节，目录权限 `0700`、文件权限 `0600`，SHA-256 为 `90ce31c10fa6332cc79d4a716f056b6af054b5320d458df3218a28278b75c9f9`。Development 复核了备份摘要和权限。恢复演练未执行。
- 停写窗口内以隔离 Alembic 配置执行 `alembic.command.upgrade(config, "7cb6e40f3d19")`，完成精确升级。原 70 张表定义一致，原小时价格 3 行与追加归档 1 行逐行一致。新增 `energy_price_items`、`energy_price_hour_meta`、`energy_price_item_hours`，分别写入三个内置项目、三个旧小时 ID 和九个项目价格。新表的金额、备注、操作者及 ID 逐项对账，四个时间字段转换为固定 `+08:00` 后保持原 UTC 瞬间。
- 对正式工作树应用经独立验证的修正补丁。HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，41 个路径的正式文件与交付清单逐项相符。Development 重新核对 41 个 SHA-256 和 `git apply --reverse --check --whitespace=error-all`，退出 0。协调者运行 `git diff --check`，退出 0。[交付文件清单](evidence/r2-candidate/ARCH-ENERGY-001-r2.sha256.tsv)

### 本机只读验证

- 正式后端由 `uv run --no-sync run.py` 恢复，监听 8000 并启用重载。Vite 保持原进程监听 5190。直连 8000 和经 5190 代理分别请求 `/api/v1/energy/pricing/items`、`/api/v1/energy/pricing/current`、`/api/v1/energy/pricing/hours?page=1&pageSize=24`。每侧三次带 Bearer 的 GET 返回 200、三次匿名 GET 返回 401。返回三个项目、三个现价卡对应项、三列历史单价。旧 `GET /api/v1/energy?page=1&pageSize=100` 的三行和 `GET /api/v1/energy/current` 也与原库逐字段对账。运行时 OpenAPI 的六个新方法核对 Energy 分组与 Bearer 声明。
- 直连和代理侧的设备选项、实时样本、过程选项、过程样本、曲线配置、能耗选项、能耗曲线组、公开能耗 latest 均返回 200。实时样本 5 条、过程样本 23 条、过程曲线配置 12 条与切换前一致。现有能耗表计选项和能耗曲线组均为 0，当前环境可核对其空态与读取入口。
- Chrome 在 `http://127.0.0.1:5190` 以中文和 `1440×900` 打开配置管理、能耗单价和能耗统计。核对三个可配置项目、三个现价卡、三列历史单价、录价弹窗取消及表计空态，`writeAttempts=0`。本轮采用验证未执行业务写入。
- 正式树的后端聚焦 `no_db` 检查为 7 通过、68 未选，编译退出 0。前端聚焦模块测试 11 通过，`check:modules` 通过（10 组、32 路由），Vite 构建退出 0。

### 临时资源和保留条件

正式采用已经整合至本机工作树，8000／5190 可供 Human Owner 试用。保留通过核验的 590958 字节备份及同目录 `backup-verification.json`，直到 Human Owner 确认无需用于恢复。首次失败的部分备份仍留在隔离的 `backend/data/dev-backups/arch-energy-001-r2-uz52ynff/`，协调者将在独立核对后回收。协调者持有的 `/private/tmp/aiis-energy001-adopt.HcfLdq` 及前两次 Development 候选为后续复核资源，待证据独立核对且归档完整后由协调者回收。本次记录补充未创建临时资源。
