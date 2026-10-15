# Backend Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- [ARCH-BE-005 r3](../plans/ARCH-BE-005-backend-business-module-reintegration/spec.md): `qa_blocked`; A independently passed 319 source tests, offline migrations and browser checks. B MySQL/Docker actions await specific approval and verification; final acceptance is pending. Prior QA histories and parallel AW document changes are preserved; rebaseline BE003 after completing this repair.

- [ARCH-BE-004 r2](../plans/ARCH-BE-004-energy-price-hourly-history/spec.md): `owner_accepted`; observedAt hourly upsert, daily history and add dialog independently verified, F-001 closed; Human Owner accepted on 2026-10-13 after successful manual use, live data migration separately gated.

- [ARCH-BE-002 r3](../plans/ARCH-BE-002-energy-price-api/spec.md): `owner_accepted`; reusable auxiliary energy-price slice in this repository, three APIs and a successor migration; Independent QA passed; Human Owner accepted r3 on 2026-10-13, real database/runtime validation deferred.
- [ARCH-BE-003 r2](../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md): `draft`; this repository equipment temperature pilot for third parties/mapping agents; four choices confirmed, nine data strategies analyzed; temperature granularity and exact scope approval pending; no backend implementation.

- Core modules: user, system, control_agent, schema_maintenance, monitor and aiis_demo.
- Module route discovery is manifest opt-in; security/runtime boundary modules remain explicit.
- Monitor Core is limited to collector/raw/latest field facts.
- `ARCH-MIG-001 r1` now has a single `d4e6f8a0b2c4` Core root for fourteen tables; the operation/metadata parity,
  downgrade and single-head evidence passed fresh-context Verification and received Human Owner final acceptance.
- `ARCH-DOCKER-001 r1` empty-volume runtime proof is owner-accepted. `ARCH-001 r3` Development restored the
  fixed-name hot-reload development stack and production-shaped external-database config/build surface;
  fresh-context r3 Verification is next.

Detailed work records live in the root architecture task bundle and in any separately approved backend task. This index does not carry project business backlog.
