# Field Flow Rust configuration

[中文](README.zh-CN.md)

Human-reviewable YAML v1 contracts and the separate Rust YAML v2 PLC catalog below; synthetic addresses only. Run one configuration at a time; each writes one physical target. This README-only directory is owned by the parent PLAN.

| File | flow.id / kind | instance_id |
| --- | --- | --- |
| [loopback.yaml](loopback.yaml) | demo01 / demo01 | ff-rust-demo01 |
| [basic02.yaml](basic02.yaml) | basic02 / plc_guard_get_int | ff-rust-basic02 |
| [basic03.yaml](basic03.yaml) | basic03 / get_value_guard_int | ff-rust-basic03 |

All three use source_id=demo01-feed, GET http://127.0.0.1:31880/demo01/command, plc_demo/DB1/16 bytes/offset0/INT, interval500ms and input_max_age10000ms. Proxy/server ports are 31102/31103, loopback only, never102/wildcard. business_name values are synthetic_command_to_int, negative_target_get_to_int and positive_bounded_command_to_int. case/flow/kind/source/command/instance have distinct roles; unknown kinds, invalid targets and overlapping writes remain rejected.

See [own guide](../USER_GUIDE.md) for every field/budget and typed input, and [examples](../examples/README.md) for complete two-mode commands and counts. Build/sync/init before fixture command generation; separate dry/execute state. Field addresses/targets are outside these synthetic examples. Preserve original identity/timestamps/database/unknown; renaming or switching databases is not recovery. Standard DB INT is two signed big-endian bytes, not BOOL/REAL/optimized DB.

## Rust YAML v2

[catalog-demo.yaml](catalog-demo.yaml) loads [two independent S7 JSON files](plcs/README.md) through plc_files. Relative paths resolve from the main file directory; symlinks/traversal are rejected. Each file uses ff.plc/schema_version=1, the main file uses schema_version=2, independently of execution SQLite schema1. All three v1 configurations and basic02/basic03 remain; v2 supports demo01/read_points only. See the [run steps](../USER_GUIDE.md#catalog-v2).
