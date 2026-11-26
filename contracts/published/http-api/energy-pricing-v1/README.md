# Energy pricing v1

All methods use a logged-in user's Bearer token. Read and write permissions are independent. Configuration writes also require the admin role.

| Method and path | Permission | Successful `data` |
| --- | --- | --- |
| `GET /api/v1/energy/pricing/items` | `energy-price-read` | All definitions, including disabled items |
| `POST /api/v1/energy/pricing/items` | `energy-price-manage` and admin | Created definition |
| `PATCH /api/v1/energy/pricing/items/{itemKey}` | `energy-price-manage` and admin | Updated definition |
| `GET /api/v1/energy/pricing/current` | `energy-price-read` | Enabled items with their individually latest applicable price and metadata |
| `GET /api/v1/energy/pricing/hours` | `energy-price-read` | Paginated actual hour updates and independent columns |
| `POST /api/v1/energy/pricing/hours` | `energy-price-manage` | Recorded hour and only the submitted item prices |

Success uses the shared `code`, `message`, `data` and `timestamp` envelope. Missing authentication returns 401, forbidden access 403, a duplicate item key 409 and invalid input 422.

Project definitions have `itemKey`, `nameZh`, `nameEn`, `unit`, `sortOrder` and `enabled`. The case-sensitive key is trimmed on input and is immutable. Supply at least one name. The page uses the other name when its language is missing. Percent-encode the key for PATCH. Use `%252e` and `%252e%252e` for the literal keys `.` and `..`. Use `%25%32%65` and `%25%32%65%25%32%65` for the literal keys `%2e` and `%2e%2e`. Omitted PATCH fields keep their values. Once the item has any price, its unit is fixed. Lists sort by `sortOrder` then `itemKey`.

Send `items` as a map of keys to `{price, remark?}`. At least one entry is required. Prices accept JSON numbers or decimal strings between 0 and 999999.9999 with at most four effective fractional places. No rounding is applied. JSON responses use numbers. An omitted project is left intact. In submitted projects, omitted `remark` preserves the existing remark in that hour. Empty or null remarks clear the field. Top-level `remark` follows the same omission and clearing rules. `observedAt` is an ISO datetime with an offset and optional seconds and up to six fractional digits. Null or omission captures server time once. Future events are rejected.

The current array contains `itemKey`, `nameZh`, `nameEn`, `unit`, `price`, `remark`, `observedAt`, `updatedAt` and `operator`. For items with no eligible price, the last five fields are null. The hourly endpoint accepts optional strict `date=YYYY-MM-DD` in IANA `Asia/Shanghai`, `page` default 1 and `pageSize` default 24 and range 1–100. Omit date for all history. Returned hours contain `hourStart`, `remark` and `values`, keyed by the original project key, each with `price`, `remark`, `observedAt`, `updatedAt` and `operator`. Absent values indicate that a project was not updated in that hour. A zero is a recorded price. `columns` contains all enabled projects and any disabled projects with prices in the query range, independent of pagination and empty results. Wire timestamps use fixed `+08:00`.

The three older `/energy` routes share the same price records and continue serving their original wire shapes. Each complete legacy hourly row may inherit a component from an earlier hour. Migration and recovery details are maintained with the backend module. [Module](../../../../backend/app/energy/README.md)

[OpenAPI](openapi.json) · [Item example](examples/item.json) · [Partial price update](examples/price.json) · [中文](README.zh-CN.md)
