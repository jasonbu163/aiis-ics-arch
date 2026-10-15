Task ID: ARCH-BE-005
Revision: r3
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: 第二次返工后的独立A源码/离线验收通过；整体因B真实MySQL尚未具体授权及验证而qa_blocked；交Human Owner决定B具体动作与后续最终验收，保留两轮失败全文
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Context: fresh；实际命名verification角色，未继承Development对话推理；contract_only
Verification Round: r3-rework2-A-third-QA
Updated: 2026-10-14

# 当前独立结论（第三轮，第二次返工后）

**A阶段通过；整体verdict为`qa_blocked`。** 本轮独立编译及完整原no_db套件为
**319 passed / 30 deselected，379.05s，exit0**；原F-001至F-004、扩展合法/非法边界、C2/E/F、
E迁移recorder与组合ASGI、离线CLI/SQL、前端既有独立证据适用性及此前缺少的真实浏览器项均已完成。
没有用DEV的319或旧QA的304/286替代本轮实际结果。未发现新的实现failure。

整体仅因**B未具体授权、未执行、未验证**而阻塞：AC-007、AC-008与AC-r2-006仍未验证；
不能写整体qa_passed、owner_accepted、deferred complete或“迁回模块均可直接运行”。
Human Owner保留具体运行动作批准、风险接受和最终验收权。

根AGENTS、README/PLAN pairs、canonical workflow、Verification TOML、最近backend/app/模块及前端说明、
完整spec（r3/r2/r1）、完整tasks、现有两轮checklist、实现/diff/可用输出均在本fresh context独立读取。
应用project-governance、aiis/CONTRACTS、backend-arch的七份相关reference、frontend-ui的FRAMEWORK/
DESIGN、i18n-workflow与code-document-indexer，仅用于验证。无backend/scripts新入口或其他运行面，
未加载/执行Docker、Worker、Rust等不适用流程。TOML的gpt-6.1-sol/max是配置证据，
没有把contract_only说成平台ACL、强制路由或运行模型探测。

本轮唯一版本化/非忽略源码文档写入为此checklist；未改spec/tasks、实现、测试、配置、依赖清单、
锁文件、真实env或六索引。**另有ignored Vite缓存写入限制，见“资源与工具副作用”**，
不宣称checklist以外的全部文件系统字节都未变化。

第二轮完整原checklist SHA为`7068c3ed97c939455a126d9533f14c5cfb0b994e7c195b8e556d52e4c5acd8c7`，
已保存为本轮`previous-checklist.md`，其**全部原字节**从本文末尾“前两轮失败报告历史”开始保留；
该原件本身已包含第一轮报告。历史失败和当时未运行项继续是当时事实，不覆盖本节当前性。

# 精确输入、指纹与环境

| 输入 | 本轮核对 |
| --- | --- |
| 工作树/C0/HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`363b297bffe65e020108f5504766b4fb1ec3b381` |
| 当前批准spec | `6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d`；顶部owner_approved和r3批准收据 |
| 当前tasks | `59a71c4b810659dc4755ad4ec23792868ddc0138bb26a0da4f10ac89ab7aa87e`；最新第二次返工developer_handoff |
| 当前module_preflight.py | `0035aaf4c4421d65f7ef15eb86f5337c92cdef57c20fbf727234be06f3e7787f` |
| 当前test_module_admission.py | `c58c2029979e958d09fcd7f53dbf48024c4ea8b4c5285a14514a37be0561246d` |
| 当前CODE_INDEX.md组合状态 | `95cfbd1752d4e725f485aa135e79eabecd90213fce99c1d1adca430041046ad1` |
| 原998文件baseline清单 | `fd532d733ef1ecc0f023e2ae7555d5955139a10f114e68cada55cc4f63280709`；逐文件原件和before均核对 |
| DEV本轮分层审计 | r3-rework2-integrity.json：`12acbd94eeb0db927e2e5b65a5e303f64eb9f75a3fd9ce55383289e5c7b72c0a` |
| 四文件only-delta / patch | JSON `ed890d39adf134cdffa8d7589339dd97326f2cdc84c10607f15e38bcde0f9f1e`；patch `10d8350f672ecbbef839a86d0c230a2f23ec051b456f0c14489ff6a34492139f`；独立按before/after重建patch原字节相同 |
| DEV当前分层指纹 | r3-rework2-current-fingerprints.json：`ba532ce76b692607ec41a8bfb7334e60654cda2f93464acade82e6436d99e0e1` |
| QA专属证据 | `/private/tmp/arch-be005-r3-rework2-qa-lGwand/` |
| 项目环境 | 既有backend/.venv、uv.lock；Python3.13.3、macOS15.7.7 arm64；SQLAlchemy2.0.48、Alembic1.18.4、FastAPI0.135.1、pytest9.0.2、Pydantic2.12.5 |

项目行为通过公开`tests/module_admission_fixtures.py:run_python/public_environment`，底层
`uv run --frozen --no-sync python -c <guard + QA payload>`；UV_OFFLINE=1。
`commands.jsonl`保存实际cwd、完整命令、payload SHA与退出码，payload和完整log均留存。
公开Settings使用TESTING=True、MySQL占位127.0.0.1:1，mock/Projection/bootstrap关闭；副本无真实env。
原生成器写死的uv-cache/pycache路径仅在QA编排层重定位至本专属目录；没有改变项目源码或测试。
在任何App导入/pytest collection之前拒绝SQLAlchemy同步/异步connect/raw_connection、可用DBAPI、
SQLite及socket连接；嵌套uv profile子进程注入同一guard。**连接尝试日志为零**。
F保留原共享conftest，通过no_db marker让DB autouse fixture早退；无create/drop/create_all或SQLite。

# 原失败关闭与扩展边界

本轮33项独立正负probe的输入、source/metadata/App结果和实际ASGI对照见`boundary-inputs/`、
`boundary-*.py/.log`及`boundary-results.json`。原两轮QA输入/log只读；新副本仅overlay最新预检，
其余反例改变只作用于本QA合成模块。完整319另外执行Development新增正负用例，二者分开计数。

