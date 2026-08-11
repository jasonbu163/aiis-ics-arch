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
├── contracts/     # 跨运行时公开合同
├── release/       # 已批准的源码版本材料
└── plans/         # 架构决策与任务三文件
```

项目仓库使用锁定的源码版本，并按同一垂直模块约定增加自己的模块。本仓库不包含项目业务页面、PLC 点表、客户数据、真实地址、凭据或构建产物。

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

## 可丢弃 Docker smoke

`docker-compose.smoke.yml` 是单独跟踪的非生产 runtime 证明：从当前源码构建 backend/frontend，在一次性
MySQL `8.4.6` volume 上执行唯一 `d4e6f8a0b2c4` Core migration，并默认把 backend/frontend 映射到可覆盖
的 smoke 端口 `18000`/`18080`。MySQL 不发布宿主机端口；四个服务固定为 `mysql`、一次性 `migration`、
`backend`、`frontend`。

smoke 使用从 example 复制、且被忽略的 `backend/.env.docker.smoke`。运行时必须固定 project name
`aiis-ics-arch-smoke`，结束时执行 `docker compose ... down --volumes --remove-orphans` 并删除临时
env。该证明只覆盖 Core MySQL 开发路径，不代表生产 readiness、多方言兼容、版本发布或真实数据库/PLC
门槛；fresh-context Verification 与 Human Owner 验收仍是独立生命周期阶段。

## 治理入口

修改前先阅读 [AGENTS.md](AGENTS.md)。当前架构状态见 [PLAN.zh-CN.md](PLAN.zh-CN.md)，源码版本记录见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)。仓库保留 MIT [LICENSE](LICENSE) 及其中声明的 ownership；该事实不授权发布或 Release。三仓协作方案见 [mutil-project-pm.md](mutil-project-pm.md)。
