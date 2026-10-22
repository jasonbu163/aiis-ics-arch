//! 文件：tests/confirmed_audit.rs；真实confirmed后持久sink故障不降级，原身份重启十轮不重发。
#![cfg(feature = "test-fixture")]
mod support;
use field_flow::{fixture::Fixture, infrastructure::state};
use serde_json::json;
use std::path::Path;
use support::*;
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn confirmed_then_sink_failure_retains_progress() {
    let mut fixture = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    let run = Run::new("confirmed-then-sink", "execute", &c);
    run.ready().await;
    fixture.command("confirmed-before-sink", json!(42));
    run.iteration(&c).await.unwrap();
    assert_eq!(state::inspect(&run.dir).unwrap()["counts"]["confirmed"], 1);
    let writes = fixture.snapshot()["writes"].as_u64().unwrap();
    assert_eq!(writes, 1);
    assert_eq!(
        run.state.test_fault("audit").await.unwrap_err(),
        "audit_persist"
    );
    assert_eq!(run.iteration(&c).await.unwrap_err(), "audit_unhealthy");
    let dir = run.close(false).await;
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["confirmed"], 1);
    let restart = Run::open(dir.clone(), "execute", &c);
    restart.ready().await;
    for _ in 0..10 {
        restart.iteration(&c).await.unwrap();
    }
    restart.close(true).await;
    assert_eq!(state::inspect(&dir).unwrap()["counts"]["confirmed"], 1);
    assert_eq!(fixture.snapshot()["writes"].as_u64().unwrap(), writes);
    let memory = readback(0);
    assert_eq!(&memory[..2], &[0, 42]);
    fixture.close().unwrap();
    println!(
        "{}",
        json!({"ac":"AC10/AC12","case":"confirmed-then-sink-failure","store":dir,"actual_writes":1,"confirmed":1,"repeat_after_restart":10,"ports_rebound":[31102,31103,31880]})
    );
}
