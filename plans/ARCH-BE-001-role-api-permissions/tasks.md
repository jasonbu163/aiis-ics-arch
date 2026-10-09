Task ID: ARCH-BE-001
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: ARCH-BE-001 r3 六env分组格式恢复与静态DEV自检完成；交主协调者启动新fresh-context Verification

Workflow Mode: STD
Execution Mode: agent_team_same_session

# r3 当前 Development 记录

依据：已读取r3 owner_approved spec与当前完整tasks/checklist历史；Human Owner已确认具体
格式方案，PM如实命名r3。复用已读project-governance/项目workflow。r1/r2完整Development
记录在下方原文保留，先前QA通过不代表r3 verdict。当前实现面仅六env和本tasks。

## 实际变更与全内容保留

- 六文件：`backend/.env`、`.env.docker.dev`、`.env.docker.prod`、`.env.example`、
  `.env.docker.dev.example`、`.env.docker.prod.example`。
- 按三份公开HEAD原边界恢复英文标题：Syntax、App、Runtime、Auth、Logging、Database Routing、
  MySQL、PostgreSQL、SQLite、MSSQL、Bootstrap；每组上下使用原80个等号分隔行。
  Syntax原标题保留，仅包分隔线；其余标题插在该组首key的既有用途注释之前，无重复章节。
- 全部六文件先在单进程内存预检生成，再写入。写前后独立比较68条完整活动赋值行，完全相同；
  去除新增标题/分隔行并忽略空行后原非空行序列逐字相同，包含全部逐key用途注释、语法和场景
  说明。因此未删改/重排原内容；原配置全文仅内存存在，不写备份、不输出秘密或秘密digest。
- 三真实权限保持supervisor `["monitor","system","control-agent-read"]`、operator `["monitor"]`；
  三example仍`[]`/`[]`。真实文件仍Git ignored。README pair写前后在内存逐字节相同。

## DEV静态检查

cwd仓库根，使用项目既有uv环境，offline/no-sync；辅助标准库文本脚本不导入Settings/应用。

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 格式恢复与内存保留比较 | `UV_CACHE_DIR=/private/tmp/arch-be-001-r3-dev/uv-cache uv run --offline --no-sync --project backend python /private/tmp/arch-be-001-r3-dev/restore_groups.py` | exit0；6×11 ordered groups、6×68赋值行不变、normalized非空行序列相同；README pair unchanged、真实env ignored |
| 当前标题/边界复核 | 同uv前缀运行 `/private/tmp/arch-be-001-r3-dev/check_groups.py` | exit0；三example HEAD原英文标题一致；六env各11标题/22分隔、实际首key边界、68key和权限正确 |
| 注释/既有合同保留 | 同uv前缀运行 `/private/tmp/arch-be-001-r2-dev/check_current.py` | exit0；6×68key英文用途说明逐字符合r2映射、权限/ignored正确；README各68key/10链接有效；159Python源码测试和依赖清单与r1 QA快照相同 |
| 格式差异 | `git diff --check` | exit0 |

本轮没有检查失败或扩大范围。未重复行为测试，不进行服务、DB、Docker或维护操作。
真实修改前证据来自DEV同进程受控内存比较，QA可独立重算当前结果及公开标题，但不宣称
独立生成过去时间点的真实env前值。

## 精确 r3 handoff 与资源

- 工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD
  `ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec`，未提交diff，无branch/worktree/commit创建。
- 当前仅写六env及tasks，共7文件；README/源码/测试/依赖/其他共享改动未触碰，spec/checklist/
  索引由对应owner负责。不改进程环境，不重启，不声称真实运行权限已生效。
- 资源 `/private/tmp/arch-be-001-r3-dev/`：`restore_groups.py`、只读`check_groups.py`、uv-cache，
  均不含真实赋值/完整env副本/秘密摘要。恢复脚本为一次性写入工具，当前勿重跑；QA可使用只读
  checker或自行独立核对。r2静态工具及r1历史资源继续保留，未回收他人证据。
- 下一gate：主协调者启动新的fresh-context Verification更新r3 checklist，完整保留r1/r2历史；
  DEV自检不替代独立QA或Human Owner最终验收。

# r2及r1完整 Development 历史记录（原文保留）

