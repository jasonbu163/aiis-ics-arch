Task ID: ARCH-AW-008
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development；Human Owner 已于 2026-11-04 精确批准 ARCH-AW-008 r1，按第3节完成文档修订与交接；fresh-context Verification 及 Owner 文档终验待后续，不含软件实施或实际联调
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 阶段 C 匿名事实集成、可靠回执与消费保留合同的文档定稿及后续实施边界
Owner: Automation World
Acceptance Chain Reference: 本 spec 第 12 节；PM -> Human Owner 精确范围批准 -> Development 文档交付 -> fresh-context Verification -> Human Owner 文档最终验收
Related Task: ARCH-AW-003, ARCH-AW-007, DAA-007, ARCH-BE-003, ARCH-BE-006

# 阶段 C 跨端事实合同与设计同步

## 1. 目标、当前 gate 与决定来源

本任务将 DAA、Backend、SMA／其他消费者之间已经讨论的事实与业务边界整理为可审阅合同，并为后续两端软件任务确定范围、依赖和验收标准。**2026-11-03 仅起草本 spec；Human Owner 已于 2026-11-04 精确批准 r1，当前交接文档 Development，依第3节修订详细设计和共同合同文档。** 本任务的 Development 仅是文档实施，不包含代码、可执行 schema、DDL、数据库迁移、软件联调或部署。

2026-11-03，Human Owner 要求：

> 可以，先出 ARCH-AW-008 r1 spec，明确匿名集成接口、JSON 和可靠回执、latest 顺序、历史游标、三自然月保留及业务永久保存，并列清后端与 DAA 的实施范围、依赖和验收标准。先只出 spec，不改代码，已有 SQLite 配置和历史不动，批准后再修订详细设计。

上句是 2026-11-03 的 spec 起草授权，不是当时尚未形成正文的精确范围批准。2026-11-04 对本 r1 的真实精确批准记录见第12节；批准不代表文档已交付或核验已通过。文档 QA、文档终验、软件实现与阶段 C 联调验收分别记录。无 Parent Task ID；旧设计和阶段 B 的批准／QA／验收不转移给本任务。

本版需要固化的方向：

- DAA 持续采集并先存本地 SQLite，通过一个固定事实入口可靠批量上传；Backend 承担 raw/latest 和可靠读取，SMA 承担后续语义映射及业务投递。
- 新增机器集成通道本阶段匿名；前端展示／管理接口继续执行已有认证和权限分组。匿名接入仍执行严格数据合同、限额、幂等、顺序和保留校验。
- raw/latest 默认并最多保存三个自然月；已经业务 API 可靠确认的数据默认永久保存，具有独立业务值和追溯资料。
- 共同合同定稿后，Backend 和 DAA 可以分别立项并行开发；实际 HTTP 联调等待后端就绪。SMA 实现及全部业务写入接口不是 DAA 阶段 C 的前置。

## 2. 只读现状与设计差额

以下是 2026-11-03 的源码／文档核对依据，不代表本任务已实施新接口或实际数据库已采用对应 schema。

| 依据 | 已有事实及差额 |
| --- | --- |
| [根 PLAN](../../PLAN.zh-CN.md)、[DAA PLAN](../../automation-world/data-acquisition-agent/PLAN.zh-CN.md)、[DAA-007 验收](../../automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) | 阶段 B 已于 2026-10-30 在受控 DS 联调范围内验收。历史证据限制和来源未明事项继续跟踪；阶段 C、自动启动策略及真实现场工作未因此获批。 |
| [DAA README](../../automation-world/data-acquisition-agent/README.zh-CN.md)、[本地 IPC](../../automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs) | 普通 pnpm tauri dev 进入 SQLite 应用；采集／连接启动停止；uploadAvailable=false，产品没有可靠上传／ACK 链路。 |
| [本地 schema](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs)、[本地事实写入](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs) | 全轮事实、manifest、源序号和 pending 同事务提交，现行样本／manifest 为 v2；原持久字节和 SHA-256 是受保护材料。不能为新传输合同重写旧样本。 |
| [事实 Model](../../backend/app/monitor/models/monitor.py) | 已有 plc_db_block_raw_snapshots 与 plc_db_block_latest_snapshots；当前 latest 唯一键为 plc_key/db_number/group_name。缺少完整 DAA 样本去重、内容冲突及源顺序接收合同。 |
| [latest GET](../../backend/app/monitor/api/realtime.py)、[monitor 路由](../../backend/app/monitor/api/routes.py) | 已有带认证及 monitor 权限的实时查询，不能把其存在当成匿名事实集成接口或安全增量读取已完成。 |
| [旧 CA writer](../../automation-world/control-agent/src-tauri/src/infrastructure/database/repositories/mod.rs) | legacy 直库 raw 追加及 latest 更新属于冻结兼容链；不是 DAA HTTP 接收／可靠回执。不得恢复为本期实现捷径。 |
| [响应序列化](../../backend/common/response.py)、[Projection 输入](../../backend/projection/input_resolver.py) | 共享响应递归转换字典键；旧 Projection 读取 decoded_payload[point_name] 标量。稳定 pointId／sampleId 等字典键保护和新旧载荷兼容需要后续 Backend 实现。 |
| [温控 POST](../../backend/app/equipment/api/temperature_samples.py)、[输入字段](../../backend/app/equipment/schemas/temperature_sample_in.py)、[Service](../../backend/app/equipment/services/async_temperature_sample.py) | 当前业务 POST 有用户／权限／设备 scope，温控要求完整字段，Service 的幂等还包含 actor_user_id。新增匿名业务通道需要模块自有合同，不能去掉路由 guard 后伪造管理员复用。 |
| [SMA README](../../automation-world/semantic-mapping-agent/README.zh-CN.md)、[ARCH-AW-007 r2](../ARCH-AW-007-general-agent-fleet-roadmap/spec.md) | SMA 保留 TSS 派生 HTTP／Backend-held 配置基线，沿表格和工作台精简；本任务不把旧详细设计中的立即迁入本地 SQLite 当作新的实施前置。 |
| [现有 DAA 设计](../../docs/AIIS_DAA_Detailed_Design.md)、[SMA 设计](../../docs/AIIS_SMA_Detailed_Design.md) | 已有冻结身份、完整性、latest 和安全 feed 目标；部分“当前现状”仍是旧 YAML／旧壳快照，三自然月仍用 UTC 描述。批准后的文档需要与现行阶段 B 和上海时间合同对齐，并保留旧批准记录。 |

