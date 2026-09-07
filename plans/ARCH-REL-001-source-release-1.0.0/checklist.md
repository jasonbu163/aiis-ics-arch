# ARCH-REL-001 1.0.0 源码定版 — fresh-context QA / Verification Checklist

Task ID: ARCH-REL-001
Revision: r3
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner final acceptance recorded; §5.4 main-only governance receipt pending manual push

Task Namespace: aiis-ics-arch
Verification Context: fresh-context Verification, independent of Development reasoning
Verification Root: /Users/jason/Desktop/DreamCode/aiis-ics-arch
Verification Date: 2026-08-21
Role Separation: PM -> Human Owner -> Development -> fresh-context QA / Verification -> Human Owner
Applicable Skills: aiis, project-governance

## 1. 验证依据与硬边界

本轮从 fresh context 独立读取了根 `AGENTS.md`、`README.md` / `README.zh-CN.md`、
`PLAN.md` / `PLAN.zh-CN.md`、`docs/README.md` / `docs/README.zh-CN.md`、
`plans/README.md` / `plans/README.zh-CN.md`，完整读取 ARCH-REL-001 r3 `spec.md`、
`tasks.md`，并读取四项依赖的最终 accepted checklist：ARCH-001 r3、ARCH-MIG-001 r1、
ARCH-DOCKER-001 r1、ARCH-DEV-001 r4。还独立检查了 r3 release-preparation commit 的
完整路径差异、当前 worktree/index、active 文档、ref/tag 对象和 Development 自检证据。

本轮只允许创建本文件。没有修改 `spec.md`、`tasks.md`、PLAN、README、CHANGELOG、
实现、测试、配置、`contracts/`、`CODE_INDEX.md` 或任何 accepted 历史任务；没有执行
`git add`、`commit`、`push`、`branch`、`tag`、GitHub 写操作、Docker/DB/PLC/CA 操作、
部署、GitHub Release、asset 或生产动作。QA 不修复实现或治理缺陷，不授予 Human Owner
最终验收、平台 ACL、强制路由或发布授权。

在创建本文件前确认 `checklist.md` 不存在，且 `tasks.md` 已为 `Revision: r3` /
`Status: developer_handoff`。本 verdict 独立于 Development 自检和 Human Owner publication
evidence；最终验收仍属于 Human Owner。

## 2. 依赖、环境与前置条件

| 项目 | 证据与结果 |
| --- | --- |
| 依赖 ARCH-001 | r3 checklist `Status: owner_accepted`；Human Owner final acceptance 已记录。 |
| 依赖 ARCH-MIG-001 | r1 checklist `Status: owner_accepted`；单一 `d4e6f8a0b2c4` Core root/head 已接受。 |
| 依赖 ARCH-DOCKER-001 | r1 checklist `Status: owner_accepted`；MySQL 8.4.6 smoke/runtime gate 已接受。 |
| 依赖 ARCH-DEV-001 | r4 checklist `Status: owner_accepted`；其同 session factual limitation 与 Human Owner acceptance 均保留。 |
| 主机与工具 | macOS Darwin 24.6.0 arm64；Git 2.50.1。未运行项目代码测试或运行时操作，本任务仅验证文档、Git refs、路径和 source-only 边界。 |
| QA 起点 | checkout 为 `main`；创建 checklist 前 `git status --short --branch` 仅显示 `## main...origin/main` 与 `tasks.md` 未暂存 handoff diff；`git diff --cached --quiet` exit `0`。 |

## 3. Bundle metadata、交接与写面检查

