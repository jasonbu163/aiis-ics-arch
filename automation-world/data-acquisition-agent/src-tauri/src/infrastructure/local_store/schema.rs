//! 新空双库v2显式schema；普通rowid表、普通列索引，无ATTACH/视图/表达式或partial索引。
pub(super) const CONFIG_APP: i64 = 0x44414143;
pub(super) const RUNTIME_APP: i64 = 0x44414152;
pub(super) const CONFIG: &str = r#"
CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
INSERT INTO schema_migrations VALUES(2,__BUSINESS_NOW__);
CREATE TABLE instance_metadata(id INTEGER PRIMARY KEY CHECK(id=1),instance_id TEXT NOT NULL, schema_version INTEGER NOT NULL CHECK(schema_version=2),time_profile TEXT NOT NULL CHECK(time_profile='asia-shanghai-rfc3339-ms-v1'));
CREATE TABLE source_documents(id TEXT PRIMARY KEY,sha256 TEXT NOT NULL, name TEXT NOT NULL,content TEXT NOT NULL,diagnostics TEXT NOT NULL);
CREATE UNIQUE INDEX source_hash ON source_documents(sha256);
CREATE TABLE configuration_draft(id INTEGER PRIMARY KEY CHECK(id=1),etag TEXT NOT NULL,payload TEXT NOT NULL,issues TEXT NOT NULL);
CREATE TABLE configuration_revisions(id TEXT PRIMARY KEY,schema_version INTEGER NOT NULL CHECK(schema_version=1),sha256 TEXT NOT NULL,payload TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE active_selection(id INTEGER PRIMARY KEY CHECK(id=1),active TEXT REFERENCES configuration_revisions(id),previous TEXT REFERENCES configuration_revisions(id));
INSERT INTO active_selection VALUES(1,NULL,NULL);
CREATE TABLE activation_intents(token TEXT PRIMARY KEY,old_revision TEXT,new_revision TEXT NOT NULL REFERENCES configuration_revisions(id),phase TEXT NOT NULL,created_at TEXT NOT NULL);
"#;
pub(super) const RUNTIME: &str = r#"
CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL);
INSERT INTO schema_migrations VALUES(2,__BUSINESS_NOW__);
CREATE TABLE runtime_metadata(id INTEGER PRIMARY KEY CHECK(id=1),instance_id TEXT NOT NULL,schema_version INTEGER NOT NULL CHECK(schema_version=2),clean_exit INTEGER NOT NULL,used_revision TEXT,time_profile TEXT NOT NULL CHECK(time_profile='asia-shanghai-rfc3339-ms-v1'));
CREATE TABLE plc_sources(plc_id TEXT PRIMARY KEY,generation TEXT NOT NULL,next_seq INTEGER NOT NULL CHECK(next_seq>0),UNIQUE(plc_id,generation));
CREATE TABLE configuration_contexts(revision TEXT PRIMARY KEY,schema_version INTEGER NOT NULL CHECK(schema_version=1),sha256 TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE activation_journal(token TEXT PRIMARY KEY,revision TEXT NOT NULL REFERENCES configuration_contexts(revision),phase TEXT NOT NULL);
CREATE TABLE collection_cycles(id TEXT PRIMARY KEY,plc_id TEXT NOT NULL,generation TEXT NOT NULL,source_seq INTEGER NOT NULL,group_id TEXT NOT NULL,revision TEXT NOT NULL REFERENCES configuration_contexts(revision),started_at TEXT NOT NULL,finished_at TEXT NOT NULL,saved_at TEXT NOT NULL,quality TEXT NOT NULL,manifest TEXT NOT NULL,sha256 TEXT NOT NULL,expected_samples INTEGER NOT NULL,UNIQUE(plc_id,generation,source_seq));
CREATE TABLE samples(sample_order INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT NOT NULL UNIQUE,cycle_id TEXT NOT NULL REFERENCES collection_cycles(id),db_number INTEGER NOT NULL,plc_id TEXT NOT NULL,group_id TEXT NOT NULL,source_seq INTEGER NOT NULL,revision TEXT NOT NULL,quality TEXT NOT NULL,saved_at TEXT NOT NULL,schema_version INTEGER NOT NULL CHECK(schema_version=2),payload TEXT NOT NULL,sha256 TEXT NOT NULL,payload_bytes INTEGER NOT NULL,UNIQUE(cycle_id,db_number));
CREATE INDEX history_order ON samples(saved_at,id);
CREATE INDEX history_plc ON samples(plc_id,saved_at,id);
CREATE TABLE sample_delivery(sample_id TEXT PRIMARY KEY REFERENCES samples(id),state TEXT NOT NULL CHECK(state IN ('pending','acknowledged')),acknowledged_at TEXT);
CREATE TABLE sample_references(sample_id TEXT NOT NULL REFERENCES samples(id),reference_id TEXT NOT NULL,PRIMARY KEY(sample_id,reference_id));
CREATE TABLE runtime_events(id INTEGER PRIMARY KEY,event TEXT NOT NULL,resource TEXT NOT NULL,result TEXT NOT NULL,created_at TEXT NOT NULL);
"#;
pub(super) fn runtime_sql() -> String {
    RUNTIME.replace(
        "__BUSINESS_NOW__",
        crate::domain::business_time::SQL_NOW.trim_start_matches("SELECT "),
    )
}

pub(super) fn config_sql() -> String {
    CONFIG.replace(
        "__BUSINESS_NOW__",
        crate::domain::business_time::SQL_NOW.trim_start_matches("SELECT "),
    )
}

/// 仅新空profile使用；不在v2打开路径执行任何投递DDL。
pub(super) fn runtime_v3_sql() -> String {
    let base = runtime_sql().replace("VALUES(2,", "VALUES(3,").replace(
        "CHECK(schema_version=2),clean_exit",
        "CHECK(schema_version=3),clean_exit",
    );
    format!("{base}\n{DELIVERY}")
}
/// v4 保留 v1 证据表，另建互不覆盖的 v2 样本投递账本。
pub(super) fn runtime_v4_sql() -> String {
    let base = runtime_v3_sql().replace("VALUES(3,", "VALUES(4,").replace(
        "CHECK(schema_version=3),clean_exit",
        "CHECK(schema_version=4),clean_exit",
    );
    format!("{base}\n{}", super::sample_upload::SQL)
}
pub(super) const REPORTING_SOURCES: &str = r#"
CREATE TABLE reporting_identity(id INTEGER PRIMARY KEY CHECK(id=1),instance_id TEXT);
CREATE TABLE reporting_bindings(local_plc_id TEXT PRIMARY KEY,plc_id TEXT NOT NULL UNIQUE,source_generation TEXT NOT NULL);
CREATE TABLE reporting_generations(plc_id TEXT NOT NULL,source_generation TEXT NOT NULL,instance_id TEXT NOT NULL,local_plc_id TEXT NOT NULL,local_generation TEXT NOT NULL,PRIMARY KEY(plc_id,source_generation));
CREATE TABLE reporting_cycles(cycle_id TEXT PRIMARY KEY REFERENCES collection_cycles(id),instance_id TEXT,plc_id TEXT,source_generation TEXT,CHECK((instance_id IS NULL AND plc_id IS NULL AND source_generation IS NULL) OR (instance_id IS NOT NULL AND plc_id IS NOT NULL AND source_generation IS NOT NULL)));
"#;
pub(super) fn runtime_v4_extended_sql() -> String {
    format!("{}\n{}", runtime_v4_sql(), REPORTING_SOURCES)
}

pub(super) const REPORTING_SWITCHES: &str = r#"
CREATE TABLE reporting_disabled(local_plc_id TEXT PRIMARY KEY REFERENCES plc_sources(plc_id));
"#;

pub(super) fn runtime_v4_switches_sql() -> String {
    format!("{}\n{}", runtime_v4_extended_sql(), REPORTING_SWITCHES)
}

pub(super) fn runtime_v4_schema(c: &rusqlite::Connection) -> Result<String, String> {
    let switches = runtime_v4_switches_sql();
    if verify_structure(c, &switches).is_ok() {
        return Ok(switches);
    }
    let extended = runtime_v4_extended_sql();
    if verify_structure(c, &extended).is_ok() {
        return Ok(extended);
    }
    let original = runtime_v4_sql();
    verify_structure(c, &original)?;
    Ok(original)
}
pub(super) const DELIVERY: &str = r#"
CREATE INDEX delivery_cycle_candidates ON collection_cycles(plc_id,group_id,source_seq);
CREATE TABLE delivery_settings(id INTEGER PRIMARY KEY CHECK(id=1),settings_revision TEXT NOT NULL,payload TEXT NOT NULL,latest_streak INTEGER NOT NULL DEFAULT 0,latest_cursor TEXT NOT NULL DEFAULT '',history_cursor TEXT NOT NULL DEFAULT '');
CREATE TABLE delivery_cycles(cycle_id TEXT PRIMARY KEY REFERENCES collection_cycles(id),target_id TEXT NOT NULL,manifest_sha TEXT NOT NULL,context_sha TEXT NOT NULL,cycle_digest TEXT NOT NULL,wire TEXT NOT NULL);
CREATE TABLE delivery_parts(sample_id TEXT NOT NULL REFERENCES samples(id),part INTEGER NOT NULL,parts INTEGER NOT NULL,cycle_id TEXT NOT NULL REFERENCES delivery_cycles(cycle_id),source_sha TEXT NOT NULL,content_digest TEXT NOT NULL,point_ids TEXT NOT NULL,state TEXT NOT NULL,batch_id TEXT,receipt_id TEXT,PRIMARY KEY(sample_id,part));
CREATE INDEX delivery_part_cycle ON delivery_parts(cycle_id,state);
CREATE INDEX delivery_part_batch ON delivery_parts(batch_id,state);
CREATE TABLE delivery_batches(batch_id TEXT NOT NULL UNIQUE,target_id TEXT NOT NULL,settings_revision TEXT NOT NULL,request_digest TEXT NOT NULL,body_sha TEXT NOT NULL,body TEXT,members TEXT NOT NULL,parent_id TEXT,parent_depth INTEGER NOT NULL,state TEXT NOT NULL,attempt INTEGER NOT NULL DEFAULT 0,protocol_failures INTEGER NOT NULL DEFAULT 0,readiness_failures INTEGER NOT NULL DEFAULT 0,next_attempt_at TEXT NOT NULL,created_at TEXT NOT NULL,last_error TEXT,created_order INTEGER PRIMARY KEY AUTOINCREMENT);
CREATE INDEX delivery_dispatch ON delivery_batches(state,next_attempt_at,created_order);
CREATE TABLE delivery_receipts(batch_id TEXT PRIMARY KEY REFERENCES delivery_batches(batch_id),receipt_id TEXT NOT NULL,request_digest TEXT NOT NULL,response_utf8 TEXT NOT NULL,response_sha TEXT NOT NULL,committed_at TEXT NOT NULL,proof_expires_at TEXT NOT NULL,terminal TEXT NOT NULL);
CREATE TABLE delivery_events(id INTEGER PRIMARY KEY,event TEXT NOT NULL,resource TEXT NOT NULL,result TEXT NOT NULL,created_at TEXT NOT NULL);
"#;

/// 只读比较显式已知DDL；缺表/列/索引/约束或意外触发器一律拒绝，不修补。
pub(super) fn verify_structure(c: &rusqlite::Connection, sql: &str) -> Result<(), String> {
    let actual = c.prepare("SELECT type,name,sql FROM sqlite_schema WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY type COLLATE BINARY,name COLLATE BINARY").map_err(super::sql_error)?.query_map([], |r| Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?,r.get::<_,String>(2)?))).map_err(super::sql_error)?.collect::<Result<Vec<_>,_>>().map_err(super::sql_error)?;
    if actual != ddl_records(sql)? {
        return Err("schema_structure_mismatch".into());
    }
    Ok(())
}
/// 同一静态记录集用于DDL核验与封存指纹；不规范化语句内部空白。
pub(super) fn ddl_records(sql: &str) -> Result<Vec<(String, String, String)>, String> {
    let mut records: Vec<(String, String, String)> = vec![];
    for statement in sql.split(';') {
        let expected = statement.trim();
        if !expected.starts_with("CREATE TABLE ")
            && !expected.starts_with("CREATE INDEX ")
            && !expected.starts_with("CREATE UNIQUE INDEX ")
        {
            continue;
        }
        let name = expected
            .split_whitespace()
            .nth(if expected.starts_with("CREATE UNIQUE INDEX ") {
                3
            } else {
                2
            })
            .and_then(|s| s.split('(').next())
            .ok_or("schema_structure_mismatch")?;
        records.push((
            if expected.starts_with("CREATE TABLE ") {
                "table"
            } else {
                "index"
            }
            .into(),
            name.into(),
            expected.into(),
        ));
    }
    records.sort_by(|a, b| {
        a.0.as_bytes()
            .cmp(b.0.as_bytes())
            .then(a.1.as_bytes().cmp(b.1.as_bytes()))
    });
    Ok(records)
}
pub(super) fn fingerprint(sql: &str) -> Result<String, String> {
    use sha2::{Digest, Sha256};
    let mut hash = Sha256::new();
    hash.update(b"daa-ddl-sha256/v1\0");
    for (kind, name, sql) in ddl_records(sql)? {
        for field in [kind, name, sql] {
            hash.update((field.len() as u32).to_be_bytes());
            hash.update(field.as_bytes());
        }
    }
    Ok(format!("sha256:{:x}", hash.finalize()))
}

