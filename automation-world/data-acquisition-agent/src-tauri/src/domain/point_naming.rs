//! 技术名称单字段状态/预览DTO与共享纯模型适配；不持有SQL、来源I/O或时钟。
use super::local_configuration::*;
use aiis_tia_import_core as core;
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum NameMode {
    Pending,
    AutoPath,
    AutoAddress,
    Manual,
}
fn nullable<'de, D, T>(d: D) -> Result<Option<Option<T>>, D::Error>
where
    D: serde::Deserializer<'de>,
    T: Deserialize<'de>,
{
    Option::<T>::deserialize(d).map(Some)
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct PointPatch {
    pub name: Option<String>,
    pub comment: Option<String>,
    pub enabled: Option<bool>,
    #[serde(
        default,
        deserialize_with = "nullable",
        skip_serializing_if = "Option::is_none"
    )]
    pub group_id: Option<Option<String>>,
    #[serde(
        default,
        deserialize_with = "nullable",
        skip_serializing_if = "Option::is_none"
    )]
    pub address: Option<Option<Address>>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct NameRequest {
    pub expected_etag: String,
    pub plc_id: String,
    pub point_ids: Vec<String>,
    pub intent: String,
    pub patch: Option<PointPatch>,
}
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct NameConfirmation {
    pub input: NameRequest,
    pub preview_token: String,
    pub input_digest: String,
}
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct NameChange {
    pub point_id: String,
    pub source_path: String,
    pub old_name: String,
    pub old_mode: Option<NameMode>,
    pub proposed_name: String,
    pub proposed_mode: Option<NameMode>,
    pub address_confirmed: bool,
    pub reason: String,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct NamePreview {
    pub rows: Vec<NameChange>,
    pub readiness: Vec<Issue>,
    pub can_confirm: bool,
    pub unchanged: bool,
    pub input_digest: String,
    pub preview_token: String,
    pub etag: String,
}
pub(crate) struct CachedNames {
    pub input_digest: String,
    pub token: String,
    pub candidate: Configuration,
    pub preview: NamePreview,
    pub input: NameRequest,
    pub created: std::time::Instant,
}
fn address(p: &Point, db: &Db) -> Option<core::ConfirmedAddress> {
    let a = p.address.as_ref()?;
    let end = a.offset.checked_add(width(&p.data_type)?)?;
    if !a.confirmed
        || a.reason.trim().is_empty()
        || !matches!(a.origin.as_str(), "manual" | "inferred")
        || end > db.length
        || end > 65536
    {
        return None;
    }
    if (p.data_type == "BOOL" && a.bit.map(|b| b > 7).unwrap_or(true))
        || (p.data_type != "BOOL" && a.bit.is_some())
    {
        return None;
    }
    Some(core::ConfirmedAddress {
        byte: a.offset,
        bit: a.bit,
    })
}
fn tree_to_core(nodes: &[FieldNode]) -> Vec<core::FieldNode> {
    nodes
        .iter()
        .map(|n| core::FieldNode {
            name: n.name.clone(),
            path: n.path.clone(),
            data_type: n.data_type.clone(),
            line: n.line,
            comment: n.comment.clone(),
            lower: n.lower,
            upper: n.upper,
            children: tree_to_core(&n.children),
        })
        .collect()
}
pub(crate) fn generated(
    c: &mut Configuration,
    ids: &BTreeSet<String>,
    proven: &BTreeSet<String>,
    manual: Option<(&str, &str)>,
    preserve_address_mode: bool,
) -> Result<Vec<(String, String)>, Vec<Issue>> {
    let mut reasons = vec![];
    let plcs: BTreeSet<_> = c
        .points
        .iter()
        .filter(|p| ids.contains(&p.id))
        .map(|p| p.plc_id.clone())
        .collect();
    for plc in plcs {
        let mut entries = vec![];
        for p in c.points.iter().filter(|p| p.plc_id == plc) {
            let Some(d) = c.dbs.iter().find(|d| d.id == p.db_id) else {
                return Err(vec![issue("db_missing", &p.id)]);
            };
            let path = if proven.contains(&d.id) {
                core::structured_leaves(&tree_to_core(&d.tree))
                    .into_iter()
                    .find(|l| l.path == p.source_path && l.data_type == p.data_type)
                    .map(|l| l.segments)
            } else {
                None
            };
            entries.push(core::NameEntry {
                key: p.id.clone(),
                db_number: d.number,
                path,
                data_type: p.data_type.clone(),
                current_name: p.name.clone(),
                mutable: ids.contains(&p.id),
                address: address(p, d),
                address_only: preserve_address_mode && p.name_mode == Some(NameMode::AutoAddress),
                manual_name: manual.filter(|(id, _)| *id == p.id).map(|(_, s)| s.into()),
            });
        }
        let plan = core::plan_names(&core::NameBatch {
            profile: core::NAME_PROFILE.into(),
            entries,
        })
        .map_err(|ds| {
            ds.into_iter()
                .map(|d| Issue {
                    code: d.code,
                    path: d.path,
                    line: d.line,
                    file: d.file,
                })
                .collect::<Vec<_>>()
        })?;
        for row in plan.rows {
            let p = c.points.iter_mut().find(|p| p.id == row.key).unwrap();
            match row.resolution {
                core::NameResolution::Pending => {
                    p.name = String::new();
                    p.name_mode = Some(NameMode::Pending)
                }
                core::NameResolution::Resolved { name, mode } => {
                    p.name = name;
                    p.name_mode = Some(match mode.as_str() {
                        "auto_path" => NameMode::AutoPath,
                        "auto_address" => NameMode::AutoAddress,
                        _ => NameMode::Manual,
                    })
                }
            }
            reasons.push((p.id.clone(), row.reason));
        }
    }
    Ok(reasons)
}
pub(crate) fn change(old: &Point, new: &Point, reason: &str) -> NameChange {
    NameChange {
        point_id: old.id.clone(),
        source_path: old.source_path.clone(),
        old_name: old.name.clone(),
        old_mode: old.name_mode.clone(),
        proposed_name: new.name.clone(),
        proposed_mode: new.name_mode.clone(),
        address_confirmed: new.address.as_ref().map(|a| a.confirmed).unwrap_or(false),
        reason: reason.into(),
    }
}