Task ID: ARCH-BE-001
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: ARCH-BE-001 r2 配置/注释/逐项文档实施和 DEV 静态自检完成；交主协调者启动新 fresh-context Verification

Workflow Mode: STD
Execution Mode: agent_team_same_session

# r2 当前 Development 记录

依据：Human Owner 精确批准 r2，spec 已 owner_approved；完整读取 r2 spec、当前tasks、
checklist（含r1失败/返工/qa_passed历史）及相关配置消费者。使用 project-governance、backend-arch。
此前读过的根/最近作用域 AGENTS、README/PLAN和workflow继续适用；r2不改源码/结构，不加载
脚本实现/打包/容器/UI专项。全部r1 Development原文在下方保留，r1 verdict不继承为r2通过。

## 实施文件与授权差异

- 三真实 `backend/.env`、`.env.docker.dev`、`.env.docker.prod`：删除活动旧key及旧完整授权历史
  注释；活动新数组统一为 supervisor `["monitor","system","control-agent-read"]`，operator
  `["monitor"]`。admin无新增配置，operator原始subset成立。
- 真实文件原有效授权与spec相符：host/prod supervisor三项、operator空；dev两角色空。
  因此host/prod operator新增monitor；dev supervisor新增三项且operator新增monitor。
  这是已获用户选择的授权增量，不称等值改名。
- 三公开 `.env.example`、`.env.docker.dev.example`、`.env.docker.prod.example`：只变英文注释，
  所有68个活动赋值原文本不变；两权限数组仍`[]`，无本机值进入公开默认。
- 六env每个key前均有相同短英文用途说明；语法提示说明字符串可单/双引号，JSON数组外层单
  引号/内部双引号，bool使用True/False。场景注释保留host published ports、dev Compose DNS、
  prod external DB与bound文件inode/restart差异。原非权限赋值顺序和文字保留，不格式化值。
- `backend/README.md` / `README.zh-CN.md`：完整保留r1权限/迁移说明，追加七配置组显式68key
  表（包含18bootstrap逐项），区分类型/用途、源码缺省、公开模板值；补入口、来源覆盖、root
  维护、测试库隔离、Projection唯一writer/default-off、TZ进程时区和显式bootstrap/reset行为。
  原Projection状态/合同校验事实勘误保留，不新增Service guard。
- 本`tasks.md`当前元数据为r2；不写spec/checklist/索引。共9个本轮文件，3个真实env仍ignored。

## 受控值保留证据

`edit_and_check.py` 一进程内读取六文件，词法解析引号/注释，在写前内存保存原活动赋值文本；
先预检六文件存在、key无重复、真实旧有效授权符合spec，全部生成内容比较合格后才首次写入。
写后重新读入同进程比较，三真实非权限赋值的集合、顺序、去词法注释后原赋值文本完全相同；
三example全部赋值同样相同。输出只含文件名、key数、相等结果和目标3/1，不输出任何非权限值。
后续仅收掉EOF多余空行，未改变任何活动赋值。原配置仅存在本地内存，进程结束后未保存备份、
全文或秘密逐key digest。QA可独立重算当前结果，历史前值以本DEV受控比较为依据。

## DEV 静态自检

工具：项目uv既有CPython环境，`--offline --no-sync`，不安装依赖、不导入Settings/应用。
辅助编辑器是标准库文本工具，源码静态AST只读Settings定义，不执行模块。

| 检查 | 命令/方法 | 结果 |
| --- | --- | --- |
| 迁移与写前后保留 | `python3 /private/tmp/arch-be-001-r2-dev/edit_and_check.py` | 六env写前预检和写后比较成功，各68key；三真实非权限不变，三example全赋值不变；随后公开README生成阶段AST算术默认值异常，整条exit1，未影响已完成env比较，未输出秘密 |
| README生成 | `python3 /private/tmp/arch-be-001-r2-dev/write_readme.py`；仅公开example/Settings AST | exit0；两语言显式68key表追加完成；随后校正RESET_PASSWORD模板列为False |
| 当前静态复核 | `UV_CACHE_DIR=/private/tmp/arch-be-001-r2-dev/uv-cache uv run --offline --no-sync --project backend python /private/tmp/arch-be-001-r2-dev/check_current.py`，cwd仓库根 | exit0；6×68key英文注释、目标3/1与example[]/[]、三真实ignored、两README各68key、10 links/anchors、代码块平衡、引号内#正确识别 |
| 源码/依赖未变 | 上述check_current对r1 QA rework快照逐文件只读比较 | 159 Python源码/测试及pyproject/uv.lock逐字节相同 |
| monitor只读表面 | `rg -n '@.*\.(get\|post\|put\|patch\|delete)\|APIRouter' backend/app/monitor/api`，并读routes聚合 | 只有两个GET `/monitor/collector/status`与`/monitor/realtime/latest`，聚合共有monitor guard；无模块/源码改动 |
| 格式差异 | `git diff --check` | exit0 |

