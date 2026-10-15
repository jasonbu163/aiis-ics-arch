//! File Path: /control-agent/src-tauri/src/services/plc_diagnostics.rs
//! Description: PLC read-only diagnostics service
//! Main Features:
//!   - Probes configured PLC endpoint TCP reachability
//!   - Performs disabled-by-default read-only S7 sample diagnostics
//!   - Reuses the shared PLC endpoint resolver before S7 infrastructure adapters

use std::net::{TcpStream, ToSocketAddrs};
use std::time::{Duration, Instant};

use crate::config::{parse_u64_or_default, AgentConfig};
use crate::domain::plc::{
    PlcEndpointProbeSnapshot, PlcPointContractSnapshot, PlcSampleReadSnapshot, ResolvedPlcEndpoint,
    RuntimePointCandidate,
};
use crate::infrastructure::minimal_s7_adapter::MinimalS7SampleReader;
use crate::infrastructure::plc_client::{
    normalize_plc_driver, PlcSampleReader, MINIMAL_S7_DRIVER, RUST_SNAP7_DRIVER,
};
use crate::infrastructure::plc_points::{
    collect_sample_points, collect_sample_points_for_plc, load_runtime_contract,
    resolve_runtime_endpoints,
};
use crate::infrastructure::rust_snap7_adapter::RustSnap7SampleReader;

pub(crate) fn idle_plc_sample_read(config: &AgentConfig) -> PlcSampleReadSnapshot {
    let enabled = crate::services::plc_collection::plc_sample_read_allowed(config);

    PlcSampleReadSnapshot {
        enabled,
        autostart: config.bool_or_default("CONTROL_AGENT_PLC_SAMPLE_READ_AUTOSTART", false),
        plc_key: String::new(),
        driver: normalize_plc_driver(
            &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", MINIMAL_S7_DRIVER),
        ),
        attempted: false,
        succeeded: false,
        sample_count: 0,
        latency_ms: 0,
        values: Vec::new(),
        error_message: "PLC sample read is waiting for operator start".to_string(),
    }
}

fn resolve_diagnostic_endpoint(
    config: &AgentConfig,
    contract: &PlcPointContractSnapshot,
) -> Result<ResolvedPlcEndpoint, String> {
    if !contract.loaded {
        return Err(if contract.error_message.is_empty() {
            "PLC point contract is not loaded".to_string()
        } else {
            contract.error_message.clone()
        });
    }

    let runtime_contract = load_runtime_contract(config)?;
    let endpoints = resolve_runtime_endpoints(config, &runtime_contract)?;

    if endpoints.len() != 1 {
        return Err(
            "PLC endpoint diagnostics require exactly one PLC in plc_points.yaml. Use collection status for multi-PLC runtime checks."
                .to_string(),
        );
    }

    endpoints
        .into_values()
        .next()
        .ok_or_else(|| "PLC point contract does not define an endpoint".to_string())
}

fn resolve_diagnostic_endpoint_for_plc(
    config: &AgentConfig,
    contract: &PlcPointContractSnapshot,
    plc_key: &str,
) -> Result<ResolvedPlcEndpoint, String> {
    if !contract.loaded {
        return Err(if contract.error_message.is_empty() {
            "PLC point contract is not loaded".to_string()
        } else {
            contract.error_message.clone()
        });
    }

    let runtime_contract = load_runtime_contract(config)?;
    let endpoints = resolve_runtime_endpoints(config, &runtime_contract)?;

    endpoints
        .get(plc_key)
        .cloned()
        .ok_or_else(|| format!("Unknown PLC key '{plc_key}' in plc_points.yaml"))
}

fn endpoint_resolution_error(enabled: bool, error_message: String) -> PlcEndpointProbeSnapshot {
    PlcEndpointProbeSnapshot {
        host: String::new(),
        port: 0,
        rack: 0,
        slot: 0,
        enabled,
        reachable: false,
        latency_ms: 0,
        error_message,
    }
}

