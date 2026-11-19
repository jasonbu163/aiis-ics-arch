# DAA User Guide

[中文](USER_GUIDE.zh-CN.md) · [Quick start](README.md) · [Configure PLCs and points](#2-configure-plcs-and-points) · [Windows operation and verification](#windows-source-startup-and-manual-checks) · [Common acquisition-data guide](../../docs/acquisition-data-guide.md)

This guide applies to source versions containing DAA-010 sample reporting and DAA-013 per-PLC bindings, with a backend that has adopted the corresponding source-registration contract. Use the deployment and authorization for the actual environment. This guide does not imply that every environment has been upgraded or accepted for field or production use. Follow the actual version's instructions for older clients or targets.

```text
PLC / simulator → DAA connection and collection → complete local sample → reporting queue
                                                                             ↓
                                    Web acquisition history ← backend storage and reliable receipt
```

Collection and reporting have separate controls: collect first and send after pausing, or run both together. Both startup switches default off. In **Workbench → Startup settings**, enable either to connect and collect from enabled PLCs or to report eligible queued samples the next time DAA opens. Saving the switches does not start or stop the current run. A manual pause or disconnect affects this run; the next start follows the saved switches. This is not an operating-system login or power-on setting.

## 1. Start and check the profile

Confirm the DAA source, PLC or simulator, backend and Web belong to the permitted environment. For a simulator, check its endpoint and loaded configuration; see the [DS user guide](../device-simulator/USER_GUIDE.md) for modeling, loading and startup. Local collection alone does not require the backend.

DAA and DS have separate profiles. If a compatible configuration and history already exist, check the directory actually selected by each app and the PLC endpoint, then continue in the original directories. An empty profile creates separate configuration and history. Do not delete the original directory or copy a sealed profile to manufacture an empty environment. Cold runtime2/3 profiles remain subject to their original admission checks and retain local collection and history without automatic reporting upgrade. Preserve the entire directory and investigate an unknown version, identity or time error.

For source development, manually copy `.env.example` to `.env` in the DAA directory only if `.env` is absent; review an existing file yourself. If needed, choose either a relative or an absolute literal path:

```dotenv
# Choose one; the relative example is under the selected configuration file's directory.
DAA_PROFILE_DIR=./.local/dev
# DAA_PROFILE_DIR=/absolute/path/to/your/daa-profile
```

A nonblank process `DAA_PROFILE_DIR` takes precedence over the selected file's nonblank value; if both are blank or absent, the application default is used. Relative file and process values use that file's directory, not the command's working directory. If the default DAA-root `.env` is absent, its directory is still the base. Advanced `DAA_ENV_FILE` must select an absolute, readable file; an invalid selection fails without fallback. Paths do not expand `~`, variables or placeholders, and parent traversal and existing symlink components are refused. An empty value is unset, not an empty directory.

On Mac, before using a new profile, pre-create the empty root under a writable parent you control. Prevent other processes from moving or replacing the parent or profile during first startup, and confirm the actual selection using the process value, selected configuration file and base above. DAA creates the SQLite files; do not create them yourself. An existing compatible profile keeps its original path, configuration, samples, pending queue, receipts and sealed identity; do not clear, copy or migrate it. If identity or admission fails, preserve the directory and follow the error. Pre-creation only avoids the specific automatic-creation window in [r5 QA2](plans/DAA-010-sample-facts-upload/checklist.md#f-r5-qa2-001-首次创建期间替换的空目录被封存为新-profile): the underlying race remains unfixed and other replacements are not proven safe. This source-development rule does not establish installed-package `.env` discovery or distribution; Windows native validation remains pending. See [README](README.md#start) for startup and compatibility details.

Install the locked dependencies once in the DAA project and start normally:

```sh
cd automation-world/data-acquisition-agent
pnpm install --frozen-lockfile
pnpm tauri dev
```

Run `cd` from the repository root. Afterwards, use `pnpm tauri dev` from the DAA project directory. If the app is already running with a checked profile, continue there. Startup follows the two saved workbench switches; saving or activating PLC configuration does not itself start collection.

### Windows source startup and manual checks

These steps are for later use on Windows 10/11 x64; native Windows validation has not yet been performed. Prepare the complete repository, Git, Node.js, the project-specified pnpm, the Rust Windows MSVC toolchain, Microsoft C++ Build Tools with the Windows SDK, and the WebView2 Runtime. See the [Tauri Windows prerequisites](https://v2.tauri.app/start/prerequisites/#windows).

1. Confirm that DAA and DS select separate data directories. Check and retain any existing compatible directories. To select the DAA directory explicitly, set `$env:DAA_PROFILE_DIR = 'C:\AIIS\DAA\profile'` in PowerShell, replacing the example with your **absolute path**; this takes precedence over `.env`. For DS startup and profile selection, see the [DS user guide](../device-simulator/USER_GUIDE.md).
2. From the repository root in the same PowerShell window, run:

   ```powershell
   cd .\automation-world\data-acquisition-agent
   pnpm install --frozen-lockfile
   pnpm tauri dev
   ```

3. Follow sections 2–3 to configure the simulated PLC, collection and reporting source, then sections 4–5 to check paused-collection reporting and concurrent collection/reporting. Check the reliable receipt and Web history for the same selected `sampleId`. Check existing configuration first; there is no need to recreate it.
4. Use the [Windows native validation record](WINDOWS_NATIVE_VALIDATION.zh-CN.md) (Chinese) to record first initialization, close/reopen, exclusive locking and failure recovery. Its first automatic-initialization check requires a test profile that **does not already exist**; ordinary use of an existing profile serves a different purpose. Mark checks that were not performed as untested.

## 2. Configure PLCs and points

| What you have or need | Steps |
| --- | --- |
| A PLC JSON exported by DS or DAA | [Import PLC JSON](#24-import-plc-json) directly to create the PLC and its points in the draft. |
| TIA `.db` / `.udt` files | [Add or select the PLC](#21-add-a-plc-manually) → [import points and confirm addresses and DB length](#22-import-points-from-db--udt) → [edit names as needed](#23-edit-names-assign-groups-and-enable). |
| A configuration to share with another app | [Export PLC JSON](#25-export-plc-json). Use **Saved draft** to export a newly saved configuration. |
| A PLC ready for collection | [Group and enable](#23-edit-names-assign-groups-and-enable) → [save draft → activate configuration → connect → start collection](#26-activate-and-start-only-when-collection-is-needed). |

DAA creates points from DB / UDT or PLC JSON. To create a DB and points by hand, build them in [DS](../device-simulator/USER_GUIDE.md), export PLC JSON, and import it into DAA.

### 2.1 Add a PLC manually

1. Open **Configuration → PLC configuration**. Reuse the target PLC if listed. To create one, choose **Add PLC**. The app supports up to four PLCs, each with a unique endpoint.
2. Enter **Name**, **IPv4 address**, **Port**, **Rack** and **Slot** to match the PLC or DS listening configuration. Use `127.0.0.1` for DS on the same computer. **Enabled** defaults off for a new PLC.
3. Choose **Save draft** in the dialog. Check the PLC appears in the list, choose **Configure points**, and check the **PLC** selection. Then import its points.

### 2.2 Import points from DB / UDT

1. In **Points and collection groups**, select the target PLC and save any unsaved draft. Open **Source files and full structure → Select source files** and select the `.db` and the `.udt` files it references together. This action is disabled for a PLC containing a JSON catalog DB.
2. On every page, select only the blocks you want to import and set the actual **DB number** for each. Leave **Existing target (explicit update)** empty for a new DB. Select the target explicitly for an update. UDTs are dependencies and need no DB number.
3. Choose **Preview import differences**. Review the DBs, structure, point paths, candidate technical names and diagnostics. Choose **Confirm import and save** once you have checked them. After the points appear, check the addresses and length of each DB.
4. **Confirm addresses.** Select a specific **DB**, then open **Assisted address layout → Preview standard-layout offsets**. Compare byte and bit offsets, candidate names and calculated length with the actual PLC documentation. Choose **Confirm non-manual offsets** after checking. The aid only handles complete, explicitly non-optimized standard layouts. It is unavailable for optimized or incomplete DBs or those with STRING or unknown types. For manual confirmation, choose **Edit** on the point, fill **Byte offset**, **Bit offset** for BOOL, and **Confirmation reason**. Check the address, turn on **Address confirmed**, review the name preview and choose **Save draft**. Confirm an address again after changing it. Inference preserves existing manual addresses.
5. **Check the DB length.** An ordinary imported DB starts at `65536` bytes. Its length updates to the theoretical value only when every point is eligible for and included in the non-manual confirmation. To correct the value, open **Source files and full structure → View complete structure**, expand the DB, enter the actual **DB length (bytes)**, close the dialog and choose **Save draft** at the top.

For a local example, use [minimal.db](src-tauri/tests/fixtures/source-import-minimal/minimal.db) and [minimal.udt](src-tauri/tests/fixtures/source-import-minimal/minimal.udt). Import `MinimalImport` as DB21 and check `payload.ready` BOOL `0.0`, `payload.count` INT `2`, `payload.temperature` REAL `4`, and an 8-byte DB length.

### 2.3 Edit names, assign groups and enable

1. **Check the points.** Select the right PLC and DB and check each **Technical name**, type and address. Choose **Edit** to set **Display name (Chinese)**, **Display name (English)** and **Comment** as needed, review the name preview, then choose **Save draft** in the dialog. **Save draft and edit** saves any pending draft changes first. Display names are limited to 256 UTF-8 bytes per language. Unset names stay empty. The top-bar language selector switches the displayed language. Current v2 reporting uses the technical name. Display names are used for the interface and configuration exchange.
2. **Create a group and enable the points to collect.** Open **Collection groups and periods → Add group**, enter a name and period, and turn on the group's **Enabled** switch. Check the points in the table, then choose **Enable selected points in this group** for that group. Put enabled points from the same PLC / DB in one group. Checks persist across pages and filters, so verify the selected count.
3. **Save and enable the PLC.** Choose **Save draft** at the top. In **PLC configuration → Edit**, turn on **Enabled** for the target PLC and choose **Save draft** in the dialog. Check the points are enabled under the right group and the page shows **Draft saved**. You can stop here if preparing configuration. To collect, continue to 2.6.

To disable points, check them and choose **Disable and unassign selected points**, then use the top-level **Save draft**. Turning off **Enabled** in a single point's editor retains its group.

### 2.4 Import PLC JSON

1. Save or cancel current edits, then open **PLC configuration → Import PLC JSON → Choose JSON file**. Select a single-PLC file exported from DS or DAA. The import creates the PLC.
2. Under **Check the acquisition client target**, verify the IPv4, port, rack and slot for the device reachable from the DAA computer. Choose **Preview again** after a change. Use a loopback address on the same computer. DAA rejects unsupported non-default TSAPs.
3. Review every DB and point, including disabled items, technical names, types, addresses, bilingual display names and descriptions. If the origin only exists in history, select **Import as a new local instance** as needed. The new PLC has a separate local identity.
4. Check **I checked the target and complete point list and confirm that descriptions will be copied to new point comments**, then choose **Confirm creation and save draft**. In **Points and collection groups**, check the new PLC and point count. The new PLC and points are disabled and the points are unassigned. For file exchange alone, stop here or export using 2.5. To collect, follow 2.3 and 2.6.

For JSON imports, display names, comments, groups and enabled state can be edited. The catalog fixes the technical names, types, addresses and point set. The DB / UDT append action is disabled for this PLC.

**Origin or endpoint conflicts.** An origin still in the current draft, active or running configuration blocks import. For a duplicate endpoint, check the target first. If you need to remove an existing PLC with that origin, check the impact. Pause collection and disconnect first if it is active or running. On that PLC row choose **Edit → Remove → Confirm**, then **Save draft** at the top. If it was only in the draft, retry. If it remains in the active or running configuration, explicitly activate the configuration without it, then retry. A new instance from a historical origin does not inherit old samples, reporting bindings, queues or receipts.

Reselect and preview a file that has changed. If the result is unknown, reload the draft and check the source before retrying. The exporter declares the source configuration digest shown in the preview. Verify the actual device layout separately.

### 2.5 Export PLC JSON

1. Save the edits to share, then open **PLC configuration → Export PLC JSON**. Choose **Saved draft** or **Active revision** and check the selected version. The file excludes unsaved edits.
2. Select the PLCs to export. The default filename uses the PLC name and adds `.json` only if the name has no `.json` suffix, regardless of case. You can rename each file. Use a valid and unique filename, keep `.json`, and avoid names that differ only by case. Choose **Preview selected PLCs**, then check each client target and all DBs and points. Preview again after changing the selection or filenames.
3. Check **I checked each PLC client target and complete point list**, then choose **Choose export folder → Export**. Read the header and each row's **Exported** status. Existing files stay in place. Change the name or choose a different folder if needed. For an unknown result, check the folder first.
4. In DS, choose **Instances → Import PLC JSON** and select the file, then check the listening target, layout and names. See the [DS guide](../device-simulator/USER_GUIDE.md).

### 2.6 Activate and start only when collection is needed

1. Check the target endpoint, point addresses, groups, and enabled states of the PLC, groups and points. At the top of the configuration page, choose **Save draft → Activate configuration**, confirm, and check **Applied**. If activation is unavailable, resolve the issues shown in the configuration bar.
2. In **Workbench**, find the target PLC and choose **Connect**. Once connected, choose **Start collection**. For a local DS instance, load the intended revision and start the instance in DS first.
3. In **Reporting and storage → Local history**, filter by PLC, group and time. Choose **View sample** to verify values, quality and time. When finished, choose **Pause collection**, then **Disconnect** if needed.

For collection alone, stop here. Samples collected without a reporting binding are **Local record only** and are never queued automatically by a later binding. For reporting, follow sections 3–5.

After a test, handle only the test objects and exports confirmed to belong to it. Retain anything referenced by active configuration or history. See the native validation records for [DAA-019](plans/DAA-019-plc-json-bidirectional/checklist.md) and [DAA-017](plans/DAA-017-plc-json-import/tasks.md).

## 3. Register the source and configure reporting

First confirm the target backend has adopted the single-table source contract and that registration and reporting are permitted for this run. Sign in as an administrator to Web **Acquisition Data → Source Configuration** and add or reuse the source: `sourceType=daa`, for example `plcId=PLC-A`, `instanceId=daa-a`, `sourceGeneration=gen-a`. Use a generation never used for that PLC when registering a new source. If a backlog exists, check its original identity and the active registration before making changes; do not assign old samples a new generation.

One DAA can collect from multiple PLCs. Each has a separate backend row and a separate set of three parameters in DAA. Different PLCs may share an `instanceId` or use different ones, but two local PLCs cannot bind to the same reporting PLC ID. On the saved row, open **Connection parameters** and choose **Copy parameters**. The JSON contains the three identifiers. `sourceType` is a display label and does not participate in sample admission; `dbNumber` belongs to the sample and query, not a registered DB list. The current single-table backend matches the three identifiers; an older r2 target follows its own DB scope contract.

1. In DAA **Reporting and storage**, open **Delivery settings**. Enter **Backend service address (including port)** and **Reporting API path**, then check the complete URL; the default path is `/api/v1/integration/plc-facts/samples`. `127.0.0.1` means the machine running DAA. Set the delivery interval as needed.
2. Under **Reporting sources**, find the `DEV-PLC-A` row, choose **Paste**, paste the JSON copied from Web, then select **Fill form**. Alternatively enter **Instance ID**, **Reporting PLC ID** and **Source generation** manually. Check each PLC separately; two local PLCs cannot share a reporting PLC ID.
3. The displayed DB comes from the **active local acquisition configuration**; pasting does not change it. Once all three identifiers are present, turn on **Report** for that row and select **Save settings**. A PLC may retain its binding with reporting off while collection continues. Saving does not validate backend registration or start delivery.
4. Produce a new collection cycle after saving the binding to obtain an eligible sample under it. Re-enabling reporting may send eligible backlog; changing address, path or identity pauses reporting until it is checked and explicitly resumed.

## 4. Manual check one: send backlog with collection paused

1. Pause collection. In **Local history** or **Reporting records → View sample**, note the sample ID, local PLC, DB, time, values and quality of a sample collected **after binding**. An unfrozen sample's details do not show its individual reporting identity; the local instance, PLC and generation in the original sample do not substitute for it. If none is eligible, complete section 3, connect the PLC, collect briefly and pause, then select a new sample. Old local-only records do not become pending automatically.
2. Before starting, inspect the reporting states and backlog. Start processes each eligible sample of enabled sources and may send more than one. An unfrozen sample may have no request body, target or receipt yet. For a frozen or attempted record, use **Delivery details** to check its available request body, target and receipt; the receipt remains empty until one is received. A frozen `prepared` sample with zero attempts may use the current new target after review and explicit resumption, keeping its body and identity. Attempted but unconfirmed samples retain their original target; see section 6 before changing it.
3. Under **Facts delivery**, select **Start reporting**. In the confirmation, compare the **current URL, contract and every listed source** against backend registration and the authorized scope, including instance, reporting PLC, DB and generation for any backlog that could send. The confirmation lists a set of sources; it does not map an individual `sampleId` to a row. If the target or any source cannot be verified, cancel and stop; confirm only after they are checked. Watch pending and unknown states; do not rely on the HTTP status or acknowledged count alone.
4. Open **Delivery details** on the selected sample and expand its read-only JSON. Check the reporting instance, PLC, generation and `sampleId` in the frozen request, then verify the receipt `instanceId` and `sampleId` match that request, `status=committed`, and `outcome=created` or `duplicate`. The local instance and PLC IDs in the original sample can differ from the reporting binding; do not confuse them. This is the sample's reliable confirmation; GET or HTTP 200 alone does not substitute for it.
5. In Web **Acquisition Data → Acquisition History**, query using the **reporting PLC ID** from the frozen request (`PLC-A` in this example), the DB and the time range covering collection. Open the **same `sampleId`** and compare point values and quality. The local name `DEV-PLC-A` or local PLC ID is not a substitute for the reporting ID. Latest values may belong to a different sample and do not substitute for history reconciliation.

Expected: collection remains paused, and the selected receipt and Web history agree. Other queue states reflect their actual results. If the record is missing, check target URL, all three source identifiers, the Report switch, sample status/error, PLC/DB, time range and backend adoption. Preserve an unknown sample and its target; do not manually mark it confirmed or delete it.

## 5. Manual check two: collect and report together

1. In the start or resume confirmation, check the current target and all sources and backlog that may send again; stop if they cannot be verified. After confirming, observe that **Facts delivery** is running and note the current **Acknowledged** count as the baseline.
2. In **Workbench**, check that the PLC is connected. If it is not connected, choose **Connect**, then **Start collection**. While collection and reporting **are both still running**, observe samples produced after starting collection in this check and their reporting records. Confirm at least one new sample shows **Reliable commit confirmed**, that the **Acknowledged** count is above the baseline, and record that sample ID.
3. **Pause collection** and allow eligible backlog to drain if needed. For that new sample, check a matching `committed/created` or `committed/duplicate` receipt and the Web values and quality for the same `sampleId`, as in section 4.
4. When finished, choose **Pause delivery** and confirm collection is paused in the workbench. If the PLC connection is no longer needed, choose **Disconnect**. Pausing delivery prevents new dispatches; an in-flight request may still complete.

Expected: a sample produced during reporting can be reconciled through the same receipt and history checks. Otherwise use the checks in section 4 and preserve the current state.

## 6. Recovery and common problems

| Symptom | First check |
| --- | --- |
| Connection fails or no new samples | Check that DS is loaded and started, IP/port/rack/slot match, DAA configuration is saved and active, and points are enabled and grouped. Check workbench status and local runtime events. |
| Reporting unavailable or only local records | Check the selected profile and version. Records collected before binding do not automatically backfill. Preserve existing data. |
| Pending, unknown or needs attention | Filter **Reporting records**, open **Delivery details**, and check diagnostics and any available target and original identity. An unfrozen sample may lack these individual details. Once network or target is checked, continue with the original sample. Unknown is not proof of failure or success. |
| Reporting address changed | Address or path changes pause reporting. A frozen `prepared` sample never attempted may use the new target after review and explicit resumption, retaining its body and identity. Attempted unconfirmed samples retain their original target: restore it, or for an unknown sample verify from actual deployment configuration that both URLs reach the same logical provider and database before choosing **Confirm same target and continue sample** in details. Connectivity or GET alone is insufficient. |
| Nothing resumed after restart | Check the two workbench startup switches and any startup or PLC error; verify the active configuration, source bindings and target. With switches off, connect and start manually. |

Business times display in the Shanghai time zone; retain the original collection time and sample. History and reliable receipts serve different checks. The [precise contract](../../contracts/published/http-api/plc-facts-v2/README.md) owns fields, errors and read limits.