只检查仓库源码与文档；未读取真实 .env、SQLite/profile 内容，未启动程序、API、DS、PLC 或数据库。

## 3. 范围、精确 allowlist 与角色

### 3.1 起草历史及当前文档交接

2026-11-03 起草阶段，PM 仅新增本 spec，主协调只在根 PLAN 双语及根 plans/README 双语增加本任务 draft 索引；当时不创建 tasks.md/checklist.md，不修改详细设计、共同合同正文或软件任务。2026-11-04 精确批准后，PM 仅登记批准与当前交接，主协调机械同步真实状态；Development 下一阶段依第3.2节写入其文档范围及 tasks.md，新的 Verification 仍须等待 developer_handoff 后才创建 checklist.md。

### 3.2 精确 r1 批准后的文档范围

以下 **17 个精确文件**按 gate 和角色使用；列入表不表示当前允许修改，不继承其他任务的 allowlist。

| 精确路径 | 角色、时点及允许变化 |
| --- | --- |
| plans/ARCH-AW-008-stage-c-facts-contract/spec.md | PM／Human Owner；范围、修订与真实批准记录。 |
| plans/ARCH-AW-008-stage-c-facts-contract/tasks.md | 精确批准后 Development 创建；仅文档计划、实际差异、自检、交接和资源记录。 |
| plans/ARCH-AW-008-stage-c-facts-contract/checklist.md | developer_handoff 后新的 fresh-context Verification 创建；文档独立核验与 verdict，Human Owner 记录真实终验。 |
| docs/AIIS_DAA_Detailed_Design.md | 批准后 Development；更新真实基线、匿名事实上传、回执／顺序／游标／保留、UI 责任及阶段 C／后续边界。 |
| docs/AIIS_SMA_Detailed_Design.md | 批准后 Development；对齐事实读取、定义漂移、双进度、业务回执／永久保存、匿名集成和当前路线；不借机规定立即迁移 SMA 配置存储。 |
| docs/AIIS_AW_Runtime_Design.md | 批准后 Development；仅同步事实链路、两段确认、时间／保留和相关引用，保留 DS／CA 等未触及内容。 |
| docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md | 批准后 Development；仅同步上述职责／数据生命周期及阶段边界，不扩展平台、连接器或中央管理范围。 |
| docs/README.md | 批准后 Development；仅本次四文档用途／合同入口摘要。 |
| docs/README.zh-CN.md | 批准后 Development；对应英文索引，语义对称。 |
| contracts/demands/automation-world-facts-integration.md | 批准后 Development 新增英文共同需求合同；Status: proposed，覆盖事实一写两读及业务投递责任，不宣称 provider 已接受／实现。 |
| contracts/demands/automation-world-facts-integration.zh-CN.md | 批准后 Development 新增中文对应合同；共享同一版本和语义。 |
| contracts/README.md | 批准后 Development；新增本 demand 的消费者／provider／proposed 状态行及正文链接。 |
| contracts/README.zh-CN.md | 批准后 Development；对应英文合同索引。 |
| PLAN.md | 主协调；仅本任务聚合状态、规格链接、最近真实 gate 与下一 gate。 |
| PLAN.zh-CN.md | 主协调；同一任务行中文对应。 |
| plans/README.md | 主协调；仅本任务 catalog 行，链接实际存在的角色文档。 |
| plans/README.zh-CN.md | 主协调；同一 catalog 行中文对应。 |

本任务采用 contracts/demands 层，因为当前只是跨端需求设计，不能替 Backend provider 发布已实现合同。未来 Backend 任务在自己的获批范围中形成 provider published 合同并与 OpenAPI／Pydantic／Model／Alembic 对齐；届时通过引用和版本关系解释替代，不长期维护两套互相冲突的正式 schema。接口路径在本任务中为明确候选，软件定稿与限额参数由后续 Backend 精确 spec 承接。

### 3.3 排除与保护

不修改代码、测试、依赖／锁文件、可执行 JSON schema／OpenAPI、SQL／Alembic、配置／env／YAML、SQLite、历史、业务表、其他任务 bundle、AGENTS、角色／workflow／skills、CODE_INDEX 或安装包。本任务不新建 ARCH-BE-009、DAA-008、SMA 或业务模块任务文件；这些 ID 仅为后续建议，起草时核对唯一性。

不启动工程、监听端口、运行项目测试、调用网络/API、操作 DS／真实 PLC／生产数据库、执行 Docker、现场切换、Git commit/push／发布或清理任务外资源。已有 SQLite 配置、历史、身份、原文／manifest／SHA-256、私有迁入记录和原联调 profile 全部保持。不批量回填旧任务或重标旧 QA／验收。

## 4. 编号需求：匿名接口与事实 JSON

### R01. 路由级匿名集成与已有权限边界

文档固定本阶段新增事实一写两读接口不要求登录、JWT、API Key 或角色授权。候选路径如下，均非现有可调用接口：

| 方法／候选路径 | 使用方与职责 | 当前设计认证 |
| --- | --- | --- |
| POST /api/v1/integration/plc-facts/batches | DAA；只写采集事实，允许同批多个 PLC／DB 的样本 | 无 |
| GET /api/v1/integration/plc-facts/latest | SMA／其他程序；查询最新点结果和派生点位目录 | 无 |
| GET /api/v1/integration/plc-facts/history | SMA／其他程序；时间段或安全游标模式读取历史 | 无 |
| POST /api/v1/integration/{module}/{resource} | 后续由模块拥有的机器业务写入入口；这里只给出合同模式 | 本阶段目标无认证，实际接口另批 |
| 各模块既有展示／管理及业务入口 | 现行消费者 | 保持各自既有认证、权限分组和业务合同 |

