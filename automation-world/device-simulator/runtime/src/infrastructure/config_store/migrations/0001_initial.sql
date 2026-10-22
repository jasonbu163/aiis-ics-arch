-- DS配置v1：只用于新空DS库；运行值和loaded身份永不持久化。
CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, migration_sha256 TEXT NOT NULL, applied_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
CREATE TABLE workspace_metadata(singleton INTEGER PRIMARY KEY CHECK(singleton=1), profile_id TEXT NOT NULL UNIQUE, format_version TEXT NOT NULL, created_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
CREATE TABLE source_blobs(sha256 TEXT PRIMARY KEY, utf8 BLOB NOT NULL, byte_len INTEGER NOT NULL CHECK(byte_len=length(utf8)));
CREATE TABLE source_versions(version_id TEXT PRIMARY KEY, lineage_id TEXT NOT NULL, blob_sha256 TEXT NOT NULL REFERENCES source_blobs(sha256), logical_name TEXT NOT NULL, import_profile TEXT NOT NULL, metadata BLOB NOT NULL);
CREATE TABLE configuration_draft(singleton INTEGER PRIMARY KEY CHECK(singleton=1), etag TEXT NOT NULL, canonical_payload BLOB NOT NULL, sha256 TEXT NOT NULL, updated_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
CREATE TABLE configuration_revisions(revision_id TEXT PRIMARY KEY, saved_seq INTEGER NOT NULL UNIQUE, payload BLOB NOT NULL, sha256 TEXT NOT NULL, created_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
CREATE TABLE instance_selection(instance_id TEXT PRIMARY KEY, revision_id TEXT NOT NULL REFERENCES configuration_revisions(revision_id), slice_sha256 TEXT NOT NULL, previous_revision_id TEXT REFERENCES configuration_revisions(revision_id), selection_etag TEXT NOT NULL);
CREATE INDEX source_versions_blob ON source_versions(blob_sha256);
CREATE INDEX instance_selection_revision ON instance_selection(revision_id);
