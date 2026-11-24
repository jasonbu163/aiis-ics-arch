Task ID: ARCH-AW-009
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development -> fresh-context Verification on the rework 1 formal working tree; earlier handoff preserved below.

# Development — existing Control Agent editor

Approved [specification](spec.md) SHA-256 c20743d64c7968f7a815f5fbd7d262a469c97c3d47ed8c681f405ec0432e2d42. Base HEAD ee942c8b82cf5b3e502872d8d6ee5c7820b2314e. Implementation is in the existing checkout, without an implementation commit. CA started clean in an otherwise dirty shared checkout.

## Delivered surface

- CA package and lockfiles, Vite, TypeScript, Tauri configuration, App.vue and main.ts. Default opens the new editor with the S7 driver. The opt-in legacy flag restores the old console and its stylesheet. Old headless dispatch and independent runtime source are preserved. New state uses the CA application data subdirectory flow-editor-v1.
- The four new CA frontend modules under src/app, plus three src/services/ca*.ts IPC adapters. The new mode uses CU's public AgentLayout, AgentSidebar, AgentTopbar, StatusCapsule, ThemeToggle, LanguageSwitch, ConsoleCard and ConsoleActionButton from the public source alias and stylesheet. CA owns the editor canvas and field-specific content. Shared CU source is untouched.
- Rust lib.rs, four module registrations and the new ca_*.rs command/domain/service/infrastructure source. Native dialogs scope file access. Immutable revisions, offline catalog intake, logical bindings and typed single-node tests use the new workspace. Callable Rust HTTP GET, HTTP POST, and S7 INT read use a stub under the isolated development profile. PLC write is configuration and simulation only.
- CA bilingual README/PLAN, frontend module README pair, CA code index, contracts README pair, and contracts/demands/ca-field-flow-v1 candidate schema, example and vectors. FF joint gate is pending.
- Targeted Rust tests under src-tauri/tests/arch_aw009/, exact producer catalogs under src-tauri/tests/fixtures/arch-aw-009/, and the [actual native full-flow export](../../automation-world/control-agent/tests/arch-aw-009/status-gate-native-export.json).

## Reproducible self-check

Commands run in automation-world/control-agent:

| Check | Observed result |
| --- | --- |
| pnpm_config_verify_deps_before_run=false pnpm_config_store_dir=/Users/jason/Library/pnpm/store pnpm build | Exit 0 after CU consumption and drag fixes. vue-tsc and Vite passed, with third-party annotations and chunk size warnings. |
| cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --lib --quiet | Exit 0; 54 passed, 3 existing I/O-related tests ignored. Covers exact legacy opt-in, graph and contract checks, real producer file import, fake S7/GET/POST request, authorization-header redaction, query encoding, confirmation, before-send failure, unknown and restart. |
| rustfmt --edition 2021 --check src-tauri/src/{commands,domain,infrastructure,services}/ca_*.rs and scoped git diff --check | Exit 0. Task-generated Tauri schema caches restored to baseline. The pnpm workspace file also matches baseline. |
| Python stdlib JSON, digest, link and bilingual-key checks | Exit 0. The reference example SHA is 28ae535c79f1b8e001d611b50eac9ca53dc1c08a0072fcddc51f1c8d426ada3c, with the same semantic digest as the actual native export. Rust validated the candidate and native file. Separate full JSON Schema validation was unavailable here. |

pnpm add used npm to fetch pinned Vue Flow 1.48.2. pnpm 11 wrote the lock and links, then reported new transitive vue-demi's optional build as unreviewed. The packaged Vue 3 entry worked without its script. Build and launch used the existing store and skipped pnpm's automatic dependency reconciliation for this host. Existing lock resolutions were preserved. Fresh install on a different machine was not independently verified.

## Native WebView and I/O evidence

Launch from the formal CA directory with an empty task-owned temporary directory containing the .ca-editor-fixture marker. The actual run used:

    cd automation-world/control-agent
    CA_FLOW_EDITOR_PROFILE=/private/tmp/aw009-dev-ca.8GYrnq \
      pnpm_config_verify_deps_before_run=false pnpm_config_store_dir=/Users/jason/Library/pnpm/store \
      CARGO_NET_OFFLINE=true pnpm tauri dev

The default sandbox declined loopback Vite listen with EPERM. Scoped elevation compiled and ran cargo run --no-default-features --features rust-snap7-driver against the formal CA code. Window title AIIS ICS Control Agent. The only loopback socket used is the app's front-end on 127.0.0.1:15190. All selected test nodes used simulation or transport stubs. No HTTP business endpoint, S7 simulator or PLC was connected, and no legacy or user profile was read for validation.

