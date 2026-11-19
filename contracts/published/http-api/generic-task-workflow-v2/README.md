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

The first performance for an existing plan copies the configured order snapshot once. When performance exists first, ordinary plan upsert can create the plan. Set `backfillExisting` to request eligible historical feedback. Values explicitly included in the plan request take precedence over one-time backfill.

## Access and migration

Integration operations use the project's trusted network boundary. The task flow has no frontend Bearer requirement or producer registration requirement. `producerId` is a label, and `fieldConfigVersion` is informational. Frontend read and write operations require login and the corresponding role grants. Configuration writes and deletes require admin.

The [v1 contract](../generic-task-workflow-v1/README.md) documents the archived workflow. Replace `syncValues` and `localValues` with the appropriate current `items`. The old dispatch claim/report, plan action and performance supplement POST paths return HTTP 410 with `task.endpoint_retired`. They are hidden from candidate OpenAPI. Verify all clients before switching. Historical values, dispatch attempts and action evidence are retained by the migration design.

Existing PLC Facts, equipment observation and business-time adoption keep their own target guards. The source recognizes `ae20b4d6f831`. Actual profiles and validated evidence must match the target. Database migration, service switch and adoption have separate approval gates.
