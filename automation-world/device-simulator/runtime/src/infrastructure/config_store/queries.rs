//! 固定SQL查询；调用方不能传入SQL或文件路径。
use super::{Selection, Snapshot};
use crate::domain::configuration::{self, Workspace};
use rusqlite::{Connection, OptionalExtension};
pub fn decode(payload: Vec<u8>, sha: String) -> Result<Workspace, String> {
    if payload.len() > 16 * 1024 * 1024 || configuration::hash_bytes(&payload) != sha {
        return Err("storage_payload_hash".into());
    }
    let workspace: Workspace = serde_json::from_slice(&payload).map_err(|_| "storage_payload")?;
    configuration::validate(&workspace)?;
    Ok(workspace)
}
pub fn load(c: &Connection) -> Result<Snapshot, String> {
    let (etag, payload, sha): (String, Vec<u8>, String) = c
        .query_row(
            "SELECT etag,canonical_payload,sha256 FROM configuration_draft WHERE singleton=1",
            [],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .map_err(|_| "storage_draft")?;
    if uuid::Uuid::parse_str(&etag).is_err() {
        return Err("storage_identity".into());
    }
    let latest = c
        .query_row(
            "SELECT revision_id FROM configuration_revisions ORDER BY saved_seq DESC LIMIT 1",
            [],
            |r| r.get(0),
        )
        .optional()
        .map_err(|_| "storage_revision")?;
    Ok(Snapshot {
        etag,
        workspace: decode(payload, sha)?,
        latest_revision: latest,
    })
}
pub fn revision(c: &Connection, id: &str) -> Result<Workspace, String> {
    let (payload, sha): (Vec<u8>, String) = c
        .query_row(
            "SELECT payload,sha256 FROM configuration_revisions WHERE revision_id=?1",
            [id],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .map_err(|_| "revision_not_found")?;
    let workspace = decode(payload, sha)?;
    validate_references(c, &workspace)?;
    Ok(workspace)
}
pub fn selections(c: &Connection) -> Result<Vec<Selection>, String> {
    let mut q=c.prepare("SELECT instance_id,revision_id,slice_sha256,previous_revision_id,selection_etag FROM instance_selection ORDER BY instance_id LIMIT 9").map_err(|_|"storage_reference")?;
    let rows = q
        .query_map([], |r| {
            Ok(Selection {
                instance_id: r.get(0)?,
                revision_id: r.get(1)?,
                slice_sha256: r.get(2)?,
                previous_revision_id: r.get(3)?,
                selection_etag: r.get(4)?,
            })
        })
        .map_err(|_| "storage_reference")?;
    let out: Vec<_> = rows
        .collect::<Result<_, _>>()
        .map_err(|_| "storage_reference")?;
    if out.len() > 8 {
        return Err("storage_reference".into());
    }
    Ok(out)
}
pub fn validate_references(c: &Connection, w: &Workspace) -> Result<(), String> {
    for source in &w.source_versions {
        let row:Option<(String,Vec<u8>,i64,String)>=c.query_row("SELECT v.lineage_id,b.utf8,b.byte_len,v.blob_sha256 FROM source_versions v JOIN source_blobs b ON v.blob_sha256=b.sha256 WHERE v.version_id=?1",[&source.version_id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).optional().map_err(|_|"storage_reference")?;
        let Some((lineage, bytes, len, hash)) = row else {
            return Err("storage_reference".into());
        };
        if lineage != source.lineage_id
            || bytes != source.bytes
            || len != bytes.len() as i64
            || hash != source.blob_sha256
            || configuration::hash_bytes(&bytes) != hash
        {
            return Err("storage_reference".into());
        }
    }
    for binding in w
        .instances
        .iter()
        .flat_map(|i| &i.dbs)
        .filter_map(|d| d.binding.as_ref())
    {
        for reference in std::iter::once(&binding.declaration).chain(binding.udt_closure.iter()) {
            if !w
                .source_versions
                .iter()
                .any(|s| s.version_id == reference.version_id)
            {
                return Err("source_reference".into());
            }
        }
    }
    Ok(())
}

pub fn revisions(c: &Connection, offset: u32) -> Result<Vec<super::RevisionInfo>, String> {
    let mut q=c.prepare("SELECT revision_id,saved_seq,sha256,created_utc FROM configuration_revisions ORDER BY saved_seq DESC LIMIT 100 OFFSET ?1").map_err(|_|"storage_revision")?;
    let rows = q
        .query_map([offset], |r| {
            Ok(super::RevisionInfo {
                revision_id: r.get(0)?,
                saved_seq: r.get::<_, i64>(1)?.to_string(),
                sha256: r.get(2)?,
                created_utc: r.get(3)?,
            })
        })
        .map_err(|_| "storage_revision")?;
    rows.collect::<Result<Vec<_>, _>>()
        .map_err(|_| "storage_revision".into())
}
pub fn revision_seq(c: &Connection, id: &str) -> Result<u64, String> {
    c.query_row(
        "SELECT saved_seq FROM configuration_revisions WHERE revision_id=?1",
        [id],
        |r| r.get::<_, u64>(0),
    )
    .map_err(|_| "revision_not_found".into())
}
