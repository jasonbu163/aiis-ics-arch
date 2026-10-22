//! 文件：tests/process_lifecycle.rs；仅本程序自建父/driver进程的崩溃、存活锁与正常退出证据。
#![cfg(feature = "test-fixture")]
mod support;
use field_flow::{
    fixture::Fixture,
    infrastructure::{posix::InstanceLock, state},
};
use serde_json::{json, Value};
use std::{
    fs::File,
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    time::Duration,
};
use support::*;
use tokio::time::{sleep, Instant};
struct Process {
    child: Child,
    dir: PathBuf,
}
impl Process {
    fn start(dir: PathBuf, delay: bool) -> Self {
        let log = File::create(dir.join("stdout.jsonl")).unwrap();
        let err = File::create(dir.join("stderr.txt")).unwrap();
        let mut cmd = Command::new(env!("CARGO_BIN_EXE_field-flow"));
        cmd.args([
            "run",
            "--config",
            Path::new("config/loopback.yaml").to_str().unwrap(),
            "--state-dir",
            dir.to_str().unwrap(),
            "--execute",
        ])
        .stdout(log)
        .stderr(err)
        .stdin(Stdio::null());
        if delay {
            cmd.env("FF_TEST_PARENT_LOST_DELAY_MS", "100");
        }
        Self {
            child: cmd.spawn().unwrap(),
            dir,
        }
    }
    fn events(&self) -> Vec<Value> {
        std::fs::read_to_string(self.dir.join("stdout.jsonl"))
            .unwrap()
            .lines()
            .filter_map(|s| serde_json::from_str(s).ok())
            .collect()
    }
    async fn pid(&self) -> u32 {
        let end = Instant::now() + Duration::from_secs(5);
        loop {
            for e in self.events() {
                if e["event"] == "driver_ready" {
                    let ctx: Value = serde_json::from_str(e["context"].as_str().unwrap()).unwrap();
                    return ctx["pid"].as_u64().unwrap() as u32;
                }
            }
            assert!(Instant::now() < end);
            sleep(Duration::from_millis(5)).await;
        }
    }
    async fn wait(&mut self, code: i32) {
        let end = Instant::now() + Duration::from_secs(15);
        loop {
            if let Some(s) = self.child.try_wait().unwrap() {
                assert_eq!(
                    s.code(),
                    Some(code),
                    "stderr: {}",
                    std::fs::read_to_string(self.dir.join("stderr.txt")).unwrap()
                );
                break;
            }
            assert!(Instant::now() < end, "parent exit deadline");
            sleep(Duration::from_millis(5)).await;
        }
    }
}
impl Drop for Process {
    fn drop(&mut self) {
        if self.child.try_wait().unwrap().is_none() {
            let _ = self.child.kill();
            let _ = self.child.wait();
        }
    }
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn child_and_parent_death_are_real() {
    let mut fixture = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    for kill_parent in [false, true] {
        let base = root(if kill_parent {
            "parent-death"
        } else {
            "child-death"
        });
        let dir = base.join("state");
        state::init(&dir, "execute", &c.instance_id).unwrap();
        fixture.command(
            if kill_parent {
                "parent-lost"
            } else {
                "child-lost"
            },
            json!(42),
        );
        fixture.fault("hold_ack");
        let before = fixture.snapshot()["applied"].as_u64().unwrap();
        let mut process = Process::start(dir.clone(), kill_parent);
        let child_pid = process.pid().await;
        eventually(|| fixture.snapshot()["applied"].as_u64().unwrap() > before).await;
        assert!(InstanceLock::acquire(&dir).is_err());
        let start = Instant::now();
        if kill_parent {
            process.child.kill().unwrap();
            process.child.wait().unwrap();
            let mut retained = false;
            while unsafe { libc::kill(child_pid as i32, 0) } == 0 {
                retained |= InstanceLock::acquire(&dir).is_err();
                assert!(
                    start.elapsed().as_millis() <= 500,
                    "parent-lost child remains"
                );
                sleep(Duration::from_millis(2)).await;
            }
            assert!(
                retained,
                "inherited lock did not retain ownership until child ended"
            );
            assert!(InstanceLock::acquire(&dir).is_ok());
        } else {
            assert_eq!(unsafe { libc::kill(child_pid as i32, libc::SIGKILL) }, 0);
            eventually(|| {
                process
                    .events()
                    .iter()
                    .any(|e| e["event"] == "driver_process_reaped")
            })
            .await;
            assert_eq!(unsafe { libc::kill(child_pid as i32, 0) }, -1);
            unsafe {
                libc::kill(process.child.id() as i32, libc::SIGTERM);
            }
            process.wait(1).await;
            assert!(!process
                .events()
                .iter()
                .any(|e| e["event"] == "shutdown_complete"));
        }
        fixture.fault("");
        let mut restart = Process::start(dir.clone(), false);
        restart.pid().await;
        sleep(Duration::from_millis(5500)).await;
        assert_eq!(fixture.snapshot()["applied"].as_u64().unwrap(), before + 1);
        assert_eq!(state::inspect(&dir).unwrap()["counts"]["unknown"], 1);
        unsafe {
            libc::kill(restart.child.id() as i32, libc::SIGTERM);
        }
        restart.wait(0).await;
        assert!(restart
            .events()
            .iter()
            .any(|e| e["event"] == "shutdown_complete"));
        println!(
            "{}",
            json!({"ac":"AC10/AC13","kill_parent":kill_parent,"old_child_pid":child_pid,"child_gone":true,"duration_to_observation_ms":start.elapsed().as_millis(),"applied":1,"unknown":1,"store":dir})
        );
    }
    fixture.close().unwrap();
}
