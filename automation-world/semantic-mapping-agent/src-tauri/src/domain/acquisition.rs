//! 采集回环纯域：验证源点类型、保留采集值并构建一次 POST。
use crate::contracts::{
    acquisition::{LoopbackConfig, Point},
    local_configuration::ConfigurationDocument,
};
use chrono::{DateTime, Datelike, FixedOffset};
use serde::Serialize;
use serde_json::value::RawValue;
use std::collections::BTreeSet;

pub const LATEST: &str = "/api/v1/acquisition-data/latest";
pub const TARGET: &str = "/api/v1/integration/plc-facts/samples";
pub const INVALID: &str = "SMA_ACQUISITION_CONFIGURATION_INVALID";
pub const RESPONSE: &str = "SMA_ACQUISITION_RESPONSE_INVALID";

pub fn identifier(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 128
        && value.trim() == value
        && !value.bytes().any(|byte| byte < 32 || byte == 127)
}

pub fn require_material(config: &ConfigurationDocument, material_key: &str) -> Result<(), String> {
    if config.materials.iter().any(|entry| {
        entry["materialKey"] == material_key
            && entry["httpMethod"] == "GET"
            && entry["path"] == LATEST
    }) {
        return Ok(());
    }
    Err("SMA_ACQUISITION_MATERIAL_MISSING".into())
}

pub fn timestamp(value: &str) -> Result<DateTime<FixedOffset>, String> {
    DateTime::parse_from_rfc3339(value)
        .ok()
        .filter(|stamp| {
            stamp.year() >= 1000
                && value.ends_with("+08:00")
                && value.contains('T')
                && value
                    .split_once('.')
                    .is_none_or(|(_, micros)| micros.len() <= 12)
        })
        .ok_or_else(|| RESPONSE.into())
}

pub fn sequence(value: &str) -> bool {
    (1..=19).contains(&value.len())
        && !value.starts_with('0')
        && value.bytes().all(|byte| byte.is_ascii_digit())
        && value
            .parse::<u64>()
            .is_ok_and(|number| number < i64::MAX as u64)
}

pub fn validate_config(config: &LoopbackConfig) -> Result<(), String> {
    let target = &config.target;
    if config.plc_id == target.plc_id && config.db_number == target.db_number {
        return Err("SMA_ACQUISITION_TARGET_EQUALS_SOURCE".into());
    }
    let points: BTreeSet<_> = config.point_ids.iter().collect();
    let mappings: BTreeSet<_> = config.moves.iter().map(|rule| &rule.from).collect();
    if config.db_number == 0
        || target.db_number == 0
        || ![
            &config.material_key,
            &config.plc_id,
            &target.plc_id,
            &target.instance_id,
            &target.source_generation,
        ]
        .into_iter()
        .all(|text| identifier(text))
        || points.len() != config.point_ids.len()
        || points.len() > 512
        || mappings.len() != config.moves.len()
        || mappings.len() > 512
        || !points.iter().all(|key| identifier(key))
        || config.moves.iter().any(|rule| {
            !identifier(&rule.from)
                || (!points.is_empty() && !points.contains(&rule.from))
                || rule.to.as_ref().is_some_and(|value| !identifier(value))
                || rule.name.as_ref().is_some_and(|value| value.len() > 100)
        })
        || [config.group_id.as_ref(), config.config_revision.as_ref()]
            .into_iter()
            .flatten()
            .any(|value| !identifier(value))
    {
        return Err(INVALID.into());
    }
    Ok(())
}

fn limits(kind: &str) -> Option<(i64, i64)> {
    Some(match kind {
        "BYTE" | "USINT" => (0, 255),
        "WORD" | "UINT" => (0, 65_535),
        "DWORD" | "UDINT" => (0, 4_294_967_295),
        "INT" => (-32_768, 32_767),
        "DINT" => (-2_147_483_648, 2_147_483_647),
        _ => return None,
    })
}

