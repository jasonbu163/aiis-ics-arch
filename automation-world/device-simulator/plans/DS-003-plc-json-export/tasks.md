Task ID: DS-003
Revision: r5
Status: developer_handoff
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Owner Role: Development
Allowed Writers: Development
Handoff: DS-003 r5 QA1-F01 rework and exact new working-tree candidate below -> new fresh-context Verification; earlier QA1 failure and native limitations remain recorded.
Approved spec SHA-256: `9adf299af89711855be896938cf7e6148f4332e171a984aebf10dd32d7c6cd89`
Working tree: `/Users/jason/Desktop/DreamCode/aiis-ics-arch`, base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`, with extensive pre-existing/parallel uncommitted work.

# Development record

- 2026-11-17 (Asia/Shanghai): the Human Owner approved ARCH-PLC-001 r5, DS-003 r4, DAA-017 r4 and the downstream sequence, including controlled use of the applications' own `.local/dev`. Development verified the recorded DS-003 r4 spec SHA-256 `89ce0e468312e013003f796909765bf94d08d3b6cf07d4d36fd0439aa96699a3` before its work. The bundle then contained only the spec.
- During r4 implementation, safe conditional replacement of an existing pathname could not be guaranteed by a check followed by overwrite. PM submitted a narrower r5; the Human Owner explicitly approved both DS-003 r5 and DAA-017 r5. Development re-read the approved r5 and verified the SHA above. r5 preserves the other scope and rejects an existing destination instead of overwriting it. The dual-name tasks' existing QA and Owner status are unchanged.
- Root and nearest applicable repository rules, canonical lifecycle workflow, project/AW/DS guidance, active parent and related importer contracts, and relevant code were read. Applied `aiis`, `plc-point-mapping`, `rust-runtime`, `desktop-tauri`, `frontend-ui`, `i18n-workflow` and `code-document-indexer`. Tauri's [official dialog documentation](https://v2.tauri.app/plugin/dialog/) and local pinned crate were consulted. No shared skill was modified.
- Parent coordination reserved AW/DS PLAN and catalog indexes to the coordinator. DS-004 already changed several shared DS files and other workstreams were dirty at start; this task preserves those changes and does not attribute entire shared-file diffs to DS-003.

## Implemented candidate

Paths are relative to `automation-world/device-simulator/`:

- `runtime/src/infrastructure/config_store/{mod.rs,queries.rs}` reads one saved revision's original payload bytes, stored SHA, metadata and validated source references from the same row. `runtime/src/domain/plc_catalog.rs` validates and builds the exchange document from that revision, including disabled DBs and points, independent old/bilingual names and description, S7 layout, client target and TSAP values. `runtime/src/services/catalog_export.rs`, `runtime/src/{app.rs,domain/mod.rs,services/mod.rs}` add bounded expiring previews, actual selected/loaded state, directory-bound temporary authorization and per-instance output receipts. Previews and export do not save/apply the configuration or start/stop instances.
- `src-tauri/src/{lib.rs,commands/mod.rs,commands/catalog_export.rs}` registers the native picker and thin IPC; frontend requests contain a short-lived token, never a destination path. `src-tauri/Cargo.toml` pins `tauri-plugin-dialog = 2.7.2` with default features off. The Cargo lock update adds its 14 package dependency closure and necessary feature/dependency references; no existing package version was upgraded and no npm package was added.
- `src/services/deviceSimulator.ts`, `src/app/simulator/views/instances/index.vue`, `src/app/simulator/components/CatalogExportDialog.vue`, paired simulator locale JSON and `src/styles/app.css` provide revision and instance selection, endpoint confirmation, loaded-version and TSAP notices, full-point preview, native folder selection, conflict rejection and per-file results. The preview table reuses the shared column preference component.
- New `runtime/tests/plc_catalog_export.rs` and `tests/plc-catalog-export.test.mjs`; updated `README.md`, `README.zh-CN.md`, both `USER_GUIDE` files, `CODE_INDEX.md`, both `runtime/README` and both `tests/README` files. Guide §7 contains scoped `.local/dev` preparation, export, SHA comparison, same-file DAA handoff and safe cleanup steps. The guide explicitly distinguishes instructions from native/joint evidence.
- No source change was made to DS-004's `runtime/src/domain/configuration.rs`, `runtime/src/services/source_import.rs`, point UI or its own task documents. No `.env`, schema, migration, pnpm dependency/lock, DAA/FF source or other task record was changed by this Development role.

## DEV self-check — observed so far

Host: macOS Darwin arm64, `rustc 1.89.0`, `cargo 1.89.0`, Node `v22.19.0`, pnpm `11.11.0`. Commands ran from the formal DS directory; `/private/tmp/ds003-dev.Zc2maS` is this task's own isolated build/test root. No dependencies were installed.

| Command | Actual result |
| --- | --- |
| `DS_TEST_RUN_ROOT=/private/tmp/ds003-dev.Zc2maS/profiles CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --test plc_catalog_export` | Exit 0; 9 passed after the final fixes. Includes missing/null/fractional/noninteger endpoint fields isolated per instance while a valid second instance exports, a real synthetic TIA source import, saved source paths and independent description, as well as saved bytes/SHA and draft isolation; bilingual, legacy, description and disabled data; invalid connection/addresses and loaded confirmation; non-default TSAP; existing, late-created and symlink targets; directory replacement, revision deletion and repeated concurrent confirmation. |
| `DS_TEST_RUN_ROOT=/private/tmp/ds003-dev.Zc2maS/regression CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test configuration_store --test source_import --test versions --test owner_contract` | Exit 0; 16 passed. Synthetic existing configuration/store, source-import, version and owner regressions; the owner snapshot case explicitly runs without a protocol listener. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --lib exclusive_link_distinguishes_conflict_from_other_write_errors` | Exit 0; one errno classification unit test passed (7 unrelated tests filtered). EEXIST is target conflict; EPERM/EIO/unknown are write failures. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7 --lib catalog_receipt_retains_partial_rows_and_reports_unknown` | Exit 0; one native bridge unit test passed (one unrelated test filtered). A partial receipt retains its rows while the top-level committed state remains unknown. |
| `node --test tests/plc-catalog-export.test.mjs tests/point-display-names.test.mjs` | Exit 0; 33 passed, 1 skipped. Four are DS-003 in-memory component tests; DS-004's optional fault-log test was skipped because its explicit fixture variable was absent. This is not a native WebView or dialog test. |
| `pnpm exec vue-tsc --noEmit` | Exit 0. |
| `pnpm exec vite build --outDir /private/tmp/ds003-dev.Zc2maS/ui` | Exit 0; existing dependency PURE-annotation and >500 kB chunk warnings. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7` | Exit 0 after the numeric and errno corrections; debug binary `/private/tmp/ds003-dev.Zc2maS/target/debug/aiis-device-simulator` SHA-256 `4f5f062ccdca82136f8d826ce87febc640aac4a5f28990ac94f432ab9d10a19a`. This is the isolated build, not a claim about the actual `pnpm tauri dev` process binary. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7` | Exit 0; this checks the real desktop target and plugin dependency, but does not open the native dialog. |
| `cargo fmt --manifest-path runtime/Cargo.toml --check`; `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | Each exit 0. |
| `git diff --check -- <tracked DS-003 candidate files>` | Exit 0; shared files also contain pre-existing work. |
| `git diff --no-index --check /dev/null <each new DS-003 source/test and tasks file>` | Each exit 1 because files differ from `/dev/null`; no whitespace diagnostics. |
| Python stdlib targeted new guide anchor/index-link checks | Exit 0; both guide anchors and six added code index links resolve. This was not a repository-wide link scan. |

