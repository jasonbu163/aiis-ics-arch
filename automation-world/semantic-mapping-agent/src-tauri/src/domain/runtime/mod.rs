//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/domain/runtime/mod.rs
//! Description: Shared managed-runtime lifecycle state for TSS r3.
//! Main Features:
//!   - Enforces one active run per runtime type
//!   - Tracks pause, resume, stop, counters, cursor, and structured events
//!   - Owns non-Flow connection and device DTOs used by Tauri adapters

use std::collections::VecDeque;
use std::sync::{Arc, Mutex, MutexGuard};
use std::time::{SystemTime, UNIX_EPOCH};

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct RuntimeStartRequest {
    pub channel: String,
    pub source_key: String,
    pub stream_key: String,
    pub interval_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct RuntimeLogEntry {
    pub sequence: u64,
    pub timestamp: String,
    pub event: String,
    pub runtime_type: String,
    pub run_id: Option<String>,
    pub result: String,
    pub error_code: Option<String>,
    pub message: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct RuntimeSnapshot {
    pub runtime_type: String,
    pub status: String,
    pub run_id: Option<String>,
    pub channel: Option<String>,
    pub profile_id: Option<String>,
    pub profile_version: Option<String>,
    pub profile_hash: Option<String>,
    pub processed_items: u64,
    pub successful_transactions: u64,
    pub failed_transactions: u64,
    pub cursor: Option<String>,
    pub last_error_code: Option<String>,
    pub last_error_message: Option<String>,
    pub logs: Vec<RuntimeLogEntry>,
}

#[derive(Clone)]
pub struct ManagedRuntimeState {
    runtime_type: &'static str,
    inner: Arc<Mutex<RuntimeControl>>,
}

#[derive(Debug)]
struct RuntimeControl {
    status: String,
    run_id: Option<String>,
    channel: Option<String>,
    profile_id: Option<String>,
    profile_version: Option<String>,
    profile_hash: Option<String>,
    pause_requested: bool,
    stop_requested: bool,
    processed_items: u64,
    successful_transactions: u64,
    failed_transactions: u64,
    cursor: Option<String>,
    last_error_code: Option<String>,
    last_error_message: Option<String>,
    log_sequence: u64,
    logs: VecDeque<RuntimeLogEntry>,
}

impl ManagedRuntimeState {
    pub fn new(runtime_type: &'static str) -> Self {
        Self {
            runtime_type,
            inner: Arc::new(Mutex::new(RuntimeControl::default())),
        }
    }

    pub fn snapshot(&self) -> RuntimeSnapshot {
        let control = self.lock();
        RuntimeSnapshot {
            runtime_type: self.runtime_type.to_string(),
            status: control.status.clone(),
            run_id: control.run_id.clone(),
            channel: control.channel.clone(),
            profile_id: control.profile_id.clone(),
            profile_version: control.profile_version.clone(),
            profile_hash: control.profile_hash.clone(),
            processed_items: control.processed_items,
            successful_transactions: control.successful_transactions,
            failed_transactions: control.failed_transactions,
            cursor: control.cursor.clone(),
            last_error_code: control.last_error_code.clone(),
            last_error_message: control.last_error_message.clone(),
            logs: control.logs.iter().cloned().collect(),
        }
    }

    pub fn start(&self, request: &RuntimeStartRequest, run_id: String) -> Result<(), String> {
        validate_channel(&request.channel)?;
        if request.interval_ms == 0 || request.interval_ms > 86_400_000 {
            return Err("TWIN_RUNTIME_INTERVAL_INVALID".to_string());
        }
        let mut control = self.lock();
        if is_active(&control.status) {
            return Err(format!(
                "{}_RUNTIME_ALREADY_ACTIVE",
                self.runtime_type.to_uppercase()
            ));
        }
        *control = RuntimeControl::default();
        control.status = "starting".to_string();
        control.run_id = Some(run_id);
        control.channel = Some(request.channel.clone());
        Ok(())
    }

    pub fn set_running(&self) {
        let mut control = self.lock();
        if control.status == "starting" {
            control.status = "running".to_string();
        }
    }

    pub fn set_profile_identity(
        &self,
        profile_id: &str,
        profile_version: &str,
        profile_hash: &str,
    ) {
        let mut control = self.lock();
        control.profile_id = Some(profile_id.to_string());
        control.profile_version = Some(profile_version.to_string());
        control.profile_hash = Some(profile_hash.to_string());
    }

    pub fn request_pause(&self) -> Result<(), String> {
        let mut control = self.lock();
        if control.status != "running" {
            return Err(format!(
                "{}_RUNTIME_NOT_RUNNING",
                self.runtime_type.to_uppercase()
            ));
        }
        control.pause_requested = true;
        Ok(())
    }

    pub fn acknowledge_pause(&self) {
        let mut control = self.lock();
        if control.status == "running" && control.pause_requested {
            control.status = "paused".to_string();
        }
    }

    pub fn resume(&self) -> Result<(), String> {
        let mut control = self.lock();
        if control.status != "paused" {
            return Err(format!(
                "{}_RUNTIME_NOT_PAUSED",
                self.runtime_type.to_uppercase()
            ));
        }
        control.pause_requested = false;
        control.status = "running".to_string();
        Ok(())
    }

    pub fn request_stop(&self) -> Result<(), String> {
        let mut control = self.lock();
        if !is_active(&control.status) {
            return Err(format!(
                "{}_RUNTIME_NOT_ACTIVE",
                self.runtime_type.to_uppercase()
            ));
        }
        control.pause_requested = false;
        control.stop_requested = true;
        control.status = "stopping".to_string();
        Ok(())
    }

    pub fn should_stop(&self) -> bool {
        self.lock().stop_requested
    }

    pub fn pause_requested(&self) -> bool {
        self.lock().pause_requested
    }

    pub fn is_paused(&self) -> bool {
        self.lock().status == "paused"
    }

    pub fn record_success(&self, count: u64, cursor: Option<String>) {
        let mut control = self.lock();
        control.processed_items = control.processed_items.saturating_add(count);
        control.successful_transactions = control.successful_transactions.saturating_add(1);
        control.cursor = cursor;
        control.last_error_code = None;
        control.last_error_message = None;
    }

    pub fn record_failure(&self, code: &str, message: &str) {
        let mut control = self.lock();
        control.failed_transactions = control.failed_transactions.saturating_add(1);
        control.last_error_code = Some(code.to_string());
        control.last_error_message = Some(message.to_string());
    }

    pub fn finish(&self, status: &str) {
        let mut control = self.lock();
        control.status = status.to_string();
        control.pause_requested = false;
        control.stop_requested = false;
    }

    pub fn log(
        &self,
        timestamp: String,
        event: &str,
        result: &str,
        code: Option<&str>,
        message: &str,
    ) {
        let mut control = self.lock();
        control.log_sequence = control.log_sequence.saturating_add(1);
        let entry = RuntimeLogEntry {
            sequence: control.log_sequence,
            timestamp,
            event: event.to_string(),
            runtime_type: self.runtime_type.to_string(),
            run_id: control.run_id.clone(),
            result: result.to_string(),
            error_code: code.map(ToString::to_string),
            message: message.to_string(),
        };
        control.logs.push_back(entry);
        while control.logs.len() > 200 {
            control.logs.pop_front();
        }
    }

    fn lock(&self) -> MutexGuard<'_, RuntimeControl> {
        self.inner.lock().unwrap_or_else(|error| error.into_inner())
    }
}

impl Default for RuntimeControl {
    fn default() -> Self {
        Self {
            status: "idle".to_string(),
            run_id: None,
            channel: None,
            profile_id: None,
            profile_version: None,
            profile_hash: None,
            pause_requested: false,
            stop_requested: false,
            processed_items: 0,
            successful_transactions: 0,
            failed_transactions: 0,
            cursor: None,
            last_error_code: None,
            last_error_message: None,
            log_sequence: 0,
            logs: VecDeque::new(),
        }
    }
}

fn is_active(status: &str) -> bool {
    matches!(status, "starting" | "running" | "paused" | "stopping")
}

pub fn validate_channel(channel: &str) -> Result<(), String> {
    if matches!(channel, "incremental" | "current" | "both") {
        Ok(())
    } else {
        Err("TWIN_RUNTIME_CHANNEL_UNSUPPORTED".to_string())
    }
}

pub fn runtime_run_id(runtime_type: &str) -> String {
    let millis = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis();
    format!("{runtime_type}-{millis}")
}

pub fn utc_now_string() -> String {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    let seconds = duration.as_secs() as i64;
    let millis = duration.subsec_millis();
    let days = seconds.div_euclid(86_400);
    let day_seconds = seconds.rem_euclid(86_400);
    let (year, month, day) = civil_from_days(days);
    let hour = day_seconds / 3_600;
    let minute = (day_seconds % 3_600) / 60;
    let second = day_seconds % 60;
    format!("{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{millis:03}Z")
}

fn civil_from_days(days: i64) -> (i32, u32, u32) {
    let days = days + 719_468;
    let era = if days >= 0 { days } else { days - 146_096 } / 146_097;
    let day_of_era = days - era * 146_097;
    let year_of_era =
        (day_of_era - day_of_era / 1_460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let mut year = year_of_era + era * 400;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let month_prime = (5 * day_of_year + 2) / 153;
    let day = day_of_year - (153 * month_prime + 2) / 5 + 1;
    let month = month_prime + if month_prime < 10 { 3 } else { -9 };
    year += i64::from(month <= 2);
    (year as i32, month as u32, day as u32)
}
