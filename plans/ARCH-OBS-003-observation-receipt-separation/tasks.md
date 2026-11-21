Task ID: ARCH-OBS-003
Revision: r4
Status: developer_handoff
Owner Role: Development

# ARCH-OBS-003 开发记录

Human Owner 明确批准 r2 实施和隔离验证。dev 切换、停服、清理和演示不在本次执行范围。交付工作树为仓库根目录，实施前 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。并行 ARCH-ACQ-006 尚在实施时先在任务专用隔离源码副本进行本任务的代码与探针，避免提前改变对方 Alembic head 和冻结候选。正式交接前将核对并整合本任务的授权 diff。

## 前驱固定

实施前只读捕获 ACQ 迁移 SHA-256 `4a121e6b353707c6a3e5602aaeb759771e10716efeb59439c6362a0c73359960`。ACQ 初次交接清单与修订中的迁移文件发生一次不同步；未将它用于正式结果。随后在 [ACQ 已更新的 Development 交接](../ARCH-ACQ-006-acquisition-consumption-delivery/tasks.md) 记录的隔离 4 项通过基础上，逐条核对并固定其 35 条清单，清单 SHA-256 为 `c9848d0ec7669666e335a02fb092c1bdf6d36d7bcfb9e220c878b334ee73e39f`。固定 ACQ 前驱迁移 SHA-256 为 `fd28dca872c063f6d9fa1a9ecb146868a5577fd6fd7c0d316bbf90ee8f384703`。在隔离源码复制和原工作树对账之前，保留 ACQ 文件原样，交接证据不属于本任务。

## 开发自检进展

- 早期探针使用任务自有 MySQL 8.4.6。证明显式 WRITE 表锁可跨外键切换、改名；遇到 MySQL 原地替换同名 FK 报错后，使用单条 ALTER 且新约束名独立，仍保留原外键索引语义。非空探针切换后观测和能耗数据及旧事件重放对账通过，初版同时提交两条能耗事件的测试对任一路 503 过于严格，正在与原 c9 行为核对；保留预先存在的重试和错误语义，不新增重复业务行。
- 只读观测回归初版聚焦组 39 项通过。冻结前驱后的扩大组第一次 192 通过、9 跳过、4 失败，其中 1 项需要执行时临时目录在 `/private/tmp`。待复测的三个源码断言：两项旧任务当前 ORM 仍要求此次拟改名表，另有刚交接的采集合同图检查仍要求 `da6` 为唯一 head。r2 允许更新前两文件的 head 断言，未授权更改这两项实时 metadata 断言或第三文件；已报协调者，相关断言保持原样，等 PM 界定处理。当前未提交 Development handoff。

## 任务自有资源

`/private/tmp/arch-obs-003-dev.xtw4tT` 含本任务源码快照、旧 c9 原始源码快照、一次性配置与隔离日志。保留至正式源码整合及 QA 交接。在 Docker Desktop 使用任务标签 `aiis.task=ARCH-OBS-003` 的任务独占 `arch-obs-003-dev-mysql`（初期探针）和 `arch-obs-003-formal-mysql`（正式开发自检）容器；随机回环端口，私有密码不进仓。测试随机 schema 由夹具回收。本任务未访问当前 dev、生产、现有数据库或真实 PLC。

## 已冻结候选的自检结果

| 检查 | 结果 |
| --- | --- |
| 真实 MySQL 8.4.6 隔离 OBS 首轮 | `python -m pytest -q -p no:cacheprovider tests_mysql/test_observation_receipt_separation_mysql.py` 在任务专用 59682 回环实例，3 通过、79.24 秒、退出 0。空库由 root 升至唯一 d8；非空库从真实 c9 认证 HTTP 写入，经 ACQ 回填到 da6，再到 d8，对账全部业务数据、三路旧回执 ID 和字段、两路回执自增水位、三处样本外键、六张采集消费表、三个触发器及合成来源、事实、待交付/已记录操作状态。旧 c9 与新 d8 都验证并发同事件只入库一次，发生并发暂不可用时用同正文重试同一结果。保留未拥有当前快照的旧回执和无业务行的历史回执。 |
| MySQL 恢复和 HTTP 行为 | 在同一 3 项通过的首轮中分别注入复制、外键、改名、移除源回执、Alembic 登记之后的故障。观察各阶段版本、表、FK、前驱触发器及已提交的数据。直接重跑被阻止；用隔离库备份恢复精确 da6、对账后重新迁移及三路旧 POST 重放通过。HTTP 变更正文 409、撤销授权先拒绝、提交前故障回滚与提交后结果未知用原正文重试通过。 |
| 采集真实 HTTP / MySQL | 任务专用实例上跑 ACQ 冻结的 `tests_mysql/test_acquisition_consumption.py`。原 da6 4 通过、20.97 秒；OBS d8 4 通过、20.51 秒，均退出 0。d8 用临时 pytest hook 指向同一 suite 的目标后继和 OBS 合成维护确认值，未修改其文件字节或共享仓库。含采集写入及同事务事件、duplicate、过期清理、续读、租约与 pending/ack 和故障重放。 |
| 聚焦源码回归及预检 | `TMPDIR=/private/tmp python -m pytest -q -p no:cacheprovider` 聚焦 OBS、ACQ 及 revision guards 联合组，193 通过、9 跳过、3 个测试断言待授权适配。临时隔离候选 `alembic heads` 为唯一 d8，`python -m compileall -q` 及 `python -m app.module_preflight --project-root "$PWD" --check-only` 退出 0。检查新增文档相对链接通过。 |

以上为 Development 自检。工作树仍有并行 ACQ 独立验证对象，尚未整合暂存源码，也未交接独立 OBS Verification。

强化隔离 MySQL 自检的首次运行 3 通过、1 失败，失败发生于测试创建低权限账号前，PyMySQL 将 SQL 中的字面 `%` 当作参数格式。修正夹具后，完整同命令复跑 **4 通过，96.97 秒，退出 0**。四类检查覆盖：

