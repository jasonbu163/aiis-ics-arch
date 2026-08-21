# 变更日志

English version: [CHANGELOG.md](CHANGELOG.md)

## 1.0.0 — 源码基线

- 建立 AIIS ICS Architecture 公开源码基线。
- 将 Core 后端、JavaScript 前端、Control Agent、工具和公开合同与使用方项目工作分开。
- 将 Core migration 重建为覆盖十四张 Core 表的单一 `d4e6f8a0b2c4` root，表结构变化继续通过显式 Alembic 任务管理。
- 采用固定名称、MySQL `8.4.6`、源码 bind、一次性 migration 与 bootstrap 默认关闭的 Docker 开发栈。
- 在历史空 volume runtime 证明获接受后，从当前仓库活动入口移除已失效的一次性 Docker smoke 表面。
- 记录 manifest opt-in、route/locale 自动发现以及数据库/PLC/运行时边界。
- 将 `docs/` 建立为根 PLAN 管理的跨仓库长期指引索引，多项目指南使用其 canonical 路径，同时 `contracts/` 继续作为根目录 Core 合同中心。
- 将前端模块组装和 Control Agent 打包配置记录为独立后续工作流。

本条只记录 source-only 状态。固定版本的权威模型是同一 commit 上的 `release/<semver>` 分支与 annotated `v<semver>` tag；本次准备记录不声称这些 refs 已经发布。1.0.0 不包含托管 GitHub Release、构建产物、部署或生产就绪声明。
