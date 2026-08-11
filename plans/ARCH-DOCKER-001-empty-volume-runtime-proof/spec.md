# ARCH-DOCKER-001 空 volume Docker 运行证明 — PM Spec

Task ID: ARCH-DOCKER-001  
Revision: r1  
Status: owner_approved  
Owner Role: PM  
Allowed Writers: PM, Human Owner  
Handoff: Human Owner approved r1; Development may create tasks.md and execute only the exact spec allowlist

Task Namespace: aiis-ics-arch  
Classification: root  
Capability: Core 源码在隔离空 MySQL volume 上的 Docker 构建、迁移、健康与清理证明  
Owner: aiis-ics-arch runtime delivery baseline  
Acceptance Chain Reference: ARCH-DOCKER-001 r1 PM spec -> Human Owner exact scope approval -> Development tasks.md -> developer_handoff -> fresh-context QA checklist.md -> Human Owner final acceptance  
Depends On: ARCH-MIG-001  
Related Task: ARCH-001  
Execution Mode: agent_team_same_session  
Created: 2026-08-10  
Updated: 2026-08-10

Revision History:

- `r1`：在 `ARCH-MIG-001 r1` 已由 Human Owner 最终接受后建立。范围只覆盖 MySQL 非生产空库 smoke；不把 PostgreSQL、MSSQL、SQLite、生产部署、许可证或 GitHub 发布并入同一验收链。
- `r1 approval`：Human Owner 于 2026-08-10 使用精确批准语句批准 r1。该批准只授权 Development 按本 spec allowlist 创建 `tasks.md`、修改列明文件并执行隔离的 `aiis-ics-arch-smoke` Docker lifecycle；不授权范围外实现、真实/外部数据库、许可证、Git/GitHub、release、PLC/CA 或生产动作。

## 1. PM 结论

本任务为公开 Core 建立第一份真实但可丢弃的 Docker runtime 证据：从源码构建 backend 与
frontend 镜像，在全新、任务专属的 MySQL named volume 上执行唯一 Core Alembic root，确认 14 张
Core 表、backend health、backend 到数据库连通性、frontend 页面与反向代理可达，最后关闭栈并删除
任务 volume。

当前仓库没有 Compose 文件；backend/frontend Dockerfile 和脱敏 env example 已存在。当前应用默认
主库与 schema-maintenance 路径是 MySQL，`ARCH-MIG-001` 的 runtime 方言也尚未在线证明。因此 r1
只使用固定版本 MySQL 8.4 LTS 镜像，不借“依赖中存在 driver”扩展 PostgreSQL、MSSQL 或 SQLite
兼容声明。

这是一项非生产、可逆、隔离的 runtime proof，不是生产拓扑、部署指南、数据库升级方案或 release。

## 2. 前置事实与依赖

1. `ARCH-MIG-001 r1` 状态必须保持 `owner_accepted`；active migration 必须仍只有
   `d4e6f8a0b2c4`，且 `down_revision=None`。
2. 当前 backend 使用 `PRIMARY_DATABASE=mysql` / `MYSQL_ENABLED=True`，Alembic 使用同步 MySQL URL；
   FastAPI 使用 async MySQL URL。
3. backend `/health` 是进程健康端点，不查询数据库。因此本任务必须另外执行 `SELECT 1` 或等价只读
   数据库连通检查，不能用 `/health` 冒充数据库 readiness。
4. 当前 frontend production Dockerfile 只提供 Nginx runtime，并假设外部已有
   `/usr/share/nginx/html/current`。本任务允许把它最小收敛为“在目标环境从源码构建 dist，再复制到
   Nginx runtime”的可复现多阶段镜像；不提交 build 产物。
5. 当前仓库没有 `.git`，且许可证仍是 `ARCH-001` 的独立 Human Owner gate。本任务不得改变这两项事实。

## 3. 成功目标

完成后应有可重复证据证明：

1. Compose 配置只包含 `mysql`、一次性 `migration`、`backend`、`frontend` 四个服务；
2. backend 与 frontend 镜像都从当前仓库源码构建，运行时不依赖宿主机源码、`.venv`、
   `node_modules` 或预构建 `dist` bind mount；
3. MySQL 使用固定 `mysql:8.4.6` 镜像和任务专属 named volume；不发布 MySQL 宿主机端口；
4. `migration` 等待 MySQL healthy 后运行 `alembic upgrade head` 并成功退出，backend 只在 migration
   成功后启动；
5. 空库最终包含且仅包含 `alembic_version` 与 ARCH-MIG-001 固定的 14 张 Core 表，版本值为
   `d4e6f8a0b2c4`；
