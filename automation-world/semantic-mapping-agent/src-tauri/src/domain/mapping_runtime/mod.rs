//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/domain/mapping_runtime/mod.rs
//! Description: Pure saved-Mapping per-cycle fact validation, request preflight, and audit fingerprints.
//! Main Features:
//!   - Builds Mapping snapshots from fresh Backend-owned facts and locked configuration
//!   - Resolves typed facts, constants, optional omissions, and value-rule membership per run
//!   - Produces deterministic delivery fingerprints without HTTP, database, or Tauri access

use std::collections::{BTreeMap, BTreeSet};

use chrono::DateTime;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendEnvelope<T> {
    pub code: i64,
    pub message: Option<String>,
    pub error_code: Option<String>,
    pub data: Option<T>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendManualRun {
    pub run_id: String,
    pub mapping_config_id: String,
    pub mapping_row_version: String,
    pub target_api_id: String,
    pub target_api_row_version: String,
    pub snapshot_id: String,
    pub status: String,
    pub error_code: Option<String>,
    pub http_status_class: Option<String>,
    pub response_summary: Option<String>,
    pub resolved_parameter_keys: Vec<String>,
    pub unresolved_parameter_keys: Vec<String>,
    pub resolved_parameter_count: usize,
    pub unresolved_parameter_count: usize,
    pub lease_expires_at: String,
    pub started_at: String,
    pub completed_at: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendManualRunClaim {
    pub claimed: bool,
    pub error_code: Option<String>,
    pub run: BackendManualRun,
    pub snapshot: Option<MappingRuntimeSnapshot>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MappingRuntimeSnapshot {
    pub snapshot_id: String,
    pub mapping: MappingConfiguration,
    pub target_api: TargetApi,
    pub facts: Vec<SnapshotFact>,
    pub value_rules: Vec<ValueRule>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendMappingRuntimeConfiguration {
    pub mapping: MappingConfiguration,
    pub target_api: TargetApi,
    pub points: Vec<MappingRuntimePoint>,
    pub value_rules: Vec<ValueRule>,
    pub state: BackendMappingRuntimeState,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "camelCase")]
pub struct MappingRuntimePoint {
    pub source_key: String,
    pub name: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendMappingRuntimeState {
    pub mapping_config_id: String,
    pub mapping_row_version: String,
    pub target_api_id: String,
    pub target_api_row_version: String,
    pub status: String,
    pub last_result: Option<String>,
    pub error_code: Option<String>,
    pub last_success_request_fingerprint: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendMappingRuntimeClaim {
    pub claimed: bool,
    pub error_code: Option<String>,
    pub state: BackendMappingRuntimeState,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendFactSnapshot {
    pub items: Vec<BackendFactSnapshotItem>,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct BackendFactSnapshotItem {
    pub source_key: String,
    pub name: String,
    pub found: bool,
    pub fact_kind: Option<String>,
    pub data_type: Option<String>,
    pub value: Option<String>,
    pub contract_version: Option<String>,
    pub updated_at: Option<String>,
    pub row_version: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ApiFirstMappingRuntimeStartRequest {
    pub backend_base_url: String,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendMappingRuntimeCompleteRequest {
    pub runtime_id: String,
    pub expected_mapping_row_version: String,
    pub expected_target_api_row_version: String,
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub delivery_fingerprint: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error_code: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MappingConfiguration {
    pub id: String,
    pub mapping_key: String,
    pub name: String,
    pub source_key: Option<String>,
    pub target_api_id: String,
    pub target_api_key: String,
    pub bindings: BTreeMap<String, MappingBinding>,
    pub interval_ms: u64,
    pub enabled: bool,
    pub row_version: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MappingBinding {
    pub kind: String,
    pub value: Option<Value>,
    pub source_key: Option<String>,
    pub fact_name: Option<String>,
    pub value_rule_key: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TargetApi {
    pub id: String,
    pub api_key: String,
    pub name: String,
    pub http_method: String,
    pub path: String,
    pub body_template: Value,
    pub parameter_schema: Vec<TargetParameter>,
    pub enabled: bool,
    pub row_version: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TargetParameter {
    pub parameter_key: String,
    pub location: String,
    pub name: String,
    pub json_path: Option<String>,
    pub data_type: String,
    pub required: bool,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SnapshotFact {
    pub source_key: String,
    pub name: String,
    pub data_type: String,
    pub value: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ValueRule {
    pub value_rule_key: String,
    pub data_type: String,
    pub values: Vec<Value>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MappingManualRunResult {
    pub run_id: String,
    pub mapping_config_id: String,
    pub mapping_row_version: String,
    pub target_api_id: String,
    pub target_api_row_version: String,
    pub snapshot_id: String,
    pub status: String,
    pub error_code: Option<String>,
    pub http_status_class: Option<String>,
    pub response_summary: Option<String>,
    pub resolved_parameter_keys: Vec<String>,
    pub unresolved_parameter_keys: Vec<String>,
    pub diagnostics: Vec<MappingRuntimeDiagnostic>,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct MappingRuntimeDiagnostic {
    pub parameter_key: String,
    pub error_code: String,
}

#[derive(Debug, Clone)]
pub struct ManualRunEvaluation {
    pub request: Option<OutboundRequest>,
    pub resolved_parameter_keys: Vec<String>,
    pub diagnostics: Vec<MappingRuntimeDiagnostic>,
}

#[derive(Debug, Clone)]
pub struct OutboundRequest {
    pub method: String,
    pub path: String,
    pub path_parameters: BTreeMap<String, String>,
    pub query: Vec<(String, String)>,
    pub headers: Vec<(String, String)>,
    pub body: Value,
}

pub fn mapping_runtime_snapshot_from_facts(
    configuration: &BackendMappingRuntimeConfiguration,
    snapshot: BackendFactSnapshot,
) -> Result<MappingRuntimeSnapshot, String> {
    let mut cache = BTreeMap::new();
    for item in snapshot.items {
        let identity = (item.source_key.clone(), item.name.clone());
        if (item.found
            && (item.data_type.as_deref().is_none_or(str::is_empty)
                || item.row_version.as_deref().is_none_or(str::is_empty)))
            || cache.insert(identity, item).is_some()
        {
            return Err("MAPPING_RUNTIME_BACKEND_RESPONSE_INVALID".to_string());
        }
    }
    let mut expected = BTreeSet::new();
    for point in &configuration.points {
        let key = (point.source_key.clone(), point.name.clone());
        if !expected.insert(key) {
            return Err("MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string());
        }
    }

    if cache.len() != expected.len() || cache.keys().ne(expected.iter()) {
        return Err("MAPPING_RUNTIME_BACKEND_RESPONSE_INVALID".to_string());
    }
    let mut facts = Vec::new();
    for key in expected {
        let item = cache
            .get(&key)
            .ok_or_else(|| "MAPPING_RUNTIME_BACKEND_RESPONSE_INVALID".to_string())?;
        if !item.found {
            continue;
        }
        let data_type = item
            .data_type
            .clone()
            .ok_or_else(|| "MAPPING_RUNTIME_BACKEND_RESPONSE_INVALID".to_string())?;
        facts.push(SnapshotFact {
            source_key: item.source_key.clone(),
            name: item.name.clone(),
            data_type,
            value: item.value.clone(),
        });
    }
    Ok(MappingRuntimeSnapshot {
        snapshot_id: "continuous-runtime".to_string(),
        mapping: configuration.mapping.clone(),
        target_api: configuration.target_api.clone(),
        facts,
        value_rules: configuration.value_rules.clone(),
    })
}

pub fn delivery_fingerprint(
    request: &OutboundRequest,
    mapping_row_version: &str,
    target_api_row_version: &str,
) -> String {
    let mut query = request.query.clone();
    let mut headers = request.headers.clone();
    query.sort_unstable();
    headers.sort_unstable();
    let value = serde_json::json!({
        "mappingRowVersion": mapping_row_version,
        "targetApiRowVersion": target_api_row_version,
        "method": &request.method,
        "path": &request.path,
        "pathParameters": &request.path_parameters,
        "query": query,
        "headers": headers,
        "body": &request.body,
    });
    let bytes = serde_json::to_vec(&value).unwrap_or_default();
    let hash = bytes.iter().fold(0xcbf2_9ce4_8422_2325_u64, |hash, byte| {
        (hash ^ u64::from(*byte)).wrapping_mul(0x0000_0100_0000_01b3)
    });
    format!("{hash:016x}")
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct BackendManualRunCompleteRequest {
    pub status: String,
    pub error_code: Option<String>,
    pub http_status_class: Option<String>,
    pub response_summary: String,
    pub resolved_parameter_keys: Vec<String>,
    pub unresolved_parameter_keys: Vec<String>,
}

impl MappingManualRunResult {
    pub fn from_audit(run: &BackendManualRun, diagnostics: Vec<MappingRuntimeDiagnostic>) -> Self {
        Self {
            run_id: run.run_id.clone(),
            mapping_config_id: run.mapping_config_id.clone(),
            mapping_row_version: run.mapping_row_version.clone(),
            target_api_id: run.target_api_id.clone(),
            target_api_row_version: run.target_api_row_version.clone(),
            snapshot_id: run.snapshot_id.clone(),
            status: run.status.clone(),
            error_code: run.error_code.clone(),
            http_status_class: run.http_status_class.clone(),
            response_summary: run.response_summary.clone(),
            resolved_parameter_keys: run.resolved_parameter_keys.clone(),
            unresolved_parameter_keys: run.unresolved_parameter_keys.clone(),
            diagnostics,
        }
    }
}

pub fn evaluate_snapshot(snapshot: &MappingRuntimeSnapshot) -> Result<ManualRunEvaluation, String> {
    if !snapshot.mapping.enabled || !snapshot.target_api.enabled {
        return Err("MAPPING_MANUAL_RUN_CONFIGURATION_UNAVAILABLE".to_string());
    }
    if snapshot.mapping.target_api_id != snapshot.target_api.id
        || snapshot.mapping.row_version.is_none()
        || snapshot.target_api.row_version.is_none()
        || !snapshot.target_api.path.starts_with('/')
        || snapshot.target_api.path.starts_with("//")
        || !snapshot.target_api.body_template.is_object()
    {
        return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
    }

    let facts = unique_facts(&snapshot.facts)?;
    let rules = unique_rules(&snapshot.value_rules)?;
    let mut body = snapshot.target_api.body_template.clone();
    let mut resolved_parameter_keys = Vec::new();
    let mut diagnostics = Vec::new();
    let mut query = Vec::new();
    let mut headers = Vec::new();
    let mut path_parameters = BTreeMap::new();
    let mut required_unresolved = false;
    let mut seen_parameter_keys = BTreeMap::new();

    for parameter in &snapshot.target_api.parameter_schema {
        if seen_parameter_keys
            .insert(parameter.parameter_key.clone(), true)
            .is_some()
            || !matches!(
                parameter.location.as_str(),
                "body" | "query" | "path" | "header"
            )
            || parameter.name.trim().is_empty()
            || (parameter.location == "path" && !parameter.required)
        {
            return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
        }

        let binding = snapshot.mapping.bindings.get(&parameter.parameter_key);
        let value = match binding {
            Some(binding) => resolve_binding(binding, parameter, &facts, &rules),
            None => Err("tss_mapping_manual_run_binding_missing".to_string()),
        };
        match value {
            Ok(value) => {
                let wire_value = scalar_text(&value)
                    .ok_or_else(|| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?;
                let applied = match parameter.location.as_str() {
                    "body" => set_body_value(
                        &mut body,
                        parameter.json_path.as_deref().unwrap_or(&parameter.name),
                        value,
                    ),
                    "query" => {
                        query.push((parameter.name.clone(), wire_value));
                        true
                    }
                    "header" => {
                        headers.push((parameter.name.clone(), wire_value));
                        true
                    }
                    "path" => {
                        path_parameters.insert(parameter.name.clone(), wire_value);
                        true
                    }
                    _ => false,
                };
                if !applied {
                    return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
                }
                resolved_parameter_keys.push(parameter.parameter_key.clone());
            }
            Err(error_code) => {
                diagnostics.push(MappingRuntimeDiagnostic {
                    parameter_key: parameter.parameter_key.clone(),
                    error_code,
                });
                if parameter.required {
                    required_unresolved = true;
                } else if parameter.location == "body"
                    && !remove_body_value(
                        &mut body,
                        parameter.json_path.as_deref().unwrap_or(&parameter.name),
                    )
                {
                    return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
                }
            }
        }
    }

    if required_unresolved {
        return Ok(ManualRunEvaluation {
            request: None,
            resolved_parameter_keys,
            diagnostics,
        });
    }
    Ok(ManualRunEvaluation {
        request: Some(OutboundRequest {
            method: snapshot.target_api.http_method.clone(),
            path: snapshot.target_api.path.clone(),
            path_parameters,
            query,
            headers,
            body,
        }),
        resolved_parameter_keys,
        diagnostics,
    })
}

fn unique_facts(
    facts: &[SnapshotFact],
) -> Result<BTreeMap<(String, String), &SnapshotFact>, String> {
    let mut result = BTreeMap::new();
    for fact in facts {
        let key = (fact.source_key.clone(), fact.name.clone());
        if result.insert(key, fact).is_some() {
            return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
        }
    }
    Ok(result)
}

fn unique_rules(rules: &[ValueRule]) -> Result<BTreeMap<String, &ValueRule>, String> {
    let mut result = BTreeMap::new();
    for rule in rules {
        if result.insert(rule.value_rule_key.clone(), rule).is_some() {
            return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
        }
    }
    Ok(result)
}

fn resolve_binding(
    binding: &MappingBinding,
    parameter: &TargetParameter,
    facts: &BTreeMap<(String, String), &SnapshotFact>,
    rules: &BTreeMap<String, &ValueRule>,
) -> Result<Value, String> {
    let value = match binding.kind.as_str() {
        "constant" => binding
            .value
            .clone()
            .ok_or_else(|| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?,
        "fact" => {
            if binding.value.is_some() {
                return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
            }
            let source_key = binding
                .source_key
                .as_deref()
                .filter(|value| !value.trim().is_empty())
                .ok_or_else(|| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?;
            let fact_name = binding
                .fact_name
                .as_deref()
                .filter(|value| !value.trim().is_empty())
                .ok_or_else(|| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?;
            let fact = facts
                .get(&(source_key.to_string(), fact_name.to_string()))
                .ok_or_else(|| "tss_mapping_manual_run_fact_missing".to_string())?;
            let raw_value = fact
                .value
                .as_deref()
                .ok_or_else(|| "tss_mapping_manual_run_fact_null".to_string())?;
            if !types_are_compatible(&fact.data_type, &parameter.data_type) {
                return Err("tss_mapping_manual_run_fact_type_incompatible".to_string());
            }
            parse_fact_value(&fact.data_type, raw_value)
                .ok_or_else(|| "tss_mapping_manual_run_fact_value_invalid".to_string())?
        }
        _ => return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string()),
    };

    if let Some(value_rule_key) = &binding.value_rule_key {
        let value_rule = rules
            .get(value_rule_key)
            .ok_or_else(|| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?;
        if value_rule.data_type != parameter.data_type
            || !value_matches_rule(&value, &value_rule.values)
        {
            return Err("tss_mapping_manual_run_value_rule_rejected".to_string());
        }
    }
    Ok(value)
}

fn types_are_compatible(fact_type: &str, target_type: &str) -> bool {
    fact_type == target_type || (fact_type == "integer" && target_type == "number")
}

fn parse_fact_value(data_type: &str, value: &str) -> Option<Value> {
    match data_type {
        "string" => Some(Value::String(value.to_string())),
        "integer" => value.parse::<i64>().ok().map(Value::from),
        "number" => value
            .parse::<f64>()
            .ok()
            .filter(|number| number.is_finite())
            .and_then(serde_json::Number::from_f64)
            .map(Value::Number),
        "boolean" => match value {
            "true" => Some(Value::Bool(true)),
            "false" => Some(Value::Bool(false)),
            _ => None,
        },
        "datetime" => DateTime::parse_from_rfc3339(value)
            .ok()
            .map(|_| Value::String(value.to_string())),
        _ => None,
    }
}

fn value_matches_rule(value: &Value, allowed_values: &[Value]) -> bool {
    allowed_values.iter().any(|allowed| match (value, allowed) {
        (Value::Number(actual), Value::Number(allowed)) => actual.as_f64() == allowed.as_f64(),
        _ => value == allowed,
    })
}

fn scalar_text(value: &Value) -> Option<String> {
    match value {
        Value::String(value) => Some(value.clone()),
        Value::Number(value) => Some(value.to_string()),
        Value::Bool(value) => Some(value.to_string()),
        _ => None,
    }
}

fn set_body_value(body: &mut Value, path: &str, value: Value) -> bool {
    let parts = path.split('.').collect::<Vec<_>>();
    if parts.is_empty() || parts.iter().any(|part| part.is_empty()) {
        return false;
    }
    let mut current = body;
    for part in &parts[..parts.len() - 1] {
        let Some(object) = current.as_object_mut() else {
            return false;
        };
        let Some(next) = object.get_mut(*part) else {
            return false;
        };
        current = next;
    }
    let Some(object) = current.as_object_mut() else {
        return false;
    };
    object
        .insert(parts[parts.len() - 1].to_string(), value)
        .is_some()
}

fn remove_body_value(body: &mut Value, path: &str) -> bool {
    let parts = path.split('.').collect::<Vec<_>>();
    if parts.is_empty() || parts.iter().any(|part| part.is_empty()) {
        return false;
    }
    let mut current = body;
    for part in &parts[..parts.len() - 1] {
        let Some(object) = current.as_object_mut() else {
            return false;
        };
        let Some(next) = object.get_mut(*part) else {
            return false;
        };
        current = next;
    }
    current
        .as_object_mut()
        .and_then(|object| object.remove(parts[parts.len() - 1]))
        .is_some()
}
