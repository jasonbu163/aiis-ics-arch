Task ID: ARCH-BE-003
Revision: r3
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: A与获批B均独立通过；F-001 closed、B-001 closed；两轮各三场景真实MySQL及专用资源清理已验证；交Human Owner最终验收，owner acceptance pending

# 当前独立验证报告：r3 最终源码与 B 第二轮（2026-10-16）

**当前 verdict 为 `qa_passed`，A=passed、B=passed，F-001=closed、B-001=closed。Human Owner final acceptance 仍为 pending。**
本报告由新的 fresh-context `verification` 角色 `/root/be003_r3_b_verification` 在最终 Development B handoff 后独立形成。
完整消费根 AGENTS、README/PLAN pair、canonical workflow、verification.toml、完整任务三文件、最近 backend/app/equipment README/PLAN pair、实现、有限 diff 与可用测试输出；没有继承 Development 对话推理，没有将 Development 第一轮 pass 复制为本轮执行结果。
只写本 checklist 与自有 `/private/tmp/arch-be003-r3-qab-verify-czudc7x0/` 公开证据，没有修改 spec、tasks、实现、测试、配置、索引或并行 AW/Console 工作。
使用 project-governance、backend-arch 及 RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/DATA_GOVERNANCE/OPERATIONS_TESTING、aiis/CONTRACTS、i18n-workflow、code-document-indexer、docker-expert 与 docker-project-ops，仅作验证。
没有 UI、Worker、打包、后端脚本、根 tools、Rust 或 PLC 映射变更，不扩大对应 skill/实现范围。
TOML 的 `gpt-6.1-sol`/`max` 是配置证据，不独立确认不可观测运行参数；本 profile 为 `contract_only`，fresh context、串行 handoff、角色文档与 diff/checklist 审计是控制，不宣称平台 ACL、强制路由或 Agent Team activation。

## 精确批准、输入与历史

Human Owner 最初批准精确 r3 的 A 源码阶段，并要求数据库/Docker 等源码检查通过后再确认。
A 独立通过、F-001 关闭后，Human Owner 明确答复：**“批准 BE003 r3 B 两轮验证及专用资源清理”**。
本轮据该具体批准执行 BE003 自己的隔离目标；没有沿用 BE005 授权。
operation-proposal.md 保持批准前方案快照；其“未执行/待批准”是形成时事实，当前运行事实以批准收据、Development 最新 tasks 和实际执行/清理收据为准。

| 已独立核对输入 | SHA256 / 标识 |
| --- | --- |
| owner_approved spec | `6192f862ab24dbf44eb76d1d4d6fe6833a2103a891935c983412821633c4c73b` |
| 最终 developer_handoff tasks | `cfcb940cf4cc7c54831b59d6cedb0236b3f160cc8e2839eca6eb67587fe16cac` |
| Development B-round1/handoff.json | `6ec31898c577413cc59abf2b466a050de985f8031059564fba09d3b745ef6536` |
| final/online source map，468 backend 文件 | `3ab094effd787916705c98eb3ed3b3012fa1e7e6deea97920bc32e4c6894f5c4` |
| 当前 MySQL 入口 | `099c5cca10460e1818a5fe8db15e972c39f348d821927ef0ad2d8a7a2221766b` |
| 当前 pure migration/normalizer 测试 | `e3df459549089614365d712991855408db286d39394044f9fc7b1b4368059ce4` |
| B-operation-approval.json | `d41b3d3c2569b59e8a2dc1039042c6d59b7ecbd13a51aaf38d974efdc0e1cafa` |
| operation-proposal.md | `1b94aacc10ed6d60487c5733539de01626d241f0e6bdde88dbcd86e9c311b480` |
| 本轮实际 proof.py | `a316f9f2b6e873253f86f6608eb56f0d81d0583c6ceb41ef1b8884e75081809c` |
| 原 A 独立 checklist（下方完整保留） | `13c391dca7891adcfc9601f04e79e9b873c2e7d98b7b57d1c8a4667cd4e66aef` |
| A 独立 qa-handoff.json | `aa01abee66b8021a1f8d527dc193c07eb88223670e54678357515cdd26099637` |
| HEAD / C0 | `1a5aa2d2fe7089b5671218865238cfaa240f9a30` / `363b297bffe65e020108f5504766b4fb1ec3b381` |

本轮保存原 13c checklist 全文为 `checklist-before.md`，并将其**完整原字节作为本文件后缀保留**；其中原 c875 `qa_failed`/12 例反例继续完整保留。
旧 A 420/483、F-001 失败及关闭、B 两次失败与最终第一轮通过均按发生时事实保留，不倒写为本轮结果。
独立验 hash 的历史 manifest 共 232 项：原 DEV19、返工 DEV26、首次失败 QA34、A 返工 QA51、B DEV102。
原 C0/C2/E14/15/16、58→60→58、offline upgrade/downgrade、单 root/head、65 例独立生命周期与原12输入复验可复用部分已验历史 hash及相关输入未变；不宣称这些额外探针在本轮重新运行。

## 当前源码复建与独立 A 命令

QA 新建 `source/backend/`，逐项复制当前 468 文件 map；另复制 214 个公开 frontend 文件供既有合同测试读取，未读取/复制真实 env。
profile 为 BE003 / 60 / e4f6a8b0c2d4，额外 profile.json 与精确 Python3.13 selector 是明确元数据/工具链，不冒称属于原468 map。
复用仓库已存在 `.venv`、pyproject.toml、uv.lock；Python3.13.3、Darwin24.6.0 arm64、pytest9.0.2、SQLAlchemy2.0.48、FastAPI0.135.1、Pydantic2.12.5、Alembic1.18.4。
公开占位环境为 MySQL127.0.0.1:1、不同 primary/test fixture 名、TESTING=True、mock/Projection/三bootstrap=False、role grants=[]、空scope。
TESTING 不作为隔离保证；guard 拒绝 SQLAlchemy/DBAPI/SQLite（含 dbapi2/_sqlite3）、socket connect/bind/listen、真实 env 打开与未授权 subprocess，并前置到嵌套 uv。

| 本轮实际命令 | 结果与证据 |
| --- | --- |
| `python3 <QA>/runner.py guard-controls <QA>/guard-controls.py` | exit0，13项动作前拒绝正控和 nested uv guard 确认；正控无实际数据库/网络/真实env/Docker执行 |
| `python3 <QA>/runner.py full-current <QA>/full.py` | **exit0，全树 compileall 通过，完整 `pytest -q -m no_db` 为 483 passed / 30 deselected，308.95s；runner312.329s** |
| `python3 <QA>/audit.py` | 修正自有 patch 排序假设后 exit0；35整体/3 Bdelta重建一致，当前468源码零漂移、保护与历史证据审计通过，22文档287相对链接通过（写本报告前） |

