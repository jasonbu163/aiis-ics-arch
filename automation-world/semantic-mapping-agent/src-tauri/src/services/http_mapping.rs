//! SMA 采集、共享 evaluator、一次性预览和独立周期调度。
use super::{
    http_scheduler::{
        HttpScheduler, JobResult, RequestActivity, ScheduledJob, SchedulerBatch, SchedulerLimits,
        SchedulerPhase, SchedulerSide, SchedulerStatus,
    },
    local_configuration::LocalConfigurationService,
};
use crate::{
    contracts::{http_mapping::*, local_configuration::*},
    domain::{http_mapping as domain, runtime::business_now_string},
    infrastructure::http_mapping as transport,
};
use serde::Serialize;
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};

const PREVIEW_LIFETIME: Duration = Duration::from_secs(120);

struct Confirmable {
    key: String,
    group: String,
    preview: PostPreview,
    created_at: Instant,
    mapping: bool,
}

#[derive(Default)]
struct SourceAttempt {
    time: String,
    error: Option<String>,
    own_version: Option<u64>,
}

#[derive(Default)]
struct Observations {
    sources: BTreeMap<String, SourceAttempt>,
    mappings: BTreeMap<String, PostResult>,
    unknown: BTreeMap<String, PostResult>,
    pending: Option<Confirmable>,
    exiting: bool,
}

#[derive(Clone)]
pub struct HttpMappingService {
    config: LocalConfigurationService,
    client: Result<reqwest::Client, String>,
    scheduler: HttpScheduler,
    observations: Arc<Mutex<Observations>>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct RuntimeStatus {
    get: SchedulerStatus,
    post: SchedulerStatus,
    mappings: BTreeMap<String, PostResult>,
    last_unknown: BTreeMap<String, PostResult>,
}

impl HttpMappingService {
    pub fn new(config: LocalConfigurationService) -> Self {
        Self {
            config,
            client: transport::client(),
            scheduler: HttpScheduler::default(),
            observations: Arc::new(Mutex::new(Observations::default())),
        }
    }

    fn client(&self) -> Result<&reqwest::Client, String> {
        self.client.as_ref().map_err(Clone::clone)
    }

    pub async fn test_source(&self, key: &str) -> Result<SourceTest, String> {
        let config = self.config.load()?;
        let (_, source) = source(&config, key)?;
        let permit = {
            let observations = self.observations.lock().expect("SMA HTTP observations");
            if observations.exiting {
                return Err("SMA_HTTP_EXITING".into());
            }
            self.scheduler.try_manual(
                SchedulerSide::Get,
                &limits(&config, SchedulerSide::Get),
                source.source_key.clone(),
                None,
            )?
        };
        let test = transport::collect(self.client()?, &source, permit.activity()).await;
        permit.finish(get_outcome(test.error_code.as_deref()));
        Ok(test)
    }

    pub fn latest(&self) -> Result<Vec<SourceState>, String> {
        let (config, snapshots) = self.config.with_http_snapshots(|d| {
            d.http_sources
                .iter()
                .filter_map(|s| s["sourceKey"].as_str().map(str::to_owned))
                .collect()
        })?;
        let mut snapshots: BTreeMap<_, _> = snapshots
            .into_iter()
            .map(|s| (s.source_key.clone(), s))
            .collect();
        let observations = self.observations.lock().expect("SMA HTTP observations");
        Ok(config
            .document
            .http_sources
            .iter()
            .filter_map(|s| s["sourceKey"].as_str())
            .map(|key| {
                let attempt = observations.sources.get(key);
                let snapshot = snapshots.remove(key);
                SourceState {
                    source_key: key.into(),
                    last_attempt_at: attempt.map(|a| a.time.clone()),
                    last_error_code: attempt.and_then(|a| a.error.clone()),
                    from_previous_session: snapshot
                        .as_ref()
                        .is_some_and(|s| attempt.and_then(|a| a.own_version) != Some(s.version)),
                    snapshot,
                }
            })
            .collect())
    }

    pub fn preview_mapping(&self, id: &str, expected: u64) -> Result<PostPreview, String> {
        let (config, states) = self.mapping_input(id)?;
        require_revision(&config, expected)?;
        let (group, preview) = domain::evaluate_mapping(&config, &states, id)?;
        self.remember(id.to_owned(), group, preview, true)
    }

    pub fn preview_target(
        &self,
        id: &str,
        expected: u64,
        values: BTreeMap<String, Value>,
    ) -> Result<PostPreview, String> {
        let config = self.config.load()?;
        require_revision(&config, expected)?;
        let (group, preview) = domain::evaluate_target(&config, id, values)?;
        self.remember(id.to_owned(), group, preview, false)
    }

