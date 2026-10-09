# AIIS ICS Architecture

English version: [README.md](README.md)

AIIS ICS Architecture 是可复用工业信息系统架构的公开源码基线。仓库只保存框架代码和脱敏示例，不是客户项目，也不提交预构建运行产物。

## 仓库结构

```text
.
├── backend/       # FastAPI、SQLAlchemy、Alembic 与 Core 模块
├── frontend-js/   # Vue 3 + Vite JavaScript Core 前端
├── control-agent/ # Rust/Tauri 现场事实采集运行时
├── tools/         # 独立的项目级工具
├── contracts/     # 根目录 Core 跨运行时合同中心
├── docs/          # 跨仓库与流程类长期文档
└── plans/         # 架构决策与任务三文件
```

项目仓库使用锁定的源码版本，并按同一垂直模块约定增加自己的模块。本仓库不包含项目业务页面、PLC 点表、客户数据、真实地址、凭据或构建产物。

## 源码版本模型

`main` 是持续演进的 Core 开发线。大版本维护线使用字面分支，例如 `release/1.x.x`（未来使用
`release/2.x.x`、`release/3.x.x` 等），只能由该大版本单独获批的发布任务继续 fast-forward。每个精确
源码版本使用不可变的 annotated tag，例如 `v1.0.0`、`v1.2.1`、`v2.1.2`；tag 不由维护分支替代。源码
不复制到实体 `release/` 目录；源码定版也不代表已经创建托管 GitHub Release、构建产物、部署或具备
生产就绪性。发布这些 Git refs 必须由单独获批的 Human Owner 手工执行。

## 运行边界

```text
frontend-js -> FastAPI Core API -> 配置的数据库
PLC -> 常驻 control-agent -> raw/latest 现场事实 -> backend Projection 宿主
```

后端 Registry 只发现声明了启用 manifest 的模块。Registry 负责暴露路由和 metadata，不负责创建数据表；表结构变化必须走显式迁移任务。`control-agent` 始终是独立的运行时和交付边界。

前端 route 和 locale 自动发现属于 JavaScript 模板。完整的 manifest 菜单自动组装由 [ARCH-FE-001](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) 单独跟踪；打包后的数据库设置和 YAML 上传由 [CA-CONFIG-001](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) 单独跟踪。

## 本地验证

```bash
cd backend
uv sync
uv run python -m compileall -q app core database projection scripts tests main.py build.py
uv run pytest -q

cd ../frontend-js
pnpm install
pnpm build

cd ../control-agent
cargo fmt --check
cargo test --workspace
```

这些命令只做源码/静态验证，不启动 Docker、不修改真实数据库、不连接 PLC，也不发布版本。运行时必须使用项目自有的环境文件和获批的非生产夹具。

## 宿主机源码启动

使用 database-only + `uv run run.py` + `pnpm dev` 时，按[宿主机源码初始化教程](INITIALIZATION.zh-CN.md#宿主机源码开发与-database-only)依次迁移、显式创建登录账号、启动应用。仅开启 bootstrap 配置不会创建账号。

## Docker 表面

`docker-compose.dev.yml` 是固定 project name 为 `aiis-ics-arch-dev` 的源码开发栈：使用 MySQL `8.4.6`，通过 backend/frontend 源码 bind 支持热更新，以一次性 migration 服务执行迁移，并把 public default 均保持关闭的 bootstrap 放在需显式启用的 `bootstrap` profile。


## 治理入口

修改前先阅读 [AGENTS.md](AGENTS.md)。当前架构状态见 [PLAN.zh-CN.md](PLAN.zh-CN.md)，源码版本记录见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)。仓库保留 MIT [LICENSE](LICENSE) 及其中声明的 ownership；该事实不授权发布或 Release。长期项目文档由 [docs/](docs/README.zh-CN.md) 索引，其中包括[多项目开发指南](docs/multi-project-pm.md)；根目录 `contracts/` 继续作为 Core 合同中心。

## 单机部署

`docker-compose.database-only.yml` 提供独立 MySQL `8.4.6`，供宿主机源码或 prod 使用。`docker-compose.prod.yml` 运行镜像内源码的 backend 与 Nginx，前端只读挂载宿主机预构建的 `frontend-js/dist`；数据库位于该 Compose 项目外。当前统一使用 dev、database-only、prod 三个入口，命令必须通过 `-f` 显式选择。

环境文件、准备步骤、显式迁移、账号初始化、重启和排障见[初始化与部署说明](INITIALIZATION.zh-CN.md#单机部署)。配置校验通过不代表已完成运行部署。
