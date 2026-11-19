//! 配置草稿CAS、不可变版本与可恢复跨库token；数据库逻辑只存在本适配层。
use super::{sql_error, Stores};
use crate::domain::{
    local_configuration::{
        id, validate_display_names, validate_for_runtime, Configuration, LocalResult,
    },
    local_runtime::{
        ConfigurationSnapshot, ConfigurationView, StartupSettings, STARTUP_PRIVATE_ID,
        STARTUP_PRIVATE_NAME,
    },
    local_sample::{digest, encode, now},
};
use rusqlite::{params, OptionalExtension};
fn collect_configuration_ids(c: &Configuration, out: &mut std::collections::BTreeSet<String>) {
    out.extend(c.plcs.iter().map(|v| v.id.clone()));
    out.extend(c.dbs.iter().map(|v| v.id.clone()));
    out.extend(c.points.iter().map(|v| v.id.clone()));
    out.extend(c.groups.iter().map(|v| v.id.clone()));
    out.extend(c.sources.iter().map(|v| v.id.clone()));
}

/// 只检查实际引用本地 PLC 的历史字段；sample/cycle/receipt 自身 ID 属于独立命名空间。
pub(super) fn runtime_local_identity_conflict(
    runtime: &rusqlite::Connection,
    ids: &std::collections::BTreeSet<String>,
) -> LocalResult<bool> {
    let version: u32 = runtime
        .query_row("PRAGMA user_version", [], |row| row.get(0))
        .map_err(sql_error)?;
    let ddl = match version {
        2 => super::schema::runtime_sql(),
        3 => super::schema::runtime_v3_sql(),
        4 => super::schema::runtime_v4_schema(runtime)?,
        _ => return Err("schema_structure_mismatch".into()),
    };
    super::schema::verify_structure(runtime, &ddl)?;
    let encoded = encode(ids)?;
    for (table, column, optional) in [
        ("plc_sources", "plc_id", false),
        ("collection_cycles", "plc_id", false),
        ("samples", "plc_id", false),
        ("reporting_bindings", "local_plc_id", true),
        ("reporting_generations", "local_plc_id", true),
        ("reporting_disabled", "local_plc_id", true),
    ] {
        let exists: bool = runtime
            .query_row(
                "SELECT EXISTS(SELECT 1 FROM sqlite_schema WHERE type='table' AND name=?1)",
                [table],
                |row| row.get(0),
            )
            .map_err(sql_error)?;
        if !exists && optional {
            continue;
        }
        if !exists {
            return Err("schema_structure_mismatch".into());
        }
        let query = format!("SELECT EXISTS(SELECT 1 FROM {table} WHERE {column} IN (SELECT value FROM json_each(?1)))");
        if runtime
            .query_row(&query, [&encoded], |row| row.get::<_, bool>(0))
            .map_err(sql_error)?
        {
            return Ok(true);
        }
    }
    Ok(false)
}

