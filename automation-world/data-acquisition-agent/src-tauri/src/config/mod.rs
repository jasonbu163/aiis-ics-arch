//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/config/mod.rs
//! Description: DAA 自有环境加载、活动路径与类型配置
//! Main Features:
//!   - Loads local .env values without taking backend .env ownership
//!   - Resolves runtime-relative file paths
//!   - 保留活动值/布尔读取与自有 profile；输出路径仅用于既有测试

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

    /// 只公开键名和发现来源；退役提示不消费或输出其值。
    pub(crate) fn configured_keys(&self) -> std::collections::BTreeSet<String> {
        self.values
            .keys()
            .cloned()
            .chain(std::env::vars_os().filter_map(|(k, _)| k.into_string().ok()))
            .collect()
    }
    pub(crate) fn locator(&self, key: &str, fallback: &str) -> (PathBuf, String) {
        if let Some(v) = std::env::var(key).ok().filter(|v| !v.trim().is_empty()) {
            return (resolve_runtime_path(v.trim()), "process".into());
        }
        if let Some(v) = self.values.get(key).filter(|v| !v.trim().is_empty()) {
            return (resolve_runtime_path(v.trim()), "env_file".into());
        }
        (resolve_runtime_path(fallback), "application_default".into())
    }
    pub(crate) fn value_or_default(&self, key: &str, default_value: &str) -> String {
        std::env::var(key)
            .ok()
            .or_else(|| self.values.get(key).cloned())
            .unwrap_or_else(|| default_value.to_string())
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

#[cfg(test)]
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

        values.entry(key.trim().to_string()).or_insert_with(|| {
            if [
                "DAA_RUNTIME_MODE",
                "DAA_PLC_READ_ALLOWED",
                "DAA_PLC_CONFIG_PATH",
                "DAA_PLC_SNAPSHOT_POLICY_PATH",
            ]
            .contains(&key.trim())
            {
                trim_env_value(value)
            } else {
                String::new()
            }
        });
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

pub(crate) mod local_bootstrap;