pub(crate) fn idle_plc_endpoint_probe(
    config: &AgentConfig,
    contract: &PlcPointContractSnapshot,
) -> PlcEndpointProbeSnapshot {
    let endpoint = match resolve_diagnostic_endpoint(config, contract) {
        Ok(endpoint) => endpoint,
        Err(error) => return endpoint_resolution_error(false, error),
    };

    PlcEndpointProbeSnapshot {
        host: endpoint.host,
        port: endpoint.port,
        rack: endpoint.rack,
        slot: endpoint.slot,
        enabled: false,
        reachable: false,
        latency_ms: 0,
        error_message: "PLC endpoint probe is waiting for operator start".to_string(),
    }
}

pub(crate) fn probe_plc_endpoint(
    config: &AgentConfig,
    contract: &PlcPointContractSnapshot,
) -> PlcEndpointProbeSnapshot {
    let enabled = config.bool_or_default("CONTROL_AGENT_PLC_ENDPOINT_PROBE_ENABLED", true);
    let endpoint = match resolve_diagnostic_endpoint(config, contract) {
        Ok(endpoint) => endpoint,
        Err(error) => return endpoint_resolution_error(enabled, error),
    };
    let host = endpoint.host;
    let port = endpoint.port;
    let rack = endpoint.rack;
    let slot = endpoint.slot;
    let timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_CONNECT_TIMEOUT_MS", "500"),
        500,
    );

    if !enabled {
        return PlcEndpointProbeSnapshot {
            host,
            port,
            rack,
            slot,
            enabled,
            reachable: false,
            latency_ms: 0,
            error_message: "PLC endpoint probe is disabled".to_string(),
        };
    }

    if host.trim().is_empty() || port == 0 {
        return PlcEndpointProbeSnapshot {
            host,
            port,
            rack,
            slot,
            enabled,
            reachable: false,
            latency_ms: 0,
            error_message: "PLC endpoint host or port is not configured".to_string(),
        };
    }

    let address = format!("{host}:{port}");
    let started_at = Instant::now();
    let resolved_address = match address.to_socket_addrs() {
        Ok(mut addresses) => addresses.next(),
        Err(error) => {
            return PlcEndpointProbeSnapshot {
                host,
                port,
                rack,
                slot,
                enabled,
                reachable: false,
                latency_ms: 0,
                error_message: format!("Failed to resolve PLC endpoint: {error}"),
            };
        }
    };

    let Some(socket_address) = resolved_address else {
        return PlcEndpointProbeSnapshot {
            host,
            port,
            rack,
            slot,
            enabled,
            reachable: false,
            latency_ms: 0,
            error_message: "PLC endpoint did not resolve to a socket address".to_string(),
        };
    };

    match TcpStream::connect_timeout(&socket_address, Duration::from_millis(timeout_ms)) {
        Ok(stream) => {
            drop(stream);
            PlcEndpointProbeSnapshot {
                host,
                port,
                rack,
                slot,
                enabled,
                reachable: true,
                latency_ms: started_at.elapsed().as_millis(),
                error_message: String::new(),
            }
        }
        Err(error) => PlcEndpointProbeSnapshot {
            host,
            port,
            rack,
            slot,
            enabled,
            reachable: false,
            latency_ms: started_at.elapsed().as_millis(),
            error_message: format!("PLC endpoint TCP probe failed: {error}"),
        },
    }
}

fn probe_plc_endpoint_for_plc(
    config: &AgentConfig,
    contract: &PlcPointContractSnapshot,
    plc_key: &str,
) -> PlcEndpointProbeSnapshot {
    let enabled = config.bool_or_default("CONTROL_AGENT_PLC_ENDPOINT_PROBE_ENABLED", true);
    let endpoint = match resolve_diagnostic_endpoint_for_plc(config, contract, plc_key) {
        Ok(endpoint) => endpoint,
        Err(error) => return endpoint_resolution_error(enabled, error),
    };

    PlcEndpointProbeSnapshot {
        host: endpoint.host,
        port: endpoint.port,
        rack: endpoint.rack,
        slot: endpoint.slot,
        enabled,
        reachable: true,
        latency_ms: 0,
        error_message: String::new(),
    }
}

