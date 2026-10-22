# Native S7 Adapter

[Product build](../BUILD.md) · [Rust FFI](../runtime/src/infrastructure/native_ffi.rs) · [C bridge](bridge/ds_s7_bridge.h) · [Vendor notice](vendor/snap7-1.4.2/NOTICE.md)

Snap7 1.4.2 upstream is retained byte-for-byte. The controlled copy differs only in `s7_server.{h,cpp}`, `s7_isotcp.{h,cpp}`, `snap_msgsock.{h,cpp}` and `snap_tcpsrvr.{h,cpp}`. The manifests and [complete patch](vendor/snap7-1.4.2/native.patch) identify these changes. The original thread framework and protocol response encoder remain unchanged. The two-file C ABI bridge contains no DB image, rules, SQLite or business write policy.

Existing dispatch checks the finite whitelist and reserves the whole PDU input/descriptors/staging/copies/worst response before item 0. Each item synchronously borrows the Rust context; its `int` result propagates to the actual S7 item error. Packed tags are copied with unaligned reads in Rust. The owner alone mutates memory. A callback return, closed socket or thread's `Closed` flag is not a real join: controlled workers/listeners are actually `pthread_join`ed before slots, sockets and callback context are released.

The validated profile is IPv4 loopback, negotiated S7 PDU 480 bytes, bounded frame 512 and at most four items. DB/BOOL/typed operations are restricted by complete touched-range checks; unsupported system operations reject or close. Handshake, frame, precommit and send deadlines use the same `CLOCK_MONOTONIC` origin as Rust. Queue/input/output reservations, C/H/TCP and closing are bounded jointly with Rust threads and memory. Capacity above 16 established sessions, complete CPU behavior, other platforms and crash isolation are not established by this profile. A native hard crash can terminate the shared process.

The runtime build script invokes this CMake project with explicit `DS_NATIVE_OUTPUT_DIR` under Cargo `OUT_DIR`. The reference client builds a separate untouched upstream library in tests and is not linked as the product server. See [validation](../tests/README.md) for real ABI, timing, wire and resource evidence rather than assuming similarly named APIs have identical behavior.
