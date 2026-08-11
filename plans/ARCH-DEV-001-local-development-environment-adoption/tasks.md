# ARCH-DEV-001 本地开发环境采用与迁移追溯 — Development Record

Task ID: ARCH-DEV-001  
Revision: r4
Status: developer_handoff  
Owner Role: Development  
Allowed Writers: Development  
Handoff: r4 失效 smoke 活动文档清理、人工 dev runtime 事实回填和 Development 自检完成；交给同一会话 checklist 做非独立事实复核

Task Namespace: aiis-ics-arch  
Execution Mode: lightweight_same_session  
Role Separation: merged_same_session  
Fresh Context: not provided  
Implemented: 2026-08-11

## 1. Human Owner 决定

Human Owner 要求本任务不启动 Agent Team，直接使用最基础的 3MD，按“先修改、再记录事实”执行。
PM 已把执行方式收敛为 r2，并把 Human Owner 后续的固定容器名决定收敛为 r3 `owner_approved`；
secret 禁止回显和 Docker/Git/数据库禁止边界
保持不变。

Human Owner 随后要求 Codex 负责已删除 Docker smoke 的活动文档清理，并逐字批准 r4。r4 只清理五个
活动文档、记录 Human Owner 已提供的 dev runtime 输出；不重新操作 Docker，不改写历史 smoke 任务证据。

## 2. 实际修改

### 2.1 backend dev env

只在被 Git 忽略的 `backend/.env.docker.dev` 修改非秘密字段：

- 应用身份改为 AIIS ICS Architecture 1.0.0 Core backend；
- Compose MySQL 继续使用 `mysql:3306`，数据库名改为 `aiis_ics_architecture`；
- `PROJECTION_RUNNER_ENABLED` 改为默认关闭；
- admin/supervisor/operator bootstrap enable 均改为默认关闭；
- API permission JSON 清空为 `{}`；
- JWT、MySQL user password、MySQL root password 原值保留，未打印、未哈希、未写入文档。

### 2.2 frontend dev env

只在被 Git 忽略的 `frontend-js/.env.docker.dev` 修改：

- page access JSON 清空为 `{}`；
- 删除五个不属于 Architecture public example 的旧 brand logo/glow key；
- 保持 `/api/v1`、`http://backend:8000`、frontend mock off 和 demo accounts off。

### 2.3 迁移追溯和索引

- `mutil-project-pm.md` 保留原有三仓方案、提取边界和手动迁移历史，更新当前事实与执行顺序；
- 新增长期 `aiis-ics-arch-dev` 教程：env、首次启动、日常热更新、依赖/migration、可选管理员、
  stop/down/volume、HTTP 检查和进入 1.0.0 的人工 gate；
- 明确 ARCH-FE-001、CA-CONFIG-001 只在 `aiis-ics-arch/main` 开发，不再从 Vibe 定版拆分；
- 根 PLAN 与 plans catalog 修正 ARCH-001 r3 的陈旧状态并索引 ARCH-DEV-001。

### 2.4 r3 固定容器名

- `docker-compose.dev.yml` 为 mysql、migration、backend、frontend 增加 Human Owner 指定的四个固定
  `container_name`；
- bootstrap 不固定名字，继续作为 `run --rm` 临时维护容器；
- 没有修改 image、build context、Dockerfile、command、depends_on、healthcheck、port、network 或 volume；
- `mutil-project-pm.md` 补记无需 rebuild、使用不带 `--volumes` 的 down/up，以及固定名的并行/scale 限制。

### 2.5 r4 失效 smoke 活动文档清理

- `README.md` / `README.zh-CN.md` 删除已不存在的 Docker smoke 运行入口；
- `INITIALIZATION.md` / `INITIALIZATION.zh-CN.md` 删除已不存在的 smoke 初始化命令；
- `CODE_INDEX.md` 删除 `docker-compose.smoke.yml` 条目，并把 `backend/Dockerfile` 描述改为
  production-shaped release-check source build；
- `plans/` 中的历史 smoke 验证证据、`.gitignore` / `.dockerignore` 的 smoke env 防泄漏规则以及
  `backend/scripts/api_smoke/` 均保持不变；
- 已删除的 `docker-compose.smoke.yml` 与 `backend/.env.docker.smoke.example` 均未恢复。

### 2.6 Human Owner 手工 dev runtime 事实

以下结果来自 Human Owner 在宿主机终端的手工执行，不是 Codex 独立 Docker Verification：

- 固定名 `aiis-ics-arch-dev-backend`、`aiis-ics-arch-dev-frontend`、`aiis-ics-arch-dev-mysql` 均为
  `healthy`；
