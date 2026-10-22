//! DS运行时职责：Checked C ABI. Callbacks borrow stable Arc backing; no exclusive Rust reference is manufactured.
use crate::services::lifecycle::Context;
use std::{
    ffi::c_void,
    os::raw::c_int,
    panic::{catch_unwind, AssertUnwindSafe},
    sync::Arc,
};
#[repr(C, packed)]
#[derive(Clone, Copy, Default)]
pub struct Tag {
    pub area: c_int,
    pub db: c_int,
    pub start: c_int,
    pub count: c_int,
    pub wordlen: c_int,
}
#[repr(C)]
#[derive(Clone, Copy, Default)]
pub struct Descriptor {
    pub pdu: u64,
    pub index: i32,
    pub area: i32,
    pub db: i32,
    pub raw: i32,
    pub count: i32,
    pub wordlen: i32,
    pub bytes: i32,
    pub offset: i32,
    pub reserved: [u8; 24],
}
#[repr(C)]
pub struct Callbacks {
    pub version: u32,
    pub size: u32,
    pub reserve: unsafe extern "C" fn(*mut c_void, *mut u64) -> c_int,
    pub cancel: unsafe extern "C" fn(*mut c_void, u64),
    pub accepted: unsafe extern "C" fn(*mut c_void, u64, c_int, *mut u64) -> c_int,
    pub active: unsafe extern "C" fn(*mut c_void, u64) -> c_int,
    pub cotp: unsafe extern "C" fn(*mut c_void, u64, *const u8, u32) -> c_int,
    pub setup: unsafe extern "C" fn(*mut c_void, u64) -> c_int,
    pub begin: unsafe extern "C" fn(*mut c_void, u64, *const u8, u32, *mut u64) -> c_int,
    pub item: unsafe extern "C" fn(
        *mut c_void,
        u64,
        u64,
        u32,
        c_int,
        *const Tag,
        *mut c_void,
        u32,
    ) -> c_int,
    pub end: unsafe extern "C" fn(*mut c_void, u64, u64),
    pub closing: unsafe extern "C" fn(*mut c_void, u64),
    pub joined: unsafe extern "C" fn(*mut c_void, u64, c_int),
    pub io: unsafe extern "C" fn(*mut c_void, u64, c_int, *const c_void, u32, u64),
}
#[repr(C)]
#[derive(Default, serde::Serialize)]
pub struct Abi {
    pub version: u32,
    pub tag_size: u32,
    pub tag_align: u32,
    pub offsets: [u32; 5],
    pub callbacks_size: u32,
    pub callbacks_align: u32,
    pub callback_offsets: [u32; 14],
    pub worker_size: u32,
    pub socket_size: u32,
    pub worker_thread_size: u32,
    pub fixed_instance_bytes: u32,
    pub callback_zero: c_int,
    pub callback_nonzero: c_int,
}
#[cfg(feature = "native-s7")]
extern "C" {
    fn ds_s7_create(c: *const Callbacks, u: *mut c_void) -> *mut c_void;
    fn ds_s7_start(s: *mut c_void, host: *const std::ffi::c_char, port: c_int) -> c_int;
    fn ds_s7_request_stop(s: *mut c_void) -> c_int;
    fn ds_s7_poll_stop(s: *mut c_void) -> c_int;
    fn ds_s7_close(s: *mut c_void, id: u64) -> c_int;
    fn ds_s7_destroy(s: *mut c_void) -> c_int;
    fn ds_s7_abi_probe(
        a: *mut Abi,
        c: extern "C" fn(*mut c_void, c_int, c_int, *const Tag, *mut c_void) -> c_int,
        u: *mut c_void,
    ) -> c_int;
    fn ds_s7_clock_ns() -> u64;
}
extern "C" fn reflect(
    _: *mut c_void,
    _sender: c_int,
    op: c_int,
    t: *const Tag,
    p: *mut c_void,
) -> c_int {
    if t.is_null() || p.is_null() {
        return -1;
    }
    let tag = unsafe { std::ptr::read_unaligned(t) };
    if tag.db != 41 || tag.start != 512 || unsafe { *(p as *const u8) } != 77 {
        return -1;
    }
    op
}

