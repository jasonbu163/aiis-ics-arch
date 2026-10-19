//! 本地runtime owner：每PLC唯一actor与串行控制，激活屏障、有限操作状态和显式退出。
use super::local_scheduler as scheduler;
use crate::{
    config::local_bootstrap::Bootstrap,
    domain::{local_configuration::*, local_runtime::*},
    infrastructure::{
        local_logging::LocalLog,
        local_profile_lock::ProfileLock,
        local_store::{StoreHandle, Stores},
        managed_s7::{ManagedS7, Transport},
    },
};
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, VecDeque},
    sync::{
        atomic::{AtomicBool, Ordering},
        mpsc::{self, SyncSender},
        Arc, Condvar, Mutex,
    },
    thread,
    time::{Duration, Instant},
};
#[derive(Clone)]
pub(crate) struct Loaded {
    pub revision: String,
    pub configuration: Configuration,
}
pub(crate) struct Gate {
    pub closed: bool,
    pub rounds: usize,
}
pub(crate) struct LocalEngine {
    pub storage: StoreHandle,
    pub migration_state: Mutex<crate::domain::yaml_migration::MigrationSummary>,
    pub bootstrap: Bootstrap,
    pub loaded: Mutex<Option<Loaded>>,
    pub states: Mutex<BTreeMap<String, PlcState>>,
    pub operations: Mutex<VecDeque<Operation>>,
    actors: Mutex<BTreeMap<String, Actor>>,
    pub gate: Mutex<Gate>,
    pub gate_changed: Condvar,
    pub activation: Mutex<()>,
    pub stopped: AtomicBool,
    pub log: Arc<LocalLog>,
    _lock: ProfileLock,
    pub active_io: Mutex<BTreeMap<String, (Instant, u64)>>,
    pub cached_snapshot: Mutex<Option<(Instant, Value)>>,
    pub import_preview: Mutex<
        Option<(
            String,
            String,
            crate::infrastructure::tia_source::ImportPreview,
            Instant,
        )>,
    >,
    pub offset_preview: Mutex<Option<(String, String, String, Instant)>>,
    #[cfg(any(test, feature = "local-validation"))]
    pub fixture: Option<Arc<crate::infrastructure::local_fixture::FixtureSet>>,
}
struct Actor {
    sender: SyncSender<Message>,
    join: Option<thread::JoinHandle<()>>,
}
pub(crate) enum Action {
    Connection(bool),
    Collection(bool),
    Test,
    Diagnose(String),
}
enum Message {
    Action(Action, String, String),
    Install(Loaded, SyncSender<LocalResult<()>>),
    Shutdown,
}
impl LocalEngine {
    pub fn open(bootstrap: Bootstrap) -> LocalResult<Arc<Self>> {
        let lock = ProfileLock::acquire(&bootstrap.profile)?;
        let dir = lock.profile.join("local-acquisition-v1");
        let mut stores = Stores::open(&dir)?;
        let migration_state =
            super::local_yaml_migration::startup(&mut stores, bootstrap.migration.as_ref());
        if !bootstrap.ignored_keys.is_empty() {
            stores.log.event(
                "retired_env_keys_ignored",
                "bootstrap",
                &bootstrap.ignored_keys.join(","),
            )?;
        }
        let view = stores.configuration()?;
        let loaded = if let Some(r) = view.active {
            Some(Loaded {
                configuration: stores.revision(&r)?,
                revision: r,
            })
        } else {
            None
        };
        let log = stores.log.clone();
        let storage = StoreHandle::start(stores);
        #[cfg(any(test, feature = "local-validation"))]
        let fixture = bootstrap
            .fixture
            .as_ref()
            .map(|p| crate::infrastructure::local_fixture::FixtureSet::load(p))
            .transpose()?;
        let engine = Arc::new(Self {
            storage,
            migration_state: Mutex::new(migration_state),
            bootstrap,
            loaded: Mutex::new(None),
            states: Mutex::new(BTreeMap::new()),
            operations: Mutex::new(VecDeque::new()),
            actors: Mutex::new(BTreeMap::new()),
            gate: Mutex::new(Gate {
                closed: true,
                rounds: 0,
            }),
            gate_changed: Condvar::new(),
            activation: Mutex::new(()),
            stopped: AtomicBool::new(false),
            log,
            _lock: lock,
            import_preview: Mutex::new(None),
            offset_preview: Mutex::new(None),
            active_io: Mutex::new(BTreeMap::new()),
            cached_snapshot: Mutex::new(None),
            #[cfg(any(test, feature = "local-validation"))]
            fixture,
        });
        if let Some(l) = loaded {
            engine.install(l)?;
        }
        engine.storage.call(false, |s| {
            s.recover_activation()?;
            if let Some((t, _)) = s.pending_activation()? {
                s.finish_activation(&t)?;
            }
            Ok(())
        })?;
        engine.gate.lock().unwrap().closed = false;
        engine.event("runtime_started", "instance", "stopped");
        Ok(engine)
    }
    fn io<T>(&self, id: &str, deadline: u64, work: impl FnOnce() -> T) -> T {
        self.active_io
            .lock()
            .unwrap()
            .insert(id.into(), (Instant::now(), deadline));
        let result = work();
        self.active_io.lock().unwrap().remove(id);
        result
    }
    pub fn event(&self, event: &str, resource: &str, result: &str) {
        if let Err(e) = self.log.event(event, resource, result) {
            self.gate.lock().unwrap().closed = true;
            tracing::error!(event = "local_log_failed", error_code = e);
        }
        let (e, r, v) = (event.to_string(), resource.to_string(), result.to_string());
        let _ = self.storage.call(false, move |s| s.event(&e, &r, &v));
    }
    pub fn install(self: &Arc<Self>, loaded: Loaded) -> LocalResult<()> {
        if !validate(&loaded.configuration).is_empty() {
            return Err("configuration_invalid".into());
        }
        // Fixture coverage is checked only when this PLC is explicitly connected.
        // Activation installs stopped actors; unknown fixture endpoints never select real transport.
        let mut actors = self.actors.lock().unwrap();
        let remove: Vec<_> = actors
            .keys()
            .filter(|id| !loaded.configuration.plcs.iter().any(|p| &p.id == *id))
            .cloned()
            .collect();
        for id in remove {
            if let Some(mut a) = actors.remove(&id) {
                let _ = a.sender.send(Message::Shutdown);
                if let Some(j) = a.join.take() {
                    let _ = j.join();
                }
            }
            self.states.lock().unwrap().remove(&id);
        }
        for plc in &loaded.configuration.plcs {
            if let Some(a) = actors.get(&plc.id) {
                let (tx, rx) = mpsc::sync_channel(1);
                a.sender
                    .send(Message::Install(loaded.clone(), tx))
                    .map_err(|_| "actor_stopped")?;
                rx.recv_timeout(Duration::from_secs(7))
                    .map_err(|_| "activation_pending")??;
            } else {
                let (tx, rx) = mpsc::sync_channel(4);
                let engine = self.clone();
                let id = plc.id.clone();
                let l = loaded.clone();
                self.states
                    .lock()
                    .unwrap()
                    .insert(id.clone(), PlcState::new(&id));
                let j = thread::spawn(move || actor_loop(engine, id, l, rx));
                actors.insert(
                    plc.id.clone(),
                    Actor {
                        sender: tx,
                        join: Some(j),
                    },
                );
            }
        }
        *self.loaded.lock().unwrap() = Some(loaded);
        Ok(())
    }
    pub fn request(
        &self,
        ids: Vec<String>,
        action: &str,
        desired: bool,
        revision: &str,
        point: Option<String>,
    ) -> LocalResult<Value> {
        let loaded = self
            .loaded
            .lock()
            .unwrap()
            .clone()
            .ok_or("active_missing")?;
        if loaded.revision != revision {
            return Err("revision_conflict".into());
        }
        if ids.is_empty()
            || ids.len() > 4
            || ids.iter().collect::<std::collections::BTreeSet<_>>().len() != ids.len()
        {
            return Err("target_ids_invalid".into());
        }
        if self.gate.lock().unwrap().closed
            && !((action == "connection" || action == "collection") && !desired)
        {
            return Err("activation_pending".into());
        }
        if !((action == "connection" || action == "collection") && !desired) {
            self.log.health()?;
        }
        let actors = self.actors.lock().unwrap();
        let mut result = vec![];
        for target in ids {
            let op = id();
            let message = match action {
                "connection" => Action::Connection(desired),
                "collection" => Action::Collection(desired),
                "test" => Action::Test,
                "diagnose" => Action::Diagnose(point.clone().ok_or("point_missing")?),
                _ => return Err("operation_invalid".into()),
            };
            let mut operation = Operation {
                operation_id: op.clone(),
                plc_id: target.clone(),
                action: action.into(),
                phase: "pending".into(),
                reason: None,
                result: None,
            };
            self.push_operation(operation.clone());
            let phase = if let Some(a) = actors.get(&target) {
                if a.sender
                    .try_send(Message::Action(message, op, revision.to_string()))
                    .is_ok()
                {
                    "pending"
                } else {
                    "blocked"
                }
            } else {
                "failed"
            };
            if phase != "pending" {
                operation.phase = phase.into();
                operation.reason = Some("actor_busy_or_missing".into());
                self.push_operation(operation.clone());
            }
            result.push(operation);
        }
        Ok(json!({"schemaVersion":1,"items":result}))
    }
    fn push_operation(&self, op: Operation) {
        let mut list = self.operations.lock().unwrap();
        if let Some(old) = list.iter_mut().find(|o| o.operation_id == op.operation_id) {
            *old = op
        } else {
            while list.len() >= 64 {
                list.pop_front();
            }
            list.push_back(op)
        }
    }
    fn complete(&self, operation: &str, result: LocalResult<Value>) {
        let op = self
            .operations
            .lock()
            .unwrap()
            .iter()
            .find(|o| o.operation_id == operation)
            .cloned();
        if let Some(mut op) = op {
            match result {
                Ok(v) => {
                    op.phase = "applied".into();
                    op.result = Some(v)
                }
                Err(e) => {
                    op.phase = "failed".into();
                    op.reason = Some(e)
                }
            }
            self.event("operation_completed", &op.plc_id, &op.phase);
            self.push_operation(op)
        }
    }
    pub fn shutdown(&self) {
        if self.stopped.swap(true, Ordering::SeqCst) {
            return;
        }
        self.gate.lock().unwrap().closed = true;
        let mut actors = self.actors.lock().unwrap();
        for a in actors.values() {
            let _ = a.sender.send(Message::Shutdown);
        }
        for a in actors.values_mut() {
            if let Some(j) = a.join.take() {
                let _ = j.join();
            }
        }
        actors.clear();
        self.event("runtime_stopped", "instance", "clean");
        self.storage.shutdown();
    }
    fn transport(&self) -> Box<dyn Transport> {
        #[cfg(any(test, feature = "local-validation"))]
        if let Some(f) = &self.fixture {
            return Box::new(crate::infrastructure::local_fixture::FixtureTransport::new(
                f.clone(),
            ));
        }
        Box::new(ManagedS7::new())
    }
}
fn actor_loop(
    engine: Arc<LocalEngine>,
    id: String,
    mut loaded: Loaded,
    rx: mpsc::Receiver<Message>,
) {
    let mut transport = engine.transport();
    let mut plc = loaded
        .configuration
        .plcs
        .iter()
        .find(|p| p.id == id)
        .unwrap()
        .clone();
    let mut groups = scheduler::schedules(&loaded.configuration, &id);
    let mut state = PlcState::new(&id);
    state.groups = scheduler::states(&groups);
    let mut last_diag = Instant::now() - Duration::from_secs(1);
    let mut reconnect = Instant::now();
    let mut attempt = 0u32;
    let mut capacity_paused = false;
    let mut storage_fault = false;
    let mut probe_due = Instant::now();
    loop {
        if engine.stopped.load(Ordering::SeqCst) {
            break;
        }
        let message = rx.try_recv().ok();
        if let Some(Message::Shutdown) = message {
            break;
        }
        if let Some(Message::Install(new, reply)) = message {
            let p = new.configuration.plcs.iter().find(|p| p.id == id).cloned();
            if let Some(p) = p {
                if p.endpoint() != plc.endpoint() || !p.enabled {
                    transport.disconnect();
                    state.connected = false;
                }
                plc = p;
                loaded = new;
                groups = scheduler::schedules(&loaded.configuration, &id);
                state.groups = scheduler::states(&groups);
                if !plc.enabled {
                    state.phase = "disconnected".into();
                    state.admission = "read_gate_closed".into();
                } else if groups.is_empty() {
                    state.phase = if state.connected {
                        "connected"
                    } else {
                        "disconnected"
                    }
                    .into();
                    state.admission = "members_missing".into();
                }
                engine
                    .states
                    .lock()
                    .unwrap()
                    .insert(id.clone(), state.clone());
                reconnect = Instant::now();
                let _ = reply.send(Ok(()));
            } else {
                let _ = reply.send(Err("plc_missing".into()));
            }
            continue;
        }
        // Give due acquisition a turn before each diagnostic; groups retain independent monotonic due times.
        if state.connected
            && state.desired_collection
            && plc.enabled
            && engine.bootstrap.read_allowed
        {
            let eligible = {
                let mut gate = engine.gate.lock().unwrap();
                if gate.closed || engine.log.health().is_err() {
                    false
                } else {
                    gate.rounds += 1;
                    true
                }
            };
            if eligible {
                if let Some(i) = scheduler::due(&groups, Instant::now()) {
                    let quota = loaded.configuration.storage.quota_bytes;
                    let cap = engine.storage.call(true, move |s| s.capacity(quota));
                    let allowed = cap
                        .as_ref()
                        .map(|c| {
                            crate::infrastructure::local_store::capacity::admit(
                                c,
                                quota,
                                capacity_paused,
                            )
                        })
                        .unwrap_or(false);
                    let healthy = if !allowed {
                        false
                    } else if storage_fault {
                        if Instant::now() < probe_due {
                            false
                        } else {
                            probe_due = Instant::now() + Duration::from_secs(1);
                            let result = engine.storage.call(false, |s| {
                                s.event("storage_health_probe", "instance", "committed")
                            });
                            if result.is_ok() {
                                storage_fault = false;
                            }
                            result.is_ok()
                        }
                    } else {
                        true
                    };
                    if allowed && healthy {
                        capacity_paused = false;
                        let begin = Instant::now();
                        state.phase = "collecting".into();
                        state.admission = "ready".into();
                        engine
                            .states
                            .lock()
                            .unwrap()
                            .insert(id.clone(), state.clone());
                        let origin = if engine.bootstrap.validation {
                            "fixture"
                        } else {
                            "s7"
                        };
                        let result = engine
                            .io(&id, u64::from(plc.deadline_ms), || {
                                scheduler::collect(
                                    &loaded.configuration,
                                    &plc,
                                    &groups[i].group,
                                    &loaded.revision,
                                    &mut *transport,
                                    origin,
                                )
                            })
                            .and_then(|cycle| {
                                engine.storage.call(false, move |s| s.commit_cycle(cycle))
                            });
                        match result {
                            Ok(_) => {
                                state.saved_cycles += 1;
                                state.used_revision = Some(loaded.revision.clone());
                                state.error = None;
                            }
                            Err(e) => {
                                state.error = Some(e.clone());
                                state.admission = "storage_fault".into();
                                storage_fault = true;
                                probe_due = Instant::now() + Duration::from_secs(1);
                                capacity_paused = true;
                                engine.event("cycle_failed", &id, &e);
                            }
                        }
                        scheduler::finish(&mut groups[i], begin, Instant::now());
                        state.groups = scheduler::states(&groups);
                    } else {
                        if !capacity_paused {
                            engine.event("capacity_paused", &id, "admission_closed");
                        }
                        capacity_paused = true;
                        state.admission = if storage_fault {
                            "storage_fault"
                        } else {
                            "capacity_paused"
                        }
                        .into();
                        let at = Instant::now();
                        scheduler::finish(&mut groups[i], at, at);
                        state.groups = scheduler::states(&groups);
                    }
                }
                let mut gate = engine.gate.lock().unwrap();
                gate.rounds -= 1;
                engine.gate_changed.notify_all();
            }
        }
        if let Some(Message::Action(action, operation, expected_revision)) = message {
            let result = (|| -> LocalResult<Value> {
                if expected_revision != loaded.revision {
                    return Err("revision_conflict".into());
                }
                match action {
                    Action::Connection(want) => {
                        state.desired_connection = want;
                        if !want {
                            state.phase = "disconnecting".into();
                            engine
                                .states
                                .lock()
                                .unwrap()
                                .insert(id.clone(), state.clone());
                            transport.disconnect();
                            state.connected = false;
                            state.phase = "disconnected".into();
                            state.admission = "disconnected".into();
                            attempt = 0;
                            return Ok(json!({"connected":false}));
                        }
                        if !plc.enabled || !engine.bootstrap.read_allowed {
                            return Err("read_gate_closed".into());
                        }
                        if !state.connected {
                            state.phase = "connecting".into();
                            engine
                                .states
                                .lock()
                                .unwrap()
                                .insert(id.clone(), state.clone());
                            engine.io(&id, 1000, || transport.connect(&plc))?;
                            state.connected = true;
                            attempt = 0;
                        }
                        state.phase = "connected".into();
                        Ok(json!({"connected":true}))
                    }
                    Action::Collection(want) => {
                        if want {
                            if !state.connected {
                                return Err("connection_required".into());
                            }
                            if !plc.enabled
                                || !engine.bootstrap.read_allowed
                                || engine.gate.lock().unwrap().closed
                            {
                                return Err("admission_closed".into());
                            }
                            if !groups.iter().any(|g| {
                                loaded.configuration.points.iter().any(|p| {
                                    p.enabled && p.group_id.as_deref() == Some(&g.group.id)
                                })
                            }) {
                                return Err("members_missing".into());
                            }
                        }
                        if want {
                            let quota = loaded.configuration.storage.quota_bytes;
                            let cap = engine.storage.call(true, move |s| s.capacity(quota))?;
                            if storage_fault {
                                return Err("storage_fault".into());
                            }
                            if !crate::infrastructure::local_store::capacity::admit(
                                &cap,
                                quota,
                                capacity_paused,
                            ) {
                                return Err("capacity_paused".into());
                            }
                        }
                        state.desired_collection = want;
                        state.phase = if want {
                            "collecting"
                        } else if state.connected {
                            "connected"
                        } else {
                            "disconnected"
                        }
                        .into();
                        state.admission = if want { "ready" } else { "stopped" }.into();
                        Ok(json!({"desiredCollection":want}))
                    }
                    Action::Test => {
                        if last_diag.elapsed() < Duration::from_secs(1) {
                            return Err("diagnostic_rate_limited".into());
                        }
                        last_diag = Instant::now();
                        if !plc.enabled || !engine.bootstrap.read_allowed {
                            return Err("read_gate_closed".into());
                        }
                        let original = state.desired_connection;
                        let was_connected = state.connected;
                        let result = if was_connected {
                            Ok(())
                        } else {
                            engine.io(&id, 1000, || transport.connect(&plc))
                        };
                        if !was_connected {
                            transport.disconnect();
                        }
                        Ok(
                            json!({"testId":operation,"testedAt":crate::domain::local_sample::now(),"success":result.is_ok(),"reason":result.err(),"originalDesiredConnection":original,"restorationPhase":"applied","connected":was_connected}),
                        )
                    }
                    Action::Diagnose(point) => {
                        if last_diag.elapsed() < Duration::from_secs(1) {
                            return Err("diagnostic_rate_limited".into());
                        }
                        last_diag = Instant::now();
                        if !state.connected || !engine.bootstrap.read_allowed {
                            return Err("connection_required".into());
                        }
                        let mut c = loaded.configuration.clone();
                        let p = c
                            .points
                            .iter_mut()
                            .find(|p| p.id == point && p.plc_id == id)
                            .ok_or("point_missing")?;
                        if !p.address.as_ref().map(|a| a.confirmed).unwrap_or(false) {
                            return Err("address_required".into());
                        }
                        let g = Group {
                            id: crate::domain::local_configuration::id(),
                            plc_id: id.clone(),
                            name: "diagnostic".into(),
                            enabled: true,
                            interval_ms: 1000,
                        };
                        p.group_id = Some(g.id.clone());
                        p.enabled = true;
                        c.points.retain(|p| p.id == point);
                        let data = scheduler::collect(
                            &c,
                            &plc,
                            &g,
                            &loaded.revision,
                            &mut *transport,
                            if engine.bootstrap.validation {
                                "fixture"
                            } else {
                                "s7"
                            },
                        )?;
                        Ok(
                            json!({"diagnosticId":operation,"revision":loaded.revision,"points":data.points,"testedAt":data.finished_at}),
                        )
                    }
                }
            })();
            if let Err(e) = &result {
                state.error = Some(e.clone());
                if state.desired_connection && !state.connected {
                    reconnect = Instant::now() + Duration::from_secs(1);
                }
            }
            engine.complete(&operation, result);
        }
        if state.connected && !transport.connected() {
            transport.disconnect();
            state.connected = false;
            state.phase = "reconnecting".into();
            state.admission = "disconnected".into();
            state.error = Some("transport_disconnected".into());
            reconnect = Instant::now() + Duration::from_secs(1);
            attempt = 1;
            engine.event("connection_lost", &id, "disconnected");
        }
        if state.desired_connection
            && !state.connected
            && plc.enabled
            && engine.bootstrap.read_allowed
            && Instant::now() >= reconnect
            && !engine.gate.lock().unwrap().closed
        {
            match engine.io(&id, 1000, || transport.connect(&plc)) {
                Ok(()) => {
                    state.connected = true;
                    state.phase = "connected".into();
                    state.error = None;
                    attempt = 0;
                    engine.event("connection_restored", &id, "connected")
                }
                Err(e) => {
                    state.error = Some(e);
                    state.phase = "reconnecting".into();
                    let seconds = (1u64 << attempt.min(5)).min(30);
                    let jitter = (uuid::Uuid::new_v4().as_u128() % 201) as u64;
                    reconnect =
                        Instant::now() + Duration::from_millis(seconds * 1000 + seconds * jitter);
                    attempt += 1;
                }
            }
        }
        engine
            .states
            .lock()
            .unwrap()
            .insert(id.clone(), state.clone());
        thread::sleep(Duration::from_millis(5));
    }
    transport.disconnect();
    state.connected = false;
    state.phase = "stopped".into();
    engine.states.lock().unwrap().insert(id, state);
}
