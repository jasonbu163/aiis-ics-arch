//! 模式/验证factory：在旧配置和headless之前检查完整参数，验证仅debug+临时fixture且无真实传输。
use crate::domain::local_configuration::LocalResult;
use std::{path::PathBuf, sync::OnceLock};
#[derive(Clone)]
pub(crate) struct Bootstrap {
    pub mode: String,
    pub profile: PathBuf,
    pub read_allowed: bool,
    pub validation: bool,
    #[cfg(test)]
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
        let c = super::AgentConfig::load()?;
        let b = ordinary(
            &c,
            std::env::var("DAA_RUNTIME_MODE").ok(),
            c.profile(std::env::var_os("DAA_PROFILE_DIR"))?,
            std::env::var("DAA_PLC_READ_ALLOWED"),
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
        #[cfg(test)]
        migration: None,
        ignored_keys: vec![],
        fixture: Some(paths["--fixture-file"].clone()),
    })
}

fn ordinary(
    c: &super::AgentConfig,
    process_mode: Option<String>,
    profile: PathBuf,
    process_read: Result<String, std::env::VarError>,
) -> LocalResult<Bootstrap> {
    let mode = c.value_or_default("DAA_RUNTIME_MODE", "local_sqlite");
    check_mode(&mode, process_mode.is_some())?;
    let allowed = [
        "DAA_ENV_FILE",
        "DAA_PROFILE_DIR",
        "DAA_RUNTIME_MODE",
        "DAA_PLC_READ_ALLOWED",
    ];
    let mut ignored_keys: Vec<String> = c
        .configured_keys()
        .into_iter()
        .filter(|k| k.starts_with("DAA_") && !allowed.contains(&k.as_str()))
        .collect();
    if c.values.contains_key("DAA_PLC_READ_ALLOWED") {
        ignored_keys.push("DAA_PLC_READ_ALLOWED".into());
    }
    if mode.trim() == "legacy_snapshot" {
        ignored_keys.push("DAA_RUNTIME_MODE".into());
    }
    Ok(Bootstrap {
        mode: "local_sqlite".into(),
        profile,
        read_allowed: ordinary_read_allowed(process_read),
        validation: false,
        #[cfg(test)]
        migration: None,
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
// 仅普通native使用；NotUnicode与空/非法均拒绝，不能把解码失败当缺失。
fn ordinary_read_allowed(value: Result<String, std::env::VarError>) -> bool {
    match value {
        Err(std::env::VarError::NotPresent) => true,
        Ok(v) => matches!(
            v.as_str(),
            "1" | "true" | "TRUE" | "True" | "yes" | "YES" | "on" | "ON"
        ),
        Err(std::env::VarError::NotUnicode(_)) => false,
    }
}

#[cfg(test)]
mod startup_env_tests {
    use super::*;
    #[test]
    fn startup_env_read_admission_is_process_only_and_stopped() {
        for file_value in ["true", "false"] {
            let c = super::super::AgentConfig::from_values(std::collections::HashMap::from([
                ("DAA_PLC_READ_ALLOWED".into(), file_value.into()),
                ("DAA_PLC_CONFIG_PATH".into(), "ignored.yaml".into()),
            ]));
            let b = ordinary(
                &c,
                None,
                PathBuf::from("/private/tmp/unused"),
                Err(std::env::VarError::NotPresent),
            )
            .unwrap();
            assert!(
                b.read_allowed && !b.validation && b.fixture.is_none() && b.migration.is_none()
            );
            assert!(b.ignored_keys.contains(&"DAA_PLC_CONFIG_PATH".into()));
            for value in ["false", "", " ", "typo", "0", " true "] {
                assert!(
                    !ordinary(&c, None, b.profile.clone(), Ok(value.into()))
                        .unwrap()
                        .read_allowed
                );
            }
        }
        for value in ["1", "true", "TRUE", "True", "yes", "YES", "on", "ON"] {
            assert!(ordinary_read_allowed(Ok(value.into())));
        }
        #[cfg(unix)]
        {
            use std::os::unix::ffi::OsStringExt;
            assert!(!ordinary_read_allowed(Err(std::env::VarError::NotUnicode(
                std::ffi::OsString::from_vec(vec![255])
            ))));
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
    #[cfg(feature = "local-validation")]
    #[test]
    fn startup_env_validation_fixture_contract() {
        use std::{fs, process::Command};
        const CHILD: &str = "DAA007_VALIDATION_CHILD";
        let case = std::env::var(CHILD).ok();
        if case.is_none() {
            for case in ["clean", "inherited_true"] {
                let mut command = Command::new(std::env::current_exe().unwrap());
                command.args(["--exact", "config::local_bootstrap::startup_env_tests::startup_env_validation_fixture_contract", "--nocapture"]);
                for (key, _) in
                    std::env::vars_os().filter(|(k, _)| k.to_string_lossy().starts_with("DAA_"))
                {
                    command.env_remove(key);
                }
                command.env(CHILD, case);
                if case == "inherited_true" {
                    command.env("DAA_PLC_READ_ALLOWED", "true");
                }
                assert!(command.status().unwrap().success());
            }
            return;
        }
        assert!(matches!(load(vec![]), Err(e) if e == "validation_arguments_required"));
        let profile =
            std::env::temp_dir().join(format!("validation-bootstrap-{}", uuid::Uuid::new_v4()));
        fs::create_dir(&profile).unwrap();
        let env = profile.join("fixture.env");
        let fixture = profile.join("fixture.json");
        fs::write(&env, "DAA_RUNTIME_MODE=local_sqlite\nDAA_LOCAL_STORAGE_ENABLED=true\nDAA_PLC_READ_ALLOWED=true\n").unwrap();
        fs::write(&fixture, "{}").unwrap();
        let args = vec![
            "--daa-local-validation".into(),
            "--env-file".into(),
            env.display().to_string(),
            "--profile-dir".into(),
            profile.display().to_string(),
            "--fixture-file".into(),
            fixture.display().to_string(),
        ];
        assert!(matches!(validation(&args), Err(e) if e == "validation_owner_required"));
        fs::write(
            profile.join(".daa-local-validation-owner"),
            "DAA-002-r2-owned\n",
        )
        .unwrap();
        if case.as_deref() == Some("inherited_true") {
            assert!(matches!(validation(&args), Err(e) if e == "validation_inherited_environment"));
        } else {
            let b = validation(&args).unwrap();
            assert!(b.read_allowed && b.validation && b.fixture.as_ref() == Some(&fixture));
            fs::write(&env, "DAA_RUNTIME_MODE=local_sqlite\nDAA_LOCAL_STORAGE_ENABLED=true\nDAA_PLC_READ_ALLOWED=false\n").unwrap();
            assert!(matches!(validation(&args), Err(e) if e == "validation_env_conflict"));
            let missing_fixture = args[..args.len() - 2].to_vec();
            assert!(
                matches!(validation(&missing_fixture), Err(e) if e == "validation_arguments_required")
            );
        }
        fs::remove_dir_all(profile).unwrap();
    }
}
