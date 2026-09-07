# ARCH-REL-001 1.0.0 源码定版 Development 记录

Task ID: ARCH-REL-001
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: `developer_handoff` -> fresh-context QA / Verification created the checklist and recorded `qa_passed`; Human Owner final acceptance is recorded there; §5.4 main-only receipt remains pending Human Owner manual push

Task Namespace: aiis-ics-arch
PM Spec: [spec.md](spec.md)
Human Owner Approval: r3 已于 2026-08-21 精确批准
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner -> Development -> fresh-context QA / Verification -> Human Owner
Fresh Context: required for Verification
Required Development Skills: aiis, project-governance, code-document-indexer
Development Owner: Development agent
Development Date: 2026-08-21
Working Tree Base OID: `f5f41550a60f439040f8c84540210cd0f2bab3aa`
Git / GitHub Writes: Human Owner-only

## 1. r3 执行依据与阶段

- Human Owner 已批准精确 r3 spec 与 allowlist；r1/r2 approval、Development 记录和 r2 main preparation
  commit 只作为 superseded history 保留，不授权继续使用旧发布模型或旧命令。
- Development 已完整读取根 `AGENTS.md`、双语 README/PLAN、`docs/README.*`、r3 spec、r2 tasks 及其
  superseded history、四项依赖任务的最终 accepted checklist、项目 Development lifecycle workflow，以及
  `aiis`、`project-governance`、`code-document-indexer` skills。
- 四项发布依赖均已有 Human Owner final acceptance：

| 依赖 | Revision | 最终事实 |
| --- | --- | --- |
| ARCH-001 | r3 | `owner_accepted` |
| ARCH-MIG-001 | r1 | `owner_accepted` |
| ARCH-DOCKER-001 | r1 | `owner_accepted` |
| ARCH-DEV-001 | r4 | `owner_accepted` |

- r3 只做 source-only 版本模型和长期文档同步。Development 未运行 `git add`、`commit`、`push`、
  `branch`、`tag` 或任何 Git/GitHub 写操作；fresh-context Verification 已在 handoff 后创建
  `checklist.md` 并独立完成验证。
- Human Owner 已完成并推送 r3 `main` release-preparation commit，创建并推送 `release/1.x.x` 与
  annotated `v1.0.0`；Development 回填本文件 §8 的 publication evidence 并进入
  `developer_handoff`。fresh-context Verification 已记录 `qa_passed`，Human Owner final acceptance
  已按原文记录在 checklist §10；该事实不把 Development 自检或 publication evidence 改写为 QA
  verdict，剩余 §5.4 receipt 仍由 Human Owner 手工追加并 push。

## 2. r3 精确实现范围

Development 按 r3 spec 完成以下 bounded preparation：

1. 将 active `AGENTS.md`、双语根 README、双语 CHANGELOG、双语 PLAN、双语 `plans/README.*` 与
   `docs/multi-project-pm.md` 统一为 `main` + 字面大版本维护分支 `release/1.x.x` / future
   `release/2.x.x` + immutable annotated tag 的 source-only 合同。
2. 明确 `release/1.x.x` 是可由未来独立获批任务 fast-forward 的 1.x 维护线，不是精确版本权威；精确版本
   只由 `v<major>.<minor>.<patch>` annotated tag 表达；本首次发布创建 `release/1.x.x` 与 `v1.0.0`。
3. 将本文件原地从 r2 升级为 `Revision: r3`，保留 r2/r1 facts 和旧
   publication commands 为 superseded history；已完成的 publication command 仅在 §7，当前 receipt
   command 仅在 §12。
4. 不修改 `CODE_INDEX.md`：r2 已完成 docs 结构变化，r3 只做版本语义同步；不修改 `contracts/`、accepted
   history、源码、配置、Docker、env、runtime 或任何未列入 §3 的路径。

## 3. r3 allowlist 与十二路径 staged-set

Development 写面是以下十一项；Human Owner 的第一个 r3 release-preparation commit 还必须包含 PM-owned
r3 `spec.md` diff，合计十二个路径。发布前 worktree 应只出现这十二项变化，index 由 Human Owner 暂存前保持
为空：

