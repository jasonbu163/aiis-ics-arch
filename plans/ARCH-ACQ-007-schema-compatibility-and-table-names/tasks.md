Task ID: ARCH-ACQ-007
Revision: r2
Status: developer_handoff
Owner Role: Development
Handoff: r2 精确隔离候选交 fresh-context Verification，正式运行源码暂不采用。

# ARCH-ACQ-007 r2 隔离开发交接

批准规格 SHA-256 为 `1b4b2b44fc7676831d1332817ded3d215a78b50ab9edd0d8b3b7350a688717b7`。任务交付的是 `/private/tmp/arch-acq-007-r2.Oz9DlE/candidate` 的隔离源码和证据。正式基线 HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e` 的 35 个产品路径连同开始时的并行改动已按 SHA-256 核对。用户指定本轮暂不合入或运行正式源码。

## r2 与 r1 的差异

- 唯一生产差异在 `backend/alembic/versions/20261113_1600_7b9d1f3a5c7e_plc_source_registry_single.py`。将一次历史建表、插入和结果对账使用的表替换为独立 metadata 的固定 `plc_source_registry`，保留 SQL 类型和字符校对规则、空值和时间默认值、JSON 客户端默认值、主键、检查约束及 InnoDB，继续执行原先的登记归并、采集事实摘要对账与六张前驱表清理。`revision=7b9d1f3a5c7e` 和 `down_revision=6a8c0e2b4d16` 保持原值。
- 更新本任务的两份测试 `backend/tests/test_acquisition_schema_compatibility.py` 和 `backend/tests_mysql/test_acquisition_consumption.py`。使用真实空库、已有数据、旧 profile、DML 权限账号、观察点内部取证和维护 CLI，补上 r1 隔离证据。其他历史迁移及已发布 HTTP JSON/YAML 按字节核对通过。
- 延续 r1 候选的日常九表结构验证、样本事件保护、显式维护按实际版本确认及三表原子更名。最新唯一 migration head 仍为 `a1c307f8d2e4`，直接前驱 `f0a2b4c6d8e1`。

## r2 DEV self-check

候选使用正式项目现有锁定的 `.venv`。启动器清空继承环境后注入合成项目设置，`uv run --offline --no-sync` 不同步依赖。离线启动器禁止 Python IPv4/IPv6 连接。MySQL 启动器只允许连接 `127.0.0.1:33407`，实际核对 MySQL `8.4.6`、UUID `bd735869-e7ba-11f1-bc50-4a1e65dec043`、上海数据库时钟偏移 `+28800` 后使用 `ACQ007_TEST_EXECUTION_ACK=ARCH-ACQ-007-r2:<role>:127.0.0.1:<port>:<uuid>`。连接凭据由协调者提供，未进入候选、补丁或记录。

```bash
./offline/run python -m pytest -q -p no:cacheprovider \
  --basetemp /private/tmp/arch-acq-007-r2.Oz9DlE/offline/pytest -m no_db \
  tests/test_acquisition_schema_compatibility.py tests/test_plc_facts_v2.py \
  tests/test_acquisition_data_browse.py tests/test_acquisition_source_registry.py \
  tests/test_acquisition_consumption_contract.py tests/test_generic_task_revision_guards.py \
  tests/test_quality_revision_guards.py tests/test_equipment_observation_r8.py \
  tests/test_legacy_acquisition_retirement.py tests/test_observation_retirement.py \
  tests/test_observation_receipt_separation.py tests/test_generic_task_migration_r3.py \
  tests/test_equipment_temperature_migration.py tests/test_mapping_migration.py
