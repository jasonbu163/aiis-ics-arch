Task ID: ARCH-ACQ-002
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development -> fresh-context Verification
Updated: 2026-11-11 Asia/Shanghai
Workflow Mode: STD
Execution Mode: agent_team_same_session

# Development 实施记录

## 批准、基线与保护

- Human Owner 已批准精确 `ARCH-ACQ-002 r2`；本次读取的 `spec.md` SHA-256 为 `79d35e149dd9d8159cd1ccb5ee461fdcb8cfa299d6a7931928f291ac74e42394`。任务启动时正式树 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，有多项 DAA、BE-012、OBS 等未提交变更；这些不是本任务清理对象。此状态不代表 commit 已包含工作树候选。
- 后端 `127.0.0.1:8000` 进程自动 reload。除下列无运行时影响的两份前端测试机械预调整，清退实现先放在任务私有公开源码副本 `/private/tmp/arch-acq002-r2-dev-h8rW0pBF/source`；未复制真实 `.env`、数据库、客户数据或 DAA/CA/SMA 运行文件。候选整合及实际 dev 操作须由协调者在同一维护窗口串行安排，本记录不代表正式树已切换。
- 协调者要求先为并行 FE-005 隔离其新增模块。正式树 `frontend-js/tests/module-registry/registry.test.mjs` SHA-256 `e0b37f35b75048f5fcd802f4a70c2b6eb1093097d43897b68e1e7e8623cc6426`，`page-access.test.mjs` SHA-256 `d7f061e472c8bea7c4337f0bbfc4644c512c9ab8f25b41cdb8373d1b539f34ae`。仅从原业务全量比较中过滤 `acquisition-data`，旧 mapping 页的原断言尚未在正式树撤下；FE 新组由其任务单独验证。后续串行整合须重新核对这两文件的现行内容。

## BE-012 r4 历史候选的可恢复材料

