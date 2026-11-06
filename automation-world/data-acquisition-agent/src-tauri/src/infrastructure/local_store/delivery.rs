//! 同runtime可靠投递：新v3能力、独立设置CAS、冻结/派发/ACK短事务与样本引用保护。
use super::{sql_error, Stores};
use crate::domain::{
    facts_canonical as pf,
    facts_wire::*,
    local_configuration::{id, LocalResult},
    local_delivery::DeliverySettings,
    local_sample::encode,
};
use rusqlite::{params, OptionalExtension};
use serde_json::{json, Value};
use std::collections::BTreeSet;
pub(super) fn verify_schema(c: &rusqlite::Connection) -> LocalResult<()> {
    super::schema::verify_structure(c, &super::schema::runtime_v3_sql())?;
    let (revision, settings): (String, String) = c
        .query_row(
            "SELECT settings_revision,payload FROM delivery_settings WHERE id=1",
            [],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .map_err(sql_error)?;
    let parsed: DeliverySettings =
        serde_json::from_str(&settings).map_err(|_| "delivery_settings_corrupt")?;
    parsed.validate()?;
    if parsed.settings_revision != revision {
        return Err("delivery_settings_corrupt".into());
    }
    Ok(())
}
#[derive(Clone, Debug)]
pub(crate) struct Frozen {
    pub batch: Batch,
    pub body: String,
    pub body_sha: String,
    pub origin: String,
    pub target_id: String,
    pub depth: u32,
}
impl Stores {
    pub fn delivery_available(&self) -> LocalResult<bool> {
        let version: i64 = self
            .runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)?;
        Ok(version == 3)
    }
    pub(super) fn delivery_guard(&self) -> LocalResult<()> {
        if self.delivery_available()? {
            Ok(())
        } else {
            Err("delivery_profile_upgrade_required".into())
        }
    }
}
pub(super) fn db_now(c: &rusqlite::Connection) -> LocalResult<String> {
    c.query_row(crate::domain::business_time::SQL_NOW, [], |r| r.get(0))
        .map_err(sql_error)
}
pub(super) fn event(
    tx: &rusqlite::Transaction,
    event: &str,
    resource: &str,
    result: &str,
) -> LocalResult<()> {
    let now = db_now(tx)?;
    tx.execute(
        "INSERT INTO delivery_events(event,resource,result,created_at) VALUES(?1,?2,?3,?4)",
        params![event, resource, result, now],
    )
    .map_err(sql_error)?;
    tx.execute(
        "DELETE FROM delivery_events WHERE id<(SELECT max(id) FROM delivery_events)-499",
        [],
    )
    .map_err(sql_error)?;
    Ok(())
}
impl Stores {
    pub fn delivery_snapshot(&self, running: bool) -> LocalResult<Value> {
        if !self.delivery_available()? {
            return Ok(
                json!({"schemaVersion":1,"available":false,"running":false,"state":"delivery_profile_upgrade_required"}),
            );
        }
        let counts = self
            .runtime
            .prepare("SELECT state,count(*) FROM delivery_batches GROUP BY state")
            .map_err(sql_error)?
            .query_map([], |r| {
                Ok((r.get::<_, String>(0)?, json!(r.get::<_, u64>(1)?)))
            })
            .map_err(sql_error)?
            .collect::<std::result::Result<serde_json::Map<String, Value>, _>>()
            .map_err(sql_error)?;
        let pending: u64 = self
            .runtime
            .query_row(
                "SELECT count(*) FROM sample_delivery WHERE state='pending'",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        // 一个 sample_delivery 主键只进入一个分类；blocked 诊断尚无 delivery_parts。
        let mut sample_counts = serde_json::Map::new();
        for key in ["unfrozen", "frozen", "needsProcessing", "acknowledged"] {
            sample_counts.insert(key.into(), json!(0));
        }
        let mut query = self.runtime.prepare("SELECT category,count(*) FROM (SELECT CASE WHEN d.state='acknowledged' THEN 'acknowledged' WHEN EXISTS(SELECT 1 FROM delivery_batches b,json_each(CASE WHEN json_type(b.members)='array' THEN b.members ELSE json_extract(b.members,'$.sampleIds') END) m WHERE b.state IN ('blocked','expired_unconfirmed','needs_review') AND CASE WHEN m.type='text' THEN m.value ELSE json_extract(m.value,'$.sampleId') END=d.sample_id) THEN 'needsProcessing' WHEN EXISTS(SELECT 1 FROM delivery_parts p WHERE p.sample_id=d.sample_id) THEN 'frozen' ELSE 'unfrozen' END category FROM sample_delivery d) GROUP BY category").map_err(sql_error)?;
        for row in query
            .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, u64>(1)?)))
            .map_err(sql_error)?
        {
            let (key, count) = row.map_err(sql_error)?;
            sample_counts.insert(key, json!(count));
        }
        let acknowledged = sample_counts["acknowledged"].as_u64().unwrap_or(0);
        let last: Option<String> = self
            .runtime
            .query_row(
                "SELECT max(acknowledged_at) FROM sample_delivery WHERE state='acknowledged'",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        let state = if running {
            [
                "needs_review",
                "expired_unconfirmed",
                "blocked",
                "unknown",
                "retry_wait",
                "inflight",
            ]
            .into_iter()
            .find(|key| counts.get(*key).and_then(Value::as_u64).unwrap_or(0) > 0)
            .unwrap_or("running")
        } else {
            "stopped"
        };
        let settings = self.delivery_settings()?;
        let bytes = self.delivery_bytes()?;
        Ok(
            json!({"schemaVersion":1,"available":true,"running":running,"state":state,"targetId":settings.target_id,"origin":settings.origin,"pending":pending,"acknowledged":acknowledged,"counts":counts,"sampleCounts":sample_counts,"lastAcknowledgedAt":last,"requestBytes":bytes.0,"receiptBytes":bytes.1,"metadataBytes":bytes.2}),
        )
    }
    pub fn list_deliveries(&self, cursor: Option<i64>, limit: u32) -> LocalResult<Value> {
        self.delivery_guard()?;
        if ![10, 20, 50].contains(&limit) || cursor.map(|n| n <= 0).unwrap_or(false) {
            return Err("query_limits".into());
        }
        let rows=self.runtime.prepare("SELECT created_order,batch_id,state,attempt,next_attempt_at,created_at,last_error,request_digest,body_sha,target_id FROM delivery_batches WHERE created_order<?1 ORDER BY created_order DESC LIMIT ?2").map_err(sql_error)?.query_map(params![cursor.unwrap_or(i64::MAX),limit],|r|Ok(json!({"order":r.get::<_,i64>(0)?,"batchId":r.get::<_,String>(1)?,"state":r.get::<_,String>(2)?,"attempt":r.get::<_,u32>(3)?,"nextAttemptAt":r.get::<_,String>(4)?,"createdAt":r.get::<_,String>(5)?,"lastError":r.get::<_,Option<String>>(6)?,"requestDigest":r.get::<_,String>(7)?,"bodySha256":r.get::<_,String>(8)?,"targetId":r.get::<_,String>(9)?}))).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok(
            json!({"schemaVersion":1,"nextCursor":if rows.len()==limit as usize{rows.last().and_then(|r|r["order"].as_i64())}else{None},"items":rows}),
        )
    }
    pub fn get_delivery(&self, batch_id: &str) -> LocalResult<Value> {
        self.delivery_guard()?;
        let (state,digest,body_sha,members,parent,depth,error):(String,String,String,String,Option<String>,u32,Option<String>)=self.runtime.query_row("SELECT state,request_digest,body_sha,members,parent_id,parent_depth,last_error FROM delivery_batches WHERE batch_id=?1",[batch_id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?))).map_err(sql_error)?;
        let receipt: Option<(String, String)> = self
            .runtime
            .query_row(
                "SELECT response_utf8,response_sha FROM delivery_receipts WHERE batch_id=?1",
                [batch_id],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .optional()
            .map_err(sql_error)?;
        Ok(
            json!({"schemaVersion":1,"batchId":batch_id,"state":state,"requestDigest":digest,"bodySha256":body_sha,"members":serde_json::from_str::<Value>(&members).map_err(|_|"delivery_corrupt")?,"parentBatchId":parent,"parentDepth":depth,"lastError":error,"receipt":receipt.as_ref().map(|r|&r.0),"receiptSha256":receipt.as_ref().map(|r|&r.1)}),
        )
    }
    pub fn facts_source_material(&self) -> LocalResult<Value> {
        self.delivery_guard()?;
        let view = self.configuration()?;
        let mut sources = vec![];
        if let Some(revision) = view.active {
            let raw: String = self
                .runtime
                .query_row(
                    "SELECT payload FROM configuration_contexts WHERE revision=?1",
                    [revision],
                    |r| r.get(0),
                )
                .map_err(sql_error)?;
            let context = pf::parse(raw.as_bytes(), 16 * 1024 * 1024)?;
            for plc in context["plcs"].as_array().ok_or("invalid_source")? {
                let plc_id = text(plc, "id")?;
                let (_, digest) = definitions(&context, plc_id)?;
                let source: Option<(String, i64)> = self
                    .runtime
                    .query_row(
                        "SELECT generation,next_seq FROM plc_sources WHERE plc_id=?1",
                        [plc_id],
                        |r| Ok((r.get(0)?, r.get(1)?)),
                    )
                    .optional()
                    .map_err(sql_error)?;
                sources.push(json!({"instanceId":self.instance,"plcId":plc_id,"sourceGeneration":source.as_ref().map(|s|&s.0),"nextSourceSeq":source.as_ref().map(|s|s.1.to_string()),"definitionSetDigest":digest,"contextSha256":pf::sha(raw.as_bytes())}));
            }
        }
        Ok(
            json!({"schemaVersion":1,"contractVersion":"plc-facts/v1","digestProfile":"pf-json/v1","instanceId":self.instance,"sources":sources}),
        )
    }
    pub(super) fn build_delivery_cycle(&self, cycle: &str) -> LocalResult<BuiltCycle> {
        let (manifest,hash,context,chash):(String,String,String,String)=self.runtime.query_row("SELECT c.manifest,c.sha256,x.payload,x.sha256 FROM collection_cycles c JOIN configuration_contexts x ON c.revision=x.revision WHERE c.id=?1",[cycle],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).map_err(sql_error)?;
        let rows = self
            .runtime
            .prepare("SELECT payload,sha256 FROM samples WHERE cycle_id=?1 ORDER BY id LIMIT 129")
            .map_err(sql_error)?
            .query_map([cycle], |r| {
                Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?))
            })
            .map_err(sql_error)?
            .collect::<std::result::Result<Vec<_>, _>>()
            .map_err(sql_error)?;
        build_cycle(&self.instance, &manifest, &hash, &context, &chash, &rows)
    }
    pub fn preview_delivery(&self, cycle: &str) -> LocalResult<Value> {
        self.delivery_guard()?;
        let built = self.build_delivery_cycle(cycle)?;
        let batch = Batch::new(
            self.instance.clone(),
            id(),
            db_now(&self.runtime)?,
            vec![built.cycle],
            built.parts,
            None,
        )?;
        Ok(
            json!({"schemaVersion":1,"previewOnly":true,"requestDigest":batch.request_digest,"bytes":batch.bytes()?.len(),"body":batch.bytes()?}),
        )
    }
    pub(super) fn source_admitted(settings: &DeliverySettings, built: &BuiltCycle) -> bool {
        settings.sources.iter().any(|s| {
            s.plc_id == built.plc_id
                && s.source_generation == built.source_generation
                && s.definition_set_digest == built.definition_set_digest
                && s.sequence_from
                    .parse::<i64>()
                    .map(|n| built.source_seq >= n)
                    .unwrap_or(false)
                && s.sequence_through
                    .parse::<i64>()
                    .map(|n| built.source_seq <= n)
                    .unwrap_or(false)
        })
    }
    fn block_cycle(
        &mut self,
        cycle: &str,
        error: &str,
        settings: &DeliverySettings,
    ) -> LocalResult<()> {
        let samples = self
            .runtime
            .prepare("SELECT id FROM samples WHERE cycle_id=?1")
            .map_err(sql_error)?
            .query_map([cycle], |r| r.get::<_, String>(0))
            .map_err(sql_error)?
            .collect::<std::result::Result<Vec<_>, _>>()
            .map_err(sql_error)?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let now = db_now(&tx)?;
        let batch = id();
        let members = encode(&json!({"cycleId":cycle,"sampleIds":samples}))?;
        tx.execute("INSERT INTO delivery_batches(batch_id,target_id,settings_revision,request_digest,body_sha,body,members,parent_id,parent_depth,state,next_attempt_at,created_at,last_error) VALUES(?1,?2,?3,'','',NULL,?4,NULL,0,'blocked',?5,?5,?6)",params![batch,settings.target_id,settings.settings_revision,members,now,error]).map_err(sql_error)?;
        for sample in samples {
            tx.execute(
                "INSERT INTO sample_references VALUES(?1,?2)",
                params![sample, format!("delivery-blocked:{cycle}")],
            )
            .map_err(sql_error)?;
        }
        event(&tx, "delivery_blocked", &batch, error)?;
        tx.commit().map_err(sql_error)?;
        Ok(())
    }
    pub(super) fn freeze_cycle(
        &mut self,
        built: BuiltCycle,
        settings: &DeliverySettings,
        latest: bool,
    ) -> LocalResult<Option<Frozen>> {
        let existing: BTreeSet<(String, u32)> = self
            .runtime
            .prepare(
                "SELECT sample_id,part FROM delivery_parts WHERE cycle_id=?1 AND state!='pending'",
            )
            .map_err(sql_error)?
            .query_map([&built.cycle.cycle_id], |r| Ok((r.get(0)?, r.get(1)?)))
            .map_err(sql_error)?
            .collect::<std::result::Result<_, _>>()
            .map_err(sql_error)?;
        let batch_id = id();
        let now = db_now(&self.runtime)?;
        let mut selected = vec![];
        for p in &built.parts {
            if existing.contains(&(p.sample_id.clone(), p.part)) {
                continue;
            }
            let mut candidate = selected.clone();
            candidate.push(p.clone());
            if Batch::new(
                self.instance.clone(),
                batch_id.clone(),
                now.clone(),
                vec![built.cycle.clone()],
                candidate.clone(),
                None,
            )
            .is_ok()
            {
                selected = candidate;
            } else if selected.is_empty() {
                return Err("minimum_request_too_large".into());
            } else {
                break;
            }
        }
        if selected.is_empty() {
            return Ok(None);
        }
        let batch = Batch::new(
            self.instance.clone(),
            batch_id.clone(),
            now,
            vec![built.cycle.clone()],
            selected,
            None,
        )?;
        let body = batch.bytes()?;
        let body_sha = pf::sha(body.as_bytes());
        let cycle_digest = cycle_digest(&built.cycle)?;
        let quota = self.delivery_quota()?;
        self.admit_maintenance(quota)?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let old: Option<(String, String)> = tx
            .query_row(
                "SELECT cycle_digest,target_id FROM delivery_cycles WHERE cycle_id=?1",
                [&built.cycle.cycle_id],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .optional()
            .map_err(sql_error)?;
        if let Some((digest, target)) = old {
            if digest != cycle_digest || Some(&target) != settings.target_id.as_ref() {
                return Err("delivery_cycle_conflict".into());
            }
        } else {
            tx.execute(
                "INSERT INTO delivery_cycles VALUES(?1,?2,?3,?4,?5,?6)",
                params![
                    built.cycle.cycle_id,
                    settings.target_id,
                    built.cycle.manifest_sha256,
                    built.cycle.context_sha256,
                    cycle_digest,
                    encode(&built.cycle)?
                ],
            )
            .map_err(sql_error)?;
            for p in &built.parts {
                tx.execute(
                    "INSERT INTO delivery_parts VALUES(?1,?2,?3,?4,?5,?6,?7,'pending',NULL,NULL)",
                    params![
                        p.sample_id,
                        p.part,
                        p.parts,
                        p.cycle_id,
                        p.source_sha256,
                        p.content_digest,
                        encode(&p.point_ids)?
                    ],
                )
                .map_err(sql_error)?;
            }
            for s in &built.cycle.transport_manifest {
                tx.execute(
                    "INSERT INTO sample_references VALUES(?1,?2)",
                    params![
                        s.sample_id,
                        format!("delivery-cycle:{}", built.cycle.cycle_id)
                    ],
                )
                .map_err(sql_error)?;
            }
        }
        let revision: String = tx
            .query_row(
                "SELECT settings_revision FROM delivery_settings WHERE id=1",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if revision != settings.settings_revision {
            return Err("settings_conflict".into());
        }
        tx.execute("INSERT INTO delivery_batches(batch_id,target_id,settings_revision,request_digest,body_sha,body,members,parent_id,parent_depth,state,next_attempt_at,created_at) VALUES(?1,?2,?3,?4,?5,?6,?7,NULL,0,'prepared',?8,?8)",params![batch_id,settings.target_id,settings.settings_revision,batch.request_digest,body_sha,body,encode(&batch.samples.iter().map(|p|json!({"sampleId":p.sample_id,"part":p.part,"contentDigest":p.content_digest})).collect::<Vec<_>>())?,batch.batch_created_at]).map_err(sql_error)?;
        for p in &batch.samples {
            let n=tx.execute("UPDATE delivery_parts SET state='prepared',batch_id=?1 WHERE sample_id=?2 AND part=?3 AND state='pending' AND batch_id IS NULL",params![batch_id,p.sample_id,p.part]).map_err(sql_error)?;
            if n != 1 {
                return Err("delivery_part_owned".into());
            }
            tx.execute(
                "INSERT OR IGNORE INTO sample_references VALUES(?1,?2)",
                params![p.sample_id, format!("delivery-batch:{batch_id}")],
            )
            .map_err(sql_error)?;
        }
        let raw: String = tx
            .query_row(
                if latest {
                    "SELECT latest_cursor FROM delivery_settings WHERE id=1"
                } else {
                    "SELECT history_cursor FROM delivery_settings WHERE id=1"
                },
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        let mut rotation = crate::domain::local_delivery::Rotation::decode(&raw);
        rotation.advance(&built.plc_id, &built.group_id);
        tx.execute(if latest{"UPDATE delivery_settings SET latest_streak=min(latest_streak+1,3),latest_cursor=?1 WHERE id=1"}else{"UPDATE delivery_settings SET latest_streak=0,history_cursor=?1 WHERE id=1"},[encode(&rotation)?]).map_err(sql_error)?;
        event(&tx, "delivery_prepared", &batch_id, "prepared")?;
        tx.commit().map_err(sql_error)?;
        self.log.event("delivery_prepared", &batch_id, "prepared")?;
        Ok(Some(Frozen {
            batch,
            body,
            body_sha,
            origin: settings.origin.clone().ok_or("target_missing")?,
            target_id: settings.target_id.clone().ok_or("target_missing")?,
            depth: 0,
        }))
    }
    fn frozen(&self, batch_id: &str, settings: &DeliverySettings) -> LocalResult<Frozen> {
        let (body,sha,target,depth,digest):(Option<String>,String,String,u32,String)=self.runtime.query_row("SELECT body,body_sha,target_id,parent_depth,request_digest FROM delivery_batches WHERE batch_id=?1",[batch_id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).map_err(sql_error)?;
        let body = body.ok_or("delivery_recovery_material_missing")?;
        if body.len() > REQUEST_MAX
            || pf::sha(body.as_bytes()) != sha
            || Some(&target) != settings.target_id.as_ref()
        {
            return Err("delivery_corrupt".into());
        }
        let batch: Batch = serde_json::from_value(pf::parse(body.as_bytes(), REQUEST_MAX)?)
            .map_err(|_| "delivery_corrupt")?;
        if batch.request_digest != digest
            || batch.digest()? != digest
            || batch.instance_id != self.instance
            || batch.batch_id != batch_id
            || batch.contract_version != "plc-facts/v1"
            || batch.source_profile != "daa-local/v2"
            || batch.digest_profile != "pf-json/v1"
            || depth > 8
        {
            return Err("delivery_corrupt".into());
        }
        let members: String = self
            .runtime
            .query_row(
                "SELECT members FROM delivery_batches WHERE batch_id=?1",
                [batch_id],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        let expected = json!(batch
            .samples
            .iter()
            .map(|p| json!({"sampleId":p.sample_id,"part":p.part,"contentDigest":p.content_digest}))
            .collect::<Vec<_>>());
        if pf::parse(format!("{{\"items\":{members}}}").as_bytes(), REQUEST_MAX)?["items"]
            != expected
        {
            return Err("delivery_corrupt".into());
        }
        for part in &batch.samples {
            let (source_hash,payload,parts,content,owned):(String,String,u32,String,String)=self.runtime.query_row("SELECT s.sha256,s.payload,p.parts,p.content_digest,p.batch_id FROM delivery_parts p JOIN samples s ON s.id=p.sample_id WHERE p.sample_id=?1 AND p.part=?2",params![part.sample_id,part.part],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).map_err(sql_error)?;
            if part.source_sha256 != format!("sha256:{source_hash}")
                || payload != part.payload_utf8
                || pf::sha(payload.as_bytes()) != part.source_sha256
                || parts != part.parts
                || content != part.content_digest
                || owned != batch_id
            {
                return Err("delivery_corrupt".into());
            }
        }
        for cycle in &batch.cycles {
            let (wire, digest): (String, String) = self
                .runtime
                .query_row(
                    "SELECT wire,cycle_digest FROM delivery_cycles WHERE cycle_id=?1",
                    [&cycle.cycle_id],
                    |r| Ok((r.get(0)?, r.get(1)?)),
                )
                .map_err(sql_error)?;
            if pf::parse(wire.as_bytes(), REQUEST_MAX)?
                != serde_json::to_value(cycle).map_err(|_| "delivery_corrupt")?
                || cycle_digest(cycle)? != digest
            {
                return Err("delivery_corrupt".into());
            }
        }
        if let Some(parent) = &batch.parent {
            let expiry:String=self.runtime.query_row("SELECT proof_expires_at FROM delivery_receipts WHERE batch_id=?1 AND terminal='rejected'",[&parent.batch_id],|r|r.get(0)).map_err(sql_error)?;
            if time(&expiry)? <= time(&db_now(&self.runtime)?)? {
                return Err("parent_proof_expired".into());
            }
        }
        Ok(Frozen {
            batch,
            body,
            body_sha: sha,
            origin: settings.origin.clone().ok_or("target_missing")?,
            target_id: target,
            depth,
        })
    }
    fn recover_frozen(
        &mut self,
        batch: &str,
        settings: &DeliverySettings,
    ) -> LocalResult<Option<Frozen>> {
        match self.frozen(batch, settings) {
            Ok(f) => Ok(Some(f)),
            Err(error) => {
                self.fail_delivery(
                    batch,
                    "needs_review",
                    error.split(':').next().unwrap_or("delivery_corrupt"),
                    1,
                    false,
                )?;
                Ok(None)
            }
        }
    }
    pub fn next_delivery_ready(&mut self, ready: Vec<String>) -> LocalResult<Option<Frozen>> {
        self.delivery_guard()?;
        let settings = self.delivery_settings()?;
        if settings.target_id.is_none() || settings.origin.is_none() {
            return Err("target_missing".into());
        }
        let (streak,latest_cursor,history_cursor):(u32,String,String)=self.runtime.query_row("SELECT latest_streak,latest_cursor,history_cursor FROM delivery_settings WHERE id=1",[],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).map_err(sql_error)?;
        let mut due = None;
        for batch in ready {
            let exists:bool=self.runtime.query_row("SELECT EXISTS(SELECT 1 FROM delivery_batches WHERE batch_id=?1 AND (state='prepared' OR state='unknown' OR state='retry_wait'))",[&batch],|r|r.get(0)).map_err(sql_error)?;
            if exists {
                due = Some(batch);
                break;
            }
        }
        let active:u32=self.runtime.query_row("SELECT count(*) FROM delivery_batches WHERE body IS NOT NULL AND state!='acknowledged' AND state!='rejected'",[],|r|r.get(0)).map_err(sql_error)?;
        let capacity = self.capacity(self.delivery_quota()?)?;
        if streak >= 3 || active >= 8 || !capacity.admission {
            if let Some(batch) = due.as_ref() {
                let frozen = self.recover_frozen(batch, &settings)?;
                self.runtime
                    .execute(
                        "UPDATE delivery_settings SET latest_streak=0 WHERE id=1",
                        [],
                    )
                    .map_err(sql_error)?;
                return Ok(frozen);
            }
            if active >= 8 || !capacity.admission {
                return Ok(None);
            }
        }
        let latest = streak < 3;
        let mut candidates = vec![];
        // At most four adopted PLCs, at most 32 group candidates per PLC: metadata bound is 128,
        // before ordering/rotation, so one fast group can never exclude another PLC.
        for source in &settings.sources {
            let groups=self.runtime.prepare("SELECT group_id FROM collection_cycles WHERE plc_id=?1 GROUP BY group_id ORDER BY group_id LIMIT 32").map_err(sql_error)?.query_map([&source.plc_id],|r|r.get::<_,String>(0)).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
            for group in groups {
                let sql=format!("SELECT c.id,c.plc_id,c.group_id,c.source_seq FROM collection_cycles c WHERE c.plc_id=?1 AND c.group_id=?2 AND EXISTS(SELECT 1 FROM samples s JOIN sample_delivery d ON d.sample_id=s.id WHERE s.cycle_id=c.id AND d.state='pending') AND NOT EXISTS(SELECT 1 FROM sample_references r JOIN samples s ON s.id=r.sample_id WHERE s.cycle_id=c.id AND r.reference_id=?3||c.id) AND (NOT EXISTS(SELECT 1 FROM delivery_cycles d WHERE d.cycle_id=c.id) OR EXISTS(SELECT 1 FROM delivery_parts p WHERE p.cycle_id=c.id AND p.state='pending')) ORDER BY c.source_seq {} LIMIT 1",if latest{"DESC"}else{"ASC"});
                let candidate = self
                    .runtime
                    .query_row(
                        &sql,
                        params![source.plc_id, group, "delivery-blocked:"],
                        |r| {
                            Ok((
                                r.get::<_, String>(0)?,
                                r.get::<_, String>(1)?,
                                r.get::<_, String>(2)?,
                                r.get::<_, i64>(3)?,
                            ))
                        },
                    )
                    .optional()
                    .map_err(sql_error)?;
                if let Some(c) = candidate {
                    candidates.push(c);
                }
            }
        }
        let cursor = if latest {
            latest_cursor
        } else {
            history_cursor
        };
        let rotation = crate::domain::local_delivery::Rotation::decode(&cursor);
        candidates.sort_by(|a, b| rotation.compare((&a.1, &a.2), (&b.1, &b.2)));
        let mut attempted = BTreeSet::new();
        for (cycle, plc, group, _) in candidates {
            if !attempted.insert((plc, group)) {
                continue;
            }
            let built = match self.build_delivery_cycle(&cycle) {
                Ok(b) => b,
                Err(e) => {
                    self.block_cycle(&cycle, &e, &settings)?;
                    continue;
                }
            };
            if !Self::source_admitted(&settings, &built) {
                self.block_cycle(&cycle, "source_adoption_required", &settings)?;
                continue;
            }
            match self.freeze_cycle(built, &settings, latest) {
                Ok(Some(f)) => return Ok(Some(f)),
                Ok(None) => {}
                Err(e) if e == "capacity_paused" => break,
                Err(e) => {
                    self.block_cycle(&cycle, &e, &settings)?;
                }
            }
        }
        if let Some(batch) = due {
            let frozen = self.recover_frozen(&batch, &settings)?;
            self.runtime
                .execute(
                    "UPDATE delivery_settings SET latest_streak=0 WHERE id=1",
                    [],
                )
                .map_err(sql_error)?;
            return Ok(frozen);
        }
        Ok(None)
    }
    pub fn mark_dispatch(&mut self, frozen: &Frozen) -> LocalResult<u32> {
        self.delivery_guard()?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let n=tx.execute("UPDATE delivery_batches SET state='inflight',attempt=min(attempt+1,2147483647) WHERE batch_id=?1 AND body_sha=?2 AND (state='prepared' OR state='unknown' OR state='retry_wait')",params![frozen.batch.batch_id,frozen.body_sha]).map_err(sql_error)?;
        if n != 1 {
            return Err("delivery_dispatch_conflict".into());
        }
        let attempt = tx
            .query_row(
                "SELECT attempt FROM delivery_batches WHERE batch_id=?1",
                [&frozen.batch.batch_id],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        event(&tx, "delivery_started", &frozen.batch.batch_id, "inflight")?;
        tx.commit().map_err(sql_error)?;
        self.log
            .event("delivery_started", &frozen.batch.batch_id, "inflight")?;
        Ok(attempt)
    }
    pub fn fail_delivery(
        &mut self,
        batch_id: &str,
        state: &str,
        error: &str,
        delay: u32,
        protocol: bool,
    ) -> LocalResult<bool> {
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let now = db_now(&tx)?;
        let next = (time(&now)? + chrono::Duration::seconds(i64::from(delay.clamp(1, 300))))
            .to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let readiness = ["not_ready", "clock_invalid"].contains(&error);
        tx.execute("UPDATE delivery_batches SET state=?1,last_error=?2,next_attempt_at=?3,protocol_failures=protocol_failures+?4,readiness_failures=readiness_failures+?5 WHERE batch_id=?6 AND state!='acknowledged' AND state!='rejected'",params![state,error,next,protocol,readiness,batch_id]).map_err(sql_error)?;
        let (p,r):(u32,u32)=tx.query_row("SELECT protocol_failures,readiness_failures FROM delivery_batches WHERE batch_id=?1",[batch_id],|r|Ok((r.get(0)?,r.get(1)?))).map_err(sql_error)?;
        if p >= 5 || r >= 5 {
            tx.execute(
                "UPDATE delivery_batches SET state='needs_review' WHERE batch_id=?1",
                [batch_id],
            )
            .map_err(sql_error)?;
        }
        event(
            &tx,
            if state == "unknown" {
                "delivery_unknown"
            } else {
                "delivery_retry_scheduled"
            },
            batch_id,
            error,
        )?;
        tx.commit().map_err(sql_error)?;
        self.log.event(
            if state == "unknown" {
                "delivery_unknown"
            } else {
                "delivery_retry_scheduled"
            },
            batch_id,
            error,
        )?;
        Ok(p >= 5 || r >= 5)
    }
}

impl Stores {
    pub fn sample_deliveries(&self, sample: &str) -> LocalResult<Vec<Value>> {
        if !self.delivery_available()? {
            return Ok(vec![]);
        }
        self.runtime.prepare("SELECT p.part,p.parts,p.state,p.batch_id,p.receipt_id,b.last_error FROM delivery_parts p LEFT JOIN delivery_batches b ON b.batch_id=p.batch_id WHERE p.sample_id=?1 ORDER BY p.part LIMIT 16").map_err(sql_error)?.query_map([sample],|r|Ok(json!({"part":r.get::<_,u32>(0)?,"parts":r.get::<_,u32>(1)?,"state":r.get::<_,String>(2)?,"batchId":r.get::<_,Option<String>>(3)?,"receiptId":r.get::<_,Option<String>>(4)?,"lastError":r.get::<_,Option<String>>(5)?}))).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)
    }
}

pub(super) fn cleanup_cycle(tx: &rusqlite::Transaction, cycle: &str) -> LocalResult<()> {
    let mut batches=tx.prepare("SELECT DISTINCT batch_id FROM delivery_parts WHERE cycle_id=?1 AND batch_id IS NOT NULL").map_err(sql_error)?.query_map([cycle],|r|r.get::<_,String>(0)).map_err(sql_error)?.collect::<std::result::Result<BTreeSet<_>,_>>().map_err(sql_error)?;
    let mut pending = batches.iter().cloned().collect::<Vec<_>>();
    while let Some(batch) = pending.pop() {
        let (state, parent): (String, Option<String>) = tx
            .query_row(
                "SELECT state,parent_id FROM delivery_batches WHERE batch_id=?1",
                [&batch],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(sql_error)?;
        if !["acknowledged", "rejected"].contains(&state.as_str()) {
            return Err("delivery_cleanup_referenced".into());
        }
        let refs: u32 = tx
            .query_row(
                "SELECT count(*) FROM sample_references WHERE reference_id=?1",
                [format!("delivery-batch:{batch}")],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if refs > 0 {
            return Err("delivery_cleanup_referenced".into());
        }
        if let Some(parent) = parent {
            if batches.insert(parent.clone()) {
                pending.push(parent)
            }
        }
        if batches.len() > 9 {
            return Err("delivery_cleanup_parent_depth".into());
        }
    }
    tx.execute("DELETE FROM delivery_parts WHERE cycle_id=?1", [cycle])
        .map_err(sql_error)?;
    tx.execute("DELETE FROM delivery_cycles WHERE cycle_id=?1", [cycle])
        .map_err(sql_error)?;
    for batch in batches {
        tx.execute("DELETE FROM delivery_receipts WHERE batch_id=?1", [&batch])
            .map_err(sql_error)?;
        tx.execute("DELETE FROM delivery_batches WHERE batch_id=?1", [batch])
            .map_err(sql_error)?;
    }
    Ok(())
}

impl Stores {
    pub fn delivery_events(&self, cursor: Option<i64>, limit: u32) -> LocalResult<Value> {
        self.delivery_guard()?;
        if ![10, 20, 50].contains(&limit) || cursor.map(|n| n <= 0).unwrap_or(false) {
            return Err("query_limits".into());
        }
        let rows=self.runtime.prepare("SELECT id,event,resource,result,created_at FROM delivery_events WHERE id<?1 ORDER BY id DESC LIMIT ?2").map_err(sql_error)?.query_map(params![cursor.unwrap_or(i64::MAX),limit],|r|Ok(json!({"order":r.get::<_,i64>(0)?,"event":r.get::<_,String>(1)?,"batchId":r.get::<_,String>(2)?,"state":r.get::<_,String>(3)?,"createdAt":r.get::<_,String>(4)?,"attempt":0,"lastError":Value::Null}))).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok(
            json!({"schemaVersion":1,"items":rows,"nextCursor":if rows.len()==limit as usize{rows.last().and_then(|r|r["order"].as_i64())}else{None}}),
        )
    }
    pub fn delivery_control_event(&mut self, event_key: &str, result: &str) -> LocalResult<()> {
        self.delivery_guard()?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        event(&tx, event_key, "target", result)?;
        tx.commit().map_err(sql_error)?;
        self.log.event(event_key, "target", result)
    }
}
