Task ID: ARCH-BE-003
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: A独立通过/F-001关闭；获批B Development第一轮三个真实MySQL场景通过并已清理专用资源；交另一位fresh Verification第二轮；Owner最终验收pending

# 批准与执行边界

Human Owner：“BE005 r3 验收通过，批准 BE003 r3，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
批准后spec SHA256为6192f862ab24dbf44eb76d1d4d6fe6833a2103a891935c983412821633c4c73b。
Development已消费BE005最新owner_accepted checklist及实现；本角色不写spec/checklist，不授予QA或最终验收。
工作树HEAD为1a5aa2d2fe7089b5671218865238cfaa240f9a30；C0固定363b297bffe65e020108f5504766b4fb1ec3b381。
首次写入前1511公开文件基线位于/private/tmp/arch-be003-r3-dev-6diknqm3/baseline与baseline-files.json；排除真实env/ignored依赖。其他任务dirty增量不归本任务。

# 实施计划

1. 两表、严格Schema/纯规则、本地配置和新async API/Service/CRUD → 原始ASGI、事务注入、SQL及精度边界。
2. 单条显式后继、public helper窄增量 → 五revision recorder/offline和C2/E保护。
3. 独立MySQL入口仅prepare/compile/guarded collect、双语说明 → 完整no_db、链接和有限delta审计。

仅在公开tmp源码副本运行项目uv既有锁/环境，placeholder配置、mock/runner/bootstrap关闭及DB连接拒绝guard。
任何数据库（含SQLite）、任何Docker命令、真实env/服务/PLC/Projection、网络/安装/发布/推送均不执行。

# 实现选型

温度为Numeric(30,10)，20位整数/10位小数、绝对值<10^20；原始JSON解析Decimal，不先经过float。非整数还要求Decimal(str(float(value)))==value，保证JSON number读回无静默变化；整数原样输出Python int。它是技术可表示域，不是物理阈值。
来源时间严格带时区ISO8601，UTC归一并拒绝非零亚毫秒尾数，UTC域为MySQL DATETIME的1000..9999年。存储DATETIME(3)、无时区UTC；系统created/updated使用数据库UTC_TIMESTAMP(3)，不修改engine/session timezone。
业务/投递key使用utf8mb4_bin（标识拒绝首尾空白，避免PAD SPACE合并）。fingerprint为canonical JSON+SHA256、Decimal规范化及UTC毫秒，不含actor/sampleId。
Service拥有commit/rollback；仅MySQL1062且命中本两unique名称时rollback后最多重试2次，重新建立可见快照。commit的非Integrity失败视结果未知503，不再次写；其他Integrity不假装duplicate。


# A 首次候选交接记录（2026-10-16，解析边界修正前历史）

精确ARCH-BE-003 r3、STD、实际Development角色，工作树HEAD仍为1a5aa2d2fe7089b5671218865238cfaa240f9a30，无commit/branch/worktree。批准spec和BE005 owner_accepted checklist字节均保持。本节是DEV self-check及非终态developer_handoff，不授予QA verdict、Human Owner验收或B操作。

## 实际实现

- 新两条async POST/GET独立router与read/ingest权限、首批admin-only写；所有caller含admin经过唯一设备scope。manifest disabled经重组移除旧新整组，旧equipment权限/GET/前端来源不改。
- 严格camelCase十值输入、原始JSON Decimal/duplicate拒绝、完整UTC毫秒与无损数字技术域、规范化SHA256；不补零、不裁剪、不伪造PLC provenance。
- 两表业务/投递unique使用utf8mb4_bin，复合FK保证receipt不能跨设备引用样本；parent额外(id,equipment_id) unique支持该FK。无user FK、无旧行迁移或双写。数据库UTC_TIMESTAMP(3)系统时间与来源时间分离。
- Service完整commit/rollback；同投递异payload冲突优先；MySQL1062仅按异常末尾真实for-key名称识别本两unique，不能因重复值含约束名而假装竞争；最多初次加2次重读。未知提交结果503并保持同键重试；提交后日志/响应失败500、重试恢复原recordId。
- 局部APIRoute适配完整依赖/请求阶段，缺Bearer先401，认证/权限/冲突/输入/不可用/内部失败真实HTTP且同值code。未知业务owner或输出Schema失败500；DEBUG及日志sink失败均脱敏。旧全局HTTP200业务失败不改。
- 本地BaseSettings按request.app.state首次懒固定每应用独立frozen实例；不跨应用共享，dotenv/process变更需重启采用。只公开已存在resolve_env_file，不改Settings/私有读取规则。
- JSON Lines有受控actor/equipment/sampleId/record/outcome上下文；身份未建立时不伪造actor，不记录10值、完整body、token、SQL或连接串。
- 唯一e4f6a8b0c2d4显式d2后继，两表Model/recorder/MySQL offline类型、约束及索引一致；旧4迁移、58表完整子集、旧3GET/8descriptor及Projection本地事务保持。
- 三env example仅追加英文说明和空scope，原前缀/11组标题/值/grants保留，均69项。双语稳定说明及CODE_INDEX只同步批准表面。equipment PLAN/catalog及根/backend六索引由Root机械写入，不归本Development。

## 实际有限变更文件

以下35路径是本Development的完整有限delta；before/after SHA和逐行patch在DEV目录delta.json/delta.patch。Root机械索引及AW/Console并行变化独立列于excluded-parallel-delta.json，不将Git总diff归己。

