//! DAA SQLite唯一执行图；旧YAML/直库运行模块保留源码但不注册。
pub(crate) mod local_activation;
pub(crate) mod local_configuration;
pub(crate) mod local_queries;
pub(crate) mod local_recovery;
pub(crate) mod local_scheduler;
pub(crate) mod local_storage;
pub(crate) mod local_supervisor;
pub(crate) mod local_yaml_migration;

pub(crate) mod local_point_naming;
