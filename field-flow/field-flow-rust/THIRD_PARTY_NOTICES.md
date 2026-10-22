# Component notices

This project's handwritten code retains the repository MIT license in LICENSE. It does not relicense dependencies.

Cargo.lock pins rust-snap7 1.142.2 from crates.io. Its Cargo package/Rust wrapper declares MulanPSL-2.0; bundled native Snap7 sources retain LGPL-3.0-or-later headers, and build.rs has a GPL-3.0-or-later header. The upstream build compiles/links native C++ into this executable. These declarations differ; the package field alone is not a license conclusion for every component. Original declarations remain in the unmodified dependency distribution. This project neither vendors nor patches it.

The small INT payload adapter is handwritten here, uses the upstream public ISO exchange API, and does not copy upstream protocol implementation. Tokio/reqwest/serde/rusqlite and other exact source/checksum entries are in Cargo.lock; rusqlite's bundled SQLite is built locally. Any artifact distribution, static-link compliance review, packaging/signing and production delivery require a separate gate; this task does not publish artifacts.
