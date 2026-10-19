Task ID: ARCH-BE-006
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA3独立验证最终B handoff：A+B通过，F-001/F-002及B-001关闭；专用资源清理已独立确认；交Human Owner final acceptance，pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Fresh Context: 独立verification上下文；未继承Development对话推理，仅消费批准spec、tasks、源码、diff及测试工件
Verified: 2026-10-17

# 当前结论与轮次

**QA3 / B最终：ARCH-BE-006 r1 qa_passed；F-001/F-002及B-001关闭，Human Owner final acceptance pending。** 完成155项相关回归/编译、三个独立MySQL场景、独立字段/约束/事务补证及五页真实浏览器矩阵；Root清理后精确Docker对象/原PID/private目录与三个端口已独立确认。当前默认全套的四项冻结profile失败历史继续如实保留，未改/skip/xfail，未冒称全套全绿。最终输入、命令、逐AC及限制见末尾QA3。

以下QA2为本轮入场历史结论；QA1/QA2正文与原失败记录保留。

**QA2 / rework-1：A通过（仅源码/no_db）；整体qa_blocked，B-001仍open。** 本轮集中150项测试、compile及独立时序/故障探针通过，F-001/F-002在A范围关闭；真实MySQL并发与全部必需数据库/浏览器验收仍待B。未授予Human Owner最终验收。

以下QA1正文保留失败历史、原输入和复现；当前检查及handoff见末尾QA2。QA1原字节副本SHA256 `d9e8bf0afca615e29bc46ff3ec0a327365d8a9bac37ff3ed2fe0b5061d4e18b6`保存在本轮证据`input/checklist.md`。

# QA1独立验证结论（失败历史）

**ARCH-BE-006 r1：qa_failed，A源码阶段未通过。** 两个确定性源码时序探针分别复现生产历史事件误判stale和投递身份冲突优先级丢失，见F-001/F-002。QA未修复实现、测试、spec或tasks。

独立当前完整no_db结果为**604 passed / 4 failed / 30 deselected，exit1**，全树compileall成功；四失败仍是保留的冻结profile断言。前端23 routes/9 groups、46模块测试、10来源/展示测试与build通过；offline base→f6、唯一head/history及B入口collect通过。这些通过项不关闭并发finding，也不证明真实MySQL或浏览器闭环。

B是必需的未解除gate，数据库（包括SQLite）、Docker、真实API/browser listener、PLC/Projection均未运行。A返工及新的fresh-context QA完成前，不进入B执行；整体不能qa_passed或owner_accepted。

# 验证依据、角色与输入冻结

独立读取根AGENTS、canonical development-lifecycle-workflow、实际`.codex/agents/verification.toml`、根README/PLAN双语、backend及app说明、equipment README/PLAN双语、monitor README双语、frontend-js及src/app说明/PLAN、完整本任务spec/tasks。未发现更近AGENTS；performance无更近README/PLAN，使用上级规则。

使用project-governance、aiis/CONTRACTS、backend-arch（分层、响应、数据库迁移、注册、认证、测试与数据治理）、frontend-ui/FRAMEWORK、i18n-workflow和code-document-indexer，只用于验证。通知窗口由Root维护，QA未另开窗口或发送邮件。

实际命名verification按fresh-context handoff工作；TOML中的`gpt-6.1-sol/max`是配置证据，不把它写成另行确认的运行model/effort，也不宣称平台角色ACL、强制路由或完整Agent Team activation。

| 冻结输入 | 独立核对结果 |
| --- | --- |
| `git rev-parse HEAD` | `f85bea8bbf36b491968c3dc9a839518a1ed434a8` |
| 批准spec SHA256 | `58c69b8eac6e3a182e6592c2c048743566100eee6c77307ac2fa885a33265557` |
| developer_handoff tasks SHA256 | `9384cfd0e31d60699dcfad4c726c6b06ad2d3ca63c6085dd060cab67b6c2e938` |
| DEV handoff.json SHA256 | `dedac1be777a5e23b081fa705ebd4d2e47179a179669cf9016d1384b39721bb9` |
| DEV delta.json / delta.patch | `790d239c21de053174ade72537f405a29979ccba5b489507f73c5e691ac8ffea` / `3beedeff96acfb45024b5563f9416a8632de837c222ae3e83eda897992cee9f7` |
| DEV source-map.json / evidence-sha256.json | `7a4ee0c976337d807433a018c5d0f52c2785566219f7d5c36049faec0fd32de1` / `c21f4b4d7545223da8efbec96d181a31dc8f4e9c35ab649bec6978f9550e0738` |

QA临时根：`/private/tmp/arch-be006-r1-qa-fresh/`。从742项公开source-map复制backend/frontend及必要治理文件到`source/`；源码与handoff hash一致。111项Development delta全部在123项有限allowlist内，before与entry-source、after与当前树一致；独立1538项公开基线审计无意外变更/删除。六个协调者索引排除实现漂移判断，spec从draft到批准收据的已知PM变化单列，不归Development。

另外逐字核对51项保护文件（含energy、Projection、旧sync Services、五条旧migration、BE003温控关键文件及依赖/lock）无变化；其余公共文件由1538项基线审计保护。现有ignored依赖没有完整事前字节基线，不声称venv/node_modules每字节未变。

# 环境与执行隔离

macOS arm64；项目uv运行时Python3.13.3，FastAPI0.135.1、SQLAlchemy2.0.48、Alembic1.18.4、Pydantic2.12.5、pytest9.0.2；Node22.19.0、pnpm11.11.0。系统python3只做纯文件审计/编排，不冒充项目行为运行时。

后端仅公开副本及合成进程配置，复用既有`.venv`，底层固定`uv run --offline --frozen --no-sync python -c <guard + payload>`。`backend-run.py`记录label/cwd/退出码/耗时；精确`-c`内容由同目录`guard.py`与对应`*-payload.py`按换行拼接，均纳入证据hash。SQLAlchemy engine/raw connection、AsyncEngine、DBAPI、SQLite、socket connect/bind/listen及真实workspace env打开被guard阻断；guard前置到嵌套uv的Python `-c`，并继承offline/no-sync。`TESTING=True`不是隔离保证。

合成配置使用127.0.0.1:1、fixture占位账号、不同primary/test库名、grants=[]、mock/runner及三bootstrap=False；真实.env未打开或改写。内存ASGITransport可用，不创建监听端口。

