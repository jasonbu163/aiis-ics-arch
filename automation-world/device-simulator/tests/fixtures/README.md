# Synthetic Inputs and Independent Expectations

- `protocol-workspace.json` preserves the original DB41 (1024 bytes), DB57 (64 bytes), DSG0A001/B001 markers, absolute point offsets and permission vectors solely for the original W/C/D/X regression. The product has no such default topology. Test setup uses the real configuration/layout/naming/confirmation/apply services before starting.
- `product-workspace.json` uses UUID A with DB71/88/109 and UUID B with DB94/130 on the two approved ports. Independent integer, finite REAL and complete STRING bytes are written/read over actual S7; A reset/stop/new-revision apply is observed while B continues reading.
- `typed-vectors.json` contains handwritten min/zero/max big-endian expectations. REAL assertions compare the intended IEEE f32 bits, not an unrelated f64 decimal rounding artifact. STRING includes the complete two-byte header and zero-filled tail.
- `rules-vectors.json` records independent SHA-256 input messages and expectations for deterministic random rules, alongside cycle/phase/floor tests. Rules use simulated monotonic time; pause/stop freeze that time.
- `invalid-cases.json` lists synthetic bounds and source rejection groups. A listing is not execution proof: the Rust consumer tests and raw results must establish each outcome.

The unchanged shared v1 `names.db`, `names.udt`, `expected-v1.json` and four layout oracles are read directly from their owning shared/DAA fixture paths by DS tests. They are not copied, normalized, regenerated or rewritten. TIA declaration/BEGIN initializers remain ignored; DS initial values require explicit confirmation. No fixture contains a real customer endpoint or project source.
