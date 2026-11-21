Task ID: ARCH-OBS-005
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: 精确隔离候选交 fresh-context Verification

# ARCH-OBS-005 r1 Development 交接

## 批准与实际交付

Human Owner 批准的 [规格](spec.md) SHA-256 为 `cd835e3f4a6fb2414b3819bacd9957a0c8d3e580da031f80f0f005c4fea97347`。本交接对应任务专属隔离候选工作树 `/private/tmp/arch-obs-005-r1.fusgi7bi/source`，基线快照 Git HEAD `7d1422523be816233f4e268af73cca365ea34b09`。候选变更留在 working tree，未提交。正式项目源码仍由现有服务使用，唯一正式写入为本交接记录。前驱 Alembic 文件 `20261119_1700_d8f2a4c6b915_observation_receipt_separation.py` 字节保持一致，SHA-256 为 `8fa1fced475cb2e4860da64032141e75508f8771c6750919a17fda7ce6ce61d9`。

- 新增 `e9f3b5d7c021` 单表迁移，前驱为 `d8f2a4c6b915`。核验 MySQL 8.4、目标 UUID、库名、时区、唯一 revision、既有关键字段和约束及新表不存在以后才创建登记表。执行者分别提供 `OBS_WRITE_EXPECTED_SCHEMA` 和 `OBS_WRITE_EXPECTED_SERVER_UUID`。本迁移为显式向前操作。
- 新增登记及第三方接口。用登记行锁序列化写入、停用和删除。以规范样本身份生成回执并识别重放和冲突，实时整包替换、历史追加或记录较早实时包的 `stale` 回执。新记录质量为 `unknown`。用旧样本、旧回执和旧 profile 身份核对碰撞，发现 profile 已发生碰撞时目标拒绝服务。
- 设备和过程页面的设备选择与数据管理可展示来源名称及登记键。管理员在数据管理可查逻辑删除来源。写入登记沿用现有配置页、双语和列宽偏好。浏览器将字面 `.`、`..` 路径段规范化，前端只对这两个键用约定双层百分号编码。
- 观察 profile 严格使用新 revision。采集消费任务和通用业务采用只扩展 revision 准入。已发布 v2 合同的 OpenAPI 与向量及其旧迁移保留。新增双语公开合同及操作手册入口。

## Development 自检

| 范围 | 实际命令及结果 |
| --- | --- |
| Alembic 与修改范围 | 在未改候选执行 `alembic heads` 得到唯一 `d8f2a4c6b915`。候选引入唯一 `e9f3b5d7c021`，经 Alembic 图断言及真实 MySQL 核对。对候选执行 `git diff --check`，退出 0。全量核对 3743 个基线路径 SHA-256，差异均在下表 43 个允许文件内。 |
| 后端 | 用正式锁定的 VENV 作为只读解释器，临时 `UV_CACHE_DIR`、合成进程环境及 `PYTHONDONTWRITEBYTECODE=1`。执行 `uv run --no-sync --offline pytest -q -p no:cacheprovider -m no_db`，目标为 `tests/test_observation_write_sources.py` 和上述回归路径（设备领域/r8/r10/r10 flow、回执分流、清退、温度／映射迁移、业务采用、任务守卫／迁移及采集消费合同）。180 passed、8 skipped、退出 0。跳过项为历史固化重现，另有既有 SQLite datetime adapter 警告。 |
| 前端 | 使用工作树复制的锁定依赖。设置两类合成页面清单与 `VITE_API_BASE_URL=/api/v1` 后执行 `pnpm --config.verify-deps-before-run=ignore --config.update-notifier=false build --outDir /private/tmp/arch-obs-005-r1.fusgi7bi/frontend-build`，2,260 模块，退出 0，Vite 报常规块体积警告。设备观测列／页面相关 Node 测试 17/17。全量 `test:modules` 90/93，退出 1。基线同为 90/93，复现下列三个失败。 |
| MySQL 非空前驱与旧合同 | 在任务独享 MySQL 8.4.6 的随机库执行 `bash infrastructure/obs005-run-mysql-dev.sh`，退出 0。使用 exact d8 旧后端真实 HTTP 生成 v2 回执（含未引用回执）与样本，并准备能耗、采集、计划／实绩夹具。升级前后的 63 张业务表逐行及 `SHOW CREATE TABLE` 对比完全相同。错误 UUID 和占用表名拒绝。旧 latest、history 和能耗的回放、Bearer、作用域、读取、新写入和提交故障回归均通过。每次临时迁移库由夹具删除。 |
| MySQL 采集后继 | `bash infrastructure/obs005-run-dev-acq.sh`，对既有采集回归的任务临时副本在原 da6 流程完成后升到 e9，实际上传、读取、续读、租约、ACK、保护清理、故障与并发覆盖，9 passed、退出 0。无正式采集实现改动。 |
| MySQL 写入并发 | 用锁定 Python 运行 `infrastructure/obs005-dev-races.py`，对相同隔离 MySQL 而独立候选 ASGI 入口测试，退出 0。覆盖大小写、同键重复、旧回执碰撞后无登记残留、旧 profile 碰撞、未来／类型拒绝、无效区域指标，以及删除先锁和写入先锁两个顺序。实际 false、空字符串落库并经公开 GET 原样读出。 |
| Chromium 与实际双目标 | 用专属 Chromium、Vue/Vite、真实候选 FastAPI 与 MySQL 执行 `node infrastructure/obs005-dev-browser.cjs <fixture-directory>`。真实登录、登记、过滤、改名、不可编辑键、字面 `..` 修改及删除、两温区四指标配置、无 token 双目标 POST/GET、五并发重试、禁用槽位重放、实时 stale／部分包、卡片／曲线／两类数据管理、停用／启用／删除、保留记录、窄屏 English 及 operator 403 通过。后续最终候选复跑见下文。 |

