# PLC 事实 v2 源码合同

[English](README.md)

`POST /api/v1/integration/plc-facts/samples` 是采集原值的通用写入入口。DAA、第三方和备用采集程序可以通过它提交已经采到的 PLC 数据。手工构造合成样本也能独立验证后端的上报、去重、实时值和历史查询。

当前开发阶段，样本 POST 和五个 GET 都无需 Bearer。每次 POST 提交一个实例、一个 PLC、一个 DB 的一次完整采集样本，点数为 1–512。正文使用 UTF-8 `application/json`，最多 524288 字节。同一次采集包含多个 DB 时，各 DB 分别 POST、分别确认。 [开发 OpenAPI](openapi-acquisition-dev-r4.json) · [请求 Schema](schema-acquisition-r2.json) · [DAA 请求与回执向量](vectors-acquisition-r2.json)

## 来源登记

后端只用 `plcId`、`instanceId` 和 `sourceGeneration` 匹配 `plc_source_registry` 的当前行。管理员每台 PLC 登记四项：三个标识和用于展示的 `sourceType`；DB 随样本发送，不参与登记校对。Web 可从已提交行复制三标识，登记提交后即时生效。登记 API 需要管理员登录，采集 POST/GET 在开发阶段免 Bearer。接管需使用该 PLC 的新代次并先处理旧队列。后端用该 PLC 登记行的 `sourceType` 标注历史，供展示，不参与准入或样本校验；正文包含 `sourceType` 返回 `422`。 [管理 API](openapi-acquisition-sources-r4.json) · [来源登记说明](../../../../backend/app/plc_facts/README.zh-CN.md)

管理员确认删除来源后，使用该身份的后续上报及重试返回 `403`，未过期历史仍可查询。删除同时移除该行的退役代次记录；相关事实和最新值都不存在时，系统可能无法识别旧代次。重新登记同一 PLC 应使用从未用过的新代次，并保留冻结样本原身份。

## 上报字段及用途

### 样本字段

| 字段 | 填写规则 | 用途 |
| --- | --- | --- |
| `contractVersion` | 必填，固定为 `plc-facts/v2`。 | 声明正文协议版本，后端据此校验合同。 |
| `instanceId` | 必填，填写后端登记的实例 ID。 | 标记采集程序实例，与 PLC ID、来源代次一起核对当前登记，并划定样本 ID 的去重范围。 |
| `sampleId` | 必填，在同一个实例内唯一。补传沿用原 ID。 | 唯一标识本次 DB 采集样本，供去重及匹配提交回执。 |
| `plcId` | 必填，填写后端登记的 PLC 标识。 | 定位设备，核对来源登记，也是查询最新值和历史的设备键。 |
| `dbNumber` | 必填，填 1–65535 的 JSON 整数。 | 指定设备上的 DB，确定本次提交和确认的最小单位。 |
| `sourceGeneration` | 必填，填写该 PLC 当前登记的来源代次。 | 区分接管或重新编号前后的采样流，来源切换后可拒绝旧代次上报。 |
| `sourceSeq` | 必填，填无前导零的十进制字符串，范围 1–9223372036854775806。 | 同一实例、PLC、DB 和代次内按采样顺序递增。较旧序号可补历史，已有逐点最新值以较大序号为准。字符串形式可保留大整数精度。 |
| `points` | 必填，填本次采样配置中该 DB 的完整上报点集。 | 把同一次采集的原值和质量一起提交，历史可按完整样本回读。 |
| `groupId` | 所有发送方均可省略、传 `null` 或填有效标识。 | 记录原采样所属的采集组，便于追溯采样配置。 |
| `configRevision` | 所有发送方均可省略、传 `null` 或填有效标识。 | 记录采样时生效的配置版本，便于追溯当时的点表。 |

标识字段按原字节精确匹配，长度为 1–128 个 UTF-8 字节。字段值首尾须为非空白字符，且排除 ASCII 控制字符。`groupId` 和 `configRevision` 的空字符串返回 `422`。

### `points` 中的字段

