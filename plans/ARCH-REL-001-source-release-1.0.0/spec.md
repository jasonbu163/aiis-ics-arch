# ARCH-REL-001 AIIS ICS Architecture 1.0.0 源码定版与 GitHub 发布 — PM Spec

Task ID: ARCH-REL-001
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 等待 Human Owner 精确批准 r1；批准前不得修改 release 合同、创建 tasks/checklist、执行 Git/GitHub 写操作或创建版本 refs

Task Namespace: aiis-ics-arch
Classification: root
Capability: AIIS ICS Architecture 1.0.0 源码定版、版本分支/tag 与 GitHub refs 发布
Owner: architecture release management
Depends On: ARCH-001 r3 owner_accepted, ARCH-MIG-001 r1 owner_accepted, ARCH-DOCKER-001 r1 owner_accepted, ARCH-DEV-001 r4 owner_accepted
Related Task: ARCH-FE-001, CA-CONFIG-001, future MODULES-001
Target Version: 1.0.0
Acceptance Chain Reference: ARCH-REL-001 r1 approval -> Development release preparation -> Human Owner manual Git publication -> fresh-context Verification -> Human Owner final acceptance -> main-only release receipt
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner -> Development -> fresh-context QA / Verification -> Human Owner
Fresh Context: required for Verification
Created: 2026-08-11
Updated: 2026-08-11

## 1. PM 结论

本任务把当前已验收的 Architecture Core 固定为第一个公开源码版本：

- 版本分支：`release/1.0.0`；
- annotated tag：`v1.0.0`；
- 托管仓库：`https://github.com/jasonbu163/aiis-ics-arch.git`；
- `main` 继续作为后续 Core 开发线；
- 版本分支和 tag 在创建后保持固定，不在本任务中 force-update、删除或重建；
- 不复制一份源码到实体 `release/` 目录；Git branch/tag 是源码定版权威；
- 不提交运行 build 产物，不创建 GitHub Release 页面，不做生产部署。

Git/GitHub 写操作全部由 Human Owner 在本机终端手工执行。Development 只准备受控文档、检查命令和
`tasks.md`，不得代替 Human Owner 运行 `git add`、`commit`、`push`、`branch` 或 `tag`。

## 2. PM 预检事实

2026-08-11 PM 只读检查：

- 当前分支为 `main`，工作区与暂存区均干净；
- `HEAD` 与本地 remote-tracking `origin/main` 均为 `e60c0ca`，提交标题为
  `Remove obsolete Docker smoke documentation`；
- 本地仅有 `main` / `origin/main`，本地 tag 列表为空；
- remote URL 为 `https://github.com/jasonbu163/aiis-ics-arch.git`；
- 实体 `release/` 目录不存在；
- `CHANGELOG.md` / `CHANGELOG.zh-CN.md` 已有 1.0.0 source-baseline 记录，但仍声明未创建 branch/tag；
- ARCH-DEV-001 r4 已 `owner_accepted`，其 Human Owner 手工证据为 backend/frontend/mysql healthy、
  migration `Exited (0)`、backend health version `1.0.0`、frontend HTTP 200、bootstrap 六开关全关闭；
- PM 尚未通过网络独立查询 remote 的 `release/1.0.0` / `v1.0.0`；Development 在任何 Git 写操作前
  必须执行远端只读碰撞检查，无输出才可继续。

## 3. Included Scope

### 3.1 长期源码定版合同

同步以下长期文档：

- `AGENTS.md`：明确固定源码版本以 `release/<semver>` 分支和 `v<semver>` annotated tag 为准，不把源码
  复制到实体 `release/` 目录；
- `README.md` / `README.zh-CN.md`：从仓库结构移除不存在的 `release/` 目录，增加简短源码版本模型；
- `CHANGELOG.md` / `CHANGELOG.zh-CN.md`：补齐 1.0.0 的 Core migration、Docker dev、smoke retirement 和
  source-only release 边界；在 refs 尚未创建前不得写成已经发布；
- `mutil-project-pm.md`：保留迁移历史，校正当前 Git 事实与 1.0.0 手工发布/验证顺序；
- 不新增 `VERSION.md`、`RELEASE.md` 或源码快照目录，版本事实继续由 CHANGELOG + Git refs 表达。

### 3.2 PLAN 与 catalog

- 把 ARCH-DEV-001 r4 同步为 `owner_accepted`；
- 增加 ARCH-REL-001 行并随真实阶段保持 `draft -> owner_approved -> implementation_in_progress ->
  developer_handoff -> qa_passed -> owner_accepted`；
- ARCH-FE-001、CA-CONFIG-001 继续保持独立 `draft`，不并入 1.0.0；
- 1.0.0 发布完成后，PLAN 的 source baseline 可声明 branch/tag 已存在，但不得声称 GitHub Release、
  build artifact、生产部署或多数据库兼容已完成。