| 历史项/边界 | 当前独立结果 |
| --- | --- |
| F-001（P1）非Error类名/空claim的Failure复用Core值 | 原输入的source、metadata及create_app均明确error-namespace/user_not_found阻断；没有依赖类名或新增注解。合法普通状态ErrorStatus.ACTIVE仍可组合，真实ASGI合法业务错误返回原共享信封 |
| F-002（P2）同名Item的qualified relationship owner | 原输入source、完整App/configure_mappers、`Ref.probe.mapper.class_ is Probe`与JOIN编译通过；独立把provider从summary之前移到之后仍指向原class；改成歧义裸Item则model-target阻断，无虚假summary依赖 |
| F-003（P2）普通package/relative module alias | 两个原QA2输入分别通过source/metadata/App及真实ASGI空白label错误响应，errorCode为admission_probe.invalid_value；同写法改Core冲突并清空claim，三个入口均error-namespace阻断 |
| 显式package绑定优先 | Model/DTO/函数三类在同名Public.py存在时仍绑定原定义，actual identity和__module__核对；Model仅model_requires且provider disabled合法，DTO/函数仍requires；删除相应依赖阻断 |
| 工厂/局部literal别名/opaque来源 | 泛型StrEnum、无注解keyword/default工厂和局部member别名合法且实际ASGI正确；改Core值仍阻断。实际opaque错误来源明确error-source，未用作错误的普通状态enum不误判 |
| disabled runtime | 缺provider的Service文件、services/API子package入口合法且未eager import；存在但disabled且依赖未安装runtime的provider也不eager import。enabled消费者依赖disabled provider、disabled model闭包缺失仍阻断；root/model源码严格，能定位的本地Core冲突仍严格 |
| F-004（P3）CODE_INDEX小时Model路径 | 当前等于AW组合入口快照的一次精确auxiliary→energy路径替换，目标存在；全部相邻AW行保留 |

一次QA负例oracle最初把unsafe root的metadata/App失败限定成ModulePreflightError，实际在manifest-import
阶段已通过ModuleRegistryError严格阻断；保留该失败helper/log，修正临时oracle为精确stage/module并
重验通过。这是QA编排问题，未作为实现failure或偷偷吞掉负例。其余编排语法/排序/计数口径与浏览器
一次中文label重定位均记录在`qa-orchestration-notes.json`，没有改项目断言或扩大r3保证。

# 本轮独立执行的A检查

| 检查 | 实际结果与证据 |
| --- | --- |
| C0+八overlay独立重建 | 140 Core文件；core-files SHA `9396972f06181157f523f8d0f05b35a7ecda741d92cd12e328512185a328d78f`、patch SHA `08947c51e44b3e7ff90a8d96a1233faf5c5428396809e661b23898b32bf030d8`。七直接批准源文件加monitor C0窄overlay；另用public generator重建交叉核对，字节相同 |
| C2 sanitization | C0四测试文件原字节；guarded pytest `--noconftest -q -m no_db tests`，12 passed/exit0，仅no_db marker warning；`C2-sanitization.log` |
| C2/E1/E2/F真实组合 | 14/15/16/58表，50/52/54/161个method/path，0/0/0/8个descriptor；全部Models/App/configure_mappers及最终routes检查exit0；四metadata-routes SHA与DEV最新报告逐字一致，见completed-checks.json |
| E冻结Core及旧14签名 | E只追加合成消费者/revision；每个Core SHA不变；E1/E2/F原14表完整signature均与C2相同，未仅数表 |
| 完整F编译+原套件 | 先compileall全树，再原样pytest `-q -m no_db --basetemp <QA>/pytest-tmp`；319 passed/30 deselected，379.05s，exit0；`full-no-db.log`。无缩套件、删断言、skip/xfail、新conftest或SQLite替换 |
| F回归所含范围 | 新旧依赖/声明/冲突、r3 Model分类、disabled/runtime/metadata环、HR关闭及5表、owner guards/401/403/404、全部有效ErrorCode、价格BE002/004边界、GET零写、8descriptor及原本地合成business/cursor/audit事务均包含于319 |
| E1/E2显式migration recorder | 独立沿ScriptDirectory重放到recorder，15/16逐表类型/PK/FK/unique/check/index签名与metadata一致并经MySQL dialect编译，各自撤增量后降回原14且签名不变；各exit0，E1/E2-migration-recorder.log |
| E2实际组合ASGI | Core/Probe/Summary真实API/Schema/Service，合成Session；camelCase POST→GET、probeId/probeState、DTO继承/ACTIVE key、两owner错误、401/空/未知/跨owner/read-only grants与失败rollback均exit0；E2-ASGI.log。它不替代B真实FK/事务 |
| F迁移/旧保护 | 完整319执行四revision recorder/58表signature、MySQL DDL编译、仅撤42保旧16、单root/head；三旧migration SHA保持；不执行SQL |
| Alembic真实CLI offline | guarded runpy等价`python -m alembic upgrade head --sql`及`downgrade d2f4a6b8c0e2:b8d0f2a4c6e8 --sql`，各exit0；59 CREATE TABLE含alembic_version、42 DROP TABLE；offline-upgrade/offline-downgrade.log。heads/history为单d2 head、单d4 root及四revision |
| 预检真实CLI | bare、--help、显式--project-root/--check-only各exit0；不导入Settings/database/App、不读取真实env；preflight-*-cli.log |
| B入口仅compile/collect | 原两文件只读；guarded compileall tests_mysql及pytest `--noconftest --collect-only -q tests_mysql`，2 collected/exit0；没有调用测试函数、DisposableTarget、连接/反射或在线迁移 |
| 价格源码保护 | 六迁移文件与原已验收auxiliary基线相比，仅app模块路径及文件头归属替换，逐字等价；两个表/三个route唯一energy owner。四auxiliary和两monitor恢复类AST与只读旧源同定义 |
| 文档/增量 | 16份稳定Markdown本地链接无缺失；四文件patch新增空白及git diff --check通过；entry到写checklist前1356源码/文档清单零变化，见pre-checklist-integrity.json |

# 前端证据适用性与本轮真实浏览器

本轮**未重跑pnpm check/test/build**。独立比较当前frontend-js的198个src/tests/scripts、package/
lock/Vite配置文件与首轮QA公开副本，全部字节相同；另比较pnpm-workspace.yaml也相同。
因此沿用其独立check exit0、**46 passed/0fail**、build exit0（既有large-chunk warning），
不是沿用DEV结果或冒称本轮另跑。三个原log的SHA及适用性见frontend-prior-evidence-applicability.json。

