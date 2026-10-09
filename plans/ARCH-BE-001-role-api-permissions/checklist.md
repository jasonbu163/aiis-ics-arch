Task ID: ARCH-BE-001
Revision: r3
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: ARCH-BE-001 r3 独立静态 Verification 为 qa_passed；交 Human Owner final acceptance，pending

Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Date: 2026-10-09
Verifier: backend_permissions_r3_qa
Fresh Context: yes；新命名 Verification 从批准 spec、完整 tasks/checklist、当前文件、公开 diff 和可用输出独立核验，不继承 Development 对话推理
Profile Enforcement: contract_only；fresh-context 调用、串行 handoff 与写入审计为合同控制，不宣称平台 ACL / 强制路由

# r3 当前 verdict

**qa_passed**，仅针对 ARCH-BE-001 r3 六 env 恢复英文分组标题、原样式分隔线和必要空行的静态范围。
无本轮实现 failure 或环境 blocker，无需 Development 返工。Human Owner final acceptance **pending**。
完整 r2 与 r1 QA 通过、返工及首轮失败记录作为本文后缀逐字保留，不自动继承为 r3 verdict。

## 输入与来源限制

- 完整读取根 AGENTS、根 README/PLAN pair、backend README/PLAN pair、canonical lifecycle workflow、
  verification TOML、完整 r3 spec/tasks 和原 checklist；backend/plans/.codex 无更近 AGENTS。
  spec 当前 r3 owner_approved，tasks 当前 r3 developer_handoff。使用 project-governance、backend-arch
  及 AUTH_SECURITY，仅用于验证；不扩展到 r1/r2 功能重审或行为测试。
- 工作树 /Users/jason/Desktop/DreamCode/aiis-ics-arch，HEAD
  ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec；被验证交付为未提交工作树。
  核对三份公开 HEAD 原英文标题、当前公开 example diff、六文件有限内容及 DEV 只读 checker。
  HEAD 累计 diff 包含 r1/r2 的权限/注释变化，不能当作独立 r3 前值快照。
- **全内容保留的历史来源是 DEV**：独立审阅 restore_groups.py，确认写前在同进程内存保存六份
  原文、全部预检后写入，写前/写后比较 68 条完整赋值与去新增标题/分隔线/空行后的原非空行
  序列，并比较 README pair 原字节；输出不含秘密，无真实 env 备份或秘密摘要保存逻辑。
  tasks 记录该操作 exit 0。QA 没有 r2 真实 env 原文，不伪称独立重建修改前秘密或全部非空行。
- QA 独立重算当前章节、边界、语法、唯一 key、逐 key 英文用途说明和权限；公开 example
  解析值另与 r1 QA 的公开快照比较相同。真实其他值仅在内存读取/比较，不输出、不备份、不 hash。

## 验收标准核对

| 标准 | 结果 | 证据与限制 |
| --- | --- | --- |
| AC-r3-001 分组恢复 | passed | 六文件均恰有 Syntax/App/Runtime/Auth/Logging/Database Routing/MySQL/PostgreSQL/SQLite/MSSQL/Bootstrap 十一标题；与三份公开 HEAD 原英文标题顺序相等；每标题上下为原80等号分隔行，共22行，非首组之前有空行。十个配置组首 key 正确，无重复标题。 |
| AC-r3-002 全内容保留 | passed with explicit DEV historical provenance | 当前六文件各68唯一key、英文逐项说明符合r2映射，dotenv无解析错误；三真实supervisor为 ["monitor","system","control-agent-read"]、operator为 ["monitor"]，三example为 []/[]，subset成立。全部原赋值行和非空内容前后相等依据为上述DEV受控内存比较；QA未独立生成过去状态。 |
| AC-r3-003 限定变更 | passed for observable static scope | 三真实env仍ignored；公开example当前值等于r1公开QA快照，累计公开diff已审；159Python源码/测试及pyproject/uv.lock仍等于历史公开QA快照。QA只写本checklist，写前后公开脏文件及三真实env在内存比较，其他文件均未变；git diff --check通过。README在r3写前后不变依据为DEV比较。 |
| AC-r3-004 独立交付 | passed | 新fresh-context QA记录精确r3、静态命令/结果、历史证据来源和资源；旧checklist全文逐字保留。r3不重跑功能测试、不修改实现；结果只交Human Owner最终验收。 |

既有组差异按 spec 保留：真实三 env 的两项角色权限数组原位于文件末尾，本次仍在 Bootstrap
标题之后；公开 examples 位于 Auth。真实 Auth/Bootstrap 当前分别4/20项，公开为6/18项。
不为统一组计数移动已有赋值；十个标题都按现有组首 key 插入，满足禁止重排原内容的约束。

## 命令、环境与结果

环境：macOS 15.7.7 arm64，uv 0.7.8，项目既有 CPython 3.13.3；cwd 仓库根。
uv 使用 --offline --no-sync 和既有临时cache，不安装依赖、不导入 Settings/应用。

