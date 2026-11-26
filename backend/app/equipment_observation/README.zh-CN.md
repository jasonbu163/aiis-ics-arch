# 设备状态、过程历史与能耗

[English](README.md) · [当前机器接口 v2 合同](../../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md) · [r10 规格](../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#r10-source-independent-energy) · [使用说明](../../../docs/equipment-status-process-monitoring.zh-CN.md#r10-guide)

本模块通过 manifest 注册机器写入、人工查询和管理员配置。r10 中，SMA、第三方或其他获授权程序使用同一套与来源无关的 v2 合同；PLC 事实和任务点证据不再是前置条件。这里说明的是后端合同，不代表某个 SMA 或 PLC 已实现接入。`sourceRefs` 是发送方可选声明的元数据，后端不验证其血缘。已发布的 [v1 合同](../../../contracts/published/http-api/equipment-observation-v1/README.zh-CN.md) 保留为历史记录。清退版本在校验身份和授权范围后明确拒绝旧 v1 事件，且不重放旧回执。设备状态和过程监控使用已配置的数据库连接，日常请求不再预检全库迁移版本或私有 profile 中的目标元数据。私有 profile 继续约束业务权限，

`equipment_main` 按设备和任务保存最新的多区域完整快照；`monitor_main` 为任务追加配置为留存的过程数据；`energy_consumption_main` 为表计追加独立能耗样本，不依赖任务。事件须传入真实 `observedAt`；服务端保留事件时间，并将带偏移的时间转换为项目时区。持久回执和按目标／事件独立重试的规则以 v2 合同为准。实时整包会清除未包含的区域，写入方必须具有完整覆盖范围的权限。

设备和过程共用 `observation_metric_*` 配置表，写入回执保存到 `observation_ingest_receipts`。表计样本独立使用 `energy_ingest_receipts`。迁移保留原 ID 和重试结果。

回执迁移支持库和表继承的默认排序规则 `utf8mb4_0900_ai_ci` 和 `utf8mb4_unicode_ci`，标识列保留显式 `utf8mb4_bin`。迁移在执行任何 DDL 前核查 MySQL 8.4 前驱中实际生效的 CHECK 表达式与每个受影响字符列的排序规则。

管理员分别配置区域、稳定指标键、显示名称、单位、卡片、曲线与历史留存；前端据此解释和显示值，不以槽位或翻译后的标题作为写入键。仓库外私有 profile 默认关闭，配置机器凭据摘要及设备、目标、区域、指标和表计授权。机器发现与写入受这些授权约束；人工查询和管理使用单独权限以及设备／表计范围校验。数据库由 Alembic 显式迁移，启动和模块注册不会自动建表或填入数据；原采集事实与 API 保持独立合同及权限。

写入登记及无需 token 的观测读写使用独立合同。[写入登记合同](../../../contracts/published/http-api/observation-write-sources-v1/README.zh-CN.md)

能耗日常运行核对所配置的 MySQL 服务和库名，只按自身业务依赖读写。管理员独立登记能耗来源。[能耗登记来源批量写入](../../../contracts/published/http-api/energy-registered-ingest-v1/README.zh-CN.md)说明免 Token 多表 POST、单一回执与事务内样本写入。

能耗集成新增免 Token GET，可按表计及采样组读取最新样本，也可按采集时间范围分页读取历史。同路径的旧 POST 继续使用机器 Bearer，Web 查询和管理继续使用登录用户 Bearer。[能耗公有读取](../../../contracts/published/http-api/energy-public-reads-v1/README.zh-CN.md)

管理员可以新增表计、修改名称和可读角色。采用本服务版本前，应在独立批准的目标库应用受保护迁移 `9e0c5d41b7a2`，执行时显式指定 `ENERGY_METER_EXPECTED_SCHEMA` 和 `ENERGY_METER_EXPECTED_SERVER_UUID`。尚未编辑的 profile 表计继续沿用原名称和角色范围。[能耗表计管理](../../../contracts/published/http-api/energy-meters-v1/README.zh-CN.md)

能耗曲线组保存一块表计、一个采样组下的有序数值指标。配置和统计读取沿用表计范围。应用迁移时，对独立获批的目标从 `9e0c5d41b7a2` 升至 `af6d8b2c4e90`，指定 `ENERGY_CURVE_EXPECTED_SCHEMA` 和 `ENERGY_CURVE_EXPECTED_SERVER_UUID`。迁移增加一张配置表，应用代码回退时保留该表。[能耗曲线组接口合同](../../../contracts/published/http-api/energy-curve-groups-v1/README.zh-CN.md)