上述 runner 的实际底层 argv 为 `uv run --offline --frozen --no-sync python -c <guard + payload>`；完整 argv/cwd/公开环境/退出码/时长/payload SHA 在 commands.jsonl。
当前 no_db 483 使用最终两测试文件，包含新字符集等价正例和五个不等价负例，以及原模块/迁移/价格/Projection 回归；未缩选择、删断言、skip或xfail。
最终 B 函数由下面的独立实库命令执行，不能把默认 no_db 当作执行过实库入口。
`forbidden-attempts.jsonl` 不存在；主动正控日志独立存放。所有 cache/pycache/pytest/logs 只落 QA 临时目录。
原 A 完整483是 B 窄修前输入的真实历史；本轮完整483是当前最终输入的新独立结果，两者不混用。

## B 第二轮真实执行、资源与迁移

第二轮由 Root 准备全新卷，QA 在操作前独立逐文件核对三个公开副本的468文件，以及实时 Docker context、精确 container ID、healthy、卷 CreatedAt/归属与 network ID。
本轮只访问获批三个 schema，实际 `DATABASE()`/`VERSION()`/`CURRENT_USER()` 均为预期 schema、8.4.6、`be003_proof@%`，每个场景在任何迁移前执行全空 guard。
账号仅限三个 schema，root 只用于镜像初始化；主库名 `be003_unused_primary` 是未创建/未授权占位值。

| 隔离轮次 | 精确资源 |
| --- | --- |
| Development 成功第一轮 | container `eecebb312432ac9b36b035a50d4a72ae5e6fade5d9189993767fc2c46a200dd3`，127.0.0.1:64261；该轮结束后已清理 |
| QA 第二轮 | container `d80796f3b0879bcf212b94fb8b208602ff3f005bef92d299bcdf35f8499d55b4`，127.0.0.1:49654；network `27eec865b5656a1f53fc754ca81eb9c63e625fcd75deba05c5155566840273cd`；卷CreatedAt `2026-10-16T11:23:10Z` |

两轮 container/network ID 与卷 CreatedAt 均不同，image 固定 mysql:8.4.6 / linux/arm64，project 固定 arch-be003-r3-proof，只有 loopback 动态端口。
QA 实际执行 **`python3 /private/tmp/arch-be003-r3-b-proposal/proof.py run --round 2`，整轮 exit0**。
每场景底层为 `uv run --offline --frozen --no-sync python -m pytest --noconftest -q tests_mysql/test_equipment_temperature.py`，cwd 仅相应公开副本，逐库/schema/endpoint/disposable ACK 均显式匹配；不进入共享破坏性 conftest。
资源只读核对、该获批 B 命令及末次缺省查询使用 require_escalated；不存在批准拒绝或绕过 guard。

| 场景 / schema | QA 第二轮结果 | 实际在线 Alembic 与原58保护 |
| --- | --- | --- |
| empty / arch_be003_r3_empty | **1 passed/12.31s，exit0** | base→e4；60表反射；3个旧58 checksum快照一致 |
| upgrade / arch_be003_r3_upgrade | **1 passed/13.69s，exit0** | base→d2，合成旧记录，再→e4；60表反射；3个checksum快照一致 |
| rollback / arch_be003_r3_rollback | **1 passed/18.55s，exit0** | base→d2+合成旧记录→e4→在线downgrade d2→e4；仅撤两新表；5个checksum快照一致、最终60表反射通过 |

各在线迁移实际 argv 为项目 Python 的 `-m alembic upgrade|downgrade <单目标revision>`，exit0及MySQLImpl输出保存在 migration-commands.jsonl。
第一轮原日志独立审计确认为12.62/13.70/18.37s，各exit0；这些是 Development 结果，本轮实际重复执行了三场景。
两轮各场景反射逐表列顺序/类型/precision/fsp/null/default、PK、FK及动作、unique、check表达式、显式index；报告的60表比较内容在两轮逐项一致。
MySQL类型精度/fsp在执行时按MySQL dialect编译比较，不把通用 `str(DATETIME)` 的报告显示当作fsp缺失。
全部58旧表均参与checksum；非空合成旧数据仅六User、一旧温控行、一撤销jti，其他55表为空也受保护，不声称58表逐表非空seed。

真实 ASGI 未启动 listener，业务 API/Schema/Service/CRUD、JWT、真实独立 AsyncSession 均执行；依赖覆盖仅绑定该专用 Session factory 和合成唯一scope，角色有效grant为合成app.state注入，不是改真实配置。
完整十值含0、十位小数、20位整数逐项 POST→按 recordId GET相等，UTC毫秒及等价时区保持；createdAt来自数据库UTC。
同投递重放、同id异内容优先409、不同id/actor同业务键同/异内容、刷新access token、同小时不同毫秒、晚到排序、实际limit=1/recordId空态均通过。
四组 `asyncio.gather` 首次竞争各自产生独立Session，覆盖同投递/不同投递×同/异payload；结果200/200或200/409、单样本与精确receipt增量及recordId一致。
真实数据库拒绝两个业务/投递unique重复及跨设备复合FK；Case/case receipt与大小写不同设备键可分别保存，API仍只开放一个设备scope。
业务insert、receipt、flush、commit注入失败均无新增持久行；真实已提交未知结果503及已提交后日志/响应500的同键重试恢复原recordId，无多写。
每场景业务矩阵结束均10 sample/14 receipt；rollback的该计数是**回退前**证据，随后downgrade有意删除两新增表中的合成观测。
旧温控GET完整data保持；新GET只读新表。无/坏/过期/refresh/撤销/inactive身份401，独立read/ingest/非admin拒写、空/跨scope403、disabled重组新旧整组404均通过。

## 两次 B 失败与窄修审计

首次失败仅在反射比较器：显式 `CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN` 对隐含同一charset的 `COLLATE UTF8MB4_BIN` 字符串不等。
保留的元数据诊断及本轮实际反射确认同一charset/collation；修正仅折叠这一个确切pair，不删除通用charset/collation/长度或precision/fsp。
新纯测试保留原 literal大小写/内部空格/boolean分组、Numeric precision/scale/unsigned、DATETIME fsp等边界，并增加五个不同charset/collation/无collation/长度负例；当前完整483实际执行通过。
第二次尝试 empty/upgrade通过，但在线downgrade使用offline range `e4:d2` 导致CLI255且DDL前停止；整个该轮仍为失败。
修正只把在线调用改为单目标d2；仅去新两表、旧58 checksum及再upgrade原断言保持，本轮真正执行在线回退并通过。
两次失败原件仍在 round-1-attempt-1-failed/ 与 round-1-attempt-2-failed/，Development另有独立保留件与manifest，均验hash；原失败资源已清理。
生产/Model/migration/Core没有因这两次失败改变；A→最终backend map精确只有六Root索引与两测试变化，不泛化为源码漂移豁免。

## 范围、兼容与 AC 审计

