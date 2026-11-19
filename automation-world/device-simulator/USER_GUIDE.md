# Device Simulator user guide

[中文](USER_GUIDE.zh-CN.md) · [Project](README.md) · [Build instructions](BUILD.md) · [DS-001 Development record](plans/DS-001-policy-table-and-usability/tasks.md)

<a id="quick-start"></a>

## Quick operating flow

If DS is not running yet, run `pnpm tauri dev` from the project directory. Continue from an existing instance if you have one. Choose a route below, then [confirm layouts and names](#confirm-layout-and-names).

| What you have | Where to start |
| --- | --- |
| No source files | [Create an instance and points manually](#quick-manual) |
| TIA `.db` / `.udt` files | [Import points from DB / UDT files](#quick-tia) |
| A PLC JSON exported by DS or DAA | [Create an instance from PLC JSON](#quick-json) |

<a id="quick-manual"></a>

### 1. Create an instance and points manually

1. Under **Configuration → Instances → Create instance**, enter a name, listener IPv4, port, rack and slot. Adjust other connection settings as needed. For connections on the same computer, use `127.0.0.1` and an available port. Choose **Finish editing → Save draft** and check that the instance appears.
2. Under **DB points**, select the instance and choose **Add DB**. Enter the DB name, number and byte length. Choose **Add manual point**, enter the technical **Name**, type, byte address and **Manual address confirmation reason**. Also enter the bit for BOOL or the length for STRING. Add Chinese and English display names and a description as needed. Choose **Finish editing** for each point, then **Save draft**. [Manual entry example](#manual-create)

<a id="quick-tia"></a>

### 2. Import points from DB / UDT files

1. Create and save the instance as in step 1 above, or use an existing one. Select it under **DB points** and choose **Save draft** if there are pending edits. In **DB / UDT source import**, choose the `.db` and required `.udt` files. For a first import, leave **New source lineage** selected and choose **Scan declarations**.
2. Select the DB declarations, choose **Add DB** as the target and enter each DB number. Check the linked UDTs and supply any missing definitions. Choose **Preview import changes**, review the DB numbers and points, then **Confirm import and save draft**. Set any needed initial values separately in DS. [Multi-DB example](#multi-db-import)

<a id="quick-json"></a>

### 3. Create an instance from PLC JSON

1. Save any pending draft edits. Under **Configuration → Instances → Import PLC JSON → Choose PLC JSON**, select a single-PLC file. Import creates the instance and DBs directly.
2. Enter the DS loopback listener IP, an unused port, rack and slot, and check the listener acknowledgement. Choose **Preview all points**, review the DBs, points and TSAPs, then choose **Create draft instance**. The draft is saved with the DBs and points disabled. [JSON import details](#plc-json-import)

<a id="confirm-layout-and-names"></a>

### Confirm layouts and names

1. Select the instance under **DB points** and **confirm all DB layouts first**. For manual or JSON DBs, choose **Confirm complete manual layout**, enter the reason for your check, and choose **Preview**. For a standard DB/UDT layout, choose **Preview standard layout**. In either case, check the DB length, types and byte/bit addresses before choosing **Confirm**. If standard layout is unavailable, enter the verified addresses and reasons, save the draft, then confirm the manual layout. [Layout example and limits](#multi-db-import)
2. **Confirm names next.** For each DB, select points page by page, choose **Preview selected point names**, review each proposed technical name, then choose **Confirm**. The header selects the current page. Selections accumulate across pages, and switching DB clears them. For DB/UDT imports, cover every point, including disabled points. The JSON catalog shows the fixed names for the entire instance for review. Finish with **Save draft**.

### Save a version, then export or run

For export only, you can leave DBs and points disabled and start at step 2.

1. **Confirm settings for simulation.** Under **DB points**, enable the required DBs. For each point to simulate, choose **Edit → Enabled → Finish editing**, then save the draft. Under **Simulation and access policies**, check mode, initial values and permissions. To make changes, use **Edit policy → Finish editing**. Filter to the enabled DBs, select all their points (including disabled points), and choose **Save draft and confirm selected initial values/policies**.
2. **Save the version.** On **Instances**, choose **Save as version**, review the history cleanup list, then **Confirm save as version**.
3. **Continue for your goal.**
   - **Export.** Choose **Export PLC JSON**, select the version and instance, and edit the **JSON filename** if needed. Review and acknowledge the client target and TSAPs and any loaded-version difference shown. Choose **Preview all points** and review them, then choose **Choose output directory → Export valid files**. Look for **Written** on the instance row. [Export details](#plc-json-export)
   - **Run.** Under **Configuration versions and loading**, select the stopped instance and choose **Preview loading** in the intended row. Review and acknowledge the list, then choose **Load and remain stopped**. Choose **Workbench → Start** and check the loaded version and points under **Online values**. [Save, first load and start](#save-and-load)

If export validation fails, choose **Change selection** and check the reported item. For an unconfirmed layout or names, go back to **DB points**, confirm them, save a new version and select it. Saving a draft leaves the saved version and runtime configuration as they were. Selecting point rows applies the current action to them. Use the **Enabled** switch to enable them.

## 1. Preparation and separate actions

Use the declared toolchain in the [build instructions](BUILD.md). With dependencies already installed, start directly. If dependencies are missing, use the project's declared pnpm version and `pnpm install --frozen-lockfile`; do not change the lockfile. Normal use keeps the default data directory and requires no extra home-directory profile. From the repository root:

```sh
cd automation-world/device-simulator
pnpm tauri dev
```

If already in the `automation-world/device-simulator` project directory, run only `pnpm tauri dev`. `pnpm dev` serves the browser frontend without the desktop bridge and cannot complete saves, imports or controls.

**Default data and existing configuration.** Without `DS_PROFILE_DIR`, DS uses Tauri's application local-data directory. Check the actual configuration path on Logs and storage. The profile holds `device-simulator-v1/config.sqlite`; logs and the persistent WebKit store are managed with the corresponding profile. Normal reopening reuses this directory without clearing it. Only a new directory should be empty. An existing default directory may contain instances and saved history; reopening initializes its selected revision and remains stopped. Check Instances first: if `PLC_Test` already exists, inspect its endpoint and DB31/71/88, then continue from completed steps instead of creating a duplicate or overwriting other configuration. If tutorial names/numbers are used for something else, identify ownership before choosing example objects; do not delete data to force a fresh tutorial.

**Development and built applications do not automatically separate data.** Both use application identifier `com.aiis.aw.devicesimulator`. With no explicit profile override, the same user runs them against the same default directory and reuses its instances and revision history. `pnpm tauri build` itself neither clears the external SQLite database nor automatically embeds it into the program. A successful build does not create an empty data environment. Two programs cannot occupy the same profile simultaneously; normally close the instance holding its lock before switching.

**Optional: keep development data in the DS project.** Edit `.env` in `automation-world/device-simulator`. If the file is absent, copy `.env.example` there first. Set `DS_PROFILE_DIR` to the value below.

```dotenv
DS_PROFILE_DIR=.local/dev
```

Both `.local/dev` and `./.local/dev` resolve to `.local/dev` in the DS project directory containing `.env`, regardless of the terminal's working directory. Existing absolute paths still work. When both sources are blank, DS uses Tauri's default directory. After startup, check the configuration path on Logs and storage. This example uses `.local/dev/device-simulator-v1/config.sqlite` within the project.

A nonblank process `DS_PROFILE_DIR` takes precedence over the value in the project's `.env`. Relative process values use the same DS project directory. The file accepts simple `KEY=VALUE` entries with one layer of paired quotes. The first duplicate wins. Paths with `..` components, `~`, variables or existing symlinks are rejected. An unreadable `.env` or invalid path stops startup before DS opens the configuration database. This setup applies to source development.

An earlier terminal export of `DS_PROFILE_DIR` overrides .env; the Owner checks once and runs `unset DS_PROFILE_DIR` if appropriate. Subsequent startup is only `pnpm tauri dev`, reusing the same profile on reopen. Do not source the entire .env. The single profile key only selects the storage root. UI + SQLite own PLCs/points/policies, while Workbench owns explicit runtime actions. Save/load never auto-start; connected/running intent is not restored. Do not delete default data for a blank tutorial. The DAA-007 joint run reuses only the original Owner synthetic profile in the [joint guide](../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/tasks.md), without copying DEV databases.

For a pnpm store mismatch, compare `pnpm store path` with `node_modules/.modules.yaml`'s `storeDir`, then reinstall only this project's locked dependencies with the declared pnpm. Historical temporary stores are not product dependencies. If a port is occupied, identify its owner; do not kill unknown processes. For `profile_in_use`, normally close the owned instance holding the lock; do not remove the lock to seize it.

| Page | Purpose |
| --- | --- |
| Workbench | Actual states; start, pause/resume rules, stop and reset |
| Configuration → Instances | Create instances, check revisions and preview a stopped load |
| Configuration → DB points | DB/point structure, source import, complete layout and naming confirmation |
| Configuration → Simulation and access policies | Current draft table, single/bulk edits and parent inheritance |
| Online values | Actual loaded revision, addresses, types, values and ordinary/maintenance writes |
| Logs and storage | Errors, configuration path, bounded events and loss counters |

Five actions remain separate: **Finish editing** returns popup edits to the current editor; **Save draft** persists the same SQLite draft across normal reopen without adding a version; **Save as version** explicitly snapshots the entire workspace and deduplicates against the latest version; a row’s **Preview loading** and confirmation load only the target instance while stopped; **Start** opens its listener and advances rules. Import, address/name, initial/policy confirmations and Save draft and close update only the draft, without implicit version creation, loading or starting.

| What you see | Meaning and location |
| --- | --- |
| Current draft | Editable instances, DBs, points and policies in Configuration; Save draft persists it for further editing |
| Latest version | Most recently saved whole-workspace snapshot, such as v15; individual instances may still use older versions |
| Selected | The instance's persisted version, used to initialize it on reopening; inspect the version question mark |
| Actually loaded | Version currently installed in runtime memory; check Workbench, Online values and version usage |
| Retained for rollback | The prior selected version retained on a genuine switch; retention alone neither makes it active nor proves that its configuration passes validation |

Switching loads only the target instance. It does not restore a historical snapshot into the editing draft or switch other instances. Configuration displays the draft; Online values displays the actually loaded configuration, which may differ.

Hover or keyboard-focus the question mark beside a field for explanations of versions, update times, log times and online write operations. Confirmation-dialog risks and unknown-result warnings remain visible. Revision, online-value and log calendar times display Shanghai time to seconds, for example `2026-10-23 11:39:15`; original milliseconds are retained, without rounding up to the next second.

### 1.1 Column widths and viewing in every table

Tables across Workbench, Instances, configuration versions, DB points, policies, online values, connections, logs and naming/layout/import/load/bulk/version-cleanup previews use the same component. Existing filters, selection scopes and pagination remain.

1. For example, open **Configuration → DB points** and choose an existing PLC/DB. Move to the right edge of the Name header, then drag when the resize cursor appears. Releasing retains the width. Regular data columns have minimum widths; selection/action utility columns use fixed widths.
2. Long text is truncated to one line with hover details, without changing underlying values or input contents. Input controls, confirmation states and bulk before/after details may expand to fit. Wide tables scroll horizontally inside the table; long tables scroll vertically under a retained header. Actions stay fixed on the right on desktop; narrow table containers unfreeze the right side to avoid covering data, so scroll right to reach actions.
3. Paging, filtering, refreshing and leaving/reopening the same page retain widths. Switching Chinese/English uses the same stable fields. Different tables remember independently, even when fields have the same name. Follow each page's existing cross-page selection rules.
4. Every table has **Reset column widths** at the top right. It clears only this table's width preferences, retaining filters, selection, current page, edits and PLC configuration. It creates no candidate revision and changes no runtime values. Other tables retain their widths.
5. Widths use the current WebView's local `localStorage`, separate from DS business SQLite and configuration revisions. Reopening the same entry/profile restores them. Sharing across computers, different development/installed-app origins or different WebView data directories is not promised. Clearing application page data may remove preferences.
6. New columns use defaults. Removed fields, fixed utility columns or old widths below the new minimum fall back to defaults. If local-preference storage is unavailable, dragging/resetting still works in the current page but persistence across reopening is not guaranteed. Do not delete a business database to troubleshoot widths.

<a id="manual-create"></a>

## 2. Manual DB31: create, save, load and run

For the first run, follow2.1–2.6. Fixed-value and bulk examples in section4 are optional. Finish editing still requires Save draft; every enabled DB needs layout, name, initial-value and policy confirmations.

### 2.1 Create an instance

1. Page: **Configuration → Instances**. Inspect existing instances first. If `PLC_Test` is absent, click **Create instance**; otherwise check the fields below and continue to its DB steps without creating a duplicate.
2. Enter name `PLC_Test`, IPv4 loopback `127.0.0.1`, port `30102`, rack `0`, slot `1`, Calling TSAP decimal `256`, established limit `16`, handshake limit `4`. If another existing instance uses `127.0.0.1:30102`, preserve it unchanged and use `30103` for the new tutorial PLC_Test after checking that port is available. All subsequent tutorial endpoints refer to the port you actually entered. With no conflict, keep `30102`.
3. **Finish editing**, then **Save draft** at the top.
4. Expected: the instance row shows PLC_Test, your entered endpoint (`127.0.0.1:30102`, or `127.0.0.1:30103` when avoiding a conflict), `16/4` and a persisted draft; the version count is unchanged. An unconfigured-DB issue is addressed next; the workbench may have no runtime row before loading.
5. Recovery: a failed save retains the draft. Record the message; do not create duplicate instances. For an ETag conflict, preserve your intended edits before explicitly reloading.

### 2.2 Create the DB and three points

1. Page: **DB points**. Select PLC_Test. Click **Add DB** only if DB31 is absent. If the tutorial DB31 already exists, check its length and three points, then continue at the unfinished step instead of adding the same DB number again.
2. The new DB is selected automatically. In the form below, set name `Manual_Demo`, number `31`, length `8` bytes and keep it enabled. These fields edit the current draft directly; there is no separate DB-submit dialog.
3. Click **Add manual point** three times, complete each row below and **Finish editing**. Keep all points enabled. Names use ASCII; display names may differ. Each point needs its own reason.

For a manual or imported point, **Edit** can separately maintain a Chinese display name, an English display name and an optional description. The table shows the value for the top-bar language; an unset value stays blank. The technical name and the legacy display name marked “language unmarked” remain separate; nothing is translated or copied automatically. Each display name allows up to 256 UTF-8 bytes and the description 500 bytes. **Cancel** discards the dialog edits; **Finish editing** changes the current draft, and **Save draft** persists them. Switching language alone does not save or load a version. An older DS binary may reject a profile containing these new fields; retain a suitable stopped backup before any rollback.

If a draft-save reply is unknown, it may already have committed. Keep the window open, do not resubmit, and use **DB points → Read saved draft and versions** to compare current saved facts, point confirmations and local inputs; the top-bar refresh only reads runtime state. For a service save-receipt or commit unknown, a successful later read from the same store follows the submitted store job, but does not prove its outcome. If cleanup of a removed instance is unproven, protection remains. For a transport or runtime-task unknown, matching reads cannot prove that the original request and its effects have ended, so conflict writes remain paused. A known successful or unchanged save followed by a failed read is identified separately.

When the result is eligible for review and saved content differs, show the differences and record any local inputs you need before explicitly confirming **Reload draft**, which discards the local draft; the ETag is checked again. A preview-release unknown only means that its temporary token may still hold a reference, independently of the save. The close dialog identifies in-flight and unresolved facts and allows Cancel or an explicit choice to discard local records and attempt a normal close. Closing does not settle an unknown result; edits and records held only in memory may be lost. If continuing after a normal close, first establish that the old process has actually exited, its exclusive lock is released, and the reopened application uses the same profile identity; then manually compare current facts with inputs recorded earlier. If any proof or input is missing, the prior result remains unresolved. No automatic retry or restart is performed.

| Name | Type | Byte | Bit | Example manual reason |
| --- | --- | --- | --- | --- |
| `Run_Bool` | BOOL | `0` | `0` | `Synthetic DB31, map only DBX0.0` |
| `Setpoint_Int` | INT | `2` | Hidden | `Synthetic DB31, bytes 2 and 3` |
| `Temperature_Real` | REAL | `4` | Hidden | `Synthetic DB31, bytes 4 to 7` |

4. Check addresses `0.0` / `2` / `4` and length8, then **Save draft**. Edit/remove actions should have an 8px gap and wrap without overlap in a narrow window.
5. Recovery: correct missing names/reasons or invalid addresses before keeping. The last mapped byte is7, so length8 is required; do not leave the default length1. Unmapped gaps are not automatically writable points.

### 2.3 Complete manual layout, then names

1. With DB31 saved, click **Confirm complete manual layout**. Enter a whole-DB reason: `Synthetic DB31: BOOL0.0, INT bytes2-3, REAL bytes4-7, length8, no overlaps.`
2. **Preview**. Expected: target DB31/Manual_Demo, length8, whole-DB reason and three point type/address/manual-reason rows. There should be no empty naming table. Check all facts, then **Confirm**.
3. In the points table select its header checkbox for the three points → **Preview selected point names**. This preview should contain real naming rows and retain the three valid manual names. **Confirm**.
4. Recovery: **Cancel** a wrong preview, correct and save the points, then preview again. Never reuse an expired token/ETag. The DB-points header selects the current page only; selection can accumulate across pages and clears on DB/PLC changes. The policy-table header in section4 selects all filtered pages. Pending point confirmation refers to initial/policy confirmation, not proof that the layout is unconfirmed.

### 2.4 Set modes, initial values and permissions for three points

1. Page: **Simulation and access policies**. Select PLC_Test and filter Manual_Demo. Read-only columns show DB/point/type/address, effective mode, initial value, sole writer, rule summary and initial/policy confirmations. **Permissions / sources** opens property values and their default/instance/DB/region/point origins. This is the current draft preview, not loaded values or server confirmation.
2. Run_Bool → **Edit policy**. Choose **Toggle**, check the linked rule owner and all three write permissions disabled. Inherit client reads (default allow). Enable the initial override and normally type `false`; half-period `1500`, other generic parameters unchanged. Review before/after values → **Finish editing**.
3. Setpoint_Int → **Edit policy**. Choose **Hold**, then owner **UI**, ordinary UI writes **Allow**, client/maintenance writes **Deny**, client reads allowed. Enable initial override, type `7`, press Tab and check it remains7 → **Finish editing**.
4. Temperature_Real: choose **Ramp**, rule owner/all writes denied, client reads allowed, initial override `20.5`, minimum `0`, maximum `100`, period `10000`, phase `0`. Review → **Finish editing**.
5. Review the owner, write-permission and complete-rule links on every mode change. They belong to the editing copy; **Cancel** discards all of them. Numeric `0` and BOOL `false` are valid explicit values, distinct from inheritance.
6. Select only these three points → **Save draft and confirm selected initial values/policies**. It confirms selected points, not structural addresses or other DBs. Expected: initial values `false/7/20.5`, all initial/policy states confirmed; rules generate BOOL/REAL, while INT allows ordinary UI writes.
7. Recovery: correct invalid retained text or explicitly cancel. A failed save retains the draft and error. A value reverting after blur is a failure: report the type, exact text, blur action and values after keep/save. Do not inject paired input/change events to replace ordinary typing.

<a id="save-and-load"></a>

### 2.5 Save the draft, save a version and load it for the first time

1. After confirmations in2.3/2.4, click **Save draft**. Expect “Draft saved” without another history entry. Repeated clicks save the same draft. “Draft not saved as a version” means it has no corresponding immutable snapshot yet.
2. Check the issue list under **Configuration draft and versions**. Follow any instance/DB/point location to fix and confirm layouts, names, initial values or policies. Drafts can be saved incrementally; complete confirmations before preparing to run.
3. **Save as version** opens “Confirm version and cleanup.” Review the proposed sequence and exact history cleanup list → **Confirm save as version**. Expect a new row. **Cancel** creates no version and deletes no history. Identical content reports no duplicate and confirmation leaves the count unchanged.
4. If the target is running, use **Workbench → PLC_Test → Stop** and wait for stopped state and released connections. A never-loaded instance can proceed directly.
5. Open **Configuration → Instances → Configuration versions and loading**. Choose **PLC_Test** in the instance dropdown → **Preview loading** in the newly saved version row. Left-hand checkboxes are for batch deletion, not loading.
6. Review every name, action and reason in the stopped-load preview. A first load initializes the three points; an existing runtime image follows the preserve/initialize list. A remove row removes a point from the old runtime image, not a historical version. To restore all initials, select **Explicitly initialize all points** and review the recalculated list.
7. Select the acknowledgment that you reviewed preservation, initialization and removal and that loading stays stopped → **Load and remain stopped**. Expected: Selected and Actually loaded both identify the intended version, still stopped; first-load values are `false/7/20.5`.
8. The summary can show “Loaded vN · Matches latest”; a different latest version shows pending loading. Hover the question mark for complete identities. Saving drafts, saving versions and loading never start the instance; continue with2.6.

If preview does not open or validation blocks it, follow [version switching and error guidance](#switch-version). A successful save does not mean configuration has loaded.

### 2.6 Start, runtime writes and recovery

1. **Workbench** → PLC_Test **Start**. Expected: running at the displayed endpoint. Inspect logs on failure rather than creating duplicates.
2. **Online values** → PLC_Test. Check the short loaded revision, DB31, types and addresses; its question mark retains full identity. Observe several seconds: BOOL toggles about every1500ms, INT remains7, REAL ramps0–100 over10000ms and need not remain20.5 after start. Updated should display Shanghai calendar time to seconds; hover its header question mark for the definition. Initialization/loading, successful commits and reset record calendar time. Refreshes, rejected writes and unchanged rule values do not advance it. Visible refresh is at most about1Hz; multiple commits within one second may share the same displayed time, so also check point sequence. One frame cannot prove a toggle.
3. INT → **Ordinary write**, enter `12`, check old value, loaded revision, epoch and point sequence, acknowledge → **Confirm this write**. Expected:12 and an advancing sequence while configuration initial remains7. Rule points should not allow ordinary writes. Refresh an unknown receipt instead of automatically retrying.
   The Operations header question mark explains ordinary/maintenance writes. Ordinary writes record UI provenance and do not issue an S7-client request; this INT is configured for UI writes. One-time maintenance applies only to explicitly permitted hold points owned by a client or no owner. It changes the current value once, without changing the initial/owner or automatically reverting later; a client may overwrite it. This example does not require changing permissions to try maintenance. Rule ownership and stopped-state write restrictions remain.
4. **Pause rules** freezes rule time without surrendering ownership; **Resume rules** continues it. **Stop** releases listeners/connections and retains the in-process value12. While stopped, **Reset runtime values**, read the discard warning and confirm. Expected: stopped with `false/7/20.5`, never automatically started.
5. To try a continuous fixed value, use the [optional4.4 example](#fixed-example). The first three-point run does not require another mode change.
6. Normally close the native window. With dirty edits, choose according to intent: keep/save-and-close/discard/cancel. Reopen the same profile: selected revision initializes and stays stopped with zero connections; previous running intent or manually written12 is not restored. Save draft and close neither publishes nor loads a version. Do not force-kill or delete the database to test this.

<a id="version-management"></a>

### 2.7 Version retention and deletion

1. **Configuration → Instances → Configuration versions and loading** lists whole-workspace history. **Usage** names every instance reference. Latest, selected, actually loaded and active loading-preview references protect a version from selection/deletion. Stopping a PLC does not release its loaded configuration. There is no force-release action for these protections.
2. **Retained for rollback (confirm release to delete)** can be explicitly relinquished. A version with only rollback retention allows **Delete**. The dialog lists version numbers, saved times and every affected instance under “Instances relinquishing rollback retention.” Review the notice and select **I confirm relinquishing every listed instance's rollback retention and deleting these versions**, then **Delete listed versions**. Release and deletion commit together, without changing current selected/loaded versions, runtime values or running/stopped state. Any remaining usage protection still prevents deletion.
3. Unreferenced history uses the same confirmation without a rollback checkbox. **Cancel before submission** preserves the version count and rollback records. Successful deletion removes only listed versions, preserving current selected/loaded versions. Submission rechecks all references; if any item changed, the entire batch is rejected. Cancel, refresh and preview again. For an unknown receipt reread the facts instead of resubmitting; closing that notice cannot undo a submitted operation.
4. For a batch, select rows on the left. The header checkbox selects eligible rows on the **current page** only and excludes usage-protected rows. Review “N versions selected” → **Delete selected**, then check every version, count and rollback instance before confirming. Cancel before submission preserves versions/retention and clears checked rows; successful deletion removes only the listed versions. Paging, **Refresh list** and successful deletion also clear selection, without accumulation across pages. Single and batch deletion use the same rules; rollback-only rows are selectable but still require explicit release in the dialog.
5. Each instance retains one previous version for rollback. A genuine switch replaces that record with the original selection; it does not permanently retain every version ever used. When the same configuration is already selected and actually loaded, repeated confirmation does not reinstall or reset values and preserves rollback retention. To restore initial values, use **Reset runtime values** in Workbench. Do not reload merely to make a version deletable.
6. Cancelling a loading preview, changing its target or leaving its page releases that page's preview. Completing a load refreshes version facts. Entering Instances or using **Refresh list** rereads usage and removes expired preview occupancy without overwriting local draft edits. If deletion remains disabled, check the specific instance/reason rather than removing locks or editing SQL.
7. Explicit publication retains the latest5 plus older usage-protected and rollback-retained versions, so the total can exceed5. Automatic cleanup never relinquishes rollback retention for you. Its exact list appears in publication confirmation; cancelling before submission cancels cleanup, and unchanged publication creates/cleans nothing. The latest5 are a retention default, not a manual-deletion lock: manual deletion follows the rules above, while the newest version always remains protected.
8. Upgrade/startup, reopening and Save draft never automatically trim existing history. Sequence numbers increase without reuse: deleting v11 does not make a later save reuse v11. Source originals and current runtime values are not deleted with history. Do not alter joint-test points or manufacture revisions to test a limit.

### 2.8 Manual confirmation of this draft/version increment

This optional checklist is not a daily requirement; completed checks need not be repeated. Use the original joint-test profile, instances and points. These are instructions, not steps executed by the Agent. Cancellation paths can be checked first; actual deletion requires your explicit decision after reviewing the list.

1. Normally close DS and restart with `pnpm tauri dev` using the same profile. Check the original joint instance, newest sequence and total remain, with instances stopped. Review any unsaved-edit prompt rather than discarding it. Check **Save draft / Save as version / Configuration versions and loading / Refresh list / Delete selected**.
2. Without point changes, **Save draft** twice: the version count must not increase. Open **Save as version**, review, then cancel: the count remains. Identical content should report no duplicate. If the draft differs, record the proposed version and cleanup items; do not submit or manufacture changes just for this check.
3. Find rollback-only history (for example v12, according to actual usage), then **Delete**. Confirmation stays disabled before the release checkbox is selected. Review all listed instances, select the checkbox and **Cancel**: version and retention remain. Any additional usage protection should still block the row; report its reason first.
4. If two eligible histories exist, select them, check the count and use **Delete selected → Cancel**. Both versions and rollback records remain. Do not create history if two eligible versions do not exist. If you explicitly confirm actual deletion, only listed versions disappear; current selected/loaded versions and point configuration remain and sequence numbers are not reused.
5. On a stopped target, use a complete, valid version for **Preview loading → Cancel**, then check preview occupancy disappears and usage returns to its prior state. If an old version immediately reports configuration validation/pending confirmations, only validation rejection was observed, not successful preview cancellation. Do not repair history or manufacture versions just for this check. For repeated loading, use the same currently selected and actually loaded configuration: confirmation should preserve rollback retention, values and stopped state, without repeated switches.
6. Report the actual state/error at each step and wait for the next instruction from the DS chat. After this increment is manually confirmed, resume the separately approved DAA S7-to-SQLite joint run. This does not close Stage B; Stage C remains deferred.

<a id="switch-version"></a>

### 2.9 Switch versions, roll back and understand validation messages

**Switching between existing usable versions does not require recreating an instance, editing points or saving another version.** It uses an existing snapshot; the draft and runtime image remain separate.

1. Finish or cancel any editor. **Save draft** to retain intended changes. Switching to an existing version does not require **Save as version**.
2. In **Workbench**, find the target → **Stop** and wait for stopped state and released connections. Pause rules keeps the service running and does not replace Stop.
3. Open **Configuration → Instances → Configuration versions and loading**, select the target such as `PLC_Test`, find the intended sequence/saved time → **Preview loading**. “Select” in the upper instance table changes the viewed instance only; it does not load a version.
4. Review the stopped-load list using the table below. **Cancel** preserves the original selected/loaded versions and rollback retention.

| Operation | Preview and confirmed behavior |
| --- | --- |
| First load | Initialize values from the target version's DS initials |
| Load a version newer than the currently selected one | Preserve according to the compatibility list; changed points/DBs initialize. Selecting Explicitly initialize all points recalculates the list |
| Roll back to a version older than the currently selected one | Explicitly initialize all points is forced on and disabled; values rebuild from that version's initials and rule time resets |
| Same configuration already selected and actually loaded | Repeated confirmation does not reinstall or reset values, epoch or rollback retention. Use Workbench's Reset runtime values when a reset is intended |

5. Select the acknowledgment that preservation, initialization and removal were reviewed → **Load and remain stopped**.
6. Check usage: the target row shows Selected / Actually loaded for the instance. A genuine switch makes the original selection its rollback-retained version. A latest version retained for rollback is still protected by Latest and cannot be deleted. Hover version help for full identities.
7. After rollback, “Loaded vN, latest vN+1, pending loading” means the instance intentionally uses an older snapshot while a newer one exists; rollback did not fail. Workbench remains stopped. Check actual loaded configuration on Online values, then explicitly **Start** when ready. Clients must reconnect to the endpoint.

Versions store configuration and initial values, not historical runtime scenes. Rolling back does not recover past manual writes. In-process stopped values, switch-time retention and initialization after reopening are different operations. Switching forward again follows its new preview list and does not automatically recover values from before rollback.

| Message or observation | Meaning and next action |
| --- | --- |
| Complete configuration has validation issues or pending confirmations | Validation checks the selected historical snapshot. Layouts, names, initials, policies or configuration conflicts may block it; the generic message does not identify the exact point. Historical-load failures currently do not expand individual issues in the UI. Rejection happens before preview/loading, leaving the existing usable version. If repair is needed, correct/confirm the current draft and save a new version; current confirmations never rewrite an old snapshot |
| Online values unchanged after Save draft | The draft was not published/loaded, or the instance still uses another version. Follow2.5 to save a version, load while stopped and start |
| Delete disabled | Check every Usage reason. Latest, any instance's selected/loaded version and active previews protect history. Only rollback-only retention may be explicitly relinquished through2.7 |
| Preview expired or versions/references changed | Cancel → Refresh list → open and review the correct version's preview again |
| Unknown receipt | Submission may already have committed. Refresh version facts and inspect actual loaded/runtime state before any further action; do not confirm again. Closing the notice cannot undo a committed operation |

<a id="multi-db-import"></a>

## 3. Read-only multi-DB / UDT import

### 3.1 Files, declarations and bindings

1. Stop PLC_Test, wait for connections to release and save dirty edits. On **DB points**, select PLC_Test and choose these two repository files together in the multi-source import selector:
   `automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-multi-db/multi.db`
   and `types.udt` in the same directory. Do not edit either fixture.
2. Keep each as **New source lineage**, then **Scan declarations**. Select only Alpha and Beta; leave other DBs unselected. Required UDTs, including nested references, link automatically. No manual DB creation or select-all UDT step is needed. Identify origins by filename and batch identity.
3. Alpha: target **Add DB**, number `71`, no UDT required. Beta: target **Add DB**, number `88`, with **Measure from types.udt** already selected. Only duplicate UDT definitions require an explicit source choice; dependencies are resolved again after that choice. Missing definitions show the field path and type in the row; add definition files and scan again.
4. **Preview import changes**, check complete Alpha/Beta trees, target71/88, retained DB31 and ignored-initializer notice → **Confirm import and save draft**. It does not load or start.
5. Recovery: missing, unresolved duplicate or cyclic UDT references block preview and preserve existing configuration. Check existing DB numbers for conflicts. Import validation errors do not indicate an unavailable Rust IPC bridge. `:=`, `BEGIN` initializers and RETAIN are not DS initial values or runtime-retention contracts.

### 3.2 Layouts and names

1. Select Alpha DB71 → **Preview standard layout** → check the table below → **Confirm**. Repeat for Beta DB88.

| DB / length | Source path | Type | Address |
| --- | --- | --- | --- |
| DB71 / 4 | ready | BOOL | 0.0 |
| DB71 / 4 | count | INT | 2 |
| DB88 / 8 | unit.running | BOOL | 0.0 |
| DB88 / 8 | unit.value | REAL | 2 |
| DB88 / 8 | bytes[3] | BYTE | 6 |
| DB88 / 8 | bytes[4] | BYTE | 7 |

2. REAL is at byte2 in this standard word layout; it is not forced to a4-byte boundary or proof of real TIA addresses. In this example, Alpha and Beta each fit on one page; select all points on each DB's page → **Preview selected point names** → review → **Confirm**. If a DB spans pages, select and accumulate every page until all its points, including disabled points, are covered before preview and confirmation. Switching DB clears the selection, so repeat for each DB. Every exported point must have a valid technical name. Expected structured names: `DB71_ready_Bool`, `DB71_count_Int`, `DB88_unit_running_Bool`, `DB88_unit_value_Real`; index fallbacks `DB88_B6_Byte`, `DB88_B7_Byte`. Check the actual candidate.
3. Recovery: cancel any wrong address/type. Never infer complete layouts from selected leaves. A DB containing STRING requires manual addresses/reasons for its complete layout; this example does not extend into it.

### 3.3 DB inheritance, initial values and running

1. On policies, under **Parent instance / DB / region policies**, choose DB/Alpha → **Edit policy**: Hold, no owner, client reads Allow, other writes Deny, initial inherited. Keep. Repeat for Beta, then **Save draft**. Do not set a common DB numeric initial for mixed types; defaults are BOOL=false and numeric0.
2. Filter Alpha then Beta in the main table. **Permissions / sources** should show no point overrides, DB origins for parent settings and type defaults for initials. Each time select all filtered points and save/confirm initial/policy. Expect2 Alpha and4 Beta points confirmed. Source `count := 7` was ignored; current count0 is a DS default.
3. To set count10, edit only its initial, type/blur normally, keep and save/confirm that point. This is an explicit DS setting, not source initializer import. Restore its initial inheritance and confirm if you want count0 for this example.
4. Save draft → Save as version, review cleanup; then use Preview loading in the new row → check new DB initialization and original DB31 retention/initialization → acknowledge and load → explicitly start at Workbench. Online values should show the actual loaded revision and nine points across three DBs. Count matches your final confirmed DS value; retained DB31 hold values follow the load list.
5. Recovery: retain errors/drafts on save/load failure. Do not edit fixtures or run DAA. Import, native runtime and reopening still await Owner execution in this task.

## 4. Policy table, filters and three-state bulk editing

### 4.1 Selection scope

1. Select PLC_Test. No DB selection means all its DBs. Selecting DB31 and DB71 shows only those DBs; clearing restores all. Ordering uses DB number/stable DB identity, then address/stable point identity. Structure is read-only here; edit it on DB points.
2. The policy header selects **all filtered pages**. The N/total count persists through paging. Changing DB filter or PLC clears selection and closes old bulk editing. A changed draft baseline blocks stale submission and requires reopening. The eleven-point/ten-row case already has a DEV pure-function check; the manual check is optional. Use an existing set larger than10, or add only two INTs to these nine: create synthetic DB95 length4 with INTs at0 and2, save and clear DB filters for eleven total points. Select the header: expected N=11, still11 on page2. The extra DB need not be loaded; remove owned DB95 and save when finished.
3. Recovery: **Clear selection** before correcting scope. IDs, not row numbers/pages/names, locate changes. Empty results or zero selection cannot submit.

### 4.2 Do not change, set uniformly and restore inheritance

1. Filter Alpha, select both points → **Bulk edit policies**. Every property defaults to **Do not change**. Expected: no-op message, cannot keep, no revision. **Cancel** leaves the draft unchanged.
2. Reopen; only client reads → **Set uniformly** → **Deny**, all others unchanged. Review every before/after value and source. BOOLfalse and INT0 initials may differ; the read-only patch does not require matching initials. Acknowledge → **Finish editing**. Only selected point.clientRead=false should change; DB parent, unselected points, initials and other properties remain. Only relevant policy confirmations invalidate.
3. Saving is separate. **Save draft**, then check pending confirmations; select only Alpha's two points and save/confirm them. Unselected Beta must not be automatically confirmed.
4. Reopen and set only client reads to **Restore inheritance**. Preview should show the DB's Allow value and DB source. Acknowledge and keep. Only this point property is cleared; unrelated owner/initial overrides stay. Save/confirm if needed.
5. Recovery: cancel a wrong preview. Keeping updates only the draft. A failed save retains the repairable draft and error; do not claim persistence or loading.

### 4.3 Compatibility failures, linked changes and cancel

1. Filter DB31, select BOOL and INT → bulk edit, set mode uniformly to **Toggle**. Expected: INT's DB/point ID/type/reason is listed; the entire candidate is blocked, with no skipped INT or partially changed BOOL. Cancel should preserve both original policies.
2. With the same mixed selection, set only initial uniformly to `7`. BOOL is incompatible; expect the same complete failure. Cancel leaves the draft unchanged. Do not force one initial across incompatible types.
3. Select INT and REAL only. Uniform numeric fixed12 is possible: set mode to Fixed and fixed value12. Links show rule owner, all three writes denied and a complete fixed rule. Review every before/after property/source; initial7/20.5 remain. Acknowledge and keep updates both points once, without runtime writes.
4. To change only reads, leave mode/owner/rule unchanged. A separately set rule requires a complete kind and parameter set; never merge leftover parameters from a different mode. Restoring mode inheritance alone does not clear owner/rule. Explicitly restore the related fields you intend to inherit and resolve preview conflicts before keeping.
5. For acceptance, first cancel step3 to prove no mutation. If you actually keep and save it, restore each point per2.4, reconfirm and reload while stopped. Parent DB, other PLCs and unselected points must remain unchanged.

<a id="fixed-example"></a>

### 4.4 Optional continuous fixed-value example

1. In your tutorial configuration, Setpoint_Int → **Edit policy → Fixed**. Check rule ownership and all three write permissions denied; set fixed value `12`, leave DS initial `7` → **Finish editing**.
2. Select only that point → **Save draft and confirm selected initial values/policies**. Fixed12 and initialization7 are different fields; saving alone does not change runtime values.
3. To run it, follow2.5: **Save as version → Stop → Preview loading** in the new row → confirm loading → Workbench **Start**. The rule should continuously generate12. Existing-point retention follows the preview list, so loading need not first display7.
4. To continue the ordinary-write example, restore **Hold → UI → ordinary writes Allow**, client/maintenance writes Deny, initial7; finish editing, select the point and save/confirm it. Save a version, load while stopped and start when the restored configuration should take effect.

## 5. Other boundaries and recovery

- Property inheritance is instance→DB→non-overlapping region→point. Regions use bit ranges, must cover complete fields and cannot overlap or split INT/REAL. The parent section retains add/range-edit/policy-edit/remove controls. After parent/range edits check affected sources and confirmations. Type/system defaults are not fabricated confirmations.
- A hold point owned by the S7 client may allow an explicitly authorized one-time maintenance write. Check old value/version/epoch/sequence; it changes neither configured initial nor owner. Paused continuous rules keep ownership. Refresh/reopen an unknown receipt instead of retrying; subsequent writes can prevent readback from proving the original result.
- For source updates, select the original lineage on each file and existing DB target on each declaration, with explicit closure/number. Preview before confirming. Structure/address/type changes invalidate affected confirmations; old initials are candidates, not automatically converted values. Recheck layouts, names, initials and policies.
- Saved but unchanged online values: compare loaded/latest and explicitly load the correct revision while stopped. Draft saves and publication do not change served values; use the intended version row to preview loading.
- Limits of8 instances,32 DBs/instance,4096 leaves/instance and64KiB/DB are configuration bounds, not capacity evidence. Another synthetic instance can use30103 only after checking the port. UUIDs are independent; names are not identities. This guide requires no16-connection or performance matrix.
- Logs/storage: refresh, filter by an actual event name, clear to restore; pages hold50 bounded events. The Time header question mark explains Shanghai time and seconds display; legacy UTC is converted exactly once. New native logs retain millisecond `timestamp` values with `+08:00` after the development process rebuilds/restarts. The new online-value `updatedAt` also requires a rebuilt Rust process; missing fields are explicitly unavailable, without formatting counters as dates. Old logs without calendar time show "Calendar time not recorded"; dates are not inferred from file modification times or monotonic ns. Monotonic counters remain separate for ordering/durations. Existing SQLite UTC fields/revision history and original logs are retained, without migration or rewriting in this step. Degraded observability or dropped logs do not prove success. Preserve original databases and errors for corrupt/incompatible/read-only/full storage; do not alter schema, delete history or overwrite with an empty database.
- The limited S7 example uses port30102/rack0/slot1, Calling TSAP256 (0x0100), Called TSAP257 (0x0101). Compatible clients need custom-port support, complete fields and per-point permissions; use bit addressing for BOOL. This guide does not launch a client or joint integration.

## 6. Owner feedback

For feedback, locate2.3 layout;2.4 modes/initials/permissions;2.5 saving/first load;2.7 deletion;2.9 switching/rollback;3 multi-DB import;4 bulk editing/inheritance/fixed values. Report “page → button → exact input → blur/confirmation action → actual value/message → expected result.” [DS-001 tasks](plans/DS-001-policy-table-and-usability/tasks.md) retain prior Development facts.

The 2026-10-30 documentation update adds the quick flow and version operations, including use of the 2026-10-29 DIRECT draft/version increment. Instructions are not per-step execution or blanket acceptance records. The [2026-10-27 Owner decision](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001) retains its original scope; independent QA was explicitly waived for DS-001. The [r5 verification/acceptance](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5) retains original times, input identities and its acceptance chain. The [seven existing native images and sources](docs/user-guide/images/README.md) are historical, not current-interface evidence. Source .env/profile support belongs to the DAA-007 r2 delta, without retroactive DS QA/acceptance. DAA–DS reads to SQLite and phase conclusions retain their separate approval boundaries; Stage C remains deferred.

<a id="plc-json-export"></a>

## 7. Export a saved PLC revision and verify locally

For everyday export, start at step 3. Steps 1, 2, 6 and 7 are for optional local verification. Export produces one JSON per selected instance, using the chosen saved version. Each file includes disabled DBs and points, bilingual display names, descriptions and any available legacy name.

1. Verify the DS process and the actual database path under **Logs and storage**. For this authorized local exercise, DS's own database should be `automation-world/device-simulator/.local/dev/device-simulator-v1/config.sqlite`. Stop if the process, existing instances or target cannot be identified. Do not inspect or copy `.env` contents, or overwrite existing instances, drafts or history. DAA uses its own `.local/dev`; the applications do not share a database.
2. Create a uniquely identified test instance on an unused `127.0.0.1` port. Follow section 2 to create a manual DB with, for example, BOOL byte 0 bit 0, INT byte 2, REAL byte 4 and `STRING[10]` byte 8, with a DB length of at least 20. Add a disabled point in a separate DB if you want to check export completeness. Enter display names and a description, leaving one language blank if desired. Confirm every DB layout first, then verify and confirm point names. Choose **Save draft**.
   - **Export only.** Choose **Save as version** and continue to step 3.
   - **Run the instance.** Follow section 2 to confirm initial values and policies for every point in each enabled DB, including disabled points. Then choose **Save as version** and load the newly saved version while stopped. If you already saved an export version, save another version after confirming initial values and policies, then load that new version.
   - Record the version number, revision UUID and test instance UUID.
3. Open **Configuration → Instances → Export PLC JSON** and select the saved revision. Its list comes from that revision; check each instance's current selected and actually loaded revision. Select the synthetic instance, check the client IPv4, port, rack/slot and calling/called TSAPs, and explicitly confirm the target. Separately acknowledge a different or unverifiable loaded revision. `127.0.0.1` is for the same computer only. Non-default TSAPs are retained in the file and cannot currently be imported by DAA for execution.
4. Review **JSON filename** for each selected instance. If the saved instance name already ends in `.json` (case insensitive), DS uses that name unchanged. Otherwise, DS appends `.json`. You can edit each full filename. Use distinct names even when ignoring case, and correct any error shown next to the field. The filename only names the output file. Choose **Preview all points** and inspect every DB's size and enabled state and every point's program name, type, address, two display names, unmarked legacy name and description. Correct errors by DB/point UUID, save a revision and preview again.
5. Choose **Choose output directory** and select a directory owned by this exercise in the native dialog. Closing or canceling writes nothing. An existing target is marked as a conflict and kept intact. Choose **Change selection** to rename a file and preview again, or choose another folder. Choose **Export valid files**. The top of the dialog shows the overall outcome and counts. Check each instance's filename, status and SHA-256 for each successful write. With partial success, check the failed rows for their reasons. If any result is unknown, inspect the selected directory and file hash before starting another export.
6. On macOS, run `shasum -a 256 "actual-selected-directory/your-filename.json"`, replacing the example with the actual path, and compare it with the displayed hash. Retain the file hash, revision UUID, instance UUID and observations; give DAA **that same file** to create the synthetic PLC. Export does not connect a device or prove physical layout. Before joint testing, verify existing DAA objects will not automatically collect or report; connect only the authorized local DS and do not send real reports.
7. Once neither application needs the test, handle only objects and files clearly owned by this exercise: normally stop its instance and related connection, then remove test objects through the applications only where existing configuration is unaffected. Retain and record anything referenced by history, unsafe to delete or still needed as evidence. Never remove the entire `.local/dev`, pre-existing instances, saved revisions or history, or silently change other instance settings for cleanup.

<a id="plc-json-import"></a>

## 8. Create a simulator instance from PLC JSON

1. On **Instances**, select **Import PLC JSON** and choose a complete single-PLC file exported by DS or DAA. Review the original byte count and SHA-256, external origin, source version, client target, and every DB and point, including bilingual names, unlabelled legacy name, independent description, source path and source-enabled flags. An omitted DB flag is shown as not provided. The source client address is displayed only; DS does not listen on or connect to it.
2. Enter and confirm a separate simulator loopback IP, unused port, rack and slot, then check the client calling TSAP and server called TSAP. A non-default calling TSAP can be retained. Import is blocked when the called TSAP cannot be represented by the entered rack and slot. Resolve identity, source, endpoint or changed-file conflicts and select or preview again.
3. Confirmation creates only a persisted draft; the instance is stopped and DBs and points are disabled. Source-enabled flags do not grant simulator, write or runtime permission. DS retains the original JSON and local/external identity mappings as a catalog source; it does not generate DB/UDT files or a TIA tree. Follow the [quick flow](#confirm-layout-and-names) to confirm all DB layouts first, then review and confirm names. Continue with initial values and policies, saving a version, export or loading and startup as needed. Catalog technical names, types, addresses and point membership cannot be changed; display metadata, enablement and simulator policies remain editable through the existing workflow.
4. Exporting the saved revision preserves the external origin and DB/point identities; producer, revision digest and enabled flags describe the saved DS configuration. Selection, collision rejection, cancellation and unknown receipts follow section 7. Import/export does not prove physical PLC layout or field authorization; compatibility of old binaries with the optional catalog metadata has not been verified. A valid input is accepted even if a later complete DS export would exceed the 1 MiB file limit. That export is refused for the affected instance without truncation or overwrite; other valid selected instances can still be exported.
