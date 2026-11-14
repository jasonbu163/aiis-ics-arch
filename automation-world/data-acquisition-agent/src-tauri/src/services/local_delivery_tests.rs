//! 纯回执/调度规则与传输替身验证；禁止网络listener。
use crate::domain::local_delivery::*;
#[test]
fn retry_bounds() {
    assert_eq!(retry_delay(1, None, 0), 1);
    assert_eq!(retry_delay(6, None, 20), 36);
    assert_eq!(retry_delay(100, Some("900"), 0), 300);
    assert_eq!(retry_delay(3, Some("0"), 0), 1);
}
use crate::{
    domain::{
        facts_canonical as pf,
        local_delivery::{classify, verify_success, Reply},
    },
    infrastructure::{
        facts_http::{Response, Transport},
        local_store::{
            delivery_tests::{adopt, fresh, receipt, seed},
            StoreHandle,
        },
    },
};
use serde_json::{json, Value};
struct Substitute {
    reply: Response,
    calls: std::sync::atomic::AtomicUsize,
}
impl Transport for Substitute {
    fn post(&self, _: &str, body: &str) -> Result<Response, String> {
        self.calls.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        assert!(pf::parse(body.as_bytes(), 4 * 1024 * 1024).is_ok());
        Ok(self.reply.clone())
    }
}
#[test]
fn strict_ack_matrix_and_transport_substitute() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let frozen = s.next_delivery().unwrap().unwrap();
    let good = receipt(&frozen);
    assert!(verify_success(&frozen.batch, &good).is_ok());
    for pointer in [
        "/code",
        "/message",
        "/data/contractVersion",
        "/data/digestProfile",
        "/data/instanceId",
        "/data/batchId",
        "/data/requestDigest",
        "/data/persistence",
        "/data/confirmation",
        "/data/receiptId",
        "/data/committedAt",
        "/data/proofExpiresAt",
        "/data/results/0/sourceSha256",
        "/data/results/0/contentDigest",
        "/data/results/0/part",
        "/data/results/0/parts",
        "/data/results/0/position/commitSerial",
        "/data/results/0/position/ordinal",
        "/data/cycles/0/cycleDigest",
        "/data/cycles/0/expectedParts",
    ] {
        let mut bad = good.clone();
        *bad.pointer_mut(pointer).unwrap() = json!("broken");
        assert!(verify_success(&frozen.batch, &bad).is_err(), "{pointer}");
    }
    for pointer in ["/data/results", "/data/cycles"] {
        let mut bad = good.clone();
        bad.pointer_mut(pointer)
            .unwrap()
            .as_array_mut()
            .unwrap()
            .clear();
        assert!(verify_success(&frozen.batch, &bad).is_err());
    }
    let mut extra = good.clone();
    let duplicate = extra["data"]["results"][0].clone();
    extra["data"]["results"]
        .as_array_mut()
        .unwrap()
        .push(duplicate);
    assert!(verify_success(&frozen.batch, &extra).is_err());
    let mut historical = good.clone();
    historical["data"]["newFactsCommitted"] = json!(false);
    historical["data"]["outcome"] = json!("duplicate");
    historical["data"]["commitSerial"] = Value::Null;
    historical["data"]["results"][0]["outcome"] = json!("duplicate");
    historical["data"]["results"][0]["confirmation"] = json!("historical_committed");
    historical["data"]["results"][0]["valueReadable"] = json!(false);
    assert!(verify_success(&frozen.batch, &historical).is_ok());
    let response = Response {
        status: 200,
        media_type: "application/json".into(),
        retry_after: None,
        body: serde_json::to_vec_pretty(&good).unwrap(),
    };
    let substitute = Substitute {
        reply: response,
        calls: Default::default(),
    };
    let attempt = s.mark_dispatch(&frozen).unwrap();
    let storage = StoreHandle::start(s);
    let reply = substitute.post(&frozen.origin, &frozen.body);
    assert!(
        !super::apply_response(&storage, &frozen, reply, attempt)
            .unwrap()
            .pause
    );
    assert_eq!(
        substitute.calls.load(std::sync::atomic::Ordering::SeqCst),
        1
    );
    assert_eq!(
        storage.call(true, |s| s.delivery_snapshot(false)).unwrap()["acknowledged"],
        1
    );
    storage.shutdown();
}
#[test]
fn response_error_matrix_never_forges_ack() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let f = s.next_delivery().unwrap().unwrap();
    for (status, error, persistence, expected) in [
        (429, "busy", "none", "retry_wait"),
        (503, "not_ready", "none", "retry_wait"),
        (500, "internal_error", "unknown", "unknown"),
        (403, "scope_rejected", "none", "needs_review"),
        (409, "batch_content_conflict", "none", "blocked"),
        (410, "sample_expired", "none", "expired_unconfirmed"),
        (410, "proof_expired", "none", "needs_review"),
        (413, "payload_too_large", "none", "blocked"),
        (415, "media_type", "none", "blocked"),
        (422, "invalid_request", "none", "blocked"),
    ] {
        let body=serde_json::to_vec(&json!({"code":status,"message":"failure","errorCode":format!("plc_facts.{error}"),"data":{"persistence":persistence,"newFactsCommitted":if persistence=="unknown"{Value::Null}else{json!(false)},"retryable":true,"retirementAllowed":false}})).unwrap();
        assert!(
            matches!(classify(&f.batch,status,"application/json",&body,None,1,0),Reply::Failure{state,..}if state==expected),
            "{status} {error}"
        );
    }
    for body in [b"{}".as_slice(), b"{\"code\":200".as_slice()] {
        assert!(
            matches!(classify(&f.batch,200,"application/json",body,None,1,0),Reply::Failure{state,..}if state=="unknown")
        );
    }
    assert!(
        matches!(classify(&f.batch,200,"text/html",b"{}",None,1,0),Reply::Failure{state,..}if state=="unknown")
    );
}
#[test]
fn invalid_utf8_is_persisted_unknown_without_ack() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let f = s.next_delivery().unwrap().unwrap();
    let attempt = s.mark_dispatch(&f).unwrap();
    let storage = StoreHandle::start(s);
    let result = super::apply_response(
        &storage,
        &f,
        Ok(Response {
            status: 200,
            media_type: "application/json".into(),
            retry_after: None,
            body: vec![0xff, 0xfe],
        }),
        attempt,
    )
    .unwrap();
    assert!(!result.pause);
    assert_eq!(
        storage.call(true, |s| s.delivery_snapshot(false)).unwrap()["counts"]["unknown"],
        1
    );
    assert_eq!(
        storage.call(true, |s| s.delivery_snapshot(false)).unwrap()["acknowledged"],
        0
    );
    storage.shutdown();
}
#[test]
fn maximum_identifier_ack_bound_is_not_truncated() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let mut f = s.next_delivery().unwrap().unwrap();
    let prototype = f.batch.samples[0].clone();
    let mut samples = vec![];
    let mut transport = vec![];
    for part in 0..32u32 {
        let mut p = prototype.clone();
        p.sample_id = format!("sample-{part}");
        p.part = 1;
        p.parts = 1;
        p.point_ids = (0..512u32)
            .map(|point| {
                let index = part * 512 + point;
                (0..128u32)
                    .map(|bit| {
                        if bit < 14 && index & (1 << bit) != 0 {
                            '\\'
                        } else {
                            '"'
                        }
                    })
                    .collect::<String>()
            })
            .collect();
        assert!(p.point_ids.iter().all(|s| s.len() == 128));
        transport.push(crate::domain::facts_wire::TransportSample {
            sample_id: p.sample_id.clone(),
            db_number: part as u16 + 1,
            source_sha256: p.source_sha256.clone(),
            parts: vec![crate::domain::facts_wire::TransportPart {
                part: 1,
                point_ids: p.point_ids.clone(),
                content_digest: p.content_digest.clone(),
            }],
        });
        samples.push(p);
    }
    f.batch.samples = samples;
    f.batch.cycles[0].transport_manifest = transport;
    let ack = receipt(&f);
    let raw = serde_json::to_vec(&ack).unwrap();
    assert!(raw.len() > 4 * 1024 * 1024 && raw.len() < 8 * 1024 * 1024);
    assert!(matches!(
        classify(&f.batch, 200, "application/json", &raw, None, 1, 0),
        Reply::Committed(_)
    ));
    let mut truncated = raw.clone();
    truncated.pop();
    assert!(
        matches!(classify(&f.batch,200,"application/json",&truncated,None,1,0),Reply::Failure{state,..}if state=="unknown")
    );
}
#[test]
fn typed_terminal_rejection_only_then_original_subset_child() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let now = crate::domain::business_time::now();
    let expiry = (crate::domain::facts_wire::time(&now).unwrap() + chrono::Duration::days(120))
        .to_rfc3339_opts(chrono::SecondsFormat::Nanos, true);
    let rejected = json!({"code":403,"message":"source_rejected","errorCode":"plc_facts.source_rejected","data":{"contractVersion":"plc-facts/v1","instanceId":f.batch.instance_id,"batchId":f.batch.batch_id,"requestDigest":f.batch.request_digest,"receiptId":crate::domain::local_configuration::id(),"recordedAt":now,"persistence":"rejection_recorded","newFactsCommitted":false,"retryable":false,"retirementAllowed":true,"rejectionToken":"synthetic-parent-token","rejectionExpiresAt":expiry,"diagnostics":f.batch.samples.iter().map(|p|json!({"sampleId":p.sample_id,"part":p.part,"diagnosis":"eligible","historicalProof":Value::Null})).collect::<Vec<_>>()}});
    for status in [201, 418] {
        let mut bad = rejected.clone();
        bad["code"] = json!(status);
        assert!(
            matches!(classify(&f.batch,status,"application/json",&serde_json::to_vec(&bad).unwrap(),None,1,0),Reply::Failure{state,..}if state=="unknown")
        );
    }
    for pointer in ["/errorCode", "/data/retryable", "/data/diagnostics/0/part"] {
        let mut bad = rejected.clone();
        *bad.pointer_mut(pointer).unwrap() = json!("forged");
        assert!(
            matches!(classify(&f.batch,403,"application/json",&serde_json::to_vec(&bad).unwrap(),None,1,0),Reply::Failure{state,..}if state=="unknown")
        );
    }
    let mut extra = rejected.clone();
    extra["data"]["unexpected"] = json!(true);
    assert!(
        matches!(classify(&f.batch,403,"application/json",&serde_json::to_vec(&extra).unwrap(),None,1,0),Reply::Failure{state,..}if state=="unknown")
    );
    let raw = serde_json::to_string_pretty(&rejected).unwrap();
    let eligible = match classify(
        &f.batch,
        403,
        "application/json",
        raw.as_bytes(),
        None,
        1,
        0,
    ) {
        Reply::Rejected { eligible, .. } => eligible,
        _ => panic!("valid recorded rejection required"),
    };
    s.reject_delivery(&f, &rejected, &eligible, &raw).unwrap();
    let child = s.next_delivery().unwrap().unwrap();
    assert_ne!(child.batch.batch_id, f.batch.batch_id);
    assert_eq!(
        child.batch.parent.as_ref().unwrap().batch_id,
        f.batch.batch_id
    );
    assert_eq!(
        child.batch.parent.as_ref().unwrap().request_digest,
        f.batch.request_digest
    );
    assert_eq!(
        child.batch.parent.as_ref().unwrap().rejection_token,
        "synthetic-parent-token"
    );
    assert_eq!(
        child.batch.samples[0].payload_utf8,
        f.batch.samples[0].payload_utf8
    );
    assert_eq!(
        child.batch.samples[0].content_digest,
        f.batch.samples[0].content_digest
    );
    assert_eq!(child.depth, 1);
    let ack = receipt(&child);
    s.mark_dispatch(&child).unwrap();
    s.commit_delivery(&child, &ack, &serde_json::to_string(&ack).unwrap())
        .unwrap();
    assert_eq!(s.delivery_snapshot(false).unwrap()["acknowledged"], 1);
}

