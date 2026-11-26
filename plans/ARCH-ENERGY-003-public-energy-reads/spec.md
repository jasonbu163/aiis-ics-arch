Task ID: ARCH-ENERGY-003
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development 按 STD 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 能耗公有最新值与历史样本读取
Owner: Core 能耗管理
Acceptance Chain Reference: Human Owner 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-007、ARCH-OBS-008、ARCH-OBS-010、ARCH-ENERGY-002

# 能耗公有读取 API · r1

## 1. 目标和依据

提供两条用于 SMA、CA、Field Flow、Python 程序及其他调用方的能耗读取接口。一条取得每个表计／采样组的最新一条样本，另一条按表计和采集时间范围分页读取历史样本。接口沿用本项目响应信封与能耗事实，返回便于直接解析的指标键和值。

Human Owner 于 2026-11-25（Asia/Shanghai）确认 [v5 交互原型](../../work/energy-curves-pricing-review-v5.html)，并明确表示“确认 v5 原型，批准按 STD 修订单价规格并起草能耗曲线设置、公有 GET 规格，先不启动开发。”此前确认两条公有 GET 和公有登记 POST 均免 Token，界面 API 保持登录 Bearer。随后 Human Owner 明确批准 r1，交由 Development 按 STD 实施。

当前 [ARCH-OBS-010 r1](../ARCH-OBS-010-energy-registered-batch-ingest/checklist.md) 已最终验收，登记来源可通过免 Token POST 写入一包一表或多表。原型的两个公有 GET 目前属于候选合同，不代表已有路由。本任务只读已有能耗表，不新增写入身份或修改采样事实。

## 2. 范围和原则

1. 新增 `GET /api/v1/integration/energy/latest` 和 `GET /api/v1/integration/energy/samples`。两者均不需要 `Authorization`，按既有公有登记接口的受控内网接入方式使用；是否附带 `Authorization` 不影响这两条 GET 的身份和结果。无需 `sourceKey`、用户登录、机器 producer、Token 或来源到表计授权。
2. 两条公有 GET 返回当前服务目标库中符合条件的已保存能耗样本，包括登记 POST 和旧 v2 写入的可解读历史。筛选不按登录用户角色或发送来源启停过滤，样本缺失时不制造记录。继续核验现有能耗目标库身份及实际业务依赖，遵循根契约的无关迁移兼容原则。
3. 页面读取、配置管理及登记管理 API 保持现有 Bearer 和权限。已有 `POST /api/v1/integration/energy/samples` 是旧机器 Bearer v2 写入，与本任务 GET **同路径、不同方法**，各自保留认证和合同；已登记来源的 `POST /api/v1/integration/energy/registered-samples` 继续免 Token。一方的中间件或 OpenAPI security 不得改变另一方法。
4. 能耗样本、表计指标和回执归能耗域。本任务不依赖实时／过程设备表、来源表、样本、任务号或跨域外键、JOIN，不新增任务号校验。需业务联合时由调用方分别读取后处理。
5. 单价、曲线配置、第三方客户端、SMA／CA／FF 源码和真实现场操作不在本任务。Python 与 SMA 配置示例是合同说明和可执行的合成验证资料。

## 3. 通用响应与样本表示

成功为 HTTP 200，响应为 `{ "code": 200, "message": "success", "data": ... }`。两个 GET 的 `data.items` 都是数组；每个元素代表一个表计、一个采样组的一条真实样本，字段为：

| 字段 | 含义 |
| --- | --- |
| `meterId` | 表计标识，如 `meter-02`。 |
| `groupKey` | 该表计的采样组，如 `electricity`。不同表计可以有同名采样组。 |
| `observedAt` | 实际采集时刻，以 `+08:00` 和六位小数输出。 |
| `quality` | 该样本原有质量，如 `good`、`bad`、`unknown`。不因质量筛掉最新一条。 |
| `intervalStartAt`、`intervalEndAt` | 该样本实际保存了完整时段时返回，均按 `+08:00` 和六位小数输出；无区间时省略两个字段。 |
| `values` | `{指标键: 数值}`，仅包括该样本实际保存并可通过能耗指标配置解读的字段。合法 `0` 保持为数字零。 |

`observedAt` 是采集时刻。区间增量需要真实的开始和结束时刻，纯累计或瞬时样本无需区间；读取时保留实际事实，不以采集时刻猜测区间。样本中没有的指标不填零、不从较早样本补值。历史槽位按该表计、采样组的 `energy_metric_configs` 解读，已停用但仍有定义的指标历史可读。若旧数据槽位缺少可解读配置，按现有能耗样本读取行为省略该槽位，不能把值误配给其他指标；整条样本及其他可解读值仍返回。

不暴露内部来源身份、回执、后台映射、操作者或任务号。查询标识使用能耗现有标识规则和大小写敏感语义。客户端以 JSON 数字读取，不能把 `0` 当缺失。

