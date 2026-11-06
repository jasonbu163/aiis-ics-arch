Task ID: DAA-008
Revision: r1
Status: dev_blocked
Owner Role: Development
Allowed Writers: Development
Handoff: partial developer_handoff of exact r1 A0/A1 source candidate; hot-journal recovery requires approved r2; fresh Verification requested
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# Development事实与执行边界

批准规格SHA-256：`382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae`。批准前原稿SHA：`f407532ff91d8ec5aa8df4d1cfaad4ca99700dc2095a1ebeba816d75f2f0e3e2`。Human Owner逐字批准见spec §14。实际Development为`/root/daa008_development`；唯一coordinator为`/root`。正式交付树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，entry HEAD `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`，共享脏树，不回退他人变更、不commit/push。

A0进行中；A1仅下列自有合成目录获批；B未获批准、未执行；完整阶段C与AC18–AC20未完成。本任务不读取真实.env、SQLite/profile、原8590样本；不运行HTTP/loopback listener、DS/PLC/MySQL、Docker或完整GUI。不迁移、覆盖或清理已有配置及历史。不重复阶段B整套测试。

## 执行计划与验证

1. P0：固定provider只读pins与正式树before；消费完整批准bundle/最近规则/相关源码。验证：SHA/allowlist。
2. P1：无损canonical、固定分片/完整轮builder、严格ACK与传输边界。验证：公开固定vectors、独立lexical反例与传输替身，无网络。
3. P2：新空config2/runtime3、六投递表、CAS、freeze/dispatch/ACK同库事务、引用/容量/重开。验证：仅全新合成v2/v3 SQLite及故障/崩溃矩阵。
4. P3：单worker、最新/历史3:1、公平恢复、显式控制/IPC/CU/i18n。验证：纯规则/替身/触达Node断言，构建不启动产品。
5. P4：双语手册与本事实记录；固定候选文件/前后SHA/diff/命令/结果/限制，developer_handoff给fresh Verification。B真实联调另提具体方案批准。

## 工具链与资源

仅使用项目Cargo锁/已有pnpm依赖，优先`--offline --locked`；不安装辅助依赖。拟将锁中reqwest 0.13.4提升直接依赖，关闭默认feature，启用blocking/标准TLS及必要JSON/stream能力；serde_json只增加raw_value/arbitrary_precision。先审计已有锁可用feature，再解析并记录确切差异。无Tauri启动feature或pnpm依赖改动。

本任务A1目录：`/private/tmp/daa-008-r1-a-xsm2qlrl/development`，由stdlib mkdtemp创建且canonicalize。所有合成test TMPDIR固定到此目录。创建者Development；用于全新合成夹具、测试日志和冻结候选。暂无子进程/监听/服务。保留至fresh Verification与Owner交接证据不再依赖后，由coordinator核对归属再清理；必要结果和摘要持久写入本文件，不以临时日志作唯一证据。

公开entry before：`/private/tmp/daa-008-r1-a-coord-l73e8_ms/entry-manifest.json`及其before目录（coordinator所有）。唯一notifier由coordinator管理，Development不另起、不发信。

## DEV self-check（持续追加）

初始记录时尚未运行产品检查。后续实际自检见下列里程碑；任何合成SQLite运行均在明确A1目录。

2026-11-05依赖解析前决定：reqwest固定`=0.13.4`、`default-features=false`、仅`blocking,rustls`（使用标准证书校验；响应以Read流计量，无需json/stream feature）；serde_json仅`raw_value,arbitrary_precision`。已从本机现有reqwest0.13.4 Cargo.toml核对features。

## R02/R12窄解释（coordinator转实际PM只读裁定）

2026-11-05，只有同origin/target/合同pins、无真实prepared/inflight/unknown/retry/父链依赖时，允许CAS更新已核来源材料并重新评估从未冻结的`source_adoption_required`诊断。`body=NULL`本身不充分：还须无requestDigest/bodySHA、attempt=0、parent=NULL且从未prepared/dispatch。仅对重新匹配成功的本地未冻结诊断解除引用/移除可再生诊断行，保留delivery_recovered事件；不匹配继续blocked。原样本身份/seq/raw/SHA/ACK不变；保存不发HTTP。任何真实冻结请求、损坏丢body或未知结果继续保护。

A1已取得真实hot-journal失败：合成子进程ACK未提交事务经sqlite3_db_cacheflush后`_exit(86)`，runtime.sqlite-journal存在；Stores::open的RO preflight返回`time_profile_unsupported:attempt to write a readonly database`。失败日志`/private/tmp/daa-008-r1-a-xsm2qlrl/development/crash-hot-first.log`和对应合成fixture保留，已交coordinator/PM裁定。未使用immutable、未放宽未知/v2门禁、未复制用户库或引入恢复协议。此项未解决前不宣称完整A0/A1可交接通过。

## 当前里程碑（2026-11-05；非QA）

