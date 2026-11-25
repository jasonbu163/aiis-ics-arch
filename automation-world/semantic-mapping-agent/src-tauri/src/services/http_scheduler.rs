//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/http_scheduler.rs
//! Description: SMA 独立的 GET／POST 调度、流量限制和运行计数。
//! Main Features:
//!   - 按线路去重并限制等待数量，繁忙目标不阻塞其他目标。
//!   - 停止后清理等待任务并收口已进入 HTTP 的请求。

use std::collections::{BTreeMap, HashMap, HashSet, VecDeque};
use std::future::Future;
use std::sync::{Arc, Mutex};
use std::time::Duration;

use serde::{Deserialize, Serialize};
use tokio::time::{self, Instant, MissedTickBehavior};

const POLL: Duration = Duration::from_millis(25);

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "lowercase")]
pub(crate) enum SchedulerSide {
    Get,
    Post,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq, Serialize)]
#[serde(rename_all = "lowercase")]
pub(crate) enum SchedulerPhase {
    #[default]
    Stopped,
    Running,
    Stopping,
}

#[derive(Clone, Copy, Debug, Default, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct SchedulerLimits {
    pub concurrency: usize,
    pub queue: usize,
    pub per_target: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ScheduledJob {
    pub key: String,
    pub target: Option<String>,
    pub interval_ms: u64,
}

pub(crate) struct SchedulerBatch {
    pub limits: SchedulerLimits,
    pub jobs: Vec<ScheduledJob>,
}

#[derive(Clone, Copy, Debug)]
pub(crate) enum JobResult {
    Completed,
    Failed,
    Blocked,
    TimedOut,
    UnknownTimedOut,
    Unknown,
    Discarded,
}

#[derive(Clone, Debug, Default, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct SchedulerStatus {
    pub phase: SchedulerPhase,
    pub active: usize,
    pub in_flight: usize,
    pub queued: usize,
    pub completed: u64,
    pub failed: u64,
    pub blocked: u64,
    pub timed_out: u64,
    pub unknown: u64,
    pub saturated: u64,
    pub skipped: u64,
    pub discarded: u64,
    pub peak_in_flight: usize,
    pub peak_queued: usize,
    pub target_in_flight: BTreeMap<String, usize>,
    pub target_peak_in_flight: BTreeMap<String, usize>,
    pub last_error: Option<String>,
    pub limits: SchedulerLimits,
}

struct Deadline {
    due: Instant,
    saturation_report_at: Instant,
}

struct ActiveJob {
    ticket: u64,
    target: Option<String>,
    scheduled: bool,
    sending: bool,
    sent: bool,
}

#[derive(Default)]
struct Lane {
    generation: u64,
    ticket: u64,
    status: SchedulerStatus,
    pending: VecDeque<ScheduledJob>,
    deadlines: HashMap<String, Deadline>,
    active: HashMap<String, ActiveJob>,
}

impl Lane {
    fn can_reserve(&self, key: &str, target: Option<&str>) -> bool {
        let limits = self.status.limits;
        self.active.len() < limits.concurrency
            && !self.active.contains_key(key)
            && target.is_none_or(|target| {
                self.active
                    .values()
                    .filter(|job| job.target.as_deref() == Some(target))
                    .count()
                    < limits.per_target
            })
    }

    fn reserve(&mut self, key: &str, target: Option<String>, scheduled: bool) -> u64 {
        self.ticket += 1;
        self.active.insert(
            key.to_owned(),
            ActiveJob {
                ticket: self.ticket,
                target,
                scheduled,
                sending: false,
                sent: false,
            },
        );
        self.ticket
    }

    fn advance(&mut self, batch: SchedulerBatch, now: Instant) -> Vec<(ScheduledJob, u64)> {
        self.status.limits = batch.limits;
        let configured: HashMap<_, _> = batch.jobs.iter().map(|job| (&job.key, job)).collect();
        let previous = self.pending.len();
        self.pending.retain(|job| {
            configured
                .get(&job.key)
                .is_some_and(|current| *current == job)
        });
        self.pending.truncate(batch.limits.queue);
        self.status.discarded += (previous - self.pending.len()) as u64;
        self.deadlines.retain(|key, _| configured.contains_key(key));

        let mut ready = Vec::new();
        for _ in 0..self.pending.len() {
            let job = self.pending.pop_front().expect("queued route");
            if self.can_reserve(&job.key, job.target.as_deref()) {
                let ticket = self.reserve(&job.key, job.target.clone(), true);
                ready.push((job, ticket));
            } else {
                self.pending.push_back(job);
            }
        }

        let pending: HashSet<_> = self.pending.iter().map(|job| job.key.clone()).collect();
        let mut due = Vec::new();
        for job in batch.jobs {
            let deadline = self.deadlines.entry(job.key.clone()).or_insert(Deadline {
                due: now,
                saturation_report_at: now,
            });
            if deadline.due <= now {
                due.push((deadline.due, job));
            }
        }
        due.sort_by_key(|(due, _)| *due);
        for (_, job) in due {
            let key = job.key.clone();
            let next = now + Duration::from_millis(job.interval_ms.max(1));
            if pending.contains(&key) || self.active.contains_key(&key) {
                self.status.skipped += 1;
            } else if self.can_reserve(&key, job.target.as_deref()) {
                let ticket = self.reserve(&key, job.target.clone(), true);
                ready.push((job, ticket));
            } else if self.pending.len() < self.status.limits.queue {
                self.pending.push_back(job);
            } else {
                // Keep an overdue job eligible ahead of newer work when capacity returns.
                let deadline = self.deadlines.get_mut(&key).expect("known route");
                if deadline.saturation_report_at <= now {
                    self.status.saturated += 1;
                    deadline.saturation_report_at = next;
                }
                continue;
            }
            let deadline = self.deadlines.get_mut(&key).expect("known route");
            deadline.due = next;
            deadline.saturation_report_at = next;
        }
        self.status.peak_queued = self.status.peak_queued.max(self.pending.len());
        ready
    }

