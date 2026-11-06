# PLC facts v1 source contract

Direction: DAA original local samples → Backend facts provider → future SMA facts consumer. `ARCH-BE-009 r1` source and approved isolated MySQL A+B passed independent QA, with [current verification evidence](../../../../plans/ARCH-BE-009-backend-facts-integration/checklist.md). Owner final/provider-ready, actual target adoption, DAA uploader, joint validation and deployment remain pending separate gates. The directory name does not imply publication to an external service.

Versions: `plc-facts/v1`, `daa-local/v2`, `pf-json/v1`, `pf-cursor/v1`.

- [openapi.json](openapi.json): exactly three operations and their recursive component closure. Requests and every 200/403/409/410/413/415/422/429/503/500 outcome are typed. Decimal wire values are JSON numbers; data point keys retain original Unicode/case/underscores.
- [schema.json](schema.json): JSON Schema 2020-12 definitions for request, strict queries, receipts, latest/changes/range and failures.
- [vectors.json](vectors.json): independent stdlib canonical bytes, approved fixed digests, original v2 material and synthetic multi-PLC/multi-DB/group/fixed-fragment examples. They contain no real endpoint or database configuration.

The original v2 text is the sole editable points body; source SHA includes its original bytes. Content/cycle/request/projection/definition digests have distinct domains. Fixed parts preserve sampleId. Complete samples/cycles require the complete expected set; received count and quality are separate. Reliable proof is finite 120 days without renewal. Parent rejection tokens recover from stored original proofs across cursor-key rotation; missing/expired parent proof never authorizes retirement.

Anonymous declarations may be impersonated. Default-off flags/empty PLC scope reject before DB access; an arbitrary profile cannot open the storage gate. Runtime requires separately adopted schema, Shanghai DB time, source generation/definition set and signing key. No login or permission is added or removed elsewhere.

Compared with [AW008](../../../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md), the approved provider refines seven independent tables, original v2 text, fixed part identities, nine-digit facts time, 4 MiB input, explicit source adoption, singleton publication order, finite rejection proofs and cursor gaps. Source generation switches increment sourceEpoch; unchanged point definitions preserve valid latest across unrelated context/revision changes. Three natural months is the maximum logical retention; all reads enforce expiry even when physical cleanup stops. A bounded one-shot maintenance tick has no scheduler or business cascade.

Source truth: [typed schemas](../../../../backend/app/plc_facts/schemas/), [module implementation](../../../../backend/app/plc_facts/README.md), [explicit migration](../../../../backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py), [approved spec](../../../../plans/ARCH-BE-009-backend-facts-integration/spec.md), [Development evidence](../../../../plans/ARCH-BE-009-backend-facts-integration/tasks.md). Machine JSON is generated from the typed runtime and independent vectors; it is not a runtime configuration file.