CU could not select the bare Mach-O. The development wrapper /private/tmp/aw009-dev-ca.8GYrnq/CA AW009 Development.app (com.aiis.aw.aw009.development) used a verified, byte-identical copy (then SHA 8319a6f5e1014a242bd4bb09d3c7a0e1582541551785225f9f84d8f9feb714a2) of the formal debug executable and pointed at the same formal Vite source. Later formal Rust rebuild SHA d48a267204d63732f1a547864582730f5ec074d8718882c47d64330954382c36 adds stricter layout/size validation and the no-I/O legacy flag test. The native wrapper used the earlier binary with the same IPC, and latest Vue changes loaded from Vite. Fresh Verification can recreate a temporary app wrapper from the final checked binary and must use its own profile. Avoid using the same profile from two application processes.

| Area | Native observations |
| --- | --- |
| AC02 | Actual CU side menu, topbar, controls, shared cards and Vue Flow loaded. Pointer dragged condition/end nodes from the palette, moved a saved read node, and dragged real handle to handle. Observed Vue Flow's edge object; selected, removed and restored edge; deleted attached node by button, then by Backspace on another run. Both restored the attached edge on undo. Undo of movement returned pristine r1; redoing the move created r2. |
| AC04 | A one-node native save/export/reimport first confirmed persistence (SHA dc3e6d7f19571a2732c2a21ac95e391996f5b9ea6c88ce81a556b5c0694e627a). Imported full status_gate, exported from macOS dialog, imported the exported file and opened identical r1 with all four edges. Full r1 export SHA 19c0bbccf4fd1c402866a6ee742c3c85e309615c84899a5d501ec365ab41800f. Moved read node from (0,0) to (35.90322580645161,-177.1225806451613) and saved new r2 (file SHA 17681d175c5592921c0c9a0c9c8d513ad2ff00971c7b2664a5242284db7f64d2). Both retained semantic SHA a84851e3b56f08c566d19cc0ac08d0cc07289e17c5c286e2a3b51cf71c89368c. |
| AC05–AC06 | Native dialogs previewed, committed and reopened original DS as plc_line_a and DAA as plc_daa. Re-selecting both originals reported identical and reopened the same pair without duplicate local resources. DS preview displayed five points including a disabled DB and point; DAA showed three with no DB-level enabled fact. Rust tests verify invalid inputs and source-change/TSAP distinctions. |
| AC07–AC09 | Bound the alias task_status to DS source Count and test-only logical HTTP target fixture.invalid. Native S7 stub preview showed DB21 byte 2 and result INT 1 quality good. GET preview resolved the manually entered upstream INT query status=1; stub returned 200. Added isolated POST on an incomplete draft, observed side-effect text and disabled execution prior to confirmation; selected stub ambiguity and saw persisted unknown. Also ran an end-node simulation. Persisted actions all have actual_io=false. Cargo covers further POST header/body/encoding, success and restart cases. |
| AC10–AC12 | Light and dark JSON screenshots and graph interactions are in the native CU transcript. The headings, buttons and JSON were visually readable, and EN/中 switching changed workbench/editor labels. Exact paired CSS measurements at 1440×900 and 1024×768 were not retained. Fresh Verification should measure both sizes, themes and error state. Existing legacy dispatch was inspected and the option tested without starting legacy device work. |
| AC13 | Independent FF interoperability remains pending. The native export is retained to link later FF work. |

## Original catalog provenance

| Producer | Original receipt |
| --- | --- |
| DAA | DAA-raw.json SHA 5d27fe3234ec2573395c2faa0fd717187a11cc541199621cef789742e28627cf. Copied unchanged from tracked automation-world/shared/daa-output/DEV-PLC-DAA.json at cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81. The file identifies data_acquisition_agent, active_revision, revision ea6fddc6-286d-409b-b403-00c7380c0bdc and a non-sensitive synthetic loopback target. |
| DS | DS-raw.json SHA 8d70a9d04b6481aaea402b0a44d5b797d6e5ac5700fd8871b7c9113abaa2931c. Disposable offline caller reused the unchanged DS synthetic workspace fixture from runtime/tests/plc_catalog_export.rs. Against DS source HEAD ee942c8b82cf5b3e502872d8d6ee5c7820b2314e it saved DB data into revision 295c1df3-562d-459a-b674-f121269bd63b and invoked unchanged services::catalog_export::{preview,choose_directory,commit}. The caller independently verified the returned file SHA and closed the app. Run in the disposable caller as DS_TEST_RUN_ROOT="$PWD/profile" AW009_DS_RAW_FILE="$PWD/DS-raw.json" cargo run --offline. Caller source SHA 76fc4ff7af5e8cc61dc78ae72b44664d610c32c706410178c35b865c465417b2, lock SHA 27de0e950e9c81528f5b716d60c4999da3c5d6d8c47f33e3a8c29523324bf238. Coordinator retains recipe at /private/tmp/aw009-r2-ds-export.LMrcmV through Verification. No protocol listener/client or DS edits. |