本轮实际在公开前端副本链接既有node_modules，不安装依赖；使用真实shift SFC、ElementPlus、主题及
i18n，仅API/user为合成stub，Vite只监听127.0.0.1:5327，无真实backend/API。
浏览器使用实际Chrome/CUA，截图、DOM快照、几何证据和stub DOM audit保存于`browser/`：

- **390×844 null四组合**：zh-CN/en-US×light/dark均明确未配置、Edit数量0、08:00/20:00假时段不存在、
  stub无PUT；提示左右44..336，scrollWidth=clientWidth=292，未溢出。实际截图明暗色与翻译正确。
- **已有规则**：07:00–19:00/19:00–07:00，Edit→真实dialog→cycle改QA_CYCLE_UPDATED→Confirm→
  stub updateShiftRule(id7)→Success；卡片显示新cycle且保留07/19，dialog随后关闭。
- **失败反馈**：中英GET异常分别显示操作失败/Error；PUT异常显示对应反馈，dialog保留编辑输入、
  原APPROVED_FIXTURE卡片规则不被成功覆盖。既有46项实际编译SFC错误测试也仍适用。

浏览器summary SHA `eb8e1525161511ee482c20362d76e8a4d22475293eb9ca2f9b9730c886617316`。
本次截图是独立QA实际浏览器证据，不能推断真实后端联调、持久化或进程已采用源码。

# AC verdict与B解除条件

| 验收面 | 当前结论 |
| --- | --- |
| AC-001..006 | A通过：导入/装配/权限/价格/只读/58表与显式后继/8descriptor/完整编译no_db/文档/前端既有独立证据与新增浏览器全部完成 |
| AC-r2-001..005 | A通过：公共合同、依赖、冲突、干净C2/E接入和完整F均有独立正负及运行对象证据 |
| AC-r3-001..005 | A通过：Model原定义分类、system→monitor公开出口与声明、runtime/model闭包分离、八overlay、旧14签名和r3完整A交接均核对 |
| AC-009、AC-r2-007 | 精确Revision/source/diff/命令/限制的独立A handoff已完成；整体后续仍受B gate约束 |
| AC-007/008、AC-r2-006 | **qa_blocked：未具体授权、未运行、未验证真实MySQL8.4.6的E/F迁移/CRUD/约束/并发/回滚/旧数据保护。** SQLite、stub、recorder与offline均不可替代 |
| Human Owner最终验收 | pending；QA不授予最终接受、发布、部署、DB操作、真实设备操作或push/refs授权 |

B解除条件是Human Owner另行批准具体disposable实例/五schema、endpoint/卷/账号身份、起始revision、
合成fixture、精确命令与清理/回退清单，再取得所需MySQL8.4.6真实证据并由后续fresh Verification复核。
`/private/tmp/arch-be005-r3-b-proposal/`及两个入口只是未执行准备。
“真实DB测试前先Alembic到最新”在源码入口中顺序成立，但不构成执行该操作的授权。
当前从未执行DB（含SQLite）、在线Alembic、任何Docker命令、真实API/Projection/PLC、部署、Git refs/push。

# 分层完整性、资源与工具副作用

原132纯BE delta、第一次返工delta/patch/integrity、两轮QA原件与原DEV输出均按原字节保全。
当前128非共享BE路径逐项匹配，其中125仍为第一次返工after，另3为本轮预检/接入测试/tasks；
AGENTS/CODE_INDEX/README pair四共享文件单列AW组合，CODE_INDEX只有批准的一条BE路径修正。
ROADMAP pair是AW获批R7状态；原54保护中52保持、2个ROADMAP与入口共享状态一致。
协调者六索引独立归属，不归本轮DEV/QA增量，不将总Git diff或AW变化归BE。未发现未归属源码漂移。

本轮专属目录保留全部输入、guard、scripts、commands、logs、SQL、profiles、screenshots与source maps。
QA evidence manifest含154个证据项，SHA
`b4a7a587b6188e73c956e4167130d59de5c8e56ac4acbf315db37e1470cc8692`；
pre-checklist-integrity SHA `9833d7b2fa47d9e9b86c4f73bb3ef36700dc29213107d49691108d46288ffdef`。
关键断言/结论已写入此checklist，不只依赖可能消失的tmp目录；原QA/DEV/协调者资源继续保留，本角色不清理。

synthetic listener首次sandbox listen EPERM/exit1，针对已批准本机harness的工具权限升级后成功；
结束Ctrl-C/exit130，lsof -iTCP:5327 -sTCP:LISTEN无输出/exit1，自己创建的tab已关闭且viewport reset。
所有本轮测试命令均结束；无分支/worktree/仍占用listener。

**QA工具限制：** copied DEV Vite harness没有指定cacheDir，复用node_modules符号链接后，Vite默认优化
缓存写入了仓库ignored的`frontend-js/node_modules/.vite`，metadata mtime为2026-10-14T06:48:22.694344Z。
这是QA缓存路径遗漏；已向协调者报告，未安装依赖或改变依赖清单/锁/源码/真实env。
没有擅自删除、回退或把共享缓存列为可安全回收。source完整性map不覆盖ignored依赖runtime cache；
后续synthetic harness必须先把cacheDir显式指向任务tmp。精确路径、SHA、原因和边界见
browser/cache-side-effect.json。另准备browser/future-fixture.vite.config.mjs显式将cacheDir放入本QA tmp，
仅供后续复建，保留实际执行config原字节，未因此冒称重跑UI。该工具副作用不改变上述A行为/合同结果，也不提供B运行证据。

# 正式handoff

1. **QA -> Human Owner：** 精确ARCH-BE-005 r3的A独立通过，整体qa_blocked；B AC及最终验收pending。
   如选择继续，先批准具体B动作，再执行/交新fresh Verification；当前不自行启动B。
2. **QA -> Development：** F-001..F-004当前已关闭，无新增实现failure需返工；保留全部失败历史及合法/
   非法输入，不将当前结果倒写成旧两轮通过。
3. **QA -> 协调者：** checklist是本轮正式独立事实面，六索引由协调者机械同步；最终checklist SHA、
   evidence/final integrity及所有关键输入SHA汇总在本轮handoff.json，当前不授予owner_accepted。

---

# 前两轮失败报告历史（完整原字节保留；以下不是当前元数据或本轮命令）

