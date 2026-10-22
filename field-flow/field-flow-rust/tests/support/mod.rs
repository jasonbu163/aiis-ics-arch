//! 文件：tests/support/mod.rs；本机协议矩阵的有界进程与状态夹具。
use field_flow::{
    config::Config,
    domain::{id, Input},
    infrastructure::state::{self, State, StateTask},
    runtime::Runtime,
    Result,
};
use std::{path::PathBuf, time::Duration};
use tokio::time::{sleep, Instant};
pub fn config() -> Config {
    Config::load(std::path::Path::new("config/loopback.yaml")).unwrap()
}
pub fn root(label: &str) -> PathBuf {
    let p = PathBuf::from(format!("/private/tmp/ff-001-r1-r2-rust-{}-{}", label, id()));
    std::fs::create_dir(&p).unwrap();
    p
}
pub struct Run {
    pub rt: Runtime,
    pub state: State,
    pub task: StateTask,
    pub dir: PathBuf,
}
impl Run {
    pub fn new(label: &str, mode: &str, c: &Config) -> Self {
        let root = root(label);
        let dir = root.join("state");
        state::init(&dir, mode, &c.instance_id).unwrap();
        Self::open(dir, mode, c)
    }
    pub fn open(dir: PathBuf, mode: &str, c: &Config) -> Self {
        let (state, task) = State::open(&dir, mode, &c.instance_id, &id()).unwrap();
        let rt = Runtime::start(
            c,
            &dir,
            std::path::Path::new(env!("CARGO_BIN_EXE_field-flow")),
            state.clone(),
        )
        .unwrap();
        Self {
            rt,
            state,
            task,
            dir,
        }
    }
    pub async fn ready(&self) {
        let until = Instant::now() + Duration::from_secs(4);
        while self.rt.owners["plc_demo"].health().state != "ready" {
            assert!(
                Instant::now() < until,
                "ready: {:?}",
                self.rt.owners["plc_demo"].health()
            );
            sleep(Duration::from_millis(10)).await;
        }
    }
    pub async fn close(self, normal: bool) -> PathBuf {
        let Self {
            rt,
            state,
            task,
            dir,
        } = self;
        let result = rt.shutdown(15000).await;
        if normal {
            result.unwrap();
            state.finalize().await.unwrap();
        } else {
            assert!(result.is_err());
        }
        drop(state);
        tokio::time::timeout(Duration::from_secs(3), task.join())
            .await
            .unwrap()
            .unwrap();
        dir
    }
    pub async fn iteration(&self, c: &Config) -> Result<()> {
        let http = field_flow::services::Http::new(&c.http)?;
        field_flow::app::demo01::iteration(
            &c.flows[0],
            &c.plcs[0],
            &http,
            &self.rt.owners["plc_demo"],
            &self.state,
            &self.rt.stop,
            &mut field_flow::domain::Clock::default(),
        )
        .await
    }
}
pub async fn eventually(mut f: impl FnMut() -> bool) {
    let end = Instant::now() + Duration::from_secs(6);
    while !f() {
        assert!(Instant::now() < end, "eventually deadline");
        sleep(Duration::from_millis(10)).await;
    }
}
pub fn intent(c: &Config, command: &str, value: i16) -> field_flow::domain::Intent {
    let now = field_flow::domain::now_ms();
    Input {
        schema_version: 1,
        source_id: c.flows[0].source_id.clone(),
        ready: true,
        command_id: Some(command.into()),
        value: Some(value),
        issued_at_ms: Some(now),
        expires_at_ms: Some(now + 60000),
    }
    .intent(&c.flows[0], &c.plcs[0])
    .unwrap()
    .unwrap()
}
pub fn readback(offset: i32) -> [u8; 16] {
    use rust_snap7::{InternalParam as P, InternalParamValue as V, S7Client};
    let c = S7Client::create();
    c.set_param(P::RemotePort, V::U16(31102)).unwrap();
    c.connect_to("127.0.0.1", 0, 1).unwrap();
    let mut b = [0; 16];
    c.db_read(1, offset, 16, &mut b).unwrap();
    c.disconnect().unwrap();
    drop(c);
    b
}