- `CODE_INDEX.md`
- `backend/.env.docker.dev.example`
- `backend/.env.docker.prod.example`
- `backend/.env.example`
- `backend/README.md`
- `backend/README.zh-CN.md`
- `backend/alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py`
- `backend/app/MODULE_CONTRACT.md`
- `backend/app/MODULE_CONTRACT.zh-CN.md`
- `backend/app/README.md`
- `backend/app/README.zh-CN.md`
- `backend/app/equipment/README.md`
- `backend/app/equipment/README.zh-CN.md`
- `backend/app/equipment/api/temperature_http.py`
- `backend/app/equipment/api/temperature_samples.py`
- `backend/app/equipment/config.py`
- `backend/app/equipment/crud/async_temperature_sample.py`
- `backend/app/equipment/error_codes.py`
- `backend/app/equipment/manifest.py`
- `backend/app/equipment/models/__init__.py`
- `backend/app/equipment/models/temperature_sample.py`
- `backend/app/equipment/schemas/temperature_sample_in.py`
- `backend/app/equipment/schemas/temperature_sample_out.py`
- `backend/app/equipment/schemas/temperature_sample_query.py`
- `backend/app/equipment/services/async_temperature_sample.py`
- `backend/app/equipment/temperature_sample_domain.py`
- `backend/app/module_contract.py`
- `backend/tests/module_admission_fixtures.py`
- `backend/tests/test_equipment_temperature_api.py`
- `backend/tests/test_equipment_temperature_config.py`
- `backend/tests/test_equipment_temperature_migration.py`
- `backend/tests/test_equipment_temperature_service.py`
- `backend/tests/test_module_contract.py`
- `backend/tests_mysql/test_equipment_temperature.py`
- `plans/ARCH-BE-003-mapping-service-api-pilot/tasks.md`

## 项目执行环境与完整证据

所有项目行为从DEV专属/private/tmp公开源码副本执行，复用backend现有.venv、pyproject.toml/uv.lock，通过生成器run_python底层`uv run --frozen --no-sync python -c <guard + payload>`。完整命令/payload/实际cwd/退出码归commands.jsonl和*-payload.py；stdlib编排不充当项目行为验证。无依赖安装/lock修改。公开配置固定MySQL 127.0.0.1:1、TESTING=True、mock/Projection/三个bootstrap=False、角色grants=[]；副本无真实.env。TESTING只选测试URL，不作为隔离依据。

前两次聚焦使用生成器原SQLAlchemy connect/raw_connection拒绝guard；后续完整/源码检查额外拒绝DBAPI、SQLite及socket，并将同一guard前置到嵌套uv子进程。原共享conftest保留，-m no_db使其DB autouse fixture早退。增强guard的connection-attempts.jsonl不存在；没有数据库（含SQLite）创建/连接/读写，没有任何Docker命令、在线Alembic、真实API listener/PLC/Projection启动、真实env读取或写入、网络/安装/发布/推送。

| 实际检查/入口 | 真实结果与证据（均在DEV目录） |
| --- | --- |
| `python3 run.py`第一次聚焦 | exit4，import/conftest前预检拒绝条件枚举来源；first.log及first公开快照保留。改为显式枚举分支，不改预检。 |
| 同driver第二次聚焦 | exit1，72 passed/5 failed；second.log。局部适配把没有header的override权限403误归401，后修为精确HTTPBearer分类及缺Bearer前置。失败原字节保留。 |
| `python3 full.py full-first` | exit0，388 passed/30 deselected、282.81s；同进程全树compileall通过，full-first.log。 |
| `python3 full.py full-final` | exit0，410 passed/30 deselected、282.21s；compileall通过，full-final.log。这是后续加严之前快照，不替代末次。 |
| `python3 full.py full-delivery` | exit0，416 passed/30 deselected、286.22s；compileall通过，full-delivery.log。 |
| **`python3 full.py full-final-exact`** | **exit0，417 passed/30 deselected、286.89s；全树compileall通过**；full-final-exact.log及其payload。保留原完整套件、原选择条件、旧断言，无skip/xfail/缩套件。 |
| `python3 checks.py`聚焦 | exit0，105 passed/8.77s；checks/targeted-final.log。其后追加的内部错误边界已包含末次417。 |
| 同driver实际Alembic CLI via guarded runpy | upgrade e4 --sql、downgrade e4:d2 --sql、heads、history各exit0；checks/offline-upgrade.log/offline-downgrade.log/migration-heads.log/migration-history.log。单d4 root/e4 head、五接链，仅offline，不apply SQL；downgrade只DROP receipt/sample两表。 |
| 同driver C2/E1/E2/BE003真实Model/App组合 | 各exit0，14/15/16/60表、50/52/54/163 method/path；E逐文件冻结Core SHA相同。checks各profile的metadata-routes.json/core-files.json保留；原C0四sanitization及C2/E正负矩阵在完整417继续执行。 |
| 五revision recorder及原58保护 | 在417内通过，旧4精确SHA保持，58→60→58完整signature，MySQL dialect DATETIME(3)/Numeric(30,10)/binary unique/复合FK/default/index同步；不执行SQL。 |
| 真实ASGI/Service/配置/SQL/error/auth矩阵 | 在417内通过：十值/0/precision/raw duplicate/未知/snake/null/bool/string/NaN/Infinity/UTF8/overflow/时区/UTC域；实际JWT无坏过期refresh撤销inactive、role/grant/scope/disabled；事务业务/receipt/flush/commit/未知提交/日志丢响应重放、3次竞争上限/非目标Integrity；SQL scope/recordId/limit/source排序；本应用快照与跨应用配置隔离、helper正例/private-setting负例、JSON Lines脱敏。都是无DB合成Session或SQL编译，不当MySQL持久证明。 |
| `python3 b-final-check.py`最终独立B入口准备 | exit0；最终tests_mysql入口compileall成功，`pytest --noconftest --collect-only -q tests_mysql/test_equipment_temperature.py` **1 collected**，未调用函数；再跑3个no_db migration/normalizer纯边界测试**3 passed**。B-entry-final.log。 |
| `python3 audit.py` | exit0，35路径only delta、433个backend/旧bundle保护文件unchanged、64本地Markdown链接、三example原前缀/69keys/英文空scope、git diff --check及新增patch空白通过。B normalizer expression/normalized AST与BE005最终已验收版本同构，literal大小写/空格/boolean分组、Numeric precision/scale/unsigned、DATETIME fsp负例保留。 |

