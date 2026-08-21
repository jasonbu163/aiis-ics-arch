# ARCH-REL-001 1.0.0 源码定版 Development 记录

Task ID: ARCH-REL-001
Revision: r2
Status: implementation_in_progress
Owner Role: Development
Allowed Writers: Development
Handoff: pending Human Owner manual Git publication outputs; `developer_handoff` is not set

Task Namespace: aiis-ics-arch
PM Spec: [spec.md](spec.md)
Human Owner Approval: r2 已于 2026-08-20 精确批准
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner -> Development -> fresh-context QA / Verification -> Human Owner
Fresh Context: required for Verification
Required Development Skills: aiis, project-governance, code-document-indexer
Development Owner: Development agent
Development Date: 2026-08-20
Working Tree Base OID: `d11159e8f4a7ce62096a0b499f3b7a93b5da807b`
Git / GitHub Writes: Human Owner-only

## 1. r2 执行依据与阶段

- Human Owner 已批准精确 r2 spec 与 allowlist；r1 approval 和 Development 记录只作为 superseded history 保留，不授权继续使用旧路径或旧 staging 命令。
- Development 已完整读取根 `AGENTS.md`、双语 README/PLAN、r2 spec、r1 tasks 历史、项目 Development lifecycle workflow，以及 `aiis`、`project-governance`、`code-document-indexer` skills。
- 四项发布依赖均已有 Human Owner final acceptance：

| 依赖 | Revision | 最终事实 |
| --- | --- | --- |
| ARCH-001 | r3 | `owner_accepted` |
| ARCH-MIG-001 | r1 | `owner_accepted` |
| ARCH-DOCKER-001 | r1 | `owner_accepted` |
| ARCH-DEV-001 | r4 | `owner_accepted` |

- 当前仅完成 r2 Development release preparation。Human Owner 尚未执行暂存、commit、push 或 refs 创建；因此本记录保持 `implementation_in_progress`，不设置 `developer_handoff`，也不声称 `release/1.0.0` 或 `v1.0.0` 已发布。

## 2. r2 精确实现范围

Development 按以下顺序完成批准范围：

1. 保留 Human Owner 提供的工作树移动：删除根 `mutil-project-pm.md`，以 `docs/multi-project-pm.md` 作为 canonical 路径；未创建根 `multi-project-pm.md`。
2. 新增互链且对称的 `docs/README.md` / `docs/README.zh-CN.md`，声明 `docs/` 由根 PLAN 管理且不建立独立 PLAN/task registry。
3. 对 canonical 多仓文档仅做 current structural/path/release correction：登记当前 r2、根 `contracts/` Core 合同中心与 canonical docs 路径；移除重复的 copyable publication 命令和动态 OID，改为摘要并链接本文件。
4. 同步 AGENTS、双语根 README/CHANGELOG、PLAN/catalog 与 CODE_INDEX 的 source-only、docs path、root contracts hub 和无实体 `release/` 目录事实。
5. 将本文件从 r1 原地升级为 r2 权威 Development 事实面，并在 §9 保留 superseded r1 历史。
6. 完成只读/static Development self-check，并准备 §7 唯一 Human Owner 手工 Git 发布命令。

未修改 `contracts/`、accepted historical task bundles、源码、配置、Compose、env、runtime 或 `checklist.md`；未创建 `docs/PLAN.*`、`docs/plans/` 或实体 `release/` 目录。

## 3. r2 Development allowlist 与十六路径事实

Development 写面是以下十五项；Human Owner 第一个 release-preparation commit 还必须包含 PM-owned r2 `spec.md` diff，合计十六个路径事实：

