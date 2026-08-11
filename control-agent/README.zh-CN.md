# AIIS ICS Control Agent

`control-agent/` 是 AIIS ICS Architecture 配套的可选 Rust/Tauri 现场运行时
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
