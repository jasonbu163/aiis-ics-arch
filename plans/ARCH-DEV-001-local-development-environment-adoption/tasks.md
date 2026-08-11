# ARCH-DEV-001 本地开发环境采用与迁移追溯 — Development Record

Task ID: ARCH-DEV-001  
Revision: r2  
Status: developer_handoff  
Owner Role: Development  
Allowed Writers: Development  
Handoff: r2 lightweight_same_session 实施和 Development 自检完成；交给同一会话 checklist 做非独立事实复核，不声称 fresh-context QA

Task Namespace: aiis-ics-arch  
Execution Mode: lightweight_same_session  
Role Separation: merged_same_session  
Fresh Context: not provided  
Implemented: 2026-08-11

## 1. Human Owner 决定

Human Owner 要求本任务不启动 Agent Team，直接使用最基础的 3MD，按“先修改、再记录事实”执行。
PM 已把该决定收敛为 r2 `owner_approved`；技术 allowlist、secret 禁止回显和 Docker/Git/数据库禁止边界
保持不变。

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

首次合并 apply_patch 因一个 hunk 上下文不匹配而整体拒绝，没有半写；随后拆分为精确小 patch 后完成。
frontend 首次组合 hunk 也因旧 brand 注释间隔不匹配而整体拒绝，改为按当前文件精确 patch 后完成。

## 4. Protected / Out of Scope

- 开始前已存在的 `backend/.env.docker.smoke.example` tracked deletion 属于 Human Owner/其他工作，本任务
  未恢复、未删除、未编辑；最终 `git status` 继续如实显示该 `D` 状态；
- 未修改任何 Compose、Dockerfile、源码、migration、lockfile、测试、LICENSE 或 example env；
- 未运行 Docker `build/up/down/restart`，未连接数据库，未运行 Alembic/bootstrap/seed；
- 未执行 Git add/commit/push、branch/tag、GitHub Release；
- 未修改 Vibe、项目仓或 modules 仓。

## 5. Development Self-check

Implementation and allowed-field checks: `pass`。  
Compose static config: `pass`。  
Secret disclosure check: `pass`；证据只记录非空/非占位布尔结果。  
Independent Verification: `not provided`，这是 Human Owner 明确批准的 lightweight 3MD 限制。

项目级 governance checker 的既有 ARCH-001 duplicate-Handoff 报告作为环境/历史限制保留，不被误记为
本任务通过；它没有改变 ARCH-DEV-001 自身 metadata、env、Compose static config 或文档结果。

Development 状态为 `developer_handoff`。同一会话只可继续写 checklist 记录事实复核；不得把该记录称为
fresh-context 或独立 QA。Human Owner 后续人工启动长期 dev Compose、决定 1.0.0 发布，均是独立 gate。