- P1：`cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib facts_canonical -- --nocapture`，`p1-storage-compile.log`、`p1-worker-compile.log`均exit0、3 passed。固定provider三机器JSON只读消费，vectors含多PLC/多DB/固定分片；独立十进制/控制字符/20层允许21层拒绝。早期canonical-first/second/third失败保留：九位时间规范投影及其固定分片字节影响先后修正，原三字符串没有重编码。
- A1：所有运行显式`TMPDIR=/private/tmp/daa-008-r1-a-xsm2qlrl/development`；`cargo test ... --lib delivery -- --nocapture`的delivery-fourth.log exit0、7 passed。后续新增CAS、容量、dispatch/ACK故障、清理与202轮不均衡PLC负载后，delivery-eighth.log exit0、12 passed，命令使用`--skip crash_real_hot_journal_recovers_atomic_state`仅为继续独立定位，**不是完整A通过**；该失败仍为真实阻碍，不删除/削弱断言。
- 真实崩溃：`cargo test ... --lib crash_real_hot_journal_recovers_atomic_state -- --nocapture`的crash-hot-first.log exit101。实际子进程flush未提交ACK事务并exit86；hot journal存在，RO preflight读库失败。PM已独立裁定：r1的RO-before-any-write与热恢复自举不能兼得，需要r2明确新profile受控恢复凭据及信任边界。Development不实现该未批协议、不以expected rejection改成通过。AC09/10/14中崩溃恢复未闭合；当前不授developer_handoff全A完成。
- 前端：`pnpm --dir automation-world/data-acquisition-agent build`，frontend-second.log与frontend-third.log exit0；仅现有Rollup注释/大chunk警告。frontend-first.log为首次TypeScript局部可空报错（exit2），已修正。未启动完整GUI或listener。
- `node --test automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs automation-world/data-acquisition-agent/tests/sample-details.test.mjs automation-world/data-acquisition-agent/tests/time-and-history-preferences.test.mjs`，node-first.log exit0，13 passed/0 skipped。具名IPC facade、字符串序号、两页控件、对称locale及既有时间/原样本展示增量；不作为实际视觉或真实HTTP证据。

上述日志均位于本A1自有development目录。后续仍在完成独立已批A0/A1实现/检查与具体候选收据；A1 hot恢复相关路径停止，待coordinator提交r2并取得精确批准。已有SQLite、真实env/profile、原联调数据、HTTP/DS/MySQL/Docker/GUI均未操作。

## Final partial developer_handoff (2026-11-05)

**This is dev_blocked / partial developer_handoff, not full A0/A1 completion, QA verdict or Owner acceptance.** The only established specification blocker is real hot-journal recovery under r1's RO-before-any-write rule. PM, through the sole coordinator, determined that a new r2 trust/recovery boundary requires precise Owner approval. No recovery credential, immutable bypass, journal deletion, v2 upgrade, env/profile migration or automatic start was added.

The implementation is in the formal delivery tree, not just a temporary checkout. Entry HEAD remains `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`; no commit, branch, worktree, Git push or publication was created. All source edits stopped before the final receipts below. The seven unchanged allowlist surfaces remain explicitly pinned alongside 45 changed files. Root CODE_INDEX edits are only the DAA-owned segment; entry dirty changes elsewhere are preserved. The workbench overview before was missing from the coordinator snapshot: its entry HEAD bytes are used only because the coordinator confirmed that file was clean at entry.

### Frozen source and diff

- Approved spec SHA-256: `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae` (unchanged).
- Final manifest: `/private/tmp/daa-008-r1-a-xsm2qlrl/development/candidate-r1-partial-manifest.json`.
- Final source-only diff: `/private/tmp/daa-008-r1-a-xsm2qlrl/development/candidate-r1-partial.diff`.
- Evidence snapshot: `/private/tmp/daa-008-r1-a-xsm2qlrl/development/candidate-r1-partial/after/`; it is not a build/implementation checkout.
- `candidate-manifest.json`, `implementation.diff` and `candidate/after` are superseded intermediate receipts and must not be used as the final candidate.
- Final tasks SHA and complete handoff diff are recorded externally in `handoff-receipt.json` to avoid circular self-hashes. The complete diff adds this Development-owned tasks file; PM-owned spec and coordinator indexes are not claimed as Development edits.

Manifest SHA-256: `a99d85980d9ae8323d15a5824848a0ea1a0d4f46a4117f35cfb2e305a796076a`. Source diff SHA-256: `e34edcaa1271dc62219ec9fc5a744d9a8acf6cba196d3d7bd3da2d8105df90f4`. Manifest enumerates 52 finite allowlist files, 45 changed.

### Resulting behavior and architecture

New empty profiles create config2/runtime3 and the six delivery tables. Known v2/v2 remains local-only without delivery DDL; config2/runtime3 schema/identity/time/ledger and explicit CREATE structure are verified read-only before persistent opening. The sample/manifest2/context1 formats and local_sample.rs bytes remain unchanged. Settings use separate CAS and verified source material; never-frozen source diagnostics may be re-evaluated only under PM's recorded narrow conditions.

The Rust path performs lossless pf-json, exact original hashes, fixed parts/full transport manifests and frozen byte identities; strict committed/terminal-rejection/failure/read envelopes; one explicit worker and shared POST/GET HTTP permit; persisted PLC/group rotation, 3:1 opportunity counter and up to eight unresolved frozen batches. Runtime retries use at most eight monotonic deadlines; persistent Shanghai nextAttemptAt is used only for bounded 1..300-second reconstruction/display. ACK, parts, sample state and references commit together; safe retention removes unreferenced delivery metadata in the original whole-cycle transaction. Real I/O/unknown retains recovery material. One worker/client is reused across repeated start/resume and pause; shutdown completes acquired results before storage close. The test factory is private service composition, with no product injection IPC.

Only Rust owns the three fixed APIs. Normal/debug fixtures and browser no-bridge remain separate; validation rejects real delivery/GET. Manual reads support latest/test, earliest changes and fixed range projection/original, small fixed page sizes, 20-page explicit continuation and typed response/digest checks. They persist only read_result diagnostics and never ACK. UI has real workbench/storage controls, detached target/source settings, bounded queue/events, public column-width preferences, original/detail dialogs, historical-commit wording and symmetric ZH/EN. Native visual/actual HTTP proof remains B.

### DEV self-check: actual commands and limits

All commands run in `/Users/jason/Desktop/DreamCode/aiis-ics-arch`. Rust tests use the explicit environment `TMPDIR=/private/tmp/daa-008-r1-a-xsm2qlrl/development`; no Bootstrap::load, real dotenv/default profile, listener, MySQL, DS, PLC, Docker or full GUI was invoked. The private actual-engine test constructs Bootstrap directly with a new synthetic profile and read_allowed=false, and injects only the bounded Transport substitute.

