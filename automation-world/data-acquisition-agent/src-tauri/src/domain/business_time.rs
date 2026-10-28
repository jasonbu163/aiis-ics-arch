//! 上海业务时间合同：固定毫秒存储/IPC、SQLite当前时间与独立诊断精度；不改变单调时钟语义。
use chrono::{DateTime, FixedOffset, SecondsFormat, Utc};
pub(crate) const TIME_PROFILE: &str = "asia-shanghai-rfc3339-ms-v1";
pub(crate) const SQL_NOW: &str = "SELECT strftime('%Y-%m-%dT%H:%M:%f+08:00','now','+8 hours')";
pub(crate) fn offset() -> FixedOffset {
    FixedOffset::east_opt(8 * 60 * 60).unwrap()
}
pub(crate) fn now() -> String {
    Utc::now()
        .with_timezone(&offset())
        .to_rfc3339_opts(SecondsFormat::Millis, false)
}
pub(crate) fn diagnostic_now() -> String {
    Utc::now()
        .with_timezone(&offset())
        .to_rfc3339_opts(SecondsFormat::Nanos, false)
}
pub(crate) fn normalize(value: &str) -> Result<String, String> {
    DateTime::parse_from_rfc3339(value)
        .map(|t| {
            t.with_timezone(&offset())
                .to_rfc3339_opts(SecondsFormat::Millis, false)
        })
        .map_err(|_| "invalid_business_time".into())
}
pub(crate) fn retention_cutoff(now: &str, days: u32) -> Result<String, String> {
    let time = DateTime::parse_from_rfc3339(now).map_err(|_| "invalid_business_time")?;
    let cutoff = time
        .checked_sub_signed(chrono::Duration::days(i64::from(days)))
        .ok_or("invalid_business_time")?;
    normalize(&cutoff.to_rfc3339())
}
