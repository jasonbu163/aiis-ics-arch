//! 采集回环配置、临时点值和预览的 IPC 合同。
use serde::{Deserialize, Serialize};
use serde_json::value::RawValue;

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct LoopbackConfig {
    pub material_key: String,
    pub plc_id: String,
    pub db_number: u16,
    pub point_ids: Vec<String>,
    pub target: TargetIdentity,
    pub moves: Vec<PointMove>,
    pub group_id: Option<String>,
    pub config_revision: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct TargetIdentity {
    pub plc_id: String,
    pub db_number: u16,
    pub instance_id: String,
    pub source_generation: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PointMove {
    pub from: String,
    pub to: Option<String>,
    pub name: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Point {
    pub point_id: String,
    #[serde(default)]
    pub name: String,
    pub data_type: String,
    pub value: Box<RawValue>,
    pub quality: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reason: Option<String>,
    pub observed_at: String,
}
