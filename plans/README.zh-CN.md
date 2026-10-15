# 架构任务目录

English version: [README.md](README.md)

本目录只链接当前真实存在的角色文档。`tasks.md` 只能在 Human Owner 精确批准 PM Revision 后由 Development 创建；`checklist.md` 只能在 `developer_handoff` 后由 fresh-context Verification 创建。

| 任务 | 聚合状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| ARCH-MULTI-001 三界架构发展蓝本 | `qa_passed` | [spec.md](ARCH-MULTI-001-versioned-stack-roadmap/spec.md)；r2 文档范围已批准，保留 r1 历史 | [tasks.md](ARCH-MULTI-001-versioned-stack-roadmap/tasks.md)；双语 ROADMAP 已交付 | [checklist.md](ARCH-MULTI-001-versioned-stack-roadmap/checklist.md)；r2 独立文档 QA 通过 AC1–AC10，待 Human Owner 最终审阅 |
| ARCH-AW-001 AW Agent 工程前置初始化 | `owner_accepted` | [spec.md](ARCH-AW-001-agent-foundation/spec.md)；已批准 r1，保留定向复核澄清 | [tasks.md](ARCH-AW-001-agent-foundation/tasks.md)；工程初始化与原生启动已交付 | [checklist.md](ARCH-AW-001-agent-foundation/checklist.md)；定向独立复核通过；Human Owner 于 2026-10-14 接受 r1；本轮未追加测试 |
| ARCH-AW-002 AW 白皮书与运行原理设计 | `qa_passed` | [spec.md](ARCH-AW-002-agent-runtime-design/spec.md)；r2 文档范围 | [tasks.md](ARCH-AW-002-agent-runtime-design/tasks.md)；白皮书、详细设计及双语入口已交付 | [checklist.md](ARCH-AW-002-agent-runtime-design/checklist.md)；独立 AC1–AC11 通过；待 Human Owner 最终验收 |
| ARCH-DOCKER-002 通用 Docker 部署 | `developer_handoff` | [spec.md](ARCH-DOCKER-002-reusable-deployment/spec.md) | [tasks.md](ARCH-DOCKER-002-reusable-deployment/tasks.md)；r2 静态自检通过 | 等待独立 Verification |
| ARCH-001 公开架构基线提取 | `owner_accepted` | [spec.md](ARCH-001-public-architecture-baseline-extraction/spec.md) | [tasks.md](ARCH-001-public-architecture-baseline-extraction/tasks.md) | [checklist.md](ARCH-001-public-architecture-baseline-extraction/checklist.md)；Human Owner 已接受 r3 |
| ARCH-MIG-001 Core-only Migration Baseline | `owner_accepted` | [spec.md](ARCH-MIG-001-core-migration-baseline/spec.md) | [tasks.md](ARCH-MIG-001-core-migration-baseline/tasks.md) | [checklist.md](ARCH-MIG-001-core-migration-baseline/checklist.md)；Human Owner 已接受 r1 |
| ARCH-DOCKER-001 空 volume Docker runtime 证明 | `owner_accepted` | [spec.md](ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | [tasks.md](ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md) | [checklist.md](ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md)；Human Owner 已接受 r1 |
| ARCH-DEV-001 本地开发环境采用 | `owner_accepted` | [spec.md](ARCH-DEV-001-local-development-environment-adoption/spec.md) | [tasks.md](ARCH-DEV-001-local-development-environment-adoption/tasks.md) | [checklist.md](ARCH-DEV-001-local-development-environment-adoption/checklist.md)；Human Owner 已接受 r4 |
| ARCH-REL-001 1.0.0 源码定版 | `owner_accepted` | [spec.md](ARCH-REL-001-source-release-1.0.0/spec.md) | [tasks.md](ARCH-REL-001-source-release-1.0.0/tasks.md) 记录 r3 准备、发布证据与 §5.4 receipt handoff，并保留 superseded 的 r1/r2 Development 历史 | [checklist.md](ARCH-REL-001-source-release-1.0.0/checklist.md)；`qa_passed` 与 Human Owner final acceptance 已记录；§5.4 receipt 仍待手工追加到 main 并 push |
| ARCH-FE-001 前端模块自动组装 | `draft` | [spec.md](ARCH-FE-001-frontend-module-auto-assembly/spec.md) | 等待阻塞解除并精确批准对应 Revision | 等待 `developer_handoff` |
| ARCH-FE-002 项目前端角色权限与模块首批接入 | `owner_accepted` | [spec.md](ARCH-FE-002-project-role-access-and-module-pilot/spec.md)；r4 已获 Owner 批准 | [tasks.md](ARCH-FE-002-project-role-access-and-module-pilot/tasks.md)；r4 developer_handoff | [checklist.md](ARCH-FE-002-project-role-access-and-module-pilot/checklist.md)；r4 独立 qa_passed，保留 r2/r3 历史；Human Owner 已于 2026-10-09 接受 r4 |
| ARCH-FE-003 剩余模块 manifest 适配 | `owner_accepted` | [spec.md](ARCH-FE-003-remaining-module-manifest-adaptation/spec.md)；已批准 r2 价格页直调 API | [tasks.md](ARCH-FE-003-remaining-module-manifest-adaptation/tasks.md)；r2 已交接，模块检查/36 项测试/构建通过 | [checklist.md](ARCH-FE-003-remaining-module-manifest-adaptation/checklist.md)；保留 r1 qa_blocked 历史，r2 独立 qa_passed，Human Owner 于 2026-10-12 接受 r2，并确认 env 页面权限显示测试正常 |
| ARCH-FE-004 系统名称与小标题配置 | `owner_accepted` | [spec.md](ARCH-FE-004-system-name-env-configuration/spec.md)；r3 已获 Owner 批准 | [tasks.md](ARCH-FE-004-system-name-env-configuration/tasks.md)；r3 developer_handoff，保留 r1/r2 历史 | [checklist.md](ARCH-FE-004-system-name-env-configuration/checklist.md)；r3 独立静态复核通过，Human Owner 于 2026-10-10 最终接受；保留历史与证据 |
| ARCH-BE-001 后端角色 API 权限配置 | `qa_passed` | [spec.md](ARCH-BE-001-role-api-permissions/spec.md)；r3 格式恢复已批准 | [tasks.md](ARCH-BE-001-role-api-permissions/tasks.md)；r3 developer_handoff | [checklist.md](ARCH-BE-001-role-api-permissions/checklist.md)；保留 r1/r2 历史，r3 独立 qa_passed；待 Owner 最终验收 |
| ARCH-BE-002 能源价格 API | `owner_accepted` | [spec.md](ARCH-BE-002-energy-price-api/spec.md)；r3 已批准范围 | [tasks.md](ARCH-BE-002-energy-price-api/tasks.md)；r3 返工交接 | [checklist.md](ARCH-BE-002-energy-price-api/checklist.md)；独立 QA 通过，Human Owner 于 2026-10-13 验收；保留历史证据 |
| ARCH-BE-003 映射 Service API 试点 | `draft` | [spec.md](ARCH-BE-003-mapping-service-api-pilot/spec.md)；r2 本仓库范围及小时分析；温控粒度待定 | 未授权；待精确 r2 范围批准 | 待 developer_handoff |
| ARCH-BE-004 小时价格与按日历史 | `owner_accepted` | [spec.md](ARCH-BE-004-energy-price-hourly-history/spec.md)；获批 r2 | [tasks.md](ARCH-BE-004-energy-price-hourly-history/tasks.md)；F-001 返工交接 | [checklist.md](ARCH-BE-004-energy-price-hourly-history/checklist.md)；独立复验通过，保留首轮失败；Human Owner 于 2026-10-13 完成人工试用并接受 |
| ARCH-BE-005 后端业务模块回迁修复 | `qa_blocked` | [spec.md](ARCH-BE-005-backend-business-module-reintegration/spec.md)；r3 owner_approved，保留 r2/r1 历史 | [tasks.md](ARCH-BE-005-backend-business-module-reintegration/tasks.md)；第二次返工已交接，B 具体操作待批准 | [checklist.md](ARCH-BE-005-backend-business-module-reintegration/checklist.md)；A 独立通过 319 项测试及浏览器检查，B 与最终验收 pending，保留先前 QA 历史 |
| CA-CONFIG-001 打包配置管理 | `draft` | [spec.md](CA-CONFIG-001-packaged-configuration-management/spec.md) | 等待基线刷新并精确批准对应 Revision | 等待 `developer_handoff` |

根 [PLAN.zh-CN.md](../PLAN.zh-CN.md) 是优先级驾驶舱；范围、实施证据和独立 verdict 继续归各任务的角色权威文档。
