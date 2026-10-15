//! File Path: /control-agent/src-tauri/src/infrastructure/plc_snapshot_policy.rs
//! Description: PLC snapshot raw/latest decoded-payload policy file adapter
//! Main Features:
//!   - Loads the same-shape v2 plc_snapshot_policy.yaml contract
//!   - Validates policy points against the authoritative PLC point contract
//!   - Exposes raw/latest decoded-payload filter keys and policy status counts

use std::collections::{HashMap, HashSet};
use std::fs;

use serde::Deserialize;
use serde_yaml::Value as YamlValue;

use crate::config::{parse_u64_or_default, resolve_runtime_path, AgentConfig};
use crate::domain::plc_collection::PlcSnapshotPolicyStatusSnapshot;
use crate::infrastructure::plc_points::load_runtime_contract;

#[derive(Debug, Default, Deserialize)]
struct SnapshotPolicyPoint {
    name: String,
    raw_enabled: Option<bool>,
    raw_policy: Option<String>,
    latest_enabled: Option<bool>,
}

#[derive(Debug, Default, Deserialize)]
struct SnapshotPolicyGroup {
    db_number: u16,
    #[serde(default, alias = "name")]
    group_name: String,
    #[serde(default)]
    points: Vec<SnapshotPolicyPoint>,
}

#[derive(Debug, Default, Deserialize)]
struct SnapshotPolicyPlc {
    snapshot_policy_version: Option<u32>,
    #[serde(default)]
    groups: Vec<SnapshotPolicyGroup>,
}

struct ContractPointIndex {
    keys: HashSet<(String, u16, String, String)>,
    point_count: u32,
}

#[derive(Default)]
struct SnapshotPolicyValidationSummary {
    version: String,
    full_decoded_point_count: u32,
    policy_point_count: u32,
    selected_point_count: u32,
    raw_selected_point_count: u32,
    latest_selected_point_count: u32,
    every_sample_count: u32,
    on_change_count: u32,
    missing_policy_point_count: u32,
    unknown_point_count: u32,
    invalid_policy_count: u32,
}

#[derive(Clone, Debug, Default)]
pub(crate) struct PlcSnapshotPayloadPolicyFilter {
    raw_grouped_points: HashMap<(String, u16, String), HashSet<String>>,
    latest_grouped_points: HashMap<(String, u16, String), HashSet<String>>,
}

impl PlcSnapshotPayloadPolicyFilter {
    pub(crate) fn allows_raw_point(
        &self,
        plc_key: &str,
        db_number: u16,
        group_name: &str,
        point_name: &str,
    ) -> bool {
        self.raw_grouped_points
            .get(&(plc_key.to_string(), db_number, group_name.to_string()))
            .map(|points| points.contains(point_name))
            .unwrap_or(false)
    }

    pub(crate) fn allows_latest_point(
        &self,
        plc_key: &str,
        db_number: u16,
        group_name: &str,
        point_name: &str,
    ) -> bool {
        self.latest_grouped_points
            .get(&(plc_key.to_string(), db_number, group_name.to_string()))
            .map(|points| points.contains(point_name))
            .unwrap_or(false)
    }

    #[cfg(test)]
    pub(crate) fn from_group_points_for_test(
        plc_key: &str,
        db_number: u16,
        group_name: &str,
        raw_point_names: &[&str],
        latest_point_names: &[&str],
    ) -> Self {
        let group_key = (plc_key.to_string(), db_number, group_name.to_string());
        let mut raw_grouped_points = HashMap::new();
        raw_grouped_points.insert(
            group_key.clone(),
            raw_point_names
                .iter()
                .map(|name| (*name).to_string())
                .collect(),
        );
        let mut latest_grouped_points = HashMap::new();
        latest_grouped_points.insert(
            group_key,
            latest_point_names
                .iter()
                .map(|name| (*name).to_string())
                .collect(),
        );

        Self {
            raw_grouped_points,
            latest_grouped_points,
        }
    }
}

