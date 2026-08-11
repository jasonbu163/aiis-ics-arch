# ARCH-001 公开架构基线去项目化与一致性恢复 — QA / Verification Checklist

Task ID: ARCH-001  
Revision: r3  
Status: owner_accepted  
Owner Role: QA / Verification  
Allowed Writers: QA / Verification, Human Owner  
Handoff: Human Owner accepted and closed ARCH-001 r3; no release, deployment, Git/GitHub, external I/O or production authorization  

Task Namespace: aiis-ics-arch  
Execution Mode: agent_team_same_session  
Verification Context: fresh-context Verification, independent of Development reasoning  
Verification Date: 2026-08-10  
Verification Root: /Users/jason/Desktop/DreamCode/aiis-ics-arch  
Role Separation: independent QA / Verification; only this checklist was written by Verification  

## 1. Verification basis and hard boundaries

This fresh context independently read the target root AGENTS.md, bilingual root README.* and PLAN.*,
the touched backend/, frontend-js/, and control-agent/ bilingual README/PLAN pairs, root
INITIALIZATION.*, plans/README.*, the complete ARCH-001 r3 spec.md and r3 tasks.md, the prior
ARCH-001 r2 checklist, and the complete owner-accepted ARCH-MIG-001 r1 and ARCH-DOCKER-001 r1 bundles.
The applicable aiis, project-governance, docker-expert, docker-project-ops, backend-arch plus
references/DATABASE_AND_MIGRATIONS.md, and code-document-indexer instructions were read before verification.

Verification only updated this checklist.md. It did not modify spec.md, tasks.md, source, Models,
API/Service/settings, migration, tests, lockfiles, Dockerfiles outside the approved implementation, Compose,
README/PLAN/INITIALIZATION/index files, AGENTS.md, LICENSE, dependency bundles, other task files, or any
external repository. No Git/GitHub, release/tag, deployment, real/external/non-empty database, PLC, Control
Agent, Celery/Redis/Worker, or production action was run. No Docker prune or broad resource cleanup was used.

The target directory is not a Git worktree. Consequently, Git diff cannot prove Development provenance. The
allowlist audit below uses the r3 task record, r2 accepted baseline evidence, current path/content/structure,
start/end mtime and SHA-256 checks for read-only boundaries, dependency bundle metadata, and exact Docker
resource cleanup. This limitation is stated rather than replaced with a fabricated diff.

## 2. Immutable ARCH-001 r2 history summary

Before writing this r3 authority surface, the prior checklist was read in full. Its historical metadata and
verdict were:

- Revision r2, Status qa_blocked, with the handoff returning AC-001 to Development/PM.
- Historical blockers were the r2 role-metadata lifecycle mismatch (AC-001), project-era migration truth
  requiring the now-separate ARCH-MIG-001 task (AC-006), and the then-missing Human Owner license decision
  (AC-013).
- r2 did not run Docker lifecycle and recorded the absence of the later migration/smoke proof.

Those facts remain historical context only. They are not silently relabeled as r3 evidence. ARCH-MIG-001 r1
and ARCH-DOCKER-001 r1 are independently owner-accepted dependencies; the r3 evidence and verdict begin below.

## 3. Environment, prerequisites and safe temporary state