| Path | 当前预期 Git 事实 | Owner |
| --- | --- | --- |
| `AGENTS.md` | modified | Development |
| `CODE_INDEX.md` | modified | Development |
| `README.md` | modified | Development |
| `README.zh-CN.md` | modified | Development |
| `CHANGELOG.md` | modified | Development |
| `CHANGELOG.zh-CN.md` | modified | Development |
| `PLAN.md` | modified | Development |
| `PLAN.zh-CN.md` | modified | Development |
| `docs/README.md` | added | Development |
| `docs/README.zh-CN.md` | added | Development |
| `docs/multi-project-pm.md` | added | Development / preserved Human Owner move input |
| `mutil-project-pm.md` | deleted | Development / preserved Human Owner move input |
| `plans/README.md` | modified | Development |
| `plans/README.zh-CN.md` | modified | Development |
| `plans/ARCH-REL-001-source-release-1.0.0/tasks.md` | added in the release-preparation commit; r1 history upgraded in place | Development |
| `plans/ARCH-REL-001-source-release-1.0.0/spec.md` | modified to approved r2 | PM |

任何额外路径都触发停止条件。cached 审核必须使用 `--no-renames`，确保旧根文件显示 `D`、三个 `docs/` 文件显示 `A`，而不是折叠为 rename。

## 4. 当前 preflight 事实

2026-08-20 Development 在写入前独立执行了只读 preflight：

| 检查 | 实际结果 |
| --- | --- |
| checkout / main OID | checkout 为 `main`；`HEAD`、`refs/heads/main`、本地 `refs/remotes/origin/main` 均为 `d11159e8f4a7ce62096a0b499f3b7a93b5da807b` |
| Git index | `git diff --cached --quiet` exit `0`，index 为空 |
| local target refs | `refs/heads/release/1.0.0` 与 `refs/tags/v1.0.0` 的 `git show-ref --verify --quiet` 均 exit `1`，表示不存在 |
| ref names | `git check-ref-format --branch release/1.0.0` 与 `git check-ref-format refs/tags/v1.0.0` 均 exit `0` |
| remote refs | sandbox 内首次 `git ls-remote` 因 `Could not resolve host: github.com` exit `128`；随后经只读网络授权重跑 exit `0`，只返回 `d11159e8f4a7ce62096a0b499f3b7a93b5da807b refs/heads/main`，目标 branch/tag 不存在 |
| Human Owner move | 写入前 `mutil-project-pm.md` 为 tracked deletion，`docs/multi-project-pm.md` 为 untracked addition；Development 保留该方向，没有回退或创建根正确拼写候选 |
| protected surfaces | `git diff --name-status --no-renames -- contracts/ <four accepted task paths>` 无输出 |

这些都是时点事实。Human Owner 真正发布前必须按 §7 重新执行碰撞、index 与 main 三方一致性检查；任一检查无法确认或结果变化即停止。

## 5. DEV self-check 证据

最终静态检查回填如下（全部是 Development 只读/本地 static 检查，不是 QA verdict）：

| 命令 / 检查 | 结果 |
| --- | --- |
| `git status --short --branch`；`git diff --name-status --no-renames` | worktree 精确为 16 个批准路径事实：12 个 tracked diff 加 4 个 untracked additions；index 为空，没有 allowlist 外路径 |
| exact 16-path allowlist audit；topology audit | porcelain expected/actual `diff` exit `0`、路径计数 `16`；三个 `docs/` 文件存在，根两个候选均不存在，`docs/PLAN.*` / `docs/plans/` / `checklist.md` 均不存在 |
| `git diff --check`；`git diff --cached --check`；untracked no-index whitespace check | 两项 Git check 均 exit `0`；cached 为空，四个 untracked 文件逐一 `--no-index --check` 无 whitespace 输出 |
| bilingual symmetry、Markdown links、active path / release residue scan | 根 README headings `6/6`、CHANGELOG bullets `8/8`、PLAN/catalog rows `7/7`、docs README headings `2/2` 且 bullets `4/4`；changed-doc relative-link checker exit `0`；canonical path 分类正确，durable 多仓文档无 copyable publication command / dynamic OID residue |
| ignore proof（不读取 env 值）；secret/artifact/path scan | `git check-ignore -v` 对根、backend、frontend-js、control-agent 四个 `.env` 路径均命中 `.gitignore:89`，tracked env 名称计数 `0`；高置信 secret 与工作树 artifact path 扫描无命中；未读取 env 内容 |
| §7 Human Owner copyable command compatibility | `rg` 命令依赖计数 `0`，两项扫描均使用 macOS 标准 `grep -E`；path/secret 正样例均 exit `0`、负样例均 exit `1`，当前空 index 上两项 gate 均无命中并继续 |
| `CODE_INDEX.md` scoped diff；`contracts/` / accepted history no-diff audit | CODE_INDEX 只替换 root contracts 描述、删除 stale physical `release/` entry并增加 docs/canonical entries；protected worktree audit exit `0`，基线 tree-list SHA-256=`dc1d5114adfdde9cfbacc60df54e35b9735b45697c92e0f471bc27c83012d646` |
| bundle metadata / checklist absence / ref-name / local+remote collision | spec=`r2/owner_approved`、tasks=`r2/implementation_in_progress`；ref names valid，local targets absent；最终只读远端查询 exit `0` 且只返回 `d11159e8f4a7ce62096a0b499f3b7a93b5da807b refs/heads/main` |
| project-governance checker | exit `1`；唯一命中是 out-of-allowlist accepted `ARCH-001/checklist.md` 既有 duplicate `Handoff:`（同一 `expected 1, found 2` 被 checker 报告两次）；未越界修复，也未误记为 pass |

