# AIIS TIA import core

[中文](README.zh-CN.md)

`aiis-tia-import-core` 0.1.0 is a publish=false, edition2021, standard-library-only local crate. Its only task authority is [DAA-006 r3](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md); DAA uses `../../shared/tia-import-core` as a real Cargo path dependency. No workspace, registry, runtime, serde or I/O dependency is needed.

Public entrypoints in [src/lib.rs](src/lib.rs): `scan_sources(&[SourceInput], ImportProfile)` preserves supplied UTF-8/BOM/CRLF bytes in the catalog, safely separates declarations and retains block diagnostics; `expand_db(catalog, DeclarationRef, closure)` uses an explicit per-DB closure; `layout_standard(ExpandedDb, LayoutProfile)` produces theoretical byte/bit/length; `plan_names(NameBatch)` performs simultaneous full-namespace naming. `validate_manual_name` and `type_suffix` share the same fixed rules. Low-level parser DTO/functions are public for the existing DAA provenance adapter; they are not a source proof or persistence API.

Profiles are `tia-subset-v1`, `siemens-step7-v20-standard-word-v1`, `tia-point-name-v1`; golden naming fixture version is v1. See [fixtures](fixtures/README.md), [DTOs](src/model.rs), [naming](src/naming.rs) and [independent consumer tests](tests/contract.rs).

Supported: named DATA_BLOCK/TYPE, bounded STRUCT/UDT closure, one-dimensional scalar/STRUCT/UDT arrays with negative/nonzero bounds, comments, VERSION, NON_RETAIN/RETAIN and the existing boolean S7_SetPoint attribute. Expansion is bounded to 8 levels/4096 leaves; arrays to 1024. UTF-8/source limits are explicit. Initializers/BEGIN are skipped, never imported or executed. Unknown syntax/types/attributes, ambiguous declarations, missing/cyclic UDT, nested/multidimensional arrays and excess budgets are rejected. STRING[1..254] imports but refuses whole-DB layout. Layout requires explicit non-optimized complete structure; the oracle is theoretical, not a real PLC address assertion.

Names use structured Field/Index segments, fixed suffixes, 1–100 ASCII bytes, full-namespace flatten collisions and one address fallback; pending has no name. ConfirmedAddress is an assertion of the consumer, which must establish confirmation and DB bounds. A batch represents exactly one PLC namespace and includes reserved disabled/legacy/manual points. The core does not assign IDs or confirm/write addresses.

DAA keeps raw source hash/proof, frozen version closure, stable IDs, conservative reimport, SQL/CAS, receipt, activation and history. DS must map its own instance/region/identity, verify region bounds, and implement initial values, big-endian encoding, memory, permissions and lifecycle itself. It must consume a pinned manifest/ref, never fork the fixture rules. This crate does not implement DS or close DAA Stage B; later DAA–DS protocol validation and Stage C need separate approval.

Source baseline HEAD is `0af5b91177f3bca63f9f3c2bef9f14004ea49944`; this delivery is a dirty-working-tree increment, not a release/ref. The exact parser source SHA, complete file hashes, lock diff, raw commands and limitations are recorded in [DAA-006 tasks](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/tasks.md). Consumers freeze that full manifest (or a later real ref), not “latest DAA”.

```bash
CARGO_TARGET_DIR=/private/tmp/owned-tia-core-target cargo test --manifest-path automation-world/shared/tia-import-core/Cargo.toml --locked
```
