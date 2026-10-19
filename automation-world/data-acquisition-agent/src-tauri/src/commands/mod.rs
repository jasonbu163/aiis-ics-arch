//! DAA SQLite唯一执行图；旧YAML/直库运行模块保留源码但不注册。
pub(crate) mod local_acquisition;
#[cfg(feature = "local-validation")]
pub(crate) mod local_validation;
