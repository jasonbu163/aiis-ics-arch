Task ID: ARCH-ACQ-006
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 ARCH-ACQ-006 r1；交 Development 在隔离环境实施并在交接后进行 fresh-context Verification，现有库及历史不动
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_governance
Capability: 采集事实稳定续读与消费投递状态
Owner: AIIS ICS Architecture Backend / 采集数据模块 Human Owner
Acceptance Chain Reference: 本规格第 6 节及 Development Lifecycle Workflow
Depends On: 现有 plc-facts/v2 样本、来源登记与历史查询基线
Related Task: aiis-ics-arch.aw.sma::SMA-008 r2
Created: 2026-11-19 Asia/Shanghai

# 采集事实稳定续读与投递状态

## 1. 目标与范围

为 SMA-008 持续读取采集数据并在失败后恢复，提供一个后端前置交付：每个消费任务固定一个 PLC 和 DB，按稳定位置读取已提交样本；后端保存消费位置和待确认投递身份，使 SMA 重启后能按相同身份重建请求并确认结果。一个任务对应一个目标，允许多个任务独立消费同一源。SMA 的 SQLite 仅存配置及其为重试保留的不可变配置版本，后端拥有采集事实和必要的运行状态。

本草案包含后端新续读与状态 API、必要的向前数据库迁移与一次性历史索引准备、采集写入事务接线、隔离验证和公开合同。后端不代 SMA 发起业务 POST，不重复保存采集点值或待发送 JSON。SMA 页面的选点、映射、发起请求和目标回执解释属于 [SMA-008 r2](../../automation-world/semantic-mapping-agent/plans/SMA-008-acquisition-data-get/spec.md)。

现有 `GET /api/v1/acquisition-data/history` 按 `sampledAt DESC, id DESC` 与 offset 分页，时间窗口最多七天，且只读未过期事实。延迟上传旧采样时间和并发写入会移动页次，无法用于无漏续读。现有采集 POST 在当前登记匹配、样本未过期时，以同一实例与样本 ID 和完全相同的 UTF-8 请求字节重试，可返回 `committed/duplicate`。丢回执后正文不同、来源切换或过期时有冲突或拒绝。 [历史查询](../../backend/app/plc_facts/crud/async_v2.py) · [v2 合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)

当前源码是事实与接口核对，尚无本规格的流、消费者 API、迁移、后端状态或 SMA 联调实现。草案不授权运行迁移、向真实数据库写入、启停现有服务、部署或使用真实设备。

## 2. 稳定顺序和历史起点

### 2.1 按 PLC/DB 的提交顺序

以精确字节 `plcId` 和 `dbNumber` 标识一条消费流。新建轻量流头保存单调 `eventSeq`；每条事件记录该序号、样本历史 ID、源身份、样本有效截止和必要索引，不复制 `points` 或请求正文。代次切换时同一 PLC/DB 沿用流及序号，事件保留各自 `instanceId` 和 `sourceGeneration`。旧来源被删除后，已提交且未过期的事件仍可按授权范围读取，新上报遵循现有登记拒绝规则。

新样本写入先取得对应流头的事务行锁，再在同一数据库事务分配序号、写入原事实、更新 latest 和新增事件；提交后才释放锁。事务回滚不留下事件或有效序号。同一流的后一个写入不能先于持锁事务提交，`created` 对应唯一事件，原样本的 `duplicate` 不再新增事件。不同 PLC/DB 可分别推进。此顺序以事务提交及该流的串行化为依据，不能用原自增 ID、`sampledAt`、`storedAt` 或 DAA `sourceSeq` 直接充当可靠游标。读取原始点集仍使用现有 v2 事实和字段语义。

### 2.2 激活时纳入现有历史

新增表和流索引有显式向前迁移。激活之前需在具体目标的维护窗口暂停全部 v2 写入和清理，阻断旧服务进程、旧二进制、直库及其他不写流记录的写入方，等待在途事务完成并检查没有混合写入；无法证明时不激活。停写窗口将激活时仍未过期的各 PLC/DB 历史行按确定的 `storedAt, id` 次序回填事件，仅保存原行引用和元数据。回填次序可重复，用于完整覆盖当时尚保留的历史，不声称重建过去的真实提交顺序。