pub fn probe() -> Result<Abi, String> {
    let offsets = [
        std::mem::offset_of!(Callbacks, version) as u32,
        std::mem::offset_of!(Callbacks, size) as u32,
        std::mem::offset_of!(Callbacks, reserve) as u32,
        std::mem::offset_of!(Callbacks, cancel) as u32,
        std::mem::offset_of!(Callbacks, accepted) as u32,
        std::mem::offset_of!(Callbacks, active) as u32,
        std::mem::offset_of!(Callbacks, cotp) as u32,
        std::mem::offset_of!(Callbacks, setup) as u32,
        std::mem::offset_of!(Callbacks, begin) as u32,
        std::mem::offset_of!(Callbacks, item) as u32,
        std::mem::offset_of!(Callbacks, end) as u32,
        std::mem::offset_of!(Callbacks, closing) as u32,
        std::mem::offset_of!(Callbacks, joined) as u32,
        std::mem::offset_of!(Callbacks, io) as u32,
    ];
    let mut a = Abi::default();
    #[cfg(feature = "native-s7")]
    unsafe {
        if ds_s7_abi_probe(&mut a, reflect, std::ptr::null_mut()) != 0 {
            return Err("native ABI probe".into());
        }
    }
    #[cfg(not(feature = "native-s7"))]
    {
        a.version = 1;
        a.tag_size = 20;
        a.tag_align = 1;
        a.offsets = [0, 4, 8, 12, 16];
        a.callbacks_size = std::mem::size_of::<Callbacks>() as u32;
        a.callbacks_align = std::mem::align_of::<Callbacks>() as u32;
        a.callback_nonzero = 37;
        a.callback_offsets = offsets;
    }
    if a.callback_offsets != offsets
        || a.tag_size != std::mem::size_of::<Tag>() as u32
        || a.tag_align != 1
        || a.offsets != [0, 4, 8, 12, 16]
        || a.callbacks_size != std::mem::size_of::<Callbacks>() as u32
        || a.callbacks_align != std::mem::align_of::<Callbacks>() as u32
        || a.callback_zero != 0
        || a.callback_nonzero != 37
        || std::mem::size_of::<Descriptor>() != 64
    {
        return Err("ABI mismatch".into());
    }
    Ok(a)
}
pub fn clock_samples() -> Result<serde_json::Value, String> {
    let mut out = vec![];
    let mut previous = 0;
    for _ in 0..100 {
        let before = super::clock::ns();
        #[cfg(feature = "native-s7")]
        let native = unsafe { ds_s7_clock_ns() };
        #[cfg(not(feature = "native-s7"))]
        let native = super::clock::ns();
        let after = super::clock::ns();
        if native < before || native > after || native < previous {
            return Err("clock bracket mismatch".into());
        }
        previous = native;
        out.push(serde_json::json!({"before_ns":before,"native_ns":native,"after_ns":after}));
    }
    Ok(serde_json::json!({"clock_id":super::clock::CLOCK_ID,"samples":out,"count":100}))
}
fn guarded(f: impl FnOnce() -> bool) -> i32 {
    match catch_unwind(AssertUnwindSafe(f)) {
        Ok(true) => 0,
        _ => 1,
    }
}
unsafe fn ctx<'a>(u: *mut c_void) -> &'a Context {
    &*(u as *const Context)
}
unsafe extern "C" fn reserve(u: *mut c_void, out: *mut u64) -> i32 {
    guarded(|| {
        if out.is_null() {
            return false;
        }
        if let Some(id) = ctx(u).reserve() {
            *out = id;
            true
        } else {
            false
        }
    })
}
unsafe extern "C" fn cancel(u: *mut c_void, t: u64) {
    let _ = guarded(|| {
        ctx(u).cancel(t);
        true
    });
}
unsafe extern "C" fn accepted(u: *mut c_void, t: u64, fd: i32, out: *mut u64) -> i32 {
    guarded(|| {
        if out.is_null() {
            return false;
        }
        if let Some(id) = ctx(u).accepted(t, fd) {
            *out = id;
            true
        } else {
            false
        }
    })
}
unsafe extern "C" fn active(u: *mut c_void, id: u64) -> i32 {
    guarded(|| ctx(u).active(id))
}
unsafe extern "C" fn cotp(u: *mut c_void, id: u64, p: *const u8, n: u32) -> i32 {
    guarded(|| {
        !p.is_null() && n <= 512 && ctx(u).cotp(id, std::slice::from_raw_parts(p, n as usize))
    })
}
unsafe extern "C" fn setup(u: *mut c_void, id: u64) -> i32 {
    guarded(|| ctx(u).setup(id))
}
unsafe extern "C" fn begin(u: *mut c_void, id: u64, p: *const u8, n: u32, out: *mut u64) -> i32 {
    guarded(|| {
        if p.is_null() || out.is_null() || n > 480 {
            return false;
        }
        if let Some(pid) = ctx(u).begin(id, std::slice::from_raw_parts(p, n as usize)) {
            *out = pid;
            true
        } else {
            false
        }
    })
}
unsafe extern "C" fn item(
    u: *mut c_void,
    id: u64,
    pdu: u64,
    i: u32,
    op: i32,
    t: *const Tag,
    p: *mut c_void,
    n: u32,
) -> i32 {
    guarded(|| {
        if t.is_null() || p.is_null() || n == 0 || n > 256 || op < 0 || op > 1 {
            return false;
        }
        let tag = std::ptr::read_unaligned(t);
        ctx(u).item(
            id,
            pdu,
            i,
            op,
            tag,
            std::slice::from_raw_parts_mut(p as *mut u8, n as usize),
        )
    })
}
unsafe extern "C" fn end(u: *mut c_void, id: u64, pdu: u64) {
    let _ = guarded(|| {
        ctx(u).end(id, pdu);
        true
    });
}
unsafe extern "C" fn closing(u: *mut c_void, id: u64) {
    let _ = guarded(|| {
        ctx(u).closing(id);
        true
    });
}
unsafe extern "C" fn joined(u: *mut c_void, id: u64, rc: i32) {
    let _ = guarded(|| {
        ctx(u).joined(id, rc);
        true
    });
}
unsafe extern "C" fn io(u: *mut c_void, id: u64, op: i32, p: *const c_void, n: u32, start: u64) {
    let _ = guarded(|| {
        let bytes = if !p.is_null() && (op == 0 || op == 1) && n <= 512 {
            std::slice::from_raw_parts(p as *const u8, n as usize)
        } else {
            &[]
        };
        ctx(u).io(id, op, bytes, n, start);
        true
    });
}
fn callbacks() -> Callbacks {
    Callbacks {
        version: 1,
        size: std::mem::size_of::<Callbacks>() as u32,
        reserve,
        cancel,
        accepted,
        active,
        cotp,
        setup,
        begin,
        item,
        end,
        closing,
        joined,
        io,
    }
}
pub struct Handle {
    pointer: *mut c_void,
    _context: Arc<Context>,
    _callbacks: Box<Callbacks>,
}
unsafe impl Send for Handle {} // Native entrypoints are serialized by Instance; callbacks synchronize Context internally.
impl Handle {
    pub fn new(context: Arc<Context>) -> Result<Self, String> {
        let cb = Box::new(callbacks());
        #[cfg(feature = "native-s7")]
        let p = unsafe { ds_s7_create(&*cb, Arc::as_ptr(&context) as *mut c_void) };
        #[cfg(not(feature = "native-s7"))]
        let p = std::ptr::null_mut();
        if p.is_null() {
            return Err("native create unavailable".into());
        }
        Ok(Self {
            pointer: p,
            _context: context,
            _callbacks: cb,
        })
    }
    pub fn start(&self, host: &str, port: i32) -> bool {
        #[cfg(feature = "native-s7")]
        unsafe {
            let Ok(host) = std::ffi::CString::new(host) else {
                return false;
            };
            return ds_s7_start(self.pointer, host.as_ptr(), port) == 0;
        }
        #[cfg(not(feature = "native-s7"))]
        {
            let _ = (host, port);
            false
        }
    }
    pub fn request_stop(&self) -> bool {
        #[cfg(feature = "native-s7")]
        unsafe {
            return ds_s7_request_stop(self.pointer) == 0;
        }
        #[cfg(not(feature = "native-s7"))]
        {
            false
        }
    }
    pub fn poll_stop(&self) -> i32 {
        #[cfg(feature = "native-s7")]
        unsafe {
            return ds_s7_poll_stop(self.pointer);
        }
        #[cfg(not(feature = "native-s7"))]
        {
            -1
        }
    }
    pub fn close(&self, id: u64) -> bool {
        #[cfg(feature = "native-s7")]
        unsafe {
            return ds_s7_close(self.pointer, id) == 0;
        }
        #[cfg(not(feature = "native-s7"))]
        {
            let _ = id;
            false
        }
    }
    pub fn destroy(self) -> bool {
        #[cfg(feature = "native-s7")]
        unsafe {
            if ds_s7_destroy(self.pointer) != 0 {
                std::mem::forget(self);
                return false;
            }
        }
        true
    }
}
// Deliberately no automatic native destruction: failed joins retain Context ownership.
impl Drop for Handle {
    fn drop(&mut self) {}
}
fn be16(p: &[u8]) -> usize {
    u16::from_be_bytes([p[0], p[1]]) as usize
}
pub fn parse_pdu(d: &[u8]) -> Option<([Descriptor; 4], usize)> {
    if d.len() < 12 || d.len() > 480 || d[0] != 0x32 || d[1] != 1 {
        return None;
    }
    let count = d[11] as usize;
    let plen = be16(&d[6..8]);
    let dlen = be16(&d[8..10]);
    let function = d[10];
    if !(1..=4).contains(&count)
        || plen != 2 + 12 * count
        || d.len() != 10 + plen + dlen
        || ![4, 5].contains(&function)
    {
        return None;
    }
    let mut desc = [Descriptor::default(); 4];
    let mut pos = 10 + plen;
    let mut total = 0;
    let mut response = 7 + 12 + 2;
    for (i, x) in desc.iter_mut().enumerate().take(count) {
        let p = &d[12 + i * 12..24 + i * 12];
        x.index = i as i32;
        x.wordlen = p[3] as i32;
        x.count = be16(&p[4..6]) as i32;
        x.db = be16(&p[6..8]) as i32;
        x.area = p[8] as i32;
        x.raw = (p[9] as i32) * 65536 + (p[10] as i32) * 256 + p[11] as i32;
        let width = match x.wordlen {
            1 | 2 => 1,
            4 | 5 => 2,
            6 | 7 | 8 => 4,
            _ => return None,
        };
        x.bytes = x.count * width;
        if p[..3] != [0x12, 10, 0x10]
            || x.count < 1
            || x.bytes > 256
            || x.wordlen == 1 && x.count != 1
            || x.wordlen != 1 && x.raw % 8 != 0
        {
            return None;
        }
        total += x.bytes as usize;
        response += if function == 4 {
            4 + x.bytes as usize + x.bytes as usize % 2
        } else {
            1
        };
        if function == 5 {
            if pos + 4 > d.len() {
                return None;
            }
            let transport = d[pos + 1];
            let length = be16(&d[pos + 2..pos + 4]);
            let expected = match x.wordlen {
                1 => 3,
                5 | 7 => 5,
                8 => 7,
                _ => 4,
            };
            if transport != expected
                || length
                    != if expected == 3 {
                        1
                    } else if expected == 7 {
                        x.bytes as usize
                    } else {
                        x.bytes as usize * 8
                    }
            {
                return None;
            }
            let bytes = if transport == 3 {
                (length + 7) / 8
            } else if transport == 4 || transport == 5 {
                if length % 8 != 0 {
                    return None;
                }
                length / 8
            } else {
                length
            };
            if bytes != x.bytes as usize || pos + 4 + bytes > d.len() {
                return None;
            }
            x.offset = (pos + 4) as i32;
            pos += 4 + bytes;
            if i < count - 1 && bytes % 2 != 0 {
                pos += 1
            }
        }
    }
    if total > 480
        || response > 512
        || response - 7 > 480
        || function == 4 && dlen != 0
        || function == 5 && pos != d.len()
    {
        return None;
    }
    Some((desc, count))
}