前端复用既有node_modules，通过继承的NODE_OPTIONS阻断net connect/listen、TLS、HTTP/HTTPS、dgram bind/connect/send及真实env读取。所有pnpm命令均显式`--config.verify-deps-before-run=false`，offline、更新检查和Corepack网络关闭；mock/demo关闭、两角色page grants=[]。不安装依赖、不改锁文件。QA两份forbidden-attempt日志均不存在，未观察到guard拒绝调用。

Development首次pnpm隐式registry尝试失败、未完成安装的历史已读原日志及tasks，不能写成整个任务从未有网络尝试。此限制与后续DEV/QA guard下执行分别记录。

# 独立执行记录

以下命令从QA临时根执行，所有日志/产物仅在该根；同名payload均已保存，可重建底层argv。

| 命令 / 输入 | 真实结果及证据 |
| --- | --- |
| `python3 /private/tmp/arch-be006-r1-qa-fresh/backend-run.py full-current` | exit1；全树compileall成功；`pytest -q -m no_db` **604 passed/4 failed/30 deselected，445.27s**。`full-current.log`，SHA256 `fdae6a92b343fab95a1d2f8e5fe904cbb19a82f20a9e4d2ad7a9684effa4bad1`。125项新定向用例包含在本次完整当前输入中，不另相加。 |
| `python3 /private/tmp/arch-be006-r1-qa-fresh/frontend-run.py` | exit0；node/pnpm版本检查；`pnpm --config.verify-deps-before-run=false check:modules`为23 routes/9 groups；`test:modules` **46 passed**；`node --test src/utils/businessDataSource.test.mjs src/app/equipment/api/mapping-source.test.mjs src/app/monitor/api/mapping-source.test.mjs src/app/performance/views/list/performance-presentation.test.mjs` **10 passed**；同pnpm选项build exit0。`frontend-0.log`至`frontend-5.log`；build保留既有chunk>500k警告。 |
| `python3 /private/tmp/arch-be006-r1-qa-fresh/backend-run.py offline-collect` | exit0；Alembic `upgrade f6a8c0e2b4d6` **sql=True**生成offline-upgrade.sql，包含VARBINARY(200)/DATETIME(3)；唯一f6 head及完整history正确；`pytest --noconftest --collect-only -q tests_mysql/test_mapping_business_api.py` **1 collected**，未调用测试函数。保留anyio已导入的assert-rewrite warning。 |
| `python3 /private/tmp/arch-be006-r1-qa-fresh/backend-run.py production-snapshot-final` | **exit1，复现F-001**；实际生产Service/CRUD，合成RR读视图与当前锁定水位，两个分支均提交stale。`production-snapshot-final.log`、`production-snapshot-final-report.json`。这是源码分支探针，不是实库并发测试。 |
| `python3 /private/tmp/arch-be006-r1-qa-fresh/backend-run.py delivery-priority` | **exit1，复现F-002**；实际drive Service/CRUD，初次receipt未见、取得业务锁前同身份请求提交后返回错误冲突key。`delivery-priority.log`、`delivery-priority-report.json`。 |
| 纯文件hash/allowlist/保护审计，`git diff --check`及HEAD只读核对 | 742项源码map、111项delta、20项DEV证据hash均一致；1538项公开基线无意外改变/删除，51保护项无变化；diff whitespace exit0。`input-audit.json`、`protected-audit.json`、`public-tree-audit.json`、`dev-evidence-audit.json`。 |
| Markdown本地目标及双语键纯文件检查 | 已触达文档及bundle共95个本地目标存在；common/equipment/performance/monitor双语叶键分别64/61/359/206且对称。CODE_INDEX按有界花括号分组索引新结构，新增关键源码有中文说明/现有文件风格。`links-audit.json`、`i18n-audit.json`。 |

QA探针准备阶段也保留真实失败：首稿误把省略字段经model_dump变成显式None，被Schema正确拒绝；第二稿缺完整Model注册而遇Plan关系解析错误。只修临时探针，未改项目代码；第三稿及最终稿均复现F-001。第一次hash摘要打印用了不存在的report别名，已保存最终report副本并重核hash；不影响产品测试结果。

## 四项冻结profile失败的归因

当前完整suite未经删断言、skip或xfail，真实执行并保留下列失败：

1. `test_business_module_migration.py::test_all_operations_match_58_tables_and_only_new_42_are_removed`：冻结58表签名与七表批准增量不等。
2. `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment`：冻结69项与当前72项不等。
3. `test_equipment_temperature_migration.py::test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types`：冻结5条与当前6条不等。
4. `test_equipment_temperature_migration.py::test_single_explicit_head_and_no_data_migration`：冻结e4与当前f6不等。

独立审计DEV的20项证据hash并读取实际输出：冻结60源码483 passed/30 deselected、exit0；较早当前64全集552 passed/4 failed/30 deselected、exit1；最终125定向exit0。QA不把这些DEV输出写成自己的复验，也未再次重跑历史483。

已批准R-005明确分开冻结F58/BE00360与新BE00664；PM只读澄清与此一致。当前新测试完整补证60→64、七目标/其他53签名、69原文前缀加3空scope、旧五迁移字节及唯一f6后继。因此四项固定旧profile断言本身不另列为r1实现finding，也不改称当前全套通过。若要改旧断言使默认全集全绿，需新Revision/allowlist。本轮A失败依据为下面两个独立实现问题。

# 八类能力与验收检查

## 八行源码矩阵

| 能力 | 独立追踪到的写/读/页面路径 | A / B边界 |
| --- | --- | --- |
| 温控 | 原BE003 temperature-samples POST/GET保持；新temperature-sample-dashboard→equipment temperature页 | 十值及原实现保护、窄adapter源码/测试通过；真实同条落库/页面待B |
| 传动 | drive-samples POST/GET→drive dashboard→drive页 | 20字段、NULL/补缺/读面检查；F-002失败；真实FLOAT/并发/页面待B |
| 生产参数 | production-parameter-samples POST/GET→dashboard→production-parameters页 | 精确coil二进制键、七可选项/process_steps=[]检查；共享补缺事务受F-002同型风险影响；真实闭环待B |
| 生产观察 | production-observations POST→mapping-records列表/详情→performance list页 | 生命周期/人工0纯规则覆盖，F-001失败；真实两Session/人工提交顺序待B |
| 过程温度 | `/{id}/process-temperature-samples`→mapping-records/{id}/process-data→温度tab | 父id/设备/coil、Numeric/整数duration、NULL域源码检查；真实FK/并发/页面待B |
| 过程张力 | `/{id}/process-tension-samples`→同process-data→张力tab | 四值/尺度/排序约束源码检查；真实父子落库/补缺/页面待B |
| 过程速度 | `/{id}/process-speed-samples`→同process-data→速度tab | 三值/尺度/排序约束源码检查；真实父子落库/补缺/页面待B |
| 过程曲线 | monitor process-curve-samples POST/GET→trends/latest→monitor temperature四图 | 12 INTEGER+21 FLOAT、存在集合、上海日UTC边界、缺测源码检查；真实精度/不可变并发/四图待B |