## 4. 取得最新样本

`GET /api/v1/integration/energy/latest` 接受可选 `meterId`、`groupKey`，不要求时间或页码。省略一个参数表示不按该参数过滤，两个都传时按交集过滤。

| 请求 | 返回 |
| --- | --- |
| `/latest` | 所有已有样本的表计／采样组，各一条最新样本。 |
| `/latest?meterId=meter-01` | 此表计各采样组，各一条最新样本。 |
| `/latest?groupKey=electricity` | 各表计的该采样组，各一条最新样本。 |
| `/latest?meterId=meter-01&groupKey=electricity` | 此表计／采样组的一条最新样本。 |

每个 `(meterId, groupKey)` 按 `observedAt` 最大选样本；采集时间相同时按样本内部记录 ID 最大选一条。返回数组按 `meterId`、`groupKey` 的 UTF-8 升序稳定排列。无匹配返回 `data.items: []`。不按指标把不同采集时刻的值合并到同一条样本，也不按接收时间或修改时间冒充采集时间。无筛选请求不分页、不截断结果。

示例请求：

```http
GET /api/v1/integration/energy/latest?meterId=meter-02&groupKey=electricity
```

示例回包：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "meterId": "meter-02",
        "groupKey": "electricity",
        "observedAt": "2026-11-24T13:00:00.000000+08:00",
        "quality": "good",
        "values": { "activePower": 0 }
      }
    ]
  }
}
```

这里 13 点样本只带 `activePower`，12 点曾上报的 `totalEnergy` 仍可从历史读取；即使它是该指标最近一次出现，也不拼接进 13 点样本。

## 5. 按时间范围读取历史

`GET /api/v1/integration/energy/samples` 要求 `meterId`、`from`、`to`，可选 `groupKey`、`page`、`pageSize`。时间参数为带偏移的可表示事件时间，规范到上海时区后以 `observedAt` 筛选，包含起点和终点；`from == to` 可查询同一时刻。时间反向或格式非法为 422。`page` 从 1 开始，默认 1；`pageSize` 默认 20，范围 1–100，沿用现有页面查询口径。范围或页内无数据返回空 `items`，`total` 与 `totalPages` 正确，空结果的 `totalPages` 为 0。

按 `observedAt` 降序、内部记录 ID 降序分页，保留每条样本的实际质量和实际字段。省略 `groupKey` 返回该表计各组，传入时限定该组。采样数据是追加事实，持续写入可能使不同请求之间的页次变化；单次响应的 `items` 与分页统计应来自一致的数据库读取视图。

示例请求中的 `+` 需 URL 编码为 `%2B`：

```http
GET /api/v1/integration/energy/samples?meterId=meter-02&groupKey=electricity&from=2026-11-24T12%3A00%3A00%2B08%3A00&to=2026-11-24T13%3A00%3A00%2B08%3A00&page=1&pageSize=20
```

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "meterId": "meter-02",
        "groupKey": "electricity",
        "observedAt": "2026-11-24T13:00:00.000000+08:00",
        "quality": "good",
        "values": { "activePower": 0 }
      },
      {
        "meterId": "meter-02",
        "groupKey": "electricity",
        "observedAt": "2026-11-24T12:00:00.000000+08:00",
        "quality": "good",
        "values": { "totalEnergy": 9820, "activePower": 21.3 }
      }
    ],
    "total": 2,
    "page": 1,
    "pageSize": 20,
    "totalPages": 1
  }
}
```

必填参数缺失、标识不合法、页码不合法或时间非法返回 422，沿用现有观测错误信封。目标库不可达或实际依赖不可用返回 503；未知但语法合法的表计／组及无匹配范围返回 HTTP 200 空列表。查询只返回已有样本，不写回执或业务表。

## 6. 接入示例

以下 Python 使用标准库，并通过 `urlencode` 保留时间偏移中的 `+`。地址仅为本机示例，应按调用环境配置。公有读取无需认证头。

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

