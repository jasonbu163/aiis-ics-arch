# ARCH-001 公开架构基线去项目化与一致性恢复 — PM Spec

Task ID: ARCH-001  
Revision: r3  
Status: owner_approved  
Owner Role: PM  
Allowed Writers: PM, Human Owner  
Handoff: Human Owner approved r3; handoff to Development for the exact scope, allowlist and authorized local non-production Docker lifecycle

Task Namespace: aiis-ics-arch  
Classification: root  
Capability: 公开 Core 源码基线在手工覆盖后的去 Vibe L2、公开安全清理与 Docker 合同一致性恢复  
Owner: aiis-ics-arch repository root  
Depends On: ARCH-MIG-001, ARCH-DOCKER-001  
Related Task: ARCH-FE-001, CA-CONFIG-001  
Acceptance Chain Reference: ARCH-001 r3 PM spec -> Human Owner exact scope approval -> Development tasks.md -> developer_handoff -> fresh-context QA / Verification checklist.md -> Human Owner final acceptance  
Execution Mode: agent_team_same_session  
Created: 2026-08-08  
Updated: 2026-08-10

Revision History:

- `r1`：Human Owner 批准 manual staging；该批准不授权 Development、Docker、Git 或发布。
- `r2`：Human Owner 批准去项目化实施；Development 已交接，fresh-context Verification 因当时的 migration 与许可证门给出 `qa_blocked`。r2 的 `tasks.md` / `checklist.md` 保持旧 Revision 事实。
- `r3`：`ARCH-MIG-001 r1` 与 `ARCH-DOCKER-001 r1` 已分别获得 Human Owner 最终接受。此后 Human Owner 手工把 Vibe L2 定版的 backend、frontend-js、control-agent、两份 Compose 与 MIT `LICENSE` 再次复制/覆盖到目标仓，并要求“进行去 Vibe L2”。r3 只处理该覆盖造成的精确漂移、恢复已接受 smoke 合同并重新验证。
- `r3 approval`：Human Owner 于 2026-08-10 逐字批准 r3 的精确范围与 allowlist，并同时确认保留 MIT `LICENSE` 及 `Copyright (c) 2026 Jason Boox` ownership 文本。该批准只授权本 spec 列明的 Development 写入和本机非生产 Docker 生命周期，不授权范围外实现、真实外部 I/O、Git/GitHub、release/tag、部署或 Human Owner 最终验收。

## 1. PM 决策

`ARCH-001 r3` 是对当前目标仓的外科手术式一致性恢复，不重做 Core 提取或已接受历史：

1. `ARCH-MIG-001 r1` 的唯一 `d4e6f8a0b2c4` root/head 与十四张 Core 表保持不变；
2. `ARCH-DOCKER-001 r1` 的 disposable MySQL `8.4.6` smoke 合同保持已接受事实；当前缺失资产按该合同恢复，再做 fresh-context re-verification，不改写其已接受三文件；
3. backend `app/` 继续只保留 Core 模块，frontend-js `src/app/` 继续只保留 `system`；不得借 r3 恢复或新增项目模块；
4. 当前 `LICENSE` 仅代表 Human Owner 手工放入的 staged intent。Human Owner 对下方精确 r3 语句的批准，同时确认 MIT 与 ownership 文本；PM 不提供法律意见；
5. 只有 Human Owner 批准精确 r3 后，Development 才能写入本 spec 的 allowlist，并执行限定的本机、非生产 Docker 生命周期。

## 2. 当前只读审计事实