fn catalog_origin(
    c: &Configuration,
    plc_id: &str,
    instance: &str,
) -> LocalResult<crate::domain::plc_catalog::Origin> {
    use crate::domain::plc_catalog::{self, Origin};
    let mut origin = None;
    for binding in &c.catalog_bindings {
        let Some(db) = c
            .dbs
            .iter()
            .find(|d| d.id == binding.local_db_id && d.plc_id == plc_id)
        else {
            continue;
        };
        let source = c
            .sources
            .iter()
            .find(|s| s.id == db.source_id)
            .ok_or("catalog_source_invalid")?;
        let parsed = plc_catalog::parse(source.content.as_bytes())?.0.origin;
        if origin.as_ref().is_some_and(|old| old != &parsed) {
            return Err("catalog_origin_conflict".into());
        }
        origin = Some(parsed);
    }
    Ok(origin.unwrap_or_else(|| Origin {
        kind: "data_acquisition_agent".into(),
        profile_id: instance.into(),
        plc_id: plc_id.into(),
    }))
}
impl Stores {
    /// 复用配置库的受保护私有记录，避免改写草稿、活动版本或旧库 DDL。
    pub fn startup_settings(&self) -> LocalResult<StartupSettings> {
        let mut stmt = self.config.prepare(
            "SELECT id,name,content,sha256,diagnostics FROM source_documents WHERE id=?1 OR name=?2 LIMIT 2",
        ).map_err(sql_error)?;
        let rows = stmt
            .query_map(params![STARTUP_PRIVATE_ID, STARTUP_PRIVATE_NAME], |r| {
                Ok((
                    r.get::<_, String>(0)?,
                    r.get::<_, String>(1)?,
                    r.get::<_, String>(2)?,
                    r.get::<_, String>(3)?,
                    r.get::<_, String>(4)?,
                ))
            })
            .map_err(sql_error)?
            .collect::<Result<Vec<_>, _>>()
            .map_err(sql_error)?;
        if rows.is_empty() {
            return Ok(StartupSettings::default());
        }
        if rows.len() != 1 {
            return Err("startup_settings_corrupt".into());
        }
        let (id, name, content, sha, diagnostics) = &rows[0];
        if id != STARTUP_PRIVATE_ID
            || name != STARTUP_PRIVATE_NAME
            || *sha != digest(content)
            || diagnostics != "[]"
        {
            return Err("startup_settings_corrupt".into());
        }
        let settings: StartupSettings =
            serde_json::from_str(content).map_err(|_| "startup_settings_corrupt")?;
        if settings.schema_version != 1 {
            return Err("startup_settings_corrupt".into());
        }
        Ok(settings)
    }
    pub fn save_startup_settings(
        &mut self,
        settings: StartupSettings,
    ) -> LocalResult<StartupSettings> {
        if settings.schema_version != 1 {
            return Err("invalid_request".into());
        }
        self.startup_settings()?;
        if settings.auto_report && self.runtime_version()? != 4 {
            return Err("delivery_profile_upgrade_required".into());
        }
        let raw = encode(&settings)?;
        let tx = self.config.transaction().map_err(sql_error)?;
        tx.execute("INSERT INTO source_documents(id,name,content,sha256,diagnostics) VALUES(?1,?2,?3,?4,'[]') ON CONFLICT(id) DO UPDATE SET content=excluded.content,sha256=excluded.sha256 WHERE name=excluded.name",
            params![STARTUP_PRIVATE_ID, STARTUP_PRIVATE_NAME, raw, digest(&raw)]).map_err(sql_error)?;
        tx.commit().map_err(sql_error)?;
        Ok(settings)
    }
    pub fn runtime_version(&self) -> LocalResult<u32> {
        self.runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)
    }
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
        validate_display_names(&draft).map_err(|_| "configuration_corrupt")?;
        self.verify_catalog_archives(&draft)?;
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
            issues: validate_for_runtime(&draft, self.runtime_version()?),
            draft,
            etag,
            loaded: None,
            active,
            previous,
            used,
            phase: "stopped".into(),
            imported_local_plc_id: None,
        })
    }
    /// 读取持久 payload 原字节计算摘要，不从内存草稿重新序列化。
    pub fn catalog_export_snapshot(&self, state: &str) -> LocalResult<ConfigurationSnapshot> {
        let view = self.configuration()?;
        let (revision, payload, configuration) = match state {
            "saved_draft" => {
                let (etag, raw): (String, String) = self
                    .config
                    .query_row(
                        "SELECT etag,payload FROM configuration_draft WHERE id=1",
                        [],
                        |r| Ok((r.get(0)?, r.get(1)?)),
                    )
                    .map_err(sql_error)?;
                if etag != view.etag {
                    return Err("draft_conflict".into());
                }
                (etag, raw, view.draft.clone())
            }
            "active_revision" => {
                let revision = view.active.clone().ok_or("active_missing")?;
                let raw: String = self
                    .config
                    .query_row(
                        "SELECT payload FROM configuration_revisions WHERE id=?1",
                        [&revision],
                        |r| r.get(0),
                    )
                    .map_err(sql_error)?;
                let configuration = self.revision(&revision)?;
                (revision, raw, configuration)
            }
            _ => return Err("invalid_request".into()),
        };
        Ok(ConfigurationSnapshot {
            state: state.into(),
            revision,
            payload_sha256: digest(&payload),
            configuration,
            instance: self.instance.clone(),
            active: view.active,
            used: view.used,
        })
    }
    fn verify_catalog_archives(&self, c: &Configuration) -> LocalResult<()> {
        crate::domain::plc_catalog::verify_bindings(c).map_err(|_| "catalog_binding_invalid")?;
        for binding in &c.catalog_bindings {
            let source = c
                .sources
                .iter()
                .find(|s| s.id == binding.source_id)
                .ok_or("catalog_source_invalid")?;
            let archived: Option<String> = self
                .config
                .query_row(
                    "SELECT content FROM source_documents WHERE sha256=?1",
                    [&source.sha256],
                    |r| r.get(0),
                )
                .optional()
                .map_err(sql_error)?;
            if archived.as_deref() != Some(source.content.as_str()) {
                return Err("catalog_source_invalid".into());
            }
        }
        Ok(())
    }
    /// 检查当前版本与被保留的历史；不以文件名、地址或显示名称推断来源身份。
    pub fn catalog_history(
        &self,
        catalog: &crate::domain::plc_catalog::Catalog,
        target: &crate::domain::plc_catalog::Connection,
        loaded: Option<&Configuration>,
    ) -> LocalResult<bool> {
        Ok(self.catalog_inventory(catalog, target, loaded)?.0)
    }

    fn catalog_inventory(
        &self,
        catalog: &crate::domain::plc_catalog::Catalog,
        target: &crate::domain::plc_catalog::Connection,
        loaded: Option<&Configuration>,
    ) -> LocalResult<(bool, std::collections::BTreeSet<String>)> {
        use std::collections::BTreeSet;
        let current = self.configuration()?;
        let mut occupied = BTreeSet::from([self.instance.clone(), current.etag.clone()]);
        let mut active = vec![current.draft.clone()];
        if let Some(revision) = &current.active {
            active.push(self.revision(revision)?);
        }
        if let Some(configuration) = loaded {
            active.push(configuration.clone());
        }
        let target_endpoint = format!(
            "{}:{}:{}/{}",
            target.host, target.port, target.rack, target.slot
        );
        for c in &active {
            collect_configuration_ids(c, &mut occupied);
            for plc in &c.plcs {
                if catalog_origin(c, &plc.id, &self.instance)? == catalog.origin {
                    return Err("catalog_origin_conflict".into());
                }
                if plc.endpoint() == target_endpoint {
                    return Err("duplicate_endpoint".into());
                }
            }
        }
        let external_ids: BTreeSet<_> = std::iter::once(catalog.origin.plc_id.clone())
            .chain(catalog.dbs.iter().map(|db| db.id.clone()))
            .chain(
                catalog
                    .dbs
                    .iter()
                    .flat_map(|db| db.points.iter().map(|point| point.id.clone())),
            )
            .collect();
        if external_ids.iter().any(|id| occupied.contains(id)) {
            return Err("catalog_identity_conflict".into());
        }
        let mut historical = false;
        for (connection, table, key) in [
            (&self.config, "configuration_revisions", "id"),
            (&self.runtime, "configuration_contexts", "revision"),
        ] {
            let mut stmt = connection
                .prepare(&format!("SELECT {key},payload,sha256 FROM {table}"))
                .map_err(sql_error)?;
            let mut rows = stmt.query([]).map_err(sql_error)?;
            while let Some(row) = rows.next().map_err(sql_error)? {
                let old_id: String = row.get(0).map_err(sql_error)?;
                let raw: String = row.get(1).map_err(sql_error)?;
                let hash: String = row.get(2).map_err(sql_error)?;
                if digest(&raw) != hash {
                    return Err("configuration_corrupt".into());
                }
                let old: Configuration =
                    serde_json::from_str(&raw).map_err(|_| "configuration_corrupt")?;
                crate::domain::plc_catalog::verify_bindings(&old)
                    .map_err(|_| "configuration_corrupt")?;
                self.verify_catalog_archives(&old)?;
                occupied.insert(old_id);
                collect_configuration_ids(&old, &mut occupied);
                for plc in &old.plcs {
                    if catalog_origin(&old, &plc.id, &self.instance)? == catalog.origin {
                        historical = true;
                    }
                }
            }
        }
        let mut stmt = self
            .config
            .prepare("SELECT id,sha256,content FROM source_documents")
            .map_err(sql_error)?;
        let mut rows = stmt.query([]).map_err(sql_error)?;
        while let Some(row) = rows.next().map_err(sql_error)? {
            let old_id: String = row.get(0).map_err(sql_error)?;
            let old_sha: String = row.get(1).map_err(sql_error)?;
            let content: String = row.get(2).map_err(sql_error)?;
            occupied.insert(old_id);
            if old_sha == digest(&content) {
                if let Ok((old, _, _)) = crate::domain::plc_catalog::parse(content.as_bytes()) {
                    if old.origin == catalog.origin {
                        historical = true;
                    }
                }
            }
        }
        let mut stmt = self
            .runtime
            .prepare("SELECT plc_id,generation FROM plc_sources")
            .map_err(sql_error)?;
        let rows = stmt
            .query_map([], |row| {
                Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
            })
            .map_err(sql_error)?;
        for row in rows {
            let (plc, generation) = row.map_err(sql_error)?;
            occupied.insert(plc);
            occupied.insert(generation);
        }
        Ok((historical, occupied))
    }

    /// 在串行存储任务中重新检查预览身份，然后由调用方进行草稿 CAS。
    pub fn ensure_catalog_new(
        &self,
        source: &crate::domain::local_configuration::SourceDocument,
        candidate: &Configuration,
        loaded: Option<&Configuration>,
    ) -> LocalResult<()> {
        let (catalog, _, sha) = crate::domain::plc_catalog::parse(source.content.as_bytes())?;
        if sha != source.sha256 {
            return Err("catalog_source_invalid".into());
        }
        let plc = candidate
            .plcs
            .iter()
            .find(|p| p.id == source.plc_id)
            .ok_or("catalog_source_invalid")?;
        let target = crate::domain::plc_catalog::Connection {
            host: plc.host.clone(),
            port: plc.port,
            rack: plc.rack,
            slot: plc.slot,
            local_tsap: None,
            remote_tsap: None,
        };
        let (historical, occupied) = self.catalog_inventory(&catalog, &target, loaded)?;
        let remapped = source.plc_id != catalog.origin.plc_id;
        if historical != remapped {
            return Err(if historical {
                "catalog_history_choice_required"
            } else {
                "catalog_identity_conflict"
            }
            .into());
        }
        let mut local =
            std::collections::BTreeSet::from([source.id.clone(), source.plc_id.clone()]);
        for binding in candidate
            .catalog_bindings
            .iter()
            .filter(|b| b.source_id == source.id)
        {
            local.insert(binding.local_db_id.clone());
            local.extend(
                binding
                    .point_mappings
                    .iter()
                    .map(|mapping| mapping.local_point_id.clone()),
            );
        }
        if local.iter().any(|id| occupied.contains(id))
            || runtime_local_identity_conflict(&self.runtime, &local)?
        {
            return Err("catalog_identity_conflict".into());
        }
        let archived: Option<String> = self
            .config
            .query_row(
                "SELECT content FROM source_documents WHERE sha256=?1",
                [&sha],
                |r| r.get(0),
            )
            .optional()
            .map_err(sql_error)?;
        if archived.as_ref().is_some_and(|old| old != &source.content) {
            return Err("catalog_source_invalid".into());
        }
        Ok(())
    }
    pub fn save_draft(
        &mut self,
        c: &Configuration,
        expected: &str,
    ) -> LocalResult<ConfigurationView> {
        validate_display_names(c)?;
        if c.sources.iter().any(|s| {
            s.name
                .starts_with(crate::domain::yaml_migration::PRIVATE_NAME)
                || s.name.starts_with(STARTUP_PRIVATE_NAME)
                || s.id == STARTUP_PRIVATE_ID
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
        let issues = encode(&validate_for_runtime(c, self.runtime_version()?))?;
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
        let c: Configuration = serde_json::from_str(&payload).map_err(|_| "revision_corrupt")?;
        validate_display_names(&c).map_err(|_| "revision_corrupt")?;
        self.verify_catalog_archives(&c)?;
        Ok(c)
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
        if !validate_for_runtime(&c, self.runtime_version()?).is_empty() {
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
        // 样本仍引用 runtime context 时，其来源归档不能因配置版本被裁剪而消失。
        for (connection, table) in [
            (&self.config, "configuration_revisions"),
            (&self.runtime, "configuration_contexts"),
        ] {
            let mut statement = connection
                .prepare(&format!("SELECT payload,sha256 FROM {table}"))
                .map_err(sql_error)?;
            let mut rows = statement.query([]).map_err(sql_error)?;
            while let Some(row) = rows.next().map_err(sql_error)? {
                let payload: String = row.get(0).map_err(sql_error)?;
                let sha: String = row.get(1).map_err(sql_error)?;
                if digest(&payload) != sha {
                    return Err("configuration_corrupt".into());
                }
                let c: Configuration =
                    serde_json::from_str(&payload).map_err(|_| "configuration_corrupt")?;
                for s in c.sources {
                    hashes.insert(s.sha256);
                }
            }
        }
        let old = self
            .config
            .prepare("SELECT sha256 FROM source_documents WHERE substr(name,1,25) != '__daa_yaml_migration_v1__' AND id != ?1")
            .map_err(sql_error)?
            .query_map([STARTUP_PRIVATE_ID], |r| r.get::<_, String>(0))
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