| Path | 预期 Git 事实 | Owner |
| --- | --- | --- |
| `AGENTS.md` | modified | Development |
| `README.md` | modified | Development |
| `README.zh-CN.md` | modified | Development |
| `CHANGELOG.md` | modified | Development |
| `CHANGELOG.zh-CN.md` | modified | Development |
| `PLAN.md` | modified | Development |
| `PLAN.zh-CN.md` | modified | Development |
| `docs/multi-project-pm.md` | modified | Development |
| `plans/README.md` | modified | Development |
| `plans/README.zh-CN.md` | modified | Development |
| `plans/ARCH-REL-001-source-release-1.0.0/tasks.md` | modified | Development |
| `plans/ARCH-REL-001-source-release-1.0.0/spec.md` | modified | PM |

任何额外路径都触发停止条件。cached 审核必须使用 `--no-renames`；r3 不应包含 `CODE_INDEX.md`、现有
`docs/README.*`、`contracts/`、accepted history、根 `multi-project-pm.md`、`docs/PLAN.*` 或
`docs/plans/`。

## 4. r3 发布前 preflight 事实

Development 在本次写入前执行了只读 preflight：

| 检查 | 实际结果 |
| --- | --- |
| checkout / main OID | checkout 为 `main`；`HEAD`、`refs/heads/main`、`refs/remotes/origin/main` 均为 `f5f41550a60f439040f8c84540210cd0f2bab3aa` |
| Git index | `git diff --cached --quiet` exit `0`，index 为空 |
| local target refs | `release/1.x.x`、`release/2.x.x`、`release/1.0.0` 与 `v1.0.0` 均不存在 |
| ref names | `release/1.x.x`、`release/2.x.x` 与 `v1.0.0` 的 ref-name 检查通过；`release/1.0.0` 仅作为禁止的 historical collision name 检查 |
| remote refs | 首次普通 sandbox 查询因 DNS `Could not resolve host: github.com` exit `128`；随后同一只读查询经精确网络授权重跑 exit `0`，只返回 `f5f41550a60f439040f8c84540210cd0f2bab3aa refs/heads/main` |
| protected surfaces | `contracts/`、`CODE_INDEX.md` 与四项 accepted task bundle 的 worktree diff 无输出 |
| docs topology | `docs/README.*` 与 `docs/multi-project-pm.md` 已存在；根 `multi-project-pm.md`、`docs/PLAN.*`、`docs/plans/` 不存在 |

以上均为发布前时点事实；Human Owner 发布前必须重新执行 §7.1。发布后的 refs 与只读复核见 §8；任一
main 分叉、index 非空、目标 ref collision、网络/权限失败或 allowlist 外变化均是停止条件。

## 5. r3 Development 记录

已按精确 allowlist 完成以下文档同步：

- `AGENTS.md`：更新长期 Git source-version boundary。
- 双语根 README：说明 `main`、大版本维护线和精确 annotated tags；消费方锁定 tag/commit。
- 双语 CHANGELOG：记录 1.0.0 source-only 定版顺序；动态 publication evidence 只归本文件 §8。
- 双语 PLAN 与 `plans/README.*`：本次 receipt preparation 将聚合索引从
  `implementation_in_progress`/pending handoff 同步为 `owner_accepted`，明确 `qa_passed` 与 Human
  Owner final acceptance 已记录，并保留 §5.4 main-only receipt pending 的边界。
- `docs/multi-project-pm.md`：只同步长期分支/tag 模型、发布顺序和任务入口；不复制当前命令、动态 OID
  或 evidence，不移动 `contracts/`。
- 本 `tasks.md`：将当前 Development authority 从 r2 升级为 r3，并把旧命令隔离为历史。

未修改 `CODE_INDEX.md`、`docs/README.*`、`contracts/`、accepted historical bundles、源码、配置、
Compose、env、runtime；`checklist.md` 仍由 Verification 独占维护，Development 未改写其 QA 或接受
结论。未创建 `release/` 源码目录、`release/1.0.0`、`release/2.x.x` 或 GitHub Release。

## 6. DEV self-check 证据

以下检查均为 Development 本地只读/static 证据，不是 Verification verdict 或 Human Owner final acceptance。

