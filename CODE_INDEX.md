# AIIS ICS Architecture Code Index

This is a grep-friendly topology index, not a second README. Update it only when
source topology or important entrypoints change.

## Root

- `backend/` — FastAPI, SQLAlchemy, Alembic and Core module registry.
- `frontend-js/` — JavaScript Core web shell, route/locale discovery and system UI.
- `automation-world/control-agent/` — optional Rust/Tauri field runtime and operations console.
- `tools/` — offline lineage, PLC mapping and simulator tools.
- `contracts/` — root Core hub for cross-runtime public contracts; source truth remains in code.
- `docs/` — root-PLAN-owned durable cross-repository and process documentation, indexed by a bilingual README pair.
- `plans/` — current root architecture task bundles.

## Backend entrypoints

- `backend/main.py` — production/package entrypoint.
- `backend/run.py` — local reload entrypoint.
- `backend/settings.py` — environment and database configuration.
- `backend/core/role_permissions.py` — pure role arrays, hierarchy and manifest-owner grant filtering.
- `backend/tests/test_role_api_permission_startup.py` — no-DB composition, configuration-source and maintenance-order regressions.
- `backend/app/module_registry.py` — manifest-based module discovery and router/model registration.
- `backend/app/router.py` — explicit Core/user/control-agent route boundary.
- `backend/app/energy/manifest.py` — unique price owner and independent read/manage permissions.
- `backend/app/energy/api/energy_price.py` — current/date-filtered history/hourly upsert HTTP APIs.
- `backend/app/energy/models/energy_price.py` / `schemas/energy_price.py` — constrained snapshot persistence and local JSON number contract.
- `backend/app/energy/crud/async_energy_price.py` / `services/async_energy_price.py` — async atomic hourly SQL, observedAt ordering and whole-group transaction.
- `backend/alembic/versions/20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py` — one-table successor to the unchanged Core root.
- `backend/tests/test_energy_price_api.py` / `test_energy_price_service.py` / `test_energy_price_migration.py` — no-DB HTTP, transaction, SQL and metadata checks.
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
- `frontend-js/src/app/dashboard/` / `frontend-js/src/app/plan/` — first enabled module onboarding pilot.
- `frontend-js/src/config/systemName.js` — independent bilingual build-time system names and optional login descriptions consumed through global i18n.
- `frontend-js/src/App.vue` — root view and reactive system-name browser title.
- `frontend-js/tests/module-registry/system-name.test.mjs` — independent name fallback, optional description and literal-text i18n contracts.
- `frontend-js/src/config/brand.js` / `brandOptions.js` — bundled Logo discovery and pure alignment/glow options.
- `frontend-js/src/components/shell/BrandLogo.vue` — shared login/shell image contain sizing and three glow regions.
- `frontend-js/src/assets/brand/demo-organization-logo.svg` — generic public fallback asset.
- `frontend-js/tests/module-registry/brand-options.test.mjs` — safe resource, alignment and glow contract matrix.
- `frontend-js/src/config/pageAccess.js` — shared pure role-array, subset and active-page validation.
- `frontend-js/scripts/check-page-access.mjs` — effective Vite mode/local/process configuration checker.
- `frontend-js/tests/module-registry/page-access.test.mjs` — grant failures, role decisions, env precedence and bilingual pilot regression.
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

- `automation-world/control-agent/src-tauri/src/commands/` — thin Tauri and headless command adapters.
- `automation-world/control-agent/src-tauri/src/domain/` — runtime contracts and state types.
- `automation-world/control-agent/src-tauri/src/services/` — PLC collection and snapshot orchestration.
- `automation-world/control-agent/src-tauri/src/infrastructure/` — configuration, PLC/S7, logging and database adapters.
- `automation-world/control-agent/src/app/` — module-local console views and translations.
- `automation-world/control-agent/config/` — sanitized, default-off YAML shape examples.

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

## ARCH-BE-004 hourly price entries

- `backend/app/energy/models/energy_price_hour.py` — UTC observedAt/hourStart hourly snapshots with a unique hour key.
- `backend/alembic/versions/20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py` — explicit hours-table successor; preserves the append archive.
- `frontend-js/src/app/auxiliary/views/price/index.vue` — readonly current prices, Shanghai daily history and whole-group add dialog.

## Public module admission and reintegration

- `backend/app/MODULE_CONTRACT.md` / `MODULE_CONTRACT.zh-CN.md` — durable Python v1 module handbook.
- `backend/app/module_contract.py` — public symbols and bounded legacy compatibility inventory.
- `backend/app/module_preflight.py` — source dependencies/public symbols and actual route/model conflicts; help-only bare CLI.
- `backend/app/auxiliary/api/auxiliary.py` / `models/auxiliary.py` / `services/async_auxiliary.py` — four non-price entities, read-only empty rules and explicit write transactions.
- `backend/app/monitor/models/business_history.py` / `api/temperature.py` / `api/energy.py` — two history entities and independently guarded read queries.
- `backend/app/{dashboard,energy,equipment,hr,maintenance,performance,plan,project,quality,reports}/manifest.py` — opt-in public business slices; HR disabled.
- `backend/alembic/versions/20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py` — explicit 42-table successor, no seed.
- `backend/tests/module_admission_fixtures.py` / `test_module_{contract,dependencies,conflicts,admission}.py` — reconstructable C2/E source profiles and admission matrices.
- `backend/tests/test_business_module_{reintegration,migration,permissions}.py` / `test_auxiliary_business.py` / `test_monitor_business.py` — F schema/guard/zero-write regressions.
- `frontend-js/src/app/auxiliary/views/shift/index.vue` / `tests/module-registry/shift-rule-empty-state.test.mjs` — legal unconfigured-rule state and existing-rule SFC regression.
- `backend/tests_mysql/test_module_admission.py` / `test_business_module_reintegration.py` — opt-in disposable MySQL E/F entrypoints; no shared destructive fixtures, execution requires separate approval.

## Automation World Agent foundation

- `automation-world/README.*`, `PLAN.*`, `plans/README.*` — lifecycle owner and unique root task references.
- `automation-world/data-acquisition-agent/` — independent frozen-CA derivative; DAA-only config/identity and existing headless runtime.
- `automation-world/semantic-mapping-agent/` — filtered TSS HTTP mapping/facts console, native gates and local help; no customer/SQL/legacy command closure.