全量前端基线失败为 `admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`、`five adapted modules retain order, owned bilingual titles and current visible leaves`。这三个断言均出现在相同 90/93 的基线复现中。直接跳过依赖状态重装检查来使用已复制锁定依赖。Backend SQLite async 驱动不在既有锁定环境，无 DB 子集使用合成 MySQL 设置及 `no_db` marker，测试本身不对该占位地址发连接。

## 边界、已知风险和独立复核

- 本次来源标识不能验证机器身份，公开接口的访问范围依赖部署网络。旧 profile 如使用登记哈希形状的标识，潜在碰撞写入由 MySQL 的 InnoDB 锁定读保证，非 Repeatable Read／Serializable 的该分支失败关闭。人工读与旧设备权限继续按各自规则处理。
- Development 测试只使用任务专用 MySQL 8.4.6（容器 `arch-obs-005-r1-dev-fusgi7bi`、随机端口 62822）及专用浏览器和合成账号。临时日志、截屏、脚本和套件位于 `/private/tmp/arch-obs-005-r1.fusgi7bi`，供独立复核和字节比对。任务协调者拥有数据库容器，DEV 进程停止后由其回收容器及仍在该容器内的随机浏览器库；其余临时工件待复核完成及确认无需追溯后回收。临时凭据从私有文件读取，未写入候选或任务文档。
- 计划／实绩的夹具、列和规则在迁移前后完整比对，通用采用守卫通过后继 revision 单元测试。本 Development 未运行计划／实绩的完整浏览器业务流。
- 将本候选的精确 Revision、基线和差异交协调者安排 fresh-context Verification，由其在独立 MySQL 和浏览器核验规格的全部验收项。正式树集成、dev 迁移、服务切换和继续演示须保留至 Human Owner 的独立确认。本文件只记录 Development 自检事实。

## 候选文件校验

预像清单 `preimage.json` SHA-256 `2fcffc2b4e98e89dee703b1270c45df3ac0c5335e8989850b8be577990ae9f95`。差异清单 `obs005-development-delta.json` SHA-256 `94fb4004f9593cefefa8c47243d50202a1061aada071567b82f5ab55c36fa882`。下表记录候选新增或修改的每个文件。

