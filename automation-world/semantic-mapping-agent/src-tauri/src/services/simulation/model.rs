//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/simulation/model.rs
//! Description: Backend HTTP contracts for collection-fact Simulation.
//! Main Features:
//!   - Separates the active HTTP start request from retired page-rule test input
//!   - Carries only Backend facts, rules, and Values API payloads used by Runtime

use serde::{Deserialize, Serialize};

/// Retained only for an ignored historical integration test. It is not an
/// active Tauri command input and cannot start the HTTP Simulation Runtime.
#[doc(hidden)]
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CollectionSimulationStartRequest {
    pub source_key: String,
    #[serde(default)]
    pub rules: Vec<SimulationRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CollectionSimulationHttpStartRequest {
    pub backend_base_url: String,
    pub source_key: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SimulationRule {
    pub fact_name: String,
    #[serde(default)]
    pub sequence: Vec<serde_json::Value>,
    pub interval_ms: u64,
    #[serde(default)]
    pub enabled: bool,
    #[serde(default)]
    pub write_current_time: bool,
    #[serde(default = "default_current_time_mode")]
    pub current_time_mode: String,
    #[serde(default)]
    pub current_time_zone: Option<String>,
}

fn default_current_time_mode() -> String {
    "utc".to_string()
}

#[derive(Debug, Clone, PartialEq)]
pub struct SimulationFact {
    pub source_key: String,
    pub name: String,
    pub fact_kind: String,
    pub data_type: String,
    pub value_text: Option<String>,
    pub contract_version: String,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendEnvelope<T> {
    pub code: u16,
    pub data: Option<T>,
    #[serde(default)]
    pub message: Option<String>,
    #[serde(default)]
    pub error_code: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendCollectionFactPage {
    pub items: Vec<BackendCollectionFact>,
    pub page: u64,
    pub page_size: u64,
    pub total: u64,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendCollectionFact {
    pub source_key: String,
    pub name: String,
    pub fact_kind: String,
    pub data_type: String,
    pub value: Option<String>,
    pub contract_version: String,
}

impl From<BackendCollectionFact> for SimulationFact {
    fn from(value: BackendCollectionFact) -> Self {
        Self {
            source_key: value.source_key,
            name: value.name,
            fact_kind: value.fact_kind,
            data_type: value.data_type,
            value_text: value.value,
            contract_version: value.contract_version,
        }
    }
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendSimulationRule {
    pub source_key: String,
    pub fact_name: String,
    pub sequence: Vec<serde_json::Value>,
    pub interval_ms: u64,
    pub enabled: bool,
    #[serde(default)]
    pub write_current_time: bool,
    #[serde(default = "default_current_time_mode")]
    pub current_time_mode: String,
    #[serde(default)]
    pub current_time_zone: Option<String>,
}

impl From<BackendSimulationRule> for SimulationRule {
    fn from(value: BackendSimulationRule) -> Self {
        Self {
            fact_name: value.fact_name,
            sequence: value.sequence,
            interval_ms: value.interval_ms,
            enabled: value.enabled,
            write_current_time: value.write_current_time,
            current_time_mode: value.current_time_mode,
            current_time_zone: value.current_time_zone,
        }
    }
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactValueWrite {
    pub name: String,
    pub value: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactValuesWriteRequest {
    pub contract_version: String,
    pub values: Vec<CollectionFactValueWrite>,
}
