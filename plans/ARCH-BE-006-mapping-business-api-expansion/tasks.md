Task ID: ARCH-BE-006
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r1 B Development三专用schema真实矩阵与五页CUA完成，已锁定新交接；等待全新资源上的fresh B Verification及Human Owner最终验收

# 批准及起点

Human Owner：“批准 ARCH-BE-006 r1，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
批准spec SHA256：58c69b8eac6e3a182e6592c2c048743566100eee6c77307ac2fa885a33265557。
HEAD=f85bea8bbf36b491968c3dc9a839518a1ed434a8；起点公开1538文件、六索引dirty和新spec由Root记录于`/private/tmp/arch-be006-r1-source-a0cpj4yj/entry-files.json`及entry-source；不归本Development源码增量。
本角色只写本tasks及r1有限allowlist，不改spec/checklist、根/backend PLAN、其他bundle、skills、依赖或锁文件。

# 执行计划及边界

1. A0：分域Model/receipt、严格输入/纯规则、本地scope、局部HTTP生命周期和显式迁移 → recorder/offline/兼容源码检查。
2. A1：equipment新写读及温控adapter/三页面 → 定向无DB合同检查。
3. A2：生产生命周期/水位/人工优先、父子过程、实绩页面 → 定向无DB状态/事务检查。
4. A3：曲线写读/来源页面、文档索引及集中收尾 → 完整no_db、compile、check:modules/test:modules/build。

仅公开隔离源码副本、合成配置、现有uv/uv.lock和pnpm/lock/已装依赖；全DB（含SQLite）、外网和listener硬阻断。禁止真实env读取、所有Docker、数据库/在线Alembic、应用/浏览器listener、PLC/Projection运行、安装/网络、Git stage/commit/ref/push。
B源码可准备但不得执行，A不替代B、独立QA或Owner最终验收。

# 实施事实

A0开始：已读根AGENTS/workflow/Development profile、批准r1、相关模块规范、BE003/BE005当前事实与实现。使用aiis/CONTRACTS、backend-arch相关references、frontend-ui/FRAMEWORK、i18n-workflow和code-document-indexer。
FLOAT选择IEEE754 binary32规范值：有限原始JSON数→binary32舍入一次，必须非零不归0且满足公开容差，后续fingerprint/比较均用该存储规范值；Numeric原始Decimal校验尺度不舍入。具体测试及命令结果随实际执行追加。

A0第一次隔离compile exit1：生成production-parameter CRUD一行缩进错误，已仅修该行；原失败日志`/private/tmp/arch-be006-r1-dev/a0-first.log`保留。

# A定向执行记录（持续）

公开隔离driver为`python3 /private/tmp/be006-run.py <name> [payload]`；底层固定`uv run --offline --frozen --no-sync python -c <guard+payload>`，cwd仅`/private/tmp/arch-be006-r1-dev/<name>/backend`，复用原.venv、不装依赖。driver/guard/payload/commands.jsonl与各log保留。

- A0 a0-first/second exit1：新CRUD生成缩进/随后窄修缩进错误；a0-third exit1 manifest非字面量；a0-fourth exit1条件异常枚举不符preflight；a0-fifth exit1其他owner新error未声明；均真实失败并已按现有Core规则修正，不修改preflight。a0-sixth compile/Model/应用组合exit0（早期候选）。
- metadata/a-all-compose exit1：旧Service内新增错误枚举需top-level import供preflight解析，已修正；a-compose-2 compile/应用组合exit0。这些不是最终全范围检查，全部日志保留。
- focused-first：39 passed/4 failed、exit1；新测试identity helper重复keyword三例、替身add未模拟flush一例。修正测试替身忠实模拟CRUD调用后focused-second为43 passed/exit0。
- focused-api：63 passed/exit0，覆盖原始严格JSON、camelCase/0/UTC毫秒、四主写面真实ASGI、静态mapping-records优先路由、admin/独立grant/scope、局部system/DBAPI依赖退出脱敏及提交后同键恢复。ASGI内存transport不创建listener、不作为MySQL/浏览器证明。

NULL策略：equipment新增可空观测类型evaluates_none保留旧default且HTTP None进入SQL参数；performance四默认数量/评分类型保持原ORM flag，仅新HTTP CRUD把缺测显式转SQL null()，避免改变旧人工Create显式None的default0语义。新HTTP来源时间与系统DB时间分开。

# 最终A Developer handoff（2026-10-16）

