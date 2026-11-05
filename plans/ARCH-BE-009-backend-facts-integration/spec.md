Task ID: ARCH-BE-009
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已于2026-11-04精确批准ARCH-BE-009 r1的A源码/no-DB阶段；PM -> Development按STD实施已批A；数据库、Docker、实际数据迁移/B和DAA改动未批准，待源码检查通过后另行确认
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 匿名 PLC 事实批量接收、逐点 latest、安全历史读取、有限保留及固定 provider 合同
Owner: Backend plc_facts 事实模块
Acceptance Chain Reference: 本 spec 第15节；PM -> Human Owner 精确范围批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Depends On: ARCH-AW-008 r1 共同语义；当前 Python Backend 模块 v1 合同及 f6a8c0e2b4d6 源码迁移基线；进入运行另受 G-B 约束
Related Task: ARCH-AW-008, ARCH-BE-010, DAA-007
Created: 2026-11-04

# 后端 PLC 事实服务与 provider 合同

## 1. 当前决定、真实状态与范围边界

本任务先把后端事实服务定成可审阅、可单独实施的 provider 规格。**本轮只有本 spec 草案；没有源码、测试、配置、迁移或运行实施。** 后端就绪后再由独立 DAA 软件任务消费固定合同，开展另批的阶段 C HTTP 联调；DAA 当前软件、已有 SQLite 配置、历史、样本身份、原文、SHA 及原阶段 B profile 完全不动。

Owner 最新同意按后端优先推进，原话为“好的，daa先不做是吧，回答我之后，其他没问题不需要我确认的话，就能继续开始”。它授权本轮具体规格整理及协调，不能成为对尚不存在的本 r1 的源码/数据库范围批准，亦不是 ARCH-AW-008 文档终验或 ARCH-BE-010 A0 最终验收。

当前证据分层：

| 表面 | 截至本次只读核对的事实 | 本任务承担的增量 |
| --- | --- | --- |
| [AW008 bundle](../ARCH-AW-008-stage-c-facts-contract/spec.md)、[独立 QA2](../ARCH-AW-008-stage-c-facts-contract/checklist.md) | r1 文档范围获批，AC01–AC20 文档 QA2 通过；Owner 文档终验 pending，软件另批。双语 [demand-r1](../../contracts/demands/automation-world-facts-integration.zh-CN.md) 仍为 proposed。 | 承接 B01–B08，选择具体字段、算法、表与参数；不改写旧批准、QA 或 demand 状态。 |
| [DAA v2](../../automation-world/data-acquisition-agent/src-tauri/src/domain/local_sample.rs)、[持久写入](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs) | 原 sample/manifest/context 有原文与 SHA；同 PLC 持久 sourceSeq，组跨 DB，同轮 manifest。原样本加 manifest 有 512 KiB 本地编码预算；uploadAvailable=false。 | 正式 wire 关联这些既存材料，不能把候选传输字段说成当前上传器已实现。 |
| [monitor Model](../../backend/app/monitor/models/monitor.py)、[认证 GET](../../backend/app/monitor/api/realtime.py) | 旧 raw/latest 与 PLC/DB/group latest 唯一键存在；旧 CA 直库及 Projection 标量输入仍是保留兼容链。 | 独立 app/plc_facts 与七张新表；不改旧表、不双写、不更换旧消费者输入。 |
| [BE010 r1 bundle](../ARCH-BE-010-anonymous-business-integration/spec.md)、[QA2](../ARCH-BE-010-anonymous-business-integration/checklist.md) | 八条业务匿名 POST 仅 A0 通过：220 测试、437 探针、88 请求；默认关闭/unready，无业务接线、迁移、持久业务 ACK 或 Owner 最终验收。 | 事实合同独立；BE010 r2 另管旧业务时间兼容、其四表 DDL 及八路接线，不是事实服务或 DAA 阶段 C 的前置。 |

2026-11-04 以 stdlib AST 只读解析六个 Alembic 源文件：单 head 为 f6a8c0e2b4d6，累计 64 个 create_table。该结果不是任何实际库的 revision。BE010 A0 另声明四张未迁移 Model；其完整 metadata68 不等于已迁移 schema68。未导入或运行项目来取得此判断。

本任务无 Parent Task ID，不继承 AW008、DAA 阶段 B、BE003/006 或 BE010 的实施、验收或运行授权。所有数字/算法是本 r1 的具体推荐，须随整个精确 r1 审阅；它们不是未经批准的现场性能承诺。

## 2. R01：阶段、模块 owner、合同与共用边界

| 阶段/gate | 可交付结果 | 进入条件及限制 |
| --- | --- | --- |
| 当前 PM | 本 spec 与主协调六处索引中的 draft 事实 | 不创建 tasks/checklist，不运行工程、测试、监听、任何 DB（含 SQLite）、Alembic current 或任何 Docker 命令。 |
| A 源码/no-DB | 本文有限 allowlist 内的 API/Domain/Service/CRUD/Model/显式迁移源码、固定机器合同、必要 no_db 测试及 DEV handoff | Human Owner 明确批准 ARCH-BE-009 r1 的 A；Development 才创建 tasks。使用项目现有 uv 环境、offline/frozen/no-sync、合成 process env 及连接/监听 guard；无依赖安装。迁移源码存在不等于执行迁移。 |
| G-B / B | 独立可丢弃 MySQL 8.4.6 的迁移、并发/故障/读取/清理证据及独立 QA | A 候选固定后，另批精确实例/账号/schema/端口/卷、命令、时间设置、故障及清理动作。当前没有目标身份和操作批准，不启动、不探库。 |
| provider-ready | A 与获批 B 均经 fresh-context Verification，Owner 接受明确后端范围，交付固定 B08 材料 | 只表示后端候选，不表示部署、DAA 软件、双方联调或阶段 C 验收。 |
| DAA 后续 | 上传器、UI/SQLite 投递元数据与受控联调 | 独立 DAA spec/批准；后端软件完成后再推进。现有 SQLite 及阶段 B 原件不得作为本 B 测试资源。 |

采用 `backend/app/plc_facts/` 普通 module owner，manifest 声明 `name=plc_facts`、`core_contract=aiis.backend-module/v1`、`requires=()`、`model_requires=()`、`exports=()`、`permissions=()`、`enabled=True`、`order=36`，只登记本任务三条 router 和本模块模型。模块存在不等于准入打开；enabled=False 在重组后仅移除本三路，不改变 monitor。API-only，无页面、设备 driver、Projection descriptor 或后台采集。

公共版本固定：`contractVersion=plc-facts/v1`、`sourceProfile=daa-local/v2`、`digestProfile=pf-json/v1`、游标 profile `pf-cursor/v1`。破坏字段/类型/身份/时间/确认语义用新主版本；新增可选字段须明确缺省、摘要与旧客户端行为，不能改已冻结请求。

未来 provider 产物精确放在 `contracts/published/http-api/plc-facts-v1/`：双语 `README.md` / `README.zh-CN.md`（方向、版本、实际 gate、限制及源链接），`openapi.json`（本三 operation 及其递归 components 闭包），`schema.json`（请求、回执、三读模式和错误的 JSON Schema 2020-12 `$defs`），`vectors.json`（独立输入/规范字节/摘要/拒绝向量）。JSON 是生成的机器合同/快照，不是手改运行配置；源真相仍为 typed Schema、模块实现和显式 Alembic。A 完成可记 implemented/source-only，B 独立通过后才记 verified 对应范围，不能只因目录名 published 写成已上线。当前不创建这些文件，不改变 demand-r1；实现产物反向引用 AW008 并列出第14节共同语义细化。

不修改或消费 `common.integration` 的业务 v1 信封/摘要/64 KiB parser。它们由 BE010 唯一维护；本模块不扩公共符号，不改 `module_contract.py`、全局 response/camelize、认证、engine、session 或 Registry。使用已公开的 Base、get_db_session/get_sync_db_context、BusinessException、log_event、ApiSchema/ModuleManifest；本地 `FactsRoute` 只处理本三路的 HTTP、严格 JSON、错误和输出，不向 Core 搬入事实/业务规则。

## 3. R02：精确后续 allowlist 与禁止面

**当前 PM 唯一仓库写入路径为本 spec。** 下表只定义精确批准后 A 的有界实现面；花括号仅展开列出的文件名。未列路径不可因“需要适配”自行扩大，实质变化返回 PM 新 Revision。

| 路径/有限集合 | owner 与允许变化 |
| --- | --- |
| `plans/ARCH-BE-009-backend-facts-integration/spec.md` | PM/Human Owner；范围、修订、真实批准。 |
| `plans/ARCH-BE-009-backend-facts-integration/tasks.md` | A 批准后 Development 创建；真实计划、自检、diff、运行 blocker 和 handoff。 |
| `plans/ARCH-BE-009-backend-facts-integration/checklist.md` | developer_handoff 后 fresh-context Verification 创建；独立 A/B verdict 与 Owner 验收。 |
| `backend/app/plc_facts/{__init__,manifest,config,error_codes,canonical,source,retention,cursors}.py` | 薄入口、模块本地设置、命名空间 StrEnum、纯摘要/原材料映射/月历/游标规则。 |
| `backend/app/plc_facts/api/{__init__,routes,batches,latest,history,http,dependencies}.py` | 三路薄 adapter、局部严格解析/原样键输出、完整依赖退出；无 SQL/DDL/设备动作。 |
| `backend/app/plc_facts/schemas/{__init__,source,batch_in,query,receipt_out,read_out}.py` | 原材料、typed 入参/查询/回执/投影/缺口和错误 schema。 |
| `backend/app/plc_facts/models/{__init__,state,receipts,facts}.py` | 仅第9节七张 Model，无旧表重定义。 |
| `backend/app/plc_facts/crud/{__init__,async_ingest,async_query,sync_maintenance}.py` | SQL/锁/查询；不 commit/rollback。 |
| `backend/app/plc_facts/services/{__init__,async_ingest,async_query,sync_maintenance}.py` | 真实执行通道与事务 owner；不导入 HTTP 或对方模块私有 Service。 |
| `backend/app/plc_facts/mocks/__init__.py`、`backend/app/plc_facts/seeds/__init__.py` | 仅 import-safe package；不提供 fallback/seed。 |
| `backend/app/plc_facts/README.md`、`backend/app/plc_facts/README.zh-CN.md` | 稳定边界/合同/运维入口；任务及 gate 由既有 backend PLAN 与根 bundle 统一拥有，无第二 Task ID 或执行事实。 |
| `backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py` | 唯一新 revision `0a2c4e6f8b10`，down_revision=`f6a8c0e2b4d6`；七张事实表，无其他表 DDL/DML。 |
| `backend/scripts/plc_facts_maintenance/{main.py,.env.example,README.md,README.zh-CN.md}` | 薄一次性维护 CLI、默认帮助、dry-run/adopt/cleanup；运行另批，不创建 daemon 或调度配置。 |
| `backend/tests/test_plc_facts_{contract,api,source,ordering,cursor,retention,migration,compatibility,maintenance}.py` | A 必要公开行为/故障替身/独立向量与静态迁移/兼容 profile；不用 SQLite。 |
| `backend/tests_mysql/test_plc_facts.py` | B 独立入口源码；默认拒绝未提供明确隔离目标/授权标识，禁止借 shared conftest 清库。 |
| `backend/tests/module_admission_fixtures.py` | 仅追加命名 BE009-A/BE009-B profile；冻结旧 fixtures、断言和失败历史不改。 |
| `backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example` | 仅追加第4节四个默认关闭/空值 key 的英文说明；旧完整原文前缀/值/grants 保持。 |
| `contracts/published/http-api/plc-facts-v1/{README.md,README.zh-CN.md,openapi.json,schema.json,vectors.json}` | 第2节有限 provider 产物，不发布到任何外部服务。 |
| `contracts/README.md`、`contracts/README.zh-CN.md`、`backend/README.md`、`backend/README.zh-CN.md`、`backend/app/README.md`、`backend/app/README.zh-CN.md`、`CODE_INDEX.md` | 仅新稳定能力入口与结构索引；与 BE010 写入相同文件时先后串行、按段合并，保留对方当前内容。 |
| `PLAN.md`、`PLAN.zh-CN.md`、`backend/PLAN.md`、`backend/PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` | 主协调唯一写入，仅本任务真实状态和存在文档链接；不由本 PM/Development/Verification代写。 |