独立从原1511 baseline重建整体35路径patch、从B1536 entry重建三路径patch，均与最终Dev patch字节相等。
原429个受保护backend输入及B-entry中473个backend/旧任务输入保持；当前468map与QA副本及B三个副本保持。
Core/get_db/Settings/private-setting规则/engine/locks、原四迁移、旧三GET/Models/Services/CRUD、八个本地descriptor、Projection business+cursor+audit、原测试与前端来源均受保护。
PUBLIC_SYMBOLS仅增加现存resolve_env_file；现有module contract测试只追加helper正例/private-setting负例，fixture仅增加profile元数据和tmp cache路由，原C0/C2/E及DB refusal guard字节保持。
三public example原68key前缀/值/grants、11英文标题全留，仅加空scope为69；双语README的69key表对称，设备文档、合同、CODE_INDEX和任务相对链接通过；git diff --check exit0。
本轮自有审计首轮仅因B patch路径排序假设exit1，保留audit-first.py/log；按原patch顺序独立重建后exit0，没有修项目文件。

| 验收标准 | 独立结果与证据口径 |
| --- | --- |
| AC-001 / 旧新归属 | passed；源码/旧GET limit/8descriptor兼容保护，B旧58与旧GET前后保持，新表不union/双写/伪造PLC来源 |
| AC-002 / 严格完整样本 | passed；当前完整ASGI no_db验证严格JSON/数值/时间边界，B真实十值/0/精度/UTC毫秒POST→GET |
| AC-003 / 持久幂等与并发 | passed；两个unique、actor/token及两类409、真实独立Session四组首次竞争/recordId/receipt条数均通过 |
| AC-004 / 逐样本读回 | passed；同小时不同毫秒/晚到各保存、scope先于recordId、实际SQL limit/来源排序、空态；旧current独立 |
| AC-005 / 事务与失败恢复 | passed；Service commit/rollback、CRUD不提交、async无同步DB，B失败原子性及未知提交/丢响应恢复，F-001关闭事实保持 |
| AC-006 / 显式迁移 | passed；五接链/单head/旧四字节/58→60→58与Model/offline历史保持；B空库/d2升级/在线回退再升级、60完整反射/58记录保护 |
| AC-007 / 认证权限scope | passed；真实JWT身份401、admin写/独立read/grant、所有caller设备scope及disabled404矩阵；user与真实grants未改 |
| AC-008 / 本地配置公共入口 | passed；只加helper、路径/优先级/懒固定每app隔离/private-setting负例及三空scope例/双语69key说明通过 |
| AC-009 / 局部HTTP安全 | passed；仅新GET/POST用TemperatureRoute，局部401/403/409/422/500/503及DEBUG脱敏；当前完整套件继续执行真实get_db退出回归，旧全局HTTP200保持 |
| AC-010 / 独立交付 | passed；当前483/30+compile、有限diff/links/历史hash，两轮真实B各三场景及专用清理完成；Owner最终验收独立pending |

## 限制、清理与 Human Owner handoff

F-001保持closed：当前局部adapter源码与A独立65例/原12输入复验时逐字相同，本轮完整483再次覆盖63个真实get_db退出回归。
B使用专用Session依赖覆盖；不将此覆盖宣称成重新运行了A的原65额外探针或真实Core get_db故障注入。
方案绑定锁内FastAPI0.135.1的fastapi_inner_astack/fastapi_function_astack，框架升级须重验；仅限新两条有界JSON接口，不宣称任意上传/流式/第三方依赖支持。
证据限MySQL8.4.6/linux arm64与合成数据，不覆盖其他DB/架构、现场吞吐/长稳、保留期、物理温控正确性、前端统一或writer切换。
MySQL DDL非事务；本轮通过不证明中途DDL自动回滚，已投运观测默认回退仍应关闭新入口并保留数据，不能直接采用本演练的drop。

Root在QA命令结束后重新核对same container ID/卷creation/network ID，限定project执行compose down --volumes --remove-orphans与assert-absent均exit0，随后仅删除两0600 regular非symlink secret。
QA独立核对 round-2/cleanup.json SHA **`9c8df824f6d2cdd96e9aa39b8c157e5e53add261b6fcd0b6654a384881f22fca`**、final-cleanup.json及两个secret path确实不存在；没有打印或复制口令。
QA再实际执行 `python3 /private/tmp/arch-be003-r3-b-proposal/proof.py assert-absent`，exit0，确认本project容器/卷/网络均不存在。
QA没有创建、重建或清理资源；全部命令结束，无QA listener/后台服务/浏览器/branch/worktree待关闭。
保留QA目录、原DEV/A/失败QA、两轮成功/两次失败公开证据供最终验收，不回收仍承担证据作用的临时文件。
未读写真实env/既有database-only/其他数据库/SQLite/PLC/Projection/listener，未安装依赖、修改lock、build应用镜像、全局prune、发布/部署/Git refs/push。

| 验收层次 | 当前事实 / 下一gate |
| --- | --- |
| 已验证范围 | A与获批B均passed；F-001与B-001closed；两轮三场景及专用清理已完成 |
| 当前实现 blocker | 无；本轮没有新增 implementation failure需交Development返工 |
| 保留兼容路径 | 旧温控表/三GET/前端来源及本地Projection writer继续保留，新HTTP观测不自动进入旧页面 |
| 范围外后续 | 生产/现场采用、真实数据/设备、保留期/吞吐、前端与writer统一、发布部署仍另立任务和具体操作批准 |
| Human Owner final acceptance | **pending**；QA不授予或推断owner_accepted |

**QA -> Human Owner：精确 ARCH-BE-003 r3 `qa_passed`，请按本checklist及已保留证据进行最终验收。**
Root可在本verdict成立后机械同步十索引；该同步不是QA修改或新的实现授权，六backend索引仍须逐路径记录，不能扩大漂移豁免。
完整命令/公开源码map/独立patch、two-round-results-audit、反射/校验和/迁移收据、history integrity、失败脚本/日志和cleanup收据都保存在QA目录；关键要求、结果、边界已落本checklist，临时目录不是唯一结论依据。
最终 qa-handoff.json 与 evidence-sha256.json 锁定本checklist/source-map/证据hash；不向本文件写自引用SHA。

---

# 前一轮 A 独立报告完整原文（13c 原字节，含 c875 失败历史）

以下全文仅为发生时历史；其中“B未批准/未执行”“qa_blocked”等当前性已由上方新报告替代，原文逐字保留。


Task ID: ARCH-BE-003
Revision: r3
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: F-001返工经另一位fresh Verification独立复验关闭；r3 A=passed，总体qa_blocked；B专用MySQL具体动作批准及两轮独立验证未完成，交Human Owner确认下一运行gate；最终验收pending

# 当前独立验证报告：r3 A / F-001返工（2026-10-16）

**当前verdict为`qa_blocked`，A=passed，F-001=closed；B未授权、未执行、未验证。**
本报告消费最新Development返工交接，取代下方首轮报告的当前性；下方原`qa_failed`全文逐字保留，
其420通过与12例失败仍是发生时的真实历史，不倒写为pass。QA通过不授予Human Owner最终验收或运行权限。