回填完成后核对历史范围内每条原事实恰有一个事件，保留原事实、最新值和登记；新服务与唯一后继 schema 一起启用，其后所有采集 POST 必须走 §2.1 的同事务路径。MySQL DDL 可能分步提交，迁移要记录阶段与目标，在中断或部分回填时继续保持写入关闭；按源历史 ID 幂等复核并恢复，发现混合状态则停止，不用清空事实、盲目 stamp 或切换为无流写入解决。恢复和实际迁移均须对应环境的具体授权。源码当前 Alembic head 为 `c9e1a3b5d720`，开发前复核并在交接中明确精确前驱和后继，不改写已有迁移。 [模型](../../backend/app/plc_facts/models/v2.py) · [清理](../../backend/app/plc_facts/crud/sync_v2_maintenance.py)

### 2.3 消费起点、过期与缺口

消费者首次创建时，后端在流头锁下原子记录 `startMode`、数据库当前时间 `startAt` 和该流已提交最大序号 `startSeq`，随后执行相应模式：

- `now` 从 `startSeq` 之后继续，明确不消费更早事实。
- `retained` 包含启用回填后、创建消费者时仍未过期的所有事件，再无缝消费 `startSeq` 之后的新事件。创建时已过期的事件不在这一任务的初始范围，接口返回这类排除的计数及边界供 UI 告知；用户选择该模式即确认这一已定义范围。启用前已过期的原历史也无法回填。旧代次或已删除来源，只要属于授权 PLC/DB 且在起点时有效，仍属于该范围。

流记录保存原 `expiresAt`。初始化时已过期且明确排除的事件可略过；属于任务范围的事件若在处理前过期、原事实意外丢失，或位置落入不可证明的缺口，必须返回 `410 acquisition_consumer.gap` 和受影响位置，停止推进。过期可能在序列中间发生，不能仅以最早一条或最大序号推断。样本清理可删除原事实，但须保留对应过期/缺口证据；只有已过期且对所有相关消费者均已处理或在其起点明确排除的连续前缀才可压缩，并保留可判定的低水位。若缺口无法判定则闭合并报告，不静默跳到最新位置。

## 3. 新 HTTP 合同草案

以下为本任务拟新增路径，均以 `/api/v1/acquisition-consumers` 为前缀。成功使用现有 `{code: 200, message: "success", data: ...}` 信封，序号作为十进制字符串传输，`eventSeq` 与位置只在该任务绑定的源流内有含义。服务端按一条一条处理；客户端读取不推进已确认位置。

| 方法与路径 | 输入 | 成功结果与行为 |
| --- | --- | --- |
| `PUT /{consumerId}` | `consumerId` 使用小写 UUID；正文为 `plcId`、`dbNumber`、`startMode`（`now` 或 `retained`）及 `target: {kind: "plc-facts-v2", instanceId, plcId, dbNumber, sourceGeneration}`。 | 首次原子固定 §2.3 的起点与源范围，返回 `consumerId`、`startAt`、`startSeq`、`lastConfirmedSeq`、历史排除摘要和初始停止状态。相同 ID 与相同原始创建参数重复返回同一起点，参数不同返回 409。更换源范围或目标使用新消费者 ID。 |
| `PUT /{consumerId}/run-state` | `operationId` 与 `desiredState`（`running` 或 `paused`）。 | 后端记录用户期望状态。相同操作重复返回相同结果；暂停阻止领取新事件、新建 pending 与新目标 POST，保留在途项。暂停前已进入目标的请求可以完成并核对回执。SMA 退出或崩溃不自动改成 paused。 |
| `POST /{consumerId}/lease` | `operationId`、`workerId` 和 `action`（`acquire`、`renew`、`release`）；续租和释放附当前 `leaseId`、`leaseGeneration`。 | 原子获取、续租或释放，返回 `leaseId`、递增 `leaseGeneration`、`expiresAt` 与建议续租时间。竞争者获得 409；重复同一操作得到同一结果，过期后新代次可接管。所有会改变投递或进度的操作核验当前代次。 |
| `GET /{consumerId}` | 服务身份。 | 返回源范围、起点、`desiredState`、确认位置、有效租约状态和待确认 `deliveryId`、源序号、目标身份、配置版本、序列化版本、正文指纹与状态，不返回已发送正文。用于响应丢失和重启对账。 |
| `GET /{consumerId}/next` | `leaseId` 与 `leaseGeneration`。 | 返回 `status: "ready"`、不可变 `eventSeq`、目标投递身份和同一条未过期完整样本；没有可读样本返回 `status: "empty"`。存在待确认项时返回同一身份和源样本，不能跨过。读取不确认、不发送 POST；需要的源已过期或缺失返回 410。 |
| `PUT /{consumerId}/pending/{deliveryId}` | 租约、`eventSeq`、`configVersion`、`configHash`、`serializerVersion`、`bodySha256` 和目标身份摘要。 | 在任何业务 POST 前，原子固定当前下一事件的投递身份、源位置、配置版本、生成规则与摘要。相同身份和参数重复成功，正文或配置哈希变化、越序和身份不匹配返回 409。状态写入结果未知可用 GET 对账后以相同参数重试。 |
| `POST /{consumerId}/pending/{deliveryId}/ack` | `operationId`、租约，以及目标合同要求的 HTTP 状态和业务回执摘要。 | 验证 pending、当前租约、目标回执和身份，在同一事务标记已确认并推进位置。相同成功 ack 重复返回已确认结果，不再次推进；响应丢失后可 GET 对账再以原操作重试。未确认或错误回执不推进。 |

