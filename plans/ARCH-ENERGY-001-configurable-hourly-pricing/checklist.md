Task ID: ARCH-ENERGY-001
Revision: r2
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification
Handoff: 本机正式源码与 3307、8000、5190 只读复核通过，交 Human Owner 业务试写及最终验收。
Workflow Mode: STD

# ARCH-ENERGY-001 r2 独立验证

2026-11-25，Asia/Shanghai。本轮在 fresh context 核对正式工作树、规格、交接、补丁及已重建的独立候选。**AC06 失败**。正常迁移和业务页面上的验证不能覆盖下面的恢复缺陷。Human Owner 最终验收、正式源码整合和实际数据库采用均待后续处理。

## 阻塞项 QA1-01：冲突的暂存结构被推进到迁移后继

在 QA 专用 MySQL 8.4.6 中使用另一个空白 schema，复制正确前驱的两个旧价格表结构、版本表以及正常后继的空 `energy_price_hour_meta` 结构，保留 `id` 的 BIGINT 类型、非空、主键和所有索引。仅移除自动生成 ID 的属性。此夹具代表恢复前已存在外观相似但无法用于正常写入的空表。

1. 在独立合成库执行 `ALTER TABLE energy_price_hour_meta MODIFY id BIGINT NOT NULL`，将单行 Alembic 前驱设为 `af6d8b2c4e90`。设置匹配此合成库的 `ENERGY_PRICING_EXPECTED_SCHEMA`、`ENERGY_PRICING_EXPECTED_SERVER_UUID` 和 `ENERGY_PRICING_WRITE_WINDOW=<schema>:<uuid>:UTC`。
2. 独立候选后端运行 `python -m alembic upgrade 7cb6e40f3d19`。**实际退出 0**。`SELECT version_num FROM alembic_version` 返回 `7cb6e40f3d19`。
3. 执行与应用首次新增小时一致的字段集合 `INSERT INTO energy_price_hour_meta(hour_start,has_builtin) VALUES ('2026-11-24 12:00:00',0)`，MySQL 返回 **1364, Field 'id' doesn't have a default value**。应用在 `backend/app/energy/crud/async_energy_price.py:32` 同样依赖数据库生成 ID。
4. 候选迁移 `20261125_1800_7cb6e40f3d19_configurable_energy_pricing.py:105` 的列比较仅含类型、可空性和主键标记。预期应在推进版本前识别冲突并保留前驱。Development 重新交接时需要覆盖缺少 AUTO_INCREMENT 的空暂存表、正确暂存表的恢复以及迁移后第一次正常写入。

## 范围及证据

| 标准 | 独立检查及结果 |
| --- | --- |
| AC01 | Chrome 登录合成管理员，创建工业用水、按键查询、编辑英文名称和排序、启停并恢复。验证已存项目键无法编辑，带价格的项目改单位由真实 HTTP 返回 422，读者创建返回 403。 |
| AC02 | 正式价格页面验证缺值、真零、自定义项目单写、部分日及空日列、停用的历史列可见性。读回旧 current 与写前相等。四卡等宽齐边，多卡换行可横滚。拖拽 162→224px，重新进入仍为 224，重置为 162。详情显示操作人、备注及实际修改时间。 |
| AC03 | 真实回环 HTTP 登录后检查 401、403、409、422，非法精度、负值、非有限值、未来时间及混合无效项目。用同日、空日及越界页验证启用和停用列与分页独立。两个项目一次提交后，零价和值均正确。 |
| AC04 | 独立 HTTP 调用旧 POST 写入完整组，新 POST 更改其中一项及自定义项目，旧历史保留原 ID 并读回 1.2345、2、3。迁移和新旧路由的进一步断言由下述 MySQL 套件覆盖。 |
| AC05 | MySQL 的空价和有价前驱用例均包含同小时竞争、不同项目、新旧 POST、回填与注入故障的回滚断言，结果见命令记录。 |
| AC06 | **失败，详见 QA1-01**。在正常浏览器前驱运行真实 Alembic 成功，正常写入与读取通过。 |
| AC07 | 隔离 FastAPI、Vite、Chrome。两种弹窗在 1440×900、1024×768，两种语言和两种主题共 8 种组合通过。检查遮罩取消、滚动正文、页脚可达和无按钮重叠，生成 16 张合成截图。模块注册与构建通过，前端两个全量基线失败见下。 |
| AC08 | 正式 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。26 个已存在路径的基线哈希及 15 个应新增路径逐一验证。独立副本还原正式基线，运行 `git apply --whitespace=error-all` 后总计 41 个候选 SHA-256 全部吻合。正式树 `git apply --check --whitespace=error-all` 退出 0。实施仍在隔离候选，恢复缺陷阻止采用。 |