- `aiis-ics-arch-dev-migration` 为 `Exited (0)`；
- `curl http://127.0.0.1:8000/health` 返回 `status=healthy`、`version=1.0.0`；
- frontend `http://127.0.0.1:5190/` 返回 HTTP `200`；
- admin/supervisor/operator 的 bootstrap enable/reset 六个开关均为 `False`。

## 3. Development 自检证据

所有 env 检查只输出字段级 pass/fail 或 key name，不输出值。

| 检查 | 结果 |
| --- | --- |
| backend actual/example key set 双向 `comm -3` | exit 0，无输出，key set 一致 |
| frontend actual/example key set 双向 `comm -3` | exit 0，无输出，key set 一致 |
| 两个 env duplicate-key audit | exit 0，`duplicate_keys: pass` |
| backend Architecture identity/version/description | 全部 pass |
| backend `mysql:3306`、Core DB name、provider enablement | 全部 pass |
| backend mock/projection/bootstrap default-off、空权限 | 全部 pass |
| 三个保留 secret 非空且非 example placeholder | 全部 pass；未输出值 |
| frontend API/proxy、mock/demo default-off、空 page access | 全部 pass |
| frontend 旧 brand key absence | pass |
| `git check-ignore -v --no-index` 两个真实 env | exit 0；均由根 `.gitignore:90` 的 `.env.*` 命中 |
| `docker compose --project-name aiis-ics-arch-dev --env-file backend/.env.docker.dev -f docker-compose.dev.yml config --quiet` | exit 0，无 Compose 展开或 secret 输出 |
| 当前 `main` 与 `origin/main` baseline | 均为 `fd8e3f0875d6730b0e0c7b2b5cfe303e47afadb5`；本任务未执行 Git 动作 |
| project-governance root checker | exit 1；仅报告既有 ARCH-001 accepted checklist 含两个 `Handoff:` 标签；该文件在本任务 allowlist 外，未修改 |
| ARCH-DEV-001 三文件 metadata 人工机械核对 | Task ID/Revision/Status/Owner/Allowed Writers/Handoff/Execution Mode/Role Separation/Fresh Context 均各自一致 |
| 四个 `container_name` 静态检查 | mysql/migration/backend/frontend 精确命中各一次；bootstrap 无 `container_name` |
| r3 Compose `config --quiet` | exit 0；未输出 secret，未访问 Docker daemon lifecycle |
| rebuild 必要性 | image/Dockerfile/build context/lock 均未变；不需要 rebuild |

r4 增量自检：

| 检查 | 结果 |
| --- | --- |
| 五个活动文档 obsolete smoke 精确扫描 | `pass`；指定 Compose/env/project-name/port marker 均无命中 |
| ignore 防泄漏规则 | `pass`；根、backend、frontend ignore 规则仍保留 smoke env pattern |
| `backend/scripts/api_smoke/` | `preserved` |
| `docker-compose.smoke.yml` | `absent`；未恢复 |
| `backend/.env.docker.smoke.example` | `absent`；未恢复 |
| `git diff --check` | exit 0，无输出 |
| Docker/数据库/Git 动作 | Codex r4 未执行；只记录 Human Owner 提供的宿主机结果 |

首次合并 apply_patch 因一个 hunk 上下文不匹配而整体拒绝，没有半写；随后拆分为精确小 patch 后完成。
frontend 首次组合 hunk 也因旧 brand 注释间隔不匹配而整体拒绝，改为按当前文件精确 patch 后完成。

## 4. Protected / Out of Scope

- r4 开始前 smoke Compose/example 已由 Human Owner 清理；本轮未恢复、未编辑，也未删除历史任务证据；
- r4 未修改任何真实 env、Compose、Dockerfile、源码、migration、lockfile、测试、LICENSE 或 example env；
- Codex r4 未运行 Docker `build/up/down/restart`，未连接数据库，未运行 Alembic/bootstrap/seed；
- 未执行 Git add/commit/push、branch/tag、GitHub Release；
- 未修改 Vibe、项目仓或 modules 仓。

## 5. Development Self-check

Implementation and allowed-field checks: `pass`。  
Compose static config: `pass`。  
Secret disclosure check: `pass`；证据只记录非空/非占位布尔结果。  
Independent Verification: `not provided`，这是 Human Owner 明确批准的 lightweight 3MD 限制。

项目级 governance checker 的既有 ARCH-001 duplicate-Handoff 报告作为环境/历史限制保留，不被误记为
本任务通过；它没有改变 ARCH-DEV-001 自身 metadata、env、Compose static config 或文档结果。

Development r4 状态为 `developer_handoff`。同一会话只可继续写 checklist 记录事实复核；不得把该记录称为
fresh-context 或独立 QA。Human Owner 已提供长期 dev Compose 手工运行事实；最终接受与 1.0.0 发布决定仍是
后续独立 gate。
