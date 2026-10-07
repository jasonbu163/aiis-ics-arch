# 初始化与本地验证

English version: [INITIALIZATION.md](INITIALIZATION.md)

本文件包含源码检查和由操作者执行的 Docker 部署步骤。Docker 构建/启停与数据库写入须单独批准运行范围；下列命令是操作说明，不代表已经执行部署。

## 手动测试顺序

建议先按[单机部署](#单机部署)执行：准备文件/dist → 启动 database-only → 等待 MySQL healthy → 初始化表结构和应用账号 → 启动 prod → 检查首页、健康接口和登录。使用明确的测试数据库；任何命令失败都先处理再继续。

之后如需测试[完整 dev](#源码开发栈)，先用各自的 `-f` 路径对 prod、database-only 执行 `down`（不加 `-v`），再按 dev 章节启动。dev 使用独立数据库卷，不会带入 prod 创建的用户；如需测试 dev 登录，临时在 backend/.env.docker.dev 配置目标 bootstrap 用户，再执行该节 bootstrap profile 命令，完成后关闭开关。所有 Compose 命令显式指定 `-f`，不再有默认根入口。

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

# 测试后停止，保留数据库卷和运行 env 文件。
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml \
  down --remove-orphans
```

Vite `/api` proxy 会把原始路径传给 backend。健康检查使用 backend 直连 `/health`；可通过需要认证的 API 路径证明代理可达，而无需新增第二个健康路由。

## 单机部署

以下命令在仓库根目录执行；仅在运行范围获批后执行构建、启停、迁移和账号写入。Docker Desktop 使用 Linux containers；原生 Linux 的 prod 连接数据库应填写可达 DNS/IP，不假定存在 `host.docker.internal`。

| 入口 | 运行文件 | 数据库/用途 |
| --- | --- | --- |
| `docker-compose.dev.yml` | backend/frontend 的 `.env.docker.dev` | 完整热更新栈；既有独立 dev 卷 |
| `docker-compose.database-only.yml` | `backend/.env` | 仅 MySQL；独立 `aiis-ics-arch-database-only_mysql_data` 卷 |
| `docker-compose.prod.yml` | `backend/.env.docker.prod` | backend + Nginx，连接外部 MySQL |

dev 与 database-only 默认都发布 3307，dev/prod 默认都发布 8000；切换时停止冲突入口，或覆盖宿主机端口。命名前缀不隔离端口，切换模式不迁移数据，不能共享/复制 MySQL 数据目录。持久数据库停止使用 `docker compose -f docker-compose.database-only.yml down`，保留卷，不加 `-v` 或 `--volumes`。

### 准备文件与前端

模板只在首次缺少运行文件时复制，已有文件不要覆盖。macOS/Linux：

```bash
[ -f backend/.env ] || cp backend/.env.example backend/.env
[ -f backend/.env.docker.prod ] || cp backend/.env.docker.prod.example backend/.env.docker.prod
mkdir -p runtime/backend/logs
pnpm --dir frontend-js install --frozen-lockfile
VITE_API_BASE_URL=/api/v1 VITE_FRONTEND_MOCK_ENABLED=false VITE_LOGIN_DEMO_ACCOUNTS_ENABLED=false pnpm --dir frontend-js build
test -f frontend-js/dist/index.html
```

Windows PowerShell：

```powershell
if (!(Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
if (!(Test-Path backend/.env.docker.prod)) { Copy-Item backend/.env.docker.prod.example backend/.env.docker.prod }
New-Item -ItemType Directory -Force runtime/backend/logs | Out-Null
pnpm --dir frontend-js install --frozen-lockfile
$env:VITE_API_BASE_URL = '/api/v1'
$env:VITE_FRONTEND_MOCK_ENABLED = 'false'
$env:VITE_LOGIN_DEMO_ACCOUNTS_ENABLED = 'false'
pnpm --dir frontend-js build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed' }
Get-Item frontend-js/dist/index.html
```

确认每一步成功再继续。VITE 配置是公开构建值，检查本地 frontend env 中的角色页面配置是否符合部署需求，不能放密钥。Nginx 不负责构建前端；它读取 `dist`，不挂源码或 node_modules。

在 `backend/.env` 设置 MySQL 库名、应用用户及强密码、root 强密码；宿主机 backend 用 `127.0.0.1:3307`。database-only 首次空卷启动由 MySQL 镜像创建该库及应用用户，应用用户使用非 root 用户。已有卷修改 env 不会自动修改数据库账号或密码。

在 `backend/.env.docker.prod` 设置独立 JWT secret、`BACKEND_HOST=0.0.0.0`、`BACKEND_PORT=8000`、`LOG_DIR=logs`，保持 mock/Projection runner 关闭。若复用 database-only，Docker Desktop 使用 `MYSQL_HOST=host.docker.internal`、`MYSQL_PORT=3307`，库名/应用账号与数据库一致；外部 MySQL 则填写部署方可达地址及端口，并由数据库管理员预先创建库、账号和授权。不使用容器内 `localhost` 连接外部数据库。

端口覆盖使用 shell 环境变量，例如 `MYSQL_HOST_PORT`、`BACKEND_HOST_PORT`、`FRONTEND_HOST_PORT`。prod 的文件 bind 不参与 Compose 变量插值；不要仅在后端 env 写宿主机端口并期待 Compose 自动读取。

### 显式初始化与启动

以下单行命令同时适用于 Bash 和 PowerShell。外部已有 MySQL 时跳过 database-only 命令。数据库启动后用 `ps` 确认 healthy；停止并处理任何失败，不能直接继续后续写入。

```text
docker compose -f docker-compose.database-only.yml config --quiet
docker compose -f docker-compose.database-only.yml up -d mysql
docker compose -f docker-compose.database-only.yml ps
docker compose -f docker-compose.prod.yml config --quiet
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

只对获批目标执行迁移；使用 arch Core migration（当前单一 root 为 `d4e6f8a0b2c4`），不导入项目迁移历史。建表不是创建网页登录账号。

如需首次管理员，在 prod env 临时设置 `ADMIN_BOOTSTRAP_ENABLED=True`、自定 `ADMIN_BOOTSTRAP_USERNAME` 和强密码 `ADMIN_BOOTSTRAP_PASSWORD`，保持 `ADMIN_BOOTSTRAP_RESET_PASSWORD=False`，其他 bootstrap 开关关闭，再执行：

```text
docker compose -f docker-compose.prod.yml run --rm backend python main.py --maintenance bootstrap-users
```

确认 `status=created` 或预期的 `status=exists` 后，将 ENABLED 改回 False、密码清空。重置已有密码必须单独明确启用 RESET_PASSWORD，完成后关闭。应用用户写入 users 表；网页登录使用此账号，不使用 MySQL 连接账号。`*_ENABLED=False` 默认只会跳过账号创建。

```text
docker compose -f docker-compose.prod.yml up -d backend frontend
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail 50 backend frontend
```

检查 `http://127.0.0.1/`、`http://127.0.0.1:8000/health` 与 Nginx 代理 `http://127.0.0.1/api/v1/health`，再用应用账号验证登录与 `/api/v1/auth/me`；覆盖端口时同步修改访问地址。`config --quiet` 仅校验配置；healthy、代理与登录结果必须在实际运行后另行记录。

### 重启、更新与排障

- Docker Desktop 需由操作者设置随登录启动；`unless-stopped` 只作用于已创建且未手动停止的 prod 容器，不会启动 Desktop 应用。database-only 未设自动重启，Desktop 恢复后显式 `up -d mysql`，等待 healthy，再 `docker compose -f docker-compose.prod.yml up -d backend frontend`。如后端尚未恢复，数据库健康后 restart backend。`depends_on` 不保证 daemon 重启时重走 Compose 健康等待。
- prod `.env.docker.prod` 是文件 bind，普通原地内容修改后 restart backend 重新读取；编辑器原子替换文件或修改挂载时，用 `up -d --force-recreate backend` 重新绑定。dev 的 `env_file` 修改需要 `up -d --force-recreate` 对应服务，单纯 restart 不会刷新容器环境变量。数据库已有账号不随 env 自动变更。
- 后端源码或依赖变更：重新 build backend 后 `up -d backend`；前端变更：重新构建 dist 并核对 index.html 后刷新。若部署过程替换了整个 dist 目录，用 `up -d --force-recreate frontend`。保留前一份已审核 dist 于部署方备份位置，失败时恢复并重新绑定；不要把备份提交到 Git。
- bind 路径缺失：先检查 env 是文件、logs/dist 是目录，并确认 Docker Desktop 允许共享仓库目录。缺少 index.html 会明确启动失败；403 时检查文件可读性、构建是否成功，挂载目标必须与 Nginx `/usr/share/nginx/html/current` 一致。
- 数据库连接失败或代理 502：先确认 MySQL healthy、host/port 与调用位置一致，再检查 backend 日志与 health。Nginx 通过 Compose 服务名 `backend:8000` 代理；不要把项目容器名写进配置。

真实 env、日志、dist 和 runtime 均保留在忽略目录，不提交。停止 prod 使用 `docker compose -f docker-compose.prod.yml down`；回退使用上一份已审核的 prod 镜像/dist，始终保留数据库卷。
