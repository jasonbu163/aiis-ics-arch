# ARCH-REL-001 AIIS ICS Architecture 1.0.0 源码定版与 GitHub 发布 — PM Spec

Task ID: ARCH-REL-001
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准当前精确 r3 spec 与 allowlist；移交 Development 按 §5.2 开始 release preparation；staging、commit、push main、创建/push release/1.x.x 与 annotated tag 仍仅由 Human Owner 手工执行

Task Namespace: aiis-ics-arch
Classification: root
Capability: AIIS ICS Architecture 1.0.0 源码定版、版本分支/tag 与 GitHub refs 发布
Owner: architecture release management
Depends On: ARCH-001 r3 owner_accepted, ARCH-MIG-001 r1 owner_accepted, ARCH-DOCKER-001 r1 owner_accepted, ARCH-DEV-001 r4 owner_accepted
Related Task: ARCH-FE-001, CA-CONFIG-001, future MODULES-001
Target Version: 1.0.0
Acceptance Chain Reference: ARCH-REL-001 r3 approval -> Development release preparation -> Human Owner manual Git publication -> Development evidence handoff -> fresh-context Verification -> Human Owner final acceptance -> main-only release receipt
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner -> Development -> fresh-context QA / Verification -> Human Owner
Fresh Context: required for Verification
Created: 2026-08-11
Updated: 2026-08-21
Required Development Skills: aiis, project-governance, code-document-indexer

## 1. PM 结论

本任务把当前已验收的 Architecture Core 固定为第一个公开源码版本，并把版本分支收敛为按大版本维护的
长期分支、按精确语义版本固定的 annotated tag：

- 持续开发线：`main`；
- 大版本维护分支：`release/1.x.x`；未来大版本按同一字面模式使用 `release/2.x.x`、
  `release/3.x.x` 等；
- annotated tag：`v1.0.0`；
- 托管仓库：`https://github.com/jasonbu163/aiis-ics-arch.git`；
- `release/1.x.x` 是 1.x 维护线，可在未来独立获批的 1.x 发布任务中正常 fast-forward；它不是
  `1.0.0` 或其他精确版本的权威；
- 精确版本只由 annotated tag 固定，例如 `v1.0.0`、`v1.2.1`、`v2.1.2`；已发布 tag 永不移动、删除
  或重建；
- 本任务首次发布时，`release/1.x.x` 与 `v1.0.0` 必须指向同一 release commit；不得创建
  `release/1.0.0`；
- 不复制一份源码到实体 `release/` 目录；Git branch/tag 是源码定版权威；
- `docs/` 作为由根 PLAN 归口的结构性支撑目录，只建立双语 README 索引/介绍；
- 跨仓长期文档的 canonical 路径为 `docs/multi-project-pm.md`；删除拼写错误的根
  `mutil-project-pm.md`，且不得创建根 `multi-project-pm.md`；
- `contracts/` 继续是根 Core contract hub，本 r3 不移动、不审计、不改写其中任何内容；
- 不提交运行 build 产物，不创建 GitHub Release 页面，不做生产部署。

Git/GitHub 写操作全部由 Human Owner 在本机终端手工执行。Development 只准备受控文档、检查命令和
`tasks.md`，不得代替 Human Owner 运行 `git add`、`commit`、`push`、`branch` 或 `tag`。r2 的
`tasks.md` 与旧 publication commands 不再是当前 ref 发布依据；r3 获批后必须由 Development 按新
allowlist 更新为 r3。

版本发布模型与 allowlist 发生 material change。r1 的范围批准、r2 approval、r2 Development 记录及
Human Owner 已推送的 main preparation commit 均保留为历史，但不再授权继续发布；当前必须先取得
Human Owner 对本 r3 的精确批准。

## 2. PM 预检事实

2026-08-21 当前基线与 Human Owner 提供的工作树事实：

- 当前 checkout 为 `main`；本地 `HEAD`、`refs/heads/main` 与 `refs/remotes/origin/main` 均为
  `f5f41550a60f439040f8c84540210cd0f2bab3aa`，与 Human Owner 已推送的远端 `main` OID 一致；
- 本地 `release/1.x.x` 与 `v1.0.0` 均不存在，Git index 为空，工作树干净；这些都是时点事实，Human
  Owner 暂存前必须重跑；