静态checker初版覆盖regex漏API_V1_PREFIX中的数字、EOF多余空行，首次检查exit1/diff exit2；
修正checker字符类并删除多余EOF空行后通过。文档生成器对LOG_MAX_BYTES的AST算术表达式改为
公开源码表达式展示，无应用导入；RESET_PASSWORD误归为secret模板列已更正。均为本轮工具/文档
自检修正，没有扩大范围。

## 精确 r2 handoff、资源与限制

- 工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD
  `ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec`，未提交diff；无branch/worktree/commit创建。
- 资源 `/private/tmp/arch-be-001-r2-dev/`：仅公开映射/工具脚本`edit_and_check.py`、
  `write_readme.py`、`check_current.py`和uv-cache；无真实env备份、完整旧授权或秘密摘要。
  编辑脚本有一次性旧状态预检，不能用其重放当前迁移；QA用只读checker或独立工具复核。
- 前轮 `/private/tmp/arch-be-001-dev/`、`arch-be-001-qa/`、`arch-be-001-qa-rework/`继续保留，
  不含本轮真实env副本。159源码比较用r1新QA快照，r2不重跑行为测试。
- 只改配置文件/注释/README/tasks，不改进程环境、不重启、不开端口、不运行Docker/DB/bootstrap、
  不登录或现场操作。当前文件通过不等于运行服务已加载；进程若有旧key仍失败，新数组覆盖仍遵循
  既有来源规则。操作者需要审查入口/进程覆盖并自行重启。
- 下一gate：主协调者启动新的fresh-context Verification更新r2 checklist并保留r1历史，
  本DEV自检不授予QA verdict或Human Owner最终验收。

# r1 完整 Development 历史记录（原文保留）

Task ID: ARCH-BE-001
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: ARCH-BE-001 r1 F-001/F-002 返工与 DEV self-check 完成；交主协调者启动新 fresh-context Verification

Workflow Mode: STD
Execution Mode: agent_team_same_session

# 实施依据与基线

Human Owner 已批准 spec r1（owner_approved）。Development 为命名 backend_permissions_dev。
已读根 AGENTS、README/PLAN pair、backend README/PLAN pair、完整当前 bundle 及 canonical workflow。
采用 backend-arch（含 AUTH_SECURITY/MODULE_REGISTRATION）、project-governance、code-document-indexer。
backend/plans 下无更近 AGENTS；当前 bundle 仅 spec，未提前创建 checklist。
共享工作树原已存在前端、治理、README、CODE_INDEX 等改动；backend README pair 和 CODE_INDEX
写前副本保存在 /private/tmp/arch-be-001-dev，保留原内容。本任务开始时后端源码与候选测试无 diff。

# 顺序与验证

1. R1/R2/R4：Settings 来源存在性、纯策略、app state 组合和依赖消费；验证隔离 no_db 测试。
2. R3/R4：三份公开 env 与 README pair；验证等值迁移、权限表面和双语链接。
3. AC-001..007：静态编译、聚焦 no_db 测试、diff 审计；完成精确 developer_handoff。

# 边界

不读取或修改真实 backend/.env、.env.docker.dev、.env.docker.prod；不连接/写数据库、运行 Docker、
启动端口、执行维护动作、改变模块 manifest 或前端。不写 spec/checklist/任务索引。

# 实际变更

- `backend/settings.py`：两数组默认 `[]`；包装既有 env/dotenv source 的返回，记录旧 key 存在性
  （包括空值与 dotenv 无值声明），保留原优先级。Settings 不发现模块、不反向依赖 app。