After adding the numeric negative test, the first format check exited 1 for an unformatted test array; `rustfmt` was applied to that owned test file and the final runtime and desktop format checks exited 0. The final bridge receipt unit test was rerun after the runtime fixes and exited 0. The coordinator also confirmed the original DS draft instance and source versions matched the saved pre-test baseline before the task-object cleanup.

`cargo metadata --manifest-path src-tauri/Cargo.toml --offline --format-version 1 --filter-platform aarch64-apple-darwin` resolved the pinned dialog's dependency closure without downloading packages. An earlier disposable generic metadata probe without platform filtering exited 101: Cargo attempted to unpack a cached Android dependency under the protected user Cargo registry. The subsequent platform-filtered probe and desktop check succeeded; the temporary probe directories were removed.

After the first candidate freeze, Development found that an all-failed export returned top-level `committed=true` despite individual failures. Before GUI testing, the coordinator stopped the initial DS process and authorized a minimal correction within r5. A wholly failed batch now reports false; a partial/unknown result retains each row and marks the bridge receipt unknown. The export tests were rerun with successful/all-failed receipt assertions, the bridge unit test above passed, four Vue tests passed, and both Rust format checks passed. The candidate hashes below supersede the earlier frozen snapshot.

## Pending evidence and limitations

**Resolved Development issue — file error classification.** The earlier exclusive `linkat` path reported every link failure as a changed target. `EEXIST` represents the target race; unsupported filesystem or other link failures should report a generic write failure instead. The operation remains fail-closed without overwrite. After the coordinator confirmed the window closed, EEXIST was mapped to target conflict and other failures to write failure; the unit test above passed. No overwrite fallback was added.

