//! DAA-005自有tmp真实SQLite/LocalEngine验证：CAS、原子回滚、旧JSON/历史保全及物理归档去重。
use super::*;
use crate::{
    config::local_bootstrap::Bootstrap,
    domain::{
        local_configuration::*, local_sample::*, source_import::*, yaml_migration::MigrationPaths,
    },
    infrastructure::{plc_layout, tia_source},
    services::local_supervisor::LocalEngine,
};
use rusqlite::OptionalExtension;
use serde_json::{json, Value};
use std::collections::BTreeMap;
const MULTI: &str = include_str!("../../../tests/fixtures/source-import-multi-db/multi.db");
const TYPES: &str = include_str!("../../../tests/fixtures/source-import-multi-db/types.udt");
pub(super) fn profile(label: &str) -> PathBuf {
    let p = std::env::temp_dir()
        .canonicalize()
        .unwrap()
        .join(format!("daa005-test-{label}-{}", id()));
    std::fs::create_dir_all(&p).unwrap();
    println!("{}", json!({"event":"daa005_test_profile","path":p}));
    p
}
fn plc(n: u8) -> Plc {
    Plc {
        id: id(),
        name: format!("Synthetic {n}"),
        enabled: false,
        host: format!("127.0.0.{n}"),
        port: 102,
        rack: 0,
        slot: 1,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    }
}
pub(super) fn engine(p: &Path) -> Arc<LocalEngine> {
    LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.into(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap()
}
pub(super) fn req(c: &Configuration, etag: &str, docs: &[(&str, &str)]) -> ImportRequest {
    let sources: Vec<_> = docs
        .iter()
        .map(|(name, body)| SourceDocument {
            id: String::new(),
            name: (*name).into(),
            content: (*body).into(),
            sha256: digest(body),
            plc_id: c.plcs[0].id.clone(),
            db_number: None,
            diagnostics: vec![],
            lineage_id: None,
        })
        .collect();
    let mut r = ImportRequest {
        raw_proofs: sources
            .iter()
            .map(|s| RawProof {
                sha256: s.sha256.clone(),
                bytes: s.content.len(),
            })
            .collect(),
        sources,
        expected_etag: etag.into(),
        confirm: false,
        stage: Some("preview".into()),
        target_plc_id: Some(c.plcs[0].id.clone()),
        mappings: vec![],
        preview_token: None,
    };
    r.mappings = tia_source::identify(c, &r)
        .unwrap()
        .blocks
        .into_iter()
        .filter(|b| b.block_key.kind == "DATA_BLOCK")
        .enumerate()
        .map(|(n, b)| BlockMapping {
            source_index: b.source_index,
            block_key: b.block_key,
            selected: true,
            db_number: Some(b.suggested_db_number.unwrap_or(501 + n as u16)),
            target_id: b.target_id,
        })
        .collect();
    r
}
pub(super) fn confirm(e: &LocalEngine, mut r: ImportRequest) -> ImportPreview {
    let p = e.import_selected(r.clone()).unwrap();
    assert!(p.can_confirm, "{:?}", p.issues);
    r.confirm = true;
    r.stage = Some("confirm".into());
    r.preview_token = p.preview_token.clone();
    let result = e.import_selected(r).unwrap();
    assert_eq!(result.configuration, p.configuration);
    result
}
pub(super) fn dump(conn: &Connection, tables: &[&str]) -> Value {
    let mut result = serde_json::Map::new();
    for table in tables {
        let mut stmt = conn
            .prepare(&format!("SELECT * FROM {table} ORDER BY rowid"))
            .unwrap();
        let n = stmt.column_count();
        let rows = stmt
            .query_map([], |row| {
                Ok((0..n)
                    .map(|i| match row.get_ref(i).unwrap() {
                        rusqlite::types::ValueRef::Null => Value::Null,
                        rusqlite::types::ValueRef::Integer(v) => json!(v),
                        rusqlite::types::ValueRef::Real(v) => json!(v),
                        rusqlite::types::ValueRef::Text(v) | rusqlite::types::ValueRef::Blob(v) => {
                            json!(String::from_utf8_lossy(v))
                        }
                    })
                    .collect::<Vec<_>>())
            })
            .unwrap()
            .collect::<Result<Vec<_>, _>>()
            .unwrap();
        result.insert((*table).into(), json!(rows));
    }
    Value::Object(result)
}
pub(super) fn protected(s: &Stores) -> Value {
    json!({"config":dump(&s.config,&["schema_migrations","instance_metadata","configuration_revisions","active_selection","activation_intents"]),"runtime":dump(&s.runtime,&["schema_migrations","runtime_metadata","plc_sources","configuration_contexts","activation_journal","collection_cycles","samples","sample_delivery","sample_references"]),"receipt":s.config.query_row("SELECT content FROM source_documents WHERE substr(name,1,25)='__daa_yaml_migration_v1__'",[],|r|r.get::<_,String>(0)).optional().unwrap()})
}
#[test]
fn engine_identify_preview_cas_token_subset_and_reload() {
    let p = profile("engine");
    let e = engine(&p);
    let v = e.configuration().unwrap();
    let mut c = v.draft;
    c.plcs = vec![plc(1), plc(2)];
    let v = e.save(c, v.etag).unwrap();
    let mut r = req(
        &v.draft,
        &v.etag,
        &[("multi.db", MULTI), ("types.udt", TYPES)],
    );
    r.mappings[5].selected = false;
    let before = e
        .storage
        .call(true, |s| {
            Ok((
                dump(&s.config, &["configuration_draft", "source_documents"]),
                protected(s),
            ))
        })
        .unwrap();
    let mut identify = r.clone();
    identify.stage = Some("identify".into());
    assert_eq!(e.identify_sources(&identify).unwrap().db_count, 6);
    let preview = e.import_selected(r.clone()).unwrap();
    assert!(preview.can_confirm);
    assert_eq!(e.configuration().unwrap().etag, v.etag);
    let after = e
        .storage
        .call(true, |s| {
            Ok((
                dump(&s.config, &["configuration_draft", "source_documents"]),
                protected(s),
            ))
        })
        .unwrap();
    assert_eq!(before, after);
    let mut forged = r.clone();
    forged.confirm = true;
    forged.stage = Some("confirm".into());
    forged.preview_token = Some(id());
    assert!(e.import_selected(forged).is_err());
    assert_eq!(e.configuration().unwrap().etag, v.etag);
    let preview = e.import_selected(r.clone()).unwrap();
    let mut tampered = r.clone();
    tampered.confirm = true;
    tampered.stage = Some("confirm".into());
    tampered.preview_token = preview.preview_token;
    tampered.mappings[0].db_number = Some(600);
    assert!(e.import_selected(tampered).is_err());
    let old = e.import_selected(r.clone()).unwrap();
    e.import_preview.lock().unwrap().as_mut().unwrap().3 =
        std::time::Instant::now() - Duration::from_secs(301);
    let mut expired = r.clone();
    expired.confirm = true;
    expired.stage = Some("confirm".into());
    expired.preview_token = old.preview_token;
    assert!(e.import_selected(expired).is_err());
    let mut invalid = r.clone();
    invalid.mappings[1].db_number = invalid.mappings[0].db_number;
    let blocked = e.import_selected(invalid.clone()).unwrap();
    assert!(!blocked.can_confirm);
    invalid.confirm = true;
    invalid.stage = Some("confirm".into());
    invalid.preview_token = blocked.preview_token;
    assert!(e.import_selected(invalid).is_err());
    assert_eq!(e.configuration().unwrap().etag, v.etag);
    let cached = e.import_selected(r.clone()).unwrap();
    let mut downgraded = r.clone();
    downgraded.stage = None;
    downgraded.confirm = true;
    assert!(e.import_selected(downgraded).is_err());
    crate::commands::local_acquisition::dispatch(e.clone(), "daa_get_configuration", json!({}))
        .unwrap();
    let mut reloaded = r.clone();
    reloaded.confirm = true;
    reloaded.stage = Some("confirm".into());
    reloaded.preview_token = cached.preview_token;
    assert!(e.import_selected(reloaded).is_err());
    let committed = confirm(&e, r.clone());
    assert_eq!(committed.configuration.dbs.len(), 5);
    let v = e.configuration().unwrap();
    assert_eq!(v.draft, committed.configuration);
    assert!(v.active.is_none());
    assert!(!e.bootstrap.read_allowed);
    let mut repeat = req(
        &v.draft,
        &v.etag,
        &[("multi.db", MULTI), ("types.udt", TYPES)],
    );
    for m in &mut repeat.mappings {
        m.selected = m.block_key.name != "Zeta";
    }
    let unchanged = confirm(&e, repeat);
    assert!(unchanged.unchanged);
    assert_eq!(unchanged.etag, v.etag);
    r.expected_etag = String::from("stale");
    assert!(e.import_selected(r).is_err());
    e.shutdown();
    drop(e);
    let reopened = engine(&p);
    let again = reopened.configuration().unwrap();
    assert_eq!(again.etag, v.etag);
    assert_eq!(again.draft, v.draft);
    reopened.shutdown();
    std::fs::write(
        p.join("evidence.json"),
        serde_json::to_vec_pretty(
            &json!({"before":before,"after":after,"etag":v.etag,"configuration":v.draft}),
        )
        .unwrap(),
    )
    .unwrap();
}
#[test]
fn store_rollback_and_same_bytes_two_plcs_distinct_names() {
    let p = profile("archive");
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let mut c = Configuration::default();
    c.plcs = vec![plc(1), plc(2)];
    let etag = s.configuration().unwrap().etag;
    let v = s.save_draft(&c, &etag).unwrap();
    let r = req(&c, &v.etag, &[("multi.db", MULTI), ("types.udt", TYPES)]);
    let p1 = tia_source::plan(&c, &r).unwrap();
    assert!(p1.can_confirm);
    let before = dump(&s.config, &["configuration_draft", "source_documents"]);
    s.config.execute_batch("CREATE TEMP TRIGGER daa005_fail BEFORE INSERT ON source_documents WHEN NEW.name='types.udt' BEGIN SELECT RAISE(ABORT,'owned test rollback'); END;").unwrap();
    assert!(s.save_draft(&p1.configuration, &v.etag).is_err());
    assert_eq!(
        before,
        dump(&s.config, &["configuration_draft", "source_documents"])
    );
    s.config.execute_batch("DROP TRIGGER daa005_fail").unwrap();
    let v = s.save_draft(&p1.configuration, &v.etag).unwrap();
    let archive = dump(&s.config, &["source_documents"]);
    let mut swapped = v.draft.clone();
    swapped.plcs.swap(0, 1);
    let r = req(
        &swapped,
        &v.etag,
        &[("other-name.db", MULTI), ("other-types.udt", TYPES)],
    );
    let p2 = tia_source::plan(&v.draft, &r).unwrap();
    assert!(p2.can_confirm, "{:?}", p2.issues);
    assert_eq!(p2.configuration.dbs.len(), 12);
    assert_eq!(p2.configuration.sources.len(), 4);
    let v2 = s.save_draft(&p2.configuration, &v.etag).unwrap();
    assert_eq!(archive, dump(&s.config, &["source_documents"]));
    assert!(validate(&v2.draft).iter().all(|i| i.code != "db_invalid"));
    let mut forged = v2.draft.clone();
    forged.sources[0].content.push(' ');
    forged.sources[0].sha256 = digest(&forged.sources[0].content);
    assert!(s.save_draft(&forged, &v2.etag).is_err());
    let original = s
        .config
        .query_row("SELECT content FROM source_documents LIMIT 1", [], |r| {
            r.get::<_, String>(0)
        })
        .unwrap();
    s.config
        .execute(
            "UPDATE source_documents SET content='owned conflict' WHERE content=?1",
            [&original],
        )
        .unwrap();
    let mut changed = v2.draft.clone();
    changed.storage.retention_days = 8;
    assert!(s.save_draft(&changed, &v2.etag).is_err());
    assert_eq!(s.configuration().unwrap().etag, v2.etag);
    s.config
        .execute(
            "UPDATE source_documents SET content=?1 WHERE content='owned conflict'",
            [original],
        )
        .unwrap();
    assert_eq!(archive, dump(&s.config, &["source_documents"]));
    s.clean_exit().unwrap();
}
pub(super) fn old_seed(s: &mut Stores, p: &Path) -> Configuration {
    let points = p.join("empty-points.yaml");
    let policy = p.join("empty-policy.yaml");
    std::fs::write(&points, "# owned empty\n").unwrap();
    std::fs::write(&policy, "# owned empty\n").unwrap();
    let paths = MigrationPaths {
        points,
        policy,
        points_origin: "owned".into(),
        policy_origin: "owned".into(),
    };
    let migration = crate::services::local_yaml_migration::startup(s, Some(&paths));
    assert_eq!(migration.status, "skipped_empty");
    let mut c = Configuration::default();
    c.plcs = vec![plc(1), plc(2)];
    let text="DATA_BLOCK \"Old\" { S7_Optimized_Access := 'FALSE' } VAR value: WORD; END_VAR BEGIN END_DATA_BLOCK";
    let r = req(&c, "", &[("old.db", text)]);
    c = tia_source::plan(&c, &r).unwrap().configuration;
    c.dbs[0].import_binding = None;
    c.sources[0].lineage_id = None;
    c.sources[0].db_number = Some(501);
    c.groups.push(Group {
        id: id(),
        plc_id: c.plcs[0].id.clone(),
        name: "Seed only".into(),
        enabled: true,
        interval_ms: 500,
    });
    c.plcs[0].enabled = true;
    let xs = plc_layout::preview(&c, &c.dbs[0].id).unwrap();
    let db = c.dbs[0].id.clone();
    plc_layout::confirm(
        &mut c,
        &db,
        &xs.iter().map(|x| x.point_id.clone()).collect::<Vec<_>>(),
    )
    .unwrap();
    c.points[0].enabled = true;
    c.points[0].group_id = Some(c.groups[0].id.clone());
    c.points[0].name = "User value".into();
    c.points[0].name_mode = None;
    c.points[0].address.as_mut().unwrap().origin = "manual".into();
    c.points[0].address.as_mut().unwrap().reason = "Seed manual review".into();
    let v = s.configuration().unwrap();
    let v = s.save_draft(&c, &v.etag).unwrap();
    let (token, revision) = s.prepare_activation(&v.etag, None, false).unwrap();
    s.prepare_context(&token, &revision).unwrap();
    s.select_active(&token, &revision).unwrap();
    s.finish_activation(&token).unwrap();
    for round in 0..2 {
        let points = BTreeMap::from([(
            501,
            BTreeMap::from([(
                c.points[0].id.clone(),
                PointFact {
                    definition: c.points[0].clone(),
                    value: json!(round),
                    observed_at: now(),
                    quality: "good".into(),
                    reason: None,
                },
            )]),
        )]);
        let out = s
            .commit_cycle(CycleInput {
                plc_id: c.plcs[0].id.clone(),
                group_id: c.groups[0].id.clone(),
                revision: revision.clone(),
                started_at: now(),
                finished_at: now(),
                origin: "daa005-owned-seed".into(),
                points,
                reads: vec![],
            })
            .unwrap();
        if round == 1 {
            s.runtime.execute("UPDATE sample_delivery SET state='acknowledged' WHERE sample_id IN (SELECT id FROM samples WHERE cycle_id=?1)",[out["cycleId"].as_str().unwrap()]).unwrap();
            s.runtime.execute("INSERT INTO sample_references SELECT id,'daa005-owned-ref' FROM samples WHERE cycle_id=?1",[out["cycleId"].as_str().unwrap()]).unwrap();
        }
    }
    c
}
#[test]
fn old_v1_raw_decode_history_receipt_and_unselected_protected() {
    let p = profile("old-history");
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let old = old_seed(&mut s, &p);
    let payload: String = s
        .config
        .query_row("SELECT payload FROM configuration_draft", [], |r| r.get(0))
        .unwrap();
    assert!(!payload.contains("importBinding"));
    assert!(!payload.contains("lineageId"));
    let v = s.configuration().unwrap();
    assert_eq!(
        payload,
        s.config
            .query_row("SELECT payload FROM configuration_draft", [], |r| r
                .get::<_, String>(0))
            .unwrap()
    );
    let before = protected(&s);
    let archives = dump(&s.config, &["source_documents"]);
    let schema = dump(&s.config, &["sqlite_master"]);
    // New DB import touches only draft/new sources and keeps all old source/point/active/history bytes.
    let r = req(
        &v.draft,
        &v.etag,
        &[("multi.db", MULTI), ("types.udt", TYPES)],
    );
    let mut r = r;
    for m in &mut r.mappings {
        m.db_number = m.db_number.map(|n| n + 1000);
    }
    let plan = tia_source::plan(&v.draft, &r).unwrap();
    assert!(plan.can_confirm);
    let v2 = s.save_draft(&plan.configuration, &v.etag).unwrap();
    assert_eq!(before, protected(&s));
    assert_eq!(schema, dump(&s.config, &["sqlite_master"]));
    assert!(v2.draft.points.contains(&old.points[0]));
    assert!(v2.draft.dbs.contains(&old.dbs[0]));
    assert!(v2.draft.sources.contains(&old.sources[0]));
    for conn in [&s.config, &s.runtime] {
        assert_eq!(
            conn.query_row("PRAGMA user_version", [], |r| r.get::<_, u32>(0))
                .unwrap(),
            1
        );
    }
    let before_engine = protected(&s);
    let etag = v2.etag.clone();
    s.clean_exit().unwrap();
    drop(s);
    let e = engine(&p);
    let v = e.configuration().unwrap();
    assert_eq!(v.etag, etag);
    let mut forged = v.draft.clone();
    forged.dbs[0].import_binding = Some(ImportBinding {
        block_key: BlockKey {
            kind: "DATA_BLOCK".into(),
            name: "Forged".into(),
        },
        lineage_id: id(),
        udt_source_ids: vec![],
    });
    assert!(e.save(forged, v.etag.clone()).is_err());
    let got = e.storage.call(true, |s| Ok(protected(s))).unwrap();
    assert_eq!(before_engine, got);
    std::fs::write(p.join("protected-evidence.json"),serde_json::to_vec_pretty(&json!({"before":before,"after":got,"oldArchives":archives,"etag":etag,"schema":schema})).unwrap()).unwrap();
    e.shutdown();
}
#[test]
fn offset_preview_confirm_reload_cas_and_manual_guard() {
    let p = profile("offset-engine");
    let e = engine(&p);
    let mut v = e.configuration().unwrap();
    v.draft.plcs.push(plc(1));
    let v = e.save(v.draft, v.etag).unwrap();
    let layout = include_str!("../../../tests/fixtures/source-import-multi-db/layout.db");
    let r = req(&v.draft, &v.etag, &[("layout.db", layout)]);
    confirm(&e, r);
    let v = e.configuration().unwrap();
    let db = v
        .draft
        .dbs
        .iter()
        .find(|d| d.name == "Arrays")
        .unwrap()
        .id
        .clone();
    let before = v.clone();
    let xs = e.offsets_at(db.clone(), Some(v.etag.clone())).unwrap();
    assert_eq!(e.configuration().unwrap().draft, before.draft);
    let digest = xs[0].layout_digest.clone();
    let ids = xs.iter().map(|x| x.point_id.clone()).collect();
    let v = e
        .confirm_offsets_at(db.clone(), ids, v.etag, Some(digest))
        .unwrap();
    assert_eq!(v.draft.dbs.iter().find(|d| d.id == db).unwrap().length, 34);
    assert!(v.draft.points.iter().filter(|p| p.db_id == db).all(|p| p
        .address
        .as_ref()
        .unwrap()
        .confirmed));
    let xs = e.offsets_at(db.clone(), Some(v.etag.clone())).unwrap();
    let mut edit = v.draft.clone();
    let point = edit
        .points
        .iter_mut()
        .find(|p| p.id == xs[0].point_id)
        .unwrap();
    point.address = Some(Address {
        offset: 200,
        bit: None,
        confirmed: false,
        origin: "manual".into(),
        reason: "Keep manual".into(),
    });
    let saved = e.save(edit, v.etag).unwrap();
    assert!(e
        .confirm_offsets_at(
            db.clone(),
            vec![xs[0].point_id.clone()],
            saved.etag.clone(),
            Some(xs[0].layout_digest.clone())
        )
        .is_err());
    let xs = e.offsets_at(db.clone(), Some(saved.etag.clone())).unwrap();
    assert!(e
        .confirm_offsets_at(
            db.clone(),
            vec![xs[0].point_id.clone()],
            saved.etag.clone(),
            Some(xs[0].layout_digest.clone())
        )
        .is_err());
    assert_eq!(e.configuration().unwrap().draft, saved.draft);
    e.shutdown();
}
