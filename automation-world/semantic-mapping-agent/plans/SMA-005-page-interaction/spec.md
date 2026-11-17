Task ID: SMA-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development 按获批 SMA-005 r1 实施 #4 和 #6，完成后交独立 Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 页面首批问题 #4 和 #6，分开连接测试与保存，明确当前运行能力
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-004
Related Task: SMA-006

# SMA-005 页面交互首批修正

## 1. 目标与依据

连接页允许试读未保存的地址。运行页和映射列表直接说明当前只支持配置与预览，让用户知道哪些动作可用。首批对应讨论中的页面问题 **#4 测试会先保存**和 **#6 运行状态误导**。两项均基于已验收的 [SMA-004 r1](../SMA-004-local-configuration/checklist.md#owner-acceptance-r1) 和 [SMA-001 总规格](../SMA-001-cu-integration-and-scope-cleanup/spec.md)。

当前「测试 OpenAPI」先调用保存。运行页可尝试启动，宿主挂载后也会随旧偏好尝试自动启动，再由 Rust 拒绝。DAA 的连接测试与编辑提交各走独立入口，诊断按真实可用状态显示。参考其交互边界，SMA 测试仍使用点击时表单中的地址。 [SMA 连接页](../../src/app/connection/views/ConnectionModuleView.vue) · [SMA 运行宿主](../../src/app/twin-facts/components/TwinJsonContractPanel.vue) · [DAA 连接与诊断页](../../../data-acquisition-agent/src/app/plc/views/diagnostics/index.vue)

## 2. 首批范围

### R1 连接测试与显式保存（#4）

- 「测试 OpenAPI」取点击当时表单的 `scheme`、`host`、`port`，通过现有 HTTP 准入后，只向生成的 HTTP 或 HTTPS 地址发一次 `GET /openapi.json`。复用现有超时和 OpenAPI 解析。主机字段去掉首尾空白后只接受单一合法主机，空值、内部空白、非法端口、凭据、路径、查询或片段在发请求前拒绝。HTTP 关闭时零请求。HTTP 重定向按测试失败呈现，探测目标与界面显示的地址一致。
- 测试中与测试结果标出本次地址，成功、不可达、超时、非法或无效的响应、HTTP 关闭使用中英文提示。测试结果只在连接页展示，测试成功也保留未保存状态。协议、主机或端口变化后，清除旧结果和目录展示。若旧请求随后返回，即使输入改回旧地址，也不能盖过当前状态或更新后发测试。
- 测试成功、失败和取消均保持已保存连接、配置文档、SQLite `revision`、本地目录和材料选择原值。测试路径不得发出 `sma-backend-connection-changing` / `sma-backend-connection-changed` 或调用配置写入。只有点「保存连接」才按已观察版本提交，HTTP 关闭时仍能保存。保存失败保留输入并给出原因，保存成功状态独立于连通性结果，保存动作本身零 HTTP 请求。

### R2 运行页与映射列表的可用状态（#6）

- 映射运行页首屏及映射列表相应位置显示「当前仅支持配置和预览，映射投递未启用」的双语提示。暂停或停止只在既有状态确实适用时呈现，保留运行状态、计数及日志的诊断读取。运行页移除当前每轮发送 POST 的操作性描述。映射列表保留已保存配置预览，与向目标接口发请求的「单次测试」明确区分。
- 启动、恢复运行、单次测试及自动启动设置隐藏或禁用，鼠标、键盘与页面入口均不得发出相应执行或偏好写入命令。宿主启动与进入页面时不按旧的 `auto-start=true` 发起前端启动调用。旧偏好保留原值，既有 Rust 运行准入、直接 IPC 拒绝和安全暂停/停止行为继续适用。HTTP 开启只控制既有外部 I/O 准入，映射投递仍关闭。

## 3. 复用与写入边界

页面继续使用 CU 公共 `ConsoleCard`、`ConsoleActionButton`、`StatusCapsule` 和现有主题。SMA 持有表单、测试状态、可用状态及文案。Development 与 Verification 按 `frontend-ui`、`i18n-workflow` 核对中英、明暗、键盘与反馈，CU 和 DAA 作为只读参照。 [CU 公共出口](../../../console-ui/src/ui/index.ts)

下表为草案所列的后续产品文件范围。实际差异按对应需求核对。

