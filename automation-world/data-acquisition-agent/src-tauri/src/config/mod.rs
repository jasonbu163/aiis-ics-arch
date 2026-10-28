//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/config/mod.rs
//! Description: DAA 自有环境加载、活动路径与类型配置
//! Main Features:
//!   - Loads local .env values without taking backend .env ownership
//!   - Parses only this app profile/mode values; retired values are ignored
//!   - 显式路径写前拒绝；普通读取准入由bootstrap的process-only规则处理

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

pub(crate) struct AgentConfig {
    values: HashMap<String, String>,
}

impl AgentConfig {
    #[cfg(not(feature = "local-validation"))]
    pub(crate) fn load() -> Result<Self, String> {
        Self::load_selected(std::env::var_os("DAA_ENV_FILE"), &application_root())
    }

    fn load_selected(selector: Option<std::ffi::OsString>, root: &Path) -> Result<Self, String> {
        let explicit = selector.is_some();
        let path = selector
            .map(PathBuf::from)
            .unwrap_or_else(|| root.join(".env"));
        if !path.is_absolute() {
            return Err("env_absolute_required:DAA_ENV_FILE".into());
        }
        let content = match fs::symlink_metadata(&path) {
            Ok(m) if m.is_file() => {
                fs::read_to_string(&path).map_err(|_| "env_read_failed:DAA_ENV_FILE")?
            }
            Ok(_) => return Err("env_regular_file_required:DAA_ENV_FILE".into()),
            Err(e) if !explicit && e.kind() == std::io::ErrorKind::NotFound => String::new(),
            Err(_) => return Err("env_read_failed:DAA_ENV_FILE".into()),
        };
        Ok(Self {
            values: parse_env(&content),
        })
    }

