# Plan and Performance User Guide

[中文](generic-plan-performance-guide.zh-CN.md)

This guide describes the current generic-task v2 pages and manual simulations. Check the deployed version, enabled field definitions, and OpenAPI document for the target environment before using it.

## 1. Workflow

```text
Administrator configures fields
       ↓
MES or a user creates a Plan with a taskNo
       ↓
CA/FF or another client queries new Plans and decides what to do
       ↓
SMA or another client submits Performance for the same taskNo
       ↓
The backend saves Performance and updates the Plan status and eligible shared values
```

“Simulate SMA” in this guide means manually sending an equivalent request in Swagger. It does not mean that SMA or a real PLC is connected. Plan and Performance provide task querying and storage; they do not determine whether CA/FF successfully sent anything to a PLC.

## 2. Pages and permissions

Sign in with access to the relevant pages. Administrators can manage field definitions. Creating and editing Plans also requires Plan management permission; editing manual Performance values depends on both account permission and field settings.

| Action | Entry | Scope |
| --- | --- | --- |
| View, create, or edit Plans | Plan Management → Plan List | Plan |
| View Performance and manual feedback | Performance Management → Performance List | Performance |
| Configure Plan local fields | Plan Management sidebar → Local Field Management | Plan only |
| Configure Performance local fields | Performance Management sidebar → Local Field Management | Performance only |
| Configure shared fields | Shared Field Management under either module | The same standalone page and configuration |

Each list has a title and actions, a filter area, and a table with pagination. Filter by task number, target, production status, or creation time. The starting creation time is inclusive; the ending time is exclusive. Scroll horizontally for wide tables and drag header boundaries to resize columns. Each table's reset action changes a local display preference only. The title help explains the business time zone and time meanings.

To create a Plan manually, select “New plan” on the Plan List, enter a task number and any editable values, and save. Open a row or select “Details” to inspect one record. Editing depends on the account, field scope, and edit switches. The Performance list has no manual creation button: the integration API creates or updates Performance. An authorized user may edit existing manual Performance fields and remarks.

## 3. Field groups and capacity

Each group has up to 100 slots, numbered 1–100.

| Group | Where values appear | Example |
| --- | --- | --- |
| Plan local | Plan only | Customer order number |
| Performance local | Performance only | Current speed |
| Shared | Plan and Performance | Product code, target length, completed length |

The shared **definition** is common. Plan and Performance store their own values for each task. Performance updates a same-number Plan value only when the shared field permits writeback and the submitted value satisfies the current rules. Both sidebar entries manage the same shared configuration.

The backend stores Plans and Performance in `plan_main` and `performance_main`, each with `local_values` and `sync_values` JSON value columns. Definitions such as field keys, bilingual labels, types, and switches are managed in `task_field_definitions` and related configuration-version records. Usage evidence supports deletion protection. Business APIs find and synchronize records by task number; users do not need to edit these database tables directly.

The stable field key, such as `productCode`, is used in API `items`. Chinese and English names are displayed in the UI. A key starts with a lowercase English letter, followed by English letters, digits, or underscores; it has at most 64 characters. System-reserved keys such as `taskNo`, `productionStatus`, and `items` cannot be used for custom fields. Shared and local keys belonging to the same module must not collide, even when a field is disabled or hidden. After saving, a field key, slot, type, or unit cannot be changed in place; create a new field for a different meaning.

Supported types are string (up to 255 Unicode characters), number (up to 10 integer digits and 4 fractional digits), and Boolean (`true` / `false`). The values `0`, `false`, and an empty string are not missing values.

Each module has at most one record per normalized `taskNo`. The server trims leading and trailing whitespace and converts letters to uppercase. A task number has 1–50 characters: English letters, digits, hyphens, underscores, and periods. Plan and Performance are stored separately; Performance can exist without a same-number Plan.

The fixed production statuses are `new`, `running`, `completed`, and `error`. Production status is not a custom field that can be disabled. Plan and Performance store their statuses separately; an integration report to Performance synchronizes its status to the same-number Plan.

