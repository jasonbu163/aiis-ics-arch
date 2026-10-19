//! 本地状态与IPC v1 DTO：意图、实态、准入、持久版本和有限查询分别表达。
use super::local_configuration::{Configuration, Issue};
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ConfigurationView {
    pub schema_version: u32,
    pub draft: Configuration,
    pub etag: String,
    pub active: Option<String>,
    pub previous: Option<String>,
    pub loaded: Option<String>,
    pub used: Option<String>,
    pub phase: String,
    pub issues: Vec<Issue>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PlcState {
    pub plc_id: String,
    pub desired_connection: bool,
    pub desired_collection: bool,
    pub connected: bool,
    pub phase: String,
    pub admission: String,
    pub error: Option<String>,
    pub saved_cycles: u64,
    pub used_revision: Option<String>,
    pub groups: Vec<GroupState>,
}
impl PlcState {
    pub fn new(id: &str) -> Self {
        Self {
            plc_id: id.into(),
            desired_connection: false,
            desired_collection: false,
            connected: false,
            phase: "disconnected".into(),
            admission: "stopped".into(),
            error: None,
            saved_cycles: 0,
            used_revision: None,
            groups: vec![],
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct GroupState {
    pub group_id: String,
    pub interval_ms: u64,
    pub duration_ms: u64,
    pub missed_ticks: u64,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct Capacity {
    pub main_bytes: u64,
    pub journal_bytes: u64,
    pub config_bytes: u64,
    pub config_journal_bytes: u64,
    pub log_bytes: u64,
    pub free_bytes: u64,
    pub quota_bytes: u64,
    pub reserved_bytes: u64,
    pub page_count: u64,
    pub freelist_count: u64,
    pub pending_count: u64,
    pub pending_bytes: u64,
    pub oldest_pending: Option<String>,
    pub state: String,
    pub admission: bool,
    pub busy_count: u64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct Operation {
    pub operation_id: String,
    pub plc_id: String,
    pub action: String,
    pub phase: String,
    pub reason: Option<String>,
    pub result: Option<serde_json::Value>,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct HistoryQuery {
    pub plc_id: Option<String>,
    pub group_id: Option<String>,
    pub from: Option<String>,
    pub to: Option<String>,
    pub quality: Option<String>,
    pub cursor: Option<i64>,
    pub limit: Option<u32>,
}