| Area | Evidence and result |
| --- | --- |
| Host/runtime | macOS arm64; Docker context desktop-linux; Docker client/server 29.6.2; Compose v5.3.1; daemon linux/aarch64, overlayfs. |
| Docker socket | Ordinary sandbox access returned permission denied. Each daemon command used an exact require_escalated call restricted to the named project/image/resource operation; no permission bypass or unrelated resource query was used. |
| Backend static environment | In backend/, UV_CACHE_DIR=/private/tmp/arch001-r3-uv-cache uv lock --check resolved 81 packages and exited 0. PYTHONPYCACHEPREFIX=/private/tmp/arch001-r3-compile uv run --no-project python -m compileall -q app core database projection scripts tests main.py build.py exited 0. |
| Host focused pytest limitation | Direct host python3 -m pytest -q tests/test_core_migration_baseline.py could not import the project settings under system Python 3.9 (TypeError: unsupported operand type(s) for |); uv isolated 3.13 had no project pytest/SQLAlchemy wheels. This is an environment limitation, not an implementation pass claim. An isolated Python 3.11 recorder independently executed the real migration operations, and the Docker runtime executed the production dependency environment. |
| Temporary env policy | backend/.env.docker.smoke, backend/.env.docker.dev, frontend-js/.env.docker.dev, and backend/.env.docker.prod were each created once by copying the corresponding sanitized .example and replacing only local one-time placeholders with non-printed random values; mode 0600. No deleted real env was read, printed, hashed, copied, restored, or referenced. |
| Cleanup of temporary files | All four temporary env files were removed after their respective lifecycle; the six r3 real-env targets are absent. Dev source binds created only task-attributable backend/logs files and empty backend/.venv/frontend-js/node_modules mountpoints; those exact generated artifacts were removed. Pre-existing backend/data/README.* and backend/data/migrations/ were preserved. |
| External fixture boundary | No safe task-exclusive external DB fixture existed, so release-check was limited to config/build as required. No real or external database was started. |

## 4. Static and governance verification

### 4.1 Bundle metadata, deletion-only targets and ownership boundaries

| Check | Command/evidence | Result |
| --- | --- | --- |
| r3 role chain | Read first metadata lines of ARCH-001 spec.md, tasks.md, and this file | ARCH-001 / r3 is consistent; PM owner_approved, Development developer_handoff, QA qa_passed; Execution Mode is agent_team_same_session. The r2 summary above is retained. |
| Accepted dependencies | Read all three files for ARCH-MIG-001 and ARCH-DOCKER-001 | Both remain r1; PM owner_approved, Development developer_handoff, QA/Human Owner owner_accepted. Their files were not changed. |
| Nested project history | for d in backend/plans frontend-js/plans control-agent/plans; do test -e "$d"; done plus path/type checks | All three exact deletion-only directories are ABSENT; root plans/ and both accepted dependency bundles remain present. |
| Six real runtime envs | Metadata-only test -e checks for backend/.env, backend/.env.docker.dev, backend/.env.docker.prod, frontend-js/.env, frontend-js/.env.docker.dev, control-agent/.env | All six are ABSENT. No content operation was performed on them. |
| Human Owner license intent | Read current LICENSE | Exact MIT text remains, including Copyright (c) 2026 Jason Boox; current SHA-256 is a3085aa852544aebbabcaf0a6434ad1a8ed678f9db4883b25e75cf668da5f13a. Verification did not edit it or infer legal publication authority. |

### 4.2 Public identity, permission, secret and artifact audit

| Audit | Command/evidence | Result and rationale |
| --- | --- | --- |
| Active identity/path scan | rg over current source, examples, Compose and stable docs for Vibe L2, vibe-l2, industrial_level_2_system, frontend-next, old resource names and project paths, excluding lockfiles and env values | No active runtime/package/module/path hit. Hits in mutil-project-pm.md and task narratives are historical migration-source names and explicit negative-scan examples, not active product identity; this is a documented public-safe rationale and the file is outside the r3 allowlist. |
| Permission scan | Read four r3-edited backend/frontend examples and frontend-js/.env.example / control-agent/.env.example | ROLE_API_PERMISSIONS_JSON='{}'; no dashboard/plan/performance/equipment/auxiliary/maintenance/quality permission set; frontend mock/demo/role access flags are false/empty; CA PLC/database/endpoint gates are false/blank. |
| Secret candidate scan | rg for connection strings, private-key headers and password/token/secret markers with manual classification | No real address, credential, token, key, certificate, DB dump or customer input. Remaining names are code fields, intentionally inert mock constants, placeholder example values, or documentation of the scan itself; no value was copied into an env, image or checklist. |
| Generated artifact scan | find for .venv, node_modules, target, dist, build, __pycache__, .pytest_cache, logs, .env (excluding .example), SQL/DB/dump/key files | Final generated-dir scan is empty. Env-like files are only the seven checked-in .example templates. No SQL/DB/dump/key/log files remain. |