| 命令 / 检查 | 结果 |
| --- | --- |
| `git status --short --branch`；`git diff --name-status --no-renames` | receipt preparation 只允许 §5.4 六项 path：五项 receipt 文件修改 + Verification `checklist.md`；Human Owner staging 前 index 为空 |
| exact receipt-path worktree audit；topology audit | 期望/实际排序路径一致 exit `0`；根 `multi-project-pm.md`、`docs/PLAN.*`、`docs/plans/` 不存在，物理 `release/` 目录不存在 |
| `git diff --check`；`git diff --cached --check` | 两项 exit `0`；index 为空 |
| bilingual symmetry、Markdown links、active ref scan | 双语 heading 对称：README `7/7`、CHANGELOG `2/2`、PLAN `4/4`、catalog `1/1`、docs README `3/3`；changed-doc link check exit `0`；active old release-model scan exit `0` |
| ignore proof（不读取 env 值）；secret/artifact/path scan | 四个真实 `.env` 路径均被 ignore；secret、artifact path 和工作树敏感文件扫描无命中 |
| `grep -E` command compatibility | All Human Owner copyable scans use macOS standard `grep -E`; no `rg` dependency |
| `CODE_INDEX.md`、`contracts/` / accepted history no-diff audit | `git diff --name-only` protected-surface audit exit `0`；`CODE_INDEX.md`、`contracts/` 与四项 accepted bundle 无 diff |
| final bundle metadata / receipt preflight basis | spec=`r3/owner_approved`、tasks=`r3/developer_handoff`、checklist=`r3/owner_accepted`；本地/远端 release refs 已按发布证据复核；receipt staging 前 index 必须为空 |
| project-governance checker | `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch` exit `1`，仅报告既有 accepted `ARCH-001/checklist.md` duplicate `Handoff:` metadata（checker 输出两次）；该 out-of-allowlist limitation 未修复 |
| post-publication refs / local state read-only recheck | local `rev-parse`/`cat-file` group exit `0`；授权 `git ls-remote --heads --tags ...` exit `0`；`main`、`release/1.x.x`、annotated tag object、peeled commit 与 `tag` 类型见 §8；publication checkpoint clean `main` |
| receipt-preparation self-check | `git diff --check` 与五项 receipt 文件范围检查 exit `0`；checklist metadata 为 `Status=owner_accepted`；tasks 保持 `Status=developer_handoff`，并明确 §5.4 receipt 尚未 push |

## 7. 已完成的 Human Owner r3 Git 发布命令（历史记录，禁止重跑）

本节保留首次 r3 publication 所用命令及 preflight，作为已经完成动作的可审计历史；不得因本 receipt
重新执行、移动、force-update、删除或重建任何 refs。当前唯一可执行的命令面仅为 §12 的 main-only
governance receipt。

### 7.1 发布前 stop-condition preflight（历史；不得重跑）

```bash
test "$(git symbolic-ref --short HEAD)" = "main"
test "$(git rev-parse HEAD)" = "$(git rev-parse refs/heads/main)"
test "$(git rev-parse HEAD)" = "$(git rev-parse refs/remotes/origin/main)"
test -z "$(git diff --cached --name-only --no-renames)"
test -z "$(git branch --list 'release/1.x.x')"
test -z "$(git tag --list 'v1.0.0')"
git check-ref-format --branch 'release/1.x.x'
git check-ref-format 'refs/tags/v1.0.0'
git ls-remote --heads --tags origin main release/1.x.x release/2.x.x release/1.0.0 v1.0.0
```

预期全部 exit `0`；最后一条只返回远端 `main`，其 OID 等于本地 `HEAD`。若 index 非空、三方 main 不同、
任一目标 ref 已存在、出现 `release/1.0.0` 或远端无法核对，立即停止。

### 7.2 只暂存精确十二路径（历史；不得重跑）

禁止 `git add .` 或 `git add -A`。Human Owner 只运行：