Task ID: ARCH-BE-005
Revision: r3
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: 第二轮A独立验证发现F-003合法module alias误拒及F-004索引残留，返回Development在r3内返工；B未授权未执行，Human Owner最终验收pending
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Context: fresh；实际命名verification角色，未继承Development对话推理；contract_only
Verification Round: r3-rework1-A-second-QA
Updated: 2026-10-14

# 当前独立结论（第二轮，返工后）

**当前verdict为`qa_failed`，A仍未通过。** 首轮F-001/F-002的原始输入本轮已独立按预期复验，
完整编译及no_db为304 passed/30 deselected；另补的普通literal模块别名正例仍被`error-source`
错误拒绝，记录为F-003。CODE_INDEX还有迁移后不存在的旧价格Model路径，记录为F-004。
不能把304通过、两个原反例通过或其他A分项通过写成整体A通过，更不能提前执行B。

本次只更新本checklist；spec、tasks、实现、测试、环境、配置、依赖与索引均未修改。根/最近作用域
治理、当前完整r3/r2/r1 spec、完整tasks（含最后“r3 第一次QA失败返工后的Developer handoff（当前）”）、
首轮checklist、当前Core实现/返工diff、完整增量清单与可用DEV/首轮QA输出已独立消费。
匹配skill为project-governance、aiis/CONTRACTS、backend-arch七份相关reference、frontend-ui的
FRAMEWORK/DESIGN、i18n-workflow及code-document-indexer；只作验证，没有运行修改型skill工具。
Verification TOML的`gpt-6.1-sol/max`仅作为配置证据；不宣称另行探测运行模型、平台ACL或强制路由。

首轮失败报告原文件SHA为`389341c7f3e7788be5e8e735fb9ec68ad7ed7faa47306a4d59b37d44f5ac1b62`。
其**全部原字节**保留在本文末尾“首轮失败报告历史”下，含原元数据、证据和当时未执行项；历史文字
不覆盖本节当前性。QA专属原件另存`previous-checklist.md`，未改首轮QA/DEV证据。

# 精确目标与环境

| 项目 | 本轮独立核对 |
| --- | --- |
| 工作树/C0/HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`363b297bffe65e020108f5504766b4fb1ec3b381` |
| 批准规格 | r3顶部和批准收据；SHA `6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d` |
| 当前tasks | SHA `008896fc66eb4eaa272f67f1be686c6c39d4758f827ad099956fe26e8ca8bf38`，仍developer_handoff；不把旧286计为当前304 |
| 原源码基线 | 998文件；baseline-files.json SHA `fd532d733ef1ecc0f023e2ae7555d5955139a10f114e68cada55cc4f63280709` |
| 当前任务delta/patch | 132文件；JSON SHA `3ee40cf5109b3e9e806d041685c7ea09fcb890a707cf0de276da3f0427198fde`；patch SHA `2ff77da6cb1bee5fbe4971965284e8d626989c763ba076e2e42099fc3077da4f` |
| 首次handoff后返工 | 五文件；only-delta SHA `879dd33ff987ac6421b4fae32ec66a1c5c5d7353b77dace8d66827abb82acd36`，与两代delta逐项吻合 |
| 当前预检实现 | module_preflight.py SHA `ca6a4b8db459ae55eca519fa2df41e59bb6eb1f4d7faa92c9aa7b4c37dce7e52` |
| 本轮专属证据 | `/private/tmp/arch-be005-r3-rework-qa-3w32Z7/` |
| 项目执行环境 | 既有backend/.venv/uv.lock，Python3.13.3，macOS15.7.7 arm64；SQLAlchemy2.0.48、Alembic1.18.4、FastAPI0.135.1、pytest9.0.2、Pydantic2.12.5 |

项目执行统一通过`uv run --offline --frozen --no-sync python <QA>/qa_execute.py <payload>`，
cwd/PYTHONPATH仅指公开profile。完整命令、payload SHA和退出码见`commands.jsonl`。
公开Settings为TESTING=True、MySQL占位127.0.0.1:1，mock/Projection/bootstrap关闭；无真实env。
`qa_support.py`在任何App导入/collection前拒绝SQLAlchemy同步/异步connect/raw_connection、
各可用DBAPI和SQLite connect及socket连接，并给嵌套profile uv子进程注入同一guard；仅把原生成器
cache/pycache路径重定位到QA目录，不改测试内容、断言或选择条件。本轮无被guard记录的连接尝试。
F保留共享conftest，no_db使其autouse DB fixture早退；未执行任何DB建库/drop/create_all。

# F-003：普通package/relative module alias被误判无法定位错误来源

**P2；阻断AC-r2-001、AC-r2-002、AC-r3-005。** 首轮F-001原漏洞已阻断，但返工新增的来源解析
仍把`from package import submodule`误当作普通attribute。位置为
[module_preflight.py](../../backend/app/module_preflight.py:220)的ImportFrom返回，及
[attribute拼接](../../backend/app/module_preflight.py:211)。源码/调用点的具体StrEnum本来可定位，
不应因普通literal写法报error-source。规格要求解析literal import/from和相对import，没有要求用某
特定import语法、类名、文件名或新增注解。这不是动态import或opaque运行值。

从本轮独立冻结的E1各复制一份，Core字节不动，仅改变合成模块Service的原错误导入与引用：

```python
# package-module-alias
from app.admission_probe import error_codes as errors
# 或 relative-module-alias（文件在services/async_item.py）
from .. import error_codes as errors

# 原非法label分支，其余逻辑不变：
raise BusinessException(errors.ErrorCode.INVALID_VALUE)
```

枚举仍为`app/admission_probe/error_codes.py`中的StrEnum，值仍是
`admission_probe.invalid_value`；manifest.error_codes仍精确声明同值。实际`check_source('.')`
对两种输入都失败，诊断分别定位各自Service第9行，原文相同：

```json
{"identifier":"app.admission_probe:error_codes.ErrorCode.INVALID_VALUE","location":"app/admission_probe/services/async_item.py:9","module":"admission_probe","other_owner":"","stage":"error-source"}
```

同一个guarded进程随后直接导入该Service，调用真实`create_item(None, ItemCreate(item_label=' '))`，
两次都正确抛出共享BusinessException，`error.error_code.value == 'admission_probe.invalid_value'`。
这条路径在触碰DB前退出，证明输入本身是正常的Python导入/调用与合法错误定义。
对照`import app.admission_probe.error_codes as errors`及同样的枚举成员引用，源码检查通过。
顶部成员别名、无注解keyword/default工厂、未用作错误的`ErrorStatus.ACTIVE='active'`也通过。