| Command | Exit / observed result | Log under the A1 development directory |
| --- | --- | --- |
| `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib delivery -- --skip crash_real_hot_journal_recovers_atomic_state --nocapture` | 0; 21 passed, including 3 child entry helpers whose substantive behavior is invoked by parent tests. The hot case is explicitly excluded only to verify independent work; it remains failed, not passed. | `delivery-handoff.log` |
| `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib facts_canonical -- --nocapture` | 0; 5 passed: provider vectors, lexical decimal/REAL/fragment limits, duplicate/UTF-8/depth, strict nine-digit time/no leap-second truncation. | `canonical-handoff.log` |
| `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib facts_http -- --nocapture` | 0; 3 passed: origins, actual bounded Read helper and typed read modes/original SHA. No socket was bound or sent. | `http-final.log` |
| `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib time_contract -- --nocapture` | 0; 5 passed: four narrow existing time/preflight cases plus synthetic v2 configuration/history/ID/sequence/pending/schema preservation. Not the full Stage B suite. | `time-candidate.log` |
| `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib actual_engine_single_worker -- --nocapture` | 0; actual LocalEngine with substitute: same worker on repeated start/resume, pause across a 1-second period, in-flight ACK, pending second sample, resume, shutdown and stopped reopen/lock release. | `worker-lifecycle-corrected.log` |
| `cargo fmt --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --check` | 0 | `fmt-handoff.log` |
| `cargo check --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver` | 0; no new unused production fields | `driver-handoff.log` |
| `cargo check --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --features local-validation` | 0; nine existing ordinary-config helpers unused under this feature, preserved | `validation-handoff.log` |
| `node --test automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs automation-world/data-acquisition-agent/tests/sample-details.test.mjs automation-world/data-acquisition-agent/tests/time-and-history-preferences.test.mjs` | 0; 13 passed / 0 skipped | `node-candidate.log` |
| `pnpm --dir automation-world/data-acquisition-agent build` | 0; vue-tsc + Vite; existing Rollup annotation/large-chunk warnings retained, no app startup | `frontend-candidate.log` |
| `git --no-optional-locks diff --check -- <the 45 manifest changed paths>` plus explicit UTF-8/new-file whitespace, paired locale/placeholder and local-link scanner | 0; 561 paired keys, 38 local file targets, all 13 fixed source pins matched their approved before/current responsibility | `static-handoff.json`, `provider-pin-audit.json` |

The 32-part/max-identifier ACK case is a conservative response-envelope budget/binding stress through the pure validator, not an actually transmitted 32-part POST or throughput proof. Callback failures, malformed UTF-8, missing/extra members, 201/418 and foreign error namespaces do not create ACK/retirement. Real journal file-size I/O faults are confined to a marked child and its limit is restored. Freeze/dispatch/ACK SQL rollback, five durable crash positions, references, eight frozen cap, 3:1 scheduling, 202-round unbalanced PLCs, per-PLC/group rotation, source CAS and monotonic wall-jump rules are exercised without actual HTTP.

Test builds retain the existing config/mod.rs empty_for_test warning. Initial BuiltCycle.context_sha production warning was removed by using the necessary cycle.context_sha256 member in tests. Initial canonical mismatch, transient test/TypeScript compilation errors, incorrect schema helper handling of CREATE UNIQUE INDEX, and worker-time slice compilation error are preserved in earlier logs and were corrected without weakening assertions. Two stdlib evidence-helper attempts failed before producing a report (oracle assertion / ambiguous payload column); the corrected read-only report is separate from product test evidence. No test skip, compilation or source-string assertion is called actual HTTP, native visual evidence or independent QA.

Tool versions: `rustc: rustc 1.89.0 (29483883e 2025-08-04)`, `cargo: cargo 1.89.0 (c24e10642 2025-06-23)`, `node: v22.19.0`, `pnpm: 11.11.0`. Rust package version remains 0.1.0; bundled rusqlite/libsqlite3-sys dependency versions remain unchanged.

### Real hot-journal blocker: durable evidence

Exact parent command: `TMPDIR=/private/tmp/daa-008-r1-a-xsm2qlrl/development cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib crash_real_hot_journal_recovers_atomic_state -- --nocapture` (no extra feature). Parent exit101; log `crash-hot-first.log`.

The actual child argv was the test binary under src-tauri/target/debug/deps with `--exact infrastructure::local_store::delivery_tests::crash_child_uncommitted_ack --nocapture`, `DAA_008_SYNTHETIC_CRASH_CHILD=yes` and the exact owned path below. It updated parts/sample_delivery/batch state inside an uncommitted transaction, asserted sqlite3_db_cacheflush return0, then called libc::_exit(86). The parent's exit-code assertion passed. Reopening then failed with:

```text
known v3 hot-journal recovery must preserve complete prior ledger:
time_profile_unsupported:attempt to write a readonly database
```

Fixture: `/private/tmp/daa-008-r1-a-xsm2qlrl/development/store-d370e482-0324-4d44-bdfb-fc078a01ec29`. Journal bytes `42496`, SHA-256 `450a67306d259678ebcf6088ac2b1e5d524d8b856715524a1becf25e63721930`, header `d9d505f920a163d70000000ae2988c030000002b0000020000001000`. Runtime bytes `176128`, SHA-256 `34e1308ce6c10ce9251dbeca7c1c349e2a090fd111c287cd80af9798e81a8127`. The journal is retained, not opened through SQLite or recovered again by Development.

The initial parent held its before-original Vec only in memory; that before snapshot was not durably captured. Consequently this failed case does **not** establish post-recovery SQL/table invariants. A read-only contiguous UTF-8 extraction (no SQLite/immutable/recovery) found payload SHA `7117cae4d8a6a81a197f2dbe3b32330c025458dbb72c2d74d6ff6d089ee7a7fa`, manifest SHA `22dc8792c4dac7996b335e886e314f22d7e3eb288f465d6929447bc854e27267`, context SHA `029466a7c25242273691a4ae957a00c44e52fc6a8a987312f8e3c055f206ba42`; this is raw observation, not a substitute for rollback proof. The test now writes its before JSON for future fresh QA, while retaining the same failing recovery assertion. The known failure was not rerun wastefully under a bypass.

