Task ID: ARCH-BE-009
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r1 B Development -> fresh Verification；专用 MySQL 8.4.6 真实矩阵/7文件修复已冻结，A/QA1/QA2历史保留；QA及Owner最终验收pending

# A源码实施与Developer自检

## 批准、交付树与角色

Human Owner于2026-11-04精确批准r1的A源码/no-DB阶段，原话及原稿SHA见spec第15节。当前spec SHA-256为`26121323384f2b8fd590921f53c477d759b564cf5214078c05834496a4884f48`，获批原稿SHA为`157932dfd6432b972ed73c327ba47bffd4b7c43f32c6e68f772c5cbef458eb86`。Development没有修改spec或创建checklist。

实际交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。没有创建commit/branch/worktree，没有Git写入。联合entry基线由主协调保管于`/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd/entry-manifest.json`和before；本任务不覆盖既有脏树或BE010编辑。

已读取根AGENTS、README/PLAN双语，backend最近README/PLAN、app README双语、development.toml、canonical workflow和完整owner_approved spec。实际使用backend-arch及RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING/DATA_GOVERNANCE、backend-script-tooling、aiis BLUEPRINT/CONTRACTS、code-document-indexer；收尾另用project-governance核对metadata/文档归属，不运行其初始化或全仓重写。没有UI、Worker、Rust、Tauri或PLC实现，不加载其专项。

## 实施顺序与范围

| 步骤/规格 | 实际结果 |
| --- | --- |
| R01–R05/AC01–02 | 新建独立plc_facts普通模块和三路typed输入输出。局部严格UTF-8/Decimal JSON、重复键/深度/字节上限、原v2/manifest/reads/context关联、值矩阵、固定贪心片、完整expected覆盖；原文及多域SHA分开。 |
| R06–R07/AC03–05/11 | 真正async Service/CRUD使用全局单例NOWAIT门闩；同批/片/cycle证明优先、全批终结拒绝、持久父token SHA与成员子集、真实commit后回执、unknown不冒称回滚。逐点sourceSeq/sourceEpoch，bad替换good，旧来源raw-only，来源/定义采用CAS及latest撤销规则。 |
| R08/AC09 | 七表Model与唯一0a2接f6迁移源码。完整VARBINARY键、BINARY摘要、LONGBLOB原文/投影、DATETIME(6)+ns、命名约束/索引；upgrade无seed/DML，downgrade七表任何非空即拒绝。0a2/71、1b3/75有限profile与F7、schema-only再核验，不调用registry私有helper。 |
| R09/AC06 | 同snapshot持久H及feed，发布位置(serial,ordinal)；changes扫描/空页/预算/显式tail，range冻结H/observedAt半开过滤及原文资格，latest逐点expiry/30秒binding分页；过滤摘要与source/content SHA分开。游标绑定epoch/filter/TTL/MAC/floor，空feed不倒退。 |
| R10–R11/AC07–08 | 上海9位时间与自然月截止，原payload最早成员保守到期、latest逐点到期、120天proof不续期；读时expiry guard。一次性CLI裸帮助先于settings/DB；显式status/adopt/cleanup及plan/apply、目标/确认、CAS、配额/预算、有限前缀proof清理、失败/降级JSON Lines。无线程/调度器/请求清表。 |
| R12–R13/AC10–12 | 九个整文件no_db、冻结旧源码指纹、正常composition与模块preflight、机器合同/双语入口/结构索引、独立B入口源码和本交接。B仅有源码，不执行。 |

独占新增57文件，完整逐文件SHA见本文末清单。另在11个已批准共享文件仅追加本能力入口：三份backend .env example、module_admission_fixtures.py、contracts/backend/app README双语及CODE_INDEX。共享路径完成后明确释放给BE010；此后由BE010合并其段落，本任务不再写共享路径。其当前完整文件hash包含并行归属，不能把对方段落算作本任务修改。再加本tasks，本任务触达69个批准路径。

公开example只追加四个默认关闭/空key与逐条英文说明；没有读取真实.env，也不修改global settings/engine/session/response/认证。新manifest为literal v1，order36、无requires/model_requires/exports/permissions。旧monitor/CA/Projection/业务API、DAA/SMA/DS/FF及六条旧迁移保持边界；BE010/common.integration由同伴唯一维护。

## 固定合同与schema口径

- `contractVersion=plc-facts/v1`、`sourceProfile=daa-local/v2`、`digestProfile=pf-json/v1`、cursor=`pf-cursor/v1`。
- 三路正常composition和OpenAPI注册，错误403/409/410/413/415/422/429/503/500均为本地typed failure。独立stdlib生成原文/规范字节/固定摘要和两PLC同DB、单PLC两DB两组、固定多片/仅首片向量；不以被测canonical生成expected。
- 原批相同内容稳定恢复；终结拒绝原token/绑定内容在有限proof内持久恢复，换游标HMAC key后父凭据仍按持久SHA验证。scope是数据准入，不是调用者认证。
- 七表语义F7=`sha256:28edcba4298a164389965c6f7d05b29e8e6494a1ace48d141d83c5edbd1d8e2e`。A只编译/核源码，没有任何live F7/时区/迁移证明。
- BE009独立B显式到`0a2c4e6f8b10`/71应用表，排除alembic_version；完整源码metadata75=71+BE010 pending4。当前联合源码唯一head是1b3→0a2→f6，A只静态解析。1b3运行及F7再核验由BE010独立后续gate承担。

## 真实检查环境与命令

使用backend现有uv环境（Python3.13.3），无sync/install/依赖修改。`check.py`在任何项目settings/database导入前，填入合成process env，禁用DotEnvSettingsSource读取；拒绝socket connect/connect_ex/bind/listen、create_connection、SQLite connect、pymysql/aiomysql/psycopg2连接及SQLAlchemy Engine/AsyncEngine连接。ASGI为进程内transport，无HTTP listener。编译cache、pytest basetemp、日志均在本任务/private/tmp目录。测试仅复制明确文件以隔离共享清库conftest，产品源码始终直接从交付树导入；副本测试hash等于正式源。

以下`GUARD`完整前缀均为：

```text
cwd=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend
UV_CACHE_DIR=/private/tmp/arch-be009-r1-a-dev/uv-cache
PYTHONPYCACHEPREFIX=/private/tmp/arch-be009-r1-a-dev/pycache
uv run --offline --frozen --no-sync python /private/tmp/arch-be009-r1-a-dev/check.py
```

| 完整后续argv/检查 | 真实结果 |
| --- | --- |
| GUARD `/private/tmp/arch-be009-r1-a-dev/run_tests.py` | exit0；最终129 passed。pytest实际argv：`-q --tb=short -p no:cacheprovider -o 'markers=no_db: no database access' -c /dev/null --confcutdir=/private/tmp/arch-be009-r1-a-dev/tests --basetemp=/private/tmp/arch-be009-r1-a-dev/pytest-temp -m no_db /private/tmp/arch-be009-r1-a-dev/tests`。只含本任务九整文件。 |
| GUARD `/private/tmp/arch-be009-r1-a-dev/regression.py` | exit0；44 passed/9 deselected。明确六文件：test_module_registry、test_module_contract、test_response_contract、test_projection_runtime、test_control_agent_authorization、test_role_api_authorization。仍用-m no_db与独立confcutdir/basetemp；DB测试未选择。 |
| GUARD `app/module_preflight.py --check-only --project-root /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend` | exit0；全部manifest只读预检，plc_facts explicit/active。 |
| GUARD `/private/tmp/arch-be009-r1-a-dev/final_surface.py` | exit0；内部check_source、create_app(testing=True)、完整metadata75、七表CreateTable/CreateIndex MySQL静态编译、迁移源码AST唯一接链、targeted compileall、typed OpenAPI逐对象等于发布快照、24本地链接/3 JSON解析全部通过。没有运行Alembic命令。 |
| GUARD `/private/tmp/arch-be009-r1-a-dev/generate.py` | exit0；生成本三路OpenAPI/2020-12 schema/独立向量。Number以typed WithJsonSchema冻结为number；query schema另收于$defs。原固定请求content/cycle/request/definition/set向量命中spec预期。 |
| `git diff --check -- <本任务独占批准路径与tasks>`及stdlib逐行UTF-8/空白检查 | exit0；未跟踪新文件也另查，不能仅依赖git diff。 |

开发中保留真实失败：首轮helper缺API_V1_PREFIX而导入exit1，补合成env后通过；一次uv从repo根运行未选择backend环境，缺pydantic_settings而exit1，没有安装依赖，改cwd；首轮测试ROOT多上一级导致大量FileNotFound，修helper后124 passed，再扩覆盖至127/129。模块准入曾被literal error_codes、registry/base私有import和动态__import__阻挡；都在本owner修正，没有改Core exports/checker或削旧断言。早期-c /dev/null产生未知no_db marker/cache warning，最终argv声明marker并关闭pytest cache。shell启动有/bin/ps Operation not permitted环境提示，命令实际exit码按表记录。

这些均为DEV self-check，不是QA verdict。没有运行全局pytest、共享清库conftest、SQLite、DBAPI连接探测、迁移、Docker、现场/网络、HTTP listener、真实数据操作或B入口。

## A范围自检对照与限制