| 检查 | 命令/证据 | 结果 |
| --- | --- | --- |
| PM/Development metadata | 读取 `spec.md` 与 `tasks.md` 首部 metadata | 两者均为 Task ID `ARCH-REL-001`、Revision `r3`；spec=`owner_approved`、tasks=`developer_handoff`；QA metadata 与 Human Owner acceptance 结果见 §10。 |
| Verification gate | `test ! -e plans/ARCH-REL-001-source-release-1.0.0/checklist.md`（创建前） | exit `0`；无提前 checklist。 |
| 当前 worktree/index | `git status --short --branch`; `git diff --name-status --no-renames`; `git diff --cached --quiet`; `git diff --check` | 当前仅有 `M plans/ARCH-REL-001-source-release-1.0.0/tasks.md`；index 为空（exit `0`）；whitespace check 无输出（exit `0`）。这是 handoff 产生的预期 Development diff。 |
| r3 release-preparation commit | `git show --format='%H%n%P%n%s' --no-patch HEAD`；`git diff-tree --no-commit-id --name-status --no-renames -r HEAD`；`git diff --check HEAD^ HEAD` | HEAD=`b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`，parent=`f5f41550a60f439040f8c84540210cd0f2bab3aa`，message=`Clarify source release branch and tag model`；commit diff exit `0`。 |
| exact r3 commit allowlist | 将 HEAD 的 12 个路径与 spec §5.3 逐项排序比较 | 精确 12 个 `M`：`AGENTS.md`、双语 README、双语 CHANGELOG、双语 PLAN、`docs/multi-project-pm.md`、双语 `plans/README.*`、r3 `spec.md`、r3 `tasks.md`；比较 exit `0`。 |
| staged/index scope | `git diff --cached --name-status --no-renames` | 无输出；Verification 未暂存任何路径。 |
| protected surfaces | `git diff --name-only HEAD^ HEAD -- CODE_INDEX.md contracts/ plans/ARCH-001-* plans/ARCH-MIG-001-* plans/ARCH-DOCKER-001-* plans/ARCH-DEV-001-*`；当前同范围 diff | 两次均为 0 行；`contracts/`、`CODE_INDEX.md` 和四项 accepted history 未进入 r3 commit 或当前 worktree。 |

Development 的 12-path commit 是本次源码定版准备的实现差异；当前未提交的单一
`tasks.md` 差异只记录 publication evidence 与 `developer_handoff`，没有改变实现或
release-preparation commit。未发现越界实现 failure，故不退回 Development。

本次精确 r3 allowlist（commit 中实际均为 `M`）为：

```text
AGENTS.md
README.md
README.zh-CN.md
CHANGELOG.md
CHANGELOG.zh-CN.md
PLAN.md
PLAN.zh-CN.md
docs/multi-project-pm.md
plans/README.md
plans/README.zh-CN.md
plans/ARCH-REL-001-source-release-1.0.0/spec.md
plans/ARCH-REL-001-source-release-1.0.0/tasks.md
```

## 4. Local/remote refs、annotated tag 与禁止目标

### 4.1 Local read-only ref verification

| 检查 | 结果 |
| --- | --- |
| checkout/main | `git symbolic-ref --short HEAD`=`main`；`HEAD`、`refs/heads/main`、`refs/remotes/origin/main` 均为 `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`。 |
| maintenance branch | `refs/heads/release/1.x.x` 与 `refs/remotes/origin/release/1.x.x` 均为 `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`。 |
| annotated tag | `git rev-parse refs/tags/v1.0.0`=`cf93268d4fea927fc27d463e75467c1eff9692fc`；`git cat-file -t refs/tags/v1.0.0`=`tag`；`git rev-parse 'refs/tags/v1.0.0^{}'`=`b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`。 |
| tag object content | `git cat-file -p refs/tags/v1.0.0` 显示 object=`b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac`、type=`commit`、tag=`v1.0.0`；annotation message=`AIIS ICS Architecture v1.0.0`。 |
| ref names | `git check-ref-format --branch release/1.x.x` 与 `git check-ref-format refs/tags/v1.0.0` 均 exit `0`。 |
| forbidden local refs | `refs/heads/release/1.0.0`、`refs/heads/release/2.x.x` 及对应 prohibited tag names 均 absent。 |

### 4.2 Remote read-only verification

命令：`git ls-remote --heads --tags origin main release/1.x.x release/2.x.x release/1.0.0 v1.0.0`。

