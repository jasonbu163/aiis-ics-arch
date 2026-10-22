//! 原子草稿CAS、不可变来源/revision及selected CAS；不持有image锁。
use super::{queries, SaveResult, Selection};
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
    let revision = uuid();
    let sha = hash_bytes(&payload);
    tx.execute("UPDATE configuration_draft SET etag=?1,canonical_payload=?2,sha256=?3,updated_utc=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE singleton=1 AND etag=?4",params![etag,payload,sha,expected]).map_err(|_|"storage_save")?;
    tx.execute("INSERT INTO configuration_revisions(revision_id,saved_seq,payload,sha256) SELECT ?1,coalesce(max(saved_seq),0)+1,?2,?3 FROM configuration_revisions",params![revision,payload,sha]).map_err(|_|"storage_save")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("before_save_commit")?;
    tx.commit().map_err(|_| "save_commit_unknown")?;
    #[cfg(feature = "test-automation")]
    super::test_checkpoint("after_save_commit").map_err(|_| "save_receipt_unknown")?;
    Ok(SaveResult {
        result: "saved".into(),
        etag,
        revision_id: Some(revision),
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
        previous_revision_id: current.map(|s| s.revision_id),
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
