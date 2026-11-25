Task ID: ARCH-OBS-010
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development 按 STD 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 能耗独立来源登记与多表批量写入
Owner: Core 能耗管理
Acceptance Chain Reference: Human Owner 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-007、ARCH-OBS-008、ARCH-ACQ-007

# 能耗写入登记与多表 POST · r1

## 1. 目标和当前状态

在「能耗管理 → 配置管理」增加写入登记，让已登记且启用的发送方使用一个免 Token 的 HTTP POST 一次提交多个表计的能耗样本。沿用现有表计指标配置、能耗样本和统计计算。Web 使用登录用户 Bearer；发送方可以是 SMA、脚本或第三方，不区分产品类型。一个请求采用整包校验、一个事务提交和逐项回执。

Human Owner 于 2026-11-24 确认[能耗原型](../../work/energy-management-full-review.html)并授权按 STD 起草规格，随后明确批准本任务精确 r1 启动 Development。原型中的示例数据和临时交互不构成接口实现；本文件定义获批合同和验收。

[ARCH-OBS-007 r1 A](../ARCH-OBS-007-energy-management/checklist.md#human-owner-最终验收) 的四页归并已获 Owner 接受。本任务接续其 B 阶段方向，使用独立任务及验收链，不改写 A 的记录。[ARCH-OBS-008](../ARCH-OBS-008-runtime-compatibility/spec.md) 已修复设备／过程读取的全库 revision 依赖，其最终验收状态以该任务记录为准。

当前能耗表计和登录用户可读表计范围来自私有 profile，表计指标维护在页面的表计指标配置。现有能耗机器 v2 接口使用 Bearer 和独立的生产者授权；当前没有登记来源免 Token 的多表入口。[现有 v2 合同](../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md)

### 1.1 r1 选择

本 r1 采用 **同一能耗来源的同一个规范采集时刻对应一包**。同一时刻需要上传的多表、多个采样组和指标应放在同一包。相同身份重复原包返回原回执，内容不同返回冲突；不静默合并或覆盖。若现场同一来源在同一真实采集时刻确需拆为多包，须另行修订身份合同。本 r1 不要求发送方提供外部事件号。

## 2. 领域、权限与页面

1. 能耗来源登记、样本与回执归能耗域。引用已有写入登记的字段、交互和通用报文格式。能耗不依赖设备状态或过程监控的登记、样本、任务号和回执，不做跨域外键、跨域表 JOIN 或任务号存在性检查。需要业务联合查询时，调用方分别读取，再在业务层处理。
2. 「能耗管理 → 配置管理」上卡增加「写入登记」选项，保留现有「表计指标配置」。下卡提供关键词查询、重置、新增、编辑、启停、删除和重置列宽。普通列通过公共列宽工具拖动并本机保存，异常、空表及无匹配状态清楚显示。PC 1440×900 与平板横屏 1024×768 分别检查中英文、明暗主题；弹窗遵循根契约 §9，点击遮罩按取消处理。
3. 登记表单只维护 `sourceKey`、可选 `name` 和 `enabled`。标识大小写敏感，允许 1–64 个 ASCII 字母、数字、点、下划线或连字符。名称可空或 1–128 字符；新登记默认启用，编辑时标识不可变。与设备状态的登记生命周期保持一致，删除为逻辑删除，停用可恢复，已删除标识不重新分配，历史样本和回执保留。浏览器对字面 `.` 与 `..` 按现有设备登记合同处理路径编码。
4. 无需给登记来源配置机器 producer、Token、设备、表计、采样组或指标授权。管理员仍按现有系统方式维护表计、用户表计读取范围以及表计指标配置。目标表计须存在于当前表计配置，发送的指标须在该表计／采样组中配置并启用。
5. 登记管理、表计配置、样本和统计页面沿用现有登录与权限检查，Web 请求使用用户 Bearer。新增机器 POST 完全省略 `Authorization` 即可调用，服务端只按本合同检查登记及数据；即使请求携带该头也不以其作为身份或改变处理结果。读 API 沿用登录与表计范围合同。无 Token 能耗 GET 为独立需求。
6. `sourceKey` 是登记标识。无 Token 入口按已确定的受控内网接入方式使用。当前登记、设备／过程机器路由和既有能耗 Bearer v2 合同与权限继续可用。

## 3. 登记管理 API

路径相对于 `/api/v1`。接口使用登录用户 Bearer 和现有管理员检查，返回项目标准 `{code, message, data}`。名称、启停和路径规则与[现有设备来源登记](../../contracts/published/http-api/observation-write-sources-v1/README.zh-CN.md#登记管理)一致。

| 方法和路径 | 行为 |
| --- | --- |
| `GET /energy/write-sources` | 列出未删除的能耗登记，含停用项。返回 `sourceKey`、`name`、`enabled`、`createdAt`、`updatedAt`。 |
| `POST /energy/write-sources` | 提交 `sourceKey`、可选 `name`、可选 `enabled` 并返回记录。 |
| `PATCH /energy/write-sources/{sourceKey}` | 更新 `name` 和／或 `enabled`，标识不变。 |
| `DELETE /energy/write-sources/{sourceKey}` | 停止写入并隐藏登记，返回 `{sourceKey, deleted: true}`。重复使用已删除标识被拒绝。 |

未登录或令牌无效返回 401，非管理员返回 403，未知或已删除的登记更新／删除返回 404，重复或冲突标识返回 409，输入不合法返回 422。日期字段以 `+08:00` 输出。登记 API 不读或写设备／过程来源表。

## 4. 机器写入合同

### 4.1 请求

`POST /api/v1/integration/energy/registered-samples` 接收 UTF-8 `application/json`。请求不含 Authorization 也可提交。沿用现有观测入口的 65,536 字节限制、JSON 解析和响应信封。外层字段为 `sourceKey`、`target`、`observedAt`、`items`，`target` 为 `energy`。

`observedAt` 是这一包各项共同的实际采集时间，须携带时区偏移并可无损保存到微秒，服务端规范为上海时间。若不同表计的真实采集时间不同，调用方按实际时间分包。时段区间可按每个采样组分别提供。一次请求示例：

```json
{
  "sourceKey": "energy-line-01",
  "target": "energy",
  "observedAt": "2026-11-24T12:00:00+08:00",
  "items": {
    "meter-01": {
      "electricity": {
        "quality": "good",
        "intervalStartAt": "2026-11-24T11:00:00+08:00",
        "intervalEndAt": "2026-11-24T12:00:00+08:00",
        "values": { "intervalEnergy": 120 }
      }
    },
    "meter-02": {
      "electricity": {
        "quality": "good",
        "values": { "totalEnergy": 9820, "activePower": 21.3 }
      }
    }
  }
}
```

- `items` 的第一级键为 `meterId`，第二级键为 `groupKey`。每个表计／采样组包含非空 `values`，其中键为已配置启用的指标键，值为可按现有能耗数值合同无损保存的有限 JSON 数字，数值 0 有效。
- `quality` 可省略或为 `null`，保存为 `unknown`。显式值为 `good`、`bad` 或 `unknown`。统计沿用原有质量规则，调用方明确知道数据正常时可发送 `good`。
- 一个组包含时段增量指标时，该组必须同时提交真实的 `intervalStartAt` 和 `intervalEndAt`，均带偏移且开始早于结束。纯累计或瞬时指标的组省略这两个字段。同组可包含累计、瞬时和增量指标，其区间只用于有区间语义的统计。各表、各组的区间可不同。
- 表计、采样组和指标键使用现有配置值。单位、计量方式和槽位从现有指标配置读取，不要求发送方重复填写。当前合同不引入 `taskNo` 或调用方 `eventId`。不按采集年龄、预设能源类型、来源到表计关系等增设校验。

### 4.2 响应与错误

成功响应为 HTTP 200；下例中每个表计／组对应一条样本，`receiptId` 与 `recordId` 为字符串：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "sourceKey": "energy-line-01",
    "target": "energy",
    "observedAt": "2026-11-24T12:00:00.000000+08:00",
    "outcome": "stored",
    "receiptId": "7001",
    "records": [
      { "meterId": "meter-01", "groupKey": "electricity", "recordId": "1048" },
      { "meterId": "meter-02", "groupKey": "electricity", "recordId": "1049" }
    ]
  }
}
```

`records` 按表计键、组键的 UTF-8 顺序稳定输出。重放返回原响应中的回执与记录 ID。未知、停用或已删除来源返回 403 `equipment_observation.source_not_enabled`；同一身份不同正文返回 409 `equipment_observation.event_conflict`；表计／组／指标不存在或未启用、数值／时间／质量不合法返回 422，响应使用现有稳定错误信封并指明类别；非 JSON 介质为 415，超过现有请求大小上限为 413，数据库不可用或提交结果未知为 503。对 503 使用原包重试。

## 5. 批次、回执及并发

1. 服务端将 `sourceKey`、固定 `target=energy` 和规范化 `observedAt` 组成批次身份。规范正文使用原有精确 JSON 规范化，键顺序不影响结果；时间统一为 `+08:00`、微秒，`quality` 省略／null 与 `unknown` 等价，数值等价表示规范后比较。
2. 锁定来源后先检查是否已启用，再查该身份已有回执。相同规范正文直接返回原回执，即使原指标配置后来停用。身份相同而正文不同返回 409。未见过的时间可乱序追加，不以服务端接收时间替代事实时间。
3. 新包一次验证所有表计、组、指标、质量、数值和区间。在一个事务中写一份能耗批次回执和每个表计／组一行 `energy_consumption_main`，所有样本引用该回执；回执的 `result_detail` 保存有序的表计／组／记录 ID 列表。任一项非法或写入异常，整包无半成品。
4. 并发重复、不同正文竞争、提交结果未知和登记停用／删除与写入竞争须保持同一结果。已提交的包保留；停用或删除之后的新请求和重试均按当前来源状态拒绝。并发情况下要么原包已完整提交，要么没有提交。请求失败后再次使用相同原包可确认结果。
5. 新登记来源使用与现有 v2 生产者隔离的内部身份和合同版本，不能与历史或未来合法 v2 producer／event 静默混用。登记创建、v2 写入及配置更改之间的身份冲突和并发必须保护已有回执与数据。旧 v2 事件、响应、重放、权限及历史记录保持既有合同。

## 6. 数据结构与运行兼容

新增 `energy_write_sources` 能耗登记表，至少包含大小写敏感且唯一的 `source_key`、与旧生产者隔离的稳定内部身份、可选名称、启用状态、创建／更新／删除时间。内部标识不暴露在普通页面或机器响应中。同源重放依据能耗回执事务内的唯一身份和规范正文摘要实现。

沿用 `energy_metric_configs`、`energy_consumption_main`、`energy_ingest_receipts` 和现有价格表。为一包多条样本复用能耗回执的 JSON 结果字段，不覆盖旧 v2 回执字段及语义。新增表和必要约束通过显式 Alembic 后继创建；迁移前保留并比对已有登记、能耗及设备／过程记录。迁移和回退方案须保护后继写入的数据及回执。

**能耗运行兼容。** 当前源码中能耗读、配置和旧写入口仍调用 `probe_target`，把全库 revision 白名单和设备来源登记表结构作为日常条件。本任务将能耗日常读、管理、旧 v2 和新登记写入按根契约 §3 调整为基于已配置数据库与实际业务依赖运行，使用项目已有上海时间工具。无关迁移推进 revision 时，只要能耗实际结构兼容，用户无需更新 profile 的 revision；不对每次请求增加统一结构扫描。数据库不可用或实际业务结构错误仍返回清晰失败，能耗的机器权限、用户表计范围和读写合同继续生效。显式迁移／采用操作可以验证具体目标及 revision。[当前 guard](../../backend/app/equipment_observation/services/guard.py)

## 7. 实施边界

- `backend/app/equipment_observation/` 内与能耗登记、POST、模型、事务、现有能耗日常运行兼容、路由／schema／OpenAPI 和必要错误处理直接相关的文件；只为保护共享源或旧能耗 v2 的身份碰撞与兼容而调整共用路径。不得改变实时／过程语义。
- `backend/alembic/versions/` 增加本任务专用后继，`backend/tests/` 和 `backend/tests_mysql/` 的对应聚焦测试；不改历史 migration。实际 head 在实施时核对，防止与并行迁移冲突。
- `frontend-js/src/app/energy/` 下管理员配置页面、登记表组件、API 和中英文 locale，以及 `frontend-js/tests/module-registry/` 的对应测试；复用公共按钮、表格、列宽与弹窗。与能耗空态跟进任务的并行改动须协调，不覆盖对方成果。
- `contracts/published/http-api/energy-registered-ingest-v1/` 的中英文合同、OpenAPI 和合成请求／响应向量，`contracts/README.*`、`backend/app/equipment_observation/README.*`、`docs/equipment-status-process-monitoring{,-guide}.*` 及必要的前端 README 仅同步本合同和使用入口。实际结构变化按项目规则更新 `CODE_INDEX.md`。协调者维护根 PLAN／目录索引。
- 明确复用 `backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`，验证按对应工具链执行。Deviation、额外表或新增授权规则须返回 PM 修订。

本任务不开发 SMA、DAA 或第三方客户端，不处理自定义单价、费用计算、设备／过程与能耗业务关联或新增无 Token 读取。生产、dev 数据库迁移与服务切换按项目契约另行授权。

## 8. 验收

| ID | 验收结果 |
| --- | --- |
| AC01 登记页面与权限 | 管理员通过用户 Bearer 增删改查、启停能耗来源，只有标识、可选名称、启用项；普通用户无法管理。删除保留样本，已删键不能重用。中英文、列宽、键盘、PC／平板明暗主题、遮罩取消均通过。 |
| AC02 一包多表 | 不携带 Authorization，提交 §4 两表样例，返回一个回执和两个可读取的能耗记录。使用原表计／组／指标配置和用户 Bearer 在数据管理、统计查询核对 120 kWh、累计值及 0，时间和组归属正确。 |
| AC03 质量与校验 | 空值、未知／禁用指标、无效来源、非法数字及错误区间按合同拒绝，数据库没有任何该包的样本和回执。省略质量保存 unknown，good／bad／unknown 的统计沿用现有规则；相同包不同组可有不同真实区间。 |
| AC04 幂等与事务 | 同身份同正文、不同键顺序及等价时间／数值重放同一回执。不同正文、同刻分包返回 409，无静默合并。测试并发相同与冲突包、数据库中途故障、提交未知后重试，证明一份回执及所有样本一起提交或一起回滚。 |
| AC05 停用与碰撞 | 测试 POST 与停用／删除并发及恢复，确认无半写入。用与历史 v2 producer／event 冲突的构造夹具及并发检查身份隔离，旧数据不被占用或重放为新包。 |
| AC06 兼容 | 含旧能耗样本、回执和配置的隔离库升级后逐项比较旧行，旧 v2 Bearer POST、发现 API、用户表计范围、样本及 summary 的路径／权限／响应／去重有效。设备和过程既有路由、数据、来源及回执按原合同通过回归。 |
| AC07 后继迁移 | 隔离库在本任务结构创建后再执行与能耗无关的后继迁移，既有 profile 不改 revision，能耗读、管理、新 POST 与旧 v2 POST 仍可用。数据库实际缺表或不可达时返回失败。禁止用全库 revision 或设备来源表存在性作为能耗运行 gate。 |
| AC08 工程与边界 | 运行项目声明的 uv/pnpm 聚焦测试、模块注册／编译构建、OpenAPI 示例和文档链接检查；真实后端依赖与浏览器使用隔离合成数据。确认机器 POST 无需 Token，所有管理员及用户读写要求 Bearer；无跨域外键、JOIN 或任务号依赖。 |

## 9. 风险和回退

同一来源同一时刻只能有一个包是本稿明确的重试边界。统计结果依赖发送方真实时间、质量和指标配置，未知质量或区间缺口按既有统计结果显示。申请停用／删除与写入并发时以事务先后为准。客户端出现 503 后保留原始包重试，避免人为改时间造成重复样本。

回退前区分本次新样本与旧 v2 数据。已写入的样本与回执需要保留、可追溯；不通过删除数据达到回退。真实目标的迁移、备份、服务切换和恢复操作另行确定。

## 10. 修订与交接

| 日期 | 记录 |
| --- | --- |
| 2026-11-24 | Human Owner 确认原型并授权按 STD 起草规格。 |
| 2026-11-24（Asia/Shanghai） | Human Owner 原话：“验收 ARCH-OBS-009 r1。批准 ARCH-OBS-010 r1，按 STD 启动 Development。” 据此批准本任务精确 r1。 |

Human Owner 已批准 r1。Development 按精确范围实施并记录自检，再交 fresh-context Verification；QA 通过后由 Human Owner 最终验收。
