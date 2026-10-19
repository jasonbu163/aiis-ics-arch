//! 本地存储健康与策略准入。采集actor等待一次完整提交返回后才可开启下一轮，总在途最多4轮。
use super::local_supervisor::LocalEngine;
use crate::domain::{local_configuration::LocalResult, local_runtime::Capacity};
impl LocalEngine {
    pub fn capacity(&self) -> LocalResult<Capacity> {
        let quota = self
            .loaded
            .lock()
            .unwrap()
            .as_ref()
            .map(|l| l.configuration.storage.quota_bytes)
            .unwrap_or(1024 * 1024 * 1024);
        self.storage.call(true, move |s| s.capacity(quota))
    }
}
