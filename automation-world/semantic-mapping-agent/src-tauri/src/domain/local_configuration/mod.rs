//! 本地配置纯域：全图引用/类型/固定边界校验，资源变更及已保存快照纯预览。
use crate::{contracts::local_configuration::*, domain::mapping_runtime as runtime};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
pub fn text<'a>(v: &'a Value, k: &str) -> Result<&'a str, String> {
    v[k].as_str()
        .ok_or_else(|| format!("SMA_CONFIGURATION_FIELD_INVALID:{k}"))
}
fn valid_key(s: &str) -> bool {
    !s.is_empty() && s.len() <= 256 && !s.chars().any(|c| c.is_control() || c.is_whitespace())
}
fn fields(v: &Value, allowed: &[&str]) -> Result<(), String> {
    if v.as_object()
        .ok_or("SMA_CONFIGURATION_OBJECT_REQUIRED")?
        .keys()
        .any(|k| !allowed.contains(&k.as_str()))
    {
        return Err("SMA_CONFIGURATION_FIELD_UNKNOWN".into());
    }
    Ok(())
}
fn typed(t: &str) -> bool {
    matches!(t, "string" | "integer" | "number" | "boolean" | "datetime")
}
fn compatible(a: &str, b: &str) -> bool {
    a == b || (a == "integer" && b == "number")
}
fn value_type(v: &Value, t: &str) -> bool {
    match t {
        "string" => v.is_string(),
        "integer" => v.as_i64().is_some(),
        "number" => v.is_number(),
        "boolean" => v.is_boolean(),
        "datetime" => v
            .as_str()
            .is_some_and(|s| chrono::DateTime::parse_from_rfc3339(s).is_ok()),
        _ => false,
    }
}
pub fn key_field(r: &str) -> Result<&'static str, String> {
    match r {
        "targetApis" => Ok("apiKey"),
        "mappingValueRules" => Ok("valueRuleKey"),
        "mappings" => Ok("mappingKey"),
        "materials" => Ok("materialKey"),
        _ => Err("SMA_CONFIGURATION_RESOURCE_INVALID".into()),
    }
}
pub fn collection<'a>(d: &'a ConfigurationDocument, r: &str) -> Result<&'a Vec<Value>, String> {
    match r {
        "targetApis" => Ok(&d.target_apis),
        "mappingValueRules" => Ok(&d.mapping_value_rules),
        "mappings" => Ok(&d.mappings),
        "materials" => Ok(&d.materials),
        _ => Err("SMA_CONFIGURATION_RESOURCE_INVALID".into()),
    }
}
fn collection_mut<'a>(
    d: &'a mut ConfigurationDocument,
    r: &str,
) -> Result<&'a mut Vec<Value>, String> {
    match r {
        "targetApis" => Ok(&mut d.target_apis),
        "mappingValueRules" => Ok(&mut d.mapping_value_rules),
        "mappings" => Ok(&mut d.mappings),
        "materials" => Ok(&mut d.materials),
        _ => Err("SMA_CONFIGURATION_RESOURCE_INVALID".into()),
    }
}
pub fn backup(d: &ConfigurationDocument) -> ConfigurationBackup {
    ConfigurationBackup {
        format: FORMAT.into(),
        schema_version: 1,
        document: d.clone(),
    }
}
mod preview;
mod transform;
mod validation;
pub use preview::saved_preview;
pub use transform::transform;
pub use validation::validate;
