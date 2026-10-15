//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/contracts/collection_facts/mod.rs
//! Description: Strict parser for the DTB-011 collection_facts.json type contract.
//! Main Features:
//!   - Rejects unknown fields, duplicate map keys, cross-group duplicates, and int aliases
//!   - Enforces stable source and lowercase dotted fact-point names without extra dependencies

use std::collections::BTreeMap;
use std::fmt;

use serde::de::{MapAccess, Visitor};
use serde::{Deserialize, Deserializer};

use crate::domain::collection_facts::{CollectionFactsContract, FactDataType};

pub const EXAMPLE: &str = r#"{
  "contract_version": "collection-facts.v1",
  "source_key": "wincc-line-01",
  "current": {
    "device1.body.position": "string",
    "vehicle.position": "string"
  },
  "incremental": {
    "production.total": "integer",
    "right_heat_box_03.temperature": "number"
  }
}"#;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct RawContract {
    contract_version: String,
    source_key: String,
    #[serde(deserialize_with = "deserialize_unique_points")]
    current: BTreeMap<String, FactDataType>,
    #[serde(deserialize_with = "deserialize_unique_points")]
    incremental: BTreeMap<String, FactDataType>,
}

pub fn parse(raw: &str) -> Result<CollectionFactsContract, String> {
    let parsed: RawContract = serde_json::from_str(raw)
        .map_err(|error| format!("COLLECTION_FACT_CONTRACT_JSON_INVALID:{error}"))?;
    if !is_contract_version(&parsed.contract_version) {
        return Err("COLLECTION_FACT_CONTRACT_VERSION_INVALID".to_string());
    }
    if !is_source_key(&parsed.source_key) {
        return Err("COLLECTION_FACT_SOURCE_KEY_INVALID".to_string());
    }
    if parsed.current.is_empty() && parsed.incremental.is_empty() {
        return Err("COLLECTION_FACT_POINTS_EMPTY".to_string());
    }
    for name in parsed.current.keys().chain(parsed.incremental.keys()) {
        if !is_fact_name(name) {
            return Err(format!("COLLECTION_FACT_NAME_INVALID:{name}"));
        }
    }
    if let Some(name) = parsed
        .current
        .keys()
        .find(|name| parsed.incremental.contains_key(*name))
    {
        return Err(format!(
            "COLLECTION_FACT_NAME_DUPLICATE_ACROSS_GROUPS:{name}"
        ));
    }
    Ok(CollectionFactsContract {
        contract_version: parsed.contract_version,
        source_key: parsed.source_key,
        current: parsed.current,
        incremental: parsed.incremental,
    })
}

pub fn pretty(contract: &CollectionFactsContract) -> Result<String, String> {
    serde_json::to_string_pretty(contract)
        .map_err(|error| format!("COLLECTION_FACT_CONTRACT_SERIALIZE_FAILED:{error}"))
}

pub fn example() -> CollectionFactsContract {
    parse(EXAMPLE).expect("built-in collection_facts.json example must stay valid")
}

fn is_contract_version(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 50
        && value.starts_with("collection-facts.")
        && value.bytes().all(|byte| {
            byte.is_ascii_lowercase() || byte.is_ascii_digit() || matches!(byte, b'.' | b'-' | b'_')
        })
}

fn is_source_key(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 100
        && value.bytes().all(|byte| {
            byte.is_ascii_lowercase() || byte.is_ascii_digit() || matches!(byte, b'.' | b'-' | b'_')
        })
}

pub fn is_fact_name(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 255
        && value.split('.').all(|segment| {
            !segment.is_empty()
                && segment
                    .bytes()
                    .all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'_')
        })
}

fn deserialize_unique_points<'de, D>(
    deserializer: D,
) -> Result<BTreeMap<String, FactDataType>, D::Error>
where
    D: Deserializer<'de>,
{
    struct UniquePointMapVisitor;

    impl<'de> Visitor<'de> for UniquePointMapVisitor {
        type Value = BTreeMap<String, FactDataType>;

        fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
            formatter.write_str("a collection fact point/type object")
        }

        fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
        where
            A: MapAccess<'de>,
        {
            let mut points = BTreeMap::new();
            while let Some((name, data_type)) = map.next_entry::<String, FactDataType>()? {
                if points.insert(name.clone(), data_type).is_some() {
                    return Err(serde::de::Error::custom(format!(
                        "duplicate collection fact point {name}"
                    )));
                }
            }
            Ok(points)
        }
    }

    deserializer.deserialize_map(UniquePointMapVisitor)
}
