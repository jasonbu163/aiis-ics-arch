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
use std::{
    collections::{BTreeMap, BTreeSet},
    time::Instant,
};

#[derive(Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct CatalogRequest {
    pub bytes: Vec<u8>,
    pub filename: String,
    pub expected_etag: String,
    pub target: Option<Connection>,
    #[serde(default)]
    pub as_new_local_instance: bool,
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
    pub history_conflict: bool,
    pub local_plc_id: String,
    pub local_db_ids: BTreeMap<String, String>,
    pub local_point_ids: BTreeMap<String, String>,
}
#[derive(Clone)]
struct LocalIds {
    plc: String,
    dbs: BTreeMap<String, String>,
    points: BTreeMap<String, String>,
}
impl LocalIds {
    fn new(catalog: &Catalog, remap: bool) -> Self {
        let mut used: BTreeSet<String> = std::iter::once(catalog.origin.plc_id.clone())
            .chain(catalog.dbs.iter().map(|d| d.id.clone()))
            .chain(
                catalog
                    .dbs
                    .iter()
                    .flat_map(|d| d.points.iter().map(|p| p.id.clone())),
            )
            .collect();
        let mut allocate = |original: &str| {
            if !remap {
                return original.to_string();
            }
            loop {
                let next = id();
                if used.insert(next.clone()) {
                    return next;
                }
            }
        };
        let plc = allocate(&catalog.origin.plc_id);
        let dbs = catalog
            .dbs
            .iter()
            .map(|d| (d.id.clone(), allocate(&d.id)))
            .collect();
        let points = catalog
            .dbs
            .iter()
            .flat_map(|d| &d.points)
            .map(|p| (p.id.clone(), allocate(&p.id)))
            .collect();
        Self { plc, dbs, points }
    }
}
pub(crate) struct CachedCatalog {
    input_digest: String,
    token: String,
    source_id: String,
    candidate: Configuration,
    ids: LocalIds,
    history_conflict: bool,
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
    local: &LocalIds,
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
    let mut ids = BTreeSet::from([local.plc.as_str(), source_id]);
    if ids.len() != 2 {
        return Err("catalog_identity_conflict".into());
    }
    for db in &catalog.dbs {
        if !ids.insert(&local.dbs[&db.id])
            || db
                .points
                .iter()
                .any(|point| !ids.insert(&local.points[&point.id]))
        {
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
    let plc_id = local.plc.clone();
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
            id: local.dbs[&db.id].clone(),
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
                local_point_id: local.points[&point.id].clone(),
                catalog_point_id: point.id.clone(),
            });
            next.points.push(Point {
                id: local.points[&point.id].clone(),
                plc_id: plc_id.clone(),
                db_id: local.dbs[&db.id].clone(),
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
                        .insert(local.points[&point.id].clone(), names.clone());
                }
            }
            if let Some(name) = &point.display_name {
                next.point_legacy_display_names
                    .insert(local.points[&point.id].clone(), name.clone());
            }
        }
        next.catalog_bindings.push(CatalogBinding {
            local_db_id: local.dbs[&db.id].clone(),
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
        r.as_new_local_instance,
    ))?))
}

impl LocalEngine {
    pub fn preview_catalog(&self, r: CatalogRequest) -> LocalResult<CatalogPreview> {
        let _activation = self
            .activation
            .try_lock()
            .map_err(|_| "activation_pending")?;
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
        let loaded = self
            .loaded
            .lock()
            .unwrap()
            .as_ref()
            .map(|l| l.configuration.clone());
        let (c, t, running) = (catalog.clone(), target.clone(), loaded.clone());
        let historical = self
            .storage
            .call(true, move |s| s.catalog_history(&c, &t, running.as_ref()))?;
        if r.as_new_local_instance && !historical {
            return Err("catalog_history_absent".into());
        }
        let ids = LocalIds::new(&catalog, historical);
        let next = candidate(
            &view.draft,
            &catalog,
            &raw,
            &sha,
            &r.filename,
            &target,
            &source_id,
            &ids,
        )?;
        let source = next
            .sources
            .iter()
            .find(|s| s.id == source_id)
            .unwrap()
            .clone();
        let checked = next.clone();
        self.storage.call(true, move |s| {
            s.ensure_catalog_new(&source, &checked, loaded.as_ref())
        })?;
        let hash = input_digest(&r, &sha, &target)?;
        let token = id();
        *self.catalog_preview.lock().unwrap() = Some(CachedCatalog {
            input_digest: hash,
            token: token.clone(),
            source_id,
            candidate: next,
            ids: ids.clone(),
            history_conflict: historical,
            created: Instant::now(),
        });
        Ok(CatalogPreview {
            catalog,
            sha256: sha,
            target,
            preview_token: token,
            etag: view.etag,
            history_conflict: historical,
            local_plc_id: ids.plc,
            local_db_ids: ids.dbs,
            local_point_ids: ids.points,
        })
    }

    pub fn confirm_catalog(&self, r: CatalogConfirmation) -> LocalResult<ConfigurationView> {
        let _activation = self
            .activation
            .try_lock()
            .map_err(|_| "activation_pending")?;
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
        if cached.history_conflict && !r.input.as_new_local_instance {
            return Err("catalog_history_choice_required".into());
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
            &cached.ids,
        )?;
        if next != cached.candidate {
            return Err("catalog_preview_conflict".into());
        }
        let mut result = self.save_candidate(next, r.input.expected_etag)?;
        self.invalidate_previews();
        self.event("catalog_imported", &cached.ids.plc, "committed");
        result.imported_local_plc_id = Some(cached.ids.plc);
        Ok(result)
    }
}
