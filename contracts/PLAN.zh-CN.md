<!--
  File Path: /contracts/PLAN.zh-CN.md
  Description: 契约中枢开发计划
  Main Features:
    - 跟踪契约中枢落地阶段
    - 连接 control-agent 门禁契约、后端实现与 CA 后续工作
-->
# 契约中枢计划

[English Version](PLAN.md)

本计划跟踪项目级契约中枢的落地。

## 当前证据 — 2026-11-05

| 合同线索 | 实际范围与下一gate |
| --- | --- |
| [ARCH-ACQ-003 r2](../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) | `owner_accepted`。Human Owner 于 2026-11-11 验收新版上报合同。DAA-010 接续使用采集 r2 合同工件。 |
| [PLC facts v2](published/http-api/plc-facts-v2/README.zh-CN.md) | ARCH-BE-012 r4 源码实施与隔离验证进行中。 |
| [PLC事实provider](published/http-api/plc-facts-v1/README.zh-CN.md) | BE-009源码及隔离MySQL A+B QA通过，Owner终验/provider-ready及真实采用待定。 |
| [typed业务provider](published/http-api/business-integration-v1/README.zh-CN.md) | BE-010 r2八路及隔离A+B QA通过，真实schema/时间采用及终验待定。 |
| [AW需求](demands/automation-world-facts-integration.zh-CN.md) | 文档仍proposed；AW008文档QA2通过、Owner文档终验待定，provider证据独立。 |
| 旧CA授权 | 原需求/provider/前置gate保留为历史输入，不证明新CA现场就绪。 |

下方K0–K3是早期契约中枢快照。旧MySQL root阻塞、migration head `b4c5d6e7f8a9`及迁移前路径属于历史，不是BE-009/010当前schema head或阻塞。源码迁移从 BE-009 `0a2c4e6f8b10` 经 BE-010 `1b3d5f7a9c20` 接至 BE-012 `2c4e6a8b0d12`，不据此断言实际数据库 revision。冻结CA当前路径为`automation-world/control-agent/`；新provider QA不替旧CA授予现场执行接受。

## 历史K0–K3记录

## 目标

建立一套可复用机制，支持 AI 开发后端、第三方开发前端、AI 开发前端、`control-agent` runtime 开发，以及后端 / Worker 交接。

第一条真实线索是 `control-agent` 高危授权门禁。

## 阶段 K0. 契约中枢基线

状态：进行中。

任务：

- [x] 创建 `contracts/README.md`。
- [x] 创建 `contracts/README.zh-CN.md`。
- [x] 创建 `contracts/PLAN.md`。
- [x] 创建 `contracts/PLAN.zh-CN.md`。
- [x] 定义目录分层：`demands/`、`published/`、`gates/`。
- [x] 记录状态生命周期：`proposed`、`accepted`、`implemented`、`verified`、`deprecated`。

验收：

- 目录解释清楚每一层契约的职责。
- 契约中枢不声称替代后端 schema、OpenAPI、migration 或 control-agent runtime 文档。

## 阶段 K1. Control-Agent 授权需求

状态：已接受。

任务：

- [x] 将现有 `control-agent` PLAN / COMMAND_CONTRACT 中的授权门禁需求提升为 demand 文档。
- [x] 保持需求由消费方拥有：`control-agent` 在未来高危动作前需要上位系统授权校验。
- [x] 保留边界：后端 API 只做授权校验，不远程执行 agent 动作。

验收：

- `contracts/demands/control-agent/high-risk-authorization-gate.zh-CN.md` 存在。
- 需求文档反向链接到 `control-agent/docs/COMMAND_CONTRACT.zh-CN.md`。

## 阶段 K2. 后端 Published API 契约

状态：已实现，本地 MySQL root 授权阻塞数据库型验证。

任务：

- [x] 定义计划中的后端 action scope 注册表、gate token 签发 API 与授权校验 API。
- [x] 记录请求、响应、权限、token 绑定、fail-closed 语义和真相源规则。
- [x] 增加 `control_agent_gate_tokens` 模型和 Alembic migration。
- [x] 实现后端 API 模块。
- [x] 增加后端测试，覆盖 action scope 注册表访问、token 签发、admin 给 supervisor 签发、拒绝、无效 token、操作者不匹配、低权限接收者禁止和响应结构。
- [ ] 本地 MySQL root 测试库初始化恢复后，重新运行后端 API 测试。

验收：

- `contracts/published/http-api/control-agent-authorization-verify.zh-CN.md` 存在。
- 最高权限用户可以给 active 的 `admin` 或 `supervisor` 目标用户签发临时 gate token，目标用户必须同时用 id 和 username 指定。
- `admin` 和 `supervisor` 用户可以读取后端 action scope 注册表；`operator` 用户被拒绝。
- gate token 只存 hash，绑定目标主体，有效期限制在 1 到 12 小时。
- 后端实现不创建遥控 `control-agent` 的 API。
- 数据库型验证恢复后，测试证明响应壳和 camelCase 字段正确。

历史验证备注：

- `uv run python -m compileall app/control_agent alembic/versions/20260624_1200_b4c5d6e7f8a9_add_control_agent_gate_tokens.py tests/test_control_agent_authorization.py tests/test_migrations.py` 通过。
- Alembic 脚本发现结果为单一 head：`b4c5d6e7f8a9`。
- FastAPI 路由注册包含 `/api/v1/control-agent/action-scopes`、`/api/v1/control-agent/gate-tokens` 和 `/api/v1/control-agent/authorization/verify`。
- `uv run pytest tests/test_migrations.py` 在测试执行前被同一个 MySQL root 授权错误阻塞。
- `uv run pytest tests/test_control_agent_authorization.py tests/test_response_contract.py` 在测试执行前被 MySQL root 授权阻塞：`Access denied for user 'root'@'169.254.169.254'`。

## 阶段 K3. Control-Agent 前置门禁

状态：已提出。

任务：

- [x] 创建第一版前置检查清单。
- [ ] 数据库型后端测试解除阻塞后运行检查清单。
- [ ] 只有在后端契约实现并验证后，才回到 `control-agent` 开发线程接入授权客户端。

验收：

- `contracts/gates/control-agent-preflight.zh-CN.md` 标明 CA 门禁开发前必须满足的检查。
- 门禁清单区分后端就绪与 CA 实现就绪。

<a id="验证命令"></a>
## 历史验证命令

以下原命令仅保留历史，不作为当前可复制操作指令；新验证按所属README/任务及具体批准执行：

```bash
uv run pytest tests/test_control_agent_authorization.py tests/test_response_contract.py
pnpm --dir control-agent build
cargo fmt --manifest-path control-agent/src-tauri/Cargo.toml --check
cargo test --manifest-path control-agent/src-tauri/Cargo.toml
git diff --check
```
