//! 受控临时双库/完整周期/身份恢复和解析黄金验证；ACK种子只存在cfg(test)模块。
use super::*;
use crate::{
    config::local_bootstrap::Bootstrap,
    domain::{local_configuration::*, local_runtime::HistoryQuery, local_sample::*},
    infrastructure::{
        local_decode, local_fixture::FixtureSet, managed_s7::Transport, plc_layout, tia_source,
    },
    services::{local_scheduler, local_supervisor::LocalEngine},
};
use serde_json::{json, Value};
use std::time::{Duration, Instant};
fn profile() -> PathBuf {
    let p = std::env::temp_dir()
        .canonicalize()
        .unwrap()
        .join(format!("daa-002-r2-test-{}", id()));
    std::fs::create_dir(&p).unwrap();
    std::fs::write(p.join(".daa-local-validation-owner"), "DAA-002-r2-owned\n").unwrap();
    p
}
fn plc(port: u16) -> Plc {
    Plc {
        id: id(),
        name: format!("Fixture {port}"),
        enabled: true,
        host: "127.0.0.1".into(),
        port,
        rack: 0,
        slot: 1,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    }
}
fn source(p: &str, name: &str, text: &str, n: Option<u16>) -> SourceDocument {
    SourceDocument {
        id: String::new(),
        name: name.into(),
        content: text.into(),
        sha256: String::new(),
        plc_id: p.into(),
        db_number: n,
        diagnostics: vec![],
        lineage_id: None,
    }
}
fn configuration() -> Configuration {
    let mut c = Configuration::default();
    c.plcs = vec![plc(31001), plc(31002)];
    for p in c.plcs.clone() {
        let g = Group {
            id: id(),
            plc_id: p.id.clone(),
            name: "cross DB".into(),
            enabled: true,
            interval_ms: 500,
        };
        c.groups.push(g.clone());
        for db in 1..=2 {
            c = tia_source::import(
                &c,
                vec![source(
                    &p.id,
                    &format!("flat{db}.db"),
                    &include_str!("../../../tests/fixtures/local-acquisition/flat.db")
                        .replace("Flat", &format!("Flat{db}")),
                    Some(db),
                )],
            )
            .unwrap()
            .configuration;
            let d = c
                .dbs
                .iter()
                .find(|d| d.plc_id == p.id && d.number == db)
                .unwrap()
                .id
                .clone();
            let changes = plc_layout::preview(&c, &d).unwrap();
            plc_layout::confirm(
                &mut c,
                &d,
                &changes
                    .iter()
                    .map(|x| x.point_id.clone())
                    .collect::<Vec<_>>(),
            )
            .unwrap();
            for pt in c.points.iter_mut().filter(|x| x.db_id == d) {
                pt.enabled = true;
                pt.group_id = Some(g.id.clone());
            }
        }
    }
    assert!(validate(&c).is_empty(), "{:?}", validate(&c));
    c
}
fn seed_engine(
    e: &Arc<LocalEngine>,
    c: &Configuration,
) -> crate::domain::local_runtime::ConfigurationView {
    let mut base = c.clone();
    base.dbs.clear();
    base.points.clear();
    base.sources.clear();
    let v = e.configuration().unwrap();
    let v = e.save(base, v.etag).unwrap();
    e.import(c.sources.clone(), v.etag.clone(), false).unwrap();
    e.import(c.sources.clone(), v.etag, true).unwrap();
    let mut v = e.configuration().unwrap();
    for point in &mut v.draft.points {
        let number = v
            .draft
            .dbs
            .iter()
            .find(|d| d.id == point.db_id)
            .unwrap()
            .number;
        let original = c
            .points
            .iter()
            .find(|p| {
                p.plc_id == point.plc_id
                    && p.source_path == point.source_path
                    && c.dbs.iter().any(|d| d.id == p.db_id && d.number == number)
            })
            .unwrap();
        point.address = original.address.clone();
        point.enabled = original.enabled;
        point.group_id = original.group_id.clone();
    }
    e.save(v.draft, v.etag).unwrap()
}
fn activated(s: &mut Stores, c: &Configuration) -> String {
    let v = s.configuration().unwrap();
    s.save_draft(c, &v.etag).unwrap();
    let v = s.configuration().unwrap();
    let (t, r) = s
        .prepare_activation(&v.etag, v.active.as_deref(), false)
        .unwrap();
    s.prepare_context(&t, &r).unwrap();
    s.select_active(&t, &r).unwrap();
    s.finish_activation(&t).unwrap();
    r
}
fn cycle(c: &Configuration, r: &str) -> CycleInput {
    let f: FixtureSet = serde_json::from_str(include_str!(
        "../../../tests/fixtures/local-acquisition/transport.json"
    ))
    .unwrap();
    let mut t = crate::infrastructure::local_fixture::FixtureTransport::new(Arc::new(f));
    t.connect(&c.plcs[0]).unwrap();
    local_scheduler::collect(c, &c.plcs[0], &c.groups[0], r, &mut t, "fixture").unwrap()
}
#[test]
fn offset_and_full_structure_golden() {
    let mut c = Configuration::default();
    c.plcs.push(plc(31001));
    let p = c.plcs[0].id.clone();
    c = tia_source::import(
        &c,
        vec![source(
            &p,
            "flat.db",
            include_str!("../../../tests/fixtures/local-acquisition/flat.db"),
            Some(1),
        )],
    )
    .unwrap()
    .configuration;
    let d = c.dbs[0].id.clone();
    let changes = plc_layout::preview(&c, &d).unwrap();
    let golden: Value = serde_json::from_str(include_str!(
        "../../../tests/fixtures/local-acquisition/offsets.json"
    ))
    .unwrap();
    for x in &changes {
        let pt = c.points.iter().find(|p| p.id == x.point_id).unwrap();
        assert_eq!(
            json!([x.proposed.offset, x.proposed.bit]),
            golden[&pt.source_path]
        );
    }
    plc_layout::confirm(
        &mut c,
        &d,
        &changes
            .iter()
            .map(|x| x.point_id.clone())
            .collect::<Vec<_>>(),
    )
    .unwrap();
    assert_eq!(c.dbs[0].length, 10);
    let old = c.points.clone();
    let txt = include_str!("../../../tests/fixtures/local-acquisition/flat.db")
        .replace(" b0 : Bool;", " extra : Bool;\n b0 : Bool;");
    let changed = tia_source::plan(
        &c,
        &crate::domain::source_import::ImportRequest {
            sources: vec![source(&p, "flat.db", &txt, Some(1))],
            expected_etag: String::new(),
            confirm: false,
            stage: None,
            target_plc_id: Some(p.clone()),
            preview_token: None,
            raw_proofs: vec![],
            mappings: vec![crate::domain::source_import::BlockMapping {
                source_index: 0,
                block_key: crate::domain::source_import::BlockKey {
                    kind: "DATA_BLOCK".into(),
                    name: c.dbs[0].name.clone(),
                },
                selected: true,
                db_number: Some(1),
                target_id: Some(d.clone()),
            }],
        },
    )
    .unwrap();
    for pt in &old {
        let new = changed
            .configuration
            .points
            .iter()
            .find(|x| x.id == pt.id)
            .unwrap();
        assert!(!new.address.as_ref().unwrap().confirmed);
        assert_eq!(
            new.address.as_ref().unwrap().offset,
            pt.address.as_ref().unwrap().offset
        );
    }
    let nested = tia_source::import(
        &Configuration {
            plcs: c.plcs.clone(),
            ..Configuration::default()
        },
        vec![
            source(
                &p,
                "nested.db",
                include_str!("../../../tests/fixtures/local-acquisition/nested.db"),
                Some(2),
            ),
            source(
                &p,
                "nested.udt",
                include_str!("../../../tests/fixtures/local-acquisition/nested.udt"),
                None,
            ),
        ],
    )
    .unwrap();
    assert!(nested.issues.is_empty(), "{:?}", nested.issues);
    assert_eq!(nested.configuration.points.len(), 7);
    assert!(nested
        .configuration
        .points
        .iter()
        .all(|p| !p.enabled && p.address.is_none() && p.group_id.is_none()));
    assert_eq!(nested.configuration.dbs[0].tree[0].lower, Some(-1));
    assert!(plc_layout::preview(&nested.configuration, &nested.configuration.dbs[0].id).is_err());
    let invalid = tia_source::import(
        &c,
        vec![source(
            &p,
            "invalid.db",
            include_str!("../../../tests/fixtures/local-acquisition/invalid.db"),
            Some(3),
        )],
    )
    .unwrap();
    assert_eq!(invalid.issues[0].line, 5);
    assert_eq!(invalid.issues[0].file, "invalid.db");
}
#[test]
fn decode_and_hostile_addresses() {
    let mut c = configuration();
    let pt = c.points.iter().find(|p| p.data_type == "REAL").unwrap();
    let v = local_decode::decode(pt, &[63, 158, 6, 82])
        .unwrap()
        .as_f64()
        .unwrap();
    assert!((v - 1.2345678806304932).abs() < 1e-12);
    assert!(local_decode::decode(pt, &f32::NAN.to_be_bytes()).is_err());
    let mut p = pt.clone();
    p.data_type = "INT".into();
    assert_eq!(local_decode::decode(&p, &[255, 254]).unwrap(), -2);
    p.data_type = "STRING[3]".into();
    assert_eq!(
        local_decode::decode(&p, &[3, 3, 65, 10, 66]).unwrap(),
        "A\nB"
    );
    assert!(local_decode::decode(&p, &[3, 4, 65, 66, 67]).is_err());
    c.points[0].address.as_mut().unwrap().offset = u32::MAX;
    assert!(!validate(&c).is_empty());
    assert!(segments(&c, &c.groups[0]).is_err());
}
#[test]
fn draft_cas_atomic_round_raw_hash_and_restart() {
    let p = profile();
    let c = configuration();
    let r;
    let raw;
    let id;
    {
        let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
        let old = s.configuration().unwrap();
        r = activated(&mut s, &c);
        assert_eq!(s.save_draft(&c, &old.etag).unwrap_err(), "draft_conflict");
        let round = cycle(&c, &r);
        let out = s.commit_cycle(round.clone()).unwrap();
        assert_eq!(out["sourceSeq"], "1");
        assert_eq!(
            s.runtime
                .query_row("SELECT count(*) FROM samples", [], |r| r.get::<_, u32>(0))
                .unwrap(),
            2
        );
        assert_eq!(s.capacity(c.storage.quota_bytes).unwrap().pending_count, 2);
        let hist = s
            .history(HistoryQuery {
                limit: Some(1),
                ..Default::default()
            })
            .unwrap();
        id = hist["items"][0]["sampleId"].as_str().unwrap().to_string();
        raw = s.sample(&id).unwrap();
        assert_eq!(digest(raw["payload"].as_str().unwrap()), raw["sha256"]);
        let payload: SamplePayload =
            serde_json::from_str(raw["payload"].as_str().unwrap()).unwrap();
        assert_eq!(payload.points.len(), 12);
        assert_eq!(payload.source_seq, "1");
        let before = s.runtime.total_changes();
        let mut invalid = round;
        invalid.points.values_mut().next().unwrap().pop_first();
        assert_eq!(s.commit_cycle(invalid).unwrap_err(), "cycle_membership");
        assert_eq!(s.runtime.total_changes(), before);
        s.clean_exit().unwrap();
    }
    {
        let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
        assert_eq!(s.sample(&id).unwrap(), raw);
        assert_eq!(s.commit_cycle(cycle(&c, &r)).unwrap()["sourceSeq"], "2");
        for conn in [&s.config, &s.runtime] {
            assert_eq!(
                conn.query_row("PRAGMA synchronous", [], |r| r.get::<_, i64>(0))
                    .unwrap(),
                3
            );
            assert_eq!(
                conn.query_row("PRAGMA journal_mode", [], |r| r.get::<_, String>(0))
                    .unwrap(),
                "delete"
            );
        }
        s.clean_exit().unwrap();
    }
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn recovery_selected_token_and_identity_fail_closed() {
    let p = profile();
    let dir = p.join("local-acquisition-v1");
    let c = configuration();
    let r;
    {
        let mut s = Stores::open(&dir).unwrap();
        let v = s.configuration().unwrap();
        s.save_draft(&c, &v.etag).unwrap();
        let v = s.configuration().unwrap();
        let (t, rev) = s.prepare_activation(&v.etag, None, false).unwrap();
        r = rev;
        s.prepare_context(&t, &r).unwrap();
        s.select_active(&t, &r).unwrap();
    }
    {
        let mut s = Stores::open(&dir).unwrap();
        assert_eq!(s.configuration().unwrap().active, Some(r));
        let (t, _) = s.pending_activation().unwrap().unwrap();
        s.finish_activation(&t).unwrap();
        s.clean_exit().unwrap();
    }
    std::fs::write(dir.join("runtime.sqlite-wal"), []).unwrap();
    assert!(matches!(Stores::open(&dir),Err(e)if e=="unexpected_wal_material"));
    std::fs::remove_file(dir.join("runtime.sqlite-wal")).unwrap();
    std::fs::remove_file(dir.join("runtime.sqlite")).unwrap();
    assert!(matches!(Stores::open(&dir),Err(e)if e=="missing_database"));
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn pending_protection_ack_cursor_and_capacity() {
    let p = profile();
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let c = configuration();
    let r = activated(&mut s, &c);
    for _ in 0..10 {
        s.commit_cycle(cycle(&c, &r)).unwrap();
    }
    s.runtime
        .execute(
            "UPDATE collection_cycles SET saved_at='2000-01-01T00:00:00.000Z'",
            [],
        )
        .unwrap();
    let eligible: String = s
        .runtime
        .query_row(
            "SELECT id FROM collection_cycles ORDER BY rowid DESC LIMIT 1",
            [],
            |r| r.get(0),
        )
        .unwrap();
    let ids = s
        .runtime
        .prepare("SELECT id FROM samples WHERE cycle_id=?1")
        .unwrap()
        .query_map([eligible], |r| r.get::<_, String>(0))
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap();
    for id in &ids {
        s.runtime
            .execute(
                "UPDATE sample_delivery SET state='acknowledged' WHERE sample_id=?1",
                [id],
            )
            .unwrap();
    }
    let before = s.capacity(c.storage.quota_bytes).unwrap();
    assert_eq!(before.pending_count, 18);
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 0);
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 2);
    assert_eq!(s.capacity(c.storage.quota_bytes).unwrap().pending_count, 18);
    let mut low = before.clone();
    low.free_bytes = 0;
    assert!(!capacity::admit(&low, c.storage.quota_bytes, false));
    low = before;
    low.state = "unexpected_wal_material".into();
    assert!(!capacity::admit(&low, c.storage.quota_bytes, false));
    s.clean_exit().unwrap();
    drop(s);
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn read_deadline_includes_queue_and_connection_reusable() {
    let p = profile();
    let handle = StoreHandle::start(Stores::open(&p.join("local-acquisition-v1")).unwrap());
    let h = handle.clone();
    let writing = thread::spawn(move || {
        h.call(false, |s| {
            thread::sleep(Duration::from_millis(1100));
            s.event("test", "owned", "committed")
        })
    });
    thread::sleep(Duration::from_millis(30));
    let begin = Instant::now();
    let result = handle.call(true, |_| -> LocalResult<()> {
        panic!("expired queued query executed")
    });
    assert_eq!(result.unwrap_err(), "storage_timeout");
    assert!(begin.elapsed() < Duration::from_millis(1200));
    writing.join().unwrap().unwrap();
    let begin = Instant::now();
    let result=handle.call(true,|s|s.runtime.query_row("WITH RECURSIVE t(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM t WHERE x<1000000000) SELECT sum(x) FROM t",[],|r|r.get::<_,i64>(0)).map_err(sql_error));
    assert_eq!(result.unwrap_err(), "storage_timeout");
    assert!(begin.elapsed() < Duration::from_millis(1300));
    handle
        .call(false, |s| s.event("after_interrupt", "owned", "committed"))
        .unwrap();
    handle.shutdown();
    drop(handle);
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn actual_actor_save_activate_two_plcs_history_and_reopen() {
    let p = profile();
    std::fs::write(
        p.join("fixture.json"),
        include_str!("../../../tests/fixtures/local-acquisition/transport.json"),
    )
    .unwrap();
    let b = Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(p.join("fixture.json")),
    };
    let e = LocalEngine::open(b.clone()).unwrap();
    let c = configuration();
    let saved = seed_engine(&e, &c);
    let activated = e.activate(saved.etag, None, false).unwrap();
    let rev = activated["active"].as_str().unwrap();
    let ids = c.plcs.iter().map(|p| p.id.clone()).collect::<Vec<_>>();
    e.request(ids.clone(), "connection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(100));
    e.request(ids.clone(), "collection", true, rev, None)
        .unwrap();
    let start = Instant::now();
    while e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .len()
        < 8
    {
        assert!(start.elapsed() < Duration::from_secs(4));
        thread::sleep(Duration::from_millis(40));
    }
    e.request(ids.clone(), "collection", false, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(100));
    let states = e.states.lock().unwrap().clone();
    assert!(states
        .values()
        .all(|s| s.connected && !s.desired_collection && s.saved_cycles >= 2));
    assert!(e
        .operations
        .lock()
        .unwrap()
        .iter()
        .all(|o| o.phase == "applied"));
    let h = e.history(HistoryQuery::default()).unwrap();
    let sample = h["items"][0]["sampleId"].as_str().unwrap().to_string();
    let original = e.sample(sample.clone()).unwrap();
    let mut edit = e.configuration().unwrap();
    edit.draft.plcs[0].name = "Changed without replacing source ID".into();
    for group in &mut edit.draft.groups {
        group.enabled = false;
    }
    let edit = e.save(edit.draft, edit.etag).unwrap();
    let second = e.activate(edit.etag, Some(rev.to_string()), false).unwrap();
    let second = second["active"].as_str().unwrap().to_string();
    assert_ne!(second, rev);
    thread::sleep(Duration::from_millis(30));
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| s.connected && s.groups.is_empty()));
    assert_eq!(e.configuration().unwrap().used.as_deref(), Some(rev));
    assert_eq!(e.sample(sample.clone()).unwrap(), original);
    let edit = e.configuration().unwrap();
    let restored = e.activate(edit.etag, Some(second), true).unwrap();
    let restored = restored["active"].as_str().unwrap().to_string();
    assert_ne!(restored, rev);
    e.request(ids.clone(), "collection", true, &restored, None)
        .unwrap();
    let started = Instant::now();
    loop {
        let rows = e.history(HistoryQuery::default()).unwrap();
        if rows["items"][0]["revision"] == restored {
            assert!(
                rows["items"][0]["sourceSeq"]
                    .as_str()
                    .unwrap()
                    .parse::<u64>()
                    .unwrap()
                    >= 3
            );
            break;
        }
        assert!(started.elapsed() < Duration::from_secs(2));
        thread::sleep(Duration::from_millis(30));
    }
    e.request(ids, "collection", false, &restored, None)
        .unwrap();
    thread::sleep(Duration::from_millis(40));
    assert_eq!(e.sample(sample.clone()).unwrap(), original);

    e.shutdown();
    drop(e);
    let e = LocalEngine::open(b).unwrap();
    assert_eq!(e.sample(sample).unwrap(), original);
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| !s.connected && !s.desired_collection));
    e.shutdown();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
}