独立程序`extra_error_boundary_checks.py`、完整输入`extra-error-inputs/`、结果
`extra-error-boundaries.json`及`boundary-*.log`均保留。两个失败probe的exit2表示成功观察到
**实现错拒**，不是普通模块应被拒绝的通过结果。其余四个对照exit0。QA未改实现或添加例外。

# F-004：代码索引仍指向迁出的小时价格Model

**P3；AC-006/AC-r2-005的结构文档修正项。** 协调者提示后，本轮独立核对
[CODE_INDEX.md](../../CODE_INDEX.md:108)：`backend/app/auxiliary/models/energy_price_hour.py`不存在；
真实单owner文件是`backend/app/energy/models/energy_price_hour.py`。该残留在保留的BE005任务
handoff快照中也存在，不能归因AW并行同步。交Development仅修正这一既有索引项并保留AW其他行；
QA不自修。这不是历史任务bundle应重写的owner记录。

# 本轮实际完成的独立检查

| 检查 | 本轮结果和证据 |
| --- | --- |
| C0+八路径独立重建C2 | `qa_support.py`从Git tree读取C0，自行叠七文件加monitor C0窄overlay；140 Core文件，core-files SHA `c64890f898101d5eb66731c513373a615053bb8acc204f0084272c8bc7c52028`，patch SHA `fa64efd112704e6c6aa49c4d7040064827d68f5647b2fe5e576d5ef925c47574`；不复制DEV profile作为QA组成 |
| C2原清理断言 | C0四测试文件原字节；guarded pytest `--noconftest -q -m no_db tests`，**12 passed**，exit0；仅no_db marker warning，`c2-sanitization.log` |
| 原F-001输入复验 | 从首轮QA原fixture复制，仅叠当前预检实现；source、import_model_packages、create_app三入口都以error-namespace/user_not_found阻断，exit0；`original-enum-class-name.log` |
| 原F-002输入复验 | 同样复制原fixture/只换预检；source、完整App/最终routes、configure_mappers及`Ref.probe.mapper.class_ is Probe`通过，JOIN编译指向probe表，exit0；`original-qualified-relationship.log` |
| C2/E1/E2/F组合 | 各exit0；14/15/16/58表，50/52/54/161个method/path，0/0/0/8个descriptor；`profile-*.log`及各metadata-routes.json。E每个冻结Core SHA不变，E/F原14表完整signature不变 |
| 完整F编译与no_db | 原样`compileall.compile_dir('.',quiet=1)`后pytest `-q -m no_db --basetemp <QA>/pytest-tmp`；**304 passed,30 deselected，281.70s，exit0**；`full-no-db.log`。无缩套件、删断言、skip/xfail |
| 完整套件所含F回归 | 新旧依赖/公开符号/冲突、r3 Model分类/扫描顺序反转/双向metadata环、58表recorder/MySQL dialect DDL编译、撤42保旧16、三旧revision、价格BE002/004、HR关闭及5Model、monitor权限隔离、owner guards、GET零写、8descriptor与合成Projection事务均包含于304；没有真实SQL/Projection运行 |
| E1/E2显式迁移 | 独立沿ScriptDirectory拓扑重放到recorder，15/16逐表signature与metadata一致，MySQL dialect编译；撤各自增量后原14表signature不变，exit0；`E1/E2-migration-recorder.log` |
| E2实际ASGI | 真实Core/Probe/Summary API和Schema/Service，合成Session；POST→GET、probeId/probeState camelCase、ProbeDTO继承/ACTIVE key、两owner稳定错误、401/空/未知/跨owner/read-only grants、失败rollback通过，exit0；`E2-ASGI.log`。不能替代B真实FK/事务 |
| Alembic真实CLI离线 | guarded runpy执行`python -m alembic upgrade head --sql`、`downgrade d2f4a6b8c0e2:b8d0f2a4c6e8 --sql`，各exit0；输出59 CREATE TABLE含alembic_version、42 DROP TABLE。只render SQL；`offline-upgrade.sql`、`offline-downgrade.sql`及logs |
| heads/history/预检CLI | 单head d2/单root d4/四revision；裸预检help和显式check-only均exit0且不导入Settings/App/database；`alembic-heads/history.log`、`preflight-cli.log` |
| B入口准备 | 两文件完整只读；guarded compileall和pytest `--noconftest --collect-only -q tests_mysql`，**2 collected**，exit0；`mysql-entry-collect-only.log`。没有调用测试函数/DisposableTarget或任何B动作 |
| 新增文档链接 | 16份任务稳定Markdown本地链接无缺失；git diff --check exit0；code literal路径另发现F-004，不以链接检查通过掩盖 |

# 首轮适用证据与未执行项

本轮未重跑前端pnpm check/test/build。独立逐字核对当前frontend-js下198个src/tests/scripts及
package/lock/Vite配置文件，与首轮QA公开副本完全一致；因此引用其check通过、**46 passed/0fail**、
build exit0（只有既有large-chunk warning）作为未变前端输入的既有独立证据，**不冒称本轮新执行**。
适用性清单和三个旧log SHA见`frontend-prior-evidence-applicability.json`。

本轮发现F-003后，协调者要求尽快正式失败handoff，完成已启动的不受影响检查即可；因此未新启动
390×844中英×日夜四组合浏览器null检查或已有规则Edit→dialog→stub保存。已读取DEV harness输入，
但未启动listener/tab，没有把DEV截图/说明或旧listen EPERM日志当作QA浏览器成功。返工后这一必要
A浏览器项仍须由新的fresh Verification独立完成，GET/PUT失败虽有未变46项实际SFC测试证据也不能
代替窄屏浏览器验收。本轮没有新的运行进程采用/真实后端前端联调结论。

AC-001..006、AC-r2-001..005及AC-r3-001..005中的上述分项通过保留；**F-003/F-004使完整A未通过**。
AC-009/AC-r2-007当前为失败返工handoff。AC-007/008、AC-r2-006仍**未授权、未运行**；整体状态
优先qa_failed，不能改成qa_passed、owner_accepted或deferred complete。

# 完整性、并行工作树与资源

