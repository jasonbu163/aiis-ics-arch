# ARCH-DOCKER-001 Development 任务记录

Task ID: ARCH-DOCKER-001  
Revision: r1  
Status: developer_handoff  
Owner Role: Development  
Allowed Writers: Development  
Handoff: Development completed the exact r1 allowlist and self-check; fresh-context Verification must create and execute checklist.md

Task Namespace: aiis-ics-arch  
Execution Mode: agent_team_same_session  
Approved: Human Owner 于 2026-08-10 使用精确语句批准 `aiis-ics-arch::ARCH-DOCKER-001 r1`：`批准 aiis-ics-arch::ARCH-DOCKER-001 r1，按 spec 精确范围和 allowlist 开始 Development。`

## 1. 目标与边界

本轮只在 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 目标仓完成 ARCH-DOCKER-001 r1：为当前
Core 源码创建四服务 `aiis-ics-arch-smoke` Compose（`mysql`、一次性 `migration`、`backend`、
`frontend`），在全新 MySQL `8.4.6` named volume 上执行唯一 `d4e6f8a0b2c4` Core Alembic
baseline，验证 backend/frontend 构建、数据库表/revision、健康与反向代理，并在每次运行后删除
任务容器、网络、volume 和临时 env。

不触碰来源仓、项目仓、modules 仓、真实/外部数据库、真实 PLC/CA、Git/GitHub、LICENSE、release、
Redis/Celery/Worker、生产部署或 allowlist 外实现。`ARCH-MIG-001 r1` 的单 root/head 与十四表
baseline 是前置事实，不在本轮修改。

## 2. 精确 allowlist

仅允许创建或修改 ARCH-DOCKER-001 spec §5 列明路径：

- `docker-compose.smoke.yml`
- `.dockerignore`
- `.gitignore`
- `backend/Dockerfile`
- `backend/Dockerfile.dockerignore`
- `backend/.dockerignore`
- `backend/.env.docker.smoke.example`
- `frontend-js/Dockerfile`
- `frontend-js/Dockerfile.dockerignore`
- `frontend-js/.dockerignore`
- `frontend-js/nginx.conf`
- 根/backend/frontend 双语 `README.*` / `PLAN.*`，`INITIALIZATION.*`、`CODE_INDEX.md`、
  `plans/README.*`
- 本 `plans/ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md`

运行时仅可创建被忽略的 `backend/.env.docker.smoke`、精确前缀为 `aiis-ics-arch-smoke` 的 Docker
容器/网络/volume/image/build cache，以及 `/private/tmp/arch-docker-001-*` 临时证据；成功或失败
均须收尾删除。

## 3. 实施策略与顺序

1. 记录 Docker daemon、Compose、主机架构、端口与 `aiis-ics-arch-smoke` 同名容器/网络/volume 的
   只读预检；未知同名资源立即停止，不扩大清理范围。
2. 在不修改 Model/migration/settings/lock 的前提下，最小修正 backend production 镜像和 build
   context：固定 uv source、保留镜像内源码，并确保迁移镜像复用 backend image。
3. 将 frontend production 镜像收敛为固定 Node/pnpm 构建阶段加 Nginx runtime；dist 只在镜像阶段
   复制，Nginx `/api/v1/health` 代理指向 Compose `backend:8000`。
4. 创建脱敏 smoke env example、Compose 四服务、隔离网络、任务 named volume、healthcheck 和
   `depends_on` 成功条件；MySQL 不发布宿主机端口。
5. 先执行 `docker compose ... config --quiet` 与 `build backend frontend`；若静态/build 失败，
   只保留有限诊断并转入限定清理，不启动依赖服务。
6. 按 `mysql -> migration -> backend -> frontend` 顺序运行；记录 migration exit、14 表加
   `alembic_version`、revision、`/health`、容器内 `SELECT 1`、frontend 首页和反向代理响应。
7. 无论成功/失败执行 `docker compose --project-name aiis-ics-arch-smoke ... down --volumes
   --remove-orphans`，再精确检查任务容器、网络、named volume 和 env 副本均已删除。
8. 仅同步已验证 MySQL smoke 的双语稳定文档、PLAN/catalog 与 `CODE_INDEX.md`；不宣称多方言、
   生产 readiness 或发布能力。

## 4. 依赖与 stop conditions

- 依赖：`ARCH-MIG-001 r1` 保持 `owner_accepted`，active migration 仍只有
  `d4e6f8a0b2c4` root/head 与固定 14 张 Core 表。
