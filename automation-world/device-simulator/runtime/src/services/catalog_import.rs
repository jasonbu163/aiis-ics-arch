//! 完整 PLC 目录原文选择、监听确认及草稿原子提交；不连接来源、不启动实例。
use crate::{
    app::App,
    domain::{
        configuration::*,
        plc_catalog::{self, CatalogBinding, CatalogDbMapping, CatalogPointMapping},
        source::SourceVersion,
    },
    services::configuration::Preview,
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs::File,
    io::Read,
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

struct Selected {
    path: PathBuf,
    sha: String,
    preview: Option<String>,
    expires: Instant,
}
#[derive(Default)]
pub struct CatalogImports {
    pending: BTreeMap<String, Selected>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PreviewIntent {
    pub file_token: String,
    pub expected_etag: String,
    pub host: String,
    pub port: u16,
    pub rack: u8,
    pub slot: u8,
    pub connection_confirmed: bool,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ConfirmIntent {
    pub file_token: String,
    pub token: String,
    pub expected_etag: String,
    pub candidate_sha256: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CancelIntent {
    pub file_token: String,
}
fn read(path: &Path) -> Result<Vec<u8>, String> {
    let file = File::open(path).map_err(|_| "catalog_file_unavailable")?;
    if !file
        .metadata()
        .map_err(|_| "catalog_file_unavailable")?
        .is_file()
    {
        return Err("catalog_file_unavailable".into());
    }
    let mut bytes = Vec::new();
    file.take(1024 * 1024 + 1)
        .read_to_end(&mut bytes)
        .map_err(|_| "catalog_file_unavailable")?;
    Ok(bytes)
}
/// 路径只来自桌面原生文件选择器或测试宿主，前端不传路径。
pub fn choose(app: &App, path: &Path) -> Result<Value, String> {
    let bytes = read(path)?;
    let document = plc_catalog::parse(&bytes)?;
    let sha = hash_bytes(&bytes);
    let name = path
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("PLC JSON")
        .to_string();
    let mut imports = app.catalog_imports.lock().map_err(|_| "catalog_state")?;
    imports.pending.retain(|_, p| p.expires > Instant::now());
    if imports.pending.len() >= 8 {
        return Err("catalog_preview_capacity".into());
    }
    let token = uuid();
    imports.pending.insert(
        token.clone(),
        Selected {
            path: path.to_path_buf(),
            sha: sha.clone(),
            preview: None,
            expires: Instant::now() + Duration::from_secs(300),
        },
    );
    Ok(
        json!({"fileToken":token,"fileName":name,"byteCount":bytes.len(),"fileSha256":sha,"document":document}),
    )
}
fn snapshot(path: &Path, sha: &str) -> Result<(Vec<u8>, plc_catalog::CatalogDocument), String> {
    let bytes = read(path)?;
    if hash_bytes(&bytes) != sha {
        return Err("catalog_file_changed".into());
    }
    let doc = plc_catalog::parse(&bytes)?;
    Ok((bytes, doc))
}
fn source_ids(c: &plc_catalog::CatalogDocument) -> BTreeSet<String> {
    std::iter::once(c.origin.plc_id.clone())
        .chain(c.dbs.iter().flat_map(|db| {
            std::iter::once(db.id.clone()).chain(db.points.iter().map(|p| p.id.clone()))
        }))
        .collect()
}
pub fn preview(app: &App, intent: PreviewIntent) -> Result<Preview, String> {
    if !intent.connection_confirmed
        || !intent
            .host
            .parse::<std::net::Ipv4Addr>()
            .is_ok_and(|v| v.is_loopback() && v.to_string() == intent.host)
        || intent.port == 0
        || intent.rack > 7
        || intent.slot > 31
    {
        return Err("catalog_listener_invalid".into());
    }
    let mut imports = app.catalog_imports.lock().map_err(|_| "catalog_state")?;
    let selected = imports
        .pending
        .get_mut(&intent.file_token)
        .ok_or("catalog_preview_stale")?;
    if selected.expires <= Instant::now() {
        return Err("catalog_preview_stale".into());
    }
    let (bytes, c) = snapshot(&selected.path, &selected.sha)?;
    let target_tsap = c.plc.connection.remote_tsap.unwrap_or(
        0x100 + u16::from(c.plc.connection.rack) * 32 + u16::from(c.plc.connection.slot),
    );
    let listen_tsap = 0x100 | (u16::from(intent.rack) << 5) | u16::from(intent.slot);
    if target_tsap != listen_tsap {
        return Err("catalog_tsap_unrepresentable".into());
    }
    let state = app.configuration.get()?;
    if state.etag != intent.expected_etag {
        return Err(format!("etag_conflict:{}", state.etag));
    }
    if state.workspace.instances.len() >= 8 {
        return Err("instance_capacity".into());
    }
    if state
        .workspace
        .instances
        .iter()
        .any(|i| i.host == intent.host && i.port == intent.port)
    {
        return Err("catalog_endpoint_conflict".into());
    }
    let incoming = source_ids(&c);
    for i in &state.workspace.instances {
        if (c.origin.kind == "device_simulator"
            && c.origin.profile_id == app.configuration.store.profile_id
            && c.origin.plc_id == i.id)
            || incoming.contains(&i.id)
            || i.dbs.iter().any(|d| {
                incoming.contains(&d.id) || d.points.iter().any(|p| incoming.contains(&p.id))
            })
        {
            return Err("catalog_identity_conflict".into());
        }
        if let Some(binding) = &i.catalog {
            let source = state
                .workspace
                .source_versions
                .iter()
                .find(|s| s.version_id == binding.source_version_id)
                .ok_or("catalog_source_invalid")?;
            let prior = plc_catalog::parse(&source.bytes)?;
            if prior.origin == c.origin || !incoming.is_disjoint(&source_ids(&prior)) {
                return Err("catalog_identity_conflict".into());
            }
        }
    }
    let mut workspace = state.workspace;
    let version = SourceVersion {
        version_id: uuid(),
        lineage_id: uuid(),
        blob_sha256: selected.sha.clone(),
        logical_name: "plc-catalog.json".into(),
        import_profile: "plc_catalog_v1".into(),
        bytes,
    };
    let mut dbs = Vec::new();
    let mut mappings = Vec::new();
    for db in &c.dbs {
        let local_db_id = uuid();
        let mut points = Vec::new();
        let mut point_mappings = Vec::new();
        for p in &db.points {
            let id = uuid();
            point_mappings.push(CatalogPointMapping {
                local_point_id: id.clone(),
                catalog_point_id: p.id.clone(),
            });
            points.push(PointConfig {
                id,
                name: p.name.clone(),
                display_name: p.display_name.clone().unwrap_or_default(),
                display_names: p.display_names.clone(),
                description: p.description.clone(),
                data_type: p.data_type.clone(),
                enabled: false,
                source_path: p.source_path.clone().unwrap_or_default(),
                segments: vec![],
                byte: Some(p.byte_offset),
                bit: p.bit,
                manual_reason: String::new(),
                manual: false,
                policy: Default::default(),
                confirmations: Default::default(),
            });
        }
        mappings.push(CatalogDbMapping {
            local_db_id: local_db_id.clone(),
            catalog_db_id: db.id.clone(),
            points: point_mappings,
        });
        dbs.push(DbConfig {
            id: local_db_id,
            name: db.name.clone(),
            number: db.number,
            length: db.size_bytes,
            enabled: false,
            manual: false,
            binding: None,
            points,
            policy: Default::default(),
            regions: vec![],
            address_confirmation: None,
        });
    }
    let instance = InstanceConfig {
        id: uuid(),
        name: c.plc.name.clone(),
        host: intent.host.clone(),
        port: intent.port,
        rack: intent.rack,
        slot: intent.slot,
        calling_tsap: c.plc.connection.local_tsap.unwrap_or(0x100),
        max_connections: 16,
        max_handshakes: 4,
        policy: Default::default(),
        dbs,
        names_confirmation: None,
        catalog: Some(CatalogBinding {
            source_version_id: version.version_id.clone(),
            source_sha256: version.blob_sha256.clone(),
            dbs: mappings,
        }),
    };
    let id = instance.id.clone();
    workspace.source_versions.push(version);
    workspace.instances.push(instance);
    if let Some(old) = selected.preview.take() {
        app.configuration.finish_preview(&old);
    }
    let preview = app.configuration.preview("catalog_import", &intent.expected_etag, workspace, json!({"instanceId":id,"fileSha256":selected.sha,"sourceConnection":c.plc.connection,"listener":{"host":intent.host,"port":intent.port,"rack":intent.rack,"slot":intent.slot,"callingTsap":c.plc.connection.local_tsap.unwrap_or(0x100),"calledTsap":listen_tsap},"document":c}))?;
    selected.preview = Some(preview.token.clone());
    Ok(preview)
}
pub fn confirm(
    app: &App,
    intent: ConfirmIntent,
) -> Result<crate::infrastructure::config_store::SaveResult, String> {
    let mut imports = app.catalog_imports.lock().map_err(|_| "catalog_state")?;
    let selected = imports
        .pending
        .get(&intent.file_token)
        .ok_or("catalog_preview_stale")?;
    if selected.expires <= Instant::now() || selected.preview.as_deref() != Some(&intent.token) {
        return Err("catalog_preview_stale".into());
    }
    if let Err(e) = snapshot(&selected.path, &selected.sha) {
        app.configuration.finish_preview(&intent.token);
        imports.pending.remove(&intent.file_token);
        return Err(e);
    }
    let result = app.configuration.confirm(
        "catalog_import",
        &intent.token,
        &intent.expected_etag,
        &intent.candidate_sha256,
    );
    if result.is_ok() {
        imports.pending.remove(&intent.file_token);
    }
    result
}
pub fn cancel(app: &App, intent: CancelIntent) -> Result<Value, String> {
    let mut imports = app.catalog_imports.lock().map_err(|_| "catalog_state")?;
    if let Some(selected) = imports.pending.remove(&intent.file_token) {
        if let Some(token) = selected.preview {
            app.configuration.finish_preview(&token);
        }
    }
    Ok(json!({"cancelled":true}))
}