#[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
#[test]
fn owned_actor_disconnect_complete_bad_round_and_reconnect() {
    use rust_snap7::{AreaCode, InternalParam as P, InternalParamValue as V, S7Server};
    let reservation = std::net::TcpListener::bind(("127.0.0.1", 0)).unwrap();
    let port = reservation.local_addr().unwrap().port();
    let server = S7Server::create();
    let mut a = [1u8, 1, 42, 0, 255, 254, 63, 158, 6, 82];
    let mut b = a;
    server.register_area(AreaCode::S7AreaDB, 1, &mut a).unwrap();
    server.register_area(AreaCode::S7AreaDB, 2, &mut b).unwrap();
    server.set_param(P::LocalPort, V::U16(port)).unwrap();
    drop(reservation);
    server.start_to("127.0.0.1").unwrap();
    let p = profile();
    let mut c = configuration();
    let plc = c.plcs[0].id.clone();
    c.plcs.retain(|p| p.id == plc);
    c.plcs[0].port = port;
    c.dbs.retain(|p| p.plc_id == plc);
    c.points.retain(|p| p.plc_id == plc);
    c.groups.retain(|p| p.plc_id == plc);
    c.sources.retain(|p| p.plc_id == plc);
    let e = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let v = seed_engine(&e, &c);
    let out = e.activate(v.etag, None, false).unwrap();
    let rev = out["active"].as_str().unwrap();
    e.request(vec![plc.clone()], "connection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(100));
    e.request(vec![plc.clone()], "collection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(700));
    server.stop().unwrap();
    let begin = Instant::now();
    loop {
        if !e.states.lock().unwrap()[&plc].connected {
            break;
        }
        assert!(begin.elapsed() < Duration::from_secs(3));
        thread::sleep(Duration::from_millis(30));
    }
    let h = e
        .history(HistoryQuery {
            quality: Some("bad".into()),
            ..Default::default()
        })
        .unwrap();
    assert_eq!(
        h["items"].as_array().unwrap().len(),
        2,
        "failed network round remains a complete cross-DB unit"
    );
    server.start_to("127.0.0.1").unwrap();
    let begin = Instant::now();
    while !e.states.lock().unwrap()[&plc].connected {
        assert!(begin.elapsed() < Duration::from_secs(4));
        thread::sleep(Duration::from_millis(40));
    }
    e.request(vec![plc.clone()], "collection", false, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(100));
    assert!(e.states.lock().unwrap()[&plc].connected);
    e.shutdown();
    server.stop().unwrap();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
    println!("owned_actor complete_bad_packages=2 reconnect_resumed=true");
}

#[test]
fn normal_import_rejects_retired_yaml() {
    let mut c = Configuration::default();
    c.plcs.push(plc(31001));
    assert_eq!(
        tia_source::import(&c, vec![source(&c.plcs[0].id, "legacy.yaml", "{}", None)])
            .err()
            .unwrap(),
        "source_limits"
    );
}

#[test]
fn actor_capacity_stop_hysteresis_and_health_recovery() {
    use std::sync::atomic::{AtomicU64, Ordering};
    let p = profile();
    std::fs::write(
        p.join("fixture.json"),
        include_str!("../../../tests/fixtures/local-acquisition/transport.json"),
    )
    .unwrap();
    let e = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(p.join("fixture.json")),
    })
    .unwrap();
    let c = configuration();
    let v = seed_engine(&e, &c);
    let out = e.activate(v.etag, None, false).unwrap();
    let rev = out["active"].as_str().unwrap();
    let free = Arc::new(AtomicU64::new(0));
    let main = Arc::new(AtomicU64::new(100000));
    let (f, m) = (free.clone(), main.clone());
    e.storage
        .call(false, move |s| {
            s.test_meter = Some((f, m));
            Ok(())
        })
        .unwrap();
    let ids = c.plcs.iter().map(|p| p.id.clone()).collect::<Vec<_>>();
    e.request(ids.clone(), "connection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(80));
    e.request(ids.clone(), "collection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(600));
    assert!(e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| !s.desired_collection));
    assert!(e
        .operations
        .lock()
        .unwrap()
        .iter()
        .filter(|o| o.action == "collection")
        .all(|o| o.phase == "failed" && o.reason.as_deref() == Some("capacity_paused")));
    free.store(10 * 1024 * 1024 * 1024, Ordering::SeqCst);
    e.request(ids.clone(), "collection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(600));
    assert!(!e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    free.store(0, Ordering::SeqCst);
    thread::sleep(Duration::from_millis(600));
    let paused = e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .len();
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| s.admission == "capacity_paused" && s.desired_collection));
    free.store(10 * 1024 * 1024 * 1024, Ordering::SeqCst);
    main.store(750 * 1024 * 1024, Ordering::SeqCst);
    thread::sleep(Duration::from_millis(600));
    assert_eq!(
        e.history(HistoryQuery::default()).unwrap()["items"]
            .as_array()
            .unwrap()
            .len(),
        paused,
        "above70% must not auto resume"
    );
    main.store(100000, Ordering::SeqCst);
    let begin = Instant::now();
    while e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .len()
        <= paused
    {
        assert!(begin.elapsed() < Duration::from_secs(2));
        thread::sleep(Duration::from_millis(40));
    }
    e.shutdown();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn fair_groups_skip_ticks_and_full_timeout_quality() {
    let c = configuration();
    let mut schedules = local_scheduler::schedules(&c, &c.plcs[0].id);
    let second = crate::services::local_scheduler::Schedule {
        group: Group {
            id: id(),
            interval_ms: 1000,
            ..c.groups[0].clone()
        },
        due: schedules[0].due,
        missed: 0,
        last_duration: 0,
    };
    schedules.push(second);
    let at = schedules[0].due;
    assert_eq!(local_scheduler::due(&schedules, at), Some(0));
    local_scheduler::finish(&mut schedules[0], at, at + Duration::from_millis(1800));
    assert_eq!(schedules[0].missed, 3);
    assert_eq!(schedules[0].due, at + Duration::from_millis(2000));
    assert_eq!(
        local_scheduler::due(&schedules, at + Duration::from_millis(1800)),
        Some(1)
    );
    let mut f: FixtureSet = serde_json::from_str(include_str!(
        "../../../tests/fixtures/local-acquisition/transport.json"
    ))
    .unwrap();
    f.endpoints.get_mut(&c.plcs[0].endpoint()).unwrap().delay_ms = 5500;
    let mut t = crate::infrastructure::local_fixture::FixtureTransport::new(Arc::new(f));
    t.connect(&c.plcs[0]).unwrap();
    let begin = Instant::now();
    let round = local_scheduler::collect(
        &c,
        &c.plcs[0],
        &c.groups[0],
        "owned-revision",
        &mut t,
        "fixture",
    )
    .unwrap();
    assert!(begin.elapsed() < Duration::from_millis(5200));
    assert_eq!(round.points.len(), 2);
    assert_eq!(round.points.values().map(|ps| ps.len()).sum::<usize>(), 24);
    assert!(round
        .points
        .values()
        .flat_map(|ps| ps.values())
        .all(|p| p.value.is_null() && p.quality == "bad_timeout"));
    assert!(round.reads.iter().all(|r| r.quality == "bad_timeout"));
}
#[test]
fn real_sql_plans_match_full_scan_expected() {
    let p = profile();
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let c = configuration();
    let r = activated(&mut s, &c);
    for _ in 0..4 {
        s.commit_cycle(cycle(&c, &r)).unwrap();
    }
    let indexed = s
        .runtime
        .prepare("SELECT id FROM samples WHERE plc_id=?1 AND saved_at>=?2 ORDER BY saved_at,id")
        .unwrap()
        .query_map(rusqlite::params![c.plcs[0].id, "2000"], |r| {
            r.get::<_, String>(0)
        })
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap();
    let scan=s.runtime.prepare("SELECT id FROM samples NOT INDEXED WHERE plc_id=?1 AND saved_at>=?2 ORDER BY saved_at,id").unwrap().query_map(rusqlite::params![c.plcs[0].id,"2000"],|r|r.get::<_,String>(0)).unwrap().collect::<Result<Vec<_>,_>>().unwrap();
    assert_eq!(indexed, scan);
    assert_eq!(indexed.len(), 8);
    let plan=s.runtime.prepare("EXPLAIN QUERY PLAN SELECT id FROM samples WHERE plc_id=?1 AND saved_at>=?2 ORDER BY saved_at,id").unwrap().query_map(rusqlite::params![c.plcs[0].id,"2000"],|r|r.get::<_,String>(3)).unwrap().collect::<Result<Vec<_>,_>>().unwrap();
    assert!(plan.iter().any(|p| p.contains("history_plc")));
    let opcodes = s
        .runtime
        .prepare(
            "EXPLAIN SELECT id FROM samples WHERE plc_id=?1 AND saved_at>=?2 ORDER BY saved_at,id",
        )
        .unwrap()
        .query_map(rusqlite::params![c.plcs[0].id, "2000"], |r| {
            r.get::<_, String>(1)
        })
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap();
    assert!(!opcodes.iter().any(|p| p == "And"));
    println!("actual_sql_plan={plan:?} covering_fullscan_equal=8");
    s.clean_exit().unwrap();
    drop(s);
    std::fs::remove_dir_all(p).unwrap();
}

#[test]
fn full_context_is_original_bounded_chunks_and_log_rotation_is_owned() {
    let p = profile();
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let mut c = configuration();
    // An unused UDT source retains >64KiB verbatim text in the immutable runtime explanation.
    let mut text = String::from("TYPE \"Unused\"\nSTRUCT\n v : Int;\nEND_STRUCT;\nEND_TYPE\n");
    text.push_str(&format!("// {}\n", "x".repeat(90000)));
    let mut src = source(&c.plcs[0].id, "unused.udt", &text, None);
    src.id = id();
    src.sha256 = digest(&src.content);
    c.sources.push(src);
    let rev = activated(&mut s, &c);
    s.commit_cycle(cycle(&c, &rev)).unwrap();
    let sample = s.history(HistoryQuery::default()).unwrap()["items"][0]["sampleId"]
        .as_str()
        .unwrap()
        .to_string();
    let mut page = s.sample_chunk(&sample, 0).unwrap();
    let hash = page["contextSha256"].as_str().unwrap().to_string();
    let mut body = page["context"].as_str().unwrap().to_string();
    let mut count = 1;
    while let Some(next) = page["contextNextOffset"].as_u64() {
        page = s.sample_chunk(&sample, next as usize).unwrap();
        assert!(page["context"].as_str().unwrap().len() <= 65536);
        body.push_str(page["context"].as_str().unwrap());
        count += 1;
    }
    assert!(count >= 2);
    assert_eq!(digest(&body), hash);
    let original: String = s
        .runtime
        .query_row(
            "SELECT payload FROM configuration_contexts WHERE revision=?1",
            [rev],
            |r| r.get(0),
        )
        .unwrap();
    assert_eq!(body, original);
    s.clean_exit().unwrap();
    drop(s);
    let dir = p.join("rotation");
    std::fs::create_dir(&dir).unwrap();
    let line = "{\"event\":\"owned_rotation_seed\"}\n";
    let text = line.repeat((4 * 1024 * 1024 - 4096) / line.len() + 1);
    for name in [
        "runtime.jsonl",
        "runtime.1.jsonl",
        "runtime.2.jsonl",
        "runtime.3.jsonl",
        "runtime.4.jsonl",
        "runtime.5.jsonl",
        "runtime.6.jsonl",
        "runtime.7.jsonl",
    ] {
        std::fs::write(dir.join(name), &text).unwrap();
    }
    let log = crate::infrastructure::local_logging::LocalLog::new(dir.clone()).unwrap();
    log.event("owned_rotation", "fixture", "committed").unwrap();
    assert_eq!(std::fs::read_dir(&dir).unwrap().count(), 8);
    assert!(capacity::log_bytes(&dir) <= 32 * 1024 * 1024);
    for entry in std::fs::read_dir(&dir).unwrap() {
        let text = std::fs::read_to_string(entry.unwrap().path()).unwrap();
        assert!(text
            .lines()
            .all(|line| serde_json::from_str::<Value>(line).is_ok()));
    }
    drop(log);
    std::fs::remove_dir_all(p).unwrap();
}

#[test]
fn public_save_cannot_forge_source_proof_and_preview_ids_match_confirm() {
    let p = profile();
    std::fs::write(
        p.join("fixture.json"),
        include_str!("../../../tests/fixtures/local-acquisition/transport.json"),
    )
    .unwrap();
    let e = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(p.join("fixture.json")),
    })
    .unwrap();
    let mut base = Configuration::default();
    base.plcs.push(plc(31001));
    let plc = base.plcs[0].id.clone();
    let v = e.configuration().unwrap();
    let v = e.save(base, v.etag).unwrap();
    let sources=vec![source(&plc,"proof.db","DATA_BLOCK \"Proof\"\n{ S7_Optimized_Access := 'FALSE' }\nSTRUCT\n value : Int;\nEND_STRUCT;\nBEGIN\nEND_DATA_BLOCK",Some(1))];
    let preview = e.import(sources.clone(), v.etag.clone(), false).unwrap();
    let confirmed = e.import(sources, v.etag, true).unwrap();
    assert_eq!(
        encode(&preview.configuration).unwrap(),
        encode(&confirmed.configuration).unwrap()
    );
    let v = e.configuration().unwrap();
    let mut forged = v.draft.clone();
    forged.dbs[0].complete = false;
    forged.dbs[0].flat = false;
    assert_eq!(
        e.save(forged, v.etag.clone()).unwrap_err(),
        "source_derived_conflict"
    );
    let mut forged = v.draft.clone();
    forged.sources[0].sha256 = "forged".into();
    assert_eq!(
        e.save(forged, v.etag.clone()).unwrap_err(),
        "source_import_required"
    );
    let mut forged = v.draft.clone();
    forged.points[0].data_type = "REAL".into();
    assert_eq!(
        e.save(forged, v.etag.clone()).unwrap_err(),
        "source_derived_conflict"
    );
    let mut editable = v.draft.clone();
    let point = editable.points[0].id.clone();
    editable.points[0].name = "Editable name".into();
    editable.points[0].comment = "Editable comment".into();
    editable.points[0].address = Some(Address {
        offset: 0,
        bit: None,
        confirmed: true,
        origin: "manual".into(),
        reason: "review".into(),
    });
    editable.points[0].address.as_mut().unwrap().reason = "explicit manual review".into();
    let v = e.save(editable, v.etag).unwrap();
    assert_eq!(v.draft.points[0].id, point);
    assert_eq!(v.draft.points[0].name, "Editable name");
    assert!(v.draft.dbs[0].complete);
    let failure = crate::commands::local_acquisition::failure(&e, "draft_conflict".into());
    assert_eq!(failure.error_code, "draft_conflict");
    assert_eq!(failure.current_etag, Some(v.etag));
    assert_eq!(failure.current_active_revision, None);
    e.shutdown();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
}

