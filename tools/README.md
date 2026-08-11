# AIIS ICS Architecture Tools

This directory contains reusable, offline-first engineering tools for Core and
project teams. Tools transform explicitly supplied source files; they do not
fetch project data, connect to PLC/DB services, or publish generated artifacts.

## Tool groups

- `lineage-audit/` — static interface-to-data evidence inventories.
- `lineage-mapping-studio/` — local visual review of lineage evidence.
- `plc/point-mapping/` — reviewed workbook to PLC contract conversion.
- `plc/projection-mapping/` — PLC-to-projection mapping review.
- `plc/snapshot-policy/` — reviewed raw/latest snapshot policy conversion.
- `plc/s7-virtual-plc/` — local simulator support for development checks.

`inputs/` and `outputs/` are empty by default. The checked-in YAML under
`config/` is a sanitized shape example, not a site contract. Keep workbooks,
point tables, mappings, logs and generated reports outside the public source
tree.

## Local checks

```bash
uv lock --check
uv run python -m compileall -q lineage-audit lineage-mapping-studio plc
uv run pytest -q
```

Use a separately reviewed fixture directory for tests that need input data.
