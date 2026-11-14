# AIIS ICS Architecture 计划

English version: [PLAN.md](PLAN.md)

## 当前源码基线

- 源码基线版本：`1.0.0`（annotated `v1.0.0` tag 与 `release/1.x.x` 维护分支已复核；不代表已创建托管
  Release 或完成部署）。
- 当前源码表面：`backend/`、`backend-dotnet/`、`frontend-js/`、`automation-world/`、`field-flow/`、`tools/`、`contracts/`；旧CA冻结兼容，DAA本地采集、SMA本地配置、后端事实/业务接口及FF各自按下方任务保留实现、QA与Owner验收层级。
- 当前文档状态快照：2026-11-05；详细证据与最新有效决定归下方所属任务bundle。
- 项目业务模块和项目输入归使用方项目仓库。

## 架构工作流

Human Owner于2026-10-30验收DAA-002 r2、DAA-003 r1、DAA-004 r1和[DAA-007 r2](automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md)，确认阶段B仅在本次受控DS联调范围内完成。DS既有接受与S7读取至SQLite证据分别保留；历史证据限制、来源未明事项、既有配置/历史和原联调profile保持。后续Backend事实与业务接口已按各自任务通过隔离验证；DAA上传器、阶段C实际联调、自动启动及真实现场验证仍未由阶段B验收完成。

