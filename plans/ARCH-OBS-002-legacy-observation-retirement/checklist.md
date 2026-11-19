# ARCH-OBS-002 r1 独立 Verification · 第一轮

**Verdict: qa_failed**。2026-11-18（上海时间）在 fresh context 独立复验隔离候选。AC05 出现可重复的错误放行，影响 AC04 的回执保护。退回 Development 修复，Human Owner 最终验收待后续独立复验。首次失败记录保留。

## 核验对象

- `shasum -a 256` 核对 spec 为 `957956ad81ed13bea03efd98a691a62f52b7526187d8c653ae1bfdf3e0424e37`，tasks 为 `7707cd063e51b585e9c1f8f8799f7562679dd0eab21142e50647373f97874533`。
- 候选根为 `/private/tmp/arch-obs-002-r1-3y1wnavr/candidate`。对 manifest 的 225 项逐条 Python SHA-256／删除状态断言通过（新增 6、修改 75、删除 144），manifest 哈希 `6c28642daea8688c19e1c85dbc380d39e5fd840b4488753507a6e6df6ad6dc69`。正式树上 `git apply --check --whitespace=error` 对交接的非漂移 diff 成功。CODE_INDEX 与两份 frontend module-registry 测试要按当前前驱语义合并。
- 项目现有 Python 3.13.3 虚拟环境，候选 backend 与 frontend-js，前端沿用现有锁定依赖。真实 dev 与运行中用户服务未参与。

## 必修缺陷及最小复现

在自身 MySQL 8.4.6 合成库的精确前驱 `ae20b4d6f831`，所有 18 张目标表为空，`energy_consumption_main` 为空。插入以下合成记录，再在确认的窗口对该库执行候选 `python -m alembic upgrade c9e1a3b5d720`。

```sql
INSERT INTO metric_ingest_receipts
 (target,producer_id,event_id,request_digest,outcome,result_record_id,
  contract_version,result_version,result_detail)
VALUES ('energy','fixture','qa-unknown',UNHEX(REPEAT('42',32)),'stored',999999,
 'aiis.metric-ingest/v2','r10',JSON_OBJECT('stored',JSON_ARRAY('kwh'),'skipped',JSON_ARRAY()));
```

预期在执行 DDL 前拒绝，仍为前驱且 18 表齐全。实际命令 exit 0，18 表已退出，revision 已更新，查询仍得到 `('energy','stored',999999)`，能耗样本数仍为 0。候选 migration 的 `_validate_data` 仅检查版本、target 集和 detail 顶层键。候选 `services/ingest_v2.py::energy` 在同一事务提交能耗样本及其回执，成功结果必有对应样本、样本 ID 和 ingest_receipt_id。该输入冒充已经存储的结果。Development 的归档位置负例仅增加顶层 resultLocation，不能检出此例。

请按真实写入语义核验 target、outcome、result_record_id 与对应记录，遇到无法确定的身份在 DROP 前停止，在真实 MySQL 中证明 18 表、回执默认值、前驱与保护数据均未变化。允许 history/no_history_metrics 无结果；latest/stale、already_stored 及早期 stored 可以共享当前快照 ID，快照的反向回执可能已更新。history/stored 与 energy/stored 可比对各自样本及其回执。修复须在实际有界锁条件下复测，避免在未锁表上查询或误拒合法回执。旧 Development 成功夹具还写入了 latest/stored + NULL result_record_id，修复后需以可由真实写入方生成的成功记录验证。

## 验收结果

| AC | 结果及证据 |
| --- | --- |
| AC01 | 候选定向 pytest 通过，核对 metadata、精确 22 个方法在 OpenAPI 中消失并逐个 HTTP 404；QA 数据库的实际表集差等于 18 张。前端有效 registry 25 路由／9 组。历史归档与合同保留。 |
| AC02 | 在同一 QA 库用候选真实 ASGI 路由、SQL 与机器 Bearer 复跑 http_smoke.py 的断言，通过多区域、0/false、空包替换、晚到与 observedAt 顺序、重试、异正文 409、设备 scope 403、v1 匿名 401／已授权 409、表计汇总 5 kWh。首次匿名描述符 profile 无法按普通文件重读，返回 503；改用 QA 临时 0600 普通文件后 exit 0。退出仍见 aiomysql 事件循环已关闭的析构警告，夹具没有证明连接池优雅关闭。 |
| AC03 | node 模块测试 90/90。新页 monitor.energy 在 /monitor/consumption，旧键 monitor.consumption 的授权配置明确 exit 1，新键加空 operator 授权 exit 0。Vite 生产构建 exit 0，存在 chunk 大小提示。ASGI 走实际角色／scope 守卫，admin 可配置，supervisor 设备/过程/能耗读取 200 管理 403，operator 仅设备读取 200，outsider 全 403，匿名全 401。人类身份由 get_current_user 依赖替身提供，真实账号登录、浏览器逐页导航未测。 |
| AC04 | 部分通过。确认前驱到 head、有界锁、56 张保护表前后数据与 DDL 快照一致（排除自增计数，单独允许两个默认值）。含合成回执、区域与快照，采集、价格、计划／实绩等空表只证明结构及空状态保持。QA 摘要 3cafa1c740672954296568f3810cb181ed012af40ac1c0d9a2451e725d66f225。当前观察与 Facts 新 head 探针通过。错误放行见上，尚无非空价格、采集和计划实绩的独立迁移对账。 |
| AC05 | **失败**。守卫能拒绝缺窗口声明、错误 UUID／前驱、旧表非空、v1／未知版本、显式归档顶层键、外部 FK、视图、缺表。最后查空后的另一连接 INSERT 等待表锁，随后收到 1146。在真实多表 DROP 之后注入异常，前驱仍在、18 表均消失，重试被拒，56 张保护表一致，反序重建 18 份合成空表 DDL 后结构一致。候选 finally 释放表锁、恢复 session lock_wait_timeout。未知结果身份却被允许。窗口声明仍依赖操作人确认外部写入方及元数据完整可见。 |
| AC06 | 待 Owner 精确授权；未访问 3307、未写真实 .env/profile，未切换用户服务。 |
| AC07 | 裸运行 business_time_adoption 只显示帮助，唯一 module 选项为 performance。源码／测试／索引仅在候选范围核验。正式启动入口、并行交集整合、真实设备、CA/SMA/DAA、生产发布及 Owner 终验均未执行。 |