6. backend `/health` 返回成功，backend 容器对 MySQL 的只读 `SELECT 1` 成功；
7. frontend 首页返回 HTTP 200，且 frontend Nginx 的 `/api/v1/health` 反向代理能到达 backend；
8. `docker compose down --volumes --remove-orphans` 后，任务容器、任务网络和 named volume 均不存在；
9. 命令、退出码、镜像/容器/volume 名、表清单、日志摘要和清理结果进入 Development 与 Verification
   各自权威文档，而不是提交运行日志或数据库文件。

## 4. 精确技术范围

### 4.1 Compose 形态

Development 创建根 `docker-compose.smoke.yml`，并在所有 lifecycle 命令中固定使用 project name：

```text
aiis-ics-arch-smoke
```

服务边界固定为：

- `mysql`：`mysql:8.4.6`；仅 Compose 内网访问；一个 named volume；明确 healthcheck；
- `migration`：复用 backend 镜像；等待 MySQL healthy；只运行 `alembic upgrade head`；成功后退出 0；
- `backend`：复用 backend 镜像；等待 migration 成功；暴露容器 8000 到可覆盖的本机 smoke 端口；
- `frontend`：从 `frontend-js/` 源码构建；等待 backend healthy；暴露容器 80 到可覆盖的本机 smoke 端口。

不得加入 Control Agent、PLC、Redis、Celery、Beat、Flower、Worker、真实外部数据库、业务 seed、管理员
bootstrap、mock service、项目模块或生产 secret 管理。

### 4.2 Env 与 secret 边界

- 创建 `backend/.env.docker.smoke.example`，只保存可公开模板和明确的非生产说明；真实运行副本
  `backend/.env.docker.smoke` 必须被 Git/Docker context 忽略，并在验证后删除。
- 本地 smoke 密码/JWT 值必须是一次性非生产值，不得复用用户、项目或生产凭据；不得出现在
  `tasks.md`、`checklist.md`、Compose、Dockerfile 或命令回显中。
- Compose 内部数据库地址固定使用服务名 `mysql:3306`，不得写 `localhost`、真实 IP、
  `host.docker.internal` 或外部 DNS。
- `DEBUG=False`、`TESTING=False`、`BACKEND_MOCK_ENABLED=False`、
  `PROJECTION_RUNNER_ENABLED=False`，所有 bootstrap 开关保持关闭。

### 4.3 镜像与 build context

- backend production 镜像继续使用镜像内源码和 lock，不挂宿主机源码；仅做完成 smoke 所必需的
  Dockerfile/build-context 修正。
- frontend production 镜像使用固定 Node/pnpm 构建阶段与 Nginx runtime 阶段，dist 只在镜像阶段间
  复制，不写入仓库。
- 禁止使用 `latest` tag。若 Development 发现现有 `uv:latest` 或其他未固定 build source 会破坏
  可重复性，可在 allowlist 内最小固定版本；不得顺手升级项目依赖或 lockfile。
- `.dockerignore` 必须排除真实 env、依赖目录、缓存、日志、数据库、dump、build/dist 和 plans 任务证据；
  同时不能误排除镜像构建所需的 lock、source、Nginx 配置或 Alembic 文件。

### 4.4 Runtime 与数据库证据

Development 与 Verification 使用隔离的非生产空 volume；启动前先确认同名任务资源不存在。若存在，
不得直接删除，必须停止并确认其是否来自本任务的可恢复残留。

最少记录：

- `docker compose ... config --quiet`；
- `docker compose ... build backend frontend`；
- `docker compose ... up -d mysql`，确认 healthy；
- 运行一次性 migration 并确认 exit 0；
- 启动 backend/frontend 并记录 `docker compose ps`；
- 查询 `alembic_version`；
- 查询当前 schema 的全部 base table，精确区分 14 张 Core 表与 `alembic_version`；
- backend `/health`、backend 容器 `SELECT 1`、frontend `/` 与 frontend `/api/v1/health`；
- 仅提取失败诊断所需的有限 logs，不提交完整日志文件；
- `down --volumes --remove-orphans` 后检查容器、网络和 volume 均已清除。

本任务不要求 `alembic downgrade`：已接受的 migration downgrade 结构由 ARCH-MIG-001 的 no-DB parity
覆盖；本轮回滚面是删除整个隔离空 volume。不得把这一规则应用于任何非空或真实数据库。

## 5. Development 精确 write allowlist

Human Owner 精确批准 r1 后，Development 只允许创建或修改：

### Docker/运行配置

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

### 稳定说明与索引

