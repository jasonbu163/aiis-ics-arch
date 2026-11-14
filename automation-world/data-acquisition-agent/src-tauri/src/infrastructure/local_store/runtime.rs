//! 全轮事实、源序号、manifest和pending同事务提交；有界历史只返回原持久字节。
#[cfg(test)]
use super::delivery::{db_now, event, Frozen};
use super::{sql_error, Stores};
#[cfg(test)]
use crate::domain::facts_wire::{Batch, Parent, RECEIPT_MAX};
#[cfg(test)]
use crate::domain::{
    facts_canonical as pf,
    facts_wire::{text, time},
};
use crate::domain::{
    local_configuration::{id, LocalResult},
    local_runtime::HistoryQuery,
    local_sample::*,
};
use rusqlite::{params, OptionalExtension};
use serde_json::{json, Value};
#[cfg(test)]
use std::collections::BTreeSet;
impl Stores {
    #[cfg(test)]
    pub fn commit_cycle(&mut self, input: CycleInput) -> LocalResult<Value> {
        let reporting = self.reporting_identity(&input.plc_id)?;
        self.commit_cycle_with_reporting(input, reporting)
    }

    pub fn commit_cycle_with_reporting(
        &mut self,
        mut input: CycleInput,
        reporting: Option<crate::domain::sample_upload::ReportingIdentity>,
    ) -> LocalResult<Value> {
        use crate::domain::business_time;
        let version: u32 = self
            .runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)?;
        input.started_at = business_time::normalize(&input.started_at)?;
        input.finished_at = business_time::normalize(&input.finished_at)?;
        for points in input.points.values_mut() {
            for point in points.values_mut() {
                point.observed_at = business_time::normalize(&point.observed_at)?;
            }
        }
        for read in &mut input.reads {
            read.started_at = business_time::normalize(&read.started_at)?;
            read.finished_at = business_time::normalize(&read.finished_at)?;
        }
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
            .query_row(business_time::SQL_NOW, [], |r| r.get(0))
            .map_err(sql_error)?;
        let mut packages = vec![];
        for (db, points) in &input.points {
            let sample = SamplePayload {
                schema_version: 2,
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
            schema_version: 2,
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
        let total = raw_manifest.len() + packages.iter().map(|(_, p, _)| p.len()).sum::<usize>();
        if (version == 4
            && (total > 4 * 1024 * 1024
                || packages.iter().any(|(_, p, _)| p.len() > 2 * 1024 * 1024)))
            || (version != 4 && total > 512 * 1024)
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
        if version == 4 {
            tx.execute("INSERT INTO reporting_cycles(cycle_id,instance_id,plc_id,source_generation) VALUES(?1,?2,?3,?4)", params![cycle, reporting.as_ref().map(|s| &s.instance_id), reporting.as_ref().map(|s| &s.plc_id), reporting.as_ref().map(|s| &s.source_generation)]).map_err(sql_error)?;
        }
        for (s, raw, hash) in packages {
            tx.execute("INSERT INTO samples(id,cycle_id,db_number,plc_id,group_id,source_seq,revision,quality,saved_at,schema_version,payload,sha256,payload_bytes) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,2,?10,?11,?12)",params![s.sample_id,cycle,s.db_number,s.plc_id,s.group_id,seq,s.revision,quality,saved,raw,hash,raw.len() as i64]).map_err(sql_error)?;
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
                *v = crate::domain::business_time::normalize(v).map_err(|_| "query_limits")?;
            }
        }
        if matches!((&q.from, &q.to), (Some(from), Some(to)) if from > to) {
            return Err("query_limits".into());
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
                [&cycle],
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
        let version: u32 = self
            .runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)?;
        let detail_budget = if version == 4 {
            3usize * 1024 * 1024
        } else {
            512usize * 1024
        };
        let available = detail_budget
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
        let mut state: String = self
            .runtime
            .query_row(
                "SELECT state FROM sample_delivery WHERE sample_id=?1",
                [id],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if version == 4 {
            let local_only: bool = self.runtime.query_row("SELECT EXISTS(SELECT 1 FROM reporting_cycles WHERE cycle_id=?1 AND instance_id IS NULL)", [&cycle], |r| r.get(0)).map_err(sql_error)?;
            if local_only {
                state = "local_only".into();
            }
        }
        let upload = if version == 4 {
            self.runtime.query_row("SELECT state,attempt,last_error,body_sha,origin,dispatched_at,acknowledged_at,receipt_sha,instance_id,plc_id,source_generation FROM sample_uploads WHERE sample_id=?1", [id], |r| Ok(json!({"protocol":"plc-facts/v2","state":r.get::<_,String>(0)?,"attempt":r.get::<_,u32>(1)?,"lastError":r.get::<_,Option<String>>(2)?,"bodySha256":r.get::<_,Option<String>>(3)?,"origin":r.get::<_,Option<String>>(4)?,"dispatchedAt":r.get::<_,Option<String>>(5)?,"acknowledgedAt":r.get::<_,Option<String>>(6)?,"receiptSha256":r.get::<_,Option<String>>(7)?,"instanceId":r.get::<_,String>(8)?,"plcId":r.get::<_,String>(9)?,"sourceGeneration":r.get::<_,String>(10)?}))).optional().map_err(sql_error)?
        } else {
            None
        };
        Ok(
            json!({"schemaVersion":1,"payload":raw,"sha256":hash,"manifest":manifest,"manifestSha256":mhash,"context":chunk,"contextOffset":context_offset,"contextNextOffset":next,"contextBytes":context_bytes,"contextSha256":chash,"deliveryState":state,"deliveries":self.sample_deliveries(id)?,"sampleUpload":upload}),
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
        let version: u32 = self
            .runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)?;
        let clock: String = self
            .runtime
            .query_row(crate::domain::business_time::SQL_NOW, [], |r| r.get(0))
            .map_err(sql_error)?;
        let cutoff = crate::domain::business_time::retention_cutoff(&clock, days)?;
        let ids=self.runtime.prepare("SELECT rowid,id,expected_samples FROM collection_cycles WHERE rowid>?2 AND saved_at < ?1 ORDER BY rowid LIMIT 8").map_err(sql_error)?.query_map(params![cutoff,self.cleanup_cursor],|r|Ok((r.get::<_,i64>(0)?,r.get::<_,String>(1)?,r.get::<_,i64>(2)?))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        if ids.is_empty() {
            self.cleanup_cursor = 0;
        }
        let mut removed = 0;
        for (cursor, cycle, expected) in ids {
            self.cleanup_cursor = cursor;
            let local_only = if version == 4 {
                self.runtime.query_row("SELECT EXISTS(SELECT 1 FROM reporting_cycles WHERE cycle_id=?1 AND instance_id IS NULL)", [&cycle], |r| r.get::<_,bool>(0)).map_err(sql_error)?
            } else {
                false
            };
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
                        if version == 4 {
                            "SELECT state FROM sample_uploads WHERE sample_id=?1"
                        } else {
                            "SELECT state FROM sample_delivery WHERE sample_id=?1"
                        },
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
                if (if local_only {
                    state.is_some()
                } else {
                    state.as_deref() != Some("acknowledged")
                }) || refs != 0
                {
                    eligible = false;
                    break;
                }
            }
            if !eligible {
                continue;
            }
            if version == 4 {
                let old_evidence: bool = self.runtime.query_row("SELECT EXISTS(SELECT 1 FROM delivery_cycles WHERE cycle_id=?1) OR EXISTS(SELECT 1 FROM delivery_parts WHERE cycle_id=?1)", [&cycle], |r| r.get(0)).map_err(sql_error)?;
                if old_evidence {
                    continue;
                }
            }
            self.admit_maintenance(quota)?;
            let delivery = self.delivery_available()?;
            let tx = self.runtime.transaction().map_err(sql_error)?;
            if delivery {
                super::delivery::cleanup_cycle(&tx, &cycle)?;
            }
            for s in &samples {
                if version == 4 && !local_only {
                    let deleted = tx.execute("DELETE FROM sample_uploads WHERE sample_id=?1 AND state='acknowledged'", [s]).map_err(sql_error)?;
                    if deleted != 1 {
                        return Err("delivery_cleanup_referenced".into());
                    }
                }
                tx.execute("DELETE FROM sample_delivery WHERE sample_id=?1", [s])
                    .map_err(sql_error)?;
            }
            tx.execute("DELETE FROM samples WHERE cycle_id=?1", [&cycle])
                .map_err(sql_error)?;
            if version == 4 {
                tx.execute("DELETE FROM reporting_cycles WHERE cycle_id=?1", [&cycle])
                    .map_err(sql_error)?;
            }
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

// Reliable receipts and sample delivery state share one runtime transaction.
impl Stores {
    #[cfg(test)]
    pub fn commit_delivery(
        &mut self,
        frozen: &Frozen,
        envelope: &Value,
        raw: &str,
    ) -> LocalResult<()> {
        crate::domain::local_delivery::verify_success(&frozen.batch, envelope)?;
        if pf::parse(raw.as_bytes(), RECEIPT_MAX)? != *envelope {
            return Err("invalid_receipt".into());
        }
        if raw.len() > RECEIPT_MAX {
            return Err("response_too_large".into());
        }
        let data = &envelope["data"];
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let old: Option<String> = tx
            .query_row(
                "SELECT receipt_id FROM delivery_receipts WHERE batch_id=?1",
                [&frozen.batch.batch_id],
                |r| r.get(0),
            )
            .optional()
            .map_err(sql_error)?;
        if let Some(receipt) = old {
            if receipt == text(data, "receiptId")? {
                return Ok(());
            }
            return Err("delivery_receipt_conflict".into());
        }
        let state: String = tx
            .query_row(
                "SELECT state FROM delivery_batches WHERE batch_id=?1 AND body_sha=?2",
                params![frozen.batch.batch_id, frozen.body_sha],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if !["inflight", "unknown", "retry_wait", "prepared"].contains(&state.as_str()) {
            return Err("delivery_state_conflict".into());
        }
        tx.execute(
            "INSERT INTO delivery_receipts VALUES(?1,?2,?3,?4,?5,?6,?7,'acknowledged')",
            params![
                frozen.batch.batch_id,
                text(data, "receiptId")?,
                frozen.batch.request_digest,
                raw,
                pf::sha(raw.as_bytes()),
                text(data, "committedAt")?,
                text(data, "proofExpiresAt")?
            ],
        )
        .map_err(sql_error)?;
        let now = db_now(&tx)?;
        for part in &frozen.batch.samples {
            let n=tx.execute("UPDATE delivery_parts SET state='acknowledged',receipt_id=?1 WHERE sample_id=?2 AND part=?3 AND batch_id=?4 AND content_digest=?5",params![text(data,"receiptId")?,part.sample_id,part.part,frozen.batch.batch_id,part.content_digest]).map_err(sql_error)?;
            if n != 1 {
                return Err("delivery_part_conflict".into());
            }
            let (expected,total,acked):(u32,u32,u32)=tx.query_row("SELECT max(parts),count(*),sum(CASE WHEN state='acknowledged' THEN 1 ELSE 0 END) FROM delivery_parts WHERE sample_id=?1",[&part.sample_id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).map_err(sql_error)?;
            if total == expected && acked == expected {
                tx.execute("UPDATE sample_delivery SET state='acknowledged',acknowledged_at=?1 WHERE sample_id=?2",params![now,part.sample_id]).map_err(sql_error)?;
                tx.execute("DELETE FROM sample_references WHERE sample_id=?1 AND reference_id LIKE 'delivery-batch:%'",[&part.sample_id]).map_err(sql_error)?;
            }
            tx.execute(
                "DELETE FROM sample_references WHERE sample_id=?1 AND reference_id=?2",
                params![
                    part.sample_id,
                    format!("delivery-batch:{}", frozen.batch.batch_id)
                ],
            )
            .map_err(sql_error)?;
        }
        for cycle in &frozen.batch.cycles {
            let remaining:u32=tx.query_row("SELECT count(*) FROM delivery_parts WHERE cycle_id=?1 AND state!='acknowledged'",[&cycle.cycle_id],|r|r.get(0)).map_err(sql_error)?;
            if remaining == 0 {
                for sample in &cycle.transport_manifest {
                    tx.execute(
                        "DELETE FROM sample_references WHERE sample_id=?1 AND reference_id=?2",
                        params![
                            sample.sample_id,
                            format!("delivery-cycle:{}", cycle.cycle_id)
                        ],
                    )
                    .map_err(sql_error)?;
                }
            }
        }
        tx.execute("UPDATE delivery_batches SET state='acknowledged',body=NULL,last_error=NULL WHERE batch_id=?1",[&frozen.batch.batch_id]).map_err(sql_error)?;
        event(
            &tx,
            "delivery_acknowledged",
            &frozen.batch.batch_id,
            "acknowledged",
        )?;
        tx.commit().map_err(sql_error)?;
        self.log.event(
            "delivery_acknowledged",
            &frozen.batch.batch_id,
            "acknowledged",
        )?;
        Ok(())
    }
    #[cfg(test)]
    pub fn reject_delivery(
        &mut self,
        frozen: &Frozen,
        envelope: &Value,
        eligible: &[(String, u32)],
        raw: &str,
    ) -> LocalResult<()> {
        let data = &envelope["data"];
        if raw.len() > RECEIPT_MAX || pf::parse(raw.as_bytes(), RECEIPT_MAX)? != *envelope {
            return Err("invalid_receipt".into());
        }
        let now = db_now(&self.runtime)?;
        if time(text(data, "rejectionExpiresAt")?)? <= time(&now)? {
            return self
                .fail_delivery(
                    &frozen.batch.batch_id,
                    "needs_review",
                    "parent_proof_expired",
                    1,
                    false,
                )
                .map(|_| ());
        }
        let child = if !eligible.is_empty() && frozen.depth < 8 {
            let parts = frozen
                .batch
                .samples
                .iter()
                .filter(|p| eligible.contains(&(p.sample_id.clone(), p.part)))
                .cloned()
                .collect::<Vec<_>>();
            let used = parts
                .iter()
                .map(|p| p.cycle_id.as_str())
                .collect::<BTreeSet<_>>();
            let cycles = frozen
                .batch
                .cycles
                .iter()
                .filter(|c| used.contains(c.cycle_id.as_str()))
                .cloned()
                .collect();
            Some(Batch::new(
                frozen.batch.instance_id.clone(),
                id(),
                now.clone(),
                cycles,
                parts,
                Some(Parent {
                    batch_id: frozen.batch.batch_id.clone(),
                    request_digest: frozen.batch.request_digest.clone(),
                    rejection_token: text(data, "rejectionToken")?.into(),
                }),
            )?)
        } else {
            None
        };
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let existing: Option<String> = tx
            .query_row(
                "SELECT receipt_id FROM delivery_receipts WHERE batch_id=?1",
                [&frozen.batch.batch_id],
                |r| r.get(0),
            )
            .optional()
            .map_err(sql_error)?;
        if let Some(receipt) = existing {
            if receipt == text(data, "receiptId")? {
                return Ok(());
            }
            return Err("delivery_receipt_conflict".into());
        }
        tx.execute(
            "INSERT INTO delivery_receipts VALUES(?1,?2,?3,?4,?5,?6,?7,'rejected')",
            params![
                frozen.batch.batch_id,
                text(data, "receiptId")?,
                frozen.batch.request_digest,
                raw,
                pf::sha(raw.as_bytes()),
                text(data, "recordedAt")?,
                text(data, "rejectionExpiresAt")?
            ],
        )
        .map_err(sql_error)?;
        tx.execute("UPDATE delivery_batches SET state='rejected',last_error=?2 WHERE batch_id=?1 AND body_sha=?3",params![frozen.batch.batch_id,text(envelope,"errorCode")?,frozen.body_sha]).map_err(sql_error)?;
        for p in &frozen.batch.samples {
            tx.execute("UPDATE delivery_parts SET state='needs_review' WHERE sample_id=?1 AND part=?2 AND batch_id=?3",params![p.sample_id,p.part,frozen.batch.batch_id]).map_err(sql_error)?;
        }
        if let Some(child) = child {
            let body = child.bytes()?;
            tx.execute("INSERT INTO delivery_batches(batch_id,target_id,settings_revision,request_digest,body_sha,body,members,parent_id,parent_depth,state,next_attempt_at,created_at) VALUES(?1,?2,(SELECT settings_revision FROM delivery_settings WHERE id=1),?3,?4,?5,?6,?7,?8,'prepared',?9,?9)",params![child.batch_id,frozen.target_id,child.request_digest,pf::sha(body.as_bytes()),body,encode(&child.samples.iter().map(|p|json!({"sampleId":p.sample_id,"part":p.part,"contentDigest":p.content_digest})).collect::<Vec<_>>())?,frozen.batch.batch_id,frozen.depth+1,child.batch_created_at]).map_err(sql_error)?;
            for p in &child.samples {
                tx.execute("UPDATE delivery_parts SET state='prepared',batch_id=?1 WHERE sample_id=?2 AND part=?3 AND batch_id=?4",params![child.batch_id,p.sample_id,p.part,frozen.batch.batch_id]).map_err(sql_error)?;
                tx.execute(
                    "INSERT OR IGNORE INTO sample_references VALUES(?1,?2)",
                    params![p.sample_id, format!("delivery-batch:{}", child.batch_id)],
                )
                .map_err(sql_error)?;
            }
        }
        event(&tx, "delivery_rejected", &frozen.batch.batch_id, "rejected")?;
        tx.commit().map_err(sql_error)?;
        self.log
            .event("delivery_rejected", &frozen.batch.batch_id, "rejected")?;
        Ok(())
    }
}