排除：所有旧迁移、monitor/CA/Projection/业务表与 API 改造、BE010 bundle/源码、DAA/SMA/DS/FF/C#、所有 SQLite/profile/真实 env、依赖/锁/Compose/CI/打包、AGENTS/role/workflow/skill、通用 SQL/动态 handler/CRUD 平台、身份平台、事件总线、Celery/Redis/Beat/Python Worker、新 PLC 采集、事实到业务自动映射、Git refs/commit/push、发布/部署及任务外资源清理。

## 4. R03：三路匿名、默认关闭准入与预算

| 方法/路径 | 职责 |
| --- | --- |
| POST `/api/v1/integration/plc-facts/batches` | 同库原子接收有界多个 PLC/DB/固定片；原 POST 重试恢复事实或拒绝回执。 |
| GET `/api/v1/integration/plc-facts/latest` | 当前有效来源下逐点最新结果，按 PLC/DB 聚合；目录由返回的实际有效点定义派生。 |
| GET `/api/v1/integration/plc-facts/history` | mode=changes 安全增量；mode=range 原 observedAt 半开范围；无另一个管理/ACK/查询 SQL 平台。 |

三路固定匿名，无 JWT/API key/角色依赖，不按 UA/Origin/自称 DAA 动态绕过；既有受保护 GET/业务 POST/用户/维护/CA token 保持。producer/instance/plc/generation/配置和来源 hash 都是声明，可以被可达客户端冒用。以下 source 资格是数据准入与顺序政策，不是身份认证或设备所有权证明。POST才执行body媒体/JSON解析；两个GET无body，只做严格query校验，未知/重复/互斥query参数422，不要求GET携带Content-Type。

四个模块本地 BaseSettings key 固定：`PLC_FACTS_ENABLED=False`，`PLC_FACTS_PLC_IDS_JSON='[]'`（精确 PLC key 集合，最多256），`PLC_FACTS_STORAGE_PROFILE='unadopted'`，`PLC_FACTS_CURSOR_HMAC_KEY=''`（真实值至少32随机字节，以64小写hex配置；公开示例空，绝不提交真实值）。仅公共 resolve_env_file 选择运行 dotenv；process env 覆盖。所有运行设置更改重启生效，不追加用户登录。HMAC 只保护服务签发 token 的完整性，不是调用者凭据。

关闭或 PLC scope 空/越界返回403；合格请求仍需 storageProfile 精确为 `mysql84_shanghai_v1`、有效 key、已显式采用的七表/schema/adoption/binding，否则503 not_ready。A 的正常默认条件必须在 DB dependency 前拒绝；不能把填一个任意 profile 当作完成运行 gate。GET 必填精确 `plcId`，不允许匿名无限列出全部部署 PLC；POST 各 cycle 的 plcId 均须在数据范围。模块 disabled 重组后三路404。

| 有界项 | r1 固定值/拒绝 |
| --- | --- |
| HTTP body | 最多4 MiB原始 UTF-8；stream 读取超限即停并413；application/json，可选charset=utf-8；压缩/其他charset/媒体415。 |
| JSON | 外层及内层原文均拒绝重复键、非法UTF-8/孤立surrogate/非有限数、BOM；最大深度20，超限413；非对象/未知静态字段/snake别名/错误类型422。数字先 Decimal，不先float。 |
| 新批 | 最多16个cycle、32个sample-part、8个不同PLC；每轮最多4096个点、128个DB样本、每样本最多16片；超过数量413。实际body上限始终优先。 |
| 原材料 | 每份payloadUtf8≤512 KiB；manifestUtf8≤128 KiB；contextUtf8≤1 MiB（均指unescape后UTF-8字节）。超限413，不裁剪/重编码旧材料。 |
| 固定片 | 每片≤512点且规范points字节≤128 KiB；超限须冻结前分片；单点超过该上限413。原payload完整重复携带并按source SHA只存一份，不进行任意字节断包。 |
| 标识/文本 | 标识精确非空1–128 UTF-8字节，无控制字符/首尾空白；UUID不强制重造；pointId/name/sourcePath允许原Unicode，分别上限128/512/2048字节；comment≤4096字节。text原貌保留。 |
| 时间/请求 | 新 batchCreatedAt 不晚于DB现在5分钟，不早于现在24小时；已存在原批优先按稳定结果恢复。每个点/读起止/源savedAt不晚于DB现在5分钟，不以接收时间修正；异常422。 |
| 事务/请求并发 | 本模块每个API进程最多4个在途数据操作，超出429/Retry-After:1；不解析一份无限等待队列。全局写锁等待≤2s，单事务目标≤2s，HTTP总预算10s；无界重试禁止。 |
| 存储准入 | adopt默认逻辑原值预算1 GiB（raw/context/规范投影/latest的精确UTF-8字节总和）和最小proof最多1,000,000行；只可显式降低到1 MiB..1 GiB、100..1,000,000行，不随请求修改，B可用低配额真实触发边界。控制行维护计数，同锁校验/更新。容量不足503 capacity_exceeded，优先恢复已有回执，不删未到期材料腾位。拒绝proof也无容量时返回none本次新事实边界/retirementAllowed=false，不假称已终结记录。此逻辑配额不证明InnoDB页/日志/备份物理空间充足，部署另留余量。 |
| 读/响应 | limit默认100、最大500；每页响应≤2 MiB，扫描最多2000个已发布part位置；达到扫描/字节预算可空页hasMore=true并明确scanBudgetReached。GET单次预算5s。 |

这些上限根据现有 v2 编码预算和有界事务选择，A/B须验证边界；不承诺现场吞吐。进程内4并发不是跨多worker的全局速率平台；跨进程数据安全由数据库门闩提供。413拒绝仍保留源本地材料，不能截短JSON、移除失败点或把一个坏批永久堵住别的PLC。

## 5. R04：原样本、manifest、点类型与固定片的完整输入

### 5.1 wire结构与唯一点位体

外层只接收下列字段，均为camelCase：

| 字段 | 必填/规则 |
| --- | --- |
| contractVersion/sourceProfile/digestProfile | 必填，固定第2节版本。 |
| instanceId/batchId/batchCreatedAt/requestDigest | 必填；batchId首次冻结不变，batchCreatedAt为投递冻结时刻；requestDigest按第6节。 |
| parent | 必填null，或第7节 `{batchId,requestDigest,rejectionToken}`；最多8层派生。 |
| cycles | 非空数组；每项固定 `{cycleId,manifestUtf8,manifestSha256,contextUtf8,contextSha256,transportManifest}`。原UTF-8内容通过JSON字符串转义携带，unescape再UTF-8所得字节必须与声明SHA一致。 |
| samples | 非空数组；每项固定 `{sampleId,cycleId,part,parts,pointIds,payloadUtf8,sourceSha256,contentDigest}`；part从1开始，pointIds为本片完整点集合，不能省略失败点。 |

`payloadUtf8` 是现有 SamplePayload v2 原文，**其中 points[pointId] 是唯一自描述点位体**。不另提供可编辑的规范points副本。Backend严格解析该原文形成只读规范投影；它仍保留原文原字节，传输/查询投影不能冒充原文。例子中的 `revision` 在规范输出映射为 `configRevision`；原字符串不改。

原SamplePayload固定字段：schemaVersion=2、sampleId/cycleId/instanceId/plcId/sourceGeneration/sourceSeq/groupId/revision/dbNumber/origin/startedAt/finishedAt/savedAt/points；sourceSeq为`[1-9][0-9]*`十进制字符串，1..9223372036854775806，不允许JSON number、前导零或跨PLC比较。dbNumber为1..65535整数。startedAt≤各点observedAt≤finishedAt≤savedAt；读取跨度/单调duration不能用来伪造日历时间。origin为1–64字节原来源描述，provider不替它证明物理设备。

每个PointFact固定definition/value/observedAt/quality/reason。definition完整保留当前Point：id/plcId/dbId/sourcePath/name、可选nameMode、dataType/comment/enabled/groupId/address；definition.id须等于points字典键，plcId/group/DB归属与样本/context相符。address为null或完整 `{offset,bit,confirmed,origin,reason}`；offset0..65535，BOOL bit0..7，其他bit=null；已知类型宽度不能越DB边界。nameMode若有则为现有pending/auto_path/auto_address/manual，不伪造managed/legacy枚举；未转换legacy可省略。不得为上传重命名原名字；未知schemaVersion/有值未知PLC类型拒绝422，不执行任何名称/地址。

contextUtf8携带原configuration_revisions/context的JSON原文，sha256与revision关联。只解释其中plcs/dbs/points/groups对当前样本的归属、定义、启用及成员；sources、树/导入诊断等作为有界不执行的原证据保留，不当作SQL/模板/handler。上下文原文中的合法扩展不变成数据库字段。首次或换来源时维护命令明确选定该context SHA；请求不能凭自报更高UUID/configRevision接管。API不返回context全文，避免把配置源码/端点当匿名目录。

manifestUtf8为现有CycleManifest v2完整原文（包括reads），其身份/来源/序号/group/revision/时间与样本相同；samples列原source sampleId/dbNumber/原sha256；expectedPointIds是完整预期集合。reads保留dbNumber/start/size/startedAt/finishedAt/durationMs/quality，durationMs整数0..9007199254740991，不与日历差额混成同一时间事实。按DB分包、跨DB依序读取不是物理原子帧。

transportManifest每项为 `{sampleId,dbNumber,sourceSha256,parts:[{part,pointIds,contentDigest}]}`；同一源样本part连续1..N、点集合互斥，全部parts的并集恰为原payload点集合；全轮样本与原manifest一一对应，所有点并集恰为expectedPointIds。收到部分原样本时先校验可证明的关联和已知子集，其余仅expected；所有材料验证齐全才complete。原manifest/transportManifest同cycle异内容409。partial ACK不能冒充原样本全片或整轮完成。

固定片在冻结前由源pointId UTF-8字节顺序贪心分组，下一点使512点或128KiB规范points预算超限时开新片；相同源原文/profile始终同一分片。sampleId保持原ID，片身份为(instanceId,sampleId,part)，不是改名的新样本；整个原payload重复携带使每片可独立验证原SHA及其point定义/值，不需要先拼一个未验证的大原文。对当前一片样本part=parts=1。原payload本身超过512KiB不隐式迁移或重新生成；明确413，后续版本另定。

### 5.2 值与缺测矩阵

| dataType | quality=good 的JSON value | 非good/缺测 |
| --- | --- | --- |
| BOOL | JSON boolean；0/1不是布尔 | quality=bad，value=null，非空reason。 |
| BYTE/USINT；INT；UINT/WORD；DINT；UDINT/DWORD | JSON整数，分别0..255、-32768..32767、0..65535、-2147483648..2147483647、0..4294967295；bool/字符串不替代 | 同上；不得补零/沿用旧成功值。 |
| REAL | 有限JSON number，abs≤3.4028234663852886e38，非零abs≥1.401298464324817e-45；保留原payload已解码数字的十进制语义，不再次binary32量化，不使用业务bi-json规则；范围检查不证明来源PLC原bit | 同上；NaN/Infinity必须在源变成bad/null/reason，不能作为JSON数提交。 |
| CHAR；STRING[n]，n=1..254 | 与当前local_decode一致为ASCII：CHAR一个U+0000..U+007F字符；STRING最长n个ASCII字符，字符串原貌包括空串/空格/转义保留 | 同上；未支持的类型仅允许bad/null及reason=unsupported_type，原definition照录。 |

