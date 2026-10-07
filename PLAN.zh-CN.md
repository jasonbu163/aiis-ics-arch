# AIIS ICS Architecture 计划

English version: [PLAN.md](PLAN.md)

## 当前源码基线

- 源码基线版本：`1.0.0`（annotated `v1.0.0` tag 与 `release/1.x.x` 维护分支已复核；不代表已创建托管
  Release 或完成部署）。
- Core 表面：`backend/`、`frontend-js/`、`control-agent/`、`tools/`、`contracts/`。
- 项目业务模块和项目输入归使用方项目仓库。

## 架构工作流

| 工作流 | 状态 | 记录 | 边界 |
| --- | --- | --- | --- |
| v1/v2 技术栈与多后端路线 | `draft` | [ARCH-MULTI-001 spec](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | 已记录 Owner 方向：1.x 增加 .NET 与原生交付；2.x 默认 Rust/PostgreSQL，采用 Vue TS/Ant Design Vue；待细化实施范围与验证 |
| 通用 Docker 部署 | `developer_handoff` | [ARCH-DOCKER-002 spec](plans/ARCH-DOCKER-002-reusable-deployment/spec.md) | r2 实施完成；三份 Compose 静态检查通过，旧根入口已退下，待独立 Verification，运行验证另行批准 |
| 公开 Core 提取 | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | fresh-context Verification 通过 public-safe Core、smoke/dev/release-check 与清理审计后，Human Owner 已接受 r3 |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner 已接受单一 `d4e6f8a0b2c4` Core root 与十四表 source/static/no-DB 基线 |
| 空 volume Docker runtime 证明 | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | fresh-context Verification 通过隔离 MySQL 8.4.6 构建/迁移/健康/代理/清理证明后，Human Owner 已接受 r1 |
| 本地开发环境采用 | `owner_accepted` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | 固定名 dev runtime、后端健康/前端检查、bootstrap default-off 证明和失效 smoke 文档清理完成后，Human Owner 已接受 r4 |
| 1.0.0 源码定版 | `owner_accepted` | [ARCH-REL-001 spec](plans/ARCH-REL-001-source-release-1.0.0/spec.md) | fresh-context Verification 已通过 r3，Human Owner 已接受；§5.4 main-only governance receipt 已准备但仍待 Human Owner 手工 push |
| 前端模块组装 | `draft` | [ARCH-FE-001 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | manifest 驱动的菜单/权限组装；不并入 Core 提取 |
| 项目前端角色权限与模块首批接入 | `draft` | [ARCH-FE-002 spec](plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md) | PM r1 草案：拆分 supervisor/operator 页面授权、覆盖三种前端 env 场景并接入 dashboard/plan；待 Owner 确认 env 含义与后续模块范围 |
| CA 打包配置 | `draft` | [CA-CONFIG-001 spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | 数据库类型/地址设置与 YAML 上传界面 |

## 延后边界

ARCH-MIG-001 r1、ARCH-DOCKER-001 r1 与 ARCH-DEV-001 r4 均已获 Human Owner 接受。MIT license 及其中
声明的 ownership 已保留，但生产 Docker 拓扑、真实 PLC/CA 操作和项目模块迁移继续作为独立 Human Owner
gate。ARCH-REL-001 r3 已在 fresh-context Verification 记录 `qa_passed` 且 Human Owner final acceptance
后达到 `owner_accepted`；r1/r2 Development 记录及 r2 main preparation commit 作为 superseded 历史
保留。六路径 §5.4 main-only governance receipt 已准备，但仍待 Human Owner 手工 staging、commit、
push；该状态不代表 GitHub Release、部署或 production readiness。

本文件只做简短索引；详细范围、命令和证据归属各自任务三文件。
