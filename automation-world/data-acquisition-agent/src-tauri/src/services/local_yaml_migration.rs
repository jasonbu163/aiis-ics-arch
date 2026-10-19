//! 锁后一次性迁入用例：既有SQLite先行；失败可编辑，重试须空实例及双CAS。
use crate::{
    domain::{local_configuration::*, yaml_migration::*},
    infrastructure::{local_store::Stores, yaml_migration},
    services::local_supervisor::LocalEngine,
};
use std::time::Instant;
fn failed(code: &str) -> MigrationSummary {
    let mut s = MigrationSummary::state("failed");
    s.error_code = Some(
        code.split(':')
            .next()
            .unwrap_or("yaml_migration_failed")
            .into(),
    );
    s.status_persistence = "unknown".into();
    s.diagnostic("yaml_status_persistence_unknown", "migration");
    s
}
fn execute(
    stores: &mut Stores,
    paths: &MigrationPaths,
    etag: &str,
    attempt: Option<&str>,
    retry: bool,
) -> MigrationSummary {
    let start = Instant::now();
    let attempt_id = id();
    let event = if retry {
        "yaml_migration_retry"
    } else {
        "yaml_migration_start"
    };
    let context =
        serde_json::json!({"resource":"yaml_migration","attemptId":attempt_id}).to_string();
    if let Err(e) = stores.log.event(event, &context, "started") {
        return failed(&e);
    }
    let mut c = yaml_migration::discover(paths);
    c.receipt.summary.attempt_id = Some(attempt_id.clone());
    let mut fallback = c.receipt.summary.clone();
    let result = stores.commit_yaml(c, etag, attempt);
    let summary = match result {
        Ok(v) => v,
        Err(e) => {
            fallback.status = "failed".into();
            fallback.status_persistence = "unknown".into();
            fallback.error_code = Some(e.split(':').next().unwrap_or("storage_error").into());
            fallback.retry_allowed = false;
            fallback.diagnostic("yaml_status_persistence_unknown", "migration");
            fallback
        }
    };
    let event = if summary.status == "failed" {
        "yaml_migration_failed"
    } else if summary.status == "skipped_empty" {
        "yaml_migration_skipped"
    } else {
        "yaml_migration_committed"
    };
    let context=serde_json::json!({"resource":"yaml_migration","attemptId":attempt_id,"counts":summary.counts,"duration_ms":start.elapsed().as_millis() as u64,"error_code":summary.error_code,"sourceSha256":summary.sources.iter().map(|s|s.sha256.clone()).collect::<Vec<_>>()}).to_string();
    let _ = stores.log.event(event, &context, &summary.status);
    tracing::info!(event, process="daa-local", resource="yaml_migration", result=%summary.status,
        error_code=?summary.error_code, attemptId=%attempt_id, counts=?summary.counts,
        source_sha=?summary.sources.iter().map(|s|s.sha256.clone()).collect::<Vec<_>>(), duration_ms=start.elapsed().as_millis() as u64);
    summary
}
pub(crate) fn startup(stores: &mut Stores, paths: Option<&MigrationPaths>) -> MigrationSummary {
    let Some(paths) = paths else {
        return MigrationSummary::state("validation_excluded");
    };
    let state = match stores.yaml_summary() {
        Ok(s) => s,
        Err(e) => return failed(&e),
    };
    if state.status != "not_attempted" {
        let _ = stores
            .log
            .event("yaml_migration_skipped", "sqlite", &state.status);
        return state;
    }
    match stores.configuration() {
        Ok(v) => execute(stores, paths, &v.etag, None, false),
        Err(e) => failed(&e),
    }
}
impl LocalEngine {
    pub fn yaml_migration(&self) -> LocalResult<MigrationSummary> {
        let fallback = self.migration_state.lock().unwrap().clone();
        if fallback.status_persistence == "unknown" {
            return Ok(fallback);
        }
        if self.bootstrap.validation {
            return Ok(fallback);
        }
        self.storage.call(true, |s| s.yaml_summary())
    }
    pub fn retry_yaml(&self, etag: String, attempt: String) -> LocalResult<MigrationSummary> {
        let paths = self
            .bootstrap
            .migration
            .clone()
            .ok_or("yaml_retry_forbidden")?;
        let _guard = self.activation.lock().unwrap();
        let summary = self.storage.call(false, move |s| {
            let state = s.yaml_summary()?;
            if s.configuration()?.etag != etag {
                return Err("draft_conflict".into());
            }
            if state.attempt_id.as_deref() != Some(&attempt) {
                return Err("yaml_attempt_conflict".into());
            }
            if !state.retry_allowed || !s.yaml_empty()? {
                return Err("yaml_retry_forbidden".into());
            }
            Ok(execute(s, &paths, &etag, Some(&attempt), true))
        })?;
        *self.migration_state.lock().unwrap() = summary.clone();
        Ok(summary)
    }
}
