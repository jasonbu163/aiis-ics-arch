# AIIS ICS Architecture Backend

Chinese version: [README.zh-CN.md](README.zh-CN.md)

This directory is the reusable FastAPI/SQLAlchemy Core. It owns authentication, system administration, module discovery, schema maintenance, projection control and project-neutral monitor facts. Consuming projects add business modules without editing the Core composition root.

## Core modules

~~~text
app/
├── user/             # authentication and account APIs
├── system/           # dictionaries and projection control-plane APIs
├── control_agent/    # backend-side CA authorization contract
├── schema_maintenance/
├── monitor/          # collector/raw/latest facts only
├── aiis_demo/        # opt-in reference module
└── module_registry.py
~~~

Every ordinary module opts in with app/<module>/manifest.py. enabled=False hides its API routes; Registry discovery never creates tables. New tables require an explicit Alembic revision or approved schema-maintenance action. user and control_agent remain explicit security/runtime boundaries in app/router.py.

The monitor Core surface returns collector health and project-neutral PLC DB-block raw/latest facts. HMI, temperature, energy, process curves and production records belong to a consuming project module.

## Runtime boundaries

- FastAPI request handlers call async Service/CRUD layers and never poll a PLC.
- The resident Rust/Tauri control-agent owns PLC collection and writes field facts through the approved contract.
- Celery, Redis, Beat, Flower and Python Worker runtime are not dependencies of this Core.
- The Core baseline is the single `d4e6f8a0b2c4` Alembic root for fourteen Core tables. Its upgrade operations and
  current SQLAlchemy metadata are mechanically checked by `tests/test_core_migration_baseline.py`; private project
  repositories retain their own historical migration graphs.

## Local checks

~~~bash
uv sync
uv run python -m compileall -q app core database projection scripts tests main.py build.py
uv run pytest -q
~~~

Static migration checks may run `uv run alembic heads`, `uv run alembic history` and offline SQL rendering with
placeholder settings. Do not run migrations against a real database as part of a source-only check. Use a separately
approved non-production database task for schema work.

The approved `ARCH-DOCKER-001` smoke builds this image from the backend source and reuses it for the one-shot
`alembic upgrade head` service and the API service. It connects only to the Compose `mysql:3306` service on a
disposable MySQL `8.4.6` volume; the smoke env is ignored and must be removed after every run.

## Host-source startup

