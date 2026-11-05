//! 文件：src/app/plc_guard_get_int.rs；单轮业务条件与既有typed解析/Execution，无调度或协议IO。
use crate::{
    config::{Flow, Plc},
    domain::{now_ms, Clock},
    infrastructure::state::State,
    runtime::{Owner, Stop},
    services::{execution::Execution, Http},
    Result,
};
pub async fn iteration(
    f: &Flow,
    p: &Plc,
    http: &Http,
    owner: &Owner,
    state: &State,
    stop: &Stop,
    clock: &mut Clock,
) -> Result<()> {
    clock.check(now_ms())?;
    let sample = owner
        .read(&f.id, f.target.db_number, f.target.byte_offset)
        .await?;
    if sample.value >= 0 {
        return Ok(());
    }
    let input = http.get(&f.get_url).await?;
    if let Some(intent) = input.intent(f, p)? {
        Execution { owner, state, stop }
            .apply(intent, clock)
            .await?;
    }
    Ok(())
}