| AC | Development源码自检依据 | B/外部限制 |
| --- | --- | --- |
| AC01–02 | typed三路与失败闭包、独立摘要/Unicode键/Decimal/严格parser/值矩阵/完整合成材料与固定片测试；OpenAPI与源码逐对象一致。 | 未证明真实MySQL BLOB/大小写/精度及真实HTTP→七表。 |
| AC03–04 | 真Service替身create/replay/conflict/reliable rejection、commit异常unknown、commit→close→send、错误路径close、父token换key仍可派生、首片不假complete。 | 替身不证明真实commit/rollback/并发或网络丢包；B须独立Session验证。 |
| AC05 | 逐点sourceSeq/代次逻辑、bad替换good、真实采用规则替身证明same-generation保留值及generation切换清值/seq1可用。 | 无真实CAS竞争/锁/PLC；匿名可被冒用的风险仍在。 |
| AC06–07 | 串行门闩独立不变量、MAC/filter/epoch/floor/TTL、真实query Service替身fact/original/gap/过滤、自然月/月末/闰年/9位/截止相等。 | 无真实RR snapshot/T1晚commit或宿主TZ证明；不使用raw.id替代发布序。 |
| AC08–09 | CLI裸帮助不加载DB、精确参数、来源CAS/退代/已知profile/F7规则、预算/有限proof前缀代码、七表DDL与Model逐字静态编译一致及七种非空downgrade拒绝。 | MySQL反射F7/计数/持锁100ms/整tick2s/故障恢复/24h清理SLA尚未运行。数据库调用耗时必须由B测量，源码预算不冒充现场性能承诺。 |
| AC10–12 | 六旧migration、monitor realtime及Projection input_resolver固定SHA；相关44 no_db、正常composition/disabled facts routes、模块准入、metadata/JSON/link/compile/diff。 | 旧六migration/旧权限不变的源码证明不等于旧现场CA/Projection/业务运行验收；不重复此前整套220/437/88或真实采集。 |

默认三路关闭/空scope/unadopted/keyless时在DB前拒绝。合格设置仍要已采用schema/时间/source，不是默认503脚手架：真实Service/CRUD/事务/查询/维护路径已实现，但未运行DB。后端provider-ready、Owner最终验收、部署/DAA上传/联调与阶段C均未成立。

## B入口及后续操作提案材料（仅源码/文档，未执行）

B源码为`backend/tests_mysql/test_plc_facts.py`，9项可审阅入口包括真实ingest→latest/history和ASGI status/content-type/body读回、同批并发/身份冲突、真commit后抛丢ACK并恢复、T1门闩阻挡/T2重试/晚观察时间、过期输入可靠拒绝、cleanup/counter、过期游标和外层proof前缀fixture。缺具体目标批准立即skip；受控expiry/proof积压fixture未准备的项明确skip，绝不可把skip当B通过。剩余更细B02–B07场景、两轮隔离资源/时间与故障动作须在另批运行提案中固定，本文不授权操作或声称完整B完成。

后续实际argv形状（目标/凭据均为待Owner具体批准的合成参数，不在A执行）：

```text
cd <approved-isolated-source>/backend
uv run --offline --frozen --no-sync pytest -q --confcutdir=tests_mysql --basetemp=<owned-round-basetemp> tests_mysql/test_plc_facts.py
```

必须显式提供：`PLC_FACTS_B_OPERATION_APPROVAL`、`PLC_FACTS_B_TARGET_ALIAS`、`PLC_FACTS_B_SCHEMA`、`PLC_FACTS_B_EXPECTED_REVISION=0a2c4e6f8b10`、`PLC_FACTS_B_STORAGE_EPOCH`、`PLC_FACTS_B_CONFIRM=RUN:<alias>:<schema>:<epoch>`；合成MYSQL_HOST/PORT/USER/PASSWORD/DATABASE及TESTING、PRIMARY_DATABASE=mysql，生产与测试schema严格隔离。另需`PLC_FACTS_ENABLED=True`、`PLC_FACTS_PLC_IDS_JSON='["plc-demo"]'`、`PLC_FACTS_STORAGE_PROFILE=mysql84_shanghai_v1`、本轮合成64hex cursor key、BACKEND_MOCK_ENABLED=False、PROJECTION_RUNNER_ENABLED=False，全部bootstrap关闭。B入口不选择本机默认服务，不执行create_all/DDL/建库/清库。

外层提案应先固定两个独立可丢弃MySQL8.4.6轮次的alias/schema/账号/端口/volume/生命周期与故障/清理，配置上海+08:00和RR；只使用公开源码副本/合成配置，禁止携入真实dotenv。先保留合成旧64表ID/值/精度hash，显式f6→0a2（绝不用head）；在未采用全空时验证允许downgrade，再重建0a2并用批准CLI adopt synthetic plc-demo/daa-demo/generation-demo/context、expectedBindingRevision=0、seqFrom=1及精确epoch。采用后验证非空downgrade拒绝。入口要求每轮proof/highSerial初始为0。

maintenance参数必须显式alias/schema/expected-schema-revision/expected-storage-epoch/operation-approval/confirmed-by，apply另加工具开关及`--confirm APPLY:<action>:<alias>:<schema>:<epoch>`。物理过期/120天proof/失败重入的外层fixture另批后才可设置`PLC_FACTS_B_CLEANUP_FIXTURE_READY=True`、`PLC_FACTS_B_HISTORICAL_BATCH_FILE`、`PLC_FACTS_B_REMOVED_PREFIX_CURSOR`；这些文件只能含该隔离轮次的合成冻结原批/游标。不得靠改DAA/旧业务日期或真实DB系统时钟制造样例。1b3/75及原F7/epoch/proof不变的schema-only再核验属于BE010后续联合gate，不混入本独立B。

## 资源、交接与写入审计

自有临时目录`/private/tmp/arch-be009-r1-a-dev/`保存guard/generator/surface/test runners、仅9个本任务测试及6个旧回归副本、basetemp、cache/pycache、各轮日志和implementation-manifest；无临时源码工作树、DB、Docker、监听端口、volume或后台服务。另有自有生成helper：`/private/tmp/be009_write.py`、`/private/tmp/be009_schemas.py`、`/private/tmp/be009_models.py`、`/private/tmp/be009_docs.py`。保留至fresh Verification消费/Owner决定后由主协调核对回收。主协调entry/before、PM、BE010证据均不归本DEV清理。

必要结论、命令结果、限制及全部独占文件SHA已持久化于本tasks，不只依赖临时日志。共享文件的纯本任务追加可由entry/before及相应能力段落核对；未写六处索引、spec/checklist、Core/旧模块、BE010/common.integration或其他禁止面。contract_only：任务bundle/串行handoff/diff审计是合同控制，不声称平台ACL或强制路由。

### Developer handoff（正式冻结）

精确revision为ARCH-BE-009 r1 A；正式工作树如上，无commit。独占源码57文件+11共享追加+tasks；所有B运行及外部动作仍未授权。主协调待两DEV联合候选冻结后启动新的fresh-context Verification，消费spec/tasks、entry/before、当前实现、本文hash、guarded复现脚本及真实日志。QA和Owner结论只由其角色后续记录。

### 冻结独占文件SHA-256

Manifest SHA-256: `b79bcee3e4b002e993e862f40a5abacf77180f1177b9df5fd4b880fe40b58382`（`implementation-manifest.json`，同以下57项）。

