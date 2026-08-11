# Lineage Audit

`lineage-audit` statically inventories frontend sources, backend routes/models
and their evidence links. It is an offline review tool: it does not call an API,
read a database, inspect PLC data or generate business mappings.

## Usage

From `tools/`:

```bash
uv run python lineage-audit/main.py \
  --frontend-root ../frontend-js/src \
  --backend-root ../backend/app \
  --outputs-dir lineage-audit/outputs
```

The checked-in `inputs/` and `outputs/` directories are intentionally empty.
Use a private or temporary fixture directory for a real audit run. Generated
CSV/JSON/Markdown evidence must not be committed to this public baseline.
