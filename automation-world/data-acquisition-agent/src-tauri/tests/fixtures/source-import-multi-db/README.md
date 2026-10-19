# Handwritten multi-DB source fixtures

[中文](README.zh-CN.md)

Owned by the [DAA PLAN](../../../../PLAN.md), under [DAA-005 r1](../../../../plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md). These synthetic texts were written independently of private Owner inputs. `multi.db` has six DBs and `types.udt` three UDTs. `expected.json` hand-defines leaf paths/types and disabled/unassigned/address-null defaults. DB501–506 (and DB701–704 in layout tests) are synthetic test mappings, never actual block numbers inferred from text. No endpoint or customer data is included.

`layout-oracle.json` was frozen before the new algorithms. It contains the exact Siemens STEP7 V20 (11/2024) official links/paragraphs, a limited non-optimized standard-word profile, hand-authored declarations and each expected leaf byte/bit, array stride and total length. `layout.db` transcribes those declarations after that freeze; the algorithm does not generate the expected offsets. The ARRAY English start sentence contradicts its own even-address clause; the official padding page and its explicit three-BYTE/seven-BYTE-array example determine start/end boundaries. Nested STRUCT/UDT boundaries and BOOL packing are cross-checked against the official STRUCT/BOOL rules.

Run only the matching Rust `tia_source::tests`, `plc_layout::tests` and `local_store::source_import_tests` filters. Engine/store tests create newly owned system-temp profiles and cfg(test) history seeds; they do not use existing profiles or old samples. The layout oracle proves this bounded source profile, not a TIA compile, all CPUs/firmware or actual PLC addresses. STRING/optimized/unknown/incomplete layouts are excluded from inference. Private real source files are not fixtures here and remain ignored/read-only.
