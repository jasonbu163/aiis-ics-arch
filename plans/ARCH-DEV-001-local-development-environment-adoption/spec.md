# ARCH-DEV-001 本地开发环境采用与迁移追溯 — PM Spec

Task ID: ARCH-DEV-001  
Revision: r2  
Status: owner_approved  
Owner Role: PM  
Allowed Writers: PM, Human Owner  
Handoff: Human Owner 已批准 r2 采用基础 3MD 的 lightweight_same_session 执行；Development 可按精确 allowlist 先实施再记录事实

Task Namespace: aiis-ics-arch  
Classification: root  
Capability: AIIS ICS Architecture 本地 Docker dev 环境采用、私密配置收敛与迁移追溯  
Owner: architecture development environment  
Depends On: ARCH-001 r3 owner_accepted, ARCH-DOCKER-001 r1 owner_accepted  
Related Task: ARCH-FE-001, CA-CONFIG-001, planned ARCH-REL-001  
Target Version: 1.0.0 pre-release development baseline；本任务不创建 release branch、tag 或 GitHub Release  
Acceptance Chain Reference: ARCH-DEV-001 PM spec -> Human Owner r2 execution-mode approval -> Development tasks.md -> same-session factual checklist.md -> Human Owner final acceptance -> separate ARCH-REL-001 decision  
Execution Mode: lightweight_same_session  
Role Separation: merged_same_session  
Fresh Context: not provided  
Created: 2026-08-11  
Updated: 2026-08-11

Revision History:

- `r1`：PM 预检固定真实 dev env 纠偏、迁移追溯文档和索引同步范围，原计划使用
  `agent_team_same_session`。
- `r2`：Human Owner 明确授权改为“最基础的 3MD”，不启动 Agent Team，并要求先修改、再记录事实。
  本任务因此使用 `lightweight_same_session`；同一会话完成 PM、Development 和 checklist 记录，明确不提供
  fresh-context 独立 QA，不把 checklist 冒充独立复核。

## 1. PM 结论

本任务把 `docker-compose.dev.yml` 采用为 `aiis-ics-arch` 后续 Core 开发的长期本地容器环境，并把本次
从旧 `vibe-l2-front-end` / 项目基线迁移到公开 Architecture 仓的最终顺序记录进
`mutil-project-pm.md`。它不是新的 Docker 架构开发，也不重新执行已经获 Human Owner 接受的
`ARCH-DOCKER-001` disposable smoke。

Human Owner 已手工把旧仓的 backend/frontend dev env 复制到 Architecture 仓。现有密码和 JWT 只要
确认为本地开发专用，就可以继续在被 Git 忽略的真实 env 中使用；Development 不擅自轮换、不打印、
不哈希、不复制到任务记录。若这些值同时用于客户、现场、生产或其他共享环境，则不得继续复用，必须
由 Human Owner 在本任务外完成独立轮换。

现有非秘密配置仍包含旧 L2 身份、项目数据库名、开启的 Projection/bootstrap、项目权限矩阵和前端
品牌变量。这些内容与公开 Architecture dev 默认边界不符，必须在首次长期启动前收敛。

## 2. Included Scope

### 2.1 backend dev env

只修改被 Git 忽略的 `backend/.env.docker.dev`：

- 保留现有非占位、非空的 `JWT_SECRET_KEY`、`MYSQL_PASSWORD`、`MYSQL_ROOT_PASSWORD`，不回显值；
- 将应用身份改为 `AIIS ICS Architecture` / `1.0.0` / Core backend 描述；
- 保持 Compose 内 MySQL 寻址为 `mysql:3306`，数据库名收敛为 `aiis_ics_architecture`；
- 保持 MySQL 为唯一启用的主库，PostgreSQL、SQLite、MSSQL 均关闭；
- `BACKEND_MOCK_ENABLED`、`PROJECTION_RUNNER_ENABLED` 与三个 bootstrap enable/reset 开关全部默认关闭；
- `ROLE_API_PERMISSIONS_JSON` 收敛为 `{}`；
- 不记录或输出任何 secret、密码、token、完整连接串或 bootstrap password。