## 完整no_db快照与最终B入口指纹区别

末次417对应`full-final-exact/backend/`，精确468个backend输入SHA记录于A-final-exact-source-map.json。此后生产源码、no_db测试、Model/migration与稳定说明均零变；**唯一源码差异为独立tests_mysql/test_equipment_temperature.py**，该入口不在默认tests testpaths、从未执行DB。本次只加强其预留B矩阵，另作最终guarded compile/collect和纯函数检查，不冒称417执行了最终B函数。

A快照B文件SHA：08d8199977a1fb2b962ba9f5d99168f6108c482908dc8c646eb24cc94d9e56d7。
最终B文件SHA：98873104d111037239271546d7e91123dd4d22a32f5620851d12b64bd6d7ced9。
差异清单A-to-final-source-differences.json只有该一项。最终组合source-map.json、delta.json/patch与integrity.json在本tasks末次写入后生成，精确SHA交handoff消息/handoff.json，不回写自引用hash。

## B入口准备与未验证gate

B真实MySQL仍未获本任务具体动作批准，未运行，不能以A、stub、SQLite、recorder或offline替代。本入口独立于破坏性conftest，只允许/private/tmp公开BE003/60/e4副本、无.env、起始全空且实际MySQL8.4.6、非root账号。必须显式：

- BE003_MYSQL_SCENARIO=empty|upgrade|rollback。
- TEST_MYSQL_DATABASE=BE003_MYSQL_SCHEMA_ACK=arch_be003_r3_<scenario>；MYSQL_DATABASE必须是不同占位主库。
- BE003_MYSQL_ENDPOINT_ACK=127.0.0.1:<MYSQL_PORT>；MYSQL_HOST必须127.0.0.1。
- BE003_MYSQL_DISPOSABLE_ACK=ARCH-BE-003-r3；TESTING=True、PRIMARY_DATABASE=mysql、mock/runner/三bootstrap=False。
- 其他MYSQL/JWT/settings占位参数由公开环境提供；运行口令只process传递，不写命令、仓库或日志。

获具体批准后才可显式`uv run --offline --frozen --no-sync python -m pytest --noconftest -q tests_mysql/test_equipment_temperature.py`，每场景新空schema：empty先base→e4，upgrade/rollback先base→d2准备合成六User/预置revoked jti/旧温控行及58表校验和，再e4；rollback仅专用副本撤两表回d2再e4。schema反射、原58记录/checksum与旧GET、新十值/0/十位小数/20位整数/UTC毫秒、unique/FK、actor/token/role/scope/disabled、独立session并发、事务失败/未知提交/丢响应精确recordId恢复均已准备源码，**尚无真实结果**。读取role policy采用合成app.state有效grant注入，不宣称修改了真实角色数组。两轮新卷与具体创建/迁移/清理方案由Root另提确认，BE005授权不转移。

MySQL DDL非事务，失败不证明中途DDL自动回滚；downgrade会丢新样本，只供另批可丢弃演练。其他DB方言、现场吞吐/保留期、物理温控、统一前端current和writer切换未验证且不在本任务实施面。

## 正式交接及资源

**Development -> fresh-context QA / Verification：** 精确ARCH-BE-003 r3 A self-check完成，以本tasks、批准spec、35路径delta、当前working tree、417完整日志与source maps独立重建验证；不得把Dev自检当QA。根/模块索引由Root机械同步，B gate与Human Owner最终验收仍pending。当前profile为contract_only，不宣称平台ACL、强制路由或Agent Team activation。

DEV专属资源为`/private/tmp/arch-be003-r3-dev-6diknqm3/`（1511原文件baseline、失败/各次公开副本、guard/payload/脚本、commands、SQL/metadata、完整logs、uv-cache/pycache/pytest产物、source maps/delta/integrity）及`/private/tmp/be003-dev-root`指针。没有listener、浏览器tab、branch/worktree、Docker/DB资源或后台服务待关闭；所有命令已结束。保留本任务非秘密证据供fresh QA，不清理Root B提案、BE005旧证据或AW/Console资源。验收后的安全收尾由协调者盘点。


# r3 收尾解析边界修正（2026-10-16）

Root只读stdlib核对确认：合法JSON科学计数法的极端正/负指数可使Decimal构造抛InvalidOperation；超深JSON可在Schema前抛RecursionError。此前局部json.loads只捕获ValueError/UnicodeError，会错误落内部500；这不改变已批准技术不可表示输入422范围。
本Development仅在temperature_http.py原始解析try内补这两个异常为422，新增三个原始JSON回归。未把它们扩展成全handler系统异常422捕获；内部业务owner/输出校验及非解析系统异常仍500。原417和全部失败/快照保留为当时证据，当前交接等待末次必要复验。


# r3 A最终 Developer handoff（解析修正后，当前）

此节取代上方首次417候选的当前性；其源码、失败及通过历史均保留，不倒写旧结果。唯一收尾生产增量为原始JSON解析try增加InvalidOperation/RecursionError→422，三个真实ASGI回归全部通过；未扩展系统/输出错误422捕获，已批准范围不变。

`python3 /private/tmp/arch-be003-r3-dev-6diknqm3/full.py full-parser-final`实际**exit0，420 passed/30 deselected、315.02s**，同进程全树compileall通过，日志full-parser-final.log，精确payload为full-parser-final-payload.py。仍为完整原no_db，不缩套件、不删原断言；增强DBAPI/SQLite/socket及嵌套uv guard连接尝试日志不存在。数据库/Docker/真实env/服务/PLC/Projection/安装/网络/发布/推送均未执行。

