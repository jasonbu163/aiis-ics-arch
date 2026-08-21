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

`main` 是持续演进的 Core 开发线。固定源码版本使用同一精确 commit 上的 `release/<semver>` 分支与 annotated `v<semver>` tag。源码不复制到实体 `release/` 目录；源码定版也不代表已经创建托管 GitHub Release、构建产物、部署或具备生产就绪性。发布这些 Git refs 必须由单独获批的 Human Owner 手工执行。

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

## Docker 表面

`docker-compose.dev.yml` 是固定 project name 为 `aiis-ics-arch-dev` 的源码开发栈：使用 MySQL `8.4.6`，通过 backend/frontend 源码 bind 支持热更新，以一次性 migration 服务执行迁移，并把 public default 均保持关闭的 bootstrap 放在需显式启用的 `bootstrap` profile。

根 `docker-compose.yml` 是 production-shaped 的 `aiis-ics-arch-release-check` config/build 表面：从源码构建 backend/frontend，连接外部配置的数据库，不提供数据库、migration 或 bootstrap 服务，也不挂载宿主机源码、dist 或 runtime。没有单独获批且任务专属的外部数据库夹具时不得启动。

## 治理入口

修改前先阅读 [AGENTS.md](AGENTS.md)。当前架构状态见 [PLAN.zh-CN.md](PLAN.zh-CN.md)，源码版本记录见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)。仓库保留 MIT [LICENSE](LICENSE) 及其中声明的 ownership；该事实不授权发布或 Release。长期项目文档由 [docs/](docs/README.zh-CN.md) 索引，其中包括[多项目开发指南](docs/multi-project-pm.md)；根目录 `contracts/` 继续作为 Core 合同中心。