```bash
git add -- \
  AGENTS.md \
  README.md \
  README.zh-CN.md \
  CHANGELOG.md \
  CHANGELOG.zh-CN.md \
  PLAN.md \
  PLAN.zh-CN.md \
  docs/multi-project-pm.md \
  plans/README.md \
  plans/README.zh-CN.md \
  plans/ARCH-REL-001-source-release-1.0.0/spec.md \
  plans/ARCH-REL-001-source-release-1.0.0/tasks.md
git diff --cached --check
git diff --cached --name-status --no-renames
git diff --cached --name-only --no-renames
```

`--name-status --no-renames` 必须精确显示十二项 `M`，且不得出现 `CODE_INDEX.md`、`docs/README.*`、
`contracts/`、accepted history、根 `multi-project-pm.md` 或其他 allowlist 外路径。随后运行机械 gate：

```bash
expected_paths=$(printf '%s\n' \
  AGENTS.md README.md README.zh-CN.md CHANGELOG.md CHANGELOG.zh-CN.md \
  PLAN.md PLAN.zh-CN.md docs/multi-project-pm.md plans/README.md plans/README.zh-CN.md \
  plans/ARCH-REL-001-source-release-1.0.0/spec.md \
  plans/ARCH-REL-001-source-release-1.0.0/tasks.md | LC_ALL=C sort)
actual_paths=$(git diff --cached --name-only --no-renames | LC_ALL=C sort)
test "$actual_paths" = "$expected_paths"
test ! -e multi-project-pm.md
test ! -e docs/PLAN.md
test ! -e docs/PLAN.zh-CN.md
test ! -d docs/plans
git check-ignore -v -- .env backend/.env frontend-js/.env control-agent/.env
if git diff --cached --name-only --no-renames | grep -E '(^|/)(\.env($|\.)|node_modules|dist|__pycache__|\.venv|\.log$|\.sql$|\.db$)'; then exit 1; fi
if git diff --cached -U0 --no-renames | grep -E 'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|AKIA[0-9A-Z]{16}|(mysql|postgres(ql)?|mssql)://[^[:space:]]+:[^[:space:]@]+@'; then exit 1; fi
```

`git check-ignore` 只打印 ignore rule/path，不读取 env 内容；四个路径必须均命中 ignore rule。两项
`grep -E` 扫描预期均无输出并继续，任何命中都停止。

### 7.3 创建唯一 r3 release-preparation commit 并先 push main（历史；不得重跑）

```bash
git commit -m "chore: prepare AIIS ICS Architecture v1.0.0 r3 release"
git push origin main
release_commit=$(git rev-parse HEAD)
remote_main=$(git ls-remote --heads origin main | awk '{print $1}')
test "$release_commit" = "$remote_main"
printf '%s\n' "$release_commit"
```

预期 commit 与 push exit `0`，`release_commit` 为新的 r3 preparation commit 且等于远端 `main` OID。若
push 或 OID 核对失败，停止，不创建 maintenance branch/tag。

### 7.4 从同一 release commit 创建并分别 push 固定 refs（历史；不得重跑）

保持 checkout 在 `main`。创建前再次确认远端目标仍无 collision：

```bash
test -z "$(git ls-remote --heads --tags origin release/1.x.x v1.0.0)"
git branch release/1.x.x "$release_commit"
git tag -a v1.0.0 "$release_commit" -m "AIIS ICS Architecture v1.0.0"
git push origin refs/heads/release/1.x.x:refs/heads/release/1.x.x
git push origin refs/tags/v1.0.0:refs/tags/v1.0.0
test "$(git symbolic-ref --short HEAD)" = "main"
git rev-parse refs/heads/main
git rev-parse refs/heads/release/1.x.x
git rev-parse refs/tags/v1.0.0
git rev-parse 'refs/tags/v1.0.0^{}'
git cat-file -t refs/tags/v1.0.0
git ls-remote --heads --tags origin main release/1.x.x release/2.x.x v1.0.0
```

预期 local/remote `main`、`release/1.x.x` 和 peeled `v1.0.0^{}` 均为 `$release_commit`；未 peeled tag
ref 另有 annotated tag object OID，`git cat-file -t refs/tags/v1.0.0` 输出 `tag`，checkout 仍为 `main`。
`release/1.x.x` 是可维护的 1.x branch，不是精确版本 authority；本任务不创建 `release/1.0.0`。

