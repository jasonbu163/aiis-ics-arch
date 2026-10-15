//! File Path: /control-agent/src-tauri/src/infrastructure/plc_points.rs
//! Description: PLC point contract file adapter
//! Main Features:
//!   - Reads and summarizes plc_points.yaml
//!   - Extracts supported read-only sample point candidates
//!   - Resolves safe per-PLC communication endpoints from the runtime contract
//!   - Keeps YAML parsing details outside diagnostics services

use std::collections::HashMap;
use std::fs;

use crate::config::{parse_u16_or_default, resolve_runtime_path, trim_env_value, AgentConfig};
use crate::domain::plc::{
    PlcPointContractSnapshot, PlcRuntimeConfig, PointTypeCount, ResolvedPlcEndpoint,
    RuntimePointCandidate,
};

fn leading_spaces(line: &str) -> usize {
    line.chars()
        .take_while(|character| *character == ' ')
        .count()
}

fn yaml_value(line: &str) -> String {
    line.split_once(':')
        .map(|(_, value)| trim_env_value(value))
        .unwrap_or_default()
}

fn is_supported_point_type(data_type: &str) -> bool {
    matches!(
        data_type,
        "Bool"
            | "Int"
            | "DInt"
            | "UInt"
            | "Word"
            | "USInt"
            | "UDInt"
            | "Real"
            | "String"
            | "Date_And_Time"
    )
}

#[derive(Default)]
struct PointScanState {
    has_name: bool,
    has_type: bool,
    has_offset: bool,
    readable: bool,
    writable: bool,
    data_type: String,
}

fn finish_point(
    point: &mut Option<PointScanState>,
    type_counts: &mut HashMap<String, u32>,
    readable_count: &mut u32,
    writable_count: &mut u32,
    missing_required_count: &mut u32,
    unsupported_type_count: &mut u32,
) {
    let Some(current) = point.take() else {
        return;
    };

    if current.readable {
        *readable_count += 1;
    }

    if current.writable {
        *writable_count += 1;
    }

    if !current.has_name || !current.has_type || !current.has_offset {
        *missing_required_count += 1;
    }

    if current.has_type {
        *type_counts.entry(current.data_type.clone()).or_insert(0) += 1;

        if !is_supported_point_type(&current.data_type) {
            *unsupported_type_count += 1;
        }
    }
}

fn supported_sample_type(data_type: &str) -> bool {
    matches!(
        data_type,
        "Bool" | "Int" | "DInt" | "UInt" | "Word" | "USInt" | "UDInt" | "Real" | "String"
    )
}

fn finish_runtime_point(
    point: &mut Option<RuntimePointCandidate>,
    points: &mut Vec<RuntimePointCandidate>,
    limit: usize,
) {
    if points.len() >= limit {
        *point = None;
        return;
    }

    let Some(current) = point.take() else {
        return;
    };

    if current.name.is_empty()
        || current.db_number == 0
        || current.offset.is_none()
        || !supported_sample_type(&current.data_type)
        || current.readable == Some(false)
    {
        return;
    }

    points.push(current);
}