| 检查 | 实际命令/方法 | 退出码与结果 |
| --- | --- | --- |
| 审后复用只读章节 checker | PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be-001-r3-dev/uv-cache uv run --offline --no-sync --project backend python /private/tmp/arch-be-001-r3-dev/check_groups.py | 0；6×11标题、22分隔、组首边界、68赋值及目标权限通过。 |
| 当前注释/未变源码静态 checker | PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be-001-r2-dev/uv-cache uv run --offline --no-sync --project backend python /private/tmp/arch-be-001-r2-dev/check_current.py | 0；6×68key英文用途说明、权限与ignored正确；既有README 68key/10链接检查和159Python源码/测试及依赖清单比较通过。仅复用既有静态检查，不进行功能重审。 |
| 独立窄范围复核 | 同r3 uv前缀 python -；stdin只导入 pathlib/io/dotenv.parser/subprocess/sys/json/re，独立核对十一组、空行、首key、唯一key与解析结果 | 最终0；六文件章节/边界/68唯一key/dotenv语法/权限subset通过；公开值等于r1 QA公开快照。真实两数组原末尾位置保留。 |
| 输入/环境/公开diff | git rev-parse HEAD；uname -m；sw_vers -productVersion；uv --version；git diff -- backend/.env.example backend/.env.docker.dev.example backend/.env.docker.prod.example | 0；HEAD/环境如上，公开累计diff含r1/r2历史变化，未当作r3独立基线。 |
| 忽略与格式 | git check-ignore backend/.env backend/.env.docker.dev backend/.env.docker.prod；git diff --check | 0；真实三文件均ignored，写前/后格式检查通过。 |
| QA写入/历史审计 | python3 -；写入时在内存比较git ls-files --modified --others --exclude-standard -z所列公开文件及真实env字节；旧checklist完整后缀比较 | 0；仅本checklist变化，零新增公开仓库文件，三真实env未被QA修改；完整r2/r1历史逐字保留。 |

独立脚本初次误假定真实和公开 Auth/Bootstrap 组计数相同，exit 1；只输出无值的组计数后发现
上述既有位置差异，依 spec 的保留原序规则修正临时 stdin 断言后 exit 0。这是 QA 检查假设问题，
不是实现 failure，未修改任何配置。其余静态检查无失败；未运行 pytest/compileall或新行为测试。

## Acceptance audit、资源与 handoff

- 本r3当前六env格式静态结果可交Human Owner验收，qa_passed；无failure/blocker，最终验收pending。
  全原文历史保值采用已声明DEV来源；真实运行加载、进程覆盖、服务重启/登录、数据库或设备效果
  不在本轮证据内。本轮未执行任何服务、端口、Docker、DB/schema/bootstrap、PLC/CA、发布或Git refs/推送。
- QA未新建资源目录、分支、worktree、脚本文件或服务；独立脚本通过stdin执行，复用既有uv-cache。
  /private/tmp/arch-be-001-r3-dev/ 的只读 checker与恢复脚本供审阅；恢复脚本是一次性写入工具，
  QA未重跑。r2-dev/r1 QA公开快照支持现有比较，需保留到Owner验收与协调者依赖核对。
  本文已持久记录结果和来源，临时路径不是唯一证据；QA不清理任何资源。
- QA -> Human Owner（经主协调者relay）：ARCH-BE-001 r3 qa_passed，final acceptance pending。
  协调者可机械同步索引；QA未修改spec/tasks/索引/实现/测试/项目配置。

# r2及r1完整 QA 历史（原文保留，非 r3 当前 verdict）

Task ID: ARCH-BE-001
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: ARCH-BE-001 r2 独立静态 Verification 为 qa_passed；交 Human Owner final acceptance，pending

Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Date: 2026-10-09
Verifier: backend_permissions_r2_qa
Fresh Context: yes；从批准 spec、完整 tasks/checklist、当前实现、diff 与可用输出独立核验，不继承 Development 对话推理
Profile Enforcement: contract_only；fresh-context 调用、串行 handoff 与写入审计为合同控制，不宣称平台 ACL / 强制路由

# r2 当前 verdict

**qa_passed**，仅针对 ARCH-BE-001 r2 获批的六 env 注释、三真实文件权限迁移和双语配置说明静态范围。
无本轮实现 failure、环境 blocker 或待 Development 返工项。Human Owner final acceptance **pending**。
r1 失败、返工和通过记录在本文后半部逐字保留；r1 verdict / 行为测试不作为 r2 自动通过依据。

## 输入、范围与证据来源

- 完整读取根 AGENTS、根 README/PLAN pair、backend README/PLAN pair、canonical lifecycle workflow、
  verification TOML、完整 r2 spec/tasks 与既有 checklist；backend/plans/.codex 无更近 AGENTS.md。
  spec r2 为 owner_approved，tasks r2 为 developer_handoff。使用 project-governance、backend-arch
  及 AUTH_SECURITY / DATABASE_AND_MIGRATIONS，均仅用于核验；本轮无源码/索引/UI/容器实现改动。
- 工作树 /Users/jason/Desktop/DreamCode/aiis-ics-arch，HEAD
  ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec；被验证交付为未提交工作树。
  阅读公开 example diff、当前配置消费者、DEV 静态 checker 与编辑器；不执行编辑器。
- 本轮独立有限读取真实三 env：仅输出权限结论、文件/key 数和比较统计；未输出其他活动值、
  完整旧授权、秘密或秘密 digest；未备份真实 env。以 python-dotenv 纯 parser 解析文本和 AST 读取
  Settings 定义，不导入 Settings / 应用，不读取进程配置来建立实际服务结论。
- **真实 env 历史前值来源**：QA 没有旧真实 env 基线。三真实文件非权限赋值原文、顺序、集合保留
  及旧有效授权由 tasks 的 Development 同进程写前/写后内存比较证明。独立审阅
  edit_and_check.py：写前保存 rows 于内存，全部文件预检后才写，写后重新读取比较，输出不含值，
  没有真实 env 备份/digest 保存逻辑。DEV 已如实记录 env 比较完成后 README 生成阶段 exit 1；
  后续仅收 EOF 空行。该历史结论明确为 DEV 证据，QA 未伪称独立重建过去状态。
