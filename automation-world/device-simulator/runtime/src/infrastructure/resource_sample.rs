//! DS运行时职责：Native macOS self-process counters; all returned Mach rights are released.
use serde_json::{json, Value};
extern "C" {
    fn mach_port_deallocate(task: u32, name: u32) -> i32;
    fn mach_port_names(
        task: u32,
        names: *mut *mut u32,
        count: *mut u32,
        types: *mut *mut u32,
        type_count: *mut u32,
    ) -> i32;
}
#[allow(deprecated)]
pub fn sample() -> Value {
    unsafe {
        let task = libc::mach_task_self();
        let mut info: libc::mach_task_basic_info = std::mem::zeroed();
        let mut n = libc::MACH_TASK_BASIC_INFO_COUNT;
        libc::task_info(
            task,
            libc::MACH_TASK_BASIC_INFO,
            &mut info as *mut _ as *mut _,
            &mut n,
        );
        let mut usage: libc::rusage = std::mem::zeroed();
        libc::getrusage(libc::RUSAGE_SELF, &mut usage);
        let mut threads = std::ptr::null_mut();
        let mut nt = 0;
        libc::task_threads(task, &mut threads, &mut nt);
        for i in 0..nt {
            mach_port_deallocate(task, *threads.add(i as usize));
        }
        if !threads.is_null() {
            libc::vm_deallocate(task, threads as usize, nt as usize * 4);
        }
        let mut names = std::ptr::null_mut();
        let mut types = std::ptr::null_mut();
        let (mut nn, mut tn) = (0, 0);
        mach_port_names(task, &mut names, &mut nn, &mut types, &mut tn);
        if !names.is_null() {
            libc::vm_deallocate(task, names as usize, nn as usize * 4);
        }
        if !types.is_null() {
            libc::vm_deallocate(task, types as usize, tn as usize * 4);
        }
        let fdbytes = libc::proc_pidinfo(
            libc::getpid(),
            libc::PROC_PIDLISTFDS,
            0,
            std::ptr::null_mut(),
            0,
        );
        let cpu = usage.ru_utime.tv_sec as f64
            + usage.ru_utime.tv_usec as f64 / 1e6
            + usage.ru_stime.tv_sec as f64
            + usage.ru_stime.tv_usec as f64 / 1e6;
        let rss = info.resident_size;
        json!({"event":"resources","pid":libc::getpid(),"cpu_seconds":cpu,"rss":rss,"threads":nt,"fd":fdbytes.max(0)as usize/std::mem::size_of::<libc::proc_fdinfo>(),"mach_ports":nn})
    }
}
