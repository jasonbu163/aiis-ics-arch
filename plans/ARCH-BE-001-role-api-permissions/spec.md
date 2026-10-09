Task ID: ARCH-BE-001
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已确认展示的六 env 分组格式方案，PM 记录为 r3 owner_approved；交命名 Development 按本窄范围恢复标题并更新 tasks.md

Task Namespace: aiis-ics-arch
Classification: root
Capability: 后端 supervisor/operator 独立接口权限配置、等级校验和模块状态诊断
Owner: backend Core 鉴权与应用组合根
Acceptance Chain Reference: ARCH-BE-001 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Related Task: ARCH-FE-002；仅参考前端角色等级规则，不继承其范围批准或验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-09
Updated: 2026-10-09

# r3 当前批准范围：恢复六份 env 的英文分组标题

Human Owner 在主会话已对具体展示的格式方案回复“是的。确认”：六份后端 env 恢复原有分组
大标题、`===` 分隔线与必要空行；标题英文，保留现有逐 key 英文注释和全部赋值，中文说明查
后端中文 README。PM 将这个已批准的具体方案记录为 r3；不声称用户曾说出 Revision 名称 r3。
r3 不改变权限、配置含义或运行行为。r2 已独立 `qa_passed`，最终验收仍 pending；r1/r2 全部
范围、批准、Development 与 QA 历史保留，不自动成为 r3 verdict。

## R3-FORMAT-001：标题来源、位置与保留要求

1. 以 `git HEAD` 的三份公开 `backend/.env*.example` 原有章节为依据，只去掉标题中文部分，
   恢复相应英文标题与原样式 `# ================================================================================`。
   当前三份公开基线均含：Syntax、App、Runtime、Auth、Logging、Database Routing、MySQL、
   PostgreSQL、SQLite、MSSQL、Bootstrap；按原顺序放在对应现有配置组或语法说明之前。
2. 六文件同源配置组的英文标题、分隔线样式保持一致；确有原组差异时保留，不为了统一强增
   分组或移动现有内容。已存在的正确标题不重复插入，不新增按角色或业务模块拆分的章节。
3. 只插入上述英文标题/分隔线及必要空行。现有逐条英文用途注释、语法提示、场景说明、全部
   活动赋值、配置顺序和其他非空行必须逐字保持；不清理、改写、删除或重排原内容。
   三真实 env 保持 r2 已配置的 supervisor 三项/operator monitor；三 example 权限仍为 `[]`。
   保留中文值，不新增中文标题/注释，不修改 README 或再次改变任何权限。

## r3 精确 allowlist 与角色边界

- Development 的文件写入面仅 `backend/.env`、`backend/.env.docker.dev`、
  `backend/.env.docker.prod`、`backend/.env.example`、`backend/.env.docker.dev.example`、
  `backend/.env.docker.prod.example`，且仅执行 R3-FORMAT-001 的插入。
- Development 更新本任务 `tasks.md` 的当前 r3 元数据并完整保留 r1/r2 记录；交接后的新
  fresh-context Verification 更新 `checklist.md` 当前 r3 元数据并完整保留 r1/r2 QA 历史。
- PM 只写 spec；主协调者只机械同步根 PLAN pair 和 plans README pair 的本任务索引。
  README、源码、测试、依赖、索引结构、进程环境及其他文件均不属于本轮实现写入面。

真实三 env 继续 Git ignored。只有限读取注释及在内存比较原内容；不输出真实赋值、不保存
整份 env/秘密摘要或备份。英文标题来自公开 Git 基线，不从私有备注推导公开内容。静态辅助
工具放 `/private/tmp`，不导入 Settings/应用，不装依赖、不启动服务或端口，不执行 DB、Docker、
bootstrap、设备、发布或 Git refs/推送。使用 `project-governance` 核对角色/历史，技术实现不变。

## r3 验收与批准记录

