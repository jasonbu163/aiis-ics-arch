Task ID: SMA-001
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Human Owner 总规格审阅；SMA-002 / SMA-003 既有候选已由各 checklist 核定 owner_accepted / qa_passed，SMA-004 r1 已获精确范围批准可交Development，本总规格仍draft
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: root
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 总体目标、阶段顺序、跨 Owner 依赖与总体验收

# SMA-001：SMA 分阶段交付总规格

## 1. 目标与本次授权

SMA 面向大量同类 HTTP API → HTTP API 映射：读取事实，经字段绑定、常量和必要转换后调用业务 API。长期目标按六阶段推进，本总规格管理目标、顺序与跨 Owner 依赖；各软件切片独立定义范围、allowlist、验收与风险。

Human Owner 于 2026-11-04（Asia/Shanghai）明确授权：

> 那就按这个顺序，先把 SMA-001 调整为总 spec，拆出“职责清理”和“CU 接入”两个子 spec，后续阶段先列目标和依赖，暂时不改代码。

上述授权在文档重组时仅覆盖规格拆分和相应索引，当时三个规格均为 `draft`，未启动 Development、应用、构建或软件验证，也未预建 tasks/checklist；该历史时点不代表当前子任务的软件授权状态。

2026-11-04 同日随后，Human Owner 先另行精确批准 SMA-002 r1，要求职责清理开发、保留 HTTP 映射并独立验证（完整原话见 SMA-002 spec §7）。该任务已完成Development handoff与独立QA；B1已披露日志事件及取证限制的Owner处置、同候选无漂移复核和条件性清理接受已由其checklist核定，当前 `owner_accepted` / `QA Verdict: qa_passed`，仅原af7140候选生效。