同一路由的认证规则不随 User-Agent、调用方自称 DAA/SMA 或前端页面切换。integration 是公开路由用途，不形成跨模块万能 SQL writer；API 薄适配、Service 校验和事务仍归相应模块。匿名接口不扩展到账号、权限、维护初始化、DDL 或设备控制。

producer／instance／PLC／sourceGeneration 是客户端声明，用于数据归属和顺序解释，不证明真实设备或调用者身份。可访问匿名写入接口的客户端具有提交／冒用来源声明的能力，是当前业务跑通阶段的明确取舍；不以本任务追加身份平台或隐式认证开关。后续安全升级须保持稳定事实身份与重试语义并独立定范围。

### R02. 单份自描述点位体、稳定身份与类型

文档统一样本、点结果、轮次及 HTTP 批次四种身份；sampleId 重试不变，pointId 为绑定主键，cycleId/manifest 证明完整轮，batchId 标识冻结投递。IP、DB 名、显示名及 name 不替代身份。sourceSeq 是同 PLC／同来源代次的持久源顺序，采用无精度损失的传输编码，示例用十进制字符串；跨 PLC 不比较。

points 以稳定 pointId 为键，每点包含定义、地址、PLC 类型、JSON 值、质量、原观察时间和可定位失败原因；类型／范围／有限浮点／缺值矩阵由 Backend 正式合同定稿。坏值不补零、不借旧成功值、不能省略预期失败成员。映射键在响应序列化、签名和目录中原样保留，字段 camelCase 转换不能改写数据身份。

沿用 DAA 已有 managed ASCII 技术命名，sourcePath 保留中文及原路径。未显式转换的 legacy 名称和历史按原定义无损传输；不能为上传强制重命名或重写旧样本。Backend 将这些值视为数据，不当作程序变量、SQL 标识符或动态字段执行。目录由已上报且有效的最新定义派生，不另存一份可编辑、永久无值目录。

### R03. 请求、完整性和摘要示例

批准后的文档至少包含：多 PLC 同 DB 不冲突、单 PLC 跨 DB 同轮拆成多个稳定包、不同组独立轮次、部分失败、拆批／固定片段和 manifest 不完整等示例。上传只引用本地已提交事实；同批不是跨 PLC 瞬时同步帧。

以下是**精简语义样例，非可调用 schema**；仅展示单个一包轮次。ID、摘要、字段编码、分片结构及版本字符串为占位，不承诺符合未来验证器。正式文档须提供与本地 v2/manifest 的逐字段对应及无损兼容方案，不把本例重新包装当作历史数据迁移。

~~~json
{
  "contractVersion": "plc-facts/v1",
  "batchId": "batch-demo-1",
  "instanceId": "daa-demo",
  "requestDigest": "illustrative-frozen-request-digest",
  "cycles": [
    {
      "plcId": "plc-a",
      "groupId": "fast",
      "cycleId": "cycle-a-142",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "manifest": [
        { "sampleId": "sample-a71", "dbNumber": 71, "part": 1, "parts": 1, "contentDigest": "illustrative-sample-digest" }
      ]
    }
  ],
  "samples": [
    {
      "sampleId": "sample-a71",
      "cycleId": "cycle-a-142",
      "plcId": "plc-a",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "fast",
      "configRevision": "config-a3",
      "dbNumber": 71,
      "points": {
        "point-a-temperature": {
          "name": "DB71_temperature_Int",
          "sourcePath": "temperature",
          "address": { "offset": 2, "bit": null, "length": 2 },
          "dataType": "INT",
          "value": 202,
          "quality": "good",
          "observedAt": "2026-11-03T10:00:00.123+08:00"
        }
      }
    }
  ]
}
~~~

摘要有三类责任：本地原样本／manifest 的原字节 SHA-256、正式传输规范化内容摘要、冻结请求覆盖摘要。不得混用或把重新缩进／解析再序列化的 JSON 声称为原字节。Backend 实施前须确定算法、字段包含／排除、时间／数值规范化、大小写与字符编码、排序和测试向量；本任务不选择实现库。若需携带原文，明确原字节表示及校验方式；若发送投影，分别标明投影身份／摘要与原样本关联，不能替换原文证据。

manifest 是应有成员及固定片摘要，不是本 HTTP 请求中碰巧出现的成员列表。确认一片／一个包不自动证明整轮完成。超限在冻结前有界拆批；冻结后不得原地增删成员、改 sampleId 或截断载荷。

## 5. 编号需求：可靠回执与 latest

### R04. 事务、可靠回执与本地确认

首版设计采用有界整批事务：合同／限额校验 -> 样本身份与内容去重 -> raw 新增或确认重复 -> latest 原子条件推进 -> 必要完整性／接收／安全 feed 记录 -> 持久提交 -> 返回回执。跨存储若不能同事务，Backend 必须提出等效可证明的接收账本方案再定稿，不能把易失入队写成全部完成。

回执必须绑定 contractVersion、batchId、请求内容摘要及每个确认样本／片身份和摘要，并区分 created、duplicate、未确认和历史确认。只有可靠提交范围可被确认。HTTP 200/202、发送完成、队列已接收或 UI 日志都不是 ACK。DAA 校验后短事务单调保存本地确认，成功后才显示已上报；本地提交失败保持原身份恢复。

下面仅示意两个成员均已可靠提交，未展示完整性证据；其 ID／摘要仍为语义占位。两个相同 batchId 的响应在可重放范围内须对应同一冻结内容，不应因重试重复增加 raw。

