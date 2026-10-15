//! SMA-only configuration: explicit application file, no parent dotenv discovery.
//! Exposes HTTP gating and paths without legacy database/scene credentials.
pub mod runtime_startup;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AppDefaults {
    pub backend_base_url: String,
    pub external_io_enabled: bool,
    pub configuration_source: String,
}

pub fn application_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf()
}
pub fn configuration_path() -> Option<PathBuf> {
    match std::env::var_os("SMA_ENV_FILE") {
        Some(value) => {
            let path = PathBuf::from(value);
            path.is_absolute().then_some(path)
        }
        None => Some(application_root().join(".env")),
    }
}
fn values() -> HashMap<String, String> {
    configuration_path()
        .and_then(|p| dotenvy::from_path_iter(p).ok())
        .map(|entries| {
            entries
                .flatten()
                .filter(|(k, _)| k.starts_with("SMA_"))
                .collect()
        })
        .unwrap_or_default()
}
pub fn load_defaults_from_env() -> AppDefaults {
    let values = values();
    let read = |key: &str| {
        std::env::var(key)
            .ok()
            .or_else(|| values.get(key).cloned())
            .unwrap_or_default()
    };
    AppDefaults {
        backend_base_url: read("SMA_BACKEND_BASE_URL"),
        external_io_enabled: matches!(read("SMA_HTTP_ENABLED").as_str(), "true" | "1"),
        configuration_source: configuration_path()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "invalid_absolute_override".into()),
    }
}
pub fn require_external_io() -> Result<(), String> {
    if load_defaults_from_env().external_io_enabled {
        return Ok(());
    }
    tracing::warn!(
        event = "sma_external_io_rejected",
        process = "aiis-semantic-mapping-agent",
        result = "rejected",
        error_code = "SMA_EXTERNAL_IO_DISABLED"
    );
    Err("SMA_EXTERNAL_IO_DISABLED".into())
}
pub fn profile_override() -> Option<PathBuf> {
    std::env::var_os("SMA_PROFILE_DIR")
        .map(PathBuf::from)
        .filter(|p| p.is_absolute())
}
