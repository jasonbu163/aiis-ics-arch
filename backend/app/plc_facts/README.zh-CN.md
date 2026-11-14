# PLC事实owner

## ARCH-ACQ-004 r3 来源管理

运行配置仅含 `target`，其 `schemaRevision` 为 `7b9d1f3a5c7e`。管理员在「采集数据 → 来源配置」每台 PLC 登记 `plcId`、`instanceId`、`sourceGeneration` 和展示类型 `sourceType`。样本只匹配前三项，DB 随样本发送；实时读取需要当前登记，未过期历史独立于登记读取。[管理 OpenAPI](../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json) · [迁移与恢复](../../scripts/plc_facts_maintenance/README.zh-CN.md#r3-单表迁移与恢复)

样本 POST 和五个 GET 按开发合同免 Bearer，管理 API 需要 active admin。来源登记不验证设备身份。Web 可复制已提交行的三个标识；接管需要版本校验、明确确认和该 PLC 的新代次，旧队列须先核对，历史不会改写。 [操作说明](../../../docs/acquisition-data-guide.zh-CN.md)

确认删除会移除来源登记并停止其上报，不删除历史。登记行中的退役代次也会删除；当相关事实和最新值已不存在时，旧代次可能无法识别。重新登记同一 PLC 应使用从未使用的新代次。

## v2 样本入口

`ARCH-BE-012 r4` 新增单 PLC/DB 样本写入、逐点最新值、历史列表及详情。默认 `PLC_FACTS_V2_ENABLED=False`，`PLC_FACTS_V2_PROFILE_FILE` 为空。以下为前驱版本 `5f7a9c1e3b25` 的历史配置格式，仅供冻结 r2 工具在 r3 迁移前导入。

```json
{
  "target": {"alias": "dev-example", "serverUuid": "00000000-0000-4000-8000-000000000001", "schema": "fixture_schema", "schemaRevision": "5f7a9c1e3b25"},
  "instances": [{"instanceId": "external-a", "sourceType": "external"}],
  "sources": [{"plcId": "PLC-A", "instanceId": "external-a", "sourceGeneration": "gen-a", "dbNumbers": [21]}],
  "readScopes": {"admin": [{"plcId": "PLC-A", "dbNumbers": [21]}]}
}
```

前驱使用配置中的 `instances` 和 `sources` 准入；r3 使用数据库中的三个标识。所有发送方的采集组和配置版本均可分别省略或传 null。历史来源类型按入库时保存，尚未核实的旧来源为 null。

前驱的 `readScopes` 仅作为迁移前对账材料。见 [v2 合同](../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)。

为保留 REAL 的原始十进制精度，v2 两张 JSON 值字段在内部把 `good` REAL 保存为经过校验的数字文本。读取时按 `dataType` 验证并编码回 JSON number，其他类型保持原 JSON 类型。该内部表示保留负零和科学计数法，不展开极小指数。

`2c4e6a8b0d12` 引入两表，`4e6a8b0d2f14` 完成定名，r3 head 为 `7b9d1f3a5c7e`。`plc_facts_history` 每行一份完整样本，`plc_facts_latest` 每行一个点的最新值。私有配置与数据库 revision 必须精确一致。[v1 合同](../../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)保留为历史，其路由、七表与维护命令已退役。BE-010 凭据独立管理并须精确匹配目标 revision。见 [ARCH-ACQ-003](../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) 和 [v2 维护](../../scripts/plc_facts_maintenance/README.zh-CN.md)。