| 标准 | 验证方式与边界 |
| --- | --- |
| AC-r3-001 分组恢复 | 六文件对应章节按公开 HEAD 原标题顺序恢复为英文；分隔线与组间空行清楚，不重复/新增业务分组，不移动原内容 |
| AC-r3-002 全内容保留 | DEV 同进程内存比较：去除本轮新增标题/分隔线与空行后，原非空行序列逐字相同；全部赋值及逐 key 注释独立比较相同，三真实3/1与三example[]不变；不输出值/保存备份 |
| AC-r3-003 限定变更 | 三真实env仍ignored；公开diff仅允许的插入，README/源码/测试/依赖及其他共享改动不变；格式检查通过，不声称服务重启或运行权限已验证 |
| AC-r3-004 独立交付 | DEV与新的fresh-context QA各自记录精确r3、命令/结果、前值来源限制与资源；r1/r2历史完整，r3 QA独立记录，Human Owner最终验收pending |

只运行静态文本/章节顺序、注释与赋值比较、`git diff --check`、`git check-ignore`；不重复行为
测试。QA 独立核对当前内容与公开 HEAD 标题，真实修改前原文保留证据明确来自 DEV 的受控
内存比较，不伪称 QA 独立生成过去状态。误插位置或误改内容只修正本轮差异，不回滚其他任务。

- 2026-10-09：Human Owner 对已具体展示的六 env 分组恢复方案回复“是的。确认”；PM 如实
  记录该范围批准并命名 r3，`Status: owner_approved`，不追加尚未讨论的功能或要求重复批准。
- Human Owner scope approval for this recorded ARCH-BE-001 r3 scope: **approved**；最终验收pending。
- 下一 gate：命名 Development 实施并交接新的 fresh-context Verification；通过后交 Human Owner
  最终验收。此前 r2 qa_passed 不自动授权 r3 通过或 owner_accepted。

# r2 历史批准范围：英文 env 注释、逐项配置说明与三环境权限迁移

本节是当前 r2 范围；下方 r1 完整范围、批准与事实勘误保留为历史，不扩大本轮 allowlist。
r1 经 Development 返工及新的 fresh-context Verification 达到 `qa_passed`，51 项 no-DB 回归与
10 项独立旧配置来源场景通过，Human Owner 最终验收仍 pending；这些证据不自动成为 r2 verdict。

Human Owner 本轮要求 env 注释只保留英文，由 `README.zh-CN.md` 提供中文配置解释，并将当前
保留权限填入三份真实后端 env。随后已明确选择：**三环境统一，operator 增加 monitor 查询权限**。
本精确 r2 已获 Human Owner 范围批准，交命名 Development 实施；PM 仅记录 spec 的范围与真实批准。

## R2-ENV-001：三个真实配置使用相同授权

以下三文件迁移为同一组活动配置，成员及顺序固定：

- `backend/.env`
- `backend/.env.docker.dev`
- `backend/.env.docker.prod`

```dotenv
SUPERVISOR_API_PERMISSIONS_JSON='["monitor","system","control-agent-read"]'
OPERATOR_API_PERMISSIONS_JSON='["monitor"]'
```

1. 删除活动旧 `ROLE_API_PERMISSIONS_JSON` 赋值及其完整旧授权历史注释，写入上述两数组；
   不保留第二个活动来源，不把旧未知 key 搬到新数组，不因已知权限目录再添加其他授权。
   普通英文迁移提示可保留，用户完整旧 JSON 不复制到 README、任务证据或临时备份。
2. 当前宿主机/prod 旧授权经过当前后端目录过滤后，supervisor 有效项为
   monitor/system/control-agent-read，operator 有效项为空；Docker dev 原授权为空。
   因此这次不是单纯等值改名：host/prod operator 新增 monitor；dev supervisor 新增三项、
   operator 新增 monitor，均来自用户本轮明确选择。admin 固定权限不增加配置。
3. 轻量源码核对确认 monitor 聚合的当前两接口仅为 GET `/monitor/collector/status` 与
   GET `/monitor/realtime/latest`，共同受 `monitor` guard 保护。授予 operator 的是这些事实
   查询；不新增写接口、前端页面或设备权限。`system` 仍含用户管理读写及既有 actor 限制，
   `control-agent-read` 只授予当前 action-scope 查询；不把它们笼统描述成全部只读权限。
4. 本轮只调整文件，不修改进程环境、不重启服务、不执行 Docker/数据库/bootstrap。若运行
   进程仍有活动旧 key 或其他权限覆盖，继续按 r1 合同失败或覆盖；不得声称仅改文件已证明
   真实服务生效。README 说明操作者需要审核运行入口及进程覆盖并自行重启。