**Resolved Development issue — client numeric input isolation.** Clearing a port/rack/slot in Element Plus may submit `null` (or a fractional number). The earlier `u32` request deserialization rejected the entire preview before the per-instance validator ran; no file is written, but a separate valid selected instance cannot proceed. This does not affect the current integer-only native mainline. After the coordinator closed the active native window, Development implemented an invalid sentinel that cannot be a valid endpoint, retained per-instance `catalog_connection` errors, and tested missing/null/floating (including `1.0`)/negative/string/bool values alongside a valid second target. The full Rust export suite and isolated desktop rebuild passed. The negative-input native retest was not executed; the fresh ordinary-entry build binary identity is recorded below.

- The coordinated macOS native and same-file local DAA observations, exact candidate identities and their limits are recorded below. The two actual GUI runs used temporary `.app` bundles with byte-identical normal-entry binaries, and are not a claim of full native UI verification under the ordinary entry itself. The empty-port native negative case was not run; the window had closed and the synthetic instances were removed. STRING was covered synthetically, not by either native export. An actual repeat-import rejection was not reported and remains unverified here.
- A source comparison found that the concurrent DAA candidate rejected duplicate DB names while the parent JSON contract requires unique DB numbers, not names; this was relayed to the coordinator and DAA Development. Final importer reconciliation requires that role’s evidence.
- Store revision loading first deserializes and validates the entire saved workspace. Invalid non-integer fields, unknown types or duplicate global IDs cannot be produced by the normal save path; if a stored row is tampered into that unreadable form, the entire revision is rejected before per-instance diagnostics. The individual isolation checks cover invalid states that the store can actually save, not selective recovery of a corrupt revision. This distinction requires Verification against DS03.
- Non-overwrite creation uses a held directory fd and atomic `linkat`, with temporary/target inode and directory checks. Tests cover the listed pre-commit races; they do not establish system-wide resistance to a malicious same-user process replacing the task's temporary filename between its identity check and filesystem syscalls. A directory moved at the publication boundary is reported as an unknown result. Unsupported filesystems must fail rather than fall back to an overwrite. This residual boundary requires independent Verification; no claim of complete system isolation is made.
- This candidate implements the atomic filesystem path for Unix. The explicit non-Unix branch fails closed with `catalog_platform_unsupported`; Windows export behavior and other platforms were not implemented or tested in this slice. The required native target is macOS arm64.
- The task-owned `/private/tmp/ds003-dev.Zc2maS` contains the isolated Cargo target, frontend output and metadata; synthetic test profiles were deleted by the tests. It is retained during ongoing work for possible reruns, then the coordinator should reclaim it only after no running process or evidence dependency remains. No user profile, real PLC, real report, production database or deployment was touched by these automated checks.

## Frozen candidate file identities (original handoff before QA1)

These historical full-file SHA-256 values identify the original candidate received by QA1 after the numeric and error-classification corrections. The QA1-F01 rework candidate is separately frozen below; shared files contain pre-existing work.