- 普通 sandbox 查询因 `Could not resolve host: github.com` exit `128`；这是环境限制，不被改写为成功。
- 同一只读命令经精确网络授权重跑 exit `0`，实际输出仅为：

  ```text
  b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac  refs/heads/main
  b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac  refs/heads/release/1.x.x
  cf93268d4fea927fc27d463e75467c1eff9692fc  refs/tags/v1.0.0
  ```

远端没有返回 `release/2.x.x` 或 `release/1.0.0`。因此 `origin/main`、
`origin/release/1.x.x` 与 peeled `v1.0.0` 均与同一 release-preparation commit 一致，
tag object 与 peeled commit 的 OID 差异符合 annotated tag 语义。未执行 fetch 或任何 ref 写入。

## 5. 文档、allowlist、双语与 source-only 边界

| 检查 | 命令/结果 | 独立结论 |
| --- | --- | --- |
| active old-model scan | 对根 AGENTS、README/CHANGELOG/PLAN、双语 catalog、`docs/README.*` 与 `docs/multi-project-pm.md` 扫描 `release/<semver>`、`release/<version>`、`release/1.0.0`；exit `0` | active 稳定文档未把精确 `release/1.0.0` 或旧 `release/<semver>` 当作当前合同。任务 spec 的禁止项、tasks 的 preflight/禁止目标及 r2/r1 superseded 命令均已按历史/负向检查分类；旧命令明确标记不可执行。 |
| active current model | 扫描 active 文档中的 `main`、`release/1.x.x`、`release/2.x.x`、annotated `v1.0.0`、source-only boundary | 当前模型一致：`main` 为持续开发线；`release/1.x.x` 为可 fast-forward 的大版本维护线；精确版本由不可变 annotated tag 固定；不创建实体 `release/` 源码目录。 |
| canonical docs topology | `docs/README.md`、`docs/README.zh-CN.md`、`docs/multi-project-pm.md` 均存在；根 `multi-project-pm.md`、历史拼写 `mutil-project-pm.md`、`docs/PLAN.*`、`docs/plans/` 均 absent；物理 `release/` 目录 absent | `docs/` 仍为 root-PLAN-owned README-only support；canonical 路径唯一；无源码副本或目录型 release。 |
| durable document boundary | `docs/multi-project-pm.md` 的 command/OID residue scan 无 `git add/commit/push/branch/tag/ls-remote`、`release_commit` 或动态 release OID；exit `0` | copyable 命令、动态 OID、publication evidence 只保留在当前 r3 `tasks.md`，没有形成第二 release truth。 |
| bilingual heading symmetry | `rg '^#{1,6} '` heading counts：README `7/7`、CHANGELOG `2/2`、PLAN `4/4`、catalog `1/1`、`docs/README` `3/3` | 双语索引/稳定文档 heading 数量对称；所需 pair 和相互链接目标均存在。 |
| protected public contract | `contracts/` 是根 Core contract hub；commit/current protected-surface diff 均为空 | r3 没有移动、审计、改写或重新授权 `contracts/`。 |
| env/artifact/secret | `git check-ignore -v -- .env backend/.env frontend-js/.env control-agent/.env` exit `0`，四者均命中 `.gitignore:89`；commit path/secret scans 均 PASS | 未读取 env 值；r3 commit 无 `.env`、依赖目录、dist/build/cache/log/DB 文件，也无私钥、AKIA 或带凭据连接串命中。 |
| release/public boundary | 本地 `find` 未发现物理 `release/`、`dist`、`build`、`target` 目录；tasks/commit 只记录 source-only refs | 未发现 build artifact、GitHub Release/asset、部署或生产就绪实现；不把 tag/branch 验证扩大为这些外部状态的授权或平台 ACL 证明。 |

## 6. Governance checker 与可用验证输出

执行：`bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch`。

- 实际 exit `1`，输出仅为既有 accepted `plans/ARCH-001-public-architecture-baseline-extraction/checklist.md`
  的重复 `Handoff:` metadata（checker 报告两次：`expected 1, found 2`）。
