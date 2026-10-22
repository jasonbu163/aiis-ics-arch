//! DS运行时职责：DS runtime: a single image owner per instance; native protocol is an adapter.
pub mod app;
pub mod config;
pub mod domain;
pub mod infrastructure;
pub mod services;
#[cfg(feature = "test-automation")]
pub mod testing;
