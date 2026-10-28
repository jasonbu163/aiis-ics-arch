# DAA–DS Stage B Joint Test Guide (Trial r2)

[中文](JOINT_TEST_GUIDE.zh-CN.md) · [DAA-007 r2 spec](plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) · [DAA](README.md) · [DS guide](../device-simulator/USER_GUIDE.md)

**r2 exactly approved; Owner operation follows P2 freeze. All M01–M09 remain not_run.** r1 time/storage changes remain. r2 adds source .env/profile selection, explicit ordinary UI read admission, standard Tauri startup and resident YAML retirement. See [tasks](plans/DAA-007-ds-joint-validation-and-time-contract/tasks.md) for actual checks/candidate. Operate native windows only after coordinator P2 freeze delivery. Expectations, Owner observations, closed-store RO reconciliation, fresh Verification and final acceptance remain distinct.

**Upgrade limitation.** Only genuinely empty profiles initialize Shanghai-time dual-store v2. Legacy UTC v1/missing/unknown contracts are rejected read-only before writing; configuration/history/raw/SHA remain without automatic migration or replacement stores. Old profiles need their compatible binary; migration/downgrade is separately approved. local-acquisition-v1 is a locator only. Reuse only the original Owner synthetic profiles, never defaults or a third profile, and never copy DEV fixtures/databases.

## P00 — Configure once and check before running

Formal source `/Users/jason/Desktop/DreamCode/aiis-ics-arch`, HEAD=`1fa1ce50a521ebd51c2c43389db011a76f2d74bf` (dirty; scoped delta recorded separately). Use tasks' new r2 freeze manifest, with no source hot edits during operation. Original RUN_ROOT=`/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run`. B0 found both original profiles empty and nonsymlink without opening stores. Before startup the Owner rechecks ownership/state and ports15191/15194/30102/30103. Stop on conflict; do not kill unknown processes or change ports for a pass.

The Owner accepted current DS, DS-001 r1 and ARCH-AW-005 r5 on2026-10-27; see [existing acceptance](../device-simulator/plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001). Historical QA4/DS-001/DIRECT and the new r2 DS bootstrap delta remain distinct; DS's QA exception does not transfer here. r1's227 DS/158 DAA/12 core planning drift is recorded in tasks history. r2 fixes its new before/51-file implementation/protection manifests without assigning old passes to new changes.

The Owner manually copies `.env.example` to `.env` in each app root, then edits it. **Preserve an existing .env** and review/edit only your own active profile key. The Agent does not read/write these real files. Fill once:

DAA: `automation-world/data-acquisition-agent/.env`

```dotenv
DAA_PROFILE_DIR=/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run/daa-profile
```

DS: `automation-world/device-simulator/.env`

```dotenv
DS_PROFILE_DIR=/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run/ds-profile
```

Each key selects the storage root: nonblank process > own .env nonblank value > original default; blank is not an empty directory. Use absolute literals without parent traversal/symlinks; no `~`/`$VAR`/`${VAR}` expansion or shell execution. One paired quote layer is removed and first duplicate wins. Missing default .env permits defaults; invalid explicit DAA_ENV_FILE, unreadable/non-UTF8 default .env and invalid profiles reject before writing without fallback. DS has no DS_ENV_FILE. Vite envDir:false remains. Dev/build do not isolate data automatically; installed-package .env discovery/distribution is outside this contract.

Check inherited overrides once in the actual launch terminals without dumping the environment or secrets. A remaining r1 `DAA_ENV_FILE` selecting RUN_ROOT/daa.env supersedes app-root .env. That synthetic file is historical; the Agent does not edit/delete it. If obsolete overrides exist, the Owner may once run `unset DAA_ENV_FILE DAA_PROFILE_DIR DS_PROFILE_DIR`; also unset an obsolete process DAA_RUNTIME_MODE=legacy_snapshot if present. Old YAML locators are ignored; ordinary startup does not read/hash them or seed PLC_1.

Ordinary native reads need no .env authorization. The Owner may remove the old DAA_PLC_READ_ALLOWED file key once or understand that either true/false is ignored. The advanced **process** key allows later UI actions only when truly absent or valid true; false/empty/invalid/undecodable denies reads and file true cannot override it. This ordinary joint run records that the process key is unset; if unintentionally inherited, the Owner may once `unset DAA_PLC_READ_ALLOWED`. Do not fix it with file true or repeat long startup commands. Stopped initial state and enable/address/activation/capacity/log/time protections remain.

