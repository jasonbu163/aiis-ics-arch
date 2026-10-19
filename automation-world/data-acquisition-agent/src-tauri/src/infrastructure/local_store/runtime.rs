//! 全轮事实、源序号、manifest和pending同事务提交；有界历史只返回原持久字节。
use super::{sql_error, Stores};
use crate::domain::{
    local_configuration::{id, LocalResult},
    local_runtime::HistoryQuery,
    local_sample::*,
};
use rusqlite::{params, OptionalExtension};
use serde_json::{json, Value};
impl Stores {
    pub fn commit_cycle(&mut self, input: CycleInput) -> LocalResult<Value> {
        let mut capacity = self.capacity(1024 * 1024 * 1024)?;
        let c = self.revision(&input.revision)?;
        capacity.quota_bytes = c.storage.quota_bytes;
        if !super::capacity::admit(&capacity, c.storage.quota_bytes, false) {
            return Err("capacity_paused".into());
        }
        let context: String = self
            .runtime
            .query_row(
                "SELECT sha256 FROM configuration_contexts WHERE revision=?1",
                [&input.revision],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if context != digest(&encode(&c)?) {
            return Err("context_mismatch".into());
        }
        let expected: Vec<_> = c
            .points
            .iter()
            .filter(|p| {
                p.enabled
                    && p.plc_id == input.plc_id
                    && p.group_id.as_deref() == Some(&input.group_id)
            })
            .map(|p| p.id.clone())
            .collect();
        let mut actual: Vec<_> = input
            .points
            .values()
            .flat_map(|p| p.keys().cloned())
            .collect();
        actual.sort();
        let mut sorted = expected.clone();
        sorted.sort();
        if sorted != actual || actual.is_empty() {
            return Err("cycle_membership".into());
        }
        let tx = self
            .runtime
            .transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)
            .map_err(sql_error)?;
        let (generation, seq): (String, i64) = tx
            .query_row(
                "SELECT generation,next_seq FROM plc_sources WHERE plc_id=?1",
                [&input.plc_id],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        if seq >= i64::MAX - 1 {
            return Err("sequence_exhausted".into());
        }
        let cycle = cycle_id();
        let saved: String = tx
            .query_row("SELECT strftime('%Y-%m-%dT%H:%M:%fZ','now')", [], |r| {
                r.get(0)
            })
            .map_err(sql_error)?;
        let mut packages = vec![];
        for (db, points) in &input.points {
            let sample = SamplePayload {
                schema_version: 1,
                sample_id: id(),
                cycle_id: cycle.clone(),
                instance_id: self.instance.clone(),
                plc_id: input.plc_id.clone(),
                source_generation: generation.clone(),
                source_seq: seq.to_string(),
                group_id: input.group_id.clone(),
                revision: input.revision.clone(),
                db_number: *db,
                origin: input.origin.clone(),
                started_at: input.started_at.clone(),
                finished_at: input.finished_at.clone(),
                saved_at: saved.clone(),
                points: points.clone(),
            };
            let raw = encode(&sample)?;
            let hash = digest(&raw);
            packages.push((sample, raw, hash));
        }
        let manifest = CycleManifest {
            schema_version: 1,
            cycle_id: cycle.clone(),
            plc_id: input.plc_id.clone(),
            source_generation: generation.clone(),
            source_seq: seq.to_string(),
            group_id: input.group_id.clone(),
            revision: input.revision.clone(),
            started_at: input.started_at.clone(),
            finished_at: input.finished_at.clone(),
            saved_at: saved.clone(),
            expected_point_ids: sorted,
            samples: packages
                .iter()
                .map(|(s, _, h)| ManifestSample {
                    sample_id: s.sample_id.clone(),
                    db_number: s.db_number,
                    sha256: h.clone(),
                })
                .collect(),
            reads: input.reads,
        };
        let raw_manifest = encode(&manifest)?;
        if raw_manifest.len() + packages.iter().map(|(_, p, _)| p.len()).sum::<usize>() > 512 * 1024
        {
            return Err("encoding_budget".into());
        }
        let quality = if input
            .points
            .values()
            .flat_map(|ps| ps.values())
            .all(|p| p.quality == "good")
        {
            "good"
        } else if input
            .points
            .values()
            .flat_map(|ps| ps.values())
            .any(|p| p.quality == "good")
        {
            "partial"
        } else {
            "bad"
        };
        tx.execute(
            "INSERT INTO collection_cycles VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13)",
            params![
                cycle,
                input.plc_id,
                generation,
                seq,
                input.group_id,
                input.revision,
                input.started_at,
                input.finished_at,
                saved,
                quality,
                raw_manifest,
                digest(&raw_manifest),
                packages.len() as i64
            ],
        )
        .map_err(sql_error)?;
        for (s, raw, hash) in packages {
            tx.execute("INSERT INTO samples(id,cycle_id,db_number,plc_id,group_id,source_seq,revision,quality,saved_at,schema_version,payload,sha256,payload_bytes) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,1,?10,?11,?12)",params![s.sample_id,cycle,s.db_number,s.plc_id,s.group_id,seq,s.revision,quality,saved,raw,hash,raw.len() as i64]).map_err(sql_error)?;
            tx.execute(
                "INSERT INTO sample_delivery VALUES(?1,'pending',NULL)",
                [s.sample_id],
            )
            .map_err(sql_error)?;
        }
        tx.execute(
            "UPDATE plc_sources SET next_seq=?1 WHERE plc_id=?2",
            params![seq + 1, input.plc_id],
        )
        .map_err(sql_error)?;
        tx.execute(
            "UPDATE runtime_metadata SET used_revision=?1 WHERE id=1",
            [&input.revision],
        )
        .map_err(sql_error)?;
        #[cfg(feature = "local-validation")]
        crate::infrastructure::local_fixture::before_cycle_commit(&tx);
        tx.commit().map_err(sql_error)?;
        #[cfg(feature = "local-validation")]
        crate::infrastructure::local_fixture::failpoint("cycle_after_commit");
        Ok(
            json!({"cycleId":cycle,"sourceSeq":seq.to_string(),"revision":input.revision,"savedAt":saved,"quality":quality,"pending":true}),
        )
    }
    pub fn history(&self, mut q: HistoryQuery) -> LocalResult<Value> {
        if q.cursor.map(|n| n <= 0).unwrap_or(false)
            || q.plc_id
                .as_deref()
                .map(|v| !crate::domain::local_configuration::valid_id(v))
                .unwrap_or(false)
            || q.group_id
                .as_deref()
                .map(|v| !crate::domain::local_configuration::valid_id(v))
                .unwrap_or(false)
            || q.quality
                .as_deref()
                .map(|v| !["good", "partial", "bad"].contains(&v))
                .unwrap_or(false)
        {
            return Err("query_limits".into());
        }
        for time in [&mut q.from, &mut q.to] {
            if let Some(v) = time {
                *v = chrono::DateTime::parse_from_rfc3339(v)
                    .map_err(|_| "query_limits")?
                    .with_timezone(&chrono::Utc)
                    .to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
            }
        }
        let n = q.limit.unwrap_or(50);
        if n == 0 || n > 100 {
            return Err("query_limits".into());
        }
        let mut stmt=self.runtime.prepare("SELECT sample_order,id,cycle_id,plc_id,group_id,source_seq,revision,quality,saved_at,db_number,sha256 FROM samples WHERE sample_order<?1 AND (?2 IS NULL OR plc_id=?2) AND (?3 IS NULL OR group_id=?3) AND (?4 IS NULL OR saved_at>=?4) AND (?5 IS NULL OR saved_at<=?5) AND (?6 IS NULL OR quality=?6) ORDER BY sample_order DESC LIMIT ?7").map_err(sql_error)?;
        let rows=stmt.query_map(params![q.cursor.unwrap_or(i64::MAX),q.plc_id,q.group_id,q.from,q.to,q.quality,n],|r|Ok(json!({"order":r.get::<_,i64>(0)?,"sampleId":r.get::<_,String>(1)?,"cycleId":r.get::<_,String>(2)?,"plcId":r.get::<_,String>(3)?,"groupId":r.get::<_,String>(4)?,"sourceSeq":r.get::<_,i64>(5)?.to_string(),"revision":r.get::<_,String>(6)?,"quality":r.get::<_,String>(7)?,"savedAt":r.get::<_,String>(8)?,"dbNumber":r.get::<_,u16>(9)?,"sha256":r.get::<_,String>(10)?}))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok(
            json!({"schemaVersion":1,"nextCursor":rows.last().and_then(|r|r["order"].as_i64()),"items":rows}),
        )
    }
    #[cfg(test)]
    pub fn sample(&self, id: &str) -> LocalResult<Value> {
        self.sample_chunk(id, 0)
    }
    pub fn sample_chunk(&self, id: &str, context_offset: usize) -> LocalResult<Value> {
        let (raw, hash, cycle, revision): (String, String, String, String) = self
            .runtime
            .query_row(
                "SELECT payload,sha256,cycle_id,revision FROM samples WHERE id=?1",
                [id],
                |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
            )
            .map_err(sql_error)?;
        let (manifest, mhash): (String, String) = self
            .runtime
            .query_row(
                "SELECT manifest,sha256 FROM collection_cycles WHERE id=?1",
                [cycle],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        let (context, chash): (String, String) = self
            .runtime
            .query_row(
                "SELECT payload,sha256 FROM configuration_contexts WHERE revision=?1",
                [revision],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        if digest(&raw) != hash || digest(&manifest) != mhash || digest(&context) != chash {
            return Err("payload_corrupt".into());
        }
        let context_bytes = context.len();
        if context_offset > context_bytes || !context.is_char_boundary(context_offset) {
            return Err("query_limits".into());
        }
        let available = (512usize * 1024)
            .saturating_sub(raw.len() + manifest.len() + 4096)
            .min(64 * 1024);
        if available < 4 {
            return Err("query_limits".into());
        }
        let mut end = (context_offset + available).min(context_bytes);
        while !context.is_char_boundary(end) {
            end -= 1
        }
        let chunk = &context[context_offset..end];
        let next = if end < context_bytes { Some(end) } else { None };
        let state: String = self
            .runtime
            .query_row(
                "SELECT state FROM sample_delivery WHERE sample_id=?1",
                [id],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        Ok(
            json!({"schemaVersion":1,"payload":raw,"sha256":hash,"manifest":manifest,"manifestSha256":mhash,"context":chunk,"contextOffset":context_offset,"contextNextOffset":next,"contextBytes":context_bytes,"contextSha256":chash,"deliveryState":state}),
        )
    }
    pub fn logs(&self, cursor: i64, limit: u32) -> LocalResult<Value> {
        if limit == 0 || limit > 200 {
            return Err("query_limits".into());
        }
        let oldest: Option<i64> = self
            .runtime
            .query_row("SELECT min(id) FROM runtime_events", [], |r| r.get(0))
            .map_err(sql_error)?;
        if cursor != 0 && oldest.map(|n| cursor < n - 1).unwrap_or(false) {
            return Err("log_cursor_expired".into());
        }
        let rows=self.runtime.prepare("SELECT id,event,resource,result,created_at FROM runtime_events WHERE id>?1 ORDER BY id LIMIT ?2").map_err(sql_error)?.query_map(params![cursor,limit],|r|Ok(json!({"cursor":r.get::<_,i64>(0)?,"event":r.get::<_,String>(1)?,"resource":r.get::<_,String>(2)?,"result":r.get::<_,String>(3)?,"createdAt":r.get::<_,String>(4)?}))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok(json!({"items":rows,"cursorExpired":false}))
    }
    pub fn cleanup_acknowledged(&mut self, days: u32, quota: u64) -> LocalResult<usize> {
        let ids=self.runtime.prepare("SELECT rowid,id,expected_samples FROM collection_cycles WHERE rowid>?2 AND saved_at < strftime('%Y-%m-%dT%H:%M:%fZ','now',?1) ORDER BY rowid LIMIT 8").map_err(sql_error)?.query_map(params![format!("-{days} days"),self.cleanup_cursor],|r|Ok((r.get::<_,i64>(0)?,r.get::<_,String>(1)?,r.get::<_,i64>(2)?))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        if ids.is_empty() {
            self.cleanup_cursor = 0;
        }
        let mut removed = 0;
        for (cursor, cycle, expected) in ids {
            self.cleanup_cursor = cursor;
            let samples = self
                .runtime
                .prepare("SELECT id FROM samples WHERE cycle_id=?1")
                .map_err(sql_error)?
                .query_map([&cycle], |r| r.get::<_, String>(0))
                .map_err(sql_error)?
                .collect::<Result<Vec<_>, _>>()
                .map_err(sql_error)?;
            if samples.len() as i64 != expected {
                continue;
            }
            let mut eligible = true;
            for s in &samples {
                let state: Option<String> = self
                    .runtime
                    .query_row(
                        "SELECT state FROM sample_delivery WHERE sample_id=?1",
                        [s],
                        |r| r.get(0),
                    )
                    .optional()
                    .map_err(sql_error)?;
                let refs: i64 = self
                    .runtime
                    .query_row(
                        "SELECT count(*) FROM sample_references WHERE sample_id=?1",
                        [s],
                        |r| r.get(0),
                    )
                    .map_err(sql_error)?;
                if state.as_deref() != Some("acknowledged") || refs != 0 {
                    eligible = false;
                    break;
                }
            }
            if !eligible {
                continue;
            }
            self.admit_maintenance(quota)?;
            let tx = self.runtime.transaction().map_err(sql_error)?;
            for s in &samples {
                tx.execute("DELETE FROM sample_delivery WHERE sample_id=?1", [s])
                    .map_err(sql_error)?;
            }
            tx.execute("DELETE FROM samples WHERE cycle_id=?1", [&cycle])
                .map_err(sql_error)?;
            tx.execute("DELETE FROM collection_cycles WHERE id=?1", [cycle])
                .map_err(sql_error)?;
            #[cfg(test)]
            super::tests::maintenance_before_commit(&tx, "cleanup");
            tx.commit().map_err(sql_error)?;
            removed += samples.len();
        }
        Ok(removed)
    }
    pub(super) fn reclaim_incremental(&mut self, quota: u64) -> LocalResult<()> {
        self.admit_maintenance(quota)?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        tx.execute_batch("PRAGMA incremental_vacuum(64)")
            .map_err(sql_error)?;
        #[cfg(test)]
        super::tests::maintenance_before_commit(&tx, "vacuum");
        tx.commit().map_err(sql_error)
    }
    pub(super) fn maintain(&mut self) -> LocalResult<()> {
        let view = self.configuration()?;
        let policy = if let Some(r) = view.active {
            self.revision(&r)?.storage
        } else {
            Default::default()
        };
        self.cleanup_acknowledged(policy.retention_days, policy.quota_bytes)?;
        #[cfg(test)]
        if let (Some(free), Some((meter, _))) = (self.test_after_cleanup_free, &self.test_meter) {
            meter.store(free, std::sync::atomic::Ordering::SeqCst);
        }
        // Cleanup may have committed; free space and the old-image journal bound must be re-read.
        self.reclaim_incremental(policy.quota_bytes)
    }
}
