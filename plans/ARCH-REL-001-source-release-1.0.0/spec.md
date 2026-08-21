# ARCH-REL-001 AIIS ICS Architecture 1.0.0 源码定版与 GitHub 发布 — PM Spec

Task ID: ARCH-REL-001
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准当前精确 r2 spec 与 allowlist；移交 Development 按 §5.2 开始 release preparation；staging、commit、push main、创建/push release branch 与 annotated tag 仍仅由 Human Owner 手工执行

Task Namespace: aiis-ics-arch
Classification: root
Capability: AIIS ICS Architecture 1.0.0 源码定版、版本分支/tag 与 GitHub refs 发布
Owner: architecture release management
Depends On: ARCH-001 r3 owner_accepted, ARCH-MIG-001 r1 owner_accepted, ARCH-DOCKER-001 r1 owner_accepted, ARCH-DEV-001 r4 owner_accepted
Related Task: ARCH-FE-001, CA-CONFIG-001, future MODULES-001
Target Version: 1.0.0
Acceptance Chain Reference: ARCH-REL-001 r2 approval -> Development release preparation -> Human Owner manual Git publication -> Development evidence handoff -> fresh-context Verification -> Human Owner final acceptance -> main-only release receipt
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner -> Development -> fresh-context QA / Verification -> Human Owner
Fresh Context: required for Verification
Created: 2026-08-11
Updated: 2026-08-20
Required Development Skills: aiis, project-governance, code-document-indexer

## 1. PM 结论

本任务把当前已验收的 Architecture Core 固定为第一个公开源码版本，并在发布前先收敛跨仓长期文档的
结构、路径与权威边界：

- 版本分支：`release/1.0.0`；
- annotated tag：`v1.0.0`；
- 托管仓库：`https://github.com/jasonbu163/aiis-ics-arch.git`；
- `main` 继续作为后续 Core 开发线；
- 版本分支和 tag 在创建后保持固定，不在本任务中 force-update、删除或重建；
- 不复制一份源码到实体 `release/` 目录；Git branch/tag 是源码定版权威；
- `docs/` 作为由根 PLAN 归口的结构性支撑目录，只建立双语 README 索引/介绍；
- 跨仓长期文档的 canonical 路径为 `docs/multi-project-pm.md`；删除拼写错误的根
  `mutil-project-pm.md`，且不得创建根 `multi-project-pm.md`；
- `contracts/` 继续是根 Core contract hub，本 r2 不移动、不审计、不改写其中任何内容；
- 不提交运行 build 产物，不创建 GitHub Release 页面，不做生产部署。

Git/GitHub 写操作全部由 Human Owner 在本机终端手工执行。Development 只准备受控文档、检查命令和
`tasks.md`，不得代替 Human Owner 运行 `git add`、`commit`、`push`、`branch` 或 `tag`。

2026-08-20 的路径与 allowlist 变化属于 material change。r1 的范围批准和 Development 记录保留为历史，
但不再授权继续发布；当前必须先取得 Human Owner 对本 r2 的精确批准。

## 2. PM 预检事实

2026-08-20 当前基线与 Human Owner 提供的工作树事实：

- 当前 checkout 为 `main`；`HEAD`、本地 `origin/main` 与 Human Owner 已核对的远端 `main` 均为
  `d11159e8f4a7ce62096a0b499f3b7a93b5da807b`；
- local/remote `release/1.0.0` 与 `v1.0.0` 均不存在，Git index 为空；这些都是时点事实，Human Owner
  暂存前必须重跑；
- 工作树包含 r1 release-preparation 文档差异，以及 Human Owner 已提供的路径移动输入：tracked 根
  `mutil-project-pm.md` 已删除，`docs/multi-project-pm.md` 当前为 untracked；
- `docs/README.md` / `docs/README.zh-CN.md` 尚不存在；根 `multi-project-pm.md` 不存在；
- 当前 `CODE_INDEX.md` 尚未登记 `docs/`，且仍有不存在的实体 `release/` 目录条目；
- r1 `tasks.md` 为 `Revision: r1` / `implementation_in_progress`，包含旧路径与旧 staging 命令；它是
  Development 历史输入，不是 r2 执行依据，r2 获批前必须保持不动；
