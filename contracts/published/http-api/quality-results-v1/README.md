# Quality results API v1

[中文版](README.zh-CN.md) · [OpenAPI](openapi.json) · [Synthetic requests](examples/requests.json)

One normalized task number identifies one quality result. Report parsers run at the edge and submit selected values in `items`; the platform stores the values and serves them through Quality Management. A quality result does not require a Plan or Performance record. The routes below use the `/api/v1` prefix and accept JSON for writes.

| Method and path | Access and behavior |
| --- | --- |
| `POST /integration/quality/upsert` | Trusted network. Create a result or merge submitted fields. |
| `GET /integration/quality/by-task/{taskNo}` | Trusted network. Read one result. |
| `GET /integration/quality` | Trusted network. Read a filtered page. |
| `GET /integration/quality/field-config` | Trusted network. Read enabled definitions and their revision. |
| `GET /quality/results` | Signed-in user with Quality permission. The page includes enabled definitions in `data.fields` for rendering. |
| `POST /quality/results` | Admin, supervisor or operator with Quality permission. Create one result with optional target and enabled, editable fields. |
| `GET /quality/results/by-task/{taskNo}` | Signed-in user with Quality permission. Read one result. |
| `POST /quality/results/upsert` | Admin, supervisor or operator with Quality permission. Update editable fields of an existing result. |
| `GET /quality/field-config` | Administrator. Read all definitions, including disabled fields. |
| `PUT /quality/field-config` | Administrator. Save the complete definition set with its current revision. |

The private `/quality` routes serve the platform Web UI and use its sign-in and role permissions. The public `/integration/quality` routes serve authorized SMA, CA, FF and third-party programs using the same trusted-network contract. Deployers enforce that network boundary. Edge programs handle report parsing and downstream delivery.

## Values and updates

- `taskNo` is trimmed and uppercased in ASCII, then restricted to 1–50 characters from `A–Z`, `0–9`, `.`, `_` and `-`. `targetKey` is an optional case-sensitive identifier, 1–64 characters from the equivalent upper/lowercase ASCII set. A non-null key can be set once.
- Keys in `items` exactly match enabled definitions. Types are strings (up to 255 characters), finite JSON numbers (at most ten integer and four decimal places), JSON booleans, and credential-free absolute HTTP(S) URLs (up to 2048 characters). A link definition can carry display text. The browser uses the URL itself when the display text is blank.
- Omitting `items` or submitting an empty object changes no fields. An omitted key preserves the stored value. Explicit null clears a nullable field. An unset enabled field reads as null. Disabled definitions preserve stored values and omit them from reads. `visible` controls list columns, and `editable` controls human input.
- Definitions contain the stable key, Chinese and English labels, type, optional unit, flags, sort order and optional `linkText`. The set supports up to 100 definitions including disabled ones. A saved key, type and unit are immutable. Keep all previously defined keys in each complete configuration request. Only a successful change advances the configuration revision.
- Both list endpoints accept `taskNo`, `targetKey`, `createdFrom`, `createdTo`, `page` and `pageSize`. The creation range uses an inclusive start and exclusive end. Supply an explicit offset or `Z`. The default page is 1 and the page size defaults to 20 with a maximum of 100. Results sort by creation time and ID, newest first. Result timestamps carry `+08:00`. An identical value retry preserves `updatedAt`.

## Responses

Success uses `{code,message,data,timestamp}`. An upsert returns `data.outcome` (`created`, `updated` or `unchanged`) and `data.quality`. Empty results are allowed on the integration route and carry no report-completion signal.

Manual creation returns HTTP 201 with envelope `code: 200`, `data.outcome: "created"` and `data.quality`. Supply `taskNo` and optionally `targetKey` and `items`. An existing normalized task number returns HTTP 409 with `quality.task_no_conflict`. Its stored values stay intact. A subsequent integration upsert may merge fields according to the existing write rules.

Errors include `errorCode` and `details` alongside the envelope. Common outcomes are `quality.unauthenticated` (401), `quality.forbidden` (403), `quality.not_found` (404), `quality.target_conflict` or `quality.config_revision_conflict` (409), and `quality.invalid_request` (422). For a lost response or `quality.commit_unknown` (503), read the current result or configuration and compare it before resubmitting. `quality.unavailable` (503) indicates storage could not serve the operation.

See the [backend route](../../../../backend/app/quality/api/results.py), [schema](../../../../backend/app/quality/schemas/results.py), [base specification](../../../../plans/ARCH-QUALITY-001-task-quality-results/spec.md) and [manual creation specification](../../../../plans/ARCH-QUALITY-002-manual-results-and-legacy-retirement/spec.md).