```text
7455556c1a5248bd6814d0a8d6f039343eb8bac46ef19ece77443e732e4c9a4e  runtime/src/app.rs
6880949a9383696c8b8c3ac948cf537aa71cdbefc43d3b8b08841cd2fc8a6a8b  runtime/src/domain/mod.rs
7554fc82bafda6c8c764a9f8065c1ea588d7721acaeb5327bb9f13b8c4220a4e  runtime/src/domain/plc_catalog.rs
1a701af378109341fe76a21c91f88ef4e9d8c38a78de35e27b9db2048c9cd473  runtime/src/services/mod.rs
ed0a13c8c84bb195f0663c6066f0eae5364acf82614efeae588388e36ed1c0c3  runtime/src/services/catalog_export.rs
16a86987b010ed26f5138391439924b4ef3855f90f03a72a87eaf98954614469  runtime/src/infrastructure/config_store/mod.rs
92384c280c330f1ee16f7ada4978098c882317ac9cc0b10e822f129ef0277966  runtime/src/infrastructure/config_store/queries.rs
8e3250dc28c7db8b8e67e18ed68d8dd325d524e7d34462ca65e6204166a0e0e1  runtime/tests/plc_catalog_export.rs
8a81729f10da6a8359084410b46f9142d11561bb0c5b730b1ceaa06454cfafa2  src-tauri/Cargo.toml
39f14c514f35cb37ef1844f3e2f23153d737c8fb91a6c108feb3f6efbd244775  src-tauri/Cargo.lock
7e316e861a72ba56ce5e3859f22fdaad03aca7feb08efdf0d7fe750bf44f71ca  src-tauri/src/lib.rs
c7ccc332d8a207ad7c920422d14bbe0e0defe798024165f61ddd87cb5b54bcac  src-tauri/src/commands/mod.rs
c77ec317ce0b7c754d509844079b92ef941df77c4a5d56c19f54fbbcc402f235  src-tauri/src/commands/catalog_export.rs
53a12222035bd381d373363425904fa74340b41f888581e8dbe266c9531538b4  src/services/deviceSimulator.ts
23de7af172012bd854a02121eaa1ebb42df257691d1b7f6b61fd0ce5562092e1  src/app/simulator/views/instances/index.vue
b234b4f0321b404865bc9b3cf0cd995eb2ff1c169966329c8afec59c91a6d37a  src/app/simulator/components/CatalogExportDialog.vue
a98dc54dee8faf1e6c0078a3127a07cf1d37617131467a0e3d750371782471e8  src/app/simulator/locales/en-US.json
dc9044b11482c1cde58caf93402b81d98c8e3fa2b1d450bc13532c2722ae2ad6  src/app/simulator/locales/zh-CN.json
75de72976e060b51dacfedf9bd7a55bbf6ae436472c7c1b77acc47b2788ad0fe  src/styles/app.css
9e875d5772af68b3b70a6c5c54bfe9f563805547d9b0576f4b51fb2df01c2ca4  tests/plc-catalog-export.test.mjs
11c12ecdb37370a49d498f5739f495b61af3d93edcf3b79312126f6d710f05d8  README.md
d93790493c4c76d47a6c113205d81885a29b9666ffc302b13d8801c02e754364  README.zh-CN.md
38eab20bda3ea4127525ec123b1739fad8e4bd00dd231d7a18266c1331745f8d  USER_GUIDE.md
3113d5d2665f42c0e03b78aa1be3aca6398b24dfcdce7acda19b3c7113070c80  USER_GUIDE.zh-CN.md
9c62c5754bef8721993512679ed52abb1329266b22cc9318cd0266abf402714a  CODE_INDEX.md
ab5f8f7211190b1b2a9ae321ecc3c5bf8786cd7f41d13a2298ea8cd3deb42335  runtime/README.md
fb2e5174c98173faf4f650ae530960b17564d5e532f6ce8bf2fc57405fb76939  runtime/README.zh-CN.md
81f4fd0fe8f08b17eee5b39cbafe5d69a7bd5ca8d3d2e4306fa075bb16e4db1f  tests/README.md
03e382faed36c35701811fcb5558cfc56bd14cddce45815076d3a4e4b92785a8  tests/README.zh-CN.md
```

## Coordinated native mainline — preliminary

The coordinator reported these observations on 2026-11-17; Development did not independently reproduce the GUI actions:

- The running DS process PID `88878` reported its configuration database under its own `automation-world/device-simulator/.local/dev/device-simulator-v1/config.sqlite` in startup logs. The normal `pnpm tauri dev` path recompiled and ran the candidate; for CUA discoverability the same binary was copied into a temporary `.app` with a different bundle identifier. The working-tree debug binary and the copy both had SHA-256 `00014f8719d7cab3429f6a18500dda0ec47a4d156efb3148237d40997229f1f2`. GUI observations below were made through that temporary bundle and do not prove native UI operation through the ordinary entry itself.
- In the GUI, saved revision `c17bc82a-1c3d-4dfd-81d5-8c192756a4c4` (v2), instance `9f548342-8640-4d63-bd75-c606881f7e74`, and selected/actually loaded revision matched. The preview showed three synthetic BOOL/INT/REAL points, program names, bilingual values and descriptions.
- Native selection and export produced `/private/tmp/ds003-json-x7cWRU/9f548342-8640-4d63-bd75-c606881f7e74.json`, SHA-256 `40552ff7b0245adb5722c4c61f9b3d50ba75ea5d6741d88b6d478a364bb700cc`. The coordinator retained that exact file for DAA. Three points alone do not establish the STRING/disabled-point matrix.
- Development independently read that coordinator-owned synthetic output without changing it: 2,076 UTF-8 bytes; SHA matched; `format=aiis.plc_points`, `schema_version=1`, `export.payload_sha256=8ec1aca281166a326294559181218c84d54788fe0f60a2c6ddf94f6c11e87b14`, `exported_at=2026-11-17T17:22:00.917+08:00`, one DB and three enabled BOOL/INT/REAL points. Every point contained both display-name keys and a description field. This verifies file observations only, not an independent QA verdict or the DAA import.
- The specifically identified synthetic DS instance ran only on `127.0.0.1:31974` for the authorized local DAA exercise. The coordinator then reported it stopped, all task-owned temporary DS windows exited and the `.local/dev` profile lock released. Before cleanup, a read-only comparison showed the original `DEV-PLC-A` instance and original `sourceVersions` matched the pre-test saved version object by object. The numeric-input issue was repaired after the window/process closed; the preceding native observation belongs to the previous candidate and does not prove the corrected candidate. Subsequent cleanup is recorded below.

- The coordinator subsequently reported that DAA native GUI used this same DS JSON to create a new PLC, assign a group and activate, connecting only the DS synthetic instance at `127.0.0.1:31974`. It observed 18 samples; the last BOOL `false`, INT `0`, and REAL `0.0` values were `good`. DAA was paused/disconnected. The DS instance was still running at that observation and was later reported stopped; cleanup and zero test sample uploads were subsequently reported as below. This is coordinator-observed local integration, not an independently verified verdict.

These are coordinated Development observations, not independent Verification or Human Owner final acceptance. The temporary `.app` and exported file have an active joint-test dependency; do not clean them before the coordinator confirms use and evidence retention are complete.

## Final candidate native retest — coordinated observations

The coordinator reported a second macOS GUI retest after the two source corrections: the normal working-tree `pnpm tauri dev` build produced a DS binary with SHA-256 `851e953d095341b3bd699888fd13bd4b9ddb87d625556ec77b412867d217d1c8`; the temporary test `.app` contained byte-identical code and used DS's `.local/dev`. The GUI observation belongs to that copied temporary bundle, not a claim of complete standard-entry native UI verification.

- Saved v3 revision `3d50439c-fb2b-41bd-9d95-56c67cd98672`, instance `31d327ba-2b97-4f5e-8949-6956ac3a5648`, was exported via native directory selection to `/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json`, file SHA-256 `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`.
- Development independently read the retained synthetic file without changing it: 2,407 bytes, matching SHA and IDs; the declared source payload SHA is `06dc1f3d5c2440fb66dc8af63de92c50ee4bf095e22c6280efd70e2ff60b976b`, `exported_at=2026-11-17T18:24:56.901+08:00`, endpoint `127.0.0.1:31975`. One DB holds source-enabled BOOL 0.0, INT 2 and REAL 4 plus source-disabled BOOL 1.0. All four contain both language keys and the description field. This observation does not verify the source payload against SQLite or cover STRING.
- The coordinator reported that final DAA preview used this same file SHA, created a PLC draft with all four points initially disabled, assigned a group to three and ran 15 local samples. All 15 were `good` and `local_only`; `sample_uploads=0`, with automatic/actual reporting kept stopped. DAA was disconnected and DS stopped. Repeat-import rejection and native negative-input exercise were not reported and remain unverified; safe cleanup was subsequently reported below.

