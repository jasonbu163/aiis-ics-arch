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
├── contracts/     # Root Core cross-runtime contract hub
├── docs/          # Durable cross-repository and process documents
└── plans/         # Architecture decisions and task bundles
```

Project repositories consume a pinned source version and add their own modules under the same vertical module conventions. This repository does not contain project-specific pages, PLC workbooks, customer data, real addresses, credentials, or build output.

## Source version model

`main` is the continuing Core development line. A major-version maintenance line uses a literal branch such as
`release/1.x.x` (future lines use `release/2.x.x`, `release/3.x.x`, and so on) and may move only through a
separately approved release task for that major line. Each exact source version uses an immutable annotated tag
such as `v1.0.0`, `v1.2.1`, or `v2.1.2`; a tag is not replaced by the maintenance branch. Source is not copied
into a physical `release/` directory, and a source version does not imply a hosted GitHub Release, build artifact,
deployment, or production readiness. Publication of those Git refs is a separately approved Human Owner action.

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

## Host-source startup

For database-only + `uv run run.py` + `pnpm dev`, follow [host-source initialization](INITIALIZATION.md#host-source-development-with-database-only): migrate, explicitly bootstrap login accounts, then start the applications. Bootstrap flags alone do not create accounts.

## Docker surfaces

`docker-compose.dev.yml` is the fixed-name `aiis-ics-arch-dev` source-development stack. It uses MySQL `8.4.6`, source binds for backend/frontend hot reload, a one-shot migration service, and an opt-in `bootstrap` profile whose public defaults remain off.


## Governance

Read [AGENTS.md](AGENTS.md) before making changes. Current architecture status is indexed in [PLAN.md](PLAN.md); source-version notes are in [CHANGELOG.md](CHANGELOG.md). The repository retains the MIT [LICENSE](LICENSE) and its stated ownership; that fact does not authorize publication or release. Durable project documentation is indexed under [docs/](docs/README.md), including the [multi-project development guide](docs/multi-project-pm.md); the root `contracts/` directory remains the Core contract hub.

## Single-host deployment

`docker-compose.database-only.yml` provides isolated MySQL `8.4.6` for host-source development or the prod stack. `docker-compose.prod.yml` runs an image-built backend and Nginx serving the host's prebuilt `frontend-js/dist`; its database is external to that Compose project. The three supported entries are dev, database-only and prod; always select one explicitly with `-f`.

See [initialization and deployment](INITIALIZATION.md#single-host-deployment) for environment files, preparation, explicit migrations, account setup, restart behavior and troubleshooting. Configuration validation does not establish successful runtime deployment.
