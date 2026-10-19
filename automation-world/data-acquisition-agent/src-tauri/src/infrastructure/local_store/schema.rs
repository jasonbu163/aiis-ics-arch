//! 双库v1显式schema；普通rowid表、普通列索引，无ATTACH/视图/表达式或partial索引。
pub(super) const CONFIG_APP: i64 = 0x44414143;
pub(super) const RUNTIME_APP: i64 = 0x44414152;
pub(super) const CONFIG: &str = r#"
CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
INSERT INTO schema_migrations VALUES(1,strftime('%Y-%m-%dT%H:%M:%fZ','now'));
CREATE TABLE instance_metadata(id INTEGER PRIMARY KEY CHECK(id=1),instance_id TEXT NOT NULL, schema_version INTEGER NOT NULL CHECK(schema_version=1));
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
INSERT INTO schema_migrations VALUES(1,strftime('%Y-%m-%dT%H:%M:%fZ','now'));
CREATE TABLE runtime_metadata(id INTEGER PRIMARY KEY CHECK(id=1),instance_id TEXT NOT NULL,schema_version INTEGER NOT NULL CHECK(schema_version=1),clean_exit INTEGER NOT NULL,used_revision TEXT);
CREATE TABLE plc_sources(plc_id TEXT PRIMARY KEY,generation TEXT NOT NULL,next_seq INTEGER NOT NULL CHECK(next_seq>0),UNIQUE(plc_id,generation));
CREATE TABLE configuration_contexts(revision TEXT PRIMARY KEY,schema_version INTEGER NOT NULL CHECK(schema_version=1),sha256 TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE activation_journal(token TEXT PRIMARY KEY,revision TEXT NOT NULL REFERENCES configuration_contexts(revision),phase TEXT NOT NULL);
CREATE TABLE collection_cycles(id TEXT PRIMARY KEY,plc_id TEXT NOT NULL,generation TEXT NOT NULL,source_seq INTEGER NOT NULL,group_id TEXT NOT NULL,revision TEXT NOT NULL REFERENCES configuration_contexts(revision),started_at TEXT NOT NULL,finished_at TEXT NOT NULL,saved_at TEXT NOT NULL,quality TEXT NOT NULL,manifest TEXT NOT NULL,sha256 TEXT NOT NULL,expected_samples INTEGER NOT NULL,UNIQUE(plc_id,generation,source_seq));
CREATE TABLE samples(sample_order INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT NOT NULL UNIQUE,cycle_id TEXT NOT NULL REFERENCES collection_cycles(id),db_number INTEGER NOT NULL,plc_id TEXT NOT NULL,group_id TEXT NOT NULL,source_seq INTEGER NOT NULL,revision TEXT NOT NULL,quality TEXT NOT NULL,saved_at TEXT NOT NULL,schema_version INTEGER NOT NULL CHECK(schema_version=1),payload TEXT NOT NULL,sha256 TEXT NOT NULL,payload_bytes INTEGER NOT NULL,UNIQUE(cycle_id,db_number));
CREATE INDEX history_order ON samples(saved_at,id);
CREATE INDEX history_plc ON samples(plc_id,saved_at,id);
CREATE TABLE sample_delivery(sample_id TEXT PRIMARY KEY REFERENCES samples(id),state TEXT NOT NULL CHECK(state IN ('pending','acknowledged')),acknowledged_at TEXT);
CREATE TABLE sample_references(sample_id TEXT NOT NULL REFERENCES samples(id),reference_id TEXT NOT NULL,PRIMARY KEY(sample_id,reference_id));
CREATE TABLE runtime_events(id INTEGER PRIMARY KEY,event TEXT NOT NULL,resource TEXT NOT NULL,result TEXT NOT NULL,created_at TEXT NOT NULL);
"#;
pub(super) fn runtime_sql() -> String {
    RUNTIME.to_string()
}
