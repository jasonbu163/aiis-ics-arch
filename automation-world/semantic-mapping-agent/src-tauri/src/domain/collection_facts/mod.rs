//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/domain/collection_facts/mod.rs
//! Description: Framework-independent DTB-011 collection-fact domain contracts.
//! Main Features:
//!   - Defines typed collection_facts.json documents and synchronization summaries
//!   - Defines bounded fact inspection queries and row-version presentation
//!   - Keeps generic contract diffing without any device inventory adapter

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum FactDataType {
    String,
    Integer,
    Number,
    Boolean,
    Datetime,
}

impl FactDataType {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::String => "string",
            Self::Integer => "integer",
            Self::Number => "number",
            Self::Boolean => "boolean",
            Self::Datetime => "datetime",
        }
    }
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct CollectionFactsContract {
    pub contract_version: String,
    pub source_key: String,
    pub current: BTreeMap<String, FactDataType>,
    pub incremental: BTreeMap<String, FactDataType>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StoredCollectionFact {
    pub name: String,
    pub fact_kind: String,
    pub data_type: String,
    pub value_text: Option<String>,
    pub contract_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactChange {
    pub name: String,
    pub from: String,
    pub to: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Default)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactSyncSummary {
    pub added: Vec<String>,
    pub retained: Vec<String>,
    pub deleted: Vec<String>,
    pub kind_changes: Vec<CollectionFactChange>,
    pub type_changes: Vec<CollectionFactChange>,
    pub version_only: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactsWorkspace {
    pub contract_json: String,
    pub summary: CollectionFactSyncSummary,
    pub contract_origin: CollectionFactsContractOrigin,
    pub generated_counts: Option<GeneratedCollectionFactCounts>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum CollectionFactsContractOrigin {
    Saved,
    Generated,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct GeneratedCollectionFactCounts {
    pub current: usize,
    pub incremental: usize,
    pub total: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Default)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CollectionFactListQuery {
    pub source_key: Option<String>,
    pub name_contains: Option<String>,
    pub fact_kind: Option<String>,
    pub data_type: Option<String>,
    pub page: Option<usize>,
    pub page_size: Option<usize>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactRecord {
    pub id: i64,
    pub source_key: String,
    pub name: String,
    pub fact_kind: String,
    pub data_type: String,
    pub value_text: Option<String>,
    pub contract_version: String,
    pub updated_at: String,
    pub row_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct CollectionFactPage {
    pub items: Vec<CollectionFactRecord>,
    pub page: usize,
    pub page_size: usize,
    pub total: usize,
}

pub fn desired_facts(contract: &CollectionFactsContract) -> BTreeMap<String, StoredCollectionFact> {
    contract
        .current
        .iter()
        .map(|(name, data_type)| (name.clone(), desired(name, "current", *data_type, contract)))
        .chain(contract.incremental.iter().map(|(name, data_type)| {
            (
                name.clone(),
                desired(name, "incremental", *data_type, contract),
            )
        }))
        .collect()
}

pub fn plan_sync(
    contract: &CollectionFactsContract,
    existing: &[StoredCollectionFact],
) -> CollectionFactSyncSummary {
    let desired = desired_facts(contract);
    let existing_by_name: BTreeMap<_, _> = existing
        .iter()
        .map(|fact| (fact.name.as_str(), fact))
        .collect();
    let mut summary = CollectionFactSyncSummary::default();

    for (name, wanted) in &desired {
        let Some(current) = existing_by_name.get(name.as_str()) else {
            summary.added.push(name.clone());
            continue;
        };
        let kind_changed = current.fact_kind != wanted.fact_kind;
        let type_changed = current.data_type != wanted.data_type;
        if kind_changed {
            summary.kind_changes.push(CollectionFactChange {
                name: name.clone(),
                from: current.fact_kind.clone(),
                to: wanted.fact_kind.clone(),
            });
        }
        if type_changed {
            summary.type_changes.push(CollectionFactChange {
                name: name.clone(),
                from: current.data_type.clone(),
                to: wanted.data_type.clone(),
            });
        }
        if !kind_changed && !type_changed {
            if current.contract_version == contract.contract_version {
                summary.retained.push(name.clone());
            } else {
                summary.version_only.push(name.clone());
            }
        }
    }
    summary.deleted = existing
        .iter()
        .filter(|fact| !desired.contains_key(&fact.name))
        .map(|fact| fact.name.clone())
        .collect();
    summary
}

fn desired(
    name: &str,
    fact_kind: &str,
    data_type: FactDataType,
    contract: &CollectionFactsContract,
) -> StoredCollectionFact {
    StoredCollectionFact {
        name: name.to_string(),
        fact_kind: fact_kind.to_string(),
        data_type: data_type.as_str().to_string(),
        value_text: None,
        contract_version: contract.contract_version.clone(),
    }
}