- 最近成功只读远端检查（`git ls-remote --heads --tags origin main release/1.x.x release/2.x.x
  release/1.0.0 v1.0.0`，exit `0`）只返回 `f5f41550a60f439040f8c84540210cd0f2bab3aa refs/heads/main`；
  因此远端 `release/1.x.x`、`release/2.x.x`、`release/1.0.0` 与 `v1.0.0` 当前均不存在；发布前仍必须
  重跑同一 collision preflight；
- r2 Development 已准备并由 Human Owner 推送 main preparation commit，但 r2 的 `release/1.0.0`
  与 `v1.0.0` 尚未创建；r2 `tasks.md` 及其中旧命令只保留为 superseded publication authority
  history，不是 r3 执行依据；
- `docs/README.md`、`docs/README.zh-CN.md` 与 `docs/multi-project-pm.md` 已由 r2 main preparation
  commit 形成；本 r3 只要求同步版本分支/tag 模型，不重复 r2 的 docs move；
- 根 `multi-project-pm.md`、`docs/PLAN.*` 与 `docs/plans/` 均不存在；
- ARCH-001 r3、ARCH-MIG-001 r1、ARCH-DOCKER-001 r1、ARCH-DEV-001 r4 仍为
  `owner_accepted`；accepted 历史任务中出现旧路径或旧发布模型属于历史证据，不在 r3 中改写；
- 当前不存在 `checklist.md`，没有 fresh-context QA verdict 或 Human Owner final acceptance。

## 3. Included Scope

### 3.1 大版本维护分支与精确 tag 合同

- `main` 是持续开发线；本任务首次发布的维护分支为字面名称 `release/1.x.x`；未来大版本按同一
  模式使用 `release/2.x.x`、`release/3.x.x` 等；
- `release/1.x.x` 是可移动的 1.x 维护线，只能在单独获批的 1.x 发布任务中 fast-forward；它不代表
  某个精确版本，也不能替代 annotated tag；
- 精确版本只由 annotated tag 固定，例如 `v1.0.0`、`v1.2.1`、`v2.1.2`；已发布 tag 永不移动、删除
  或重建；
- 本任务只首次创建并推送 `release/1.x.x` 与 `v1.0.0`，两者指向同一 release commit；不得创建
  `release/1.0.0`；
- 不复制源码到实体 `release/` 目录；版本 tag 不代表已创建 GitHub Release、构建产物、部署或生产
  就绪。

### 3.2 r3 稳定文档与索引同步

Human Owner 精确批准 r3 后，Development 只按 §5.2 同步当前版本发布模型：

- `AGENTS.md`、双语根 `README.*`、双语 `CHANGELOG.*` 更新为 `main`、大版本维护分支和精确 annotated
  tag 的 source-only 合同，并明确 `release/1.x.x` 可由未来获批任务 fast-forward；
- 双语 `PLAN.*`、`plans/README.*`、`docs/multi-project-pm.md` 只做当前 r3 状态、发布顺序和索引同步；
  不重复 r2 的 docs move，也不建立 `docs/PLAN.*` 或 `docs/plans/`；
- `contracts/` 仍是根 Core contract hub；本 r3 不移动、审计、重写或修改其内容；
- 不因版本模型变化修改 `CODE_INDEX.md`、源码、配置或其他不在 allowlist 的文件；不把长期文档变成第二
  copyable command/evidence truth。

### 3.3 r3 Release preparation

Human Owner 精确批准 r3 后，Development 必须：

1. 完整读取 r3 spec、r2 `tasks.md` 及其 superseded history、所有依赖任务的最终 checklist；
2. 使用 `aiis` 与 `project-governance`，只修改 §5.2 r3 Development allowlist；技术实现不属于本任务；
3. 将现有 `tasks.md` 原地升级为 `Revision: r3` / `implementation_in_progress`，保留 r2/r1 事实和旧
   publication commands 为 superseded history，不把它们当作当前 ref 发布依据；
4. 重新核对 `main`、local `origin/main` 与 remote `main` 的 OID，确认 index 为空、工作树按 allowlist
   精确变化，并确认 local/remote `release/1.x.x` 与 `v1.0.0` 均不存在；
5. 运行双语、链接、secret、Git diff、ref-name、release-boundary 与 exact allowlist 检查；任何网络、权限、
   分叉或 collision 无法可靠确认时停止；
6. 在 r3 `tasks.md` 给出唯一的 copyable Human Owner staging/commit/push/branch/tag 命令与预期输出；
7. Human Owner 完整 Git 输出返回前保持 `implementation_in_progress`，不得声称 refs 已发布。