| 文件 | SHA-256 |
| --- | --- |
| `backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py` | `05d4e2912ec53d17b597c21894bfd32cadea9812a91ce3e7be21c99c77bf84f5` |
| `backend/app/plc_facts/README.md` | `dd440e8af2825504d28a16384594c035b03d14a25d0bf8a995bf7c6c7fda2cf1` |
| `backend/app/plc_facts/README.zh-CN.md` | `d2221d40ed612c08083380926c8e30f224b9cc3aa1db58ca152d691a9c73c440` |
| `backend/app/plc_facts/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/api/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/api/batches.py` | `b08081c5486b3463164b8a8b384d972ce01c57fab56ee90a8ed97ff03ceec524` |
| `backend/app/plc_facts/api/dependencies.py` | `ee80d94d5e65bb8bb2c2c758044fec359057f0a3b02a7458052c592db7fae2a8` |
| `backend/app/plc_facts/api/history.py` | `3ade3187a476859d806d58d52d28e4595bcbd374d479176bee49ca343a4490fe` |
| `backend/app/plc_facts/api/http.py` | `4664f4c6315aa1b0f46f24a8193860558085c12664c1016b1f7efbcf10ee4c27` |
| `backend/app/plc_facts/api/latest.py` | `798f3f88f55d7568f9f9d5742769a333eabe7223069cc5d0c5c204fee0624fd8` |
| `backend/app/plc_facts/api/routes.py` | `b73df8fc9570d8cdfaf33c58dd1ae2bad5452f7c715c51ba69504b144b0379b8` |
| `backend/app/plc_facts/canonical.py` | `c48f0957b65c4348dec4fdfd8d76d9bd29891355b302b4d189b81cad7bbf1cd9` |
| `backend/app/plc_facts/config.py` | `7f498a16a316d94a21cf28dd1572b3c044883910c0e16de2ca0ac79c40374577` |
| `backend/app/plc_facts/crud/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/crud/async_ingest.py` | `2e087d3b5466630e41358c0c24b0b15a7dac4f1aba7721491995ca81a2e131aa` |
| `backend/app/plc_facts/crud/async_query.py` | `86686afb7ef383f9bc702e374b20eced4306b5c8184c0646de00ff3745bb6645` |
| `backend/app/plc_facts/crud/sync_maintenance.py` | `56a8edad06658e1fed9d94026f88de67158d663110ffcfae5d74af9863b9f1b5` |
| `backend/app/plc_facts/cursors.py` | `e1bf72ffb13a32e096418275054222e95a455f46eca1b6e412644f90cbc9f783` |
| `backend/app/plc_facts/error_codes.py` | `8529c74ec787137f508e29fae4c8afcad51bb2ca9d63908fde30edb59b1824ce` |
| `backend/app/plc_facts/manifest.py` | `3a75ce0f0ec93d7a7c19548d964b498a15ae9625977d708fdeed4b255b85fc8a` |
| `backend/app/plc_facts/mocks/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/models/__init__.py` | `d65b53615a322618641d925ef7017e3a785feb264190474a7c7051b452998721` |
| `backend/app/plc_facts/models/facts.py` | `920e89c963190bef00edb6c06d0195a93afa38cbb876c9edc946f3e3c203b89f` |
| `backend/app/plc_facts/models/receipts.py` | `c27e1729f6ef1ee283dedad6c48f8e6f22274a0258034b6ba0d033aa7f220af2` |
| `backend/app/plc_facts/models/state.py` | `05ba33db3c4bbeb4b4a2797cddc456a38aada07baf807fdfd4c073dda4e48580` |
| `backend/app/plc_facts/retention.py` | `f73c302c1196eaeeaf521de73bbd220a9466b8e2666f2aaa51e78fc01d591e9d` |
| `backend/app/plc_facts/schemas/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/schemas/batch_in.py` | `a0a625433a76c9b39a7009a04579ca02f9844c119679ba9a533ff678dbcbc69b` |
| `backend/app/plc_facts/schemas/query.py` | `1689676876f6f5b360ccac23769a56da6a7b3f926bd5f90d0c4af385254671cf` |
| `backend/app/plc_facts/schemas/read_out.py` | `4b8c421e993d9977f652e1f74fd2904837cacbd91a1136cf32c0d082259e2ad9` |
| `backend/app/plc_facts/schemas/receipt_out.py` | `14d37df54acbef48fe55eedc9d26b1c3512a422f9f4bdaac45b304b651979e40` |
| `backend/app/plc_facts/schemas/source.py` | `1c3726df2f8b73761e1b0aff61323ed5452911ab941df3065ae5e35f60f9e639` |
| `backend/app/plc_facts/seeds/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/services/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/services/async_ingest.py` | `91b15e1842847db6612fc83753a9a9fac2caaa44a57c655ee223a12685a9a60f` |
| `backend/app/plc_facts/services/async_query.py` | `7755a9537779afa4ee05615686282de831e0451fc02fe77948479e46d46b383e` |
| `backend/app/plc_facts/services/sync_maintenance.py` | `b137060496eddbf7357491dad6c5debdd25cc5460960981a785e5c745d502a28` |
| `backend/app/plc_facts/source.py` | `ee8c3f0e659d8625c033a72999aba8a2b8228e0673ef255fb728b2bcd3ecc864` |
| `backend/scripts/plc_facts_maintenance/.env.example` | `0566bf0000ca7971b51c57e8619f1ef396c5b6197768d61db7228388f645644f` |
| `backend/scripts/plc_facts_maintenance/README.md` | `93a1dd80d22aeeae9183bfc4c39d64c988145b192813fefe7cd0483cd34fe565` |
| `backend/scripts/plc_facts_maintenance/README.zh-CN.md` | `2779bf3112b4e24f00a386bbed3e15d5cc0bdaca175cb1c549435ba9281bb2a5` |
| `backend/scripts/plc_facts_maintenance/main.py` | `5edbd02e113ac97d648dbe07b790d85f01c7e5ba50cff56b92abbf4538b99e66` |
| `backend/tests/test_plc_facts_api.py` | `6e5846b3411d35f707628a7878ce8e5e5344aa7b62ad5f674eaf9b184f76bed9` |
| `backend/tests/test_plc_facts_compatibility.py` | `a59199a867fffed737f20ed93fb1dcb0fe12532a2531f0ccedacab2667fe1908` |
| `backend/tests/test_plc_facts_contract.py` | `e867628362d40a58b832bfa3313342ab6696604c367f3beda1c464d72f27dd49` |
| `backend/tests/test_plc_facts_cursor.py` | `caff312c0c0e2ef5b5cbf7b704a27aa387382d6c1ac47aa4dc43f0948ff6f6fc` |
| `backend/tests/test_plc_facts_maintenance.py` | `03088f260af627470a6af073a9526ca517dbf54ba1556f2eee86b3b4166cc4c5` |
| `backend/tests/test_plc_facts_migration.py` | `c36a0a892fc8965d3751db2f32bdd55f2134340c135b8670aec4df8f5520499f` |
| `backend/tests/test_plc_facts_ordering.py` | `c03cdafbff4bded33617e5676fe7ef85aa401449ecc924163192d6d158be76fc` |
| `backend/tests/test_plc_facts_retention.py` | `e7569f3aa2f3db5b12f216c877b08d415decfe9d3fc400a08f36ea8455052637` |
| `backend/tests/test_plc_facts_source.py` | `b510216995600761018469e42f94cabb4a9c91c2451708cde91c930618008b30` |
| `backend/tests_mysql/test_plc_facts.py` | `676bb934a5d592f9c24fe2731724c29b81db9f12861d9478f2f39e53d28930ca` |
| `contracts/published/http-api/plc-facts-v1/README.md` | `1c039c4d19ef0637f94fbd0f8d7f8898e02f30d88ff7dcd9172ac09803ecd6c8` |
| `contracts/published/http-api/plc-facts-v1/README.zh-CN.md` | `cd18b24a2302e232e3ee19f2fcf798263430afeb02dd3f5fb484d8a3ad46bfc3` |
| `contracts/published/http-api/plc-facts-v1/openapi.json` | `bec51c468ff64a8d34dbb0a2faab2fda76d2b33769ee5ef066dc81e8bca274ee` |
| `contracts/published/http-api/plc-facts-v1/schema.json` | `60d0e285bebb1c6d24588f4d5f90e7bdd85ed0befdeab9d0b93445a94f45d4b3` |
| `contracts/published/http-api/plc-facts-v1/vectors.json` | `9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782` |

### 自检helper SHA-256

- `check.py`: `18911725840d26fcd696e19e3e4c8003cd721f7d3d2d062ba360a71fc958153a`
- `run_tests.py`: `5a932e3e38714b163a7368b11a873f6aa5a35611977693017b60137eb98bafac`
- `regression.py`: `3fdf44a19982c8a0be8fa1dd217ee1ee56bb6d4d860306282918bd34630f038e`
- `surface.py`: `f1502c0662a0d7983935b623c2eb9a4e743032a94a9df047f16eab7a5378bfc8`
- `final_surface.py`: `4debcb9b87d2c4ae04d32f1accd0c88c13736ada13e703cd5f4ef9fa4dfea072`
- `generate.py`: `4d1dcd4628c2b4fb6b3bffe242a108100c2874cd263d135f2ab8242316b3ffa1`

2026-11-04正式交接：最终A九文件129 passed（tests-handoff-final.log，30.02s），旧相关44 passed/9 deselected，静态surface/OpenAPI/链接/编译退出0；57项SHA及UTF-8/逐行空白复核退出0。以上是Development self-check；等待主协调联合冻结后启动fresh Verification。此后Development停止写入，除非收到明确返工。

## QA1后的Development返工1（2026-11-04）

独立QA1已停写，其checklist SHA为`acf3620e7198e22aabec4f06d4e4f7c1a45a093cac26d188c3e1683535c9a246`，结论`qa_failed`。原57 manifest `b79bcee3…b58382`及tasks `434c5827…4c45e5`和上文自检/交接均为第一候选历史，不能套用到返工候选。

本轮仅修F-QA1-001的三种Cycle候选饥饿（已空原文前缀、多tick清200后停滞、有引用proof前缀）及F-QA1-002的精确REAL边界；不写spec/checklist/共享或BE010表面。先复现独立反例红灯，再补正式回归和修复；新证据归`/private/tmp/arch-be009-r1-a-dev/rework-1/`。继续原A noDB/无网络/不读真实dotenv/不运行B边界。

### 返工1实际修复与新候选

原独立QA六反例先复制到本DEV自有red/运行，真实exit1：6 failed in0.43s；QA证据未改。随后在两个正式测试文件追加回归，产品修复前真实exit1：15 failed、35 passed、76 deselected in0.89s；precision7还会错误拒绝合法近下界，失败均保留。

F-QA1-001：SQL在LIMIT之前统一资格。原值候选为实际正字节且wall+ns精确到期；Cycle的NULL与空BLOB均不占原值窗口。Cycle proof候选为已满120天、三原文零字节且NOT EXISTS任何同instance/cycle的sample receipt引用。status复用同一正字节/到期资格，计数按实际内容减少。Service不再逐行跳过有引用前缀；sample feed仍只删除完整、全部已到期的serial前缀，不放宽TTL/配额/锁/行数/字节/时间预算。

为支持相关NOT EXISTS，SampleReceipt Model及同一0a2迁移同步增加ix_pf_cycle_receipts(instance_id,cycle_id)完整复合索引（VARBINARY合计1024字节）。未新增表/revision，主协调已确认r1原allowlist内本实现；没有SQL/EXPLAIN/反射或迁移执行。

F-QA1-002：REAL先Decimal(v).copy_abs()精确取幅值再比较原十进制上下界；不用受context舍入的abs，不再binary32量化。覆盖正负上下界、恰相等/极小内外差、0/-0、precision7/28/100及strict parser→typed PointFact→canonical精确往返。

新增正式清理回归直接解释真实SQLAlchemy WHERE/ORDER/LIMIT（含coalesce/octet_length/相关NOT EXISTS），不硬编码候选结果。覆盖200个NULL或空BLOB前缀后第201条原文、连续tick清200/1/0行、200个有receipt引用proof前缀后可删proof、有原值proof前缀、部分清空/字节预算/纳秒截止、status与实际blob/proof计数、未到期成员或不足行预算不得部分删serial。确定性时钟只隔离候选算法，不证明DB耗时。原QA有限替身不解释新SQL资格，故绿灯采用正式表达式解释器；QA原脚本/日志保持原状。

### 返工1真实命令

所有项目命令cwd=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend。完整前缀为：

```text
UV_CACHE_DIR=/private/tmp/arch-be009-r1-a-dev/rework-1/uv-cache
PYTHONPYCACHEPREFIX=/private/tmp/arch-be009-r1-a-dev/rework-1/pycache
uv run --offline --frozen --no-sync python /private/tmp/arch-be009-r1-a-dev/rework-1/guard.py
```