新API为async API→async Service→async CRUD→AsyncSession，局部HTTP错误用模块StrEnum，共享壳输出；CRUD不commit。scope每应用懒固定、公开resolve_env_file、空值拒绝全部caller；manifest按整组注册。真实DB裁决、独立Session首次竞争、刷新快照以及页面实际读回必须继续验证，不能凭矩阵声明闭环完成。

## 逐AC结论

| AC | A独立结果 / 精确证据 | 未完成的必需B证据 |
| --- | --- | --- |
| AC-01 八类闭环 | 上述八行源码存在、实际ASGI路由与facade/SFC部分模拟覆盖；未给落库/页面整体pass | 八类真实写→指定GET按recordId/父id/设备→五页面选外部来源/日期看到同条完整观测 |
| AC-02 字段与缺测 | strict JSON、原始Decimal、binary32、毫秒、0/省略/null、条件字段及SQL NULL/legacy默认测试在604通过项内 | MySQL实际数值、NULL、反射类型与页面断点；模拟refresh不代替存储读回 |
| AC-03 防重与补缺 | **失败F-001/F-002**；现有串行补缺/冲突、故障替身通过不能覆盖这两种并发时序 | 返工后真实独立Session首次竞争、同/异身份、同刻旧事件、丢响应/未知commit稳定恢复 |
| AC-04 主子与人工优先 | **旧成功观察判重/冲突失败F-001**；manual override含0、duration优先、父失败重试、显式PUT/DELETE隔离的源码/ASGI模拟通过 | 原PUT实际改HTTP行，人工/观察两提交顺序、真实父/子/FK、退出/unknown/重激活/晚到 |
| AC-05 分域兼容 | 旧CRUD仅NULL域过滤；旧8 sync Service/Projection事务链、温控旧表/原接口与energy关键文件逐字保护；当前旧行为回归除四冻结项通过 | 新旧同键共存、真实删除/更新隔离、跨设备读及全旧行校验和 |
| AC-06 事务/故障/HTTP | 新Service单事务、CRUD不提交；局部两层依赖退出先于响应、DEBUG脱敏、模拟flush/refresh/receipt/commit/退出失败测试通过；并发裁定仍有finding | 各模块真实insert/update/flush/commit/依赖commit/rollback/close故障及未知提交恢复；无孤立receipt/部分业务 |
| AC-07 权限/模块 | JWT坏/过期/refresh/revoked/inactive及admin/read/ingest/scope在内存ASGI覆盖；本地配置process>合成dotenv与每app隔离通过；三example原69前缀逐字保持加3空scope，grants未改 | 真实JWT撤销存储、模块重组disabled404与各caller读写的数据库环境复验 |
| AC-08 迁移 | recorder/Model64表、仅七目标增量/其他53保护、旧五字节、唯一f6 head及offline DDL通过；安全downgrade前置拒绝用替身检查 | 空库base→f6、e4合成旧行→f6、64表反射/约束/collation/default/fsp、旧行校验、可丢弃回退及有HTTP/毫秒/NULL时拒绝 |
| AC-09 页面 | 五入口URL legacy/http+equipmentId，空设备不查、不fallback、清空/代次、NULL/0及双语源码检查；46+10及build通过 | 浏览器实际刷新/返回/分页/轮询/日期/过程弹窗、403/故障/空态、日夜/窄屏/中英与同条数据 |
| AC-10 有界交付 | 当前完整604/4/30及编译、前端、offline/collect、diff/hash/allowlist已完成；原断言未缩减；**A因F-001/F-002失败** | 返工精确handoff及新fresh QA；B获批后完整实库/浏览器矩阵；Owner最终验收单独记录 |

# 实现失败与返工

## F-001：水位锁后的旧事件查询仍消费旧一致性快照（P1，QA1 open；QA2 A关闭，B待验证）

对应R-003、R-004及AC-03/04/06。源码：[production transaction/apply](../../backend/app/performance/services/async_production_observation.py)，L32先普通get_receipt，L92锁水位，L93查旧事件，L98–103在未见旧事件时返回stale；[receipt CRUD](../../backend/app/performance/crud/async_mapping_ingest.py)L4–9两次均普通SELECT，后一次没有current/locking read。现有[engine](../../backend/database/engine.py)不指定隔离级别，本轮未查询任何实库隔离级别。

合法RR调度：请求C初次receipt普通读建立早于t1的视图；在C取得水位行锁之前，其他请求依次提交t1成功生产事件（原recordId=1）与更晚t2停产事件。C取得当前水位t2后，用同设备/t1的新actor/sampleId重放同内容或异内容。普通get_applied_event仍看不到快照后的t1成功receipt；代码直接走stale并提交新stale receipt，无unique冲突或新事务重读。

规格要求：t1已有成功事件时，同内容duplicate且关联原业务id；异内容409 `performance.mapping_observation_time_conflict`。实际Service/CRUD确定性无DB探针两分支均返回`outcome=stale, record_id=null, affected_record_ids=[]`并commit一次，receipt.outcome=stale。改变旧内容也成功留下stale回执；不是规格允许的“尚无成功事件的晚到”。

SQL证据顺序为`receipt普通SELECT → state ... FOR UPDATE → applied-event普通SELECT`，由实际CRUD编译生成。探针仅替代连接的快照/当前视图返回值，未改项目函数；它证明源码对该合法视图组合的错误裁定，**未声称已在MySQL实库复现**。

复现命令：`python3 /private/tmp/arch-be006-r1-qa-fresh/backend-run.py production-snapshot-final`。payload SHA256 `7cf746b3d19fd9ae4f6afa0a9e3185cbb22c78e0836888bcdf793750d5ea3b31`；最终report SHA256 `52f95a827203a36feafc2c9e67fec361f6c6a7b95a92f1d401659577e8fb5242`。

返工要求：在已批准边界内使水位串行裁定中的历史成功事件判重/冲突消费当前提交事实，并补该时序的必要回归；不得通过改全局engine隔离、删除旧断言或把已成功旧事件一律改成stale绕过。B后续验证实际独立Session调度与稳定原recordId。