- **公开 example 前值**：QA 独立与 /private/tmp/arch-be-001-qa-rework/backend 中 r1 QA 公开快照
  比较，三文件全部 68 项原始赋值（剥离词法注释）及 dotenv 解析值均相同，包含权限 []/[]。

## 验收标准核对

| 标准 | 结果 | 独立证据与限制 |
| --- | --- | --- |
| AC-r2-001 目标授权 | passed | 三真实文件各 68 个唯一活动 key；新 supervisor 数组严格等于 ["monitor","system","control-agent-read"]，operator 严格等于 ["monitor"]，成员顺序与原始 subset 正确；无旧 key 或旧授权历史文本。monitor 聚合只挂两 GET：/monitor/collector/status、/monitor/realtime/latest，共同受 monitor guard 保护。host/prod operator 与 dev 两角色的授权增量按 spec/tasks 明示，不称等值改名。 |
| AC-r2-002 值保留与语言 | passed with explicit historical provenance | 六文件每个 key 前有同 key 一致的英文用途说明，所有注释为 ASCII 英文；dotenv 独立解析无错误/重复 key，支持引号内 #。语法提示准确说明单/双引号、JSON 外单内双和 True/False；公开三 example 全赋值与 r1 QA 快照相同，两数组仍 []。真实非权限前后保留依据为上述 DEV 受控比较；QA 独立确认当前结果并保留来源限制。 |
| AC-r2-003 说明完整准确 | passed | 两 README 各 68 个唯一 key，与三 example 相同 key 并集精确相等；每行类型、源码缺省、模板值经 AST/example 独立逐项比较，双语列一致，含 18 bootstrap 字段。用途与入口/副作用人工对照消费者；10 本地链接/anchor 有效，代码块平衡。r1 Projection 状态/合同校验事实勘误和权限边界保留。 |
| AC-r2-004 安全边界 | passed for observable static scope | 三真实 env 仍 Git ignored；三公开 example 赋值未变，README 仅使用公开安全值。159 Python 源码/测试及 pyproject.toml/uv.lock 与 r1 QA 快照逐字节相等。本轮 63 个已有公开脏文件在 checklist 写前零变化；QA 仓库写入仅本 checklist，未执行服务/DB/Docker/设备动作。真实历史基线、服务是否已加载新配置不作独立证明。 |
| AC-r2-005 独立交付 | passed | 新 fresh-context Verification 对精确 r2 独立解析与核对，命令/结果和历史证据来源明确；r1 完整原文作为后缀保留，本轮不重跑 r1 行为测试。qa_passed 仅交 Human Owner，最终验收 pending。 |

## 关键语义对照

- Settings 源码缺省与公开模板值分别核对，而非把当前本机值写入表格。APP_NAME/APP_VERSION/DEBUG
  等无源码缺省字段标必填；LOG_MAX_BYTES 算术默认表达式、None 字段、三个 RESET_PASSWORD=False
  及空 bootstrap 密码模板均准确。66 个非权限真实活动值未对外展示。
- backend/settings.py:83 的 PRIMARY_DATABASE 优先于兼容 DATABASE_TYPE，别名及 enabled 校验正确；
  :131/:156 的普通 async/sync URL 使用同一主库。:180 的 ROOT_DATABASE_URL 使用独立 MySQL
  root 账号和共用 host/port；README 未把它当 Docker root provisioning 授权。
- settings.py:136/:161 仅 MySQL URL 随 TESTING 切入测试库，README 明确不是所有数据库的沙盒。
  core/registrar.py:156-168 在普通入口测试模式关闭 Projection runtime；单 writer 是部署约束，
  不是已证实的跨进程锁。runtime.py 只提供进程内 guard，未据文档扩称跨宿主强制。
- main.py:31-38 只设置进程 TZ 并在可用时调用 tzset，不迁移 DB 时区；main.py:66 与 run.py:21
  支持生产 worker 配置以及 frozen/dev 强制单 worker 的说明。
- scripts/maintenance/ensure_admin_user.py:35-74 的 enabled/非空密码、创建/既有账号、
  reset 密码/重新激活及仅补空 name/role 与双语说明一致；main.py:41 在维护分发前组合 app。
  普通启动/登录不执行 bootstrap。本轮只阅读，不运行维护入口。
- 当前 monitor 两 GET 与 app/monitor/manifest.py 的 monitor permission 一致；
  system 含用户管理写入、control-agent-read 是 action-scope 查询、Projection actor_user_id
  不构成角色检查的 r1 更正保持。未改变任何 guard、路由、Service 或权限粒度。

## 命令、环境与结果

环境：macOS 15.7.7 arm64，uv 0.7.8，项目既有 CPython 3.13.3；cwd 为仓库根。
项目解释器用 offline/no-sync，不安装依赖、不修改锁。辅助文件/差异分析用标准库 Python。

