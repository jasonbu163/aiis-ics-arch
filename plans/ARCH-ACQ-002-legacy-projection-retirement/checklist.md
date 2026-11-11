Task ID: ARCH-ACQ-002
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA / Verification -> Human Owner 最终验收 ARCH-ACQ-002 r2
Workflow Mode: STD
Execution Mode: agent_team_same_session
Updated: 2026-11-11 Asia/Shanghai

# ARCH-ACQ-002 r2 独立 Verification

## 验证依据与环境

- 串行收到精确 `developer_handoff` 后，以命名 `verification` fresh context 独立复核。角色配置为 `contract_only`。读取根契约、README/PLAN、相应模块手册和任务两份输入。验证应用项目治理、AIIS 架构、接口血缘、后端/API/数据库、维护 CLI、前端、i18n、代码索引及隔离 Docker 技能。 [根契约](../../AGENTS.md) · [开发工作流](../../.codex/workflows/development-lifecycle-workflow.md)
- 正式交付是当前未提交工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。获批 `spec.md` SHA-256 `79d35e149dd9d8159cd1ccb5ee461fdcb8cfa299d6a7931928f291ac74e42394`，`tasks.md` SHA-256 `415c64beceb2c0008e169e96594510b36815ebcbdf1cf7023990d63cf99501a9`。125 路径最终 manifest SHA-256 `b1b03ab0468b85b34b83a15899ef226f5e24c8ad549f6f4e1f531cae671184d5`。 [已批准规格](spec.md) · [Development 交接](tasks.md#developer-handoff)
- Darwin arm64、Python 3.13.3、uv 0.7.8、pytest 9.0.2、Node 22.19.0、pnpm 11.11.0。用本任务独立公开源码副本和项目现有锁定依赖。后端离线阶段使用合成配置并拦截网络、SQLite 及正式 `.env` 访问。前端使用空合成角色数组，构建输出落在 QA 临时目录。正式源码运行只读复核使用已指认的 3307 与 8000。

## 验收结果

| 标准 | 结果 | 独立证据 |
| --- | --- | --- |
| AC01 范围与调用方 | 通过 | 正式树、副本、持久候选归档 A3/M68/D54 共 125 项逐一吻合，125 条实际整合回执与 manifest 对齐。相对 HEAD 或已冻结候选可复核 118 个 M/D 前置字节，根 README 双份与两份前端测试的前置摘要来自已保存的交接 manifest。9 份旧 migration、4 份历史 MySQL runner 文件与冻结候选逐字节一致，归档 661 文件和 QA3 原 35 项摘要全部复核。现有工作树包含其他任务改动，FE-005 及共用索引按各自归属核对。 |
| AC02 旧入口与业务保全 | 通过 | 独立 app 探针中 v1 三路、旧快照和 Projection 探针均 404。真实字典路由无登录 401、无 grant 403，合成 admin 读取 200。已批准的业务 401/403 测试、当前模块 preflight 与三个公共符号正反例通过。8000 OpenAPI 旧 route 为 0，实际登录与 collector 成功。业务适配器、来源描述类型及历史 Projection metadata 留存。前端模块检查及 50 项通过，`/system/dict` 不在 manifest/导航，双语撤下旧键，残余 page grant 被拒，未知直链走既有路由守卫。HMI 页面、facade/mock 保留。其真实 HTTP 后端归消费项目，Core 在切换前已无 HMI HTTP 路由。 |
| AC03 两种升级 | 通过 | 自有 13394 执行空库全链及合成 2c4 升级。均到唯一 `3d5f7a9c1e23`，精确 68 张应用表，无旧九表，空库 ORM 与实际表清单一致。合成升级前后逐表 SHOW CREATE、行数和 checksum 相等，保留 v2 两表的微秒值、旧 Projection 水位和业务记录/回执。旧 migration 9/9 SHA 不变。 |
| AC04 预检与恢复 | 通过 | 真实 MySQL 非空、可见视图依赖、错误 UUID、冲突锁等待均拒绝且原表集合及 revision 保留。离线替身另覆盖多/错 revision、额外/部分缺表、引擎和各类依赖。实测一次固定九表 DDL 后人为中断版本登记，处于 2c4/九表全无，无确认重跑拒绝。完整保留表对账后，经同迁移入口登记 3d5。重复到后继为无变更，降级拒绝。复建九表完整 metadata 与仅归一冗余字符集声明后的 DDL 摘要一致。 |
| AC05 v2 与并行 Web | 通过 | 五路生成 OpenAPI 的引用解析后完全相同，v1/v2 与 BE-010 的发布工件保持原字节。隔离实测 POST 鉴权、创建、重复和冲突，options/latest/history/detail、越范围 403、旧 profile/关闭 503，以及 `cleanup-v2` 拒旧目标并能计划/执行。3307 只读后置数据和 profile 摘要与记录对齐，8000 四 GET 与 collector 均 200。FE-005 自己的验收由其 bundle 记录。 |
| AC06 BE-010 与历史 | 通过 | 前驱合成写入八路。后继上三 owner 用旧凭据均 503。精确同目标的新凭据重放八份永久回执并保留 record ID、receipt ID 与 committedAt，新写八路可成功和幂等重放。正式 dev 的配置仍为三个 owner 关闭且 unadopted。历史 BE-012 B 两入口及 BE-010 A+B 各按其冻结候选与原批准使用。 |
| AC07 指定 dev 对账 | 通过 | 独立只读连接确认 3307 MySQL 8.4.6、上海偏移 +28800、目标身份、唯一后继、九表全无、68 张保留表及 v2 各 2 行。下列结构、对象、内容及 profile 摘要与迁移前后持久记录相符。历史维护窗口依据协调者保留的进程/连接、空表和无依赖回执。Verification 未对该库执行 DDL/DML。 |

### 旧调用与入口证据

- 在 Core 活跃 app/core/common 和 frontend/src 查找旧九表及接口名。表级命中归迁移、显式隔离测试和保留历史引用。普通装配没有旧 runner。保留业务的 descriptor/provenance、同步适配器和 Projection metadata 可见于当前源码。维护入口裸运行只显示 `cleanup-v2` 帮助并 exit 0。
- `vibe-l2-front-end` 两个前端仍有旧快照/Projection facade，其 backend 和 CA 仍有对应旧实现。Core 外的 DAA 旧 v1 HTTP、直库兼容实体和冻结 CA 均仍能在源码定位。当前指定 dev 已撤下这些旧合同，消费方另有采用或切换任务。本轮核对调用方只读。维护窗口内旧 writer/reader 不存在的证据来自协调者当时的连接、进程、事务和运行配置核对，不外推到其他部署。
- 现有 `tools/lineage-audit` 从副本运行，使用合成空策略及与 tools lock 一致的 PyYAML 6.0.3，exit 0。后端 183 路由，前端 101 API、130 条组件链接。静态扫描器计 26 条前端路由，实际 manifest checker 计 24 条，动态装配以实际 checker/OpenAPI 为准。可复核行包括 `backend_routes.csv` 的 `backend_routes:f18f96e32bb5`（options），`frontend_links.csv` 的 `frontend_links:28647cb778c6`（HMI → facade）。合成空策略只供发现调用关系。

## 命令与证据

- `uv run --offline --frozen --no-sync pytest -vv --tb=short --show-capture=no -p no:cacheprovider tests_mysql/test_legacy_acquisition_retirement.py` 从 QA 副本执行，**3 passed，exit 0，36.34 s**。私有注册表权限 0600，经 Docker 名称、任务标签、固定镜像、loopback 端口、MySQL 8.4.6、非 root、三独占空 schema 和实际 SQL 身份核对。QA UUID SHA-256 `0320e2d7873e56776e58b52538f2f97fa6eaa6d2c7953910e7ad1c6841d06fbf`，与 Dev/3307 均不同。三个 schema 为 `arch_acq002_qa_r2_empty`、`arch_acq002_qa_r2_upgrade`、`arch_acq002_qa_r2_guard`。
- 隔离九表复建的 metadata SHA-256 前后均 `15c9e016426e521712fdde87e606f753bfa07d5476fa77639be12062d31aab5c`。归一完整 DDL 前后均 `cc9250d3cecd4420242f4ff597f0902dd78f119cd24ff54d2337e58dc498b954`。MySQL SHOW CREATE 仅四表增加 19 处冗余字符集声明。独立 QA 恢复证明 JSON SHA-256 `adefb6a50ab3e2b1f0be63a9d8745bc802c1a8f6fa2b25e897b79da5328e0b87`。协调者在 Dev 夹具用实际 dev 备份复建 9/9 张空表，SHOW CREATE 逐字一致，前后 metadata SHA-256 均为 `08af2aca6c75e3e5b6ff10fe4ac1a1c05e9c3dacc3d0b281a70040c9ef3ad20a`。
- 对 3307 用事务只读会话及定界查询重算摘要。68 表结构/行数 `b7787f6958a25bc01d688a4495381667ec7c2d65f0fa373d3ad88dc7f3dabf27`，对象 `455072696435b6aa0ec8a51b9d5dd47ec8afd98b4b423f40c1d491a6a8107752`。v2 样本 `df14f8ef31a6382f933e52350494c2fdcb3e47fb6503a8207acad30037b075ea`，latest `40e7c677e0b1f7900d8ce55ac74418be6c8833aa7bcd999fe462491b5a048b86`。新 profile `2179386159122eb1d888b1f220cf3d16a10c389fa6cb080b513cc64707975f52`，扣除 revision 的前后摘要 `b28e0103fe3cac9adfa6938f16d7d0f00c0960ca960cc9d491ff87fc6a06e489`。8000 正常登录后只发已批准的 GET，四路 v2 响应摘要 `cf6215aa43e30a2a11503aa4645a7db6fd5a3b8ae95b982a2f749a8394626041`，与切换前相同。Docker Compose project 为 `aiis-ics-arch-database-only`，实际 MySQL 容器为 `aiis-ics-arch-database-only-mysql-1`。QA 连接使用 127.0.0.1，原服务 3307 宿主映射为 IPv4/IPv6 通配地址。
- `uv run --offline --frozen --no-sync python -m compileall -q app core database projection scripts tests tests_mysql main.py build.py`、`alembic heads`（唯一后继）和 `python -m app.module_preflight --project-root <候选 backend> --check-only` 均 exit 0。定向 15 个 pytest 文件共 **147 passed、3 skipped，exit 0**，包含清退、v2、入口、权限、业务存储与迁移回归。三项 skipped 是历史 BE-012 B、F/58、BE003/60 的现行候选占位。冻结 QA3 的两个历史入口检查 **2 passed，exit 0**。
- v2 OpenAPI 独立对照中仅 20 个 `FailureOut` 和 1 个 `ReceiptOut` 的生成引用名改变，原因是删除了名称冲突的 v1 模型。解析组件引用后五路的完整操作定义 SHA-256 同为 `c2c07f8e0e0ce1851eaa67a685199106505db76491b0378548349a8c20f65a5b`，发布工件未随运行时名称改变。
- `pnpm --config.verify-deps-before-run=false run check:modules`、`... run test:modules`、`... run build --outDir <QA临时输出>` 均 exit 0，10 组/24 路由、**50 passed**。构建保留既有大 chunk 警告。系统文案中英均 73 个叶键，breadcrumb 中英均 2 个叶键。4 份 JSON 解析成功，20 份现行文档 198 个本地路径均有效，`git diff --check` exit 0。

### 定向后端复跑入口

合成配置指向恢复的 QA3 源码及其三个公开示例，设置 `ARCH_ACQ002_HISTORICAL_BACKEND`、`ARCH_ACQ002_HISTORICAL_EXAMPLES`。Docker 两份公开示例从固定 HEAD 复建。运行源码位置由显式 `PYTHONPATH` 固定到副本。

```bash
uv run --offline --frozen --no-sync pytest -q --tb=short --show-capture=no -p no:cacheprovider \
  tests/test_legacy_acquisition_retirement.py tests/test_plc_facts_v2.py \
  tests/test_aiis_demo_module.py tests/test_business_integration_compatibility.py \
  tests/test_business_integration_migration.py tests/test_business_integration_storage.py \
  tests/test_business_module_migration.py tests/test_business_module_reintegration.py \
  tests/test_core_migration_baseline.py tests/test_energy_price_migration.py \
  tests/test_equipment_temperature_migration.py tests/test_logging.py \
  tests/test_mapping_migration.py tests/test_module_registry.py tests/test_openapi_router_tags.py
```

## 扩展检查与判定边界

- 正确提供归档输入的扩展 `uv run --offline --frozen --no-sync pytest -q -m no_db --tb=short --show-capture=no -p no:cacheprovider` 为 **1023 passed、6 failed、3 skipped、28 deselected，exit 1**。与 Development 记录的六个失败 node ID 相同。
- 六项已知失败逐一重跑。两项旧公开 example 数量/摘要测试依赖 r2 已获批撤掉的旧配置。三项 `test_module_contract.py` 用当前 preflight 扫描冻结 C2，先于目标断言在旧 System 对 `SnapshotPolicyCatalog` 的私有引用处失败。原 QA3 及其公开示例中这五项均通过。独立对当前树执行 preflight，并在合成模块实际检查三组公共/私有符号，正反例全部通过。
- `test_business_module_permissions.py::test_each_registered_business_method_has_declared_owner_guard` 在当前与冻结 QA3 均对 BE-010 匿名 `/api/v1/integration/performances/production-observations` 失败。其旁边的已注册业务 401/403 正常鉴权回归通过。独立对照上述六项和业务鉴权时，当前为 6 failed / 1 passed，冻结 QA3 的六项为 1 failed / 5 passed。
- 无归档变量试跑的三项定向失败均为缺少冻结输入，非运行时数据库失败。正确提供固定归档和示例后，定向测试 147/3 完成。默认 pytest 入口中的历史 fixture 有额外输入要求。上述扩展失败和普通入口限制保留为交接项。r2 验收以批准的定向范围、现行合同探针、独立 MySQL 和 dev 证据判定。

## 限制与资源

- 真实 dev 的迁移前、迁移后、9 张空表 DDL、复建回执与 125 条操作日志已复核 SHA 和权限。持久目录为 `backend/data/maintenance-evidence/arch-acq002-r2-history/dev-3307-20261111/`，保留至 Human Owner 验收、恢复证据依赖及后续任务需要结束。BE-012 公开候选归档保留至原 r4 B 验证和 Human Owner 决定完成且无其他依赖。恢复真实 dev 需要独立批准。
- 两轮夹具由协调者在各自最后 SQL 操作后回收。QA 复查任务标签无容器、13393/13394 无监听，原 dev 容器仍健康且 8000 监听。协调者确认两个临时凭据登记文件已清除。QA 临时源码和日志位于 `/private/tmp/arch-acq002-r2-qa-Uu5JuQSK/`，供终验核对后由协调者按归属清理。关键结果与指纹已写在本文件。
- 新迁移明确要求在线和两项精确目标变量。现有 Compose migration/可选自动迁移入口仍调用 `upgrade head`，新库和前驱库未准备这些变量时会拒绝。后端手册现行迁移节有护栏说明，早先 smoke 与通用离线 SQL 示例未指向该护栏。独立 QA 只覆盖获批 dev 和隔离迁移，未运行整栈 Compose 或发布/打包。审查时 backend 与 frontend-js 模块 PLAN 仍将旧快照及 System 映射页列在当前基线，索引机械同步由协调者处理。
- 扩展 no-db 不是全绿。详见下节。跨端正式接线、DAA 原配置/SQLite/积压、SMA、冻结 CA、其他库、现场、生产及原 BE-012 B 属独立范围。本轮未执行这些环境的变更。

## Human Owner 最终验收

`qa_passed` 覆盖精确 r2 的 AC01–AC07。无阻断该范围终验的未通过项。扩展套件、当前启动说明及独立交付边界按上文交接。Human Owner 对精确 ARCH-ACQ-002 r2 的最终验收待决定。
