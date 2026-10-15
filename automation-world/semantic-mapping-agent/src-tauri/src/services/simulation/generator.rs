//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/simulation/generator.rs
//! Description: Strict sequence and current-time-zone value generation for collection facts.
//! Main Features:
//!   - Normalizes typed JSON sequence elements to canonical Values API text
//!   - Generates current datetime values at Runtime tick time through a saved strategy

use std::str::FromStr;

use chrono::{DateTime, Local, SecondsFormat, Utc};
use chrono_tz::Tz;
use serde_json::Value;

use super::model::{SimulationFact, SimulationRule};

pub fn value(
    rule: &SimulationRule,
    fact: &SimulationFact,
    sequence_index: u64,
) -> Result<String, String> {
    if rule.sequence.is_empty() {
        return Err(format!(
            "COLLECTION_SIMULATION_SEQUENCE_VALUES_REQUIRED:{}",
            fact.name
        ));
    }
    let item = &rule.sequence[(sequence_index as usize) % rule.sequence.len()];
    let generated = normalize_value(fact, item)?;
    validate_value(fact, &generated)?;
    Ok(generated)
}

pub fn current_time_value(rule: &SimulationRule, fact: &SimulationFact) -> Result<String, String> {
    current_time_value_at(rule, fact, Utc::now())
}

pub fn current_time_value_at(
    rule: &SimulationRule,
    fact: &SimulationFact,
    now: DateTime<Utc>,
) -> Result<String, String> {
    validate_current_time_rule(rule, fact)?;
    let generated = match rule.current_time_mode.as_str() {
        "utc" => now.to_rfc3339_opts(SecondsFormat::Millis, true),
        "system" => now
            .with_timezone(&Local)
            .to_rfc3339_opts(SecondsFormat::Millis, false),
        "custom" => {
            let zone = Tz::from_str(rule.current_time_zone.as_deref().unwrap_or_default())
                .map_err(|_| {
                    format!(
                        "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_INVALID:{}",
                        fact.name
                    )
                })?;
            now.with_timezone(&zone)
                .to_rfc3339_opts(SecondsFormat::Millis, false)
        }
        _ => unreachable!("current-time mode is validated before generation"),
    };
    validate_value(fact, &generated)?;
    Ok(generated)
}

pub fn validate_current_time_rule(
    rule: &SimulationRule,
    fact: &SimulationFact,
) -> Result<(), String> {
    if fact.data_type != "datetime" {
        return Err(format!(
            "COLLECTION_SIMULATION_CURRENT_TIME_DATETIME_REQUIRED:{}",
            fact.name
        ));
    }
    match rule.current_time_mode.as_str() {
        "utc" | "system" if rule.current_time_zone.is_none() => Ok(()),
        "utc" | "system" => Err(format!(
            "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_UNEXPECTED:{}",
            fact.name
        )),
        "custom" => {
            let zone = rule.current_time_zone.as_deref().ok_or_else(|| {
                format!(
                    "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_REQUIRED:{}",
                    fact.name
                )
            })?;
            Tz::from_str(zone).map_err(|_| {
                format!(
                    "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_INVALID:{}",
                    fact.name
                )
            })?;
            Ok(())
        }
        _ => Err(format!(
            "COLLECTION_SIMULATION_CURRENT_TIME_MODE_INVALID:{}",
            fact.name
        )),
    }
}

pub fn should_update(fact: &SimulationFact, generated: &str) -> bool {
    fact.fact_kind == "incremental" || fact.value_text.as_deref() != Some(generated)
}

fn normalize_value(fact: &SimulationFact, value: &Value) -> Result<String, String> {
    let invalid = || format!("COLLECTION_SIMULATION_TYPE_INVALID:{}", fact.name);
    match fact.data_type.as_str() {
        "string" | "datetime" => value.as_str().map(ToString::to_string).ok_or_else(invalid),
        "integer" => value
            .as_i64()
            .map(|item| item.to_string())
            .or_else(|| value.as_u64().map(|item| item.to_string()))
            .ok_or_else(invalid),
        "number" => value
            .as_f64()
            .filter(|item| item.is_finite())
            .map(|item| serde_json::Number::from_f64(item).unwrap().to_string())
            .ok_or_else(invalid),
        "boolean" => value
            .as_bool()
            .map(|item| item.to_string())
            .ok_or_else(invalid),
        _ => Err(invalid()),
    }
}

pub fn validate_value(fact: &SimulationFact, value: &str) -> Result<(), String> {
    let valid_type = match fact.data_type.as_str() {
        "string" => true,
        "integer" => value.parse::<i64>().is_ok(),
        "number" => value.parse::<f64>().is_ok_and(f64::is_finite),
        "boolean" => matches!(value, "true" | "false"),
        "datetime" => DateTime::parse_from_rfc3339(value).is_ok(),
        _ => false,
    };
    if valid_type {
        Ok(())
    } else {
        Err(format!("COLLECTION_SIMULATION_TYPE_INVALID:{}", fact.name))
    }
}
