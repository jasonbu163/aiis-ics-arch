# Backend Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- [ARCH-BE-005 r3](../plans/ARCH-BE-005-backend-business-module-reintegration/spec.md): `owner_accepted`; Human Owner accepted on 2026-10-16 after independent A and two isolated MySQL rounds, all five scenarios in each round and dedicated resource cleanup; prior histories are preserved.

- [ARCH-BE-006 r1](../plans/ARCH-BE-006-mapping-business-api-expansion/spec.md): `qa_passed`; A+B independently passed, both dedicated MySQL rounds and five-page browser checks completed, resources and test secrets cleaned; 155 related tests passed, four historical frozen-profile failures retained; Human Owner final acceptance pending.

- [ARCH-BE-004 r2](../plans/ARCH-BE-004-energy-price-hourly-history/spec.md): `owner_accepted`; observedAt hourly upsert, daily history and add dialog independently verified, F-001 closed; Human Owner accepted on 2026-10-13 after successful manual use, live data migration separately gated.

- [ARCH-BE-002 r3](../plans/ARCH-BE-002-energy-price-api/spec.md): `owner_accepted`; reusable auxiliary energy-price slice in this repository, three APIs and a successor migration; Independent QA passed; Human Owner accepted r3 on 2026-10-13, real database/runtime validation deferred.
- [ARCH-BE-003 r3](../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md): `qa_passed`; r3 A/B independently passed: current source 483 passed/30 deselected and compileall; all three MySQL scenarios in both rounds passed; F-001/B-001 closed, dedicated resources and test secrets cleaned; Human Owner final acceptance pending.

- Core modules: user, system, control_agent, schema_maintenance, monitor and aiis_demo.
- Module route discovery is manifest opt-in; security/runtime boundary modules remain explicit.
- Monitor Core is limited to collector/raw/latest field facts.
- `ARCH-MIG-001 r1` now has a single `d4e6f8a0b2c4` Core root for fourteen tables; the operation/metadata parity,
  downgrade and single-head evidence passed fresh-context Verification and received Human Owner final acceptance.
- `ARCH-DOCKER-001 r1` empty-volume runtime proof is owner-accepted. `ARCH-001 r3` Development restored the
  fixed-name hot-reload development stack and production-shaped external-database config/build surface;
  fresh-context r3 Verification is next.

Detailed work records live in the root architecture task bundle and in any separately approved backend task. This index does not carry project business backlog.
