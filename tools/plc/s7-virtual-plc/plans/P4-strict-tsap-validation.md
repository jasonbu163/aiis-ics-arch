<!--
  File Path: /tools/plc/s7-virtual-plc/plans/P4-strict-tsap-validation.md
  Description: S7 虚拟 PLC 严格 TSAP rack/slot 身份校验计划
  Main Features:
    - 固化模拟器的 PLC 身份、COTP called-TSAP 校验与拒绝语义
    - 定义与 CA C5/C5.9 的匹配和不匹配联调证据
    - 保留真实 PLC 设备验收边界
-->
# P4 严格 TSAP rack/slot 身份校验实施计划

## 状态

已实现 / 开发验证通过（2026-07-16）。本文是 `tools/plc/s7-virtual-plc/` 的 P4 权威任务记录；实现、工具测试和 CA 的只读匹配 / 不匹配联调证据均已完成。

返回工具驾驶舱：[PLAN.zh-CN.md](../PLAN.zh-CN.md)。

## 目标

让虚拟 PLC 在 S7 ISO-on-TCP/COTP 建连阶段表现为一个有明确 rack/slot 身份的目标端：CA 或其他客户端只有带着与模拟器配置一致的 **called TSAP** 才能获得 COTP confirm 并开始 S7 DB 读取；rack 或 slot 不一致、called TSAP 缺失或畸形时，服务端必须在任何 DB 读取前关闭该会话。

这项工作解决当前 python-snap7 server 接受任意 COTP connection request 的缺口。它不把模拟器配置并入 CA `.env`，也不改变 C5.9 的“CA 空 endpoint env 回退 YAML、完整单 PLC env 覆盖”的解析规则。

## 已接受协议与配置合同

### 1. 模拟器身份独立于 CA

- 新增工具自有环境变量：`PLC_SIM_RACK`、`PLC_SIM_SLOT`，并在 `.env.example` 以当前开发合同写明 `0`、`1`。`PLC_SIM_PLC_KEY` 继续选择模拟的 PLC/group/point 合同。
- `serve` 与 `dry-run` 都必须解析并显示同一份身份；命令行可提供 `--rack`、`--slot` 作为单次显式覆盖。优先级固定为 `CLI > 工具环境变量 > 工具 .env`，不得读取或推导 CA 的 `CONTROL_AGENT_PLC_*`。
- rack/slot 在最终解析时必须存在、为十进制整数、非负，并能编码进 S7 TSAP；无效、溢出或部分配置必须以稳定的配置错误失败，不能回退为隐式 `0/1` 或让 Python traceback 泄漏为运行合同。
- `PLC_SIM_PLC_KEY` 必须精确命中 `plc_points.yaml` 顶层 key。当前“找不到就取第一个 PLC”的 loader 回退必须移除；未知 key 在 `dry-run` 和 `serve` 均 fail closed。
- 模拟器 rack/slot 必须与该精确 PLC key 在 `plc_points.yaml` 中声明的 rack/slot 一致。此比较只校验 rack/slot：虚拟服务使用本地开发端口是有意的，不要求复用 YAML 的 IP 或 port。
- 一个 `serve` 进程只模拟一个 `PLC_SIM_PLC_KEY + rack + slot` 身份；多个 PLC 以多个进程和端口启动，不在单端口上混合多个 TSAP 身份。

### 2. 严格握手语义

客户端 COTP connection request 的 `C2` 参数是 called TSAP。服务端按以下公式计算目标身份：

```text
expected_called_tsap = 0x0100 + rack * 0x20 + slot
```

- 只校验 `C2`，且长度必须恰为两个字节；`C1`（calling TSAP）由客户端决定，不作为拒绝条件。
- `C2` 缺失、截断、长度错误、无法解析或数值不等于 `expected_called_tsap` 时，不发送 COTP connection confirm，直接关闭 socket；不能注册 DB read、不能进入 S7 PDU 处理。
- 接收时走当前正常 server path，保持现有 DB area、profile 和读取行为。
- 启动摘要必须稳定输出 `plc_key`、port、rack、slot、expected called TSAP、DB area 数、点位数和 profile 来源。拒绝日志只记录安全的事件名与 expected/received TSAP，不记录凭据或 payload。

