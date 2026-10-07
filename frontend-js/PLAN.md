# Frontend JavaScript Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- Core pages: login, system/user and system/dict.
- Route, navigation, default entry and locale assembly share the normalized module Registry.
- Project business modules and page IDs are intentionally absent from this Core template.
- [ARCH-FE-001 r3](../plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md): `developer_handoff`; first QA findings reworked, 15 contract test groups and isolated production build passed. Fresh-context re-verification and Human Owner acceptance remain pending; release version is deferred.
- [ARCH-FE-002 r1](../plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md): `draft`; split supervisor/operator page access, three frontend env contexts, and dashboard/plan onboarding are proposed. Owner confirmation of env identity and module scope is pending; no implementation is authorized.

Detailed UI work requires a separate approved task. This index does not carry a project business backlog.
