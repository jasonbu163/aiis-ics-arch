//! DS时钟：单调计数用于调度/耗时；上海日历时间用于日志/显示，不参与运行时排序。
use std::time::{Duration, SystemTime, UNIX_EPOCH};

pub const BUSINESS_TIME_ZONE: &str = "Asia/Shanghai";
const BUSINESS_OFFSET_SECONDS: u64 = 8 * 60 * 60;
const BUSINESS_OFFSET: &str = "+08:00";

pub fn calendar_timestamp() -> Option<String> {
    calendar_timestamp_at(SystemTime::now())
}

pub fn calendar_timestamp_at(time: SystemTime) -> Option<String> {
    format_calendar_time(time.duration_since(UNIX_EPOCH).ok()?)
}

fn format_calendar_time(since_epoch: Duration) -> Option<String> {
    // 第一版业务合同固定东八区；gmtime_r不读取宿主机TZ，也不修改进程时区。
    let seconds: libc::time_t = since_epoch
        .as_secs()
        .checked_add(BUSINESS_OFFSET_SECONDS)?
        .try_into()
        .ok()?;
    let mut calendar = std::mem::MaybeUninit::<libc::tm>::uninit();
    if unsafe { libc::gmtime_r(&seconds, calendar.as_mut_ptr()) }.is_null() {
        return None;
    }
    let calendar = unsafe { calendar.assume_init() };
    Some(format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}.{:03}{BUSINESS_OFFSET}",
        calendar.tm_year + 1900,
        calendar.tm_mon + 1,
        calendar.tm_mday,
        calendar.tm_hour,
        calendar.tm_min,
        calendar.tm_sec,
        since_epoch.subsec_millis()
    ))
}

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

#[cfg(test)]
mod calendar_time_tests {
    use super::*;

    #[test]
    fn calendar_time_has_explicit_business_offset() {
        assert_eq!(
            format_calendar_time(Duration::ZERO).as_deref(),
            Some("1970-01-01T08:00:00.000+08:00")
        );
    }

    #[test]
    fn calendar_time_rolls_day_and_preserves_milliseconds() {
        assert_eq!(
            format_calendar_time(Duration::new(16 * 60 * 60, 123_000_000)).as_deref(),
            Some("1970-01-02T00:00:00.123+08:00")
        );
    }

    #[test]
    fn calendar_time_retained_event_keeps_independent_monotonic_clock() {
        let evidence = crate::infrastructure::logging::Evidence::default();
        evidence.put(serde_json::json!({"event":"calendar_time_probe"}));
        let snapshot = evidence.query(0, 1, None);
        let row = &snapshot["rows"][0];
        assert!(row["timestamp"].as_str().unwrap().ends_with("+08:00"));
        assert_eq!(row["time_zone"], BUSINESS_TIME_ZONE);
        assert_eq!(row["clock_id"], CLOCK_ID);
        assert!(row["monotonic_ns"].as_u64().unwrap() > 0);
        assert_eq!(evidence.take()[0]["timestamp"], row["timestamp"]);
    }
}