./mysql-test/run bd735869-e7ba-11f1-bc50-4a1e65dec043
./mysql-test/run bd735869-e7ba-11f1-bc50-4a1e65dec043 preflight-only
./offline/run alembic heads
./offline/run python scripts/plc_facts_maintenance/main.py --help
git -C baseline apply --check --whitespace=error-all ../arch-acq-007-r2.patch
```

- 离线定向检查 249 通过、3 条历史或条件用例跳过，18.29 秒，退出 0。核对历史 DDL 与原 ORM 等价、MySQL 版本拒绝和新旧目标守卫。逐个编译 35 文件中修改的 Python 源码并核对新增文档链接，通过。新旧公开合同工件 SHA-256 对照通过。
- 首轮同源码隔离 MySQL 11 通过，62.23 秒，退出 0。确认空库执行单次 Alembic upgrade 成功，且已有数据前驱和后继均采用同一份候选。最终补跑扩展后的实测见下。
- 最终同一候选隔离 MySQL `19 passed in 89.58s`，退出 0。命令未使用 staged plugin、冻结历史源码、手工建目标登记表或 stamp。
- 最后一次 `preflight-only` 核验退出 0。随机测试 schema 和 DML 账号已由 fixture 回收，只剩四个系统库，`mysql.user` 无任务创建账号。协调者保留独占实例和临时凭据供 fresh Verification，验证完成后回收。

| 验收 | DEV self-check 证据 |
| --- | --- |
| AC01 | 已有数据轮在 `6a8c0e2b4d16` 注入合成来源，验证原历史迁移归并活跃及退役代次并保留登记时间和版本，再前进至质量前驱并写入消费状态。快照证明三张改名表及六张消费表的数据和索引一致。停写未确认、错绑、时点/事件/定义错误、冲突对象和部分改名均拒绝。改名后 history 不可变和到期守卫按预期拒绝。 |
| AC02 | 真正应用隔离无关后继 `eeeeeeeeeeee`，旧 profile `da6c32f8a701` 文件逐字节保留。DML 账号真实调用来源管理 POST/GET/PATCH、普通样本 POST/duplicate、latest/history、消费 API、受控清理及设备观测所调用的采集取证服务。来源管理使用合成管理员依赖替身，路由、schema、service 和数据库保持真实。测试验证实例/库名错误和实际会话时钟错误拒绝。不同 MySQL 版本使用离线元数据替身验证。设备观测独立版本守卫按原规则拒绝无关后继。 |
| AC03 | 实库分别施加缺表、缺列、关键类型错误、唯一键缺失、ready 为 0 和单例缺失，每项 latest 读与普通 POST 返回 `503 plc_facts_v2.not_ready`，无 history、latest、事件或流残留。在线 DML 账号无触发器元数据访问权仍可正常使用。删除追加触发器或删除、篡改已存在事件时，普通写入或 duplicate 拒绝并检查回滚和水位。 |
| AC04 | 同流并发、来源身份变更、回滚、消费租约/pending/ACK、受控清理及缺口通过。维护触发器检查拒绝错误所属表、时点、事件、定义及不可读取元数据。显式同步维护拒绝错误实际 revision、UUID 和库名。实际 CLI 计划在传入正确版本时通过，传入旧版本时返回维护错误非零退出。 |
| AC05 | 另起独立空库，同一候选执行一次 `alembic upgrade a1c307f8d2e4`，确认从根、经过 `7b9d1f3a5c7e`、再到唯一新 head，旧三表名均消失，九表及 ready 存在。已布库轮在改名前显式检查旧表定义与归并事实。编译、文档链接、合同机器工件及历史唯一例外审计通过。 |

## 候选指纹和 Verification 交接

补丁文件 `/private/tmp/arch-acq-007-r2.Oz9DlE/arch-acq-007-r2.patch`，SHA-256 `48790ed3bac404c0635f3aa8ae46d02106f12baf71eaab1cccc1bbda5ce3f848`。前后文件清单在同目录 `arch-acq-007-r2-files.sha256`，SHA-256 `9b7ffa42564214bb73d098b4993582b7695d49121b81e979bf2e79f21cf230a0`。由协调者交 fresh-context Verification 复核这份候选与规格。正式源码合并和实际环境切换未获批准。正式 dev 库、8000 服务及现有私有配置未参与。

实际采用前由目标 Owner 核对表级授权、外部直查和共库存量版本守卫。运行账号无法识别窗口外特权账号对不可变和到期触发器的篡改。DDL 失败保持停写，核对九表、触发器、实际 revision 和已提交事实后再决定恢复路径。暂留候选、基线、补丁、指纹清单和测试启动器供独立核验。

每行依次为正式基线 SHA-256、隔离候选 SHA-256、仓库相对路径，`-` 表示基线文件不存在。

```text
3c31bf18eae8a7140252ce0453bd5cd101ea7df5fecfda71b429f4299d2e3d56  b56fe58ecc8ff7f0daf6bf342724b530b2d3f5581a1fdebd0340c8b63884c7e6  backend/alembic/versions/20261113_1600_7b9d1f3a5c7e_plc_source_registry_single.py
-  c2f40cdb3e35da2a2bb35bcb21190ae5ff8abefd7fe0fca6bba196879c1ca90c  backend/alembic/versions/20261124_1000_a1c307f8d2e4_acquisition_table_names.py
79226114d3200159589c46a22d792e5e5b87c16640cb349c3666aa8c733aeecc  efa4a24abcae402fd4ce7baaca293893a89d5930a0cce15ea5044f92e64c4145  backend/app/plc_facts/README.md
45dfb18375a0d3a65b920844c3ccbd724879c5ccef00a3b9c80a42661ed020a5  c8ff96c6ca51d96dbc505daa6fb970006b0fc2a86a889eee8390bbd23a955f3f  backend/app/plc_facts/README.zh-CN.md
1c2e4a5bc7633ed6a3be2ad47fe3fb622938c9638a3305e99fcbdc6b7327f909  95b4277002a8368b1687e57d80952dc2db73f1a9e1c4f12b4520ad7a8f37cc5a  backend/app/plc_facts/crud/async_consumption.py
18507f93bb8c46175277e17545aa31580f08b2599ac6fc4bdaef898dae677111  cb615b33327d25d350c7b86d5db6579a054b6d151811670fe84ed51fcc019219  backend/app/plc_facts/crud/async_v2.py
6ac60feebb1ec47576960502f87ebe56df605062d2a769e105a89211881364bd  be72e2570cd47b86afd833579fb410502e2a015dd68364ddce2375614ef6c872  backend/app/plc_facts/crud/sync_v2_maintenance.py
b54cae59e8efa2f27f3bdc47c0826295d2aa50cdf6806e06b7a6206ddae29502  090929c6d70a3fe9cb4735a35ea0f0c0ae2bda63e5bd1d512cf0d0d8e66d5347  backend/app/plc_facts/models/source_registry.py
96215de88cd3e78beff3056c97b23db6b017a5649a8e078932d4c421df7fb4b7  72aed210660b28f206dc105b4de51fcd02b05789ffb9426a13884f3d38ed1cfd  backend/app/plc_facts/models/v2.py
3362064b0fae1322b99652983fe0412cd0ad68dbead83a1d432175aed447a5b6  95279b9b646b0997ed80d07fa0c736d49059f29488344da04193281572bff521  backend/app/plc_facts/services/async_consumption.py
c99242e72cbd80a317a464e2651ef3677ded45af906599973c3426d047672c89  2e4fc3d2fd6bc48ff4d51adebb7e021febfff6edf766c96791a9a389ba4ef7fe  backend/app/plc_facts/services/async_v2.py
b23a16e827f0078e356217845127c52f532daec72fe6c6e8639907649f08beff  8aff66ddd0331835f416d8830261c886c3bbda1faacb80415047d2c7893ef8e1  backend/app/plc_facts/services/sync_v2_maintenance.py
fc95b7b7b3d0223496dee44579cd17a4363f9fe537cc1f91d3edb0ba9e29ad96  34b7e5c8b403dd31a021648ab0059b0f849b39ab36f031ff4269fa488907447e  backend/app/plc_facts/v2_config.py
6ebe7a6c2337aac344cbb3bdc289bdfbeeb704d1dedc823b52e10dd04d393fac  48fc518920667702057618070b621e1e248bff4d80d7d4ed60a2331fefe768f8  backend/scripts/plc_facts_maintenance/README.md
242b129b39803fa38886fd47f05661e021c9fec577f508131034fca6af4744ff  81d1f2d405751b09976c9c3bdc401508afc3aba399857e03b13c1086175fecc5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
fcbf509b033de57147e5bc3e9a9c49e62ed4b4e491a0a731f4fc88448be119ef  7937b481d151c73ee0792bf3c8d041e70d357051280a5492f6b60dc938e44e74  backend/scripts/plc_facts_maintenance/main.py
9a246d62a7d0b665552e3543dc0e24cbc2c0c430affec2f1a506124e3849666b  51054e315a1a2145bd1ea74f2ae5dffcc00542b35abda865273aa90574faefa7  backend/tests/test_acquisition_consumption_contract.py
638ddc78b3218ca303a2acb5b546edbba4304433b76d93fc0664723c1c7360f8  96336afb8997df0ec261a1bca35f392cee1c374b8a04a3a2c6a8c8270d49ebc6  backend/tests/test_acquisition_data_browse.py
-  9c40b3b6b38f22223c213fe231fe0bf6fc71d33ef15c36709a8355fcdbc889a2  backend/tests/test_acquisition_schema_compatibility.py
d08e7a4bc413759eb50f463cd6da684fc2e6bfdc334e7cb0872b0a0bb60373ba  9fdcd4e8700e276209c17e6b441efe17b21763f6084312ce024bc22af4262814  backend/tests/test_acquisition_source_registry.py
d160cd81b4d10004388944e0eb109a227f32830c200df8416caa3fb749ece7b5  5745b03ba3ee081176489f4ec7a29d60045ca194c1f9c1c1ba38d87d5727ce78  backend/tests/test_equipment_observation_r8.py
1dc5a56bf3c298e47cd4409ba0d803cd423a793a070ceddd9ff6fe72ccc0a925  95670aff231d9234ac391f0dc19e6d60f7af3050bd517a5e13804389a2700b18  backend/tests/test_equipment_temperature_migration.py
705d7c0b81f2a388ce479e9d76a2a8f1cd31688a6a3e7681464e342ecda57d59  95545c561d62c8e6e565685a4fa2608d135c1925599fadf68c9416c8a19cdde6  backend/tests/test_generic_task_migration_r3.py
0b9cf7f9594b4490da4ebb7da05e2e75d6a1ffbb397875f6e7689bfab9d9d60c  dde0036b90108db79575bd99cc33d94a6df5a1622967ccbb0852ed3b508d104d  backend/tests/test_generic_task_revision_guards.py
5317e016e304cd1ba18dba2d84b97815b2a9b327039f3922f0a7c9c2285fa9ab  a6516cbd4f079bcad1b3a48b0670e5d0c0002d26e4ae77a499562be2053fef6c  backend/tests/test_legacy_acquisition_retirement.py
fad941a0d281de9d0d4f897e8c81d3f6105c1bd9ae9184cfaeb408efe3375757  ebeff55d6d3c09f3489672fdf3b2f9cbe74d267c2dacfd35bb986fdcb8836c1a  backend/tests/test_mapping_migration.py
e256e709d26b097dc7836c182fecc08d63e2457c0d8b05cd2ba9beef4bcaaf6e  c046025ef2f6f3993a80f965622a3205bcc5db7c76b081d0c04c08c4349b0b65  backend/tests/test_observation_receipt_separation.py
16c0d155080b9022800054addc8913656abbf942a4a35fb5a129df4b2a30ecde  a1aa8a7c266cfc9023f993f254eff1bf509dc7b24faf8ac205aae7139037de23  backend/tests/test_observation_retirement.py
08a3f949a5364bca3444aacd6897c22b9a9a522b16a969558c99196c8fb82d00  ff3d1830c440bed8b3eb00b2f4e9fbe2b50a02c4a20fcaa73194d5916ba65fad  backend/tests/test_plc_facts_v2.py
c8f6f633eda36001b827f2c0f2d0919bf13bae48d34e56af0f4fdfd4b9c36dce  214011ea6b6d96284b0d88baa9de3fc702c9fb38b237264ef83ff4c995cbe12d  backend/tests/test_quality_revision_guards.py
c3320018a2eceb6957bd22c66f79a617cd54543ae85f32576dfc1e8be981a8a0  f77c8862bfd1b82cc37f48dd48696ed28fb7b50bd9b42a3b65271e40215950d3  backend/tests_mysql/test_acquisition_consumption.py
4cca67d827302521bd55b2cf897d9cb794fe4bb73cb06da0ea5023c015c3dc8c  77941952393865a3f7f43d505cf0fac3be7529997ceb2785f31a31c56b6bcde8  contracts/published/http-api/plc-facts-v2/README.md
cd3dce51ebfe1554a933046e4c246a5db9ec1f371cc7f408e3ff213efb30eed4  6c5cb3c1e66a652195c4895c5d607084ccae55c3afeeaef60196b8c575042b6c  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
4bb1c803b16516cab3b12294b3303d5862f67b21a60a1720f8f914a16a6a6969  5fd839e330a08ad534c97bb9d71c2c2a1a26862e28250d2c105dbedf26580859  docs/acquisition-data-guide.md
6ba3b09ace3cfd0156c8027d8aa353eab11e516211daa4c269bb655ad4d74943  0d74dcf526163bf78a6092396ed95dedbe8fac7468dd1950155e78a00c55789f  docs/acquisition-data-guide.zh-CN.md
```

以下保留 r1 的开发记录和失败证据。

Task ID: ARCH-ACQ-007
Revision: r1
Status: owner_approved
Owner Role: Development
Handoff: 隔离候选已交协调者核对。正式运行源码尚未整合。

# ARCH-ACQ-007 r1 开发候选

批准规格的 SHA-256 为 `a31d8603b704445d3775f0ba08317c7c1173e69772ce36a946073faa7d3ea9f7`。基准为正式工作树在 HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e` 的源码快照，包含并行质量前驱 `f0a2b4c6d8e1` 及已有改动。将现有公开文件复制为独立基线和候选，排除私有配置、运行数据、日志、依赖及 Git 元数据。候选由协调者后续整合，以免正式开发服务的热重载提前采用三张新表名。

