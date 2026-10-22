//! 配置保存与有界确认票据：普通草稿不能伪造来源/布局/初值/策略证明。
use crate::{
    domain::{configuration::*, layout},
    infrastructure::config_store::{SaveResult, Snapshot, Store},
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SaveIntent {
    pub expected_etag: String,
    pub workspace: Workspace,
    #[serde(default)]
    pub confirm_points: Vec<String>,
}
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Preview {
    pub token: String,
    pub expected_etag: String,
    pub kind: String,
    pub candidate_sha256: String,
    pub details: Value,
    pub workspace: Workspace,
}
struct Pending {
    kind: String,
    etag: String,
    candidate: Workspace,
    sha: String,
    details: Value,
    expires: Instant,
}
pub struct Configuration {
    pub store: Arc<Store>,
    pending: Mutex<BTreeMap<String, Pending>>,
}
// 确认属于实际DB布局；来源版本/注释及显示名称本身不改变该上下文。
fn same_confirmation_context(db: &DbConfig, old: &DbConfig) -> bool {
    db.number == old.number
        && db.length == old.length
        && db.points.len() == old.points.len()
        && db.points.iter().zip(&old.points).all(|(p, previous)| {
            p.id == previous.id
                && p.data_type == previous.data_type
                && p.segments == previous.segments
                && p.manual == previous.manual
                && p.byte == previous.byte
                && p.bit == previous.bit
        })
}
impl Configuration {
    pub fn new(store: Arc<Store>) -> Self {
        Self {
            store,
            pending: Mutex::new(BTreeMap::new()),
        }
    }
    pub fn get(&self) -> Result<Snapshot, String> {
        self.store.load()
    }
    pub fn save(&self, intent: SaveIntent) -> Result<SaveResult, String> {
        let (etag, candidate) = self.prepare(intent)?;
        self.store.save(&etag, candidate)
    }
    pub fn prepare(&self, intent: SaveIntent) -> Result<(String, Workspace), String> {
        let previous = self.get()?;
        if previous.etag != intent.expected_etag {
            return Err(format!("etag_conflict:{}", previous.etag));
        }
        let mut next = intent.workspace;
        if next.source_versions != previous.workspace.source_versions {
            return Err("derived_source_read_only".into());
        }
        for i in &mut next.instances {
            let old_i = previous.workspace.instances.iter().find(|v| v.id == i.id);
            for db in &mut i.dbs {
                let old_db = old_i.and_then(|v| v.dbs.iter().find(|v| v.id == db.id));
                if db.binding.as_ref() != old_db.and_then(|v| v.binding.as_ref())
                    && !(db.manual && db.binding.is_none())
                {
                    return Err("derived_source_read_only".into());
                }
                if db.binding.is_some() {
                    let old = old_db.ok_or("derived_source_read_only")?;
                    let topology = |d: &DbConfig| {
                        digest(
                            &d.points
                                .iter()
                                .map(|p| {
                                    (&p.id, &p.data_type, &p.source_path, &p.segments, p.manual)
                                })
                                .collect::<Vec<_>>(),
                        )
                    };
                    if topology(db) != topology(old) {
                        return Err("derived_structure_read_only".into());
                    }
                }
                db.address_confirmation = old_db
                    .and_then(|old| old.address_confirmation.clone())
                    .filter(|c| {
                        c.structure_sha256 == layout::structure_signature(db)
                            && c.layout_sha256 == layout::layout_signature(db)
                    });
            }
            i.names_confirmation = old_i
                .and_then(|old| old.names_confirmation.clone())
                .filter(|s| *s == layout::names_signature(i));
            let immutable = i.clone();
            for db in &mut i.dbs {
                let old_db = old_i.and_then(|i| i.dbs.iter().find(|d| d.id == db.id));
                let retain_confirmations = old_db
                    .map(|old| same_confirmation_context(db, old))
                    .unwrap_or(false);
                for point in &mut db.points {
                    let old = old_db
                        .filter(|_| retain_confirmations)
                        .and_then(|d| d.points.iter().find(|p| p.id == point.id));
                    point.confirmations = old.map(|p| p.confirmations.clone()).unwrap_or_default();
                    let immutable_db = immutable.dbs.iter().find(|d| d.id == db.id).unwrap();
                    match layout::effective_policy(&immutable, immutable_db, point) {
                        Ok(e) => {
                            if point.confirmations.initial.as_ref()
                                != layout::initial_signature(&point.data_type, &e)
                                    .ok()
                                    .as_ref()
                            {
                                point.confirmations.initial = None
                            }
                            if point.confirmations.policy.as_ref()
                                != Some(&layout::policy_signature(&e))
                            {
                                point.confirmations.policy = None
                            }
                        }
                        Err(_) => point.confirmations = Default::default(),
                    }
                }
            }
        }
        let confirmations: BTreeSet<_> = intent.confirm_points.iter().collect();
        if confirmations.len() != intent.confirm_points.len() || confirmations.len() > 4096 {
            return Err("point_selection".into());
        }
        let mut found = BTreeSet::new();
        for i in &mut next.instances {
            let immutable = i.clone();
            for db in &mut i.dbs {
                let immutable_db = immutable.dbs.iter().find(|d| d.id == db.id).unwrap();
                for p in &mut db.points {
                    if confirmations.contains(&p.id) {
                        let e = layout::effective_policy(&immutable, immutable_db, p)?;
                        p.confirmations.initial =
                            Some(layout::initial_signature(&p.data_type, &e)?);
                        p.confirmations.policy = Some(layout::policy_signature(&e));
                        found.insert(&p.id);
                    }
                }
            }
        }
        if found.len() != confirmations.len() {
            return Err("point_selection".into());
        }
        validate(&next)?;
        Ok((intent.expected_etag, next))
    }
    pub fn preview(
        &self,
        kind: &str,
        etag: &str,
        mut candidate: Workspace,
        details: Value,
    ) -> Result<Preview, String> {
        validate(&candidate)?;
        let current = self.get()?;
        if current.etag != etag {
            return Err(format!("etag_conflict:{}", current.etag));
        }
        // apply预览消费已确认的不可变revision，不是一次新的布局编辑。
        for i in candidate
            .instances
            .iter_mut()
            .filter(|_| matches!(kind, "import" | "layout"))
        {
            let old_i = current
                .workspace
                .instances
                .iter()
                .find(|old| old.id == i.id);
            for db in &mut i.dbs {
                let retain_confirmations = old_i
                    .and_then(|old| old.dbs.iter().find(|old| old.id == db.id))
                    .map(|old| same_confirmation_context(db, old))
                    .unwrap_or(false);
                if !retain_confirmations {
                    for point in &mut db.points {
                        point.confirmations = Default::default();
                    }
                }
            }
        }
        let mut pending = self.pending.lock().unwrap();
        pending.retain(|_, p| p.expires > Instant::now());
        let reserved: usize = pending
            .values()
            .map(|p| {
                serde_json::to_vec(&p.candidate)
                    .map(|b| b.len() * 2)
                    .unwrap_or(usize::MAX / 2)
            })
            .sum();
        if pending.len() >= 8
            || reserved.saturating_add(
                serde_json::to_vec(&candidate)
                    .map_err(|_| "configuration_format")?
                    .len()
                    * 2,
            ) > 64 * 1024 * 1024
        {
            return Err("preview_capacity".into());
        }
        let token = uuid();
        let sha = digest(&candidate);
        pending.insert(
            token.clone(),
            Pending {
                kind: kind.into(),
                etag: etag.into(),
                candidate: candidate.clone(),
                sha: sha.clone(),
                details: details.clone(),
                expires: Instant::now() + Duration::from_secs(300),
            },
        );
        Ok(Preview {
            token,
            expected_etag: etag.into(),
            kind: kind.into(),
            candidate_sha256: sha,
            details,
            workspace: candidate,
        })
    }
    pub fn pending_candidate(
        &self,
        kind: &str,
        token: &str,
        etag: &str,
        sha: &str,
    ) -> Result<(Workspace, Value), String> {
        let pending = self.pending.lock().unwrap();
        let p = pending.get(token).ok_or("preview_not_found")?;
        if p.kind != kind || p.etag != etag || p.sha != sha || p.expires <= Instant::now() {
            return Err("preview_stale".into());
        }
        Ok((p.candidate.clone(), p.details.clone()))
    }
    pub fn finish_preview(&self, token: &str) {
        self.pending.lock().unwrap().remove(token);
    }
    pub fn confirm(
        &self,
        kind: &str,
        token: &str,
        etag: &str,
        sha: &str,
    ) -> Result<SaveResult, String> {
        let mut pending = self.pending.lock().unwrap();
        let p = pending.get(token).ok_or("preview_not_found")?;
        if p.kind != kind || p.etag != etag || p.sha != sha || p.expires <= Instant::now() {
            return Err("preview_stale".into());
        }
        let candidate = p.candidate.clone();
        drop(pending);
        let result = self.store.save(etag, candidate)?;
        pending = self.pending.lock().unwrap();
        pending.remove(token);
        Ok(result)
    }
}
