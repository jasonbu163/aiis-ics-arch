# 项目文档

[English](README.md)

`docs/` 仅作为跨仓库与流程类长期文档的 README 结构支撑。其生命周期和状态由根目录 [PLAN](../PLAN.zh-CN.md) 管理；本目录不建立独立 PLAN 或任务登记表。

## 索引

| 文档 | 用途 |
| --- | --- |
| [多项目开发指南](multi-project-pm.md) | Core、复用模块仓和项目仓之间的长期边界与治理指引。 |

## 权威边界

- [`contracts/`](../contracts/) 继续作为根目录 Core 合同中心；合同不迁入 `docs/`。
- [`plans/`](../plans/) 负责保存任务范围、Development 证据、Verification 记录和 Human Owner 验收历史。
- 根目录或模块 README 与 `INITIALIZATION*.md` 负责稳定的运行、初始化指引；当前任务的 `tasks.md` 是发布操作唯一可复制命令与动态证据事实面。
- 本目录的变更由根目录 PLAN 跟踪。不要创建 `docs/PLAN*.md` 或 `docs/plans/`。