pub(crate) fn collect_sample_points(
    config: &AgentConfig,
    limit: usize,
) -> Vec<RuntimePointCandidate> {
    let configured_path =
        config.value_or_default("CONTROL_AGENT_PLC_CONFIG_PATH", "config/plc_points.yaml");
    let resolved_path = resolve_runtime_path(&configured_path);
    let Ok(content) = fs::read_to_string(resolved_path) else {
        return Vec::new();
    };

    let mut points = Vec::new();
    let mut current_db_number = 0;
    let mut current_point: Option<RuntimePointCandidate> = None;

    for raw_line in content.lines() {
        if points.len() >= limit {
            break;
        }

        let line = raw_line.trim_end();
        let trimmed = line.trim();

        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let indent = leading_spaces(line);

        if indent == 4 && trimmed.starts_with("- name:") {
            finish_runtime_point(&mut current_point, &mut points, limit);
            current_db_number = 0;
            continue;
        }

        if indent == 6 && trimmed.starts_with("db_number:") {
            current_db_number = parse_u16_or_default(&yaml_value(trimmed), 0);
            continue;
        }

        if indent == 8 && trimmed.starts_with("- name:") {
            finish_runtime_point(&mut current_point, &mut points, limit);
            current_point = Some(RuntimePointCandidate {
                name: yaml_value(trimmed),
                db_number: current_db_number,
                ..Default::default()
            });
            continue;
        }

        if indent == 10 {
            if let Some(point) = current_point.as_mut() {
                if trimmed.starts_with("type:") {
                    point.data_type = yaml_value(trimmed);
                } else if trimmed.starts_with("offset:") {
                    point.offset = yaml_value(trimmed).parse::<u32>().ok();
                } else if trimmed.starts_with("bit:") {
                    point.bit = yaml_value(trimmed).parse::<u8>().unwrap_or(0);
                } else if trimmed.starts_with("length:") {
                    point.length = yaml_value(trimmed).parse::<u16>().ok();
                } else if trimmed.starts_with("readable:") {
                    point.readable = Some(matches!(
                        yaml_value(trimmed).as_str(),
                        "true" | "True" | "1"
                    ));
                }
            }
        }
    }

    finish_runtime_point(&mut current_point, &mut points, limit);

    points
}

fn collect_sample_points_from_plc(
    plc: &PlcRuntimeConfig,
    limit: usize,
) -> Vec<RuntimePointCandidate> {
    let mut points = Vec::new();

    for group in &plc.groups {
        for point in &group.points {
            if points.len() >= limit {
                return points;
            }

            let candidate = point.as_runtime_candidate(group.db_number);
            if candidate.name.is_empty()
                || candidate.db_number == 0
                || candidate.offset.is_none()
                || !supported_sample_type(&candidate.data_type)
                || candidate.readable == Some(false)
            {
                continue;
            }

            points.push(candidate);
        }
    }

    points
}

pub(crate) fn collect_sample_points_for_plc(
    config: &AgentConfig,
    plc_key: &str,
    limit: usize,
) -> Result<Vec<RuntimePointCandidate>, String> {
    let contract = load_runtime_contract(config)?;
    let plc = contract
        .get(plc_key)
        .ok_or_else(|| format!("Unknown PLC key '{plc_key}' in plc_points.yaml"))?;

    Ok(collect_sample_points_from_plc(plc, limit))
}

pub(crate) fn load_runtime_contract(
    config: &AgentConfig,
) -> Result<HashMap<String, PlcRuntimeConfig>, String> {
    let configured_path =
        config.value_or_default("CONTROL_AGENT_PLC_CONFIG_PATH", "config/plc_points.yaml");
    let resolved_path = resolve_runtime_path(&configured_path);
    let content = fs::read_to_string(&resolved_path).map_err(|error| {
        format!(
            "Failed to read PLC point contract {}: {error}",
            resolved_path.display()
        )
    })?;

    serde_yaml::from_str::<HashMap<String, PlcRuntimeConfig>>(&content)
        .map_err(|error| format!("Failed to parse PLC point contract YAML: {error}"))
}

fn parse_endpoint_u16(key: &str, value: String) -> Result<u16, String> {
    value
        .parse::<u16>()
        .map_err(|_| format!("{key} must be an unsigned 16-bit integer"))
}

fn global_endpoint_override(config: &AgentConfig) -> Result<Option<ResolvedPlcEndpoint>, String> {
    let host = config.non_empty_value("CONTROL_AGENT_PLC_HOST");
    let port = config.non_empty_value("CONTROL_AGENT_PLC_PORT");
    let rack = config.non_empty_value("CONTROL_AGENT_PLC_RACK");
    let slot = config.non_empty_value("CONTROL_AGENT_PLC_SLOT");
    let configured_count = [&host, &port, &rack, &slot]
        .into_iter()
        .filter(|value| value.is_some())
        .count();

    if configured_count == 0 {
        return Ok(None);
    }

    if configured_count != 4 {
        return Err(
            "Global PLC endpoint override must configure all four values together: CONTROL_AGENT_PLC_HOST, CONTROL_AGENT_PLC_PORT, CONTROL_AGENT_PLC_RACK and CONTROL_AGENT_PLC_SLOT."
                .to_string(),
        );
    }

    let port = parse_endpoint_u16(
        "CONTROL_AGENT_PLC_PORT",
        port.ok_or_else(|| "CONTROL_AGENT_PLC_PORT is required".to_string())?,
    )?;
    let rack = parse_endpoint_u16(
        "CONTROL_AGENT_PLC_RACK",
        rack.ok_or_else(|| "CONTROL_AGENT_PLC_RACK is required".to_string())?,
    )?;
    let slot = parse_endpoint_u16(
        "CONTROL_AGENT_PLC_SLOT",
        slot.ok_or_else(|| "CONTROL_AGENT_PLC_SLOT is required".to_string())?,
    )?;

    if port == 0 {
        return Err("CONTROL_AGENT_PLC_PORT must be greater than zero".to_string());
    }

    Ok(Some(ResolvedPlcEndpoint {
        host: host.ok_or_else(|| "CONTROL_AGENT_PLC_HOST is required".to_string())?,
        port,
        rack,
        slot,
    }))
}

