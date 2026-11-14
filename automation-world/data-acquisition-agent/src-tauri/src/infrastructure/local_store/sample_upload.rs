//! v2 冻结正文与可靠确认短事务；网络等待和操作员来源核对不在事务内。
use super::{sql_error, Stores};
use crate::domain::{
    facts_canonical as pf,
    local_configuration::LocalResult,
    sample_upload::{
        self, Binding, Reply, ReportingBinding, ReportingIdentity, Settings, BODY_LIMIT, CONTRACT,
    },
};
use rusqlite::{params, Connection, OptionalExtension};
use std::collections::{BTreeSet, VecDeque};

pub(super) const SQL: &str = r#"
CREATE TABLE sample_upload_settings(id INTEGER PRIMARY KEY CHECK(id=1),settings_revision TEXT NOT NULL,origin TEXT,path TEXT NOT NULL,interval_seconds INTEGER NOT NULL CHECK(interval_seconds BETWEEN 1 AND 3600));
CREATE TABLE sample_uploads(sample_id TEXT PRIMARY KEY REFERENCES samples(id),instance_id TEXT NOT NULL,plc_id TEXT NOT NULL,db_number INTEGER NOT NULL,source_generation TEXT NOT NULL,contract TEXT NOT NULL,origin TEXT,body TEXT,body_sha TEXT,state TEXT NOT NULL CHECK(state IN ('prepared','inflight','unknown','needs_processing','acknowledged')),attempt INTEGER NOT NULL DEFAULT 0,next_attempt_at TEXT NOT NULL,last_error TEXT,dispatched_at TEXT,acknowledged_at TEXT,receipt TEXT,receipt_sha TEXT);
CREATE INDEX sample_upload_dispatch ON sample_uploads(origin,plc_id,db_number,source_generation,state,next_attempt_at);
CREATE TABLE sample_upload_source_blocks(origin TEXT NOT NULL,instance_id TEXT NOT NULL,plc_id TEXT NOT NULL,source_generation TEXT NOT NULL,reason TEXT NOT NULL,PRIMARY KEY(origin,instance_id,plc_id,source_generation));
CREATE TABLE sample_upload_attempts(sample_id TEXT NOT NULL REFERENCES sample_uploads(sample_id) ON DELETE CASCADE,attempt INTEGER NOT NULL,target_url TEXT NOT NULL,started_at TEXT NOT NULL,PRIMARY KEY(sample_id,attempt));
CREATE TABLE sample_upload_rebindings(id INTEGER PRIMARY KEY,sample_id TEXT NOT NULL REFERENCES sample_uploads(sample_id) ON DELETE CASCADE,old_url TEXT NOT NULL,new_url TEXT NOT NULL,confirmed_at TEXT NOT NULL);
"#;

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Frozen {
    pub sample_id: String,
    pub instance_id: String,
    pub plc_id: String,
    pub db_number: u16,
    pub source_generation: String,
    pub origin: String,
    pub body: String,
    pub body_sha: String,
}

