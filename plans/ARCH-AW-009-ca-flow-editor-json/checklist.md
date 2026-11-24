# ARCH-AW-009 r2 independent Verification

Status: qa_failed. Handoff: Development for rework. Human Owner acceptance pending.

## Candidate and environment

Fresh Verification on the formal macOS 15.7.7 working tree, Node v22.19.0. Base ee942c8b82cf5b3e502872d8d6ee5c7820b2314e, spec SHA-256 c20743d64c7968f7a815f5fbd7d262a469c97c3d47ed8c681f405ec0432e2d42. Verified all 54 paths with `shasum -a 256 -c /private/tmp/aw009-dev-ca.8GYrnq/candidate.sha256`. Manifest SHA-256 9dc0ef623a8b04af36fcac6207cc3c42cf08cac7af363594692d252d1b73a1a2.

## Findings

1. **AC03 / AC08 failed for a legal reconverging flow.** Use read → condition → GET → end, connecting both named condition outputs to GET. Set GET query sample to read.value. The read dominates GET on both routes. The graph validator intersects parent dominators in ca_flow.rs lines 405–437. The editor excludes the field at model.ts line 49 and the node-test service rejects it at ca_node_test.rs lines 87–109 with test_reference_invalid. In the formal CA directory, the following independent read-only probe returned `[]`, exit 0, where read.value and branch.matched must be selectable:
   
   ```sh
   node --experimental-strip-types --input-type=module <<'JS'
   import {outputs} from './src/app/flow-editor/model.ts'
   const nodes=[{id:'read',type:'plc.read',config:{value_type:'int16'}},{id:'branch',type:'condition.compare',config:{}},{id:'get',type:'http.request',config:{method:'GET'}}]
   const edges=[['read','next','branch'],['branch','true','get'],['branch','false','get']].map(([from_node_id,from_port,to_node_id])=>({from_node_id,from_port,to_node_id}))
   console.log(outputs({flow:{nodes,edges}},'get'))
   JS
   ```
2. **AC06 changed-source preview is incomplete.** In ca_workspace.rs lines 428–446, catalog_diff compares points with their DB numbers and the PLC connection only. On the original DS file, changing only a DB's source_enabled yields identical compared point maps and connection. Added, removed and changed lists are empty, and connection_changed is false despite a substantive catalog change. The UI simply prints this diff. Preserve the former resource and show the changed DB fact when previewing this case.

## Other checks and limits

- AC05/06 provenance: compared both fixture files to originals using shasum. DAA tracked DEV-PLC-DAA.json and its fixture both have 5d27fe3234ec2573395c2faa0fd717187a11cc541199621cef789742e28627cf. DS offline exporter artifact and its fixture both have 8d70a9d04b6481aaea402b0a44d5b797d6e5ac5700fd8871b7c9113abaa2931c. Ran existing Development handoff binary src-tauri/target/debug/deps/aiis_ics_control_agent_lib-c1f8b18dd1bb6087 with filter ca_ --quiet, exit 0, five passed, 52 filtered. This was a replay of the built test executable. No protocol I/O.
- AC01/02/04/10/11/12: read the public CU imports and Vite aliases. Git status for automation-world/console-ui clean. Copied final formal debug binary SHA d48a267204d63732f1a547864582730f5ec074d8718882c47d64330954382c36 into an isolated macOS QA wrapper with own fixture marker and profile. Launch Services open returned 0. Native app selection failed with “unknown or expired node_repl continuation” after 444 seconds. Native render, gestures, dialogs, both viewport/theme pairs and visual readability remain independently unverified. Development observations remain attributed to tasks.md.
- AC07/09: reviewed S7 and GET/POST construction, fake paths, confirmation, unknown persistence and retry settings. Targeted binary replay passed, no independent end-to-end UI verdict. AC12 fresh build and schema validation deferred on failing candidate. AC13 FF remains pending.
- QA wrapper/profile root /private/tmp/aw009-qa.T4yBce, dedicated bundle com.aiis.aw.aw009.verification. Rework handoff may dispose of this QA-owned root once its process exits. Development session is separate.
- Return to Development for both findings. Fresh Verification on the replacement candidate must repeat affected checks and outstanding native acceptance before handoff for final acceptance.

The QA-only bundle quit command returned 0. The Development Vite session was left available to the coordinator.

## QA2 — replacement candidate, independent verification

**Current verdict: qa_blocked.** Both QA1 implementation findings are closed on the replacement candidate. Independent native interaction and four-way visual coverage remain partial. Human Owner acceptance and FF joint verification remain pending.

Verified the formal working tree against all 55 entries in the rework-1 manifest with `shasum -a 256 -c`. Manifest SHA-256 is 1a4a2c9ef82c5bec94b2813daa319b2fc05c40d80e3514796fbb06188c0833c9. Formal debug executable SHA-256 is f57622350c8e83fab4e449d53ecd7db2ca7be367b5817db13f60b10526a2e1a1. Workspace.vue imports the actual CU public shell, cards and action components through the Vite aliases to console-ui/src/ui/index.ts and its public stylesheet. Scoped git status for console-ui was empty.