#[test]
fn connection_test_restores_intent_and_point_diagnosis_keeps_ledger_empty() {
    let p = profile();
    std::fs::write(
        p.join("fixture.json"),
        include_str!("../../../tests/fixtures/local-acquisition/transport.json"),
    )
    .unwrap();
    let e = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(p.join("fixture.json")),
    })
    .unwrap();
    let c = configuration();
    let v = seed_engine(&e, &c);
    let point = v
        .draft
        .points
        .iter()
        .find(|p| p.plc_id == c.plcs[0].id && p.data_type == "REAL")
        .unwrap()
        .id
        .clone();
    let out = e.activate(v.etag, None, false).unwrap();
    let rev = out["active"].as_str().unwrap();
    let target = c.plcs[0].id.clone();
    e.request(vec![target.clone()], "test", false, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(80));
    assert!(!e.states.lock().unwrap()[&target].connected);
    assert!(!e.states.lock().unwrap()[&target].desired_connection);
    let op = e.operations.lock().unwrap().back().unwrap().clone();
    assert_eq!(op.phase, "applied");
    assert_eq!(op.result.as_ref().unwrap()["success"], true);
    assert_eq!(
        op.result.as_ref().unwrap()["originalDesiredConnection"],
        false
    );
    assert_eq!(op.result.as_ref().unwrap()["restorationPhase"], "applied");
    e.request(vec![target.clone()], "connection", true, rev, None)
        .unwrap();
    thread::sleep(Duration::from_millis(1100));
    e.request(vec![target.clone()], "diagnose", false, rev, Some(point))
        .unwrap();
    thread::sleep(Duration::from_millis(80));
    let op = e.operations.lock().unwrap().back().unwrap().clone();
    assert_eq!(op.phase, "applied");
    assert!(op.result.unwrap()["points"].is_object());
    assert!(e.states.lock().unwrap()[&target].connected);
    assert!(e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    let cap = e.capacity().unwrap();
    assert_eq!(cap.pending_count, 0);
    e.shutdown();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
}