- 需要修改 Model、Schema、API、Service、settings、pyproject/lock、frontend 业务源码、CA、tools、
  contracts 或其他 allowlist 外路径时停止并返回 PM 新 Revision。
- 同名未知 Docker 资源、真实/非空/外部数据库、无法安全归属的 volume、secret/客户数据泄露风险、
  daemon/网络/磁盘/架构限制导致无法完成真实 lifecycle，或 material scope/acceptance/allowlist
  变化时停止并将本文件标记 `dev_blocked`。

## 5. Developer self-check（执行后填写）

### 5.1 文件与配置

- [x] Compose `config --quiet` 通过且只有 mysql/migration/backend/frontend。
- [x] backend/frontend Dockerfile 与 ignore 无 `latest` runtime/build source、宿主机源码/`.venv`/
      `node_modules`/外部 dist bind mount；env example 仅占位符且默认关闭 bootstrap/mock。
- [x] 文档和索引只陈述 MySQL 8.4.6 非生产 smoke 与独立生产/license/release gates。

### 5.2 Runtime 证据

- [x] 记录命令、退出码、资源名、镜像构建、MySQL healthy、migration exit 0、14 表 + `alembic_version`
      与 `d4e6f8a0b2c4`。
- [x] 分开记录 backend `/health`、容器内 `SELECT 1`、frontend `/` 和 `/api/v1/health` 代理结果。
- [x] 记录 `down --volumes --remove-orphans` 后容器、网络、volume、真实 env 均不存在。

### 5.3 边界与 handoff

- [x] 未运行真实/外部 DB、PLC/CA、Redis/Celery/Worker、Git/GitHub、release/LICENSE 或生产动作。
- [x] 记录环境限制、有限日志摘要、失败/重试与已知风险；不输出秘密。
- [x] 完成后将本文件改为 `developer_handoff`，交给 fresh-context Verification 创建唯一
      `checklist.md`；Development self-check 不给 QA verdict 或 Human Owner final acceptance。

## 6. 实施记录与证据

### 6.1 预检与配置

- Human Owner 精确批准已记录在本文件 metadata；本轮未修改 PM `spec.md`，未预先创建 QA `checklist.md`。
- 预检命令（只读）：`uname -m` -> `arm64`；`docker --version` -> `29.6.2`；
  `docker compose version` -> `v5.3.1`；`docker context ls` -> active `desktop-linux`；
  `docker info --format ...`（经精确权限请求）-> Server `29.6.2`、overlayfs、linux、aarch64。
- `docker ps -a --filter name=aiis-ics-arch-smoke`、`docker network ls --filter name=...`、
  `docker volume ls --filter name=...` 均为空；任务镜像名 `aiis-ics-arch-smoke-backend:local` /
  `aiis-ics-arch-smoke-frontend:local` 预检均不存在。主机 `8000`/`5190` 已被 Docker Desktop 监听，
  因此使用可覆盖的 `18000`/`18080`，未发现后者监听冲突。
- Compose 静态检查：
  `docker compose --project-name aiis-ics-arch-smoke --env-file backend/.env.docker.smoke -f docker-compose.smoke.yml config --quiet`
  exit `0`；`config --services` 精确输出 `mysql`、`migration`、`backend`、`frontend`；
  `config --images` 输出两个任务镜像和 `mysql:8.4.6`。第一次 shell 变量误调用未触碰资源，固定
  project name 的重跑为上述干净结果。

### 6.2 Build 与 runtime lifecycle

- backend/frontend build 命令（固定 project/env/file）最终重跑 exit `0`；日志摘要保存在
  `/private/tmp/arch-docker-001-build-final.log`，两镜像分别成功命名为
  `aiis-ics-arch-smoke-backend:local`、`aiis-ics-arch-smoke-frontend:local`。backend 使用 Python
  digest 与 uv `0.7.8` digest；frontend 使用 Node digest、pnpm `11.11.0` 多阶段构建并把源码 dist 复制进
  Nginx。第一次 wrapper 在镜像完成后因 zsh 的只读变量 `status` 记录错误，随后缓存重跑取得 exit `0`；
  该记录不代表 build failure。
