# 项目文档

[English](README.md)

`docs/` 仅作为跨仓库与流程类长期文档的 README 结构支撑。其生命周期和状态由根目录 [PLAN](../PLAN.zh-CN.md) 管理；本目录不建立独立 PLAN 或任务登记表。

## 索引

| 文档 | 用途 |
| --- | --- |
| [多项目开发指南](multi-project-pm.md) | Core、复用模块仓和项目仓之间的长期边界与治理指引。 |
| [AW 白皮书与演进路线](AIIS_AW_Whitepaper_Roadmap_v0.4.md) | CAF/CU/DAA/SMA/CA 角色、近期本地配置与长期路线；中文设计正文。 |
| [AW 运行原理与详细设计](AIIS_AW_Runtime_Design.md) | SQLite、S7 点位、API、共享流程 Core 与设备执行/恢复的设计依据；非实现声明。 |
| [DAA 详细设计](AIIS_DAA_Detailed_Design.md) | 多 PLC、双 SQLite、有界最新优先补传及 Backend 最多三自然月窗口的中文目标设计；补充 CU 消费、工作台/配置页面、运行数据流、DB 包/批次示例与分阶段实施；不授权实现。 |
| [SMA 详细设计](AIIS_SMA_Detailed_Design.md) | 本地表单绑定、API 材料/手工目标、定义校验/转换、持久进度/outbox 与可靠业务 API 投递的中文目标设计；不授权实现。 |
| [DS 详细设计](AIIS_DS_Detailed_Design.md) | 004 r2已验收历史及已批005 r5产品MVP设计：DAA派生六页、单Rust runtime、typed导入/配置/apply、DS SQLite与自动验证；DEV实施证据与最新独立QA/Owner状态见所属tasks/checklist；DAA至SQLite联调另批，不倒记旧验收。 |


## 权威边界

- [`contracts/`](../contracts/) 继续作为根目录 Core 合同中心；合同不迁入 `docs/`。
- [`plans/`](../plans/) 负责保存任务范围、Development 证据、Verification 记录和 Human Owner 验收历史。
- 根目录或模块 README 与 `INITIALIZATION*.md` 负责稳定的运行、初始化指引；当前任务的 `tasks.md` 是发布操作唯一可复制命令与动态证据事实面。
- 本目录的变更由根目录 PLAN 跟踪。不要创建 `docs/PLAN*.md` 或 `docs/plans/`。
