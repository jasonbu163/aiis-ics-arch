# AIIS ICS Architecture 计划

English version: [PLAN.md](PLAN.md)

## 当前源码基线

- 源码基线版本：`1.0.0`（只记录源码状态，不代表已经创建 tag、分支、托管 Release 或完成部署）。
- Core 表面：`backend/`、`frontend-js/`、`control-agent/`、`tools/`、`contracts/`。
- 项目业务模块和项目输入归使用方项目仓库。

## 架构工作流

| 工作流 | 状态 | 记录 | 边界 |
| --- | --- | --- | --- |
| 公开 Core 提取 | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | fresh-context Verification 通过 public-safe Core、smoke/dev/release-check 与清理审计后，Human Owner 已接受 r3 |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner 已接受单一 `d4e6f8a0b2c4` Core root 与十四表 source/static/no-DB 基线 |
| 空 volume Docker runtime 证明 | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | fresh-context Verification 通过隔离 MySQL 8.4.6 构建/迁移/健康/代理/清理证明后，Human Owner 已接受 r1 |
| 本地开发环境采用 | `qa_passed` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | lightweight 同会话字段审计与 Compose 静态解析通过且未泄露 secret；Human Owner 人工 dev runtime 与最终接受仍在独立 1.0.0 发布决定之前 |
| 前端模块组装 | `draft` | [ARCH-FE-001 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | manifest 驱动的菜单/权限组装；不并入 Core 提取 |
| CA 打包配置 | `draft` | [CA-CONFIG-001 spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | 数据库类型/地址设置与 YAML 上传界面 |

## 延后边界

ARCH-MIG-001 r1 与 ARCH-DOCKER-001 r1 均已获 Human Owner 接受。MIT license 及其中声明的 ownership 已保留，
但生产 Docker 拓扑、Git/GitHub 发布、版本分支/tag、真实 PLC/CA 操作和项目模块迁移继续作为独立 Human Owner gate。

本文件只做简短索引；详细范围、命令和证据归属各自任务三文件。