最终A快照为full-parser-final/backend，468个backend输入SHA归A-parser-final-source-map.json，A-parser-final-source-differences.json为空：**当前全部backend生产、no_db测试、最终B入口及稳定文档与此快照逐字相同**。它包含最终B SHA98873104d111037239271546d7e91123dd4d22a32f5620851d12b64bd6d7ced9；compileall编译该入口，完整420中的纯normalizer/migration检查读取它，但从未执行B测试函数。该同一最终B文件此前guarded collect为1项/exit0、纯边界3 passed/exit0，B-entry-final.log保留。

上方417对应的A-final-exact-source-map.json及一项B差异清单是旧候选历史，不代替本节新的零差异最终map。五revision recorder、旧58/旧四迁移保护、C2/E14/15/16、实际offline SQL及heads/history/metadata和三env/doc检查的实现面与最新源码一致；最终audit.py再次核对35路径delta、433保护、64链接、英文69key空scope及git diff --check。末次tasks/delta/patch/source map/evidence SHA统一归handoff.json及交接消息，不回写自引用hash。

**Development -> Root / fresh-context Verification：精确ARCH-BE-003 r3、A self-check完成、developer_handoff。** 当前工作树/HEAD仍1a5aa2d2fe7089b5671218865238cfaa240f9a30，无commit。仅Dev自检，不授QA或Owner验收。B真实MySQL精度/持久化/并发/约束/迁移/回退/58记录保护尚未执行，继续待本任务具体动作批准及独立验证；不能整体qa_passed/owner_accepted。所有自建命令结束，无listener/运行资源；此前列出的DEV临时证据继续保留。


# r3 F-001独立QA失败后的Development返工（2026-10-16）

已完整消费checklist SHA c875a839fdedac666058b0635ade9b245b520ae79eeb12f3f2f9600ee85dec3d、qa-handoff SHA98d9c1e8f57d86a924f860858388e1c10d9868832d1dd8d9aeca41f878f09d9d及12例dependency-exit原始源码/log/results。当前独立verdict仍qa_failed/F-001；上方420、首次developer_handoff及全部失败是历史证据，不表示A通过。QA原文件及DEV顶层handoff/maps/log全部保留不覆写。

返工前建立rework1/entry公开完整快照及entry-files.json（包含Root已同步qa_failed的10索引），只允许新局部adapter、定向API测试及本tasks增量。Root不写代码；Development不写checklist/spec/索引，不自行启动其他角色。数据库（含SQLite）、任何Docker、真实env/listener/网络/安装/PLC/Projection/发布推送继续禁止。

故障为FastAPI0.135.1外层request_response在get_route_handler返回之后退出request/function AsyncExitStack，真实get_db退出commit/rollback/close可能在200已发送后失败。改为本新route每请求在现有try中拥有这两种依赖stack、按function→request顺序完成退出、还原原scope引用后才返回Response；原Core依赖/Service commit均保留。
此方案有意绑定本uv.lock/已安装FastAPI0.135.1的fastapi_inner_astack/fastapi_function_astack约定，不声明这些键是Core公共API。升级框架须重验本合同；仅当前两条有界JSON接口使用，不泛化上传/流式响应/全局middleware或响应SDK。缺失/异常stack环境受控500；typed Business/HTTP/system退出均在局部边界处理，不能被旧全局HTTP200先消费。


# r3 A Developer handoff（F-001返工后，最新）

本节为本次同r3最新Development交接，取代上方420交接的当前性；原420通过、原QA qa_failed/F-001及全部失败/成功证据仍按发生时事实保留，不覆写。独立checklist当前仍qa_failed；是否关闭F-001由另一位fresh Verification决定，Development只记录自检。

## 精确实现与事务结果

本次相对rework1/entry只修改三路径：`backend/app/equipment/api/temperature_http.py`、`backend/tests/test_equipment_temperature_api.py`和本tasks。整体r3仍为原35路径，没有增加allowlist。Core get_db、全局handler/router/deps/settings、Service/CRUD、旧GET、manifest/descriptors、Models/schema/migration/B入口均未改；Root的十机械索引和并行AW/Console材料不归DEV差异。

局部route取得并校验FastAPI两种原stack后，使用每请求局部function/request AsyncExitStack完成依赖；function先退出，request后退出，退出异常与endpoint异常同处现有局部try，finally还原原scope引用后才返回最终Response。缺失/异常框架stack受控500，不补造环境。新63例包括真实get_db的GET/POST×DEBUG两态×成功及exit commit/rollback/close、flush/receipt/Service commit失败、request/function两scope的模块Business/HTTP401/403/422/500/503/DBAPI/系统/未知Core Business以及缺失/坏stack；真实ASGI捕获response.start/body顺序，检查typed脱敏与stack引用恢复。

POST业务commit仍在Service完成。若随后真实get_db exit commit失败返回503，rollback/close系统失败返回500；已提交的业务及receipt不伪装回滚，也不提前发送200。Session只由Python durable lists合成，随后新Session同sampleId恢复同recordId/outcome=duplicate且始终一业务/一receipt；初始业务/receipt flush或Service提交失败仍无持久数据。此为无DB事务路径证据，不冒充MySQL持久化或并发证明。

版本风险已明确：此最小局部适配绑定锁内FastAPI0.135.1的两个scope键，框架升级须重验。只用于当前两条有界JSON路由，不建立全局响应平台，不声称支持流式/上传/任意第三方依赖。未知内部/输出/HTTP500仍500，已知DBAPI/HTTP503为503，认证权限分别401/403，均为局部真实HTTP与稳定errorCode，不泄露SQL/token/异常detail/DEBUG traceback。

## 返工实际检查与证据

