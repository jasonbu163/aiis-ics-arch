//! SMA HTTP 配置、来源最新快照及单次投递的本地 IPC 合同。
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct HttpSource {
    pub id: String,
    pub source_key: String,
    pub name: String,
    pub url: String,
    #[serde(default)]
    pub query: BTreeMap<String, String>,
    pub interval_ms: u64,
    pub timeout_ms: u64,
    pub enabled: bool,
    #[serde(default)]
    pub response_path: Option<String>,
    #[serde(default)]
    pub response_condition: Option<ResponseCondition>,
    pub points: Vec<HttpPoint>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct HttpPoint {
    pub point_key: String,
    pub name: String,
    pub data_type: String,
    pub path: String,
    #[serde(default)]
    pub selector: Option<PointSelector>,
    #[serde(default)]
    pub quality_path: Option<String>,
    #[serde(default)]
    pub observed_at_path: Option<String>,
    #[serde(default)]
    pub sample_id_path: Option<String>,
    #[serde(default)]
    pub accepted_quality: Vec<String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PointSelector {
    pub path: String,
    pub key: String,
    pub value: Value,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ResponseCondition {
    pub path: String,
    pub equals: Value,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RuntimeLimits {
    pub get_concurrency: usize,
    pub get_queue: usize,
    pub post_concurrency: usize,
    pub post_queue: usize,
    pub per_target_concurrency: usize,
}

impl Default for RuntimeLimits {
    fn default() -> Self {
        Self {
            get_concurrency: 8,
            get_queue: 128,
            post_concurrency: 8,
            post_queue: 384,
            per_target_concurrency: 2,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PointReading {
    pub point_key: String,
    pub value: Option<Value>,
    pub quality: Option<String>,
    pub observed_at: Option<String>,
    pub sample_id: Option<String>,
    pub error_code: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SourceSnapshot {
    pub source_key: String,
    pub version: u64,
    pub collected_at: String,
    pub points: Vec<PointReading>,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SourceState {
    pub source_key: String,
    pub last_attempt_at: Option<String>,
    pub last_error_code: Option<String>,
    pub from_previous_session: bool,
    pub snapshot: Option<SourceSnapshot>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SourceTest {
    pub source_key: String,
    pub http_status: Option<u16>,
    pub response: Option<Value>,
    pub points: Vec<PointReading>,
    pub error_code: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SourceReference {
    pub source_key: String,
    pub version: Option<u64>,
    pub collected_at: Option<String>,
    pub points: Vec<PointReading>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PreparedPost {
    pub method: &'static str,
    pub url: String,
    pub headers: Vec<(String, String)>,
    pub body: Value,
    #[serde(skip)]
    pub timeout_ms: u64,
    #[serde(skip)]
    pub receipt: Option<ResponseCondition>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PostPreview {
    pub token: Option<String>,
    pub revision: u64,
    pub request: Option<PreparedPost>,
    pub sources: Vec<SourceReference>,
    pub diagnostics: Vec<crate::domain::mapping_runtime::MappingRuntimeDiagnostic>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PostResult {
    pub run_id: String,
    pub status: &'static str,
    pub http_status: Option<u16>,
    pub error_code: Option<String>,
    pub response: Option<Value>,
    pub finished_at: String,
    pub sources: Vec<SourceReference>,
    pub diagnostics: Vec<crate::domain::mapping_runtime::MappingRuntimeDiagnostic>,
}
