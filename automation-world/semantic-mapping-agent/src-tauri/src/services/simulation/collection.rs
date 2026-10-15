//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/simulation/collection.rs
//! Description: Backend-HTTP per-point Simulation loop for saved collection facts.
//! Main Features:
//!   - Loads facts and enabled rules from Backend HTTP instead of MSSQL
//!   - Batches same-cycle Values API writes and stops on Backend/API failure
//!   - Preserves pause, resume, stop, status, counters, and bounded logs

use std::collections::{BTreeMap, BTreeSet};
use std::time::Duration;

use reqwest::{Client, StatusCode, Url};
use serde::de::DeserializeOwned;
use tokio::time::Instant;

use crate::domain::runtime::{
    runtime_run_id, utc_now_string, RuntimeSnapshot, RuntimeStartRequest,
};

use super::generator;
use super::model::{
    BackendCollectionFactPage, BackendEnvelope, BackendSimulationRule, CollectionFactValueWrite,
    CollectionFactValuesWriteRequest, CollectionSimulationHttpStartRequest,
    CollectionSimulationStartRequest, SimulationFact, SimulationRule,
};
use super::state::CollectionFactSimulationRuntimeState;

const CONTROL_POLL_MS: u64 = 20;
const CONTROL_WAIT_TIMEOUT_MS: u64 = 5_000;
const BACKEND_REQUEST_TIMEOUT_MS: u64 = 5_000;
const MIN_POINT_INTERVAL_MS: u64 = 20;
const MAX_POINT_INTERVAL_MS: u64 = 86_400_000;
const VALUES_API_MAX_COUNT: usize = 500;

#[derive(Debug, Clone)]
struct PlannedRule {
    fact: SimulationFact,
    rule: SimulationRule,
    sequence_index: u64,
    next_due: Instant,
}

#[derive(Debug)]
struct PlannedWrite {
    plan_index: usize,
    name: String,
    value: String,
}

#[derive(Clone)]
struct BackendRuntime {
    client: Client,
    base_url: Url,
    source_key: String,
}

impl BackendRuntime {
    fn from_request(request: &CollectionSimulationHttpStartRequest) -> Result<Self, String> {
        let source_key = request.source_key.trim();
        if source_key.is_empty() {
            return Err("COLLECTION_SIMULATION_SOURCE_REQUIRED".to_string());
        }
        let mut base_url = Url::parse(request.backend_base_url.trim())
            .map_err(|_| "COLLECTION_SIMULATION_BACKEND_URL_INVALID".to_string())?;
        if !matches!(base_url.scheme(), "http" | "https")
            || base_url.host_str().is_none()
            || !base_url.username().is_empty()
            || base_url.password().is_some()
            || base_url.path() != "/"
            || base_url.query().is_some()
            || base_url.fragment().is_some()
        {
            return Err("COLLECTION_SIMULATION_BACKEND_URL_INVALID".to_string());
        }
        base_url.set_path("/");
        let client = Client::builder()
            .timeout(Duration::from_millis(BACKEND_REQUEST_TIMEOUT_MS))
            .build()
            .map_err(|_| "COLLECTION_SIMULATION_BACKEND_CLIENT_INVALID".to_string())?;
        Ok(Self {
            client,
            base_url,
            source_key: source_key.to_string(),
        })
    }

    fn endpoint(&self, path: &str) -> Result<Url, String> {
        self.base_url
            .join(path.trim_start_matches('/'))
            .map_err(|_| "COLLECTION_SIMULATION_BACKEND_URL_INVALID".to_string())
    }
}

pub async fn start_http(
    runtime: &CollectionFactSimulationRuntimeState,
    request: CollectionSimulationHttpStartRequest,
) -> Result<RuntimeSnapshot, String> {
    let backend = BackendRuntime::from_request(&request)?;
    let managed_request = RuntimeStartRequest {
        channel: "both".to_string(),
        source_key: backend.source_key.clone(),
        stream_key: "collection-facts".to_string(),
        interval_ms: MIN_POINT_INTERVAL_MS,
    };
    runtime.0.start(
        &managed_request,
        runtime_run_id("collection-fact-simulation"),
    )?;
    let spawned = runtime.clone();
    tauri::async_runtime::spawn(async move {
        run_loop(spawned, backend).await;
    });
    Ok(runtime.0.snapshot())
}

