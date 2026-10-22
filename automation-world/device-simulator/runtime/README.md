# Rust Simulator Runtime

`ds-runtime` 0.1.0 is the shared product business library. It owns UUID instance management, generic DB images, typed big-endian encoding, six write sources, CAS, five deterministic rules, per-item fairness, admission budgets, stopped revision loading and DS configuration SQLite. It directly consumes the frozen `aiis-tia-import-core` 0.1.0 API; it does not fork the parser, naming algorithm or DAA transport.

Default `native-s7` builds the finite native adapter automatically. The desktop also selects this feature explicitly. Construction restores valid selected revisions with initialized values and stopped instances; saving does not apply or start. SQL and network IO remain outside the image owner lock. Stop admission and generation changes do not wait behind an apply SQL transaction. A committed selected revision with failed installation is reported as `load_failed`; the diagnostic old image cannot serve.

[Product build](../BUILD.md) · [Validation](../tests/README.md) · [Approved scope](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)

`test-automation` is non-default. Its required-feature test host shares the same App/services/owner and adds only fixed owned-manifest commands, bounded barriers/overlays and one-shot per-store transaction fault points. It creates no second image or product IPC. Historical G0 files remain unregistered until conditional retirement; they are not normal build entries.