| AC | Independent evidence and remaining limits |
| --- | --- |
| 01 | The macOS QA app wrapper used the formal debug binary with a fresh marked fixture profile. Its initial workbench displayed the isolated transport badge. The legacy routing regression ran with Cargo. Development ran the exact pnpm tauri dev launcher. QA2 ran formal Vite and the matching binary separately. |
| 02 | At a measured 1440×900 native content viewport, OS pointer drags added read_1 and end_1, connected the read output handle to the end input, then moved end_1. The native JSON view contained read_1:next → end_1, read position (133,267) and end position (508,390). Independently replayed button deletion/undo on a one-node draft in a separate background native QA2B window: JSON node count 1 → 0 → 1 and restored end_1 config and coordinates. Edge selection/deletion, attached-edge restoration, keyboard deletion and undo of each individual gesture remain unverified independently. |
| 03 | Both native Save and Export returned AXEnabled=0 on an unbound read draft. Selected end_2 simulated successfully on an incomplete graph. The selector's two branch regression tests passed. Rust graph and node-test cases passed, including the prior shared-parent and branch-only cases. |
| 04 | Native QA2B saved a simple valid r1, file SHA prefix dc3e6d7f1957. Rust graph_validators_and_roundtrip passed. Validated both reference status-gate and the prior native export against the candidate schema. Independent native full-flow export/reimport and layout-only r2 replay remain open. |
| 05 | Compared tracked DAA original and archived fixture (SHA 5d27fe3234ec2573395c2faa0fd717187a11cc541199621cef789742e28627cf) and offline DS export and archived fixture (SHA 8d70a9d04b6481aaea402b0a44d5b797d6e5ac5700fd8871b7c9113abaa2931c). Both pairs matched. See tasks.md for original producer revisions. Independent Rust test original_catalogs_preview_commit_reopen_repeat_and_conflict passed. Native QA2B opened the PLC file picker; neither producer import was completed in the native replay. |
| 06 | Both catalog regression tests passed, including original DS source_enabled true→false and cross-producer false→absent with no overwrite. Source compares DB metadata by external ID and differentiates a missing DB from an omitted enabled fact. |
| 07–09 | selected_node_simulation_fake_get_post_read_and_restart and the reconvergence test passed in the formal Rust suite. These exercise selected-node target resolution, stub S7, GET and POST, error/unknown classification and restart, with protocol communication disabled. The independent native click-through reached one simulated end-node result. Native replay of PLC/GET/POST resource setup and result controls remains outstanding. |
| 10 | Readable editor labels, node text, controls and JSON observed on PC light. PC dark JSON and tablet dark English JSON also reviewed. The first QA viewport was 1440×900 and the second 1024×768 measured from the native WebView scroll area, excluding the title bar. Valid evidence under /private/tmp/aw009-qa2.9R1CBo: pc-light-editor.png, pc-light-json.png, pc-dark-json.png, tablet-dark-json.png. Its tablet-light-json.png was captured after an externally changed window geometry/draft and is excluded. QA2B confirmed 1024×768 light test controls by accessibility, but its background window could not be captured. Tablet light and full error/scroll coverage at each theme/size remain open. |
| 11 | Native workbench explicitly states whole-flow execution is unsupported. QA2B isolated state persisted r1 and exactly one completed end_2 simulated record with actual_io=false and result=matched. |
| 12 | Independent formal frontend build passed. Rust 56 passed, 3 ignored, 0 failed. Node selector tests 2 passed. A native simulated end-node result crossed UI→IPC→Rust and persisted. Python jsonschema 4.26.0 Draft202012Validator checked the schema, candidate example and actual archived native export. Both contract README link checks and scoped git diff --check passed. |
| 13 | FF joint gate pending. |

Commands from automation-world/control-agent were `node --experimental-strip-types --test tests/arch-aw-009/upstream-outputs.test.mjs`, `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --lib --quiet`, and `pnpm_config_verify_deps_before_run=false pnpm_config_store_dir=/Users/jason/Library/pnpm/store pnpm build`. All exited 0. Vite reported existing annotation and chunk-size warnings. Schema checks used the existing cached Python environment under /Users/jason/.cache/uv/archive-v0/h7qFq2OmO2sJdItomXges with no dependency installation.

Native blocker and handoff: CUA selecting com.aiis.aw.aw009.qa2 returned “unknown or expired node_repl continuation” after 516 seconds despite a requested 10-second timeout. Native macOS Accessibility and Quartz provided the evidence above. Initial System Events actions by process name gave inconsistent window association and are excluded. Accepted gestures used PID 54238, window 245137, and verified target-window bounds. The first window later changed to a different unsaved draft and 1920×1027 content viewport without QA input. QA left it intact. Background QA2B, PID 62498, window 245288, used its own new marked /private/tmp/aw009-qa2b.C8owyb profile and PID-scoped input. Its native open sheet appeared, but a background path shortcut did not present a path field and the directory AXOpen operation returned -25205. Window-only screencapture returned “could not create image from window”. No further foreground keyboard or mouse replay was attempted while the desktop was in use. Neither QA profile used protocol requests. The initial name-based observations cannot establish the identity of another window; no save or test command was issued during those observations.

Retain the two marked QA roots and the task-owned loopback Vite service on 15190 while the first window or its unsaved draft is in use. Coordinator can retire them after that dependency ends, preserving the cited screenshots. A short exclusive native replay can close the outstanding interactions and visual matrix; this verdict does not identify another implementation rework.

QA2B was inactive at closeout. Verified its exact PID and bundle ID, requested normal termination, and confirmed its running-application list was empty. QA2 PID 54238 and Vite session 85481 were left available. The two fixture directories retain evidence until coordinator closeout.