禁止 force push/tag、ref 删除、history rewrite、GitHub Release 页面/asset 创建或任何未授权外部状态变化。

## 8. Human Owner publication evidence（r3 Development handoff）

Human Owner 已完成 r3 手工 publication sequence：先将 release-preparation commit 推送到 `main`，再从
同一 commit 创建并推送 `release/1.x.x` 与 annotated `v1.0.0`。这只证明 Human Owner 已执行获批的 Git
publication gate，不构成 QA verdict、Human Owner final acceptance、GitHub Release、部署或生产授权。

证据来源必须区分：Human Owner 提供给协调侧的原始输出只覆盖 `git cat-file -t refs/tags/v1.0.0` 与
`git ls-remote --heads --tags origin main release/1.x.x release/2.x.x release/1.0.0 v1.0.0` 两个
检查的结果；未提供完整的逐条 stdout/stderr/exit-code transcript，因此本节不补造不存在的 Human Owner
逐条退出码。以下 OID、peeled commit、tag type 和工作树状态由 Development/协调侧以只读命令独立复核。

| Evidence | Value | Source and boundary |
| --- | --- | --- |
| r3 release-preparation commit / local `main` / tracking `origin/main` / remote `main` | `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac` | Human Owner 已完成并推送；协调侧 `git rev-parse HEAD`、`git rev-parse refs/heads/main`、`git rev-parse refs/remotes/origin/main` 及授权只读 `git ls-remote` 均复核为该 OID。 |
| local / remote `release/1.x.x` OID | `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac` | 协调侧 `git rev-parse refs/heads/release/1.x.x` 与授权只读 `git ls-remote` 复核；与 release-preparation commit 相同。 |
| annotated tag object OID | `cf93268d4fea927fc27d463e75467c1eff9692fc` | 协调侧只读 `git rev-parse refs/tags/v1.0.0` 复核；该对象类型另由 `git cat-file -t refs/tags/v1.0.0` 复核为 `tag`。 |
| peeled `v1.0.0^{}` commit OID | `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac` | 协调侧只读 `git rev-parse 'refs/tags/v1.0.0^{}'` 复核；与 `main` 和 `release/1.x.x` 相同。 |
| tag type | `tag` | Human Owner 原始回传覆盖了 `git cat-file` 检查；协调侧再次只读复核，未执行任何 tag 写操作。 |
| remote read-only recheck output | `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac refs/heads/main`; `b6c36a8c7eb7bb229f6bc7798d74e08a97e288ac refs/heads/release/1.x.x`; `cf93268d4fea927fc27d463e75467c1eff9692fc refs/tags/v1.0.0` | 精确授权重跑 `git ls-remote --heads --tags origin main release/1.x.x release/2.x.x release/1.0.0 v1.0.0` exit `0`；输出未把 `release/1.0.0` 或 `release/2.x.x` 列为存在。 |
| publication-time worktree / checkout | `git status --short --branch` exit `0`，输出仅 `## main...origin/main`；checkout 为 `main` | 协调侧只读复核发生在本次 tasks.md handoff 写入前；当前 §5.4 receipt preparation 只允许五项 receipt 文件与 Verification checklist 的变化，Human Owner staging 前 index 必须为空。 |
| exact command-output limitation | Human Owner 原始回传没有完整逐条退出码；协调侧普通 sandbox `git ls-remote` 因 DNS 失败 exit `128`，随后精确网络授权只读重跑 exit `0` | 这是环境/证据来源限制，不改写为 Human Owner 成功 transcript；Development 未执行任何 Git/GitHub 写操作。 |
| Development handoff | `developer_handoff` | fresh-context QA / Verification 已创建 checklist 并独立复核 refs、tag annotation、source-only boundary 与本节证据；verdict=`qa_passed`，Human Owner final acceptance 已记录，§5.4 receipt 仍待 Human Owner 手工 push。 |

## 9. r2 superseded Development history

- r2 于 2026-08-20 获 Human Owner 精确批准，Development 在基线 `d11159e8f4a7ce62096a0b499f3b7a93b5da807b` 上
  完成 docs move、双语 `docs/README.*`、root contracts hub wording、CODE_INDEX 与 source-only
  `release/1.0.0` preparation；其工作树差异随后由 Human Owner 以 main preparation commit
  `f5f41550a60f439040f8c84540210cd0f2bab3aa` 推送。