~~~json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v1",
    "batchId": "batch-demo-2",
    "requestDigest": "illustrative-request-digest-2",
    "status": "committed",
    "results": [
      { "sampleId": "sample-a71", "contentDigest": "illustrative-sample-digest", "outcome": "created" },
      { "sampleId": "sample-b71", "contentDigest": "illustrative-b71-digest", "outcome": "duplicate" }
    ]
  }
}
~~~

raw 接收、latest 推进、整轮完整接收、SMA 接收和业务入库是不同结果。可靠样本 ACK 可以发生在该点 latest 未推进、或该轮仍缺其他包时；响应须能表达这种区别，不给 DAA 一个最大序号冒充全部历史已确认。

### R05. 重复、冲突、过期、未知结果与冻结批次处置

| 情况 | Backend 合同要求 | DAA 后续动作 |
| --- | --- | --- |
| 同样本身份、同内容 | 可靠确认已存在，不新增 raw，不倒退 latest | 可按有效回执持久 ACK |
| 同样本／批次身份、不同内容 | 明确冲突，不覆盖旧事实；全批不得声称新提交 | 保留原材料，隔离需处理，不换 ID 掩盖冲突 |
| Backend 已提交但响应丢失，或本地 ACK 失败 | 可能已成功；相同冻结请求可恢复回执 | 按原 ID／内容重试，不先删除 |
| 未提交的过期事实 | 明确不可重试过期拒绝，不写入／复活 raw/latest | 需处理并保留证据，不当已上报清理 |
| 已到期但有有效历史提交证明 | 可重放明确的历史确认摘要，不恢复过期原值／目录 | 按正式历史确认范围记录，不能称当前值可读 |
| 数据库／网络提交结果未知 | 不假称未提交或成功；返回可重试／unknown 语义 | 原身份核实或重试 |
| 新批混合有效与过期／冲突成员 | 首版全批拒绝新提交，逐成员诊断不等于部分 ACK | 按定稿的退休／派生批次矩阵隔离，原冻结批次不原地改写 |

合同文档必须给出混合批次的状态矩阵：何时可以证明整批没有新增提交，如何保留已存在的旧证明，何时需先恢复未知结果，如何在原批有审计关联的前提下建立新派生批次并继续合法成员。重组不改原样本身份／内容，不因一个坏样本无限阻塞所有 PLC，也不能将拒绝变为确认。Backend／DAA 实施 spec 必须在编码前定稿该矩阵；本任务不实现退休机制。

以下三个示例分别对应 HTTP 409、410、503；正式业务码及结构由 Backend 定稿，文档要求机器可判断原因、重试性和真实持久边界。not_committed 仅说明该次拒绝没有新提交，不否认其他历史请求已经保存的事实；仅在能够证明此边界时使用。503 的 unknown 不能被客户端理解成已回滚。

~~~json
{
  "code": 409,
  "message": "conflict",
  "errorCode": "facts.sample_content_conflict",
  "data": { "batchId": "batch-conflict", "retryable": false, "persistence": "not_committed", "sampleIds": ["sample-a71"] }
}
~~~

~~~json
{
  "code": 410,
  "message": "expired",
  "errorCode": "facts.sample_expired",
  "data": { "batchId": "batch-expired", "retryable": false, "persistence": "not_committed", "sampleIds": ["sample-old"] }
}
~~~

~~~json
{
  "code": 503,
  "message": "temporarily_unavailable",
  "errorCode": "facts.commit_outcome_unknown",
  "data": { "batchId": "batch-unknown", "retryable": true, "persistence": "unknown" }
}
~~~

### R06. 逐点 latest、并发顺序与来源定义

保留 raw 追加历史和 latest 当前结果两类核心职责，**latest 语义按稳定 PLC／pointId 独立维护，查询再按 DB 聚合**。建议 Backend 采用逐点物理 latest；实际表名／粒度／索引／辅助账本及旧表兼容由其精确 spec 决定，不把“两个核心职责”承诺成数据库只允许两张表。

同一有效来源代次和有效定义下，仅更高 sourceSeq 的本点结果可以原子推进 latest。同 DB 的不同组更新各自点，不相互整包覆盖；某点的高序号不能使另一点合法较低序号被跳过。旧历史按当时定义追加，不回滚当前地址／类型／成员，不复活停用点。sourceGeneration/configRevision 等 opaque 字符串不能排序，HTTP／接收时间、可回拨采集时钟和请求发送顺序也不能替代源顺序。

来源切换需要明确旧代次截止、新代次基线和唯一有效当前来源的受控选择，正常重启／换周期／移组不清零序号。无认证时该选择是协议／配置约束，不是已验证设备所有权。未知／旧来源的 raw 接收资格与推进 latest 资格分开；Backend 任务须明确首次采用、冲突来源、代次替换、定义起效及并发 CAS／等效规则，不能从任意较新 UUID 或晚到 HTTP 自动授予接管。

### R07. 质量、停用与定义漂移

本版选择 latest 表示“最近结果”而非“最近好值”：合格新顺序的坏质量结果保留新观察时间／失败原因并显示缺值，旧好值若另作参考必须带旧身份／时间，不能冒充当前成功。质量和新鲜度分别判断；latest 可读不证明 PLC 在线或业务条件成立。

组移位仍保留 pointId；单包缺点不当删除。显式停用／退役／定义变化要有有效成员／定义声明，表达可随同一事实入口的受限元数据完成，正式编码由 Backend 合同决定。没有声明也没有新样本时只能报告陈旧／到期，不能承诺立即发现停用。停用声明不能为旧值续期或制造新测量。

SMA 的绑定签名包括定义和有效性，不包括值／质量／时间。地址、类型、名称或有效性变化只暂停受影响绑定等待确认，无关配置变化不全停；SMA 调整业务映射，不修改 DAA 的真实 PLC 地址。实际 PLC 程序变了但 DAA 仍报告旧定义的情况，不能单凭 JSON 自动证明检测成功。

## 6. 编号需求：历史读取、时间与保留

### R08. 一个 history 接口的两种模式