Successful worker fixture `/private/tmp/daa-008-r1-a-xsm2qlrl/development/engine-38377ad3-a016-4bc0-8945-ec7b5856241c` independently retains two acknowledged samples/two cycles/two receipts and zero references after stopped reopen. Its exact original strings and SHA checks are in worker-originals-evidence.json; the public-seed/identity comparison returned true for both payloads, manifests and contexts.

- SourceSeq `1`, sample `dc90671d-d962-4d1e-a71d-c0bfdc1caded`: payload `a34a6e66afba43ebf9431914d03bbda2fcf5be8c2d928ae9a79575a442da5108`, manifest `41d136a906112332e1e706095f21ef866ecfd7dc26ff0a831a40a53cfdfd8bb4`, context `029466a7c25242273691a4ae957a00c44e52fc6a8a987312f8e3c055f206ba42`.
- SourceSeq `2`, sample `d96eaea3-bba0-4e4e-9179-4a897399d326`: payload `d63ec7dccfa896f2df6002380ade271ff700ffe9ee7522d41483323a9aeeacae`, manifest `bcfec70797dc0ed49d62300794dceb6579a430db7457376f876f7f45e34174fe`, context `029466a7c25242273691a4ae957a00c44e52fc6a8a987312f8e3c055f206ba42`.

### AC mapping and still-open gates (DEV observations only)

| AC | Development observation / boundary |
| --- | --- |
| AC01–03 | Exact revision/pins/allowlist fixed; no existing env/profile read; synthetic v2 data and schema preserved; new2/3 and rejection guards exercised. |
| AC04–06 | Lossless vectors/numeric/time/fragment limits and frozen identities exercised; no actual Backend duplicate-write proof. |
| AC07 | Independent period, fair persisted PLC/group rotation, 3:1 opportunity, eight cap, real single-worker substitute observed. Actual HTTP/field load is B. |
| AC08 | Typed ACK/failure/rejection/read matrix and conservative 8MiB response bound observed through substitutes/pure rules. |
| AC09–10 | Same-runtime transaction rollback, original bytes, unknown identity and durable non-hot crash positions observed. **Real hot ACK crash recovery remains blocked; not full completion.** |
| AC11–13 | Failure classification, legal parent subset, settings CAS/source-change boundaries, physical reserve/retention and bounded read diagnostics exercised. Actual provider lifetime/window/cross-system behavior and adoption belong to B. |
| AC14 | Actual substitute worker lifecycle/stopped reopen/lock release observed. **Interrupted hot transaction recovery remains blocked.** |
| AC15 | Build/Node/i18n/column and original-display checks observed; native dark/light/narrow-window visual evidence and Owner M05 remain B. |
| AC16–17 | Fixed Rust APIs/guards, no arbitrary request/ACK/SQL, bounded/redacted events, formal-tree/snapshot consistency and records checked. No ACL/enforced-routing claim. |
| AC18–20 | Unexecuted: actual HTTP/DS/MySQL/Docker/target-source adoption, Owner native ledger comparison, full Stage C QA and final Owner acceptance. A-only is not complete Stage C. |

### Dependencies, resource ownership and next actor

The sole Development-owned root is `/private/tmp/daa-008-r1-a-xsm2qlrl/` (development subdirectory). It contains synthetic SQLite/logs, controlled child output, public-source evidence snapshots, intermediate/final receipts and regenerateable check artifacts. The one hot fixture above remains a necessary QA/r2 dependency. No server/listener/DS/MySQL/Docker process, branch, worktree or real env/profile was created. All test child processes exited; the actual-engine test explicitly joined worker/store and reacquired the lock. Existing shared src-tauri/target and ignored DAA dist caches were used/extended by approved compilation/build, not treated as isolated delivery source or safe-to-delete private resources.

Retain the root, final candidate/diff and hot fixture until fresh Verification/r2/Owner evidence no longer depends on them; then the coordinator inventories ownership and performs permitted cleanup. No real profile, old historical data or original joint-test resource is a cleanup target. No source is left solely in a temporary copy.

Next is a new fresh-context Verification of this exact partial r1 candidate and the real blocker. It must preserve the failed test and distinguish A-only observations, hot recovery failure, B gates and Owner acceptance. PM/r2 and precise Owner approval are required before introducing a new recovery trust boundary. Development has neither supplied a QA verdict nor granted final acceptance.

### Changed file receipt

Full before/after SHA-256 values follow; new files use `new` for before. Paths are relative to the DAA root except root CODE_INDEX.md. The complete finite 52-file enumeration, including unchanged allowlist files, is in the final manifest.

