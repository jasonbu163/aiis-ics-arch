//! Siemens V20标准非优化完整嵌套布局；先行oracle逐叶校核，显式确认且人工地址受保护。
use crate::domain::local_configuration::*;
use serde::Serialize;
use std::collections::BTreeSet;
pub(crate) const PROFILE: &str = "siemens-step7-v20-standard-word-v1";
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct OffsetChange {
    pub point_id: String,
    pub old: Option<Address>,
    pub proposed: Address,
    pub protected_manual: bool,
    pub manual_conflict: bool,
    pub db_length: u32,
    pub profile: String,
    pub layout_digest: String,
    pub proposed_name: Option<String>,
    pub proposed_name_mode: Option<crate::domain::point_naming::NameMode>,
}
#[cfg(test)]
fn layout(
    nodes: &[FieldNode],
    cursor: &mut u32,
    out: &mut Vec<(String, u32, Option<u8>)>,
    depth: usize,
) -> LocalResult<()> {
    aiis_tia_import_core::layout::layout_nodes(
        &super::tia_source::parser::tree_to_core(nodes),
        cursor,
        out,
        depth,
    )
}
pub(crate) fn preview(c: &Configuration, db_id: &str) -> LocalResult<Vec<OffsetChange>> {
    let d = c.dbs.iter().find(|d| d.id == db_id).ok_or("db_missing")?;
    super::tia_source::verify_db(c, d)?;
    let tree = super::tia_source::parser::tree_to_core(&d.tree);
    let plan = aiis_tia_import_core::layout_standard(
        &aiis_tia_import_core::ExpandedDb {
            name: d.name.clone(),
            leaves: aiis_tia_import_core::structured_leaves(&tree),
            tree,
            standard: true,
        },
        aiis_tia_import_core::LayoutProfile::SiemensStep7V20StandardWordV1,
    )
    .map_err(|v| v[0].code.clone())?;
    let length = plan.length;
    let rows = plan.leaves.into_iter().map(|r| (r.path, r.byte, r.bit));
    if length == 0 || length > d.length || length > 65536 {
        return Err("layout_db_length".into());
    }
    let mut hash_sources = vec![d.source_id.clone()];
    if let Some(binding) = &d.import_binding {
        hash_sources.extend(binding.udt_source_ids.clone());
    }
    let hashes: Vec<_> = hash_sources
        .iter()
        .map(|id| {
            c.sources
                .iter()
                .find(|s| s.id == *id)
                .map(|s| s.sha256.clone())
                .ok_or("incomplete_source")
        })
        .collect::<Result<_, _>>()?;
    let layout_digest = crate::domain::local_sample::digest(&crate::domain::local_sample::encode(
        &(PROFILE, d, hashes),
    )?);
    let mut changes = vec![];
    for (path, offset, bit) in rows {
        let p = c
            .points
            .iter()
            .find(|p| p.db_id == d.id && p.source_path == path)
            .ok_or("point_source_mismatch")?;
        let protected = p
            .address
            .as_ref()
            .map(|a| a.origin == "manual")
            .unwrap_or(false);
        let conflict = protected
            && p.address
                .as_ref()
                .map(|a| a.offset != offset || a.bit != bit)
                .unwrap_or(false);
        changes.push(OffsetChange {
            point_id: p.id.clone(),
            proposed_name: None,
            proposed_name_mode: None,
            old: p.address.clone(),
            proposed: Address {
                offset,
                bit,
                confirmed: false,
                origin: "inferred".into(),
                reason: PROFILE.into(),
            },
            protected_manual: protected,
            manual_conflict: conflict,
            db_length: length,
            profile: PROFILE.into(),
            layout_digest: layout_digest.clone(),
        });
    }
    let mut named = c.clone();
    let ids: BTreeSet<_> = changes
        .iter()
        .filter(|x| !x.protected_manual)
        .filter_map(|x| {
            let p = c.points.iter().find(|p| p.id == x.point_id)?;
            matches!(
                p.name_mode,
                Some(crate::domain::point_naming::NameMode::Pending)
                    | Some(crate::domain::point_naming::NameMode::AutoAddress)
            )
            .then_some(p.id.clone())
        })
        .collect();
    for row in &changes {
        if !row.protected_manual {
            let p = named
                .points
                .iter_mut()
                .find(|p| p.id == row.point_id)
                .unwrap();
            let mut a = row.proposed.clone();
            a.confirmed = true;
            p.address = Some(a)
        }
    }
    let proven = named
        .dbs
        .iter()
        .filter(|d| super::tia_source::verify_db(&named, d).is_ok())
        .map(|d| d.id.clone())
        .collect();
    crate::domain::point_naming::generated(&mut named, &ids, &proven, None, true)
        .map_err(|es| es[0].code.clone())?;
    for row in &mut changes {
        if ids.contains(&row.point_id) {
            let p = named.points.iter().find(|p| p.id == row.point_id).unwrap();
            row.proposed_name = Some(p.name.clone());
            row.proposed_name_mode = p.name_mode.clone();
        }
    }
    Ok(changes)
}
pub(crate) fn confirm(c: &mut Configuration, db_id: &str, ids: &[String]) -> LocalResult<()> {
    let changes = preview(c, db_id)?;
    let mut seen = BTreeSet::new();
    for id in ids {
        if !seen.insert(id) {
            return Err("offset_selection_invalid".into());
        }
        let change = changes
            .iter()
            .find(|x| &x.point_id == id)
            .ok_or("point_missing")?;
        if change.protected_manual {
            return Err("manual_address_protected".into());
        }
    }
    if ids.is_empty() {
        return Err("offset_selection_invalid".into());
    }
    let all = changes
        .iter()
        .all(|x| ids.contains(&x.point_id) && !x.protected_manual);
    let length = changes.first().map(|x| x.db_length);
    for mut x in changes {
        if ids.contains(&x.point_id) {
            x.proposed.confirmed = true;
            c.points
                .iter_mut()
                .find(|p| p.id == x.point_id)
                .ok_or("point_missing")?
                .address = Some(x.proposed);
        }
    }
    if all {
        if let Some(n) = length {
            c.dbs
                .iter_mut()
                .find(|d| d.id == db_id)
                .ok_or("db_missing")?
                .length = n;
        }
    }
    let selected = ids
        .iter()
        .filter(|id| {
            c.points.iter().any(|p| {
                p.id.as_str() == id.as_str()
                    && matches!(
                        p.name_mode,
                        Some(crate::domain::point_naming::NameMode::Pending)
                            | Some(crate::domain::point_naming::NameMode::AutoAddress)
                    )
            })
        })
        .cloned()
        .collect();
    let proven = c
        .dbs
        .iter()
        .filter(|d| super::tia_source::verify_db(c, d).is_ok())
        .map(|d| d.id.clone())
        .collect();
    crate::domain::point_naming::generated(c, &selected, &proven, None, true)
        .map_err(|es| es[0].code.clone())?;
    Ok(())
}
#[cfg(test)]
mod tests;