1. 从 root 到 d8 空库和错误目标、不明 target、冲突表名、外部外键、视图依赖、缺全局可见性账号的实际拒绝。
2. 并发连接写旧、新回执表均被显式 WRITE 表锁阻止，最终无并发插入记录。
3. 复制、外键、改名、移除源回执、版本登记后五处故障；受控备份恢复通过。
4. 非空 c9 → da6 → d8 数据、错类和孤儿回执防护、两表原值及自增水位、HTTP 原响应重放和提交故障。各业务表原值、旧回执 ID 和传感数据均保留。

当前隔离候选的 30 文件清单位于 `obs-candidate-draft.sha256`（SHA-256 `59ecb98621ffdb060d95c78d1d12b6bbfd85170e823d569befd90f4680225b36`），授权范围合并前工作树 preimage `obs-candidate-worktree-preimage.txt`（SHA-256 `1a8bdb3e0e997505f976d6bf94b446725ad4eac809fcb43a79858f61a1b40fe3`），均在本任务隔离目录。后续整合前须核对并行 ACQ 的冻证对象已固定，复核当前文件 preimage，保留并行文件与索引改动。当前剩余工作为 r3 精确批准后适配三个源码断言、完整复测、正式源码整合核对，才可交独立 Verification。当前不构成开发交接或独立 QA 通过。


## r3 Development handoff

2026-11-19，Human Owner 明确批准 r3 精确断言范围和隔离验证。已在冻结 r2 隔离候选仅修改 §5.1 三处断言，保留旧迁移的历史常量、旧接口断言和 ACQ 发布合同。业务代码、MySQL suite、迁移和既有合同的 r2 实测字节一致。ACQ QA 的交接源仍单独固定，当前工作树上三个原断言均未改动；实施路径仍等待协调者核定并行证据窗口后按强一致规程整合。对工作树的三文件 preimage：

```text
c66159b04c55d1d2b1cbda64a7e04f3ad5123e532fe58ef1a279963d4bbcd80e  backend/tests/test_observation_retirement.py
d00b066c8a2a9c8abbe5191a2e93100ab3c668150bbb2c67fcb42427ecea4fc5  backend/tests/test_legacy_acquisition_retirement.py
bff052eaf82ceedfb3989e19581a0b25e46f7b2c699f6d0582acd165bf81c65f  backend/tests/test_acquisition_consumption_contract.py
```

其中在 r2 临时候选已授权更新首两文件的 head 断言，三处 r3 断言只追加 §5.1 范围变更。``CODE_INDEX.md`` 的两条 OBS 新项在隔离候选，后续整合仅机械加入，不覆盖并行项。当前正式工作树和候选还不相同，以下是供独立 QA 验证的**冻结候选**，不是工作树已整合的声明。