## Residual verification and resources

Keep the development wrapper, Vite session and isolated profile temporarily for the user's visible UI and Verification replay. After the coordinator determines they are no longer needed, stop the task-owned processes and remove the task-owned /private/tmp/aw009-dev-ca.8GYrnq resources. CA catalogs and native export are durable. No independent verdict, exact paired viewport measurements, non-macOS execution or real integration is claimed. FF reuse and live hardware/API acceptance remain separate.

Exact scoped candidate file manifest: /private/tmp/aw009-dev-ca.8GYrnq/candidate.sha256 (54 files, manifest SHA-256 9dc0ef623a8b04af36fcac6207cc3c42cf08cac7af363594692d252d1b73a1a2). The shared contracts README pair also carries another task's pre-existing diff; this task adds only the CA/FF candidate section.

## Rework 1 — replacement Development handoff after QA1

The approved spec stays at r2, SHA c20743d64c7968f7a815f5fbd7d262a469c97c3d47ed8c681f405ec0432e2d42. Base still ee942c8b82cf5b3e502872d8d6ee5c7820b2314e. The earlier handoff and independent [QA1 findings](checklist.md) remain historical evidence. This replacement handoff applies to the same formal working tree.

- AC03 / AC08: Vue Flow allows mutually exclusive condition outputs to lead to a common node. Field selection computes the intersection of predecessor paths, so the same-parent two-port case exposes both shared fields. A value produced only on one branch stays unavailable. The Rust validator and node-test preflight now reuse the same topological computation. Contract READMEs clarify that branches can reconverge and nodes have no parallel execution.
- AC06: Changed-source preview compares DB metadata by external DB ID. The preview exposes previous/new values, including source_enabled true, false and omitted, and distinguishes a missing fact from an absent DB. The bilingual UI renders source-state changes next to the existing point/connection diff. Preview never overwrites the original resource. Both original producer files and the native status-gate export retain their previous hashes.

Actual checks from the formal CA directory:

- node --experimental-strip-types --test tests/arch-aw-009/upstream-outputs.test.mjs — 2 passed. Reproduces the exact shared-parent case and excludes a branch-only value.
- cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --lib --quiet — 56 passed, 3 existing tests ignored, exit 0. Adds exact reconvergence with fake GET, type and branch-only rejection, DS true→false, and cross-producer false→missing without catalog overwrite.
- pnpm_config_verify_deps_before_run=false pnpm_config_store_dir=/Users/jason/Library/pnpm/store pnpm build — exit 0; same third-party annotations and chunk-size warnings.
- cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --no-default-features --features rust-snap7-driver --bin aiis-ics-control-agent — exit 0. Formal binary src-tauri/target/debug/aiis-ics-control-agent SHA f57622350c8e83fab4e449d53ecd7db2ca7be367b5817db13f60b10526a2e1a1.
- Scoped git diff --check, targeted rustfmt, bilingual key parity, exact spec SHA and fixture digests — passed. Generated Tauri schema files restored; pnpm-workspace.yaml and CU public source are unchanged.

Exact replacement manifest /private/tmp/aw009-dev-ca.8GYrnq/candidate-rework-1.sha256, 55 files, SHA-256 1a4a2c9ef82c5bec94b2813daa319b2fc05c40d80e3514796fbb06188c0833c9. Verify from repository root with shasum -a 256 -c against that manifest.

No new native UI run during rework. Elevated lsof found no listener at 127.0.0.1:15190. Use a fresh marked temporary profile and a QA-owned lifecycle for Vite and any native bundle, separate from the existing Development profile. Native replay on the final binary and exact viewport measurements remain open as recorded by Verification. No actual HTTP or S7 test took place. FF joint validation remains pending.