- `docs/multi-project-pm.md` 仍含旧根路径、r1 当前状态、重复的现场 publication 命令和若干当前结构
  偏差；这些只证明需要 r2 纠偏，不证明 r2 已获批准或已实施；
- ARCH-001 r3、ARCH-MIG-001 r1、ARCH-DOCKER-001 r1、ARCH-DEV-001 r4 仍为
  `owner_accepted`；accepted 历史任务中出现旧路径属于历史证据，不在 r2 中改写；
- 当前不存在 `checklist.md`，没有 fresh-context QA verdict 或 Human Owner final acceptance。

## 3. Included Scope

### 3.1 `docs/` 结构与 canonical 路径

- `docs/` 是 durable cross-repository/process 文档的结构性支撑目录，生命周期继续由根 `PLAN.*` 归口；
- 只新增 `docs/README.md` / `docs/README.zh-CN.md`，作为双语目录索引和简短介绍；两份 README 必须互链、
  链接 `multi-project-pm.md`，说明根 PLAN ownership，且不承载 live task tracking；
- 不创建 `docs/PLAN.md`、`docs/PLAN.zh-CN.md`、`docs/plans/` 或 task bundle；
- canonical 多仓文档固定为 `docs/multi-project-pm.md`；删除根 `mutil-project-pm.md`；不得创建根
  `multi-project-pm.md`；
- 修正 active root docs、current r2 spec/tasks 和 `docs/multi-project-pm.md` 内当前示例/链接使用的新路径；
- accepted 历史 task bundle 继续保留旧路径文字作为当时证据，不做批量路径清洗。当前 r2 文档若必须
  提到旧路径，只能用于 r1 history、明确删除目标或 negative check，不能继续把它当入口。

### 3.2 多仓文档的 bounded correction

`docs/multi-project-pm.md` 只做本次发布必需的当前事实纠偏：

- 更新 canonical 路径、当前目录示例、active internal references、r2 状态和 release sequence；
- 将 `contracts/` 明确为现有根 Core contract hub；本 r2 不移动、审计或改写 `contracts/` 内容，也不把
  它改归 `docs/`；
- 保留仍然正确的迁移历史与三仓边界，不因移动文件而做推测性大改写；
- 不把 ARCH-FE-001、CA-CONFIG-001、MODULES-001、frontend、CA 或项目模块实施并入本任务；
- 不复制 r2 的现场命令、动态 OID 或 evidence。durable 文档只能摘要长期顺序并链接当前
  `plans/ARCH-REL-001-source-release-1.0.0/tasks.md`；当前 publication 命令与执行证据仅由 r2
  `tasks.md` 权威维护。

### 3.3 长期 release 文档、索引与 CODE_INDEX

- `AGENTS.md`、双语 `README.*`、双语 `CHANGELOG.*` 继续维护 source-only branch/tag、无实体
  `release/`、无 hosted GitHub Release/build/deployment claim 的长期合同；
- 双语 README 仓库 map 增加 `docs/` 结构性入口，并把三仓文档链接改为
  `docs/multi-project-pm.md`；`contracts/` 仍保持根 Core surface；
- `PLAN.*` 与 `plans/README.*` 只做当前 Revision/status/next-gate 的机械同步，并继续保持 ARCH-FE-001、
  CA-CONFIG-001 独立 `draft`；
- Development 必须遵循 `code-document-indexer`，仅对真实结构变化外科手术式更新 `CODE_INDEX.md`：增加
  `docs/` 与 canonical 多仓文档入口，删除不存在的实体 `release/` 目录条目；不得重建索引、改写无关
  entry，也不得运行全局 `/init` 或 `/document-init`；
- 不新增 `VERSION.md`、`RELEASE.md` 或源码快照目录，版本事实继续由 CHANGELOG + Git refs 表达。

### 3.4 r2 Release preparation

Human Owner 精确批准 r2 后，Development 必须：

1. 读取 r2 approved spec、r1 `tasks.md` 历史与所有依赖任务的最终 checklist；
2. 使用 `aiis`、`project-governance` 与 `code-document-indexer`，只修改 §5 r2 Development allowlist；
3. 将现有 `tasks.md` 原地升级为 `Revision: r2` / `implementation_in_progress`，保留 r1 Development
   事实为 superseded history，不把旧路径、旧 staging 命令或 r1 approval 当作 r2 授权；
