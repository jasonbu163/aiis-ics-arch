Task ID: DAA-008
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: same approved r2 P2 fixture coordination exact source frozen 2026-11-06T11:28:24+08:00 -> sole coordinator /root -> NEW fresh QA3; default parallel22 and finite overlap passed, old parallel failures/cause undetermined retained; no DEV QA closure/Owner acceptance, B/AC18-20 open
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# Development事实与执行边界

当前有效实施见末尾 r2 开工记录；其前 r1 正文保留为历史，不据“当前/下一”旧措辞扩大或否定 r2 批准。

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

## r2 开工与精确范围（2026-11-06）

唯一获批spec SHA `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de`；批准稿SHA `4029dfedfda0dd8523e4fe9bee0fa5df3536f274c88ecb4a3dd89bc8ebdfb524`，Owner逐字原文见spec §16。上文r1事实与失败保留；原tasks SHA `287b64181b1420e888e5c4aa9d296793963500263381ff774b35487e12f1070f`，QA2 checklist SHA `eec8b82f5b444a7b125b9d4f76938ed1d4356c3ff1a790e32d4aa090f7422e84`。F002–004关闭/F001失败仅消费原QA事实，不由DEV改判。正式树entry HEAD `bcafa89fa31bdf62329bced89baebc193323a739`、entry clean；协调随后四处索引改动保留且不纳入实现候选。

1. A0：严格credential/sentinel/staging DTO、原inner UTF8/SHA、静态DDL fingerprint及精确extended776门禁 → 纯独立golden/反例。
2. A0：真实ProfileLock共用工厂、durable封存、单次native恢复及明确新基线；sealed cold/hot完整分页账本后检，之后才持久日志/业务 → 编译/结构审计。
3. A1：新r2目录初始化各步故障、cacheflush/_exit86、commit前后、恢复前/native后RO前/RO后业务前二次退出、锁竞争/漂移/拒绝 → durable before/after原串、完整账、物理journal与预算。
4. 收尾：最小双语诊断/说明/CODE_INDEX，触达回归/相关构建/链接/格式，冻结scope SHA/diff/命令/资源 → 新fresh Verification；实际B/完整阶段C另批。

现有private Stores::open(dir)统一取得父profile真实锁并持续到双库关闭；产品唯一locator仍为显式profile/local-acquisition-v1。历史private p/store调用仅内部兼容，同工厂/同严格门禁，本r2 A1及cacheflush子进程只用固定local-acquisition-v1，不改或运行范围外yaml测试、不开放产品locator。既有v2及未sealed r1 v3不自动补封。raw DB/journal FD在SQLite前全部关闭，776判定前保留原extended_code，不匹配错误文本。初始化辅助256KiB分配预算计入既有额外32MiB，不增加配额/依赖/env/feature/IPC/repair UI。

A0 implementation_in_progress；A1 planned；B未批未执行。不读取真实env/profile/8590样本或r1失败SQLite，不启动HTTP/loopback/DS/PLC/MySQL/Docker/GUI。coordinator独占notifier/邮件/四索引；Development不启动子agent、不改spec/checklist/local_profile_lock.rs/provider/wire。

本轮DEV唯一新资源根 `/private/tmp/daa-008-r2-a-fhgcwsig/`，development子目录为合成TMPDIR/日志/公开候选，stdlib mkdtemp新建、0700及canonical确认。保留到新QA/r2/Owner无证据依赖后由协调核归属回收；旧r1资源保持，不复用/open/seal。初次辅助heredoc因UTF8输入编码报错，尚未执行任何写入，随后拆成ASCII资源记录与apply_patch；不是产品失败或A1证据。

### r2 P1/工厂接线里程碑（持续事实，非QA）

`TMPDIR=/private/tmp/daa-008-r2-a-fhgcwsig/development cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib profile_contract_ -- --nocapture`：pure-first.log exit101（初版Vec类型推断/encode导入歧义），修正后pure-second.log exit0、3 passed：strict原inner UTF8/SHA/字段反例、独立DDL golden/缺约束、原始extended776正反门禁。随后factory-compile-first/second.log exit101，为接线闭包错误类型与移动后Value import漏项，均保留并修正，不登记产品QA finding。当前sealed-cold-first.log用于首条真实新目录初始化/完整cold后检，尚未以未完成输出记pass。

结构评审：profile_contract负责FS/原字节凭据/封存与native恢复协议，schema负责静态DDL及索引分页SQL账本关系，mod保留原队列/装配与共用typed SQL adapter，capacity统一物理空间及辅助分配。只新增已批两个文件；500/800行是拆分评审警戒，按以上责任在既有allowlist内安放，不为卡行数压缩或绕fmt。无新env/feature/IPC/repair入口。仅进程内canonical profile占用登记在任何raw DB FD之前拒绝重入，防止hash FD close释放同进程已有SQLite POSIX锁；跨进程仍依原ProfileLock，双库关闭后才释放OS锁/登记。

本地Configuration/context用独立重复键/尾随/BOM检查及原serde递归边界，不套pf-json depth20/十进制预算；合法未冻结/blocked原轮不以provider形状限额拒绝整个profile。wire严格限额只核已有delivery_cycles/冻结批/ACK。r1 delivery helper直接插plc-demo/config-demo等公开vector，不能证明sealed关系完整性；r2崩溃材料改走真实合法配置→activation→commit_cycle，旧兼容夹具在新根/真实父锁下从对应schema造起，不从sealed删marker或降级，不打开r1旧SQLite。

### r2 A1 首批实际结果与只读解释

A1已执行，不再沿用上文planned里程碑作为当前状态。sealed-cold-first.log exit101定位到issues数组被误交仅接受object的provider parser；修正为本地strict JSON后sealed-cold-second.log exit0、1 passed。hot-ack-first.log exit0、1 passed：实际合法配置/激活/commit_cycle及原commit_delivery，子进程在COMMIT trace前cacheflush rc0、exit86，真实hot journal与原始776；正式factory恢复旧账本/unknown/停态，另一个已commit后exit86保留新ACK。profile-matrix-first.log exit0、11 passed（含无参数child入口helper）：3个恢复二次退出边界、8个初始化持久checkpoint退出、13处初始化故障与no-replace、末次dir fsync错误当次拒绝/下次sealed cold全检等有限矩阵；不是11项现场或真实HTTP证明。gate-negatives-first.log exit0、2父测试覆盖15类marker/credential/身份/链接/头/WAL/schema/空NULL主键及双journal、锁前/native前漂移，无业务写入。日志/独立child argv/exit/原件均在本轮新development根；后续完整收据将冻结SHA。

实际PM经Root只读解释，approved SHA仍2d9ffde6…：末次sentinel unlink后目录fsync当次错误必须拒绝且不称完成；下一次若可见完整credential、无sentinel/staging并绑定匹配，可作为新sealed cold执行同等级完整账本后检，不追认前次fsync成功，也不称掉电证明。sentinel_removed后退出同理，不新增poison或重建marker。AC22缺失负例限当前材料要求凭据但欠缺：全部三aux无且无hot的合法v2/v3保留r1 unsealed cold，不补封；有sentinel/staging或776而欠credential拒绝，坏credential不降级，预检已见后消失按TOCTOU拒绝。本格式不能识别启动前外部彻底删除全部marker的历史；运维禁止删除降级，新增永久识别协议不属于r2。

profile-matrix-second.log exit101仅为兼容helper新增id()与facts_wire::id导入歧义，尚未执行测试；已用完整路径修正，保留编译原日志。当前继续独立坏账本/外部锁/大本地context/合法partial及父链触达，不重跑未变r1上传矩阵或Stage B。

## r2 Developer handoff（2026-11-06，A-only）

本节为当前事实；之前各里程碑及 r1 QA 失败历史保留。A0 实现与第11.1节有限新目录 A1 自检已形成可审阅候选；实际 HTTP/DS/MySQL/Docker/GUI、AC18–20/B 与完整阶段 C 仍未执行/未完成。**DEV不关闭F-QA1-001、不授QA verdict或Owner接受**，由新的fresh Verification核本r2 exact candidate。正式树仍为 entry HEAD bcafa89fa31bdf62329bced89baebc193323a739 上的未提交修改；无commit/push。

### 当前实现与冻结

源码冻结时刻 `2026-11-06T10:18:52.263407+08:00`，批准spec SHA `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de`。新54项源码集合=原r1 52项+仅新增profile_contract.rs/profile_contract_tests.rs；其中本轮18项变更，其余36项保持entry after SHA。完整逐项before/after在 `/private/tmp/daa-008-r2-a-fhgcwsig/development/r2-source-manifest.json`，SHA `00a4247e737ee31c831e60ef0dd868d62d994bb30e178cf19ed4665806b71236`。scope hash按sorted UTF8 path + NUL + lowercase after SHA + LF为 `fb312d01075d430bd6af44b70eb042cf0b8317bf4d97fbb1f9ae3ea8bb437c8a`；精确before差异 `r2-source.diff` SHA `5e5d9312cf18f823ff486e234188ee67c7e8bbac7e8e9b7a60a6b020684fe74a`。source-after/是正式树冻结的公开审计副本，实施/测试均发生在正式树，未以副本替代交付。四协调索引、spec/checklist及tasks不在source集合中；Root entry60文件baseline SHA36465683…保留。

已实现：严格原inner UTF8/SHA/typed凭据/DDL指纹，sentinel和no-replace封存、显式sync/close与失败保留，原OS锁全生命周期/进程内目录身份排他、所有raw DB FD在SQLite前关闭；仅新sealed精确776的一次默认VFS无CREATE原生rollback；sealed cold/hot同等级完整RO后检及明确post-native基线；之后才恢复原账本/日志/actor且仍停采停传。分页每屏≤100 key，首屏覆盖NULL/空key并拒绝坏行，不全量载入历史。capacity仅metadata核辅助allocated/256KiB子预算并等额减剩余32MiB，未增配额。独立本地JSON边界不套provider depth20/大小到未冻结或blocked轮。local_supervisor只消费统一Stores工厂，不再分持同一锁。

结构评审最终：profile_contract 828行（FS/凭据/恢复）；schema 801行（原静态DDL与有界账本）；mod 826行（原串行队列/工厂装配/typed SQL适配）；capacity 213行；测试1322行（独立故障/进程矩阵及完整durable对账）。超过500/800为明确评审信号，已按责任在获批两新增文件及原接线面内组织；未增加第三文件、未压缩fmt或跨任务重构。

### 实际检查与失败归因

共同cwd为正式根；所有Cargo tests均显式 `TMPDIR=/private/tmp/daa-008-r2-a-fhgcwsig/development`，无extra feature，前缀为 `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib`，filter后 `-- --nocapture`。完整argv/env/cwd/exit在各*-command.json、legacy-commands.json、final-check-commands.json；这是实际子命令exit，不以总wrapper exit0掩盖Cargo101。

| filter/检查 | 实际结果 | 日志（本轮development根下） |
| --- | --- | --- |
| profile_contract_ 首批 | exit0，11 tests（含无参数child入口）；真实hot/已commit、3二次退出、8初始化退出/13故障等 | profile-matrix-first.log |
| profile_contract_rejects_ | exit0，2父测试；15类绑定/marker/头/链接/WAL/未知DDL/NULL或空key，加双journal/两处漂移 | gate-negatives-first.log |
| profile_contract_ 扩充 | exit101，16 passed/2 failed；新增外部真实锁/低空间/目录inode别名/原生后坏账本拒绝通过，两个fixture问题如下 | profile-matrix-fifth.log |
| profile_contract_partial_ack | 修正fixture后exit0，1父测试：合法multipart partial ACK→cold pending→后续全片→cold仍接受cached partial；另合法拒绝→父token子批cold→子ACK后cold | partial-second.log |
| profile_contract_large_and_deep | 修正fixture后exit0，1父测试：合法2453152字节context/深层Struct，本地blocked、原文/SHA守恒并sealed cold准入 | local-context-third.log |
| v2_keeps_schema_configuration_history_ids_sequence_and_pending | exit0，1；新根原生config2/runtime2不补封/无投递DDL，旧配置/历史/序号/pending保留 | legacy-v2.log |
| unknown_reopen_same_identity_and_stopped | exit0，1；新根原生未sealed v3冷开保持原冻结身份/停态，不补凭据 | legacy-v3.log |
| unsealed_hot_journal_is_refused_without_recovery_authority | exit0，1；实际cacheflush/exit86产生新unsealed hot，拒绝且journal原字节保留，不伪称旧r1热恢复通过 | legacy-unsealed-hot.log |
| time_contract_legacy_unknown_single_and_identity_reject_before_lock | 修正旧helper断言后exit0，1；未知/单库/身份/WAL/schema保护 | old-time-guard-corrected.log |
| time_contract_lock_second_check_detects_empty_and_valid_drift_before_rw | exit0，1；原锁后漂移门禁 | old-lock-guard.log |
| cargo fmt --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --check | exit0 | fmt-final.log |
| cargo check同manifest --offline --locked --features rust-snap7-driver | exit0，无新增生产warning | driver-check-final.log |
| cargo check同manifest --offline --locked --features local-validation | exit0，原config的9个feature选择unused warnings保留 | validation-check-final.log |
| node --test tests/facts-delivery.test.mjs tests/sample-details.test.mjs tests/time-and-history-preferences.test.mjs（DAA cwd） | exit0，13 tests；无GUI/HTTP | node-final.log |
| pnpm build（DAA cwd，现有依赖/锁，无install） | exit0；原chunk>500kB提示保留 | build-final.log |
| 实际vue-i18n createI18n切en-US/zh-CN，common全keys对称及profile稳定诊断解析 | exit0；两语言均返回翻译非key | locale-switch-final.log |
| 6个双语手册本地链接/保护pins/git diff --check | exit0，38链接；10provider pins、原ProfileLock、approved spec/旧QA2 checklist一致 | doc-links-final.json / r2-protection-check.json |