/// Compatibility adapter for an ignored historical test. It deliberately
/// rejects the retired page-rules input; product commands use start_http.
#[doc(hidden)]
pub async fn start<LegacyConnection>(
    _runtime: &CollectionFactSimulationRuntimeState,
    _legacy_connection: LegacyConnection,
    _request: CollectionSimulationStartRequest,
) -> Result<RuntimeSnapshot, String> {
    Err("COLLECTION_SIMULATION_HTTP_START_REQUIRED".to_string())
}

pub async fn pause(
    state: &CollectionFactSimulationRuntimeState,
) -> Result<RuntimeSnapshot, String> {
    state.0.request_pause()?;
    wait_for_status(&state.0, "paused", "COLLECTION_SIMULATION_PAUSE_TIMEOUT").await?;
    state.0.log(
        utc_now_string(),
        "collection_simulation_paused",
        "success",
        None,
        "pause reached an HTTP Values request boundary",
    );
    Ok(state.0.snapshot())
}

pub fn resume(state: &CollectionFactSimulationRuntimeState) -> Result<RuntimeSnapshot, String> {
    state.0.resume()?;
    state.0.log(
        utc_now_string(),
        "collection_simulation_resumed",
        "success",
        None,
        "collection-fact Simulation resumed without catch-up",
    );
    Ok(state.0.snapshot())
}

pub async fn stop(state: &CollectionFactSimulationRuntimeState) -> Result<RuntimeSnapshot, String> {
    state.0.request_stop()?;
    wait_for_terminal(&state.0).await
}

async fn run_loop(state: CollectionFactSimulationRuntimeState, backend: BackendRuntime) {
    let (contract_version, mut plan) = match build_plan(&backend).await {
        Ok(plan) => plan,
        Err(error) => {
            fail(&state.0, &error);
            return;
        }
    };
    state.0.set_running();
    state.0.log(
        utc_now_string(),
        "collection_simulation_started",
        "success",
        None,
        "per-point Simulation started through Backend HTTP; operators must coordinate external writers",
    );
    let mut paused = false;

    loop {
        if state.0.should_stop() {
            finish_stopped(&state.0);
            return;
        }
        if state.0.pause_requested() {
            state.0.acknowledge_pause();
        }
        if state.0.is_paused() {
            paused = true;
            tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
            continue;
        }
        if paused {
            let resumed_at = Instant::now();
            for item in &mut plan {
                item.next_due = resumed_at + Duration::from_millis(item.rule.interval_ms);
            }
            paused = false;
        }

        let now = Instant::now();
        let mut handled_due_point = false;
        let mut writes = Vec::new();
        for (plan_index, item) in plan.iter_mut().enumerate() {
            if item.next_due > now {
                continue;
            }
            handled_due_point = true;
            let value = if item.rule.write_current_time {
                generator::current_time_value(&item.rule, &item.fact)
            } else {
                generator::value(&item.rule, &item.fact, item.sequence_index)
            };
            let value = match value {
                Ok(value) => value,
                Err(error) => {
                    fail(&state.0, &error);
                    return;
                }
            };
            if generator::should_update(&item.fact, &value) {
                writes.push(PlannedWrite {
                    plan_index,
                    name: item.fact.name.clone(),
                    value,
                });
            }
            if !item.rule.write_current_time {
                item.sequence_index = item.sequence_index.saturating_add(1);
            }
            item.next_due = Instant::now() + Duration::from_millis(item.rule.interval_ms);
        }

        if !writes.is_empty() {
            if let Err(error) = write_due_values(&state, &backend, &contract_version, &writes).await
            {
                fail(&state.0, &error);
                return;
            }
            for write in &writes {
                plan[write.plan_index].fact.value_text = Some(write.value.clone());
            }
            state.0.log(
                utc_now_string(),
                "collection_simulation_values_written",
                "success",
                None,
                &format!(
                    "points={} contract_version={contract_version}",
                    writes.len()
                ),
            );
        }
        if !handled_due_point {
            tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
        }
    }
}

