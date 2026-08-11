<!--
  File Path: /tools/plc/s7-virtual-plc/plans/README.zh-CN.md
  Description: S7 虚拟 PLC 任务计划索引
  Main Features:
    - 链接由虚拟 PLC 工具拥有的具体任务记录
    - 区分当前计划驾驶舱与长期实施细节
-->
# S7 虚拟 PLC 任务计划索引

[English version](README.md)

本目录保存 `tools/plc/s7-virtual-plc/` 的具体、权威任务记录。上级 [PLAN.zh-CN.md](../PLAN.zh-CN.md) 是当前驾驶舱，只保留活跃状态、验收和下一道门禁。

## 使用规则

- 任务状态、验收、blocker 或下一步变化时，更新上级 `PLAN.*`。
- 具体实施步骤、协议决策和验证证据只保留一份中文 `<task-id>.md` 事实记录；除非外部协作明确要求，不创建翻译镜像。
- 工具 README 继续负责使用说明。只有已实现的命令或运行合同发生变化时才更新；仅落计划时不得把未来行为描述为当前行为。
- 跨工具 SOP 改动归 `docs/`；CA runtime 行为继续归 `control-agent/`。

## 任务记录

| 文档 | 用途 |
| --- | --- |
| [P4-strict-tsap-validation.md](P4-strict-tsap-validation.md) | 已实现的虚拟 PLC 严格 rack/slot 身份：显式模拟器身份、COTP called-TSAP 拒绝，以及 CA 匹配 / 不匹配只读联调证据。 |