#[cfg(test)]
pub(crate) fn read_plc_samples(
    config: &AgentConfig,
    probe: &PlcEndpointProbeSnapshot,
) -> PlcSampleReadSnapshot {
    let enabled = crate::services::plc_collection::plc_sample_read_allowed(config);

    read_plc_samples_with_gate(config, probe, enabled)
}

pub(crate) fn read_plc_samples_once_from_console() -> PlcSampleReadSnapshot {
    let config = AgentConfig::load();
    let contract = crate::infrastructure::plc_points::read_plc_point_contract(&config);
    let probe = probe_plc_endpoint(&config, &contract);
    let sample_enabled = crate::services::plc_collection::plc_sample_read_allowed(&config);
    let sample = read_plc_samples_with_gate(&config, &probe, sample_enabled);

    tracing::info!(
        event = "plc_sample_read_once",
        driver = %sample.driver,
        attempted = sample.attempted,
        succeeded = sample.succeeded,
        sample_count = sample.sample_count,
        latency_ms = sample.latency_ms,
        error = %sample.error_message,
    );

    sample
}

pub(crate) fn read_plc_samples_once_for_plc_from_console(plc_key: String) -> PlcSampleReadSnapshot {
    let config = AgentConfig::load();
    let contract = crate::infrastructure::plc_points::read_plc_point_contract(&config);
    let probe = probe_plc_endpoint_for_plc(&config, &contract, &plc_key);
    let sample_enabled = crate::services::plc_collection::plc_sample_read_allowed(&config);
    let sample = read_plc_samples_with_gate_for_plc(&config, &probe, sample_enabled, &plc_key);
    crate::services::plc_collection::record_plc_sample_read_result(
        &plc_key,
        sample.succeeded,
        sample.latency_ms,
        &sample.error_message,
    );

    tracing::info!(
        event = "plc_sample_read_once",
        plc_key = %plc_key,
        driver = %sample.driver,
        attempted = sample.attempted,
        succeeded = sample.succeeded,
        sample_count = sample.sample_count,
        latency_ms = sample.latency_ms,
        error = %sample.error_message,
    );

    sample
}

fn read_plc_samples_with_gate(
    config: &AgentConfig,
    probe: &PlcEndpointProbeSnapshot,
    enabled: bool,
) -> PlcSampleReadSnapshot {
    let sample_limit = sample_limit(config);
    let points = collect_sample_points(config, sample_limit);

    read_plc_samples_with_points(config, probe, enabled, "", points)
}

fn read_plc_samples_with_gate_for_plc(
    config: &AgentConfig,
    probe: &PlcEndpointProbeSnapshot,
    enabled: bool,
    plc_key: &str,
) -> PlcSampleReadSnapshot {
    let sample_limit = sample_limit(config);
    let points = match collect_sample_points_for_plc(config, plc_key, sample_limit) {
        Ok(points) => points,
        Err(error) => {
            return PlcSampleReadSnapshot {
                enabled,
                autostart: config.bool_or_default("CONTROL_AGENT_PLC_SAMPLE_READ_AUTOSTART", false),
                plc_key: plc_key.to_string(),
                driver: normalize_plc_driver(
                    &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", MINIMAL_S7_DRIVER),
                ),
                attempted: false,
                succeeded: false,
                sample_count: 0,
                latency_ms: 0,
                values: Vec::new(),
                error_message: error,
            };
        }
    };

    read_plc_samples_with_points(config, probe, enabled, plc_key, points)
}

fn sample_limit(config: &AgentConfig) -> usize {
    parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_SAMPLE_LIMIT", "8"),
        8,
    )
    .clamp(1, 32) as usize
}

