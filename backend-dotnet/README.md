# C# Plan learning slice

Chinese: [README.zh-CN.md](README.zh-CN.md). Task authority: [ARCH-BE-008 r1](../plans/ARCH-BE-008-csharp-backend-plan-slice/spec.md); Development evidence: [tasks](../plans/ARCH-BE-008-csharp-backend-plan-slice/tasks.md).

This independent ASP.NET Core API writes MySQL directly through EF Core. It is a first learning slice, with three Plan operations and no login. Python remains the existing delivery path. This does not replace the authenticated frontend/backend or authorize shared databases, deployment, MES or PLC access.

## Fixed toolchain

SDK **10.0.403**, net10.0, runtime **10.0.14**; FastEndpoints/OpenApi 8.3.0, FluentValidation 12.1.1, EF Core/Relational 10.0.14, Oracle MySql.EntityFrameworkCore 10.0.12 / MySql.Data 26.10.0, Serilog.AspNetCore 10.0.0 / File 7.0.0 / Compact 3.0.0. Tests use Test SDK 18.11.0, MSTest 4.5.2, MVC Testing 10.0.14. Direct versions are centralized in [Directory.Packages.props](Directory.Packages.props); both projects retain lock files. `global.json` disables roll-forward and preview. `NuGet.Config` clears inherited sources and uses only official nuget.org.

Use a new private `/private/tmp/arch-be008-sdk-<nonce>/` tool root, with SDK under `sdk/` and private `cli-home/`, `nuget-packages/`, `nuget-http-cache/`. Do not reuse another task's writable tools. The approved macOS arm64 archive is [official SDK10.0.403](https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.403/dotnet-sdk-10.0.403-osx-arm64.tar.gz); verify its SHA512 against [official release metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json) before extraction. Recorded digest and actual commands are in the root task. Do not change global PATH or user SDK configuration.

All project commands run from this directory:

```bash
cd /path/to/aiis-ics-arch/backend-dotnet
export BE008_TOOL_ROOT=/private/tmp/arch-be008-sdk-<nonce>
export BE008_DOTNET="$BE008_TOOL_ROOT/sdk/dotnet"
export DOTNET_CLI_HOME="$BE008_TOOL_ROOT/cli-home"
export NUGET_PACKAGES="$BE008_TOOL_ROOT/nuget-packages"
export NUGET_HTTP_CACHE_PATH="$BE008_TOOL_ROOT/nuget-http-cache"
export DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_CLI_TELEMETRY_OPTOUT=1
"$BE008_DOTNET" --version
"$BE008_DOTNET" restore AIIS.Backend.Api.csproj --configfile NuGet.Config --locked-mode
"$BE008_DOTNET" restore tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --configfile NuGet.Config --locked-mode
"$BE008_DOTNET" build AIIS.Backend.Api.csproj --no-restore
"$BE008_DOTNET" test tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --no-restore --filter 'TestCategory!=MySQL'
```

The initial approved restore uses `--use-lock-file`; subsequent restores use `--locked-mode`. The API root project explicitly excludes `tests/**` Compile/Content/None globs. Test dependencies never become API package references.

## Explicit startup and configuration

```bash
export Database__ConnectionString='Server=127.0.0.1;Port=<approved-port>;Database=<approved-database>;User ID=<insert-select-user>;Password=<private-password>'
"$BE008_DOTNET" run --project AIIS.Backend.Api.csproj --no-build
```

This is a placeholder example, not a ready credential. `.NET` does not load `.env`; use the intended process environment, never another project's real configuration. `Database:ConnectionString` defaults empty and fails startup validation. Connection and command timeouts are fixed to five seconds. Binding is loopback HTTP only, default `http://127.0.0.1:18108`; `BusinessTimeZone` is fixed `Asia/Shanghai`. The dedicated B database uses server/session `+08:00`; create verifies its time configuration and offset without changing it.

`Modules__Plan__Enabled=false` removes all three actual routes and their OpenAPI entries after restart. Static manifest assembly rejects duplicate IDs, missing dependencies and route collisions; registration opens no connection. FastEndpoints caches registration within a process, so the disabled test uses a separate real process, matching the restart contract. `/health` is liveness only; `/openapi/v1.json` is JSON documentation with no JWT scheme or UI. Only these two infrastructure routes and three business operations exist.

Logs are compact JSON Lines on stdout and `logs/backend-*.jsonl`, rolling at 10MiB with five retained files. `LoggingOptions__Directory` changes the explicit log directory. Host shutdown disposes/flushed sinks. Stable events include request ID, validation/transaction/commit outcomes and created plan ID, without DTO bodies, SQL parameters, passwords or connection strings. Reads are quiet except failures.

## API contract

| Method | Path | Result |
| --- | --- | --- |
| POST | `/api/v1/plans` | HTTP200 after confirmed commit, complete PlanOut |
| GET | `/api/v1/plans/{id}` | Positive Int32 ID; HTTP200 or404, invalid ID422 |
| GET | `/api/v1/plans` | `page=1`, `pageSize=20` (1–100), optional `coilNo`, `grade`, `materialStatus`, `status` |

Minimum create JSON:

```json
{"coilNo":"EXAMPLE-001","grade":"G","spec":"S","weight":"1.2300","thickness":"0.123","width":"10.00"}
```