| 文件 | 修改前 SHA-256 | 修改后 SHA-256 |
| --- | --- | --- |
| `CODE_INDEX.md` | `83295a32eb310c8947844e90ee9ebe5f8d40676eaf2a64b6cd0148a2adca83fd` | `709f928894ad619de7576a5a606945adcf22493a45f0ee7744c8ea286d854d0f` |
| `backend/alembic/versions/20261120_1600_e9f3b5d7c021_observation_write_sources.py` | `新增` | `e1f58111286a09c25eaad1b9694dba2da2fbeb6c34a28afdd84f819241682f96` |
| `backend/app/equipment_observation/README.md` | `5d07eff0aef80c49edd34c21c5bd67f0f3069c0d64139987049828f69fc58057` | `37e9c0671bbd703787f682ef3da777d2c20c69ffe39f261daad8ed46adf76c55` |
| `backend/app/equipment_observation/README.zh-CN.md` | `3e2af054d2a508efcd716764d3fb80fc696065c36ef652423eb6289aef598b49` | `36466f8b426a8902ee0b3c9af0a49d3cc9531884dc4aa8cfa57881d35f34822e` |
| `backend/app/equipment_observation/api/routes.py` | `3d50f4480b3ec4a167001a5fcde7c5a88b5e8aebd7f4aa2499964cd2fc6ce649` | `d94b73853e6ad4a00ccdb0b18f468419878a57d98697b7f35fe9b891c47bc4c4` |
| `backend/app/equipment_observation/api/write_source_contract.py` | `新增` | `c51edd99aee5d06399982d319e2fb1922ca4c8f0a955cd16cb6af9077bdd8c23` |
| `backend/app/equipment_observation/models/__init__.py` | `02173650766620ddefe24fc6e02b50066c16c4f525119264d89fd0cc294fec2e` | `5af8e1724c18ba91285bb47f4c1244d86d4370043584d7968e3f7f8c0b0c5a57` |
| `backend/app/equipment_observation/models/write_source.py` | `新增` | `09e6e5c7151ef1ba9c85b2012973a4915a502c1405e4e4b7848d75656f1d1d1b` |
| `backend/app/equipment_observation/profile.py` | `016bc41234efc14552b262d956b501d8a39d1003dac064d99ebb19315e034cca` | `87e538ac3faded13b7a5649c5a9300d6500e7e18d8ea645bda43e102b8f3262e` |
| `backend/app/equipment_observation/services/guard.py` | `60b870f2eb2fc7dbea43a83a498245e1312d6f3d6402d0aca80ef535c1de4be3` | `dcb96f798191a8eaa8a396b343b4cb986892e68b3ed03fb683f2ecaa8ce0c735` |
| `backend/app/equipment_observation/services/ingest_v2.py` | `77c893ccd72f72631ee6cea3ed8d68bd9f2f00fbf41bb12c5eaa18f1dd8350be` | `75cb117b1d83bbf7e4e5ff413d83542d6d8c4f12a64fb4f35fc252c0700b2faa` |
| `backend/app/equipment_observation/services/reads.py` | `f3e8ab8c2d5d711f301593cabb68a756d76699f5b22a6e97a65d479673daf6c2` | `da694dc35d362aa6d5a5f577c5ffeb90db44ba2c1db783d4f8196b91f8e4facd` |
| `backend/app/equipment_observation/services/registered_ingest.py` | `新增` | `e7e6d0c954c13c8bd99b97894640ae3484a6f2ddf866c36c1e54228adf07c36a` |
| `backend/app/equipment_observation/services/write_sources.py` | `新增` | `e06e3a13bd4d2d710dfa7a1b64d75447b0407dc10dd79ab4bbd5b0c7e1676445` |
| `backend/app/plc_facts/v2_config.py` | `8566e67e21f8f6e0200a8eda925849f408f5d2341bff01bf76e4482565eaad24` | `c3eae2e3b760339a45ff89f252cdfe68e77dfbbf3de442d52c7c824628945b0f` |
| `backend/common/integration/storage.py` | `bf44047648ec7ef25588da9a680397b241fbbd573508669c2c6e1f783b40c57b` | `3f3edc6cd946c445f0d20ee3384ab9559bcfc3da6aeccb9d47794520d82b4bf7` |
| `backend/tests/test_acquisition_consumption_contract.py` | `aee23914ca6370ec49933f42313141d37dbcf63472c701b667abaab9263ba03e` | `b388d88898ed863d89c3d50ee671f14b240b31c784a4c26ec37174a950e1b866` |
| `backend/tests/test_business_integration_storage.py` | `2c7462f835c315efd2043ec1b60db9fe2bf6285b529f12b8fef4908de5e6c7a1` | `a0cceb727b6868dad9fcb485141b2302360e2babec1e4a907c53ae4fc2899e19` |
| `backend/tests/test_equipment_observation_r10.py` | `eb0d9c23f7b98dd4ee8e261687af1fa39020ef430dd3ea4b8efc37b96c5cfb39` | `272626ba4e961a121469f86b5c329369660c822620619cc1d56b1be36eb0d1c4` |
| `backend/tests/test_equipment_temperature_migration.py` | `20081e8931518860a3d633007b6e379f219646fee675a768614d87af280d934d` | `f2a2d7c0cf14c99424e9c30edccfeed1015c43da56ae17a25c557041617fa4c6` |
| `backend/tests/test_generic_task_migration_r3.py` | `ac675ea1605a48afbbbc573f7cfb1a01d091da3f356bd758551526bca4136351` | `ae2e344e4290970258e3bc75bdb2c6a9cd0be138a0cfb22dddc1959980326896` |
| `backend/tests/test_generic_task_revision_guards.py` | `64e0a1d7838feac1f120a31ad3ce814d5501d38ffb95b58d0a9056c4efc5e82f` | `0b9cf7f9594b4490da4ebb7da05e2e75d6a1ffbb397875f6e7689bfab9d9d60c` |
| `backend/tests/test_legacy_acquisition_retirement.py` | `891bcf93cd74138072ac7df62eb4dc4eed64ad88c414adf705aa067e4c05683c` | `131389901e3337068728d9d2251cef6fa20f3c27e57d3a11a4e7e998955441d8` |
| `backend/tests/test_mapping_migration.py` | `35b740b78096a88dc6430eeda365bc956385d871788dac2d4f19236d94e5072d` | `40bc68f7a2c88ddbbbc69f9757b8e46c3286a1615640941f47285a2cd4638e26` |
| `backend/tests/test_observation_receipt_separation.py` | `430745e4fbb1ec7ade3594c8acfdef9446e19ada04216541c238484cb7e19a99` | `d3d8c7d3ead30d5409f9343a3f7a7ce3ec2a0437598d3f930747e9e9f5de3bdd` |
| `backend/tests/test_observation_retirement.py` | `c2e89ea7566b31e42bb5d085debecdd15b14a8489e5aa51b1b756043ce2cd475` | `e67d2dc31ed10b0932d1fe1980963e9d819751b9786be0d157e0c7367d8fb78d` |
| `backend/tests/test_observation_write_sources.py` | `新增` | `315cad9f232b949c508eded21980831eecd0487c6cbb9e7c43dc314a9ab6993c` |
| `contracts/published/http-api/observation-write-sources-v1/README.md` | `新增` | `1629188fd7117e1070b5f1f30aea2cad5cb9fb7dbda0f55e939946a4c7b12568` |
| `contracts/published/http-api/observation-write-sources-v1/README.zh-CN.md` | `新增` | `f358c6b6f6a05b8586e35dd0137fb41f210979489df8b7212622dd923e5ea50a` |
| `contracts/published/http-api/observation-write-sources-v1/openapi.json` | `新增` | `cf047d573128aab8edf600b5780cdcf6b1b526fa4503f4650cbe72de25301663` |
| `contracts/published/http-api/observation-write-sources-v1/vectors.json` | `新增` | `6fe9162ba7a9dfd2a9df1976d4d90c7d93b7b13f70a7c4704cacd000395110b2` |
| `docs/equipment-status-process-monitoring-guide.md` | `d202111ee14eb84f0af5aff60a451959416209f21f251759baa0ea17d4954858` | `e422ffe31eef8902609f81131548a5f73ba21022930ecd1a0cb62b7a3d44737b` |
| `docs/equipment-status-process-monitoring-guide.zh-CN.md` | `5bc7bf31420c1e0c1dc0b4442dad0736349e8974eaeac490291618ddc8cd70ea` | `7114a2700b697103ca8da7fc8b0c0a629d90d32718660de37cd880452a535429` |
| `frontend-js/src/app/equipment/api/observations.js` | `ca56e4c8b672d05067c1394d9a832b9beed201ad04477b2c6735989205b661ef` | `e05f903e06724872643198a6aa904b5615d8fc65c101a402026398371e91636f` |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | `b2ac30ca6e7779ad16b8e5825ad150438e9d219678fa574d655dc706269ec688` | `bc13b54d5e4a14f7bdfb84337d33dc7a26cfa4412c9497d3e7cc2dc691a34d99` |
| `frontend-js/src/app/equipment/components/observations/columnModel.js` | `bcb9c4f4b433db6da0acdcb0f24d6dacafddbbf02930032c69679ecf94626cba` | `1e199ce4a223645aaa401fc47120a3208cae7430ceb3b71965bb5eb73e1b9ba8` |
| `frontend-js/src/app/equipment/locales/en-US.json` | `0c4448870bb4591c269730390b554cf03da62eb675ec9c04cc64001095b54d61` | `e35ccc149c0a86eef48d9a8f56d60bd0e01e72158e8c29a8021180211da300b8` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | `0b27765f55f0ede2ab798429d25ab2ff6b556d17eacb39ed3744dd87b498b0f9` | `24584c3a30a7a8af73db84e9a0ff24c3b2b786c1afb364e718f6afdc803f1102` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | `a352e1cf1c61737c1e56a6e09b8e0ff2ee66205d8e28cb996ef341601ce06e99` | `b1c90001e9a8cb292a1f7c6bc7f7b70397dc4f75f52bdfe584cc016cf036e11f` |
| `frontend-js/src/app/equipment/views/observations/cards.vue` | `9d3dcb8d7f74e69dfb2c270978e9c688187f8c9d68091b0b383864e64182579d` | `e75b5361379402ca68d85e148329731227a249cd178ef77ff560298e4533aa72` |
| `frontend-js/src/app/monitor/api/observations.js` | `cd8169d6b5a3bb4aee72974704410ead5337c9bb1ff45b02047362647ad1e987` | `fbd061cc2dca2e8614940c70a7ecb96760f4b51dca57111bde1820d1f23a4d45` |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | `a202167be58e577d4076273f1e98e1e9051b553469ac1afb4b0f8f90cfb1fd10` | `a490320efcf879fb94a4ad01f4dc9b7900dfc99762b2b955441070667d96d0bf` |
| `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | `1c1fb713da172a59889567762b99d518a0edf57f0cc534ae396271f79c69290e` | `08a4b7a545b16c40de6f39d9444f2f61b8a3b5d3c7c5b0b3c56d00812c6f282f` |

## 最终候选复跑与工件

- 专属 `obs005_dev_b29d729d3141` 空库以最终迁移文件从 base 完整升级至 `e9f3b5d7c021`。真实 Chromium 首阶段通过配置登记、过滤、不可修改标识、精确 `{sourceKey}` 路由及 `..` 特殊路径的修改和删除。首次拖拽动作发生在表格加载遮罩过渡期间。等待遮罩清除后在同一合成库续跑，`OBS005_BROWSER_CONTINUE=1 node infrastructure/obs005-dev-browser.cjs obs005_dev_b29d729d3141-browser` 退出 0。拖动来源标识列后本机值写入并在页面重新加载后恢复，重置清除了该表偏好。双目标 HTTP、真实卡片与 ECharts、数据保留及双语窄屏断言通过。截屏保存在该临时浏览器目录。
- MySQL 旧合同复跑日志位于 `obs003_76dd9f853cbd4cb1-migration-dev` 和 `obs005-migration-self-check.log`。前端、后端、采集、并发及最终浏览器汇总分别在任务临时目录的 `obs005-frontend-test.log`、`obs005-backend-test.log`、`obs005-acq-test.log`、`obs005-race-dev.log`、`obs005-browser-final.log`。
- 已检查双语合同和手册的 38 个相对文档链接，解析两个新增 JSON 工件，并以 180 项通过的后端子集核对实际 OpenAPI 和发布请求描述、规范摘要及等价重放向量。最终候选 `git diff --check` 退出 0。
- Development 本轮创建的 Uvicorn、Vite、Chromium 进程已结束。隔离容器及候选由任务协调者管理，因独立复核和正式交付一致性检查而保留本记录列出的相关工件。

## QA1 退回后的 Development 修复与再次交接

- 继续使用精确 `ARCH-OBS-005 r1`。规格 SHA-256 `cd835e3f4a6fb2414b3819bacd9957a0c8d3e580da031f80f0f005c4fea97347`，本轮输入为 [QA1 核验记录](checklist.md)，SHA-256 `27559ef2c086dc4fcae43b8b90fbb6f932cc722e6901610fc5ce006c8a1931cf`。保留首次 Development 的记录和差异清单。
- 登记服务取得来源行锁后，逐字段比较请求中的 `name` 或 `enabled` 与数据库现值。无变化时返回原记录并结束只读事务以释放锁。真实改名、启停或删除继续使用锁内数据库时钟，更新后提交。测试覆盖仅名称相同、仅状态相同、两者均相同、真实改名、仅一字段有变化、清空名称和删除。
- 修复前先执行 `uv run --no-sync --offline pytest -q -p no:cacheprovider -m no_db tests/test_observation_write_sources.py -k change_updates`。3 项无变化用例按预期失败，4 项实际变更用例通过。修复后使用同一锁定 VENV、同一合成进程环境，执行原交接的 14 模块后端用例，187 passed、8 skipped、退出 0，保留既有 SQLite datetime adapter 警告。
- 用锁定 Python 启动 `infrastructure/isolated-stack.py --source "$D/source" --phase dev --mysql-port 54575 --mysql-uuid 85d5c687-e4bc-11f1-a32a-860712e7f85b`，其中 `D=/private/tmp/arch-obs-005-r1.fusgi7bi`。专属容器 `arch-obs-005-r1-dev2-fusgi7bi` 使用 MySQL 8.4.6 和 +08:00，数据库 `obs005_dev_f1bc29d9031b` 由空库迁移到 `e9f3b5d7c021`。随后执行 `python infrastructure/obs005-rework1-http.py obs005_dev_f1bc29d9031b-browser`，真实登录和 HTTP 请求配合独立 SQL 会话，退出 0。创建后的 `updatedAt` 是 `2026-11-20T16:35:30.151079+08:00`，仅同名、仅同状态和两字段均相同的 PATCH 后，HTTP 返回值和数据库原记录保持一致。实际改名推进至 `16:35:30.210828`，实际停用推进至 `16:35:30.217584`，再次提交同一停用状态保持该值。删除后 `updatedAt` 和 `deletedAt` 同为 `16:35:30.228512`，后续 PATCH 返回 404。所有变更时间由独立 SQL 会话的数据库时钟核对。
- 候选仍在 `$D/source` working tree，基线 `7d1422523be816233f4e268af73cca365ea34b09`。重新校验 3743 个前像路径和全部 43 个允许变更文件，`git diff --check` 退出 0。新清单 `$D/obs005-rework1-delta.json` SHA-256 `a46b5778c724154228580f8fa8345d0c605ab7394f0c2cbe50735c0aa3264451`，原清单 `94fb4004f9593cefefa8c47243d50202a1061aada071567b82f5ab55c36fa882` 保留。相对冻结的 QA1，只有下表两文件发生变化。
- Uvicorn 和 Vite 已停止，独立 SQL 及 HTTP 会话已关闭。本轮未启动 Chromium，前端文件与迁移文件字节均与 QA1 一致。日志 `obs005-rework1-{before,backend,http}.log` 和专属 MySQL 工件留在 `$D`，由协调者按任务资源边界回收。正式源码整合、dev 库迁移与服务切换等待独立确认。

| 相对 QA1 的变更文件 | QA1 SHA-256 | 本候选 SHA-256 |
| --- | --- | --- |
| `backend/app/equipment_observation/services/write_sources.py` | `e06e3a13bd4d2d710dfa7a1b64d75447b0407dc10dd79ab4bbd5b0c7e1676445` | `31af08cc00ba3e454d2d659523f4d9beb936c1986067c6b90ec0fdc3d13a40ba` |
| `backend/tests/test_observation_write_sources.py` | `315cad9f232b949c508eded21980831eecd0487c6cbb9e7c43dc314a9ab6993c` | `3d6d030a4418dc57ad14c146958e2443a7bea105a3f478fa2f9a79d54904ef56` |

此次再次交接为 `developer_handoff`。由任务协调者冻结新清单对应的精确候选，并交 fresh-context Verification 独立复核。首次交接中已记录的基线用例限制继续适用。

## Human Owner 单独授权后的正式合入、dev 迁移及热重置

Human Owner 单独回复“好的确认，合并吧，然后热重置”和“数据库我授权给你alembic”。执行范围为精确 `ARCH-OBS-005 r1` 的正式工作树合入、单次 dev schema 后继、对应私有 profile 更新及 8000／5190 服务恢复。输入仍为 QA2 候选 `/private/tmp/arch-obs-005-r1.fusgi7bi/qa2-source` 和清单 SHA-256 `a46b5778c724154228580f8fa8345d0c605ab7394f0c2cbe50735c0aa3264451`。执行时 [QA2 checklist](checklist.md) SHA-256 `34d6f0eff7df1016d1b08ec399c6abc1392718c50316f494d1b440d76f779f2b`。原批准规格 SHA-256 未变。

- **正式工作树**。执行前 Git HEAD `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。核对 43 个候选路径的预像、候选字节及文件权限。42 个交付文件逐字节匹配 QA2。并行修改的 `CODE_INDEX.md` 用预像、正式当前文件及 QA2 做无冲突三方合并，保留双方内容，正式文件 SHA-256 `183c8437dad559341ceb1697406cbdb0833e3c79dbd21fe9235251215fa79f3f`。正式前驱迁移 SHA 保持 `8fa1fced475cb2e4860da64032141e75508f8771c6750919a17fda7ce6ce61d9`，正式后继迁移 SHA `e1f58111286a09c25eaad1b9694dba2da2fbeb6c34a28afdd84f819241682f96`。正式 `alembic heads` 返回唯一 `e9f3b5d7c021`，源码范围 `git diff --check` 退出 0。合入保留为工作树修改。
- **停写及备份**。以正式锁定 Python 运行任务私有脚本 `cutover.py preflight`、`cutover.py execute`，均退出 0。用旧服务监听、运行目录和命令核实 PID 后，向正式 Uvicorn 17678 与 Vite 17721 发 SIGTERM 并确认监听释放。MySQL 保持运行。确认 `127.0.0.1:3307 / industrial_level_2_system`、MySQL 8.4.6、UUID SHA-256 前缀 `ac2319a3fdc8`、+08:00 以及唯一 DB 前驱 `d8f2a4c6b915`；经同一现有容器内 TCP 双查。维护前再次核对活动连接、InnoDB 事务、待定及持有写入类元数据锁。运行容器自带 8.4.6 `mysqldump`，一次一致性事务备份，退出 0，首尾完整，304,040 字节，SHA-256 `4a945d9c216a8e12bd300c8177151458faa92e969b5e5a138864294a940a8a86`。备份及两份 profile 预像均为 0600，本次未执行恢复演练。
- **数据库与配置**。停机窗口中从正式 backend 目录使用锁定解释器运行 `python -m alembic upgrade e9f3b5d7c021`，传给进程的预期 schema／UUID 与该 dev 目标一致，退出 0。迁移前后 63 张既有业务表的行指纹、行数、完整 DDL 指纹一致；触发器、例程及事件指纹也一致。仅增加空的 `observation_write_sources` 表和其主键、唯一索引。对当前实际启用的 OBS 和 ACQ 两份 profile 分别原子替换 `target.schemaRevision` 的单一字段，确认其余字节及文件权限一致。未发现其他启用且指向此目标的 integration adoption 文件，后端 `.env` 字节无变化。用正式 app 账号实际加载 OBS/ACQ profile 并验证数据库 guard 均通过。
- **服务与只读验证**。在原正式目录以原入口恢复 Uvicorn `run.py`（PID 75521、worker 75523、127.0.0.1:8000）和 Vite（PID 75570、5190，原监听地址）。执行脚本退出后独立确认监听及 HTTP `/health`、前端首页均为 200。8000 的 OpenAPI 包含四个新路径模板，5190 的转换后登记 Vue 模块为 200；经 Vite 代理查询未知来源为 404，未登录列登记为 401。使用既有管理员账号的只读认证链路，登记列表、设备／过程选项及采集 options/latest browse 均 200。此次无业务写入、启动 bootstrap 或演示调用。
- **证据与保留**。0700 私有目录 `/private/tmp/arch-obs-005-r1-dev-cutover.HSPN9I` 保存一份 `dev-full-d8.sql`、两个 profile 备份、紧凑指纹和日志。脚本、迁移前指纹、迁移后指纹、正式 43 路径后像、HTTP 结果分别为 SHA-256 `291d7a3d72c2f180d872b672d44f5294f40d9ee68366e78265c1be1833f217d8`、`90059f5fff3337c2f564d3cc55cf70adbac4e4ee02f55325e96a33013c8633b2`、`b3e63400cf8fd32f4074b47c82bbe545e5c6e2cef5f6a14cf64bd10cdfecfd80`、`7ab5cca16f4a8665be9d31a99b60e6738d5dcef9ad0c86343866f0594b0497f0`、`8310b008bc8bbdc92e8fc1f32c0c969e97762442de6af2099feeaf58bb1ba5fd`。正式服务进程及控制台日志持续为当前 dev 服务使用；保留备份至维护复核完成且由 Owner 明确其处理方式。其余隔离测试资源由协调者安排。

上述为正式切换动作和 Development 自检证据，已交协调者安排独立切换后复核。