| 检查 | 实际命令/方法 | 退出码与结果 |
| --- | --- | --- |
| 审后复用 DEV 只读 checker | UV_CACHE_DIR=/private/tmp/arch-be-001-r2-dev/uv-cache uv run --offline --no-sync --project backend python /private/tmp/arch-be-001-r2-dev/check_current.py | 0；6×68key、英文逐项说明、真实3/1/example[]、三真实ignored、两README各68key、10链接/anchor、代码块与引号内#检查通过；159源码/测试和依赖清单等于r1 QA快照。 |
| 独立解析/表格验证 | PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be-001-r2-dev/uv-cache uv run --offline --no-sync --project backend python -；stdin 仅导入 pathlib/io/collections/ast/json/re/sys 与 dotenv.parser | 0；6×68唯一key，目标顺序/subset与无旧key；三example原始/解析赋值均与r1 QA快照相等；两README精确68key，类型、源码缺省、模板值及双语对应逐行通过。未导入应用。 |
| 消费者静态核对 | cat / rg 读取 settings.py、main/run、registrar、JWT、common/log、database engine/session、bootstrap、Projection runtime/batch 和 monitor router/manifest；读取公开 example git diff | 最终读取/检索 0；关键语义见上节。首次 rg 猜测了不存在的 log/connection/session/bootstrap 文件路径，exit 2，未运行后续 cat；经 rg --files 定位后实际路径读取 exit 0，非实现 failure。 |
| 环境/输入身份 | git rev-parse HEAD、uname -m、sw_vers -productVersion、uv --version；独立解析命令报告 sys.version | 0；环境/HEAD 如上。 |
| 格式检查 | git diff --check，checklist 写前与写后 | 0。 |
| QA 写入与历史审计 | python3 -；git ls-files --modified --others --exclude-standard -z 的公开文件摘要在 QA 写前/后内存比较；完整旧 checklist 后缀比较 | 0；写前63文件零变化；写后仅本checklist变化、零新增公开仓库文件；r1原文逐字保留。摘要排除 ignored 真实env，不计算秘密hash。 |

本轮没有新增实现测试，不执行 r1 pytest/compileall；只读配置/文档修改采用上述静态检查。
没有实际服务启动、端口、真实登录、数据库/schema/bootstrap、Docker、PLC/CA、发布、Git refs 或推送。

## Acceptance audit、资源与 handoff

- 可交 Human Owner 验收：r2 文件静态授权、英文注释、公开模板赋值保留和双语 68key 说明，
  独立 verdict 为 qa_passed。无 r2 failure/blocker；不覆盖 r1 历史结果或授予 owner_accepted。
- 尚未证明且仍独立 gate：现有服务加载/进程覆盖、重启、真实登录/DB/设备/部署与最终验收。
  操作者仍须审查实际入口和进程中的旧 key/新数组覆盖；仅修改文件不证明运行授权已切换。
- QA 无新建分支、worktree、服务或 QA 产物目录；仅复用 DEV 只读 checker/uv-cache，独立验证脚本
  通过 stdin 运行。/private/tmp/arch-be-001-r2-dev/ 根仅 edit_and_check.py、write_readme.py、
  check_current.py、uv-cache；审阅工具无真实env备份/旧授权全文/秘密摘要保存逻辑。
- DEV、r1 QA 和 r1 rework 资源继续保留；公开 example/159源码比较仍引用 r1 QA 快照，
  临时目录不是唯一持久结论。QA 不清理资源；Owner 验收后协调者核对归属/依赖再收尾。
- QA -> Human Owner（由主协调者 relay）：ARCH-BE-001 r2 qa_passed，final acceptance pending。
  协调者可据此机械同步本任务索引；QA 未写 spec/tasks/索引/实现/测试/项目配置。

# r1 完整 QA 历史（原文保留，非 r2 当前 verdict）

Task ID: ARCH-BE-001
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: ARCH-BE-001 r1 返工经新 fresh-context Verification 独立 qa_passed；交 Human Owner final acceptance，pending

Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Date: 2026-10-09
Verifier: backend_permissions_qa_rework（第二轮）；首轮 backend_permissions_qa 失败历史保留
Fresh Context: yes；不继承 Development 对话推理，从批准 spec、tasks、当前实现、diff 与测试输出独立核验
Profile Enforcement: contract_only；未宣称角色文件系统 ACL、自动路由或强制隔离

# 第二轮返工复验：当前 verdict

**qa_passed**，仅针对 ARCH-BE-001 r1 当前公开源码 / no-DB 范围。F-001、F-002 已由本轮独立证据关闭；
无本轮实现 failure 或环境 blocker。首轮 `qa_failed`、复现输入及结果在本文后半部原文保留，
不是撤回或改写首轮事实。Human Owner final acceptance **pending**。

## 输入、独立性与当前快照

- 本轮为新的命名 Verification、fresh context；未继承 Development 对话推理。完整读取根 AGENTS、
  根 README/PLAN pair、backend README/PLAN pair、backend/app README pair、canonical workflow、
  verification profile、完整 spec/tasks/checklist，独立审查当前源码、diff、四个测试与 conftest、
  DEV runner 和 pytest-rework.log。backend、plans、.codex 未发现更近 AGENTS。
- 使用 project-governance、backend-arch（AUTH_SECURITY / MODULE_REGISTRATION）、code-document-indexer，
  均仅用于核验；未加载不适用的 UI、Worker、打包或脚本实现 skill。profile 为 `contract_only`。
- spec r1 为 owner_approved；PM 对 Projection 现状作同 r1 事实勘误，没有新增 guard 或 Service 改动。
  tasks 最新为返工 developer_handoff。工作树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，
  HEAD `ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec`，未提交 working-tree diff。
- 新建 `/private/tmp/arch-be-001-qa-rework/backend`，从当前工作树复制 165 个公开 Python 源码/测试、
  config/plc_snapshot_policy.yaml、入口、pyproject/uv.lock 和三份 example；`.env` 仅由公开
  `.env.example` 复制。未复用首轮失败快照。复制前后及测试后均与仓库逐文件、逐字节核对一致。
- 排序 `relative_path + space + SHA256`、以换行连接后的聚合 SHA256 为
  `3a6782e8cdd9580c453c919e611100e26243f5a77d2cca59194db70727df0070`；本轮 settings.py SHA256 为
  `b8d30d4fdb252de5b69d8e386574b6b68ce4d8d8fb9e07055117f9b5a08aefd5`。
