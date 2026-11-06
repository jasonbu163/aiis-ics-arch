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
    use rusqlite::OptionalExtension;
    let mut expected_count = 0;
    for statement in sql.split(';') {
        let expected = statement.trim();
        if !expected.starts_with("CREATE TABLE ")
            && !expected.starts_with("CREATE INDEX ")
            && !expected.starts_with("CREATE UNIQUE INDEX ")
        {
            continue;
        }
        expected_count += 1;
        let name = expected
            .split_whitespace()
            .nth(if expected.starts_with("CREATE UNIQUE INDEX ") {
                3
            } else {
                2
            })
            .and_then(|s| s.split('(').next())
            .ok_or("schema_structure_mismatch")?;
        let actual: Option<String> = c
            .query_row("SELECT sql FROM sqlite_master WHERE name=?1", [name], |r| {
                r.get(0)
            })
            .optional()
            .map_err(super::sql_error)?;
        if actual.as_deref() != Some(expected) {
            return Err("schema_structure_mismatch".into());
        }
    }
    let actual: u32 = c
        .query_row(
            "SELECT count(*) FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%'",
            [],
            |r| r.get(0),
        )
        .map_err(super::sql_error)?;
    if actual != expected_count {
        return Err("schema_structure_mismatch".into());
    }
    Ok(())
}
