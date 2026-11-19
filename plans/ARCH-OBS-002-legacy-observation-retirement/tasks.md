# ARCH-OBS-002 r1 开发记录

Development 根据 Human Owner 在 2026-11-18 的答复“批准 r1 和隔离验证”实施。[批准规格](spec.md) 的 SHA-256 为 957956ad81ed13bea03efd98a691a62f52b7526187d8c653ae1bfdf3e0424e37。正式工作树尚未整合，真实 dev 切换与 Owner 最终验收待独立决定。

## 实现

- 当前设备状态、过程历史和独立表计写入保持 v2、原 URL 及现有配置／管理权限。清退旧 equipment、monitor 后端模块、collector 和 r8 查询共 22 个 HTTP 方法。旧 v1 先核验机器身份和设备、目标、组、指标授权，再明确拒绝，不查询或重放旧回执。
- 明确前向 Alembic c9e1a3b5d720，前驱 ae20b4d6f831。检查连接、迁移状态、维护确认、依赖可见性和回执，在同一 MySQL 连接取得有界表锁后重新核验，再用单条 InnoDB DROP 处理 18 个目标并修改回执的两个默认值。观察 profile 只接受新 head。PLC Facts 和共享业务存储接受新 head 并保留旧版本边界。
- 复用现有新版能耗页 /monitor/consumption 和页面授权 monitor.energy。旧链接、专用代码和旧页面退出，公开示例和双语文档同步。monitor.consumption 被配置校验识别为未知页面。现有后端权限配置没有额外授权。CLI 不再接受 equipment／monitor，原 performance 参数仍保留，当前其历史巡检导出不可用。

## Development 自检

