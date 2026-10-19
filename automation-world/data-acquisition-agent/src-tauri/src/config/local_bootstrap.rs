//! 模式/验证factory：在旧配置和headless之前检查完整参数，验证仅debug+临时fixture且无真实传输。
use crate::domain::local_configuration::LocalResult;
use std::{path::PathBuf, sync::OnceLock};
#[derive(Clone)]
pub(crate) struct Bootstrap {
    pub mode: String,
    pub profile: PathBuf,
    pub read_allowed: bool,
    pub validation: bool,
    pub migration: Option<crate::domain::yaml_migration::MigrationPaths>,
    pub ignored_keys: Vec<String>,
    #[cfg_attr(not(any(test, feature = "local-validation")), allow(dead_code))]
    pub fixture: Option<PathBuf>,
}
static CURRENT: OnceLock<Bootstrap> = OnceLock::new();
pub(crate) fn current() -> Option<&'static Bootstrap> {
    CURRENT.get()
}
#[cfg(feature = "local-validation")]
fn reject_symlinks(p: &std::path::Path) -> LocalResult<()> {
    for a in p.ancestors() {
        if a.is_symlink() {
            return Err("validation_symlink".into());
        }
    }
    Ok(())
}
pub(crate) fn load(args: Vec<String>) -> LocalResult<Bootstrap> {
    let validation_flag = args.iter().any(|s| s == "--daa-local-validation");
    #[cfg(feature = "local-validation")]
    {
        if !cfg!(debug_assertions) {
            return Err("validation_release_forbidden".into());
        }
        if !validation_flag {
            return Err("validation_arguments_required".into());
        }
        let b = validation(&args)?;
        let _ = CURRENT.set(b.clone());
        return Ok(b);
    }
    #[cfg(not(feature = "local-validation"))]
    {
        if validation_flag
            || args
                .iter()
                .any(|s| s == "--fixture-file" || s == "--profile-dir" || s == "--env-file")
        {
            return Err("validation_feature_required".into());
        }
        if args.iter().any(|a| a.starts_with("--ca-")) {
            return Err("legacy_entry_retired".into());
        }
        for key in ["DAA_ENV_FILE", "DAA_PROFILE_DIR"] {
            if let Some(v) = std::env::var_os(key) {
                if !PathBuf::from(v).is_absolute() {
                    return Err("locator_absolute_required".into());
                }
            }
        }
        let c = super::AgentConfig::load();
        let b = ordinary(
            &c,
            std::env::var("DAA_RUNTIME_MODE").ok(),
            super::profile_dir(),
        )?;
        let _ = CURRENT.set(b.clone());
        Ok(b)
    }
}
#[cfg(feature = "local-validation")]
fn validation(args: &[String]) -> LocalResult<Bootstrap> {
    if args.iter().any(|a| a.starts_with("--ca-")) {
        return Err("mixed_runtime_arguments".into());
    }
    let mut values = std::collections::HashMap::new();
    let mut i = 0;
    while i < args.len() {
        if args[i] == "--daa-local-validation" {
            i += 1;
            continue;
        }
        let key = &args[i];
        if !["--env-file", "--profile-dir", "--fixture-file"].contains(&key.as_str())
            || i + 1 >= args.len()
            || values.insert(key.clone(), args[i + 1].clone()).is_some()
        {
            return Err("validation_arguments_required".into());
        }
        i += 2;
    }
    let mut paths = std::collections::HashMap::new();
    let tmp = std::env::temp_dir()
        .canonicalize()
        .map_err(|_| "validation_tmp")?;
    let private_tmp = std::path::Path::new("/private/tmp").canonicalize().ok();
    for key in ["--env-file", "--profile-dir", "--fixture-file"] {
        let p = PathBuf::from(values.get(key).ok_or("validation_arguments_required")?);
        if !p.is_absolute() {
            return Err("validation_absolute_required".into());
        }
        reject_symlinks(&p)?;
        let canonical = p.canonicalize().map_err(|_| "validation_path_missing")?;
        if !canonical.starts_with(&tmp)
            && !private_tmp
                .as_ref()
                .map(|t| canonical.starts_with(t))
                .unwrap_or(false)
        {
            return Err("validation_tmp_required".into());
        }
        paths.insert(key, canonical);
    }
    let profile = paths["--profile-dir"].clone();
    if !profile.is_dir()
        || std::fs::read_to_string(profile.join(".daa-local-validation-owner"))
            .ok()
            .as_deref()
            != Some("DAA-002-r2-owned\n")
    {
        return Err("validation_owner_required".into());
    }
    for key in ["--env-file", "--fixture-file"] {
        let p = &paths[key];
        if !p.starts_with(&profile) || !p.is_file() {
            return Err("validation_profile_boundary".into());
        }
    }
    // Reject inherited DAA overrides rather than leaking a real locator or business gate into validation.
    if std::env::vars_os().any(|(k, _)| k.to_string_lossy().starts_with("DAA_")) {
        return Err("validation_inherited_environment".into());
    }
    let content = std::fs::read_to_string(&paths["--env-file"]).map_err(|_| "validation_env")?;
    let mut keys = std::collections::BTreeSet::new();
    for line in content
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
    {
        let (k, v) = line.split_once('=').ok_or("validation_env")?;
        let k = k.trim();
        if !keys.insert(k.to_string()) {
            return Err("validation_env_conflict".into());
        }
        let v = v.trim();
        match k {
            "DAA_RUNTIME_MODE" if v == "local_sqlite" => (),
            "DAA_LOCAL_STORAGE_ENABLED" | "DAA_PLC_READ_ALLOWED" if v == "true" => (),
            "DAA_DATABASE_ENABLED"
            | "DAA_DATABASE_WRITE_ALLOWED"
            | "DAA_PLC_WRITE_ALLOWED"
            | "DAA_UPPER_SYSTEM_AUTH_ENABLED"
            | "DAA_PLC_COLLECTION_LOOP_AUTOSTART"
            | "DAA_PLC_SAMPLE_READ_AUTOSTART"
                if v == "false" =>
            {
                ()
            }
            "DAA_PLC_AUTOSTART_MODE" if v == "stopped" => (),
            _ => return Err("validation_env_conflict".into()),
        }
    }
    for k in [
        "DAA_RUNTIME_MODE",
        "DAA_LOCAL_STORAGE_ENABLED",
        "DAA_PLC_READ_ALLOWED",
    ] {
        if !keys.contains(k) {
            return Err("validation_env_required".into());
        }
    }

    Ok(Bootstrap {
        mode: "local_sqlite".into(),
        profile,
        read_allowed: true,
        validation: true,
        migration: None,
        ignored_keys: vec![],
        fixture: Some(paths["--fixture-file"].clone()),
    })
}