SMA 当前 HTTP 映射可直接读取固定表计和组的最新示例。将请求参数设为 `meterId=meter-02`、`groupKey=electricity`，响应根设为 `/data`，数值点位路径设为 `/items/0/values/activePower`，类型为 `number`，采集时间路径设为 `/items/0/observedAt`，质量路径可设为 `/items/0/quality`。该筛选最多一条，因此索引 0 是固定语义；空数组或无此指标时按 SMA 当前缺测行为处理。全量数组不能仅用一个 `meterId` 选择条件保证唯一采样组。此处描述源码支持的映射方式，真实 SMA 页面／现场联调另行确认。CA 当前 HTTP 单节点可展示响应正文，下游通用嵌套字段提取不在本任务范围。[SMA 映射实现](../../automation-world/semantic-mapping-agent/src-tauri/src/domain/http_mapping/mod.rs#L230) · [CA 节点输出](../../automation-world/control-agent/src-tauri/src/domain/ca_flow.rs#L290)

## 7. 实施范围、兼容与风险

- 允许修改 `backend/app/equipment_observation/` 中能耗公有读取路由、样本投影／查询及必要的共享错误和 OpenAPI 处理；优先复用现有 `energy_consumption_main`、`energy_metric_configs` 和能耗目标库核验。不得修改其他域语义。
- 允许新增或调整 `backend/tests/`、`backend/tests_mysql/` 中与两条 GET、旧 POST 兼容、空值和排序直接相关的测试。使用合成资料，Python 和 SMA 路径可用确定的回包夹具验证。实际 SMA／CA／FF 客户端源码和现场行为不在本范围。
- 允许在 `contracts/published/http-api/energy-public-reads-v1/` 新增中英文合同、运行时一致的 OpenAPI 和合成请求／回包向量，更新 `contracts/README.*`、`backend/app/equipment_observation/README.*` 和直接相关的 `docs/equipment-status-process-monitoring{,-guide}.*`，列出公有 GET 与旧 POST 在同一路径下的认证差异，提供 Python 和 SMA 示例。实际结构变化时按根契约更新 `CODE_INDEX.md`。
- 本 r1 复用既有索引 `ix_energy_sample_meter_time`，不新增数据库表、索引或 Alembic 迁移。如果实施发现真实技术依赖需要结构变化，返回 PM 修订并获得精确批准。无 Token 读取返回服务内可匹配的能耗数据，按用户确认的受控内网使用。真实部署、dev 数据库变更和服务切换按项目契约另行授权。
- 多任务可能同时触达同一能耗路由和说明，Development 应基于当前交付工作树合并，不覆盖其他已交接工作。回退时移除或禁用新增 GET 的应用改动，保留原能耗样本、回执、旧接口和配置。
- 本任务 Development 使用 `backend-arch` 和 `code-document-indexer`；若发布合同或修改文档链接，按项目现行工具检查。独立 Verification 以真实后端隔离 HTTP、MySQL 和合成数据验证；完成隔离验证不构成真实现场联调或部署。

## 8. 验收标准

| ID | 可验证结果 |
| --- | --- |
| AC01 免 Token 与现有权限 | 两 GET 无 `Authorization` 可读；附带任意 Authorization 不改变 GET 内容。登记 POST 免 Token、旧同路径 v2 POST 仍要求原 Bearer，界面样本／配置仍要求用户 Bearer，OpenAPI 分别正确。 |
| AC02 最新筛选 | 无参数、仅 meter、仅 group、两者的结果与四种组合一致；未知筛选为空数组。每个表计／组按 observedAt、ID 选一条，乱序写入、相同时间不同记录和 bad／unknown 质量均按实际最新输出。所有结果稳定顺序，不截断。 |
| AC03 字段与时段 | 数值零保留，未传值缺席，最新样本不与旧样本拼接。各表计、各组独立，时间为 `+08:00` 六位小数；有效时段按真实值返回，无区间时省略。历史已停用指标及旧 v2 数据可按现有配置正确解读。 |
| AC04 历史查询 | 核对必填参数、可选组、含两个边界的时间范围、时区等价、相同时间 ID 次序、默认及边界页码、空结果和多页数据；非法参数返回 422。数据与分页总数在单次读取中一致。 |
| AC05 接入示例 | 以真实隔离 HTTP 回包验证标准库 Python 同时读取最新和翻页历史，保留 0 并显示缺测。对固定表计／组验证 SMA 所示 JSON Pointer 可取值与时间，空数组／缺字段正确反映缺测；不宣称 SMA 原生现场联调。 |
| AC06 回归与工程 | 旧 v2 Bearer POST、登记 POST、多表回执重放、界面 GET 权限及设备／过程入口回归；模拟无关后继 revision、能耗实际结构兼容时两个 GET 仍可用；真实依赖缺失或数据库不可用返回 503。运行 uv 聚焦测试、必要隔离 MySQL、OpenAPI、合同向量与文档链接检查。 |
| AC07 数据边界 | 读取前后比较相关能耗样本、回执、指标和旧实时／过程数据，确认无写入、跨域关联或任务号要求。验证本任务没有新的数据库结构迁移，交付对象和限制记录于任务 bundle。 |

## 9. 修订与交接

| 日期 | 记录 |
| --- | --- |
| 2026-11-25（Asia/Shanghai） | Human Owner 确认 v5 原型并批准按 STD 起草本规格，未批准 Development。 |
| 2026-11-25（Asia/Shanghai） | Human Owner 明确表示“批准 ARCH-ENERGY-003 r1，按 STD 启动 Development。”据此批准本任务精确 r1。 |

Human Owner 已批准 r1。由 Development 建立 `tasks.md` 并按精确范围实施、自检，再交 fresh-context Verification；最终验收由 Human Owner 决定。
