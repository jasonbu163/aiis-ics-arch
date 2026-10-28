# Device Simulator user guide

[中文](USER_GUIDE.zh-CN.md) · [Project](README.md) · [Build instructions](BUILD.md) · [DS-001 Development record](plans/DS-001-policy-table-and-usability/tasks.md)

This text guide describes the current DS version accepted by Human Owner on 2026-10-27 (Asia/Shanghai); see the [DS-001 acceptance](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001). It remains an operating guide with expected results, not a per-step execution record. Development compilation, pure-function/static checks and Owner manual acceptance are separate facts; independent QA was explicitly waived for DS-001. Record your actual revision and state, and report the point, input, action and message when something differs.

Create manual DB31 first, then import Alpha/Beta/Measure from read-only examples. DB numbers, names and ports are editable synthetic examples. DS runs independently of DAA, SMA and Backend. DAA–DS reads into SQLite need separate approval; Stage C remains deferred. This guide needs no screenshots. The [seven existing native images and sources](docs/user-guide/images/README.md) remain historical material; they do not prove the new interface or typing behavior. Source .env/profile startup support is a new DAA-007 r2 delta awaiting that task's independent verification; it is not part of the earlier DS QA or acceptance.

## 1. Preparation and separate actions

Use the declared toolchain in the [build instructions](BUILD.md). With dependencies already installed, start directly. If dependencies are missing, use the project's declared pnpm version and `pnpm install --frozen-lockfile`; do not change the lockfile. Normal use keeps the default data directory and requires no extra home-directory profile. From the repository root:

```sh
cd automation-world/device-simulator
pnpm tauri dev
```

If already in the `automation-world/device-simulator` project directory, run only `pnpm tauri dev`. `pnpm dev` serves the browser frontend without the desktop bridge and cannot complete saves, imports or controls.

**Default data and existing configuration.** Without `DS_PROFILE_DIR`, DS uses Tauri's application local-data directory. Check the actual configuration path on Logs and storage. The profile holds `device-simulator-v1/config.sqlite`; logs and the persistent WebKit store are managed with the corresponding profile. Normal reopening reuses this directory without clearing it. Only a new directory should be empty. An existing default directory may contain instances and saved history; reopening initializes its selected revision and remains stopped. Check Instances first: if `PLC_Test` already exists, inspect its endpoint and DB31/71/88, then continue from completed steps instead of creating a duplicate or overwriting other configuration. If tutorial names/numbers are used for something else, identify ownership before choosing example objects; do not delete data to force a fresh tutorial.

**Development and built applications do not automatically separate data.** Both use application identifier `com.aiis.aw.devicesimulator`. With no explicit profile override, the same user runs them against the same default directory and reuses its instances and revision history. `pnpm tauri build` itself neither clears the external SQLite database nor automatically embeds it into the program. A successful build does not create an empty data environment. Two programs cannot occupy the same profile simultaneously; normally close the instance holding its lock before switching.

**Optional: configure the source-development profile once.** In this project root, manually copy `.env.example` to `.env` only if absent; review an existing file and edit your own active key. Optionally set `DS_PROFILE_DIR` to an absolute directory you own; blank uses the original default. Nonblank process > own .env nonblank value > default; first duplicate wins. Only simple KEY=VALUE with one paired quote layer is parsed. No `~`, `$VAR`/`${VAR}` expansion, shell execution or parent/other-app search occurs. Relative paths, parent traversal, symlinks or unreadable/non-UTF8 .env fail before lock/database/logs, without fallback or a replacement database. Installed-package .env discovery/distribution is outside this contract.

An earlier terminal export of `DS_PROFILE_DIR` overrides .env; the Owner checks once and runs `unset DS_PROFILE_DIR` if appropriate. Subsequent startup is only `pnpm tauri dev`, reusing the same profile on reopen. Do not source the entire .env. The single profile key only selects the storage root. UI + SQLite own PLCs/points/policies, while Workbench owns explicit runtime actions. Save/load never auto-start; connected/running intent is not restored. Do not delete default data for a blank tutorial. The DAA-007 joint run reuses only the original Owner synthetic profile in the [joint guide](../data-acquisition-agent/JOINT_TEST_GUIDE.md), without copying DEV databases.

For a pnpm store mismatch, compare `pnpm store path` with `node_modules/.modules.yaml`'s `storeDir`, then reinstall only this project's locked dependencies with the declared pnpm. Historical temporary stores are not product dependencies. If a port is occupied, identify its owner; do not kill unknown processes. For `profile_in_use`, normally close the owned instance holding the lock; do not remove the lock to seize it.

