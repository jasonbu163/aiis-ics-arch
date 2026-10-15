# AIIS Semantic Mapping Agent

[English](README.md)

本工程来源：DTB TSS a87c107c10e8d9d9d3e389e357b50d203d2aebf7。统一生命周期归 [AW PLAN](../PLAN.zh-CN.md)，范围和实际证据见根 [ARCH-AW-001](../../plans/ARCH-AW-001-agent-foundation/tasks.md)。

SMA 保留通用 HTTP 事实/材料/目标 API/映射逻辑和适用 TSS 界面；排除客户页面、SQL/legacy IPC 和跨 DTB 帮助生成。既有 /api/tss/v1 和 collection-facts HTTP 合同保持不变，不打包 backend。

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

独立身份、端口、配置加载和临时profile用法见 [AW README](../README.zh-CN.md)。默认所有外部I/O关闭；纯本地工程验证不证明真实PLC/DB/Target或业务闭环。SQLite配置/映射存储后续另立spec。
