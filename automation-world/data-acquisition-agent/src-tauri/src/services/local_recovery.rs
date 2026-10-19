//! 启动/退出装配：SQLite恢复与身份/版本核对先于actor，启动没有人工连接/采集意图。
use super::local_supervisor::LocalEngine;
use crate::{config::local_bootstrap::Bootstrap, domain::local_configuration::LocalResult};
use std::sync::Arc;
pub(crate) fn open(bootstrap: Bootstrap) -> LocalResult<Arc<LocalEngine>> {
    LocalEngine::open(bootstrap)
}
