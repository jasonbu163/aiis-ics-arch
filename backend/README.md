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

## Packaging

main.py is the reload-disabled application entry; run.py is the local development entry. build.py is an optional PyInstaller source package path and never copies a real .env, data dump or customer input. See BUILD.md.
