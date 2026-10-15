//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/mapping_runtime/mod.rs
//! Description: HTTP-only execution service for confirmed Mapping manual runs and continuous runtime.
//! Main Features:
//!   - Claims Backend-owned immutable Mapping snapshots and completes safe audit records
//!   - Reads fresh bound facts on every Mapping interval and and persists Backend-owned Mapping state
//!   - Disables redirects and retries; ambiguous target outcomes are never replayed

use std::collections::BTreeSet;
use std::time::Duration;

use reqwest::header::{HeaderName, HeaderValue};
use reqwest::{Client, Method, StatusCode, Url};
use serde::de::DeserializeOwned;
use serde::Serialize;
use tokio::time::Instant;

use crate::config::runtime_startup::{self, RuntimeStartupPreferences};
use crate::domain::mapping_runtime::{
    delivery_fingerprint, evaluate_snapshot, mapping_runtime_snapshot_from_facts,
    ApiFirstMappingRuntimeStartRequest, BackendEnvelope, BackendFactSnapshot, BackendManualRun,
    BackendManualRunClaim, BackendManualRunCompleteRequest, BackendMappingRuntimeClaim,
    BackendMappingRuntimeCompleteRequest, BackendMappingRuntimeConfiguration,
    BackendMappingRuntimeState, ManualRunEvaluation, MappingManualRunResult,
    MappingRuntimeDiagnostic, MappingRuntimePoint, OutboundRequest,
};
use crate::domain::runtime::{
    runtime_run_id, utc_now_string, ManagedRuntimeState, RuntimeSnapshot, RuntimeStartRequest,
};

const BACKEND_REQUEST_TIMEOUT_MS: u64 = 5_000;
const CONTROL_POLL_MS: u64 = 20;
const BOUND_FACTS_MAX_COUNT: usize = 500;

#[derive(Clone)]
struct BackendManualRunClient {
    client: Client,
    base_url: Url,
}

enum TargetRequestError {
    Configuration,
    Ambiguous,
}

impl BackendManualRunClient {
    fn from_saved_base_url(value: &str) -> Result<Self, String> {
        let mut base_url = Url::parse(value.trim())
            .map_err(|_| "MAPPING_MANUAL_RUN_BACKEND_URL_INVALID".to_string())?;
        if !matches!(base_url.scheme(), "http" | "https")
            || base_url.host_str().is_none()
            || !base_url.username().is_empty()
            || base_url.password().is_some()
            || base_url.path() != "/"
            || base_url.query().is_some()
            || base_url.fragment().is_some()
        {
            return Err("MAPPING_MANUAL_RUN_BACKEND_URL_INVALID".to_string());
        }
        base_url.set_path("/");
        let client = Client::builder()
            .timeout(Duration::from_millis(BACKEND_REQUEST_TIMEOUT_MS))
            .redirect(reqwest::redirect::Policy::none())
            .retry(reqwest::retry::never())
            .build()
            .map_err(|_| "MAPPING_MANUAL_RUN_HTTP_CLIENT_INVALID".to_string())?;
        Ok(Self { client, base_url })
    }

    fn endpoint(&self, segments: &[&str]) -> Result<Url, String> {
        let mut url = self.base_url.clone();
        let mut path_segments = url
            .path_segments_mut()
            .map_err(|_| "MAPPING_MANUAL_RUN_BACKEND_URL_INVALID".to_string())?;
        path_segments.clear();
        for segment in segments {
            path_segments.push(segment);
        }
        drop(path_segments);
        Ok(url)
    }

    async fn claim(
        &self,
        mapping_id: &str,
        expected_row_version: &str,
    ) -> Result<BackendManualRunClaim, String> {
        if !is_saved_mapping_id(mapping_id) || expected_row_version.trim().is_empty() {
            return Err("MAPPING_MANUAL_RUN_INPUT_INVALID".to_string());
        }
        let url = self.endpoint(&[
            "api",
            "tss",
            "v1",
            "mappings",
            mapping_id,
            "manual-runs",
            "claim",
        ])?;
        self.backend_data(
            self.client
                .post(url)
                .header("accept", "application/json")
                .json(&ClaimRequest {
                    expected_row_version,
                }),
        )
        .await
    }