async fn build_plan(backend: &BackendRuntime) -> Result<(String, Vec<PlannedRule>), String> {
    let facts = load_source_facts(backend).await?;
    if facts.is_empty() {
        return Err("COLLECTION_SIMULATION_SOURCE_EMPTY".to_string());
    }
    if facts
        .iter()
        .any(|fact| fact.source_key != backend.source_key)
    {
        return Err("COLLECTION_SIMULATION_BACKEND_RESPONSE_INVALID".to_string());
    }
    let contract_versions = facts
        .iter()
        .map(|fact| fact.contract_version.clone())
        .collect::<BTreeSet<_>>();
    if contract_versions.len() != 1 {
        return Err("COLLECTION_SIMULATION_CONTRACT_VERSION_INVALID".to_string());
    }
    let contract_version = contract_versions
        .into_iter()
        .next()
        .ok_or_else(|| "COLLECTION_SIMULATION_CONTRACT_VERSION_INVALID".to_string())?;
    let by_name = facts
        .into_iter()
        .map(|fact| (fact.name.clone(), fact))
        .collect::<BTreeMap<_, _>>();
    let backend_rules: Vec<BackendSimulationRule> =
        get_backend_data(backend, backend.endpoint("api/tss/v1/simulation-rules")?).await?;
    let rules = backend_rules
        .into_iter()
        .filter(|rule| rule.source_key == backend.source_key && rule.enabled)
        .map(SimulationRule::from)
        .collect::<Vec<_>>();
    if rules.is_empty() {
        return Err("COLLECTION_SIMULATION_ENABLED_POINTS_EMPTY".to_string());
    }

    let mut names = BTreeSet::new();
    let plan = rules
        .into_iter()
        .map(|rule| {
            if !names.insert(rule.fact_name.clone()) {
                return Err(format!(
                    "COLLECTION_SIMULATION_RULE_DUPLICATE:{}",
                    rule.fact_name
                ));
            }
            let fact = by_name.get(&rule.fact_name).cloned().ok_or_else(|| {
                format!("COLLECTION_SIMULATION_FACT_NOT_SAVED:{}", rule.fact_name)
            })?;
            if !(MIN_POINT_INTERVAL_MS..=MAX_POINT_INTERVAL_MS).contains(&rule.interval_ms) {
                return Err(format!(
                    "COLLECTION_SIMULATION_INTERVAL_INVALID:{}",
                    rule.fact_name
                ));
            }
            if rule.write_current_time {
                generator::validate_current_time_rule(&rule, &fact)?;
            } else {
                for index in 0..rule.sequence.len() {
                    generator::value(&rule, &fact, index as u64)?;
                }
            }
            Ok(PlannedRule {
                fact,
                rule,
                sequence_index: 0,
                next_due: Instant::now(),
            })
        })
        .collect::<Result<Vec<_>, String>>()?;
    Ok((contract_version, plan))
}

async fn load_source_facts(backend: &BackendRuntime) -> Result<Vec<SimulationFact>, String> {
    let first_page = get_collection_fact_page(backend, 1).await?;
    if first_page.page_size == 0 {
        return Err("COLLECTION_SIMULATION_BACKEND_RESPONSE_INVALID".to_string());
    }
    let page_count = first_page.total.div_ceil(first_page.page_size);
    let mut facts = first_page.items;
    for page in 2..=page_count {
        facts.extend(get_collection_fact_page(backend, page).await?.items);
    }
    Ok(facts.into_iter().map(SimulationFact::from).collect())
}

async fn get_collection_fact_page(
    backend: &BackendRuntime,
    page: u64,
) -> Result<BackendCollectionFactPage, String> {
    let mut url = backend.endpoint("api/integration/v1/collection-facts")?;
    url.query_pairs_mut()
        .append_pair("sourceKey", &backend.source_key)
        .append_pair("page", &page.to_string())
        .append_pair("pageSize", "100");
    get_backend_data(backend, url).await
}

