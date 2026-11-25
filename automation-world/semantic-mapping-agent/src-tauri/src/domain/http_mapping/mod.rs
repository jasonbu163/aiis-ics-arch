//! SMA HTTP 映射纯域：来源路径、类型、目标配置校验与同一组包逻辑。
use crate::{
    contracts::http_mapping::*,
    domain::local_configuration::{typed, valid_key, value_type},
};
use reqwest::Url;
use serde_json::Value;
use std::collections::BTreeSet;

mod evaluate;
pub use evaluate::{evaluate_mapping, evaluate_target, target_group};

pub fn validate_sources(values: &[Value]) -> Result<Vec<HttpSource>, String> {
    values
        .iter()
        .map(|raw| {
            let key = raw["sourceKey"].as_str().unwrap_or("?");
            let source: HttpSource = serde_json::from_value(raw.clone())
                .map_err(|_| format!("SMA_HTTP_SOURCE_INVALID:{key}"))?;
            if source.name.trim().is_empty()
                || http_url(&source.url).is_err()
                || !(1..=86_400_000).contains(&source.interval_ms)
                || !valid_timeout(source.timeout_ms)
                || source
                    .response_path
                    .as_deref()
                    .is_some_and(|p| !valid_pointer(p))
                || source
                    .response_condition
                    .as_ref()
                    .is_some_and(|c| !valid_condition(c))
                || source.points.len() > crate::contracts::local_configuration::MAX_ITEMS
                || source
                    .query
                    .keys()
                    .any(|k| k.trim().is_empty() || k.chars().any(char::is_control))
            {
                return Err(format!("SMA_HTTP_SOURCE_INVALID:{key}"));
            }
            let mut keys = BTreeSet::new();
            for point in &source.points {
                if !valid_key(&point.point_key)
                    || !keys.insert(&point.point_key)
                    || point.name.trim().is_empty()
                    || !typed(&point.data_type)
                    || !valid_pointer(&point.path)
                    || [
                        &point.quality_path,
                        &point.observed_at_path,
                        &point.sample_id_path,
                    ]
                    .into_iter()
                    .flatten()
                    .any(|path| !valid_pointer(path))
                    || point.accepted_quality.iter().any(|q| q.trim().is_empty())
                    || (!point.accepted_quality.is_empty() && point.quality_path.is_none())
                    || point.selector.as_ref().is_some_and(|selector| {
                        !valid_pointer(&selector.path)
                            || !valid_pointer(&selector.key)
                            || !is_scalar(&selector.value)
                    })
                {
                    return Err(format!("SMA_HTTP_POINT_INVALID:{key}:{}", point.point_key));
                }
            }
            Ok(source)
        })
        .collect()
}

pub fn validate_limits(limits: &RuntimeLimits) -> Result<(), String> {
    if [
        limits.get_concurrency,
        limits.post_concurrency,
        limits.per_target_concurrency,
    ]
    .into_iter()
    .any(|n| !(1..=128).contains(&n))
        || limits.per_target_concurrency > limits.post_concurrency
        || [limits.get_queue, limits.post_queue]
            .into_iter()
            .any(|n| !(1..=10_000).contains(&n))
    {
        return Err("SMA_HTTP_LIMITS_INVALID".into());
    }
    Ok(())
}

