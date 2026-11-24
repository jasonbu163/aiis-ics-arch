# CA to Field Flow candidate JSON v1

[简体中文](README.zh-CN.md)

Status `proposed`. CA produces and consumes this candidate. The independent Field Flow acceptance gate is pending.

- [JSON Schema](schema.json) describes the closed wire format. [Example](examples/status-gate.json) and [vectors](vectors.json) document the reference graph and outcomes.
- A single entry reaches every node. The graph is acyclic. Mutually exclusive branches may reconverge. Nodes never execute in parallel in this format. Ordinary nodes use one `next` edge, comparisons use `true` and `false`, and `end` has no outgoing edge. Referenced fields must come from an upstream node that has executed along every possible path to the consumer. Read exposes `value`, compare `matched` and HTTP `status`. Compare and simulated write require matching operand types.
- The example reads logical point `plc_line_a/task_status`. An INT value of 1 runs GET and then ends `matched`. Other valid INT values end `not_matched`. Missing or bad-quality reads and wrong types stop the round with an error. A future scheduler waits the interval after completion, never overlaps rounds and never catches up missed ticks.
- No address, credentials, local paths or runtime values belong in a flow. Confirm bindings in the current CA workspace. PLC write is configuration and simulation only in this revision.
- File SHA-256 covers exact UTF-8 file bytes. Semantic SHA-256 covers the `flow` object without `revision`, excluding the top-level envelope and layout. Sort nodes by ID and edges lexically by source ID, port and target ID. Encode JSON as UTF-8 with recursively ordered object keys, no insignificant whitespace, no final newline, and omitted empty optional HTTP maps. The [Rust serializer](../../../automation-world/control-agent/src-tauri/src/domain/ca_flow.rs) is the current candidate reference for string escaping and number formatting.
- Structural validation does not imply semantic validity. The editor also checks declared node versions, unique IDs, connectivity, ports, coordinates, relative paths, types and bound logical resources. Files are limited to 1 MiB and 16 levels.

The same file hash must link later FF acceptance evidence for both branches and a next-round read, followed by reimport into CA.
