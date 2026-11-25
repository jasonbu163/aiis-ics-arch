Task ID: ARCH-OBS-010
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-OBS-010 r1 Development

Human Owner 于 2026-11-24（Asia/Shanghai）批准按 STD 启动 r1。实施和自检以 [获批规格](spec.md) 为准。工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD `7f654acd951171767bc253ea5bebdcda6435b608`，当前实现为该工作树已落地的未提交变更。依照根 AGENTS、STD canonical workflow、AIIS 配套约定、backend-arch、frontend-ui、i18n-workflow、code-document-indexer 实施。

## 实施结果

- 管理员从「能耗管理 → 配置管理 → 写入登记」查询、新增、编辑、启停和删除。表计指标配置保留原入口。登记只维护大小写敏感的标识、可选名称及启用状态。来源标识固定，逻辑删除保留历史数据及标识。中英文、公共请求封装、公共表格列宽和紧凑三段式弹窗均接入，遮罩关闭操作不提交变更。
- `POST /api/v1/integration/energy/registered-samples` 用现有严格 JSON 解析和 65,536 字节限制，按启用的能耗来源、真实采集时刻及已配置指标接受一包多表、多采样组。时间、精确数字和默认质量按合同规范化。一个登记行锁串行化同来源的写入和停用／删除。一个事务写一条能耗回执与全部样本。等价重放读取原回执，改变同一身份的正文返回 409。
- 独立表 `energy_write_sources` 使用独立内部命名空间。标识前缀不可通过 v2 生产者标识校验，登记时检查已存在的同内部标识能耗回执，以防误用历史导入数据。旧 v2 能耗事件与能耗登记来源可以使用相同的可见标识及事件键而各自写入。既有设备和过程业务服务继续按当前合同运行。
- 能耗保留配置的 MySQL 服务和库名校验，读写按能耗业务表运行。日常路径不读取全库迁移版本或设备来源表。日期写入使用已有上海数据库时钟。迁移 `b52e9c416a07` 是当前唯一后继，前驱 `a1c307f8d2e4`。迁移只新增登记表，并核验专用目标及前置结构。代码回退保留登记和回执，数据库迁移拒绝降级。
- 第三方合同、运行时 OpenAPI 的五项操作、请求／响应向量及用户指南已同步。

## 实际变更路径

| 范围 | 路径 |
| --- | --- |
| HTTP、模型和配置 | `backend/app/equipment_observation/api/{routes,write_source_contract}.py`、`models/{__init__,energy_write_source}.py`、`profile.py` |
| 数据库业务服务 | `backend/app/equipment_observation/services/{energy_registered_ingest,energy_write_sources,energy_reads,guard,ingest_v2}.py` |
| 迁移 | `backend/alembic/versions/20261124_2300_b52e9c416a07_energy_write_sources.py` |
| 聚焦回归 | `backend/tests/test_energy_registered_ingest.py`、`backend/tests_mysql/test_energy_registered_ingest_mysql.py`、`backend/tests/test_equipment_observation_{r10_flow,r8}.py`、`backend/tests/test_{generic_task,quality}_revision_guards.py` |
| 图与元数据测试 | `backend/tests/test_{acquisition_consumption_contract,equipment_temperature_migration,generic_task_migration_r3,legacy_acquisition_retirement,mapping_migration,observation_receipt_separation,observation_retirement}.py` 的唯一 head 期望，以及 legacy acquisition 当前 metadata 额外表 |
| 前端 | `frontend-js/src/app/energy/views/admin.vue`、`components/EnergyWriteSources.vue`、`api/observations.js`、`locales/{en-US,zh-CN}.json`、`frontend-js/tests/module-registry/energy-write-sources.test.mjs` |
| 合同与说明 | `contracts/published/http-api/energy-registered-ingest-v1/{README.md,README.zh-CN.md,openapi.json,examples/batch.json}`、`contracts/README.*`、`backend/app/equipment_observation/README.*`、`docs/equipment-status-process-monitoring{,-guide}.*`、`frontend-js/README.*`、`CODE_INDEX.md` |