## R2-DOC-001：六份 env 的英文注释

1. 三份真实 env 和三份 `.example` 的自然语言注释、章节标题、语法提示统一英文；同 key 使用
   相同的短用途说明，场景寻址、空卷初始化等确实不同的说明允许按文件保留准确差异。
   既有双语标题中的中文移走，由中文 README 解释。只要求注释英文，不要求修改中文配置值。
2. 每个活动 key 附近有对应英文用途说明；解释 JSON 数组使用外层单引号、内部双引号的有效
   dotenv 写法，不能沿用“所有字符串必须双引号”的误导性总规则。保留 True/False 示例。
3. 三个公开 example 两项权限仍为 `[]`，其余所有活动 key/value 保持不变；不得把本机授权、
   用户名/口令、地址、token、数据库名或其他私有配置复制为公开默认。
4. 三个真实 env 只有旧/新权限 key 允许活动赋值变化；其他赋值，包括数据库、JWT、bootstrap、
   App/日志/运行参数，逐 key 和去除词法注释后的原赋值文本保持相等。不重排或格式化非权限赋值；对注释进行
   词法安全编辑，不能把引号内的 `#` 当注释，不能把注释清理变成配置值修改或文件删除。

## R2-DOC-002：后端 README 逐配置解释

完整性以当前三份公开 example 的活动 key 并集为边界：**68 个 key，三文件集合相同**。
不扩展到所有 Settings 内部派生字段，不另建配置手册或新增 env 配置。两份后端 README
提供对应英文/中文解释，按以下章节组织表格，每个 key 必须能直接或通过明确的 prefix/suffix
展开规则追溯到一条解释；bootstrap 可用三角色 × 六字段说明，但不能只写泛泛的一段“账号设置”。

| 配置组 | 本轮说明范围 |
| --- | --- |
| App/API | APP_NAME、APP_VERSION、APP_DESCRIPTION、API_V1_PREFIX、BACKEND_HOST/PORT/WORKERS |
| Runtime/Projection | DEBUG、TESTING、BACKEND_MOCK_ENABLED、PROJECTION_RUNNER_ENABLED/INTERVAL_SECONDS/BATCH_SIZE、TZ |
| Auth/permissions | JWT_SECRET_KEY、JWT_ALGORITHM、ACCESS_TOKEN_EXPIRE_MINUTES、REFRESH_TOKEN_EXPIRE_DAYS、两项角色权限数组 |
| Logging | LOG_DIR、LOG_LEVEL、LOG_MAX_BYTES、LOG_BACKUP_COUNT |
| Database routing | PRIMARY_DATABASE、DATABASE_TYPE 兼容关系、MYSQL/POSTGRES/SQLITE/MSSQL_ENABLED |
| Database connections | MySQL 7 项、PostgreSQL 5 项、SQLite 1 项、MSSQL 7 项，均按公开模板的完整 key 明列 |
| Bootstrap | ADMIN/SUPERVISOR/OPERATOR × ENABLED/USERNAME/PASSWORD/NAME/ROLE/RESET_PASSWORD，共18项 |

解释包括用途、类型/单位或允许值、源码缺省与公开模板值的区别、适用入口及关键副作用边界；
已有 Role API permissions 专节可复用并链接，不复制一套矛盾策略。数据库路由/root维护用途、
Projection 单 writer 与默认关闭、TESTING 测试数据库隔离、TZ 仅为进程时区而非 DB 时区迁移、
bootstrap 仅显式维护生效及 reset-password 行为，应依据当前消费者说明。不为解释新增功能。
使用公开安全示例；可把三项/一项授权写成通用当前模块配置示例，不声称其为模板默认或公开
用户完整历史权限。r1 的权限粒度、模块开关、告警与 Projection Service 事实勘误继续准确保留。

## r2 精确 allowlist 与安全读取

Development 获批后只编辑：

- `backend/.env`、`backend/.env.docker.dev`、`backend/.env.docker.prod`：权限赋值及注释，按以上限制。
- `backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example`：
  仅注释，所有活动值不变，两项权限维持 `[]`。
