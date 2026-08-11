# Backend Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- Core modules: user, system, control_agent, schema_maintenance, monitor and aiis_demo.
- Module route discovery is manifest opt-in; security/runtime boundary modules remain explicit.
- Monitor Core is limited to collector/raw/latest field facts.
- `ARCH-MIG-001 r1` now has a single `d4e6f8a0b2c4` Core root for fourteen tables; the operation/metadata parity,
  downgrade and single-head evidence passed fresh-context Verification and received Human Owner final acceptance.
- `ARCH-DOCKER-001 r1` empty-volume runtime proof is owner-accepted. `ARCH-001 r3` Development restored the
  fixed-name hot-reload development stack and production-shaped external-database config/build surface;
  fresh-context r3 Verification is next.

Detailed work records live in the root architecture task bundle and in any separately approved backend task. This index does not carry project business backlog.