### 2.2 frontend dev env

只修改被 Git 忽略的 `frontend-js/.env.docker.dev`：

- 保持 `/api/v1` 与 `http://backend:8000` Compose 网络合同；
- 保持 frontend mock 和 demo account 关闭；
- 将 `VITE_ROLE_PAGE_ACCESS_JSON` 收敛为 `{}`；
- 删除不在 Architecture public example 中的旧品牌 glow/logo 变量；
- 最终 key set 与 `frontend-js/.env.docker.dev.example` 一致。

### 2.3 迁移追溯文档

更新 `mutil-project-pm.md`，但保留其历史方案和迁移过程，新增或修正：

1. 当前事实：ARCH-001 r3、ARCH-MIG-001 r1、ARCH-DOCKER-001 r1 已 owner accepted，GitHub `main`
   已首次推送，`release/1.0.0` 与 `v1.0.0` 尚未创建；
2. Architecture 长期 dev Compose 的 env 准备、首次启动、日常热更新、状态/日志/HTTP 验证；
3. `stop`、`down` 与 `down --volumes` 的数据保留/删除边界；
4. Python、frontend 依赖和 Alembic migration 变化后的开发命令；
5. 后续顺序固定为 dev 人工确认 -> `ARCH-REL-001` -> `ARCH-FE-001` -> `CA-CONFIG-001` ->
   下一 Core 定版 -> `MODULES-001`；
6. `ARCH-FE-001` 和 `CA-CONFIG-001` 只在 `aiis-ics-arch/main` 开发，不再从 Vibe L2 定版继续拆分；
7. 真实 env 受 `.gitignore` 保护但仍不得作为可提交证据，文档只记录字段级纠偏，不记录值。

### 2.4 索引同步

同步根 `PLAN.md` / `PLAN.zh-CN.md` 与 `plans/README.md` / `plans/README.zh-CN.md`：

- 把已有证据明确支持的 `ARCH-001 r3` 状态从陈旧的 `developer_handoff` 修正为 `owner_accepted`；
- 增加 `ARCH-DEV-001` 当前阶段及下一 gate；
- 不改变 ARCH-FE-001 或 CA-CONFIG-001 的 draft 技术范围。

## 3. Exact Allowlist

PM 当前只允许写本 `spec.md` 和四个任务索引。Human Owner 批准 r2 后，Development allowlist 为：