    async fn complete(
        &self,
        run_id: &str,
        request: &BackendManualRunCompleteRequest,
    ) -> Result<BackendManualRun, String> {
        if !is_saved_mapping_id(run_id) {
            return Err("MAPPING_MANUAL_RUN_BACKEND_RESPONSE_INVALID".to_string());
        }
        let url = self.endpoint(&[
            "api",
            "tss",
            "v1",
            "mapping-manual-runs",
            run_id,
            "complete",
        ])?;
        self.backend_data(
            self.client
                .post(url)
                .header("accept", "application/json")
                .json(request),
        )
        .await
    }

    async fn runtime_configurations(
        &self,
    ) -> Result<Vec<BackendMappingRuntimeConfiguration>, String> {
        let url = self.endpoint(&["api", "tss", "v1", "mapping-runtime", "configurations"])?;
        self.backend_data(self.client.get(url).header("accept", "application/json"))
            .await
    }

    async fn snapshot_facts(
        &self,
        points: &[MappingRuntimePoint],
    ) -> Result<BackendFactSnapshot, String> {
        if points.is_empty() || points.len() > BOUND_FACTS_MAX_COUNT {
            return Err("MAPPING_RUNTIME_INPUT_TOO_LARGE".to_string());
        }
        let url = self.endpoint(&["api", "integration", "v1", "collection-facts", "snapshot"])?;
        self.backend_data(
            self.client
                .post(url)
                .header("accept", "application/json")
                .json(&FactPointRequest::new(points)),
        )
        .await
    }

    async fn claim_runtime(
        &self,
        mapping_id: &str,
        runtime_id: &str,
        expected_mapping_row_version: &str,
        expected_target_api_row_version: &str,
    ) -> Result<BackendMappingRuntimeClaim, String> {
        if !is_saved_mapping_id(mapping_id) {
            return Err("MAPPING_RUNTIME_INPUT_INVALID".to_string());
        }
        let url = self.endpoint(&["api", "tss", "v1", "mapping-runtime", mapping_id, "claim"])?;
        self.backend_data(
            self.client
                .post(url)
                .header("accept", "application/json")
                .json(&RuntimeClaimRequest {
                    runtime_id,
                    expected_mapping_row_version,
                    expected_target_api_row_version,
                }),
        )
        .await
    }

    async fn complete_runtime(
        &self,
        mapping_id: &str,
        request: &BackendMappingRuntimeCompleteRequest,
    ) -> Result<BackendMappingRuntimeState, String> {
        if !is_saved_mapping_id(mapping_id) {
            return Err("MAPPING_RUNTIME_INPUT_INVALID".to_string());
        }
        let url = self.endpoint(&[
            "api",
            "tss",
            "v1",
            "mapping-runtime",
            mapping_id,
            "complete",
        ])?;
        self.backend_data(
            self.client
                .post(url)
                .header("accept", "application/json")
                .json(request),
        )
        .await
    }

    async fn backend_data<T>(&self, request: reqwest::RequestBuilder) -> Result<T, String>
    where
        T: DeserializeOwned,
    {
        let response = request.send().await.map_err(backend_request_error)?;
        let status = response.status();
        let envelope = response
            .json::<BackendEnvelope<T>>()
            .await
            .map_err(|_| "MAPPING_MANUAL_RUN_BACKEND_RESPONSE_INVALID".to_string())?;
        ensure_backend_success(status, envelope)
    }
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct ClaimRequest<'a> {
    expected_row_version: &'a str,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct FactPointRequest {
    points: Vec<FactPointIdentity>,
}

