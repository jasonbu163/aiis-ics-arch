# AIIS ICS Control Agent

## 流程编辑器

在本目录执行 `pnpm tauri dev`，打开流程编辑器并启用 S7 driver feature。pnpm 11 若提示 Vue 3 兼容层的可选构建步骤，可先执行 `pnpm --config.strict-dep-builds=false install --frozen-lockfile` 准备依赖。编辑器启动时不加载旧配置，数据保存在 CA 应用数据子目录 `flow-editor-v1`。

工作台支持打开已保存的流程版本。Vue Flow 编辑器支持拖拽、类型化连线、布局编辑和 JSON 交换。在「PLC 与点位」导入 DAA 或 DS 的原始点表，再分别绑定逻辑点位与 HTTP 目标。单节点测试默认模拟，确认解析后的目标才可调用 HTTP GET/POST 或读取 S7 的 INT 点位。PLC 写入仅可模拟。整流执行留待后续任务。

旧桌面进入方式为 `pnpm tauri dev -- --ca-legacy-console`。既有 headless 采集和独立运行时命令继续保留。下方兼容基线描述这些原有入口。

参阅[候选合同](../../contracts/demands/ca-field-flow-v1/README.zh-CN.md)及 [ARCH-AW-009 r2](../../plans/ARCH-AW-009-ca-flow-editor-json/spec.md)。

`automation-world/control-agent/` 是 AIIS ICS Architecture 配套的可选 Rust/Tauri 现场运行时
和本地运维控制台。它负责 PLC 采集以及后端拥有的 raw/latest 快照合同；它
不是第二套 Web 后端，也不替代后端模块注册机制。

## 公开基线

- `src/` 保存 Tauri 控制台和模块内翻译。
- `src-tauri/` 保存 Rust 运行时、只读 PLC 合同适配器和显式快照写入器。
- `config/plc_points.yaml` 与 `config/plc_snapshot_policy.yaml` 只是脱敏的
  结构示例。
- `.env.example` 默认关闭 PLC、数据库和端点探测门禁。

默认配置不包含客户端点、真实点位表、密钥或数据库 URL。现场启用任何
外部 I/O 前，必须提供单独审核过的现场配置。PostgreSQL/MSSQL 选择、YAML
上传和设置页面属于后续 `CA-CONFIG-001`，不属于当前基线。

## 本地检查

```bash
pnpm install
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml
```

以上只检查本地源码，不启动 Docker、不连接真实 PLC 或数据库，也不发布
构建产物。构建目录和依赖目录不纳入仓库。

## 运行边界

后端可以通过 Core API 暴露采集与快照状态；PLC 读取始终由常驻 Control
Agent 完成。数据库写入必须同时通过本地显式门禁和现场合同审核。任何 Web
请求都不能变成 PLC 轮询循环。

## 冻结兼容基线

CA 归属 [Automation World](../README.zh-CN.md)。ARCH-AW-001 r1 整体迁移本程序，不改运行时源码和应用身份。迁移验证后，[Development tasks](../../plans/ARCH-AW-001-agent-foundation/tasks.md) 中的 freeze receipt 固定本源码基线。后续采集工作进入 DAA；CA 不导入 DAA/SMA/shared 源码。冻结不停止现有 CA 运行，也不授权现场切换。历史任务证据仍保留于根 plans。