- `backend/README.md`、`backend/README.zh-CN.md`：逐 key 配置表、语言/配置/迁移说明及相关链接。
- 本任务 `tasks.md` 由 Development 更新当前 r2 元数据并完整保留 r1 记录；新 fresh-context
  Verification 更新 `checklist.md` 当前 r2 元数据并保留 r1 失败/返工/通过历史。
- PM 只修改 spec；主协调者只机械同步根 PLAN pair 与 plans README pair 的本任务行。

真实 env 继续 Git ignored，绝不提交。授权有限读取权限和注释；验证非权限赋值时仅在本地内存
解析/比较原文，不输出内容、不把整个 env 复制到临时目录或备份、不保存秘密的逐 key digest。
对外证据只记录文件、key 数量、允许的权限数组和相等/不相等结果；不得运行能展开整个配置的
`cat .env`、env dump、`docker compose config` 等命令。若某真实文件缺失、含冲突权限重复赋值
或迁移前状态与本节明显不符，记录脱敏 blocker，不用 example 覆盖或擅自合并其余配置。

技术 handoff：Development/Verification 使用 `project-governance` 和 `backend-arch` 核对配置
消费者与权限边界；本轮不改 env 分层/来源、Compose、应用入口或数据库，不加载其实现专项。
临时静态检查工具位于 `/private/tmp`，不安装依赖，不导入会加载真实 Settings 的应用模块。

## r2 验收标准与验证方式

| 标准 | 验收证据 |
| --- | --- |
| AC-r2-001 目标授权 | 三真实env各只有一组新key，无活动旧key，数组与固定3/1成员及顺序相等；原始subset成立；monitor当前路由只有两GET的源码证据；角色授权增量如实记录 |
| AC-r2-002 值保留与语言 | 六env全部自然语言注释英文，每key有用途说明；真实三文件非权限赋值原文/集合不变，三example全部赋值不变、两数组[]；中文值不误改，无完整旧授权历史遗留 |
| AC-r2-003 说明完整准确 | 两README逐项覆盖公开模板并集68key，分组展开可追溯；类型/单位/默认或模板值区别、入口/风险准确，原权限事实勘误与bootstrap独立性保留，双语语义一致、本地链接/anchor有效 |
| AC-r2-004 安全边界 | 三真实文件仍ignored，无全env/秘密进入公开diff或临时证据；源码/测试/依赖/其他配置及共享改动未变；静态编辑不冒称服务重启、DB/设备/登录或Owner最终验收 |
| AC-r2-005 独立交付 | DEV与新fresh-context QA独立记录精确r2、命令/退出码、前后比较和限制；r1全部历史保留且不自动继承verdict；r2通过后交Human Owner最终验收 |

验证采用只读文本/JSON检查：修改前在内存建立活动赋值基线，修改后按上表比对；注释英文与
key附近说明检查；68key与两README覆盖集合比较；权限JSON解析/静态subset和公开manifest目录
核对；双语链接/anchor、代码块与 `git diff --check`、`git check-ignore`。QA 独立重算当前结果，
前值依据明确标注为DEV受控内存比较证据，不伪称QA独立生成了过去时间点的原env。
本轮不新增镜像实现的测试，不重复 r1 全套行为测试，不启动服务/端口、导入真实配置的应用、
连接数据库或执行迁移/bootstrap；发现需要源码修复则停止该部分并回PM修订。

## r2 风险、回退与批准记录

- dev 空授权变为3/1，host/prod operator 新增monitor，均是已选的授权变化；填写文件只在下一次
  启动读取时生效，不能证明其他运行入口/进程覆盖相同。未来monitor新增写接口须重新审查该key。
- 注释编辑误碰秘密/值以受控内存前后比较拦截，不保存完整真实配置副本；发现失败只修正本轮
  越界差异。任何真实服务/配置回退需独立授权，不能回滚其他任务改动。
- 2026-10-09：r1独立复验qa_passed、最终验收pending；Human Owner提出本轮注释/说明/真实env
  请求并明确选择统一三环境、operator增加monitor，形成r2 draft。此请求不是对尚未提交的精确
  r2实施范围的批准；随后 Human Owner 对精确提交的 ARCH-BE-001 r2 回复“批准”。
