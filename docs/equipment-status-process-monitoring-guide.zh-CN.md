# 设备状态、过程监控和能耗操作手册

[English](equipment-status-process-monitoring-guide.md) · [项目文档](README.zh-CN.md) · [r10 操作与背景](equipment-status-process-monitoring.zh-CN.md#r10-guide) · [v2 机器合同](../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md)

过程监控的能耗统计页面地址为 `/monitor/consumption`，唯一页面授权键为 `monitor.energy`。旧直链 `/monitor/energy` 已退出。已有 `monitor.consumption` 的部署须由负责人审查并显式处理，页面权限不会增加 `energy-consumption-read`、表计范围或管理权限。 私有 profile 的目标 revision 须为 `c9e1a3b5d720`，历史样例中的 revision 按实际获批目标填写。 [清退规格](../plans/ARCH-OBS-002-legacy-observation-retirement/spec.md)

## 1. 准备环境和权限

在已获授权、前端和后端服务已就绪且数据库已完成对应迁移的测试环境操作。先请环境负责人准备专属合成设备（示例为 `obs-demo-device`），需要测能耗时再准备专属表计 `obs-demo-meter`。实时接口会整包覆盖同一设备和任务的快照，测试请避开现有设备和任务。使用示例键前确认它们在目标环境可用，因为区域、指标、卡片和曲线是全局配置。

环境负责人在仓库外的私有 profile 中合并本次设置，保留现有配置。核对 `target.serverUuid`、`schema`、`schemaRevision` 与实际后端数据库目标一致，使用真实目标标识和独立凭据，样例中的 UUID 和摘要均为占位符。[v2 私有 profile 样例](../contracts/published/http-api/equipment-observation-v2/example-profile.json)

- `devices` 登记设备键 `equipmentId`、双语名和 `staleAfterSeconds`、`futureToleranceSeconds`。在 `readScopes` 为相关人类角色（包括执行管理的 `admin`）添加设备键。使用实际登录账号，卡片、曲线、能耗页面的读取权限分别为 `equipment-observation-read`、`monitor-observation-read`、`energy-consumption-read`。配置管理和数据管理要求 admin，记录仍受设备／表计范围约束。
- `producers` 登记并启用合成发送方，`kind` 可用 `external`。通过安全渠道向发送方交付随机 ASCII 机器 Bearer。计算令牌的 SHA-256，只把 64 位小写十六进制摘要填入 `tokenSha256`。为同一个 `equipmentId`、`groupKey: heatZone1` 分别添加 `target: latest` 和 `target: history` 两条 `grants`，每条的 `metricKeys` 均含 `zone1Actual` 和 `zone1Set`。机器授权与人类账号分开。
- 如需能耗，在 `meters` 登记表计键 `meterId` 和双语名，在 `meterReadScopes` 给相应人类角色分配表计，在发送方的 `energyGrants` 授权该 `meterId`、`groupKey: electricity` 和 `metricKeys: ["energyInterval"]`。

由环境负责人确认后端 `OBSERVATION_ENABLED=true`、`OBSERVATION_PROFILE_FILE` 指向该私有文件，并协调重载进程以加载缓存的配置。Web 管理页负责定义区域和展示，设备／表计身份及机器授权由 profile 管理。下拉列表为空时先查相应登记与读范围。刚配置时也可能还没有卡片、曲线、表计指标或样本。

## 2. 创建加热区、指标和两路槽位

以 admin 打开 **设备状态 → 配置管理**，在每个页签点 **新增**，填完点 **保存**。

1. **区域配置**。此处的 **指标键** 填区域键 `heatZone1`（`groupKey`）。**类别**选 **温控工艺**，**中文名称／英文名称**填「加热区 1」／「Heating Zone 1」，**排序**填 `10`，打开 **启用**。
2. **指标设置**。新增下表两条，**采样组**下拉选择「加热区 1」，**类别**随区域带出，**类型**选 **数字**，**单位**填 `°C`（可选），**小数位**填 `1`。

   | 指标键 | 中文名称 | 英文名称 |
   | --- | --- | --- |
   | `zone1Actual` | 实际温度 | Actual temperature |
   | `zone1Set` | 设定温度 | Set temperature |

3. **槽位设置**。对下表逐条新增，**采样组**在表单中手填区域键 `heatZone1`，**指标键**下拉选对应名称，每条打开 **启用**。

   | 写入目标 | 采样组 | 槽位 | 指标键 |
   | --- | --- | --- | --- |
   | 实时（`latest`） | `heatZone1` | 1 | `zone1Actual` |
   | 实时（`latest`） | `heatZone1` | 2 | `zone1Set` |
   | 历史（`history`） | `heatZone1` | 1 | `zone1Actual` |
   | 历史（`history`） | `heatZone1` | 2 | `zone1Set` |

每个目标、每个区域独立使用 1–100 号槽。已用槽位的绑定及指标类型、单位等物理含义受保护。只看实时的指标可只建实时槽。修改显示名后，发送方仍使用原有稳定键。

## 3. 配置卡片和曲线

1. **设备状态 → 配置管理 → 卡片设置 → 新增**。**指标键**填卡片键 `heatZone1Card`（`cardKey`），**页面**选 **温控工艺**，**中文标题／英文标题**填「加热区 1 温度」／「Heating Zone 1 Temperature」，**排序**填 `10`，打开 **启用**。点 **添加指标** 两次，选实际温度和设定温度，启用两项并保存。每张卡最多启用 10 项。
2. **过程监控 → 配置管理 → 曲线设置 → 新增**。**指标键**填图框键 `heatingTemperature`（`curveGroupKey`），**类别**选 **温控工艺**（温度类），**中文标题／英文标题**填「加热区温度」／「Heating Zone Temperatures」，**排序**填 `10`，打开 **启用**。点 **添加指标** 加入并启用两条 `°C` 数值指标，保存。同一图框使用同类别、同单位的数值指标。卡片、曲线、实时写入和历史留存各有独立配置，画出历史值还需要启用历史槽并收到样本。

## 4. 手动发现、上报和查看

以下命令用于专属测试设备。将示例地址换成获准环境的 API 基址，核对设备、任务、已授权的区域和指标键，请环境负责人通过安全渠道提供机器令牌，在下方终端提示中隐蔽输入。明文避免写入文件、命令参数或 shell 历史。用请求客户端时可填入其 Bearer Token 栏。

```bash
OBS_API='https://observation.example.invalid/api/v1'
printf 'Machine token (hidden): '
read -r -s OBS_MACHINE_TOKEN
printf '\n'

printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
  curl --fail-with-body -sS -H @- "$OBS_API/integration/metric-definitions?equipmentId=obs-demo-device"
```

GET 只返回当前机器获准的区域和指标定义，包括类型、单位及两路启用状态。两条指标在两个目标均启用后，将下面的共同请求正文保存为 `observation.json`。发送前将示例 `observedAt` 替换为实际采样时刻（合成测试用模拟采样发生的时刻），保留时区偏移。若使用不同样本，填新 `eventId`。任务号是字符串，保留前导零。

```json
{
  "eventId": "obs-demo-000042-001",
  "data": {
    "equipmentId": "obs-demo-device",
    "taskNo": "000042",
    "observedAt": "2026-11-18T10:00:00+08:00",
    "quality": "good",
    "groups": {
      "heatZone1": { "zone1Actual": 810.2, "zone1Set": 815.0 }
    }
  }
}
```

```bash
printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
  curl --fail-with-body -sS -H @- -H 'Content-Type: application/json' \
  --data-binary @observation.json "$OBS_API/integration/equipment/latest-snapshots"

printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
  curl --fail-with-body -sS -H @- -H 'Content-Type: application/json' \
  --data-binary @observation.json "$OBS_API/integration/monitor/history-samples"
```

- **实时**。同一设备、任务仅保留最新整包。较晚采样会覆盖所有区域，未传区域或值清空为缺测。机器需要整个替换范围的权限。
- **历史**。显式传 `quality: "good"`，仅追加已启用历史槽的指标。两路可用同一事件号，各自返回回执。每路核对 `outcome`、`recordId`、`stored`／`skipped`。同一目标重试保留同一发送方、`eventId` 和原始正文。
- **数值**。用原始类型的标量，单位填在配置中。缺测时省略区域或指标，`null` 不是有效的指标值。数字 `0` 和布尔 `false` 均是有效值。其他可省略字段见 [v2 机器合同](../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md)。

打开 **设备状态 → 温控工艺**，选择测试设备，在任务下拉选 `000042` 或使用 **跟随最近采样**，点 **刷新**。卡片的「实际温度 (°C)」应显示 `810.2`，「设定温度 (°C)」应显示 `815.0`。其他卡片入口为 **生产参数、传动工艺、清洗工艺**。

打开 **过程监控 → 温度曲线**，选同一设备，在 **任务号**输入 `000042`，选择覆盖实际采样时刻的上海时间范围，点 **查询**。历史横轴取 `observedAt`，更新时间 `updatedAt` 不参与绘制。一条样本对应每条曲线上的一个点，再用较晚采样和新事件号上报，可看见两点形成的趋势。无样本时保留空轴并提示原因；其他曲线入口为 **传动监控、清洗监控**。

## 5. 添加第二个区域和检查数据

新建另一个温控区域 `heatZone2`，登记 `zone2Actual`（「2 区实际温度」／「Zone 2 actual temperature」）和 `zone2Set`（「2 区设定温度」／「Zone 2 set temperature」），便于按名称从下拉列表选择。在各自目标下分别使用该区的槽 1、2。按需新建第二张卡，在现有 `heatingTemperature` 图框追加同为 `°C` 的两个指标。由环境负责人补齐两个目标的第二区授权并加载。下一次发送同一设备和任务的新整包时，在 `data.groups` 同时传 `heatZone1` 和 `heatZone2`，保留仍需显示的实时值。重新查询温度曲线后，用 **选择区域** 勾选单区或多区，也可点 **全选区域**。

| admin 入口 | 筛选、显示和编辑 |
| --- | --- |
| **设备状态 → 数据管理** | 按设备、采样组（填 `heatZone1`）和任务号筛选实时快照。点 **指标列设置**选择显示列和顺序，点 **详情**核对原始采样值，可保存备注。 |
| **过程监控 → 数据管理 → 过程样本** | 同样按设备、采样组和任务号筛选，还可选采集时间范围。用 **指标列设置**选择显示列和顺序，点 **详情**核对采样值，可保存备注和 **异常／已复核** 标记。 |
| **过程监控 → 数据管理 → 能耗样本** | 按表计和采样组查询，在 **表计指标配置**设置 **显示列**和 **列顺序**。在列表核对采样值，通过 **编辑**保存备注和 **异常／已复核** 标记。 |

这些设置用于显示和标注，界面不提供原始值编辑或删除。

## 6. 配置并上报能耗

1. 打开 **过程监控 → 配置管理 → 表计指标配置**。选测试表计，**采样组**填 `electricity`，**先点查询，再点新增**。在表单确认 **采样组**、**指标键** `energyInterval`、**槽位** `1`，双语名称「时段用电量」／「Interval electricity use」，**物理量键** `electricityConsumption`，**计量方式**选 **时段增量**（`interval`），**单位** `kWh`，**小数位** `1`。打开 **启用**和 **显示列**，**列顺序**可设 `10`，保存。连续性和最大采样间隔规则用于累计读数。
2. 用机器 GET 发现获准且启用的表计定义，再用独立的能耗 POST 提交下面的 `energy.json`。将事件号、表计、组、指标和时间替换为本次获准的实际配置和采样；增量样本用真实区间，起点早于终点。能耗按表计与组上报，无需任务号。

   ```json
   {
     "eventId": "obs-demo-energy-001",
     "data": {
       "meterId": "obs-demo-meter",
       "groupKey": "electricity",
       "observedAt": "2026-11-18T10:15:00+08:00",
       "quality": "good",
       "intervalStartAt": "2026-11-18T10:00:00+08:00",
       "intervalEndAt": "2026-11-18T10:15:00+08:00",
       "values": { "energyInterval": 2.5 }
     }
   }
   ```

   ```bash
   printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
     curl --fail-with-body -sS -H @- "$OBS_API/integration/energy/metric-definitions?meterId=obs-demo-meter&groupKey=electricity"

   printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
     curl --fail-with-body -sS -H @- -H 'Content-Type: application/json' \
     --data-binary @energy.json "$OBS_API/integration/energy/samples"
   ```

3. 在 **过程监控 → 能耗统计** 选表计、`electricity` 和「时段用电量」，将统计起止设为示例样本的实际完整区间，点 **查询**。区间完整时示例为 **时段用量 2.5 kWh**。到 **能耗样本**按表计和采样组核对原记录。若区间有缺口、重叠或跨统计边界，查看不完整原因。

**累计读数**（`cumulative`）的用量取起止边界读数之差，需要确认单位、连续性及换表规则，并设置允许的最大采样间隔。缺边界、连续性未知、读数下降或质量异常时，用量不补零。**时段增量**只合计完整覆盖统计区间、互不重叠的合格增量。**瞬时量**（`instantaneous`，如 kW 功率）只看读数或曲线，不能直接求和为用量。只含累计或瞬时指标的包不带区间字段。同一笔消耗避免同时叠加累计计算和区间增量。

## 7. 排查和收尾

- **没有设备／表计选项**。检查人类读取权限、profile 的登记和读范围，以及服务是否已加载。**有选项但无数据**时，再核对启用的指标、卡片或曲线、对应槽位、任务和采集时间范围。检查回执中的 `stale`、`no_history_metrics` 或跳过项。
- **请求失败**。`401` 查机器凭据，`403` 查授权和完整替换范围，`422` 查键、类型、带偏移的时间和历史质量，`409` 查事件号与正文冲突。`503` 可能是目标未就绪、竞争失败或提交结果未知。先核对目标状态和已知回执。重试相同事件时按 v2 合同保留原事件号和原文，避免改号重复保存。
- **清理测试数据**。保留目标、发送方、事件号和记录 ID。需要清理时，由环境负责人核实归属、其他引用及授权后按精确记录处理。

手动 HTTP 上报验证的是当前环境的配置与机器接口。SMA 产品接入、DAA／PLC 联调及生产部署各自需要对应验证。
