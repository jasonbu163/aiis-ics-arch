# Stage C facts delivery guide

[中文](STAGE_C_GUIDE.zh-CN.md)

DAA-008 r1 implements an A-only source candidate. The [Development record](plans/DAA-008-reliable-facts-upload/tasks.md) contains actual checks and the known hot-journal recovery blocker. A0/A1 is not fully passed; actual HTTP/DS/MySQL, native visual checks and complete Stage C acceptance remain pending. Do not run the procedure below until its specific B environment is separately approved.

## Preconditions and ownership

- Preserve all existing profiles, configuration and history. A legacy config-v2/runtime-v2 profile remains local-only; this release does not migrate or upload its history.
- B must name a genuinely new, empty absolute DAA profile, Backend candidate/origin/target ID, dedicated MySQL schema/revision/time profile, admitted PLCs and source bindings, controlled DS instances, permitted faults and resource cleanup. This guide provides no target or deployment authorization.
- The Backend owner adopts schema/time/source using its own approved process. DAA never receives MySQL/HMAC credentials and cannot perform adoption. Anonymous source declarations are admission material, not authentication.
- Use the existing ordinary `pnpm tauri dev` entry only after B approval. Application startup always leaves connections, collection and delivery stopped. The debug fixture host cannot use the facts HTTP adapter.

New empty profiles create config SQLite v2/runtime SQLite v3. Samples/manifests stay v2 and contexts stay v1. Unknown combinations, missing stores, WAL material, identity/time/schema mismatches and symlinks fail closed. r1 currently also fails closed on a real hot rollback journal: do not delete journals, lower versions or use an old binary to force-open v3. Keep the whole new profile and report the error; the recovery protocol requires r2 approval.

## Configure once, then operate explicitly

1. Start the approved new profile and verify stopped state. Prepare the smallest already accepted PLC/group configuration; activate/connect/collect remain separate actions. Importing or saving never starts I/O.
2. Save at least one complete local round. Open **Source handoff material** in Reporting and storage. Give the Backend owner the exact instance/PLC/generation, context SHA, definition-set digest and sequence window. No HTTP is sent when this material is generated.
3. After the Backend owner confirms adoption, open **Delivery settings**. Enter its verified target ID, origin and adoption reference; select only verified PLC sources with their exact decimal-string windows and references. The default delivery interval is 5 seconds, permitted 1–3600 seconds. Contract digests are fixed and read-only. Saving uses a separate CAS and does not create a collection revision.
4. Use **Read test (GET)** with an existing PLC: the default test performs latest with limit 1. It tests read admission only. A missing latest/history fact cannot establish that an earlier POST failed.
5. Load local history and open the original-cycle preview. The request is generated from complete committed original payload/manifest/context bytes; there is no JSON editor or second point-upload switch.
6. Explicitly start collection and delivery in Workbench. They are independent controls. The uploader sends one HTTP request at a time, preserves frozen identities and gives latest/history opportunities in a persisted 3:1 rotation across PLCs/groups. It freezes at most eight unresolved requests.
7. Confirm that **reliable confirmation**, rather than HTTP sends, increases the local confirmed sample count. Open a delivery for its immutable digest/member/parent binding and original receipt. A sample is confirmed only after every fixed part has a validated receipt and the single-runtime ACK transaction commits. Original read quality and receipt-time cycle completeness remain distinct.

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
- Physical quota includes SQLite/journal, requests, receipts, metadata and the additional 32 MiB ACK recovery reserve. High water stops new collection/freezes while preserving recovery; genuine I/O failure can still leave the result unknown. Pending, blocked, unknown and referenced materials are never removed by retention.
- Pause stops new dispatch; the current request finishes within its bounded timeout and persists any valid result. Normal quit keeps unresolved identities. Reopening never restarts collection or delivery. r1's known hot-journal failure remains an explicit blocker to its crash-recovery claims.

## B evidence and stop points

Once separately approved, perform only the necessary increment: controlled values → local original bytes/SHA → POST/receipt → local ACK → latest/history; temporary API loss and recovery; then normal quit/reopen without clicking start and explicit resume. Retain both sides' identity/value/quality/time/digest ledger. Stage B imports/naming/grouping do not need to be repeated wholesale.

Stop and preserve the new profile on storage/schema/time/source conflicts, proof expiry or unknown outcomes. Give the Backend owner target/source/read diagnostics and give Development the batch/receipt IDs and digests, without credentials or parent tokens. Native visual evidence, actual HTTP, DS/MySQL/Docker actions and resource cleanup must follow the exact B proposal. A-only checks and a successful build are not end-to-end or production proof.
