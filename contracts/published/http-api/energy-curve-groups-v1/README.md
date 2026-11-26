# Energy curve groups v1

Administrators configure one chart per meter and sampling group under **Energy Management → Configuration → Curve settings**. Energy Statistics can display a saved group or query directly by meter.

| Method and path | Authorization | Successful data |
| --- | --- | --- |
| `GET /api/v1/energy/curve-configs` | Administrator and meter scope | All scoped groups, including disabled groups |
| `POST /api/v1/energy/curve-configs` | Administrator and meter scope | Created group |
| `PATCH /api/v1/energy/curve-configs/{curveGroupKey}` | Administrator and scope for both the existing and submitted meter | Updated group |
| `GET /api/v1/energy/consumption/curve-configs` | `energy-consumption-read` and meter scope | Enabled scoped groups |

All four methods accept a login user Bearer token. Both GETs accept optional `meterId` and sort by ascending `sortOrder`, then `curveGroupKey`. The success envelope is `{code, message, data}`, with `code: 200`. Here is a synthetic create body.

```json
{
  "curveGroupKey": "meter01-power",
  "titleZh": "1号电表功率",
  "titleEn": "Meter 01 power",
  "meterId": "meter-01",
  "groupKey": "electricity",
  "sortOrder": 10,
  "enabled": true,
  "series": [
    {"metricKey": "phaseAPower", "enabled": true, "lineStyle": "solid"},
    {"metricKey": "phaseBPower", "enabled": true, "lineStyle": "dashed"}
  ]
}
```

Use at least one title. A missing title is returned as an empty string and the UI uses the other language. The globally unique, case-sensitive group key is immutable and uses the existing 1–64 character identifier rule. Percent-encode it as one path segment for PATCH. For keys `.` and `..`, use `%252e` and `%252e%252e` so browsers preserve the segments. For literal keys `%2e` and `%2e%2e`, use `%25%32%65` and `%25%32%65%25%32%65`. PATCH preserves omitted fields and replaces the entire ordered `series` array when supplied.

Each series refers to an existing numeric metric in the selected meter and group. Metric keys may appear once per group. At least one series is enabled. Enabled series share the same quantity and unit. Missing units match each other. A metric's write enablement does not change access to its historical samples. The statistics page uses the first enabled valid series for the existing summary call and takes metric names, precision and units from the energy definitions API.

Missing or invalid authentication returns 401. Permission or meter scope denial returns 403. Unknown groups on PATCH return 404. Duplicate keys return 409. Invalid fields, metric references and unit combinations return 422. An unavailable database or incompatible schema returns 503. Errors use `{code, message, data, errorCode}`.

[OpenAPI](openapi.json) · [中文](README.zh-CN.md)
