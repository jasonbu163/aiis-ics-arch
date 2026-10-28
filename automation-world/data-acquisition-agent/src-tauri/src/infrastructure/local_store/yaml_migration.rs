//! 迁入局部repository：只用现有v1表，草稿/来源/私有receipt短事务与CAS，不改DDL。
use super::{sql_error, Stores};
use crate::domain::{
    local_configuration::*,
    local_sample::{digest, encode},
    yaml_migration::*,
};
use rusqlite::Connection;
#[cfg(test)]
use {crate::domain::local_sample::now, rusqlite::params};
fn config_empty(c: &Connection) -> LocalResult<bool> {
    let payload: String = c
        .query_row(
            "SELECT payload FROM configuration_draft WHERE id=1",
            [],
            |r| r.get(0),
        )
        .map_err(sql_error)?;
    let draft: Configuration =
        serde_json::from_str(&payload).map_err(|_| "configuration_corrupt")?;
    if draft != Configuration::default() {
        return Ok(false);
    }
    for sql in ["SELECT count(*) FROM configuration_revisions","SELECT count(*) FROM activation_intents","SELECT count(*) FROM active_selection WHERE active IS NOT NULL OR previous IS NOT NULL","SELECT count(*) FROM source_documents WHERE substr(name,1,25) != '__daa_yaml_migration_v1__'"] {
        let n:i64=c.query_row(sql,[],|r|r.get(0)).map_err(sql_error)?;if n!=0{return Ok(false);}
    }
    Ok(true)
}
fn runtime_empty(c: &Connection) -> LocalResult<bool> {
    for sql in [
        "SELECT count(*) FROM plc_sources",
        "SELECT count(*) FROM configuration_contexts",
        "SELECT count(*) FROM activation_journal",
        "SELECT count(*) FROM collection_cycles",
        "SELECT count(*) FROM samples",
        "SELECT count(*) FROM sample_delivery",
        "SELECT count(*) FROM sample_references",
        "SELECT count(*) FROM runtime_metadata WHERE used_revision IS NOT NULL",
    ] {
        let n: i64 = c.query_row(sql, [], |r| r.get(0)).map_err(sql_error)?;
        if n != 0 {
            return Ok(false);
        }
    }
    Ok(true)
}
fn receipt(c: &Connection) -> LocalResult<Option<(String, Receipt)>> {
    let mut stmt=c.prepare("SELECT id,sha256,content,name FROM source_documents WHERE substr(name,1,25) = '__daa_yaml_migration_v1__'").map_err(sql_error)?;
    let rows = stmt
        .query_map([], |r| {
            Ok((
                r.get::<_, String>(0)?,
                r.get::<_, String>(1)?,
                r.get::<_, String>(2)?,
                r.get::<_, String>(3)?,
            ))
        })
        .map_err(sql_error)?
        .collect::<Result<Vec<_>, _>>()
        .map_err(sql_error)?;
    if rows.len() > 1 {
        return Err("yaml_receipt_conflict".into());
    }
    let Some((id, hash, content, name)) = rows.into_iter().next() else {
        return Ok(None);
    };
    if !valid_id(&id)
        || name != PRIVATE_NAME
        || content.len() > RECEIPT_LIMIT
        || digest(&content) != hash
    {
        return Err("yaml_receipt_corrupt".into());
    }
    let r: Receipt = serde_json::from_str(&content).map_err(|_| "yaml_receipt_corrupt")?;
    if r.yaml_migration_version != 1
        || encode(&r)? != content
        || r.summary.diagnostics.len() > 200
        || r.summary.sources.len() > 2
        || r.summary.attempt_id.as_deref().map(valid_id) != Some(true)
        || !matches!(
            r.summary.status.as_str(),
            "imported"
                | "imported_with_diagnostics"
                | "archived_policy_only"
                | "skipped_empty"
                | "failed"
        )
    {
        return Err("yaml_receipt_corrupt".into());
    }
    if encode(&r.summary)?.len() > 256 * 1024
        || r.summary.diagnostic_total < r.summary.diagnostics.len()
        || r.summary.diagnostic_omitted != r.summary.diagnostic_total - r.summary.diagnostics.len()
        || r.summary
            .diagnostics
            .iter()
            .any(|d| d.code.len() > 100 || d.path.len() > 512 || d.file.len() > 4096)
        || r.ids.len() > 20000
        || r.ids
            .iter()
            .any(|(path, id)| path.len() > 512 || !valid_id(id))
    {
        return Err("yaml_receipt_corrupt".into());
    }
    Ok(Some((id, r)))
}
impl Stores {
    #[cfg(test)]
    pub(crate) fn yaml_test_prune(&mut self) -> LocalResult<()> {
        self.prune_config()
    }
    pub fn yaml_empty(&self) -> LocalResult<bool> {
        Ok(config_empty(&self.config)? && runtime_empty(&self.runtime)?)
    }
    pub fn yaml_receipt(&self) -> LocalResult<Option<Receipt>> {
        Ok(receipt(&self.config)?.map(|(_, r)| r))
    }
    pub fn yaml_summary(&self) -> LocalResult<MigrationSummary> {
        let r = self.yaml_receipt()?;
        let empty = self.yaml_empty()?;
        if let Some(r) = r {
            let mut summary = r.summary;
            summary.retry_allowed = false;
            #[cfg(test)]
            {
                summary.retry_allowed = empty && retryable(&summary.status);
            }
            return Ok(summary);
        }
        Ok(MigrationSummary::state(if empty {
            "not_attempted"
        } else {
            "existing_sqlite_preserved"
        }))
    }
    #[cfg(test)]
    pub fn commit_yaml(
        &mut self,
        mut candidate: Candidate,
        expected: &str,
        attempt: Option<&str>,
    ) -> LocalResult<MigrationSummary> {
        self.log.health()?;
        let new_etag = id();
        candidate.receipt.summary.committed_etag = Some(new_etag.clone());
        candidate.receipt.summary.committed_at = Some(now());
        candidate.receipt.summary.status_persistence = "persisted".into();
        let payload = encode(&candidate.configuration)?;
        let content = encode(&candidate.receipt)?;
        if payload.len() > 16 * 1024 * 1024 || content.len() > RECEIPT_LIMIT {
            return Err("yaml_receipt_limit".into());
        }
        let cap = self.capacity(candidate.configuration.storage.quota_bytes)?;
        let growth = (payload.len() + content.len()) as u64 * 3 + 65536;
        if cap
            .config_bytes
            .saturating_mul(2)
            .saturating_add(cap.config_journal_bytes)
            .saturating_add(growth)
            > 64 * 1024 * 1024
            || !super::capacity::admit(&cap, candidate.configuration.storage.quota_bytes, false)
            || cap.free_bytes.saturating_sub(growth)
                < 512 * 1024 * 1024
                    + cap.reserved_bytes
                    + 2 * (cap.config_bytes + cap.config_journal_bytes)
                    + 96 * 1024 * 1024
        {
            return Err("configuration_capacity".into());
        }
        let tx = self
            .config
            .transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)
            .map_err(sql_error)?;
        let etag: String = tx
            .query_row("SELECT etag FROM configuration_draft WHERE id=1", [], |r| {
                r.get(0)
            })
            .map_err(sql_error)?;
        if etag != expected {
            return Err("draft_conflict".into());
        }
        let prior = receipt(&tx)?;
        if prior
            .as_ref()
            .and_then(|(_, r)| r.summary.attempt_id.as_deref())
            != attempt
        {
            return Err("yaml_attempt_conflict".into());
        }
        if prior
            .as_ref()
            .map(|(_, r)| !retryable(&r.summary.status))
            .unwrap_or(false)
        {
            return Err("yaml_retry_forbidden".into());
        }
        if !config_empty(&tx)? || !runtime_empty(&self.runtime)? {
            return Err("yaml_existing_sqlite".into());
        }
        for src in &candidate.configuration.sources {
            if src.name.starts_with(PRIVATE_NAME) {
                return Err("yaml_private_source".into());
            }
            tx.execute("INSERT INTO source_documents(id,sha256,name,content,diagnostics) VALUES(?1,?2,?3,?4,?5)",params![src.id,src.sha256,src.name,src.content,encode(&src.diagnostics)?]).map_err(|_|"yaml_source_hash_conflict")?;
        }
        let rowid = prior.as_ref().map(|(id, _)| id.clone()).unwrap_or_else(id);
        if prior.is_some() {
            tx.execute("DELETE FROM source_documents WHERE id=?1", [&rowid])
                .map_err(sql_error)?;
        }
        tx.execute("INSERT INTO source_documents(id,sha256,name,content,diagnostics) VALUES(?1,?2,?3,?4,'[]')",params![rowid,digest(&content),PRIVATE_NAME,content]).map_err(|_|"yaml_source_hash_conflict")?;
        let changed=tx.execute("UPDATE configuration_draft SET etag=?1,payload=?2,issues=?3 WHERE id=1 AND etag=?4",params![new_etag,payload,encode(&validate(&candidate.configuration))?,expected]).map_err(sql_error)?;
        if changed != 1 {
            return Err("draft_conflict".into());
        }
        #[cfg(test)]
        super::super::yaml_migration::tests::commit_boundary(&tx, "before");
        tx.commit().map_err(sql_error)?;
        #[cfg(test)]
        super::super::yaml_migration::tests::after_commit_boundary();
        Ok(candidate.receipt.summary)
    }
}
