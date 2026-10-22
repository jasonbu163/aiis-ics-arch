//! DS运行时职责：Shared absolute monotonic nanoseconds. Instant is never a cross-process epoch.
pub const CLOCK_ID: &str = "darwin-clock-monotonic-ns";
pub fn ns() -> u64 {
    let mut t = libc::timespec {
        tv_sec: 0,
        tv_nsec: 0,
    };
    assert_eq!(
        unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut t) },
        0
    );
    (t.tv_sec as u64) * 1_000_000_000 + t.tv_nsec as u64
}
pub fn seconds() -> f64 {
    ns() as f64 / 1e9
}