| Page | Purpose |
| --- | --- |
| Workbench | Actual states; start, pause/resume rules, stop and reset |
| Configuration → Instances | Create instances, check revisions and preview a stopped load |
| Configuration → DB points | DB/point structure, source import, complete layout and naming confirmation |
| Configuration → Simulation and access policies | Current draft table, single/bulk edits and parent inheritance |
| Online values | Actual loaded revision, addresses, types, values and ordinary/maintenance writes |
| Logs and storage | Errors, configuration path, bounded events and loss counters |

**Keep changes** changes only the local draft. **Save candidate** saves an immutable revision. **Load and remain stopped** replaces the in-memory revision. **Start** opens the listener and advances rules. Bulk editing, saving and initial/policy confirmation do not write runtime values, load or start automatically.

Hover or keyboard-focus the question mark beside a field for explanations of versions, update times, log times and online write operations. Confirmation-dialog risks and unknown-result warnings remain visible. Revision, online-value and log calendar times display Shanghai time to seconds, for example `2026-10-23 11:39:15`; original milliseconds are retained, without rounding up to the next second.

### 1.1 Column widths and viewing in every table

All 13 tables across Workbench, Instances, DB points, policies, online values, connections, logs and naming/layout/import/load/bulk previews use the same component. Existing filters, selection scopes and pagination remain.

1. For example, open **Configuration → DB points** and choose an existing PLC/DB. Move to the right edge of the Name header, then drag when the resize cursor appears. Releasing retains the width. Regular data columns have minimum widths; selection/action utility columns use fixed widths.
2. Long text is truncated to one line with hover details, without changing underlying values or input contents. Input controls, confirmation states and bulk before/after details may expand to fit. Wide tables scroll horizontally inside the table; long tables scroll vertically under a retained header. Actions stay fixed on the right on desktop; narrow table containers unfreeze the right side to avoid covering data, so scroll right to reach actions.
3. Paging, filtering, refreshing and leaving/reopening the same page retain widths. Switching Chinese/English uses the same stable fields. Different tables remember independently, even when fields have the same name. Follow each page's existing cross-page selection rules.
4. Every table has **Reset column widths** at the top right. It clears only this table's width preferences, retaining filters, selection, current page, edits and PLC configuration. It creates no candidate revision and changes no runtime values. Other tables retain their widths.
5. Widths use the current WebView's local `localStorage`, separate from DS business SQLite and configuration revisions. Reopening the same entry/profile restores them. Sharing across computers, different development/installed-app origins or different WebView data directories is not promised. Clearing application page data may remove preferences.
6. New columns use defaults. Removed fields, fixed utility columns or old widths below the new minimum fall back to defaults. If local-preference storage is unavailable, dragging/resetting still works in the current page but persistence across reopening is not guaranteed. Do not delete a business database to troubleshoot widths.

## 2. Manual DB31: structure, confirmation and ordinary typing

### 2.1 Create an instance

1. Page: **Configuration → Instances**. Inspect existing instances first. If `PLC_Test` is absent, click **Create instance**; otherwise check the fields below and continue to its DB steps without creating a duplicate.
2. Enter name `PLC_Test`, IPv4 loopback `127.0.0.1`, port `30102`, rack `0`, slot `1`, Calling TSAP decimal `256`, established limit `16`, handshake limit `4`. If another existing instance uses `127.0.0.1:30102`, preserve it unchanged and use `30103` for the new tutorial PLC_Test after checking that port is available. All subsequent tutorial endpoints refer to the port you actually entered. With no conflict, keep `30102`.
3. **Keep changes**, then **Save candidate** at the top.
4. Expected: the instance row shows PLC_Test, your entered endpoint (`127.0.0.1:30102`, or `127.0.0.1:30103` when avoiding a conflict), `16/4` and a saved revision. An unconfigured-DB issue is addressed next; the workbench may have no runtime row before loading.
5. Recovery: a failed save retains the draft. Record the message; do not create duplicate instances. For an ETag conflict, preserve your intended edits before explicitly reloading.

### 2.2 Create the DB and three points

