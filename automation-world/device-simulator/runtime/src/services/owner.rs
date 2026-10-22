//! 唯一image owner：协议/规则/UI逐item公平；锁内无SQL、socket或阻塞日志I/O。
use super::scheduler;
use crate::{
    domain::{
        image::{hex, Image},
        layout::CompiledInstance,
        policy,
        request::{Request, Source},
        result::ItemResult,
        rule, typed_value,
    },
    infrastructure::{clock, logging::Evidence},
};
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, BTreeSet, VecDeque},
    sync::{Arc, Condvar, Mutex},
    thread::{self, JoinHandle},
    time::Duration,
};
pub struct Job {
    pub request: Request,
    pub result: Mutex<Option<ItemResult>>,
    pub ready: Condvar,
}
struct State {
    image: Image,
    config: Arc<CompiledInstance>,
    queues: [VecDeque<Arc<Job>>; 3],
    running: bool,
    paused: bool,
    quit: bool,
    in_commit: bool,
    cancelled: BTreeSet<u64>,
    next_class: usize,
    last_connection: u64,
    pending: usize,
    rule_index: usize,
    next_tick: u64,
    simulated_ns: u64,
    anchor_ns: u64,
    generation: u64,
    #[cfg(feature = "test-automation")]
    barrier: u64,
    #[cfg(feature = "test-automation")]
    test_unconfirmed: bool,
}
#[derive(Clone)]
pub struct Captured {
    pub config: Arc<CompiledInstance>,
    pub epoch: u64,
    pub seq: u64,
    pub generation: u64,
    pub simulated_ns: u64,
    pub loaded_revision: String,
    pub values: BTreeMap<String, Value>,
}
pub struct Owner {
    state: Mutex<State>,
    wake: Condvar,
    thread: Mutex<Option<JoinHandle<()>>>,
    pub events: Evidence,
    pub instance: String,
}
impl Owner {
    pub fn new(
        config: Arc<CompiledInstance>,
        revision: String,
        events: Evidence,
    ) -> Result<Arc<Self>, String> {
        let instance = config.config.id.clone();
        let image = Image::new(&config, 1, 1, revision, Source::Initialize);
        let out = Arc::new(Self {
            state: Mutex::new(State {
                image,
                config,
                queues: std::array::from_fn(|_| VecDeque::new()),
                running: false,
                paused: false,
                quit: false,
                in_commit: false,
                cancelled: BTreeSet::new(),
                next_class: 0,
                last_connection: 0,
                pending: 0,
                rule_index: 0,
                next_tick: 0,
                simulated_ns: 0,
                anchor_ns: 0,
                generation: 0,
                #[cfg(feature = "test-automation")]
                barrier: 0,
                #[cfg(feature = "test-automation")]
                test_unconfirmed: false,
            }),
            wake: Condvar::new(),
            thread: Mutex::new(None),
            events,
            instance,
        });
        let owned = out.clone();
        *out.thread.lock().unwrap() = Some(
            thread::Builder::new()
                .name("ds-image-owner".into())
                .spawn(move || owned.run())
                .map_err(|_| "owner_thread")?,
        );
        Ok(out)
    }
    fn log(&self, mut event: Value) {
        event["instance"] = json!(self.instance);
        self.events.put(event)
    }
    pub fn epoch_revision(&self) -> (u64, u64) {
        let s = self.state.lock().unwrap();
        (s.image.epoch, s.image.revision)
    }
    pub fn loaded_revision(&self) -> String {
        self.state.lock().unwrap().image.loaded_revision.clone()
    }
    pub fn compiled(&self) -> Arc<CompiledInstance> {
        self.state.lock().unwrap().config.clone()
    }
    pub fn call(&self, mut request: Request) -> ItemResult {
        let class = match request.source {
            Source::Rule => 1,
            Source::Ui | Source::Maintenance => 2,
            _ => 0,
        };
        if request.admitted == 0 {
            request.admitted = clock::ns()
        }
        let job = Arc::new(Job {
            request,
            result: Mutex::new(None),
            ready: Condvar::new(),
        });
        {
            let mut s = self.state.lock().unwrap();
            if s.quit || s.queues[class].len() >= [64, 1, 4][class] {
                return ItemResult::default();
            }
            self.log(json!({"event":"enqueue_intent","connection":job.request.connection,"pdu":job.request.pdu,"item":job.request.item,"admitted_ns":job.request.admitted}));
            s.queues[class].push_back(job.clone());
            self.wake.notify_one();
        }
        let mut result = job.result.lock().unwrap();
        while result.is_none() {
            result = job.ready.wait(result).unwrap()
        }
        result.take().unwrap()
    }
    pub fn cancel(&self, id: u64) {
        self.state.lock().unwrap().cancelled.insert(id);
        self.wake.notify_all()
    }
    pub fn joined(&self, id: u64) {
        self.state.lock().unwrap().cancelled.remove(&id);
    }
    fn freeze(s: &mut State) {
        if s.running && !s.paused {
            s.simulated_ns = s
                .simulated_ns
                .saturating_add(clock::ns().saturating_sub(s.anchor_ns));
            s.anchor_ns = clock::ns();
        }
    }
    pub fn control(&self, command: &str, _arg: u64) -> bool {
        let mut s = self.state.lock().unwrap();
        match command {
            "start" => {
                if s.running {
                    return true;
                }
                s.running = true;
                s.paused = false;
                s.anchor_ns = clock::ns();
                s.next_tick = s.anchor_ns;
            }
            "stop" => {
                Self::freeze(&mut s);
                s.running = false;
                s.paused = false;
                s.pending = 0;
                for q in &mut s.queues {
                    for job in q.drain(..) {
                        *job.result.lock().unwrap() = Some(ItemResult::default());
                        job.ready.notify_one()
                    }
                }
            }
            "pause" => {
                if !s.running {
                    return false;
                }
                Self::freeze(&mut s);
                s.paused = true;
                s.pending = 0;
            }
            "resume" => {
                if !s.running || !s.paused {
                    return false;
                }
                s.paused = false;
                s.anchor_ns = clock::ns();
                s.next_tick = s.anchor_ns + 100_000_000;
            }
            "reset" => {
                if s.running || s.in_commit {
                    return false;
                }
                s.image = Image::new(
                    &s.config,
                    s.image.epoch + 1,
                    s.image.revision,
                    s.image.loaded_revision.clone(),
                    Source::Reset,
                );
                s.simulated_ns = 0;
                s.pending = 0;
                self.log(
                    json!({"event":"reset_image_commit","source":5,"epoch":s.image.epoch,"seq":0}),
                );
            }
            #[cfg(feature = "test-automation")]
            "barrier" => s.barrier = _arg,
            #[cfg(feature = "test-automation")]
            "release" => s.barrier = 0,
            _ => return false,
        }
        s.generation += 1;
        self.log(json!({"event":"control","command":command,"epoch":s.image.epoch,"generation":s.generation}));
        self.wake.notify_all();
        true
    }
    #[cfg(feature = "test-automation")]
    fn barrier<'a>(
        &self,
        mut s: std::sync::MutexGuard<'a, State>,
        r: &Request,
        phase: u64,
    ) -> std::sync::MutexGuard<'a, State> {
        if r.source == Source::Client && r.connection != 0 && s.barrier == phase {
            self.log(
                json!({"event":"barrier","phase":phase,"connection":r.connection,"pdu":r.pdu}),
            );
            let end = clock::ns() + 2_000_000_000;
            while s.barrier == phase
                && !s.quit
                && s.running
                && !s.cancelled.contains(&r.connection)
                && clock::ns() < end
            {
                s = self
                    .wake
                    .wait_timeout(s, Duration::from_millis(5))
                    .unwrap()
                    .0;
            }
        }
        s
    }
    fn apply<'a>(
        &self,
        mut s: std::sync::MutexGuard<'a, State>,
        r: &Request,
    ) -> (std::sync::MutexGuard<'a, State>, ItemResult) {
        let mut out = ItemResult::default();
        #[cfg(feature = "test-automation")]
        {
            s = self.barrier(s, r, 1);
        }
        if (r.source == Source::Initialize) == s.running
            || s.quit
            || clock::ns().saturating_sub(r.admitted) > 2_000_000_000
            || s.cancelled.contains(&r.connection)
            || r.epoch != s.image.epoch
            || r.revision != s.image.revision
            || r.source == Source::Reset
            || r.source == Source::Rule && s.paused
        {
            self.log(json!({"event":"item_rejected","connection":r.connection,"pdu":r.pdu,"item":r.item,"reason":"version_cancel_deadline"}));
            return (s, out);
        }
        #[cfg(feature = "test-automation")]
        if s.test_unconfirmed
            && r.source == Source::Client
            && r.db == 41
            && r.start < 60
            && r.start.saturating_add(r.size) > 56
        {
            self.log(json!({"event":"item_rejected","connection":r.connection,"pdu":r.pdu,"item":r.item,"reason":"test_unconfirmed_overlay"}));
            return (s, out);
        }
        let Some(access) = policy::validate(r, &s.image, &s.config) else {
            self.log(json!({"event":"item_rejected","connection":r.connection,"pdu":r.pdu,"item":r.item,"reason":"coverage_type_cas"}));
            return (s, out);
        };
        if r.source == Source::Read {
            out.data[..access.end - access.begin]
                .copy_from_slice(&s.image.dbs[&access.db].bytes[access.begin..access.end]);
            out.ok = true;
            out.seq = s.image.seq;
            return (s, out);
        }
        let current = &s.image.dbs[&access.db].bytes;
        if r.source == Source::Rule
            && if r.bit.is_some() {
                (current[access.begin] >> (r.start % 8)) & 1 == r.data[0]
            } else {
                current[access.begin..access.end] == r.data[..r.size]
            }
        {
            out.ok = true;
            out.seq = s.image.seq;
            return (s, out);
        }
        s.in_commit = true;
        self.log(
            json!({"event":"commit_begin","connection":r.connection,"pdu":r.pdu,"item":r.item}),
        );
        #[cfg(feature = "test-automation")]
        {
            s = self.barrier(s, r, 2);
        }
        // phase2既已取得提交权；stop等待同一临界区，取消不回滚已准入的原子item。
        s.image.seq += 1;
        out.seq = s.image.seq;
        out.ok = true;
        let now = clock::ns();
        let db = s.image.dbs.get_mut(&access.db).unwrap();
        if r.bit.is_some() {
            let mask = 1 << (r.start % 8);
            db.bytes[access.begin] =
                (db.bytes[access.begin] & !mask) | if r.data[0] != 0 { mask } else { 0 }
        } else {
            db.bytes[access.begin..access.end].copy_from_slice(&r.data[..r.size]);
        }
        for index in access.points {
            let point = &mut db.points[index];
            point.seq = out.seq;
            point.source = r.source;
            point.updated = now;
        }
        let committed = hex(&db.bytes[access.begin..access.end]);
        s.generation += 1;
        self.log(json!({"event":"commit","connection":r.connection,"pdu":r.pdu,"item":r.item,"source":r.source as i32,"epoch":s.image.epoch,"seq":out.seq,"db":access.db,"start":access.begin,"bytes":committed}));
        s.in_commit = false;
        #[cfg(feature = "test-automation")]
        {
            s = self.barrier(s, r, 3);
        }
        (s, out)
    }
    fn run(self: Arc<Self>) {
        let mut s = self.state.lock().unwrap();
        while !s.quit {
            let now = clock::ns();
            if s.running && !s.paused && now >= s.next_tick {
                let elapsed = (now - s.next_tick) / 100_000_000 + 1;
                let count = s.config.rule_points.len();
                let missed = (elapsed - 1) * count as u64 + s.pending as u64;
                s.pending = count;
                s.rule_index = 0;
                s.next_tick += elapsed * 100_000_000;
                s.generation += 1;
                self.log(json!({"event":"rule_cycle","bucket":s.simulated_ns.saturating_add(now.saturating_sub(s.anchor_ns))/100_000_000,"due":elapsed*count as u64,"missed":missed}));
            }
            let mut mask = 0;
            for c in 0..3 {
                if !s.queues[c].is_empty() || c == 1 && s.pending > 0 {
                    mask |= 1 << c
                }
            }
            let Some(class) = scheduler::class(mask, &mut s.next_class) else {
                s = self
                    .wake
                    .wait_timeout(s, Duration::from_millis(1))
                    .unwrap()
                    .0;
                continue;
            };
            let eligible = s.queues[class]
                .iter()
                .map(|j| j.request.connection)
                .collect::<Vec<_>>();
            let job = if class == 1 && s.queues[1].is_empty() {
                let (number, index) = s.config.rule_points[s.rule_index];
                s.rule_index += 1;
                s.pending -= 1;
                let point = &s.config.dbs[&number].points[index];
                let simulated = s
                    .simulated_ns
                    .saturating_add(now.saturating_sub(s.anchor_ns));
                let data = match rule::evaluate(
                    &point.config.data_type,
                    point.policy.rule.as_ref().unwrap(),
                    &self.instance,
                    &point.config.id,
                    simulated,
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        self.log(json!({"event":"rule_rejected","code":e}));
                        continue;
                    }
                };
                let mut r = Request {
                    source: Source::Rule,
                    db: number as i32,
                    start: if let Some(bit) = point.bit {
                        point.byte * 8 + bit as usize
                    } else {
                        point.byte
                    },
                    bit: point.bit,
                    size: point.width,
                    epoch: s.image.epoch,
                    revision: s.image.revision,
                    admitted: now,
                    ..Request::default()
                };
                r.data[..data.len()].copy_from_slice(&data);
                Arc::new(Job {
                    request: r,
                    result: Mutex::new(None),
                    ready: Condvar::new(),
                })
            } else if class == 0 {
                let mut last = s.last_connection;
                let job =
                    scheduler::connection(&mut s.queues[0], &mut last, |j| j.request.connection)
                        .unwrap();
                s.last_connection = last;
                job
            } else {
                s.queues[class].pop_front().unwrap()
            };
            self.log(json!({"event":"dispatch","class":class,"eligible_classes":mask,"eligible_connections":eligible,"connection":job.request.connection,"pdu":job.request.pdu,"wait_ms":clock::ns().saturating_sub(job.request.admitted) as f64/1e6}));
            let (next, result) = self.apply(s, &job.request);
            s = next;
            *job.result.lock().unwrap() = Some(result);
            job.ready.notify_one();
            drop(s);
            thread::yield_now();
            s = self.state.lock().unwrap();
        }
        for q in &mut s.queues {
            for job in q.drain(..) {
                *job.result.lock().unwrap() = Some(ItemResult::default());
                job.ready.notify_one()
            }
        }
        self.log(json!({"event":"rust_owner_execute_return"}));
    }
    pub fn capture(&self) -> Result<Captured, String> {
        let s = self.state.lock().unwrap();
        if s.running || s.in_commit || s.queues.iter().any(|q| !q.is_empty()) {
            return Err("instance_not_stopped".into());
        }
        let mut values = BTreeMap::new();
        for (number, db) in &s.config.dbs {
            for (index, p) in db.points.iter().enumerate() {
                values.insert(p.config.id.clone(), s.image.typed(*number, index, p)?);
            }
        }
        Ok(Captured {
            config: s.config.clone(),
            epoch: s.image.epoch,
            seq: s.image.seq,
            generation: s.generation,
            simulated_ns: s.simulated_ns,
            loaded_revision: s.image.loaded_revision.clone(),
            values,
        })
    }
    pub fn install(
        &self,
        expected: &Captured,
        config: Arc<CompiledInstance>,
        image: Image,
        simulated_ns: u64,
    ) -> Result<(), String> {
        let mut s = self.state.lock().unwrap();
        if s.running
            || s.in_commit
            || s.generation != expected.generation
            || s.image.epoch != expected.epoch
            || s.image.seq != expected.seq
        {
            return Err("apply_snapshot_stale".into());
        }
        s.image = image;
        s.config = config;
        s.simulated_ns = simulated_ns;
        s.pending = 0;
        s.generation += 1;
        self.wake.notify_all();
        Ok(())
    }
    pub fn values(&self, offset: usize, limit: usize) -> Value {
        let s = self.state.lock().unwrap();
        let rows=s.config.dbs.iter().flat_map(|(number,db)|db.points.iter().enumerate().map(move|(index,p)|(*number,index,p))).skip(offset).take(limit.min(100)).map(|(number,index,p)|{let state=&s.image.dbs[&number].points[index];json!({"pointId":p.config.id,"dbNumber":number,"byte":p.byte,"bit":p.bit,"name":p.config.name,"dataType":p.config.data_type,"value":s.image.typed(number,index,p).ok(),"pointSeq":state.seq.to_string(),"source":state.source as i32,"updatedNs":state.updated.to_string(),"effective":p.policy})}).collect::<Vec<_>>();
        json!({"instanceId":self.instance,"loadedRevision":s.image.loaded_revision,"epoch":s.image.epoch.to_string(),"seq":s.image.seq.to_string(),"rows":rows,"total":s.config.point_index.len(),"stale":false})
    }
    pub fn write_point(
        &self,
        point_id: &str,
        value: &Value,
        revision: &str,
        epoch: u64,
        point_seq: u64,
        maintenance: bool,
    ) -> Result<ItemResult, String> {
        let request = {
            let s = self.state.lock().unwrap();
            if s.image.loaded_revision != revision || s.image.epoch != epoch {
                return Err("value_cas_conflict".into());
            }
            let (number, index) = *s
                .config
                .point_index
                .get(point_id)
                .ok_or("point_not_found")?;
            let p = &s.config.dbs[&number].points[index];
            let data = typed_value::encode(&p.config.data_type, value)?;
            let mut r = Request {
                source: if maintenance {
                    Source::Maintenance
                } else {
                    Source::Ui
                },
                db: number as i32,
                start: if let Some(bit) = p.bit {
                    p.byte * 8 + bit as usize
                } else {
                    p.byte
                },
                bit: p.bit,
                size: p.width,
                cas: point_seq,
                epoch,
                revision: s.image.revision,
                ..Request::default()
            };
            r.data[..data.len()].copy_from_slice(&data);
            r
        };
        let result = self.call(request);
        if result.ok {
            Ok(result)
        } else {
            Err("value_rejected_or_cas_conflict".into())
        }
    }
    pub fn snapshot(&self) -> Value {
        let s = self.state.lock().unwrap();
        json!({"instanceId":self.instance,"protocolWaiting":s.queues[0].len(),"ruleWaiting":s.queues[1].len()+s.pending,"uiWaiting":s.queues[2].len(),"epoch":s.image.epoch.to_string(),"loadedRevision":s.image.loaded_revision,"seq":s.image.seq.to_string(),"generation":s.generation.to_string(),"simulatedNs":(s.simulated_ns+if s.running&&!s.paused{clock::ns().saturating_sub(s.anchor_ns)}else{0}).to_string(),"state":if s.running{if s.paused{"paused"}else{"running"}}else{"stopped"}})
    }
    #[cfg(feature = "test-automation")]
    pub fn test_overlay(&self, enabled: bool) -> bool {
        self.state.lock().unwrap().test_unconfirmed = enabled;
        true
    }
    #[cfg(feature = "test-automation")]
    pub fn test_budget(&self) -> Value {
        let s = self.state.lock().unwrap();
        json!({"instanceId":self.instance,"compiledAllocationUpper":s.config.allocation_upper,"ownerStateBytes":std::mem::size_of::<State>(),"ownerJobBytes":std::mem::size_of::<Job>(),"queueItemLimits":[64,1,4],"queueJobsUpper":69*std::mem::size_of::<Job>(),"singleOwnerCoverageScratchUpper":2048*std::mem::size_of::<usize>(),"dbCapacities":s.image.dbs.iter().map(|(n,db)|json!({"db":n,"bytesCapacity":db.bytes.capacity(),"pointCapacity":db.points.capacity(),"pointStateBytes":std::mem::size_of::<crate::domain::image::PointState>()})).collect::<Vec<_>>(),"configurationSqlPreviewLogReservation":288*1024*1024,"pendingEvidenceBytesUpper":8*1024*1024,"historyEvidenceBytesUpper":8*1024*1024,"appenderBytesUpper":128*131072})
    }
    #[cfg(feature = "test-automation")]
    pub fn test_snapshot(&self) -> Value {
        let s = self.state.lock().unwrap();
        let dbs=s.image.dbs.iter().map(|(number,db)|(number.to_string(),json!({"bytes":hex(&db.bytes),"sha256":crate::domain::configuration::hash_bytes(&db.bytes),"points":db.points.iter().map(|p|json!({"last_seq":p.seq,"source":p.source as i32,"updated_at":p.updated})).collect::<Vec<_>>()}))).collect::<serde_json::Map<_,_>>();
        let image = &s.image;
        let points=s.config.dbs.iter().flat_map(|(number,db)|db.points.iter().enumerate().map(move |(index,p)|{let state=&image.dbs[number].points[index];json!({"db":number,"id":p.config.id,"bit_address":p.byte*8+p.bit.unwrap_or(0)as usize,"last_seq":state.seq,"source":state.source as i32,"updated_at":state.updated})})).collect::<Vec<_>>();
        let simulated = s.simulated_ns
            + if s.running && !s.paused {
                clock::ns().saturating_sub(s.anchor_ns)
            } else {
                0
            };
        json!({"instance":self.instance,"epoch":s.image.epoch,"revision":s.image.revision,"seq":s.image.seq,"tick":simulated/100_000_000,"next_tick_ns":s.next_tick,"running":s.running,"protocol_waiting":s.queues[0].len(),"rule_waiting":s.queues[1].len()+s.pending,"ui_waiting":s.queues[2].len(),"image":s.image.dbs.get(&41).map(|d|hex(&d.bytes)),"marker":s.image.dbs.get(&57).map(|d|hex(&d.bytes)),"points":points,"dbs":dbs})
    }
    pub fn request_shutdown(&self) {
        let mut s = self.state.lock().unwrap();
        s.quit = true;
        s.running = false;
        s.pending = 0;
        self.wake.notify_all()
    }
    pub fn shutdown(&self) -> bool {
        self.request_shutdown();
        if let Some(h) = self.thread.lock().unwrap().take() {
            let ok = h.join().is_ok();
            self.log(json!({"event":"rust_join_return","ok":ok}));
            ok
        } else {
            true
        }
    }
}
