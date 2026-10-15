//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/config/mod.rs
//! Description: Control Agent configuration loading helpers
//! Main Features:
//!   - Loads local .env values without taking backend .env ownership
//!   - Resolves runtime-relative file paths
//!   - Provides typed parsing and non-empty override helpers for services and infrastructure

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

pub(crate) struct AgentConfig {
    values: HashMap<String, String>,
}

impl AgentConfig {
    pub(crate) fn load() -> Self {
        let mut values = HashMap::new();

        for path in candidate_env_paths() {
            load_env_file(&path, &mut values);
        }

        Self { values }
    }

    #[cfg(test)]
    pub(crate) fn from_values(values: HashMap<String, String>) -> Self {
        Self { values }
    }

    #[cfg(test)]
    pub(crate) fn empty_for_test() -> Self {
        Self {
            values: HashMap::new(),
        }
    }

    pub(crate) fn value_or_default(&self, key: &str, default_value: &str) -> String {
        std::env::var(key)
            .ok()
            .or_else(|| self.values.get(key).cloned())
            .unwrap_or_else(|| default_value.to_string())
    }

    pub(crate) fn raw_value(&self, key: &str) -> Option<String> {
        std::env::var(key)
            .ok()
            .or_else(|| self.values.get(key).cloned())
    }

    pub(crate) fn non_empty_value(&self, key: &str) -> Option<String> {
        match std::env::var(key) {
            Ok(value) => {
                let value = value.trim().to_string();
                (!value.is_empty()).then_some(value)
            }
            Err(_) => self
                .values
                .get(key)
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty()),
        }
    }

    pub(crate) fn bool_or_default(&self, key: &str, default_value: bool) -> bool {
        match self
            .value_or_default(key, if default_value { "true" } else { "false" })
            .as_str()
        {
            "1" | "true" | "TRUE" | "True" | "yes" | "YES" | "on" | "ON" => true,
            "0" | "false" | "FALSE" | "False" | "no" | "NO" | "off" | "OFF" => false,
            _ => default_value,
        }
    }

    pub(crate) fn is_configured(&self, key: &str) -> bool {
        std::env::var(key)
            .map(|value| !value.trim().is_empty())
            .unwrap_or_else(|_| {
                self.values
                    .get(key)
                    .map(|value| !value.trim().is_empty())
                    .unwrap_or(false)
            })
    }
}

/// Only this application's explicit absolute file or known source root is read.
fn candidate_env_paths() -> Vec<PathBuf> {
    if let Ok(value) = std::env::var("DAA_ENV_FILE") {
        let path = PathBuf::from(value);
        return if path.is_absolute() {
            vec![path]
        } else {
            vec![]
        };
    }
    vec![application_root().join(".env")]
}

pub(crate) fn application_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf()
}

pub(crate) fn profile_dir() -> PathBuf {
    std::env::var_os("DAA_PROFILE_DIR")
        .map(PathBuf::from)
        .filter(|path| path.is_absolute())
        .unwrap_or_else(|| {
            dirs::data_local_dir()
                .unwrap_or_else(std::env::temp_dir)
                .join("com.aiis.aw.dataacquisitionagent")
        })
}

pub(crate) fn resolve_output_path(value: &str) -> PathBuf {
    let path = PathBuf::from(value);
    if path.is_absolute() {
        path
    } else {
        profile_dir().join(path)
    }
}

fn load_env_file(path: &Path, values: &mut HashMap<String, String>) {
    let Ok(content) = fs::read_to_string(path) else {
        return;
    };

    for raw_line in content.lines() {
        let line = raw_line.trim();

        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        let Some((key, value)) = line.split_once('=') else {
            continue;
        };

        values
            .entry(key.trim().to_string())
            .or_insert_with(|| trim_env_value(value));
    }
}

pub(crate) fn trim_env_value(value: &str) -> String {
    let trimmed = value.trim();

    if trimmed.len() >= 2 {
        let first = trimmed.as_bytes()[0] as char;
        let last = trimmed.as_bytes()[trimmed.len() - 1] as char;

        if (first == '"' && last == '"') || (first == '\'' && last == '\'') {
            return trimmed[1..trimmed.len() - 1].to_string();
        }
    }

    trimmed.to_string()
}

pub(crate) fn parse_u16_or_default(value: &str, default_value: u16) -> u16 {
    value.parse::<u16>().unwrap_or(default_value)
}

pub(crate) fn parse_u64_or_default(value: &str, default_value: u64) -> u64 {
    value.parse::<u64>().unwrap_or(default_value)
}

pub(crate) fn resolve_runtime_path(path_value: &str) -> PathBuf {
    let path = PathBuf::from(path_value);
    if path.is_absolute() {
        path
    } else {
        application_root().join(path)
    }
}

#[cfg(test)]
mod isolation_tests {
    use super::*;

    #[test]
    fn relative_contract_paths_are_anchored_to_this_application() {
        assert_eq!(
            resolve_runtime_path("config/plc_points.yaml"),
            application_root().join("config/plc_points.yaml")
        );
        assert_eq!(resolve_output_path("logs"), profile_dir().join("logs"));
    }

    #[test]
    fn only_daa_namespace_is_consumed() {
        let config = AgentConfig::from_values(HashMap::from([(
            "CONTROL_AGENT_DATABASE_ENABLED".into(),
            "true".into(),
        )]));
        assert!(!config.bool_or_default("DAA_DATABASE_ENABLED", false));
    }
}