精确`ARCH-BE-006 r1`，批准spec SHA保持`58c69b8eac6e3a182e6592c2c048743566100eee6c77307ac2fa885a33265557`。
工作树HEAD仍`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，未stage/commit/创建ref/worktree/push。主协调者的六索引独立，不归本Development增量。

## 实施结果与有界技术选择

- 七个新async POST与指定新GET、BE003温控dashboard adapter已接入；分模块receipt与生产状态水位、精确binary设备/卷/zone键、业务/receipt同事务，三次上限命名unique重读。CRUD不提交，Service不执行同步DB。温控原POST/GET及八sync Services/Projection调用链保持。
- 设备/三过程同键只补NULL，任何旧非空异值整次409；曲线33项不可变；生产同刻事件判重/冲突、晚到stale、水位防旧回放、重激活/前卷退出、同设备父与精确卷校验。新HTTP无PLC provenance、不操作Plan/能源汇总。
- 人工重量仍沿原PUT权限，HTTP必须显式source/equipment，只接受weight/remark；manual override含0优先，采集只更新collected。DELETE HTTP域409，旧读NULL域404；新范围不能靠猜id绕过scope。主行加锁同步人工与观察；DB并发两提交顺序尚待B。
- 总用时优先manual pair→reported pair→first/last，输出秒与来源；负范围或超既有INTEGER表示域`0..2147483647`拒绝422并回滚，不截断。Root转递PM确认这是r1必要技术表示限制，不增加r2或客户业务阈值。
- FLOAT按binary32单次规范化，非零不得归0，并同时检查相对≤1e-6与绝对公开容差；fingerprint/冲突比较同一存储规范值。Numeric由原始Decimal校验技术域/scale不舍入。设备身份不trim；普通grade/spec/remark仅非空白/长度/UTF8，保留来源空格。
- 只增一条f6后继与四表；七目标nullable键/时间毫秒、原53签名保护。全值卷/zone键使用MySQL VARBINARY(200)，不用BLOB/prefix unique。新设备None用evaluates_none，新主实绩默认字段仅HTTP CRUD显式SQL null()，原人工Create None→default0保持。
- 五页面入口新增URL来源/设备选择，默认legacy、HTTP空设备不查，切换清空/请求代次隔离；HTTP不走mock/fallback，缺测为符号/断点，真实0保持。实绩HTTP编辑其他字段只读；布局、菜单、pageId和grants保持。
- 新局部HTTP在响应发送前退出本请求两层FastAPI dependency stack，恢复原scope；锁定FastAPI0.135.1现有内部stack约定，未来升级须重验。旧全局错误壳不改。日志仅受控actor/stream/equipment/id/outcome/状态及拒绝失败，不输出payload/token/SQL/DSN/测量值。

## 最终DEV检查矩阵和精确命令

以下均真实执行，125包含此前43/63/97/100/123/124，不能把它们相加。旧483、当前全套、当前新测试、前端46与来源10分别明确输入和含义。

| 输入/命令（driver底层命令归commands.jsonl及payload） | 真实结果与限制 |
| --- | --- |
| `BE006_SOURCE_ROOT=/private/tmp/arch-be006-r1-source-a0cpj4yj/entry-source python3 /private/tmp/be006-run.py full-frozen60 /private/tmp/be006-full.py` | exit0；全树compileall成功，完整原no_db **483 passed/30 deselected**，410.33s。冻结起点60表/69key/e4合同；不冒称验证当前f6新功能。 |
| `python3 /private/tmp/be006-run.py full-current-1 /private/tmp/be006-full.py` | **exit1；552 passed/4 failed/30 deselected**，463.07s；同次compileall成功。全当前套件实际执行，未deselect/skip/xfail或改旧断言。 |
| `python3 /private/tmp/be006-run.py all-focused-final-exact /private/tmp/be006-final-focused.py` | **exit0；125 passed**，6.22s；最新全树compileall成功。当前64新schema/数值/JSON/JWT/权限/scope/局部退出/合并/事务/生产生命周期/父/人工0与时间、SQL NULL/legacy默认/SQL过滤/迁移/69+3配置/旧5字节/B旧行校验函数。 |
| `python3 /private/tmp/be006-run.py final-compile-offline-collect /private/tmp/be006-collect-offline.py` | exit0；全树compile、base→f6 offline SQL、heads/history通过；唯一f6 head/d4 root、VARBINARY(200)/DATETIME(3)离线SQL；`pytest --noconftest --collect-only -q tests_mysql/test_mapping_business_api.py` **1 collected**，未执行函数。后续普通文本纯校验微修由末次125/compile覆盖，B入口字节未变。 |
| `python3 /private/tmp/be006-frontend.py frontend-final-1` | 四步exit0：`pnpm --config.verify-deps-before-run=false check:modules`（23 routes/9 groups），`test:modules` **46 passed**，`node --test ...` **10 passed**（含真实drive SFC晚设备响应/空设备/真实0、facade路径/日期、双语duration来源），`pnpm --config.verify-deps-before-run=false build`通过。既有chunk>500k警告，无浏览器listener。 |
| `git diff --check`、`git rev-parse HEAD` | exit0；HEAD同上；新增文件patch/allowlist和保护字节由Root最终diff审计复核。 |

当前全套四失败精确为：

1. `test_business_module_migration.py::test_all_operations_match_58_tables_and_only_new_42_are_removed`：冻结58的七目标旧签名与当前增量不等。
2. `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment`：冻结69而当前72。
3. `test_equipment_temperature_migration.py::test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types`：冻结5条而当前6条。
4. `test_equipment_temperature_migration.py::test_single_explicit_head_and_no_data_migration`：冻结e4而当前f6。

Root转递PM的只读r1澄清：完整覆盖可以按冻结F58/BE00360与独立BE00664矩阵验证，不等于默认当前单次pytest全绿。
当前125明确补证四项：60→64/七表增量/其余53完整签名保护、原69前缀逐字hash+3空scope、原五migration逐字hash、f6唯一e4后继/head。
原失败日志保留，当前suite仍如实exit1；本矩阵是否满足A由fresh Verification独立判断，Development不授QA结论。
完整当前suite后仅新合同边界/日志/普通文案校验及B测试/文档/UI窄收尾有变；末次125及前端最终构建使用当前对应源码，未无依据重跑冻结483。

## 失败、环境与未运行边界

额外真实定向历史：migration-first 9 passed/1 failed（测试ORM insert collector缺合成dialect），修测试后migration-second 10 passed；focused-final-1为73 passed/1 failed、all-focused-final为96 passed/1 failed，系manual API测试只替换Depends而未注入其每app公开config，补合成app.state配置后all-focused-final-2为97 passed。后续100、123、124、125逐步增强均exit0。失败不删、不伪造为通过。

前端首次`frontend-first` exit1：pnpm11自动verify-deps触发registry检查/自动install流程，registry网络失败后在`ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`中止，无完成安装。
随后显式禁verify/update，NODE_OPTIONS继承guard拒绝Socket.prototype.connect、Server.listen、TLS/http/https及dgram bind/connect。
原node_modules/.modules.yaml与.pnpm/lock.yaml mtime均2026-09-07，早于本turn；未创建ignored依赖完整基线，不能据此证明所有依赖文件逐字零变，作为限制保留。pyproject/lock源码未改。

Backend所有项目命令只在公开tmp副本用原uv环境、frozen/no-sync/offline锁；SQLAlchemy/DBAPI/SQLite/socket connect/bind/listen拒绝guard注入嵌套uv；最新guard再以audit hook拒绝真实workspace env打开。
合成MySQL地址127.0.0.1:1、mock/runner/三bootstrap关闭、grants=[]。TESTING不是隔离保证。拒绝日志不存在；未连接/创建/读写任何数据库（含SQLite），未运行任何Docker命令、在线Alembic、服务listener、浏览器目标、PLC/Projection、安装或Git写入。
前端首次隐式联网尝试如上单独如实记录；其后guard下无网络/listener尝试。未读取/修改真实.env、实际grants、客户数据或现场资源。

## B独立入口与继续gate

`backend/tests_mysql/test_mapping_business_api.py`独立于共享破坏性conftest；只编译、guarded collect及纯函数无DB检查，**B函数未执行**。
具体目标须由Root提案及Human Owner另批，不能复用BE003/BE005许可。精确调用接口：

- 公开tmp profile.json：profile=BE006、expected_table_count=64、target_revision=f6a8c0e2b4d6；无.env。
- `BE006_MYSQL_SCENARIO=empty|upgrade|rollback`；`TEST_MYSQL_DATABASE=BE006_MYSQL_SCHEMA_ACK=arch_be006_r1_<scenario>`。
- `BE006_MYSQL_ENDPOINT_ACK=127.0.0.1:<MYSQL_PORT>`、`MYSQL_HOST=127.0.0.1`；`BE006_MYSQL_DISPOSABLE_ACK=ARCH-BE-006-r1`。
- 主库占位名称必须不同；TESTING=True、PRIMARY_DATABASE=mysql、mock/runner/bootstrap=False、非root、实际MySQL8.4.6、每scenario起始全空schema；口令只process传递。
- 获具体批准后才可在该副本显式`uv run --offline --frozen --no-sync python -m pytest --noconftest -q tests_mysql/test_mapping_business_api.py`。

源码已覆盖base→f6；e4反射七表合成旧0/秒值/重复键→f6；空HTTP回退/re-upgrade；原列/原PK逐旧行保护；新八类写读、实际人工0优先及三过程/33曲线与部分首次并发。
这只是预备入口，不宣称已完成实库所有故障/并发/两提交顺序、浏览器五页/日夜/窄屏/双语或现场量纲证明。B的完整矩阵与具体运行方案仍须在获批目标逐项执行；当前来源页面只能源码/SFC/build证明。

## 实际修改文件

以下是本Development相对entry-source的有限文件集合，before/after hash与逐行diff在最终handoff evidence中，tasks自引用hash统一只写外部handoff.json。
- `CODE_INDEX.md`
- `backend/.env.docker.dev.example`
- `backend/.env.docker.prod.example`
- `backend/.env.example`
- `backend/README.md`
- `backend/README.zh-CN.md`
- `backend/alembic/versions/20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py`
- `backend/app/README.md`
- `backend/app/README.zh-CN.md`
- `backend/app/equipment/README.md`
- `backend/app/equipment/README.zh-CN.md`
- `backend/app/equipment/api/mapping_http.py`
- `backend/app/equipment/api/mapping_samples.py`
- `backend/app/equipment/api/temperature_dashboard.py`
- `backend/app/equipment/crud/async_drive_sample.py`
- `backend/app/equipment/crud/async_equipment.py`
- `backend/app/equipment/crud/async_mapping_ingest.py`
- `backend/app/equipment/crud/async_production_parameter_sample.py`
- `backend/app/equipment/crud/sync_drive.py`
- `backend/app/equipment/crud/sync_production_parameters.py`
- `backend/app/equipment/manifest.py`
- `backend/app/equipment/mapping_config.py`
- `backend/app/equipment/mapping_domain.py`
- `backend/app/equipment/mapping_error_codes.py`
- `backend/app/equipment/models/__init__.py`
- `backend/app/equipment/models/equipment.py`
- `backend/app/equipment/models/mapping_ingest.py`
- `backend/app/equipment/schemas/drive_sample_in.py`
- `backend/app/equipment/schemas/mapping_sample_query.py`
- `backend/app/equipment/schemas/production_parameter_sample_in.py`
- `backend/app/equipment/services/async_drive_sample.py`
- `backend/app/equipment/services/async_production_parameter_sample.py`
- `backend/app/equipment/services/async_temperature_dashboard.py`
- `backend/app/monitor/README.md`
- `backend/app/monitor/README.zh-CN.md`
- `backend/app/monitor/api/mapping_http.py`
- `backend/app/monitor/api/process_curve_samples.py`
- `backend/app/monitor/crud/async_mapping_ingest.py`
- `backend/app/monitor/crud/async_process_curve_sample.py`
- `backend/app/monitor/crud/async_temperature.py`
- `backend/app/monitor/manifest.py`
- `backend/app/monitor/mapping_config.py`
- `backend/app/monitor/mapping_domain.py`
- `backend/app/monitor/mapping_error_codes.py`
- `backend/app/monitor/models/__init__.py`
- `backend/app/monitor/models/business_history.py`
- `backend/app/monitor/models/mapping_ingest.py`
- `backend/app/monitor/schemas/process_curve_in.py`
- `backend/app/monitor/schemas/process_curve_query.py`
- `backend/app/monitor/services/async_process_curve_sample.py`
- `backend/app/performance/api/mapping_http.py`
- `backend/app/performance/api/mapping_observations.py`
- `backend/app/performance/api/process_samples.py`
- `backend/app/performance/api/routes.py`
- `backend/app/performance/crud/_sync_process_common.py`
- `backend/app/performance/crud/async_mapping_ingest.py`
- `backend/app/performance/crud/async_performance.py`
- `backend/app/performance/crud/async_process_sample.py`
- `backend/app/performance/crud/async_production_observation.py`
- `backend/app/performance/crud/sync_process_speed.py`
- `backend/app/performance/crud/sync_process_temperature.py`
- `backend/app/performance/crud/sync_process_tension.py`
- `backend/app/performance/crud/sync_production_record.py`
- `backend/app/performance/manifest.py`
- `backend/app/performance/mapping_config.py`
- `backend/app/performance/mapping_domain.py`
- `backend/app/performance/mapping_error_codes.py`
- `backend/app/performance/models/__init__.py`
- `backend/app/performance/models/mapping_ingest.py`
- `backend/app/performance/models/performance.py`
- `backend/app/performance/schemas/mapping_query.py`
- `backend/app/performance/schemas/performance_all.py`
- `backend/app/performance/schemas/process_sample_in.py`
- `backend/app/performance/schemas/production_observation_in.py`
- `backend/app/performance/services/async_mapping_query.py`
- `backend/app/performance/services/async_performance.py`
- `backend/app/performance/services/async_process_sample.py`
- `backend/app/performance/services/async_production_observation.py`
- `backend/tests/module_admission_fixtures.py`
- `backend/tests/test_equipment_mapping.py`
- `backend/tests/test_mapping_api.py`
- `backend/tests/test_mapping_compatibility.py`
- `backend/tests/test_mapping_migration.py`
- `backend/tests/test_mapping_service.py`
- `backend/tests/test_monitor_mapping.py`
- `backend/tests/test_performance_mapping.py`
- `backend/tests_mysql/test_mapping_business_api.py`
- `frontend-js/README.md`
- `frontend-js/README.zh-CN.md`
- `frontend-js/src/app/equipment/api/index.js`
- `frontend-js/src/app/equipment/api/mapping-source.test.mjs`
- `frontend-js/src/app/equipment/views/drive/index.vue`
- `frontend-js/src/app/equipment/views/production-parameters/index.vue`
- `frontend-js/src/app/equipment/views/temperature/index.vue`
- `frontend-js/src/app/monitor/api/index.js`
- `frontend-js/src/app/monitor/api/mapping-source.test.mjs`
- `frontend-js/src/app/monitor/components/QualityCurve.vue`
- `frontend-js/src/app/monitor/components/SpeedCurve.vue`
- `frontend-js/src/app/monitor/components/TemperatureCurve.vue`
- `frontend-js/src/app/monitor/components/TensionCurve.vue`
- `frontend-js/src/app/monitor/views/temperature/index.vue`
- `frontend-js/src/app/performance/api/performance.js`
- `frontend-js/src/app/performance/locales/en-US.json`
- `frontend-js/src/app/performance/locales/zh-CN.json`
- `frontend-js/src/app/performance/views/list/index.vue`
- `frontend-js/src/app/performance/views/list/performance-presentation.test.mjs`
- `frontend-js/src/components/BusinessDataSourceSelect.vue`
- `frontend-js/src/locales/en-US/common.json`
- `frontend-js/src/locales/zh-CN/common.json`
- `frontend-js/src/utils/businessDataSource.mjs`
- `frontend-js/src/utils/businessDataSource.test.mjs`

## 资源和交接

本任务资源：`/private/tmp/arch-be006-r1-dev/`各公开失败/成功副本、guard/payload/commands/logs、offline SQL、build/dist、pytest/pycache/uv-cache与最终证据；编排脚本为`/private/tmp/be006-*.py`。
没有本任务listener、后台服务、DB/Docker/浏览器tab、分支或worktree待关闭；所有DEV命令已结束。Root起点目录及其他任务资源不归本角色，不清理。
保留非秘密源码/diff/原失败/成功证据供fresh Verification；终态后由主协调者盘点回收。

**Development -> Root -> fresh-context QA / Verification：ARCH-BE-006 r1 A、developer_handoff。** 消费同一批准spec、本tasks、当前working tree、分profile日志/精确输入hash/diff及限制，独立判断A并记录checklist。
B具体运行未获批准/未执行，整体不能qa_passed或owner_accepted。Development不写spec/checklist，不作QA verdict或Owner最终验收；contract_only不代表平台ACL/强制路由。


# QA1失败后的r1 Development返工（2026-10-16）

已完整读取QA1 checklist SHA`d9e8bf0afca615e29bc46ff3ec0a327365d8a9bac37ff3ed2fe0b5061d4e18b6`、独立证据manifest SHA`f651969e53f0b0308c036328e7d05d84f53076a3d4a42518c2202a79565e361d`及两实际Service/CRUD时序payload/report。
QA1明确qa_failed，F-001/F-002 open；上方首次handoff及125/完整套件历史不表示当前A通过。本Development不改QA记录、不自行关闭finding。

返工起点有限文件快照与hash在`/private/tmp/arch-be006-r1-dev/rework-1/entry/`、`entry-files.json`；原DEV目录handoff/delta/source-map/evidence及QA1目录原样保留，不覆写。
Root观察到其他AW任务spec并发变化，该文件不归本任务，不读取/恢复/修改。仍只写原r1实现allowlist与本tasks；数据库（含SQLite）、任何Docker/真实env/网络安装/listener/浏览器/PLC/Projection/Git写继续禁止。

修复选择：生产观察初查receipt未见后结束只读事务，再取得设备state锁，令历史事件的一致性读视图在锁取得后创建，不改engine/session隔离级别，也不对缺失receipt新增locking/gap锁。
equipment两stream、performance四stream与monitor曲线遇业务拒绝后先rollback，再在新事务普通读取当前已提交投递；异内容优先sample_id_conflict，同内容duplicate返回原稳定结果，无receipt保持原业务拒绝。额外恢复有界为一次，不重新应用业务，不把未知提交重写成成功。
必要回归与真实命令结果在完成后追加；所有模拟仍不等于MySQL B证明。


## Rework-1实施、DEV self-check与新交接

精确Revision仍为**ARCH-BE-006 r1**，spec SHA不变，working tree HEAD仍为`f85bea8bbf36b491968c3dc9a839518a1ed434a8`；无Git写。
返工只改三份Service、两份新合同测试及本tasks（共6文件）：

- `backend/app/equipment/services/async_drive_sample.py`：共用drive/production_parameters拒绝后投递恢复。
- `backend/app/performance/services/async_production_observation.py`：观察初查miss结束只读事务，水位锁后首个历史一致性读；四stream共用拒绝恢复。
- `backend/app/monitor/services/async_process_curve_sample.py`：曲线拒绝恢复。
- `backend/tests/test_mapping_service.py`：锁等待、state首次插入1062、历史原id/同刻冲突、7 stream投递优先级、恢复失败/同内容原id、初始rollback失败回归。既有人工0生命周期替身先commit模拟已完成人工事务，并在rollback后重新获取替身当前行，原断言保留。
- `backend/tests/test_mapping_api.py`：未绑定SQLAlchemy Session的真实identity-map/User失效状态与真实ASGI production响应。
- 本`tasks.md`：保留首次交接、QA1失败，并记录本次返工。

没有改CRUD锁查询、Model、migration、全局engine/session隔离、认证合同、前端、稳定README或CODE_INDEX；既有文件职责/结构未变。初始生产只读rollback发生于业务写之前；认证User因此失效，API已在调用前取出actor整数，后续Service/日志仅使用该整数、重新查询的业务对象和结果字典。无业务ORM对象跨初始rollback读取；拒绝恢复只访问新事务查询的receipt并在commit前复制结果。没有缺失receipt的locking SELECT/gap锁，也没有新增锁顺序。

恢复查询限一次：无已提交receipt则保持原业务拒绝；异指纹409 sample_id_conflict；同指纹duplicate返回稳定原recordId，业务不重做。系统/数据库失败不进入成功恢复；重读系统500、DBAPI503、未知commit503，均rollback且不返回成功。初始只读rollback失败维持503，不继续业务或重读为成功。

| 实际命令/输入 | DEV真实结果 |
| --- | --- |
| `python3 /private/tmp/arch-be006-r1-dev/rework-1/run.py focused-first /private/tmp/be006-final-focused.py` | exit0；compileall成功；149 passed/7.35s，早期候选。 |
| `python3 /private/tmp/arch-be006-r1-dev/rework-1/run.py focused-final /private/tmp/be006-final-focused.py` | **exit0；全隔离backend compileall成功；150 passed/6.95s**，最终三Service+两测试源码。底层`uv run --offline --frozen --no-sync python -c <guard+payload>`；7个新合同test文件完整执行。150含原125与本轮25例，包含149，不相加。 |
| `python3 /private/tmp/arch-be006-r1-dev/rework-1/run.py sql-traces /private/tmp/arch-be006-r1-dev/rework-1/sql-traces-source.py` | exit1；独立证据payload未导入完整Model Registry，ORM关系Plan未解析。失败日志/payload保留；没有数据库连接或项目源码修改。 |
| `python3 /private/tmp/arch-be006-r1-dev/rework-1/run.py sql-traces-final /private/tmp/arch-be006-r1-dev/rework-1/sql-traces-source.py` | exit0；补用现有`import_model_packages`后，6组真实Service+CRUD MySQL编译SQL和合成RR时序输出`sql-traces.json`；4组生产同内容/异内容×state首次竞争、2组equipment投递冲突，结果断言通过。不是实库并发证据。 |
| `python3 /private/tmp/arch-be006-r1-dev/rework-1/prepare-evidence.py`、`git diff --check` | exit0；原DEV四主证据/原tasks与QA1 manifest hash保持；无guard拒绝事件；前端221个公开文件与QA1输入及原DEV输入完全相同，未重跑前端构建。 |

149/150均在公开源码副本与合成配置运行，沿用锁定uv/已有venv，无安装。guard阻断全DBAPI（含SQLite）、Engine连接、socket connect/bind/listen，前置嵌套python子进程并UV_OFFLINE；audit拒绝真实env。User identity-map测试仅`Session()`无bind，不创建engine、不执行SQL、不连接任何数据库。实际SQL痕迹来自compile及合成execute，不是MySQL运行。

新不可变输入：`/private/tmp/arch-be006-r1-dev/rework-1/source-map.json` SHA **b15027fe4ca3753dc2e4bbbe8d19e7134035cce390f8c3118a1c8424a2ff8792**（742公开backend/frontend文件）；已执行源码副本`focused-final/`。返工delta/patch按`entry/`逐字对比，含本tasks；`handoff-source/`固定同一完整公开输入和本tasks；`evidence-sha256.json`及`handoff.json`记录各输入、命令、日志、报告、delta/patch/hash。原DEV handoff/delta/source-map/evidence未覆写，原QA1 checklist/证据保持，QA1失败仍有效历史。

本轮按Root指示不重复历史483、当前完整no_db或未变前端构建。原DEV552 pass/4 frozen fail与QA1完整604 pass/4 frozen fail/30 deselect/exit1真实结果保持，不宣称当前完整套件全绿；原4冻结断言未改/skip/xfail。本轮150仅为修改相关集中DEV自检；未变前端沿用QA1 23routes/9groups、46+10和build成功及其原manifest，不将旧通过冒称本轮重跑。

B入口、migration与MySQL真实反射/旧值/约束/NULL/并发/回退、真实浏览器均未执行且仍待另批。RR时序合成证明需要后续获准B再确认真实MySQL行为。Development仅提交修复和自检证据；F-001/F-002是否关闭与A结论由新的fresh Verification判断，不改QA记录或授予Owner验收。

资源：新增`/private/tmp/arch-be006-r1-dev/rework-1/`公开entry/执行副本/guard/payload/log/SQL trace/pycache/uv-cache与新交接证据；无新listener、后台进程、DB/Docker/浏览器tab、分支或worktree。全部命令已结束，保留非秘密证据供独立复验，清理由Root统一盘点。**完成后停止源码/tasks写入，交Root启动fresh Verification。**


# B具体批准后的Development执行（2026-10-16）

Human Owner明确原话：“批准 B 两轮验证及专用资源清理”。具体批准对象`/private/tmp/arch-be006-r1-proof-2nndlnnf/approved-operation-proposal.md` SHA256 `665c5ef2dc9fcfcf81e0e5d2a1449a6f0b0516ef28f671f622b11eb4dbb6d129`，收据同目录`authorization.json`。原r1 spec SHA保持，A QA2 checklist SHA`dc1bbf1b0da119d5693ac434f2fc1501db77a2a248c16d47c9cd93056bf2a583`；A finding由QA2在source/no_db范围关闭，真实B仍需执行，不改既有失败历史。

Root拥有专用Docker资源/secret/运行准备与清理；Development只拥有既有allowlist测试/必要修复/tasks及本轮DEV证据。仅新dev实例127.0.0.1:33076的arch_be006_r1_empty/upgrade/rollback三个专用初始空库、非root账号；be006_unused_primary不可连接，任何既有DB/SQLite/其他endpoint禁止。Root ready前不连接。密码/JWT仅0600私有配置读取后进程注入，不打印/写公共日志/argv/源码；真实env、网络安装、其他listener、PLC/Projection、Git写仍禁止。

执行顺序：补入口及纯编译→收到ready后按empty/upgrade/rollback实际迁移/反射/旧行保护→真实JWT/API/独立Session的8类读写、7stream并发/故障/权限/父子/人工0→专用API18066/前端15176五页CUA闭环→精确公开handoff。失败保留原日志；污染schema需Root核归属重建，本角色不DROP或切共享DB。Development正式handoff后Root清理dev，再创建全新qa卷/secret/instance交新的fresh Verification。当前尚未执行任何B数据库/浏览器命令。


B进行记录（2026-10-17）：Root已给dev READY，实例容器ID `9d0a71fe8e237efaf46c195283486c2c8fee7b541a421f85f35eef916edb5276`，MySQL8.4.6、be006_dev、RR、SYSTEM、三库全空；资源记录归Root `dev/resource-record.json`及`target-preflight.json`。Root最初internal network未发布端口的资源失败/专用重建记录独立归Root，不算应用验证。私有配置读取后仅process注入；公开driver `/private/tmp/arch-be006-r1-dev/B-development/run-mysql.py`。

- 独立compile/collect：exit0，1 collected，无DB；后续扩展AST通过。
- empty-1 exit1：私有进程配置遗漏公开必填API_V1_PREFIX，第一次连接前Settings拒绝；driver显式补合成`/api/v1`，不改真实env/Root私有配置。
- empty-2 exit1：默认沙箱拒绝loopback连接，OS Operation not permitted/MySQL2003。按既有B批准对精确guarded driver require_escalated，自动审查允许，无重复Owner确认。
- empty-3 exit1：实际base→f6在equipment_drive DATETIME(3)列默认now()被MySQL1067拒绝；这是实现缺陷，日志和`migration-commands.jsonl`保留。原allowlist f6/两设备Model改为同DB时间默认CURRENT_TIMESTAMP(3)，downgrade恢复秒now()；旧五migration未动。部分DDL已发生，已请求Root仅重建arch_be006_r1_empty，本角色不DROP/不改其他schema。
- ddl-default-focused exit1：149 pass/2 fail；BE006自有Recorder未反映server_default，以及新编译断言缺literal_binds。只补BE006 Recorder/断言，原冻结断言保持；定向复验结果后续记录。

全部输出先捕获再脱敏，命令argv不含secret；SQLAlchemy/DBAPI/socket guard只允许精确测试schema/user/127.0.0.1:33076，拒绝primary/root/SQLite/外网/额外listener/真实env，嵌套Alembic继承sitecustomize。所有失败证据保留，未转写成通过。


B迁移/反射进展：PM经Root确认fsp3默认修复属于r1技术适配，无r2；未来省略timestamp时DB默认生成值可能含毫秒，旧行/数值default/旧五migration仍保持，downgrade在无损检查后恢复秒默认。ddl-default-focused-2 compile/151 pass/exit0。Root多次只核归属重建empty，upgrade/rollback仍全空，各timestamp reset收据保留，不覆盖原失败。

- empty-4：实际base→f6成功，反射CHECK比较未折叠MySQL的冗余IS [NOT] NULL原子括号，测试失败/exit1，业务行0。只修测试精确原子归一化，不删除AND/OR分组或约束断言。
- empty-5：实际base→f6成功，反射默认比较误对旧str默认调用compile，测试失败/exit1，业务行0。保留str，仅SQL表达式按MySQL literal编译。
- empty-reflect-1：同专用f6目标**只读完整64表**列类型/null/default/fsp/PK/FK actions/unique/check/index比较成功exit0，schema-reflection.json保留；无业务/DDL写入。Root随后只重建empty。
- empty-6：base→f6、完整64反射、独立Session首次state竞争（RR 1213→503重试后updated/duplicate，唯一state）及初步八类POST/GET/人工0真实通过；prepared drive四请求竞争出现500，整场景exit1，不能宣称empty通过。现场保留用于有界诊断。
- empty-race-diagnostic：四独立请求实际3个1213 OperationalError正确503、1个200，诊断命令exit0仅说明探针执行，不能解释原500或宣称业务通过。记录异常type/errno/栈位置，无token/SQL参数/DSN。
- empty-refresh-diagnostic：确定性barrier“B receipt普通读完成→A提交新业务行→B锁读该新行→refresh”在drive与production_parameters均稳定500，栈InvalidRequestError落在receive_partial的普通refresh。B旧RR视图无法看见已锁current read所见的晚提交行。这是本轮实库发现的新实现缺陷，A模拟不能替代它。
- 原allowlist最小修复：只给共用`db.refresh(record)`加`with_for_update=True`，沿用已锁业务行的current read，同锁顺序、不改全局隔离/不锁缺失receipt；monitor只refresh自己新增行，不存在同型已锁重复分支，过程/观察无该refresh。empty-refresh-fixed同barrier两stream均200 duplicate原id、异常列表空，命令exit0，原500报告保留。
- refresh-current-focused compile/153 pass/exit0；refresh-sql-focused compile/**155 pass/exit0**。155包含原150+默认精度1+refresh时序2+真正AsyncSession ORM refresh SQL构造2；实际无bind Session在execute前截获`SELECT ... id ... FOR UPDATE`，不创建engine/连接，无旧冻结断言变化。永久B入口也追加两stream同barrier及0/NULL读回。

新B证据均在`/private/tmp/arch-be006-r1-dev/B-development/`分label公开副本/脱敏日志/命令及JSON中，原A交接与QA1/QA2不覆盖。当前正请求Root再次仅重建empty后运行完整矩阵；尚未形成B正式handoff，尚无整体实库/浏览器通过结论。


B最新进展（2026-10-17）：empty-7 exit1为测试legacy人工Create缺旧必填planId/grade/weight；已只在legacy fixture增加合成Plan（捕获原60行前）并用有效DTO，不放宽原Schema。empty-8 exit1为空scope测试override的lambda默认闭包参数被FastAPI当query解析，已改真正零参closure；empty-auth-fixed在同受控schema真实JWT/角色/独立read-ingest/空与跨scope/disabled全部通过exit0，逐行snapshot不变。未来父id fixture只读专用库AUTO_INCREMENT，不以max+1猜测并发保留id。两次整场景失败和局部32 notes保留，不累计成通过。

**empty-9完整场景：1 passed/36.40s/exit0。** 真实base→f6、64反射、首次state竞争、八类API/DB完整字段与0/NULL、全部投递/业务冲突/原子补缺、7stream×4首次独立Session barrier、refresh旧RR视图回归、原F-001两分支/F-002两stream、生产父子/晚到/状态/人工0两提交顺序/原PUT权限/DELETE、8类79个真实事务/DEBUG脱敏故障点、JWT/scope/disabled、unique/FK及业务coil/zone大小写、energy两表/三API保护、八旧sync业务Service直接调用与caller业务+cursor+audit原子rollback/commit、全旧行保护、最终HTTP数据拒绝downgrade全部执行完成。旧sync是合成facts直接业务调用，不运行Projection runner/PLC/collector。

empty-9有168条完成note，尚不代表其他两个scenario或页面通过。同库补证identity/check独立命令：首次测试LIKE键选择误包含另一业务`-case` fixture，exit1，未写；第二次实际CHECK3819由driver映射OperationalError而非IntegrityError，测试捕获类型过窄exit1、拒绝行未提交。改精确fixture键regex与只接受MySQL3819（不宽泛吞DB错误）后，empty-identity-checks-3 exit0：8类Case/case实际各2receipt、3新receipt uppercase stream CHECK确实拒绝，整个业务snapshot前后不变。最新独立入口已包含该补证，upgrade/rollback完整使用最新输入；应用源码与empty-9一致，区别仅测试fixture/补证，源hash按label分别记录。

新稳定backend README pair已窄修fsp3默认说明。当前upgrade-1正执行e4合成旧行→f6/53签名保护/完整矩阵，rollback未连接。UI资源仍未启动；CUA仅只读能力初始化，无网络拦截/延迟API，已向Root提出精确GET受控transport故障/barrier夹具；成功页面字段必须仍来自真实API/DB，故障夹具不能作为成功数据证据。登录准备实际执行者/秘密通道待Root协调，私有密码不会写入工具文本。


B三场景DEV数据库执行完成：upgrade-1 `1 passed/39.64s/exit0`；rollback-1 `1 passed/50.64s/exit0`，均为最新独立入口（含身份/CHECK补证）和全79故障点。upgrade从e4逐原列/PK保护旧60行与53表签名后升f6；rollback另外实际NULL/毫秒拒绝、干净降e4再升f6，然后完整业务矩阵和HTTP数据拒绝降级。三者各自独立schema/输入/日志，不作为独立Verification。

Root已只新增合成UI admin user7，启动仅loopback API18066/Frontend15176；源输入归Root `dev/ui-inputs.json`。DEV CUA创建专用Chrome tab346106632；Root受控同源桥真实auth/login+auth/me建会话，DEV未读取密码/token/桥HTML/localStorage，不计login表单验证。五页闭环进行中；成功读回仍为真实API/MySQL，503与hold/release只由Root受控transport精确注入，不作为成功数据证据。


## B Development最终自检与正式交接（2026-10-17）

精确Revision仍为**ARCH-BE-006 r1**，批准spec SHA保持`58c69b8eac6e3a182e6592c2c048743566100eee6c77307ac2fa885a33265557`，working tree HEAD仍`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，无Git写。B批准及Root ready/reset收据与上文真实失败全部保留。不是QA verdict，不授予Owner验收。