协调基线记录于 `/private/tmp/aiis-obs010-coordinator.swH5gY/`。与 OBS008 同文件处保留其现有设备和过程变化，只修改能耗执行路径或替换其旧能耗门卫期望。与 OBS007／009 共用前端模块，登记改动限于配置管理及其独立 API／locale。候选文件清单和逐文件 SHA-256 在 `/private/tmp/aiis-obs010-dev.Witcd1/{changed-files.txt,candidate-source.sha256}`，对应归档 `candidate-source.tar.gz` 的 SHA-256 为 `7fb8cee20038c7d78c4ae259c05132d2709946f463ebe02a1abd5b130f8cc020`。

## DEV self-check

| 验收点 | 命令、结果及证据 |
| --- | --- |
| AC01 页面、认证、生命周期 | 实际 Chrome 的隔离构建在 PC 1440×900 与横屏平板 1024×768，分别检查中文／英文和浅色／深色，共八组通过。标题、独立正文滚动、页脚与列操作完整可达。确认关键字 Enter 查询、新增键盘触发、标识只读、搜索无匹配、读取失败重试、启停、逻辑删除及三个遮罩取消操作。普通列实际从 185px 拖至 219px，重载记忆并恢复至 185px。API 夹具收到了用户 Bearer 与正确的字面点编码。在实际隔离 MySQL 通过 JWT 确认未登录及无效凭据 401、普通用户管理 403。 |
| AC02、AC03 | SQLite HTTP 聚焦回归确认一个回执、两条有序样本，原能耗读 API 读出 120 kWh、累计值 9820、零值、上海时间和默认质量。验证越权表计读、无 Token 读取、空值、未知指标、无效来源、非数值、质量和错误区间的区分，以及无回执或样本残留。 |
| AC04、AC05 | `sh /private/tmp/aiis-obs010-dev.Witcd1/run-mysql.sh` 退出 0，1 个 MySQL 集成场景通过。实际并发相同正文返回同一回执，同身份竞争合法不同正文得 200／409。触发器使第二条样本失败后，比较库中回执、样本和指标配置无变化。模拟数据库提交后调用端失去确认，HTTP 503，用同一原包确认已提交结果。与来源停用／删除竞争时检查 200 对应完整的两条记录，或请求返回 403；停用后的重试拒绝，恢复允许。同名 v2 生产者和同事件键的并发写入均完成且独立，异常历史导入内部键的再分配返回 409。 |
| AC06、AC07 | 同一 MySQL 场景在合成前驱 A1 的业务结构上，通过原 HTTP 向旧能耗、设备和过程写样本，校验实际 Alembic 目标错误拒绝及成功升级前后逐行一致。成功执行专用能耗后继和独立无关后继，并保留旧 profile revision 测通能耗登记、用户读、v2 发现和重放、新登记 POST、实时及过程 v2 重放。隔离库移走设备来源表后能耗仍可用，缺失实际能耗配置表返回稳定 503。拒绝降级后既有数据仍在。 |
| AC08 静态和构建 | 后端聚焦命令退出 0，163 通过，1 条冻结的 BE003 历史用例按既有标记跳过，1 条既有 SQLite 适配器弃用警告。 `uv run --no-sync alembic heads` 显示唯一 `b52e9c416a07`。 `pnpm check:modules` 与 `pnpm build --outDir /private/tmp/aiis-obs010-dev.Witcd1/frontend-dist --emptyOutDir` 退出 0，构建报告原有大包体积提醒。新增前端两条聚焦用例通过。全量 `pnpm test:modules` 为 119 通过、2 失败，失败分别在 `page-access.test.mjs` 和 `registry.test.mjs`，为 OBS009 已记录的两个系统／维保顺序期望差异。 |
| AC08 OpenAPI 和文档 | `PYTHONPATH="$PWD" uv run --no-sync python /private/tmp/aiis-obs010-dev.Witcd1/check-contract.py`（backend）退出 0。与活动路由对比五个操作，确认管理四项均有 HTTPBearer，机器 POST 无认证声明。比较 request／response schema、合成示例、时间、零值及合同 Markdown 链接。 `git diff --check` 退出 0。 |

后端聚焦命令从 `backend/` 执行，`UV_CACHE_DIR=/private/tmp/aiis-obs010-coordinator.swH5gY/uv-cache`。

```sh
uv run --no-sync pytest -q -p no:cacheprovider \
  tests/test_equipment_observation_domain.py tests/test_observation_write_sources.py \
  tests/test_equipment_observation_r10_flow.py tests/test_equipment_observation_r8.py \
  tests/test_energy_registered_ingest.py tests/test_generic_task_revision_guards.py \
  tests/test_quality_revision_guards.py tests/test_observation_receipt_separation.py \
  tests/test_observation_retirement.py tests/test_business_module_permissions.py \
  tests/test_legacy_acquisition_retirement.py tests/test_acquisition_consumption_contract.py \
  tests/test_equipment_temperature_migration.py tests/test_generic_task_migration_r3.py \
  tests/test_mapping_migration.py
```