The [approved field table](../plans/ARCH-BE-008-csharp-backend-plan-slice/spec.md#6-创建-dto-的精确合同) defines all 21 input fields, required/default/null rules and precision. JSON must be a flat, case-sensitive camelCase object. Unknown/duplicate keys, snake_case, invalid Unicode and wrong types fail422. Only `remark` permits null. Decimal accepts invariant number or decimal-string/exponent syntax and checks raw nonzero excess scale before parsing; extra trailing zeros are accepted. String length counts Unicode scalars. Priority accepts integer tokens only. Original coil text is preserved; Python-strip semantics apply only to validation.

Success is `{code,message:"success",data,timestamp}`. PlanOut has25 fields; Decimal is a string with fixed scale4/3/2, timestamps are database `DATETIME(0)` calendar values rendered `YYYY-MM-DDTHH:mm:ss+08:00`; GET does not refresh `updatedAt`. Response `timestamp` is Unix milliseconds. List data is `{items,total,page,pageSize,totalPages}`, ordered `created_at DESC,id DESC`. Empty/out-of-range pages retain true totals. Offset beyond Int32 fails422. `coilNo` uses parameterized LIKE contains, preserving `%`/`_` wildcard semantics; other filters use database collation equality. Empty filters are ignored, unknown query keys (including priority/sort) have no function.

Errors are `{code,message,data:null,errorCode,timestamp,errors?}` with stable keys:422 `plan_invalid_request`/`plan_invalid_coil_no`,409 `plan_coil_already_exists`,404 `plan_not_found`,503 `plan_database_unavailable`/`plan_write_outcome_unknown`,500 `plan_internal_error`; non-JSON415 uses `plan_invalid_request`. Unknown routes and unsupported methods retain ordinary404/405 semantics. No update/delete/XLSX/maintenance/authentication routes exist.

## Persistence and known differences

A scoped DbContext maps only the25-column `plans` table and its four named indexes. Service owns SaveChanges/commit/rollback; persistence helpers never commit. Create performs a parameterized canonical precheck, obtains one database CURRENT_TIMESTAMP and sets both time columns explicitly, then inserts and confirms commit. There are no EF migrations, startup DDL, schema creation or seeds. Alembic remains the existing schema authority; [plans.sql](tests/infra/plans.sql) is only the explicitly applied disposable test fixture.

Same raw coil concurrent requests produce one success/one conflict under `ix_plans_coil_no`. Sequential ASCII case/outer-space variants conflict through database lower(trim(...)). Non-ASCII casefold/collation equivalence is limited to the fixed test collation; different raw strings with equal canonical form are **not** guaranteed atomic uniqueness when the existing unique key does not cover them. No canonical column/index, advisory lock, new table or exactly-once claim is added. Cross-request pagination is not a snapshot.

Python differences are deliberate: no authentication; strict camelCase/unknown/null/type/storage validation; semantic HTTP statuses and unified errors; `success` message; Shanghai offset output; stable ID tie-breaker. Existing Python authentication, schema and UTC domains remain untouched. C# is not a drop-in wire replacement.

Commit acknowledgement loss is not simulated or claimed proven. A failure after commit was attempted returns `plan_write_outcome_unknown`, never blindly retries or promises rollback. A caller that loses the response must query the coil/content before creating another plan. Reliable idempotency/receipt handling is a future task.

## Disposable MySQL B

Only the explicitly approved ARCH-BE-008 resources may be used: Compose project `aiis-arch-be008`, container `aiis-arch-be008-mysql`, network `aiis-arch-be008-net`, volume `aiis-arch-be008-mysql-data`, official `mysql:8.4.6`, `127.0.0.1:13388`, database `arch_be008_plan`. All three resources carry task/runId labels. Unknown same-name resources or occupied ports stop preparation; no fallback address/database is chosen.

```bash
# Requires explicit B approval and the private fixed SDK exports above.
BE008_RUN_ROOT=$(mktemp -d /private/tmp/arch-be008-run-XXXXXXXX)
chmod 700 "$BE008_RUN_ROOT"
tests/scripts/run-mysql-tests.sh prepare --run-root "$BE008_RUN_ROOT"
tests/scripts/run-mysql-tests.sh test --run-root "$BE008_RUN_ROOT"
```

Bare script prints help only. `prepare` requires an empty owned0700 directory, generates0600 random credential files, verifies fixed resources/version/empty schema/timezone, applies only the plans fixture and grants app INSERT/SELECT. The separate fixture account manages synthetic tests in this one database. No root project env is read. `test` verifies the manifest and labels, executes real MySQL category tests and records independent SELECT output. Tests include explicit stop/start recovery; commands never use global prune/build or another project.

After evidence persistence, the coordinator verifies ownership and API/PID/port dependencies, then runs the explicit cleanup command with `BE008_COORDINATOR_CLEANUP_CONFIRMED=<manifest-runId>`; it verifies all three resources disappeared. Verification records evidence and hands cleanup to the coordinator. Fresh QA uses a new empty instance. SDK/cache/log/secret directories are inventoried and removed only when no later evidence/runtime dependency remains. See root tasks for real failures, resource ownership and current handoff; source/build/testing does not imply QA, final acceptance or production readiness.