本次所有项目行为仍只从DEV专属`/private/tmp/arch-be003-r3-dev-6diknqm3/rework1/`公开源码副本执行，现有uv.lock/.venv、占位settings、无真实.env、mock/runner/bootstrap关闭。guard拒绝SQLAlchemy/DBAPI/SQLite（含dbapi2/_sqlite3）及socket connect/bind/listen，并注入嵌套uv子进程；TESTING=True不作为隔离依据。connection-attempts.jsonl不存在。未运行任何数据库、Docker、真实listener/env/网络/安装/PLC/Projection/发布/推送。

| 实际命令 | 真实结果与完整证据（rework1目录） |
| --- | --- |
| `python3 /private/tmp/arch-be003-r3-dev-6diknqm3/rework1/run.py focused-first` | exit0；API+Service定向 **156 passed/7.94s**，adapter compile成功；focused-first.log与focused-first-payload.py。 |
| `python3 /private/tmp/arch-be003-r3-dev-6diknqm3/rework1/original-repro.py` | exit0；原独立QA 12输入逐个通过DEV修复断言：均先context_exit再response.start，commit=503、rollback/close=500、局部errorCode、无200、无外逸异常；original-repro-results.json/log/payload.py。只在DEV复制件更换结果路径及期望，原QA失败字节不改。此exit0是本次修复断言通过，不把原QA观察缺陷的exit0倒写为PASS。 |
| **`python3 /private/tmp/arch-be003-r3-dev-6diknqm3/rework1/run.py full-final`** | **exit0；完整no_db 483 passed/30 deselected、290.91s；同进程全树compileall成功**；full-final.log/full-final-payload.py和full-final/backend源码副本。保留完整选择条件及原断言，无skip/xfail/缩套件。 |
| `python3 /private/tmp/arch-be003-r3-dev-6diknqm3/rework1/audit.py` | exit0；返工三路径/整体35路径；465 backend/旧bundle受保护输入未变、468 backend输入与full-final副本零差异；64本地链接、git diff --check及新增差异空白通过。旧正式DEV handoff及其19项证据、批准spec、QA final checklist/handoff/manifest和BE005 accepted checklist SHA均保持。 |

完整参数、cwd、exit归rework1/commands.jsonl，完整guard与payload保留。run.py两次实际底层argv为`uv run --offline --frozen --no-sync python -c <guard+payload>`；原QA复制件复验实际底层argv为`uv run --frozen --no-sync python -c <guard+payload>`（无安装、嵌套UV_OFFLINE=1、连接guard），不冒称其argv带--offline。没有在仓库运行项目行为。

完整483包含原420及新增63；既有C2/E14/15/16/helper正负、旧58表/five revision recorder、严格数字/时区/parser边界、auth/config/Service/idempotency/SQL与normalizer纯测试继续执行。此次未改迁移/B入口，未无理由重跑offline CLI或B guarded collect；其原offline/heads/history和最终B compile/1 collected/3纯边界证据保持原SHA，本次全树compile再次编译最终B文件，纯边界亦在483中继续验证。B源码SHA仍98873104d111037239271546d7e91123dd4d22a32f5620851d12b64bd6d7ced9；从未执行B函数。

## 精确交接、限制与资源

新正式证据全部另存rework1：entry-files.json、delta.json/patch（三路径）、overall-delta.json/patch（整体35路径）、source-map.json与full-final-source-map.json（468 backend输入）、full-final-source-differences.json（空）、integrity.json、commands/logs/payload、evidence-sha256.json和handoff.json。完成本tasks后再计算精确SHA，统一通过handoff.json及协调者交接消息锁定，不回写自引用hash。原顶层handoff/maps/patch/420日志及QA失败材料保持，不能将新图谱冒称旧图谱。

**Development -> Root / 另一位fresh-context Verification：ARCH-BE-003 r3 A、F-001返工DEV self-check完成，developer_handoff。** HEAD仍1a5aa2d2fe7089b5671218865238cfaa240f9a30、未commit；以最新tasks、批准spec、原独立失败checklist、rework1三路径及整体35路径diff、锁定源码与真实命令结果独立复验。Development不写checklist、不关闭QA finding、不授Owner验收，不宣称平台ACL或强制路由。

B真实MySQL精度/持久化/并发/约束/迁移/回退/58记录保护仍未执行，继续待Human Owner具体动作批准及独立验证；不能整体qa_passed/owner_accepted。其原guard键/三场景入口合同保持，Root另提具体方案。

本次新增资源仅rework1公开源码/pytest/pycache/uv-cache/证据文件；所有命令已结束，无listener、后台服务、Docker/DB/浏览器/branch/worktree待关闭。保留非秘密证据供fresh QA，旧DEV/QA、Root提案及并行任务资源不清理。


# r3 B具体批准后的Development第一轮（2026-10-16）

本节记录新的具体运行批准，早期“A only/B未授权”文字均保留为当时事实，不继续充当本轮限制。Human Owner明确原话：“批准 BE003 r3 B 两轮验证及专用资源清理”。批准对象为`/private/tmp/arch-be003-r3-b-proposal/operation-proposal.md`，SHA1b94aacc10ed6d60487c5733539de01626d241f0e6bdde88dbcd86e9c311b480；批准收据B-operation-approval.json SHA d41b3d3c2569b59e8a2dc1039042c6d59b7ecbd13a51aaf38d974efdc0e1cafa。本角色已完整消费最新checklist/qa-handoff、spec B gates、提案与批准，继续应用backend-arch及适用references，并加载docker-expert/docker-project-ops核对运行边界。

新的fresh Verification已独立确认A passed、F-001 closed，483 passed/30 deselected及compileall；checklist SHA13c391dca7891adcfc9601f04e79e9b873c2e7d98b7b57d1c8a4667cd4e66aef，qa-handoff SHA aa01abee66b8021a1f8d527dc193c07eb88223670e54678357515cdd26099637。其总体qa_blocked是批准前B未完成的事实，不推断整体验收。