## 命令及测试基线

- 读取候选迁移、实际回执写入和重放、临时合成驱动、manifest/diff、两端测试及 Developer 输出。候选 backend 执行 `python -m app.module_preflight --project-root "$PWD" --check-only` 和 `python -m alembic heads`，唯一 head 符合规格。`python -m pytest -p no:cacheprovider -q -m no_db tests/test_observation_retirement.py tests/test_equipment_observation_r10*.py --tb=short` 为 38 passed、1 个 SQLite datetime deprecation warning。首次将 LOG_DIR 指向 /dev/null 造成 38 个 teardown error，改为任务临时日志目录后消失。
- 前端 `node scripts/check-module-manifests.mjs --check`、`node --test tests/module-registry/*.test.mjs`、`node scripts/check-page-access.mjs --check --mode production`、`./node_modules/.bin/vite build --outDir /private/tmp/arch-obs-002-r1-qa-vite`。新版 supervisor grant 和空 operator 为合成配置。
- QA 用项目 Alembic 从空库执行 `-x obs_r10_writers_quiesced=yes upgrade ae20b4d6f831`，迁移链使用与该 QA 目标匹配的各自 UUID、schema 和受控确认。对 Development 的 migration_checks_final.py 在内存中仅改端口／库名、保留 DDL 到内存并加入上述反例，复用真实迁移代码。确认 SQL 返回版本、库、UUID 和上海偏移 28800；随后复跑目标化的 http_smoke.py。未运行本地真实数据库。
- 审计 pytest-final.log、pytest-original-f.log、pytest-original-c2.log 和历史 ACQ-002 checklist。候选全量 no_db 是 **634 passed、5 failed、12 skipped、24 deselected，exit 1**（Development 运行，QA 独立复跑上述 38 项）。F 的历史 58 表子集断言及旧 performance descriptor 的 ProcessSpeed ImportError 在固定 f7c5608 对照也失败，候选已扣除本轮退役表，其余既有差异仍未验证。3 个 C2 用例均先于目标断言在旧 System 的 SnapshotPolicyCatalog 私有导入处失败；两边用同一公开 bcafa89 夹具，该夹具与当年 QA3 未提交源码有别，不能声称 QA3 原件重跑失败。五项均有独立的既有失败证据，不能算全量通过，也不能解释本次新发现的 SQL 缺陷。
- `git show f7c5608:backend/tests/<原名>.py | cmp - <候选归档>` 逐份验证旧 mapping API、mapping service、business integration service 三份逐字节一致；其历史运行日志为 75 passed／21 原 skip。现行 r10、路由、元数据及前端回归仍可运行。历史测试通过数未并入现行候选。

## 资源交接

QA 容器 `arch-obs-002-r1-qa`，ID `9590dbfa32029556183ac76eecf0605bc722c2b38ab38277bc4455a4af0395ed`，独占合成库 `obs002_qa`，UUID `83ce39b2-e339-11f1-9c30-7e2b90cdaed5`，仅绑定 127.0.0.1:13319。本机 arm64 mysql:8.4.6 镜像 ID `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`，使用 --pull=never，匿名卷 `1f2cd15ecb192ee8cbdf789858df3b58cd760d85e03681eecbfca321f5bb8d5c`。创建前端口和名称空闲，创建后用 docker inspect 复核身份；MySQL 随机生成的 QA 密码仅在命令内部使用，容器日志含其初始化输出，不应导出或作为公开证据。QA 自有 `/private/tmp/arch-obs-002-r1-qa-vite`、`/private/tmp/arch-obs-002-r1-qa-pytest-log` 为生成物。保留至协调者核实证据与返工是否依赖后按 ID、卷及路径核对回收。Development 资源与三处并行漂移见 [handoff](tasks.md)。本轮 Verification 未清理资源；返工后须重新固定候选与交接摘要，并由新的 fresh-context Verification 复验。

## QA2 独立复验 · ARCH-OBS-002 r1 · 2026-11-18 上海时间

**Verdict：qa_failed。** 返工关闭 QA1 的悬空能耗样本缺陷。另有一类明确指向旧归档的回执在实际删除前通过守卫，AC05 仍失败。交回 Development；正式整合与 dev 切换均待独立批准和复核。

### 新缺陷与精确复现

在任务专属 MySQL 8.4.6 的新合成库 obs002_qa2_detail，从空库运行 Alembic 至 ae20b4d6f831。18 张待清退表均为空。插入：

```sql
INSERT INTO metric_ingest_receipts
(target,producer_id,event_id,request_digest,outcome,result_record_id,contract_version,result_version,result_detail)
VALUES ('history','fixture','qa2-detail',UNHEX(REPEAT('42',32)),'no_history_metrics',NULL,
'aiis.metric-ingest/v2','r10',JSON_OBJECT('stored',JSON_ARRAY(JSON_OBJECT('resultLocation',
'process_monitor_r8_archive','resultRecordId',999999)),'skipped',JSON_ARRAY()));
```

