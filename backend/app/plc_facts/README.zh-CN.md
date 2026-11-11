# PLC事实owner

## v2 样本入口

`ARCH-BE-012 r4` 新增单 PLC/DB 样本写入、逐点最新值、历史列表及详情。默认 `PLC_FACTS_V2_ENABLED=False`，`PLC_FACTS_V2_PROFILE_FILE` 为空。启用前在仓库外准备私有 JSON，并在进程环境或后端运行配置中显式指定文件。以下只是合成配置结构，摘要是占位值。

```json
{
  "target": {"alias": "dev-example", "serverUuid": "00000000-0000-4000-8000-000000000001", "schema": "fixture_schema", "schemaRevision": "4e6a8b0d2f14"},
  "instances": [{"instanceId": "daa-a", "sourceType": "daa"}],
  "credentials": [{"instanceId": "daa-a", "tokenSha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}],
  "sources": [{"plcId": "PLC-A", "instanceId": "daa-a", "sourceGeneration": "gen-a", "dbNumbers": [21]}],
  "readScopes": {"admin": [{"plcId": "PLC-A", "dbNumbers": [21]}]}
}
```

每个登记实例指定 `daa` 或 `external` 类型并使用独立随机凭据，配置文件只存凭据的 SHA-256 小写十六进制摘要。吊销凭据时可保留实例登记和活跃来源，供获准用户读取现有最新值。DAA 必须提交采集组和配置版本，外部程序可以分别省略或传 null。历史来源类型按入库时保存，尚未核实的旧来源保持 null。所有角色（含 admin）的读范围均单独配置；非 admin 还需 `plc-facts-read`。配置变更由所有后端进程在协调切换后重新加载。见 [v2 合同](../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)。

为保留 REAL 的原始十进制精度，v2 两张 JSON 值字段在内部把 `good` REAL 保存为经过校验的数字文本。读取时按 `dataType` 验证并编码回 JSON number，其他类型保持原 JSON 类型。该内部表示保留负零和科学计数法，不展开极小指数。

`2c4e6a8b0d12` 引入两表；新精确 head 为 `4e6a8b0d2f14`。`plc_facts_history` 每行一份完整样本，`plc_facts_latest` 每行一个点的最新值。私有配置与数据库 revision 必须精确一致。[v1 合同](../../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)保留为历史，其路由、七表与维护命令已退役。BE-010 凭据独立管理并须精确匹配目标 revision。见 [ARCH-ACQ-003](../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) 和 [v2 维护](../../scripts/plc_facts_maintenance/README.zh-CN.md)。源码变化不证明部署或采用。