1. Page: **DB points**. Select PLC_Test. Click **Add DB** only if DB31 is absent. If the tutorial DB31 already exists, check its length and three points, then continue at the unfinished step instead of adding the same DB number again.
2. Name `Manual_Demo`, DB number `31`, DB length `8` bytes, enabled.
3. Click **Add manual point** three times, complete each row below and **Keep changes**. Keep all points enabled. Names use ASCII; display names may differ. Each point needs its own reason.

| Name | Type | Byte | Bit | Example manual reason |
| --- | --- | --- | --- | --- |
| `Run_Bool` | BOOL | `0` | `0` | `Synthetic DB31, map only DBX0.0` |
| `Setpoint_Int` | INT | `2` | Hidden | `Synthetic DB31, bytes 2 and 3` |
| `Temperature_Real` | REAL | `4` | Hidden | `Synthetic DB31, bytes 4 to 7` |

4. Check addresses `0.0` / `2` / `4` and length8, then **Save candidate**. Edit/remove actions should have an 8px gap and wrap without overlap in a narrow window.
5. Recovery: correct missing names/reasons or invalid addresses before keeping. The last mapped byte is7, so length8 is required; do not leave the default length1. Unmapped gaps are not automatically writable points.

### 2.3 Complete manual layout, then names

1. With DB31 saved, click **Confirm complete manual layout**. Enter a whole-DB reason: `Synthetic DB31: BOOL0.0, INT bytes2-3, REAL bytes4-7, length8, no overlaps.`
2. **Preview**. Expected: target DB31/Manual_Demo, length8, whole-DB reason and three point type/address/manual-reason rows. There should be no empty naming table. Check all facts, then **Confirm**.
3. In the points table select its header checkbox for the three points → **Preview selected point names**. This preview should contain real naming rows and retain the three valid manual names. **Confirm**.
4. Recovery: **Cancel** a wrong preview, correct and save the points, then preview again. Never reuse an expired token/ETag. The DB-points header selects the current page only; selection can accumulate across pages and clears on DB/PLC changes. The policy-table header in section4 selects all filtered pages. Pending point confirmation refers to initial/policy confirmation, not proof that the layout is unconfirmed.

### 2.4 Single-point policies, nonzero input and focus changes

1. Page: **Simulation and access policies**. Select PLC_Test and filter Manual_Demo. Read-only columns show DB/point/type/address, effective mode, initial value, sole writer, rule summary and initial/policy confirmations. **Permissions / sources** opens property values and their default/instance/DB/region/point origins. This is the current draft preview, not loaded values or server confirmation.
2. Run_Bool → **Edit policy**. Choose **Toggle**, check the linked rule owner and all three write permissions disabled. Inherit client reads (default allow). Enable the initial override and normally type `false`; half-period `1500`, other generic parameters unchanged. Review before/after values → **Keep changes**.
3. Setpoint_Int → **Edit policy**. Choose **Hold**, then owner **UI**, ordinary UI writes **Allow**, client/maintenance writes **Deny**. Enable initial override and normally type `7`, press Tab and click another control. Expected:7 remains. Keep and reopen. Enter `-`, empty text or `abc`: text should remain with an error and keeping blocked; the top save is disabled while editing. Correct to `-7`, keep, then restore `7`.
4. Temperature_Real: choose **Ramp**, rule owner/all writes denied, initial override `20.5`, minimum `0`, maximum `100`, period `10000`, phase `0`. Type normally, delete/refill, Tab and mouse-blur; check retention, then keep.
5. Review the owner, write-permission and complete-rule links on every mode change. They belong to the editing copy; **Cancel** discards all of them. Numeric `0` and BOOL `false` are valid explicit values, distinct from inheritance.
6. Select only these three points → **Save and confirm selected initial values / policies**. It confirms only selected points, not structural addresses or other DBs. Reopen each editor and check `false/7/20.5`, then cancel. Draft values and confirmation statuses should agree.
7. Recovery: correct invalid retained text or explicitly cancel. A failed save retains the draft and error. A value reverting after blur is a failure: report the type, exact text, blur action and values after keep/save. Do not inject paired input/change events to replace ordinary typing.

### 2.5 fixed12 and saved/selected/loaded revisions

