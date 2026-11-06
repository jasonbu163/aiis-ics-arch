# AIIS ICS Architecture Code Index

This is a grep-friendly topology index, not a second README. Update it only when
source topology or important entrypoints change.

## Root

- `backend/` — FastAPI, SQLAlchemy, Alembic and Core module registry.
- `backend-dotnet/` — independent C# Plan learning slice; three direct-MySQL APIs, no login; [local source index](backend-dotnet/CODE_INDEX.md).
- `frontend-js/` — JavaScript Core web shell, route/locale discovery and system UI.
- `automation-world/control-agent/` — optional Rust/Tauri field runtime and operations console.
- `field-flow/` — independent Rust/Python field runtimes; exact r4 passed unified fresh-context local QA2, with Human Owner final acceptance pending.
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

- [Field Flow README](field-flow/README.md) / [Chinese pair](field-flow/README.zh-CN.md) and [FF plan](field-flow/PLAN.md) / [Chinese pair](field-flow/PLAN.zh-CN.md) — FF-owned documentation and runtime work.
- [FF task catalog](field-flow/plans/README.md) / [Chinese pair](field-flow/plans/README.zh-CN.md) — unique owning bundle for the [ARCH-TOOL-001 r2 baseline](field-flow/plans/ARCH-TOOL-001-field-flow-runner/spec.md), including preserved r1 history and the CA prompt.
- [FF-001 r4 spec](field-flow/plans/FF-001-dual-runtime-demo01/spec.md), [Development handoff](field-flow/plans/FF-001-dual-runtime-demo01/tasks.md) and [QA records](field-flow/plans/FF-001-dual-runtime-demo01/checklist.md) — current dual candidate passed fresh QA2 AC01–AC15; three Rust QA1 defects closed and failure/history retained; Human Owner final acceptance pending.
- [FF-003 r1 scope](field-flow/plans/FF-003-csharp-runtime-demo01/spec.md) — proposed independent C# runtime, local demo01 and bilingual use/publish guides; status `draft`, exact scope approval pending, no C# implementation or QA yet.
- [FF-002 r1 scope](field-flow/plans/FF-002-user-guide-and-runtime-positioning/spec.md) — Python/Rust user guides, case-development tutorials and Rust BUILD; status `qa_passed`, with Human Owner final acceptance separate.
- [Python/Rust comparison guide](field-flow/USER_GUIDE.md) / [中文](field-flow/USER_GUIDE.zh-CN.md) — source-backed entrypoints, runtime lifecycle, methods and case walkthroughs.
- [Rust user guide](field-flow/field-flow-rust/USER_GUIDE.md) and [BUILD](field-flow/field-flow-rust/BUILD.md); [Python user guide](field-flow/field-flow-python/USER_GUIDE.md) — self-contained guides for each independently copyable project.
- [Rust project guide](field-flow/field-flow-rust/README.md), [PLC driver process](field-flow/field-flow-rust/src/driver_process.rs) and [INT response adapter](field-flow/field-flow-rust/src/infrastructure/s7_int_pdu.rs) — repaired queue/IO deadlines, pre-call clock guards and actual started statistics independently verified; formal/isolated full18 and additional protocol/process probes passed.
- [Python project guide](field-flow/field-flow-python/README.md), [runtime](field-flow/field-flow-python/src/field_flow/runtime.py), [demo01](field-flow/field-flow-python/src/field_flow/app/demo01.py) and [INT response adapter](field-flow/field-flow-python/src/field_flow/infrastructure/s7_int_pdu.py) — unchanged independent candidate passed QA2 using verified QA1 formal/isolated evidence and fresh build/unit/gate/CLI checks; [original public API precheck](field-flow/field-flow-python/tests/python_api_preflight.py) failure retained.
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
- `automation-world/data-acquisition-agent/` — independent DAA runtime; CU public-source shell, workbench plus PLC/points/storage leaves, one local owner, pure preference/navigation shell and local PLAN; legacy YAML/direct-DB/headless graph retired.
- `automation-world/data-acquisition-agent/src-tauri/src/config/local_bootstrap.rs` — SQLite-only ordinary startup, explicit UI read permission with a process-only deny override, retired-key provenance and the unchanged owned debug validation factory; no resident YAML discovery.
- `automation-world/data-acquisition-agent/src-tauri/src/domain/local_{configuration,sample,runtime}.rs` — configuration/context/envelope v1, sample/manifest v2, stable IDs, group/read budgets and self-describing runtime DTOs.
- `automation-world/data-acquisition-agent/src-tauri/src/domain/{facts_canonical,facts_wire,local_delivery}.rs` — DAA-008 lossless pf-json, original-cycle transport, strict receipts, source settings and fixed manual-read DTOs.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/{facts_http.rs,local_store/delivery.rs}` / `services/local_delivery.rs` / `commands/local_delivery.rs` — fixed bounded HTTP, v3 delivery ledger, explicit single worker, monotonic retry and nine named IPC commands; r1 hot-journal recovery remains blocked.
- `automation-world/data-acquisition-agent/src/services/factsDelivery.ts` / `components/console/{FactsDeliveryPanel,FactsDeliveryDialog}.vue` — real Workbench/storage delivery controls, source/CAS dialog, bounded queue/events/manual reads and read-only originals.
- `automation-world/data-acquisition-agent/src-tauri/src/{domain/facts_canonical_tests.rs,infrastructure/facts_http_tests.rs,infrastructure/local_store/delivery_tests.rs,services/local_delivery_tests.rs}` / `tests/facts-delivery.test.mjs` — fixed provider vectors, transport substitutes, owned synthetic SQLite transactions/crashes and focused UI contracts; no actual HTTP/DS proof.
- `automation-world/data-acquisition-agent/src-tauri/src/domain/business_time.rs` — centralized Shanghai calendar timestamps, canonical millisecond parsing and retention boundaries; monotonic scheduling remains separate.
- `automation-world/data-acquisition-agent/src-tauri/src/services/local_{configuration,activation,supervisor,scheduler,storage,queries,recovery}.rs` — protected derived configuration/CAS, token activation, unique PLC actors, fair groups, admission, bounded history and stopped recovery.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/` — new config2/runtime3 and legacy v2/v2 admission, DELETE/EXTRA, serial work, immutable cycles and same-runtime delivery transactions with protected capacity; paired schema READMEs.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/{tia_source,plc_layout,local_decode,managed_s7,local_profile_lock,local_logging,local_fixture}.rs` — full bounded source expansion, verified standard nested layout inference, typed values, persistent S7, OS lock, bounded logs and compile-gated owned fixtures.
- `automation-world/data-acquisition-agent/src-tauri/src/commands/local_{acquisition,validation}.rs` / `src/bin/daa-local-validation.rs` — named local IPC and nondefault debug JSON Lines adapter; no ACK/upload/SQL executor.
- `automation-world/data-acquisition-agent/src/services/localAcquisition.ts` / `src/console/composables/useLocalAcquisitionConsole.ts` — bootstrap-first IPC contract, local edit-base CAS and one runtime refresh owner; normal reload/save no longer query or retry YAML migration.
- `automation-world/data-acquisition-agent/src/components/console/{ConfigRevisionBar,LocalHistoryPanel,LocalLogPanel}.vue` — draft/active/loaded/used version facts and bounded immutable history/events; ordinary pages have no YAML migration fault/retry entry.
- `automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue` — immutable sample summary, paged point facts and collapsed formatted JSON; upload state is separate from read quality.
- `automation-world/data-acquisition-agent/src/console/sampleDetails.ts` — read-only frozen-context labels, point values and whitespace-only JSON formatting without rewriting stored originals or hashes.
- `automation-world/data-acquisition-agent/src/console/time.ts` — host-independent Shanghai wall-time inputs, second-level views and inclusive millisecond history boundaries.
- `automation-world/data-acquisition-agent/src/console/tableWidths.ts` — history/sample-table column minimums, separate stable local preference keys and restore-default behavior without business configuration writes.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/time_contract_tests.rs` — synthetic-profile tests for read-only admission, schema/time contracts, canonical queries and immutable cycle evidence.
- `automation-world/data-acquisition-agent/tests/time-and-history-preferences.test.mjs` — bounded Node/TypeScript checks for host-independent time boundaries and isolated history-column preferences.
- `automation-world/data-acquisition-agent/src-tauri/src/domain/yaml_migration.rs` / `services/local_yaml_migration.rs` — 私有历史receipt摘要的只读兼容DTO/IPC，retry写前拒绝；旧startup/execute仅测试编译，无设备连接。
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/yaml_migration.rs` / `yaml_migration_tests.rs` — 仅测试编译的历史双来源安全读取/停用转换与保护验证；普通启动不扫描YAML。
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/yaml_migration.rs` — 保留私有receipt/来源前缀及只读摘要；历史原子迁入DML仅测试编译，不执行schema迁移。
- `automation-world/data-acquisition-agent/src/console/composables/useAgentConsoleShell.ts` / `components/console/YamlMigrationNotice.vue` — 纯壳偏好导航与已从普通页面解绑的历史迁入组件；无桥预览无外发/假保存。
- `automation-world/data-acquisition-agent/vite.validation.config.ts` / `src-tauri/tests/fixtures/local-acquisition/` — env-isolated validation build and bounded sanitized parser/layout/transport fixtures.
- `automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-minimal/` — handwritten DB21/UDT three-leaf controlled import pair, independent expected checklist and paired notes; no TIA export or live address proof.
- `automation-world/semantic-mapping-agent/` — Rust/SQLite-owned local connection/catalog/materials/targets/rules/mappings and saved-revision pure preview; normal delivery admission disabled for SMA-004. Read-only facts and inert startup v1 compatibility remain; production/help/legacy SQL responsibilities stay retired.
- `automation-world/semantic-mapping-agent/src/console/uiPreferences.ts` — isolated SMA theme/language preferences; App consumes CU public layout/sidebar/topbar/cards/actions/status and themed Element Plus dialogs without business-state remounts.
- `automation-world/semantic-mapping-agent/tests/cu-integration.test.mjs` — UI preference persistence/fallback, cross-application/business-key isolation and no-HTTP regression; all native business tables reuse SMA tableWidths state/directive.
- `automation-world/semantic-mapping-agent/src-tauri/src/contracts/local_configuration.rs` — finite local configuration, CAS intent, import preview and complete JSON backup DTOs.
- `automation-world/semantic-mapping-agent/src-tauri/src/domain/local_configuration/` — complete graph/type/reference validation, normalized resource transforms and saved-revision pure mapping preview.
- `automation-world/semantic-mapping-agent/src-tauri/src/infrastructure/config_store/mod.rs` — SMA-owned schema v1 SQLite singleton; short-transaction CAS, bounded busy failure and atomic rollback.
- `automation-world/semantic-mapping-agent/src-tauri/src/services/local_configuration/mod.rs` — serialized local configuration use cases, runtime-busy guard and content/revision-bound preview/apply.
- `automation-world/semantic-mapping-agent/src-tauri/src/commands/local_configuration/mod.rs` — thin local configuration/load/change/import/export/saved-preview IPC adapters.
- `automation-world/semantic-mapping-agent/src/app/twin-facts/api/localConfiguration.ts` — native configuration facade with observed revision and explicit import token; no remote/localStorage fallback.
- `automation-world/semantic-mapping-agent/src-tauri/tests/local_configuration_tests.rs` — disposable SQLite CAS/rollback/busy/corruption/reference/limits/profile/process-reopen tests.
- `automation-world/semantic-mapping-agent/tests/local-configuration.test.mjs` — explicit in-memory IPC/store tests for stale editor CAS, no implicit network and JSON/XLSX boundaries.
  - `src/app/twin-facts/store/mappingStartup.ts` — Mapping-only startup state; `src/console/tableWidths.ts` / `time.ts` — stable field column preferences and Shanghai calendar display.
  - `src-tauri/tests/startup_cleanup_tests.rs` / `tests/cleanup.test.mjs` — isolated preference, retirement, file exchange, gate and display regressions.