fn empty_policy_status(
    config: &AgentConfig,
    configured_path: String,
    resolved_path: String,
    exists: bool,
    error_message: String,
) -> PlcSnapshotPolicyStatusSnapshot {
    PlcSnapshotPolicyStatusSnapshot {
        configured_path,
        resolved_path,
        exists,
        loaded: false,
        version: String::new(),
        latest_mode: "policy_scoped".to_string(),
        raw_hot_retention_days: raw_retention_days_from_env(config),
        full_decoded_point_count: 0,
        policy_point_count: 0,
        selected_point_count: 0,
        raw_selected_point_count: 0,
        latest_selected_point_count: 0,
        every_sample_count: 0,
        on_change_count: 0,
        missing_policy_point_count: 0,
        unknown_point_count: 0,
        invalid_policy_count: 0,
        error_message,
    }
}

fn allowed_raw_policy(policy: &str) -> bool {
    matches!(policy, "every_sample" | "on_change" | "hourly")
}

fn raw_retention_days_from_env(config: &AgentConfig) -> u32 {
    parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_RAW_HOT_RETENTION_DAYS", "7"),
        7,
    )
    .clamp(1, u32::MAX as u64) as u32
}

fn point_index_from_contract(config: &AgentConfig) -> Result<ContractPointIndex, String> {
    let contract = load_runtime_contract(config)?;
    let mut keys = HashSet::new();

    for (plc_key, plc) in contract {
        for group in plc.groups {
            for point in group.points {
                keys.insert((
                    plc_key.clone(),
                    group.db_number,
                    group.name.clone(),
                    point.name,
                ));
            }
        }
    }

    let point_count = keys.len().min(u32::MAX as usize) as u32;
    Ok(ContractPointIndex { keys, point_count })
}

fn parse_snapshot_policy_file(content: &str) -> Result<HashMap<String, SnapshotPolicyPlc>, String> {
    let root = serde_yaml::from_str::<YamlValue>(content)
        .map_err(|error| format!("Failed to parse PLC snapshot policy YAML: {error}"))?;
    let Some(mapping) = root.as_mapping() else {
        return Err("PLC snapshot policy must be a YAML mapping keyed by PLC id".to_string());
    };

    let legacy_root_keys = ["version", "defaults", "groups", "points"];
    for key in legacy_root_keys {
        if mapping.contains_key(&YamlValue::String(key.to_string())) {
            return Err(
                "Unsupported PLC snapshot policy contract: regenerate the same-shape v2 YAML with top-level PLC keys, raw_enabled, raw_policy and latest_enabled"
                    .to_string(),
            );
        }
    }

    serde_yaml::from_value::<HashMap<String, SnapshotPolicyPlc>>(root)
        .map_err(|error| format!("Failed to parse same-shape PLC snapshot policy YAML: {error}"))
}

fn add_policy_point(
    grouped_points: &mut HashMap<(String, u16, String), HashSet<String>>,
    plc_key: &str,
    db_number: u16,
    group_name: &str,
    point_name: &str,
) {
    grouped_points
        .entry((plc_key.to_string(), db_number, group_name.to_string()))
        .or_default()
        .insert(point_name.to_string());
}

