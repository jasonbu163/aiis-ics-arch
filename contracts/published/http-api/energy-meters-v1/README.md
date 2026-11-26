# Energy meter management v1

Administrators manage energy meter identity, bilingual names, and user read scopes through the metric configuration page. All three methods use the existing login user Bearer token and administrator permission.

| Method and path | Request | Successful data |
| --- | --- | --- |
| `GET /api/v1/energy/meters` | None | Meter definitions sorted by `meterId` |
| `POST /api/v1/energy/meters` | `meterId`, `nameZh`, `nameEn`, optional `readRoles` | Created definition |
| `PATCH /api/v1/energy/meters` | `meterId` plus any of `nameZh`, `nameEn`, `readRoles` | Updated definition |

All successes use `{code, message, data}`. A meter definition contains `meterId`, `nameZh`, `nameEn`, and `readRoles`. Meter IDs are 1–64 characters and case-sensitive. For example, `water/A.1` and `water/a.1` identify distinct meters. Names are 1–128 characters. Roles use stable system keys and duplicates are removed. Creation defaults to `["admin"]`. A supplied empty role list removes login read access. An omitted PATCH field retains its current value. The identifier remains fixed.

Database definitions override profile definitions for the same meter. When a profile meter has no database row, its names and scopes continue to come from the profile. An explicit update takes effect on the next applicable request. Existing login endpoint permissions still apply. The registered sample POST and public reads retain their own contracts. Machine v2 grants continue to come from the compatibility profile. [Registered energy writes](../energy-registered-ingest-v1/README.md) · [Public energy reads](../energy-public-reads-v1/README.md)

The endpoint returns 401 for missing or invalid login authentication, 403 for callers without administrator permission, 404 for updating an unknown meter, 409 for a duplicate ID, 422 for an invalid request, and 503 when the configured database or required schema is unavailable. [OpenAPI](openapi.json) · [中文](README.zh-CN.md)