## F-002：业务行锁等待后的投递身份冲突失去优先级（P2，QA1 open；QA2 A关闭，B待验证）

对应R-003及AC-03。源码：[receive_partial](../../backend/app/equipment/services/async_drive_sample.py)L29先查receipt，L35取得业务行锁；L43–48遇已有异值直接抛`mapping_value_conflict`。receipt insert在L63之后，只有IntegrityError才进入L71–76的有界重读，因此该提前BusinessException无法恢复投递冲突优先级。

调度：两个请求有相同actor/equipment/stream/sampleId和同来源时间，分别tv=1与tv=2。第二个请求初查receipt未见；在其取得业务行锁前，第一个请求提交tv=1及同投递receipt。第二个取得当前业务行后，直接返回409 `equipment.mapping_value_conflict`并rollback，没有重读已提交receipt。

规格要求同投递异内容优先409 `equipment.mapping_sample_id_conflict`。无DB探针调用实际drive Service与CRUD、保留实际SQL，返回值为`actual=equipment.mapping_value_conflict, status=409, rollbacks=1`；只有两条SELECT，未触发receipt unique路径。该缺陷不依赖RR：初查与取得业务锁之间的并发提交本身即可触发。现有串行sampleId冲突用例不能覆盖。

复现命令：`python3 /private/tmp/arch-be006-r1-qa-fresh/backend-run.py delivery-priority`。payload SHA256 `ee20075d835f2a409ec9f41a2d11574acfb3765c42598353e9c257410fe6f77b`；report SHA256 `99bb13ad727100466821ac5ad821cc3752426e54f55481d36f72fa14f8ad24dc`。

返工要求：锁后业务冲突裁定仍须保证投递身份优先级，加入上述必要回归，并检查生产参数复用receive_partial及performance各stream的同型路径。具体实现由Development负责；QA不代写修复。

# Acceptance Audit、阻塞与handoff

| 表面 | 当前事实 | 下一gate |
| --- | --- | --- |
| A源码静态/串行模拟/前端构建 | 上述通过项有独立证据；A整体未通过F-001/F-002 | Development r1返工、精确新handoff、新fresh-context Verification |
| B真实数据库与页面 | **B-001：未获具体批准且未执行**，不是deferred complete | A通过后由Root提交BE006专用MySQL8.4.6/schema/账号/端口/卷、API/browser、动作与清理方案，Owner具体批准后执行 |
| legacy / rollback | 旧域及旧来源保留；不删除已接收HTTP数据 | 真实回退/迁移均独立授权 |
| Human Owner final acceptance | pending，QA不授最终验收 | 全部必需验收证据齐备后只交Human Owner决定 |
| 现场采用、PLC/Projection、部署/发布/Git变更 | 本任务未执行且仍排除 | 后续独立批准 |

B必须覆盖本checklist逐AC列出的全部实库/浏览器项，不能只执行当前准备入口的一条测试后宣称完成；尤其要增加两项finding的真实时序、人工重量两种提交顺序、所有故障位置和五页实际同条闭环。prepared B入口的compile/collect与纯函数检查不关闭这些gate。

QA唯一仓库写入为本checklist；未改spec/tasks、源码、测试、配置、锁文件、六索引、其他bundle或Git状态。六索引由协调者依据本verdict机械同步。实现failure通过Root返回Development；QA结果仅供Human Owner后续最终验收，不自动进入运行采用。

QA资源为`/private/tmp/arch-be006-r1-qa-fresh/`内公开源码、guards、drivers、payloads、失败/成功logs、offline SQL、前端dist及审计json；未创建服务、DB、Docker资源、浏览器tab、分支或worktree，无运行中的QA命令。DEV与Root临时目录继续保留供返工/复验，不由QA清理。临时路径不是唯一证据：本文件已记录输入hash、命令/环境、结果、失败调度及解除条件。

QA证据根manifest：`qa-evidence-sha256.json`，SHA256 `f651969e53f0b0308c036328e7d05d84f53076a3d4a42518c2202a79565e361d`。完整证据含原准备失败；返工及Human Owner最终验收前保留，资源收尾由Root按实际依赖盘点。

**Verification → Root → Development：F-001/F-002，r1源码返工。Verification → Human Owner：qa_failed、A未通过、B未批准/未执行、最终验收pending。**

# QA2：rework-1 fresh-context独立复验（2026-10-16）

本轮为新的实际verification上下文，不继承Development推理；独立阅读完整r1 bundle、根/最近作用域AGENTS与README/PLAN、canonical workflow、verification TOML、三Service及其调用者/CRUD、返工diff与可用输出。使用project-governance、aiis/CONTRACTS及backend-arch的分层/事务、响应、数据库和运行测试规则。未变前端、迁移与索引采用指纹及QA1证据复核，不冒称本轮重新执行其构建或完整旧套件。profile为contract_only；角色配置值不是另行确认的运行model/effort或平台ACL。

## 输入、环境与保护

| 精确输入 | SHA256 / 独立核对 |
| --- | --- |
| HEAD / 批准spec | `f85bea8bbf36b491968c3dc9a839518a1ed434a8` / `58c69b8eac6e3a182e6592c2c048743566100eee6c77307ac2fa885a33265557` |
| rework-1 tasks | `377874b6a124b4aa9465d504c587563ed233176b4cbe1ac9351d509cc0b7a3ae` |
| DEV rework-1 handoff / source-map | `d060bdea361e38d19c66bd61d209159c69ca606318ffbe71fb04ed2fb6b35fef` / `b15027fe4ca3753dc2e4bbbe8d19e7134035cce390f8c3118a1c8424a2ff8792` |
| DEV delta.json / delta.patch | `f974d7a58f26b79b5e8417901a5b93a18722705d262d38e9560fe29bf4e6b59c` / `0406bac4b5022286072bc21986fbd04b5210d27d094c66b83246f5da7a830ad2` |
| DEV rework-1 evidence manifest | `a55a7f9e8aafde963cb7556b4232d1f6a9a5477d4dc72ec8bde8987b4b32b435`；20项全部匹配 |
| QA1 evidence manifest | `f651969e53f0b0308c036328e7d05d84f53076a3d4a42518c2202a79565e361d`；36项全部匹配，包含原失败探针/报告 |