## 实施范围

- 三张采集表在迁移 `a1c307f8d2e4` 内执行一条同库 `RENAME TABLE`。先核对实例、时钟、前驱、停写确认和命名互斥锁，再锁定 Alembic 版本行和 activation 行，核对九张表、可见外键及视图引用和三个 history 守卫。改名后重新核对九表、守卫所属新表与定义和实际前驱。MySQL DDL 会释放事务锁，命名锁与人工停写窗口贯穿关键操作。
- 日常访问沿用实例 UUID、库名和上海数据库时钟，检查九张 InnoDB 表、列类型和可空性、声明的关键主键与唯一键，以及 `id=1, ready=1`。使用采集服务共用的目标探针覆盖来源管理、查询、写入、消费和设备观测的采集事实证据。旧私有 profile 的 `schemaRevision` 保留作诊断。设备观测自身守卫沿用基线。
- 新写入和同字节冲突重试都核对唯一消费事件的流、序号、来源身份和到期时刻。保留来源及流锁、样本时间重检、冲突优先级和提交回执边界。显式 `cleanup-v2` 核验实际版本和新表结构，保留版本行共享锁和到期触发器标记。
- 更新 ORM 和双语采用说明。历史迁移、已发布 HTTP JSON/YAML 合同和私有配置均保持基线。`CODE_INDEX.md` 在本 Revision 的实施清单之外。

