# Snap7 1.4.2 controlled experimental copy

Source: official snap7-full-1.4.2.7z, 20591252 bytes, SHA-256 1f4270cde8684957770a10a1d311c226e670d9589c69841a9012e818f7b9f80e. The original package was read from the approved P0 material; this run verifies package bytes and copies original source, not distributed binaries.

Original copyright and LGPL-3.0-or-later notices remain in each source. Original gpl.txt and lgpl-3.0.txt are included in both trees. This is local experimental use, not a distribution permission conclusion. The separate rust-snap7 package retains its original MulanPSL manifest, GPL build-script notice and LGPL native materials inside the isolated original package cache.

upstream is byte-identical original source. controlled changes only s7_server.{h,cpp}, s7_isotcp.{h,cpp}, snap_msgsock.{h,cpp}, snap_tcpsrvr.{h,cpp}. Native S7 item parsing/encoding and ISO dispatch loops remain; guards call the unique Rust runtime owner through the versioned C bridge and pre-reserve the whole PDU. The controlled ISO destination pointer uses the original payload base plus cumulative offset to avoid cumulative pointer drift across fragments. No alternate protocol loop is introduced.

Controlled creation checks pthread_create at original worker/listener lifecycle points and reuses the original ThreadProc. Execute records pthread_self; completion notification plus real pthread_join precedes destruction/slot release. TSnapThread/unix_threads and the original non-G0 branch remain unchanged. Ready timeout retains ownership; known creation failure releases a never-created thread separately. Stop can retry partial cleanup. Server IO uses absolute monotonic deadlines, bounded frames, a four-entry kernel listen backlog, and a resourceless callback returning int; no registered image pointer exists.

The exact file manifests and native-g0.patch describe this candidate, not an upstream fix or general Snap7 qualification. Original native and Python candidates remain no_go; controlled candidate runtime status belongs exclusively to the root task record and subsequent independent checklist.

ARCH-AW-005 r4 retires the six unadopted C++ business sources after verified persistent archival. Native owns no business image, rules, fairness queue or capacity policy; Rust supplies admission/connection/PDU decisions. Server absolute IO and lifecycle timing use the macOS original _CLOCK_MONOTONIC enum, avoiding the frozen upstream helper macro value0 without modifying that helper. The original runtime-resource limitations remain subject to the r4 B0 and wire evidence.
