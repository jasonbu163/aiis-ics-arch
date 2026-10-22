//! DS运行时职责：Rust transport admission and lifecycle truth; native only performs protocol and real joins.
use crate::{
    domain::{
        image::hex,
        request::{Request, Source},
    },
    infrastructure::{
        clock,
        native_ffi::{self, Descriptor, Handle},
    },
    services::owner::{Job, Owner},
};
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, BTreeSet},
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    time::Duration,
};
/// 主进程固定宿主预留替换而非叠加：含SQL/日志/采样/控制，owner/listener/reaper/TCP另计。
/// Desktop40覆盖Tauri主进程已观测空profile28/峰36并留余量；不包含外部XPC/WK服务。
pub const HEADLESS_FIXED_THREADS: usize = 12;
pub const DESKTOP_FIXED_THREADS: usize = 40;
pub struct Global {
    pub fixed_threads: usize,
    pub tcp: usize,
    pub h: usize,
    pub c: usize,
    pub bytes: usize,
    pub owners: usize,
    pub listeners: usize,
}
impl Default for Global {
    fn default() -> Self {
        Self {
            fixed_threads: HEADLESS_FIXED_THREADS,
            tcp: 0,
            h: 0,
            c: 0,
            bytes: 0,
            owners: 0,
            listeners: 0,
        }
    }
}
pub struct Connection {
    pub fd: i32,
    pub peer_port: u16,
    pub established: bool,
    pub closing: bool,
    pub inflight: bool,
    pub reason: i32,
    pub pdu: u64,
    pub epoch: u64,
    pub revision: u64,
    pub accepted: u64,
    pub established_at: u64,
    pub last_recv: u64,
    pub last_send: u64,
    pub admitted: u64,
    pub count: usize,
    pub refs: usize,
    pub desc: [Descriptor; 4],
}
pub struct Transport {
    pub next: u64,
    pub tokens: BTreeSet<u64>,
    pub connections: BTreeMap<u64, Connection>,
    pub c: usize,
    pub h: usize,
    pub base: usize,
    pub fixed: usize,
    pub budgets: [usize; 3],
}
pub struct Context {
    pub owner: Arc<Owner>,
    pub transport: Mutex<Transport>,
    pub global: Arc<Mutex<Global>>,
    pub gate: AtomicBool,
}
impl Context {
    pub fn event(&self, mut v: Value) {
        v["instance"] = json!(self.owner.instance.to_string());
        self.owner.events.put(v)
    }
    pub fn reserve(&self) -> Option<u64> {
        let mut t = self.transport.lock().unwrap();
        let h = t.tokens.len() + t.connections.values().filter(|c| !c.established).count();
        if !self.gate.load(Ordering::SeqCst)
            || h >= t.h
            || t.connections.len() + t.tokens.len() >= t.c + t.h
        {
            return None;
        }
        let mut g = self.global.lock().unwrap();
        if g.h >= 32
            || g.fixed_threads + g.owners + g.listeners * 2 + g.tcp + 1 > 64
            || g.tcp >= 160
            || t.base > t.budgets[0]
            || t.fixed + (t.connections.len() + t.tokens.len() + 1) * t.base > t.budgets[1]
            || g.bytes + t.base > t.budgets[2]
        {
            self.event(json!({"event":"accept_rejected","reason":"budget_or_capacity"}));
            return None;
        }
        t.next += 1;
        let token = t.next;
        t.tokens.insert(token);
        g.tcp += 1;
        g.h += 1;
        g.bytes += t.base;
        Some(token)
    }
    pub fn cancel(&self, token: u64) {
        let mut t = self.transport.lock().unwrap();
        if t.tokens.remove(&token) {
            let mut g = self.global.lock().unwrap();
            g.tcp -= 1;
            g.h -= 1;
            g.bytes -= t.base;
            self.event(json!({"event":"accept_cancel","token":token}))
        }
    }
    pub fn accepted(&self, token: u64, fd: i32) -> Option<u64> {
        let mut t = self.transport.lock().unwrap();
        if !t.tokens.remove(&token) {
            return None;
        }
        let (er, rev) = self.owner.epoch_revision();
        let mut addr: libc::sockaddr_in = unsafe { std::mem::zeroed() };
        let mut len = std::mem::size_of_val(&addr) as u32;
        let mut snd = 8192i32;
        let mut rcv = 8192i32;
        unsafe {
            libc::getpeername(fd, &mut addr as *mut _ as *mut _, &mut len);
            let one = 1i32;
            libc::setsockopt(
                fd,
                libc::SOL_SOCKET,
                libc::SO_NOSIGPIPE,
                &one as *const _ as *const _,
                4,
            );
            libc::setsockopt(
                fd,
                libc::SOL_SOCKET,
                libc::SO_SNDBUF,
                &snd as *const _ as *const _,
                4,
            );
            libc::setsockopt(
                fd,
                libc::SOL_SOCKET,
                libc::SO_RCVBUF,
                &rcv as *const _ as *const _,
                4,
            );
            let mut n = 4;
            libc::getsockopt(
                fd,
                libc::SOL_SOCKET,
                libc::SO_SNDBUF,
                &mut snd as *mut _ as *mut _,
                &mut n,
            );
            libc::getsockopt(
                fd,
                libc::SOL_SOCKET,
                libc::SO_RCVBUF,
                &mut rcv as *mut _ as *mut _,
                &mut n,
            );
        }
        let now = clock::ns();
        let port = u16::from_be(addr.sin_port);
        t.connections.insert(
            token,
            Connection {
                fd,
                peer_port: port,
                established: false,
                closing: false,
                inflight: false,
                reason: 0,
                pdu: 0,
                epoch: er,
                revision: rev,
                accepted: now,
                established_at: 0,
                last_recv: 0,
                last_send: 0,
                admitted: 0,
                count: 0,
                refs: 0,
                desc: [Descriptor::default(); 4],
            },
        );
        self.event(json!({"event":"accepted","connection":token,"fd":fd,"peer_port":port,"accepted_ns":now,"sndbuf":snd,"rcvbuf":rcv}));
        Some(token)
    }
    pub fn active(&self, id: u64) -> bool {
        let t = self.transport.lock().unwrap();
        self.gate.load(Ordering::SeqCst)
            && t.connections
                .get(&id)
                .map(|c| {
                    !c.closing
                        && (c.established || clock::ns().saturating_sub(c.accepted) < 5_000_000_000)
                })
                .unwrap_or(false)
    }
    pub fn cotp(&self, id: u64, data: &[u8]) -> bool {
        let (mut calling, mut called) = (None, None);
        let mut k = 11;
        if data.len() < 11 || data.len() > 512 {
            return false;
        }
        while k + 2 <= data.len() {
            let ty = data[k];
            let n = data[k + 1] as usize;
            if k + 2 + n > data.len() {
                return false;
            }
            if n == 2 {
                let v = u16::from_be_bytes([data[k + 2], data[k + 3]]);
                if ty == 0xc1 {
                    calling = Some(v)
                }
                if ty == 0xc2 {
                    called = Some(v)
                }
            }
            k += 2 + n
        }
        let config = self.owner.compiled();
        let ok = calling == Some(config.config.calling_tsap)
            && called == Some(config.config.called_tsap());
        self.event(
            json!({"event":"cotp","connection":id,"calling":calling,"called":called,"ok":ok}),
        );
        ok
    }
    pub fn setup(&self, id: u64) -> bool {
        let mut t = self.transport.lock().unwrap();
        if !self.gate.load(Ordering::SeqCst)
            || t.connections.values().filter(|c| c.established).count() >= t.c
        {
            return false;
        }
        let Some(c) = t.connections.get_mut(&id) else {
            return false;
        };
        if c.established {
            return false;
        }
        let mut g = self.global.lock().unwrap();
        if g.c >= 128 {
            return false;
        }
        g.c += 1;
        g.h -= 1;
        c.established = true;
        c.established_at = clock::ns();
        c.last_recv = c.established_at;
        self.event(json!({"event":"established","connection":id}));
        true
    }
    pub fn begin(&self, id: u64, data: &[u8]) -> Option<u64> {
        let (desc, count) = native_ffi::parse_pdu(data)?;
        let mut t = self.transport.lock().unwrap();
        let base = t.base;
        if base > t.budgets[0]
            || t.fixed + (t.connections.len() + t.tokens.len()) * base > t.budgets[1]
            || self.global.lock().unwrap().bytes > t.budgets[2]
        {
            self.event(json!({"event":"pdu_rejected","connection":id,"reason":"whole_pdu_budget","item0_executed":false}));
            return None;
        }
        if !self.gate.load(Ordering::SeqCst) {
            return None;
        }
        let c = t.connections.get_mut(&id)?;
        if c.inflight || c.closing {
            return None;
        }
        let mut pending = 0;
        unsafe {
            libc::ioctl(c.fd, libc::FIONREAD, &mut pending);
        }
        if pending > 0 {
            self.event(json!({"event":"inflight_rejected","connection":id}));
            return None;
        }
        c.inflight = true;
        c.pdu += 1;
        c.admitted = clock::ns();
        c.last_recv = c.admitted;
        c.count = count;
        c.desc = desc;
        let pdu = c.pdu;
        self.event(json!({"event":"pdu_reserved","connection":id,"pdu":pdu,"items":count,"q":2208,"admitted_ns":c.admitted}));
        Some(pdu)
    }
    pub fn item(
        &self,
        id: u64,
        pdu: u64,
        index: u32,
        op: i32,
        tag: native_ffi::Tag,
        data: &mut [u8],
    ) -> bool {
        let (d, admitted, epoch, revision) = {
            let mut t = self.transport.lock().unwrap();
            let Some(c) = t.connections.get_mut(&id) else {
                return false;
            };
            if !c.inflight || c.pdu != pdu || index as usize >= c.count {
                return false;
            }
            let d = c.desc[index as usize];
            if d.area != 0x84
                || tag.area != d.area
                || tag.db != d.db
                || tag.count != d.count
                || tag.wordlen != d.wordlen
                || tag.start != if d.wordlen == 1 { d.raw } else { d.raw / 8 }
                || data.len() != d.bytes as usize
            {
                return false;
            }
            c.refs += 1;
            (d, c.admitted, c.epoch, c.revision)
        };
        let mut r = Request {
            connection: id,
            pdu,
            item: index,
            admitted,
            epoch,
            revision,
            db: d.db,
            start: tag.start.max(0) as usize,
            size: data.len(),
            bit: if d.wordlen == 1 {
                Some((d.raw % 8) as u8)
            } else {
                None
            },
            source: if op == 0 {
                Source::Read
            } else {
                Source::Client
            },
            ..Request::default()
        };
        if op != 0 {
            r.data[..data.len()].copy_from_slice(data)
        }
        let result = self.owner.call(r);
        if op == 0 && result.ok {
            data.copy_from_slice(&result.data[..data.len()])
        }
        if let Some(c) = self.transport.lock().unwrap().connections.get_mut(&id) {
            c.refs -= 1
        }
        self.event(json!({"event":"callback_return","connection":id,"pdu":pdu,"item":index,"result":result.ok,"seq":result.seq}));
        result.ok
    }
    pub fn end(&self, id: u64, pdu: u64) {
        if let Some(c) = self.transport.lock().unwrap().connections.get_mut(&id) {
            if c.pdu == pdu {
                c.inflight = false
            }
        }
        self.event(json!({"event":"pdu_released","connection":id,"pdu":pdu}))
    }
    pub fn closing(&self, id: u64) {
        let found = {
            let mut t = self.transport.lock().unwrap();
            if let Some(c) = t.connections.get_mut(&id) {
                c.closing = true;
                if c.reason == 0 {
                    c.reason = 4
                }
                true
            } else {
                false
            }
        };
        if found {
            self.owner.cancel(id);
        }
        self.event(json!({"event":"closing","connection":id}))
    }
    pub fn joined(&self, id: u64, rc: i32) {
        let mut t = self.transport.lock().unwrap();
        if let Some(c) = t.connections.remove(&id) {
            let mut g = self.global.lock().unwrap();
            g.tcp -= 1;
            if c.established {
                g.c -= 1
            } else {
                g.h -= 1
            }
            g.bytes -= t.base;
            self.owner.joined(id)
        }
        self.event(json!({"event":if rc==0{"pthread_join_return_release"}else{"create_failed_no_thread_release"},"connection":id,"rc":rc}))
    }
    pub fn io(&self, id: u64, op: i32, bytes: &[u8], len: u32, start: u64) {
        if let Some(c) = self.transport.lock().unwrap().connections.get_mut(&id) {
            if op == 2 {
                c.last_send = clock::ns()
            }
            if op == 4 || op == 5 {
                c.reason = op
            }
        }
        self.event(json!({"event":"io","connection":id,"op":op,"started_ns":start,"length":len,"bytes":if op==0||op==1{hex(bytes)}else{String::new()}}))
    }
    pub fn snapshot(&self) -> Value {
        let t = self.transport.lock().unwrap();
        let c = t.connections.values().filter(|c| c.established).count();
        let connections=t.connections.iter().map(|(id,c)|json!({"connection":id.to_string(),"peer":format!("127.0.0.1:{}",c.peer_port),"phase":if c.closing{"closing"}else if c.established{"established"}else{"handshaking"},"accepted_ns":c.accepted.to_string(),"established_ns":c.established_at.to_string(),"last_receive_complete_ns":c.last_recv.to_string(),"last_send_complete_ns":c.last_send.to_string(),"executing_pdu":usize::from(c.inflight),"callback_refs":c.refs,"waiting_pdu":0,"bytes":t.base+usize::from(c.inflight)*2208,"reason":c.reason})).collect::<Vec<_>>();
        json!({"c":c,"h":t.connections.len()-c+t.tokens.len(),"tcp":t.connections.len()+t.tokens.len(),"accepted_tcp":t.connections.len(),"config_c":t.c,"config_h":t.h,"closing":t.connections.values().filter(|c|c.closing).count(),"reserved_bytes":t.connections.values().filter(|c|c.inflight).count()*2208,"connections":connections})
    }
}
pub struct Instance {
    pub context: Arc<Context>,
    native: Mutex<Option<Handle>>,
    listener_reserved: AtomicBool,
    released: AtomicBool,
    pub control: Mutex<()>,
}
impl Instance {
    pub fn new(owner: Arc<Owner>, global: Arc<Mutex<Global>>) -> Result<Self, String> {
        let config = owner.compiled();
        let c = &config.config;
        let abi = native_ffi::probe()?;
        let fixed = abi.fixed_instance_bytes as usize;
        let base = abi.worker_size as usize
            + abi.worker_thread_size as usize
            + std::mem::size_of::<Connection>()
            + std::mem::size_of::<Job>()
            + 4096
            + 20
            + 2208
            + 2048
            + 256;
        {
            let mut g = global.lock().unwrap();
            // 按组合根固定额度+实际owner+listener/reaper+reserved TCP联合准入；真实释放才还额度。
            if g.fixed_threads + g.owners + 1 + g.listeners * 2 + g.tcp > 64
                || g.bytes + fixed > 4194304
            {
                return Err("runtime_capacity".into());
            }
            g.owners += 1;
            g.bytes += fixed;
        }
        let ctx = Arc::new(Context {
            owner,
            global: global.clone(),
            gate: AtomicBool::new(false),
            transport: Mutex::new(Transport {
                next: 0,
                tokens: BTreeSet::new(),
                connections: BTreeMap::new(),
                c: c.max_connections as usize,
                h: c.max_handshakes as usize,
                base,
                fixed,
                budgets: [65536, 1048576, 4194304],
            }),
        });
        let handle = match Handle::new(ctx.clone()) {
            Ok(h) => h,
            Err(e) => {
                let mut g = global.lock().unwrap();
                g.owners -= 1;
                g.bytes -= fixed;
                ctx.owner.shutdown();
                return Err(e);
            }
        };
        Ok(Self {
            context: ctx,
            native: Mutex::new(Some(handle)),
            listener_reserved: AtomicBool::new(false),
            released: AtomicBool::new(false),
            control: Mutex::new(()),
        })
    }
    pub fn start(&self) -> bool {
        if self.released.load(Ordering::SeqCst) {
            return false;
        }
        if self.context.gate.load(Ordering::SeqCst) {
            return true;
        }
        if !self.stopped() {
            return false;
        }
        {
            let mut g = self.context.global.lock().unwrap();
            if g.fixed_threads + g.owners + (g.listeners + 1) * 2 + g.tcp > 64 {
                return false;
            }
            g.listeners += 1;
            self.listener_reserved.store(true, Ordering::SeqCst);
        }
        let n = self.native.lock().unwrap();
        let Some(n) = n.as_ref() else { return false };
        self.context.owner.control("start", 0);
        self.context.gate.store(true, Ordering::SeqCst);
        let config = self.context.owner.compiled();
        if n.start(&config.config.host, config.config.port as i32) {
            true
        } else {
            self.context.gate.store(false, Ordering::SeqCst);
            self.context.owner.control("stop", 0);
            if n.request_stop() {
                let end = clock::ns() + 2_000_000_000;
                while clock::ns() < end {
                    if n.poll_stop() == 0 {
                        self.release_listener();
                        return false;
                    }
                    std::thread::sleep(Duration::from_millis(2));
                }
            }
            false
        }
    }
    fn release_listener(&self) {
        if self.listener_reserved.swap(false, Ordering::SeqCst) {
            self.context.global.lock().unwrap().listeners -= 1;
        }
    }
    pub fn request_stop(&self) -> bool {
        self.context.gate.store(false, Ordering::SeqCst);
        self.context.owner.control("stop", 0);
        if !self.listener_reserved.load(Ordering::SeqCst) {
            return true;
        }
        self.native
            .lock()
            .unwrap()
            .as_ref()
            .is_none_or(|n| n.request_stop())
    }
    pub fn poll_stop(&self) -> bool {
        if self.listener_reserved.load(Ordering::SeqCst) {
            let n = self.native.lock().unwrap();
            if n.as_ref().is_some_and(|n| n.poll_stop() != 0) {
                return false;
            }
            self.release_listener();
        }
        self.stopped()
    }
    pub fn stop_until(&self, deadline: u64) -> bool {
        if !self.request_stop() {
            return false;
        }
        while clock::ns() < deadline {
            if self.poll_stop() {
                return true;
            }
            std::thread::sleep(Duration::from_millis(2));
        }
        false
    }
    pub fn stop(&self) -> bool {
        self.stop_until(clock::ns() + 5_000_000_000)
    }
    pub fn stopped(&self) -> bool {
        let t = self.context.transport.lock().unwrap();
        !self.context.gate.load(Ordering::SeqCst)
            && !self.listener_reserved.load(Ordering::SeqCst)
            && t.connections.is_empty()
            && t.tokens.is_empty()
    }
    pub fn close(&self, id: u64) -> bool {
        if !self
            .context
            .transport
            .lock()
            .unwrap()
            .connections
            .contains_key(&id)
        {
            return true;
        }
        self.context.closing(id);
        self.native
            .lock()
            .unwrap()
            .as_ref()
            .is_some_and(|n| n.close(id))
    }
    #[cfg(feature = "test-automation")]
    pub fn budget(&self, c: usize, i: usize, g: usize) {
        self.context.transport.lock().unwrap().budgets = [c, i, g]
    }
    pub fn snapshot(&self) -> Value {
        let mut value = self.context.owner.snapshot();
        for (k, x) in self.context.snapshot().as_object().unwrap() {
            value[k] = x.clone()
        }
        let config = self.context.owner.compiled();
        value["endpoint"] = json!(format!("{}:{}", config.config.host, config.config.port));
        value
    }
    pub fn refresh_limits(&self) {
        let config = self.context.owner.compiled();
        let mut t = self.context.transport.lock().unwrap();
        t.c = config.config.max_connections as usize;
        t.h = config.config.max_handshakes as usize;
    }
    pub fn finish_shutdown(&self) -> bool {
        if !self.poll_stop() {
            return false;
        }
        let mut native = self.native.lock().unwrap();
        if let Some(handle) = native.take() {
            if !handle.destroy() {
                return false;
            }
        }
        let joined = self.context.owner.shutdown();
        if joined && !self.released.swap(true, Ordering::SeqCst) {
            let mut g = self.context.global.lock().unwrap();
            g.owners -= 1;
            g.bytes -= self.context.transport.lock().unwrap().fixed;
        }
        joined
    }
    pub fn shutdown(&self) -> bool {
        self.stop() && self.finish_shutdown()
    }
}