- r2 的十六路径 staged set 包含当时的 `CODE_INDEX.md`、docs README/new canonical path、根拼写错误文件
  删除、r2 spec 与 r2 tasks；这些结果已成为当前 `main` 的历史输入，r3 不重复修改或重演 docs move。
- r2 没有执行 Git/GitHub 写操作以外的 Development 禁止动作，没有创建 `release/1.0.0` 或 `v1.0.0`，
  没有进入 `developer_handoff`、fresh-context Verification 或 final acceptance。
- 下列旧命令仅为审计保留，已经 superseded，禁止复制执行；r3 当前 publication authority 只在 §7：

```bash
# superseded r2 history — do not run
git branch release/1.0.0 "$release_commit"
git tag -a v1.0.0 "$release_commit" -m "AIIS ICS Architecture v1.0.0"
git push origin refs/heads/release/1.0.0:refs/heads/release/1.0.0
```

## 10. r1 superseded Development history

- r1 于 2026-08-11 获 Human Owner 精确批准，并形成 `Revision: r1` / `implementation_in_progress` 的
  source-release preparation 记录。
- r1 在基线 `d11159e8f4a7ce62096a0b499f3b7a93b5da807b` 上确认当时 local/remote main 一致、index 为空、
  当时的精确版本 branch/tag 不存在，并完成其旧文档 allowlist 的 static self-check。
- r1 没有执行 Git/GitHub 写操作，没有创建 release refs，没有进入 `developer_handoff`、QA 或 final
  acceptance。r1 的 `release/1.0.0` 目标和命令因 r2、再因 r3 的 material release-model change 被
  superseded；不作为当前执行依据。

## 11. Development 限制与 handoff

- Development 未运行且无权运行任何 Git/GitHub 写操作；本节只记录 Human Owner 已完成的手工 §7 gate
  与协调侧只读复核。
- 本任务仅验证文档、路径、引用、ref 名称和 source-only release boundary；未运行 Docker build/up/down、
  数据库 migration、真实 PLC/CA、部署、GitHub Release、asset 或 artifact 操作。
- `checklist.md` 已由本次 `developer_handoff` 后的 fresh-context Verification 创建并记录 `qa_passed`；
  Human Owner final acceptance 已按原文记录在 checklist §10。Development 不修改 checklist，也不把
  `owner_accepted` 改成 Development status。
- 精确 handoff：Task ID `ARCH-REL-001` / Revision `r3`；publication commit 与 refs 已在 §8 记录；
  receipt preparation 只更新 §5.4 允许的五个非 checklist 文件，当前 index 必须保持为空。剩余
  main-only receipt 由 Human Owner 手工 staging、commit、push；未执行前不得宣称 receipt 完成。
- Development self-check 不构成 QA verdict、Human Owner final acceptance、平台 ACL、强制路由、发布部署或
  生产授权。

## 12. Human Owner §5.4 main-only governance receipt command

本节是当前唯一的 receipt command surface；它不重建 §7 的已完成 publication sequence。请在仓库根目录
逐条执行并保留 stdout、stderr 与退出码。任何一步失败立即停止，不删除、移动、force-update 或重建
任何 release ref，也不继续执行后续命令。receipt 只提交到当前 main，不创建 release/2.x.x。

