# 架构任务目录

English version: [README.md](README.md)

本目录只链接当前真实存在的角色文档。`tasks.md` 只能在 Human Owner 精确批准 PM Revision 后由 Development 创建；`checklist.md` 只能在 `developer_handoff` 后由 fresh-context Verification 创建。

| 任务 | 聚合状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| ARCH-001 公开架构基线提取 | `developer_handoff` | [spec.md](ARCH-001-public-architecture-baseline-extraction/spec.md) | [tasks.md](ARCH-001-public-architecture-baseline-extraction/tasks.md) | 现有 [checklist.md](ARCH-001-public-architecture-baseline-extraction/checklist.md) 是历史 r2 `qa_blocked` 记录；下一步是 fresh-context r3 Verification |
| ARCH-MIG-001 Core-only Migration Baseline | `owner_accepted` | [spec.md](ARCH-MIG-001-core-migration-baseline/spec.md) | [tasks.md](ARCH-MIG-001-core-migration-baseline/tasks.md) | [checklist.md](ARCH-MIG-001-core-migration-baseline/checklist.md)；Human Owner 已接受 r1 |
| ARCH-DOCKER-001 空 volume Docker runtime 证明 | `owner_accepted` | [spec.md](ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | [tasks.md](ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md) | [checklist.md](ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md)；Human Owner 已接受 r1 |
| ARCH-FE-001 前端模块自动组装 | `draft` | [spec.md](ARCH-FE-001-frontend-module-auto-assembly/spec.md) | 等待阻塞解除并精确批准对应 Revision | 等待 `developer_handoff` |
| CA-CONFIG-001 打包配置管理 | `draft` | [spec.md](CA-CONFIG-001-packaged-configuration-management/spec.md) | 等待基线刷新并精确批准对应 Revision | 等待 `developer_handoff` |

根 [PLAN.zh-CN.md](../PLAN.zh-CN.md) 是优先级驾驶舱；范围、实施证据和独立 verdict 继续归各任务的角色权威文档。