## 证据身份与运行环境

规格、Development 交接、实现补丁和逐文件清单 SHA-256 依次为：

~~~
446c014bfc6d3a52d34d41296010bd641b8e950e38981640659996545e62695e
68228f3faf41d128136ebd7836652afd1d22dff6cbb63f0bc6a2610f23a9be2e
62387124ef7758e101ffd6d68a847ee379b1a395f2d931af72adfbbf99a3656a
274e6d3b376e46d078fe7e00f901bf487a779fc9539e85426695b2fbf2b68cb3
~~~

macOS，锁定的 uv、pnpm 项目依赖，Chrome 的时区为 America/Los_Angeles。专用 MySQL 容器 `energy001-qa-b8ueocie` 仅绑定 127.0.0.1:52364，使用临时内存数据卷。以独立 FastAPI `uv run --no-sync run.py`（18191）与 Vite `pnpm --config.verify-deps-before-run=ignore run dev --host 127.0.0.1 --strictPort`（15291）测试两个真实入口。所有账户及数据库数据均为合成夹具。首次使用过长的夹具口令导致登录页提示 6–20 字符，改用有效的合成口令后全流程通过。首次配置的读者权限未包含在主管权限中，修正测试配置后重跑。正式服务、共享数据库及 002 均未执行变更。

## 命令记录

- `pnpm --config.verify-deps-before-run=ignore run check:modules` 退出 0，10 组、32 路由。`pnpm --config.verify-deps-before-run=ignore run build --outDir <qa>/dist` 退出 0，有 Vite 大块提示。
- `TZ=America/Los_Angeles pnpm --config.verify-deps-before-run=ignore run test:modules` 候选 121 通过、2 失败，正式基线 123 通过、2 失败。两处同名失败均为角色路由与模块发现的既有断言。`node --test tests/module-registry/{price-page,energy-write-sources}.test.mjs` 11 通过，退出 0。
- `node <qa>/browser.mjs` 退出 0。使用从交接脚本复制并调整测试端口及证据目录的 Playwright 脚本。登录后实测 `/energy/observations/admin` 与 `/auxiliary/price`。另以 HTTPX 直连独立 API 检查 AC03 与旧接口投影，退出 0。
- `uv run --no-sync alembic heads` 仅返回 `7cb6e40f3d19 (head)`。触达后端文件执行 `uv run --no-sync python -m compileall -q` 退出 0。解析变更 JSON 并逐项检查变更 Markdown 文件至本地目标的 233 个文件／目标组合，全部可解析。
- `TZ=America/Los_Angeles PYTHONPATH=. uv run --no-sync pytest -p no:cacheprovider -q tests_mysql/test_energy_pricing_mysql.py tests_mysql/test_energy_curve_groups_mysql.py tests_mysql/test_energy_meters_mysql.py tests_mysql/test_energy_registered_ingest_mysql.py tests_mysql/test_energy_public_reads_mysql.py`，专有 schema 且核对 server UUID，**6 通过，退出 0，128.20 秒**。该组覆盖非上海宿主、空库/有历史前驱、旧小时身份与边界、并发及事务、无关后继与观测接口；新增独立冲突夹具揭示 QA1-01。
- `uv run --no-sync pytest -p no:cacheprovider -m no_db -q tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py`，**111 通过，退出 0**。相同命令对 `tests/test_openapi_router_tags.py` 加 `-k 'not test_openapi_contains_only_public_core_operation_tags and not test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean'`，3 通过，退出 0；未选既有全局 Quality tag 和依赖 Git 历史的 C2 检查。上述测试结果均来自独立还原的候选。
- 首轮错误配置及其结果不用于本次断言。最终干净运行保留了 QA1-01 作为实施失败，退出码正常的其他套件不能代替该断言。

