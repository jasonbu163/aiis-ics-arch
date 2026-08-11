<!--
  File Path: /backend/app/aiis_demo/README.md
  Description: AIIS Demo reference module guide
  Main Features:
    - Documents the disabled project-local module reference
    - Defines copy/rename, permission and migration boundaries
    - Records restart and no-hot-unload semantics
-->
# AIIS Demo Reference Module

[中文版本](README.zh-CN.md)

`aiis_demo` is a project-local reference for the current backend module shape. It is
reference-only, not a business capability, a second `backend/templates` tree, or an
AIIS shared skill/template mirror. The package is intentionally committed so a real
module can be copied and renamed against an executable example.

## Default composition

- `manifest.enabled` is `False`, so normal application composition excludes the
  router, OpenAPI path and Projection owner.
- The manifest still declares `models_package="app.aiis_demo.models"`. Registry model
  discovery imports that empty package for metadata inspection; importing it adds no
  SQLAlchemy table and performs no DDL, migration, database, seed, mock or external I/O.
- The only route is the harmless reference `GET /api/v1/aiis-demo/ping`. It is exposed
  only by an explicit in-memory enabled override in an isolated test/app.
- `permissions=("aiis_demo",)` is metadata for the copy/rename example. It is not
  authorization, an ACL grant, or a substitute for a real route dependency and
  business permission design.

The ping path is deliberately `API -> services/async_ping.py -> schemas/ping.py` and
returns a static `code/message/data` response with `module="aiis_demo"`,
`status="ok"`, and `reference=true`. It does not open a session, read settings or
files, call a network/PLC/Control Agent, start a task, or emit an audit event.

## Package responsibilities

The package keeps the standard `api/`, `models/`, `schemas/`, `crud/`, `services/`,
`mocks/`, and `seeds/` entrypoints. The empty `models`, `crud`, `mocks`, and `seeds`
packages are honest placeholders: they do not contain commented ORM, fake CRUD,
write helpers, mock providers, or seed runners. An empty placeholder is not an
implemented business capability.

## Copy and rename checklist

Use this module as a starting reference only after a separate business task defines
the new owner and acceptance contract:

1. Copy `backend/app/aiis_demo/` to the new package name and remove every `aiis_demo`
   / demo / reference-only meaning from Python, routes, schemas and documentation.
2. Set `manifest.name` to the directory name, deliberately choose `enabled`, `order`,
   router paths, model package and business permission keys, and keep manifest import
   free of database, network and runtime side effects.
3. Replace the static ping with real API -> Service -> Schema behavior. Keep API thin;
   add CRUD and models only when the capability truly owns persistence. Do not leave
   demo payloads, placeholder permissions, or fake success paths in a real module.
4. Revisit authorization explicitly. Manifest `permissions` does not grant access;
   add and test the real dependency/role policy in the approved business scope.
5. If real models, tables, indexes, constraints or columns are introduced, add and
   review an explicit Alembic migration. Model import never replaces migration and
   does not authorize `create_all` or implicit writes.
6. Add focused route, response, service, authorization, metadata and migration tests;
   do not add the module to a second registry or generator without a new governance
   decision.

## Enabled and restart semantics

Changing `manifest.enabled` may cause a development source watcher to autoreload the
whole backend process; that is development reload behavior, not an in-process hot
plugin contract. If the watcher does not reload, restart the backend manually.

Adding, removing, renaming a module/package, or changing its router/models/services
topology requires a backend process or corresponding container restart so discovery
and composition rebuild from zero. Every source/package change in production requires
restart/redeploy. The composed FastAPI app does not support hot unload: changing an
already-running manifest from enabled to disabled does not remove a mounted router;
restart is required to recompute the exposed surface.

This reference does not enable `aiis_demo` in the real application, publish it, deploy
it, or authorize production use.