- runner 在任何 Settings 导入前，依据其 AST 清除本进程中的项目配置字段与旧 key；确认实际导入
  `/private/tmp/arch-be-001-qa-rework/backend/settings.py`。audit hook 拒绝三个真实 backend env 的
  resolved path open，以及 socket.connect / bind / getaddrinfo；拒绝测试对仓库写入，禁用 bytecode
  写回。pytest 禁用自动插件发现，仅显式加载项目既有 pytest_asyncio；collection 检查 51 项均有
  no_db，conftest 自动建/清表分支未执行。ASGI 请求使用 stub 身份，不启动监听服务。

## F-001 关闭证据

`backend/settings.py:195-210` 现在从既有 env_settings / dotenv_settings 的 key inventory 取 OR，
通过独立派生 source 优先提供存在性字段；普通 init/process/dotenv 对同名 bool 的 false 不能覆盖。
没有额外 dotenv 读取；两新数组仍保持 init > process > dotenv。`core/registrar.py:149-154`
在建立 app 前消费该事实。新正式回归包含六组交叉来源负例与新数组优先级回归。

此外本轮独立 runner 使用公开 example，创建真实 Settings 后注入 registrar，实际调用
`create_app(testing=True)`，重放首轮四例并扩展为下列十例；未依赖 DEV 测试断言。

| 活动旧 key 来源 | 同名内部 bool=false 输入来源 | 派生标记 | 实际 app 组合 |
| --- | --- | --- | --- |
| dotenv | 无 | true | REJECTED |
| dotenv | process | true | REJECTED |
| dotenv | init | true | REJECTED |
| dotenv | process + init | true | REJECTED |
| process | 无 | true | REJECTED |
| process | process | true | REJECTED |
| process | init | true | REJECTED |
| process | process + init | true | REJECTED |
| dotenv | dotenv + init | true | REJECTED |
| 仅注释旧 key | init | false | APP_COMPOSED |

九例拒绝均为 `ROLE_API_PERMISSIONS_JSON is retired`，并同时指出两项新变量；
`contract_failures=0`、命令 exit 0。公开旧值为 `{}`；空值/无值声明由正式来源测试覆盖。
重放核心为 `Settings(_env_file=public_fixture, legacy_role_api_permissions_present=False)`，
配合 process/internal false 与 dotenv/process 旧 key 组合，然后 `registrar.settings=configuration`
及真实 `registrar.create_app(testing=True)`；源存在时必须得到迁移 ValueError。

## F-002 关闭证据

双语 README 的 `projection-mapping-manage` 表格及 admin 说明均改为 Service 状态/合同校验；
`backend/README.md:86,92` 与 `README.zh-CN.md:85,91` 明确当前没有额外 role/admin 门槛，
`actor_user_id` 只记录操作者，不构成角色校验。

独立核对 `app/system/api/projection_mapping.py:200-313` 六个管理入口：permission guard 后只传
current_user.id；Service `async_projection_mapping.py:119` 起接收 actor_user_id，并在发布/回滚等
路径执行状态/合同校验，全文无角色门槛。相关 router/Service/manifest 均无 working-tree diff。
未为满足旧描述新增 guard；未执行 Projection 写库。F-002 作为文档 failure 已关闭。

## 当前验收标准核对

| 标准 | 本轮结果 | 独立依据与限制 |
| --- | --- | --- |
| AC-001 输入合同 | passed | 严格数组、缺省/空数组、错误定位、注释/空旧值/新旧共存、dotenv/process检测正式回归通过；上述独立十例确认内部false不再覆盖存在性。错误源码未回显原配置。 |
| AC-002 原始等级 | passed | 有效/未知/disabled operator独有key均在过滤前失败；原始subset及重复精确key回归通过，无自动补权。 |
| AC-003 过滤及告警 | passed | 所有manifest owner及显式user/CA key、共享key任一enabled语义、unknown/disabled WARNING与过滤；resolver消费app同一只读策略，不恢复忽略项、不按请求告警。 |
| AC-004 请求/模块边界 | passed for approved no-DB scope | ASGI stub身份下admin/supervisor通过，operator/未知角色403，未初始化fail closed；仅登录probe、disabled路由/OpenAPI缺席及404、metadata、user/CA独立规则回归通过。Projection边界按真实源码核对，未做DB业务或真实登录。 |
| AC-005 启动/维护边界 | passed for approved stub scope | testing/生产组合负例、开发main:app入口、main两维护stub顺序通过；非法输入在动作前失败，告警允许继续。未启动端口、未调用真实维护。 |
| AC-006 示例与文档 | passed | 三example新数组[]、无活动旧key、五行英文说明一致；双语当前八个key/迁移/来源/重启/bootstrap边界一致，F-002已关闭；8个本地链接/anchor有效。真实env未读/改。 |
| AC-007 交付治理 | passed for audit scope | exact r1、角色文档归属、allowlist及共享差异核对；写checklist前63个已有脏文件摘要不变，DEV写前两README完整前缀保留，CODE_INDEX仅两行本任务新增。QA仓库写入只限本checklist。 |

## 本轮命令、环境与结果

环境：macOS 15.7.7 arm64，uv 0.7.8，项目既有 CPython 3.13.3；未安装依赖或更改锁文件。
以下 uv 命令 cwd=`/private/tmp/arch-be-001-qa-rework/backend`，均用项目运行时、offline/no-sync。

