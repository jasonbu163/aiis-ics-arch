//! SMA 有界 HTTP 传输。关闭重定向和自动重试，超时覆盖响应读取。
use crate::{
    contracts::http_mapping::*,
    domain::{http_mapping as domain, runtime::business_now_string},
    services::http_scheduler::RequestActivity,
};
use reqwest::{Client, Response};
use serde_json::Value;
use std::time::Duration;

const MAX_RESPONSE_BYTES: usize = 4 * 1024 * 1024;

pub fn client() -> Result<Client, String> {
    Client::builder()
        .redirect(reqwest::redirect::Policy::none())
        .retry(reqwest::retry::never())
        .timeout(Duration::from_secs(60))
        .build()
        .map_err(|_| "SMA_HTTP_CLIENT_UNAVAILABLE".into())
}

pub(crate) async fn collect(
    client: &Client,
    source: &HttpSource,
    activity: RequestActivity,
) -> SourceTest {
    let mut test = SourceTest {
        source_key: source.source_key.clone(),
        http_status: None,
        response: None,
        points: vec![],
        error_code: None,
    };
    let result = async {
        let mut url = domain::http_url(&source.url)?;
        if !source.query.is_empty() {
            let retained = url
                .query_pairs()
                .into_owned()
                .filter(|(key, _)| !source.query.contains_key(key))
                .collect::<Vec<_>>();
            url.set_query(None);
            url.query_pairs_mut()
                .extend_pairs(retained)
                .extend_pairs(&source.query);
        }
        let request = client
            .get(url)
            .timeout(Duration::from_millis(source.timeout_ms))
            .header(reqwest::header::ACCEPT, "application/json");
        let active = activity.begin_http()?;
        let response = request.send().await.map_err(network_error)?;
        test.http_status = Some(response.status().as_u16());
        if !response.status().is_success() {
            return Err("SMA_HTTP_SOURCE_HTTP_FAILED".into());
        }
        let raw = body(response).await?;
        drop(active);
        let value: Value =
            serde_json::from_slice(&raw).map_err(|_| "SMA_HTTP_SOURCE_JSON_INVALID")?;
        let readings = domain::extract_points(source, &value);
        test.response = Some(value);
        test.points = readings?;
        Ok(())
    }
    .await;
    test.error_code = result.err();
    test
}

pub(crate) async fn post(
    client: &Client,
    preview: PostPreview,
    activity: RequestActivity,
) -> PostResult {
    let mut result = PostResult {
        run_id: uuid::Uuid::new_v4().to_string(),
        status: "blocked",
        http_status: None,
        error_code: None,
        response: None,
        finished_at: String::new(),
        sources: preview.sources,
        diagnostics: preview.diagnostics,
    };
    if let Some(request) = preview.request {
        send(client, request, activity, &mut result).await;
    } else {
        result.error_code = Some("SMA_HTTP_MAPPING_BLOCKED".into());
    }
    result.finished_at = business_now_string();
    result
}

async fn send(
    client: &Client,
    request: PreparedPost,
    activity: RequestActivity,
    result: &mut PostResult,
) {
    let receipt = request.receipt;
    let mut builder = client
        .post(&request.url)
        .timeout(Duration::from_millis(request.timeout_ms));
    if !request
        .headers
        .iter()
        .any(|(name, _)| name.eq_ignore_ascii_case("accept"))
    {
        builder = builder.header(reqwest::header::ACCEPT, "application/json");
    }
    for (name, value) in request.headers {
        builder = builder.header(name, value);
    }
    let built = match builder.json(&request.body).build() {
        Ok(request) => request,
        Err(_) => {
            result.error_code = Some("SMA_HTTP_REQUEST_INVALID".into());
            return;
        }
    };
    let active = match activity.begin_http() {
        Ok(active) => active,
        Err(code) => {
            result.error_code = Some(code);
            return;
        }
    };
    let response = match client.execute(built).await {
        Ok(response) => response,
        Err(error) => {
            result.status = "unknown";
            result.error_code = Some(network_error(error));
            return;
        }
    };
    let status = response.status();
    result.http_status = Some(status.as_u16());
    if !status.is_success() {
        result.status = "failed";
        result.error_code = Some("SMA_HTTP_POST_HTTP_FAILED".into());
        result.response = body(response)
            .await
            .ok()
            .and_then(|bytes| serde_json::from_slice(&bytes).ok());
        return;
    }
    let bytes = match body(response).await {
        Ok(bytes) => bytes,
        Err(code) => {
            result.status = "unknown";
            result.error_code = Some(code);
            return;
        }
    };
    drop(active);
    result.response = serde_json::from_slice(&bytes).ok();
    if let Some(condition) = receipt {
        match result
            .response
            .as_ref()
            .and_then(|v| domain::condition_result(&condition, v))
        {
            Some(true) => result.status = "succeeded",
            Some(false) => {
                result.status = "failed";
                result.error_code = Some("SMA_HTTP_BUSINESS_REJECTED".into());
            }
            None => {
                result.status = "unknown";
                result.error_code = Some("SMA_HTTP_RECEIPT_INVALID".into());
            }
        }
    } else {
        result.status = "http_succeeded";
    }
}

async fn body(mut response: Response) -> Result<Vec<u8>, String> {
    let mut result = Vec::new();
    while let Some(chunk) = response.chunk().await.map_err(network_error)? {
        if result.len() + chunk.len() > MAX_RESPONSE_BYTES {
            return Err("SMA_HTTP_RESPONSE_TOO_LARGE".into());
        }
        result.extend_from_slice(&chunk);
    }
    Ok(result)
}

fn network_error(error: reqwest::Error) -> String {
    if error.is_timeout() {
        "SMA_HTTP_TIMED_OUT"
    } else {
        "SMA_HTTP_TRANSPORT_INTERRUPTED"
    }
    .into()
}