    fn snapshot(&self) -> SchedulerStatus {
        let mut status = self.status.clone();
        status.active = self.active.len();
        status.queued = self.pending.len();
        status
    }

    fn end_transport(&mut self, target: Option<&str>) {
        self.status.in_flight -= 1;
        if let Some(target) = target {
            let count = self
                .status
                .target_in_flight
                .get_mut(target)
                .expect("transport target");
            *count -= 1;
            if *count == 0 {
                self.status.target_in_flight.remove(target);
            }
        }
    }

    fn finish_stop(&mut self) {
        if self.status.phase == SchedulerPhase::Stopping
            && !self.active.values().any(|job| job.scheduled)
        {
            self.status.phase = SchedulerPhase::Stopped;
        }
    }
}

#[derive(Clone, Default)]
pub(crate) struct HttpScheduler {
    get: Arc<Mutex<Lane>>,
    post: Arc<Mutex<Lane>>,
}

impl HttpScheduler {
    fn lane(&self, side: SchedulerSide) -> &Arc<Mutex<Lane>> {
        match side {
            SchedulerSide::Get => &self.get,
            SchedulerSide::Post => &self.post,
        }
    }

    pub fn start<Plan, PlanFuture, Run, RunFuture>(
        &self,
        side: SchedulerSide,
        plan: Plan,
        run: Run,
    ) -> SchedulerStatus
    where
        Plan: Fn() -> PlanFuture + Send + 'static,
        PlanFuture: Future<Output = Result<SchedulerBatch, String>> + Send + 'static,
        Run: Fn(ScheduledJob, RequestActivity) -> RunFuture + Send + Sync + 'static,
        RunFuture: Future<Output = JobResult> + Send + 'static,
    {
        let (generation, status) = {
            let mut lane = self.lane(side).lock().expect("runtime lane");
            if lane.status.phase != SchedulerPhase::Stopped {
                return lane.snapshot();
            }
            lane.generation += 1;
            lane.status.phase = SchedulerPhase::Running;
            lane.status.last_error = None;
            (lane.generation, lane.snapshot())
        };
        let scheduler = self.clone();
        let run = Arc::new(run);
        tokio::spawn(async move {
            let mut tick = time::interval(POLL);
            tick.set_missed_tick_behavior(MissedTickBehavior::Skip);
            loop {
                tick.tick().await;
                if !scheduler.is_running(side, generation) {
                    break;
                }
                let batch = plan().await;
                let ready = {
                    let mut lane = scheduler.lane(side).lock().expect("runtime lane");
                    if lane.generation != generation || lane.status.phase != SchedulerPhase::Running
                    {
                        break;
                    }
                    match batch {
                        Ok(batch) => {
                            lane.status.last_error = None;
                            lane.advance(batch, Instant::now())
                        }
                        Err(error) => {
                            lane.status.last_error = Some(error);
                            Vec::new()
                        }
                    }
                };
                for (job, ticket) in ready {
                    let permit = scheduler.permit(side, job.key.clone(), ticket);
                    let run = run.clone();
                    tokio::spawn(async move {
                        let activity = permit.activity();
                        let result = if activity.can_start() {
                            run(job, activity).await
                        } else {
                            JobResult::Discarded
                        };
                        permit.finish(result);
                    });
                }
            }
        });
        tracing::info!(event = "sma_scheduler_start", ?side, result = "running");
        status
    }

    pub fn stop(&self, side: SchedulerSide) -> SchedulerStatus {
        let mut lane = self.lane(side).lock().expect("runtime lane");
        if lane.status.phase == SchedulerPhase::Running {
            lane.status.phase = SchedulerPhase::Stopping;
            let discarded = lane.pending.len();
            lane.status.discarded += discarded as u64;
            lane.pending.clear();
            lane.deadlines.clear();
            lane.finish_stop();
            tracing::info!(event = "sma_scheduler_stop", ?side, discarded);
        }
        lane.snapshot()
    }

    pub fn stop_all(&self) {
        self.stop(SchedulerSide::Get);
        self.stop(SchedulerSide::Post);
    }