| 范围 | 实际命令与结果 |
| --- | --- |
| 前端装配与回归 | 候选前端执行 node scripts/check-module-manifests.mjs --check，通过，25 路由／9 组。执行 node --test tests/module-registry/*.test.mjs，90 通过、0 失败。pnpm 11 对隔离副本的既有依赖链接尝试更新，改直接执行 package.json 声明的命令，未改依赖。 |
| 前端权限与构建 | 使用合成 supervisor grant monitor.energy 和空 operator grants 执行 node scripts/check-page-access.mjs --check --mode production，exit 0；使用 monitor.consumption 则明确提示未知键并 exit 1。同一合成授权执行 ./node_modules/.bin/vite build，exit 0，仍有 bundle chunk 大小提示。 |
| 后端静态 | 项目 .venv Python 3.13，以任务专属 PYTHONPYCACHEPREFIX 执行 python -m compileall -q backend/app/equipment_observation backend/alembic backend/tests，exit 0。 |
| 隔离迁移 | 在候选用 run-final-db.sh、migration_checks_final.py、项目 Alembic 连接实际 MySQL 8.4.6，经 ae20b4d6f831 升至 c9e1a3b5d720。两次合成验证在 obs002_fixture 和 obs002_fixture_final。最终退出 18 个旧表，逐表核对 56 张保护表的行及 SHOW CREATE TABLE，排除自增计数，允许回执的两个批准默认值变化。已有合成 v2/r10 回执、区域配置及实时快照保持。价格／采集等受保护表参与对账，其中有空表。最终保护对象 SHA-256 590d53623d0b335c91e6bddf7ac6aac096a4e974ae8a676475cf2cdeee81f7ab。 |
| 拒绝和恢复 | 实测拒绝缺维护确认、目标 UUID 错误、错误前驱、非空归档、v1 或未知回执、伪装新版且含归档位置的回执、外部 FK／视图及缺表。不同真实连接在最终查空后竞争 INSERT，等待真实表锁，删除后返回 1146。在真实多表 DROP 后注入异常模拟结果未知，18 表已退出而前驱仍登记，保护对象一致，迁移拒绝再次运行。用 18 份合成的空表 DDL 反序重建后逐表精确对账，再以 Alembic 正常升级。 |
| 实际 MySQL ASGI | run-smoke.sh／http_smoke.py，exit 0。用正式路由、实际异步数据库连接、仓库外合成 profile 和真实机器 Bearer 验证指标定义／发现、两路多区域、0／false、晚到、空包、同事件重试及异正文冲突；旧 v1 匿名 401／有授权 409；独立表计汇总 5 kWh；观察和 Facts 的新 head 探针。管理员、supervisor、operator、无权限和匿名经真实路由授权，测试以依赖注入提供人类身份，未复验账户登录。夹具结束时 aiomysql 报事件循环已关闭，无断言失败。 |
| 后端 no_db | 初次 537 通过、55 失败、16 skip，67 个历史 setup error 源于缺少 Git 和历史 fixture。修订本任务相关断言后定向运行 181 通过、8 个已有 skip、9 失败。另用真正的仓库 Git 上下文、固定存档时点 bcafa89fa31bdf62329bced89baebc193323a739 的公开旧源码、任务自己的 --basetemp 进行整套复验。该存档时点与历史 ACQ-002 QA3 的未提交源码区分。最终统计见下。 |

## 交付物和资源

- 隔离候选位于 /private/tmp/arch-obs-002-r1-3y1wnavr/candidate。来源正式 HEAD f7c5608c0e433612b15821a578a7ef3e4f155cdb，加上含 ae20b4d6f831 的必要未提交前驱。起始 1,492 个来源文件的 preimage.sha256 摘要 d55f76ead8ddf749ff1c152bab02c81310e7f94b2beccfbec0ae21ee38347757。
- 本任务拥有的 Development 容器 arch-obs-002-r1-dev，完整 ID 7ccda8c167ccecb6a15ea57da4b63cd40ee15dde9ef09c32d4511a4b107a72d6，绑定 127.0.0.1:13318，使用本地 arm64 mysql:8.4.6 镜像 sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9。合成配置使用任务临时目录 0600 文件。默认 sandbox 禁止 loopback，受审执行只连接批准的 13318。未创建 QA 容器。
- 仅协调者按已批准资源范围核验并回收上述容器。保留候选、清单、验证日志、合成恢复 DDL 到独立复验、正式整合校验和关键证据持久化为止。真实 3307、真实 profile、真实 .env 和用户服务未操作。实际维护应重新核验相关 writer、连接、元数据可见性和恢复材料。真实设备、SMA、DAA、冻结 CA 及生产未验证。

## 后端扩展复验

候选使用原仓库 Git 读取入口、临时公开历史 fixture、已安装 .venv 和任务专属 --basetemp，执行 python -m pytest tests -m no_db -q --tb=short。最终 **634 passed、5 failed、12 skipped、24 deselected，exit 1**。当前候选的 python -m app.module_preflight --project-root "$PWD" --check-only 与 python -m alembic heads 单独通过，唯一 head 为 c9e1a3b5d720。无新增 skip 用来替代本次迁移或 API 验证。

| 当前候选测试 | 失败与对照 |
| --- | --- |
| test_business_module_reintegration.py::test_f_has_exact_58_tables_and_price_has_one_owner | 历史 58 表的现行 metadata 子集断言失败；原固定 f7c5608 源码的同名测试也失败。候选仍验证 F recorder 的 58 表及在独立清退测试验证当前 metadata／价表。 |
| test_business_module_reintegration.py::test_performance_sync_descriptors_stay_local_and_uniquely_owned | 原 8 descriptor 测试已退出旧设备／过程四项，余下旧 Performance descriptor 的导入无法读取 ProcessSpeed。固定 f7c5608 的原 test_eight_sync_descriptors_stay_local_and_uniquely_owned 同样 ImportError。 |
| test_module_contract.py::test_integration_public_surface_and_private_boundary | 扫历史 C2 时，在断言目的之前失败于旧 System 的 projection.policy_catalog:SnapshotPolicyCatalog 私有导入。以同一公开历史夹具在原固定 f7c5608 对照，三项全部同样失败，错误与 ACQ-002 已知记录一致。 |
| test_module_contract.py::test_temperature_env_helper_is_only_additive_public_setting | 同上。 |
| test_module_contract.py::test_business_time_public_pure_symbols_and_private_rejection | 同上。 |

ACQ-002 已记录这三个 C2 历史错误及 QA3 原源码的区别。候选测试使用的公开旧源来自 bcafa89fa31bdf62329bced89baebc193323a739，和原 QA3 未提交工作内容不同。 [ACQ-002 独立复验记录](../ARCH-ACQ-002-legacy-projection-retirement/checklist.md)

另将 test_business_integration_service.py、test_mapping_api.py 和 test_mapping_service.py 逐用例核对后逐字节归档。活跃用例针对本次退出的设备／过程旧实现，原 skip 用例针对先前退出的旧实绩。原路径及 SHA-256 保存于候选 backend/tests/historical_observation/README.md。以 git archive 固定 f7c5608c0e433612b15821a578a7ef3e4f155cdb 导出的旧源码复跑三份旧测试，**75 passed、21 原 skip，exit 0**。这组历史结果不计入当前候选统计。通用业务合同与存储、现有授权、前向链及各历史迁移 recorder 保持各自测试。

## Developer handoff

交给 Coordinator 和 fresh-context Verification 的候选位于 /private/tmp/arch-obs-002-r1-3y1wnavr/candidate。此为隔离候选 handoff。正式源码整合及真实 dev 切换仍待批准，当前工作树只有本 Development 记录。

- candidate-manifest.tsv 记录 225 项（A6／M75／D144），每项为状态、开始时正式树 preimage SHA-256、候选 SHA-256、handoff 时正式树 SHA-256、相对路径。manifest SHA-256 6c28642daea8688c19e1c85dbc380d39e5fd840b4488753507a6e6df6ad6dc69。未纳入候选生成物、依赖链接、任何真实配置或数据库。
- candidate-nondrift.unified.diff 是排除当前三个漂移路径的辅助 diff，SHA-256 32455b1f958879268d795bfe9e7a260bbeba54f10a622b55f21f068dd0f58a2e。git apply --check --whitespace=error 已对正式树只读通过；启用正式操作前重新检查逐文件 preimage，禁止仅根据旧清单覆盖。新增／修改 Markdown 链接的本地路径抽查无缺失，差异新增行无普通尾随空白。
- 三个重叠路径为 CODE_INDEX.md（同时更新计划／实绩编辑器和共享字段页索引）、frontend-js/tests/module-registry/page-access.test.mjs（实绩前驱有当前授权列表更改）及 frontend-js/tests/module-registry/registry.test.mjs（并行前驱新增计划／实绩 registry 断言）。正式整合须对这三份做按行语义合并，保留并行任务内容，同时应用 r1 观测受影响的入口和断言。
- 当时并行前驱漂移还发生在 backend/app/task/domain.py、frontend-js/src/app/performance 的 manifest.js 和双语 locale、frontend-js/src/app/plan 的 manifest.js、双语 locale、TaskConfigDialog.vue、TaskPage.vue 及 frontend-js/tests/module-registry/generic-task.test.mjs。保留它们的正式原字节。并行任务记录仍引用旧 test_mapping_api.py，正式整合前须协调引用指向其明确使用的历史源码。
- 关键原始日志：migration-checks-final.log、fixture-restoration-ddl.json、http-smoke.log、frontend-build.log、pytest-final.log、pytest-original.log、pytest-original-f.log、pytest-original-c2.log、preflight.log。守卫／并发／恢复及 ASGI 的复现脚本保留在同一私有目录。正式整合后复跑 backend 应用正常装配、唯一迁移图、前端权限和构建、最新并行任务回归及对应 SQL 和 API；协调者按规格在维护窗口重新核对真实目标/版本/配置，直到其独立验收。

<details>
<summary>候选逐文件路径</summary>

```text
M CODE_INDEX.md
M README.md
M README.zh-CN.md
M backend/.env.docker.dev.example
M backend/.env.docker.prod.example
M backend/.env.example
M backend/README.md
M backend/README.zh-CN.md
M backend/alembic/env.py
A backend/alembic/versions/20261118_1645_c9e1a3b5d720_retire_legacy_observation.py
M backend/app/equipment/PLAN.md
M backend/app/equipment/PLAN.zh-CN.md
M backend/app/equipment/README.md
M backend/app/equipment/README.zh-CN.md
D backend/app/equipment/__init__.py
D backend/app/equipment/api/__init__.py
D backend/app/equipment/api/integration.py
D backend/app/equipment/api/mapping_http.py
D backend/app/equipment/api/mapping_samples.py
D backend/app/equipment/api/routes.py
D backend/app/equipment/api/temperature_dashboard.py
D backend/app/equipment/api/temperature_http.py
D backend/app/equipment/api/temperature_samples.py
D backend/app/equipment/config.py
D backend/app/equipment/crud/__init__.py
D backend/app/equipment/crud/async_drive_sample.py
D backend/app/equipment/crud/async_equipment.py
D backend/app/equipment/crud/async_integration.py
D backend/app/equipment/crud/async_mapping_ingest.py
D backend/app/equipment/crud/async_production_parameter_sample.py
D backend/app/equipment/crud/async_temperature_sample.py
D backend/app/equipment/crud/sync_drive.py
D backend/app/equipment/crud/sync_integration.py
D backend/app/equipment/crud/sync_production_parameters.py
D backend/app/equipment/crud/sync_temperature.py
D backend/app/equipment/error_codes.py
D backend/app/equipment/integration_config.py
D backend/app/equipment/integration_domain.py
D backend/app/equipment/integration_error_codes.py
D backend/app/equipment/integration_storage.py
D backend/app/equipment/manifest.py
D backend/app/equipment/mapping_config.py
D backend/app/equipment/mapping_domain.py
D backend/app/equipment/mapping_error_codes.py
D backend/app/equipment/mocks/__init__.py
D backend/app/equipment/models/__init__.py
D backend/app/equipment/models/equipment.py
D backend/app/equipment/models/integration.py
D backend/app/equipment/models/mapping_ingest.py
D backend/app/equipment/models/temperature_sample.py
D backend/app/equipment/schemas/__init__.py
D backend/app/equipment/schemas/drive_sample_in.py
D backend/app/equipment/schemas/equipment_query.py
D backend/app/equipment/schemas/integration.py
D backend/app/equipment/schemas/mapping_sample_query.py
D backend/app/equipment/schemas/production_parameter_sample_in.py
D backend/app/equipment/schemas/temperature_sample_in.py
D backend/app/equipment/schemas/temperature_sample_out.py
D backend/app/equipment/schemas/temperature_sample_query.py
D backend/app/equipment/seed.py
D backend/app/equipment/seeds/__init__.py
D backend/app/equipment/services/__init__.py
D backend/app/equipment/services/_sync_common.py
D backend/app/equipment/services/async_drive_sample.py
D backend/app/equipment/services/async_equipment.py
D backend/app/equipment/services/async_integration.py
D backend/app/equipment/services/async_production_parameter_sample.py
D backend/app/equipment/services/async_temperature_dashboard.py
D backend/app/equipment/services/async_temperature_sample.py
D backend/app/equipment/services/sync_drive.py
D backend/app/equipment/services/sync_production_parameters.py
D backend/app/equipment/services/sync_temperature.py
D backend/app/equipment/temperature_sample_domain.py
M backend/app/equipment_observation/README.md
M backend/app/equipment_observation/README.zh-CN.md
M backend/app/equipment_observation/api/routes.py
M backend/app/equipment_observation/models/records.py
M backend/app/equipment_observation/profile.py
M backend/app/equipment_observation/schemas.py
D backend/app/equipment_observation/services/ingest.py
M backend/app/equipment_observation/services/ingest_v2.py
M backend/app/module_contract.py
M backend/app/monitor/README.md
M backend/app/monitor/README.zh-CN.md
D backend/app/monitor/__init__.py
D backend/app/monitor/api/__init__.py
D backend/app/monitor/api/collector.py
D backend/app/monitor/api/energy.py
D backend/app/monitor/api/integration.py
D backend/app/monitor/api/mapping_http.py
D backend/app/monitor/api/process_curve_samples.py
D backend/app/monitor/api/routes.py
D backend/app/monitor/api/temperature.py
D backend/app/monitor/crud/__init__.py
D backend/app/monitor/crud/async_collector.py
D backend/app/monitor/crud/async_energy.py
D backend/app/monitor/crud/async_integration.py
D backend/app/monitor/crud/async_mapping_ingest.py
D backend/app/monitor/crud/async_process_curve_sample.py
D backend/app/monitor/crud/async_temperature.py
D backend/app/monitor/crud/sync_integration.py
D backend/app/monitor/crud/sync_process_curve.py
D backend/app/monitor/integration_config.py
D backend/app/monitor/integration_domain.py
D backend/app/monitor/integration_error_codes.py
D backend/app/monitor/integration_storage.py
D backend/app/monitor/manifest.py
D backend/app/monitor/mapping_config.py
D backend/app/monitor/mapping_domain.py
D backend/app/monitor/mapping_error_codes.py
D backend/app/monitor/mocks/__init__.py
D backend/app/monitor/models/__init__.py
D backend/app/monitor/models/business_history.py
D backend/app/monitor/models/integration.py
D backend/app/monitor/models/mapping_ingest.py
D backend/app/monitor/models/monitor.py
D backend/app/monitor/schemas/__init__.py
D backend/app/monitor/schemas/collector.py
D backend/app/monitor/schemas/energy.py
D backend/app/monitor/schemas/integration.py
D backend/app/monitor/schemas/process_curve_in.py
D backend/app/monitor/schemas/process_curve_query.py
D backend/app/monitor/schemas/temperature.py
D backend/app/monitor/seeds/__init__.py
D backend/app/monitor/services/__init__.py
D backend/app/monitor/services/_shared.py
D backend/app/monitor/services/async_energy.py
D backend/app/monitor/services/async_integration.py
D backend/app/monitor/services/async_process_curve_sample.py
D backend/app/monitor/services/async_temperature.py
D backend/app/monitor/services/collector/__init__.py
D backend/app/monitor/services/collector/async_query.py
D backend/app/monitor/services/sync_process_curve.py
M backend/app/plc_facts/v2_config.py
M backend/common/integration/storage.py
M backend/scripts/business_time_adoption/README.md
M backend/scripts/business_time_adoption/README.zh-CN.md
M backend/scripts/business_time_adoption/main.py
D backend/tests/app/monitor/test_collector.py
A backend/tests/historical_observation/README.md
A backend/tests/historical_observation/test_business_integration_service.py.txt
A backend/tests/historical_observation/test_mapping_api.py.txt
A backend/tests/historical_observation/test_mapping_service.py.txt
M backend/tests/test_business_integration_api.py
M backend/tests/test_business_integration_contract.py
M backend/tests/test_business_integration_migration.py
M backend/tests/test_business_integration_provider.py
D backend/tests/test_business_integration_service.py
M backend/tests/test_business_integration_storage.py
M backend/tests/test_business_module_migration.py
M backend/tests/test_business_module_permissions.py
M backend/tests/test_business_module_reintegration.py
M backend/tests/test_business_time_adoption.py
M backend/tests/test_core_migration_baseline.py
M backend/tests/test_energy_price_migration.py
M backend/tests/test_equipment_mapping.py
M backend/tests/test_equipment_observation_domain.py
M backend/tests/test_equipment_observation_r10.py
M backend/tests/test_equipment_observation_r10_flow.py
M backend/tests/test_equipment_observation_r8.py
D backend/tests/test_equipment_temperature_api.py
D backend/tests/test_equipment_temperature_config.py
M backend/tests/test_equipment_temperature_migration.py
D backend/tests/test_equipment_temperature_service.py
M backend/tests/test_generic_task_migration_r3.py
M backend/tests/test_generic_task_revision_guards.py
M backend/tests/test_legacy_acquisition_retirement.py
D backend/tests/test_mapping_api.py
M backend/tests/test_mapping_compatibility.py
M backend/tests/test_mapping_migration.py
D backend/tests/test_mapping_service.py
M backend/tests/test_module_registry.py
M backend/tests/test_module_structure.py
D backend/tests/test_monitor_business.py
D backend/tests/test_monitor_mapping.py
A backend/tests/test_observation_retirement.py
M backend/tests/test_openapi_router_tags.py
M backend/tests/test_role_api_permission_startup.py
M contracts/PLAN.md
M contracts/PLAN.zh-CN.md
M contracts/README.md
M contracts/README.zh-CN.md
M contracts/published/http-api/equipment-observation-v2/README.md
M contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
M docs/equipment-status-process-monitoring-guide.md
M docs/equipment-status-process-monitoring-guide.zh-CN.md
M docs/equipment-status-process-monitoring.md
M docs/equipment-status-process-monitoring.zh-CN.md
M frontend-js/README.md
M frontend-js/README.zh-CN.md
M frontend-js/src/app/dashboard/views/home/index.vue
D frontend-js/src/app/equipment/api/index.js
D frontend-js/src/app/equipment/api/mapping-source.test.mjs
D frontend-js/src/app/equipment/api/mock.js
M frontend-js/src/app/equipment/locales/en-US.json
M frontend-js/src/app/equipment/locales/zh-CN.json
D frontend-js/src/app/equipment/views/drive/index.vue
D frontend-js/src/app/equipment/views/production-parameters/index.vue
D frontend-js/src/app/equipment/views/temperature/index.vue
D frontend-js/src/app/monitor/api/index.js
D frontend-js/src/app/monitor/api/mapping-source.test.mjs
D frontend-js/src/app/monitor/api/mock.js
D frontend-js/src/app/monitor/components/EnergyTrendChart.vue
D frontend-js/src/app/monitor/components/QualityCurve.vue
D frontend-js/src/app/monitor/components/SpeedCurve.vue
D frontend-js/src/app/monitor/components/TemperatureCurve.vue
D frontend-js/src/app/monitor/components/TensionCurve.vue
D frontend-js/src/app/monitor/components/hmi/CoilerTensionPanel.vue
D frontend-js/src/app/monitor/components/hmi/HeatingZoneGrid.vue
D frontend-js/src/app/monitor/components/hmi/HmiLineOverview.vue
D frontend-js/src/app/monitor/components/hmi/HmiStateCell.vue
D frontend-js/src/app/monitor/components/hmi/HmiValueCell.vue
D frontend-js/src/app/monitor/components/hmi/MotorStatusMatrix.vue
D frontend-js/src/app/monitor/components/hmi/PositionControlMatrix.vue
D frontend-js/src/app/monitor/components/hmi/hmiConfig.js
D frontend-js/src/app/monitor/components/hmi/hmiUtils.js
M frontend-js/src/app/monitor/locales/en-US.json
M frontend-js/src/app/monitor/locales/zh-CN.json
M frontend-js/src/app/monitor/manifest.js
D frontend-js/src/app/monitor/views/energy/index.vue
M frontend-js/src/app/monitor/views/observations/energy.vue
D frontend-js/src/app/monitor/views/realtime/index.vue
D frontend-js/src/app/monitor/views/temperature/index.vue
M frontend-js/tests/module-registry/page-access.test.mjs
M frontend-js/tests/module-registry/registry.test.mjs
```

</details>

## QA1 后返工与 Developer handoff

按获批 r1 第 5.2、6 节完成首轮返工。独立 QA1 的 [checklist](checklist.md) SHA-256 cb8478cce554937114444afdd1cb68e1c9203b595b498c6fd454b5b26443f374，首次 handoff 的 tasks SHA-256 7707cd063e51b585e9c1f8f8799f7562679dd0eab21142e50647373f97874533。旧候选及证据保留原字节供追溯；新核验对象是 /private/tmp/arch-obs-002-r1-3y1wnavr/candidate-rework1。

返工相对 QA1 候选仅修改 backend/alembic/versions/20261118_1645_c9e1a3b5d720_retire_legacy_observation.py。该文件 SHA-256 从 fdde8af29e5bbc620d133787e7585ef76fd902b7ee3cd9d89fc00c17a7b84ada 更新为 6535e9829f7fc6a48f5d1c0575ab25adad5185280e91ba4d4bfbf1fdd1bc0cbd。r1 规格、历史迁移、已发布合同、QA checklist、业务 Service 与本轮前端字节保持原样。

- 先核对版本、目标、已知 outcome、ID 和现行回执 detail（仅 stored/skipped 两组数组），再在有界的同连接表锁内检查三个现行目标及其所属回执。latest 的 stored、stale、already_stored 均指向存在的同一目标表行，允许多个合法历史回执共享快照 ID。当前快照回指实际拥有的 stored 回执。history/stored 和 energy/stored 需正反引用一致。history/no_history_metrics 只合法于 NULL，并禁止当前样本回指它。
- 继续沿用既有受控检查、单条多表 DROP 和回执默认值更新。新增查询表只做校验和加锁，旧表范围仍为 18，未知关系会在 DDL 前拒绝。既有 latest 回执未单列设备／任务，校验以数据库可证明的行身份及当前所属关系为限。维护窗口仍需由操作方确认外部写入方静默和元数据权限完整。

### 返工自检

| 自检 | 实际命令与结果 |
| --- | --- |
| 精确目标和正例 | 在任务容器 127.0.0.1:13318 新建合成 schema obs002_rework1，复核原容器完整 ID、镜像和端口。候选 backend 中执行 setup-rework1.sh，项目 Python 调用 Alembic -x obs_r10_writers_quiesced=yes upgrade ae20b4d6f831 成功。执行 run-rework1.sh http_rework1 before，真实 ASGI、MySQL、bcrypt 登录/JWT、机器 Bearer 生成 9 个合法回执，包含 latest 两次存储覆盖、stale 和 already_stored 共享一个 ID、history/stored 与合法 NULL、energy/stored。夹具只有构造前驱数据时临时允许观察 profile 接受该前驱版本，原代码和实际 DB 目标探针仍使用各自精确版本。 |
| QA1 精确负例 | run-rework1.sh migration_rework1 用实际 Alembic CLI 复现 QA1 的 energy/stored + 999999，返回非零并明确 unknown observation receipt result for energy。断言前驱、18 张表、回执默认值及所有保护行和结构与迁移前一致。另实测 energy NULL/0、history 和 latest 缺 ID、错误大小写/未知 outcome 或 target、no_history_metrics 有 ID、history 跨表数值撞号、energy 存在 ID 但反向所有权不同、快照错误反向归属、显式旧归档位置、v1／未知版本。各有针对性的拒绝检查与数据对账。 |
| 并发、恢复与中断 | 同一 runner 实测缺窗口、UUID／schema／版本不符、归档非空、依赖 FK／视图及缺表。并发旧记录 INSERT 在最终查空后等待真实锁，DROP 后报 1146。并发 UPDATE 能耗样本在 atomic DROP 后仍被锁挡住，只有 UNLOCK 后完成并由夹具回滚。在真实 DROP 后模拟结果未知、自动重试被拒，读取记录仍为前驱；精确重建 18 张空表后正式升级一次成功。 |
| 非空对象保全 | rework1 的 56 张受保护表逐项比对 DDL 与所有行，排除 AUTO_INCREMENT 水位，两个预期回执默认值单独核对。SHA-256 c2ae513fd12815b0d42d21281875b0482e1d501c7c5cb49e0a7b0d2e8d9fd31a。含非空回执 9、实时 1、过程 3、能耗 1、能源单价和小时价各 1、PLC 来源和最新／历史各 1、计划和实绩各 1、真实合成登录账号 4。价格、采集和任务样本用于持久化对账，由夹具 SQL 合成。 |
| 升级后当前读取 | run-rework1.sh http_rework1 after 成功；真实 MySQL 和原生 profile 通过观察／Facts 新 head 探针，用真实登录 JWT 覆盖 admin/supervisor/operator/未授权账号和匿名，能耗汇总与迁移前同为 5 kWh。结束显式 dispose AsyncEngine。 |
| 候选快速回归 | Python compileall、Alembic heads、app.module_preflight --check-only 均成功。pytest -p no:cacheprovider -m no_db -q --tb=short tests/test_observation_retirement.py tests/test_equipment_observation_r10*.py tests/test_generic_task_revision_guards.py tests/test_business_time_adoption.py 为 59 passed，1 个原 SQLite datetime adapter 弃用提示。前端模块装配 25 路由／9 组、90/90、Vite 生产 build 成功，保留旧大 chunk 提示。 |
| 历史测试边界 | 返工未再次执行整套 634／5 测试。本记录上方单列了上版候选及不可变 f7c5608 的 5 项同样失败；frontend 与老历史档案未改。没有把使用公开后备夹具 bcafa89 的三项历史失败视为 QA3 原件复跑结果。 |

新的 candidate-rework1-manifest.tsv SHA-256 080b31c5f7516e74162ad94a76cc0490c55bcee92acf43f473da06b97e308123，原 preimage.sha256 不变。相对正式树路径仍为 A6／M75／D144，详见上方逐文件表和新清单；旧候选 manifest 仍为 6c28642daea8688c19e1c85dbc380d39e5fd840b4488753507a6e6df6ad6dc69。三处正式并行漂移仍为 CODE_INDEX.md、frontend-js/tests/module-registry/page-access.test.mjs、frontend-js/tests/module-registry/registry.test.mjs，按真实前驱做按行合并。candidate-rework1-nondrift.unified.diff SHA-256 0e3bdeba46061e16184d52e3e71e2de6e4bca94e8ca572a6502017b2f2307ef7，排除三处，git apply --check --whitespace=error 只读通过。原切换边界仍适用。正式树及真实 3307 / 配置 / 用户服务未操作。

关键证据在任务临时目录。migration-rework1.log SHA-256 a4da94026b8881d71054061a22b05cb1682314c9e54d8caae251f87cf0633bf7，fixture-restoration-rework1-ddl.json SHA-256 df5874d3093b1a345059371c3fef77d94c390e62ac287d06d66c70461396c836。http-rework1-before.log、http-rework1-after.log、pytest-rework1.log、frontend-rework1-tests.log、frontend-rework1-build.log 及同目录脚本供 fresh-context Verification 复建。复验角色使用自己已批准的目标及账户；不直接沿用 Development 连接配置。临时资源由协调者核对归属，证据持久化与复核完成后清理。

浏览器检查在独立 headless Chrome 通过，以既有 Playwright、候选 Vite 生产构建和 ASGI stdio 桥接实际路由，无独立 HTTP listener。命令在候选 backend 中为 node /private/tmp/arch-obs-002-r1-3y1wnavr/browser-rework1.cjs。Browser 夹具在迁移对账完成后才创建四个仅用于浏览器的合成账户。登录表单和真实登录 API、四设备页、三过程曲线页、两边各自配置／记录管理页、独立能耗页均对应实际 HTTP 200。实际菜单点击进入新版能耗，旧直链跳转；具有 monitor.energy 页面授权的 supervisor 可到新版能耗，不能访问管理页。测试构建中的 operator 和无授权角色没有页面授权，跳转登录；不同于现有环境授权。这项检查未使用运行中的用户浏览器，首次夹具等错过程配置 GET，改等 /monitor/curve-configs 后全量 exit 0，日志为 browser-rework1.log 和 browser-rework1-retry.log。

## QA2 后返工与 Developer handoff

按同一获批 r1 范围返工。QA2 结论记录于 [checklist](checklist.md)，SHA-256 a6ff1d0ef5292efdb6ece1af5746ff6d940dc62c950ee4561cbbe42d2ffa6f7c。返工前 tasks SHA-256 6a42cffa621b1a29d3ce8cdba6edb6ed2647163a4954d2c9ffa0a403066afb44。新候选位于 /private/tmp/arch-obs-002-r1-3y1wnavr/candidate-rework2；前两套候选、清单、日志和 DDL 保留。新候选从前序清单核对复制 1,354 个源码文件并重建前端依赖符号链接，复制时没有进入依赖目录。

相对 QA2 候选，唯一源码变化仍在 backend/alembic/versions/20261118_1645_c9e1a3b5d720_retire_legacy_observation.py。迁移 SHA-256 从 6535e9829f7fc6a48f5d1c0575ab25adad5185280e91ba4d4bfbf1fdd1bc0cbd 更新为 84c5ea03870eb3d39109d557e3bd2f1673a8520e14ea09db470f787dbccc7623。升级仍为 ae20b4d6f831 至 c9e1a3b5d720。实际 v2 writer、表锁范围、双向引用、18 个 DDL 目标与禁止自动恢复条件均沿用。获批 spec 和独立 checklist 未写。

- MySQL 8.4 的 JSON_SCHEMA_VALID 在同一受保护连接校验各 target 的明细。顶层仅 stored／skipped。设备 stored 的元素只允许 groupKey 和非空字符串 metricKeys 列表；skipped 的元素只允许 groupKey、metricKey、与目标一致的 latest_disabled 或 history_disabled。设备常规 stored 和 latest/already_stored 继续允许空列表；latest/stale、history/no_history_metrics 的 stored 必须为空，仍可有合法 skipped。energy/stored 要求非空的指标键字符串列表与空 skipped。
- 特定字段名（如 resultLocation、resultRecordId）若出现在不属于现行结构的位置，迁移拒绝。业务标识支持 Unicode，与历史表恰好同名的合法字段值不作为引用识别。守卫核验可证明的写入结构、结果及相互引用，未从历史回执摘要推定设备、任务或持久状态之外的语义。

### 返工2 自检

| 核验 | 实际命令与结果 |
| --- | --- |
| 目标和正例 | setup-rework2.sh 重核开发容器、固定镜像和 127.0.0.1:13318 绑定，创建新合成库 obs002_rework2，经项目 Alembic 升至 ae20b4d6f831。run-rework2.sh http_rework2 before 使用真实 ASGI、SQL、登录/JWT 和机器 Bearer 生成 13 个合法 v2 回执，覆盖三个目标及全部 outcome，含 64 个 Unicode 码点（含补充平面字符）的指标键、与旧过程归档同名的业务分组、旧实时共享结果 ID、stale 和 no_history_metrics 两种有／无 skipped、缺测的 already_stored、无存储指标但历史落行的缺测／跳过、正常表计。生成前驱 fixture 仅暂时允许对应观察 profile 版本，数据库探针仍实际校验精确目标。 |
| 两轮精确反例及矩阵 | run-rework2.sh migration_rework2 用真实项目 Alembic CLI 分别运行 QA1 的 energy/stored/999999 和 QA2 的 history/no_history_metrics/NULL 带嵌套归档标识，均 exit 1。比较失败前后的全库表集、DDL（含默认值）、所有行及前驱登记，保持一致。另验证回执版本／target／outcome／ID、错误正反向身份、跨表撞号和归档字段。26 个结构细项分别覆盖 stale／无历史指标冒充存储、两个设备目标的 stored／skipped 嵌套归档字段、错误及大小写不符的 reason、缺键、错误元素类型、重复／空／过长键，和能耗空存储、非空跳过、对象／数值／NULL／重复元素、SQL NULL 明细等。每项实际拒绝且逐表比对一致。首次 runner 在任何写入及升级前因两个合法无历史回执选择条件过宽退出，限定事件号后完整复跑成功，首次输出保留。 |
| 锁及恢复 | 新实测独立连接持有能耗表 READ 锁阻挡迁移，等待 5.01 秒后 MySQL 1205，原 session timeout 恢复、全部表和数据保持。正向演练中，空检查后竞争旧表 INSERT 等待，真正 DROP 后收到 1146；受保护能耗写者在 DROP 后仍阻塞，UNLOCK 后才可 UPDATE 并测试回滚。真实 DROP 后模拟结果未知，仍为前驱，拒绝盲目再次执行。按记录逆序重建 18 张空表并比对，最后真实 Alembic 升级成功。原旧表非空、FK／视图依赖、缺表、维护窗口、目标／前驱核验一并经过 MySQL。 |
| 非空数据保全 | 去除的表集仍为精确 18，56 张保护表逐项比较完整结构和全行（排除自增水位，单独允许两个回执默认值变化）。SHA-256 09c7550f9f6783cd436fbef8342feaacfeba03425c72476b24dadca808b58e83。13 回执、实时 1、过程 4、独立表计 1、单价／小时价、采集三个表、计划／实绩和四账号均非空。归档同名键和 Unicode 键随合法回执保留。未进行生产量级性能验证。 |
| 升级后读回 | run-rework2.sh http_rework2 after，exit 0。实际登录 JWT、既有角色／数据范围、观察与 Facts profile 正式新 head 探针、能耗汇总 5 kWh 与迁移前一致。 |
| 其余回归 | 候选 backend 的 compileall、Alembic heads（唯一 head）、app.module_preflight --check-only 通过。此前同一组选定 pytest -p no:cacheprovider -m no_db 的四组验证再次为 59 passed，含原 SQLite datetime 弃用提示。候选前端 25 路由／9 组、90/90 及合成授权 Vite 生产构建通过，保留原 chunk 大小提示。浏览器与完整 no_db 仍引用前序运行及载明的五项原基线错误，本次未重跑这两项。 |

candidate-rework2-manifest.tsv SHA-256 f724db65478afc1af28ef141715137d4e4d344787ffad0fe11b1ee8c84adb10f，共 225 项 A6／M75／D144。起始 preimage.sha256 和原相对路径表保持。三重叠文件仍为 CODE_INDEX.md、frontend-js/tests/module-registry/page-access.test.mjs 和 frontend-js/tests/module-registry/registry.test.mjs。其他工作又修改了候选范围外的 backend/app/task/services/async_fields.py，前序另列的并行路径仍保留正式原字节。排除三个重叠文件的 candidate-rework2-nondrift.unified.diff SHA-256 dd621eba5f66498eb8dad7a8f01bd579827450ac54ffc4237274ae78ffa40833，git apply --check --whitespace=error 只读通过；真正整合前仍逐项复核并语义合并三个文件。

证据 migration-rework2.log SHA-256 2f5df3047f4caea2b32ad4ed817fc6784d5c9a144b381f84927561396df8079a，fixture-restoration-rework2-ddl.json SHA-256 df5874d3093b1a345059371c3fef77d94c390e62ac287d06d66c70461396c836。另留 http-rework2-before.log、http-rework2-after.log、pytest-rework2.log、frontend-rework2-tests.log、frontend-rework2-build.log、setup-rework2.log。驱动与验证脚本在同一任务私有目录。fresh-context Verification 使用其已批准并单独核对的 QA 资源。正式工作树未整合，真实 3307、真实配置和用户服务未操作。任务自有容器与临时目录请协调者在 QA、证据固化及归属核对后清理。

## QA3 后返工与 Developer handoff

按已批准 r1 回执未知身份守卫返工。[QA3 checklist](checklist.md) SHA-256 6b4d9cf23d0dcf254ba402978c4b883345de4023377255d327742066e5d54a7a，前次 tasks SHA-256 bf50fd74973a29c12f4e540f3f3fa5b15e8048731cc52697c9a2a33262b8b556。在 /private/tmp/arch-obs-002-r1-3y1wnavr/candidate-rework3 按清单复制 1,354 个源文件，单独重建前端依赖链接。前三版候选和清单保留原样。

| 相对 QA3 候选的两个源码变化 | 返工前 SHA-256 | 返工后 SHA-256 |
| --- | --- | --- |
| backend/alembic/versions/20261118_1645_c9e1a3b5d720_retire_legacy_observation.py | 84c5ea03870eb3d39109d557e3bd2f1673a8520e14ea09db470f787dbccc7623 | 224733b68dbc9deb9e4c8ddc76c0a98315bb55d63b6282c1e543533f13a76bee |
| backend/tests/test_observation_retirement.py | 8f75c66eaadd42765721d9c410cbf0102139c71e696208c402087caa0f3e6029 | 479c2f042b5bae990c21795ee85a70bd3805677ce3071b1d8bfb78e8f31e3297 |

延续既有结构、双向引用和表锁，在同一连接按回执主键流式读取每页最多 64 行，客户端缓冲一行，页结果关闭后才发下一条 SQL。冻结规则按现行 writer 校验 Unicode 码点数、首尾空白、C* 分类及严格 UTF-8；覆盖设备／表计明细的全部键及 producer、event、成对 mapping，长度上限分别为 64／128／64／32，错误不显示行内容。允许合法内部空格、普通中英文、补充平面字符、emoji 变体和恰好与历史表同名的键。

v2 task_evidence 仅接受 JSON null 或等价 SQL NULL。sourceRefs 接受缺失的两种等价 null 或现行 writer 所允许的 0–128 项对象数组，每项 kind 必须为 1–128 码点的字符串，其它字段保留为调用者声明，不用于推定血缘、结果位置或当前 profile 授权。

| 核验 | 命令和实测结果 |
| --- | --- |
| 合成目标和正例 | setup-rework3.sh 核对 Development 容器完整 ID、固定镜像、单一 13318 绑定，建立 obs002_rework3 至 ae20b4d6f831。run-rework3.sh http_rework3 before／after 均 exit 0。实际 ASGI／MySQL／机器 Bearer／登录 JWT 生成 154 个回执，覆盖三个目标所有 outcome、64 Unicode 码点含非 BMP 字符、内部空格、合法 emoji 变体、旧表同名分组、Unicode producer、128 码点 event、成对 mapping 和 32 码点 revision。真实 writer 生成缺失 sourceRefs 的 JSON null、显式空数组、非空数组及含同名表和 ID 的 opaque 字段，另构造无证据的等价 SQL NULL，均保留。升级后实际角色及新 head 探针通过，能耗仍为 5 kWh。 |
| 守卫反例 | run-rework3.sh migration_rework3 完整 exit 0。按项目 Alembic CLI 拒绝 QA1、QA2、QA3 共四条精确输入，前驱、18 表、默认与保护数据不变。再按实际 MySQL 验证 26 个结构细项、81 个三目标／九明细字段 Unicode 和长度组合（首尾 Unicode 空白，Cc/Cf/Co/Cn、非法 ZWJ、65 码点）、伪造 producer/event/mapping、半对、旧任务证据、错误 sourceRefs 与原结果关联等。MySQL 拒绝 lone surrogate；额外 SELECT 强制转换非法原始 UTF-8 时报告 1300 并返回 SQL NULL，未持久化原坏字节；离线直接注入 malformed bytes 亦明确拒绝且关闭结果。两次对 SELECT 转码的夹具假设失败均早于 DDL，保留原日志。 |
| 分页、并发与恢复 | 第三页注入真实异常回执，确认查询按主键 64 一页及驱动使用 SSCursor；异常后同一会话可查询、原 timeout 恢复、另一连接取实际保护行锁，全库快照未变。另实测锁竞争 5.01 秒返回 1205 并恢复 timeout。最终查空后旧表 INSERT 等待并在 DROP 后报 1146，能耗 UPDATE 在 DROP 后仍阻塞至 UNLOCK，实际执行并回滚。DROP 完成后模拟失败，旧 revision 留在，拒绝盲重试；用记录 DDL 逆序重建 18 张空表后正式 Alembic 升级。 |
| 正向对账 | 精确退出 18 张旧表。56 张保护表对比全行与 DDL，排除自增计数、确认两个预期回执默认变化。含非空 154 回执、快照、历史、表计、单价与小时价、采集三表、计划实绩和账号。摘要 cca60345f4de3713423d9628655c467f884d2bce09891cbfd26ebd01972c9631。 |
| 环境和回归 | 用同一项目解释器 Python 3.13.3/UCD 15.1.0 比较 writer 和迁移。冻结算法使用运行时 Unicode 库。不同解释器的 UCD 版本可能导致新赋值码点分类差异，未执行跨版本或生产规模测试。Python 编译、唯一 head、模块 preflight 通过。定向后端 77 passed，原 SQLite datetime 弃用提示。前端装配 25 路由／9 组、90/90、合成授权 Vite 构建通过，旧大 chunk 提示。浏览器和后端整套 no_db 沿用前序证据；五项既有基线失败按上文记录。 |

返工清单 candidate-rework3-manifest.tsv SHA-256 893e2378f5b91c44779b190aada69fab073fab51609b8b882fb56efc9f302d07，仍为 225 项 A6／M75／D144。原 preimage.sha256 和路径表保持。排除三份正式漂移文件（CODE_INDEX.md、frontend-js/tests/module-registry/page-access.test.mjs 和 registry.test.mjs）的 candidate-rework3-nondrift.unified.diff SHA-256 128698f4641dc7345905821a6515da1def7636b4088898ceab4f9f252ddfaae5，只读 git apply --check --whitespace=error 通过。正式整合须协调者重新核对当前 preimages 与并行任务语义。

证据 migration-rework3.log SHA-256 0c5d9500fe61b900dd22a543d2b120b9fae6c503f70589501a85986c56bd3b95，fixture-restoration-rework3-ddl.json SHA-256 df5874d3093b1a345059371c3fef77d94c390e62ac287d06d66c70461396c836。前后 HTTP、定向、编译、构建和复现脚本在同一任务临时目录。独立 Verification 使用其单独批准和核对的隔离资源；协调者在证据固化和核对归属后统一收尾。正式工作树未整合，真实 3307、真实配置和用户服务未操作。规格和 checklist 未修改。

## QA4 后返工与整合预览交接

按已批准 r1 处理 QA4 的历史样本双向错指。[QA4 checklist](checklist.md) SHA-256 2e036e6468fd3c1907fdf39e618183f0b3c71e57eb4a50e205ffb94bba31fa0c，前三次返工记录的最后 tasks SHA-256 为 6528f0a9be5533523fefc6fe60b565155db1f2878065f8a14504816f29ce5130。QA4 的原始复现、独立结论和资源记录保留在 checklist 中。

### 整合预览与并行保全

以当前正式树的公开源码和必要未提交前驱制作 /private/tmp/arch-obs-002-r1-3y1wnavr/integration-preview。在 225 项清退路径中，仅 CODE_INDEX.md、frontend-js/tests/module-registry/page-access.test.mjs、frontend-js/tests/module-registry/registry.test.mjs 的正式 preimage 有漂移。以语义合并保留最新 ARCH-TASK-001 两个 shared-fields 路由断言和三个最新代码索引条目，并应用唯一能耗当前路由的断言。三文件对上一候选的实际差异在 integration-preview-relative-to-candidate.diff，SHA-256 4a2e4364e9b95f6a890fc34349bb97fbd8ef684b864b24f1a05d700b0b783372。

正式来源的 1,495 路径 preimage 清单 integration-preview-current-source.sha256 为 c94e03287e4a00b758246f02d42be4c4bcc9ddffe88e4844569a9de5e2abd3f7，预览组合清单 integration-preview-manifest.tsv 为 a0485438703abac22c51f72fd3782701467a65bd6f470ec9aaca5fa9236673e2。整合预览 diff 为 5e4d8346b568ae5cd3be0c4c42aebd3260fe35d4d03e9908c88a931d36d5acf8，git apply --check --whitespace=error 只读通过。非清退目标的 22 处当前正式并行代码、测试及治理文档按字节保留，候选对照清单 integration-preview-preserved-parallel.tsv SHA-256 bbe6bc1b7ee8cb7d28f48f8c106a6922220fe0aeec2d3f93743ae91044fc4a55。其中含新 TaskFieldEditor、页头适配和 shared-fields 页面、领域和配置 service、任务 flow test 以及计划／实绩双语。包含未提交 ae20b4d6f831 前驱。未复制真实配置、数据库、依赖目录或产物；仅在临时副本重建指向已有锁定前端依赖的符号链接。

ARCH-TASK-001 的历史证据 backend/tests/test_mapping_api.py 在清退后的精确源码保存路径为 backend/tests/historical_observation/test_mapping_api.py.txt，SHA-256 434b6c18007da5d2b1d4c19c2a870f4fb470600d1e34fad9237052a730061072。与正式旧路径实读字节及 ARCH-TASK-001 已记录指纹一致。该源码和成对旧测试使用归档 README 所载的固定 f7c5608 源复现；对方任务记录未改写。

该预览单独完成后端计划／实绩、观察、鉴权、采集版本守卫与 OpenAPI 同组定向 246 passed、9 skipped，前端 92/92、27 路由／9 组、生产构建及授权检查均成功。整合预览阶段未执行 MySQL 迁移。

### 返工4 候选与自检

从冻结整合预览逐字节核对并复制 1,357 个公开源码到 /private/tmp/arch-obs-002-r1-3y1wnavr/candidate-rework4。仅下表两个文件与预览有字节差异，前四套候选与预览、其指纹及前序 QA 证据保持。

| 文件 | 预览 SHA-256 | 返工后 SHA-256 |
| --- | --- | --- |
| backend/alembic/versions/20261118_1645_c9e1a3b5d720_retire_legacy_observation.py | 224733b68dbc9deb9e4c8ddc76c0a98315bb55d63b6282c1e543533f13a76bee | db65a407492bdd7b68345ff76df45646dc5dd03b6347c30e923aa47354f10898 |
| backend/tests/test_observation_retirement.py | 479c2f042b5bae990c21795ee85a70bd3805677ce3071b1d8bfb78e8f31e3297 | 3ad143d617340f124d2bbef966abc9aa8f4fdf187b4ffea3772e930860e92f8d |

迁移复用同连接、同一批次 64 行的 SSCursor 读取，以回执结果主键及源表反向外键匹配该结果的 stored owning receipt，验证其持久 source_sample_key 等于严格 UTF-8 紧凑 JSON 字符串数组 [producerId,eventId] 的 SHA-256。固定当期 writer 的 canonical_bytes 字符串数组编码语义。正反向 ID 检查和其它守卫沿用。实时快照只校验当前 owner 的身份，合法旧 stored、stale 和 already_stored 可共享结果 ID。能耗表无 source_sample_key，仅沿用已有真实关联检查，不从历史 profile 推断字段。

| 核验 | 实际命令与结果 |
| --- | --- |
| 实际测试目标 | setup-rework4.sh 在已批准 Dev 容器重新侦测完整 ID／本地固定镜像／13318，绑定实际 MySQL 8.4.6 和 UUID，创建 obs002_rework4，经正式 Alembic 到前驱。run-rework4.sh http_rework4 before 的真实 ASGI、登录 JWT、机器 Bearer 和实际 MySQL 产生 156 个回执，含两个实时 owned snapshots、历史 first/late、稳定所有关系和电表。真实源键涵盖 Unicode、内部空格、双引号、反斜杠、emoji 变体；已有合法回执的所有结果分支、Unicode/长度和来源声明语义保留。run-rework4.sh http_rework4 after 用真实登录与当前 scope 再核预期权限，能耗仍 5 kWh。前后脚本 exit 0。 |
| 精确 QA4 和其它来源负例 | run-rework4.sh migration_rework4，exit 0。QA4 两个历史事件 first/late 的实际 key 逐个与 QA4 固定值相同；同事务换绑回执结果 ID 和样本 ingest_receipt_id，SQL 验证双向一致后用真实 Alembic CLI 仍拒绝，未动前驱、旧表、回执默认值或全库行/结构。另验证两个当前最新快照互换拒绝；同样通过词法但伪造的 producer/event 拒绝；带引号和反斜杠的有效历史回执位于第三页，是本夹具的最后一个历史结果；在前驱库篡改其样本 key，迁移持锁检查仍在 DDL 前失败。正例与既有 writer 做源码／实测 SHA256 比对，三个新离线精确回归也验证序列化。 |
| 既有负例与并发恢复 | 同脚本复跑 QA1–QA3 的四条精确反例、结构/Unicode/来源/版本/身份/FK/视图/非空/目标前置。实际窗口冲突 5.01 秒，原 session timeout 恢复；验证第三页错误后的结果集关闭、保护锁释放及快照一致。竞争旧表 INSERT 阻塞后收到 1146，保护能耗 UPDATE 在 DROP 后仍等待，解锁后执行并回滚。真实 DROP 后注入结果未知，仍登记前驱，再跑被拒。18 空表按记录 DDL 恢复后执行正式迁移。 |
| 非空全表对账 | 精确退出 18，56 张保护表比较全行和结构／约束，仅排除自增计数、确认两个预期回执默认变化。含 156 回执、2 实时快照、5 过程样本、独立能耗、非空能源价／小时价、采集三表、计划实绩和账号。保护摘要 367e5d01c405fbc45ade6f410229abc5a0758315594937365a6b50dad088f68c。 |
| 最新组合回归 | Python compileall、Alembic heads 唯一 c9e1a3b5d720、应用模块 preflight 成功。在 127.0.0.1:1 合成配置与既有公开历史夹具用 pytest -m no_db -p no:cacheprovider 验证 tests/test_generic_task*.py、test_observation_retirement.py、test_equipment_observation*.py、test_business_time_adoption.py、test_business_integration_storage.py、test_plc_facts_v2.py、test_acquisition_data_browse.py、test_business_module_permissions.py、test_openapi_router_tags.py，249 passed／9 skipped，原 SQLite adapter 弃用提示。前端全模块 92/92、27 路由／9 组、合成权限 checker 和本轮 Vite 构建成功。既有 chunk 提示和首次全量后端的五项原基线失败仍按前文记录，本次未重跑全量。 |

最终 candidate-rework4-manifest.tsv SHA-256 4c897ce32f6a7a92232e1cd2292d7a7e969e4164df4199f1afd32378c2a140b7（225 项 A6／M75／D144，逐路径含当前可应用正式 preimage、候选摘要、原 preimage 与整合预览摘要）。含三个已合并路径的完整 candidate-rework4.unified.diff SHA-256 cd70404c1831f06a7d93e67310b8fe28b26010ed778a653a50701ce615cc9acf，运行 git apply --check --whitespace=error 只读通过。正式 225 路径 preimage 在核对时未相对预览移动；正式项目治理四文件 PLAN 双语和 plans/README 双语后续更新属于本补丁范围外，保留最新正式内容。正式应用前须再复核目标 preimage。

migration-rework4.log SHA-256 9401e25c475f2811def408563eb7c6aaf9706b08dfb1073d165714563e2a8c42；恢复 DDL fixture-restoration-rework4-ddl.json SHA-256 df5874d3093b1a345059371c3fef77d94c390e62ac287d06d66c70461396c836。同一任务私有路径下有测试驱动、合成凭据、HTTP／前端／后端日志以及之前所有候选。Development 在 Python 3.13.3 / UCD 15.1.0 验证；未验证跨 Unicode 版本或生产负载。独立 Verification 使用其已批准、独立复核的 MySQL 库。协调者待证据固化、核对归属后统一清理。正式源码未整合，真实 3307、私有配置、用户服务、QA 容器未操作。规格和历史 checklist 均原样。

本轮整合产物另用独立无头 Chrome 复测，命令为候选 backend 下执行 node /private/tmp/arch-obs-002-r1-3y1wnavr/browser-rework4.cjs，exit 0。真实登录表单经 ASGI stdio 桥接合成 MySQL；计划／实绩两个列表与两个共享字段设置、设备、过程、能耗与管理共 16 个实际页面的相关 GET 为 200。菜单指唯一新版能耗，旧 URL 重定向；合成 supervisor 可读新版能耗且管理拒绝，合成 operator 和 outsider 未授页面，持续重定向。测试用管理员和其他角色账号独立于用户现有账号，且在迁移保护快照取证后创建。Browser 日志 SHA-256 b5335ff63c8c2c57fc4505f8ecf23cafb57bb164970d4292867b0f713c26dd0b。


## 正式 dev 切换与 Developer handoff（2026-11-18，上海时间）

Human Owner 先批准 r1 与隔离验证。QA5 完成后，Owner 另行授权正式 dev 操作，原文为“批准切换，写入方已停。请按你列出的范围继续，服务恢复时告诉我。”针对残留 8000 监听，Owner 另明确说“你帮我停掉”。协调者核对并对正式后端进程发送 SIGINT，确认父子进程退出。Development 接手后重新检查端口和数据库，8000、5190 无监听，3307 维持原 MySQL 服务。协调者确认 ARCH-TASK-001 的验证会话已空闲，QA5 对三个重叠路径的计划／实绩字段、路由断言及代码索引保全适用。

### 正式交付源码与自检

正式 working tree 为本仓当前 `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 加现有未提交源码及本轮切换差异。逐项核对候选和正式 preimage 后，按 `git apply --check --whitespace=error` 和 `git apply --whitespace=error` 应用 [隔离 QA5](checklist.md) 的确切补丁，两条 Git 命令均 exit 0。实际文件列表为本记录上文的候选清退路径及最终 `candidate-rework4-manifest.tsv`，225 项含 A6、M75、D144，最终清单 SHA-256 `4c897ce32f6a7a92232e1cd2292d7a7e969e4164df4199f1afd32378c2a140b7`、补丁 SHA-256 `cd70404c1831f06a7d93e67310b8fe28b26010ed778a653a50701ce615cc9acf`。使用 Git 工作树基线逐项核对了 225 项交付字节与文件模式。集成辅助进程将私有证据的 umask 077 继承到 Git，首次写后校验因 81 个赋为 0600 的源码文件 exit 1。核对正式 preimage 的原始 0644 和候选的 0644 后，仅对摘要匹配的这 81 个源码路径恢复 0644，复核成功。对照 1,276 个清单外源码，只有四个预先确认的治理文件相比候选基线有差异，保留这四个文件在正式树的版本。保全对照摘要 `169ed4f701067b4acd31507a77a408d6a001434dd291aa7699b937547aca1ccc`。正式迁移文件 SHA-256 `db65a407492bdd7b68345ff76df45646dc5dd03b6347c30e923aa47354f10898`。

| 正式自检 | 命令与结果 |
| --- | --- |
| 编译、唯一 head、模块契约 | 使用现有 Python 3.13.3 项目解释器，在 backend 执行 `python -m compileall -q app core database alembic scripts tests run.py main.py`、`python -m alembic heads`、`python -m app.module_preflight --project-root "$PWD" --check-only`，均 exit 0。唯一 head 为 c9e1a3b5d720。首次 preflight 少传 project-root 只打印帮助，已用上述真命令复查。 |
| 后端定向 | 项目环境指向合成 127.0.0.1:1，并关闭 profile 和 mock。执行 `python -m pytest -q -m no_db -p no:cacheprovider --basetemp <任务私有目录>`，用例范围为 `tests/test_generic_task*.py tests/test_observation_retirement.py tests/test_equipment_observation*.py tests/test_business_time_adoption.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_business_module_permissions.py tests/test_openapi_router_tags.py`。首次 exit 1，248 passed、9 skipped，C2 缺历史 fixture。第二次只复跑 C2，用了不包含其依赖的旧材料路径，exit 1。随后用既有公开 `historical-from-fd99922-parent/backend` 和正式只读 Git 上下文复跑 C2，exit 0，1 passed；合计 249 个通过、9 个跳过。SQLite datetime 既有弃用提示仍出现。全量基线五项既有失败沿用历史记录。 |
| 前端 | `pnpm test:modules` 92/92；`pnpm check:modules` 27 路由、9 组；`pnpm check:access --mode development` 以真实有效前端环境通过，supervisor 3、operator 2。生产 checker 和 `pnpm build --outDir <任务私有目录>/dist` 以合成 supervisor `monitor.energy` 与空 operator 权限通过。以上 exit 0，既有 chunk 大小提示保留。首次 checker 重复传入 `--check`，exit 2，按正确命令复跑成功。 |
| 差异与链接 | `git diff --check` 在获批实现范围内 exit 0。冻结补丁反向只读检查使用 `git apply --reverse --check --whitespace=nowarn`，exit 0。严格检查反向恢复的旧源码会遇到 12 行旧有尾随空白。变更 Markdown 的相对文件链接检查 exit 0，未发现失效路径。 |

### 维护窗口和真实目标

- 真实目标固定为 `127.0.0.1:3307 / industrial_level_2_system`，MySQL 8.4.6，UUID SHA-256 前缀 `ac2319a3fdc8`，会话时区为 UTC+08:00。普通 sandbox 的首次探测返回连接 OperationalError。受审只读探针重新按本机端口、全局 `SHOW GRANTS`、进程列表、InnoDB 事务、元数据待锁、旧表、回执守卫和全表保护摘要核对。两次早期辅助命令因模式参数和证据文件名已存在失败，无数据库写入。最终受审只读探针 exit 0，数据库实际前驱 `ae20b4d6f831`，无人连接、无活动事务、无待锁，18 张 InnoDB 旧表逐一查空。
- 已知本机消费者及端口在用户停服窗口重新核查。当前集成代码、配置和并行历史证明沿用隔离验证所核对的边界。正式 settings 选中两个真实私有 profile，旧内容与拟议新内容均被对应的 loader 或 validator 接受。一次辅助预检误用 Facts 历史格式 parser 被纠正。当前 Performance 存储采用配置为 unadopted，无额外精确版本绑定 profile。两份 profile 拥有者和 0600 模式核对，backend .env 为 0644。两角色数组各有一个 `monitor`，当前无 `energy-consumption-read`，实际 backend settings 权限数组与磁盘对应。
- 在原 3307 完整核查全局可见外键与数据库对象。目标相关 FK 列关系为 48 条，涉及旧表的关系与冻结迁移允许图完全一致，所有非系统视图、触发器、例程、事件均为 0。数据库 event scheduler 为 ON，非系统事件为 0。复核依赖后保存 18 表可复建 DDL、精确前驱和回执原默认值。DDL 摘要 `3c76832ae8a7d72a7711cf8664a18cfe7323c6b21ab46e6a0144e138db37a1c4`。
- 单次受审运行 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python /private/tmp/arch-obs-002-r1-dev.vqRvqwhQ/window.py execute-confirmed-dev-cutover`。先复核实际目标、数据库和配置 preimage、有效 settings、相同目录原子替换所需的可写性和两个用户端口停服，再运行正式 backend 的 `python -m alembic upgrade c9e1a3b5d720`。本次仅执行这一条真实升级命令，exit 0。使用显式的环回主机、3307、schema、UUID、维护窗口确认及匹配的迁移账户。未使用 stamp、降级、额外 SQL DDL 或插入业务样本。已获批的迁移持同一连接和有界表锁重核旧表及回执，再做 SQL 操作。
- 升级后只读核对：唯一注册 revision 为 `c9e1a3b5d720`，基表总数 75 → 57，表集之差精确为 §2.1 的 18 张；FK 列关系 48 → 29，只有涉及旧表的列关系退出。全量比对其余 56 张保护表的行数、完整行摘要、表结构、索引和约束，除自增水位及两个经单独验证的回执默认值外均一致。回执默认变为 `aiis.metric-ingest/v2` 和 `r10`，现存回执 0 行。保护数据示例为设备指标分组 1、指标配置 2、能源单价 1、小时价 3、PLC 来源 3、最新 6、历史 107，计数随迁移保持。保护摘要 `3b30265f8c6d31c9f441f40d64ad5f33b80db999a6e2dc9191f8c0af5310e978`。
- 数据库对账通过后，仅改实际采用的设备观察和 PLC Facts 两份私有 JSON 的唯一 `schemaRevision` 字段 `ae20b4d6f831` → `c9e1a3b5d720`，以及 backend .env 的 supervisor/operator 活动数组各删除一个既有 `monitor`。确认三份原有属主、组和模式保持，其余设置、顺序、scope、值均保持。两个真实加载器均加载新版本。前端所有 `.env*` 文件指纹核对相同。命令整体 exit 0。Development 未启动用户服务；完成时 8000、5190 仍停，协调者随后已通知 Human Owner 由其恢复。真实运行时回归等待独立只读核验。

### 证据与未验证边界

任务私有目录 `/private/tmp/arch-obs-002-r1-dev.vqRvqwhQ` 模式为 0700，保存实际命令驱动、权限和私有路径证据、保护对象摘要、旧表恢复 DDL 及对账和编译测试日志。禁止转贴私有内容。迁移日志 SHA-256 `11c543ee80e294c949df98c3810c96208f0aaa8bf175b088753e2deda275d224`，迁移前后 DB 证据分别为 `58974b490d0c4edd7fd79821ef53b894e52a3d178d4dcc119286b8bf74a58a52`、`856d4334f3f853112d3e8e36fba5af2009983d0655d46c777e467dd7a53479c5`。迁移前后 FK 与对象证据分别为 `271a2497f1604140bfa21bfcfcf221910452d61df235b0b7844035a983287ba8`、`bd0445a27cf2bf4865dbc147cdeb6b0166301fb077079b89c106941417337a0d`。真实 DDL 恢复材料保留至独立核验及 Owner 收尾决定。Dev/QA 隔离资源和历史候选继续按上文归属保留至交接确认，协调者核实后清理。本轮没有操作容器生命周期、生产、真实设备或冻结 CA／DAA／SMA／Field Flow。真实 dev 的写入和未转移外部数据流维持 Owner 控制，正式 dev 复验限于只读。Python Unicode 跨版本、生产负载和现场兼容性没有本轮实测。

### developer_handoff

交付 ARCH-OBS-002 r1（spec SHA-256 `957956ad81ed13bea03efd98a691a62f52b7526187d8c653ae1bfdf3e0424e37`）给协调者安排 fresh-context Verification。精确对象为上述正式工作树和 225 项清单、保留并行差异、三处运维配置动作、`c9e1a3b5d720` 真实 dev 及本段 DEV 自检。独立核验先核工作树与数据库、配置，再在 Owner 启动服务后使用其真实端口限制在只读 GET、OpenAPI、既有配置和页面查证。本任务 bundle 只追加 tasks.md，spec.md 和已存在 QA5 checklist 仍为原摘要；独立 QA 及 Human Owner 最终验收待各自角色记录。