### 3.4 Human Owner 手工 Git 发布

r3 `tasks.md` 是当前 copyable publication command 与执行证据的唯一权威。命令必须保持以下顺序：

1. 重新核对 `main == local origin/main == remote main`、Git index 为空且 local/remote `release/1.x.x`
   与 `v1.0.0` 不存在；
2. 以显式路径暂存 §5.3 的 r3 staged set，使用 `git diff --cached --name-status --no-renames` 审核；
3. 运行 cached diff/secret/path 检查后，只创建一个 release-preparation commit 并 push `main`；
4. 打印该精确 commit OID，从它创建 `release/1.x.x` 与 annotated `v1.0.0`，分别 push，并保持 checkout
   在 `main`；
5. 返回全部命令、stdout/stderr、退出码、main/maintenance-branch OID、tag object OID 与 peeled commit。

禁止 `git add .`、`git add -A`、force push/tag、ref 删除、history rewrite、创建 `release/1.0.0` 或
GitHub Release 页面。任一步失败即停止并保留输出，不通过删除、移动或重建 refs 掩盖失败。

### 3.5 Post-publication evidence、Verification 与 receipt

Human Owner 返回手工输出后：

- Development 只在 r3 `tasks.md` 记录命令、退出码、release commit OID 和已发布 refs，进入
  `developer_handoff`；r2/r1 历史继续保留但不覆盖 r3 当前事实；
- fresh-context Verification 独立核对 local/remote `main`、`release/1.x.x`、`v1.0.0` 最终指向同一
  release commit，检查 annotated tag、维护分支语义、路径/文档/contract 边界和公开 release 边界，只写
  `checklist.md`；
- QA verdict 后由 Human Owner 作最终接受决定；`qa_passed` 不等于 final acceptance；
- Human Owner 最终接受后，由 Human Owner 手工把 §5.4 main-only receipt allowlist 形成第二个纯治理提交
  并 push 到 `main`；不得移动已发布 tag，也不得在本任务中 fast-forward `release/1.x.x`；
- 该 main-only receipt 晚于 1.0.0 release commit 是预期行为，`v1.0.0` 不需要自我包含其 post-release
  验证结果。

## 4. Git / GitHub Authority

r3 获批只启动 Development release preparation，不授予 Development、PM、Verification 或协调 Agent
任何 Git/GitHub 写权限。只允许 Human Owner 手工创建以下外部状态：

- `origin/main` 上一个 release preparation commit；
- `origin/release/1.x.x`，作为 1.x 大版本维护线的初始 ref；
- `origin/v1.0.0` annotated tag，作为精确 1.0.0 版本 ref；
- 最终接受后的一个 main-only governance receipt commit。

`release/1.x.x` 在本次首次创建后可由未来单独获批的 1.x 发布任务 fast-forward；该分支不是精确版本
权威。任何已发布 annotated tag（包括 `v1.0.0`）均不得移动、删除、重建或 force-update；本任务不创建
`release/1.0.0`，也不创建 `release/2.x.x`。

不授权：GitHub Release 页面、asset 上传、branch protection/settings、PR、issue、deployment、package
registry、Actions secret、协作者/权限调整或其他仓库操作。

## 5. Exact Allowlist

### 5.1 r3 精确批准前

PM 与主协调只允许写以下范围；本 PM role 实际只写 `spec.md`，不提前同步 PLAN/catalog：

- `plans/ARCH-REL-001-source-release-1.0.0/spec.md`；

当前 r2 `tasks.md` 必须保持 untouched。r3 批准前不得更新 `tasks.md`、PLAN/catalog、README、AGENTS、
CHANGELOG、新建 `checklist.md`、暂存文件或执行任何 Git/GitHub 写操作。

### 5.2 r3 Development allowlist

Human Owner 精确批准 r3 后，Development 只允许写：

- `AGENTS.md`；
- `README.md`；
- `README.zh-CN.md`；
- `CHANGELOG.md`；
- `CHANGELOG.zh-CN.md`；
- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `docs/multi-project-pm.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`；
- `plans/ARCH-REL-001-source-release-1.0.0/tasks.md`。

本次没有结构变化，`CODE_INDEX.md`、现有 `docs/README.*`、`contracts/`、accepted 历史 task bundle、根
`multi-project-pm.md`、`docs/PLAN.*` 与 `docs/plans/` 不在 Development allowlist。`spec.md` 仍是
PM-owned 文件，只有其现有 r3 diff 作为 staged set 的第十二个路径。