impl FactPointRequest {
    fn new(points: &[MappingRuntimePoint]) -> Self {
        Self {
            points: points
                .iter()
                .map(|point| FactPointIdentity {
                    source_key: point.source_key.clone(),
                    name: point.name.clone(),
                })
                .collect(),
        }
    }
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct FactPointIdentity {
    source_key: String,
    name: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct RuntimeClaimRequest<'a> {
    runtime_id: &'a str,
    expected_mapping_row_version: &'a str,
    expected_target_api_row_version: &'a str,
}

pub async fn run_mapping_manual_once(
    mapping_id: String,
    expected_row_version: String,
    backend_base_url: String,
) -> Result<MappingManualRunResult, String> {
    let backend = BackendManualRunClient::from_saved_base_url(&backend_base_url)?;
    let claim = backend.claim(&mapping_id, &expected_row_version).await?;
    if !claim.claimed {
        let mut result = MappingManualRunResult::from_audit(&claim.run, Vec::new());
        result.error_code = claim.error_code.or(result.error_code);
        return Ok(result);
    }
    let snapshot = match claim.snapshot {
        Some(snapshot) if snapshot.snapshot_id == claim.run.snapshot_id => snapshot,
        _ => {
            return complete_configuration_rejection(&backend, &claim.run, Vec::new()).await;
        }
    };
    match evaluate_snapshot(&snapshot) {
        Ok(evaluation) => execute_evaluation(&backend, &claim.run, evaluation).await,
        Err(_) => complete_configuration_rejection(&backend, &claim.run, Vec::new()).await,
    }
}

pub fn load_runtime_startup_preferences(
    app: &tauri::AppHandle,
) -> Result<RuntimeStartupPreferences, String> {
    runtime_startup::load(app)
}

pub fn save_runtime_startup_preferences(
    app: &tauri::AppHandle,
    preferences: RuntimeStartupPreferences,
) -> Result<(), String> {
    runtime_startup::save(app, &preferences)
}

async fn execute_evaluation(
    backend: &BackendManualRunClient,
    run: &BackendManualRun,
    evaluation: ManualRunEvaluation,
) -> Result<MappingManualRunResult, String> {
    let unresolved_parameter_keys = evaluation
        .diagnostics
        .iter()
        .map(|diagnostic| diagnostic.parameter_key.clone())
        .collect::<Vec<_>>();
    let Some(request) = evaluation.request else {
        return complete_run(
            backend,
            run,
            BackendManualRunCompleteRequest {
                status: "preflight_rejected".to_string(),
                error_code: Some("tss_mapping_manual_run_required_unresolved".to_string()),
                http_status_class: None,
                response_summary: "required parameters were unresolved".to_string(),
                resolved_parameter_keys: evaluation.resolved_parameter_keys,
                unresolved_parameter_keys,
            },
            evaluation.diagnostics,
        )
        .await;
    };
    match send_saved_target_request(backend, request).await {
        Ok(status) if status.is_success() => {
            complete_run(
                backend,
                run,
                BackendManualRunCompleteRequest {
                    status: "succeeded".to_string(),
                    error_code: None,
                    http_status_class: status_class(status),
                    response_summary: "target returned a successful response".to_string(),
                    resolved_parameter_keys: evaluation.resolved_parameter_keys,
                    unresolved_parameter_keys,
                },
                evaluation.diagnostics,
            )
            .await
        }
        Ok(status) => {
            complete_run(
                backend,
                run,
                BackendManualRunCompleteRequest {
                    status: "request_failed".to_string(),
                    error_code: Some("tss_mapping_manual_run_request_failed".to_string()),
                    http_status_class: status_class(status),
                    response_summary: "target returned a non-success response".to_string(),
                    resolved_parameter_keys: evaluation.resolved_parameter_keys,
                    unresolved_parameter_keys,
                },
                evaluation.diagnostics,
            )
            .await
        }
        Err(TargetRequestError::Configuration) => {
            complete_run(
                backend,
                run,
                BackendManualRunCompleteRequest {
                    status: "preflight_rejected".to_string(),
                    error_code: Some("tss_mapping_manual_run_config_unavailable".to_string()),
                    http_status_class: None,
                    response_summary: "configuration changed before execution".to_string(),
                    resolved_parameter_keys: evaluation.resolved_parameter_keys,
                    unresolved_parameter_keys,
                },
                evaluation.diagnostics,
            )
            .await
        }
        Err(TargetRequestError::Ambiguous) => {
            complete_run(
                backend,
                run,
                BackendManualRunCompleteRequest {
                    status: "request_ambiguous".to_string(),
                    error_code: Some("tss_mapping_manual_run_request_ambiguous".to_string()),
                    http_status_class: None,
                    response_summary: "target response was not determinable".to_string(),
                    resolved_parameter_keys: evaluation.resolved_parameter_keys,
                    unresolved_parameter_keys,
                },
                evaluation.diagnostics,
            )
            .await
        }
    }
}

async fn complete_configuration_rejection(
    backend: &BackendManualRunClient,
    run: &BackendManualRun,
    diagnostics: Vec<MappingRuntimeDiagnostic>,
) -> Result<MappingManualRunResult, String> {
    complete_run(
        backend,
        run,
        BackendManualRunCompleteRequest {
            status: "preflight_rejected".to_string(),
            error_code: Some("tss_mapping_manual_run_config_unavailable".to_string()),
            http_status_class: None,
            response_summary: "configuration changed before execution".to_string(),
            resolved_parameter_keys: Vec::new(),
            unresolved_parameter_keys: diagnostics
                .iter()
                .map(|diagnostic| diagnostic.parameter_key.clone())
                .collect(),
        },
        diagnostics,
    )
    .await
}

async fn complete_run(
    backend: &BackendManualRunClient,
    run: &BackendManualRun,
    request: BackendManualRunCompleteRequest,
    diagnostics: Vec<MappingRuntimeDiagnostic>,
) -> Result<MappingManualRunResult, String> {
    let completed = backend.complete(&run.run_id, &request).await?;
    Ok(MappingManualRunResult::from_audit(&completed, diagnostics))
}

async fn send_saved_target_request(
    backend: &BackendManualRunClient,
    request: OutboundRequest,
) -> Result<StatusCode, TargetRequestError> {
    let url = saved_target_url(backend, &request).map_err(|_| TargetRequestError::Configuration)?;
    let method = Method::from_bytes(request.method.as_bytes())
        .map_err(|_| TargetRequestError::Configuration)?;
    let mut builder = backend
        .client
        .request(method, url)
        .header("accept", "application/json")
        .json(&request.body);
    for (name, value) in request.headers {
        let header_name = HeaderName::from_bytes(name.as_bytes())
            .map_err(|_| TargetRequestError::Configuration)?;
        let header_value =
            HeaderValue::from_str(&value).map_err(|_| TargetRequestError::Configuration)?;
        builder = builder.header(header_name, header_value);
    }
    builder
        .send()
        .await
        .map(|response| response.status())
        .map_err(|_| TargetRequestError::Ambiguous)
}

fn saved_target_url(
    backend: &BackendManualRunClient,
    request: &OutboundRequest,
) -> Result<Url, String> {
    if !request.path.starts_with('/')
        || request.path.starts_with("//")
        || request.path.contains('?')
        || request.path.contains('#')
    {
        return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
    }
    let mut url = backend.base_url.clone();
    let mut path_segments = url
        .path_segments_mut()
        .map_err(|_| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?;
    path_segments.clear();
    for segment in request.path.trim_start_matches('/').split('/') {
        if segment.is_empty() {
            return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string());
        }
        let value = match segment
            .strip_prefix('{')
            .and_then(|value| value.strip_suffix('}'))
        {
            Some(name) if !name.is_empty() => request
                .path_parameters
                .get(name)
                .map(String::as_str)
                .ok_or_else(|| "MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())?,
            Some(_) => return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string()),
            None if segment.contains('{') || segment.contains('}') => {
                return Err("MAPPING_MANUAL_RUN_CONFIGURATION_INVALID".to_string())
            }
            None => segment,
        };
        path_segments.push(value);
    }
    drop(path_segments);
    if !request.query.is_empty() {
        url.query_pairs_mut()
            .extend_pairs(request.query.iter().map(|(name, value)| (name, value)));
    }
    Ok(url)
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
        return Err(format!("MAPPING_MANUAL_RUN_BACKEND_REJECTED:{detail}"));
    }
    envelope
        .data
        .ok_or_else(|| "MAPPING_MANUAL_RUN_BACKEND_RESPONSE_INVALID".to_string())
}

