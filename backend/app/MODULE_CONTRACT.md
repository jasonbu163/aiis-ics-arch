# Backend module contract v1

[中文版本](MODULE_CONTRACT.zh-CN.md)

`aiis.backend-module/v1` is a Python source contract on the verified Core source and `uv.lock` versions. Copying a conforming `app/<module>/` package, declaring dependencies, applying its explicitly approved Alembic increment and restarting discovers its API, metadata and permission declarations. This never installs packages, creates tables, seeds data, grants accounts access or enables a writer. `user` and `control_agent` remain explicit security boundaries. Trusted Python imports can execute arbitrary code; preflight is a conformance check, not a sandbox.

## Public Python surface

The machine source is [module_contract.py](module_contract.py), including `CORE_CONTRACT`, `PUBLIC_SYMBOLS`, and the bounded legacy compatibility inventories. Tests resolve these symbols and check their existing signatures/fields/wire behavior. Private helpers and implementation modules are not extension points. Breaking changes require a new contract version and separate approval.

| Entry | Supported surface |
| --- | --- |
| `app.module_registry` | `ModuleManifest` |
| `database` | `Base`, `TimestampMixin`, `IntPk`, `Timestamp`, `UpdatedAt`; existing `get_db/get_db_session`, `get_sync_db/get_sync_db_context/create_sync_session` signatures and caller-owned sessions |
| `common.schema_base` | `ApiSchema`, `to_camel` |
| `common.response` | `SuccessResponse`, `StandardResponse`, `serialize_api_data`; existing envelope, aliases and pagination shapes |
| `common.exceptions` / `core.deps` | `BusinessException`; `get_current_user`, `get_current_active_admin`, `require_permissions` |
| Explicit user types | `app.user.models.user:User`, `app.user.schemas.user_out:UserResponse`; read-only types, no arbitrary user CRUD |
| `common.log` / `settings` | `log_event`, `logger`; `settings.BACKEND_MOCK_ENABLED` and the pure path helper `resolve_env_file` for new modules |
| Optional CRUD helpers | `common.async_crud_base:BaseService`, `common.sync_crud_base:SyncBaseCRUD`; existing get/list/create/update/delete and no-commit semantics |
| Optional Projection declarations | `projection.registry:ProjectionHandlerDescriptor`, `ProjectionHandlerInput`, `ProjectionHandlerGroupIdentity`, `ProjectionInvocationContext`; local synchronous declarations, no runner/runtime internals |

APIs use asynchronous sessions. Retained owner-local synchronous adapters use caller-owned sessions; Core no longer discovers or starts the old Projection runner. A module must not retain a global session, import engines or read private Settings. Third-party libraries must already exist in the approved consumer lock/environment.

`common.data_keys`, the fifteen restored global legacy errors, legacy lineage errors and the two existing schema-maintenance errors are frozen compatibility for the listed old owners. Their exact symbols/owners are enumerated in the machine inventory. Future modules put states/rules in their own domain/data_keys and use their own `StrEnum` with errors such as `sample.invalid_value`. Do not add business enums or errors to Core.

`BusinessException` accepts Core ErrorCode and module StrEnum with a nonempty string value. Bare strings and numeric Enum values are programming errors. Existing `error_code/code/message`, HTTP 200 business failures and `{code,message,data:null,errorCode}` remain unchanged. Existing legacy snake_case wire keys remain stable. Preflight follows the actual `BusinessException` error argument through literal imports, aliases, thin reexports, local literal assignments and actual factory arguments. Concrete enum annotations can supply otherwise unavailable provenance; annotations are not required when call sites identify the enum. Enum class names carry no error semantics: ordinary domain state StrEnums are not error declarations unless used as business errors. Error values used this way and manifest claims must match, use the owning namespace and avoid Core/other-owner collisions. Only error arguments whose concrete StrEnum cannot be located from their source/call sites fail with `error-source`; generic or absent parameter annotations alone do not cause rejection. An unresolved error is never silently ignored.

## Manifest declarations

Keep the seven packages `api/models/schemas/crud/services/mocks/seeds` and a thin package entrypoint. `manifest.py` uses literal keyword values, with no Service imports or runtime work:

```python
from app.module_registry import ModuleManifest
manifest = ModuleManifest(
    name="sample", enabled=True, order=100,
    core_contract="aiis.backend-module/v1",
    routers=("app.sample.api.routes:router",),
    models_package="app.sample.models",
    permissions=("sample-read", "sample-manage"),
    requires=(), model_requires=(),
    exports=("app.sample.models:Item",),
    error_codes=("sample.invalid_value",),
)
```

`requires` declares direct executable Service/handler/function, DTO and pure-key dependencies. The provider must exist, be compatible and enabled. Runtime cycles, self/duplicate dependencies and unknown contract versions fail with a chain. `order` remains `(order,name)` assembly priority and never becomes a dependency sort.

