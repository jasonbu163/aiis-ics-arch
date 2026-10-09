# Initialization and Local Verification

Chinese version: [INITIALIZATION.zh-CN.md](INITIALIZATION.zh-CN.md)

This document covers source checks and operator-run Docker deployment procedures. Docker build/start/stop and database writes require separately approved runtime scope; the commands below are instructions, not evidence that deployment has run.

## Manual test order

For `uv run run.py` + `pnpm dev` with database-only, follow [host-source development](#host-source-development-with-database-only), including the explicit account initialization step.

Start with [single-host deployment](#single-host-deployment): prepare files/dist, start database-only, wait for MySQL healthy, initialize the schema and application account, then start prod and check the homepage/health/login. Use a reviewed test database, and stop after any failed command.

To test [full dev](#source-development-stack) afterwards, stop prod and database-only with their explicit `-f` paths and `down` (without `-v`), then follow the dev section. Dev uses its own database volume; prod-created users are not present there. For a dev login test, temporarily configure the desired bootstrap user in backend/.env.docker.dev, then run the documented bootstrap profile command; disable the flag afterwards. Always specify `-f`; there is no default root Compose entry.

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

## Host-source development with database-only

Use this path when MySQL runs in `docker-compose.database-only.yml` while the backend and frontend run with `uv` and `pnpm` on the host. Start from the repository root. Run lifecycle and database-write commands only against the approved development database; stop after any failure.

1. If absent, copy `backend/.env.example` to `backend/.env` and `frontend-js/.env.example` to `frontend-js/.env`; preserve existing files. Configure the database name, non-root MySQL user/password, root password and JWT secret in `backend/.env`. Use `MYSQL_HOST=127.0.0.1` and `MYSQL_PORT=3307` (or the actual published port). Stop a conflicting full dev stack first; its database volume and users are separate.
2. Start MySQL and wait until `ps` reports healthy. Skip startup if the intended database-only service is already healthy.

   ```bash
   docker compose -f docker-compose.database-only.yml config --quiet
   docker compose -f docker-compose.database-only.yml up -d mysql
   docker compose -f docker-compose.database-only.yml ps
   ```

3. Install backend dependencies and migrate the selected database:

   ```bash
   cd backend
   uv sync
   uv run alembic upgrade head
   ```

4. Configure the desired login accounts in `backend/.env` using the following prefixes. For each desired account, temporarily set `<PREFIX>_BOOTSTRAP_ENABLED=True`, choose `<PREFIX>_BOOTSTRAP_USERNAME`, a non-empty strong `<PREFIX>_BOOTSTRAP_PASSWORD`, and `<PREFIX>_BOOTSTRAP_NAME`. Keep `<PREFIX>_BOOTSTRAP_RESET_PASSWORD=False` for initial creation; leave unneeded accounts disabled.

   | Prefix | Default username | `<PREFIX>_BOOTSTRAP_ROLE` |
   | --- | --- | --- |
   | `ADMIN` | `admin` | `admin` |
   | `SUPERVISOR` | `supervisor` | `supervisor` |
   | `OPERATOR` | `operator` | `operator` |

   From `backend/`, explicitly run:

   ```bash
   uv run python main.py --maintenance bootstrap-users
   ```

   **Alembic creates tables; neither `uv run run.py` nor `pnpm dev` creates login accounts. Setting ENABLED only allows this maintenance command to act.** Source execution reads `backend/.env`, not `.env.docker.dev` or `.env.docker.prod`; exported process variables can override file values. MySQL connection accounts and application login accounts in `users` are separate.

   With all three enabled and absent, expect these summaries (custom usernames appear instead when configured):

   ```text
   target=admin_user status=created username=admin role=admin
   target=supervisor_user status=created username=supervisor role=supervisor
   target=operator_user status=created username=operator role=operator
   ```

   Repeating with RESET_PASSWORD=False preserves existing users and reports `status=exists`; disabled entries report `status=skipped reason=bootstrap_disabled`. RESET_PASSWORD=True resets an existing password and reactivates the account, reporting `status=password_reset`; use it only for an intentional reset. After success, set the enabled flags back to False, clear bootstrap passwords, and keep reset flags False. Already-created accounts remain available.
5. Start the API from `backend/`:

   ```bash
   uv run python run.py
   ```

   In another terminal at the repository root, configure `frontend-js/.env` with `VITE_API_BASE_URL=/api/v1`, `VITE_PROXY_TARGET=http://127.0.0.1:8000` (match the backend port), `VITE_FRONTEND_MOCK_ENABLED=false` and `VITE_LOGIN_DEMO_ACCOUNTS_ENABLED=false`, then run:

   ```bash
   pnpm --dir frontend-js install --frozen-lockfile
   pnpm --dir frontend-js dev
   ```

   Open the URL printed by Vite and log in with an initialized application account. If the API was already running against the same database, account creation normally requires no API restart. Restart the backend after changing its connection settings.

For login HTTP 401, first check the bootstrap result and whether the API and maintenance command use the same database and environment overrides; then check the entered credentials. A 401 alone does not prove the user is missing. If maintenance reports missing tables, verify the migration target and successful completion; if it reports a connection failure, check MySQL health and the published host port. Frontend role/page settings do not create backend accounts.

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

# Stop after testing; retain the database volume and runtime env files.
docker compose --project-name aiis-ics-arch-dev \
  --env-file backend/.env.docker.dev -f docker-compose.dev.yml \
  down --remove-orphans
```

The Vite `/api` proxy forwards the original path to the backend. Use the backend's direct `/health` endpoint for health checks; authenticated API paths can prove proxy reachability without adding a second health route.

## Single-host deployment

Run these commands from the repository root, after separate approval for runtime builds, lifecycle operations and database writes. Docker Desktop must use Linux containers. On native Linux, use a reachable database DNS/IP rather than assuming `host.docker.internal` exists.

| Entry | Runtime files | Database / purpose |
| --- | --- | --- |
| `docker-compose.dev.yml` | backend/frontend `.env.docker.dev` | Full hot-reload stack; existing independent dev volume |
| `docker-compose.database-only.yml` | `backend/.env` | MySQL only; independent `aiis-ics-arch-database-only_mysql_data` volume |
| `docker-compose.prod.yml` | `backend/.env.docker.prod` | backend + Nginx against external MySQL |

Dev/database-only both publish 3307; dev/prod both publish 8000. Stop conflicting entries or override host ports. Prefixes do not isolate ports, switching does not migrate data, and MySQL data directories must not be shared/copied. Stop persistent database-only with `docker compose -f docker-compose.database-only.yml down`, retaining its volume; never append `-v` or `--volumes` for ordinary shutdown.

### Prepare files and frontend

Copy templates only when runtime files are absent. macOS/Linux:

```bash
[ -f backend/.env ] || cp backend/.env.example backend/.env
[ -f backend/.env.docker.prod ] || cp backend/.env.docker.prod.example backend/.env.docker.prod
mkdir -p runtime/backend/logs
pnpm --dir frontend-js install --frozen-lockfile
VITE_API_BASE_URL=/api/v1 VITE_FRONTEND_MOCK_ENABLED=false VITE_LOGIN_DEMO_ACCOUNTS_ENABLED=false pnpm --dir frontend-js build
test -f frontend-js/dist/index.html
```

Windows PowerShell:

```powershell
if (!(Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
if (!(Test-Path backend/.env.docker.prod)) { Copy-Item backend/.env.docker.prod.example backend/.env.docker.prod }
New-Item -ItemType Directory -Force runtime/backend/logs | Out-Null
pnpm --dir frontend-js install --frozen-lockfile
$env:VITE_API_BASE_URL = '/api/v1'
$env:VITE_FRONTEND_MOCK_ENABLED = 'false'
$env:VITE_LOGIN_DEMO_ACCOUNTS_ENABLED = 'false'
pnpm --dir frontend-js build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed' }
Get-Item frontend-js/dist/index.html
```

Confirm each step succeeds before continuing. VITE settings are public build values; review both VITE_SUPERVISOR_PAGE_ACCESS_JSON and VITE_OPERATOR_PAGE_ACCESS_JSON in the shared frontend-js/.env (operator must be a subset of supervisor), and never include secrets. Host dev/build share this file; existing mode/local files and process variables override it by Vite precedence. Docker dev uses .env.docker.dev. Preserve and migrate old role arrays; comment the retired VITE_ROLE_PAGE_ACCESS_JSON line instead of keeping it active. Run pnpm --dir frontend-js check:access --mode production before building; unknown, disabled or admin-only pageIds fail explicitly. Nginx serves dist and does not build it or mount source/node_modules.

Set the MySQL database, non-root application user/password and root password in `backend/.env`. Host-source backend uses `127.0.0.1:3307`. On first empty-volume startup the MySQL image creates the configured database and application account. Editing env for an existing volume does not update its accounts/passwords.

Set an independent JWT secret, `BACKEND_HOST=0.0.0.0`, `BACKEND_PORT=8000` and `LOG_DIR=logs` in `backend/.env.docker.prod`; keep mocks/Projection runner off. To reuse database-only on Docker Desktop, use `MYSQL_HOST=host.docker.internal`, `MYSQL_PORT=3307` and matching database/application credentials. For external MySQL use deployment-owned reachable host/port and have the database administrator provision the database/account/grants first. Do not use container-local `localhost` for external databases.

Override ports through shell variables such as `MYSQL_HOST_PORT`, `BACKEND_HOST_PORT` and `FRONTEND_HOST_PORT`. The prod file bind does not participate in Compose interpolation; writing host-port variables only into backend env will not configure Compose ports.

### Explicit initialization and startup

These single-line commands work in Bash and PowerShell. Skip database-only commands for an existing external MySQL. Check `ps` for healthy database status; stop and resolve failures before continuing with writes.

```text
docker compose -f docker-compose.database-only.yml config --quiet
docker compose -f docker-compose.database-only.yml up -d mysql
docker compose -f docker-compose.database-only.yml ps
docker compose -f docker-compose.prod.yml config --quiet
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

Migrate only the approved target, using the arch Core migration graph (current single root `d4e6f8a0b2c4`), without importing project migration history. Schema creation does not create a web-login account.

For an initial administrator, temporarily set `ADMIN_BOOTSTRAP_ENABLED=True`, choose `ADMIN_BOOTSTRAP_USERNAME` and a strong `ADMIN_BOOTSTRAP_PASSWORD` in prod env, retaining `ADMIN_BOOTSTRAP_RESET_PASSWORD=False` and keeping other bootstrap flags off:

```text
docker compose -f docker-compose.prod.yml run --rm backend python main.py --maintenance bootstrap-users
```

After confirming `status=created` or the expected `status=exists`, disable ENABLED and clear the password. Resetting an existing password requires explicit RESET_PASSWORD enablement; disable it afterwards. Application accounts live in users; web login uses them, not MySQL credentials. The default disabled flags only skip account creation.

```text
docker compose -f docker-compose.prod.yml up -d backend frontend
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail 50 backend frontend
```

Check `http://127.0.0.1/`, `http://127.0.0.1:8000/health` and the Nginx proxy at `http://127.0.0.1/api/v1/health`, then validate application login and `/api/v1/auth/me`. Adjust URLs for overridden ports. `config --quiet` is configuration validation only; record health, proxy and login results after actual execution.

### Restart, updates and troubleshooting

- Configure Docker Desktop to start at login separately. `unless-stopped` applies only to existing prod containers that were not manually stopped; it cannot launch Desktop. Database-only has no automatic restart policy. After Desktop restarts, explicitly `up -d mysql`, wait for healthy, then run `docker compose -f docker-compose.prod.yml up -d backend frontend`. If backend has not recovered, restart it after the database becomes healthy. `depends_on` does not guarantee Compose health ordering on daemon restart.
- Prod `.env.docker.prod` is a file bind: ordinary in-place edits require backend restart to reread it. If an editor atomically replaces the file or mounts change, use `up -d --force-recreate backend` to rebind it. Changes to dev `env_file` need `up -d --force-recreate` for affected services; restart alone does not refresh container environment variables. Existing database credentials do not change with env edits.
- Backend source/dependency changes require build backend and then `up -d backend`. Frontend changes require rebuilding dist, checking index.html and refreshing. If the whole dist directory was replaced, use `up -d --force-recreate frontend`. Retain the previous reviewed dist in a deployment-owned backup location; restore and rebind it on failure. Do not commit backups.
- Missing bind path: confirm env is a file, logs/dist are directories and Docker Desktop can share the repository directory. Missing index.html fails startup explicitly. For 403, check readability/build success and match the mount target to Nginx `/usr/share/nginx/html/current`.
- Database failures or proxy 502: check MySQL health and host/port relative to the caller, then backend logs/health. Nginx uses Compose service `backend:8000`; do not hardcode customer container names.

Keep real env, logs, dist and runtime ignored. Stop prod with `docker compose -f docker-compose.prod.yml down`. Roll back using the previous reviewed prod image/dist; always retain database volumes.