## DEV 自检

在候选 `backend/` 使用项目既有 `.venv`，运行命令前清空继承的环境变量并注入合成项目配置，数据库地址为 `127.0.0.1:1`，Python 阻止 IPv4/IPv6 出站连接。启动器在候选根目录外的 `offline/run`。uv 使用本任务独立缓存，参数 `--offline --no-sync`。

```bash
python -m pytest -q -m no_db \
  tests/test_acquisition_schema_compatibility.py tests/test_plc_facts_v2.py \
  tests/test_acquisition_data_browse.py tests/test_acquisition_source_registry.py \
  tests/test_acquisition_consumption_contract.py tests/test_generic_task_revision_guards.py \
  tests/test_quality_revision_guards.py tests/test_equipment_observation_r8.py \
  tests/test_legacy_acquisition_retirement.py tests/test_observation_retirement.py \
  tests/test_observation_receipt_separation.py tests/test_generic_task_migration_r3.py \
  tests/test_equipment_temperature_migration.py tests/test_mapping_migration.py
```

| 检查 | 实际结果 |
| --- | --- |
| 上述离线定向套件 | 248 通过、3 跳过，首次 17.65 秒，修订锁查询后 18.39 秒，两次均退出 0。覆盖旧 revision 独立于日常守卫、缺表或关键列、类型、可空性、键、ready、事件缺失或身份错误、迁移预检和中断分支、HTTP 契约及历史迁移图。 |
| `alembic heads` | 退出 0，唯一 head 为 `a1c307f8d2e4`，直接前驱为 `f0a2b4c6d8e1`。 |
| `python scripts/plc_facts_maintenance/main.py --help` | 退出 0，显示帮助。 |
| Python 编译和文档检查 | 对全部变更 Python 源码使用 `compile(source_bytes, filename, 'exec')` 通过。新增本地文档链接和锚点通过，已发布 HTTP JSON/YAML 与基线逐字节相同。 |
| `git apply --check --whitespace=error-all` | 在隔离基线通过。34 条路径的基线 SHA-256 与正式树相符。候选文件 SHA-256 与下方清单相符。 |
| `python -m pytest -q tests_mysql/test_acquisition_consumption.py` | 首轮离线自检时隔离环境未启用，模块级守卫跳过，pytest 退出 5。后获准的隔离实测见下节。 |