### 4.3 Core module and migration truth audit

| Check | Evidence | Result |
| --- | --- | --- |
| Backend Core-only surface | find backend/app -mindepth 1 -maxdepth 1 -type d | Exactly user, system, control_agent, schema_maintenance, monitor, aiis_demo; no project business package. |
| Frontend Core-only surface | find frontend-js/src/app -mindepth 1 -maxdepth 1 -type d | Exactly system; no project page/module. |
| Deferred tasks | Active source scan for ARCH-FE-001 / CA-CONFIG-001 implementation paths | No implementation; each remains a draft PM-only spec. |
| Migration graph | Isolated Python 3.11 ScriptDirectory inspection (no app/settings import) | One active file 20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py; bases=['d4e6f8a0b2c4'], heads=['d4e6f8a0b2c4'], down_revision=None. |
| Actual migration operations | Independent recorder executed the current migration upgrade() and downgrade() | revision=d4e6f8a0b2c4; 14 create_table, 39 create_index, the single cycle FK fk_projection_mapping_set_active_revision; downgrade drops all 14 and leaves metadata empty. This is the actual operation surface, not a second hand-written schema. |
| Read-only implementation boundaries | Start/end SHA-256 and mtime checks for AGENTS.md, LICENSE, production Dockerfile, backend/frontend locks, migration, backend/settings.py, and backend/pyproject.toml | Hashes and mtimes were identical across QA. The no-Git limitation prevents proving earlier Development authorship, so current tasks evidence and this immutable read-only snapshot are retained as the honest boundary. |

## 5. Compose static verification

| Surface | Command/result | Independent conclusion |
| --- | --- | --- |
| Smoke | docker compose --project-name aiis-ics-arch-smoke --env-file backend/.env.docker.smoke -f docker-compose.smoke.yml config --quiet, then config --services / config --images | Exit 0; exactly mysql, migration, backend, frontend; mysql:8.4.6; task backend/frontend images only. |
| Dev | Fixed project aiis-ics-arch-dev config/services/profiles/images | Exit 0; default services are mysql, migration, backend, frontend; only profile is bootstrap; mysql:8.4.6; no fixed container_name, Vibe path, legacy resource name or tools/config mount. |
| Release-shaped | Fixed project aiis-ics-arch-release-check config/services/images | Exit 0; only backend and frontend; source contexts are backend/ and frontend-js/; no DB, migration, bootstrap, host source/dist/runtime bind or top-level volumes. |
| Pin/forbidden scan | rg against all three Compose files and four Dockerfiles | All active base/build sources are version + digest pinned; no active latest tag. The only latest text is an explanatory comment. Production Dockerfiles/locks remain read-only. |
| Dev contract | Read Compose and inspect running mounts | Backend uses ./backend:/app plus named .venv/uv-cache volumes; frontend uses ./frontend-js:/app plus named node_modules; migration and bootstrap are separate actions; bootstrap is profile-gated/default-off. |

## 6. Independent smoke lifecycle (aiis-ics-arch-smoke)

The lifecycle started after an exact preflight showed no task-prefixed containers, networks or volumes. The
temporary env was generated from backend/.env.docker.smoke.example and was not reused from a deleted file.