本轮为实际`verification`角色`/root/be003_r3_a_rework_verification`的新fresh context；不继承Development对话推理。
独立完整阅读根AGENTS、README/PLAN pair、canonical workflow、verification.toml、本任务完整三文件、
最近backend/app/equipment README/PLAN、实现、35路径diff/三路径返工diff及可用原始证据。
使用project-governance、backend-arch及RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/
MODULE_REGISTRATION/AUTH_SECURITY/DATA_GOVERNANCE/OPERATIONS_TESTING、aiis/CONTRACTS、
i18n-workflow和code-document-indexer，仅用于验证。无前端、脚本、Rust或Docker实施面，不加载其专用skill。
TOML声明`gpt-6.1-sol`/`max`只是配置证据；不据此确认不可观测的运行参数。
本profile为`contract_only`，以fresh调用、串行handoff、角色文件归属及diff/checklist审计控制，不宣称平台ACL、强制路由或Agent Team activation。

## 精确输入与起点

Human Owner原话：“BE005 r3 验收通过，批准 BE003 r3，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
本轮仅写本checklist与自有`/private/tmp`证据；没有修改spec、tasks、实现、测试、配置或索引，没有静默修复。

| 已独立核对输入 | SHA256 / 标识 |
| --- | --- |
| owner_approved spec | `6192f862ab24dbf44eb76d1d4d6fe6833a2103a891935c983412821633c4c73b` |
| 最新 developer_handoff tasks | `e44ba6893ae88b6c8d1a5ecf6e651f77527189ae69585765d81f778cbad81d91` |
| DEV rework1/handoff.json | `db5aab3fbbe9ee7bc8063dc9418de8d91991145352bc103e4de5c14a423f4c34` |
| DEV rework1/source-map.json，468输入 | `0e6904e02447a71c6be74d1a027f25bc46904094d6cf92164aa6961c9e25b83c` |
| DEV rework1/delta.json，三路径 | `27f006bb89218ff411b95848ae2300f281e4cb4d4b2b677ae0612e792f54366d` |
| DEV rework1/overall-delta.json，35路径 | `d0997f0d72ce17f4f01329d3957ef8661037861cb35ad5baa624df40394796a2` |
| 首轮qa_failed checklist原文 | `c875a839fdedac666058b0635ade9b245b520ae79eeb12f3f2f9600ee85dec3d` |
| 首轮QA qa-handoff.json | `98d9c1e8f57d86a924f860858388e1c10d9868832d1dd8d9aeca41f878f09d9d` |
| BE005 owner_accepted checklist | `ee2de0b58ef837ca087576fcd7483d7dc22ee5cff050fff4f50a605629e27853` |
| HEAD / C0 | `1a5aa2d2fe7089b5671218865238cfaa240f9a30` / `363b297bffe65e020108f5504766b4fb1ec3b381` |

QA专属目录`/private/tmp/arch-be003-r3-reqa-a1rq6ege/`，新公开副本为`source/backend/`及同级frontend-js。
初始1536个公开文件；相对DEV原1511基线为46路径：35 DEV增量、10 Root机械索引、已形成的首轮checklist。
DEV 35路径after、返工三路径及468后端输入全部匹配，当前backend map无漂移。
QA map以自身序列化保存，SHA为`1ce98205db347a5cadc5a833624ff2944fae35a0f0229227e5ea541390ba881e`，
其468个path→SHA数据与DEV map逐项相等；编码换行差异不冒称源码差异。
QA profile明确`BE003`/60/e4f6a8b0c2d4，不冒称BE005 F/58。

六个可能由Root后续机械同步的后端输入精确为backend PLAN pair、equipment PLAN pair、equipment plans/README pair；
本轮取样及验证时六者亦零漂移。以后同步仅能逐路径记录为状态索引变动，不能泛化豁免任何实现、测试或稳定说明漂移。

## 环境、独立命令与安全控制

所有项目行为在新公开副本执行，复用仓库现有`.venv`、pyproject.toml、uv.lock；没有安装或锁文件变更。
底层实际argv为`uv run --offline --frozen --no-sync python -c <独立guard + payload>`。
`runner.py`仅作stdlib编排；完整argv/cwd/公开占位环境/退出码/时长/payload SHA保存在`commands.jsonl`。
运行环境为Python3.13.3、Darwin24.6.0 arm64、pytest9.0.2、SQLAlchemy2.0.48、FastAPI0.135.1、Pydantic2.12.5、Alembic1.18.4。
公开占位配置固定MySQL 127.0.0.1:1、两个不同fixture库名、TESTING=True、mock/Projection/三bootstrap=False、角色数组=[]、空scope。
TESTING不作为隔离保证；副本无真实.env。

独立guard拒绝SQLAlchemy connect/raw_connection、各DBAPI与sqlite3/dbapi2/_sqlite3、socket connect/bind/listen、
真实env打开及非白名单子进程；嵌套uv前置同一guard及offline/cache/pycache约束。
13项主动正控在实际动作前被拒绝，日志单独归`guard-positive-controls.jsonl`；嵌套uv确认guard有效。
实际项目检查的`forbidden-attempts.jsonl`不存在；正控不表示执行了数据库、网络、真实env读取或Docker进程。
全部cache、pycache、pytest、日志和产物在本QA临时目录。

| 本轮实际命令 / 检查 | 独立结果 |
| --- | --- |
| `python3 <QA>/runner.py guard-controls <QA>/guard-controls.py` | exit0，13项动作前拒绝及嵌套uv保护确认 |
| `python3 <QA>/runner.py full <QA>/full.py` | **exit0；全树compileall通过；完整`pytest -q -m no_db`为483 passed / 30 deselected，296.55s，runner299.719s**；未缩套件、删断言、skip或xfail |
| `python3 <QA>/runner.py original-input-recheck <QA>/original-input-recheck.py` | exit0，首轮真实get_db原12输入独立复验通过；仅复制件修改断言及输出路径，原失败证据不动 |
| `python3 <QA>/runner.py lifecycle <QA>/lifecycle-probe.py` | exit0，自建65例真实Router/Service/CRUD/get_db生命周期及纯Python Session矩阵通过，81条受控结构化日志脱敏 |
| `python3 <QA>/runner.py composition-compat <QA>/composition-compat.py` | exit0，实际preflight/App/ORM组合为60表、163 method/path、恰好8个原本地descriptor；只新GET/POST使用TemperatureRoute；旧GET limit不转发及旧全局业务HTTP200保持 |
| `python3 <QA>/runner.py b-collect <QA>/b-collect.py` | exit0，最终B入口compile与`pytest --noconftest --collect-only -q tests_mysql/test_equipment_temperature.py`为1 collected；未调用B函数 |
| `python3 <QA>/audit.py` | exit0，35路径整体/三路径返工patch独立重建与DEV逐字节相等；1490原基线保护文件（429 backend）及Root658保护文件保持；原测试/四迁移/Settings/Core/旧链路不变；22文档281本地相对链接（写本报告前）通过；三example/双语逐项表/中文头/索引及git diff --check通过 |

