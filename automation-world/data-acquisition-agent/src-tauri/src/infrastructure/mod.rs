//! DAA SQLite唯一执行图；旧YAML/直库运行模块保留源码但不注册。
pub(crate) mod local_decode;
#[cfg(any(test, feature = "local-validation"))]
pub(crate) mod local_fixture;
pub(crate) mod local_logging;
pub(crate) mod local_profile_lock;
pub(crate) mod local_store;
pub(crate) mod managed_s7;
pub(crate) mod plc_layout;
pub(crate) mod tia_source;
#[cfg(test)]
pub(crate) mod yaml_migration;
