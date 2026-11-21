Task ID: ARCH-ACQ-006
Revision: r1
Status: developer_handoff
Owner Role: Development

# ARCH-ACQ-006 r1 开发交接

## 实施和候选

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基准 HEAD `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。本任务在该工作树直接落源码与合同。隔离验证使用无项目 `.env`、`.local`、日志、缓存和库数据的源码副本。源码未提交，原工作树已有并行改动延续。

- `da6c32f8a701` 是 `c9e1a3b5d720` 的唯一后继。迁移核对明确的 MySQL 目标和停写窗口，建立历史写入守卫和固定截止时刻，回填仍有效样本的事件引用，保持现有事实、latest 和登记。新写入锁 PLC/DB 流头，在事实同事务内追加事件。清理保留事件有效期和身份。
- `/api/v1/acquisition-consumers` 实现按授权消费、精确起点、租约、待投递及回执确认。进度和回执同事务提交。后端新增表仅保存身份、配置版本标识、摘要和运行状态。已绑定采集目标 POST 须核对服务身份、租约、目标身份和原始请求字节摘要。
- 新增版本化 OpenAPI、Schema、验收向量与双语说明。已发布 v2 机器工件原字节保持。公开合同和维护说明见 [消费者合同](../../contracts/published/http-api/acquisition-consumers-v1/README.zh-CN.md) 与 [事实模块](../../backend/app/plc_facts/README.zh-CN.md)。
- 真实库与历史未操作。SMA、DAA 源码未改动。隔离回放用内存 SQLite 模拟配置版本重构，并不作为 SMA 接入证据。

候选清单 35 条，以下按路径排序，每行 `sha256<两个空格>仓库相对路径<LF>`。清单 SHA-256 为 `c9848d0ec7669666e335a02fb092c1bdf6d36d7bcfb9e220c878b334ee73e39f`。清单内 CODE_INDEX 完整文件摘要供工作树核对，本任务定向增量是采集消费入口和后继迁移两行。

```text
d8e2d1ee3ef59da4dd7a452602b4bbd7f8594ff97710e94a239b03cb2bd85163  CODE_INDEX.md
fd28dca872c063f6d9fa1a9ecb146868a5577fd6fd7c0d316bbf90ee8f384703  backend/alembic/versions/20261119_1500_da6c32f8a701_acquisition_consumption.py
79226114d3200159589c46a22d792e5e5b87c16640cb349c3666aa8c733aeecc  backend/app/plc_facts/README.md
45dfb18375a0d3a65b920844c3ccbd724879c5ccef00a3b9c80a42661ed020a5  backend/app/plc_facts/README.zh-CN.md
62ab1e84f1ac502b83e250f3b4b2bb277ee49c038c3f3d8d890367d10a3724d6  backend/app/plc_facts/api/consumption.py
8dc0b1d1aab27c1b37c3cb9c23cf804f6af7de320181d02491edf0bb4380a66e  backend/app/plc_facts/api/v2.py
7d955621e0b36e802ac14fe3fcdf3270936ae295eb9a62772a4acb9cf805245c  backend/app/plc_facts/consumption_config.py
95e0226163de37d7cdeb37ff505151e4c5b5c7f2a607edaa25e0f5f061015cab  backend/app/plc_facts/consumption_domain.py
1c2e4a5bc7633ed6a3be2ad47fe3fb622938c9638a3305e99fcbdc6b7327f909  backend/app/plc_facts/crud/async_consumption.py
18507f93bb8c46175277e17545aa31580f08b2599ac6fc4bdaef898dae677111  backend/app/plc_facts/crud/async_v2.py
6ac60feebb1ec47576960502f87ebe56df605062d2a769e105a89211881364bd  backend/app/plc_facts/crud/sync_v2_maintenance.py
cfb5836e142d4e8aa8525c8d376ad0048cb66749800b2e12a1f01a5044fceff2  backend/app/plc_facts/manifest.py
e547bc13e9e272d63164ba1a6a59facd39aadb362f391e5b11e0fab2acecfa78  backend/app/plc_facts/models/__init__.py
376bd7f5b9f84a532f5a6bdd42dafebee89c7f6ca6911cd19a1ae49b861a5324  backend/app/plc_facts/models/consumption.py
76ca8debb53221133641133d7b61c8919982465d31c1249999564f6c9c9808ee  backend/app/plc_facts/schemas/consumption.py
351328474c27840df606f785af48d74da7778950d36550387b00c50419de7e22  backend/app/plc_facts/services/async_consumption.py
e6e111450b89650a17c339be3b5570299c1d54f97ce6f6767633cdaba5c9afcd  backend/app/plc_facts/services/async_v2.py
3f11d8947f502b5a0f44a7cf6e8d07f21d43fa87c487166c550aee7a8cd2fad4  backend/app/plc_facts/services/sync_v2_maintenance.py
4f0208e015639340b5909ef650b32c094eac17750de89154f3610e7f19d56a50  backend/app/plc_facts/v2_config.py
50a1dbcafb82c7953e8a7161a99c144ce5c7da0122fe94169a38588577c86a86  backend/common/integration/storage.py
bff052eaf82ceedfb3989e19581a0b25e46f7b2c699f6d0582acd165bf81c65f  backend/tests/test_acquisition_consumption_contract.py
77611de2e6ddba88ab3a6d0ccc984bc184dd99f1c78306905b8661ea02b56e76  backend/tests/test_equipment_temperature_migration.py
4008fb64f0dc67663280bdb680228929197394b81481571d089feeb082af7ea2  backend/tests/test_generic_task_migration_r3.py
d00b066c8a2a9c8abbe5191a2e93100ab3c668150bbb2c67fcb42427ecea4fc5  backend/tests/test_legacy_acquisition_retirement.py
95e4a943810dd7512ad23d9558ccef4d780cb9a0b770643d03ffab56cd5495b7  backend/tests/test_mapping_migration.py
c66159b04c55d1d2b1cbda64a7e04f3ad5123e532fe58ef1a279963d4bbcd80e  backend/tests/test_observation_retirement.py
08a3f949a5364bca3444aacd6897c22b9a9a522b16a969558c99196c8fb82d00  backend/tests/test_plc_facts_v2.py
317d86aa1d862df2ed269d81549c1fe0b1a0ba4b25f6deca15b40c73d2418239  backend/tests_mysql/test_acquisition_consumption.py
19890c14c3eb03a5db6627d7554406d61f8b36d1b491cec8be2bd66c3b40918d  contracts/published/http-api/acquisition-consumers-v1/README.md
a0eedad155335213530c4c0113b88fecd90ec8dc8e433eed573865908ad5cb6b  contracts/published/http-api/acquisition-consumers-v1/README.zh-CN.md
433a8b571962123e7d0300a1e767497c1e64d4befe7b854f7b05caab8be87ccd  contracts/published/http-api/acquisition-consumers-v1/openapi.json
2617dd6c6db7ea574b2f6f13187a3e39440adf1650b5f8ae3945b20a2d4a8d87  contracts/published/http-api/acquisition-consumers-v1/schema.json
7241b087e5575281ca7c40d2d2bf71d71f8476bd1dee1231ee05ff0da20a3698  contracts/published/http-api/acquisition-consumers-v1/vectors.json
4cca67d827302521bd55b2cf897d9cb794fe4bb73cb06da0ea5023c015c3dc8c  contracts/published/http-api/plc-facts-v2/README.md
cd3dce51ebfe1554a933046e4c246a5db9ec1f371cc7f408e3ff213efb30eed4  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
```

## Development 自检

| 预期 | 实际结果 |
| --- | --- |
| Python 编译，退出 0 | 使用项目 `.venv/bin/python -m compileall -q` 对采集模块、后继迁移和本任务新增测试编译，退出 0。字节码写入本任务临时目录。 |
| 已发布合同和事实回归，退出 0 | 在 `backend/` 使用 `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp .venv/bin/python -m pytest -q -p no:cacheprovider`，选择 `test_acquisition_consumption_contract.py`、`test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_acquisition_source_registry.py`、`test_legacy_acquisition_retirement.py`、`test_generic_task_migration_r3.py`、`test_mapping_migration.py`、`test_equipment_temperature_migration.py`、`test_observation_retirement.py` 和 `test_business_integration_storage.py`。188 通过、10 跳过，14.91 秒，退出 0。被跳过的是已有的条件/历史用例。 |
| 专属 MySQL 验证，退出 0 | 在不含项目环境配置的源码副本中用同一项目锁环境执行 `python -m pytest -q -x -p no:cacheprovider tests_mysql/test_acquisition_consumption.py`。专用 MySQL 8.4.6，角色 `dev`，loopback:54868，时区偏移 +28800。4 通过，18.86 秒，退出 0。 |
| 差异与文档 | `git diff --check`、新文件行尾与相对文档链接检查通过。对既有 `plc-facts-v2/*.json` 的差异检查为空。 |

隔离 suite 需要 `ACQ006_TEST_ROLE=dev|qa`、`ACQ006_TEST_PORT`、`ACQ006_TEST_SERVER_UUID`、`ACQ006_TEST_PASSWORD` 和 `ACQ006_TEST_EXECUTION_ACK=ARCH-ACQ-006-r1:<role>:127.0.0.1:<port>:<uuid>`。使用独立目标并在连接前核对确认字符串，连接后核对实际 UUID、版本和时区。fixture 创建并回收自己的随机 schema；由协调者回收本任务 MySQL 实例及其私有凭据。无项目 `.env` 的运行目录需给后端基本设置提供合成的项目名称、数据库选项、JWT 和 API 前缀。内部迁移使用精确的独立 schema，刺激前驱已有历史与中断后重跑。测试通过 FastAPI ASGI transport 执行 HTTP 契约，数据库执行为真实 MySQL。

### AC 核对

| AC | Development 证据 |
| --- | --- |
| AC01 | 同流接续和跨流并发，后上传的旧时间样本，事实写入回滚及 duplicate 均通过。 |
| AC02 | 明确拒绝欠缺确认的目标；隔离数据库保留并对账已有历史、latest 与登记，阻断未跟踪历史写入和删除，模拟中断并复用相同截止时刻、索引引用。 |
| AC03 | 测试 now 与 retained、初始化排除的中间过期、活跃任务中间缺口，以及实际清理后的缺口证据。 |
| AC04 | 旧源删除后既有事实可读，旧身份提交拒绝，重新登记代次接续游标。目标接管后旧 pending 保留。 |
| AC05 | 两执行者竞争、续租结果未知、旧租约拦截、暂停和接管。测试写入前、提交后故障和幂等重放。 |
| AC06 | 目标事务提交后故障，恢复同字节请求返回 duplicate，目标从历史和详情回读只一条。错回执不推进；确认提交后故障能够重放。 |
| AC07 | 重建字节、配置变化冲突、已过期及已清除源缺口、目标代次变化均检查停在原位置。模拟 SMA 配置库只含版本设置。 |
| AC08 | 401、权限与源范围 403、绑定目标 Bearer、已登记目标正文指纹、未绑定源 POST 和现有五个 GET 回归。 |

## 交接边界

本轮自检未使用实际项目库、现有历史或 DAA/SMA 应用。候选等待独立 Verification，隔离验证不授权真实采用、迁移或部署。迁移的停写窗口与事务对账必须按实际环境另行确认；数据库管理员和拥有 DDL 的特权用户仍须由部署权限隔离。事件和操作摘要保留，不在本 r1 自动压缩。过期、源缺失或不能恢复原字节时停止推进。

临时 Development 源码副本及本轮辅助脚本和字节码在自检后回收。协调者管理隔离实例、凭据及最终回收，Verification 使用自己的隔离实例和精确候选。

## developer_handoff rework-1

同一获批的 ARCH-ACQ-006 r1。首轮候选及自检记录保留，独立 QA1 结论见 [checklist.md](checklist.md)。

- 迁移按名称核验守卫的时点、事件、目标表和正文，检查同名守卫跨表冲突。隔离 fixture 逐一放入同名同正文但元数据有差异的三个定义，均拒绝激活，原三张表及前驱 revision 保持。排除冲突后复用原固定截止时刻准备历史索引。
- 四个并发矩阵用例以应用事件为屏障，交叉 `now`、`retained` 与写入先持锁、创建先持锁。确认争用事务等待，创建冻结正确起点，并完整回读并确认对应序列。
- 故障矩阵覆盖创建、运行和暂停、获取和续租及释放、登记待投递、ACK，以及绑定目标 POST。提交前丢响应保持读回状态，提交后丢响应可重放同一操作，改变同一身份的有效请求内容返回冲突。绑定目标 POST 验证写入数从 0 到 1，原字节重试为 duplicate。
- 独立构造错误实例、样本 ID、HTTP 状态、业务码、合同版本、回执状态和 outcome。每次拒绝后读取原 pending、原游标及唯一的目标事实。
- 隔离客户端将两份映射配置版本存进同一个 SQLite 文件，首次使用指定版本映射点位并固定摘要。换执行租约后重新 GET 并重新打开配置库，按 pending 指定的旧版本重建与发送。改用新版本和移除旧版本分别阻断重构，保留原 pending、游标及唯一目标样本。

仍在交付工作树直接落地。相对首轮仅改变后继迁移和隔离测试两文件。下列 35 条按原算法重算，清单 SHA-256 为 `a984198eaa14266df0a429720158582a4530e733cd83a66c1313a7009082231c`，基准 HEAD 仍为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。

```text
d8e2d1ee3ef59da4dd7a452602b4bbd7f8594ff97710e94a239b03cb2bd85163  CODE_INDEX.md
f4212cdff3a513f75f79e182f80e9088d301437bd688ce91b5b5d19c80d4adca  backend/alembic/versions/20261119_1500_da6c32f8a701_acquisition_consumption.py
79226114d3200159589c46a22d792e5e5b87c16640cb349c3666aa8c733aeecc  backend/app/plc_facts/README.md
45dfb18375a0d3a65b920844c3ccbd724879c5ccef00a3b9c80a42661ed020a5  backend/app/plc_facts/README.zh-CN.md
62ab1e84f1ac502b83e250f3b4b2bb277ee49c038c3f3d8d890367d10a3724d6  backend/app/plc_facts/api/consumption.py
8dc0b1d1aab27c1b37c3cb9c23cf804f6af7de320181d02491edf0bb4380a66e  backend/app/plc_facts/api/v2.py
7d955621e0b36e802ac14fe3fcdf3270936ae295eb9a62772a4acb9cf805245c  backend/app/plc_facts/consumption_config.py
95e0226163de37d7cdeb37ff505151e4c5b5c7f2a607edaa25e0f5f061015cab  backend/app/plc_facts/consumption_domain.py
1c2e4a5bc7633ed6a3be2ad47fe3fb622938c9638a3305e99fcbdc6b7327f909  backend/app/plc_facts/crud/async_consumption.py
18507f93bb8c46175277e17545aa31580f08b2599ac6fc4bdaef898dae677111  backend/app/plc_facts/crud/async_v2.py
6ac60feebb1ec47576960502f87ebe56df605062d2a769e105a89211881364bd  backend/app/plc_facts/crud/sync_v2_maintenance.py
cfb5836e142d4e8aa8525c8d376ad0048cb66749800b2e12a1f01a5044fceff2  backend/app/plc_facts/manifest.py
e547bc13e9e272d63164ba1a6a59facd39aadb362f391e5b11e0fab2acecfa78  backend/app/plc_facts/models/__init__.py
376bd7f5b9f84a532f5a6bdd42dafebee89c7f6ca6911cd19a1ae49b861a5324  backend/app/plc_facts/models/consumption.py
76ca8debb53221133641133d7b61c8919982465d31c1249999564f6c9c9808ee  backend/app/plc_facts/schemas/consumption.py
351328474c27840df606f785af48d74da7778950d36550387b00c50419de7e22  backend/app/plc_facts/services/async_consumption.py
e6e111450b89650a17c339be3b5570299c1d54f97ce6f6767633cdaba5c9afcd  backend/app/plc_facts/services/async_v2.py
3f11d8947f502b5a0f44a7cf6e8d07f21d43fa87c487166c550aee7a8cd2fad4  backend/app/plc_facts/services/sync_v2_maintenance.py
4f0208e015639340b5909ef650b32c094eac17750de89154f3610e7f19d56a50  backend/app/plc_facts/v2_config.py
50a1dbcafb82c7953e8a7161a99c144ce5c7da0122fe94169a38588577c86a86  backend/common/integration/storage.py
bff052eaf82ceedfb3989e19581a0b25e46f7b2c699f6d0582acd165bf81c65f  backend/tests/test_acquisition_consumption_contract.py
77611de2e6ddba88ab3a6d0ccc984bc184dd99f1c78306905b8661ea02b56e76  backend/tests/test_equipment_temperature_migration.py
4008fb64f0dc67663280bdb680228929197394b81481571d089feeb082af7ea2  backend/tests/test_generic_task_migration_r3.py
d00b066c8a2a9c8abbe5191a2e93100ab3c668150bbb2c67fcb42427ecea4fc5  backend/tests/test_legacy_acquisition_retirement.py
95e4a943810dd7512ad23d9558ccef4d780cb9a0b770643d03ffab56cd5495b7  backend/tests/test_mapping_migration.py
c66159b04c55d1d2b1cbda64a7e04f3ad5123e532fe58ef1a279963d4bbcd80e  backend/tests/test_observation_retirement.py
08a3f949a5364bca3444aacd6897c22b9a9a522b16a969558c99196c8fb82d00  backend/tests/test_plc_facts_v2.py
c3320018a2eceb6957bd22c66f79a617cd54543ae85f32576dfc1e8be981a8a0  backend/tests_mysql/test_acquisition_consumption.py
19890c14c3eb03a5db6627d7554406d61f8b36d1b491cec8be2bd66c3b40918d  contracts/published/http-api/acquisition-consumers-v1/README.md
a0eedad155335213530c4c0113b88fecd90ec8dc8e433eed573865908ad5cb6b  contracts/published/http-api/acquisition-consumers-v1/README.zh-CN.md
433a8b571962123e7d0300a1e767497c1e64d4befe7b854f7b05caab8be87ccd  contracts/published/http-api/acquisition-consumers-v1/openapi.json
2617dd6c6db7ea574b2f6f13187a3e39440adf1650b5f8ae3945b20a2d4a8d87  contracts/published/http-api/acquisition-consumers-v1/schema.json
7241b087e5575281ca7c40d2d2bf71d71f8476bd1dee1231ee05ff0da20a3698  contracts/published/http-api/acquisition-consumers-v1/vectors.json
4cca67d827302521bd55b2cf897d9cb794fe4bb73cb06da0ea5023c015c3dc8c  contracts/published/http-api/plc-facts-v2/README.md
cd3dce51ebfe1554a933046e4c246a5db9ec1f371cc7f408e3ff213efb30eed4  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
```

| 自检 | 结果 |
| --- | --- |
| 项目解释器 `-m compileall -q` 编译采集模块、后继迁移和两项本任务测试 | 退出 0 |
| 首轮指定的十组离线回归命令 | 188 通过、10 跳过，15.23 秒，退出 0 |
| 无 `.env` 副本内执行项目解释器 `-m pytest -q -x -p no:cacheprovider --basetemp <仓外临时测试目录> tests_mysql/test_acquisition_consumption.py` | 独占 Dev MySQL 8.4.6，9 通过，34.67 秒，退出 0 |
| 普通差异、相对文档链接、已发布 v2 JSON 对 HEAD 比对 | 差异与链接检查通过，既有 v2 JSON 保持原字节 |

自检过程中 MySQL 对同名跨表触发器的 `IF NOT EXISTS` 行为由预读元数据消解。测试凭据和 SQLite 测试库使用副本仓外临时路径。最终候选与副本的后端文件逐字节一致。每个 Dev 测试 schema 由夹具回收，本轮源码副本和专属 pytest 临时目录已回收。隔离实例与其凭据由协调者管理。真实库与历史未操作，SMA-008 r2 未改动。本候选交下一次 fresh-context Verification。