- 在最终 Dockerfile 将 uv source 固定到
  `ghcr.io/astral-sh/uv:0.7.8@sha256:0178a92d156b6f6dbe60e3b52b33b421021f46d634aa9f81f42b91445bb81cdf`
  后，`docker compose ... build backend` 再次 exit `0`；只删除新建的任务 backend 镜像，未启动 runtime，
  临时 env 随后再次核对为 `ABSENT`。
- 创建 runtime env：`cp backend/.env.docker.smoke.example backend/.env.docker.smoke`，本机用
  `openssl rand -hex` 生成一次性 JWT/DB/root 值并以 mode `0600` 写入；未回显值。验证结束后执行
  `rm -f backend/.env.docker.smoke`，并核对 `runtime_env=ABSENT`。
- `docker compose ... up -d mysql` exit `0`；资源为
  `aiis-ics-arch-smoke_smoke` network、`aiis-ics-arch-smoke_mysql_data` named volume、
  `aiis-ics-arch-smoke-mysql-1` container；MySQL `mysql:8.4.6` healthy，无宿主机数据库端口。
- MySQL 只读 schema 结果（`aiis_ics_architecture`）：共 `15` 张表，精确为
  `alembic_version` 加以下 14 张 Core 表：`control_agent_gate_tokens`、`monitor_collector_states`、
  `plc_db_block_latest_snapshots`、`plc_db_block_raw_snapshots`、`projection_mapping_audit_events`、
  `projection_mapping_bindings`、`projection_mapping_revisions`、`projection_mapping_sets`、
  `projection_runtime_audit_events`、`projection_runtime_cursors`、`sys_dict_items`、`sys_dicts`、
  `token_blacklist`、`users`。`SELECT version_num FROM alembic_version` 输出
  `d4e6f8a0b2c4`，未运行 seed/bootstrap。
- 一次性 `docker compose ... up migration` exit `0`；service
  `aiis-ics-arch-smoke-migration-1` 为 `Exited (0)`，日志仅显示 MySQLImpl、非事务 DDL 与
  `Running upgrade -> d4e6f8a0b2c4`。`up -d backend` 在 migration 成功后启动，backend health 为
  `running|healthy|0`。
- backend 进程健康：容器内 `httpx.get('http://127.0.0.1:8000/health')` -> HTTP `200`，body
  `{"status":"healthy","version":"1.0.0"}`（timestamp 未写入本记录）。数据库连通性单独验证：
  backend 容器使用 settings 连接 Compose `mysql:3306` 执行只读 `SELECT 1` -> `1`。
- frontend 初始镜像的 `localhost` healthcheck 在当前 Nginx/IPv6 行为下出现 `unhealthy`，但容器内
  `wget http://127.0.0.1/` 已返回首页 `200`；Development 仅按 allowlist 将 healthcheck 改为
  `127.0.0.1`，frontend clean rebuild exit `0` 并 force-recreate。最终
  `aiis-ics-arch-smoke-frontend-1` 为 `running|healthy|0`。
- 最终 `docker compose ps -a`：backend `Up (healthy)` 映射 `18000:8000`，frontend `Up (healthy)`
  映射 `18080:80`，mysql `Up (healthy)`（仅 `3306/tcp,33060/tcp`），migration `Exited (0)`。
- frontend 容器内只读可达性：`wget http://127.0.0.1/` -> HTTP `200`、`697` bytes、包含
  `AIIS ICS Architecture`；`wget http://127.0.0.1/api/v1/health` -> HTTP `200`，返回 backend
  `{"status":"healthy","version":"1.0.0"}`，证明 Nginx reverse proxy 到 `backend:8000`。
- 宿主机 `curl 127.0.0.1:18000/health` 与 `:18080/` 在当前 sandbox 普通网络权限下返回
  `curl: (7) Failed to connect`/HTTP `000`；Compose 端口映射已由 `ps` 静态确认，未把该沙箱限制误写为
  容器 health failure。Fresh-context Verification 应在其获准环境复核宿主发布端口。

### 6.3 精确 cleanup

- 运行 `docker compose --project-name aiis-ics-arch-smoke --env-file backend/.env.docker.smoke -f docker-compose.smoke.yml down --volumes --remove-orphans`
  exit `0`；四容器、`aiis-ics-arch-smoke_smoke` network 与 `aiis-ics-arch-smoke_mysql_data`
  volume 均移除。随后仅删除本任务镜像 `aiis-ics-arch-smoke-backend:local` /
  `aiis-ics-arch-smoke-frontend:local`，exit `0`；未执行广域 prune。