#[test]
fn admission_limits_are_checked_at_exact_boundary() {
    let mut c = Configuration::default();
    c.plcs.push(plc(31001));
    let target = c.plcs[0].id.clone();
    let gid = id();
    c.groups.push(Group {
        id: gid.clone(),
        plc_id: target.clone(),
        name: "Boundary".into(),
        enabled: true,
        interval_ms: 500,
    });
    let fields = (0..257)
        .map(|n| format!(" p{n} : Int;\n"))
        .collect::<String>();
    let text=format!("DATA_BLOCK \"Boundary\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\n{fields}END_VAR\nBEGIN\nEND_DATA_BLOCK\n");
    c = tia_source::import(&c, vec![source(&target, "boundary.db", &text, Some(1))])
        .unwrap()
        .configuration;
    let db = c.dbs[0].id.clone();
    let changes = plc_layout::preview(&c, &db).unwrap();
    plc_layout::confirm(
        &mut c,
        &db,
        &changes
            .iter()
            .map(|x| x.point_id.clone())
            .collect::<Vec<_>>(),
    )
    .unwrap();
    for p in c.points.iter_mut().take(256) {
        p.enabled = true;
        p.group_id = Some(gid.clone())
    }
    assert!(validate(&c).is_empty(), "{:?}", validate(&c));
    c.points[256].enabled = true;
    c.points[256].group_id = Some(gid);
    assert!(validate(&c).iter().any(|i| i.code == "group_limits"));
    c.points[256].enabled = false;
    for port in 31002..=31005 {
        c.plcs.push(plc(port))
    }
    assert!(validate(&c)
        .iter()
        .any(|i| i.code == "configuration_limits"));
    c.plcs.pop();
    assert!(validate(&c).is_empty());
    c.groups[0].interval_ms = 499;
    assert!(validate(&c).iter().any(|i| i.code == "group_invalid"));
    c.groups[0].interval_ms = 500;
    for port in 0..7 {
        c.groups.push(Group {
            id: id(),
            plc_id: target.clone(),
            name: format!("Empty{port}"),
            enabled: false,
            interval_ms: 500,
        })
    }
    assert!(validate(&c).is_empty());
    c.groups.push(Group {
        id: id(),
        plc_id: target,
        name: "Ninth".into(),
        enabled: false,
        interval_ms: 500,
    });
    assert!(validate(&c).iter().any(|i| i.code == "plc_limits"));
}