`model_requires` declares model-package/FK/relationship closure and direct references to a provider's public SQLAlchemy Model anywhere in API/CRUD/Service. Classification follows the original mapped class through thin reexports, not the consumer file's directory or a class name. The provider needs a manifest, model package and export, but its API may be disabled. It does not authorize provider API calls or writes. Explicitly declaring `requires` still requires an enabled provider. Bidirectional metadata relationships may form cycles; Python import cycles are not exempt. String relationships resolve the original qualified mapped class; SQLAlchemy module suffixes and bare class names must identify one class. Ambiguous same-name targets fail instead of inheriting the last scanned owner.

`exports` contains exact owner-local `module:attribute` strings. Cross-owner imports must use those public entrypoints; private CRUD/internal paths fail with file/line/symbol. Reexporting the same class preserves its table owner. Disabled runtime dependencies are inactive; static Service export existence is checked without eagerly importing that Service. Disabled metadata/model exports remain validated and loaded.

Missing manifest means opt-out. Malformed manifests and internal import errors fail. Empty/unknown/disabled role grant keys retain the existing WARNING + ignore behavior; declaring a permission never grants a user access. `user/control_agent` cannot be ordinary dependency names.

## Preflight and conflicts

```bash
uv run python -m app.module_preflight --help
uv run python -m app.module_preflight --project-root /private/tmp/public-backend --check-only
```

Bare invocation only prints help. Source checking imports no settings/App/database and performs no DDL or external connections. It inspects literal/relative imports, declared paths, Model/FK/relationships, public Core symbols and Settings access. Dynamic business imports/exec are unsupported and fail. Diagnostics contain stage/module/location/identifier/other owner, without secret configuration.

Normal discovery shares these checks. Before readiness, object checks reject duplicate router objects, model/table definitions, permissions, error values and final HTTP method/path identities, including explicit Core and framework routes. Parameter-name variants share one path shape. Different methods and static `/current` versus `/{id}` may coexist in the original order; no conflict is silently overwritten. Metadata loading is separate from migration application.

## Reproducible source profiles

The [fixture generator](../tests/module_admission_fixtures.py) builds historical C2 using the explicit preserved pre-retirement backend (`ARCH_ACQ002_HISTORICAL_BACKEND`) and immutable C0 `363b297bffe65e020108f5504766b4fb1ec3b381`, the five narrow contract patches and the r3 system manifest/import plus C0 monitor-manifest overlay. The public C0 placeholder snapshot policy supplies test configuration; monitor facts/routes/models remain C0. No real env is copied.

C2 retains fourteen tables and executes the original Core sanitization assertions. Its `core-files.json` freezes source and overlay SHA256. E only adds synthetic admission_probe (fifteen tables) and admission_summary (sixteen combined), their explicit fixture revisions and independent keys/errors/permissions; Core fingerprints must stay unchanged. F is this task's complete reintegration profile (58 tables), with a 42-table successor after the protected original sixteen. These counts belong to these fixtures, not to a permanent global module/table allowlist.

```bash
uv run python tests/module_admission_fixtures.py --profile C2 --output /private/tmp/module-C2
uv run python tests/module_admission_fixtures.py --profile E --summary --output /private/tmp/module-E
uv run python tests/module_admission_fixtures.py --profile F --output /private/tmp/module-F
```

Use public explicit process configuration, the approved project uv environment and the generator's DB-denying subprocess guard for A/no_db checks. Source composition, mocks, recorder/offline SQL and frontend fixtures do not prove real persistence. Separately approved disposable MySQL 8.4.6 migrations/API/constraint/rollback tests remain required before runtime adoption. Docker, database actions, deployment, real devices and publishing have separate gates.

## Module-local runtime configuration

`settings.resolve_env_file() -> Path` is the one additive public helper: it computes the backend-directory `.env` in source mode and the executable-directory `.env` in frozen mode (the existing Docker entry uses `/app/.env`). The function only computes a path; importing the settings module still performs its existing module-level Settings initialization. This does not expose additional private Settings fields.

Approved equipment scope belongs to its local BaseSettings and lazy dependency. Explicit parameters override process env, which overrides the selected dotenv; tests explicitly pass a synthetic file or `_env_file=None`. No cross-app cache or import-time config instance is introduced. This helper is not authorization, a device directory or a new configuration platform. Real env adoption/restart and MySQL verification remain separate operational gates.

BE003 callers of `generate_full_profile` explicitly pass `profile_name="BE003", expected_table_count=60, target_revision="e4f6a8b0c2d4"`; this new full-tree snapshot must not be labelled the frozen BE005 F/58 profile. C2/E 14/15/16 guarantees and original assertions remain unchanged.


## Anonymous integration primitives

A0 exports only the finite `common.integration` surface enumerated by `module_contract.PUBLIC_SYMBOLS`. Business fields, module StrEnum errors, SQL and lifecycle rules stay in their owners. The contract constants are `CONTRACT_VERSION="aiis.business-integration/v1"` and `DIGEST_PROFILE="bi-json/v1"`.

