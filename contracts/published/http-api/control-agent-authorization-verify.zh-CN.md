<!--
  File Path: /contracts/published/http-api/control-agent-authorization-verify.zh-CN.md
  Description: 计划中的后端授权校验 API 契约
  Main Features:
    - 定义 control-agent 授权的提供方 HTTP 契约
    - 将接口限制为校验，而不是远程执行
-->
# Control-Agent 授权校验 API

[English Version](control-agent-authorization-verify.md)

## 契约元信息

| 字段 | 值 |
| --- | --- |
| 状态 | `implemented` |
| 消费方 | `control-agent` |
| 提供方 | 后端 HTTP API |
| 已实现端点 | `GET /api/v1/control-agent/action-scopes`；`POST /api/v1/control-agent/gate-tokens`；`POST /api/v1/control-agent/authorization/verify` |
| 实现后的真相源 | 后端 route、schema 与 OpenAPI |
| 关联需求 | `contracts/demands/control-agent/high-risk-authorization-gate.zh-CN.md` |

## 动作 Scope 注册表端点

```http
GET /api/v1/control-agent/action-scopes
Authorization: Bearer <backendAccessToken>
```

已认证的 `admin` 和 `supervisor` 用户可以读取该注册表。`operator` 用户禁止读取。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "registryVersion": "2026-06-24-control-agent-gate-v1",
    "defaultScope": "authorization.self_test",
    "items": [
      {
        "actionScope": "authorization.self_test",
        "riskLevel": "self_test",
        "status": "implemented",
        "requiresGateToken": true,
        "defaultResourceId": "control-agent",
        "payloadHashStrategy": "fixed_self_test",
        "samplePayloadHash": "sha256:self-test-payload",
        "allowedSubjectRoles": ["admin", "supervisor"],
        "titleKey": "controlAgent.authorization.scope.selfTest.title",
        "descriptionKey": "controlAgent.authorization.scope.selfTest.description"
      }
    ]
  }
}
```

当前注册表刻意只发布 `authorization.self_test`。真实高危动作必须先进入这里，CA 或前端 UI 才能启用对应按钮。

## 签发门禁 Token 端点

```http
POST /api/v1/control-agent/gate-tokens
Authorization: Bearer <backendAccessToken>
Content-Type: application/json
```

只有最高权限用户组可以签发 token。签发者必须同时用 id 和 username 明确指定目标用户。

请求：

```json
{
  "subjectUserId": 2,
  "subjectUsername": "supervisor",
  "durationHours": 2
}
```

规则：

- `subjectUserId` 与 `subjectUsername` 必须指向同一个 active 后端用户。
- 目标用户角色必须是 `admin` 或 `supervisor`。
- `operator` 用户不能接收 gate token。
- `durationHours` 必须在 1 到 12 之间。
- 默认有效期为 2 小时。
- 响应只返回一次明文 token。
- 数据库只保存 `tokenHash`，不保存明文 token。
- token 绑定到 `subjectUserId` / `subjectUsername`；使用 token 时两个字段都要校验。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "gateToken": "<opaque-token>",
    "tokenId": 1,
    "subjectUserId": 2,
    "subjectUsername": "supervisor",
    "subjectRole": "supervisor",
    "issuedByUserId": 1,
    "issuedByUsername": "admin",
    "issuedByRole": "admin",
    "allowedScopes": ["authorization.self_test"],
    "resourceScope": "*",
    "expiresAt": "2026-06-24T12:00:00Z",
    "failClosed": true
  }
}
```

## 校验授权端点

```http
POST /api/v1/control-agent/authorization/verify
Authorization: Bearer <gateToken>
Content-Type: application/json
```

## 请求体

```json
{
  "operatorUserId": 2,
  "operatorUsername": "supervisor",
  "actionScope": "authorization.self_test",
  "resourceId": "control-agent",
  "payloadHash": "sha256:self-test-payload"
}
```

