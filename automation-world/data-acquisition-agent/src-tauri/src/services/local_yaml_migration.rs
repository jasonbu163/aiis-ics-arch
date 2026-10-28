//! 常驻迁入已退役：显式兼容摘要只读，retry写前拒绝；历史算法仅测试编译。
#[cfg(test)]
use crate::{
    domain::{local_configuration::id, yaml_migration::MigrationPaths},
    infrastructure::{local_store::Stores, yaml_migration},
};
use crate::{
    domain::{local_configuration::LocalResult, yaml_migration::MigrationSummary},
    services::local_supervisor::LocalEngine,
};
#[cfg(test)]
use std::time::Instant;
#[cfg(test)]
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
#[cfg(test)]
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
#[cfg(test)]
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
        self.storage.call(true, |s| {
            let mut summary = s.yaml_summary()?;
            summary.retry_allowed = false;
            Ok(summary)
        })
    }
    pub fn retry_yaml(&self, _etag: String, _attempt: String) -> LocalResult<MigrationSummary> {
        Err("yaml_retry_forbidden".into())
    }
}