- `backend/app/` 仍只有 Core 边界模块；`frontend-js/src/app/` 仍只有 `system/`；active migration 仍只有已接受的 `20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py`。
- 一次性项目历史重新出现：`backend/plans/` 93 files、`frontend-js/plans/` 62 files、`control-agent/plans/` 27 files。
- 以下六个真实 runtime env 文件名存在，但 PM 未读取、未回显其内容：`backend/.env`、`backend/.env.docker.dev`、`backend/.env.docker.prod`、`frontend-js/.env`、`frontend-js/.env.docker.dev`、`control-agent/.env`。
- 三份 backend env example 仍含 `Industrial Level 2 System`、`industrial_level_2_system`、项目 page/permission 标识及默认开启的开发 bootstrap。
- `docker-compose.yml` / `docker-compose.dev.yml` 是 Vibe L2 覆盖版本，包含旧镜像、容器、network、volume 名、错误的 `frontend-next-js` 路径、浮动 `mysql:8.4`、migration 与 `ensure_admin_user` 串联、`tools/config` mount 及 fixed `container_name`。
- 已接受的 `docker-compose.smoke.yml` 与 `backend/.env.docker.smoke.example` 当前缺失，但根 README、INITIALIZATION 与 `CODE_INDEX.md` 仍引用它们。
- `backend/Dockerfile.dev` 仍使用未 pin 的 Python base 与 `ghcr.io/astral-sh/uv:latest`；production `backend/Dockerfile` / `frontend-js/Dockerfile` 仍是已固定基线，不应退化。
- `LICENSE` 当前为 MIT，ownership 行为 `Copyright (c) 2026 Jason Boox`。
- 根 PLAN 仍把 ARCH-001 记为 r2 `qa_blocked` 并把 Docker/license 写成 pending；backend PLAN 仍把已接受的 empty-volume proof 写成 deferred。

这些事实证明当前 checkout 需要恢复。r3 已获精确范围批准，但该批准不代表已经完成、可以公开或可以发布。

## 3. 精确范围与 write allowlist

Human Owner 精确批准 r3 后，Development 仅可写下列路径。所有未列路径均为只读；条件路径没有实际必要时必须保持不变。

### 3.1 Deletion-only：一次性项目历史

- `backend/plans/**`
- `frontend-js/plans/**`
- `control-agent/plans/**`

三个目录只允许从 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 删除，不允许读取任务正文后再摘抄、搬迁、归档或重建；删除前只记录路径、文件数与目标根解析结果。根 `plans/**` 不在本项范围。

### 3.2 Deletion-only：真实 runtime env

- `backend/.env`
- `backend/.env.docker.dev`
- `backend/.env.docker.prod`
- `frontend-js/.env`
- `frontend-js/.env.docker.dev`
- `control-agent/.env`

Development 与 Verification 都不得读取、打印、hash、复制或引用其内容；只核对精确文件名并删除。不得把值迁移到 example、Compose、文档、任务证据、镜像或临时日志。

### 3.3 Public-safe examples

- `backend/.env.example`
- `backend/.env.docker.dev.example`
- `backend/.env.docker.prod.example`
- `frontend-js/.env.docker.dev.example`

只允许完成以下收敛：身份改为 `AIIS ICS Architecture`，数据库示例名改为 `aiis_ics_architecture`，`ROLE_API_PERMISSIONS_JSON` 默认使用空对象或仅含已存在 Core 标识且不得含 dashboard/plan/performance/equipment/auxiliary/maintenance/quality 等项目权限，所有 bootstrap 开关默认 `False` 且密码为空或明显占位；frontend Docker dev proxy 使用 Compose `backend:8000`，mock、demo account 与 role access 注入保持默认关闭/空值。

`frontend-js/.env.example` 与 `control-agent/.env.example` 的当前 public-safe/default-off 合同只读保护；若审计出现新残留，立即停止并回 PM，不在 r3 擅自扩大。

### 3.4 Docker 合同

- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.smoke.yml`（恢复）
- `backend/.env.docker.smoke.example`（恢复）
- `backend/Dockerfile.dev`
- `frontend-js/Dockerfile.dev`
- `.gitignore`（仅在缺少本 r3 精确 env/产物忽略时最小修正）
- `.dockerignore`（同上）
- `backend/.dockerignore`（同上）
- `frontend-js/.dockerignore`（同上）
- `backend/Dockerfile.dev.dockerignore`（仅为 dev build context 最小收敛）
- `frontend-js/Dockerfile.dev.dockerignore`（仅在确有必要时创建最小 context allowlist）

固定合同：

1. `docker-compose.smoke.yml` 恢复 `ARCH-DOCKER-001 r1` 已接受的四服务 `mysql` / `migration` / `backend` / `frontend`、`mysql:8.4.6`、固定 project name `aiis-ics-arch-smoke`、空 volume、十四张 Core 表 + `alembic_version`、health/proxy 与限定 cleanup；不新增能力，也不修改 ARCH-DOCKER-001 三文件。
2. `docker-compose.dev.yml` 是专属热更新环境，固定使用 project name `aiis-ics-arch-dev` 和 `mysql:8.4.6`；路径必须是 `backend/` 与 `frontend-js/`，不得保留 Vibe 身份、fixed `container_name`、`frontend-next-js`、旧 volume/network 名或无证据的 `tools/config` mount。
3. dev schema migration 与账号 bootstrap 必须是不同服务/动作。默认启动链只允许显式 migration；bootstrap 必须使用显式 profile/命令且所有开关 default-off，不能成为 backend 启动依赖。
4. `docker-compose.yml` 只保留 production-shaped `backend` + `frontend` 外部数据库拓扑；不内置数据库，不自动 migration/bootstrap，不使用预构建 host dist、旧 runtime bind 或错误路径，不宣称真实数据库 readiness。
5. dev Dockerfiles 的 base/build source 必须固定版本与 digest，不得使用 `latest` 或浮动 major/minor；不得改项目 lock。production `backend/Dockerfile`、`frontend-js/Dockerfile`、其 production context allowlist 与 Nginx 合同为已接受只读基线，r3 不授权修改。
6. Compose 资源依赖固定 project name 形成唯一 `aiis-ics-arch-*` 前缀；不得 fixed `container_name`，不得操作或清理其他 project 资源。

### 3.5 长期事实文档与索引

- `README.md`
- `README.zh-CN.md`
- `PLAN.md`
- `PLAN.zh-CN.md`
- `INITIALIZATION.md`
- `INITIALIZATION.zh-CN.md`
- `CODE_INDEX.md`
- `plans/README.md`
- `plans/README.zh-CN.md`
- `backend/PLAN.md`
- `backend/PLAN.zh-CN.md`

只同步 r3 当前事实、恢复后的 smoke/dev/release-check 入口、已接受依赖和下一 gate。README/PLAN/INITIALIZATION 语言 pair 必须同步；`CODE_INDEX.md` 删除 nested project plans 仍存在的陈述并反映真实入口。不得把 r3 一次性范围写回 `AGENTS.md`，不得修改 ARCH-MIG-001 / ARCH-DOCKER-001 已接受三文件。

### 3.6 3MD 角色文件

- PM/Human Owner：本 `spec.md`
- Development：`plans/ARCH-001-public-architecture-baseline-extraction/tasks.md`
- QA / Verification、Human Owner：`plans/ARCH-001-public-architecture-baseline-extraction/checklist.md`

当前 `tasks.md` / `checklist.md` 的 r2 metadata 与证据继续是旧 Revision 权威事实，因此在 r3 draft 阶段会暂时与本 spec 跨 Revision。Human Owner 批准 r3 后，Development 才将 `tasks.md` 更新为 r3，并保留 r2 历史摘要；只有新的 `developer_handoff` 后，fresh-context QA / Verification 才将 `checklist.md` 更新为 r3 并保留 r2 verdict 摘要。PM 不代写二者，也不把临时跨 Revision 状态冒充完整一致。

## 4. 明确不做

- 不实现或启动 `ARCH-FE-001`、`CA-CONFIG-001`；不新增/恢复任何项目业务模块；
- 不修改 backend Model/API/Service/settings/scripts/tests/migration、frontend 业务源码、Control Agent 源码/config、tools、contracts 或 release；
- 不修改来源仓、私有项目仓、modules 仓，且不从这些仓复制更多内容；
- 不读取或回显真实 `.env` 内容；不连接真实/外部 DB、PLC、Control Agent 或生产服务；
- 不执行 Git/GitHub、branch/tag/release、CI、registry push、部署或生产动作；
- 不修改 MIT 正文或 ownership 文本，不提供法律意见；
- 不用 production Compose 连接真实外部数据库来制造 runtime proof，不把空 volume smoke 冒充生产迁移证据；
- 不创建新顶层目录，不修改 `AGENTS.md`，不使用 `backend/**`、`frontend-js/**` 或 `control-agent/**` 大口袋授权。

## 5. 获批后的执行与验证门

Development 必须加载 `aiis`、`project-governance`、`docker-expert`、`docker-project-ops`，涉及 env/数据库入口时加载 `backend-arch`，更新 `CODE_INDEX.md` 时加载 `code-document-indexer`。QA / Verification 在 fresh context 重新加载相同适用 skill；PM 不替代技术角色实施。

获批后顺序固定为：

1. Development 读取 r3、本任务 r2 两份旧角色事实、ARCH-MIG-001 与 ARCH-DOCKER-001 完整已接受 bundle，并把精确批准写入 r3 `tasks.md`；
2. 解析目标根后执行三个 nested plans 与六个真实 env 的 deletion-only 清理，不读取正文/值；
3. 脱敏 examples，收敛两份 Compose 与 dev Dockerfiles，恢复已接受 smoke 两文件；
4. 先做 public-safety、路径、身份、Compose config 与 source/build-context 静态检查；
5. 仅在 Human Owner r3 批准后执行以下本机非生产生命周期：
   - `aiis-ics-arch-smoke`：按已接受合同重新完成 empty-volume build/migrate/health/proxy/cleanup；
   - `aiis-ics-arch-dev`：使用一次性本地配置和任务资源完成 migration、backend/frontend health/proxy 与 default-off bootstrap 证明，结束后限定 cleanup；
   - `aiis-ics-arch-release-check`：production Compose 只要求 config/build；仅当能使用任务专属安全 fixture 且不改变 production topology 时才做 health/proxy，否则诚实记录未运行，绝不接真实外部 DB。
6. 每个生命周期启动前确认同名前缀资源不存在；结束时删除本任务 containers、networks、volumes、临时 env 与任务 images，不做 broad prune；未知资源立即停止；
7. 同步长期文档/index，Development 完成 self-check 后 `developer_handoff`；fresh-context QA 独立复核当前实现和至少 smoke/dev 的生命周期，给出 `qa_passed|qa_failed|qa_blocked`；Human Owner 最终验收仍单独进行。

## 6. Acceptance Criteria

| ID | 验收条件 |
| --- | --- |
| AC-001 | r3 `spec.md`、获批后的 r3 `tasks.md`、交接后的 r3 `checklist.md` 具有一致 Task ID/Revision/Execution Mode/角色 metadata；r2 历史保留且未被重写成 r3 证据。 |
| AC-002 | 根与活动配置使用 `AIIS ICS Architecture` / `aiis-ics-arch` 身份；`AGENTS.md` 未写入一次性正文。 |
| AC-003 | `backend/plans/`、`frontend-js/plans/`、`control-agent/plans/` 已 deletion-only 清除；根 `plans/` 与已接受依赖 bundle 未被删除或修改。 |
| AC-004 | 六个真实 env 精确 absent，且任务过程没有读取、hash、复制、输出或迁移其值。 |
| AC-005 | examples 为 public-safe Core-only/default-off：无旧产品/数据库名、项目 permission 集、默认启用 bootstrap、真实地址或 secret。 |
| AC-006 | `ARCH-MIG-001 r1` 仍为 owner-accepted；active migration 仍只有 `d4e6f8a0b2c4` 单 root/head 与十四张 Core 表，未回退或重做。 |
| AC-007 | backend `app/` 与 frontend-js `src/app/` 的 Core-only 模块面未扩大；未实现 ARCH-FE-001 或 CA-CONFIG-001。 |
| AC-008 | dev Compose 使用正确路径、固定 MySQL 8.4.6、无 Vibe/fixed container 名/旧 resource 名/无证据 mount；migration 与 bootstrap 分离且 bootstrap default-off。 |
| AC-009 | dev Dockerfiles 的 base/build source 已 pin 且无 `latest`；production Dockerfiles/lock 未退化或改动。 |
| AC-010 | `docker-compose.smoke.yml` 与 `backend/.env.docker.smoke.example` 按 ARCH-DOCKER-001 已接受合同恢复，并由当前 r3 fresh-context QA 重新完成 disposable smoke；不改写已接受历史。 |
| AC-011 | production Compose 精确为 source-built backend + frontend 外部 DB 拓扑，无内置 DB、自动 migration/bootstrap、旧 bind/path/identity；只完成隔离 config/build，或在安全 fixture 存在时增加 health/proxy。 |
| AC-012 | 本机 smoke/dev 的 migration、health、DB readiness、frontend/proxy、default-off 与 cleanup 证据分别记录；所有任务资源使用唯一前缀并已清除。 |
| AC-013 | Human Owner 的 r3 精确批准已同时确认保留 MIT `LICENSE` 与 `Copyright (c) 2026 Jason Boox` 文本，从而关闭 r2 的许可证决定门；文件未被 Agent 改写。 |
| AC-014 | public audit 无未解释的 Vibe L2、旧镜像/路径/resource、项目权限、真实 env、secret、客户/项目输入或生成物；保留命中必须有明确 public-safe 理由。 |
| AC-015 | 根双语 README/PLAN/INITIALIZATION、plans catalog、backend PLAN pair 与 `CODE_INDEX.md` 对 r3、已接受依赖、实际 Docker 文件和下一 gate 一致。 |
| AC-016 | 未触碰来源/项目/modules 仓，未连接真实 DB/PLC/CA，未执行 Git/GitHub、release/tag、生产部署或范围外 Docker 资源操作。 |
| AC-017 | Development 记录精确变更、命令、退出码、资源与限制；fresh-context QA 独立复核并给出正式 verdict。 |
| AC-018 | `qa_passed` 仍不等于 Human Owner final acceptance，也不授权发布、部署、Git/GitHub 或生产动作。 |

## 7. 风险、回滚与 Stop Conditions

| 风险 | 控制 |
| --- | --- |
| 删除错仓或误删根任务 | 每个 deletion-only 目标先解析为 `aiis-ics-arch` 下的精确路径；禁止变量、父目录、来源路径和 broad glob。 |
| env 泄漏 | 只检查文件存在并删除；不读、不 hash、不备份、不回显。需要配置时从脱敏 example 重新创建。 |
| 破坏已接受 migration/smoke | migration 与 production Dockerfile 保持只读；smoke 仅按 ARCH-DOCKER-001 r1 合同恢复并 re-verify。 |
| 删除未知 Docker 数据 | 固定三个 project name；只清理本任务创建且精确匹配的资源；未知同名资源停止。 |
| 把 dev/release-check 当生产证明 | 文档与证据显式区分 disposable smoke、dev hot reload、production-shaped config/build 与真实生产 gate。 |
| License 权限误判 | 只记录 Human Owner staged intent 与精确确认；不提供法律解释，不推断发布授权。 |

出现以下任一情况立即停止并回到 PM 新 Revision：

- 需要触达 allowlist 外文件、真实 env 内容、来源/私有/modules 仓或新顶层目录；
- Core module 集合、十四表集合、`d4e6f8a0b2c4`、已接受 smoke 合同或 MIT ownership 文本需要变化；
- Compose 只能靠修改 Model/settings/scripts/tests/migration/production Dockerfile/lock 或恢复项目模块才能工作；
- 需要真实/外部/非空数据库、PLC/CA、生产 secret、Git/GitHub、release 或部署；
- 发现无法安全归属的 Docker 资源、第三方资产/许可证问题或 public-safety 残留；
- scope、allowlist、risk、Acceptance Criteria 或 verification 出现实质变化。

失败回滚只允许恢复 r3 对 Compose/dev Dockerfile/example/长期文档的自有变更，并清除本任务 Docker 资源；不得恢复三个 nested project plans 或六个真实 env 到公开仓，不得从私有仓复制备份来掩盖失败。

## 8. Human Owner 精确批准门

本 spec 当前为 `owner_approved`。Human Owner 于 2026-08-10 已逐字批准：

```text
批准 aiis-ics-arch::ARCH-001 r3，按 spec 精确范围和 allowlist 开始 Development；同时确认保留 MIT LICENSE 及 Copyright (c) 2026 Jason Boox ownership 文本。
```

该批准只授权 r3 allowlist、本机非生产固定 project Docker 生命周期和 r3 Development 角色写入；不授权真实 DB/PLC/CA、Git/GitHub、release/tag、生产部署、ARCH-FE-001、CA-CONFIG-001 或 Human Owner 最终验收。Development 现在可以更新其 r3 `tasks.md` 并按本 spec 开始实施；任何 material change 仍须停止并回到 PM 新 Revision。
