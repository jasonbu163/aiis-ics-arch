//! 现有采集 API HTTP adapter：固定同源、限制读取，不发送 Bearer。
use reqwest::{Method, Url};
use serde::Deserialize;
use serde_json::{value::RawValue, Value};
use std::time::Duration;

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Envelope {
    code: u16,
    data: Option<Box<RawValue>>,
    message: Option<String>,
    error_code: Option<String>,
}

pub struct AcquisitionHttp {
    client: reqwest::Client,
    base: Url,
}

#[derive(Debug, Clone)]
pub struct Failure {
    pub code: String,
    pub status: Option<u16>,
    pub unknown: bool,
}

impl Failure {
    pub fn local(code: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            status: None,
            unknown: false,
        }
    }
}

impl From<String> for Failure {
    fn from(value: String) -> Self {
        Self::local(value)
    }
}

impl AcquisitionHttp {
    pub fn new(base: &str) -> Result<Self, Failure> {
        crate::config::require_external_io()?;
        let base =
            Url::parse(base).map_err(|_| Failure::local("SMA_ACQUISITION_CONNECTION_INVALID"))?;
        if !matches!(base.scheme(), "http" | "https")
            || base.host().is_none()
            || !base.username().is_empty()
            || base.password().is_some()
            || base.path() != "/"
            || base.query().is_some()
            || base.fragment().is_some()
        {
            return Err(Failure::local("SMA_ACQUISITION_CONNECTION_INVALID"));
        }
        let client = reqwest::Client::builder()
            .no_proxy()
            .redirect(reqwest::redirect::Policy::none())
            .timeout(Duration::from_secs(8))
            .build()
            .map_err(|_| Failure::local("SMA_ACQUISITION_CONNECTION_INVALID"))?;
        Ok(Self { client, base })
    }

    pub async fn fetch(
        &self,
        method: Method,
        path: &str,
        query: &[(&str, &str)],
        content: Option<Vec<u8>>,
    ) -> Result<Value, Failure> {
        let raw = self.fetch_raw(method, path, query, content).await?;
        serde_json::from_str(raw.get())
            .map_err(|_| Failure::local("SMA_ACQUISITION_RESPONSE_INVALID"))
    }

    pub async fn fetch_raw(
        &self,
        method: Method,
        path: &str,
        query: &[(&str, &str)],
        content: Option<Vec<u8>>,
    ) -> Result<Box<RawValue>, Failure> {
        crate::config::require_external_io()?;
        let url = self
            .base
            .join(path)
            .map_err(|_| Failure::local("SMA_ACQUISITION_CONNECTION_INVALID"))?;
        if url.origin() != self.base.origin() {
            return Err(Failure::local("SMA_ACQUISITION_CONNECTION_INVALID"));
        }
        let posting = method == Method::POST;
        let mut request = self.client.request(method, url).query(query);
        if let Some(bytes) = content {
            request = request
                .header("content-type", "application/json")
                .body(bytes);
        }
        let transport = |error: reqwest::Error| Failure {
            code: if error.is_timeout() {
                "SMA_ACQUISITION_TIMEOUT"
            } else {
                "SMA_ACQUISITION_TRANSPORT"
            }
            .into(),
            status: None,
            unknown: posting,
        };
        let mut response = request.send().await.map_err(transport)?;
        let status = response.status().as_u16();
        let mut bytes = Vec::new();
        while let Some(chunk) = response.chunk().await.map_err(transport)? {
            if bytes.len() + chunk.len() > 16 * 1024 * 1024 {
                return Err(Failure {
                    code: "SMA_ACQUISITION_RESPONSE_INVALID".into(),
                    status: Some(status),
                    unknown: posting,
                });
            }
            bytes.extend_from_slice(&chunk);
        }
        let mut body: Option<Envelope> = serde_json::from_slice(&bytes).ok();
        if status == 200 {
            if let Some(body) = body.as_mut().filter(|body| body.code == 200) {
                if let Some(data) = body.data.take() {
                    return Ok(data);
                }
            }
        }
        let backend = body
            .as_ref()
            .and_then(|body| body.error_code.as_deref().or(body.message.as_deref()))
            .filter(|code| {
                (code.starts_with("plc_facts_v2.") || code.starts_with("plc_facts.v2."))
                    && code.len() <= 96
                    && code
                        .bytes()
                        .all(|char| char.is_ascii_alphanumeric() || matches!(char, b'.' | b'_'))
            });
        let code = backend.unwrap_or(if status == 200 {
            "SMA_ACQUISITION_RESPONSE_INVALID"
        } else {
            "SMA_ACQUISITION_HTTP"
        });
        Err(Failure {
            code: code.into(),
            status: Some(status),
            unknown: posting
                && (code.ends_with(".commit_outcome_unknown")
                    || (backend.is_none() && matches!(status, 200 | 500 | 502..=504))),
        })
    }
}