## ARCH-BE-003 complete temperature sample slice

- `backend/app/equipment/config.py`, `error_codes.py`, `temperature_sample_domain.py`: module-local lazy scope, stable errors, strict decimal/time normalization and canonical fingerprint.
- `backend/app/equipment/api/temperature_samples.py`, `temperature_http.py`: independent async POST/GET and local sanitized HTTP adapter.
- `backend/app/equipment/schemas/temperature_sample_in.py`, `temperature_sample_query.py`, `temperature_sample_out.py`: strict camelCase complete sample/query/output contracts.
- `backend/app/equipment/models/temperature_sample.py`: immutable observations and actor delivery receipts, exact decimals/UTC milliseconds/binary unique keys.
- `backend/app/equipment/crud/async_temperature_sample.py`, `services/async_temperature_sample.py`: scoped SQL and atomic commit/rollback with bounded unique-race recovery.
- `backend/alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py`: two-table explicit d2 successor; no old-row migration.
- `backend/tests/test_equipment_temperature_api.py`, `test_equipment_temperature_service.py`, `test_equipment_temperature_migration.py`, `test_equipment_temperature_config.py`: no-DB HTTP/auth/transaction/config/recorder contracts.
- `backend/tests_mysql/test_equipment_temperature.py`: separately gated disposable MySQL proof outside destructive shared conftest.
- [Equipment guide](backend/app/equipment/README.md) / [中文说明](backend/app/equipment/README.zh-CN.md): separate old/new sources and runtime gates.


