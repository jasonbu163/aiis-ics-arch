//! SMA 映射预览与周期执行共享配置和 SQLite 快照组包。
use super::*;
use crate::{
    contracts::local_configuration::{ConfigurationSnapshot, ConnectionProfile},
    domain::mapping_runtime as runtime,
};
use reqwest::header::{HeaderName, HeaderValue};
use std::collections::{BTreeMap, BTreeSet};

pub fn evaluate_mapping(
    config: &ConfigurationSnapshot,
    states: &[SourceState],
    id: &str,
) -> Result<(String, PostPreview), String> {
    let mapping = config
        .document
        .mappings
        .iter()
        .find(|m| m["id"] == id)
        .ok_or("SMA_CONFIGURATION_NOT_FOUND")?;
    let max_age = mapping["maxAgeMs"]
        .as_u64()
        .ok_or("SMA_HTTP_MAPPING_SETUP_REQUIRED")?;
    let target = config
        .document
        .target_apis
        .iter()
        .find(|t| t["apiKey"] == mapping["targetApiKey"])
        .ok_or("SMA_CONFIGURATION_REFERENCE_MISSING")?;
    let mapping: runtime::MappingConfiguration = deserialize(mapping)?;
    let source_keys: BTreeSet<_> = mapping
        .bindings
        .values()
        .filter_map(|b| b.source_key.as_deref())
        .collect();
    let sources = source_keys
        .into_iter()
        .map(|key| {
            let snapshot = states
                .iter()
                .find(|state| state.source_key == key)
                .and_then(|state| state.snapshot.as_ref());
            SourceReference {
                source_key: key.to_owned(),
                version: snapshot.map(|s| s.version),
                collected_at: snapshot.map(|s| s.collected_at.clone()),
                points: snapshot
                    .map(|s| {
                        s.points
                            .iter()
                            .filter(|p| {
                                mapping.bindings.values().any(|b| {
                                    b.source_key.as_deref() == Some(key)
                                        && b.fact_name.as_deref() == Some(p.point_key.as_str())
                                })
                            })
                            .cloned()
                            .collect()
                    })
                    .unwrap_or_default(),
            }
        })
        .collect::<Vec<_>>();
    let enabled_sources: BTreeSet<_> = config
        .document
        .http_sources
        .iter()
        .filter(|s| s["enabled"] == true)
        .filter_map(|s| s["sourceKey"].as_str())
        .collect();
    let rules = config
        .document
        .mapping_value_rules
        .iter()
        .filter(|r| r["enabled"] == true)
        .map(deserialize)
        .collect::<Result<_, _>>()?;
    let now = chrono::Utc::now();
    let choose_value = |binding: &runtime::MappingBinding,
                        _parameter: &runtime::TargetParameter| {
        let key = binding
            .source_key
            .as_deref()
            .ok_or("SMA_HTTP_SOURCE_MISSING")?;
        if !enabled_sources.contains(key) {
            return Err("SMA_HTTP_SOURCE_DISABLED".into());
        }
        let source = sources
            .iter()
            .find(|s| s.source_key == key)
            .ok_or("SMA_HTTP_SOURCE_MISSING")?;
        let time = source
            .collected_at
            .as_deref()
            .and_then(|s| chrono::DateTime::parse_from_rfc3339(s).ok())
            .ok_or("SMA_HTTP_SNAPSHOT_MISSING")?;
        let age = now.timestamp_millis() - time.timestamp_millis();
        if age < 0 || age as u64 > max_age {
            return Err("SMA_HTTP_SNAPSHOT_STALE".into());
        }
        let point = source
            .points
            .iter()
            .find(|point| binding.fact_name.as_deref() == Some(point.point_key.as_str()))
            .ok_or("SMA_HTTP_POINT_MISSING")?;
        if let Some(error) = &point.error_code {
            return Err(error.clone());
        }
        point
            .value
            .clone()
            .ok_or_else(|| "SMA_HTTP_POINT_MISSING".to_owned())
    };
    let group = target_group(config, target)?;
    let mut preview = evaluate(config, mapping, target, rules, choose_value)?;
    preview.sources = sources;
    Ok((group, preview))
}

pub fn evaluate_target(
    config: &ConfigurationSnapshot,
    id: &str,
    values: BTreeMap<String, Value>,
) -> Result<(String, PostPreview), String> {
    let target = config
        .document
        .target_apis
        .iter()
        .find(|t| t["id"] == id)
        .ok_or("SMA_CONFIGURATION_NOT_FOUND")?;
    let typed: runtime::TargetApi = deserialize(target)?;
    for key in values.keys() {
        if !typed
            .parameter_schema
            .iter()
            .any(|p| &p.parameter_key == key)
        {
            return Err(format!("SMA_HTTP_TARGET_PARAMETER_UNKNOWN:{key}"));
        }
    }
    let mapping = runtime::MappingConfiguration {
        id: id.into(),
        mapping_key: id.into(),
        name: typed.name,
        source_key: None,
        target_api_id: id.into(),
        target_api_key: typed.api_key,
        bindings: values
            .into_iter()
            .map(|(key, value)| {
                (
                    key,
                    runtime::MappingBinding {
                        kind: "constant".into(),
                        value: Some(value),
                        source_key: None,
                        fact_name: None,
                        value_rule_key: None,
                    },
                )
            })
            .collect(),
        interval_ms: 0,
        enabled: true,
        row_version: None,
    };
    let group = target_group(config, target)?;
    Ok((
        group,
        evaluate(config, mapping, target, vec![], |_, _| {
            Err("SMA_HTTP_SOURCE_MISSING".into())
        })?,
    ))
}

