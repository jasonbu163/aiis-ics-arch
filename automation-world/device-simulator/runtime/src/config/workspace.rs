//! IPC的严格值合同：白名单意图、UUID操作身份与十进制u64，不接受任意raw/SQL。
use serde::{Deserialize, Serialize};
use serde_json::Value;
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Operation<T> {
    pub operation_id: String,
    pub payload: T,
}
impl<T> Operation<T> {
    pub fn validate(&self) -> Result<(), String> {
        uuid::Uuid::parse_str(&self.operation_id)
            .map(|_| ())
            .map_err(|_| "operation_identity".into())
    }
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Response<T> {
    pub result: String,
    pub error_code: Option<String>,
    pub committed: Option<bool>,
    pub receipt_state: String,
    pub current_etag: Option<String>,
    pub data: Option<T>,
}
impl Response<Value> {
    pub fn from_result(result: Result<Value, String>, command_mutates: bool) -> Self {
        match result {
            Ok(data) => {
                let changed = data
                    .get("committed")
                    .and_then(Value::as_bool)
                    .unwrap_or_else(|| {
                        command_mutates
                            && !matches!(
                                data.get("result").and_then(Value::as_str),
                                Some("unchanged" | "already_loaded")
                            )
                    });
                Self {
                    result: "ok".into(),
                    error_code: None,
                    committed: Some(changed),
                    receipt_state: "known".into(),
                    current_etag: None,
                    data: Some(data),
                }
            }
            Err(error) => {
                let (code, detail) = error.split_once(':').unwrap_or((&error, ""));
                let unknown = matches!(
                    code,
                    "apply_receipt_unknown"
                        | "save_receipt_unknown"
                        | "save_commit_unknown"
                        | "selection_receipt_unknown"
                        | "selection_commit_unknown"
                        | "runtime_task_receipt_unknown"
                        | "ipc_transport_unknown"
                );
                let selected_committed = code == "load_failed_after_selection_commit";
                let facts = if selected_committed || code == "load_failed" {
                    serde_json::from_str(detail).ok()
                } else {
                    None
                };
                Self {
                    result: if unknown { "unknown" } else { "error" }.into(),
                    error_code: Some(
                        if selected_committed {
                            "load_failed"
                        } else {
                            code
                        }
                        .into(),
                    ),
                    committed: if unknown {
                        None
                    } else {
                        Some(selected_committed)
                    },
                    receipt_state: if unknown { "unknown" } else { "known" }.into(),
                    current_etag: if code == "etag_conflict" {
                        Some(detail.into())
                    } else {
                        None
                    },
                    data: facts,
                }
            }
        }
    }
}

pub fn u64_value(s: &str) -> Result<u64, String> {
    if s.is_empty() || s.len() > 20 || !s.bytes().all(|b| b.is_ascii_digit()) {
        return Err("decimal_u64".into());
    }
    s.parse().map_err(|_| "decimal_u64".into())
}
#[derive(Default, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ConfigurationQuery {
    pub revision_id: Option<String>,
    #[serde(default)]
    pub revision_offset: u32,
}
fn page_size() -> u16 {
    50
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SnapshotQuery {
    pub instance_id: Option<String>,
    #[serde(default)]
    pub offset: u32,
    #[serde(default = "page_size")]
    pub limit: u16,
}
impl Default for SnapshotQuery {
    fn default() -> Self {
        Self {
            instance_id: None,
            offset: 0,
            limit: 50,
        }
    }
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Confirmation {
    pub expected_etag: String,
    pub token: String,
    pub candidate_sha256: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ControlIntent {
    pub instance_id: String,
    pub command: String,
    pub expected_loaded_revision: String,
    pub epoch: String,
    #[serde(default)]
    pub discard_values: bool,
}
#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WriteKind {
    Ordinary,
    Maintenance,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct WriteIntent {
    pub instance_id: String,
    pub point_id: String,
    pub expected_loaded_revision: String,
    pub epoch: String,
    pub point_seq: String,
    pub value: Value,
    pub source: WriteKind,
    #[serde(default)]
    pub confirmed: bool,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CloseIntent {
    pub instance_id: String,
    pub connection_id: String,
    pub expected_loaded_revision: String,
    pub epoch: String,
    pub confirmed: bool,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct LogsQuery {
    #[serde(default)]
    pub offset: u32,
    #[serde(default = "page_size")]
    pub limit: u16,
    pub event: Option<String>,
}