quality首版仅good/bad；good必须有非null合格value且reason=null；bad必须value=null且reason为1..128字节稳定原因。definition/observedAt在bad仍必需；address缺失/未确认只可bad。空points拒绝，失败仍是完整轮成员。显示目录只从已上报、当前定义、未到期的latest结果形成；bad也有可解释定义，完全未上报点不造目录。

### 5.3 完整合成请求示例

下例由原v2合成样本构成；三个字符串中的原JSON只为演示，没有读取SQLite。其source/manifest/context SHA、contentDigest与requestDigest须以第6节算法校验；不是当前DAA可直接调用的上传实现。后续vectors.json还须包含两个PLC同DB、同PLC跨DB、两组和两片仅到一片的完整正反例。

```json
{
  "contractVersion": "plc-facts/v1",
  "sourceProfile": "daa-local/v2",
  "digestProfile": "pf-json/v1",
  "instanceId": "daa-demo",
  "batchId": "batch-demo",
  "batchCreatedAt": "2026-11-04T10:00:01.000+08:00",
  "parent": null,
  "cycles": [
    {
      "cycleId": "cycle-demo",
      "manifestUtf8": "{\"cycleId\":\"cycle-demo\",\"expectedPointIds\":[\"point_x\"],\"finishedAt\":\"2026-11-04T10:00:00.200+08:00\",\"groupId\":\"group-demo\",\"plcId\":\"plc-demo\",\"reads\":[{\"dbNumber\":1,\"durationMs\":24,\"finishedAt\":\"2026-11-04T10:00:00.124+08:00\",\"quality\":\"good\",\"size\":2,\"start\":0,\"startedAt\":\"2026-11-04T10:00:00.100+08:00\"}],\"revision\":\"config-demo\",\"samples\":[{\"dbNumber\":1,\"sampleId\":\"sample-demo\",\"sha256\":\"4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2\"}],\"savedAt\":\"2026-11-04T10:00:00.201+08:00\",\"schemaVersion\":2,\"sourceGeneration\":\"generation-demo\",\"sourceSeq\":\"1\",\"startedAt\":\"2026-11-04T10:00:00.100+08:00\"}",
      "manifestSha256": "sha256:77ddfb39fd9314aad8f51f7fdec465cf02da8653142a12728d00a7d5c79f49d4",
      "contextUtf8": "{\"dbs\":[{\"complete\":true,\"flat\":true,\"id\":\"db-demo\",\"length\":2,\"name\":\"DB1\",\"number\":1,\"plcId\":\"plc-demo\",\"sourceId\":\"source-demo\",\"tree\":[]}],\"groups\":[{\"enabled\":true,\"id\":\"group-demo\",\"intervalMs\":1000,\"name\":\"Demo group\",\"plcId\":\"plc-demo\"}],\"plcs\":[{\"connectTimeoutMs\":1000,\"deadlineMs\":3000,\"enabled\":true,\"host\":\"192.0.2.10\",\"id\":\"plc-demo\",\"ioTimeoutMs\":1000,\"name\":\"Demo PLC\",\"port\":102,\"rack\":0,\"slot\":1}],\"points\":[{\"address\":{\"bit\":null,\"confirmed\":true,\"offset\":0,\"origin\":\"source\",\"reason\":\"\"},\"comment\":\"\",\"dataType\":\"INT\",\"dbId\":\"db-demo\",\"enabled\":true,\"groupId\":\"group-demo\",\"id\":\"point_x\",\"name\":\"DB1_temperature_Int\",\"nameMode\":\"manual\",\"plcId\":\"plc-demo\",\"sourcePath\":\"炉温.当前值\"}],\"schemaVersion\":1,\"sources\":[{\"content\":\"DATA_BLOCK DB1 demo\",\"dbNumber\":1,\"diagnostics\":[],\"id\":\"source-demo\",\"name\":\"demo.scl\",\"plcId\":\"plc-demo\",\"sha256\":\"c0835a81c400136b0cba2a0b34caa208df991cc8b57870ce4d5fbccd7c57f925\"}],\"storage\":{\"quotaBytes\":1073741824,\"retentionDays\":7}}",
      "contextSha256": "sha256:029466a7c25242273691a4ae957a00c44e52fc6a8a987312f8e3c055f206ba42",
      "transportManifest": [
        {
          "sampleId": "sample-demo",
          "dbNumber": 1,
          "sourceSha256": "sha256:4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2",
          "parts": [
            {
              "part": 1,
              "pointIds": [
                "point_x"
              ],
              "contentDigest": "sha256:93b60f03748d5e780ef326856dfca77e60c8be29a39fc3af56fae083e606b877"
            }
          ]
        }
      ]
    }
  ],
  "samples": [
    {
      "sampleId": "sample-demo",
      "cycleId": "cycle-demo",
      "part": 1,
      "parts": 1,
      "pointIds": [
        "point_x"
      ],
      "payloadUtf8": "{\"cycleId\":\"cycle-demo\",\"dbNumber\":1,\"finishedAt\":\"2026-11-04T10:00:00.200+08:00\",\"groupId\":\"group-demo\",\"instanceId\":\"daa-demo\",\"origin\":\"s7\",\"plcId\":\"plc-demo\",\"points\":{\"point_x\":{\"definition\":{\"address\":{\"bit\":null,\"confirmed\":true,\"offset\":0,\"origin\":\"source\",\"reason\":\"\"},\"comment\":\"\",\"dataType\":\"INT\",\"dbId\":\"db-demo\",\"enabled\":true,\"groupId\":\"group-demo\",\"id\":\"point_x\",\"name\":\"DB1_temperature_Int\",\"nameMode\":\"manual\",\"plcId\":\"plc-demo\",\"sourcePath\":\"炉温.当前值\"},\"observedAt\":\"2026-11-04T10:00:00.123+08:00\",\"quality\":\"good\",\"reason\":null,\"value\":202}},\"revision\":\"config-demo\",\"sampleId\":\"sample-demo\",\"savedAt\":\"2026-11-04T10:00:00.201+08:00\",\"schemaVersion\":2,\"sourceGeneration\":\"generation-demo\",\"sourceSeq\":\"1\",\"startedAt\":\"2026-11-04T10:00:00.100+08:00\"}",
      "sourceSha256": "sha256:4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2",
      "contentDigest": "sha256:93b60f03748d5e780ef326856dfca77e60c8be29a39fc3af56fae083e606b877"
    }
  ],
  "requestDigest": "sha256:e279f83a003d8cc3b6c2ed779c5dbc3252e90ead9d7c4360cf05e7649e91dc35"
}
```

## 6. R05：三个摘要层、规范字节与独立向量

1. 原SHA为 `sha256:`+64小写hex，覆盖payloadUtf8/manifestUtf8/contextUtf8各自unescape后UTF-8**原字节**，包括空白和原offset/数字拼法。无重新缩进、Unicode归一化或先解析再声称原文相同。DAA本地原sha256无前缀时只增加wire前缀，原hex不改。
2. `pf-json/v1`：验证后的静态字段用精确camelCase；对象键按UTF-8字节升序；字符串原Unicode scalar，采用JSON最小转义（仅双引号、反斜杠、U+0000..001F，控制字符用小写`\\u00xx`，不转义`/`或非ASCII）；无空白。整数/Decimal无指数、去无效尾零、负零归0；不经float。规范时间转换一次到固定UTC+08:00，始终9位小数，原文另存不改；数组除下述集合外保留顺序。
3. contentDigest覆盖规范对象 `{sourceSha256,sampleId,cycleId,instanceId,plcId,sourceGeneration,sourceSeq,groupId,configRevision,dbNumber,origin,startedAt,finishedAt,savedAt,part,parts,points}`，points仅本片，但definition完整。其字节前置 `plc-facts/v1\0sample-part\0` 再SHA-256。pointIds与points键集合相同且按UTF-8排序，不单独改变语义。contentDigest本身不进入自身；原source SHA进入，故同身份原文哪怕仅格式变化也冲突，不把语义相等误称原文相等。
4. cycleDigest覆盖 `{manifestSha256,contextSha256,transportManifest}`，transportManifest按sampleId、parts按part排序，pointIds按UTF-8排序，前置 `plc-facts/v1\0cycle\0`。原manifest中reads数组顺序不能重排冒充同一次读取。
5. requestDigest覆盖外层**除requestDigest外全部字段**，cycles按cycleId、samples按(sampleId,part)排序，parent保持冻结内容；所有原UTF-8字符串仍为原字符串，不把内层规范化替换原文。batchCreatedAt在此统一9位上海时间，sourceSeq不转number；前置 `plc-facts/v1\0batch\0`。因此HTTP空白/外层key排列不改变摘要，改变原材料字节、成员/片/parent/身份则改变。重复对象/成员拒绝而非排序去重。
6. 查询 `projectionDigest`覆盖实际返回的规范part投影（含被筛选后points），前置 `plc-facts/v1\0query-projection\0`；明确不同于原sourceSha256与完整contentDigest，过滤不能假称返回了完整原文。

以下是独立stdlib可复算的字节向量；Development不得用被测canonical本身生成expected，再测试它等于自己。SHA层和完整请求向量同样须以独立实现或逐字节人工固定预期。

| 向量 | 精确UTF-8字节文本（不含Markdown反引号） | SHA-256（无域前缀的基础向量） |
| --- | --- | --- |
| empty | `{}` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| numbers | `{"n":1,"z":0}` | `11beb7b10beec1509e9c51e46aaa2445ba87a6134074c358144a087207082403` |
| data-keys | `{"A":"中文","a":"x_y"}` | `f0b76ee71d3de40923891c395d4e603c0fcebc252ea86253ed61734fe286d0a6` |

| 域向量 | 规范字节/域 | sha256结果 |
| --- | --- | --- |
| sample-part-empty | ASCII `plc-facts/v1` + NUL + ASCII `sample-part` + NUL + UTF-8 `{}` | `sha256:2c28257e2df4234ce62fd9deb1fd7d2a948ad95742224f91c5b3fad081ceb4ca` |
| cycle-empty | ASCII `plc-facts/v1` + NUL + ASCII `cycle` + NUL + UTF-8 `{}` | `sha256:1f49907793e5bc4fabb661186cd3c158986d5bc6b760d87c8cd652da38b52ace` |
| batch-empty | ASCII `plc-facts/v1` + NUL + ASCII `batch` + NUL + UTF-8 `{}` | `sha256:e0f1dedaff692e2ce5dedb0dedd6997bdb963732fb910ec0a62b3824c3bceeb3` |
| query-projection-empty | ASCII `plc-facts/v1` + NUL + ASCII `query-projection` + NUL + UTF-8 `{}` | `sha256:6f195650e8e74f2327437afbc08c6051b0cf4d001d07c2ed73d02e90574f5285` |
| definition-empty | ASCII `plc-facts/v1` + NUL + ASCII `definition` + NUL + UTF-8 `{}` | `sha256:339b46388541dabcf9c099b1c290596cde85578cf61434a1bee20b354de7202b` |
| definition-set-empty | ASCII `plc-facts/v1` + NUL + ASCII `definition-set` + NUL + UTF-8 `{}` | `sha256:42b6200b76449af730f97b714c0a72add947a9cc75577d83e6ade84da5c65d3b` |

完整第5.3节样例独立预期：

| 摘要 | 预期 |
| --- | --- |
| sourceSha256 | `sha256:4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2` |
| manifestSha256 | `sha256:77ddfb39fd9314aad8f51f7fdec465cf02da8653142a12728d00a7d5c79f49d4` |
| contextSha256 | `sha256:029466a7c25242273691a4ae957a00c44e52fc6a8a987312f8e3c055f206ba42` |
| contentDigest | `sha256:93b60f03748d5e780ef326856dfca77e60c8be29a39fc3af56fae083e606b877` |
| cycleDigest | `sha256:be762e20d082fc2519c10bb2617588c973f6da2be2a765e85d13115c66d5dfb7` |
| requestDigest | `sha256:e279f83a003d8cc3b6c2ed779c5dbc3252e90ead9d7c4360cf05e7649e91dc35` |
| projectionDigest | `sha256:b6b7bb6c66ce92107e76841cfdb5637d8682314f08094e5d77b6416794936de0` |