## 4. Field settings

| Setting | Purpose |
| --- | --- |
| Stable field key, slot, type | Identify the field and constrain its value type; set when creating it. |
| Chinese name, English name, unit | Display labels and optional unit. |
| Enabled | Includes the field in current reads and permitted writes. Disabling does not delete historical values. |
| Nullable | Allows an explicit `null` to clear a stored value. An omitted field retains its value. |
| Plan editable | Allows a signed-in user with Plan editing permission to edit this field in the UI. It is not the MES integration switch. |
| Performance editable | Allows an authorized user to edit a manual-owned field. |
| Plan visible, Performance visible | Control whether the corresponding list shows this column; they do not grant read or write access. |
| Plan order, Performance order | Set dynamic column order for each list; the slot is used when no order is set. |
| Sync to Plan | Shared fields only. Eligible submitted Performance values update the same-number Plan according to current rules. |

Performance ownership determines the writer. **Order snapshot** copies an enabled shared value from an existing Plan when Performance is first created; later Plan changes do not automatically update an existing Performance snapshot. **Automatic** is submitted by the Performance integration API. **Manual** is entered by an authorized signed-in user. Order snapshots cannot enable writeback; Performance editing can be enabled only for manual ownership. Plan-local fields have no Performance ownership.

Shared Field Management supports search by stable key or either name, and filters by enabled state or Performance ownership. The table defaults to 20 rows per page. The header checkbox selects the current page. Changing pages preserves selections. A new search or filter reset clears them. “Edit” opens one field, while “Batch edit” opens the selected fields. The list and batch editor remember their own column widths on this device.

Add and edit dialogs keep a draft until Save. Cancel or close the dialog to discard it. The Plan Management and Performance Management sidebars open their respective standalone local field management pages with the same editing workflow. A revision conflict preserves the current draft for review.

“Field version” identifies the current field-definition version. “Configuration revision” detects concurrent saves or deletes; neither is edited by hand. After a revision conflict, record any unsaved changes if needed, cancel or leave, reload the latest configuration, and review it before editing again. The optional integration request `fieldConfigVersion` is informational and does not switch the current configuration.

## 5. Add and delete an unused test field

This example changes field configuration and performs reads only; it does not create or update tasks. If another program may write Plans or Performance during the test, coordinate the test window first.

1. As an administrator, open Shared Field Management under either module.
2. Select “Add field” and keep the automatically selected free slot.
3. Enter `tryScratch19` as the stable key (choose another unused key if needed), `临时测试` as the Chinese name, `Temporary test` as the English name, `string` as the type, and `manual` as Performance ownership.
4. Select Enabled, Plan visible, and Performance visible, then save. This example does not require writeback or edit switches.
5. Open both lists and scroll horizontally if needed. Both should have a “临时测试” column in Chinese. Existing tasks without a value show `—`. A read does not create usage evidence.
6. Return to Shared Field Management. Select “Delete” in the row and confirm. Deleting a saved field is submitted immediately after confirmation; another click on the bottom “Save” is not required. On success, the row disappears and its slot can be reused.
7. Select “Add field” to inspect the free slot, then cancel the new-field dialog.

The backend makes the final deletion decision. A task is considered to have used a field if a Plan or Performance was created or validly updated under a configuration containing that field, even if the field was empty or disabled, or the POST did not change a stored value. Historical dispatch batches can also count. Viewing or GET alone does not count. If the UI reports an existing reference or insufficient usage evidence, do not try to force deletion.

For multiple fields in the current group, select them, open “Batch delete”, and confirm the listed identities. A protected field prevents the whole batch from being deleted. If a save or deletion result is unknown, check the current configuration shown by the page before attempting another operation. Use “Local Field Management” in the Plan Management or Performance Management sidebar to open the corresponding local field page. Returning restores the list preferences and reloads the field configuration.

## 6. Disable, re-enable, and reuse slots

