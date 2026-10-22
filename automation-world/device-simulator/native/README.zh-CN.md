# 原生 S7 适配层

[产品构建](../BUILD.zh-CN.md) · [Rust FFI](../runtime/src/infrastructure/native_ffi.rs) · [C bridge](bridge/ds_s7_bridge.h) · [Vendor 说明](vendor/snap7-1.4.2/NOTICE.md)

Snap7 1.4.2 upstream 保持原字节。controlled 副本仅修改 `s7_server.{h,cpp}`、`s7_isotcp.{h,cpp}`、`snap_msgsock.{h,cpp}`、`snap_tcpsrvr.{h,cpp}`；manifest 与[完整 patch](vendor/snap7-1.4.2/native.patch) 固定差异。原线程框架与协议响应编码器不变。两文件 C ABI bridge 不保存 DB image、规则、SQLite 或业务写策略。

既有 dispatch 检查有限白名单，并在 item 0 前预留整 PDU 的输入、描述符、stage、副本及最大响应。每 item 同步借用 Rust context，`int` 结果传播到真实 S7 item 错误；packed tag 在 Rust 以 unaligned read 复制。仅 owner 修改内存。callback 返回、socket 关闭或线程 `Closed` 标记都不是真实 join：受控 worker/listener 必须实际 `pthread_join` 后才释放名额、socket 与 callback context。

验证 profile 为 IPv4 loopback、协商 S7 PDU 480 字节、frame 上限 512、最多四 item。DB/BOOL/typed 操作受完整触达范围限制；未支持系统操作明确拒绝或关闭。握手、frame、precommit、send 截止与 Rust 共用 `CLOCK_MONOTONIC` 原点。队列、输入/输出预留及 C/H/TCP/closing 与 Rust 线程/内存联合限制。本 profile 不证明超过 16 个已建立会话的容量、完整 CPU 行为、其它平台或崩溃隔离；native 硬崩可能终止整个进程。

runtime build script 为本 CMake 工程显式提供 Cargo `OUT_DIR` 下的 `DS_NATIVE_OUTPUT_DIR`。测试 reference client 独立构建 untouched upstream 库，不充当产品 server。真实 ABI、时序、wire 和资源证据见[验证说明](../tests/README.zh-CN.md)，不能由同名 API 推断行为。
