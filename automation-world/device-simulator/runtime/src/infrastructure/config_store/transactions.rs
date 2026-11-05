//! 草稿CAS、版本发布/批量删除与回退保留确认解除；同一事务复核引用，不迁移schema。
use super::{queries, RollbackRelease, SaveResult, Selection};
use crate::{
    domain::configuration::{self, digest, hash_bytes, uuid, Workspace},
    infrastructure::profile_lock::ProfileLock,
};
use rusqlite::{params, Connection};
pub fn save(
    c: &mut Connection,
    lock: &ProfileLock,
    expected: &str,
    w: Workspace,
) -> Result<SaveResult, String> {
    configuration::validate(&w)?;
    let payload = serde_json::to_vec(&w).map_err(|_| "configuration_format")?;
    lock.check_capacity(payload.len() * 3)?;
    let tx = c.transaction().map_err(|_| "storage_busy")?;
    let current = queries::load(&tx)?;
    if current.etag != expected {
        return Err(format!("etag_conflict:{}", current.etag));
    }
    if current.workspace == w {
        return Ok(SaveResult {
            result: "unchanged".into(),
            etag: current.etag,
            revision_id: current.latest_revision,
        });
    }
    for source in &w.source_versions {
        tx.execute(
            "INSERT OR IGNORE INTO source_blobs(sha256,utf8,byte_len) VALUES(?1,?2,?3)",
            params![source.blob_sha256, source.bytes, source.bytes.len() as i64],
        )
        .map_err(|_| "storage_source")?;
        let metadata = serde_json::to_vec(source).map_err(|_| "source_format")?;
        tx.execute("INSERT OR IGNORE INTO source_versions(version_id,lineage_id,blob_sha256,logical_name,import_profile,metadata) VALUES(?1,?2,?3,?4,?5,?6)",params![source.version_id,source.lineage_id,source.blob_sha256,source.logical_name,source.import_profile,metadata]).map_err(|_|"storage_source")?;
        let existing: Vec<u8> = tx
            .query_row(
                "SELECT metadata FROM source_versions WHERE version_id=?1",
                [&source.version_id],
                |r| r.get(0),
            )
            .map_err(|_| "storage_source")?;
        if existing != metadata {
            return Err("source_immutable".into());
        }
    }
    queries::validate_references(&tx, &w)?;
    for selected in queries::selections(&tx)? {
        if !w.instances.iter().any(|i| i.id == selected.instance_id) {
            tx.execute(
                "DELETE FROM instance_selection WHERE instance_id=?1",
                [selected.instance_id],
            )
            .map_err(|_| "storage_selection")?;
        }
    }
    let etag = uuid();
    let sha = hash_bytes(&payload);
    tx.execute("UPDATE configuration_draft SET etag=?1,canonical_payload=?2,sha256=?3,updated_utc=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE singleton=1 AND etag=?4",params![etag,payload,sha,expected]).map_err(|_|"storage_save")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("before_save_commit")?;
    tx.commit().map_err(|_| "save_commit_unknown")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("after_save_commit").map_err(|_| "save_receipt_unknown")?;
    Ok(SaveResult {
        result: "saved".into(),
        etag,
        revision_id: current.latest_revision,
    })
}