同日再后，主协调明确提出“先处理已披露B1/取证限制并由QA复核、清理验收后，批准并实施已链接SMA-003 r1，再规划配置独立化及后续闭环”的顺序，Human Owner直接回复“好的，批准”。SMA-003 r1据此独立获批，完成Development及fresh Verification；Human Owner本轮明确表示“好的，验收 SMA-003 r1”，其[checklist](../SMA-003-cu-integration/checklist.md#owner-acceptance-r1)已登记 `owner_accepted` / `qa_passed`，仅原ae9b3c候选生效。

同条消息另要求“接下来先准备‘配置独立化’的子 spec，暂时不改代码”，据此先形成[SMA-004 r1](../SMA-004-local-configuration/spec.md) draft。同日随后Human Owner明确表示“好的，批准 SMA-004 r1，按本地配置和纯预览的范围开始开发，暂时关闭正常投递，完成后做独立验证”，其spec已登记 `owner_approved`、前置003接受gate满足，可交Development。此处只机械衔接子任务既有批准/验收，SMA-001 r2仍为 `draft`，不新增总体批准或④–⑥授权。

## 2. 总体边界与现行基线

- SMA 来自 DTB TSS `a87c107c10e8d9d9d3e389e357b50d203d2aebf7` 的过滤副本；AW `control-agent/` 是冻结的旧 PLC 采集兼容运行时，后续通用 CA 为另一建设目标。原 TSS、旧 CA 及其它应用不在写入范围。
- 现有 SMA 已有 HTTP 取事实、组包、投递主链；源仍为固定 `POST /api/integration/v1/collection-facts/snapshot`，目标沿用保存的 Backend base URL，配置/lease/审计依赖旧 `/api/tss/v1`，尚非通用 GET→POST 闭环。
- 当前本仓 Backend 未配套该套旧接口，逐项 await 调度未证明批量吞吐。局部 UI、loopback 或构建通过不代替真实合同、业务保存、可靠性或容量接受。
- 默认 `SMA_HTTP_ENABLED=false`；保持独立 SMA 身份、配置隔离及普通 `pnpm tauri dev`。真实 HTTP/DB/PLC、真实 profile/历史修改、部署与 Git 发布仍需具体授权。

## 3. 阶段顺序与当前子任务

顺序为：职责清理 → CU 接入 → 配置独立化 → 单目标 GET→POST 闭环 → 历史消费与可靠恢复 → 批量运行优化。

| 顺序 | 当前任务 / 状态 | 产物与下一 gate |
| --- | --- | --- |
| ① 职责清理 | [SMA-002 r1](../SMA-002-scope-cleanup/spec.md)，checklist为 `owner_accepted` / `qa_passed` | [独立checklist](../SMA-002-scope-cleanup/checklist.md)已确认B1关闭、原af7140候选无漂移，Owner条件性接受仅此清理基线生效；原偏差/工具失败/blocked历史保留，不放宽未来真实profile禁令。 |
| ② CU 接入 | [SMA-003 r1](../SMA-003-cu-integration/spec.md)，checklist为 `owner_accepted` / `qa_passed`；Depends On: SMA-002 | [独立checklist](../SMA-003-cu-integration/checklist.md#owner-acceptance-r1)已记录Owner明确验收，N1/N2恢复关闭与原分层限制保留；仅原ae9b3c候选生效，不代表配置独立化或GET→POST已完成。 |
| ③ 配置独立化 | [SMA-004 r1](../SMA-004-local-configuration/spec.md)，`owner_approved`；Depends On: SMA-003 | Owner已精确批准本地配置与纯预览、暂时关闭正常投递；003前置接受已核定，可交Development，完成后仍须fresh独立验证及Owner终验，真实配置采用不在本次授权。 |

以上子任务为本 namespace 内同一 SMA 能力、模块 Owner 和总验收链的范围切片，均 `child_inherited`。父子只复用上下文；每个 Task ID / Revision 独立取得范围批准、形成 DEV handoff、fresh Verification 和 Human Owner 接受，不继承批准或 verdict。

子 spec 可先行准备，软件实施必须按上述顺序串行。SMA-002 交接实际变更、删除/保留清单、mapping 启动偏好及已触达展示 helper；SMA-003 已复用该基线，SMA-004 再以已接受CU候选为前提，避免重复整改或恢复退役能力。根 AGENTS 的表格/时间规则在各自实际触达范围持续适用。

## 4. 后续阶段：仅目标与依赖

阶段③上述SMA-004 r1已精确获批，其实施与独立验证归自身bundle；以下④–⑥未创建软件 spec/bundle、未分配 Task ID，进入时再界定精确合同、范围、验收和风险，不在本总规格提前冻结新 API、并发数或重试参数。

| 顺序 | 目标 | 前置依赖与届时决定 |
| --- | --- | --- |
| ④ 单目标 GET→POST 闭环 | 用一个受控目标完成源 GET → 绑定/常量/必要转换 → 目标 POST，核对真实业务保存。 | 配置独立化；源事实/目标业务 API 的可调用合同与固定候选就绪，身份/数据/错误/确认语义明确，真实联调单独批准。 |
| ⑤ 历史消费与可靠恢复 | 补齐历史完整消费、持久进度、待投递、回执及断线/重启/unknown 对账。 | 单目标接受；Backend 历史/排序/安全游标/保留合同与目标去重/回执可用；另定恢复/迁移规格，不以 latest 代替历史完整性。 |
| ⑥ 批量运行优化 | 在正确性与恢复基线上定义负载目标，测量容量并优化调度、资源占用和可观测性。 | 历史/恢复接受；代表负载、环境、容量口径获批；不预设并发模型，不以并发数冒充吞吐证明。 |

## 5. 外部依赖与并行准备

Backend 事实 API 合同和 DAA 阶段 C 可在各自 Owner/批准链下并行准备，无需等待前两阶段软件完成；当前 [Stage C 事实合同草案](../../../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md) 仅为关联背景，不转移状态或授权。

Backend 拥有事实/业务 API，DAA 拥有采集/上传，均非 SMA 子任务隐含范围。非 DAA 来源也须有明确事实生产 Owner。单目标闭环前，所选源与目标必须有固定候选、真实可调用合同和受控数据；若用 DAA 数据，其上传候选与 Backend 配套也需就绪。

外部接口未就绪不阻塞职责清理、CU和配置独立化的局部验证；这些阶段通过不能宣称外部合同、DAA 阶段 C 或业务闭环完成。

## 6. 总体验收与状态控制

| 条件 | 总任务完成前必须存在的事实 |
| --- | --- |
| 分阶段证据 | 六阶段均有届时获批的精确范围、实现、独立验证和 Human Owner 接受；尚无 spec 的阶段不能靠目标表判为完成。 |
| 连贯交付 | 整合到约定交付工作树，来源/配置/接口/恢复/负载边界一致，各接受候选及之后变更可追溯。 |
| 业务与可靠性 | 真实 GET→POST、业务保存、历史完整性/恢复、批量目标均有对应范围及证据，不能由前两阶段替代。 |
| 总体决定 | Human Owner 审阅阶段汇总、未关闭风险及外部依赖后明确总体接受；前两个子任务完成仅代表阶段①②完成。 |

各子 bundle 独立形成 spec、批准后 tasks、handoff 后 fresh checklist。主协调依据角色事实同步 PLAN/catalog；本总规格不重复子任务 allowlist/测试矩阵，不把文档静态检查记为软件 QA。

范围、关系、验收或风险实质改变时由 PM 修订并重新取得相应精确批准。PM profile 为 `contract_only`；主会话、bundle 与 diff 审计是合同控制，不宣称 ACL、自动路由或完整 Agent Team 激活。

## 7. 修订、历史与交接

| 日期（Asia/Shanghai） | Revision | 真实状态 |
| --- | --- | --- |
| 2026-11-03 | r1 | 合并 CU/职责清理的未实施 draft，未获软件范围批准、未开发或 QA。 |
| 2026-11-04 | r2 | 按§1授权重组；SMA-002/003 r1原候选均依各checklist核定owner_accepted/qa_passed。SMA-004 r1先形成draft，随后获Owner精确批准，可交Development。总spec仍draft，④–⑥未获软件批准；只同步事实，不改范围/顺序/关系/总体验收或r2。旧slug仅作链接兼容。 |

[r1 原文归档](evidence/r1-before-task-split/spec.md) 只读保留，SHA-256：`2af6751eff91a9d082fd99fd058c4e90cd314be8f79708b3dd7b0ac6247544f6`；不追认批准，不作当前软件执行依据。

文档重组阶段PM仅写三份spec；本次PM仅在SMA-004 r1登记Owner精确批准并最小同步本总规格的子状态/链接，不改SMA-002/003的spec/tasks/checklist。主协调负责索引并实际启动SMA-004 Development，DEV handoff后仍须fresh Verification。父任务不转移批准，④–⑥不随之获得授权或创建空bundle。