完整no_db再次执行原C0/C2/E正负矩阵、14/15/16子集、58→60→58 recorder、原4迁移指纹、价格和Projection本地事务回归。
既有独立首轮QA的offline upgrade/downgrade、单root/head/history、C2/E metadata/Core指纹证据被复用前逐项验hash；
相关迁移/Model/graph/Core输入与其时点逐字相同，不无依据重复命令，不将其写成本轮新执行。
首轮guard早期只读环境元数据误拒绝及失败日志仍保留，未冒称pass。首轮34项QA、原DEV19项及新DEV26项证据均验hash保持。

## F-001关闭证据

原失败要求为AC-009/R3-006的完整依赖生命周期及成功发送时序。
[局部TemperatureRoute](../../backend/app/equipment/api/temperature_http.py)现在在本地try内持有request/function两个AsyncExitStack，
先完成function退出、再完成request退出，在finally精确还原原scope对象后才返回Response。
[真实get_db](../../backend/database/session_async.py)、Core handler/deps、Service/CRUD、旧GET及其他生产表面未改。
本方案仅绑定已锁FastAPI0.135.1的`fastapi_inner_astack`/`fastapi_function_astack`；本地框架源码SHA/摘录归`framework-evidence.json`。
这些不是Core公开API；升级框架须重验，当前证据限新两条有界JSON接口，不泛化为流式响应、上传或任意第三方依赖支持。

原12输入仍使用真实新Router/Schema/Service/CRUD/get_db，只替换Session工厂为纯Python对象，不替换get_db函数。
GET/POST × DEBUG=False/True × exit commit/rollback/close均无外逸异常，响应壳严格含真实HTTP=code、data:null及局部稳定errorCode。
commit失败503，rollback/close系统失败500；没有提前HTTP200。POST退出commit的实际顺序为：

```text
commit_1 -> commit_2(fail) -> rollback -> close -> context_exit
         -> response_start_503 -> response_body
```

65例自建补充矩阵使用实际两条新router及纯Python durable Store：

- GET/POST、DEBUG两态、正常及三种退出故障共16例，所有session_exit均先于第一个ASGI send。
- POST已提交后退出故障保持一业务/一receipt，随后新Session同sampleId得到相同recordId、duplicate；总insert始终2，无多写。
- 业务flush、receipt flush、Service commit失败均无持久行；已写入后未知commit返回503，同键重试恢复原记录。
- request/function两scope × DEBUG两态 × 模块Business、HTTP401/403/422/500/503、DBAPI、system及未知Core Business共40例，全部本地映射、脱敏、不外逸，原scope引用精确恢复，局部stack清空。
- 同一次真实GET的function退出先于request退出，二者先于send；缺失/坏两种框架stack共4例均受控500且保持原环境。
- 81条JSON结构化事件无合成SQL/DSN/异常detail/token/完整十值payload。

**F-001已由本轮fresh Verification独立关闭。** 不把纯Python durable Store当MySQL持久化、约束、隔离级别或真实并发证明。

## AC与验收审计

| AC | 本轮A独立结果 / 仍需B的部分 |
| --- | --- |
| AC-001 | A通过：旧3GET/Models/async及sync字节、恰好8descriptor/本地business+cursor+audit回归保持；独立旧GET limit兼容检查通过。新表不union、双写或改变旧前端来源。B旧58代表记录/旧GET真实读回待验证 |
| AC-002 | A通过：真实ASGI原始JSON的十值/0/缺失/null/bool/字符串/非有限数/未知重复snake/quality、无损Numeric(30,10)域、时区/UTC范围/精确毫秒/极端指数/深JSON等422，wire camelCase稳定。MySQL逐值precision/毫秒待B |
| AC-003 | A通过：投递/业务键、actor/token、等价时区与数值、冲突优先级、仅真实named-1062有界恢复/其他Integrity负例；本轮额外验证退出后重试不多写。MySQL两个unique、独立Session首次并发裁决待B |
| AC-004 | A通过：同小时不同时刻及晚到样本、GET scope→recordId过滤、真实SQL limit/来源排序及空态。真实MySQL UTC毫秒读回待B |
| AC-005 | A通过：Service拥有commit/rollback、CRUD不提交、async链无同步DB；业务/receipt/flush/commit与未知提交、已提交丢响应同键重放通过；真实get_db退出结束后才发响应。MySQL原子性待B |
| AC-006 | A通过：单e4后继、五接链/单head、Model/recorder/offline签名与58→60→58/四迁移字节保护；C2/E14/15/16与BE00360明确区分。真实MySQL空库、d2升级、downgrade/re-upgrade、反射与58记录待B；不宣称DDL事务回滚 |
| AC-007 | A通过：真实JWT依赖无/坏/过期/refresh/revoked/inactive401、独立read/ingest、非admin即使有ingest仍403、所有caller scope、disabled整组404矩阵。user/role resolver/真实grants未改；真实B待验证 |
| AC-008 | A通过：仅公开现存resolve_env_file，签名/源码冻结路径、private-setting负例、本地显式/process/合成dotenv优先级、每app懒固定/隔离通过；三example原前缀/11标题/68旧key值grants保留，仅增空scope为69，双语各69key说明同步。未读取真实env |
| AC-009 | **A通过，F-001关闭**：仅新两method/path局部适配，v1/errors/exports/preflight通过；原12输入+自建65例证明typed HTTP/Business/DBAPI/system与DEBUG脱敏、依赖退出先于send、stack还原；旧全局HTTP200不变 |
| AC-010 | A通过：独立完整483/30、compile、迁移/价格/Projection回归、链接/diff/有限允许面与证据锁定。整体保留qa_blocked，不以A替代B或Human Owner最终验收 |

| 验收层次 | 当前事实 / 下一gate |
| --- | --- |
| 源码已验证 | A=passed；F-001=closed，仅指本报告锁定的源码/no-DB范围 |
| 必需但未验证 | **B-001**：BE003专用真实MySQL8.4.6的具体目标、动作及清理方案未获Human Owner批准；两轮独立真实验证未执行 |
| 保留兼容路径 | 旧温控GET/旧表/本地Projection writer及旧前端来源继续保留，不代表新HTTP观测自动展示 |
| 范围外后续 | 前端统一/采集writer切换、保留期、真实PLC/现场、部署/发布等另立任务与操作批准 |
| Human Owner final acceptance | pending；没有授予或推断最终验收 |

B-001解除条件：Human Owner另批BE003自己的精确disposable MySQL8.4.6目标/受限账号/loopback端口/schema/新卷/命令及清理方案；
随后在批准范围完成两轮新隔离资源上的独立真实验证，覆盖base→e4、d2带合成旧数据→e4、专用downgrade/re-upgrade、
60表约束/索引/精度反射、58表记录/旧GET保护、完整十值/UTC毫秒POST→GET、unique/FK/独立Session并发、事务失败与同键恢复，
并记录专用资源清理结果。BE005批准不转移；stub/SQLite/recorder/offline不能替代该gate。

## Handoff、证据与资源

**QA -> Human Owner：总体qa_blocked；A passed / F-001 closed，确认B具体运行gate后继续。**
本轮没有新实现failure需要返工；若后续证据否定合同，应以精确finding再交Development，QA不自修。
协调者可据本已成立verdict机械同步十索引；不能据此写qa_passed、owner_accepted或运行采用。

