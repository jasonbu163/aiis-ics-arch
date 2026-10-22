# Build and Run

Use the project locks with Node 22.19.0, pnpm 11.11.0, Rust/Cargo 1.89.0, CMake 4.0.2 and Apple clang 17 / SDK 26.1 on macOS arm64. No installer, signing, system registration or other platform is validated here.

From this directory:

```sh
pnpm install --frozen-lockfile
pnpm tauri dev
pnpm tauri build --no-bundle
```

Tauri's `build.features` explicitly enables `native-s7`, including when the CLI passes `--no-default-features`. The runtime build script automatically invokes CMake in Cargo `OUT_DIR`; the desktop consumes Cargo `DEP_DS_S7_NATIVE_*` metadata and links the native library with the required rpath. No G0 environment variables or prebuilt library in `/private/tmp` are product prerequisites. Frontend-only `pnpm dev` uses strict `127.0.0.1:15194`; it reports unavailable desktop operations rather than mock success. Preview uses strict port 14194.

To isolate a local product session, set optional `DS_PROFILE_DIR` to a new absolute owned directory before launch. It contains DS configuration, logs and the persistent WebView store ID; macOS stores actual WebKit data separately under that ID. Do not delete unknown existing profiles or system WebKit directories. A profile in use is rejected rather than replaced. The new profile starts empty and never opens S7 listeners until a configured, applied instance is explicitly started. Product configuration accepts IPv4 loopback endpoints; insufficient permissions or occupied ports produce a real start failure.

The non-default `test-automation` feature and an explicit owned manifest enable the fixed native DOM driver or `ds-test-host`. They are absent from the normal product command surface. See [tests](tests/README.md) for the approved role paths, build/gate sequence and exact validation commands. Protocol experiments use only 127.0.0.1:30102/30103, with 30104 reserved for negative cases; they never fall back to 102 or kill another listener. Test build, native lifecycle, wire results and independent QA are distinct evidence.

Layout regression uses the existing non-default native driver at a 960×640 outer window: card gaps, local table overflow, dialog bounds/footer spacing and page-change scroll are checked against actual DOM. Browser preview pixels are separate evidence and do not prove native IPC.