1. Setpoint_Int → **Edit policy**, choose **Fixed**. Check rule owner and all three writes disabled. Normally type fixed value `12`, Tab, mouse-blur and delete/refill. Expected: text remains. Leave initial7 unchanged.
2. Review and keep, select **only this point**, then save/confirm its initial/policy. Reopen and check fixed12 and initial7, then cancel. Fixed12 and the DS initialization value7 are separate fields.
3. Restore the ordinary-write example: choose **Hold**, then owner UI, ordinary UI writes Allow, other writes Deny, initial7. Keep, select only this point and save/confirm.
4. Page **Instances**, select PLC_Test. The configuration bar and Workbench show one loaded version when aligned, such as “Loaded v12 · Matches latest”; a new candidate shows “Loaded v12 · Latest v13 · Pending load”. Use your actual sequences. Hover the version question mark to check latest saved, instance selected and loaded-in-memory identities, including full UUIDs. The question mark beside the lower Version field explains save/load and timezone. Options look like `v12 · 2026-10-23 11:39:15`, without milliseconds; sequences distinguish saves within the same second. An older version missing from the current list uses `#short-ID` in summaries, retaining its full identity in help. Check the revision for the next load preview: without a manual historical choice it follows latest; explicit old choices survive later saves and show a warning. **Choose latest saved revision** restores following latest.
5. Before **Preview load and retention**, check no dirty edits and that the pending revision is the latest just confirmed. In the preview check instance, actual revision and all retained/initialized/deleted points. First load initializes all three. Acknowledge the list → **Load and remain stopped**.
6. Expected: stopped, selected/loaded match the chosen revision, first stopped values `false/7/20.5`. Latest-but-not-loaded should be visible. Saving alone must not change currently served loaded values.
7. Recovery: cancel a wrong-version preview, choose latest and preview again. Stop a running instance first. Resolve configuration issues at their reported location rather than repeatedly starting. Loading an older revision forces full initialization; current draft confirmations cannot repair a historical revision.

### 2.6 Start, runtime writes and recovery

1. **Workbench** → PLC_Test **Start**. Expected: running at the displayed endpoint. Inspect logs on failure rather than creating duplicates.
2. **Online values** → PLC_Test. Check the short loaded revision, DB31, types and addresses; its question mark retains full identity. Observe several seconds: BOOL toggles about every1500ms, INT remains7, REAL ramps0–100 over10000ms and need not remain20.5 after start. Updated should display Shanghai calendar time to seconds; hover its header question mark for the definition. Initialization/loading, successful commits and reset record calendar time. Refreshes, rejected writes and unchanged rule values do not advance it. Visible refresh is at most about1Hz; multiple commits within one second may share the same displayed time, so also check point sequence. One frame cannot prove a toggle.
3. INT → **Ordinary write**, enter `12`, check old value, loaded revision, epoch and point sequence, acknowledge → **Confirm this write**. Expected:12 and an advancing sequence while configuration initial remains7. Rule points should not allow ordinary writes. Refresh an unknown receipt instead of automatically retrying.
   The Operations header question mark explains ordinary/maintenance writes. Ordinary writes record UI provenance and do not issue an S7-client request; this INT is configured for UI writes. One-time maintenance applies only to explicitly permitted hold points owned by a client or no owner. It changes the current value once, without changing the initial/owner or automatically reverting later; a client may overwrite it. This example does not require changing permissions to try maintenance. Rule ownership and stopped-state write restrictions remain.
4. **Pause rules** freezes rule time without surrendering ownership; **Resume rules** continues it. **Stop** releases listeners/connections and retains the in-process value12. While stopped, **Reset runtime values**, read the discard warning and confirm. Expected: stopped with `false/7/20.5`, never automatically started.
5. To check actual fixed runtime behavior, repeat fixed12 in2.5, save/confirm, stop → latest → preview/load → explicitly start. It should continuously produce12. Owner performs this runtime check; afterward restore hold/UI per2.5 step3 and save/load it again.
6. Normally close the native window. With dirty edits, choose according to intent: keep/save-and-close/discard/cancel. Reopen the same profile: selected revision initializes and stays stopped with zero connections; previous running intent or manually written12 is not restored. Save-and-close does not load a new candidate. Do not force-kill or delete the database to test this.

## 3. Read-only multi-DB / UDT import

### 3.1 Files, declarations and bindings

1. Stop PLC_Test, wait for connections to release and save dirty edits. On **DB points**, select PLC_Test and choose these two repository files together in the multi-source import selector:
   `automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-multi-db/multi.db`
   and `types.udt` in the same directory. Do not edit either fixture.
