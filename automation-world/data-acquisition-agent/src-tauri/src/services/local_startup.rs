//! DAA 软件启动偏好：仅原生启动时调度现有 PLC actor 与样本上报器。
use super::local_supervisor::LocalEngine;
use crate::domain::{local_configuration::LocalResult, local_runtime::StartupSettings};
use serde_json::{json, Value};
use std::sync::Arc;

impl LocalEngine {
    pub fn startup_settings(&self) -> LocalResult<Value> {
        // 与先前可能仍在执行的偏好写入排队，以免把旧值误当作最终结果。
        let settings = self.storage.call(false, |s| s.startup_settings())?;
        Ok(json!({"settings": settings, "errors": self.startup_errors.lock().unwrap().clone()}))
    }

    pub fn save_startup_settings(&self, settings: StartupSettings) -> LocalResult<Value> {
        self.log.health()?;
        self.storage
            .call(false, move |s| s.save_startup_settings(settings))?;
        self.event("startup_settings_saved", "instance", "committed");
        self.startup_settings()
    }

    fn startup_failure(&self, kind: &str, error: &str) {
        self.startup_errors
            .lock()
            .unwrap()
            .insert(kind.into(), error.into());
        self.event("startup_automation_failed", kind, error);
    }

    /// 由原生启动入口恰好调用一次；切换设置、刷新和重新激活不调用。
    pub(crate) fn startup_automation(self: &Arc<Self>) {
        let settings = match self.storage.call(true, |s| s.startup_settings()) {
            Ok(settings) => settings,
            Err(error) => {
                self.startup_failure("settings", &error);
                return;
            }
        };
        if settings.auto_collect {
            let loaded = self.loaded.lock().unwrap().clone();
            if let Some(loaded) = loaded {
                let targets: Vec<_> = loaded
                    .configuration
                    .plcs
                    .iter()
                    .filter(|p| p.enabled)
                    .map(|p| p.id.clone())
                    .collect();
                if targets.is_empty() {
                    self.startup_failure("collection", "plc_missing");
                }
                for id in targets {
                    if let Err(error) =
                        self.request(vec![id], "startup_collection", true, &loaded.revision, None)
                    {
                        self.startup_failure("collection", &error);
                    }
                }
            } else {
                self.startup_failure("collection", "active_missing");
            }
        }
        if settings.auto_report {
            if let Err(error) = self.start_automatic_delivery() {
                self.startup_failure("report", &error);
            }
        }
    }
}