| Step | Command/result |
| --- | --- |
| Build | docker compose ... build --no-cache backend frontend -> exit 0; logs were redirected to /private/tmp/arch001-r3-smoke-build.log and only a finite tail was inspected. |
| MySQL | up -d mysql -> exit 0; mysql:8.4.6 became healthy; docker port produced no host port. |
| Migration | up migration -> exit 0; MySQL health gate passed; Alembic logged Running upgrade -> d4e6f8a0b2c4; migration exited 0. |
| Schema/revision | Read-only MySQL queries returned 15 tables exactly (alembic_version + the 14 Core tables) and version d4e6f8a0b2c4; all 14 Core COUNT(*) values were 0. |
| Backend | up -d backend -> exit 0; container healthy; host GET /health -> HTTP 200; container pymysql SELECT 1 -> 1. |
| Frontend/proxy | up -d frontend -> exit 0; container healthy; host / -> HTTP 200 with AIIS ICS Architecture; /api/v1/health -> HTTP 200 backend health JSON. |
| Default-off | In-container settings reported BACKEND_MOCK_ENABLED=False, PROJECTION_RUNNER_ENABLED=False, all three bootstrap flags False, and role permissions {}; smoke has no bootstrap service. |
| Mount/resource audit | Backend/migration/frontend had no mounts; MySQL had only aiis-ics-arch-smoke_mysql_data -> /var/lib/mysql; service names and ports matched the fixed contract. |
| Cleanup | down --volumes --remove-orphans -> exit 0; only the two exact task images were removed. Final smoke containers/network/volume/images were absent. |

One initial read-only table-count wrapper failed with MySQL 1045 because its shell assignment did not export
MYSQL_PWD; the corrected wrapper exported the already-in-container variable and returned all fourteen tables at
zero. No data or configuration changed; this is recorded as QA command orchestration, not implementation failure.

## 7. Independent dev lifecycle (aiis-ics-arch-dev)

The dev lifecycle also started from an exact empty prefix and used one-time envs copied from the two dev examples.

| Step | Command/result |
| --- | --- |
| Build | docker compose ... build --no-cache backend frontend -> exit 0. |
| MySQL/migration | MySQL 8.4.6 healthy with the explicit dev host mapping 3307:3306; migration waited for health and exited 0; read-only schema count 15, revision d4e6f8a0b2c4. |
| Backend | Container healthy; direct /health -> HTTP 200; container SELECT 1 -> 1. |
| Known API route | Direct backend /api/v1/health -> HTTP 404 {"detail":"Not Found"}. No Vite config or source was changed to hide this existing route fact. Direct /api/v1/auth/me -> HTTP 401 {"detail":"Not authenticated"}, proving the API path is reachable. |
| Frontend/proxy | Vite homepage -> HTTP 200 with AIIS ICS Architecture; frontend /api/v1/health -> 404; frontend /api/v1/auth/me -> 401, proving proxy reachability without inventing a second health route. |
| Bootstrap proof | --profile bootstrap run --rm bootstrap -> exit 0; admin/supervisor/operator each reported status=skipped reason=bootstrap_disabled; users count remained 0. |
| Default-off | Backend settings reported mock/projection/bootstrap all False, role permissions {}. |
| Correct mounts | Inspect showed backend source /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend -> /app plus named .venv/uv-cache; frontend source /Users/jason/Desktop/DreamCode/aiis-ics-arch/frontend-js -> /app plus named node_modules; MySQL only its named volume. |
| Cleanup | down --volumes --remove-orphans -> exit 0; only the two exact dev images were removed; all dev containers/network/volumes/images absent. Task-created source-bind logs and empty mountpoint dirs were removed without touching pre-existing backend/data. |

## 8. Production-shaped release-check (aiis-ics-arch-release-check)

The fixed project preflight was empty. docker compose ... config --quiet exited 0, and
docker compose ... build --no-cache backend frontend exited 0; both images were source-built and then
removed by exact image name. No containers, network or volume were created. No external DB fixture was available,
so runtime health/proxy was intentionally not attempted. This is an honest config/build gate, not a production
readiness claim.

## 9. Final resource, env and artifact confirmation

The final exact-prefix audit for aiis-ics-arch-smoke, aiis-ics-arch-dev, and
aiis-ics-arch-release-check returned no containers, networks, volumes or task images. The six real env targets,
the temporary smoke env, dev envs and prod env all returned ABSENT. Final generated-directory and sensitive-file
scans returned no .venv, node_modules, target, dist, build, __pycache__, .pytest_cache, logs, SQL/DB/dump/key/log
files; only checked-in .env*.example templates remain.

## 10. Acceptance criteria audit

