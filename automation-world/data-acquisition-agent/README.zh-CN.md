# AIIS Data Acquisition Agent

[English](README.md)

本工程来源：CA freeze receipt。统一生命周期归 [AW PLAN](../PLAN.zh-CN.md)，范围和实际证据见根 [ARCH-AW-001](../../plans/ARCH-AW-001-agent-foundation/tasks.md)。

DAA 暂时保留旧 raw/latest 快照实现；尚未接入新 AW 事实/配置 API。

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

独立身份、端口、配置加载和临时profile用法见 [AW README](../README.zh-CN.md)。默认所有外部I/O关闭；纯本地工程验证不证明真实PLC/DB/Target或业务闭环。SQLite配置/映射存储后续另立spec。