- `backend/.env.docker.dev`（Git ignored，可能含 secret；禁止回显）；
- `frontend-js/.env.docker.dev`（Git ignored）；
- `mutil-project-pm.md`；
- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`；
- `plans/ARCH-DEV-001-local-development-environment-adoption/tasks.md`（Development 唯一任务记录）。

同一会话事实复核后唯一新增 checklist 写面为：

- `plans/ARCH-DEV-001-local-development-environment-adoption/checklist.md`。

## 4. Explicit Exclusions

- 不修改、恢复或删除当前用户拥有的 `backend/.env.docker.smoke.example` working-tree 删除状态；
- 不修改任何 `.env.*.example`、Compose、Dockerfile、应用源码、migration、lockfile、测试或 LICENSE；
- 不启动、停止、重建或删除 Docker container、network、volume 或 image；
- 不连接数据库，不执行 Alembic、bootstrap、seed 或业务写入；
- 不执行 Git add/commit/push、branch、tag、GitHub Release 或生产部署；
- 不修改 Vibe L2、项目仓或 modules 仓；
- 不实现 ARCH-FE-001、CA-CONFIG-001、PostgreSQL 或 MSSQL adapter；
- 不把真实 secret 写入 `mutil-project-pm.md`、tasks、checklist、日志或终端输出。

## 5. Development Verification

Development 必须在不回显 env 值的情况下记录：

1. 两个真实 env 均由根 `.gitignore` 的 `.env.*` 规则命中；
2. backend/frontend 实际 key set 与对应 example 一致；
3. 不存在重复 key；
4. backend 只输出字段级 pass/fail：Architecture 身份、`mysql:3306`、Core 数据库名、默认关闭开关、
   空权限矩阵，以及三个保留 secret 是否为非空非占位；
5. frontend 只输出字段级 pass/fail：API/proxy、mock/demo default-off、空权限矩阵、无额外品牌 key；
6. `docker compose --project-name aiis-ics-arch-dev --env-file backend/.env.docker.dev
   -f docker-compose.dev.yml config --quiet` exit `0`；禁止去掉 `--quiet`；
7. 文档中的命令与当前 Compose service、端口、volume、migration 和 bootstrap profile 一致；
8. `git diff --check` 通过，并证明 unrelated smoke-example 删除未被修改。

Development self-check 不构成 Docker runtime 通过，也不构成 release readiness。Human Owner 后续人工
启动 dev Compose 并确认稳定，仍是进入 `ARCH-REL-001` 前的独立决定。

## 6. Acceptance Criteria

- **AC-001**：两个真实 dev env 被 Git 忽略，且未向任何输出或任务文档泄露 secret。
- **AC-002**：backend dev env key set 完整、无重复，非秘密字段满足 2.1，保留的三个 secret 非空非占位。
- **AC-003**：frontend dev env key set 完整、无重复，满足 2.2，旧品牌/项目权限变量不再存在。
- **AC-004**：Compose `config --quiet` exit `0`，但未发生 Docker daemon lifecycle 或数据库动作。
- **AC-005**：`mutil-project-pm.md` 保留历史并新增可直接执行的长期 dev 教程、迁移事实和后续顺序。
- **AC-006**：FE 与 CA-CONFIG 的唯一后续开发源明确为 `aiis-ics-arch/main`；Vibe 只保留历史参考。
- **AC-007**：PLAN/catalog 与 ARCH-001 r3 owner-accepted 事实及本任务阶段一致。
- **AC-008**：allowlist 外文件未改，尤其不触碰当前 unrelated `backend/.env.docker.smoke.example` 删除。
- **AC-009**：同一会话只在 checklist 记录事实复核与 `qa_passed|qa_failed|qa_blocked`，并明确
  `Role Separation: merged_same_session`、`Fresh Context: not provided`，不冒充独立 QA。

## 7. Risks and Rollback

- 旧 MySQL password 若已经用于现有 Docker volume，擅自轮换会造成应用无法登录，因此本任务默认保留；
- 若旧 secret 不是本地 dev 专用，复用会扩大凭据影响面，Human Owner 必须独立轮换后再启动；
- 关闭 bootstrap 后空数据库没有登录账号属于预期安全默认；需要 dev 管理员时另由 Human Owner 显式启用、
  运行一次 bootstrap，再恢复关闭；
- `down --volumes` 会删除本地 MySQL、backend venv 和 frontend node_modules volumes，教程必须显著警告；
- env 回滚方式是恢复本任务前的本地备份，但备份仍不得进入 Git；tracked 文档由 Git diff 回滚。

## 8. Human Owner Approval

2026-08-11 Human Owner 原文：

`我授权调整到直接用最基础的3md执行。不用上升agent team。本来就不是一个复杂的事情。先修改，再记录事实。`

PM 将该决定收敛为 r2：保持 r1 技术 allowlist 和 secret 边界不变，只把 Execution Mode 改为
`lightweight_same_session`，允许同一会话按“实施 -> tasks 事实记录 -> checklist 非独立复核”完成。
该批准不授权 Docker lifecycle、数据库动作、Git/GitHub 发布、release branch/tag 或生产操作。