没有在最后再全跑18项矩阵：16个已通过用例后的产品改动仅非Unix分支close_file拼写和等效Unix cfg限定；两个失败只改本任务测试夹具，分别定向复验。第三/四次matrix exit101是新增测试encode歧义及private classify/Reply import编译错误，未执行产品检查；已用domain正式接口修正。fifth两失败：comment1000超过本地500使import不确认、测试误读counts而非sampleCounts；local-context-second还因sources为空不进入候选（正常行为），第三次显式合成source候选先触发本地wire超限blocked。partial-first/second、local-context-second/third全日志保留；未削生产校验/放宽账本。old-time-guard首次exit101是seed现在经真实factory已生成持久锁文件，旧断言要求它不存在；现改核“拒绝前后原tree及锁是否存在守恒”，并允许sealed精确credential-invalid稳定错误，未知旧库仍原前缀。r1历史失败及原版断言在entry/旧tasks中保留，不覆盖成pass。

### 真实热恢复关键证据（持久摘录）

代表性新profile `/private/tmp/daa-008-r2-a-fhgcwsig/development/profile-e5502cc9-4447-4cb9-91b2-d029b0fa4494`。子程序为正式树 `src-tauri/target/debug/deps/aiis_data_acquisition_agent_lib-748dc1ffa2ece542 --exact infrastructure::local_store::profile_contract_tests::profile_contract_child --nocapture`，env_clear，仅TMPDIR/技术测试mode/profile；mode hot，实际exit86。真实commit_delivery COMMIT trace前 `sqlite3_db_cacheflush returnCode=0`，journal 58880字节，SHA `3f61876ffe82512db3c42a39f5be87138e24e33888045668b390970aab4bf05d`；RO probe实际断言原始extended776，未匹配字符串或primary8。子命令pid/env/exit/stdout与stderr SHA留child-hot-none-command.json，原journal副本r2-hot-journal.bin，完整原串表账r2-before.json/r2-after.json。

runtime物理SHA：native前 `2ce833abf24edd0fb04a3245c46a40895eb681cc71773854e3cabb0a0536fc29`，native后 `51d51ad380c60e5941bcbca75ee64c83ab5a976ab157e3376951bf4c59559ba1`，RO后同 `51d51ad…`，正常停态恢复事务后 `80fdf892c410ea7035b5be01483be781bf693b6ae8a77a82ca40895d98e9f097`。这是明确新基线，**不称DB未写/整体文件SHA守恒**。完整before文件SHA `7903c270c60ccad2a5e0bc06543f32bbc0c5f4c08ec390dab7e5e127fda2c54f`、after `5842769257cf2646e700c950dc461e50895135f3ee6d4cdf63ee8ca541a988e1`，因元数据/unknown事件合法不同；14张来源/配置/activation/原轮/sample/deliverycycle/parts/sample_delivery/ref表逐行原值严格相等，receiptCount0，原frozen batch request/body/digest/ID/seq保留，inflight→unknown且running=false。独立JSON二次对账及各表摘要见r2-hot-durable-summary.json。

已commit后exit86用独立新profile，严格等于durable after-commit中的receipt/parts/sample_delivery/batches/references新账；不能仅“旧或新任一”。恢复前/native后RO前/RO后业务前第二次exit86用各自新profile；第一次前退出无native变化，后二者journal已由SQLite去除，下次sealed cold仍全账本后检、原文与ACK原子保留及停态。坏old payload原SHA刻意不匹配的hot fixture原生恢复后报 `profile_recovery_business_admission_failed`，journal已由SQLite移除、native后SHA已变，业务拒绝；无产品自删journal/修复/补表。stdout区分recovery_write_completed=true/false，后检前不新建持久日志/actor。

辅助预算实测：sealed-cold-evidence.json中logical1379字节、allocated4096，子预算262144；旧页journal预算340296（实际sector4096），remaining ACK recovery33550336，allocated4096+remaining33550336=33554432；reserved100999496 + allocated4096 = old340296 + 3×33554432。两个加法分别证明子预算位于原extra32MiB、旧页/原四轮/维护预留另计，既不把实际aux再完整未来预留双计，也不借原旧页预算冒充新额度。注入可用空间计量0的初始化与hot门禁均在native/业务前拒绝，原hot原件保持；不是耗尽真实磁盘。

### 限制、复用与资源

AC21–26及触达AC03/09/10/12/14/17的上述DEV证据交新QA独立判断；未变r1 wire/HTTP/调度/worker等沿用QA2有效证据，不重复40组协议或阶段B。partial cold测试为合法持久子集状态的有限夹具，生成于dispatch前，原样本/manifest/context不改；不证明产品现场会以该粒度派发或吞吐。8MiB合法空白ACK保存/普通rollback/32MiB压力证据沿用r1 QA2，本轮真实hot为合法普通ACK；不将阶段退出声称SQLite pager内部掉电。新profile处理risk：SHA/inode不是认证，无法完全阻止恶意同inode/伪造journal/非合作TOCTOU；1000ms仅busy等待预算不是OS I/O硬截止。macOS arm64实证不推出Linux/Windows/真实掉电保证；非Unix cold接线静态审阅/当前target编译不算Windows运行通过。两个实际PM窄解释见上，approved spec未改。

资源仅本次 `/private/tmp/daa-008-r2-a-fhgcwsig/`；合成profile/SQLite/journal/child命令/log/JSON/raw before-after/冻结source-after/manifest/diff供fresh QA和Owner审计，故暂保留。没有临时实施工作树；source-after仅公开收据，不是交付树。所有本轮子进程均已wait结束，未启动监听、GUI、PLC/DS/MySQL/Docker，无运行连接/进程需交接。Cargo target及pnpm dist为正式树现有共享构建目录，不整目录删除以免影响其他任务；本轮无新增依赖/安装。无证据依赖的临时夹具/生成物可在Root确认fresh QA与Owner均无依赖后按归属回收；r1旧资源/真实配置历史不触碰。下一角色唯一协调/root启动NEW fresh Verification；本Development现停止源码/tasks写入，最终receipt另存owned根，包含本tasks精确SHA避免自引用。

## r2 QA1 后有限返工开工（2026-11-06）

Root收到实际fresh QA `/root/daa008_r2_verification_1` 停写交接后，明确在原批准r2内开启F-R2-QA1-001/P1返工；approved spec SHA仍 `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de`。正式checklist SHA `137fe21ac4eaf3c1e5ccc89694cb971485587be67bbfc3c552b3f630cf31d003`、QA receipt SHA `01a27bb4909599c51ad372dda18a74ee182df808a5c84758f410347d1b6e4704`，均qa_failed，不改写。原r2 scope fb312d…/54源码和原tasks SHA1c429e…及其冻结收据保留。本节重新打开Development写面，不追认初候选全通过。

问题已只读定位：locked后cold分支重取快照接受非native漂移；checked重新按此时credential是否存在决定全账本义务，导致已见sealed可降级，native后凭据消失时坏原文SHA也漏检。计划：先在新目录用真实factory复现三个失败→最小修复本次已建立sealed/原凭据/目录/同伴连续性，cold不得换基线、native只允许指定pager材料变化且全检义务不能随marker消失→仅受工厂影响的阶段漂移/cold/hot/init/旧库兼容→冻结54文件两种diff交NEW fresh QA。无新协议/永久poison/补封/依赖/feature/env/IPC/第三文件；不改spec/checklist/原ProfileLock/Root四索引。

唯一新A1根 `/private/tmp/daa-008-r2-a-dedws2xe/`，development子目录显式TMPDIR，stdlib mkdtemp/canonical/0700；只新建合成profile，QA及旧DEV/r1 SQLite不打开、复用或封存，只读QA公开JSON/log/probe与冻结源码收据。A0/A1返工进行中，B/GUI/HTTP/DS/PLC/MySQL/Docker/真实env/profile边界不变。仍唯一Root协调/notifier，不启其他agent或外发；自有新资源保留到fresh QA/Owner证据依赖解除后由Root核归属回收。

## r2 F-R2-QA1-001 返工 Developer handoff

本节为最新事实。DEV已完成此原批准r2内的实现返工及有限A1验证，**不关闭QA finding，不称全A/全并发通过或Owner接受**；原QA1 qa_failed/三失败、原DEV候选与全部日志保留。B、AC18–20、原生视觉与完整阶段C仍开放。唯一新证据根为 `/private/tmp/daa-008-r2-a-dedws2xe/development/`，以下文件名均相对该根。

### 修改与精确冻结

正式树HEAD仍 `bcafa89fa31bdf62329bced89baebc193323a739`；source冻结 `2026-11-06T10:55:58.935861+08:00`。approved spec仍 `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de`，QA1 checklist仍 `137fe21ac4eaf3c1e5ccc89694cb971485587be67bbfc3c552b3f630cf31d003`，DEV未写spec/checklist/Root四索引。

| 正式源码（DAA src-tauri/src/infrastructure/local_store/下） | 原r2冻结SHA → 本次after SHA |
| --- | --- |
| profile_contract.rs | `bd30382fdebf76489d8a535c13fd7029c0f671e16e3844b1b6452f93101a7108` → `c6b6873d98d6446382d2465b608e6d471592f5852e8d6cf53bc804e021f2711d` |
| profile_contract_tests.rs | `0e82cfb33fe03c8d5acacfd2194ba1ad2d99b1571b2064630d60a44d69da4d50` → `1b092904a3051b150be597615cb081da5afaf44f35203dfb78fa69f86f69882e` |

仅这两个既有源码返工（894/1483行）；其余52个源码/手册/locale/依赖/入口SHA与原r2候选一致。责任仍FS/凭据/恢复与其私有测试，无新文件/结构/对外接口，CODE_INDEX无需再增段，不修改已准确描述的双语手册或重复UI构建。实现始终在正式树；source-after/仅为冻结审计副本。

完整54项 `r2-rework-source-manifest.json` SHA `49bf21d9c80c93acd7872f863ef3730c03dd2b131b0c50343a273510648eb589`；scope `6fd00d43b165268f1b175bf3e7cd106cbabb657601a1613678e9a3b5ff0e21fa`，算法仍sorted path UTF8+NUL+after SHA+LF。原r2候选→本返工2文件diff `r2-initial-to-rework.diff` SHA `dde87fa8d003d844b5fad01b4c6c16d20df64952c34e1aae785b75a5062bc474`；Root entry→最终18文件diff `r2-entry-to-final.diff` SHA `07e58beb84509b433a1efac3caaa589cbc153002fc5fb453e9c9e06bd708b814`。Manifest逐项列beforeEntry/beforeRework/after，保留原scope fb312d…，不包含tasks/spec/checklist/协调索引。

修复：cold全程以原preflight快照为expected，不接受locked后新SHA；本次sealed/full-check义务只来自原凭据或本次受控初始化的凭据，不再从当前marker重新分类。native close后仅允许失败库与对应journal产生pager变化，原目录身份/模式、原credential材料、同伴库等必须与原候选相等，再绑定已知头/文件身份，并固定新baseline；之后after_native/RO阶段漂移均拒绝，完整账本后检不能因凭据丢失跳过。初始化返回已核Snapshot/Contract；原DB在初始RO前后、安装前后相等，最终credential与本次staging原字节/身份一致，在sentinel_removed checkpoint前锚定，防止初始化完成到正常准入间又吸收漂移。没有增加永久poison、补封、旧库修复或降级识别协议。

### 真实命令与未定因并发失败

共同cwd正式根，显式 `TMPDIR=/private/tmp/daa-008-r2-a-dedws2xe/development`，移除继承DAA_*/VITE_DAA_*。前缀 `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --offline --locked --lib`；下表filter后均 `-- --nocapture`，串行另加 `--test-threads=1`。完整argv/cwd/exit/log SHA在对应*-command.json及affected-check-commands.json/final-source-check-commands.json，均实际子命令结果。