消费者 ID、操作 ID、请求字段的长度、字符集、时间格式、响应 Schema、错误码和 OpenAPI 向量由本任务交付合同固定。`next` 的样本含现有 v2 的身份、点位及原采集时间；同一事件在保留期内按固定点顺序、类型和可重复序列化规则返回。HTTP 200 和 `code=200` 都要成立；`empty` 不表示事件已被投递。

建议将状态稳定定义为 `idle`、`pending`、`confirmed` 和 `blocked`，区分期望运行状态与实际执行租约。一个任务只有一个有效租约，代次变化使旧执行者无法新建 pending 或推进。若旧执行者已有 POST 在途，接管者仅可使用相同待确认身份与字节重试；目标幂等合同负责避免重复写入。已确认的相同 ack 重放可只读返回既有结果，即使原租约已到期；新确认仍必须使用当前有效租约。

需持有租约的请求使用 `X-Consumer-Lease-Id` 和 `X-Consumer-Lease-Generation` 请求头，同时携带服务 Bearer；采集目标的绑定流 POST 另带 `X-Consumer-Id` 和 `X-Delivery-Id`。

所有写入操作都要处理提交结果未知：同一 `operationId`/相同输入重放返回同一结果；同一 ID 与不同输入为 `409 acquisition_consumer.operation_conflict`。租约占用、旧代次、越序和 pending 内容变化用可区分的 409；错误字段为 422；来源事实过期或缺失为 410；后端未就绪为 503，提交边界不明返回 `503 acquisition_consumer.commit_outcome_unknown`。每个错误包含稳定 `errorCode`，不泄露凭据、点值或完整请求。

## 4. 投递、权限与数据边界

### 4.1 身份、配置和采集 POST

待投递身份按 `uuid5(NAMESPACE_URL, "aiis:acq-consumer:v1:{consumerId}:{eventSeq}")` 确定生成；消费者 ID 唯一且永久绑定一条源流。先从 next 得到稳定 `deliveryId`，再将原有配置的不可变版本和确定性序列化结果的 SHA-256 写入 pending。SMA 只在取得成功响应或通过状态查询确认 pending 已持久化之后 POST。配置版本保留在 SMA SQLite，属于配置；后端只保留版本标识、哈希和必要运行元数据。相同版本必须保留目标地址、映射、常量、类型转换、序列化规则及影响请求语义的配置，不能因后续编辑改写。密钥通过环境私有配置提供，不记录进状态或日志。

测试采集目标采用已单独登记、与源 PLC 不同的 `external` 测试来源。每个采集目标流 `(instanceId, plcId, dbNumber, sourceGeneration)` 只绑定一个消费者，使用全新且未曾使用的代次并确认无既有目标样本。`sampleId` 由稳定 `deliveryId` 确定，目标 `sourceSeq` 使用该源流 `eventSeq`，因此单任务按事件顺序递增；范围须符合现有 v2 正整数上限。同一后端对已绑定目标流的样本 POST 校验服务 Bearer、消费者、投递 ID、当前租约代次、样本身份和 pending 正文摘要，拒绝其他写入者向该流提交；原有未绑定来源的 v2 行为保持不变。目标来源登记被删除或接管后停止，不能换身份冒充旧待投递。