### 5.3 Human Owner r3 release-preparation staged set

第一个 main release-preparation commit 必须精确包含以下十二个路径事实：

- §5.2 的十一项 Development 写面；
- PM-owned `plans/ARCH-REL-001-source-release-1.0.0/spec.md` r3 diff。

Human Owner 的 copyable `git add -- <explicit paths>` 只能由 r3 `tasks.md` 给出。cached 审核必须使用
`--no-renames` 比较路径集合，且不得出现 `release/1.0.0`、根 `multi-project-pm.md`、`contracts/`、
accepted history 或其他 allowlist 外路径。

### 5.4 Verification 与 main-only receipt

`developer_handoff` 后 fresh-context Verification 唯一新增写面：

- `plans/ARCH-REL-001-source-release-1.0.0/checklist.md`。

Human Owner final acceptance 后的 main-only receipt 只允许包含：

- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`；
- `plans/ARCH-REL-001-source-release-1.0.0/tasks.md`；
- `plans/ARCH-REL-001-source-release-1.0.0/checklist.md`。

receipt 只追加到 `main`，不得修改 `v1.0.0`、移动已发布 tag、在本任务中 fast-forward `release/1.x.x`
或夹带其他路径。任何实质 scope、acceptance、risk、Execution Mode 或 allowlist 变化都必须停止并建立
新 Revision。

## 6. Explicit Exclusions

- 不修改 backend、frontend-js、control-agent、tools 的源码、配置、migration、lockfile、Dockerfile 或
  Compose；
- 不移动、审计、重写或修改 `contracts/` 的任何文件；`contracts/` 继续是根 Core contract hub；
- 不修改 ARCH-001、ARCH-MIG-001、ARCH-DOCKER-001、ARCH-DEV-001 或其他 accepted 历史 task bundle，
  即使其中仍提到旧路径或旧发布模型；
- 不创建根 `multi-project-pm.md`、`docs/PLAN.md`、`docs/PLAN.zh-CN.md` 或 `docs/plans/`；
- 不对 `docs/multi-project-pm.md` 做 contracts audit、frontend/CA/module 实施设计或推测性大改写；只同步
  r3 当前版本分支/tag 模型；
- 不把 copyable publication commands、动态 OID 或执行 evidence 复制进 durable 多仓文档；
- 不读取、打印、提交或复制任何真实 env、secret、token、证书、SQL、日志、缓存或构建产物；
- 不启动、停止、重建 Docker，不连接数据库，不运行 Alembic/bootstrap/seed，不连接 PLC/CA；
- 不创建实体 `release/` 源码目录，不生成 tar/zip、binary、image export 或安装包；
- 不创建 `release/1.0.0`、`release/2.x.x` 或其他精确版本分支；本任务只创建 `release/1.x.x`；
- 不实现 ARCH-FE-001、CA-CONFIG-001 或 MODULES-001；
- 不创建 GitHub Release 页面，不上传 assets，不宣称 production readiness、多数据库兼容或现场验收；
- 不运行全局 `/init`、`/document-init`，不批量重建 `CODE_INDEX.md`；
- Codex 不执行 Git/GitHub 写操作。

## 7. Stop Conditions

遇到任一条件立即停止并回报 Human Owner：

- r3 尚未精确批准却需要继续 Development、修改 r2 `tasks.md` 或执行 Git/GitHub 写操作；
- 本地或远端 `release/1.x.x` / `v1.0.0` 已存在；
- 任何人要求创建、推送、移动或覆盖 `release/1.0.0`，或把 maintenance branch 当作精确版本权威；
- local `main`、local `origin/main` 与 remote `main` 在发布前不一致，Git index 非空，或远端状态因网络、
  认证/权限无法可靠核对；
- 工作树或 staged set 出现 §5 之外的路径；
- 出现根 `multi-project-pm.md`、`docs/PLAN.*` 或 `docs/plans/`；
- r3 staging 前 `tasks.md` 未升级为 `Revision: r3`，或仍把 r2/r1 旧命令作为当前 publication authority；
- active root docs、current r3 tasks 或 durable 文档仍把旧的 `release/<semver>` / `release/1.0.0` 模型当作
  当前合同；accepted 历史 task 记录中的旧模型命中不构成清理授权；
- `contracts/` 或任一 accepted 历史 task bundle 出现 diff；
- `CODE_INDEX.md` 进入 r3 staged set，或需要运行全局文档初始化才能继续；
- durable 多仓文档复制了 r3 copyable publication commands、动态 OID/evidence，形成第二 release truth；
- 暂存列表包含真实 env、secret、build artifact、日志、数据库文件或 allowlist 外路径；
- release branch、tag peeled commit、release commit 不一致；
- GitHub 权限、网络、认证或 push 失败；
- 需要 force、删除或重写已发布 ref 才能继续；
- 文档仍声称实体 `release/` 目录或已退休 Docker smoke 是当前入口；
- fresh-context Verification 无法独立核对远端 refs。

## 8. Verification

### 8.1 Development self-check

- `git status --short --branch`、`git diff --name-status --no-renames`、`git diff --cached --name-status
  --no-renames` 与 exact allowlist/staged-set audit；
- `git diff --check` 与 `git diff --cached --check`；
- `git check-ignore` 证明真实 dev env 仍被忽略，禁止读取值；
- `main` 三方 OID、本地/远端 branch/tag collision 与 ref-name preflight；
- topology check：既有三个 `docs/` 文件存在，根两个候选文件均不存在，且无 `docs/PLAN.*` / `docs/plans/`；
- active-reference check：active root docs、current r3 spec/tasks 和 durable 文档只以
  `docs/multi-project-pm.md` 为入口，并一致描述 `main`、`release/1.x.x` 与 annotated tags；r1/r2 history
  与 accepted 历史 task 记录需分类，不得以全仓零命中为由改写历史；
- bilingual README/CHANGELOG/PLAN/catalog 与 `docs/README.*` 对称/链接检查；
- `CODE_INDEX.md` no-diff audit：本次无结构变化，不应进入 staged set；
- `git diff --name-only -- contracts/` 与 accepted historical task path audit 必须无输出；
- durable `docs/multi-project-pm.md` diff audit：只包含当前版本分支/tag 模型纠偏，不含 duplicate copyable
  publication commands、动态 OID/evidence、contracts audit 或大范围 speculative rewrite；
- 文档残留扫描：实体 release 目录、已退休 Docker smoke、GitHub Release/build/production 误声明；
- r3 bundle metadata check：spec=`draft|owner_approved` 后，tasks 必须为同一 `Revision: r3` 且在发布前保持
  `implementation_in_progress`；`checklist.md` 在 `developer_handoff` 前必须不存在；
- 运行 project-governance checker；若仍只命中 accepted ARCH-001 checklist 的既有 duplicate
  `Handoff:`，如实记录为 out-of-allowlist historical defect，不得越界修复或把 exit 1 写成 pass；
- Human Owner Git 输出中的命令、退出码和 commit/ref OID 记录。

### 8.2 Fresh-context Verification

- 独立读取 r3 spec/tasks、r2/r1 superseded history、依赖任务 accepted checklist 与最终 diff/commit；
- 复核 release commit 只触达 §5 staged set，真实 env/secret/build/runtime、`contracts/` 与 accepted 历史
  task surface 未进入 Git；
- 复核 `docs/` 是 root-PLAN-owned README-only structural support、canonical 路径唯一、根旧/正确拼写
  文件均不存在，active refs 与 CODE_INDEX 正确；
- 复核 durable 多仓文档 correction bounded，current publication commands/evidence 只在 r3 `tasks.md`；
- `git status`、本地 branch/tag、remote refs、annotated tag 和 peeled commit；
- 确认 `origin/main`、`origin/release/1.x.x`、`v1.0.0^{}` 在发布时指向同一 release commit，且
  `git cat-file -t refs/tags/v1.0.0` 为 `tag`；
- 确认 `release/1.0.0` 不存在，main-only post-release receipt 不移动已发布 tag 或在本任务中 fast-forward
  maintenance branch；
- 只写 checklist，并给出 `qa_passed|qa_failed|qa_blocked`；不得代录 Human Owner 最终接受。

## 9. Acceptance Criteria

- **AC-001**：ARCH-001、ARCH-MIG-001、ARCH-DOCKER-001、ARCH-DEV-001 的依赖 Revision 均有 Human
  Owner final acceptance；r3 PLAN/catalog 只按真实阶段机械同步。
- **AC-002**：active stable contracts and bilingual indexes consistently describe `main`, major-line
  maintenance branches and immutable annotated tags; no active document presents `release/1.0.0` as a target。
- **AC-003**：`release/1.x.x` 是 1.x maintenance branch，未来 `release/2.x.x` 采用同一大版本模式；精确
  版本只由 `v<major>.<minor>.<patch>` annotated tag 表达，且已发布 tag 不可移动、删除或重建。
- **AC-004**：accepted 历史 task bundle 未修改；其中旧路径或旧发布模型只作为历史证据保留。`contracts/`
  仍是根 Core contract hub，且本 r3 对 `contracts/` 无任何 diff、move、audit 或 rewrite。
- **AC-005**：`docs/multi-project-pm.md` 只同步当前 r3 版本分支/tag 模型与发布顺序，不扩展为
  contracts/frontend/CA/module 实施或 speculative rewrite；copyable 命令、动态 OID 与 evidence 只在 r3
  `tasks.md`。
- **AC-006**：r3 Development staged set 只包含 §5.3 的十二个路径事实；不包含 `CODE_INDEX.md`、现有
  `docs/README.*`、源码、`contracts/`、accepted history、真实 env、secret、构建产物、日志、数据库或
  runtime 文件。
- **AC-007**：发布前 local main、local origin/main 与 remote main 指向同一 OID，index 为空，local/remote
  `release/1.x.x` 与 `v1.0.0` 均不存在；碰撞、分叉、DNS/权限失败或无法核对会 stop。
- **AC-008**：唯一 release-preparation commit 推送到 `origin/main` 后，从同一 OID 创建并 push
  `release/1.x.x` 与 annotated `v1.0.0`；不得创建 `release/1.0.0`。
- **AC-009**：fresh-context Verification 证明发布时 `origin/main`、`origin/release/1.x.x` 与
  `v1.0.0^{}` 指向同一 release commit，tag annotation 正确，maintenance branch 语义与
  docs/contracts/release 边界均通过。
- **AC-010**：没有 GitHub Release 页面、asset、build artifact、deployment、branch setting 或其他未授权
  外部状态变化；main 保持后续开发线。
- **AC-011**：r1 approval/Development 与 r2 approval/Development/main preparation history 均保留为
  superseded history；同一任务的 r3 3MD 完成 Development handoff、fresh-context verdict 与 Human Owner
  final acceptance，未把旧 approval 或 DEV self-check 冒充 r3 approval/QA/final acceptance。
- **AC-012**：最终本地工作区干净，Human Owner 已把 §5.4 main-only receipt 精确 push 到 `main`；receipt
  没有移动已发布 tag、在本任务中 fast-forward maintenance branch 或改变 1.0.0 source。

## 10. Risks and Rollback

- r3 draft 与仍为 r2 的 `tasks.md` 会暂时 metadata 不一致；这是 material-change gate 的显式暂停状态。
  r3 未批准前不改 tasks；批准后 Development 必须先升级 tasks 至 r3，再继续实施或 staging；
- r2 `tasks.md` 中的 `release/1.0.0` 命令与旧 staged set 容易被误复制；r3 获批后必须用新命令覆盖当前
  authority，但保留 r2 文字为 superseded history；
- `release/1.x.x` 是可 fast-forward 的维护线而非精确版本，若文档、脚本或人员把它当定版事实会造成
  追溯歧义；精确验收必须比较 annotated tag 的 peeled commit；
- `release/1.x.x`、`release/2.x.x` 字面命名是公开长期合同；拼写或 commit 选错会形成高成本纠偏，创建
  前必须打印并人工比对 branch/tag 名称与 commit OID；
- 已发布 annotated tag 的对象 OID 与 peeled commit OID 不同是正常现象，验收比较使用 `v1.0.0^{}`；
- 较早 PM 复核曾因 DNS 无法访问 GitHub；该历史 limitation 不替代当前成功的只读结果，Human Owner 发布前
  仍必须重新成功执行 remote preflight；
- 发布前的 docs/path/staging 错误通过不 commit、不 push 直接停止并修正工作树，不回退他人输入；
- main release commit 已 push 但 refs 尚未创建时，用新的 r3 修复提交纠偏，不 rewrite `main`；
- `v1.0.0` 一旦 push 后不得删除、force 或移动；`release/1.x.x` 的 fast-forward 只能在未来独立获批
  的 1.x 发布任务中进行，需要纠偏时停止并由 Human Owner 决定新 Revision；
- post-release `tasks.md` evidence、`checklist.md` verdict/final acceptance 与 PLAN/catalog 状态晚于 1.0.0
  release commit，必须只进入 later main-only receipt；这不是移动 tag 或本任务中推进 maintenance branch 的理由；
- dev 容器可以继续运行；本任务不依赖停止容器，也不把容器状态打包进版本。

## 11. Revision 与 Human Owner Approval History

### r3 — owner_approved

- 2026-08-21：Human Owner 确认采用 `main` + `release/1.x.x`、`release/2.x.x` 等大版本维护分支，精确
  版本只使用 `v<major>.<minor>.<patch>` annotated tags（示例：`v1.0.0`、`v1.2.1`、`v2.1.2`），并要求
  将 ARCH-REL-001 微调为 r3；该确认触发 material-change reapproval。
- 批准日期：2026-08-21；Human Owner 精确批准原文（逐字保留）：

  `批准 aiis-ics-arch::ARCH-REL-001 r3，按 spec 精确范围和 allowlist 开始 Development；Git/GitHub 写操作继续由 Human Owner 手工执行。`
- 解释：该原文明确批准当前精确 r3 spec 与 allowlist，并将 Development 启动于 r3；Git/GitHub 写操作仍
  仅归 Human Owner 手工执行，不授予 Development、PM、Verification 或协调 Agent 任何外部写权限。
- 批准结果：`owner_approved`，按 `agent_team_same_session` 移交 Development；Development 只准备 §5.2
  allowlist 内文档、r3 `tasks.md`、检查与 copyable commands；本批准不是 Git publication evidence、QA
  verdict 或 Human Owner final acceptance。
- r3 将首次发布 `release/1.x.x` 与 `v1.0.0` 指向同一 release commit；不创建 `release/1.0.0`。

### r2 — superseded publication authority history

- 2026-08-20：Human Owner 请求先纠正多仓文档结构/路径，再继续同一 1.0.0 手工定版序列；该请求授权
  PM 形成 r2 draft，不等于对 r2 范围、风险、allowlist 或外部 Git 动作的精确批准；
- 批准日期：2026-08-20；
- Human Owner 批准原文（逐字保留）：

  `好的，批准 r2，推mian再推版本分支的时候我手动来做。`

- 解释：上下文明确指向刚呈交的当前精确 ARCH-REL-001 r2 spec 与 allowlist；原文中的“推mian”仅规范化
  理解为 Human Owner 手工 push `main`，不扩展或转移其他权限；
- 批准结果：`owner_approved`，按 `agent_team_same_session` 移交 Development。Development 只准备 §5.2
  allowlist 内文档、r2 `tasks.md`、检查与 copyable commands；staging、commit、push `main`、创建/push
  `release/1.0.0` 与创建/push annotated `v1.0.0` 全部继续仅由 Human Owner 手工执行；
- `developer_handoff` 后仍必须 fresh-context Verification；本批准不是 Git publication evidence、QA verdict
  或 Human Owner final acceptance。
- Human Owner 随后已将 r2 main preparation commit 推送为 `f5f41550a60f439040f8c84540210cd0f2bab3aa`；
  `release/1.0.0` 与 `v1.0.0` 尚未创建。
- r2 的 `tasks.md`、旧 staged set 与其中的 `release/1.0.0` commands 现仅作为 superseded publication
  authority history 保留；r3 获批后必须由 Development 以 r3 tasks 和新 allowlist 取代，不能继续用于 ref 发布。

### r1 — superseded history

- 批准日期：2026-08-11；
- 批准原文：

  `批准 aiis-ics-arch::ARCH-REL-001 r1，按 spec 精确范围和 allowlist 开始 Development；Git/GitHub 写操作继续由 Human Owner 手工执行。`

- r1 曾为 `owner_approved`，Development 形成了当前 r1 `tasks.md` / `implementation_in_progress` 历史，
  但未执行 Git/GitHub 写操作、未创建 release refs、未进入 `developer_handoff`，也没有 checklist/QA/
  final acceptance；
- 2026-08-20 因 canonical path、docs governance、CODE_INDEX 与 allowlist material change，r1 执行授权被
  r2 draft supersede。r1 approval 与 Development 事实保留，不回写或伪造其结果；
- r2 精确批准前，r1 `tasks.md` 保持 untouched。r2 获批后由 Development 原地升级为 r2，并在其 rework/
  history 中保留 r1 事实；PM 不替 Development 修改该文件。
