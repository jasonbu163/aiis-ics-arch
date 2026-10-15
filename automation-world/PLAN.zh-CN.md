# Automation World 计划

[English](PLAN.md)

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| ARCH-AW-001 | owner_accepted | [r1](../plans/ARCH-AW-001-agent-foundation/spec.md) | CA已迁入并冻结，DAA/SMA可构建并独立启动；定向复核通过，Human Owner于2026-10-14接受r1；本轮未追加测试。UI与SQLite后续处理。 |

CA保留冻结兼容基线；后续采集发展由DAA承接。S1 API合同、AW事实上传、业务闭环、共享UI、SQLite配置及映射存储另立spec。完整索引见[任务目录](plans/README.zh-CN.md)。

## 子工程计划

AW 管理整体阶段和跨工程依赖。各子工程 PLAN 管理自身实施任务，并链接唯一的本地 bundle；根目录历史任务保持原位。

| 工程 | 所属计划 | 当前阶段 |
| --- | --- | --- |
| Console UI | [CU PLAN](console-ui/PLAN.zh-CN.md) | [CU-001 r1](console-ui/plans/CU-001-workbench-foundation/spec.md) 为 draft；轻量工作台与公共 UI 源码出口待精确范围批准 |