| 字段 | 填写规则 | 用途 |
| --- | --- | --- |
| `pointId` | 必填，使用稳定标识，在同一份样本内唯一。 | 在 PLC 和 DB 下定位点位，支持精确读取单点最新值。 |
| `dataType` | 必填，例如 `INT`、`BOOL`、`REAL`。 | 声明 PLC 原值类型，后端据此校验值的 JSON 类型和范围。 |
| `value` | 必填。`good` 填与类型匹配的原值，`bad` 填 `null`。 | 保存采集到的原始值。`INT` 使用 JSON 数字，`BOOL` 使用 JSON 布尔值。 |
| `quality` | 必填，填 `good` 或 `bad`。 | 告诉读端该值是否有效，并区分正常的 `0`、`false` 和采集失败。 |
| `observedAt` | 必填，日期和时间用 `T` 分隔，带 `+08:00`，可保留至微秒。 | 记录原采集时间，用于历史查询和计算原值保留期限。补传沿用原时间。 |
| `name` | 可选，最多 100 个 UTF-8 字节。 | 提供用于界面显示的点名。 |
| `reason` | `bad` 必填，填非空字符串，最多 128 个 UTF-8 字节。`good` 时省略或填 `null`。 | 说明采集失败或缺测原因，例如 `missing`。 |

## 提交与补传

完整样本写入 `plc_facts_history`，逐点最新值写入 `plc_facts_latest`，同一事务提交后返回 HTTP `200` 和 `data.status=committed`。首次提交的 `data.outcome` 为 `created`。样本仍在有效期内，且 `plcId`、`instanceId`、`sourceGeneration` 仍与该 PLC 当前登记匹配时，同一实例和样本 ID 使用相同正文字节重试，`outcome` 为 `duplicate`，历史仍只有一条。接管后，即使正文未变，使用旧身份重试也可能返回 `403 plc_facts_v2.scope_rejected`。

调用方保存原样本的 ID、序号、采集时间和实际发送的 UTF-8 正文。遇到超时、丢回执或 `503 plc_facts_v2.commit_outcome_unknown` 时，保留待确认样本并重发原字节。收到 `committed` 后，核对回执中的 `contractVersion`、`instanceId` 和 `sampleId`，再标记为已确认。

重排字段、改空白、把省略的字段补成 `null` 都会改变正文。失败响应可按 HTTP 状态和 `errorCode` 判断。

| HTTP | `errorCode` | 含义 |
| --- | --- | --- |
| `403` | `plc_facts_v2.scope_rejected` | 上报来源与登记不匹配，或显式查询实时数据的 PLC 未登记。 |
| `404` | `plc_facts_v2.not_found` | 历史详情对应的样本不存在或已过期。 |
| `409` | `plc_facts_v2.sample_content_conflict` | 当前来源仍通过准入且样本未过期时，同一身份的正文变化，或序号被同一采样流中的另一条样本占用。 |
| `410` | `plc_facts_v2.expired_unconfirmed` | 样本已到有效截止。 |
| `413` | `plc_facts_v2.payload_too_large` | 正文字节数超过限制。 |
| `415` | `plc_facts_v2.media_type` | 媒体类型、字符集或压缩编码不符合要求。 |
| `422` | `plc_facts_v2.invalid_request` | 正文或查询参数无效。例如必填字段缺失、超过 512 点，或采集时间比后端当前时间晚 5 分钟以上。 |
| `503` | `plc_facts_v2.not_ready` 或 `plc_facts_v2.commit_outcome_unknown` | 服务或目标库未就绪，或写入结果未知。 |

## 读取接口

以下路径以 `/api/v1/acquisition-data` 开头。实时读取使用当前来源登记；历史独立于登记读取所有未过期事实，包括当前未登记 PLC。开发 GET 免 Bearer，这些事实也可通过接口查询。SMA、CA、FF 等读取程序可通过这些 GET 获取原值。

| 接口 | 查询参数与结果 |
| --- | --- |
| `GET /options` | 默认返回已登记 PLC 的有效历史和当前最新值的 DB；`?view=history` 返回所有未过期历史的 PLC/DB 选项。 |
| `GET /latest` | 必填 `plcId`、`dbNumber`，可选精确 `pointId`。省略 `pointId` 返回该 DB 的有效最新点位，指定时 `data.items` 至多一条。 |
| `GET /latest/browse` | 可选 `plcId`、`dbNumber` 和点位搜索词 `pointSearch`。在读取范围内分页。 |
| `GET /history` | 必填 `from`、`to`，可选 `plcId`、`dbNumber`。按样本采集时间查询摘要，从 `data.items` 取历史 `id`。 |
| `GET /history/{id}` | 用十进制字符串 `id` 查询一份样本，在 `data.points` 中读取完整点集。 |

