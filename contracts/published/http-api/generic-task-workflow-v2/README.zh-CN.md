# 通用计划与实绩 HTTP API v2 候选

[English](README.md) · [OpenAPI](openapi.json) · [合成请求](examples/requests.json)

候选属于 ARCH-TASK-001 r3。接入前请核对目标环境实际合同。示例按顺序用于初始配置修订为 `1` 的临时数据夹具；实际采用环境先读取当前修订并登记合适的字段身份。

## 集成流程

1. 通过 `GET /api/v1/integration/task-field-configs?module=plan` 或 `module=performance` 读取当前字段定义。
2. 向 `POST /api/v1/integration/plans/upsert` 提交计划，最少填规范化任务号。业务值放在以稳定字段键索引的 `items`。
3. 通过 `GET /api/v1/integration/plans?productionStatus=new` 筛选并分页读取计划。现场处理由调用方决定。
4. 向 `POST /api/v1/integration/performances/upsert` 提交同号实绩。有同号计划时，实绩当前状态和本次提交且允许回写的共享值在同一事务更新计划。无计划时也可保存实绩。
5. 通过对应的 `/by-task/{taskNo}` 获取记录。收到 `task.commit_unknown` 时先按任务号 GET 对账，再决定是否重发。

生产状态固定为 `new`、`running`、`completed`、`error`。省略字段保留原值，可空字段提交 `null` 才清空，0、false 和空字符串均为值。提交自动采集项时使用本次观测时间，缺省时清空观测时间。仅状态且缺省观测时间时保留旧观测时间。业务时间输入须带时区，输出为上海时间。以成功处理顺序更新，已完成的任务可经下一次有效上报恢复生产中。

同号计划先存在时，首次保存实绩继承启用的订单快照字段。实绩先建也可通过普通计划 POST 补建，缺省不回填。显式 `backfillExisting` 请求回填允许回写的历史共享值，本次给定的计划值优先。

## 权限和切换

任务集成入口按项目可信网络边界开放，无需前端 Bearer 或登记生产者。`producerId` 是标签，`fieldConfigVersion` 只作信息。网页入口要求登录和对应角色授权，只有管理员可修改、删除字段定义。

[v1 合同](../generic-task-workflow-v1/README.zh-CN.md)保留原流程。客户端需把 `syncValues`、`localValues` 替换为当前 `items`。原领取、下发回执、计划状态动作和实绩专用补建 POST 返回 HTTP 410 和 `task.endpoint_retired`，新 OpenAPI 中隐藏。切换前逐一核对客户端。迁移设计保留历史业务值、下发批次和人工动作证据。

采集事实、设备观测及业务时间采用沿用各自目标守卫。源码允许 `ae20b4d6f831`，实际 profile 和有效采用证据仍须与真实目标精确一致。数据库迁移、服务切换和采用各自另行审批。
