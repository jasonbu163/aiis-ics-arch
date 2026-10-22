//! 文件：src/app/demo01.rs；手写单轮GET→typed条件→执行服务，无循环、SQL或协议IO。
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
        Execution { owner, state, stop }
            .apply(intent, clock)
            .await?;
    }
    Ok(())
}