时间段模式按原采集时间筛选，明确上海时区、起止包含规则、过滤项、稳定排序、分页快照／边界和页游标。增量模式按 Backend 已可靠发布的提交位置读取，返回 stable nextCursor、hasMore、样本／来源／完整性信息；时间段页游标与持续增量 cursor 不混用，游标绑定模式、合同版本和过滤条件。

latest 用于当前状态和预览；逐样本计算、历史曲线和完整输入使用 history。SMA 在 10:20 才收到 10:05 的补传，仍应由增量模式读到；不能仅以上次最大采集时间作为下次起点。合法 JSON 的空页示例：

~~~json
{
  "code": 200,
  "message": "success",
  "data": {
    "mode": "changes",
    "items": [],
    "nextCursor": "opaque-server-cursor-example",
    "hasMore": false
  }
}
~~~

items 的正式结构和非空例子在文档交付中与 R02/R03 对齐；空页不是采集缺口、没有待提交事务或全部源序号已完整的证明。

### R09. 安全游标与缺口

Backend 必须证明 cursor 之前的可交付提交不会以后才出现；并发事务可能先分配较小自增 ID、后提交，未经证明的 max(raw.id)、最大 sourceSeq 或当前查询最大时间均不合格。选择提交有序发布、缺口感知或等效算法及其验证由 Backend 实施 spec 完成，本任务不选实现框架。

过滤后源序号自然跳号不等于丢失；完整轮／片段前缀和最大已见序号分别表达。断线补传可能使输入晚到或源顺序乱序，安全接收 cursor 不代表 SMA 处理 checkpoint；有状态窗口／历史算法仍须自己的完整性、迟到和 gap 策略。

cursor 超窗、过滤改变、合同变更或材料已删除时，应返回明确原因、可恢复范围和受影响缺口，给出显式重新建立基线／重同步流程；不能静默跳到尾部宣称无漏读。重同步不回滚已完成业务结果，也不能把已处理输入反复生成新的业务投递身份。

### R10. 上海时间与最多三个自然月

事实 API／新传输时间采用 Asia/Shanghai、带 +08:00 的 RFC 3339，保留所需原精度；UI 按项目统一 24 小时显示。区分点观察、轮次读取起止、本地保存、后端提交和查询时刻。未来异常时钟要按允许偏差明确拒绝／隔离，不能改成接收时刻或任意截到当前时间。

raw/latest 默认保留三个自然月，允许更短，最大不能超过三个自然月。逐点截止 = 原 observedAt 加三自然月，目标月无对应日期时取月末的同一上海墙上时刻；达到截止即不可作为有效事实读取。不是 90 天，不按上传、查询、回执或其他点更新续期。

| 原观察时刻 | 三自然月最大截止 |
| --- | --- |
| 2026-01-31T12:00:00.123+08:00 | 2026-04-30T12:00:00.123+08:00 |
| 2023-11-30T06:00:00.000+08:00 | 2024-02-29T06:00:00.000+08:00 |
| 2024-11-30T06:00:00.000+08:00 | 2025-02-28T06:00:00.000+08:00 |

批准后的 DAA／SMA／AW 相关旧 UTC 文案和例子须显式对齐此规则，并保留其历史效力来源。这个文档修订不代表旧数据库时区已知或迁移完成；禁止整体加八小时、重编码历史／原文或旁建替代 profile 充当迁移。

### R11. 原文、投影、物理清理与去重证明

一包各点 observedAt 可以不同。**整包不可变原文的读取默认按最早成员截止保守到期**，防止因其他点尚有效而泄露已到期值；latest 各点仍按自身截止。Backend 若采用等效逐点投影／存储策略，须在其实施 spec 明确证明不返回过期值、不冒称投影仍是原文，并给出原文摘要／查询投影摘要区分。较晚包时间、保存时间或新成员不能延长早成员的最大期限。

逻辑不可读、有限批次物理删除、磁盘回收／副本／备份职责分开。Backend 任务冻结清理 SLA、批量／锁／负载预算和失败可观测性，不声称截止瞬间销毁全部介质。原值到期后，幂等／历史回执／完整性最小摘要可按独立有限期限保留；不得借回执或 feed 永久保留原始值。没有历史提交证明时，不得用“应当曾提交”伪造 ACK。

历史回执重放不复活 raw/latest，cursor 与去重证明的可恢复范围需一致解释；长期无新数据的 latest 和派生目录也会到期。Backend 不因 DAA／SMA 未确认而延长原值可读窗口，无法恢复的缺口必须显式报告。DAA 本地清理不能删除受保护的未确认引用／未完成材料，其有限容量和历史保护仍独立，不能把后端拒绝直接变成本地删除许可。

## 7. 编号需求：SMA 与业务永久保存

### R12. 两段可靠投递及模块责任

DAA -> 事实 API 的确认终点是 Backend 事实可靠提交；SMA -> 业务 API 的确认终点是模块业务事务可靠提交。前一 ACK 不证明后一段完成。SMA 不连接 PLC 或业务 SQL；按需求读取最新／历史，选择点和转换，依据 OpenAPI 或手工目标配置生成模块字段。

后续匿名业务 API 采用模块自有 typed data，执行必填／类型／设备／领域约束、幂等和事务；不得接收表名＋任意字段直接写数据库。已有带认证接口不因“非前端使用”自动取消认证。新增集成 producer 的幂等范围由模块规范确定，不能伪造用户／admin 为现有 actor_user_id 提供值。

以下为拟新增单温度业务记录的语义样例，不是现有完整温控 POST 的可调用载荷：

~~~json
{
  "producerId": "sma-demo",
  "eventId": "delivery-demo-1",
  "mappingId": "mapping-temperature",
  "mappingRevision": "mapping-v3",
  "sourceRefs": [
    { "plcId": "plc-a", "sampleId": "sample-a71", "pointId": "point-a-temperature" }
  ],
  "data": {
    "equipmentId": "equipment-demo",
    "sampledAt": "2026-11-03T10:00:00.123+08:00",
    "temperature": 202
  }
}
~~~