pub fn validate_target_options(
    raw: &Value,
    target: &crate::domain::mapping_runtime::TargetApi,
) -> Result<(), String> {
    if !raw["url"].is_null() {
        let raw_url = raw["url"].as_str().ok_or("SMA_HTTP_TARGET_URL_INVALID")?;
        let url = http_url(raw_url).map_err(|_| "SMA_HTTP_TARGET_URL_INVALID")?;
        let names: BTreeSet<_> = target
            .parameter_schema
            .iter()
            .filter(|p| p.location == "path")
            .map(|p| p.name.as_str())
            .collect();
        if target.http_method != "POST"
            || placeholder_names(raw_url_path(raw_url))? != names
            || url.query().is_some_and(|query| query.contains(['{', '}']))
        {
            return Err(format!("SMA_HTTP_TARGET_URL_INVALID:{}", target.api_key));
        }
    }
    if !raw["timeoutMs"].is_null() && !raw["timeoutMs"].as_u64().is_some_and(valid_timeout) {
        return Err(format!("SMA_HTTP_TIMEOUT_INVALID:{}", target.api_key));
    }
    if !raw["receipt"].is_null() {
        let condition: ResponseCondition = serde_json::from_value(raw["receipt"].clone())
            .map_err(|_| "SMA_HTTP_RECEIPT_INVALID")?;
        if !valid_condition(&condition) {
            return Err(format!("SMA_HTTP_RECEIPT_INVALID:{}", target.api_key));
        }
    }
    if !raw["url"].is_null() || !raw["timeoutMs"].is_null() || !raw["receipt"].is_null() {
        validate_wire_parameters(target)?;
    }
    Ok(())
}

pub fn validate_wire_parameters(
    target: &crate::domain::mapping_runtime::TargetApi,
) -> Result<(), String> {
    let mut body = BTreeSet::new();
    let mut headers = BTreeSet::new();
    for p in &target.parameter_schema {
        let invalid = match p.location.as_str() {
            "body" => !body.insert(p.json_path.as_deref().unwrap_or_default()),
            "header" => {
                let name = p.name.to_ascii_lowercase();
                reqwest::header::HeaderName::from_bytes(name.as_bytes()).is_err()
                    || matches!(
                        name.as_str(),
                        "host" | "content-length" | "transfer-encoding" | "connection"
                    )
                    || !headers.insert(name)
            }
            _ => false,
        };
        if invalid {
            return Err(format!(
                "SMA_CONFIGURATION_PARAMETER_INVALID:targetApis:{}:{}",
                target.api_key, p.parameter_key
            ));
        }
    }
    Ok(())
}

fn raw_url_path(raw: &str) -> &str {
    let authority_and_route = raw.split_once("://").map_or(raw, |(_, end)| end);
    let route = authority_and_route.split('?').next().unwrap_or_default();
    route.find('/').map_or("/", |index| &route[index..])
}

fn placeholder_names(mut path: &str) -> Result<BTreeSet<&str>, String> {
    let mut names = BTreeSet::new();
    while let Some(start) = path.find('{') {
        if path[..start].contains('}') {
            return Err("SMA_HTTP_TARGET_URL_INVALID".into());
        }
        let (name, remainder) = path[start + 1..]
            .split_once('}')
            .ok_or("SMA_HTTP_TARGET_URL_INVALID")?;
        if name.is_empty() || name.contains(['{', '/', '?', '#']) {
            return Err("SMA_HTTP_TARGET_URL_INVALID".into());
        }
        names.insert(name);
        path = remainder;
    }
    if path.contains('}') {
        return Err("SMA_HTTP_TARGET_URL_INVALID".into());
    }
    Ok(names)
}

fn valid_timeout(ms: u64) -> bool {
    (1..=60_000).contains(&ms)
}

pub fn http_url(raw: &str) -> Result<Url, String> {
    let url = Url::parse(raw).map_err(|_| "SMA_HTTP_URL_INVALID")?;
    if !matches!(url.scheme(), "http" | "https")
        || url.host_str().is_none()
        || !url.username().is_empty()
        || url.password().is_some()
        || url.fragment().is_some()
        || raw.chars().any(|c| c == '\\' || c.is_control())
    {
        return Err("SMA_HTTP_URL_INVALID".into());
    }
    Ok(url)
}

fn valid_pointer(path: &str) -> bool {
    (path.is_empty() || path.starts_with('/'))
        && path.split('~').skip(1).all(|s| s.starts_with(['0', '1']))
}

fn is_scalar(value: &Value) -> bool {
    value.is_string() || value.is_number() || value.is_boolean()
}

