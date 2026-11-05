//! 文件：src/app/get_value_guard_int.rs；单轮业务条件与既有typed解析/Execution，无调度或协议IO。
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
    let input = http.get(&f.get_url).await?;
    if let Some(intent) = input.intent(f, p)? {
        if intent.value <= 0 {
            return Ok(());
        }
        if intent.value > 100 {
            return Ok(());
        }
        Execution { owner, state, stop }
            .apply(intent, clock)
            .await?;
    }
    Ok(())
}