- 2026-10-09：Human Owner scope approval for ARCH-BE-001 r2: **approved**；范围不变，最终验收pending。
- 下一gate：Development实施并交接新的fresh-context Verification；本轮范围最终
  验收仍由Human Owner记录。不得修改源码或新增业务guard来迎合文档。

# r1 历史范围与批准记录（保留，不作为 r2 新增写入授权）

# 目标与当前依据

将后端单一 `ROLE_API_PERMISSIONS_JSON` 对象拆为 supervisor/operator 两项独立配置，明确
`operator ⊆ supervisor`、admin 固定权限，以及普通模块关闭后的接口与残留授权行为。同步后端
双语 README 和三份公开 env 示例，使操作者能理解配置、迁移、启动错误与非阻断告警。

本 r1 已获 Human Owner 精确范围批准，待命名 Development 实施。PM 仅记录本 spec 的范围与
真实批准；Development/Verification 各自创建归属文件并记录实施、自检与独立验证结果。

2026-10-09 只读基线：

- `backend/settings.py` 默认旧对象为 `{}`；`core/deps.py` 每请求解析，解析失败返回空授权，
  `require_permissions()` 固定允许 admin 通过权限依赖。user Service 的 actor/目标用户约束独立存在。
- `app/module_registry.py` 的 `ModuleManifest.enabled` 已控制普通 Router 注册；关闭模块的
  model package 仍可为 metadata 导入。`app/router.py` 显式装配 user/auth 和 control_agent。
- `core/registrar.py:create_app()` 是 API 组合入口；`main.py` 先创建 app，再解析维护参数，
  因而 `main.py --maintenance ...` 目前也先完成 API 组合。`run.py` 使用 `main:app` 并启用 reload。
- ARCH-FE-002 当前为 r4、独立 `qa_passed`，Human Owner final acceptance pending；其前端
  pageId 规则与后端 API permission 是两个合同。共享工作树已有其他任务改动，必须保留。

# 范围与需求

## R1：两项配置与等级校验

| 配置 | 格式 / 缺省 | 含义 |
| --- | --- | --- |
| `SUPERVISOR_API_PERMISSIONS_JSON` | JSON 字符串数组，缺省 `[]` | supervisor 获得的配置型接口 permission |
| `OPERATOR_API_PERMISSIONS_JSON` | JSON 字符串数组，缺省 `[]` | operator 获得的配置型接口 permission，必须是 supervisor 子集 |

1. 复用现有 Settings 的 env 来源和环境变量覆盖规则，不新增配置文件、加载优先级或动态刷新。
   permission 是后端稳定 key，精确、区分大小写匹配，不是前端 pageId、URL 或任意模块名。
2. JSON 语法错误、顶层非数组、非字符串成员或空/纯空白成员必须在 API 组合期失败，指出变量
   与成员位置/问题，不输出整份 env 或秘密。缺失变量等价于 `[]`；显式空字符串不是合法 JSON。
   重复有效 key 可按集合去重，不为重复项增加未讨论的启动阻断。`*` 不表示全部权限，按未知
   key 告警并忽略；两个数组均不能配置或改变 admin 的固定权限。
3. 对解析成功的**原始成员集合**先严格检查 `operator ⊆ supervisor`。存在 operator 独有 key
   就阻止 API 组合/正常启动，指出 operator 变量、独有 key 和 supervisor 缺少它。即使该 key
   属于未知或 disabled 模块，也先失败；不得先过滤再放行，不自动给 supervisor 补权限。
4. 仅 supervisor/operator 使用新数组；未知角色仍 fail closed。空数组不授予配置型接口权限，
   不改变只要求登录的接口、认证流程、admin-only guard 或独立业务约束。

## R2：权限目录、模块关闭与非阻断告警

1. 普通权限目录复用当前全部合法 manifest 的 `permissions` 和 `enabled`，不再维护第二份普通
   模块名单。显式装配的安全边界也须纳入：user 的 `system`；control_agent 的
   `control-agent-read`、`control-agent`。不能因它们没有普通 manifest 而误判未知授权。
