# Acquisition Consumers v1

采集消费者按已提交顺序读取单个 PLC/DB。消费者 API 管理起点、运行状态、租约、待投递及 ACK；由 SMA 等已授权调用方发送目标 POST。后端保存运行元数据，原始点值仍由采集事实表持有。

[OpenAPI](openapi.json) · [JSON Schema](schema.json) · [验收向量](vectors.json) · [样本 POST 和回执](../plc-facts-v2/README.zh-CN.md) · [English](README.md)

## 请求顺序

1. `PUT /api/v1/acquisition-consumers/{consumerId}` 固定源 PLC/DB 和专属的 `external` 目标，起点选 `now` 或 `retained`。前者只消费创建起点之后的提交，后者还包括起点时仍有效的回填历史。重复创建返回原起点。
2. 设 `run-state` 为 `running`，获取 `lease`。一个任务在一个时刻只有一个有效租约。续租、释放及进度写入检查 `X-Consumer-Lease-Id` 和 `X-Consumer-Lease-Generation`。读 `next` 得到一个按顺序待处理的事件或 `empty`，读取不推进。
3. 以 `pending/{deliveryId}` 先固定配置版本、生成规则、目标身份和目标正文 SHA-256，再发送样本 POST。绑定的目标请求须包含服务 Bearer、两个租约头、`X-Consumer-Id` 和 `X-Delivery-Id`。目标 `sampleId` 与 `deliveryId` 相同，`sourceSeq` 是该事件的 `eventSeq`。
4. 收到匹配的目标 `committed/created` 或 `committed/duplicate` 回执，再提交 `ack`。回执确认和游标推进同事务。状态查询用于进程重启后的对账。请求使用相同身份和完全相同字节才能安全重试，前提是来源登记和样本有效期仍满足。
5. 对 `503 acquisition_consumer.commit_outcome_unknown` 先读状态，再按原操作重放。创建及 pending 分别以消费者 ID、投递 ID 幂等。其他写操作复用同一 `operationId` 与同一输入，改变输入会产生冲突。旧租约不能推进或提交新的绑定目标 POST，已完成的同一 ACK 可返回已确认结果。
6. `410 acquisition_consumer.gap` 表示存在应消费但已过期或无法读取的事实。错误 `data` 包含 `eventSeq` 和 `lastConfirmedSeq`。客户端保留位置，使用新身份换发或跳至最新都会改变交付范围，需要操作方另行决定。

## 权限与边界

消费者 API 校验专用 Bearer，并限制允许的消费者、PLC/DB 和操作。凭据由后端私有配置管理。只有已绑定的专属目标流要求新增的写入校验，其他 v2 采集接口仍遵循原开发合同。本合同定义的目标回执为同一后端的 `plc-facts-v2`。实际目标接管、超过保留期限或无法重构一致正文时，自动重试不能继续。

游标顺序由每条流的事务锁分配，跨 PLC/DB 没有全局顺序。已领取结果不占用或推进游标，只有持久化待投递状态、匹配回执后的 ACK 能推进。后端保存请求指纹和版本标识，SMA 保留配置及其不可变版本。
