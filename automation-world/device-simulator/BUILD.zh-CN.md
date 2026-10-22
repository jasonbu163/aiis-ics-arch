# 构建与运行

在 macOS arm64 使用项目锁及 Node 22.19.0、pnpm 11.11.0、Rust/Cargo 1.89.0、CMake 4.0.2、Apple clang 17 / SDK 26.1。本轮不验证安装器、签名、系统注册或其它平台。

在本目录执行：

```sh
pnpm install --frozen-lockfile
pnpm tauri dev
pnpm tauri build --no-bundle
```

遇到store不匹配或modules重建提示，先看[手册的pnpm说明](USER_GUIDE.zh-CN.md#12-pnpm-store-提示怎样处理)。历史`/private/tmp`验证store不是正常启动依赖；保持声明的pnpm版本/锁，核对重装只涉及本工程依赖。手工DB与导入步骤及当前非零初值/持续固定值输入问题见[使用手册](USER_GUIDE.zh-CN.md)。

Tauri `build.features` 显式启用 `native-s7`，CLI 使用 `--no-default-features` 时同样有效。runtime build script 自动在 Cargo `OUT_DIR` 调用 CMake；桌面消费 Cargo `DEP_DS_S7_NATIVE_*` 元数据并设置所需 rpath。正常产品不要求 G0 环境变量或 `/private/tmp` 预编译库。仅前端的 `pnpm dev` 使用严格 `127.0.0.1:15194`，桌面操作不可用时明确提示，不返回 mock 成功；preview 使用严格端口 14194。

需要隔离本地会话时，在启动前将可选 `DS_PROFILE_DIR` 设置为新的自有绝对目录。目录保存 DS 配置、日志及持久 WebView store ID；macOS 实际 WebKit 数据按该 ID 另存。不要删除归属未知的既有 profile 或系统 WebKit 目录。已占用 profile 拒绝打开，不替换原目录。新 profile 默认空配置，只有配置、应用后的实例经显式启动才打开 S7 listener。产品配置接受 IPv4 loopback；权限不足或端口占用会真实启动失败。

非默认 `test-automation` feature 与显式 owned manifest 同时开启后，才可运行固定原生 DOM driver 或 `ds-test-host`；普通产品命令面没有这些测试入口。[测试说明](tests/README.zh-CN.md) 列批准的角色路径、构建/gate 顺序和精确验证命令。协议实验仅使用 127.0.0.1:30102/30103，30104 只作负例；不回退 102、不杀其它 listener。测试构建、原生生命周期、wire 结果和独立 QA 分开取证。

布局回归复用现有非默认原生 driver，在960×640外窗核实际DOM的卡片间距、表内横滚、弹窗边界/按钮间距及切页滚动。浏览器preview像素单列取证，不作为原生IPC证明。