eventId 在一次逻辑投递中首次冻结，重试／重启保持；sourceRefs 解释输入，mappingRevision 固定转换语义。不能每次定时轮询都为同一个输出新造 ID；重算／修正与业务自然键冲突由目标模块规则明确。若目标已有 sampleId 等幂等字段，需在模块合同中明确等价映射，不能同时存在两套含义不明的确认身份。

目标可靠回执应绑定 producer／event／内容摘要并给出业务记录 ID、created／duplicate 和持久结果。SMA 持久确认后才标已投递；接收 cursor、处理 checkpoint、冻结 outbox 和各目标业务确认分开，按后续 SMA spec 实施。无可靠目标确认不因为 HTTP 200/202 就删 outbox。

### R13. 业务数据默认永久保存

已经模块 API 校验并可靠持久确认的业务记录，默认永久保存，即不参加自动到期删除；修正／删除仍走模块明确业务规则。业务表持有实际业务值、事件时间和必要来源／定义／映射版本，raw/latest 过期后仍可独立查询和解释。不是仅保一个 raw 外键后宣称业务已永久保存。

raw/latest 清理不级联删除业务记录或尚未完成的 SMA outbox。业务需要的追溯摘要有独立 owner／规则，不把所有 raw 原文永久复制为“业务追溯”。SMA 输入／outbox 仍有容量和期限，不能成为无限原始备份。

若 SMA 在原事实到期前已可靠保存足够业务请求，可按自身和目标期限继续投递；尚未取得的输入或缺片已经到期时，必须报告真实缺口、暂停受影响任务并显式重同步。业务永久保存不能补救从未成功采集、取得或入库的数据，不承诺每个采样都自动成为业务记录。

## 8. 后续软件任务、依赖与验收标准

### R14. 三项任务的关系及实施 gate

下列软件 ID 是后续建议，当前不创建、不批准，也不把其完成写入本任务验收。

| 阶段／候选任务 | 归属与范围 | 前置与就绪／完成标准 |
| --- | --- | --- |
| ARCH-AW-008 r1 | 当前根目录文档任务；修订需求合同和四份设计，完成独立文档核验 | 精确 r1 批准后才进入文档 Development；文档 QA 和 Owner 终验不代表软件可运行 |
| ARCH-BE-009（暂拟） | 当前 Python Backend 的事实接收、raw/latest、两种读取、保留和兼容实现 | Backend 自有精确 spec／批准；接收结构、摘要／manifest／回执／错误／限额／来源定义／混合批次矩阵、迁移和游标算法定稿；通过下列 B01–B08 后形成固定可联调候选 |
| DAA-008（暂拟） | DAA 可靠上传器、配置/UI、必要增量验证、手册和受控阶段 C 联调 | DAA 自有精确 spec／批准；依同一正式 provider 合同开发，实际 HTTP 联调等待 Backend 独立就绪及明确隔离测试授权；通过 D01–D08 后提交阶段 C 接受 |
| 后续 SMA／各业务模块任务 | 消费、映射、持久业务投递与相应匿名模块入口 | 各自合同／范围批准及独立验收；不作为 DAA 阶段 C 的前置，不由 008 文档授权执行 |

共同需求文档验收后，Backend provider 在其任务中确定正式版本／字段／参数并取得精确批准；DAA 固定消费该版本。双方各自批准后可并行开发，不能先猜字段写上传器再要求对方兼容。若共同语义实质改变，先由 PM 修订受影响 spec 并重新精确批准。

### R15. Backend 后续范围和软件验收输入

| 编号 | 必须交付的增量能力／可验证条件 |
| --- | --- |
| B01 | 新匿名事实一写两读路由和 OpenAPI／严格输入输出／稳定错误；新接口无凭据可调用，既有认证／权限路由未降级；非法类型／范围／体积仍拒绝。 |
| B02 | 显式 Model／索引／Alembic 与兼容方案；不改旧基线冒充升级，不使用启动自动 DDL；旧 CA／Projection／标量消费者有版本隔离或适配，不对同来源双写。 |
| B03 | 整批事务、去重／异内容冲突和可靠回执；丢响应后同请求可恢复结果，mixed／expired／unknown 矩阵和原确认范围可对账。 |
| B04 | 逐点并发 latest 不倒退；同 DB 多组、两 PLC 同 DB、旧代次补传、新坏质量、移组／定义／停用均按合同解释。 |
| B05 | history range 和安全 cursor；独立证明先分配后提交、并发晚提交、晚历史、重复页／空页、过滤绑定和 cursor 到期不漏读或不假完整。 |
| B06 | 三自然月月末／闰年／精度、混合点到期、未来时钟、逻辑过滤、有限物理清理、去重历史证明不复活原值；不级联业务／未完成输出。 |
| B07 | 单独获批隔离数据库上的必要迁移／事务／并发检查及 fresh Verification；实际命令、库身份、schema版本和清理依赖有记录，不触及生产或 Owner 原 profile。 |
| B08 | 向 DAA 交付正式合同／OpenAPI、源码和 schema 版本、关键文件指纹、限额／错误／回执／来源规则、测试数据／地址占位和就绪记录；QA通过、Owner接受、部署分别标示，不以源码存在声称服务已上线。 |

本任务只列以上标准，不执行数据库／API 测试，不预记通过。业务匿名写入适配、既有业务时间迁移及所有模块接口不并入事实服务任务的默认范围，应另有明确 spec。

### R16. DAA 后续范围和软件验收输入