| 工作流 | 状态 | 记录 | 边界 |
| --- | --- | --- | --- |
| 计划与实绩通用任务 | `qa_passed`（ARCH-TASK-001 r1，QA3） | [r1 spec](plans/ARCH-TASK-001-generic-plan-performance/spec.md) | dev 切换、合成闭环和两个列表页通过独立 QA，待 Human Owner 最终验收。[QA 记录](plans/ARCH-TASK-001-generic-plan-performance/checklist.md) |
| 采集数据优化与业务接线项目路线 | `draft`（ARCH-ACQ-001 r1） | [r1 spec](plans/ARCH-ACQ-001-acquisition-data-coordination/spec.md) | 由 Owner 主动触发跟踪四项交付、两条业务线及最终 SMA 接线。后端事实先行。 |
| 简化后端采集事实 | `qa_blocked`（ARCH-BE-012 r4） | [r4 spec](plans/ARCH-BE-012-simplified-plc-facts/spec.md) | 独立源码验证和 Owner 指定的 dev 功能验证通过。原隔离矩阵及最终验收待定。 |
| Web 采集数据模块 | `qa_passed`（ARCH-FE-005 r2） | [r2 spec](plans/ARCH-FE-005-acquisition-data-module/spec.md) · [QA 记录](plans/ARCH-FE-005-acquisition-data-module/checklist.md) | QA5 通过 PLC 选中后的筛选对齐、标题帮助及 dev 实读复验，待 Human Owner 最终验收。 |
| 旧 Projection 与采集旧表清退 | `qa_passed`（ARCH-ACQ-002 r2） | [r2 spec](plans/ARCH-ACQ-002-legacy-projection-retirement/spec.md) · [QA 记录](plans/ARCH-ACQ-002-legacy-projection-retirement/checklist.md) | 独立 QA 通过。Alembic 已清退指定 3307 dev 库的九张空表，v2 数据对账一致。两个测试容器已回收，待 Human Owner 最终验收。 |
| 采集事实表、来源登记与默认浏览 | `owner_accepted`（ARCH-ACQ-003 r2） | [r2 spec](plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) | Human Owner 于 2026-11-11 验收 r2 提供方、API 和指定 dev 页面。DAA-010 使用当前开发阶段上报合同。 [验收记录](plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) · [开发 OpenAPI](contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json) · [原理与使用](docs/acquisition-data-guide.zh-CN.md) |
| 简化 PLC 来源登记 | `owner_accepted`（ARCH-ACQ-004 r4） | [r4 规格](plans/ARCH-ACQ-004-acquisition-source-registry/spec.md) | Human Owner 于 2026-11-13 验收源码及隔离 QA3；[验收记录](plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#arch-acq-004-r4-human-owner-最终验收)。现有 dev 数据库迁移及人工验证另行处理。 |
| PLC 来源删除与独立历史查询 | `qa_passed`（ARCH-ACQ-005 r1） | [r1 规格](plans/ARCH-ACQ-005-acquisition-source-deletion/spec.md) | dev API 和 Web 独立验证通过，等待 Human Owner 最终验收。 |
| 配置优先的设备状态与过程监控 | `qa_passed`（ARCH-OBS-001 r7 QA3） | [r7 实施范围](plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#r7-implementation) | 隔离候选通过 R7-AC01–07。六项旧回归断言失败已记录，待 Human Owner 最终验收。[QA3 独立核验](plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/checklist.md#r7-qa3-独立验证)。 |
| C# 原生开发配置 | `draft`（ARCH-BE-011 r2） | [r2 spec](plans/ARCH-BE-011-dotnet-local-environment-loading/spec.md) | appsettings/User Secrets与Development启动profile替代未批准的r1 .env方案。获授权只读核对确认Plan结构/权限匹配，但SYSTEM时区名称不通过现C#创建校验；待精确r2实施批准，现库采用另行处理。 |
| 项目现状与设计决策文档同步 | `qa_passed`（ARCH-DOC-001 r1，QA2） | [r1 spec](plans/ARCH-DOC-001-project-state-and-decision-sync/spec.md) | 四份设计正文6处返工后，fresh-context QA2通过全部14项文档验收并关闭两组QA1问题；QA1失败及证据保留。Owner文档终验pending。 |
| 匿名PLC事实服务 | `owner_accepted`（r1，2026-11-05）；保留A历史 | [spec](plans/ARCH-BE-009-backend-facts-integration/spec.md) | 两轮独立MySQL8.4.6验证通过：Development 9项正式MySQL及42项扩展；fresh QA独立通过9项正式、47项具名扩展、181项聚焦和44项旧测试（9项未选）。专用资源和27份临时口令/操作配置已清理并独立核验。Human Owner于2026-11-05验收获批源码及隔离A+B交付；真实采用、DAA/SMA联调及生产长期SLA仍单独处理；现有库/真实历史未操作。 |
| 后端业务匿名集成入口 | `owner_accepted`（r2，2026-11-05）；保留A历史 | [r2 spec](plans/ARCH-BE-010-anonymous-business-integration/spec.md) | 两轮独立MySQL8.4.6验证通过：两轮真实MySQL/ASGI/时间/并发/断线、各161项受影响源码回归及事实清理后永久业务回执。专用资源和27份临时口令/操作配置已清理并独立核验。Human Owner于2026-11-05验收获批源码及隔离A+B交付；真实采用、DAA/SMA联调及生产长期SLA仍单独处理；现有库/真实历史未操作。 |
| SMA本地配置与工作台 | `qa_passed`（SMA-004 r1；SMA-002/003已接受） | [SMA-004 r1 spec](automation-world/semantic-mapping-agent/plans/SMA-004-local-configuration/spec.md) | 单SQLite配置、备份恢复及纯预览通过QA2，待Owner终验；正常投递保持关闭。SMA-001总规格仍draft；GET→POST运行器、来源身份适配和可靠恢复后续分别批准。 |
| 阶段C匿名事实合同与设计同步 | `qa_passed`（ARCH-AW-008 r1，QA2） | [r1 spec](plans/ARCH-AW-008-stage-c-facts-contract/spec.md) | 文档QA2关闭F-QA1-001并通过AC01–AC20，原QA1失败保留，待Owner文档终验。proposed共同需求与四份设计已交付；后续Backend软件证据见BE009/010，DAA上传器与阶段C实际联调仍未交付。 |
| C# 后端首期 Plan 切片 | `qa_passed`（ARCH-BE-008 r1，QA2） | [ARCH-BE-008 r1 spec](plans/ARCH-BE-008-csharp-backend-plan-slice/spec.md) | 新 fresh QA2 独立 A11、可丢弃 MySQL B 及 291 正式 HTTP 检查通过，F-QA1-001 已关闭，QA1 失败历史保留。根 backend-dotnet 已实现计划创建/详情/列表，无登录认证；待 Human Owner 最终验收，未进入生产采用。 |
| C# 后端架构设计 | `owner_approved`（ARCH-BE-007 r1） | [ARCH-BE-007 r1 spec](plans/ARCH-BE-007-csharp-backend-architecture/spec.md) | Human Owner 于 2026-10-28 批准精确 r1 设计：独立 FastEndpoints/EF Core/MySQL、DTO 校验、模块分层及逐步替代路线，首期无登录认证。另行获批的 ARCH-BE-008 A+B 承担软件实施及后续 QA。 |
| 最新三界总图与状态快照 | `qa_passed` | [ARCH-MULTI-002 r1 spec](plans/ARCH-MULTI-002-three-worlds-diagram-sync/spec.md) | 独立 AC01–AC10 文档 QA 结论已写入 checklist；结论保存后的 Agent 最终回报遇到模型容量错误。Mermaid 未渲染，待 Human Owner 最终验收；仅文档改动。 |
| Field Flow 独立现场运行程序 | `qa_passed`（FF-001 r4） | [FF 计划](field-flow/PLAN.zh-CN.md)；[FF-001 r4 spec](field-flow/plans/FF-001-dual-runtime-demo01/spec.md) | Fresh QA2已通过双版本本地 AC01–AC15，关闭全部三项 Rust QA1 缺陷。Rust 正式/隔离全18项通过；未变的 Python48 原 QA1 全量证据已核准，并完成新环境构建/单元/gate/CLI 复验。失败历史保留，Human Owner 最终验收、现场及长期运行验证待定。 |
| Field Flow PLC JSON目录与多PLC调用 | `owner_accepted`（FF-004 r2 A） | [r2 spec](field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/spec.md) · [最终验收](field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md) | QA3 在 macOS arm64 回环环境通过 AC01–AC14，Human Owner 于 2026-11-10 接受 Rust 每 PLC JSON、YAML v2 和多 PLC S7 INT16。Modbus 仅支持结构校验，旧驱动与现场验证边界见任务记录。 |
| Field Flow基础与进阶案例库 | `owner_accepted`（FF-005 r1 A） | [r1 spec](field-flow/plans/FF-005-basic-and-advanced-examples/spec.md) | Human Owner于2026-11-04接受有限本地案例库；QA2通过，QA1失败和旧hold_ack完整扣ACK强制回收限制保留。案例接受不等于现场、跨平台或长期运行接受。 |
| Field Flow C# 运行时 | `dev_blocked` (FF-003 r2) | [FF-003 r2 spec](field-flow/plans/FF-003-csharp-runtime-demo01/spec.md) | C# 源码和 macOS arm64 开发自检已完成。正式树与独立副本各通过 21 项测试，5 组回环进程场景通过。Win10 x64 原生验证待实验宿主。 [开发记录](field-flow/plans/FF-003-csharp-runtime-demo01/tasks.md). |
| Field Flow 手册与 Rust 构建说明 | `qa_passed`（FF-002 r1） | [FF-002 r1 spec](field-flow/plans/FF-002-user-guide-and-runtime-positioning/spec.md) | 新的独立 Verification 已通过修正手册及有限本地教程验收，QA1 失败保留；Human Owner 最终验收待定。Windows 适配、Linux 验证、现场托管与长稳仍分别推进。 |
| DAA/SMA/CA 三应用发展路线 | `owner_accepted` | [ARCH-AW-007 r2 spec](plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md) | Human Owner 于 2026-10-21 最终验收精确 r2 文档，原 fresh-context AC01–AC14 QA 保留。DAA 专用采集、TSS 派生 SMA 表格/工作台、CA 通用编排/内部连接器及未来全类型健康明确，首版无登录。完整 r1 历史/QA 保留，证据已归档，两处自有临时目录共 49 文件已清理；未改代码、未追加测试，软件另立范围。 |
| DAA/SMA/CA 与 CA 通用流程设计 | `owner_approved` | [ARCH-AW-006 r2 spec](plans/ARCH-AW-006-unified-flow-agent-design/spec.md) | Human Owner 已批准 r2 设计：DAA 大量采集、TSS 派生 SMA 映射表/工作台、CA 节点/版本/上下文及扩展；首版无登录认证。产线/实验室案例及完整 r1 保留，文档实施统一归 007 r2，软件实施另立范围。 |
| DS产品实施与G0退役 | `owner_accepted`（ARCH-AW-005 r5） | [r5 spec](plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) | 2026-10-27接受r5及当时DS版本；原QA4精确候选、34核心测试、16客户端/第17条拒绝及失败历史保持，G0已退役。10月29日草稿/版本管理DIRECT增量待人工确认；10月30日受控DAA联调接受归DAA-007，不扩及现场或后续能力。 |
| DS 产品易用性迭代 | `owner_accepted`（DS-001 r1） | [DS PLAN](automation-world/device-simulator/PLAN.zh-CN.md)；[Owner决定](automation-world/device-simulator/plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001) | Human Owner于2026-10-27接受当前DS；必要开发自检、纯文字手册及另批DIRECT整改已交付，独立QA仅DS-001例外未执行。本轮仅验收收尾；SQLite联调另批，阶段C排除。 |
| DS 多实例 S7 详细设计 | `owner_accepted` | [ARCH-AW-004 r2 spec](plans/ARCH-AW-004-ds-detailed-design/spec.md) | Human Owner 于 2026-10-18 验收精确 r2 详细设计，独立 AC1–AC29 文档 QA 与 r1 历史保留，文档收尾已记录。G0、软件实施、原生/S7 联调及容量实证须另行立项批准。 |
| DAA/SMA 详细设计与配合合同 | `owner_accepted` | [ARCH-AW-003 spec](plans/ARCH-AW-003-daa-detailed-design/spec.md) | Human Owner 于 2026-10-17 验收 r3，独立 AC21–AC35/R26 文档 QA 保留；r1/r2 历史保留，SMA/AW Runtime 原字节未改；仅设计验收，实施另需获批 spec |
| DAA 阶段 A：CU 布局与既有页面 | `owner_accepted` | [DAA-001 r1 spec](automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md) | Human Owner 于 2026-10-17 验收 r1；新的 fresh Verification 通过，F-001/F-002 关闭，原失败历史保留。仅阶段 A 布局与既有功能兼容，B/C 实施另批。 |
| DAA 阶段 B：本地采集闭环 | `owner_accepted` | [DAA-002 r2 spec](automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/spec.md) | Human Owner于2026-10-30验收r2，QA4通过AC01–AC20、F-001–F-004解除。本地采集、双SQLite、容量恢复及受控原生基线已接受。失败历史和历史raw当前可用性限制保留；后续入口退役/DS联调归DAA-003/007。 |
| DAA SQLite 唯一入口与 YAML 迁入 | `owner_accepted` | [DAA-003 r1 spec](automation-world/data-acquisition-agent/plans/DAA-003-sqlite-only-startup/spec.md) | Human Owner于2026-10-30验收r1，QA2解除F-001/F-002。接受SQLite唯一入口及历史一次性停用草稿迁入；DAA-007已退出普通迁入链。配置/历史和私有回执保护保持，失败及历史raw当前可用性限制保留。 |
| DAA 迁入提示收敛与最小源码导入验证 | `owner_accepted` | [DAA-004 r1 spec](automation-world/data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/spec.md) | Human Owner于2026-10-30验收r1，AC01–AC08核验通过双语说明、界面收敛及受控三点DB/UDT导入。操作差异、观察及历史raw当前可用性限制保留，配置/历史和私有回执保持。 |
| DAA 多DB导入与嵌套辅助偏移 | `owner_accepted` | [DAA-005 r1 spec](automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) | Human Owner已于2026-10-19最终验收精确DAA-005 r1，独立QA2已通过AC01–AC13。本次仅验收收尾，原失败和原生证据保留，未追加测试或实现改动。 checklist. |
| DAA–DS阶段B联调与上海时间合同 | `owner_accepted` | [DAA-007 r2 spec](automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | Human Owner于2026-10-30验收r2，并确认阶段B在本次受控DS联调范围内完成；AC01–AC22核验及8590份样本/4295轮完整重开比较通过。历史checkpoint缺失和15:27来源未明事项继续跟踪。配置/历史及原联调profile保留；阶段C、自动启动策略和现场验证另项。 |
| DAA 点位技术命名与导入能力复用准备 | `owner_accepted` | [DAA-006 r3 spec](automation-world/data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md) | Human Owner于2026-10-20最终验收r3及另行DIRECT界面调整；独立AC01–AC20核验、原blocked历史及原生限度保留。验收源码已固定，临时资源已归档/清理；后续受控阶段B验收见DAA-007，阶段C另项。 |
| 三界架构发展蓝本 | `qa_passed` | [ARCH-MULTI-001 spec](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | r2 [双语 ROADMAP](ROADMAP.zh-CN.md) 已交付；独立文档 QA 通过 AC1–AC10，待 Human Owner 最终审阅；未改代码 |
| AW Agent 工程前置初始化 | `owner_accepted` | [ARCH-AW-001 spec](plans/ARCH-AW-001-agent-foundation/spec.md) | CA 已迁入并冻结，DAA/SMA 初始化并可独立启动；定向复核通过，Human Owner 于 2026-10-14 接受 r1；本轮未追加测试；UI/SQLite 后续另立任务 |
| AW 白皮书与运行原理设计 | `owner_accepted` | [ARCH-AW-002 spec](plans/ARCH-AW-002-agent-runtime-design/spec.md) | r3 DS 增补独立 QA 通过 AC12–AC17，Human Owner 于 2026-10-18 验收 r3 文档；未开始代码实现；r2 文档 QA 保留为历史；未授权功能实施 |
| 通用 Docker 部署 | `developer_handoff` | [ARCH-DOCKER-002 spec](plans/ARCH-DOCKER-002-reusable-deployment/spec.md) | r2 实施完成；三份 Compose 静态检查通过，旧根入口已退下，待独立 Verification，运行验证另行批准 |
| 公开 Core 提取 | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | fresh-context Verification 通过 public-safe Core、smoke/dev/release-check 与清理审计后，Human Owner 已接受 r3 |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner 已接受单一 `d4e6f8a0b2c4` Core root 与十四表 source/static/no-DB 基线 |
| 空 volume Docker runtime 证明 | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | fresh-context Verification 通过隔离 MySQL 8.4.6 构建/迁移/健康/代理/清理证明后，Human Owner 已接受 r1 |
| 本地开发环境采用 | `owner_accepted` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | 固定名 dev runtime、后端健康/前端检查、bootstrap default-off 证明和失效 smoke 文档清理完成后，Human Owner 已接受 r4 |
| 1.0.0 源码定版 | `owner_accepted` | [ARCH-REL-001 spec](plans/ARCH-REL-001-source-release-1.0.0/spec.md) | fresh-context Verification 已通过 r3，Human Owner 已接受；§5.4 main-only governance receipt 已准备但仍待 Human Owner 手工 push |
| 前端模块组装 | `qa_passed`（ARCH-FE-001 r3） | [r3 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | 第二轮fresh-context Verification通过；15项合同测试、隔离构建和装配/权限兼容检查保留。首轮三项缺陷已关闭；待Human Owner最终验收，版本与发布另行决定。 |
| 项目前端角色权限与模块首批接入 | `owner_accepted` | [ARCH-FE-002 spec](plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md) | r4 品牌、配置、启动、构建与公开浏览器检查已独立通过；保留 r2/r3 历史，Human Owner 已于 2026-10-09 接受 r4，其他模块预留 003 |
| 剩余前端模块 manifest 适配 | `owner_accepted` | [ARCH-FE-003 spec](plans/ARCH-FE-003-remaining-module-manifest-adaptation/spec.md) | r2 价格页直调 auxiliary API；模块检查、36 项测试及隔离构建独立验证通过，Human Owner 于 2026-10-12 接受 r2，并确认 env 页面权限显示测试正常；保留 r1 历史 |
| 前端系统名称与小标题配置 | `owner_accepted` | [ARCH-FE-004 spec](plans/ARCH-FE-004-system-name-env-configuration/spec.md) | r3 独立静态复核通过后，Human Owner 于 2026-10-10 反馈测试无误并接受；保留 r1/r2 历史与原始证据 |
| 后端角色 API 权限配置 | `qa_passed` | [ARCH-BE-001 spec](plans/ARCH-BE-001-role-api-permissions/spec.md) | r3 已恢复十一组英文 env 标题；配置值和逐项注释保留；独立 QA 通过；待 Human Owner 最终验收 |
| 能源价格后端 API | `owner_accepted` | [ARCH-BE-002 spec](plans/ARCH-BE-002-energy-price-api/spec.md) | r3 已批准在本仓库实施可复用 auxiliary；三个 API、独立权限与显式迁移；独立 QA 通过，Human Owner 已于 2026-10-13 验收 r3，真实数据库操作另行授权 |
| 映射 Service API 试点 | `qa_passed` | [ARCH-BE-003 spec](plans/ARCH-BE-003-mapping-service-api-pilot/spec.md) | r3 A/B 独立通过：当前源码 483 通过/30 未选及编译通过，两轮 MySQL 各三场景全部通过；F-001/B-001 关闭，专用资源和测试口令已清理，待 Human Owner 最终验收 |
| 小时价格与按日历史 | `owner_accepted` | [ARCH-BE-004 spec](plans/ARCH-BE-004-energy-price-hourly-history/spec.md) | r2 独立 QA 通过：211 后端、38 前端及浏览器验证；F-001 已关闭，Human Owner 于 2026-10-13 完成人工试用并接受；真实数据迁移另行授权 |
| 后端业务模块回迁修复 | `owner_accepted` | [ARCH-BE-005 spec](plans/ARCH-BE-005-backend-business-module-reintegration/spec.md) | 独立 A 及两轮隔离 MySQL 各五场景通过，专用资源已清理；Human Owner 于 2026-10-16 最终验收 r3 |
| 映射业务 API 扩展 | `qa_passed` | [ARCH-BE-006 spec](plans/ARCH-BE-006-mapping-business-api-expansion/spec.md) | A+B 独立验证通过；两轮专用 MySQL 及五页浏览器检查完成，资源与测试秘密已清理；155 项相关测试通过，四项历史冻结 profile 失败保留；Human Owner 最终验收 pending |
| CA打包配置方向 | `draft`（CA-CONFIG-001 r1） | [spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | 旧CA配置界面方向草案；须按当前本地配置权威及独立应用责任刷新后再精确批准。冻结兼容源码不因此启动新CA/DAA配置开发，当前未实施。 |

## 延后边界

ARCH-MIG-001 r1、ARCH-DOCKER-001 r1 与 ARCH-DEV-001 r4 均已获 Human Owner 接受。MIT license 及其中
声明的 ownership 已保留，但生产 Docker 拓扑、真实 PLC/CA 操作和项目模块迁移继续作为独立 Human Owner
gate。ARCH-REL-001 r3 已在 fresh-context Verification 记录 `qa_passed` 且 Human Owner final acceptance
后达到 `owner_accepted`；r1/r2 Development 记录及 r2 main preparation commit 作为 superseded 历史
保留。六路径 §5.4 main-only governance receipt 已准备，但仍待 Human Owner 手工 staging、commit、
push；该状态不代表 GitHub Release、部署或 production readiness。

本文件只做简短索引；详细范围、命令和证据归属各自任务三文件。