#[test]
fn unknown_fixture_plc_can_activate_without_connecting_or_blocking_known_plcs() {
    let p = profile();
    std::fs::write(
        p.join("fixture.json"),
        include_str!("../../../tests/fixtures/local-acquisition/transport.json"),
    )
    .unwrap();
    let bootstrap = Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(p.join("fixture.json")),
    };
    let e = LocalEngine::open(bootstrap.clone()).unwrap();
    let mut config = configuration();
    let known: Vec<_> = config.plcs.iter().map(|p| p.id.clone()).collect();
    let unknown = plc(31999);
    let unknown_id = unknown.id.clone();
    config.plcs.push(unknown);
    let saved = seed_engine(&e, &config);
    let activated = e.activate(saved.etag, None, false).unwrap();
    let revision = activated["active"].as_str().unwrap().to_string();
    assert_eq!(e.states.lock().unwrap().len(), 3);
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| !s.connected && !s.desired_connection && !s.desired_collection));
    assert!(e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    e.shutdown();
    drop(e);
    let e = LocalEngine::open(bootstrap).unwrap();
    assert_eq!(
        e.configuration().unwrap().active.as_deref(),
        Some(revision.as_str())
    );
    assert_eq!(e.configuration().unwrap().draft.plcs.len(), 3);
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| !s.connected && !s.desired_connection && !s.desired_collection));
    let wait = |op: &str| {
        let begin = Instant::now();
        loop {
            let result = e
                .operations
                .lock()
                .unwrap()
                .iter()
                .find(|x| x.operation_id == op)
                .cloned()
                .unwrap();
            if result.phase != "pending" {
                break result;
            }
            assert!(begin.elapsed() < Duration::from_secs(3));
            thread::sleep(Duration::from_millis(10));
        }
    };
    let request = e
        .request(
            vec![unknown_id.clone()],
            "connection",
            true,
            &revision,
            None,
        )
        .unwrap();
    let connection = wait(request["items"][0]["operationId"].as_str().unwrap());
    assert_eq!(connection.phase, "failed");
    assert_eq!(
        connection.reason.as_deref(),
        Some("fixture_endpoint_missing")
    );
    let request = e
        .request(
            vec![unknown_id.clone()],
            "connection",
            false,
            &revision,
            None,
        )
        .unwrap();
    wait(request["items"][0]["operationId"].as_str().unwrap());
    let request = e
        .request(vec![unknown_id.clone()], "test", false, &revision, None)
        .unwrap();
    let test = wait(request["items"][0]["operationId"].as_str().unwrap());
    assert_eq!(test.result.as_ref().unwrap()["success"], false);
    assert_eq!(
        test.result.as_ref().unwrap()["reason"],
        "fixture_endpoint_missing"
    );
    assert!(!e.states.lock().unwrap()[&unknown_id].connected);
    assert!(e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    let request = e
        .request(known.clone(), "connection", true, &revision, None)
        .unwrap();
    for op in request["items"].as_array().unwrap() {
        assert_eq!(wait(op["operationId"].as_str().unwrap()).phase, "applied");
    }
    e.request(known.clone(), "collection", true, &revision, None)
        .unwrap();
    let begin = Instant::now();
    loop {
        let h = e.history(HistoryQuery::default()).unwrap();
        if h["items"].as_array().unwrap().len() >= 8 {
            break;
        }
        assert!(begin.elapsed() < Duration::from_secs(4));
        thread::sleep(Duration::from_millis(30));
    }
    e.request(known.clone(), "collection", false, &revision, None)
        .unwrap();
    thread::sleep(Duration::from_millis(100));
    let h = e.history(HistoryQuery::default()).unwrap();
    assert!(h["items"]
        .as_array()
        .unwrap()
        .iter()
        .all(|x| x["plcId"] != unknown_id));
    assert!(known
        .iter()
        .all(|id| e.states.lock().unwrap()[id].saved_cycles >= 2));
    let sample_id = h["items"][0]["sampleId"].as_str().unwrap().to_string();
    let raw = e.sample(sample_id).unwrap();
    assert_eq!(raw["deliveryState"], "pending");
    e.shutdown();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
}

