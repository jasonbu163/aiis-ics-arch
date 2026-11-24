# PLC事实owner

## ARCH-ACQ-004 r3 来源管理

运行配置仅含 `target`，其中原 `schemaRevision` 字段保留供诊断。管理员在「采集数据 → 来源配置」每台 PLC 登记 `plcId`、`instanceId`、`sourceGeneration` 和展示类型 `sourceType`。样本只匹配前三项，DB 随样本发送；实时读取需要当前登记，未过期历史独立于登记读取。[管理 OpenAPI](../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json) · [迁移与恢复](../../scripts/plc_facts_maintenance/README.zh-CN.md#r3-单表迁移与恢复)

安装观察模块的 r8 后继后也显式支持 `8c0e2a4d6f18`。私有 profile 与目标实际 revision 仍必须精确相等；旧目标可继续使用旧 revision，未知或错配一律拒绝。观察模块只经内部证据服务读取当前来源，不改变公开采集合同。

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

`2c4e6a8b0d12` 引入两表，`4e6a8b0d2f14` 完成定名，r3 head 为 `7b9d1f3a5c7e`。`plc_facts_history` 每行一份完整样本，`plc_facts_latest` 每行一个点的最新值。该历史阶段要求私有配置与数据库 revision 精确一致。[v1 合同](../../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)保留为历史，其路由、七表与维护命令已退役。BE-010 凭据独立管理并须精确匹配目标 revision。见 [ARCH-ACQ-003](../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) 和 [v2 维护](../../scripts/plc_facts_maintenance/README.zh-CN.md)。

## 稳定续读和消费投递

`da6c32f8a701` 为每个 PLC/DB 保留提交顺序和到期缺口元数据。消费者以服务身份访问新 API，选择「现在」或「仍保留的历史」起点，经租约、待投递和 ACK 管理进度。后端不重复保存点值或 POST 正文。 [消费者合同](../../../contracts/published/http-api/acquisition-consumers-v1/README.zh-CN.md)

`ACQ_CONSUMPTION_CREDENTIALS_FILE` 指向仓外私有 JSON 文件，留空时没有可用凭据。文件仅允许所有者访问。每项授权含 `sha256`（高强度 Bearer 的小写十六进制摘要）、`consumerId`、精确的 `plcId` 和 `dbNumber` 及 `permissions` 数组。权限值可用 `create`、`read`、`run`、`lease`、`pending`、`ack`、`target`。重启服务加载文件变化。普通采集配置保持原有格式。

后继迁移要求一个确切维护目标，先停写和清理、隔离旧进程及直库写入并等待在途事务结束。目标审批后，交由维护方提供 `ACQ_CONSUMPTION_EXPECTED_SCHEMA`、`ACQ_CONSUMPTION_EXPECTED_SERVER_UUID` 和 `ACQ_CONSUMPTION_WINDOW_CONFIRMED`（`<schema>:<serverUuid>`）。这三个值声明已核查目标及停写窗口，数据库账号仍须按部署隔离及最小权限管理。迁移保留原事实、latest 和登记，先安装阻断未跟踪历史写入的数据库守卫，再固定回填截止时刻。确认事件对账、触发器和后继 revision 后才恢复写入，运行 profile 必须精确改为已采用的后继。新清理路径保留事件的到期证据。中断后保持停写，复核目标、守卫和异常结构，修复冲突后从同一前驱和截止时刻重跑。禁止用清空事实或 Alembic stamp 代替恢复。

## ARCH-ACQ-007 运行表结构

经批准的表名切换完成后，源码使用 `acq_plc_source_registry`、`acq_plc_facts_history`、`acq_plc_facts_latest` 和原有六张消费表。日常访问核对 MySQL 8.4 实例、库名、上海数据库时钟、九张 InnoDB 表结构和消费启用状态。旧 profile revision 或无关的全库后继迁移不影响结构兼容的目标。新写入和重复成功回执均须核对匹配的消费事件。显式清理仍确认实际 Alembic revision。 [切换与恢复](../../scripts/plc_facts_maintenance/README.zh-CN.md#arch-acq-007-表名切换)
