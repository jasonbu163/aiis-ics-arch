# Native user-guide image provenance

[简体中文](README.zh-CN.md) · [User guide](../../../USER_GUIDE.md)

The coordinator captured these seven PNGs from the real native window on 2026-10-22 using synthetic data. Images were copied byte for byte, without generated pixels, editing or browser-preview substitution.

| File | UTC capture time | Step | SHA256 |
| --- | --- | --- | --- |
| [01-workbench.png](01-workbench.png) | 2026-10-22T06:14:34.593Z | Empty workbench | `aefadea6f73cd36f6c068145ab94c9bbb2d98278aacf37bfe5fc171f2ecf34c2` |
| [02-instance-editor.png](02-instance-editor.png) | 2026-10-22T06:17:58.386Z | PLC_Test editor | `628b7183167cf2f87c437dc51df1d73eb631ca8386fcdd4723bbf3e424e77541` |
| [03-manual-point.png](03-manual-point.png) | 2026-10-22T06:18:32.457Z | Manual BOOL point | `63bf9b456a6e4105ea30c8876a4f919abf3b38793dd7dfa0a36409ab66c543ca` |
| [04-manual-layout.png](04-manual-layout.png) | 2026-10-22T06:20:06.486Z | Complete manual layout | `0b3f8d840c37ccebc55e8c3aa9a768e8c69372e48636779e021a0164890e20f9` |
| [05-policy.png](05-policy.png) | 2026-10-22T06:24:17.127Z | REAL policy, explicit initial 0 | `eddd0d86f43af59db075e5dc1c0122ee5c287e61269a1f918780b860d2a0216f` |
| [06-apply-preview.png](06-apply-preview.png) | 2026-10-22T06:25:07.998Z | Saved sequence 7 load preview | `def4ad4418763b429245e92bf19a44f2df70765258d334bf0a1aa4ddbfbf5abf` |
| [07-online-values.png](07-online-values.png) | 2026-10-22T06:26:57.569Z | Runtime values, ordinary UI write 12 | `9012c04035ca263633da61b1b4bdbdf7d40f613b16dcabc2f0a314055ad84651` |

## Facts and outstanding steps

Manual_Demo is DB31, length8, with BOOL0.0/INT2/REAL4. Toggle half-period is1500ms (generic period remained1000); REAL ramps0..100/10000ms; initials are false/0/0. Coordinator observations include ordinary write12, both BOOL states, changing REAL and Pause/Resume/Stop. One image cannot prove toggling.

Actual initial20 typing reverted to0. The fixed-value input is a source-derived same-binding risk, not an independently reproduced dynamic failure. An earlier05 attempt is retained separately in raw; published05 is the retake with initial0. Published07 is the final left-column view. Capture intent text does not prove input acceptance. Synchronous automated input/change events do not replace real typing evidence.

Owner's latest instruction to take over supersedes the mechanical ten-image target. Import bindings, imported names and stopped reopen have no images: no08/09/10 files or image references are created. Complete textual instructions remain. Reset, import submission and normal close/reopen were not completed.

## Originals and retained resources
Original archive: `/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/dev-run-0331`; inventory SHA256 `e53f29e7c4e3c5bdf39040fa2645f73c8adabb46744b67aa84fb30121b75c3e0`. Per-member hashes are in inventory.json; raw and launch.json retain observations, capture attempts and fixture-copy provenance. Existing QA archives remain unchanged.

Product source `306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4`; Original QA productDesktop SHA256 `a6b485e86232151f021d076a3f8acdf48b98decfc4af9217058a3a7969dae11d`. Same-byte carrier native-library SHA256 `83ab0462ba83c536d9d8eda93b8a57005802ab734a2229b53f101023a7b41ad5`.

The first background PID88101 had no captured successful exit code; a foreground sandbox attempt exited134. Neither proves normal shutdown. The later carrier PID89100/session90871 remained live when Owner took over its Open file chooser; no files were selected. Profile: T5/profile/dev/user-guide-20261022; carrier: T5/tmp/dev/user-guide-20261022/DS-User-Guide-Capture.app (T5=/private/tmp/arch-aw-005-r5-exec). Retain both for user operation. The empty lsof30102 exit1 only records no listener at that instant, not process exit. Reclaim the carrier only after Owner releases the example and owned process/listener release is verified; do not remove unknown resources.