fn backend_request_error(error: reqwest::Error) -> String {
    if error.is_timeout() {
        "MAPPING_MANUAL_RUN_BACKEND_TIMEOUT".to_string()
    } else {
        "MAPPING_MANUAL_RUN_BACKEND_HTTP_FAILED".to_string()
    }
}

fn status_class(status: StatusCode) -> Option<String> {
    match status.as_u16() / 100 {
        1..=5 => Some(format!("{}xx", status.as_u16() / 100)),
        _ => None,
    }
}

fn is_saved_mapping_id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 36
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
}

#[derive(Clone)]
pub struct ApiFirstMappingRuntimeState(pub ManagedRuntimeState);

impl Default for ApiFirstMappingRuntimeState {
    fn default() -> Self {
        Self(ManagedRuntimeState::new("api_first_mapping"))
    }
}

struct MappingSchedule {
    configuration: BackendMappingRuntimeConfiguration,
    blocked: bool,
    next_due: Instant,
}

enum MappingTickOutcome {
    Interrupted,
    ReadFailed(String),
    Advanced {
        processed_items: u64,
        event: &'static str,
    },
    Blocked {
        error_code: String,
        message: &'static str,
    },
}

impl MappingSchedule {
    fn new(configuration: BackendMappingRuntimeConfiguration) -> Result<Self, String> {
        let _mapping_row_version = configuration
            .mapping
            .row_version
            .as_deref()
            .filter(|value| !value.is_empty())
            .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
        let _target_api_row_version = configuration
            .target_api
            .row_version
            .as_deref()
            .filter(|value| !value.is_empty())
            .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
        if configuration.mapping.id != configuration.state.mapping_config_id
            || configuration.mapping.target_api_id != configuration.target_api.id
            || configuration.target_api.id != configuration.state.target_api_id
        {
            return Err("MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string());
        }
        let mut identities = BTreeSet::new();
        for point in &configuration.points {
            if point.source_key.trim().is_empty()
                || point.name.trim().is_empty()
                || !identities.insert((point.source_key.clone(), point.name.clone()))
            {
                return Err("MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string());
            }
        }
        let mut bound_identities = BTreeSet::new();
        for binding in configuration.mapping.bindings.values() {
            if binding.kind != "fact" {
                continue;
            }
            let source_key = binding
                .source_key
                .as_deref()
                .filter(|value| !value.trim().is_empty())
                .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
            let fact_name = binding
                .fact_name
                .as_deref()
                .filter(|value| !value.trim().is_empty())
                .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
            bound_identities.insert((source_key.to_string(), fact_name.to_string()));
        }
        if identities != bound_identities {
            return Err("MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string());
        }
        Ok(Self {
            configuration,
            blocked: false,
            next_due: Instant::now(),
        })
    }

    fn interval(&self) -> Duration {
        Duration::from_millis(self.configuration.mapping.interval_ms.max(1))
    }

    fn apply_checkpoint(&mut self, state: &BackendMappingRuntimeState) -> Result<(), String> {
        let mapping_row_version = self
            .configuration
            .mapping
            .row_version
            .as_deref()
            .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
        let target_api_row_version = self
            .configuration
            .target_api
            .row_version
            .as_deref()
            .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
        if state.mapping_config_id != self.configuration.mapping.id
            || state.target_api_id != self.configuration.target_api.id
            || state.mapping_row_version != mapping_row_version
            || state.target_api_row_version != target_api_row_version
        {
            return Err("MAPPING_RUNTIME_BACKEND_RESPONSE_INVALID".to_string());
        }
        Ok(())
    }
}

pub async fn start_api_first_mapping_runtime(
    state: &ApiFirstMappingRuntimeState,
    request: ApiFirstMappingRuntimeStartRequest,
) -> Result<RuntimeSnapshot, String> {
    let backend = BackendManualRunClient::from_saved_base_url(&request.backend_base_url)
        .map_err(map_runtime_error)?;
    let lifecycle_request = RuntimeStartRequest {
        channel: "both".to_string(),
        source_key: "api-first-mapping".to_string(),
        stream_key: "mapping-runtime".to_string(),
        interval_ms: CONTROL_POLL_MS,
    };
    state.0.start(
        &lifecycle_request,
        runtime_run_id("api-first-mapping-runtime"),
    )?;
    let spawned = state.clone();
    tauri::async_runtime::spawn(async move {
        run_continuous_mapping_runtime(spawned, backend).await;
    });
    Ok(state.0.snapshot())
}

pub async fn pause_api_first_mapping_runtime(
    state: &ApiFirstMappingRuntimeState,
) -> Result<RuntimeSnapshot, String> {
    state.0.request_pause()?;
    wait_for_status(&state.0, "paused", "MAPPING_RUNTIME_PAUSE_TIMEOUT").await?;
    state.0.log(
        utc_now_string(),
        "api_first_mapping_runtime_paused",
        "success",
        None,
        "Mapping runtime reached a Backend request boundary",
    );
    Ok(state.0.snapshot())
}

pub fn resume_api_first_mapping_runtime(
    state: &ApiFirstMappingRuntimeState,
) -> Result<RuntimeSnapshot, String> {
    state.0.resume()?;
    state.0.log(
        utc_now_string(),
        "api_first_mapping_runtime_resumed",
        "success",
        None,
        "Mapping runtime resumed without catch-up",
    );
    Ok(state.0.snapshot())
}

pub async fn stop_api_first_mapping_runtime(
    state: &ApiFirstMappingRuntimeState,
) -> Result<RuntimeSnapshot, String> {
    state.0.request_stop()?;
    wait_for_terminal(&state.0).await
}

async fn run_continuous_mapping_runtime(
    state: ApiFirstMappingRuntimeState,
    backend: BackendManualRunClient,
) {
    let configurations = match backend
        .runtime_configurations()
        .await
        .map_err(map_runtime_error)
    {
        Ok(configurations) => configurations,
        Err(error) => {
            fail_continuous_runtime(&state.0, &error);
            return;
        }
    };
    let mut schedules = match configurations
        .into_iter()
        .map(MappingSchedule::new)
        .collect::<Result<Vec<_>, _>>()
    {
        Ok(schedules) if !schedules.is_empty() => schedules,
        Ok(_) => {
            fail_continuous_runtime(&state.0, "MAPPING_RUNTIME_CONFIGURATION_EMPTY");
            return;
        }
        Err(error) => {
            fail_continuous_runtime(&state.0, &error);
            return;
        }
    };
    state.0.set_running();
    state.0.set_profile_identity(
        "api-first-mapping-runtime",
        "TSS-021",
        "fresh-facts-per-mapping-interval",
    );
    state.0.log(
        utc_now_string(),
        "api_first_mapping_runtime_started",
        "success",
        None,
        &format!("mappings={}", schedules.len()),
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
            for schedule in &mut schedules {
                if !schedule.blocked {
                    schedule.next_due = resumed_at + schedule.interval();
                }
            }
            paused = false;
        }

        let now = Instant::now();
        let mut handled_due_mapping = false;
        for schedule in &mut schedules {
            if schedule.blocked || schedule.next_due > now {
                continue;
            }
            if state.0.should_stop() || state.0.pause_requested() {
                break;
            }
            handled_due_mapping = true;
            let runtime_id = match state.0.snapshot().run_id {
                Some(value) => value,
                None => {
                    fail_continuous_runtime(&state.0, "MAPPING_RUNTIME_RUN_ID_MISSING");
                    return;
                }
            };
            match run_mapping_tick(&backend, schedule, &state.0, &runtime_id).await {
                Ok(MappingTickOutcome::Interrupted) => break,
                Ok(MappingTickOutcome::ReadFailed(error)) => {
                    state
                        .0
                        .record_failure(&error, "Fresh fact read failed; this cycle was not sent");
                    state.0.log(
                        utc_now_string(),
                        "api_first_mapping_runtime_facts_read_failed",
                        "failed",
                        Some(&error),
                        &format!("mapping_id={}", schedule.configuration.mapping.id),
                    );
                }
                Ok(MappingTickOutcome::Advanced {
                    processed_items,
                    event,
                }) => {
                    state.0.record_success(processed_items, None);
                    state.0.log(
                        utc_now_string(),
                        event,
                        "success",
                        None,
                        &format!("mapping_id={}", schedule.configuration.mapping.id),
                    );
                }
                Ok(MappingTickOutcome::Blocked {
                    error_code,
                    message,
                }) => {
                    schedule.blocked = true;
                    state.0.record_failure(&error_code, message);
                    state.0.log(
                        utc_now_string(),
                        "api_first_mapping_runtime_mapping_blocked",
                        "failed",
                        Some(&error_code),
                        &format!("mapping_id={}", schedule.configuration.mapping.id),
                    );
                }
                Err(error) => {
                    schedule.blocked = true;
                    state
                        .0
                        .record_failure(&error, "Mapping tick stopped without replay");
                    state.0.log(
                        utc_now_string(),
                        "api_first_mapping_runtime_mapping_blocked",
                        "failed",
                        Some(&error),
                        &format!("mapping_id={}", schedule.configuration.mapping.id),
                    );
                }
            }
            schedule.next_due = Instant::now() + schedule.interval();
        }
        if schedules.iter().all(|schedule| schedule.blocked) {
            state.0.finish("blocked");
            return;
        }
        if !handled_due_mapping {
            tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
        }
    }
}

async fn run_mapping_tick(
    backend: &BackendManualRunClient,
    schedule: &mut MappingSchedule,
    state: &ManagedRuntimeState,
    runtime_id: &str,
) -> Result<MappingTickOutcome, String> {
    // A static Mapping needs no Snapshot request. Each bound Mapping reads only its
    // own points, and no values survive this cycle to serve as a fallback.
    let mut items = Vec::new();
    for points in schedule.configuration.points.chunks(BOUND_FACTS_MAX_COUNT) {
        let facts = backend
            .snapshot_facts(points)
            .await
            .map_err(map_runtime_error);
        if state.should_stop() || state.pause_requested() {
            return Ok(MappingTickOutcome::Interrupted);
        }
        match facts {
            Ok(facts) => items.extend(facts.items),
            Err(error) => return Ok(MappingTickOutcome::ReadFailed(error)),
        }
    }
    let snapshot = match mapping_runtime_snapshot_from_facts(
        &schedule.configuration,
        BackendFactSnapshot { items },
    ) {
        Ok(snapshot) => snapshot,
        Err(error) => return Ok(MappingTickOutcome::ReadFailed(error)),
    };
    if state.should_stop() || state.pause_requested() {
        return Ok(MappingTickOutcome::Interrupted);
    }
    let evaluation = match evaluate_snapshot(&snapshot) {
        Ok(evaluation) => evaluation,
        Err(_) => {
            return complete_preflight_rejection(
                backend,
                schedule,
                runtime_id,
                "tss_mapping_runtime_config_unavailable",
                "Saved Mapping configuration could not be evaluated",
            )
            .await;
        }
    };
    let claim = claim_runtime(backend, schedule, runtime_id).await?;
    if !claim.claimed {
        return Ok(MappingTickOutcome::Blocked {
            error_code: claim
                .error_code
                .unwrap_or_else(|| "tss_mapping_runtime_lease_held".to_string()),
            message: "another Mapping runtime owns the current delivery lease",
        });
    }

    let Some(request) = evaluation.request else {
        return complete_preflight_rejection_after_claim(
            backend,
            schedule,
            runtime_id,
            "tss_mapping_runtime_required_unresolved",
            "Required Mapping parameters were unresolved from this cycle snapshot",
        )
        .await;
    };

    let mapping_row_version = schedule
        .configuration
        .mapping
        .row_version
        .as_deref()
        .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
    let target_api_row_version = schedule
        .configuration
        .target_api
        .row_version
        .as_deref()
        .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
    let fingerprint = delivery_fingerprint(&request, mapping_row_version, target_api_row_version);
    // Control may arrive while the Backend claim is in flight. Release the
    // prepared delivery without sending; never carry the read into resume.
    // The existing non-blocking preflight receipt represents the withdrawn input.
    if state.should_stop() || state.pause_requested() {
        complete_runtime(
            backend,
            schedule,
            runtime_id,
            "preflight_rejected",
            None,
            Some("tss_mapping_runtime_required_unresolved"),
        )
        .await?;
        return Ok(MappingTickOutcome::Interrupted);
    }

    match send_saved_target_request(backend, request).await {
        Ok(status) if status.is_success() => {
            let completed = complete_runtime(
                backend,
                schedule,
                runtime_id,
                "succeeded",
                Some(fingerprint),
                None,
            )
            .await?;
            schedule.apply_checkpoint(&completed)?;
            Ok(MappingTickOutcome::Advanced {
                processed_items: 1,
                event: "api_first_mapping_runtime_target_succeeded",
            })
        }
        Ok(_) => {
            complete_runtime(
                backend,
                schedule,
                runtime_id,
                "request_failed",
                None,
                Some("tss_mapping_runtime_request_failed"),
            )
            .await?;
            Ok(MappingTickOutcome::Blocked {
                error_code: "tss_mapping_runtime_request_failed".to_string(),
                message: "target returned a non-success response without replay",
            })
        }
        Err(TargetRequestError::Configuration) => {
            complete_runtime(
                backend,
                schedule,
                runtime_id,
                "preflight_rejected",
                None,
                Some("tss_mapping_runtime_config_unavailable"),
            )
            .await?;
            Ok(MappingTickOutcome::Blocked {
                error_code: "tss_mapping_runtime_config_unavailable".to_string(),
                message: "saved target request configuration was not executable",
            })
        }
        Err(TargetRequestError::Ambiguous) => {
            complete_runtime(
                backend,
                schedule,
                runtime_id,
                "request_ambiguous",
                None,
                Some("tss_mapping_runtime_request_ambiguous"),
            )
            .await?;
            Ok(MappingTickOutcome::Blocked {
                error_code: "tss_mapping_runtime_request_ambiguous".to_string(),
                message: "target outcome was ambiguous and will not be replayed",
            })
        }
    }
}

async fn claim_runtime(
    backend: &BackendManualRunClient,
    schedule: &MappingSchedule,
    runtime_id: &str,
) -> Result<BackendMappingRuntimeClaim, String> {
    let mapping_row_version = schedule
        .configuration
        .mapping
        .row_version
        .as_deref()
        .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
    let target_api_row_version = schedule
        .configuration
        .target_api
        .row_version
        .as_deref()
        .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
    backend
        .claim_runtime(
            &schedule.configuration.mapping.id,
            runtime_id,
            mapping_row_version,
            target_api_row_version,
        )
        .await
        .map_err(map_runtime_error)
}

async fn complete_preflight_rejection(
    backend: &BackendManualRunClient,
    schedule: &mut MappingSchedule,
    runtime_id: &str,
    error_code: &str,
    message: &'static str,
) -> Result<MappingTickOutcome, String> {
    let claim = claim_runtime(backend, schedule, runtime_id).await?;
    if !claim.claimed {
        return Ok(MappingTickOutcome::Blocked {
            error_code: claim
                .error_code
                .unwrap_or_else(|| "tss_mapping_runtime_lease_held".to_string()),
            message: "another Mapping runtime owns the current delivery lease",
        });
    }
    complete_preflight_rejection_after_claim(backend, schedule, runtime_id, error_code, message)
        .await
}

async fn complete_preflight_rejection_after_claim(
    backend: &BackendManualRunClient,
    schedule: &mut MappingSchedule,
    runtime_id: &str,
    error_code: &str,
    message: &'static str,
) -> Result<MappingTickOutcome, String> {
    let completed = complete_runtime(
        backend,
        schedule,
        runtime_id,
        "preflight_rejected",
        None,
        Some(error_code),
    )
    .await?;
    schedule.apply_checkpoint(&completed)?;
    if completed.status == "blocked" {
        return Ok(MappingTickOutcome::Blocked {
            error_code: error_code.to_string(),
            message,
        });
    }
    Ok(MappingTickOutcome::Advanced {
        processed_items: 0,
        event: "api_first_mapping_runtime_preflight_rejected",
    })
}

async fn complete_runtime(
    backend: &BackendManualRunClient,
    schedule: &MappingSchedule,
    runtime_id: &str,
    status: &str,
    delivery_fingerprint: Option<String>,
    error_code: Option<&str>,
) -> Result<BackendMappingRuntimeState, String> {
    let mapping_row_version = schedule
        .configuration
        .mapping
        .row_version
        .clone()
        .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
    let target_api_row_version = schedule
        .configuration
        .target_api
        .row_version
        .clone()
        .ok_or_else(|| "MAPPING_RUNTIME_CONFIGURATION_INVALID".to_string())?;
    backend
        .complete_runtime(
            &schedule.configuration.mapping.id,
            &BackendMappingRuntimeCompleteRequest {
                runtime_id: runtime_id.to_string(),
                expected_mapping_row_version: mapping_row_version,
                expected_target_api_row_version: target_api_row_version,
                status: status.to_string(),
                delivery_fingerprint,
                error_code: error_code.map(ToString::to_string),
            },
        )
        .await
        .map_err(map_runtime_error)
}

async fn wait_for_status(
    state: &ManagedRuntimeState,
    expected: &str,
    error_code: &str,
) -> Result<(), String> {
    let deadline = Instant::now() + Duration::from_millis(BACKEND_REQUEST_TIMEOUT_MS);
    while Instant::now() < deadline {
        if state.snapshot().status == expected {
            return Ok(());
        }
        tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
    }
    Err(error_code.to_string())
}

async fn wait_for_terminal(state: &ManagedRuntimeState) -> Result<RuntimeSnapshot, String> {
    let deadline = Instant::now() + Duration::from_millis(BACKEND_REQUEST_TIMEOUT_MS);
    while Instant::now() < deadline {
        let snapshot = state.snapshot();
        if matches!(snapshot.status.as_str(), "stopped" | "failed" | "blocked") {
            return Ok(snapshot);
        }
        tokio::time::sleep(Duration::from_millis(CONTROL_POLL_MS)).await;
    }
    Err("MAPPING_RUNTIME_STOP_TIMEOUT".to_string())
}

fn finish_stopped(state: &ManagedRuntimeState) {
    state.finish("stopped");
    state.log(
        utc_now_string(),
        "api_first_mapping_runtime_stopped",
        "success",
        None,
        "Mapping runtime stopped at a Backend request boundary",
    );
}

fn fail_continuous_runtime(state: &ManagedRuntimeState, error_code: &str) {
    state.record_failure(error_code, "Mapping runtime stopped without replay");
    state.log(
        utc_now_string(),
        "api_first_mapping_runtime_failed",
        "failed",
        Some(error_code),
        "Mapping runtime stopped without replay",
    );
    state.finish("failed");
}

fn map_runtime_error(error: String) -> String {
    error.replace("MAPPING_MANUAL_RUN", "MAPPING_RUNTIME")
}
