//! 文件：src/infrastructure/http.rs；HTTP有界输入服务；无业务重试、代理或重定向。
use crate::{config::Http as Config, domain::Input, Result};
use std::{sync::Arc, time::Duration};
#[derive(Clone)]
pub struct Http {
    client: reqwest::Client,
    slots: Arc<tokio::sync::Semaphore>,
    config: Config,
}
impl Http {
    pub fn new(c: &Config) -> Result<Self> {
        let client = reqwest::Client::builder()
            .no_proxy()
            .redirect(reqwest::redirect::Policy::none())
            .retry(reqwest::retry::never())
            .connect_timeout(Duration::from_millis(c.connect_timeout_ms))
            .timeout(Duration::from_millis(c.total_timeout_ms))
            .pool_max_idle_per_host(c.max_connections)
            .build()
            .map_err(|_| "http_config")?;
        Ok(Self {
            client,
            slots: Arc::new(tokio::sync::Semaphore::new(c.max_connections)),
            config: c.clone(),
        })
    }
    pub async fn get(&self, url: &str) -> Result<Input> {
        tokio::time::timeout(Duration::from_millis(self.config.total_timeout_ms), async {
            let _slot = tokio::time::timeout(
                Duration::from_millis(self.config.pool_wait_ms),
                self.slots.acquire(),
            )
            .await
            .map_err(|_| "http_pool_timeout")?
            .map_err(|_| "http_pool")?;
            let mut response = self
                .client
                .get(url)
                .send()
                .await
                .map_err(|_| "http_communication")?;
            if response.status() != 200 {
                return Err("http_status".into());
            }
            if !response
                .headers()
                .get(reqwest::header::CONTENT_TYPE)
                .and_then(|v| v.to_str().ok())
                .is_some_and(|v| {
                    v.split(';')
                        .next()
                        .is_some_and(|v| v.trim() == "application/json")
                })
            {
                return Err("input_content_type".into());
            }
            if response
                .content_length()
                .is_some_and(|n| n > self.config.max_body_bytes as u64)
            {
                return Err("input_body_size".into());
            }
            let mut b = Vec::new();
            while let Some(chunk) = response.chunk().await.map_err(|_| "http_communication")? {
                if b.len() + chunk.len() > self.config.max_body_bytes {
                    return Err("input_body_size".into());
                }
                b.extend_from_slice(&chunk);
            }
            {
                let v: serde_json::Value =
                    serde_json::from_slice(&b).map_err(|_| "input_schema")?;
                let object = v.as_object().ok_or("input_schema")?;
                let keys = [
                    "schema_version",
                    "source_id",
                    "ready",
                    "command_id",
                    "value",
                    "issued_at_ms",
                    "expires_at_ms",
                ];
                if object.len() != keys.len() || keys.iter().any(|k| !object.contains_key(*k)) {
                    return Err("input_schema".into());
                }
                serde_json::from_value(v).map_err(|_| "input_schema".into())
            }
        })
        .await
        .map_err(|_| "http_timeout")?
    }
}
