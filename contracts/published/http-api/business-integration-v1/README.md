# Business integration v1 provider

Chinese: [README.zh-CN.md](README.zh-CN.md).

[openapi.json](openapi.json) contains exactly eight anonymous POST operations and their closed component-reference set, extracted from normal backend module registration. [examples.json](examples.json) contains the eight normative requests, request/business digests, complete success/error examples and frozen `bi-json/v1` normalization vectors. The wire version stays `aiis.business-integration/v1`; r2 is the implementation-task revision.

This is `source_ready_unadopted` source. Defaults are disabled/empty/unadopted. Scope admission precedes adoption checking and session creation; `shanghai-v1` additionally requires the exact external `business-time-adoption/v1` evidence, finite basis profile and a transaction-local target UUID/schema/revision/DB-clock match. No setting string alone enables business writes. Actual schema/time adoption, database/Docker/B and Owner acceptance remain separate gates.

| Resource | Values / technical storage domain |
| --- | --- |
| temperature | All ten set/actual °C values; exact NUMERIC(30,10), abs < 10^20, at most ten decimal places. |
| drive | At least one of 20 values; binary32. TV/KM units undefined; dew point °C, oxygen ppm, pressure Pa, gas flows m³/h, five tension pairs kN. |
| production_parameters | Exact coil; at least one of grade/entryTime/thickness/width/totalTime/weight/speed. Binary32 nonnegative quantities; mm, minutes, tonnes, m/min. No process-step invention. |
| production_observation | Explicit in/not-in/unknown status. In production requires coil and may carry thirteen observations. Weight/output/qualified NUMERIC(10,4), length (10,2), diameter (8,2), density (5,3), rates/scores (5,2), all nonnegative. Quantity/density/qualityScore units are undefined; no guessed conversion or <=100 clamp. |
| process_temperature | Four NUMERIC(8,2) °C values and integer duration 0..9999999999 **minutes**; at least one value. |
| process_tension / process_speed | Nonnegative NUMERIC(10,2), kN / m/min; at least one value. |
| process_curve | At least one of 33 metrics: twelve signed int32 °C temperatures; 21 binary32 measurements. Speed m/min, unc/rec tension P %, four tension Kg fields retain the old kg label, fans Hz, N₂ total m³, electricity total kWh, flows m³/h, oxygen ppm, dew point °C, pressure Pa. Cumulative observations do not create billing/energy summaries. |

JSON uses numbers/integers only, never numeric strings or null measurements. Omission is missing data and persists SQL NULL; zero is observed. Decimal excess scale/range rejects without rounding. FLOAT is normalized once to binary32, finite abs <= 3.4028234663852886e38, relative error <=1e-6 and absolute error <=max(1e-6,abs(input)×1e-6); nonzero underflow rejects. Digests use the exact decimal value of that stored binary32. Temperature/tension min/avg/max and speed avg/max must remain ordered after the complete NULL-fill merge.

Source timestamps accept explicit Z/offset and reject nonzero submillisecond tails, normalize once to +08:00, and must not exceed the injected DB clock by five minutes. Receipt sourceTime/committedAt use exactly three fractional digits and +08:00; source-reference timestamps retain necessary precision. Production DATE and elapsed seconds/minutes are separate semantics. Fixed old HTTP UTC wire/fingerprints/JSON results remain compatibility views after controlled adoption.

Delivery identity is module + producerId + eventId. Identical retries preserve all first facts except outcome=duplicate; changing routing/parent/data/presence/mapping/source with the same identity yields event_conflict before a business conflict. Temperature/curve are immutable, drive/parameters/process only fill NULL, and production uses a serialized device watermark plus an independent permanent historical event index. Process parent IDs must come from a reliable in-production receipt of this channel; missing parents return 404, mismatched/legacy parents 409. Manual weight including zero and valid manual time pairs retain priority.

A successful receipt confirms the committed business transaction or a durable stale decision; stale always has decision_only/applied=false/null target/empty affected IDs. `committedAt` is the winning transaction's last DB clock sample before commit, not the exact physical instant the engine finished commit. Caller must validate version, identity, digests, target and confirmation, then persist its own ACK. A bare HTTP 200, flush, log or raw-facts ACK is insufficient.

Errors use actual HTTP 403/404/409/413/415/422/503/500 and the module-local code/message/data:null/errorCode schema. 404 and parent_mismatch are process-only; observation_time_conflict is observation-only. For commit_unknown, unavailable, internal failure or lost response, retain the original frozen identity/body and reconcile by resending it. A content repair is a new logical event and still obeys the business key. Raw expiry does not delete business, source/mapping evidence or minimal receipts; these have no automatic TTL. Production aggregates may evolve and do not promise a complete version history.

Generation uses the normal guarded `create_app(testing=True).openapi()`, selects the eight `/api/v1/integration/{equipment,performances,monitor}` POSTs and recursively includes every referenced schema. Actual generation argv, hashes and DEV checks are recorded in [ARCH-BE-010 tasks](../../../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md); no listener, lifespan, DB, Alembic or Docker runs to generate these files. Static source chain is BE009 0a2 (71 application tables) followed by BE010 1b3 (75), excluding alembic_version. This provider is independent from the facts provider and grants no authentication/permissions to old APIs.


Generated artifact SHA-256: `openapi.json` = `d92bf03a9e8b3e4575fddc9caa68233e6b415210a6965c0a29b6b99264727562`; `examples.json` = `2255e6752cb8079d813ddc65773f07460cbfdedc0c00d10faaec63064d7cc724`.