| 编号 | 必须交付的增量能力／可验证条件 |
| --- | --- |
| D01 | UI＋SQLite 管理单一事实目标、独立上报周期、批次／超时等有限高级项，无凭据表单／第二套上报点开关／任意事实 JSON 编辑；普通启动保持 pnpm tauri dev。 |
| D02 | Rust 长运行上传器只取本地已提交事实，有界批次、首版单在途及退避；切页／弹窗不控制采样或上传寿命，不等待网络持有数据库写事务。 |
| D03 | 冻结请求与身份恢复，ACK 的合同／请求／样本摘要和覆盖范围校验，本地确认单调事务；后端已存响应丢失、本地 ACK 失败和重启恢复均不假确认。 |
| D04 | 最新优先＋公平历史预算，多个 PLC／组有进展；坏／过期批次需处理不全局饥饿、不静默删样本或更换身份掩盖冲突。 |
| D05 | 采集／上报独立开始暂停、容量准入与安全清理；后端不可用不阻止容量允许的本地采集。启动／重开仍停止，手工恢复后续传；程序启动时自动采集／上报另项。 |
| D06 | 工作台展示待传、最老待传、可靠已确认、最近成功／错误与上报实态；有界日志／脱敏／i18n。保留既有样本详情及原文／SHA，表格按公共列宽规则，弹窗／间距沿 CU。 |
| D07 | 需要的投递元数据／显式 schema 升级及回退在 DAA 自有 spec 先说明，不改旧样本／manifest原文、ID、SHA或覆盖配置；使用新的隔离阶段C profile，阶段B原profile保留。不重复导入／命名／分组等已通过整套B测试。 |
| D08 | 新增中英文阶段C操作手册，Owner仅做必要原生正常上传、API不可达缓冲／恢复补传、有积压退出重开及查询核对；难稳定手工制造的丢回执／并发／过期等由必要自动化承担。固定双方候选和闭库对账材料，fresh Verification 后由 Owner 接受受控阶段C范围。 |

真正阶段 C 的完成必须同时具有 Backend 就绪、DAA 上传／恢复证据、双方事实对账和真实 Owner 决定；不是仅“定时 POST 成功”或状态码 200。DS 继续复用已接受受控能力，DS 新功能、真实 PLC／现场切换、生产迁移、自动启动、后台托管、跨平台打包／分发均另批。

实现默认直接在约定交付源码树；临时副本的有效变更须整合并核对实际入口。各软件任务自行记录必要证据和资源依赖，只清理明确自有且无后续／证据依赖的临时物，不用临时源码验证替代正式交付，不删除阶段B库／历史。

## 9. 本任务文档验收标准

本表是精确 r1 批准后的独立文档核验标准；当前未执行 Development／QA。B01–B08、D01–D08 是未来软件标准，文档核验只检查是否被清楚定义，不把其预期写成已通过。

| AC | 可独立核对的结果 | 对应需求 |
| --- | --- | --- |
| AC01 | Task ID／Revision／角色／阶段一致，状态与实际gate一致（当前起草为draft，后续批准如实更新）；17路径及staged 3MD无假批准／QA，不继承旧任务权力。 | 第1、3节 |
| AC02 | 阶段B已接受、DAA上传未实现、旧CA直库、现有表／认证GET／业务POST和SMA路线分清；陈旧现状原位更新，历史记录不改。 | 第2节 |
| AC03 | 匿名事实一写两读与后续业务集成、现有前端权限边界明确；无动态绕过、伪造admin、万能SQL或隐式身份平台。 | R01/R12 |
| AC04 | pointId／sampleId键原样、四层身份、类型／坏质量、managed ASCII与legacy保留、单份points／派生目录明确。 | R02 |
| AC05 | 请求和manifest例子可解析，包含跨DB／PLC与分片／失败解释；sample/cycle/batch完成范围不混。 | R03 |
| AC06 | 原字节SHA、传输摘要、请求摘要分清，缺少算法／参数的正式定稿责任明确；不重写历史。 | R03 |
| AC07 | 提交后可靠回执、created／duplicate、样本与整轮边界及本地ACK事务可推演；HTTP／易失入队不被当确认。 | R04 |
| AC08 | 重复／冲突／到期／历史确认／unknown／混合批次和退休派生规则有责任矩阵；错误示例不虚构成功或已回滚。 | R05 |
| AC09 | 逐点latest与DB聚合、同DB多组、源顺序／定义／代次并发与首次采用／交接任务明确；旧包不回退。 | R06 |
| AC10 | latest最近结果含坏质量，缺点不删、停用声明／无声明限制、定义漂移局部处理和新鲜度分别明确。 | R07 |
| AC11 | 时间段与增量模式、过滤／排序／分页游标绑定、安全提交位置及晚提交反例、过期／重同步完整；接收cursor不冒充处理顺序。 | R08/R09 |
| AC12 | 默认／最大三自然月、上海+08、月末／闰年／原精度、按原采集时间及防续期规则对称；旧UTC修订不是历史迁移。 | R10 |
| AC13 | 含不同点时刻的整包原文到期、latest逐点到期、投影／原文摘要、逻辑过滤／物理清理／有限去重证明无矛盾。 | R11 |
| AC14 | DAA事实ACK与SMA业务确认分开，eventId／mappingRevision／来源示例和永久业务独立值明确；raw清理不级联。 | R12/R13 |
| AC15 | Backend范围／B01–B08、正式合同与DDL／游标算法／兼容／隔离测试／固定交接材料列清，未假称实现。 | R14/R15 |
| AC16 | DAA范围／D01–D08、独立周期／Rust owner／队列／UI／容量／恢复／默认停止／手册明确，只补必要增量证据。 | R14/R16 |
| AC17 | 合同稳定后分别批准并行开发，实际联调待Backend就绪；SMA／业务API、自动启动／现场不是本任务或DAA首版前置。 | R14–R16 |
| AC18 | 新共同合同在demands/proposed；文档／provider承诺／可执行schema／实现／验证／部署状态分层，文档不造第二套正式schema。 | 第3、8节 |
| AC19 | 本地链接／锚点、Markdown表格／围栏及全部JSON语法通过；中英文合同及索引对称，图文／跨文档规则一致，已有保护面无越界差异。 | 全文 |
| AC20 | Development自检与新的fresh-context Verification实际记录分开；Owner文档终验和后续软件验收分别真实；无代码／库／配置／API／设备／发布操作。 | 第3、12节 |