QA2根为`/private/tmp/arch-be006-r1-qa-rework1-fresh/`。742项公开源码与DEV handoff-source/实际focused-final逐字匹配；当前实现仅五文件相对QA1变化，另加tasks共6项，均在既有123项allowlist内。当前backend两份PLAN相对DEV source-map有协调者机械漂移，已单列，执行副本固定声明输入而非把索引漂移当实现变化。首次准备审计因此exit1；仅调整临时审计对六索引的已授权分类后exit0，原准备脚本/输出保留。

51项保护文件、旧CRUD/Model/migration/前端全部指纹无变。221项前端与QA1及原DEV一致。原1538公开基线中1471项逐字保持、54项既有批准实现变化、6项已知AW并发文档变化，其余为六索引及PM批准spec；无意外改变/删除。AW观察不扩BE006 allowlist、不归因给BE006且未恢复/修改。最终写入审计另存`closing-audit.json`。

运行环境实测macOS15.7.7 arm64、Python3.13.3、FastAPI0.135.1、SQLAlchemy2.0.48、Alembic1.18.4、Pydantic2.12.5、pytest9.0.2。仅公开副本/合成进程配置及项目既有venv，`uv run --offline --frozen --no-sync`，UV_OFFLINE/UV_NO_SYNC继承到嵌套uv；无安装、锁文件修改或网络。独立审查并前置guard阻DBAPI/Engine/SQLite、socket连接/绑定/监听/DNS及真实env打开；forbidden-attempts日志不存在。合成127.0.0.1:1、mock/runner/bootstrap关闭、grants=[]；ASGITransport与无bind ORM identity map均不创建数据库/listener。旧DEV首次pnpm隐式registry失败历史继续保留，不能宣称整个任务从未尝试网络。

## 本轮实际命令与结果

底层argv、cwd、耗时/退出码在`commands.jsonl`；`<label>-executed.py`保存真正执行的guard+payload。以下三个项目行为命令均由QA2独立执行，不是DEV自检转录。

| 命令 | 实际结果 / 证据 |
| --- | --- |
| `python3 /private/tmp/arch-be006-r1-qa-rework1-fresh/backend-run.py focused` | exit0；公开backend全树compileall成功；完整七个相关test文件 **150 passed / 8.33s**。`focused.log` SHA `cfbd0ee3e395f62148c4c5eda1cbfe44b255b03f72d0bec395f21e91db0790af`；150含原125及本次25，不相加。 |
| 同driver `timing` | exit0；**31例**实际Service+CRUD、MySQL编译SQL及合成调度：F-001四例、七stream三分支共21例、三owner重读system/DBAPI六例。`timing-report.json` SHA `5aa0286860cc25691e8fa94157928dff57ef3a20f0f79057866e46e3e67efead`。 |
| 同driver `faults` | exit0；**28例**七stream各原始system/DBAPI/内部500/未知commit失败；均无成功假恢复，receipt只读一次、无业务commit。`faults-report.json` SHA `7284305410d164fda3ead7fd0800e333ac2553cd896b108314cad90be87810bb`。 |
| `python3 .../prepare.py`；`python3 .../close.py`；`git --no-optional-locks diff --check` | 准备修正机械索引分类后exit0；终检核对源码/保护/本轮仓库写入、bundle本地链接及whitespace，结果见`input-audit.json`、`baseline-audit.json`、`closing-audit.json`。 |

未重跑完整no_db或冻结483、前端构建、offline迁移及B collect：未变指纹及原真实输出已独立核对。QA1完整当前输入仍如实为604 passed/4冻结失败/30 deselected、exit1；四冻结断言未改/skip/xfail。QA1前端23routes/9groups、46+10测试/build、offline base→f6/head/history及B仅collect的通过仅作为前轮证据引用，不等于当前默认全套全绿或实库证明。

## Finding、AC与事务时序结论

| Finding / 对应AC | QA2 A结论 | 必需B复验 |
| --- | --- | --- |
| F-001，AC-03/04/06 | **A关闭**。初查receipt及认证可能建立RR视图；miss时结束只读事务，随后state锁为current read，首个历史一致性读在锁取得后建立新视图。独立模型按rollback清除视图/待写入、后续读重建；保留QA1原固定旧视图失败输入，未原样误用不允许rollback的旧替身。相同内容返回原recordId=1并只补duplicate receipt；不同内容409 observation_time_conflict、无commit；state首次插入1062后新事务重试同样通过，t2水位未倒退。 | 真实MySQL RR、独立Session按原t1/t2锁等待调度、首次state竞争与原id/无stale误收据 |
| F-002，AC-03/06 | **A关闭**。七stream在业务拒绝后rollback，再一次普通receipt读：已提交异内容优先sample_id_conflict；无receipt保持原value/time拒绝。同内容首次receipt未见→命名unique→新事务duplicate返回稳定原id，业务不重做；三helper同内容恢复/未知commit/rollback失败由150项覆盖。恢复不锁缺失receipt，不增加业务提交。 | 七stream真实首次竞争/补缺/冲突、receipt可见性、各故障位置与commit结果未知重试 |

补充源审与回归：初始rollback只在production且在业务写之前；真实SQLAlchemy Session.rollback会结束根事务并失效已装载ORM状态。API在await前取actor.id，后续Service及错误日志使用已捕获整数/请求state，新事务重新读业务/receipt；150项包含无bind Session的真实User失效+ASGI成功。结果字典在commit前复制，不访问回滚前旧业务对象。原始系统/DBAPI/commit失败不进入成功恢复；恢复重读系统500、DBAPI503，未知提交503。CRUD仍不commit，未改全局隔离或新增gap锁。

AC-03/04/06的两项A failure已解除；AC-01/02/05/07/08/09/10沿用上方QA1逐项源码证据并由本轮相关回归/保护复核，无新增已证实实现finding。所有AC的实库、真实浏览器、人工重量两种提交顺序与完整故障矩阵仍按原B列执行，未把模拟升级为最终验收。

## 当前verdict、阻塞与停止写入handoff

**A subverdict：passed（source/no_db only）。整体：qa_blocked；B-001 open，Human Owner final acceptance pending。** 下一gate为Root提交BE006自己的disposable MySQL8.4.6/schema/非root账号/loopback端口/卷、迁移/反射/旧值/约束/并发/故障/回退、测试API/五页浏览器目标及清理清单，Human Owner具体批准后再执行B；当前准备入口的一条测试不能代表全部AC。

本轮唯一仓库写入为本checklist。未改spec/tasks、源码/测试/env/依赖/锁/六索引/其他bundle；未运行任何DB（含SQLite）、Docker、在线Alembic、listener/真实浏览器、PLC/Projection或Git写。无新服务、后台命令、DB/Docker资源、tab、分支/worktree；全部QA命令已结束。证据、原失败及公开副本保留供B/Owner复核，不由QA回收；Root维护通知窗口，QA未另开/发送邮件。

