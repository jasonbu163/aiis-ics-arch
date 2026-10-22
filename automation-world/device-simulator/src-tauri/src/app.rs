//! 桌面只持共享runtime/日志和正常关闭门；未确认dirty时不执行shutdown。
use std::sync::{atomic::AtomicBool, Arc, Mutex};
pub struct Desktop {
    pub bootstrap: crate::config::bootstrap::Bootstrap,
    pub runtime: Arc<ds_runtime::app::App>,
    pub logs: Mutex<Option<ds_runtime::infrastructure::logging::LogThread>>,
    pub close_approved: AtomicBool,
}
impl Desktop {
    pub fn stop_logs(&self) {
        if let Some(log) = self.logs.lock().unwrap().take() {
            log.stop();
        }
    }
}
