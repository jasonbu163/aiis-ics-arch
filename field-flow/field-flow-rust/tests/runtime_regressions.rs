//! 文件：tests/runtime_regressions.rs；QA1真实FIFO预算、queued/precall时钟与started统计回归。
#![cfg(feature = "test-fixture")]
#[allow(dead_code)]
mod support;
use field_flow::{
    domain::{now_ms, Clock},
    fixture::Fixture,
    infrastructure::state,
    services::execution::Execution,
};
use serde_json::{json, Value};
use std::{path::Path, time::Duration};
use support::*;
use tokio::time::{sleep, Instant};
fn logs(dir: &Path) -> usize {
    std::fs::read_to_string(dir.join("runtime.jsonl"))
        .unwrap()
        .lines()
        .filter(|s| {
            serde_json::from_str::<Value>(s)
                .ok()
                .is_some_and(|v| v["event"] == "driver_call_started")
        })
        .count()
}
async fn close(run: Run) -> Value {
    let pid = run.rt.owners["plc_demo"].health().pid;
    let result = run.rt.shutdown(15000).await;
    drop(run.state);
    run.task.join().await.unwrap();
    if let Some(pid) = pid {
        assert_eq!(unsafe { libc::kill(pid as i32, 0) }, -1);
    }
    json!({"shutdown":result,"driver_pid":pid,"driver_gone":true,"state_dir":run.dir,"state":state::inspect(&run.dir).unwrap()})
}
fn report(root: &Path, mut f: Fixture, result: Value) {
    let native = f.native_pid;
    let protocol = f.snapshot();
    f.close().unwrap();
    std::fs::write(root.join("report.json"),serde_json::to_vec_pretty(&json!({"result":result,"protocol":protocol,"native_pid":native,"native_exit":0,"fixture_joined":true,"ports_rebound":[31102,31103,31880]})).unwrap()).unwrap();
    println!(
        "{}",
        json!({"regression_evidence":root.join("report.json")})
    );
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn fifo_dispatch_io_budget_read_and_write() {
    let root = root("r4-rework-fifo");
    let f = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let mut c = config();
    c.plcs[0].io_timeout_ms = 1200;
    c.plcs[0].queue_wait_ms = 1000;
    c.validate().unwrap();
    let run = Run::new("r4-rework-fifo-state", "execute", &c);
    run.ready().await;
    let original = run.rt.owners["plc_demo"].health();
    f.fault("delay600");
    let o = run.rt.owners["plc_demo"].clone();
    let first = tokio::spawn(async move { o.read("read-first", 1, 0).await });
    eventually(|| f.snapshot()["reads"].as_u64().unwrap() >= 1).await;
    let start = Instant::now();
    let second = run.rt.owners["plc_demo"].read("read-second", 1, 0).await;
    let second_ms = start.elapsed().as_millis();
    let first = first.await.unwrap();
    let count = f.snapshot()["reads"].as_u64().unwrap();
    let o = run.rt.owners["plc_demo"].clone();
    let third = tokio::spawn(async move { o.read("before-write", 1, 0).await });
    eventually(|| f.snapshot()["reads"].as_u64().unwrap() > count).await;
    let start = Instant::now();
    let write = Execution {
        owner: &run.rt.owners["plc_demo"],
        state: &run.state,
        stop: &run.rt.stop,
    }
    .apply(intent(&c, "fifo-write", 42), &mut Clock::default())
    .await;
    let write_ms = start.elapsed().as_millis();
    let third = third.await.unwrap();
    let end_health = run.rt.owners["plc_demo"].health();
    let good = first.is_ok()
        && second.is_ok()
        && third.is_ok()
        && write.is_ok()
        && original.pid == end_health.pid;
    let count = f.snapshot();
    let original_store = close(run).await;
    // 500ms合法IO只有100ms工作期；child不能再次扣400ms预留。
    f.fault("");
    let mut minimum = c.clone();
    minimum.plcs[0].io_timeout_ms = 500;
    let short = Run::new("r4-rework-minimum-io", "execute", &minimum);
    short.ready().await;
    let minimum_read = short.rt.owners["plc_demo"]
        .read("minimum-budget", 1, 0)
        .await;
    let minimum_write = Execution {
        owner: &short.rt.owners["plc_demo"],
        state: &short.state,
        stop: &short.rt.stop,
    }
    .apply(intent(&minimum, "minimum-write", 42), &mut Clock::default())
    .await;
    let minimum_good = minimum_read.is_ok() && minimum_write.is_ok();
    let minimum_store = close(short).await;
    report(
        &root,
        f,
        json!({"io_timeout_ms":1200,"queue_wait_ms":1000,"response_delay_ms":600,"first":first.as_ref().map(|s|s.value),"second":second.as_ref().map(|s|s.value),"third":third.as_ref().map(|s|s.value),"write":write,"second_ms":second_ms,"write_ms":write_ms,"original":original,"final":end_health,"store":original_store,"minimum_read":minimum_read.as_ref().map(|s|s.value),"minimum_write":minimum_write,"minimum_store":minimum_store}),
    );
    assert!(
        good && minimum_good && second_ms > 1000 && write_ms > 1000,
        "fresh per-dispatch budget must permit reads and queued write"
    );
    assert_eq!(count["reads"], 3);
    assert_eq!(count["writes"], 1);
}
async fn clock_case(precall: bool) -> bool {
    let root = root(if precall {
        "r4-rework-clock-precall"
    } else {
        "r4-rework-clock-queued"
    });
    let file = root.join("wall-offset");
    std::fs::write(&file, b"0").unwrap();
    std::env::set_var("FF_TEST_CLOCK_FILE", &file);
    let release = root.join("release");
    if precall {
        std::env::set_var("FF_TEST_CHILD_RELEASE_FILE", &release);
    }
    let f = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    let run = Run::new("r4-rework-clock-state", "execute", &c);
    run.ready().await;
    let reader = if !precall {
        f.fault("delay600");
        let o = run.rt.owners["plc_demo"].clone();
        let h = tokio::spawn(async move { o.read("occupy", 1, 0).await });
        eventually(|| f.snapshot()["reads"].as_u64().unwrap() > 0).await;
        Some(h)
    } else {
        None
    };
    let o = run.rt.owners["plc_demo"].clone();
    let s = run.state.clone();
    let stop = run.rt.stop.clone();
    let mut i = intent(&c, "clock-aged", 42);
    i.issued_at_ms = now_ms() - 5000;
    i.expires_at_ms = i.issued_at_ms + 60000;
    let identity = i.clone();
    let mut clock = Clock::default();
    std::env::remove_var("FF_TEST_CLOCK_FILE");
    std::env::remove_var("FF_TEST_CHILD_RELEASE_FILE");
    let job = tokio::spawn(async move {
        let r = Execution {
            owner: &o,
            state: &s,
            stop: &stop,
        }
        .apply(i, &mut clock)
        .await;
        (r, clock)
    });
    eventually(|| state::inspect(&run.dir).unwrap()["counts"]["in_flight"] == 1).await;
    sleep(Duration::from_millis(30)).await;
    std::fs::write(&file, b"-2000").unwrap();
    if precall {
        std::fs::write(&release, b"go").unwrap();
    }
    let (result, mut clock) = job.await.unwrap();
    if let Some(h) = reader {
        h.await.unwrap().unwrap();
    }
    f.fault("");
    std::fs::write(&file, b"0").unwrap();
    let latched = clock.check(now_ms());
    let read = run.rt.owners["plc_demo"].read("independent", 1, 0).await;
    let stable = Execution {
        owner: &run.rt.owners["plc_demo"],
        state: &run.state,
        stop: &run.rt.stop,
    }
    .apply(
        intent(&c, "fresh-after-clock-invalid", 42),
        &mut Clock::default(),
    )
    .await;
    let clock_health = run.rt.owners["plc_demo"].health();
    let state = run.state.command_status(identity).await.unwrap();
    let writes = f.snapshot()["writes"].as_u64().unwrap();
    let good = result.as_ref().is_err_and(|e| e == "clock_invalid")
        && latched.as_ref().is_err_and(|e| e == "clock_invalid")
        && read.is_ok()
        && writes == 0
        && state == "canceled"
        && stable.as_ref().is_err_and(|e| e == "clock_invalid")
        && clock_health.clock_invalid;
    report(
        &root,
        f,
        json!({"precall":precall,"source_initial_age_ms":5000,"wall_offset_ms":-2000,"result":result,"latched_after_reset":latched,"independent_read":read.as_ref().map(|s|s.value),"writes":writes,"state":state,"stable_new_identity":stable,"clock_health":clock_health,"store":close(run).await}),
    );
    good
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn queued_and_precall_clock_invalid_zero_write() {
    let queued = clock_case(false).await;
    let precall = clock_case(true).await;
    assert!(
        queued && precall,
        "same anchor must guard queued and child precall"
    );
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn health_follows_actual_started_and_completion() {
    let root = root("r4-rework-started");
    let release = root.join("release");
    std::env::set_var("FF_TEST_CHILD_RELEASE_FILE", &release);
    let f = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let mut c = config();
    c.plcs[0].io_timeout_ms = 1200;
    let run = Run::new("r4-rework-started-state", "execute", &c);
    run.ready().await;
    std::env::remove_var("FF_TEST_CHILD_RELEASE_FILE");
    f.fault("delay600");
    let o = run.rt.owners["plc_demo"].clone();
    let s = run.state.clone();
    let stop = run.rt.stop.clone();
    let i = intent(&c, "health-started", 42);
    let job = tokio::spawn(async move {
        Execution {
            owner: &o,
            state: &s,
            stop: &stop,
        }
        .apply(i, &mut Clock::default())
        .await
    });
    eventually(|| state::inspect(&run.dir).unwrap()["counts"]["in_flight"] == 1).await;
    sleep(Duration::from_millis(100)).await;
    let before = run.rt.owners["plc_demo"].health();
    let before_events = logs(&run.dir);
    let before_writes = f.snapshot()["writes"].clone();
    std::fs::write(&release, b"go").unwrap();
    eventually(|| f.snapshot()["writes"] == 1).await;
    sleep(Duration::from_millis(30)).await;
    let during = run.rt.owners["plc_demo"].health();
    let during_events = logs(&run.dir);
    let result = job.await.unwrap();
    let after = run.rt.owners["plc_demo"].health();
    let good = before.in_flight == 0
        && before_events == 0
        && before_writes == 0
        && during.in_flight == 1
        && during_events == 1
        && after.in_flight == 0
        && result.is_ok();
    f.fault("hold_ack");
    let owner = run.rt.owners["plc_demo"].clone();
    let state = run.state.clone();
    let stop = run.rt.stop.clone();
    let i = intent(&c, "health-timeout", 42);
    let fault = tokio::spawn(async move {
        Execution {
            owner: &owner,
            state: &state,
            stop: &stop,
        }
        .apply(i, &mut Clock::default())
        .await
    });
    eventually(|| f.snapshot()["writes"] == 2).await;
    sleep(Duration::from_millis(20)).await;
    let fault_started = run.rt.owners["plc_demo"].health();
    let fault_result = fault.await.unwrap();
    let fault_after = run.rt.owners["plc_demo"].health();
    let fault_good =
        fault_started.in_flight == 1 && fault_result.is_err() && fault_after.in_flight == 0;
    assert_eq!(
        unsafe { libc::kill(fault_started.pid.unwrap() as i32, 0) },
        -1
    );
    f.fault("");
    report(
        &root,
        f,
        json!({"before":before,"before_events":before_events,"before_writevar":before_writes,"during":during,"during_events":during_events,"after":after,"result":result,"fault_started":fault_started,"fault_after":fault_after,"fault_result":fault_result,"store":close(run).await}),
    );
    assert!(
        good && fault_good,
        "execution health must follow real started/completion/fault cleanup"
    );
}