本轮`qa-evidence-sha256.json`与外部`handoff.json`固定证据及最终checklist哈希，交Root机械同步当前聚合状态；QA1 manifest和原失败仍保留。**Verification → Human Owner：A源码通过、整体qa_blocked、B-001未批准/未执行；完成本checklist及证据审计后停止仓库写入。**

# QA3 / B最终handoff独立验证（2026-10-17）

本轮为实际命名`/root/be006_r1_b_verification`的fresh-context Verification，未继承Development推理。独立读取根AGENTS、canonical workflow、实际verification TOML、根README/PLAN双语及最近backend/equipment/monitor/frontend说明，完整r1三文件bundle、最终B源码/diff与DEV原始工件；按变化使用project-governance、aiis/CONTRACTS、backend-arch及其数据库/响应/认证/测试边界、frontend-ui/FRAMEWORK、i18n-workflow、code-document-indexer、interface-lineage-audit，以及Docker边界skills，仅用于验证。没有运行血缘扫描器或修改实现。`contract_only`仍不代表平台ACL/强制路由。

Human Owner明确批准“批准 B 两轮验证及专用资源清理”。本轮仅在该具体授权的第二轮新QA资源上执行；上一轮Development证明只作交接材料，未充当QA。初步通过与最终cleanup gate分开：数据库/浏览器检查完成后先向Root报告，Root清理后再独立查验，最后更新本checklist。Human Owner最终验收仍pending。

## 最终输入与增量源审

| 输入 | 独立核对的SHA256 / 事实 |
| --- | --- |
| HEAD / 批准spec | `f85bea8bbf36b491968c3dc9a839518a1ed434a8` / `58c69b8eac6e3a182e6592c2c048743566100eee6c77307ac2fa885a33265557` |
| B操作提案 / approval receipt | `665c5ef2dc9fcfcf81e0e5d2a1449a6f0b0516ef28f671f622b11eb4dbb6d129` / `166403b5c9d7a15abcb649a2e679cff3b0dbb235c248d45850b2d77531a54ea7`；位于`/private/tmp/arch-be006-r1-proof-2nndlnnf/` |
| B tasks / handoff.json | `6611e65ba65f9b283f0461c8db3ea6145a6dd51ee780f5097f2e363bdce43e87` / `6d7f22a475ea96ffbdd506d518001ecdc3c913702c31e17d1803fa3dc17bac47` |
| B source-map / delta.json / delta.patch | `ef41fb7b326720c99d041478a0fc39c0705ad773c4c52d5b89029eaf2c8ce199` / `03c6970a52fa3af61259efb77ad026f0c811087e880dd9a1ef249ba44bf495f1` / `2ae07da4de72243f3ac4e5677be9723a1ee2c77ff8c8e9bc29cc7f35188b5ba3` |
| B DEV evidence manifest | `e442e37e852877bdbdc3c65665125013718dcfe40049f6f9204015649d5287da`；162项逐项核对，DEV结论未转录成QA结论 |
| QA2 checklist入场副本 | `dc1bbf1b0da119d5693ac434f2fc1501db77a2a248c16d47c9cd93056bf2a583`，保存于本轮`input/plans/.../checklist.md`；以下QA1/QA2历史正文保留 |

QA临时根：`/private/tmp/arch-be006-r1-qa-b-fresh/`。742项固定公开源码包含521 backend与221 frontend；四个实际B执行副本各521项以及临时UI的521 backend/221 frontend逐项匹配。相对QA2仅九个源码/README/test路径，加tasks共十项变化，均在已批准范围；backend PLAN双语相对handoff的Root机械同步单列。1600项公开入场基线在初步handoff时无变化/删除；最终仅本checklist为QA写入，源码、spec/tasks与HEAD再次保持。原五迁移、energy、Projection与旧sync源码、BE003、frontend及依赖锁由固定source-map/相关回归保护。没有撤回并发AW更改。

本次产品增量为设备两表DATETIME(3)默认值使用`CURRENT_TIMESTAMP(3)`，与真实MySQL精度匹配；补缺事务对已锁定业务行的refresh改为`with_for_update=True`，使RR下实际读回已提交完整行。独立完整相关155项检查及真实锁等待/refresh回归通过。原F-001的初始只读事务结束、F-002的拒绝后一次receipt重读保持；未改全局隔离、冻结profile、旧调用链或前端。

## 环境、目标与实际执行

macOS15.7.7 arm64、Python3.13.3、FastAPI0.135.1、SQLAlchemy2.0.48、Alembic1.18.4、Pydantic2.12.5、pytest9.0.2；使用项目既有venv与锁文件，uv为`--offline --frozen --no-sync`。公开副本/进程合成配置；真实env未读取/改写、未安装依赖。no_db guard阻断全部DB/网络/listener；B guard只放行127.0.0.1:33076、精确QA非root账号和本次单个schema，禁止其他DB/SQLite/真实env/额外listener/DNS，并以sitecustomize继承到Alembic子进程。

Root的QA资源记录与独立运行时身份一致：新container `4e628af7c3e85d4662011f41145b2b17ff436994363d2702dd7820496b481f97`，MySQL8.4.6、`be006_qa@%`、REPEATABLE-READ、SYSTEM；新卷`arch-be006-r1-proof-qa_mysql-data`，CreatedAt `2026-10-16T17:18:55Z`，与DEV卷不同；network `062245725f890d48d2e7fb9f167804dbe42c42d9c7244adf6a1785d14b8b2abe`。精确三schema `arch_be006_r1_empty/upgrade/rollback`分别从0表开始。primary `be006_unused_primary`仅用于目标差异断言，未连接或创建。mock、Projection runner及三个bootstrap关闭；新三scope为line-A，BE003温控为temperature-pilot-01。秘密仅从Root0600 runtime文件进入受guard进程，不进入argv或公开工件。