本轮源码、完整命令、原12输入复验、自建65例时序、JSON Lines、框架证据、公开maps、重建diff、审计、context与SHA manifest均归QA目录。
最终`qa-handoff.json`记录本checklist/source maps/evidence manifest的SHA；本文件不嵌入自引用SHA。
首轮checklist原字节还保存在本目录`round1-failed-checklist.md`，同时完整保留下方历史全文。
验收后仍需保留这些非秘密证据，临时路径不是唯一结论依据：关键标准、环境、结果、限制、时序与blocker已在本checklist落地。

所有本轮命令已结束；无listener、后台服务、浏览器tab、branch/worktree、数据库或Docker资源。
QA目录只剩公开源码、脚本、cache/pycache/pytest和证据；不执行回收。
原DEV/rework1、首轮QA、Root提案/协调目录、BE005及并行AW/Console资源全部保护，未修改或清理。
任何数据库（包括SQLite/内存库）、Docker命令、在线Alembic、真实env读写、实际listener/PLC/Projection、网络/安装、
依赖/lock变更、部署、Git refs/push均未执行；B函数从未调用。

---

# 首轮独立QA原文（不可覆盖的qa_failed历史）

以下内容保持原SHA c875a839fdedac666058b0635ade9b245b520ae79eeb12f3f2f9600ee85dec3d的完整字节；
其中“当前”“待返工”等指首轮时点，当前性以本文件上方最新报告为准。

Task ID: ARCH-BE-003
Revision: r3
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r3 A 独立完整420通过，但AC-009的依赖退出错误合同被12例ASGI反例否定；qa_failed/F-001退回Development同r3新turn，修复交接后另起fresh Verification；B仍未批准，Human Owner最终验收pending

# 验证身份、基线与权限

本记录由实际 `verification` 角色 `/root/be003_r3_a_verification` 在 fresh context 中创建。
消费 `.codex/agents/verification.toml`、根 AGENTS 与 canonical workflow；不继承 Development 的对话推理。
该 profile 为 `contract_only`；角色合同、串行 handoff 和 diff/checklist 审计是本次控制，不能据此宣称平台 ACL、强制路由或 Agent Team activation。
TOML 声明 `gpt-6.1-sol` / `max`，属于配置证据，不据此独立确认不可观测的实际运行参数。

Human Owner 精确批准：“BE005 r3 验收通过，批准 BE003 r3，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
当前验证只覆盖 A：不连接、创建、读取或写入任何数据库（包括 SQLite/内存库）；不执行任何 Docker 命令、在线 Alembic、真实 env 读写、listener、PLC/Projection、安装、网络、发布或推送。
只写本 checklist 与自有 `/private/tmp` 证据，不修复实现、测试、spec/tasks、配置或索引；不清理资源。

| 输入 | 已独立核对 SHA256 / 标识 |
| --- | --- |
| owner_approved spec | `6192f862ab24dbf44eb76d1d4d6fe6833a2103a891935c983412821633c4c73b` |
| 当前 developer_handoff tasks | `ff80bba2461800aaac980f2f35c89f7aa72dcf290bb0585b058c79a1d8ef2e76` |
| BE005 owner_accepted checklist | `ee2de0b58ef837ca087576fcd7483d7dc22ee5cff050fff4f50a605629e27853` |
| DEV handoff.json | `01ba24cf9e7b8eca1b88d00f86975cd93da66228ce1944809b555e7da8bc8e70` |
| DEV baseline-files.json / 1511 files | `2bee6f9328c0d6d1b85bc6d579438e24084d2f171720f29c088b3014c816ec47` |
| DEV delta.json / 35 paths | `a08979226c806ce2c26ed2cefab4800b71af7e4c9ff9524d89d3a13ebb03e0fd` |
| DEV delta.patch | `607d83550a444937b5399cf2a57aae6a4f40ba0c4d3a9827f4ab405cebac3ab1` |
| DEV source-map.json / 468 backend files | `8669183efaa57095c8865c21b25ecf16ad794ece75af754e9c9f8d8daac9ba02` |
| 当前 HEAD / C0 | `1a5aa2d2fe7089b5671218865238cfaa240f9a30` / `363b297bffe65e020108f5504766b4fb1ec3b381` |

已完整消费本任务 spec（r3 当前范围及 r1/r2 历史）、tasks（以末节420最终交接为当前事实）、根 README/PLAN pairs、最近 backend/app/equipment README/PLAN、实际实现和可用 DEV 证据；DEV self-check 仅作为输入。
应用 `project-governance`、`backend-arch` 及适用 references、`code-document-indexer`，仅用于验证。

# A 独立验证环境与证据

QA 自建目录：`/private/tmp/arch-be003-r3-qa-rtf31shs/`；公开源码副本为其中 `source/backend/` 及 sibling `frontend-js/`，无真实 `.env`。
初始公开工作树 1535 文件与 DEV 原基线相比45路径：精确35个 DEV delta 加10个 Root 机械索引；没有其他增量。
35路径 after SHA 全部匹配。DEV 468 backend map 仅六个已声明索引发生变化：backend PLAN pair、equipment PLAN pair 与 equipment plans/README pair；生产源码、测试、稳定 README 逐字保持。
QA 当前468输入 map 为 `source-map.json`，SHA256 `59f6d69f46c9a70b132eb63e5b6964a81a6dfdd6291c794e1c903d48d3be8bd6`；精确变化归 `handoff-drift.json`，不把索引变化当实现漂移。
初始快照 `start-public-files.json`、`start-baseline-delta.json` 和 `input-check.json` 保留在上述目录。
本轮过程中 Root 按本 checklist 已成立的 `qa_in_progress` 事实再次同步10机械索引；源码审计将这些变化单列在 `coordinator-index-during-qa.json`，不是 QA 写入或 Development 生产变化。

# 当前独立 verdict

**ARCH-BE-003 r3 当前 verdict 为 `qa_failed`；A=failed，失败项 F-001 / AC-009。**
完整 `420 passed / 30 deselected` 和其他源码检查保留为真实通过证据，但不足以证明整个请求及依赖生命周期的局部错误合同。
本轮不修复实现，不把失败改写为单纯的 B 环境阻塞。Human Owner 最终验收 pending。

B 必需真实 MySQL 精度、持久化、unique/FK、独立 Session 并发、事务失败/重放、全链迁移/回退和原58表记录保护均未执行、未验证；B 具体动作批准尚未到达。
A修复并重新独立通过后仍须另批并验证B，不能用本轮源码结果授予整体 `qa_passed` 或 `owner_accepted`。

# F-001：真实 get_db 退出错误逃逸局部 adapter

**要求：** R3-006及AC-009要求本新router处理整个请求和依赖阶段的异常，提供真实HTTP、同值code、`data:null`、稳定equipment错误key，并在DEBUG开启时保持受控错误。成功响应须在可能失败的依赖结束之前完成该错误决策。