浏览器命令为 `node /private/tmp/aiis-obs010-dev.Witcd1/browser.cjs`，全部应用资源及 API 请求由夹具拦截。浏览器和本机隔离容器动作通过本地自动审批执行。证据日志为 `backend-focused.log`、`mysql-tests.log`、`browser.log`、`frontend-build.log`、`frontend-modules.log`、`contract.log`。迁移用例以合成前驱表结构和原 HTTP 写入的样本执行真实 Alembic，整条历史迁移链及实际部署环境的采用属于独立验证边界。

## developer_handoff

本记录交接精确 `ARCH-OBS-010 r1` 给 fresh-context Verification。复验对象为上述未提交交付工作树及候选文件摘要。验证需关注能耗和 v2 生产者命名空间隔离、提交不确定后的相同包重试、当前来源状态优先、历史回执不变，以及在无关数据库版本升级后保留目标身份、表计授权和登录验证。相同来源与实际采集时刻只允许一包。真实 dev 和生产仍需独立授权后执行数据库迁移和服务切换。当前只完成 Development self-check。

## 临时资源收尾

已关闭 Chrome，停止并移除专属的 `aiis-obs010-dev-Witcd1` 容器和其隔离数据库。临时密码、监听端口及容器标识文件已清除。保留 `/private/tmp/aiis-obs010-dev.Witcd1/` 内候选源码归档和摘要、构建、复验脚本、日志与截图，供本轮独立复验。复验结果落盘且无需返工后，由协调者回收。无本任务分支或额外 worktree。

## 2026-11-24 验收后本机 dev 迁移记录

Human Owner 于 2026-11-24（Asia/Shanghai）明确批准：“批准将本机 dev 数据库从 `a1c307f8d2e4` 迁移到 `b52e9c416a07`，并验证写入登记读取”。会话协调者执行迁移和在线检查，Development 据其证据补记。原交接正文的 SHA-256 `5020c49c998fb7a9b8694489fa4f87280f05bd9907195eecb70213575ffc823b` 与独立 [验收记录](checklist.md) 所引用的摘要一致。

- 目标为本机 `127.0.0.1:3307` 的 `industrial_level_2_system`，服务 UUID 和库名与已生效的观测 profile 一致。首次使用宿主机 mysqldump 9.3.0 的 `--routines` 选项，服务器报 `information_schema.LIBRARIES` 不存在。失败的临时备份在迁移前已清理。确认库内无存储例程、所有基本表均为 InnoDB 后，使用 `mysqldump --single-transaction --quick --skip-lock-tables --no-tablespaces --set-gtid-purged=OFF --skip-routines --events` 完成一致性备份。
- 通过精确目标门禁后，执行 `.venv/bin/python -B -m alembic upgrade b52e9c416a07`，退出码 0。迁移后 revision 为 `b52e9c416a07`，唯一新增表为 `energy_write_sources`。原表全部保留，`energy_metric_configs`、`energy_ingest_receipts`、`energy_consumption_main` 的行数迁移前后均为 0。
- 使用登录 Bearer 读取 `GET /api/v1/energy/write-sources`，现有 Vite 5190 代理和后端直连 8000 均由迁移前 503 恢复为迁移后 200，返回 `data: []`。迁移后匿名读取返回 401。通过 5190 检查能耗指标配置、能耗表计选项、设备及过程观测选项、过程曲线配置和采集数据选项，迁移前后均返回 200。
- 本次操作包含备份、迁移和接口读取。业务数据、现有服务进程和 profile 保持原状。独立 Verification 结论沿用验收记录。本次在线检查覆盖现有接口读取。

备份保留于 `/private/tmp/arch-obs-010-dev-backup.05atj081/dev-before-b52e9c416a07.sql`，目录权限 `0700`，文件权限 `0600`，大小 356048 字节，SHA-256 为 `862ba873985a573c0c6554559d5a3a1fdfd46cf6bdf578e0b9f13517785ef8bf`。保留至 Human Owner 确认在线结果及恢复需要后回收。本次迁移无其他保留的临时文件。
