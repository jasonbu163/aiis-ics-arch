//! 显式源识别/逐块映射/不可变闭包与预览DTO；无SQL或文件I/O。
use super::local_configuration::*;
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct BlockKey {
    pub kind: String,
    pub name: String,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct ImportBinding {
    pub block_key: BlockKey,
    pub lineage_id: String,
    pub udt_source_ids: Vec<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct BlockMapping {
    pub source_index: usize,
    pub block_key: BlockKey,
    pub selected: bool,
    pub db_number: Option<u16>,
    pub target_id: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct RawProof {
    pub sha256: String,
    pub bytes: usize,
}
#[derive(Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct ImportRequest {
    pub sources: Vec<SourceDocument>,
    pub expected_etag: String,
    pub confirm: bool,
    pub stage: Option<String>,
    pub target_plc_id: Option<String>,
    #[serde(default)]
    pub mappings: Vec<BlockMapping>,
    pub preview_token: Option<String>,
    #[serde(default)]
    pub raw_proofs: Vec<RawProof>,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct IdentifiedBlock {
    pub source_index: usize,
    pub block_key: BlockKey,
    pub file: String,
    pub line: usize,
    pub leaf_count: usize,
    pub issues: Vec<Issue>,
    pub suggested_db_number: Option<u16>,
    pub target_id: Option<String>,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct Identification {
    pub blocks: Vec<IdentifiedBlock>,
    pub file_count: usize,
    pub db_count: usize,
    pub udt_count: usize,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct DbDelta {
    pub db_id: String,
    pub block_name: String,
    pub number: u16,
    pub status: String,
    pub added_paths: Vec<String>,
    pub type_changed_paths: Vec<String>,
    pub removed_paths: Vec<String>,
    pub layout_changed: bool,
    pub comments_changed: bool,
    pub preserved_points: usize,
    pub preserved_manual: usize,
    pub invalidated_confirmations: usize,
    pub isolated_udt_versions: bool,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ImportPreview {
    pub configuration: Configuration,
    pub changes: Vec<String>,
    pub issues: Vec<Issue>,
    pub readiness: Vec<Issue>,
    pub deltas: Vec<DbDelta>,
    pub name_changes: Vec<super::point_naming::NameChange>,
    pub can_confirm: bool,
    pub unchanged: bool,
    pub preview_token: Option<String>,
    pub input_digest: String,
    pub etag: String,
}