## Mapping business HTTP domains

- `backend/app/{equipment,performance,monitor}/mapping_{config,domain,error_codes}.py` — local scopes, strict numbers/source times/presence fingerprints and stable errors.
- `backend/app/{equipment,performance,monitor}/models/mapping_ingest.py` — three typed receipts, exact FK targets and production observation watermark; explicit migration owns DDL.
- `backend/app/equipment/api/{mapping_samples,temperature_dashboard,mapping_http}.py` / `schemas/{drive_sample_in,production_parameter_sample_in,mapping_sample_query}.py` — equipment HTTP boundaries and complete-temperature read adapter.
- `backend/app/equipment/services/{async_drive_sample,async_production_parameter_sample,async_temperature_dashboard}.py` / `crud/{async_drive_sample,async_production_parameter_sample,async_mapping_ingest}.py` — bounded merge/receipt transactions and scoped reads.
- `backend/app/performance/api/{mapping_observations,process_samples,mapping_http}.py` / `schemas/{production_observation_in,process_sample_in,mapping_query}.py` — ordered production/parent process inputs and local HTTP lifecycle.
- `backend/app/performance/services/{async_production_observation,async_process_sample,async_mapping_query}.py` / `crud/{async_production_observation,async_process_sample,async_mapping_ingest}.py` — production watermark, manual priority, scoped parent/child transactions and read adapters.
- `backend/app/monitor/api/{process_curve_samples,mapping_http}.py` / `schemas/{process_curve_in,process_curve_query}.py` / `services/async_process_curve_sample.py` / `crud/{async_process_curve_sample,async_mapping_ingest}.py` — immutable complete-curve source domain and Shanghai-day reads.
- `backend/alembic/versions/20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py` — sole e4 successor, seven-table nullable HTTP increments, three receipts and observation state, guarded downgrade.
- `frontend-js/src/components/BusinessDataSourceSelect.vue` / `src/utils/businessDataSource.mjs` — source/equipment URL selection and pure request-generation guard.
- `backend/tests/test_mapping_{api,service,migration,compatibility}.py` / `test_{equipment,performance,monitor}_mapping.py` — no-DB source/HTTP/transaction/SQL/schema contracts.
- `backend/tests_mysql/test_mapping_business_api.py` — separately gated BE006/64/f6 disposable MySQL entry, outside shared destructive fixtures.
- `frontend-js/src/utils/businessDataSource.test.mjs` / `src/app/{equipment,monitor}/api/mapping-source.test.mjs` — source paths, empty selection and stale-response contracts.

