# Backend Scripts

Chinese version: [README.zh-CN.md](README.zh-CN.md)

The Core script surface is intentionally small:

| Directory | Purpose |
| --- | --- |
| maintenance/ | Explicit schema and bootstrap-user actions |
| api_smoke/ | Read-only HTTP smoke entry |

Scripts must be run from the backend environment:

~~~bash
uv run python scripts/maintenance/ensure_admin_user.py
~~~

No script in this directory starts a worker, polls a PLC, runs a default migration, or reads a project input. Database writes require an explicit action and a separately approved target.
