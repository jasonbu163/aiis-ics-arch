# AIIS ICS Architecture Code Index

This is a grep-friendly topology index, not a second README. Update it only when
source topology or important entrypoints change.

## Root

- `backend/` — FastAPI, SQLAlchemy, Alembic and Core module registry.
- `frontend-js/` — JavaScript Core web shell, route/locale discovery and system UI.
- `control-agent/` — optional Rust/Tauri field runtime and operations console.
- `tools/` — offline lineage, PLC mapping and simulator tools.
- `contracts/` — root Core hub for cross-runtime public contracts; source truth remains in code.
- `docs/` — root-PLAN-owned durable cross-repository and process documentation, indexed by a bilingual README pair.
- `plans/` — current root architecture task bundles.

## Backend entrypoints

- `backend/main.py` — production/package entrypoint.
- `backend/run.py` — local reload entrypoint.
- `backend/settings.py` — environment and database configuration.
- `backend/app/module_registry.py` — manifest-based module discovery and router/model registration.
- `backend/app/router.py` — explicit Core/user/control-agent route boundary.
- `backend/app/monitor/` — collector health and generic raw/latest PLC snapshot facts.
- `backend/alembic/` — single `d4e6f8a0b2c4` Core root migration for fourteen tables plus static parity coverage.
- `backend/scripts/` — generic maintenance and smoke helpers.
- `backend/Dockerfile` — reproducible source-built backend image used by the prod deployment entry.
- `backend/Dockerfile.dev` — pinned dependency image for the source-mounted backend development service.

## Frontend entrypoints

- `frontend-js/src/router/` — router creation, auth guards and active Registry route consumption.
- `frontend-js/src/app/moduleManifest.js` — pure manifest/locale validation, normalization, sorting and access consumers.
- `frontend-js/src/app/moduleRegistry.js` — single Vite manifest/locale discovery and active assembly.
- `frontend-js/src/app/system/` — system/user/mapping Core module.
- `frontend-js/src/app/aiis_demo/` — default-disabled offline module example.
- `frontend-js/src/locales/` — global dictionaries and module locale assembly.
- `frontend-js/src/styles/` — Core theme tokens and shared layout styles.
- `frontend-js/src/components/` — shared Core UI components.
- `frontend-js/src/components/navigation/ModuleNavigation.vue` — generic group/leaf menu and icon fallback.
- `frontend-js/scripts/check-module-manifests.mjs` — dependency-free prebuild contract checker.
- `frontend-js/tests/module-registry/` — pure registry and actual source regression matrix.
- `frontend-js/Dockerfile` — locked pnpm source build copied into the Nginx runtime image.
- `frontend-js/Dockerfile.dev` — pinned dependency image for the source-mounted Vite development service.
- `frontend-js/nginx.conf` — SPA serving and `/api/v1` proxy to the Compose backend service.

Manifest-driven navigation shares the Registry and consumer-supplied page access checks.

## Docker entrypoints

- `docker-compose.dev.yml` — fixed-name MySQL `8.4.6` development stack with backend/frontend source hot reload,
  one-shot migration and an opt-in, default-off bootstrap profile.
- `docker-compose.database-only.yml` — isolated MySQL 8.4.6 volume for host-source or prod use.
- `docker-compose.prod.yml` — image-built backend and Nginx with prebuilt host dist and external MySQL.

## Control Agent entrypoints

- `control-agent/src-tauri/src/commands/` — thin Tauri and headless command adapters.
- `control-agent/src-tauri/src/domain/` — runtime contracts and state types.
- `control-agent/src-tauri/src/services/` — PLC collection and snapshot orchestration.
- `control-agent/src-tauri/src/infrastructure/` — configuration, PLC/S7, logging and database adapters.
- `control-agent/src/app/` — module-local console views and translations.
- `control-agent/config/` — sanitized, default-off YAML shape examples.

Database engine settings and YAML upload are deferred to `CA-CONFIG-001`.

## Documentation entrypoints

- `docs/README.md` / `docs/README.zh-CN.md` — bilingual index and authority boundary for durable project documents.
- `docs/multi-project-pm.md` — canonical multi-project development and governance guide.

## Tools entrypoints

- `tools/lineage-audit/` — static source/route/model evidence scanner.
- `tools/lineage-mapping-studio/` — local lineage evidence review UI.
- `tools/plc/point-mapping/` — reviewed workbook-to-contract converter.
- `tools/plc/projection-mapping/` — explicit field-to-point mapping review.
- `tools/plc/snapshot-policy/` — raw/latest policy converter.
- `tools/plc/s7-virtual-plc/` — local read-only S7 simulator.
- `tools/config/` — sanitized example contract only; site inputs stay outside the repository.

## Documentation rules

README files own stable usage and boundaries; PLAN files own current workstream
indexes; task bundles own scope and verification facts. Do not run global
documentation initialization in this repository.