准备了独立 MySQL 用例，覆盖有事实及消费状态的迁移前后九表对账、真正应用一条合成的无关后继迁移、原 profile、仅有 DML 权限的在线账号、触发器拒绝和故障后的事实及事件检查。用例需单独获准的专用 MySQL 8.4 实例及 `ACQ007_TEST_ROLE`、`ACQ007_TEST_PORT`、`ACQ007_TEST_SERVER_UUID`、`ACQ007_TEST_PASSWORD` 和 `ACQ007_TEST_EXECUTION_ACK=ARCH-ACQ-007-r1:<role>:127.0.0.1:<port>:<uuid>`。已授权的后续实库证据见下节。较早阶段的隔离用例依赖其历史表布局和冻结源码，当前候选专用回归使用新布局。

## 候选指纹和后续边界

候选目录 `/private/tmp/arch-acq-007-r1.hQFO5Zv1/candidate`，同级 `baseline` 为快照。`arch-acq-007-r1.patch` 的 SHA-256 为 `1ba019f50949708adcd3b4f63d57c307e5838f474255fa768f6bada42048975f`。前后文件清单 `arch-acq-007-r1-files.sha256` 的 SHA-256 为 `477ef33c29fc0f5cb25b91842f4ade38685e278adef7252d9eaa9785247c471c`。依赖候选整合和独立 Verification 的临时资源暂留，由协调者确认没有验证、后续工作或证据依赖后回收。正式产品源码、正式数据库、服务和私有配置在本轮保持原状。

实际采用前，目标 Owner 须核对未知直查、表级授权和其他模块的全库版本守卫。现有设备观测与公共集成仍按自己的全库 revision 规则运行，升库前需由协调者单独处理采用依赖。任何 DDL 或后置检验错误均保持停写，依据备份和实际已提交事实确认前向修复或恢复。在线 DML 账号无法察觉窗口外对不可变或到期触发器的特权修改。正式源码整合、独立 Verification 和 Human Owner 最终验收仍待各自阶段。