Root独占专用资源创建、启动、清理及secret/公开副本准备；Development只在Root round1就绪后执行既定`python3 /private/tmp/arch-be003-r3-b-proposal/proof.py run --round 1`，不自行重建/清理。项目arch-be003-r3-proof，mysql:8.4.6/linux/arm64，仅127.0.0.1动态端口，be003_proof只访问arch_be003_r3_empty/upgrade/rollback三个专用schema。root仅镜像初始化；不读写原运行.env、既有database-only/其他库/其他Docker资源，不执行共享conftest、SQLite、现场PLC/Projection、安装/锁变更或发布推送。随机口令/连接串/token/完整payload不进入任务材料或输出。

第一轮前DEV建立`/private/tmp/arch-be003-r3-dev-6diknqm3/B-round1/entry`及1536文件公开基线、source-map和input-check。相对A锁定468 backend输入仅Root六个机械索引逐字改变（backend PLAN pair、equipment PLAN pair、equipment plans/README pair），完整before/after归A-to-B-mechanical-indices.json；其他462输入精确相同，没有泛化实现漂移豁免，MySQL入口SHA仍98873104d111037239271546d7e91123dd4d22a32f5620851d12b64bd6d7ced9。B起点source-map SHA f7645097581b869b3ffb5934a7e3eb1f6eec2cdaa8f6865b165af606e2c2c54b。

本轮计划：Root就绪及端点/资源归属确认→独立于conftest的三个场景真实迁移/API/事务/并发/旧58保护→实际结果、source pin、资源清理收据交接。失败时先保留精确脱敏trace/复现及分类报Root，不在公开测试副本静默修到pass；必要修复仍限原allowlist，实质范围变化先回PM。第一轮自检不替代第二轮fresh Verification及Human Owner最终验收。


## B第一轮首次真实失败与窄测试修正

Root提供首卷就绪记录round-1/resources-created.json：container b873c32ced6192c5502ae0a3eca0f77af5587adf45328109eadc117cbae15af1，endpoint127.0.0.1:62047，mysql:8.4.6/linux/arm64、Healthy、专用project/卷/网络标签与0600 secret权限。Development按指定入口实际运行`python3 /private/tmp/arch-be003-r3-b-proposal/proof.py run --round 1`，**exit1**；empty失败后停止，upgrade/rollback未执行。guard实际核对MySQL8.4.6/be003_proof/空schema后，base→e4迁移成功，seed/checksum完成，schema比较在equipment_temperature_samples.equipment_id类型展开处失败，尚未运行API业务矩阵。

原失败为反射`VARCHAR(128) CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN`对Model `VARCHAR(128) COLLATE UTF8MB4_BIN`的字符串不等；并非实测数据/精度/业务路径失败。首次empty.log SHA9a5b0eb460a61bb54b495b7571c24fbdc7d04a8d7b356be3ab071edaef83b8ba、results及迁移/target/checksum/资源记录复制到DEV B-round1/first-failure并建立manifest，原件亦保留，不用后续pass覆写。

只读诊断`python3 /private/tmp/arch-be003-r3-dev-6diknqm3/B-round1/diagnose.py`实际exit0，在该专用schema导出三个ID列及collation元数据：全部charset=utf8mb4/collation=utf8mb4_bin，information_schema.collations确认utf8mb4_bin→utf8mb4。仅此获准元数据，无其他业务库或payload；diagnose.log/payload/command保留。已通知Root不再需要失败卷，只有Root清理/重建。

因此仅在已批准B入口normalized()折叠确切`CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN`为`COLLATE UTF8MB4_BIN`，不泛化删charset/collation；原类型比较仍保留Numeric precision/scale/unsigned、DATETIME fsp、长度，SQL字面大小写/内部空格/boolean分组也保持。迁移纯测试补显式不同LATIN1/UTF8MB3 charset、不同collation、没有collation的显式charset和不同VARCHAR长度负例。与BE005 normalized AST的差别只有这个本任务新类型的确切等价适配，不修改BE005或弱化旧58表比较。

`python3 /private/tmp/arch-be003-r3-dev-6diknqm3/B-round1/b-normalizer-check.py`实际exit0：入口compile成功，`pytest --noconftest --collect-only -q tests_mysql/test_equipment_temperature.py`为1 collected（函数未执行），完整本任务migration/normalizer no_db为3 passed/0.35s；底层uv --offline --frozen --no-sync、公开tmp、连接拒绝guard，连接尝试日志不存在。B-entry-final.log/payload和commands.jsonl保留。生产源码未变，故不无理由重跑483；新测试及入口SHA交Root，待新空卷再次真实执行。

Root准备阶段另一次preflight发现A 468 map不列.python-version但fixture公开副本含该文件；Root仅在tmp proof.py允许profile.json和精确3.13 selector SHA02e735b3dfe1c32833eb550b7ff8ffa17f5f2bc3fa1e7bae61a8f5a3883ce398，旧失败副本/脚本及prepare-preflight-correction.json保留，生产/测试未被该辅助修正改变。本轮DEV执行时proof.py SHA f8d57f02ecae349ab6577d771faf53df15aefd7604dfd989b73e8bd26565cebb。

Root已对首次失败专用资源严格核对同containerID、卷创建时间、networkID后执行限定compose down --volumes --remove-orphans及assert-absent，均exit0。首次round-1整个目录现保留为`/private/tmp/arch-be003-r3-b-proposal/round-1-attempt-1-failed/`，上文首次round-1路径均指该保留件；原失败empty.log/results/资源receipt及cleanup.json均未丢弃。cleanup收据SHA 0e506455969d3373f11f0c94cd09af944ab979fdb912bbdbd38d51bdbb1b001a，DEV另存first-attempt-cleanup.json。第一轮重试必须新空卷，不能对已有迁移/seed残留复跑。


## B第一轮第二次尝试：业务矩阵通过，在线回退CLI参数失败