定义摘要补充向量使用第5.3节point_x：规范definition只保留第8.1节字段，address为`{"bit":null,"confirmed":true,"offset":0}`；definitionDigest=`sha256:57da9fe8cb09be36ce592ccfa9d4c58a48bfa8767a6be0756c5fe4dc54d35168`，该单点PLC的definitionSetDigest=`sha256:3dbb84547a5971668f78412c4552fcd1512b6042dd4cdd7dd7dca47a0a1035af`。这两个摘要不包含comment、group.intervalMs、其他PLC或opaque revision。

正向必须包含1/1.0/1e0和0/-0规范相同、外层数组集合排列相同、中文与x_y/大小写数据键原样、等瞬间offset/9位时间一致。反向必须包含原payload空白改变source SHA、point定义/value/quality/观察时间/片/来源/parent改变相应摘要、缺值与0不同、reads次序不同、伪造digest/重复key/不合法类型拒绝。业务 `bi-json/v1` 的float32重规范、sourceRefs集合或request/business双摘要不得套到本profile。

## 7. R06：全批事务、完整回执、unknown与退休派生

### 7.1 持久边界与幂等窗口

批身份 `(instanceId,batchId)`，片身份 `(instanceId,sampleId,part)`；同PLC代次序号唯一对应cycle，source sampleId与cycle/DB/原SHA关系不可改。所有key用完整UTF-8精确二进制比较，不使用大小写/尾空格不敏感collation或截断hash当唯一键。新批冻结后不得原地增删样本/片或修正文义。

解析/规范摘要在DB事务前完成；进入事务后先锁第10节单例，再current read原批/片证明和source binding。优先恢复相同批稳定结果，异requestDigest409；再判片异contentDigest/原cycle异内容409，再判未知source或过期等。raw、有效latest、sample receipt/feed、cycle完整性与batch成功回执在同库同一事务提交。只在真实commit且所有可失败的yield依赖退出完成后发送成功；flush、内存入队、202、日志均不是ACK。

Service独占commit/rollback；CRUD不提交。使用公开get_db_session建立本模块依赖，不通过会二次commit的通用get_db偷换事务边界；局部FactsRoute保证完整request/function依赖退出后才发送一次响应。事务开始前拒绝可标none；已开始且无法证明rollback或commit结果的503/500必须标unknown。连接断开、commit超时或响应前退出异常不能假称not_committed。无盲目事务重试；原请求后续重放从数据库恢复。

sample/cycle/batch最小证明自**首次可靠记录DB时间起120天**，重复不续期；证明只含身份、摘要、观察/到期边界、点ID/片覆盖、稳定首次结果和发布位置，无原值/原文/name/path/配置源码。新批首次冻结超过24小时且无记录时，在门闩内记录终结拒绝 `batch_admission_expired`，允许合法未到期成员在退休规则下派生；有记录优先恢复，不因24h门槛吞掉已提交批。120天后不保证原批回执可恢复；旧事实仍按原observedAt拒绝，不因证明删除变成新数据。调用方不得复用任何原身份或改变sourceSeq伪装新事实。

### 7.2 成功回执完整形状