| AC | Verdict | Independent evidence |
| --- | --- | --- |
| AC-001 | pass | r3 spec.md/tasks.md/this checklist share Task ID, Revision, Execution Mode and v2 role metadata; r2 qa_blocked is retained as a historical summary and not rewritten as r3 evidence. |
| AC-002 | pass | Active root/config identity is AIIS ICS Architecture / aiis-ics-arch; current AGENTS.md hash stayed unchanged and contains no one-off r3 body. |
| AC-003 | pass | Three nested project plans/ directories are absent; root plans/ and accepted dependency bundles remain. Non-Git provenance limitation is explicitly recorded. |
| AC-004 | pass | Six real env paths were metadata-checked only and are absent; temporary envs came from sanitized examples and were deleted, with no content/hash/output/restore operation on deleted files. |
| AC-005 | pass | Four r3-edited backend/frontend examples are Core identity, empty/Core-only permission, no real address/secret, and default-off; frontend/CA public-safe examples remain unchanged. |
| AC-006 | pass | ARCH-MIG-001 remains owner-accepted; active graph is one d4e6f8a0b2c4 root/head; actual migration recorder has 14 tables/39 indexes and the smoke/dev databases each contain exactly 14 Core tables plus alembic_version. |
| AC-007 | pass | Backend app surface is six Core packages and frontend src/app is only system; no ARCH-FE-001 or CA-CONFIG-001 implementation is present. |
| AC-008 | pass | Dev uses correct backend/frontend paths, MySQL 8.4.6, no fixed container/legacy resource/extra mount, separate migration, profile-gated default-off bootstrap; lifecycle and mounts passed. |
| AC-009 | pass | Dev Dockerfiles and active production Dockerfiles use pinned digest sources with no active latest; production Dockerfile/lock hashes were unchanged during QA. |
| AC-010 | pass | Smoke Compose/env example match the accepted ARCH-DOCKER-001 four-service contract; fresh r3 smoke independently built, migrated, checked schema/health/proxy/default-off, and cleaned resources. Dependency three-file history was not rewritten. |
| AC-011 | pass | Release-shaped Compose parsed and source-built backend/frontend with only external-DB topology; no DB/migration/bootstrap/volume/source bind; runtime was not started without a safe fixture. |
| AC-012 | pass | Independent smoke/dev commands, exit codes, MySQL readiness, migration/revision/table counts, health, SELECT 1, frontend/proxy, bootstrap skip, mounts and exact cleanup are recorded above. |
| AC-013 | pass | LICENSE remains MIT with exact ownership text; r3 spec records Human Owner's precise confirmation. Verification did not modify it or grant publication authority. |
| AC-014 | pass | Current public audit found no active Vibe/project identity, old Docker path/resource, project permission set, real env, secret, customer input or generated artifact. Historical mutil-project-pm.md/task narrative hits have the explicit public-safe migration-document rationale in section 4.2. |
| AC-015 | pass | Root/backend README/PLAN/INITIALIZATION pairs, plans catalog and CODE_INDEX describe the current smoke/dev/release-check surfaces and accepted dependencies; frontend/CA README/PLAN remain Core/deferred boundaries. |
| AC-016 | pass | No source/private/modules repository, real DB/PLC/CA, Git/GitHub, release/tag, deployment or broad Docker operation was used; exact resource names were the only Docker targets. |
| AC-017 | pass | Development handoff evidence was independently rechecked with fresh commands, host/runtime limitations and exact resource cleanup; QA verdict is separate from Development self-check. |
| AC-018 | pass | This qa_passed is a Verification result only. Handoff is to Human Owner for final acceptance and does not authorize release, deployment, Git/GitHub, production, platform ACL or forced routing. |

## 11. Acceptance Audit