精确绑定该库、UUID 和合成维护窗口后，运行 `python -m alembic upgrade c9e1a3b5d720`。预期拒绝，保留前驱及全部旧表。实际 exit 0，版本为 c9e1a3b5d720，SHOW TABLES LIKE 'process_monitor_r8_archive' 返回空，回执仍含上述 stored 项。candidate-rework1 的 ingest_v2.py 第 185 行对 no_history_metrics 总写 stored=[]；迁移只检查 stored/skipped 为数组，允许与 outcome 矛盾的明细，包括本例的明确旧归档结果。请 Development 按活动 writer 各 target/outcome 的实际明细结构验证，并保留合法空数组及合法跳过项。无需改变业务写入格式。

### 独立执行与证据

- 固定的 spec/tasks/QA1 checklist 和返工 manifest SHA-256 均匹配交接。独立逐行核对 manifest 225 项候选摘要与删除状态；其中仅目标迁移不同于 QA1，正式树 preimage 漂移恰为 CODE_INDEX.md 和两个前端 registry 测试。排除三处的补丁 git apply --check --whitespace=error 通过。
- AC01/AC02。候选 backend 的 pytest -p no:cacheprovider -m no_db 对 retirement、r10、generic revision guard、business time adoption 共 59 passed，1 项 SQLite datetime 弃用提示。复用已审阅的合成驱动，将连接显式绑定独立库和 QA 账号，先运行 http_rework1 before、再运行 migration_rework1、最后 http_rework1 after，各 exit 0。真实 ASGI/MySQL、机器 Bearer、实际合成登录与 JWT，检查多区域、缺测、重试与冲突、过期包、权限及能耗统计。生成前驱合成记录时仅夹具临时接受该 revision；升级后走原生 profile。两个阶段均通过。
- AC03。模块装配 25 路由／9 组，node --test tests/module-registry/*.test.mjs 为 90/90。隔离无头浏览器使用候选已有 dist 与绑定 QA 数据库的真实 ASGI relay，browser-rework1.cjs exit 0。管理员真实登录浏览四设备、三过程、两类管理／记录和能耗页，通过菜单打开唯一能耗页，旧地址重定向。supervisor 的合成页授权允许能耗，管理拒绝；operator 及 outsider 的合成配置无页授权，发生重定向。此浏览器测试复用了 Development 的前端构建，QA2 未重新构建，不代表用户 dev 角色配置。
- AC04/AC05。隔离 obs002_qa2 从准确前驱升级；在最终查空前持有 18 旧表、回执、三张当前样本表、版本表的 WRITE 锁。同连接锁内逐表读取成功。另一连接对旧表并发 INSERT 等待后报 1146，对能耗样本的 UPDATE 在 DROP 后仍等待，UNLOCK 后可执行并回滚。实测竞争针对上述两表，未对其余每表各起一写者。实际拒绝未知 target、大小写或 outcome、ID 为空／错误／错属、显式顶层归档 detail、旧／未知版本、旧表非空、外部 FK／视图、缺表、错 UUID／schema／前驱及未确认写入窗口。实际 DROP 后注入中断，前驱未登记，盲目重试被拒；按记录 DDL 重建 18 个空表再验证升级。对有样本的库及另一个能耗样本数正好为零的 obs002_qa2_empty 均复验 energy/stored/999999；后者 Alembic exit 1，全部 75 表行及结构一致（排除 AUTO_INCREMENT 水位），18 表和前驱、默认值保留。
- 正例中，latest 的早期 stored、stale、already_stored 共享快照，history/no_history_metrics 携带 NULL，均通过。迁移前后 56 张保护表逐表核对 DDL 和全行，仅允许两个回执默认值变化，排除自增水位。非空行有回执 9、快照 1、过程 3、能耗 1、价格与小时价格各 1、采集来源／latest／history 各 1、计划／实绩各 1、登录账号 4。QA2 独立摘要 a2b0932230ff4ef22c76ca42211ea905c4eb0c06088d7eef8ba853e2d1709f35。
- 历史回归。逐一 git show f7c5608:backend/tests/<原名> | cmp 核对历史 mapping API、mapping service、business integration service 三份测试归档字节相同。当前保留的观察、授权、机器写入和路由由定向 pytest 与 ASGI 实际覆盖。归档三文件自身未在 QA2 重跑。首次全 no_db 结果 634 passed、5 failed、12 skipped、24 deselected，exit 1。对照原始两份历史日志，F 的 58 表断言和旧 performance descriptor 的 ProcessSpeed 导入亦失败；C2 的 integration public surface、temperature env helper、business time public symbols 三项在两侧均首先失败于历史 System 私有导入 SnapshotPolicyCatalog。后三项使用同一公开后备 bcafa89，而非原 QA3 工作树；五项有基线失败证据，QA2 未重跑全套。
- AC06/AC07。仅核验临时候选。未操作 3307、真实配置、用户服务、已有浏览器、现场设备或生产环境。正式源码整合、三处并行漂移、正式启动入口验证和 dev 切换未执行。CLI 退出范围由上述定向回归及与 QA1 候选字节对照覆盖。

### QA2 资源交接

Docker inspect 在执行前匹配 QA1 记录的完整容器／镜像 ID 和唯一 127.0.0.1:13319 绑定。三个新 QA2 合成库均在创建前复核 UUID 83ce39b2-e339-11f1-9c30-7e2b90cdaed5 及 8.4.6。obs002_qa2 保留成功升级与浏览器合成数据，obs002_qa2_detail 保留新失败现场，obs002_qa2_empty 保留原 QA1 修复验证现场；QA1 库未重置。临时夹具与日志在 /private/tmp/arch-obs-002-r1-qa2-independent，内含私有测试凭据；与任务候选和容器一起交由协调者在返工、证据固化和归属核实后回收。Verification 未清理资源。待 Development 精确返工交接后由 fresh-context Verification 复验；最终验收归 Human Owner。

## QA3 · ARCH-OBS-002 r1 第二次返工

**qa_failed，退回 Development。** AC05 仍允许含未知指标身份的回执进入删除阶段。QA1 的悬空能耗引用与 QA2 的嵌套归档引用均已在真实 Alembic 复验关闭。最终验收归 Human Owner。

### 新阻断与复现

在新建的 obs002_qa3_edge、MySQL 8.4.6、准确前驱 ae20b4d6f831 上，使用下面的语句分别插入两条 history/no_history_metrics 回执。两条均为 NULL 结果 ID、空 stored、合法 history_disabled。第一条的 metricKey 为三个 ASCII 空格，第二条为 a、U+200B、b。复现参数分别为 ('qa3-0','202020')、('qa3-1','61E2808B62')。

```sql
INSERT INTO metric_ingest_receipts
(target,producer_id,event_id,request_digest,outcome,result_record_id,contract_version,result_version,result_detail)
VALUES ('history','qa3',?,UNHEX(REPEAT('42',32)),'no_history_metrics',NULL,'aiis.metric-ingest/v2','r10',
JSON_OBJECT('stored',JSON_ARRAY(),'skipped',JSON_ARRAY(JSON_OBJECT('groupKey','safe-group',
'metricKey',CONVERT(UNHEX(?) USING utf8mb4),'reason','history_disabled'))));
```

实际夹具使用绑定等价 JSON 文本的 CAST 参数。以相同两键调用活动 writer 使用的 app.equipment_observation.domain.identifier，各返回 ObservationError 422。device_event 对每个组键、指标键调用此函数，energy_event 对组与指标亦调用；ingest_v2.device 从已校验的输入直接生成 skipped 字段。这两个键违反既有身份语法，均无法由该合同生成，无需推断历史配置。按 spec §3 及 AC05，未知身份应在删除前阻断。实际绑定已核对 UUID、schema、维护窗口，执行项目 Python 的 `-m alembic upgrade c9e1a3b5d720`，exit 0，18 表消失，两条回执键字节原样存在，新 head 已登记。字段类别、字符数通过了迁移的 _RESULT_KEY 校验。请 Development 对齐现行身份语法，同时保留普通 Unicode 标识、补充平面字符与旧表同名业务键。日志 edge.log SHA-256 006ad308cb31bdebbf25e662be6b7e9c166e16cb6003d2bbb52a46991ccf875a。

### 验收证据

- 交接指纹。spec、tasks、原 checklist 依次匹配 957956ad81ed13bea03efd98a691a62f52b7526187d8c653ae1bfdf3e0424e37、bf50fd74973a29c12f4e540f3f3fa5b15e8048731cc52697c9a2a33262b8b556、a6ff1d0ef5292efdb6ece1af5746ff6d940dc62c950ee4561cbbe42d2ffa6f7c。candidate-rework2 manifest 匹配 f724db65478afc1af28ef141715137d4e4d344787ffad0fe11b1ee8c84adb10f，逐项检查 225 个摘要与删除状态，且逐项对照前驱 preimage 列表内源码。相对 QA2 只有迁移不同，SHA-256 84c5ea03870eb3d39109d557e3bd2f1673a8520e14ea09db470f787dbccc7623。非漂移补丁 git apply --check --whitespace=error 成功，正式树三处重叠仍是 CODE_INDEX.md 与两个 frontend registry 测试。
- AC01、AC02。QA3 正向库 obs002_qa3 经真实 ASGI/MySQL 与已认证机器 API 生成 13 个合法回执，覆盖三个目标全部 outcome、共享 latest ID、缺测空包、disabled skips、64 码点含 💡 的指标和 process_monitor_r8_archive 组键，迁移前后实际读取验证通过。旧 22 方法 OpenAPI 与 HTTP 404、通用后端定向 59 passed 复用相同源码的 QA1/QA2 证据。真实合成 JWT 在升级后分别验证四种角色和匿名用户的设备、过程、能耗、管理 API，能耗读回 5 kWh。
- AC03。QA3 重新运行 node --test tests/module-registry/*.test.mjs，90 passed。首次 Vite build 缺少明确角色页配置而退出；指定合成 supervisor=[monitor.energy]、operator=[] 执行 pnpm exec vite build --outDir 到 QA3 目录成功，保留大 chunk 提示。页面菜单、实际浏览器登录、旧 URL 和管理路由沿用 QA2 的同源码浏览器证据。
- AC04。setup.sh、run.sh http_rework2 before、run.sh migration_rework2、run.sh http_rework2 after 完整执行成功。18 表精确退出，对照 56 张保护表 DDL 和全行，仅忽略自增水位并单独转换两个预期默认值。回执 13、快照 1、历史 4、表计 1、能源价／小时价各 1、PLC 来源／历史／最新各 1、计划／实绩各 1、账号 4。QA3 快照摘要 43faa56dea93ce5fdaefa9faf59638ff1c8d74bbf1666ffc13d71da5b816e660。
- AC05。原两例由实际 Alembic CLI 拒绝，比较前驱、18 表、全库所有表的行与 DDL 含默认值保持。复跑 26 项结构负例，另外独立注入 latest 的 skipped 含 owner 对象、history 的 metricKeys 含嵌套数组、energy 的 stored 含布尔值，均拒绝且全库快照一致。实际测试维护窗口、目标不符、非空旧表、外部 FK／视图、锁竞争超时 5.01 秒、并发旧表 INSERT 等待后 1146、并发保护表 UPDATE 于解锁后完成并回滚、真实 DROP 后注入中断与拒绝重试，按记录重建空表后成功升级。新身份反例见上。正向及负向验证日志 migration.log SHA-256 06be90fc1572f608d384a7d844fa5ffe2f4137036e783719239c74fbf9565d9f。
- 历史测试。逐文件 git show f7c5608:backend/tests/<原名> 对照候选，三份测试归档逐字节相同。重新核对 pytest-final.log 与 pytest-original-f.log、pytest-original-c2.log，首次全 no_db 为 634 passed、5 failed、12 skipped、24 deselected。58 表及 performance descriptor 历史断言两项、C2 三项历史私有导入错误有原基线失败记录；C2 使用公开后备 bcafa89。QA3 未重跑整套或归档测试。
- AC06、AC07。正式整合、真实 3307、实际配置和用户服务均待授权。历史工具退出沿用同源码独立定向证据。候选依赖并行前驱，整合前仍须确认三处重叠及其他工作树漂移。未测生产规模、设备和现场兼容。

### 资源与交接

Docker inspect 实核 QA1 所载完整容器与镜像 ID、PID 83027、唯一端口 127.0.0.1:13319；建库前校验 UUID 83ce39b2-e339-11f1-9c30-7e2b90cdaed5 和版本 8.4.6。新建 obs002_qa3 保存正向结果，obs002_qa3_edge 保存失败现场。夹具、私有合成凭据及日志在 /private/tmp/arch-obs-002-r1-qa3-independent。保留给协调者在证据固化、返工依赖解除并核实归属后回收。第二次返工候选验证结束，等待 Development 新交接及独立复验。

## QA4 · ARCH-OBS-002 r1 · 2026-11-18（上海）

**qa_failed。AC05 的历史样本结果身份检查失败，退回 Development。** 之前 QA1–QA3 报告的三个问题在本候选均已关闭。AC06 延后，最终验收由 Human Owner 决定。

### 可复现的阻断项

在新建的 `obs002_qa4_edge` 前驱库使用实际 ASGI 和机器认证产生 history/stored 回执。两个事件均来自 `obs002-writer`。样本的 `source_sample_key` 由当前 writer 的 `services/ingest_v2.py` 第 157 行以 `SHA256(canonical_bytes([producerId,eventId]))` 生成，历史样本同时保存回执外键，回执保存该样本主键。用同一 canonical 函数重算得 first 为 `7e16bb91577ebcc0134e89c1ef431a09cd7d58fbdbb41d9ed62f507f4c17b27b`，late 为 `d8d4fb63aef3b51855bbb9b1c717a5900dd95c63a7644909e9322ea75b29dfaf`。已断言互换前两个摘要与持久化值分别一致。两个合成 UPDATE 在同一事务内交换 result_record_id 和 ingest_receipt_id。样本身份键、回执 producer/event、数据内容和版本均原样保留。

| 历史样本 ID | 持久化身份键对应事件 | 原回执 ID / event | 互换后双向引用的回执 ID / event |
| --- | --- | --- | --- |
| 1 | first | 4 / first | 8 / late |
| 2 | late | 8 / late | 4 / first |

实际执行 `python -m alembic upgrade c9e1a3b5d720`。初次探针缺显式 expected schema，守卫拒绝，exit 1，前驱及 18 表仍在。校验同一 UUID、schema 和原有错指现场，显式传入精确目标后 exit 0，revision 由 ae20b4d6f831 变成 c9e1a3b5d720，18 个目标表全部消失。升级后再次读取，两个样本各自仍指向另一事件的回执。当前迁移只比较两侧结果／回执 ID，未发现可由样本身份键直接证明的错指。按 §5.2，应在删除前阻断。这里使用的是拥有固定结果的 history/stored；共享可覆盖快照的旧 latest 回执有不同的所有权语义。 Development 返工应保留现行合法回执并重测。独立夹具 `edge/edge.py`、`edge/retry.py`，后者执行日志 SHA-256 为 `65716a4ebe24dcef21b1302da7111e429c99fe4a9a4f57d7adf8ba9dfa6b85f8`。

### 精确候选和验收证据

- 工作区为 candidate-rework3。原 spec／tasks／checklist 摘要与交接一致。清单 SHA-256 为 `893e2378f5b91c44779b190aada69fab073fab51609b8b882fb56efc9f302d07`，逐条核对 6 新增、75 修改、144 删除。对 preimage 和 manifest 并集的 1,498 路径比对 QA3，仅迁移和 test_observation_retirement.py 不同，对应 SHA-256 为 `224733b68dbc9deb9e4c8ddc76c0a98315bb55d63b6282c1e543533f13a76bee` 与 `479c2f042b5bae990c21795ee85a70bd3805677ce3071b1d8bfb78e8f31e3297`。非漂移补丁 git apply --check --whitespace=error 成功。
- AC01、AC02、AC03。正向库独立执行 setup.sh、run.sh http_rework3 before／after，真实 JWT、机器 Bearer、MySQL 生成 154 条回执，覆盖三类目标、各 outcome、缺测／晚到、重试与冲突、独立能耗和角色 scope。升级后读取、权限及表计统计通过。候选 backend 执行 pytest -p no:cacheprovider -q -m no_db tests/test_observation_retirement.py tests/test_equipment_observation_r10*.py，56 passed，一个原 SQLite datetime 警告。frontend-js 执行 node --test tests/module-registry/*.test.mjs，90 passed。沿用同源码 QA1–QA3 的 22 旧方法、路由、构建、文案与角色浏览器检查。重核原基线日志，整套 634 passed、5 failed、12 skipped、24 deselected；前述五个基线失败及后备夹具限制仍适用，QA4 未重新运行全套。
- AC04。run.sh migration_rework3 使用 QA4 的 UUID、端口和新合成库重放交接矩阵，exit 0。实际 18 空表退出、56 保护表（行和 DDL／约束）对账，含 154 回执、非空配置、采集、价格、计划／实绩、账号及样本。版本默认值 v2／r10 正确，对账摘要 `91731f6a02c8613b2160f40af72175e35e1e74c738ccc29014f117d2d7c61744`。合法内部空格、中文、非 BMP、Unicode 边界长度、与归档同名的组键、成对 mapping、sourceRefs 的空数组、opaque 额外字段和等价 SQL／JSON null 均保留。
- AC05。实际 Alembic 拒绝 QA1 悬空能耗结果、QA2 嵌套旧归档位置、QA3 空白和 U+200B；结构、源引用及身份反例、多页末部坏值、旧版本、外部 FK／视图、非空旧表、目标和窗口守卫均复测。64 行一页，第三页发现非法字段后表、数据、默认值和前驱一致。并发锁等待 5.01 秒超时，旧表 INSERT 等待后收到 1146；保护表竞争更新在解锁后才完成，夹具回滚。真实 DROP 后模拟结果未知、复核原始状态、拒绝盲重试、以记录 DDL 重建空表及再次升级均验证。正向库 migration.log SHA-256 为 `a5b88b9abf1b28fa924ecd003aed46f18ea3c03b78442269c4c2572d7a2c83f2`。另一个独立库的错指结果使 AC05 失败。
- AC06 deferred。AC07 工具边界沿用相同源码的既有独立结果。正式树整合、真实 dev 数据或配置切换、服务启停及现场采用均需另行授权。本次未验证整合预览、真实设备或生产规模。

### 资源与 handoff

已 inspect 容器 arch-obs-002-r1-qa，完整 ID 为 `9590dbfa32029556183ac76eecf0605bc722c2b38ab38277bc4455a4af0395ed`，镜像 ID 和唯一绑定 127.0.0.1:13319 匹配。建库前核对 MySQL 8.4.6 及 UUID `83ce39b2-e339-11f1-9c30-7e2b90cdaed5`。保留 obs002_qa4、obs002_qa4_edge、`/private/tmp/arch-obs-002-r1-qa4-independent`（含合成凭据，勿公开）及所有前轮证据，供 Development 精确返工及独立复验；解除证据依赖后由协调者核实归属收尾。本轮仅追加本 checklist。等待 Development 新交接。

## QA5 · ARCH-OBS-002 r1 · candidate-rework4（2026-11-18 上海时间）

**qa_passed（批准的源码候选及隔离验证范围）。AC01–AC05、AC07 通过；AC06 deferred，等待 Human Owner 决定正式整合与真实目标操作。** 本轮由 fresh-context Verification 执行。QA1–QA4 原文及失败现场保留。以下 SQL、浏览器和测试结果来自本轮 QA 运行。

### 精确交付面

- spec、tasks、追加前 checklist 的 SHA-256 分别为 957956ad81ed13bea03efd98a691a62f52b7526187d8c653ae1bfdf3e0424e37、992591882d335acc69f1b4040eac943a23750af53b63f81fe53fdf25bc136270、2e036e6468fd3c1907fdf39e618183f0b3c71e57eb4a50e205ffb94bba31fa0c。
- 对照正式工作树、保存的原像、整合预览和 candidate-rework4，逐项核验 6 新增、75 修改、144 删除。manifest 4c897ce32f6a7a92232e1cd2292d7a7e969e4164df4199f1afd32378c2a140b7，完整 patch cd70404c1831f06a7d93e67310b8fe28b26010ed778a653a50701ce615cc9acf，git apply --check --whitespace=error 成功。预览与 QA4 的 225 路径中仅 CODE_INDEX、page-access.test.mjs、registry.test.mjs 三个重叠文件有变化，分别保留共享字段索引、管理员清单和路由装配。预览到本候选仅迁移及其回归测试变化。迁移 db65a407492bdd7b68345ff76df45646dc5dd03b6347c30e923aa47354f10898。
- 对清单以外基线 1,276 路径比较预览和本候选，全部符合捕获摘要。另逐条核对相对 QA4 的 22 路径并行变化。正式 PLAN 双语、plans/README 双语在捕获后已有新修改，均在补丁范围外，正式整合须保留最新文本并再查 preimage。历史 test_mapping_api.py.txt 和正式旧路径原始字节摘要均为 434b6c18007da5d2b1d4c19c2a870f4fb470600d1e34fad9237052a730061072。

### 独立环境、命令及结果

- Docker inspect 核对 QA 容器完整 ID 9590dbfa32029556183ac76eecf0605bc722c2b38ab38277bc4455a4af0395ed，镜像 sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9，仅绑定 127.0.0.1:13319。create.py 先断言 UUID 83ce39b2-e339-11f1-9c30-7e2b90cdaed5、8.4.6，再 CREATE DATABASE obs002_qa5。按 QA4 设置和经过审阅的交接夹具重定向到全新 QA5 目标。依次 bash run.sh create、bash setup.sh、bash run.sh http_rework4 before、bash run.sh migration_rework4、bash run.sh http_rework4 after，均 exit 0。前驱夹具临时允许旧 revision 生成真实 writer 样本，升级后的请求走实际新 revision。
- **AC04/AC05**。真实 Alembic CLI 测试使 history/stored 的 first、late 同时交换两侧关联，保持主外键成对且保留原样本身份值。upgrade c9e1a3b5d720 返回 1，报 unknown observation sample source identity；检查前后每表 SHOW CREATE TABLE、所有行和 alembic_version 全部一致（DDL 对账忽略 AUTO_INCREMENT 计数）。对 latest 两个当前 stored owner 互换、单独伪造合法 producer/event 和第三页篡改样本摘要亦在 DDL 前拒绝。冻结算法对两个字符串执行无 ASCII 转义、无分隔空格的 JSON，strict UTF-8 后 SHA-256；与 writer canonical_bytes 的字符串数组分支逐步一致，不读取现行私有 profile。
- 成功升级后另编 proof.py，使用 writer 的 canonical_bytes 独立读取并重算全部 2 个实时和 5 个历史 owner 的身份摘要，7/7 相同。两类对象均有含引号、反斜杠及 Unicode 的真实 producer/event，末页实际序位分别为 154、155。快照 1 保留 147 条共用结果的回执，包含 stored、already_stored、stale，快照 2 有 1 条 stored。proof.log SHA-256 517513c3301d389a2e430fa8d7f8c78fd0c5a3aa19a2a1a1235b2bfc70108151。
- 重跑 QA1 悬空能耗、QA2 嵌套归档、QA3 空白／不可见字符、非空旧表、身份／窗口／前驱、外部 FK 和可见对象等拒绝场景。实测锁等待 5.02 秒，竞争旧表写入待锁后获 1146，竞争保护表更新解锁后完成并由夹具回滚。模拟真实 DROP 后结果未知，核对现场、拒绝盲重试、按存档 DDL 重建空表并重新验证。实际正向升级移除精确 18 表，56 张保护表全行及结构／约束对账，两个回执默认值变为 v2、r10。保留 156 回执、配置、价格和小时价、采集来源和历史／最新、计划／实绩、独立能耗及账号。保护摘要 4f3b425dc433e7522037e6f465da40671dfbee5f961fccae49eadb41c496be44，migration.log 摘要 0b2e08e0e924df8ae2f3a7cea48be1c0c49f206fdbbc5117f34635099bfa9265。
- **AC01/AC02/AC03**。本候选真实 ASGI/MySQL 写入和登录读回，覆盖多区域、重试／正文冲突、缺测、过期、独立表计及权限。22 个退役方法逐个 404 沿用此前同源码 QA1 结果，本轮另跑 retirement、OpenAPI 等定向用例。node --test tests/module-registry/*.test.mjs 92/92；manifest checker 27 路由、9 组；production 权限 checker 和 Vite build 均 exit 0，保留既有 chunk 大小提示。对本轮构建执行 node browser-rework4.cjs，以独立无头 Chrome 和真实登录访问 16 个页面及对应 GET，覆盖计划／实绩列表和两条共享字段管理路径。管理员菜单唯一新版能耗入口、旧 URL 重定向、supervisor 能耗与管理边界、空 grant operator／outsider 重定向均通过。browser.log 摘要 c95b69309c4dec361b61f57cff623d094c9df0112ffba4407d3ae96eec87dd08。
- 组合回归使用候选 backend，pytest -p no:cacheprovider -m no_db，覆盖 generic_task*、observation_retirement、equipment_observation*、business_time_adoption、business_integration_storage、plc_facts_v2、acquisition_data_browse、business_module_permissions、openapi_router_tags。首次 248 passed、1 failed、9 skipped，C2 子夹具在临时副本查找 Git 失败。显式指定正式 Git 只读入口、固定公开历史 backend 和锁定 Python 环境后单独重跑该项，1 passed。合计 249 项通过、9 项跳过，原 SQLite datetime 弃用提示。全量后端未重跑，QA4 所引原基线五项失败仍适用。
- **AC06 deferred；AC07 通过**。工具入口沿用 QA1 同源码裸调用证据及本轮 business_time_adoption 定向回归。仅验证 Python 3.13.3 / UCD 15.1.0 与上述分页合成负载；跨 Unicode 数据库版本、生产数据量、真实设备及冻结 CA 兼容性无实测。

### Handoff

交 Human Owner 决定最终验收。正式工作树整合、3307 和实际私有 profile／配置、用户服务操作仍待单独授权。仓内仅追加本 checklist。保留任务容器、obs002_qa5 和 /private/tmp/arch-obs-002-r1-qa5-independent（含合成凭据、恢复 DDL、运行驱动与日志），用于验收追溯。此前各轮数据库及证据保持原位；由协调者在证据依赖解除并核实归属后统一收尾。

## 正式 dev 切换独立复验（QA6，2026-11-18，Asia/Shanghai）

**ARCH-OBS-002 r1，AC06 通过，整体 `qa_passed`。** 已结合 QA5 同一冻结候选的 AC01–AC05、AC07 证据和本轮真实 dev 复验。Human Owner 已报告服务恢复，最终验收待 Owner 记录。

- 交接基线。独立核对 spec、Development tasks 和追加前 checklist 的 SHA-256，分别为 `957956ad81ed13bea03efd98a691a62f52b7526187d8c653ae1bfdf3e0424e37`、`4e2e4812ca76e876d73f6fa1faae6baf57c20c67523d309ec3e824a6c3b0130d`、`2184c0e205942e64e5636b22c107f9ac1711cb0084549779bd0e021a8a5de169`。正式 Git HEAD 为 f7c5608c0e433612b15821a578a7ef3e4f155cdb。以 Python hashlib/pathlib 对 manifest 每行核工作树与 QA5 候选，A6/M75 的字节和文件模式相同，D144 两端均不存在。manifest/补丁摘要分别为 4c897ce32f6a7a92232e1cd2292d7a7e969e4164df4199f1afd32378c2a140b7、cd70404c1831f06a7d93e67310b8fe28b26010ed778a653a50701ce615cc9acf。另对 preserved-capture-files.sha256 全部 1,276 项重新散列，差异 0。正式 backend 项目解释器执行 `-m alembic heads` 和 `-m app.module_preflight --project-root "$PWD" --check-only` 均 exit 0，唯一 head c9e1a3b5d720。frontend-js 执行 `pnpm check:access --mode development` exit 0，supervisor 3、operator 2。
- 维护窗口证据。核对 window.py 真实执行分支、私有 migration.log 和 db/deps 的前后留存。固定目标前驱 ae20b4d6f831，窗口快照显示其他会话、活动事务及待锁均为 0，驱动先验证旧表为空、允许的 FK 和回执，再执行一次指定 head 的 Alembic upgrade。迁移日志 SHA-256 11c543ee80e294c949df98c3810c96208f0aaa8bf175b088753e2deda275d224。独立按 spec §2.1 解析出 18 个表名，比对数据库快照和恢复 DDL 集合，75 → 57 恰好退出该集合。按关系两端筛除退役表后，48 → 29 条 FK 与其余依赖证据完全一致。
- 真实库只读校验。普通沙箱连接被拒，受审本机连接 exit 0。2026-11-18 19:50:53 +08:00，以项目应用账户向 127.0.0.1:3307 / industrial_level_2_system 执行 `START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY`。SELECT 确认 MySQL 8.4.6、UUID 摘要前缀 ac2319a3fdc8、UTC 偏移 28800 秒、唯一 revision c9e1a3b5d720。对 56 张保护表逐张重算全部行的有序行摘要、计数、SHOW CREATE TABLE 摘要（忽略自增水位），与迁移后记录完全匹配。对迁移前记录独立复算差异，仅回执的 contract_version/result_version 默认从 v1/r8 变为 aiis.metric-ingest/v2 与 r10，现存回执 0 行。涵盖区域／指标、价格、计划、实绩、用户与采集，包括 1 个设备指标分组、2 个指标配置、1 个价格及 3 个分时价、3 个 PLC 来源、6 行 latest、107 行历史。真实当前信息架构中 29 条 FK 逐列相同。db-before/after 的 SHA-256 分别为 58974b490d0c4edd7fd79821ef53b894e52a3d178d4dcc119286b8bf74a58a52、856d4334f3f853112d3e8e36fba5af2009983d0655d46c777e467dd7a53479c5；deps-before/after 分别为 271a2497f1604140bfa21bfcfcf221910452d61df235b0b7844035a983287ba8、bd0445a27cf2bf4865dbc147cdeb6b0166301fb077079b89c106941417337a0d。
- 配置。对两份实际启用的私有 profile 核对目标 schema、UUID 摘要、唯一 revision、前后整文件指纹、属主／组及 0600。仅反向替换 revision 就准确重建历史指纹，两种正式 loader 均读取新 revision。对 backend .env 的两个有效角色数组各仅补回一个 monitor，在内存中重建完整 preimage 并命中历史指纹，两角色均未获得 energy-consumption-read，settings 与磁盘相同，属主／组与原 0644 一致。初次重建探针遗漏空数组，修正解析后 exit 0。config-locked-window.json 摘要 aec9470571c319eab0e2c8ad047ea95a1c1ccfeb7e14f622f6dc775cf19ad051。前端 .env* 窗口前后指纹一致依据 Development 的同进程采集和比较，QA 另以实际环境运行权限 checker。
- 已恢复服务。仅通过 urllib 向实际 8000 和 5190 发匿名 GET。/openapi.json 返回 200，有 101 条路径，spec 列出的 22 个旧方法均缺席，所有旧 GET 实际返回 404。新版实时／历史机器接口、发现、表计接口、计划、实绩、PLC Facts 和单价仍注册。九个正式 GET 均在 OpenAPI 中并返回 401，包括设备 observation-options/latest-cards、过程 observation-options/history-curves、integration/metric-definitions，以及能耗 consumption/options、consumption/summary、metric-configs、admin/consumption-samples。5190 首页、Vite 客户端、新版监控 API 模块均 200。首次探针误将单价路径写作 /energy/price，依据现行正式路由修正为 /energy/current 后 exit 0。真实账号正向授权读取及交互界面沿用 QA5 的隔离角色浏览器证据，本轮未登录正式账号、提交业务请求或操控服务。
- 环境及收尾。Python 3.13.3 / UCD 15.1.0。沿用全量 no_db 基线五项失败（历史 58 表断言、ProcessSpeed 导入和三个 C2 夹具导入），本轮未重跑全套。跨 UCD、生产负载、真实设备／SMA／DAA 和冻结 CA 兼容性仍无现场实测。QA 阻塞项为零。保留任务所属隔离容器、QA 候选与 0700 私有证据目录 /private/tmp/arch-obs-002-r1-dev.vqRvqwhQ，供 Owner 验收及后续资源收尾。外部写入恢复由 Owner 控制。