HTTP/code=200、Content-Type application/json。所有ID/大序号为字符串，points原样键不经过共享camelize。以下与示例请求关联的摘要由第5.3节生成材料替换；结果字段定义完整。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v1",
    "digestProfile": "pf-json/v1",
    "instanceId": "daa-demo",
    "batchId": "batch-demo",
    "requestDigest": "sha256:e279f83a003d8cc3b6c2ed779c5dbc3252e90ead9d7c4360cf05e7649e91dc35",
    "receiptId": "11111111-1111-4111-8111-111111111111",
    "status": "committed",
    "persistence": "committed",
    "newFactsCommitted": true,
    "outcome": "created",
    "originalOutcome": "created",
    "confirmation": "facts_committed",
    "commitSerial": "1",
    "committedAt": "2026-11-04T10:00:01.000000+08:00",
    "proofExpiresAt": "2027-03-04T10:00:01.000000+08:00",
    "results": [
      {
        "sampleId": "sample-demo",
        "part": 1,
        "parts": 1,
        "sourceSha256": "sha256:4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2",
        "contentDigest": "sha256:93b60f03748d5e780ef326856dfca77e60c8be29a39fc3af56fae083e606b877",
        "outcome": "created",
        "originalOutcome": "created",
        "confirmation": "created",
        "sourceSampleComplete": true,
        "position": {
          "commitSerial": "1",
          "ordinal": 1
        },
        "latestAdvancedPointIds": [
          "point_x"
        ],
        "expiresAt": "2027-02-04T10:00:00.123000000+08:00",
        "valueReadable": true
      }
    ],
    "cycles": [
      {
        "cycleId": "cycle-demo",
        "cycleDigest": "sha256:be762e20d082fc2519c10bb2617588c973f6da2be2a765e85d13115c66d5dfb7",
        "complete": true,
        "qualityGood": true,
        "receivedParts": 1,
        "expectedParts": 1
      }
    ]
  }
}
```

`receiptId`为稳定batch UUID；`commitSerial`为首次含新事实事务的发布序号，无新事实重复批可null；committedAt是首次可靠事务所记录的DB时间，表示该提交事务的时间戳而非可排序的commit-clock。`originalOutcome`为首次created/duplicate，重放outcome=duplicate但首次各片/整轮/时间/发布位置保留；最新查询另提供当前整轮进度，不能重放时改写首次回执。

每片confirmation=created/duplicate/historical_committed，sourceSampleComplete仅证明该sample全部固定片验证并收齐；cycle.complete要求所有expected样本和片齐全，qualityGood另算，不能以收到的成员数取代应有集合。latestAdvancedPointIds是首次事务真实推进的点，不是ACK前置，不证明现在仍是latest。重放时newFactsCommitted=false，outcome=duplicate；原identity/digest/position/committedAt/originalOutcome/latest推进范围和首次完整性保持，confirmation与valueReadable只可按当前原值到期情况改为historical_committed/false。persistence=committed证明原提交，不表示重放再次写事实。expired replay只返回最小身份/摘要证明，绝不返回原值或重建latest；证明TTL不因这些派生读态更新续期。

### 7.3 拒绝/unknown及混合批次

| 情况 | 固定结果及安全后续 |
| --- | --- |
| 同片同内容、仍在120天证明期 | 新批可以确认duplicate；同原批恢复稳定结果，不新增raw、不续TTL。 |
| 同批异内容、同片异内容或manifest冲突 | 409；全批无新事实。原提交证明保持；冲突成员隔离，不能换sampleId掩盖。 |
| 新批含有效、过期无证明、冲突或source不合格成员 | 全批不提交任何新事实/推进latest；在同锁事务只写终结拒绝摘要，逐成员诊断不是partial ACK。错误优先级：身份冲突409 > source拒绝403 > 过期410 > 其余422。 |
| 已过期但有有效历史证明的成员 + 有效新成员 | 该历史成员按historical_committed确认，不恢复原值；其余合法成员可在同批提交。任何另外一个不可确认成员仍导致整批无新事实。 |
| 数据库已提交，响应丢失/本地ACK失败 | 原批重试恢复原结果；不新造batch/sample，不推断回滚。 |
| commit/rollback/依赖退出结果不明 | 503/500，persistence=unknown，retryable=true，retirementAllowed=false；先原请求恢复。 |
| 明确终结拒绝已可靠记录 | data.persistence=rejection_recorded、newFactsCommitted=false；只可凭有效rejectionToken派生原成员的相同ID/内容子集，不改原批。 |
| proof已经删除或批超过恢复窗 | 410 proof_expired，确认=none/unknown历史边界；不得伪造ACK。旧observedAt达到截止无条件拒绝，无原值复活。 |

终结拒绝响应绑定版本、instance/batch/requestDigest、稳定receiptId、DB recordedAt、rejectionToken及expiresAt、各片`diagnosis`（eligible/duplicate_proven/expired_unproven/conflict/source_rejected）、可引用的historicalProof（仅有效摘要，不等于本拒绝的成功results）。拒绝token首次由当时服务HMAC生成，覆盖parent身份/摘要、完整成员身份+digest集合、reason和该batch首次记录起120天的proof截止；**其原token字符串、token的SHA-256及绑定内容同拒绝记录持久保存**，重试返回同一token，不续期。已存在同batchId异内容时不能覆盖原batch记录来生成另一个拒绝token，只返回409及none本次新事实边界；先恢复原冻结请求，再处理合法成员。

父拒绝凭据以数据库原记录为真相：门闩内读取该instance/batch的terminal=rejected记录，核对requestDigest/未到期proof，再constant-time比较提交token的SHA-256与持久原SHA，成员子集及派生深度均从原记录验证；不信任token自报内容，也不要求用**当前**HMAC key重新签验旧token。故单key轮转或进程重启后，原拒绝仍可重放、原token在原120天窗口内仍可派生；父记录缺失/到期即410，不以单独MAC通过补造历史证明。存原token仅为有限拒绝证明的稳定恢复，不是调用者认证凭据，不输出日志，不引入keyring或多key管理。

派生必须新batchId、parent三字段引用**已终结拒绝**，所有成员必须是原集合内同ID/part/contentDigest和同原材料的子集。服务端在门闩内验证parent记录/token及无独立事实副作用，绝不接受unknown父；新增成员不可以借parent，须独立新批。原批保持rejected，合法成员可公平继续；被排除/过期/冲突材料仍需DAA后续独立需处理记录，后端拒绝不是本地删除许可。一个片被其他批确认不自动终结unknown原批，仍须恢复后再处理引用。

完整失败示例（以下摘要为有效格式占位，不是算法向量；完整有值样例在vectors.json按合成请求生成）：

```json
{"code":410,"message":"plc_facts.sample_expired","errorCode":"plc_facts.sample_expired","data":{"contractVersion":"plc-facts/v1","instanceId":"daa-demo","batchId":"batch-mixed","requestDigest":"sha256:0000000000000000000000000000000000000000000000000000000000000000","receiptId":"receipt-rejected-demo","recordedAt":"2026-11-04T10:00:01.000000+08:00","persistence":"rejection_recorded","newFactsCommitted":false,"retryable":false,"retirementAllowed":true,"rejectionToken":"opaque-server-rejection-token","rejectionExpiresAt":"2027-03-04T10:00:01.000000+08:00","diagnostics":[{"sampleId":"sample-valid","part":1,"diagnosis":"eligible","historicalProof":null},{"sampleId":"sample-old","part":1,"diagnosis":"expired_unproven","historicalProof":null}]}}
```

```json
{"code":503,"message":"plc_facts.commit_outcome_unknown","errorCode":"plc_facts.commit_outcome_unknown","data":{"contractVersion":"plc-facts/v1","instanceId":"daa-demo","batchId":"batch-unknown","requestDigest":"sha256:0000000000000000000000000000000000000000000000000000000000000000","persistence":"unknown","newFactsCommitted":null,"retryable":true,"retirementAllowed":false,"diagnostics":[],"rejectionToken":null}}
```

无法可靠解析身份的格式失败使用同一失败壳，data为 `{persistence:"none",newFactsCommitted:false,retryable:false,retirementAllowed:false,diagnostics:[]}`，不回显原body。不得把异常连接串、SQL、token或私密context放入DEBUG错误。错误真实HTTP/code一致：403 scope_rejected/source_rejected；409 batch_content_conflict/sample_content_conflict/cycle_content_conflict/binding_conflict；410 sample_expired/proof_expired/cursor_expired/cursor_gap/parent_proof_expired/batch_admission_expired；413 payload_too_large；415 media_type；422 invalid_request/digest_mismatch/cursor_mismatch；429 busy；503 not_ready/unavailable/commit_outcome_unknown/clock_invalid/capacity_exceeded；500 internal_error，均加`plc_facts.` namespace并登记manifest/error enum。无202、无伪admin、无旧全局失败合同变化。capacity_exceeded为可恢复容量拒绝，retryable=true，但仅unknown才需要先按原请求核实提交；none只证明本次未写新事实，不否认历史提交。

## 8. R07：逐点latest、受控来源/定义与时间

### 8.1 唯一当前来源及定义采用

`source_bindings`按plcId唯一，包含current instanceId/sourceGeneration、单调sourceEpoch、采用时configRevision/contextSha256引用、active definitionSetDigest、允许seq区间、单调bindingRevision；最多8个明确旧代次/定义集raw-only窗口（含instanceId/generation/definitionSetDigest/seqFrom/seqThrough）。首次没有binding时503；不从任意首次POST自动登记/抢占，不按UUID、configRevision字符串、HTTP到达或观察时间授予当前来源。

明确运行批准后的维护 `adopt` 使用人工审阅的原context、expectedBindingRevision与切换资料，锁同一个stream_state，CAS更新binding。它不是匿名HTTP管理入口。代次切换必须冻结旧seq截止、新代次基线和唯一current，旧代次只能在明确窗口补raw、永不推进latest；正常重启/换周期/移组不重置sourceSeq。旧source新数据不在配置窗口则拒绝，合法旧raw有自己的历史身份。

current `(instanceId,sourceGeneration)` 任一改变时，在**同一adopt事务**递增sourceEpoch（首次采用为1）、移除该PLC全部旧latest行并准确调整逻辑字节计数，再提交新binding/基线；raw/历史proof不删。latest写入和查询都要求row.sourceEpoch等于当前sourceEpoch，查询在同一一致性读事务取得binding及rows，sourceSeq只在该epoch内逐点比较。旧代次seq1005不得阻挡新代次从已批准基线1开始；切换commit后的新查询在新代次尚无结果时latest为空，不能沿用旧代次值。bindingRevision用于任何受控绑定变更和分页失效；sourceEpoch只用于来源代次隔离，两者不混用。

definitionDigest使用第6节相同的ASCII `plc-facts/v1` + NUL + ASCII `definition` + NUL域，内容为pf-json/v1({id,plcId,dbId,sourcePath,name,nameMode,dataType,enabled,groupId,address})；nameMode省略统一null，address只含offset/bit/confirmed（或null），排除注释、地址来源说明、值、quality、时间和revision字符串。definitionSetDigest使用域`definition-set`，内容为 `{plcId,plcEnabled,points:[{pointId,dbNumber,groupEnabled,definitionDigest}]}`，包含context内本PLC全部点（含disabled），pointId升序；无group的groupEnabled=false。DB号从context的dbId解析，不能仅用一个可能重命名的DB显示名。

**同一来源内只有definitionSetDigest发生变化才需有界维护选择**：输入新context SHA及effectiveFromSeq，禁止推断opaque revision顺序。单纯周期、注释、其他PLC或无关配置revision变化而本PLC定义集不变，后续同current generation请求可以正常接收/推进，不强迫人工重选全部PLC；sourceEpoch不变，原有效latest继续可查询，不能因旧row的context SHA/configRevision或bindingRevision不同而整组隐藏。context原SHA与configRevision仍逐样本保留，不能冒称原文相同。实际换定义时，对已存在latest逐点比较definitionDigest：未变化的保留原结果和sourceRefs；改变/禁用/消失的点撤销当前值资格并移除该latest行，旧值不复制到新定义，不补零。新context中从未上报点不造值/目录，不另建可编辑永久pointCatalog。旧定义集后续只可按raw-only资格接收，因此删latest不授权旧定义复活。

后续POST必须提供其当时完整context原文与正确SHA，Backend独立派生本PLC definitionSetDigest；既存旧来源/定义集也可在其raw-only窗口补历史。仅current generation+active definitionSetDigest中有效点可以推进latest；本PLC定义集不变的不同context SHA不阻断其他点进度。未声明变化只能呈现陈旧/到期；本合同不能自动发现PLC程序实际漂移。人工换binding是数据准入约束，匿名声明可被冒用这一取舍不消失。

### 8.2 原子逐点顺序

latest的主键是(plcId,pointId)，每点记录sourceEpoch、source instance/generation/seq、config/definition digest、sample/part/cycle/group/DB、quality/reason/value/原observedAt及自身expiry。持有全局门闩后仅当前sourceEpoch内本点更高sourceSeq、有效current binding/definition且未到期才更新；等seq同点异内容409，旧seq只raw，禁止跨generation直接比较seq。某点seq1005不使另一点合法seq1001被跳过；同DB不同组仅更新其点，两个PLC同DB各自独立。源序号相同的整轮不同DB/片可以分别推进不同点。

latest是最近结果：新seq的bad/null更新后不能继续把旧good当当前；不额外维护lastGood副本。quality、新鲜度和保留期分别表达，asOf是查询时刻、observedAt是原采集时间。组移位保留pointId，单包缺点不是停用；完整manifest missing是完整性缺口，不触发删除别组点。

### 8.3 上海与原精度

全部新规范日历时间固定东八区Asia/Shanghai；其他明确offset仅在边界转一次，不依据机器系统TZ或历史DST/LMT换义。接受RFC3339最多9位小数，拒绝缺offset、闰秒、超范围或第10位及更多小数；原文原时间仍逐字保留。规范输出9位小数、+08:00；DB来源/到期比较用DATETIME(6)上海墙上时间+0..999 submicro_ns，原字符串保留必要源精度。MySQL年份1000..9999且加月不溢出。不得为匹配旧业务DATETIME(3)而舍弃事实精度。

系统recordedAt/committedAt/asOf取数据库CURRENT_TIMESTAMP(6)，源savedAt不冒充后端提交时间。运行采用先验证DB时间实际为+08:00；本模块检查session CURRENT_TIMESTAMP与UTC_TIMESTAMP差为28800秒且不比stream_state已确认时钟倒退，否则503 clock_invalid。既不改全局engine/session offset，也不把Python now()写入系统持久时间。B必须覆盖不同宿主TZ、月末、闰年、亚微秒和时钟倒退；A纯函数替身不是实际数据库时区证明。

## 9. R08：七表、唯一迁移链、物理/metadata口径

七表全部归plc_facts，无跨owner写入、无旧raw FK、无业务级联。**本文64→71→75均指本仓Model/Alembic迁移管理的应用表，不含Alembic自建的alembic_version维护表**；真实information_schema总数可能多1，验收按应用表名集合比较，另核维护表revision，不能盲断言数据库总表数。Model/DDL/Schema字段/非空/CHECK/索引一致；所有表有DATETIME(6) created_at/updated_at，由已确认DB时间填入，不散落UTC默认。关键key使用完整VARBINARY(512)，短枚举用稳定ASCII；摘要BINARY(32)，sourceSeq/serial为正BIGINT（wire字符串），原文/规范数字投影以LONGBLOB保存精确UTF-8，不能经MySQL JSON double规范化丢精度。

| 表 | 数据/键/必要索引与期限 |
| --- | --- |
| plc_facts_stream_state | 单例id=1，storageEpoch UUID、profile/adoptionId、schemaProfile/verifiedSchemaRevision/F7、highSerial、proofFloorSerial/proofFloorOrdinal、lastDbTime、逻辑原值字节/proof行数与上限、cleanup成功/积压摘要；CHECK单例/非负。migration只建空结构，显式adopt才插行，普通请求绝不创建。无原值，可长期保留固定一行。 |
| plc_facts_source_bindings | PK plcId；当前来源/sourceEpoch/采用context SHA引用/active definitionSetDigest/seq窗口、bindingRevision及有界raw-only窗口；无原值/完整目录。维护CAS唯一writer，按PLC最多256行。 |
| plc_facts_batches | PK或unique(instanceId,batchId)，稳定receipt UUID、requestDigest、terminal committed/rejected、首次结果/成员摘要、parent身份、原拒绝token及token SHA、recordedAt/proofExpiresAt；索引(proofExpiresAt,receiptId)，不存完整请求/值。120天，不续期；原token随proof删除。 |
| plc_facts_sample_receipts | unique(instanceId,sampleId,part)，unique(commitSerial,ordinal)，来源/cycle/DB/pointId覆盖、源/content摘要、观察min/max、rawExpiresAt、首次结果/proofExpiresAt；索引(plcId,commitSerial,ordinal)和(proofExpiresAt,commitSerial)。兼有限feed/去重证明，不是业务事件总线，无原值/definition/path。 |
| plc_facts_raw_samples | unique(instanceId,sampleId)，cycle/来源/seq/DB、sourceSHA、payloadUtf8、规范投影、min/max观察及最早point expiry；(expiresAt,id)与(plcId,dbNumber,id)索引。部分片只发布已确认覆盖；原文读取另需sourceSampleComplete。原文达到最早成员截止即逻辑不可读，有限清理。 |
| plc_facts_cycles | unique(instanceId,cycleId)，unique(plcId,sourceGeneration,sourceSeq)，原manifest/context UTF-8与SHA、transportManifest、expected/received摘要、complete与qualityGood、原文expiry/proofExpiresAt；expiry/proof索引。原文到期清除，随后只留有限无值完整性摘要。 |
| plc_facts_latest_points | PK(plcId,pointId)，sourceEpoch/current definition/源身份、seq、DB/group、规范PointFact、observedAt+ns/expiry+ns；(plcId,dbNumber,pointId)、(expiresAt,pointId)索引。逐点expiry，无raw FK/CASCADE，最新坏值与好值同规则。 |

source sample/part、cycle和batch之间的关联在同owner内保留精确摘要/键；如果采用FK，只能RESTRICT/显式先删子，禁止ON DELETE CASCADE跨有限证明与有效原值。完整复合唯一键预算在MySQL8.4.6/InnoDB下静态及真实验证；不能前缀unique、hash-only equality或忽略冲突字段。所有计数/结果JSON都受第4节成员上限，不能装无限日志。

迁移固定且已经与BE010 PM协调：

```text
既有六条 ... -> f6a8c0e2b4d6（64张应用表）
 -> 0a2c4e6f8b10（本任务，仅七新表，应用71）
 -> 1b3d5f7a9c20（BE010 r2自有，仅其四张A0 pending表，应用75）
