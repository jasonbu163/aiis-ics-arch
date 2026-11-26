# Public energy reads v1

[中文](README.zh-CN.md) · [OpenAPI](openapi.json) · [Request and response vectors](examples/reads.json) · [Specification](../../../../plans/ARCH-ENERGY-003-public-energy-reads/spec.md) · [Provider](../../../../backend/app/equipment_observation/services/energy_public_reads.py)

Use these read-only endpoints on the controlled internal network. Neither GET requires or consults `Authorization`. The registered batch POST is also token-free. The older `POST /api/v1/integration/energy/samples` at the same path as the new history GET still requires its machine Bearer token. Web and administration APIs retain user Bearer authentication and their original permission checks. [Registered batch write](../energy-registered-ingest-v1/README.md) · [Existing Bearer write](../equipment-observation-v2/README.md)

| Endpoint with `/api/v1` prefix | Parameters and behavior |
| --- | --- |
| `GET /integration/energy/latest` | Optional `meterId` and `groupKey`. Omission leaves that dimension unfiltered. Returns one latest stored sample per matching meter and group, sorted by both keys in UTF-8 order, with no pagination or truncation. |
| `GET /integration/energy/samples` | Requires `meterId`, `from`, and `to`. Optional `groupKey`, `page` (default 1), and `pageSize` (default 20, 1–100). Both event time bounds are inclusive. Returns `items`, `total`, `page`, `pageSize`, and `totalPages` from one read view. |

The response envelope is `{code, message, data}`, with `data.items` always an array on success. Samples sort by collection time and internal record ID, both descending, for newest selection and history pagination. Each sample includes `meterId`, `groupKey`, `observedAt`, `quality`, and a `values` object keyed by metric. Times render with six fractional digits and `+08:00`. Both interval bounds appear only when the stored sample has both. A partial sample carries only its recorded, decodable metrics. Zero is a number. Missing values are omitted, including when a stored slot can no longer be decoded. An inactive metric with a retained definition remains readable in its historic samples.

A syntactically valid unmatched meter, group, time range or page returns HTTP 200 with empty `items`. An out-of-range page still reports the matched total. Invalid queries return 422. An unavailable database, a mismatched configured target, or missing actual read dependencies returns 503. Observations arriving between independent page requests can shift the pages.

## Python example

```python
import json
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = "http://127.0.0.1:8000/api/v1/integration/energy"

def get_data(path, **params):
    query = urlencode(params)
    url = BASE + path + ("?" + query if query else "")
    with urlopen(url, timeout=5) as response:
        result = json.load(response)
    if result["code"] != 200:
        raise RuntimeError(result["message"])
    return result["data"]

latest = get_data("/latest", meterId="meter-02", groupKey="electricity")
for row in latest["items"]:
    power = row["values"].get("activePower")
    print(row["observedAt"], power if power is not None else "缺测")

filters = {
    "meterId": "meter-02",
    "groupKey": "electricity",
    "from": "2026-11-24T12:00:00+08:00",
    "to": "2026-11-24T13:00:00+08:00",
}
page = 1
while True:
    history = get_data("/samples", **filters, page=page, pageSize=20)
    for row in history["items"]:
        print(row["observedAt"], row["values"])
    if page >= history["totalPages"]:
        break
    page += 1
```

## SMA mapping example

For a fixed meter and group, request `/api/v1/integration/energy/latest?meterId=meter-02&groupKey=electricity`, use `/data` as the response root, and map the number at `/items/0/values/activePower`. Use `/items/0/observedAt` and `/items/0/quality` for the timestamp and quality. This query returns at most one item. An empty array or omitted metric is missing data. Select both meter and group when identifying one entry, since a meter can have several groups. [SMA mapping implementation](../../../../automation-world/semantic-mapping-agent/src-tauri/src/domain/http_mapping/mod.rs)