```bash
UV_CACHE_DIR=/private/tmp/arch-be-001-qa-rework/uv-cache PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/arch-be-001-qa-rework/backend uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python /private/tmp/arch-be-001-qa-rework/run_guarded.py pytest
UV_CACHE_DIR=/private/tmp/arch-be-001-qa-rework/uv-cache PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/arch-be-001-qa-rework/backend uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python /private/tmp/arch-be-001-qa-rework/run_guarded.py legacy
UV_CACHE_DIR=/private/tmp/arch-be-001-qa-rework/uv-cache uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -m compileall -q core app settings.py tests
```

| 检查 | 结果 |
| --- | --- |
| run_guarded.py pytest模式；精确四文件：test_role_api_authorization.py、test_module_registry.py、test_delivery_runtime.py、test_role_api_permission_startup.py | exit 0；51 passed, 4 warnings in 1.07s；51项均no_db。 |
| run_guarded.py legacy模式；上表独立十例 | exit 0；9 REJECTED + 1注释对照APP_COMPOSED，contract_failures=0。 |
| 上述compileall | exit 0。 |
| 根目录 `python3 /private/tmp/arch-be-001-qa-rework/audit_static.py` | exit 0；165公开文件相同、8链接/anchor、3示例说明块一致、2README前缀保留、CODE_INDEX仅2行新增、bundle元数据/四份索引链接有效、63脏文件未变。 |
| 根目录 `git diff --check`；git status/diff、HEAD、权限/业务约束rg与源码读取 | exit 0；未发现本轮新增failure。 |
| 最终Python SHA256写入审计与首轮正文比较；再运行 `git diff --check` | exit 0；63个已有公开脏文件中仅本checklist变化，零新增仓库文件；165文件仍与快照一致；首轮失败正文逐字保留。 |

4 warnings均为未注册no_db标记的PytestUnknownMarkWarning；标记实际存在，fixture据此跳过DB。
QA首个runner尝试exit1：仓库写保护阻止pytest_asyncio首次import向既有venv写pycache，测试未运行；
仅调整临时runner并启用PYTHONDONTWRITEBYTECODE后重跑成功，未改项目。两次定向rg曾猜错dict文件名
exit2；先用rg --files确认真实路径为app/system/api/routes.py后重跑exit0，非实现failure。

## Acceptance audit、资源与 handoff

- 当前可交Human Owner验收的基线：本r1公开源码、隔离配置、no-DB / stub行为与文档检查为qa_passed。
  Human Owner尚未最终接受；QA不授予owner_accepted、发布、部署或外部动作权限。
- 本轮无待Development返工failure。首轮F-001/F-002已关闭，其历史qa_failed保持下文快照。
- 排除/独立gate：真实backend env人工迁移、真实登录/数据库/Projection写入、schema/bootstrap、
  Docker、PLC/CA、长运行、打包制品、部署、Git refs/推送。现有真实env若仍有旧key，预期启动失败；
  本轮证据不证明本机真实env已经迁移或可运行。
- 本轮只创建 `/private/tmp/arch-be-001-qa-rework/`：公开源码/.env快照、manifest.json、dirty-before.json、
  checklist-before.md、run_guarded.py、audit_static.py、pytest.log、legacy.log、uv-cache、pytest临时目录、
  pycache与日志。没有branch/worktree、服务进程、监听端口或设备连接。
- DEV与首轮QA目录仍保留；本轮QA不回收任何资源。本文已持久记录输入、结果、摘要和限制，
  临时日志不是唯一证据；Owner验收后协调者核对依赖再处理。
- QA -> Human Owner（经主协调者relay）：ARCH-BE-001 r1独立qa_passed；final acceptance pending。
  协调者可据此机械同步本任务索引，QA未修改索引/spec/tasks/实现/测试/配置。

# 首轮 QA 失败历史（原文保留，非当前 verdict）

首轮 verifier为backend_permissions_qa，Status为qa_failed，handoff为F-001/F-002返回Development；
该次失败快照由后续返工与本轮新fresh-context复验处理。以下保留首轮正文和证据。

# Verdict 与 blocker

**qa_failed**。公开隔离夹具复现活动旧配置检测被来源优先级覆盖：内部 bool 标记可由进程环境或
Settings 初始化参数设为 false，从而在旧 key 仍存在时成功组合应用，违反 R4 / AC-001。
另有新增 README 对 Projection Service 独立角色限制的描述与当前实现不符，违反按实际实现
说明权限边界的要求。不得将 44 项既有聚焦回归通过解释为本 Revision 验收通过。

无阻止本轮验证的环境 blocker；实现与文档 failure 为当前交付 blocker。Verification 未修实现、
测试、spec、tasks、配置或索引；失败通过主协调者返回 Development。最终验收仅由 Human Owner 决定。

# 基线、输入与独立性

- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD
  `ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec`，被验证实现为未提交工作树。
- 完整读取根 AGENTS、根 README/PLAN pair、backend README/PLAN pair、canonical lifecycle workflow、
  `.codex/agents/verification.toml`、本任务 spec/tasks；核对 backend/app README、实现、diff、
  四个聚焦测试文件、conftest、DEV runner 与 `pytest-final.log`。根之外未发现更近 AGENTS.md。
- 使用 `project-governance`、`backend-arch` 及其 AUTH_SECURITY/MODULE_REGISTRATION reference；
  新文件头及真实索引按 `code-document-indexer` 核验。未触及维护脚本、打包实现或用户接口错误合同。
- 独立建立 `/private/tmp/arch-be-001-qa/backend`。从当前工作树复制 171 个公开源码/测试/config/
  项目清单/example 文件；其 `.env` 仅复制公开 `.env.example`。复制前后逐字节一致，测试后再次
  确认全部 171 文件与当前工作树一致；不是验证陈旧 DEV 副本。