### 3.3 Release preparation

Development 必须先完成：

1. 读取 r1 spec 与所有依赖任务的最终 checklist；
2. 确认工作区起点仅包含 PM 已批准的 spec/index 变更；
3. 检查本地与远端均不存在 `release/1.0.0` 和 `v1.0.0`；任一存在即停止；
4. 只修改 §5 Development allowlist；
5. 运行文档、secret、Git diff、ref-name 和 release-boundary 检查；
6. 写 `tasks.md`，先保持 `implementation_in_progress`，向 Human Owner 给出精确 staging/commit/push/
   branch/tag 命令；
7. 不在 Human Owner 手工 Git 输出返回前声称 refs 已发布。

### 3.4 Human Owner 手工 Git 发布

Development handoff 中的命令必须遵循以下语义，具体显式文件列表以最终 allowlist diff 为准：

```bash
# 1. 只暂存批准文件并复核
git add <explicit-approved-paths>
git diff --cached --check
git diff --cached --name-status

# 2. 创建并推送唯一 release commit 到 main
git commit -m "chore: release AIIS ICS Architecture v1.0.0"
git push origin main

# 3. 在该精确 commit 上创建固定 branch 和 annotated tag；保持 main checkout
release_commit=$(git rev-parse HEAD)
git branch release/1.0.0 "$release_commit"
git tag -a v1.0.0 "$release_commit" -m "AIIS ICS Architecture v1.0.0"
git push origin release/1.0.0
git push origin v1.0.0
```

禁止使用 `git add .`、`git add -A`、force push、tag force、ref 删除、history rewrite 或 GitHub Release
创建命令。若任一步失败，停止并保留完整输出，不用删除/重建 refs 掩盖失败。

### 3.5 Post-publication evidence and receipt

Human Owner 返回手工输出后：

- Development 只在 `tasks.md` 记录命令、退出码、release commit OID 和已发布 refs，进入
  `developer_handoff`；
- fresh-context Verification 独立核对 local/remote `main`、`release/1.0.0`、`v1.0.0` 最终指向同一
  release commit，检查 annotated tag、工作区和公开 release 边界，只写 `checklist.md`；
- Human Owner 最终接受后，PLAN/catalog 与 checklist 的 acceptance receipt 只追加到 `main`，由 Human
  Owner 手工形成第二个纯治理提交并 push；不得移动已经固定的 release branch/tag；
- 该 main-only receipt 晚于 1.0.0 release commit 是预期行为，1.0.0 tag 不需要自我包含其 post-release
  验证结果。

## 4. Git / GitHub Authority

r1 获批后只允许 Human Owner 手工创建以下外部状态：

- `origin/main` 上一个 release preparation commit；
- `origin/release/1.0.0`；
- `origin/v1.0.0` annotated tag；
- 最终接受后的一个 main-only governance receipt commit。

不授权：GitHub Release 页面、asset 上传、branch protection/settings、PR、issue、deployment、package
registry、Actions secret、协作者/权限调整或其他仓库操作。

## 5. Exact Allowlist

PM 在 r1 获批前只允许写：

