# Minimal source import pair

[中文](README.zh-CN.md)

Owned by the [DAA PLAN](../../../../PLAN.md), this structural fixture supports DAA-004 controlled source-import validation. `minimal.db` and `minimal.udt` are handwritten UTF-8 sources, not actual TIA exports or site inputs. `expected.json` is an independent verification checklist authored from the approved leaf table before these sources, not runtime configuration or parser-generated output.

Select the DB and its UDT together through the ordinary Points source-file input, bind both to the selected disabled PLC, and explicitly enter DB number **21**. The DB declares `MinimalImport` with standard access and one `payload` field referencing `MinimalPayload`.

| sourcePath | Type | Imported defaults |
| --- | --- | --- |
| `payload.ready` | BOOL | disabled, no group, no address |
| `payload.count` | INT | disabled, no group, no address |
| `payload.temperature` | REAL | disabled, no group, no address |

Expect two editing sources, one complete non-flat DB with the full reference-expansion tree, three points and zero groups. Source/DB/point IDs are service-generated; verify their PLC/DB/source references and stability after reload rather than preselecting UUIDs. Source SHA-256 must match the selected file bytes. No offset is inferred for this UDT and no default length is an evidenced DB length.

Selecting only the DB diagnoses the missing UDT; preview and Cancel do not commit. For this validation, confirm only the complete pair with no issues, then reload and reconcile the same owned SQLite database. Existing confirm semantics can save candidates with diagnostics; this fixture adds no blocking rule. Activation, connection and collection are outside this validation. This pair establishes neither TIA export compatibility, live PLC addresses nor real-device behavior. The one-time YAML receipt remains separate and unchanged.