4. 核对 Human Owner 已提供的 docs move，不回退或重复移动，并确认工作树路径精确匹配 r2 release-
   preparation staged set；
5. 重跑 local/remote main 与 branch/tag collision preflight；任一目标 ref 已存在、main 分叉、index 非空
   或网络/权限无法验证时停止；
6. 运行文档、链接、双语、secret、Git diff、CODE_INDEX、ref-name、release-boundary 与 exact allowlist 检查；
7. 在 r2 `tasks.md` 给出唯一的 copyable Human Owner staging/commit/push/branch/tag 命令和预期输出；
8. Human Owner 完整 Git 输出返回前保持 `implementation_in_progress`，不得声称 refs 已发布。

### 3.5 Human Owner 手工 Git 发布

r2 `tasks.md` 是当前 copyable publication 命令与执行证据的唯一权威。命令必须保持以下顺序：

1. 重新核对 `main == local origin/main == remote main`、Git index 为空且 local/remote 目标 refs 不存在；
2. 以显式路径暂存 §5 的 r2 release-preparation staged set；使用
   `git diff --cached --name-status --no-renames` 审核时，旧根文件必须显示删除，三个 `docs/` 文件必须
   显示新增，且不得出现根 `multi-project-pm.md`；
3. 运行 cached diff/secret/path 检查后，只创建一个 release-preparation commit 并 push `main`；
4. 打印该精确 commit OID，从它创建 `release/1.0.0` 与 annotated `v1.0.0`，分别 push，并保持
   checkout 在 `main`；
5. 返回全部命令、stdout/stderr、退出码、main/release branch OID、tag object OID 与 peeled commit。

禁止 `git add .`、`git add -A`、force push/tag、ref 删除、history rewrite 或 GitHub Release 创建命令。
任一步失败即停止并保留输出，不通过删除、移动或重建 refs 掩盖失败。

### 3.6 Post-publication evidence、Verification 与 receipt

Human Owner 返回手工输出后：

- Development 只在 r2 `tasks.md` 记录命令、退出码、release commit OID 和已发布 refs，进入
  `developer_handoff`；r1 历史继续保留但不覆盖 r2 当前事实；
- fresh-context Verification 独立核对 local/remote `main`、`release/1.0.0`、`v1.0.0` 最终指向同一
  release commit，检查 annotated tag、路径/文档/contract 边界和公开 release 边界，只写
  `checklist.md`；
- QA verdict 后由 Human Owner 作最终接受决定；`qa_passed` 不等于 final acceptance；
- Human Owner 最终接受后，由 Human Owner 手工把 §5 main-only receipt allowlist 形成第二个纯治理提交
  并 push 到 `main`；不得移动已经固定的 release branch/tag；
- 该 main-only receipt 晚于 1.0.0 release commit 是预期行为，1.0.0 tag 不需要自我包含其 post-release
  验证结果。

## 4. Git / GitHub Authority

r2 获批只启动 Development release preparation，不授予 Development、PM、Verification 或协调 Agent
任何 Git/GitHub 写权限。只允许 Human Owner 手工创建以下外部状态：

- `origin/main` 上一个 release preparation commit；
- `origin/release/1.0.0`；
- `origin/v1.0.0` annotated tag；
- 最终接受后的一个 main-only governance receipt commit。

不授权：GitHub Release 页面、asset 上传、branch protection/settings、PR、issue、deployment、package
registry、Actions secret、协作者/权限调整或其他仓库操作。

## 5. Exact Allowlist

### 5.1 r2 精确批准前

PM 与主协调只允许写以下范围；本 PM role 实际只写 `spec.md`，PLAN/catalog 仅供 coordinator 做
mechanical synchronization：