#[test]
fn manual_read_limits_and_persisted_plc_group_rotation() {
    use crate::domain::local_delivery::{ReadQuery, Rotation};
    let read = ReadQuery {
        plc_id: "plc-demo".into(),
        mode: None,
        from: None,
        to: None,
        cursor: None,
        page: Some(1),
    };
    assert_eq!(read.parameters().unwrap().3, 1);
    let mut original = read.clone();
    original.mode = Some("original".into());
    original.from = Some("2026-11-04T00:00:00.000+08:00".into());
    original.to = Some("2026-11-05T00:00:00.000+08:00".into());
    assert_eq!(original.parameters().unwrap().3, 1);
    original.page = Some(21);
    assert!(original.parameters().is_err());
    let mut latest = read;
    latest.mode = Some("latest".into());
    assert_eq!(latest.parameters().unwrap().3, 8);
    let candidates = [("A", "fast"), ("A", "slow"), ("B", "only")];
    let mut rotation = Rotation::default();
    let mut seen = vec![];
    for _ in 0..6 {
        let chosen = *candidates
            .iter()
            .min_by(|a, b| rotation.compare(**a, **b))
            .unwrap();
        seen.push(chosen);
        rotation.advance(chosen.0, chosen.1);
        rotation = Rotation::decode(&serde_json::to_string(&rotation).unwrap());
    }
    assert_eq!(
        seen,
        [
            ("A", "fast"),
            ("B", "only"),
            ("A", "slow"),
            ("B", "only"),
            ("A", "fast"),
            ("B", "only")
        ]
    );
}
#[test]
fn retry_clock_ignores_running_wall_jumps_and_clamps_restart() {
    use super::RetryClock;
    let rows = vec![("a".into(), "2026-11-05T10:00:30.000+08:00".into())];
    let mut clock = RetryClock::default();
    clock
        .sync(&rows, "2026-11-05T10:00:00.000+08:00", 1000)
        .unwrap();
    assert!(clock.ready(30999).is_empty());
    clock
        .sync(&rows, "2026-11-05T23:00:00.000+08:00", 1001)
        .unwrap();
    assert!(clock.ready(30999).is_empty());
    clock
        .sync(&rows, "2026-11-04T00:00:00.000+08:00", 1002)
        .unwrap();
    assert_eq!(clock.ready(31000), ["a"]);
    let mut restart = RetryClock::default();
    restart
        .sync(&rows, "2026-11-04T00:00:00.000+08:00", 0)
        .unwrap();
    assert!(restart.ready(299999).is_empty());
    assert_eq!(restart.ready(300000), ["a"]);
    let mut expired = RetryClock::default();
    expired
        .sync(&rows, "2026-11-06T00:00:00.000+08:00", 0)
        .unwrap();
    assert!(expired.ready(999).is_empty());
    assert_eq!(expired.ready(1000), ["a"]);
}

