# Field Flow Rust — 构建与平台边界

[English](BUILD.md)

本说明使用本工程Cargo.toml/Cargo.lock；rust-version=1.89为声明的最低Rust版本，不保证所有OS/工具链组合。Rust为后续部署runtime建设方向；本轮构建/运行有限macOS arm64候选，不发布包或授予现场服务资格。

## 锁定原生构建

使用已有≥1.89 Rust/Cargo、本机C/C++编译器/linker及匹配OS SDK。缺工具为前置失败；本轮不安装target/compiler/SDK。在本工程根（或独立副本）创建私有输出根，分别构建产品与夹具：

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust
rustc -Vv
cargo -V
clang++ --version
FF_BUILD=$(mktemp -d /private/tmp/ff-002-r1-build-XXXXXX)
printf "%s\n" "$FF_BUILD"
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_BUILD/product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_BUILD/fixture"
"$FF_BUILD/product/release/field-flow"
"$FF_BUILD/product/release/field-flow" --lang zh-CN --help
"$FF_BUILD/fixture/release/ff-fixture" --help
file "$FF_BUILD/product/release/field-flow"
otool -L "$FF_BUILD/product/release/field-flow"
```
上例为macOS原生host产物。--locked拒绝锁变化，--release选择优化profile，--bin指定产物。产品明确不启用default/test feature；test-fixture仅用于独立ff-fixture及测试hook，交付runtime无需带夹具。分开target避免feature构建与产品混淆。这些build命令不启动服务或发布产物。完整init/run/inspect/正常停止见自身[USER_GUIDE](USER_GUIDE.zh-CN.md)。

## 运行文件与native依赖

| 项目 | 真实要求 |
| --- | --- |
| `field-flow` | 产品本身同时作为driver child：current_exe()以继承的私有FD/锁启动隐藏__driver，无需人工调用，不存在ff-driver binary。 |
| `config` | 显式--config YAML，不自动找父/兄弟配置；现场值外置并另需批准。 |
| `locales` | en-US/zh-CN JSON由include_str!编入产品，运行无需另复制locale文件。 |
| `state/logs` | 单独可写目录、仅显式初始化一次；state.sqlite、instance.lock、临时gate-*、runtime.jsonl备份，不是构建资源。 |
| `native Snap7` | rust-snap7 C++由cc编为archive并链接，不需要额外Snap7 daemon。 |
| `SQLite` | rusqlite=0.32.1启用bundled SQLite，要求C构建工具。 |
| `system libraries` | 按目标检查最终executable；native静态archive不代表最终全静态。 |
| `LICENSE / THIRD_PARTY_NOTICES` | 保留源码/组件声明，产物分发合规另gate。 |

冻结rust-snap7=1.142.2，source=registry+https://github.com/rust-lang/crates.io-index，Cargo.lock checksum=8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243。DEV宿主未修改源码位于/Users/jason/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rust-snap7-1.142.2/build.rs；此路径是核对证据，非运行必需路径。build.rs调用cc::Build::new().cpp(true)，枚举native/*.cpp并compile("libsnap7.a")；compiler/linker与C++runtime仍依赖目标环境，不证明MSVC/GNU/musl/static可移植性。

本轮macOS arm64只读检查产品链接到/usr/lib/libc++.1.dylib、/usr/lib/libSystem.B.dylib、/System/Library/Frameworks/Security.framework/Versions/A/Security、/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation及/usr/lib/libiconv.2.dylib。这是当前候选的实测链接清单，不是通用单文件/全静态承诺；构建改变后须重做file/otool核对。

[既有notices](THIRD_PARTY_NOTICES.zh-CN.md)区分包装crate的MulanPSL-2.0、native Snap7的LGPL-3.0-or-later头和build.rs的GPL-3.0-or-later头；保留差异和上游原声明。crate许可字段不等于完整分发许可结论，本轮未完成静态链接合规、签名、安装器或分发审查。

## 平台矩阵

| OS / arch / Rust target | 原生compiler/linker/SDK条件 | 当前源码 / 本轮证据 / 下一gate |
| --- | --- | --- |
| `macOS arm64 / aarch64-apple-darwin` | Rust host tools + Apple clang/clang++ + Apple linker/macOS SDK（已有Command Line Tools）。 | 本机rustc1.89/Cargo1.89/Apple clang17、Darwin24.6 arm64实际构建运行；无macOS x86_64证明，现场/托管/长稳仍待。 |
| `Linux x86_64 or arm64 / x86_64-unknown-linux-gnu or aarch64-unknown-linux-gnu` | 原生Rust +兼容gcc/g++或clang/clang++、linker、libc及开发headers；目标C/C++/SQLite构建链。 | 仅静态核对Unix方向，无本轮Linux构建/运行；待原生冻结依赖编译、链接、CLI/IO/生命周期验证。 |
| `Windows x86_64 / x86_64-pc-windows-msvc (GNU is a different ABI/toolchain choice)` | 源码适配后：Rust target +匹配MSVC C/C++ Build Tools/link.exe/Windows SDK；GNU方案需要匹配MinGW compiler/linker/runtime，不能混用MSVC库。 | 现源码阻塞：std::os::unix::net::UnixStream、CommandExt/pre_exec、raw FD继承、libc::flock/fcntl、tokio::signal::unix，无Windows cfg替代实现；不能声称原样可构建/交付，待独立移植与原生验证。 |

满足上述已有原生条件的Unix宿主可执行前述锁定host命令；Linux须先核对目标环境/compiler版本。--target改变产物路径为target-dir/TRIPLE/release/field-flow。仅target标准库不够：交叉构建还需匹配target linker、C/C++ compiler/runtime、SQLite C构建链、目标系统库/SDK与cc配置（例如target对应CC_/CXX_/AR_及Cargo target linker）。本轮不运行rustup target add、不下载交叉工具链；不得从上游target清单推断musl/全静态、Windows GNU/MSVC支持。

官方primary：[Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html)解释产物/profile/feature/target/lock选项；[Rust platform support](https://doc.rust-lang.org/rustc/platform-support.html)解释编译器target层级。官方工具链事实不验证本工程POSIX/native源码在另一OS可用，交付结论以冻结依赖源码及实际目标证据为准。

## 可执行文件替换与状态生命周期

源码/config是可审查候选，target是可重建产物；新synthetic教学状态只在证据/归属核对后可回收。既有execute库是执行历史，不能删库重来。替换executable或迁机前：正常停writer、实际wait/reap子进程、核对端口/PID、inspect schema/implementation/mode/instance及未决命令，保留原状态/日志。不随意复制运行中SQLite/journal/lock/gate，不切语言共用可写库或生成新身份重放。本轮无可交付的backup/restore、schema兼容迁移或跨主机fencing流程，须另立范围。换binary不授权schema/数据变更或unknown处置。

本轮不安装服务、不部署、不操作真实PLC/HTTP、不Git发布、不签名或授予许可合规结论。[本机runtime手册](USER_GUIDE.zh-CN.md)含有限loopback步骤和正常释放证据。
