# 设备状态与过程历史写入合同 v1

[English](README.md) · [OpenAPI](openapi.json) · [脱敏向量](vectors.json) · [r8 规格](../../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#r8-dev-integration)

SMA 与第三方使用同一个机器 Bearer 认证入口和三条路径。调用者类别及设备、组、目标、指标范围由服务端私有 profile 绑定，正文不能授予权限。本合同描述源码行为，不代表现场 SMA、DAA 或生产部署已采用。

| 方法和路径 | 含义 |
| --- | --- |
| `GET /api/v1/integration/metric-definitions?equipmentId=line-01&groupKey=temperature&target=latest` | 发现获准目标的已启用指标键、类型、可选单位；`history` 再取历史白名单交集。仅发现，不返回采集值、历史或槽位。三个查询参数均必传。 |
| `POST /api/v1/integration/equipment/latest-snapshots` | 对设备、任务、组的快照整组覆盖，旧时间样本返回 `stale`。 |
| `POST /api/v1/integration/monitor/history-samples` | 对合格样本按来源去重并追加历史。 |

两个 POST 均为 `application/json`、最多 65536 字节，均以 `values.metricKey` 提交已登记类型的 JSON 数字、字符串或布尔值；键大小写有意义，缺测指标应省略，`null` 值无效，`0`、`false` 和卷号前导零保留。标题和单位来自配置，不由写入方提交。原始采样时间必须带时区，后端转换到上海时区。`taskNo` 要有已入库的任务点来源证据，不能由当前界面任务或接收时间推断。

| 字段 | 第三方 | SMA |
| --- | --- | --- |
| `sourceRefs` | 每次一条 `external_event`，必填 `sourceEventId`；`sourceId` 可省略并由绑定补齐。 | 每次 `plc_fact` 引用同一份已入库 v2 样本，至少包括绑定的任务点及映射用点。 |
| `data.taskNo`、`data.sampledAt`、`data.values` | 每次必填。 | 每次必填。 |
| `data.equipmentId`、`data.groupKey` | 身份固定单设备／组时可省略，否则必填。 | 每次必填。 |
| `data.quality` | 实时可省略或为 `null`，记为 `unknown`；历史必须明确 `good`。 | 每次必填，历史必须为 `good`。 |
| `contractVersion`、`producerId`、`mappingId`、`mappingRevision` | 可省略，映射两字段一起省略或一起提交；后端用身份配置补齐。 | 每次必填，可由程序一次配置后自动带上。 |
| `eventId` | 可省略，由来源和目标稳定生成。 | 每目标每次必填且重试沿用。 |

第三方其他字段的省略并非传 `null`；除实时质量外，显式 `null` 不合法。有效重试采用同一目标、同一事件及原内容，返回原收据；同事件内容不同返回 `409`。同源历史以另一个合法事件重投得到 `already_stored`；旧实时样本可返回 `stale`。`503` 可能是未就绪或提交结果未知，保留原事件并按原内容重试；两路分别确认和重试。采样间隔由发送方按采集时间选样，不是展示开关。原始事实及观察回执均保留对应 task evidence；数据质量与人工复核标记是不同字段。

常见状态：`401` 凭据缺失或无效；`403` 身份停用或越权；`409` 事件、样本或任务证据冲突；`413` 正文过大；`415` 非 JSON 媒体类型；`422` 类型、字段、目标指标或质量错误；`503` profile／目标未就绪或提交结果未知。错误原因随 `errorCode` 返回；验证层拒绝也可能采用 FastAPI 的标准 422 结构。完整合法值和条件见 [r7 规格第 5、9 节](../../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#5-sma-指标发现和写入接口)。

[vectors.json](vectors.json) 包含两份不同的 v2 合成样本、一次指标发现、第三方最简两路及合成 SMA 全信封两路和示意回执。每个调用方的两路使用各自同一来源采样；第三方来源号与 SMA 样本号不同。样本中的固定时间和记录 ID 只作解释，执行前应生成在当前任务证据有效期内的采样时间和新的来源／序号。`walkthrough.py` 是限定回环地址的可复跑合成端；私有 profile、独立机器 token、设备绑定与目标数据库须事先在受控环境按下文配置。

脚本使用固定的合成 PLC、设备、任务号和指标，只能指向已确认专用可丢弃数据的独立测试目标，**不能用于现有 dev 库**；确认参数不是数据库身份校验。先在采集来源登记 `plc-01/daa-fixture/generation-1`，再配置专用 OBS profile 和账号。设置 `OBS_DEMO_ADMIN_USER`、`OBS_DEMO_ADMIN_PASS`、`OBS_DEMO_EXTERNAL_TOKEN`、`OBS_DEMO_SMA_TOKEN` 后，可执行 `python walkthrough.py --base-url http://127.0.0.1:18395 --fixture-ack DISPOSABLE-OBS-FIXTURE`。脚本会写入数据，不自动清理。不要把真实凭据写入仓库。`groupSettings` 对设备和组设正数 `staleAfterSeconds`，与任务点 `maxTaskAgeSeconds` 分开；历史 `historyRules` 独立配置指标白名单和正数 `intervalSeconds`。

[私有 profile 结构示例](example-profile.json)中的摘要和 UUID 均为虚构占位：须替换为各独立随机 token 的 SHA-256 和已核对的目标，并将实际文件放到仓库外。PLC facts v2 另用 target-only profile，采集来源通过当前登记表核验。

当前采集模块的开发版事实 GET/POST 按其自身合同提供，不使用本文的机器 Bearer 或旧的 `readScopes`；观察模块的三条机器接口仍需各自授权。DAA 和 SMA 产品执行与现场联调以各自任务和当前采集合同为准。