fn deserialize<T: serde::de::DeserializeOwned>(value: &Value) -> Result<T, String> {
    serde_json::from_value(value.clone()).map_err(|_| "SMA_HTTP_CONFIGURATION_INVALID".into())
}

fn evaluate(
    config: &ConfigurationSnapshot,
    mut mapping: runtime::MappingConfiguration,
    raw_target: &Value,
    value_rules: Vec<runtime::ValueRule>,
    choose_value: impl Fn(&runtime::MappingBinding, &runtime::TargetParameter) -> Result<Value, String>,
) -> Result<PostPreview, String> {
    let mut target_api: runtime::TargetApi = deserialize(raw_target)?;
    if target_api.http_method != "POST" {
        return Err("SMA_HTTP_TARGET_POST_REQUIRED".into());
    }
    validate_wire_parameters(&target_api)?;
    // 本地 revision 只在内存中适配纯组包器，不进入旧 backend 租约。
    mapping.row_version = Some(config.revision.to_string());
    target_api.row_version = mapping.row_version.clone();
    let evaluated = runtime::evaluate_bindings(
        &runtime::MappingRuntimeSnapshot {
            snapshot_id: config.revision.to_string(),
            mapping,
            target_api,
            facts: vec![],
            value_rules,
        },
        choose_value,
    )?;
    let request = evaluated
        .request
        .map(|request| prepare(&config.document.connection, raw_target, request))
        .transpose()?;
    Ok(PostPreview {
        token: None,
        revision: config.revision,
        request,
        sources: vec![],
        diagnostics: evaluated.diagnostics,
    })
}

pub fn target_group(config: &ConfigurationSnapshot, target: &Value) -> Result<String, String> {
    let raw = target_url(&config.document.connection, target)?;
    let mut url = http_url(&raw)?;
    url.set_query(None);
    Ok(url.to_string())
}

fn target_url(connection: &ConnectionProfile, target: &Value) -> Result<String, String> {
    if let Some(url) = target["url"].as_str() {
        return Ok(url.to_owned());
    }
    if connection.host.is_empty() || connection.port == 0 {
        return Err("SMA_HTTP_CONNECTION_REQUIRED".into());
    }
    let path = target["path"]
        .as_str()
        .ok_or("SMA_HTTP_TARGET_URL_INVALID")?;
    let host = if connection.host.contains(':') && !connection.host.starts_with('[') {
        format!("[{}]", connection.host)
    } else {
        connection.host.clone()
    };
    Ok(format!(
        "{}://{}:{}{path}",
        connection.scheme, host, connection.port
    ))
}

fn prepare(
    connection: &ConnectionProfile,
    target: &Value,
    request: runtime::OutboundRequest,
) -> Result<PreparedPost, String> {
    let raw = target_url(connection, target)?;
    let path = raw_url_path(&raw);
    let query = raw
        .split_once('?')
        .map(|(_, query)| format!("?{query}"))
        .unwrap_or_default();
    let mut resolved = path.to_owned();
    for (name, value) in request.path_parameters {
        // RFC 3986 path component. Reject the two dot-segment forms normalized by URL parsers.
        if matches!(value.as_str(), "." | "..") {
            return Err("SMA_HTTP_TARGET_PATH_INVALID".into());
        }
        let encoded = value
            .bytes()
            .map(|b| match b {
                b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                    (b as char).to_string()
                }
                _ => format!("%{b:02X}"),
            })
            .collect::<String>();
        resolved = resolved.replace(&format!("{{{name}}}"), &encoded);
    }
    let origin = http_url(&raw)?.origin().ascii_serialization();
    let mut url = http_url(&format!("{origin}{resolved}{query}"))?;
    // Explicitly mapped query parameters replace values embedded in the URL template.
    let target_schema: Vec<runtime::TargetParameter> = deserialize(&target["parameterSchema"])?;
    let mapped_query: BTreeSet<_> = target_schema
        .iter()
        .filter(|p| p.location == "query")
        .map(|p| p.name.as_str())
        .collect();
    let static_query = url
        .query_pairs()
        .into_owned()
        .filter(|(name, _)| !mapped_query.contains(name.as_str()))
        .collect::<Vec<_>>();
    url.set_query(None);
    if !static_query.is_empty() || !request.query.is_empty() {
        url.query_pairs_mut()
            .extend_pairs(static_query)
            .extend_pairs(request.query);
    }
    for (name, value) in &request.headers {
        if HeaderName::from_bytes(name.as_bytes()).is_err()
            || HeaderValue::from_str(value).is_err()
            || matches!(
                name.to_ascii_lowercase().as_str(),
                "host" | "content-length" | "transfer-encoding" | "connection"
            )
        {
            return Err(format!("SMA_HTTP_HEADER_INVALID:{name}"));
        }
    }
    Ok(PreparedPost {
        method: "POST",
        url: url.into(),
        headers: request.headers,
        body: request.body,
        timeout_ms: target["timeoutMs"].as_u64().unwrap_or(5_000),
        receipt: deserialize(&target["receipt"])?,
    })
}