| Entry | Public signature / behavior |
| --- | --- |
| `envelope` | `IntegrationSchema`, `IntegrationEnvelope[DataT]`, `Identifier`, `SourceTime`, `BUSINESS_TIMEZONE`; strict camelCase, unknown fields forbidden, finite discriminated source references. |
| `envelope` | `identifier(value, maximum=128)`, `source_time(value)`, `shanghai_time(value)`, `fact_time(value)`, `validate_source_clock(value, database_now)`; Shanghai business milliseconds; reference fractional seconds retain necessary precision; DB clock must be explicitly injected. |
| `canonical` | `canonical_bytes(value) -> bytes`; exact JSON numbers, UTF-8 byte key ordering, no key rewriting. Numbers are bounded to 256 significant digits / absolute exponent 1000 to reject extreme inputs before formatting; DTOs further restrict actual storage domains. |
| `canonical` | `integration_digests(envelope, resource, parent_record_id=None) -> (requestDigest, businessDigest)`; data keys represent supplied fields; business object is `{resource,parentRecordId,data}`. Source refs sort by canonical bytes; absent non-process parent is null. FLOAT32 is encoded using the exact decimal value of the stored binary32, never default float repr. |
| `http` | `strict_json(body) -> dict`, `IntegrationPayloadError(status,suffix)`, `IntegrationRoute`, `MAX_BODY_BYTES=65536`, `MAX_DEPTH=12`; raw Decimal, duplicate-key rejection, bounded HTTP streaming and local sanitized status shell. Module Route subclass supplies owner/error enum; complete yield dependency exit precedes response. |
| `receipt` | `IntegrationReceipt`, `receipt_response(receipt, replay=False) -> bytes`; explicit stable fields and original outcome; replay changes only outcome to duplicate. Call only after durable commit and use an explicit JSON response; this pure function cannot prove database commit. |

Submodules' other imports/helpers are private. These primitives never import business tables or implement a dynamic handler/CRUD platform. Legacy `serialize_api_data` behavior stays unchanged. New endpoints must define typed data, presence/units/time, natural/delivery keys, both digests, atomic transaction boundaries, stable ACK/recovery, retention and authorization/admission before implementation. Breaking meaning changes require a new major contract. The normative examples and vectors live in [ARCH-BE-010](../../plans/ARCH-BE-010-anonymous-business-integration/spec.md) and [its Development record](../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md).

Each owner uses local `{EQUIPMENT,PERFORMANCE,MONITOR}_INTEGRATION_{ENABLED,EQUIPMENT_IDS_JSON,PRODUCER_IDS_JSON,STORAGE_PROFILE}` settings. Defaults are False / `[]` / `[]` / `unadopted`; device scopes contain at most 256 exact identifiers. Explicit construction overrides process env, then the selected dotenv, then defaults; each application lazily fixes its own configuration. A0 always rejects admitted requests with module `integration_not_ready` before DB access; a configuration string does not prove G-T. Model declarations without an approved migration are preparation only. No consumer may deploy this slice as an enabled business provider.

The separately named `BE010-A0` public fixture has 68 metadata tables and 84 public example assignments (the exact old 72-assignment prefixes plus twelve default-closed settings). `target_revision=null` and `schema_state=models_only_unadopted_no_migration` explicitly record that no new migration is implemented. Frozen C2/E/F/BE003/BE006 fixtures and assertions are unchanged; their fixed historical counts are not repurposed as this profile.


## Bounded business-time source surface (BE010 r2)

`common.integration.storage` exports exactly `StorageProbe`, `AdoptionContext`, `parse_adoption_manifest(value,module)`, `validate_adoption_probe(manifest,probe)`, `to_storage_time(value,basis)`, and `to_legacy_time(value,basis)`. All are pure: no settings, file, SQL, Session or target access. Owners export only `integration_storage:BUSINESS_TIME_COLUMN_PROFILE` and `crud.sync_integration:probe_storage(db)` through their own manifests for the read-only maintenance tool. Async probes stay owner-private; each probe uses its passed session and fixed UUID/schema/revision/UTC clock reads, without creating/committing sessions. Revision reads use a shared current-read lock.

`IntegrationSuccess[ReceiptT]` supplies the typed code/message/data envelope. Owner receipt types, finite HTTP error models and eight request schemas remain local. A new module selects its own data and state rules; it need not copy these eight resources or the fixed time-column profile.

The historical A0 fixture remains named `BE010-A0` (68 metadata/84 assignments/models-only); its configuration/schema surface is reconstructed without BE009/new migrations. Current source is `BE010-r2-A`: 75 application tables after the chained 71→75 successors and 91 assignments (69 earlier baseline +3 BE006 +12 A0 +4 BE009 +3 adoption paths). `source_ready_unadopted` is a source state; actual target adoption, schema migration, database/Docker/B and Owner acceptance remain separate gates.
