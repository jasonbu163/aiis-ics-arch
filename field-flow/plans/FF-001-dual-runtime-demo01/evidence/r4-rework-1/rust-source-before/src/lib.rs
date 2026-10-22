//! 文件：src/lib.rs；FF运行时装配入口与模块边界，不执行IO。
pub mod app;
pub mod commands;
pub mod config;
pub mod domain;
pub mod driver_process;
pub mod infrastructure;
pub mod runtime;
pub mod services;
pub type Result<T> = std::result::Result<T, String>;
#[cfg(feature = "test-fixture")]
pub mod fixture;