**源码定位：** [TemperatureRoute](../../backend/app/equipment/api/temperature_http.py) 的 `get_route_handler()` 只包住 `await handler(request)`。
新两条route使用默认scope的 [get_db](../../backend/database/session_async.py)，其yield之后仍执行commit、异常时rollback及finally close。
本地项目环境 FastAPI **0.135.1** 的 `fastapi/routing.py:112-120` 在这个handler外拥有request/function两个AsyncExitStack：

```python
async with AsyncExitStack() as request_stack:
    scope["fastapi_inner_astack"] = request_stack
    async with AsyncExitStack() as function_stack:
        scope["fastapi_function_astack"] = function_stack
        response = await f(request)
    await response(scope, receive, send)
    response_awaited = True
```

`routing.py:972` 用 `request_response(self.get_route_handler())` 包装路由；`routing.py:449-461`将外部request stack传给solve_dependencies。
所以本地catch返回Response后，默认request-scope依赖在响应发送后才退出；其错误已经不在TemperatureRoute的try范围。
精确框架文件SHA与上述摘录在 `framework-evidence.json`，SHA256 `5ce9b9f03c323bf87a8ab14172ed9e2c63a73b11c32940907c37229eb0874afe`。

**独立无DB复现：** `dependency-exit-repro.py` 从QA新公开副本导入真实新Router、Schema、Service、CRUD和真实get_db函数；仅将 `database.session_async.async_session_maker` 替换为纯Python合成Session。没有DB连接、SQLite、listener或网络。
认证使用合成active admin依赖override；scope显式为公开合成key。直接捕获ASGI发送消息与退出异常，分别对GET/POST、debug=False/True及退出commit/rollback/close注入故障。
POST的Service第一次commit正常返回，故障注入第二次即依赖退出commit；没有把Service本身已覆盖的提交失败再次当成新缺陷。

| 12例组成 | 实际结果 | 所需结果 |
| --- | --- | --- |
| GET × debug=False/True × exit commit | 两例均先HTTP200/code200、`items=[]`，之后OperationalError逸出；commit1/rollback1/close1 | 依赖结束前处理已知DB失败为503及`equipment.temperature_unavailable`，不先发送成功 |
| GET × debug=False/True × exit rollback | 两例均先HTTP200/code200，随后rollback RuntimeError逸出；commit1/rollback1/close1 | 依赖结束前受控500/稳定内部错误壳；不能逸出局部合同或先发送成功 |
| GET × debug=False/True × exit close | 两例均先HTTP200/code200，随后close RuntimeError逸出；commit1/rollback0/close1 | 依赖结束前受控500/稳定内部错误壳 |
| POST × debug=False/True × exit commit | 两例均先HTTP200/code200、outcome=created，之后第二次commit OperationalError逸出；commit2/rollback1/close1 | Service已提交事实保留；依赖失败仍须受控503，不能先发送成功 |
| POST × debug=False/True × exit rollback | 两例均先HTTP200/code200、created，随后rollback RuntimeError逸出；commit2/rollback1/close1 | 依赖失败受控500/稳定内部错误壳；已提交业务不冒称已回滚 |
| POST × debug=False/True × exit close | 两例均先HTTP200/code200、created，随后close RuntimeError逸出；commit2/rollback0/close1 | 依赖失败受控500/稳定内部错误壳；已提交业务不冒称已回滚 |

实际POST退出commit事件序列：

```text
commit_1 -> response_start_200 -> response_body -> commit_2(fail)
         -> rollback -> close -> context_exit -> OperationalError
```

12例均没有局部失败`errorCode`。本复现观察到的wire内容是已发送的成功体；不把ASGI逸出的合成SQL/DSN异常误报为已观察到HTTP响应正文泄密。
DEBUG true同样未改变该退出边界。问题是局部错误和成功发送时序合同失守，不是已证明业务事务丢失或真实数据库回滚失败。

| 反例证据 | SHA256 |
| --- | --- |
| `dependency-exit-repro.py` | `c2a0666b722aff195646ded7ae94940bd2c4479c13c6da16aaf8f2e686c2f460` |
| 实际guard+payload | `286fc88d46ba0adbacf338a4872ea6562608c867588b0430da87713edcc1c938` |
| `dependency-exit-repro.log` | `26131e07f914d7c6fabe4d18c3053d6864e26669ec621f0b36235355e2aa6a2b` |
| `dependency-exit-results.json`，12例完整响应/异常/时序 | `a060bde07d3d2362ff9117fe31577c87568fbf4e6de049fafd7d3dcec094b274` |

反例命令exit0表示**成功观察上述缺陷**，不是AC通过。现有420未注入yield依赖退出阶段的故障，不能据其全绿否定本反例。

# 独立命令、环境与结果

项目行为统一从 `source/backend/` 执行，复用仓库现有 `.venv`、`pyproject.toml`、`uv.lock`，底层命令为：

```text
uv run --offline --frozen --no-sync python -c <QA guard + payload>
```

完整argv、cwd、显式公开环境、payload SHA、退出码和时长在 `commands.jsonl`，SHA256 `a95b1b7d63ea93bb2cd27dcdfd1eb9eacd55d260a03ef4a30883fb41af0c3a1d`。
外层 `python3 runner.py` 只作stdlib编排；不以Agent helper环境执行项目行为。
运行Python3.13.3/arm64 Darwin24.6.0；pytest9.0.2、SQLAlchemy2.0.48、FastAPI0.135.1、Pydantic2.12.5、Alembic1.18.4。
环境仅公开placeholder：MySQL 127.0.0.1:1、fixture primary/test两个名字、TESTING=True、mock/Projection/三bootstrap=False、角色数组=[]、scope缺省空。
TESTING仅为配置，不当隔离保证。强guard拒绝SQLAlchemy、各DBAPI、sqlite3/_sqlite3、socket connect/bind/listen和真实env打开，并前置到嵌套uv。
最终 `connection-attempts-v3.jsonl` 不存在；`guard.py` SHA256 `1fb6d84cf4088a974ad541fa7132630a320cd49e3e69d8e0e566b6b1cba95619`。