fn build_policy_filter(
    policy_file: HashMap<String, SnapshotPolicyPlc>,
    contract_index: &ContractPointIndex,
) -> (
    PlcSnapshotPayloadPolicyFilter,
    SnapshotPolicyValidationSummary,
    Vec<String>,
) {
    let mut filter = PlcSnapshotPayloadPolicyFilter::default();
    let mut summary = SnapshotPolicyValidationSummary {
        version: "2".to_string(),
        full_decoded_point_count: contract_index.point_count,
        ..Default::default()
    };
    let mut errors = Vec::new();
    let mut policy_keys = HashSet::new();

    for (plc_key, plc_policy) in policy_file {
        if plc_policy.snapshot_policy_version != Some(2) {
            summary.invalid_policy_count = summary.invalid_policy_count.saturating_add(1);
            errors.push(format!(
                "{plc_key} has invalid snapshot_policy_version {:?}; expected 2",
                plc_policy.snapshot_policy_version
            ));
        }

        for group in plc_policy.groups {
            let group_name = group.group_name;
            for point in group.points {
                summary.policy_point_count = summary.policy_point_count.saturating_add(1);

                let policy_key = (
                    plc_key.clone(),
                    group.db_number,
                    group_name.clone(),
                    point.name.clone(),
                );
                if !policy_keys.insert(policy_key.clone()) {
                    summary.invalid_policy_count = summary.invalid_policy_count.saturating_add(1);
                    errors.push(format!(
                        "{}:DB{}:{}:{} is duplicated in plc_snapshot_policy.yaml",
                        plc_key, group.db_number, group_name, point.name
                    ));
                    continue;
                }

                if !contract_index.keys.contains(&policy_key) {
                    summary.unknown_point_count = summary.unknown_point_count.saturating_add(1);
                    errors.push(format!(
                        "{}:DB{}:{}:{} is not defined in plc_points.yaml",
                        plc_key, group.db_number, group_name, point.name
                    ));
                    continue;
                }

                let Some(raw_enabled) = point.raw_enabled else {
                    summary.invalid_policy_count = summary.invalid_policy_count.saturating_add(1);
                    errors.push(format!(
                        "{}:DB{}:{}:{} is missing raw_enabled",
                        plc_key, group.db_number, group_name, point.name
                    ));
                    continue;
                };
                let Some(raw_policy) = point.raw_policy else {
                    summary.invalid_policy_count = summary.invalid_policy_count.saturating_add(1);
                    errors.push(format!(
                        "{}:DB{}:{}:{} is missing raw_policy",
                        plc_key, group.db_number, group_name, point.name
                    ));
                    continue;
                };
                let Some(latest_enabled) = point.latest_enabled else {
                    summary.invalid_policy_count = summary.invalid_policy_count.saturating_add(1);
                    errors.push(format!(
                        "{}:DB{}:{}:{} is missing latest_enabled",
                        plc_key, group.db_number, group_name, point.name
                    ));
                    continue;
                };

                if !allowed_raw_policy(&raw_policy) {
                    summary.invalid_policy_count = summary.invalid_policy_count.saturating_add(1);
                    errors.push(format!(
                        "{}:DB{}:{}:{} has invalid raw_policy {}",
                        plc_key, group.db_number, group_name, point.name, raw_policy
                    ));
                    continue;
                }

                if raw_enabled {
                    summary.raw_selected_point_count =
                        summary.raw_selected_point_count.saturating_add(1);
                    match raw_policy.as_str() {
                        "every_sample" => {
                            summary.every_sample_count =
                                summary.every_sample_count.saturating_add(1)
                        }
                        "on_change" => {
                            summary.on_change_count = summary.on_change_count.saturating_add(1)
                        }
                        _ => {}
                    }
                    add_policy_point(
                        &mut filter.raw_grouped_points,
                        &plc_key,
                        group.db_number,
                        &group_name,
                        &point.name,
                    );
                }

                if latest_enabled {
                    summary.latest_selected_point_count =
                        summary.latest_selected_point_count.saturating_add(1);
                    add_policy_point(
                        &mut filter.latest_grouped_points,
                        &plc_key,
                        group.db_number,
                        &group_name,
                        &point.name,
                    );
                }
            }
        }
    }

    for contract_key in &contract_index.keys {
        if !policy_keys.contains(contract_key) {
            summary.missing_policy_point_count =
                summary.missing_policy_point_count.saturating_add(1);
        }
    }
    if summary.missing_policy_point_count > 0 {
        errors.push(format!(
            "plc_snapshot_policy.yaml is missing {} point(s) from plc_points.yaml",
            summary.missing_policy_point_count
        ));
    }

    summary.selected_point_count = summary.raw_selected_point_count;

    (filter, summary, errors)
}

pub(crate) fn read_plc_snapshot_payload_policy_filter(
    config: &AgentConfig,
) -> Result<Option<PlcSnapshotPayloadPolicyFilter>, String> {
    let configured_path = config.value_or_default(
        "CONTROL_AGENT_PLC_SNAPSHOT_POLICY_PATH",
        "config/plc_snapshot_policy.yaml",
    );
    let resolved_path = resolve_runtime_path(&configured_path);

    if !resolved_path.exists() {
        return Ok(None);
    }

    let content = fs::read_to_string(&resolved_path)
        .map_err(|error| format!("Failed to read PLC snapshot policy file: {error}"))?;
    let policy_file = parse_snapshot_policy_file(&content)?;
    let contract_point_index = point_index_from_contract(config)?;
    let (filter, _summary, errors) = build_policy_filter(policy_file, &contract_point_index);

    if errors.is_empty() {
        Ok(Some(filter))
    } else {
        Err(format!(
            "Invalid PLC snapshot policy for raw/latest filtering: {}",
            errors.join("; ")
        ))
    }
}

