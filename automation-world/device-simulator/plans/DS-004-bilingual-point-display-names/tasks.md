Task ID: DS-004
Revision: r2
Status: developer_handoff
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Owner Role: Development
Allowed Writers: Development
Handoff: r2 Development implementation and self-check recorded below -> fresh-context Verification; native UI and native close/reopen remain unverified.
Approved spec SHA-256: `c3e719d6373c70d4fe45df289a26cd83f104e88878b74693900f76533509c267`
Working tree: `/Users/jason/Desktop/DreamCode/aiis-ics-arch` at base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`, with pre-existing unrelated changes.

# Development record

- 2026-11-17: Human Owner approved DS-004 r2 and the parent-version linkage. Verified exact r2 `owner_approved` spec SHA-256 `c3e719d6373c70d4fe45df289a26cd83f104e88878b74693900f76533509c267` and parent ARCH-PLC-001 r4 `owner_approved` SHA-256 `7b2c37a6aa37ffcd03403a435c106da5c3a9f81e12b3a2ffcab04f68ec3a11cc`. QA3 `qa_failed` checklist SHA-256 `057624c3e55f2a6ea4de896479c8140d499f6c0e21024eb2db7f6af3d7c7c5b9`; its F3/F4, QA1/QA2 and all earlier Development evidence remain intact below and in the checklist. r2 adds only `src/App.vue` to the r1 product allowlist; GUI/CUA and real profiles remain prohibited.
- 2026-11-17: fresh-context QA2 preserved QA1 history, rechecked F1 and recorded F2 `qa_failed` in `checklist.md` SHA-256 `a122c57cfbb5d0cb9b74b45d9b0786ddd5cfed9c3cdb9fea268e6ad01ea88f10`. An unknown stop receipt followed by a known pause rejection was overwritten in a single safety-failure slot and then hidden when the unrelated save check cleared it. Rework will retain unresolved runtime-control receipts and require an explicit check of current runtime facts; that check cannot prove the prior operation's outcome.
- 2026-11-17: fresh-context Verification recorded `qa_failed` in `checklist.md` for F1: an actually committed draft save can return an unknown receipt; existing UI wrongly states failure and ordinary refresh does not read draft/version facts. Rework remains within r1 allowlist; pending unknown results must not be automatically retried or silently overwrite local edits or concurrent changes. The earlier handoff and evidence below are retained as history.
- 2026-11-17 (Asia/Shanghai): verified r1 `owner_approved`, the exact spec hash, parent ARCH-PLC-001 r3, project rules and task scope. Task bundle initially contained only `spec.md`.
- Development-owned temporary root: `/private/tmp/ds-004-r1-dev.G6mp7M`. Only synthetic profiles and isolated build outputs will be created there; no real profile, network/device operation or DDL is authorized. Resources are retained while DEV and fresh QA need compatibility evidence, then may be removed by the owner after QA confirms no dependency.
- Planned sequence: capture an old-implementation binary and synthetic legacy profile; implement optional independent fields and UI; exercise Rust/Node/build/native behavior; record exact results and handoff.
- Baseline `CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-old cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names --no-run` exited 0 before product changes. Old runtime test executable `cargo-old/debug/deps/point_display_names-f259d2b34ad19b3e` SHA-256 `70589d62bd2708f3c0a0276cfb5c86280473358e9e636bf086dcfc2d0e70eb4a`. Its explicitly ignored `compatibility_probe`, with `DS4_COMPAT_MODE=create` then `old` and `DS4_COMPAT_PROFILE=/private/tmp/ds-004-r1-dev.G6mp7M/legacy-profile`, each exited 0. The old application opened and closed the synthetic selected-revision profile with legacy `displayName` intact and unchanged SQLite bytes; database SHA-256 `4d7a20af276841ce1018de1aef0df33569d9c14d578afb0951ba53ed8e805781` at baseline.

## Implemented candidate

All paths below are relative to `automation-world/device-simulator/`. `runtime/src/domain/configuration.rs` adds closed, optional `displayNames` and optional `description`, rejects explicit null/wrong types/extra keys and enforces UTF-8 byte limits without changing the serialization of absent fields. `runtime/src/services/source_import.rs` initializes the two fields as absent for new points; same-identity imports continue to clone the previous point. `src/services/deviceSimulator.ts`, `src/app/simulator/views/points/index.vue`, `src/app/simulator/components/PointEditor.vue`, and paired `src/app/simulator/locales/{en-US,zh-CN}.json` add the independent editors and current-language table column through the existing shared table. Editing metadata on an incomplete imported or manual point does not infer or change its name, type, byte or bit. Cancel edits a detached form; the existing explicit draft save remains the persistence boundary.

Added `runtime/tests/point_display_names.rs` and `tests/point-display-names.test.mjs`; added two rows to the module `CODE_INDEX.md` for those new files and one matching paragraph to each `USER_GUIDE.md` / `USER_GUIDE.zh-CN.md`. Both user guides already had unrelated uncommitted changes before this task; those changes were retained. No production configuration, dependency, lockfile, schema definition, migration, other module, other task spec, `checklist.md` or PLAN was edited by Development.

The following SHA-256 values describe the **initial** candidate that produced QA F1; the updated rework hashes below supersede them:

```text
22331f7649a5849102cc919f8441dfbf9f472b54e43a806a3831e7426d0b75e4  runtime/src/domain/configuration.rs
e4e365fa9f7411fb9ac5fb58dbdc478fd62ee0e4d7bcdbaba81761f4266a9dec  runtime/src/services/source_import.rs
d30e505d7cb73e7f9989109dcd8523264ce59da9a9d902928d08a21f84380c6d  src/services/deviceSimulator.ts
30b86a632b09255d80ff67a77a650b4033265fdc321df3035eddb6b05a6c1c0a  src/app/simulator/views/points/index.vue
ef57a7f010506377b9155822ccacc5eff44aa110fcb67817984e8b0520e21079  src/app/simulator/components/PointEditor.vue
ca4cb7709be5e64d952f65b2ad073ad688279c3cc83262c3c2e5d1cd3915f3a1  src/app/simulator/locales/en-US.json
e078891300d0660e005c4c2a28eef23e49f873a8a5f94ea7853613b7db129744  src/app/simulator/locales/zh-CN.json
f084fca67bf363a0801eb80b630a36075728d60f921d1b221e967034cd63de25  runtime/tests/point_display_names.rs
f5544d59948b209c79741c9ae163f55b3bfba9d361592c985d95b84a4e10cd3a  tests/point-display-names.test.mjs
```

## DEV self-check — actual results

Commands below were run in the DS directory on macOS arm64 (Darwin 24.6.0), `rustc 1.89.0`, `cargo 1.89.0`, Node `v22.19.0`, pnpm `11.11.0`. All Cargo targets, generated UIs and profiles were under the task's temporary root. The zsh startup repeatedly printed `/bin/ps: Operation not permitted`; it did not make the listed successful commands fail.

| Command / check | Actual result |
| --- | --- |
| `CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/rust-regression cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract` | Exit 0; 19 passed; the separately invoked compatibility probe was ignored in the ordinary suite. Tests use only new synthetic profiles. |
| `CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/rust-final cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names` | Exit 0; 3 passed, 1 explicit compatibility probe ignored. Covers malformed/null/extra keys and byte boundaries, preserved Unicode/spaces, independent old/new fields, SQLite save/reopen, stale ETag, revisions/selections, TIA same-ID retention and changed-ID isolation, preview cancellation and stale import. |
| `node --test tests/*.test.mjs` | Exit 0; 23 passed, including actual Vue component/page logic rendered in memory, cancellation, over-byte rejection, unconfirmed TIA/manual address preservation, Chinese/English empty-side selection without save, locale parity and shared table-width utility regression. This is not a native WebView test. |
| `cargo fmt --manifest-path runtime/Cargo.toml --check` | Exit 0 after formatting the touched Rust files. Initial check before formatting exited 1. |
| `pnpm exec vue-tsc --noEmit && pnpm exec vite build --outDir /private/tmp/ds-004-r1-dev.G6mp7M/ui` | Exit 0. Vite reported existing dependency PURE-annotation and chunk-size warnings; no dependency change was made. |
| `git diff --check -- <tracked candidate files>` | Exit 0. `git diff --no-index --check /dev/null` for each new test emitted no whitespace warnings and returned 1 because the files differ. |
| Python stdlib relative-file-link scan of the two guides and `CODE_INDEX.md` | Exit 0; 41 checked links, zero missing. Anchor validation was not performed. |

The first in-memory Vue test run exposed a test-harness footer-slot omission (2 failures); fixing the harness yielded the passing runs above. The component test also exposed and drove correction of an initially introduced change to an unconfirmed imported BOOL bit. These are Development self-checks, not independent QA.

### Legacy binary and source archive

After the old binary created the synthetic legacy profile, the newly compiled binary ran the same ignored `compatibility_probe` with `DS4_COMPAT_MODE=old` against it: exit 0, old selected revision opened and the SQLite bytes remained unchanged. A copy of that **owned synthetic** DB was made at `new-profile`; the new binary ran `DS4_COMPAT_MODE=upgrade` (exit 0), explicitly saved a Chinese value and description, and retained the old revision/selection. The old binary then ran `DS4_COMPAT_MODE=reject` (exit 0): `App::open` returned `storage_payload`, and the entire new DB SHA-256 before and after rejection was `9baabb5ac058b8cff20886be719c99c9570f023da49567c31a1d4b64db481dad`. It did not open an empty substitute profile.

For an additional old source-archive case, an isolated helper `/private/tmp/ds-004-r1-dev.G6mp7M/old_source_probe.rs` was compiled with `rustc --edition 2021`, linked against the **pre-change** `cargo-old/debug/deps/libds_runtime-f3dc85d8b60c292c.rlib`, and run only on `legacy-source-profile`. The old library created a synthetic archived source and published a second revision. Old and new ignored `compatibility_probe` executions in `old` mode each exited 0. The entire SQLite file stayed `abe4291ec0969a95c6b8769e5cfc9470588dd7b1a8020f3d47e28f276b5d4e6d`; the archive row retained 86 bytes and SHA-256 `8a90d93c0f5eda7fd350251ee03865c2a009374be18e24afba2e38440e1fcdd8`, with two historical revisions. The helper, binary and owned profiles are retained at the task temporary root for fresh Verification.

### Capacity and unknown receipt

The additional owned `/private/tmp/ds-004-r1-dev.G6mp7M/capacity_probe.rs` linked the new `ds-runtime` and generated 4,096 points with both display names at 256 UTF-8 bytes and descriptions at 500 bytes. The initial serialized payload was 5,926,517 bytes, below the existing 16 MiB configuration limit. The probe published the first version; its second `Store::save` returned `save_receipt_unknown` and the probe exited 1. No retry was made. After that process exited, a **read-only** SQLite query found `quick_check=ok`, schema/user_version 1, one intact revision with first description prefix `0`, and an intact 4,096-point draft with prefix `1` and ETag `a4fe1050-c25c-4c59-929b-31cf66036d00`; both payload hashes matched. The second save therefore committed despite the one-second receipt timeout. The approximately 11 MiB DB and calculated pending budget were below the existing 128 MiB storage gate; this is an observed large-payload timing/unknown-receipt risk, not proof of capacity exhaustion. A native readback/reopen at this extreme has not been verified. QA should independently inspect the retained synthetic profile, reconcile unknown results before any retry, and decide whether this risk satisfies r1.

## Native UI limitation and isolation evidence

No real macOS WebView/window was started, so editing in the native UI, top-bar switching there, and native drag/reopen/reset column widths are **not verified**; DS4-07 is not claimed as passed. The ordinary bootstrap reads an existing source-tree `.env` before resolving even an explicit process override. For isolation preparation, the formal product runtime, desktop source, native source and shared TIA core were copied (excluding `.env` and build targets) into `/private/tmp/ds-004-r1-dev.G6mp7M/native-snapshot`; `rsync -rcn` checks excluding tests showed no product-source differences. The frontend output was built from the formal tree above. A normal Tauri product build from this snapshot with existing CLI, `CARGO_NET_OFFLINE=true`, `--debug --no-bundle`, a temporary `frontendDist`, and empty `beforeBuildCommand` exited 0; this is a build only, not an entrypoint or UI run.

The existing test-automation build avoids ordinary `.env` but requires the fixed ARCH-AW-005 profile root, scenario set and validation identifier. macOS actual WebKit storage is separate from the profile (`BUILD.md` and `scripts/run_validation.py:265,296`). A fresh empty synthetic profile under `native-profile` has UUID `166246f3-4e9f-499c-b32a-89964e872ddc`; the exact UUID subdirectories under product, executable-name and validation WebKit identities were absent when checked. A task-unique `.app` built with Tauri config identifier `com.aiis.aw.ds004.g6mp7m` has that outer Info.plist identifier, but its product Mach-O still embeds `com.aiis.aw.devicesimulator`. A separate Tauri dev-mode build with the unique config identifier has an embedded plist containing name/version but **no** CFBundleIdentifier. The unique app-level Application Support, Caches, Logs, Preferences and WebKit paths were absent on read-only precheck, but the actual OS/WebKit choice between bundle, embedded and executable-name identities and shared XPC/cache writes has not been established. Neither candidate was launched, no HOME was changed, and no existing WebKit directory was touched. GUI verification requires a safely isolated and sandbox-authorized native launch, with actual store ownership and normal close/reopen confirmed; this remains for fresh Verification / coordinator assessment.

An additional unlaunched exploration used `TAURI_CONFIG='{"identifier":"com.aiis.aw.ds004.g6mp7m","build":{"devUrl":"http://127.0.0.1:45294"}}' CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-native-unique CARGO_NET_OFFLINE=true cargo build --manifest-path src-tauri/Cargo.toml --features native-s7 --locked --offline` in the same snapshot: exit 0. The temporary `DS004-dev.app` wraps the resulting Mach-O without changing it (`cmp` exit 0; SHA-256 `786649e4166c994830665113ee13c899d4e4f2f3e96e5a7bd6e737ceee971ff1`), with a manually created outer Info.plist containing that unique identifier; the embedded plist still has no identifier. `lsof -nP -iTCP:45294 -sTCP:LISTEN` returned 1 with no listener output at the time, but a future bind must still check for races. A task-owned local static server serving the already built `/private/tmp/ds-004-r1-dev.G6mp7M/ui` would be needed for this devUrl. No server was started, and neither actual WebKit identity nor absence of shared OS writes was proven; this is a candidate for QA to assess, not native UI evidence or permission to bypass sandbox controls.

One attempted `pnpm exec tauri build` from the temporary snapshot exited 1: pnpm unexpectedly attempted a registry metadata GET, then aborted module-directory removal/install because there was no TTY. No dependency was installed. Subsequent builds invoked the existing repository Tauri CLI file directly with Cargo offline. No user profile, real device, PLC listener, deployment, Git commit, or intended network/transport action was used. Creating each new synthetic profile did execute the project's unchanged `0001_initial.sql` **initial database-creation DDL**; no schema modification, migration or existing-profile DDL was performed. This distinction is recorded rather than claiming that no SQL DDL executed at all.

## developer_handoff

Candidate is the uncommitted formal working tree at HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`, plus the exact files and hashes above; there are extensive unrelated pre-existing parallel changes which must not be treated as DS-004. The approved spec hash remains `322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`. Hand off this record, the scoped diff, test output, old binary and owned synthetic profiles to a fresh-context Verification. Native UI and the observed large-payload unknown receipt remain explicit open evidence/risk; Development does not give a QA verdict or Human Owner acceptance. Temporary assets are retained for independent review and can be reclaimed after QA confirms they are no longer needed; do not remove unrelated profiles, application caches or WebKit stores.

## F1 rework and updated developer_handoff

Fresh-context Verification recorded `qa_failed` for F1 in `checklist.md` (observed SHA-256 `d40b62e37348de997eaf7eaaf2c1ea83a9a6d5545214867c5b49eca953f1e86d`). The exact approved spec remains r1 and SHA-256 `322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`. Development did not modify either file.

The rework uses only r1 allowlisted files. `src/console/composables/useDeviceSimulator.ts` retains the submitted workspace and ETag on an unknown save, freezes subsequent save/configuration actions without retrying, and preserves local edits. Stop and pause remain callable; a separate unknown runtime receipt remains visible after save reconciliation. A read-only check fetches draft, revisions and selections into a separate snapshot. Explicit confirmation is allowed only when both current local content and the saved content match the submitted snapshot; it re-reads ETag and workspace immediately before releasing the freeze. A changed ETag, local edit, open editor or read failure keeps the freeze. The existing explicitly confirmed **Reload draft** is permitted only after inspection and only if local content did not change while the read was in flight; its existing confirmation explains that it discards local edits. Subsequent writes still use the normal ETag CAS. If a known save acknowledgement is followed by failed readback or intervening local edits, the same conservative reconciliation applies.

`src/app/simulator/views/points/index.vue` supplies the read-only recovery entry and displays the saved ETag, latest/selected version and the selected DB page's saved bilingual names/descriptions alongside the still-local draft. `src/styles/app.css` preserves whitespace in that readback. Paired locales replace the misleading generic failure and explain from any page how to reach the check; they distinguish draft readback from runtime/value refresh and warn against resubmission. Both user guides and the existing module index describe the behavior. Neither `App.vue` nor `ConfigRevisionBar.vue` was modified. The retained in-memory draft is not a durable recovery journal: closing or crashing can lose changes that have not actually persisted, as the UI says.

### Rework DEV self-check

All commands ran from `automation-world/device-simulator`; synthetic profiles and Cargo target remain under the existing Development-owned `/private/tmp/ds-004-r1-dev.G6mp7M`, with new rework data in its `rework/` subdirectory. The existing project schema initializes new synthetic databases; no schema file, migration or real profile was changed.

```sh
set -o pipefail
CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/rework/rust cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names committed_save_receipt_fault_emits_real_readback_for_ui_reconciliation -- --nocapture | tee /private/tmp/ds-004-r1-dev.G6mp7M/rework/fault.log
# exit 0: explicit after_save_commit injection, 1 passed
DS4_FAULT_LOG=/private/tmp/ds-004-r1-dev.G6mp7M/rework/fault.log node --test tests/*.test.mjs
# exit 0: 31 passed, 0 skipped; includes actual fault envelope through the real TS IPC facade and real Vue state with an in-memory invoke boundary
CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/rework/regression cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract
# exit 0: 20 passed, 1 explicitly ignored compatibility probe
CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/rework/no-feature cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names
# exit 0: 3 passed, 1 explicitly ignored compatibility probe
cargo fmt --manifest-path runtime/Cargo.toml --check
# exit 0
pnpm exec vue-tsc --noEmit && pnpm exec vite build --outDir /private/tmp/ds-004-r1-dev.G6mp7M/rework/ui
# exit 0; existing Rollup PURE annotation and >500 kB chunk warnings
```

The controlled fault emitted `result=unknown`, `errorCode=save_receipt_unknown`, `committed=null`, `receiptState=unknown`; the actual service readback had ETag `1489fccf-8866-4404-b7ee-22575bf1c08c`. An independent read-only SQLite inspection of the owned fault profile found `quick_check=ok`, matching payload SHA, the committed `故障注入` / `Synthetic fault` values and `explicit` description, zero revisions, and DB SHA-256 `f160ea1438aa7ce2c19870bdfde49a229640fbf9eac99dd25a1c4bce1616e6c2`. The Node bridge consumes that real envelope and saved workspace, but substitutes the Tauri invoke boundary; it is not a native GUI or real Tauri IPC test. An earlier version of the new asynchronous test exited 1 because its test harness assumed two microtasks were enough to reach the readback; replacing that assumption with an explicit test barrier produced the passing result above.

After the earlier 4,096-point unknown result was reconciled read-only, an additional no-feature helper `/private/tmp/ds-004-r1-dev.G6mp7M/rework/capacity_readback.rs` linked against the new product runtime. It opened that owned profile, called `queries::configuration` once, and shut down: exit 0; open 368 ms, configuration query 1,263 ms, actual ETag `a4fe1050-c25c-4c59-929b-31cf66036d00`, 4,096 points and one version. DB SHA-256 was `15cfde5be6d26ffecf2150a76ea83353b15cca43cc3bffadd8e94a04741c07b2` before and after. No save was retried. This single run does not guarantee future latency or remove the existing unknown-receipt possibility.

Scoped tracked `git diff --check` exited 0; relative-file link scan of the two guides and module index exited 0 for 41 links (anchors not checked). New-file `git diff --no-index --check /dev/null` emitted no whitespace diagnostics and returned 1 for differing files. Original QA failure remains in `checklist.md`; this is Development evidence, not a QA verdict.

### Updated exact candidate

The formal, uncommitted working tree is still `/Users/jason/Desktop/DreamCode/aiis-ics-arch` at base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`. Unrelated pre-existing and parallel changes, including DS bootstrap and earlier guide edits, remain present and are not part of this task. The task files relative to `automation-world/device-simulator/` and their current SHA-256 are:

```text
22331f7649a5849102cc919f8441dfbf9f472b54e43a806a3831e7426d0b75e4  runtime/src/domain/configuration.rs
e4e365fa9f7411fb9ac5fb58dbdc478fd62ee0e4d7bcdbaba81761f4266a9dec  runtime/src/services/source_import.rs
d30e505d7cb73e7f9989109dcd8523264ce59da9a9d902928d08a21f84380c6d  src/services/deviceSimulator.ts
ac5fbd56654c7e694d7f70078d6a1944a79b295d386b847ba2d519d97a084dd2  src/console/composables/useDeviceSimulator.ts
18285666ee42e9f36bd1b6a29f184abfbe35ddb403b576a050106e8aa76d36f8  src/app/simulator/views/points/index.vue
ef57a7f010506377b9155822ccacc5eff44aa110fcb67817984e8b0520e21079  src/app/simulator/components/PointEditor.vue
2bf4bba796318017bd73f8254354ec59f9d408c2cbc8e1e27f82d71342290dc7  src/app/simulator/locales/en-US.json
bec676350e5ad2ca923b240b1fd9e3913a2de7c07199ea46edf0ac3173b9b2c7  src/app/simulator/locales/zh-CN.json
9df2585577b81f809b7c87a4e9d01d72f1ac95db0d48b069ffcd24f9c2adc178  src/styles/app.css
c446666534009d535742a79a6fb54affc1556db04f3f89d153924516ff4f24e5  runtime/tests/point_display_names.rs
cfeaf3e0f75751e823afee4414e26908df56662c1e8fcac0fa6bd91fa77b542a  tests/point-display-names.test.mjs
b1537c4cf334720b03fdd7f479a5a2a418bdae619e84f0c72a7a7ed08deccbb4  USER_GUIDE.md
2bda17d12585331a48780fe95b3ab53f61d4586aecc6e66c527edda867b44f94  USER_GUIDE.zh-CN.md
99fede9dc32b63956fc46d813404c79fb3709c204303cc9f6efb8b252d2dc816  CODE_INDEX.md
```

Fresh Verification must assess this updated candidate and F1, including the controlled fault evidence and concurrency behavior. Native macOS UI, actual top-bar interaction, restart column-width persistence/reset and ordinary Tauri startup remain unexecuted. The earlier temporary native binaries and UI assets predate F1 and must not be treated as the updated candidate. The task-owned profiles, fault log and build outputs are retained for independent review; clean only after QA confirms they are no longer needed. No native window, DAA UI, real profile/device, deployment or network delivery was operated in rework. No QA verdict, final acceptance or future import/export authorization is asserted here.

## F2 rework and current developer_handoff

Fresh-context QA2 recorded F2 `qa_failed` after verifying F1. Its preserved `checklist.md` SHA-256 is `a122c57cfbb5d0cb9b74b45d9b0786ddd5cfed9c3cdb9fea268e6ad01ea88f10`; the `owner_approved` r1 spec remains SHA-256 `322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`. Development did not edit either document. Earlier `developer_handoff` candidates and both QA histories remain above and in the checklist; their candidate hashes are superseded by the following list.

Within the r1 allowlist, `src/console/composables/useDeviceSimulator.ts` now retains every unresolved stop/pause unknown receipt with its instance, requested operation, epoch and loaded revision. Known rejections, a successful or failed background snapshot, and separate draft-save reconciliation cannot erase these records. Stop and pause remain callable; other state-changing actions and saving are blocked while a save or control receipt is pending. Existing unrelated unknowns encountered before or during a safety operation, including an unknown preview-release response, remain unknown after control/save confirmation; background version and log reads do not clear that retained result. No operation is automatically retried. Existing local edits are preserved and the existing save ETag/concurrency checks remain in force.

The points page lists unresolved control receipts and offers an explicit, read-only current-runtime check. The user may acknowledge the displayed facts only after that check; confirmation re-reads every affected instance and requires the same current state, epoch, loaded revision and no intervening stop/pause attempt. Unavailable, missing, duplicate, stale or invalid facts keep the receipts and freeze. A current unloaded or load-failed state is shown as such. This comparison does **not** establish whether any prior unknown stop/pause succeeded or failed; an instance removed from the current snapshot cannot be acknowledged by this flow until it reappears. These records exist only in this window, and the bilingual UI explicitly warns that closing discards them. This is a bounded in-memory recovery aid, not a durable operation journal.

### F2 DEV self-check

All commands ran in the formal `automation-world/device-simulator` working tree on the environment recorded above. Cargo targets and profiles are task-owned and isolated; no GUI, CUA or DAA application was started or attached. The frontend build consumed the formal current tree directly, not a temporary source snapshot; its `vite.config.ts` has `envDir: false`, and build output went to the task-owned `/private/tmp` directory. No dependencies were installed.

```sh
CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/f2/fault cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names committed_save_receipt_fault_emits_real_readback_for_ui_reconciliation -- --nocapture > /private/tmp/ds-004-r1-dev.G6mp7M/f2/fault.log 2>&1
# exit 0: one real service after_save_commit fault; 1 passed
DS4_FAULT_LOG=/private/tmp/ds-004-r1-dev.G6mp7M/f2/fault.log node --test tests/*.test.mjs > /private/tmp/ds-004-r1-dev.G6mp7M/f2/node-final.log 2>&1
# exit 0: 35 passed, 0 skipped
pnpm exec vue-tsc --noEmit > /private/tmp/ds-004-r1-dev.G6mp7M/f2/types-final.log 2>&1
# exit 0; an earlier initial run exited 2 on inferred stop/pause command type, corrected before this run
node node_modules/vite/bin/vite.js build --outDir /private/tmp/ds-004-r1-dev.G6mp7M/f2/ui-final > /private/tmp/ds-004-r1-dev.G6mp7M/f2/build-final.log 2>&1
# exit 0; existing dependency PURE annotation and >500 kB chunk warnings
cargo fmt --manifest-path runtime/Cargo.toml --check
# exit 0; Rust implementation is unchanged in F2
git diff --check -- runtime/src/domain/configuration.rs runtime/src/services/source_import.rs src/services/deviceSimulator.ts src/console/composables/useDeviceSimulator.ts src/app/simulator/views/points/index.vue src/app/simulator/components/PointEditor.vue src/app/simulator/locales/en-US.json src/app/simulator/locales/zh-CN.json src/styles/app.css USER_GUIDE.md USER_GUIDE.zh-CN.md CODE_INDEX.md
# exit 0
git diff --no-index --check /dev/null tests/point-display-names.test.mjs
git diff --no-index --check /dev/null runtime/tests/point_display_names.rs
# each exit 1 because the file differs from /dev/null; no whitespace diagnostics
```

The new Rust fault produced `result=unknown`, `errorCode=save_receipt_unknown`, `committed=null`; ETag changed from `9f61f83e-b381-4447-920f-ceb63a840a75` to `8e332afd-f02d-4f3d-a08d-b39cb0479a68`. After process exit, Python `sqlite3` in `mode=ro` confirmed `quick_check=ok`, committed bilingual values and description, zero revisions, actual payload SHA-256 `3fc184eb493f560143c3ced348eccef196e4676506a9c5d9ff850ffaad082ee7`, and identical database SHA-256 before/after `c73884f87ba55cbed2d0a78ccdf4802c9418655d50402b7d174b9d667fb86723`. The explicit single-save fault log SHA-256 is `c30583e31cae66cc24adc2f157f1a0a95d7e22e25204a3645a002fdfc280d11b`. The Node regression feeds that real Rust envelope and saved draft through the formal TS IPC facade and Vue state, with a **synthetic** invoke boundary for stop unknown followed by pause known rejection; it verifies the stop remains visible and saving blocked after save acknowledgement. It is not native Tauri IPC.

Additional Node tests cover multiple instances and receipts, known rejections, background refresh, save/control acknowledgement in both orders, unrelated apply/preview unknowns, non-point-page recovery, unchanged local draft, missing/duplicate/stale/malformed snapshots, current state/epoch changes, a safety request during confirmation, explicit confirmation, bilingual key parity, and points-page in-memory rendering. The initial older-log Node run also exited 0 with 35 passed; the final run above consumes this F2 fault. Prior F1 Rust regression, no-feature tests, compatibility probes, large-payload unknown and read-only reconciliation remain recorded above; Rust product code did not change in F2.

### Current exact candidate

Formal uncommitted working tree `/Users/jason/Desktop/DreamCode/aiis-ics-arch`, base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`. These full-file hashes identify the candidate, not authorship of every pre-existing line. Relative to `automation-world/device-simulator/`:

```text
22331f7649a5849102cc919f8441dfbf9f472b54e43a806a3831e7426d0b75e4  runtime/src/domain/configuration.rs
e4e365fa9f7411fb9ac5fb58dbdc478fd62ee0e4d7bcdbaba81761f4266a9dec  runtime/src/services/source_import.rs
d30e505d7cb73e7f9989109dcd8523264ce59da9a9d902928d08a21f84380c6d  src/services/deviceSimulator.ts
6c973a4996aaeed89a1b2fc62e66e97f58d1161b0a697bdd09e21bd6d4a30296  src/console/composables/useDeviceSimulator.ts
d8f2571ad0d5d079484a543e394ed11bd990e5dc2d9a8162e3743661c73c7ef6  src/app/simulator/views/points/index.vue
ef57a7f010506377b9155822ccacc5eff44aa110fcb67817984e8b0520e21079  src/app/simulator/components/PointEditor.vue
a7b2d592732172f36b50e05663b3626e3e5ca3f8cbfd0a64b63fa0903f99e565  src/app/simulator/locales/en-US.json
6afe38663306d250524aba4f49e7dae4d796154ba00f2c39150d186a1540bc7b  src/app/simulator/locales/zh-CN.json
9df2585577b81f809b7c87a4e9d01d72f1ac95db0d48b069ffcd24f9c2adc178  src/styles/app.css
c446666534009d535742a79a6fb54affc1556db04f3f89d153924516ff4f24e5  runtime/tests/point_display_names.rs
1ffe9d05c4a5e67b5591eb4bf86c4d32902adf9721e37d1a19dd6e0a859f28ff  tests/point-display-names.test.mjs
b1537c4cf334720b03fdd7f479a5a2a418bdae619e84f0c72a7a7ed08deccbb4  USER_GUIDE.md
2bda17d12585331a48780fe95b3ab53f61d4586aecc6e66c527edda867b44f94  USER_GUIDE.zh-CN.md
99fede9dc32b63956fc46d813404c79fb3709c204303cc9f6efb8b252d2dc816  CODE_INDEX.md
```

The F2 edits were confined to the composable, points page, paired locales, the existing task test and this Development `tasks.md`; pre-existing parallel changes were retained. Handoff this exact candidate and evidence for fresh-context Verification. DS4-07 real macOS UI, real top-bar language switch, ordinary `pnpm tauri dev`, and native column drag/restart persistence/reset remain **unverified**. GUI/CUA is currently paused by coordinator because of a separate DAA isolation incident; resumption requires its explicit release and an independently demonstrated isolated environment/profile/OS storage as described above. Do not treat old native binaries or previous UI outputs as this candidate. The 4,096-point save timing/unknown risk and read-only reconciliation remain open evidence for QA, not a claim of capacity failure or a reason to retry. `/private/tmp/ds-004-r1-dev.G6mp7M` and its `f2/` logs, isolated Cargo target, build outputs and synthetic profiles are retained for independent verification; reclaim only after QA/coordinator confirms no evidence or process dependency, without touching other tasks' assets. New synthetic database creation used the existing initial schema, not a migration or DDL against a real profile. No QA verdict, Human Owner acceptance, physical device/network action, deployment or release is asserted by Development.

## DS-004 r2 Development and developer_handoff

Exact active spec `owner_approved` SHA-256 `c3e719d6373c70d4fe45df289a26cd83f104e88878b74693900f76533509c267`; parent ARCH-PLC-001 r4 `owner_approved` SHA-256 `7b2c37a6aa37ffcd03403a435c106da5c3a9f81e12b3a2ffcab04f68ec3a11cc`. QA3 `qa_failed` checklist SHA-256 `057624c3e55f2a6ea4de896479c8140d499f6c0e21024eb2db7f6af3d7c7c5b9` remains unchanged; r1, QA1–QA3 and earlier handoffs remain above/in that checklist. The candidate is the formal uncommitted `/Users/jason/Desktop/DreamCode/aiis-ics-arch` working tree at base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`; other existing and parallel edits were retained. `src/App.vue` had no tracked diff when r2 began. r2 product edits were confined to `src/App.vue`, `src/services/deviceSimulator.ts`, `src/console/composables/useDeviceSimulator.ts`, the points page, the paired locale files and the two task guides; r2 tests extend the two existing DS-004 test files. No Tauri Rust, configuration, dependency, lock, DDL or other module was changed.

### Implemented behavior and boundaries

- A save retains the submitted workspace, original ETag and a copy of `confirmPoints`. It distinguishes known saved, known unchanged, known rejection, service receipt/commit unknown, runtime-task unknown, transport unknown, and known save with failed readback or unproven removal cleanup. A successful save whose later read sees a different ETag does not replace the local submission. Transport and runtime-task unknown cannot be unlocked by matching reads or by manually reloading; the user may inspect current facts, retain the window, or explicitly discard the in-memory records and attempt normal close. There is no automatic retry, persistent operation ledger or automatic restart.
- A normal service `save_receipt_unknown`/`save_commit_unknown` came from `queries::save` after `Store::request` accepted a job. Source inspection shows `try_send` precedes its timeout, and the single worker consumes that queue serially; a subsequent successful configuration Load from the same application Store therefore follows that job. A controlled `after_save_commit` service fault and explicit thread/channel ordering exercise this case. The read is current state, not proof of historical success/failure. When the submission removes an instance and cleanup cannot be proven, protection remains. The controlled fault is not a natural timeout; `save_commit_unknown`, task-join and transport responses are also exercised at a synthetic JS/IPC boundary, not by forcing an actual SQLite commit failure or Tauri JoinError.
- The point page shows saved ETag, selected/latest revision, submitted confirmation IDs, saved instance/DB/point confirmations and per-field differences against local inputs. A service candidate may differ because confirmation signatures were legitimately recomputed. Explicit reload is allowed only after differences are shown, the local draft still matches the inspected local snapshot, and a fresh read matches the inspected ETag/content; its existing confirmation explains discarded local edits. Related stop/pause receipts are individually retained and current facts are explicitly reviewed without claiming the earlier operation succeeded. F2's general standalone control-recovery behavior was withdrawn; QA3 F3's no-save-intersection legacy behavior is not claimed fixed.
- Preview release calls are tracked while in flight; unknown releases directly intersecting a save or the close gate remain separate and visible. A token may still protect a reference; timeout/expiry is not presented as proof of release. `App.vue` and the composable implement a **single-window frontend** close gate: while a decision is being made new releases are held as unsent, in-flight/unknown facts are shown, changed facts require renewed explicit discard, Cancel restores the window and sends only formerly unsent releases, and save-close does not silently close on a pending/unknown release. Known save success remains visible separately. The gate ends at sending the close decision; it does not prove native closure, IPC atomicity, crash safety or across-restart persistence.

### r2 Development self-check

Commands ran from the formal `automation-world/device-simulator` directory on macOS 15.7.7 / Darwin 24.6.0 arm64, Rust/Cargo 1.89.0, Node v22.19.0, pnpm 11.11.0. `CARGO_TARGET_DIR` is this Development's pre-existing isolated target, and all new profiles/logs/UI output are inside its task-owned `/private/tmp/ds-004-r1-dev.G6mp7M/r2/`. Vite's existing configuration has `envDir: false`; the final build used the formal source directly. No dependencies were installed.

```sh
CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/r2/full cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract -- --nocapture > /private/tmp/ds-004-r1-dev.G6mp7M/r2/rust-full.log 2>&1
# exit 0: 24 passed, 2 explicitly ignored probes; log SHA-256 45ff179aa37d9b331a70d2d74e0f090b1ac264a91b7745cdc05202877c189dcf
CARGO_TARGET_DIR=/private/tmp/ds-004-r1-dev.G6mp7M/cargo-new DS_TEST_RUN_ROOT=/private/tmp/ds-004-r1-dev.G6mp7M/r2/no-feature cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names > /private/tmp/ds-004-r1-dev.G6mp7M/r2/no-feature.log 2>&1
# exit 0: 5 passed, 2 explicitly ignored probes
DS4_FAULT_LOG=/private/tmp/ds-004-r1-dev.G6mp7M/r2/rust-full.log node --test tests/*.test.mjs > /private/tmp/ds-004-r1-dev.G6mp7M/r2/node-final.log 2>&1
# exit 0: 48 passed, 0 skipped; Tauri invoke and App close event are in-memory test boundaries
node node_modules/vue-tsc/bin/vue-tsc.js --noEmit > /private/tmp/ds-004-r1-dev.G6mp7M/r2/types-final.log 2>&1
# exit 0
node node_modules/vite/bin/vite.js build --outDir /private/tmp/ds-004-r1-dev.G6mp7M/r2/ui-final > /private/tmp/ds-004-r1-dev.G6mp7M/r2/build-final.log 2>&1
# exit 0; existing dependency PURE annotation and >500 kB chunk warnings
cargo fmt --manifest-path runtime/Cargo.toml --check
# exit 0
git diff --check -- runtime/src/domain/configuration.rs runtime/src/services/source_import.rs src/App.vue src/services/deviceSimulator.ts src/console/composables/useDeviceSimulator.ts src/app/simulator/views/points/index.vue src/app/simulator/components/PointEditor.vue src/app/simulator/locales/en-US.json src/app/simulator/locales/zh-CN.json src/styles/app.css USER_GUIDE.md USER_GUIDE.zh-CN.md CODE_INDEX.md
# exit 0
git diff --no-index --check /dev/null runtime/tests/point_display_names.rs
git diff --no-index --check /dev/null tests/point-display-names.test.mjs
# each exit 1 because the new file differs; no whitespace diagnostics
```

An initial in-progress type check exited 2 on TypeScript closure inference and an initial Node run exited 1 with 28 passing/7 failing because the r1 test fixtures and assertions did not yet reflect r2; both were corrected and the final commands above passed. A stdlib link scan of both guides and module index exited 0: 41 file links checked, none missing; anchors were not checked. Node exercises the real Vue state/facade and App script in an in-memory renderer, including two equal reads followed by a delayed synthetic save with nonempty `confirmPoints`, service unknown comparisons, concurrent ETag and local edit guards, save/stop/pause and preview interleavings, known save versus unknown release, deferred close-gated releases, cancel, changed-fact re-confirmation and explicit discard. These are not real WebView/Tauri close or native IPC tests.

The real synthetic Rust service test with `confirmPoints` and `after_save_commit` observed changed initial/policy confirmations and invalidated address/naming confirmations while preserving the bilingual metadata. Its separate FIFO test waits on an explicit channel for the service unknown, joins the test thread and reads the same Store/profile; the first read reflects the test's committed state. This demonstrates the exercised fault case and source ordering, not every production timeout or a durable receipt. The subprocess test holds a fresh synthetic Store profile lock, confirms a competing open is `profile_in_use` while the child lives, requests normal test-process shutdown, waits for the child to exit, and reopens the same profile UUID. It does not test actual native app close, crash, forced exit, failed close or automated detection of an arbitrary wrong user profile; those remain unverified.

The separate non-feature capacity command used a fresh task-owned profile, exactly 4,096 points with each display name 256 UTF-8 bytes and description 500 bytes; serialized payload was 5,926,517 bytes. One actual `queries::save` returned known `saved`, ETag `08c0fbb6-5ca3-420f-9087-13722c6ffcb3`, and readback matched. The same test rejected 4,097 points as `point_capacity` and a synthetic workspace over 16 MiB as `configuration_capacity` before that save, preserving the original draft/ETag. A subsequent SQLite `mode=ro` check of `/private/tmp/ds-004-r1-dev.G6mp7M/r2/capacity/ca53f318-a494-4f7b-b737-2be9ef31e314/device-simulator-v1/config.sqlite` found `quick_check=ok`, all lengths correct, payload SHA-256 `9b080adb0df1a88a4cbff179bfee7154fb9661fb5120569362840dfaf087577b`, and unchanged DB SHA-256 before/after read `3c931b21009b2638776623c1d2076b9869d202f6d40e51ad2d9398117681619a`. The earlier 4,096-point unknown receipt and committed readback remain recorded above; neither single observation predicts all timing.

For a new synthetic `/private/tmp/ds-004-r1-dev.G6mp7M/r2/compat` profile, the old executable SHA-256 `70589d62bd2708f3c0a0276cfb5c86280473358e9e636bf086dcfc2d0e70eb4a` and new no-feature executable SHA-256 `923c452a2f1e84bab252c3cfd98e002d6921e7d96dae66e4bca56f68cef2e8e5` each ran `--ignored --exact compatibility_probe --nocapture`. Sequence `old/create`, `old/old`, `new/old`, `new/upgrade`, `old/reject` used `DS4_COMPAT_PROFILE` set to that path and `DS4_COMPAT_MODE` set to the shown mode; all five exit 0. After old/new old-format reads, whole DB SHA was `5c5734ac328e54c8814cfacfd838ce70160c652f184c3c39b8f38a359455a762`. After explicit new-format upgrade, old binary rejected with expected `storage_payload`; before/after rejection DB SHA remained `3a510565e49fb8e2bcd0c2f49a1a3f8dd16f97eed85c01700a0f69e107caf7f9`. Old binary identity is the Development-retained baseline, not a signed build.

### r2 exact candidate files

These full-file hashes identify the candidate; they do not attribute all pre-existing lines in shared files to this task. Paths are relative to `automation-world/device-simulator/`:

```text
22331f7649a5849102cc919f8441dfbf9f472b54e43a806a3831e7426d0b75e4  runtime/src/domain/configuration.rs
e4e365fa9f7411fb9ac5fb58dbdc478fd62ee0e4d7bcdbaba81761f4266a9dec  runtime/src/services/source_import.rs
d12189cf22eb535209c7fd9f49b7f3b712fb5114fad7b5cc6c1aa33713583de0  src/App.vue
2d92f3271e30853405c8b695181266c06fb408246af89a2f81bc38fc77c2b7b8  src/services/deviceSimulator.ts
1b0c1d3fe7048c49323097dc243357499304e05181c1fc334ac6f9e79d5622c9  src/console/composables/useDeviceSimulator.ts
8dedf40f3a2e2cff695183f51004a63b8e8c42d10ba56bdc62d306db38a91541  src/app/simulator/views/points/index.vue
ef57a7f010506377b9155822ccacc5eff44aa110fcb67817984e8b0520e21079  src/app/simulator/components/PointEditor.vue
6cb460e560ea4e4238694f7087bc6dc19cc01c09b1194b74a99b7879d7badee0  src/app/simulator/locales/en-US.json
a987d9cb655e36007008c80151497d27cdff67d2f18ad9d9efeec0db4a5796de  src/app/simulator/locales/zh-CN.json
9df2585577b81f809b7c87a4e9d01d72f1ac95db0d48b069ffcd24f9c2adc178  src/styles/app.css
c2426485fb919496a1573ac1202309db57cd993e0df9313e8a85807cdac3a7e5  runtime/tests/point_display_names.rs
7200291077ad2964a04b443dbc5bb0fae1f249e2989b08221493e56b27f61ff8  tests/point-display-names.test.mjs
428247b6cb7e2f35b558b84890eaf8cf72717853a5cd369d4793d1a3ec269640  USER_GUIDE.md
083efe4ab5047268106e6c2b44eae4d1a2b7b9d0d51bd6df6c274e8ee86d3ae6  USER_GUIDE.zh-CN.md
99fede9dc32b63956fc46d813404c79fb3709c204303cc9f6efb8b252d2dc816  CODE_INDEX.md
```

This is `developer_handoff`, not a QA verdict or Human Owner acceptance. Fresh-context Verification must assess this exact candidate, especially the limited close gate, FIFO proof and late/unknown branches. DS4-07 actual macOS UI/top-bar/column resizing and restart/reset, ordinary `pnpm tauri dev`, and native close/reopen remain unexecuted. GUI/CUA remains paused due to the separately recorded DAA isolation event; do not use old pre-r2 native binaries as evidence. The task-owned `/private/tmp/ds-004-r1-dev.G6mp7M/r2/` profiles, logs and output and the earlier task-owned target/compatibility artifacts remain for QA; reclaim only after coordinator/QA confirms no evidence or running-process dependency. Newly created synthetic SQLite profiles used the unchanged initial schema only; no user profile, existing database migration, real PLC, external delivery, import/export, deployment or release occurred.
