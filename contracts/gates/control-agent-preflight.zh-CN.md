<!--
  File Path: /contracts/gates/control-agent-preflight.zh-CN.md
  Description: control-agent 门禁前置检查清单
  Main Features:
    - 跟踪 CA 授权接入前的后端就绪状态
    - 区分授权校验与命令执行
-->
# Control-Agent 前置门禁

[English Version](control-agent-preflight.md)

## 范围

本门禁用于判断项目是否已经可以为未来高危动作实现 `control-agent` 授权客户端。

它本身不批准真实现场动作执行。

## 后端就绪

- [x] `POST /api/v1/control-agent/gate-tokens` 已存在。
- [x] `GET /api/v1/control-agent/action-scopes` 已存在。
- [x] `POST /api/v1/control-agent/authorization/verify` 已存在。
- [x] 端点要求认证。
- [x] 端点要求与 control-agent 授权相匹配的权限。
- [x] 只有最高权限用户组可以签发门禁 token。
- [x] 门禁 token 以 hash 保存，明文只在签发响应中返回一次。
- [x] 门禁 token 通过 id 和 username 绑定明确的 `admin` 或 `supervisor` 目标用户。
- [x] 门禁 token 有效期限制为 1 到 12 小时。
- [x] service 验证中，授权操作员调用 `authorization.self_test` 返回 `allowed=true`。
- [x] 当前 self-test action scope 可通过后端注册表 API 发现。
- [x] service 验证中，未知 action scope 返回 `allowed=false`。
- [x] service 行为中，无效 token 默认 fail closed。
- [ ] 过期、撤销和数据库型 token 检查通过 API 测试。
- [x] 响应 data 包含 `allowed`、`decision`、`approvalId`、`operatorUserId`、`operatorUsername`、`actionScope`、`resourceId`、`payloadHash`、`expiresAt` 和 `failClosed`。
- [x] 响应 data 序列化为 camelCase。
- [x] 后端测试覆盖成功、拒绝、认证失败、权限失败和响应契约结构。
- [x] API 不创建、抢占、执行、取消、暂停、恢复或修复命令任务行。

## 契约就绪

- [x] 消费方需求已存在。
- [x] 提供方 API 契约已存在。
- [x] 契约已说明后端 API 是授权门禁，不是远程控制端点。
- [x] 契约已记录后端 action scope 注册表端点。
- [x] 后端 route 实现与 published contract 结构一致。
- [ ] 任何契约偏差都在 CA 实现前记录。

## Control-Agent 就绪

- [ ] CA 已有后端授权 URL 配置。
- [ ] CA 通过授权请求头发送 token，不写入日志或 query string。
- [ ] CA 发送 `operatorUserId`、`operatorUsername`、`actionScope`、`resourceId` 和 `payloadHash`。
- [ ] 当后端调用拒绝、超时、失败或返回无效数据时，CA 拒绝高危动作。
- [ ] CA 记录授权证据，但不写入原始密钥。
- [ ] CA 仍不把后端 API 当作命令执行路径。

## 验证命令

后端：

```bash
uv run pytest tests/test_control_agent_authorization.py tests/test_response_contract.py
```

Control-agent：

```bash
pnpm --dir control-agent build
cargo fmt --manifest-path control-agent/src-tauri/Cargo.toml --check
cargo test --manifest-path control-agent/src-tauri/Cargo.toml
```

仓库：

```bash
git diff --check
```
