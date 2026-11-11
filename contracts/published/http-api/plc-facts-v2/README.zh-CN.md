# PLC 事实 v2 源码合同

每次 `POST /api/v1/integration/plc-facts/samples` 提交一个实例、一个 PLC、一个 DB 的完整样本。一个请求最多 512 点、524288 字节 UTF-8 JSON。实时和补传使用同一接口，DAA 在本地冻结正文后按原字节重试。历史和逐点最新值同事务提交，只有提交完成才返回 `committed`。

冻结的原 [OpenAPI](openapi.json)、[JSON Schema](schema.json) 和[向量](vectors.json)对应原提供方；新 [r2 OpenAPI](openapi-acquisition-r2.json)、[r2 请求 Schema](schema-acquisition-r2.json) 和 [r2 向量](vectors-acquisition-r2.json)描述当前源码合同。鉴权后，登记为 `daa` 的发送方必须提供非空 `groupId` 和 `configRevision`；`external` 可分别省略或传 null。来源类型由服务端登记决定，正文不得提交 `sourceType`。相同样本身份由省略改为显式 null 会因原始字节变化产生冲突。见 [ARCH-ACQ-003 r2](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md)。

机器使用独立 Bearer。后端针对每个实例配置一份 SHA-256 摘要，校验 PLC、DB 和当前代次。首次保存返回 `outcome: created`，保留期内相同身份和正文重试返回 `outcome: duplicate`。身份或序号冲突返回 409，到达有效截止后返回 410 `plc_facts_v2.expired_unconfirmed`。提交结果未知返回 503 `plc_facts_v2.commit_outcome_unknown`，发送方继续保留并重试冻结样本。

读接口 `/api/v1/acquisition-data/options`、`latest`、`latest/browse`、`history` 和 `history/{id}` 要求登录、`plc-facts-read` 和角色的 PLC/DB 读范围。浏览和历史可省略 PLC 或 DB，先与授权范围求交集再分页，默认 50 条、最多 100 条。latest 支持精确 `pointId`。历史按上海时间半开区间查询，跨度最多 7 天。历史 `sourceType`、`groupId`、`configRevision` 现在可为 null，旧严格类型读取方需适配。样本 ID 为十进制字符串。原值有效截止为原采集时间加三个自然月再减 24 小时，清理方案见 [维护 CLI](../../../../backend/scripts/plc_facts_maintenance/README.zh-CN.md)。

模块注册器内的错误声明采用 `plc_facts.v2.*`，HTTP `errorCode` 采用本合同的 `plc_facts_v2.*`。源码合同固定不代表隔离验证、实际数据库采用或 DAA 联调已完成。

REAL 在数据库的 v2 JSON 字段内使用校验过的十进制数字文本，读取时恢复为 JSON number。调用方收到的数值保留输入精度、负零和科学计数法。