| File | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| `CODE_INDEX.md` | `c167b573b25a27ea275cac62a6a772a76a7ee5efbbb9bb0752de848340600d85` | `6a0272fc22f5516dbe3797c8c1b9819fdcf95ebd5007f758c77fa760760c7514` |
| `README.md` | `3dd94d7adf6e79121f6dd536b7bf881da690cdc0edc676c53a1e95bec38577e8` | `d471d224d3269f3a4763924f992d4182120e28dfec1b38be837d816e2c814330` |
| `README.zh-CN.md` | `97f50d7a1be7f78f5dcfb997eba8538e5a7a6c477dd1a9dedb041ebe99e14742` | `67839e70367a7ea0be00a42472ac89ce05cdf8688e3dd73f2aa7057de068a489` |
| `STAGE_C_GUIDE.md` | `new` | `250192d1d65115e2a9faed34e4b100c501d54b3d14b36127cb313e9d2423c320` |
| `STAGE_C_GUIDE.zh-CN.md` | `new` | `fd956c13c6b9467f92e888ef537b9545e94cec0f6ca68e3471ecd5959332818d` |
| `src-tauri/Cargo.lock` | `0fd260eb50278b28e6b3a2e016dcc18ed6a4030b0c95a2a828db8ddcbfc05a61` | `3689918ee18e16f63357ceb92811bbcf6019486b38ea747853638073e26b18cc` |
| `src-tauri/Cargo.toml` | `6ca767c287b9118449027671684b3fd4dea5d4503d266d09a5d8cc22bd92c88e` | `bc8e6ae9bc74e6a9dad963e1b1b5df96fb927d9ba866eeb1c19ee3b30f472d2e` |
| `src-tauri/src/commands/local_acquisition.rs` | `61c8b1bc03298117e329fcc67347fcc8ff582049979dc2c2b0901422cca47167` | `f7c5a73282d2d462897f76f5861ed11a6a0952c7c0ac62cf5978e70f74f589f5` |
| `src-tauri/src/commands/local_delivery.rs` | `new` | `5ad21f9c9cfd2534da96fc226459f725679613c6ccf70248aad461fd517710c3` |
| `src-tauri/src/commands/mod.rs` | `b7768385b916d81faed1cdd1b52a24ee3d99373782c0532655cd4a1020e297f8` | `dbc2485d9bf3e9e00ae9120e8bc59b983bc169811c0a0b6ec51b845e4f581f3f` |
| `src-tauri/src/domain/facts_canonical.rs` | `new` | `504a541bd8507e0b5dd25fecd832de675cf4e81e47584be6e1277191dda15943` |
| `src-tauri/src/domain/facts_canonical_tests.rs` | `new` | `839545e518b29ceba073d291fb8d534ac8ae720cfcb5bb1ec50984f0f532b1ec` |
| `src-tauri/src/domain/facts_wire.rs` | `new` | `f857eb79280011466b2192a6e170ae082fbbf774b785a4388df65a8faf8f8ed5` |
| `src-tauri/src/domain/local_delivery.rs` | `new` | `416e6b58c90c8bc207e336cebeac00c7d69f8c6eaf6c122fd04e069bbac1eff6` |
| `src-tauri/src/domain/local_runtime.rs` | `a305a88a3388b0a52d69ccdf6f80501cc90524f6ee6b0a55c7f27156f5266ce7` | `f123494df4c39385792c8072a6c7d28dace8de16e135611496e80cd143b00a1e` |
| `src-tauri/src/domain/mod.rs` | `e192fe45f1777e797b73f4f1e2397158d1c902a67459dc4c6cf381b880c3326a` | `3111482e1efc1403bdab5ba19735dc5564114664edb1562ba740f16021494311` |
| `src-tauri/src/infrastructure/facts_http.rs` | `new` | `0065344297fb1ef2a3aeff26afcfb345ca43f3be69217e56fe1205ced43c73bc` |
| `src-tauri/src/infrastructure/facts_http_tests.rs` | `new` | `a187ef39e26994454e09f5346044b1f3f8f1c72c4c33f78f9065e24a515447c1` |
| `src-tauri/src/infrastructure/local_store/README.md` | `6ab7be131260d58e248094c21abe44da1242984e1ede38cc0935d3a6bdadb7fb` | `d76e49d03002befb7f2dfdf1c4603a312318ed03430d0a5eacda585bd9615175` |
| `src-tauri/src/infrastructure/local_store/README.zh-CN.md` | `c86279cebb6bacae838767d340d73b8e40dca778d8571f71856bcdba8642821a` | `766e76a15405bb637c0aad5b68324545a43f7ef217ad986d12604184f84a9e31` |
| `src-tauri/src/infrastructure/local_store/capacity.rs` | `81dcfa4c94fe3ff789b6b350b0505d09355145e316e81a67d0276e1be9b844dc` | `6edaa6c29fe55ce8faf47245618b535b51fef1d2bc4a477c489359f42dfbf5b1` |
| `src-tauri/src/infrastructure/local_store/delivery.rs` | `new` | `078eac4c89d704eeb79b467e8ee1d5f837877054cd59f3f2e75cb275dee9b37e` |
| `src-tauri/src/infrastructure/local_store/delivery_tests.rs` | `new` | `04631bb227f9775dfe1c0e755dc194f01bcfd04172a756e7764700c26f4fe1cf` |
| `src-tauri/src/infrastructure/local_store/mod.rs` | `2125fcd576154cb9f1c6d598b241b23af7a0df995fc626e3b6632ded892fb990` | `910bc481da945f17e5b92c73432c48564f87677c1b63561144d4b64537058027` |
| `src-tauri/src/infrastructure/local_store/runtime.rs` | `970239ed7f79c88cf43f846aabd7d883f684861ce487e8577992960058dc9d66` | `c79a08081e8fdeb4a80f176e5980af6160252bd3bf5802ea0d813b859cf1f47b` |
| `src-tauri/src/infrastructure/local_store/schema.rs` | `c8c2189bd24bc427833fbe98d2a6b8b8c1f99a00e6b7e64a46e3afe26f922d81` | `d695180f02d244b8d5efb8efdbcb33306aba3a4155c1086db6c81d5bafd194af` |
| `src-tauri/src/infrastructure/local_store/time_contract_tests.rs` | `728253b5200a398a1f51dd69959eb54df0998af27fa2c13390cc06c1e86fde51` | `d69b942119e01fcde3a2ca9f5048d7535fba132038e906b7e5c381b83791d363` |
| `src-tauri/src/infrastructure/mod.rs` | `a6750fc68e67dc738063beb359ad1b7da5469e462f924cbb8f12ddbf83e725d8` | `90cf8b9ddddeea03b4569c7befb0133d66c0f01b2bc154473416745d905faf89` |
| `src-tauri/src/lib.rs` | `3dc85db7b60206aee41523961fe6af25145469223f3b6723d4f9abb6e73b9b97` | `9266b4790eb4c57864cb4d260f394abfafbcb71891d5cd0b7dcd88dea55c36f0` |
| `src-tauri/src/services/local_delivery.rs` | `new` | `64b182acda44f9d89b18e61bc194662842ec10a8cc5f8a7eea8039a9ac43c897` |
| `src-tauri/src/services/local_delivery_tests.rs` | `new` | `462ef420afb0df6373ab847566ebfee97efc48cd59f0d8c72d7f09575d6f2cae` |
| `src-tauri/src/services/local_supervisor.rs` | `a99ba74dcdda6735f674054946c2dae922e0a2c737c9c504c1925f309d90dc6e` | `e331cf547b72e3dcbc7343b5be9b17cb5b9304e28a2fab4842a9596c7fb4e1e6` |
| `src-tauri/src/services/mod.rs` | `1dd5259d9c0723baa359274618935007243f66c147973e913bcadbbab45eb883` | `040898a98d7188f71f83b4b6dbc4ccb37e967f396177fee4ba7a471233363444` |
| `src/app/collection/views/storage/index.vue` | `d97c7a883e8a486b411dc0713f2d8682b402f570c6157912b9f826bb907fb8f2` | `598e3dab17cc1b815aa5bca5018388f5e6b762f6f44a89fccb13d7301f880117` |
| `src/app/runtime/views/overview/index.vue` | `187f7d753e23d268822d4afbf0d3e38d176d14bf93f83db12c32a6059cce5b5b` | `546fddd8ca20a257a06dccc24b786901a49f16f5b2ec370cc618c11d308adaf4` |
| `src/components/console/FactsDeliveryDialog.vue` | `new` | `9172b559dc2c2805388f946ddea7ed39cb5d20940cc94e3a435a0fa8045fcc8e` |
| `src/components/console/FactsDeliveryPanel.vue` | `new` | `68f2503da54df55f99931bc411b4b7ecf5bb42b4b3a6e39f6e89d30339398df9` |
| `src/components/console/LocalSampleDetail.vue` | `fe6bebf4f02cb06be33f9d61136bc7c6dd29f9117cc950b34548e86edafbbd75` | `108a633a0a1be84f933952f93a05566df85dd1c5b98324a7b0685682d0794a13` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `c855c63d6a3902b274be2b29201482ba2486871a778c78affb8448d51dda4a2a` | `ef523ea307049f52ed3f3c2123dcaf8bddb9a92afef0054c7e2ad3b7268f75aa` |
| `src/locales/en-US/common.json` | `a79cf6976c3068d395d9738f205d9c8d37d4058d9a0eab7ffcd5373475b272e7` | `3b1cfb51dc617a502ca832f4b867a4030e57a95a47a71fbd22f235158dce877c` |
| `src/locales/zh-CN/common.json` | `4937c78a08fcec597ade0267479be30c39edd3ddec986cadf6dc2f0f06de9c3d` | `edd14a419c65eb8b8a28c69cb0e530b8438ca91098b1ad0447051ab398eec74c` |
| `src/services/factsDelivery.ts` | `new` | `351ec1f15a82d344cdbfc76d2e889917f99a9ee4213425f42a029a9a693f2585` |
| `src/services/localAcquisition.ts` | `1a855f274176a4250765205a27d3be3b104e67199d6cfef670c41bf7b2eaec5d` | `c685e208236c4f5a2124e2c6f0c92d770bb5438fd15176267f608a240e83d0e2` |
| `src/styles/app.css` | `a15b7ae6b3e12a4de7567f02de025ca043f79308c3aa91535bff0db143a2cdbf` | `744adc3c7d133afb90af9dd9a4415a6abc9bb315777ca162f4cd6cb6f2af81dc` |
| `tests/facts-delivery.test.mjs` | `new` | `ef1e13c19f259b05b7b03d1d80b5bd6791f96e169f503aa793b357368923fa10` |