2. Keep each as **New source lineage**, then **Scan declarations**. Select only Alpha and Beta; leave all other DBs, including Frame/Spare, unselected. Identify origins by filename and batch identity.
3. Alpha: target **Add DB**, number `71`, empty UDT closure. Beta: target **Add DB**, number `88`, closure **only Measure from types.udt**.
4. **Preview import changes**, check complete Alpha/Beta trees, target71/88, retained DB31 and ignored-initializer notice → **Save import candidate**. It does not load or start.
5. Recovery: cancel and correct a wrong closure/declaration. Check existing DB numbers for conflicts. `:=`, `BEGIN` initializers and RETAIN are not DS initial values or runtime-retention contracts.

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

2. REAL is at byte2 in this standard word layout; it is not forced to a4-byte boundary or proof of real TIA addresses. In each DB, select the whole current point page → **Preview selected point names** → review → **Confirm**. Expected structured names: `DB71_ready_Bool`, `DB71_count_Int`, `DB88_unit_running_Bool`, `DB88_unit_value_Real`; index fallbacks `DB88_B6_Byte`, `DB88_B7_Byte`. Check the actual candidate.
3. Recovery: cancel any wrong address/type. Never infer complete layouts from selected leaves. A DB containing STRING requires manual addresses/reasons for its complete layout; this example does not extend into it.

### 3.3 DB inheritance, initial values and running

1. On policies, under **Parent instance / DB / region policies**, choose DB/Alpha → **Edit policy**: Hold, no owner, client reads Allow, other writes Deny, initial inherited. Keep. Repeat for Beta, then **Save candidate**. Do not set a common DB numeric initial for mixed types; defaults are BOOL=false and numeric0.
2. Filter Alpha then Beta in the main table. **Permissions / sources** should show no point overrides, DB origins for parent settings and type defaults for initials. Each time select all filtered points and save/confirm initial/policy. Expect2 Alpha and4 Beta points confirmed. Source `count := 7` was ignored; current count0 is a DS default.
3. To set count10, edit only its initial, type/blur normally, keep and save/confirm that point. This is an explicit DS setting, not source initializer import. Restore its initial inheritance and confirm if you want count0 for this example.
4. Instances → choose latest → stopped preview → check new DB initialization and original DB31 retention/initialization → acknowledge and load → explicitly start at Workbench. Online values should show the actual loaded revision and nine points across three DBs. Count matches your final confirmed DS value; retained DB31 hold values follow the load list.
5. Recovery: retain errors/drafts on save/load failure. Do not edit fixtures or run DAA. Import, native runtime and reopening still await Owner execution in this task.

## 4. Policy table, filters and three-state bulk editing

### 4.1 Selection scope

1. Select PLC_Test. No DB selection means all its DBs. Selecting DB31 and DB71 shows only those DBs; clearing restores all. Ordering uses DB number/stable DB identity, then address/stable point identity. Structure is read-only here; edit it on DB points.
2. The policy header selects **all filtered pages**. The N/total count persists through paging. Changing DB filter or PLC clears selection and closes old bulk editing. A changed draft baseline blocks stale submission and requires reopening. The eleven-point/ten-row case already has a DEV pure-function check; the manual check is optional. Use an existing set larger than10, or add only two INTs to these nine: create synthetic DB95 length4 with INTs at0 and2, save and clear DB filters for eleven total points. Select the header: expected N=11, still11 on page2. The extra DB need not be loaded; remove owned DB95 and save when finished.
3. Recovery: **Clear selection** before correcting scope. IDs, not row numbers/pages/names, locate changes. Empty results or zero selection cannot submit.

### 4.2 Do not change, set uniformly and restore inheritance

1. Filter Alpha, select both points → **Bulk edit policies**. Every property defaults to **Do not change**. Expected: no-op message, cannot keep, no revision. **Cancel** leaves the draft unchanged.
2. Reopen; only client reads → **Set uniformly** → **Deny**, all others unchanged. Review every before/after value and source. BOOLfalse and INT0 initials may differ; the read-only patch does not require matching initials. Acknowledge → **Keep changes**. Only selected point.clientRead=false should change; DB parent, unselected points, initials and other properties remain. Only relevant policy confirmations invalidate.
3. Saving is separate. **Save candidate**, then check pending confirmations; select only Alpha's two points and save/confirm them. Unselected Beta must not be automatically confirmed.
4. Reopen and set only client reads to **Restore inheritance**. Preview should show the DB's Allow value and DB source. Acknowledge and keep. Only this point property is cleared; unrelated owner/initial overrides stay. Save/confirm if needed.
5. Recovery: cancel a wrong preview. Keeping updates only the draft. A failed save retains the repairable draft and error; do not claim persistence or loading.

