# Generic Plan and Performance HTTP API v2 candidate

[中文](README.zh-CN.md) · [OpenAPI](openapi.json) · [Synthetic requests](examples/requests.json)

This source candidate belongs to ARCH-TASK-001 r3. Confirm the deployed contract before using it on an environment. The examples run in order on a disposable fixture with configuration revision `1`; read the current revision and register suitable field identities in an adopted environment.

## Integration flow

1. Read current field definitions with `GET /api/v1/integration/task-field-configs?module=plan` or `module=performance`.
2. Submit a plan to `POST /api/v1/integration/plans/upsert`. A normalized task number is sufficient. Use `items` keyed by stable field names to send values.
3. Query plans with `GET /api/v1/integration/plans?productionStatus=new`. The list filters and paginates without claiming work. The caller owns field execution.
4. Submit actual production to `POST /api/v1/integration/performances/upsert` with the same task number. A plan may be absent. If present, the performance status and eligible submitted shared items update the plan in the same transaction.
5. Read either record from the corresponding `/by-task/{taskNo}` route. If the response says `task.commit_unknown`, reconcile with these GETs before deciding to submit again.

The fixed statuses are `new`, `running`, `completed`, and `error`. A partial update preserves omitted fields. Explicit `null` clears an allowed item; zero, false and the empty string are values. Automatic performance writes update the observation time from the report, clearing it when items were submitted without a time. Status-only calls with no observation time keep it. Business timestamps carry an offset and return in Shanghai time. Processing order determines the last write. A later accepted report can move a completed task back to running.

The first Performance record for an existing Plan copies enabled `order_snapshot` and `snapshot_auto` shared fields once. The `snapshot_auto` mode is available only to shared fields. The Performance integration POST accepts explicit values for this mode, including on the first request, and those values take precedence. With `syncEnabled`, only a submitted value is written back to the matching Plan. Inheriting the initial value alone does not write back the field. Plain `order_snapshot` remains read-only on Performance and cannot be written back. The `automated` mode does not inherit Plan values.

When Performance exists first, ordinary Plan upsert can create the Plan without recreating existing Performance snapshots. Set `backfillExisting` to request eligible historical feedback. Values explicitly included in the Plan request take precedence over one-time backfill.

## Field administration

The existing configuration GET, PUT, and single-delete operations remain compatible. GET returns definitions.
An administrator can submit multiple changed shared fields in one PUT with `module=shared` and the current `configRevision`.

`POST /api/v1/task-field-configs/batch-delete` accepts the current `configRevision` and 1–100 distinct shared field
identities (`scope=shared_sync`, `slotNo`, `name`). Only administrators can execute it. The server applies the existing
history and usage protection to every field under the configuration lock and commits the batch atomically.
Success returns `outcome=deleted`, `deleted` in request order, and `configVersion` and `configRevision`, each advanced once.

A stale revision or protected field returns 409, a missing identity returns 404, and invalid input returns 422.
An indexed detail such as `fields.1.name` identifies an item when available. A global history failure can refer to `fields`.
Those rejections leave the entire batch intact. After `503 task.commit_unknown` or a lost response, read the
current configuration to check identities and revision before deciding whether to submit again.
Check MES, SMA and other external references separately. GET does not provide deletion eligibility.

Plan and Performance local fields use the same PUT for single or batched changes with `module=plan` or
`module=performance`. The standalone local field pages use `POST /api/v1/task-field-configs/local/batch-delete`
for batch deletion. Only signed-in administrators may call it. Supply the module, current `configRevision`,
and 1–100 distinct identities. Every identity must have `scope=plan_local` for Plan or
`scope=performance_local` for Performance. Mixed scopes and shared identities are rejected.
The response, atomicity, failure and reconciliation rules above also apply. The existing shared deletion path
still accepts only shared identities. Both administration endpoints are outside the integration API.

## Access and migration

Integration operations use the project's trusted network boundary. The task flow has no frontend Bearer requirement or producer registration requirement. `producerId` is a label, and `fieldConfigVersion` is informational. Frontend read and write operations require login and the corresponding role grants. Configuration writes and deletes require admin.

The [v1 contract](../generic-task-workflow-v1/README.md) documents the archived workflow. Replace `syncValues` and `localValues` with the appropriate current `items`. The old dispatch claim/report, plan action and performance supplement POST paths return HTTP 410 with `task.endpoint_retired`. They are hidden from candidate OpenAPI. Verify all clients before switching. Historical values, dispatch attempts and action evidence are retained by the migration design.

Existing PLC Facts, equipment observation and business-time adoption keep their own target guards. The source recognizes `ae20b4d6f831`. Actual profiles and validated evidence must match the target. Database migration, service switch and adoption have separate approval gates.
