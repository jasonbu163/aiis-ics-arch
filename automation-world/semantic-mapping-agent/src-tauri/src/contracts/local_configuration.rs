//! SMA本地配置IPC合同：完整快照、CAS及显式导入意图，无事实值或运行权限。
use serde::{Deserialize, Serialize};
use serde_json::Value;

pub const MAX_BYTES: usize = 10 * 1024 * 1024;
pub const MAX_ITEMS: usize = 10_000;
pub const FORMAT: &str = "aiis.sma.configuration";
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ConfigurationDocument {
    pub connection: ConnectionProfile,
    pub catalog: Vec<Value>,
    pub materials: Vec<Value>,
    pub target_apis: Vec<Value>,
    pub mapping_value_rules: Vec<Value>,
    pub mappings: Vec<Value>,
    pub source_metadata: Vec<SourceMetadata>,
}
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ConnectionProfile {
    pub scheme: String,
    pub host: String,
    pub port: u16,
}
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SourceMetadata {
    pub source_key: String,
    pub fact_name: String,
    pub data_type: String,
    pub fact_kind: Option<String>,
    pub source_locator: String,
    pub definition_version: Option<String>,
}
impl Default for ConfigurationDocument {
    fn default() -> Self {
        Self {
            connection: ConnectionProfile {
                scheme: "http".into(),
                host: String::new(),
                port: 0,
            },
            catalog: vec![],
            materials: vec![],
            target_apis: vec![],
            mapping_value_rules: vec![],
            mappings: vec![],
            source_metadata: vec![],
        }
    }
}
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ConfigurationSnapshot {
    pub schema_version: u32,
    pub revision: u64,
    pub updated_at: String,
    pub document: ConfigurationDocument,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ConfigurationBackup {
    pub format: String,
    pub schema_version: u32,
    pub document: ConfigurationDocument,
}
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ChangeIntent {
    pub kind: String,
    pub resource: String,
    pub id: Option<String>,
    pub payload: Value,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ImportError {
    pub key: String,
    pub error_code: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ImportPreview {
    pub token: String,
    pub expected_revision: u64,
    pub created_keys: Vec<String>,
    pub updated_keys: Vec<String>,
    pub unchanged_keys: Vec<String>,
    pub deleted_keys: Vec<String>,
    pub errors: Vec<ImportError>,
}