// 私有维护反例种子和完整账本比较；不编入产品或local-validation命令。
fn maintenance_rows(s: &Stores) -> Value {
    let mut out = serde_json::Map::new();
    for table in [
        "plc_sources",
        "configuration_contexts",
        "activation_journal",
        "collection_cycles",
        "samples",
        "sample_delivery",
        "sample_references",
    ] {
        let mut stmt = s
            .runtime
            .prepare(&format!("SELECT * FROM {table} ORDER BY rowid"))
            .unwrap();
        let n = stmt.column_count();
        let rows = stmt
            .query_map([], |row| {
                Ok(Value::Array(
                    (0..n)
                        .map(|i| match row.get_ref(i).unwrap() {
                            rusqlite::types::ValueRef::Null => Value::Null,
                            rusqlite::types::ValueRef::Integer(v) => json!(v),
                            rusqlite::types::ValueRef::Real(v) => json!(v),
                            rusqlite::types::ValueRef::Text(v) => {
                                json!(std::str::from_utf8(v).unwrap())
                            }
                            rusqlite::types::ValueRef::Blob(v) => json!(v),
                        })
                        .collect(),
                ))
            })
            .unwrap()
            .collect::<Result<Vec<_>, _>>()
            .unwrap();
        out.insert(table.into(), Value::Array(rows));
    }
    Value::Object(out)
}
fn maintenance_seed(s: &mut Stores, c: &Configuration, r: &str, extra: usize) -> Vec<Vec<String>> {
    let mut ids = Vec::new();
    for _ in 0..5 + extra {
        let result = s.commit_cycle(cycle(c, r)).unwrap();
        let cycle_id = result["cycleId"].as_str().unwrap();
        ids.push(
            s.runtime
                .prepare("SELECT id FROM samples WHERE cycle_id=?1 ORDER BY db_number")
                .unwrap()
                .query_map([cycle_id], |row| row.get::<_, String>(0))
                .unwrap()
                .collect::<Result<Vec<_>, _>>()
                .unwrap(),
        );
    }
    s.runtime
        .execute(
            "UPDATE collection_cycles SET saved_at='2000-01-01T00:00:00.000Z'",
            [],
        )
        .unwrap();
    for cycle in &ids[1..] {
        for sample in cycle {
            s.runtime
                .execute(
                    "UPDATE sample_delivery SET state='acknowledged' WHERE sample_id=?1",
                    [sample],
                )
                .unwrap();
        }
    }
    for (sample, reference) in [
        (&ids[1][0], "hold-a"),
        (&ids[1][0], "shared"),
        (&ids[2][0], "shared"),
        (&ids[2][0], "hold-c"),
    ] {
        s.runtime
            .execute(
                "INSERT INTO sample_references VALUES(?1,?2)",
                rusqlite::params![sample, reference],
            )
            .unwrap();
    }
    s.runtime.execute("UPDATE collection_cycles SET expected_samples=expected_samples+1 WHERE id=(SELECT cycle_id FROM samples WHERE id=?1)", [&ids[3][0]]).unwrap();
    ids
}
fn protected_raw(s: &Stores, ids: &[Vec<String>]) -> Vec<Value> {
    ids[..4]
        .iter()
        .flatten()
        .map(|id| {
            let raw = s.sample(id).unwrap();
            assert_eq!(digest(raw["payload"].as_str().unwrap()), raw["sha256"]);
            assert_eq!(
                digest(raw["manifest"].as_str().unwrap()),
                raw["manifestSha256"]
            );
            assert_eq!(
                digest(raw["context"].as_str().unwrap()),
                raw["contextSha256"]
            );
            raw
        })
        .collect()
}
#[test]
fn acknowledged_overlapping_references_and_incomplete_cycles_are_protected() {
    let p = profile();
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let c = configuration();
    let revision = activated(&mut s, &c);
    let ids = maintenance_seed(&mut s, &c, &revision, 0);
    let raw = protected_raw(&s, &ids);
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 2);
    assert_eq!(protected_raw(&s, &ids), raw);
    assert_eq!(s.capacity(c.storage.quota_bytes).unwrap().pending_count, 2);
    for id in &ids[4] {
        assert!(s.sample(id).is_err());
    }
    s.runtime
        .execute(
            "DELETE FROM sample_references WHERE reference_id='hold-a'",
            [],
        )
        .unwrap();
    s.cleanup_cursor = 0;
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 0);
    assert_eq!(protected_raw(&s, &ids), raw); // shared still protects both cycles.
    s.runtime
        .execute(
            "DELETE FROM sample_references WHERE reference_id='shared'",
            [],
        )
        .unwrap();
    s.cleanup_cursor = 0;
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 2);
    for id in &ids[1] {
        assert!(s.sample(id).is_err());
    }
    for (id, original) in ids[2..4].iter().flatten().zip(raw[4..].iter()) {
        assert_eq!(&s.sample(id).unwrap(), original);
    }
    s.runtime
        .execute(
            "DELETE FROM sample_references WHERE reference_id='hold-c'",
            [],
        )
        .unwrap();
    s.cleanup_cursor = 0;
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 2);
    for id in &ids[2] {
        assert!(s.sample(id).is_err());
    }
    for (id, original) in ids[3].iter().zip(raw[6..].iter()) {
        assert_eq!(&s.sample(id).unwrap(), original);
    }
    s.runtime.execute("UPDATE collection_cycles SET expected_samples=expected_samples-1 WHERE id=(SELECT cycle_id FROM samples WHERE id=?1)", [&ids[3][0]]).unwrap();
    s.cleanup_cursor = 0;
    assert_eq!(s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap(), 2);
    for (id, original) in ids[0].iter().zip(raw[..2].iter()) {
        assert_eq!(&s.sample(id).unwrap(), original);
    }
    assert_eq!(s.capacity(c.storage.quota_bytes).unwrap().pending_count, 2);
    s.clean_exit().unwrap();
    drop(s);
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn periodic_maintenance_rechecks_current_space_before_cleanup_and_vacuum() {
    use std::sync::atomic::{AtomicU64, Ordering};
    for deny_after_cleanup in [false, true] {
        let p = profile();
        let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
        let c = configuration();
        let revision = activated(&mut s, &c);
        let ids = maintenance_seed(&mut s, &c, &revision, 0);
        let raw = protected_raw(&s, &ids);
        let before = maintenance_rows(&s);
        let cap = s.capacity(c.storage.quota_bytes).unwrap();
        let free = Arc::new(AtomicU64::new(if deny_after_cleanup {
            u64::MAX
        } else {
            0
        }));
        s.test_meter = Some((free.clone(), Arc::new(AtomicU64::new(cap.main_bytes))));
        s.test_after_cleanup_free = deny_after_cleanup.then_some(0);
        s.last_maintenance = Instant::now() - Duration::from_secs(61);
        let handle = StoreHandle::start(s);
        handle.call(false, |_| Ok(())).unwrap(); // Actual production job -> 60s maintenance branch.
        let (after, after_raw, page_count, freelist, clock_reset) = handle
            .call(false, move |s| {
                Ok((
                    maintenance_rows(s),
                    protected_raw(s, &ids),
                    s.capacity(c.storage.quota_bytes)?.page_count,
                    s.capacity(c.storage.quota_bytes)?.freelist_count,
                    s.last_maintenance.elapsed() < Duration::from_secs(5),
                ))
            })
            .unwrap();
        assert!(clock_reset);
        assert_eq!(after_raw, raw);
        if deny_after_cleanup {
            assert_ne!(after, before);
            assert_eq!(page_count, cap.page_count);
            assert!(freelist > cap.freelist_count);
        } else {
            assert_eq!(after, before);
        }
        assert_eq!(free.load(Ordering::SeqCst), 0);
        let records = maintenance_log_records(&p);
        assert_eq!(records.len(), 1);
        assert_eq!(records[0]["error_code"], "capacity_paused");
        assert_eq!(records[0]["result"], "deferred");
        println!(
            "{}",
            json!({"case":"worker_budget","afterCleanup":deny_after_cleanup,"productLogRecords":records})
        );
        free.store(u64::MAX, Ordering::SeqCst);
        handle
            .call(false, |s| s.event("post_maintenance", "test", "write_ok"))
            .unwrap();
        handle
            .call(true, |s| {
                Ok(s.runtime
                    .query_row("PRAGMA integrity_check", [], |r| r.get::<_, String>(0))
                    .unwrap())
            })
            .map(|v| assert_eq!(v, "ok"))
            .unwrap();
        handle.shutdown();
        std::fs::remove_dir_all(p).unwrap();
    }
}
#[test]
fn maintenance_busy_rolls_back_and_releases_worker_for_following_writes() {
    let p = profile();
    let dir = p.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let c = configuration();
    let r = activated(&mut s, &c);
    maintenance_seed(&mut s, &c, &r, 0);
    let before = maintenance_rows(&s);
    let reader = Connection::open(dir.join("runtime.sqlite")).unwrap();
    reader
        .execute_batch("BEGIN; SELECT count(*) FROM samples;")
        .unwrap();
    s.last_maintenance = Instant::now() - Duration::from_secs(61);
    let handle = StoreHandle::start(s);
    let at = Instant::now();
    handle.call(false, |_| Ok(())).unwrap();
    assert_eq!(
        handle.call(false, |s| Ok(maintenance_rows(s))).unwrap(),
        before
    );
    assert!(at.elapsed() >= Duration::from_millis(900));
    assert!(at.elapsed() < Duration::from_secs(3));
    let records = maintenance_log_records(&p);
    assert_eq!(records.len(), 1);
    assert_eq!(records[0]["error_code"], "storage_busy");
    assert_eq!(records[0]["result"], "failed");
    println!(
        "{}",
        json!({"case":"worker_busy","productLogRecords":records})
    );
    reader.execute_batch("ROLLBACK").unwrap();
    drop(reader);
    handle
        .call(false, |s| s.event("post_busy", "test", "write_ok"))
        .unwrap();
    handle
        .call(true, |s| Ok(s.capacity(1024 * 1024 * 1024)?.pending_count))
        .map(|v| assert_eq!(v, 2))
        .unwrap();
    handle.shutdown();
    std::fs::remove_dir_all(p).unwrap();
}
// Executed only in the exact ignored unit-test child below, never in product/validation builds.
pub(super) fn maintenance_before_commit(connection: &Connection, stage: &str) {
    if std::env::var("DAA002_MAINT_CHILD_MODE").as_deref() != Ok("kill")
        || std::env::var("DAA002_MAINT_CHILD_STAGE").as_deref() != Ok(stage)
    {
        return;
    }
    let profile = maintenance_child_profile();
    connection.cache_flush().unwrap();
    let journal = profile.join("local-acquisition-v1/runtime.sqlite-journal");
    let bytes = std::fs::read(&journal).unwrap();
    assert_eq!(
        &bytes[..8],
        &[0xd9, 0xd5, 0x05, 0xf9, 0x20, 0xa1, 0x63, 0xd7]
    );
    std::fs::write(
        profile.join("maintenance-ready.json"),
        json!({"stage":stage,"journalBytes":bytes.len(),"magic":"d9d505f920a163d7","header64Hex":bytes.iter().take(64).map(|b|format!("{b:02x}")).collect::<String>()}).to_string(),
    )
    .unwrap();
    thread::sleep(Duration::from_secs(10));
    panic!("controller failed to SIGKILL owned maintenance child");
}
fn maintenance_child_profile() -> PathBuf {
    let p = PathBuf::from(std::env::var_os("DAA002_MAINT_CHILD_PROFILE").unwrap());
    assert!(p.is_absolute() && !p.is_symlink() && p.canonicalize().unwrap() == p);
    assert_eq!(
        p.parent().unwrap(),
        std::env::temp_dir().canonicalize().unwrap()
    );
    assert!(p
        .file_name()
        .unwrap()
        .to_str()
        .unwrap()
        .starts_with("daa-002-r2-test-"));
    assert_eq!(
        std::fs::read_to_string(p.join(".daa-local-validation-owner")).unwrap(),
        "DAA-002-r2-owned\n"
    );
    p
}
#[test]
#[ignore = "private marked tmp child, launched only by the maintenance parent tests"]
fn maintenance_fault_child() {
    let p = maintenance_child_profile();
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let c = s
        .revision(s.configuration().unwrap().active.as_deref().unwrap())
        .unwrap();
    let stage = std::env::var("DAA002_MAINT_CHILD_STAGE").unwrap();
    let mode = std::env::var("DAA002_MAINT_CHILD_MODE").unwrap();
    let before = maintenance_rows(&s);
    if mode == "worker-write-failure" {
        let mut old: libc::rlimit = unsafe { std::mem::zeroed() };
        s.last_maintenance = Instant::now() - Duration::from_secs(61);
        unsafe {
            assert_eq!(libc::getrlimit(libc::RLIMIT_FSIZE, &mut old), 0);
            libc::signal(libc::SIGXFSZ, libc::SIG_IGN);
            // A fresh SQLite journal exceeds 4KiB; the one-line product log does not.
            assert_eq!(
                libc::setrlimit(
                    libc::RLIMIT_FSIZE,
                    &libc::rlimit {
                        rlim_cur: 4096,
                        rlim_max: old.rlim_max
                    }
                ),
                0
            );
        }
        let handle = StoreHandle::start(s);
        handle.call(false, |_| Ok(())).unwrap();
        let after = handle.call(true, |s| Ok(maintenance_rows(s))).unwrap();
        unsafe {
            assert_eq!(libc::setrlimit(libc::RLIMIT_FSIZE, &old), 0);
        }
        assert_eq!(after, before);
        let records = maintenance_log_records(&p);
        assert_eq!(records.len(), 1);
        assert_eq!(records[0]["error_code"], "storage_error");
        assert_eq!(records[0]["result"], "failed");
        handle
            .call(false, |s| s.event("post_worker_ioerr", "test", "write_ok"))
            .unwrap();
        handle
            .call(true, |s| Ok(s.capacity(1024 * 1024 * 1024)?.pending_count))
            .map(|v| assert_eq!(v, 2))
            .unwrap();
        handle.shutdown();
        println!(
            "{}",
            json!({"case":"worker_ioerr","profile":p,"productLogRecords":records,"originalLedgerUnchanged":true,"followingReadWrite":"ok"})
        );
        return;
    }
    let mut old: libc::rlimit = unsafe { std::mem::zeroed() };
    if mode == "write-failure" {
        unsafe {
            assert_eq!(libc::getrlimit(libc::RLIMIT_FSIZE, &mut old), 0);
            libc::signal(libc::SIGXFSZ, libc::SIG_IGN);
            let limit = libc::rlimit {
                rlim_cur: 0,
                rlim_max: old.rlim_max,
            };
            assert_eq!(libc::setrlimit(libc::RLIMIT_FSIZE, &limit), 0);
        }
    }
    let result = if stage == "cleanup" {
        s.cleanup_acknowledged(7, c.storage.quota_bytes).map(|_| ())
    } else {
        s.reclaim_incremental(c.storage.quota_bytes)
    };
    if mode == "write-failure" {
        unsafe {
            assert_eq!(libc::setrlimit(libc::RLIMIT_FSIZE, &old), 0);
        }
        let error = result.unwrap_err();
        assert!(error.contains("storage_error"), "{error}");
        assert_eq!(maintenance_rows(&s), before);
        s.event("post_io_failure", "test", "write_ok").unwrap();
        println!(
            "{}",
            json!({"stage":stage,"mode":mode,"error":error,"originalLedgerUnchanged":true,"followingWrite":"ok"})
        );
        s.clean_exit().unwrap();
    } else {
        panic!("kill hook was not reached: {result:?}");
    }
}
#[test]
fn maintenance_faults_recover_original_protected_ledger() {
    use std::os::unix::process::ExitStatusExt;
    for stage in ["cleanup", "vacuum"] {
        for mode in ["write-failure", "kill"] {
            let p = profile();
            let dir = p.join("local-acquisition-v1");
            let mut s = Stores::open(&dir).unwrap();
            let c = configuration();
            let r = activated(&mut s, &c);
            let ids = maintenance_seed(&mut s, &c, &r, if stage == "vacuum" { 80 } else { 0 });
            if stage == "vacuum" {
                for _ in 0..16 {
                    s.cleanup_acknowledged(7, c.storage.quota_bytes).unwrap();
                }
                assert!(s.capacity(c.storage.quota_bytes).unwrap().freelist_count > 64);
            }
            let before = maintenance_rows(&s);
            let raw = protected_raw(&s, &ids);
            let cap = s.capacity(c.storage.quota_bytes).unwrap();
            s.clean_exit().unwrap();
            drop(s);
            let mut child = std::process::Command::new(std::env::current_exe().unwrap())
                .args([
                    "--exact",
                    "infrastructure::local_store::tests::maintenance_fault_child",
                    "--ignored",
                    "--nocapture",
                ])
                .env("DAA002_MAINT_CHILD_PROFILE", &p)
                .env("DAA002_MAINT_CHILD_STAGE", stage)
                .env("DAA002_MAINT_CHILD_MODE", mode)
                .stdout(std::process::Stdio::piped())
                .stderr(std::process::Stdio::piped())
                .spawn()
                .unwrap();
            let mut peak = 0;
            if mode == "kill" {
                let at = Instant::now();
                while !p.join("maintenance-ready.json").exists() {
                    if let Some(status) = child.try_wait().unwrap() {
                        let out = child.wait_with_output().unwrap();
                        panic!(
                            "child exited before marker {stage} {status}: {} {}",
                            String::from_utf8_lossy(&out.stdout),
                            String::from_utf8_lossy(&out.stderr)
                        );
                    }
                    if at.elapsed() > Duration::from_secs(5) {
                        child.kill().unwrap();
                        let _ = child.wait();
                        panic!("owned child marker timeout");
                    }
                    thread::sleep(Duration::from_millis(10));
                }
                let marker: Value = serde_json::from_slice(
                    &std::fs::read(p.join("maintenance-ready.json")).unwrap(),
                )
                .unwrap();
                peak = marker["journalBytes"].as_u64().unwrap();
                assert!(peak > 0 && peak < cap.reserved_bytes - 64 * 1024 * 1024);
                child.kill().unwrap();
            }
            let output = child.wait_with_output().unwrap();
            if mode == "kill" {
                assert_eq!(output.status.signal(), Some(libc::SIGKILL));
            } else {
                assert!(
                    output.status.success(),
                    "{} {}",
                    String::from_utf8_lossy(&output.stdout),
                    String::from_utf8_lossy(&output.stderr)
                );
            }
            let mut recovered = Stores::open(&dir).unwrap();
            assert_eq!(maintenance_rows(&recovered), before);
            assert_eq!(protected_raw(&recovered, &ids), raw);
            assert_eq!(
                recovered
                    .runtime
                    .query_row("PRAGMA integrity_check", [], |r| r.get::<_, String>(0))
                    .unwrap(),
                "ok"
            );
            let restored = maintenance_rows(&recovered);
            recovered.event("post_reopen", "test", "write_ok").unwrap();
            if stage == "cleanup" {
                recovered.cleanup_cursor = 0;
                assert_eq!(
                    recovered
                        .cleanup_acknowledged(7, c.storage.quota_bytes)
                        .unwrap(),
                    2
                );
            } else {
                recovered
                    .reclaim_incremental(c.storage.quota_bytes)
                    .unwrap();
                assert!(
                    recovered
                        .capacity(c.storage.quota_bytes)
                        .unwrap()
                        .page_count
                        < cap.page_count
                );
            }
            assert_eq!(protected_raw(&recovered, &ids), raw);
            println!(
                "{}",
                json!({"stage":stage,"mode":mode,"profile":p,"journalPeak":peak,"journalOldPageBound":cap.reserved_bytes-64*1024*1024,"journalBoundReserve":cap.reserved_bytes,"killSignal":output.status.signal(),"ledgerSHA256Before":digest(&before.to_string()),"ledgerSHA256Restored":digest(&restored.to_string()),"allProtectedOriginalBytesRetained":true,"followingReadWriteAndMaintenance":"ok","childStdout":String::from_utf8_lossy(&output.stdout)})
            );
            std::fs::write(p.join("maintenance-evidence.json"), json!({"stage":stage,"mode":mode,"ledgerBefore":before,"ledgerAfterRecovery":restored,"protectedOriginalRaw":raw,"protectedAfterMaintenance":protected_raw(&recovered,&ids),"pageCountBefore":cap.page_count,"pageCountAfter":recovered.capacity(c.storage.quota_bytes).unwrap().page_count,"journalPeak":peak,"journalOldPageBound":cap.reserved_bytes-64*1024*1024,"signal":output.status.signal(),"childStdout":String::from_utf8_lossy(&output.stdout)}).to_string()).unwrap();
            recovered.clean_exit().unwrap();
            drop(recovered); // Marked temporary evidence profile is closed and retained for the controller.
        }
    }
}