### 4.3 Compatibility failures, linked changes and cancel

1. Filter DB31, select BOOL and INT → bulk edit, set mode uniformly to **Toggle**. Expected: INT's DB/point ID/type/reason is listed; the entire candidate is blocked, with no skipped INT or partially changed BOOL. Cancel should preserve both original policies.
2. With the same mixed selection, set only initial uniformly to `7`. BOOL is incompatible; expect the same complete failure. Cancel leaves the draft unchanged. Do not force one initial across incompatible types.
3. Select INT and REAL only. Uniform numeric fixed12 is possible: set mode to Fixed and fixed value12. Links show rule owner, all three writes denied and a complete fixed rule. Review every before/after property/source; initial7/20.5 remain. Acknowledge and keep updates both points once, without runtime writes.
4. To change only reads, leave mode/owner/rule unchanged. A separately set rule requires a complete kind and parameter set; never merge leftover parameters from a different mode. Restoring mode inheritance alone does not clear owner/rule. Explicitly restore the related fields you intend to inherit and resolve preview conflicts before keeping.
5. For acceptance, first cancel step3 to prove no mutation. If you actually keep and save it, restore each point per2.4, reconfirm and reload while stopped. Parent DB, other PLCs and unselected points must remain unchanged.

## 5. Other boundaries and recovery

- Property inheritance is instance→DB→non-overlapping region→point. Regions use bit ranges, must cover complete fields and cannot overlap or split INT/REAL. The parent section retains add/range-edit/policy-edit/remove controls. After parent/range edits check affected sources and confirmations. Type/system defaults are not fabricated confirmations.
- A hold point owned by the S7 client may allow an explicitly authorized one-time maintenance write. Check old value/version/epoch/sequence; it changes neither configured initial nor owner. Paused continuous rules keep ownership. Refresh/reopen an unknown receipt instead of retrying; subsequent writes can prevent readback from proving the original result.
- For source updates, select the original lineage on each file and existing DB target on each declaration, with explicit closure/number. Preview before confirming. Structure/address/type changes invalidate affected confirmations; old initials are candidates, not automatically converted values. Recheck layouts, names, initials and policies.
- Saved but unchanged online values: compare loaded/latest and explicitly load the correct revision while stopped. A manually chosen historical revision remains chosen; choose latest to resume following saves.
- Limits of8 instances,32 DBs/instance,4096 leaves/instance and64KiB/DB are configuration bounds, not capacity evidence. Another synthetic instance can use30103 only after checking the port. UUIDs are independent; names are not identities. This guide requires no16-connection or performance matrix.
- Logs/storage: refresh, filter by an actual event name, clear to restore; pages hold50 bounded events. The Time header question mark explains Shanghai time and seconds display; legacy UTC is converted exactly once. New native logs retain millisecond `timestamp` values with `+08:00` after the development process rebuilds/restarts. The new online-value `updatedAt` also requires a rebuilt Rust process; missing fields are explicitly unavailable, without formatting counters as dates. Old logs without calendar time show "Calendar time not recorded"; dates are not inferred from file modification times or monotonic ns. Monotonic counters remain separate for ordering/durations. Existing SQLite UTC fields/revision history and original logs are retained, without migration or rewriting in this step. Degraded observability or dropped logs do not prove success. Preserve original databases and errors for corrupt/incompatible/read-only/full storage; do not alter schema, delete history or overwrite with an empty database.
- The limited S7 example uses port30102/rack0/slot1, Calling TSAP256 (0x0100), Called TSAP257 (0x0101). Compatible clients need custom-port support, complete fields and per-point permissions; use bit addressing for BOOL. This guide does not launch a client or joint integration.

## 6. Owner feedback

For later feedback, locate2.3 layout;2.4 initial7/20.5/false/0 and invalid text;2.5 fixed12 and latest/historical choices;3 multi-DB import;4 filters/paging/bulk/inheritance. Report “page → button → exact input → blur/confirmation action → actual value/message → expected result.” [DS-001 tasks](plans/DS-001-policy-table-and-usability/tasks.md) retain prior Development facts. Final acceptance is recorded in the [2026-10-27 Owner decision](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001); the guide, self-checks and historical images add no independent QA. The [r5 verification/acceptance](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5) retains original time/input identities and its own acceptance chain. New work needs its own approved scope.