相对A QA2消费的rework-1输入，本Development仅有9份实现/文档文件加本tasks，共10文件增量：

- `backend/app/equipment/models/equipment.py`、唯一f6 migration：两扩精度timestamp使用合法MySQL CURRENT_TIMESTAMP(3)默认；无损降级恢复秒默认，旧五migration字节不变。
- `backend/app/equipment/services/async_drive_sample.py`：共用两equipment stream已锁业务行refresh使用FOR UPDATE current read，修实库RR晚提交行不可见500；不改隔离或缺失receipt锁。
- `backend/tests/test_mapping_service.py`、`test_mapping_compatibility.py`、`test_mapping_migration.py`：最小回归、真实未绑定ORM SQL编译及MySQL默认声明验证。
- `backend/tests_mysql/test_mapping_business_api.py`：独立guard、三scenario完整有界B矩阵与确定性barrier、真实API/Session/DB故障注入、旧行保护和浏览器合成fixture；不消费共享破坏性conftest。
- `backend/README.md`及中文pair：旧行/秒值/数值默认保持，与未来省略timestamp可能含毫秒的精确默认变化说明。
- 本tasks。既有CODE_INDEX职责/结构未变，hash仍`9df31c49fc27324f3d8b64925f3856e36a932d88fd081abed1f700811bcbb79a`。六索引由Root维护，其他AW任务变化不归本Development、不恢复。

