<!--
  File Path: /backend/app/README.md
  Description: Backend application module guide
  Main Features:
    - Explains backend app module ownership
    - Documents controlled package-aware manifest discovery
    - Defines safe module registration boundaries
-->
# Backend App Modules

[中文版本](README.zh-CN.md)

`backend/app/` owns FastAPI business modules and the controlled manifest discovery used by the backend composition root. This directory README is a structure guide, not a task tracker. Backend work state remains in [../PLAN.md](../PLAN.md), with detailed module-registration history in [../plans/B11-backend-module-manifest-autoregistration.md](../plans/B11-backend-module-manifest-autoregistration.md).

## Registration Model

The backend uses controlled package-aware discovery instead of unrestricted directory scanning:

- [module_registry.py](module_registry.py) enumerates only immediate child packages of the imported `app` package.
- A module opts in only when `app.<module>.manifest` directly exports a typed `manifest: ModuleManifest` whose `name` exactly matches the package name.
- A package without `manifest.py` is skipped and contributes no routes, models or Projection handlers; malformed manifests and internal manifest imports fail visibly.
- [router.py](router.py) keeps router creation and route aggregation centralized.
- Enabled manifests provide ordinary routers and Projection owners. Disabled manifests provide neither, but their declared model package is still imported for SQLAlchemy metadata and migration inspection.
- Alembic and explicit schema-maintenance actions remain the only schema-change paths; model import does not execute DDL or migrations.

Security and field-runtime boundaries stay explicit:

- `user` routes are mounted directly in [router.py](router.py) because authentication and user management are security-boundary entrypoints.
- `control_agent` routes are mounted directly because they are field-runtime and authorization-boundary APIs.
- Retired Worker-control infrastructure is not part of `app/` or ordinary discovery.

## Standard Business Module Shape

```text
backend/app/<module>/
├── __init__.py                  # Thin package entrypoint; no registration side effects
├── manifest.py                  # Registry metadata only
├── api/
│   └── routes.py                # FastAPI APIRouter definitions
├── models/                      # SQLAlchemy models
├── schemas/                     # Pydantic contracts
├── crud/                        # Database access helpers
├── services/                    # Business orchestration and transaction boundaries
├── mocks/                       # Business mock provider package; may contain only an import-safe marker
└── seeds/                       # Seed provider package; never runs writes on import
```

Some older or special modules may contain additional files, but new ordinary business modules should converge toward this shape.

## Project-local Reference Source

[`aiis_demo/`](aiis_demo/README.md) is the preferred project-local copy source when a
new module needs to learn the current package shape. It is reference-only and remains
`enabled=False`; normal composition therefore does not expose its route or Projection
owner. Its empty model package is imported for metadata discovery but declares no table.
Do not treat it as a business template, an authorization grant, or an AIIS shared
skill/template. Copying it requires deliberate replacement of every demo name and
payload, a new business permission design, and a separate Alembic migration whenever
real persistence is introduced.

## Manifest Rules

`manifest.py` should declare metadata only:

```python
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name="equipment",
    order=50,
    routers=("app.equipment.api.routes:router",),
    models_package="app.equipment.models",
    permissions=("equipment",),
)
```

Rules:

- Keep `manifest.py` import-safe and side-effect free.
- Do not open database, message-broker, PLC, camera, ERP or network connections during manifest import.
- Do not start threads, loops, timers, workers or migrations during manifest import.
- Keep route strings explicit as `module:attribute` import paths.
- Keep model package imports explicit so Alembic metadata and tests can see expected tables.
- A valid manifest is the module's opt-in; there is no second central module list to maintain.

## Adding A Normal Business Module

1. Create `backend/app/<module>/` with `__init__.py`, `manifest.py`, `api/`, `models/`, `schemas/`, `crud/`, `services/`, `mocks/` and `seeds/`.
2. Implement an `APIRouter` in `api/routes.py`.
3. Put SQLAlchemy models under `models/` and ensure `models/__init__.py` imports the models that Alembic should see.
4. Add a metadata-only `manifest.py`.
5. If diagnostic backend mock data is needed, put providers under `mocks/` and call them from Services only when `settings.BACKEND_MOCK_ENABLED` is true.
6. Keep the manifest import-safe and add focused tests for route registration, metadata registration and enabled/disabled behavior.
7. Add Alembic migrations for database structure changes. Registry model import does not replace migrations.

Do not opt high-risk control, authentication or field-runtime modules into ordinary discovery without a specific architecture decision; keep them explicit.

## Offline Module Creation SOP

Use this path when creating a normal backend business module without network access or without a generator. Prefer copying the closest existing registry-backed module, then rename it deliberately.