2. 未声明 key 输出 `WARNING`、原因 `unknown_permission`，并从有效授权中排除；只由关闭
   普通模块声明的 key 输出 `WARNING`、原因 `disabled_module`，并排除。两类告警均允许后端
   正常启动，包含变量名、permission 和适用模块名，不把整份配置或私有地址放进日志。
3. permission 是全局稳定 key；多个普通模块声明同一 key 时，任一启用 owner 即允许该 key
   参与授权；全部 owner 关闭才按 disabled 处理，日志列清 owner。显式边界声明视为可用 owner。
   不新增全局唯一 key 强制规则，不由发现顺序覆盖结果，不在本任务重构 Registry。
4. 一次应用组合完成解析、原始子集校验、目录过滤和有效授权建立；诊断只在该次组合记录，
   不在每个请求重新解析、发现模块或重复告警。reload/重启后的新应用重新校验。实际
   `get_role_permissions()` / `require_permissions()` 必须消费过滤后的同一授权结果；未建立
   有效策略时非 admin fail closed，不得另读原始数组恢复被忽略的 key。
5. 保留已有 `enabled=False` 语义：该普通 manifest 的整组路由不挂载，也不在 OpenAPI 中出现，
   三角色请求关闭模块的专属路径均为正常未注册路径 404；admin 不能调用不存在的接口。
   重启/整个进程 reload 才重组，不能宣称热卸载。关闭不删表、不删数据、不阻止 model metadata
   导入，也不改变 Alembic。user/auth、control_agent 保持显式装配，不增普通模块开关。

## R3：admin 与现有接口语义

admin 无需 env 授权，继续通过 `require_permissions()`。登录有效性、参数、数据状态、用户管理
actor 规则、Projection 状态/合同校验与 CA 门禁/token 约束继续生效；不能把 admin 绕过 permission
依赖写成绕过所有业务/安全校验。授予某 key 只通过相应 permission guard，不自动授予另一 key。

README 必须依据实际路由和 Service 逐项说明当前 key，不自动细分现有读写权限：

| permission | 当前表面与说明边界 |
| --- | --- |
| `system` | 显式 user 管理接口，包括读写；actor/目标用户限制仍独立执行，不等同 system 模块总权限 |
| `system-dict` | system 字典查询与维护共用该 key；不能描述为只读 |
| `projection-mapping` | Projection handler/policy catalog 与 mapping 查询 |
| `projection-mapping-manage` | mapping 草稿、校验、发布、复制与回滚的 permission guard；Service 保留状态/合同校验，目前没有额外 role/admin 门槛 |
| `monitor` | collector 与 raw/latest 现场事实接口；不包含客户业务曲线或前端 monitor 页面授权 |
| `control-agent-read` | CA action-scope 目录查询 |
| `control-agent` | gate-token 签发 permission guard；不会远程执行设备动作，仍有独立角色限制 |
| `aiis_demo` | 默认关闭示例 manifest 的 key；作为 disabled 告警示例，不启用 demo |

`schema_maintenance` 没有配置型 permission，使用 admin-only guard；CA authorization verify 使用
其门禁 token 合同。README 说明这些独立边界，不能用两个数组代替它们。

Projection mapping 管理路由将当前用户的 `actor_user_id` 传入 Service 记录操作者；此字段不构成
角色校验。Development 必须在双语 README 如实说明现状，不为匹配旧描述新增 Service guard。

## R4：旧配置退役与操作文档

1. 活动 `ROLE_API_PERMISSIONS_JSON` 在当前 Settings 有效输入中存在时，即使值为 `{}` 或空值，
   也报迁移错误并阻止 API 组合；指出退役变量和两项新变量。不隐式兼容、不选择新旧优先级。
   注释行不属于活动配置。检测覆盖 dotenv 与进程环境来源，不为检测回显或另存真实 env。
2. 三份公开示例删除活动旧变量，使用相同新 key、`[]` 安全默认和一致英文用途注释。新增双语
   README 专节说明各变量用途、格式、缺省、当前 permission 含义/读写边界、子集、admin、模块
   enabled、401/403/404 区别、错误/告警、重启、来源与旧对象迁移步骤。