- 独立 QA3 的公开候选 `/private/tmp/arch-be012-r4-qaA3-fltc5j47/source` 中，`development-r4-qa2-fix-hashes.txt` 指定的 backend/contracts 35 项逐项重算，35/35 一致。该目录后续出现 `backend/logs` 四个日志，归档明确排除这些日志；未打包真实 `.env`、私有 profile、数据库、数据目录、凭据文件、符号链接、运行缓存或 venv。三个 `.env.example` 为公开示例。
- 可恢复归档（忽略项、非源码 diff）位于 `backend/data/maintenance-evidence/arch-acq002-r2-history/be012-r4-qa3-public-source.tar.gz`，SHA-256 `a011e4667228c314ce8518ec48f29a7506f6fee265f509e840ca20e0d18cb9d3`；661 个文件逐字节与源副本核对。逐文件清单 `be012-r4-qa3-public-source.sha256` SHA-256 `ec41fd83db8e3c1123b1b638d7d78de29499a50256a715210129190ac6735e48`。目录和文件由本任务创建，权限为本机私有。
- 恢复时先核对归档 SHA-256，解压到新建的 `/private/tmp/arch-be012-r4-*` 目录，保留其 `source/backend` 路径形状，再按 [BE-012 r4 B 启动修订](../ARCH-BE-012-simplified-plc-facts/tasks.md#b-启动方式修订替换前文所有-b-直接启动命令)使用原候选、原 `tests_mysql/test_plc_facts_v2.py` 与 `tests_mysql/test_business_integration.py`、各自的完整目标护栏和经另批的隔离目标。原 v1、F7 与 `1b3`/`2c4` 验证不能在本任务新 head 引入已退役模型代替。归档至少保留到 BE-012 r4 原 B 全部完成、Human Owner 作出最终决定且协调者确认无其他依赖，再决定清理。
- QA3 副本只包含主 `.env.example`。另外两份公开 Docker examples 从固定 Git `bcafa89fa31bdf62329bced89baebc193323a739` 恢复，且恢复前分别与正式树未修改的公开示例逐字节一致；三份完整文件 SHA-256 依次为 `33021261d511c17930445c8d0ff9596cd5b645dc1d3e8c1250ba7fed7a5e6bf9`、`ea2886aa84c88b28d019ea3518c5714eca43c45efc7310862674c324569d1800`、`54c3fc39f69833c9f49e9c4d71e22ef2282a84b25f3c633dc3d5b12a0afb8c7c`。

## 已完成的隔离候选检查

- 后端使用合成公开环境和项目 `uv` 锁定依赖运行定向 `pytest -q --tb=short --show-capture=no -p no:cacheprovider`，覆盖 `test_legacy_acquisition_retirement.py`、`test_plc_facts_v2.py` 和 r2 列出的入口、业务、迁移、权限与日志回归：**147 passed、3 skipped，exit 0**。三项跳过分别为须用原 BE-012 B 候选的离线 runner 检查，以及历史 F/58、BE003/60 模型 parity；不把现行后继模型冒充旧模型。
- 原历史 runner 检查从 QA3 候选运行两项，**2 passed，exit 0**。不可变 Git `1a5aa2d` 的原 F/58 测试与 `f85bea8` 的原 BE003/60 测试各自从临时重建源码运行，各 **1 passed，exit 0**；原测试断言未被改写。完整 B 阶段未运行。
- 表外历史断言 `test_mapping_compatibility.py::test_69_original_public_assignments_preserved_plus_three_empty_scopes` 与 `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment` 从恢复的 QA3 历史候选和上述固定公开示例原样执行，**2 passed，exit 0**。当前示例依据 r2 撤掉 3 个旧 Projection 配置与 4 个 v1 事实配置，与这些固定旧配置快照断言冲突；不修改表外测试或全局 skip，也不宣称当前全量测试通过。
- 候选前端在复用现有锁定依赖、合成空权限环境下，`pnpm --config.verify-deps-before-run=false run check:modules`、`... run test:modules`、`... run build` 分别 exit 0；模块测试 **46 passed**。构建报告既有较大 chunk 提示。最初未关闭 pnpm 依赖自动核验的试运行被无 TTY 防护中止且 exit 非零，未执行依赖安装；补全 Node PATH 和禁用自动核验后上述命令通过。
- 按 `interface-lineage-audit` 检查现有离线工具：原工具的 `inputs/module_alignment_policy.yaml` 缺失，直接运行失败。将工具公开源码复制到任务临时目录，提供空合成策略（所有未列模块仅 `unassessed`，不是通过结论），以 `uv run --offline --frozen --no-sync` 对候选前后端扫描 exit 0，输出 183 条后端路由、124 条组件链接、100 个前端 API、24 条前端路由。使用 PyYAML 6.0.3，与 tools 锁文件一致。扫描器对 route→model 及动态注册标为 manual review；并通过源码及 OpenAPI 定向核对旧路由不存在、v2 五路和 collector 保留。

## 尚未完成

- 一次性 MySQL 8.4.6 夹具尚未获得启动及实际运行结果；空库全链、合成旧库升级、锁等待、非空/依赖拒绝、版本登记故障恢复、v2 和 BE-010 八路验证均未记为通过。
- 指定 3307 dev 的正式预检、恢复 DDL 和保留数据摘要、实际迁移、私有 profile 原子单键切换、加载与四路 GET 对账均由协调者安排，尚未在此记录为完成。调用方是否连接目标、跨 schema 完整可见性及无并发 writer 仍为实际迁移前 gate。
- 尚未形成 `developer_handoff`，尚未交 fresh-context Verification，不能据此推断 QA verdict 或 Human Owner 最终验收。

## 扩展检查与当前停点（2026-11-10 23:18 Asia/Shanghai）

- `uv run --offline --frozen --no-sync python -m compileall -q app core database projection scripts tests tests_mysql main.py` 在隔离公开候选和合成环境执行，exit 0。新增清退护栏测试定向重跑 `pytest -q --tb=short --show-capture=no -p no:cacheprovider tests/test_legacy_acquisition_retirement.py` 为 **19 passed，exit 0**；九个旧 Alembic 版本文件与 QA3 原候选逐文件 SHA-256 比对 9/9 一致。20 份修改的 Markdown，198 个相对路径链接检查，缺失 0；未声称逐锚点验证。
- 较宽的 `uv run --offline --frozen --no-sync pytest -q -m no_db --tb=short --show-capture=no -p no:cacheprovider` 为 **1023 passed、3 skipped、28 deselected、6 failed，exit 1**。六项逐一核对：
  - 表外 `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment` 和 `test_mapping_compatibility.py::test_69_original_public_assignments_preserved_plus_three_empty_scopes` 固定旧公开 example 的赋值数量/摘要，与 r2 撤除 3 项 Projection 与 4 项 v1 赋值冲突；两项在恢复的 QA3 原候选和固定 HEAD 公开示例下原样 **2 passed**。
  - 表外 `test_module_contract.py` 的 `test_integration_public_surface_and_private_boundary`、`test_temperature_env_helper_is_only_additive_public_setting`、`test_business_time_public_pure_symbols_and_private_rejection` 在现行 preflight 中扫描冻结 C2 的旧 System Projection 文件，因现行私有兼容面退役而失败；同三项在 QA3 原候选 **3 passed**。保全的 C2 仍由其原候选提供旧 CRUD、快照及 Model 出口。
  - 表外 `test_business_module_permissions.py::test_each_registered_business_method_has_declared_owner_guard` 假定 BE-010 匿名生产写入具有通用登录 permission；QA3 原候选复跑同一断言也以相同路径失败，**1 failed，exit 1**，为既有基线冲突。本任务不修改这些表外测试、不全局 skip、不以此声称全量通过。
- 隔离 MySQL 入口只完成静态检查。`python /private/tmp/arch-acq002-r2-dev-h8rW0pBF/run_mysql_fixture.py /private/tmp/arch-acq002-r2-dev-h8rW0pBF/fixture-guard-test.json` 使用合成账号、虚构 schema 和禁用的 3307 端口；在导入项目配置及创建连接前于 pytest collection 显式拒绝，exit 2（预期拒绝）。新增入口中同连接固定九表 `LOCK TABLES ... WRITE`、5 秒元数据锁等待、锁内重查、单条固定 DROP、`UNLOCK TABLES` 与等待设置恢复有离线替身检查；真正 MySQL 的竞争及恢复行为仍未验证。
- 协调者提供的**只读预备盘点**（不是维护窗口正式预检）：指定 3307 dev 是 MySQL 8.4.6、上海会话偏移 +28800、唯一前驱 `2c4e6a8b0d12`、77 张应用表，九表为 InnoDB 且均空；已识别 DBX 与 backend 空闲连接，无未决事务。已记录保留 68 表行数/结构和 v2 两表各 2 行摘要，脱敏预备记录 `/private/tmp/arch-acq002-r2-coord-dPORAa/dev-before.json`；九表复建 DDL SHA-256 `0f4b65671bcd2afd325aed13aafd66e3c5ecdee76b4bdf3db140f807cf6a5b4f`。8000 四 GET 与 collector 均返回 200，v2 数据摘要 SHA-256 `cf6215aa43e30a2a11503aa4645a7db6fd5a3b8ae95b982a2f749a8394626041`。此为协调者当时事实，不能替代执行前复核 server UUID、完整依赖可见性、连接、写入方和维护窗口，不能证明已迁移。
- **停点 `needs_input`：** 尚缺 Human Owner 对各自独占的一次性 MySQL 8.4.6 测试资源与临时 Docker 启停/回收的具体授权。协调者已拟定 Development `127.0.0.1:13393`、Verification `127.0.0.1:13394`，各自三个独立空 schema、非 root 账号和匹配的 server UUID；明确授权实例、卷/网络、连接、schema、迁移/合成写入、锁竞争/故障注入及回收后，先运行 Development 完整隔离矩阵并保存结果，再完成 3307 同窗口预检和切换；随后才可形成精确 `developer_handoff` 并启动 fresh-context Verification。没有这些结果，候选未 ready，3307 未迁移，profile 未变更，未作 QA 或 Owner 结论。
- 恢复本任务需保留 `/private/tmp/arch-acq002-r2-dev-h8rW0pBF/`（候选、实际使用的测试辅助脚本、合成 policy、输出和 diff 清单）；它只供本任务继续与验证，不是唯一持久结论。完成整合及后续验证、确认无依赖后由协调者按资源生命周期回收。独立的 QA3 历史归档按上文长期保留条件处理；`/private/tmp/arch-be012-r4-acq002-history-jcf0wzis` 是从归档恢复的本任务副本，原 QA3 副本未被回收。

## 精确候选清单

以下为隔离候选相对 **2026-11-10 23:18** 正式工作树的 125 项计划变更（新增 3、修改 68、删除 54），不是正式树已实施清单。四列为 `A/M/D`、路径、当前正式树 SHA-256、候选 SHA-256；`-` 表示不存在。对应 TSV 的 SHA-256 为 `2e6fc149c8f8d6ad07859ad1d3c714ad493a05cbd50f17613abf4a76eb569b9f`。正式树任何相关文件在整合前变化均需重新比较、协调合并和复测；不得整目录覆盖并行 FE 修改。52 个 backend 删除项与保全的 QA3 原候选逐字节一致；两个前端删除项在正式工作树无未提交修改、可由当前 Git HEAD 恢复。原有九份 Alembic 文件不在清单内。

```text
M	README.md	174e8ac63197c26f84666b3f78c6ab10014b90763eac518b8f830bd6231385c4	e6bcc9e1bd2c7aa1eab3a0592a6e7585292b477e20a18a5d820d245a591b2dce
M	README.zh-CN.md	b8cdc833cf395abb3dd6d9677cb380cee2512a3ed97655050959d2cf165487ae	45f5176b66e912e823e9081baf81ca94097d315761271bc2572ef7fae988c3bf
M	backend/.env.docker.dev.example	ea2886aa84c88b28d019ea3518c5714eca43c45efc7310862674c324569d1800	67a1d8710d368ea295afc0643c38447cc96133fd1482c2178ce0417c72fae433
M	backend/.env.docker.prod.example	54c3fc39f69833c9f49e9c4d71e22ef2282a84b25f3c633dc3d5b12a0afb8c7c	4b4312bc06b614cb1cd31c7134ccfdb9afa210f58e5c47af0ecd7479bd33ac6a
M	backend/.env.example	33021261d511c17930445c8d0ff9596cd5b645dc1d3e8c1250ba7fed7a5e6bf9	7a0da42671a48b3334f59d51605bc2939604fc7c0755c05c995ffc8b86d7a794
M	backend/README.md	44818a8189a86e893fbdc078b21869bcabbc36d5136d79e7485ffc9ff26b0956	49e8e4eec550d81c5a8ace04adb4caa21bb94419aefd630f3e093bb31c5cf02f
M	backend/README.zh-CN.md	bf810beb28285a231fce3a3d5e9a044b61b5032d99c2e39ae585efc093fa3ad7	32b66919995dfe7982427d577e6594b7b4bcec5accfd1337f87246d47bc9746a
M	backend/alembic/env.py	6e4195c922c06946f217e344fa41d105875d60e7a7925c374fab4cab0ce5d2e5	d15288cd684a05d86906af56504dbf9765a5139669e8a1cefad8c335cc9418d5
A	backend/alembic/versions/20261110_2215_3d5f7a9c1e23_retire_legacy_acquisition.py	-	337ea1530f379e6076d784757572ae56be25752c5f039e41ff84bddbc66591d5
M	backend/app/MODULE_CONTRACT.md	59df0919940179652d8e6719ee74d2e31e0bbcdb9d91f431690e54249b73b4fd	67799004be3174ddf9f70d6dde01a620cdbbc1b59fb28b3b0e1bd5ddc54ecd49
M	backend/app/MODULE_CONTRACT.zh-CN.md	14a6b3cf0d49133c6664cd234835f375f5113f243c0b398be489d076e87e57e1	15cd536cd9e1339c37d6f06cac50e04f8cfd0ceff71f546bdb6d806ec791c787
M	backend/app/README.md	13c2171a32930fa69bb9e40bff63988d27544d480901139cd4d5be74c1a067da	b0a36169c0b22279d72bcbc7ea11d0241b69f11468d884f82f1beb242453a386
M	backend/app/README.zh-CN.md	eeb606e726592326e1d109e7d2222d15f46c365b60203103a08ece93febdc9b8	d9099e1198df08c459cb7ced2a4eacca2587cf4dbd5141cc1454e40da5f22c69
M	backend/app/module_contract.py	d91c98d46f526af8e87502685833dd00570f45c090c40949938ae689cfd84778	2c28724c7f4f34426e3c000f276f8dcb0b0b8ab16c79e4f75b970e1684253e75
M	backend/app/module_registry.py	de6c73d49a988de66a8d49617e78679176b2ebf3459f93cfc348610244a260ab	d055822e1e3866ef6e64e0d166e1e74d9158c0c37d7b6a8f14656118b439f711
M	backend/app/monitor/README.md	cc47ae0ada0301e6be7e47c01bef90d136742f2cdf11e98c78b8c3ea55139a2c	82429bcce197ec6dd114f64fd9f7818bb0c81a9b4f304a0df4f84071a492a29a
M	backend/app/monitor/README.zh-CN.md	72be0c1d0b2896796ba669f3481b9448d083a05de42d68b9217101a020927db5	8376758df08447424ab43696a86624af7f192b284779f92ec42744d574f02c5d
D	backend/app/monitor/api/realtime.py	cf0d4e6b3f5ece1a0383b76e365fdfae245cf05550ba43cf368f108349464773	-
M	backend/app/monitor/api/routes.py	ff15b5e30c3907e9313e1147ac491675f15aa375055cf54c5342f028e591538f	a2a8210a6f4a44bac601da2f65cad7fe9e39183d5f3031779274b5a3db0d6b9e
D	backend/app/monitor/crud/async_realtime.py	c8b8d47a1b56f08e6c7bc9237c8cba69f348f6cb343e8670abb83c8c472db38a	-
M	backend/app/monitor/manifest.py	571e95bcf0867318d817d0ef57c185c39cf649f9730260254b484f722ef3034d	46f48e7022dadf43507b5fd5821fa35c9becc46d8f930728cff6dacf1e9f15bb
M	backend/app/monitor/models/__init__.py	f0d8df47e2e9ef028e1f0d6779e97dc92bea82b8edfa619019bd3696d336d7af	554bbea9a380b5968efda2d79dc82965ba44f9f05f928b17c3b455d5002cadf5
M	backend/app/monitor/models/monitor.py	5ca4b558469b7d4f96dd838b50b1128d349ccb6515c071bf5c3bc45cfbe58521	0885e75bba793d0ba0d282e5a27b195d99dbc06662fa0b42662d3b4a94a0828c
M	backend/app/monitor/schemas/__init__.py	7391a35dc4d4a7bb845e539732468fc01868a37078538bcc1915a40935d37665	3b037cd93c6d2f50c22720a80ccce89cb0261e3efb4838d698ea880b1d88b8dc
D	backend/app/monitor/schemas/realtime.py	f0ef917714ef327a83e9a822cbdfb3394e1c80763715d71e3c3f9f5217574111	-
D	backend/app/monitor/services/async_realtime.py	830f7a4e4d612bc7ceace233fdf90fac833a3fa84e524df5491e26fc8d8064a4	-
M	backend/app/plc_facts/README.md	c714086d5d9aca44b221ff096f33fd3bea56d9e594405871cf206ed51dc99a7b	dca3ad3c3cf173c7df1f1ea744e3a1c7cf52f1df6af0f16f62cbe2947bd39640
M	backend/app/plc_facts/README.zh-CN.md	88867ef7cfcc6e2a07bed7682e59be2a99d4b42253038df243b95bd12efc03a4	031286299bc3408798a1b354037aec287a16d294ebdbf73c6f177b82e8b70d9d
D	backend/app/plc_facts/api/batches.py	b08081c5486b3463164b8a8b384d972ce01c57fab56ee90a8ed97ff03ceec524	-
D	backend/app/plc_facts/api/dependencies.py	ee80d94d5e65bb8bb2c2c758044fec359057f0a3b02a7458052c592db7fae2a8	-
D	backend/app/plc_facts/api/history.py	3ade3187a476859d806d58d52d28e4595bcbd374d479176bee49ca343a4490fe	-
D	backend/app/plc_facts/api/http.py	4664f4c6315aa1b0f46f24a8193860558085c12664c1016b1f7efbcf10ee4c27	-
D	backend/app/plc_facts/api/latest.py	798f3f88f55d7568f9f9d5742769a333eabe7223069cc5d0c5c204fee0624fd8	-
D	backend/app/plc_facts/api/routes.py	b73df8fc9570d8cdfaf33c58dd1ae2bad5452f7c715c51ba69504b144b0379b8	-
D	backend/app/plc_facts/canonical.py	c48f0957b65c4348dec4fdfd8d76d9bd29891355b302b4d189b81cad7bbf1cd9	-
D	backend/app/plc_facts/config.py	7f498a16a316d94a21cf28dd1572b3c044883910c0e16de2ca0ac79c40374577	-
D	backend/app/plc_facts/crud/async_ingest.py	2e087d3b5466630e41358c0c24b0b15a7dac4f1aba7721491995ca81a2e131aa	-
D	backend/app/plc_facts/crud/async_query.py	86686afb7ef383f9bc702e374b20eced4306b5c8184c0646de00ff3745bb6645	-
D	backend/app/plc_facts/crud/sync_maintenance.py	059a6677f8430b24e310feddecad8e64ba22d83be0ab0e8ff3bd56a293bb0c24	-
D	backend/app/plc_facts/cursors.py	e1bf72ffb13a32e096418275054222e95a455f46eca1b6e412644f90cbc9f783	-
D	backend/app/plc_facts/error_codes.py	8529c74ec787137f508e29fae4c8afcad51bb2ca9d63908fde30edb59b1824ce	-
M	backend/app/plc_facts/manifest.py	358f77c2405322fc20bd5415b2406bb492385f11e0d012e34a3b22255eafced9	54fc73b417aaa8153e1a1e6feb8b104d05728fba0c4d03a5b12be654f2ccfd51
M	backend/app/plc_facts/models/__init__.py	e6738175c336bda4f11f228fc43b8f6de7571cda331c45ae4aea2edc2dba74ea	f3f21e21fdda181915452b67c7ef13b083d613154b385a2310d8e055a4e41f4c
D	backend/app/plc_facts/models/facts.py	920e89c963190bef00edb6c06d0195a93afa38cbb876c9edc946f3e3c203b89f	-
D	backend/app/plc_facts/models/receipts.py	880e98b0cc2a3440e0c139c47d03369fe5937d79afef85d09e5e8018413deda1	-
D	backend/app/plc_facts/models/state.py	104bedf1907a325decc54e1f041ff31d1a723434f35a38331515f398e2aa3d0d	-
D	backend/app/plc_facts/retention.py	f73c302c1196eaeeaf521de73bbd220a9466b8e2666f2aaa51e78fc01d591e9d	-
D	backend/app/plc_facts/schemas/batch_in.py	a0a625433a76c9b39a7009a04579ca02f9844c119679ba9a533ff678dbcbc69b	-
D	backend/app/plc_facts/schemas/query.py	1689676876f6f5b360ccac23769a56da6a7b3f926bd5f90d0c4af385254671cf	-
D	backend/app/plc_facts/schemas/read_out.py	4b8c421e993d9977f652e1f74fd2904837cacbd91a1136cf32c0d082259e2ad9	-
D	backend/app/plc_facts/schemas/receipt_out.py	14d37df54acbef48fe55eedc9d26b1c3512a422f9f4bdaac45b304b651979e40	-
D	backend/app/plc_facts/schemas/source.py	1c3726df2f8b73761e1b0aff61323ed5452911ab941df3065ae5e35f60f9e639	-
D	backend/app/plc_facts/services/async_ingest.py	91b15e1842847db6612fc83753a9a9fac2caaa44a57c655ee223a12685a9a60f	-
D	backend/app/plc_facts/services/async_query.py	7755a9537779afa4ee05615686282de831e0451fc02fe77948479e46d46b383e	-
D	backend/app/plc_facts/services/sync_maintenance.py	3e138ae817c49a20243cf8c6df0c5df57ffc2e91248171956a5f29d28798ff61	-
D	backend/app/plc_facts/source.py	a7fd7ef75149e251a47d838fbd57db00c540c7990d1f64f3d9e9a67edc1489d8	-
M	backend/app/plc_facts/v2_config.py	8a7d27cc40eb090fcc3374e74576d545e216881f607429bb62b501ee5e02cd60	2cfcc8957a945769a6e5dc178dca8eff0d022956244b519ea8d1f066751967e3
D	backend/app/system/api/projection_mapping.py	4783d6a5d112c9bcf768944725a88452798ab877da09b0562994bc8cb64d1589	-
D	backend/app/system/crud/async_projection_mapping.py	58b84727175e5fc97bf18c7eb9f73a06879c27a2f40d26959fb851335c97319e	-
M	backend/app/system/manifest.py	a538991218b29bedb465ae75b8df949e128dbf091c5d7d915ca2d0a324ab1f5f	275c3dee481402a2b888da5f5e55ad6dcf842a9696ae44ad509a7ba4766b0bdf
D	backend/app/system/schemas/projection_mapping.py	775886cc86d883679c4c3d6aa1fb10155f7fca5d8cd3e019724d9dd85d2d1b09	-
D	backend/app/system/services/async_projection_mapping.py	478643849bce3d197bec303ffacbc4d9a821ac7980deabaf0034eb3669ea972d	-
M	backend/common/error_codes.py	90db8c6e452b992a77aa14c507d354ec77b4c7e3e112d05742b7f681ddacae35	72d4259da29c1bdcb146804fc7de3f913d8434eaaa4841060c68db7247fc1933
M	backend/common/integration/storage.py	ce1ebfb113b826300d15d34a3ab4ba083cd6f6be9b2808028e5770244d912362	7ce719f7f309c6a246192cd090ee373b5dcf88f15f7e961135f0cf5d7b4eaaa3
M	backend/common/log.py	da77925fd582e8ae65565d905b393d383f6282e8afb45911125101a379c64bc4	d9d25da2d787f75a286f21f5d7433c1da36064159447ead9f3fe61b0a15587b6
M	backend/core/registrar.py	b52e86b8c6b617607cc9dc26b35e7e8fcd6264cb333bad5f55578c97ac0d30f8	274612b5c15ef386f8491d99632adc3fe7645507c04c3578b6abc63119ecc2e4
M	backend/projection/__init__.py	a89c1ce75f2b56efb64960739deea084b6fff3a3f5fa67af279679d3102660e1	8c8081577a9ce8882f952e89e606f21d6415d7b09c422020e5695a732f41e8c2
D	backend/projection/failure_observability.py	29279ecaf3becbf5094ed92f811480d22ac71bd353a8172504a4392e33aadf00	-
D	backend/projection/input_resolver.py	61c0b098390ea5c95ebf31cc7cc3cf0d04b771fe6c21592ca6763f4f85696981	-
D	backend/projection/policy_catalog.py	605cd1aa578b9271c7318d8cf7a5a4f326abf003a205405ff323b4ba753124bc	-
M	backend/projection/registry.py	cc222d301879da3850262e5aa3f6e979f735d9f87f058d7b519e2d5d4c68d502	fdc3bdad4041066d8f22c9551e56b7873543e8d5c562a1ebb041d041d1dfd90b
D	backend/projection/runner.py	d2ebb20e0f1c6f7a7616b657d40ea11327fc58fa0e64972ff77f38fd7c648e98	-
D	backend/projection/runtime.py	8c0bc50c649dc2c91932002a94463e205f13609beb6d2001489e1488d618bc65	-
M	backend/scripts/business_time_adoption/README.md	c5af6cad7d8825b996f1557fed529d7028ed05e76c6e765c2aae8e60e87d0e3d	6de7acc07c7a9f406a237ff030f408132cd7d22b244ce13431b5c65603dc1ecb
M	backend/scripts/business_time_adoption/README.zh-CN.md	13a8222d190ebea93c588d44bb60e9d6afc31404b32eb06bc39fe85564450032	ad5ad99df80ea89ceb0e15b95207bc6d4510e55c516c79da400f7a4ae6720207
M	backend/scripts/plc_facts_maintenance/README.md	0b43546e1fa7ee1142b92fc1b5a472c8878ca0c8747ba63fa23773fcc7070166	53bdf5bc27cc8e9f312f7b6ebac7b6e723a0250b7d3ee41f63402f76136075ff
M	backend/scripts/plc_facts_maintenance/README.zh-CN.md	8025ccb669e80ab157bf0954758888800bfbdc0abb96dd44a2e84e341fe31e51	638f25aeb183fb787080e2c89ecd766ee111fa4d2ca48bb385a333ebd10e580d
M	backend/scripts/plc_facts_maintenance/main.py	f71e81f308f862461e791cf30c9c95ca07967c523cfe82f2fbffd11fa90b1ec0	bbb4f20b33b24f0d5b612729fa65766d672800f0b17eb2746fb6aa54bee7306e
M	backend/settings.py	b8d30d4fdb252de5b69d8e386574b6b68ce4d8d8fb9e07055117f9b5a08aefd5	048e1a9451d35a83dc78fd580f4133300481c827139ed6303d028fa51e6d34ab
D	backend/tests/app/monitor/test_realtime.py	516a0ebe9310517edb7f0bbe021b6d2234cdc7ba3e9feb800b36633017f50ce6	-
M	backend/tests/module_admission_fixtures.py	cd3c399657aaf5444d2fd718192016c7df6f76db87985bdd2fbfa8aa9786ecc9	842638ac8784c1bc5124b4c0dfd5c72ad127690436724035196ed4f61247016a
M	backend/tests/test_aiis_demo_module.py	aeb568ba544e478f791d0cf092b8dbe911a6ffc7afcc423994244c764fabfb6f	fae3dc3af1bc12e2bcc04274fd88baf7e914d5202f4ca391681e9d678a592c3c
M	backend/tests/test_business_integration_compatibility.py	8ee66757ed69bb792a357ed06be257e0b1ffa56ce68be82f749fe5b4b364f354	878a6625d750a50afaa2f44e71b75dc3e86e0d5c34bc1d3da1526229740bc6bf
M	backend/tests/test_business_integration_migration.py	455e73a14c9ef6e2336215daef488efe136e6ae6a7e9e8b750bd519476a6df95	d15f8d9dad880b0baa6290788ff331bb9bbeb4944f7959019106fdc551e58379
M	backend/tests/test_business_integration_storage.py	70c5e69c3bdb4587cc23b7c20a0cccfeec8d33f50125a648ee3445a662c226df	f012565f959751d8f855a011992cb8e3b0f0781a0b0470a0cc2508a212893244
M	backend/tests/test_business_module_migration.py	bcc639d0b474178851733ae65c5624a5c37320b538d4d5d86ce0b006e67a7fe9	2c00593e3a40fcdede096272d8a0b2a98fd30fd954e6cf72411d3a902079d68b
M	backend/tests/test_business_module_reintegration.py	6524b111d2ee86c9dbdc8518d56caa1483b20358bfc8d722e49d3040c9188433	b0cf1d0ce374be0ba15c2d367214d44ed450c8ccea3b1484dd06b6cb578d9876
M	backend/tests/test_core_migration_baseline.py	59da77c910f89f3de025d1f2a58c835363a49f099bcfdad69cefc86f85e1f57b	1a53329909917acbbf206598d5a0336c92e094acf1c41ff9f0091e321357bba9
M	backend/tests/test_energy_price_migration.py	8de09226f8251f5eb24a2e7eee88e5c724d1cc7f7681c0a3119031edbe71d6fb	46767c5c7552a5e23db377886528f122eff253fb43abd9c69df0c380da484a79
M	backend/tests/test_equipment_temperature_migration.py	e3df459549089614365d712991855408db286d39394044f9fc7b1b4368059ce4	77e831eb9e444c1affc3bb1558d3a6be6a1e737c9f37012e83b6df85b37cd18b
A	backend/tests/test_legacy_acquisition_retirement.py	-	90e4f4c6d66d0df21a9c18f44df7eb8b0ffeb77342fb75573b9d0da84eccb13e
M	backend/tests/test_logging.py	99b646a451c22597e7672bc974c735d71ad0de03c834500049f8f8c09cb44ac3	8f5169855794d3acb828c3323605964863603376be59db5667a27a089c65ba68
M	backend/tests/test_mapping_migration.py	6cac3ca24586c8a50170bb75b2c7048d428b0d8e892975e2766d972c1beaee15	6d5bc289bcc2c8abf1324bdb0c4778b480a5cd34bbcd3c879279f7f345886d28
M	backend/tests/test_module_registry.py	d78781f9bba9133a524de90af41fd5257de1d6baf4ba0d0cadfc0624cdd273b6	ee55dd1f4dc73eb3ba935759418d640ba613d7695393118f30e197ac6605759b
M	backend/tests/test_openapi_router_tags.py	7b05a73dd27f4a3c1a7d140e440fee451f00b78e0a605df317def1de73c3200d	fe8e913eeb206fe9a3fce9a13874ddf85b7bff989d1be99454690bad2a7ee2e8
D	backend/tests/test_plc_facts_api.py	6e5846b3411d35f707628a7878ce8e5e5344aa7b62ad5f674eaf9b184f76bed9	-
D	backend/tests/test_plc_facts_compatibility.py	a59199a867fffed737f20ed93fb1dcb0fe12532a2531f0ccedacab2667fe1908	-
D	backend/tests/test_plc_facts_contract.py	e867628362d40a58b832bfa3313342ab6696604c367f3beda1c464d72f27dd49	-
D	backend/tests/test_plc_facts_cursor.py	caff312c0c0e2ef5b5cbf7b704a27aa387382d6c1ac47aa4dc43f0948ff6f6fc	-
D	backend/tests/test_plc_facts_maintenance.py	8411c164fd742aac59e3681ff7dd392462ec7b7d93dd5e74ceb0b3f85e91ffca	-
D	backend/tests/test_plc_facts_migration.py	972ac57918ea828cfd91dd8e2299eaa39c9969550900d5c156c7bacd5a90e321	-
D	backend/tests/test_plc_facts_ordering.py	c03cdafbff4bded33617e5676fe7ef85aa401449ecc924163192d6d158be76fc	-
D	backend/tests/test_plc_facts_retention.py	e7569f3aa2f3db5b12f216c877b08d415decfe9d3fc400a08f36ea8455052637	-
D	backend/tests/test_plc_facts_source.py	f5848c5fe5172590f3d5e1875371a4e578ac21f986af6ad332086a506161e5d0	-
M	backend/tests/test_plc_facts_v2.py	88f068467b8ebec440f3427be05f834a2bcb90e7d0ac586f74ce3706afeb607f	a9b863ea2dd597a43a31cb036bc81a1a87c90ce26db9b584cdcce3508b025e31
D	backend/tests/test_projection_control_plane_registration.py	9e888282a7a4d5cd1385f51079ced3065f75ae4723425da74f72a0668bf8413c	-
D	backend/tests/test_projection_failure_observability.py	f2bef8356ffe6d5831640fa4c5b1a9275119f93ff8f8c602cf92c0ff918e0fd4	-
D	backend/tests/test_projection_runtime.py	12963fdb1d8b3bfe9dd0cf933a47ab8ae30186576f4a0b6a48146bf9b4a26ae4	-
A	backend/tests_mysql/test_legacy_acquisition_retirement.py	-	7d0f22acb203a7a7ca783fcebe7fcf2f734d2307bd315278b8420c5a9b917e41
M	contracts/README.md	2a27befb2fc494f6cb0dce45e500340efb23e8e4342a86d0543472b1d183760d	7249e215e8f69506ecb34d3b634f7bad8fbfadda93dc41c6f07457aec4dc1763
M	contracts/README.zh-CN.md	12125df76c806c046a7802344000a0ae756338eaa2290a4b718df45aa2b95366	c460eb9a10ae4d8d81866cd980c15f5080e821749a21c37432abecadf99460a4
M	contracts/published/http-api/plc-facts-v1/README.md	2b2e24a0d14acbc0ae54f264b706b040848be3a88bbcb8c2a9ab82bbe0726b42	a38c69e9e42ab81d15e9b5f50c3cf9be618e3b9846653de3a4a79f3306344e33
M	contracts/published/http-api/plc-facts-v1/README.zh-CN.md	477af9f359ff049f2088f9eddfa6f0e127aa6d95f2afbd6a16498c8778f66487	7d8bc879feddc61ae7894dff31f266fe7486601ce8ea2f49067e887065745854
M	frontend-js/src/app/monitor/api/index.js	15d42eb7abc5f36d6cb9c9157e8bc54f264ba722eb3d176bba68a0b0cb27c1e3	aef3ce89fe1267ca3c3100f41b840ebf64f859c34a292c1761bf6b439ad6d5c7
M	frontend-js/src/app/monitor/api/mock.js	7999a1fb40ca3db096b27c56fb496426f71e6ead40371f50b7be83f57b5bf500	ef110eb60d4a7482df6889b4091af0e4e37a597557cf715f4cbd45782dc629ac
M	frontend-js/src/app/system/api/index.js	3679a8356ab97f3fdbf78e4b9c6b72bda85cc16ab335d64a6419b560672416e9	02345e5b6bf81cac876b14e13a21b14c4ef169cbfe646d9a67ca84ea7a6c67b6
D	frontend-js/src/app/system/api/projectionMapping.js	1f6dc184dfa2d0824afe9e6067f19d1bf4b99e850d4f5e8884d86f1838647a08	-
M	frontend-js/src/app/system/locales/en-US.json	dd93a6ace95a53603eb1c20cee3025d9ea19e210a714f4e95382d561aec7c89c	d4c50e562c286abd1ab190c3e80910fcbc4c568554d8ba5bac5648ab860f5a2d
M	frontend-js/src/app/system/locales/zh-CN.json	8a2494a7f5e22e92248e66125b0a66a3ae82ad115d6609bdf6eddb098be81075	64502a6036429086fa8997b7c078265e22d059d638f12041aba80f459eb692a7
M	frontend-js/src/app/system/manifest.js	e613eab2ec7405b746cfd12350efb41e48f9aeac9ba45bb94d6ba677e70796ec	b7473f8d073d931cee651943b8ff88a4c4034b83902f287735fe9a648fb553e3
D	frontend-js/src/app/system/views/dict/index.vue	40301a6b43a5d83ac61836f8535bd73c87e730df84ea8c17b5bfbd333175b6e1	-
M	frontend-js/src/locales/en-US/breadcrumb.json	6beceee1194032408ad6c8289dca240423c46c0204a05a61ce698e3352489310	67221d19010ce5a3797ae9aafbdac533a27923242f8cedf55fdba7a7a866d32c
M	frontend-js/src/locales/zh-CN/breadcrumb.json	7ba5328dfa759b547c85c7521b2b0544d0a3e2c8fa9941e6e29ea5642df342c8	334a6fd180de38f3bb1d896323b9eb8106556ea622d6ad6292baee3249b93762
M	frontend-js/tests/module-registry/page-access.test.mjs	d7f061e472c8bea7c4337f0bbfc4644c512c9ab8f25b41cdb8373d1b539f34ae	93688972891b8a0a8862fda5d794481708bc25a2d634f6282c46755071ebc19d
M	frontend-js/tests/module-registry/registry.test.mjs	e0b37f35b75048f5fcd802f4a70c2b6eb1093097d43897b68e1e7e8623cc6426	9e74a835a86f1639c840aceb7b57763e4faa60c312f38fd2f2509a5be4ba9ff0
```


## 候选可恢复归档与入口检查

- 候选的 71 个新增/修改公开文件与含 54 个删除项及正式树前置 SHA 的完整清单已另存于忽略项 `backend/data/maintenance-evidence/arch-acq002-r2-history/arch-acq002-r2-staged-changes.tar.gz`，SHA-256 `4fecdcba43f9c8b9c1c67a47c19ea491262fed42c1522721c85eca8b9b541e64`。独立 TSV `arch-acq002-r2-staged-changes.tsv` SHA-256 `2e6fc149c8f8d6ad07859ad1d3c714ad493a05cbd50f17613abf4a76eb569b9f`。归档前核对 125 个前置/候选散列，归档后逐项核对 71 个文件及 54 个删除记录；仅 `.env*.example` 为公开示例，无实际 dotenv、私有配置、凭据、日志或运行数据。
- 归档的 `staged/` 是**变更集而非完整运行树**。下一轮先校验归档与 TSV 摘要，在新建的私有公开源码副本中按每项正式树前置 SHA 合并；重新叠加已批准 FE-005 变更、同步共享索引并完整验证。禁止用归档整目录覆盖工作树，删除项只有在调用方门槛、目标基线和维护窗口均满足后才由协调者安排正式整合。
- 隔离 MySQL 测试的源码导入护栏会在连接前核对 `settings`、`database` 和 `app` 都来自当前公开候选；pytest 启动必须将 `PYTHONPATH` 显式指向该候选的 `backend`。合成配置下运行 `run_mysql_fixture.py ... --collect-only`，3 项成功收集、exit 0、未执行 fixture/连接；去掉候选 `PYTHONPATH` 时按预期拒绝。原禁止 3307 的负向检查同样在连接前拒绝。
- 实际执行时提供显式 `ARCH_ACQ002_FIXTURE_ROUND=dev`、`ARCH_ACQ002_FIXTURE_PORT`、`ARCH_ACQ002_FIXTURE_UUID`、`ARCH_ACQ002_SCHEMA_EMPTY`、`ARCH_ACQ002_SCHEMA_UPGRADE`、`ARCH_ACQ002_SCHEMA_GUARD`、`ARCH_ACQ002_FIXTURE_ACK=ACQ002:dev:<uuid>:<port>:<empty>:<upgrade>:<guard>`，以及对应 loopback `MYSQL_HOST`/`MYSQL_PORT`、非 root `MYSQL_USER`/`MYSQL_PASSWORD`、不同于三库的 `MYSQL_DATABASE` 和 `TESTING=True`。独占 schema 必须匹配 `arch_acq002_dev_...`，为空且互不相同。用私有文件传凭据，不在终端回显。项目依赖使用 `uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider tests_mysql/test_legacy_acquisition_retirement.py`；Dev/QA 的实际隔离目标须分别完成批准及身份校验。


## 2026-11-11 恢复 Development 与隔离 MySQL 实测

- Human Owner 于上海时间 2026-11-11 明确批准 Development/Verification 各自的一次性 MySQL 8.4.6 夹具，分别仅绑定 loopback 13393/13394、验证后回收，并批准隔离验证通过后按本任务预检用 Alembic 清退指定 3307 dev 九表；DAA 不变。当前 Development 只使用 13393，13394 未使用，3307 由协调者管控；历史 `needs_input` 停点保留为当时记录。
- 恢复时重核 spec SHA-256 `79d35e149dd9d8159cd1ccb5ee461fdcb8cfa299d6a7931928f291ac74e42394`、HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 及前一候选/历史归档摘要。125 个正式前置路径和归档内 71 个新增/修改文件逐项一致，漂移 0。并行 FE-005 的 12 个公开源码/测试文件只读叠加进隔离候选，逐项与正式树一致；不纳入 ACQ-002 修改或复制清单。
- 夹具为 `127.0.0.1:13393`，MySQL `8.4.6`，会话上海偏移 +28800；`arch_acq002_dev_r2_empty`、`arch_acq002_dev_r2_upgrade`、`arch_acq002_dev_r2_guard` 为独占合成库，账号非 root。协调者私有记录 server UUID 与容器身份，分别对其原值计算 SHA-256 为 `4180fe0a60aaace4729a8837867759702c77e2642b14421a6172b126817d3e65`、`7ad5289fa3c24c68b02d7daa44e65f4e84c6ba8f350bf803a65f71f9870f6a3b`；凭据未进入公开记录。
- `python3 /private/tmp/arch-acq002-r2-dev-h8rW0pBF/run_mysql_fixture.py /private/tmp/arch-acq002-r2-coord-dPORAa/fixture-dev.json` 在项目 `uv run --offline --frozen --no-sync` 和显式候选 `PYTHONPATH` 下执行。首次沙箱网络限制在连接前报 `PermissionError: Operation not permitted`，pytest 3 setup errors、exit 1，没有 DDL；根据已批准范围通过沙箱外执行后，第一、第二轮各 **2 passed / 1 failed**，恢复表 SHOW CREATE 的差异被如实保留。协调者每轮仅重置上述三个测试库，其他库未触及。
- 第二轮捕获的真实差异仅为四张表共 19 处在 `COLLATE utf8mb4_unicode_ci` 前显式增加 `CHARACTER SET utf8mb4`：两张快照各 6，`plc_facts_batches` 2，`plc_facts_stream_state` 5；除这唯一片段外原始 SQL 字节一致。diff SHA-256 `9c1aa2724b0070783529a71719182009b116347071a112cbe35cdc6341a9afe1`。修正**隔离测试**以核验数据库中该排序规则确属 `utf8mb4`，并在仅归一这一冗余字符集声明后比较完整 DDL，同时逐项对比 information_schema 的表引擎/行格式/排序规则、列类型/默认/字符集/排序规则、索引、约束、CHECK 表达式和引用；其他差异继续失败，没有更改旧 migration 或迁移实现。
- 第三轮全矩阵 **3 passed，exit 0，35.49 s**。空库根迁移至唯一 `3d5f7a9c1e23`、合成旧库 `2c4e6a8b0d12` 的 77→68、受保护表结构/行数/checksum 与合成 v2/Projection 旧值守恒均通过。旧凭据在三个业务 owner 因 revision 不符被拒；同目标新凭据在真实 async Service/CRUD 和隔离数据库完成八路写入与旧永久回执重放。v2 五路通过 in-process ASGI 与隔离数据库验证写入、重复、冲突、四类查询、scope/default-off/旧目标拒绝及 cleanup。检查非空旧表、可见依赖、错误 UUID 和有界锁等待均拒绝 DDL；合成故障注入观察前驱 2c4/九表全无、无证据重跑拒绝，再经同迁移受控入口登记后继 3d5/九表全无，且保留对象对账一致。隔离恢复的九张空表 metadata 前后 SHA-256 同为 `15c9e016426e521712fdde87e606f753bfa07d5476fa77639be12062d31aab5c`，归一完整 DDL 摘要同为 `cc9250d3cecd4420242f4ff597f0902dd78f119cd24ff54d2337e58dc498b954`。
- 仅合成 DDL 差异及恢复证明归档为忽略项 `backend/data/maintenance-evidence/arch-acq002-r2-history/arch-acq002-r2-mysql-proof-20261111.tar.gz`，11 个文件，SHA-256 `84d404e40487a068443d4d836d80702043f86529b7a0ef11df2ce3e4f842c292`。其中恢复证明 JSON SHA-256 `adefb6a50ab3e2b1f0be63a9d8745bc802c1a8f6fa2b25e897b79da5328e0b87`。这是隔离合成证据；真实 dev 的九表恢复仍须使用其实际备份另行在隔离目标证明。
- FE-005 与清退联合隔离候选 `pnpm --config.verify-deps-before-run=false run check:modules` exit 0（10 groups、24 routes），`... run test:modules` **50 passed**，`... run build` exit 0；仍报告既有大 vendor chunk 提示。
- 相对 11-10 已保存候选，仅 `backend/tests_mysql/test_legacy_acquisition_retirement.py` 更新，当前 SHA-256 `551e1c3cfa5f94358bb5ea56677d6929cae16ac0ea2db12ac51de19763a32a51`；125 项最新正式前置/候选 TSV SHA-256 `b1b03ab0468b85b34b83a15899ef226f5e24c8ad549f6f4e1f531cae671184d5`。新的公开候选归档 `backend/data/maintenance-evidence/arch-acq002-r2-history/arch-acq002-r2-postmysql-20261111.tar.gz` SHA-256 `26be6c6c52993fd4e899173e9e7e6d6d4f18302ba2657514ab9d76a8dad622c2`；配套 TSV 为上述摘要。保留原归档与其完整清单供历史追溯，新增归档逐项复核 71 个文件和 54 个删除记录，未包含私有 dotenv、凭据、日志或运行数据。
- 协调者报告 3307 当前正式只读预检：MySQL 身份与 v2 profile 相符、唯一 2c4/77 表、九表均空、85 条可见外键无旧表依赖、无非系统视图/触发器/routine/event；已识别 8000 backend 与 DBX 的空闲连接，无未决事务，14 条旧路由、四条 v2 GET 与 collector 当时均 200。这是协调者的只读预检，执行前必须再核对完整可见性、同库写入方、可控重连、现场备份和维护窗口。
- 预备整合脚本 `/private/tmp/arch-acq002-r2-dev-h8rW0pBF/integrate_candidate.py` SHA-256 `a3f983ea09ea878ec40c6be1d24d4d4d1e5da2de4fc6bcd8b5eaa1e3aa2a3999`；无参数只读核对 125 项正式前置和候选 SHA，exit 0。必须由协调者确认 8000 已暂停及维护窗口 `go` 才能逐文件整合，脚本不改变 CODE_INDEX 或 FE-005 文件；逐项记录操作并校验目标，异常不自动回滚。本条不是正式整合或 developer_handoff。

## 2026-11-11 指定 dev 恢复演练、正式整合与切换

- 协调者用指定 dev 的**实际九张空表备份 DDL** 在 13393 独占 guard 库复建，9/9 `SHOW CREATE` 与备份逐字一致、九表均空；实际备份与复建 metadata SHA-256 均为 `08af2aca6c75e3e5b6ff10fe4ac1a1c05e9c3dacc3d0b281a70040c9ef3ad20a`，逐项覆盖 167 列、67 索引行、26 约束/引用和 11 CHECK。记录 `backend/data/maintenance-evidence/arch-acq002-r2-history/dev-3307-20261111/restore-rehearsal.json` SHA-256 `4253073ae6103e8feeb88acfdf5f145b7185ad78d2d7184b47ae1136d4fa1511`；备份 `dev-old-nine-empty-tables.sql` SHA-256 `0f4b65671bcd2afd325aed13aafd66e3c5ecdee76b4bdf3db140f807cf6a5b4f`。该演练不等于真实 dev 已恢复；实际恢复仍须分别授权。
- 协调者确认 8000 原 reloader PID 50794、worker PID 50796 已暂停，3307 前驱/表/依赖和连接重核通过后下达同窗口 `go`。Development 执行逐文件整合入口，125 项 A3/M68/D54 前置与候选 SHA 复核、应用和最终逐项验证均通过，exit 0；无目录覆盖、无自动回滚，FE-005 与共用 `CODE_INDEX.md` 未被该脚本覆盖。实际操作清单已持久化到同证据目录 `integration-operations.jsonl`，125 行，SHA-256 `8b7608160b0f56aebd288692c7e5bc72b9acbfc667c954fbd1a5b9726a12264e`。正式 HEAD 仍为 `bcafa89fa31bdf62329bced89baebc193323a739`，交付为当前未提交工作树，不是 commit。
- 协调者于上海时间 2026-11-11 08:18:36，在已核对的 `127.0.0.1:3307` MySQL 8.4.6、schema `industrial_level_2_system` 执行 `uv run --offline --frozen --no-sync alembic upgrade 3d5f7a9c1e23`，exit 0。目标的唯一 revision `2c4e6a8b0d12 → 3d5f7a9c1e23`，应用表 `77 → 68`，固定九表均不存在；未使用手工 DROP/stamp 或关闭外键检查。该操作由协调者执行，Development 未自行连接 3307 写入。
- 同窗口私有 v2 profile 仅原子修改 `target.schemaRevision`，原文件权限保持；前/后 SHA-256 分别为 `a0a0a8723008287c2cde931f8413ae1ae1c14d5840907cc6f184d0aab4a1f68b` / `2179386159122eb1d888b1f220cf3d16a10c389fa6cb080b513cc64707975f52`，排除该单键后的摘要均为 `b28e0103fe3cac9adfa6938f16d7d0f00c0960ca960cc9d491ff87fc6a06e489`。目标 server UUID 前/后脱敏 SHA-256 均为 `3615b4f7af6be31eb03e5b5b096e504d645bfbd4d84b6837aaa8cca2d51ab94f`；未公开私有 profile 内容或凭据。
- 68 张保留表结构/行数摘要前后均为 `b7787f6958a25bc01d688a4495381667ec7c2d65f0fa373d3ad88dc7f3dabf27`，保留对象摘要均为 `455072696435b6aa0ec8a51b9d5dd47ec8afd98b4b423f40c1d491a6a8107752`。v2 samples 与 latest 各 2 行；对应内容摘要前后分别为 `df14f8ef31a6382f933e52350494c2fdcb3e47fb6503a8207acad30037b075ea` 和 `40e7c677e0b1f7900d8ce55ac74418be6c8833aa7bcd999fe462491b5a048b86`，结构摘要均保持。`dev-before.json` / `dev-after.json` SHA-256 分别为 `6c45f046dfe2c6624d608d708da68633cca5c2193c4afe8bd2877877c847baca` / `ddb596428e67e66eaffe1e6bf224d90cbefd80cd480f45d98953c9068e956682`，均在上述 ignored 证据目录。
- 协调者确认原 reloader PID 50794 恢复，worker 从 50796 换为 88626，仍在 `127.0.0.1:8000`；四个 v2 GET 和 collector 前后均为 200，四 GET 响应摘要前后均为 `cf6215aa43e30a2a11503aa4645a7db6fd5a3b8ae95b982a2f749a8394626041`，原 14 条旧 route 数量从 14 变 0。实际 v2 新写、过期清理和 BE-010 写入/回执只在隔离合成夹具执行。13393 已由协调者回收，13394 留作独立 Verification，不代表该轮已完成。
- 正式交付树复核：最终 125 项与最新 post-MySQL manifest 逐项一致；并行 FE-005 的 12 个源码/测试文件与联合验证候选一致；9 个历史 Alembic 版本逐字节不变。38 个变更 Python 文件内存编译、4 个 JSON 解析、20 个文档的 198 个相对路径检查均通过；`git diff --check` exit 0。正式源码在合成配置、禁网络/SQLite 与正式 `.env` 禁读审计下定向 `pytest -q --tb=short --show-capture=no -p no:cacheprovider` 为 **147 passed、3 个历史 profile skipped，exit 0**；历史断言、全量 no-db 的 6 项已知失败与验证边界见上文。正式前端 `check:modules` 与 `test:modules` 为 **50 passed、exit 0**；隔离联合候选 build exit 0。


## 最终正式工作树改动清单

以下为本任务实际整合到正式工作树的精确 125 路径和前/后 SHA-256（`-` 表示不存在）；与 `arch-acq002-r2-postmysql-20261111.tsv` 逐项一致。前面的 11-10 清单为保留历史，测试文件后续因隔离复建差异诊断和严格 metadata 等价验证发生了有记录的变更。并行 FE-005、DAA、SMA、冻结 CA 和协调者负责的 `CODE_INDEX.md` 不计入这 125 项。

```text
M	README.md	174e8ac63197c26f84666b3f78c6ab10014b90763eac518b8f830bd6231385c4	e6bcc9e1bd2c7aa1eab3a0592a6e7585292b477e20a18a5d820d245a591b2dce
M	README.zh-CN.md	b8cdc833cf395abb3dd6d9677cb380cee2512a3ed97655050959d2cf165487ae	45f5176b66e912e823e9081baf81ca94097d315761271bc2572ef7fae988c3bf
M	backend/.env.docker.dev.example	ea2886aa84c88b28d019ea3518c5714eca43c45efc7310862674c324569d1800	67a1d8710d368ea295afc0643c38447cc96133fd1482c2178ce0417c72fae433
M	backend/.env.docker.prod.example	54c3fc39f69833c9f49e9c4d71e22ef2282a84b25f3c633dc3d5b12a0afb8c7c	4b4312bc06b614cb1cd31c7134ccfdb9afa210f58e5c47af0ecd7479bd33ac6a
M	backend/.env.example	33021261d511c17930445c8d0ff9596cd5b645dc1d3e8c1250ba7fed7a5e6bf9	7a0da42671a48b3334f59d51605bc2939604fc7c0755c05c995ffc8b86d7a794
M	backend/README.md	44818a8189a86e893fbdc078b21869bcabbc36d5136d79e7485ffc9ff26b0956	49e8e4eec550d81c5a8ace04adb4caa21bb94419aefd630f3e093bb31c5cf02f
M	backend/README.zh-CN.md	bf810beb28285a231fce3a3d5e9a044b61b5032d99c2e39ae585efc093fa3ad7	32b66919995dfe7982427d577e6594b7b4bcec5accfd1337f87246d47bc9746a
M	backend/alembic/env.py	6e4195c922c06946f217e344fa41d105875d60e7a7925c374fab4cab0ce5d2e5	d15288cd684a05d86906af56504dbf9765a5139669e8a1cefad8c335cc9418d5
A	backend/alembic/versions/20261110_2215_3d5f7a9c1e23_retire_legacy_acquisition.py	-	337ea1530f379e6076d784757572ae56be25752c5f039e41ff84bddbc66591d5
M	backend/app/MODULE_CONTRACT.md	59df0919940179652d8e6719ee74d2e31e0bbcdb9d91f431690e54249b73b4fd	67799004be3174ddf9f70d6dde01a620cdbbc1b59fb28b3b0e1bd5ddc54ecd49
M	backend/app/MODULE_CONTRACT.zh-CN.md	14a6b3cf0d49133c6664cd234835f375f5113f243c0b398be489d076e87e57e1	15cd536cd9e1339c37d6f06cac50e04f8cfd0ceff71f546bdb6d806ec791c787
M	backend/app/README.md	13c2171a32930fa69bb9e40bff63988d27544d480901139cd4d5be74c1a067da	b0a36169c0b22279d72bcbc7ea11d0241b69f11468d884f82f1beb242453a386
M	backend/app/README.zh-CN.md	eeb606e726592326e1d109e7d2222d15f46c365b60203103a08ece93febdc9b8	d9099e1198df08c459cb7ced2a4eacca2587cf4dbd5141cc1454e40da5f22c69
M	backend/app/module_contract.py	d91c98d46f526af8e87502685833dd00570f45c090c40949938ae689cfd84778	2c28724c7f4f34426e3c000f276f8dcb0b0b8ab16c79e4f75b970e1684253e75
M	backend/app/module_registry.py	de6c73d49a988de66a8d49617e78679176b2ebf3459f93cfc348610244a260ab	d055822e1e3866ef6e64e0d166e1e74d9158c0c37d7b6a8f14656118b439f711
M	backend/app/monitor/README.md	cc47ae0ada0301e6be7e47c01bef90d136742f2cdf11e98c78b8c3ea55139a2c	82429bcce197ec6dd114f64fd9f7818bb0c81a9b4f304a0df4f84071a492a29a
M	backend/app/monitor/README.zh-CN.md	72be0c1d0b2896796ba669f3481b9448d083a05de42d68b9217101a020927db5	8376758df08447424ab43696a86624af7f192b284779f92ec42744d574f02c5d
D	backend/app/monitor/api/realtime.py	cf0d4e6b3f5ece1a0383b76e365fdfae245cf05550ba43cf368f108349464773	-
M	backend/app/monitor/api/routes.py	ff15b5e30c3907e9313e1147ac491675f15aa375055cf54c5342f028e591538f	a2a8210a6f4a44bac601da2f65cad7fe9e39183d5f3031779274b5a3db0d6b9e
D	backend/app/monitor/crud/async_realtime.py	c8b8d47a1b56f08e6c7bc9237c8cba69f348f6cb343e8670abb83c8c472db38a	-
M	backend/app/monitor/manifest.py	571e95bcf0867318d817d0ef57c185c39cf649f9730260254b484f722ef3034d	46f48e7022dadf43507b5fd5821fa35c9becc46d8f930728cff6dacf1e9f15bb
M	backend/app/monitor/models/__init__.py	f0d8df47e2e9ef028e1f0d6779e97dc92bea82b8edfa619019bd3696d336d7af	554bbea9a380b5968efda2d79dc82965ba44f9f05f928b17c3b455d5002cadf5
M	backend/app/monitor/models/monitor.py	5ca4b558469b7d4f96dd838b50b1128d349ccb6515c071bf5c3bc45cfbe58521	0885e75bba793d0ba0d282e5a27b195d99dbc06662fa0b42662d3b4a94a0828c
M	backend/app/monitor/schemas/__init__.py	7391a35dc4d4a7bb845e539732468fc01868a37078538bcc1915a40935d37665	3b037cd93c6d2f50c22720a80ccce89cb0261e3efb4838d698ea880b1d88b8dc
D	backend/app/monitor/schemas/realtime.py	f0ef917714ef327a83e9a822cbdfb3394e1c80763715d71e3c3f9f5217574111	-
D	backend/app/monitor/services/async_realtime.py	830f7a4e4d612bc7ceace233fdf90fac833a3fa84e524df5491e26fc8d8064a4	-
M	backend/app/plc_facts/README.md	c714086d5d9aca44b221ff096f33fd3bea56d9e594405871cf206ed51dc99a7b	dca3ad3c3cf173c7df1f1ea744e3a1c7cf52f1df6af0f16f62cbe2947bd39640
M	backend/app/plc_facts/README.zh-CN.md	88867ef7cfcc6e2a07bed7682e59be2a99d4b42253038df243b95bd12efc03a4	031286299bc3408798a1b354037aec287a16d294ebdbf73c6f177b82e8b70d9d
D	backend/app/plc_facts/api/batches.py	b08081c5486b3463164b8a8b384d972ce01c57fab56ee90a8ed97ff03ceec524	-
D	backend/app/plc_facts/api/dependencies.py	ee80d94d5e65bb8bb2c2c758044fec359057f0a3b02a7458052c592db7fae2a8	-
D	backend/app/plc_facts/api/history.py	3ade3187a476859d806d58d52d28e4595bcbd374d479176bee49ca343a4490fe	-
D	backend/app/plc_facts/api/http.py	4664f4c6315aa1b0f46f24a8193860558085c12664c1016b1f7efbcf10ee4c27	-
D	backend/app/plc_facts/api/latest.py	798f3f88f55d7568f9f9d5742769a333eabe7223069cc5d0c5c204fee0624fd8	-
D	backend/app/plc_facts/api/routes.py	b73df8fc9570d8cdfaf33c58dd1ae2bad5452f7c715c51ba69504b144b0379b8	-
D	backend/app/plc_facts/canonical.py	c48f0957b65c4348dec4fdfd8d76d9bd29891355b302b4d189b81cad7bbf1cd9	-
D	backend/app/plc_facts/config.py	7f498a16a316d94a21cf28dd1572b3c044883910c0e16de2ca0ac79c40374577	-
D	backend/app/plc_facts/crud/async_ingest.py	2e087d3b5466630e41358c0c24b0b15a7dac4f1aba7721491995ca81a2e131aa	-
D	backend/app/plc_facts/crud/async_query.py	86686afb7ef383f9bc702e374b20eced4306b5c8184c0646de00ff3745bb6645	-
D	backend/app/plc_facts/crud/sync_maintenance.py	059a6677f8430b24e310feddecad8e64ba22d83be0ab0e8ff3bd56a293bb0c24	-
D	backend/app/plc_facts/cursors.py	e1bf72ffb13a32e096418275054222e95a455f46eca1b6e412644f90cbc9f783	-
D	backend/app/plc_facts/error_codes.py	8529c74ec787137f508e29fae4c8afcad51bb2ca9d63908fde30edb59b1824ce	-
M	backend/app/plc_facts/manifest.py	358f77c2405322fc20bd5415b2406bb492385f11e0d012e34a3b22255eafced9	54fc73b417aaa8153e1a1e6feb8b104d05728fba0c4d03a5b12be654f2ccfd51
M	backend/app/plc_facts/models/__init__.py	e6738175c336bda4f11f228fc43b8f6de7571cda331c45ae4aea2edc2dba74ea	f3f21e21fdda181915452b67c7ef13b083d613154b385a2310d8e055a4e41f4c
D	backend/app/plc_facts/models/facts.py	920e89c963190bef00edb6c06d0195a93afa38cbb876c9edc946f3e3c203b89f	-
D	backend/app/plc_facts/models/receipts.py	880e98b0cc2a3440e0c139c47d03369fe5937d79afef85d09e5e8018413deda1	-
D	backend/app/plc_facts/models/state.py	104bedf1907a325decc54e1f041ff31d1a723434f35a38331515f398e2aa3d0d	-
D	backend/app/plc_facts/retention.py	f73c302c1196eaeeaf521de73bbd220a9466b8e2666f2aaa51e78fc01d591e9d	-
D	backend/app/plc_facts/schemas/batch_in.py	a0a625433a76c9b39a7009a04579ca02f9844c119679ba9a533ff678dbcbc69b	-
D	backend/app/plc_facts/schemas/query.py	1689676876f6f5b360ccac23769a56da6a7b3f926bd5f90d0c4af385254671cf	-
D	backend/app/plc_facts/schemas/read_out.py	4b8c421e993d9977f652e1f74fd2904837cacbd91a1136cf32c0d082259e2ad9	-
D	backend/app/plc_facts/schemas/receipt_out.py	14d37df54acbef48fe55eedc9d26b1c3512a422f9f4bdaac45b304b651979e40	-
D	backend/app/plc_facts/schemas/source.py	1c3726df2f8b73761e1b0aff61323ed5452911ab941df3065ae5e35f60f9e639	-
D	backend/app/plc_facts/services/async_ingest.py	91b15e1842847db6612fc83753a9a9fac2caaa44a57c655ee223a12685a9a60f	-
D	backend/app/plc_facts/services/async_query.py	7755a9537779afa4ee05615686282de831e0451fc02fe77948479e46d46b383e	-
D	backend/app/plc_facts/services/sync_maintenance.py	3e138ae817c49a20243cf8c6df0c5df57ffc2e91248171956a5f29d28798ff61	-
D	backend/app/plc_facts/source.py	a7fd7ef75149e251a47d838fbd57db00c540c7990d1f64f3d9e9a67edc1489d8	-
M	backend/app/plc_facts/v2_config.py	8a7d27cc40eb090fcc3374e74576d545e216881f607429bb62b501ee5e02cd60	2cfcc8957a945769a6e5dc178dca8eff0d022956244b519ea8d1f066751967e3
D	backend/app/system/api/projection_mapping.py	4783d6a5d112c9bcf768944725a88452798ab877da09b0562994bc8cb64d1589	-
D	backend/app/system/crud/async_projection_mapping.py	58b84727175e5fc97bf18c7eb9f73a06879c27a2f40d26959fb851335c97319e	-
M	backend/app/system/manifest.py	a538991218b29bedb465ae75b8df949e128dbf091c5d7d915ca2d0a324ab1f5f	275c3dee481402a2b888da5f5e55ad6dcf842a9696ae44ad509a7ba4766b0bdf
D	backend/app/system/schemas/projection_mapping.py	775886cc86d883679c4c3d6aa1fb10155f7fca5d8cd3e019724d9dd85d2d1b09	-
D	backend/app/system/services/async_projection_mapping.py	478643849bce3d197bec303ffacbc4d9a821ac7980deabaf0034eb3669ea972d	-
M	backend/common/error_codes.py	90db8c6e452b992a77aa14c507d354ec77b4c7e3e112d05742b7f681ddacae35	72d4259da29c1bdcb146804fc7de3f913d8434eaaa4841060c68db7247fc1933
M	backend/common/integration/storage.py	ce1ebfb113b826300d15d34a3ab4ba083cd6f6be9b2808028e5770244d912362	7ce719f7f309c6a246192cd090ee373b5dcf88f15f7e961135f0cf5d7b4eaaa3
M	backend/common/log.py	da77925fd582e8ae65565d905b393d383f6282e8afb45911125101a379c64bc4	d9d25da2d787f75a286f21f5d7433c1da36064159447ead9f3fe61b0a15587b6
M	backend/core/registrar.py	b52e86b8c6b617607cc9dc26b35e7e8fcd6264cb333bad5f55578c97ac0d30f8	274612b5c15ef386f8491d99632adc3fe7645507c04c3578b6abc63119ecc2e4
M	backend/projection/__init__.py	a89c1ce75f2b56efb64960739deea084b6fff3a3f5fa67af279679d3102660e1	8c8081577a9ce8882f952e89e606f21d6415d7b09c422020e5695a732f41e8c2
D	backend/projection/failure_observability.py	29279ecaf3becbf5094ed92f811480d22ac71bd353a8172504a4392e33aadf00	-
D	backend/projection/input_resolver.py	61c0b098390ea5c95ebf31cc7cc3cf0d04b771fe6c21592ca6763f4f85696981	-
D	backend/projection/policy_catalog.py	605cd1aa578b9271c7318d8cf7a5a4f326abf003a205405ff323b4ba753124bc	-
M	backend/projection/registry.py	cc222d301879da3850262e5aa3f6e979f735d9f87f058d7b519e2d5d4c68d502	fdc3bdad4041066d8f22c9551e56b7873543e8d5c562a1ebb041d041d1dfd90b
D	backend/projection/runner.py	d2ebb20e0f1c6f7a7616b657d40ea11327fc58fa0e64972ff77f38fd7c648e98	-
D	backend/projection/runtime.py	8c0bc50c649dc2c91932002a94463e205f13609beb6d2001489e1488d618bc65	-
M	backend/scripts/business_time_adoption/README.md	c5af6cad7d8825b996f1557fed529d7028ed05e76c6e765c2aae8e60e87d0e3d	6de7acc07c7a9f406a237ff030f408132cd7d22b244ce13431b5c65603dc1ecb
M	backend/scripts/business_time_adoption/README.zh-CN.md	13a8222d190ebea93c588d44bb60e9d6afc31404b32eb06bc39fe85564450032	ad5ad99df80ea89ceb0e15b95207bc6d4510e55c516c79da400f7a4ae6720207
M	backend/scripts/plc_facts_maintenance/README.md	0b43546e1fa7ee1142b92fc1b5a472c8878ca0c8747ba63fa23773fcc7070166	53bdf5bc27cc8e9f312f7b6ebac7b6e723a0250b7d3ee41f63402f76136075ff
M	backend/scripts/plc_facts_maintenance/README.zh-CN.md	8025ccb669e80ab157bf0954758888800bfbdc0abb96dd44a2e84e341fe31e51	638f25aeb183fb787080e2c89ecd766ee111fa4d2ca48bb385a333ebd10e580d
M	backend/scripts/plc_facts_maintenance/main.py	f71e81f308f862461e791cf30c9c95ca07967c523cfe82f2fbffd11fa90b1ec0	bbb4f20b33b24f0d5b612729fa65766d672800f0b17eb2746fb6aa54bee7306e
M	backend/settings.py	b8d30d4fdb252de5b69d8e386574b6b68ce4d8d8fb9e07055117f9b5a08aefd5	048e1a9451d35a83dc78fd580f4133300481c827139ed6303d028fa51e6d34ab
D	backend/tests/app/monitor/test_realtime.py	516a0ebe9310517edb7f0bbe021b6d2234cdc7ba3e9feb800b36633017f50ce6	-
M	backend/tests/module_admission_fixtures.py	cd3c399657aaf5444d2fd718192016c7df6f76db87985bdd2fbfa8aa9786ecc9	842638ac8784c1bc5124b4c0dfd5c72ad127690436724035196ed4f61247016a
M	backend/tests/test_aiis_demo_module.py	aeb568ba544e478f791d0cf092b8dbe911a6ffc7afcc423994244c764fabfb6f	fae3dc3af1bc12e2bcc04274fd88baf7e914d5202f4ca391681e9d678a592c3c
M	backend/tests/test_business_integration_compatibility.py	8ee66757ed69bb792a357ed06be257e0b1ffa56ce68be82f749fe5b4b364f354	878a6625d750a50afaa2f44e71b75dc3e86e0d5c34bc1d3da1526229740bc6bf
M	backend/tests/test_business_integration_migration.py	455e73a14c9ef6e2336215daef488efe136e6ae6a7e9e8b750bd519476a6df95	d15f8d9dad880b0baa6290788ff331bb9bbeb4944f7959019106fdc551e58379
M	backend/tests/test_business_integration_storage.py	70c5e69c3bdb4587cc23b7c20a0cccfeec8d33f50125a648ee3445a662c226df	f012565f959751d8f855a011992cb8e3b0f0781a0b0470a0cc2508a212893244
M	backend/tests/test_business_module_migration.py	bcc639d0b474178851733ae65c5624a5c37320b538d4d5d86ce0b006e67a7fe9	2c00593e3a40fcdede096272d8a0b2a98fd30fd954e6cf72411d3a902079d68b
M	backend/tests/test_business_module_reintegration.py	6524b111d2ee86c9dbdc8518d56caa1483b20358bfc8d722e49d3040c9188433	b0cf1d0ce374be0ba15c2d367214d44ed450c8ccea3b1484dd06b6cb578d9876
M	backend/tests/test_core_migration_baseline.py	59da77c910f89f3de025d1f2a58c835363a49f099bcfdad69cefc86f85e1f57b	1a53329909917acbbf206598d5a0336c92e094acf1c41ff9f0091e321357bba9
M	backend/tests/test_energy_price_migration.py	8de09226f8251f5eb24a2e7eee88e5c724d1cc7f7681c0a3119031edbe71d6fb	46767c5c7552a5e23db377886528f122eff253fb43abd9c69df0c380da484a79
M	backend/tests/test_equipment_temperature_migration.py	e3df459549089614365d712991855408db286d39394044f9fc7b1b4368059ce4	77e831eb9e444c1affc3bb1558d3a6be6a1e737c9f37012e83b6df85b37cd18b
A	backend/tests/test_legacy_acquisition_retirement.py	-	90e4f4c6d66d0df21a9c18f44df7eb8b0ffeb77342fb75573b9d0da84eccb13e
M	backend/tests/test_logging.py	99b646a451c22597e7672bc974c735d71ad0de03c834500049f8f8c09cb44ac3	8f5169855794d3acb828c3323605964863603376be59db5667a27a089c65ba68
M	backend/tests/test_mapping_migration.py	6cac3ca24586c8a50170bb75b2c7048d428b0d8e892975e2766d972c1beaee15	6d5bc289bcc2c8abf1324bdb0c4778b480a5cd34bbcd3c879279f7f345886d28
M	backend/tests/test_module_registry.py	d78781f9bba9133a524de90af41fd5257de1d6baf4ba0d0cadfc0624cdd273b6	ee55dd1f4dc73eb3ba935759418d640ba613d7695393118f30e197ac6605759b
M	backend/tests/test_openapi_router_tags.py	7b05a73dd27f4a3c1a7d140e440fee451f00b78e0a605df317def1de73c3200d	fe8e913eeb206fe9a3fce9a13874ddf85b7bff989d1be99454690bad2a7ee2e8
D	backend/tests/test_plc_facts_api.py	6e5846b3411d35f707628a7878ce8e5e5344aa7b62ad5f674eaf9b184f76bed9	-
D	backend/tests/test_plc_facts_compatibility.py	a59199a867fffed737f20ed93fb1dcb0fe12532a2531f0ccedacab2667fe1908	-
D	backend/tests/test_plc_facts_contract.py	e867628362d40a58b832bfa3313342ab6696604c367f3beda1c464d72f27dd49	-
D	backend/tests/test_plc_facts_cursor.py	caff312c0c0e2ef5b5cbf7b704a27aa387382d6c1ac47aa4dc43f0948ff6f6fc	-
D	backend/tests/test_plc_facts_maintenance.py	8411c164fd742aac59e3681ff7dd392462ec7b7d93dd5e74ceb0b3f85e91ffca	-
D	backend/tests/test_plc_facts_migration.py	972ac57918ea828cfd91dd8e2299eaa39c9969550900d5c156c7bacd5a90e321	-
D	backend/tests/test_plc_facts_ordering.py	c03cdafbff4bded33617e5676fe7ef85aa401449ecc924163192d6d158be76fc	-
D	backend/tests/test_plc_facts_retention.py	e7569f3aa2f3db5b12f216c877b08d415decfe9d3fc400a08f36ea8455052637	-
D	backend/tests/test_plc_facts_source.py	f5848c5fe5172590f3d5e1875371a4e578ac21f986af6ad332086a506161e5d0	-
M	backend/tests/test_plc_facts_v2.py	88f068467b8ebec440f3427be05f834a2bcb90e7d0ac586f74ce3706afeb607f	a9b863ea2dd597a43a31cb036bc81a1a87c90ce26db9b584cdcce3508b025e31
D	backend/tests/test_projection_control_plane_registration.py	9e888282a7a4d5cd1385f51079ced3065f75ae4723425da74f72a0668bf8413c	-
D	backend/tests/test_projection_failure_observability.py	f2bef8356ffe6d5831640fa4c5b1a9275119f93ff8f8c602cf92c0ff918e0fd4	-
D	backend/tests/test_projection_runtime.py	12963fdb1d8b3bfe9dd0cf933a47ab8ae30186576f4a0b6a48146bf9b4a26ae4	-
A	backend/tests_mysql/test_legacy_acquisition_retirement.py	-	551e1c3cfa5f94358bb5ea56677d6929cae16ac0ea2db12ac51de19763a32a51
M	contracts/README.md	2a27befb2fc494f6cb0dce45e500340efb23e8e4342a86d0543472b1d183760d	7249e215e8f69506ecb34d3b634f7bad8fbfadda93dc41c6f07457aec4dc1763
M	contracts/README.zh-CN.md	12125df76c806c046a7802344000a0ae756338eaa2290a4b718df45aa2b95366	c460eb9a10ae4d8d81866cd980c15f5080e821749a21c37432abecadf99460a4
M	contracts/published/http-api/plc-facts-v1/README.md	2b2e24a0d14acbc0ae54f264b706b040848be3a88bbcb8c2a9ab82bbe0726b42	a38c69e9e42ab81d15e9b5f50c3cf9be618e3b9846653de3a4a79f3306344e33
M	contracts/published/http-api/plc-facts-v1/README.zh-CN.md	477af9f359ff049f2088f9eddfa6f0e127aa6d95f2afbd6a16498c8778f66487	7d8bc879feddc61ae7894dff31f266fe7486601ce8ea2f49067e887065745854
M	frontend-js/src/app/monitor/api/index.js	15d42eb7abc5f36d6cb9c9157e8bc54f264ba722eb3d176bba68a0b0cb27c1e3	aef3ce89fe1267ca3c3100f41b840ebf64f859c34a292c1761bf6b439ad6d5c7
M	frontend-js/src/app/monitor/api/mock.js	7999a1fb40ca3db096b27c56fb496426f71e6ead40371f50b7be83f57b5bf500	ef110eb60d4a7482df6889b4091af0e4e37a597557cf715f4cbd45782dc629ac
M	frontend-js/src/app/system/api/index.js	3679a8356ab97f3fdbf78e4b9c6b72bda85cc16ab335d64a6419b560672416e9	02345e5b6bf81cac876b14e13a21b14c4ef169cbfe646d9a67ca84ea7a6c67b6
D	frontend-js/src/app/system/api/projectionMapping.js	1f6dc184dfa2d0824afe9e6067f19d1bf4b99e850d4f5e8884d86f1838647a08	-
M	frontend-js/src/app/system/locales/en-US.json	dd93a6ace95a53603eb1c20cee3025d9ea19e210a714f4e95382d561aec7c89c	d4c50e562c286abd1ab190c3e80910fcbc4c568554d8ba5bac5648ab860f5a2d
M	frontend-js/src/app/system/locales/zh-CN.json	8a2494a7f5e22e92248e66125b0a66a3ae82ad115d6609bdf6eddb098be81075	64502a6036429086fa8997b7c078265e22d059d638f12041aba80f459eb692a7
M	frontend-js/src/app/system/manifest.js	e613eab2ec7405b746cfd12350efb41e48f9aeac9ba45bb94d6ba677e70796ec	b7473f8d073d931cee651943b8ff88a4c4034b83902f287735fe9a648fb553e3
D	frontend-js/src/app/system/views/dict/index.vue	40301a6b43a5d83ac61836f8535bd73c87e730df84ea8c17b5bfbd333175b6e1	-
M	frontend-js/src/locales/en-US/breadcrumb.json	6beceee1194032408ad6c8289dca240423c46c0204a05a61ce698e3352489310	67221d19010ce5a3797ae9aafbdac533a27923242f8cedf55fdba7a7a866d32c
M	frontend-js/src/locales/zh-CN/breadcrumb.json	7ba5328dfa759b547c85c7521b2b0544d0a3e2c8fa9941e6e29ea5642df342c8	334a6fd180de38f3bb1d896323b9eb8106556ea622d6ad6292baee3249b93762
M	frontend-js/tests/module-registry/page-access.test.mjs	d7f061e472c8bea7c4337f0bbfc4644c512c9ab8f25b41cdb8373d1b539f34ae	93688972891b8a0a8862fda5d794481708bc25a2d634f6282c46755071ebc19d
M	frontend-js/tests/module-registry/registry.test.mjs	e0b37f35b75048f5fcd802f4a70c2b6eb1093097d43897b68e1e7e8623cc6426	9e74a835a86f1639c840aceb7b57763e4faa60c312f38fd2f2509a5be4ba9ff0
```

## R01 调用链与实际环境边界

- 源码静态命中与实际环境分开记录：`vibe-l2-front-end/frontend-next-js/` 及 `frontend-next-js-collab/` 仍引用旧 `/monitor/realtime/latest` 和 `/projection-mappings`；该消费项目 backend 仍有旧 Projection API/快照模型，其 control-agent 仍声明两张旧直库快照。它们是**静态旧依赖**，不证明采用了本次 3307；本任务未修改消费项目。
- 本仓冻结 CA 的 `automation-world/control-agent/src-tauri/src/infrastructure/database/entities/plc_db_block_{raw,latest}_snapshot.rs` 仍指向旧表；DAA `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/facts_http.rs` 仍使用 v1 `/batches`、`/latest`、`/history`。这两套源码、DAA 的 SQLite/配置/积压和 SMA 均未由本任务修改。升级后的指定 dev 不再提供旧表和 v1 上传/查询；DAA 的继续使用、补传和消费项目的替代路径按各自任务治理，不能从本任务推断其他环境已切换。
- 协调者在本机维护窗口以 `lsof -nP -iTCP:8000 -iTCP:3307 -sTCP:ESTABLISHED` 逐端口核对：当时全部 3307 入站连接分别为 DBX PID 39367 的 18 条和本项目 backend worker PID 50796 的 5 条，未见其他 TCP 客户端；8000 仅绑定 `127.0.0.1`，当时无其他已建立 TCP 会话。MySQL 全可见检查为 23 个 Sleep、0 未决事务和 2 个无事务内部 daemon；暂停 backend 后再次复核。协调者实际检查该 backend 配置和进程环境，v1 准入、Projection runner 及 3 个 BE-010 owner 均关闭/未采用。
- 协调者额外只读盘点本机进程命令和 Docker 容器名称，未发现匹配 DAA/CA/SMA 的名称；该名称检查不能证明其他部署或所有可能进程已停用。本次没有刻意停止或重连 DAA/CA。上述具体连接结果限定**本次指定 3307/8000 与维护窗口**：未观察到 DAA、冻结 CA 或消费项目实际连接及旧调用；不声称其所有其他部署均停用、已升级，或永久不会重连。相关调用方实际采用与恢复仍是独立边界。


## Developer handoff

- **精确输入：** `ARCH-ACQ-002 r2`，获批规格 SHA-256 `79d35e149dd9d8159cd1ccb5ee461fdcb8cfa299d6a7931928f291ac74e42394`；正式交付是 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 当前未提交工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。不得把其他并行未提交工作归为本任务，亦不得以 HEAD 或临时副本替代工作树审查。
- **实际文件：** 本任务实际 A3/M68/D54 共 125 路径及前/后 SHA 见上方最终清单和 ignored 证据 `arch-acq002-r2-postmysql-20261111.tsv`（SHA-256 `b1b03ab0468b85b34b83a15899ef226f5e24c8ad549f6f4e1f531cae671184d5`）；另有本 Development `tasks.md`。协调者负责共用 `CODE_INDEX.md` 机械同步，其当前 SHA-256 `cca4253d755e3af0b049f47baa11255adc8e0cec11f8ba0bae11feee9c664456`；FE-005 12 个文件属于该任务。新迁移为 `337ea1530f379e6076d784757572ae56be25752c5f039e41ff84bddbc66591d5`，`v2_config.py` 为 `2cfcc8957a945769a6e5dc178dca8eff0d022956244b519ea8d1f066751967e3`，九份原 migration 字节未变。
- **DEV self-check：** 13393 隔离 MySQL 第三轮 **3 passed**；前两轮的 2 passed / 1 failed 及唯一 MySQL 展示规范化差异、metadata 严格等价、锁竞争和恢复证据均在上文保留。真实 3307 由协调者按已批准范围完成 2c4→3d5、77→68 与 profile 单键切换，保留数据/对象和 v2 双表摘要一致、四 GET 及 collector 恢复。正式树定向后端 **147 passed / 3 历史候选 skip**，正式前端 **50 passed**；候选和正式树逐文件一致、编译/JSON/相对链接/diff 检查通过，联合候选 build 通过。自检不是 QA verdict。
- **已知限制：** 扩展 no-db 检查 **1023 passed / 6 failed / 3 skipped / 28 deselected**，原因、历史候选对照及未修改表外测试的事实见上文；不报告全量通过。九表恢复 DDL 中 MySQL 合成输出的 19 处冗余字符集明示已限定归一并对照所有结构元数据；真实 dev 九表备份在隔离库逐字复建。静态消费方、旧 DAA v1 与冻结 CA 仍有旧路径，指定 dev 升级后不兼容；本任务没有修改 DAA SQLite/配置/积压、SMA、冻结 CA 或消费项目，不代表其他环境完成迁移或跨端联调。BE-012 r4 原 B、真实业务接入、现场/生产及其他库仍按各自批准执行；恢复真实 dev 的旧表/进程/profile 需另批。
- **资源和证据：** Development 隔离容器 13393 已由协调者回收；Verification 的独占 13394 仍待该角色执行。`backend/data/maintenance-evidence/arch-acq002-r2-history/` 下历史 QA3 公开候选、post-MySQL 候选、隔离证明、实际 dev 前后摘要及九表恢复材料为本机 ignored 证据；请核对上文各 SHA、权限与保留期。原 BE-012 历史归档至少保留至该任务 B 完成及 Owner 决定后、无其他依赖。`/private/tmp/arch-acq002-r2-dev-h8rW0pBF/` 与从历史归档恢复的任务临时副本保留至独立验证及必要复核结束；由协调者确认无依赖后回收，不清理不明归属的资源。
- **下一 gate：** 将本精确 Revision、正式工作树及上述 diff/证据移交 fresh-context `verification`；其自行使用 13394 隔离目标复现 AC03–AC06，对 3307 仅只读复核。Verification 只在所属 `checklist.md` 记录独立 verdict；Human Owner final acceptance 随后单独决定。此 handoff 不授予 QA、验收、发布或现场操作。