Root以新空卷准备attempt2，container4c29fa105b545b87ad6560b48e5891ec68eaa9fb3d8039afe4d144c5981b292c、endpoint127.0.0.1:63178，均不同首次失败；三个公开副本468输入逐字匹配normalizer-source-map SHA0055b72fa3a8824de458b0f7d25f759d8d2595351712472e76ff400f92953c76。DEV实际再次执行指定proof.py run --round 1，整轮exit1：empty **1 passed/12.66s**，upgrade **1 passed/13.71s**；rollback通过到e4迁移、60表反射和全部真实API/事务/并发/旧58 checksum业务矩阵后，在在线Alembic downgrade命令处exit255。输出为`FAILED: Range revision not allowed`，没有执行downgrade DDL，整轮不能算通过。

原因是B测试调用将仅offline适用的revision range e4:d2传给在线CLI。本Development先保留全部脱敏trace/命令/结果/三个behavior/reflection/checksum/资源记录并报告Root，不在测试副本静默修到pass；DEV另存B-round1/second-failure及manifest。生产migration完全不改，只把B入口该一调用改为在线单目标`target.migrate("d2f4a6b8c0e2","downgrade")`，保留回退仅剩旧58表、checksum和再升级全部原断言。

`python3 /private/tmp/arch-be003-r3-dev-6diknqm3/B-round1/b-online-check.py`实际exit0，最终入口compile成功、guarded --noconftest collect=1，相关migration/normalizer纯测试3 passed/0.20s；B-entry-online-final.log/payload/commands保留，不覆盖首次定向结果。未为CLI参数添加镜像断言，未无依据重跑483。最终B入口SHA099c5cca10460e1818a5fe8db15e972c39f348d821927ef0ad2d8a7a2221766b；online-source-map.json SHA3ab094effd787916705c98eb3ed3b3012fa1e7e6deea97920bc32e4c6894f5c4，相对normalizer map仅B入口该行变化；生产/其他测试无变。等待Root严格归属cleanup后再次新空卷跑完整三个场景。

Root已对attempt2同ID资源严格核对后限定down --volumes/--remove-orphans与assert-absent均exit0；原整轮保留为`/private/tmp/arch-be003-r3-b-proposal/round-1-attempt-2-failed/`，上文attempt2的round-1相对路径现指该保留件。cleanup收据SHA 87eb2ba4913cb956035584a5148a5216a1c546d3319b358bbabd2df15b1d7645，DEV另存second-attempt-cleanup.json；两次失败真实结果全部保留。


# r3 B第一轮最终 Developer handoff（最新，2026-10-16）

本节是最新同r3 Development交接。A独立passed/F-001 closed保持；B已获具体批准，Development第一轮通过，fresh Verification第二轮尚未执行，Human Owner最终验收pending。首次A失败、420/483及两次B真实失败完整保留，不改写历史。

## 最终源码与实际命令

相对本轮1536文件B入口基线，仅两测试文件和本tasks变化：tests_mysql/test_equipment_temperature.py的确切charset等价适配及online downgrade单目标，tests/test_equipment_temperature_migration.py的等价正例/不等价负例。生产/Model/migration/Core/旧路径/依赖/lock全不变。整体r3仍原35路径；Root十索引及并行AW/Console保持。

最终B入口SHA099c5cca10460e1818a5fe8db15e972c39f348d821927ef0ad2d8a7a2221766b，纯migration测试SHAe3df459549089614365d712991855408db286d39394044f9fc7b1b4368059ce4。三成功副本均BE003/60/e4f6a8b0c2d4，468 backend输入逐字相同；初始A map到B仅六Root索引加这两测试增量，逐路径before/after可查，不能豁免任何生产漂移。公开copy额外profile.json和精确3.13 .python-version selector分别为声明元数据/已核对工具链，不冒称在468原map内。

A完整483/30及独立QA为上述两测试窄修前的真实结果，不冒称执行过最终B文件；本轮最终compile/guarded collect与相关3 no_db的必要复验如上，未缩原断言或无依据重跑全套。最新final-source-map、三副本map、delta/patch（B增量三路径）与overall-delta/patch（整体35）在本tasks写入后计算精确SHA，统一锁定handoff.json/交接消息，不回写自引用hash。

Root以第三个全新空卷准备成功轮：container eecebb312432ac9b36b035a50d4a72ae5e6fade5d9189993767fc2c46a200dd3，endpoint127.0.0.1:64261，mysql:8.4.6/linux/arm64/Healthy。proof.py SHAa316f9f2b6e873253f86f6608eb56f0d81d0583c6ceb41ef1b8884e75081809c。DEV实际第三次执行`python3 /private/tmp/arch-be003-r3-b-proposal/proof.py run --round 1`，**整轮exit0**；每场景实际底层为`uv run --offline --frozen --no-sync python -m pytest --noconftest -q tests_mysql/test_equipment_temperature.py`，cwd仅相应/private/tmp公开副本。没有调用共享conftest或仓库普通全套pytest。

| 成功场景 | 真实结果 | 迁移与保护 |
| --- | --- | --- |
| empty / arch_be003_r3_empty | **1 passed/12.62s，exit0** | 空schema base→e4；60业务表完整反射；旧58 checksum三快照相同；真实业务矩阵通过。 |
| upgrade / arch_be003_r3_upgrade | **1 passed/13.70s，exit0** | base→d2，合成旧记录，再→e4；60表反射、旧58 checksum三快照相同；真实业务矩阵通过。 |
| rollback / arch_be003_r3_rollback | **1 passed/18.37s，exit0** | base→d2+合成旧记录→e4，真实业务矩阵后在线downgrade单目标d2仅去两表，再upgrade e4；五checksum快照保持原58，最终60表反射通过。 |