    fn remember(
        &self,
        key: String,
        group: String,
        mut preview: PostPreview,
        mapping: bool,
    ) -> Result<PostPreview, String> {
        let mut observations = self.observations.lock().expect("SMA HTTP observations");
        if observations.exiting {
            return Err("SMA_HTTP_EXITING".into());
        }
        observations.pending = if preview.request.is_some() {
            preview.token = Some(uuid::Uuid::new_v4().to_string());
            Some(Confirmable {
                key,
                group,
                preview: preview.clone(),
                created_at: Instant::now(),
                mapping,
            })
        } else {
            None
        };
        Ok(preview)
    }

    pub fn cancel_post(&self, token: &str) {
        let mut observations = self.observations.lock().expect("SMA HTTP observations");
        if observations
            .pending
            .as_ref()
            .and_then(|p| p.preview.token.as_deref())
            == Some(token)
        {
            observations.pending = None;
        }
    }

    pub async fn confirm_post(&self, token: &str) -> Result<PostResult, String> {
        let pending = {
            let mut observations = self.observations.lock().expect("SMA HTTP observations");
            if observations.exiting {
                return Err("SMA_HTTP_EXITING".into());
            }
            if observations
                .pending
                .as_ref()
                .and_then(|p| p.preview.token.as_deref())
                != Some(token)
            {
                return Err("SMA_HTTP_PREVIEW_REQUIRED".into());
            }
            observations
                .pending
                .take()
                .ok_or("SMA_HTTP_PREVIEW_REQUIRED")?
        };
        if pending.created_at.elapsed() > PREVIEW_LIFETIME {
            return Err("SMA_HTTP_PREVIEW_EXPIRED".into());
        }
        let config = if pending.mapping {
            let (config, states) = self.mapping_input(&pending.key)?;
            require_revision(&config, pending.preview.revision)?;
            let (_, fresh) = domain::evaluate_mapping(&config, &states, &pending.key)?;
            if fresh.request.is_none()
                || !fresh
                    .sources
                    .iter()
                    .zip(&pending.preview.sources)
                    .all(|(a, b)| a.source_key == b.source_key && a.version == b.version)
                || fresh.sources.len() != pending.preview.sources.len()
            {
                return Err("SMA_HTTP_PREVIEW_CHANGED".into());
            }
            config
        } else {
            let config = self.config.load()?;
            require_revision(&config, pending.preview.revision)?;
            config
        };
        let permit = {
            let observations = self.observations.lock().expect("SMA HTTP observations");
            if observations.exiting {
                return Err("SMA_HTTP_EXITING".into());
            }
            self.scheduler.try_manual(
                SchedulerSide::Post,
                &limits(&config, SchedulerSide::Post),
                pending.key.clone(),
                Some(pending.group),
            )?
        };
        tracing::info!(event = "sma_http_manual_post", resource = %pending.key, revision = config.revision, result = "confirmed");
        let result = transport::post(self.client()?, pending.preview, permit.activity()).await;
        permit.finish(post_outcome(&result));
        tracing::info!(event = "sma_http_manual_post", resource = %pending.key,
            run_id = %result.run_id, result = result.status, http_status = result.http_status,
            error_code = result.error_code.as_deref());
        if pending.mapping {
            self.record(&pending.key, &result);
        }
        Ok(result)
    }

    pub(crate) fn start(&self, side: SchedulerSide) -> Result<SchedulerStatus, String> {
        let observations = self.observations.lock().expect("SMA HTTP observations");
        if observations.exiting {
            return Err("SMA_HTTP_EXITING".into());
        }
        self.client()?;
        self.config.load()?;
        let planner = self.clone();
        let runner = self.clone();
        Ok(self.scheduler.start(
            side,
            move || {
                let planner = planner.clone();
                async move { planner.plan(side) }
            },
            move |job, activity| {
                let runner = runner.clone();
                async move {
                    match side {
                        SchedulerSide::Get => runner.run_get(job, activity).await,
                        SchedulerSide::Post => runner.run_post(job, activity).await,
                    }
                }
            },
        ))
    }

    pub(crate) fn stop(&self, side: SchedulerSide) -> SchedulerStatus {
        self.scheduler.stop(side)
    }

    pub fn begin_shutdown(&self) -> bool {
        let mut observations = self.observations.lock().expect("SMA HTTP observations");
        if observations.exiting {
            return false;
        }
        observations.exiting = true;
        observations.pending = None;
        self.scheduler.stop_all();
        true
    }

