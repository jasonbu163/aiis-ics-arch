# DAA User Guide

[中文](USER_GUIDE.zh-CN.md) · [Quick start](README.md) · [Common acquisition-data guide](../../docs/acquisition-data-guide.zh-CN.md)

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

For source development, manually copy `.env.example` to `.env` in the DAA directory only if `.env` is absent; review an existing file yourself. If needed, set `DAA_PROFILE_DIR` to an absolute literal path, for example:

```dotenv
DAA_PROFILE_DIR=/absolute/path/to/your/daa-profile
```

A nonblank process `DAA_PROFILE_DIR` takes precedence over the selected `.env`; advanced `DAA_ENV_FILE` can select a different environment file. An empty value is unset, not an empty directory; paths do not expand `~` or environment variables. See [README](README.md#start) for startup and compatibility details.

Install the locked dependencies once in the DAA project and start normally:

```sh
cd automation-world/data-acquisition-agent
pnpm install --frozen-lockfile
pnpm tauri dev
```

Run `cd` from the repository root. Afterwards, use `pnpm tauri dev` from the DAA project directory. If the app is already running with a checked profile, continue there. Startup follows the two saved workbench switches; saving or activating PLC configuration does not itself start collection.

## 2. Configure one PLC and inspect a local sample

This synthetic example need not replace existing configuration. In DS use [minimal.db](src-tauri/tests/fixtures/source-import-minimal/minimal.db) and [minimal.udt](src-tauri/tests/fixtures/source-import-minimal/minimal.udt): create `DEV-PLC-A` at `127.0.0.1:31281`, rack `0`, slot `1`; import `MinimalImport` as DB21, confirm standard layout, give the three points readable initial values, then load and start it. Saving the draft, saving a version, loading and starting are separate actions; see the [DS guide](../device-simulator/USER_GUIDE.md).

| DB21 source path | Type | Address | Example initial value |
| --- | --- | --- | --- |
| `payload.ready` | BOOL | `0.0` | `false` |
| `payload.count` | INT | `2` | `0` |
| `payload.temperature` | REAL | `4` | `12.5` |

1. In DAA **PLC configuration**, add and enable `DEV-PLC-A`, enter the same IPv4, port, rack and slot, finish editing and **Save draft**. Review an existing PLC instead of adding a duplicate.
2. Open **Points and collection groups**, select that PLC, and select both files under the source-file and structure area. Select `MinimalImport`, enter DB number `21`, preview and confirm the import. Under offset assistance, choose **Preview standard-layout offsets**, check the table and 8-byte length, then **Confirm non-manual offsets**. Verify real PLC addresses against the actual source.
3. Under collection groups and periods, add and enable `G1_1000` at `1000 ms`. Select the three points and choose **Enable selected points in this group**. Enabled points for one PLC/DB belong to the same group. Save the draft, choose **Activate configuration**, confirm, and check it is applied.
4. In **Workbench**, select **Connect** for the PLC, then **Start collection**. After a few seconds choose **Pause collection**. Pausing collection and disconnecting are separate actions.
5. Open **Reporting and storage → Local history**, filter by PLC, group and time, and choose **View sample** on a DB21 row. Check the three values, quality and collection times. Samples collected before the reporting binding is saved are **Local record only** and do not automatically enter the queue later.

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
3. Under **Facts delivery**, select **Start / resume reporting**. In the confirmation, compare the **current URL, contract and every listed source** against backend registration and the authorized scope, including instance, reporting PLC, DB and generation for any backlog that could send. The confirmation lists a set of sources; it does not map an individual `sampleId` to a row. If the target or any source cannot be verified, cancel and stop; confirm only after they are checked. Watch pending and unknown states; do not rely on the HTTP status or acknowledged count alone.
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
