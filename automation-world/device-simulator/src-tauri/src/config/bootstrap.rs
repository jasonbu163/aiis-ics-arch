//! 普通源码启动：process > 自身.env > Tauri默认profile；自动化manifest保持权威。
use serde::Serialize;
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Bootstrap {
    pub product: String,
    pub version: String,
    pub profile_dir: String,
    pub native_enabled: bool,
    pub schema_version: u32,
    pub webview_store_id: String,
}
pub fn load(default: &std::path::Path) -> Result<Bootstrap, String> {
    #[cfg(feature = "test-automation")]
    let profile = {
        // lib.rs已验证manifest并设置该进程键；不读取普通源码.env。
        let explicit = std::env::var("DS_PROFILE_DIR").map_err(|_| "profile_manifest_required")?;
        ds_runtime::config::profile::resolve(default, Some(&explicit))?
    };
    #[cfg(not(feature = "test-automation"))]
    let profile = ordinary_profile(default, std::env::var_os("DS_PROFILE_DIR"), &source_root())?;
    Ok(Bootstrap {
        product: "AIIS Device Simulator".into(),
        version: "0.1.0".into(),
        profile_dir: profile.display().to_string(),
        native_enabled: cfg!(feature = "native-s7"),
        schema_version: 1,
        webview_store_id: String::new(),
    })
}

#[cfg(not(feature = "test-automation"))]
fn source_root() -> std::path::PathBuf {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf()
}

#[cfg(any(test, not(feature = "test-automation")))]
fn ordinary_profile(
    default: &std::path::Path,
    process: Option<std::ffi::OsString>,
    root: &std::path::Path,
) -> Result<std::path::PathBuf, String> {
    let file = root.join(".env");
    let content = match std::fs::symlink_metadata(&file) {
        Ok(m) if m.is_file() => {
            std::fs::read_to_string(&file).map_err(|_| "env_read_failed:DS_PROFILE_DIR")?
        }
        Ok(_) => return Err("env_regular_file_required:DS_PROFILE_DIR".into()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => String::new(),
        Err(_) => return Err("env_read_failed:DS_PROFILE_DIR".into()),
    };
    let file_profile = parse_profile(&content);
    let process = process
        .map(|v| {
            v.into_string()
                .map_err(|_| "profile_invalid:DS_PROFILE_DIR")
        })
        .transpose()?;
    let explicit = process
        .as_deref()
        .filter(|v| !v.trim().is_empty())
        .or_else(|| file_profile.as_deref().filter(|v| !v.trim().is_empty()));
    if explicit.is_some_and(|v| v.contains(['$', '~', '<', '>'])) {
        return Err("profile_literal_required:DS_PROFILE_DIR".into());
    }
    ds_runtime::config::profile::resolve(default, explicit.map(str::trim))
}

#[cfg(any(test, not(feature = "test-automation")))]
fn parse_profile(content: &str) -> Option<String> {
    for line in content
        .lines()
        .map(str::trim)
        .filter(|v| !v.is_empty() && !v.starts_with('#'))
    {
        let Some((key, value)) = line.split_once('=') else {
            continue;
        };
        if key.trim() != "DS_PROFILE_DIR" {
            continue;
        }
        let v = value.trim();
        return Some(
            if v.len() >= 2
                && ((v.starts_with('"') && v.ends_with('"'))
                    || (v.starts_with('\'') && v.ends_with('\'')))
            {
                v[1..v.len() - 1].to_string()
            } else {
                v.to_string()
            },
        );
    }
    None
}

#[cfg(test)]
mod startup_env_tests {
    use super::*;
    use std::fs;
    #[test]
    fn startup_env_own_file_precedence_literals_and_rejection() {
        let root = std::env::temp_dir().join(format!(
            "ds-startup-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&root).unwrap();
        let default = root.join("default");
        let file_profile = root.join("file-profile");
        let process = root.join("process-profile");
        assert_eq!(ordinary_profile(&default, None, &root).unwrap(), default);
        fs::write(root.join(".env"), format!("# own file\nDS_PROFILE_DIR='{}'\nDS_PROFILE_DIR=/ignored\nDAA_PROFILE_DIR=/other-app\n", file_profile.display())).unwrap();
        assert_eq!(
            ordinary_profile(&default, None, &root).unwrap(),
            file_profile
        );
        assert_eq!(
            ordinary_profile(&default, Some(" ".into()), &root).unwrap(),
            file_profile
        );
        assert_eq!(
            ordinary_profile(&default, Some(process.clone().into_os_string()), &root).unwrap(),
            process
        );
        for bad in [
            "relative",
            "$HOME/profile",
            "${HOME}/profile",
            "~/profile",
            "/private/tmp/$HOME",
            "/private/tmp/<profile>",
            "/private/tmp/../escape",
        ] {
            fs::write(root.join(".env"), format!("DS_PROFILE_DIR={bad}")).unwrap();
            assert!(ordinary_profile(&default, None, &root).is_err());
        }
        #[cfg(unix)]
        {
            use std::os::unix::{ffi::OsStringExt, fs::symlink};
            assert!(ordinary_profile(
                &default,
                Some(std::ffi::OsString::from_vec(vec![255])),
                &root
            )
            .is_err());
            let link = root.join("link");
            symlink(&root, &link).unwrap();
            assert!(ordinary_profile(&default, Some(link.into_os_string()), &root).is_err());
            fs::remove_file(root.join(".env")).unwrap();
            symlink(root.join("missing-target"), root.join(".env")).unwrap();
            assert!(ordinary_profile(&default, None, &root).is_err());
            fs::remove_file(root.join(".env")).unwrap();
        }
        fs::write(root.join(".env"), "DS_PROFILE_DIR=\n").unwrap();
        assert_eq!(ordinary_profile(&default, None, &root).unwrap(), default);
        fs::write(root.join(".env"), [255]).unwrap();
        assert!(ordinary_profile(&default, Some(process.into_os_string()), &root).is_err());
        fs::remove_file(root.join(".env")).unwrap();
        fs::create_dir(root.join(".env")).unwrap();
        assert!(ordinary_profile(&default, None, &root).is_err());
        assert!(!default.exists() && !file_profile.exists());
        fs::remove_dir_all(root).unwrap();
    }
}
