# Control Agent 计划

## 当前基线

Control Agent 是 AIIS ICS Architecture 的可选配套运行时。当前源码基线保留
Tauri 控制台、Rust supervisor、只读 PLC 点位/策略适配器以及后端拥有的快照
合同。

公开示例已经脱敏，所有外部门禁默认关闭。本仓库不保存生产 PLC、数据库、
客户配置或构建产物。

## 边界

1. PLC 读取归常驻 Rust 运行时负责。
2. 快照写入必须同时通过本地显式数据库门禁和审核过的现场合同。
3. 后端仍是 Web/API 边界，并拥有快照表。
4. 数据库引擎设置和 YAML 上传推迟到 `CA-CONFIG-001`。
5. 发布打包和部署不属于本源码基线。

## 验证入口

在具备声明依赖的环境中执行 `pnpm build`、`cargo fmt --manifest-path
src-tauri/Cargo.toml --check` 和 `cargo test --manifest-path
src-tauri/Cargo.toml`。这些检查必须保持不连接真实 PLC/数据库。