| Pre-run record | Owner confirmation pending |
| --- | --- |
| Candidate/drivers | New freeze; DAA Tauri build.features=[rust-snap7-driver], local-validation off; DS native-s7, test-automation off |
| Configuration source | Both resolved profiles and their sources, ordinary process read key unset; no unintended default/old stores |
| Ownership/ports | Original two Owner profiles meet P00 conditions;15191/15194/30102/30103 conflict-free |
| Initial state | No DS/DAA connection or running/collection intent; empty DAA without PLC_1 or new migration receipt |
| Data protection | No real/default stores; tasks holds synthetic legacy/v2/Shanghai checks, without asking Owner to open old stores |

## M01 — Standard short desktop startup

After one-time .env configuration and coordinator freeze confirmation, run only:

Terminal A:

```sh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator
pnpm tauri dev
```

Terminal B:

```sh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent
pnpm tauri dev
```

DAA Tauri configuration supplies existing rust-snap7-driver (the S7 communication implementation); DS retains native-s7. No feature argument/driver alias is required. Record actual commands, candidate/features, resolved profiles/sources, ordinary process read key unset and both stopped initial states. Expect two native windows, empty DS/DAA lists and no S7 listener/connection/collection yet (Vite may listen). Existing objects/history require ownership/profile investigation, never deletion for a blank test. UI + SQLite own endpoints/points/groups/periods; save/activate/load and explicit Workbench connect/collect/pause/disconnect remain separate, without a global SQLite read switch, auto-start or restored runtime intent.

## M02 — Configure distinguishable DS instances

Configure A first; B can wait until M06.