    pub fn status(&self, side: SchedulerSide) -> SchedulerStatus {
        self.lane(side).lock().expect("runtime lane").snapshot()
    }

    pub fn try_manual(
        &self,
        side: SchedulerSide,
        limits: &SchedulerLimits,
        key: String,
        target: Option<String>,
    ) -> Result<ManualPermit, String> {
        let mut lane = self.lane(side).lock().expect("runtime lane");
        lane.status.limits = *limits;
        if lane.status.phase == SchedulerPhase::Stopping
            || !lane.can_reserve(&key, target.as_deref())
        {
            lane.status.saturated += 1;
            return Err("SMA_RUNTIME_BUSY".to_owned());
        }
        let ticket = lane.reserve(&key, target, false);
        Ok(self.permit(side, key, ticket))
    }

    fn permit(&self, side: SchedulerSide, key: String, ticket: u64) -> ManualPermit {
        ManualPermit(Some(RequestActivity {
            scheduler: self.clone(),
            side,
            key,
            ticket,
        }))
    }

    fn is_running(&self, side: SchedulerSide, generation: u64) -> bool {
        let lane = self.lane(side).lock().expect("runtime lane");
        lane.generation == generation && lane.status.phase == SchedulerPhase::Running
    }
}

#[derive(Clone)]
pub(crate) struct RequestActivity {
    scheduler: HttpScheduler,
    side: SchedulerSide,
    key: String,
    ticket: u64,
}

impl RequestActivity {
    fn can_start(&self) -> bool {
        let lane = self.scheduler.lane(self.side).lock().expect("runtime lane");
        lane.active.get(&self.key).is_some_and(|job| {
            job.ticket == self.ticket
                && (!job.scheduled || lane.status.phase == SchedulerPhase::Running)
        })
    }

    pub fn begin_http(&self) -> Result<HttpActivity, String> {
        let mut lane = self.scheduler.lane(self.side).lock().expect("runtime lane");
        let running = lane.status.phase == SchedulerPhase::Running;
        let job = lane
            .active
            .get_mut(&self.key)
            .filter(|job| job.ticket == self.ticket && !job.sent && (!job.scheduled || running))
            .ok_or_else(|| "SMA_RUNTIME_DISPATCH_CANCELLED".to_owned())?;
        job.sending = true;
        job.sent = true;
        let target = job.target.clone();
        lane.status.in_flight += 1;
        lane.status.peak_in_flight = lane.status.peak_in_flight.max(lane.status.in_flight);
        if let Some(target) = target {
            let count = lane
                .status
                .target_in_flight
                .entry(target.clone())
                .or_default();
            *count += 1;
            let count = *count;
            let peak = lane.status.target_peak_in_flight.entry(target).or_default();
            *peak = (*peak).max(count);
        }
        Ok(HttpActivity(self.clone()))
    }
}

pub(crate) struct HttpActivity(RequestActivity);

impl Drop for HttpActivity {
    fn drop(&mut self) {
        let RequestActivity {
            scheduler,
            side,
            key,
            ticket,
        } = &self.0;
        let mut lane = scheduler.lane(*side).lock().expect("runtime lane");
        if let Some(job) = lane
            .active
            .get_mut(key)
            .filter(|job| job.ticket == *ticket && job.sending)
        {
            job.sending = false;
            let target = job.target.clone();
            lane.end_transport(target.as_deref());
        }
    }
}

pub(crate) struct ManualPermit(Option<RequestActivity>);

impl ManualPermit {
    pub fn activity(&self) -> RequestActivity {
        self.0.as_ref().expect("active request permit").clone()
    }

    pub fn finish(mut self, result: JobResult) {
        self.close(Some(result));
    }

    fn close(&mut self, result: Option<JobResult>) {
        let Some(RequestActivity {
            scheduler,
            side,
            key,
            ..
        }) = self.0.take()
        else {
            return;
        };
        let mut lane = scheduler.lane(side).lock().expect("runtime lane");
        let job = lane.active.remove(&key).expect("active request permit");
        if job.sending {
            lane.end_transport(job.target.as_deref());
        }
        match result.unwrap_or_else(|| match (side, job.sent) {
            (SchedulerSide::Post, true) => JobResult::Unknown,
            (_, true) => JobResult::Failed,
            _ => JobResult::Discarded,
        }) {
            JobResult::Completed => lane.status.completed += 1,
            JobResult::Failed => lane.status.failed += 1,
            JobResult::Blocked => lane.status.blocked += 1,
            JobResult::TimedOut => lane.status.timed_out += 1,
            JobResult::UnknownTimedOut => {
                lane.status.timed_out += 1;
                lane.status.unknown += 1;
            }
            JobResult::Unknown => lane.status.unknown += 1,
            JobResult::Discarded => lane.status.discarded += 1,
        }
        lane.finish_stop();
    }
}

impl Drop for ManualPermit {
    fn drop(&mut self) {
        self.close(None);
    }
}

#[cfg(test)]
mod tests;