- 该 defect 位于 ARCH-REL-001 r3 exact allowlist 外，且来自已接受历史 bundle；本轮未修改它，也未把
  checker exit `1` 写成 pass。
- 创建本 checklist 后只读重跑仍 exit `1`：除上述历史 duplicate 外，checker 报告双语
  `plans/README.*` 尚未链接本新 checklist。该链接与 PLAN/catalog 聚合状态属于 Human Owner final
  acceptance 后的 §5.4 main-only receipt 写面；QA 按“只能写 checklist.md”边界未越权修改。
- 当前 r3 新 checklist 只保留一条 metadata `Handoff:`，不会复制历史缺陷。上述两个 checker 原因均为已知
  的历史治理缺陷或当前 receipt 待办，不构成 ARCH-REL-001 实现 failure；如需治理修复或提前同步索引，
  应另立/回到独立治理任务或由 Human Owner 执行精确 receipt。

没有适用的后端、前端、Rust、Docker、数据库或现场测试需要在本任务中重跑。Development 已提供
文档/路径/ref/static 自检输出；本 QA 复核了其中的关键命令并独立重跑了 local/remote ref、tag、
allowlist、protected-surface、文档边界和 metadata 检查。不得因未运行越界 runtime 测试而宣称
release/deployment/production readiness。

## 7. Acceptance Audit（当前 QA 阶段）

| AC | 当前结论 | 独立证据与边界 |
| --- | --- | --- |
| AC-001 | 通过（依赖/角色链） | 四项依赖均有对应 Revision 的 Human Owner `owner_accepted`；r3 spec/tasks/checklist 角色链一致。根 PLAN/catalog 仍是 release-preparation 期间的聚合索引，后续 receipt 同步是生命周期 gate，不在本 checklist 代写。 |
| AC-002 | 通过 | active 双语稳定文档一致描述 `main`、大版本维护线与 annotated tags；active scan 无 `release/1.0.0` 当前权威。 |
| AC-003 | 通过 | 本地/远端 `release/1.x.x` 与 annotated `v1.0.0` 语义和对象验证通过；禁止的 `release/1.0.0`、`release/2.x.x` 未出现。 |
| AC-004 | 通过 | accepted 历史 task bundle、`contracts/`、`CODE_INDEX.md` 在 release commit 和当前 diff 中均无变化。 |
| AC-005 | 通过 | `docs/multi-project-pm.md` 只保留长期版本模型/顺序/任务入口；可复制命令、动态 OID 和 evidence 只在 r3 tasks。 |
| AC-006 | 通过 | HEAD release-preparation commit 精确 12-path allowlist；没有源码、env、secret、artifact、日志、DB 或 runtime 路径。 |
| AC-007 | 通过 | tasks 记录的发布前三方 main/空 index/目标 refs collision preflight 与本次最终 refs 复核相互一致；普通网络失败已作为 limitation 保留，授权只读复核成功。 |
| AC-008 | 通过 | `origin/main` 先存在 release-preparation commit；local/remote `release/1.x.x` 和 `v1.0.0` 均从同一 commit 复核，tag object 类型为 `tag`；不创建精确版本 branch。 |
| AC-009 | 通过 | fresh-context 独立复核同一 release commit、maintenance branch 语义、tag annotation、source-only 文档和 contract/public boundaries。 |
| AC-010 | 通过（受边界限制） | 本地 diff/ref 和 tasks evidence 未显示 GitHub Release、asset、deployment 或 settings 写入；本轮不查询/声称平台 ACL、强制路由或外部发布页面。 |
| AC-011 | 通过 | r1/r2 superseded history 保留；r3 tasks 已 `developer_handoff`，本 checklist 为 fresh-context QA authority；QA verdict 与 Human Owner final acceptance 分离，接受结果见 §10。 |
| AC-012 | 延后 gate，不是 QA failure | Human Owner final acceptance 已记录；§5.4 main-only governance receipt 仍待 Human Owner 手工追加并 push，当前不声称 receipt 完成，也不移动 tag 或 fast-forward maintenance branch。 |