### 3. 配置与依赖边界

- `PLC_SIM_HOST` 不进入本任务；当前本地监听约定保持不变。
- 不增加 S7 写入、CPU 仿真、多个 TSAP 共端口或 CA 运维 UI。
- 实现必须位于工具源码，不能修改项目 `.venv` 中的 `python-snap7` 文件。若严格 adapter 需要继承或组合 python-snap7 3.x 的 server internals，`tools/pyproject.toml` 必须将依赖限制在已验证的 3.x 兼容范围，并由测试保护升级风险。
- P4 只证明 CA 与虚拟 PLC 的标准 TSAP 配置契约；真实 CPU rack/slot、网关、optimized access、连接资源、授权和现场网络仍需真实设备验收。

## 变更地图

| 位置 | 预期变更 | 不做什么 |
| --- | --- | --- |
| `.env.example` | 增加 `PLC_SIM_RACK=0`、`PLC_SIM_SLOT=1` 及严格身份说明。 | 不复制 CA endpoint env。 |
| `src-python/core/` | 增加身份解析、精确 PLC key 校验、TSAP 计算/解析和严格 server adapter。 | 不编辑 `tools/.venv`。 |
| `src-python/cli/` | 为 `dry-run` / `serve` 增加 rack/slot 参数、统一解析和启动摘要。 | 不恢复隐式启动或旧 action flags。 |
| `tests/` | 增加配置、COTP parser 和本地 socket/S7 client 联调测试。 | 不把真实 PLC 作为自动化测试依赖。 |
| `tools/pyproject.toml` | 把 python-snap7 范围收敛到经 P4 测试的 3.x 接口。 | 不为工具引入额外运行时包。 |
| `README.*`、`docs/PLC_TO_BUSINESS_SOP.*` | 实现后同步环境变量、命令、证据与真实设备边界。 | 本次计划落盘不提前改写当前使用说明。 |
| `control-agent/plans/C5-plc-collection.md`、`C5.9-ca-plc-endpoint-resolution.md`、`control-agent/PLAN.*` | 将 P4 连接为 C5.6/C5.8/C5.9 的虚拟联调前置证据。 | 不新建 CA Rust 实现任务，不改 C5.7 身份边界。 |

## 实施任务与验收

### P4.1 解析模拟器身份与精确 PLC 合同

1. 定义一个纯值的 simulator identity（`plc_key`、rack、slot、port、expected called TSAP），供 `dry-run` 和 `serve` 共用。
2. 在读取 profile 或启动 socket 前校验 key、rack、slot 和 YAML rack/slot 一致性；错误要指出字段与 PLC key，但不输出环境中无关内容。
3. 修改 loader，使未知 `PLC_SIM_PLC_KEY` 立即失败，移除“第一个 PLC”回退。
4. 更新 `.env.example`，并在实现完成后更新 README/SOP 的单进程单身份约定。

验收测试：

- 完整 `PLC_SIM_PLC_KEY=PLC_1`、rack `0`、slot `1` 可生成身份与 expected TSAP `0x0101`。
- 未知 PLC key、缺失 rack/slot、非整数、负值、不可编码值、只提供其中一项，以及与 YAML 不一致的 rack/slot 都稳定失败。
- CLI 覆盖、环境变量和工具 `.env` 的优先级可由单元测试证明；`dry-run` 与 `serve` 输出同一解析结果。

### P4.2 在 COTP connection request 前实施严格 called-TSAP 校验