| 命令与精确输入 | 实际DEV结果 |
| --- | --- |
| `uv run --offline --frozen --no-sync python -c <commands.jsonl逐字argv code>`；cwd=.../refresh-sql-focused/backend，完整code另存refresh-sql-focused-payload.py | 全DB/socket/真实env硬阻断，compileall成功，**155 passed/6.73s/exit0**；包含原150及新增5例，和151/153不重复相加。 |
| `python3 .../B-development/run-mysql.py empty-9 empty` | 专用empty从base直达f6，**1 passed/36.40s/exit0**；168完成note，79真实故障点与28首次竞争等；最新身份/CHECK11项以同库empty-identity-checks-3独立exit0补证，应用源码相同。 |
| `python3 .../B-development/run-mysql.py upgrade-1 upgrade` | 初始空upgrade→e4合成旧行→f6/旧60逐原列PK保护/53签名保护及完整矩阵，**1 passed/39.64s/exit0**；179note，包含上述11项，79故障点不跨场景累计成新种类。 |
| `python3 .../B-development/run-mysql.py rollback-1 rollback` | 初始空rollback→e4旧行→f6，NULL/毫秒拒绝降级且数据保持、干净降e4/再升f6、完整业务及HTTP数据拒绝降级，**1 passed/50.64s/exit0**；179note。 |
| `python3 .../B-development/source-run.py final-b-compile-collect .../compile-collect-source.py` | 最新B入口compile与独立`--noconftest --collect-only`，1 collected/exit0，无DB。 |
| `git diff --check` | exit0。742公开backend/frontend输入与实际upgrade/rollback副本一致；前端221文件与A/QA1输入一致，未无故重复build/旧483。 |

