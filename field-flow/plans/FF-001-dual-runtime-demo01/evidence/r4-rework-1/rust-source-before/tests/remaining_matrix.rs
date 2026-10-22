//! 文件：tests/remaining_matrix.rs；INT逐值独立读回、过期队列、审计故障、容量轮转与ref维护。
#![cfg(feature = "test-fixture")]
mod support;
use field_flow::{
    domain::{now_ms, Clock},
    fixture::Fixture,
    infrastructure::state,
    services::execution::Execution,
};
use serde_json::{json, Value};
use std::{path::Path, sync::atomic::Ordering, time::Duration};
use support::*;
use tokio::time::sleep;
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn additional_protocol_contracts() {
    let mut fixture = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    let mut proof = Vec::new();
    for value in [-32768i16, -1, 0, 42, 32767] {
        let run = Run::new("int-readback", "execute", &c);
        run.ready().await;
        fixture.command(&format!("int-{}", value), json!(value));
        run.iteration(&c).await.unwrap();
        run.close(true).await;
        let b = readback(0);
        assert_eq!(&b[..2], &value.to_be_bytes());
        assert!(b[2..].iter().all(|v| *v == 0xa5));
        proof.push(json!({"value":value,"bytes":b}));
    }
    // Native block boundary rejects a validly formed request outside the actual registered DB.
    let run = Run::new("block-boundary", "execute", &c);
    run.ready().await;
    assert!(run.rt.owners["plc_demo"]
        .read("outside", 1, 15)
        .await
        .is_err());
    run.close(false).await;
    // Same identity cannot refresh time or substitute physical target.
    let run = Run::new("immutable", "execute", &c);
    run.ready().await;
    let i = intent(&c, "immutable", 42);
    run.state.admit(i.clone()).await.unwrap();
    for n in 0..3 {
        let mut other = i.clone();
        match n {
            0 => other.issued_at_ms += 1,
            1 => other.expires_at_ms += 1,
            _ => other.target.offset = 2,
        }
        assert_eq!(
            run.state.admit(other).await.unwrap_err(),
            "identity_conflict"
        );
    }
    run.close(true).await;
    // A queued write expires while another independent read is blocked; no permit can later execute.
    let run = Run::new("queued-expiry", "execute", &c);
    run.ready().await;
    fixture.fault("split");
    let owner = run.rt.owners["plc_demo"].clone();
    let reader = tokio::spawn(async move { owner.read("slow-read", 1, 0).await });
    sleep(Duration::from_millis(50)).await;
    let mut i = intent(&c, "short-ttl", 42);
    i.expires_at_ms = now_ms() + 700;
    let before = fixture.snapshot()["writes"].as_u64().unwrap();
    let result = Execution {
        owner: &run.rt.owners["plc_demo"],
        state: &run.state,
        stop: &run.rt.stop,
    }
    .apply(i.clone(), &mut Clock::default())
    .await;
    assert_eq!(result.unwrap_err(), "expired");
    assert_eq!(run.state.command_status(i).await.unwrap(), "expired");
    assert!(reader.await.unwrap().is_err());
    fixture.fault("");
    run.close(false).await;
    assert_eq!(fixture.snapshot()["writes"].as_u64().unwrap(), before);
    // Real rotation with lowered logical capacity retains all command identities and state events.
    let run = Run::new("capacity", "execute", &c);
    run.ready().await;
    run.state.test_limits(10, 100, 2048).await.unwrap();
    for n in 0..10 {
        fixture.command(&format!("cap-{n}"), json!(42));
        run.iteration(&c).await.unwrap();
    }
    fixture.command("cap-11", json!(42));
    assert_eq!(run.iteration(&c).await.unwrap_err(), "capacity_paused");
    let dir = run.close(true).await;
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["confirmed"], 10);
    let logs = std::fs::read_dir(&dir)
        .unwrap()
        .filter_map(|p| p.ok())
        .filter(|p| p.file_name().to_string_lossy().starts_with("runtime.jsonl"))
        .collect::<Vec<_>>();
    assert!(logs.len() > 1 && logs.len() <= 5);
    for log in logs {
        assert!(log.metadata().unwrap().len() <= 2048);
        for line in std::fs::read_to_string(log.path()).unwrap().lines() {
            serde_json::from_str::<Value>(line).unwrap();
        }
    }
    // Audit failure closes the same physical start gate before already queued permits can run; reads continue.
    std::env::set_var("FF_TEST_CHILD_BARRIER", "1");
    let run = Run::new("audit-queued", "execute", &c);
    run.ready().await;
    std::env::remove_var("FF_TEST_CHILD_BARRIER");
    let before = fixture.snapshot()["writes"].as_u64().unwrap();
    let mut jobs = Vec::new();
    for n in 0..2 {
        let owner = run.rt.owners["plc_demo"].clone();
        let state = run.state.clone();
        let stop = run.rt.stop.clone();
        let i = intent(&c, &format!("audit-{n}"), 42);
        jobs.push(tokio::spawn(async move {
            Execution {
                owner: &owner,
                state: &state,
                stop: &stop,
            }
            .apply(i, &mut Clock::default())
            .await
        }));
        sleep(Duration::from_millis(50)).await;
    }
    assert_eq!(run.rt.owners["plc_demo"].health().queue_depth, 1);
    assert_eq!(
        run.state.test_fault("audit").await.unwrap_err(),
        "audit_persist"
    );
    for job in jobs {
        assert!(job.await.unwrap().is_err());
    }
    assert!(!run.state.healthy.load(Ordering::Acquire));
    run.rt.owners["plc_demo"]
        .read("read-after-audit", 1, 0)
        .await
        .unwrap();
    let dir = run.close(false).await;
    assert_eq!(fixture.snapshot()["writes"].as_u64().unwrap(), before);
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["canceled"], 2);
    // Counter rotates before ref reuse, preserving confirmed identity across child generation change.
    std::env::set_var("FF_TEST_REF_NEAR_END", "1");
    let run = Run::new("ref-epoch", "execute", &c);
    run.ready().await;
    std::env::remove_var("FF_TEST_REF_NEAR_END");
    let old = run.rt.owners["plc_demo"].health();
    fixture.command("near-end", json!(42));
    run.iteration(&c).await.unwrap();
    eventually(|| {
        run.rt.owners["plc_demo"].health().generation > old.generation
            && run.rt.owners["plc_demo"].health().state == "ready"
    })
    .await;
    let new = run.rt.owners["plc_demo"].health();
    assert_ne!(old.pid, new.pid);
    let before = fixture.snapshot()["writes"].as_u64().unwrap();
    for _ in 0..10 {
        run.iteration(&c).await.unwrap();
    }
    assert_eq!(fixture.snapshot()["writes"].as_u64().unwrap(), before);
    run.close(true).await;
    fixture.close().unwrap();
    println!(
        "{}",
        json!({"ac":"AC03/04/05/12/15","int_readbacks":proof,"queue_expired_zero_write":true,"audit_queued_zero_write":true,"capacity_retains_confirmed":10,"ref_epoch_maintenance":true})
    );
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn server_absent_then_recovers() {
    let c = config();
    let mut run = Run::new("server-absent", "execute", &c);
    run.rt.launch_flows(&c).unwrap();
    sleep(Duration::from_millis(750)).await;
    assert_ne!(run.rt.owners["plc_demo"].health().state, "ready");
    assert!(run.rt.flows.lock().unwrap()["demo01"].iterations >= 1);
    let mut fixture = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    run.ready().await;
    run.rt.owners["plc_demo"]
        .read("after-start", 1, 0)
        .await
        .unwrap();
    eventually(|| run.rt.flows.lock().unwrap()["demo01"].state == "running").await;
    run.close(false).await;
    fixture.close().unwrap();
    let occupant = std::net::TcpListener::bind("127.0.0.1:31102").unwrap();
    assert!(Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).is_err());
    assert_eq!(occupant.local_addr().unwrap().port(), 31102);
    drop(occupant);
    println!(
        "{}",
        json!({"ac":"AC08/AC13","server_initially_absent":true,"recovered_read":true,"independent_http_flow_recovered":true,"port_conflict_preserves_occupant":true})
    );
}
