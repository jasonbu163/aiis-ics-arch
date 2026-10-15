//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/config/runtime_startup.rs
//! Description: Local app-open runtime auto-start and Mapping facts polling preference persistence.
//! Main Features:
//!   - Stores only Simulation source selection, Mapping runtime enablement, and facts polling interval in app-data JSON
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
    pub collection_fact_simulation: CollectionFactSimulationAutoStart,
    pub api_mapping_runtime: ApiMappingRuntimeAutoStart,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CollectionFactSimulationAutoStart {
    pub enabled: bool,
    pub source_key: Option<String>,
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
                collection_fact_simulation: CollectionFactSimulationAutoStart {
                    enabled: false,
                    source_key: None,
                },
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
    tracing::info!(event="sma_startup_preferences_loaded", process="aiis-semantic-mapping-agent", path=%path.display(), simulation_autostart=preferences.runtime_auto_start.collection_fact_simulation.enabled, mapping_autostart=preferences.runtime_auto_start.api_mapping_runtime.enabled, result="loaded");
    Ok(preferences)
}

pub fn save(app: &AppHandle, preferences: &RuntimeStartupPreferences) -> Result<(), String> {
    save_to_path(&preferences_path(app)?, preferences)
}

pub fn load_from_path(path: &Path) -> Result<RuntimeStartupPreferences, String> {
    match fs::read_to_string(path) {
        Ok(value) => parse(&value),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            Ok(RuntimeStartupPreferences::default())
        }
        Err(_) => Err("RUNTIME_STARTUP_PREFERENCES_READ_FAILED".to_string()),
    }
}

pub fn save_to_path(path: &Path, preferences: &RuntimeStartupPreferences) -> Result<(), String> {
    validate(preferences)?;
    let content = serde_json::to_string_pretty(preferences)
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

fn parse(value: &str) -> Result<RuntimeStartupPreferences, String> {
    let preferences = serde_json::from_str(value)
        .map_err(|_| "RUNTIME_STARTUP_PREFERENCES_INVALID".to_string())?;
    validate(&preferences)?;
    Ok(preferences)
}

fn validate(preferences: &RuntimeStartupPreferences) -> Result<(), String> {
    if preferences.schema_version != SCHEMA_VERSION {
        return Err("RUNTIME_STARTUP_PREFERENCES_VERSION_UNSUPPORTED".to_string());
    }
    if preferences
        .runtime_auto_start
        .collection_fact_simulation
        .enabled
        && preferences
            .runtime_auto_start
            .collection_fact_simulation
            .source_key
            .as_deref()
            .is_none_or(|source_key| source_key.trim().is_empty())
    {
        return Err("RUNTIME_STARTUP_SIMULATION_SOURCE_REQUIRED".to_string());
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
