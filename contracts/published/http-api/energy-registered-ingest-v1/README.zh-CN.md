# 能耗已登记来源批量写入 v1

[English](README.md) · [OpenAPI](openapi.json) · [合成请求与响应](examples/batch.json) · [批准规格](../../../../plans/ARCH-OBS-010-energy-registered-batch-ingest/spec.md)

## 登记来源

管理员从「能耗管理 → 配置管理 → 写入登记」操作，也可使用下列用户 Bearer API。标识区分大小写，允许 1–64 个 ASCII 字母、数字、点、下划线或连字符。名称可选，最多 128 字符。默认启用。标识不可修改，删除后不可再次使用。`.` 和 `..` 的路径分别使用 `%252E` 和 `%252E%252E`，与[设备登记合同](../observation-write-sources-v1/README.zh-CN.md#登记管理)一致。

| 方法 | 相对 `/api/v1` 的路径 | 操作 |
| --- | --- | --- |
| GET | `/energy/write-sources` | 列出未删除的登记，包含停用来源 |
| POST | `/energy/write-sources` | 输入 `sourceKey`、可选 `name`、可选 `enabled` |
| PATCH | `/energy/write-sources/{sourceKey}` | 修改 `name`、`enabled` 或两者 |
| DELETE | `/energy/write-sources/{sourceKey}` | 删除登记并保留原样本及回执 |

管理员另行维护表计指标。现有表计配置和角色读取范围继续适用。登记无需机器 token，也无需逐个绑定表计。既有 [Bearer v2](../equipment-observation-v2/README.zh-CN.md) 入库合同继续按其生产者权限执行。

## 发送样本

在获准的内网使用 `POST /api/v1/integration/energy/registered-samples` 和 `Content-Type: application/json`。服务不使用 `Authorization` 头。UTF-8 JSON 最大 65,536 字节。

- 同一已启用来源在同一实际采集时刻对应一包。发送 `sourceKey`、`target: "energy"`、`observedAt`、`items`。在 `items` 中按表计、采样组组织非空的 `values`，值为已配置启用指标的有限数字，0 有效。
- 时间携带实际偏移，微秒后的非零小数不接受。包含时段增量指标的组必须提交 `intervalStartAt` 和 `intervalEndAt`，且开始早于结束。只含累计和瞬时指标的组省略区间。省略 `quality` 或传 null 等同于 `unknown`。可用质量值有 `good`、`bad` 和 `unknown`。
- 成功返回一个字符串 `receiptId`。每个表计／采样组返回一个字符串 `recordId`，按表计键和组键的 UTF-8 顺序排列。整包在一个事务内提交。时间统一输出上海时间并保留六位小数。

保留原包用于重试。等价数值、时区表示、键顺序和默认质量会返回原回执及有序记录。同一来源同一采集时刻的正文不同，返回 HTTP 409 `equipment_observation.event_conflict`。未知、停用或已删来源的写入和重试均返回 HTTP 403 `equipment_observation.source_not_enabled`。字段或表计配置错误为 422，过大为 413，介质错误为 415。HTTP 503 包含 `equipment_observation.commit_unknown` 时也应重试原包。

## 存储和兼容性

`energy_write_sources` 独立保留删除的标识，与旧生产者的内部身份隔离。每包占用一条 `energy_ingest_receipts`，有序结果保存在 `result_detail`，各 `energy_consumption_main` 样本引用这一回执。日常运行继续核对配置的 MySQL 服务和库名，并按能耗实际依赖读写。采集时间和样本无需任务、设备状态或过程监控记录。

`b52e9c416a07` 的前驱为 `a1c307f8d2e4`。显式迁移要求匹配的 `ENERGY_WRITE_EXPECTED_SCHEMA` 和 `ENERGY_WRITE_EXPECTED_SERVER_UUID`。若回退应用代码，保留已登记来源、样本和回执。迁移拒绝降级以保护数据。实际库迁移及服务切换另外授权。

[路由](../../../../backend/app/equipment_observation/api/routes.py) · [批次事务](../../../../backend/app/equipment_observation/services/energy_registered_ingest.py) · [迁移](../../../../backend/alembic/versions/20261124_2300_b52e9c416a07_energy_write_sources.py)
