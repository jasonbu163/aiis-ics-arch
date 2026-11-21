# 设备观察与能耗机器写入 v2

[English](README.md) · [OpenAPI](openapi.json) · [合成请求](vectors.json) · [私有配置样例](example-profile.json) · [批准的 r10 规格](../../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#r10-source-independent-energy)

清退后的源码仅接受 v2，鉴权后明确拒绝旧 v1 且不重放归档回执。设备观察私有 profile 仅接受 `d8f2a4c6b915`；同目录已发布的向量、OpenAPI 和 profile 样例保留原版本。 [清退规格](../../../../plans/ARCH-OBS-002-legacy-observation-retirement/spec.md)

设备和过程共用 `observation_metric_*` 配置表，写入回执保存到 `observation_ingest_receipts`。表计样本独立使用 `energy_ingest_receipts`。迁移保留原 ID 和重试结果。

本合同说明当前接口沿用的 r10 v2 报文。机器 Bearer 的 producer、设备、目标、区域、指标与表计权限在服务端私有 profile 中配置，提交方类型可为 SMA、第三方或其他授权程序，正文不可授予权限；不要求 PLC 证据，也不表示 SMA 产品已经实现该投递。profile 在进程加载时缓存，修改需按运行环境协调重载；样例中的目标、摘要均为不可使用的占位符，不能提交真实 token 或 profile。

| 方法及路径（均以 `/api/v1` 为前缀） | 使用 |
| --- | --- |
| `GET /integration/metric-definitions?equipmentId=...` | 返回当前机器有权限的区域、指标类型、单位及两路启用状态，不返回采样值。 |
| `POST /integration/equipment/latest-snapshots` | 一设备一任务的完整多区域快照；较新包整包替换。 |
| `POST /integration/monitor/history-samples` | 同样的包追加历史，只保存历史启用的指标，回执注明保存／跳过。 |
| `GET /integration/energy/metric-definitions?meterId=...&groupKey=...` | 返回该机器有权限且启用的表计指标、物理量、单位与各自计量模式。 |
| `POST /integration/energy/samples` | 一表计一组一个样本，不含任务号。 |

三个 POST 限制 `application/json` 且不超过 65,536 字节；具体结构见 [OpenAPI](openapi.json)。设备两路每次必填 `eventId`、`data.equipmentId`、字符串 `taskNo`、原始 `observedAt` 和 `groups`；历史还须明确 `quality: "good"`。实时质量缺省／`null` 为 `unknown`。能耗每次必填 `eventId`、`meterId`、`groupKey`、`observedAt` 与非空 `values`；含增量指标时须同时提交真实 `intervalStartAt`、`intervalEndAt`，起点早于终点。不含增量指标不能带区间。时间须有偏移，最多可无损保存微秒，后端转换上海时间，不能用接收时间代填。

可省略 `contractVersion`（默认 v2）和 `producerId`（使用认证身份，若传则必须匹配）；`mappingId` 与 `mappingRevision` 可一起省略或一起提供；`sourceRefs` 可省略，仅用于调用方声明，不证明数据血缘。具体机器凭据及可写范围配置一次；`eventId` 和采样数据每次提供。重试保留相同事件和原正文；目标、producer、事件号组成各路独立去重身份，冲突内容返回 409。重放已存回执时仍按当前权限鉴权：须有请求所需权限，实时还须有完整替换范围权限，权限已撤销时返回 403。未知提交结果使用原身份及原文重试。

区域键／指标键为稳定标识，不使用可变中英文标题。完整包可省略区域、发送空区域或 `groups: {}` 表示缺测；实时替换要求有被清空范围的全部权限。空组也须登记和授权；未知组／指标、越权或错误类型整包拒绝，不产生部分写入；`null` 非有效指标值，数字 0、布尔 false 和空字符串有效。数字必须可无损经过 JSON 数值存储。历史启用但整包缺测时仍保存缺测事件以形成曲线断点；无任何历史启用指标才返回 `no_history_metrics`。不同事件同一真实采样时刻分别保留，不能把事件号当时间或自动证明跨发送方是同一个物理样本。

标准成功回执 `data` 含 `target`、`producerId`、`eventId`、`outcome`、`recordId`，设备两路还可有 `stored`、`skipped`。常见结果为 `stored`、`stale`、`already_stored`、`no_history_metrics`。`401` 是身份错误，`403` 是越权，`409` 是事件或样本冲突，`422` 是字段／类型／时间／质量等校验失败，`503` 是目标未就绪或提交结果未知。机器 GET 不读取业务样本；业务用户和 admin 的读取、配置、管理另用各自人类权限和设备／表计范围，见[使用说明](../../../../docs/equipment-status-process-monitoring.zh-CN.md#r10-guide)。
