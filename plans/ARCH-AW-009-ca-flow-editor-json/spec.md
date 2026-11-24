Task ID: ARCH-AW-009
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-AW-009 r2 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 现有 CA 的 Vue Flow 编辑、版本化流程 JSON、PLC 点表导入与单节点测试
Owner: Automation World / Control Agent
Acceptance Chain Reference: 本文第 10 节及 Development Lifecycle Workflow
Related Task: ARCH-AW-006 r2; ARCH-AW-007 r2; ARCH-PLC-001 r8; field-flow::FF-004 r2 A

# ARCH-AW-009 r2：在现有 CA 中实现流程编辑与单节点能力（范围已批准）

## 1. 修订目的、当前事实与批准状态

Human Owner 要求按前次讨论修订 r2：直接在现有 `automation-world/control-agent/` 内建设真实 Vue Flow 编辑器，能拖入、移动、连线、删除和撤销；流程 JSON 能导出再导入，浅色模式可读；兼容 DAA/DS 导出的 PLC JSON；实现 HTTP GET、POST 和 PLC 单点读取的单节点功能。本轮先看设计，不修改代码，也不进行实际联调。

**Human Owner 已精确批准本 r2 的实施范围，见第 11 节。** r1 仍为历史草案；本次批准来自对 r2 的明确决定，不是推断自以往架构方向。本文的 API、文件路径、界面与验收是待实施合同，不是已经存在的功能；最终状态分别以 Development 事实、独立 Verification 和 Human Owner 决定为准。

[现有 CA](../../automation-world/control-agent/README.zh-CN.md)是旧兼容工程，其已有配置、数据、启动方式与旧代码需要保护；此次在同一正式工程内新增编辑器，不新建独立 `ca-flow-editor` 项目。当前源码的旧桌面启动可依据环境触发 PLC 采集，新编辑器启动不得触发它。当前工作树未发现已跟踪的 CA `src-tauri/tauri.conf.json`、`vite.config.ts` 与 `tsconfig.json`；后续应先核对现状，必要时在本任务范围补齐，使约定的 `pnpm tauri dev` 真正启动交付树，而不是以原型或其他副本代替。

[点位交换设计](../../automation-world/plans/ARCH-PLC-001-shared-plc-point-json/spec.md) r8 保留 r7/r5 的 `aiis.plc_points` v1 设计；其历史各端 QA 和未验证边界不因本文改变。[FF 当前 YAML v2](../../field-flow/README.zh-CN.md) 与固定示例并非通用 `aiis.flow` 执行器。CA 可先交付自己的编辑、JSON 和模拟/单节点能力，FF 是否接收和执行须由 FF 所有者的独立任务确定。

## 2. 系统原理与本期范围

```text
DAA / DS 已导出的每 PLC 一份 JSON                 HTTP 连接配置（本机）
          │                                               │
          ▼                                               │
    只读解析 / 预览 ──用户确认──> CA 逻辑 PLC / 点位目录 │
          │                         │                     │
          │                    显式本机目标绑定 ◄─────────┘
          ▼                         │
  流程管理 → Vue Flow 画布 → 图和引用校验 → 保存有效版本 / 导出 aiis.flow JSON
                  │                                      │
                  └──选一个节点→模拟测试 / 显式真实测试    └→ 未来 FF 独立实现读取和执行
                                 仅该节点、无下游              FF 通过前保持 pending
```

