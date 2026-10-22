//! 文件：src/runtime.rs；独立flow调度、每PLC FIFO监督owner、停止与真实join。
use crate::{
    config::{Config, Plc},
    domain::{id, now_ms, Intent},
    driver_process::{Driver, Wire},
    infrastructure::{posix::Gate, state::State},
    Result,
};
use serde_json::json;
use std::{
    collections::HashMap,
    fs::File,
    path::{Path, PathBuf},
    sync::{
        atomic::{AtomicBool, AtomicU8, Ordering},
        Arc, Mutex,
    },
    time::Duration,
};
use tokio::{
    sync::{mpsc, oneshot, watch, Notify},
    task::JoinHandle,
    time::{timeout_at, Instant},
};
#[derive(Clone)]
pub struct Stop {
    pub stopped: Arc<AtomicBool>,
    notify: Arc<Notify>,
    at: Arc<Mutex<Option<Instant>>>,
    gates: Arc<Vec<Arc<Gate>>>,
}
impl Stop {
    pub fn new(gates: Vec<Arc<Gate>>) -> Self {
        Self {
            stopped: Arc::new(AtomicBool::new(false)),
            notify: Arc::new(Notify::new()),
            at: Arc::new(Mutex::new(None)),
            gates: Arc::new(gates),
        }
    }
    pub fn close(&self) -> Result<()> {
        self.stopped.store(true, Ordering::Release);
        let mut at = self.at.lock().unwrap();
        if at.is_none() {
            *at = Some(Instant::now())
        }
        drop(at);
        for g in self.gates.iter() {
            g.close()?;
        }
        self.notify.notify_waiters();
        Ok(())
    }
    pub async fn wait(&self) {
        let notified = self.notify.notified();
        tokio::pin!(notified);
        notified.as_mut().enable();
        if !self.stopped.load(Ordering::Acquire) {
            notified.await;
        }
    }
    fn deadline(&self, budget: u64) -> Instant {
        self.at.lock().unwrap().unwrap_or_else(Instant::now) + Duration::from_millis(budget)
    }
}
#[derive(Debug, Clone, serde::Serialize)]
pub struct OwnerHealth {
    pub state: String,
    pub generation: u64,
    pub pid: Option<u32>,
    pub queue_depth: usize,
    pub in_flight: u8,
}
#[derive(Debug, Clone, serde::Serialize)]
pub struct Sample {
    pub request_id: String,
    pub flow_id: String,
    pub generation: u64,
    pub pid: u32,
    pub value: i16,
    pub quality: String,
    pub sampled_at_ms: i64,
    pub write_ack: Option<crate::infrastructure::s7_int_pdu::ValidatedWriteAck>,
}
struct Request {
    flow: String,
    id: String,
    db: u16,
    offset: u32,
    intent: Option<Intent>,
    deadline: Instant,
    reply: oneshot::Sender<Result<Sample>>,
    phase: Arc<AtomicU8>,
}
#[derive(Clone)]
pub struct Owner {
    tx: mpsc::Sender<Request>,
    health: watch::Receiver<OwnerHealth>,
    plc: Plc,
    stop: Stop,
    state: State,
}
pub struct OwnerTask {
    join: JoinHandle<Result<()>>,
}
impl OwnerTask {
    pub async fn join(&mut self) -> Result<()> {
        (&mut self.join).await.map_err(|_| "owner_join")?
    }
}
impl Owner {
    pub fn spawn(
        plc: Plc,
        executable: PathBuf,
        gate: Arc<Gate>,
        lock: Arc<File>,
        state: State,
        stop: Stop,
        forced: Arc<AtomicBool>,
    ) -> (Self, OwnerTask) {
        let (tx, rx) = mpsc::channel(plc.queue_capacity);
        let (health, h) = watch::channel(OwnerHealth {
            state: "starting".into(),
            generation: 0,
            pid: None,
            queue_depth: 0,
            in_flight: 0,
        });
        let handle = Self {
            tx,
            health: h,
            plc: plc.clone(),
            stop: stop.clone(),
            state: state.clone(),
        };
        let join = tokio::spawn(owner_loop(
            plc, executable, gate, lock, state, stop, forced, rx, health,
        ));
        (handle, OwnerTask { join })
    }
    pub fn health(&self) -> OwnerHealth {
        let mut h = self.health.borrow().clone();
        h.queue_depth = self.tx.max_capacity() - self.tx.capacity();
        h
    }
    async fn ready(&self, deadline: Instant) -> Result<()> {
        let mut h = self.health.clone();
        let end = (Instant::now() + Duration::from_millis(self.plc.ready_wait_ms)).min(deadline);
        timeout_at(end, async {
            loop {
                if self.stop.stopped.load(Ordering::Acquire) {
                    return Err("canceled".into());
                }
                if h.borrow().state == "ready" {
                    return Ok(());
                }
                h.changed().await.map_err(|_| "owner_closed")?;
            }
        })
        .await
        .map_err(|_| "plc_unavailable")?
    }
    async fn request(
        &self,
        flow: &str,
        db: u16,
        offset: u32,
        intent: Option<Intent>,
        deadline: Instant,
    ) -> Result<Sample> {
        self.ready(deadline).await?;
        let end = (Instant::now() + Duration::from_millis(self.plc.queue_wait_ms)).min(deadline);
        let permit = timeout_at(end, self.tx.reserve())
            .await
            .map_err(|_| "queue_timeout")?
            .map_err(|_| "owner_closed")?;
        if self.stop.stopped.load(Ordering::Acquire) {
            return Err("canceled".into());
        }
        if deadline <= Instant::now() + Duration::from_millis(400) {
            return Err("expired".into());
        }
        let request_id = id();
        if let Some(i) = &intent {
            i.validate_time(now_ms())?;
            self.state.dispatch(i.clone(), request_id.clone()).await?;
        }
        let (reply, rx) = oneshot::channel();
        let phase = Arc::new(AtomicU8::new(0));
        permit.send(Request {
            flow: flow.into(),
            id: request_id,
            db,
            offset,
            intent,
            deadline,
            reply,
            phase: phase.clone(),
        });
        match timeout_at(deadline + Duration::from_millis(500), rx).await {
            Ok(reply) => reply.map_err(|_| "owner_closed")?,
            Err(_) => {
                if phase
                    .compare_exchange(0, 2, Ordering::AcqRel, Ordering::Acquire)
                    .is_ok()
                {
                    Err("expired".into())
                } else {
                    Err("driver_cleanup_incomplete".into())
                }
            }
        }
    }
    pub async fn read(&self, flow: &str, db: u16, offset: u32) -> Result<Sample> {
        self.request(
            flow,
            db,
            offset,
            None,
            Instant::now() + Duration::from_millis(self.plc.io_timeout_ms),
        )
        .await
    }
    pub async fn write(&self, i: Intent, deadline: Instant) -> Result<Sample> {
        let f = i.flow_id.clone();
        let db = i.target.db;
        let offset = i.target.offset;
        self.request(
            &f,
            db,
            offset,
            Some(i),
            deadline.min(Instant::now() + Duration::from_millis(self.plc.io_timeout_ms)),
        )
        .await
    }
}
async fn owner_loop(
    plc: Plc,
    executable: PathBuf,
    gate: Arc<Gate>,
    lock: Arc<File>,
    state: State,
    stop: Stop,
    forced: Arc<AtomicBool>,
    mut rx: mpsc::Receiver<Request>,
    health: watch::Sender<OwnerHealth>,
) -> Result<()> {
    let mut driver: Option<Driver> = None;
    let mut generation = 0;
    let mut failures = 0usize;
    let mut operation_failed = false;
    let update = |status: &str, driver: &Option<Driver>, generation: u64, in_flight| {
        health.send_replace(OwnerHealth {
            state: status.into(),
            generation,
            pid: driver.as_ref().map(|d| d.pid),
            queue_depth: 0,
            in_flight,
        });
    };
    while !stop.stopped.load(Ordering::Acquire) {
        if driver.is_none() {
            generation += 1;
            update("connecting", &driver, generation, 0);
            let _ = state
                .log(
                    "driver_spawn",
                    json!({"target_id":plc.id,"generation":generation}),
                )
                .await;
            match Driver::spawn(
                &executable,
                &plc,
                generation,
                gate.path.clone(),
                &lock,
                state.clone(),
            )
            .await
            {
                Ok(d) => {
                    let pid = d.pid;
                    driver = Some(d);
                    update("ready", &driver, generation, 0);
                    let _=state.log("driver_ready",json!({"target_id":plc.id,"generation":generation,"pid":pid,"result":"ok"})).await;
                }
                Err(e) => {
                    if e.starts_with("forced_driver_stop") {
                        forced.store(true, Ordering::Release);
                    }
                    operation_failed = true;
                    failures += 1;
                    update("recovering", &driver, generation, 0);
                    let delay = if failures % 5 == 0 {
                        10000
                    } else {
                        [250, 500, 1000, 2000][(failures - 1) % 5]
                    };
                    let _ = state
                        .log(
                            "owner_backoff",
                            json!({"target_id":plc.id,"error_key":e,"backoff_ms":delay}),
                        )
                        .await;
                    tokio::select! {_=stop.wait()=>{},_=tokio::time::sleep(Duration::from_millis(delay))=>{}}
                    continue;
                }
            }
        }
        let request = tokio::select! {_=stop.wait()=>None,r=rx.recv()=>r};
        let Some(r) = request else { break };
        if stop.stopped.load(Ordering::Acquire)
            || r.deadline <= Instant::now() + Duration::from_millis(400)
        {
            let _ = r.reply.send(Err(if stop.stopped.load(Ordering::Acquire) {
                "canceled"
            } else {
                "expired"
            }
            .into()));
            continue;
        }
        if let Some(i) = &r.intent {
            if !state.healthy.load(Ordering::Acquire) {
                let _ = r.reply.send(Err("canceled".into()));
                continue;
            }
            if i.validate_time(now_ms()).is_err() {
                let _ = r.reply.send(Err("expired".into()));
                continue;
            }
        }
        if r.phase
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Acquire)
            .is_err()
        {
            let _ = r.reply.send(Err("expired".into()));
            continue;
        }
        update("ready", &driver, generation, 1);
        let d = driver.as_mut().unwrap();
        let mut wire = Wire::new(
            if r.intent.is_some() { "write" } else { "read" },
            generation,
            &r.id,
        );
        wire.flow_id = r.flow.clone();
        wire.db = r.db;
        wire.offset = r.offset;
        wire.value = r.intent.as_ref().map(|i| i.value);
        wire.intent = r.intent.clone();
        let result = d.call(wire, &stop.stopped, r.deadline).await;
        let mut maintenance = false;
        let mut answer = match result {
            Ok((reply, started)) => {
                maintenance = reply.retire;
                if started && r.intent.is_some() {
                    let _=state.log("driver_call_started",json!({"flow_id":r.flow,"request_id":r.id,"generation":generation,"pid":d.pid})).await;
                }
                if reply.result == "ok" {
                    failures = 0;
                    Ok(Sample {
                        request_id: r.id.clone(),
                        flow_id: r.flow.clone(),
                        generation,
                        pid: d.pid,
                        value: reply
                            .sample
                            .or_else(|| r.intent.as_ref().map(|i| i.value))
                            .unwrap_or(0),
                        quality: "good".into(),
                        sampled_at_ms: now_ms(),
                        write_ack: reply.write_ack,
                    })
                } else {
                    Err(reply.result)
                }
            }
            Err(e) => {
                forced.store(true, Ordering::Release);
                let _=state.log("forced_driver_stop",json!({"target_id":plc.id,"request_id":r.id,"error_key":e,"result":"fault_cleanup","pid":d.pid})).await;
                if d.reaped {
                    let _ = state
                        .log(
                            "driver_process_reaped",
                            json!({"target_id":plc.id,"pid":d.pid,"result":"fault_cleanup"}),
                        )
                        .await;
                } else {
                    let _ = stop.close();
                }
                Err(e)
            }
        };
        let reconnect = answer
            .as_ref()
            .is_err_and(|e| !matches!(e.as_str(), "canceled" | "expired"));
        if reconnect {
            operation_failed = true;
        }
        if reconnect || maintenance {
            update("recovering", &driver, generation, 0);
            if let Some(mut old) = driver.take() {
                if !old.reaped {
                    if let Err(error) = old.close(r.deadline).await {
                        forced.store(true, Ordering::Release);
                        let _=state.log("forced_driver_stop",json!({"target_id":plc.id,"pid":old.pid,"result":"fault_cleanup","error_key":error})).await;
                    }
                }
                if old.reaped {
                    let _=state.log("driver_process_reaped",json!({"target_id":plc.id,"pid":old.pid,"result":if old.forced{"fault_cleanup"}else{"normal"}})).await;
                } else {
                    answer = Err("driver_cleanup_incomplete".into());
                    let _ = stop.close();
                }
            }
            failures += 1;
        } else {
            update("ready", &driver, generation, 0);
        }
        let _ = r.reply.send(answer);
        if reconnect {
            tokio::select! {_=stop.wait()=>{},_=tokio::time::sleep(Duration::from_millis(250))=>{}}
        }
    }
    update("stopping", &driver, generation, 0);
    rx.close();
    while let Some(r) = rx.recv().await {
        let _ = r.reply.send(Err("canceled".into()));
    }
    if let Some(mut d) = driver.take() {
        let end = stop.deadline(plc.connect_timeout_ms.max(plc.io_timeout_ms));
        if d.close(end).await.is_err() {
            forced.store(true, Ordering::Release);
            operation_failed = true;
            let _=state.log("forced_driver_stop",json!({"target_id":plc.id,"pid":d.pid,"result":"fault_cleanup","error_key":"stop_deadline"})).await;
        }
        if d.reaped {
            let _=state.log("driver_process_reaped",json!({"target_id":plc.id,"pid":d.pid,"result":if d.forced{"fault_cleanup"}else{"normal"}})).await;
        } else {
            operation_failed = true;
            let _ = state
                .log(
                    "driver_cleanup_incomplete",
                    json!({"target_id":plc.id,"pid":d.pid,"result":"blocked"}),
                )
                .await;
        }
    }
    update("stopped", &driver, generation, 0);
    if operation_failed {
        Err("owner_had_errors".into())
    } else {
        Ok(())
    }
}
#[derive(Debug, Clone, serde::Serialize)]
pub struct FlowHealth {
    pub state: String,
    pub last_iteration_ms: Option<i64>,
    pub last_success_ms: Option<i64>,
    pub consecutive_errors: u64,
    pub iterations: u64,
    pub in_flight: u8,
}
pub struct Runtime {
    pub stop: Stop,
    pub owners: HashMap<String, Owner>,
    owner_tasks: Vec<OwnerTask>,
    pub forced: Arc<AtomicBool>,
    pub flows: Arc<Mutex<HashMap<String, FlowHealth>>>,
    flow_tasks: Vec<JoinHandle<()>>,
    state: State,
    gates: Vec<PathBuf>,
}
impl Runtime {
    pub fn start(config: &Config, dir: &Path, executable: &Path, state: State) -> Result<Self> {
        let mut gates = Vec::new();
        for p in &config.plcs {
            gates.push(Arc::new(Gate::create(dir.join(format!(
                "gate-{}-{}",
                id(),
                p.id
            )))?));
        }
        state.register_gates(gates.clone());
        let paths = gates.iter().map(|g| g.path.clone()).collect();
        let stop = Stop::new(gates.clone());
        let forced = Arc::new(AtomicBool::new(false));
        let mut owners = HashMap::new();
        let mut owner_tasks = Vec::new();
        for (p, g) in config.plcs.iter().zip(gates) {
            let (o, t) = Owner::spawn(
                p.clone(),
                executable.to_owned(),
                g,
                state.lock.clone(),
                state.clone(),
                stop.clone(),
                forced.clone(),
            );
            owners.insert(p.id.clone(), o);
            owner_tasks.push(t);
        }
        Ok(Self {
            stop,
            owners,
            owner_tasks,
            forced,
            flows: Arc::new(Mutex::new(HashMap::new())),
            flow_tasks: Vec::new(),
            state,
            gates: paths,
        })
    }
    pub fn launch_flows(&mut self, config: &Config) -> Result<()> {
        let http = crate::services::Http::new(&config.http)?;
        for f in config.flows.clone() {
            let plc = config
                .plcs
                .iter()
                .find(|p| p.id == f.target.plc_id)
                .unwrap()
                .clone();
            let owner = self.owners[&plc.id].clone();
            let stop = self.stop.clone();
            let state = self.state.clone();
            let http = http.clone();
            let health = self.flows.clone();
            health.lock().unwrap().insert(
                f.id.clone(),
                FlowHealth {
                    state: "starting".into(),
                    last_iteration_ms: None,
                    last_success_ms: None,
                    consecutive_errors: 0,
                    iterations: 0,
                    in_flight: 0,
                },
            );
            self.flow_tasks.push(tokio::spawn(async move{let mut clock=crate::domain::Clock::default();let mut blocked=false;loop{if stop.stopped.load(Ordering::Acquire){break} {let mut h=health.lock().unwrap();let h=h.get_mut(&f.id).unwrap();h.in_flight=1;h.last_iteration_ms=Some(now_ms());h.iterations+=1;}
   let result=if blocked{Err("flow_blocked".into())}else{crate::app::demo01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await};
   let mut event=None;{let mut h=health.lock().unwrap();let h=h.get_mut(&f.id).unwrap();h.in_flight=0;match result{Ok(_)=>{h.consecutive_errors=0;h.last_success_ms=Some(now_ms());h.state="running".into();},Err(ref e)=>{h.consecutive_errors+=1;if matches!(e.as_str(),"identity_conflict"|"target_unknown"|"clock_invalid"|"audit_unhealthy"|"capacity_paused"){blocked=true;h.state="blocked".into();}else{h.state="recovering".into();}if h.consecutive_errors==1||blocked{event=Some(e.clone());}}}}
   if let Some(e)=event{let _=state.log("flow_health",json!({"flow_id":f.id,"error_key":e,"state":if blocked{"blocked"}else{"recovering"}})).await;}
   tokio::select!{_=stop.wait()=>break,_=tokio::time::sleep(Duration::from_millis(f.interval_ms))=>{}}
  }health.lock().unwrap().get_mut(&f.id).unwrap().state="stopped".into();}));
        }
        Ok(())
    }
    pub async fn health(&self) -> Result<()> {
        let flows = self.flows.lock().unwrap().clone();
        let owners: HashMap<_, _> = self.owners.iter().map(|(k, o)| (k, o.health())).collect();
        let store = self.state.snapshot().await?;
        self.state.log("health",json!({"flows":flows,"owners":owners,"store":store,"had_forced_driver_stop":self.forced.load(Ordering::Acquire)})).await
    }
    pub async fn shutdown(mut self, budget: u64) -> Result<()> {
        let mut failed = self.stop.close().is_err();
        if self
            .state
            .log("stop_gate_closed", json!({"result":"ok"}))
            .await
            .is_err()
        {
            failed = true;
        }
        let end = self.stop.deadline(budget);
        failed |= !self.state.healthy.load(Ordering::Acquire);
        for mut t in self.flow_tasks.drain(..) {
            match timeout_at(end, &mut t).await {
                Ok(Ok(())) => {}
                Ok(Err(_)) => failed = true,
                Err(_) => {
                    failed = true;
                    t.abort();
                    let _ = t.await;
                }
            }
        }
        self.owners.clear();
        for mut task in self.owner_tasks.drain(..) {
            match timeout_at(end, task.join()).await {
                Ok(Ok(())) => {}
                Ok(Err(_)) => failed = true,
                Err(_) => {
                    failed = true;
                    task.join.abort();
                    let _ = task.join.await;
                }
            }
        }
        let forced = self.forced.load(Ordering::Acquire);
        if forced || failed {
            self.state
                .log(
                    "shutdown_incomplete",
                    json!({"result":"fault_cleanup","had_forced_driver_stop":forced}),
                )
                .await?;
            return Err("runtime_fault".into());
        }
        self.state
            .log("runtime_tasks_joined", json!({"result":"normal"}))
            .await?;
        for g in self.gates {
            std::fs::remove_file(g).map_err(|_| "gate_cleanup")?;
        }
        Ok(())
    }
}