三个schema实际均MySQL8.4.6、be003_proof@%，开始为空；不采用root业务连接，不创建其他schema。详细argv及脱敏输出在各profile/migration-commands.jsonl，每条在线迁移均exit0。MySQL DDL非事务，本结果不宣称中途DDL自动回滚；专用rollback确实删除本增量合成观测，两次再建表的语义不扩为已投运回退策略。

## 真实B证据覆盖与边界

每场景完整SQLAlchemy反射逐表比对60表列顺序/类型/精度/fsp/null/default、PK/FK及动作、unique、check表达式和index；原58记录checksum在迁移/API/回退相应阶段逐字保持。合成旧记录具体为六User、一旧equipment_temperature行和一撤销jti，其他旧表保持空且全部58仍参与checksum；不声称58表每表均有非空seed。旧温控GET完整data前后保持，新GET只读取新表。

真实ASGI不启动listener，使用真实JWT认证、API/Schema/Service/CRUD及独立真实AsyncSession；仅以显式依赖覆盖把Session factory绑定专用schema，模块配置固定合成scope，不使用mock数据或替换业务实现。全部十数值（含0、十位小数、20位整数）POST→按recordId GET逐项一致，UTC毫秒/等价时区与database UTC createdAt读回通过。同投递、不同sampleId/actor、刷新token、sampleId/time两冲突、同小时不同毫秒/晚到保存、实际limit/来源排序/空态/scope边界均通过。

四组首次竞争由asyncio.gather发起各自独立Session：同投递同/异payload、不同投递同业务键同/异payload，验证200/200或200/409、单样本、精确receipt增量及recordId一致。数据库实际拒绝重复业务unique、重复receipt unique与跨设备引用FK；Case/case两receipt及业务设备大小写不同的两行实际共存。直接第二设备插入只证明schema case-sensitive，不开放API第二scope。

业务insert、receipt、flush、commit各故障注入均没有新增持久行；真实已提交未知结果503、已提交后日志/响应500分别同sampleId重试恢复，不多写。每场景业务矩阵结束counts为10 sample/14 receipt，初始recordId=1；rollback场景该counts是回退前证据，不冒称回退后观测仍保存。无/坏/过期/refresh/撤销/inactive身份401、read/ingest/admin/角色/grant矩阵、空或跨scope403及重组disabled旧新整组404通过；不改真实用户/角色策略/运行grants。

上述B结果仍是Development self-check；另一位fresh Verification必须消费精确最终源码、保留失败及修正diff，在第二个获批独立新卷重复真实三场景，不能复制本轮pass当自己的验证。A独立QA历史保持，是否整体qa_passed由该角色判断；不授予Owner验收、部署、发布或现场writer切换。

## 资源、证据与交接

Root已对成功attempt3的同containerID、卷创建时间、networkID再次核对归属，限定compose down --volumes --remove-orphans和assert-absent均exit0；在第一轮cleanup检查时本project容器/卷/网络均不存在；这是该清理时点事实。成功round-1目录保持，cleanup收据SHA 61b5161e9df2244da39376b4876a7a144db9dcbc9268fa1f82f9ca9147d5b3b4，DEV另存successful-evidence/cleanup.json。两0600口令仅由Root为获批第二轮暂留，末轮后由Root删除；DEV不打印、复制或清理秘密。

原成功证据位于`/private/tmp/arch-be003-r3-b-proposal/round-1/`；DEV另存`/private/tmp/arch-be003-r3-dev-6diknqm3/B-round1/successful-evidence/`及successful-results-summary.json。前两次失败Root保留完整目录round-1-attempt-1-failed/round-1-attempt-2-failed，DEV保留first-failure/second-failure、诊断、两次窄纯检查及cleanup收据；资源均已清理，证据不丢弃。DEV B-round1的actual-run-history、commands、input/preflight、source/delta/patch、audit/integrity和新的handoff/evidence manifest锁定本轮。

`python3 /private/tmp/arch-be003-r3-dev-6diknqm3/B-round1/audit.py`实际exit0：三路径/整体35有限增量、465 backend/旧bundle保护输入、468源码与三成功副本、所有58 checksum/60反射、64本地链接、git diff --check/新增行空白，以及原DEV两次正式handoff与全部旧QA证据hash保持。初始stdlib预检一次括号SyntaxError发生在任何项目动作前，已校正后零副作用预检通过；不计为项目结果，也不隐瞒为pass。

**Development -> Root / fresh-context Verification：ARCH-BE-003 r3，A已独立通过，B第一轮Developer handoff。** HEAD仍1a5aa2d2fe7089b5671218865238cfaa240f9a30，未commit；以批准spec/具体B receipt、本tasks、A独立checklist、最终source-map、三路径B增量与整体35路径diff、两次真实失败和最终三场景exit0及cleanup独立复验。只改自己权威面，不写spec/checklist/Root索引，不宣称平台ACL、强制路由。

所有DEV命令结束，无DEV listener/后台服务/浏览器/branch/worktree；第一轮DB/Docker资源已Root清理，DEV仅保留公开源码/证据/cache。没有真实env/既有database-only/其他库或SQLite/现场PLC/Projection、依赖安装/lock修改、应用镜像build、全局prune或发布推送。获批具体MySQL验证及专用资源动作不等于运行采用。


交接收尾期间Root已在第一轮完全清理后另建第二轮专用新卷，尚未运行第二轮测试，等待fresh Verification。第二轮container d80796f3b0879bcf212b94fb8b208602ff3f005bef92d299bcdf35f8499d55b4、endpoint127.0.0.1:49654；round-2/resources-created.json及two-round-resource-separation.json核对container/network ID与volume CreatedAt均不同。此资源属于Root协调的待QA第二轮，不能把第一轮已清理收据扩大为交接时整个project仍无资源；DEV没有创建或使用第二轮资源。Root负责QA结束后的专用cleanup/secret删除。