3. 前后对比例必须保持成员等值，例如旧
   `{"supervisor":["monitor","control-agent-read"],"operator":["monitor"]}` 分为
   supervisor `["monitor","control-agent-read"]` 与 operator `["monitor"]`；解释合法等值迁移
   的授权不变，但错误从请求时空授权/403变为启动失败，unknown/disabled 改为告警并过滤。
4. bootstrap 仍是显式账号维护动作，独立于 API 授权数组；配置授权不会创建账号，关闭授权也
   不会删除账号或修改密码。保留已有宿主机初始化教程链接，不恢复启动隐式 bootstrap。
5. 本 r1 默认**排除真实** `backend/.env`、`.env.docker.dev`、`.env.docker.prod` 的读取、迁移和
   修改。README 提供人工等值迁移步骤；开发/QA 使用公开临时夹具。旧本机配置未迁移时预期
   启动失败，公开夹具通过不能宣称本机现有 env 已可运行。若要由 Agent 迁移真实配置，必须由
   Human Owner 明确授权并修订精确 allowlist；无需用户提供密码或数据库信息。

# Development allowlist 与实施约束

Human Owner 已批准 r1，Development 可修改以下实现面；不要求每个候选文件都改：

- `backend/settings.py`、`backend/core/deps.py`、`backend/core/registrar.py`；如需解耦纯解析与
  策略过滤，可新增唯一薄模块 `backend/core/role_permissions.py`，不引入泛化权限框架。
- `backend/tests/test_role_api_authorization.py`、`backend/tests/test_module_registry.py`、
  `backend/tests/test_delivery_runtime.py`；可新增
  `backend/tests/test_role_api_permission_startup.py` 记录有意义的应用组合/输入来源回归。
- `backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example`；
  `backend/README.md`、`backend/README.zh-CN.md`；根 `CODE_INDEX.md` 仅同步新增源码/测试的真实索引。
- 本任务 `tasks.md` 只由 Development 在精确批准后创建；`checklist.md` 只由
  developer_handoff 后 fresh-context Verification 创建。PM 只写本 spec，主协调者只机械维护
  根 `PLAN.md` / `PLAN.zh-CN.md`、`plans/README.md` / `plans/README.zh-CN.md` 的本任务索引。

技术 handoff：Development 与 Verification 必须使用 `backend-arch`，读取其
`references/AUTH_SECURITY.md`、`references/MODULE_REGISTRATION.md`；新增文件/索引使用
`code-document-indexer`，任务文档使用 `project-governance`。若触及维护脚本、应用打包入口或
用户可见接口错误合同，先回 PM 修订范围并指定 `backend-script-tooling`、`backend-packaging`
或 `i18n-workflow` 的适用面；本 r1 只新增启动诊断，不改变接口错误文案/响应合同。

组合顺序约束：Settings 保持输入层，不导入 app/router 或发现业务模块；纯解析/子集与目录过滤
不依赖 FastAPI/DB。组合根先建立有效策略，再返回可服务 app。`core/deps` 不反向导入
registrar/router 触发循环；manifest import 不进行连接、写库或外部操作。实现位置由 Development
在现有分层内确定，不为本任务改变 Router/Registry/Projection 架构。

维护边界：保留当前入口顺序，`uv run python main.py --maintenance schema` 与
`... --maintenance bootstrap-users` 同样先组合 app，因而也受本次校验。阻断错误发生在维护
动作调用前，unknown/disabled 告警不阻止维护入口继续；是否实际执行 schema/bootstrap 仍需
独立外部动作授权。本任务用 stub 验证调用先后，不执行维护写库，不改 main/run/维护脚本。
不得将此结果扩大为所有直接脚本或 Alembic CLI 都运行相同 API 校验。

# 验收标准

