# Local acquisition fixtures

Sanitized deterministic inputs for DAA-002. These are not site configuration or live PLC facts.

- `flat.db` / `offsets.json`: nine BOOL leaves followed by BYTE/INT/REAL. The independent expected offsets are 0.0–1.0, byte 2, INT 4, REAL 6; even DB length 10. No recursive layout assumptions.
- `nested.db` / `nested.udt`: complete ARRAY[-1..1] of UDT and ASCII STRING declarations. Import expands seven disabled/unassigned leaves; addresses require manual confirmation.
- `invalid.db`: multidimensional array rejection with real file/line/path.
- `transport.json`: two frozen in-memory endpoints and DB byte arrays, including a REAL with more than three decimal digits. It never opens network sockets. Only explicit debug validation or cfg(test) compiles this adapter. Native Snap7 tests separately own loopback sockets/servers.
- `empty.env`: explicit local mode/read gates, all old DB/write/auth/autostart gates closed. Copy it only into a newly owned canonical system-tmp validation profile; do not replace real env files.

Validation profiles require `.daa-local-validation-owner` containing exactly `DAA-002-r2-owned\n`, explicit absolute env/profile/fixture paths and no symlink ancestors/inherited DAA overrides. The optional frozen `failAt` supports named activation/commit failpoints only. `cycle_hot_journal` flushes the actual product transaction's page cache, emits a marker and waits at most 10 seconds for the owned controller's SIGKILL; it is not arbitrary SQL. Product code has no ACK fixture command. ACK seed rows remain only in cfg(test) Rust tests.

Offset basis: [Siemens S7-300 integration application, §5.3 p34](https://support.industry.siemens.com/cs/attachments/50708061/50708061_application_pcs7_s7300_en.pdf) describes BOOL packing, next-byte BYTE/CHAR and WORD boundaries for other standard types, with an independent BOOL/BYTE/BOOL example. [TIA standard DB principles](https://docs.tia.siemens.cloud/r/en-us/v21/programming-data-blocks/basic-principles-for-programming-of-data-blocks) states final DB size is padded to a WORD. These support only the stated standard flat subset; they do not establish optimized/complex layouts or replace a separately authorized TIA/site check.
