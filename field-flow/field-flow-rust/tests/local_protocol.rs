//! 文件：tests/local_protocol.rs；真实HTTP/S7、唯一会话、故障和恢复矩阵，逐版串行。
#![cfg(feature = "test-fixture")]
mod support;
use field_flow::{
    domain::{now_ms, Clock},
    fixture::Fixture,
    infrastructure::state,
};
use serde_json::{json, Value};
use std::time::Duration;
use support::*;
use tokio::time::{sleep, Instant};
fn total(f: &Fixture, key: &str) -> u64 {
    f.snapshot()[key].as_u64().unwrap()
}
fn report(ac: &str, case: &str, value: Value) {
    println!(
        "{}",
        json!({"ac":ac,"case":case,"result":"dev_check_passed","evidence":value})
    );
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn approved_loopback_matrix() {
    let mut fixture =
        Fixture::start(std::path::Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    // AC03/05: real HTTP->typed S7 write; each new identity, immutable repeats then parent-store reopen.
    let run = Run::new("int", "execute", &c);
    run.ready().await;
    let generation = run.rt.owners["plc_demo"].health();
    for (n, value) in [-32768, -1, 0, 42, 32767].into_iter().enumerate() {
        fixture.command(&format!("int-{n}"), json!(value));
        for _ in 0..10 {
            run.iteration(&c).await.unwrap();
        }
        assert_eq!(total(&fixture, "writes"), n as u64 + 1);
    }
    assert_eq!(total(&fixture, "sessions"), 1);
    let dir = run.close(true).await;
    let bytes = readback(0);
    assert_eq!(&bytes[..2], &32767i16.to_be_bytes());
    assert!(bytes[2..].iter().all(|v| *v == 0xa5));
    let run = Run::open(dir.clone(), "execute", &c);
    run.ready().await;
    for _ in 0..10 {
        run.iteration(&c).await.unwrap();
    }
    assert_eq!(total(&fixture, "writes"), 5);
    let original = state::inspect(&dir).unwrap();
    fixture.command("int-4", json!(1));
    assert_eq!(run.iteration(&c).await.unwrap_err(), "identity_conflict");
    assert_eq!(state::inspect(&dir).unwrap(), original);
    run.close(true).await;
    report(
        "AC03/AC05",
        "INT-and-ten-repeats-restart",
        json!({"writes":5,"initial_pid":generation.pid,"generation":generation.generation,"readback":bytes}),
    );
    // AC04: invalid sources and types, never substitute last good value.
    let run = Run::new("reject", "execute", &c);
    run.ready().await;
    let baseline = total(&fixture, "writes");
    let mut rejected = 0;
    for value in [
        json!(32768),
        json!(-32769),
        json!(1.0),
        json!(true),
        json!("42"),
    ] {
        fixture.command(&format!("bad-{rejected}"), value);
        assert!(run.iteration(&c).await.is_err());
        rejected += 1;
    }
    for (issued, expires) in [
        (now_ms() - 20000, now_ms() + 10000),
        (now_ms() + 5000, now_ms() + 10000),
        (now_ms(), now_ms() + 60001),
        (now_ms() - 2000, now_ms() - 1000),
    ] {
        fixture.body(json!({"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"time","value":42,"issued_at_ms":issued,"expires_at_ms":expires}));
        assert!(run.iteration(&c).await.is_err());
        rejected += 1;
    }
    fixture.behavior.lock().unwrap().status = 503;
    assert_eq!(run.iteration(&c).await.unwrap_err(), "http_status");
    fixture.behavior.lock().unwrap().status = 200;
    fixture.behavior.lock().unwrap().body = vec![b'x'; 4097];
    assert_eq!(run.iteration(&c).await.unwrap_err(), "input_body_size");
    fixture.behavior.lock().unwrap().body = b"{bad".to_vec();
    assert_eq!(run.iteration(&c).await.unwrap_err(), "input_schema");
    fixture.body(json!({"schema_version":1,"source_id":"wrong","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}));
    assert!(run.iteration(&c).await.is_err());
    fixture.body(json!({"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}));
    run.iteration(&c).await.unwrap();
    let mut clock = Clock::default();
    assert_eq!(clock.check(now_ms() - 2000).unwrap_err(), "clock_invalid");
    assert_eq!(total(&fixture, "writes"), baseline);
    run.close(true).await;
    report(
        "AC04",
        "invalid-idle-body-clock",
        json!({"rejected":rejected,"new_writes":0}),
    );
    // AC06: independent reads return independent identities through one persistent PID/session.
    let start_sessions = total(&fixture, "sessions");
    let run = Run::new("concurrent", "execute", &c);
    run.ready().await;
    let h = run.rt.owners["plc_demo"].health();
    let mut handles = Vec::new();
    for n in 0..3 {
        let owner = run.rt.owners["plc_demo"].clone();
        handles.push(tokio::spawn(async move {
            let mut ids = std::collections::HashSet::new();
            for _ in 0..20 {
                let s = owner.read(&format!("reader{n}"), 1, 0).await.unwrap();
                assert_eq!(s.flow_id, format!("reader{n}"));
                assert!(ids.insert(s.request_id));
                assert_eq!(s.pid, h.pid.unwrap());
                assert_eq!(s.generation, h.generation);
            }
            ids.len()
        }));
    }
    for handle in handles {
        assert_eq!(handle.await.unwrap(), 20)
    }
    assert_eq!(total(&fixture, "sessions") - start_sessions, 1);
    run.close(true).await;
    report(
        "AC06",
        "three-independent-readers",
        json!({"samples_per_flow":20,"sessions":1,"pid":h.pid}),
    );
    // AC07: one 1200ms HTTP iteration does not reserve PLC owner position.
    let mut run = Run::new("slow-http", "execute", &c);
    fixture.behavior.lock().unwrap().delay_ms = 1200;
    run.rt.launch_flows(&c).unwrap();
    run.ready().await;
    let owner = run.rt.owners["plc_demo"].clone();
    let end = Instant::now() + Duration::from_secs(8);
    let mut times = Vec::new();
    while Instant::now() < end {
        owner.read("fast", 1, 0).await.unwrap();
        times.push(Instant::now());
        sleep(Duration::from_millis(100)).await;
    }
    let max = times
        .windows(2)
        .map(|w| w[1].duration_since(w[0]).as_millis())
        .max()
        .unwrap();
    assert!(times.len() >= 20 && max <= 500);
    assert!(run.rt.flows.lock().unwrap()["demo01"].in_flight <= 1);
    drop(owner);
    run.close(true).await;
    fixture.behavior.lock().unwrap().delay_ms = 0;
    report(
        "AC07",
        "slow-GET-independent-read",
        json!({"samples":times.len(),"max_gap_ms":max}),
    );
    // AC11: GET observations create simulated only; mode mismatch never opens.
    let run = Run::new("dry", "dry_run", &c);
    run.ready().await;
    fixture.command("dry-1", json!(42));
    let before = total(&fixture, "writes");
    run.iteration(&c).await.unwrap();
    run.rt.owners["plc_demo"]
        .read("dry-read", 1, 0)
        .await
        .unwrap();
    let dir = run.close(true).await;
    assert_eq!(total(&fixture, "writes"), before);
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["simulated"], 1);
    assert!(state::State::open(&dir, "execute", &c.instance_id, "wrong").is_err());
    report(
        "AC11",
        "separate-dry-store",
        json!({"new_writes":0,"simulated":1}),
    );
    // AC08/09: matching ACK retained after real application, whole-call expiry, actual child reap, target blocked.
    let run = Run::new("lost-ack", "execute", &c);
    run.ready().await;
    fixture.command("lost-1", json!(42));
    fixture.fault("hold_ack");
    let before = total(&fixture, "writes");
    let started = Instant::now();
    let error = run.iteration(&c).await.unwrap_err();
    let elapsed = started.elapsed().as_millis();
    assert!(error.starts_with("forced_driver_stop"));
    assert!(elapsed <= 5500);
    assert_eq!(total(&fixture, "writes"), before + 1);
    fixture.fault("");
    let dir = run.close(false).await;
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["unknown"], 1);
    let run = Run::open(dir.clone(), "execute", &c);
    run.ready().await;
    for _ in 0..10 {
        assert_eq!(run.iteration(&c).await.unwrap_err(), "target_unknown");
    }
    fixture.command("new-bypass", json!(7));
    assert_eq!(run.iteration(&c).await.unwrap_err(), "target_unknown");
    run.rt.owners["plc_demo"]
        .read("unrelated", 1, 0)
        .await
        .unwrap();
    run.close(true).await;
    assert_eq!(total(&fixture, "writes"), before + 1);
    report(
        "AC08/AC09",
        "applied-ACK-lost-reap-unknown",
        json!({"elapsed_ms":elapsed,"error":error,"writes":1,"store":dir}),
    );
    fixture.close().unwrap();
    report(
        "AC13",
        "fixture-natural-exit-ports",
        json!({"ports":[31102,31103,31880],"snapshot":fixture.snapshot()}),
    );
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn fault_and_stop_matrix() {
    let mut fixture =
        Fixture::start(std::path::Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    // Supervisor deadlines include real child termination; native IO deliberately has longer phase timeouts.
    for fault in ["split", "slow", "stale"] {
        let run = Run::new(fault, "execute", &c);
        run.ready().await;
        let pid = run.rt.owners["plc_demo"].health().pid.unwrap();
        fixture.fault(fault);
        let start = Instant::now();
        let result = run.rt.owners["plc_demo"].read("fault-reader", 1, 0).await;
        let ms = start.elapsed().as_millis();
        assert!(result.is_err() && ms <= 5500);
        fixture.fault("");
        run.close(false).await;
        assert_eq!(unsafe { libc::kill(pid as i32, 0) }, -1);
        report(
            "AC08",
            fault,
            json!({"duration_ms":ms,"driver_pid":pid,"pid_gone":true,"result":result}),
        );
    }
    // Connect deadline includes spawn/IPC/real reap with a silent COTP transport.
    fixture.fault("silent_cotp");
    let mut small = c.clone();
    small.plcs[0].connect_timeout_ms = 500;
    small.plcs[0].ready_wait_ms = 500;
    let run = Run::new("silent-cotp", "execute", &small);
    let start = Instant::now();
    assert!(run.rt.owners["plc_demo"]
        .read("not-ready", 1, 0)
        .await
        .is_err());
    assert!(start.elapsed().as_millis() <= 1000);
    fixture.fault("");
    run.close(false).await;
    report(
        "AC08",
        "silent-COTP",
        json!({"connect_budget_ms":500,"result":"no_io_before_ready"}),
    );
    // Existing session lost; only owner recovers and does not replay commands.
    let run = Run::new("disconnect", "execute", &c);
    run.ready().await;
    fixture.disconnect();
    assert!(run.rt.owners["plc_demo"]
        .read("disconnect-reader", 1, 0)
        .await
        .is_err());
    eventually(|| {
        run.rt.owners["plc_demo"].health().generation >= 2
            && run.rt.owners["plc_demo"].health().state == "ready"
    })
    .await;
    run.rt.owners["plc_demo"]
        .read("recovered", 1, 0)
        .await
        .unwrap();
    run.close(false).await;
    // T1 replay uses the original source times; T2 recovery is conservatively unknown before connecting.
    let parent = root("t1");
    let dir = parent.join("state");
    state::init(&dir, "execute", &c.instance_id).unwrap();
    let i = intent(&c, "t1-original", 42);
    let (s, t) = state::State::open(&dir, "execute", &c.instance_id, "t1").unwrap();
    s.admit(i.clone()).await.unwrap();
    drop(s);
    t.join().await.unwrap();
    let run = Run::open(dir, "execute", &c);
    run.ready().await;
    field_flow::services::execution::Execution {
        owner: &run.rt.owners["plc_demo"],
        state: &run.state,
        stop: &run.rt.stop,
    }
    .apply(i.clone(), &mut Clock::default())
    .await
    .unwrap();
    let dir = run.close(true).await;
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["confirmed"], 1);
    let parent = root("t2");
    let dir = parent.join("state");
    state::init(&dir, "execute", &c.instance_id).unwrap();
    let i = intent(&c, "t2-original", 1);
    let (s, t) = state::State::open(&dir, "execute", &c.instance_id, "t2").unwrap();
    s.admit(i.clone()).await.unwrap();
    s.dispatch(i.clone(), "test-pre-permit".into())
        .await
        .unwrap();
    drop(s);
    t.join().await.unwrap();
    let run = Run::open(dir, "execute", &c);
    run.ready().await;
    assert_eq!(
        run.state.command_status(i.clone()).await.unwrap(),
        "unknown"
    );
    for alias in 0..4 {
        let mut other = i.clone();
        other.command_id = format!("bypass-{alias}");
        other.source_id = format!("alias-{alias}");
        other.flow_id = format!("alias-flow-{alias}");
        other.target.offset = if alias == 3 { 1 } else { 0 };
        assert_eq!(run.state.admit(other).await.unwrap_err(), "target_unknown");
    }
    run.close(true).await;
    report(
        "AC09",
        "T1-T2-recovery-and-physical-overlap",
        json!({"confirmed":1,"unknown":1,"alias_rejections":4}),
    );
    // ACK succeeds at protocol level but T3 fails: original in_flight is retained and next open makes unknown.
    let run = Run::new("t3-fail", "execute", &c);
    run.ready().await;
    run.state.test_fault("t3").await.unwrap();
    fixture.command("t3", json!(42));
    let before = total(&fixture, "writes");
    assert!(run.iteration(&c).await.is_err());
    let dir = run.close(false).await;
    let run = Run::open(dir, "execute", &c);
    run.ready().await;
    assert_eq!(run.iteration(&c).await.unwrap_err(), "target_unknown");
    assert_eq!(total(&fixture, "writes"), before + 1);
    run.close(true).await;
    report(
        "AC10",
        "ACK-then-T3-failure",
        json!({"actual_writes":1,"recovery":"unknown"}),
    );
    // Child invocation barrier + parent queued permit: stop must cancel both without any actual write.
    std::env::set_var("FF_TEST_CHILD_BARRIER", "1");
    let run = Run::new("queued-stop", "execute", &c);
    run.ready().await;
    std::env::remove_var("FF_TEST_CHILD_BARRIER");
    let mut jobs = Vec::new();
    let before = total(&fixture, "writes");
    for n in 0..2 {
        let i = intent(&c, &format!("queued-{n}"), 42);
        run.state.admit(i.clone()).await.unwrap();
        let owner = run.rt.owners["plc_demo"].clone();
        jobs.push(tokio::spawn(async move {
            owner
                .write(i, Instant::now() + Duration::from_secs(5))
                .await
        }));
        sleep(Duration::from_millis(50)).await;
    }
    assert_eq!(run.rt.owners["plc_demo"].health().queue_depth, 1);
    let start = Instant::now();
    let dir = run.close(true).await;
    for job in jobs {
        assert_eq!(job.await.unwrap().unwrap_err(), "canceled");
    }
    assert_eq!(total(&fixture, "writes"), before);
    assert!(start.elapsed().as_secs() < 15);
    report(
        "AC13",
        "child-precall-and-parent-queue-stop",
        json!({"actual_writes":0,"duration_ms":start.elapsed().as_millis(),"store":dir}),
    );
    fixture.close().unwrap();
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn stale_reference_probe() {
    let mut fixture =
        Fixture::start(std::path::Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    let run = Run::new("stale-reference-probe", "execute", &c);
    run.ready().await;
    let child = run.rt.owners["plc_demo"].health().pid.unwrap();
    fixture.fault("stale_once");
    let read = run.rt.owners["plc_demo"].read("stale-reader", 1, 0).await;
    fixture.command("stale-write-001", json!(42));
    let write = run.iteration(&c).await;
    let dir = run.close(true).await;
    fixture.fault("");
    let memory = readback(0);
    let store = state::inspect(&dir).unwrap();
    let snapshot = fixture.snapshot();
    let close = fixture.close();
    let evidence = json!({"task":"FF-001","revision":"r2","case":"unmatched-S7-PDU-reference","read_result":read,"write_iteration_result":write,"actual_writevar_count":snapshot["writes"],"applied_positive_ack_count":snapshot["applied"],"native_memory_readback_hex":memory.iter().map(|b|format!("{b:02x}")).collect::<String>(),"neighbor_bytes_preserved":memory[2..].iter().all(|b|*b==0xa5),"parent_store":store,"store_dir":dir,"child_pid":child,"child_pid_gone":unsafe{libc::kill(child as i32,0)}==-1,"fixture_natural_close":close,"released_ports":[31102,31103,31880],"protocol_trace":snapshot["trace"]});
    std::fs::write(
        dir.parent().unwrap().join("stale-reference-evidence.json"),
        serde_json::to_vec_pretty(&evidence).unwrap(),
    )
    .unwrap();
    println!("{}", evidence);
    assert!(
        evidence["write_iteration_result"].get("Err").is_some()
            && evidence["parent_store"]["counts"]["confirmed"]
                .as_u64()
                .unwrap_or(0)
                == 0,
        "T3 contract: unmatched WriteVar ACK must not confirm"
    );
}