- 候选根 `/private/tmp/arch-obs-003-dev.xtw4tT/source`，开发基准 HEAD `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。独立 QA 复制到其任务自有路径并核对如下 31 文件的全部 SHA-256。候选清单摘要 `2383e7658eae02abb756fb3dc5e7a45fb82e6005a5a9aef86aa4fc1c84f60272`。前驱 ACQ 文件本身仍为 `fd28dca872c063f6d9fa1a9ecb146868a5577fd6fd7c0d316bbf90ee8f384703`。ACQ 35 文件清单是改动前底稿，OBS 有意修改的交叠文件依据批准范围单独对照，不能当作 ACQ 原件。
- r3 聚焦回归 196 通过、9 跳过、1 SQLite datetime deprecation warning，15.69 秒，退出 0。选择此前聚焦的 13 个后端测试文件。r3 隔离候选 compileall、模块只读 preflight、单一 Alembic head `d8f2a4c6b915` 退出 0。r2 已通过的真实 MySQL 8.4.6 数据路径覆盖 r3 相同产品字节；另行运行了 r3 同一冻结候选 MySQL 补充复测，结果单独附记。
- 运行 OBS MySQL suite 命令为 `python -m pytest -q -p no:cacheprovider tests_mysql/test_observation_receipt_separation_mysql.py`。环境需提供仅绑定高位回环端口、时区 +08 的另一个任务专用真实 MySQL 8.4 实例，通过 `OBS003_TEST_PORT`、`OBS003_TEST_SERVER_UUID`、`OBS003_TEST_PASSWORD`、`OBS003_TEST_ACK=ARCH-OBS-003-r2:127.0.0.1:<port>:<uuid>` 和 `OBS003_TEST_OLD_BACKEND` 指定。确认字符串仍使用相同数据路径自检的固定识别符 r2。前驱旧 HTTP 来源由 `git archive cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81 backend` 取不带本机私有配置的源码。故障恢复测试使用本机 MySQL 命令行工具，所有数据库权限和目标都在专用实例内。独立 QA 使用自己的实例和配置，不复用 Development 的私密口令或现有库。
- 数据库迁移维护值为 `OBS_RECEIPT_EXPECTED_SCHEMA`、`OBS_RECEIPT_EXPECTED_SERVER_UUID`、`OBS_RECEIPT_WINDOW_CONFIRMED=<schema>:<UUID>`。候选仅支持在线 MySQL 8.4 和明确前驱，遇部分状态做版本、表、数据、外键对账后凭备份在取得授权的环境恢复。复验中如需重放已有采集兼容 suite，可审计 `pytest_obs003_acq.py` 对其临时目标版本插桩，或独立实现等价测试。

```text
83295a32eb310c8947844e90ee9ebe5f8d40676eaf2a64b6cd0148a2adca83fd  CODE_INDEX.md
5f70a800f41e7654aec308e89683bbdb369b6b9825e56c4274d52ecbb75f7b97  backend/README.md
e1c843d8e025439aca074d4ed6bdd866db4dc5151c32d10a5b288aaaad4ece74  backend/README.zh-CN.md
f567abbf1db7a7ee9bbb204cf7a687583351ed26d012c718511340dcda7940a9  backend/alembic/versions/20261119_1700_d8f2a4c6b915_observation_receipt_separation.py
5aa719a2e00af0b45f4fa64fcaa8ffc8a5ce68e9565b3ef98662994ffbee52f7  backend/app/equipment_observation/README.md
17c80c56fff90dd7ff377392654c2aa1357a51f23fbd21af131abee2ebed97ab  backend/app/equipment_observation/README.zh-CN.md
02173650766620ddefe24fc6e02b50066c16c4f525119264d89fd0cc294fec2e  backend/app/equipment_observation/models/__init__.py
91168200142451f72ecdbafbaeb0f0acc95b6eca3a549e179b1e91a510a2e25d  backend/app/equipment_observation/models/records.py
016bc41234efc14552b262d956b501d8a39d1003dac064d99ebb19315e034cca  backend/app/equipment_observation/profile.py
77c893ccd72f72631ee6cea3ed8d68bd9f2f00fbf41bb12c5eaa18f1dd8350be  backend/app/equipment_observation/services/ingest_v2.py
3362064b0fae1322b99652983fe0412cd0ad68dbead83a1d432175aed447a5b6  backend/app/plc_facts/services/async_consumption.py
c99242e72cbd80a317a464e2651ef3677ded45af906599973c3426d047672c89  backend/app/plc_facts/services/async_v2.py
b23a16e827f0078e356217845127c52f532daec72fe6c6e8639907649f08beff  backend/app/plc_facts/services/sync_v2_maintenance.py
8566e67e21f8f6e0200a8eda925849f408f5d2341bff01bf76e4482565eaad24  backend/app/plc_facts/v2_config.py
bf44047648ec7ef25588da9a680397b241fbbd573508669c2c6e1f783b40c57b  backend/common/integration/storage.py
aee23914ca6370ec49933f42313141d37dbcf63472c701b667abaab9263ba03e  backend/tests/test_acquisition_consumption_contract.py
2c7462f835c315efd2043ec1b60db9fe2bf6285b529f12b8fef4908de5e6c7a1  backend/tests/test_business_integration_storage.py
235ff261a3983f9fdec2763609950ec4938062fcbdb4a8bd7b062c0bce45680b  backend/tests/test_equipment_observation_domain.py
eb0d9c23f7b98dd4ee8e261687af1fa39020ef430dd3ea4b8efc37b96c5cfb39  backend/tests/test_equipment_observation_r10.py
340aabc97f9a59f09a930a49ef7d2e56a2e296c3584165e7db58017069790446  backend/tests/test_equipment_observation_r10_flow.py
20081e8931518860a3d633007b6e379f219646fee675a768614d87af280d934d  backend/tests/test_equipment_temperature_migration.py
ac675ea1605a48afbbbc573f7cfb1a01d091da3f356bd758551526bca4136351  backend/tests/test_generic_task_migration_r3.py
64e0a1d7838feac1f120a31ad3ce814d5501d38ffb95b58d0a9056c4efc5e82f  backend/tests/test_generic_task_revision_guards.py
891bcf93cd74138072ac7df62eb4dc4eed64ad88c414adf705aa067e4c05683c  backend/tests/test_legacy_acquisition_retirement.py
35b740b78096a88dc6430eeda365bc956385d871788dac2d4f19236d94e5072d  backend/tests/test_mapping_migration.py
430745e4fbb1ec7ade3594c8acfdef9446e19ada04216541c238484cb7e19a99  backend/tests/test_observation_receipt_separation.py
c2e89ea7566b31e42bb5d085debecdd15b14a8489e5aa51b1b756043ce2cd475  backend/tests/test_observation_retirement.py
491a669b05072156c65c92863048c8515535dcb5d7ba63cb4b3646ce5654f49f  backend/tests_mysql/test_observation_receipt_separation_mysql.py
38dbb89c46be03b71455cd92ba523f6897aa03e7eb4339ee79cb05f67a58c1f2  contracts/published/http-api/equipment-observation-v2/README.md
1d96ad153fecd16589214c06212ea8e27266e4bb023698ee3ebd7dda30c3f41f  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
34a7aeb21b93ff1a68cc3b4075ff177e39b04f4499fdb940e1647cd03e1099ae  docs/equipment-status-process-monitoring.zh-CN.md
```

Status `developer_handoff` 表示独立验证候选已交协调者安排 fresh context QA。涉及 dev 的数据库、真实数据清理、服务和演示均未进行。最终范围和验收由各有权角色记录。

### r3 补充复测与正式工作树待切换材料

- 同一冻结 r3 候选在任务专用 MySQL 8.4.6 回环实例补充复测完整 OBS suite，**4 通过、97.20 秒、退出 0**。结果与同业务字节的 r2 自检一致。
- 只读整合检查 `/private/tmp/arch-obs-003-dev.xtw4tT/integration-preflight.py` 核对了 OBS 31 个候选文件、官方 ACQ 已固定 35 个输入及交叠 12 个受控 preimage，**0 个不匹配**。`CODE_INDEX.md` 保留已有 ACQ 等并行内容，其差异只有两条 OBS 记录新增。
- 便携补丁为 `/private/tmp/arch-obs-003-dev.xtw4tT/ARCH-OBS-003-r3.patch`，SHA-256 `ff13dcadee41ae0f65cf83edd9fa081f925b792abd670460b186c364dc63bd29`。在真实工作树只执行了只读 `git apply --check`，退出 0；在任务独占 preimage 副本执行实际补丁重放，31 个输出文件逐字节匹配交接 SHA-256。补丁不含私密配置、工作流状态或 ACQ 前驱改写。
- 正式 backend 由用户的本机自动重载进程运行，所以正式源码整合与 dev 切换保持在用户另行批准的维护窗口。在获授权的窗口内，先明确 ACQ 与 OBS 次序和目标，停止相关写入方及自动重载应用，复核各自候选、preimage、备份和目标 revision，之后按固定 SHA-256 应用补丁。若此时任何源文件漂移，停止该步核对；不得覆盖并行变更。应用后先验证官方工作树 31 文件 SHA-256、唯一 d8 head 和模块预检，核对 ACQ 按其单独授权在真实目标完成 da6，再执行显式 d8 目标迁移和授权范围内的 profile 切换。只有最终源码、schema、profile 和相应数据验证一致才恢复服务。如发生 DDL 路径失败，保持停写并依据实际表、外键和版本使用预先验证的备份恢复方案。
- 当前没有应用正式补丁、启动或停止真实服务、写真实数据库、改真实 profile 或恢复演示。本次可验证候选和补丁保留至独立 QA 及另行批准的切换完成，之后由协调者按任务资源收尾规则处理。

## r3 返工探针，正式验证暂停

独立检查报告两项 AC05 可复现缺口后，在新任务自有副本 `/private/tmp/arch-obs-003-guard-rework.yol7kZ/source` 修复；原 r3 工作树 preimage、冻结候选、31 文件清单和失败阶段证据保留。正式工作树未整合。探针仍使用原固定 ACQ 前驱 SHA-256 `fd28dca872c063f6d9fa1a9ecb146868a5577fd6fd7c0d316bbf90ee8f384703`，仅供有边界开发自检；真实并行 ACQ 前驱候选已变化，新前驱和 r4 尚不得作为本轮批准或新独立 QA 的依据。

- `backend/alembic/versions/20261119_1700_d8f2a4c6b915_observation_receipt_separation.py` 探针 SHA-256 `845ec87a09cdb25743afb4844be4c6643b1a4127930709d3975294d0de3bfa88`。按 MySQL 返回的 `CHECK_CLAUSE` 验证实际布尔表达式，仅有同名并已启用不足以通过。比对前驱库、表和继承的字段排序规则，关键标识字段保留显式 `utf8mb4_bin`。
- `backend/tests_mysql/test_observation_receipt_separation_mysql.py` 探针 SHA-256 `748f6302677db1e11c20721515f2d4ee055a727d888cbf03dd88b7d07cc34493`。在 OBS 任务隔离 MySQL 8.4.6 运行 `python -m pytest -q -p no:cacheprovider tests_mysql/test_observation_receipt_separation_mysql.py -k predecessor_guard`，**1 项通过、4 项未选择、12.29 秒、退出 0**。证据 `targeted-mysql.log` 在探针目录。依次证明同名且 ENFORCED 的宽松 CHECK 被拒绝、单个回执目标列改为 `utf8mb4_0900_as_cs` 被拒绝，两次均保留 da6 和原表集。恢复原 `utf8mb4_0900_ai_ci` 与 CHECK 后迁移成功。
- 当前探针仅验证 `utf8mb4_0900_ai_ci`。其余继承排序规则的支持集合、对应真 MySQL 正向验证和新 ACQ 前驱固定，等精确 r4 批准及可核验交接。没有新增 Development handoff、独立 QA 结论、真实库操作或服务变更。


## r4 Development handoff

2026-11-19，Human Owner 明确批准精确 r4 实施和隔离复验。r3 失败结果及现有 r3 候选证据原样保留。本轮在任务独占副本完成，对正式工作树只做读取、preimage 核对及补丁检查；与 dev 自动重载及迁移的真实切换仍等单独窗口，无真实库、服务或现有业务数据操作。

### 新采集前驱固定

按 [ACQ 已返工的交接](../ARCH-ACQ-006-acquisition-consumption-delivery/tasks.md) 固定该任务最后一段 35 文件清单 SHA-256 `a984198eaa14266df0a429720158582a4530e733cd83a66c1313a7009082231c`，逐字节核对当时正式工作树 35/35 一致。[ACQ 独立 QA2](../ARCH-ACQ-006-acquisition-consumption-delivery/checklist.md) 记录 `qa_passed`，本验收不代替其 Human Owner 最终验收。相对前一次 OBS 固定的 ACQ 内容，只有采集迁移及采集隔离 suite 两个文件更新。当前实际验证前驱迁移哈希 `f4212cdff3a513f75f79e182f80e9088d301437bd688ce91b5b5d19c80d4adca`，采集隔离 suite 哈希 `c3320018a2eceb6957bd22c66f79a617cd54543ae85f32576dfc1e8be981a8a0`。其余 ACQ 源码与发布工件保全，OBS 没有改写该迁移或 suite。

### r4 返工范围及实际结果

相对冻结 r3 OBS 候选，仅修改 d8 迁移预检、它的隔离测试及模块双语 README 共四个文件。按 MySQL 8.4 实际 `CHECK_CLAUSE` 值逐字匹配预期表达式和 `ENFORCED`，保留原样的数据库行为。批准支持明确的两种前驱库与表默认规则 `utf8mb4_0900_ai_ci`、`utf8mb4_unicode_ci`；固定前驱 DDL 未指定表级默认规则，迁移校验所有受影响表和继承列与原库默认一致，显式标识列仍要求 `utf8mb4_bin`。其他默认规则或单列漂移在任何迁移 DDL 之前拒绝。没改服务写入代码、路由或公开合同字节。

| 检查 | Development 自检证据 |
| --- | --- |
| 真实 MySQL 8.4.6 OBS 套件 | `python -m pytest -q -p no:cacheprovider --basetemp=<专用目录> tests_mysql/test_observation_receipt_separation_mysql.py`，**6 通过，142.98 秒，退出 0**。含从全空库 root 向前 d8、两种已声明默认规则各一套非空 c9 → da6 → d8 真实 HTTP 三路迁移和回执重放、逐字段数据及表／列排序规则保全对账。 |
| 两处 r3 预检缺口与既有防护 | OBS 套件用非空合成真实写入分别构造同名启用的宽松 CHECK 和回执 target 列改变为 `utf8mb4_0900_as_cs`。均在迁移 DDL 之前失败；保留精确 da6、表清单、故障注入后的 SHOW CREATE 和数据（包含回执）。恢复原生表达式和规则后成功。未知库默认规则、错类／孤儿回执、权限不足、表名占用、外键／视图依赖及真实 SQL 竞争拒绝通过。复制、外键、改名、移除源回执、版本登记五处阶段故障、备份恢复和再次迁移验证通过。 |
| 精确 ACQ 候选及 OBS 后继 | 更新后采集 MySQL suite 在 da6 **9 通过，37.56 秒**，d8 **9 通过，36.98 秒**，均退出 0。分别构造同名／同正文但时点、事件或所属表错误的真实触发器，均保留 c9、原事实、latest 和登记，且未激活；正常前驱回填成功。两版本均验证采集同事务追加、duplicate 不增、续读、租约和清理。OBS 非空用例另对账 ACQ 六张表及三个触发器在迁移前后内容相等。d8 采用同份 ACQ 证据文件与临时目标版本 hook，未改 ACQ suite 字节。 |
| 聚焦源码与静态检查 | 同一 r3 聚焦 13 文件组在 `TMPDIR=/private/tmp`，**196 通过、9 跳过、1 SQLite datetime deprecation warning，16.23 秒，退出 0**。compileall、模块只读 preflight、单一 d8 Alembic head、双语 README 链接、差异空白检查通过。 |

### 候选、补丁与测试复现

- 冻结候选根 `/private/tmp/arch-obs-003-guard-rework.yol7kZ/source`。31 文件清单在本节及 `obs-r4-handoff.sha256`，清单 SHA-256 **`5129fa3478f11362ca64ff9f1ed92aded00e30100be1f86b560dd0f53d3cf1f9`**。与 ACQ 35 文件清单的 12 个交叠已按固定原件核对，从候选比较时区分本任务授权的源码／测试／索引修改。ACQ 前驱迁移不包含于 OBS 补丁。
- 暂存补丁 `/private/tmp/arch-obs-003-guard-rework.yol7kZ/ARCH-OBS-003-r4.patch`，SHA-256 **`a6cdbb8ae93ac27d653a12b7ad095d0aa70912b567be1fa9403c153b7e84ea9c`**。`integration-preflight-r4.py` 只读检查 31 OBS／35 ACQ／12 交叠，零不匹配；正式工作树 `git apply --check` 通过。任务独占正式 preimage 副本应用补丁后 31 个文件全部逐字节吻合，未把补丁应用到正式运行源。r3 的安全切换顺序仍有效；批准的窗口内以此 r4 批次代替 r3，并重新验证目标、preimage、冻结摘要和部署前保护。
- fresh Verification 从冻结根复制，核对下方 31 哈希与 ACQ 返工前驱和 suite 哈希。使用自己的可验证 MySQL 8.4 专用实例、时区 +08:00、回环端口与合成身份。OBS suite 入口、环境和旧 c9 用 `git archive cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81 backend` 的要求沿用 r3 交接。采集 da6 运行 `tests_mysql/test_acquisition_consumption.py`，d8 用同份 suite 把 `CONSUMPTION_REVISION` 定向到 d8 并按实际合成 schema／UUID 注入 OBS 维护确认，或独立重演相同检查。旧前驱测试使用隔离 fixture 触发器注入，不调整任何产品数据库。
- 任务自有的两个开发容器与旧 r3／r4 开发副本、日志、补丁和 fixture 仍用于证据及后续窗口。各测试随机临时 schema 已由夹具回收。关键结果在本文件持久记录，临时目录不做唯一证据。真实 dev 与 replay 演示继续隔离。

```text
83295a32eb310c8947844e90ee9ebe5f8d40676eaf2a64b6cd0148a2adca83fd  CODE_INDEX.md
5f70a800f41e7654aec308e89683bbdb369b6b9825e56c4274d52ecbb75f7b97  backend/README.md
e1c843d8e025439aca074d4ed6bdd866db4dc5151c32d10a5b288aaaad4ece74  backend/README.zh-CN.md
d7bc0abf9a8d529d9b916f9db7f8d260366758284a3169093f7932ac4938e288  backend/alembic/versions/20261119_1700_d8f2a4c6b915_observation_receipt_separation.py
5d07eff0aef80c49edd34c21c5bd67f0f3069c0d64139987049828f69fc58057  backend/app/equipment_observation/README.md
3e2af054d2a508efcd716764d3fb80fc696065c36ef652423eb6289aef598b49  backend/app/equipment_observation/README.zh-CN.md
02173650766620ddefe24fc6e02b50066c16c4f525119264d89fd0cc294fec2e  backend/app/equipment_observation/models/__init__.py
91168200142451f72ecdbafbaeb0f0acc95b6eca3a549e179b1e91a510a2e25d  backend/app/equipment_observation/models/records.py
016bc41234efc14552b262d956b501d8a39d1003dac064d99ebb19315e034cca  backend/app/equipment_observation/profile.py
77c893ccd72f72631ee6cea3ed8d68bd9f2f00fbf41bb12c5eaa18f1dd8350be  backend/app/equipment_observation/services/ingest_v2.py
3362064b0fae1322b99652983fe0412cd0ad68dbead83a1d432175aed447a5b6  backend/app/plc_facts/services/async_consumption.py
c99242e72cbd80a317a464e2651ef3677ded45af906599973c3426d047672c89  backend/app/plc_facts/services/async_v2.py
b23a16e827f0078e356217845127c52f532daec72fe6c6e8639907649f08beff  backend/app/plc_facts/services/sync_v2_maintenance.py
8566e67e21f8f6e0200a8eda925849f408f5d2341bff01bf76e4482565eaad24  backend/app/plc_facts/v2_config.py
bf44047648ec7ef25588da9a680397b241fbbd573508669c2c6e1f783b40c57b  backend/common/integration/storage.py
aee23914ca6370ec49933f42313141d37dbcf63472c701b667abaab9263ba03e  backend/tests/test_acquisition_consumption_contract.py
2c7462f835c315efd2043ec1b60db9fe2bf6285b529f12b8fef4908de5e6c7a1  backend/tests/test_business_integration_storage.py
235ff261a3983f9fdec2763609950ec4938062fcbdb4a8bd7b062c0bce45680b  backend/tests/test_equipment_observation_domain.py
eb0d9c23f7b98dd4ee8e261687af1fa39020ef430dd3ea4b8efc37b96c5cfb39  backend/tests/test_equipment_observation_r10.py
340aabc97f9a59f09a930a49ef7d2e56a2e296c3584165e7db58017069790446  backend/tests/test_equipment_observation_r10_flow.py
20081e8931518860a3d633007b6e379f219646fee675a768614d87af280d934d  backend/tests/test_equipment_temperature_migration.py
ac675ea1605a48afbbbc573f7cfb1a01d091da3f356bd758551526bca4136351  backend/tests/test_generic_task_migration_r3.py
64e0a1d7838feac1f120a31ad3ce814d5501d38ffb95b58d0a9056c4efc5e82f  backend/tests/test_generic_task_revision_guards.py
891bcf93cd74138072ac7df62eb4dc4eed64ad88c414adf705aa067e4c05683c  backend/tests/test_legacy_acquisition_retirement.py
35b740b78096a88dc6430eeda365bc956385d871788dac2d4f19236d94e5072d  backend/tests/test_mapping_migration.py
430745e4fbb1ec7ade3594c8acfdef9446e19ada04216541c238484cb7e19a99  backend/tests/test_observation_receipt_separation.py
c2e89ea7566b31e42bb5d085debecdd15b14a8489e5aa51b1b756043ce2cd475  backend/tests/test_observation_retirement.py
e54cd88d4aa63feb94d1268288cde817588a047ed7f9dae7554eac7126985690  backend/tests_mysql/test_observation_receipt_separation_mysql.py
38dbb89c46be03b71455cd92ba523f6897aa03e7eb4339ee79cb05f67a58c1f2  contracts/published/http-api/equipment-observation-v2/README.md
1d96ad153fecd16589214c06212ea8e27266e4bb023698ee3ebd7dda30c3f41f  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
34a7aeb21b93ff1a68cc3b4075ff177e39b04f4499fdb940e1647cd03e1099ae  docs/equipment-status-process-monitoring.zh-CN.md
```

运行 ACQ suite 时，测试模块收集阶段会在创建其随机夹具库之前导入 backend Settings。隔离 QA 的进程环境应显式提供以下合成基础设置，不能依赖正式工作树的 `.env`。数据库用户名、密码和端口均使用独占实例；`never_demo_obs003` 故意是未创建的名字，以防导入阶段误连。suite 内部核验实际 UUID 后自行指定随机库连接。

```bash
export APP_NAME=obs003-fixture APP_VERSION=0.0.0 DEBUG=false TESTING=true
export PRIMARY_DATABASE=mysql MYSQL_ENABLED=true MYSQL_HOST=127.0.0.1
export MYSQL_PORT="$ACQ006_TEST_PORT" MYSQL_USER=root MYSQL_PASSWORD="$ACQ006_TEST_PASSWORD"
export MYSQL_ROOT_USER=root MYSQL_ROOT_PASSWORD="$ACQ006_TEST_PASSWORD"
export MYSQL_DATABASE=never_demo_obs003 TEST_MYSQL_DATABASE=never_demo_obs003
export JWT_SECRET_KEY=isolated-test-only JWT_ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=5 REFRESH_TOKEN_EXPIRE_DAYS=1 API_V1_PREFIX=/api/v1
export BACKEND_MOCK_ENABLED=false ADMIN_BOOTSTRAP_ENABLED=false TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1
```

采集测试另设角色 `ACQ006_TEST_ROLE=qa`、端口、UUID、独占密码及 `ACQ006_TEST_EXECUTION_ACK=ARCH-ACQ-006-r1:qa:127.0.0.1:<port>:<UUID>`；d8 的临时 hook 只改变夹具所用后继及对应的 OBS 目标/schema/window 变量，保留 ACQ 的错误确认负例。正式角色可自建同等 hook 或复演独立 HTTP 流程，用同一 ACQ suite 路由语义。Development 的 hook 逻辑位于 `/private/tmp/arch-obs-003-dev.xtw4tT/pytest_obs003_acq.py`，不包含密码。


## r4 返工后的 Development handoff

[独立 QA 的 AC05 失败证据](checklist.md) 保留。原 r4 候选 `5129fa347…`、补丁 `a6cdbb8…` 和其开发/验证记录不覆盖。仍在已批准 r4 的预检与隔离验收范围内，另建任务独占候选 `/private/tmp/arch-obs-003-r4-qa-guard-rework.X6uHwY/source`。相对上一 r4 QA 候选只改 d8 迁移与自己的 MySQL suite 两个允许文件。没有修改 HTTP 业务实现、发布合同或 ACQ 文件。

| 检查 | 返工后的 Development 结果 |
| --- | --- |
| 回执防护 | 业务表及两份回执共享完整索引、CHECK 校验。原生旧表和数据复制前的能耗表均要求无 CHECK；核对列顺序、类型、默认值、完整 EXTRA、排序规则，以及索引列、升降序、可见性、BTREE 和表达式。真实非空 fixture 注入旧回执的 `CHECK (char_length(event_id)<100)`、不可见或降序唯一索引及不可见列，逐项在迁移 DDL 前拒绝。另在 CREATE LIKE 后受控注入目标表 CHECK，确认在复制和 FK 变更前拒绝，原表所有数据与 DDL 完整不变。仅在隔离 fixture 确认可丢弃的副本无人引用且为空后移除它，正常前驱恢复并完成迁移及 HTTP 重放。 |
| OBS 真实 MySQL 8.4.6 | 完整本任务 suite **7 通过、174.49 秒、退出 0**。`r4-obs-mysql.log` 记录空库链、两种排序规则完整非空升级、旧回执逐字段及三路独立重放、原 ID／自增水位、多路并发、权限、错误结构、五处迁移故障后的备份恢复。 |
| AC04 HTTP 补证 | 原 c9 与新 d8 已对比 **25 项管理员 GET 观测及 2 项机器发现**，从真实身份和数据取得结果。包括卡片、曲线、区域／指标／槽位配置、选项、观测列表列、能源统计和计量配置、设备及过程管理员列表和按真实回执记录 ID 读取的详情。无产品路由／逻辑变更。 |
| 精确采集前驱 | 官方 ACQ 固定清单仍为 `a984198eaa14266df0a429720158582a4530e733cd83a66c1313a7009082231c`，35/35 正式 preimage 一致；候选中的 `da6` 迁移 `f4212cdff3a513f75f79e182f80e9088d301437bd688ce91b5b5d19c80d4adca` 和实际 suite `c3320018a2eceb6957bd22c66f79a617cd54543ae85f32576dfc1e8be981a8a0` 保持。实际隔离采集测试 da6 **9 通过、37.11 秒**，d8 **9 通过、37.57 秒**，均退出 0。原生错时点／事件／所属表触发器阻止激活，正常回填、新写入、原事实保全、duplicate、消费续读和清理均已复验。 |
| 回归与静态 | 聚焦 13 文件组 **196 通过、9 跳过、1 条 SQLite datetime 弃用提示，16.52 秒**，退出 0。compileall、模块只读预检、Alembic 唯一 d8 head、源码差异空白检查均通过。 |

独立 Verification 使用此**返工候选**重新核对。测试 fixture、合成 Settings、旧 c9 Git 归档与 ACQ 定向 hook 按上方 r4 handoff，使用 Verification 自己的 MySQL 8.4 专用实例与随机库。Development 的日志在本轮隔离目录，重要事实已记录于本页。

- 新清单 `obs-r4-handoff.sha256` SHA-256 **`261500f8f13e61848faa103216c58014213e4b7a49a7d5bc04867b5b7da8479c`**。正式可能改动 31 个路径。
- 新补丁 `/private/tmp/arch-obs-003-r4-qa-guard-rework.X6uHwY/ARCH-OBS-003-r4.patch` SHA-256 **`72353582063352aa172f3cad69052ab01fc635ccefb727e7921d76933e21de67`**。正式工作树 `git apply --check` 通过；`integration-preflight-r4.py` 检查 31 OBS、35 ACQ、12 交叠且 0 不匹配。在独占正式 preimage 副本应用该补丁后，31 个输出逐字节匹配。工作树热重载服务仍未操作，正式整合仅等获批窗口；届时重新检查 preimage 与目标，按上方切换流程采用此补丁。
- 本任务临时资源范围新增该返工副本、补丁、日志和独占测试目录。仍使用同两台已登记的 Development 专用隔离容器，所有本轮随机 schema 已由夹具回收。真实 dev 数据、profile、服务、演示继续挂起。

```text
83295a32eb310c8947844e90ee9ebe5f8d40676eaf2a64b6cd0148a2adca83fd  CODE_INDEX.md
5f70a800f41e7654aec308e89683bbdb369b6b9825e56c4274d52ecbb75f7b97  backend/README.md
e1c843d8e025439aca074d4ed6bdd866db4dc5151c32d10a5b288aaaad4ece74  backend/README.zh-CN.md
8fa1fced475cb2e4860da64032141e75508f8771c6750919a17fda7ce6ce61d9  backend/alembic/versions/20261119_1700_d8f2a4c6b915_observation_receipt_separation.py
5d07eff0aef80c49edd34c21c5bd67f0f3069c0d64139987049828f69fc58057  backend/app/equipment_observation/README.md
3e2af054d2a508efcd716764d3fb80fc696065c36ef652423eb6289aef598b49  backend/app/equipment_observation/README.zh-CN.md
02173650766620ddefe24fc6e02b50066c16c4f525119264d89fd0cc294fec2e  backend/app/equipment_observation/models/__init__.py
91168200142451f72ecdbafbaeb0f0acc95b6eca3a549e179b1e91a510a2e25d  backend/app/equipment_observation/models/records.py
016bc41234efc14552b262d956b501d8a39d1003dac064d99ebb19315e034cca  backend/app/equipment_observation/profile.py
77c893ccd72f72631ee6cea3ed8d68bd9f2f00fbf41bb12c5eaa18f1dd8350be  backend/app/equipment_observation/services/ingest_v2.py
3362064b0fae1322b99652983fe0412cd0ad68dbead83a1d432175aed447a5b6  backend/app/plc_facts/services/async_consumption.py
c99242e72cbd80a317a464e2651ef3677ded45af906599973c3426d047672c89  backend/app/plc_facts/services/async_v2.py
b23a16e827f0078e356217845127c52f532daec72fe6c6e8639907649f08beff  backend/app/plc_facts/services/sync_v2_maintenance.py
8566e67e21f8f6e0200a8eda925849f408f5d2341bff01bf76e4482565eaad24  backend/app/plc_facts/v2_config.py
bf44047648ec7ef25588da9a680397b241fbbd573508669c2c6e1f783b40c57b  backend/common/integration/storage.py
aee23914ca6370ec49933f42313141d37dbcf63472c701b667abaab9263ba03e  backend/tests/test_acquisition_consumption_contract.py
2c7462f835c315efd2043ec1b60db9fe2bf6285b529f12b8fef4908de5e6c7a1  backend/tests/test_business_integration_storage.py
235ff261a3983f9fdec2763609950ec4938062fcbdb4a8bd7b062c0bce45680b  backend/tests/test_equipment_observation_domain.py
eb0d9c23f7b98dd4ee8e261687af1fa39020ef430dd3ea4b8efc37b96c5cfb39  backend/tests/test_equipment_observation_r10.py
340aabc97f9a59f09a930a49ef7d2e56a2e296c3584165e7db58017069790446  backend/tests/test_equipment_observation_r10_flow.py
20081e8931518860a3d633007b6e379f219646fee675a768614d87af280d934d  backend/tests/test_equipment_temperature_migration.py
ac675ea1605a48afbbbc573f7cfb1a01d091da3f356bd758551526bca4136351  backend/tests/test_generic_task_migration_r3.py
64e0a1d7838feac1f120a31ad3ce814d5501d38ffb95b58d0a9056c4efc5e82f  backend/tests/test_generic_task_revision_guards.py
891bcf93cd74138072ac7df62eb4dc4eed64ad88c414adf705aa067e4c05683c  backend/tests/test_legacy_acquisition_retirement.py
35b740b78096a88dc6430eeda365bc956385d871788dac2d4f19236d94e5072d  backend/tests/test_mapping_migration.py
430745e4fbb1ec7ade3594c8acfdef9446e19ada04216541c238484cb7e19a99  backend/tests/test_observation_receipt_separation.py
c2e89ea7566b31e42bb5d085debecdd15b14a8489e5aa51b1b756043ce2cd475  backend/tests/test_observation_retirement.py
aebdbf832fc25af52e8df037030a76672fca91ee3224dd0400e27f0228d16daa  backend/tests_mysql/test_observation_receipt_separation_mysql.py
38dbb89c46be03b71455cd92ba523f6897aa03e7eb4339ee79cb05f67a58c1f2  contracts/published/http-api/equipment-observation-v2/README.md
1d96ad153fecd16589214c06212ea8e27266e4bb023698ee3ebd7dda30c3f41f  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
34a7aeb21b93ff1a68cc3b4075ff177e39b04f4499fdb940e1647cd03e1099ae  docs/equipment-status-process-monitoring.zh-CN.md
```

## r4 正式 dev 两阶段切换与复核交接

2026-11-19（Asia/Shanghai），Human Owner 批准同一停写窗口执行 ACQ → OBS、一次轻量全库备份，不安排本次正式库备份的完整恢复演练。执行前，Owner 明确说“已停写。DBX 的 dev 连接已断开，采集上报、消费客户端和其他写入方都已暂停。请按已批准的方案备份一次并执行两阶段切换，数据和接口复核通过后继续温区 1 的演示。” Development 的作用止于库、正式源码和配置切换后的静态和连接验证。运行服务由 Human Owner 恢复，在线只读接口和后续演示另行核对。

- 目标为 `127.0.0.1:3307 / industrial_level_2_system`，MySQL **8.4.6**，UUID SHA-256 前缀 `ac2319a3fdc8`，时区偏移 +08:00；由外部回环和指定现有容器内 TCP 客户端双查同一 UUID、版本、schema。停写确认后每阶段重核，无其他会话、活动事务、待锁，也无 8000 或 5190 的监听。已固定的 ACQ 35 项输入及 OBS 31 项正式 preimage 同先前证据。
- 任务专用 0700 目录 `/private/tmp/arch-obs-003-r4-dev-cutover.pD8XeX` 保存一份 0600 全逻辑 dump `dev-full-c9.sql`。实际使用指定现有容器自带 8.4.6 `mysqldump`，单事务、InnoDB、包含数据库定义、表、行、外键、触发器、例程和事件，退出 0，头尾标记齐全，**253,317 字节**，SHA-256 **`25fcec35868de049cd826611daf33c4a23f8c48cdf4580e15f63be91d99bcbd5`**。备份后受保护全表指纹与冻结前一致。两份原私有 profile 字节也在该 0700 目录以 0600 保全，不暴露路径或凭据。
- 维护入口以 `OBS003_LINKED_WINDOW=OWNER_CONFIRMED_STOPPED:c9:da6:d8:3307 PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python <任务私有目录>/cutover.py execute-confirmed-window` 执行一次，退出 **0**。脚本 SHA-256 `c2ff4c85872b009e8219ea68fd51cd90e7b4b378bbfeb25f3a898eeea9a6ea91`。应用独立验证通过的补丁 `72353582063352aa172f3cad69052ab01fc635ccefb727e7921d76933e21de67`，核对正式 31 项后置 SHA-256、原 ACQ 前驱文件不变、模块预检通过且正式 Alembic 唯一 head 为 `d8f2a4c6b915`。未写仓库 Git refs。
- **ACQ**：在正式源码运行显式 `alembic upgrade da6c32f8a701`，退出 0；只增加六张消费表、三个预期定义的守卫 trigger，截止 **2026-11-19 22:57:43.231507+08:00**。真实采集历史 **107 条**、最新点值 **6 条**、来源 **3 条**逐表保全；截止规则计算到 **107 条事件、2 条流**，固定序号与截止核对通过。消费者、投递及操作表为空。原有 56 张业务表（不含 `alembic_version`）的数据和 DDL 完全一致。
- **OBS**：ACQ 链路数据验证通过后才执行显式 `alembic upgrade d8f2a4c6b915`，退出 0。验证五张既有表的改名和业务行指纹，核对索引、约束及三种样本 FK 预期变化；非对应表 DDL 和数据、ACQ 六表三 trigger 及证据保持。切换前实时、过程、能耗样本和共享回执均为 **0 行**，切换后两类回执仍共 **0 行**；拆分后两张表的下一回执 ID 均为 **266**，与原共享表水位相同。现役范围共 63 张业务表（不含版本表）。没有新增或删除用户业务数据、回执或配置。非空旧回执、逐 ID 重放与并发则由上述隔离验证提供证据。
- 数据确认后，只更新实际启用的两个观察／Facts 外部私有 profile 的唯一 `target.schemaRevision`，由 c9 到 d8，保留原属主、组、0600 模式及余下原始字节。两份正式加载器和应用账户的真实目标探针均通过；没改 `.env`、读写授权、消费凭据或前端配置。执行完仍保持用户服务未启动。请在服务恢复后由独立角色进行只读运行验证，切勿误记为本步骤已验收实际 HTTP 或已开始温区 1 演示。

| 私有证据 | SHA-256 |
| --- | --- |
| c9 `before.json` | `e9ba6d079e73dfb0d74ac9f0d756b3740c315e11818473fd017200ae060a597a` |
| da6 `stage.json` | `56fa500f6673b46c2a6a052a86b4e3c79917aafaa992c7a1e64a28ddac1fa8ba` |
| d8 `after.json` | `8099439c044cde8296ff84a317d8de35b2150cc69a7c7c9a44fae59b788c5beb` |
| `configuration.json` | `1825675b9672960df7ba4610d9526c237f37cb9c984ce8882bbb3283a157103b` |
| `migration-acq.log` | `ed875c3d2cbeb2834ffba4d85ff5457629d40f4970ede7951b5b300f0d4fecdf` |
| `migration-obs.log` | `5fc59cdf36c226a32cabb932e68a39b5d66877460b8fea23e89a67f6d43e28fa` |
| `profile-loaders.log` | `1cb4f9663533bc5f513d4a0eb873e84e4f94682afb32902b5a3b610b41520f6d` |
| `completed.json` | `53b4c0c2d6a37fae050ca6ba7e0135ec6967fa92087d38675c2fef73892f1a32` |

完整 dump、阶段证据及原 profile 保留至用户确认在线复核、完成演示并决定保留期限。未执行真实恢复、回滚、stamp 或重跑，也未处理测试隔离资源清理。
