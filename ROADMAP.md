# AIIS ICS Architecture Roadmap

Chinese version: [ROADMAP.zh-CN.md](ROADMAP.zh-CN.md)

## 1. Purpose and baseline

This roadmap describes the target responsibilities of PW, AW and AIW, and the capability stages for reaching them while preserving the stable baseline. It is a development direction, not a claim that the target applications, tables or deployments already exist.

The current source surfaces remain `backend/` (FastAPI/SQLAlchemy/Alembic), `frontend-js/` (Vue JavaScript) and `automation-world/` (Rust/Tauri). The original Control Agent (CAF frozen-reference identity in this revision) collects and decodes PLC values, writes backend-owned raw/latest snapshots directly to the database, and supplies the backend Projection framework. The public template does not imply that a customer Handler or a live PLC chain is running.

Existing documentation at `automation-world/control-agent/` records the relocated frozen old CA baseline. New CA means control execution; CAF relocation/path needs its owning task evidence and is not certified here. DAA inherits an independent project from frozen CA; SMA contains a filtered copy of generic HTTP mapping from `data-twin-backend` (DTB) Twin State Studio (TSS), with original TSS retained. [ARCH-AW-001](plans/ARCH-AW-001-agent-foundation/spec.md) tracks initialization and no-I/O native startup; its bundle owns independent QA/final acceptance. `aw_*` tables, new AW APIs, shared UI and the business chain remain targets.