- `backend/core/role_permissions.py`（新增）：无 FastAPI/DB 依赖的严格 JSON 字符串数组解析、
  原始 subset、所有 manifest owner 汇总、显式 user/CA 权限、WARNING 字段回调与只读有效集合。
- `backend/core/registrar.py`：每次组合建立策略并保存 app.state；testing 模式同样校验，组合
  不成功则没有可服务 app。无全局授权缓存；失败的新组合不会覆盖已有 app 的授权。
- `backend/core/deps.py`：删除旧每请求 JSON 解析；resolver/guard 读取当前 Request 所属 app 的
  同一有效策略。无策略/未知角色 fail closed；保留 admin permission bypass 与原响应合同。
- `backend/tests/test_role_api_authorization.py`：原始 subset、严格输入、共享 owner、忽略 key、
  显式权限、admin/非admin guard、未初始化拒绝，以及 user/CA 独立业务规则回归。
- `backend/tests/test_role_api_permission_startup.py`（新增）：dotenv/process 来源、新旧共存、
  注释/缺省/覆盖、testing/生产组合失败、WARNING 不重复、多 app 策略隔离、ASGI 请求 guard、
  disabled demo 路由/OpenAPI 404、仅登录 probe、开发入口与 main 两维护入口的 stub 顺序。
- 三份 `backend/.env*.example`：删除旧活动赋值，新数组空默认和一致英文说明。
- `backend/README.md` / `README.zh-CN.md`：用途、格式、key 表面/读写边界、原始 subset、admin、
  模块开关、错误/告警、401/403/404、来源/重启、人工等值迁移与 bootstrap 独立性。
  写前已有的宿主机启动教程段落逐字保留。
- `CODE_INDEX.md`：只增加新纯模块和新测试两行，保留已有前端索引 diff。
- 本 `tasks.md`；未改候选 test_module_registry.py/test_delivery_runtime.py，仍运行其既有回归。

# DEV self-check

环境：macOS arm64，项目既有 uv 环境，CPython 3.13.3，未安装依赖/修改锁文件。
在 `/private/tmp/arch-be-001-dev/backend` 运行复制后的源码；该目录 `.env` 仅复制公开 `.env.example`。
复制 app/core/common/database/projection/scripts/tests、config/plc_snapshot_policy.yaml、settings/main/run/
build/pyproject/uv.lock 和公开 example；未复制、打开真实 env。测试均 `no_db`，不触发 conftest
建/清表 fixture。额外 runner guard 拒绝 socket connect/create_connection 和三个真实 env 的 open。

| 检查 | 实际命令/方法 | 结果 |
| --- | --- | --- |
| 最终聚焦回归 | `UV_CACHE_DIR=/private/tmp/arch-be-001-dev/uv-cache PYTHONPATH=/private/tmp/arch-be-001-dev/backend uv run --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python /private/tmp/arch-be-001-dev/run_no_db.py`，cwd 为隔离 backend | exit 0；44 passed, 4 warnings in 0.92s |
| 静态编译 | `UV_CACHE_DIR=/private/tmp/arch-be-001-dev/uv-cache uv run --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -m compileall -q core app settings.py tests`，同 cwd | exit 0 |
| 文档与示例 | Python 正则遍历两README相对链接，存在性/目标标题anchor核对；三example新数组 JSON 为 `[]`，无活动旧key，完整permission说明块逐字一致 | exit 0；8 local links/anchors valid；3 blocks identical and safe |
| 差异审计 | `git diff --check` | exit 0 |
| 共享变更保留 | backend README pair 与 CODE_INDEX 对写前副本逐行差异核对 | 本任务仅追加权限专节及两行索引；其他既有内容保留 |

runner 内精确 pytest 参数：

```text
-q tests/test_role_api_authorization.py tests/test_module_registry.py
   tests/test_delivery_runtime.py tests/test_role_api_permission_startup.py
```

必要测试修正/环境记录：首次工具启动以尚不存在隔离 cwd 运行，被工具拒绝，未执行命令；
默认 uv cache 不可访问导致 exit 2，改用本任务 `/private/tmp` cache 后恢复，不提权。
首次收集缺少复制的公开 `config/plc_snapshot_policy.yaml`，pytest exit 2；补复制公开 config 后
43 tests 通过。之后补充独立业务约束测试、整理 import、修正示例旧注释，最终 guard runner 44通过。
4 warnings 均为仓库既有未注册 `pytest.mark.no_db` 警告（含新文件同一标记）；未扩范围改 pyproject。

