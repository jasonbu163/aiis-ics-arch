# Field Flow Rust — Build and platform limits

[中文](BUILD.zh-CN.md)

This source build guide uses Cargo.toml/Cargo.lock from this project. rust-version=1.89 is the minimum declared Rust version; it does not guarantee every OS/toolchain combination. Rust is the future deployment-runtime direction. This task builds and runs a bounded macOS arm64 candidate, not a released package or field-qualified service.

## Locked native builds

Use an existing Rust/Cargo toolchain ≥1.89 plus native C/C++ compiler, linker and matching OS SDK. Missing tools are a prerequisite failure; this task does not install targets, compilers or SDKs. Run in this project root (or its standalone copy), create a private output root and build product and fixture separately:

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
The paths above are macOS native host outputs. --locked refuses lockfile changes; --release selects the optimized profile; --bin chooses the artifact. Product explicitly excludes default/test features. test-fixture enables only the separate ff-fixture/test hooks; release runtimes need not ship the fixture. Keep separate target directories so a feature build cannot be mistaken for the product. No build command here runs services or publishes artifacts. Full init/run/inspect/normal-stop steps are in this project’s [USER_GUIDE](USER_GUIDE.md).

## Runtime files and native dependencies

| Item | Actual requirement |
| --- | --- |
| `field-flow` | The product executable is also the driver child: current_exe() starts hidden __driver with inherited private FDs/lock. Do not manually invoke it. There is no ff-driver binary. |
| `config` | Explicit --config YAML path; no default parent/sibling config. Site values remain external and require approval. |
| `locales` | en-US/zh-CN JSON is include_str! compiled into product; no runtime locale-file copy required. |
| `state/logs` | Separate writable directory, explicitly initialized once; state.sqlite, instance.lock, transient gate-*, runtime.jsonl backups. Not build assets. |
| `native Snap7` | rust-snap7 C++ sources are compiled by cc into archive and linked; no separate Snap7 daemon is required. |
| `SQLite` | rusqlite=0.32.1 uses bundled SQLite; C build tools are required. |
| `system libraries` | Inspect the final executable per target; static native archives do not imply fully static output. |
| `LICENSE / THIRD_PARTY_NOTICES` | Retain source/component notices and perform a separate artifact distribution review. |

The frozen rust-snap7 package is 1.142.2, source registry+https://github.com/rust-lang/crates.io-index, Cargo.lock checksum 8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243. On the Development host its unmodified source is /Users/jason/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rust-snap7-1.142.2/build.rs. That path is evidence, not a required runtime path. The build script calls cc::Build::new().cpp(true), enumerates native/*.cpp and compile("libsnap7.a"); compiler/linker availability and C++ runtime still depend on the target environment. It does not prove MSVC/GNU/musl/static portability.

Local read-only dependency inspection on macOS arm64 found /usr/lib/libc++.1.dylib, /usr/lib/libSystem.B.dylib /System/Library/Frameworks/Security.framework/Versions/A/Security, /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation and /usr/lib/libiconv.2.dylib in the product. This is the observed link list for this candidate, not a claim of a universal single-file/static artifact. Re-run file/otool on any changed build.

The [existing notices](THIRD_PARTY_NOTICES.md) distinguish the wrapper package’s MulanPSL-2.0, native Snap7 LGPL-3.0-or-later headers and build.rs GPL-3.0-or-later header; preserve these distinctions and original upstream declarations. The wrapper package field is not a complete distribution license conclusion. This task does not complete static-link compliance, signing, installer or distribution review.

## Platform matrix

| OS / arch / Rust target | Native compiler/linker/SDK condition | Current source / this task evidence / next gate |
| --- | --- | --- |
| `macOS arm64 / aarch64-apple-darwin` | Rust host tools + Apple clang/clang++ + Apple linker/macOS SDK (existing Command Line Tools). | Locally built/runnable with existing rustc1.89/Cargo1.89/Apple clang17, Darwin24.6 arm64. No x86_64 macOS proof. Field/service/long-soak gate remains. |
| `Linux x86_64 or arm64 / x86_64-unknown-linux-gnu or aarch64-unknown-linux-gnu` | Native Rust + compatible gcc/g++ or clang/clang++, linker, libc and development headers; target C/C++ and SQLite build chain. | Unix-oriented source is statically compatible in direction only; no Linux build/run in this task. Native frozen-dependency compile, link, CLI/IO/lifecycle validation required. |
| `Windows x86_64 / x86_64-pc-windows-msvc (GNU is a different ABI/toolchain choice)` | After source adaptation: Rust target + matching MSVC C/C++ Build Tools/link.exe/Windows SDK; GNU alternative needs matching MinGW compiler/linker/runtime, not mixed MSVC libs. | Blocked by current source: std::os::unix::net::UnixStream, CommandExt/pre_exec, raw FD inheritance, libc::flock/fcntl and tokio::signal::unix. No cfg Windows implementation. Not buildable/deliverable as-is; separate port and native validation required. |

On a supported Unix host with the listed existing native prerequisites, use the locked host-native commands above; on Linux select the available compiler version only after target-environment review. --target changes the output directory to target-dir/TRIPLE/release/field-flow. A target standard library alone is insufficient: cross builds additionally need a matching target linker, C/C++ compiler and runtime, SQLite C chain, target system libraries/SDK and cc configuration (e.g. CC_/CXX_/AR_ target settings plus Cargo target linker). This task neither runs rustup target add nor downloads a cross toolchain. musl/full-static, Windows GNU and MSVC support must not be inferred from an upstream target list.

Primary documentation: [Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html) explains artifact/profile/feature/target/lock flags; [Rust platform support](https://doc.rust-lang.org/rustc/platform-support.html) describes compiler target tiers. Those official toolchain facts do not validate this project’s POSIX/native source on another OS. Frozen dependency source plus actual target evidence controls delivery claims.

## State survives executable replacement

Source/config is a reviewable candidate; target output is a rebuildable artifact; a new synthetic lesson state is disposable only after evidence/ownership review. An existing execute store is execution history and must not be deleted to start again. Before replacing an executable or moving host: stop the active writer normally, actually wait/reap its children, verify ports/PIDs, inspect schema/implementation/mode/instance and unresolved commands, and retain original state and logs. Do not casually copy a running SQLite DB/journal/lock/gate, switch language against the same writable DB or regenerate identities to replay. Backup/restore, schema compatibility, migration and cross-host fencing have no delivered workflow here and need a separate scope. A binary replacement does not authorize schema/data changes or unknown reconciliation.

This task performs no service installation, deployment, real PLC/HTTP operation, Git publication, signing or license-compliance conclusion. [Local runtime guide](USER_GUIDE.md) contains the bounded loopback steps and normal release evidence.
