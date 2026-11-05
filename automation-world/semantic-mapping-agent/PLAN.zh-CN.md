# Semantic Mapping Agent 计划

[English](PLAN.md)

本 PLAN 管理 SMA 任务；[AW PLAN](../PLAN.zh-CN.md)管理跨工程依赖。历史 ARCH-AW-001 证据保持在仓库根目录。

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| SMA-001 | draft | [r2 总规格](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md) | SMA-002/SMA-003 已获 Owner 验收。SMA-004 r1 经有限返工后独立 QA2 通过，待 Owner 最终验收；后续阶段仍仅列目标，总规格保持 draft。 |
| SMA-002 | owner_accepted | [r1 职责清理](plans/SMA-002-scope-cleanup/spec.md) | [独立验证与 Owner 收口](plans/SMA-002-scope-cleanup/checklist.md)固定候选 af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2，确认无漂移，并在 Owner 接受已披露影响与限制后关闭 B1。QA 通过，条件性清理验收仅对此候选生效；原事件历史与未来 profile 保护不变。 |
| SMA-003 | owner_accepted | [r1 CU 接入](plans/SMA-003-cu-integration/spec.md) | [独立验证与 Owner 验收](plans/SMA-003-cu-integration/checklist.md#owner-acceptance-r1)固定候选 ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf：QA 通过、N1/N2 已关闭，Human Owner 于 2026-11-04 最终验收本 CU 阶段。历史失败及原生跨进程偏好持久性未实测限制保留；API/DAA 对接和 SMA 总体完成另项。 |
| SMA-004 | qa_passed | [r1 配置独立化](plans/SMA-004-local-configuration/spec.md) | [独立 QA2](plans/SMA-004-local-configuration/checklist.md#qa2-r1)核准 53 项候选 9d514bc4c71ae3ebb0b634118c86c6f409835f5d8d933b3fab5bccc51fc93676，关闭 F-QA1-001/002/003。原生 Save As、产品真实备份/恢复及本地化控件通过，未变存储/重开/Rust 证据已核准复用；QA1 失败和证明限制保留。正常投递保持关闭，Owner 最终验收 pending。 |

实施顺序：**SMA-002 → SMA-003 → SMA-004**。前两阶段已接受，SMA-004 已通过 QA2、待 Owner 最终验收；阶段④–⑥仍仅列目标与依赖，未创建未来 bundle。子任务接受不代表 SMA 总体交付完成。

实际角色文件和待创建阶段见[任务目录](plans/README.zh-CN.md)。