## 6. Development 限制与剩余 gate

- Development 未运行且无权运行 `git add`、`git commit`、`git push`、`git branch`、`git tag` 或其他 Git/GitHub 写操作。
- 本任务是 source-only 文档与 ref 发布准备；未执行 Docker build/up/down、数据库 migration、真实 PLC/CA、部署、GitHub Release、asset 或 artifact 操作。
- 工作树有意保持未暂存，等待 Human Owner 审核并手工执行 §7；当前 index 仍应为空。
- Human Owner 返回完整命令、stdout/stderr、退出码、release commit OID、branch OID、tag object OID 与 peeled commit 前，不进入 `developer_handoff`。
- 发布后仍需 fresh-context Verification 创建 `checklist.md`；Development self-check 不构成 QA verdict 或 Human Owner final acceptance。

## 7. Human Owner 唯一手工 Git 发布命令

本节是当前 r2 唯一 copyable publication command surface。请在仓库根目录逐条执行并保留每条命令的 stdout、stderr 与退出码；任何一步失败即停止，不删除、移动、force-update 或重建 refs，不 rewrite history。

### 7.1 重新执行发布前 stop-condition preflight

```bash
test "$(git symbolic-ref --short HEAD)" = "main"
test "$(git rev-parse HEAD)" = "$(git rev-parse refs/heads/main)"
test "$(git rev-parse HEAD)" = "$(git rev-parse refs/remotes/origin/main)"
test -z "$(git diff --cached --name-only --no-renames)"
test -z "$(git branch --list release/1.0.0)"
test -z "$(git tag --list v1.0.0)"
git check-ref-format --branch release/1.0.0
git check-ref-format refs/tags/v1.0.0
git ls-remote --heads --tags origin main release/1.0.0 v1.0.0
```

预期：全部 exit `0`；最后一条只返回一个 `refs/heads/main`，其 OID 与本地 `HEAD` 完全相同。若 index 非空、三方 main 不同、任一目标 ref 已存在，或网络/权限导致远端无法核对，立即停止。

### 7.2 只暂存精确十六路径

禁止使用 `git add .` 或 `git add -A`。只运行：

```bash
git add -- \
  AGENTS.md \
  CODE_INDEX.md \
  README.md \
  README.zh-CN.md \
  CHANGELOG.md \
  CHANGELOG.zh-CN.md \
  PLAN.md \
  PLAN.zh-CN.md \
  docs/README.md \
  docs/README.zh-CN.md \
  docs/multi-project-pm.md \
  mutil-project-pm.md \
  plans/README.md \
  plans/README.zh-CN.md \
  plans/ARCH-REL-001-source-release-1.0.0/spec.md \
  plans/ARCH-REL-001-source-release-1.0.0/tasks.md
git diff --cached --check
git diff --cached --name-status --no-renames
git diff --cached --name-only --no-renames
```

`--name-status --no-renames` 必须精确显示十五项 Development 写面加一项 PM spec，共十六项；其中必须包含：

```text
A	docs/README.md
A	docs/README.zh-CN.md
A	docs/multi-project-pm.md
D	mutil-project-pm.md
```