- cleanup 只读核对：精确前缀容器、网络、volume、任务镜像均 `NONE`；runtime env `ABSENT`。
- `/private/tmp/arch-docker-001-*` 仅保留有限 build/runtime/cleanup 文本摘要，不进入仓库；不含密码、
  JWT、连接串或完整日志。临时 Docker build cache 未做全局清理，以避免触碰其他项目资源。

## 7. 限制、风险与交接

- Docker daemon/socket 访问需要精确权限请求；本次仅在获批命令中操作目标 project，未访问未知资源。
- 主机 8000/5190 既有 Docker Desktop 监听，因此默认 smoke ports 为 18000/18080；当前 sandbox
  无法从宿主 curl 访问 Docker Desktop 发布端口，fresh-context Verification 需复核该外部边界。
- 首次 frontend healthcheck 的 `localhost`/IPv6 差异已在 allowlist 内改为 IPv4 loopback，并重新 build/
  recreate；这是已知环境适配，不扩大 runtime 范围。
- MySQL `mysql:8.4.6` 是本轮唯一在线方言/版本；不宣称 PostgreSQL、MSSQL、SQLite、多库或生产兼容。
- 没有执行 Alembic downgrade；本轮回滚固定为删除隔离 volume/network/containers。没有访问真实/外部/
  非空 DB，不运行 seed/bootstrap，不触碰 CA/PLC/Redis/Celery/Worker/Git/GitHub/LICENSE/release。

## 8. Developer handoff

Development self-check 已完成，状态为 `developer_handoff`。请 fresh-context Verification 重新读取完整
ARCH-DOCKER-001 r1 bundle、当前实现和本节真实证据，从无同名资源起点独立运行/复核并唯一创建
`plans/ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md`。本 Development 记录不提供 QA verdict，
不授予 Human Owner final acceptance、发布、部署、ACL、强制路由或生产权限。

## 9. Development rework after QA `qa_failed`

- Fresh-context QA 将 checklist 标记为 `qa_failed`，唯一报告原因是本 Development 曾把四个不在
  ARCH-DOCKER-001 r1 spec §5 allowlist 内的模块索引写入 `backend/PLAN.md`、
  `backend/PLAN.zh-CN.md`、`frontend-js/PLAN.md`、`frontend-js/PLAN.zh-CN.md`；本节不修改
  `checklist.md`，也不提供 QA verdict。
- 精确恢复已完成且仅触及上述四个模块 PLAN：backend 双语 PLAN 删除新增的 ARCH-DOCKER-001
  smoke 两行，并把 ARCH-MIG-001 行尾恢复为 `Empty-volume runtime proof remains deferred to
  \`ARCH-DOCKER-001\`.` / `空 volume runtime 证明仍延后到 \`ARCH-DOCKER-001\`。`；frontend-js
  双语 PLAN 删除新增的 ARCH-DOCKER-001 smoke 两行。未改同文件其他文本。
- 静态证据（只读）：
  - `rg -n 'ARCH-DOCKER-001 r1|remains a separate|仍作为独立|Development smoke built this image|Development smoke 已构建本镜像|source dist into Nginx|源码 dist 构建进 Nginx' backend/PLAN.md backend/PLAN.zh-CN.md frontend-js/PLAN.md frontend-js/PLAN.zh-CN.md` -> exit `1`，无输出，越界新增段均已移除。
  - `rg -n 'Empty-volume runtime proof remains deferred to|空 volume runtime 证明仍延后到' backend/PLAN.md backend/PLAN.zh-CN.md` -> exit `0`，仅命中 `backend/PLAN.md:12` 与 `backend/PLAN.zh-CN.md:12` 的恢复行。
  - 只读 `git diff -- backend/PLAN.md backend/PLAN.zh-CN.md frontend-js/PLAN.md frontend-js/PLAN.zh-CN.md` -> exit `129`（目标目录不是 Git worktree）；未以此命令写入任何内容，以上 `rg`/行号证据为本次静态核对依据。
- 本次 rework 未运行 Docker、未创建或清理 runtime 资源、未触及源码/镜像/Compose/运行时配置；只修改了四个越界 PLAN 的自有新增内容及本 `tasks.md`。临时 env、容器、网络、volume 的既有 Development cleanup 状态保持不变。
- 恢复后状态回到 `developer_handoff`；fresh-context Verification 必须基于当前文件重新评估并维护既有唯一
  `checklist.md`，Development 不授予 Human Owner final acceptance。