```

BE010后继精确路径为 `backend/alembic/versions/20261104_1400_1b3d5f7a9c20_add_business_integration_receipts.py`，down_revision=`0a2c4e6f8b10`。该文件不在本任务allowlist。本任务不得替其迁移equipment/performance/monitor三receipt及performance观察事件表，不从f6另开并列head，也不重写六旧migration或用autogenerate把别人的pending Model带进本DDL。

命名profile：BE009-A静态目标=f6→0a2，**预期物理应用表71，源码完整metadata75=71+BE010 pending4**；BE009-B实际upgrade必须显式到0a2，不以当时head自动升级别人的任务。比较本七表+既有64的选定metadata子集（排除alembic_version），pending4单独列名/缺失为预期而非schema已采用。BE010后继完成后才允许相应联合profile应用表75==metadata75；其旧业务时间整改不产生本任务DDL或隐式回填。

事实运行只识别两个有限schema profile：`BE009-B`对应0a2/71应用表；`BE009-BE010-JOINT`对应1b3/75应用表。两者共用mysql84_shanghai_v1事实存储合同，七张facts表的语义结构指纹F7必须与固定A候选及首个0a2采用证据一致。F7按表名排序，覆盖列名/方言类型/长度/精度/NULL/default、PK、命名unique/check/FK/index（各项稳定排序），对规范JSON做SHA-256；不比较SHOW CREATE的排版字节，也不把BE010新增四表计入F7。精确F7值由A的实际DDL/Model交付冻结、B独立核验，不在本PM阶段虚构。

BE010另批升级至1b3后，部署责任人在其获批窗口显式运行第12节现有adopt命令的`--revalidate-schema-only` plan/apply模式：核对live只有一个revision且精确为1b3、应用表集合75、F7不变、DB上海时间和原storageEpoch；以原adoptionId/revision作CAS，只刷新stream_state的schemaProfile/verifiedSchemaRevision/F7/采用凭据时间及批准引用。**不重新选择source，不改storageEpoch/sourceEpoch、binding、latest/raw/proof、游标HMAC key、TTL或数据**，不执行迁移/DDL/stamp。API只在live revision与该已核验凭据一致时接收/读取；未完成显式再核验暂503 not_ready，完成后facts可在1b3正常运行，不能硬钉0a2永久拒绝已知后继。

1b3联合证据须包含批准/前后revision、七表F7一致、应用表集合（排除alembic_version）、原storageEpoch/来源及有限proof不变、旧事实回执恢复和三路正常行为；它由BE010后续联合运行gate提供，不把BE009独立B变成执行BE010迁移的授权。任一未知head/多head/未知应用表/七表漂移仍拒绝，不自动放宽范围、选择新head或stamp；没有通用版本兼容平台。

本migration upgrade仅建七张表/约束，不seed、不新建管理员、不改数据库时区、不移旧数据。downgrade只在本七表全空且未采用时可执行；存在原值、proof、binding或state即拒绝，防止删除可靠确认。默认回退关闭PLC_FACTS_ENABLED，保留七表和所有已接受证明；任何真实downgrade/清理仍须独立运行授权。

## 10. R09：能证明提交安全的history游标

### 10.1 发布算法及证明义务

全部事实写入、source adopt、proof物理删除都先对`stream_state(id=1)`执行SELECT FOR UPDATE；原材料解析/hash在锁外。**发布位置只在锁内分配**：含新片的事务取highSerial+1，本批新片按(instanceId,sampleId,part)稳定排序分ordinal=1..N；receipt/feed与raw/latest/cycle/batch结果一同commit，highSerial同事务更新。拒绝、纯重放无新feed位置；raw自增ID仅内部定位。

不变量：持锁事务T1未commit/rollback前，T2不能取得较高发布serial；T1 commit则H及其全部part同时可见，rollback则未发布serial无效且可重用。任何读看到持久H，就不会以后再出现serial≤H的新事实。T2可以先解析/先进入请求，甚至别的表先分配过ID，均不得在拿门闩前持久分配发布位置。因此读游标推进到H不会越过晚commit的T1；没有用max(raw.id)、sourceSeq或观察/接收时间替代证明。

读事务使用同一个一致性snapshot读取H和≤H的receipt/feed，并以当前读依赖退出完成才响应；不在RR旧snapshot里先读H再用另一个事务读取rows。验证必须真实阻塞T1于commit前、让T2及reader并发，分别覆盖T1 commit/rollback/断线、较小raw ID晚提交和历史补传。只有客户端单在途或fake session测试不能满足B05。

### 10.2 mode=changes

必填mode=changes/plcId；可选instanceId/sourceGeneration/dbNumber/groupId/pointId、limit。sourceSeq不作为筛选下界；禁止from/to/pageCursor/view=original。首次必须`start=earliest`或`start=tail`，其后cursor；两者不能并用，不默认偷偷从尾。earliest从仍有proof的最早安全位置起，可能收到明确expired gap；tail返回显式baseline=explicit_tail、omittedThrough=H，调用方自行记录接受范围。

按(commitSerial,ordinal)扫描，最多2000个位置；匹配且仍有效的片返回`kind=fact`及实际point筛选后的规范投影、source/manifest状态、contentDigest/source SHA/projectionDigest；已到期匹配片返回`kind=gap,reason=raw_expired`及来源/ID/原时间区间/expiredAt，不含值/原文。未匹配过滤不是gap。返回nextCursor指向**最后检查过的安全位置**，若已扫到H可指向(H,该serial末ordinal)；不能指向未扫描的更高匹配项。页内原子位置不得跳过尚未返回的超字节项；停止于前一完整item，该项下页再读。

hasMore只表示本snapshot H内还有扫描位置；空页可能因过滤/预算，必须标scanBudgetReached和scannedThrough；不是源序连续、整轮齐全、无在途事务或业务已处理证明。新到10:20但原observedAt=10:05的补传分配更高serial，后续页必能看到。完整轮状态、最大已见sourceSeq和接收cursor分开，不宣称完整源前缀；有状态算法自行处理迟到/缺片。

游标为base64url(canonical payload).base64url(HMAC-SHA256)，绑定profile/contract/mode、storageEpoch、PLC scope/全部规范过滤hash、after位置、issuedAt/expiresAt；24h有效，每次合法响应签发新24h token。r1只配置一个key，不保留旧key；轮换/重启采用新key后旧cursor即使未满24h也因MAC不符返回422 invalid_request并requiresResync=true（不能区分旧key与伪MAC），明确选择新baseline，不静默跳尾。第7节父拒绝token由持久原凭据核验，继续其原120天恢复窗，不受本游标key轮换影响。token完整性不是客户端认证。

proof只允许按**完整serial前缀**删除，且前缀每个proof均已满120天；同锁保存被删前缀的末位置(proofFloorSerial,proofFloorOrdinal)，初始(0,0)。cursor的after位置小于该floor才410 cursor_gap，等于floor可安全从后续第一项继续；不能因最后serial相同而漏掉未消费ordinal。错误返回丢失的serial/ordinal区间、earliestRecoverableCursor/范围及requiresResync=true。TTL到期410 cursor_expired，模式/过滤/epoch/合同不符422 cursor_mismatch，畸形/伪MAC422 invalid_request；都不静默跳尾。新baseline要调用方明确start选择，保留已处理/已业务确认身份，不为重取输入重造业务event。

### 10.3 mode=range 与latest

range必填plcId/from/to（有offset，规范上海9位，from<to），只按**每点原observedAt**匹配半开[from,to)，可加上述过滤、limit、pageCursor；不能传changes cursor/start。排序固定(commitSerial,ordinal,pointId UTF-8)，是提交稳定序，不冒称源时间顺序；需要时间图由消费者按原时间解释。第一页冻结snapshotHighSerial=H，后页≤H；新提交不混进这个range分页。pageCursor绑定过滤/from/to/H/last位置/epoch，15分钟。记录级筛选只投影匹配points，完整contentDigest与投影digest分开。

range对匹配的过期原样本返回显式gap，而非伪完整空结果；无法恢复的旧proof前缀用coverage.unknownBeforeSerial与complete=false说明。每页用当前DB asOf重新检查expiry，即使页游标仍有效也不保留旧页的读权，物理清理/过期不能因snapshot续期。range页游标过期/材料缺失返回明确410及恢复范围，不能拿它当持续changes进度。

latest必填plcId；可选dbNumber/groupId/pointId/limit/pageCursor，按(DB,pointId UTF-8)聚合。只返回有效current definition、截至asOf未到期的最近PointFact（含bad），每点带原source身份/seq/config/definitionDigest/sample/part/cycle、observedAt/expiresAt；directory为同批结果的派生定义，不另存无值目录。最新页不是历史快照，分页token绑定bindingRevision，30秒有效；中途binding变更明确409 binding_conflict，调用方重查，不能把多页当一个同步现场帧。没有结果为items=[]，不补历史旧好值。

三种读成功统一code/message/data。共同必填contractVersion/digestProfile/asOf/mode/items/hasMore/coverage；changes必填nextCursor/snapshotHighSerial/scannedThrough/scanBudgetReached/baseline；range必填nextPageCursor/snapshotHighSerial/scannedThrough/scanBudgetReached；latest必填nextPageCursor/bindingRevision。已无后续页的nextPageCursor为null；changes即使hasMore=false也返回可继续轮询的nextCursor。未知字段/额外日期筛选不允许静默忽略。limit对history数part item，对latest数点（然后按DB聚合），不是聚合DB数。所有Map数据键保持原样。

| 读item/公共对象 | 精确字段与含义 |
| --- | --- |
| position/scannedThrough | `{commitSerial:string,ordinal:integer}`，ordinal为1..32；stream尚无记录时专用`{"commitSerial":"0","ordinal":0}`。每个serial的末ordinal可从该批稳定覆盖证明取得，不能任意造大值跳项。 |
| kind=fact | `{kind,position,sourceSha256,contentDigest,projectionDigest,projection,cycle}`。projection是第6节content规范对象加expiresAt，points可依query筛选；所有时间规范9位，static camelCase，数据point键原样。source/content摘要对应完整已确认原片，projectionDigest只覆盖实际projection对象。 |
| cycle | `{cycleId,cycleDigest,complete,qualityGood,receivedParts,expectedParts}`，是本次读取已持久状态；whole cycle未齐仍可读已确认片，不从最大seq推完整。 |
| kind=gap | `{kind,position,reason,instanceId,plcId,sourceGeneration,sourceSeq,cycleId,sampleId,part,pointIds,sourceSha256,contentDigest,observedFrom,observedTo,expiredAt}`；reason=raw_expired/raw_unavailable，观察边界为保守包含区间，不含value/definition/原文。range只要proof的点ID和观察区间可能相交就报告保守gap，不冒称知道已删除点的精确值/时刻。 |
| kind=original | 仅range view=original：`{kind,position,instanceId,plcId,sampleId,sourceSha256,payloadUtf8,sourceSampleComplete,expiresAt}`，可重复出现同一source sample的不同已确认part位置；诊断使用者按sampleId识别，不能当多个新样本。无context全文、无伪projectionDigest。 |
| latest DB item | `{plcId,dbNumber,points}`；每个PointFact保留完整definition/value/quality/reason/observedAt，另加expiresAt与source。source固定`{instanceId,sourceGeneration,sourceSeq,configRevision,definitionDigest,sampleId,part,cycleId,groupId}`。query asOf不进入任何原采集时间字段。 |
| coverage | `{complete:false,meaning:"receipt_feed_only_not_source_completeness",unknownBeforeSerial:string}`；明确不证明采集源连续或业务完成。历史proof前缀已清/未取得的范围不能用空items掩盖。 |

完整gap item示例（可作为changes/range的items成员；摘要仍为格式占位）：

```json
{"kind":"gap","position":{"commitSerial":"1","ordinal":1},"reason":"raw_expired","instanceId":"daa-demo","plcId":"plc-demo","sourceGeneration":"generation-demo","sourceSeq":"1","cycleId":"cycle-demo","sampleId":"sample-demo","part":1,"pointIds":["point_x"],"sourceSha256":"sha256:0000000000000000000000000000000000000000000000000000000000000000","contentDigest":"sha256:1111111111111111111111111111111111111111111111111111111111111111","observedFrom":"2026-11-04T10:00:00.123000000+08:00","observedTo":"2026-11-04T10:00:00.123000000+08:00","expiredAt":"2027-02-04T10:00:00.123000000+08:00"}
```

```json
{"code":200,"message":"success","data":{"contractVersion":"plc-facts/v1","digestProfile":"pf-json/v1","asOf":"2026-11-04T10:00:02.000000+08:00","mode":"changes","items":[],"snapshotHighSerial":"19","scannedThrough":{"commitSerial":"19","ordinal":2},"nextCursor":"opaque-server-cursor","hasMore":false,"scanBudgetReached":false,"baseline":null,"coverage":{"complete":false,"meaning":"receipt_feed_only_not_source_completeness","unknownBeforeSerial":"0"}}}
```

非空changes完整样例（point_x等数据键保持原样；projectionDigest覆盖projection本身）：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v1",
    "digestProfile": "pf-json/v1",
    "asOf": "2026-11-04T10:00:02.000000+08:00",
    "mode": "changes",
    "items": [
      {
        "kind": "fact",
        "position": {
          "commitSerial": "1",
          "ordinal": 1
        },
        "contentDigest": "sha256:93b60f03748d5e780ef326856dfca77e60c8be29a39fc3af56fae083e606b877",
        "sourceSha256": "sha256:4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2",
        "projectionDigest": "sha256:b6b7bb6c66ce92107e76841cfdb5637d8682314f08094e5d77b6416794936de0",
        "projection": {
          "sampleId": "sample-demo",
          "cycleId": "cycle-demo",
          "instanceId": "daa-demo",
          "plcId": "plc-demo",
          "sourceGeneration": "generation-demo",
          "sourceSeq": "1",
          "groupId": "group-demo",
          "dbNumber": 1,
          "origin": "s7",
          "startedAt": "2026-11-04T10:00:00.100000000+08:00",
          "finishedAt": "2026-11-04T10:00:00.200000000+08:00",
          "savedAt": "2026-11-04T10:00:00.201000000+08:00",
          "points": {
            "point_x": {
              "definition": {
                "id": "point_x",
                "plcId": "plc-demo",
                "dbId": "db-demo",
                "sourcePath": "炉温.当前值",
                "name": "DB1_temperature_Int",
                "nameMode": "manual",
                "dataType": "INT",
                "comment": "",
                "enabled": true,
                "groupId": "group-demo",
                "address": {
                  "offset": 0,
                  "bit": null,
                  "confirmed": true,
                  "origin": "source",
                  "reason": ""
                }
              },
              "value": 202,
              "quality": "good",
              "reason": null,
              "observedAt": "2026-11-04T10:00:00.123000000+08:00"
            }
          },
          "configRevision": "config-demo",
          "sourceSha256": "sha256:4501fbf86f8cbdee5489be8a1a99f16ea3cdcca4fe3d6ae146eb8a7e8b4b1ca2",
          "part": 1,
          "parts": 1,
          "expiresAt": "2027-02-04T10:00:00.123000000+08:00"
        },
        "cycle": {
          "cycleId": "cycle-demo",
          "cycleDigest": "sha256:be762e20d082fc2519c10bb2617588c973f6da2be2a765e85d13115c66d5dfb7",
          "complete": true,
          "qualityGood": true,
          "receivedParts": 1,
          "expectedParts": 1
        }
      }
    ],
    "snapshotHighSerial": "1",
    "scannedThrough": {
      "commitSerial": "1",
      "ordinal": 1
    },
    "nextCursor": "opaque-server-cursor",
    "hasMore": false,
    "scanBudgetReached": false,
    "baseline": null,
    "coverage": {
      "complete": false,
      "meaning": "receipt_feed_only_not_source_completeness",
      "unknownBeforeSerial": "0"
    }
  }
}
```

