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
| `common.log` / `settings` | `log_event`, `logger`; only `settings.BACKEND_MOCK_ENABLED` for new modules |
| Optional CRUD helpers | `common.async_crud_base:BaseService`, `common.sync_crud_base:SyncBaseCRUD`; existing get/list/create/update/delete and no-commit semantics |
| Optional Projection declarations | `projection.registry:ProjectionHandlerDescriptor`, `ProjectionHandlerInput`, `ProjectionHandlerGroupIdentity`, `ProjectionInvocationContext`; local synchronous declarations, no runner/runtime internals |

APIs use asynchronous sessions. Local Projection uses synchronous caller-owned sessions and its existing business/cursor/audit transaction. A module must not retain a global session, import engines or read private Settings. Third-party libraries must already exist in the approved consumer lock/environment.

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

The [fixture generator](../tests/module_admission_fixtures.py) builds C2 from immutable C0 `363b297bffe65e020108f5504766b4fb1ec3b381`, the five narrow contract patches and the r3 system manifest/import plus C0 monitor-manifest overlay. The public C0 placeholder snapshot policy supplies test configuration; monitor facts/routes/models remain C0. No real env is copied.

C2 retains fourteen tables and executes the original Core sanitization assertions. Its `core-files.json` freezes source and overlay SHA256. E only adds synthetic admission_probe (fifteen tables) and admission_summary (sixteen combined), their explicit fixture revisions and independent keys/errors/permissions; Core fingerprints must stay unchanged. F is this task's complete reintegration profile (58 tables), with a 42-table successor after the protected original sixteen. These counts belong to these fixtures, not to a permanent global module/table allowlist.

```bash
uv run python tests/module_admission_fixtures.py --profile C2 --output /private/tmp/module-C2
uv run python tests/module_admission_fixtures.py --profile E --summary --output /private/tmp/module-E
uv run python tests/module_admission_fixtures.py --profile F --output /private/tmp/module-F
```

Use public explicit process configuration, the approved project uv environment and the generator's DB-denying subprocess guard for A/no_db checks. Source composition, mocks, recorder/offline SQL and frontend fixtures do not prove real persistence. Separately approved disposable MySQL 8.4.6 migrations/API/constraint/rollback tests remain required before runtime adoption. Docker, database actions, deployment, real devices and publishing have separate gates.
