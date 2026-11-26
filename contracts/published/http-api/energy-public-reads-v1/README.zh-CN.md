# 能耗公有读取 v1

[English](README.md) · [OpenAPI](openapi.json) · [请求与回包样例](examples/reads.json) · [规格](../../../../plans/ARCH-ENERGY-003-public-energy-reads/spec.md) · [后端实现](../../../../backend/app/equipment_observation/services/energy_public_reads.py)

在受控内网使用这两条只读接口。公有 GET 不需要 `Authorization`，登记批量 POST 同样免 Token。历史读取同路径的旧 `POST /api/v1/integration/energy/samples` 继续使用机器 Bearer。Web 和管理 API 沿用登录用户 Bearer 及原有权限。[登记批量写入](../energy-registered-ingest-v1/README.zh-CN.md) · [已有 Bearer 写入](../equipment-observation-v2/README.zh-CN.md)

| 接口（前缀 `/api/v1`） | 参数与行为 |
| --- | --- |
| `GET /integration/energy/latest` | 可选 `meterId`、`groupKey`。省略则不按该项筛选。每个匹配的表计和采样组返回一条最新样本，按两个键的 UTF-8 顺序排列，不分页也不截断。 |
| `GET /integration/energy/samples` | 必填 `meterId`、`from`、`to`，可选 `groupKey`、`page`（默认 1）及 `pageSize`（默认 20，范围 1–100）。时间范围含起止时刻。单次读取返回一致的 `items`、`total`、`page`、`pageSize` 和 `totalPages`。 |

响应信封为 `{code, message, data}`，成功时 `data.items` 均为数组。最新样本选择与历史分页均按采集时刻、内部记录 ID 降序确定次序。每条样本包括 `meterId`、`groupKey`、`observedAt`、`quality` 和以指标键为键的 `values` 对象。时间统一输出六位小数和 `+08:00`。只有样本保存完整区间时才一起返回两个区间字段。样本只含实际保存且可解读的指标。零以数值保留，缺测和不能解读的旧槽位省略。指标停用但定义仍在时，其历史记录仍可读取。

语法合法的筛选查不到记录或请求页越界时，返回 HTTP 200 和空 `items`。越界页仍返回匹配总数。非法查询返回 422。数据库不可用、配置目标不匹配或实际读取依赖缺失时返回 503。持续写入可能使不同分页请求的结果发生移动。

## Python 示例

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

## SMA 映射示例

固定表计和采样组时，请求 `/api/v1/integration/energy/latest?meterId=meter-02&groupKey=electricity`，响应根设为 `/data`，数字点位路径设为 `/items/0/values/activePower`。时间和质量路径分别为 `/items/0/observedAt` 和 `/items/0/quality`。这组筛选最多返回一条记录，空数组或未传该指标都表示缺测。一个表计可以有多组，定位单条记录时按表计和组同时筛选。[SMA 映射实现](../../../../automation-world/semantic-mapping-agent/src-tauri/src/domain/http_mapping/mod.rs)
