//! YAML一次性迁入v1：安全摘要与服务私有receipt；不提供文件备份或运行模式。
#[cfg(test)]
use crate::domain::local_configuration::Configuration;
use crate::domain::local_configuration::Issue;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
#[cfg(test)]
use std::path::PathBuf;
pub(crate) const PRIVATE_NAME: &str = "__daa_yaml_migration_v1__";
#[cfg(test)]
pub(crate) const SOURCE_LIMIT: usize = 1024 * 1024;
pub(crate) const RECEIPT_LIMIT: usize = 8 * 1024 * 1024;
#[cfg(test)]
#[derive(Clone)]
pub(crate) struct MigrationPaths {
    pub points: PathBuf,
    pub points_origin: String,
    pub policy: PathBuf,
    pub policy_origin: String,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Counts {
    pub plcs: usize,
    pub dbs: usize,
    pub groups: usize,
    pub points: usize,
    pub policy_plcs: usize,
    pub policy_groups: usize,
    pub policy_points: usize,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct SourceInfo {
    pub kind: String,
    pub path: String,
    pub origin: String,
    pub bytes: Option<u64>,
    pub sha256: Option<String>,
    pub hash_unavailable: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct MigrationSummary {
    pub status: String,
    pub status_persistence: String,
    pub attempt_id: Option<String>,
    pub committed_etag: Option<String>,
    pub committed_at: Option<String>,
    pub counts: Counts,
    pub sources: Vec<SourceInfo>,
    pub diagnostics: Vec<Issue>,
    pub diagnostic_total: usize,
    pub diagnostic_omitted: usize,
    pub error_code: Option<String>,
    pub retry_allowed: bool,
}
impl MigrationSummary {
    pub fn state(status: &str) -> Self {
        Self {
            status: status.into(),
            status_persistence: "not_required".into(),
            attempt_id: None,
            committed_etag: None,
            committed_at: None,
            counts: Counts::default(),
            sources: vec![],
            diagnostics: vec![],
            diagnostic_total: 0,
            diagnostic_omitted: 0,
            error_code: None,
            retry_allowed: false,
        }
    }
    #[cfg(test)]
    pub fn diagnostic(&mut self, code: &str, path: &str) {
        self.diagnostic_total += 1;
        if self.diagnostics.len() < 200 {
            self.diagnostics
                .push(crate::domain::local_configuration::issue(code, path));
        }
        self.diagnostic_omitted = self.diagnostic_total - self.diagnostics.len();
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Receipt {
    pub yaml_migration_version: u32,
    pub summary: MigrationSummary,
    pub archive: serde_json::Value,
    pub ids: BTreeMap<String, String>,
}
#[cfg(test)]
pub(crate) struct Candidate {
    pub configuration: Configuration,
    pub receipt: Receipt,
}
#[cfg(test)]
pub(crate) fn retryable(status: &str) -> bool {
    matches!(status, "failed" | "skipped_empty" | "archived_policy_only")
}