async fn write_due_values(
    state: &CollectionFactSimulationRuntimeState,
    backend: &BackendRuntime,
    contract_version: &str,
    writes: &[PlannedWrite],
) -> Result<(), String> {
    for chunk in writes.chunks(VALUES_API_MAX_COUNT) {
        let request = CollectionFactValuesWriteRequest {
            contract_version: contract_version.to_string(),
            values: chunk
                .iter()
                .map(|write| CollectionFactValueWrite {
                    name: write.name.clone(),
                    value: write.value.clone(),
                })
                .collect(),
        };
        let mut url = backend.endpoint("api/integration/v1/collection-facts")?;
        {
            let mut segments = url
                .path_segments_mut()
                .map_err(|_| "COLLECTION_SIMULATION_BACKEND_URL_INVALID".to_string())?;
            segments.push(&backend.source_key);
            segments.push("values");
        }
        let response = backend
            .client
            .put(url)
            .header("accept", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(backend_request_error)?;
        let status = response.status();
        let envelope = response
            .json::<BackendEnvelope<serde_json::Value>>()
            .await
            .map_err(|_| "COLLECTION_SIMULATION_BACKEND_RESPONSE_INVALID".to_string())?;
        ensure_backend_success(status, envelope)?;
        state
            .0
            .record_success(chunk.len() as u64, Some(format!("values={}", chunk.len())));
    }
    Ok(())
}

async fn get_backend_data<T>(backend: &BackendRuntime, url: Url) -> Result<T, String>
where
    T: DeserializeOwned,
{
    let response = backend
        .client
        .get(url)
        .header("accept", "application/json")
        .send()
        .await
        .map_err(backend_request_error)?;
    let status = response.status();
    let envelope = response
        .json::<BackendEnvelope<T>>()
        .await
        .map_err(|_| "COLLECTION_SIMULATION_BACKEND_RESPONSE_INVALID".to_string())?;
    ensure_backend_success(status, envelope)
}

fn ensure_backend_success<T>(
    status: StatusCode,
    envelope: BackendEnvelope<T>,
) -> Result<T, String> {
    if !status.is_success() || envelope.code != 200 {
        let detail = envelope
            .error_code
            .or(envelope.message)
            .unwrap_or_else(|| status.as_u16().to_string());
        return Err(format!("COLLECTION_SIMULATION_BACKEND_REJECTED:{detail}"));
    }
    envelope
        .data
        .ok_or_else(|| "COLLECTION_SIMULATION_BACKEND_RESPONSE_INVALID".to_string())
}

fn backend_request_error(error: reqwest::Error) -> String {
    if error.is_timeout() {
        "COLLECTION_SIMULATION_BACKEND_TIMEOUT".to_string()
    } else {
        "COLLECTION_SIMULATION_BACKEND_HTTP_FAILED".to_string()
    }
}

fn fail(state: &crate::domain::runtime::ManagedRuntimeState, error: &str) {
    let code = error
        .split(':')
        .next()
        .unwrap_or("COLLECTION_SIMULATION_FAILED");
    state.record_failure(code, error);
    state.log(
        utc_now_string(),
        "collection_simulation_failed",
        "failed",
        Some(code),
        error,
    );
    state.finish("failed");
}

async fn wait_for_status(
    state: &crate::domain::runtime::ManagedRuntimeState,
    expected: &str,
    timeout: &str,
) -> Result<RuntimeSnapshot, String> {
    for _ in 0..(CONTROL_WAIT_TIMEOUT_MS / CONTROL_POLL_MS) {
        let snapshot = state.snapshot();
        if snapshot.status == expected {
            return Ok(snapshot);
        }
        tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
    }
    Err(timeout.to_string())
}

async fn wait_for_terminal(
    state: &crate::domain::runtime::ManagedRuntimeState,
) -> Result<RuntimeSnapshot, String> {
    for _ in 0..(CONTROL_WAIT_TIMEOUT_MS / CONTROL_POLL_MS) {
        let snapshot = state.snapshot();
        if !matches!(
            snapshot.status.as_str(),
            "starting" | "running" | "paused" | "stopping"
        ) {
            return Ok(snapshot);
        }
        tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
    }
    Err("COLLECTION_SIMULATION_STOP_TIMEOUT".to_string())
}

fn finish_stopped(state: &crate::domain::runtime::ManagedRuntimeState) {
    state.finish("stopped");
    state.log(
        utc_now_string(),
        "collection_simulation_stopped",
        "success",
        None,
        "collection-fact Simulation stopped after an HTTP Values request boundary",
    );
}