采集目标确认须具备 HTTP 200、业务 `code=200`、`status=committed`、`outcome=created` 或 `duplicate`，以及与 pending 一致的 `contractVersion`、`instanceId`、`sampleId`。后端核对 SMA 提交的回执摘要并原子确认，它不独立代目标验证 SMA 传入的回执；真实目标写入以隔离回读验证，安全保证以受信 SMA 正确转交真实回执及目标合同成立为前提。测试采集来源必须排除在自身源范围之外。

同身份完全相同 UTF-8 正文字节可在现有来源登记及有效期满足时重试。SMA 必须从仍保留的源样本和原配置版本重新构造，并在发送前核对摘要；结果未知时不能换 `sampleId` 或生成新的正文。源过期、正文不一致、`403` 来源不符、`409` 内容冲突、`410` 过期或目标能力不足均停在待确认，不能自动推进。本 r1 的目标适配与回执校验限 `plc-facts-v2`。其他业务目标后续可在不改源事件含义的前提下扩展目标合同，自动重试须先具备明确的请求身份幂等或结果查询合同；本草案不声称任意第三方 POST 自动实现去重。

### 4.2 新接口准入

新消费者 API 使用 `Authorization: Bearer` 服务身份。后端私有配置将高强度服务凭据的摘要绑定到可用 `consumerId`、PLC/DB 精确范围和操作权限；服务端按身份及范围在查询前过滤，创建、读、租约和确认分别检查。无效或缺失身份返回 401，身份有效但越权返回 403。凭据与日志分离，源码和示例只使用占位值。允许复用现有身份机制中满足机器身份与精确范围的部分，不假定现有网页用户角色已具备这些能力。

当前开发合同的采集 GET 和普通样本 POST 免 Bearer，本草案只为新消费者 API 和上述已绑定目标流提供各自准入，不把网络地址当身份，也不宣称既有开发接口已实现同等鉴权。正常来源登记、latest/history 返回及其他业务 API 的权限合同保持现状。

## 5. 允许触达与迁移边界

| 表面 | 实施范围 |
| --- | --- |
| 采集后端 | `backend/app/plc_facts/` 内 API、schemas、services、crud、models、配置与 manifest 的本能力相关文件；样本写入同事务追加事件，清理保留缺口元数据，目标流身份绑定和服务身份准入。 |
| 数据库 | 一个基于实际单一 head 的新 Alembic 后继，新增流头、事件、消费者、投递及幂等操作所需结构。已有事实与登记保持；隔离回填纳入 §2.2。明确迁移中断恢复、既有目标 revision 守卫与新 revision 兼容，不自动作用到真实目标。 |
| 合同与说明 | 在 `contracts/published/http-api/` 为新消费者合同增补版本化 OpenAPI、Schema 和验收向量；更新采集模块双语 README 与受影响的 v2 合同说明；保留已发布工件的原字节。必要时同步 `CODE_INDEX.md` 中触达入口。 |
| 测试 | `backend/tests/` 定向合同和原有 v2 回归；`backend/tests_mysql/` 专属隔离 MySQL 并发、回填、保留、响应丢失和重启测试。 |

`backend/common/integration/storage.py`、采集目标 revision allowlist 与维护脚本/说明可在保证既有 profile、精确目标守卫和允许 revision 不回退的前提下适配新后继。实际目标迁移、现有服务重启、DAA/SMA 源码、CU、业务目标 API 和生产部署不在本次软件写入范围。新增结构和索引名由 Development 按合同确定，最终公开 API 与机械向量须与实现一致。

Development 与 Verification 按 `backend-arch`、`code-document-indexer` 及项目锁文件工作。若本草案的路径、模式、数据表或安全保证需要实质变化，回 PM 修订并取得精确范围批准。

## 6. 验收标准

