//! 本地配置用例：保存/导入两步确认与CAS；服务不构造SQL或从服务器任意路径读取。
use super::local_supervisor::LocalEngine;
use crate::{
    domain::{
        local_configuration::*,
        local_runtime::ConfigurationView,
        source_import::{Identification, ImportRequest},
    },
    infrastructure::{
        plc_layout,
        tia_source::{self, ImportPreview},
    },
};
impl LocalEngine {
    pub fn configuration(&self) -> LocalResult<ConfigurationView> {
        let mut view = self.storage.call(true, |s| s.configuration())?;
        view.loaded = self
            .loaded
            .lock()
            .unwrap()
            .as_ref()
            .map(|l| l.revision.clone());
        view.phase = if self.gate.lock().unwrap().closed {
            "activation_pending"
        } else {
            "loaded"
        }
        .into();
        Ok(view)
    }
    pub fn save(&self, draft: Configuration, etag: String) -> LocalResult<ConfigurationView> {
        self.invalidate_previews();
        let previous = self.configuration()?;
        if previous.etag != etag {
            return Err("draft_conflict".into());
        }
        protect_derived(&previous.draft, &draft)?;
        self.save_candidate(draft, etag)
    }
    fn save_candidate(
        &self,
        mut draft: Configuration,
        etag: String,
    ) -> LocalResult<ConfigurationView> {
        if draft.plcs.len() > 4
            || draft.points.len() > 16384
            || draft.dbs.len() > 128
            || draft.groups.len() > 32
            || draft.sources.len() > 128
        {
            return Err("configuration_limits".into());
        }
        for p in &mut draft.plcs {
            if p.id.is_empty() {
                p.id = id()
            }
            if let Ok(ip) = p.host.parse::<std::net::Ipv4Addr>() {
                p.host = ip.to_string()
            }
        }
        for d in &mut draft.dbs {
            if d.id.is_empty() {
                d.id = id()
            }
        }
        for p in &mut draft.points {
            if p.id.is_empty() {
                p.id = id()
            }
        }
        for g in &mut draft.groups {
            if g.id.is_empty() {
                g.id = id()
            }
        }
        let quota = draft.storage.quota_bytes;
        let cap = self.storage.call(true, move |s| s.capacity(quota))?;
        let encoded = crate::domain::local_sample::encode(&draft)?.len() as u64;
        if cap.config_bytes.saturating_mul(2) + encoded * 3 + 65536 > 64 * 1024 * 1024 {
            return Err("configuration_capacity".into());
        }
        self.storage
            .call(false, move |s| s.save_draft(&draft, &etag))?;
        self.event("draft_saved", "configuration", "committed");
        self.configuration()
    }
    pub fn invalidate_previews(&self) {
        *self.import_preview.lock().unwrap() = None;
        *self.offset_preview.lock().unwrap() = None;
    }
    pub fn identify_sources(&self, r: &ImportRequest) -> LocalResult<Identification> {
        self.invalidate_previews();
        let view = self.configuration()?;
        if view.etag != r.expected_etag {
            return Err("draft_conflict".into());
        }
        tia_source::identify(&view.draft, r)
    }
    #[cfg(test)]
    pub fn import(
        &self,
        sources: Vec<SourceDocument>,
        etag: String,
        confirm: bool,
    ) -> LocalResult<ImportPreview> {
        self.import_selected(ImportRequest {
            sources,
            expected_etag: etag,
            confirm,
            stage: None,
            target_plc_id: None,
            mappings: vec![],
            preview_token: None,
            raw_proofs: vec![],
        })
    }
    pub fn import_selected(&self, r: ImportRequest) -> LocalResult<ImportPreview> {
        let outcome = (|| -> LocalResult<ImportPreview> {
            if r.stage.is_none()
                && (!r.mappings.is_empty()
                    || r.target_plc_id.is_some()
                    || !r.raw_proofs.is_empty()
                    || r.preview_token.is_some())
            {
                return Err("invalid_request".into());
            }
            let stage = r
                .stage
                .as_deref()
                .unwrap_or(if r.confirm { "confirm" } else { "preview" });
            if !matches!(stage, "preview" | "confirm") || r.confirm != (stage == "confirm") {
                return Err("invalid_request".into());
            }
            let view = self.configuration()?;
            if view.etag != r.expected_etag {
                return Err("draft_conflict".into());
            }
            let mut input = r.clone();
            input.stage = None;
            input.confirm = false;
            input.preview_token = None;
            let hash =
                crate::domain::local_sample::digest(&crate::domain::local_sample::encode(&input)?);
            let mut preview = if r.confirm {
                let cached = self
                    .import_preview
                    .lock()
                    .unwrap()
                    .take()
                    .ok_or("import_preview_required")?;
                if cached.0 != r.expected_etag
                    || cached.1 != hash
                    || cached.3.elapsed() > std::time::Duration::from_secs(300)
                    || (r.stage.is_some() && cached.2.preview_token != r.preview_token)
                {
                    return Err("import_preview_conflict".into());
                }
                if !cached.2.can_confirm {
                    return Err("source_import_blocked".into());
                }
                cached.2
            } else {
                *self.import_preview.lock().unwrap() = None;
                let mut p = if r.stage.is_some() {
                    tia_source::plan(&view.draft, &r)?
                } else {
                    tia_source::legacy_import(&view.draft, r.sources.clone())?
                };
                p.preview_token = Some(id());
                p.input_digest = hash.clone();
                p.etag = r.expected_etag.clone();
                *self.import_preview.lock().unwrap() = Some((
                    r.expected_etag.clone(),
                    hash,
                    p.clone(),
                    std::time::Instant::now(),
                ));
                p
            };
            if r.confirm {
                // Cached candidate is immutable and server-generated. SQL rechecks CAS/archives atomically.
                let saved = self.save_candidate(preview.configuration.clone(), r.expected_etag)?;
                preview.configuration = saved.draft;
                preview.etag = saved.etag;
                *self.offset_preview.lock().unwrap() = None;
                self.event(
                    "sources_imported",
                    "configuration",
                    if preview.unchanged {
                        "unchanged"
                    } else {
                        "committed"
                    },
                );
            }
            Ok(preview)
        })();
        if outcome.is_err() {
            let code = outcome
                .as_ref()
                .err()
                .unwrap()
                .split(':')
                .next()
                .unwrap_or("source_import_failed");
            let resource =
                serde_json::json!({"resource":"configuration","error_code":code}).to_string();
            self.event("source_import_rejected", &resource, "rejected");
        }
        outcome
    }
    pub fn offsets_at(
        &self,
        db: String,
        etag: Option<String>,
    ) -> LocalResult<Vec<plc_layout::OffsetChange>> {
        *self.offset_preview.lock().unwrap() = None;
        let c = self.configuration()?;
        if etag.as_ref().map(|e| e != &c.etag).unwrap_or(false) {
            return Err("draft_conflict".into());
        }
        let changes = plc_layout::preview(&c.draft, &db)?;
        let digest = changes
            .first()
            .map(|x| x.layout_digest.clone())
            .ok_or("incomplete_source")?;
        *self.offset_preview.lock().unwrap() =
            Some((c.etag, db, digest, std::time::Instant::now()));
        Ok(changes)
    }
    pub fn confirm_offsets_at(
        &self,
        db: String,
        points: Vec<String>,
        etag: String,
        digest: Option<String>,
    ) -> LocalResult<ConfigurationView> {
        let result = (|| -> LocalResult<ConfigurationView> {
            let cached = self
                .offset_preview
                .lock()
                .unwrap()
                .take()
                .ok_or("offset_preview_required")?;
            let mut c = self.configuration()?;
            if c.etag != etag {
                return Err("draft_conflict".into());
            }
            if cached.0 != etag
                || cached.1 != db
                || cached.3.elapsed() > std::time::Duration::from_secs(300)
                || digest.as_ref().map(|d| d != &cached.2).unwrap_or(false)
            {
                return Err("offset_preview_conflict".into());
            }
            let check = plc_layout::preview(&c.draft, &db)?;
            if check.first().map(|v| v.layout_digest.as_str()) != Some(cached.2.as_str()) {
                return Err("offset_preview_conflict".into());
            }
            plc_layout::confirm(&mut c.draft, &db, &points)?;
            self.save(c.draft, etag)
        })();
        self.event(
            if result.is_ok() {
                "offsets_confirmed"
            } else {
                "offsets_rejected"
            },
            &db,
            if result.is_ok() {
                "committed"
            } else {
                result.as_ref().err().unwrap()
            },
        );
        result
    }
}