| 路径相对 SMA | 用途 |
| --- | --- |
| `src/app/connection/views/ConnectionModuleView.vue`、`src/app/connection/components/BackendConnectionPanel.vue`、`src/app/connection/components/OpenApiOperationCatalog.vue`、`src/app/connection/api/index.ts` | R1 的显式动作、诊断反馈与草稿地址校验 |
| `src/app/twin-facts/components/{ApiFirstMappingRuntimePanel,MappingConfigurationsPanel,TwinJsonContractPanel}.vue`、`src/app/twin-facts/store/{apiFirstMappingRuntime,mappingStartup}.ts` | R2 的页面状态与调用装配。`MappingConfigurationsPanel.vue` 仅涉及列表和单次运行入口 |
| `src/app/{connection,twin-facts}/locales/{zh-CN,en-US}.json`、`tests/local-configuration.test.mjs`、`tests/page-interaction.test.mjs` | 对称文案与现有或定向的前端回归 |

SMA-006 负责弹窗表单和弹窗内反馈。两份规格可独立批准，建议 SMA-005 先交接页面变更，再基于同一工作树处理可能重叠的组件和文案。现有 SQLite schema、显式保存版本检查和各资源业务合同继续适用。GET→POST、真实 profile 采用或迁移、DAA/Backend 联调与发布另列范围。

## 4. 验收标准

| ID | 操作与通过标准 |
| --- | --- |
| AC01 | 在隔离 profile 存好地址 A，并记录配置快照、目录、材料选择及 `revision`。输入未保存的地址 B 点「测试 OpenAPI」。本机受控服务只收到发往 B 的一次 `GET /openapi.json`，页面显示 B 与结果。关闭重开后仍加载 A。配置内容、版本及连接变更事件计数没有变化。 |
| AC02 | 对 B 分别返回非成功、非法 OpenAPI、超时和重定向，页面给出对应提示，零配置写入且重定向目标零请求。HTTP 关闭、主机带空格、路径或 `@`、端口无效时监听器零请求。B 的旧请求未结束时切换到 C 再测，或改回 B 后重测，旧响应不能回填或覆盖后发结果。最后在 HTTP 关闭时点保存，按原版本检查一次提交。冲突时保留输入和现有 SQLite 内容。 |
| AC03 | 在 HTTP 关闭与开启的隔离场景打开运行页和映射列表。单次测试、启动、恢复、自动启动控制无法触发，说明清楚。预置旧 `auto-start=true` 后重开，前端执行和偏好写入调用计数均为 0，旧偏好原值可读。现有受控状态和日志可读，适用的暂停、停止调用保持原语义。直接执行准入的拒绝由原生既有回归证据核对。配置和预览照常可用，目标监听器零请求。 |
| AC04 | 在默认 `1280×800` 和最小 `1024×720` 检查中、英与明、暗组合。用键盘完成测试或保存，焦点可见，地址、状态与禁用原因可读，无新增页面横向溢出。至少一个正常 Tauri 窗口内使用隔离 profile 对照保存、只测、重开与运行提示。 |

开发与独立验证使用可丢弃 SMA profile、受控本机 HTTP 和模拟 IPC，按证据层分别记录观察。候选以 `pnpm check`、`pnpm test`、`pnpm build`、差异与链接检查交接，软件结果由实施后形成的记录承载。 [实际窗口设置](../../src-tauri/tauri.conf.json)

## 5. 后续与交接

- 页面第二批计划处理 **#1 卡片粘连**、**#2 首屏主次**、**#3 表头和操作列错位**。第三批 **#5 源事实难查**先明确读取状态，采集 v2 接入时再定 PLC、DB 和点位搜索。
- 主要回归风险是旧请求覆盖新状态，或关闭运行入口时误伤预览和安全停止。失败候选由 Development 修复或撤回本次前端差异，既有配置数据继续按 SMA-004 合同维护。
- 2026-11-14（Asia/Shanghai）形成 r1 草案，交 Human Owner 审阅。范围批准后进入 Development，交接后由独立 Verification 执行第 4 节。

## 6. Human Owner 批准

Human Owner 于 2026-11-16（Asia/Shanghai）批准 SMA-005 r1。

> 好的，先批准 SMA-005 r1，按 #4 和 #6 的范围开始开发，完成后做独立验证。SMA-006 先保留草案，等页面交接后再做。

获批的 r1 草案 SHA-256 为 `719ba68bdd9a46814361c0fd06860e07dfdebc12b74073d04842f76e6dd38b80`。