## 11. R10：三自然月、原文防泄漏与有限物理清理

retentionMonths默认3，运行采用可选1或2，不得>3；由stream_state采用参数固定，不能每请求传入或为重复续期。每点截止为**原observedAt上海时间+N自然月**，目标月无该日则月末同墙上时刻与原纳秒；达到截止不可有效读。不是90天，不以保存/上传/查询/ACK或其他点新值更新。

| 原observedAt | N=3截止 |
| --- | --- |
| 2026-01-31T12:00:00.123456789+08:00 | 2026-04-30T12:00:00.123456789+08:00 |
| 2023-11-30T06:00:00.000000000+08:00 | 2024-02-29T06:00:00.000000000+08:00 |
| 2024-11-30T06:00:00.000000000+08:00 | 2025-02-28T06:00:00.000000000+08:00 |

整份raw payload含多点时，raw及其历史投影均按**全部原成员最早截止**保守到期；不能只删返回点后仍通过payloadUtf8读到过期值。latest复制的单点独立按自身截止，不因raw保守到期提前改成其他值。cycle原manifest/context原文按cycle.startedAt+N月保守到期（不晚于其任何点截止），只保有限无值完整性摘要。history原文视图仅range可选`view=original`，必须无point/group过滤、sourceSampleComplete且整个payload未到期；仅选择全部点观察时间均包含于[from,to)的完整原样本，不能把边界外点伪装成已过滤投影。返回payloadUtf8/sourceSha256，始终不返回context全文。默认view=projection、changes与latest只返回投影，query摘要不能冒称原SHA。

所有读都执行expiry guard，即使物理清理停止仍不可读取已到期原值；有proof的重复可恢复历史摘要，但创建raw/latest和延长expiry均禁止。证明消失则明确unknown/expired，不用“以前应收到过”确认。重新提交原sourceSeq/observedAt不绕过；原身份更换seq/时间属改内容，客户端禁止，有限证明期内409。120天以外不能声称无限身份冲突检测，真实旧观察仍无条件过期。

物理清理由**部署责任人显式安排的一次性维护CLI tick**驱动，推荐调度频率60秒；本任务实现命令与合同，不创建OS调度、daemon、lifespan线程或Worker，不利用普通请求偷偷清表/DDL。运行频率及部署启用另批。每次tick：锁stream_state（等待≤250ms，不抢占正常写）→DB当前时刻→每事务最多删除/清空200行或2MiB原文、最多100ms持锁→commit；整次最多10事务、2000行/20MiB、2s，先清raw/过期latest/原cycle文本，再清已到期batch proof与完整serial前缀sample/cycle最小proof，精确减少同锁配额计数。不做OPTIMIZE、VACUUM、重建表、备份/副本清除或全库清理。配额不能通过删除尚有效proof或重置计数绕过，崩溃/重试验证计数与实际owner记录一致。

失败rollback当小批、非零exit并JSON Lines报告，下一次同条件重入；不延长逻辑读窗，不绕过锁。连续3次失败/3分钟未成功，status报告cleanup_degraded及最老过期年龄；超过24小时仍有可清原文属于物理清理SLA违约，要求运维处理/调整预算或停准入，不得宣称已及时销毁。**SLA推荐为运行健康、每分钟调度且到期量不超过每分钟20MiB/2000行的已验证预算下，24小时内清除应用主库过期原值**；B用受控积压/故障验证。超载不能靠静默加长raw保留解决，未来容量改版需重新审阅；不承诺介质瞬间擦除、备份或DB页空间立即回收。

source bindings/control仅有界准入/游标状态，无原值；120天proof不永久复制payload/context/definition。raw/latest/proof清理无业务/BE010/outbox FK或调用，绝不级联业务永久记录、SMA未完成输出或DAA本地待确认材料。事实ACK、SMA接收cursor、处理checkpoint、业务ACK分别拥有，保留永久业务值由BE010/目标模块负责。

## 12. R11：维护入口、运行gate与日志

`backend/scripts/plc_facts_maintenance/main.py`裸执行和`--help`只显示帮助，必须在加载settings/DB之前退出；无默认输入、默认目标或隐式seed。子命令固定`status`、`adopt --plan`、`adopt --apply`、`cleanup --plan`、`cleanup --apply`；只进入本owner的sync Service。status/plan对库的只读访问也须G-B具体目标批准；当前不执行。

apply要求显式目标alias/schema、预期schemaRevision/storageEpoch、任务批准操作标识、环境开关`PLC_FACTS_MAINTENANCE_ENABLED`（工具专用.env.example=False）、精确确认参数；scope不是权限平台。普通adopt只插控制单例/有限source binding及第8节必要latest资格变化，须expectedBindingRevision CAS、context文件明确路径/ SHA、旧代次截止/新基线；`adopt --revalidate-schema-only --plan/--apply`仅按第9节已知0a2/1b3规则核验/刷新控制行采用凭据，禁止与source切换参数混用。二者都不执行Alembic、seed或业务迁移。工具配置优先级CLI > OS env > 工具.env > backend.env > 安全默认，凭据不输出。首次adopt空目标/非MySQL/未知或不匹配revision/未知时间拒绝，不create_all/stamp。

数据库时间采用凭据记录版本、目标别名、schemaProfile/verifiedSchemaRevision/七表F7、DB现在/UTC差、retentionMonths、storageEpoch、binding摘要、确认人/批准引用及真实命令结果；不把凭据保存为代码常量或真实配置提交。schema再核验也须记录原/新采用引用与真实结果，不能由普通请求隐式更新凭据。CLI最终默认JSON Lines stdout（start/dry-run/commit/failed/complete及汇总），只有显式--output-log写文件，不发信、不挂调度。错误脱敏、失败非零；仅绑定当前owner表，不支持任意table/query。

API复用现有日志设施，不新增Core logger：稳定events `plc_facts_batch_committed/replayed/rejected/commit_unknown`、`plc_facts_binding_adopted`、`plc_facts_cleanup_completed/failed/degraded`、`plc_facts_cursor_gap`；记录受控instance/batch/PLC、digest、计数/位置、状态/错误/耗时、实际改变范围。无每点值、完整body/context/manifest、URL凭据、token/HMAC key、SQL/DSN；普通轮询无逐点噪音。API stdout及已有持久JSON Lines logs保持，CLI遵脚本证据规则。日志失败不能把已提交事务改称回滚，也不能因日志写成功产生ACK。

## 13. R12：A/B验收标准与B01–B08映射

当前下面均为**未来要求，未运行/未判通过**。A源码替身/静态SQL不能替代B真实MySQL事务；B没有独立运行批准时整体记录qa_blocked或明确A-only verdict，不授完整provider-ready。