| Area | Current acceptance state | Next handling |
| --- | --- | --- |
| Public Core identity/residue and Core-only module surfaces | Accepted for r3 static scope | Preserve the current sanitized baseline; any new module requires its own approved task. |
| Migration/schema truth | Accepted dependency baseline: one d4e6f8a0b2c4 root and 14 Core tables | Preserve ARCH-MIG-001; schema changes require a new PM Revision. |
| Disposable MySQL smoke | Accepted for this r3 implementation baseline | Keep the exact project name and cleanup contract; do not infer production readiness. |
| Dev hot-reload and bootstrap boundary | Accepted for this r3 implementation baseline | Keep /api/v1/health 404 as the current route fact; use authenticated path checks rather than modifying Vite/API source. |
| Release-shaped config/build | Config/build accepted; runtime not accepted or attempted | Requires a separately approved, disposable external DB fixture before any runtime check. |
| Host standard pytest/no-DB environment | Not independently runnable under available Python/dependency environment | Re-run only if Human Owner requests a locked clean host environment; Docker/runtime and standalone operation parity remain recorded. |
| Production/site/multi-dialect/real PLC/CA/release | Deferred gate / out of scope | Separate Human Owner decisions and tasks; no authorization is implied by this QA verdict. |
| Human Owner final acceptance | Accepted on 2026-08-10 for ARCH-001 r3 | Close this task; release, deployment, Git/GitHub, production and external-system actions remain separate gates. |

## 12. Limitations, blockers and rework routing

### Blockers

No implementation failure, material allowlist mismatch, unsafe resource ownership, unclean task resource, or
required external-I/O condition was observed. There is no QA blocker for the approved r3 scope.

### Limitations

1. The target has no Git history/worktree, so Development's historical authorship and deletion provenance cannot be
   reconstructed with Git diff; current content/structure, task evidence, mtime/hash snapshots and final absence
   checks are the available honest evidence.
2. Standard host focused pytest could not run because the system Python was 3.9 and the isolated uv environment
   lacked cached project wheels. The actual migration operations were independently recorded under Python 3.11,
   and the MySQL smoke/dev migrations executed in the built project images.
3. Release-shaped runtime was deliberately not started because no safe external DB fixture existed. Production,
   site compatibility, multi-dialect, PLC/CA, packaging and publication remain unverified/deferred.
4. The historical mutil-project-pm.md still contains old source names and an older r2 status line by design of
   the r3 allowlist; those are explanatory migration-governance text, not active product identity. Updating that
   file would require a new approved scope.
5. One QA-only MySQL COUNT wrapper initially omitted export MYSQL_PWD and returned access denied; the corrected
   read-only command passed, with no data change. This does not reduce the runtime verdict.

### Rework routing

If a later review identifies an actual implementation mismatch, return the exact evidence to Development and stop
the current Revision. Any material change to scope, allowlist, migration set, license text, runtime topology,
acceptance or risk requires a new PM Revision; do not repair it in this checklist. This qa_passed result is
handed only to Human Owner for final acceptance.

## 13. QA verdict and handoff

**QA verdict: qa_passed**

ARCH-001 r3 independently satisfies AC-001..AC-018 for the approved public-safe Core, deletion-only residue/env
cleanup, Core migration dependency, pinned Docker surfaces, fresh disposable smoke and dev lifecycles,
production-shaped config/build boundary, public audit and exact cleanup. The known dev /api/v1/health 404 is
recorded honestly with a 401 authenticated-path proxy proof; no Vite/API source was changed. Host pytest and
release runtime are documented limitations/deferred gates, not fabricated passes. No real external I/O or unsafe
resource action occurred.

Handoff: Human Owner final acceptance is recorded below. Release, deployment, Git/GitHub, production use,
platform ACL, forced routing and external-system authorization remain separate and are not authorized by this
acceptance.

## 14. Human Owner final acceptance

Acceptance date: 2026-08-10  
Acceptance statement: `Human Owner 最终接受 aiis-ics-arch::ARCH-001 r3。`  
Final status: `owner_accepted`

This acceptance closes only the approved ARCH-001 r3 scope and preserves the QA verdict `qa_passed`. It does not
authorize Git/GitHub initialization or push, release/tag creation, deployment, production use, real/external
database access, PLC/Control Agent actions, platform ACL changes, forced routing, or other external-system work.