These are coordinated Development observations, not an independent QA verdict or Human Owner final acceptance. The actual file and any retained temporary bundles remain task-owned resources whose retention/cleanup is coordinated separately; do not erase evidence needed by Verification. STRING, adversarial filesystem races, other platforms and old binary compatibility are not proved by this native exercise.

## Cleanup and original developer_handoff (before QA1)

The coordinator reported that both synthetic DS test instances were deleted through the DS UI and the draft saved. A read-only comparison then found the current draft `instances`, `schemaVersion` and `sourceVersions` object-for-object equal to the pre-test v1, with the original `DEV-PLC-A` still selected at v1. DS v2/v3 are test-created saved history; v3 is protected as latest and is retained for QA, while the pre-existing v1 was not removed. Both synthetic DAA PLCs were removed from its draft and that draft saved/activated; the 15+18 samples and related history remain. Reporting was stopped and no test `sample_uploads` existed. Both test applications and development servers exited, and the coordinator reported locks and ports released. These are coordinator-observed operations, not a claim that the full databases or audit logs were unchanged.

`device-simulator::DS-003 r5`, approved spec SHA-256 `9adf299af89711855be896938cf7e6148f4332e171a984aebf10dd32d7c6cd89`, is handed from Development to fresh-context Verification in the dirty working tree `/Users/jason/Desktop/DreamCode/aiis-ics-arch` at base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`. The implemented files and exact 29 full-file hashes, real test commands/results, two separate native candidate identities, retained histories, unrun negative test, read-only corrupt-revision behavior, filesystem race boundary, platform limitations and task-owned temporary resources are recorded above. A final SHA comparison checked all 29 listed files with zero mismatches and rechecked the spec hash. Shared files include pre-existing DS-004 work; Verification must audit the scoped diff without attributing the entire dirty tree to this task.

The two actual JSON files and synthetic test/build root are retained for the next gate; their paths and ownership are recorded above. The coordinator should reclaim only resources it has positively identified as task-owned, once Verification no longer needs the original bytes and no process depends on them. QA must independently assess the approved r5, current source and these results; no QA verdict, final Owner acceptance, release, real device use or external reporting is asserted by this handoff.

## QA1-F01 Development rework and new developer_handoff

2026-11-17 (Asia/Shanghai), fresh-context Verification recorded `qa_failed` in `checklist.md` SHA-256 `d64ce1a93795a82b37907235a58eca00fd909708fb82bfa56e4840b3b7878c18`. QA1-F01 demonstrated that a saved point ID with v4 version bits but an NCS variant was exported as if it were an RFC UUID v4. The approved r5 spec remains SHA-256 `9adf299af89711855be896938cf7e6148f4332e171a984aebf10dd32d7c6cd89`; the original handoff tasks SHA before this rework was `edcab9f2f52d652f502e602f0fe21dc21adc8e208d0aa6a58fcd34fab338c218`. The earlier failure, evidence and candidate identities are preserved above and in the Verification-owned checklist.

Development first added a regression that saves and publishes a synthetic version with disabled point ID `55555555-5555-4555-0555-555555555555`, then previews two instances. Before the code fix, `DS_TEST_RUN_ROOT=/private/tmp/ds003-dev.Zc2maS/profiles CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --test plc_catalog_export qa1_f01_non_rfc_saved_point_blocks_only_its_instance -- --exact --nocapture` exited 101 because no point identity issue was reported; the temporary owned failing profile printed by the test (`/private/tmp/ds003-dev.Zc2maS/profiles/00f52980-44f3-47c8-80a6-b1b472a615ef`) was removed after its process exited. No user `.local/dev` was accessed.

The narrow correction in `runtime/src/domain/plc_catalog.rs` requires canonical lowercase text, version number 4 **and** `uuid::Variant::RFC4122` for the existing shared identity validator. It does not renumber, save, migrate or alter any profile or revision. `runtime/tests/plc_catalog_export.rs` adds the saved-revision/disabled-point reproduction with per-instance isolation and a separate contract test for profile, revision, PLC, DB and point IDs: RFC variant leading hex 8/9/a/b accepted; NCS/Microsoft/future variants, other version, uppercase and compact form rejected. After the fix the invalid instance reports its DB and point, produces no file, and the other valid instance exports.

### Rework DEV self-check

| Command | Actual result |
| --- | --- |
| `DS_TEST_RUN_ROOT=/private/tmp/ds003-dev.Zc2maS/profiles CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --test plc_catalog_export` | Exit 0; 11 tests passed, including both new QA1-F01 regressions. |
| `DS_TEST_RUN_ROOT=/private/tmp/ds003-dev.Zc2maS/qa1-rework CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test plc_catalog_export --test configuration_store --test source_import --test versions --test owner_contract` | Exit 0; 11 + 4 + 4 + 5 + 3 = 27 tests passed using task-owned synthetic profiles; owner snapshot test does not start a protocol listener. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7` | Exit 0. Isolated debug binary SHA-256 `b365c7e0f465db54eb5bb0ee105fc27cac087968b83f8444baf0cfb8f6f3ec97`; this build was not launched or used in the earlier GUI/DAA test. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7 --lib catalog_receipt_retains_partial_rows_and_reports_unknown` | Exit 0; 1 passed, 1 unrelated test filtered. |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --lib exclusive_link_distinguishes_conflict_from_other_write_errors` | Exit 0; 1 passed, 7 unrelated tests filtered. |
| `cargo fmt --manifest-path runtime/Cargo.toml --check`; `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | Both exit 0 after formatting the touched source. The first combined check exited 1 on the new validator's layout; the second check had not yet run in that attempt. |
| `git diff --check -- <tracked DS candidate paths>`; `git diff --no-index --check /dev/null <each changed new file>` | Tracked check exit 0; each no-index check exit 1 because the file differs from empty, with no whitespace diagnostics. |

UI, locale, dependency and build configuration sources did not change in this rework; prior UI/type/build evidence remains tied to the earlier candidate and was not rerun merely for this Rust-only correction. No new native GUI, DS→DAA collection, real device, report or user-profile operation was performed. Both locks remained byte-identical to the QA1 candidate: runtime `bdb170c99a5e863bfd7010032739c37bcbd19234de25c47da868b62c9b8bfaab`; desktop `39f14c514f35cb37ef1844f3e2f23153d737c8fb91a6c108feb3f6efbd244775`.

A file-by-file comparison against the original 29-file handoff found only the approved validator and its test file changed. Reconstructing the original validator by removing the added variant clause gave its exact old SHA `7554fc82bafda6c8c764a9f8065c1ea588d7721acaeb5327bb9f13b8c4220a4e`; hashing the test prefix before the two appended regressions gave its old SHA `8e3250dc28c7db8b8e67e18ed68d8dd325d524e7d34462ca65e6204166a0e0e1`. This audits the scoped rework without treating other pre-existing changes as this role's edits.

### Exact rework candidate hashes

Full-file identities below include pre-existing contents of shared files; only the validator and test differ from the original QA1 candidate.

```text
7455556c1a5248bd6814d0a8d6f039343eb8bac46ef19ece77443e732e4c9a4e  runtime/src/app.rs
6880949a9383696c8b8c3ac948cf537aa71cdbefc43d3b8b08841cd2fc8a6a8b  runtime/src/domain/mod.rs
a916b1c6e660839bf701fc0d535bf630f5e9dd9a3a775036fc3d36abb3880985  runtime/src/domain/plc_catalog.rs
1a701af378109341fe76a21c91f88ef4e9d8c38a78de35e27b9db2048c9cd473  runtime/src/services/mod.rs
ed0a13c8c84bb195f0663c6066f0eae5364acf82614efeae588388e36ed1c0c3  runtime/src/services/catalog_export.rs
16a86987b010ed26f5138391439924b4ef3855f90f03a72a87eaf98954614469  runtime/src/infrastructure/config_store/mod.rs
92384c280c330f1ee16f7ada4978098c882317ac9cc0b10e822f129ef0277966  runtime/src/infrastructure/config_store/queries.rs
e6bf66e981fa785ed212201b88c94d4c0fda2044bb6f4475df90d44acd8b87fc  runtime/tests/plc_catalog_export.rs
8a81729f10da6a8359084410b46f9142d11561bb0c5b730b1ceaa06454cfafa2  src-tauri/Cargo.toml
39f14c514f35cb37ef1844f3e2f23153d737c8fb91a6c108feb3f6efbd244775  src-tauri/Cargo.lock
7e316e861a72ba56ce5e3859f22fdaad03aca7feb08efdf0d7fe750bf44f71ca  src-tauri/src/lib.rs
c7ccc332d8a207ad7c920422d14bbe0e0defe798024165f61ddd87cb5b54bcac  src-tauri/src/commands/mod.rs
c77ec317ce0b7c754d509844079b92ef941df77c4a5d56c19f54fbbcc402f235  src-tauri/src/commands/catalog_export.rs
53a12222035bd381d373363425904fa74340b41f888581e8dbe266c9531538b4  src/services/deviceSimulator.ts
23de7af172012bd854a02121eaa1ebb42df257691d1b7f6b61fd0ce5562092e1  src/app/simulator/views/instances/index.vue
b234b4f0321b404865bc9b3cf0cd995eb2ff1c169966329c8afec59c91a6d37a  src/app/simulator/components/CatalogExportDialog.vue
a98dc54dee8faf1e6c0078a3127a07cf1d37617131467a0e3d750371782471e8  src/app/simulator/locales/en-US.json
dc9044b11482c1cde58caf93402b81d98c8e3fa2b1d450bc13532c2722ae2ad6  src/app/simulator/locales/zh-CN.json
75de72976e060b51dacfedf9bd7a55bbf6ae436472c7c1b77acc47b2788ad0fe  src/styles/app.css
9e875d5772af68b3b70a6c5c54bfe9f563805547d9b0576f4b51fb2df01c2ca4  tests/plc-catalog-export.test.mjs
11c12ecdb37370a49d498f5739f495b61af3d93edcf3b79312126f6d710f05d8  README.md
d93790493c4c76d47a6c113205d81885a29b9666ffc302b13d8801c02e754364  README.zh-CN.md
38eab20bda3ea4127525ec123b1739fad8e4bd00dd231d7a18266c1331745f8d  USER_GUIDE.md
3113d5d2665f42c0e03b78aa1be3aca6398b24dfcdce7acda19b3c7113070c80  USER_GUIDE.zh-CN.md
9c62c5754bef8721993512679ed52abb1329266b22cc9318cd0266abf402714a  CODE_INDEX.md
ab5f8f7211190b1b2a9ae321ecc3c5bf8786cd7f41d13a2298ea8cd3deb42335  runtime/README.md
fb2e5174c98173faf4f650ae530960b17564d5e532f6ce8bf2fc57405fb76939  runtime/README.zh-CN.md
81f4fd0fe8f08b17eee5b39cbafe5d69a7bd5ca8d3d2e4306fa075bb16e4db1f  tests/README.md
03e382faed36c35701811fcb5558cfc56bd14cddce45815076d3a4e4b92785a8  tests/README.zh-CN.md
```

The precise handoff is `device-simulator::DS-003 r5` at formal working tree `/Users/jason/Desktop/DreamCode/aiis-ics-arch`, base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`, with approved spec and frozen QA1 checklist hashes above, the exact file/lock identities above, self-check results and limits in this section. The task-owned `/private/tmp/ds003-dev.Zc2maS/qa1-rework` synthetic regression profiles and shared isolated build target remain for the next verification; reclaim only after the coordinator confirms no process or evidence dependency. Previous actual output files and protected test history retain their earlier documented dependencies. Fresh-context Verification must recheck this new candidate and QA1-F01; its verdict and Human Owner final acceptance remain outside Development authority. Earlier native/DAA observations, unrun native empty-port/STRING checks, repeat-import observation, filesystem race limitations and non-Unix fail-closed boundary are not upgraded by this rework.
