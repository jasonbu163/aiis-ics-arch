# Stage C facts delivery guide

[中文](STAGE_C_GUIDE.zh-CN.md)

**This walkthrough covers DS → DAA → local SQLite and the DAA-010 sample uploader.** The exact ARCH-ACQ-004 r2 candidate passed independent isolated verification; the r3/r4 single-table steps apply only to targets that have adopted that contract. ARCH-ACQ-004 r4 status and actual environment adoption follow their own task records and authorizations. DAA native UI and Windows remain subject to their own records. This guide does not imply that an existing environment has been switched. The second half retains the DAA-008 B-RUN-01 joint-test history. [Stage B acceptance](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 specification](plans/DAA-010-sample-facts-upload/spec.md)

## Reusing an existing project dev setup

If DS and DAA already use their respective `.local/dev` profiles and the simulated PLC, DB, points and collection group are configured, check the selected profile, endpoint and configuration in each app and continue in those directories. There is no need to create new profiles or reimport points from the isolated example below. Adopt and initialize the actual backend under the approved target procedure; see [host-source project dev](../../INITIALIZATION.md#host-source-development-with-database-only) and [r3/r4 single-table migration and recovery](../../backend/scripts/plc_facts_maintenance/README.md#r3-single-table-migration-and-recovery) and [r2 predecessor migration, import and recovery](../../backend/scripts/plc_facts_maintenance/README.md#r2-candidate-migration-import-and-recovery-frozen-predecessor-tooling).

When pending or unknown samples exist, check and preserve the instance ID, PLC ID, DB and generation captured at sampling. For samples already frozen or attempted, also check and retain the target, body and receipt where present in their details. A pending sample may not yet be frozen, so its target, body or receipt can be empty; do not infer or rewrite its original identity from the current settings. If reusing an existing active backend source, check that it matches the queued identity. If a known old generation cannot be registered, resolve the old queue first and use a new generation only for new samples; do not reassign old samples. After target adoption, continue with [source registration and single-sample reconciliation](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) and sections 5–7 below. Starting reporting processes the eligible queue one sample at a time and may send more than one sample.

## Isolated operation

### 1. Choose the environment

Use a new, explicitly selected DS profile, DAA profile and an approved isolated backend target. Check the actual addresses and that the intended ports are free before starting; the values below are examples, not a claim that any service is running. The existing project dev backend, MySQL and `.local/dev` profiles require the separate operating authorization described in [DAA-010 §7](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续) before registration, migration or delivery.

| Purpose | Example address |
| --- | --- |
| DAA backend origin | `http://127.0.0.1:38117` |
| Project Web | `http://127.0.0.1:5190` |
| Isolated MySQL, used only by the backend | `127.0.0.1:33317` |
| This example's DS simulated PLC S7 listener | `127.0.0.1:31281` |

The local collection exercise needs only DS and DAA. Start other services only within their approved environment; see [project initialization](../../INITIALIZATION.md).

### 2. Start DS and DAA

Each app reads its own root `.env`. This example selects a new `.local/daa-v2-isolated` profile in each app directory. Replace `/absolute/path/to/aiis-ics-arch` in the templates with the actual absolute repository path.

```dotenv
# automation-world/device-simulator/.env
DS_PROFILE_DIR=/absolute/path/to/aiis-ics-arch/automation-world/device-simulator/.local/daa-v2-isolated
```

```dotenv
# automation-world/data-acquisition-agent/.env
DAA_PROFILE_DIR=/absolute/path/to/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-v2-isolated
```

Check the relevant key in an existing `.env`. Paths are absolute literals, with no expansion of `~` or environment variables. A nonblank `DS_PROFILE_DIR` or `DAA_PROFILE_DIR` exported in the terminal takes precedence over `.env`; `DAA_ENV_FILE` can also select a different DAA environment file. If these variables were set in the current terminal, check them and clear obsolete selections before starting. The applications use separate profiles.

For later Windows 10/11 x64 testing, choose a separate absolute local path in PowerShell from the DAA directory, for example `$env:DAA_PROFILE_DIR = 'C:\DAA\isolated'`, then run `pnpm tauri dev`. This instruction is not evidence of a Windows native build, hot-journal recovery or device test; record actual results under DAA-010 AC08.

From the repository root, run these commands in separate terminal tabs. `mkdir` refuses to replace an existing profile; choose and check a different new name if it already exists.

```zsh
cd automation-world/device-simulator
mkdir -p .local
mkdir .local/daa-v2-isolated
pnpm tauri dev
```

```zsh
cd automation-world/data-acquisition-agent
mkdir -p .local
mkdir .local/daa-v2-isolated
pnpm tauri dev
```

When both programs are already running with these profiles, continue below. A new profile starts with empty instance and PLC lists. An existing profile is handled under the version and approval rules below. DAA stores configuration and samples in `local-acquisition-v1/config.sqlite` and `runtime.sqlite`; DS stores configuration in `device-simulator-v1/config.sqlite`. Keep existing `.local` configuration, samples and archives. Selecting an empty profile creates a new configuration and history. [DAA storage](README.md#configuration-authority-and-startup) · [DS storage](../device-simulator/README.md)

### 3. Configure one simulated PLC in DS

This example uses two controlled repository text fixtures, [minimal.db](src-tauri/tests/fixtures/source-import-minimal/minimal.db) and [minimal.udt](src-tauri/tests/fixtures/source-import-minimal/minimal.udt). Select both in the file picker. If an instance with the same name already exists, check its endpoint and DB and continue from the first unfinished step.

1. In DS, open **Configuration → Instances** and create `DEV-PLC-A` with IPv4 `127.0.0.1`, port `31281`, rack `0`, slot `1` and decimal Calling TSAP `256`. Finish editing and select **Save draft**. This rack/slot corresponds to Called TSAP `257`.
2. Open **DB points**, select `DEV-PLC-A`, and select both files in **DB / UDT source import**. Keep each file as **New source lineage** and select **Scan declarations**. Select `MinimalImport`, choose **Add DB** as the target and enter DB number `21`. `MinimalPayload` is associated automatically. Check for missing-dependency messages, select **Preview import changes**, then confirm import and save the draft.
3. Select the imported DB21. Choose **Preview standard layout**, check the `8`-byte DB length and the addresses below, then confirm. Select all three points and choose **Preview selected point names**, review and confirm. Newly imported DBs and points are enabled by default.
4. Open **Simulation and access**, select the instance and DB21, then edit each point's policy. Set simulation mode to **Hold**, write owner to **No write owner**, client reads to **Allow** and the other three write permissions to **Deny**. Enable **Override** for the DS initial value and enter the value below for each point, then finish each edit. Select all three points and choose **Save draft and confirm selected initial values/policies**.
5. Select **Save draft**, then **Save as version**, and confirm the version. Under **Configuration → Instances → Configuration versions and loading**, select `DEV-PLC-A` and choose **Preview loading** on the new version's row. Review the list, acknowledge it and choose **Load and remain stopped**. Start the instance from **Workbench**, then check the values under **Runtime values**.

| Original point path | Type | DB21 address | Explicit DS initial value |
| --- | --- | --- | --- |
| `payload.ready` | BOOL | `0.0` | `false` |
| `payload.count` | INT | `2` | `0` |
| `payload.temperature` | REAL | `4` | `12.5` |

These addresses are the standard-layout inference for this fixture. Declaration and `BEGIN` initializers are not imported as DS initial values. Saving the draft, saving a version, loading and starting are separate actions. [DS user guide](../device-simulator/USER_GUIDE.md)

### 4. Configure DAA and check a local sample

1. In **PLC configuration**, add and enable `DEV-PLC-A` with `127.0.0.1:31281`, rack `0` and slot `1`. Finish editing and save the draft.
2. Open **Points and collection groups**, select the PLC and expand **Source files and full structure**. Select the two files from section 3 together. Select `MinimalImport`, enter DB number `21`, preview the differences, then confirm import and save.
3. Select `MinimalImport · DB21` and expand **Assisted address layout**. Choose **Preview standard-layout offsets**, check the addresses and length `8` above, then **Confirm non-manual offsets**.
4. Expand **Collection groups and periods**, add an enabled group such as `G1_1000`, and set its period to `1000 ms`. Select the three points in the table and choose **Enable selected points in this group** on that group. Save the draft and confirm **Activate configuration**.
5. Under **Workbench**, connect `DEV-PLC-A`, then start collection. After about 5 seconds, pause collection. Open **Reporting and storage → Local history**, run the query and open a DB21 sample to check the three values and their quality. Keep upload stopped.

### 5. Existing directories and new reporting

A new empty DAA profile initializes config2/runtime4 with collection and upload stopped and reporting identity empty. An unbound PLC can collect; its samples are marked local only and do not enter the upload queue when a binding is later saved. A cold runtime2/3 profile that passes its original admission checks continues local collection and history at the same path, without automatic upload upgrade.

The ARCH-ACQ-004 r2 candidate adds a same-directory runtime4 compatibility path after the original structure, identity and integrity checks. It preserves database inode, acquisition configuration, original samples and frozen request bytes, and stores reporting identities separately. Existing eligible records keep their original identity and target rules. The exact r2 candidate passed independent isolated verification; actual target adoption remains separate and must not be assumed for a real profile. [QA5 record](../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#独立验证-qa5) On an incomplete initialization/identity upgrade or credential mismatch, stop and preserve the entire original directory, databases, journals, sentinel and staging; do not manually remove or recreate them.

Do not delete journals, markers or credentials, copy sealed files as a replacement for the original, or open a new store with an old binary. Preserve unknown schemas, missing stores and identity/time mismatches as reported. Actual `.local/dev` adoption, backups, target changes and rollback require separate authorization.

### 6. Register sources and start delivery

1. On an approved backend, an administrator opens **Acquisition data → Source configuration** and follows the rules of the target's adopted version:

   - **Adopted r3/r4 single-table target:** register one row per PLC with `plcId`, `instanceId`, `sourceGeneration` and `sourceType` (`daa` for DAA). `sourceType` only labels and displays the source; it is not part of POST admission or the sample body. POST admission matches the first three identifiers. `dbNumber` remains a sample field and a query filter; no DB read or write list is registered. After saving, open **Connection parameters** on the row and select **Copy parameters** for its three-field JSON.
   - **Older r2 target not yet switched:** register the `daa` source with PLC ID, instance ID, generation and the explicitly authorized reporting DBs; separately authorize the DBs to read. This target continues to use its existing DB write and read scopes. Save, open **Connection parameters** on the row and select **Copy parameters**.

   For either target, use a never-used generation for a new source. If an old queue exists and an active source is reused, check its original identity first.
2. Under DAA **Reporting and storage → Delivery settings → Reporting sources**, enter or paste instance ID, reporting PLC ID and generation separately on each local PLC row. Different PLCs may use the same or different instance IDs; changing the instance for a reporting PLC requires a new generation. Paste accepts the three-field JSON or the older JSON with `dbNumbers`; displayed DBs always come from the active local acquisition configuration and paste does not alter them. Leave all three fields blank for an unbound PLC. Saving does not verify backend registration or start delivery. Enter the backend address including port and API path, default `/api/v1/integration/plc-facts/samples`, and check the combined URL. For a remote backend use that machine's address; `127.0.0.1` is the DAA machine. The interval is 1–3600 seconds, default 5.
   Once the three fields are complete, turn on **Report** for each PLC that should deliver and save. Existing bindings default to on; a new binding must be enabled manually. Turning a PLC off stops its new dispatches while collection continues under the acquisition configuration. After re-enabling, eligible pending samples resume with their original identities; in-flight requests may still finish. Saving only switches leaves other PLCs running; changing the address, path or identities still pauses reporting until explicitly resumed. Samples collected while unbound remain local-only.
3. Collect a new cycle after saving the bindings, then check the target, contract and each instance / PLC / DB / generation, including eligible historical pending sources, before explicitly starting or resuming reporting. Each POST contains one complete PLC/DB sample; live and backlog use the same identity, original bytes and receipt rules. The page separates pending, unknown, needs-processing and confirmed; historical v1 confirmations are separate. Only a matching valid `committed` / `created|duplicate` receipt confirms a sample, not an HTTP status or GET result. [Current development contract](../../contracts/published/http-api/plc-facts-v2/README.md)
   In **Reporting records**, filter by state and open **View sample** or **Delivery details** for a row. The former shows the saved point values, quality and configuration context; the latter shows the target, body digest and read-only receipt. List PLC names come from the currently saved configuration; the PLC ID identifies the historical source and is shown if no current name exists. The list reloads when status counts change and can also be refreshed manually. Column widths can be dragged and reset.
   **Local storage** shows runtime and rollback-journal usage, pending bytes, oldest pending time and the active retention period. The expanded policy form shows draft values; after editing, save the draft and explicitly activate it using the configuration bar at the top. No active policy is inferred when no configuration is active. Local history and runtime events are in the collapsible sections below.
4. Check readback using the backend's configured GET routes or project Web. For an adopted single-table target, check the PLC registration and query conditions; DBs with qualifying facts can be read without a registered DB read list. On an unswitched r2 target, the existing read scope must cover the PLC/DB. The current development contract needs no machine Bearer. A custom POST path does not reveal the GET address: ask the deployer for it. Local samples, requests and receipts remain available if readback is unavailable.

### 7. Pause, target changes and recovery

Pause stops new dispatch; an in-flight response settles against its original attempt. Reopening stops both collection and reporting. Changing the address or path pauses reporting. After checking registration, explicitly resume: never-sent samples may use the new URL while retaining frozen bytes. Attempted, unconfirmed samples remain bound to the old URL. Restore the old address, or open an unknown sample's delivery details and use actual deployment configuration to verify that old and new URLs lead to the same logical provider and the same database and that sources are registered. Select **Confirm same target and continue sample** only after this check. The decision and URLs are recorded; retry still uses the original identity and bytes and requires a valid receipt. Connectivity, matching versions or GET readback alone do not establish database identity. If uncertain, leave the sample for review; do not redirect it to another database or source generation.

## Historical record · DAA-008 B-RUN-01

Everything from **Starting M01** through the end of this page is the unchanged historical v1 run material, including its old `/batches` commands, credentials, target identifiers, read workflow and recovery rules. It is retained for traceability and is not an instruction for the v2 workflow above. Its resources and commands describe that specific earlier environment; no present resource status is inferred. [Approval](plans/DAA-008-reliable-facts-upload/spec.md#r4-b01-f7-owner-approval) · [Run record](plans/DAA-008-reliable-facts-upload/tasks.md)

<a id="m01-launch"></a>

## Starting M01

DAA is a standalone collector. M01 uses a second app, Device Simulator (DS), to provide the C008-A/B simulated PLCs. If the correct isolated DS is already running and both instances are ready, start only DAA. If both apps need starting, use two tabs or split panes in one terminal window because each `pnpm tauri dev` keeps running in the foreground. For everyday DAA use, run `pnpm tauri dev` from its project directory and set `DAA_PROFILE_DIR` in DAA's own `.env` if needed. [Everyday startup](README.md)

**M01 requires no edits to either project's root `.env`.** The dedicated file `.local/daa-008-r2-b01-ops/config/daa-launch.env` is already prepared under the DAA project directory. It contains only the line below.

```dotenv
DAA_PROFILE_DIR=/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01
```

The variables below apply only to their respective launch processes. DAA selects the dedicated file with `DAA_ENV_FILE` and pins the directory with the process `DAA_PROFILE_DIR`. If the shell already has `DAA_PLC_READ_ALLOWED` set, the command prints a message and stops so you can check the inherited setting.

```zsh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent &&
if [ "${DAA_PLC_READ_ALLOWED+x}" = x ]; then
  printf '%s\n' 'DAA_PLC_READ_ALLOWED is set in this shell. Check the inherited startup configuration first.'
else
  DAA_ENV_FILE="$PWD/.local/daa-008-r2-b01-ops/config/daa-launch.env" \
  DAA_PROFILE_DIR="$PWD/.local/daa-008-r2-b01" \
  pnpm tauri dev
fi
```

If DS needs starting, run this in another tab. The DS process pins the isolated directory with `DS_PROFILE_DIR`. On startup DS still reads its own root `.env` automatically under the approved read-only exception. Let DS read it directly. If the file cannot be read or is invalid UTF-8, stop and report the error. [DS read exception](plans/DAA-008-reliable-facts-upload/spec.md#r3-ds-env-exception)

```zsh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator &&
  DS_PROFILE_DIR="$PWD/.local/daa-008-r2-b01" pnpm tauri dev
```

## Coordinator preparation and run boundaries

Use the verified B01 paths, ports and candidate. Stop and check any unexpected directory, port conflict, symlink or candidate drift. Keep the sealed DAA profile at its original location. [B01 resources and stop conditions](plans/DAA-008-reliable-facts-upload/tasks.md#b01-proposal)

| Item | Fixed value |
| --- | --- |
| DAA final profile D | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01` |
| DS final profile S | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator/.local/daa-008-r2-b01` |
| Private operations/evidence O | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01-ops`; 0700, new configuration 0600 |
| DS instances | C008-A / C008-B, real UUIDs generated by the new GUI and recorded afterwards; S7 `127.0.0.1:31281` / `:31282`, rack0/slot1, Calling TSAP256/Called257, connections16/handshakes4 |
| API / DAA origin | upstream `127.0.0.1:18283`, one worker without reload; fixed three-API relay origin `http://127.0.0.1:18281`, no origin switching |
| MySQL / target | `mysql:8.4.6`, `127.0.0.1:13381`; alias `daa008-r2-b01-db`, schema `daa008_r2_b01`, targetAlias/targetId `daa008-r2-b01` |
| New Docker resources | container `daa008-r2-b01-mysql`, volume `daa008-r2-b01-data`, network `daa008-r2-b01-net`, label `aiis.task=DAA-008-r2-b01`, no automatic restart |
| Schema / time | only `0a2c4e6f8b10` / BE009-B / 71 application tables (plus alembic_version); F7 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`; RR, Shanghai +08:00 |
| Lifetimes / capacity | raw values 3 natural months; stable proof 120 days; new-batch 24h admission is separate. Adopted backend budgets 1073741824 value bytes / 1000000 proof rows |
| Ordinary frontend listeners | DAA15191, DS15194, unchanged Tauri configuration; both new profiles start stopped |

The coordinator and backend owner use the following preparation and run boundaries.

1. Freezes the DAA and backend/three machine contracts, DS/runtime/shared core/locks listed in tasks; checks new empty resources, free ports and existing dependencies. Creates accounts/schema only in the new dedicated target, explicitly base→`0a2c4e6f8b10`, never BE010 `upgrade head`. Root creates schema/accounts/grants only. `daa008_migrator` has migration privileges solely there and its runtime credential is disabled afterwards. `daa008_app` / `daa008_maint` each receive SELECT on all71 application tables and alembic_version for metadata visibility, DML on only7 facts tables, no DDL/GRANT/cross-schema access. Verify visibility/F7/version/RR/+28800 seconds. Other64 empty tables remain unwritten; no customer business is enabled. New random passwords/HMAC never enter DAA; no old BE009 resources/passwords are restored.
2. Readiness checks used the private files, `backend_runner.py` and `facts_relay.py` under O. The coordinator prepares `observe_new_profile.py` after the M01 material handoff. Review and freeze each helper's SHA, arguments and guards before use. Backend Settings/FactsSettings anchor backend/.env; the maintenance CLI explicitly merges two dotenv files too. `uv --env-file` cannot isolate them. Before any project import the runner blocks Pydantic and explicit dotenv reads, loads only this private synthetic configuration, verifies13381/schema/account and rejects without fallback. It calls the formal Alembic API / `MaintenanceOptions`+`execute` / `main.app`, preserving CLI enable/exact confirmation/target/epoch/adoption/CAS/approval responsibility checks. Uvicorn is single-worker/no-reload; all bootstrap/mock/Projection/old writers are off. These helpers are fixtures for the isolated run.
3. Uses a fixed relay for `/api/v1/integration/plc-facts/{batches,latest,history}`, only upstream18283, without arbitrary proxying/retries/rewrites. The coordinator may arm exactly once: bind the actual batchID/digest/bodySHA, discard the downstream receipt only after a complete strictly matching upstream committed ACK, then transparently forward the same identity/body retry. It never writes a local ACK. M03/04 stop/restart only this relay, keeping API/DB/target unchanged; tasks fixes limits/timeouts/logging.

## Owner native M01–M05

The Owner starts/clicks the native apps personally; preparation does not operate the GUI or seed configuration with SQLite DML. Capture only5–10 seconds then pause: two1-second groups produce about2 rounds/s, while a1-second uploader sends about1 batch/s. Do not keep collecting while waiting for zero backlog. No instantaneous unknown click or predetermined sample count is required.

### M01 — New configuration and source handoff

1. Open the required apps using the [startup commands](#m01-launch). On first use of the isolated profiles, check that the DS instance and DAA PLC lists are empty and that connections, collection and delivery are stopped. If this run already has configuration, verify the same isolated profiles and corresponding C008-A/B, then resume at the first unfinished step. Stop and verify the paths if other records appear. Keep the databases.
2. If the same isolated DS already runs C008-A/B, verify both S7 endpoints from the table and the DB, point and read/write settings in this step, then continue to step 3. For first-time setup, create C008-A/B in DS Configuration→Instances using the table endpoints. Once per instance select public [minimal.db](src-tauri/tests/fixtures/source-import-minimal/minimal.db) and [minimal.udt](src-tauri/tests/fixtures/source-import-minimal/minimal.udt), choose only MinimalImport, explicitly DB **21**. Preview standard addresses→Confirm, verify length **8**. Select the3 points→Preview selected point names→Confirm without inventing technical names. In DB points verify the DB/all3 points are enabled and save; then in Simulation and read/write policies allow client reads, choose Hold and No write owner, deny all3 write types; explicitly override initial values as below. Finish editing, select the3 points→Save draft and confirm selected initials/policies, then Save draft→Save as version→preview/load while stopped→Workbench Start each instance. Source BEGIN/initializers are not executed.
3. DAA PLC configuration: create/enable the two matching endpoints. Points and collection groups: once per PLC import the same pair as DB21, preview/confirm. Preview standard-layout offsets→Confirm nonmanual offsets; verify below. Add one enabled `G1_1000` group per PLC at **1000ms**, assign/enable the3 points individually, Save draft→explicitly Activate configuration. Do not repeat accepted parser/renaming boundary tests.
4. Workbench: connect each PLC, collect about5 seconds, pause. **Do not start delivery.** Reporting and storage→Source handoff material, hand it to preparation and stop here until adoption is confirmed.

| DB21 point | Type / address | A initial | B initial |
| --- | --- | --- | --- |
| payload.ready | Bool / 0.0 | false | true |
| payload.count | Int / 2 | 0 | 202 |
| payload.temperature | Real / 4 | 12.5 | 25.0 |

Preparation performs one approved new-database RO export: collection/delivery stopped, inflight drained, no journal/WAL/SHM; independent mode=ro/query_only short snapshot, only the new runtime and handed-off instanceId. No immutable/nolock/ATTACH/write/recovery or acquiring/releasing/bypassing the product ProfileLock. Busy/hot/identity/state/relation drift means stop. Export the same committed snapshot's **original UTF8 context and SHA**, revision/cycle/sample/source/sequence relations; recompute SHA and create new output files without replacement. GUI JSON is formatted and has no original-text download; the Owner does not write/reformat JSON.

The backend owner validates material then plans/applies each adoption: new binding revision0, seqFrom1; actual new storageEpoch/adoptionId, with the second PLC using that same epoch/first returned adoptionId/budgets. Provider seqThrough is fixed at **9223372036854775806**. Record actual UUIDs/digests in binding-receipt, never invent them or substitute DS UUIDs for DAA PLC IDs. This new profile's sequence1 is the sole window; no old history. DAA receives no MySQL/HMAC credentials. No upload before adoption and scope readiness.

### M02 — First real delivery and independent upload while collection stops

1. With binding-receipt, Delivery settings: origin `http://127.0.0.1:18281`, targetId `daa008-r2-b01`, actual adoption reference; select only the two verified sources, their seqFrom1 / seqThrough9223372036854775806 / references. Set **1 second**, save; contract digests are read-only.
2. Select PLC→Read test (GET). Initial latest may legally be empty and does not prove a POST failed. Query local history, view Original-cycle package preview, then explicitly Start delivery in Workbench. Watch reliable confirmed samples increase; reconcile false/0/REAL and two PLCs sharing DB21 without cross-talk. GET is never ACK.
3. After the first chain check, Pause delivery; when asked, stop DS A briefly; start DAA A collection for at most5 seconds→pause→disconnect. With both PLCs paused/disconnected, explicitly Resume delivery; the stored backlog can upload independently. Record actual bad/null from the stopped device; if absent, mark uncovered without fabricating/repeated waiting. The coordinator restores DS A for M03. Coordinator handles the single committed-ACK drop; no racing unknown or repeated clicking.

### M03 — Bounded API loss and recovery

Coordinator stops the relay for **20 seconds**, leaving upstream API/DB running. Owner reconnects both PLCs, captures5–10 seconds then pauses. Local backlog grows without false ACKs; after recovery notification keep collection paused.

Existing frozen/unknown requests resume with the same ID/time/digest/bytes. Do not discard them for freshness. Coordinator records at least4 **new freeze opportunities**, with backlog still present, checking the latest/history3:1 rotation including its starting streak phase and that older sequence raw backfill cannot replace newer latest. The first resumed TCP/POST need not be latest. Insufficient backlog/opportunities are reported as a gap, not extended into a soak or a repeated Stage B suite.

### M04 — Backlog exit and stopped reopen, once only

Coordinator stops the relay again until the stopped-reopen checkpoint, at most **180 seconds**. On timeout end the case and restore normally, reporting the gap without another Owner attempt. Owner captures about5 seconds on both PLCs then pauses. Coordinator first verifies actual pending/frozen unresolved work and records a checkpoint. Only then Owner **Cmd+Q** quits DAA once. If there is no unresolved work, stop and record the missing evidence rather than repeating exits. After closed-store reconciliation, reopen with **the same D/env/command**, without pressing any start button.

Both PLCs remain disconnected, collection/delivery stopped; history/queue persist. Coordinator compares original payload/manifest/context/IDs/SHA and any frozen batch bytes/time/digest/members, then restores the relay. Owner explicitly Resume delivery. Claim frozen preservation only when the checkpoint actually had a frozen request; unfrozen pending is separate. No duplicate facts after confirmation. Do not kill DAA, delete journals/markers or change profiles.

### M05 — Details, native appearance and finish

Open a delivery detail in Reporting and storage to inspect original receipt/state; select PLC and read latest plus one original page in a fixed Shanghai range. Pending total must equal unfrozen+frozen+needs-processing, confirmations separate, with multipart membership counted once. Blocked/expired/review must not appear simply running. View the same detail in Chinese/English, light/dark and a narrow window; check spacing/readability, drag a column, page to verify memory then reset. Retain actual screenshots and list visual gaps. Coordinator handles complex cursor scans; Owner writes no SQL/JSON.

Quit both apps normally and notify the coordinator for closeout. This is neither final Stage C acceptance nor deletion authorization.

## Subsequent reconciliation and closeout

Backend owner supplies all7 facts ledgers, beyond HTTP200: stream_state, source_bindings, batches, sample_receipts, raw_samples, cycles, latest_points (all prefixed `plc_facts_`). Join instance/PLC/generation/cycle/sample/part/point, not just name/DB. Check original SHA/definitions/values/quality, observed/saved/committed/expires/proof times, complete-cycle and partial-receipt quality separately, publication(commitSerial,ordinal), sequence, references and idempotency. Compare M04 closed/reopened local originals and reliable ACKs member by member.

Coordinator performs only the listed single lost ACK, one≤2-second dedicated-lock busy case and one independent synthetic unadopted-source rejection; no Owner batch mutation or fabricated receipts. Read latest8/changes8/projection8/original1 per page, at most20 pages/action, with one small-page cursor continuation. Gaps/expired/mismatched cursors/scanBudgetReached are incomplete; another budget needs explicit continuation; GET saves only read_result. Check three-natural-month/120-day exact expiry calculations and cleanup plan, without clock changes/SQL seeding old proofs or claiming elapsed expiry. Reuse same-SHA A evidence for complex parents/local crashes/large receipts and preserve live HTTP coverage gaps.

Stop only registered owned PIDs/children/connections and the new container normally. **Retain D/S, the new MySQL volume and O evidence until the Owner gate and dependency release.** If B-RUN-01 is explicitly approved, after all running/evidence dependencies end the coordinator may remove only this new container/network by recorded ID+label and owned reproducible caches; that approval supplies the authority. Volume/profile deletion remains excluded and requires separate named approval. Retain necessary O evidence, runnable helpers/private configuration and credentials needed to reuse the volume. QA/acceptance itself grants no deletion authority. No down -v/prune, no old profile/history/.env/B007/failure or unrelated resource cleanup. Private env/HMAC/originals stay outside the public repository. Unknown or SHA/schema/time/source/capacity/lock/recovery errors stop new collection/dispatch; preserve material for the responsible owner, never manually ACK/clear the queue.

## Local recovery and original contract limits

New empty profiles create config SQLite v2/runtime SQLite v3. Samples/manifests stay v2 and contexts stay v1. Unknown combinations, missing stores, WAL material, identity/time/schema mismatches and links fail closed. Supported Unix systems seal only genuinely new profiles with `profile-contract.json`, bound to their canonical path, directory and database identities and known schema. Initialization uses a sentinel and no-replace installation; a remaining sentinel/staging file refuses startup without automatic repair. An initialization error does not mean completion. After a final directory-sync error, a later visible complete credential may independently pass sealed cold validation; this does not prove the earlier sync succeeded or establish power-loss durability.

Only a valid sealed profile with exact SQLite extended error 776, one matching journal, an unchanged companion store and the real profile lock can trigger one native rollback attempt. Complete read-only ledger checks run before business logging/actors, on both recovery and sealed cold starts. A later error distinguishes **recovery writes may have occurred** from **native recovery completed but business admission failed**. Preserve the entire profile and report the stable diagnostic; do not delete journals/markers or manually mark samples confirmed.

Existing v2 and unsealed r1 v3 profiles never receive credentials. With no auxiliary files and no hot journal they retain their original cold behavior; without a required credential, hot recovery is refused. A corrupt credential cannot downgrade to unsealed. The format cannot identify complete external deletion of every marker before startup; deleting markers to downgrade remains prohibited. Moving/copying/replacing a sealed profile normally changes its binding and is refused. SHA/inode binding is not authentication and cannot establish protection against malicious same-inode edits or forged journals. Platforms without Unix identity support retain unsealed cold behavior and refuse Unix credentials; macOS synthetic checks do not establish Linux, Windows or power-loss guarantees. Use the original compatible profile/version for rollback, never an older binary on new sealed data.

## Manual read reconciliation

The read dialog offers latest (8 points/page), changes from an explicit earliest baseline (8 items/page), a fixed Shanghai time range/projection (8 items/page), and original samples (1 item/page). Range bounds are half-open and use `Asia/Shanghai`. Dates display seconds; original wire strings retain their precision.

Each explicit action reads one bounded page, at most 2 MiB. **Continue** keeps the opaque cursor and filters. At page 20 it reports incomplete work and requires an explicit new page-budget continuation. Empty pages and `scanBudgetReached` do not imply completion. Gaps or expired/mismatched cursors are shown as incomplete; explicitly restart the desired range or earliest baseline. There is no silent tail jump or SMA checkpoint. These actions save only `read_result` diagnostics and never acknowledge a batch. Original response JSON is displayed without regenerating numeric tokens.

Both delivery cards count distinct local samples: pending total is the sum of unfrozen, frozen and needing attention. Multiple parts or batches do not add samples. Frozen includes prepared/inflight/retry/unknown; blocked, expired-unconfirmed and review cases need attention. Reliable confirmations are separate.

The queue and delivery-events views are separate from acquisition logs. Lists default to 20 rows (10/20/50), with bounded cursor pages. Column widths use stable local field keys and have a reset action. They do not modify business configuration.

## Failure and recovery boundaries

- Timeout, invalid UTF-8/JSON, truncation, wrong content type, conflicting members/digests, and failed local ACK persistence retain the original frozen request as unknown. Resume retries the same target, ID, creation time, digest and bytes. GET is never an ACK substitute.
- A strictly validated terminal rejection alone permits a child containing a legal subset of the same members, with the parent token and at most eight parent levels. Unknown parents cannot be retired. Tokens, values and bodies are not logged.
- Old raw values expire under the provider's natural-month policy; retained proof can confirm a historical commit with `valueReadable=false`. Proof/token expiry is a review boundary, not permission to change timestamps, generate a new identity or delete pending samples.
- Changing target/origin/contracts/source declarations is refused while real unresolved requests remain. Only never-frozen source-adoption diagnostics can be re-evaluated after a matching CAS material update. A silently replaced backend at the same URL cannot be automatically identified from nonexistent epoch/adoption wire fields.
- Physical quota includes SQLite/journal, requests, receipts, metadata and the additional 32 MiB ACK recovery reserve. The initialization auxiliary sub-budget is 256 KiB inside that 32 MiB: actual allocated auxiliary bytes count as used and reduce the remaining reserve by the same amount. Old-page journal and maintenance/system reserves remain separate. High water stops new collection/freezes while preserving recovery; genuine I/O failure can still leave the result unknown. Pending, blocked, unknown and referenced materials are never removed by retention.
- Pause stops new dispatch; the current request finishes within its bounded timeout and persists any valid result. Normal quit keeps unresolved identities. Reopening, including native recovery, never restarts collection or delivery. The r1 failure remains historical evidence; only new sealed profiles have the r2 recovery path.
