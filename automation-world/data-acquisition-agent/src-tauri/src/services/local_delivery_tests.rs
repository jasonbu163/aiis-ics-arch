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
    fn get(&self, _: &str, _: &str, _: &[(String, String)]) -> Result<Response, String> {
        Err("synthetic_get_cannot_ack".into())
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

#[test]
fn actual_engine_single_worker_pause_inflight_ack_resume_shutdown_and_stopped_reopen() {
    use crate::{
        config::local_bootstrap::Bootstrap,
        domain::{facts_wire::Batch, local_configuration::id},
        infrastructure::local_store::delivery::Frozen,
        services::local_supervisor::LocalEngine,
    };
    use std::sync::{
        atomic::{AtomicUsize, Ordering},
        mpsc, Arc, Mutex,
    };
    use std::time::{Duration, Instant};
    struct Controlled {
        calls: AtomicUsize,
        entered: mpsc::SyncSender<usize>,
        release: Mutex<mpsc::Receiver<()>>,
    }
    impl Transport for Controlled {
        fn post(&self, origin: &str, body: &str) -> Result<Response, String> {
            let number = self.calls.fetch_add(1, Ordering::SeqCst) + 1;
            self.entered.send(number).map_err(|_| "synthetic_channel")?;
            self.release
                .lock()
                .unwrap()
                .recv_timeout(Duration::from_secs(3))
                .map_err(|_| "synthetic_deadline")?;
            let batch: Batch = serde_json::from_value(pf::parse(body.as_bytes(), 4 * 1024 * 1024)?)
                .map_err(|_| "synthetic_request")?;
            let f = Frozen {
                batch,
                body: body.into(),
                body_sha: pf::sha(body.as_bytes()),
                origin: origin.into(),
                target_id: "synthetic-target".into(),
                depth: 0,
            };
            Ok(Response {
                status: 200,
                media_type: "application/json".into(),
                retry_after: None,
                body: serde_json::to_vec(&receipt(&f)).unwrap(),
            })
        }
        fn get(&self, _: &str, _: &str, _: &[(String, String)]) -> Result<Response, String> {
            panic!("no GET in lifecycle substitute")
        }
    }
    let root = std::env::temp_dir().canonicalize().unwrap();
    assert!(root.to_string_lossy().contains("daa-008-r1-a-"));
    let profile = root.join(format!("engine-{}", id()));
    assert!(!profile.exists());
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
    assert!(engine.delivery.lock().unwrap().join.is_none());
    assert!(engine.delivery_available().unwrap());
    engine
        .storage
        .call(false, |s| {
            let b = seed(s, 1);
            adopt(s, &b);
            let old = s.delivery_settings()?;
            let mut settings = old.clone();
            settings.interval_seconds = 1;
            s.save_delivery_settings(settings, old.settings_revision)?;
            Ok(())
        })
        .unwrap();
    let (entered_tx, entered_rx) = mpsc::sync_channel(2);
    let (release_tx, release_rx) = mpsc::sync_channel(2);
    let transport = Arc::new(Controlled {
        calls: AtomicUsize::new(0),
        entered: entered_tx,
        release: Mutex::new(release_rx),
    });
    let substitute = transport.clone();
    engine
        .set_delivery_using("start", move || Ok(substitute))
        .unwrap();
    assert_eq!(entered_rx.recv_timeout(Duration::from_secs(2)).unwrap(), 1);
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
        .set_delivery_using("start", || panic!("second worker/client forbidden"))
        .unwrap();
    engine
        .set_delivery_using("resume", || panic!("second worker/client forbidden"))
        .unwrap();
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
    engine
        .set_delivery_using("pause", || panic!("pause cannot construct transport"))
        .unwrap();
    engine
        .storage
        .call(false, |s| {
            seed(s, 2);
            Ok(())
        })
        .unwrap();
    release_tx.send(()).unwrap();
    let deadline = Instant::now() + Duration::from_secs(2);
    loop {
        if engine.delivery_snapshot().unwrap()["acknowledged"] == 1 {
            break;
        }
        assert!(Instant::now() < deadline);
        std::thread::sleep(Duration::from_millis(10));
    }
    std::thread::sleep(Duration::from_millis(1100));
    assert_eq!(transport.calls.load(Ordering::SeqCst), 1);
    assert_eq!(engine.delivery_snapshot().unwrap()["pending"], 1);
    engine
        .set_delivery_using("resume", || panic!("resume must reuse worker/client"))
        .unwrap();
    assert_eq!(entered_rx.recv_timeout(Duration::from_secs(2)).unwrap(), 2);
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
    let closing = engine.clone();
    let shutdown = std::thread::spawn(move || closing.shutdown());
    release_tx.send(()).unwrap();
    shutdown.join().unwrap();
    assert!(engine.delivery.lock().unwrap().join.is_none());
    assert_eq!(transport.calls.load(Ordering::SeqCst), 2);
    drop(engine);
    let reopened = LocalEngine::open(boot).unwrap();
    assert_eq!(reopened.delivery_snapshot().unwrap()["running"], false);
    assert_eq!(reopened.delivery_snapshot().unwrap()["acknowledged"], 2);
    assert!(reopened.delivery.lock().unwrap().join.is_none());
    reopened.shutdown();
    drop(reopened);
    let lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile).unwrap();
    drop(lock);
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