pub(crate) fn read_plc_snapshot_policy_status(
    config: &AgentConfig,
) -> PlcSnapshotPolicyStatusSnapshot {
    let configured_path = config.value_or_default(
        "CONTROL_AGENT_PLC_SNAPSHOT_POLICY_PATH",
        "config/plc_snapshot_policy.yaml",
    );
    let resolved_path = resolve_runtime_path(&configured_path);
    let resolved_path_text = resolved_path.display().to_string();

    if !resolved_path.exists() {
        return empty_policy_status(
            config,
            configured_path,
            resolved_path_text,
            false,
            "PLC snapshot policy file does not exist".to_string(),
        );
    }

    let content = match fs::read_to_string(&resolved_path) {
        Ok(content) => content,
        Err(error) => {
            return empty_policy_status(
                config,
                configured_path,
                resolved_path_text,
                true,
                format!("Failed to read PLC snapshot policy file: {error}"),
            );
        }
    };
    let policy_file = match parse_snapshot_policy_file(&content) {
        Ok(policy_file) => policy_file,
        Err(error) => {
            return empty_policy_status(config, configured_path, resolved_path_text, true, error);
        }
    };
    let contract_point_index = match point_index_from_contract(config) {
        Ok(index) => index,
        Err(error) => {
            return empty_policy_status(
                config,
                configured_path,
                resolved_path_text,
                true,
                format!("Failed to validate PLC snapshot policy against point contract: {error}"),
            );
        }
    };

    let (_filter, summary, errors) = build_policy_filter(policy_file, &contract_point_index);
    let error_message = if errors.is_empty() {
        String::new()
    } else {
        format!(
            "Policy validation failed: missing_policy_point_count={}, unknown_point_count={}, invalid_policy_count={}",
            summary.missing_policy_point_count,
            summary.unknown_point_count,
            summary.invalid_policy_count
        )
    };

    PlcSnapshotPolicyStatusSnapshot {
        configured_path,
        resolved_path: resolved_path_text,
        exists: true,
        loaded: errors.is_empty(),
        version: summary.version,
        latest_mode: "policy_scoped".to_string(),
        raw_hot_retention_days: raw_retention_days_from_env(config),
        full_decoded_point_count: summary.full_decoded_point_count,
        policy_point_count: summary.policy_point_count,
        selected_point_count: summary.selected_point_count,
        raw_selected_point_count: summary.raw_selected_point_count,
        latest_selected_point_count: summary.latest_selected_point_count,
        every_sample_count: summary.every_sample_count,
        on_change_count: summary.on_change_count,
        missing_policy_point_count: summary.missing_policy_point_count,
        unknown_point_count: summary.unknown_point_count,
        invalid_policy_count: summary.invalid_policy_count,
        error_message,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn loads_default_snapshot_policy_file() {
        let config = AgentConfig::empty_for_test();
        let status = read_plc_snapshot_policy_status(&config);

        assert!(status.exists);
        assert!(status.loaded);
        assert_eq!(status.version, "2");
        assert_eq!(status.latest_mode, "policy_scoped");
        assert!(status.full_decoded_point_count >= 1);
        assert!(status.raw_selected_point_count >= 1);
        assert!(status.latest_selected_point_count >= status.raw_selected_point_count);
    }

    #[test]
    fn reports_missing_policy_without_failing_collection() {
        let mut values = HashMap::new();
        values.insert(
            "CONTROL_AGENT_PLC_SNAPSHOT_POLICY_PATH".to_string(),
            "config/missing_snapshot_policy.yaml".to_string(),
        );
        let config = AgentConfig::from_values(values);
        let status = read_plc_snapshot_policy_status(&config);

        assert!(!status.exists);
        assert!(!status.loaded);
    }

    #[test]
    fn rejects_legacy_policy_shape() {
        let content = r#"
version: 1
points:
  - name: DB28_read_1_Int
    history_enabled: true
    policy: every_sample
"#;

        let error = parse_snapshot_policy_file(content).unwrap_err();

        assert!(error.contains("Unsupported PLC snapshot policy contract"));
    }
}
