//! 本地样本v1：按点ID排序的无损JSON、SHA及同轮完整manifest；不可变字段与ACK分离。
use super::local_configuration::{id, Point};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
pub(crate) fn now() -> String {
    chrono::Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true)
}
pub(crate) fn digest(s: &str) -> String {
    format!("{:x}", Sha256::digest(s.as_bytes()))
}
pub(crate) fn encode<T: Serialize>(v: &T) -> Result<String, String> {
    serde_json::to_string(v).map_err(|_| "encoding_failed".into())
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PointFact {
    pub definition: Point,
    pub value: Value,
    pub observed_at: String,
    pub quality: String,
    pub reason: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ReadTiming {
    pub db_number: u16,
    pub start: u32,
    pub size: u32,
    pub started_at: String,
    pub finished_at: String,
    pub duration_ms: u64,
    pub quality: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct CycleInput {
    pub plc_id: String,
    pub group_id: String,
    pub revision: String,
    pub started_at: String,
    pub finished_at: String,
    pub origin: String,
    pub points: BTreeMap<u16, BTreeMap<String, PointFact>>,
    pub reads: Vec<ReadTiming>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct SamplePayload {
    pub schema_version: u32,
    pub sample_id: String,
    pub cycle_id: String,
    pub instance_id: String,
    pub plc_id: String,
    pub source_generation: String,
    pub source_seq: String,
    pub group_id: String,
    pub revision: String,
    pub db_number: u16,
    pub origin: String,
    pub started_at: String,
    pub finished_at: String,
    pub saved_at: String,
    pub points: BTreeMap<String, PointFact>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ManifestSample {
    pub sample_id: String,
    pub db_number: u16,
    pub sha256: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct CycleManifest {
    pub schema_version: u32,
    pub cycle_id: String,
    pub plc_id: String,
    pub source_generation: String,
    pub source_seq: String,
    pub group_id: String,
    pub revision: String,
    pub started_at: String,
    pub finished_at: String,
    pub saved_at: String,
    pub expected_point_ids: Vec<String>,
    pub samples: Vec<ManifestSample>,
    pub reads: Vec<ReadTiming>,
}
pub(crate) fn cycle_id() -> String {
    id()
}