1. DS Configuration → Instances: create `B007-A`, `127.0.0.1:30102`, rack0/slot1, Calling TSAP256 (0x0100), Called TSAP257 (0x0101), connection/handshake limits16/4. Keep edit, then save candidate.
2. In DB Points, follow [DS guide §3](../device-simulator/USER_GUIDE.md#3-read-only-multi-db--udt-import): select `automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-multi-db/multi.db` and adjacent `types.udt`. Scan, select only Alpha/Beta; Alpha needs no UDT, Beta selects only Measure in its closure.
3. Map Alpha to DB71 and Beta to DB88, preview and confirm import. Preview/confirm standard addresses per DB and review naming. Leave Gamma/Delta/Epsilon/Zeta unselected and source files unchanged.
4. Explicitly set the following DS initial values/policies, enable all six points and allow client reads. Unspecified writes stay denied. `count := 7` and `BEGIN` are not imported initial values. Save and confirm selected initial values/policies. Match physical addresses, not cross-application UUIDs.

| DB / length | Source path / type / address | Technical name | A initial | B initial | Policy |
| --- | --- | --- | --- | --- | --- |
| 71 / 4B | ready / BOOL / 0.0 | DB71_ready_Bool | false | false | Toggle, rule owner, halfPeriodMs=1000 (2000ms full cycle), generic periodMs=2000 and phase=0; all three writes denied |
| 71 / 4B | count / INT / 2 | DB71_count_Int | 101 | 202 | Hold, UI owner, ordinary UI writes allowed |
| 88 / 8B | unit.running / BOOL / 0.0 | DB88_unit_running_Bool | false | true | Hold, no owner, all three writes denied |
| 88 / 8B | unit.value / REAL / 2 | DB88_unit_value_Real | 12.5 | 25.0 | Hold, UI owner, ordinary UI writes allowed |
| 88 / 8B | bytes[3] / BYTE / 6 | DB88_B6_Byte | 18 | 86 | Hold, no owner, all three writes denied |
| 88 / 8B | bytes[4] / BYTE / 7 | DB88_B7_Byte | 52 | 120 | Hold, no owner, all three writes denied |

5. Toggle changes each `halfPeriodMs`; the UI has no `base` field. False is the initial value, not a continuous-rule parameter. Retain established valid defaults for other rule fields. Instances: select latest saved version, preview loading/preservation, review six points/DBs/lengths/initials and confirm load while stopped. Explicitly start A in Workbench, then **pause rules** while retaining readable S7 service.
6. Online Values: check six points. Count/REAL/BYTE match the loaded table values; ready may already have toggled, so record its actual paused snapshot. Record the loaded revision: saving is not loading.

For address/name confirmation failures return to that step; for policy confirmation inspect the selected points. For read rejection check enable/client-read rather than granting unrelated writes.

## M03 — Configure the first DAA PLC, points and groups

1. Configuration → PLC Configuration: add enabled `B007-A`, host127.0.0.1, port30102, rack0/slot1; retain established timeout defaults and save draft. Saving does not connect.
2. Points and Collection Groups: select A and the same source pair. Expect6 DB/3 UDT declarations; select only Alpha/Beta, map71/88, preview complete differences and confirm import.
3. For Alpha and Beta separately, Auxiliary Address Calculation → Preview Standard Layout Offsets → Confirm Nonmanual Offsets. Compare types/addresses/lengths and names with M02; never bulk-replace manual addresses.
4. Collection Groups and Periods: add enabled `Fast_500` (500ms) and `Slow_1000` (1000ms), save draft. Edit each point in its dialog: both BOOLs belong to Fast, INT/REAL/two BYTEs to Slow; enable all six and retain confirmed addresses. Each point belongs to one group.
5. Use individual dialogs here rather than assigning all filtered points accidentally. Header selection is for naming, not acquisition enablement. Save, inspect each group/enable/address and explicitly activate configuration.
6. Expect applied runtime configuration with no connection/acquisition yet. Resolve pending names, missing groups, unconfirmed addresses, dirty edits or active editors at their source, then save/preview again.

## M04 — Connect, compare a point and collect

1. In DAA Workbench connect only A and wait for completion. DS A gains one DAA session. Use connection testing/single-point diagnostics as needed; diagnostics reuse that connection.
2. Keep DS rules paused. Start DAA A collection, wait about10seconds, then pause collection. Pausing normally retains the connection; disconnect is a separate action.
3. Reporting and Storage → Local History: both groups and DB71/88 have new records. Open sample details, original payload, full-cycle manifest and configuration context. Expect origin `s7`, quality `good`, delivery `pending`, and original-byte SHA.
4. Compare by PLC/DB/source path/address/type with the paused DS snapshot. DAA dictionaries use DAA point IDs. This example uses exactly representable REAL12.5/25.0; future dynamic floats require their type precision.

Each group spans two DBs: one completed group cycle produces two DB samples with a common cycle ID/full manifest. Fast contains two BOOLs, Slow four other points. Cross-group/DB reads are not an atomic PLC snapshot. Source sequence is shared by the PLC groups; gaps after group filtering are normal. The coordinator reconciles the isolated stores read-only after final normal exit; no manual row arithmetic is needed.

## M05 — Changed values and different periods

1. Resume DS A rules and restart DAA A collection. Within roughly15seconds, ready history should include true and false; unit.running retains its configured state.
2. In DS A Online Values, ordinary-write count101→111 and REAL12.5→13.25. Review loaded revision/old values and confirm each write. These are DS UI memory writes; DAA still only reads through S7.
3. Wait a few seconds, pause DS rules and record its snapshot. New good DAA samples contain111/13.25; earlier samples retain earlier values.
4. Fast/Slow acquisition intervals should approach500/1000ms, with roughly2:1 completed cycles in a stable healthy interval. The1Hz UI refresh cannot prove sampling frequency. Reconciliation uses actual cycle times and read/save costs, not one page's row count or hard real-time guarantees.

## M06 — Second PLC and identical DB numbers

1. Keep A. Repeat M02 for DS `B007-B`, port30103 and B initials, then load/start/pause its rules.
2. Pause DAA A collection. Repeat M03 for B with port30103, the same sources, DB71/88, groups and six points. Save/activate and verify A's draft, IDs, addresses and history remain. Activation may change runtime revisions; explicitly reconnect/start according to actual Workbench state.
3. Connect and collect both DAA PLCs. Expect one DAA session per DS instance, B markers202/25.0/86/120, A's actual current markers, and no cross-PLC history contamination.
4. During normal collection diagnose one A point; B continues and A reuses its session. Do not introduce other clients that would obscure connection counts.

## M07 — Disconnect, unaffected peer and recovery

1. With both collecting, **stop only DS A**. Keep B serving. Record the action time, wait roughly5seconds and observe A's fault/reconnecting state while B gains good history.
2. A may have explicit bad/null/error samples or no committed cycles during the outage. Never label cached good values as newly read good samples or promise reconstruction of unread PLC values.
3. Restart DS A. If DAA retained connection/collection intent, it reconnects within backoff and gains new good samples. Current backoff plus jitter can approach36seconds; observe up to45seconds before reporting state/error/times, without repeatedly connecting or changing ports.
4. Verify B continued. A hold-value retention follows DS same-process stop/start semantics; reset or process restart initializes differently and is not part of this step.

## M08 — Time, history filtering and details

1. Pause both DAA PLCs and allow in-flight cycles to finish. Filter by PLC/group/quality, turn a page and open details. Delivery remains pending: no upload, ACK or queue clearing.
2. Ordinary calendar displays use Shanghai `YYYY-MM-DD HH:mm:ss`. New payload/ordinary IPC timestamps carry `+08:00`, retaining original milliseconds. savedAt represents saving, not UI refresh.
3. Choose a Shanghai-calendar interval covering the run and find known samples. Bounds are inclusive, from the start second's `.000` through the end second's `.999`, retaining end-second samples. Start-after-end must produce a clear error; clear both to restore querying. Refreshing does not change original times, values or hashes.
4. Resize one ordinary history column, paginate/filter/navigate away and back: retain width. Restore Default Widths affects only this table. Resize again for M09 restart checking; selection/action columns may be fixed.
5. Record one A and one B sampleId/cycleId/SHA/group. Expand manifest/context and close. No large-JSON copying or direct SQLite editing is required.

The developer checks non-Shanghai host-timezone behavior and the legacy guard using synthetic data. Do not change your system timezone or try default databases for these checks.

## M09 — Normal exit, reopen and handoff

1. Pause and disconnect both DAA PLCs, wait for DS sessions to release, resolve unsaved edits and Cmd+Q DAA once. Do not force-kill. Report **M09 first exit complete** and leave DAA closed until the coordinator records a read-only closed-store baseline and confirms reopening. This proves the next step preserves existing samples; acquisition is not repeated.
2. After that baseline confirmation, reopen DAA with the **same .env and original Owner profile** from M01, retaining env/profile. Expect both configurations/groups/history and recorded IDs/hashes, with no connection/acquisition. History widths persist; then restore defaults.
3. Query/open the two known samples, then normally exit DAA for coordinator read-only reconciliation. Stop both DS instances and normally exit DS. Three repeated window cycles are not required.
4. Keep this run's data until feedback and final acceptance. After evidence archival and dependency/ownership checks the coordinator may reclaim only owned run data, never defaults/shared targets/original sources.

M09 also records the resolved profile/source, same r2 candidate/features, ordinary process read key unset and stopped initial state. Wait for the DEV RO checkpoint after first exit before one same-profile reopen; do not repeat M02–M08.

## Common blockers

| Symptom | Check first |
| --- | --- |
| `driver_unavailable` | Check the formal candidate and Tauri build.features behind ordinary pnpm tauri dev, with local-validation off |
| Connection failure/reconnecting | DS loaded and started, selected PLC/port/rack/slot/TSAP; saving a candidate does not start listening |
| `bad_read` / null value | Actual DB number, bounds, enabled points and client-read permissions; pause rules and inspect loaded configuration |
| Activation disabled | Active editor, unsaved draft, group membership, pending names, address confirmation and reported issues; header selection does not enable collection |
| Legacy time contract/unknown schema | Preserve the databases and stop using that profile for the new version; return to P00, never clear data or edit time/schema |

## Feedback and finalization

Record actual outcomes. Use `not_run` for unperformed work and `blocked` for a blocker, including step ID, page/button/input/message and approximate time. Text feedback is sufficient; screenshots are optional evidence where useful.

| Stage | Operator/run | Actual result (initially not_run) | Issue/recheck scope |
| --- | --- | --- | --- |
| P00 | Pending | not_run | Version, DS baseline, paths, ports |
| M01–M03 | Pending | not_run | Startup, DS and DAA configuration |
| M04–M05 | Pending | not_run | Static/changed values and periods |
| M06–M07 | Pending | not_run | Multiple PLCs, sessions and recovery |
| M08–M09 | Pending | not_run | Time, history and normal reopen |

Walk the trial once, repair only affected items and record focused rechecks. Development self-checks, Owner native observation, post-exit read-only reconciliation, fresh-context Verification and Owner final acceptance remain separate. Verification must not claim it operated native windows or repeat the entire DS/DAA stress matrix. Finalize the guide only after the steps work in practice and the Owner confirms them.

DAA-007 acceptance does not accept DS-001 or older DAA tasks automatically. Overall Stage B needs the finite baseline/joint evidence and explicit Owner acceptance. Stage C reliable upload, Backend/SMA, real PLCs, production databases/APIs and field switching remain separately scoped.
