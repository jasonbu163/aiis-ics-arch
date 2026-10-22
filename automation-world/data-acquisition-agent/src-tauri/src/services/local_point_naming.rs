//! 技术名只读预览/原子确认：单份300秒候选，输入摘要/随机token/ETag重核；不写SQL。
use super::local_supervisor::LocalEngine;
use crate::domain::local_runtime::ConfigurationView;
use crate::domain::{local_configuration::*, point_naming::*};
use std::{collections::BTreeSet, time::Instant};
pub(crate) fn proven_dbs(c: &Configuration) -> BTreeSet<String> {
    c.dbs
        .iter()
        .filter(|d| crate::infrastructure::tia_source::verify_db(c, d).is_ok())
        .map(|d| d.id.clone())
        .collect()
}
fn candidate(
    c: &Configuration,
    r: &NameRequest,
) -> LocalResult<(Configuration, Vec<NameChange>, Vec<Issue>)> {
    let ids: BTreeSet<_> = r.point_ids.iter().cloned().collect();
    if ids.is_empty()
        || ids.len() != r.point_ids.len()
        || ids.len() > 4096
        || !matches!(r.intent.as_str(), "generate" | "edit")
        || !c.plcs.iter().any(|p| p.id == r.plc_id)
        || r.point_ids
            .iter()
            .any(|id| !c.points.iter().any(|p| p.id == *id && p.plc_id == r.plc_id))
        || (r.intent == "edit" && (ids.len() != 1 || r.patch.is_none()))
        || (r.intent == "generate" && r.patch.is_some())
    {
        return Err("point_name_selection".into());
    }
    let mut next = c.clone();
    let mut mutable = ids.clone();
    let mut manual = None;
    if let Some(patch) = &r.patch {
        let p = next
            .points
            .iter_mut()
            .find(|p| p.id == r.point_ids[0])
            .unwrap();
        if let Some(comment) = &patch.comment {
            p.comment = comment.clone()
        }
        if let Some(enabled) = patch.enabled {
            p.enabled = enabled
        }
        if let Some(group) = &patch.group_id {
            p.group_id = group.clone()
        }
        if let Some(address) = &patch.address {
            p.address = address.clone()
        }
        let old = c.points.iter().find(|o| o.id == p.id).unwrap();
        if let Some(name) = patch.name.as_deref().filter(|n| *n != old.name) {
            manual = Some((p.id.clone(), name.to_string()))
        } else if matches!(old.name_mode, None | Some(NameMode::Manual)) {
            mutable.clear()
        }
    }
    let proven = proven_dbs(&next);
    let result = generated(
        &mut next,
        &mutable,
        &proven,
        manual
            .as_ref()
            .map(|(id, name)| (id.as_str(), name.as_str())),
        r.intent == "edit",
    );
    let (reasons, mut issues) = match result {
        Ok(rows) => (rows, vec![]),
        Err(es) => (vec![], es),
    };
    for p in next.points.iter().filter(|p| ids.contains(&p.id)) {
        if r.intent == "generate" && p.name_mode == Some(NameMode::Pending) {
            issues.push(issue("point_name_pending", &p.id))
        }
        if let Some(a) = &p.address {
            if a.confirmed
                && (a.reason.trim().is_empty()
                    || !matches!(a.origin.as_str(), "manual" | "inferred")
                    || a.offset
                        .checked_add(width(&p.data_type).unwrap_or(65537))
                        .map(|v| {
                            v > 65536
                                || next
                                    .dbs
                                    .iter()
                                    .find(|d| d.id == p.db_id)
                                    .map(|d| v > d.length)
                                    .unwrap_or(true)
                        })
                        .unwrap_or(true)
                    || (p.data_type == "BOOL" && a.bit.map(|b| b > 7).unwrap_or(true))
                    || (p.data_type != "BOOL" && a.bit.is_some()))
            {
                issues.push(issue("address_invalid", &p.id))
            }
        }
    }
    issues.extend(validate(&next).into_iter().filter(|i| {
        ids.contains(&i.path)
            && matches!(
                i.code.as_str(),
                "point_invalid"
                    | "point_name_invalid"
                    | "point_name_conflict"
                    | "cross_plc_group"
                    | "address_invalid"
                    | "address_overlap"
            )
    }));
    let rows = r
        .point_ids
        .iter()
        .map(|id| {
            let old = c.points.iter().find(|p| p.id == *id).unwrap();
            let new = next.points.iter().find(|p| p.id == *id).unwrap();
            change(
                old,
                new,
                reasons
                    .iter()
                    .find(|(key, _)| key == id)
                    .map(|(_, reason)| reason.as_str())
                    .unwrap_or("preserved"),
            )
        })
        .collect();
    Ok((next, rows, issues))
}
impl LocalEngine {
    pub fn preview_point_names(&self, r: NameRequest) -> LocalResult<NamePreview> {
        self.invalidate_previews();
        let current = self.configuration()?;
        if current.etag != r.expected_etag {
            return Err("draft_conflict".into());
        }
        let (next, rows, readiness) = candidate(&current.draft, &r)?;
        let hash = crate::domain::local_sample::digest(&crate::domain::local_sample::encode(&r)?);
        let token = id();
        let p = NamePreview {
            rows,
            can_confirm: readiness.is_empty(),
            unchanged: next == current.draft,
            readiness,
            input_digest: hash.clone(),
            preview_token: token.clone(),
            etag: current.etag,
        };
        *self.name_preview.lock().unwrap() = Some(CachedNames {
            input_digest: hash,
            token,
            candidate: next,
            preview: p.clone(),
            input: r,
            created: Instant::now(),
        });
        Ok(p)
    }
    pub fn confirm_point_names(&self, r: NameConfirmation) -> LocalResult<ConfigurationView> {
        let result = (|| {
            let cached = self
                .name_preview
                .lock()
                .unwrap()
                .take()
                .ok_or("name_preview_required")?;
            let hash = crate::domain::local_sample::digest(&crate::domain::local_sample::encode(
                &r.input,
            )?);
            if cached.created.elapsed().as_secs() >= 300
                || cached.token != r.preview_token
                || cached.input_digest != r.input_digest
                || hash != cached.input_digest
            {
                return Err("name_preview_conflict".into());
            }
            let current = self.configuration()?;
            if current.etag != r.input.expected_etag {
                return Err("draft_conflict".into());
            }
            if !cached.preview.can_confirm {
                return Err("point_name_blocked".into());
            }
            let (next, _, issues) = candidate(&current.draft, &cached.input)?;
            if !issues.is_empty() || next != cached.candidate {
                return Err("name_preview_conflict".into());
            }
            self.invalidate_previews();
            self.save_candidate(next, r.input.expected_etag)
        })();
        self.event(
            if result.is_ok() {
                "point_names_confirmed"
            } else {
                "point_names_rejected"
            },
            "configuration",
            if result.is_ok() {
                "committed"
            } else {
                result.as_ref().err().unwrap()
            },
        );
        result
    }
}
