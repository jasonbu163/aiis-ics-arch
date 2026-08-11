# AIIS ICS Architecture

Chinese version: [README.zh-CN.md](README.zh-CN.md)

AIIS ICS Architecture is the public source baseline for reusable industrial information-system architecture. It contains framework code and sanitized examples, not a customer project and not a prebuilt release artifact.

## Repository map

```text
.
├── backend/       # FastAPI, SQLAlchemy, Alembic and Core modules
├── frontend-js/   # Vue 3 + Vite JavaScript Core frontend
├── control-agent/ # Rust/Tauri field-fact collection runtime
├── tools/         # Independent project-level tools
├── contracts/     # Cross-runtime public contracts
├── release/       # Approved source-version materials
└── plans/         # Architecture decisions and task bundles
```

Project repositories consume a pinned source version and add their own modules under the same vertical module conventions. This repository does not contain project-specific pages, PLC workbooks, customer data, real addresses, credentials, or build output.

## Runtime boundaries

```text
frontend-js -> FastAPI Core API -> configured database
PLC -> resident control-agent -> raw/latest field facts -> backend Projection host
```

The backend module registry discovers only modules that provide an enabled manifest. Registry discovery exposes routes and metadata; it does not create database tables. Schema changes require an explicit migration task. The `control-agent` remains a separate runtime and artifact boundary.

Frontend route and locale discovery are part of the JavaScript template. Full manifest-driven menu assembly is tracked separately in [ARCH-FE-001](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md). Packaged database settings and YAML upload are tracked separately in [CA-CONFIG-001](plans/CA-CONFIG-001-packaged-configuration-management/spec.md).

## Local validation

```bash
cd backend
uv sync
uv run python -m compileall -q app core database projection scripts tests main.py build.py
uv run pytest -q

cd ../frontend-js
pnpm install
pnpm build

cd ../control-agent
cargo fmt --check
cargo test --workspace
```

These commands are source/static checks. They do not start Docker, modify a real database, connect to a PLC, or publish a release. Use explicit project-owned environment files and approved non-production fixtures for runtime work.

## Docker surfaces

`docker-compose.dev.yml` is the fixed-name `aiis-ics-arch-dev` source-development stack. It uses MySQL `8.4.6`, source binds for backend/frontend hot reload, a one-shot migration service, and an opt-in `bootstrap` profile whose public defaults remain off.

The root `docker-compose.yml` is the production-shaped `aiis-ics-arch-release-check` config/build surface: source-built backend and frontend, an externally configured database, no database/migration/bootstrap service, and no host source, distribution, or runtime bind. Do not start it without a separately approved, task-exclusive external-database fixture.

## Disposable Docker smoke

`docker-compose.smoke.yml` is the separately tracked, non-production runtime proof. It builds the backend and
frontend from this source tree, runs the single `d4e6f8a0b2c4` Core migration against a disposable MySQL `8.4.6`
volume, and exposes only configurable smoke ports (`18000` and `18080` by default). MySQL has no host port; the
four services are `mysql`, one-shot `migration`, `backend`, and `frontend`.

The smoke uses the ignored `backend/.env.docker.smoke` copied from its example. Run it only with the fixed
project name `aiis-ics-arch-smoke`, and always finish with `docker compose ... down --volumes --remove-orphans`
and removal of the temporary env. This proves the Core MySQL development path only; it is not production
readiness, multi-dialect compatibility, release publication, or a real database/PLC gate. Fresh-context
Verification and Human Owner acceptance remain separate lifecycle stages.

## Governance

Read [AGENTS.md](AGENTS.md) before making changes. Current architecture status is indexed in [PLAN.md](PLAN.md); source-version notes are in [CHANGELOG.md](CHANGELOG.md). The repository retains the MIT [LICENSE](LICENSE) and its stated ownership; that fact does not authorize publication or release. The three-repository operating model is documented in [mutil-project-pm.md](mutil-project-pm.md).