    pub(crate) fn profile(&self, process: Option<std::ffi::OsString>) -> Result<PathBuf, String> {
        let process = process
            .map(|v| {
                v.into_string()
                    .map_err(|_| "profile_invalid:DAA_PROFILE_DIR")
            })
            .transpose()?;
        let selected = process
            .as_deref()
            .filter(|v| !v.trim().is_empty())
            .or_else(|| {
                self.values
                    .get("DAA_PROFILE_DIR")
                    .map(String::as_str)
                    .filter(|v| !v.trim().is_empty())
            });
        if selected.is_some_and(|v| v.contains(['$', '~', '<', '>'])) {
            return Err("profile_literal_required:DAA_PROFILE_DIR".into());
        }
        let path = selected
            .map(|v| PathBuf::from(v.trim()))
            .unwrap_or_else(default_profile_dir);
        if !path.is_absolute()
            || path
                .components()
                .any(|c| matches!(c, std::path::Component::ParentDir))
        {
            return Err("profile_absolute_required:DAA_PROFILE_DIR".into());
        }
        // 不canonicalize Owner选择；逐层拒绝既有symlink，在锁/开库/日志前停止。
        if path.ancestors().any(Path::is_symlink) {
            return Err("profile_symlink:DAA_PROFILE_DIR".into());
        }
        Ok(path)
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
    pub(crate) fn value_or_default(&self, key: &str, default_value: &str) -> String {
        std::env::var(key)
            .ok()
            .or_else(|| self.values.get(key).cloned())
            .unwrap_or_else(|| default_value.to_string())
    }

    #[cfg(test)]
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

pub(crate) fn application_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf()
}

fn default_profile_dir() -> PathBuf {
    dirs::data_local_dir()
        .unwrap_or_else(std::env::temp_dir)
        .join("com.aiis.aw.dataacquisitionagent")
}

#[cfg(test)]
pub(crate) fn resolve_output_path(value: &str) -> PathBuf {
    let path = PathBuf::from(value);
    if path.is_absolute() {
        path
    } else {
        default_profile_dir().join(path)
    }
}

fn parse_env(content: &str) -> HashMap<String, String> {
    let mut values = HashMap::new();
    for line in content
        .lines()
        .map(str::trim)
        .filter(|v| !v.is_empty() && !v.starts_with('#'))
    {
        let Some((key, value)) = line.split_once('=') else {
            continue;
        };
        let key = key.trim();
        // 旧键只保留键名供退役提示；从不保存/传播未知值。
        values.entry(key.to_string()).or_insert_with(|| {
            if ["DAA_PROFILE_DIR", "DAA_RUNTIME_MODE"].contains(&key) {
                trim_env_value(value)
            } else {
                String::new()
            }
        });
    }
    values
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

#[cfg(test)]
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
        assert_eq!(
            resolve_output_path("logs"),
            default_profile_dir().join("logs")
        );
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

#[cfg(test)]
mod startup_env_tests {
    use super::*;
    #[test]
    fn startup_env_owned_file_and_profile_fail_before_writes() {
        let root = std::env::temp_dir().join(format!("daa-startup-{}", uuid::Uuid::new_v4()));
        fs::create_dir(&root).unwrap();
        let file_profile = root.join("file-profile");
        let process = root.join("process-profile");
        let c = AgentConfig::load_selected(None, &root).unwrap();
        assert_eq!(c.profile(None).unwrap(), default_profile_dir());
        fs::write(root.join(".env"), format!("# own file\n DAA_PROFILE_DIR = '{}'\nDAA_PROFILE_DIR=/ignored\nDAA_PLC_READ_ALLOWED=true\nDAA_PLC_CONFIG_PATH=/ignored.yaml\nUNKNOWN=SECRET\n", file_profile.display())).unwrap();
        let c = AgentConfig::load_selected(None, &root).unwrap();
        assert_eq!(c.profile(None).unwrap(), file_profile);
        assert_eq!(c.profile(Some(" ".into())).unwrap(), file_profile);
        assert_eq!(
            c.profile(Some(process.clone().into_os_string())).unwrap(),
            process
        );
        assert_eq!(c.values.get("DAA_PLC_READ_ALLOWED").unwrap(), "");
        assert!(!c.values.values().any(|v| v.contains("SECRET")));
        let alternate = root.join("selected.env");
        fs::write(&alternate, "DAA_PROFILE_DIR=\n").unwrap();
        assert_eq!(
            AgentConfig::load_selected(Some(alternate.clone().into_os_string()), &root)
                .unwrap()
                .profile(None)
                .unwrap(),
            default_profile_dir()
        );
        for selector in [
            PathBuf::from("relative.env"),
            root.join("missing.env"),
            root.clone(),
        ] {
            assert!(AgentConfig::load_selected(Some(selector.into_os_string()), &root).is_err());
        }
        for bad in [
            "relative",
            "$HOME/profile",
            "${HOME}/profile",
            "~/profile",
            "/private/tmp/$HOME",
            "/private/tmp/<profile>",
            "/private/tmp/../escape",
        ] {
            let c = AgentConfig {
                values: parse_env(&format!("DAA_PROFILE_DIR={bad}")),
            };
            assert!(c.profile(None).is_err());
            assert!(c.profile(Some(bad.into())).is_err());
        }
        #[cfg(unix)]
        {
            use std::os::unix::{ffi::OsStringExt, fs::symlink};
            let link = root.join("link");
            symlink(&root, &link).unwrap();
            assert!(c
                .profile(Some(link.join("child").into_os_string()))
                .is_err());
            assert!(c
                .profile(Some(std::ffi::OsString::from_vec(vec![255])))
                .is_err());
            fs::remove_file(root.join(".env")).unwrap();
            symlink(root.join("missing-target"), root.join(".env")).unwrap();
            assert!(AgentConfig::load_selected(None, &root).is_err());
            fs::remove_file(root.join(".env")).unwrap();
        }
        fs::write(&alternate, [255]).unwrap();
        assert!(AgentConfig::load_selected(Some(alternate.into_os_string()), &root).is_err());
        fs::write(root.join(".env"), [255]).unwrap();
        assert!(AgentConfig::load_selected(None, &root).is_err());
        assert!(!file_profile.exists() && !process.exists());
        fs::remove_dir_all(root).unwrap();
    }
}