| Document | Responsibility |
| --- | --- |
| [README.md](README.md) | Current identity, source layout and run entrypoints |
| This ROADMAP pair | Long-term responsibilities, stages, dependencies and completion gates |
| [PLAN.md](PLAN.md) | Current task status, evidence summary and next gate |
| [ARCH-MULTI-001 r2](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | Approved scope of this documentation task; r1 retained as history |
| [AW whitepaper](docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md) / [runtime design](docs/AIIS_AW_Runtime_Design.md) | ARCH-AW-002 r2 role, local SQLite/API and shared visual flow design; no implementation claim |
| Each implementation task bundle | Exact approved scope, Development evidence and independent Verification |

The future direction replaces r1's interchangeable-backend/default-stack roadmap with responsibility-based evolution. Old version defaults, database matrices, directory proposals and Ant Design Vue migration are not commitments of this roadmap. Any remaining need requires a separate task.

## 2. Three-world responsibilities

| World | Owns | Current transition and target |
| --- | --- | --- |
| PW | Business models, users and permissions, business rules, transactions and business APIs | Existing FastAPI business capabilities remain PW responsibilities; future target is C#/.NET/ASP.NET Core with FastEndpoints |
| AW — Automation World | Acquisition, field facts, semantic mapping; later archiving and controlled execution as needed | Rust; reuse CAF/TSS material first. Local SQLite owns near-term configuration; existing FastAPI hosts fact, durable-intent and runtime APIs. AWB with Axum is deferred |
| AIW | Models, analysis, reasoning and recommendations | Python/FastAPI; PW business rules and authorization decide how outputs are adopted |

These are responsibility boundaries. They do not require three repositories, three immediate deployments or a simultaneous language migration. Python business code does not become AIW merely because it is Python. AIW does not acquire direct authority over field actions.

Keep the current stable baseline usable and approve each implementation independently. Field control, database changes, PW migration and AWB remain separate work. This direction does not restore Celery, Redis or retired industrial-command contracts.

## 3. Data and configuration flows

### Current source path

```text
PLC -> original CA / CAF acquisition/decoding -> backend raw/latest snapshot database
    -> backend Projection input resolution -> module business Handler
    -> business state/records -> business API/UI
```

Source anchors: [CAF historical acquisition](automation-world/control-agent/src-tauri/src/services/plc_collection.rs), [snapshot writer](automation-world/control-agent/src-tauri/src/infrastructure/database/repositories/mod.rs), [Projection runner](backend/projection/runner.py). This is a source-level responsibility description, not field validation.

### Near-term target path

```text
PLC -> DAA acquisition/decoding -> FastAPI AW facts API / aw_* latest facts
    -> SMA binding/validation/request assembly -> PW business API
    -> business Service / business tables -> UI; later AIW consumption when authorized

Agent UI -> local Rust configuration service -> own SQLite -> validation/explicit activation
Third party -> system API validation/durable intent -> CA atomic claim -> device write/ack
                                                     CA -> execution receipt
Later as needed: central publication -> Agent download/validation/activation/status
```

Business APIs accept semantic device/business identities, measurements, timestamps and events. Business Services do not interpret PLC DB numbers, offsets, bits or raw point names; provenance can remain available for tracing. SMA owns field conversion and request assembly. Order transitions, business-state rules and transactions remain in PW.

Freeze the configuration, facts, mapping/receipt contracts and one actual business API pilot first. The pilot does not require implementing all eight inventoried legacy Handler APIs. Once contracts are fixed, backend, DAA and SMA implementation can proceed in parallel; integration requires real callable APIs.

## 4. Independent Agents, CAF and CU

ARCH-AW-001 records the independent DAA/SMA foundation. New CA targets a Tauri management entry and independent Rust control execution. CAF denotes the frozen original CA reference; no unconfirmed expansion or new path is invented. Existing old `control-agent/` documents and the `console-ui/` directory do not prove new CA/CU delivery.

| Role | Near-term design responsibility |
| --- | --- |
| DAA | Fixed S7 acquisition, DB/UDT import and constrained manual offsets, local configuration and facts API; no business flow canvas |
| SMA | Semantic processing of AW facts and third-party/upstream API delivery; no PLC/business-database writes |
| CA | Consume durable eligible system intents; map, check field conditions, write/handshake and report; no arbitrary external URL-to-device path |
| CAF | Frozen original CA reference and compatibility provenance; not an active shared runtime |
| CU / console-ui | Shared UI source and runnable design workbench; build-time reuse, no online workbench dependency |
| AWC | Long-term console role and management form, distinct from CU source components |

Roles keep independent entrypoints, configuration/credentials, writable state, queues and lifecycles. Co-location does not merge resident processes. Window-close, background and explicit-exit behavior require implementation contracts; Tauri does not supply headless hosting automatically.

## 5. Shared UI, Flow Core and independent delivery

Use [CAF console material](automation-world/control-agent/src/layouts/AgentLayout.vue) as the visual reference. CU UI composition describes pages/layout/parameters; SMA/CA flow composition describes triggers, inputs, transformations, conditions and actions. Their publication semantics differ. Rust Flow Core is shared runtime capability outside CU; CU does not operate PLCs.

```text
CU shared source + Agent UI -> own dist -> own installer
Shared flow editor + Rust Flow Core -> separate SMA / CA hosts and nodes
CU workbench previews designs independently; installed Agents need no online workbench.
```

Recommend a Vue canvas and Rust interpretation of versioned definitions, without code generation/recompilation per edit. Vue Flow is a candidate. Node-RED plus a Rust device service is an alternative, not arbitrary Node-RED JSON/Function compatibility. SMA assembly rejects device-write nodes; delivery retry and CA unknown-result reconciliation use distinct recovery policies.

Implementation still needs Vite/TypeScript resolution, dependency consistency, frontendDist, separate ports, packaging and platform startup evidence. Shared source is a rebuild dependency, not an online service. This document establishes no completed build capability. See [Tauri project structure](https://v2.tauri.app/start/project-structure/).

## 6. Reuse CAF, TSS and generic backend capabilities

| Source | Reuse | Required adaptation |
| --- | --- | --- |
| Frozen reference [CAF](automation-world/control-agent/README.md) | PLC reading, decoding, collection loops, diagnostics and logs | Explicitly import configuration into local SQLite; upload through facts APIs; central publication is later work |
| DTB `twin-state-studio/` | Pure Rust mapping Domain, scheduler, facts/target-API binding, value rules, editing and diagnostics | Adapt lifecycle, networking and backend dependencies; retain functional logic while reusing CAF visual material |
| DTB generic backend | Fact/configuration APIs, execution leases and receipts | Fit this repository's MySQL, Registry/manifest, authentication/permissions, response contract and explicit Alembic migrations |

External source references in DTB are `twin-state-studio/README.zh-CN.md`, `twin-state-studio/src-tauri/src/domain/mapping_runtime/mod.rs`, `twin-state-studio/src-tauri/src/services/mapping_runtime/mod.rs` and `backend/app/tss/`. They fix SMA provenance. The current SMA retains applicable desktop HTTP/pure computation and excludes customer/SQL/legacy IPC and cross-DTB help generation. It starts independently; online capabilities still require compatible Backend contracts. This foundation neither imports DTB backend nor implements new AW APIs.

MSSQL-specific mechanisms such as `ROWVERSION` need a MySQL-compatible contract. DTB migration files are historical source material, not ready-to-run migrations for this repository. Preserve source attribution and applicable licensing. Import reusable public capabilities and sanitized examples only; customer pages, real configurations, data/resources and legacy direct-business-table writes remain outside the new AW boundary.

Retain the historical CAF database-snapshot and backend Projection path as an explicit compatibility/rollback path until a controlled switch. In the target chain DAA uses facts APIs and SMA writes business results through business APIs. Current DAA temporarily retains the old snapshot implementation with external gates off; new fact-API integration remains later work.

## 7. Configuration, facts and the `aw_` ownership marker

Local SQLite is the near-term DAA configuration authority; SMA/CA are recommended to follow with separate instance stores. FastAPI provides facts, durable intents, claims and receipts. Central publication and AWB are deferred. The following `aw_` names mark backend AW ownership; central configuration/mapping tables are later candidates, not concurrent editable authorities alongside SQLite.

| Illustrative table | AW responsibility |
| --- | --- |
| `aw_collection_configs` | Versioned acquisition configuration |
| `aw_collection_facts` | Fact definitions and latest values |
| `aw_target_apis` | Target API parameter contracts |
| `aw_mapping_configs` | Fact/constant bindings and mapping configuration |
| `aw_mapping_runtime_states` | Mapping runtime states, leases and receipts |
| `aw_agent_states` | Agent status and applied configuration versions |

These names illustrate ownership, not a final schema. Orders, device business states and business sampling records keep their business owners and table names. A table does not become AW-owned because a Mapping references it. The prefix establishes neither database/permission isolation nor a completed AW split.

Acquisition configuration must cover both [plc_points.yaml](automation-world/control-agent/config/plc_points.yaml) (connections, DB blocks, types, offset/bit) and [plc_snapshot_policy.yaml](backend/config/plc_snapshot_policy.yaml) (raw/latest retention selection). Explicitly import, preview and validate legacy configuration; local Rust saves drafts and activates complete revisions. Central publication/download is later work. SQLite commit and memory activation are distinct; recovery remains to be specified.

Facts can reuse `(sourceKey, factName)` identity. API/schema tasks must define source/Agent identity, stable sample ID or sequence, collection and receive times, quality, point-contract version and mapping version, together with batch atomicity, authorization, idempotency and version behavior.

Latest facts describe current state; they cannot prove every intervening change was consumed. Events, append-only business records and history need explicit separate contracts. Missing, bad-quality, stale and out-of-order values need policies so a stopped source's last value is not indefinitely treated as valid.

Local SQLite configuration is the near-term direction; a complete fact engine is not a prerequisite. Draft/active/previous is a proposed edit lifecycle, with its exact relationship to long-term current/previous stable slots still open. Agents hold no Backend/Redis storage credentials; a storage change cannot silently weaken receipt guarantees. Add bounded persistent buffers/outboxes, offline delivery and configuration snapshots according to field requirements. Configuration rollback must preserve runtime records, pending deliveries and consumption cursors.

## 8. Capability stages and transition gates

S0–S4 are capability milestones, not version numbers, dates or approval to implement. Each implementation needs its own scope and acceptance evidence.

| Stage | Goal | Dependency / entry condition | Checkable completion condition |
| --- | --- | --- | --- |
| S0 — Documentation baseline | This bilingual blueprint, current/target distinction, reuse and naming boundaries | Approved documentation scope | Paired content, paths and links checked; independent documentation Verification and Human Owner final acceptance |
| S1 — Contracts and one business pilot | Acquisition configuration, fact read/write, mapping/receipts and one PW business API | Identify target project and business owner | Sample identity, quality/time/version, permissions and idempotency fixed; APIs and explicit migrations verified in separately approved implementation tasks |
| S2 prerequisite — Agent engineering foundation | Original CA (CAF) relocation/freeze, DAA inheritance, filtered TSS-to-SMA and configuration/native-startup isolation | Can precede S1 API implementation; S1 contract gate remains | ARCH-AW-001 r1 owns engineering evidence, independent QA and final acceptance; shared UI/business-chain completion is not implied |
| S2 — Local configuration and limited chains | CAF material→DAA, TSS→SMA, SQLite, CU and facts API; new CA shared flow/simulated execution scoped separately | Freeze S1 contracts; implementations can then proceed in parallel | Applications build/run independently; verify S7 support/import/offsets, SQLite activation, facts→mapping→API and simulated CA handshake; verify Core permissions/recovery before separately approved field work |
| S3 — Field reliability and delivery | Configuration application/rollback, quality/staleness, resources/capacity, persistent buffering/recovery and maintenance | S2 chain and explicit field reliability requirements | Bounded storage, disconnect/restart, duplicates/order, failure recovery and logs verified; real PLC, long-running and deployment evidence separately authorized |
| S4 — Three-world hosting as needed | Central publication, AWB/Axum, PG/Redis, HA/SA, independent Rust Runtimes/unified AWC, PW .NET/FastEndpoints and AIW Python/FastAPI | Project demand and stable contracts; separate tasks | Unique data/business write ownership, module equivalence or approved differences, migration and rollback verified; not required for near-term delivery |

TSS currently rereads bound facts each cycle and sends even unchanged values. Failed or uncertain target requests are not automatically replayed. This is not reliable offline delivery. Append APIs need stable idempotency keys, transactional business writes and receipts, success acknowledgment, and explicit retry/manual-recovery boundaries. Per-Mapping leases do not arbitrate conflicts between different Mappings targeting the same business object.

Compare old/new results before switching by source/target. Disable the corresponding old Projection before enabling SMA production writes so each business target has one effective writer. Define cursor/sample identity, rollback and duplicate-consumption behavior. These are future switching gates, not authorization to change a field system now. Short smoke runs do not replace long-duration or field validation.

## 9. Deferred decisions and task alignment

- [ARCH-BE-003](plans/ARCH-BE-003-mapping-service-api-pilot/spec.md) needs its own revision for the target project, sample identity, idempotency and permissions. Begin with one business API, not the complete legacy Handler inventory.
- [CA-CONFIG-001](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) needs separate reassessment against local SQLite authority and later central publication. This roadmap does not modify or approve its implementation.
- [ARCH-BE-002](plans/ARCH-BE-002-energy-price-api/spec.md) is an independent reusable public capability, not a prerequisite of the sampling pilot.
- Defer AWB, headless Runtime extraction, unified AWC, database changes and PW technology migration until justified. PW/AW/AIW capabilities may advance independently; no all-at-once migration is required.
- Exact component versions/drivers, supported database combinations, deployment forms, directory decisions beyond this target and schedules belong to their implementation tasks. Automatic OpenAPI ingestion, full import/export and simulation can be scoped there as needed.

This documentation task creates no Agent directories, code, APIs, tables or deployment artifacts. Future stages remain planned. Runtime/build/site evidence and final acceptance are recorded in their owning task bundles, not inferred from this roadmap.
