# DS Frontend Module

`simulator/manifest.ts` registers DS locales; `console/sections.ts` is the explicit six-page navigation registry. The DAA-derived shell, CU theme/language controls and Element Plus provider remain shared presentation infrastructure. No DAA acquisition, SQLite client, upload or history module is registered.

The six views and eight bounded editors/confirmations consume the normal 16-command facade in `services/deviceSimulator.ts`. `useDeviceSimulator` is the host state owner: dirty draft, saved configuration and actual runtime snapshots are separate; visible refresh is bounded to 1 Hz, stale failures retain the last valid snapshot, and instance/page identity rejects late responses. The Rust runtime performs import, layout, naming, policy, encoding, rules and CAS; Vue does not duplicate them.

User-visible text belongs to symmetric `simulator/locales/en-US.json` and `zh-CN.json`. Technical UUIDs and actual DB/byte/bit/revision are shown as facts, not derived from the editable draft. Browser preview has no desktop bridge and cannot return simulated IPC success. The native test driver is a non-default fixed test surface, not a frontend module or product control API.
