# 设备状态、过程历史与能耗

[English](README.md) · [当前机器接口 v2 合同](../../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md) · [r10 规格](../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#r10-source-independent-energy) · [使用说明](../../../docs/equipment-status-process-monitoring.zh-CN.md#r10-guide)

本模块通过 manifest 注册机器写入、人工查询和管理员配置。r10 中，SMA、第三方或其他获授权程序使用同一套与来源无关的 v2 合同；PLC 事实和任务点证据不再是前置条件。这里说明的是后端合同，不代表某个 SMA 或 PLC 已实现接入。`sourceRefs` 是发送方可选声明的元数据，后端不验证其血缘。已发布的 [v1 合同](../../../contracts/published/http-api/equipment-observation-v1/README.zh-CN.md) 保留为历史记录：不承诺接收新的 v1 事件；已存储的相同 v1 请求可按原规则重放，包括其历史任务证据。

`equipment_status_main` 按设备和任务保存最新的多区域完整快照；`process_monitor_main` 为任务追加配置为留存的过程数据；`energy_consumption_main` 为表计追加独立能耗样本，不依赖任务。事件须传入真实 `observedAt`；服务端保留事件时间，并将带偏移的时间转换为项目时区。持久回执和按目标／事件独立重试的规则以 v2 合同为准。实时整包会清除未包含的区域，写入方必须具有完整覆盖范围的权限。

管理员分别配置区域、稳定指标键、显示名称、单位、卡片、曲线与历史留存；前端据此解释和显示值，不以槽位或翻译后的标题作为写入键。仓库外私有 profile 默认关闭，配置机器凭据摘要及设备、目标、区域、指标和表计授权。机器发现与写入受这些授权约束；人工查询和管理使用单独权限以及设备／表计范围校验。数据库由 Alembic 显式迁移，启动和模块注册不会自动建表或填入数据；原采集事实与 API 保持独立合同及权限。