/// 版本快照仅在明确发布时插入；清理清单与发布在同一事务中提交。
/// latest永不允许删除，因此max(saved_seq)是既有schema下不可回退的版本高水位。
pub fn revise(
    c: &mut Connection,
    lock: &ProfileLock,
    expected: &str,
    publish: bool,
    remove: Vec<String>,
    runtime_protected: Vec<String>,
    releases: Vec<RollbackRelease>,
) -> Result<SaveResult, String> {
    lock.check_capacity(4096)?;
    let tx = c.transaction().map_err(|_| "storage_busy")?;
    let current = queries::load(&tx)?;
    if current.etag != expected {
        return Err(format!("etag_conflict:{}", current.etag));
    }
    let mut protected: std::collections::BTreeSet<_> = runtime_protected.into_iter().collect();
    if let Some(id) = &current.latest_revision {
        protected.insert(id.clone());
    }
    let selections = queries::selections(&tx)?;
    let mut released_instances = std::collections::BTreeSet::new();
    for release in &releases {
        if publish
            || !remove.contains(&release.revision_id)
            || !released_instances.insert(release.instance_id.clone())
        {
            return Err("revision_selection".into());
        }
        let selection = selections
            .iter()
            .find(|s| s.instance_id == release.instance_id)
            .ok_or("revision_preview_stale")?;
        if selection.selection_etag != release.selection_etag
            || selection.previous_revision_id.as_ref() != Some(&release.revision_id)
        {
            return Err("revision_preview_stale".into());
        }
    }
    for selection in &selections {
        protected.insert(selection.revision_id.clone());
        if !released_instances.contains(&selection.instance_id) {
            protected.extend(selection.previous_revision_id.clone());
        }
    }
    let unique: std::collections::BTreeSet<_> = remove.iter().collect();
    if unique.len() != remove.len() || (!publish && remove.is_empty()) {
        return Err("revision_selection".into());
    }
    for id in &remove {
        if protected.contains(id) {
            return Err("revision_protected".into());
        }
        queries::revision_seq(&tx, id)?;
    }
    let revision = if publish {
        if let Some(id) = &current.latest_revision {
            if queries::revision(&tx, id)? == current.workspace {
                if !remove.is_empty() {
                    return Err("revision_preview_stale".into());
                }
                return Ok(SaveResult {
                    result: "unchanged".into(),
                    etag: current.etag,
                    revision_id: Some(id.clone()),
                });
            }
        }
        queries::validate_references(&tx, &current.workspace)?;
        let payload = serde_json::to_vec(&current.workspace).map_err(|_| "configuration_format")?;
        lock.check_capacity(payload.len() * 2)?;
        let id = uuid();
        tx.execute("INSERT INTO configuration_revisions(revision_id,saved_seq,payload,sha256) SELECT ?1,coalesce(max(saved_seq),0)+1,?2,?3 FROM configuration_revisions",params![id,payload,hash_bytes(&payload)]).map_err(|_|"storage_save")?;
        Some(id)
    } else {
        current.latest_revision
    };
    // 回退标记与版本删除原子提交；不改当前selected、已加载image或运行值。
    for release in &releases {
        if tx.execute("UPDATE instance_selection SET previous_revision_id=NULL,selection_etag=?1 WHERE instance_id=?2 AND selection_etag=?3 AND previous_revision_id=?4",params![uuid(),release.instance_id,release.selection_etag,release.revision_id]).map_err(|_|"storage_selection")? != 1 {
            return Err("revision_preview_stale".into());
        }
    }
    for id in remove {
        if tx
            .execute(
                "DELETE FROM configuration_revisions WHERE revision_id=?1",
                [id],
            )
            .map_err(|_| "storage_revision")?
            != 1
        {
            return Err("revision_not_found".into());
        }
    }
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("before_save_commit")?;
    tx.commit().map_err(|_| "save_commit_unknown")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("after_save_commit").map_err(|_| "save_receipt_unknown")?;
    Ok(SaveResult {
        result: if publish { "published" } else { "deleted" }.into(),
        etag: current.etag,
        revision_id: revision,
    })
}
pub fn select(
    c: &mut Connection,
    lock: &ProfileLock,
    instance: &str,
    revision: &str,
    expected: Option<String>,
) -> Result<Selection, String> {
    lock.check_capacity(4096)?;
    let tx = c.transaction().map_err(|_| "storage_busy")?;
    let w = queries::revision(&tx, revision)?;
    let slice = w
        .instances
        .iter()
        .find(|i| i.id == instance)
        .ok_or("instance_not_found")?;
    let current: Option<Selection> = queries::selections(&tx)?
        .into_iter()
        .find(|s| s.instance_id == instance);
    if current.as_ref().map(|s| s.selection_etag.clone()) != expected {
        return Err("selection_conflict".into());
    }
    let selection = Selection {
        instance_id: instance.into(),
        revision_id: revision.into(),
        slice_sha256: digest(slice),
        previous_revision_id: current.and_then(|s| {
            if s.revision_id == revision {
                s.previous_revision_id
            } else {
                Some(s.revision_id)
            }
        }),
        selection_etag: uuid(),
    };
    tx.execute("INSERT INTO instance_selection(instance_id,revision_id,slice_sha256,previous_revision_id,selection_etag) VALUES(?1,?2,?3,?4,?5) ON CONFLICT(instance_id) DO UPDATE SET revision_id=excluded.revision_id,slice_sha256=excluded.slice_sha256,previous_revision_id=excluded.previous_revision_id,selection_etag=excluded.selection_etag",params![selection.instance_id,selection.revision_id,selection.slice_sha256,selection.previous_revision_id,selection.selection_etag]).map_err(|_|"storage_selection")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("before_select_commit")?;
    tx.commit().map_err(|_| "selection_commit_unknown")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("after_select_commit").map_err(|_| "selection_receipt_unknown")?;
    Ok(selection)
}