// Only this service's parsed import preview can create or replace source-derived identity/structure.
// Public save edits user fields; it cannot turn an incomplete YAML or altered tree into proof.
fn protect_derived(old: &Configuration, new: &Configuration) -> LocalResult<()> {
    let kept = |plc: &str| new.plcs.iter().any(|p| p.id == plc);
    for src in &new.sources {
        if !old.sources.iter().any(|s| s == src) {
            return Err("source_import_required".into());
        }
    }
    for src in &old.sources {
        if kept(&src.plc_id) && !new.sources.iter().any(|s| s.id == src.id) {
            return Err("source_import_required".into());
        }
    }
    for db in &new.dbs {
        let original = old
            .dbs
            .iter()
            .find(|d| d.id == db.id)
            .ok_or("source_import_required")?;
        let mut candidate = db.clone();
        candidate.length = original.length;
        if &candidate != original {
            return Err("source_derived_conflict".into());
        }
    }
    for db in &old.dbs {
        if kept(&db.plc_id) && !new.dbs.iter().any(|d| d.id == db.id) {
            return Err("source_import_required".into());
        }
    }
    for point in &new.points {
        let original = old
            .points
            .iter()
            .find(|p| p.id == point.id)
            .ok_or("source_import_required")?;
        if point.plc_id != original.plc_id
            || point.db_id != original.db_id
            || point.source_path != original.source_path
            || point.data_type != original.data_type
        {
            return Err("source_derived_conflict".into());
        }
    }
    for point in &old.points {
        if kept(&point.plc_id) && !new.points.iter().any(|p| p.id == point.id) {
            return Err("source_import_required".into());
        }
    }
    Ok(())
}
