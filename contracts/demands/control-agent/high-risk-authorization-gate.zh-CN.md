<!--
  File Path: /contracts/demands/control-agent/high-risk-authorization-gate.zh-CN.md
  Description: control-agent 高危授权需求
  Main Features:
    - 记录消费方侧门禁需求
    - 定义 control-agent 期望的最小授权数据
-->
# 高危授权门禁需求

[English Version](high-risk-authorization-gate.md)

## 契约元信息

| 字段 | 值 |
| --- | --- |
| 状态 | `accepted` |
| 消费方 | `control-agent` |
| 候选提供方 | 后端 HTTP API |
| 需求来源 | `control-agent/docs/COMMAND_CONTRACT.zh-CN.md` |
| 实现 owner | 先后端实现，再由 `control-agent` 接入客户端 |
| 门禁 | `contracts/gates/control-agent-preflight.zh-CN.md` |

## 需求

`control-agent` 在未来高危本地动作产生现场副作用前，需要调用上位授权校验。

动作由操作员在本地发起。后端或上位系统负责校验该动作是否允许。后端不得直接调用运行中的 agent，也不得代替 agent 执行动作。

## 最小请求数据

| 字段 | 含义 |
| --- | --- |
| `operatorUserId` | 使用 gate token 的后端用户 id。 |
| `operatorUsername` | 使用 gate token 的后端用户名。 |
| `actionScope` | 稳定动作 key，例如 `authorization.self_test` 或未来高危动作 key。 |
| `resourceId` | 目标资源标识，例如 `control-agent`、`plan:123` 或设备 key。 |
| `payloadHash` | 动作 payload 或摘要的 hash，用于防重放绑定。 |
| `temporaryToken` | 后端签发的门禁 token，通过授权请求头传递。 |

## 最小响应数据

| 字段 | 含义 |
| --- | --- |
| `allowed` | 布尔型允许 / 拒绝结论。 |
| `decision` | 稳定决策 key：`allowed`、`denied`、`expired`、`invalid_token`、`scope_not_allowed` 或 `not_configured`。 |
| `approvalId` | 允许时返回的稳定授权 id。 |
| `operatorUserId` | 后端校验后的授权操作员用户 id。 |
| `operatorUsername` | 后端校验后的授权操作员用户名。 |
| `actionScope` | 已授权动作范围。 |
| `resourceId` | 已授权资源 id。 |
| `payloadHash` | 接受后回显的 payload hash。 |
| `expiresAt` | 授权过期时间。 |
| `failClosed` | 高危动作默认必须为 true，除非另有单独的紧急例外文档。 |

## 非目标

- 本需求不要求提供遥控 `control-agent` 的 API。
- 本需求不要求后端执行命令动作。
- 本需求不把 command claim、heartbeat、resource lock 或 execution checkpoint 移入 HTTP 请求线程。

## 验收

- 后端发布授权校验契约。
- 只有最高权限用户组可以签发临时门禁 token。
- gate token 签发者必须是 `admin`。
- gate token 接收者可以是 `admin` 或 `supervisor`，且必须同时用 id 和 username 指定。
- 门禁 token 不能由其他 operator user id 或 username 使用。
- 门禁 token 有效期为 1 到 12 小时。
- 无效、缺失、过期或无权限 token 默认 fail closed。
- 未知 action scope 默认 fail closed。
- 响应使用后端统一响应壳。
- 最终 CA 实现会在现场副作用前记录授权证据。
