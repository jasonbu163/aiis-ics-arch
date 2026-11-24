//! Serialized, transactional flow revisions, catalog import and logical bindings.
use crate::domain::{
    ca_catalog::{Catalog, Connection, Db, Point},
    ca_flow::{checked_json, id, sha, Document, Issue, Kind, NodeBody},
};
use crate::infrastructure::ca_store;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, BTreeSet},
    path::PathBuf,
    sync::{Mutex, MutexGuard},
    time::Instant,
};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct Saved {
    pub document: Document,
    pub semantic_sha256: String,
    pub file_sha256: String,
}
impl Saved {
    pub fn bytes(&self) -> Vec<u8> {
        serde_json::to_vec_pretty(&self.document).expect("typed document")
    }
    fn new(document: Document) -> Self {
        let bytes = serde_json::to_vec_pretty(&document).expect("typed document");
        Self {
            semantic_sha256: document.digest(),
            file_sha256: sha(&bytes),
            document,
        }
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct CatalogRecord {
    pub id: String,
    pub file_sha256: String,
    pub raw: String,
    pub catalog: Catalog,
    pub binding: Option<Connection>,
    #[serde(default)]
    pub point_aliases: BTreeMap<String, String>,
}
impl CatalogRecord {
    pub fn point(&self, reference: &str) -> Option<(&Db, &Point)> {
        self.catalog.dbs.iter().find_map(|db| {
            db.points
                .iter()
                .find(|point| {
                    self.point_aliases
                        .get(reference)
                        .map_or(point.name == reference, |id| id == &point.id)
                })
                .map(|point| (db, point))
        })
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct HttpBinding {
    pub base_url: String,
    #[serde(default)]
    pub headers: BTreeMap<String, String>,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub(crate) enum Binding {
    Plc {
        id: String,
        target: Connection,
    },
    Http {
        id: String,
        target: HttpBinding,
    },
    Point {
        id: String,
        point_id: String,
        alias: String,
    },
}
#[derive(Default, Clone, Serialize, Deserialize)]
pub(crate) struct Data {
    pub generation: u64,
    pub flows: Vec<Saved>,
    pub catalogs: Vec<CatalogRecord>,
    pub http: BTreeMap<String, HttpBinding>,
    pub tests: Vec<Value>,
}
pub(crate) enum Pending {
    Flow {
        path: PathBuf,
        sha: String,
    },
    Catalog {
        path: PathBuf,
        sha: String,
        generation: u64,
    },
    Test(crate::services::ca_node_test::Prepared),
}
pub(crate) struct Workspace {
    path: PathBuf,
    data: Mutex<Data>,
    tokens: Mutex<BTreeMap<String, (Instant, Pending)>>,
    pub fake: bool,
}
impl Workspace {
    pub fn open(root: PathBuf, fake: bool) -> Result<Self, String> {
        let path = root.join("workspace.json");
        let mut data: Data = ca_store::load(&path)?;
        let mut edited = false;
        for item in &mut data.tests {
            if item["status"] == "sending" {
                item["status"] = json!("unknown");
                item["error"] = json!("process_interrupted");
                edited = true;
            }
        }
        if edited {
            ca_store::save(&path, &data)?
        }
        Ok(Self {
            path,
            data: Mutex::new(data),
            tokens: Mutex::new(BTreeMap::new()),
            fake,
        })
    }
    pub fn snapshot(&self) -> Result<MutexGuard<'_, Data>, String> {
        self.data.lock().map_err(|_| "workspace_poisoned".into())
    }
    pub fn update<T>(&self, f: impl FnOnce(&mut Data) -> Result<T, String>) -> Result<T, String> {
        let mut data = self.snapshot()?;
        let mut next = data.clone();
        let result = f(&mut next)?;
        if next.generation != data.generation || next.tests != data.tests {
            ca_store::save(&self.path, &next)?;
            *data = next;
        }
        Ok(result)
    }
    pub fn issue(&self, pending: Pending) -> Result<String, String> {
        let mut tokens = self.tokens.lock().map_err(|_| "workspace_poisoned")?;
        tokens.retain(|_, (t, _)| t.elapsed().as_secs() < 300);
        if tokens.len() >= 32 {
            return Err("too_many_previews".into());
        }
        let token = Uuid::new_v4().to_string();
        tokens.insert(token.clone(), (Instant::now(), pending));
        Ok(token)
    }
    pub fn consume(&self, token: &str) -> Result<Pending, String> {
        self.tokens
            .lock()
            .map_err(|_| "workspace_poisoned")?
            .remove(token)
            .filter(|(t, _)| t.elapsed().as_secs() < 300)
            .map(|(_, p)| p)
            .ok_or_else(|| "preview_expired".into())
    }
    pub fn validate(&self, doc: &Document) -> Result<Vec<Issue>, String> {
        Ok(validate_with(&*self.snapshot()?, doc))
    }
    pub fn save_flow(&self, mut document: Document, expected: u32) -> Result<Saved, String> {
        self.update(|data| {
            if !validate_with(data, &document).is_empty() {
                return Err("flow_invalid".into());
            }
            let actual = data
                .flows
                .iter()
                .filter(|s| s.document.flow.flow_id == document.flow.flow_id)
                .map(|s| s.document.flow.revision)
                .max()
                .unwrap_or(0);
            if actual != expected {
                return Err("flow_revision_conflict".into());
            }
            if data.flows.len() >= 512 {
                return Err("flow_capacity".into());
            }
            document.flow.revision = actual.checked_add(1).ok_or("flow_revision_conflict")?;
            let saved = Saved::new(document);
            data.flows.push(saved.clone());
            data.generation += 1;
            Ok(saved)
        })
    }
    pub fn get_flow(&self, id: &str, revision: u32) -> Result<Saved, String> {
        self.snapshot()?
            .flows
            .iter()
            .find(|s| s.document.flow.flow_id == id && s.document.flow.revision == revision)
            .cloned()
            .ok_or("flow_not_found".into())
    }
    pub fn preview_flow(&self, path: PathBuf, raw: &[u8]) -> Result<Value, String> {
        let doc: Document = checked_json(raw)?;
        let data = self.snapshot()?;
        let issues = validate_with(&data, &doc);
        let status = match data.flows.iter().find(|s| {
            s.document.flow.flow_id == doc.flow.flow_id
                && s.document.flow.revision == doc.flow.revision
        }) {
            Some(s) if s.document == doc => "identical",
            Some(_) => "conflict",
            None => "new",
        };
        drop(data);
        let token = self.issue(Pending::Flow {
            path,
            sha: sha(raw),
        })?;
        let file_sha = sha(raw);
        Ok(
            json!({"document":doc,"issues":issues,"status":status,"token":token,"file_sha256":file_sha}),
        )
    }
    pub fn import_flow(&self, token: &str, copy_id: Option<String>) -> Result<Saved, String> {
        let Pending::Flow { path, sha: hash } = self.consume(token)? else {
            return Err("preview_mismatch".into());
        };
        let raw = ca_store::read_bytes(&path, crate::domain::ca_flow::MAX_JSON)?;
        if sha(&raw) != hash {
            return Err("source_changed".into());
        }
        let mut doc: Document = checked_json(&raw)?;
        self.update(|data| {
            if !validate_with(data, &doc).is_empty() {
                return Err("flow_invalid".into());
            }
            if let Some(copy_id) = copy_id {
                if !id(&copy_id)
                    || data
                        .flows
                        .iter()
                        .any(|s| s.document.flow.flow_id == copy_id)
                {
                    return Err("flow_identity_conflict".into());
                }
                doc.flow.flow_id = copy_id;
                doc.flow.revision = 1;
            }
            if let Some(s) = data.flows.iter().find(|s| {
                s.document.flow.flow_id == doc.flow.flow_id
                    && s.document.flow.revision == doc.flow.revision
            }) {
                return if s.document == doc {
                    Ok(s.clone())
                } else {
                    Err("flow_revision_conflict".into())
                };
            }
            if data.flows.len() >= 512 {
                return Err("flow_capacity".into());
            }
            let saved = Saved::new(doc);
            data.flows.push(saved.clone());
            data.generation += 1;
            Ok(saved)
        })
    }
    pub fn preview_catalog(&self, path: PathBuf, raw: &[u8]) -> Result<Value, String> {
        let (catalog, hash) = Catalog::parse(raw)?;
        let data = self.snapshot()?;
        let previous: Vec<_> = data
            .catalogs
            .iter()
            .filter(|p| p.catalog.origin == catalog.origin)
            .collect();
        let status = if previous.iter().any(|p| p.file_sha256 == hash) {
            "identical"
        } else if previous.is_empty() {
            "new"
        } else {
            "changed"
        };
        let diff = previous.last().map(|p| catalog_diff(&p.catalog, &catalog));
        let existing = previous
            .iter()
            .find(|p| p.file_sha256 == hash)
            .map(|p| p.id.clone());
        let generation = data.generation;
        drop(data);
        let token = self.issue(Pending::Catalog {
            path,
            sha: hash.clone(),
            generation,
        })?;
        Ok(
            json!({"catalog":catalog,"file_sha256":hash,"status":status,"existing":existing,"diff":diff,"token":token}),
        )
    }
    pub fn import_catalog(&self, token: &str, alias: &str) -> Result<Value, String> {
        let Pending::Catalog {
            path,
            sha: expected,
            generation,
        } = self.consume(token)?
        else {
            return Err("preview_mismatch".into());
        };
        let raw = ca_store::read_bytes(&path, crate::domain::ca_flow::MAX_JSON)?;
        let (catalog, hash) = Catalog::parse(&raw)?;
        if hash != expected {
            return Err("source_changed".into());
        }
        self.update(|data| {
            if data.generation != generation {
                return Err("preview_stale".into());
            }
            if let Some(existing) = data.catalogs.iter().find(|p| p.file_sha256 == hash) {
                return Ok(json!({"id":existing.id,"status":"identical"}));
            }
            if !id(alias) || data.catalogs.iter().any(|p| p.id == alias) {
                return Err("catalog_identity_conflict".into());
            }
            if data.catalogs.len() >= 32 {
                return Err("catalog_capacity".into());
            }
            data.catalogs.push(CatalogRecord {
                id: alias.into(),
                file_sha256: hash,
                raw: String::from_utf8(raw).map_err(|_| "catalog_encoding_invalid")?,
                catalog,
                binding: None,
                point_aliases: BTreeMap::new(),
            });
            data.generation += 1;
            Ok(json!({"id":alias,"status":"created"}))
        })
    }
    pub fn bindings(&self) -> Result<Value, String> {
        let data = self.snapshot()?;
        Ok(json!({
            "plcs":data.catalogs.iter().map(|r|json!({"id":r.id,"catalog":r.catalog,"file_sha256":r.file_sha256,"binding":r.binding,"point_aliases":r.point_aliases})).collect::<Vec<_>>(),
            "http":data.http.iter().map(|(id,h)|json!({"id":id,"base_url":h.base_url,"header_names":h.headers.keys().collect::<Vec<_>>()})).collect::<Vec<_>>(),
            "fake":self.fake
        }))
    }
    pub fn bind(&self, binding: Binding) -> Result<(), String> {
        self.update(|data| {
            match binding {
                Binding::Plc { id, target } => {
                    if !target.valid() || !target.default_tsap() {
                        return Err("binding_invalid".into());
                    }
                    let plc = data
                        .catalogs
                        .iter_mut()
                        .find(|r| r.id == id)
                        .ok_or("catalog_not_found")?;
                    if !plc.catalog.plc.connection.default_tsap() {
                        return Err("binding_tsap_unsupported".into());
                    }
                    plc.binding = Some(target);
                }
                Binding::Point {
                    id: plc_id,
                    point_id,
                    alias,
                } => {
                    let record = data
                        .catalogs
                        .iter_mut()
                        .find(|r| r.id == plc_id)
                        .ok_or("catalog_not_found")?;
                    if !id(&alias)
                        || !record
                            .catalog
                            .dbs
                            .iter()
                            .any(|db| db.points.iter().any(|p| p.id == point_id))
                    {
                        return Err("point_alias_invalid".into());
                    }
                    if let Some((_, point)) = record.point(&alias) {
                        return if point.id == point_id {
                            Ok(())
                        } else {
                            Err("point_alias_conflict".into())
                        };
                    }
                    record.point_aliases.insert(alias, point_id);
                }
                Binding::Http {
                    id: alias,
                    mut target,
                } => {
                    let url =
                        reqwest::Url::parse(&target.base_url).map_err(|_| "binding_invalid")?;
                    if !id(&alias)
                        || !matches!(url.scheme(), "http" | "https")
                        || url.host().is_none()
                        || !url.username().is_empty()
                        || url.password().is_some()
                        || url.path() != "/"
                        || url.query().is_some()
                        || url.fragment().is_some()
                        || target.headers.len() > 32
                    {
                        return Err("binding_invalid".into());
                    }
                    for (key, value) in &target.headers {
                        use reqwest::header::{HeaderName, HeaderValue};
                        if matches!(
                            key.to_ascii_lowercase().as_str(),
                            "host" | "content-length" | "transfer-encoding" | "connection"
                        ) || key.parse::<HeaderName>().is_err()
                            || value.len() > 4096
                            || HeaderValue::from_str(value).is_err()
                        {
                            return Err("binding_header_invalid".into());
                        }
                    }
                    target.base_url = url.origin().ascii_serialization();
                    data.http.insert(alias, target);
                }
            }
            data.generation += 1;
            Ok(())
        })
    }
}
fn catalog_diff(previous: &Catalog, next: &Catalog) -> Value {
    let points = |c: &Catalog| {
        c.dbs
            .iter()
            .flat_map(|db| {
                db.points
                    .iter()
                    .map(move |p| (p.id.clone(), json!({"db":db.number,"point":p})))
            })
            .collect::<BTreeMap<_, _>>()
    };
    let blocks = |catalog: &Catalog| {
        catalog
            .dbs
            .iter()
            .map(|db| {
                (
                    db.id.clone(),
                    json!({
                        "number":db.number, "name":db.name, "size_bytes":db.size_bytes,
                        "source_enabled":db.source_enabled
                    }),
                )
            })
            .collect::<BTreeMap<_, _>>()
    };
    let old_blocks = blocks(previous);
    let new_blocks = blocks(next);
    let db_changes = old_blocks
        .keys()
        .chain(new_blocks.keys())
        .collect::<BTreeSet<_>>()
        .into_iter()
        .filter_map(|id| {
            let before = old_blocks.get(id);
            let after = new_blocks.get(id);
            (before != after).then(|| json!({"id":id, "before":before, "after":after}))
        })
        .collect::<Vec<_>>();
    let old = points(previous);
    let new = points(next);
    json!({
        "added":new.keys().filter(|key|!old.contains_key(*key)).collect::<Vec<_>>(),
        "removed":old.keys().filter(|key|!new.contains_key(*key)).collect::<Vec<_>>(),
        "changed":new.iter().filter_map(|(k,v)|old.get(k).filter(|o|*o!=v).map(|_|k)).collect::<Vec<_>>(),
        "db_changes":db_changes,
        "connection_changed":json!(previous.plc.connection)!=json!(next.plc.connection)
    })
}
pub(crate) fn point_kind(t: &str) -> Option<Kind> {
    match t {
        "INT" => Some(Kind::Int16),
        "BOOL" => Some(Kind::Boolean),
        "REAL" => Some(Kind::Real),
        s if s.starts_with("STRING[") => Some(Kind::String),
        _ => None,
    }
}
fn validate_with(data: &Data, doc: &Document) -> Vec<Issue> {
    let mut issues = doc.validate();
    for n in &doc.flow.nodes {
        let point_check = |plc: &str, point: &str, kind: Kind| {
            data.catalogs
                .iter()
                .find(|p| p.id == plc)
                .and_then(|p| p.point(point))
                .is_some_and(|(_, p)| point_kind(&p.data_type) == Some(kind))
        };
        let ok = match &n.body {
            NodeBody::Read(p) => point_check(&p.plc_ref, &p.point_ref, p.value_type),
            NodeBody::Write(p) => point_check(&p.plc_ref, &p.point_ref, p.value_type),
            NodeBody::Http(h) => data.http.contains_key(&h.endpoint_ref),
            _ => true,
        };
        if !ok {
            issues.push(Issue {
                code: "resource_reference_invalid",
                node_id: Some(n.id.clone()),
            })
        }
    }
    issues
}