- `README.md`
- `README.zh-CN.md`
- `INITIALIZATION.md`
- `INITIALIZATION.zh-CN.md`
- `backend/README.md`
- `backend/README.zh-CN.md`
- `frontend-js/README.md`
- `frontend-js/README.zh-CN.md`
- `PLAN.md`
- `PLAN.zh-CN.md`
- `plans/README.md`
- `plans/README.zh-CN.md`
- `CODE_INDEX.md`

### 3MD 角色文件

- Development：`plans/ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md`
- QA / Verification：`plans/ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md`

运行时只允许临时创建被忽略的 `backend/.env.docker.smoke`、Docker 的
`aiis-ics-arch-smoke*` 容器/网络/volume/image/build cache，以及 `/private/tmp/arch-docker-001-*`
证据缓存；成功或失败收尾均须清理 runtime 资源和真实 env 副本。不得提交这些临时对象。

PM 本 `spec.md` 只由 PM/Human Owner 维护。Development 不得修改 spec 或预先创建 checklist。若需要
触达应用源码、Model、migration、settings、pyproject/lock、frontend 业务源码、CA、tools、contracts、
release 或 allowlist 外路径，必须停止并回 PM 新 Revision。

## 6. 明确不做

- 不验证或宣称 PostgreSQL、MSSQL、SQLite、多数据库或生产 MySQL 兼容；
- 不修改 `ARCH-MIG-001` migration、Model、Schema、API、Service、settings 或 lockfile；
- 不运行任何真实、外部、已有或非空数据库，不导入/导出业务数据，不执行 seed/bootstrap；
- 不创建生产 Compose、Kubernetes、Swarm、CI/CD、registry push、镜像发布或部署自动化；
- 不启动 Control Agent，不连接 PLC，不恢复 Celery/Redis/Worker；
- 不执行 Git/GitHub、branch/tag/release，不创建 `LICENSE`，不决定许可证；
- 不实现 `ARCH-FE-001` 菜单自动组装或 `CA-CONFIG-001`；
- 不创建 `release/1.0.0`、`v1.0.0` 或任何构建产物归档；
- 不把 smoke 通过描述为生产 readiness、现场兼容或 ARCH-001 最终接受。

## 7. Development 顺序

1. 读取本 spec、ARCH-001 r2 与 ARCH-MIG-001 r1 完整 bundle；在 `tasks.md` 记录 Human Owner 精确批准。
2. 只读确认 Docker daemon、Compose 版本、主机架构、端口与任务资源冲突；存在未知同名资源时停止。
3. 按 allowlist 创建最小 smoke Compose、env example，并修正 backend/frontend production 镜像构建链。
4. 先运行静态 config/build 检查；失败时保留有限日志摘要，不继续启动依赖服务。
5. 用任务专属空 volume 按 `mysql -> migration -> backend -> frontend` 顺序完成 runtime 证明。
6. 收集表/revision、健康、连通与 reachability 证据；不得收集或输出 secret。
7. 无论成功或失败，执行限定资源的 down/volume cleanup；若自动清理失败，停止并精确报告残留名。
8. 同步双语 README/INITIALIZATION、PLAN/catalog 与 `CODE_INDEX.md` 的稳定事实，不写生产承诺。
9. 将 `tasks.md` 更新为 `developer_handoff`，由 fresh-context Verification 从空资源重新执行并创建
   `checklist.md`。

## 8. 验收标准

| ID | 验收条件 |
| --- | --- |
| AC-001 | staged 3MD、Task ID/Revision/Execution Mode、批准、allowlist 与 handoff 一致；批准前只有 PM spec。 |
| AC-002 | `ARCH-MIG-001 r1` 保持 `owner_accepted`，active migration 仍是唯一 `d4e6f8a0b2c4` root/head；未修改 migration/Model/settings/lock。 |
| AC-003 | Compose 解析通过，仅有 mysql/migration/backend/frontend；资源使用 `aiis-ics-arch-smoke` 前缀，MySQL 不发布宿主机端口，无 CA/PLC/Redis/Celery/Worker/seed/bootstrap。 |
| AC-004 | backend/frontend 镜像从当前源码和锁构建成功，runtime 不依赖宿主机源码、`.venv`、`node_modules` 或外部 dist bind mount；无 `latest` build/runtime source。 |
| AC-005 | MySQL 使用固定 `mysql:8.4.6` 与全新任务 named volume；migration 等待 DB healthy，`alembic upgrade head` exit 0，backend 只在 migration 成功后启动。 |
| AC-006 | schema 恰好包含 14 张固定 Core 表和单独的 `alembic_version`，版本值为 `d4e6f8a0b2c4`；无项目表、seed 或业务数据。 |
| AC-007 | backend `/health` 成功且容器内对 MySQL 的 `SELECT 1` 成功；两项证据分开记录。 |
| AC-008 | frontend 首页 HTTP 200，frontend `/api/v1/health` 反向代理返回 backend health；浏览器 mock/demo account 默认关闭。 |
| AC-009 | `.env.docker.smoke.example` 公开安全；真实 smoke env、密码、token、日志、数据库文件、dump、dist、cache 不进入仓库、镜像层或任务文档。 |
| AC-010 | Development 与 fresh-context Verification 均从无同名资源的起点独立完成一次 lifecycle，并记录命令、退出码、容器状态、表/revision、health/reachability 和限制。 |
| AC-011 | 每次运行结束后 `down --volumes --remove-orphans`；任务容器、网络、named volume 均不存在，env 副本已删除；未知既有资源从未被删除。 |
| AC-012 | 双语 README/INITIALIZATION、PLAN/catalog 与 `CODE_INDEX.md` 只描述已验证的 MySQL smoke 和独立 production/license/release gates；没有误报多方言或生产 readiness。 |
| AC-013 | 未触碰来源/项目/modules 仓，未运行真实 DB、Git/GitHub、release、LICENSE、PLC/CA 或生产动作。 |