1. 有工作台入口、流程列表、新建/打开/版本、Vue Flow 编辑界面、PLC 与点位、HTTP 连接和测试结果。工作台可查看已保存流程和版本；整流启动、调度、执行进度与运行日志为明确标注“未支持”的入口/空状态，不能模拟成正在执行。测试记录仅属于单节点测试。
2. 可保存合格图的不可变 revision、选择打开旧版、导出和重新导入；不合格图保留编辑状态但不得保存为有效版本或导出。单节点测试不要求整图完成。
3. 使用真正的 Vue Flow 图画布和本地锁定依赖，不使用截图、CDN 模拟或手工 HTML 假画布。本草案选 [Vue Flow `@vue-flow/core` 1.48.2](https://www.npmjs.com/package/@vue-flow/core)；与现有 Vue/Tauri 不兼容时停止并回 PM，不随意改合同。
4. 首版实现可调用的 Rust HTTP GET、HTTP POST、S7 DB 单点读取路径，并接到 UI 的单节点测试。默认模拟；真实调用需用户明确选择、核对并确认单节点目标与副作用。实际 HTTP、回环 HTTP、S7 模拟器、真实 PLC 和生产环境联调均不在本 revision 的 Development/QA 验证授权中；可用隔离假 transport、纯内存测试和合成文件证明逻辑与接线，不能据此声称真实通信成功。
5. 无应用登录认证。禁止真实 PLC 写入；PLC 写节点可配置和模拟，真实执行未支持。无整图运行器、定时执行、批量采集、自定义代码节点或现场命令。DAA 继续承担大规模采集，SMA 独立；此版本不实现替代它们。

## 3. 现有入口和数据保护

- 普通 `cd automation-world/control-agent && pnpm tauri dev` 进入**新编辑器模式**，默认不启动旧采集或任务、不连接 PLC/HTTP、不读取旧 `.env` 以执行任务，也不自动扫描、迁移或重写 CA/DAA/SMA/FF 的既有 profile、数据库、历史和配置。界面无登录。模拟和真实测试必须在界面明确区分。
- 保留旧桌面与 headless/CLI 逻辑及语义；建议显式桌面参数 `--ca-legacy-console` 进入旧兼容模式，只有该模式按原有旧配置与自启动规则执行。已有 `--ca-collect-plc-snapshots-once`、`--ca-collect-plc-snapshots-loop`、`--ca-smoke-plc-collection-loop` 和独立 runtime 入口保持原有含义，不偷偷重定向到新编辑器，也不在验证时实际连接。旧模式仍属兼容用途，不把新模式的默认禁自动启动虚报为旧模式行为已改变。
- 新编辑器的流程、资源、模拟结果和需持久化的未知结果放 CA 应用数据下新命名空间 `flow-editor-v1`；写入按原子方式完成，失败不覆盖旧版；不改变应用已有身份、旧目录或旧数据。测试使用专属合成数据、明确的临时目录与假 transport；不得借用、修改用户真实 profile。此项是同一应用内的数据边界，不要求另建源码隔离工作树。
- 开发前核实工作树、启动脚本、Cargo features、原有未提交改动和旧配置触发点；实现后验证新旧入口路由和无意 I/O。旧功能如无法在不改变既有语义的前提下保留，应停下交回 PM，不能通过删除功能或调整用户环境“解决”。

## 4. 界面与交互

```text
┌ CA ────────────────────────────────────────── 工作台 / 流程管理 / PLC 与点位 / HTTP 连接 / 测试记录 ┐
│ 流程管理 / 设备状态检查                                      [校验] [撤销] [导入] [导出] [保存] │
├────────────────┬─────────────────────────────────────────┬────────────────────────────────────┤
│ 节点库         │ 真实 Vue Flow 画布                       │ 节点：PLC 单点读取                 │
│  PLC 单点读取  │  [读取 status] → [status == 1?]         │ PLC：[选择逻辑 PLC] 点：[选择点]   │
│  类型化条件    │                         ├真→ [HTTP GET] │ 字段：[上游输出选择器]             │
│  HTTP GET/POST │                         │       ↓       │ [参数] [测试此节点] [删除节点]    │
│  PLC 写(模拟)  │                         │    [结束]     │ 测试模式：模拟 / 真实              │
│  结束本轮      │                         └假→ [结束]     │ 目标、输入、输出、耗时与错误     │
└────────────────┴─────────────────────────────────────────┴────────────────────────────────────┘
```

- 用户以鼠标从节点库**拖入画布**、拖动已添加节点，用源输出把手拖到目标输入把手形成连线；能选中并删除节点或单条边，选中节点有明确删除按钮，也支持键盘删除。删除节点同时移除关联边；撤销一次应恢复该次删除及其相关连接和参数，移动/新增/连线/删除均能撤销，撤销不能篡改已保存 revision。无效连接即时提示；最终仍须整体校验。
- 参数区展示当前节点名和稳定 ID、目标资源、类型与输出。输入可选择常量或可达上游节点字段，字段选择器展示节点名/ID、字段及类型；条件比较为类型化配置，不要求用户写表达式或手填 JSON。没有合适上游字段时提示原因。
- 列表显示流程名、ID、修订版本和校验状态；已保存版本可重新打开、另存新 revision、导出。画布、参数/测试区应在 PC `1440×900` 和平板横屏 `1024×768` CSS 像素可操作，侧栏/面板可折叠或滚动而不遮住关键操作。浅/深色与中英配套；标题、按钮、选中/禁用状态、报错和 JSON 在背景上清楚可读，不出现白字叠浅底。长 JSON 可滚动和复制。
- 「测试此节点」有参数、手填/选用已保存的模拟上游输入、运行前目标预览、结果区。若所需输入为空/类型错误，定位错误并禁止执行；不运行上游和下游。编辑未完成也能模拟单个节点。切换真实调用须在调用前显示目标、方法/点位、输入摘要和可能副作用，明确确认并显示真实 I/O 标签；切换回模拟不得沿用真实成功状态。

## 5. 流程 JSON、语义与校验

### 5.1 合同

候选合同位于 `contracts/demands/ca-field-flow-v1/`，格式 `aiis.flow`、整数 `schema_version: 1`，包含执行语义 `flow` 和可选 `layout`。结构与 JSON Schema、语义规则、标准化摘要、节点实现版本和正反例向量一起维护；属于 CA 候选合同，尚未声明 FF 已接受。

`flow` 包含稳定 `flow_id`、不可变 `revision`、周期 `trigger`（正整数 `interval_ms`）、`entry_node_id`、`nodes`、`edges`；节点含稳定 ID、type、version、类型化 config。边以源 node ID、具名输出端口和目标 node ID 表达。字段引用如 `{ "node_id": "read_status", "field": "value" }`，常量如 `{ "type": "int16", "value": 1 }`。`layout` 以节点 ID 保存坐标/画布信息，缺失时自动布局；布局不参与执行语义、不能影响顺序。新增、编辑或布局变更后显式保存生成新 revision，旧版本不可静默覆盖。导出和再次导入保留节点 ID、边、引用、节点参数、条件分支及原有坐标；无 layout 同样可导入再编辑。记录完整文件 SHA-256 和不含布局、展示标签、revision 的规范化执行语义摘要，各自用途不混淆。

v1 仅表达单入口 DAG：首版节点为 S7 单点读取、类型化 `eq` 条件、HTTP GET/POST、PLC 写（仅配置/模拟）、结束；周期触发属于流程而非图节点。普通节点一个成功出口，条件有 `true`/`false` 两个具名出口，结束无出口。定时按单轮结束后等待间隔、同一流不重入、不追赶漏掉的 tick 的语义记录；本期不执行此调度。图内循环、并行汇合、同轮无限等待以及重读节点均为后续范围。

保存和导出共用最终校验：版本/节点版本、唯一 ID 和入口、端口类型/数量、无悬空边、所有节点可达、所有分支终止、无环、必要配置、字段在对应路径已执行且存在、引用和常量类型匹配、逻辑资源引用有效。条件严格区分 `int16` 的 `1` 与字符串 `"1"`、`true`、空值、坏质量和读取错误；不可将错误默认为零或成功。未知 schema/节点版本必须明确拒绝，不能丢失未知语义后冒充成功。校验失败时显示可定位的问题，**导出和保存有效版本禁用**，单节点模拟仍可独立进行。

文件只携带逻辑 PLC/点、逻辑 HTTP 资源及相对 path，不包含主机、端口、rack/slot、凭据、token、真实客户数据、本机绝对路径。目标地址和凭据在当前环境中单独绑定并作敏感遮罩。导入先校验再预览：同 ID/revision 且内容相同可打开既有版本、新建副本或取消；同 ID/revision 但内容不同只可改新 flow ID 另存副本或取消，不能覆盖。导出由用户选定目标，取消/失败不留被当成成功的半文件，不自动覆盖已有文件。

### 5.2 贯穿样例

用户编辑 `status_gate`：周期 1000 ms，读取逻辑 `plc_line_a` 的 `task_status`（`int16`）；`value == 1` 时走 HTTP GET `/status` 再结束，否则直接结束本轮。图语义要求下轮定时触发后重新读取，不在当前轮无限等待。可以从节点输出字段选择 `read_status.value` 给条件或 GET query。CA 导出并导回相同文件后仍能编辑、保存新 revision；后续 FF 另行批准实现后，拿**同一文件**证明两条分支和下一轮重读，再由 CA 导回继续编辑。CA 当前没有完整运行器，不能以本地模拟替代这项 FF 联合证明。


该样例的候选 JSON 结构如下；schema 和向量随实施精确定义，FF 接受前仍属 CA 候选。数值、名称和周期均为合成示例：

```json
{
  "format": "aiis.flow",
  "schema_version": 1,
  "flow": {
    "flow_id": "status_gate",
    "revision": 1,
    "trigger": {"type": "interval", "interval_ms": 1000},
    "entry_node_id": "read_status",
    "nodes": [
      {"id": "read_status", "type": "plc.read", "version": 1, "config": {"plc_ref": "plc_line_a", "point_ref": "task_status", "value_type": "int16"}},
      {"id": "check_status", "type": "condition.compare", "version": 1, "config": {"left": {"node_id": "read_status", "field": "value"}, "op": "eq", "right": {"type": "int16", "value": 1}}},
      {"id": "get_info", "type": "http.request", "version": 1, "config": {"endpoint_ref": "backend_api", "method": "GET", "path": "/status", "query": {"status": {"node_id": "read_status", "field": "value"}}}},
      {"id": "end_true", "type": "end", "version": 1, "config": {"result": "matched"}},
      {"id": "end_false", "type": "end", "version": 1, "config": {"result": "not_matched"}}
    ],
    "edges": [
      {"from_node_id": "read_status", "from_port": "next", "to_node_id": "check_status"},
      {"from_node_id": "check_status", "from_port": "true", "to_node_id": "get_info"},
      {"from_node_id": "get_info", "from_port": "next", "to_node_id": "end_true"},
      {"from_node_id": "check_status", "from_port": "false", "to_node_id": "end_false"}
    ]
  },
  "layout": {"nodes": {"read_status": {"x": 0, "y": 0}, "check_status": {"x": 200, "y": 0}, "get_info": {"x": 400, "y": 0}, "end_true": {"x": 600, "y": 0}, "end_false": {"x": 400, "y": 150}}}
}
```

数值为 1 时期望执行一次 GET 后结束 `matched`；0 或其他有效 `int16` 走 `not_matched`，下一轮重新读。读取失败、缺失、错误类型或坏质量应终止并报告，不走 false 或替换为 0。这些是候选语义，不表示当前 CA 已运行整图。

## 6. 兼容 DAA / DS PLC JSON

以 [ARCH-PLC-001 r8 保留的 r7/r5 合同](../../automation-world/plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 为权威：`format: "aiis.plc_points"`、`schema_version: 1`，一文件一 PLC，兼容 DAA 与 DS 两种真实 producer。按合同校验完整文件和全部 DB/点（包括禁用或未引用点）：UTF-8、重复键、版本和闭合字段、大小/层级/数量、UUID、地址范围、BOOL bit、类型词法、长度和重叠等；字段不满足合同必须定位并拒绝，不得静默丢点、猜地址或修改。并区分 **文件合同无效**、**文件合法但当前运行时不支持该类型/连接布局**：后者完整保留并显示原因，不可强行转换为 INT 或伪造读数。

预览包括 producer、外部 `origin`、PLC/DB/点 ID、DB 号、byte/bit、原类型、source path、原有双语/描述、源启用状态、连接信息及全部点数量。DAA 允许 DB 层缺省 `source_enabled`，DS 按其合同输出该层；点启用状态按导出方实际含义显示，不赋予采集、写入、连接权限。对非默认 TSAP 等运行时不支持的合法配置，导入时明确标示不可执行；不得改成默认值冒充兼容。首版至少支持执行标准 DB `INT` 的单点读取；`BOOL`、`REAL` 及其他合同合法类型是否可执行以实现后的明确类型矩阵为准，未支持者可导入但禁止真实读取，单独提示；不因导入成功而声称整张点表可执行。

来源连接地址仅是文件携带的**来源信息**，导入预览或确认不连接、不采集、不上报。用户须在 CA 显式建立/确认目标绑定后才能选择真实测试；导出流程 JSON 仍只引用逻辑 ID。导入前保留原始文件字节和独立文件 SHA；文件内 `export.payload_sha256` 是来源 payload 摘要，不等同整文件 SHA。以外部 origin + 外部 DB/点 ID 标识来源，建立并持久化本机资源 ID 映射。相同文件再次导入可识别既有来源并打开或取消，不复制身份；同源但内容改变先列差异、禁止静默覆盖，用户可明确选择作为新本机资源导入，保留新的外部到本机映射并要求流程重新绑定；既有资源和已保存版本不变。预览/取消不写入；确认时重验文件内容与目标状态，冲突或失败不得留下半套目录。不同来源不可仅按名字合并。

验收需各一份由 DAA、DS **既有真实导出实现**针对合成配置离线产生、或来自可核验原导出来源且非敏感的原样文件；记录导出方版本/来源、原文件 SHA，并作为文件输入分别经 CA 实际解析、预览、确认、重开和重复导入验证。只检查文件和 CA 本地行为，不连接 DAA、DS、PLC 或 HTTP；不得以手写近似 JSON 冒充两端原导出文件，不改 DAA/DS 导出器。若不能安全取得可核验源文件则记录阻塞，不虚报兼容通过。

## 7. 单节点测试和真实实现边界

| 操作 | 行为与边界 |
| --- | --- |
| 编辑预览 | 只校验节点配置、引用和模拟值，不调用 HTTP/PLC。 |
| 模拟单节点 | 手填或选取先前保存的模拟上游字段，类型校验后只演算本节点；结果标“模拟”，不触发上下游。 |
| 真实单节点 | UI 需单独选择、预览目标与副作用并明确确认；仅发起所选节点的一个调用，不自动遍历图、不自动重试 POST。此 revision 实现可调用路径，但本次不执行真实或本机联调。 |
| 整流测试/运行 | 后续任务定义；当前入口不可执行且标明未支持，绝不把单节点测试标为整流成功。 |

HTTP GET/POST 的 Rust 实现必须实际构造并可调用请求，包括已绑定的 HTTP(S) 目标、相对路径、query、必要 headers、POST body、类型化常量/上游输入、超时及响应状态/结果；绝不是仅返回模拟数据的占位。相对 path 不得改变已确认的 scheme/host/port；默认禁止自动跟随重定向，返回可见原因。测试使用注入的假 transport 验证实际命令调用服务、请求构造、响应和错误处理，不发网络包。请求参数与日志中敏感头/凭据遮罩，真实调用与模拟结果在 UI/记录中可区分；收到 HTTP 响应只证明响应，不代表客户业务完成。

S7 单点读 Rust 路径解析并校验用户已绑定的 PLC、DB、byte/bit、类型和超时，调用既有可复用的 S7 adapter/driver 或同等可编译真实实现并解码；开发测试注入假 adapter 验证地址、类型、错误、值与质量，不建立 S7 连接。现有旧 reader 为每次读取建连并断连，不能宣称已提供跨节点持久连接池；本期单节点能力无定时采集和会话复用承诺，后续 CA 常驻采集及共享连接需独立设计和验证。`pnpm tauri dev` 的 Tauri 配置应提供所需 `rust-snap7-driver` feature，无需用户手工指定 feature；不可在无 driver 时假成功。

POST 发送前记录动作 ID 与目标摘要；若已发送或可能已发送而结果无法确认，标为 `unknown` 并保留，进程重启后仍可看到并供用户核实，绝不自动重发；明确发送前失败与收到响应要区分。模拟的 unknown 仅证明分类和保存逻辑，不声称现场写入、业务幂等或真实故障恢复已验证。PLC 写只可模拟；不提供真实 PLC 写命令。

每次测试展示节点/版本、模式、资源、解析后目标、输入摘要、输出或错误、开始时间、耗时和是否实际 I/O；失败、超时、取消以及前置校验不满足均有可见状态。所有真实执行仅由用户显式操作触发；本次 Development、Verification 只使用假 transport/合成文件，无回环或真实 I/O。

## 8. 接口、文件和职责

### 8.1 CA UI ↔ Tauri/Rust 本地 IPC 候选矩阵

| IPC 命令 | 请求 / 响应摘要 | 副作用 |
| --- | --- | --- |
| `ca_flow_validate` | 草稿图 → 结构/语义问题和节点定位 | 纯校验 |
| `ca_flow_list` / `ca_flow_get` | 筛选或 ID/revision → 已保存版本及 layout | 只读新命名空间 |
| `ca_flow_save` | 有效图、预期版本 → 新不可变 revision / 冲突 | 原子保存；无整流执行 |
| `ca_flow_import` / `ca_flow_export` | 用户选定文件、冲突选择 → 预览/导入结果或导出结果 | 用户明确文件操作；导出先最终校验 |
| `ca_plc_catalog_preview` / `ca_plc_catalog_commit` | 用户选定源文件 → 原信息/校验/差异，确认 token → 本机映射 | 预览只读；确认原子写新 CA 目录，不连接 |
| `ca_resource_list` / `ca_resource_save_binding` | 逻辑 PLC、点和 HTTP 资源 → 列表；显式目标绑定 → 结果 | 仅存 CA 绑定；不主动连接，敏感值遮罩 |
| `ca_node_test_preview` / `ca_node_test_run` | 单节点、模式、模拟输入 → 解析/副作用预览；明确确认 → 一次测试结果 | 默认模拟；真实 GET/POST/S7 read 只在用户显式确认后有 I/O；不触发下游 |
| `ca_node_test_list` / `ca_node_test_get` | 测试/动作 ID → 已保存结果、状态、`unknown` | 只读测试结果，不重发 |

IPC 是本应用内部接口，名称可由 Development 与实现映射但不得少于上述能力或改变其行为；文件访问需用户选择且受 Tauri capability 约束，不开放前端任意文件系统或地址读写。无新增 backend HTTP API，CA 调用的 GET/POST 由用户配置为外部接口，不能声称具体客户 API 已存在。先绑定逻辑资源、请求路径、输入和目标，再允许测试；不自动读取 DAA 内部数据库。

### 8.2 后续实施精确 allowlist

此表是 Human Owner 已精确批准的 **r2 实施允许改动范围**；记录批准时尚未开始实施。各目录通配只限下述职责；增加无关文件、能力、已有数据或任务外配置需先回 PM。

| 相对仓库根目录 | 可写内容及限制 |
| --- | --- |
| `automation-world/control-agent/package.json`, `pnpm-lock.yaml` | Vue Flow、实现所需直接依赖与受锁工具链；不动其他应用依赖。 |
| `automation-world/control-agent/{vite.config.ts,tsconfig.json,tsconfig.node.json}`、`src-tauri/tauri.conf.json` | 必要时新建/补齐现有 CA 常规启动、TS 构建、资源别名和 Tauri feature 配置；遵守现有应用身份与端口，不导入客户配置。 |
| `automation-world/control-agent/{src/App.vue,src/main.ts,src/env.d.ts,src/console/sections.ts,src/console/types.ts,src/console/composables/useControlAgentConsole.ts,src/console/composables/useAgentLocale.ts,src/console/composables/useAgentTheme.ts,src/layouts/AgentLayout.vue,src/components/shell/AgentSidebar.vue,src/components/shell/AgentTopbar.vue,src/components/shell/RuntimeStatusCapsule.vue,src/styles/app.css,src/styles/theme.css}` | 仅路由/壳层接入新模式及主题适配；保护旧模式。 |
| `automation-world/control-agent/src/app/{flow-editor,plc-catalog,http-connections,node-tests}/**`、`src/services/{caFlow.ts,caResources.ts,caNodeTest.ts}`、`src/locales/index.ts`、`src/locales/{en-US,zh-CN}/{common,navigation}.json` | 新 CA 界面、Vue Flow 集成、节点/目录/单点测试、对称 i18n；不改旧业务模块。 |
| `automation-world/control-agent/src-tauri/{Cargo.toml,Cargo.lock,capabilities/default.json,src/lib.rs,src/main.rs,src/domain/mod.rs,src/services/mod.rs,src/infrastructure/mod.rs,src/commands/mod.rs}` | 仅依赖、驱动 feature、明确新旧启动分派、模块注册及最小 capability；保留旧收集和旧命令行为。 |
| `automation-world/control-agent/src-tauri/src/{domain,services,infrastructure,commands}/ca_*.rs` | 仅新增 CA 流程、目录、资源绑定、文件原子存储、节点测试及 HTTP/S7 适配；复用旧只读 driver 时不改旧采集业务。 |
| `automation-world/control-agent/{tests/arch-aw-009/**,src-tauri/tests/arch_aw009/**,src-tauri/tests/fixtures/arch-aw-009/**}` | 用户交互/合同/假 transport 测试、经证实的无敏感真实导出文件及合成向量；无用户 profile、地址、密钥或设备记录。 |
| `automation-world/control-agent/{README.md,README.zh-CN.md,PLAN.md,PLAN.zh-CN.md,CODE_INDEX.md}`、`automation-world/control-agent/src/app/{README.md,README.zh-CN.md}` | 只记录新旧入口、能力和实际限制及必需索引；双语长期文档同步，不改写历史事实。 |
| `contracts/demands/ca-field-flow-v1/{README.md,README.zh-CN.md,schema.json,vectors.json,examples/**}`、`contracts/{README.md,README.zh-CN.md}` | 候选流程合同、示例/向量和候选索引；FF 未接受前不标 provider accepted。 |
| `automation-world/{README.md,README.zh-CN.md,PLAN.md,PLAN.zh-CN.md}`、`{PLAN.md,PLAN.zh-CN.md,plans/README.md,plans/README.zh-CN.md}`、`automation-world/plans/{README.md,README.zh-CN.md}` | 仅主协调按实际阶段机械更新本任务/现有 CA 入口事实，保留并发改动，不重写历史。 |
| `plans/ARCH-AW-009-ca-flow-editor-json/tasks.md`、`checklist.md` | 批准后分别由 Development 和 fresh-context Verification 创建/维护；不由 PM 代写。 |

不修改 DAA、DS、SMA、FF、backend 源码/配置或其他共享组件；如实际需要修改共享 `console-ui`、驱动现有实现、`build.rs`、其他文件或授权新的能力，停止并请 PM 修订。允许必要的本任务新文件头和索引；最终测试必须针对正式交付树。不新增客户真实信息、依赖外网 CDN、发布、部署或现场连接。

## 9. 可复现实施顺序与验收

实施顺序：① 保护现有数据、明确启动模式并完成基本构建；② 设计目录/流程合同及存储、两种原导出文件导入；③ 接 Vue Flow 编辑器、布局和整图验证；④ 实现 Rust 节点调用与假 transport 测试和 UI 测试；⑤ 正式 CA 入口做真实画布人机验收并更新有限文档。步骤中只使用合成数据，不运行实际联调；任何超出范围或无法保护旧数据的情况回 PM。

| 编号 | 可独立观察的验收标准 |
| --- | --- |
| AC01 | 在正式 `automation-world/control-agent` 通过普通 `pnpm tauri dev` 启动新界面，Tauri 构建包含 S7 feature；空的合成新命名空间和旧环境配置并存时，新入口不触发旧自动采集、外网、旧数据库、外部数据库或 PLC；显式旧模式与旧 CLI 分派用不产生 I/O 的测试证明保留语义。记录入口、profile 身份和测试限制。 |
| AC02 | 在实际运行的 CA Tauri/WebView 中，以鼠标从库拖节点入画布、移动、从输出把手拖线到输入把手；可选边删除；可用按钮及键盘删除节点并连带删除边；撤销恢复节点、参数和边，新增/移动/连线可撤销。提供真实交互记录，不以静态截图、模拟 DOM 或假画布代替。 |
| AC03 | 编辑不完整图可做单节点模拟，但保存有效版本和导出禁用；悬空边、不可达节点、环、缺失分支、错误端口、非法引用、类型不符和未知版本分别定位并阻断。严格验证 INT `1` 与字符串、布尔、空值及坏质量不混同。 |
| AC04 | 完成 §5.2 图，保存 revision、导出，再实际导入同一文件，节点 ID、连线端口、引用、配置和布局无损；修改布局只改变新 revision 的完整文件内容，不改语义摘要或旧版；无 layout 自动布局；同 ID/revision 冲突不覆盖。 |
| AC05 | 使用可溯源的 DAA、DS 原导出各一份合成/非敏感 `aiis.plc_points` v1 文件，验证完整预览、确认、重开及再次导入身份不变；列出每份原 SHA/producer/版本。无外部连接、无修改来源软件、无手写 fixture 冒充。 |
| AC06 | PLC 文件覆盖两种 producer 的 `source_enabled` 差异、所有点与禁用点、双语和原身份；损坏结构、未知字段/版本、重复 ID、错误 bit/长度、越界和重叠均拒绝；合法但不支持的类型/TSAP 保留并标不可读。相同源变更、取消、失败及显式新建均不覆盖旧对象/已保存版本。 |
| AC07 | 选择 PLC 单点读取节点和合成 PLC/点，模拟模式可手填样本值；假 adapter 模式核对目标 DB/offset/type 并返回合成 `int16`；界面显示模式、目标、输入、值/质量/耗时或错误，仅此节点，无实际 S7 包。未绑定和不支持类型禁止真实执行。 |
| AC08 | 选择 HTTP GET 节点，以常量和模拟上游字段构造 query；假 transport 证实 Rust 服务收到已解析的目标、方法、编码和超时，界面显示合成响应/错误与耗时，无实际 HTTP 请求、无下游动作。 |
| AC09 | HTTP POST 的真实可调用路径经假 transport 验证 body/headers、成功响应、发送前失败、可能发送后 `unknown`、重启保留及不自动重试；默认模拟、显式真实预览区分副作用，无实际 HTTP 请求或现场下发。PLC 写只能模拟。 |
| AC10 | 在 PC `1440×900` 和平板横屏 `1024×768` 的实际 CA UI，分别检查浅/深色：标题、操作按钮、错误、JSON 预览文字清楚，画布、侧栏、滚动与测试操作可达；中英文对称。保留可复现截图及操作证据。 |
| AC11 | 工作台/列表准确显示已保存流程和版本；整流启动/日志清楚标注未支持；单节点测试不声称上游/下游或整流执行，模拟不冒充真实。 |
| AC12 | UI → Tauri IPC → Rust 服务和假 transport 的连接被验证；`pnpm` 构建、Cargo 针对性测试、合同/链接检查和必要的旧入口无 I/O 回归记录真实命令、退出码、候选源码和局限。不得因不能启动真实 Tauri 或取得来源文件而以 unit 测试代替对应 AC。 |
| AC13 | FF 联合 gate 独立 `pending`：CA 导出同一份文件 → 经 FF 独立批准后的 Rust FF 读取并验证两个条件分支和下一轮重读 → CA 再导入继续编辑；以文件 SHA、版本、输入和证据关联。缺任一环节不能标完成，不阻塞 CA 独立验收。 |

## 10. 角色交接、风险和非目标

PM 使用 `aiis`、`project-governance` 明确范围。只有 Human Owner 审阅并**精确批准 ARCH-AW-009 r2** 后，Development 才可按 allowlist 写 `tasks.md` 并实施；涉及 Vue 使用 `frontend-ui`、Tauri 使用 `desktop-tauri`、Rust/driver 使用 `rust-runtime`、PLC 点映射使用 `plc-point-mapping`、可见文案使用 `i18n-workflow`、源码索引使用 `code-document-indexer`。任何范围、数据保护、文件 allowlist 或验收实质变更回 PM 新 revision。Development 给出真实自检后交 fresh-context Verification；Verification 在自身 `checklist.md` 独立核对证据并给出真实 verdict；Human Owner 再决定最终验收。角色约定为 contract-only，不表示平台 ACL 或自动强制路由。

记录本次批准时尚无 `tasks.md`、`checklist.md`、实施、构建、界面运行或真实联调证据；范围批准不等于 Development 完成、QA 或 Human Owner 最终验收。特别保留实际现场目标、真实 HTTP/S7、Windows/其他平台、长期稳定性、FF 消费、生产发布及对客户接口的认证/协议适配均未验证。后续如要实际设备操作、真实发送、部署、迁移历史或更改旧自动运行机制，须另行明确任务边界。样本级兼容与假 transport 不能推出所有 DAA/DS 配置或所有 PLC 可用。


## 11. Human Owner 精确范围批准

2026-11-24（Asia/Shanghai），经主协调转达，Human Owner 明确回复：

> 批准 ARCH-AW-009 r2，按 STD 直接在现有 CA 里实施，做完后交独立验证。真实 Vue Flow 的拖拽、连线、删除撤销、JSON 导入导出和浅色可读性都要实际验收。用 DAA、DS 各一份原导出 JSON 验证兼容，单节点 GET、POST、S7 读功能做出来，用替身验证，实际联调先不做。

本决定精确批准 `ARCH-AW-009 r2` 的实施范围。批准前供审阅的 r2 草案 SHA-256 为 `c382788f167cfff7d41c0007329348965bb9c75750f8b25c3a0d114a051f4fb6`。Development 按本文 allowlist 和验收实施；r1 原始历史不变。

此决定不等于实施完成、独立 QA 或 Human Owner 最终验收，也不授权本文排除的真实 HTTP/S7 联调、真实设备操作、部署或对其他工作流的修改。FF 对候选流程合同的接受及联合 gate 仍独立待定；范围、allowlist 和验收有实质变更时须回 PM 修订并重新批准。

## 附录：r1 完整历史（仅历史，不是当前活动规格）

以下完整保留写前 r1 的 UTF-8 字节，包括结尾换行，其 SHA-256：`66b2b86d659e424c1cdc4aebf85637dd16f4f707601dbe05e6e2586e32354754`。每行添加固定前缀 `r1|`，去除每行这 3 个字节即可精确恢复；历史中的路径、状态和未来时态仅表示 r1 时点，若与 r2 不一致以本次已批准 r2 为准。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~text
r1|Task ID: ARCH-AW-009
r1|Revision: r1
r1|Status: draft
r1|Owner Role: PM
r1|Allowed Writers: PM, Human Owner
r1|Handoff: PM -> Human Owner 审阅并决定是否批准精确 r1 范围；批准前不启动 Development
r1|Workflow Mode: STD
r1|Execution Mode: agent_team_same_session
r1|Task Namespace: aiis-ics-arch
r1|Classification: root
r1|Capability: CA 节点编辑、版本化流程 JSON 与有界单节点测试
r1|Owner: Automation World / Control Agent
r1|Acceptance Chain Reference: 本文第 10 节及 Development Lifecycle Workflow
r1|Related Task: ARCH-AW-006 r2; ARCH-AW-007 r2; field-flow::FF-004 r2 A; field-flow::ARCH-TOOL-001; ARCH-PLC-001 r8
r1|
r1|# CA 节点编辑与流程 JSON 首版
r1|
r1|## 1. 来源、目标与当前状态
r1|
r1|来源为 Human Owner 经 FF 会话转入 CA 会话的请求，来源会话 ID `01a15c7d-1175-7a92-a009-0dc36a2ad53f`。本任务先实现可独立操作的 CA 编辑切片，支持拖放节点、连线、选择上游字段、配置有类型条件、保存、导入和导出版本化流程 JSON；在未完成整条图时可以隔离测试单个 PLC 或 HTTP 节点。整个流程由后续 Rust FF 读取和执行，最终将同一导出文件重新导入 CA 继续编辑。
r1|
r1|本 r1 是 PM 草案，尚未获 Human Owner 精确范围批准。后续角色事实由各自的 `tasks.md`、`checklist.md` 记录。ARCH-AW-006 r2 是已批准的整体方向；ARCH-AW-007 r2 的文档验收不等同于本软件切片的范围批准或验收。首版不设登录认证。
r1|
r1|当前 [CA 基线](../../automation-world/control-agent/README.zh-CN.md)为冻结的旧兼容工程，尚无本任务节点编辑器。Rust FF 的 [YAML v2](../../field-flow/field-flow-rust/config/catalog-demo.yaml)使用逐 PLC 的 `ff.plc` 点位 JSON 和固定 `kind`；[固定示例](../../field-flow/field-flow-rust/src/app/plc_guard_get_int.rs)读取条件为负数后 GET 并可能写入，不是本任务 `status == 1` 的图执行器。FF-004 r2 A 的本地验收不证明 FF 已消费本文流程 JSON。现有 [ARCH-PLC-001](../../automation-world/plans/ARCH-PLC-001-shared-plc-point-json/spec.md)是点位交换合同，保持独立，不与流程 JSON 混用。
r1|
r1|## 2. 本次范围、依赖和阶段验收
r1|
r1|### 2.1 CA 首版软件范围
r1|
r1|1. 提供独立 Tauri / Vue CA 编辑切片，包含流程列表、节点画布及节点参数/校验/测试面板。支持新建、编辑、保存并重开、导入和导出；当前选中的节点可单独测试。
r1|2. 定义 CA 生产、FF 未来消费的 `aiis.flow` v1 便携 JSON、结构 schema、语义规则及脱敏一致性向量。布局与执行语义分离，支持往返编辑。
r1|3. 以单入口有向无环图表达定时触发，覆盖本任务示例的 PLC 单点读、有类型条件、HTTP GET 与结束节点；编辑器提供手动单节点测试。PLC 写、HTTP POST 节点可配置并提供模拟测试，但实际写入不在本期。
r1|4. 编辑预览只校验或使用人工模拟输入。单节点本地联调包含隔离的本机 S7 测试夹具真实单点读和 HTTP 测试夹具真实 GET；可显示目标、输入输出、耗时和错误。
r1|5. 交付双语使用说明、源码索引、配套验证与可复现的 CA 本地证据。
r1|
r1|### 2.2 CA 独立验收与跨端闭环
r1|
r1|CA 的独立验收包括第 7 节 AC01–AC16，能在 FF 尚未提供图消费能力时完成。验证只可声称 CA 产出的文件、回导及本机夹具结果达到本任务要求。
r1|
r1|跨端闭环以本任务导出的**同一份文件**为共同输入，交由 FF 自己的会话及其独立任务批准、实现和验证。完整目标必须同时具备：CA 编辑导出；Rust FF 实际加载该文件并经本地夹具证明 `status == 1` 与不等于 1 的两条路径及下一轮重读；随后 CA 再导入原文件并继续编辑。证据必须关联导出文件 SHA、合同版本、CA/FF 版本、fixture 输入、事件顺序和导回结果。该跨端结果记为本任务关联的联合 gate，缺任何一段时保持 `pending`，不以模拟解释、人工转写、假 FF 消费、另生成的同名文件或独立 CA QA 冒充闭环完成。
r1|
r1|FF 是否接受 `aiis.flow` v1、其精确路径和执行语义以 FF owning task 的批准与实现为准；CA 先输出候选合同和向量，不改 FF 源码或声称消费合同已接受。如 FF 对合同提出实质变更，双方回各自 PM 修订并重新批准对应范围。CA 本地验收通过不自动更改 FF 的任务状态或现场资格。
r1|
r1|## 3. 预计实施 allowlist
r1|
r1|以下是供 Human Owner 审阅的**后续 r1 实施候选范围**，当前只形成本文。本任务采用独立切片，避免覆盖冻结旧 CA。真实地址、凭据、客户文件、数据和运行产物不进入源码。
r1|
r1|| 范围 | 可写内容及用途 |
r1|| --- | --- |
r1|| `automation-world/ca-flow-editor/` | 新独立候选应用。限根部 `package.json`、`pnpm-lock.yaml`、`index.html`、`vite.config.*`、`.gitignore`、`README.md`、`README.zh-CN.md`、`PLAN.md`、`PLAN.zh-CN.md`、`CODE_INDEX.md`，以及 `plans/README.md`、`plans/README.zh-CN.md` 两个模块任务目录索引；`src/**` 的 Vue/JS 页面、编辑器、图验证、字段选择、测试界面、i18n；`src-tauri/{Cargo.toml,Cargo.lock,build.rs,tauri.conf.json}`、`src-tauri/icons/**`、`src-tauri/capabilities/**`、`src-tauri/src/**` 的 Tauri 本地文件与受控单节点夹具适配；`tests/**` 和 `src-tauri/tests/**` 的合成向量与测试。按项目工具链创建/锁定必要依赖，普通桌面入口使用 `pnpm tauri dev`。 |
r1|| `contracts/demands/ca-field-flow-v1/` | `README.md`、`README.zh-CN.md`、`schema.json`、`examples/**`、`vectors.json`，作为 proposed 候选合同与可执行一致性向量；引用逻辑端点和点位，不含真实绑定或凭据。 |
r1|| `contracts/README.md`、`contracts/README.zh-CN.md` | 仅增加候选合同索引，不声称 provider 已接受或 verified。 |
r1|| `automation-world/README.md`、`automation-world/README.zh-CN.md` | 仅增加独立候选切片的实际入口及冻结旧 CA 的边界。 |
r1|| `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`、`automation-world/PLAN.md`、`automation-world/PLAN.zh-CN.md`、`automation-world/plans/README.md`、`automation-world/plans/README.zh-CN.md` | 主协调仅机械同步本任务条目及实际角色事实，保留并发改动。 |
r1|| `plans/ARCH-AW-009-ca-flow-editor-json/tasks.md` | Development 在批准后创建并维护。 |
r1|| `plans/ARCH-AW-009-ca-flow-editor-json/checklist.md` | fresh-context Verification 在 Development handoff 后创建并维护。 |
r1|
r1|该目录范围包含实现所需局部文件，不包括外部应用源码或无关项目目录。若需要新的目录归属、增加子项目长期治理文件、不同合同位置、其它协议/节点类型或扩大 I/O 能力，先回 PM 修订，不从目录通配推断授权。保留未由本任务产生的 dirty 内容。正式验证应针对最终交付树，若先用临时副本，需在交接前整合并核对一致性。
r1|
r1|## 4. 编辑与流程定义合同
r1|
r1|### R01 编辑操作
r1|
r1|从节点面板拖入节点，连线、移动、删除，双击或选中后编辑节点名称、逻辑资源引用和参数；字段选择器按上游节点和可用输出展示字段、类型与必要说明。用户可取消编辑并保留已保存版本。列表须显示名称、保存版本和校验状态，支持打开和继续编辑；保存、导出前校验整图，失败时定位到节点、字段或连线并保留草稿。
r1|
r1|不完整草稿可在编辑会话中继续编辑和测试单节点。该草稿只有通过整图验证才可保存为有效流程版本或导出；测试单节点不要求整图已完成。导入先校验文件版本与内容。与已有 flow ID 和 revision 全文相同的文件由用户选择打开现有版本、新建副本或取消；同 ID 和 revision 但内容不同的文件标识冲突，只允许用户新建不同 flow ID 的副本或取消，不得覆盖已有版本。副本保留节点语义与节点 ID，其新的 flow ID 与 revision 在界面中明确显示。文件保存/导出采用用户明确选择的目标，失败或取消不得替换既有文件或留下被当作成功的半文件。
r1|
r1|### R02 v1 节点与端口
r1|
r1|| 节点 | 必要配置/行为 | 输出 |
r1|| --- | --- | --- |
r1|| 周期触发 | 间隔毫秒为正的有限整数；一个完成后等待间隔触发下一轮，同一流程不重入且不追赶漏掉的 tick | 触发身份及每轮新上下文 |
r1|| PLC 单点读取 | 逻辑 PLC ID、逻辑 point ID、声明类型；首版合成验收为 S7 标准 DB `int16` | `value`、原采集时间、质量、逻辑来源及样本身份 |
r1|| 条件比较 | 上游字段引用、`eq` 和类型化常量；首版验收为 `int16` 与 `1` 的精确比较 | `true` 或 `false` 分支 |
r1|| HTTP 请求 | 逻辑 endpoint ID、method、相对 path、可由常量或上游字段引用组成的 query 映射；首版实测 `GET` | 响应状态、类型化结果或明确错误 |
r1|| PLC 写／HTTP POST | 定义目标和输入的配置、输入输出 schema 和副作用说明 | 首版只模拟，不执行真实写入 |
r1|| 结束 | 可区分满足条件和不满足条件的本轮终态 | 本轮结束 |
r1|
r1|端口连线决定流向，画布坐标不改变执行顺序。每个普通节点有一个成功出口，条件有 `true`、`false` 两个具名出口，结束无出口。节点输出按运行路径可引用；失败不能成为默认零值或成功值。定时调度属于图定义，首版不提供图内任意环、无限等待、并行汇合或同轮反复读取；后续需要同轮等待时用有明确最大时长/次数的重读节点表达，属于后续范围。
r1|
r1|### R03 便携 JSON 草案
r1|
r1|JSON 顶层包含 `format: "aiis.flow"`、整数 `schema_version: 1`、`flow` 和可选 `layout`。`flow` 至少有稳定 `flow_id`、不可变 `revision`、周期 `trigger`、`entry_node_id`、含稳定 ID/节点 type/节点实现 version/类型化参数的 `nodes`、含 `from_node_id`/`from_port`/`to_node_id` 的 `edges`。首版便携合同的触发类型限 `interval`，手动单节点测试是编辑器操作而非导出触发类型。引用采用 `{ "node_id": "read_status", "field": "value" }` 的结构；类型化常量用 `{ "type": "int16", "value": 1 }`。HTTP GET 的 query 映射值可为该类型化常量或已完成上游节点字段引用，编码规则由候选合同及向量固定。节点与字段 key 为稳定机器身份，页面展示名称/语言可独立变化。
r1|
r1|`layout` 只保存以 node ID 标识的节点位置及必要画布信息，永不决定执行；缺失时 CA 使用自动布局。导出后再导入应保留节点 ID、语义、边、引用与已有位置；没有 layout 的文件可编辑并再导出。语义摘要覆盖规范化的执行语义投影，排除 `revision`、`layout` 和展示标签；布局或中文标签变化不得变更执行摘要。已保存版本包含 layout 的完整内容，布局单独变更后保存也形成新 revision，旧版原内容保留；完整文件 SHA 与执行语义摘要分别记录。摘要算法和规范化精确字节规则必须写入候选合同和向量，CA 与未来 FF 使用相同版本。
r1|
r1|`schema.json` 定义结构和各节点版本；语义校验另验证入口唯一、无悬空边、端口合法/单出口规则、所有节点从入口可达、所有分支终止、无图环、必填配置、引用节点在当前路径先执行且可用、引用字段存在、类型匹配与资源引用合法。示例的状态必须严格为 `int16` 值 1，字符串 `"1"`、布尔 `true`、null、缺失、坏质量或错误不能隐式等价于 1。对未知 schema 或节点版本明确拒绝并说明；不得丢弃未知语义后继续导出。连线判断及类型检查既需前端提示，也需保存/导出所调用的最终校验保证。
r1|
r1|逻辑资源描述与环境绑定分开。导出流只含 `plc_line_a`、`task_status`、`backend_api` 等逻辑引用及相对接口路径，真实 host/port、机架/槽位、凭据、token 和客户点表由目标环境显式绑定；CA/FF 各自维护自己的绑定文件或配置，不要求共用运行库。首版可以用内置脱敏点位描述和人工编辑逻辑资源供字段选择，不能宣称已具备 DAA 点表导入或 FF 点目录互通。对将来导入 ARCH-PLC-001 / `ff.plc` 点目录的身份、版本及映射另立合同。
r1|
r1|### R04 不可变版本与范围
r1|
r1|保存产生完整有效的不可变流程 revision，当前草稿继续修改必须形成新 revision；旧版本仍可重新打开/导出。已打开的草稿、保存版本和单节点测试输入有明确身份。首版文件与本地编辑存储不得使用旧 CA、DAA、SMA 或 FF 的可写数据库，应用标识、profile、端口与实际路径不得冲突或自动扫描其它应用配置。layout 可更新的行为必须避免静默覆盖已经导出的旧文件。流程文件不携带任何本机绝对路径或密钥。
r1|
r1|## 5. 编辑预览与单节点测试
r1|
r1|### R05 四种操作的边界
r1|
r1|| 操作 | 输入及行为 | 副作用 |
r1|| --- | --- | --- |
r1|| 编辑预览 | 草稿校验、模拟字段和条件评估；允许图不完整时报告局部可验证结果 | 不访问 HTTP/PLC；不执行目标；不创建生产记录 |
r1|| 模拟单节点测试 | 选择一个节点，手填或选择模拟的上游输出，类型校验后模拟该节点；不执行任何其它节点 | 不访问网络/PLC，不触发下游 |
r1|| 夹具单节点测试 | 显式选择此节点，输入逻辑资源与隔离夹具绑定，在发起前展示解析后的本地目标及调用方式；只执行一个实际只读调用 | 首版仅允许本任务启动/拥有的回环 S7 单点读或回环 HTTP GET；不触发下游 |
r1|| 整流测试/运行 | 在当前切片保留未来概念和禁用/明确未支持说明；FF 后续按其任务实现整流执行 | 需要完整图、固定版本和对所含全部节点的副作用合同；本次不实施 |
r1|
r1|“手填上游输出”不运行上游节点；可从本次测试上下文选择先前明确保存的模拟结果，显示其来源及值。测试输入缺失或类型错误时定位错误并拒绝调用。显示节点 ID、测试模式、所选逻辑资源、解析目标、输入摘要、输出或错误、开始时间与耗时、是否实际 I/O；界面不能把模拟成功显示成现场成功。日志/报告不包含凭据或完整敏感请求。完成单节点测试不会自动保存图或改变流程版本。
r1|
r1|### R06 目标和未知结果
r1|
r1|实际只读节点调用必须显式选择本任务本机夹具环境并检查解析目标为该夹具。HTTP 的相对 path 不得改变 scheme、host 或 port，重定向默认不跟随；夹具测试若遇重定向需报出目标并终止，不能访问跳转目标。夹具绑定由专用临时目录及其本任务启动的进程提供，不从真实环境自动发现配置；停止后验证进程和端口收尾。真实接口、真实 PLC 的调用与实际下发另行明确范围及授权；测试环境未建立时显示不可用，不静默连现场。
r1|
r1|PLC 写、HTTP POST 默认且首版只能模拟。测试界面应展示将要写入的逻辑目标及字段摘要并标记副作用；模拟成功只表示校验/演算成功。未来若启用外部写调用，`unknown` 表示可能已发送但无法确认，必须保留原动作身份及结果，供核实，不以新身份自动重发。首版通过合成故障向量验证 `unknown` 分类/展示，不声称现场写入、持久恢复或真实 unknown 已被验证。
r1|
r1|## 6. 端到端样例与数据合同
r1|
r1|命名示例为 `device_status_gate`，周期 `1000 ms` 仅为脱敏样例而非现场建议。定义入口 `read_status` 读取逻辑 `plc_line_a.task_status` 的 `int16`，将输出 `value` 连接 `check_status` 的左操作数；右操作数为类型 `int16` 的 `1`。匹配时进入 `get_info`，对 `backend_api` 的示例相对路径 `/status` 执行 GET，然后进入 `end_true`。不匹配时直接进入 `end_false`。
r1|
r1|一个可审阅的结构示意如下，实施合同的 schema 和向量是机器真相源。
r1|
r1|```json
r1|{
r1|  "format": "aiis.flow",
r1|  "schema_version": 1,
r1|  "flow": {
r1|    "flow_id": "device_status_gate",
r1|    "revision": 1,
r1|    "trigger": {"type": "interval", "interval_ms": 1000},
r1|    "entry_node_id": "read_status",
r1|    "nodes": [
r1|      {"id": "read_status", "type": "plc.read", "version": 1, "config": {"plc_ref": "plc_line_a", "point_ref": "task_status", "value_type": "int16"}},
r1|      {"id": "check_status", "type": "condition.compare", "version": 1, "config": {"left": {"node_id": "read_status", "field": "value"}, "op": "eq", "right": {"type": "int16", "value": 1}}},
r1|      {"id": "get_info", "type": "http.request", "version": 1, "config": {"endpoint_ref": "backend_api", "method": "GET", "path": "/status"}},
r1|      {"id": "end_true", "type": "end", "version": 1, "config": {"result": "matched"}},
r1|      {"id": "end_false", "type": "end", "version": 1, "config": {"result": "not_matched"}}
r1|    ],
r1|    "edges": [
r1|      {"from_node_id": "read_status", "from_port": "next", "to_node_id": "check_status"},
r1|      {"from_node_id": "check_status", "from_port": "true", "to_node_id": "get_info"},
r1|      {"from_node_id": "get_info", "from_port": "next", "to_node_id": "end_true"},
r1|      {"from_node_id": "check_status", "from_port": "false", "to_node_id": "end_false"}
r1|    ]
r1|  },
r1|  "layout": {"nodes": {"read_status": {"x": 0, "y": 0}, "check_status": {"x": 200, "y": 0}, "get_info": {"x": 400, "y": 0}, "end_true": {"x": 600, "y": 0}, "end_false": {"x": 400, "y": 150}}}
r1|}
r1|```
r1|
r1|预期执行语义为：本轮读取值为 1 时，只请求一次 GET 并结束 `matched`；读到 0 或其它有效 `int16` 时，本轮不请求 GET、结束 `not_matched`。下一轮触发时重新读取，不复用上轮值。读失败、缺失、错误类型、坏质量均终止该轮并报告，不走 false 或将值替换为 0。
r1|
r1|实际 CA 首版应在编辑预览以模拟值证明该分支，单节点测试分别证明 PLC/HTTP 夹具行为；这不代表 CA 已执行整条图。未来 FF 联调必须用导出的原始文件和同一版本合同证明上述逐轮行为。
r1|
r1|## 7. 首版验收标准
r1|
r1|| 编号 | CA 独立验收观察 |
r1|| --- | --- |
r1|| AC01 | 独立切片可按 README 的 `pnpm tauri dev` 普通入口启动并完成一次保存重开；旧 CA 源码、identity、旧本地数据和 FF 工程保持原状。 |
r1|| AC02 | 可以拖入首版节点、移动、连线和删除，列表打开编辑弹窗；中英切换的新增文案均有对应 key。 |
r1|| AC03 | 字段选择器列出可到达上游节点的输出类型；选择 `read_status.value` 构成类型化条件并可再次打开查看。 |
r1|| AC04 | 示例有效图可保存不可变 revision、导出 JSON、关闭并从导出文件导入；语义 ID、类型、边、参数、layout 与摘要按合同保持。无 layout 也可导入并自动布局。 |
r1|| AC05 | 保存/导出拒绝断线、悬空节点、无出口、条件出口错误、不可达、无终止、环、未知节点/版本，并定位问题；失败保留草稿及先前版本。 |
r1|| AC06 | 引用缺失、未来节点/非必经分支、未知字段、类型不一致、null、布尔或字符串冒充数字均被定位拒绝；坏质量/读错误不能映射为 0 或 false。 |
r1|| AC07 | 缺失版本、未知 schema/节点版本、损坏 JSON、超过合同限额和冲突导入明确失败或需用户选择新建；不静默丢未知语义、不覆盖旧文件/版本。 |
r1|| AC08 | 编辑预览用 1/0 的模拟输入得到对应分支；全程无 HTTP/PLC I/O，也无生产 outbox。 |
r1|| AC09 | 整图未完成时选中 PLC 读取节点，可手填或选择一个类型正确的模拟样本值并看到逻辑目标/节点配置/模拟输出/耗时；无上游执行或下游触发。 |
r1|| AC10 | 连接本任务隔离 S7 夹具，对一个配置的 `int16` 点做单节点实际读取；显示实际目标、值、质量、原采集时间、耗时及错误；夹具调用计数证明只执行一次读取且不触发后续 HTTP。 |
r1|| AC11 | HTTP GET 的 `query.sample` 引用上游数值字段，在图未完成时手填模拟输入 `5` 或选择模拟结果；向隔离 HTTP 夹具发送一次解析后的 `GET /status?sample=5`，展示目标、输入、请求、响应/错误和耗时；夹具计数证明只调用所选节点且无下游触发。 |
r1|| AC12 | 输入缺失、类型不符、端点缺失或非本任务夹具、断连/超时分别得到明确结果；错误不变成成功，也不调用其它节点。绝对 URL、协议相对路径、非本夹具目标及跳转到第二目标均被拒绝或终止，第二目标计数为零。 |
r1|| AC13 | PLC 写/HTTP POST 默认仅模拟，展示目标与副作用；fixture 证明无写调用。合成 `unknown` 向量可显示待核实和原动作身份，不触发自动重发。 |
r1|| AC14 | 导出只包含逻辑资源引用，无真实 endpoint、凭据、token 或本机路径；同一逻辑图可使用两份隔离 fixture 绑定，输出文件语义相同。 |
r1|| AC15 | 按仓库工具链完成范围相关的构建、图校验、节点测试、schema/语义向量、双语及链接检查；结果、退出码和受控设备/网络范围由对应角色实际记录。 |
r1|| AC16 | 独立识别 CA 本地验收与跨端联合 gate；若 FF 消费尚未实现或未联调，界面/文档及验收记录不能标为 FF 执行通过。 |
r1|
r1|### 跨端联合 gate（不由 CA 自证）
r1|
r1|| 编号 | 后续必须留存的真实证据 |
r1|| --- | --- |
r1|| J01 | CA 操作产生文件并记录绝对证据副本及 SHA-256、合同版本/语义摘要，运行用的环境绑定与该文件分离。 |
r1|| J02 | 经 FF 自己批准的 Rust 实现实际读取 J01 原文件；隔离 S7/HTTP 夹具的调用记录证明值为 1 时一次 GET、值非 1 时零 GET 且本轮终止。 |
r1|| J03 | 后一触发轮读取变化后的新值并按当轮值选择分支；提供 FF 逐轮 ID、节点次序、fixture 读数/请求计数与文件 SHA 对照。 |
r1|| J04 | 将 J01 原文件导入 CA 后显示并可继续编辑同一类型化图，原文件 SHA 不变；编辑新 revision 后原版本仍可复现。 |
r1|| J05 | CA/FF 各自 QA 与 Human Owner 接受有独立出处；联合记录只陈述其环境和版本，不代替任何一端各自的验收或真实现场验证。 |
r1|
r1|## 8. 风险与实施注意
r1|
r1|- CA 和 FF 的数据模型发生分歧时，按 `format`、`schema_version` 和向量协商；未知版本 fail closed。不得把已有 `ff.plc` 点目录误当作流程图。
r1|- JSON Schema 负责结构，引用在执行路径上的可用性、分支可达性和资源类型需要语义校验。错误应能定位，避免仅以 schema 通过当作可执行。
r1|- 导入可能带有未识别字段、布局或私密数据；通过明确合同校验和预览处理，不能静默丢失语义或把绑定写入导出文件。
r1|- 本机夹具必须使用隔离配置、测试数据和动态可用端口，记录进程与资源归属和清理条件。真实 PLC、业务 API 和配置不用于本任务验收。
r1|- 本轮没有 CA 全图执行器与实际写入。单节点模拟及 fixture 读取不能用于证明长运行、并发、真实 PLC、现场联锁或交付部署。
r1|- 首版候选可独立于冻结 CA 部署运行。未来合入正式 CA 的源码迁移、配置迁移和切换另立范围；回退本切片不会删除任何其它应用配置、历史和设备状态。
r1|
r1|## 9. 角色与技术 handoff
r1|
r1|批准后 Development 先读取当前完整 bundle 与 allowlist，核对 repo 并行变更，并按需使用 `desktop-tauri`、`rust-runtime`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`code-document-indexer` 和 `project-governance`。图、类型/资源声明与返回数据由同一合同驱动，受控本地 I/O 由 Rust 层执行；不得为了图预览而启动通信。依赖版本、许可和锁文件由 Development 根据仓库现有工具链确定并记录，不能仅凭本 PM 草案宣称选型已安装或验证。
r1|
r1|Development 完成批准范围后记录 `tasks.md`、自检、handoff、实际构建入口和临时资源归属；新的 Verification 使用 fresh context 校验精确 handoff 并创建 `checklist.md`。CA 独立 AC 与 J01–J05 联合 gate 分项记录。FF 的设计、代码和验证由 FF owning task 自行处理；CA 只提供候选 JSON、版本和向量供协商。
r1|
r1|## 10. 决策和批准历史
r1|
r1|| 日期 | Revision | 事实 |
r1|| --- | --- | --- |
r1|| 2026-11-24 | r1 | PM 根据转入请求起草 CA 节点编辑、流程 JSON、单节点测试及跨端联合 gate；待 Human Owner 审阅精确范围。 |
r1|
r1|后续顺序为 Human Owner 精确批准本 r1 → 命名 Development 实施 → fresh-context Verification → Human Owner 对 CA 本地交付最终验收。FF 端读取执行及 J01–J05 需 FF 自己的实现与联合验证，不由本规格代签。实际写入/真实设备和接口联调属于另行明确的范围。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