## 8. Blockers、限制与返工路由

### Blockers

本轮未发现 ARCH-REL-001 r3 实现 failure、allowlist 外 release commit、ref/tag OID 不一致、
禁止目标 ref collision、active `release/1.0.0` 权威、`contracts/`/accepted history 变更或
需要返工的 source-only 文档越界。因此不退回 Development，verdict 为 `qa_passed`。

### Limitations and deferred gates

1. 普通 sandbox 无法解析 `github.com`，`git ls-remote` 首次 exit `128`；同一只读命令经精确网络授权
   exit `0`。本地/远端证据以成功授权重跑为准，失败原始事实保留，不代表 Human Owner 的完整 transcript。
2. Human Owner 原始回传未包含每一条 publication 命令的完整 stdout/stderr/exit-code transcript；tasks
   明确区分了该证据来源，Development/QA 只记录可独立复核的 OID、对象类型和 remote 输出，没有补造缺失
   的逐条人工退出码。
3. 本轮未执行 Docker、数据库、PLC/CA、部署、GitHub Release 页面/asset、branch protection/settings、
   package registry 或生产检查；这些是 spec 明确排除的外部/后续 gate，不由本 verdict 推断为已完成。
4. 根 `PLAN.*` 与 `plans/README.*` 当前仍显示 `implementation_in_progress`/pending handoff，
   这是首个 release commit 后、Human Owner final acceptance 已记录但 main-only receipt 尚未 push 的
   聚合待办；本 QA 不越权修改这些文件。Receipt 时须由 Human Owner 只在 §5.4 allowlist 内同步真实阶段
   与本 checklist 状态。
5. project-governance checker 的 ARCH-001 duplicate `Handoff:` 是已接受历史、越界的治理 limitation，
   不是本任务实现 failure；不在本轮修复。

若后续发现实际 ref、文档、范围或 allowlist mismatch，必须以精确证据返回 Development 并停止当前
Revision；任何 material scope/acceptance/risk/Execution Mode/allowlist 变化都必须回 PM 建立新 Revision。
不得在本 checklist 静默修复实现或治理。

## 9. QA verdict 与 Human Owner 交接

**QA verdict: `qa_passed`**

ARCH-REL-001 r3 当前 fresh-context Verification scope 已通过：依赖接受状态、developer handoff
metadata、12-path release-preparation diff、空 index/current worktree 边界、local/remote refs、
annotated tag 与 peeled commit、禁止目标、active 双语/source-only 文档、canonical docs topology、
`contracts/`/accepted history 保护面和公开发布边界均有具体证据。已知治理 checker exit `1` 只来自
ARCH-001 accepted 历史 duplicate `Handoff:`，单独记录且未越界修复。

本 `qa_passed` evidence 已由 Human Owner 在 §10 确认接受；该 `owner_accepted` 仍不等于 GitHub Release、
部署、生产 readiness、平台 ACL、强制路由或任何未授权外部状态。其后 §5.4 main-only receipt 仍 pending；
receipt 不得移动 `v1.0.0`，也不得在本任务中 fast-forward `release/1.x.x`。

## 10. Human Owner final acceptance

Acceptance date: 2026-08-21
Acceptance authority: Human Owner
Exact acceptance: `接受 aiis-ics-arch::ARCH-REL-001 r3 Verification qa_passed，确认 Human Owner final acceptance；按 spec §5.4 由我手工追加 main-only governance receipt。`
Final status: `owner_accepted`

该接受仅确认本 checklist 已记录的 `qa_passed` Verification evidence，并不代替 §5.4
main-only governance receipt。剩余行动是 Human Owner 手工追加并 push 该 receipt；截至本记录尚未 push。
不得移动 `v1.0.0`、在本任务中 fast-forward `release/1.x.x`，或将 receipt 解释为 GitHub Release、部署、
生产 readiness、平台 ACL 或强制路由授权。