R=/private/tmp/arch-be009-r1-a-dev/rework-1。guard是已审阅QA1 guard的DEV自有副本：项目import前清除继承配置、注入合成env、禁止真实dotenv/SQLite文件、所有DBAPI/SQLAlchemy/socket/listen连接。QA1目录没有写入。

| 前缀后的精确argv | 结果 |
| --- | --- |
| R/run_suite.py red，修改产品前 | exit1；6 failed/0.43s，qa-counterexamples-red.log。 |
| R/run_suite.py focused -k 'cleanup or real_limits'，修改产品前 | exit1；15 failed/35 passed/76 deselected/0.89s，formal-regressions-red.log。 |
| 同上，修改产品后 | exit0；50 passed/76 deselected/4.50s，formal-regressions-green.log。 |
| R/run_suite.py focused -k 'test_plc_facts_maintenance or test_plc_facts_source' | exit0；两个完整文件100 passed/34 deselected/10.99s，whole-files-green.log。 |
| R/run_suite.py focused -k 'test_plc_facts_migration or test_plc_facts_contract' | exit0；26 passed/108 deselected/0.65s，static-contract-tests.log；七表Model/迁移MySQL静态DDL与Index一致。 |
| R/surface.py | exit0；完整preflight/正常三路composition/metadata75/pending4/唯一1b3→0a2→f6源码链、七表DDL/Index静态编译、targeted compile、OpenAPI=快照、24链接/3JSON、独立9摘要及>28位canonical字节均一致。 |
| R/record_sql.py | exit0；实际候选/status SELECT静态编译到cleanup-candidates.sql，包含LIMIT前资格和NOT EXISTS；不执行SQL。 |
| stdlib R/audit.py及最终SHA/UTF-8/空白/测试副本核对 | exit0；57数量不变、7改/50不变；原SHA匹配的返工前文本和精确diff保存；spec/checklist及3机器JSON未变。 |

run_suite完整pytest argv为：-q --tb=short -p no:cacheprovider -o asyncio_mode=auto -o 'markers=no_db: prohibits database access' -c /dev/null --confcutdir=R/<suite> --basetemp=R/<suite>-temp -m no_db R/<suite>，再跟表中-k。focused仅五个明确文件（maintenance/source、contract/migration及ordering辅助导入），副本与正式源逐字一致，产品始终直接导入交付树。没有共享conftest或全局pytest/B。

surface是QA1脚本复制到DEV自有目录后，将旧F7固定断言改为新索引检查/本轮F7记录；这是DEV self-check，不冒充独立QA2。未重跑未改动且QA1已独立通过的44旧回归和4双故障HTTP，保留它们历史。

### 返工1当前有效handoff

当前有效候选为本返工1；上文第一候选129项、旧57 manifest及其SHA/F7作为失败候选历史保留，不能当作本轮当前事实。新静态F7为sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed，七表应用71/完整metadata75及版本链不变。旧F7的BE010 tasks:98联合B材料已通知主协调，待其QA冻结结束后由相应owner同步；本DEV不写BE010/共享或QA1历史。

正式树仍为/Users/jason/Desktop/DreamCode/aiis-ics-arch，HEAD8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b，无commit/worktree。本轮仅七个独占文件及tasks改变，没有新增文件。旧57 manifest b79bcee3…b58382、原tasks434c5827…4c45e5、QA1 checklist acf3620e…c9a246保持历史。新manifest及完整57 SHA见下表。

实际MySQL反射/时区/锁耗时/并发/清理预算与24h SLA仍未证明；本轮无DB/SQLite/Docker/Alembic/网络/listener/PLC/DAA/真实dotenv/数据迁移/B。Developer self-check不关闭QA1结论，不授Owner验收或provider-ready。

新57 manifest SHA-256: `4f7b57c21fb512bf2cb8c0eb6a9cb43599a3bd9656b6cff890d0d3a85e9e0776`。

| 本轮改变文件 | 当前SHA-256 |
| --- | --- |
| `backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py` | `657031969cbe50432a4aeaa8cf089bfac653f507b49c556fc058f5a1d2abce51` |
| `backend/app/plc_facts/crud/sync_maintenance.py` | `328597aeaddcec8d443cf7e1e668287365a39087f44afd8ba4e9d5bf92bfcbba` |
| `backend/app/plc_facts/models/receipts.py` | `880e98b0cc2a3440e0c139c47d03369fe5937d79afef85d09e5e8018413deda1` |
| `backend/app/plc_facts/services/sync_maintenance.py` | `e30fec0575217a62e177a5afb3fc89fd5ecf085cc7c99aaabf666774cd6ccd84` |
| `backend/app/plc_facts/source.py` | `a7fd7ef75149e251a47d838fbd57db00c540c7990d1f64f3d9e9a67edc1489d8` |
| `backend/tests/test_plc_facts_maintenance.py` | `c1e12a1c0d9d51a1dc58b8503307436cb13aface52e9f9fd393098aa52aa1b94` |
| `backend/tests/test_plc_facts_source.py` | `f5848c5fe5172590f3d5e1875371a4e578ac21f986af6ad332086a506161e5d0` |

### 返工1完整57文件SHA-256

| 文件 | 当前SHA-256 |
| --- | --- |
| `backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py` | `657031969cbe50432a4aeaa8cf089bfac653f507b49c556fc058f5a1d2abce51` |
| `backend/app/plc_facts/README.md` | `dd440e8af2825504d28a16384594c035b03d14a25d0bf8a995bf7c6c7fda2cf1` |
| `backend/app/plc_facts/README.zh-CN.md` | `d2221d40ed612c08083380926c8e30f224b9cc3aa1db58ca152d691a9c73c440` |
| `backend/app/plc_facts/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/api/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/api/batches.py` | `b08081c5486b3463164b8a8b384d972ce01c57fab56ee90a8ed97ff03ceec524` |
| `backend/app/plc_facts/api/dependencies.py` | `ee80d94d5e65bb8bb2c2c758044fec359057f0a3b02a7458052c592db7fae2a8` |
| `backend/app/plc_facts/api/history.py` | `3ade3187a476859d806d58d52d28e4595bcbd374d479176bee49ca343a4490fe` |
| `backend/app/plc_facts/api/http.py` | `4664f4c6315aa1b0f46f24a8193860558085c12664c1016b1f7efbcf10ee4c27` |
| `backend/app/plc_facts/api/latest.py` | `798f3f88f55d7568f9f9d5742769a333eabe7223069cc5d0c5c204fee0624fd8` |
| `backend/app/plc_facts/api/routes.py` | `b73df8fc9570d8cdfaf33c58dd1ae2bad5452f7c715c51ba69504b144b0379b8` |
| `backend/app/plc_facts/canonical.py` | `c48f0957b65c4348dec4fdfd8d76d9bd29891355b302b4d189b81cad7bbf1cd9` |
| `backend/app/plc_facts/config.py` | `7f498a16a316d94a21cf28dd1572b3c044883910c0e16de2ca0ac79c40374577` |
| `backend/app/plc_facts/crud/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/crud/async_ingest.py` | `2e087d3b5466630e41358c0c24b0b15a7dac4f1aba7721491995ca81a2e131aa` |
| `backend/app/plc_facts/crud/async_query.py` | `86686afb7ef383f9bc702e374b20eced4306b5c8184c0646de00ff3745bb6645` |
| `backend/app/plc_facts/crud/sync_maintenance.py` | `328597aeaddcec8d443cf7e1e668287365a39087f44afd8ba4e9d5bf92bfcbba` |
| `backend/app/plc_facts/cursors.py` | `e1bf72ffb13a32e096418275054222e95a455f46eca1b6e412644f90cbc9f783` |
| `backend/app/plc_facts/error_codes.py` | `8529c74ec787137f508e29fae4c8afcad51bb2ca9d63908fde30edb59b1824ce` |
| `backend/app/plc_facts/manifest.py` | `3a75ce0f0ec93d7a7c19548d964b498a15ae9625977d708fdeed4b255b85fc8a` |
| `backend/app/plc_facts/mocks/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/models/__init__.py` | `d65b53615a322618641d925ef7017e3a785feb264190474a7c7051b452998721` |
| `backend/app/plc_facts/models/facts.py` | `920e89c963190bef00edb6c06d0195a93afa38cbb876c9edc946f3e3c203b89f` |
| `backend/app/plc_facts/models/receipts.py` | `880e98b0cc2a3440e0c139c47d03369fe5937d79afef85d09e5e8018413deda1` |
| `backend/app/plc_facts/models/state.py` | `05ba33db3c4bbeb4b4a2797cddc456a38aada07baf807fdfd4c073dda4e48580` |
| `backend/app/plc_facts/retention.py` | `f73c302c1196eaeeaf521de73bbd220a9466b8e2666f2aaa51e78fc01d591e9d` |
| `backend/app/plc_facts/schemas/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/schemas/batch_in.py` | `a0a625433a76c9b39a7009a04579ca02f9844c119679ba9a533ff678dbcbc69b` |
| `backend/app/plc_facts/schemas/query.py` | `1689676876f6f5b360ccac23769a56da6a7b3f926bd5f90d0c4af385254671cf` |
| `backend/app/plc_facts/schemas/read_out.py` | `4b8c421e993d9977f652e1f74fd2904837cacbd91a1136cf32c0d082259e2ad9` |
| `backend/app/plc_facts/schemas/receipt_out.py` | `14d37df54acbef48fe55eedc9d26b1c3512a422f9f4bdaac45b304b651979e40` |
| `backend/app/plc_facts/schemas/source.py` | `1c3726df2f8b73761e1b0aff61323ed5452911ab941df3065ae5e35f60f9e639` |
| `backend/app/plc_facts/seeds/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/services/__init__.py` | `7854abf69f61c0f894d6e7ade415f472f09c2279f77e32112a342dbc67ea3270` |
| `backend/app/plc_facts/services/async_ingest.py` | `91b15e1842847db6612fc83753a9a9fac2caaa44a57c655ee223a12685a9a60f` |
| `backend/app/plc_facts/services/async_query.py` | `7755a9537779afa4ee05615686282de831e0451fc02fe77948479e46d46b383e` |
| `backend/app/plc_facts/services/sync_maintenance.py` | `e30fec0575217a62e177a5afb3fc89fd5ecf085cc7c99aaabf666774cd6ccd84` |
| `backend/app/plc_facts/source.py` | `a7fd7ef75149e251a47d838fbd57db00c540c7990d1f64f3d9e9a67edc1489d8` |
| `backend/scripts/plc_facts_maintenance/.env.example` | `0566bf0000ca7971b51c57e8619f1ef396c5b6197768d61db7228388f645644f` |
| `backend/scripts/plc_facts_maintenance/README.md` | `93a1dd80d22aeeae9183bfc4c39d64c988145b192813fefe7cd0483cd34fe565` |
| `backend/scripts/plc_facts_maintenance/README.zh-CN.md` | `2779bf3112b4e24f00a386bbed3e15d5cc0bdaca175cb1c549435ba9281bb2a5` |
| `backend/scripts/plc_facts_maintenance/main.py` | `5edbd02e113ac97d648dbe07b790d85f01c7e5ba50cff56b92abbf4538b99e66` |
| `backend/tests/test_plc_facts_api.py` | `6e5846b3411d35f707628a7878ce8e5e5344aa7b62ad5f674eaf9b184f76bed9` |
| `backend/tests/test_plc_facts_compatibility.py` | `a59199a867fffed737f20ed93fb1dcb0fe12532a2531f0ccedacab2667fe1908` |
| `backend/tests/test_plc_facts_contract.py` | `e867628362d40a58b832bfa3313342ab6696604c367f3beda1c464d72f27dd49` |
| `backend/tests/test_plc_facts_cursor.py` | `caff312c0c0e2ef5b5cbf7b704a27aa387382d6c1ac47aa4dc43f0948ff6f6fc` |
| `backend/tests/test_plc_facts_maintenance.py` | `c1e12a1c0d9d51a1dc58b8503307436cb13aface52e9f9fd393098aa52aa1b94` |
| `backend/tests/test_plc_facts_migration.py` | `c36a0a892fc8965d3751db2f32bdd55f2134340c135b8670aec4df8f5520499f` |
| `backend/tests/test_plc_facts_ordering.py` | `c03cdafbff4bded33617e5676fe7ef85aa401449ecc924163192d6d158be76fc` |
| `backend/tests/test_plc_facts_retention.py` | `e7569f3aa2f3db5b12f216c877b08d415decfe9d3fc400a08f36ea8455052637` |
| `backend/tests/test_plc_facts_source.py` | `f5848c5fe5172590f3d5e1875371a4e578ac21f986af6ad332086a506161e5d0` |
| `backend/tests_mysql/test_plc_facts.py` | `676bb934a5d592f9c24fe2731724c29b81db9f12861d9478f2f39e53d28930ca` |
| `contracts/published/http-api/plc-facts-v1/README.md` | `1c039c4d19ef0637f94fbd0f8d7f8898e02f30d88ff7dcd9172ac09803ecd6c8` |
| `contracts/published/http-api/plc-facts-v1/README.zh-CN.md` | `cd18b24a2302e232e3ee19f2fcf798263430afeb02dd3f5fb484d8a3ad46bfc3` |
| `contracts/published/http-api/plc-facts-v1/openapi.json` | `bec51c468ff64a8d34dbb0a2faab2fda76d2b33769ee5ef066dc81e8bca274ee` |
| `contracts/published/http-api/plc-facts-v1/schema.json` | `60d0e285bebb1c6d24588f4d5f90e7bdd85ed0befdeab9d0b93445a94f45d4b3` |
| `contracts/published/http-api/plc-facts-v1/vectors.json` | `9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782` |