use super::profile_contract::local_json;
use super::{count, number, record, require, str_at};
use crate::domain::{
    facts_canonical as pf, facts_wire as wire,
    local_configuration::{Configuration, LocalResult},
    local_sample::{digest, CycleManifest, SamplePayload},
};
use rusqlite::Connection;
use serde_json::{json, Value};
/// 固定内部SQL的typed text/integer/null记录；不接受任意产品SQL入口。
/// 只分页稳定索引key；每页<=100个小ID，逐条读取原材料，不收集整个历史。
fn each(
    c: &Connection,
    table: &str,
    key: &str,
    mut visit: impl FnMut(&str) -> LocalResult<()>,
) -> LocalResult<()> {
    let mut cursor: Option<String> = None;
    loop {
        let keys=c.prepare(&format!("SELECT {key} FROM {table} WHERE (?1 IS NULL OR {key}>?1 COLLATE BINARY) ORDER BY {key} COLLATE BINARY LIMIT 100")).map_err(super::sql_error)?.query_map([cursor.as_deref()],|r|r.get::<_,String>(0)).map_err(super::sql_error)?.collect::<Result<Vec<_>,_>>().map_err(super::sql_error)?;
        if keys.is_empty() {
            break;
        }
        for key in &keys {
            require(!key.is_empty())?;
            visit(key)?;
        }
        cursor = keys.last().cloned();
    }
    Ok(())
}
fn configuration(raw: &str) -> LocalResult<Configuration> {
    let c: Configuration = serde_json::from_value(local_json(raw, 16 * 1024 * 1024)?)
        .map_err(|_| "profile_ledger_invalid")?;
    require(c.schema_version == 1 && c.sources.iter().all(|s| s.sha256 == digest(&s.content)))?;
    Ok(c)
}
fn context(r: &Connection, revision: &str) -> LocalResult<Configuration> {
    let row = record(
        r,
        "SELECT payload,sha256 FROM configuration_contexts WHERE revision=?1",
        &[&revision],
    )?;
    require(digest(str_at(&row, 0)?) == str_at(&row, 1)?)?;
    configuration(str_at(&row, 0)?)
}
fn core_check(c: &Connection, r: &Connection, instance: &str) -> LocalResult<()> {
    let runtime_version: u32 = r
        .query_row("PRAGMA user_version", [], |row| row.get(0))
        .map_err(super::sql_error)?;
    for db in [c, r] {
        require(str_at(&record(db, "PRAGMA integrity_check", &[])?, 0)? == "ok")?;
        let mut q = db
            .prepare("PRAGMA foreign_key_check")
            .map_err(super::sql_error)?;
        require(
            q.query([])
                .map_err(super::sql_error)?
                .next()
                .map_err(super::sql_error)?
                .is_none(),
        )?;
        require(count(db, "SELECT count(*) FROM schema_migrations", &[])? == 1)?;
    }
    require(
        count(c, "SELECT count(*) FROM instance_metadata", &[])? == 1
            && count(r, "SELECT count(*) FROM runtime_metadata WHERE clean_exit IN (0,1) AND (used_revision IS NULL OR EXISTS(SELECT 1 FROM configuration_contexts c WHERE c.revision=runtime_metadata.used_revision))", &[])? == 1
            && count(c, "SELECT count(*) FROM configuration_draft", &[])? == 1
            && count(c, "SELECT count(*) FROM active_selection", &[])? == 1,
    )?;
    let draft = record(
        c,
        "SELECT etag,payload,issues FROM configuration_draft WHERE id=1",
        &[],
    )?;
    require(crate::domain::local_configuration::valid_id(str_at(
        &draft, 0,
    )?))?;
    configuration(str_at(&draft, 1)?)?;
    require(local_json(str_at(&draft, 2)?, 16 * 1024 * 1024)?.is_array())?;
    each(c, "source_documents", "id", |id| {
        let row = record(
            c,
            "SELECT content,sha256 FROM source_documents WHERE id=?1",
            &[&id],
        )?;
        require(digest(str_at(&row, 0)?) == str_at(&row, 1)?)
    })?;
    for (db, table, key) in [
        (c, "configuration_revisions", "id"),
        (r, "configuration_contexts", "revision"),
    ] {
        each(db, table, key, |id| {
            let row = record(
                db,
                &format!("SELECT payload,sha256,schema_version FROM {table} WHERE {key}=?1"),
                &[&id],
            )?;
            require(
                crate::domain::local_configuration::valid_id(id)
                    && number(&row, 2)? == 1
                    && digest(str_at(&row, 0)?) == str_at(&row, 1)?,
            )?;
            let config = configuration(str_at(&row, 0)?)?;
            require(
                crate::domain::local_configuration::validate(&config).is_empty()
                    || (runtime_version == 4
                        && crate::domain::local_configuration::validate_for_runtime(&config, 4)
                            .is_empty()),
            )
        })?;
    }
    let selected = record(
        c,
        "SELECT active,previous FROM active_selection WHERE id=1",
        &[],
    )?;
    if let Some(active) = selected[0].as_str() {
        let rev = record(
            c,
            "SELECT sha256 FROM configuration_revisions WHERE id=?1",
            &[&active],
        )?;
        let ctx = record(
            r,
            "SELECT sha256 FROM configuration_contexts WHERE revision=?1",
            &[&active],
        )?;
        require(rev == ctx)?;
    }
    each(c, "activation_intents", "token", |token| {
        let row = record(
            c,
            "SELECT old_revision,new_revision,phase FROM activation_intents WHERE token=?1",
            &[&token],
        )?;
        let revision = str_at(&row, 1)?;
        let phase = str_at(&row, 2)?;
        require(["prepared", "selected", "applied"].contains(&phase))?;
        if phase == "prepared" {
            require(selected[0] == row[0])?;
        } else if phase == "selected" {
            require(selected[0] == row[1])?;
        }
        if phase != "prepared" {
            let journal = record(
                r,
                "SELECT revision,phase FROM activation_journal WHERE token=?1",
                &[&token],
            )?;
            require(
                str_at(&journal, 0)? == revision
                    && (phase != "applied" || str_at(&journal, 1)? == "applied"),
            )?;
        }
        Ok(())
    })?;
    each(r, "activation_journal", "token", |token| {
        let row = record(
            r,
            "SELECT revision,phase FROM activation_journal WHERE token=?1",
            &[&token],
        )?;
        require(["prepared", "applied"].contains(&str_at(&row, 1)?))?;
        let n = count(
            c,
            "SELECT count(*) FROM activation_intents WHERE token=?1 AND new_revision=?2",
            &[&token, &str_at(&row, 0)?],
        )?;
        require(n == 1 || str_at(&row, 1)? == "applied")
    })?;
    each(r, "plc_sources", "plc_id", |plc| {
        let row = record(
            r,
            "SELECT generation,next_seq FROM plc_sources WHERE plc_id=?1",
            &[&plc],
        )?;
        require(
            crate::domain::local_configuration::valid_id(plc)
                && crate::domain::local_configuration::valid_id(str_at(&row, 0)?)
                && number(&row, 1)? > 0,
        )
    })?;
    each(r, "collection_cycles", "id", |cid| {
        let row=record(r,"SELECT manifest,sha256,plc_id,generation,source_seq,group_id,revision,started_at,finished_at,saved_at,expected_samples,quality FROM collection_cycles WHERE id=?1",&[&cid])?;
        require(digest(str_at(&row, 0)?) == str_at(&row, 1)?)?;
        let manifest: CycleManifest =
            serde_json::from_value(pf::parse(str_at(&row, 0)?.as_bytes(), 512 * 1024)?)
                .map_err(|_| "profile_ledger_invalid")?;
        require(
            manifest.schema_version == 2
                && manifest.cycle_id == cid
                && manifest.samples.len() <= 32
                && !manifest.samples.is_empty(),
        )?;
        require(
            json!([
                manifest.plc_id,
                manifest.source_generation,
                manifest
                    .source_seq
                    .parse::<i64>()
                    .map_err(|_| "profile_ledger_invalid")?,
                manifest.group_id,
                manifest.revision,
                manifest.started_at,
                manifest.finished_at,
                manifest.saved_at,
                manifest.samples.len()
            ]) == json!([row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]),
        )?;
        let source = record(
            r,
            "SELECT generation,next_seq FROM plc_sources WHERE plc_id=?1",
            &[&manifest.plc_id],
        )?;
        require(
            str_at(&source, 0)? == manifest.source_generation
                && number(&source, 1)? > number(&row, 4)?,
        )?;
        let config = context(r, &manifest.revision)?;
        let mut expected = config
            .points
            .iter()
            .filter(|p| {
                p.enabled
                    && p.plc_id == manifest.plc_id
                    && p.group_id.as_deref() == Some(&manifest.group_id)
            })
            .map(|p| p.id.clone())
            .collect::<Vec<_>>();
        expected.sort();
        require(expected == manifest.expected_point_ids)?;
        require(
            count(r, "SELECT count(*) FROM samples WHERE cycle_id=?1", &[&cid])?
                == manifest.samples.len() as i64,
        )?;
        let mut seen = std::collections::BTreeSet::new();
        let mut seen_db = std::collections::BTreeSet::new();
        let mut all_good = true;
        let mut any_good = false;
        for sample in &manifest.samples {
            require(seen_db.insert(sample.db_number))?;
            let v=record(r,"SELECT payload,sha256,cycle_id,db_number,plc_id,group_id,source_seq,revision,saved_at,schema_version,payload_bytes FROM samples WHERE id=?1",&[&sample.sample_id])?;
            let raw = str_at(&v, 0)?;
            require(
                digest(raw) == sample.sha256
                    && str_at(&v, 1)? == sample.sha256
                    && number(&v, 9)? == 2
                    && number(&v, 10)? == raw.len() as i64,
            )?;
            let parsed = local_json(
                raw,
                if runtime_version == 4 {
                    2 * 1024 * 1024
                } else {
                    512 * 1024
                },
            )?;
            let p: SamplePayload =
                serde_json::from_value(parsed.clone()).map_err(|_| "profile_ledger_invalid")?;
            require(
                p.schema_version == 2
                    && p.instance_id == instance
                    && p.sample_id == sample.sample_id
                    && p.cycle_id == cid
                    && p.db_number == sample.db_number
                    && p.plc_id == manifest.plc_id
                    && p.source_generation == manifest.source_generation
                    && p.source_seq == manifest.source_seq
                    && p.group_id == manifest.group_id
                    && p.revision == manifest.revision
                    && p.started_at == manifest.started_at
                    && p.finished_at == manifest.finished_at
                    && p.saved_at == manifest.saved_at,
            )?;
            require(
                json!([
                    p.cycle_id,
                    p.db_number,
                    p.plc_id,
                    p.group_id,
                    p.source_seq
                        .parse::<i64>()
                        .map_err(|_| "profile_ledger_invalid")?,
                    p.revision,
                    p.saved_at
                ]) == json!([v[2], v[3], v[4], v[5], v[6], v[7], v[8]]),
            )?;
            for (pid, fact) in &p.points {
                require(
                    seen.insert(pid.clone())
                        && config.points.iter().any(|d| {
                            d.id == *pid
                                && d == &fact.definition
                                && config
                                    .dbs
                                    .iter()
                                    .any(|db| db.id == d.db_id && db.number == p.db_number)
                        }),
                )?;
                require(
                    (fact.quality == "good" && fact.reason.is_none())
                        || (["bad", "bad_read", "bad_timeout", "bad_decode"]
                            .contains(&fact.quality.as_str())
                            && fact.value.is_null()
                            && fact.reason.as_ref().map(|r| !r.is_empty()).unwrap_or(false)),
                )?;
                wire::time(&fact.observed_at)?;
                all_good &= fact.quality == "good";
                any_good |= fact.quality == "good";
            }
            for time in [&p.started_at, &p.finished_at, &p.saved_at] {
                wire::time(time)?;
            }
            require(
                count(
                    r,
                    "SELECT count(*) FROM sample_delivery WHERE sample_id=?1",
                    &[&p.sample_id],
                )? == 1,
            )?;
        }
        require(
            seen.into_iter().collect::<Vec<_>>() == expected
                && str_at(&row, 11)?
                    == if all_good {
                        "good"
                    } else if any_good {
                        "partial"
                    } else {
                        "bad"
                    },
        )
    })?;
    Ok(())
}
fn built(r: &Connection, cid: &str, instance: &str) -> LocalResult<wire::BuiltCycle> {
    let row = record(
        r,
        "SELECT manifest,sha256,revision FROM collection_cycles WHERE id=?1",
        &[&cid],
    )?;
    let manifest: CycleManifest = serde_json::from_value(local_json(str_at(&row, 0)?, 512 * 1024)?)
        .map_err(|_| "profile_ledger_invalid")?;
    let context = record(
        r,
        "SELECT payload,sha256 FROM configuration_contexts WHERE revision=?1",
        &[&manifest.revision],
    )?;
    let mut payloads = vec![];
    for s in manifest.samples {
        let p = record(
            r,
            "SELECT payload,sha256 FROM samples WHERE id=?1",
            &[&s.sample_id],
        )?;
        payloads.push((str_at(&p, 0)?.to_owned(), str_at(&p, 1)?.to_owned()));
    }
    wire::build_cycle(
        instance,
        str_at(&row, 0)?,
        str_at(&row, 1)?,
        str_at(&context, 0)?,
        str_at(&context, 1)?,
        &payloads,
    )
}
fn batch(r: &Connection, id: &str, row: &Value, instance: &str) -> LocalResult<wire::Batch> {
    let members = local_json(str_at(row, 4)?, wire::REQUEST_MAX)?;
    let members = members.as_array().ok_or("profile_ledger_invalid")?;
    require(!members.is_empty() && members.len() <= 32)?;
    let mut cycles = std::collections::BTreeMap::new();
    let mut parts = vec![];
    let mut seen = std::collections::BTreeSet::new();
    for member in members {
        require(
            member
                .as_object()
                .map(|m| {
                    m.len() == 3
                        && ["sampleId", "part", "contentDigest"]
                            .iter()
                            .all(|k| m.contains_key(*k))
                })
                .unwrap_or(false),
        )?;
        let sid = wire::text(member, "sampleId")?;
        let part = member["part"]
            .as_u64()
            .filter(|n| *n > 0 && *n <= 16)
            .ok_or("profile_ledger_invalid")? as u32;
        require(seen.insert((sid, part)))?;
        let p=record(r,"SELECT p.parts,p.cycle_id,p.source_sha,p.content_digest,p.point_ids,s.payload FROM delivery_parts p JOIN samples s ON s.id=p.sample_id WHERE p.sample_id=?1 AND p.part=?2",&[&sid,&part])?;
        require(str_at(&p, 3)? == wire::text(member, "contentDigest")?)?;
        let cid = str_at(&p, 1)?;
        if !cycles.contains_key(cid) {
            let wire = record(
                r,
                "SELECT wire,target_id FROM delivery_cycles WHERE cycle_id=?1",
                &[&cid],
            )?;
            require(str_at(&wire, 1)? == str_at(row, 8)?)?;
            let cycle: wire::Cycle =
                serde_json::from_value(pf::parse(str_at(&wire, 0)?.as_bytes(), wire::REQUEST_MAX)?)
                    .map_err(|_| "profile_ledger_invalid")?;
            cycles.insert(cid.to_owned(), cycle);
        }
        parts.push(wire::Part {
            sample_id: sid.into(),
            cycle_id: cid.into(),
            part,
            parts: number(&p, 0)? as u32,
            source_sha256: str_at(&p, 2)?.into(),
            content_digest: str_at(&p, 3)?.into(),
            point_ids: serde_json::from_value(local_json(str_at(&p, 4)?, 128 * 1024)?)
                .map_err(|_| "profile_ledger_invalid")?,
            payload_utf8: str_at(&p, 5)?.into(),
        });
    }
    let parent = if let Some(parent) = row[5].as_str() {
        let p=record(r,"SELECT request_digest,parent_depth,state,target_id,members FROM delivery_batches WHERE batch_id=?1",&[&parent])?;
        require(
            str_at(&p, 2)? == "rejected"
                && number(row, 6)? == number(&p, 1)? + 1
                && str_at(row, 8)? == str_at(&p, 3)?,
        )?;
        let allowed = local_json(str_at(&p, 4)?, wire::REQUEST_MAX)?;
        require(
            members
                .iter()
                .all(|m| allowed.as_array().map(|a| a.contains(m)).unwrap_or(false)),
        )?;
        let proof = record(
            r,
            "SELECT response_utf8 FROM delivery_receipts WHERE batch_id=?1 AND terminal='rejected'",
            &[&parent],
        )?;
        let proof = pf::parse(str_at(&proof, 0)?.as_bytes(), wire::RECEIPT_MAX)?;
        Some(wire::Parent {
            batch_id: parent.into(),
            request_digest: str_at(&p, 0)?.into(),
            rejection_token: wire::text(&proof["data"], "rejectionToken")?.into(),
        })
    } else {
        require(number(row, 6)? == 0)?;
        None
    };
    let result = wire::Batch::new(
        instance.into(),
        id.into(),
        str_at(row, 7)?.into(),
        cycles.into_values().collect(),
        parts,
        parent,
    )?;
    require(
        result.request_digest == str_at(row, 3)?
            && pf::sha(result.bytes()?.as_bytes()) == str_at(row, 2)?,
    )?;
    if let Some(raw) = row[1].as_str() {
        require(
            pf::sha(raw.as_bytes()) == str_at(row, 2)?
                && serde_json::to_value(&result).map_err(|_| "profile_ledger_invalid")?
                    == pf::parse(raw.as_bytes(), wire::REQUEST_MAX)?,
        )?;
    }
    Ok(result)
}
fn delivery_check(r: &Connection, instance: &str) -> LocalResult<()> {
    use crate::domain::local_delivery::{classify, verify_success, Reply};
    super::delivery::verify_schema(r)?;
    require(count(r,"SELECT count(*) FROM delivery_settings",&[])?==1&&count(r,"SELECT count(*) FROM delivery_batches WHERE body IS NOT NULL AND state NOT IN ('acknowledged','rejected')",&[])?<=8)?;
    each(r, "delivery_cycles", "cycle_id", |cid| {
        let b = built(r, cid, instance)?;
        let row=record(r,"SELECT manifest_sha,context_sha,cycle_digest,wire FROM delivery_cycles WHERE cycle_id=?1",&[&cid])?;
        require(
            str_at(&row, 0)? == b.cycle.manifest_sha256
                && str_at(&row, 1)? == b.cycle.context_sha256
                && str_at(&row, 2)? == wire::cycle_digest(&b.cycle)?
                && pf::parse(str_at(&row, 3)?.as_bytes(), wire::REQUEST_MAX)?
                    == serde_json::to_value(&b.cycle).map_err(|_| "profile_ledger_invalid")?,
        )?;
        require(
            count(
                r,
                "SELECT count(*) FROM delivery_parts WHERE cycle_id=?1",
                &[&cid],
            )? == b.parts.len() as i64,
        )?;
        for part in &b.parts {
            let p=record(r,"SELECT parts,cycle_id,source_sha,content_digest,point_ids,state,batch_id,receipt_id FROM delivery_parts WHERE sample_id=?1 AND part=?2",&[&part.sample_id,&part.part])?;
            require(
                number(&p, 0)? == part.parts as i64
                    && str_at(&p, 1)? == cid
                    && str_at(&p, 2)? == part.source_sha256
                    && str_at(&p, 3)? == part.content_digest
                    && local_json(str_at(&p, 4)?, 128 * 1024)? == json!(part.point_ids),
            )?;
            match str_at(&p, 5)? {
                "pending" => require(p[6].is_null() && p[7].is_null())?,
                "prepared" | "needs_review" => {
                    require(p[7].is_null())?;
                    let batch = str_at(&p, 6)?;
                    require(
                        count(
                            r,
                            "SELECT count(*) FROM delivery_batches WHERE batch_id=?1",
                            &[&batch],
                        )? == 1,
                    )?;
                    require(count(r,"SELECT count(*) FROM sample_references WHERE sample_id=?1 AND reference_id=?2",&[&part.sample_id,&format!("delivery-batch:{batch}")])?==1)?;
                }
                "acknowledged" => {
                    let batch = str_at(&p, 6)?;
                    let receipt = str_at(&p, 7)?;
                    require(count(r,"SELECT count(*) FROM delivery_receipts WHERE batch_id=?1 AND receipt_id=?2 AND terminal='acknowledged'",&[&batch,&receipt])?==1)?;
                }
                _ => return Err("profile_ledger_invalid".into()),
            }
        }
        let remaining = count(
            r,
            "SELECT count(*) FROM delivery_parts WHERE cycle_id=?1 AND state!='acknowledged'",
            &[&cid],
        )?;
        for sample in b.cycle.transport_manifest {
            require(
                count(
                    r,
                    "SELECT count(*) FROM sample_references WHERE sample_id=?1 AND reference_id=?2",
                    &[&sample.sample_id, &format!("delivery-cycle:{cid}")],
                )? == if remaining == 0 { 0 } else { 1 },
            )?;
        }
        Ok(())
    })?;
    each(r, "delivery_batches", "batch_id", |id| {
        let row=record(r,"SELECT state,body,body_sha,request_digest,members,parent_id,parent_depth,created_at,target_id,attempt,next_attempt_at,settings_revision FROM delivery_batches WHERE batch_id=?1",&[&id])?;
        let state = str_at(&row, 0)?;
        require(
            crate::domain::local_configuration::valid_id(id)
                && [
                    "prepared",
                    "inflight",
                    "unknown",
                    "retry_wait",
                    "blocked",
                    "expired_unconfirmed",
                    "needs_review",
                    "rejected",
                    "acknowledged",
                ]
                .contains(&state)
                && number(&row, 6)? <= 8
                && number(&row, 6)? >= 0
                && number(&row, 9)? >= 0,
        )?;
        wire::time(str_at(&row, 7)?)?;
        wire::time(str_at(&row, 10)?)?;
        if str_at(&row, 3)?.is_empty() {
            require(
                state == "blocked"
                    && row[1].is_null()
                    && str_at(&row, 2)?.is_empty()
                    && row[5].is_null()
                    && number(&row, 6)? == 0
                    && number(&row, 9)? == 0,
            )?;
            let members = local_json(str_at(&row, 4)?, wire::REQUEST_MAX)?;
            let cid = wire::text(&members, "cycleId")?;
            let samples = members["sampleIds"]
                .as_array()
                .ok_or("profile_ledger_invalid")?;
            require(
                count(r, "SELECT count(*) FROM samples WHERE cycle_id=?1", &[&cid])?
                    == samples.len() as i64
                    && count(
                        r,
                        "SELECT count(*) FROM delivery_parts WHERE cycle_id=?1",
                        &[&cid],
                    )? == 0,
            )?;
            let mut seen = std::collections::BTreeSet::new();
            for sample in samples {
                let sid = sample.as_str().ok_or("profile_ledger_invalid")?;
                require(seen.insert(sid)&&count(r,"SELECT count(*) FROM samples WHERE id=?1 AND cycle_id=?2",&[&sid,&cid])?==1&&count(r,"SELECT count(*) FROM sample_references WHERE sample_id=?1 AND reference_id=?2",&[&sid,&format!("delivery-blocked:{cid}")])?==1)?;
            }
            return Ok(());
        }
        let batch = batch(r, id, &row, instance)?;
        if !["acknowledged", "rejected"].contains(&state) {
            require(row[1].is_string())?;
            let settings = record(r, "SELECT payload FROM delivery_settings WHERE id=1", &[])?;
            let settings: crate::domain::local_delivery::DeliverySettings =
                serde_json::from_str(str_at(&settings, 0)?)
                    .map_err(|_| "profile_ledger_invalid")?;
            require(settings.target_id.as_deref() == Some(str_at(&row, 8)?))?;
            for p in &batch.samples {
                require(count(r,"SELECT count(*) FROM delivery_parts WHERE sample_id=?1 AND part=?2 AND batch_id=?3 AND state='prepared'",&[&p.sample_id,&p.part,&id])?==1)?;
            }
            require(
                count(
                    r,
                    "SELECT count(*) FROM delivery_receipts WHERE batch_id=?1",
                    &[&id],
                )? == 0,
            )?;
        } else {
            let receipt=record(r,"SELECT receipt_id,request_digest,response_utf8,response_sha,committed_at,proof_expires_at,terminal FROM delivery_receipts WHERE batch_id=?1",&[&id])?;
            let raw = str_at(&receipt, 2)?;
            let value = pf::parse(raw.as_bytes(), wire::RECEIPT_MAX)?;
            let data = &value["data"];
            require(
                str_at(&receipt, 1)? == batch.request_digest
                    && str_at(&receipt, 3)? == pf::sha(raw.as_bytes())
                    && str_at(&receipt, 6)? == state
                    && str_at(&receipt, 0)? == wire::text(data, "receiptId")?,
            )?;
            if state == "acknowledged" {
                verify_success(&batch, &value)?;
                require(
                    row[1].is_null()
                        && str_at(&receipt, 4)? == wire::text(data, "committedAt")?
                        && str_at(&receipt, 5)? == wire::text(data, "proofExpiresAt")?,
                )?;
                for p in &batch.samples {
                    require(count(r,"SELECT count(*) FROM delivery_parts WHERE sample_id=?1 AND part=?2 AND batch_id=?3 AND receipt_id=?4 AND state='acknowledged'",&[&p.sample_id,&p.part,&id,&str_at(&receipt,0)?])?==1)?;
                }
            } else {
                require(
                    matches!(
                        classify(
                            &batch,
                            value["code"].as_u64().ok_or("profile_ledger_invalid")? as u16,
                            "application/json",
                            raw.as_bytes(),
                            None,
                            1,
                            0
                        ),
                        Reply::Rejected { .. }
                    ) && str_at(&receipt, 4)? == wire::text(data, "recordedAt")?
                        && str_at(&receipt, 5)? == wire::text(data, "rejectionExpiresAt")?,
                )?;
            }
        }
        Ok(())
    })?;
    each(r, "sample_delivery", "sample_id", |sid| {
        let d = record(
            r,
            "SELECT state,acknowledged_at FROM sample_delivery WHERE sample_id=?1",
            &[&sid],
        )?;
        let parts=record(r,"SELECT count(*),coalesce(max(parts),0),coalesce(sum(CASE WHEN state='acknowledged' THEN 1 ELSE 0 END),0) FROM delivery_parts WHERE sample_id=?1",&[&sid])?;
        let ack = number(&parts, 0)? > 0 && parts[0] == parts[1] && parts[0] == parts[2];
        require((str_at(&d, 0)? == "acknowledged") == ack)?;
        if ack {
            wire::time(str_at(&d, 1)?)?;
        } else {
            require(d[1].is_null())?;
        }
        Ok(())
    })?;
    Ok(())
}
/// sealed cold与native恢复后完全相同；两RO连接close完成前不打开任何原始DB FD。
pub(super) fn full_check(dir: &std::path::Path, instance: &str) -> LocalResult<()> {
    let ro = |role: &str| {
        Connection::open_with_flags(
            dir.join(format!("{role}.sqlite")),
            rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
        )
        .map_err(super::sql_error)
    };
    let config = ro("config")?;
    let runtime = match ro("runtime") {
        Ok(r) => r,
        Err(e) => {
            config.close().map_err(|(_, e)| super::sql_error(e))?;
            return Err(e);
        }
    };
    let checked = (|| {
        for c in [&config, &runtime] {
            c.busy_timeout(std::time::Duration::from_millis(1000))
                .map_err(super::sql_error)?;
            c.execute_batch("PRAGMA trusted_schema=OFF; PRAGMA query_only=ON;")
                .map_err(super::sql_error)?;
        }
        core_check(&config, &runtime, instance)?;
        let version: u32 = runtime
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(super::sql_error)?;
        match version {
            2 => Ok(()),
            3 => delivery_check(&runtime, instance),
            4 => {
                delivery_check(&runtime, instance)?;
                super::sample_upload::full_check(&runtime, instance)
            }
            _ => Err("profile_ledger_invalid".into()),
        }
    })();
    let close_config = config.close().map_err(|(_, e)| super::sql_error(e));
    let close_runtime = runtime.close().map_err(|(_, e)| super::sql_error(e));
    checked?;
    close_config?;
    close_runtime
}