/// 无标记表示旧格式记录，空标记表示采样时尚未绑定，仅保存在本地。
fn cycle_reporting(
    c: &Connection,
    cycle: &str,
    sample: &crate::domain::local_sample::SamplePayload,
) -> LocalResult<Option<ReportingIdentity>> {
    let extended: bool = c.query_row("SELECT EXISTS(SELECT 1 FROM sqlite_schema WHERE type='table' AND name='reporting_cycles')", [], |r| r.get(0)).map_err(sql_error)?;
    let row: Option<(Option<String>, Option<String>, Option<String>)> = if extended {
        c.query_row(
            "SELECT instance_id,plc_id,source_generation FROM reporting_cycles WHERE cycle_id=?1",
            [cycle],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .optional()
        .map_err(sql_error)?
    } else {
        None
    };
    match row {
        None => Ok(Some(ReportingIdentity {
            instance_id: sample.instance_id.clone(),
            plc_id: sample.plc_id.clone(),
            source_generation: sample.source_generation.clone(),
        })),
        Some((None, None, None)) => Ok(None),
        Some((Some(instance_id), Some(plc_id), Some(source_generation)))
            if [&instance_id, &plc_id, &source_generation]
                .iter()
                .all(|v| crate::domain::facts_wire::id(v)) =>
        {
            Ok(Some(ReportingIdentity {
                instance_id,
                plc_id,
                source_generation,
            }))
        }
        _ => Err("profile_ledger_invalid".into()),
    }
}

impl Stores {
    pub fn recover_sample_upload(&mut self) -> LocalResult<()> {
        let at = super::delivery::db_now(&self.runtime)?;
        recover(&mut self.runtime, &at)
    }
    pub fn list_sample_uploads(
        &self,
        cursor: Option<i64>,
        limit: u32,
        state: Option<&str>,
    ) -> LocalResult<serde_json::Value> {
        if ![10, 20, 50].contains(&limit)
            || cursor.map(|n| n <= 0).unwrap_or(false)
            || state
                .map(|s| !["pending", "unknown", "needs_processing", "acknowledged"].contains(&s))
                .unwrap_or(false)
        {
            return Err("query_limits".into());
        }
        let sql = "SELECT s.sample_order,s.id,s.plc_id,s.db_number,c.started_at,coalesce(u.state,'pending'),coalesce(u.attempt,0),u.last_error FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN sample_delivery d ON d.sample_id=s.id LEFT JOIN sample_uploads u ON u.sample_id=s.id LEFT JOIN reporting_cycles rc ON rc.cycle_id=c.id WHERE s.sample_order<?1 AND (u.sample_id IS NOT NULL OR d.state='pending') AND (rc.cycle_id IS NULL OR rc.instance_id IS NOT NULL) AND (?2 IS NULL OR CASE WHEN u.state IN ('inflight','unknown') THEN 'unknown' WHEN u.state='prepared' OR u.state IS NULL THEN 'pending' ELSE u.state END = ?2) ORDER BY s.sample_order DESC LIMIT ?3";
        let rows = self.runtime.prepare(sql).map_err(sql_error)?.query_map(params![cursor.unwrap_or(i64::MAX),state,limit], |r| Ok(serde_json::json!({"order":r.get::<_,i64>(0)?,"batchId":r.get::<_,String>(1)?,"plcId":r.get::<_,String>(2)?,"dbNumber":r.get::<_,u16>(3)?,"createdAt":r.get::<_,String>(4)?,"state":r.get::<_,String>(5)?,"attempt":r.get::<_,u32>(6)?,"lastError":r.get::<_,Option<String>>(7)?}))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok(
            serde_json::json!({"schemaVersion":1,"nextCursor":if rows.len()==limit as usize {rows.last().and_then(|r|r["order"].as_i64())} else {None},"items":rows}),
        )
    }

    pub fn get_sample_upload(&self, sample_id: &str) -> LocalResult<serde_json::Value> {
        let row: Option<(String,u16,String,String,Option<String>,Option<String>,Option<String>,Option<String>,Option<String>,u32)> = self.runtime.query_row("SELECT s.plc_id,s.db_number,c.started_at,coalesce(u.state,'pending'),u.origin,u.body,u.body_sha,u.receipt,u.last_error,coalesce(u.attempt,0) FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN sample_delivery d ON d.sample_id=s.id LEFT JOIN sample_uploads u ON u.sample_id=s.id WHERE s.id=?1 AND (u.sample_id IS NOT NULL OR d.state='pending')", [sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?,r.get(7)?,r.get(8)?,r.get(9)?))).optional().map_err(sql_error)?;
        let (plc, db, at, state, origin, body, sha, receipt, error, attempt) =
            row.ok_or("sample_missing")?;
        let attempts = self.runtime.prepare("SELECT attempt,target_url,started_at FROM sample_upload_attempts WHERE sample_id=?1 ORDER BY attempt").map_err(sql_error)?.query_map([sample_id], |r| Ok(serde_json::json!({"attempt":r.get::<_,u32>(0)?,"url":r.get::<_,String>(1)?,"startedAt":r.get::<_,String>(2)?}))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        let rebindings = self.runtime.prepare("SELECT old_url,new_url,confirmed_at FROM sample_upload_rebindings WHERE sample_id=?1 ORDER BY id").map_err(sql_error)?.query_map([sample_id], |r| Ok(serde_json::json!({"oldUrl":r.get::<_,String>(0)?,"newUrl":r.get::<_,String>(1)?,"confirmedAt":r.get::<_,String>(2)?}))).map_err(sql_error)?.collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok(
            serde_json::json!({"schemaVersion":1,"batchId":sample_id,"plcId":plc,"dbNumber":db,"createdAt":at,"state":state,"origin":origin,"body":body,"bodySha256":sha,"receipt":receipt,"lastError":error,"attempt":attempt,"attempts":attempts,"rebindings":rebindings}),
        )
    }

    pub fn sample_upload_snapshot(&self, running: bool) -> LocalResult<serde_json::Value> {
        let pending = pending_usage(&self.runtime)?.0;
        let (unknown, needs, acknowledged, last): (u64,u64,u64,Option<String>) = self.runtime.query_row("SELECT coalesce(sum(CASE WHEN state IN ('inflight','unknown') THEN 1 ELSE 0 END),0),coalesce(sum(CASE WHEN state='needs_processing' THEN 1 ELSE 0 END),0),coalesce(sum(CASE WHEN state='acknowledged' THEN 1 ELSE 0 END),0),max(acknowledged_at) FROM sample_uploads", [], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).map_err(sql_error)?;
        let history: u64 = self
            .runtime
            .query_row(
                "SELECT count(*) FROM sample_delivery WHERE state='acknowledged'",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        let reason: Option<String> = self.runtime.query_row("SELECT last_error FROM sample_uploads WHERE state='needs_processing' AND last_error IS NOT NULL ORDER BY rowid DESC LIMIT 1", [], |r| r.get(0)).optional().map_err(sql_error)?;
        let settings = self.sample_upload_settings()?;
        let state = if !running {
            "stopped"
        } else if needs > 0 {
            "needs_processing"
        } else if unknown > 0 {
            "unknown"
        } else {
            "running"
        };
        Ok(
            serde_json::json!({"schemaVersion":1,"available":true,"running":running,"state":state,"origin":settings.target()?,"pending":pending,"acknowledged":acknowledged,"historicalV1Acknowledged":history,"lastAcknowledgedAt":last,"needsReason":reason,"sampleCounts":{"pending":pending.saturating_sub(unknown).saturating_sub(needs),"unknown":unknown,"needsProcessing":needs,"acknowledged":acknowledged}}),
        )
    }

    pub fn confirm_sample_upload_sources(
        &mut self,
        origin: &str,
        bindings: &[Binding],
    ) -> LocalResult<()> {
        let tx = self.runtime.transaction().map_err(sql_error)?;
        for b in bindings {
            tx.execute("DELETE FROM sample_upload_source_blocks WHERE origin=?1 AND instance_id=?2 AND plc_id=?3 AND source_generation=?4", params![origin,b.instance_id,b.plc_id,b.source_generation]).map_err(sql_error)?;
            // 仅确证从未派发的冻结样本可随本次显式继续切换目标；正文和身份不变。
            tx.execute("UPDATE sample_uploads SET origin=?1 WHERE instance_id=?2 AND plc_id=?3 AND db_number=?4 AND source_generation=?5 AND state='prepared' AND attempt=0", params![origin,b.instance_id,b.plc_id,b.db_number,b.source_generation]).map_err(sql_error)?;
        }
        tx.commit().map_err(sql_error)
    }

    /// 自动启动不解除来源阻断或改写旧目标；向界面返回需人工核对的事实。
    pub fn automatic_delivery_needs_review(
        &self,
        target: &str,
        bindings: &[Binding],
    ) -> LocalResult<bool> {
        let other_target: bool = self.runtime.query_row(
            "SELECT EXISTS(SELECT 1 FROM sample_uploads WHERE origin IS NOT NULL AND origin<>?1 AND state IN ('prepared','inflight','unknown'))",
            [target], |r| r.get(0),
        ).map_err(sql_error)?;
        if other_target {
            return Ok(true);
        }
        for binding in bindings {
            let blocked: bool = self.runtime.query_row(
                "SELECT EXISTS(SELECT 1 FROM sample_upload_source_blocks WHERE origin=?1 AND instance_id=?2 AND plc_id=?3 AND source_generation=?4)",
                params![target,binding.instance_id,binding.plc_id,binding.source_generation], |r| r.get(0),
            ).map_err(sql_error)?;
            if blocked {
                return Ok(true);
            }
        }
        Ok(false)
    }

    pub fn mark_sample_upload_attempt(&mut self, frozen: &Frozen) -> LocalResult<u32> {
        let quota = self.delivery_quota()?;
        if !super::capacity::admit(&self.capacity(quota)?, quota, false) {
            return Err("capacity_paused".into());
        }
        let now = super::delivery::db_now(&self.runtime)?;
        mark_attempt(&mut self.runtime, frozen, &now)
    }

    /// 已选样本在最终派发前仍须满足本机 PLC 的开关。
    pub fn sample_upload_enabled(&self, sample_id: &str) -> LocalResult<bool> {
        self.runtime.query_row("SELECT EXISTS(SELECT 1 FROM samples s WHERE s.id=?1 AND NOT EXISTS(SELECT 1 FROM reporting_disabled off WHERE off.local_plc_id=s.plc_id))", [sample_id], |r| r.get(0)).map_err(sql_error)
    }

    pub fn record_sample_upload_response(
        &mut self,
        frozen: &Frozen,
        response: LocalResult<crate::infrastructure::facts_http::Response>,
        attempt: u32,
    ) -> LocalResult<(Reply, u32)> {
        let now = super::delivery::db_now(&self.runtime)?;
        let retry_after = response
            .as_ref()
            .ok()
            .and_then(|r| r.retry_after.as_deref());
        let delay = crate::domain::local_delivery::retry_delay(
            attempt,
            retry_after,
            (uuid::Uuid::new_v4().as_u128() % 21) as u32,
        );
        let next = (crate::domain::facts_wire::time(&now)?
            + chrono::Duration::seconds(i64::from(delay)))
        .to_rfc3339_opts(chrono::SecondsFormat::Millis, false);
        match response {
            Ok(r) => apply_for_attempt(
                &mut self.runtime,
                frozen,
                attempt,
                r.status,
                &r.media_type,
                &r.body,
                &now,
                &next,
            )
            .map(|reply| (reply, delay)),
            Err(_) => {
                let changed = self.runtime.execute("UPDATE sample_uploads SET state='unknown',last_error='transport_unknown',next_attempt_at=?1 WHERE sample_id=?2 AND instance_id=?3 AND plc_id=?4 AND db_number=?5 AND source_generation=?6 AND origin=?7 AND body=?8 AND body_sha=?9 AND attempt=?10 AND state='inflight' AND EXISTS(SELECT 1 FROM sample_upload_attempts a WHERE a.sample_id=sample_uploads.sample_id AND a.attempt=?10 AND a.target_url=?7)", params![next,frozen.sample_id,frozen.instance_id,frozen.plc_id,frozen.db_number,frozen.source_generation,frozen.origin,frozen.body,frozen.body_sha,attempt]).map_err(sql_error)?;
                if changed != 1 {
                    return Err("sample_response_conflict".into());
                }
                Ok((Reply::Retry("transport_unknown"), delay))
            }
        }
    }

    pub fn sample_upload_settings(&self) -> LocalResult<Settings> {
        let (settings_revision, origin, path, interval_seconds) = self.runtime.query_row("SELECT settings_revision,origin,path,interval_seconds FROM sample_upload_settings WHERE id=1", [], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).map_err(sql_error)?;
        let bindings = self.runtime.prepare("SELECT b.local_plc_id,g.instance_id,b.plc_id,b.source_generation FROM reporting_bindings b LEFT JOIN reporting_generations g ON g.plc_id=b.plc_id AND g.source_generation=b.source_generation AND g.local_plc_id=b.local_plc_id ORDER BY b.local_plc_id COLLATE BINARY").map_err(sql_error)?
            .query_map([], |r| Ok(ReportingBinding { local_plc_id:r.get(0)?,instance_id:r.get(1)?,plc_id:r.get(2)?,source_generation:r.get(3)? })).map_err(sql_error)?
            .collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        let disabled_local_plcs = self
            .runtime
            .prepare(
                "SELECT local_plc_id FROM reporting_disabled ORDER BY local_plc_id COLLATE BINARY",
            )
            .map_err(sql_error)?
            .query_map([], |r| r.get(0))
            .map_err(sql_error)?
            .collect::<Result<Vec<String>, _>>()
            .map_err(sql_error)?;
        let settings = Settings {
            schema_version: 1,
            settings_revision,
            origin,
            path,
            interval_seconds,
            identity_mode: "per_plc".into(),
            bindings,
            disabled_local_plcs,
        };
        settings.validate()?;
        Ok(settings)
    }

    pub fn save_sample_upload_settings(
        &mut self,
        mut settings: Settings,
        expected: String,
    ) -> LocalResult<Settings> {
        if let Some(origin) = &settings.origin {
            settings.origin = Some(sample_upload::upload_origin(origin)?);
        }
        let normalized = sample_upload::target_url(
            settings
                .origin
                .as_deref()
                .unwrap_or("http://example.invalid"),
            &settings.path,
        )?;
        let parsed = reqwest::Url::parse(&normalized).map_err(|_| "invalid_target")?;
        settings.path = parsed.path().to_string();
        settings.validate()?;
        settings.settings_revision = crate::domain::local_configuration::id();
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let n = tx.execute("UPDATE sample_upload_settings SET settings_revision=?1,origin=?2,path=?3,interval_seconds=?4 WHERE id=1 AND settings_revision=?5", params![settings.settings_revision,settings.origin,settings.path,settings.interval_seconds,expected]).map_err(sql_error)?;
        if n != 1 {
            return Err("delivery_settings_conflict".into());
        }
        for b in &settings.bindings {
            let generation: Option<String> = tx
                .query_row(
                    "SELECT generation FROM plc_sources WHERE plc_id=?1",
                    [&b.local_plc_id],
                    |r| r.get(0),
                )
                .optional()
                .map_err(sql_error)?;
            let generation = generation.ok_or("source_binding_unknown")?;
            let prior: Option<(String,String,String)> = tx.query_row("SELECT instance_id,local_plc_id,local_generation FROM reporting_generations WHERE plc_id=?1 AND source_generation=?2", params![b.plc_id,b.source_generation], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional().map_err(sql_error)?;
            let current = (b.instance_id.clone(), b.local_plc_id.clone(), generation);
            if prior.as_ref().map(|p| p != &current).unwrap_or(false) {
                return Err("source_generation_reuse".into());
            }
            tx.execute(
                "INSERT OR IGNORE INTO reporting_generations VALUES(?1,?2,?3,?4,?5)",
                params![
                    b.plc_id,
                    b.source_generation,
                    current.0,
                    current.1,
                    current.2
                ],
            )
            .map_err(sql_error)?;
        }
        // 旧程序只理解单一实例；混合实例时留空，使其全检在业务写入前拒绝。
        let shared_instance = settings.bindings.first().and_then(|first| {
            settings
                .bindings
                .iter()
                .all(|b| b.instance_id == first.instance_id)
                .then_some(first.instance_id.as_str())
        });
        tx.execute(
            "UPDATE reporting_identity SET instance_id=?1 WHERE id=1",
            [shared_instance],
        )
        .map_err(sql_error)?;
        tx.execute("DELETE FROM reporting_bindings", [])
            .map_err(sql_error)?;
        for b in &settings.bindings {
            tx.execute(
                "INSERT INTO reporting_bindings VALUES(?1,?2,?3)",
                params![b.local_plc_id, b.plc_id, b.source_generation],
            )
            .map_err(sql_error)?;
        }
        tx.execute("DELETE FROM reporting_disabled", [])
            .map_err(sql_error)?;
        for local_plc in &settings.disabled_local_plcs {
            let exists: bool = tx
                .query_row(
                    "SELECT EXISTS(SELECT 1 FROM plc_sources WHERE plc_id=?1)",
                    [local_plc],
                    |r| r.get(0),
                )
                .map_err(sql_error)?;
            if !exists {
                return Err("source_binding_unknown".into());
            }
            tx.execute(
                "INSERT INTO reporting_disabled(local_plc_id) VALUES(?1)",
                [local_plc],
            )
            .map_err(sql_error)?;
        }
        tx.commit().map_err(sql_error)?;
        Ok(settings)
    }

    /// 采样开始前获取当前映射；未绑定与旧版本分别保持本地或原身份语义。
    pub fn reporting_identity(&self, local_plc: &str) -> LocalResult<Option<ReportingIdentity>> {
        let version: u32 = self
            .runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)?;
        if version != 4 {
            return Ok(None);
        }
        self.runtime.query_row("SELECT g.instance_id,b.plc_id,b.source_generation FROM reporting_bindings b JOIN reporting_generations g ON g.plc_id=b.plc_id AND g.source_generation=b.source_generation AND g.local_plc_id=b.local_plc_id WHERE b.local_plc_id=?1", [local_plc], |r| Ok(ReportingIdentity { instance_id:r.get(0)?,plc_id:r.get(1)?,source_generation:r.get(2)? })).optional().map_err(sql_error)
    }

    pub fn reporting_local_sources(&self) -> LocalResult<Vec<serde_json::Value>> {
        let Some(revision) = self.configuration()?.active else {
            return Ok(vec![]);
        };
        let config = self.revision(&revision)?;
        Ok(config
            .plcs
            .iter()
            .map(|plc| {
                let dbs: BTreeSet<u16> = config
                    .dbs
                    .iter()
                    .filter(|db| {
                        db.plc_id == plc.id
                            && config
                                .points
                                .iter()
                                .any(|p| p.enabled && p.plc_id == plc.id && p.db_id == db.id)
                    })
                    .map(|db| db.number)
                    .collect();
                serde_json::json!({"localPlcId":plc.id,"name":plc.name,"dbNumbers":dbs})
            })
            .collect())
    }

    /// 操作员已在部署配置中核对同一 provider 和数据库后，才为指定未决样本登记新目标。
    pub fn rebind_sample_upload(
        &mut self,
        sample_id: &str,
        old_url: &str,
        new_url: &str,
        expected: &str,
        bindings: &[Binding],
    ) -> LocalResult<()> {
        let settings = self.sample_upload_settings()?;
        if settings.settings_revision != expected
            || settings.target()?.as_deref() != Some(new_url)
            || sample_upload::normalize_target(old_url)? != old_url
            || old_url == new_url
        {
            return Err("delivery_settings_conflict".into());
        }
        // 该方法在 storage actor 内执行；完整来源重验和重绑写入不能被新采样插队。
        if self.sample_upload_bindings()? != bindings {
            return Err("source_confirmation_changed".into());
        }
        let quota = self.delivery_quota()?;
        if !super::capacity::admit(&self.capacity(quota)?, quota, false) {
            return Err("capacity_paused".into());
        }
        let at = super::delivery::db_now(&self.runtime)?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let row: Option<(String,String,u16,String)> = tx.query_row("SELECT instance_id,plc_id,db_number,source_generation FROM sample_uploads WHERE sample_id=?1 AND origin=?2 AND state='unknown' AND attempt>0 AND body IS NOT NULL AND body_sha IS NOT NULL", params![sample_id,old_url], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).optional().map_err(sql_error)?;
        let (instance_id, plc_id, db_number, source_generation) =
            row.ok_or("sample_rebind_not_available")?;
        if !bindings.contains(&Binding {
            instance_id,
            plc_id,
            db_number,
            source_generation,
        }) {
            return Err("source_confirmation_changed".into());
        }
        let n = tx.execute("UPDATE sample_uploads SET origin=?1 WHERE sample_id=?2 AND origin=?3 AND state='unknown' AND attempt>0", params![new_url,sample_id,old_url]).map_err(sql_error)?;
        if n != 1 {
            return Err("sample_rebind_not_available".into());
        }
        tx.execute("INSERT INTO sample_upload_rebindings(sample_id,old_url,new_url,confirmed_at) VALUES(?1,?2,?3,?4)", params![sample_id,old_url,new_url,at]).map_err(sql_error)?;
        tx.commit().map_err(sql_error)
    }

    /// 当前来源和历史待处理来源取并集；操作者须对照实际目标登记后才能启动。
    pub fn sample_upload_bindings(&self) -> LocalResult<Vec<Binding>> {
        let mut result = BTreeSet::new();
        let mut q = self.runtime.prepare("SELECT DISTINCT coalesce(rc.instance_id,?1),coalesce(rc.plc_id,s.plc_id),s.db_number,coalesce(rc.source_generation,c.generation) FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN sample_delivery d ON d.sample_id=s.id LEFT JOIN sample_uploads u ON u.sample_id=s.id LEFT JOIN reporting_cycles rc ON rc.cycle_id=c.id WHERE d.state='pending' AND (u.sample_id IS NULL OR u.state!='acknowledged') AND (rc.cycle_id IS NULL OR rc.instance_id IS NOT NULL) LIMIT 129").map_err(sql_error)?;
        for row in q
            .query_map([&self.instance], |r| {
                Ok((
                    r.get::<_, String>(0)?,
                    r.get::<_, String>(1)?,
                    r.get::<_, u16>(2)?,
                    r.get::<_, String>(3)?,
                ))
            })
            .map_err(sql_error)?
        {
            result.insert(row.map_err(sql_error)?);
        }
        if result.len() > 128 {
            return Err("source_binding_limits".into());
        }
        if let Some(revision) = self.configuration()?.active {
            let config = self.revision(&revision)?;
            for db in &config.dbs {
                if !config
                    .points
                    .iter()
                    .any(|p| p.enabled && p.plc_id == db.plc_id && p.db_id == db.id)
                {
                    continue;
                }
                if let Some(source) = self.reporting_identity(&db.plc_id)? {
                    result.insert((
                        source.instance_id,
                        source.plc_id,
                        db.number,
                        source.source_generation,
                    ));
                }
            }
        }
        if result.len() > 128 {
            return Err("source_binding_limits".into());
        }
        Ok(result
            .into_iter()
            .map(
                |(instance_id, plc_id, db_number, source_generation)| Binding {
                    instance_id,
                    plc_id,
                    db_number,
                    source_generation,
                },
            )
            .collect())
    }

    fn mark_sample_review(
        &mut self,
        sample: &crate::domain::local_sample::SamplePayload,
        source: &ReportingIdentity,
        origin: &str,
        at: &str,
        reason: &str,
    ) -> LocalResult<()> {
        self.runtime.execute("INSERT INTO sample_uploads(sample_id,instance_id,plc_id,db_number,source_generation,contract,origin,state,next_attempt_at,last_error) VALUES(?1,?2,?3,?4,?5,?6,?7,'needs_processing',?8,?9)", params![sample.sample_id,source.instance_id,source.plc_id,sample.db_number,source.source_generation,CONTRACT,origin,at,reason]).map_err(sql_error)?;
        Ok(())
    }

    /// 每次最多检查八个不合格候选；每个候选仅绑定已确认的目标与来源。
    #[cfg(test)]
    pub fn next_sample_upload(
        &mut self,
        origin: &str,
        bindings: &[Binding],
        latest: bool,
    ) -> LocalResult<Option<Frozen>> {
        self.next_sample_upload_ready(origin, bindings, latest, &[])
    }

    pub fn sample_retry_schedule(&self) -> LocalResult<(String, Vec<(String, String)>)> {
        let now = super::delivery::db_now(&self.runtime)?;
        let rows = self.runtime.prepare("SELECT sample_id,next_attempt_at FROM sample_uploads WHERE state='unknown' ORDER BY sample_id").map_err(sql_error)?
            .query_map([], |r| Ok((r.get(0)?,r.get(1)?))).map_err(sql_error)?
            .collect::<Result<Vec<_>,_>>().map_err(sql_error)?;
        Ok((now, rows))
    }

    pub fn next_sample_upload_ready(
        &mut self,
        origin: &str,
        bindings: &[Binding],
        latest: bool,
        waiting: &[String],
    ) -> LocalResult<Option<Frozen>> {
        use crate::domain::local_sample::{digest, CycleManifest, SamplePayload};
        if sample_upload::normalize_target(origin)? != origin || bindings.len() > 128 {
            return Err("invalid_target".into());
        }
        let at = super::delivery::db_now(&self.runtime)?;
        self.runtime.execute_batch("CREATE TEMP TABLE IF NOT EXISTS sample_retry_wait(sample_id TEXT PRIMARY KEY); DELETE FROM sample_retry_wait;").map_err(sql_error)?;
        {
            let tx = self.runtime.transaction().map_err(sql_error)?;
            {
                let mut insert = tx
                    .prepare("INSERT INTO sample_retry_wait VALUES(?1)")
                    .map_err(sql_error)?;
                for id in waiting {
                    insert.execute([id]).map_err(sql_error)?;
                }
            }
            tx.commit().map_err(sql_error)?;
        }
        for _ in 0..8 {
            let mut selected: Option<(String, i64)> = None;
            for binding in bindings {
                let direction = if latest { "DESC" } else { "ASC" };
                let query = format!("SELECT s.id,s.sample_order FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN sample_delivery d ON d.sample_id=s.id LEFT JOIN sample_uploads u ON u.sample_id=s.id LEFT JOIN reporting_cycles rc ON rc.cycle_id=c.id WHERE coalesce(rc.plc_id,s.plc_id)=?1 AND s.db_number=?2 AND coalesce(rc.source_generation,c.generation)=?3 AND coalesce(rc.instance_id,?5)=?6 AND (rc.cycle_id IS NULL OR rc.instance_id IS NOT NULL) AND d.state='pending' AND ((u.sample_id IS NULL) OR (u.origin=?4 AND u.state IN ('prepared','unknown'))) AND NOT EXISTS(SELECT 1 FROM reporting_disabled off WHERE off.local_plc_id=s.plc_id) AND NOT EXISTS(SELECT 1 FROM sample_retry_wait w WHERE w.sample_id=s.id) AND NOT EXISTS(SELECT 1 FROM sample_upload_source_blocks b WHERE b.origin=?4 AND b.instance_id=?6 AND b.plc_id=?1 AND b.source_generation=?3) ORDER BY s.sample_order {direction} LIMIT 1");
                let row: Option<(String, i64)> = self
                    .runtime
                    .query_row(
                        &query,
                        params![
                            binding.plc_id,
                            binding.db_number,
                            binding.source_generation,
                            origin,
                            self.instance,
                            binding.instance_id
                        ],
                        |r| Ok((r.get(0)?, r.get(1)?)),
                    )
                    .optional()
                    .map_err(sql_error)?;
                if let Some(row) = row {
                    if selected
                        .as_ref()
                        .map(|x| if latest { row.1 > x.1 } else { row.1 < x.1 })
                        .unwrap_or(true)
                    {
                        selected = Some(row);
                    }
                }
            }
            let Some((id, _)) = selected else {
                return Ok(None);
            };
            let existing: Option<(String,String,String,u16,String,String,String)> = self.runtime.query_row("SELECT instance_id,plc_id,source_generation,db_number,origin,body,body_sha FROM sample_uploads WHERE sample_id=?1", [&id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?))).optional().map_err(sql_error)?;
            if let Some((
                instance_id,
                plc_id,
                source_generation,
                db_number,
                origin,
                body,
                body_sha,
            )) = existing
            {
                if pf::sha(body.as_bytes()) != body_sha {
                    return Err("sample_frozen_invalid".into());
                }
                return Ok(Some(Frozen {
                    sample_id: id,
                    instance_id,
                    plc_id,
                    db_number,
                    source_generation,
                    origin,
                    body,
                    body_sha,
                }));
            }
            let (raw,sha,cycle,manifest,mhash,context,chash): (String,String,String,String,String,String,String) = self.runtime.query_row("SELECT s.payload,s.sha256,s.cycle_id,c.manifest,c.sha256,x.payload,x.sha256 FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN configuration_contexts x ON x.revision=s.revision WHERE s.id=?1", [&id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?))).map_err(sql_error)?;
            if digest(&raw) != sha || digest(&manifest) != mhash || digest(&context) != chash {
                return Err("payload_corrupt".into());
            }
            let sample: SamplePayload =
                serde_json::from_value(super::profile_contract::local_json(&raw, 2 * 1024 * 1024)?)
                    .map_err(|_| "payload_corrupt")?;
            let manifest: CycleManifest =
                serde_json::from_value(super::profile_contract::local_json(&manifest, 512 * 1024)?)
                    .map_err(|_| "payload_corrupt")?;
            let config = serde_json::from_value(super::profile_contract::local_json(
                &context,
                16 * 1024 * 1024,
            )?)
            .map_err(|_| "payload_corrupt")?;
            let source =
                cycle_reporting(&self.runtime, &cycle, &sample)?.ok_or("source_not_bound")?;
            let reason = match legacy_status(&self.runtime, &id, &cycle)? {
                LegacyStatus::NeverSent => None,
                _ => Some("legacy_reconciliation_required"),
            };
            if let Some(reason) = reason {
                self.mark_sample_review(&sample, &source, origin, &at, reason)?;
                continue;
            }
            let body = match sample_upload::deadline(&sample).and_then(|deadline| {
                if deadline <= crate::domain::facts_wire::time(&at)? {
                    return Err("expired_unconfirmed".into());
                }
                sample_upload::build_with_identity(
                    &sample,
                    &sha,
                    &manifest,
                    &config,
                    &self.instance,
                    Some(&source),
                )
            }) {
                Ok(body) => body,
                Err(reason) => {
                    self.mark_sample_review(&sample, &source, origin, &at, &reason)?;
                    continue;
                }
            };
            let quota = self.delivery_quota()?;
            if !super::capacity::admit(&self.capacity(quota)?, quota, false) {
                return Err("capacity_paused".into());
            }
            let f = Frozen {
                sample_id: id,
                instance_id: source.instance_id,
                plc_id: source.plc_id,
                db_number: sample.db_number,
                source_generation: source.source_generation,
                origin: origin.into(),
                body_sha: pf::sha(body.as_bytes()),
                body,
            };
            freeze(&mut self.runtime, &f, &at)?;
            return Ok(Some(f));
        }
        Ok(None)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(super) enum LegacyStatus {
    NeverSent,
    HistoricalAcknowledged,
    NeedsReview,
}

pub(super) fn pending_usage(c: &Connection) -> LocalResult<(u64, u64, Option<String>)> {
    c.query_row("SELECT count(*),coalesce(sum(s.payload_bytes),0),min(s.saved_at) FROM samples s JOIN sample_delivery d ON d.sample_id=s.id LEFT JOIN sample_uploads u ON u.sample_id=s.id LEFT JOIN reporting_cycles rc ON rc.cycle_id=s.cycle_id WHERE (rc.cycle_id IS NULL OR rc.instance_id IS NOT NULL) AND ((u.sample_id IS NOT NULL AND u.state!='acknowledged') OR (u.sample_id IS NULL AND d.state='pending'))", [], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).map_err(sql_error)
}

/// 基于旧账本全部关联判断：不能从 pending 或缺少回执推断未发。
/// 调用前须在锁下完成旧版本 schema、引用与原字节全检。
pub(super) fn legacy_status(
    c: &Connection,
    sample: &str,
    cycle: &str,
) -> LocalResult<LegacyStatus> {
    let state: String = c
        .query_row(
            "SELECT state FROM sample_delivery WHERE sample_id=?1",
            [sample],
            |r| r.get(0),
        )
        .map_err(sql_error)?;
    let parts: Vec<(i64, i64, String, Option<String>, Option<String>)> = c.prepare("SELECT part,parts,state,batch_id,receipt_id FROM delivery_parts WHERE sample_id=?1 ORDER BY part").map_err(sql_error)?
        .query_map([sample], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).map_err(sql_error)?
        .collect::<Result<_,_>>().map_err(sql_error)?;
    if !parts.is_empty()
        && parts.iter().enumerate().any(|(i, (part, total, _, _, _))| {
            *part != (i + 1) as i64 || *total != parts.len() as i64
        })
    {
        return Ok(LegacyStatus::NeedsReview);
    }
    if state == "acknowledged" {
        if parts.is_empty() {
            return Ok(LegacyStatus::NeedsReview);
        }
        for (_, _, state, batch, receipt) in &parts {
            let (Some(batch), Some(receipt)) = (batch, receipt) else {
                return Ok(LegacyStatus::NeedsReview);
            };
            let present: bool = c.query_row("SELECT EXISTS(SELECT 1 FROM delivery_receipts WHERE batch_id=?1 AND receipt_id=?2 AND terminal='acknowledged')", params![batch,receipt], |r| r.get(0)).map_err(sql_error)?;
            if state != "acknowledged" || !present {
                return Ok(LegacyStatus::NeedsReview);
            }
        }
        return Ok(LegacyStatus::HistoricalAcknowledged);
    }
    if state != "pending"
        || parts.iter().any(|(_, _, state, batch, receipt)| {
            receipt.is_some()
                || !((state == "pending" && batch.is_none())
                    || (state == "prepared" && batch.is_some()))
        })
    {
        return Ok(LegacyStatus::NeedsReview);
    }
    let cycle_frozen: bool = c
        .query_row(
            "SELECT EXISTS(SELECT 1 FROM delivery_cycles WHERE cycle_id=?1)",
            [cycle],
            |r| r.get(0),
        )
        .map_err(sql_error)?;
    if cycle_frozen && parts.is_empty() {
        return Ok(LegacyStatus::NeedsReview);
    }
    let mut pending: VecDeque<String> = parts
        .iter()
        .filter_map(|(_, _, _, id, _)| id.clone())
        .collect();
    // 部分诊断记录只有 members 而没有 parts；先筛候选，再精确检查 JSON 字符串。
    let mut query = c.prepare("SELECT batch_id,members FROM delivery_batches WHERE instr(members,?1)>0 OR instr(members,?2)>0 LIMIT 10001").map_err(sql_error)?;
    let rows = query
        .query_map(params![sample, cycle], |r| {
            Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?))
        })
        .map_err(sql_error)?;
    let mut scanned = 0;
    for row in rows {
        let (id, raw) = row.map_err(sql_error)?;
        scanned += 1;
        if scanned > 10000 {
            return Ok(LegacyStatus::NeedsReview);
        }
        let members = match super::profile_contract::local_json(&raw, 4 * 1024 * 1024) {
            Ok(value) => value,
            Err(_) => return Ok(LegacyStatus::NeedsReview),
        };
        fn contains(v: &serde_json::Value, id: &str) -> bool {
            match v {
                serde_json::Value::String(s) => s == id,
                serde_json::Value::Array(a) => a.iter().any(|v| contains(v, id)),
                serde_json::Value::Object(m) => m.values().any(|v| contains(v, id)),
                _ => false,
            }
        }
        if contains(&members, sample) || contains(&members, cycle) {
            pending.push_back(id);
        }
    }
    drop(query);
    let mut seen = BTreeSet::new();
    while let Some(id) = pending.pop_front() {
        if !seen.insert(id.clone()) {
            continue;
        }
        if seen.len() > 10000 {
            return Ok(LegacyStatus::NeedsReview);
        }
        let row: Option<(String, i64, Option<String>)> = c
            .query_row(
                "SELECT state,attempt,parent_id FROM delivery_batches WHERE batch_id=?1",
                [&id],
                |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
            )
            .optional()
            .map_err(sql_error)?;
        let Some((state, attempt, parent)) = row else {
            return Ok(LegacyStatus::NeedsReview);
        };
        let receipt: bool = c
            .query_row(
                "SELECT EXISTS(SELECT 1 FROM delivery_receipts WHERE batch_id=?1)",
                [&id],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if state != "prepared" || attempt != 0 || receipt {
            return Ok(LegacyStatus::NeedsReview);
        }
        if let Some(parent) = parent {
            pending.push_back(parent);
        }
        let children: Vec<String> = c
            .prepare("SELECT batch_id FROM delivery_batches WHERE parent_id=?1 LIMIT 10001")
            .map_err(sql_error)?
            .query_map([&id], |r| r.get(0))
            .map_err(sql_error)?
            .collect::<Result<_, _>>()
            .map_err(sql_error)?;
        if children.len() > 10000 {
            return Ok(LegacyStatus::NeedsReview);
        }
        pending.extend(children);
    }
    Ok(LegacyStatus::NeverSent)
}

/// 按稳定主键分页检查 v4 原正文、固定目标、尝试和回执；不修改任何材料。
pub(super) fn full_check(c: &Connection, instance: &str) -> LocalResult<()> {
    use crate::domain::local_sample::{digest, CycleManifest, SamplePayload};
    let extended: bool = c.query_row("SELECT EXISTS(SELECT 1 FROM sqlite_schema WHERE type='table' AND name='reporting_cycles')", [], |r| r.get(0)).map_err(sql_error)?;
    let has_switches: bool = c.query_row("SELECT EXISTS(SELECT 1 FROM sqlite_schema WHERE type='table' AND name='reporting_disabled')", [], |r| r.get(0)).map_err(sql_error)?;
    if has_switches {
        let ids: Vec<String> = c
            .prepare("SELECT local_plc_id FROM reporting_disabled LIMIT 129")
            .map_err(sql_error)?
            .query_map([], |r| r.get(0))
            .map_err(sql_error)?
            .collect::<Result<_, _>>()
            .map_err(sql_error)?;
        if ids.len() > 128
            || ids
                .iter()
                .any(|id| !crate::domain::local_configuration::valid_id(id))
        {
            return Err("profile_ledger_invalid".into());
        }
    }
    if extended {
        let rows: Vec<(Option<String>,)> = c
            .prepare("SELECT instance_id FROM reporting_identity WHERE id=1")
            .map_err(sql_error)?
            .query_map([], |r| Ok((r.get(0)?,)))
            .map_err(sql_error)?
            .collect::<Result<_, _>>()
            .map_err(sql_error)?;
        let all: i64 = c
            .query_row("SELECT count(*) FROM reporting_identity", [], |r| r.get(0))
            .map_err(sql_error)?;
        if all != 1
            || rows.len() != 1
            || rows[0]
                .0
                .as_deref()
                .map(|v| !crate::domain::facts_wire::id(v))
                .unwrap_or(false)
        {
            return Err("profile_ledger_invalid".into());
        }
        let mut local = BTreeSet::new();
        let mut remote = BTreeSet::new();
        let mut instances = BTreeSet::new();
        let mut q = c.prepare("SELECT local_plc_id,plc_id,source_generation FROM reporting_bindings ORDER BY local_plc_id COLLATE BINARY").map_err(sql_error)?;
        let bindings = q
            .query_map([], |r| {
                Ok((
                    r.get::<_, String>(0)?,
                    r.get::<_, String>(1)?,
                    r.get::<_, String>(2)?,
                ))
            })
            .map_err(sql_error)?;
        for b in bindings {
            let (local_id, plc, generation) = b.map_err(sql_error)?;
            let binding_instance: Option<String> = c.query_row("SELECT g.instance_id FROM plc_sources p JOIN reporting_generations g ON g.local_plc_id=p.plc_id AND g.local_generation=p.generation WHERE p.plc_id=?1 AND g.plc_id=?2 AND g.source_generation=?3", params![local_id,plc,generation], |r| r.get(0)).optional().map_err(sql_error)?;
            if binding_instance
                .as_deref()
                .map(crate::domain::facts_wire::id)
                != Some(true)
                || !crate::domain::local_configuration::valid_id(&local_id)
                || !crate::domain::facts_wire::id(&plc)
                || !crate::domain::facts_wire::id(&generation)
                || !local.insert(local_id)
                || !remote.insert(plc)
                || remote.len() > 128
            {
                return Err("profile_ledger_invalid".into());
            }
            instances.insert(binding_instance.unwrap());
        }
        if (!instances.is_empty()
            && instances.len() == 1
            && rows[0].0.as_ref() != instances.first())
            || (instances.len() > 1 && rows[0].0.is_some())
        {
            return Err("profile_ledger_invalid".into());
        }
        let mut q = c.prepare("SELECT g.plc_id,g.source_generation,g.instance_id,g.local_plc_id,g.local_generation,p.generation FROM reporting_generations g LEFT JOIN plc_sources p ON p.plc_id=g.local_plc_id").map_err(sql_error)?;
        for row in q
            .query_map([], |r| {
                Ok((
                    r.get::<_, String>(0)?,
                    r.get::<_, String>(1)?,
                    r.get::<_, String>(2)?,
                    r.get::<_, String>(3)?,
                    r.get::<_, String>(4)?,
                    r.get::<_, Option<String>>(5)?,
                ))
            })
            .map_err(sql_error)?
        {
            let (plc, generation, inst, local_id, local_generation, current) =
                row.map_err(sql_error)?;
            if [&plc, &generation, &inst]
                .iter()
                .any(|v| !crate::domain::facts_wire::id(v))
                || !crate::domain::local_configuration::valid_id(&local_id)
                || !crate::domain::local_configuration::valid_id(&local_generation)
                || current.as_deref() != Some(&local_generation)
            {
                return Err("profile_ledger_invalid".into());
            }
        }
        let invalid: bool = c.query_row("SELECT EXISTS(SELECT 1 FROM reporting_cycles r LEFT JOIN collection_cycles c ON c.id=r.cycle_id WHERE c.id IS NULL)", [], |r| r.get(0)).map_err(sql_error)?;
        if invalid {
            return Err("profile_ledger_invalid".into());
        }
        let mut q = c.prepare("SELECT r.instance_id,r.plc_id,r.source_generation,c.plc_id,c.generation FROM reporting_cycles r JOIN collection_cycles c ON c.id=r.cycle_id").map_err(sql_error)?;
        for row in q
            .query_map([], |r| {
                Ok((
                    r.get::<_, Option<String>>(0)?,
                    r.get::<_, Option<String>>(1)?,
                    r.get::<_, Option<String>>(2)?,
                    r.get::<_, String>(3)?,
                    r.get::<_, String>(4)?,
                ))
            })
            .map_err(sql_error)?
        {
            match row.map_err(sql_error)? {
                (None,None,None,_,_) => (),
                (Some(i),Some(p),Some(g),local_id,local_generation) if [&i,&p,&g].iter().all(|v| crate::domain::facts_wire::id(v)) && c.query_row("SELECT EXISTS(SELECT 1 FROM reporting_generations WHERE plc_id=?1 AND source_generation=?2 AND instance_id=?3 AND local_plc_id=?4 AND local_generation=?5)", params![p,g,i,local_id,local_generation], |r| r.get::<_,bool>(0)).map_err(sql_error)? => (),
                _ => return Err("profile_ledger_invalid".into()),
            }
        }
    }
    let (revision, origin, path, interval): (String, Option<String>, String, u32) = c.query_row("SELECT settings_revision,origin,path,interval_seconds FROM sample_upload_settings WHERE id=1", [], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).map_err(sql_error)?;
    let settings_count: i64 = c
        .query_row("SELECT count(*) FROM sample_upload_settings", [], |r| {
            r.get(0)
        })
        .map_err(sql_error)?;
    if settings_count != 1
        || !crate::domain::local_configuration::valid_id(&revision)
        || !(1..=3600).contains(&interval)
        || sample_upload::target_url(origin.as_deref().unwrap_or("http://example.invalid"), &path)
            .is_err()
        || origin
            .as_ref()
            .map(|o| sample_upload::upload_origin(o).as_deref() != Ok(o.as_str()))
            .unwrap_or(false)
    {
        return Err("profile_ledger_invalid".into());
    }
    let mut cursor = String::new();
    loop {
        let ids: Vec<String> = c.prepare("SELECT sample_id FROM sample_uploads WHERE sample_id>?1 COLLATE BINARY ORDER BY sample_id COLLATE BINARY LIMIT 100").map_err(sql_error)?
            .query_map([&cursor], |r| r.get(0)).map_err(sql_error)?.collect::<Result<_,_>>().map_err(sql_error)?;
        if ids.is_empty() {
            break;
        }
        for id in &ids {
            let (inst, plc, db, generation, contract, origin, body, body_sha, state, attempt, next, dispatched, ack_at, receipt, receipt_sha): (String,String,u16,String,String,Option<String>,Option<String>,Option<String>,String,u32,String,Option<String>,Option<String>,Option<String>,Option<String>) = c.query_row("SELECT instance_id,plc_id,db_number,source_generation,contract,origin,body,body_sha,state,attempt,next_attempt_at,dispatched_at,acknowledged_at,receipt,receipt_sha FROM sample_uploads WHERE sample_id=?1", [id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?,r.get(7)?,r.get(8)?,r.get(9)?,r.get(10)?,r.get(11)?,r.get(12)?,r.get(13)?,r.get(14)?))).map_err(sql_error)?;
            if contract != CONTRACT
                || origin
                    .as_ref()
                    .map(|o| sample_upload::normalize_target(o).as_deref() != Ok(o.as_str()))
                    .unwrap_or(false)
                || (state != "needs_processing" && origin.is_none())
                || !matches!(
                    state.as_str(),
                    "prepared" | "inflight" | "unknown" | "needs_processing" | "acknowledged"
                )
                || (state == "prepared" && attempt != 0)
                || (matches!(state.as_str(), "inflight" | "unknown" | "acknowledged")
                    && (attempt == 0 || dispatched.is_none()))
            {
                return Err("profile_ledger_invalid".into());
            }
            let attempts: Vec<(u32,String,String)> = c.prepare("SELECT attempt,target_url,started_at FROM sample_upload_attempts WHERE sample_id=?1 ORDER BY attempt").map_err(sql_error)?
                .query_map([id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).map_err(sql_error)?
                .collect::<Result<_,_>>().map_err(sql_error)?;
            if attempts.len() != attempt as usize {
                return Err("profile_ledger_invalid".into());
            }
            for (index, (number, url, time)) in attempts.iter().enumerate() {
                if *number as usize != index + 1
                    || sample_upload::normalize_target(url).as_deref() != Ok(url.as_str())
                    || crate::domain::facts_wire::time(time).is_err()
                {
                    return Err("profile_ledger_invalid".into());
                }
            }
            let rebindings: Vec<(String,String,String)> = c.prepare("SELECT old_url,new_url,confirmed_at FROM sample_upload_rebindings WHERE sample_id=?1 ORDER BY id").map_err(sql_error)?
                .query_map([id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).map_err(sql_error)?
                .collect::<Result<_,_>>().map_err(sql_error)?;
            for (old, new, time) in &rebindings {
                if old == new
                    || sample_upload::normalize_target(&old).as_deref() != Ok(old.as_str())
                    || sample_upload::normalize_target(&new).as_deref() != Ok(new.as_str())
                    || crate::domain::facts_wire::time(&time).is_err()
                {
                    return Err("profile_ledger_invalid".into());
                }
            }
            if let Some((_, first_url, _)) = attempts.first() {
                let mut target = first_url.as_str();
                let mut changes = rebindings.iter();
                for (_, url, _) in &attempts {
                    while target != url {
                        let (old, new, _) = changes.next().ok_or("profile_ledger_invalid")?;
                        if old != target {
                            return Err("profile_ledger_invalid".into());
                        }
                        target = new;
                    }
                }
                for (old, new, _) in changes {
                    if old != target {
                        return Err("profile_ledger_invalid".into());
                    }
                    target = new;
                }
                if origin.as_deref() != Some(target) {
                    return Err("profile_ledger_invalid".into());
                }
            } else if !rebindings.is_empty() {
                return Err("profile_ledger_invalid".into());
            }
            crate::domain::facts_wire::time(&next)?;
            if let Some(at) = &dispatched {
                crate::domain::facts_wire::time(at)?;
            }
            let (raw, sha, cycle, manifest, manifest_sha, context, context_sha): (String,String,String,String,String,String,String) = c.query_row("SELECT s.payload,s.sha256,s.cycle_id,cc.manifest,cc.sha256,x.payload,x.sha256 FROM samples s JOIN collection_cycles cc ON cc.id=s.cycle_id JOIN configuration_contexts x ON x.revision=s.revision WHERE s.id=?1", [id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?))).map_err(sql_error)?;
            if digest(&raw) != sha
                || digest(&manifest) != manifest_sha
                || digest(&context) != context_sha
            {
                return Err("profile_ledger_invalid".into());
            }
            let sample: SamplePayload =
                serde_json::from_value(super::profile_contract::local_json(&raw, 2 * 1024 * 1024)?)
                    .map_err(|_| "profile_ledger_invalid")?;
            let source = cycle_reporting(c, &cycle, &sample)?.ok_or("profile_ledger_invalid")?;
            if sample.sample_id != *id
                || sample.instance_id != instance
                || source.instance_id != inst
                || source.plc_id != plc
                || sample.db_number != db
                || source.source_generation != generation
            {
                return Err("profile_ledger_invalid".into());
            }
            match (&body, &body_sha) {
                (Some(body), Some(sha256)) => {
                    let manifest: CycleManifest = serde_json::from_value(
                        super::profile_contract::local_json(&manifest, 512 * 1024)?,
                    )
                    .map_err(|_| "profile_ledger_invalid")?;
                    let config = serde_json::from_value(super::profile_contract::local_json(
                        &context,
                        16 * 1024 * 1024,
                    )?)
                    .map_err(|_| "profile_ledger_invalid")?;
                    if pf::sha(body.as_bytes()) != *sha256
                        || body.len() > BODY_LIMIT
                        || sample_upload::build_with_identity(
                            &sample,
                            &sha,
                            &manifest,
                            &config,
                            instance,
                            Some(&source),
                        )? != *body
                        || legacy_status(c, id, &cycle)? != LegacyStatus::NeverSent
                    {
                        return Err("profile_ledger_invalid".into());
                    }
                }
                (None, None) if state == "needs_processing" => {}
                _ => return Err("profile_ledger_invalid".into()),
            }
            if state == "acknowledged" {
                let raw = receipt.as_ref().ok_or("profile_ledger_invalid")?;
                if receipt_sha.as_deref() != Some(pf::sha(raw.as_bytes()).as_str())
                    || sample_upload::classify(200, "application/json", raw.as_bytes(), &inst, id)
                        != Reply::Committed
                {
                    return Err("profile_ledger_invalid".into());
                }
                crate::domain::facts_wire::time(
                    ack_at.as_deref().ok_or("profile_ledger_invalid")?,
                )?;
            } else if ack_at.is_some() || receipt.is_some() || receipt_sha.is_some() {
                return Err("profile_ledger_invalid".into());
            }
        }
        cursor = ids.last().unwrap().clone();
    }
    Ok(())
}

/// 正文在本事务内冻结；同一 sample 一旦绑定，不能重编号、重编码或改投。
pub(super) fn freeze(c: &mut Connection, f: &Frozen, at: &str) -> LocalResult<()> {
    if sample_upload::normalize_target(&f.origin)? != f.origin
        || f.body.len() > BODY_LIMIT
        || pf::sha(f.body.as_bytes()) != f.body_sha
    {
        return Err("sample_frozen_invalid".into());
    }
    let body = pf::parse(f.body.as_bytes(), BODY_LIMIT)?;
    if body["contractVersion"] != CONTRACT
        || body["instanceId"] != f.instance_id
        || body["sampleId"] != f.sample_id
        || body["plcId"] != f.plc_id
        || body["dbNumber"] != f.db_number
        || body["sourceGeneration"] != f.source_generation
    {
        return Err("sample_frozen_invalid".into());
    }
    let tx = c.transaction().map_err(sql_error)?;
    let existing: Option<(String, String, String, u16, String, String, Option<String>, Option<String>)> = tx
        .query_row("SELECT instance_id,plc_id,contract,db_number,source_generation,origin,body,body_sha FROM sample_uploads WHERE sample_id=?1", [&f.sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?,r.get(7)?)))
        .optional().map_err(sql_error)?;
    if let Some(row) = existing {
        if row
            != (
                f.instance_id.clone(),
                f.plc_id.clone(),
                CONTRACT.into(),
                f.db_number,
                f.source_generation.clone(),
                f.origin.clone(),
                Some(f.body.clone()),
                Some(f.body_sha.clone()),
            )
        {
            return Err("sample_binding_conflict".into());
        }
        return Ok(());
    }
    tx.execute("INSERT INTO sample_uploads(sample_id,instance_id,plc_id,db_number,source_generation,contract,origin,body,body_sha,state,next_attempt_at) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,'prepared',?10)", params![f.sample_id,f.instance_id,f.plc_id,f.db_number,f.source_generation,CONTRACT,f.origin,f.body,f.body_sha,at]).map_err(sql_error)?;
    tx.commit().map_err(sql_error)
}

/// 派发标记必须先提交，再由调用者开始网络请求。
pub(super) fn mark_attempt(c: &mut Connection, f: &Frozen, at: &str) -> LocalResult<u32> {
    let tx = c.transaction().map_err(sql_error)?;
    let changed = tx.execute("UPDATE sample_uploads SET state='inflight',attempt=attempt+1,dispatched_at=?1,last_error=NULL WHERE sample_id=?2 AND instance_id=?3 AND plc_id=?4 AND db_number=?5 AND source_generation=?6 AND contract=?7 AND origin=?8 AND body=?9 AND body_sha=?10 AND state IN ('prepared','unknown') AND NOT EXISTS(SELECT 1 FROM sample_upload_source_blocks b WHERE b.origin=sample_uploads.origin AND b.instance_id=sample_uploads.instance_id AND b.plc_id=sample_uploads.plc_id AND b.source_generation=sample_uploads.source_generation)", params![at,f.sample_id,f.instance_id,f.plc_id,f.db_number,f.source_generation,CONTRACT,f.origin,f.body,f.body_sha]).map_err(sql_error)?;
    if changed != 1 {
        return Err("sample_dispatch_conflict".into());
    }
    let attempt = tx
        .query_row(
            "SELECT attempt FROM sample_uploads WHERE sample_id=?1",
            [&f.sample_id],
            |r| r.get(0),
        )
        .map_err(sql_error)?;
    tx.execute("INSERT INTO sample_upload_attempts(sample_id,attempt,target_url,started_at) VALUES(?1,?2,?3,?4)", params![f.sample_id,attempt,f.origin,at]).map_err(sql_error)?;
    tx.commit().map_err(sql_error)?;
    Ok(attempt)
}

/// 冷重开保持停态，已标记但结果未知的请求继续受保护。
pub(super) fn recover(c: &mut Connection, at: &str) -> LocalResult<()> {
    let tx = c.transaction().map_err(sql_error)?;
    tx.execute("UPDATE sample_uploads SET state='unknown',last_error='process_restarted',next_attempt_at=?1 WHERE state='inflight'", [at]).map_err(sql_error)?;
    tx.commit().map_err(sql_error)
}

/// 回执及 v2 状态同事务提交；冻结目标、原字节与派发证据必须仍然相同。
#[cfg(test)]
pub(super) fn apply(
    c: &mut Connection,
    f: &Frozen,
    status: u16,
    media: &str,
    raw: &[u8],
    at: &str,
    next: &str,
) -> LocalResult<Reply> {
    let attempt = c
        .query_row(
            "SELECT attempt FROM sample_uploads WHERE sample_id=?1",
            [&f.sample_id],
            |r| r.get(0),
        )
        .map_err(sql_error)?;
    apply_for_attempt(c, f, attempt, status, media, raw, at, next)
}
pub(super) fn apply_for_attempt(
    c: &mut Connection,
    f: &Frozen,
    attempt: u32,
    status: u16,
    media: &str,
    raw: &[u8],
    at: &str,
    next: &str,
) -> LocalResult<Reply> {
    if pf::sha(f.body.as_bytes()) != f.body_sha {
        return Err("sample_frozen_invalid".into());
    }
    let reply = sample_upload::classify(status, media, raw, &f.instance_id, &f.sample_id);
    let tx = c.transaction().map_err(sql_error)?;
    let matches: bool = tx.query_row("SELECT EXISTS(SELECT 1 FROM sample_uploads WHERE sample_id=?1 AND instance_id=?2 AND plc_id=?3 AND db_number=?4 AND source_generation=?5 AND contract=?6 AND origin=?7 AND body=?8 AND body_sha=?9 AND attempt=?10 AND state IN ('inflight','unknown') AND EXISTS(SELECT 1 FROM sample_upload_attempts a WHERE a.sample_id=sample_uploads.sample_id AND a.attempt=?10 AND a.target_url=?7))", params![f.sample_id,f.instance_id,f.plc_id,f.db_number,f.source_generation,CONTRACT,f.origin,f.body,f.body_sha,attempt], |r| r.get(0)).map_err(sql_error)?;
    if !matches {
        return Err("sample_response_conflict".into());
    }
    match &reply {
        Reply::Committed => {
            let receipt = std::str::from_utf8(raw).map_err(|_| "invalid_receipt")?;
            tx.execute("UPDATE sample_uploads SET state='acknowledged',acknowledged_at=?1,receipt=?2,receipt_sha=?3,last_error=NULL WHERE sample_id=?4", params![at,receipt,pf::sha(raw),f.sample_id]).map_err(sql_error)?;
        }
        Reply::SourceBlocked => {
            tx.execute("INSERT OR REPLACE INTO sample_upload_source_blocks(origin,instance_id,plc_id,source_generation,reason) VALUES(?1,?2,?3,?4,'scope_rejected')", params![f.origin,f.instance_id,f.plc_id,f.source_generation]).map_err(sql_error)?;
            tx.execute("UPDATE sample_uploads SET state='unknown',last_error='scope_rejected',next_attempt_at=?1 WHERE sample_id=?2", params![next,f.sample_id]).map_err(sql_error)?;
        }
        Reply::NeedsProcessing(reason) => {
            tx.execute("UPDATE sample_uploads SET state='needs_processing',last_error=?1 WHERE sample_id=?2", params![reason,f.sample_id]).map_err(sql_error)?;
        }
        Reply::TargetMismatch => {
            tx.execute("UPDATE sample_uploads SET state='unknown',last_error='target_protocol_mismatch',next_attempt_at=?1 WHERE sample_id=?2", params![next,f.sample_id]).map_err(sql_error)?;
        }
        Reply::Retry(reason) => {
            tx.execute("UPDATE sample_uploads SET state='unknown',last_error=?1,next_attempt_at=?2 WHERE sample_id=?3", params![reason,next,f.sample_id]).map_err(sql_error)?;
        }
    }
    tx.commit().map_err(sql_error)?;
    Ok(reply)
}