| 标准 | 必须证明的行为 |
| --- | --- |
| AC-001 输入合同 | 缺失/合法空数组/正常数组通过；坏 JSON、非数组、非字符串和空成员明确失败；旧活动 key 在 dotenv/进程来源都失败，注释不失败，新旧共存不隐式覆盖；无敏感值输出 |
| AC-002 原始等级 | 合法 subset 通过；operator 独有有效、未知和 disabled key 均在过滤前阻断，错误可定位，supervisor 不被自动补权 |
| AC-003 过滤及告警 | unknown/全部 owner disabled key 告警但 app 组合成功；有效目录覆盖显式 system/CA key；共享 key 的任一启用 owner 语义确定；被忽略 key 不经 resolver 恢复，不重复每请求告警 |
| AC-004 请求/模块边界 | admin 可通过现有 permission guard；两非 admin 角色按有效集合放行/403，未知角色及未初始化策略 fail closed；仅登录路由仍按原合同；disabled 普通模块所有专属 route/OpenAPI 缺席、三角色均404，metadata保持；业务约束不被绕过 |
| AC-005 启动/维护边界 | create_app 测试模式也验证；开发/生产两入口使用同一组合校验，公开输入负例拒绝就绪；main维护路径在stub动作前失败或仅告警后继续；无需真实DB/端口/设备即可验证，无循环import |
| AC-006 示例与文档 | 三example仅新key、安全默认、一致英文说明；backend README pair覆盖R3全部key及R4操作、迁移前后差异、告警/启动和bootstrap独立性；双语一致、本地链接有效，真实env未被改动 |
| AC-007 交付治理 | 修改仅在allowlist，保留其他任务diff；DEV和fresh-context QA分别记录精确r1、命令/退出码、限制及资源；源码/fixture通过不冒称真实env、数据库、设备、部署或Owner验收 |

验证用 `uv`、现有依赖/锁与公开临时配置，no-DB 测试必须标记 `no_db` 并 stub 数据库/业务边界。
特别注意当前 autouse fixture 会为未标记测试建/清表，禁止为本任务运行有真实写库副作用的测试。
建议最小命令：

```bash
cd backend
uv run pytest -q tests/test_role_api_authorization.py tests/test_module_registry.py tests/test_delivery_runtime.py tests/test_role_api_permission_startup.py
uv run python -m compileall -q core app settings.py tests
```

新 startup 测试文件若未创建则从命令删除；公开夹具应隔离真实 dotenv 并保持原来源/覆盖规则，
必要 subprocess 检查只组合/stub入口，不实际监听服务。另检查本任务双语链接、example schema
和 `git diff --check`。记录未运行原因与已有范围外失败，不顺手修旧测试或扩到全量DB测试。

# 排除、风险与回退

- 不改前端、现有模块路由/Service/manifest、权限粒度、用户模型、token合同、数据库结构、
  Registry发现算法、Projection运行、Compose/Dockerfile、依赖锁、应用打包或维护脚本。
- 不读取/改写真实env，不登录真实账号，不数据库迁移/写入，不 Docker up/down/build，
  不PLC/现场CA动作，不Git refs/推送、发布或部署。
- 旧配置迁移是兼容性变化，未迁移会阻断启动；须先审核等值新配置。unknown/disabled过滤
  可能使非admin请求403，告警要可定位，不能通过自动扩权解决。有效策略在重启前不动态更新。
- 回退只能恢复本任务源码与对应旧配置组合，保留其他任务改动；不自动回退真实服务或配置。
  fresh-context QA通过后仍由Human Owner最终验收，发布/现场动作继续另行授权。

# 修订、批准与下一 gate

- 2026-10-09：按用户“回到STD”“正常落spec”请求建立 r1 draft；仅形成范围草案。
- 2026-10-09：Human Owner 对上一条提交的 ARCH-BE-001 r1 回复“批准”；记录为
  `owner_approved`，仅批准本精确范围，不增加真实env迁移或外部动作授权。
- 2026-10-09：PM 核实 QA 发现的 R3 事实错误：Projection mapping 管理路由使用 permission
  guard，Service 接收 `actor_user_id`，执行状态/合同校验，没有额外 role/admin 校验。原表格
  “Service 的角色限制仍有效”已勘误，要求 Development 同步更正双语 README。此为同 r1
  的现状描述更正；范围、AC、allowlist、实际行为及风险边界不变，不授权新增 guard 或修改 Service。
- Human Owner scope approval for ARCH-BE-001 r1: **approved**；最终验收仍 pending。
- 真实env迁移默认排除。该范围如需增加，先修订并批准。
- 下一 gate：Development 创建 tasks.md 并实施；developer_handoff 后主协调者启动新的
  `agent_type="verification", fork_turns="none"`，独立记录 checklist.md；最终由Human Owner接受。