## 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allowed": true,
    "decision": "allowed",
    "approvalId": "auth-20260624-000001",
    "operatorUserId": 2,
    "operatorUsername": "supervisor",
    "actionScope": "authorization.self_test",
    "resourceId": "control-agent",
    "payloadHash": "sha256:self-test-payload",
    "expiresAt": "2026-06-24T12:00:00Z",
    "failClosed": true
  }
}
```

## 拒绝响应

业务拒绝仍应返回标准响应壳：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allowed": false,
    "decision": "scope_not_allowed",
    "approvalId": null,
    "operatorUserId": 2,
    "operatorUsername": "supervisor",
    "actionScope": "unknown.action",
    "resourceId": "control-agent",
    "payloadHash": "sha256:self-test-payload",
    "expiresAt": null,
    "failClosed": true
  }
}
```

认证失败沿用后端认证行为。权限失败沿用后端权限行为。

## 第一批允许范围

第一批允许的 scope 是：

```text
authorization.self_test
```

它只用于证明门禁链路，不启用任何现场动作。只有绑定同一个 operator user id 和 username 的 active gate token 才返回 `allowed=true`。

## 前端 / CA 使用说明

`gateToken` 是临时钥匙，它本身不等于某个动作的授权。

验证请求仍然必须携带明确的动作描述：

- `actionScope` 是后端发布的动作 key，必须来自 `GET /api/v1/control-agent/action-scopes` 或本契约。生产 UI 不应让用户随意输入字符串。
- `resourceId` 表示本次动作作用的目标资源。当前 self-test 固定使用 `control-agent`；未来可以是 `plan:123` 或 `device:line-1`。
- `payloadHash` 用于把授权校验绑定到本次动作 payload。当前 self-test 固定使用 `sha256:self-test-payload`；未来 CA client 应根据规范化 JSON payload 自动计算。

Swagger UI 测试说明：

1. 先用 admin 后台 access token 授权 Swagger。
2. 通过 `/control-agent/gate-tokens` 签发 gate token。
3. 将 Swagger 的授权 token 替换为响应中的 `gateToken`。
4. 调用 `/control-agent/authorization/verify`，请求体使用 `authorization.self_test`、`control-agent` 和 `sha256:self-test-payload`。

如果提交 Swagger 默认值，例如 `actionScope: "string"`，正确结果就是 `allowed=false` 且 `decision=scope_not_allowed`。

后续工作：

- 在业务动作、资源 id 和 payload hash 规则完成文档化后，把真实高危动作加入后端 action scope 注册表。
- 只有在第一批动作注册表稳定后，才扩展 token 签发时的 `allowedScopes` 和 `resourceScope`。
- 在动作注册表、payload hash 规范化和审计路径文档完成前，真实高危按钮保持禁用。

## 提供方规则

- verify API 只做授权校验。
- verify API 不得创建、抢占、取消、暂停、恢复或执行命令任务行。
- token 签发只保存 token hash。
- 低权限用户不能签发门禁 token。
- gate token 签发者必须是 `admin`。
- gate token 接收者可以是 `admin` 或 `supervisor`。
- gate token 接收者必须同时用 `subjectUserId` 与 `subjectUsername` 指定。
- action scope 注册表是只读接口，不得执行动作。
- API 不得连接 PLC 或现场设备。
- 响应 data 必须序列化为 camelCase。
- `failClosed` 必须为 true。
- 未知 scope 必须拒绝。

## 后端实现建议

已实现模块：

```text
backend/app/control_agent/
  api/routes.py
  schemas/authorization.py
  services/async_authorization.py
```

已实现测试：

```text
backend/tests/test_control_agent_authorization.py
```

当前验证备注：

- 模块编译通过。
- 直接 service 验证通过。
- FastAPI 路由注册包含已实现端点。
- 完整 API 测试被本地 MySQL root 测试库初始化阻塞。

## 验证

- 有效 admin 或 supervisor JWT 可以读取 action scope 注册表。
- `operator` 用户不能读取 action scope 注册表。
- 有效 admin JWT 可以给 active 的 `admin` 或 `supervisor` 目标用户签发 gate token。
- 有效 gate token + 匹配的 `operatorUserId` / `operatorUsername` + `authorization.self_test` 返回 `allowed=true`。
- 缺失或无效 gate token 返回 fail-closed 拒绝或被后端认证拒绝。
- 无权限用户不能签发 gate token。
- `operator` 用户不能接收 gate token。
- 未知 `actionScope` 返回 `allowed=false`。
- 响应壳包含 `code`、`message`、`data`。
- 嵌套 data 使用 camelCase 字段。