## 10. 文档推演反例

| 输入／误解 | 文档必须能回答 |
| --- | --- |
| 不带Token向新事实接口提交；同时匿名访问现有管理GET | 前者依合同校验接收，后者仍遵守原认证；route用途不同而非根据客户端绕过。 |
| A/B都有DB71、同DB两个组各有不同点 | 身份不冲突，latest合并不同点；各PLC裸序号不比较。 |
| 先1005后1001，1005是坏质量 | raw保留历史，latest不倒退；最新失败不能被1001旧好值冒充当前成功。 |
| 一个cycle两包，只有一包收到ACK | 该包可靠确认，整轮仍不完整，不能以最大序号跳过缺片。 |
| 服务端提交后响应丢失／本地ACK写失败 | 同冻结请求恢复；既不重造身份，也不先清理材料。 |
| 合法样本和过期样本已冻结同批 | 根据全批拒绝／历史证明／unknown状态明确处置，原批不改写、不假ACK，合法数据仍有调度机会。 |
| 小raw ID先分配后提交，SMA已取较大ID页面 | Backend安全cursor证明不会越过该晚提交；普通max ID不足。 |
| 一包早一点已到期，其他点晚几毫秒仍有效 | 原文保守到期或经明确投影策略过滤；不能通过原文查看返回早一点过期值。 |
| SMA收到数据但尚未完成业务投递，raw到期 | 有足够持久输出可按独立期限继续；无输入报真实缺口，业务永久策略不补造缺失。 |
| 旧中文legacy名字／原字节JSON被新格式化 | 稳定pointId无损解释，历史原文／SHA不改；投影与原文校验分开。 |
| 文档QA通过即启动Backend迁移或真实DS联调 | 仍需对应软件精确批准及运行授权，本任务只完成文档。 |

## 11. 风险、待定技术参数与回退

- 匿名集成允许可达客户端提交来源声明；当前不认证决定显式记录，不宣称来源真实性或设备所有权，不以该风险自行扩展登录／认证实现。
- 最新优先、同源历史完整、commit-safe cursor和业务处理顺序不同；文档用反例区分，后续以并发／故障证据验证，客户端单在途不代替Backend并发控制。
- 原文到期、保留摘要和永久业务容易互相越界；以R10–R13分别限制可读原值、有限证明、业务独立值与真正缺口。
- 旧表／Projection／业务POST的认证、actor幂等及UTC时间不是新匿名合同的现成实现；未来模块任务明确兼容／迁移，不在此批量改写。
- 正式编码／算法／数值仍需后续Backend与DAA spec冻结：type/缺值矩阵、manifest／片编码、摘要profile与测试向量、首次来源采用与定义起效、历史游标算法／过滤／起止规则、时钟容差、限额／速率／超时、公平预算、混合批次退休、清理SLA及最小证明期限。它们的责任和进入软件前的gate必须清楚，不能据占位例子直接写生产代码。

本任务回退仅限实际文档变更，先核对并发差异、保留旧批准／QA和必要审计，不整文件覆盖他人内容；真实schema／业务／设备／部署回退另批。临时阅读／检查材料不作为唯一证据；主协调依当前workflow只收尾明确自有资源。

## 12. 当前交接、批准与修订历史

| 时间 | 事件 | 效力 |
| --- | --- | --- |
| 2026-11-03 | Human Owner要求先起草ARCH-AW-008 r1，原话见第1节 | 允许本spec起草及必要索引；不是精确r1正文批准，不改详细设计／代码／SQLite |
| 2026-11-03 | PM形成r1 draft | 待Human Owner精确批准；Development、fresh Verification、Owner文档终验尚未发生 |
| 2026-11-04 | Human Owner精确批准ARCH-AW-008 r1 | 本次仅登记真实批准并交接文档Development；需求、风险、17路径allowlist及AC保持，独立文档QA与最终验收仍待后续 |

2026-11-04 Human Owner 精确批准原话：

> 可以，批准 ARCH-AW-008 r1，按 spec 修订跨端合同和相关详细设计，并完成独立文档核验。只改文档，不改代码，已有 SQLite 配置和历史不动；后端与 DAA 的软件实施另行立项，本次不启动实际联调。

本次精确批准对应的批准前 spec SHA-256 为 de6d5eb92a445f163b5eaacf669821c879634b570043e99189ce1bca7ece6417。批准只授权第3节原有文档范围；没有改变R01–R16、AC01–AC20、B01–B08/D01–D08的责任划分和17路径allowlist，不授权代码／DDL／真实API／数据库／设备／实际联调。已有SQLite配置、历史、原文及SHA保持保护；Backend与DAA软件仍各自另立项。

本次PM批准登记不创建tasks/checklist，不宣称Development、独立QA或Owner文档终验已经发生；正文起草阶段的draft表述属于2026-11-03历史，当前状态以元数据与本节真实gate为准。

当前交接及后续顺序：

1. 已完成范围gate：Human Owner于2026-11-04精确批准ARCH-AW-008 r1；PM如实登记，主协调仅机械同步索引。
2. 主协调调用实际Development，完整读取本bundle和当前受影响源／文档，在第3节文档范围交付tasks及DEV自检；不执行未来B/D软件验收。
3. developer_handoff后调用新的fresh-context Verification，只核验本任务AC01–AC20及保护面并记录checklist，不修改实现。
4. qa_passed后由Human Owner最终验收文档。之后Backend／DAA分别以自有spec取得精确软件范围批准；本文件不触发自动接续、跨会话发消息或软件启动。

适用skill：本任务文档治理用aiis、project-governance，HTTP／数据边界用backend-arch；未来Backend实现按其response/layers/database/migration/auth/operations references，DAA按rust-runtime、desktop-tauri，Vue／文案按frontend-ui、i18n-workflow，实际点位算法变化才加plc-point-mapping。所有技能均服从当前已批准范围，不恢复Celery／Redis／Python Worker，也不将PM自检写成独立QA。
