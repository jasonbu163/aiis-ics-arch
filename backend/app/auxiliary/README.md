# Auxiliary business module

[中文版本](README.zh-CN.md)

Auxiliary owns ShiftTeam, Shift, ShiftRule and StopRecord and their existing `/shift-teams`, `/shifts`, `/shift-rules` and `/stop-records` APIs. Its single permission key is `auxiliary`; it does not grant price access. [Energy](../energy/README.md) owns prices. Historical [module PLAN](PLAN.md) and accepted price task records retain their original owner/time facts.

Ordinary GET requests never seed shifts or a default rule. Empty rules return the shared success envelope with `data:null`. The frontend displays “not configured” and disables rule editing/saving until a real id exists. There is no create-rule API; first initialization remains a separately authorized data/configuration action. Existing rule GET/PUT behavior remains available.

CRUD only queries/adds/flushes; explicit writes commit/rollback in Service. StopRecord is publicly exported as `app.auxiliary.models:StopRecord` for declared model consumers. See the [module contract](../MODULE_CONTRACT.md). The explicit 42-table successor includes these four entities; source/recorder checks do not establish applied schema or runtime readiness. Real migration/data operations need their own gate.