### 变更文件

每行依次为基线 SHA-256、候选 SHA-256、仓库相对路径。`-` 表示基线文件不存在。

```text
-  c2f40cdb3e35da2a2bb35bcb21190ae5ff8abefd7fe0fca6bba196879c1ca90c  backend/alembic/versions/20261124_1000_a1c307f8d2e4_acquisition_table_names.py
79226114d3200159589c46a22d792e5e5b87c16640cb349c3666aa8c733aeecc  efa4a24abcae402fd4ce7baaca293893a89d5930a0cce15ea5044f92e64c4145  backend/app/plc_facts/README.md
45dfb18375a0d3a65b920844c3ccbd724879c5ccef00a3b9c80a42661ed020a5  c8ff96c6ca51d96dbc505daa6fb970006b0fc2a86a889eee8390bbd23a955f3f  backend/app/plc_facts/README.zh-CN.md
1c2e4a5bc7633ed6a3be2ad47fe3fb622938c9638a3305e99fcbdc6b7327f909  95b4277002a8368b1687e57d80952dc2db73f1a9e1c4f12b4520ad7a8f37cc5a  backend/app/plc_facts/crud/async_consumption.py
18507f93bb8c46175277e17545aa31580f08b2599ac6fc4bdaef898dae677111  cb615b33327d25d350c7b86d5db6579a054b6d151811670fe84ed51fcc019219  backend/app/plc_facts/crud/async_v2.py
6ac60feebb1ec47576960502f87ebe56df605062d2a769e105a89211881364bd  be72e2570cd47b86afd833579fb410502e2a015dd68364ddce2375614ef6c872  backend/app/plc_facts/crud/sync_v2_maintenance.py
b54cae59e8efa2f27f3bdc47c0826295d2aa50cdf6806e06b7a6206ddae29502  090929c6d70a3fe9cb4735a35ea0f0c0ae2bda63e5bd1d512cf0d0d8e66d5347  backend/app/plc_facts/models/source_registry.py
96215de88cd3e78beff3056c97b23db6b017a5649a8e078932d4c421df7fb4b7  72aed210660b28f206dc105b4de51fcd02b05789ffb9426a13884f3d38ed1cfd  backend/app/plc_facts/models/v2.py
3362064b0fae1322b99652983fe0412cd0ad68dbead83a1d432175aed447a5b6  95279b9b646b0997ed80d07fa0c736d49059f29488344da04193281572bff521  backend/app/plc_facts/services/async_consumption.py
c99242e72cbd80a317a464e2651ef3677ded45af906599973c3426d047672c89  2e4fc3d2fd6bc48ff4d51adebb7e021febfff6edf766c96791a9a389ba4ef7fe  backend/app/plc_facts/services/async_v2.py
b23a16e827f0078e356217845127c52f532daec72fe6c6e8639907649f08beff  8aff66ddd0331835f416d8830261c886c3bbda1faacb80415047d2c7893ef8e1  backend/app/plc_facts/services/sync_v2_maintenance.py
fc95b7b7b3d0223496dee44579cd17a4363f9fe537cc1f91d3edb0ba9e29ad96  34b7e5c8b403dd31a021648ab0059b0f849b39ab36f031ff4269fa488907447e  backend/app/plc_facts/v2_config.py
6ebe7a6c2337aac344cbb3bdc289bdfbeeb704d1dedc823b52e10dd04d393fac  48fc518920667702057618070b621e1e248bff4d80d7d4ed60a2331fefe768f8  backend/scripts/plc_facts_maintenance/README.md
242b129b39803fa38886fd47f05661e021c9fec577f508131034fca6af4744ff  81d1f2d405751b09976c9c3bdc401508afc3aba399857e03b13c1086175fecc5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
fcbf509b033de57147e5bc3e9a9c49e62ed4b4e491a0a731f4fc88448be119ef  7937b481d151c73ee0792bf3c8d041e70d357051280a5492f6b60dc938e44e74  backend/scripts/plc_facts_maintenance/main.py
9a246d62a7d0b665552e3543dc0e24cbc2c0c430affec2f1a506124e3849666b  51054e315a1a2145bd1ea74f2ae5dffcc00542b35abda865273aa90574faefa7  backend/tests/test_acquisition_consumption_contract.py
638ddc78b3218ca303a2acb5b546edbba4304433b76d93fc0664723c1c7360f8  96336afb8997df0ec261a1bca35f392cee1c374b8a04a3a2c6a8c8270d49ebc6  backend/tests/test_acquisition_data_browse.py
-  57c6928e12147a7cb1f2321e4c5b484ccbfc9becd447e49d9a285db09680fba1  backend/tests/test_acquisition_schema_compatibility.py
d08e7a4bc413759eb50f463cd6da684fc2e6bfdc334e7cb0872b0a0bb60373ba  9fdcd4e8700e276209c17e6b441efe17b21763f6084312ce024bc22af4262814  backend/tests/test_acquisition_source_registry.py
d160cd81b4d10004388944e0eb109a227f32830c200df8416caa3fb749ece7b5  5745b03ba3ee081176489f4ec7a29d60045ca194c1f9c1c1ba38d87d5727ce78  backend/tests/test_equipment_observation_r8.py
1dc5a56bf3c298e47cd4409ba0d803cd423a793a070ceddd9ff6fe72ccc0a925  95670aff231d9234ac391f0dc19e6d60f7af3050bd517a5e13804389a2700b18  backend/tests/test_equipment_temperature_migration.py
705d7c0b81f2a388ce479e9d76a2a8f1cd31688a6a3e7681464e342ecda57d59  95545c561d62c8e6e565685a4fa2608d135c1925599fadf68c9416c8a19cdde6  backend/tests/test_generic_task_migration_r3.py
0b9cf7f9594b4490da4ebb7da05e2e75d6a1ffbb397875f6e7689bfab9d9d60c  dde0036b90108db79575bd99cc33d94a6df5a1622967ccbb0852ed3b508d104d  backend/tests/test_generic_task_revision_guards.py
5317e016e304cd1ba18dba2d84b97815b2a9b327039f3922f0a7c9c2285fa9ab  a6516cbd4f079bcad1b3a48b0670e5d0c0002d26e4ae77a499562be2053fef6c  backend/tests/test_legacy_acquisition_retirement.py
fad941a0d281de9d0d4f897e8c81d3f6105c1bd9ae9184cfaeb408efe3375757  ebeff55d6d3c09f3489672fdf3b2f9cbe74d267c2dacfd35bb986fdcb8836c1a  backend/tests/test_mapping_migration.py
e256e709d26b097dc7836c182fecc08d63e2457c0d8b05cd2ba9beef4bcaaf6e  c046025ef2f6f3993a80f965622a3205bcc5db7c76b081d0c04c08c4349b0b65  backend/tests/test_observation_receipt_separation.py
16c0d155080b9022800054addc8913656abbf942a4a35fb5a129df4b2a30ecde  a1aa8a7c266cfc9023f993f254eff1bf509dc7b24faf8ac205aae7139037de23  backend/tests/test_observation_retirement.py
08a3f949a5364bca3444aacd6897c22b9a9a522b16a969558c99196c8fb82d00  ff3d1830c440bed8b3eb00b2f4e9fbe2b50a02c4a20fcaa73194d5916ba65fad  backend/tests/test_plc_facts_v2.py
c8f6f633eda36001b827f2c0f2d0919bf13bae48d34e56af0f4fdfd4b9c36dce  214011ea6b6d96284b0d88baa9de3fc702c9fb38b237264ef83ff4c995cbe12d  backend/tests/test_quality_revision_guards.py
c3320018a2eceb6957bd22c66f79a617cd54543ae85f32576dfc1e8be981a8a0  78a63e134d6743893ca00f5f23617171c389528339216d2c5d773a3c982a54d2  backend/tests_mysql/test_acquisition_consumption.py
4cca67d827302521bd55b2cf897d9cb794fe4bb73cb06da0ea5023c015c3dc8c  77941952393865a3f7f43d505cf0fac3be7529997ceb2785f31a31c56b6bcde8  contracts/published/http-api/plc-facts-v2/README.md
cd3dce51ebfe1554a933046e4c246a5db9ec1f371cc7f408e3ff213efb30eed4  6c5cb3c1e66a652195c4895c5d607084ccae55c3afeeaef60196b8c575042b6c  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
4bb1c803b16516cab3b12294b3303d5862f67b21a60a1720f8f914a16a6a6969  5fd839e330a08ad534c97bb9d71c2c2a1a26862e28250d2c105dbedf26580859  docs/acquisition-data-guide.md
6ba3b09ace3cfd0156c8027d8aa353eab11e516211daa4c269bb655ad4d74943  0d74dcf526163bf78a6092396ed95dedbe8fac7468dd1950155e78a00c55789f  docs/acquisition-data-guide.zh-CN.md
```