1. 将 COTP connection request 的参数解析为受限的纯函数，安全提取 `C2`。不得假设参数顺序，不得越界读取。
2. 在工具自有 strict server adapter 中，于 COTP confirm 前调用该函数。只有与 expected TSAP 相等的 `C2` 才进入现有 python-snap7 server 建连路径。
3. 不匹配路径关闭连接并写安全结构化日志；不得生成伪造的 S7 成功或在同一会话中继续处理。
4. 用私有 adapter 隔离 python-snap7 3.x internals，避免把实现散落到 CLI 或 runtime loop。

验收测试：

- `C2=0x0101` 在 rack `0`/slot `1` 时接受。
- slot 不同、rack 不同、`C2` 缺失、`C2` 长度非二、截断和不完整参数均被拒绝；改变 `C1` 不导致拒绝。
- 本地临时服务的 S7 client 使用 `0/1` 可以读取一个已注册 DB；同一服务使用 `0/2` 在 DB read 前失败。测试不得依赖固定端口或常驻进程。

### P4.3 命令面、日志与回归文档

1. `dry-run` 和 `serve` 都接受 `--rack` / `--slot`，帮助文本清楚标注其是虚拟 PLC 端的身份，不是 CA 覆盖。
2. 启动摘要与 TSAP 拒绝日志采用稳定、可搜索字段；未匹配时不输出 profile payload 或数据库内容。
3. 更新 README、中文 README、PLC-to-business SOP 双语版和工具 PLAN 验证锚点，明确“TCP 可达”不是 rack/slot 证据。
4. 因严格 adapter 依赖 python-snap7 3.x internals，复核并更新项目依赖范围，再运行整个工具测试集。

验收命令（实现时以项目实际解释器为准）：

```bash
cd tools && uv run python -m py_compile plc/s7-virtual-plc/main.py plc/s7-virtual-plc/src-python/cli/commands.py plc/s7-virtual-plc/src-python/core/config.py plc/s7-virtual-plc/src-python/core/identity.py plc/s7-virtual-plc/src-python/core/loader.py plc/s7-virtual-plc/src-python/core/runtime.py plc/s7-virtual-plc/src-python/core/strict_server.py
cd tools && uv run python -m unittest discover plc/s7-virtual-plc/tests
cd tools && uv run python plc/s7-virtual-plc/main.py dry-run --rack 0 --slot 1
git diff --check
```

### P4.4 CA C5/C5.9 联调证据（不改 CA 实现）

在 P4.1-P4.3 通过后，启动虚拟 PLC 为 `PLC_1 / rack 0 / slot 1`。用 CA 的 rust-snap7 路径做两组只读优先验证：

1. **匹配组：** CA 解析到 `0/1` 时，实际读取配置的 DB group 成功；随后按 C5.6/C5.8 需要，在已授权的写库 smoke 中证明 raw 增长、latest 刷新和 policy payload 范围正确。
2. **不匹配组：** 仅让 CA 使用 `0/2`，保持其余 host/port/profile 不变。采集或样本读取必须在服务端握手处失败，状态记录可诊断错误，且 read-only 验证期间 `raw_snapshots_written=0`、`latest_snapshots_written=0`；若使用写库 smoke，还必须用只读查询证明 raw/latest 行数未变化。

建议命令轮廓（实际数据库凭据只由本地 ignored `.env` 提供，不能写入计划或日志）：

```bash
# terminal A: P4 implementation's strict virtual PLC, with the reviewed local profile
cd tools && uv run python plc/s7-virtual-plc/main.py serve --rack 0 --slot 1 --port 1102

# terminal B: matching CA diagnostic / collection evidence
CONTROL_AGENT_PLC_COLLECTION_ENABLED=true CONTROL_AGENT_PLC_COLLECTION_WRITE_ENABLED=false CONTROL_AGENT_PLC_DRIVER=rust_snap7 CONTROL_AGENT_PLC_HOST=127.0.0.1 CONTROL_AGENT_PLC_PORT=1102 CONTROL_AGENT_PLC_RACK=0 CONTROL_AGENT_PLC_SLOT=1 pnpm --dir control-agent plc:collect-once

# terminal B: mismatching evidence; it must not obtain an S7 DB read
CONTROL_AGENT_PLC_COLLECTION_ENABLED=true CONTROL_AGENT_PLC_COLLECTION_WRITE_ENABLED=false CONTROL_AGENT_PLC_DRIVER=rust_snap7 CONTROL_AGENT_PLC_HOST=127.0.0.1 CONTROL_AGENT_PLC_PORT=1102 CONTROL_AGENT_PLC_RACK=0 CONTROL_AGENT_PLC_SLOT=2 pnpm --dir control-agent plc:collect-once
```