| QA实际命令 | 真实结果与公开证据 |
| --- | --- |
| `python3 /private/tmp/arch-be006-r1-qa-b-fresh/backend-run.py focused` | exit0；完整backend compileall；七个完整相关test文件 **155 passed / 8.32s**。`focused.log` SHA `c1aee6ebc7166d0e1a11ed521072095a01349b216d2fdd8ef0014700d13a44cf`。 |
| `python3 .../run-mysql.py empty-1 empty` | exit0；`pytest --noconftest -q ... tests_mysql/test_mapping_business_api.py` **1 passed / 37.20s**；空库base→f6、64表反射及完整业务矩阵。`empty-1.log` SHA `f6d7d23c9bc6f2aafa9fa4f1148210144a2023405fc83c4ba6d84cb1ad7cbba0`。 |
| 同driver `upgrade-1 upgrade` | exit0；**1 passed / 39.44s**；base→e4、合成旧行→f6、其他53表签名/60旧表原列与PK值保护、完整业务矩阵。`upgrade-1.log` SHA `07ce362a032650288e912b7a9d4d1aa4b36a595b46e42a33f67ea4373dd1069b`。 |
| 同driver `rollback-1 rollback` | exit0；**1 passed / 51.25s**；e4→f6；实际NULL/毫秒降级拒绝均exit1且DDL前schema不变；清除专用探针值后可丢弃f6→e4→f6及完整业务矩阵；有HTTP数据时再次拒绝降级。`rollback-1.log` SHA `0693c4ed7e81270fddf6cd598d32b317b9101cd93e0c0a9dbefa0635ab3cbef3`。 |
| 同driver `independent-3 upgrade independent-probe` | exit0；独立补写的真实API/SQL字段、原生约束与旧事务探针。113提交字段逐项GET↔DB；11个named unique冲突1062、3个跨设备复合FK冲突1452；跨scope403无泄漏；旧八sync caller rollback前后全部11表行一致。`qa-independent-proof.json` SHA `b7d8a6cf118e5e5c69e56049eb4bc33116ac63878fe439f1b42152af1f171875`。 |
| CUA Chrome五页 / 三过程tab | 五入口实际API/DB、来源/设备/日期、403/空态/受控503/旧响应隔离、分页/刷新/历史、中文暗色及英文浅色390窄屏通过。实际DOM/动作摘录`browser-observations.md` SHA `402709081d48d56d38cabbc85db881d757d18116e30603bed9d0dbbf44b03cc3`；图片仅在对话可见，没有声称磁盘PNG。 |
| `python3 .../closing-audit.py`；`git --no-optional-locks diff --check` | exit0；742源码/执行副本/UI产品源与独立夹具指纹、输入/保护/1600公开基线、155本地链接及whitespace核对。 |
| `python3 .../resource-audit.py dev-clean`及`final` | 均exit0，只读精确对象检查；最终DEV/QA共10名称/原ID查验均absent、两个private目录不存在、33076/18066/15176均无LISTEN，详见清理gate。 |

命令的真实argv/cwd/退出码/总耗时分别保存在`commands.jsonl`与`mysql-commands.jsonl`，不是表内pytest耗时的替代。每次B均执行完整入口而非collect或prepared诊断：各179个完成notes、28个首次双Session竞争调度、79个实事务故障位置。它们是单pytest测试内的结构化场景/断言，不冒称179个独立pytest测试，也不与155相加。

保留QA准备错误：第一准备脚本把backend PLAN机械漂移误归增量而exit1，分类修正后通过；独立探针首次误把最终UI手工remark仍当原上报remark、第二次误设子表自带coil字段，两次均在只读字段比较处exit1；仅修QA临时预期，第三次完整通过，原脚本/日志均保留。真实三个MySQL场景首次执行全部通过。CUA原生readonly combobox、清空rerender时source选择及restore主题错误title的失败尝试、弹窗关闭动画期间未生效的点击和reload期间transient后退也如实记录；不把未完成操作算pass或产品finding。

## 实库裁决、独立补证与AC结论

三场景均用真实JWT、实际ASGI路由、SQLAlchemy独立AsyncSession、显式barrier与MySQL提交/回滚，未将同Session串行循环冒称并发。反射64业务表与Model比较column/type/null/default/fsp/collation/index/unique/FK/check；大小写equipment/sample/coil/zone实际共存，三owner receipt stream/target CHECK实际拒绝非法行；HTTP省略值为SQL NULL，legacy0/默认值保持。旧60表原列与原PK值在多个阶段按row checksum保护，其他53表结构签名不变。

F-001按真实RR的t1成功、t2更新水位、等待者旧receipt读视图调度复验：同内容duplicate返回原recordId，异内容409 observation_time_conflict，水位不倒退、不留下错误stale receipt。F-002真实锁等待中同投递异内容优先sample_id_conflict。生产state首次竞争每轮均一个initial200/一个可重试503，稳定重试为updated/duplicate两个200且只有一state行；28个首次竞争涵盖补缺/同值/异值。原始QA1失败探针及QA2 A结论仍保留；**F-001/F-002的B gate本轮关闭**。

79故障位置覆盖实际业务SQL与flush/refresh/receipt/Service commit/依赖commit/rollback/close，并包含实际commit之后注入未知结果、稳定重试恢复。故障通过受控wrapper在真实Session/事务上注入，不宣称MySQL服务宕机演练；每场景检查没有部分业务、孤立receipt或虚假成功。父缺失失败后重试、退出/unknown/重激活/晚到、父设备/coil检查与跨设备FK，人工重量0在两种实际锁/提交顺序中均保留，reported duration优先保持。旧八sync Service由caller实际控制rollback与commit，同时保护HTTP行；Projection runner没有执行。

| AC | QA3 B最终结论与独立证据 |
| --- | --- |
| AC-01 八类闭环 | **通过**。八stream真实写入→指定GET→DB逐项对照；独立113字段覆盖温控11、drive21、参数9、生产16、过程温度8/张力7/速度6、曲线35（包括来源时间与coil经父记录）。五入口及三过程tab读同条/同parent固定数据。 |
| AC-02 字段/缺测 | **通过**。真实FLOAT/Numeric/INTEGER/毫秒、SQL NULL/0、省略/null/strict JSON拒绝、case-sensitive binary keys反射与读回；UI将真实0与缺测区分。 |
| AC-03 防重/补缺 | **通过**。同投递/存在集合/内容冲突、完整delivery case8类、首次竞争28、RR锁后refresh2、F-001两分支/F-002两模块、未知commit恢复均实际复验；原recordId稳定。 |
| AC-04 主子/人工 | **通过**。真实父子关联/生命周期/晚到、人工0两提交顺序、原PUT编辑权限与HTTP字段隔离；页面parent31三tab同父，HTTP编辑只开放重量/备注，未通过UI额外提交。 |
| AC-05 分域兼容 | **通过**。新旧同键共存、NULL域旧读写/删除隔离、60旧表原值/53非目标结构、旧8sync caller事务、energy两表三API独立；原保护源码保持。 |
| AC-06 事务/故障/HTTP | **通过**。79实事务故障位置、稳定重试与失败壳、提交退出次序、无部分业务/孤立receipt；浏览器transport503另证空态及晚响应隔离，没有替代数据库故障检查。 |
| AC-07 权限/模块 | **通过**。真实JWT/撤销存储/角色read-ingest/空scope及跨设备403、三模块重组disabled404；实际三新scope与BE003scope分开，公开grants未改。 |
| AC-08 迁移 | **通过**。empty/upgrade/rollback三独立0表目标、64表/七目标/四新表/其他53保护、旧行及byte保护、NULL/毫秒/HTTP降级拒绝与无损回退恢复。 |
| AC-09 页面 | **通过**。五入口真实数据，source/device清空、日期真实空、403、无legacy fallback、受控503与held真实200后的旧响应隔离；刷新/稳定Back-Forward/分页、三过程tab、中英日夜390必要控件均实测。 |
| AC-10 有界交付 | **通过**。155相关回归/compile、完整三场景与独立补探针、源码/文档/真实浏览器与资源终检完成；没有扩大源码allowlist或修改冻结断言，Owner acceptance仍单独pending。 |

