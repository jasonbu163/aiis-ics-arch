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
}
fn aligned(bits: u32) -> LocalResult<u32> {
    bits.checked_add(15)
        .map(|n| n / 16 * 16)
        .ok_or("layout_overflow".into())
}
fn layout(
    nodes: &[FieldNode],
    cursor: &mut u32,
    out: &mut Vec<(String, u32, Option<u8>)>,
    depth: usize,
) -> LocalResult<()> {
    if depth > 8 {
        return Err("expansion_depth".into());
    }
    for n in nodes {
        let result = (|| -> LocalResult<()> {
            if !n.children.is_empty() {
                *cursor = aligned(*cursor)?;
                if n.data_type == "ARRAY" {
                    let lo = n.lower.ok_or("array_bounds")?;
                    let hi = n.upper.ok_or("array_bounds")?;
                    let count = i64::from(hi) - i64::from(lo) + 1;
                    if !(1..=1024).contains(&count) || n.children.len() != count as usize {
                        return Err("array_bounds".into());
                    }
                    if has_array(&n.children) {
                        return Err("nested_array".into());
                    }
                }
                layout(&n.children, cursor, out, depth + 1)?;
                *cursor = aligned(*cursor)?;
            } else {
                if n.data_type.starts_with("STRING[")
                    || n.data_type == "ARRAY"
                    || n.data_type == "STRUCT"
                {
                    return Err("offset_inference_unsupported".into());
                }
                let width = width(&n.data_type).ok_or("unsupported_type")?;
                let (byte, bit) = if n.data_type == "BOOL" {
                    let at = (*cursor / 8, Some((*cursor % 8) as u8));
                    *cursor = cursor.checked_add(1).ok_or("layout_overflow")?;
                    at
                } else {
                    let mut byte = cursor.checked_add(7).ok_or("layout_overflow")? / 8;
                    if width >= 2 {
                        byte = byte.checked_add(1).ok_or("layout_overflow")? / 2 * 2;
                    }
                    *cursor = byte
                        .checked_add(width)
                        .and_then(|b| b.checked_mul(8))
                        .ok_or("layout_overflow")?;
                    (byte, None)
                };
                out.push((n.path.clone(), byte, bit));
            }
            if *cursor > 65536 * 8 {
                return Err("layout_overflow".into());
            }
            Ok(())
        })();
        result.map_err(|e| {
            format!(
                "{}:path={}:line={}",
                e.split(':').next().unwrap_or("layout_invalid"),
                n.path,
                n.line
            )
        })?;
    }
    Ok(())
}
fn has_array(nodes: &[FieldNode]) -> bool {
    nodes
        .iter()
        .any(|n| n.data_type == "ARRAY" || has_array(&n.children))
}
pub(crate) fn preview(c: &Configuration, db_id: &str) -> LocalResult<Vec<OffsetChange>> {
    let d = c.dbs.iter().find(|d| d.id == db_id).ok_or("db_missing")?;
    super::tia_source::verify_db(c, d)?;
    let mut cursor = 0;
    let mut rows = vec![];
    layout(&d.tree, &mut cursor, &mut rows, 0)?;
    let length = aligned(cursor)? / 8;
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
    Ok(())
}
#[cfg(test)]
mod tests;