该验收复用已实现的 C5.9 endpoint resolver；P4 不让 CA 读取模拟器 `.env`，也不把“错误 rack/slot”改成 endpoint resolver 的额外业务规则。TCP probe 只能说明端口可达，不能替代这两组 S7 实际读取/拒绝证据。

## 实施与验证记录（2026-07-16）

- 新增 `core/identity.py`，以精确 YAML `plc_key`、rack、slot、port 生成唯一模拟器身份和 expected called TSAP；未知 key、缺失 / 非法 / 越界或与 YAML 不一致的 rack/slot 都 fail closed。
- 新增 `core/strict_server.py`。它只在工具源码内替换 python-snap7 3.x 的 ISO connection 构造点；纯函数会验证 COTP CR 长度、恰有一个长度为 2 的 `C2`，并允许 `C1` 任意值和参数重排。拒绝路径不发送 COTP confirm，也不进入 DB request loop。
- `dry-run` 与 `serve` 都接受 `--rack`、`--slot`、`--port`，并按 `CLI > OS env > 工具 .env` 解析。启动摘要和拒绝日志含稳定的 `plc_key`、rack、slot、port、`expected_called_tsap` 字段；`.env.example`、README/SOP 与 `python-snap7>=3.0,<4` 已同步。
- 工具验证：`tools` 运行时的 25 个测试通过，覆盖 COTP parser、CLI/env 优先级、精确 key、YAML / port 身份错误、错误配置先于 profile 失败、畸形 COTP 不发 confirm / 不读 DB，以及本地临时 S7 server 的 `0/1` DB read 成功和 `0/2`、`1/1` 拒绝且无 DB read。
- 实际 CA 只读联调：用临时本地 `127.0.0.1:11102` 严格服务，`0/1` 的 `rust_snap7` collection 成功读取 6 个 DB group、1314 个点，`raw_snapshots_written=0`、`latest_snapshots_written=0`；仅改 slot 为 `2` 后 6 个 group 均 failed，两个写入计数仍为 `0`。模拟器为每次拒绝记录 `expected_called_tsap=0x0101 received_called_tsap=0x0102`，没有进入 DB read。

## 完成定义

P4 只有在以下全部成立时才可标记为“已实现 / 开发验证通过”：

- 工具 `.env.example`、CLI、dry-run、serve、README/SOP 和依赖约束一致说明 simulator-owned rack/slot；未知 PLC key 与不完整/无效身份均 fail closed。
- 正确 `C2` 可完成一次真实 S7 DB read；错误 rack、slot 或畸形 `C2` 在 COTP confirm 前被服务端关闭，且测试可重复证明。
- CA 对同一虚拟 PLC 的 `0/1` 成功和 `0/2` 拒绝均保留脱敏运行证据；错误配置不能写 raw/latest。
- 工具单元/联调测试、CA 所需聚焦验证、文档链接和 `git diff --check` 通过。

## 明确不在范围内

- 真实 Siemens CPU、网络网关、optimized DB access、连接资源、授权客户端或现场安全验收。
- CA-PC 身份字段、C5.7 跨生产线 `plc_key -> device_id` 配对，以及 B6 Projection 映射。
- 用 `coil_no` 或任何业务点位推断 rack/slot；它们属于不同层次的合同。