已核对原998基线每条before、五文件返工before/after及132任务增量。当前128条after仍与DEV一致；
其余四份根AGENTS/CODE_INDEX/README pair的当前字节含获批ARCH-AW-001的AW/CA路径/索引同步，
不能声称132全部仍match。它们在本轮entry快照时已经是当前值，BE005的energy/模块合同片段保留。
本轮另只读核对AW spec r1批准收据/R7/allowlist，确认该共享文档同步在其批准范围；独立从BE005
baseline+精确patch重建四份DEV handoff文档，对照差异保留为`shared-root-docs-drift.json/.patch`。
不覆盖AW内容、不把AW增量计为BE005、不把F-004归因并行任务。

pre-checklist审计时54 protected逐项SHA全部unchanged；最终写入审计时52仍匹配，ROADMAP pair刚被
并行AW按其已批准R7同步（英文45c71a→4da6d4，中文5fc78c→07c8a1）。这是单独列出的共享保护面
差异，不是BE005/QA写入；完整before/after归final-integrity.json。spec/tasks、五返工源/测试/合同文件、
旧history及两代delta/patch未变。本轮entry 1356源码文件map与最终审计之间的其他变动限于已知并行automation-world和协调者
PLAN面，详见`pre-checklist-integrity.json`；本角色未写它们，也不宣称整个共享工作树静止。
当前checklist是本角色唯一仓库写入。审计最初因这四份并行根文档差异失败，随后保留/分类该差异而非
放宽实现指纹；没有修任何项目文件。一次只读ps受sandbox EPERM，未升级执行，也不依此推断运行状态。

证据保留在本轮专属tmp，含脚本、完整输入、guard、commands、reports、SQL与log；关键失败输入/
诊断和结论同时写在此checklist。`qa-evidence-sha256.json`覆盖本轮证据，最终SHA由handoff消息提供。
首轮QA目录、DEV历史与返工目录、协调者protected map/B提案仍有审计用途，均保留，本角色不清理。
本轮所有已启动测试命令均已结束；没有新建listener、浏览器tab、分支、worktree或待关闭持久服务。

# 当前handoff与后续gate

1. **QA failure -> Development：** 在精确r3范围内修复F-003的正常package/relative module alias来源
   解析及F-004索引路径，保留本轮完整输入/对照和两代失败历史；不得用新命名/注解限制、虚假依赖或
   删除断言规避。提交新的实现/回归/精确delta/tasks developer_handoff；QA没有自修。
2. **协调者 -> 新fresh Verification：** 串行启动，复验F-003两个输入与合法/冲突对照、F-004、原
   F-001/F-002、完整A，并补完独立窄屏四组合和已有规则浏览器保存。不能以本轮304替代修复后结果。
3. **结果 -> Human Owner：** 当前独立结果qa_failed；A通过后才另交具体disposable MySQL8.4.6 /
   Docker操作清单申请B批准。B AC和Human Owner最终验收继续保留，当前均未授予。B提案README仅
   是未执行准备；本轮从未执行DB/SQLite、在线Alembic、任何Docker命令、真实API/Projection/PLC、
   部署、Git refs或push。

---

# 首轮失败报告历史（全文原字节保留；以下不是当前元数据或本轮命令）

Task ID: ARCH-BE-005
Revision: r3
Status: qa_failed
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: A存在F-001/F-002源码合同失败，返回Development返工；B未授权未执行，Human Owner最终验收待后续fresh-context复验
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Context: fresh；实际命名verification角色，未继承Development对话推理
Updated: 2026-10-14

# 独立结论与身份

**本轮verdict为`qa_failed`，A未通过。** 原有完整套件通过，但独立补充的两个普通模块反例分别证明
错误合同漏检和合法限定Model关系的owner误判；这两项必须由Development修复后另启fresh-context
Verification。本轮没有修改实现、测试、spec、tasks、配置或六个索引，唯一仓库写入为本checklist。

本次实际选择Verification profile，contract_only。`.codex/agents/verification.toml`声明
`gpt-6.1-sol` / `max`，这是配置证据，未另行声称运行模型/effort探测、平台ACL或强制路由。
主协调者提供了approved bundle、工作树、完整任务delta和DEV输出；其阶段摘要只用于定位输入，
结论以本轮独立读文件和执行结果为准。下方DEV结果明确与QA实际运行分开。

已消费根AGENTS、README/PLAN pairs、canonical lifecycle workflow、Verification TOML、完整r3/r2/r1
spec及完整tasks，backend/app及auxiliary/energy/monitor最近说明、相关前端说明和实现/差异。
审计使用project-governance、aiis及CONTRACTS、backend-arch的LAYERS、RESPONSE_CONTRACT、
MODULE_REGISTRATION、DATABASE_AND_MIGRATIONS、DATA_GOVERNANCE、AUTH_SECURITY、OPERATIONS_TESTING；
前端窄面使用frontend-ui的FRAMEWORK/DESIGN和i18n-workflow；结构/头部使用code-document-indexer，
均只用于验证。没有加载或执行Docker、Worker、Rust等本轮未触达表面的操作流程。

# 锁定的交接与环境

| 输入 | 本轮核对结果 |
| --- | --- |
| 工作树/C0/HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`363b297bffe65e020108f5504766b4fb1ec3b381` |
| 当前生效规格 | r3顶部及批准收据；SHA256 `6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d` |
| DEV源码基线 | 998文件；baseline-files.json SHA256 `fd532d733ef1ecc0f023e2ae7555d5955139a10f114e68cada55cc4f63280709` |
| 精确DEV增量 | 132文件，46新增/9删除/77修改；r3-delta.json SHA256 `c2e56630d9cdca21ed3c674c13850865c3fced27e3064bfbf17b73196f1fc622`；全部before/after与基线/当前文件一致 |
| 精确patch | r3-delta.patch SHA256 `8657ca565d17d3e2af74aeae81e09ef47b69fcc7f2d5ded1b55fc8a3a372e81e` |
| 保护面 | 协调者54文件map逐项核对无变化；包括三旧revision、database/settings/auth/CA/锁文件和历史bundle |
| QA专属资源 | `/private/tmp/arch-be005-r3-qa-QY6jUF/`，未复用或修改DEV证据目录 |
| 项目运行时 | 既有backend/.venv及uv.lock；Python 3.13.3，macOS 15.7.7 arm64；SQLAlchemy 2.0.48、Alembic 1.18.4、FastAPI 0.135.1、pytest 9.0.2、Pydantic 2.12.5 |