If a field was used, its usage cannot be verified, or it is temporarily unnecessary:

1. Open the appropriate field management entry and find the field.
2. Clear Enabled and save. Ordinary GET no longer returns the disabled field, and current writes, inheritance, and writeback no longer use it. Historical values remain stored.
3. To restore the same field, select Enabled and save. Its existing values become visible again.

Disabling does not free a slot and must not be used to give an old field a new meaning. Only a field that the backend confirms was unused and an administrator successfully deletes frees its slot. Before deleting, check external MES, SMA, and other mappings; this system cannot automatically discover every external client.

To try the “used fields cannot be deleted” case, create a separate test field and then create or update a test task before attempting deletion. Under current rules that field continues occupying its slot and can only be disabled. Do not perform this test with an existing business field.

## 7. Simulate MES, CA/FF, and Performance in Swagger

### 7.1 Preparation

For a local development environment, `http://127.0.0.1:8000/docs` is a common Swagger URL. Use the actual backend address in other environments. The `/api/v1/integration/...` task endpoints use the existing trusted-network contract and do not require the frontend login Bearer. Field management and manual UI edits still require login and appropriate permissions.

Choose an unused test task number. These tests create or update records in the target database; the ordinary task API does not provide a test-record deletion endpoint. Check the Plan and Performance by-task GET endpoints before starting. If either record exists, choose another number and use it consistently in subsequent requests.

The complete example assumes the following fields are configured and enabled. First query `GET /api/v1/integration/task-field-configs?module=plan` and `module=performance` and check keys, types, and ownership. Do not alter existing business fields just to run an example:

| Key | Group and type | Purpose |
| --- | --- | --- |
| `productCode` | Shared, string, order snapshot | Plan product code |
| `targetLength` | Shared, number, order snapshot | Plan target length |
| `customerOrderNo` | Plan local, string | Customer order number |
| `completedLength` | Shared, number, automatic, Sync to Plan enabled | Completed length from Performance |
| `currentSpeed` | Performance local, number, automatic | Performance speed |

### 7.2 Simulate MES creating task A

Expand `POST /api/v1/integration/plans/upsert` in Swagger, select “Try it out,” replace the request body with this JSON, and select “Execute”:

```json
{
  "taskNo": "GUIDE-A-001",
  "items": {
    "productCode": "PRODUCT-A",
    "targetLength": 120,
    "customerOrderNo": "MES-A-001"
  }
}
```

For a first creation with no same-number Performance and no submitted status, the Plan status is `new`. In the Swagger response body, `data.outcome: created` indicates creation; `updated` means an existing record changed, and `unchanged` means its business values did not change. An existing task number causes a partial update, which is why the number must be checked first.

Find the task in the Plan List or open its details to inspect the product code, target length, and customer order number. If a column is missing, check its Plan visibility and scroll horizontally.

### 7.3 Simulate CA/FF querying new Plans

For `GET /api/v1/integration/plans`, select “Try it out,” set `productionStatus` to `new`, execute, and look for A in `data.items`. Alternatively, query `GET /api/v1/integration/plans/by-task/{taskNo}`. This GET is a query, not a claim or PLC dispatch.

### 7.4 Simulate SMA or a third party reporting A

Submit the following to `POST /api/v1/integration/performances/upsert`:

```json
{
  "taskNo": "GUIDE-A-001",
  "items": {
    "completedLength": 45,
    "currentSpeed": 0
  }
}
```

A newly created Performance defaults to `running` when status is omitted. Inspect `data.performance` and `data.planSync` in the response body, then query both records again: `completedLength` is written back according to its switch; `currentSpeed` is Performance-local. Without an actual observation time, the last observed time displays `—`.

Find A in the Performance List: “Has Plan” should be yes. Open details to inspect its fields. The Plan displays the written-back completed length. Fields not configured as visible in the list can be inspected in details or in the `items` returned by the appropriate by-task GET.

### 7.5 Complete and partially update