## 9. 风险与控制

| 风险 | 控制 |
| --- | --- |
| 删除用户已有 Docker 数据 | 所有命令固定 project name；启动前 inspect 同名资源；只清理本任务创建且名称精确匹配的资源。未知同名资源立即停止。 |
| smoke secret 泄漏 | 只提交 example；真实副本被 Git/Docker ignore；命令和文档不回显值；收尾删除副本。 |
| health 假阳性 | `/health` 与 DB `SELECT 1` 分开验证；migration exit、表集合和 version 另行检查。 |
| frontend 只证明 Nginx 空壳 | 镜像必须从当前源码构建 dist；检查首页与 API reverse proxy。 |
| 把 MySQL smoke 当多方言/生产证明 | r1 只接受固定 MySQL 8.4 smoke；文档显式保留 production/site/provider gates。 |
| migration 失败留下脏状态 | volume 是新建且可丢弃；失败后保存有限诊断摘要并删除整套任务资源，不 stamp、不手工补表。 |
| 构建依赖网络或架构限制 | 记录 Docker/Compose/主机架构、失败层和原始错误；不改 lock/版本规避。若无法完成真实 build/runtime，QA 不得判 passed。 |

## 10. 回滚

代码回滚限于本任务 allowlist 内新增/修改的 Compose、Dockerfile、ignore 与文档；Development 在
`tasks.md` 记录精确变更。runtime 回滚固定为关闭 `aiis-ics-arch-smoke` 栈并删除本任务 named volume、
network、containers 和 env 副本。

不得对未知 volume、其他 Compose project、外部数据库或宿主机数据库执行删除。若任务资源无法安全
归属，保留现场并报告 `dev_blocked` / `qa_blocked`，不得扩大清理范围。

## 11. Stop conditions

出现任一情况立即停止：

- `ARCH-MIG-001` 不再是 owner-accepted 单 root/head，或 14 表集合发生变化；
- 同名 Docker 容器、network 或 volume 已存在且无法证明属于本任务可丢弃残留；
- 需要访问外部/真实/非空数据库，或需要删除非本任务 volume；
- migration 只能靠 stamp、create_all、手工 DDL、seed、改 Model/settings/lock 才能通过；
- 需要启用 PostgreSQL/MSSQL/SQLite、CA/PLC、Redis/Celery/Worker、生产 secret 或管理员 bootstrap；
- build/runtime 必须触达 allowlist 外代码或恢复项目模块；
- secret、客户数据、真实地址将进入源码、镜像层、日志或证据；
- Docker daemon/网络/磁盘/架构限制导致真实 lifecycle 无法完成；
- material scope、risk、allowlist、兼容性或 Acceptance Criteria 变化。

material change 必须形成 `r2` 并重新取得 Human Owner 精确批准。

## 12. Human Owner 批准门

本 spec 当前为 `owner_approved`。Human Owner 于 2026-08-10 使用以下精确语句批准 r1：

```text
批准 aiis-ics-arch::ARCH-DOCKER-001 r1，按 spec 精确范围和 allowlist 开始 Development。
```

Development 现在可以创建 `tasks.md` 并执行本任务精确限定的隔离 Docker lifecycle。即使后续
`qa_passed`，仍须 Human Owner final acceptance；该接受不授权 LICENSE、Git/GitHub、release/tag、
生产部署、真实数据库或 PLC/CA。