## QA1 r1 有限返工（implementation_in_progress）

2026-11-05：按 coordinator 指派重新开放源码冻结；消费独立 QA1 `qa_failed` checklist SHA `eab00b347a3b81350f64d5073f1f05bd333fdf8e6f7ba0eaa42076b545ab63f1`，保留上述首轮部分候选和失败历史。仅修正 F-QA1-002（完整性/质量独立轴）、003（可证明 sourceSampleComplete 不变量）、004（真实互斥样本分类及两卡显示），并补 AC12 新合成 SQLite 合法 ACK/事务/物理空间证据。验证只跑受影响 ACK/read/count/budget 及必要构建；无真实 HTTP/设备/既有 profile。F-QA1-001 热 journal 恢复仍开放，未批准 r2，不改写前门禁。返工前基线为 `candidate-r1-partial-manifest.json` SHA `a99d85980d9ae8323d15a5824848a0ea1a0d4f46a4117f35cfb2e305a796076a`。

### QA1 返工部分 developer_handoff（dev_blocked，非全 A 完成）

仍为精确获批 r1，spec SHA `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae`；上述 QA1 checklist 未改。19:26 中间冻结因 PM/协调明确解释的同语义 8MiB 格式空白资源压力测试而重开；最终实现冻结 `2026-11-05T11:33:12.048185+00:00`。以下仅为 Development 修正/self-check，不代替独立 Verification 关闭 finding，也不授 Owner 验收。

- **F-QA1-002**：删除 qualityGood ⇒ complete 错误耦合，保留 complete iff received==expected、成员/身份/摘要/received 上下界。若本批原材料或历史 projection 明确有 bad 事实则不能 qualityGood=true。固定 provider 原材料正例证明部分全 good 可接受；历史 partial-good、partial-bad/false 和 bad/true 反例均覆盖。依据为只读 async_ingest.py 的两轴逻辑，不以 QA probe 为唯一 oracle。
- **F-QA1-003**：单片 false 必拒；本批送齐该样本且 created，或本轮 complete 且该片 created 时也必须 true；true 时 receivedParts 不得小于样本 parts。后来轮完整不改历史 duplicate/historical_committed 首次缓存 false 的合法性。正反例覆盖以上边界。合成 receipt helper 独立计算质量和样本片完整性。
- **F-QA1-004**：新增真实 sampleCounts.{unfrozen,frozen,needsProcessing,acknowledged}，按 sample_delivery 主键互斥分类：acknowledged 优先，其次需处理，再 frozen，其余未冻结；原 pending 总数及 batch-state counts 保留。blocked/expired_unconfirmed/needs_review 归需处理；prepared/inflight/retry/unknown 和固定后未派发分片归 frozen。真实 SQLite 断言覆盖同一样本两片、多个批/诊断引用不重复计数，blocked/expired 运行状态。两页共同 panel 显示四类及原总数，双语说明单位与总数关系，指南同步。