## 专用 MySQL 续验

Human Owner 另行批准隔离合成验证和清理。协调者提供独占 MySQL `8.4.6`，仅使用 `127.0.0.1:33407`。候选入口用清空后的环境和任务凭据，在连接后实际核对 UUID `ea1df2f9-e7b4-11f1-9cef-9aef26ad3b47`、版本及 `+28800` 偏移。Python 出站 socket 只允许该地址。首轮沙箱连通性检查拒绝连接，随后对该隔离目标单独放行。应用测试使用独立随机库和暂时 DML 账号，普通服务进程和原 dev 数据库未参与。

### AC05 空库链路阻塞

直接以同一候选执行 `python -m pytest -q -x tests_mysql/test_acquisition_consumption.py`。空库的 Alembic `upgrade c9e1a3b5d720` 返回 0，随后向前驱表 `plc_source_registry` 插入合成登记失败，MySQL 返回 1146。历史迁移 `7b9d1f3a5c7e` 动态导入 `app.plc_facts.models.source_registry.PlcSourceRegistry`，以 `PlcSourceRegistry.__table__.create()` 取用候选的现役 ORM 名称，从空库提前创建 `acq_plc_source_registry`。新迁移需要完整旧名布局，因此仅用候选从空库到新后继的链路未满足。