fn read_plc_samples_with_points(
    config: &AgentConfig,
    probe: &PlcEndpointProbeSnapshot,
    enabled: bool,
    plc_key: &str,
    points: Vec<RuntimePointCandidate>,
) -> PlcSampleReadSnapshot {
    let driver = normalize_plc_driver(
        &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", MINIMAL_S7_DRIVER),
    );
    let autostart = config.bool_or_default("CONTROL_AGENT_PLC_SAMPLE_READ_AUTOSTART", false);

    if !enabled {
        return PlcSampleReadSnapshot {
            enabled,
            autostart,
            plc_key: plc_key.to_string(),
            driver,
            attempted: false,
            succeeded: false,
            sample_count: 0,
            latency_ms: 0,
            values: Vec::new(),
            error_message: "PLC sample read is disabled".to_string(),
        };
    }

    if probe.host.trim().is_empty() || probe.port == 0 {
        return PlcSampleReadSnapshot {
            enabled,
            autostart,
            plc_key: plc_key.to_string(),
            driver,
            attempted: false,
            succeeded: false,
            sample_count: 0,
            latency_ms: 0,
            values: Vec::new(),
            error_message: if probe.error_message.is_empty() {
                "PLC endpoint host or port is not configured".to_string()
            } else {
                probe.error_message.clone()
            },
        };
    }

    if points.is_empty() {
        return PlcSampleReadSnapshot {
            enabled,
            autostart,
            plc_key: plc_key.to_string(),
            driver,
            attempted: false,
            succeeded: false,
            sample_count: 0,
            latency_ms: 0,
            values: Vec::new(),
            error_message: "No supported readable PLC sample points were found".to_string(),
        };
    }

    let timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_CONNECT_TIMEOUT_MS", "500"),
        500,
    );
    let timeout = Duration::from_millis(timeout_ms);
    let started_at = Instant::now();

    let read_result = match driver.as_str() {
        MINIMAL_S7_DRIVER => MinimalS7SampleReader.read_samples(probe, &points, timeout),
        RUST_SNAP7_DRIVER => RustSnap7SampleReader.read_samples(probe, &points, timeout),
        _ => Err(format!(
            "Unsupported PLC driver '{driver}'. Supported drivers: {MINIMAL_S7_DRIVER}, {RUST_SNAP7_DRIVER}"
        )),
    };

    match read_result {
        Ok(values) => PlcSampleReadSnapshot {
            enabled,
            autostart,
            plc_key: plc_key.to_string(),
            driver,
            attempted: true,
            succeeded: true,
            sample_count: values.len() as u32,
            latency_ms: started_at.elapsed().as_millis(),
            values,
            error_message: String::new(),
        },
        Err(error) => PlcSampleReadSnapshot {
            enabled,
            autostart,
            plc_key: plc_key.to_string(),
            driver,
            attempted: true,
            succeeded: false,
            sample_count: 0,
            latency_ms: started_at.elapsed().as_millis(),
            values: Vec::new(),
            error_message: error,
        },
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;
    use std::fs;

    use super::*;
    use crate::config::resolve_runtime_path;
    use crate::config::AgentConfig;
    use crate::infrastructure::plc_points::{
        collect_sample_points_for_plc, read_plc_point_contract,
    };

    #[test]
    fn idle_sample_read_reflects_enabled_and_autostart_flags() {
        let mut values = HashMap::new();
        values.insert(
            "CONTROL_AGENT_PLC_SAMPLE_READ_ENABLED".to_string(),
            "true".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_READ_ALLOWED".to_string(),
            "true".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_SAMPLE_READ_AUTOSTART".to_string(),
            "true".to_string(),
        );

        let config = AgentConfig::from_values(values);
        let sample = idle_plc_sample_read(&config);

        assert!(sample.enabled);
        assert!(sample.autostart);
        assert!(!sample.attempted);
    }

    #[test]
    fn blocks_unknown_plc_sample_driver_at_read_gate() {
        let mut values = HashMap::new();
        values.insert(
            "CONTROL_AGENT_PLC_SAMPLE_READ_ENABLED".to_string(),
            "true".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_READ_ALLOWED".to_string(),
            "true".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_DRIVER".to_string(),
            "unknown".to_string(),
        );

        let config = AgentConfig::from_values(values);
        let probe = PlcEndpointProbeSnapshot {
            host: "127.0.0.1".to_string(),
            port: 1102,
            rack: 0,
            slot: 1,
            enabled: true,
            reachable: true,
            latency_ms: 0,
            error_message: String::new(),
        };
        let sample = read_plc_samples(&config, &probe);

        assert!(!sample.attempted);
        assert!(!sample.succeeded);
        assert_eq!(sample.driver, "unknown");
        assert_eq!(sample.error_message, "PLC sample read is disabled");
    }

    #[test]
    #[ignore = "requires tools/plc/s7-virtual-plc to be running on 127.0.0.1:1102"]
    fn reads_samples_from_local_virtual_plc() {
        assert_local_virtual_plc_samples(MINIMAL_S7_DRIVER);
    }

    #[test]
    #[cfg(feature = "rust-snap7-driver")]
    #[ignore = "requires tools/plc/s7-virtual-plc to be running on 127.0.0.1:1102"]
    fn reads_samples_from_local_virtual_plc_with_rust_snap7() {
        assert_local_virtual_plc_samples(RUST_SNAP7_DRIVER);
    }

    fn assert_local_virtual_plc_samples(driver: &str) {
        let contract_path = write_single_plc_test_contract();
        let mut values = HashMap::new();
        values.insert(
            "CONTROL_AGENT_PLC_CONFIG_PATH".to_string(),
            contract_path.display().to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_HOST".to_string(),
            "127.0.0.1".to_string(),
        );
        values.insert("CONTROL_AGENT_PLC_PORT".to_string(), "1102".to_string());
        values.insert("CONTROL_AGENT_PLC_RACK".to_string(), "0".to_string());
        values.insert("CONTROL_AGENT_PLC_SLOT".to_string(), "1".to_string());
        values.insert(
            "CONTROL_AGENT_PLC_CONNECT_TIMEOUT_MS".to_string(),
            "1000".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_SAMPLE_READ_ENABLED".to_string(),
            "true".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_READ_ALLOWED".to_string(),
            "true".to_string(),
        );
        values.insert(
            "CONTROL_AGENT_PLC_SAMPLE_LIMIT".to_string(),
            "3".to_string(),
        );
        values.insert("CONTROL_AGENT_PLC_DRIVER".to_string(), driver.to_string());

        let config = AgentConfig::from_values(values);
        let contract = read_plc_point_contract(&config);
        let probe = probe_plc_endpoint(&config, &contract);
        let sample = read_plc_samples(&config, &probe);

        assert!(probe.reachable, "probe failed: {}", probe.error_message);
        assert!(sample.succeeded, "sample failed: {}", sample.error_message);
        assert_eq!(sample.driver, driver);
        assert_eq!(sample.sample_count, 3);
        assert!(sample
            .values
            .iter()
            .any(|value| value.name == "example_value"));

        let _ = fs::remove_file(contract_path);
    }

    #[test]
    fn targeted_sample_read_resolves_each_plc_endpoint_and_point_set() {
        let contract_path = write_multi_plc_test_contract(12001, 12002);
        let config = AgentConfig::from_values(HashMap::from([(
            "CONTROL_AGENT_PLC_CONFIG_PATH".to_string(),
            contract_path.display().to_string(),
        )]));
        let contract = read_plc_point_contract(&config);

        for (plc_key, expected_port) in [("PLC_1", 12001), ("PLC_2", 12002)] {
            let endpoint = resolve_diagnostic_endpoint_for_plc(&config, &contract, plc_key)
                .expect("configured PLC endpoint should resolve");
            let points = collect_sample_points_for_plc(&config, plc_key, 3)
                .expect("configured PLC point set should resolve");

            assert_eq!(endpoint.host, "127.0.0.1");
            assert_eq!(endpoint.port, expected_port);
            assert_eq!(endpoint.rack, 0);
            assert_eq!(endpoint.slot, 1);
            assert_eq!(points.len(), 3);
        }

        let _ = fs::remove_file(contract_path);
    }

    #[test]
    #[cfg(feature = "rust-snap7-driver")]
    #[ignore = "requires virtual PLCs on 127.0.0.1:12001 and 127.0.0.1:12002"]
    fn reads_samples_from_two_local_virtual_plcs_with_rust_snap7() {
        let contract_path = write_multi_plc_test_contract(12001, 12002);
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_CONFIG_PATH".to_string(),
                contract_path.display().to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_CONNECT_TIMEOUT_MS".to_string(),
                "1000".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_SAMPLE_LIMIT".to_string(),
                "3".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_DRIVER".to_string(),
                RUST_SNAP7_DRIVER.to_string(),
            ),
        ]));
        let contract = read_plc_point_contract(&config);

        for plc_key in ["PLC_1", "PLC_2"] {
            let probe = probe_plc_endpoint_for_plc(&config, &contract, plc_key);
            let sample = read_plc_samples_with_gate_for_plc(&config, &probe, true, plc_key);

            assert!(
                probe.reachable,
                "{plc_key} probe failed: {}",
                probe.error_message
            );
            assert!(
                sample.succeeded,
                "{plc_key} sample failed: {}",
                sample.error_message
            );
            assert_eq!(sample.plc_key, plc_key);
            assert_eq!(sample.sample_count, 3);
        }

        let _ = fs::remove_file(contract_path);
    }

    fn write_single_plc_test_contract() -> std::path::PathBuf {
        let source_path = resolve_runtime_path("config/plc_points.yaml");
        let source = fs::read_to_string(source_path).expect("default PLC contract should exist");
        let mut source_contract: serde_yaml::Mapping =
            serde_yaml::from_str(&source).expect("default PLC contract should parse");
        let plc_key = serde_yaml::Value::String("PLC_1".to_string());
        let plc = source_contract
            .remove(&plc_key)
            .expect("default PLC contract should contain PLC_1");
        let mut single_contract = serde_yaml::Mapping::new();
        single_contract.insert(plc_key, plc);

        let path = std::env::temp_dir().join(format!(
            "ca-runtime-002-single-plc-{}.yaml",
            std::process::id()
        ));
        fs::write(
            &path,
            serde_yaml::to_string(&single_contract).expect("single PLC contract should serialize"),
        )
        .expect("single PLC test contract should be writable");
        path
    }

    fn write_multi_plc_test_contract(plc_1_port: u16, plc_2_port: u16) -> std::path::PathBuf {
        let source_path = resolve_runtime_path("config/plc_points.yaml");
        let source = fs::read_to_string(source_path).expect("default PLC contract should exist");
        let mut contract: serde_yaml::Mapping =
            serde_yaml::from_str(&source).expect("default PLC contract should parse");
        let plc_1_key = serde_yaml::Value::String("PLC_1".to_string());
        let plc_1 = contract
            .get(&plc_1_key)
            .cloned()
            .expect("default PLC contract should contain PLC_1");

        for (plc_key, port) in [("PLC_1", plc_1_port), ("PLC_2", plc_2_port)] {
            let key = serde_yaml::Value::String(plc_key.to_string());
            if !contract.contains_key(&key) {
                contract.insert(key.clone(), plc_1.clone());
            }
            let plc = contract
                .get_mut(&key)
                .and_then(serde_yaml::Value::as_mapping_mut)
                .expect("default PLC contract should contain both PLC keys");
            plc.insert(
                serde_yaml::Value::String("ip".to_string()),
                serde_yaml::Value::String("127.0.0.1".to_string()),
            );
            plc.insert(
                serde_yaml::Value::String("port".to_string()),
                serde_yaml::to_value(port).expect("PLC test port should serialize"),
            );
        }

        let path = std::env::temp_dir().join(format!(
            "ca-runtime-002-multi-plc-{}.yaml",
            std::process::id()
        ));
        fs::write(
            &path,
            serde_yaml::to_string(&contract).expect("multi PLC contract should serialize"),
        )
        .expect("multi PLC test contract should be writable");
        path
    }
}