- `plans/ARCH-REL-001-source-release-1.0.0/spec.md`；
- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`。

Human Owner 批准 r1 后，Development allowlist 为：

- `AGENTS.md`；
- `README.md`；
- `README.zh-CN.md`；
- `CHANGELOG.md`；
- `CHANGELOG.zh-CN.md`；
- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `mutil-project-pm.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`；
- `plans/ARCH-REL-001-source-release-1.0.0/tasks.md`。

`developer_handoff` 后 fresh-context Verification 唯一新增写面：

- `plans/ARCH-REL-001-source-release-1.0.0/checklist.md`。

Human Owner final acceptance 后的 main-only receipt 只允许更新 PLAN/catalog pair、ARCH-REL checklist；不得
修改 1.0.0 source、release branch 或 tag。

## 6. Explicit Exclusions

- 不修改 backend、frontend-js、control-agent、tools、contracts 的源码、配置、migration、lockfile、
  Dockerfile 或 Compose；
- 不读取、打印、提交或复制任何真实 env、secret、token、证书、SQL、日志、缓存或构建产物；
- 不启动、停止、重建 Docker，不连接数据库，不运行 Alembic/bootstrap/seed，不连接 PLC/CA；
- 不创建实体 `release/` 源码目录，不生成 tar/zip、binary、image export 或安装包；
- 不实现 ARCH-FE-001、CA-CONFIG-001 或 MODULES-001；
- 不创建 GitHub Release 页面，不上传 assets，不宣称 production readiness、多数据库兼容或现场验收；
- Codex 不执行 Git/GitHub 写操作。

## 7. Stop Conditions

遇到任一条件立即停止并回报 Human Owner：

- 本地或远端 `release/1.0.0` / `v1.0.0` 已存在；
- `main` 与 `origin/main` 在发布前不一致或工作区出现 allowlist 外变更；
- 暂存列表包含真实 env、secret、build artifact、日志、数据库文件或 allowlist 外路径；
- release branch、tag peeled commit、release commit 不一致；
- GitHub 权限、网络、认证或 push 失败；
- 需要 force、删除或重写已发布 ref 才能继续；
- 文档仍声称实体 `release/` 目录或已退休 Docker smoke 是当前入口；
- fresh-context Verification 无法独立核对远端 refs。

## 8. Verification

### 8.1 Development self-check

- `git status --short --branch` 与 `git diff --name-status`；
- explicit allowlist diff audit；
- `git diff --check`；
- `git check-ignore` 证明真实 dev env 仍被忽略，禁止读取值；
- 本地/远端 branch/tag collision preflight；
- bilingual README/CHANGELOG/PLAN/catalog 对称检查；
- 文档残留扫描：实体 release 目录、已退休 Docker smoke、GitHub Release/build/production 误声明；
- Human Owner Git 输出中的命令、退出码和 commit/ref OID 记录。

### 8.2 Fresh-context Verification

- 独立读取 spec/tasks、依赖任务 accepted checklist 与最终 diff；
- 复核只触达 allowlist，真实 env/secret/build/runtime surface 未进入 Git；
- `git status`、本地 branch/tag、remote refs、annotated tag 和 peeled commit；
- 确认 `origin/main`、`origin/release/1.0.0`、`v1.0.0^{}` 在发布时指向同一 release commit；
- 确认 main-only post-release receipt 不移动 release branch/tag；
- 只写 checklist，并给出 `qa_passed|qa_failed|qa_blocked`；不得代录 Human Owner 最终接受。

## 9. Acceptance Criteria

- **AC-001**：ARCH-001、ARCH-MIG-001、ARCH-DOCKER-001、ARCH-DEV-001 的依赖 Revision 均有 Human
  Owner final acceptance，PLAN/catalog 同步 ARCH-DEV-001 r4 `owner_accepted`。
- **AC-002**：长期文档明确 Git branch/tag 是源码定版权威，不存在实体 `release/` 目录或源码复制流程。
- **AC-003**：CHANGELOG 双语准确描述 1.0.0 内容与 source-only 边界，不宣称 build/production/hosted
  GitHub Release。
- **AC-004**：发布前 `main == origin/main`、工作区干净，local/remote 目标 branch/tag 均不存在；碰撞会
  stop，不覆盖。
- **AC-005**：release commit 只包含 exact allowlist 文档/3MD，不包含源码、真实 env、secret、构建产物、
  日志、数据库或 runtime 文件。
- **AC-006**：Human Owner 手工把 release commit 推到 `origin/main`，并从同一 OID 创建/push
  `release/1.0.0` 与 annotated `v1.0.0`。
- **AC-007**：fresh-context Verification 证明 `origin/main`（发布时）、`origin/release/1.0.0` 与
  `v1.0.0^{}` 指向同一 release commit；tag annotation 正确。
- **AC-008**：没有 GitHub Release 页面、asset、build artifact、deployment、branch setting 或其他外部
  状态变更。
- **AC-009**：main 保持后续开发线；release branch/tag 创建后未被移动、删除、force 或重写。
- **AC-010**：3MD 完成 Development handoff、fresh-context verdict 与 Human Owner final acceptance；
  post-release receipt 只追加到 main，不改 1.0.0 refs。
- **AC-011**：最终本地工作区干净，main-only receipt 已由 Human Owner 手工 push，远端公开文档与 task
  状态可追溯。

## 10. Risks and Rollback

- branch/tag 名称是公开长期合同；拼写或 commit 选错会形成高成本纠偏，因此创建前必须打印并人工比对
  commit OID；
- annotated tag 的对象 OID 与 peeled commit OID 不同是正常现象，验收比较使用 `v1.0.0^{}`；
- 发布前错误可通过不提交/不 push 直接停止；
- main release commit 已 push 但 refs 尚未创建时，用新的修复提交纠偏，不 rewrite `main`；
- 任一 release ref 已 push 后，不得在本任务中删除、force 或移动。需要纠偏时停止，另开 Revision / fix
  任务并由 Human Owner 决定新版本或 ref 处理；
- dev 容器可以继续运行；本任务不依赖停止容器，也不把容器状态打包进版本。

## 11. Human Owner Approval

Pending。可复制批准语句：

`批准 aiis-ics-arch::ARCH-REL-001 r1，按 spec 精确范围和 allowlist 开始 Development；Git/GitHub 写操作继续由 Human Owner 手工执行。`
