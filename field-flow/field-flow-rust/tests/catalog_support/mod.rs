//! 文件：tests/catalog_support/mod.rs；FF-004有界真实CLI、结构化JSONL判定及确切资源证据。
#![allow(dead_code)]
use field_flow::{
    domain::id,
    fixture::catalog_demo::{CatalogFixture, Options},
    infrastructure::state,
};
use serde_json::{json, Value};
use std::{
    fs::{self, File},
    net::TcpListener,
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    thread::sleep,
    time::{Duration, Instant},
};
pub const PRODUCT: &str = env!("CARGO_BIN_EXE_field-flow");
pub const FIXTURE: &str = env!("CARGO_BIN_EXE_ff-fixture");
pub fn root(suite: &str) -> PathBuf {
    let base = std::env::var_os("FF004_EVIDENCE_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(format!("/private/tmp/ff-004-r2-test-{}", id())));
    fs::create_dir_all(&base).unwrap();
    let p = base.join(suite);
    fs::create_dir(&p).expect("new suite evidence directory required");
    p
}
pub fn config(dir: &Path) -> PathBuf {
    let cfg = dir.join("config");
    fs::create_dir(&cfg).unwrap();
    fs::create_dir(cfg.join("plcs")).unwrap();
    for name in ["s7-a.json", "s7-b.json", "modbus-example.json"] {
        fs::copy(
            Path::new("config/plcs").join(name),
            cfg.join("plcs").join(name),
        )
        .unwrap();
    }
    fs::copy("config/catalog-demo.yaml", cfg.join("main.yaml")).unwrap();
    cfg.join("main.yaml")
}
pub fn value(p: &Path) -> Value {
    serde_yaml::from_slice(&fs::read(p).unwrap()).unwrap()
}
pub fn put(p: &Path, v: &Value) {
    fs::write(p, serde_json::to_vec_pretty(v).unwrap()).unwrap();
}
pub fn cli(args: &[&str]) -> std::process::Output {
    Command::new(PRODUCT).args(args).output().unwrap()
}
pub fn events(p: &Path) -> Vec<Value> {
    fs::read_to_string(p)
        .unwrap_or_default()
        .lines()
        .filter_map(|s| serde_json::from_str::<Value>(s).ok())
        .map(|mut v| {
            if let Some(s) = v["context"].as_str() {
                v["context"] = serde_json::from_str(s).expect("JSON context");
            }
            v
        })
        .collect()
}
pub fn forced(v: &Value) -> bool {
    v["event"] == "forced_driver_stop"
        || v["error_key"]
            .as_str()
            .is_some_and(|s| s.starts_with("forced_driver_stop"))
        || v["context"]["error_key"]
            .as_str()
            .is_some_and(|s| s.starts_with("forced_driver_stop"))
        || v["had_forced_driver_stop"].as_bool() == Some(true)
        || v["context"]["had_forced_driver_stop"].as_bool() == Some(true)
}
pub fn absent(pid: u32) -> bool {
    pid > 0
        && unsafe { libc::kill(pid as i32, 0) } == -1
        && std::io::Error::last_os_error().raw_os_error() == Some(libc::ESRCH)
}
pub fn until(seconds: u64, mut p: impl FnMut() -> bool) {
    let end = Instant::now() + Duration::from_secs(seconds);
    while !p() {
        assert!(Instant::now() < end, "bounded observation deadline");
        sleep(Duration::from_millis(5));
    }
}
pub fn preflight() {
    for p in [34102, 34103, 34112, 34113, 34880] {
        drop(
            TcpListener::bind(("127.0.0.1", p))
                .expect("port conflict; do not kill or change ports"),
        );
    }
}
pub struct Scene {
    pub dir: PathBuf,
    pub config: PathBuf,
    pub state: PathBuf,
    pub product: Option<Child>,
    pub fixture: Option<CatalogFixture>,
    pub started: Instant,
    pub report: Value,
    pub normal: bool,
}
impl Scene {
    pub fn new(root: &Path, label: &str, mode: &str, edit: impl FnOnce(&mut Value)) -> Self {
        let dir = root.join(label);
        fs::create_dir(&dir).unwrap();
        let config = config(&dir);
        let mut v = value(&config);
        edit(&mut v);
        put(&config, &v);
        let state = dir.join("state");
        let out = cli(&[
            "state",
            "init",
            "--synthetic",
            "--mode",
            mode,
            "--state-dir",
            state.to_str().unwrap(),
            "--instance-id",
            v["instance_id"].as_str().unwrap(),
        ]);
        assert!(out.status.success());
        fs::write(dir.join("init.jsonl"), &out.stdout).unwrap();
        Self {
            dir,
            config,
            state,
            product: None,
            fixture: None,
            started: Instant::now(),
            report: json!({"label":label,"mode":mode,"result":"incomplete"}),
            normal: true,
        }
    }
    pub fn start_fixture(&mut self, options: Options) {
        preflight();
        self.fixture = Some(CatalogFixture::start_with(Path::new(FIXTURE), options).unwrap());
    }
    pub fn start(&mut self, execute: bool) {
        self.start_path(execute, self.config.clone());
    }
    pub fn start_path(&mut self, execute: bool, p: PathBuf) {
        let mut c = Command::new(PRODUCT);
        c.args([
            "run",
            "--config",
            p.to_str().unwrap(),
            "--state-dir",
            self.state.to_str().unwrap(),
        ]);
        if execute {
            c.arg("--execute");
        }
        let child = c
            .stdout(Stdio::from(
                File::options()
                    .create(true)
                    .append(true)
                    .open(self.dir.join("product.jsonl"))
                    .unwrap(),
            ))
            .stderr(Stdio::from(
                File::options()
                    .create(true)
                    .append(true)
                    .open(self.dir.join("product.stderr"))
                    .unwrap(),
            ))
            .spawn()
            .unwrap();
        self.report["product_pid"] = json!(child.id());
        self.product = Some(child);
    }
    pub fn snapshot(&self) -> Value {
        self.fixture.as_ref().unwrap().snapshot()
    }
    pub fn rows(&self) -> Vec<Value> {
        events(&self.dir.join("product.jsonl"))
    }
    pub fn read_round(&self, expected: &[i16]) -> bool {
        self.rows().iter().any(|v| {
            let c = &v["context"];
            v["event"] == "points_health"
                && c["flow_id"] == "read_pair"
                && c["status"] == "complete"
                && c["items"].as_array().is_some_and(|a| {
                    a.iter()
                        .map(|i| i["sample"]["value"].as_i64())
                        .collect::<Vec<_>>()
                        == expected.iter().map(|n| Some(*n as i64)).collect::<Vec<_>>()
                })
        })
    }
    pub fn wire_round(&self, expected: &[i16]) -> bool {
        let s = self.snapshot();
        let mut rows: Vec<_> = s["trace"]
            .as_array()
            .unwrap()
            .iter()
            .flat_map(|t| t.as_array().unwrap())
            .filter(|r| r["operation"] == 4)
            .collect();
        rows.sort_by_key(|r| r["sequence"].as_u64().unwrap());
        let values: Vec<_> = rows.iter().map(|r| r["wire_value"].as_i64()).collect();
        values
            .windows(expected.len())
            .any(|w| w == expected.iter().map(|n| Some(*n as i64)).collect::<Vec<_>>())
    }
    pub fn stop(&mut self, expected: i32) {
        if let Some(mut child) = self.product.take() {
            assert_eq!(unsafe { libc::kill(child.id() as i32, libc::SIGTERM) }, 0);
            let end = Instant::now() + Duration::from_secs(16);
            let status = loop {
                if let Some(status) = child.try_wait().unwrap() {
                    break status;
                }
                if Instant::now() >= end {
                    child.kill().unwrap();
                    child.wait().unwrap();
                    panic!("forced product cleanup");
                }
                sleep(Duration::from_millis(5));
            };
            self.report["product_exit"] = json!(status.code());
            assert_eq!(status.code(), Some(expected));
            assert!(absent(child.id()));
        }
    }
    pub fn finish(&mut self) {
        let rows = self.rows();
        if self.normal {
            assert!(rows.iter().any(|v| v["event"] == "runtime_tasks_joined"));
            assert!(rows.iter().any(|v| v["event"] == "shutdown_complete"));
            assert!(!rows.iter().any(forced), "normal scenario forced stop");
        }
        let mut pids = Vec::new();
        for v in &rows {
            if let Some(pid) = v["context"]["pid"].as_u64() {
                pids.push(pid as u32);
            }
        }
        if let Some(f) = self.fixture.as_mut() {
            f.close().unwrap();
            let snap = f.snapshot();
            assert_eq!(snap["trace_truncated"], false);
            for pid in snap["native_pids"].as_array().unwrap() {
                pids.push(pid.as_u64().unwrap() as u32);
            }
            self.report["fixture"] = snap;
        }
        pids.sort();
        pids.dedup();
        for pid in &pids {
            assert!(absent(*pid), "unreaped {pid}");
        }
        preflight();
        self.report["reaped_pids"] = json!(pids);
        self.report["ports_rebound"] = json!([34102, 34103, 34112, 34113, 34880]);
        self.report["elapsed_seconds"] = json!(self.started.elapsed().as_secs_f64());
        self.report["result"] = json!("passed");
        self.save();
        assert!(self.started.elapsed() <= Duration::from_secs(45));
    }
    pub fn save(&self) {
        fs::write(
            self.dir.join("report.json"),
            serde_json::to_vec_pretty(&self.report).unwrap(),
        )
        .unwrap();
    }
}
impl Drop for Scene {
    fn drop(&mut self) {
        if let Some(mut child) = self.product.take() {
            if child.try_wait().unwrap().is_none() {
                unsafe { libc::kill(child.id() as i32, libc::SIGTERM) };
                let end = Instant::now() + Duration::from_secs(16);
                while child.try_wait().unwrap().is_none() && Instant::now() < end {
                    sleep(Duration::from_millis(10));
                }
                if child.try_wait().unwrap().is_none() {
                    let _ = child.kill();
                    let _ = child.wait();
                    self.report["forced_cleanup"] = json!(true);
                }
            }
        }
        if let Some(f) = self.fixture.as_mut() {
            let closed = f.close();
            self.report["cleanup_result"] = json!(closed);
            self.report["fixture_cleanup"] = f.snapshot();
        }
        self.save();
    }
}
pub fn read_flow(id: &str, devices: Value, reads: Value) -> Value {
    json!({"id":id,"kind":"read_points","business_name":id,"interval_ms":100,"device_ids":devices,"reads":reads})
}
pub fn counts(scene: &Scene) -> Value {
    state::inspect(&scene.state).unwrap()["counts"].clone()
}
pub fn check_raw(s: &Value) {
    fn bytes(v: &Value) -> Vec<u8> {
        let s = v.as_str().unwrap();
        (0..s.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap())
            .collect()
    }
    for i in 0..2 {
        let rows = s["trace"][i].as_array().unwrap();
        let cotp = rows
            .iter()
            .find(|r| {
                r["operation"] == 0
                    && r["request_hex"]
                        .as_str()
                        .is_some_and(|h| h.contains("c1020100") && h.contains("c2020101"))
            })
            .expect("COTP C1/C2");
        let cr = bytes(&cotp["request_hex"]);
        assert_eq!(&cr[..2], &[3, 0]);
        assert_eq!(u16::from_be_bytes([cr[2], cr[3]]) as usize, cr.len());
        assert_eq!(cr[5], 0xe0);
        let mut last_end = 0;
        let mut previous_ref = 0;
        for row in rows
            .iter()
            .filter(|r| r["operation"] == 4 || r["operation"] == 5)
        {
            let req = bytes(&row["request_hex"]);
            let resp = bytes(&row["response_hex"]);
            let op = row["operation"].as_u64().unwrap() as u8;
            for frame in [&req, &resp] {
                assert_eq!(&frame[..7], &[3, 0, 0, frame.len() as u8, 2, 0xf0, 0x80]);
                assert_eq!(
                    u16::from_be_bytes([frame[2], frame[3]]) as usize,
                    frame.len()
                );
            }
            assert_eq!(&req[7..11], &[0x32, 1, 0, 0]);
            assert_eq!(
                &req[13..19],
                &[0, 14, 0, if op == 4 { 0 } else { 6 }, op, 1]
            );
            assert_eq!(&req[19..25], &[0x12, 0x0a, 0x10, 2, 0, 2]);
            assert_eq!(req[27], 0x84);
            let db = u16::from_be_bytes([req[25], req[26]]);
            let offset = ((req[28] as u32) << 16 | (req[29] as u32) << 8 | req[30] as u32) / 8;
            assert_eq!(row["db"], db);
            assert_eq!(row["byte_offset"], offset);
            assert_eq!(row["length"], 2);
            assert!(matches!(db, 1 | 2));
            assert!(matches!(offset, 0 | 2));
            let reference = u16::from_be_bytes([req[11], req[12]]);
            assert_eq!(reference, previous_ref + 1);
            previous_ref = reference;
            assert_eq!(&resp[7..11], &[0x32, 3, 0, 0]);
            assert_eq!(&resp[11..13], &req[11..13]);
            assert_eq!(
                &resp[13..22],
                &[0, 2, 0, if op == 4 { 6 } else { 1 }, 0, 0, op, 1, 0xff]
            );
            if op == 4 {
                assert_eq!(req.len(), 31);
                assert_eq!(resp.len(), 27);
                assert_eq!(&resp[22..25], &[4, 0, 16]);
                assert_eq!(row["wire_value"], i16::from_be_bytes([resp[25], resp[26]]));
            } else {
                assert_eq!(req.len(), 37);
                assert_eq!(resp.len(), 22);
                assert_eq!(&req[31..35], &[0, 4, 0, 16]);
                assert_eq!(row["wire_value"], i16::from_be_bytes([req[35], req[36]]));
            }
            let begin = row["started_us"].as_u64().unwrap();
            let end = row["elapsed_us"].as_u64().unwrap();
            assert!(
                begin >= last_end && end >= begin,
                "one real in-flight call per PLC"
            );
            last_end = end;
        }
    }
}