| 命令/filter | 真实结果 | 日志 |
| --- | --- | --- |
| profile_contract_rework_regression，修复前生产源码 | **exit101，0pass/3fail**；新自有三fixture全部错误admitted，真实复现QA，不是预期拒绝/编译失败 | regressions-before.log |
| 同filter，首次修后 | exit0，3pass；三个均拒绝，native后使用已写恢复而业务拒绝错误 | regressions-after-first.log |
| profile_contract_，默认并发 | **exit101，21pass/1fail**；原初始化fault例最后直接重取ProfileLock得到profile_locked，其余21通过 | factory-affected-final.log |
| profile_contract_initialization_faults_and_no_replace，单独定位 | exit0，1pass，原锁释放断言保留 | initialization-lock-isolation.log |
| profile_contract_，串行隔离 | exit0，22pass/0ignored；原故障/锁断言均保留 | factory-serial-isolation.log |
| profile_contract_，加仅测试失败现场记录后的最终源码，串行 | exit0，22pass/0ignored，44.81秒；含无参数child入口helper，不称22项独立现场场景 | factory-serial-final.log（SHA `4223055bef4b24dd89f18aca2d7ff7187790bb6acacbb51a2de26fc4cf643c6c`） |
| v2_keeps_schema_configuration_history_ids_sequence_and_pending；unknown_reopen_same_identity_and_stopped；unsealed_hot_journal_is_refused_without_recovery_authority；time_contract_legacy_unknown_single_and_identity_reject_before_lock；time_contract_lock_second_check_detects_empty_and_valid_drift_before_rw | 各exit0，各1pass；新造旧v2/未封存v3、不补封、hot拒绝与原锁/未知合同门禁 | legacy-v2/legacy-v3/legacy-unsealed-hot/old-time-guard/old-lock-guard.log |
| cargo fmt同manifest --check；cargo check同manifest --offline --locked --features rust-snap7-driver | 最终各exit0，无新增生产warning | fmt-final.log / driver-check-final.log |
| cargo check同manifest --offline --locked --features local-validation | exit0，既有9个该feature unused warnings保留；之后仅改测试失败诊断，产品源码SHA未再变 | validation-check.log |
| 保护SHA、source diff/UTF8/git diff --check | exit0；10provider pins、原ProfileLock、approved spec、QA1 checklist一致；其余52源码不变 | protection-check.json |

并发失败未被标pass/偶发：失败在原测试第570行立即重取自有profile OS锁，错误profile_locked；当时没有精确case/PID/inode/FD快照，不能事后补造。单独及串行通过不足以证明并发失败原因；“并发fork到exec前临时继承flock”仅为未核实假设，不称已定位或产品锁已证明无缺陷。按Root要求，在原断言Err支新增仅cfg(test)诊断：精确stage/profile/PID/lock dev/ino，本进程/dev/fd最多4096条fstat匹配该自有lock inode并记FD flags；不开关DB原FD、不重试、不修改ProfileLock或断言。最终串行未再失败，所以该新增现场记录未触发；原并发失败、隔离pass与最终串行pass一并交新QA判断。没有继续无关广测。

未变wire/HTTP/UI/locale/Node/build的52项SHA相同，复用初r2 QA1及之前QA2有效检查，不重跑UI/40协议/StageB/后端/DS。并发未知因限制继续开放；DEV不以串行pass授予全A verdict。

### 三核心反例修前→修后与阶段边界

`three-regression-before-after.json` SHA `d2ea99d567e3162f0152ac5028b06a2d6c370e95b440948f6dc3b4a551e86e11`，全部profile在本轮新根且彼此独立；每例before/after原候选/stat/len/SHA/credential存在性、注入与准入结果独立落JSON。修前3例admitted=true，修后3例admitted=false；修后注入结束到返回Err期间受控材料逐项未再变化。

| 反例 | 修前profile / 修后profile（development根下） | 修后错误 / 关键结果 |
| --- | --- | --- |
| locked删本次已见credential | profile-3f0fad53-546c-4b11-b24c-018c6ab40c38 / profile-d09bea6b-95de-4933-b838-00c76a56d397 | profile_contract_business_admission_failed，未降级 |
| locked同inode追加runtime原字节 | profile-f2e411e9-14d7-463b-abdd-ff826041e21e / profile-f9dafcee-727c-4522-9c76-0b042b34bab0 | profile_contract_business_admission_failed，未换cold基线 |
| hot_bad_old原生后删credential | profile-2bb12b62-f5aa-4674-9f8c-7fe9e0b0ff7d / profile-44463f65-8446-4847-8676-1f4e3d663973 | profile_recovery_business_admission_failed，明确native已写，原journal由SQLite去除、坏SHA未被准入 |

最强例修前/后均真实commit_delivery COMMIT前cacheflush rc0、child exit86、原始extended776断言；journal均58880B，SHA分别 `458cbc7c057ceb39f83bfe3aedd51734e31fe5f41e37a2aa2e4705067d0dff53` / `2c19dd30bb19b74c9cf5766ac18960912e46dc4423bb86ca8834cdecc315e3a6`。修后两条payload各7265B：sample eea901e3-604a-47ee-80a8-3e2b07cec11b，存SHA `ac8705f0c652e7933e6159caae8913ed23e4a51f9ae69afdf733dccea7834e29`/实际 `c4b1e1787a4c8432d6fa16d0018cdca18e361bffb7fa5f5183359321999312f2`；sample 27e7153a-1b00-46cd-ad34-af265a9e6fdb，存 `20f2cc35db7a33e86ee6e2515ce3cb7de006de50fe703f79de13b19ed0bcfa4e`/实际 `c847ea63b130150be824f6334dcb8ed58a7a13c8c5d4d153c58be81878ce302a`。这些从自有durable before原文JSON独立重算，不打开QA或旧库；修复不声称修好坏数据，而是拒绝业务准入。修后结果JSON SHA `a096472dc8fee8f8b3a419f626edf6b5ce8420f6270dea58c77c57ee98d143cd`，注入JSON SHA `7f2d48ae1920008f25a00a02ed9b374ca5fd20dd0af0a436798dd9c7b5dcf538`。

另11个有限组合覆盖cold locked改合法credential空白/after_ro缺失；native刚close、baseline前改credential原字节/换inode/改同伴库；native baseline后追加runtime/换credential、RO后再改；初始化initial_ro_checked改DB、sentinel_removed后删credential或改DB，均拒绝。正常cold/hot/已commit、三处二次退出、全账本坏原SHA/ACK、合法partial历史标志/父链、大本地context、容量及原初始化故障/no-replace继续由最终串行22项覆盖。阶段崩溃不称pager内部掉电或真实HTTP证明。

### 资源与下一交接

本次新增资源仅 `/private/tmp/daa-008-r2-a-dedws2xe/`（0700 canonical）：合成fixture/SQLite、durable JSON原账、原journal副本、全部真实成功/失败log/command、三反例汇总、54源码公开快照/两diff/manifest；留供新fresh QA/Owner，依赖解除后由Root确认归属回收。旧DEV/r1/QA资源和真实.env/profile不读取SQLite、不恢复、不清理；source-after不是实施/测试目录。所有本轮直接子进程及技术child均wait结束，无listener/GUI/HTTP/PLC/DS/MySQL/Docker，无新安装/依赖/feature/env/IPC/第三源码文件。共享Cargo target/dist不整目录删除。

两条PM只读解释继续原样有效：全部marker在启动前已无的合法unsealed cold历史不能被本格式识别；末次dir fsync错误不追认成功、下次完整可见sealed cold独立全检。本修复只保持本次已见材料连续性，不增加永久历史识别或认证承诺。恶意同inode/伪造journal/非合作TOCTOU、Linux/Windows原生与掉电保证仍是原限制。现Development停止源码/tasks写入，将精确最终tasks SHA和外部receipt交唯一Root，再启动NEW fresh Verification；F-R2-QA1-001关闭权归该QA，Human Owner终验仍pending。

## r2 P2 测试夹具协调开工（2026-11-06）

实际fresh QA2 `/root/daa008_r2_verification_2` 已冻结qa_failed并停写，checklist SHA `b74c0e90ae7b0d0a4076434352b150c55baebde99d825ec831058d21b00ff6c6`、receipt SHA `eeb9e8c172ea26c8a45542ca6fe07b4644e3bb91e29986f32e531c6c0d41ae21`。P1 F-R2-QA1-001 已由该实际QA独立closed；P2 F-R2-QA2-001仍开放，默认并发再现21pass/1fail、sqlite_close立即重获锁profile_locked；PID83784的有界现场扫描27 FD、ownMatchingLockFDs=[]，后续一次同inode flock成功不定位失败时holder。原DEV/QA并发失败、串行pass及未定因限制全部保留，不追认fork原因。

Root在原approved r2（spec SHA仍2d9ffde6…）明确只开 `profile_contract_tests.rs` 与tasks写面，生产工厂/ProfileLock/重试及其他53源码保持scope `6fd00d43b165268f1b175bf3e7cd106cbabb657601a1613678e9a3b5ff0e21fa`。方案：原13故障/no-replace及原立即取锁断言在现有helper启动的独立exact测试子进程内执行；子进程自己创建/打开各新profile、不再spawn子进程，立即取锁断言必须在退出前完成。真正跨进程hold_lock保留。只用cfg(test)/既有技术mode/argv/10秒界/JSON，无新依赖/feature/公共env/文件实现面；不削断言、不加生产重试或用退出清锁冒充。

唯一新私有根 `/private/tmp/daa-008-r2-a-w7gv433k/`，development显式TMPDIR，stdlib mkdtemp/canonical/0700；先核旧54源码与冻结逐项一致。计划：夹具所有权协调与原断言字节审计→默认并发factory矩阵、有限并发重复及逐case PID/identity/退出前重获证据→fmt/编译与54项新scope/两diff/命令资源收据→NEW fresh QA3。未变53源码/协议/UI/Node/build沿用QA2有效证据，不重跑StageB。原QA/旧SQLite/真实env/profile不打开或复用；无网络/GUI/DS/PLC/MySQL/Docker/子agent/notifier或外发，资源留到Root确认QA/Owner依赖解除。

## r2 P2 测试夹具协调 Developer handoff

当前只交已批准r2的P2夹具协调与有限A1证据；P1已由实际QA2独立closed，**DEV不关闭P2、不授QA verdict或Owner接受**。此前DEV/QA默认并发21pass/1fail、现场ownMatchingLockFDs=[]、串行22pass及旧原因未定的正文/收据均保留。新夹具通过不追认“旧fork根因已证”，也不声称旧失败未发生。B/AC18–20/完整阶段C继续开放。

### 精确源码与原断言

正式树HEAD仍bcafa89fa31bdf62329bced89baebc193323a739，源码冻结 `2026-11-06T11:28:24.994690+08:00`。approved spec仍 `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de`，QA2 checklist仍 `b74c0e90ae7b0d0a4076434352b150c55baebde99d825ec831058d21b00ff6c6`。本轮只改 `src-tauri/src/infrastructure/local_store/profile_contract_tests.rs` 与tasks；该test SHA `1b092904a3051b150be597615cb081da5afaf44f35203dfb78fa69f86f69882e`→`625b2b6787b39b95de22193e220b64fc713eaa7cdfc41b2bc459a719baa83c62`。其余53源码逐项SHA不变，尤其生产profile_contract=`c6b6873d98d6446382d2465b608e6d471592f5852e8d6cf53bc804e021f2711d`，原ProfileLock/生产重试/依赖/入口/locale均未改。不改CODE_INDEX或任何新文件实现面。

全部材料在 `/private/tmp/daa-008-r2-a-w7gv433k/development/`：54项 `p2-source-manifest.json` SHA `ebfa1abaca2d87f5f1d0ba13a018c9d07e89da93ef6b1c2dccadba84c8132e0c`；scope `26cebdb087c5aa4be93fd431bec1a54d253e104ca57fd5ee1d0b3a4e9aa57b7c`（原算法sorted path UTF8+NUL+after SHA+LF）；6fd候选→本次1文件diff `previous-6fd-to-p2.diff` SHA `9d3d0213f20631ea7425d48aaa3faecb46dd28f3c65dbb09f4f5c45669f56377`；Root entry→累计18文件diff `entry-to-p2-final.diff` SHA `bc7138f68bf185083845344bbedda5e3b0c4c8e4ae4c2fd1071e025c015bd258`。beforeEntry/beforeP2/after逐项记录，source-after仅公开冻结审计副本，实际修改/编译/运行均在正式树。spec/checklist/tasks/Root四索引不混入source scope。

原13故障与no-replace测试体移入同文件私有 `initialization_fault_cases`；既有exact child helper只新增测试mode值initialization_fault_suite，在默认Stores分支前调用并返回。父测试只准备控制目录和现有10秒界child，不预开任何case库/锁；每个case profile由该单一子进程从零创建/打开，case helper没有spawn，不再将相关锁FD先持在并发父进程。**Stores失败→sentinel重开拒绝→立即原ProfileLock重获→drop(lock)**的原断言整段字节相同，SHA `aad28a6c1a7498b7eee0fc5b62b2be29b8edb110d3c808ff35b75298d2e7dae8`；各个fault/no-replace原期待原样保留。真正跨进程hold_lock测试函数也逐字节相同。不是靠子进程退出释放来让父进程锁检查通过，case内断言失败仍原panic及fstat诊断，无retry/skip/降低期待。