- `automation-world/data-acquisition-agent/src-tauri/src/domain/source_import.rs` — explicit per-block mapping, immutable lineage/UDT binding, identification and delta preview DTOs.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source/{parser,reconcile,tests}.rs` — safe declaration boundaries/limited syntax, selected immutable-version reconciliation and preservation tests.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/plc_layout/tests.rs` — prior independent Siemens standard-word oracle and whole-DB/manual-address guards.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/source_import_tests.rs` — owned-temp real-store/engine CAS, atomic rollback, physical archive reuse and old history/receipt preservation tests.
- `automation-world/data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue` — private paged block selection/number table and bounded import/structure dialogs; state remains with the single console owner.
- `automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-multi-db/` — handwritten six-DB/three-UDT inputs, independent structure expectations and prior per-leaf layout oracle; no private source or field-address proof.

## DAA technical names and shared import core

- `automation-world/shared/tia-import-core/src/{lib,model,parser,layout,naming}.rs` — std-only no-I/O catalog/structured-path DTOs and the single bounded TIA parser, expansion, standard layout and deterministic namespace naming algorithm; DAA consumes a local path dependency.
- `automation-world/shared/tia-import-core/src/dependencies.rs` / `tests/dependencies.rs` — additive AST-based UDT dependency plans, unique recursive resolution, explicit duplicate-source choices and located missing/cycle regressions; no I/O or changes to DAA's explicit expansion contract.
- `automation-world/shared/tia-import-core/tests/contract.rs` / `fixtures/{names.db,names.udt,expected-v1.json,daa005-layout-oracle.json}` — independent consumer/name fixtures v1 and exact prior layout-oracle mirror; no real inputs.
- `automation-world/data-acquisition-agent/src-tauri/src/domain/point_naming.rs` / `services/local_point_naming.rs` — optional nameMode/finite preview DTO, pure adapter, single bounded token/digest/ETag cache and atomic selected/edit confirmation through existing Stores.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source/parser.rs` / `infrastructure/plc_layout.rs` — shared algorithm adapters retaining DAA raw/version/closure proof, manual-address protection, CAS and same-transaction offset/name confirmation.
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/point_naming_tests.rs` — owned Engine/Stores old-JSON/selected/CAS/mode/rollback/history checks and explicit cfg(test) native seed; no product seed endpoint.
- `automation-world/data-acquisition-agent/src/app/plc/components/PointNamePreviewDialog.vue` / `SourceImportPanel.vue` / `views/points/index.vue` — cross-page explicit selection, technical/original name differences, pending/legacy and paged dialogs under the sole owner.
- `automation-world/data-acquisition-agent/tests/point-editing.test.mjs` — real Vue owner/SFC lifecycle tests with isolated IPC doubles: checked-only grouping, save-before-edit CAS requests, preserved conflicts, cancellation and repeat editing; no SQLite/PLC/native operations.
- `automation-world/data-acquisition-agent/tests/sample-details.test.mjs` — immutable sample projections, exact JSON tokens, value/quality distinction, paging/column preferences and bilingual detail rendering without SQLite or PLC access.
- `automation-world/data-acquisition-agent/src-tauri/src/config/mod.rs` — source-owned literal env parsing, process/file/default profile selection and early path/file rejection; ordinary files ignore retired read/YAML keys, while owned validation retains its original contract.

## DS product MVP and finite protocol validation

- `automation-world/device-simulator/src-tauri/src/config/bootstrap.rs` — ordinary desktop source-owned env/profile selection with early validation and unchanged explicit test-automation profile authority; no protocol or runtime policy changes.
- [DS project](automation-world/device-simulator/README.md) / [plan](automation-world/device-simulator/PLAN.md): independent DAA-derived Tauri/Vue product with six pages and explicit validation entry points, with no DAA acquisition/upload/runtime dependency. DEV execution facts belong to the [owning tasks](plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md); latest independent Verification/Owner status belongs to the [owning checklist](plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md).
- [Rust composition](automation-world/device-simulator/runtime/src/app.rs), [configuration](automation-world/device-simulator/runtime/src/domain/configuration.rs), [typed codec](automation-world/device-simulator/runtime/src/domain/typed_value.rs), [rules](automation-world/device-simulator/runtime/src/domain/rule.rs), [coverage](automation-world/device-simulator/runtime/src/domain/layout.rs), [image](automation-world/device-simulator/runtime/src/domain/image.rs), [owner](automation-world/device-simulator/runtime/src/services/owner.rs), [lifecycle](automation-world/device-simulator/runtime/src/services/lifecycle.rs): UUID manager, single mutation owner and joint admission/stop truth.
- [Config store](automation-world/device-simulator/runtime/src/infrastructure/config_store/mod.rs), [v1 schema](automation-world/device-simulator/runtime/src/infrastructure/config_store/migrations/0001_initial.sql), [profile lock](automation-world/device-simulator/runtime/src/infrastructure/profile_lock.rs), [configuration service](automation-world/device-simulator/runtime/src/services/configuration.rs), [source import](automation-world/device-simulator/runtime/src/services/source_import.rs), [layout](automation-world/device-simulator/runtime/src/services/layout.rs), [naming](automation-world/device-simulator/runtime/src/services/naming.rs), [apply](automation-world/device-simulator/runtime/src/services/apply.rs): DS-owned SQLite revisions/CAS and shared-core consumers, with explicit stopped loading.
- [Thin desktop host](automation-world/device-simulator/src-tauri/src/lib.rs), [16 command adapters](automation-world/device-simulator/src-tauri/src/commands/mod.rs), [strict DTOs](automation-world/device-simulator/runtime/src/config/workspace.rs), [frontend facade](automation-world/device-simulator/src/services/deviceSimulator.ts), [host state](automation-world/device-simulator/src/console/composables/useDeviceSimulator.ts) and [six page registry](automation-world/device-simulator/src/console/sections.ts): normal IPC and dirty-close workflow; source/build evidence is distinct from native verification.
- [Source import panel](automation-world/device-simulator/src/app/simulator/components/SourceImportPanel.vue), [IPC health](automation-world/device-simulator/src/console/ipcStatus.ts), [feedback tests](automation-world/device-simulator/tests/import-feedback.test.mjs): Rust-owned automatic UDT links and explicit ambiguity resolution through the existing import command; business validation is separate from bridge availability.
- [Native C bridge](automation-world/device-simulator/native/bridge/ds_s7_bridge.cpp), [ABI header](automation-world/device-simulator/native/bridge/ds_s7_bridge.h), [CMake](automation-world/device-simulator/native/CMakeLists.txt), [automatic Cargo build](automation-world/device-simulator/runtime/build.rs), [native FFI](automation-world/device-simulator/runtime/src/infrastructure/native_ffi.rs), [clock](automation-world/device-simulator/runtime/src/infrastructure/clock.rs), [logging](automation-world/device-simulator/runtime/src/infrastructure/logging.rs): finite Snap7 protocol/IO/join adapter, no C++ business image.
- [Owner tests](automation-world/device-simulator/runtime/tests/owner_contract.rs), [retention/receipt tests](automation-world/device-simulator/runtime/tests/apply_retention.rs), [store tests](automation-world/device-simulator/runtime/tests/configuration_store.rs), [v1 consumer tests](automation-world/device-simulator/runtime/tests/layout_naming.rs) and [typed/rule tests](automation-world/device-simulator/runtime/tests/typed_rules.rs): real runtime/configuration contracts, including typed snapshot consumers and failure receipts; the owning bundle records K/N/original protocol execution separately from independent verification. Obsolete G0 entry points were retired after the approved archive and DEV product gate; the owning task preserves the per-file migration and subsequent checks.

- [Formal validation](automation-world/device-simulator/scripts/run_validation.py), [B0 build/ABI/budget](automation-world/device-simulator/scripts/build_native.py), [original wire matrix](automation-world/device-simulator/scripts/run_protocol.py), [sealed raw](automation-world/device-simulator/scripts/collect_evidence.py), [verification](automation-world/device-simulator/scripts/verify_evidence.py), [conditional retirement](automation-world/device-simulator/scripts/retire_g0.py): explicit role/owned paths, no default side effects.
- [Fixed native driver](automation-world/device-simulator/tests/ui/native_driver.js), [bounded report adapter](automation-world/device-simulator/src-tauri/src/testing/native_driver.rs), [product test host](automation-world/device-simulator/runtime/src/bin/ds-test-host.rs), [test-only hooks](automation-world/device-simulator/runtime/src/testing/hooks.rs), [generic fixture](automation-world/device-simulator/tests/fixtures/product-workspace.json), [protocol fixture](automation-world/device-simulator/tests/fixtures/protocol-workspace.json): real DOM/normal IPC and same product runtime; non-default feature plus owned manifest.


<a id="arch-be-010-a0-integration-source"></a>
## ARCH-BE-010 shared integration primitives and A0 provenance

- [backend/common/integration/__init__.py](backend/common/integration/__init__.py) — finite JSON/envelope/digest/receipt/HTTP primitives; no DB wiring.
- [backend/common/integration/canonical.py](backend/common/integration/canonical.py) — finite JSON/envelope/digest/receipt/HTTP primitives; no DB wiring.
- [backend/common/integration/envelope.py](backend/common/integration/envelope.py) — finite JSON/envelope/digest/receipt/HTTP primitives; no DB wiring.
- [backend/common/integration/http.py](backend/common/integration/http.py) — finite JSON/envelope/digest/receipt/HTTP primitives; no DB wiring.
- [backend/common/integration/receipt.py](backend/common/integration/receipt.py) — finite JSON/envelope/digest/receipt/HTTP primitives; no DB wiring.
- [backend/app/equipment/api/integration.py](backend/app/equipment/api/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/equipment/schemas/integration.py](backend/app/equipment/schemas/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/equipment/models/integration.py](backend/app/equipment/models/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/equipment/integration_config.py](backend/app/equipment/integration_config.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/equipment/integration_domain.py](backend/app/equipment/integration_domain.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/equipment/integration_error_codes.py](backend/app/equipment/integration_error_codes.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/performance/api/integration.py](backend/app/performance/api/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/performance/schemas/integration.py](backend/app/performance/schemas/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/performance/models/integration.py](backend/app/performance/models/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/performance/integration_config.py](backend/app/performance/integration_config.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/performance/integration_domain.py](backend/app/performance/integration_domain.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/performance/integration_error_codes.py](backend/app/performance/integration_error_codes.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/monitor/api/integration.py](backend/app/monitor/api/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/monitor/schemas/integration.py](backend/app/monitor/schemas/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/monitor/models/integration.py](backend/app/monitor/models/integration.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/monitor/integration_config.py](backend/app/monitor/integration_config.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/monitor/integration_domain.py](backend/app/monitor/integration_domain.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/app/monitor/integration_error_codes.py](backend/app/monitor/integration_error_codes.py) — module-owned typed integration, isolated A+B QA passed; default-off / unadopted.
- [backend/tests/test_business_integration_contract.py](backend/tests/test_business_integration_contract.py) — A0 no-DB validation and frozen public vectors.
- [backend/tests/test_business_integration_api.py](backend/tests/test_business_integration_api.py) — A0 no-DB validation and frozen public vectors.
- [backend/tests/test_business_integration_migration.py](backend/tests/test_business_integration_migration.py) — A0 no-DB validation and frozen public vectors.
- [backend/tests/test_business_integration_compatibility.py](backend/tests/test_business_integration_compatibility.py) — A0 no-DB validation and frozen public vectors.

## ARCH-BE-009 PLC facts source

- `backend/app/plc_facts/manifest.py` — API-only module v1 registration, three routes, no permission grant.
- `backend/app/plc_facts/{config,error_codes,canonical,source,retention,cursors}.py` — default-off admission, strict Decimal JSON, original v2 validation, definition and part digests, Shanghai nanoseconds/natural months, signed bounded cursors.
- `backend/app/plc_facts/api/{routes,batches,latest,history,http,dependencies}.py` — thin anonymous adapters, local typed failures, admission before session, complete dependency exit before send.
- `backend/app/plc_facts/schemas/{source,batch_in,query,receipt_out,read_out}.py` — original material, batch/receipt, strict query, latest/changes/range and gap schemas.
- `backend/app/plc_facts/models/{state,receipts,facts}.py` — seven owner tables with binary identity and UTF-8 BLOB precision.
- `backend/app/plc_facts/crud/{async_ingest,async_query,sync_maintenance}.py` — async facts/query and explicit synchronous maintenance SQL; no commits.
- `backend/app/plc_facts/services/{async_ingest,async_query,sync_maintenance}.py` — transaction ownership, replay/rejection, publication order, expiry guards and bounded maintenance.
- `backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py` — explicit seven-table successor of f6, empty/unadopted downgrade guard.
- `backend/scripts/plc_facts_maintenance/main.py` — no-argument help before settings import; explicit status/adopt/cleanup and JSON Lines evidence.
- `backend/tests/test_plc_facts_{contract,api,source,ordering,cursor,retention,migration,compatibility,maintenance}.py` — no-DB source and behavior checks.
- `backend/tests_mysql/test_plc_facts.py` — separately gated MySQL verification entry, never run by A.
- `contracts/published/http-api/plc-facts-v1/` — fixed OpenAPI/schema and independent source vectors; isolated A+B QA passed, Owner final/provider-ready and actual adoption pending.

Package `__init__.py` files, `mocks/` and `seeds/` are import-safe and do not execute setup or fallback providers.


## ARCH-BE-010 r2 bounded business integration

- `backend/common/integration/storage.py` — pure adoption manifest/probe values, finite basis and Shanghai/legacy conversions; no IO/SQL.
- `backend/common/integration/{envelope,receipt,http,canonical}.py` — strict numeric JSON/OpenAPI, typed success/receipt, complete dependency exit and frozen dual digests.
- `backend/app/{equipment,performance,monitor}/integration_storage.py` — owner-fixed 13-table/41-column profile and read-only legacy views.
- `backend/app/{equipment,performance,monitor}/crud/{async_integration,sync_integration}.py` — passed-session current-read adoption probes and owner async business/receipt SQL.
- `backend/app/equipment/services/async_integration.py` — temperature immutability and drive/parameter NULL-fill transactions.
- `backend/app/performance/services/async_integration_{observation,process}.py` — serialized production event/watermark/receipt and proven-parent process transactions.
- `backend/app/monitor/services/async_integration.py` — immutable 33-metric curve transactions and permanent source/mapping receipt.
- `backend/alembic/versions/20261104_1400_1b3d5f7a9c20_add_business_integration_receipts.py` — exact four-table successor of BE009 0a2; rejects nonempty destructive downgrade.
- `backend/scripts/business_time_adoption/main.py` — explicit read-only inspect/plan/verify, candidate reports, bare help without target/config IO.
- `backend/tests/test_business_integration_{service,storage,provider}.py` — no-DB transaction/compatibility/time/typed provider tests.
- `backend/tests/test_business_time_adoption.py` — no-side-effect CLI and finite candidate boundary tests.
- `backend/tests_mysql/test_business_integration.py` — separately gated real MySQL business/concurrency/commit-loss/retention entry source; A never executes it.
- `backend/tests_mysql/test_business_time_adoption.py` — separately gated isolated 13-table/41-column synthetic time fixture; never a production historical apply tool.
- `contracts/published/http-api/business-integration-v1/` — closed eight-operation OpenAPI, normative examples, units/precision/replay and adoption boundaries.