fn ordinary(
    c: &super::AgentConfig,
    process_mode: Option<String>,
    profile: PathBuf,
) -> LocalResult<Bootstrap> {
    let mode = c.value_or_default("DAA_RUNTIME_MODE", "local_sqlite");
    check_mode(&mode, process_mode.is_some())?;
    let allowed = [
        "DAA_ENV_FILE",
        "DAA_PROFILE_DIR",
        "DAA_RUNTIME_MODE",
        "DAA_PLC_READ_ALLOWED",
        "DAA_PLC_CONFIG_PATH",
        "DAA_PLC_SNAPSHOT_POLICY_PATH",
    ];
    let mut ignored_keys: Vec<String> = c
        .configured_keys()
        .into_iter()
        .filter(|k| k.starts_with("DAA_") && !allowed.contains(&k.as_str()))
        .collect();
    if mode.trim() == "legacy_snapshot" {
        ignored_keys.push("DAA_RUNTIME_MODE".into());
    }
    let (points, points_origin) = c.locator("DAA_PLC_CONFIG_PATH", "config/plc_points.yaml");
    let (policy, policy_origin) = c.locator(
        "DAA_PLC_SNAPSHOT_POLICY_PATH",
        "config/plc_snapshot_policy.yaml",
    );
    Ok(Bootstrap {
        mode: "local_sqlite".into(),
        profile,
        read_allowed: c.bool_or_default("DAA_PLC_READ_ALLOWED", false),
        validation: false,
        migration: Some(crate::domain::yaml_migration::MigrationPaths {
            points,
            points_origin,
            policy,
            policy_origin,
        }),
        ignored_keys,
        fixture: None,
    })
}
fn check_mode(mode: &str, process: bool) -> LocalResult<()> {
    match mode.trim() {
        "" | "local_sqlite" => Ok(()),
        "legacy_snapshot" if !process => Ok(()),
        "legacy_snapshot" => Err("legacy_runtime_retired".into()),
        _ => Err("runtime_mode_invalid".into()),
    }
}
#[cfg(test)]
mod retirement_tests {
    use super::*;
    #[test]
    fn mode_source_is_explicit() {
        for m in ["", "local_sqlite"] {
            assert!(check_mode(m, true).is_ok());
        }
        assert!(check_mode("legacy_snapshot", false).is_ok());
        assert_eq!(
            check_mode("legacy_snapshot", true).unwrap_err(),
            "legacy_runtime_retired"
        );
        assert_eq!(
            check_mode("typo", false).unwrap_err(),
            "runtime_mode_invalid"
        );
    }
    #[test]
    fn ordinary_bootstrap_ignores_retired_business_values_and_fixes_locators() {
        use std::collections::HashMap;
        let profile = PathBuf::from("/private/tmp/daa003-bootstrap-test-no-write");
        let c = super::super::AgentConfig::from_values(HashMap::new());
        let b = ordinary(&c, None, profile.clone()).unwrap();
        assert_eq!(b.mode, "local_sqlite");
        assert!(!b.read_allowed);
        assert!(!profile.exists());
        assert_eq!(
            b.migration.unwrap().points,
            super::super::application_root().join("config/plc_points.yaml")
        );
        let c = super::super::AgentConfig::from_values(HashMap::from([
            ("DAA_RUNTIME_MODE".into(), "legacy_snapshot".into()),
            ("DAA_LOCAL_STORAGE_ENABLED".into(), "false".into()),
            ("DAA_DATABASE_ENABLED".into(), "true".into()),
            ("DAA_DATABASE_URL".into(), "SECRET_NOT_EXPOSED".into()),
            ("DAA_PLC_AUTOSTART_MODE".into(), "collect".into()),
            ("DAA_PLC_HOST".into(), "not-an-endpoint".into()),
            (
                "DAA_PLC_CONFIG_PATH".into(),
                "config/owned-test.yaml".into(),
            ),
        ]));
        let b = ordinary(&c, None, profile.clone()).unwrap();
        assert!(!b.read_allowed);
        assert!(b.ignored_keys.contains(&"DAA_DATABASE_ENABLED".into()));
        assert!(b.ignored_keys.contains(&"DAA_RUNTIME_MODE".into()));
        let m = b.migration.unwrap();
        assert_eq!(m.points_origin, "env_file");
        assert_eq!(
            m.points,
            super::super::application_root().join("config/owned-test.yaml")
        );
        std::env::set_var("DAA_PLC_CONFIG_PATH", "/private/tmp/daa003-process.yaml");
        let (p, origin) = c.locator("DAA_PLC_CONFIG_PATH", "unused");
        std::env::remove_var("DAA_PLC_CONFIG_PATH");
        assert_eq!(p, PathBuf::from("/private/tmp/daa003-process.yaml"));
        assert_eq!(origin, "process");
        assert!(ordinary(&c, Some("legacy_snapshot".into()), profile.clone()).is_err());
        assert!(!profile.exists());
    }
}
