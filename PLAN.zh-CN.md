# AIIS ICS Architecture 计划

English version: [PLAN.md](PLAN.md)

## 当前源码基线

- 源码基线版本：`1.0.0`（annotated `v1.0.0` tag 与 `release/1.x.x` 维护分支已复核；不代表已创建托管
  Release 或完成部署）。
- 当前工作树表面：`backend/`、`frontend-js/`、`automation-world/`、`tools/`、`contracts/`；CA 已迁入 AW 并冻结，DAA/SMA 初始化状态见下方任务。
- 项目业务模块和项目输入归使用方项目仓库。

## 架构工作流

| 工作流 | 状态 | 记录 | 边界 |
| --- | --- | --- | --- |
| 三界架构发展蓝本 | `qa_passed` | [ARCH-MULTI-001 spec](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | r2 [双语 ROADMAP](ROADMAP.zh-CN.md) 已交付；独立文档 QA 通过 AC1–AC10，待 Human Owner 最终审阅；未改代码 |
| AW Agent 工程前置初始化 | `owner_accepted` | [ARCH-AW-001 spec](plans/ARCH-AW-001-agent-foundation/spec.md) | CA 已迁入并冻结，DAA/SMA 初始化并可独立启动；定向复核通过，Human Owner 于 2026-10-14 接受 r1；本轮未追加测试；UI/SQLite 后续另立任务 |
| AW 白皮书与运行原理设计 | `qa_passed` | [ARCH-AW-002 spec](plans/ARCH-AW-002-agent-runtime-design/spec.md) | r2 白皮书与详细原理设计已交付；独立文档 QA 通过 AC1–AC11；待 Human Owner 最终审阅；未改代码 |
| 通用 Docker 部署 | `developer_handoff` | [ARCH-DOCKER-002 spec](plans/ARCH-DOCKER-002-reusable-deployment/spec.md) | r2 实施完成；三份 Compose 静态检查通过，旧根入口已退下，待独立 Verification，运行验证另行批准 |
| 公开 Core 提取 | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | fresh-context Verification 通过 public-safe Core、smoke/dev/release-check 与清理审计后，Human Owner 已接受 r3 |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner 已接受单一 `d4e6f8a0b2c4` Core root 与十四表 source/static/no-DB 基线 |
| 空 volume Docker runtime 证明 | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | fresh-context Verification 通过隔离 MySQL 8.4.6 构建/迁移/健康/代理/清理证明后，Human Owner 已接受 r1 |
| 本地开发环境采用 | `owner_accepted` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | 固定名 dev runtime、后端健康/前端检查、bootstrap default-off 证明和失效 smoke 文档清理完成后，Human Owner 已接受 r4 |
| 1.0.0 源码定版 | `owner_accepted` | [ARCH-REL-001 spec](plans/ARCH-REL-001-source-release-1.0.0/spec.md) | fresh-context Verification 已通过 r3，Human Owner 已接受；§5.4 main-only governance receipt 已准备但仍待 Human Owner 手工 push |
| 前端模块组装 | `draft` | [ARCH-FE-001 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | manifest 驱动的菜单/权限组装；不并入 Core 提取 |
| 项目前端角色权限与模块首批接入 | `owner_accepted` | [ARCH-FE-002 spec](plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md) | r4 品牌、配置、启动、构建与公开浏览器检查已独立通过；保留 r2/r3 历史，Human Owner 已于 2026-10-09 接受 r4，其他模块预留 003 |
| 剩余前端模块 manifest 适配 | `owner_accepted` | [ARCH-FE-003 spec](plans/ARCH-FE-003-remaining-module-manifest-adaptation/spec.md) | r2 价格页直调 auxiliary API；模块检查、36 项测试及隔离构建独立验证通过，Human Owner 于 2026-10-12 接受 r2，并确认 env 页面权限显示测试正常；保留 r1 历史 |
| 前端系统名称与小标题配置 | `owner_accepted` | [ARCH-FE-004 spec](plans/ARCH-FE-004-system-name-env-configuration/spec.md) | r3 独立静态复核通过后，Human Owner 于 2026-10-10 反馈测试无误并接受；保留 r1/r2 历史与原始证据 |
| 后端角色 API 权限配置 | `qa_passed` | [ARCH-BE-001 spec](plans/ARCH-BE-001-role-api-permissions/spec.md) | r3 已恢复十一组英文 env 标题；配置值和逐项注释保留；独立 QA 通过；待 Human Owner 最终验收 |
| 能源价格后端 API | `owner_accepted` | [ARCH-BE-002 spec](plans/ARCH-BE-002-energy-price-api/spec.md) | r3 已批准在本仓库实施可复用 auxiliary；三个 API、独立权限与显式迁移；独立 QA 通过，Human Owner 已于 2026-10-13 验收 r3，真实数据库操作另行授权 |
| 映射 Service API 试点 | `draft` | [ARCH-BE-003 spec](plans/ARCH-BE-003-mapping-service-api-pilot/spec.md) | r2 已确定本仓库 equipment；四项业务选择已确认、小时存储分析已记录；温控存储粒度及精确范围待批准；现有 backend 映射保留 |
| 小时价格与按日历史 | `owner_accepted` | [ARCH-BE-004 spec](plans/ARCH-BE-004-energy-price-hourly-history/spec.md) | r2 独立 QA 通过：211 后端、38 前端及浏览器验证；F-001 已关闭，Human Owner 于 2026-10-13 完成人工试用并接受；真实数据迁移另行授权 |
| 后端业务模块回迁修复 | `qa_blocked` | [ARCH-BE-005 spec](plans/ARCH-BE-005-backend-business-module-reintegration/spec.md) | r3 A 独立通过：319 项源码测试及浏览器检查；B MySQL/Docker 具体操作待批准和验证，最终验收 pending |
| CA 打包配置 | `draft` | [CA-CONFIG-001 spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | 数据库类型/地址设置与 YAML 上传界面 |

## 延后边界

ARCH-MIG-001 r1、ARCH-DOCKER-001 r1 与 ARCH-DEV-001 r4 均已获 Human Owner 接受。MIT license 及其中
声明的 ownership 已保留，但生产 Docker 拓扑、真实 PLC/CA 操作和项目模块迁移继续作为独立 Human Owner
gate。ARCH-REL-001 r3 已在 fresh-context Verification 记录 `qa_passed` 且 Human Owner final acceptance
后达到 `owner_accepted`；r1/r2 Development 记录及 r2 main preparation commit 作为 superseded 历史
保留。六路径 §5.4 main-only governance receipt 已准备，但仍待 Human Owner 手工 staging、commit、
push；该状态不代表 GitHub Release、部署或 production readiness。

本文件只做简短索引；详细范围、命令和证据归属各自任务三文件。