For host-source development, follow [database-only and account initialization](../INITIALIZATION.md#host-source-development-with-database-only). After migration and configuring the desired bootstrap accounts in `backend/.env`, run `uv run python main.py --maintenance bootstrap-users` from this directory, then `uv run python run.py`. Neither Alembic nor API startup creates login accounts; ENABLED flags only take effect when the maintenance command runs.

## Packaging

main.py is the reload-disabled application entry; run.py is the local development entry. build.py is an optional PyInstaller source package path and never copies a real .env, data dump or customer input. See BUILD.md.

## Single-host Docker entry

The root `docker-compose.prod.yml` reuses this Dockerfile and mounts `.env.docker.prod` read-only at `/app/.env`, with logs in `runtime/backend/logs`. Source remains inside the image. The database-only entry reads this directory's `.env`; its MySQL volume is independent from dev. Keep bootstrap flags off until an explicit account-initialization action is needed. Follow the root [deployment instructions](../INITIALIZATION.md#single-host-deployment).

## Role API permissions

`SUPERVISOR_API_PERMISSIONS_JSON` grants API permission keys to supervisor accounts;
`OPERATOR_API_PERMISSIONS_JSON` grants them to operator accounts. Each is a JSON array of non-blank
strings and defaults to `[]` (no configured grants). Keys match exactly and are case-sensitive: they are
backend permission keys, not frontend pageIds, URLs or arbitrary module names. Duplicate keys are deduplicated;
`*` is an unknown key, not a wildcard. Only these two roles use the arrays; unknown roles fail closed.

~~~dotenv
SUPERVISOR_API_PERMISSIONS_JSON='["monitor","control-agent-read"]'
OPERATOR_API_PERMISSIONS_JSON='["monitor"]'
~~~

Operator's **original configured keys must be a subset of supervisor's original keys**. Both arrays must
explicitly contain each operator grant; supervisor is never automatically granted a missing key. This is
checked before unknown/disabled filtering, so even an unknown or disabled operator-only key prevents startup.
Admin needs no array and bypasses `require_permissions()`; authentication, parameter validation, user-management
actor/target rules, Projection state/contract validation and CA gate-token rules still apply. Empty arrays
do not change authenticated-only APIs or admin-only guards. Granting one key never implies another key.

| Key | Current API surface and boundary |
| --- | --- |
| `system` | Explicit user-management reads and writes; independent actor/target restrictions remain. It is not all system-module access. |
| `system-dict` | System dictionary queries **and maintenance** share this key. |
| `projection-mapping` | Projection handler/policy catalogs and mapping queries. |
| `projection-mapping-manage` | Mapping draft, validation, publish, copy and rollback permission guards; Service state/contract validation remains, with no additional role/admin guard today. |
| `monitor` | Collector and raw/latest field facts; excludes customer business curves and frontend monitor-page access. |
| `control-agent-read` | CA action-scope catalog queries. |
| `control-agent` | Gate-token issuance permission guard; does not remotely execute device actions and retains independent role restrictions. |
| `aiis_demo` | Default-disabled reference manifest; a configured grant warns and is ignored. The array does not enable it. |

Projection management routes pass `actor_user_id` to record the actor; this is not a role check.

`schema_maintenance` has no configurable permission key: it uses an admin-only guard. CA authorization verify
uses its gate-token contract. These independent boundaries cannot be replaced by the arrays.

Ordinary modules declare `enabled` and `permissions` in `app/<module>/manifest.py`. `enabled=False` removes
that manifest's whole route group and OpenAPI entries on restart/full process reload. All roles, including
admin, receive the normal 404 for its absent exclusive paths. It does not drop tables/data, prevent model
metadata imports or change Alembic. `user/auth` and `control_agent` remain explicitly mounted and have no
ordinary-module switch. Frontend and backend switches are independent. Where several owners declare one key,
any enabled owner makes it available; it is disabled only when all ordinary owners are off. Explicit user/CA
boundary permissions count as available owners.

Configuration is parsed, checked and filtered once per API composition, including `create_app(testing=True)`.
Requests consume that application's effective policy; changes require restart/full process reload.

| Condition | Result |
| --- | --- |
| Missing variable or `[]` | Valid, no grants for that role. |
| Empty string, invalid JSON, non-array, non-string or blank member | Startup fails with variable/member position; configuration contents are not echoed. |
| Operator key missing from supervisor | Startup fails and identifies the missing key and both variables. |
| Unknown permission | `WARNING`, reason `unknown_permission`; key ignored, startup continues. |
| Key owned only by disabled modules | `WARNING`, reason `disabled_module`, with owner names; key ignored, startup continues. |
| Active retired `ROLE_API_PERMISSIONS_JSON`, even `{}` or empty | Startup fails with a migration instruction. Commented lines do not count. |

Warnings identify the variable and permission, and modules where applicable. They occur at composition, not
on every request. Ignored permissions cannot grant access. A login 401 indicates authentication failure;
an authenticated caller missing a permission receives 403; an unregistered disabled-module path receives 404.

### Configuration source and migration

Settings keeps the existing source precedence: explicit Settings initialization, process environment, the
single runtime `.env`, then file secrets/defaults. Source execution reads `backend/.env`; packaged execution
reads `.env` beside the executable. Docker uses the env mounted at `/app/.env` by its selected entry. Process
environment overrides dotenv for new arrays. An active old key in either source is rejected even when new
keys coexist; there is no compatibility merge or old/new priority. The three public example files use safe
empty arrays. Real `.env`, `.env.docker.dev` and `.env.docker.prod` are not automatically migrated.

Before restarting, manually migrate the configuration used by your selected entry:

1. Review the old object and keep each role's members unchanged. For example:

   ~~~dotenv
   ROLE_API_PERMISSIONS_JSON='{"supervisor":["monitor","control-agent-read"],"operator":["monitor"]}'
   ~~~

2. Remove/comment the old assignment in dotenv and remove it from the process environment; write the two
   arrays shown above. Confirm operator is a subset, and review permission names and module `enabled` states.
3. Restart/reload the backend and check startup diagnostics. Invalid input or hierarchy now fails before
   service readiness instead of silently becoming empty grants/403 at request time. Unknown/disabled keys
   now warn and are filtered. Valid equivalent migration preserves the same role grants.

`main.py` composes the app before dispatching `--maintenance schema` or `--maintenance bootstrap-users`;
these entries therefore also fail before the maintenance action for blocking configuration errors, while
unknown/disabled warnings allow dispatch to continue. This does not mean direct scripts or Alembic CLI use
the same API validation. Maintenance/database operations still require their own authorization.

Bootstrap remains an explicit account-maintenance action: these arrays neither create/delete accounts nor
change passwords. Keep using the [host-source initialization tutorial](../INITIALIZATION.md#host-source-development-with-database-only).

## Configuration reference

These tables cover the same 68 active keys in the three public env examples. Source defaults come from Settings; required fields fail configuration loading when absent. Template values show distinct public host/dev/prod values, merging equal entries; passwords/secrets are shown only as placeholder. Templates are not local effective configuration. Use True/False for booleans, single or double quotes for strings, and outer single quotes with inner double quotes for JSON arrays.

### App/API

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `APP_NAME` | Application display name. (str) | Required; no source default | `AIIS ICS Architecture` |
| `APP_VERSION` | Application version reported by API metadata. (str) | Required; no source default | `1.0.0` |
| `APP_DESCRIPTION` | Application description in API metadata. (str) | `'AIIS ICS Architecture Core Backend'` | `AIIS ICS Architecture Core Backend` |
| `API_V1_PREFIX` | Prefix for versioned API routes. (str) | Required; no source default | `/api/v1` |
| `BACKEND_HOST` | Uvicorn bind address; container serving normally uses 0.0.0.0. (str) | `'127.0.0.1'` | `127.0.0.1` / `0.0.0.0` |
| `BACKEND_PORT` | Uvicorn listening port, positive integer. (int) | `8000` | `8000` |
| `BACKEND_WORKERS` | Production Uvicorn worker count; development and packaged entry force one. (int) | `1` | `1` / `4` |

### Runtime/Projection

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `DEBUG` | Enable diagnostic error detail; disable for production. (bool) | Required; no source default | `True` / `False` |
| `TESTING` | Use the separate MySQL test database and disable the Projection runtime. (bool) | `False` | `False` |
| `BACKEND_MOCK_ENABLED` | Allow module Service mock providers or explicit sample seeds. (bool) | `False` | `False` |
| `PROJECTION_RUNNER_ENABLED` | Enable the lifespan Projection runner only on one designated writer host. (bool) | `False` | `False` |
| `PROJECTION_RUNNER_INTERVAL_SECONDS` | Projection polling interval in seconds, positive number. (float) | `1.0` | `1.0` |
| `PROJECTION_RUNNER_BATCH_SIZE` | Maximum raw facts per Projection batch, positive integer. (int) | `100` | `100` |
| `TZ` | Process timezone; restart to apply, without changing database timezone. (str) | `'Asia/Shanghai'` | `Asia/Shanghai` |

### Auth/permissions

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `JWT_SECRET_KEY` | JWT signing secret; replace the public placeholder and keep private. (str) | Required; no source default | placeholder |
| `JWT_ALGORITHM` | JWT signing and verification algorithm, normally HS256. (str) | Required; no source default | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime in minutes. (int) | Required; no source default | `120` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token lifetime in days. (int) | Required; no source default | `7` |
| `SUPERVISOR_API_PERMISSIONS_JSON` | Supervisor API permission keys as a JSON string array; default [] grants none. (str) | `'[]'` | `[]` |
| `OPERATOR_API_PERMISSIONS_JSON` | Operator API permission keys as a JSON string array; must be a supervisor subset. (str) | `'[]'` | `[]` |

### Logging

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `LOG_DIR` | Directory for JSON Lines log files. (str) | `'logs'` | `logs` |
| `LOG_LEVEL` | Log threshold such as DEBUG, INFO, WARNING or ERROR. (str) | `'INFO'` | `INFO` |
| `LOG_MAX_BYTES` | Maximum log-file size before rotation, in bytes. (int) | `10 * 1024 * 1024` | `10485760` |
| `LOG_BACKUP_COUNT` | Number of rotated log backups retained. (int) | `5` | `5` |

### Database routing

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `PRIMARY_DATABASE` | Primary database selector: mysql, postgresql, sqlite or mssql. (str \| None) | `None` | `mysql` |
| `DATABASE_TYPE` | Legacy database selector used when PRIMARY_DATABASE is empty. (str) | `'mysql'` | `mysql` |
| `MYSQL_ENABLED` | Permit selecting MySQL as the primary database. (bool) | `True` | `True` |
| `POSTGRES_ENABLED` | Permit selecting PostgreSQL as the primary database. (bool) | `False` | `False` |
| `SQLITE_ENABLED` | Permit selecting SQLite as the primary database. (bool) | `False` | `False` |
| `MSSQL_ENABLED` | Permit selecting SQL Server as the primary database. (bool) | `False` | `False` |

### Database connections

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `MYSQL_HOST` | MySQL host shared by application and root maintenance connections. (str) | Required; no source default | `127.0.0.1` / `mysql` / `replace-with-external-mysql-host` |
| `MYSQL_PORT` | MySQL TCP port shared by application and root maintenance connections. (int) | Required; no source default | `3307` / `3306` |
| `MYSQL_USER` | MySQL application account. (str) | Required; no source default | `devuser` / `appuser` |
| `MYSQL_PASSWORD` | MySQL application password; keep private. (str) | Required; no source default | placeholder |
| `MYSQL_DATABASE` | Primary MySQL application database name. (str) | Required; no source default | `aiis_ics_architecture` |
| `MYSQL_ROOT_USER` | MySQL account for root maintenance connections, not application requests. (str) | Required; no source default | `root` |
| `MYSQL_ROOT_PASSWORD` | MySQL root maintenance password; keep private. (str) | Required; no source default | placeholder |
| `POSTGRES_HOST` | PostgreSQL host, required when selected. (str \| None) | `None` | `localhost` / `postgres` |
| `POSTGRES_PORT` | PostgreSQL TCP port, required when selected. (int \| None) | `None` | `5432` |
| `POSTGRES_USER` | PostgreSQL application account, required when selected. (str \| None) | `None` | `devuser` / `appuser` |
| `POSTGRES_PASSWORD` | PostgreSQL application password; keep private. (str \| None) | `None` | placeholder |
| `POSTGRES_DATABASE` | PostgreSQL application database name, required when selected. (str \| None) | `None` | `aiis_ics_architecture` |
| `SQLITE_DATABASE_PATH` | SQLite database file path. (str) | `'./data/aiis_ics_architecture.sqlite3'` | `./data/aiis_ics_architecture.sqlite3` |
| `MSSQL_HOST` | SQL Server host. (str) | `'host.docker.internal'` | `host.docker.internal` |
| `MSSQL_PORT` | SQL Server TCP port. (int) | `1433` | `1433` |
| `MSSQL_USER` | SQL Server application account. (str) | `'sa'` | `sa` |
| `MSSQL_PASSWORD` | SQL Server application password; keep private. (str) | `''` | placeholder |
| `MSSQL_DATABASE` | SQL Server application database name. (str) | `'aiis_ics_architecture'` | `aiis_ics_architecture` |
| `MSSQL_DRIVER` | Installed ODBC driver name for SQL Server. (str) | `'ODBC Driver 18 for SQL Server'` | `ODBC Driver 18 for SQL Server` |
| `MSSQL_TRUST_SERVER_CERTIFICATE` | Trust the SQL Server certificate without certificate validation. (bool) | `True` | `True` |

### Bootstrap

| Key | Purpose/type | Source default | Public template value |
| --- | --- | --- | --- |
| `ADMIN_BOOTSTRAP_ENABLED` | Enable this account only for the explicit bootstrap maintenance action. (bool) | `False` | `False` |
| `ADMIN_BOOTSTRAP_USERNAME` | Username to locate or create during bootstrap. (str) | `'admin'` | `admin` |
| `ADMIN_BOOTSTRAP_PASSWORD` | Non-empty bootstrap password when enabled; keep private. (str) | `''` | `""` |
| `ADMIN_BOOTSTRAP_NAME` | Display name for a newly created bootstrap account. (str) | `'Administrator'` | `Administrator` |
| `ADMIN_BOOTSTRAP_ROLE` | Role assigned to a newly created bootstrap account. (str) | `'admin'` | `admin` |
| `ADMIN_BOOTSTRAP_RESET_PASSWORD` | Allow explicit bootstrap to reset an existing password and reactivate the account. (bool) | `False` | `False` |
| `SUPERVISOR_BOOTSTRAP_ENABLED` | Enable this account only for the explicit bootstrap maintenance action. (bool) | `False` | `False` |
| `SUPERVISOR_BOOTSTRAP_USERNAME` | Username to locate or create during bootstrap. (str) | `'supervisor'` | `supervisor` |
| `SUPERVISOR_BOOTSTRAP_PASSWORD` | Non-empty bootstrap password when enabled; keep private. (str) | `''` | `""` |
| `SUPERVISOR_BOOTSTRAP_NAME` | Display name for a newly created bootstrap account. (str) | `'Supervisor'` | `Supervisor` |
| `SUPERVISOR_BOOTSTRAP_ROLE` | Role assigned to a newly created bootstrap account. (str) | `'supervisor'` | `supervisor` |
| `SUPERVISOR_BOOTSTRAP_RESET_PASSWORD` | Allow explicit bootstrap to reset an existing password and reactivate the account. (bool) | `False` | `False` |
| `OPERATOR_BOOTSTRAP_ENABLED` | Enable this account only for the explicit bootstrap maintenance action. (bool) | `False` | `False` |
| `OPERATOR_BOOTSTRAP_USERNAME` | Username to locate or create during bootstrap. (str) | `'operator'` | `operator` |
| `OPERATOR_BOOTSTRAP_PASSWORD` | Non-empty bootstrap password when enabled; keep private. (str) | `''` | `""` |
| `OPERATOR_BOOTSTRAP_NAME` | Display name for a newly created bootstrap account. (str) | `'Operator'` | `Operator` |
| `OPERATOR_BOOTSTRAP_ROLE` | Role assigned to a newly created bootstrap account. (str) | `'operator'` | `operator` |
| `OPERATOR_BOOTSTRAP_RESET_PASSWORD` | Allow explicit bootstrap to reset an existing password and reactivate the account. (bool) | `False` | `False` |


### Entry and side-effect notes

Source execution reads this directory's `.env`; dev/prod Docker entries supply their selected env as
`/app/.env`, and packaged execution reads beside the executable. Review process environment overrides and
remove any active retired permission variable there before restarting yourself. Editing these files alone
does not prove that a running service has loaded them. Env comments are English; this reference has a
[Chinese counterpart](README.zh-CN.md#配置逐项说明).

`PRIMARY_DATABASE` takes precedence over the compatible `DATABASE_TYPE`; recognized aliases include
`postgres`/`pg` and `sqlserver`/`sql_server`. The selected engine must have its corresponding `*_ENABLED`
flag on. These flags permit selection, do not start databases, and do not route each request to all engines.
The normal async/sync application sessions use that primary database. MySQL root maintenance uses
`MYSQL_ROOT_USER`/`MYSQL_ROOT_PASSWORD` with `MYSQL_HOST`/`MYSQL_PORT`, not the ordinary application account;
these settings are not the Docker image's root-account provisioning authority. Drivers and external database
availability remain deployment prerequisites. Database-only's empty-volume initialization does not update
accounts in an existing volume.

`TESTING=True` switches MySQL application URLs to the separate test database (source default name
`aiis_ics_architecture_test`), not a universal sandbox for every engine. Database tests can create/clear
that database and require an explicitly isolated approved target; use `no_db` tests for static checks.
The public templates keep TESTING, business mock mode and the Projection runner off. Projection reads CA
raw facts, never polls PLCs, and must have one active writer: enable only on a designated host with one worker,
not the ordinary multi-worker API deployment. Its interval and batch size affect polling/work batches.
`TZ` configures process time only; it does not migrate database timestamps or the database server timezone.

All 18 bootstrap fields above apply only to explicit `main.py --maintenance bootstrap-users`, never ordinary
startup/login or Alembic. Each role's ENABLED defaults off; enabled accounts require a non-empty PASSWORD.
A missing account is created using USERNAME/PASSWORD/NAME/ROLE. Existing accounts are left alone unless
RESET_PASSWORD is true; reset changes the password, reactivates the account, and fills name/role only if absent.
It does not replace an existing non-empty role/name. Keep reset off after the intended maintenance action.
Grant arrays neither create accounts nor update their passwords. Maintenance is a database write requiring its
own operational authorization; its entry first performs the permission configuration checks documented above.

A generic current-module grant set is supervisor `["monitor","system","control-agent-read"]` and operator
`["monitor"]`. The current monitor router includes only GET `/monitor/collector/status` and
GET `/monitor/realtime/latest`: operator receives those fact queries. `system` includes user-management
writes with independent actor restrictions; `control-agent-read` covers action-scope queries. This is an
explicit grant choice, not the public templates' safe `[]` defaults. The approved local three-environment
migration adds monitor for host/prod operator and adds all three supervisor keys plus monitor for dev operator;
it is not merely an equivalent variable rename. Future interfaces added under a key require renewed review.
