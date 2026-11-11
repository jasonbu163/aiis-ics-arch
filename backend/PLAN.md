# Backend Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- [ARCH-ACQ-003 r2](../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md): `owner_accepted`. The specified dev schema is at `4e6a8b0d2f14`. Both renamed tables preserve their original rows. Human Owner accepted the r2 provider and the verified dev scope on 2026-11-11.

- ARCH-ACQ-002 r2 passed independent QA. Revision `3d5f7a9c1e23` retired nine empty tables in the specified 3307 dev schema and preserved both v2 tables. Human Owner acceptance is pending. [QA record](../plans/ARCH-ACQ-002-legacy-projection-retirement/checklist.md)
- ARCH-BE-012 r4 introduced the sample API and two v2 tables at `2c4e6a8b0d12`. Independent source verification and dev functional checks passed. Its original isolated matrix and final acceptance are pending. [QA record](../plans/ARCH-BE-012-simplified-plc-facts/checklist.md)

- [ARCH-BE-009 r1](../plans/ARCH-BE-009-backend-facts-integration/spec.md): `owner_accepted`; 9 formal MySQL cases and 42 expanded Dev scenarios; fresh QA independently passed 9 formal, 47 named expanded scenarios, 181 focused and 44 legacy tests (9 deselected) passed; A/failure histories retained. Two containers/volumes/networks, eight dedicated schemas and 27 temporary credential/config files were cleaned and independently observed absent. Human Owner accepted the approved source and isolated A+B delivery on 2026-11-05; live adoption, DAA/SMA integration and production SLA remain separate; existing databases/history were not operated on.

- [ARCH-BE-010 r2](../plans/ARCH-BE-010-anonymous-business-integration/spec.md): `owner_accepted`; both real MySQL/ASGI/time/concurrency/disconnect rounds, 161 affected source regressions in each, and permanent business receipts after facts cleanup passed; A/failure histories retained. Two containers/volumes/networks, eight dedicated schemas and 27 temporary credential/config files were cleaned and independently observed absent. Human Owner accepted the approved source and isolated A+B delivery on 2026-11-05; live adoption, DAA/SMA integration and production SLA remain separate; existing databases/history were not operated on.

- [ARCH-BE-005 r3](../plans/ARCH-BE-005-backend-business-module-reintegration/spec.md): `owner_accepted`; Human Owner accepted on 2026-10-16 after independent A and two isolated MySQL rounds, all five scenarios in each round and dedicated resource cleanup; prior histories are preserved.

- [ARCH-BE-006 r1](../plans/ARCH-BE-006-mapping-business-api-expansion/spec.md): `qa_passed`; A+B independently passed, both dedicated MySQL rounds and five-page browser checks completed, resources and test secrets cleaned; 155 related tests passed, four historical frozen-profile failures retained; Human Owner final acceptance pending.

- [ARCH-BE-004 r2](../plans/ARCH-BE-004-energy-price-hourly-history/spec.md): `owner_accepted`; observedAt hourly upsert, daily history and add dialog independently verified, F-001 closed; Human Owner accepted on 2026-10-13 after successful manual use, live data migration separately gated.

- [ARCH-BE-002 r3](../plans/ARCH-BE-002-energy-price-api/spec.md): `owner_accepted`; reusable auxiliary energy-price slice in this repository, three APIs and a successor migration; Independent QA passed; Human Owner accepted r3 on 2026-10-13, real database/runtime validation deferred.
- [ARCH-BE-003 r3](../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md): `qa_passed`; r3 A/B independently passed: current source 483 passed/30 deselected and compileall; all three MySQL scenarios in both rounds passed; F-001/B-001 closed, dedicated resources and test secrets cleaned; Human Owner final acceptance pending.

- Core modules: user, system, control_agent, schema_maintenance, monitor and aiis_demo.
- Module route discovery is manifest opt-in; security/runtime boundary modules remain explicit.
- Monitor Core exposes collector status. The old raw/latest snapshot tables and their Core query are retired.
- `ARCH-MIG-001 r1` now has a single `d4e6f8a0b2c4` Core root for fourteen tables; the operation/metadata parity,
  downgrade and single-head evidence passed fresh-context Verification and received Human Owner final acceptance.
- `ARCH-DOCKER-001 r1` empty-volume runtime proof is owner-accepted. `ARCH-001 r3` Development restored the
  fixed-name hot-reload development stack and production-shaped external-database config/build surface;
  fresh-context r3 Verification and Human Owner acceptance are complete under [ARCH-001](../plans/ARCH-001-public-architecture-baseline-extraction/checklist.md). This historical Core acceptance does not accept later provider adoption.

Detailed work records live in the root architecture task bundle and in any separately approved backend task. This index does not carry project business backlog.

The API-only `plc_facts` owner writes v2 samples and serves scoped queries from the history and latest-point tables. The historical migration order includes BE-009 `0a2c4e6f8b10` → BE-010 `1b3d5f7a9c20`. BE-010 owns four business-integration tables and bounded time compatibility. Human Owner accepted the approved BE-009 and BE-010 source and isolated A+B delivery scopes on 2026-11-05. Their target adoption and DAA/SMA integration remain separate.
