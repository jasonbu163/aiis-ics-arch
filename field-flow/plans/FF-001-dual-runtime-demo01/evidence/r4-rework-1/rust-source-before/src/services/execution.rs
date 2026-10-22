//! 文件：src/services/execution.rs；父执行状态编排、意图/确认事务及失败保守分类。
use crate::{
    domain::{now_ms, Clock, Intent},
    infrastructure::state::State,
    runtime::{Owner, Stop},
    Result,
};
use std::sync::atomic::Ordering;
use tokio::time::Instant;
pub struct Execution<'a> {
    pub owner: &'a Owner,
    pub state: &'a State,
    pub stop: &'a Stop,
}
impl Execution<'_> {
    pub async fn apply(&self, intent: Intent, clock: &mut Clock) -> Result<()> {
        if self.stop.stopped.load(Ordering::Acquire) {
            return Err("canceled".into());
        }
        clock.check(now_ms())?;
        let deadline = Instant::from_std(intent.deadline());
        let status = self.state.admit(intent.clone()).await?;
        if status != "pending" {
            return if status == "unknown" {
                Err("target_unknown".into())
            } else {
                Ok(())
            };
        }
        clock.check(now_ms())?;
        match self.owner.write(intent.clone(), deadline).await {
            Ok(sample) if sample.write_ack.is_some() => {
                self.state.finish(intent, "confirmed", "s7_protocol").await
            }
            Ok(_) => {
                self.state
                    .finish(intent, "unknown", "missing_ack_proof")
                    .await?;
                Err("missing_ack_proof".into())
            }
            Err(error) => {
                let persisted = self.state.command_status(intent.clone()).await?;
                if persisted == "pending" && intent.validate_time(now_ms()).is_err() {
                    self.state
                        .finish(intent, "expired", "input_expired")
                        .await?;
                    return Err("expired".into());
                }
                if matches!(error.as_str(), "expired" | "canceled") {
                    self.state.finish(intent, &error, &error).await?;
                } else if persisted == "in_flight" {
                    self.state.finish(intent, "unknown", &error).await?;
                }
                Err(error)
            }
        }
    }
}
