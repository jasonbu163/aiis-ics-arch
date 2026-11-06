//! 独立单上传worker：显式启停、网络在SQLite事务外，GET仅人工核对且永不生成ACK。
use super::local_supervisor::LocalEngine;
use crate::{
    domain::{
        facts_canonical as pf,
        local_configuration::LocalResult,
        local_delivery::{classify, DeliverySettings, Reply},
    },
    infrastructure::{
        facts_http::{FactsHttp, Transport, LATEST},
        local_store::delivery::Frozen,
    },
};
use serde_json::{json, Value};
use std::{
    sync::Arc,
    thread,
    time::{Duration, Instant},
};
#[derive(Default)]
pub(crate) struct DeliveryControl {
    pub running: bool,
    pub error: Option<String>,
    pub join: Option<thread::JoinHandle<()>>,
    pub retries: RetryClock,
}
impl LocalEngine {
    pub fn delivery_available(&self) -> LocalResult<bool> {
        if self.bootstrap.validation {
            return Ok(false);
        }
        self.storage.call(true, |s| s.delivery_available())
    }
    pub fn delivery_settings(&self) -> LocalResult<DeliverySettings> {
        self.storage.call(true, |s| s.delivery_settings())
    }
    pub fn save_delivery_settings(
        &self,
        mut settings: DeliverySettings,
        expected: String,
    ) -> LocalResult<DeliverySettings> {
        if self.bootstrap.validation {
            return Err("delivery_validation_forbidden".into());
        }
        if let Some(origin) = &settings.origin {
            settings.origin = Some(crate::domain::local_delivery::normalize_origin(origin)?);
        }
        settings.validate()?;
        self.storage
            .call(false, move |s| s.save_delivery_settings(settings, expected))
    }
    pub fn delivery_snapshot(&self) -> LocalResult<Value> {
        let c = self.delivery.lock().unwrap();
        let running = c.running;
        let error = c.error.clone();
        drop(c);
        let mut value = self
            .storage
            .call(true, move |s| s.delivery_snapshot(running))?;
        value["lastError"] = json!(error);
        if self.bootstrap.validation {
            value["available"] = json!(false);
            value["running"] = json!(false);
        }
        Ok(value)
    }
    pub fn set_delivery(self: &Arc<Self>, action: &str) -> LocalResult<Value> {
        self.set_delivery_using(action, || {
            Ok(Arc::new(FactsHttp::new()?) as Arc<dyn Transport>)
        })
    }
    fn set_delivery_using(
        self: &Arc<Self>,
        action: &str,
        make: impl FnOnce() -> LocalResult<Arc<dyn Transport>>,
    ) -> LocalResult<Value> {
        if !["start", "pause", "resume"].contains(&action) {
            return Err("invalid_request".into());
        }
        if action == "pause" {
            self.delivery.lock().unwrap().running = false;
            if self.delivery_available()? {
                self.storage.call(false, |s| {
                    s.delivery_control_event("delivery_paused", "paused")
                })?;
            }
            return self.delivery_snapshot();
        }
        if self.bootstrap.validation || !self.delivery_available()? {
            return Err("delivery_profile_upgrade_required".into());
        }
        self.log.health()?;
        let settings = self.delivery_settings()?;
        settings.validate()?;
        if settings.origin.is_none()
            || settings.sources.is_empty()
            || settings.adoption_reference.is_empty()
        {
            return Err("source_adoption_required".into());
        }
        let mut control = self.delivery.lock().unwrap();
        if control.running {
            drop(control);
            return self.delivery_snapshot();
        }
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
                    let result = engine.delivery_tick(transport.as_ref());
                    let interval = engine
                        .delivery_settings()
                        .map(|s| s.interval_seconds)
                        .unwrap_or(5);
                    next = Instant::now() + Duration::from_secs(u64::from(interval));
                    if let Err(error) = result {
                        let mut c = engine.delivery.lock().unwrap();
                        c.error = Some(error);
                        c.running = false;
                    }
                }
            }));
        }
        control.running = true;
        control.error = None;
        drop(control);
        self.storage.call(false, |s| {
            s.delivery_control_event("delivery_started", "running")
        })?;
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
    fn delivery_tick(&self, transport: &dyn Transport) -> LocalResult<()> {
        self.log.health()?;
        let permit = match self.delivery_http.try_lock() {
            Ok(p) => p,
            Err(_) => return Ok(()),
        };
        let schedule = self.storage.call(true, |s| s.delivery_schedule())?;
        let ticks = self
            .delivery_epoch
            .elapsed()
            .as_millis()
            .min(u128::from(u64::MAX)) as u64;
        let ready = {
            let mut control = self.delivery.lock().unwrap();
            control
                .retries
                .sync(&schedule, &crate::domain::business_time::now(), ticks)?;
            control.retries.ready(ticks)
        };
        let frozen = match self
            .storage
            .call(false, move |s| s.next_delivery_ready(ready))?
        {
            Some(f) => f,
            None => return Ok(()),
        };
        if !self.delivery.lock().unwrap().running {
            return Ok(());
        }
        let copy = frozen.clone();
        let attempt = self.storage.call(false, move |s| s.mark_dispatch(&copy))?;
        let response = transport.post(&frozen.origin, &frozen.body);
        drop(permit);
        let result = apply_response(&self.storage, &frozen, response, attempt)?;
        let ticks = self
            .delivery_epoch
            .elapsed()
            .as_millis()
            .min(u128::from(u64::MAX)) as u64;
        let mut control = self.delivery.lock().unwrap();
        if let Some(delay) = result.delay {
            control
                .retries
                .schedule(&frozen.batch.batch_id, ticks, delay);
        } else {
            control.retries.deadlines.remove(&frozen.batch.batch_id);
        }
        if result.pause {
            control.running = false;
        }
        Ok(())
    }

    pub fn delivery_endpoint_test(
        &self,
        q: crate::domain::local_delivery::ReadQuery,
    ) -> LocalResult<Value> {
        if self.bootstrap.validation || !self.delivery_available()? {
            return Err("delivery_validation_forbidden".into());
        }
        let (latest, mode, original, limit, parameters) = q.parameters()?;
        let material = self.storage.call(true, |s| s.facts_source_material())?;
        if !material["sources"]
            .as_array()
            .map(|a| a.iter().any(|p| p["plcId"] == q.plc_id))
            .unwrap_or(false)
        {
            return Err("unknown_plc".into());
        }
        let settings = self.delivery_settings()?;
        let permit = self
            .delivery_http
            .try_lock()
            .map_err(|_| "delivery_http_busy")?;
        let response = FactsHttp::new()?.get(
            settings.origin.as_deref().ok_or("target_missing")?,
            if latest {
                LATEST
            } else {
                crate::infrastructure::facts_http::HISTORY
            },
            &parameters,
        )?;
        drop(permit);
        if response.media_type.split(';').next().map(str::trim) != Some("application/json") {
            return Err("invalid_read_response".into());
        }
        let value = pf::parse(&response.body, 2 * 1024 * 1024)?;
        let (cursor, more, gap) = if response.status == 200 {
            crate::infrastructure::facts_http::validate_read(
                &value, &q.plc_id, &mode, original, limit,
            )?
        } else {
            crate::domain::local_delivery::valid_failure(&value, response.status)?;
            if value["errorCode"] == "plc_facts.binding_conflict" {
                self.delivery.lock().unwrap().running = false;
            }
            (None, false, true)
        };
        let code = if response.status != 200 {
            value["errorCode"]
                .as_str()
                .unwrap_or("invalid_read_response")
                .to_string()
        } else if gap {
            "read_gap".into()
        } else if more {
            "read_more".into()
        } else {
            "read_complete".into()
        };
        let plc = q.plc_id.clone();
        self.storage
            .call(false, move |s| s.read_result(&plc, &code))?;
        Ok(
            json!({"schemaVersion":1,"readOnly":true,"acknowledgesBatch":false,"coverageComplete":false,"status":response.status,"result":value,"responseUtf8":String::from_utf8(response.body).map_err(|_|"invalid_utf8")?,"nextCursor":cursor,"hasMore":more,"gap":gap,"scanComplete":!more&&!gap,"page":q.page.unwrap_or(1),"pageBudgetReached":q.page.unwrap_or(1)>=20&&more}),
        )
    }
}
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
                .map(|pause| ApplyOutcome {
                    pause,
                    delay: Some(delay),
                });
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
        Ok(stop) => Ok(ApplyOutcome {
            pause: stop,
            delay: retry,
        }),
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
        if rows.len() > 8 {
            return Err("delivery_queue_limit".into());
        }
        self.deadlines
            .retain(|id, _| rows.iter().any(|r| &r.0 == id));
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
pub(crate) struct ApplyOutcome {
    pub pause: bool,
    pub delay: Option<u32>,
}