## 交接及临时资源

退回 Development 处理 QA1-01，下一次独立 Verification 应核对新补丁、新摘要并复测正常和冲突恢复路径。真实库的备份、停写、明确目标与实际迁移，以及服务切换须由 Human Owner 另行授权。

QA 临时目录 `/private/tmp/aiis-energy001-r2-qa.B8uEOciE` 供本轮独立重建、测试、截图及合成凭据使用。复现步骤与结果已写入本清单。已关闭专属 Chrome 会话、FastAPI、Vite 和 MySQL 容器，确认 18191、15291、52364 均无监听。QA 临时目录及其合成凭据完成回收。Development 的原交接保留在 `/private/tmp/aiis-energy001-r2-dev.qci1x4kb`，用于失败候选字节追溯；修正交接、复验及源码整合后由协调者核对并回收。

## 第二轮独立验证（2026-11-25，Asia/Shanghai）

**ARCH-ENERGY-001 r2 修正候选为 `qa_passed`，QA1-01 已关闭。** 本节为最新 verdict，前文保留第一轮失败时的原始检查。第二轮在 fresh context 独立读取正式任务、源码差异与测试，并从正式文件基线重建 41 个交付路径。

- **证据身份。** 正式 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。spec SHA-256 为 `446c014bfc6d3a52d34d41296010bd641b8e950e38981640659996545e62695e`，修正 tasks 为 `56e56f0d861d3dc8fdf36103b625247704a445edd718cf97ece8ee0b83bb7e28`。复验前 checklist SHA-256 为 `f9491e4a8bba22c7f67a331763ae2e1ac2f66f198c58e70a0b64524ea5e953fe`。
- **AC01、02、03、07。** 校验两份逐文件清单、原候选和新候选。39 个文件字节一致，包含全部页面、locale、应用 API、权限、服务及公开合同。仅显式迁移和 MySQL 回归测试发生改变。沿用上轮真实浏览器、HTTP、PC／平板、双主题与双语，以及构建和前端单测证据；本轮无新增浏览器运行。上轮记录的两个全量前端基线断言仍为已知限制。独立解析变更 JSON，并用 Python 逐一核对 233 个 Markdown 本地文件引用，均成功。
- **AC04、05、06。** 在 macOS 独立副本运行 `TZ=America/Los_Angeles PYTHONPATH=. uv run --no-sync pytest -p no:cacheprovider -q -x`，文件为 `tests_mysql/` 下的 `test_energy_pricing_mysql.py`、`test_energy_curve_groups_mysql.py`、`test_energy_meters_mysql.py`、`test_energy_registered_ingest_mysql.py`、`test_energy_public_reads_mysql.py`。专属 MySQL 8.4.6，回环端口 54503，UUID `bc9ab818-e8bf-11f1-b80b-2e389c4976e9`。7 通过、0 跳过，退出 0，115.95 秒。覆盖空及有价前驱、并发、新旧接口、补录、无关后继与观测读写。
- **QA1-01 复现与恢复。** 同一合成库中，分别删除暂存表主键的 AUTO_INCREMENT、额外添加 operator 唯一索引，真实 Alembic 均以非零退出。两次检查均保留前驱 af6d8b2c4e90、暂存表 DDL、空暂存数据以及两个旧表的全部行。修复夹具结构后正常升至 7cb6e40f3d19，保留 22、72、85 三个旧 ID 和九项小时记录。以有效 Bearer 经完整 FastAPI ASGI 路由 POST /api/v1/energy/pricing/hours，返回 200 并生成大于 85 的新 ID；旧 current 读回 0.9123、3.0123、999999.9999。旧源数据逐行保持一致。
- **代码检查。** 独立副本 `uv run --no-sync alembic heads` 仅返回 `7cb6e40f3d19 (head)`，两个返工文件的 compileall 退出 0。设置独立 UV_CACHE_DIR 后重跑成功。迁移 no_db 单测 4 通过，退出 0。
- **AC08 与最终交接。** 正式树 26 个基线文件及 15 个新增目标符合清单，在独立副本从基线执行 `git apply --whitespace=error-all` 后 41 个 SHA-256 全部匹配。正式源树 `git apply --check --whitespace=error-all` 退出 0。持久化的[修正补丁](evidence/r2-candidate/ARCH-ENERGY-001-r2.patch) SHA-256 为 `3ab47215aa201ec6e56e95624171a53d4895e6be548cbb0738edc0c19049310f`，[逐文件摘要](evidence/r2-candidate/ARCH-ENERGY-001-r2.sha256.tsv) 为 `c50a13c237ee5b534bafeb811644adf99e119887fa7b88079f5ef6f15040ea1d`。隔离候选可运行，正式热加载源码尚待整合，目标运行环境当前尚未采用此功能。交 Human Owner 决定最终验收，实际迁移、服务切换和部署需另行授权。
- **临时资源。** 第二轮 QA 专属容器 energy001-qa2-71ad 已停止并自动删除，数据卷使用 tmpfs。已回收独立副本、合成环境、测试输出和 uv 缓存所在目录 `/private/tmp/energy001-qa2.tNsTHTAf`。QA2 无保留的临时资源。两次 Development 交接目录由协调者在持久工件及后续依赖核对后回收。