- `plans/ARCH-REL-001-source-release-1.0.0/spec.md`；
- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`。

当前 r1 `tasks.md` 必须保持 untouched。r2 批准前不得更新 `tasks.md`、新建 `checklist.md`、暂存文件或
执行任何 Git/GitHub 写操作。

### 5.2 r2 Development allowlist

Human Owner 精确批准 r2 后，Development 只允许写：

- `AGENTS.md`；
- `CODE_INDEX.md`；
- `README.md`；
- `README.zh-CN.md`；
- `CHANGELOG.md`；
- `CHANGELOG.zh-CN.md`；
- `PLAN.md`；
- `PLAN.zh-CN.md`；
- `docs/README.md`；
- `docs/README.zh-CN.md`；
- `docs/multi-project-pm.md`；
- 删除根 `mutil-project-pm.md`；
- `plans/README.md`；
- `plans/README.zh-CN.md`；
- `plans/ARCH-REL-001-source-release-1.0.0/tasks.md`。

`contracts/`、accepted 历史 task bundle、根 `multi-project-pm.md`、`docs/PLAN.*` 与 `docs/plans/` 不在
Development allowlist。

### 5.3 Human Owner release-preparation staged set

第一个 main release-preparation commit 必须精确包含以下十六个路径事实：

- §5.2 的十五项 Development 写面（其中根 `mutil-project-pm.md` 是 deletion）；
- PM-owned `plans/ARCH-REL-001-source-release-1.0.0/spec.md` r2 diff。

Human Owner 的 copyable `git add -- <explicit paths>` 只能由 r2 `tasks.md` 给出。cached 审核必须使用
`--no-renames` 比较路径集合，避免 Git rename detection 把旧根删除与新 canonical 文件新增折叠成单一
rename 记录。三个 `docs/` 文件应为新增，根 `mutil-project-pm.md` 应为删除；根
`multi-project-pm.md` 必须不存在且不得进入 index。

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

receipt 只追加到 `main`，不得修改 1.0.0 source、移动 release branch/tag，或夹带其他路径。任何实质
scope、acceptance、risk、Execution Mode 或 allowlist 变化都必须停止并建立新 Revision。

## 6. Explicit Exclusions

- 不修改 backend、frontend-js、control-agent、tools 的源码、配置、migration、lockfile、Dockerfile 或
  Compose；
- 不移动、审计、重写或修改 `contracts/` 的任何文件；`contracts/` 继续是根 Core contract hub；
- 不修改 ARCH-001、ARCH-MIG-001、ARCH-DOCKER-001、ARCH-DEV-001 或其他 accepted 历史 task bundle，
  即使其中仍提到旧 `mutil-project-pm.md` 路径；
- 不创建根 `multi-project-pm.md`、`docs/PLAN.md`、`docs/PLAN.zh-CN.md` 或 `docs/plans/`；
- 不对 `docs/multi-project-pm.md` 做 contracts audit、frontend/CA/module 实施设计或推测性大改写；
- 不把 copyable publication commands、动态 OID 或执行 evidence 复制进 durable 多仓文档；
- 不读取、打印、提交或复制任何真实 env、secret、token、证书、SQL、日志、缓存或构建产物；
- 不启动、停止、重建 Docker，不连接数据库，不运行 Alembic/bootstrap/seed，不连接 PLC/CA；
- 不创建实体 `release/` 源码目录，不生成 tar/zip、binary、image export 或安装包；
- 不实现 ARCH-FE-001、CA-CONFIG-001 或 MODULES-001；
- 不创建 GitHub Release 页面，不上传 assets，不宣称 production readiness、多数据库兼容或现场验收；
- 不运行全局 `/init`、`/document-init`，不批量重建 `CODE_INDEX.md`；
- Codex 不执行 Git/GitHub 写操作。

## 7. Stop Conditions

遇到任一条件立即停止并回报 Human Owner：

- r2 尚未精确批准却需要继续 Development、修改 r1 `tasks.md` 或执行 Git/GitHub 写操作；
- 本地或远端 `release/1.0.0` / `v1.0.0` 已存在；
- local `main`、local `origin/main` 与 remote `main` 在发布前不一致，Git index 非空，或远端状态因网络、
  认证/权限无法可靠核对；
- 工作树或 staged set 出现 §5 之外的路径，或已知 Human Owner docs move 被回退/覆盖；
- 根 `mutil-project-pm.md` 未按删除处理、`docs/multi-project-pm.md` 缺失、出现根
  `multi-project-pm.md`、`docs/PLAN.*` 或 `docs/plans/`；
- r2 staging 前 `tasks.md` 仍是 `Revision: r1`，或仍把旧路径/旧命令作为当前 publication authority；
- active root docs、current r2 tasks 或 durable 文档仍把旧根路径当入口；accepted 历史 task 记录中的旧
  路径命中不构成清理授权；
- `contracts/` 或任一 accepted 历史 task bundle 出现 diff；
- `CODE_INDEX.md` 除增加 `docs/`/canonical entry、删除虚构实体 `release/` entry 外出现无关重写，或需要
  运行全局文档初始化才能继续；
- durable 多仓文档复制了 r2 copyable publication commands、动态 OID/evidence，形成第二 release truth；
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
- topology check：三个 `docs/` 文件存在，根两个候选文件均不存在，且无 `docs/PLAN.*` / `docs/plans/`；
- active-reference check：active root docs、current r2 spec/tasks 和 durable 文档只以
  `docs/multi-project-pm.md` 为入口；r1/history/delete/negative wording 与 accepted 历史 task 记录需分类，
  不得以全仓零命中为由改写历史；
- bilingual README/CHANGELOG/PLAN/catalog 与 `docs/README.*` 对称/链接检查；
- `CODE_INDEX.md` scoped diff audit：只增加 docs/canonical entry、删除不存在的 physical release entry；
- `git diff --name-only -- contracts/` 与 accepted historical task path audit 必须无输出；
- durable `docs/multi-project-pm.md` diff audit：只包含 current structural/path/release corrections，不含
  duplicate copyable publication commands、动态 OID/evidence、contracts audit 或大范围 speculative rewrite；
- 文档残留扫描：实体 release 目录、已退休 Docker smoke、GitHub Release/build/production 误声明；
- r2 bundle metadata check：spec=`draft|owner_approved` 后，tasks 必须为同一 `Revision: r2` 且在发布前保持
  `implementation_in_progress`；`checklist.md` 在 `developer_handoff` 前必须不存在；
- 运行 project-governance checker；若仍只命中 accepted ARCH-001 checklist 的既有 duplicate
  `Handoff:`，如实记录为 out-of-allowlist historical defect，不得越界修复或把 exit 1 写成 pass；
- Human Owner Git 输出中的命令、退出码和 commit/ref OID 记录。

### 8.2 Fresh-context Verification

- 独立读取 r2 spec/tasks、r1 superseded history、依赖任务 accepted checklist 与最终 diff/commit；
- 复核 release commit 只触达 §5 staged set，真实 env/secret/build/runtime、`contracts/` 与 accepted 历史
  task surface 未进入 Git；
- 复核 `docs/` 是 root-PLAN-owned README-only structural support、canonical 路径唯一、根旧/正确拼写
  文件均不存在，active refs 与 CODE_INDEX 正确；
- 复核 durable 多仓文档 correction bounded，current publication commands/evidence 只在 r2 `tasks.md`；
- `git status`、本地 branch/tag、remote refs、annotated tag 和 peeled commit；
- 确认 `origin/main`、`origin/release/1.0.0`、`v1.0.0^{}` 在发布时指向同一 release commit；
- 确认 main-only post-release receipt 不移动 release branch/tag；
- 只写 checklist，并给出 `qa_passed|qa_failed|qa_blocked`；不得代录 Human Owner 最终接受。

## 9. Acceptance Criteria

- **AC-001**：ARCH-001、ARCH-MIG-001、ARCH-DOCKER-001、ARCH-DEV-001 的依赖 Revision 均有 Human
  Owner final acceptance；r2 PLAN/catalog 只按真实阶段机械同步。
- **AC-002**：`docs/README.md` / `docs/README.zh-CN.md` 是互链、内容对称且链接 canonical 多仓文档的
  root-PLAN-owned structural-support index；不存在 `docs/PLAN.*` 或 `docs/plans/`。
- **AC-003**：canonical 文档只位于 `docs/multi-project-pm.md`；根 `mutil-project-pm.md` 已删除，根
  `multi-project-pm.md` 不存在；active refs/current examples 使用 canonical 路径。
- **AC-004**：accepted 历史 task bundle 未修改；其中旧路径文字被保留为历史证据。`contracts/` 仍是根
  Core contract hub，且本 r2 对 `contracts/` 无任何 diff、move、audit 或 rewrite。
- **AC-005**：`docs/multi-project-pm.md` 只纠正 current structural/path/release deviations；未扩展为
  contracts/frontend/CA/module 实施或 speculative rewrite，且只摘要/链接 release 顺序，copyable 命令、
  动态 OID 与 evidence 只在 r2 `tasks.md`。
- **AC-006**：AGENTS、双语 README/CHANGELOG、PLAN/catalog 与 `CODE_INDEX.md` 对 source-only、canonical
  docs path、root contracts hub 和不存在 physical `release/` 的当前事实一致；CODE_INDEX 只做 scoped
  topology correction。
- **AC-007**：发布前 local main、local origin/main 与 remote main 指向同一 OID，index 为空，local/remote
  `release/1.0.0` 与 `v1.0.0` 均不存在；碰撞、分叉或无法核对会 stop。
- **AC-008**：唯一 release-preparation commit 的 staged set 精确等于 §5 十六个路径事实：旧根文件为
  deletion、三个 docs 文件为 additions；不包含根 `multi-project-pm.md`、源码、`contracts/`、accepted
  history、真实 env、secret、构建产物、日志、数据库或 runtime 文件。
- **AC-009**：Human Owner 手工把唯一 release-preparation commit 推到 `origin/main`，并从同一 OID 创建/
  push `release/1.0.0` 与 annotated `v1.0.0`。
- **AC-010**：fresh-context Verification 证明发布时 `origin/main`、`origin/release/1.0.0` 与
  `v1.0.0^{}` 指向同一 release commit，tag annotation 正确，且 docs/contracts/release 边界均通过。
- **AC-011**：没有 GitHub Release 页面、asset、build artifact、deployment、branch setting 或其他未授权
  外部状态变化；main 保持后续开发线，release branch/tag 未被移动、删除、force 或重写。
- **AC-012**：r1 approval/Development history 保留为 superseded history；同一任务的 r2 3MD 完成
  Development handoff、fresh-context verdict 与 Human Owner final acceptance，未把 r1 approval 或 DEV
  self-check 冒充 r2 approval/QA/final acceptance。
- **AC-013**：最终本地工作区干净，Human Owner 已把 §5 main-only receipt 精确 push 到 `main`；receipt
  没有移动 1.0.0 refs，远端公开文档与 task 状态可追溯。

## 10. Risks and Rollback

- r2 draft 与仍为 r1 的 `tasks.md` 会暂时 metadata 不一致；这是 material-change gate 的显式暂停状态。
  r2 未批准前不改 tasks；批准后 Development 必须先升级 tasks 至 r2，再继续实施或 staging；
- Human Owner 已提供的 move 当前是 untracked add + tracked delete；普通 `git push` 不会带上未跟踪文件，
  必须由 tasks 给出 explicit staging，并以 cached exact-set 审核证明三个 docs additions 均已进入 index；
- Git rename detection 可能把旧根删除和新文件新增折叠为 rename，掩盖路径集合；因此 allowlist 机械审计
  使用 `--no-renames`；
- 全仓旧路径扫描会命中 r1 history、删除/negative wording 和 accepted 历史任务；这些命中必须分类，
  不能以“清零”为由篡改历史，也不能把 active stale reference 当历史忽略；
- 长篇 durable 多仓文档容易因顺手整理发生 scope creep，或复制 task 命令形成第二 truth；Development
  和 Verification 必须按 scoped diff 审核 current-only correction；
- `CODE_INDEX.md` 当前有 stale physical `release/` entry；修正必须和新增 docs entry 一起保持 surgical，
  不能触发全局文档初始化或无关 topology rewrite；
- branch/tag 名称是公开长期合同；拼写或 commit 选错会形成高成本纠偏，因此创建前必须打印并人工比对
  commit OID；
- annotated tag 的对象 OID 与 peeled commit OID 不同是正常现象，验收比较使用 `v1.0.0^{}`；
- 发布前的 docs/path/staging 错误通过不 commit、不 push 直接停止并修正工作树，不回退他人输入；
- main release commit 已 push 但 refs 尚未创建时，用新的修复提交纠偏，不 rewrite `main`；
- 任一 release ref 已 push 后，不得在本任务中删除、force 或移动。需要纠偏时停止，另开 Revision / fix
  任务并由 Human Owner 决定新版本或 ref 处理；
- post-release `tasks.md` evidence、`checklist.md` verdict/final acceptance 与 PLAN/catalog 状态晚于 1.0.0
  release commit，必须只进入 later main-only receipt；这不是移动 1.0.0 refs 的理由；
- dev 容器可以继续运行；本任务不依赖停止容器，也不把容器状态打包进版本。

## 11. Revision 与 Human Owner Approval History

### r2 — owner_approved

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
