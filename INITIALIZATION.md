# Initialization and Local Verification

Chinese version: [INITIALIZATION.zh-CN.md](INITIALIZATION.zh-CN.md)

This document describes a safe local source check. It is not a deployment guide and never requests real credentials, PLC access, database writes or repository publication.

## Prerequisites

- Python and `uv` compatible with `backend/`.
- Node.js and `pnpm` compatible with `frontend-js/`.
- Rust/Cargo compatible with `control-agent/`.
- No checked-in `.env`, customer input, generated output or real connection address.

## Sequence

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

Use a project-owned non-production environment only when a separately approved runtime task requires it. Database migration execution, Docker lifecycle, PLC collection, packaging and Git/GitHub actions are outside this baseline.

## Source-development stack

The development stack uses the fixed project name `aiis-ics-arch-dev`, MySQL `8.4.6`, source hot reload, a separate migration service, and a default-off bootstrap profile.

```bash
cp backend/.env.docker.dev.example backend/.env.docker.dev
cp frontend-js/.env.docker.dev.example frontend-js/.env.docker.dev
# Replace only the local development placeholders; keep all bootstrap flags false.

docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml config --quiet
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml build backend frontend
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml up -d mysql
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml up migration
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml up -d backend frontend

# Optional default-off proof: all three bootstrap users must be skipped.
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml \
  --profile bootstrap run --rm bootstrap

docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml \
  down --volumes --remove-orphans
rm -f backend/.env.docker.dev frontend-js/.env.docker.dev
```

The Vite `/api` proxy forwards the original path to the backend. Use the backend's direct `/health` endpoint for health checks; authenticated API paths can prove proxy reachability without adding a second health route.

## Production-shaped config/build check

The root Compose file builds backend and frontend from source and expects an external database. It intentionally has no database, migration, or bootstrap service and no host runtime bind.

```bash
cp backend/.env.docker.prod.example backend/.env.docker.prod
# Replace local placeholders without printing or committing their values.

docker compose --project-name aiis-ics-arch-release-check \
  --env-file backend/.env.docker.prod -f docker-compose.yml config --quiet
docker compose --project-name aiis-ics-arch-release-check \
  --env-file backend/.env.docker.prod -f docker-compose.yml build backend frontend

rm -f backend/.env.docker.prod
```

Do not run the release-shaped services unless a separately approved, task-exclusive and safely disposable external-database fixture is available. Never substitute a real database for that fixture.