## 2026-11-25 本机 dev 采用独立复核

**ARCH-ENERGY-001 r2 本机采用验证为 `qa_passed`。** 复核前 checklist SHA-256 为 `8854972f4beeaf2e2f188428ef078cf761b0838dd9c17ba1dbde812120a547c4`。spec 与 QA2 相同，追加采用记录的 tasks SHA-256 为 `b00713d5120438c73e5b5b51799c9c26522fa3006a397f27a6d9655a8fdf1302`，[采用证据](evidence/r2-dev-adoption.json) 为 `806ea8a9eda8fe2ed30eaa3ecc71f38840e52a08e1add3bf6ccf6355333e6090`。

- 正式仓逐文件计算 SHA-256，41/41 与 QA2 清单一致。`git apply --reverse --check --whitespace=error-all` 和 `git diff --check` 均退出 0。
- 独立读取 SQL 备份，590958 字节，SHA-256 为 `90ce31c10fa6332cc79d4a716f056b6af054b5320d458df3218a28278b75c9f9`。覆盖 70 张不同表，含前驱 revision、旧小时 3 行、旧归档 1 行及完整结束标记。目录、SQL、校验 JSON 权限为 0700、0600、0600。协调者记录首次客户端 9.3.0 遇到错误 1109 后恢复原服务，改用匹配的 8.4.6 客户端完成备份。此次 QA 未做恢复演练。
- 自正式 backend 运行 `uv run --locked --offline --no-sync python -B -`，使用项目设置和只读事务。首次沙箱访问 localhost 被拒，获准访问后退出 0。3307 的 schema、服务器 UUID 摘要与存档相符，revision 为 `7cb6e40f3d19`。旧 3 小时逐行对上 3 条新小时和 9 个项目价格，核对 ID、四种时间的一次性转换、价格、备注与操作人，旧归档仍为 1 行。
- 独立从 8000 和用户入口 5190 发 GET。每侧项目、现价、小时历史鉴权均为 200，匿名均为 401，三个项目、三张卡、三列历史与三小时匹配。两侧旧接口对账通过，设备实时、过程监测、能耗统计与集成的八条只读路径均为 200。复核已有浏览器证据，5190 的配置、卡片、历史列、录价弹窗取消和统计入口均已覆盖，业务写请求尝试为 0。统计选项为空，未验证有有效表计的样本曲线。
- 本机正式入口可交 Human Owner 试用。模型未用真实数据试写，业务写入试验与最终验收由 Human Owner 执行。此次 QA 没有执行迁移、启停或部署。
- 本轮 Verification 无临时资源。由协调者按 tasks 的资源清单回收失败备份、采用工作目录和开发候选，并记录结果。有效备份及同目录校验 JSON 保留至 Human Owner 确认解除恢复依赖。