且不得出现根 `multi-project-pm.md` 或任何 allowlist 外路径。随后运行机械路径、ignore 与 secret gate：

```bash
expected_paths=$(printf '%s\n' \
  AGENTS.md CODE_INDEX.md README.md README.zh-CN.md CHANGELOG.md CHANGELOG.zh-CN.md \
  PLAN.md PLAN.zh-CN.md docs/README.md docs/README.zh-CN.md docs/multi-project-pm.md \
  mutil-project-pm.md plans/README.md plans/README.zh-CN.md \
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

`git check-ignore` 只打印 ignore rule/path，不读取 env 内容；四个路径必须均被 ignore rule 命中。两项 `if ...; then exit 1` 扫描预期均无输出并继续，任何命中都停止。

### 7.3 创建唯一 preparation commit 并先 push main

```bash
git commit -m "chore: prepare AIIS ICS Architecture v1.0.0 source release"
git push origin main
release_commit=$(git rev-parse HEAD)
remote_main=$(git ls-remote --heads origin main | awk '{print $1}')
test "$release_commit" = "$remote_main"
printf '%s\n' "$release_commit"
```

预期：commit 与 push exit `0`，`release_commit` 为新提交且等于远端 `main` OID。若 push 或 OID 核对失败，停止，不创建 branch/tag。

### 7.4 从同一 OID 创建并分别 push 固定 refs

保持 checkout 在 `main`：

```bash
git branch release/1.0.0 "$release_commit"
git tag -a v1.0.0 "$release_commit" -m "AIIS ICS Architecture v1.0.0"
git push origin refs/heads/release/1.0.0:refs/heads/release/1.0.0
git push origin refs/tags/v1.0.0:refs/tags/v1.0.0
test "$(git symbolic-ref --short HEAD)" = "main"
git rev-parse refs/heads/main
git rev-parse refs/heads/release/1.0.0
git rev-parse refs/tags/v1.0.0
git rev-parse 'refs/tags/v1.0.0^{}'
git cat-file -t refs/tags/v1.0.0
git ls-remote --heads --tags origin main release/1.0.0 v1.0.0
```

预期：local/remote `main`、`release/1.0.0` 和 peeled `v1.0.0^{}` 均为 `$release_commit`；`git cat-file -t` 输出 `tag`，未 peeled tag ref 另有 tag object OID；checkout 仍为 `main`。请把全部原始输出和退出码返回 Development。

禁止 force push/tag、ref 删除、history rewrite、GitHub Release 页面/asset 创建或任何未授权外部状态变化。

## 8. Human Owner publication evidence（等待回填）

| Evidence | Value |
| --- | --- |
| release-preparation commit / remote main OID | Pending Human Owner execution |
| local / remote `release/1.0.0` OID | Pending Human Owner execution |
| annotated tag object OID | Pending Human Owner execution |
| peeled `v1.0.0^{}` OID | Pending Human Owner execution |
| exact command outputs and exit codes | Pending Human Owner execution |
| Development handoff | Not set; remains `implementation_in_progress` |

## 9. r1 superseded Development history

- r1 曾于 2026-08-11 获 Human Owner 精确批准，并形成 `Revision: r1` / `implementation_in_progress` 的 release-preparation Development 记录。
- r1 preflight 在基线 OID `d11159e8f4a7ce62096a0b499f3b7a93b5da807b` 上确认本地/远端 main 一致、index 为空、目标 refs 不存在，并完成当时十二路径文档 allowlist 的静态检查。
- r1 没有执行任何 Git/GitHub 写操作，没有创建或发布 release branch/tag，也没有进入 `developer_handoff` 或 fresh-context Verification。
- 2026-08-20 canonical docs path、`docs/` governance、CODE_INDEX 与 staged set 发生 material change，r1 执行授权被 superseded。旧根路径、旧十二路径 staging 命令和 r1 approval 不再是当前 publication authority，故不在本节重复为可复制命令。
- r2 延续 r1 的 source-only、Human Owner-only Git 权限与 collision stop conditions，同时以本文件 §7 取代全部旧 publication 命令。
