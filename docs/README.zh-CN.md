# 项目文档

[English](README.md)

`docs/` 仅作为跨仓库与流程类长期文档的 README 结构支撑。其生命周期和状态由根目录 [PLAN](../PLAN.zh-CN.md) 管理；本目录不建立独立 PLAN 或任务登记表。

## 索引

| 文档 | 用途 |
| --- | --- |
| [多项目开发指南](multi-project-pm.md) | Core、复用模块仓和项目仓之间的长期边界与治理指引。 |
| [采集数据模块原理与使用](acquisition-data-guide.zh-CN.md) | Web 来源登记、样本上报、后端存储及实时历史读取，适用于 DAA 与第三方。 |
| [计划与实绩通用任务机制讨论稿](generic-task-workflow-discussion.zh-CN.md) · [English](generic-task-workflow-discussion.md) | 整理 MES → CA/FF → PLC → DAA → SMA → 实绩 → 计划回写的讨论口径、建议与待定项，包含流程/状态/ER示意图、项目约定的PLC写入条件、字段、页面和接口示例；不作为实施spec或已发布合同。 |
| [设备状态与过程监控讨论稿](equipment-status-process-monitoring.zh-CN.md) · [English](equipment-status-process-monitoring.md) | ARCH-OBS-001 r6 审阅指南，涵盖两张值表、SMA 或第三方上报到落库和展示，以及[第三方哪些字段能省略或传 null](equipment-status-process-monitoring.zh-CN.md#third-party-ingest)。 |
| [AW 白皮书与演进路线](AIIS_AW_Whitepaper_Roadmap_v0.4.md) | 角色与分阶段路线；ARCH-AW-008对齐事实到业务的生命周期，不授权软件。 |
| [AW 运行原理与详细设计](AIIS_AW_Runtime_Design.md) | 采集、配置与执行边界；匿名事实集成及独立业务确认；中文设计正文。 |
| [DAA 详细设计](AIIS_DAA_Detailed_Design.md) | 已接受的受控阶段B基线；阶段C不可变双SQLite事实、有界最新优先上传、可靠回执与Backend读取／保留需求。 |
| [SMA 详细设计](AIIS_SMA_Detailed_Design.md) | 当前Rust/SQLite配置与纯预览阶段，正常投递关闭；清理/CU已接受，本地配置QA2通过待Owner，GET→POST/history/outbox仍另项。 |
| [AW事实集成共同需求](../contracts/demands/automation-world-facts-integration.zh-CN.md) · [English](../contracts/demands/automation-world-facts-integration.md) | proposed：匿名一写两读、JSON／可靠回执、逐点latest、安全history、上海三自然月及业务永久保存；需求状态独立于已实现provider及其隔离QA。 |
| [DS 详细设计](AIIS_DS_Detailed_Design.md) · [使用手册](../automation-world/device-simulator/USER_GUIDE.zh-CN.md) · [快速流程](../automation-world/device-simulator/USER_GUIDE.zh-CN.md#quick-start) | 手册覆盖创建实例/点位→确认→保存草稿→保存为版本→停机加载→启动，以及[版本切换/回退](../automation-world/device-simulator/USER_GUIDE.zh-CN.md#switch-version)、单个/批量删除、多DB/UDT导入和策略编辑。2026-10-27的DS-001 r1、ARCH-AW-005 r5验收与原DEV/QA历史保持原范围，独立QA仅DS-001例外未执行；受控DAA–DS S7→SQLite联调已于10月30日独立接受；10月29日DS草稿/版本增量仍保持DEV自检/人工确认边界，阶段C另项。 |
| [事实provider](../contracts/published/http-api/plc-facts-v1/README.zh-CN.md) / [业务provider](../contracts/published/http-api/business-integration-v1/README.zh-CN.md) | 固定源码合同及独立通过的隔离MySQL A+B范围；Owner终验、真实采用及DAA/SMA接线待定。 |


## 权威边界

- [`contracts/`](../contracts/) 继续作为根目录 Core 合同中心；合同不迁入 `docs/`。
- [`plans/`](../plans/) 负责保存任务范围、Development 证据、Verification 记录和 Human Owner 验收历史。
- 根目录或模块 README 与 `INITIALIZATION*.md` 负责稳定的运行、初始化指引；当前任务的 `tasks.md` 是发布操作唯一可复制命令与动态证据事实面。
- 本目录的变更由根目录 PLAN 跟踪。不要创建 `docs/PLAN*.md` 或 `docs/plans/`。