### AC12 三层证据（DEV，不含 F001 热恢复）

1. 全新合成、通过 Configuration validate 的256点/32DB/32读取配置，走真实 activation/commit_cycle/wire builder/freeze/严格ACK/SQLite。请求383660字节，32片共256点，compact ACK27230字节。proof 按固定 provider retention.py:40 为 committedAt+120天，原值期限 observedAt+3自然月，serial 用 signed BIGINT 可持久的 i64::MAX（19位）。
2. 独立逐 typed 字段编码枚举（不是可发送回执）穷举固定字段名/标点、版本/枚举/UUID/71字符摘要/35字符时间/19位serial/bool/u32。无点列表 result 保守753字节；空数组 envelope1112字节；一轮 cycle437字节。客户端一批一轮、32 result、组内256点；最宽128 UTF-8字节 ID 按258 JSON字节+1逗号计。枚举上界 `1112+32×753+31+437+256×259=91980`；松上界 `32×1024+256×259+2048=101120<128KiB`。各字段独立最大值过估联合情况，不伪称为合法最大请求。协议32×512点理论上限另列。完整键集对照实际ACK，见 rework-qa1-canonical-ack-bound.json。
3. 按 PM 只读解释及协调授权，同一完全 typed 合法 ACK **仅增加 JSON 格式空白到8388608字节**，标为客户端接收资源上限压力，**不称 provider 普通输出**。真实 strict parse/保存原文及SHA；TEMP trigger 在事务内观察 journal，RAISE(ABORT) 后 receipt=0、原 runtime SHA 和 payload/SHA 守恒，再去掉故障真实提交、确认32样本。未添加未知字段或重复ID，保留活 journal 副本及SHA。

| 8MiB 压力实测（字节） | 数值 |
| --- | --- |
| 原 main / 峰值 main / 新页增长 | 1110016 / 9515008 / 8404992 |
| rollback / commit 活 journal | 30240 / 79488 |
| reservedBefore / reservedAfter | 102889592 / 119715992 |
| request / receipt / metadata（前→后） | 383660→0 / 0→8388608 / 212004→212004 |

预算分工：旧页 journal 上界 `pageCount×(4096+8+sector)+sector`，本例271页、sector4096，得到2226296；四轮 B-tree预留33554432；既有维护预留33554432；**额外 ACK/恢复预留33554432**，合计102889592。实际 journal79488只计旧页预算，新页增长8404992只计额外32MiB，不重复计账、不借用四轮或维护预算。原响应SHA `sha256:a512186dc6fee83abeda4136a2a7acd62c7678c09dd2da8cb9e2c00637de65a4`。完整 before/after、journal SHA 与capacity见 rework-qa1-ack-budget.json / rework-qa1-reserve-audit.json。最终fixture `/private/tmp/daa-008-r1-a-xsm2qlrl/development/store-756ced0c-3560-4f63-afb9-2646c83479f2`。

失败/修正历史：budget-first.log exit101 为本次夹具缺 leaf 结构/地址确认依据，validate 正确拒绝，随后只修夹具。budget-final.log 曾误用24h proof/u64::MAX；协调指出非provider可产生回执，Development撤回其“合法预算”含义，修为120天/signed BIGINT后仅重跑预算例。budget-provider-final.log exit0及27KB证据 rework-qa1-ack-budget-client-cardinality.json 保留；8MiB最终资源证据单列，旧日志不改写。

### 本次命令、结果与限制

共同 cwd 为正式根工作树；显式 `TMPDIR=/private/tmp/daa-008-r1-a-xsm2qlrl/development`。Cargo 使用既有依赖/锁 `--offline --locked`。下表 test 使用精确前缀 `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib`，filter 后均为 `-- --nocapture`。全部日志位于上述 TMPDIR，文件名有共同前缀 `rework-qa1-`；完整 argv/cwd/env/exit/日志 SHA 见 rework-qa1-commands.json。

| filter / 命令 | exit / 结果 | 日志后缀 |
| --- | --- | --- |
| receipt_partial_quality | 0 / 1 pass | partial-final.log |
| facts_http | 0 / 4 pass | read-final.log |
| delivery_sample_counts | 0 / 1 pass | counts-final.log |
| ack（受影响有限回归） | 0 / 16 pass | ack-regression-final.log |
| delivery_client_cardinality_and_max_response_ack_sqlite_budget | 0 / 1 pass | budget-8mib-final.log |
| cargo fmt --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --check | 0 | fmt-final.log |
| cargo check --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver | 0 / 无新增 warning | driver-check-final.log |
| node --test tests/facts-delivery.test.mjs tests/sample-details.test.mjs tests/time-and-history-preferences.test.mjs（cwd=DAA） | 0 / 13 pass | node-final.log |
| pnpm --dir automation-world/data-acquisition-agent build | 0 / vue-tsc+Vite | build-final.log |
| python3 /private/tmp/daa-008-r1-a-xsm2qlrl/development/rework-qa1-budget-audit.py | 0 / typed枚举、SHA、预留分解 | canonical-ack-bound.json / reserve-audit.json |
| git apply --check --reverse --whitespace=error-all /private/tmp/daa-008-r1-a-xsm2qlrl/development/candidate-r1-qa1-rework.diff | 0 | 最终receipt |

