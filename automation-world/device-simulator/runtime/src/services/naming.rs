//! 单instance完整NameBatch，保留所有未选/停用/manual名字，禁止逐DB独立命名。
use super::configuration::{Configuration, Preview};
use crate::domain::layout;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::BTreeSet;
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct NamesIntent {
    pub expected_etag: String,
    pub instance_id: String,
    pub point_ids: Vec<String>,
    #[serde(default)]
    pub address_only: bool,
}
pub fn preview(service: &Configuration, intent: NamesIntent) -> Result<Preview, String> {
    let mut state = service.get()?;
    if state.etag != intent.expected_etag {
        return Err(format!("etag_conflict:{}", state.etag));
    }
    let i = state
        .workspace
        .instances
        .iter_mut()
        .find(|i| i.id == intent.instance_id)
        .ok_or("instance_not_found")?;
    let selected: BTreeSet<_> = intent.point_ids.iter().collect();
    if selected.len() != intent.point_ids.len() {
        return Err("point_selection".into());
    }
    let entries = i
        .dbs
        .iter()
        .flat_map(|d| {
            d.points.iter().map(|p| aiis_tia_import_core::NameEntry {
                key: p.id.clone(),
                db_number: d.number,
                path: (!p.segments.is_empty()).then(|| {
                    p.segments
                        .iter()
                        .map(aiis_tia_import_core::PathSegment::from)
                        .collect()
                }),
                data_type: p.data_type.clone(),
                current_name: p.name.clone(),
                mutable: selected.contains(&p.id),
                address: if d.address_confirmation.as_ref().is_some_and(|c| {
                    c.layout_sha256 == layout::layout_signature(d)
                        && c.structure_sha256 == layout::structure_signature(d)
                }) {
                    p.byte
                        .map(|byte| aiis_tia_import_core::ConfirmedAddress { byte, bit: p.bit })
                } else {
                    None
                },
                manual_name: p.manual.then(|| p.name.clone()),
                address_only: intent.address_only,
            })
        })
        .collect::<Vec<_>>();
    if entries.iter().filter(|e| e.mutable).count() != selected.len() {
        return Err("point_selection".into());
    }
    let plan = aiis_tia_import_core::plan_names(&aiis_tia_import_core::NameBatch {
        profile: aiis_tia_import_core::NAME_PROFILE.into(),
        entries,
    })
    .map_err(|e| {
        e.first()
            .map(|e| e.code.clone())
            .unwrap_or("point_name_invalid".into())
    })?;
    let mut rows = vec![];
    let mut enabled_pending = false;
    for row in plan.rows {
        let p = i
            .dbs
            .iter_mut()
            .flat_map(|d| &mut d.points)
            .find(|p| p.id == row.key)
            .unwrap();
        match row.resolution {
            aiis_tia_import_core::NameResolution::Resolved { name, mode } => {
                p.name = name.clone();
                rows.push(json!({"pointId":p.id,"name":name,"mode":mode,"reason":row.reason}));
            }
            aiis_tia_import_core::NameResolution::Pending => {
                enabled_pending |= p.enabled;
                rows.push(json!({"pointId":p.id,"pending":true,"reason":row.reason}));
            }
        }
    }
    i.names_confirmation = (!enabled_pending).then(|| layout::names_signature(i));
    service.preview(
        "names",
        &intent.expected_etag,
        state.workspace,
        json!({"rows":rows,"enabledPending":enabled_pending}),
    )
}