# 精确 Developer handoff

- Revision：ARCH-BE-001 r1，spec 仍为 owner_approved；本记录仅 DEV self-check，无 QA verdict。
- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD
  `ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec`；实施为未提交 working-tree diff，无新 branch/worktree/commit。
- 本任务文件为上述13个（含tasks）；allowlist外未写。spec/checklist/任务索引由相应owner负责。
- fresh QA 输入：批准spec、本tasks、当前实现及diff；可复用上述隔离命令或自行建立公开隔离环境。
  源码变更后应重新复制变更文件，不从仓库真实 env 导入 Settings。QA应独立审查命令与代码。
- 资源：`/private/tmp/arch-be-001-dev/`（写前README/CODE_INDEX副本、隔离源码/公开.env/config、
  `run_no_db.py`、`pytest.log`、`pytest-final.log`、uv-cache、logs、pycache）。当前保留给fresh QA；
  唯一持久证据摘要为本tasks，不依赖临时日志永久存在。无服务进程/端口/新分支/worktree。
- 限制与风险：真实env未读取/迁移/测试；本机若仍有旧key，启动失败是预期。未知/disabled会被
  过滤而导致非admin请求403。公开源码/noDB测试不代表真实数据库、登录、PLC/CA、部署或Owner验收。
  未运行全量DB测试，不执行在线迁移/bootstrap、Docker、真实服务；维护只用stub。
- 下一gate：主协调者显式启动 `agent_type=verification, fork_turns=none`，独立创建 checklist.md。


# 返工记录：QA F-001 / F-002（同 r1）

2026-10-09 已完整读 QA checklist 及 PM 同 r1 事实勘误。前轮44通过是有限 DEV自检，不能覆盖
QA公开复现的三种来源绕过；保留前轮记录及checklist失败历史，未修改QA文档。

- F-001根因：旧key存在性被放入普通来源优先级字段，较高优先级的false会覆盖dotenv的true。
  `settings.py` 改用独立派生来源 `legacy_presence`，根据已加载 env/dotenv source 的key inventory
  取 OR，并在普通输入之前提供这个唯一派生字段。显式初始化、同名进程变量或dotenv赋值均不能
  关闭真实存在性；没有额外读取dotenv。两项权限数组仍保持init > process > dotenv原优先级。
- 新增正式回归：dotenv/process旧key × process/init/both标记false六组负例，均实际调用
  create_app(testing=True)验证拒绝；另有新数组init/process/dotenv优先级回归。均no_db。
- F-002勘误依据：管理路由使用projection-mapping-manage permission guard，Service接收
  actor_user_id记录操作者并执行状态/合同校验，没有额外role/admin门槛。同步双语README表格、
  admin说明及actor字段说明。未新增Service guard、未修改路由或Service。
- 本轮修改仅settings.py、test_role_api_permission_startup.py、backend README pair和tasks。
  原有模块业务实现、真实env及其他任务diff保持。

返工后命令（cwd `/private/tmp/arch-be-001-dev/backend`，更新复制settings与startup测试后运行）：

```bash
UV_CACHE_DIR=/private/tmp/arch-be-001-dev/uv-cache PYTHONPATH=/private/tmp/arch-be-001-dev/backend uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python /private/tmp/arch-be-001-dev/run_no_db.py
UV_CACHE_DIR=/private/tmp/arch-be-001-dev/uv-cache uv run --offline --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -m compileall -q core app settings.py tests
```

- 聚焦回归exit0：**51 passed, 4 warnings in 1.07s**，网络/真实env open guard继续启用。
- compileall exit0；README 8 links/anchors与写前内容前缀保留检查exit0；git diff --check exit0。
- 新证据资源 `/private/tmp/arch-be-001-dev/pytest-rework.log`；原dev/qa目录保留供fresh复验。
  QA目录仍是前轮失败实现，不作为新实现证据；当前dev目录已更新两改动源码/测试。
- working tree/HEAD与13文件集合不变，无新提交。限制、真实env人工迁移、无数据库/设备/部署动作
  及Owner最终验收pending边界与前handoff相同。
- 本轮为DEV返工自检；新fresh-context Verification由主协调者启动，独立决定QA结果。