fn value_fits(point: &Point) -> bool {
    let kind = point.data_type.as_str();
    let string_size = kind
        .strip_prefix("STRING[")
        .and_then(|value| value.strip_suffix(']'))
        .filter(|value| !value.starts_with('0'))
        .and_then(|value| value.parse::<usize>().ok())
        .filter(|size| (1..=254).contains(size));
    let known =
        matches!(kind, "BOOL" | "REAL" | "CHAR") || limits(kind).is_some() || string_size.is_some();
    let raw = point.value.get();
    match point.quality.as_str() {
        "bad" => {
            known
                && raw == "null"
                && point
                    .reason
                    .as_ref()
                    .is_some_and(|reason| !reason.is_empty() && reason.len() <= 128)
        }
        "good" => {
            point.reason.is_none()
                && match kind {
                    "BOOL" => matches!(raw, "true" | "false"),
                    // Parse directly from the decimal token; f64 → f32 would double-round at the overflow boundary.
                    "REAL" => raw.parse::<f32>().is_ok_and(f32::is_finite),
                    "CHAR" => serde_json::from_str::<String>(raw)
                        .is_ok_and(|value| value.len() == 1 && value.is_ascii()),
                    _ => {
                        if let Some((min, max)) = limits(kind) {
                            raw.parse::<i64>()
                                .is_ok_and(|value| (min..=max).contains(&value))
                        } else {
                            string_size.is_some_and(|size| {
                                serde_json::from_str::<String>(raw)
                                    .is_ok_and(|value| value.is_ascii() && value.len() <= size)
                            })
                        }
                    }
                }
        }
        _ => false,
    }
}

pub fn point_data(values: &[Box<RawValue>]) -> Result<Vec<Point>, String> {
    let mut keys = BTreeSet::new();
    values
        .iter()
        .map(|raw| {
            let point: Point = serde_json::from_str(raw.get()).map_err(|_| RESPONSE)?;
            if !identifier(&point.point_id)
                || point.name.len() > 100
                || !keys.insert(point.point_id.clone())
                || timestamp(&point.observed_at).is_err()
                || !value_fits(&point)
            {
                return Err(RESPONSE.into());
            }
            Ok(point)
        })
        .collect()
}

pub struct MappedSample {
    pub bytes: Vec<u8>,
    pub sampled_at: String,
}

pub fn body(
    config: &LoopbackConfig,
    points: Vec<Point>,
    sample_id: &str,
    source_seq: &str,
) -> Result<MappedSample, String> {
    validate_config(config)?;
    if !sequence(source_seq) {
        return Err("SMA_ACQUISITION_SEQUENCE_INVALID".into());
    }
    let mut selected: Vec<_> = points
        .into_iter()
        .filter(|point| config.point_ids.is_empty() || config.point_ids.contains(&point.point_id))
        .collect();
    if selected.is_empty() {
        return Err("SMA_ACQUISITION_EMPTY".into());
    }
    if !config.point_ids.is_empty() && selected.len() != config.point_ids.len() {
        return Err("SMA_ACQUISITION_POINTS_MISSING".into());
    }
    let mut target_ids = BTreeSet::new();
    for point in &mut selected {
        if let Some(rule) = config.moves.iter().find(|rule| rule.from == point.point_id) {
            if let Some(to) = &rule.to {
                point.point_id = to.clone();
            }
            if let Some(name) = &rule.name {
                point.name = name.clone();
            }
        }
        if !target_ids.insert(point.point_id.clone()) {
            return Err("SMA_ACQUISITION_POINTS_COLLIDE".into());
        }
    }
    if selected.len() > 512 {
        return Err("SMA_ACQUISITION_SAMPLE_TOO_LARGE".into());
    }
    let sampled_at = selected
        .iter()
        .max_by_key(|point| {
            // Same Shanghai offset, with validated timestamp precision.
            timestamp(&point.observed_at).ok()
        })
        .ok_or("SMA_ACQUISITION_EMPTY")?
        .observed_at
        .clone();
    let target = &config.target;
    #[derive(Serialize)]
    #[serde(rename_all = "camelCase")]
    struct Payload<'a> {
        contract_version: &'static str,
        instance_id: &'a str,
        sample_id: &'a str,
        plc_id: &'a str,
        db_number: u16,
        source_generation: &'a str,
        source_seq: &'a str,
        points: &'a [Point],
        group_id: Option<&'a str>,
        config_revision: Option<&'a str>,
    }
    // Serialize directly instead of going through Value, which normalizes the raw number -0.
    let bytes = serde_json::to_vec_pretty(&Payload {
        contract_version: "plc-facts/v2",
        instance_id: &target.instance_id,
        sample_id,
        plc_id: &target.plc_id,
        db_number: target.db_number,
        source_generation: &target.source_generation,
        source_seq,
        points: &selected,
        group_id: config.group_id.as_deref(),
        config_revision: config.config_revision.as_deref(),
    })
    .map_err(|_| RESPONSE)?;
    if bytes.len() > 512 * 1024 {
        return Err("SMA_ACQUISITION_SAMPLE_TOO_LARGE".into());
    }
    Ok(MappedSample { bytes, sampled_at })
}