以上实际B runner子命令均`uv run --offline --frozen --no-sync python -m pytest --noconftest -q tests_mysql/test_mapping_business_api.py`；逐label argv/cwd/源SHA/退出码/总耗时记录`mysql-commands.jsonl`，pytest耗时与进程总耗时不同，均保留。require_escalated只用于已获准精确loopbackdriver，默认沙箱失败原样保留。无安装、无依赖/锁修改、无真实env读取，无SQLite/外网/额外listener。三库实际DATABASE/VERSION/CURRENT_USER/RR ACK与只准schema/socket/DBAPI/嵌套Alembic guards均生效，无guard拒绝事件；Root独占所有Docker/重建/secret。

真实矩阵由`database-summary.json`及三场景`business-proof.json`逐项索引：八类指定GET对DB完整字段、FLOAT/Numeric/0/NULL、七stream28首次独立Session barrier、F-001 t1/t2两分支及F-002两equipment分支、设备state首次竞争/1213→503同键恢复、人工0两提交顺序、生产生命周期/父子/晚到、8类79个insert/update/receipt/state/flush/commit/dependency/rollback/close/日志故障、真实JWT/roles/read-ingest/scopes/disabled、64完整反射/unique/FK/二进制大小写/CHECK、能源保护与八旧sync业务Service caller业务+cursor+audit同事务。旧sync仅直接调用合成facts业务，不启动Projection runner/PLC。