```bash
release_commit=$(git rev-parse 'refs/tags/v1.0.0^{}')
tag_object=$(git rev-parse refs/tags/v1.0.0)
expected_paths=$(printf '%s\n' \
  PLAN.md \
  PLAN.zh-CN.md \
  plans/README.md \
  plans/README.zh-CN.md \
  plans/ARCH-REL-001-source-release-1.0.0/tasks.md \
  plans/ARCH-REL-001-source-release-1.0.0/checklist.md | LC_ALL=C sort)
actual_worktree_paths=$(git status --short | awk '{print substr($0,4)}' | LC_ALL=C sort)
test "$actual_worktree_paths" = "$expected_paths"
test "$(git symbolic-ref --short HEAD)" = "main"
test "$(git rev-parse HEAD)" = "$release_commit"
test "$(git rev-parse refs/heads/main)" = "$release_commit"
test "$(git rev-parse refs/remotes/origin/main)" = "$release_commit"
test -z "$(git diff --cached --name-only --no-renames)"
test "$(git cat-file -t refs/tags/v1.0.0)" = "tag"
test "$(git rev-parse refs/heads/release/1.x.x)" = "$release_commit"
test -z "$(git branch --list 'release/2.x.x')"
test -z "$(git ls-remote --heads origin refs/heads/release/2.x.x)"
remote_main_before=$(git ls-remote --heads origin refs/heads/main | awk '$2 == "refs/heads/main" {print $1}')
remote_release_before=$(git ls-remote --heads origin refs/heads/release/1.x.x | awk '$2 == "refs/heads/release/1.x.x" {print $1}')
remote_tag_before=$(git ls-remote --tags origin refs/tags/v1.0.0 | awk '$2 == "refs/tags/v1.0.0" {print $1}')
test "$remote_main_before" = "$release_commit"
test "$remote_release_before" = "$release_commit"
test "$remote_tag_before" = "$tag_object"

git add -- \
  PLAN.md \
  PLAN.zh-CN.md \
  plans/README.md \
  plans/README.zh-CN.md \
  plans/ARCH-REL-001-source-release-1.0.0/tasks.md \
  plans/ARCH-REL-001-source-release-1.0.0/checklist.md
git diff --cached --check
git diff --cached --name-status --no-renames
actual_paths=$(git diff --cached --name-only --no-renames | LC_ALL=C sort)
test "$actual_paths" = "$expected_paths"
expected_status=$( {
  printf 'M\t%s\n' \
    PLAN.md \
    PLAN.zh-CN.md \
    plans/README.md \
    plans/README.zh-CN.md \
    plans/ARCH-REL-001-source-release-1.0.0/tasks.md
  printf 'A\t%s\n' \
    plans/ARCH-REL-001-source-release-1.0.0/checklist.md
} | LC_ALL=C sort)
actual_status=$(git diff --cached --name-status --no-renames | LC_ALL=C sort)
test "$actual_status" = "$expected_status"
test -z "$(git diff --cached --diff-filter=R --name-only --no-renames)"
if git diff --cached --name-only --no-renames | grep -E '(^|/)(\.env($|\.)|node_modules|dist|build|target|__pycache__|\.venv|\.log$|\.sql$|\.db$)'; then exit 1; fi

git commit -m "chore: record v1.0.0 release acceptance"
git push origin HEAD:refs/heads/main
post_main=$(git ls-remote --heads origin refs/heads/main | awk '$2 == "refs/heads/main" {print $1}')
test "$post_main" = "$(git rev-parse HEAD)"
test "$post_main" != "$release_commit"
git merge-base --is-ancestor "$release_commit" "$post_main"
test "$(git symbolic-ref --short HEAD)" = "main"
test "$(git rev-parse refs/heads/release/1.x.x)" = "$release_commit"
test "$(git rev-parse refs/tags/v1.0.0)" = "$tag_object"
test "$(git rev-parse 'refs/tags/v1.0.0^{}')" = "$release_commit"
test "$(git cat-file -t refs/tags/v1.0.0)" = "tag"
remote_release_after=$(git ls-remote --heads origin refs/heads/release/1.x.x | awk '$2 == "refs/heads/release/1.x.x" {print $1}')
remote_tag_after=$(git ls-remote --tags origin refs/tags/v1.0.0 | awk '$2 == "refs/tags/v1.0.0" {print $1}')
test "$remote_release_after" = "$remote_release_before"
test "$remote_tag_after" = "$remote_tag_before"
test -z "$(git branch --list 'release/2.x.x')"
test -z "$(git ls-remote --heads origin refs/heads/release/2.x.x)"
test -z "$(git status --short)"
```

以上命令只把本节六项路径追加到 main；不会修改 release/1.x.x、v1.0.0 或任何禁止目标。命令
完成前，qa_passed 与 Human Owner final acceptance 已记录，但 §5.4 receipt 仍应视为 pending。