fn valid_condition(condition: &ResponseCondition) -> bool {
    valid_pointer(&condition.path) && is_scalar(&condition.equals)
}

pub fn condition_result(condition: &ResponseCondition, value: &Value) -> Option<bool> {
    let actual = value.pointer(&condition.path)?;
    if !matches!(
        (actual, &condition.equals),
        (Value::String(_), Value::String(_))
            | (Value::Bool(_), Value::Bool(_))
            | (Value::Number(_), Value::Number(_))
    ) {
        return None;
    }
    Some(crate::domain::mapping_runtime::value_matches_rule(
        actual,
        std::slice::from_ref(&condition.equals),
    ))
}

pub fn extract_points(source: &HttpSource, response: &Value) -> Result<Vec<PointReading>, String> {
    if source
        .response_condition
        .as_ref()
        .is_some_and(|c| condition_result(c, response) != Some(true))
    {
        return Err("SMA_HTTP_SOURCE_CONDITION_FAILED".into());
    }
    let root = response
        .pointer(source.response_path.as_deref().unwrap_or(""))
        .filter(|value| !value.is_null())
        .ok_or("SMA_HTTP_SOURCE_RESPONSE_PATH_MISSING")?;
    Ok(source
        .points
        .iter()
        .map(|point| read_point(root, point))
        .collect())
}

fn read_point(root: &Value, point: &HttpPoint) -> PointReading {
    let mut reading = PointReading {
        point_key: point.point_key.clone(),
        value: None,
        quality: None,
        observed_at: None,
        sample_id: None,
        error_code: None,
    };
    let outcome = (|| {
        let node = match &point.selector {
            None => root,
            Some(selector) => {
                let array = root
                    .pointer(&selector.path)
                    .and_then(Value::as_array)
                    .ok_or("SMA_HTTP_POINT_ARRAY_MISSING")?;
                let mut matches = array
                    .iter()
                    .filter(|item| item.pointer(&selector.key) == Some(&selector.value));
                let item = matches.next().ok_or("SMA_HTTP_POINT_MISSING")?;
                if matches.next().is_some() {
                    return Err("SMA_HTTP_POINT_ID_DUPLICATE");
                }
                item
            }
        };
        reading.quality = field(node, &point.quality_path)
            .and_then(Value::as_str)
            .map(str::to_owned);
        reading.sample_id = field(node, &point.sample_id_path).and_then(|value| {
            value
                .as_str()
                .map(str::to_owned)
                .or_else(|| value.is_number().then(|| value.to_string()))
        });
        reading.observed_at = field(node, &point.observed_at_path)
            .and_then(Value::as_str)
            .filter(|value| chrono::DateTime::parse_from_rfc3339(value).is_ok())
            .map(str::to_owned);
        let value = node.pointer(&point.path).filter(|value| !value.is_null());
        reading.value = value.filter(|v| value_type(v, &point.data_type)).cloned();
        if !point.accepted_quality.is_empty()
            && !reading
                .quality
                .as_ref()
                .is_some_and(|quality| point.accepted_quality.contains(quality))
        {
            return Err("SMA_HTTP_POINT_QUALITY_REJECTED");
        }
        if value.is_none() {
            return Err("SMA_HTTP_POINT_MISSING");
        }
        if reading.value.is_none() {
            return Err("SMA_HTTP_POINT_TYPE_INVALID");
        }
        Ok(())
    })();
    reading.error_code = outcome.err().map(str::to_owned);
    reading
}

fn field<'a>(node: &'a Value, path: &Option<String>) -> Option<&'a Value> {
    node.pointer(path.as_deref()?)
}

/// 用稳定摘要核对最新值所属来源定义，与配置文档分离保存。
pub fn source_definition_key(definition: &Value) -> String {
    let hash = definition
        .to_string()
        .bytes()
        .fold(0xcbf29ce484222325_u64, |hash, byte| {
            (hash ^ u64::from(byte)).wrapping_mul(0x100000001b3)
        });
    format!("{hash:016x}")
}