A profiles不含真实env、数据库/运行数据、依赖副本或日志。公开process参数明示TESTING，MySQL
占位`127.0.0.1:1`，writer/mock/bootstrap关闭；没有安装依赖。QA guard在应用导入及pytest collection
之前拒绝SQLAlchemy同步/异步connect/raw_connection、各可用DBAPI及SQLite connect，并拒绝原始
socket连接。嵌套profile子进程使用同一guard；仅把生成器写死的cache/pycache路径重定位到QA目录，
测试源码、选择条件及断言未改。全程无被guard记录的连接尝试。

F保留原共享conftest，实际执行`-m no_db`使autouse数据库fixture早退；未运行任何建库/drop/create_all
或数据库测试。前端公开副本只链接项目现有node_modules，build参数为公开空page grants、mock false。

# F-001：错误值检查依赖枚举类名，漏过声明/namespace/Core冲突

**优先级P1，阻断AC-r2-001 / AC-r2-003。**

位置：[module_preflight.py](../../backend/app/module_preflight.py:283)。当前只有类名含`Error`，或者某
成员值已在manifest.error_codes中时，才扫描这个StrEnum。随后用被扫描的local_errors与声明比较。
当合法Python错误枚举采用其他类名且声明为空，两边同时为空，namespace和Core碰撞检查一并漏过。
[BusinessException](../../backend/common/exceptions.py:16)接受所有非空StrEnum，这是获批窄合同，
不能依赖异常构造器替预检发现声明问题。已批准规格没有要求错误类名必须含Error。

独立fixture从冻结E1派生，Core SHA不变，只改合成模块以下输入：

```python
# app/admission_probe/error_codes.py
from enum import StrEnum
class Failure(StrEnum):
    INVALID_VALUE = "user_not_found"  # 与现有Core错误重复且没有模块namespace

# manifest的其他字段保留，改为：
error_codes=()

# services/async_item.py使用该枚举：
from app.admission_probe.error_codes import Failure
raise BusinessException(Failure.INVALID_VALUE)
```

应有结果：源码/组合预检定位未声明错误、非法namespace或Core冲突并阻断。
实际结果：`check_source('.')`接受；完整`import_model_packages()`和`create_app(testing=True)`接受；
ASGITransport对`POST /api/v1/admission-probe/items`发送`{"itemLabel":" "}`，实际返回：

```json
{"code":400,"message":"user_not_found","data":null,"errorCode":"user_not_found"}
```

HTTP为200。它把新模块错误复用成Core错误，却没有任何error_codes声明或碰撞诊断，违反v1错误归属。
没有真实HTTP监听或数据库调用。复现程序exit0表示**成功观察到实现失败**，并非该接入应通过。
完整输入在`repros/enum-class-name/`，执行payload/log为
`repro-undeclared-error-enum.py` / `repro-undeclared-error-enum.log`。

# F-002：限定relationship丢失模块路径，同名Model被错误归属

**优先级P2，阻断AC-r2-002及r3公开Model/metadata owner正确性。**

位置：[module_preflight.py](../../backend/app/module_preflight.py:274)以裸类名建立全局classes字典，
[关系解析](../../backend/app/module_preflight.py:339)又把限定字符串截为末级类名。不同owner均定义
常见类名`Item`时，后扫描者覆盖前者，即使关系使用SQLAlchemy支持的完整路径仍指向错误owner。

独立fixture由冻结E2派生；probe/summary本来各有`Item`。新增QA专用七包`admission_ref`、显式v1
manifest和仅在tmp的显式revision `e3a5c7e9b1d3`（down E2，未在线执行）。该模块没有HTTP API，
`requires=()`、`model_requires=("admission_probe",)`，公开自己的`Ref`。核心Model输入为：

```python
class Ref(Base):
    __tablename__ = "admission_refs"
    id: Mapped[int] = mapped_column(primary_key=True)
    probe_id: Mapped[int] = mapped_column(ForeignKey("admission_probe_items.id"))
    probe: Mapped["app.admission_probe.models.item.Item"] = relationship(
        "app.admission_probe.models.item.Item"
    )
```

应有结果：FK及relationship都属于admission_probe，现有model_requires满足，不要求虚假的summary边。
实际`check_source('.')`阻断，诊断原文：

```json
{"identifier":"app.admission_probe.models.item.Item -> admission_summary","location":"app/admission_ref/models/ref.py:8","module":"admission_ref","other_owner":"","stage":"undeclared-model-dependency"}
```

为独立确认输入本身合法，在同一拒绝DB的进程中直接导入这些Model定义、执行`configure_mappers()`，
并断言`Ref.probe.property.mapper.class_ is Probe`，全部通过；实际目标原定义模块是
`app.admission_probe.models.item`。`select(Ref).join(Ref.probe)`编译为：

```sql
SELECT admission_refs.id, admission_refs.probe_id
FROM admission_refs JOIN admission_probe_items ON admission_probe_items.id = admission_refs.probe_id
```

这只证明ORM定义/目标及SQL编译，无SQL执行或App就绪声明。补写无实际引用的summary依赖会掩盖
owner错误，不能作为合规修复。完整输入在`repros/qualified-relationship/`；执行payload/log为
`repro-qualified-relationship.py` / `repro-qualified-relationship.log`。本复现exit0同样表示观察成功。

# 本轮实际命令与通过证据

下表均是QA新执行，不沿用DEV通过结果。完整cwd/命令/退出码及payload SHA记录于`commands.jsonl`；
public process参数和所有guard实现见QA目录`qa_support.py` / `qa_execute.py`。