后续分阶段验证命令为 `./mysql-test/run ea1df2f9-e7b4-11f1-9cef-9aef26ad3b47 -p acq007_staged`。临时插件仅用冻结基线执行第一段 `upgrade c9e1a3b5d720`，后续从合成的历史布局走候选源码、历史后继、三表切换及无关后继。该方法用来检查已布库升级，仍需处理正式空库链路。

隔离试验修正了 r1 允许改动范围内的实际问题。新的命名锁查询通过显式绑定 `:suffix` 传入 `:acq006`，避免 SQLAlchemy 将 SQL 字面中的冒号解析为未提供的参数。测试补齐观测回执、观测来源和质量迁移的隔离目标确认，并参数化临时 MySQL 账号与 host，避免 PyMySQL 将通配符 `%` 当格式字符。历史迁移与其引用保持原样。

### 提交 PM 讨论的新 Revision 路径

1. 如保留历史迁移原字节，在 `models/source_registry.py` 内保留旧迁移导入的 `PlcSourceRegistry` 及其旧表定义，将历史对象隔离出正式 metadata。以独立正式 ORM 类型映射新名。同步更新 `models/__init__.py`、`crud/async_source_registry.py`、`crud/async_v2.py`、`crud/async_consumption.py`、`crud/sync_v2_maintenance.py` 和 `services/observation_evidence.py` 的运行引用，并核对 `tests_mysql/test_acquisition_source_registry.py` 对历史表的建表引用、当前 metadata 和空库回归。前两条文件是 r1 allowlist 外的新增授权面。
2. 如经 Human Owner 批准额外触达 `7b9d1f3a5c7e`，在该迁移内用固定旧名和独立 metadata 冻结当期建表定义，现役 ORM 保持新名。审计历史文件变更，并以同一正式候选从空库走完整链路，重新验证已有数据升级。不论采用哪种路径，均需在新 Revision 重新核对范围和验收。

### 已布库实测结果

对清单标识的新候选执行分阶段命令，`10 passed in 55.10s`，退出 0。前驱有来源、历史事实、最新水位、事件、流头、消费游标、待投递、操作状态和 activation。三张改名表及六张消费表的行与索引对账一致。迁移拒绝无停写确认及错绑触发器，正确切换后 history 的不可变和到期守卫按预期拦截。应用一个真实合成无关 Alembic 后继 `eeeeeeeeeeee` 后，旧 profile `da6c32f8a701` 配合只有 DML 权限的在线账号，样本提交、同字节重复、latest/history、消费租约与待投递/ACK、同流并发及间隔过期清理通过。破坏追加触发器或篡改已存在事件身份时，样本 POST 拒绝，事实、latest、流及事件状态符合预期。显式清理传入实际 `eeeeeeeeeeee`，清除到期历史事实并保留消费事件缺口证据。

缺表、关键列及类型、主键/唯一键、ready 异常和未核验触发器定义的部分情况，本轮使用离线替身覆盖。来源管理 HTTP 全路径和设备观测采集证据入口未在此次专用 MySQL 回归中单独跑完。空库链路依然保留前述失败证据，正式环境采用及独立 Verification 待后续决定。

测试 fixture 回收专用随机 schema 和 DML 账号。最后再次通过只读核验，实例只剩 `information_schema`、`mysql`、`performance_schema`、`sys` 四个系统库，`mysql.user` 没有 `arch_acq007_` 临时账号。Development 已结束对实例的依赖，实例及其专用凭据由协调者回收。候选、补丁、校验清单和必要复现入口保留到协调者确认接收。

协调者已按精确容器 ID 核对任务标签和匿名数据卷，执行 `docker rm -f -v`，并删除专用凭据、ID 文件与空目录。复核容器和卷均不存在，隔离端口 `33407` 已关闭，原 `8000` 服务进程 `89377`、`89379` 仍在。Development 已回收自己创建的测试日志、缓存、临时 pytest 夹具和编辑片段，保留候选、基线、补丁、校验清单及无凭据复现入口供下一 Revision 使用。