五页实际CUA：温控、传动、生产参数、实绩列表+同父31的温度/张力/速度tabs、monitor曲线均选择外部设备并看见本轮fixture同记录数据；所有完整原值另有GET↔DB证据，旧页面只显示其原有字段/精度，不虚称为新增所有内部字段列。温控与参数/monitor URL reload、浏览器返回实绩、同source/device分页、monitor日期17→无数据18→17、四曲线类型均实际操作。每页真实跨scope403后空表/缺测，无旧99回退/伪零；空设备提示明确。Root受控transport的503错误态实际可见，随后hold在清设备和切legacy后才放行真实API200，释放后DOM仍legacy tv99/km0；原第一次错过503视觉窗口的事件仅历史，不计视觉通过。

中文深色宽屏及英文浅色390x844下五页来源/设备/必要控件与过程tabs实际可用；窄屏正常收起现有侧栏、表格使用横向滚动，未扩范围重做布局。语言/主题恢复中文深色，viewport reset。CUA实际截图仅emit于对话，工具无已文档化磁盘保存接口，不编造PNG/hash；`ui-evidence/browser-observations.json`如实记录动作/DOM观察及限制，`events.jsonl`为Root无header/body/token的实际GET/夹具事件副本。

登录由Root0600 secret服务器内真实auth/login+auth/me会话桥准备；Development未读取秘密/桥HTML/localStorage，不计login表单验证。收尾Development实际重开同15176 origin专用tab→真实用户菜单退出→确认→01:09:16 /login与退出成功DOM→close；两个自建tab346106632/346106636都关闭，不碰其他用户tab。未读/打印token/userInfo值。

