//! 地址预览直接消费共享core；人工确认需理由且不自动覆盖原人工地址。
use super::configuration::{Configuration, Preview};
use crate::domain::{configuration::*, layout};
use serde::{Deserialize, Serialize};
use serde_json::json;
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct LayoutIntent {
    pub expected_etag: String,
    pub instance_id: String,
    pub db_id: String,
    pub method: String,
    #[serde(default)]
    pub reason: String,
}
pub fn preview(service: &Configuration, intent: LayoutIntent) -> Result<Preview, String> {
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
    let db = i
        .dbs
        .iter_mut()
        .find(|d| d.id == intent.db_id)
        .ok_or("db_not_found")?;
    if intent.method == "standard" {
        if db.manual
            || db
                .points
                .iter()
                .any(|p| p.manual || !p.manual_reason.is_empty())
        {
            return Err("manual_layout_preserved".into());
        }
        let binding = db.binding.as_ref().ok_or("source_required")?;
        if db.points.iter().any(|p| p.data_type.starts_with("STRING[")) {
            return Err("string_layout_manual_required".into());
        }
        let tree = binding
            .tree
            .iter()
            .map(aiis_tia_import_core::FieldNode::from)
            .collect::<Vec<_>>();
        let expanded = aiis_tia_import_core::ExpandedDb {
            name: db.name.clone(),
            leaves: aiis_tia_import_core::structured_leaves(&tree),
            tree,
            standard: binding.standard,
        };
        let plan = aiis_tia_import_core::layout_standard(
            &expanded,
            aiis_tia_import_core::LayoutProfile::SiemensStep7V20StandardWordV1,
        )
        .map_err(|e| {
            e.first()
                .map(|e| e.code.clone())
                .unwrap_or("layout_invalid".into())
        })?;
        if plan.leaves.len() != db.points.len() {
            return Err("structure_incomplete".into());
        }
        for p in &mut db.points {
            let at = plan
                .leaves
                .iter()
                .find(|l| l.path == p.source_path)
                .ok_or("structure_incomplete")?;
            p.byte = Some(at.byte);
            p.bit = at.bit;
        }
        db.length = plan.length;
    } else if intent.method == "manual" {
        if intent.reason.trim().is_empty() || intent.reason.len() > 1000 {
            return Err("manual_reason_required".into());
        }
    } else {
        return Err("layout_method".into());
    }
    let mut spans = vec![];
    for p in &db.points {
        let byte = p.byte.ok_or("address_unconfirmed")?;
        let width = crate::domain::typed_value::width(&p.data_type)? as u32;
        if byte.checked_add(width).is_none_or(|v| v > db.length)
            || p.data_type == "BOOL" && p.bit.is_none()
            || p.data_type != "BOOL" && p.bit.is_some()
        {
            return Err("address_invalid".into());
        }
        let first = byte * 8 + p.bit.unwrap_or(0) as u32;
        spans.push((
            first,
            first + if p.data_type == "BOOL" { 1 } else { width * 8 },
        ));
    }
    spans.sort();
    if spans.windows(2).any(|p| p[0].1 > p[1].0) {
        return Err("layout_overlap".into());
    }
    db.address_confirmation = Some(AddressConfirmation {
        structure_sha256: layout::structure_signature(db),
        layout_sha256: layout::layout_signature(db),
        method: intent.method.clone(),
        reason: intent.reason.clone(),
    });
    i.names_confirmation = None;
    let details = json!({"dbId":db.id,"length":db.length,"method":intent.method,"reason":intent.reason,"initializersImported":false});
    service.preview("layout", &intent.expected_etag, state.workspace, details)
}
