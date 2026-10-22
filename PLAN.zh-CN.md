# AIIS ICS Architecture 计划

English version: [PLAN.md](PLAN.md)

## 当前源码基线

- 源码基线版本：`1.0.0`（annotated `v1.0.0` tag 与 `release/1.x.x` 维护分支已复核；不代表已创建托管
  Release 或完成部署）。
- 当前工作树表面：`backend/`、`frontend-js/`、`automation-world/`、`field-flow/`、`tools/`、`contracts/`；CA 已迁入 AW 并冻结，DAA/SMA 初始化状态见下方任务。Field Flow 已有局部 Rust 候选，因 S7 确认关联问题阻塞；Python 未开始。
- 项目业务模块和项目输入归使用方项目仓库。

## 架构工作流

DAA 阶段 B 整体仍未关闭，已有受控本地证据和已验收增量继续有效；仍需取得满足联调要求且独立验收的 DS 协议基线，再另批 DAA–DS S7 读取至 SQLite 联调，完成 fresh QA 与 Human Owner 验收。阶段 C 实施在 B 整体验收及 Backend API 合同稳定后推进。下表各任务状态保留其原有有限范围。

| 工作流 | 状态 | 记录 | 边界 |
| --- | --- | --- | --- |
| 最新三界总图与状态快照 | `qa_passed` | [ARCH-MULTI-002 r1 spec](plans/ARCH-MULTI-002-three-worlds-diagram-sync/spec.md) | 独立 AC01–AC10 文档 QA 结论已写入 checklist；结论保存后的 Agent 最终回报遇到模型容量错误。Mermaid 未渲染，待 Human Owner 最终验收；仅文档改动。 |
| Field Flow 独立现场运行程序 | `draft`（FF-001 r3）；r2 `dev_blocked` | [FF 计划](field-flow/PLAN.zh-CN.md)；[FF-001 r3 spec](field-flow/plans/FF-001-dual-runtime-demo01/spec.md) | r2 已有可编译 Rust 候选及局部本机证据，但未匹配 S7 写 ACK 被提交 confirmed。PM 提议经原库公开 raw ISO API 增加受限 INT 适配，精确 r3 待批准。全部源码/历史/证据保留；Python、完整交接及 QA 待完成，ARCH-TOOL-001 r2 不变。 |
| DAA/SMA/CA 三应用发展路线 | `owner_accepted` | [ARCH-AW-007 r2 spec](plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md) | Human Owner 于 2026-10-21 最终验收精确 r2 文档，原 fresh-context AC01–AC14 QA 保留。DAA 专用采集、TSS 派生 SMA 表格/工作台、CA 通用编排/内部连接器及未来全类型健康明确，首版无登录。完整 r1 历史/QA 保留，证据已归档，两处自有临时目录共 49 文件已清理；未改代码、未追加测试，软件另立范围。 |
| DAA/SMA/CA 与 CA 通用流程设计 | `owner_approved` | [ARCH-AW-006 r2 spec](plans/ARCH-AW-006-unified-flow-agent-design/spec.md) | Human Owner 已批准 r2 设计：DAA 大量采集、TSS 派生 SMA 映射表/工作台、CA 节点/版本/上下文及扩展；首版无登录认证。产线/实验室案例及完整 r1 保留，文档实施统一归 007 r2，软件实施另立范围。 |
| DS 产品实施与 G0 退役 | `qa_passed` | [ARCH-AW-005 r5 spec](plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)；[r5 开发交接](plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md)；[Verification 记录](plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md) | 源码 306a09d5 独立核验通过：34 项核心测试、普通启动、N1–N3 和原协议适用矩阵，含 16 客户端通信及第 17 条连接拒绝。F-r5-003 已关闭，废弃 G0 已退役，失败历史保留。Owner 最终验收待完成；DAA–DS SQLite 联调另批，阶段 C 排除。 |
| DS 多实例 S7 详细设计 | `owner_accepted` | [ARCH-AW-004 r2 spec](plans/ARCH-AW-004-ds-detailed-design/spec.md) | Human Owner 于 2026-10-18 验收精确 r2 详细设计，独立 AC1–AC29 文档 QA 与 r1 历史保留，文档收尾已记录。G0、软件实施、原生/S7 联调及容量实证须另行立项批准。 |
| DAA/SMA 详细设计与配合合同 | `owner_accepted` | [ARCH-AW-003 spec](plans/ARCH-AW-003-daa-detailed-design/spec.md) | Human Owner 于 2026-10-17 验收 r3，独立 AC21–AC35/R26 文档 QA 保留；r1/r2 历史保留，SMA/AW Runtime 原字节未改；仅设计验收，实施另需获批 spec |
| DAA 阶段 A：CU 布局与既有页面 | `owner_accepted` | [DAA-001 r1 spec](automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md) | Human Owner 于 2026-10-17 验收 r1；新的 fresh Verification 通过，F-001/F-002 关闭，原失败历史保留。仅阶段 A 布局与既有功能兼容，B/C 实施另批。 |
| DAA 阶段 B：本地采集闭环 | `qa_passed` | [DAA-002 r2 spec](automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/spec.md) | 独立QA4已通过受控阶段B的AC01–AC20，F-001–F-004均已解除，全部失败历史及76份原样本保留。待Human Owner最终验收；缺省legacy模式保持，阶段C、Backend/SMA、DS联调及真实现场动作仍排除。 |
| DAA SQLite 唯一入口与 YAML 迁入 | `qa_passed` | [DAA-003 r1 spec](automation-world/data-acquisition-agent/plans/DAA-003-sqlite-only-startup/spec.md) | 新的独立QA2已通过，[checklist](automation-world/data-acquisition-agent/plans/DAA-003-sqlite-only-startup/checklist.md) 确认F-001/F-002解除并完整保留QA1失败历史。普通入口采用唯一SQLite，YAML仅首次空实例迁入停用草稿，已有配置/历史优先保留。必要增量与原受控原生保存重开证据已核准，自有测试进程/15191已释放、证据保留；Human Owner最终验收待定。 |
| DAA 迁入提示收敛与最小源码导入验证 | `qa_passed` | [DAA-004 r1 spec](automation-world/data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/spec.md) | 新的独立Verification通过AC01–AC08，有限README/界面调整及受控三点DB/UDT导入闭环已完成；操作差异和观察限制保留，已有配置/历史与SQLite防重回执保持。待Human Owner最终验收；阶段C和真实TIA/PLC联调仍属范围外。 [checklist](automation-world/data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/checklist.md) |
| DAA 多DB导入与嵌套辅助偏移 | `owner_accepted` | [DAA-005 r1 spec](automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) | Human Owner已于2026-10-19最终验收精确DAA-005 r1，独立QA2已通过AC01–AC13。本次仅验收收尾，原失败和原生证据保留，未追加测试或实现改动。 [checklist](automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |
| DAA 点位技术命名与导入能力复用准备 | `owner_accepted` | [DAA-006 r3 spec](automation-world/data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md) | Human Owner于2026-10-20最终验收r3及另行DIRECT界面调整；独立AC01–AC20核验、原blocked历史及原生限度保留。验收源码已固定，临时资源已归档/清理；整体B、DS及阶段C门禁保持。 |
| 三界架构发展蓝本 | `qa_passed` | [ARCH-MULTI-001 spec](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | r2 [双语 ROADMAP](ROADMAP.zh-CN.md) 已交付；独立文档 QA 通过 AC1–AC10，待 Human Owner 最终审阅；未改代码 |
| AW Agent 工程前置初始化 | `owner_accepted` | [ARCH-AW-001 spec](plans/ARCH-AW-001-agent-foundation/spec.md) | CA 已迁入并冻结，DAA/SMA 初始化并可独立启动；定向复核通过，Human Owner 于 2026-10-14 接受 r1；本轮未追加测试；UI/SQLite 后续另立任务 |
| AW 白皮书与运行原理设计 | `owner_accepted` | [ARCH-AW-002 spec](plans/ARCH-AW-002-agent-runtime-design/spec.md) | r3 DS 增补独立 QA 通过 AC12–AC17，Human Owner 于 2026-10-18 验收 r3 文档；未开始代码实现；r2 文档 QA 保留为历史；未授权功能实施 |
| 通用 Docker 部署 | `developer_handoff` | [ARCH-DOCKER-002 spec](plans/ARCH-DOCKER-002-reusable-deployment/spec.md) | r2 实施完成；三份 Compose 静态检查通过，旧根入口已退下，待独立 Verification，运行验证另行批准 |
| 公开 Core 提取 | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | fresh-context Verification 通过 public-safe Core、smoke/dev/release-check 与清理审计后，Human Owner 已接受 r3 |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner 已接受单一 `d4e6f8a0b2c4` Core root 与十四表 source/static/no-DB 基线 |
| 空 volume Docker runtime 证明 | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | fresh-context Verification 通过隔离 MySQL 8.4.6 构建/迁移/健康/代理/清理证明后，Human Owner 已接受 r1 |
| 本地开发环境采用 | `owner_accepted` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | 固定名 dev runtime、后端健康/前端检查、bootstrap default-off 证明和失效 smoke 文档清理完成后，Human Owner 已接受 r4 |
| 1.0.0 源码定版 | `owner_accepted` | [ARCH-REL-001 spec](plans/ARCH-REL-001-source-release-1.0.0/spec.md) | fresh-context Verification 已通过 r3，Human Owner 已接受；§5.4 main-only governance receipt 已准备但仍待 Human Owner 手工 push |
| 前端模块组装 | `draft` | [ARCH-FE-001 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | manifest 驱动的菜单/权限组装；不并入 Core 提取 |
| 项目前端角色权限与模块首批接入 | `owner_accepted` | [ARCH-FE-002 spec](plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md) | r4 品牌、配置、启动、构建与公开浏览器检查已独立通过；保留 r2/r3 历史，Human Owner 已于 2026-10-09 接受 r4，其他模块预留 003 |
| 剩余前端模块 manifest 适配 | `owner_accepted` | [ARCH-FE-003 spec](plans/ARCH-FE-003-remaining-module-manifest-adaptation/spec.md) | r2 价格页直调 auxiliary API；模块检查、36 项测试及隔离构建独立验证通过，Human Owner 于 2026-10-12 接受 r2，并确认 env 页面权限显示测试正常；保留 r1 历史 |
| 前端系统名称与小标题配置 | `owner_accepted` | [ARCH-FE-004 spec](plans/ARCH-FE-004-system-name-env-configuration/spec.md) | r3 独立静态复核通过后，Human Owner 于 2026-10-10 反馈测试无误并接受；保留 r1/r2 历史与原始证据 |
| 后端角色 API 权限配置 | `qa_passed` | [ARCH-BE-001 spec](plans/ARCH-BE-001-role-api-permissions/spec.md) | r3 已恢复十一组英文 env 标题；配置值和逐项注释保留；独立 QA 通过；待 Human Owner 最终验收 |
| 能源价格后端 API | `owner_accepted` | [ARCH-BE-002 spec](plans/ARCH-BE-002-energy-price-api/spec.md) | r3 已批准在本仓库实施可复用 auxiliary；三个 API、独立权限与显式迁移；独立 QA 通过，Human Owner 已于 2026-10-13 验收 r3，真实数据库操作另行授权 |
| 映射 Service API 试点 | `qa_passed` | [ARCH-BE-003 spec](plans/ARCH-BE-003-mapping-service-api-pilot/spec.md) | r3 A/B 独立通过：当前源码 483 通过/30 未选及编译通过，两轮 MySQL 各三场景全部通过；F-001/B-001 关闭，专用资源和测试口令已清理，待 Human Owner 最终验收 |
| 小时价格与按日历史 | `owner_accepted` | [ARCH-BE-004 spec](plans/ARCH-BE-004-energy-price-hourly-history/spec.md) | r2 独立 QA 通过：211 后端、38 前端及浏览器验证；F-001 已关闭，Human Owner 于 2026-10-13 完成人工试用并接受；真实数据迁移另行授权 |
| 后端业务模块回迁修复 | `owner_accepted` | [ARCH-BE-005 spec](plans/ARCH-BE-005-backend-business-module-reintegration/spec.md) | 独立 A 及两轮隔离 MySQL 各五场景通过，专用资源已清理；Human Owner 于 2026-10-16 最终验收 r3 |
| 映射业务 API 扩展 | `qa_passed` | [ARCH-BE-006 spec](plans/ARCH-BE-006-mapping-business-api-expansion/spec.md) | A+B 独立验证通过；两轮专用 MySQL 及五页浏览器检查完成，资源与测试秘密已清理；155 项相关测试通过，四项历史冻结 profile 失败保留；Human Owner 最终验收 pending |
| CA 打包配置 | `draft` | [CA-CONFIG-001 spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | 数据库类型/地址设置与 YAML 上传界面 |

## 延后边界

ARCH-MIG-001 r1、ARCH-DOCKER-001 r1 与 ARCH-DEV-001 r4 均已获 Human Owner 接受。MIT license 及其中
声明的 ownership 已保留，但生产 Docker 拓扑、真实 PLC/CA 操作和项目模块迁移继续作为独立 Human Owner
gate。ARCH-REL-001 r3 已在 fresh-context Verification 记录 `qa_passed` 且 Human Owner final acceptance
后达到 `owner_accepted`；r1/r2 Development 记录及 r2 main preparation commit 作为 superseded 历史
保留。六路径 §5.4 main-only governance receipt 已准备，但仍待 Human Owner 手工 staging、commit、
push；该状态不代表 GitHub Release、部署或 production readiness。

本文件只做简短索引；详细范围、命令和证据归属各自任务三文件。