| AC | A需证内容 | B另批后需证内容 | AW008 |
| --- | --- | --- | --- |
| AC01 三路/合同 | 正常composition三路匿名/typed输入输出，完整200/403/409/410/413/415/422/429/503/500失败schema，全部ref可解析；Decimal机器schema只number，point键原样，所有例子/生成产物一致 | 无凭据有效scope真实API→七表→查询/回执读回，完整status/content-type/body/ID/digest/time和副作用核对 | B01/B08 |
| AC02 原材料/严格值 | 原文SHA、v2全字段/manifest/reads/context/definitions映射，支持类型边界、bad/null/reason/0、深度/数量/字节/UTF8/重复key/未知字段/超精度拒绝；独立向量而非同实现自证 | UTF8/BLOB数字原貌及9位时间比较精度，非法整批无部分事实；原文格式冲突可恢复；真实大小写/Unicode精确键 | B01/B03 |
| AC03 原子回执 | create/duplicate/historical/rejected/unknown/父token各结构与优先级；完整依赖退出send顺序，DEBUG脱敏，default-off/noDB依赖拒绝 | raw/latest/cycle/feed/batch同事务，flush/commit/rollback/close/发送前故障，已提交丢回执重放；unknown不假rollback，原ID不增raw | B03 |
| AC04 固定片/混合批 | 多PLC同DB/多DB/多组、完整manifest缺片、固定贪心分片、bad成员也齐全；退休派生子集验证 | 全批拒绝无新事实+可靠拒绝token、旧已确认proof不否认、unknown父禁止派生；HMAC轮换/重启后同POST仍恢复原父token并可在原120天内派生，篡改/缺失/到期proof拒绝；不同PLC合法后续可前进；完成计数不假ACK | B03/B04 |
| AC05 latest/定义 | 原子按点规则反例、source/binding CAS、有效当前/历史区分、未变定义保留/变更清资格、定义集摘要独立向量 | 1005后1001/同点并发、同DB不同组独立、另一点1001不丢、等seq异值409、新bad替代旧good、移组/停用/代次切换/旧代次raw-only及CAS竞争；旧generation1005切新generation1成功且切换后旧值不可查；同generation定义未变而只换context/revision，原有效值仍可查 | B04 |
| AC06 safe cursor | 独立算法推演不变量、签名/filter/epoch绑定、24h/15min/30s、空页/扫描预算/重页/晚观察时间与投影摘要 | 两独立Session真实T1先分配rawID后延迟commit，T2/reader不能越过；T1 rollback/断线；新的晚历史下页可见；游标过窗/删除前缀明确410不漏报 | B05 |
| AC07 保留/精度 | 三自然月非90天、月末闰年/纳秒、原payload最早成员与latest独立、未来/时钟倒退/可短不可长，proof无值120天不续 | 截止前/等于/后读取，混合成员原文无泄漏、物理未删仍不可读、历史ACK不复活、proof超窗真实gap、宿主TZ改变DB上海时钟不变义 | B06 |
| AC08 清理 | CLI裸帮助无加载/副作用、显式plan/apply、预算/锁/非零失败、无Worker/DDL/seed，日志脱敏 | 60s受控tick/中断恢复/并发正常写；字节/行配额与计数在commit/rollback/重复后准确，满容量可恢复旧ACK且不删有效证明；每事务/每tick预算、3失败降级、超24h告警，原值/最小proof按次序删除，非owner行/业务/outbox不变 | B06/B07 |
| AC09 schema/链 | 唯一0a2接f6，七表静态DDL/Model约束与metadata75/pending4口径，有限0a2/1b3 profile/F7/凭据/CAS规则；旧六migration字节不变 | BE009独立B获批空库只显式到0a2，应用71表（排除alembic_version）、带合成旧64应用表升级前后ID/值/精度/hash一致；pending4不存在为预期；非空downgrade拒绝、空且未采用可回。1b3/75联合proof由BE010另批gate提供，F7/epoch/原proof不变并再核验后facts可运行；未知head/漂移拒绝 | B02/B07 |
| AC10 旧边界 | 旧monitor受保护GET、旧八POST/权限及Projection标量输入源码指纹和相关no_db回归；无旧表writer或Core默认改变 | 相同获批目标合成旧CA/Projection/业务夹具的原接口/源不受新表/开关/清理影响；不运行真实CA/PLC，不对同来源双写 | B02 |
| AC11 准入/可靠故障 | 关闭/空/越界403，合格但未adopt/key/profile/时间不ready503，module关闭404；错误失败不暴露敏感材料；无认证/伪actor | 新旧source冲突、并发首次批/同异内容/首片/父proof、锁timeout/负载429，数据库是最终裁定；不改全局隔离级别 | B01/B03/B07 |
| AC12 真实交付 | 相关no_db/compile/模块准入/文档链接/JSON/diff检查命令退出码，冻结旧suite失败准确归因，不削断言；正式交付树/副本一致 | 独立fresh Verification复现A和获批B，固定目标/revision/资源/清理；B08清单齐全，Owner接受与部署/DAA联调分gate | B07/B08 |

建议A命令由Development在tasks固定完整guarded argv：`uv run --offline --frozen --no-sync python -m compileall`仅相关源码；`uv run --offline --frozen --no-sync pytest -m no_db`只运行九个本任务整文件、模块准入和必要旧认证/Projection相关文件，所有测试显式basetemp、拒绝socket/SQLite/DBAPI连接。原样本/业务静态DDL用编译而非执行。不得默认pytest全套触发共享清库conftest；不重复DAA阶段B、BE010 A0整套220/437/88或现场采集。旧profile含固定表/配置数量或迁移head的失败保持并注明entry/本轮差别，新命名profile不能把历史失败覆写为全绿。

B脚本只消费另批合成MySQL8.4.6目标，测试独立Session/真实commit/同库查询，禁用业务mock和Projection runner，隔离volume/fixture；必须先固定运行资源/账号/schema/端口/镜像与清理动作，不能凭本r1直接选择本机服务。B不接受SQLite近似，也不恢复Celery/Redis/Python Worker。若A有新实质修改导致B候选变化，冻结新handoff并由新的fresh QA消费。

## 14. R13：交接清单、跨任务细化与风险

B08 provider交付至少含：本spec/批准Revision、源码工作树与差异/关键hash、Model/迁移revision及schema/metadata/profile、三路OpenAPI/schema/vector SHA、sourceProfile逐字段映射、真实请求与稳定成功/拒绝/unknown/过期样例、source首次采用/代次/定义规则、固定限额/时间/保留/清理及游标规则、A/B命令/结果/限制、可供未来DAA使用的合成数据/地址占位、部署/当前listener状态及独立QA/Owner状态。不得把本地mock、源码存在或200状态单独称后端就绪。

对AW008/demand-r1的细化是本r1审阅内容，不偷偷修改旧文件：选择独立七表、原v2文本作为唯一points载体、保留sampleId并增加part子身份、9位事实精度、4MiB事实预算、受控维护选择source/config、数据库门闩发布序、120天最小证明及同窗父拒绝token、明确gap以及一次性维护清理。候选JSON只是语义例，本r1才提出正式provider编码；如Owner认为其中改变已批共同语义，先修订对应spec并精确批准，不能由实现自行声称兼容通过。

与BE010 r2无循环依赖：facts先独立到0a2/71表，BE010后接1b3/四表及其有界旧UTC→上海兼容/业务接线；common/integration和业务v1保持其唯一归属。事实DATETIME(6)+ns不是业务DATETIME(3)的整改，双方只在后续SMA sourceRefs保留事实时间。事实不写/读取八类业务、不运行旧时间数据迁移；BE010不承担raw清理。未来可分别批准源码，迁移应用按链串行。

主要风险及控制：匿名来源可冒用（Owner明确接受准入范围而非伪认证）；全局门闩限制写吞吐（首版选择可证明安全而有界，B不达预算时回PM）；原配置大于预算可拒绝（不能重写历史适配）；source adopt属于运维写（单独G-B与CAS）；原文保守到期可能早于某些点（latest仍按点，历史明确gap）；有限proof无法无限恢复（120天内稳定、超窗明确缺口）；无自动物理清理调度即无SLA运行证明（默认关闭、另批调度）；共享脏树并发（按自有基线/段审计，不覆盖他人）。

回退优先关闭新事实准入并保留已接受raw/最小证明/来源选择，旧monitor/CA/Projection路径按其原合同保留。不能以回退删已确认事实、清旧profile、解除认证或逆转未经调查的历史时间；物理回滚/部署/数据恢复另批。临时检查产物归本PM私有目录，重要结论在本文持久化；不把临时路径当唯一证据，不删主协调before、AW008或BE010证据。

## 15. 当前handoff、skill与真实批准历史

本spec使用aiis（BLUEPRINT/CONTRACTS）、project-governance、backend-arch（RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING/DATA_GOVERNANCE）限定范围，维护CLI按backend-script-tooling。后续Development/Verification按相同面使用这些skill；真实结构索引用code-document-indexer，若将错误展示到UI再由对应UI任务用i18n-workflow。B确实采用Docker时才加载Docker专项；Rust/Tauri/PLC采集均另交对应角色，不由PM执行。本profile为contract_only，bundle/串行handoff/diff审计是合同控制，不宣称平台ACL或强制路由。

| 日期/Revision | 真实事件/效力 |
| --- | --- |
| 2026-11-04 r1 | Owner同意后端优先、DAA后做，授权具体规格整理；实际PM起草本draft。没有对本正文的精确范围批准、Development、独立QA或最终验收。 |
| 2026-11-04 r1 draft澄清 | 主协调草案复核后，PM明确sourceEpoch隔离代次与同来源未变定义保留旧latest；明确父拒绝凭据持久恢复不依赖当前游标HMAC key，并补对应未来AC。仍为未批准draft，不新增接口/调度器或实施事实。 |
| 2026-11-04 r1 draft联合profile澄清 | 最后复核补充已知0a2/1b3的F7不变与显式schema再核验规则，应用表数排除alembic_version；BE009独立B仍只到0a2，1b3运行另受BE010联合gate约束。仍未批准，不执行任何迁移或采用。 |

主协调下一步提交Human Owner审阅的**精确范围**：ARCH-BE-009 r1的A源码/no-DB、七表迁移源码与唯一接链、三路匿名provider合同及本文风险/限额/来源/回执/游标/保留/维护算法。**B数据库/Docker/维护运行、真实配置、DAA开发和联调、真实PLC、部署和发布继续不授权。** Owner可明确批准A，随后实际Development创建tasks；不能把“开始”登记为owner_approved，不能自动接续B。

AW008文档最终验收仍pending；本spec起草不以其pending阻止整理，也不补造终验。如后续实施批准需要接受本provider对共同语义的具体选择，由Owner对本精确r1明确决定；不以AW008文档QA替代软件批准。BE010 A0当前独立通过及其Owner验收pending继续保持。

PM交接仅包含本文、静态JSON/链接/空白/范围自检与最终文件SHA（由外部handoff固定，避免自引用）。没有运行项目测试/构建/监听/网络API/DB/SQLite/Alembic current/Docker，没有读取真实.env或profile，没有安装依赖/Git写入，也没有启动Development长任务notifier或外发邮件。本轮不预建tasks/checklist/README/status/evidence文件。

### PM文档自检（不是Development或独立QA）

`python3 -B /private/tmp/arch-backend-api-specs-as6r4aey/be009-pm/check_spec.py`实际退出0：严格解析7个JSON围栏及3份内嵌原文JSON，31项独立原SHA/规范摘要/定义集/字段关联/数值与offset/月末关系均true；16张Markdown表格、8围栏、9本地链接、metadata及全部行末空白无错。完整请求及成功/非空读取中的摘要为真实stdlib独立预期，错误/gap的格式占位有明确说明。脚本没有导入或运行项目。

`git diff --check -- plans/ARCH-BE-009-backend-facts-integration/spec.md`实际退出0；新未跟踪文件的逐行空白由上述stdlib另查，不能只依赖Git忽略未跟踪正文。task目录仅spec，无提前角色文件。相对主协调1050公共源码hash，1048项相同，两项变化仅backend/PLAN双语并行索引；不据共享文件变化声称本PM修改或回退了它们。AW008完整bundle及双语demand保持原hash；BE010 spec由同伴PM修订为r2，旧批准/QA仍按其原证据保留，本PM不改写。

私有合成fixture、两份stdlib文档helper与报告仅在上述be009-pm目录，仍供主协调/Owner审阅；没有应用、数据库、监听、构建、临时源码或worktree资源。本文与外部最终SHA是持久审阅入口；自检只证明文档结构与这些例子，不证明真实事务、DDL、时间采用、清理SLA、软件QA或Owner通过。

### r1 精确批准收据与A源码交接（2026-11-04）

Human Owner明确批准原话：

> 批准 ARCH-BE-009 r1 和 ARCH-BE-010 r2，按 STD 进入 A 源码阶段开发。数据库、Docker 和实际数据迁移先不执行，等源码检查通过后再确认；DAA 暂不改动。

本任务对应的获批draft SHA-256为 `157932dfd6432b972ed73c327ba47bffd4b7c43f32c6e68f772c5cbef458eb86`。本次只登记真实精确批准：Revision仍为r1，R01–R13、allowlist、七表/接链、A/B边界、风险和AC不变。上文draft/待审阅/未批准表述保留为该获批正文的起草历史；当前效力以顶部元数据、本收据及Owner明确阶段限制为准。除Status/Handoff两行外，获批draft原字节前缀完整保留，可恢复上述SHA核对，不重写原文制造新的批准范围。

当前仅交实际Development按STD进入第2节A源码/no-DB阶段，并创建所属tasks、记录真实实施和源码检查；七表迁移源文件属于获批源码范围，**不授权执行迁移或任何数据库操作（含SQLite）、Docker、实际数据迁移、维护采用/B验证或DAA改动**。这些动作须等待源码检查通过后另行具体确认；不因本次A批准自动接续。DAA原配置/历史/profile、实联、真实PLC、部署和发布的保护边界保持。

本次批准不是Development完成、独立QA或Human Owner最终验收，也不是AW008文档终验或BE010 A0最终验收。本PM只更新本spec，不创建tasks/checklist、不修改其他文件，不运行项目、测试、数据库、Docker或设备动作；后续按精确handoff进行Development与fresh-context Verification。
