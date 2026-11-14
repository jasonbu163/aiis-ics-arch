//! 独立单样本上报 worker：显式启停，网络操作不持有 SQLite 事务。
use super::local_supervisor::LocalEngine;
#[cfg(test)]
use crate::{
    domain::local_delivery::{classify, Reply},
    infrastructure::local_store::delivery::Frozen,
};
use crate::{
    domain::{
        local_configuration::LocalResult,
        sample_upload::{Binding, Settings},
    },
    infrastructure::facts_http::{FactsHttp, Transport},
};
use serde_json::{json, Value};
use std::{
    sync::Arc,
    thread,
    time::{Duration, Instant},
};
#[cfg(test)]
type StartupTransports = std::collections::BTreeMap<std::path::PathBuf, Arc<dyn Transport>>;
#[cfg(test)]
static STARTUP_TRANSPORTS: std::sync::OnceLock<std::sync::Mutex<StartupTransports>> =
    std::sync::OnceLock::new();
#[cfg(test)]
pub(crate) fn startup_test_transport(
    profile: &std::path::Path,
    transport: Option<Arc<dyn Transport>>,
) {
    let mut map = STARTUP_TRANSPORTS
        .get_or_init(Default::default)
        .lock()
        .unwrap();
    if let Some(transport) = transport {
        map.insert(profile.into(), transport);
    } else {
        map.remove(profile);
    }
}
#[derive(Default)]
pub(crate) struct DeliveryControl {
    pub running: bool,
    pub error: Option<String>,
    pub join: Option<thread::JoinHandle<()>>,
    pub bindings: Vec<Binding>,
    pub origin: Option<String>,
    pub latest: bool,
    pub retry_clock: RetryClock,
}
impl LocalEngine {
    pub fn delivery_available(&self) -> LocalResult<bool> {
        if self.bootstrap.validation {
            return Ok(false);
        }
        self.storage.call(true, |s| {
            s.runtime
                .query_row("PRAGMA user_version", [], |r| r.get::<_, u32>(0))
                .map(|v| v == 4)
                .map_err(crate::infrastructure::local_store::sql_error)
        })
    }
    pub fn sample_upload_settings(&self) -> LocalResult<Settings> {
        self.storage.call(true, |s| s.sample_upload_settings())
    }
    pub fn save_sample_upload_settings(
        &self,
        settings: Settings,
        expected: String,
    ) -> LocalResult<Settings> {
        self.save_sample_upload_settings_after_lock(settings, expected, || {})
    }
    fn save_sample_upload_settings_after_lock(
        &self,
        settings: Settings,
        expected: String,
        after_lock: impl FnOnce(),
    ) -> LocalResult<Settings> {
        if self.bootstrap.validation || !self.delivery_available()? {
            return Err("delivery_profile_upgrade_required".into());
        }
        // 与派发的最终状态检查使用同一把锁；失败时保留原运行状态。
        let mut control = self.delivery.lock().unwrap();
        after_lock();
        let result = self.storage.call(false, move |s| {
            let before = s.sample_upload_settings()?;
            let saved = s.save_sample_upload_settings(settings, expected)?;
            let switches_only = before.disabled_local_plcs != saved.disabled_local_plcs
                && before.origin == saved.origin
                && before.path == saved.path
                && before.interval_seconds == saved.interval_seconds
                && before.bindings == saved.bindings;
            Ok((saved, switches_only))
        });
        // storage_pending 表示写入已排队但结果未知，迟到提交前也须停止新派发。
        if matches!(&result, Ok((_, false)))
            || matches!(&result, Err(error) if error == "storage_pending")
        {
            control.running = false;
        }
        result.map(|(saved, _)| saved)
    }
    pub fn sample_upload_sources(&self) -> LocalResult<Value> {
        self.storage.call(true, |s| Ok(json!({"schemaVersion":1,"contractVersion":"plc-facts/v2","sources":s.sample_upload_bindings()?,"localSources":s.reporting_local_sources()?})))
    }
    pub fn rebind_sample_upload(
        &self,
        sample_id: String,
        old_url: String,
        expected: String,
        sources: Vec<Binding>,
    ) -> LocalResult<Value> {
        self.rebind_sample_upload_after_check(sample_id, old_url, expected, sources, || {})
    }
    fn rebind_sample_upload_after_check(
        &self,
        sample_id: String,
        old_url: String,
        expected: String,
        sources: Vec<Binding>,
        before_write: impl FnOnce(),
    ) -> LocalResult<Value> {
        if !self.delivery_available()? {
            return Err("delivery_profile_upgrade_required".into());
        }
        let settings = self.sample_upload_settings()?;
        let new_url = settings.target()?.ok_or("target_missing")?;
        let current = self.storage.call(true, |s| s.sample_upload_bindings())?;
        if settings.settings_revision != expected || current != sources {
            return Err("source_confirmation_changed".into());
        }
        before_write();
        self.storage.call(false, move |s| {
            s.rebind_sample_upload(&sample_id, &old_url, &new_url, &expected, &sources)
        })?;
        self.delivery_snapshot()
    }
    pub fn delivery_snapshot(&self) -> LocalResult<Value> {
        let c = self.delivery.lock().unwrap();
        let running = c.running;
        let error = c.error.clone();
        drop(c);
        let mut value = self.storage.call(true, move |s| {
            let version: u32 = s
                .runtime
                .query_row("PRAGMA user_version", [], |r| r.get(0))
                .map_err(crate::infrastructure::local_store::sql_error)?;
            if version == 4 {
                s.sample_upload_snapshot(running)
            } else {
                s.delivery_snapshot(false)
            }
        })?;
        if !self.delivery_available()? {
            value["available"] = json!(false);
        }
        value["lastError"] = json!(error);
        if self.bootstrap.validation {
            value["available"] = json!(false);
            value["running"] = json!(false);
        }
        Ok(value)
    }
    pub fn set_delivery(
        self: &Arc<Self>,
        action: &str,
        expected: Option<String>,
        bindings: Option<Vec<Binding>>,
    ) -> LocalResult<Value> {
        if action != "pause" && (expected.is_none() || bindings.is_none()) {
            return Err("source_confirmation_required".into());
        }
        self.set_delivery_using_checked(action, expected.zip(bindings), || {
            Ok(Arc::new(FactsHttp::new()?) as Arc<dyn Transport>)
        })
    }
    #[cfg(test)]
    fn set_delivery_using(
        self: &Arc<Self>,
        action: &str,
        make: impl FnOnce() -> LocalResult<Arc<dyn Transport>>,
    ) -> LocalResult<Value> {
        self.set_delivery_using_checked(action, None, make)
    }
    fn set_delivery_using_checked(
        self: &Arc<Self>,
        action: &str,
        confirmation: Option<(String, Vec<Binding>)>,
        make: impl FnOnce() -> LocalResult<Arc<dyn Transport>>,
    ) -> LocalResult<Value> {
        self.set_delivery_using_checked_at_lock(action, confirmation, make, || {})
    }
    fn set_delivery_using_checked_at_lock(
        self: &Arc<Self>,
        action: &str,
        confirmation: Option<(String, Vec<Binding>)>,
        make: impl FnOnce() -> LocalResult<Arc<dyn Transport>>,
        before_lock: impl FnOnce(),
    ) -> LocalResult<Value> {
        self.set_delivery_with_authority(action, confirmation, make, before_lock, true)
    }
    /// 自动启动沿用目标与队列核验，但不能执行仅由人工确认授权的来源解除/目标更改。
    pub(crate) fn start_automatic_delivery(self: &Arc<Self>) -> LocalResult<Value> {
        self.set_delivery_with_authority(
            "start",
            None,
            || {
                #[cfg(test)]
                if let Some(transport) = STARTUP_TRANSPORTS
                    .get_or_init(Default::default)
                    .lock()
                    .unwrap()
                    .get(&self.bootstrap.profile)
                    .cloned()
                {
                    return Ok(transport);
                }
                Ok(Arc::new(FactsHttp::new()?) as Arc<dyn Transport>)
            },
            || {},
            false,
        )
    }
    fn set_delivery_with_authority(
        self: &Arc<Self>,
        action: &str,
        confirmation: Option<(String, Vec<Binding>)>,
        make: impl FnOnce() -> LocalResult<Arc<dyn Transport>>,
        before_lock: impl FnOnce(),
        operator_confirmed: bool,
    ) -> LocalResult<Value> {
        if !["start", "pause", "resume"].contains(&action) {
            return Err("invalid_request".into());
        }
        if action == "pause" {
            self.delivery.lock().unwrap().running = false;
            return self.delivery_snapshot();
        }
        let runtime_version: u32 = self.storage.call(true, |s| {
            s.runtime
                .query_row("PRAGMA user_version", [], |r| r.get(0))
                .map_err(crate::infrastructure::local_store::sql_error)
        })?;
        if runtime_version != 4 {
            return Err("delivery_profile_upgrade_required".into());
        }
        if self.bootstrap.validation || !self.delivery_available()? {
            return Err("delivery_profile_upgrade_required".into());
        }
        self.log.health()?;
        // 与设置保存串行化，从读取确认快照到发布运行状态都持有同一把锁。
        before_lock();
        let mut control = self.delivery.lock().unwrap();
        let (settings, bindings) = self.storage.call(true, |s| {
            Ok((s.sample_upload_settings()?, s.sample_upload_bindings()?))
        })?;
        settings.validate()?;
        let origin = settings.target()?.ok_or("target_missing")?;
        if bindings.is_empty() {
            return Err("source_adoption_required".into());
        }
        if confirmation
            .as_ref()
            .map(|(revision, sources)| {
                revision != &settings.settings_revision || sources != &bindings
            })
            .unwrap_or(false)
        {
            return Err("source_confirmation_changed".into());
        }
        if control.running {
            drop(control);
            return self.delivery_snapshot();
        }
        // 没有在途 HTTP 时才恢复残留 inflight；确认事务失败后同进程也可显式继续。
        let permit = self
            .delivery_http
            .try_lock()
            .map_err(|_| "delivery_http_busy")?;
        self.storage.call(false, |s| s.recover_sample_upload())?;
        drop(permit);
        if control.join.is_none() {
            let transport = make()?;
            let weak = Arc::downgrade(self);
            control.join = Some(thread::spawn(move || {
                let mut next = Instant::now();
                loop {
                    let engine = match weak.upgrade() {
                        Some(e) => e,
                        None => break,
                    };
                    if engine.stopped.load(std::sync::atomic::Ordering::SeqCst) {
                        break;
                    }
                    let running = engine.delivery.lock().unwrap().running;
                    if !running || Instant::now() < next {
                        drop(engine);
                        thread::sleep(Duration::from_millis(25));
                        continue;
                    }
                    for _ in 0..32 {
                        match engine.delivery_tick_v2(transport.clone()) {
                            Ok(true) => {}
                            Ok(false) | Err(_) => break,
                        }
                    }
                    let interval = engine
                        .sample_upload_settings()
                        .map(|s| s.interval_seconds)
                        .unwrap_or(5);
                    next = Instant::now() + Duration::from_secs(u64::from(interval));
                }
            }));
        }
        let confirmed = bindings.clone();
        let confirmed_origin = origin.clone();
        let confirmed_revision = settings.settings_revision.clone();
        let needs_review = self.storage.call(false, move |s| {
            // 新采样或激活不受 delivery 锁保护；最终核对与来源确认须同一 actor 回合。
            let current = s.sample_upload_settings()?;
            if current.settings_revision != confirmed_revision
                || current.target()?.as_deref() != Some(confirmed_origin.as_str())
                || s.sample_upload_bindings()? != confirmed
            {
                return Err("source_confirmation_changed".into());
            }
            if operator_confirmed {
                s.confirm_sample_upload_sources(&confirmed_origin, &confirmed)?;
                Ok(false)
            } else {
                s.automatic_delivery_needs_review(&confirmed_origin, &confirmed)
            }
        })?;
        control.origin = Some(origin);
        control.bindings = bindings;
        control.latest = false;
        control.running = true;
        control.error = None;
        drop(control);
        if operator_confirmed {
            self.startup_errors.lock().unwrap().remove("report");
        } else if needs_review {
            self.startup_errors
                .lock()
                .unwrap()
                .insert("report".into(), "startup_delivery_needs_review".into());
        }
        self.event("sample_delivery_started", "instance", "running");
        self.delivery_snapshot()
    }
    pub fn stop_delivery(&self) {
        let join = {
            let mut c = self.delivery.lock().unwrap();
            c.running = false;
            c.join.take()
        };
        if let Some(j) = join {
            let _ = j.join();
        }
    }
    fn delivery_tick_v2(&self, transport: Arc<dyn Transport>) -> LocalResult<bool> {
        self.delivery_tick_v2_before_mark(transport, || {})
    }
    fn delivery_tick_v2_before_mark(
        &self,
        transport: Arc<dyn Transport>,
        before_mark: impl FnOnce(),
    ) -> LocalResult<bool> {
        let permit = match self.delivery_http.try_lock() {
            Ok(p) => p,
            Err(_) => return Ok(false),
        };
        let result = self.delivery_tick_v2_under_permit(transport, before_mark);
        if let Err(error) = &result {
            // 先锁存本轮失败再释放许可，避免迟到错误覆盖后续明确继续。
            let mut control = self.delivery.lock().unwrap();
            control.error = Some(error.clone());
            control.running = false;
        }
        drop(permit);
        result
    }
    fn delivery_tick_v2_under_permit(
        &self,
        transport: Arc<dyn Transport>,
        before_mark: impl FnOnce(),
    ) -> LocalResult<bool> {
        self.log.health()?;
        let (origin, bindings, latest) = {
            let mut c = self.delivery.lock().unwrap();
            if !c.running {
                return Ok(false);
            }
            let values = (
                c.origin.clone().ok_or("target_missing")?,
                c.bindings.clone(),
                c.latest,
            );
            c.latest = !c.latest;
            values
        };
        let current = self.storage.call(true, |s| s.sample_upload_bindings())?;
        if current.iter().any(|binding| !bindings.contains(binding)) {
            return Err("source_changed".into());
        }
        let (wall, rows) = self.storage.call(true, |s| s.sample_retry_schedule())?;
        let ticks = self
            .delivery_epoch
            .elapsed()
            .as_millis()
            .min(u128::from(u64::MAX)) as u64;
        let waiting = {
            let mut c = self.delivery.lock().unwrap();
            c.retry_clock.sync(&rows, &wall, ticks)?;
            c.retry_clock
                .deadlines
                .iter()
                .filter(|(_, due)| **due > ticks)
                .map(|(id, _)| id.clone())
                .collect::<Vec<_>>()
        };
        let selected_origin = origin.clone();
        let selected_bindings = bindings.clone();
        let frozen = match self.storage.call(false, move |s| {
            s.next_sample_upload_ready(&selected_origin, &selected_bindings, latest, &waiting)
        })? {
            Some(f) => f,
            None => return Ok(false),
        };
        before_mark();
        let c = self.delivery.lock().unwrap();
        if !c.running || c.origin.as_deref() != Some(&origin) {
            return Ok(false);
        }
        let copy = frozen.clone();
        let confirmed = bindings.clone();
        let confirmed_origin = origin.clone();
        let attempt = self.storage.call(false, move |s| {
            // 同一 actor 回合核对现行目标和来源，再标记派发尝试。
            if s.sample_upload_settings()?.target()?.as_deref() != Some(confirmed_origin.as_str()) {
                return Err("source_confirmation_changed".into());
            }
            if s.sample_upload_bindings()?
                .iter()
                .any(|b| !confirmed.contains(b))
            {
                return Err("source_changed".into());
            }
            if !s.sample_upload_enabled(&copy.sample_id)? {
                return Ok(None);
            }
            s.mark_sample_upload_attempt(&copy).map(Some)
        })?;
        let Some(attempt) = attempt else {
            return Ok(false);
        };
        let (tx, rx) = std::sync::mpsc::sync_channel(1);
        let send_origin = frozen.origin.clone();
        let send_body = frozen.body.clone();
        let spawned = thread::Builder::new()
            .name("daa-sample-http".into())
            .spawn(move || {
                let _ = tx.send(transport.post_sample(&send_origin, &send_body));
            });
        drop(c);
        let response = match spawned {
            Ok(_) => rx
                .recv()
                .unwrap_or_else(|_| Err("transport_unknown".into())),
            Err(_) => Err("transport_unknown".into()),
        };
        let copy = frozen.clone();
        let (result, delay) = self.storage.call(false, move |s| {
            s.record_sample_upload_response(&copy, response, attempt)
        })?;
        if result != crate::domain::sample_upload::Reply::Committed {
            let ticks = self
                .delivery_epoch
                .elapsed()
                .as_millis()
                .min(u128::from(u64::MAX)) as u64;
            self.delivery
                .lock()
                .unwrap()
                .retry_clock
                .schedule(&frozen.sample_id, ticks, delay);
        }
        if result == crate::domain::sample_upload::Reply::TargetMismatch {
            self.delivery.lock().unwrap().running = false;
        }
        Ok(true)
    }
}
#[cfg(test)]
pub(crate) fn apply_response(
    storage: &crate::infrastructure::local_store::StoreHandle,
    frozen: &Frozen,
    response: LocalResult<crate::infrastructure::facts_http::Response>,
    attempt: u32,
) -> LocalResult<ApplyOutcome> {
    let jitter = (uuid::Uuid::new_v4().as_u128() % 21) as u32;
    let response = match response {
        Ok(r) => r,
        Err(error) => {
            let id = frozen.batch.batch_id.clone();
            let delay = crate::domain::local_delivery::retry_delay(attempt, None, jitter);
            return storage
                .call(false, move |s| {
                    s.fail_delivery(&id, "unknown", &error, delay, false)
                })
                .map(|pause| ApplyOutcome { pause });
        }
    };
    let reply = classify(
        &frozen.batch,
        response.status,
        &response.media_type,
        &response.body,
        response.retry_after.as_deref(),
        attempt,
        jitter,
    );
    let retry = match &reply {
        Reply::Failure {
            delay, protocol, ..
        } => Some(if *protocol {
            crate::domain::local_delivery::retry_delay(attempt, None, jitter)
        } else {
            *delay
        }),
        _ => None,
    };
    let raw = String::from_utf8(response.body).ok();
    let copy = frozen.clone();
    let result = match reply {
        Reply::Committed(value) => storage
            .call(false, move |s| {
                s.commit_delivery(&copy, &value, raw.as_deref().ok_or("invalid_utf8")?)
            })
            .map(|_| false),
        Reply::Rejected { envelope, eligible } => storage
            .call(false, move |s| {
                s.reject_delivery(
                    &copy,
                    &envelope,
                    &eligible,
                    raw.as_deref().ok_or("invalid_utf8")?,
                )
            })
            .map(|_| false),
        Reply::Failure {
            state,
            error,
            delay,
            pause,
            protocol,
        } => {
            let id = frozen.batch.batch_id.clone();
            storage
                .call(false, move |s| {
                    s.fail_delivery(&id, &state, &error, retry.unwrap_or(delay), protocol)
                })
                .map(|stop| stop || pause)
        }
    };
    match result {
        Ok(stop) => Ok(ApplyOutcome { pause: stop }),
        Err(error) => {
            let id = frozen.batch.batch_id.clone();
            let code = if error.starts_with("storage") {
                "ack_persistence_unknown"
            } else {
                "delivery_commit_unknown"
            };
            let _ = storage.call(false, move |s| {
                s.fail_delivery(&id, "unknown", code, 1, false)
            });
            Err(error)
        }
    }
}
#[cfg(test)]
#[path = "local_delivery_tests.rs"]
mod tests;