### 返工1证据SHA-256与资源

- `rework-1/guard.py`: `7db1fd033b1e81cbb5ceeb3eccf7adff02b83a6d2098b7992da7f395d5406356`
- `rework-1/run_suite.py`: `57f58642dc01063218d9a9ab85cf17f6c80fbe5ddba0f1026be7c24046287ce4`
- `rework-1/surface.py`: `afcab4ea4bb560087976fc448f62e48e7b3597eaa1720fa79b5117e109be7fa9`
- `rework-1/record_sql.py`: `b521ff1f3e829083dbf91ebe2c69deae646ba2752e7c5da2b2adccef1da59459`
- `rework-1/audit.py`: `4b9698cebeeaa593d7da41e9ab903080b24a369493f65fbcecdab3724f73c841`
- `rework-1/qa-counterexamples-red.log`: `fadd4db063f914e2e502c35b60479c8453ac0ef1489214e5c94fcdd60738f13b`
- `rework-1/formal-regressions-red.log`: `45a6c24a9970047eb91e549f0bc99336bfe2db56c1b0bc1f63563bed07f68cd2`
- `rework-1/formal-regressions-green.log`: `926a8e776151b26e16e490c964e03ea79f7b95ba89edd2c89af244055901b5b0`
- `rework-1/whole-files-green.log`: `78c6a6c03a6e61eabff9cb9021ccd712aa5b0428e87ed33bda84c27be31d4329`
- `rework-1/static-contract-tests.log`: `c8dd8fb264fae8a8f2a0fb26feb1d1c437b499bbc2bd70d75192987233d860ab`
- `rework-1/surface-report.json`: `0e47d5d94cee34d3effcb189a474c320b3e69d9b318d3855ac59aca2a6463580`
- `rework-1/cleanup-candidates.sql`: `7d866e2e14b33baf85eedc37b709f137acd1ef7f3c3184b0ccd4d152a729f4b9`
- `rework-1/diff-audit.json`: `104cdfaadd76779a769d8e309b167bb008e7994b3ca38b892a47ae8d1a4581a9`

新增自有资源只在rework-1：guard/test/反例副本、红绿日志、静态DDL/SQL、旧SHA验证before审计快照/diff、manifest/cache/pycache/basetemp。before仅审计，不执行或替代交付源。保留至QA2/Owner消费后由主协调核对回收；QA1/其他任务证据不归本DEV清理。

Development现在重新developer_handoff并停止写入。主协调启动新的fresh-context Verification QA2，独立消费r1 spec、完整tasks/QA1失败checklist、新57 SHA、七文件差异及真实输出。本轮不提供QA verdict或Human Owner验收，不授权B、provider-ready或部署。


## 已批准 B：Development 执行记录（2026-11-04；起始记录与后续正式完成交接）

Owner 本次明确批准原话：“批准 B 操作提案，按 STD 完成 ARCH-BE-009 r1 和 ARCH-BE-010 r2 的两轮隔离 MySQL 8.4.6 验证及专用资源清理。现有数据库、真实历史数据和 DAA 不动。”精确操作合同为主协调 `/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd/B-operation-proposal.md`；主协调先核验 A 冻结 `joint-source-final.json` SHA `46b27579731898cbd685b69664894b79a8fedf5f75eb03e5f61a9ac61c08c13d` 的163项与 HEAD 全部一致，再明确释放 Dev 轮运行。其本轮基线为 `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu/b-entry-manifest.json`（2718公开文件），不是新 PM Revision。

当前身份为真实 Development `/root/be009_r1_b_development`；只写本 tasks 和已批准 allowlist 内实际发现的必要修复，不写 spec/checklist 或六索引。完整阅读当前 bundle、根/最近 AGENTS/README/PLAN、canonical workflow、development.toml 与 backend-arch、backend-script-tooling、docker-expert、docker-project-ops。此前 A 记录中的“B 未批准”是原阶段事实，不能覆盖本次具体批准；此前旧 F7 `28ed...` 仅为 QA1 候选历史。当前 B 预期 F7 为 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。

本轮证据目录 `/private/tmp/arch-be009-r1-b-dev`（0700）。从冻结公开清单逐文件 hash 验证后复制640份 backend/contracts 源文件到其 source；不复制真实 dotenv/SQLite/历史或项目环境，复用交付树 backend 现有 uv 环境，不安装依赖。所有执行使用 `uv run --offline --frozen --no-sync python`。`run.py` 在产品导入前注入合成 TESTING/MySQL 设置、关闭所有 bootstrap/mock/Projection runner，阻断真实 dotenv、SQLite、监听、非127.0.0.1:33379、非当前专用 schema 与非本轮应用账号的连接；primary 使用 never_connect_primary 合成哨兵。口令/随机 cursor key/epoch 仅在0600私有 connection.json/docker.env，不进入仓库或输出。

先 inspect 专用名称与 lsof33379：均不存在/无监听，固定 mysql:8.4.6 本机镜像已存在，无 pull。初次普通 sandbox Docker及loopback被拒绝，改用已批准动作的 require_escalated 后成功；这不是业务故障。Dev专用容器 `arch-be009-be010-proof-dev-mysql` ID `be0e024aaa7ffda4b9e1148b63d819c2dfa6d984b1f5d8c18958cd4f812645ae`；网络 `arch-be009-be010-proof-dev-net` ID `43cd94fb05c0599463fddf3db4a75778f4a4b90d496256736fa6e9c9cd0f680a`；卷 `arch-be009-be010-proof-dev-data`。三者标签 `aiis.task=ARCH-BE-009-r1-ARCH-BE-010-r2`、`aiis.round=dev`；容器loopback映射127.0.0.1:33379→3306，挂载仅本卷。镜像ID `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`，inspect脱敏结果保存docker-container.txt、docker-volume.json、docker-network.json。资源由root最后核验ID/标签并清理，本Development和QA均不自行删除。

