//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/config/runtime_startup.rs
//! Description: Local app-open runtime auto-start and Mapping facts polling preference persistence.
//! Main Features:
//!   - Exposes mapping-only IPC preferences; retains the inert v1 producer segment on disk
//!   - Rejects invalid or unknown preference documents without storing credentials or runtime state
//!   - Uses atomic local-file replacement; it never configures operating-system boot start

use std::fs;
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager};

const PREFERENCES_FILE: &str = "runtime-startup.json";
const SCHEMA_VERSION: u8 = 1;
pub const DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS: u64 = 1_000;

fn default_mapping_facts_polling_interval_ms() -> u64 {
    DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RuntimeStartupPreferences {
    pub schema_version: u8,
    pub runtime_auto_start: RuntimeAutoStartPreferences,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RuntimeAutoStartPreferences {
    pub api_mapping_runtime: ApiMappingRuntimeAutoStart,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ApiMappingRuntimeAutoStart {
    pub enabled: bool,
    // Historical preference only: TSS-021 uses each saved Mapping interval.
    #[serde(default = "default_mapping_facts_polling_interval_ms")]
    pub facts_polling_interval_ms: u64,
}

impl Default for RuntimeStartupPreferences {
    fn default() -> Self {
        Self {
            schema_version: SCHEMA_VERSION,
            runtime_auto_start: RuntimeAutoStartPreferences {
                api_mapping_runtime: ApiMappingRuntimeAutoStart {
                    enabled: false,
                    facts_polling_interval_ms: DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS,
                },
            },
        }
    }
}

pub fn load(app: &AppHandle) -> Result<RuntimeStartupPreferences, String> {
    let path = preferences_path(app)?;
    let preferences = load_from_path(&path)?;
    tracing::info!(event="sma_startup_preferences_loaded", process="aiis-semantic-mapping-agent", path=%path.display(), mapping_autostart=preferences.runtime_auto_start.api_mapping_runtime.enabled, result="loaded");
    Ok(preferences)
}

pub fn save(app: &AppHandle, preferences: &RuntimeStartupPreferences) -> Result<(), String> {
    save_to_path(&preferences_path(app)?, preferences)
}

// v1磁盘兼容DTO，无执行者。旧段作为Value惰性保存，不解释其enabled/sourceKey。
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct DiskPreferences {
    schema_version: u8,
    runtime_auto_start: DiskAutoStart,
}
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct DiskAutoStart {
    #[serde(default = "neutral_legacy")]
    collection_fact_simulation: serde_json::Value,
    api_mapping_runtime: ApiMappingRuntimeAutoStart,
}
fn neutral_legacy() -> serde_json::Value {
    serde_json::json!({"enabled": false, "sourceKey": null})
}
impl DiskPreferences {
    fn mapping(&self) -> RuntimeStartupPreferences {
        RuntimeStartupPreferences {
            schema_version: self.schema_version,
            runtime_auto_start: RuntimeAutoStartPreferences {
                api_mapping_runtime: self.runtime_auto_start.api_mapping_runtime.clone(),
            },
        }
    }
}
fn load_disk(path: &Path) -> Result<DiskPreferences, String> {
    let disk: DiskPreferences = match fs::read_to_string(path) {
        Ok(value) => serde_json::from_str(&value)
            .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_INVALID".to_string())?,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => DiskPreferences {
            schema_version: SCHEMA_VERSION,
            runtime_auto_start: DiskAutoStart {
                collection_fact_simulation: neutral_legacy(),
                api_mapping_runtime: RuntimeStartupPreferences::default()
                    .runtime_auto_start
                    .api_mapping_runtime,
            },
        },
        Err(_) => return Err("RUNTIME_STARTUP_PREFERENCES_READ_FAILED".to_string()),
    };
    validate(&disk.mapping())?;
    Ok(disk)
}
pub fn load_from_path(path: &Path) -> Result<RuntimeStartupPreferences, String> {
    Ok(load_disk(path)?.mapping())
}

pub fn save_to_path(path: &Path, preferences: &RuntimeStartupPreferences) -> Result<(), String> {
    validate(preferences)?;
    // Read before writing so corrupt/unknown documents cannot be overwritten by stale UI state.
    let mut disk = load_disk(path)?;
    disk.runtime_auto_start.api_mapping_runtime =
        preferences.runtime_auto_start.api_mapping_runtime.clone();
    let content = serde_json::to_string_pretty(&disk)
        .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_SERIALIZE_FAILED".to_string())?;
    let directory = path
        .parent()
        .ok_or_else(|| "RUNTIME_STARTUP_PREFERENCES_PATH_INVALID".to_string())?;
    fs::create_dir_all(directory)
        .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_DIRECTORY_FAILED".to_string())?;
    let temporary = directory.join(format!(".{PREFERENCES_FILE}.tmp-{}", std::process::id()));
    fs::write(&temporary, content)
        .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_WRITE_FAILED".to_string())?;
    fs::rename(&temporary, path)
        .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_RENAME_FAILED".to_string())
}

fn preferences_path(app: &AppHandle) -> Result<PathBuf, String> {
    crate::config::profile_override()
        .map(Ok)
        .unwrap_or_else(|| app.path().app_data_dir())
        .map(|directory| directory.join(PREFERENCES_FILE))
        .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_PATH_INVALID".to_string())
}

fn validate(preferences: &RuntimeStartupPreferences) -> Result<(), String> {
    if preferences.schema_version != SCHEMA_VERSION {
        return Err("RUNTIME_STARTUP_PREFERENCES_VERSION_UNSUPPORTED".to_string());
    }
    if preferences
        .runtime_auto_start
        .api_mapping_runtime
        .facts_polling_interval_ms
        == 0
    {
        return Err("RUNTIME_STARTUP_MAPPING_FACTS_POLLING_INTERVAL_INVALID".to_string());
    }
    Ok(())
}