/// Monotonic milliseconds are injected; wall time is consulted only when a frozen batch first enters memory.
#[derive(Default)]
pub(crate) struct RetryClock {
    pub deadlines: std::collections::BTreeMap<String, u64>,
}
impl RetryClock {
    pub fn sync(&mut self, rows: &[(String, String)], wall: &str, ticks: u64) -> LocalResult<()> {
        let live = rows
            .iter()
            .map(|r| r.0.as_str())
            .collect::<std::collections::BTreeSet<_>>();
        self.deadlines.retain(|id, _| live.contains(id.as_str()));
        let now = crate::domain::facts_wire::time(wall)?;
        for (id, at) in rows {
            if !self.deadlines.contains_key(id) {
                let wait = (crate::domain::facts_wire::time(at)? - now)
                    .num_seconds()
                    .clamp(1, 300) as u32;
                self.schedule(id, ticks, wait);
            }
        }
        Ok(())
    }
    pub fn schedule(&mut self, id: &str, ticks: u64, seconds: u32) {
        self.deadlines.insert(
            id.into(),
            ticks.saturating_add(u64::from(seconds.clamp(1, 300)) * 1000),
        );
    }
    #[cfg(test)]
    pub fn ready(&self, ticks: u64) -> Vec<String> {
        let mut rows = self
            .deadlines
            .iter()
            .filter(|(_, due)| **due <= ticks)
            .collect::<Vec<_>>();
        rows.sort_by(|a, b| a.1.cmp(b.1).then(a.0.cmp(b.0)));
        rows.into_iter().map(|(id, _)| id.clone()).collect()
    }
}
#[cfg(test)]
pub(crate) struct ApplyOutcome {
    pub pause: bool,
}