| 检查 | 实际入口与结果 |
| --- | --- |
| 独立重建C2/E/F | `python3 .../qa_support.py`，exit0；直接读取C0 Git tree并按八路径批准overlay重建C2；E只加已阅读的固定合成源码/显式revision，F从公开源码独立复制 |
| C2来源冻结 | 140 Core文件；core-files.json SHA `334e8c53797ab412c4dd5892c716f08f912acd7f91dfed2106a372e0cbe98ec6`，core-patch.diff SHA `317937d0e08efaf1461227c13a405e865da43e2539eb03689df3dd2cc2fe07b1`，与DEV一致；无common.data_keys或补回的业务ErrorCode |
| 原Core sanitization | guarded `uv run --offline --frozen --no-sync python .../qa_execute.py .../c2-sanitization.py`；payload原样调用pytest `--noconftest -q -m no_db tests`，C0四份测试文件字节不改；**12 passed**，exit0；仅既有no_db marker warning |
| C2/E1/E2/F实际组合 | 同一guarded uv入口执行`profile-C2/E1/E2/F.py`，各exit0；实际14/15/16/58表，50/52/54/161个method+path，0/0/0/8个descriptor；全Model导入、configure_mappers、最终routes检查通过 |
| Core不变 | E1/E2所有冻结Core文件SHA逐项一致；E1/E2/F中的原14表完整签名与C2一致，未以表数替代签名 |
| 完整F编译及no_db | guarded uv运行`f-full-no-db.py`：先`compileall.compile_dir('.',quiet=1)`，再`pytest.main(['-q','-m','no_db','--basetemp',QA专属路径])`；**286 passed,30 deselected,76.18s**，exit0；未缩套件/skip/xfail |
| F迁移/价格/Projection回归 | 包含于上述完整286：四revision recorder、MySQL dialect DDL编译、58表完整签名、撤42保旧16、single root/head；价格BE004/guards、auxiliary/monitor GET零写、8descriptor与本地合成business/cursor/audit事务回归通过 |
| 价格源码保护 | 六个迁移文件与DEV基线auxiliary已验收版本比较，除app路径及文件头归属替换外逐字相同；价格两表、三route唯一energy owner；不是重新实现旧价格 |
| 恢复Model来源 | 四个auxiliary及两个monitor类AST与只读旧源原定义一致；旧12个monitor Model未进入本批F；Core事实及保护文件不变 |
| 前端模块检查 | QA公开副本`pnpm --config.verify-deps-before-run=false check:modules`，exit0 |
| 前端实际SFC回归 | 同工具链`test:modules`，**46 passed,0 failed**，exit0；包含实际编译SFC的中英null/禁止误PUT、已有规则GET/PUT、GET及PUT失败反馈；不是只凭源码正则 |
| 前端构建 | 同工具链`build`，公开空page grants/mock false，exit0；仅既有large-chunk warning；产物只在QA副本 |
| 增量/写入审计 | `git diff --check` exit0；写checklist前全源码快照与QA入口相比零变化、132条DEV after仍一致、54保护文件仍一致；未改六索引/共享dirty/并行AW001 |
| 两项反例 | guarded uv分别执行以上两个repro payload，exit0，日志明确观察到错误接受/错误拒绝；其实现结果判fail |

# AC审计与未执行边界

| AC | 本轮状态/限制 |
| --- | --- |
| AC-001/002 | 公开F导入/组合、HR关闭仍有5表、demo关闭、权限401/403/404及价格唯一owner的完整回归通过；不能据此宣布整个v1接入合同正确 |
| AC-003 | BE004/错误闭包、GET零写及双语实际SFC行为回归通过；新模块错误声明/冲突被F-001否定 |
| AC-004/005 | 286中的recorder/DDL编译/旧16/三旧revision、8descriptor和合成事务通过；没有在线迁移或启动Projection |
| AC-006 | 完整no_db/compileall/前端check/test/build已独立通过；本轮发现阻断后未开展独立真实浏览器窄屏四组合、新增链接专项或CLI offline SQL render，不能把DEV对此的输出/说明冒充QA复跑 |
| AC-r2-001/003 | **fail：F-001**；其余公共符号/同壳/路由/权限冲突既有正负矩阵通过不能覆盖漏检 |
| AC-r2-002 / r3 Model依赖边界 | **fail：F-002**；原按models/CRUD/Service分类、disabled/runtime及双向metadata环的既有矩阵通过，限定同名Model owner仍错误 |
| AC-r2-004/005及AC-r3-004 | 独立C2冻结及E/F组成/14表签名已核对；E1 ASGI合同在完整套件中实际运行；E2额外组合ASGI/显式E migration replay未在本轮另复跑，A整体失败 |
| AC-r3-001/002/003/005 | system公开raw Model与显式model_requires、r3业务声明迁移等既有回归通过；完整r3交接验收受F-001/F-002阻断 |
| AC-007/008、AC-r2-006 | **未授权、未运行。** 未执行任何DB（含SQLite）、在线Alembic、Docker命令（含只读）、真实API/Projection/PLC、部署/refs/push；不是deferred complete |
| AC-009、AC-r2-007 | 当前已提交独立失败证据；整体handoff回Development，不能进入qa_passed或Human Owner最终接受 |

已阅读DEV的handoff-integrity、final-profiles相关脚本及日志索引、E recorder/组合ASGI脚本和两个
tests_mysql入口源码。DEV声称的offline SQL、浏览器四组合和B入口collect-only是**已提供DEV证据**，
本轮未独立执行这些项；tests_mysql的测试函数一次也未调用。父协调者B提案
`/private/tmp/arch-be005-r3-b-proposal/`只是未执行草案，不是批准或运行事实。本轮失败后不以此申请
B操作来绕过A门禁，也不把286/46通过改写为“全部模块已可用”。

# 证据保留、限制和下一handoff

QA证据清单`qa-evidence-sha256.json`的SHA256为
`f13b3145fd49ed7d759a792ee8c38945a31a4d114580c513a9ee4b81123ff1d2`，覆盖关键脚本、运行日志、
profiles报告及两个反例输入；核心输入、实际失败响应、诊断和命令已写入本checklist，避免只依赖临时路径。
`entry-integrity.json`、`pre-checklist-integrity.json`记录独立完整性审计。QA临时目录、DEV基线/delta/
logs及协调者protected map仍承担返工与复验依据，须保留；本角色不清理它们。

本轮没有创建后台listener、浏览器tab、分支或worktree；两条测试命令进程均已完成。没有持久服务
资源待关。前端dist、pycache、uv-cache和公开profiles均只位于QA专属tmp目录；它们不构成交付包或部署。

1. **QA -> Development：** 按精确r3范围修复F-001/F-002，保留此失败历史及反例；提交更新实现/
   回归/精确delta和新的developer_handoff。QA没有指定通过增加虚假依赖、命名白名单或删断言来规避问题。
2. **协调者 -> fresh Verification：** 返工handoff后实际另启fresh context，复验两个反例、完整A及
   本轮尚未独立完成的必要A项。不得在此失败turn继续自修实现或以DEV自检替代复验。
3. **QA -> Human Owner：** 当前独立结论为qa_failed；A修复并通过后，B才另交具体可丢弃MySQL8.4.6 /
   Docker操作清单供批准。B证据和Human Owner最终验收仍是后续gate，当前均未授予。