// v1 dispatch is retired. The two v2 worker tests below retain the former
// single-worker, pause/in-flight, resume, shutdown and stopped-reopen checks.
#[cfg(unix)]
#[test]
fn legacy_engine_does_not_dispatch_or_rewrite_inflight_v1_evidence() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::sealed_v3_inflight_fixture,
        services::local_supervisor::LocalEngine,
    };
    let profile = sealed_v3_inflight_fixture();
    let path = profile.join("local-acquisition-v1/runtime.sqlite");
    let before = rusqlite::Connection::open_with_flags(
        &path,
        rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
    )
    .unwrap();
    let ledger: (String, u32, String, String, i64, i64) = before.query_row(
        "SELECT state,attempt,body,body_sha,(SELECT count(*) FROM delivery_receipts),(SELECT count(*) FROM sample_delivery WHERE state='pending') FROM delivery_batches", [],
        |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?)),
    ).unwrap();
    assert_eq!(
        (&*ledger.0, ledger.1, ledger.4, ledger.5),
        ("inflight", 1, 0, 2)
    );
    before.close().unwrap();
    let boot = Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    };
    let engine = LocalEngine::open(boot.clone()).unwrap();
    assert!(!engine.delivery_available().unwrap());
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    for action in ["start", "resume"] {
        assert_eq!(
            engine
                .set_delivery_using(action, || panic!("v1 client must not be constructed"))
                .unwrap_err(),
            "delivery_profile_upgrade_required"
        );
    }
    engine
        .set_delivery_using("pause", || panic!("pause must not construct a client"))
        .unwrap();
    assert!(engine.delivery.lock().unwrap().join.is_none());
    engine.shutdown();
    drop(engine);
    let reopened = LocalEngine::open(boot).unwrap();
    assert_eq!(reopened.delivery_snapshot().unwrap()["running"], false);
    let after = reopened.storage.call(true, |s| s.runtime.query_row(
        "SELECT state,attempt,body,body_sha,(SELECT count(*) FROM delivery_receipts),(SELECT count(*) FROM sample_delivery WHERE state='pending') FROM delivery_batches", [],
        |r| Ok((r.get::<_,String>(0)?,r.get::<_,u32>(1)?,r.get::<_,String>(2)?,r.get::<_,String>(3)?,r.get::<_,i64>(4)?,r.get::<_,i64>(5)?)),
    ).map_err(crate::infrastructure::local_store::sql_error)).unwrap();
    assert_eq!(after, ledger);
    reopened.shutdown();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn v2_saved_binding_cycle_reopens_and_delivers_matching_receipts_over_loopback() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            add_v4_cycle_for, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{
        io::{Read, Write},
        net::TcpListener,
        sync::mpsc,
        time::{Duration, Instant},
    };

    let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
    listener.set_nonblocking(true).unwrap();
    let origin = format!("http://{}", listener.local_addr().unwrap());
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let boot = Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    };
    let engine = LocalEngine::open(boot.clone()).unwrap();
    let first_local_plc = engine
        .storage
        .call(true, |s| {
            let active = s.configuration()?.active.ok_or("active_missing")?;
            Ok(s.revision(&active)?.plcs[0].id.clone())
        })
        .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    settings.origin = Some(origin.clone());
    settings.interval_seconds = 1;
    for (index, binding) in settings.bindings.iter_mut().enumerate() {
        binding.instance_id = format!("instance-{index}");
        binding.plc_id = format!("acq004-plc-{index}");
        binding.source_generation = format!("acq004-new-generation-{index}");
    }
    let first_binding = settings
        .bindings
        .iter()
        .find(|binding| binding.local_plc_id == first_local_plc)
        .unwrap();
    assert!(!first_binding.instance_id.is_empty());
    let saved = engine
        .save_sample_upload_settings(settings, expected)
        .unwrap();
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    assert_eq!(engine.delivery_snapshot().unwrap()["pending"], 0);
    engine.shutdown();
    drop(engine);

    let engine = LocalEngine::open(boot.clone()).unwrap();
    let loaded = engine.sample_upload_settings().unwrap();
    assert_eq!(loaded.settings_revision, saved.settings_revision);
    assert_eq!(loaded.origin.as_deref(), Some(origin.as_str()));
    assert_eq!(
        loaded
            .bindings
            .iter()
            .map(|b| b.instance_id.as_str())
            .collect::<std::collections::BTreeSet<_>>()
            .len(),
        2
    );
    assert_eq!(loaded.bindings, saved.bindings);
    engine
        .storage
        .call(false, |s| add_v4_cycle_for(s, 0))
        .unwrap();
    engine
        .storage
        .call(false, |s| add_v4_cycle_for(s, 1))
        .unwrap();
    assert_eq!(engine.delivery_snapshot().unwrap()["pending"], 4);
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    assert!(
        matches!(listener.accept(), Err(error) if error.kind() == std::io::ErrorKind::WouldBlock)
    );

    let (sent, received) = mpsc::sync_channel(5);
    let (continue_send, continue_receive) = mpsc::sync_channel::<()>(1);
    let server = std::thread::spawn(move || {
        for request_number in 0..5 {
            let deadline = Instant::now() + Duration::from_secs(10);
            let mut stream = loop {
                match listener.accept() {
                    Ok((stream, _)) => break stream,
                    Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                        assert!(Instant::now() < deadline, "no synthetic loopback request");
                        std::thread::sleep(Duration::from_millis(10));
                    }
                    Err(error) => panic!("loopback accept failed: {error}"),
                }
            };
            stream
                .set_read_timeout(Some(Duration::from_secs(5)))
                .unwrap();
            let mut bytes = Vec::new();
            let mut buffer = [0u8; 8192];
            let (head_end, length) = loop {
                let n = stream.read(&mut buffer).unwrap();
                assert!(n > 0);
                bytes.extend_from_slice(&buffer[..n]);
                if let Some(at) = bytes.windows(4).position(|window| window == b"\r\n\r\n") {
                    let header = std::str::from_utf8(&bytes[..at])
                        .unwrap()
                        .to_ascii_lowercase();
                    assert!(header
                        .starts_with("post /api/v1/integration/plc-facts/samples http/1.1\r\n"));
                    assert!(!header.contains("authorization:"));
                    let length = header
                        .lines()
                        .find_map(|line| {
                            line.strip_prefix("content-length:")
                                .map(|value| value.trim().parse::<usize>().unwrap())
                        })
                        .unwrap();
                    break (at + 4, length);
                }
            };
            while bytes.len() - head_end < length {
                let n = stream.read(&mut buffer).unwrap();
                assert!(n > 0);
                bytes.extend_from_slice(&buffer[..n]);
            }
            let body = String::from_utf8(bytes[head_end..head_end + length].to_vec()).unwrap();
            let request: Value = serde_json::from_str(&body).unwrap();
            let receipt_instance = if request_number == 0 {
                json!("wrong-instance")
            } else {
                request["instanceId"].clone()
            };
            let response = json!({"code":200,"message":"success","data":{
                "contractVersion":"plc-facts/v2","instanceId":receipt_instance,
                "sampleId":request["sampleId"],"status":"committed","outcome":if request_number == 4 { "duplicate" } else { "created" }}})
            .to_string();
            write!(stream, "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}", response.len(), response).unwrap();
            sent.send(body).unwrap();
            if request_number == 0 {
                continue_receive
                    .recv_timeout(Duration::from_secs(10))
                    .unwrap();
            }
        }
    });
    let bindings = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    assert!(bindings.len() >= 4);
    assert_eq!(
        engine
            .set_delivery("start", Some("stale".into()), Some(bindings.clone()))
            .unwrap_err(),
        "source_confirmation_changed"
    );
    assert_eq!(
        engine
            .set_delivery(
                "start",
                Some(loaded.settings_revision.clone()),
                Some(bindings[..bindings.len() - 1].to_vec())
            )
            .unwrap_err(),
        "source_confirmation_changed"
    );
    let mut wrong_instance = bindings.clone();
    wrong_instance[0].instance_id = "incorrect-instance".into();
    assert_eq!(
        engine
            .set_delivery(
                "resume",
                Some(loaded.settings_revision.clone()),
                Some(wrong_instance)
            )
            .unwrap_err(),
        "source_confirmation_changed"
    );
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    engine
        .set_delivery(
            "start",
            Some(loaded.settings_revision.clone()),
            Some(bindings),
        )
        .unwrap();
    let first = received.recv_timeout(Duration::from_secs(12)).unwrap();
    let first_sample = serde_json::from_str::<Value>(&first).unwrap()["sampleId"]
        .as_str()
        .unwrap()
        .to_owned();
    let deadline = Instant::now() + Duration::from_secs(5);
    loop {
        let id = first_sample.clone();
        let state = engine
            .storage
            .call(true, move |s| s.get_sample_upload(&id))
            .unwrap();
        if state["state"] == "unknown" {
            break;
        }
        assert!(
            Instant::now() < deadline,
            "invalid receipt did not remain unknown"
        );
        std::thread::sleep(Duration::from_millis(10));
    }
    continue_send.send(()).unwrap();
    let mut requests = vec![first.clone()];
    requests.extend((0..4).map(|_| received.recv_timeout(Duration::from_secs(12)).unwrap()));
    assert_eq!(requests.iter().filter(|body| **body == first).count(), 2);
    assert_eq!(
        requests
            .iter()
            .map(
                |body| serde_json::from_str::<Value>(body).unwrap()["sampleId"]
                    .as_str()
                    .unwrap()
                    .to_owned()
            )
            .collect::<std::collections::BTreeSet<_>>()
            .len(),
        4
    );
    server.join().unwrap();
    let deadline = Instant::now() + Duration::from_secs(5);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 4 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    assert_eq!(engine.delivery_snapshot().unwrap()["pending"], 0);
    for body in requests {
        let request: Value = serde_json::from_str(&body).unwrap();
        let bound = loaded
            .bindings
            .iter()
            .find(|b| b.plc_id == request["plcId"].as_str().unwrap())
            .unwrap();
        assert_eq!(request["instanceId"], bound.instance_id);
        assert_eq!(request["sourceGeneration"], bound.source_generation);
        assert!([1, 2].contains(&request["dbNumber"].as_u64().unwrap()));
        assert!(
            request["sourceSeq"]
                .as_str()
                .unwrap()
                .parse::<u64>()
                .unwrap()
                > 0
        );
        let sample_id = request["sampleId"].as_str().unwrap().to_string();
        let row = engine.storage.call(true, move |s| {
            s.runtime.query_row("SELECT state,instance_id,plc_id,source_generation,body,receipt FROM sample_uploads WHERE sample_id=?1", [&sample_id], |row| {
                Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, String>(2)?,
                    row.get::<_, String>(3)?, row.get::<_, String>(4)?, row.get::<_, String>(5)?))
            }).map_err(crate::infrastructure::local_store::sql_error)
        }).unwrap();
        assert_eq!(row.0, "acknowledged");
        assert_eq!(row.1, bound.instance_id);
        assert_eq!(row.2, bound.plc_id);
        assert_eq!(row.3, bound.source_generation);
        assert_eq!(row.4, body);
        let receipt: Value = serde_json::from_str(&row.5).unwrap();
        assert_eq!(receipt["data"]["sampleId"], request["sampleId"]);
        assert_eq!(receipt["data"]["status"], "committed");
    }
    engine.shutdown();
    drop(engine);
    let reopened = LocalEngine::open(boot).unwrap();
    assert_eq!(reopened.delivery_snapshot().unwrap()["running"], false);
    assert_eq!(reopened.delivery_snapshot().unwrap()["acknowledged"], 4);
    reopened.shutdown();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{
            atomic::{AtomicUsize, Ordering},
            mpsc, Arc, Mutex,
        },
        time::{Duration, Instant},
    };
    struct Controlled {
        calls: AtomicUsize,
        entered: mpsc::SyncSender<(String, String, String)>,
        release: Mutex<mpsc::Receiver<()>>,
    }
    impl Transport for Controlled {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 dispatch forbidden")
        }
        fn post_sample(&self, target: &str, body: &str) -> Result<Response, String> {
            let value: Value = serde_json::from_str(body).map_err(|_| "synthetic_request")?;
            self.calls.fetch_add(1, Ordering::SeqCst);
            self.entered
                .send((
                    value["sampleId"].as_str().unwrap().into(),
                    target.into(),
                    body.into(),
                ))
                .map_err(|_| "synthetic_channel")?;
            self.release
                .lock()
                .unwrap()
                .recv_timeout(Duration::from_secs(5))
                .map_err(|_| "synthetic_deadline")?;
            Ok(Response { status:200, media_type:"application/json".into(), retry_after:None, body:serde_json::to_vec(&json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":value["instanceId"],"sampleId":value["sampleId"],"status":"committed","outcome":"created"}})).unwrap() })
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let boot = Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    };
    let engine = LocalEngine::open(boot.clone()).unwrap();
    assert!(!engine.delivery_snapshot().unwrap()["running"]
        .as_bool()
        .unwrap());
    let mut settings = engine.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:8001".into());
    settings.interval_seconds = 1;
    engine
        .save_sample_upload_settings(settings, expected)
        .unwrap();
    let (entered_tx, entered_rx) = mpsc::sync_channel(4);
    let (release_tx, release_rx) = mpsc::sync_channel(4);
    let transport = Arc::new(Controlled {
        calls: AtomicUsize::new(0),
        entered: entered_tx,
        release: Mutex::new(release_rx),
    });
    let substitute = transport.clone();
    engine
        .set_delivery_using("start", move || Ok(substitute))
        .unwrap();
    let first = entered_rx.recv_timeout(Duration::from_secs(3)).unwrap();
    let stale = engine.sample_upload_settings().unwrap();
    assert_eq!(
        engine
            .save_sample_upload_settings(stale, "stale-revision".into())
            .unwrap_err(),
        "delivery_settings_conflict"
    );
    assert!(engine.delivery_snapshot().unwrap()["running"]
        .as_bool()
        .unwrap());
    let worker = engine
        .delivery
        .lock()
        .unwrap()
        .join
        .as_ref()
        .unwrap()
        .thread()
        .id();
    engine
        .set_delivery_using("pause", || panic!("pause cannot construct a client"))
        .unwrap();
    release_tx.send(()).unwrap();
    let deadline = Instant::now() + Duration::from_secs(3);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 1 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    std::thread::sleep(Duration::from_millis(1200));
    assert_eq!(transport.calls.load(Ordering::SeqCst), 1);
    assert_eq!(engine.delivery_snapshot().unwrap()["pending"], 1);
    engine
        .set_delivery_using("resume", || panic!("resume reuses the worker"))
        .unwrap();
    let second = entered_rx.recv_timeout(Duration::from_secs(3)).unwrap();
    assert_ne!(first.0, second.0);
    assert_eq!(first.1, second.1);
    assert_eq!(
        engine
            .delivery
            .lock()
            .unwrap()
            .join
            .as_ref()
            .unwrap()
            .thread()
            .id(),
        worker
    );
    // Saving a new target stops new dispatch while the old in-flight receipt settles.
    let mut changed = engine.sample_upload_settings().unwrap();
    let expected = changed.settings_revision.clone();
    changed.origin = Some("http://127.0.0.1:8002".into());
    engine
        .save_sample_upload_settings(changed, expected)
        .unwrap();
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    release_tx.send(()).unwrap();
    let deadline = Instant::now() + Duration::from_secs(3);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 2 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    for (id, original_url, original_body) in [first, second] {
        let detail = engine
            .storage
            .call(true, move |s| s.get_sample_upload(&id))
            .unwrap();
        assert_eq!(detail["state"], "acknowledged");
        assert_eq!(detail["origin"], original_url);
        assert_eq!(detail["body"], original_body);
    }
    assert_eq!(transport.calls.load(Ordering::SeqCst), 2);
    engine.shutdown();
    drop(engine);
    let reopened = LocalEngine::open(boot).unwrap();
    assert_eq!(reopened.delivery_snapshot().unwrap()["running"], false);
    assert_eq!(reopened.delivery_snapshot().unwrap()["acknowledged"], 2);
    reopened.shutdown();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn v2_worker_drains_bounded_bursts_and_interleaves_old_with_new() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            add_v4_cycle, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{
        collections::BTreeSet,
        sync::{
            atomic::{AtomicUsize, Ordering},
            mpsc, Arc, Mutex,
        },
        time::{Duration, Instant},
    };
    struct Burst {
        count: AtomicUsize,
        sent: mpsc::SyncSender<String>,
        first: Mutex<mpsc::Receiver<()>>,
    }
    impl Transport for Burst {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 dispatch forbidden")
        }
        fn post_sample(&self, _: &str, body: &str) -> Result<Response, String> {
            let v: Value = serde_json::from_str(body).map_err(|_| "synthetic_request")?;
            let n = self.count.fetch_add(1, Ordering::SeqCst);
            self.sent
                .send(v["sampleId"].as_str().unwrap().into())
                .map_err(|_| "synthetic_channel")?;
            if n == 0 {
                self.first
                    .lock()
                    .unwrap()
                    .recv_timeout(Duration::from_secs(5))
                    .map_err(|_| "synthetic_deadline")?;
            }
            std::thread::sleep(Duration::from_millis(10));
            Ok(Response { status:200, media_type:"application/json".into(), retry_after:None, body:serde_json::to_vec(&json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":v["instanceId"],"sampleId":v["sampleId"],"status":"committed","outcome":"created"}})).unwrap() })
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 6);
    let boot = Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    };
    let engine = LocalEngine::open(boot).unwrap();
    let initial: Vec<String> = engine
        .storage
        .call(true, |s| {
            s.runtime
                .prepare("SELECT id FROM samples ORDER BY sample_order")
                .map_err(crate::infrastructure::local_store::sql_error)?
                .query_map([], |r| r.get(0))
                .map_err(crate::infrastructure::local_store::sql_error)?
                .collect::<Result<_, _>>()
                .map_err(crate::infrastructure::local_store::sql_error)
        })
        .unwrap();
    assert_eq!(initial.len(), 12);
    let mut settings = engine.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:8001".into());
    assert_eq!(settings.interval_seconds, 5);
    engine
        .save_sample_upload_settings(settings, expected)
        .unwrap();
    let (sent_tx, sent_rx) = mpsc::sync_channel(32);
    let (gate_tx, gate_rx) = mpsc::sync_channel(1);
    let transport = Arc::new(Burst {
        count: AtomicUsize::new(0),
        sent: sent_tx,
        first: Mutex::new(gate_rx),
    });
    let start = Instant::now();
    let sender = transport.clone();
    engine
        .set_delivery_using("start", move || Ok(sender))
        .unwrap();
    let first = sent_rx.recv_timeout(Duration::from_secs(3)).unwrap();
    assert_eq!(first, initial[0]);
    engine
        .storage
        .call(false, |s| {
            add_v4_cycle(s)?;
            add_v4_cycle(s)?;
            Ok(())
        })
        .unwrap();
    let producer = engine.clone();
    let producer = std::thread::spawn(move || {
        for _ in 0..4 {
            std::thread::sleep(Duration::from_millis(25));
            producer.storage.call(false, add_v4_cycle).unwrap();
        }
    });
    gate_tx.send(()).unwrap();
    let mut sent = vec![first];
    while sent.len() < 24 {
        sent.push(sent_rx.recv_timeout(Duration::from_secs(4)).unwrap());
    }
    producer.join().unwrap();
    let deadline = Instant::now() + Duration::from_secs(3);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 24 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    assert!(start.elapsed() < Duration::from_secs(5));
    assert_eq!(sent.iter().collect::<BTreeSet<_>>().len(), 24);
    let original: BTreeSet<_> = initial.iter().collect();
    assert!(!original.contains(&sent[1]));
    assert!(initial.iter().all(|id| sent.contains(id)));
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn v2_worker_retries_after_local_ack_write_failure_without_reopen() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::{Duration, Instant},
    };
    struct Committed(mpsc::SyncSender<String>);
    impl Transport for Committed {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            unreachable!()
        }
        fn post_sample(&self, _: &str, body: &str) -> Result<Response, String> {
            self.0.send(body.into()).map_err(|_| "test_channel")?;
            let sample: Value = serde_json::from_str(body).map_err(|_| "test_body")?;
            Ok(Response { status:200, media_type:"application/json".into(), retry_after:None, body:json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":sample["instanceId"],"sampleId":sample["sampleId"],"status":"committed","outcome":"duplicate"}}).to_string().into_bytes() })
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    settings.interval_seconds = 1;
    engine
        .save_sample_upload_settings(settings, expected)
        .unwrap();
    engine.storage.call(false, |s| s.runtime.execute_batch("CREATE TEMP TRIGGER fail_sample_ack BEFORE UPDATE ON sample_uploads WHEN NEW.state='acknowledged' BEGIN SELECT RAISE(FAIL,'synthetic_ack_write_failure'); END;").map_err(crate::infrastructure::local_store::sql_error)).unwrap();
    let (tx, rx) = mpsc::sync_channel(8);
    engine
        .set_delivery_using("start", || Ok(Arc::new(Committed(tx))))
        .unwrap();
    let first = rx.recv_timeout(Duration::from_secs(3)).unwrap();
    let sample: Value = serde_json::from_str(&first).unwrap();
    let id = sample["sampleId"].as_str().unwrap().to_string();
    let deadline = Instant::now() + Duration::from_secs(3);
    loop {
        let snapshot = engine.delivery_snapshot().unwrap();
        if snapshot["running"] == false && snapshot["lastError"].is_string() {
            break;
        }
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    let check = id.clone();
    assert_eq!(
        engine
            .storage
            .call(true, move |s| s
                .runtime
                .query_row(
                    "SELECT state FROM sample_uploads WHERE sample_id=?1",
                    [&check],
                    |r| r.get::<_, String>(0)
                )
                .map_err(crate::infrastructure::local_store::sql_error))
            .unwrap(),
        "inflight"
    );
    engine
        .storage
        .call(false, |s| {
            s.runtime
                .execute_batch("DROP TRIGGER fail_sample_ack")
                .map_err(crate::infrastructure::local_store::sql_error)
        })
        .unwrap();
    engine
        .set_delivery_using("resume", || panic!("reuse worker"))
        .unwrap();
    let deadline = Instant::now() + Duration::from_secs(6);
    loop {
        let body = rx.recv_timeout(Duration::from_secs(4)).unwrap();
        let value: Value = serde_json::from_str(&body).unwrap();
        if value["sampleId"] == id {
            assert_eq!(body, first);
            break;
        }
        assert!(Instant::now() < deadline);
    }
    let deadline = Instant::now() + Duration::from_secs(4);
    loop {
        let check = id.clone();
        let state = engine
            .storage
            .call(true, move |s| {
                s.runtime
                    .query_row(
                        "SELECT state FROM sample_uploads WHERE sample_id=?1",
                        [&check],
                        |r| r.get::<_, String>(0),
                    )
                    .map_err(crate::infrastructure::local_store::sql_error)
            })
            .unwrap();
        if state == "acknowledged" {
            break;
        }
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[test]
fn receipt_partial_quality_and_cached_sample_completeness() {
    // Provider persist(): complete counts parts, quality accumulates observations;
    // first_result retains each duplicate's original sourceSampleComplete flag.
    let vectors: Value = serde_json::from_str(include_str!(
        "../../../../../contracts/published/http-api/plc-facts-v1/vectors.json"
    ))
    .unwrap();
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let mut f = s.next_delivery().unwrap().unwrap();
    f.batch = serde_json::from_value(vectors["fixtures"]["partialFragment"].clone()).unwrap();
    let partial = receipt(&f);
    assert_eq!(partial["data"]["cycles"][0]["complete"], false);
    assert_eq!(partial["data"]["cycles"][0]["qualityGood"], true);
    assert_eq!(partial["data"]["results"][0]["sourceSampleComplete"], false);
    assert!(verify_success(&f.batch, &partial).is_ok());
    for (field, value) in [
        ("complete", json!(true)),
        ("receivedParts", json!(0)),
        ("expectedParts", json!(3)),
    ] {
        let mut bad = partial.clone();
        bad["data"]["cycles"][0][field] = value;
        assert!(verify_success(&f.batch, &bad).is_err(), "{field}");
    }
    // Later arrival completes the cycle; a historical duplicate still reports its cached false.
    let mut cached = partial.clone();
    cached["data"]["newFactsCommitted"] = json!(false);
    cached["data"]["outcome"] = json!("duplicate");
    cached["data"]["commitSerial"] = Value::Null;
    cached["data"]["results"][0]["outcome"] = json!("duplicate");
    cached["data"]["results"][0]["confirmation"] = json!("historical_committed");
    cached["data"]["results"][0]["valueReadable"] = json!(false);
    cached["data"]["cycles"][0]["receivedParts"] = json!(2);
    cached["data"]["cycles"][0]["complete"] = json!(true);
    assert!(verify_success(&f.batch, &cached).is_ok());
    let mut impossible_created = partial.clone();
    impossible_created["data"]["cycles"][0]["receivedParts"] = json!(2);
    impossible_created["data"]["cycles"][0]["complete"] = json!(true);
    assert!(verify_success(&f.batch, &impossible_created).is_err());
    let mut impossible_early = partial.clone();
    impossible_early["data"]["results"][0]["sourceSampleComplete"] = json!(true);
    assert!(verify_success(&f.batch, &impossible_early).is_err());
    f.batch = serde_json::from_value(vectors["fixtures"]["fragmented"].clone()).unwrap();
    let full = receipt(&f);
    assert!(verify_success(&f.batch, &full).is_ok());
    let mut impossible = full;
    impossible["data"]["results"][0]["sourceSampleComplete"] = json!(false);
    assert!(verify_success(&f.batch, &impossible).is_err());
    f.batch = serde_json::from_value(vectors["request"].clone()).unwrap();
    let mut single = receipt(&f);
    single["data"]["results"][0]["sourceSampleComplete"] = json!(false);
    assert!(verify_success(&f.batch, &single).is_err());
}

#[cfg(unix)]
#[test]
fn qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct Record(mpsc::Sender<String>);
    impl Transport for Record {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("no v1 allowed");
        }
        fn post_sample(&self, target: &str, _: &str) -> Result<Response, String> {
            self.0.send(target.into()).unwrap();
            Err("qa_synthetic_response".into())
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let old_revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    let old = engine
        .save_sample_upload_settings(settings, old_revision)
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let (transport_tx, transport_rx) = mpsc::channel();
    let start_engine = engine.clone();
    let confirmation = old.settings_revision.clone();
    let start = std::thread::spawn(move || {
        start_engine.set_delivery_using_checked_at_lock(
            "start",
            Some((confirmation, sources)),
            || Ok(Arc::new(Record(transport_tx))),
            || {
                entered_tx.send(()).unwrap();
                resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
            },
        )
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    let mut new = old.clone();
    new.origin = Some("http://127.0.0.1:38118".into());
    let saved = engine
        .save_sample_upload_settings(new, old.settings_revision)
        .unwrap();
    assert!(!engine.delivery_snapshot().unwrap()["running"]
        .as_bool()
        .unwrap());
    resume_tx.send(()).unwrap();
    let start_result = start.join().unwrap();
    let dispatched = transport_rx.recv_timeout(Duration::from_secs(2)).ok();
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
    assert_eq!(start_result.unwrap_err(), "source_confirmation_changed");
    assert!(
        dispatched.is_none(),
        "stale start dispatched to {dispatched:?}"
    );
    assert_eq!(saved.origin.as_deref(), Some("http://127.0.0.1:38118"));
}

#[cfg(unix)]
#[test]
fn qa_rebind_refuses_stale_complete_source_confirmation() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            add_v4_cycle_for, deactivate_second_plc, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{sync::mpsc, time::Duration};
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let old_origin = "http://127.0.0.1:38117";
    let new_origin = "http://127.0.0.1:38118";
    let mut settings = engine.sample_upload_settings().unwrap();
    let rev = settings.settings_revision.clone();
    settings.origin = Some(old_origin.into());
    let settings = engine.save_sample_upload_settings(settings, rev).unwrap();
    let old_url = settings.target().unwrap().unwrap();
    let lookup_target = old_url.clone();
    let frozen = engine
        .storage
        .call(false, move |s| {
            add_v4_cycle_for(s, 0)?;
            let sources = s.sample_upload_bindings()?;
            let frozen = s
                .next_sample_upload(&lookup_target, &sources, false)?
                .unwrap();
            let attempt = s.mark_sample_upload_attempt(&frozen)?;
            s.record_sample_upload_response(&frozen, Err("qa_synthetic_response".into()), attempt)?;
            Ok(frozen)
        })
        .unwrap();
    let mut new = settings.clone();
    new.origin = Some(new_origin.into());
    let new = engine
        .save_sample_upload_settings(new, settings.settings_revision)
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let rebind_engine = engine.clone();
    let sample_id = frozen.sample_id.clone();
    let expected = new.settings_revision.clone();
    let confirmed = sources.clone();
    let rebind = std::thread::spawn(move || {
        rebind_engine.rebind_sample_upload_after_check(
            sample_id,
            old_url,
            expected,
            confirmed,
            || {
                entered_tx.send(()).unwrap();
                resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
            },
        )
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    let current = engine
        .storage
        .call(false, |s| {
            deactivate_second_plc(s)?;
            s.sample_upload_bindings()
        })
        .unwrap();
    assert_ne!(sources, current);
    assert_eq!(
        engine.sample_upload_settings().unwrap().settings_revision,
        new.settings_revision
    );
    assert!(current.iter().any(|b| b.instance_id == frozen.instance_id
        && b.plc_id == frozen.plc_id
        && b.db_number == frozen.db_number
        && b.source_generation == frozen.source_generation));
    resume_tx.send(()).unwrap();
    let result = rebind.join().unwrap();
    let frozen_id = frozen.sample_id.clone();
    let after = engine
        .storage
        .call(true, move |s| s.get_sample_upload(&frozen_id))
        .unwrap();
    assert_eq!(result.unwrap_err(), "source_confirmation_changed");
    assert!(after["origin"].as_str().unwrap().starts_with(old_origin));
    assert_eq!(after["state"], "unknown");
    assert_eq!(after["body"], frozen.body);
    assert_eq!(after["bodySha256"], frozen.body_sha);
    assert!(after["rebindings"].as_array().unwrap().is_empty());

    // A settings save after the service read must also preserve the old target.
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let other = engine.clone();
    let sample_id = frozen.sample_id.clone();
    let old_target = frozen.origin.clone();
    let revision = new.settings_revision.clone();
    let confirmed = current.clone();
    let rebind = std::thread::spawn(move || {
        other.rebind_sample_upload_after_check(sample_id, old_target, revision, confirmed, || {
            entered_tx.send(()).unwrap();
            resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        })
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    let mut later = new.clone();
    later.origin = Some("http://127.0.0.1:38119".into());
    let later = engine
        .save_sample_upload_settings(later, new.settings_revision)
        .unwrap();
    resume_tx.send(()).unwrap();
    assert_eq!(
        rebind.join().unwrap().unwrap_err(),
        "delivery_settings_conflict"
    );
    let sample_id = frozen.sample_id.clone();
    let unchanged = engine
        .storage
        .call(true, move |s| s.get_sample_upload(&sample_id))
        .unwrap();
    assert_eq!(unchanged["origin"], frozen.origin);
    assert_eq!(unchanged["body"], frozen.body);
    assert!(unchanged["rebindings"].as_array().unwrap().is_empty());
    engine
        .rebind_sample_upload(
            frozen.sample_id.clone(),
            frozen.origin.clone(),
            later.settings_revision,
            current,
        )
        .unwrap();
    let sample_id = frozen.sample_id.clone();
    let rebound = engine
        .storage
        .call(true, move |s| s.get_sample_upload(&sample_id))
        .unwrap();
    assert!(rebound["origin"]
        .as_str()
        .unwrap()
        .starts_with("http://127.0.0.1:38119"));
    assert_eq!(rebound["body"], frozen.body);
    assert_eq!(rebound["bodySha256"], frozen.body_sha);
    assert_eq!(rebound["rebindings"].as_array().unwrap().len(), 1);
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn start_refuses_sources_that_change_before_running() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            captured_v4_cycle_for, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct Record(mpsc::Sender<String>);
    impl Transport for Record {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, target: &str, _: &str) -> Result<Response, String> {
            self.0.send(target.into()).unwrap();
            Err("unexpected_dispatch".into())
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let (late_cycle, late_identity) = engine
        .storage
        .call(true, |s| captured_v4_cycle_for(s, 1))
        .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    for (i, b) in settings.bindings.iter_mut().enumerate() {
        b.instance_id = format!("new-instance-{i}");
        b.source_generation = format!("new-generation-{i}");
    }
    let saved = engine
        .save_sample_upload_settings(settings, expected)
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let (sent_tx, sent_rx) = mpsc::channel();
    let other = engine.clone();
    let revision = saved.settings_revision.clone();
    let confirmed = sources.clone();
    let start = std::thread::spawn(move || {
        other.set_delivery_using_checked("start", Some((revision, confirmed)), || {
            entered_tx.send(()).unwrap();
            resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
            Ok(Arc::new(Record(sent_tx)))
        })
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    engine
        .storage
        .call(false, move |s| {
            s.commit_cycle_with_reporting(late_cycle, late_identity)
                .map(|_| ())
        })
        .unwrap();
    let current = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    assert!(current.iter().any(|b| !sources.contains(b)));
    resume_tx.send(()).unwrap();
    assert_eq!(
        start.join().unwrap().unwrap_err(),
        "source_confirmation_changed"
    );
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    assert!(sent_rx.recv_timeout(Duration::from_millis(100)).is_err());
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn dispatch_rechecks_sources_after_selection_before_attempt() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            captured_v4_cycle_for, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct Record(mpsc::Sender<()>);
    impl Transport for Record {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, _: &str) -> Result<Response, String> {
            self.0.send(()).unwrap();
            Err("unexpected_dispatch".into())
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let (late_cycle, late_identity) = engine
        .storage
        .call(true, |s| captured_v4_cycle_for(s, 1))
        .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    for (i, b) in settings.bindings.iter_mut().enumerate() {
        b.instance_id = format!("new-instance-{i}");
        b.source_generation = format!("new-generation-{i}");
    }
    let saved = engine
        .save_sample_upload_settings(settings, revision)
        .unwrap();
    let target = saved.target().unwrap().unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    {
        let mut c = engine.delivery.lock().unwrap();
        c.running = true;
        c.origin = Some(target.clone());
        c.bindings = sources.clone();
    }
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let (sent_tx, sent_rx) = mpsc::channel();
    let other = engine.clone();
    let tick = std::thread::spawn(move || {
        other.delivery_tick_v2_before_mark(Arc::new(Record(sent_tx)), || {
            entered_tx.send(()).unwrap();
            resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        })
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    engine
        .storage
        .call(false, move |s| {
            s.commit_cycle_with_reporting(late_cycle, late_identity)
                .map(|_| ())
        })
        .unwrap();
    let current = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    assert!(current.iter().any(|b| !sources.contains(b)));
    resume_tx.send(()).unwrap();
    assert_eq!(tick.join().unwrap().unwrap_err(), "source_changed");
    assert!(sent_rx.recv_timeout(Duration::from_millis(100)).is_err());
    let stored = engine
        .storage
        .call(true, |s| {
            s.runtime
                .query_row(
                    "SELECT state,attempt,origin,body,body_sha FROM sample_uploads LIMIT 1",
                    [],
                    |r| {
                        Ok((
                            r.get::<_, String>(0)?,
                            r.get::<_, u32>(1)?,
                            r.get::<_, String>(2)?,
                            r.get::<_, String>(3)?,
                            r.get::<_, String>(4)?,
                        ))
                    },
                )
                .map_err(crate::infrastructure::local_store::sql_error)
        })
        .unwrap();
    assert_eq!(
        (stored.0.as_str(), stored.1, stored.2.as_str()),
        ("prepared", 0, target.as_str())
    );
    assert_eq!(
        crate::domain::facts_canonical::sha(stored.3.as_bytes()),
        stored.4
    );
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn qa2_pending_settings_commit_must_not_allow_new_post_to_stale_origin() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            add_v4_cycle_for, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct Record(mpsc::Sender<String>);
    impl Transport for Record {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden");
        }
        fn post_sample(&self, target: &str, _: &str) -> Result<Response, String> {
            self.0.send(target.into()).unwrap();
            Err("qa2_synthetic_response".into())
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    settings.interval_seconds = 1;
    let old = engine
        .save_sample_upload_settings(settings, expected)
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    let (posted_tx, posted_rx) = mpsc::channel();
    assert_eq!(
        engine
            .set_delivery_using_checked(
                "start",
                Some((old.settings_revision.clone(), sources.clone())),
                || Ok(Arc::new(Record(posted_tx)))
            )
            .unwrap()["running"],
        true
    );
    // Keep HTTP quiescent until the pending save has committed.
    let http = engine.delivery_http.lock().unwrap();
    let (block_ready_tx, block_ready_rx) = mpsc::channel();
    let (release_tx, release_rx) = mpsc::channel();
    let block_engine = engine.clone();
    let (queue_blocker_tx, queue_blocker_rx) = mpsc::channel();
    let blocker = std::thread::spawn(move || {
        queue_blocker_rx
            .recv_timeout(Duration::from_secs(5))
            .unwrap();
        block_engine.storage.call(false, move |_| {
            block_ready_tx.send(()).unwrap();
            release_rx.recv_timeout(Duration::from_secs(20)).unwrap();
            Ok(())
        })
    });
    let mut next = old.clone();
    next.origin = Some("http://127.0.0.1:38118".into());
    let result =
        engine.save_sample_upload_settings_after_lock(next, old.settings_revision.clone(), || {
            queue_blocker_tx.send(()).unwrap();
            block_ready_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        });
    assert_eq!(result.unwrap_err(), "storage_pending");
    assert!(!engine.delivery.lock().unwrap().running);
    // While the queued write has not settled, a fresh start cannot dispatch.
    assert_eq!(
        engine
            .set_delivery(
                "start",
                Some(old.settings_revision.clone()),
                Some(sources.clone())
            )
            .unwrap_err(),
        "storage_timeout"
    );
    release_tx.send(()).unwrap();
    // The caller of the blocking synthetic job timed out, too. Its actor turn has returned.
    assert_eq!(blocker.join().unwrap().unwrap_err(), "storage_pending");
    let new = engine
        .storage
        .call(false, |s| {
            let new = s.sample_upload_settings()?;
            add_v4_cycle_for(s, 0)?;
            Ok(new)
        })
        .unwrap();
    let snapshot = engine.delivery_snapshot().unwrap();
    assert_eq!(new.origin.as_deref(), Some("http://127.0.0.1:38118"));
    assert_ne!(new.settings_revision, old.settings_revision);
    assert_eq!(
        sources,
        engine
            .storage
            .call(true, |s| s.sample_upload_bindings())
            .unwrap()
    );
    assert_eq!(snapshot["running"], false);
    drop(http);
    let dispatched = posted_rx.recv_timeout(Duration::from_millis(250)).ok();
    assert!(dispatched.is_none(), "stale dispatch: {dispatched:?}");
    assert_eq!(
        engine
            .set_delivery("start", Some(old.settings_revision), Some(sources.clone()))
            .unwrap_err(),
        "source_confirmation_changed"
    );
    assert_eq!(
        engine
            .set_delivery("resume", Some(new.settings_revision), Some(sources))
            .unwrap()["running"],
        true
    );
    let new_target = posted_rx.recv_timeout(Duration::from_secs(4)).unwrap();
    assert!(
        new_target.starts_with("http://127.0.0.1:38118/"),
        "{new_target}"
    );
    engine.set_delivery("pause", None, None).unwrap();
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn pending_save_pauses_new_dispatch_but_settles_inflight_and_requires_reconfirmation() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{
            atomic::{AtomicUsize, Ordering},
            mpsc, Arc, Mutex,
        },
        time::{Duration, Instant},
    };
    struct Controlled {
        count: AtomicUsize,
        posted: mpsc::Sender<(String, String, String)>,
        release: Mutex<mpsc::Receiver<()>>,
        response_ready: mpsc::Sender<()>,
    }
    impl Transport for Controlled {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, target: &str, body: &str) -> Result<Response, String> {
            let request: Value = serde_json::from_str(body).map_err(|_| "invalid_fixture")?;
            let ordinal = self.count.fetch_add(1, Ordering::SeqCst);
            self.posted
                .send((
                    request["sampleId"].as_str().unwrap().into(),
                    target.into(),
                    body.into(),
                ))
                .map_err(|_| "fixture_channel")?;
            if ordinal == 0 {
                self.release
                    .lock()
                    .unwrap()
                    .recv_timeout(Duration::from_secs(25))
                    .map_err(|_| "fixture_timeout")?;
                self.response_ready
                    .send(())
                    .map_err(|_| "fixture_channel")?;
            }
            Ok(Response { status:200, media_type:"application/json".into(), retry_after:None, body:json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":request["instanceId"],"sampleId":request["sampleId"],"status":"committed","outcome":"created"}}).to_string().into_bytes() })
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    settings.interval_seconds = 1;
    let old = engine
        .save_sample_upload_settings(settings, revision)
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    let (posted_tx, posted_rx) = mpsc::channel();
    let (response_tx, response_rx) = mpsc::channel();
    let (response_ready_tx, response_ready_rx) = mpsc::channel();
    let transport = Arc::new(Controlled {
        count: AtomicUsize::new(0),
        posted: posted_tx,
        release: Mutex::new(response_rx),
        response_ready: response_ready_tx,
    });
    let substitute = transport.clone();
    engine
        .set_delivery_using_checked(
            "start",
            Some((old.settings_revision.clone(), sources.clone())),
            || Ok(substitute),
        )
        .unwrap();
    let first = posted_rx.recv_timeout(Duration::from_secs(4)).unwrap();
    assert!(first.1.starts_with("http://127.0.0.1:38117/"));
    let (queue_tx, queue_rx) = mpsc::channel();
    let (ready_tx, ready_rx) = mpsc::channel();
    let (release_tx, release_rx) = mpsc::channel();
    let blocker_engine = engine.clone();
    let blocker = std::thread::spawn(move || {
        queue_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        blocker_engine.storage.call(false, move |_| {
            ready_tx.send(()).unwrap();
            release_rx.recv_timeout(Duration::from_secs(20)).unwrap();
            Ok(())
        })
    });
    let mut changed = old.clone();
    changed.origin = Some("http://127.0.0.1:38118".into());
    let save = engine.save_sample_upload_settings_after_lock(
        changed,
        old.settings_revision.clone(),
        || {
            queue_tx.send(()).unwrap();
            ready_rx.recv_timeout(Duration::from_secs(5)).unwrap();
            // The original HTTP response arrives while the storage actor is blocked.
            response_tx.send(()).unwrap();
            response_ready_rx
                .recv_timeout(Duration::from_secs(5))
                .unwrap();
        },
    );
    assert_eq!(save.unwrap_err(), "storage_pending");
    assert!(!engine.delivery.lock().unwrap().running);
    // The dispatch permit cannot be released before the timed-out receipt error is latched.
    let deadline = Instant::now() + Duration::from_secs(3);
    loop {
        if let Ok(permit) = engine.delivery_http.try_lock() {
            assert_eq!(
                engine.delivery.lock().unwrap().error.as_deref(),
                Some("storage_pending")
            );
            drop(permit);
            break;
        }
        assert!(Instant::now() < deadline, "dispatch permit did not settle");
        std::thread::sleep(Duration::from_millis(10));
    }
    assert_eq!(
        engine
            .set_delivery(
                "start",
                Some(old.settings_revision.clone()),
                Some(sources.clone())
            )
            .unwrap_err(),
        "storage_timeout"
    );
    release_tx.send(()).unwrap();
    assert_eq!(blocker.join().unwrap().unwrap_err(), "storage_pending");
    let current = engine
        .storage
        .call(false, |s| s.sample_upload_settings())
        .unwrap();
    assert_eq!(current.origin.as_deref(), Some("http://127.0.0.1:38118"));
    assert_ne!(current.settings_revision, old.settings_revision);
    let deadline = Instant::now() + Duration::from_secs(4);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 1 {
        assert!(
            Instant::now() < deadline,
            "old in-flight receipt did not settle"
        );
        std::thread::sleep(Duration::from_millis(10));
    }
    let id = first.0.clone();
    let detail = engine
        .storage
        .call(true, move |s| s.get_sample_upload(&id))
        .unwrap();
    assert_eq!(detail["state"], "acknowledged");
    assert_eq!(detail["origin"], first.1);
    assert_eq!(detail["body"], first.2);
    assert!(detail["receipt"].as_str().is_some());
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    assert!(posted_rx.recv_timeout(Duration::from_millis(300)).is_err());
    assert_eq!(
        engine
            .set_delivery("resume", Some(old.settings_revision), Some(sources.clone()))
            .unwrap_err(),
        "source_confirmation_changed"
    );
    engine
        .set_delivery("resume", Some(current.settings_revision), Some(sources))
        .unwrap();
    let second = posted_rx
        .recv_timeout(Duration::from_secs(8))
        .unwrap_or_else(|error| {
            panic!(
                "confirmed resume did not dispatch: {error:?}; snapshot={:?}",
                engine.delivery_snapshot()
            )
        });
    assert_ne!(second.0, first.0);
    assert!(second.1.starts_with("http://127.0.0.1:38118/"));
    let deadline = Instant::now() + Duration::from_secs(4);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 2 {
        assert!(
            Instant::now() < deadline,
            "new confirmed receipt did not settle"
        );
        std::thread::sleep(Duration::from_millis(10));
    }
    engine.set_delivery("pause", None, None).unwrap();
    assert_eq!(transport.count.load(Ordering::SeqCst), 2);
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn plc_switch_rechecks_before_dispatch_without_stopping_other_sources() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct Record(mpsc::Sender<String>);
    impl Transport for Record {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, body: &str) -> Result<Response, String> {
            let value: serde_json::Value = serde_json::from_str(body).unwrap();
            self.0
                .send(value["sampleId"].as_str().unwrap().into())
                .unwrap();
            Ok(Response { status:200, media_type:"application/json".into(), retry_after:None, body:serde_json::json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":value["instanceId"],"sampleId":value["sampleId"],"status":"committed","outcome":"created"}}).to_string().into_bytes() })
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    let settings = engine
        .save_sample_upload_settings(settings, revision)
        .unwrap();
    let local = engine
        .storage
        .call(true, |s| {
            s.runtime
                .query_row(
                    "SELECT plc_id FROM samples ORDER BY sample_order LIMIT 1",
                    [],
                    |r| r.get::<_, String>(0),
                )
                .map_err(crate::infrastructure::local_store::sql_error)
        })
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    {
        let mut control = engine.delivery.lock().unwrap();
        control.running = true;
        control.origin = settings.target().unwrap();
        control.bindings = sources;
    }
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let (posted_tx, posted_rx) = mpsc::channel();
    let other = engine.clone();
    let sender = posted_tx.clone();
    let tick = std::thread::spawn(move || {
        other.delivery_tick_v2_before_mark(Arc::new(Record(sender)), || {
            entered_tx.send(()).unwrap();
            resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        })
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    let mut disabled = settings.clone();
    disabled.disabled_local_plcs.push(local);
    let disabled = engine
        .save_sample_upload_settings(disabled, settings.settings_revision)
        .unwrap();
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], true);
    resume_tx.send(()).unwrap();
    assert!(!tick.join().unwrap().unwrap());
    assert!(posted_rx.recv_timeout(Duration::from_millis(100)).is_err());
    let mut enabled = disabled.clone();
    enabled.disabled_local_plcs.clear();
    engine
        .save_sample_upload_settings(enabled, disabled.settings_revision)
        .unwrap();
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], true);
    assert!(engine
        .delivery_tick_v2(Arc::new(Record(posted_tx)))
        .unwrap());
    assert!(!posted_rx
        .recv_timeout(Duration::from_secs(1))
        .unwrap()
        .is_empty());
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn dispatch_rechecks_current_target_after_selection_before_attempt() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct Record(mpsc::Sender<()>);
    impl Transport for Record {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, _: &str) -> Result<Response, String> {
            self.0.send(()).unwrap();
            Err("unexpected_dispatch".into())
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    let old = engine
        .save_sample_upload_settings(settings, revision)
        .unwrap();
    let old_target = old.target().unwrap().unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    {
        let mut control = engine.delivery.lock().unwrap();
        control.running = true;
        control.origin = Some(old_target.clone());
        control.bindings = sources.clone();
    }
    let (entered_tx, entered_rx) = mpsc::channel();
    let (resume_tx, resume_rx) = mpsc::channel();
    let (posted_tx, posted_rx) = mpsc::channel();
    let other = engine.clone();
    let tick = std::thread::spawn(move || {
        other.delivery_tick_v2_before_mark(Arc::new(Record(posted_tx)), || {
            entered_tx.send(()).unwrap();
            resume_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        })
    });
    entered_rx.recv_timeout(Duration::from_secs(5)).unwrap();
    // Model the actor turn of a save that committed after its caller stopped waiting.
    let mut next = old.clone();
    next.origin = Some("http://127.0.0.1:38118".into());
    let saved = engine
        .storage
        .call(false, move |s| {
            s.save_sample_upload_settings(next, old.settings_revision)
        })
        .unwrap();
    assert_eq!(saved.origin.as_deref(), Some("http://127.0.0.1:38118"));
    assert_eq!(
        engine
            .storage
            .call(true, |s| s.sample_upload_bindings())
            .unwrap(),
        sources
    );
    resume_tx.send(()).unwrap();
    assert_eq!(
        tick.join().unwrap().unwrap_err(),
        "source_confirmation_changed"
    );
    assert!(posted_rx.recv_timeout(Duration::from_millis(100)).is_err());
    let row = engine
        .storage
        .call(true, |s| {
            s.runtime
                .query_row(
                    "SELECT state,attempt,origin,body,body_sha FROM sample_uploads LIMIT 1",
                    [],
                    |r| {
                        Ok((
                            r.get::<_, String>(0)?,
                            r.get::<_, u32>(1)?,
                            r.get::<_, String>(2)?,
                            r.get::<_, String>(3)?,
                            r.get::<_, String>(4)?,
                        ))
                    },
                )
                .map_err(crate::infrastructure::local_store::sql_error)
        })
        .unwrap();
    assert_eq!(
        (row.0.as_str(), row.1, row.2.as_str()),
        ("prepared", 0, old_target.as_str())
    );
    assert_eq!(crate::domain::facts_canonical::sha(row.3.as_bytes()), row.4);
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn pending_save_that_later_fails_remains_paused_until_explicit_resume() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct NoNetwork;
    impl Transport for NoNetwork {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("no samples in fixture")
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    let saved = engine
        .save_sample_upload_settings(settings, revision)
        .unwrap();
    let sources = engine
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    engine
        .set_delivery_using_checked(
            "start",
            Some((saved.settings_revision.clone(), sources.clone())),
            || Ok(Arc::new(NoNetwork)),
        )
        .unwrap();
    let (queue_tx, queue_rx) = mpsc::channel();
    let (ready_tx, ready_rx) = mpsc::channel();
    let (release_tx, release_rx) = mpsc::channel();
    let other = engine.clone();
    let blocker = std::thread::spawn(move || {
        queue_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        other.storage.call(false, move |_| {
            ready_tx.send(()).unwrap();
            release_rx.recv_timeout(Duration::from_secs(20)).unwrap();
            Ok(())
        })
    });
    let mut invalid = saved.clone();
    invalid.bindings[0].instance_id = " leading-space".into();
    assert_eq!(
        engine
            .save_sample_upload_settings_after_lock(
                invalid,
                saved.settings_revision.clone(),
                || {
                    queue_tx.send(()).unwrap();
                    ready_rx.recv_timeout(Duration::from_secs(5)).unwrap();
                }
            )
            .unwrap_err(),
        "storage_pending"
    );
    assert!(!engine.delivery.lock().unwrap().running);
    release_tx.send(()).unwrap();
    assert_eq!(blocker.join().unwrap().unwrap_err(), "storage_pending");
    let unchanged = engine
        .storage
        .call(false, |s| s.sample_upload_settings())
        .unwrap();
    assert_eq!(unchanged.settings_revision, saved.settings_revision);
    assert_eq!(unchanged.bindings, saved.bindings);
    assert_eq!(unchanged.origin, saved.origin);
    assert_eq!(engine.delivery_snapshot().unwrap()["running"], false);
    assert_eq!(
        engine
            .set_delivery("resume", Some(unchanged.settings_revision), Some(sources))
            .unwrap()["running"],
        true
    );
    engine.set_delivery("pause", None, None).unwrap();
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn startup_delivery_respects_plc_switches_and_reliable_receipts() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{
            add_v4_cycle_for, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::{Duration, Instant},
    };
    struct Ack(mpsc::Sender<(String, String)>);
    impl Transport for Ack {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, body: &str) -> Result<Response, String> {
            let value: Value = serde_json::from_str(body).unwrap();
            self.0
                .send((
                    value["sampleId"].as_str().unwrap().into(),
                    value["plcId"].as_str().unwrap().into(),
                ))
                .unwrap();
            Ok(Response { status:200, media_type:"application/json".into(), retry_after:None, body:json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":value["instanceId"],"sampleId":value["sampleId"],"status":"committed","outcome":"created"}}).to_string().into_bytes() })
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    engine
        .storage
        .call(false, |s| add_v4_cycle_for(s, 1))
        .unwrap();
    let mut settings = engine.sample_upload_settings().unwrap();
    let second = settings.bindings[1].local_plc_id.clone();
    let first_remote = settings.bindings[0].plc_id.clone();
    let second_remote = settings.bindings[1].plc_id.clone();
    settings.origin = Some("http://127.0.0.1:38117".into());
    settings.disabled_local_plcs.push(second);
    let rev = settings.settings_revision.clone();
    let saved = engine.save_sample_upload_settings(settings, rev).unwrap();
    let (tx, rx) = mpsc::channel();
    engine
        .set_delivery_with_authority(
            "start",
            None,
            || Ok(Arc::new(Ack(tx.clone()))),
            || {},
            false,
        )
        .unwrap();
    let a = rx.recv_timeout(Duration::from_secs(4)).unwrap();
    let b = rx.recv_timeout(Duration::from_secs(4)).unwrap();
    assert_ne!(a.0, b.0);
    assert_eq!(a.1, first_remote);
    assert_eq!(b.1, first_remote);
    let deadline = Instant::now() + Duration::from_secs(3);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 2 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    engine.set_delivery("pause", None, None).unwrap();
    assert!(rx.recv_timeout(Duration::from_millis(150)).is_err());
    let mut enabled = saved.clone();
    enabled.disabled_local_plcs.clear();
    engine
        .save_sample_upload_settings(enabled, saved.settings_revision)
        .unwrap();
    engine
        .set_delivery_with_authority("start", None, || Ok(Arc::new(Ack(tx))), || {}, false)
        .unwrap();
    let c = rx.recv_timeout(Duration::from_secs(7)).unwrap();
    let d = rx.recv_timeout(Duration::from_secs(7)).unwrap();
    assert_ne!(c.0, d.0);
    assert_eq!(c.1, second_remote);
    assert_eq!(d.1, second_remote);
    let deadline = Instant::now() + Duration::from_secs(3);
    while engine.delivery_snapshot().unwrap()["acknowledged"] != 4 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    engine.set_delivery("pause", None, None).unwrap();
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn startup_delivery_does_not_clear_blocks_or_retarget_prepared_samples() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        infrastructure::local_store::sample_upload_tests::{sealed_v4_fixture, seed_v4_fixture},
        services::local_supervisor::LocalEngine,
    };
    use std::{
        sync::{mpsc, Arc},
        time::Duration,
    };
    struct NoPost(mpsc::Sender<()>);
    impl Transport for NoPost {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, _: &str) -> Result<Response, String> {
            self.0.send(()).unwrap();
            Err("unexpected_dispatch".into())
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let engine = LocalEngine::open(Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    })
    .unwrap();
    let mut old = engine.sample_upload_settings().unwrap();
    old.origin = Some("http://127.0.0.1:38117".into());
    let rev = old.settings_revision.clone();
    let old = engine.save_sample_upload_settings(old, rev).unwrap();
    let target = old.target().unwrap().unwrap();
    let frozen = engine
        .storage
        .call(false, move |s| {
            let bindings = s.sample_upload_bindings()?;
            s.next_sample_upload(&target, &bindings, false)?
                .ok_or("no_sample".into())
        })
        .unwrap();
    let mut next = old.clone();
    next.origin = Some("http://127.0.0.1:38118".into());
    let next = engine
        .save_sample_upload_settings(next, old.settings_revision)
        .unwrap();
    let new_target = next.target().unwrap().unwrap();
    let blocked = frozen.clone();
    let blocked_target = new_target.clone();
    engine.storage.call(false,move |s| { s.runtime.execute("INSERT INTO sample_upload_source_blocks(origin,instance_id,plc_id,source_generation,reason) VALUES(?1,?2,?3,?4,'scope_rejected')",rusqlite::params![blocked_target,blocked.instance_id,blocked.plc_id,blocked.source_generation]).map_err(crate::infrastructure::local_store::sql_error)?; Ok(()) }).unwrap();
    let (tx, rx) = mpsc::channel();
    engine
        .set_delivery_with_authority("start", None, || Ok(Arc::new(NoPost(tx))), || {}, false)
        .unwrap();
    assert_eq!(
        engine
            .startup_errors
            .lock()
            .unwrap()
            .get("report")
            .map(String::as_str),
        Some("startup_delivery_needs_review")
    );
    assert!(rx.recv_timeout(Duration::from_millis(350)).is_err());
    let sample = frozen.clone();
    let (origin, body, attempt, blocks) = engine
        .storage
        .call(true, move |s| {
            let (origin, body, attempt): (String, String, u32) = s
                .runtime
                .query_row(
                    "SELECT origin,body,attempt FROM sample_uploads WHERE sample_id=?1",
                    [sample.sample_id],
                    |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
                )
                .map_err(crate::infrastructure::local_store::sql_error)?;
            let blocks: i64 = s
                .runtime
                .query_row(
                    "SELECT count(*) FROM sample_upload_source_blocks",
                    [],
                    |r| r.get(0),
                )
                .map_err(crate::infrastructure::local_store::sql_error)?;
            Ok((origin, body, attempt, blocks))
        })
        .unwrap();
    assert_eq!(
        (origin, body, attempt, blocks),
        (frozen.origin, frozen.body, 0, 1)
    );
    engine.set_delivery("pause", None, None).unwrap();
    engine.shutdown();
    drop(engine);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn startup_delivery_native_open_picks_up_newly_bound_plc() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        domain::local_runtime::StartupSettings,
        infrastructure::local_store::sample_upload_tests::{
            add_v4_cycle_for, captured_v4_cycle_for, sealed_v4_fixture, seed_v4_fixture,
        },
        services::local_recovery,
    };
    use std::{
        sync::{mpsc, Arc},
        time::{Duration, Instant},
    };
    struct Ack(mpsc::Sender<(String, String)>);
    impl Transport for Ack {
        fn post(&self, _: &str, _: &str) -> Result<Response, String> {
            panic!("v1 forbidden")
        }
        fn post_sample(&self, _: &str, body: &str) -> Result<Response, String> {
            let value: Value = serde_json::from_str(body).unwrap();
            self.0
                .send((
                    value["sampleId"].as_str().unwrap().into(),
                    value["plcId"].as_str().unwrap().into(),
                ))
                .unwrap();
            Ok(Response {status:200,media_type:"application/json".into(),retry_after:None,body:json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":value["instanceId"],"sampleId":value["sampleId"],"status":"committed","outcome":"created"}}).to_string().into_bytes()})
        }
    }
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let b = Bootstrap {
        mode: "local_sqlite".into(),
        profile: profile.clone(),
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    };
    let e = crate::services::local_supervisor::LocalEngine::open(b.clone()).unwrap();
    let mut settings = e.sample_upload_settings().unwrap();
    let config = e.configuration().unwrap().draft;
    let first_local = &config.plcs[0].id;
    let second_local = &config.plcs[1].id;
    let second = settings
        .bindings
        .iter()
        .find(|b| &b.local_plc_id == second_local)
        .unwrap()
        .clone();
    let first = settings
        .bindings
        .iter()
        .find(|b| &b.local_plc_id == first_local)
        .unwrap()
        .plc_id
        .clone();
    settings.bindings.retain(|b| &b.local_plc_id == first_local);
    settings.origin = Some("http://127.0.0.1:38117".into());
    let rev = settings.settings_revision.clone();
    e.save_sample_upload_settings(settings, rev).unwrap();
    e.storage.call(false, |s| add_v4_cycle_for(s, 0)).unwrap();
    e.save_startup_settings(StartupSettings {
        schema_version: 1,
        auto_collect: false,
        auto_report: true,
    })
    .unwrap();
    let (tx, rx) = mpsc::channel();
    super::startup_test_transport(&profile, Some(Arc::new(Ack(tx))));
    e.shutdown();
    drop(e);
    let e = local_recovery::open(b.clone()).unwrap();
    let a = rx.recv_timeout(Duration::from_secs(4)).unwrap();
    let c = rx.recv_timeout(Duration::from_secs(4)).unwrap();
    assert_ne!(a.0, c.0);
    assert_eq!(a.1, first);
    assert_eq!(c.1, first);
    let deadline = Instant::now() + Duration::from_secs(3);
    while e.delivery_snapshot().unwrap()["acknowledged"] != 2 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    e.set_delivery("pause", None, None).unwrap();
    let mut settings = e.sample_upload_settings().unwrap();
    settings.bindings.push(second.clone());
    let rev = settings.settings_revision.clone();
    e.save_sample_upload_settings(settings, rev).unwrap();
    e.storage
        .call(false, |s| {
            let (cycle, identity) = captured_v4_cycle_for(s, 1)?;
            s.commit_cycle_with_reporting(cycle, identity).map(|_| ())
        })
        .unwrap();
    assert_eq!(
        e.startup_settings().unwrap()["settings"]["autoReport"],
        true
    );
    e.shutdown();
    drop(e);
    let e = local_recovery::open(b).unwrap();
    let a = rx.recv_timeout(Duration::from_secs(4)).unwrap();
    let c = rx.recv_timeout(Duration::from_secs(4)).unwrap();
    assert_ne!(a.0, c.0);
    assert_eq!(a.1, second.plc_id);
    assert_eq!(c.1, second.plc_id);
    let deadline = Instant::now() + Duration::from_secs(3);
    while e.delivery_snapshot().unwrap()["acknowledged"] != 4 {
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    e.shutdown();
    drop(e);
    super::startup_test_transport(&profile, None);
    std::fs::remove_dir_all(profile).unwrap();
}