The same endpoint accepts only the fields being changed. For example:

```json
{
  "taskNo": "GUIDE-A-001",
  "productionStatus": "completed"
}
```

After success, both Performance and its same-number Plan have status `completed`; stored length and speed remain. Repeated requests merge only submitted fields; an explicit `null` clears a field only when its definition permits it. The new-record default does not mean an existing Performance becomes `running` when an update omits status.

`producerId`, `targetKey`, `fieldConfigVersion`, `observationSeq`, and `observedAt` may be omitted under the contract. An unknown target is left blank, not automatically assigned. Supply `observedAt` with a timezone offset only when the actual observation time is known; do not substitute request time. If a request submits automatic values without an observation time, the last observed time becomes missing. The API outputs `+08:00`; pages display Shanghai time to seconds.

`createdAt` is record creation time. `updatedAt` changes only when that record actually changes. `lastObservedAt` is the observation time supplied with the latest collection report, not the screen refresh time. When a request submits only status and omits `observedAt`, the previous observation time is retained.

Updates follow the order successfully processed by the server. Neither `observationSeq` nor observation time provides deduplication or ordering: a delayed valid request may overwrite a newer value or status, and a valid `running` after `completed` also overwrites it. `task.commit_unknown` means the result is unknown; first query by task number, then decide whether to resend.

## 8. Report without a Plan and create one later

Performance can be saved without a same-number Plan; “Has plan” shows no. An authorized user with access to the Plan page can open “Supplement plan” from Performance details. Historical shared feedback is not copied by default. If needed, select the one-time backfill option for values whose shared fields permit writeback. Later valid Performance submissions still follow the current writeback switches.

To simulate this separately, first confirm both Plan and Performance have no `GUIDE-B-001`, then send to the Performance endpoint:

```json
{
  "taskNo": "GUIDE-B-001",
  "items": {"completedLength": 20, "currentSpeed": 0}
}
```

Query B's Performance. Expected: `hasPlan` is `false`, `planSync.outcome` is `skipped`, and the reason is `no_plan`. Then create a Plan from the Performance details or submit this separate request to the Plan endpoint to explicitly request one-time backfill:

```json
{
  "taskNo": "GUIDE-B-001",
  "backfillExisting": true
}
```

Query both sides again. B's Plan inherits the current Performance status and backfills `completedLength` when writeback is enabled. This request did not provide product code or target length; an existing Performance order snapshot is not automatically recreated when the Plan is added later. Run this example only where test task B may be retained.

## 9. Troubleshooting

- **A column is missing:** Check Enabled and the corresponding list visibility, refresh, and scroll horizontally.
- **A field cannot be deleted:** A task or historical dispatch may have used it, usage evidence may be incomplete, or a recognizable reference may remain. Follow the message, disable if appropriate, and check external mappings.
- **A request is rejected:** Check the key, Enabled, type, Performance ownership, and nullable switch. One invalid item rejects the entire request.
- **Conflict or unavailable:** A stale configuration revision, conflicting known target, or field in use can return `409`; invalid fields or types can return `422`. For `503 task.commit_unknown`, query the task before taking further action. Handle other unavailable errors according to the actual response.
- **Values differ between modules:** A shared definition does not make values automatically identical. Confirm the Performance request submitted the field, writeback is enabled, and the same-number Plan exists.
- **SMA cannot start delivery:** The current SMA configuration stage provides local configuration and pure preview; automatic delivery and real integration have separate tasks and acceptance boundaries.

For authoritative API details use the target environment's `/docs` and the [generic task v2 contract candidate](../contracts/published/http-api/generic-task-workflow-v2/README.md). The [field settings quick guide](../frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md) is available in Chinese. The [historical discussion](generic-task-workflow-discussion.md) can retain obsolete proposals and is not the current operation guide. Verification, final acceptance, and real-device integration have separate statuses in the [task record](../plans/ARCH-TASK-001-generic-plan-performance/checklist.md); this guide does not replace acceptance.
