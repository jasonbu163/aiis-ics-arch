# 初始化与本地验证

English version: [INITIALIZATION.md](INITIALIZATION.md)

本文件只描述安全的源码检查，不是部署手册，不要求真实凭据、PLC 连接、数据库写入或仓库发布。

## 前置条件

- 安装与 `backend/` 兼容的 Python 和 `uv`。
- 安装与 `frontend-js/` 兼容的 Node.js 和 `pnpm`。
- 安装与 `control-agent/` 兼容的 Rust/Cargo。
- 仓库中不得有已提交的 `.env`、客户输入、生成输出或真实连接地址。

## 顺序

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

只有单独获批的运行时任务才能使用项目自有的非生产环境。数据库迁移执行、Docker 生命周期、PLC 采集、打包和 Git/GitHub 操作不属于本源码基线。

## 源码开发栈

开发栈固定使用 project name `aiis-ics-arch-dev`、MySQL `8.4.6`、源码热更新、独立 migration 服务，以及默认关闭的 bootstrap profile。

```bash
cp backend/.env.docker.dev.example backend/.env.docker.dev
cp frontend-js/.env.docker.dev.example frontend-js/.env.docker.dev
# 只替换本地开发占位值；所有 bootstrap flag 保持 false。

docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml config --quiet
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml build backend frontend
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml up -d mysql
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml up migration
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml up -d backend frontend

# 可选的 default-off 证明：三个 bootstrap 用户都必须被跳过。
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml \
  --profile bootstrap run --rm bootstrap

docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml \
  down --volumes --remove-orphans
rm -f backend/.env.docker.dev frontend-js/.env.docker.dev
```

Vite `/api` proxy 会把原始路径传给 backend。健康检查使用 backend 直连 `/health`；可通过需要认证的 API 路径证明代理可达，而无需新增第二个健康路由。

## Production-shaped config/build 检查

根 Compose 从源码构建 backend/frontend，并要求外部数据库；它刻意不提供数据库、migration、bootstrap 服务或宿主机 runtime bind。

```bash
cp backend/.env.docker.prod.example backend/.env.docker.prod
# 替换本地占位值，但不要打印或提交其值。

docker compose --project-name aiis-ics-arch-release-check \
  --env-file backend/.env.docker.prod -f docker-compose.yml config --quiet
docker compose --project-name aiis-ics-arch-release-check \
  --env-file backend/.env.docker.prod -f docker-compose.yml build backend frontend

rm -f backend/.env.docker.prod
```

只有在另行获批、任务专属且可安全丢弃的外部数据库夹具存在时才可启动 release-shaped 服务；不得用真实数据库替代该夹具。