// Read the actual bounded product file, not a wrapper's captured stdout.
fn maintenance_log_records(profile: &std::path::Path) -> Vec<Value> {
    let text =
        std::fs::read_to_string(profile.join("local-acquisition-v1/logs/runtime.jsonl")).unwrap();
    text.lines()
        .map(|line| serde_json::from_str::<Value>(line).unwrap())
        .filter(|line| line["event"] == "maintenance_failed")
        .map(|line| {
            assert_eq!(line["process"], "daa-local");
            assert_eq!(line["resource"], "storage_maintenance");
            assert!(line["at"].is_string());
            line
        })
        .collect()
}
#[test]
fn periodic_maintenance_ioerr_reaches_product_log_and_stdout() {
    let p = profile();
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let c = configuration();
    let r = activated(&mut s, &c);
    let ids = maintenance_seed(&mut s, &c, &r, 0);
    let before = maintenance_rows(&s);
    let raw = protected_raw(&s, &ids);
    s.clean_exit().unwrap();
    drop(s);
    let output = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "infrastructure::local_store::tests::maintenance_fault_child",
            "--ignored",
            "--nocapture",
        ])
        .env("DAA002_MAINT_CHILD_PROFILE", &p)
        .env("DAA002_MAINT_CHILD_STAGE", "cleanup")
        .env("DAA002_MAINT_CHILD_MODE", "worker-write-failure")
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{} {}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    let stdout = String::from_utf8(output.stdout).unwrap();
    let record = stdout
        .lines()
        .filter_map(|line| serde_json::from_str::<Value>(line).ok())
        .find(|line| line["fields"]["event"] == "maintenance_failed")
        .unwrap();
    assert_eq!(record["fields"]["error_code"], "storage_error");
    assert_eq!(record["fields"]["persistence"], "persisted");
    let mut recovered = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    assert_eq!(maintenance_rows(&recovered), before);
    assert_eq!(protected_raw(&recovered, &ids), raw);
    assert_eq!(
        recovered
            .capacity(c.storage.quota_bytes)
            .unwrap()
            .pending_count,
        2
    );
    recovered.clean_exit().unwrap();
    drop(recovered);
    std::fs::write(p.join("worker-ioerr-stdout.jsonl"), &stdout).unwrap();
    println!(
        "{}",
        json!({"case":"worker_ioerr_parent","profile":p,"stdoutRecord":record,"productLogRecords":maintenance_log_records(&p),"originalLedgerAndPayloadHashesUnchanged":true,"childExited":true})
    );
}
#[test]
fn periodic_maintenance_log_failure_keeps_history_stop_and_shutdown_available() {
    let p = profile();
    std::fs::write(
        p.join("fixture.json"),
        include_str!("../../../tests/fixtures/local-acquisition/transport.json"),
    )
    .unwrap();
    let e = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(p.join("fixture.json")),
    })
    .unwrap();
    let view = seed_engine(&e, &configuration());
    e.activate(view.etag, view.active, false).unwrap();
    let revision = e.loaded.lock().unwrap().as_ref().unwrap().revision.clone();
    let c = e
        .loaded
        .lock()
        .unwrap()
        .as_ref()
        .unwrap()
        .configuration
        .clone();
    let copy = c.clone();
    e.storage
        .call(false, move |s| {
            let ids = maintenance_seed(s, &copy, &revision, 0);
            Ok(ids)
        })
        .unwrap();
    let before = e.storage.call(true, |s| Ok(maintenance_rows(s))).unwrap();
    let log = e.log.clone();
    assert!(e
        .storage
        .call(true, move |s| Ok(Arc::ptr_eq(&s.log, &log)))
        .unwrap());
    let path = p.join("local-acquisition-v1/logs/runtime.jsonl");
    std::fs::rename(&path, p.join("before-unwritable-runtime.jsonl")).unwrap();
    std::fs::create_dir(&path).unwrap(); // Owned path conflict; no host disk-fill/permission change.
    e.storage
        .call(false, |s| {
            s.test_meter = Some((
                Arc::new(std::sync::atomic::AtomicU64::new(0)),
                Arc::new(std::sync::atomic::AtomicU64::new(0)),
            ));
            s.last_maintenance = Instant::now() - Duration::from_secs(61);
            Ok(())
        })
        .unwrap();
    let after = e.storage.call(true, |s| Ok(maintenance_rows(s))).unwrap(); // Barrier after actual worker branch.
    assert_eq!(before, after);
    assert_eq!(e.log.health().unwrap_err(), "log_io_unknown_interval");
    assert_eq!(
        e.storage.call(false, |_| Ok(())).unwrap_err(),
        "log_io_unknown_interval"
    );
    let history = e.history(Default::default()).unwrap();
    assert_eq!(history["items"].as_array().unwrap().len(), 10);
    assert_eq!(e.logs(0, 20).unwrap_err(), "log_io_unknown_interval");
    // Reads must not resume maintenance writes after a log fault, even when space recovers.
    e.storage
        .call(true, |s| {
            s.test_meter
                .as_ref()
                .unwrap()
                .0
                .store(u64::MAX, std::sync::atomic::Ordering::SeqCst);
            s.last_maintenance = Instant::now() - Duration::from_secs(61);
            Ok(())
        })
        .unwrap();
    assert_eq!(
        e.storage.call(true, |s| Ok(maintenance_rows(s))).unwrap(),
        before
    );
    let snapshot = e.snapshot().unwrap();
    assert!(snapshot["plcs"]
        .as_array()
        .unwrap()
        .iter()
        .all(|s| s["admission"] == "storage_fault" && s["error"] == "log_io_unknown_interval"));
    let revision = e.loaded.lock().unwrap().as_ref().unwrap().revision.clone();
    let ids = c.plcs.iter().map(|p| p.id.clone()).collect::<Vec<_>>();
    assert_eq!(
        e.request(ids.clone(), "collection", true, &revision, None)
            .unwrap_err(),
        "log_io_unknown_interval"
    );
    let stop = e
        .request(ids, "collection", false, &revision, None)
        .unwrap();
    let at = Instant::now();
    loop {
        let operations = e.operations.lock().unwrap();
        if stop["items"].as_array().unwrap().iter().all(|s| {
            operations.iter().any(|o| {
                o.operation_id == s["operationId"].as_str().unwrap() && o.phase == "applied"
            })
        }) {
            break;
        }
        assert!(at.elapsed() < Duration::from_secs(3));
        drop(operations);
        thread::sleep(Duration::from_millis(10));
    }
    assert_eq!(
        e.storage.call(true, |s| Ok(maintenance_rows(s))).unwrap(),
        before
    );
    e.shutdown(); // No writer callback/self-wait even when its log cannot be persisted.
    std::fs::remove_dir(&path).unwrap();
    let mut reopened = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    assert_eq!(maintenance_rows(&reopened), before);
    assert_eq!(
        reopened
            .capacity(c.storage.quota_bytes)
            .unwrap()
            .pending_count,
        2
    );
    reopened.clean_exit().unwrap();
    drop(reopened);
    println!(
        "{}",
        json!({"case":"worker_log_unavailable","profile":p,"errorCode":"log_io_unknown_interval","persistentSuccessNotClaimed":true,"historyReadable":true,"manualStopApplied":true,"normalShutdownReturned":true,"originalLedgerUnchanged":true,"reopenReadable":true})
    );
}

#[path = "time_contract_tests.rs"]
mod time_contract_tests;

#[test]
fn resident_retirement_active_configuration_reopens_stopped_with_native_admission() {
    let p = std::env::temp_dir().join(format!("resident-active-{}", id()));
    std::fs::create_dir(&p).unwrap();
    let b = Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    };
    let mut stores = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let active = activated(&mut stores, &configuration());
    drop(stores);
    let e = LocalEngine::open(b.clone()).unwrap();
    assert!(!e.states.lock().unwrap().is_empty());
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| !s.connected && !s.desired_connection && !s.desired_collection));
    e.shutdown();
    drop(e);
    let e = LocalEngine::open(b).unwrap();
    assert!(e.bootstrap.read_allowed && !e.bootstrap.validation && e.fixture.is_none());
    assert_eq!(
        e.configuration().unwrap().active.as_deref(),
        Some(active.as_str())
    );
    assert!(e
        .states
        .lock()
        .unwrap()
        .values()
        .all(|s| !s.connected && !s.desired_connection && !s.desired_collection));
    assert!(e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    e.shutdown();
    drop(e);
    std::fs::remove_dir_all(p).unwrap();
}