| ID | 操作与预期 |
| --- | --- |
| AC01 提交顺序 | 隔离 MySQL 交错同流写入事务，证明后者在前者结束前不能分配并提交下一事件；不同流中制造较早分配数据库 ID 而后提交的情况，并在旧采样时间补传，证明排序不依赖样本 ID 或采样时间。每个成功提交的样本各有且仅有一个事件，回滚无事件，采集 POST duplicate 无新事件。 |
| AC02 激活和历史 | 有非空原历史时，在停写隔离窗口回填并对账未过期行、latest 与登记。注入中断和重复回填恢复，尝试旧二进制与直库旁路写入均被阻断；无法证明停写或发现混合状态时不激活、不清空原数据。启用前已过期历史明确排除。 |
| AC03 起点及缺口 | 测试 `now` 和 `retained`，并在创建前后并发写入，固定起点不漏新事件、不重复创建。构造中间事件先过期、后续事件仍有效，以及创建后才过期和原事实缺失，分别验证初始化排除摘要和 410 停止；清理后缺口仍可辨识。 |
| AC04 来源变化 | 同 PLC/DB 两个来源代次先后写入，事件顺序不断裂。删除来源后已提交且仍有效的旧事件按授权可读，旧身份新 POST 被拒；再次登记新代次后事件接续，旧 pending 不被静默改写。 |
| AC05 租约与原子性 | 两个客户端竞争、续租超时、旧租约过期后恢复，最多一个有效代次能创建 pending 或推进。每个写入操作在提交前后注入丢响应，同一 ID 重放返回相同结果，不同输入冲突。 |
| AC06 POST 未知与 ACK | 隔离采集目标真实接收原始 POST 后丢回执，以相同字节和身份重试得到 `duplicate`，目标 history 回读仅一条。错误合同、实例、样本、HTTP 状态及业务回执均不能推进；成功 ack 的事务提交后丢响应，重放或读状态只返回一次确认，cursor 与确认原子一致。 |
| AC07 保留和重构 | pending 后重启模拟 SMA，使用源事实和原配置版本生成一致字节并核对哈希。依次让源过期、旧配置缺失、正文哈希变化、目标来源接管或目标结果不可确认，均保持待确认或阻断，不生成新目标 ID、不越过未确认项。SMA 本机测试配置库仅含配置和不可变配置版本，无点值或 POST 正文；后端新表不保存点值或正文。 |
| AC08 身份和兼容 | 缺失/错误 Bearer 为 401，跨消费者或 PLC/DB 为 403，合法服务只看到授权范围。绑定测试目标流拒绝非归属写入，普通未绑定采集 POST 和五个现有 GET 维持开发合同，旧公开工件原字节不变。 |

Development 记录源码编译、定向离线测试、专属隔离 MySQL 测试、原 v2/清理/来源登记及 schema 守卫回归的命令、退出码和环境。Verification 在 fresh context 独立复核同一候选及测试。目标采用、真实数据库迁移、DAA 联调和实际业务目标运行需要各自的具体环境证据与决定，不能由隔离测试替代。

## 7. 风险与批准历史

- 稳定续读要求所有写入者参加同一事务序列；混合旧版本、直库写入或不受控清理会破坏完整性，切换阶段的技术阻断与对账是必要条件。
- `retained` 只能覆盖激活回填时及消费者创建时仍保留的样本。之后过期、丢失或目标拒绝会形成明确阻断，人工处置需保留未确认状态及影响说明。
- 后端不保存 POST 正文。源、固定配置或序列化版本缺失后无法验证同字节重发时只能停下；不能把本方案扩大为无期限重放或任意业务接口的恰好一次保证。
- `plc-facts/v2` 开发 POST 当前免 Bearer，同一后端受控目标流须有本规格的定向归属保护。其他后端或第三方目标必须由其自身提供等价的身份、幂等与回执保证。

2026-11-19：Human Owner 请求先形成一份后端前置 spec，完成后 SMA-008 再依据后端合同接续。r1 先作为 PM 草案提出，草案本身未实施、迁移、验证或验收。 [开发工作流](../../.codex/workflows/development-lifecycle-workflow.md)

### r1 实施范围批准

Human Owner 明确表示：

> 好的，批准 ARCH-ACQ-006 r1，先按草案做后端续读游标和投递状态，用隔离环境，完成后做独立验证。现有库和历史数据先别动，SMA-008 r2 等后端验收后再做。

PM 于上海时间 2026-11-19 15:13:33 登记上述批准。获批草案 SHA-256 为 `06e1395ce8bf46d32276c852c066e9eaeb428370989d56f4d658c34193b6346c`。Development 在隔离环境按本规格实施，交接后由 fresh-context Verification 独立验证；现有库和历史数据保持不动，SMA-008 r2 等待后端验收。该范围批准不代表已实施、已验证或最终验收。
