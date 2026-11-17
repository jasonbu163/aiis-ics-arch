//! 逐 PLC 目录导入：原字节、目标和草稿 ETag 绑定单次预览，确认时重新校验并事务保存。
use super::local_supervisor::LocalEngine;
use crate::domain::{
    local_configuration::*,
    local_runtime::ConfigurationView,
    local_sample::{digest, encode},
    plc_catalog::{self, Catalog, CatalogBinding, Connection, PointMapping},
    point_naming::NameMode,
};
use serde::{Deserialize, Serialize};
use std::{collections::BTreeSet, time::Instant};

#[derive(Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct CatalogRequest {
    pub bytes: Vec<u8>,
    pub filename: String,
    pub expected_etag: String,
    pub target: Option<Connection>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct CatalogConfirmation {
    pub input: CatalogRequest,
    pub preview_token: String,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct CatalogPreview {
    pub catalog: Catalog,
    pub sha256: String,
    pub target: Connection,
    pub preview_token: String,
    pub etag: String,
}
pub(crate) struct CachedCatalog {
    input_digest: String,
    token: String,
    source_id: String,
    candidate: Configuration,
    pub(crate) created: Instant,
}

fn candidate(
    current: &Configuration,
    catalog: &Catalog,
    raw: &str,
    sha: &str,
    filename: &str,
    target: &Connection,
    source_id: &str,
) -> LocalResult<Configuration> {
    if filename.is_empty()
        || filename.len() > 255
        || filename.contains(['/', '\\'])
        || !filename.to_ascii_lowercase().ends_with(".json")
        || filename.starts_with(crate::domain::yaml_migration::PRIVATE_NAME)
    {
        return Err("catalog_filename_invalid".into());
    }
    if !plc_catalog::valid_connection(target) {
        return Err("catalog_connection_invalid".into());
    }
    if current.plcs.len() >= 4 {
        return Err("configuration_limits".into());
    }
    let endpoint = format!(
        "{}:{}:{}/{}",
        target.host, target.port, target.rack, target.slot
    );
    if current.plcs.iter().any(|p| p.endpoint() == endpoint) {
        return Err("duplicate_endpoint".into());
    }
    let mut ids = BTreeSet::from([catalog.origin.plc_id.as_str(), source_id]);
    if ids.len() != 2 {
        return Err("catalog_identity_conflict".into());
    }
    for db in &catalog.dbs {
        if !ids.insert(&db.id) || db.points.iter().any(|point| !ids.insert(&point.id)) {
            return Err("catalog_identity_conflict".into());
        }
    }
    if current.plcs.iter().any(|p| ids.contains(p.id.as_str()))
        || current.dbs.iter().any(|d| ids.contains(d.id.as_str()))
        || current.points.iter().any(|p| ids.contains(p.id.as_str()))
        || current.groups.iter().any(|g| ids.contains(g.id.as_str()))
        || current.sources.iter().any(|s| ids.contains(s.id.as_str()))
    {
        return Err("catalog_identity_conflict".into());
    }
    let mut next = current.clone();
    let plc_id = catalog.origin.plc_id.clone();
    next.plcs.push(Plc {
        id: plc_id.clone(),
        name: catalog.plc.name.clone(),
        enabled: false,
        host: target.host.clone(),
        port: target.port,
        rack: target.rack,
        slot: target.slot,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    });
    next.sources.push(SourceDocument {
        id: source_id.into(),
        name: filename.into(),
        content: raw.into(),
        sha256: sha.into(),
        plc_id: plc_id.clone(),
        db_number: None,
        diagnostics: vec![],
        lineage_id: None,
    });
    for db in &catalog.dbs {
        next.dbs.push(Db {
            id: db.id.clone(),
            plc_id: plc_id.clone(),
            source_id: source_id.into(),
            name: db.name.clone(),
            number: db.number,
            length: db.size_bytes,
            complete: true,
            flat: true,
            tree: vec![],
            import_binding: None,
        });
        let mut mappings = vec![];
        for point in &db.points {
            mappings.push(PointMapping {
                local_point_id: point.id.clone(),
                catalog_point_id: point.id.clone(),
            });
            next.points.push(Point {
                id: point.id.clone(),
                plc_id: plc_id.clone(),
                db_id: db.id.clone(),
                source_path: point.source_path.clone().unwrap_or_default(),
                name: point.name.clone(),
                name_mode: Some(NameMode::Manual),
                data_type: point.data_type.clone(),
                comment: point.description.clone().unwrap_or_default(),
                enabled: false,
                group_id: None,
                address: Some(Address {
                    offset: point.byte_offset,
                    bit: point.bit,
                    confirmed: true,
                    origin: "catalog".into(),
                    reason: "operator_confirmed_catalog".into(),
                }),
            });
            if let Some(names) = &point.display_names {
                if !names.empty() {
                    next.point_display_names
                        .insert(point.id.clone(), names.clone());
                }
            }
            if let Some(name) = &point.display_name {
                next.point_legacy_display_names
                    .insert(point.id.clone(), name.clone());
            }
        }
        next.catalog_bindings.push(CatalogBinding {
            local_db_id: db.id.clone(),
            source_id: source_id.into(),
            source_sha256: sha.into(),
            source_kind: "exchange_json".into(),
            origin_db_id: db.id.clone(),
            point_mappings: mappings,
        });
    }
    validate_display_names(&next)?;
    plc_catalog::verify_bindings(&next)?;
    Ok(next)
}

fn input_digest(r: &CatalogRequest, sha: &str, target: &Connection) -> LocalResult<String> {
    Ok(digest(&encode(&(
        &r.filename,
        &r.expected_etag,
        sha,
        target,
    ))?))
}

impl LocalEngine {
    pub fn preview_catalog(&self, r: CatalogRequest) -> LocalResult<CatalogPreview> {
        self.invalidate_previews();
        let view = self.configuration()?;
        if view.etag != r.expected_etag {
            return Err("draft_conflict".into());
        }
        let (catalog, raw, sha) = plc_catalog::parse(&r.bytes)?;
        let target = r
            .target
            .clone()
            .unwrap_or_else(|| catalog.plc.connection.clone());
        let source_id = id();
        let next = candidate(
            &view.draft,
            &catalog,
            &raw,
            &sha,
            &r.filename,
            &target,
            &source_id,
        )?;
        let source = next
            .sources
            .iter()
            .find(|s| s.id == source_id)
            .unwrap()
            .clone();
        self.storage
            .call(true, move |s| s.ensure_catalog_new(&source))?;
        let hash = input_digest(&r, &sha, &target)?;
        let token = id();
        *self.catalog_preview.lock().unwrap() = Some(CachedCatalog {
            input_digest: hash,
            token: token.clone(),
            source_id,
            candidate: next,
            created: Instant::now(),
        });
        Ok(CatalogPreview {
            catalog,
            sha256: sha,
            target,
            preview_token: token,
            etag: view.etag,
        })
    }

    pub fn confirm_catalog(&self, r: CatalogConfirmation) -> LocalResult<ConfigurationView> {
        let cached = self
            .catalog_preview
            .lock()
            .unwrap()
            .take()
            .ok_or("catalog_preview_required")?;
        let (catalog, raw, sha) = plc_catalog::parse(&r.input.bytes)?;
        let target = r
            .input
            .target
            .clone()
            .unwrap_or_else(|| catalog.plc.connection.clone());
        if cached.created.elapsed().as_secs() >= 300
            || cached.token != r.preview_token
            || cached.input_digest != input_digest(&r.input, &sha, &target)?
        {
            return Err("catalog_preview_conflict".into());
        }
        let view = self.configuration()?;
        if view.etag != r.input.expected_etag {
            return Err("draft_conflict".into());
        }
        let next = candidate(
            &view.draft,
            &catalog,
            &raw,
            &sha,
            &r.input.filename,
            &target,
            &cached.source_id,
        )?;
        if next != cached.candidate {
            return Err("catalog_preview_conflict".into());
        }
        let result = self.save_candidate(next, r.input.expected_etag)?;
        self.invalidate_previews();
        self.event("catalog_imported", &catalog.origin.plc_id, "committed");
        Ok(result)
    }
}
