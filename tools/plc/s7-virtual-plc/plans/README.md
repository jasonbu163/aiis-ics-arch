<!--
  File Path: /tools/plc/s7-virtual-plc/plans/README.md
  Description: S7 virtual PLC task-plan index
  Main Features:
    - Links detailed task records owned by the virtual PLC tool
    - Separates active plan dashboard from durable implementation detail
-->
# S7 Virtual PLC Task Plan Index

Chinese version: [README.zh-CN.md](README.zh-CN.md)

This directory contains detailed, canonical task records for `tools/plc/s7-virtual-plc/`. The parent [PLAN.md](../PLAN.md) is the active dashboard and keeps only current status, acceptance and next gates.

## Rules

- Update the parent `PLAN.*` when task status, acceptance, blockers or the next gate changes.
- Keep concrete implementation steps, protocol decisions and verification evidence in one canonical Chinese `<task-id>.md` record. Do not add a translated task-record mirror unless external collaboration requires one.
- The tool README remains a usage guide. Update it only when an implemented command or runtime contract changes; a plan-only decision must not describe future behavior as current behavior.
- Cross-tool SOP changes belong in `docs/`; CA runtime behavior remains owned by `control-agent/`.

## Task Records

| Document | Purpose |
| --- | --- |
| [P4-strict-tsap-validation.md](P4-strict-tsap-validation.md) | Implemented strict virtual-PLC rack/slot identity: explicit simulator identity, COTP called-TSAP rejection and CA matching/mismatching read-only integration evidence. |