root只用于创建四个proposal精确schema与专用非root账号 `be009_be010_dev`；GRANT仅覆盖四库。真实查询已确认 VERSION=8.4.6、global time_zone=+08:00、REPEATABLE-READ、CURRENT_TIMESTAMP/UTC_TIMESTAMP差28800秒，provision exit0。库为 `arch_be009_r1_dev_schema`、`arch_be009_r1_dev_facts`、`arch_be010_r2_dev_joint`、`arch_be010_r2_dev_time`。后续普通迁移/行为只用非root账号。

执行脚本与命令：`stage.py`逐项调用 `uv run --offline --frozen --no-sync python /private/tmp/arch-be009-r1-b-dev/run.py <精确schema> -m alembic upgrade f6a8c0e2b4d6` / `upgrade 0a2c4e6f8b10` / 专用schema空七表 `downgrade f6a8c0e2b4d6`；每次输出日志及完整 argv/exit 保存commands.json，失败不静默跳过。schema.py对全部旧64表保存结构、rowcount、行值/ID/精度摘要；schema库额外植入合成 energy_prices 行900009（Numeric四位边界），比较升级/空回退/重建守恒；joint/time旧表初态为空如实记录。这是本节建立时的进行中记录；当前完成结果以随后 B 实际命令和最终 Developer handoff 为准，不把当时计划冒充已执行结果。


### B 实际红灯、修复与最终源码

本轮真实 MySQL 发现三项源码问题，均在原 r1 实现 allowlist 内修复，无新表/Revision、公开合同或依赖：

1. 首次 `f6→0a2` 退出1，MySQL错误3818：`Check constraint 'ck_pf_state_singleton' cannot refer to an auto-increment column.` 原 `Column(Integer, primary_key=True)` 使单例id默认 AUTO_INCREMENT。仅 Model 与同一0a2迁移显式 `autoincrement=False`；失败发生首张新表，原64表/合成行保持。重跑真实迁移、空七表回退、再升级全部exit0；未用stamp/create_all绕过。首次失败退出记录仍在commands.json，本段保存精确错误；同名schema-0a2.log后来是修复后成功日志，不能冒称保存了首次完整trace。
2. 实际七表成功后采用退出1，live F7 `84323f629ce9feb3a30d5b006ac0e3ca82c2bed3f664bad64f88a65c80f7f672` 不等于 frozen `1ba...`。具体差异仅 MySQL 把继承 `COLLATE UTF8MB4_BIN` 附在 String/VARCHAR 的类型展示：batches.receipt_id/terminal 与 stream_state 的adoption_id/schema_profile/storage_epoch/storage_profile/verified_schema_revision。七表所有这些列均无Model/DDL显式collation，是内部UUID/固定枚举；身份比较键仍完整VARBINARY，未改变。normalized_type只消除这个继承展示后缀，真实反射F7命中 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。保留f7-model.json/f7-live.json/f7-diff.log与失败facts-adopt.log。补正式回归；另证VARCHAR长度、VARCHAR/VARBINARY、DATETIME精度、DECIMAL精度仍不同，未抹除NULL/default/索引/约束字段；不使用此规则放宽承担比较语义的显式排序规则。
3. 201条过期Cycle原值真实 `execute(cleanup)` 退出1/busy：原代码循环积累修改后集中flush，实际SQL时间未在后续候选预算中计入，最终>100ms回滚。修为每项值/批proof删除后flush，完整serial前缀整体flush；只flush不commit，counter/floor/实际删除继续同事务。候选工作留20ms余量给最后SQL，最终100ms防线保留，200行/2MiB、10事务/2000行/20MiB/2s上限不变。真实201行新fixture最终exit0，事务118行/88ms、83行/62ms、空事务8ms，共清603bytes；精确计数相符。三次故障在真实SQL/flush之后抛出，实际rollback保住原行/计数，独立失败计数1/2/3并degraded，随后重入清800000bytes并归零。正式回归模拟每次flush耗时，旧实现会积累200项，修复后3项后停止；原200前缀/多tick/引用proof回归保留。

B入口同时修真实异步测试边界：所有async测试使用module loop，module finalizer在loop关闭前dispose实际AsyncEngine。首轮正式9项通过但有mysql marker warning，最终命令显式登记该marker；最终9项通过且无warning/skip。允许已知fixture重入时仅接受外层明确固定 EXPECTED_HIGH_SERIAL/EXPECTED_PROOF_ROWS/SOURCE_SEQ_START，默认仍要求0/0/0；不清库或静默复用未知状态。没有把私有手工调用代替公开整入口。