1. Choose a source module with the same shape. Start with the project-local
   [`aiis_demo/`](aiis_demo/README.md) reference for package and disabled-composition
   mechanics; use `plan`, `monitor`, `equipment` or `quality` for an existing business
   behavior reference. Do not use `user` or `control_agent` as templates for normal modules.
2. Copy the directory to `backend/app/<new-module>/`.
3. Keep `__init__.py` thin. It may expose package metadata, but it must not register routers, import services for side effects or start runtime work.
4. Rename Python modules, classes, schemas, service functions and table names from the old business meaning to the new one.
5. Update `api/routes.py`: route prefix, tags, endpoint names, dependency usage and service calls.
6. Update `schemas/`: request, query, response and page contracts. Backend internals stay `snake_case`; frontend-facing JSON aliasing belongs in schemas / response serialization.
7. Update `models/`: table names, indexes, constraints and relationships. Ensure `models/__init__.py` imports every model class Alembic must see.
8. Update `crud/`: persistence helpers only. CRUD functions must not commit or rollback.
9. Update `services/`: business actions, transaction boundaries, state transitions, audit/log events and external-integration decisions.
10. Keep diagnostic mocks under `mocks/` and seed providers under `seeds/`; both packages must be import-safe, and mock usage stays guarded by `settings.BACKEND_MOCK_ENABLED`.
11. Update `manifest.py`: `name`, `order`, `routers`, `models_package` and `permissions`.
12. Keep the manifest package import valid and let the controlled immediate-child discovery opt the module in.
13. Add an Alembic revision for every database structure change. Registry model import does not replace migrations.
14. Add or update focused tests for route exposure, metadata registration, response contracts and key business failures.

Do not add new dependencies in this SOP. Reuse project-local common response helpers, schema base classes, logging utilities and existing database/session patterns.

## Copy / Rename Checklist

After copying an existing backend module, run these local searches before testing:

```bash
rg -n "<old_module>|OldBusinessName|old_business_table" backend/app/<new-module>
rg -n "<new-module>|app\\.<new-module>|<new_module>" backend/app/<new-module>/manifest.py
rg -n --glob '!**/*.md' "api/mock\\.py" backend/app/<new-module>
```

Expected result:

- No stale old module import path remains unless intentionally reused.
- `manifest.name` matches the folder name exactly.
- `manifest.routers` points to the new module route object.
- `manifest.models_package` points to the new module `models` package when the module owns tables.
- The manifest name exactly matches the immediate package name and no explicit boundary module was added to ordinary discovery.
- Route prefixes and tags match the new module.
- Table names, schema names, service names and error/status keys match the new business meaning.
- No backend business mock is placed under `api/mock.py`.
- Alembic has a revision for any table, index, enum or constraint change.

If the module has no public HTTP API, omit `routers` and document why. If it has no database tables, omit `models_package` and add tests that prove the registry behavior is intentional.

## Restart and no-hot-unload semantics

Changing a manifest `enabled` value may trigger development source autoreload of the
whole backend process; if the watcher does not reload, restart manually. Adding,
removing or renaming a module/package, or changing router/models/services topology,
requires restarting the backend process or its container so discovery and composition
rebuild from zero. Production source/package changes require restart/redeploy. A
composed FastAPI application does not hot-unload a mounted router: changing an already
running manifest from enabled to disabled takes effect only after restart.

## Layering Boundaries

- API handlers stay thin: authenticate, validate, inject dependencies, call services and return response models.
- Services own business orchestration and transaction boundaries.
- Services own the decision to use module-local mock providers when `BACKEND_MOCK_ENABLED=true`; real integration checks must use `BACKEND_MOCK_ENABLED=false`.
- CRUD modules own persistence helpers and should not commit or rollback transactions.
- Domain rules should not import FastAPI objects or database sessions.
- Backend internals use `snake_case`; frontend-facing JSON naming is handled by backend schemas and response serialization.
- Device and PLC simulation belongs to Control Agent or the PLC development tools. Backend business API mock data uses `BACKEND_MOCK_ENABLED`.

## Verification

Minimum checks after changing registry-backed modules:

```bash
cd backend
uv run pytest tests/test_module_structure.py tests/test_module_registry.py tests/test_migrations.py
rg -n -P --glob '!**/*.md' "\\bMOCK_ENABLE\\b" app settings.py .env*
rg -n --glob '!**/*.md' "api/mock\\.py" app
```

Broader backend changes should run the relevant focused tests and, when appropriate:

```bash
uv run python -m compileall -q app core database scripts tests
```
