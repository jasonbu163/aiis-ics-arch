//! 可恢复实例级激活：先关新轮并等完整提交，再依次准备/解释/CAS/安装/确认，不宣称双库原子。
use super::local_supervisor::{Loaded, LocalEngine};
use crate::domain::local_configuration::*;
use serde_json::{json, Value};
use std::{
    sync::Arc,
    time::{Duration, Instant},
};
fn failpoint(name: &str) {
    #[cfg(feature = "local-validation")]
    crate::infrastructure::local_fixture::failpoint(name);
    #[cfg(not(feature = "local-validation"))]
    let _ = name;
}
impl LocalEngine {
    pub fn activate(
        self: &Arc<Self>,
        etag: String,
        expected: Option<String>,
        rollback: bool,
    ) -> LocalResult<Value> {
        let _activation = self
            .activation
            .try_lock()
            .map_err(|_| "activation_pending")?;
        let view = self.configuration()?;
        if view.etag != etag || view.active != expected {
            return Err("activation_conflict".into());
        }
        let candidate = if rollback {
            let r = view.previous.clone().ok_or("previous_missing")?;
            self.storage.call(true, move |s| s.revision(&r))?
        } else {
            view.draft
        };
        if !validate(&candidate).is_empty() {
            return Err("configuration_invalid".into());
        }
        // Fixture coverage is checked only when this PLC is explicitly connected.
        // Activation installs stopped actors; unknown fixture endpoints never select real transport.
        let begin = Instant::now();
        {
            let mut gate = self.gate.lock().unwrap();
            gate.closed = true;
            while gate.rounds > 0 {
                if begin.elapsed() > Duration::from_secs(7) {
                    return Err("activation_pending".into());
                }
                let (g, _) = self
                    .gate_changed
                    .wait_timeout(gate, Duration::from_millis(50))
                    .map_err(|_| "activation_pending")?;
                gate = g;
            }
        }
        let (token, revision) = self.storage.call(false, move |s| {
            if let Some(x) = s.pending_activation()? {
                return Ok(x);
            }
            s.prepare_activation(&etag, expected.as_deref(), rollback)
        })?;
        failpoint("activation_prepared");
        let (t, r) = (token.clone(), revision.clone());
        self.storage
            .call(false, move |s| s.prepare_context(&t, &r))?;
        failpoint("activation_context");
        let (t, r) = (token.clone(), revision.clone());
        self.storage.call(false, move |s| s.select_active(&t, &r))?;
        failpoint("activation_selected");
        let r = revision.clone();
        let c = self.storage.call(true, move |s| s.revision(&r))?;
        self.install(Loaded {
            configuration: c,
            revision: revision.clone(),
        })?;
        failpoint("activation_loaded");
        let t = token.clone();
        self.storage.call(false, move |s| s.finish_activation(&t))?;
        failpoint("activation_applied");
        self.gate.lock().unwrap().closed = false;
        self.event("configuration_activated", &revision, "applied");
        Ok(
            json!({"schemaVersion":1,"token":token,"phase":"applied","active":revision,"loaded":revision,"used":self.configuration()?.used}),
        )
    }
}