    pub fn drained(&self) -> bool {
        self.scheduler.status(SchedulerSide::Get).active == 0
            && self.scheduler.status(SchedulerSide::Post).active == 0
    }

    pub(crate) fn status(&self) -> RuntimeStatus {
        let mut get = self.scheduler.status(SchedulerSide::Get);
        let mut post = self.scheduler.status(SchedulerSide::Post);
        let mut observations = self.observations.lock().expect("SMA HTTP observations");
        if let Ok(config) = self.config.load() {
            if get.phase == SchedulerPhase::Stopped {
                get.limits = limits(&config, SchedulerSide::Get);
            }
            if post.phase == SchedulerPhase::Stopped {
                post.limits = limits(&config, SchedulerSide::Post);
            }
            let current: BTreeSet<_> = config
                .document
                .mappings
                .iter()
                .filter_map(|m| m["id"].as_str())
                .collect();
            observations
                .mappings
                .retain(|id, _| current.contains(id.as_str()));
            observations
                .unknown
                .retain(|id, _| current.contains(id.as_str()));
            let sources: BTreeSet<_> = config
                .document
                .http_sources
                .iter()
                .filter_map(|source| source["sourceKey"].as_str())
                .collect();
            observations
                .sources
                .retain(|key, _| sources.contains(key.as_str()));
        }
        RuntimeStatus {
            get,
            post,
            mappings: observations.mappings.clone(),
            last_unknown: observations.unknown.clone(),
        }
    }

    fn plan(&self, side: SchedulerSide) -> Result<SchedulerBatch, String> {
        let config = self.config.load()?;
        let jobs = match side {
            SchedulerSide::Get => config
                .document
                .http_sources
                .iter()
                .filter(|s| s["enabled"] == true)
                .map(|s| ScheduledJob {
                    key: s["sourceKey"].as_str().unwrap_or_default().into(),
                    target: None,
                    interval_ms: s["intervalMs"].as_u64().unwrap_or_default(),
                })
                .collect(),
            SchedulerSide::Post => config
                .document
                .mappings
                .iter()
                .filter(|m| m["enabled"] == true && m["maxAgeMs"].is_number())
                .filter_map(|m| {
                    let key = m["id"].as_str()?.to_owned();
                    let target = config
                        .document
                        .target_apis
                        .iter()
                        .find(|t| t["apiKey"] == m["targetApiKey"])?;
                    Some(ScheduledJob {
                        key,
                        target: domain::target_group(&config, target).ok(),
                        interval_ms: m["intervalMs"].as_u64().unwrap_or_default(),
                    })
                })
                .collect(),
        };
        Ok(SchedulerBatch {
            limits: limits(&config, side),
            jobs,
        })
    }

    async fn run_get(&self, job: ScheduledJob, activity: RequestActivity) -> JobResult {
        let Ok(client) = self.client() else {
            return JobResult::Failed;
        };
        let Ok(config) = self.config.load() else {
            return JobResult::Failed;
        };
        let Ok((definition, source)) = source(&config, &job.key) else {
            return JobResult::Discarded;
        };
        if !source.enabled {
            return JobResult::Discarded;
        }
        let test = transport::collect(client, &source, activity).await;
        if test.error_code.as_deref() == Some("SMA_RUNTIME_DISPATCH_CANCELLED") {
            return JobResult::Discarded;
        }
        let time = business_now_string();
        let (version, error) = if let Some(error) = test.error_code {
            (None, Some(error))
        } else {
            match self
                .config
                .publish_http_snapshot(definition, time.clone(), test.points)
            {
                Ok(s) => (Some(s.version), None),
                Err(error) => (None, Some(error)),
            }
        };
        let result = get_outcome(error.as_deref());
        let mut observations = self.observations.lock().expect("SMA HTTP observations");
        let entry = observations.sources.entry(job.key.clone()).or_default();
        if entry.error != error {
            if let Some(code) = &error {
                tracing::warn!(event = "sma_http_collect", resource = %job.key, result = "failed", error_code = %code);
            } else {
                tracing::info!(event = "sma_http_collect", resource = %job.key, result = "recovered");
            }
        }
        entry.time = time;
        entry.error = error;
        if version.is_some() {
            entry.own_version = version;
        }
        result
    }