分页默认 50 条，每页最多 100 条。历史用上海时间 `[from, to)`，最大跨度 7 天。历史 `sourceType`、`groupId`、`configRevision` 可为 `null`。每个点的原值查询截止为原采集时间加三个自然月再减 24 小时，整份样本取最早截止。REAL 的内部 JSON 值以校验过的十进制数字文本保存，读取时恢复为 JSON number，保留输入精度、负零和科学计数法。 [维护 CLI](../../../../backend/scripts/plc_facts_maintenance/README.zh-CN.md)

## Swagger 手工测试

1. 打开开发后端的 `/docs`，展开 `plc-facts-v2`。准备一个登记为 `external` 的合成来源。首次上报后可用 `GET /api/v1/acquisition-data/options` 查看实际 PLC 和 DB。示例标识与后端说明中的合成来源配套。使用已有 dev 来源时，将三个标识替换为登记值，DB 编号填写本次采集值。 [本机 Swagger](http://127.0.0.1:8000/docs) · [合成来源配置](../../../../backend/app/plc_facts/README.zh-CN.md#v2-样本入口)
2. 打开 `POST /api/v1/integration/plc-facts/samples`，点 `Try it out`，粘贴下方最小请求并点 `Execute`。对新的合成样本，使用新 `sampleId`、该采样流下一个未用的递增 `sourceSeq`，并把 `observedAt` 换成这次测试的上海时间。示例序号 `"1"` 适用于新的合成采样流。期望返回 HTTP `200` 和下方 `created` 回执。
3. 在三个标识仍与当前登记匹配且样本有效时，保持正文原样再点 `Execute`。期望仍为 HTTP `200` 和 `committed`，`outcome` 变为 `duplicate`。在相同条件下，也可以将该样本的 `value` 改为 `43` 再提交，保留原 ID 和序号时应返回 `409`。
4. 执行 `GET /api/v1/acquisition-data/latest`，传入本次提交的 `plcId`、`dbNumber` 和 `pointId=demo_counter`。检查 `data.items[0]` 的 `value=42`、`quality=good`、`sampleId` 和 `sourceType=external`。
5. 执行 `GET /api/v1/acquisition-data/history`，输入同一 PLC、DB，并用包含 `observedAt` 的 `from`、`to` 查询。例如示例时间对应 `2026-11-11T16:59:00+08:00` 至 `2026-11-11T17:01:00+08:00`。按 `sampleId` 找到唯一的一条摘要，再将其 `id` 填入 `GET /api/v1/acquisition-data/history/{id}`，核对 `data.points` 中的原值及 `groupId`、`configRevision` 为 `null`。

最小的外部程序请求包含一个正常点位。登记为 `daa` 时使用 DAA 的来源标识，也可省略或填写原采样的 `groupId` 和 `configRevision`。 [完整 DAA 示例](vectors-acquisition-r2.json)

```json
{
  "contractVersion": "plc-facts/v2",
  "instanceId": "external-a",
  "sampleId": "swagger-external-001",
  "plcId": "PLC-A",
  "dbNumber": 21,
  "sourceGeneration": "gen-a",
  "sourceSeq": "1",
  "points": [
    {
      "pointId": "demo_counter",
      "dataType": "INT",
      "value": 42,
      "quality": "good",
      "observedAt": "2026-11-11T17:00:00+08:00"
    }
  ]
}
```

首次提交成功的回执如下。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v2",
    "instanceId": "external-a",
    "sampleId": "swagger-external-001",
    "status": "committed",
    "outcome": "created"
  }
}
```

## 合同工件与源码

模块注册器内的错误声明采用 `plc_facts.v2.*`，HTTP `errorCode` 采用 `plc_facts_v2.*`。 [HTTP 路由](../../../../backend/app/plc_facts/api/v2.py) · [请求与响应模型](../../../../backend/app/plc_facts/schemas/v2.py) · [原值校验](../../../../backend/app/plc_facts/v2_domain.py)

历史机器合同保存了各验收基线。 [原 OpenAPI](openapi.json) · [原请求 Schema](schema.json) · [原向量](vectors.json) · [r2 OpenAPI](openapi-acquisition-r2.json) · [ARCH-BE-012 r4 开发记录](../../../../plans/ARCH-BE-012-simplified-plc-facts/tasks.md) · [ARCH-ACQ-003 r2 验收](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)
