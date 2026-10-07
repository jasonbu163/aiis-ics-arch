# 架构任务目录

English version: [README.md](README.md)

本目录只链接当前真实存在的角色文档。`tasks.md` 只能在 Human Owner 精确批准 PM Revision 后由 Development 创建；`checklist.md` 只能在 `developer_handoff` 后由 fresh-context Verification 创建。

| 任务 | 聚合状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| ARCH-MULTI-001 v1/v2 技术栈与多后端路线 | `draft` | [spec.md](ARCH-MULTI-001-versioned-stack-roadmap/spec.md)；已记录 Owner 路线决定 | 待细化实施任务并精确批准对应 Revision | 等待各实施任务 developer_handoff |
| ARCH-DOCKER-002 通用 Docker 部署 | `developer_handoff` | [spec.md](ARCH-DOCKER-002-reusable-deployment/spec.md) | [tasks.md](ARCH-DOCKER-002-reusable-deployment/tasks.md)；r2 静态自检通过 | 等待独立 Verification |
| ARCH-001 公开架构基线提取 | `owner_accepted` | [spec.md](ARCH-001-public-architecture-baseline-extraction/spec.md) | [tasks.md](ARCH-001-public-architecture-baseline-extraction/tasks.md) | [checklist.md](ARCH-001-public-architecture-baseline-extraction/checklist.md)；Human Owner 已接受 r3 |
| ARCH-MIG-001 Core-only Migration Baseline | `owner_accepted` | [spec.md](ARCH-MIG-001-core-migration-baseline/spec.md) | [tasks.md](ARCH-MIG-001-core-migration-baseline/tasks.md) | [checklist.md](ARCH-MIG-001-core-migration-baseline/checklist.md)；Human Owner 已接受 r1 |
| ARCH-DOCKER-001 空 volume Docker runtime 证明 | `owner_accepted` | [spec.md](ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | [tasks.md](ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md) | [checklist.md](ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md)；Human Owner 已接受 r1 |
| ARCH-DEV-001 本地开发环境采用 | `owner_accepted` | [spec.md](ARCH-DEV-001-local-development-environment-adoption/spec.md) | [tasks.md](ARCH-DEV-001-local-development-environment-adoption/tasks.md) | [checklist.md](ARCH-DEV-001-local-development-environment-adoption/checklist.md)；Human Owner 已接受 r4 |
| ARCH-REL-001 1.0.0 源码定版 | `owner_accepted` | [spec.md](ARCH-REL-001-source-release-1.0.0/spec.md) | [tasks.md](ARCH-REL-001-source-release-1.0.0/tasks.md) 记录 r3 准备、发布证据与 §5.4 receipt handoff，并保留 superseded 的 r1/r2 Development 历史 | [checklist.md](ARCH-REL-001-source-release-1.0.0/checklist.md)；`qa_passed` 与 Human Owner final acceptance 已记录；§5.4 receipt 仍待手工追加到 main 并 push |
| ARCH-FE-001 前端模块自动组装 | `draft` | [spec.md](ARCH-FE-001-frontend-module-auto-assembly/spec.md) | 等待阻塞解除并精确批准对应 Revision | 等待 `developer_handoff` |
| ARCH-FE-002 项目前端角色权限与模块首批接入 | `draft` | [spec.md](ARCH-FE-002-project-role-access-and-module-pilot/spec.md)；PM r1 草案 | 待 Owner 确认三种 env 场景与模块范围，再精确批准 Revision | 等待 `developer_handoff` |
| CA-CONFIG-001 打包配置管理 | `draft` | [spec.md](CA-CONFIG-001-packaged-configuration-management/spec.md) | 等待基线刷新并精确批准对应 Revision | 等待 `developer_handoff` |

根 [PLAN.zh-CN.md](../PLAN.zh-CN.md) 是优先级驾驶舱；范围、实施证据和独立 verdict 继续归各任务的角色权威文档。