## 浏览器输入、时序与证据边界

Root启动授权loopback API18066/frontend15176，仅新增合成UI admin/user7；产品文件从QA已固定upgrade/backend与frontend副本复制，521+221逐项匹配。Root Vite cache wrapper、合成120s request timeout、ASGI transport/一次性安全同源会话桥分别指纹。PM只读澄清属r1必要适配、spec未改。桥实际auth/login+auth/me只是安全会话准备，不计产品登录表单测试；QA没有读密码/token/storage/桥HTML。

固定UI行：temperature11、drive27、parameters28、production31、process temperature23/tension22/speed23（parent31）、curve23；来源时间`2026-10-17T07:00:00.123Z`，上海日期17。`upgrade-1/backend/browser-rows.json` SHA `162a8a1dd009ff5438e23eea00110c99421033b1645532644068b0f7f8db6b19`。production显示人工0.0000与reported1小时，三个过程tab数值同DB；monitor六zone真实0、其余1.25，日期18空值显示“-”。390宽度使用现有横向表格滚动/折叠侧栏，必要来源/设备/刷新/查询/过程tab可操作，不声称所有列同时可见或全面视觉重设计验证。

drive精确line-A GET的一次503显示`BE006 proof transport unavailable / 操作失败`及全部缺测，没有回退TV99。下一请求held后实际清空设备/切legacy，DOM显示TV99/KM0；Root release于UTC17:32:57.931333，实际应用200于17:32:57.938777；QA再次确认当前legacy DOM未被旧HTTP回填。Root completion标记`real_app_called=true`，不是仅prepared/时间猜测。

Root ASGI补充日志白名单误写singular performance，真实产品路径是`/api/v1/performances`；仅遗漏补充事件，没有拦截/改写performance。QA逐项独立核对九条derived access events与实际JSON Uvicorn原日志一致，包含list/process-data31/page2真实200及outside-scope403；明确此为access-log补证而非原ASGI事件。五页DOM、动作及截图由CUA实际观察；工具无落盘截图能力，图片在对话，公开证据只保存DOM/动作摘录和日志指纹，没有虚构PNG/截图hash。

原完整默认no_db仍如QA1记录为604 passed/4 frozen-profile failed/30 deselected、exit1。四个旧58/60/e4profile断言完整保留，没有改/skip/xfail；R-005的冻结profile与BE00664分开，不能冒称当前全套全绿。本轮按B变化执行155相关完整文件并审查迁移保护，未重复未变前端构建/全工程：QA1的23routes/9groups、46+10前端测试/build及QA2 A150/31/28证据作为历史沿用，不冒充本轮新执行。唯一新B实际结果与上表分开。

## 清理gate、最终verdict与停止写入handoff

初步检查通过后Root负责停止两个临时listener与专用compose down --volumes/删除四秘密文件；QA未执行Docker up/down/drop schema、秘密清理或kill。先前DEV initial cleanup实际down成功但absent解析大小写导致中止，原失败/恢复/最终receipt均保留，本轮入场及最终均独立确认DEV对象/私密目录absent。QA cleanup首次最后ordinary bind遇Errno48，未捕获精确端口；Root保留initial-incomplete/failure及port-recheck，随后只读复核原对象/PID/private目录缺失、三个ordinary bind均真实成功并补final receipt，没有重跑删除或信号。TIME_WAIT只是原因推断，没有直接TCP状态观测，不作为确定事实。

QA独立`resource-audit.py final`对DEV/QA精确容器名及原ID、卷名、network名及原ID共10次inspect均“No Such”，两个private目录不存在，三个端口33076/18066/15176的lsof均exit1、无LISTEN；再独立确认原API PID65972/frontend PID66006均不存在。Root真实API exit0/frontend SIGINT(-2)预期；Root普通bind三端口成功与QA无LISTEN检查分开记录，不把首次失败改写成成功。QA逐项核对v3协调工具/收尾manifest22项，manifest SHA `67a7992851b9932a11417f3385b29fa8a98ff9bb15ff145f1a064064475a60f0`；最终`qa/cleanup.json` SHA `7b9e48ab4f2944388bab102f635a26a3ed711c3b50c137ade42bd34c956c3cf8`、cleanup_complete=true。原helper在删除秘密前已完成Root公开proof目录精确秘密扫描且零匹配，但扫描文件count因最后bind异常未持久化，因此count unknown，不杜撰；没有将其宣称为QA独立秘密扫描。

浏览器已恢复默认viewport/中文/深色/原展开侧栏，真实菜单退出→确认→/login/退出成功后关闭自建tab346106640并清单确认；未触碰其他tab。没有QA自建秘密/env副本、服务/后台命令、branch/worktree或Git写，公开tmp证据保留。

**最终：ARCH-BE-006 r1 `qa_passed`；F-001/F-002 A+B关闭，B-001关闭；Human Owner final acceptance pending。** QA1失败与QA2 A结论保持完整历史。QA本轮唯一仓库写入为本checklist，最终hash/证据manifest/handoff存于QA临时根，交Root做机械聚合状态同步。Verification结果仅交Human Owner决定最终验收，不授予owner_accepted、部署/发布、真实数据库/设备操作或Git/GitHub权限。通知窗口由Root持有，QA未另开或发邮件。完成最终audit/handoff后停止仓库写入。