每case在真实立即取锁成功并drop之后、子进程退出之前持久化stage/PID/parentPID/lock dev/ino/原错误/无日志/sentinel状态；套件report同样在子进程退出前落盘。父测试wait真实exit0后核实际child command PID、report PID及parentPID、13个case PID/成功字段，保留report原SHA。原释放断言/故障期待/跨进程函数原文审计在guard-audit.json与original-guard-preserved.txt，不只靠新增boolean字段作oracle。

### 实际有限检查与生命周期证据

共同cwd正式仓根；显式 `TMPDIR=/private/tmp/daa-008-r2-a-w7gv433k/development`，清除继承DAA_*/VITE_DAA_*。所有Cargo使用原锁/依赖 `--offline --locked`，无安装/新增依赖。M精确为 `automation-world/data-acquisition-agent/src-tauri/Cargo.toml`。

| 实际命令/检查 | exit及结果 | 新根内证据 |
| --- | --- | --- |
| `cargo test --manifest-path M --offline --locked --lib profile_contract_ -- --nocapture` | **0，默认并发22pass/0fail/0ignored，17.28秒**；没有serial override，含一个无参数child入口helper，不称22个现场场景 | factory-default-parallel.log SHA `c57a7409a4be13d788755e7d638c2cdf062266722a120054043607508e27ecf7`；对应command.json |
| 两份同时启动的 `cargo test --manifest-path M --offline --locked --lib infrastructure::local_store::profile_contract_tests::profile_contract_initialization_faults_and_no_replace -- --exact --nocapture` | 各0、各1pass；有限重复2次，不是直到pass的循环，无serial参数，实际case窗口重叠 | fault-overlap-1.log / fault-overlap-2.log；fault-overlap-commands.json |
| `cargo fmt --manifest-path M --check` | 0 | fmt-final.log / static-check-commands.json |
| `cargo test --manifest-path M --offline --locked --lib --no-run` | 0，编译测试而不再运行；既有empty_for_test warning保留，无allow抑制 | test-compile-final.log |
| 逐case PID/identity/原报告SHA/退出前断言及重叠审计 | 0，3套×13=39 case、3次no-replace；所有自有锁inode匹配原记录，原无日志/未完成保护成立 | p2-lifecycle-audit.json SHA `038cd1e2b67afea138573c4d63319cedae666946e940b1d7a5687a24fdac900a` |
| 原立即取锁断言/外部hold_lock原文；53源码/10pins/spec/checklist/原ProfileLock；git diff --check | 0 | guard-audit.json / p2-protection-check.json |

默认矩阵父PID11120、套件子PID11124（exit0）；控制目录profile-514e4b9f-6270-425c-96ff-caa44a340ba6/report SHA `c49a1dd66c7e1a6f8e3f168ee86274ca6509b43e468a8492d184fc4dcb58e736`。其sqlite_close case为profile-f55da7ec-ce75-47f4-891b-14c899113df4，lock dev16777229/ino80850821，11:24:48.926+08:00已在子进程退出前立即重获；firstError仍synthetic_profile_sqlite_close，sentinel=true、productLogs=false。

有限并发重复的Cargo runner PID12839/12840先全部spawn再wait；实际Rust父PID12843/12845、套件子PID12844/12847，均exit0。39条case并非来自父进程退出清锁：每组13条在相同child PID中完成，report及真实child command PID相符。两子case时间窗分别11:26:04.823–11:26:05.584+08:00、11:26:05.063–11:26:05.811+08:00，真实交叠。对应控制目录profile-148070af-25eb-4306-914a-cf4563d50a1c / profile-e1fa37aa-d4c6-4cd5-9129-8196d102a44e，report SHA `cdf0f7e2b0fbb2933cb8d98541b2c1718a11ab624ca87b9ee27ba1265ef8a31a` / `5bd14e09a13d6a2a16b3514ee663aaa1e0334831bae001b125bdd96e2bf9dc28`。sqlite_close锁inode分别80852382/80852475（同dev16777229），都在各自活跃子进程内立即重获。详细每case profile/PID/dev/ino/stage见报告及各自initialization-case.json。

本轮说明的是新的合法测试所有权边界下原义务有真实通过证据，不给旧失败定因。原QA2 P2仍需新的fresh QA3独立判断；真实跨进程排他测试未被隔离掉，仍在默认22矩阵原样执行。其他53源码同SHA，产品feature编译、协议/UI/Node/build/i18n有效结果复用QA2，不重复StageB或实际HTTP/DS/MySQL。没有新增产品修复、重试或平台保证。

### 资源与停止写入

仅本轮 `/private/tmp/daa-008-r2-a-w7gv433k/` 为新增自有根（0700 canonical）：新profile/SQLite/阶段退出原journal、39逐case JSON/3套父子报告/command/log、原断言副本、54公开source-after/manifest/两diff与审计。全部启动的Cargo/test父进程及技术child已wait结束，无监听/GUI/HTTP/设备/数据库服务/Docker资源，无需接手运行连接。旧QA/DEV/r1及真实env/profile不打开SQLite、不恢复/清理；共享target/dist不整删。保留新证据到Root确认新QA3/Owner无依赖后按归属回收，source-after不是临时实施树。

现在Development停止source/tasks写入，最终tasks SHA及外部P2 receipt交唯一Root，随后NEW fresh QA3。P1关闭只消费QA2事实，P2关闭权不由DEV授予；完整阶段C/Owner终验与B具体运行授权仍未完成。


## r2 B01 文档提案开工（2026-11-06）

Owner本轮仅授权：“可以，先出 DAA-008 r2 的 B 联调具体方案和手动操作手册，明确新 profile、端口、后端 API／MySQL、DS 实例及资源收尾。已有配置、历史和原 profile 不动，原生测试由我手动执行，不重复阶段 B。先只改文档，批准后再准备环境和联调。”实际PM只读确认此为已批r2 §11.2/11.3的待批B文档，无新Revision；approved spec SHA仍2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de。当前QA3 A0/A1 qa_passed见checklist §24–29；Owner最终接受、B运行及完整阶段C仍未完成。

实际Development只写本tasks追加及STAGE_C_GUIDE双语；不改spec/checklist/四索引/源码/测试/配置/SQL/env/依赖/旧B手册。不是独占工作树，不回退他人内容。步骤：①消费治理/bundle及公开实现，静态固定profile/env/三API/源采用/MySQL/DS/UI边界；②编写一个具体B01待批资源提案及Owner M01–M05；③仅stdlib SHA/公开链接/双语参数/diff检查，冻结doc-only handoff→Root→NEW fresh文档QA。验证目标为文档可执行性与源证完整，不把静态检查当环境可用/HTTP/原生证据。

文档入口 /private/tmp/daa-008-r2-b-doc-rd8ex0t7/entry-manifest.json SHA b7b8706ef862df7347534fd2f0a237ca7e1062e70c7520d029c6cfa4c9144f2f；54源scope26cebdb087c5aa4be93fd431bec1a54d253e104ca57fd5ee1d0b3a4e9aa57b7c。原tasks SHA47b1585d3d2eb7309acafd778ed3c1638ede23a85c3d06776d39a6d066810ff8；旧正文原字节保持。仅公开文档审计物可写该root/development，不生成env/SQLite/profile/runner。禁运行产品/测试/import/HTTP/监听探测/Docker/DB/DS/GUI，不读真实.env/profile，不安装依赖。所有以下资源均拟定、环境未核验、B尚未批准；冲突/已存在即停，不换目标求过。

<a id="b01-proposal"></a>

## r2 B01 精确待批运行提案（仅文档，2026-11-06）

**效力：拟定；环境未核验；r3及B均尚未批准，尚未准备/运行。** 本节由r2 §11.2/11.3文档授权起草。后续实际PM发现DS普通启动只读自身真实.env也违反r2 AC02，不能仅靠B批准覆盖，Root已要求最小r3 draft承载精确例外；当前本tasks Revision仍r2，不冒称r3实施/QA。本提案须同时获“精确r3有限DS自身.env只读例外＋B-RUN-01参数运行批准”，不是运行收据或Owner终验。前一开工段记录当时r2内起草判断，已由本风险门禁更新；r2 A0/A1 QA3及全部旧史不改。普通原生测试由Owner亲自执行；协调方仅在未来精确批准后准备环境、执行列明的有限故障/账核并交接。旧DAA-007阶段B已接受，不重跑其整套导入/布局/命名/分组测试。r1/r2全部失败与QA历史保持。实际PM关于末次dir-fsync及aux全无unsealed cold的两条r2只读解释不变；本轮无恢复协议/源码变化。

### B01-1 固定候选与静态来源