pub(crate) fn resolve_runtime_endpoints(
    config: &AgentConfig,
    contract: &HashMap<String, PlcRuntimeConfig>,
) -> Result<HashMap<String, ResolvedPlcEndpoint>, String> {
    let Some(override_endpoint) = global_endpoint_override(config)? else {
        return Ok(contract
            .iter()
            .map(|(plc_key, plc)| {
                (
                    plc_key.clone(),
                    ResolvedPlcEndpoint {
                        host: plc.ip.clone(),
                        port: plc.port,
                        rack: plc.rack,
                        slot: plc.slot,
                    },
                )
            })
            .collect());
    };

    if contract.len() != 1 {
        return Err(
            "Global PLC endpoint override requires exactly one PLC in plc_points.yaml. Leave all four endpoint variables blank to use each PLC's YAML endpoint."
                .to_string(),
        );
    }

    Ok(contract
        .keys()
        .map(|plc_key| (plc_key.clone(), override_endpoint.clone()))
        .collect())
}

pub(crate) fn read_plc_point_contract(config: &AgentConfig) -> PlcPointContractSnapshot {
    let configured_path =
        config.value_or_default("CONTROL_AGENT_PLC_CONFIG_PATH", "config/plc_points.yaml");
    let resolved_path = resolve_runtime_path(&configured_path);
    let resolved_path_text = resolved_path.display().to_string();

    if !resolved_path.exists() {
        return PlcPointContractSnapshot {
            configured_path,
            resolved_path: resolved_path_text,
            exists: false,
            loaded: false,
            plc_count: 0,
            group_count: 0,
            point_count: 0,
            readable_count: 0,
            writable_count: 0,
            missing_required_count: 0,
            unsupported_type_count: 0,
            endpoint_ip: String::new(),
            endpoint_port: 0,
            endpoint_rack: 0,
            endpoint_slot: 0,
            type_counts: Vec::new(),
            error_message: "PLC point contract file does not exist".to_string(),
        };
    }

    let Ok(content) = fs::read_to_string(&resolved_path) else {
        return PlcPointContractSnapshot {
            configured_path,
            resolved_path: resolved_path_text,
            exists: true,
            loaded: false,
            plc_count: 0,
            group_count: 0,
            point_count: 0,
            readable_count: 0,
            writable_count: 0,
            missing_required_count: 0,
            unsupported_type_count: 0,
            endpoint_ip: String::new(),
            endpoint_port: 0,
            endpoint_rack: 0,
            endpoint_slot: 0,
            type_counts: Vec::new(),
            error_message: "Failed to read PLC point contract file".to_string(),
        };
    };

    let mut plc_count = 0;
    let mut group_count = 0;
    let mut point_count = 0;
    let mut readable_count = 0;
    let mut writable_count = 0;
    let mut missing_required_count = 0;
    let mut unsupported_type_count = 0;
    let mut endpoint_ip = String::new();
    let mut endpoint_port = 0;
    let mut endpoint_rack = 0;
    let mut endpoint_slot = 0;
    let mut type_counts = HashMap::new();
    let mut current_point: Option<PointScanState> = None;

    for raw_line in content.lines() {
        let line = raw_line.trim_end();
        let trimmed = line.trim();

        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let indent = leading_spaces(line);

        if indent == 0 && trimmed.ends_with(':') {
            finish_point(
                &mut current_point,
                &mut type_counts,
                &mut readable_count,
                &mut writable_count,
                &mut missing_required_count,
                &mut unsupported_type_count,
            );
            plc_count += 1;
            continue;
        }

        if indent == 2 {
            if trimmed.starts_with("ip:") && endpoint_ip.is_empty() {
                endpoint_ip = yaml_value(trimmed);
            } else if trimmed.starts_with("port:") && endpoint_port == 0 {
                endpoint_port = parse_u16_or_default(&yaml_value(trimmed), 0);
            } else if trimmed.starts_with("rack:") && endpoint_rack == 0 {
                endpoint_rack = parse_u16_or_default(&yaml_value(trimmed), 0);
            } else if trimmed.starts_with("slot:") && endpoint_slot == 0 {
                endpoint_slot = parse_u16_or_default(&yaml_value(trimmed), 0);
            } else if trimmed.starts_with("- name:") {
                finish_point(
                    &mut current_point,
                    &mut type_counts,
                    &mut readable_count,
                    &mut writable_count,
                    &mut missing_required_count,
                    &mut unsupported_type_count,
                );
                group_count += 1;
            }
            continue;
        }

        if indent == 4 && trimmed.starts_with("- name:") {
            finish_point(
                &mut current_point,
                &mut type_counts,
                &mut readable_count,
                &mut writable_count,
                &mut missing_required_count,
                &mut unsupported_type_count,
            );
            group_count += 1;
            continue;
        }

        if indent == 8 && trimmed.starts_with("- name:") {
            finish_point(
                &mut current_point,
                &mut type_counts,
                &mut readable_count,
                &mut writable_count,
                &mut missing_required_count,
                &mut unsupported_type_count,
            );
            point_count += 1;
            current_point = Some(PointScanState {
                has_name: !yaml_value(trimmed).is_empty(),
                ..Default::default()
            });
            continue;
        }

        if indent == 10 {
            if let Some(point) = current_point.as_mut() {
                if trimmed.starts_with("type:") {
                    point.data_type = yaml_value(trimmed);
                    point.has_type = !point.data_type.is_empty();
                } else if trimmed.starts_with("offset:") {
                    point.has_offset = !yaml_value(trimmed).is_empty();
                } else if trimmed.starts_with("readable:") {
                    point.readable = matches!(yaml_value(trimmed).as_str(), "true" | "True" | "1");
                } else if trimmed.starts_with("writable:") {
                    point.writable = matches!(yaml_value(trimmed).as_str(), "true" | "True" | "1");
                }
            }
        }
    }

    finish_point(
        &mut current_point,
        &mut type_counts,
        &mut readable_count,
        &mut writable_count,
        &mut missing_required_count,
        &mut unsupported_type_count,
    );

    let mut type_counts: Vec<PointTypeCount> = type_counts
        .into_iter()
        .map(|(data_type, count)| PointTypeCount { data_type, count })
        .collect();
    type_counts.sort_by(|left, right| left.data_type.cmp(&right.data_type));

    PlcPointContractSnapshot {
        configured_path,
        resolved_path: resolved_path_text,
        exists: true,
        loaded: true,
        plc_count,
        group_count,
        point_count,
        readable_count,
        writable_count,
        missing_required_count,
        unsupported_type_count,
        endpoint_ip,
        endpoint_port,
        endpoint_rack,
        endpoint_slot,
        type_counts,
        error_message: String::new(),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::*;
    use crate::domain::plc::PlcRuntimeConfig;

    fn runtime_plc(ip: &str, port: u16, rack: u16, slot: u16) -> PlcRuntimeConfig {
        PlcRuntimeConfig {
            ip: ip.to_string(),
            port,
            rack,
            slot,
            groups: Vec::new(),
        }
    }

    fn endpoint_values(host: &str, port: &str, rack: &str, slot: &str) -> HashMap<String, String> {
        HashMap::from([
            ("CONTROL_AGENT_PLC_HOST".to_string(), host.to_string()),
            ("CONTROL_AGENT_PLC_PORT".to_string(), port.to_string()),
            ("CONTROL_AGENT_PLC_RACK".to_string(), rack.to_string()),
            ("CONTROL_AGENT_PLC_SLOT".to_string(), slot.to_string()),
        ])
    }

    #[test]
    fn reads_default_plc_point_contract() {
        let config = AgentConfig::empty_for_test();
        let contract = read_plc_point_contract(&config);

        assert!(contract.loaded);
        assert!(contract.plc_count >= 1);
        assert!(contract.group_count >= 1);
        assert!(contract.point_count >= 1);
    }

    #[test]
    fn collects_readable_sample_points_from_default_contract() {
        let config = AgentConfig::empty_for_test();
        let points = collect_sample_points(&config, 3);

        assert_eq!(points.len(), 3);
        assert!(points
            .iter()
            .all(|point| point.db_number > 0 && point.offset.is_some()));
        assert!(points
            .iter()
            .all(|point| supported_sample_type(&point.data_type)));
    }

    #[test]
    fn word_is_supported_by_contract_summary_and_sample_collection() {
        assert!(is_supported_point_type("Word"));
        assert!(supported_sample_type("Word"));
    }

    #[test]
    fn endpoint_resolver_uses_each_yaml_endpoint_when_global_values_are_empty() {
        let config = AgentConfig::from_values(endpoint_values("", "", "", ""));
        let contract = HashMap::from([
            ("PLC_1".to_string(), runtime_plc("127.0.0.1", 102, 0, 1)),
            ("PLC_2".to_string(), runtime_plc("127.0.0.2", 1102, 0, 2)),
        ]);

        let endpoints = resolve_runtime_endpoints(&config, &contract).unwrap();

        assert_eq!(endpoints["PLC_1"].host, "127.0.0.1");
        assert_eq!(endpoints["PLC_1"].port, 102);
        assert_eq!(endpoints["PLC_1"].rack, 0);
        assert_eq!(endpoints["PLC_1"].slot, 1);
        assert_eq!(endpoints["PLC_2"].host, "127.0.0.2");
        assert_eq!(endpoints["PLC_2"].port, 1102);
        assert_eq!(endpoints["PLC_2"].rack, 0);
        assert_eq!(endpoints["PLC_2"].slot, 2);
    }

    #[test]
    fn endpoint_resolver_allows_complete_global_override_for_single_plc() {
        let config = AgentConfig::from_values(endpoint_values("127.0.0.1", "1102", "0", "1"));
        let contract = HashMap::from([("PLC_1".to_string(), runtime_plc("127.0.0.1", 102, 0, 2))]);

        let endpoints = resolve_runtime_endpoints(&config, &contract).unwrap();

        assert_eq!(endpoints["PLC_1"].host, "127.0.0.1");
        assert_eq!(endpoints["PLC_1"].port, 1102);
        assert_eq!(endpoints["PLC_1"].rack, 0);
        assert_eq!(endpoints["PLC_1"].slot, 1);
    }

    #[test]
    fn endpoint_resolver_rejects_partial_global_override() {
        for values in [
            endpoint_values("127.0.0.1", "", "", ""),
            endpoint_values("", "1102", "", ""),
            endpoint_values("", "", "0", ""),
            endpoint_values("", "", "", "1"),
        ] {
            let config = AgentConfig::from_values(values);
            let contract =
                HashMap::from([("PLC_1".to_string(), runtime_plc("127.0.0.1", 102, 0, 1))]);

            let error = resolve_runtime_endpoints(&config, &contract).unwrap_err();

            assert!(error.contains("all four"));
        }
    }

    #[test]
    fn endpoint_resolver_rejects_global_override_for_multi_plc_contract() {
        let config = AgentConfig::from_values(endpoint_values("127.0.0.1", "1102", "0", "1"));
        let contract = HashMap::from([
            ("PLC_1".to_string(), runtime_plc("127.0.0.1", 102, 0, 1)),
            ("PLC_2".to_string(), runtime_plc("127.0.0.2", 102, 0, 1)),
        ]);

        let error = resolve_runtime_endpoints(&config, &contract).unwrap_err();

        assert!(error.contains("exactly one PLC"));
    }
}