最终改变7个实现/测试文件及本tasks，无新增仓库路径；F7语义值不变（auto increment未包含在既有F7 shape，故另有实际DDL与明确回归，不能声称F7覆盖它）。正式交付树仍 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD仍 `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，无commit/Git写入。7文件与实际验证公开副本逐字相同：

| 文件 | 最终 SHA-256 |
| --- | --- |
| `backend/app/plc_facts/models/state.py` | `104bedf1907a325decc54e1f041ff31d1a723434f35a38331515f398e2aa3d0d` |
| `backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py` | `e6114a2e9236572a83bbeba7bd10d4e8d5df7e0e072da83c38518419a0d63da1` |
| `backend/app/plc_facts/crud/sync_maintenance.py` | `661c9a94eb026401173a588412517e3240966f66d802612cdbaa475e40cbabc4` |
| `backend/app/plc_facts/services/sync_maintenance.py` | `3e138ae817c49a20243cf8c6df0c5df57ffc2e91248171956a5f29d28798ff61` |
| `backend/tests/test_plc_facts_migration.py` | `972ac57918ea828cfd91dd8e2299eaa39c9969550900d5c156c7bacd5a90e321` |
| `backend/tests/test_plc_facts_maintenance.py` | `8411c164fd742aac59e3681ff7dd392462ec7b7d93dd5e74ceb0b3f85e91ffca` |
| `backend/tests_mysql/test_plc_facts.py` | `45a9408f7f33f4365a1b798f94d76a92e9abebc44b07a88f997bfff9aef958bf` |

### B 实际命令、环境与结果

以下P固定 `/private/tmp/arch-be009-r1-b-dev`，W固定正式树backend目录。普通数据库行为命令均在W使用既有Python3.13.3/uv环境，无install/sync。完整公共前缀：`UV_CACHE_DIR=P/uv-cache uv run --offline --frozen --no-sync python P/run.py <精确schema>`，随后argv见表；run.py切至P/source/backend公开副本，只连接该schema专用账号。shell内P/W在真实命令中均已展开绝对路径。Docker与loopback因sandbox需require_escalated，操作仍限Owner具体合同；没有自动审核拒绝后绕过未授权动作。

| 完整后续argv / 真实命令 | 实际退出码/结果 |
| --- | --- |
| `P/provision.py`（独立root入口，非run.py） | 0；仅四新库/专用账号与本轮权限、8.4.6/+08/RR/28800秒；root不用于普通测试。 |
| `-m alembic upgrade f6a8c0e2b4d6` / `upgrade 0a2c4e6f8b10`；schema库 `downgrade f6a8c0e2b4d6` / 重新upgrade0a2 | 初次0a2为上述3818 exit1，修复后全部exit0；完整schema/argv/各次退出码保存commands.json；应用表64→71，排除alembic_version。 |
| `P/schema.py seed/64/71/rollback64` | 0；原64各表结构与全部行/值/ID/precision逐项对等；schema合成energy行900009保留，joint/time初始旧64全空如实记录。 |
| `P/adopt.py <facts/schema/joint精确schema>` | 首次F7差异exit1；修复后真实profile、CLI adopt plan/apply全部0，目标/epoch/expected-binding0/context SHA确认，控制行由采用创建。 |
| `P/base_matrix.py`（facts） | 0；7个公开原函数单loop真实执行，仅定位证据，未执行的06/09未称skip通过。 |
| `-m pytest -q --confcutdir=tests_mysql --basetemp=P/formal-temp -p formal_fixture -p no:cacheprovider tests_mysql/test_plc_facts.py`（schema） | 0；正式9 passed/14.04s，零skip；外层plugin于06明确建立合成到期/120天前缀，09真实historical/cursor_gap。初轮仅mysql marker warning。 |
| `P/formal_final.py`（schema）实际pytest argv `-q --confcutdir=tests_mysql --basetemp=P/formal-final-temp -o 'markers=mysql: dedicated MySQL B' -p formal_fixture -p no:cacheprovider tests_mysql/test_plc_facts.py` | 0；**最终9 passed/12.18s，零skip/warning**，消费最终7文件；外层只读冻结当前fixture水位/proof/sourceSeq，不清库。 |
| `P/extended.py`（最终成功续阶段extended-5.log）及此前成功checkpoint | 最终续阶段0；真实定义/代次/片/父token/并发/期限/配额场景见下表。私有helper曾ImportError、跨组manifest不完整、组合摘要未排序等exit1，纠正helper并从真实已提交checkpoint继续，没有改产品去容忍坏fixture；完整失败日志保留，原有proof未删除。extended_clean_round.py另整理完整干净轮可复现脚本，尚未以该脚本重跑，不能冒称它已有exit0。 |
| `P/cleanup_matrix.py`（cleanup-matrix-fixed.log），`P/cleanup_budget_final.py`（cleanup-budget-final-2.log） | 0；预算/201饥饿/引用proof/真实rollback/120天前缀/时钟/旧64矩阵；201新fixture实际逐事务结果如上。首次cleanup-matrix.log exit1是产品预算失败；首次final报告把float交pf-json导致TypeError，真实DB事务已成功，修正报告类型后另用新fixture复验0。 |
| `P/precision_matrix.py`（precision-matrix-2.log） | 0；真实高精度REAL/原UTF8 BLOB/亚微秒、真实SQL截止前等后；首helper manifest未改PLC归属exit1，修正后通过，未改产品。 |
| `P/supplement.py` / `P/faults_final.py` / `P/read_boundaries_final.py`（read-boundaries-final-2.log） | 均0；多PLC/DB/组、二进制键、ASGI错误/并发、值配额/回滚/锁与2000扫描/混合原文到期。read helper首轮源码分段SyntaxError退出1，修正私有helper后0。 |
| `P/tick_interval.py`（tick-interval.log） | 0；生产维护Service两次实际tick相隔60.083秒，均真实0行/1事务；不安装调度，不替代生产长期SLA。 |
| `P/joint_revalidate.py`（joint） | 0；BE010明确升1b3/75并释放joint后才运行；schema-only plan/apply及三路实际ASGI/旧ACK恢复/守恒见下表，完成已交还BE010。time始终BE010独占。 |
| A guard `.../arch-be009-r1-a-dev/rework-1/guard.py P/a_runner.py` | 0；正式九整文件逐字副本 **181 passed/26.95s**（原178+3有意义回归），直接导入最终正式源码；禁DB/socket/dotenv、独立confcutdir/basetemp。第一次误把-m传给只消费脚本路径的guard退出1，改自有a_runner调用pytest.main后通过。 |
| 同A guard运行原rework-1/surface.py，日志P/final-surface.log | 0；preflight/正常composition/metadata75/pending4/唯一链/七表DDL-Model/OpenAPI快照/24链接/独立9摘要/targeted compile通过。该旧helper写出的surface-report.json与A历史原hash `0e47d5...` 逐字一致，未改变历史结论；复制同字节结果到P/final-surface-report.json作为本轮证据。 |
| `P/final_db_audit.py`（facts，最后数据库入口） | 0；live0a2/71与F7正确，value/proof计数等于实际，除本次审核自身外facts/schema无其它应用连接；自身engine随后dispose/进程退出。joint/time其它活动由BE010负责，不据本次断言它们已关闭。 |

每次实际HTTP都使用ASGITransport，不开TCP listener；普通query无Content-Type要求。完整成功/unknown/拒绝JSON与身份/digest/+08时间/副作用由断言和相应私有proof保存；口令/key不打印，拒绝token不作为公开日志。新源码无结构新增，CODE_INDEX及根六索引没有Development写入。旧六迁移/旧engine/session/认证/Projection源未改；新七表不调用旧writer或真实PLC。

### B 逐项 Development 证据（不是 QA verdict）

| AC / 场景 | 已实际执行的证据与结果 | 限制/职责边界 |
| --- | --- | --- |
| AC01/11 三路与准入 | 正式ASGI POST→MySQL七表→latest/history读回，真实status/Content-Type/full JSON/身份/摘要/+08、side effect；415/422/413/403均none且计数不变；四真实在途reader的第五请求429/Retry-After1，释放后四200、inflight归0。 | 匿名scope不是身份认证；未开放TCP服务/部署。 |
| AC02 精确材料/键 | UTF8原payload BLOB逐字、中文、Case/case/中_文point键和Sample/sample源身份实际共存；REAL `1.0000000000000000000000000000000000001`及observed_ns=789在BLOB/查询精确保存；两精确越界REAL整批422/零DB变化。 | 原PLC float bit准确性不由本服务证明。 |
| AC03 原子/故障恢复 | raw/receipt/cycle/batch/latest增量精确、同批相同回执、同身份变材料409、同批并发；真实commit后丢ACK、真实commit后ASGI close异常、实际flush后rollback确认丢失均unknown，原身份恢复原结果或一次created，不增重复raw。 | 故障为专用Session受控注入，仍使用真实SQL/commit/rollback；不是生产故障概率证明。 |
| AC04 固定片/混合/父 | 实际固定两片跨批first incomplete→rest complete，重放first仍保留首次不完整ACK；新有效+无证明过期成员全批拒绝，无raw/sample部分写，只有终结proof；更换HMAC key重放同父仍同token，子集新batch可提交，篡改token422/unknown缺父410。 | 原父凭据只在合成120天窗，DAA本地退休未实施。 |
| AC05 来源/逐点/定义 | 真实1005点A/1001点B分别推进，旧1003不盖A、等seq异内容409；新bad/null替旧0；same-generation只换context注释/revision保留另点；定义禁用只撤该latest，旧定义窗口只raw；generation1005→新generation1先latest空再1成功；stale CAS409。两PLC同DB同seq、同PLC两DB两组分别独立读回。 | 不按UUID授源；维护CAS受控，不是真设备所有权证明。 |
| AC06 提交安全cursor | 真实独立Session T1已有rawID、commit前停住，T2 429、reader tail不越过；T1 commit、rollback、invalidate断线三类都原身份恢复、后页见所有新事实；晚观察时间新serial可见；过滤空页、真实2000扫描预算空页及续页、range冻结H、原文逐字、24h过窗410与删除完整前缀后的gap410。 | 2001位置扫描负载用专用合成proof fixture，不称真实PLC采集完整前缀。 |
| AC07 expiry/精度 | real SQL latest/history在同microsecond的ns788/789/790前/等/后资格、物理仍在时逻辑gap/无原值、混合成员raw原文保守隐藏而另点latest保留；historical原ACK不复活、不续proof；真实DB+08在process TZ=UTC下不变，state倒退拒绝；月末/闰年纯规则与真实ns存储结合。 | 纳秒“精确相等”调用真实query helper固定asOf，非改系统时钟；月末过去日期用明确合成规则，未修改历史业务/DAA日期。 |
| AC08 清理/配额 | 200空BLOB/NULL前缀后的第201原文、201有值多批、200被引用proof前缀后的无引用尾proof均真实前进；2MiB事务清1600000留800000；真实SQL后3次故障rollback/counter/degraded，恢复归零；full serial prefix才删并存floor；value/proof饱和不删有效材料、旧ACK仍恢复；NOWAIT争锁实际<250ms；26h积压真实status SLA告警；60.083s双tick。 | 条件预算的受控验证，不承诺生产每分钟调度/24h长期SLA、物理页/备份擦除。 |
| AC09 schema/守恒 | f6/64→0a2/71，六旧迁移未改；schema合成energy行900009四位精度及全部64表结构/行逐项相同，空且未采用允许回退再升级；已采用有state拒绝downgrade由正式Model/迁移回归及既有防线覆盖，真实非空回退预期exit1且后验0a2/71/proof/energy合成行均保留（见最终追加结果）；live F7核对1ba...，pending4在0a2不存在。joint0a2真实事实先冻结，再BE010升1b3/75，live F7同；未再核验前latest503，schema-only plan无变、apply只刷新凭据；epoch/adoptionId、sourceBinding、raw/latest/cycle/sample/batch/proof/水位/counters前后逐字相同，三路恢复/同receipt。 | 本角色不替BE010接受其业务/时间采用；未知head/类型漂移不自动兼容。 |
| AC10 兼容 | 64表全部values hash经清理不变，旧六迁移/monitor认证/CA/Projection实现无本轮编辑；相关A preflight和静态compatibility回归通过。joint清理后永久业务值/receipt/sourceRefs由BE010独占执行并记录其bundle。 | 不运行真实CA/PLC/旧环境，不把source保全当现场兼容证明。 |
| AC12 交付 | 最终正式树/公开副本7文件一致；9项B+181项A、静态/编译/机器合同/链接/diff审计真实记录，失败历史保留。 | Development只交接；fresh Verification第二轮独立MySQL/最终QA、Owner最终验收仍pending。 |

### B 资源、敏感材料与 handoff

专用资源未清理，root统一核验ID/标签后按Owner具体批准处理，QA不回收。`resources.json` 是脱敏完整身份；`sensitive-files-inventory.json` 仅列P/connection.json（root/app口令、cursor key、epoch）与P/docker.env（容器初始root口令），均0600，不含值。它们供BE010当前Dev资源和root后续清理，不能作为唯一测试证据；公开报告已保存目标身份/F7/矩阵/摘要，无需把秘密持久化到仓库。所有本角色子进程已退出/引擎连接关闭，事实/schema无其它连接；无HTTP listener/后台调度。joint/time在串行移交后仍由BE010使用，资源仍有后续依赖，不能据本角色完成立即删库/卷。

B自有临时资源仅P：640公开源码副本、合成fixture/私有guard/runner、pytest basetemp、pycache/uvcache/log、DDL/反射/快照/矩阵与7文件diff清单；不创建branch/worktree/commit。P目录保留给fresh QA/Owner，root最终回收可不再依赖的部分。原A/QA/PM/BE010/root证据不归本Development清理。

最终Developer handoff：ARCH-BE-009 r1，A返工1 + 本次已批准B必要7文件修复，正式未提交工作树及精确SHA如上；最终DEV self-check已覆盖上述真实MySQL/ASGI矩阵。请fresh-context Verification消费完整spec/tasks/原checklist、root B-entry/A冻结、7文件diff/SHA和上述真实命令/日志，并在其全新QA容器/卷/四库独立验证；不得把本Dev容器复用为第二轮或把本self-check写成QA verdict。Owner最终验收、生产历史采用、部署/DAA/SMA/PLC/现场及生产调度SLA未取得。本profile仍contract_only，串行handoff/任务文档/diff审计是合同控制。

关键证据SHA-256（P内；完整清单b-evidence-manifest.json，不含秘密）：

| 证据 | SHA-256 |
| --- | --- |
| `formal-final.log` | `6df03d945b2089494a2b65db393e443bec9b910908353324ae608cfacd2ece47` |
| `a-regression-2.log` | `1212206b9842d9250fccf9bdb76ef4b1fa0484f625a240327f7b9531e5662714` |
| `extended-report.json` | `928027d8841e45290621053d470b9de50596cf7e13172e7f40719a90ba62a48d` |
| `cleanup-report.json` | `06bad82398951f19f2d91f568bdaedb2286ced844fd202b9496ed83862427f0f` |
| `joint-schema-only-proof.json` | `260f69afa1c52a003cf7eaa455fcd6a186137bde84bb5f86603a8c957f51103b` |
| `old64-conservation.json` | `8a1d776e0c8de1d1e700c49729409f310eaba00b22871a9f0d93d9a79766bf2a` |
| `final-db-audit.json` | `1e13987fee3cfb863f55a4d92ea16335b6f7dc9e62168a4e9d262d4d1e98935e` |
| `final-surface-report.json` | `0e47d5d94cee34d3effcb189a474c320b3e69d9b318d3855ac59aca2a6463580` |
| `resources.json` | `08e54a70f80e2abf8ec50b07c6a459e4160f0e89d8efd974433b553b3c0a9450` |
| `b-final-source-manifest.json` | `36df6af4caafea3fac278f8a350ce092808f05e0f34ab66b6025f0cc73bb9307` |
| `sensitive-files-inventory.json` | `dc071dcc1eb6ed617e111a043f2c71fec19bcadb0e3848ce04be0ad887d37568` |
| `run.py` | `6bf1ea815d070583b9fce925a01b8e2965a47a79d4c29158f94de427495518a6` |
| `formal_fixture.py` | `446d8cf21ed9f7a305e52385080001b488d58c712801b37ae41f227eaed7a49a` |
| `stage.py` | `3f077d45b6cf304d1fd271a740710a9d50c73a6161743c3fcc866cda2e5ea393` |
| `adopt.py` | `a1164aa29b268b6df22ffd1a4d06fb1a3b0c9ead808750fe533c62cd91a36246` |
| `base_matrix.py` | `def7c8d5801f5d1011d903843edbd18ae3541a0b229a61fb79c0cefb9bd7a707` |
| `extended_clean_round.py` | `f2206e11f028f0d823ff82831e87a7b6beaff23a96aa76dca66bebff1c070059` |
| `cleanup_matrix.py` | `64eaad103b273675e4106bf2538061b5a130004084d6c80e9e61d57c30799955` |
| `cleanup_budget_final.py` | `f20dd0c43eaf2945bb43232b721c0fc2e6c7d1390e1025d555f0ba1b33f6c35f` |
| `precision_matrix.py` | `4387be085c2cd8026477023ae29c3a9e1088fd00e70202ce0b4069f2b7610fa9` |
| `supplement.py` | `13c3c6bd92ef546dbc140a7930f1c604e88d9e97874df453ee3b547c9be7c166` |
| `faults_final.py` | `e505b6358fa412218b47c89beabccb75c4d6ce9b1fa654c73af4a11347041753` |
| `read_boundaries_final.py` | `5ec374989f290dba6f7372bc526bd54ddeab275ccf958396c42d1a7dc0611102` |
| `joint_revalidate.py` | `50fedd6964c69303c4f4432d40d5765b2f36ce7f3d5b00d9decc5d9ee43a996f` |
| `tick_interval.py` | `0884be34dfae703d773b7d33f7006091f0d345d5c49315385a75f7b64f522941` |


最终收尾追加：`run.py arch_be009_r1_dev_schema -m alembic downgrade f6a8c0e2b4d6` 实际预期exit1，明确 `PLC facts downgrade requires all seven tables empty and unadopted`；随后的 `refused_downgrade_audit.py` exit0确认revision仍0a2、71应用表、所有proof/value计数一致且energy_prices.id900009与0.1234/12.3456/999999.9999保留。此只读后验是最后数据库命令，进程退出/engine dispose；此前final-db-audit同样0。没有真正删除已采用表或回执。

最终证据汇总P/development-summary.json列明私有场景名称及7文件精确hash，保护spec/checklist与六旧迁移对root B-entry均未变，公开源码副本相同；逐行UTF8/空白及git diff --check退出0。整体仍是Developer handoff，fresh Verification与Owner结论未取得。所有本角色写入停止，专用资源保留给root/BE010当前依赖和后续收尾。

### B 最后联合清理与再次 Developer handoff（2026-11-04）

上次handoff后，root按同一已批准B提案安排最后联合清理，产品7文件保持冻结。BE010明确完成business extra m10、非空后继回退拒绝及68非facts表/485行全行快照，确认DB进程退出、Engine disposed、无活动事务后，才暂交joint。本角色此前只准备私有脚本并AST校验，没有提前连接；time/facts/schema及任何任务外数据库未触碰。

唯一实际命令（cwd为正式树backend；P仍为本轮目录）：`UV_CACHE_DIR=P/uv-cache uv run --offline --frozen --no-sync python P/run.py arch_be010_r2_dev_joint P/joint_cleanup.py > P/joint-cleanup.log 2>&1`，真实exit0。先核live1b3/75/F7=1ba...、原epoch/adoptionId与精确计数，仅对joint-fixture.json中原1批/1sample/1cycle建立明确合成到期fixture，再调用本owner CLI；没有改变系统时钟、原材料/摘要、来源绑定或业务值，没有DDL/任意清表。

CLI精确argv为`cleanup --target-alias arch-be009-be010-proof-dev-mysql --schema arch_be010_r2_dev_joint --expected-schema-revision 1b3d5f7a9c20 --expected-storage-epoch <joint-fixture中原epoch> --operation-approval Owner-approved-B-operation-proposal-2026-11-04 --confirmed-by BE009-Development`，先`--plan`，再`--apply --confirm APPLY:cleanup:arch-be009-be010-proof-dev-mysql:arch_be010_r2_dev_joint:<同原epoch>`。完整展开目标在私有joint-cleanup-proof.json，口令/key未输出。plan预测5行/4229bytes/2proof（无实际flush后的Cycle proof释放）；apply实际6行/4229bytes/3proof/2事务、整次55ms，最后空事务5ms，真实exit0。

原raw/latest/sample receipt/batch receipt/cycle proof全部删除；state.value_bytes/proof_rows=0且等于实际。完整serial前缀floor从(0,0)推进至(1,1)，旧cursor明确410/requiresResync。storageEpoch/adoptionId/sourceBinding、F7与highSerial=1保持；68张非owner应用表全部485行的rowcount及完整行摘要前后相同。BE010另有FLOAT CAST DOUBLE精确快照，将独立检查永久业务ACK/sourceRefs/mapping/生产事件/父子引用，本角色不代判。这里人为提前到期proof，删除后不重放仍带近期观察时间的原facts wire制造不真实复活；不把fixture冒充真实120天自然流逝。

进程exit0并dispose同步engine后，已立即明确交还joint给BE010。交还后本角色不再连接。资源没有回收；新增私有文件仅joint_cleanup.py、joint-cleanup.log、joint-cleanup-proof.json、joint-cleanup-manifest.json，无新秘密文件。七产品文件、spec/checklist/六索引保持不变。joint-cleanup-manifest.json记录脚本及两份证据SHA；本任务再次以同一r1 B、同一正式未提交工作树和7文件最终manifest handoff给root，待与BE010 retained结果共同冻结后进行fresh Verification。以上仍是DEV self-check，无QA verdict或Owner最终验收。再次停止所有写入。

### B 专用资源收尾记录（root 执行，2026-11-04）

本段只登记后续实际资源状态；上文A/B失败、全部实施/交接与当时“资源保留”的记录作为历史完整保留。依据同一Human Owner明确批准的两轮隔离B操作提案及专用资源清理，实际执行者为root lifecycle coordinator，不是本Development或QA。root收据完成时间为`2026-11-04T22:10:52.665327+08:00`。

Development本次仅读取并核对以下三份脱敏收据的SHA，没有调用DB/Docker、测试或任何源码实现入口，没有读取、恢复或连接已删除的口令/配置：

| root收据（目录 `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu`） | SHA-256 |
| --- | --- |
| `cleanup-receipt.json` | `23048893ca4c71a6fc7ca76d0e9a466371c41e6fda15880458f8515cac5e41cb` |
| `owned-resource-cleanup.json` | `2c7df8944739811cadc1ac1286f4807b33e9b516140eb4b70b7548c25b155d95` |
| `sensitive-cleanup.json` | `230ee3c391b98001b87cdbf3e437903d7cd0c025b0fbdc8559ead7d3930e9b0a` |

按root实际执行及收据，两轮精确创建身份核验通过后，2个专用容器、2个卷、2个网络已删除并核验不存在，8个专用schema随所属卷删除；资源清理与敏感配置清理均exit0，清理期间数据库连接数为0。Dev容器/网络ID与本tasks原创建记录一致；QA容器ID为`4dc2c195c5d800c792684c97a61f66a4ad7bef12cc35b343d6b47c3eed906bf2`，网络ID为`f3ae03e4c91a3fee11bce68011867d738fdde437623003eb169483a7678d2dc5`，卷为`arch-be009-be010-proof-qa-data`。root仅处理本次专用资源，没有触及现有数据库、真实历史、DAA或其它任务资源。

两轮inventory列出的27份生成口令/key/操作配置已去重删除，逐项不存在；收据明确未读内容、未输出秘密。本Development原P/connection.json、P/docker.env也已删除，之前引用它们的运行命令仅为历史证据，不能再作为现成连接入口，不恢复其内容。产品7文件、本任务spec/checklist、六索引及A/B失败历史本次均未编辑。

以下五个目录中脱敏命令、日志、报告、公开源码副本与before/diff证据仍保留，供独立QA收尾与Human Owner最终审阅：`/private/tmp/arch-be009-r1-b-dev`、`/private/tmp/arch-be010-r2-b-dev`、`/private/tmp/arch-be009-r1-b-qa`、`/private/tmp/arch-be010-r2-b-qa`、`/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu`。生成的操作秘密已经移除，不以秘密文件作为唯一证据。后续回收触发为Owner最终验收后，先把必要结论持久化至各自tasks/checklist，并确认无证据、运行或后续任务依赖，再由root核对归属处理；其它任务及A历史本次不回收。

本次只追加Development资源事实并报告tasks新SHA，不代替QA独立核对或更新其checklist，不授予Human Owner最终验收或实际生产采用；Owner final仍pending。再次停止写入。