不可变交接目录`/private/tmp/arch-be006-r1-dev/B-development/handoff/`固定742公开输入及spec/tasks/CODE_INDEX、相对rework-1的10文件delta/patch、各失败成功命令/日志/报告的hash manifest与handoff.json。实际测试/UI固定source-map SHA`ef41fb7b326720c99d041478a0fc39c0705ad773c4c52d5b89029eaf2c8ce199`；browser-rows SHA`162a8a1dd009ff5438e23eea00110c99421033b1645532644068b0f7f8db6b19`。最终tasks/patch/evidence/handoff hash以handoff.json和Root收据为准，不在本文件制造自引用hash。

原A handoff/rework-1/QA1失败/QA2 source-only、旧冻结483及当前4冻结失败均原样保留；本轮B不改变冻结断言，不宣称完整当前no_db全绿，也不把DEV输出当独立B QA。前端未变，沿用QA1 23routes/9groups、46+10及build证据和221逐hash，未声称本轮重跑。

资源：DEV无运行测试命令/浏览器tab/分支/worktree；公开`B-development/`各副本、脱敏日志、guards/payload、证据保留供fresh QA。专用API18066/Frontend15176/MySQL33076/DEV容器卷网络、Root0600配置仍由Root按已批准清单停止与清理，本角色不Docker/DROP。**本Development正式developer_handoff，停止源码/tasks写入；Root清理DEV后，以全新QA实例/卷/secret/空schema启动fresh Verification。** 整体非qa_passed/owner_accepted，最终验收由Human Owner另行决定。

交接工件工具第一次exit1：有限allowlist含未创建的可选mapping_sample_out.py槽位，helper错误要求前后均存在。没有应用/数据库动作；失败部分目录保留handoff-prepare-failed-1。helper仅对前后都不存在路径跳过（不跳测试/不忽略差异）后exit0，确认实际10文件delta与全部输入一致；第一候选handoff-candidate-1保留，最终handoff单独固定，不覆写。最终工具git diff检查/本任务与README相对文档链接检查exit0。
