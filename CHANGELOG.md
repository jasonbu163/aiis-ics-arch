# Changelog

Chinese version: [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)

## 1.0.0 — Source baseline

- Established the AIIS ICS Architecture public source baseline.
- Separated Core backend, JavaScript frontend, Control Agent, tools and public contracts from consuming project work.
- Rebuilt the Core migration baseline as the single `d4e6f8a0b2c4` root covering fourteen Core tables, with schema changes remaining explicit Alembic work.
- Adopted the fixed-name MySQL `8.4.6` Docker development stack with source binds, one-shot migration and default-off bootstrap controls.
- Retired the obsolete disposable Docker smoke entrypoints from the active repository after their historical empty-volume runtime proof was accepted.
- Documented manifest opt-in, route/locale discovery and the database/PLC/runtime boundaries.
- Established `docs/` as the root-PLAN-owned index for durable cross-repository guidance, with the multi-project guide at its canonical path while `contracts/` remains the root Core contract hub.
- Recorded frontend module assembly and packaged Control Agent configuration as independent follow-up workstreams.

This is a source-only record. The authoritative fixed-version model is a `release/<semver>` branch plus an annotated `v<semver>` tag on the same commit; this preparation record does not claim those refs have already been published. Version 1.0.0 includes no hosted GitHub Release, build artifact, deployment or production-readiness claim.