| 独立入口 | 实际结果 |
| --- | --- |
| `runner.py full-v3 full.py`：先compileall全树，再完整 `pytest -q -m no_db --basetemp <QA tmp>` | **420 passed / 30 deselected，298.12s，exit0**；总runner301.325s。未缩套件或删原断言；全树compileall通过。日志SHA `313ccbe631953219c1d6c01ed24babf6872107fe474fd5059d5cb5289707aaf7` |
| `runner.py supplemental supplemental.py` | exit0；实际guarded Alembic offline upgrade/downgrade、组合、B compile/collect。整体16.409s |
| 五revision recorder / 原四迁移 / 58→60→58 | 完整420内通过；原4迁移字节和原58表完整签名保持，不把58改为60来削弱保护 |
| Alembic offline `upgrade e4f6a8b0c2d4 --sql` | exit0；生成60业务表及alembic_version，未apply SQL；日志SHA `d7f0d27dec2709f4ed7c11dad761bd138a6d8d5a76084ba1924124ae4c86b469` |
| Alembic offline `downgrade e4f6a8b0c2d4:d2f4a6b8c0e2 --sql` | exit0；只DROP receipt、sample两表及回退版本号；日志SHA `02f4701ed2c32a974f0b0d28ba640c39cbb9feef0e0ff2c29aa4afae090df3c5` |
| `runner.py heads-fresh/history-fresh` | 各exit0，0.328s/0.223s；单d4 root/e4 head与五接链。初次同进程捕获heads/history受Alembic stdout绑定影响未得到输出，已用独立新进程取得原始输出，不冒称空日志为内容证据 |
| C2/E1/E2实际preflight/App/ORM组合及Core指纹 | 各exit0，14/15/16表、50/52/54 method/path。三者Core逐文件SHA一致，core-files.json SHA均`b980a9bffb5e8ea539956016322bb38e4b0ec6bbd2230bed394a99cdf54abc66`；原C0清理和E正负矩阵包含于420 |
| 新BE003组合 | 60表、163 method/path，两条新method/path独立存在；无新增第9个descriptor |
| 最终B入口compile及 `pytest --noconftest --collect-only -q tests_mysql/test_equipment_temperature.py` | exit0，**1 collected，函数未调用**。入口SHA `98873104d111037239271546d7e91123dd4d22a32f5620851d12b64bd6d7ced9`；仅既有anyio assert-rewrite warning |
| `runner.py dependency-exit-repro dependency-exit-repro.py` | exit0，0.353s；12例成功观察F-001失败，不是通过 |
| stdlib `audit.py` | exit0：35 DEV路径、10 Root索引、1490原基线保护文件（含429 backend文件）保持；21文档279本地相对链接目标存在；三example原前缀/68旧key值/grants保持、仅增空scope成为69项、双语逐项表均69；新文件中文头/原测试保留、窄diff及新增行空白检查通过；`git diff --check` exit0 |

QA harness早期 `full` 与 `full-v2` 各exit1，发生在测试开始前：环境元数据读取分别触发只读uname/file，被过严subprocess白名单拒绝；保留两份日志/旧guard，校正只读元数据允许项后才执行上述full-v3。未改项目或测试。
审计初次因Root按qa_in_progress同步10索引触发快照断言，单列这10个既定机械路径后重新审计exit0；生产/测试/稳定文档没有变化。
这些是QA编排限制，不记为额外实现failure，也不删除失败历史。

# AC与验收审计

| AC | A独立结果及限制 |
| --- | --- |
| AC-001 | 通过：旧3GET/旧Models/async及sync链字节保护、8descriptor与本地business+cursor+audit既有回归保持；新样本不union/双写旧表，前端来源保持。B原58记录/旧GET真实读回未验证 |
| AC-002 | 通过：真实ASGI原始JSON、十值/零、未知/重复/snake/缺失/null/bool/字符串/非有限数、数值技术域、UTC时区/毫秒/极端指数与深JSON解析422；camelCase及局部稳定错误。真实MySQL逐值精度仍待B |
| AC-003 | 源码部分通过：投递/业务键、actor、时区等价、冲突优先级、有界恢复和非目标Integrity负例；不把合成Session当真实并发唯一证明，B未执行 |
| AC-004 | 源码部分通过：同小时多时刻、晚到样本、SQL实际scope/recordId/limit/source排序及空态；MySQL UTC毫秒真实读回待B |
| AC-005 | Service事务范围通过：业务/receipt/flush/commit失败、未知提交与已提交丢响应重放；CRUD不commit/rollback、async链无同步DB I/O。请求依赖退出边界另见F-001，真实DB原子性待B |
| AC-006 | A通过：五revision、两表Model/recorder/offline类型/约束一致、单head、原4迁移字节和58子集保持；C2/E14/15/16及BE003/60 profile明确。真实MySQL空库/旧head/回退待B；不宣称DDL事务回滚 |
| AC-007 | A通过：真实JWT依赖无/坏/过期/refresh/revoked/inactive401、独立read/ingest/admin写、scope/disabled404矩阵；旧用户/role resolver/真实grants字节不变。真实B未执行 |
| AC-008 | A通过：PUBLIC_SYMBOLS仅加resolve_env_file，helper源码/冻结签名及private-setting负例保持；本地配置优先级、每app懒固定、跨app隔离、英文空scope69key与双语说明通过；没有真实env读取 |
| AC-009 | **失败：F-001。** 进入依赖/Service/解析错误的局部401/403/409/422/500/503及日志脱敏既有测试通过，但12例yield依赖退出异常在HTTP200之后逸出，完整依赖阶段合同未成立 |
| AC-010 | 完整420、compile、迁移/价格/Projection回归、链接/diff和精确handoff审计通过；独立发现F-001后A与整体仍qa_failed；B与Human Owner gate保持未授予 |

所有真实数据库（包括SQLite/内存DB）、Docker（包括只读命令）、在线迁移、真实env、listener、PLC/Projection、浏览器、安装/网络、Git refs/推送、发布/部署均未执行。
没有重复已验收BE005的浏览器/数据库验证，没有追加无关UI测试。

# 失败handoff、资源与最终验收gate

1. **QA -> Development：** 对精确r3回退F-001。在已批准的新局部adapter/router及定向测试allowlist内修复完整依赖结束与成功发送时序，保留Core/get_db全局合同、新旧接口边界和本次失败证据。QA不指定绕过失败或缩测试的实现。若必须越界，按workflow回PM新Revision。
2. **Development -> 新fresh Verification：** 新turn完成后交更新的tasks、实现/diff/source指纹、定向退出故障矩阵及必要完整A自检；再由实际verification、fresh context独立复验。不能在本失败turn自修后自授通过。
3. **QA -> Human Owner：** 本轮为qa_failed，最终验收pending。A修复并独立通过后再确认BE003专用B目标/动作与清理方案；BE005批准不转移，A通过也不能替代B。

证据manifest `evidence-sha256.json` SHA256为 `57ef02c33ee983ab894c1751e1b1804ce96e22ba779dc98cb81af1fb77503f13`，覆盖34个关键输入、脚本、通过/失败日志、反例结果、审计与公开指纹。
关键要求、框架边界、12例时序和verdict已记录在本checklist，临时目录不作为唯一事实源。
QA自有 `/private/tmp/arch-be003-r3-qa-rtf31shs/`、DEV `/private/tmp/arch-be003-r3-dev-6diknqm3/` 与其指针仍承担返工/复验依据，全部保留；Root B提案、BE005及AW/Console资源未修改或清理。
本QA的命令均已结束，没有创建listener、后台服务、浏览器tab、branch/worktree或DB/Docker资源；cache、pycache、pytest产物只在QA临时目录。验收后的资源盘点由协调者处理。
最终checklist SHA及非自引用 `qa-handoff.json` SHA由结束消息交Root；本文件不嵌入自己的SHA。

**Human Owner final acceptance：pending；本轮没有最终验收授权或记录。**
