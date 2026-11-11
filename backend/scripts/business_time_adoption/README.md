# Business time adoption evidence

Chinese: [README.zh-CN.md](README.zh-CN.md).

This finite tool inspects the BE010 fixed 13-table/41-column profile, prepares a candidate plan and compares read-only snapshots. It never applies schema/data changes, infers a timestamp's timezone, starts business writers, installs adoption files, or approves adoption. A numeric wall timestamp cannot prove its source basis. Unknown or mixed unclassifiable sources keep G-T closed.

Bare source entry prints help without loading settings, dotenv, modules or a target:

```bash
cd backend
uv run --offline --frozen --no-sync python scripts/business_time_adoption/main.py
```

Only separately approved target operations may use the following shape. Create a private tool env from `.env.example`; select its **absolute** path explicitly. Dedicated process `BUSINESS_TIME_DB_*` keys override that explicit file; there is no implicit tool/backend `.env` fallback. Target configuration is used only for the explicit tool engine. Use a read-only account with access to the fixed application columns, UUID/schema/clock, information_schema and current revision probe. Reports contain counts, metadata and ordered per-column hashes, never raw rows, passwords or DSNs.

```text
... main.py inspect --module equipment --env-file /private/approved/tool.env --source-revision <reviewed-source> --output /private/approved/inspection.json
... main.py plan --module equipment --inspection-report /private/approved/inspection.json --classification-report /private/approved/classification.json --source-revision <reviewed-source> --output /private/approved/plan.json
... main.py verify --module equipment --env-file /private/approved/tool.env --inspection-report /private/approved/inspection.json --source-revision <reviewed-source> --output /private/approved/verification.json
```

`plan` is offline. Classification version `business-time-classification/v1` requires exactly each `table.column` from inspection, with `basis` (`utc_wall`, `shanghai_wall`, `known_offset`, `unknown`), `coveredRows` equal to investigated rows and `evidenceRef` to private source evidence. It cannot turn that assertion into proof; every plan remains `state=candidate`, `adoptionEligible=false`. `verify` compares the same target/profile, row counts and time-column hashes; it does not claim that changed hashes prove correct conversion or unchanged IDs/values/FK/pairs. Those proofs, old HTTP/Projection compatibility, writer isolation, backup, approved data-only conversion and explicit Owner target adoption remain required separately.

The runtime manifest `business-time-adoption/v1` is a different operational artifact: exact module/profile/schema revision (`1b3d5f7a9c20`, `2c4e6a8b0d12`, `3d5f7a9c1e23` or `4e6a8b0d2f14`, matching the actual database), target UUID/schema, fixed-column digest, source revision, complete `be010.fixed-basis/v1`, report digest/reference triples, backup/Owner approval references, Shanghai `verifiedAt`, and `state=adopted`. The tool never promotes candidate reports to it. Protect these external private artifacts and preserve earlier digests on atomic replacement. No raw data/configuration belongs in the public repository.

Output is JSON Lines start/complete/failed plus an explicitly named new JSON report; existing output files are never overwritten. No default inputs/outputs directory, persistent log, packaging artifact or standalone executable is created. Use the project uv environment; standalone packaging is outside this task. A source-only test does not authorize any target operation.