- 公开文件清单排序后按 `relative_path + space + SHA256` 拼接的聚合 SHA256：
  `1bde6d8d30c3a3fca133b5812a55fc82cb1a58d1da5ba832dc73e7d31d64556b`。
  被验证 `settings.py` SHA256：
  `ee6010014b94b1d815eb2a96fb1bd020e82774eb00386cb9f268b6b136f62548`。
- 隔离 runner 先依据 Settings AST 清除进程中的项目配置字段及旧 key，再加载公开夹具；
  `builtins.open` / `io.open` 拒绝三个真实 backend env 的 resolved path；audit hook 拒绝
  `socket.connect`、`socket.bind`、`socket.getaddrinfo`。没有真实 env 读取、DB 写入、监听端口或设备操作。

# Failure evidence

## F-001：旧配置存在性可被可输入 bool 覆盖（验收 blocker）

位置：`backend/settings.py:192` 将 `legacy_role_api_permissions_present` 声明为普通可输入 Field；
`:199-209` 将各来源检测结果放入同一个字段并保留普通优先级。`backend/core/registrar.py:153`
仅消费最终 bool；更高优先级的 false 因而可压过较低来源检测到的 true。
`exclude=True` / `repr=False` 只影响输出，不禁止输入该字段。

本轮公开夹具包含三份示例相同的新数组 `[]`，并追加活动 `ROLE_API_PERMISSIONS_JSON={}`；
通过真实 Settings 来源合并后将 configuration 注入 registrar，再实际调用 `create_app(testing=True)`。

| 场景 | 预期 | 实际标记 | 实际组合 |
| --- | --- | --- | --- |
| dotenv 旧 key，无额外标记 | 拒绝 | true | ValueError，正确拒绝 |
| dotenv 旧 key，进程 `legacy_role_api_permissions_present=false` | 拒绝 | false | APP_COMPOSED |
| dotenv 旧 key，Settings 初始化同名 `False` | 拒绝 | false | APP_COMPOSED |
| 进程旧 key，Settings 初始化同名 `False` | 拒绝 | false | APP_COMPOSED |

命令退出码 **1**；`contract_failures=3, cases=4`。未启动服务或调用维护动作。
这不是正常 grants 的优先级争议：R4 明确要求 dotenv / 进程任一来源存在活动旧 key 即拒绝，
而检测事实现在能够被另一输入字段覆盖。Development 应在 r1 allowlist 内修复存在性聚合，
并覆盖交叉来源/显式初始化负例，保留两项新数组原有覆盖规则。QA 不指定额外权限框架或改真实 env。

本轮复现核心（在上述 open/socket guard 与公开配置清理后执行）：

```python
from pathlib import Path
from settings import Settings
from core import registrar
import os

qa = Path.cwd()
fixture = qa / 'qa-legacy-public.env'
fixture.write_text((qa / '.env.example').read_text() + '\nROLE_API_PERMISSIONS_JSON={}\n')

def compose(configuration):
    registrar.settings = configuration
    try:
        registrar.create_app(testing=True)
        return 'APP_COMPOSED'
    except ValueError:
        return 'REJECTED'

assert compose(Settings(_env_file=fixture)) == 'REJECTED'
os.environ['legacy_role_api_permissions_present'] = 'false'
assert compose(Settings(_env_file=fixture)) == 'APP_COMPOSED'  # failure evidence
os.environ.pop('legacy_role_api_permissions_present')
assert compose(Settings(_env_file=fixture, legacy_role_api_permissions_present=False)) == 'APP_COMPOSED'
os.environ['ROLE_API_PERMISSIONS_JSON'] = '{}'
assert compose(Settings(_env_file=qa / '.env.example', legacy_role_api_permissions_present=False)) == 'APP_COMPOSED'
```

## F-002：README 宣称当前不存在的 Projection Service 角色限制

新增英文 README 称 `Projection management role restrictions`、`Service role restrictions still apply`；
中文 pair 同样声称 Projection 管理角色限制及 Service 角色限制仍有效。
当前 `backend/app/system/api/projection_mapping.py:200` 的管理入口依赖仅为
`require_permissions('projection-mapping-manage')`，随后仅传 `actor_user_id=current_user.id`。
`backend/app/system/services/async_projection_mapping.py:113` 起的 Service 方法接收 actor_user_id，
没有 actor role 参数；全文检索未发现 role/admin/supervisor 校验。现有业务参数/状态校验不能被
描述为独立角色限制。该 key 由 enabled system manifest 声明，配置给非 admin 时 permission guard 可通过。

这是静态证据形成的文档 failure；本轮没有执行 Projection 写库，也不宣称完成其真实业务路径测试。
Development 应按真实边界澄清双语 README，并向协调者说明 spec 中相同前提；若要新增角色限制，
属于当前排除的权限粒度/Service 改动，应回 PM，而不能借文档返工静默引入。

# 验收标准核对

