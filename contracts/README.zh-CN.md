<!--
  File Path: /contracts/README.zh-CN.md
  Description: 跨角色开发契约中枢索引
  Main Features:
    - 定义 demand、published contract 与 gate 边界
    - 区分前端 API 契约与 control-agent runtime 契约
-->
# 契约中枢

[English Version](README.md)

`contracts/` 是本项目用于跨角色、跨进程开发的项目级契约中枢。

它记录：

- 消费方需要什么能力。
- 提供方承诺暴露什么能力。
- 最终实现由哪个 source of truth 负责。
- 哪个门禁证明这份契约已经可以被实现或消费。

本目录不替代 OpenAPI、Pydantic schema、Alembic migration 或 `control-agent` 命令表契约。它是指向这些真相源的协作层。

## 目录地图

| 路径 | 用途 |
| --- | --- |
| `demands/` | 消费方在实现前提出的能力需求。消费方可以是 `frontend-js`、`control-agent`、第三方客户端、后端服务或外部系统。 |
| `published/` | 提供方承诺的契约。提供方可以是后端 HTTP API、runtime 数据库契约、命令任务、事件或后续外部适配器。 |
| `gates/` | 判断契约是否可以进入实现或消费的就绪检查。 |

## 状态模型

每份契约应使用以下状态之一：

| 状态 | 含义 |
| --- | --- |
| `proposed` | 消费方提出能力需求，但提供方尚未接受具体形态。 |
| `accepted` | 提供方接受方向，可以进入实现或发布契约。 |
| `implemented` | 代码已经存在，但验证可能尚未完成。 |
| `verified` | 测试、构建、联调或人工验收已经证明契约可用。 |
| `deprecated` | 契约已被替代或不再使用。 |

## 边界规则

- 后端 HTTP API 仍是业务和第三方集成入口。
- `control-agent` 的内部现场 runtime 行为可以使用明确的数据库直连契约。
- 后端 API 不得变成直接遥控运行中 `control-agent` 的入口。
- HTTP 响应结构、schema alias、错误码和 OpenAPI 真相源仍属于后端代码。
- 数据库结构真相源仍属于 SQLAlchemy model 和 Alembic migration。
- 契约文档必须反向链接到对应真相源。

## 当前活跃契约线索

| 线索 | 消费方 | 提供方 | 状态 |
| --- | --- | --- | --- |
| [高危授权门禁](demands/control-agent/high-risk-authorization-gate.zh-CN.md) | `control-agent` | 后端 HTTP API | `accepted` |
| [control-agent 授权校验 API](published/http-api/control-agent-authorization-verify.zh-CN.md) | `control-agent` | 后端 HTTP API | `implemented` |
| [control-agent 前置门禁](gates/control-agent-preflight.zh-CN.md) | 项目交付 | 后端 + `control-agent` | `proposed` |
| [AW事实集成](demands/automation-world-facts-integration.zh-CN.md) · [English](demands/automation-world-facts-integration.md) | DAA／SMA／HTTP消费者 | Backend事实与typed业务模块 | `proposed`；仅ARCH-AW-008文档范围 |

## PLC事实provider v2

[PLC facts v2](published/http-api/plc-facts-v2/README.zh-CN.md)定义每次提交一个 PLC/DB 完整样本及授权原值查询。源码和隔离验证由 [ARCH-BE-012 r4](../plans/ARCH-BE-012-simplified-plc-facts/tasks.md)记录。

## PLC事实provider v1

[PLC facts v1](published/http-api/plc-facts-v1/README.zh-CN.md)是已退役匿名 batch/latest/history 源码的历史合同，固定严格Decimal JSON、可靠结果、安全发布游标及有限保留。固定源码合同及获批隔离MySQL A+B验证归[BE-009](../plans/ARCH-BE-009-backend-facts-integration/checklist.md)。Owner终验/provider-ready、实际数据库采用、DAA联调和部署分别保留。


[业务集成v1](published/http-api/business-integration-v1/README.zh-CN.md)发布八路typed匿名业务入口、闭合schema、样例和摘要向量。[BE-010 r2](../plans/ARCH-BE-010-anonymous-business-integration/checklist.md)已通过获批隔离A+B验证；Owner终验、真实目标/时间采用及DAA/SMA接线待定，默认仍关闭/未采用。AW需求保留自身proposed状态，不据此声称这些provider不存在。

## 通用任务流程候选合同

[通用任务流程 v1](published/http-api/generic-task-workflow-v1/README.zh-CN.md)保存 ARCH-TASK-001 r1 实际注册的计划/实绩源码合同和 A/B 合成样例。业务集成 v1 的四条历史实绩操作随本候选退出，设备和监控操作保留。部署、独立验证和 Human Owner 终验分别进行。
