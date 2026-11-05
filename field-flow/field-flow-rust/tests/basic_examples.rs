//! 文件：tests/basic_examples.rs；FF-005正式CLI/配置矩阵，自身Fixture、有限报告及真实回收。
#![cfg(feature = "test-fixture")]
use field_flow::{config::Config, domain::id, fixture::Fixture, infrastructure::state};
use serde_json::{json, Value};
use std::{
    fs::{self, File},
    net::TcpListener,
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::{Mutex, OnceLock},
    thread::sleep,
    time::{Duration, Instant},
};
static SERIAL: Mutex<()> = Mutex::new(());
static ROOT: OnceLock<PathBuf> = OnceLock::new();
static START: OnceLock<Instant> = OnceLock::new();
fn root() -> &'static PathBuf {
    START.get_or_init(Instant::now);
    ROOT.get_or_init(|| {
        let p = std::env::var_os("FF005_EVIDENCE_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from(format!("/private/tmp/ff-005-r1-rust-{}", id())));
        fs::create_dir_all(&p).unwrap();
        assert_eq!(
            fs::read_dir(&p).unwrap().count(),
            0,
            "use a new empty evidence root"
        );
        println!("{}", json!({"ff005_evidence":p}));
        p
    })
}
fn cli(args: &[&str], dir: &Path, label: &str) -> Value {
    let out = Command::new(env!("CARGO_BIN_EXE_field-flow"))
        .args(args)
        .output()
        .unwrap();
    fs::write(dir.join(format!("{label}.stdout")), &out.stdout).unwrap();
    fs::write(dir.join(format!("{label}.stderr")), &out.stderr).unwrap();
    json!({"command":args,"executable":env!("CARGO_BIN_EXE_field-flow"),"exit_code":out.status.code(),"stdout":String::from_utf8_lossy(&out.stdout),"stderr":String::from_utf8_lossy(&out.stderr)})
}
fn count(v: &Value, k: &str) -> u64 {
    v[k].as_u64().unwrap_or(0)
}
fn wait_for(child: &mut Child, mut predicate: impl FnMut() -> bool) {
    let end = Instant::now() + Duration::from_secs(8);
    while !predicate() {
        assert!(
            child.try_wait().unwrap().is_none(),
            "product exited before observation"
        );
        assert!(Instant::now() < end, "bounded observation deadline");
        sleep(Duration::from_millis(10));
    }
}
fn absent(pid: u32) -> bool {
    assert!(pid > 0);
    let result = unsafe { libc::kill(pid as i32, 0) };
    result == -1 && std::io::Error::last_os_error().raw_os_error() == Some(libc::ESRCH)
}
fn stop(child: &mut Child) -> std::process::ExitStatus {
    assert_eq!(unsafe { libc::kill(child.id() as i32, libc::SIGTERM) }, 0);
    let end = Instant::now() + Duration::from_secs(16);
    loop {
        if let Some(status) = child.try_wait().unwrap() {
            return status;
        }
        if Instant::now() >= end {
            child.kill().unwrap();
            child.wait().unwrap();
            panic!("forced product cleanup is failure");
        }
        sleep(Duration::from_millis(10));
    }
}
fn memory(seed: Option<i16>) -> String {
    use field_flow::infrastructure::s7_int_pdu::{Operation, Session, Validated};
    use rust_snap7::{InternalParam as P, InternalParamValue as V, S7Client};
    let client = S7Client::create();
    client.set_param(P::RemotePort, V::U16(31102)).unwrap();
    client.connect_to("127.0.0.1", 0, 1).unwrap();
    let mut session = Session::default();
    if let Some(value) = seed {
        assert!(matches!(
            session
                .exchange(&client, 1, 0, Operation::Write(value))
                .unwrap(),
            Validated::Write(_)
        ));
    }
    let mut bytes = Vec::new();
    for offset in (0..16).step_by(2) {
        if let Validated::Read(v) = session
            .exchange(&client, 1, offset, Operation::Read)
            .unwrap()
        {
            bytes.extend(v.value().to_be_bytes());
        } else {
            panic!("missing independent read");
        }
    }
    client.disconnect().unwrap();
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}
fn scenario(case: &str, mode: &str, value: i16, variant: &str, seed: Option<i16>) {
    let started = Instant::now();
    let dir = root().join(format!("{case}-{mode}-{variant}-{value}-{seed:?}"));
    fs::create_dir(&dir).unwrap();
    let config = Path::new("config").join(if case == "basic01" {
        "loopback.yaml".into()
    } else {
        format!("{case}.yaml")
    });
    let c = Config::load(&config).unwrap();
    let state_dir = dir.join("state");
    let path = state_dir.to_str().unwrap();
    let init = cli(
        &[
            "state",
            "init",
            "--synthetic",
            "--mode",
            mode,
            "--state-dir",
            path,
            "--instance-id",
            &c.instance_id,
        ],
        &dir,
        "init",
    );
    assert_eq!(init["exit_code"], 0);
    let mut fixture = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let mut child: Option<Child> = None;
    let mut report = json!({"case":case,"mode":mode,"variant":variant,"init":init,"config":config,"result":"failed"});
    let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        if seed.is_some() {
            memory(seed);
        }
        let preparation = fixture.snapshot();
        if variant != "idle" {
            fixture.command(&format!("ff005-{}", id()), json!(value));
            let mut body: Value =
                serde_json::from_slice(&fixture.behavior.lock().unwrap().body).unwrap();
            if variant == "invalid" {
                body["value"] = json!("42");
            }
            if variant == "expired" {
                body["issued_at_ms"] = json!(body["issued_at_ms"].as_i64().unwrap() - 2000);
                body["expires_at_ms"] = json!(body["issued_at_ms"].as_i64().unwrap() + 1000);
            }
            fixture.body(body);
        }
        let original = fixture.behavior.lock().unwrap().body.clone();
        if variant == "unknown" {
            fixture.behavior.lock().unwrap().delay_ms = 300;
        }
        if variant == "read_error" {
            fixture.fault("short_ack");
        }
        let mut args = vec![
            "run",
            "--config",
            config.to_str().unwrap(),
            "--state-dir",
            path,
        ];
        if mode == "execute" {
            args.push("--execute");
        }
        child = Some(
            Command::new(env!("CARGO_BIN_EXE_field-flow"))
                .args(&args)
                .stdout(Stdio::from(
                    File::create(dir.join("product.jsonl")).unwrap(),
                ))
                .stderr(Stdio::from(
                    File::create(dir.join("product.stderr")).unwrap(),
                ))
                .spawn()
                .unwrap(),
        );
        let parent = child.as_mut().unwrap();
        report["product_pid"] = json!(parent.id());
        report["fixture_pid"] = json!(fixture.native_pid);
        report["input"] = serde_json::from_slice(&original).unwrap();
        report["preparation"] = preparation.clone();
        report["command"] = json!(args);
        let allowed = variant == "value"
            && !(case == "basic03" && !(1..=100).contains(&value))
            && !(case == "basic02" && seed == Some(0));
        let many = allowed && value == 42;
        if variant == "unknown" {
            wait_for(parent, || count(&fixture.snapshot(), "gets") == 1);
            fixture.fault("short_ack");
            wait_for(parent, || count(&fixture.snapshot(), "writes") == 1);
            fixture.fault("");
            wait_for(parent, || {
                state::inspect(&state_dir).unwrap()["counts"]["unknown"] == 1
            });
            let before = count(&fixture.snapshot(), "reads");
            wait_for(parent, || {
                count(&fixture.snapshot(), "reads") >= before + 10
            });
        }
        if variant == "read_error" {
            wait_for(parent, || count(&fixture.snapshot(), "reads") >= 2);
        } else if case == "basic02" {
            wait_for(parent, || {
                count(&fixture.snapshot(), "reads") - count(&preparation, "reads")
                    >= if many { 11 } else { 3 }
            });
        } else {
            wait_for(parent, || {
                count(&fixture.snapshot(), "gets") >= if many { 11 } else { 3 }
            });
        }
        if case == "basic02"
            && seed != Some(0)
            && !matches!(variant, "read_error" | "unknown")
            && !(allowed && mode == "execute")
        {
            wait_for(parent, || {
                count(&fixture.snapshot(), "gets") >= if many { 11 } else { 3 }
            });
        }
        let key = if mode == "execute" {
            "confirmed"
        } else {
            "simulated"
        };
        if allowed {
            wait_for(parent, || {
                state::inspect(&state_dir).unwrap()["counts"][key] == 1
            });
        }
        let product = fixture.snapshot();
        let state = state::inspect(&state_dir).unwrap();
        assert_eq!(
            fixture.behavior.lock().unwrap().body,
            original,
            "original identity/time changed"
        );
        assert_eq!(
            state["counts"],
            if variant == "unknown" {
                json!({"unknown":1})
            } else if allowed {
                json!({key:1})
            } else {
                json!({})
            }
        );
        assert_eq!(
            count(&product, "writes") - count(&preparation, "writes"),
            u64::from((allowed && mode == "execute") || variant == "unknown")
        );
        if case == "basic02" {
            if seed == Some(0) {
                assert_eq!(product["gets"], 0);
            } else if variant == "read_error" {
                assert_eq!(product["gets"], 0);
            } else if (allowed && mode == "execute") || variant == "unknown" {
                assert_eq!(product["gets"], 1);
            } else {
                assert!(count(&product, "gets") >= 3);
            }
            let trace = product["trace"].as_array().unwrap();
            let before = preparation["trace"].as_array().unwrap().len();
            assert_eq!(
                trace[before..]
                    .iter()
                    .find(|v| matches!(v["operation"].as_u64(), Some(4 | 5)))
                    .unwrap()["operation"],
                4
            );
        }
        report["product_window"] = product;
        report["state_before_stop"] = state;
        let status = stop(parent);
        report["product_exit"] = json!(status.code());
        assert_eq!(
            status.code(),
            Some(if matches!(variant, "unknown" | "read_error") {
                1
            } else {
                0
            })
        );
        assert!(absent(parent.id()));
        let text = fs::read_to_string(dir.join("product.jsonl")).unwrap();
        if matches!(variant, "unknown" | "read_error") {
            assert!(text.contains("shutdown_incomplete"));
            assert!(!text.lines().any(|line| {
                let row: Value = serde_json::from_str(line).unwrap();
                row["event"] == "forced_driver_stop"
            }));
        } else {
            assert!(text.contains("runtime_tasks_joined") && text.contains("shutdown_complete"));
            assert!(!text.contains("fault_cleanup"));
        }
        if matches!(variant, "invalid" | "expired" | "read_error") {
            assert!(text.contains("recovering"));
        } else if variant != "unknown" {
            assert!(!text.contains("recovering") && !text.contains("\"blocked\""));
        }
        let mut pids = vec![parent.id(), fixture.native_pid];
        for line in text.lines() {
            let row: Value = serde_json::from_str(line).unwrap();
            let context: Value = row["context"]
                .as_str()
                .map(|s| serde_json::from_str(s).unwrap())
                .unwrap_or(json!({}));
            if let Some(pid) = context["pid"].as_u64().or_else(|| row["pid"].as_u64()) {
                pids.push(pid as u32);
            }
        }
        report["inspect"] = cli(&["state", "inspect", "--state-dir", path], &dir, "inspect");
        assert_eq!(report["inspect"]["exit_code"], 0);
        fixture.fault("");
        let verified = memory(None);
        let expected = if (allowed && mode == "execute") || variant == "unknown" {
            value
        } else {
            seed.unwrap_or(-23131)
        };
        assert_eq!(
            verified,
            format!("{:04x}{}", expected as u16, "a5".repeat(14))
        );
        report["independent_memory_hex"] = json!(verified);
        fixture.close().unwrap();
        for pid in &pids {
            assert!(absent(*pid), "unreaped PID {pid}");
        }
        for port in [31102, 31103, 31880] {
            drop(TcpListener::bind(("127.0.0.1", port)).unwrap());
        }
        report["reaped_pids"] = json!(pids);
        report["ports_rebound"] = json!([31102, 31103, 31880]);
        report["fixture_exit"] = json!(0);
        report["result"] = json!("passed");
    }));
    if let Some(parent) = child.as_mut() {
        if parent.try_wait().unwrap().is_none() {
            report["forced_cleanup"] = json!(true);
            stop(parent);
        }
    }
    let closed = fixture.close();
    report["fixture_cleanup"] = json!(closed);
    report["elapsed_seconds"] = json!(started.elapsed().as_secs_f64());
    fs::write(
        dir.join("report.json"),
        serde_json::to_vec_pretty(&report).unwrap(),
    )
    .unwrap();
    if let Err(panic) = outcome {
        std::panic::resume_unwind(panic);
    }
    assert!(closed.is_ok());
    assert!(started.elapsed() <= Duration::from_secs(45));
    assert!(START.get().unwrap().elapsed() <= Duration::from_secs(600));
}
#[test]
fn basic01_cli() {
    let _serial = SERIAL.lock().unwrap_or_else(|e| e.into_inner());
    for mode in ["dry_run", "execute"] {
        scenario("basic01", mode, 42, "value", None);
        scenario("basic01", mode, 42, "idle", None);
    }
}
#[test]
fn basic02_cli() {
    let _serial = SERIAL.lock().unwrap_or_else(|e| e.into_inner());
    for mode in ["dry_run", "execute"] {
        for variant in ["value", "idle", "invalid", "expired", "read_error"] {
            scenario("basic02", mode, 42, variant, None);
        }
        for seed in [-1, 0] {
            scenario("basic02", mode, 42, "value", Some(seed));
        }
    }
    scenario("basic02", "execute", 42, "unknown", None);
}
#[test]
fn basic03_cli() {
    let _serial = SERIAL.lock().unwrap_or_else(|e| e.into_inner());
    for mode in ["dry_run", "execute"] {
        for value in [-1, 0, 1, 42, 100, 101] {
            scenario("basic03", mode, value, "value", None);
        }
        for variant in ["idle", "invalid", "expired"] {
            scenario("basic03", mode, 42, variant, None);
        }
    }
}