部分 test feature 仍有未改模块既有 empty_for_test warning；Node shell 启动有 /bin/ps 环境限制提示，Node 本身13 pass；前端构建保留既有 PURE/chunk size 提示。未把源码字符串断言/编译称为原生视觉或真实 HTTP 证据。未重复 Stage B/后端/DS 全套；只读 provider pins、spec/checklist SHA 无变化；编辑指南的本地链接均解析成功。

### 冻结候选与资源

正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，entry HEAD `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`，未创建 commit。52项有限实现面、累计45变更，相对首轮最终候选13文件返工。完整 manifest/首轮→本次 diff/entry累计 diff/after 字节副本在 `/private/tmp/daa-008-r1-a-xsm2qlrl/development/candidate-r1-qa1-rework*`；tasks 最终 SHA/完整差异由 handoff-qa1-rework-receipt.json 记录，避免自引用。根四处 PLAN/catalog 归协调，不在本次返工差异中。

**仍开放 F-QA1-001**：真实 hot-journal 重开恢复失败，首次子进程/日志/原字节证据及 PM“需r2”裁定保留；未新增凭据、未放宽写前门禁、未再无效重跑。故本次仅 partial developer_handoff / dev_blocked，不能称全 A0/A1 或阶段 C 完成。AC12本次补齐获批 A1 的客户端资源/事务证据，hot恢复仍另项未闭合；AC18–20的实际 HTTP/DS/MySQL、Docker、原生视觉/现场/最终验收均未执行或未批准。

沿用唯一 DEV 自有根 `/private/tmp/daa-008-r1-a-xsm2qlrl/development/`，盘点248个 runtime.sqlite（496个合成双库文件），无新增外部环境/监听端口/运行后台 worker。新旧候选、失败日志、F001 hot夹具、27KB与8MiB夹具及journal证据由协调保留到 fresh QA2/r2/Owner 不再依赖后触发清理，Development不抢先删除。既有共享 Cargo target 与忽略的 dist 源码构建产物保留，不清理其他会话资源。原配置/历史/真实dotenv未读取或覆盖。从此冻结源码/tasks，后续事实补充先报协调。

返工文件 before=首轮最终候选，after=本次冻结源码（DAA相对路径）：

| 文件 | before SHA256 | after SHA256 |
| --- | --- | --- |
| `STAGE_C_GUIDE.md` | `250192d1d65115e2a9faed34e4b100c501d54b3d14b36127cb313e9d2423c320` | `6e5a02c8f57e7e77f7438a57b8483d69e63258562e825f6df1e26a6fa4ff2d00` |
| `STAGE_C_GUIDE.zh-CN.md` | `fd956c13c6b9467f92e888ef537b9545e94cec0f6ca68e3471ecd5959332818d` | `1e003d1a5eaca4a0708b2906842a40f38b55dd870db16998d2a4b152ddd8952a` |
| `src-tauri/src/domain/local_delivery.rs` | `416e6b58c90c8bc207e336cebeac00c7d69f8c6eaf6c122fd04e069bbac1eff6` | `15f8fb76056819c0fc01b225837e9ef2414e895e6d555bc12bac951a9395ccf6` |
| `src-tauri/src/infrastructure/facts_http.rs` | `0065344297fb1ef2a3aeff26afcfb345ca43f3be69217e56fe1205ced43c73bc` | `96994e38a68af51b0794c413548bf90f025e037e435f01be804c929917017750` |
| `src-tauri/src/infrastructure/facts_http_tests.rs` | `a187ef39e26994454e09f5346044b1f3f8f1c72c4c33f78f9065e24a515447c1` | `68cf32df8868ab8974907192b12f0707688b0f5f20c5dfa1b427af9c734271ac` |
| `src-tauri/src/infrastructure/local_store/delivery.rs` | `078eac4c89d704eeb79b467e8ee1d5f837877054cd59f3f2e75cb275dee9b37e` | `7ddbbf634c51afe58a9173837a1fc3071445c07d0159993baa03a18dccc37d25` |
| `src-tauri/src/infrastructure/local_store/delivery_tests.rs` | `04631bb227f9775dfe1c0e755dc194f01bcfd04172a756e7764700c26f4fe1cf` | `9538185506a2eae604e167593b190bafdc995bdf3c3b08f2fb6b22603a0c77d5` |
| `src-tauri/src/infrastructure/local_store/time_contract_tests.rs` | `d69b942119e01fcde3a2ca9f5048d7535fba132038e906b7e5c381b83791d363` | `dfe1a4d3ed933989b4de9c6e232281f4e2c14e4a27a5211f0ad3b2d808d48ad0` |
| `src-tauri/src/services/local_delivery_tests.rs` | `462ef420afb0df6373ab847566ebfee97efc48cd59f0d8c72d7f09575d6f2cae` | `45ca0b7333bc55023b4092b03e4e3d6a57f19a84a09d8bb87a37dc8eb95615a7` |
| `src/components/console/FactsDeliveryPanel.vue` | `68f2503da54df55f99931bc411b4b7ecf5bb42b4b3a6e39f6e89d30339398df9` | `b5c214466174ac9e63a04545cdad7e51e7bc5e733e3f7de230ad790be3fd53ef` |
| `src/locales/en-US/common.json` | `3b1cfb51dc617a502ca832f4b867a4030e57a95a47a71fbd22f235158dce877c` | `7adb8c557a837ee554d3e0349ce53e706e39b72df9cc65a343a19271d6844557` |
| `src/locales/zh-CN/common.json` | `edd14a419c65eb8b8a28c69cb0e530b8438ca91098b1ad0447051ab398eec74c` | `a22405272d17f69e2e98b1b3a9a50dfdb7ca2b2f8133217492d995e044cf50fb` |
| `src/services/factsDelivery.ts` | `351ec1f15a82d344cdbfc76d2e889917f99a9ee4213425f42a029a9a693f2585` | `8d132bbbe67d0212bd42646d3c84babe6a2f505afabcef53bd5cf3e13adb66bd` |