    async fn run_post(&self, job: ScheduledJob, activity: RequestActivity) -> JobResult {
        let Ok(client) = self.client() else {
            return JobResult::Failed;
        };
        let input = self
            .mapping_input(&job.key)
            .and_then(|(config, states)| domain::evaluate_mapping(&config, &states, &job.key));
        let result = match input {
            Ok((group, preview)) => {
                if job.target.as_deref() != Some(group.as_str()) {
                    return JobResult::Discarded;
                }
                transport::post(client, preview, activity).await
            }
            Err(error) => PostResult {
                run_id: uuid::Uuid::new_v4().to_string(),
                status: "blocked",
                http_status: None,
                error_code: Some(error),
                response: None,
                finished_at: business_now_string(),
                sources: vec![],
                diagnostics: vec![],
            },
        };
        let outcome = post_outcome(&result);
        if !matches!(outcome, JobResult::Discarded) {
            self.record(&job.key, &result);
        }
        outcome
    }

    fn record(&self, key: &str, result: &PostResult) {
        let mut observations = self.observations.lock().expect("SMA HTTP observations");
        let previous = observations.mappings.get(key);
        if result.status == "unknown"
            || previous.is_none_or(|previous| {
                previous.status != result.status || previous.error_code != result.error_code
            })
        {
            tracing::info!(event = "sma_http_post", resource = key, run_id = %result.run_id,
                result = result.status, http_status = result.http_status, error_code = result.error_code.as_deref());
        }
        let mut summary = result.clone();
        summary.response = None;
        if summary.status == "unknown" {
            observations.unknown.insert(key.into(), summary.clone());
        }
        observations.mappings.insert(key.into(), summary);
    }

    fn mapping_input(&self, id: &str) -> Result<(ConfigurationSnapshot, Vec<SourceState>), String> {
        let (config, snapshots) = self.config.with_http_snapshots(|document| {
            let mapping = document.mappings.iter().find(|m| m["id"] == id);
            mapping
                .and_then(|m| m["bindings"].as_object())
                .into_iter()
                .flat_map(|bindings| {
                    bindings
                        .values()
                        .filter_map(|binding| binding["sourceKey"].as_str().map(str::to_owned))
                })
                .collect::<BTreeSet<_>>()
                .into_iter()
                .collect()
        })?;
        let states = snapshots
            .into_iter()
            .map(|snapshot| SourceState {
                source_key: snapshot.source_key.clone(),
                snapshot: Some(snapshot),
                ..Default::default()
            })
            .collect();
        Ok((config, states))
    }
}

fn source<'a>(
    config: &'a ConfigurationSnapshot,
    key: &str,
) -> Result<(&'a Value, HttpSource), String> {
    let definition = config
        .document
        .http_sources
        .iter()
        .find(|s| s["sourceKey"] == key || s["id"] == key)
        .ok_or("SMA_CONFIGURATION_NOT_FOUND")?;
    let source =
        serde_json::from_value(definition.clone()).map_err(|_| "SMA_HTTP_SOURCE_INVALID")?;
    Ok((definition, source))
}

fn require_revision(config: &ConfigurationSnapshot, expected: u64) -> Result<(), String> {
    if config.revision != expected {
        return Err("SMA_CONFIGURATION_CONFLICT".into());
    }
    Ok(())
}

fn limits(config: &ConfigurationSnapshot, side: SchedulerSide) -> SchedulerLimits {
    let limits = config.document.runtime_limits.clone().unwrap_or_default();
    match side {
        SchedulerSide::Get => SchedulerLimits {
            concurrency: limits.get_concurrency,
            queue: limits.get_queue,
            per_target: limits.get_concurrency,
        },
        SchedulerSide::Post => SchedulerLimits {
            concurrency: limits.post_concurrency,
            queue: limits.post_queue,
            per_target: limits.per_target_concurrency,
        },
    }
}

fn get_outcome(error: Option<&str>) -> JobResult {
    match error {
        None => JobResult::Completed,
        Some("SMA_HTTP_TIMED_OUT") => JobResult::TimedOut,
        Some("SMA_RUNTIME_DISPATCH_CANCELLED") => JobResult::Discarded,
        Some(_) => JobResult::Failed,
    }
}

fn post_outcome(result: &PostResult) -> JobResult {
    if result.error_code.as_deref() == Some("SMA_RUNTIME_DISPATCH_CANCELLED") {
        return JobResult::Discarded;
    }
    match result.status {
        "http_succeeded" | "succeeded" => JobResult::Completed,
        "blocked" => JobResult::Blocked,
        "unknown" if result.error_code.as_deref() == Some("SMA_HTTP_TIMED_OUT") => {
            JobResult::UnknownTimedOut
        }
        "unknown" => JobResult::Unknown,
        _ => JobResult::Failed,
    }
}

#[cfg(test)]
#[path = "http_mapping/acceptance_tests.rs"]
mod acceptance_tests;