唯一canonical现为[spec r3 draft第17节](spec.md#r3-ds-env-exception)，实际PM已停写，Root转交冻结SHA `0a6bbc4d5f0b6868e994b6dee2752d9876edca4577c01f02dc20752bb3352416`，DEV独立重算一致；**未批准**。Root只读r2 archive `evidence/r2-approved-spec.txt` 86546B/SHA2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de逐字核准。此为r3待批文档对齐，不将r2 tasks改登记为r3实施；此前r2 A0/A1 QA3不重跑。

正式树HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，有既存未提交A候选；HEAD不能单独代表dirty候选。A0/A1 QA3仅覆盖原54源码scope `26cebdb087c5aa4be93fd431bec1a54d253e104ca57fd5ee1d0b3a4e9aa57b7c`，checklist SHA `1bbbb201c6cdeafc9f917a7c583d5cdbbe8f727ea28e93e73ddb54986f8700be`。本轮52项非指南候选表面（含文档/索引/锁文件）逐字保留，两指南doc-only更新；旧QA3不自动覆盖新指南。B环境准备前须再核本轮文档收据、正式DAA候选及32项公开辅助pins，有漂移即停交协调方，不就地更换候选。

公开静态pins完整清单 `/private/tmp/daa-008-r2-b-doc-rd8ex0t7/development/static-source-pins.json`（32项，SHA `94cfd2c74b2f56308a20a13d5856da464a0dcb9ae5f6104e289066712acc24f1`，path+NUL+SHA+LF scope `798dcf1bc414ccbf90d90d3ebb4cb8cba980f3dc756f25fa6dc11b29517d1c32`）。包括backend入口/settings/engine/Alembic/facts/锁文件，DS入口/engine/lifecycle/bootstrap/三锁文件，共享导入核心、最小fixture及三机器合同。另固定完整公开provider/DS候选：`development/b01-provider-ds-source-manifest.json`，710项，SHA `e407ec180afdbf2e0389ac6f6e7876d3894d61806e6392a89c798cb23e4ae5ae`、scope `76baa528e25088771db435cedb96d7e510f40f0e7556f8179665fb549e08a298`；按清单明确选择backend/DS/shared-core/三机器合同的公开源码/锁/构建元数据（含native C/C++，不读env/profile/二进制/测试/任务文档）。这是本提案的具体后端/DS基线，不以HEAD替代dirtytree；批准后启动前再逐项复核，依赖/本机原生制品及新增helper另验/冻结，漂移即停，不能默认为新候选获批。三机器合同SHA为openapi `bec51c468ff64a8d34dbb0a2faab2fda76d2b33769ee5ef066dc81e8bca274ee`；schema `60d0e285bebb1c6d24588f4d5f90e7bdd85ed0befdeab9d0b93445a94f45d4b3`；vectors `9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782`。

| §11.2字段 / 采用的公开来源 | 静态结论及后批核验责任 |
| --- | --- |
| [DAA配置入口](../../src-tauri/src/config/mod.rs)、[普通壳](../../src-tauri/tauri.conf.json)、[profile合同](../../src-tauri/src/infrastructure/local_store/profile_contract.rs) | process DAA_ENV_FILE选本次新文件，process profile优先；配置/历史在最终profile/local-acquisition-v1，new config2/runtime3；seal后不移动/复制。正常入口pnpm tauri dev，15191、rust-snap7-driver由Tauri配置给出；不加feature |
| [DS bootstrap](../../../device-simulator/src-tauri/src/config/bootstrap.rs)、[壳](../../../device-simulator/src-tauri/tauri.conf.json)、[生命周期](../../../device-simulator/runtime/src/services/lifecycle.rs)、[用户手册](../../../device-simulator/USER_GUIDE.zh-CN.md) | process DS_PROFILE_DIR非空优先，但普通bootstrap仍读自身.env；不声称避读.env。15194/native-s7、UI UUID、新草稿→版本→停机加载→显式启动；现存.env不人工读取/修改，坏文件立即停 |
| [Settings](../../../../backend/settings.py)、[FactsSettings](../../../../backend/app/plc_facts/config.py)、[maintenance入口](../../../../backend/scripts/plc_facts_maintenance/main.py)、[正式service](../../../../backend/app/plc_facts/services/sync_maintenance.py)、[BE009隔离先例](../../../../plans/ARCH-BE-009-backend-facts-integration/tasks.md) | backend/.env明确锚定；maintenance还显式dotenv_values合并。uv --env-file不隔离。下述临时runner先阻dotenv，再导入formal service；不运行run.py reload入口，不改后端源码 |
| [verify_profile/clock](../../../../backend/app/plc_facts/crud/sync_maintenance.py)、[显式迁移](../../../../backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py)、[Alembic env](../../../../backend/alembic/env.py) | 精确0a2c4e6f8b10/BE009-B/71应用表（另alembic_version），F7=`sha256:28edcba4298a164389965c6f7d05b29e8e6494a1ace48d141d83c5edbd1d8e2e`，8.4.x/RR/+28800秒。新库从base显式upgrade到0a2，禁止upgrade head到1b3；不运行BE01013表41列business_time_adoption |
| [三API adapter](../../src-tauri/src/infrastructure/facts_http.rs)、[provider routes](../../../../backend/app/plc_facts/api/routes.py)、[query](../../../../backend/app/plc_facts/schemas/query.py)、[retention](../../../../backend/app/plc_facts/retention.py) | POST batches / GET latest / GET history，在/api/v1/integration/plc-facts下；4MiB POST、8MiB ACK、2MiB GET，客户端单HTTP；新批24h准入、稳定proof120天、原值3自然月是三条独立期限，不改机器时钟冒充 |
| [source材料](../../src-tauri/src/infrastructure/local_store/delivery.rs)、[详情原串IPC](../../src-tauri/src/infrastructure/local_store/runtime.rs)、[详情UI](../../src/components/console/LocalSampleDetail.vue)、[上传控件](../../src/components/console/FactsDeliveryPanel.vue) | 接入材料无context原串/configRevision正文，详情JSON经过格式化；不能复制显示再当原SHA。由获批RO observer导出原串；Owner只看/交接，不写JSON。GET仅read_result，不写ACK |
| [最小fixture](../../src-tauri/tests/fixtures/source-import-minimal/README.md)、[DS源导入](../../../device-simulator/runtime/src/services/source_import.rs)、[DAA调度](../../src-tauri/src/infrastructure/local_store/delivery.rs) | 一次必要导入DB21/3点/8B，不执行BEGIN初值；每批是一个完整cycle所选片；latest/history新冻结机会3:1，旧unknown原批先恢复，不保证恢复第一条TCP/POST是新轮 |

### B01-2 唯一拟定资源表

以下路径均为绝对字面值，尚未检查存在性、symlink、端口空闲、依赖或Docker可用。未来获批后先检查：任何已存在/占用/归属不明即停，不覆盖、迁移、kill未知进程或自动换号。根.gitignore已有automation-world/**/.local/；忽略不等于获准写入。

| 资源 | 唯一拟定值 / 限制 |
| --- | --- |
| DAA最终profile D | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01`；新空，不复用任何旧profile；seal前确定最终路径，后不移动/复制 |
| DS最终profile S | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator/.local/daa-008-r2-b01`；全新device-simulator-v1 |
| 私有操作/证据根 O | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01-ops`；新建0700，helpers/evidence/config子目录；新私有配置0600，不入Git或公开收据 |
| DAA技术文件 | O/config/daa-launch.env（新建只含明确的DAA_PROFILE_DIR=D）；启动终端process再显式DAA_ENV_FILE与DAA_PROFILE_DIR；普通DAA_PLC_READ_ALLOWED进程键须确实未设置，异常继承先停核对，不用file true覆盖 |
| DS实例 / S7 | C008-A / C008-B，127.0.0.1:31281 / :31282，rack0/slot1，Calling TSAP256/Called257、连接16/握手4；UUID仅由新GUI生成后记入binding-receipt，不预造、不使用B007-A/B |
| UI开发监听 | DAA15191、DS15194，Tauri原配置不改；批准后只检查这两个及本表端口，冲突停 |
| MySQL | 官方`mysql:8.4.6`，获批后记录实际image ID/digest及平台；container `daa008-r2-b01-mysql`、volume `daa008-r2-b01-data`、bridge network `daa008-r2-b01-net`、network alias `daa008-r2-b01-db`；仅127.0.0.1:13381→3306；label `aiis.task=DAA-008-r2-b01`，无自动restart策略 |
| DB目标 | targetAlias/DAA targetId `daa008-r2-b01`；schema `daa008_r2_b01`；API/maintenance宿主连接固定127.0.0.1:13381，不用alias作为宿主地址，不落回localhost:3306；容器内仅用专用alias |
| 账号 | 新随机各异口令：`daa008_app`、`daa008_maint`、`daa008_migrator`；root仅专用实例建schema/账号/授权后离线封存。app/maint对71应用表及alembic_version SELECT（metadata可见），仅下述7表INSERT/UPDATE/DELETE；无DDL/GRANT/跨schema。migrator仅本schema迁移所需DDL/DML/索引/引用，不GRANT/跨库；完成即停用运行凭据，不给DAA任何MySQL/HMAC/管理凭据 |
| 时间/schema/budgets | MySQL服务default-time-zone=+08:00、transaction-isolation=REPEATABLE-READ；每连接实际clock +28800秒及RR均核。DAA新profile保持默认quota1073741824B/本地7天保留（pending不因保留期删除），记录实际GUI容量与extra32MiB预留；0a2/71/F7精确匹配后才能adopt；retention_months=3、max_value_bytes=1073741824、max_proof_rows=1000000；新随机storageEpoch，首次服务返回adoptionId，后续PLC共享，不虚构wire epoch字段 |
| API / relay | upstream uvicorn单worker无reload，127.0.0.1:18283；唯一DAA origin `http://127.0.0.1:18281` 为本次固定relay。只三facts路径，无任意代理/redirect/重试；真实请求目标和IDs/原文hash审计，不公开值/body/token |
| 凭据/日志 | O/config/backend-private.env、mysql私有配置及随机64hex cursor HMAC仅O/0600；全新JWT合成密钥、所有bootstrap/mock/Projection/旧工业writer关闭、primary=mysql/TESTING=false、TZ=Asia/Shanghai、API_V1_PREFIX=/api/v1、BACKEND_HOST=127.0.0.1/BACKEND_PORT=18283/BACKEND_WORKERS=1，所有DB URL与schema guard双核。日志仅O/evidence，启动前禁止读取原backend/.env/工具.env，无生产目标 |

7表为 `plc_facts_stream_state`、`plc_facts_source_bindings`、`plc_facts_batches`、`plc_facts_sample_receipts`、`plc_facts_raw_samples`、`plc_facts_cycles`、`plc_facts_latest_points`。其余64应用表为空只读，用于verify_profile精确metadata可见，不启用/写入客户或BE010业务。mysql系统库仅账号管理责任方的必要操作；业务账号不读写其他schema。口令不沿用任何BE009资源/旧口令，旧已回收资源不重建。

### B01-3 批准后协调方准备与交接（现在不执行）

1. **前检并冻结。** 核正式候选/pins/已有依赖与锁，不安装、不sync、不升级锁。检查仅拟定路径及端口资源无冲突/无symlink，记录canonical路径/归属/计划。Docker镜像若本地缺失，批准范围含拉取精确mysql:8.4.6，记录digest；失败停，不替换版本。明确只在新专用schema从零base→0a2；任何已有业务数据不迁移/清理。取得精确r3例外和B-RUN-01双重批准后才新建D/S/O；DAA最终路径此后不改变。无原profile/.env人工读取、copy或重写。
2. **临时隔离runner（尚未生成/运行）。** 后端责任方在O/helpers/backend_runner.py生成并审阅一次性夹具，记录SHA/argv后才执行。启动形式拟为：在backend目录使用已有`uv run --offline --frozen --no-sync python <O>/helpers/backend_runner.py <schema|adopt-plan|adopt-apply|status|cleanup-plan|serve|audit>`，实际绝对路径见资源表，不能直接运行产品run.py或maintenance CLI。协调方先以明确白名单child环境调用uv（清除UV_ENV_FILE等继承env-file选择），helper在任何项目导入前清理继承业务配置，仅解析显式私有配置，禁止DotEnvSettingsSource读文件、封住显式dotenv_values/load_dotenv；不依赖“从customise_sources移除”这种读后移除。无文件参数、未知键、非本schema/13381/账号、非127.0.0.1监听均fail closed；无fallback。固定私有env仅helpers自己读，阻止原backend/.env及工具.env访问；settings和facts settings两者都覆盖。正式schema使用Alembic API command.upgrade到0a2（绝不用head）；serve先导入正式main.app，再uvicorn app object，reload=false/workers=1/access_log=false/log在O（公开请求日志不含query/body/token），禁自动维护/seed。正式serviceexecute路径绕开maintenance/main.py显式dotenv合并，但夹具必须保留CLI enable、精确`APPLY:<action>:daa008-r2-b01:daa008_r2_b01:<actualStorageEpoch>`确认、operation_approval/confirmed_by、目标/schema/revision/epoch/adoptionId/CAS及context≤1MiB门禁，默认plan；不把复制校验变产品能力。独立连接/listener guard仅允许本表目标及本次凭据。尚未有可运行的新入口；隔离/guard未通过就停，不用真实.env补齐。
3. **数据库就绪。** 新容器/net/volume/schema及三个业务账号按上表创建，root/migrator完成后退出。只跑0a2，不运行旧BE009迁移回退/BE010联测。app和maint各自核真实71表可见、F7/唯一alembic revision/8.4.6/RR/+08；事实clock/adoption足够，不运行不适用的business_time_adoption。新库7表须全空、highSerial/proof floor待首次adopt初始化0。API先facts关闭/空scope，不做业务种子。app/maint的Settings必填root字段仅合成不可连接哨兵，禁止root_engine连接；真正root口令只在新实例建schema/账号授权进程使用，不传API。冻结backend实际导入闭包、DS入口/runtime/shared-core/锁文件和临时runner SHA。后端责任方签准备收据，再交Owner两个原生终端命令。
4. **临时relay（尚未生成/运行）。** O/helpers/facts_relay.py，独立已记录PID/代码SHA，固定listen18281→18283，仅POST batches和GET latest/history，原method/path/query/body/状态/media原样有界转发，禁代理别的host/route/重定向/自动重试，max4MiB request/8MiB ACK/2MiB GET、连接≤3秒、POST总≤15秒、GET总≤8秒/只一在途。常态透传。仅协调方具名arm一次，锁定下一实际batchId/requestDigest/bodySHA；必须先完整收到并严格匹配上游typed committed ACK，核HTTP200/身份/摘要/成员，才丢弃这一次下游ACK并断开，记录上游提交证据而不代写本地ACK；未获匹配ACK不消耗为“已commit丢ACK成功”。之后同batchID必须同原体hash，透传原请求和provider稳定证明/receiptId（duplicate响应字段可依法变化，不要求回执原文相同），不改时间/ID、不造ACK/拒绝。arm失败/多batch/摘要不符停止该case，不循环直到成功。响应body/token仅私有证据，公开日志仅ID/hash/长度。M03不可达固定20秒；M04第二次停relay至重开停态checkpoint但最长180秒，超时终止该case、正常恢复relay并记未覆盖，不要求Owner重做。upstream/DB保持；恢复同端口同目标，不换origin。无真实设备网络。
5. **新材料采用交接。** M01后协调方使用O/helpers/observe_new_profile.py（后批生成/审阅SHA）只读固定D/local-acquisition-v1/runtime.sqlite和已交接instanceId；采集已暂停、上报停止、无在途及journal/WAL/SHM，独立短`mode=ro`/`query_only`事务，无immutable/nolock/ATTACH/DDL/DML/恢复，不取得、释放或绕过产品ProfileLock及SQLite原生锁，也不称工厂准入证明。busy/hot/身份/前后状态变化立即停，不重试修复。仅导出已commit配置context原UTF8字节/原SHA、configRevision及所选cycles/samples/plc_sources账至新建不覆盖证据文件；核各SHA与GUI接入材料一致。GUI没有原串下载，格式化展示不是原字节导出。Owner不写/重排JSON，不加退出循环。后端责任方用原context进行每PLC`adopt-plan→adopt-apply`，首次expected_binding_revision=0、seq_from=1、old_seq_through=None，不传expected_adoption_id；第二PLC必须使用第一次返回adoptionId、同storageEpoch/retention/budgets。provider seqThrough固定9223372036854775806，不能随意封上界；DAA填同范围。记录实际instance/PLC/generation/configRevision/contextSHA/definitionSetDigest/seq/adoption引用/时间/F7至binding-receipt；真正新window从1覆盖本profile本次首次采集，不包含旧历史。scope仅这两个实际DAA PLC ID（非DS UUID），HMAC不交DAA。启API facts/scope仅在采用完成后，以同新私有配置重启单API；不猜wire epoch/adoption字段。

### B01-4 Owner原生M01–M05与必要增量

双语STAGE_C_GUIDE为Owner唯一主路径，以下是协调/核账细节。Owner使用正常`pnpm tauri dev`，应用feature由Tauri给出，不用调试fixture宿主。每段采集5–10秒后暂停，两个1s组产生约2轮/s而上报1s约1批/s；不能持续采着等清零。小规模有界代表case，不重跑StageB测试。

| 步骤 | Owner必要点击 | 协调方证据 / 通过条件（未来实际填写，不预称通过） |
| --- | --- | --- |
| M01 | 新D/S普通启动、核停止/空列表；DS新建C008-A/B，双PLC各导入公开minimal.db+minimal.udt选DB21；“预览标准地址”确认、3点命名预览确认、保持/无写入owner/写禁止/显式初值与客户端读、“保存草稿并确认所选初值/策略”→保存草稿→保存版本→停机加载→Start；DAA同样新建A/B端点、一次导入、偏移确认、每PLC一个G1_1000组/3启用点→保存→激活；工作台连接，采5秒→暂停，上传不启动；“查看接入材料”交协调方 | GUI新UUID记录，不杜撰；DB长度8，Bool0.0/Int2/Real4；A false/0/12.5，B true/202/25；无原B007对象/历史。export/adopt完成前停在此，保存/导入/激活不等于启动。DS UUID和DAA PLC UUID不要求相同 |
| M02 | 按binding-receipt填origin/target/采用引用、两个source精确窗口，周期1秒保存；选PLC“读取测试(GET)”；查历史/原轮只读包预览；显式“开始上报”；首次链核后先“暂停上报”，协调方短暂停DS A后，按提示DAA A采≤5秒→暂停→断开；两PLC均停采停连后显式“继续上报”，看已有积压可靠确认增加 | 首次GET可合法空，不证明未POST。三点false/0/REAL完整链及两PLC同DB隔离；A设备停止时坏读/null按真实结果记录，不能伪造bad。若短窗未生成bad则记未覆盖，由后续明确有界补证，不无限等；原始质量与cycle完整性两轴。全部PLC断开、采集停止仍可上传积压。一次relay丢ACK由协调方执行，Owner不反复点击 |
| M03 | DS恢复A Start，DAA按提示重连；协调方停relay20秒（上游不动），DAA双PLC采5–10秒后暂停；恢复relay后保持停采观察队列 | 未伪ACK、本地积压；已有frozen/unknown必须原批恢复，不能要求恢复首条POST最新。只对新freeze机会观察至少4个且积压仍在时latest/latest/latest/history（计入既存streak相位），持续记录PLC/组；不足四机会如实未覆盖。旧seq补raw不覆盖新latest，恢复可清理有限积压，无吞吐承诺 |
| M04 | 协调方再次停relay（至重开停态checkpoint，最长180秒），Owner双PLC采5秒→暂停、保持积压/冻结；等协调方记录checkpoint后只正常Cmd+Q一次。用同D/同env重开，不点任何开始按钮；看历史/队列/停止态；收到通知恢复relay后显式“继续上报” | 协调方在可达时限内等待在途收尾/冻结出现，若未冻不冒称frozen守恒；闭库RO全账、再开RO/IPC对照sample/manifest/context/ID/SHA及batch body/createdAt/digest/成员/父引用，原体未变。无自启连接/采集/上报；明确续传同身份，provider receipt不重复事实。禁止killDAA制造额外崩溃 |
| M05 | 任一投递详情→查看回执/状态；选PLC读取latest及固定范围original一页，窄窗/明暗/中英文各看同弹窗（不另跑全套UI）；正常退出双应用 | Pending总样本=unfrozen+frozen+needsProcessing，可靠确认单列；多片不重复计；需处理不得仅称running。原生详情/间距/分页/列宽拖动记忆与reset截屏。复杂history页/changes/cursor和完整7表账由协调方做，Owner不写JSON/SQL。未覆盖视觉项单列，不以源码字符串替代 |

### B01-5 协调方有限自动case、全账与停止点

- **一次真实丢ACK**按B01-3 relay合同执行，确认provider已commit、DAAunknown/原体重试、稳定证明/receiptId及本地ACK（duplicate合法响应字段可变化）及7表不重复。普通暂停/退出覆盖生命周期；本B01不新增kill/SQLite写故障/DS crash/人工改库。A1崩溃/本地事务故障/32片8MiB预算/父链混合拒绝证据按同源码复用；如果实际环境暴露新缺口，先报具体新增动作另批，不能为了补coverage扩故障。
- **一次busy、一次准入拒绝**：仅O新fixture进程：maint新连接短事务锁本schema streamState≤2秒，恰好一个已记录请求遇busy则放锁；不重试制造覆盖，不改生产超时。拒绝用协调方全新合成POST（引用其中一个已采用PLC和已核定义、另取独立synthetic instance/generation/cycle/sample/batch，不混Owner冻结批；上下文/摘要按正式合同重算并预检），只发一次不匹配现绑定的source请求，核typed403 source_rejected及可靠终结拒绝证明、无raw/sample_receipt/cycle/latest新事实；batch拒绝证明及容量账的合法变化须精确列账，不能称7表全不变；不篡Owner批/伪造父token。此处只是必要代表，复杂混合拒绝/过窗父链沿用A证据，不声称全部真实HTTP已覆盖。
- **期限与历史代表**：不改宿主/MySQL时钟，不把24h新批准入当proof TTL，不直接UPDATE期限或播种旧proof。对Owner本次新数据核observed+3自然月expiresAt与committed+120天proofExpiresAt精确算式；仅用正式retention纯函数作一个月末/三自然月边界代表计算，不import产品入口或触发其他DB。专用库执行一次cleanup-plan（非apply），核当下无到期数据时未误删。实际等待三个月/120天及历史proof过窗的真实HTTP仍未覆盖，明确复用A/BE009已固定证据而不冒称本B跑过。
- **查询预算**：每PLC latest8/页，history changes earliest8/页、固定上海[from,to) projection8/页、original1/页，最多20页/次。至少一例limit1分页/nextCursor衔接，核(commitSerial,ordinal)、sourceSeq与latest不回退；不可从空页/scanBudgetReached断言完结，gap/过窗/mismatch如出现记未完成并停，不静默tail/ACK。GET只read_result。20页仍hasMore需人工明确新预算，不自动扫全库。必要源证见query/async_query；不必重复旧全套游标矩阵。
- **完整双边账**：后端责任方分别给7表全量本次有限数据导出（SELECT，私有原文不进公开仓）、表行数/主键/引用/hash、stream highSerial/proof floor/valueBytes/proofRows、2binding/context/seq窗口/F7/epoch/adoption、batch原回执/requestDigest、sample receipt/member/位置/partial quality/complete、raw payload/上下文/manifest/点值/observed/saved/committed/expires/proofExpired/readable，以及latest点来源。DAA本次闭库RO核全部本地原样本及delivery metadata/ACK引用/计数/停态；每个已确认sample全parts有可靠receipt，unknown不伪确认；前后原串SHA守恒。双方join按instance/plc/generation/cycle/sample/part/point ID，不按名称/DB单独join；本轮严格只有2个Owner PLC，辅助synthetic身份在账中独立标记不合并。
- **停止**：目录/端口/候选漂移，错误env/profile/未知对象，F7/71/revision/RR/+08/scope/adoption不符，原SHA不符、容量/锁/journal诊断、proof过期/unknown无法校对，均暂停新采集/派发、保留原件与当前新资源，交责任方；无手工ACK、队列清理、换ID/时间、删marker/journal、repair或自动换库。无新凭据向DAA泄露。

### B01-6 生命周期与明确批准语句

| 资源 | 未来获批可停止 | 必须保留 / 删除授权 |
| --- | --- | --- |
| Owner两个native应用、各自dev server | Owner正常退出；协调方只stop本轮已登记PID及子PID，不kill未知 | D/S配置历史、sealed目录/marker/journal原位保留至Owner另行明确删除；QA passed/Owner验收不自动授权删除 |
| API/relay/observer/runner/短DB连接 | 结束case后关闭本轮连接；协调方正常停登记PID，核无本轮在途，再停API/relay | O/helpers SHA、command/env键名/无密钥参数、receipt/原文hash/错误/证据保留至Owner gate及后续依赖解除。私有原文/凭据不公开；必要O证据、可再运行helpers/私有配置继续保留，尤其volume再运行所需凭据不能提前删；无依赖的自有可再生缓存可按B-RUN-01条件清理 |
| 新MySQL容器/net/volume | 证据交接后stop专用container（记录实际ID/label），不影响其他容器 | 新volume/再运行所需凭据保留。若B-RUN-01获批且本轮container/network已停、无运行或证据依赖，协调方可按已记录ID+label仅移除本轮新container/network及自有可再生缓存；不是QA/验收自动授权。volume/profile删除不含于B批准，仍须Owner另行点名。无默认down -v/prune，不删schema求过 |
| 本轮doc审计root | 无运行资源/连接需停；只公开文本收据 | /private/tmp/daa-008-r2-b-doc-rd8ex0t7保留必要原doc/diff/manifest/check结果；fresh文档QA封存hash结果且Root核无引用后，可回收冗余公开源码快照副本/缓存，不因B待批无限保留52份无变化代码。它不是runtime profile。旧QA/DEV/r1失败及B007/8590/原.env/历史/任务外资源永不作为本轮清理目标 |

可复制的 **B-RUN-01 运行批准语句（待Owner发出，当前不是批准）**：

> 批准 DAA-008 精确 r3（spec draft SHA 0a6bbc4d5f0b6868e994b6dee2752d9876edca4577c01f02dc20752bb3352416）的有限例外：仅本B普通DS按既有bootstrap只读自身.env，非空process DS_PROFILE_DIR固定本次新profile；错误立即停，不显示/复制/改写.env，不采用旧profile或旧库，其余r2边界保持。并批准 B-RUN-01，按 tasks 的 B01-1 至 B01-6 与双语 STAGE_C_GUIDE 准备及实施必要增量联调。仅新建文中 DAA/DS 两个 .local/daa-008-r2-b01 最终 profile 和独立 daa-008-r2-b01-ops；仅使用拟定的 15191/15194、31281/31282、13381、18281/18283 及所列新 mysql:8.4.6 容器/卷/网/alias/schema/账号。允许冲突前检、精确镜像拉取/新资源创建、专用 schema base→0a2c4e6f8b10/71/F7、+08/RR、两新 source 显式采用及最小权限；允许在项目导入前隔离全部dotenv的临时runner、固定三API relay及一次严格匹配已提交ACK丢弃、两次relay停止/恢复（M03为20秒，M04最长180秒，超时中止case不重做）、一次≤2秒本schema忙锁、一次合成非采用source拒绝、有限真实HTTP查询/期限算式/cleanup plan、只读本次新SQLite短观测和M04闭库全账。原生GUI由我手动执行M01–M05；协调方按文中合同准备、核账和停止本轮登记PID/新容器，但保留profile、MySQL卷、必要O证据/可再运行helpers/私有配置及再运行所需凭据；后续无运行/证据依赖后，允许按已记录ID+label仅移除本轮新container/network和自有可再生缓存。此条件清理的权限来自本批准，非QA或验收；删除volume/profile仍须另行点名批准。已有配置、历史、原profile/.env及旧失败证据不动；冲突/漂移立即停，不换目标，不重复阶段B。此批准不含完整阶段C终验、生产/SMA、自动启动、旧历史上传、真实PLC/现场、部署发布或任何未列环境动作。

批准后仍须提交binding/运行receipt与独立Verification，Owner再决定阶段C最终接受；本轮仅文档自检和手交，不能填写B通过。

## r2 B01 文档 Developer handoff（r3 draft对齐，未实施r3/B）

本轮只完成Owner授权的具体提案/双语手册。tasks仍保留r2身份；DEV不授r3批准/实施、QA verdict、B通过或Owner接受。actual PM已停写r3 draft，spec SHA `0a6bbc4d5f0b6868e994b6dee2752d9876edca4577c01f02dc20752bb3352416`；DEV独立重算匹配。r3有限DS自身.env只读例外及B-RUN-01参数均待批准。原r2 archive 86546B/SHA2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de、QA3 checklist SHA1bbbb201c6cdeafc9f917a7c583d5cdbbe8f727ea28e93e73ddb54986f8700be保持；PM外部收据SHA220684c692eb6566f2e01310842dbe6f5c85b2865fded678d4e508ea8b986db5，精确r2→r3 diff SHA5927af552fffbdab178a42bee794e0965c2278e65b8117dd68fe0014204bc019单独归属。

仅修改STAGE_C_GUIDE.md、STAGE_C_GUIDE.zh-CN.md及本tasks追加，entry原tasks **84507字节逐字保留**。正式树/HEAD仍 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` / bcafa89fa31bdf62329bced89baebc193323a739；无临时实施树。spec/archive为PM/Root写面，四索引为Root写面，均不混入本DEV三文件diff；checklist/CODE_INDEX不改。52项非指南候选表面（含文档/索引/锁文件）逐项原SHA不变，scope `ca942975d851184d20987cee4c2af461eb3a72e231a79ae06553791e106e89f8`。两指南保留原恢复/读取/失败合同，新增具体B主路径及当前门禁，旧QA3不自动覆盖新指南。

54项当前scope `7e677674769862d7241148e0f57287f1e81e046eae3a4c32a19a704431fe1330`；指南SHA：EN `948f335a9e04cdc136d1a8559c0ffa96b3618bdfd2bd07ffc6b7f1d603c094ac`、ZH `2c3395f25136329cc284c0e1955fda18d8e4bda97b1fd97844d5d5cbc69926ab`。完整54项before/after manifest、三文件公开after、相对doc-entry精确diff、最终tasks SHA由 `/private/tmp/daa-008-r2-b-doc-rd8ex0t7/development/doc-developer-handoff.json` 外部固定，避免自引用。

| DEV实际静态命令/检查（cwd正式仓根） | 真实exit / 结果 |
| --- | --- |
| `python3 -B /private/tmp/daa-008-r2-b-doc-rd8ex0t7/development/check_documents.py` | 0；授权三文件、原tasks、spec draft/r2archive/checklist pins、54/52项、37本地链接、双语资源技术值/两个普通启动shell及5个Owner步骤、32/710公开pins匹配。最终argv/cwd/exit/stdout/stderr在final-check-command.json，结果static-doc-check.json |
| helper内 `git --no-optional-locks diff --check -- automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md automation-world/data-acquisition-agent/plans/DAA-008-reliable-facts-upload/tasks.md` | 0，空输出；不扩到他人写面 |
| stdlib SHA/JSON；`git --no-optional-locks ls-files --cached --others --exclude-standard -- backend/ automation-world/device-simulator/ automation-world/shared/tia-import-core/ contracts/published/http-api/plc-facts-v1/`后只读明确公开源码/锁/构建元数据 | 0；710项scope76baa528e25088771db435cedb96d7e510f40f0e7556f8179665fb549e08a298，manifest SHAe407ec180afdbf2e0389ac6f6e7876d3894d61806e6392a89c798cb23e4ae5ae；32关键pins manifest SHA94cfd2c74b2f56308a20a13d5856da464a0dcb9ae5f6104e289066712acc24f1 |

真实失败保留：自有文档生成helper两次exit1（Non-UTF-8/source line53），加显式UTF8 coding头后exit0，提案仅追加成功一次；一份尚未执行的handoff stdin helper同类编译exit1，未产生写入，改为公开Markdown模板+显式UTF8小helper。首次doc check exit1指出两指南EOF空行，修剪本轮尾空行后原断言exit0；后一次保护check因PM合法更新canonical spec而exit1（spec.md路径），收到Root精确r3 pin后仅更新外部metadata期待，52项/旧tasks断言保留并exit0。见helper-failures.json及static-check-first-failure.txt。这些是文档辅助/格式/并发元数据事实，不是产品finding；发现型rg/sed误猜公开路径/未命中不充通过检查或环境结论。

已消费根及最近治理/README/PLAN、workflow/actual development角色、完整bundle历史/QA3 §24–29及r3 §17；按表面使用aiis/project-governance/desktop-tauri/backend-arch/code-document-indexer，Docker skill仅静态设计，无Docker检查。没有产品/测试/build/import项目、HTTP/端口/进程探测、Docker、SQLite/MySQL、DS/GUI、真实.env/profile访问、安装/下载、子agent/notifier/邮件。32/710清单是公开源码文本检查，不是环境检查。O/helpers未来backend_runner/facts_relay/observe_new_profile仅写行为合同，未生成/运行/验证；guard不成立即停，不能称现成入口。

所有路径/端口/镜像/账号/UUID等运行参数拟定、环境未核验，冲突不自动换号。loopback HTTP不证明TLS/真实PLC/生产/长期SLA；实际三月/120天等待、复杂混合拒绝/父链、本地崩溃/大回执沿用同SHA既有有限证据，不冒称本B跑过。A0/A1 QA3、未来B及最终Owner接受分立。

新增资源仅doc审计root内公开entry/pins/静态脚本/报告/diff/after/收据，无运行profile/env/DB/服务/待停PID。必要原doc、manifest、diff、失败与check结果保留；fresh文档QA封存摘要且Root核无引用后可回收冗余公开source副本/缓存，不因B待批永久堆52份无变化代码。旧DEV/QA/r1失败/原profile/env/历史不触碰。未来B-RUN-01若明确批准：无运行/证据依赖后按实际ID+label仅移除本轮新container/network和自有可再生缓存；D/S、MySQL卷、必要O证据/helpers/配置/volume再运行凭据保留，删volume/profile仍另点名；QA/验收本身不授删除。

Development现在停止三文档写入，外部收据固定后经唯一Root交NEW fresh文档Verification。它只核r3 draft/B01/指南文档，不是r3实施或B运行QA；文档QA后Owner仍须精确批准r3+B-RUN-01，随后实际B交接、新fresh B核验及完整阶段C最终接受保持开放。

## DAA-008 r3 · B-RUN-01 执行记录（2026-11-07，Asia/Shanghai）

Development 实际身份 `/root/daa008_r3_b01_prepare`。按 [spec.md](spec.md) §17–18 的 Human Owner 精确批准及本文件 B01-1–6 执行准备。批准后 spec SHA-256 为 `a60e92309b1108038a374196d5dc700a084bde4b447ce54be6cd9d03512a3db7`，源码基线 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。根协调复核冻结的32关键项、710上游项及54项DAA相关面，中文手册表格空白差异经 PM 认定不改变批准范围。此前提案及 A0/A1 状态保留为历史。

**本次准备在 `schema_fingerprint` 硬门停住，未交出 M01。** 本次冻结的 B01-1 期望 F7 为 `sha256:28edcba4298a164389965c6f7d05b29e8e6494a1ace48d141d83c5edbd1d8e2e`。专用库的正式后端模型和两个账户实际反射均为 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。后者与 [ARCH-BE-009 交付记录](../../../../plans/ARCH-BE-009-backend-facts-integration/tasks.md#L336) 一致。该记录将 `28ed…` 列为已被取代的 QA1 候选。冻结值、失败证据及新建资源保留，已交 Root/PM 核对并处理批准门槛。诊断结果未替代严格 readiness。

- D、S、O 为 B01-1 登记的三个新目录。创建前均不存在，均匹配 Git 忽略规则。D、S 保持空，O 和其三个子目录均为 `0700`。`O/config/daa-launch.env` 为 `0600`，仅含 `DAA_PROFILE_DIR=<D 的绝对路径>`，SHA-256 `e29fbdeeb89680b3e839623af076996b2895ea5c8401971f120fa0b3b4c76b35`。未访问既有 .env、SQLite 配置、历史或旧 profile。DS 有限例外尚未由 Owner 启动触发。
- Docker Desktop `desktop-linux` 仅使用缓存镜像 `mysql:8.4.6` linux/arm64，ID `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`。新容器 `daa008-r2-b01-mysql` ID `9819614cd5f8c7074ccdec379c71d534fc8d0e2e029e469578a3b6e3f00222ff`，网络 `daa008-r2-b01-net` ID `aa0f45ecfdf65e05f1bcc36592f79f460baa2625a52e0a3c552ef182c98bfa03`，卷 `daa008-r2-b01-data`，均带 `aiis.task=DAA-008-r2-b01`。DB 仅绑定 `127.0.0.1:13381`。正式 Alembic 用专用迁移账户从空库显式升级到 `0a2c4e6f8b10`，随后锁定迁移账户。真实 root 仅用于此容器内初始化与授权。口令仅保存于 O 内的私有 `0600` 文件。
- `daa008_app`、`daa008_maint` 分别只读核实专用 schema `daa008_r2_b01`、71 应用表另 `alembic_version`、MySQL 8.4.6、RR、会话 `+08:00` 与实际偏移 +28800 秒。两账号各精确73项 GRANT（72表 SELECT 与基础 USAGE，写权限只授七张事实表），七张事实表行数均为 0。
- 后端临时入口在 O 内，在导入后端源码前阻止普通 .env 读取和不符的数据库连接。执行助手、backend runner 及 relay 已静态审阅并固定 SHA。API、relay、DAA、DS 均未启动，未进行 HTTP 调用、设备操作、阶段 B 重测或事实写入。复查约定七个端口，仅 `127.0.0.1:13381` 有监听。

| 实际检查 | 结果 |
| --- | --- |
| `/usr/bin/python3 -I -B O/helpers/prepare_b01.py init/schema/grant`（三个独立调用） | 各退出 0，新资源、迁移及授权见 `prepare-events.jsonl` |
| `/usr/bin/python3 -I -B O/helpers/prepare_b01.py audit` | 退出 1，app 严格审计因 `schema_fingerprint` 拒绝 |
| `uv run --offline --frozen --no-sync --no-env-file python -I -B O/helpers/diagnose_f7.py <role>`（app、maint 独立调用，backend cwd，隔离继承环境） | 各退出 0，证实正式后端 F7 与实库相同，且均异于 B01 冻结值。只读诊断不放行 |
| 首次可选 uv 元数据探测（默认 sandbox） | 退出 2，uv 缓存权限受限，未导入项目。实际迁移和诊断使用获准的受限主机调用并成功 |
| `lsof -nP -sTCP:LISTEN -iTCP:13381,18281,18283,15191,15194,31281,31282 -Fpcn` | 退出 0，仅绑定 `127.0.0.1:13381` |

脱敏证据固定在 `O/evidence/preparation-blocked-receipt.json`（`0600`，SHA-256 `226b44826d5174840073621976e43975875e39953a5a8647b7f71c167b7e5f62`），含 Docker 标识、连接和权限、两份指纹与佐证文件 SHA。原 helper pins 保留，额外只读诊断助手 SHA-256 `8de6082eadc8b7477d6eb80f4bd1d626bac75be6cb4b83ab67775143c2fe373c`。D、S、O 及新 MySQL 容器、网络、卷有调查和接续依赖，保留原状。后续回收时仅按本轮 ID 与 label 复核，卷和 profile 单独授权。当前状态为 `preparation_blocked`，已交 Root/PM 处理冻结指纹差异，完整 B 开发交接和 fresh B Verification 尚未发生。

## DAA-008 r4 · B-RUN-01 准备就绪与 M01 交接（2026-11-07，Asia/Shanghai）

实际 Development `/root/daa008_r3_b01_prepare` 按 [r4 第19–20节](spec.md#r4-b01-f7-owner-approval) 接续同一 B-RUN-01。批准后 spec SHA-256 `bbf5cdb7d472f7439102431300f69736715928acf4c36159d270ab7fd90fda70`，正式树 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。32项关键公开 pins 与710项 provider/DS 清单逐项一致。54项 DAA 清单除已记录的中文手册两张表格排版外一致，本轮未改双语手册、provider、产品、spec 或 checklist。首次本机表格比对仅归一空格，分隔线长度差使该命令退出 1。将 Markdown 分隔线归一后复核通过，中文手册当前 SHA 仍为原 r3 开工时已审定的 `dd48028411f2c79e680ebc7f9dadf4e9d92b72f150dd9d89834a52f4ff674ec3`。

- 私有 `O/helpers/backend_runner.py` 只替换单个 F7 字面量为 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`，保留正式 provider 核验和严格等值条件。旧 runner、旧 pin 文件分别逐字节归档为 `O/evidence/backend_runner-r3.py.txt`、`helper-pins-r3.json`，旧阻塞收据 SHA 仍为 `226b44826d5174840073621976e43975875e39953a5a8647b7f71c167b7e5f62`。r4 runner SHA `e4bff1eaea3223d133049f6e43ead4d83f989f0571a961025d656e0c0ccb50dc`，运行 pin SHA `23885a6f8269b45e11e3fbda47315f9bd116b89eb2601c93eb2918cd4c80fc2e`，单行差异 `f7-r4-helper.diff` SHA `e11818047c150a15a5908d4e4670a73b2807f9b1698c0155e2756d700ce21cbb`。AST 解析和逆替换原字节断言通过，其他 helper pins 不变。
- 使用同一登记容器 `9819614cd5f8c7074ccdec379c71d534fc8d0e2e029e469578a3b6e3f00222ff`、8.4.6 linux/arm64 缓存镜像、同一归属网络及专用卷。Docker 定向 inspect 核对 ID、标签、单一专用卷及单一网络、无自动重启、仅绑定 `127.0.0.1:13381`。未重新执行 init/schema/grant 或迁移。D、S 仍为空，D/S/O 及子目录保护和忽略规则复核通过。只含一行的 `O/config/daa-launch.env` 仍为 0600，SHA `e29fbdeeb89680b3e839623af076996b2895ea5c8401971f120fa0b3b4c76b35`。
- `/usr/bin/python3 -I -B O/helpers/prepare_b01.py audit` 退出 0，app、maint 各一次只读核对均退出 0。正式 profile 验证和新固定 F7 严格等值通过，`0a2c4e6f8b10`、BE009-B、71 应用表、8.4.6、RR、+08:00/28800秒、原精确权限及七张事实表全空均通过。`O/evidence/mysql-readiness.json` SHA `78dfc995d163d25ee203f8ef2cc00102f207d018ef458867c2c0ad61c4214468`。
- `/usr/bin/python3 -I -B O/helpers/prepare_b01.py serve` 退出 0。正式 API 以单 worker、无 reload 监听 `127.0.0.1:18283`，facts 关闭、scope 为空、storage profile 未采用。固定三路 relay 监听 `127.0.0.1:18281`，未启用故障。latest/history 的 upstream 与 relay 均为完全相同的 403 正文 `plc_facts.scope_rejected`，relay 非允许路径 `/health` 返回 404。未发 POST、未采用 source、未写事实。进程复核默认 sandbox 下 `ps` 被拒，获准的受限宿主 `ps/lsof` 最终退出 0，仅见 MySQL `13381`、API `18283`、relay `18281`，API wrapper PID 55203、实际监听子进程 55205（同组），relay PID 55204。
- 脱敏收据 `O/evidence/r4-readiness-receipt.json`（0600，SHA `746465942ee117678b30c6e9fdb1617fc6cd3656e0161903a53470ccc5d26d98`）记录候选、库与进程身份、profile、HTTP 门禁和佐证摘要。MySQL、API、relay 为 M01 依赖，保持本机运行。

状态 `needs_owner_m01`。由 Root 交 Owner 按 [手册 M01](../../STAGE_C_GUIDE.zh-CN.md#m01新配置及来源交接) 各用普通 `pnpm tauri dev` 手动启动 DAA 与 DS。仅在新 profile 配置 C008-A/B，短采样后暂停，保持上报停止并交接“查看接入材料”。本次 Development 未启动原生、未访问既有 .env/SQLite/history/profile、未重复阶段 B。来源采用、M02–M05、完整 B 开发交接、fresh B Verification 与最终验收尚未发生。

## DAA-008 r4 · M01 启动说明校订交接（2026-11-09，Asia/Shanghai）

Owner 要求直接更新操作手册并说明 env 设置。实际 Development `/root/daa008_r4_m01_guide` 在既有 r4（批准 spec SHA `bbf5cdb7d472f7439102431300f69736715928acf4c36159d270ab7fd90fda70`、工作树 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`）下更新[中文手册](../../STAGE_C_GUIDE.zh-CN.md#m01-launch)与[英文手册](../../STAGE_C_GUIDE.md#m01-launch)。把当前就绪和启动说明放在最前，区分日常 DAA 与使用独立 DS 的 M01。已运行且配置匹配的本次 DS 可复用，两应用均需启动时可在同一终端窗口使用两个标签页。展示专用启动文件的原有单行，启动变量仅作用于各自进程。保留 DAA 读门禁和 r3 的 DS 自身 `.env` 有限只读例外，按 r4 第19节同步手册 F7。M01 来源交接仍先暂停采集并保持上报停止。

- 本次校订前，以排他创建方式将 DQA1 冻结原文留存于现有 B01 私有 `O/evidence`，权限均为 `0600`。英文 `r4-m01-guide-baseline-en.md` SHA `948f335a9e04cdc136d1a8559c0ffa96b3618bdfd2bd07ffc6b7f1d603c094ac`，中文 `r4-m01-guide-baseline-zh-CN.md` SHA `2c3395f25136329cc284c0e1955fda18d8e4bda97b1fd97844d5d5cbc69926ab`。工作树中文校订前另存为 `r4-m01-guide-pre-edit-zh-CN.md`，SHA `dd48028411f2c79e680ebc7f9dadf4e9d92b72f150dd9d89834a52f4ff674ec3`。冻结记录继续指向旧字节，操作使用新手册。
- 新英文 SHA `960f8d0be4d10efa00372845a1e9725476d83fa49cd937e4f512dda5d9968b8a`，新中文 SHA `aa4ad53702962a05c956b7c82253a2502919b20c9b861330c5642d9ec18cc769`。Python 3 静态核对专用启动文件、获批 F7、资源表差异、启动变量、相对文档链接及 M01 来源交接、M02–M05 原文。首次因检查脚本的章节分隔也匹配三级标题而退出 1，按行首精确定位后退出 0。四段启动命令经 `/bin/zsh -n` 通过，命令正文仅做语法解析。`git diff --check` 对双语手册及本记录退出 0。
- 仅交接本次文档差异供独立复核，B 运行状态仍为 `needs_owner_m01`。本次未执行启动命令、未读取或修改项目根 `.env`，也未操作 profile 内容、数据库或服务。来源采用、B 运行核验及最终验收按现有交接继续。

## DAA-008 r4 · M01 来源材料只读 checkpoint（2026-11-10，Asia/Shanghai）

Human Owner 确认已停采并以原生界面交接两个来源，截图中的下一序号为 75 / 74。实际 Development `/root/daa008_r4_m01_source_handoff_dev` 根据 B01-3 第5项执行一次本次新 profile 只读材料导出。此处是 M01 阶段事实记录，完整 B 的 Development handoff、独立 Verification、后端采用及 Human Owner 终验仍待后续步骤。

- 在既有私有操作根 `O/helpers/observe_new_profile.py` 排他创建一次性只读 observer，权限 0600，SHA-256 `3c3e706a74c8956528004b9e68f1e1aebd32a51ff383767eba684e5b60f87613`。入口缺省只输出帮助，显式 `--capture` 固定本轮新 runtime、实例和两条来源，拒绝侧文件、身份/状态变化及已有证据目录。以 `mode=ro`、`query_only` 和一次短事务读取，不取得产品 ProfileLock，也不使用 immutable/nolock、ATTACH、恢复或应用数据库写入。捕获前后 runtime 的设备、inode、尺寸和 mtime/ctime 一致，config/runtime 的 journal/WAL/SHM 均不存在。已核目标及来源设置为空，投递轮、分片、批次、回执、事件均为 0。
- 导出至新建 `O/evidence/m01-source-handoff/`，目录 0700、文件 0600。证据包含 `context.utf8` 原 UTF-8、`sources.json`、`cycles.jsonl`、`samples.jsonl` 和 `receipt.json`。两个 JSONL 中的 manifest 和 sample 原字节使用可逆 Base64 保存，连同原 SHA 和身份字段逐条对应，未将 GUI 格式化 JSON 作为原始字节。context 长 7248 字节，重算 SHA-256 为 `939011c366610666e289c5665d3a466c0bcb546d04a292bef54bb06b79d318eb`，与两条界面材料一致；receipt SHA-256 为 `1aaddedfd9ef440d6709821dd9afeb8c078cc10df8764cd1221dfd3818e592b5`。
- 两条来源的 definition-set SHA 均从实际 context 按固定投影和 pf-json/v1 域摘要重新计算，与界面材料一致。公开合同的 definition 与 definition-set 摘要向量均通过。147 轮和 147 样本逐条核对 manifest、原 payload、SHA、revision、PLC、generation、group、DB21、序号及点位定义，均为 good 且待上报。C008-A 为序号 1–74、next 75，C008-B 为 1–73、next 74。实际样本时间为 `2026-11-10T11:25:24.252+08:00` 至 `2026-11-10T11:26:36.768+08:00`；记录实际采集区间，不将其写作手册的 5–10 秒短窗。
- Development 自检：`/usr/bin/python3 -I -B` 解析 observer AST、无参数帮助、公开 definition/definition-set 向量及受限数字反例，均 exit 0；显式 `--capture` 真实执行一次、exit 0；独立读取已导出证据并解码全部 Base64，逐项重算 context、147 manifest、147 sample、证据文件 SHA，核对目录及文件权限，exit 0。本 checkpoint 未执行 MySQL、HTTP、source adopt、API scope 变更或服务重启。私有 helper 与材料因后端接续和后续核验需要保留；候选差异由主协调继续处理，不能据此宣称采用或 B 已通过。

## DAA-008 r4 · B-RUN-01 来源采用与 M02 前置（2026-11-10，Asia/Shanghai）

Human Owner 明确同意以当前 DAA 候选接续 B-RUN-01，完成 C008-A/B 的来源采用。主协调固定 59 文件候选范围 SHA-256 `aaa975420a729302861273c6540bdc2d90ed85fab62337b1b9d62cc0b1d018bd`，排他保存的私有候选收据 SHA `6ba925b62cae7b09b2ab6c0199d4357069a6ac57111831fa5400c523719f3879`；32 项静态 pin、710 项 provider/DS pin 均逐项匹配。此前冻结的 M01 context、样本及原配置证据未更改。实际 Development `/root/daa008_r4_m01_source_handoff_dev` 在原批准专用资源上完成以下有限步骤。

- 定向检查登记的 MySQL 8.4.6 容器 ID、任务标签、唯一专用卷与网络、`127.0.0.1:13381` 端口及无自动重启。沿用已固定的 `O/helpers/backend_runner.py`（SHA `e4bff1eaea3223d133049f6e43ead4d83f989f0571a961025d656e0c0ccb50dc`），app、maint 两个角色分别执行只读 audit：schema `daa008_r2_b01`、71 表、revision `0a2c4e6f8b10`、F7 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`、RR、`+08:00` 与逐表授权匹配，采用前七张 facts 表均为空。使用项目锁定的 `uv run --offline --frozen --no-sync --no-env-file python -I -B`，项目模块导入前隔离 dotenv、环境及目标连接；未输出凭据。
- 在私有 `O/helpers` 排他新增 `b01_source_adoption.py`（0600，SHA `fc5477f31e9d19ae619143b58f8df73e4e5e2cda6e020ed89faea407f0988355`），固定候选、来源原文、schema 和精确采用目标；调用正式 `MaintenanceOptions` / `execute`。A、B 均先独立 dry plan，再通过各自已固定 plan 摘要、显式确认和 CAS 0 进行 apply；两个实际提交使用同一新 storageEpoch `a50afe42-cf9e-43ee-bcfa-0a249e145382` 和 A 返回的 adoptionId `b45c0bd6-02f6-46b7-87e7-3f4903bb0df1`。A plan/apply SHA 分别为 `7bb8d7be6c67ae2e68cf256d59f60c2667e0c6a61ce5859c32839ec3ff1cd891` / `a0645ab78c6ae8792c3b7f7effa015bc7852a8bd17d4beb4b5b31aa197bfa171`；B plan/apply SHA 分别为 `a6ab9aa3618179f7ce00e5f173facf0ec566d8603dae60bf44237ee3fe4a56d6` / `a7efc694fee4688555c3c649c6a76b6f06ff6f18f4e39482f0e3e736c34c4948`。每次提交后单独只读核对；两条绑定均为 revision 1、seqFrom 1、seqThrough 9223372036854775806，来源 UUID、generation、context、definition 摘要及空 raw-only 窗口均与 M01 一致。
- `O/evidence/m01-source-adoption/binding-receipt.json`（0600，SHA `db9702cc2f128aff03724667d08edc43c568a5dbfc132446ed0c761f09a8f3b3`）固定两来源及界面填写值。`B-RUN-01/<adoptionId>` 和对应 `.../C008-A`、`.../C008-B` 是根据实际采用 ID 与绑定生成的人可读核对引用，不声称这些字符串由后端直接返回。
- 仅停止原隔离 API 已核实的 worker 55205，保留 relay 55204；使用新增私有 `O/helpers/b01_adopted_api.py`（0600，SHA `f3cea8df83539fba3b4ccd5b074a52ceb632fd2c0738f500274ad89edd288a60`）先在锁定环境中 `--check`，核三条正式路由、单 worker、指定端口与两来源 scope，再启动同一隔离 API。新 wrapper 32348、worker 32350 监听 `127.0.0.1:18283`，原 relay 55204 仍监听 `127.0.0.1:18281`。新的进程收据 SHA `1dda1f5394a10ed3dede2bc06dfff92387a71c1cd44eba0117848238aad2c461`。只在受控进程启用 facts 与两条已采用 PLC scope，不更改产品代码或项目根 env；辅助启动检查依赖已固定候选、私有收据与原专用库，而不要求 DAA runtime 在用户后续保存设置后保持旧 inode 时间。
- 经 relay 对 A、B 各一次 latest GET、一次 history/changes GET：四次 HTTP 200，合同、时间、响应结构及空 `items` 均核对通过；一次未采用合成 PLC 的 GET 返回 403 `plc_facts.scope_rejected`。验证回执 SHA `18035f11ecbcb11c103fa80ad24c72e3ebd07b851bdc37fb4bafeadb5b24eb20`。首次本地校验脚本在已收到 HTTP 200 后因系统 Python 3.9 的 `fromisoformat` 不能解析九位小数而退出；改为校验正式九位小数及日期后，重新完成上述有界只读验证。该错误属于校验脚本，不据此归因后端，也没有重试数据库写入。
- GET 后执行一次 maint 只读完整身份和容量账核对（exit 0）：stream 1、binding 2，batch、sample receipt、raw、cycle 和 latest 均为 0；`O/evidence/m01-source-adoption/post-read-db-audit.json` SHA `b881c2590ec83f37a51c7e996996d9b0a2819c63f94b7ee3f2b74b8864922f8a`。本步骤没有 POST、采集或派发；原隔离 profile、已有历史、其他资源和既有证据保留。就绪结果为 `needs_owner_m02`，等待 Owner 填写上报设置与手动验证；M02–M05、完整 B Development handoff、独立 Verification、阶段 C 终验均未完成。
