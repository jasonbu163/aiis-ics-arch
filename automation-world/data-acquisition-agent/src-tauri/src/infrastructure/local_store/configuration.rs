//! 配置草稿CAS、不可变版本与可恢复跨库token；数据库逻辑只存在本适配层。
use super::{sql_error, Stores};
use crate::domain::{
    local_configuration::{id, validate, Configuration, LocalResult},
    local_runtime::ConfigurationView,
    local_sample::{digest, encode, now},
};
use rusqlite::{params, OptionalExtension};
impl Stores {
    pub fn pending_activation(&self) -> LocalResult<Option<(String, String)>> {
        self.config.query_row("SELECT token,new_revision FROM activation_intents WHERE phase!='applied' ORDER BY created_at,token LIMIT 1",[],|r|Ok((r.get(0)?,r.get(1)?))).optional().map_err(sql_error)
    }
    pub fn configuration(&self) -> LocalResult<ConfigurationView> {
        let (etag, payload): (String, String) = self
            .config
            .query_row(
                "SELECT etag,payload FROM configuration_draft WHERE id=1",
                [],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        let draft: Configuration =
            serde_json::from_str(&payload).map_err(|_| "configuration_corrupt")?;
        let (active, previous): (Option<String>, Option<String>) = self
            .config
            .query_row(
                "SELECT active,previous FROM active_selection WHERE id=1",
                [],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        let used: Option<String> = self
            .runtime
            .query_row(
                "SELECT used_revision FROM runtime_metadata WHERE id=1",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        Ok(ConfigurationView {
            schema_version: 1,
            issues: validate(&draft),
            draft,
            etag,
            loaded: None,
            active,
            previous,
            used,
            phase: "stopped".into(),
        })
    }
    pub fn save_draft(
        &mut self,
        c: &Configuration,
        expected: &str,
    ) -> LocalResult<ConfigurationView> {
        if c.sources.iter().any(|s| {
            s.name
                .starts_with(crate::domain::yaml_migration::PRIVATE_NAME)
        }) {
            return Err("yaml_private_source".into());
        }
        let current = self.configuration()?;
        if current.etag != expected {
            return Err("draft_conflict".into());
        }
        for source in &c.sources {
            if source.sha256 != digest(&source.content) {
                return Err("source_hash_mismatch".into());
            }
            if current
                .draft
                .sources
                .iter()
                .any(|old| old.id == source.id && old != source)
            {
                return Err("source_identity_conflict".into());
            }
        }
        if current.draft == *c {
            return Ok(current);
        }
        let payload = encode(c)?;
        if payload.len() > 16 * 1024 * 1024 {
            return Err("configuration_limits".into());
        }
        let issues = encode(&validate(c))?;
        let tx = self.config.transaction().map_err(sql_error)?;
        let changed=tx.execute("UPDATE configuration_draft SET etag=?1,payload=?2,issues=?3 WHERE id=1 AND etag=?4",params![id(),payload,issues,expected]).map_err(sql_error)?;
        if changed != 1 {
            return Err("draft_conflict".into());
        }
        for src in &c.sources {
            let same_id: Option<(String, String)> = tx
                .query_row(
                    "SELECT sha256,content FROM source_documents WHERE id=?1",
                    [&src.id],
                    |r| Ok((r.get(0)?, r.get(1)?)),
                )
                .optional()
                .map_err(sql_error)?;
            if same_id
                .as_ref()
                .map(|(h, b)| h != &src.sha256 || b != &src.content)
                .unwrap_or(false)
            {
                return Err("source_identity_conflict".into());
            }
            let same_hash: Option<String> = tx
                .query_row(
                    "SELECT content FROM source_documents WHERE sha256=?1",
                    [&src.sha256],
                    |r| r.get(0),
                )
                .optional()
                .map_err(sql_error)?;
            match same_hash {
                Some(body) if body != src.content => return Err("source_hash_mismatch".into()),
                Some(_) => {} // Global content archive keeps its original id/name/diagnostics.
                None => {
                    tx.execute("INSERT INTO source_documents(id,sha256,name,content,diagnostics) VALUES(?1,?2,?3,?4,?5)",params![src.id,src.sha256,src.name,src.content,encode(&src.diagnostics)?]).map_err(sql_error)?;
                }
            }
        }
        tx.commit().map_err(sql_error)?;
        self.configuration()
    }
    pub fn revision(&self, id: &str) -> LocalResult<Configuration> {
        let (payload, hash): (String, String) = self
            .config
            .query_row(
                "SELECT payload,sha256 FROM configuration_revisions WHERE id=?1",
                [id],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        if digest(&payload) != hash {
            return Err("revision_corrupt".into());
        }
        serde_json::from_str(&payload).map_err(|_| "revision_corrupt".into())
    }
    pub fn prepare_activation(
        &mut self,
        expected_etag: &str,
        expected_active: Option<&str>,
        rollback: bool,
    ) -> LocalResult<(String, String)> {
        let view = self.configuration()?;
        if view.etag != expected_etag || view.active.as_deref() != expected_active {
            return Err("activation_conflict".into());
        }
        let c = if rollback {
            self.revision(view.previous.as_deref().ok_or("previous_missing")?)?
        } else {
            view.draft
        };
        if !validate(&c).is_empty() {
            return Err("configuration_invalid".into());
        }
        let payload = encode(&c)?;
        let cap = self.capacity(c.storage.quota_bytes)?;
        if cap.config_bytes.saturating_mul(2) + (payload.len() as u64) * 3 + 65536
            > 64 * 1024 * 1024
        {
            return Err("configuration_capacity".into());
        }
        let token = id();
        let revision = id();
        let tx = self.config.transaction().map_err(sql_error)?;
        let unfinished: i64 = tx
            .query_row(
                "SELECT count(*) FROM activation_intents WHERE phase!='applied'",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if unfinished != 0 {
            return Err("activation_pending".into());
        }
        tx.execute(
            "INSERT INTO configuration_revisions VALUES(?1,1,?2,?3,?4)",
            params![revision, digest(&payload), payload, now()],
        )
        .map_err(sql_error)?;
        tx.execute(
            "INSERT INTO activation_intents VALUES(?1,?2,?3,'prepared',?4)",
            params![token, view.active, revision, now()],
        )
        .map_err(sql_error)?;
        tx.commit().map_err(sql_error)?;
        Ok((token, revision))
    }
    pub fn prepare_context(&mut self, token: &str, revision: &str) -> LocalResult<()> {
        let c = self.revision(revision)?;
        let payload = encode(&c)?;
        let mut cap = self.capacity(c.storage.quota_bytes)?;
        cap.reserved_bytes = cap
            .reserved_bytes
            .saturating_add((payload.len() as u64).saturating_mul(3));
        if !super::capacity::admit(&cap, c.storage.quota_bytes, false) {
            return Err("capacity_paused".into());
        }
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let existing: Option<String> = tx
            .query_row(
                "SELECT sha256 FROM configuration_contexts WHERE revision=?1",
                [revision],
                |r| r.get(0),
            )
            .optional()
            .map_err(sql_error)?;
        if existing
            .as_deref()
            .map(|x| x != digest(&payload))
            .unwrap_or(false)
        {
            return Err("context_conflict".into());
        }
        tx.execute(
            "INSERT OR IGNORE INTO configuration_contexts VALUES(?1,1,?2,?3)",
            params![revision, digest(&payload), payload],
        )
        .map_err(sql_error)?;
        tx.execute(
            "INSERT OR IGNORE INTO activation_journal VALUES(?1,?2,'prepared')",
            params![token, revision],
        )
        .map_err(sql_error)?;
        for p in &c.plcs {
            tx.execute(
                "INSERT OR IGNORE INTO plc_sources VALUES(?1,?2,1)",
                params![p.id, id()],
            )
            .map_err(sql_error)?;
        }
        tx.commit().map_err(sql_error)
    }
    pub fn select_active(&mut self, token: &str, revision: &str) -> LocalResult<()> {
        let tx = self.config.transaction().map_err(sql_error)?;
        let(old,phase):(Option<String>,String)=tx.query_row("SELECT old_revision,phase FROM activation_intents WHERE token=?1 AND new_revision=?2",params![token,revision],|r|Ok((r.get(0)?,r.get(1)?))).map_err(sql_error)?;
        let active: Option<String> = tx
            .query_row("SELECT active FROM active_selection WHERE id=1", [], |r| {
                r.get(0)
            })
            .map_err(sql_error)?;
        if phase == "prepared" {
            if active != old {
                return Err("activation_conflict".into());
            }
            tx.execute(
                "UPDATE active_selection SET previous=active,active=?1 WHERE id=1",
                [revision],
            )
            .map_err(sql_error)?;
            tx.execute(
                "UPDATE activation_intents SET phase='selected' WHERE token=?1",
                [token],
            )
            .map_err(sql_error)?;
        } else if active.as_deref() != Some(revision) {
            return Err("activation_conflict".into());
        }
        tx.commit().map_err(sql_error)
    }
    pub fn finish_activation(&mut self, token: &str) -> LocalResult<()> {
        self.runtime
            .execute(
                "UPDATE activation_journal SET phase='applied' WHERE token=?1",
                [token],
            )
            .map_err(sql_error)?;
        self.config
            .execute(
                "UPDATE activation_intents SET phase='applied' WHERE token=?1",
                [token],
            )
            .map_err(sql_error)?;
        self.prune_config()?;
        Ok(())
    }
    pub fn recover_activation(&mut self) -> LocalResult<()> {
        let rows=self.config.prepare("SELECT token,new_revision FROM activation_intents WHERE phase!='applied' ORDER BY created_at,token").map_err(sql_error)?.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        if rows.len() > 1 {
            return Err("activation_corrupt".into());
        }
        for (t, r) in rows {
            self.prepare_context(&t, &r)?;
            self.select_active(&t, &r)?;
        }
        let active: Option<String> = self
            .config
            .query_row("SELECT active FROM active_selection WHERE id=1", [], |r| {
                r.get(0)
            })
            .map_err(sql_error)?;
        if let Some(a) = active {
            let c = self.revision(&a)?;
            let hash = digest(&encode(&c)?);
            let actual: String = self
                .runtime
                .query_row(
                    "SELECT sha256 FROM configuration_contexts WHERE revision=?1",
                    [a],
                    |r| r.get(0),
                )
                .map_err(sql_error)?;
            if actual != hash {
                return Err("context_mismatch".into());
            }
        }
        Ok(())
    }
    pub(super) fn prune_config(&mut self) -> LocalResult<()> {
        let view = self.configuration()?;
        let all = self
            .config
            .prepare("SELECT id FROM configuration_revisions ORDER BY created_at DESC,id DESC")
            .map_err(sql_error)?
            .query_map([], |r| r.get::<_, String>(0))
            .map_err(sql_error)?
            .collect::<Result<Vec<_>, _>>()
            .map_err(sql_error)?;
        for old in all.into_iter().skip(8) {
            if view.active.as_deref() == Some(&old) || view.previous.as_deref() == Some(&old) {
                continue;
            }
            let references:i64=self.config.query_row("SELECT count(*) FROM activation_intents WHERE new_revision=?1 AND phase!='applied'",[&old],|r|r.get(0)).map_err(sql_error)?;
            if references != 0 {
                continue;
            }
            let context: i64 = self
                .runtime
                .query_row(
                    "SELECT count(*) FROM configuration_contexts WHERE revision=?1",
                    [&old],
                    |r| r.get(0),
                )
                .map_err(sql_error)?;
            if context == 1 {
                self.config
                    .execute(
                        "DELETE FROM activation_intents WHERE new_revision=?1 AND phase='applied'",
                        [&old],
                    )
                    .map_err(sql_error)?;
                self.config
                    .execute("DELETE FROM configuration_revisions WHERE id=?1", [&old])
                    .map_err(sql_error)?;
            }
        }
        let mut hashes = std::collections::BTreeSet::new();
        for s in view.draft.sources {
            hashes.insert(s.sha256);
        }
        let rows = self
            .config
            .prepare("SELECT payload FROM configuration_revisions")
            .map_err(sql_error)?
            .query_map([], |r| r.get::<_, String>(0))
            .map_err(sql_error)?
            .collect::<Result<Vec<_>, _>>()
            .map_err(sql_error)?;
        for row in rows {
            let c: Configuration =
                serde_json::from_str(&row).map_err(|_| "configuration_corrupt")?;
            for s in c.sources {
                hashes.insert(s.sha256);
            }
        }
        let old = self
            .config
            .prepare("SELECT sha256 FROM source_documents WHERE substr(name,1,25) != '__daa_yaml_migration_v1__'")
            .map_err(sql_error)?
            .query_map([], |r| r.get::<_, String>(0))
            .map_err(sql_error)?
            .collect::<Result<Vec<_>, _>>()
            .map_err(sql_error)?;
        for h in old {
            if !hashes.contains(&h) {
                self.config
                    .execute("DELETE FROM source_documents WHERE sha256=?1", [h])
                    .map_err(sql_error)?;
            }
        }
        Ok(())
    }
}