| 标准 | 结果 | 独立证据与限制 |
| --- | --- | --- |
| AC-001 输入合同 | **failed** | 严格数组、空/缺省、旧 key 常规存在性负例通过；F-001 证明来源交叉时仍可绕过拒绝。 |
| AC-002 原始等级 | passed | 合法 subset、重复精确 key；operator 独有有效/未知/disabled key 在告警和过滤前失败，无自动补权。 |
| AC-003 过滤及告警 | passed | 所有 manifest owner 合并；显式 system/CA key；共享 key 任一 enabled owner；unknown/disabled WARNING、有效集合过滤、resolver不恢复忽略项、请求不重复告警。 |
| AC-004 请求/模块边界 | passed for tested scope | ASGI stub 身份下 admin/supervisor 放行、operator/未知角色403、未初始化 fail closed、仅登录 probe；disabled demo 路由/OpenAPI缺席且各角色404，model metadata保持。user与CA独立规则回归通过。未做真实登录、DB业务或设备测试；Projection文档问题见F-002。 |
| AC-005 启动/维护边界 | partial / failed guarantee | testing/生产组合、run开发入口及main两维护stub顺序回归通过；F-001仍破坏活动旧key必须阻断API组合的共同前提。未调用真实维护。 |
| AC-006 示例与文档 | **failed** | 三example安全空数组/英文注释一致，8个相对链接及anchors有效，等值迁移与bootstrap独立性齐备；F-002权限边界说明不准确，F-001亦使无条件旧key拒绝承诺不成立。 |
| AC-007 交付治理 | passed for audit scope | exact r1、角色文件归属、allowlist与共享diff核对；本轮唯一仓库写入为checklist。DEV写前README/CODE_INDEX副本对比保留先前内容。最终Owner验收pending。 |

# 命令、环境与结果

环境：macOS 15.7.7 arm64；`uv 0.7.8`；项目既有 CPython 3.13.3。未安装依赖或改锁。
下面 uv 命令均 cwd=`/private/tmp/arch-be-001-qa/backend`，使用项目既有环境、`--offline --no-sync`。

| 检查 | 实际命令 / 输入 | 退出码与结果 |
| --- | --- | --- |
| 独立聚焦回归 | `UV_CACHE_DIR=/private/tmp/arch-be-001-qa/uv-cache PYTHONPATH=/private/tmp/arch-be-001-qa/backend uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -`；stdin设置上述guards后调用`pytest.main(['-q','tests/test_role_api_authorization.py','tests/test_module_registry.py','tests/test_delivery_runtime.py','tests/test_role_api_permission_startup.py'])` | 0；44 passed, 4 warnings in 0.95s；验证实际导入QA路径的settings.py。 |
| F-001独立负例 | 同一`uv ... python -`命令；stdin设置上述guards、公开dotenv与四场景，比较每项实际结果与REJECTED预期 | **1**；3/4违反合同，具体结果已完整落入上表。 |
| 静态编译 | `UV_CACHE_DIR=/private/tmp/arch-be-001-qa/uv-cache uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -m compileall -q core app settings.py tests` | 0。 |
| 文档/example/保留审计 | 仓库根`python3 -`；逐个解析README Markdown本地链接及目标标题slug；解析三example活动赋值/JSON及相邻说明块；与DEV写前副本比较 | 0；8 links/anchors，3 safe arrays，说明块一致；两个README原内容为完整前缀；CODE_INDEX仅本任务两行新增。 |
| 实现及范围审计 | `git status --short`、`git diff --stat`、`git diff -- <本任务allowlist>`、源码读取及`rg -n`权限/业务限制；`git rev-parse HEAD` | 0；确认目标工作树与真实接口说明；F-002为静态发现。 |
| 差异格式 | 仓库根`git diff --check` | 0。 |
| 源码新鲜度/写入边界 | Python SHA256逐文件比较QA拷贝与仓库；对进入QA时`git ls-files --modified --others --exclude-standard -z`所得公开文件做前后摘要比较 | 0；171源码相同；写checklist前已有工作树文件零变化、零新增。 |

4个 warnings 是未注册 `pytest.mark.no_db` 的 PytestUnknownMarkWarning；conftest仍根据该标记跳过
自动建/清表，所有本轮测试有标记且网络guard生效。本轮未扩到可能建/清数据库的全量测试。
QA辅助检查曾因正则跨过说明块而误比较整个example尾部，exit1；修正为逐行定位说明块后exit0，
不是实现失败。环境版本查询首次忘记临时UV_CACHE_DIR而exit2（默认cache权限），按表中临时cache重跑exit0。
首个测试shell的Homebrew login初始化有`/bin/ps: Operation not permitted`提示；pytest仍exit0，后续使用login=false。

# Acceptance audit、资源与 handoff

- 当前基线：聚焦源码/no-DB行为有上述通过证据，但整个r1为qa_failed，不能标记完成或owner_accepted。
- 尚未接受：F-001旧key来源存在性、F-002Projection权限边界文档；返工后需要新的fresh-context QA。
- 排除/独立gate：真实backend env迁移、真实登录/数据库/Projection写入、schema/bootstrap、Docker、
  PLC/CA、长运行、打包制品、部署、Git refs/推送。公开夹具通过不证明这些环境或动作可用。
- 本轮资源：`/private/tmp/arch-be-001-qa/`，包括当前公开源码快照、公开`.env`、
  `qa-legacy-public.env`复现夹具、uv-cache、pytest cache/pycache和日志。没有新branch/worktree、服务或端口。
  DEV `/private/tmp/arch-be-001-dev/`仍保留。QA不回收资源；返工/复验完成且Human Owner接受后由协调者核对依赖再处理。
- 本checklist保存失败输入、结果、源码位置、摘要、命令与限制，临时目录不是唯一持久证据。
  QA目录为此次被验证失败实现快照；Development返工后不能直接据此宣称验证新实现，须重建或逐文件更新并核对。
- QA -> Development：F-001/F-002及上述证据；按现r1边界返工并更新tasks，不能静默改spec或扩大实现allowlist。
- QA -> Human Owner（经主协调者relay）：独立verdict为qa_failed；Human Owner final acceptance **pending**。
