//! SMA 配置加载：HTTP 设置保持原读取方式，profile 在写入前按所选配置文件解析。
pub mod runtime_startup;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::ffi::OsString;
use std::fs;
use std::path::{Component, Path, PathBuf};

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
/// 启动时解析一次，供配置库、日志和启动偏好使用同一目录。
pub(crate) struct ResolvedProfile(PathBuf);

impl ResolvedProfile {
    pub(crate) fn database_path(&self) -> PathBuf {
        self.0.join("configuration.sqlite3")
    }

    pub(crate) fn logging_directory(&self) -> PathBuf {
        self.0.join("logs")
    }

    pub(crate) fn startup_preferences_path(&self) -> PathBuf {
        self.0.join(runtime_startup::PREFERENCES_FILE)
    }
}

struct SelectedEnv {
    directory: PathBuf,
    content: String,
}

impl SelectedEnv {
    fn load(selector: Option<OsString>, root: &Path) -> Result<Self, String> {
        let explicit = selector.is_some();
        let path = selector
            .map(PathBuf::from)
            .unwrap_or_else(|| root.join(".env"));
        if !path.is_absolute() {
            return Err("SMA_ENV_FILE_ABSOLUTE_REQUIRED".into());
        }
        if path.to_str().is_none() {
            return Err("SMA_ENV_FILE_INVALID".into());
        }
        let content = match fs::symlink_metadata(&path) {
            Ok(metadata) if metadata.file_type().is_file() => {
                fs::read_to_string(&path).map_err(|_| "SMA_ENV_FILE_READ_FAILED")?
            }
            Ok(_) => return Err("SMA_ENV_FILE_REGULAR_FILE_REQUIRED".into()),
            Err(error) if !explicit && error.kind() == std::io::ErrorKind::NotFound => {
                String::new()
            }
            Err(_) => return Err("SMA_ENV_FILE_READ_FAILED".into()),
        };
        Ok(Self {
            directory: path.parent().ok_or("SMA_ENV_FILE_INVALID")?.to_path_buf(),
            content,
        })
    }

    fn profile(&self, process: Option<OsString>) -> Result<Option<PathBuf>, String> {
        let process = process
            .map(|value| value.into_string().map_err(|_| "SMA_PROFILE_DIR_INVALID"))
            .transpose()?;
        let file = self.content.lines().find_map(|line| {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                return None;
            }
            let (key, value) = line.split_once('=')?;
            if key.trim() != "SMA_PROFILE_DIR" {
                return None;
            }
            let value = value.trim();
            Some(
                if value.len() >= 2
                    && ((value.starts_with('"') && value.ends_with('"'))
                        || (value.starts_with('\'') && value.ends_with('\'')))
                {
                    &value[1..value.len() - 1]
                } else {
                    value
                },
            )
        });
        let selected = process
            .as_deref()
            .filter(|value| !value.trim().is_empty())
            .or_else(|| file.filter(|value| !value.trim().is_empty()));
        let Some(selected) = selected.map(str::trim) else {
            return Ok(None);
        };
        if selected.contains(['$', '~', '<', '>']) || contains_windows_variable(selected) {
            return Err("SMA_PROFILE_DIR_LITERAL_REQUIRED".into());
        }
        let path = Path::new(selected);
        if path
            .components()
            .any(|part| matches!(part, Component::ParentDir))
        {
            return Err("SMA_PROFILE_DIR_PARENT_NOT_ALLOWED".into());
        }
        let path = if path.is_absolute() {
            path.to_path_buf()
        } else {
            if path.has_root()
                || path
                    .components()
                    .any(|part| matches!(part, Component::Prefix(_)))
            {
                return Err("SMA_PROFILE_DIR_ABSOLUTE_REQUIRED".into());
            }
            self.directory.join(path)
        };
        let path: PathBuf = path.components().collect();
        Ok(Some(path))
    }
}

fn validate_profile_path(path: &Path) -> Result<(), String> {
    path.to_str().ok_or("SMA_PROFILE_DIR_INVALID")?;
    if !path.is_absolute()
        || path
            .components()
            .any(|part| matches!(part, Component::ParentDir))
    {
        return Err("SMA_PROFILE_DIR_ABSOLUTE_REQUIRED".into());
    }
    let mut nearest_directory = None;
    for ancestor in path.ancestors().collect::<Vec<_>>().into_iter().rev() {
        match fs::symlink_metadata(ancestor) {
            Ok(metadata) if metadata.file_type().is_symlink() => {
                return Err("SMA_PROFILE_DIR_SYMLINK".into());
            }
            Ok(metadata) if !metadata.is_dir() => {
                return Err("SMA_PROFILE_DIR_NOT_DIRECTORY".into());
            }
            Ok(_) => nearest_directory = Some(ancestor),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) if error.kind() == std::io::ErrorKind::PermissionDenied => {
                return Err("SMA_PROFILE_DIR_NOT_SEARCHABLE".into());
            }
            Err(_) => return Err("SMA_PROFILE_DIR_UNAVAILABLE".into()),
        }
    }
    validate_directory_access(nearest_directory.ok_or("SMA_PROFILE_DIR_UNAVAILABLE")?)
}

#[cfg(any(target_os = "macos", target_os = "linux"))]
fn validate_directory_access(directory: &Path) -> Result<(), String> {
    use std::ffi::CString;
    use std::os::raw::{c_char, c_int};
    use std::os::unix::ffi::OsStrExt;

    #[cfg(target_os = "macos")]
    const AT_FDCWD: c_int = -2;
    #[cfg(target_os = "macos")]
    const AT_EACCESS: c_int = 0x0010;
    #[cfg(target_os = "linux")]
    const AT_FDCWD: c_int = -100;
    #[cfg(target_os = "linux")]
    const AT_EACCESS: c_int = 0x0200;
    const X_OK: c_int = 1;
    const W_OK: c_int = 2;

    unsafe extern "C" {
        fn faccessat(dirfd: c_int, path: *const c_char, mode: c_int, flags: c_int) -> c_int;
    }

    let path =
        CString::new(directory.as_os_str().as_bytes()).map_err(|_| "SMA_PROFILE_DIR_INVALID")?;
    for (mode, denied) in [
        (X_OK, "SMA_PROFILE_DIR_NOT_SEARCHABLE"),
        (W_OK, "SMA_PROFILE_DIR_NOT_WRITABLE"),
    ] {
        // SAFETY: path is a live NUL-terminated CString and constants match the target OS.
        let result = unsafe { faccessat(AT_FDCWD, path.as_ptr(), mode, AT_EACCESS) };
        if result != 0 {
            return Err(if std::io::Error::last_os_error().kind()
                == std::io::ErrorKind::PermissionDenied
            {
                denied
            } else {
                "SMA_PROFILE_DIR_UNAVAILABLE"
            }
            .into());
        }
    }
    Ok(())
}

#[cfg(windows)]
fn validate_directory_access(directory: &Path) -> Result<(), String> {
    use std::os::windows::fs::OpenOptionsExt;

    const FILE_ADD_FILE: u32 = 0x0002;
    const FILE_ADD_SUBDIRECTORY: u32 = 0x0004;
    const FILE_TRAVERSE: u32 = 0x0020;
    const FILE_FLAG_BACKUP_SEMANTICS: u32 = 0x0200_0000;
    const FILE_SHARE_ALL: u32 = 0x0001 | 0x0002 | 0x0004;

    for (rights, denied) in [
        (FILE_TRAVERSE, "SMA_PROFILE_DIR_NOT_SEARCHABLE"),
        (
            FILE_ADD_FILE | FILE_ADD_SUBDIRECTORY,
            "SMA_PROFILE_DIR_NOT_WRITABLE",
        ),
    ] {
        let result = fs::OpenOptions::new()
            .read(true)
            .access_mode(rights)
            .share_mode(FILE_SHARE_ALL)
            .custom_flags(FILE_FLAG_BACKUP_SEMANTICS)
            .open(directory);
        if let Err(error) = result {
            return Err(if error.kind() == std::io::ErrorKind::PermissionDenied {
                denied
            } else {
                "SMA_PROFILE_DIR_UNAVAILABLE"
            }
            .into());
        }
    }
    Ok(())
}

#[cfg(not(any(target_os = "macos", target_os = "linux", windows)))]
fn validate_directory_access(_directory: &Path) -> Result<(), String> {
    Err("SMA_PROFILE_DIR_UNSUPPORTED_PLATFORM".into())
}

fn contains_windows_variable(literal: &str) -> bool {
    literal.match_indices('%').any(|(start, _)| {
        let suffix = &literal[start + 1..];
        suffix.find('%').is_some_and(|end| {
            let name = &suffix[..end];
            !name.is_empty() && !name.contains(['/', '\\'])
        })
    })
}

fn resolve_profile(
    selector: Option<OsString>,
    process: Option<OsString>,
    root: &Path,
    default: impl FnOnce() -> Result<PathBuf, String>,
) -> Result<ResolvedProfile, String> {
    let env = SelectedEnv::load(selector, root)?;
    let path = match env.profile(process)? {
        Some(path) => path,
        None => default()?,
    };
    validate_profile_path(&path)?;
    Ok(ResolvedProfile(path))
}

pub(crate) fn configuration_profile(app: &tauri::AppHandle) -> Result<ResolvedProfile, String> {
    use tauri::Manager;
    resolve_profile(
        std::env::var_os("SMA_ENV_FILE"),
        std::env::var_os("SMA_PROFILE_DIR"),
        &application_root(),
        || {
            app.path()
                .app_data_dir()
                .map_err(|_| "SMA_CONFIGURATION_PROFILE_UNAVAILABLE".into())
        },
    )
}

#[cfg(test)]
mod startup_path_tests {
    use super::*;
    use crate::infrastructure::config_store::ConfigStore;
    use std::process::Command;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn fixture_root() -> PathBuf {
        let base = std::env::temp_dir().canonicalize().unwrap();
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let root = base.join(format!("sma-007-{}-{unique}", std::process::id()));
        fs::create_dir(&root).unwrap();
        root
    }

    fn profile(root: &Path, selector: Option<OsString>, process: Option<OsString>) -> PathBuf {
        resolve_profile(selector, process, root, || Ok(root.join("default")))
            .unwrap()
            .0
    }

    #[test]
    fn startup_path_file_process_and_absolute_precedence() {
        let root = fixture_root();
        let selected_dir = root.join("selected");
        fs::create_dir(&selected_dir).unwrap();
        assert_eq!(profile(&root, None, None), root.join("default"));
        assert_eq!(
            profile(&root, None, Some("./.local/dev".into())),
            root.join(".local/dev")
        );
        for value in [".local/dev", "./.local/dev"] {
            fs::write(root.join(".env"), format!("SMA_PROFILE_DIR={value}\n")).unwrap();
            assert_eq!(profile(&root, None, None), root.join(".local/dev"));
        }
        let absolute = root.join("old-absolute");
        fs::write(
            root.join(".env"),
            format!(
                "SMA_PROFILE_DIR='{}'\nSMA_PROFILE_DIR=ignored\n",
                absolute.display()
            ),
        )
        .unwrap();
        assert_eq!(profile(&root, None, None), absolute);
        assert_eq!(profile(&root, None, Some(" ".into())), absolute);
        assert_eq!(
            profile(&root, None, Some("process".into())),
            root.join("process")
        );

        let selected = selected_dir.join("selected.env");
        fs::write(
            &selected,
            "SMA_PROFILE_DIR=\"./file\"\nSMA_PROFILE_DIR=ignored\n",
        )
        .unwrap();
        assert_eq!(
            profile(&root, Some(selected.clone().into()), None),
            selected_dir.join("file")
        );
        assert_eq!(
            profile(
                &root,
                Some(selected.clone().into()),
                Some("./process".into())
            ),
            selected_dir.join("process")
        );
        assert_eq!(
            profile(
                &root,
                Some(selected.clone().into()),
                Some(absolute.clone().into())
            ),
            absolute
        );
        fs::write(&selected, "SMA_PROFILE_DIR=\n").unwrap();
        assert_eq!(
            profile(&root, Some(selected.into()), Some(" ".into())),
            root.join("default")
        );
        assert!(!root.join(".local").exists());
        assert!(!root.join("default").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn startup_path_accepts_literal_selected_env_parent_and_default() {
        let root = fixture_root();
        let selected_dir = root.join("%EXISTING%").join("real$literal~<folder>");
        fs::create_dir_all(&selected_dir).unwrap();
        let selected = selected_dir.join("selected.env");
        fs::write(&selected, "SMA_PROFILE_DIR=./.local/dev\n").unwrap();
        assert_eq!(
            profile(&root, Some(selected.clone().into()), None),
            selected_dir.join(".local/dev")
        );
        assert_eq!(
            profile(&root, Some(selected.into()), Some("process".into())),
            selected_dir.join("process")
        );
        let default = root.join("default%EXISTING%$literal");
        let resolved = resolve_profile(None, None, &root, || Ok(default.clone())).unwrap();
        assert_eq!(resolved.0, default);
        assert_eq!(
            resolve_profile(None, Some("%TEMP%/profile".into()), &root, || Ok(default))
                .err()
                .as_deref(),
            Some("SMA_PROFILE_DIR_LITERAL_REQUIRED")
        );
        assert!(!selected_dir.join(".local").exists());
        assert!(!selected_dir.join("process").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn startup_path_rejects_invalid_inputs_before_writes() {
        let root = fixture_root();
        let invalid_selector = [
            OsString::from(""),
            OsString::from("relative.env"),
            root.join("missing.env").into_os_string(),
            root.clone().into_os_string(),
        ];
        for selector in invalid_selector {
            assert!(
                resolve_profile(Some(selector), None, &root, || Ok(root.join("default"))).is_err()
            );
        }
        for bad in [
            "../escape",
            "nested/../escape",
            "$HOME/profile",
            "%TEMP%/profile",
            "%APPDATA%/profile",
            "%ProgramFiles(x86)%/profile",
            "~/profile",
            "<profile>",
        ] {
            assert!(
                resolve_profile(None, Some(bad.into()), &root, || Ok(root.join("default")))
                    .is_err(),
                "{bad}"
            );
        }
        let literal_percent = root.join("literal-100%/profile");
        assert_eq!(
            profile(&root, None, Some(literal_percent.clone().into())),
            literal_percent
        );
        fs::write(root.join(".env"), "SMA_PROFILE_DIR=%TEMP%/profile\n").unwrap();
        assert_eq!(
            resolve_profile(None, None, &root, || Ok(root.join("default")))
                .err()
                .as_deref(),
            Some("SMA_PROFILE_DIR_LITERAL_REQUIRED")
        );
        fs::remove_file(root.join(".env")).unwrap();
        fs::write(root.join("ordinary-file"), "data").unwrap();
        assert_eq!(
            resolve_profile(None, Some("ordinary-file/child".into()), &root, || Ok(
                root.join("default")
            ))
            .err()
            .unwrap(),
            "SMA_PROFILE_DIR_NOT_DIRECTORY"
        );
        #[cfg(unix)]
        {
            use std::os::unix::{ffi::OsStringExt, fs::symlink};
            assert!(
                resolve_profile(None, Some(OsString::from_vec(vec![255])), &root, || Ok(
                    root.join("default")
                ))
                .is_err()
            );
            symlink(&root, root.join("link")).unwrap();
            assert_eq!(
                resolve_profile(None, Some("link/child".into()), &root, || Ok(
                    root.join("default")
                ))
                .err()
                .unwrap(),
                "SMA_PROFILE_DIR_SYMLINK"
            );
            symlink(root.join("missing.env"), root.join(".env")).unwrap();
            assert!(resolve_profile(None, None, &root, || Ok(root.join("default"))).is_err());
            fs::remove_file(root.join(".env")).unwrap();
        }
        #[cfg(windows)]
        for bad in [r"C:foo", r"\foo", r"C:"] {
            assert!(
                resolve_profile(None, Some(bad.into()), &root, || Ok(root.join("default")))
                    .is_err()
            );
        }
        fs::write(root.join(".env"), [255]).unwrap();
        assert!(resolve_profile(None, None, &root, || Ok(root.join("default"))).is_err());
        assert!(!root.join("default").exists());
        assert!(!root.join("ordinary-file/child").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn startup_path_rejects_readonly_nearest_directory_before_writes() {
        use std::os::unix::fs::PermissionsExt;

        let root = fixture_root();
        let locked = root.join("locked");
        fs::create_dir(&locked).unwrap();
        let known_child = locked.join("known-child");
        fs::create_dir(&known_child).unwrap();
        fs::write(root.join(".env"), "SMA_PROFILE_DIR=locked/new-profile\n").unwrap();
        let original = fs::metadata(&locked).unwrap().permissions();
        fs::set_permissions(&locked, fs::Permissions::from_mode(0o555)).unwrap();
        let write_probe = locked.join("write-probe");
        let can_write = match fs::create_dir(&write_probe) {
            Ok(()) => {
                fs::remove_dir(&write_probe).unwrap();
                true
            }
            Err(error) if error.kind() == std::io::ErrorKind::PermissionDenied => false,
            Err(error) => panic!("unexpected fixture error: {error}"),
        };
        let results: Vec<_> = [locked.clone(), locked.join("new-profile")]
            .into_iter()
            .map(|path| {
                resolve_profile(None, Some(path.into()), &root, || Ok(root.join("default"))).err()
            })
            .collect();
        let from_file = resolve_profile(None, None, &root, || Ok(root.join("default"))).err();
        fs::set_permissions(&locked, fs::Permissions::from_mode(0o666)).unwrap();
        let can_search = fs::metadata(&known_child).is_ok();
        let not_searchable =
            resolve_profile(None, Some(locked.join("new-profile").into()), &root, || {
                Ok(root.join("default"))
            })
            .err();
        fs::set_permissions(&locked, original).unwrap();
        for result in results {
            assert_eq!(
                result.as_deref(),
                (!can_write).then_some("SMA_PROFILE_DIR_NOT_WRITABLE")
            );
        }
        assert_eq!(
            from_file.as_deref(),
            (!can_write).then_some("SMA_PROFILE_DIR_NOT_WRITABLE")
        );
        assert_eq!(
            not_searchable.as_deref(),
            (!can_search).then_some("SMA_PROFILE_DIR_NOT_SEARCHABLE")
        );
        assert!(!locked.join("new-profile").exists());
        assert!(!locked.join("logs").exists());
        assert!(!locked.join("configuration.sqlite3").exists());
        assert!(!locked.join("runtime-startup.json").exists());
        assert!(!root.join("default").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn startup_path_checks_effective_user_and_allows_writable_existing_child() {
        use std::os::unix::fs::PermissionsExt;

        let root = fixture_root();
        let parent = root.join("owner-without-write");
        let existing_child = parent.join("writable-child");
        fs::create_dir_all(&existing_child).unwrap();
        let original = fs::metadata(&parent).unwrap().permissions();
        fs::set_permissions(&parent, fs::Permissions::from_mode(0o557)).unwrap();
        let write_probe = parent.join("write-probe");
        let can_write = match fs::create_dir(&write_probe) {
            Ok(()) => {
                fs::remove_dir(&write_probe).unwrap();
                true
            }
            Err(error) if error.kind() == std::io::ErrorKind::PermissionDenied => false,
            Err(error) => panic!("unexpected fixture error: {error}"),
        };
        println!("0557 fixture current process can create a directory: {can_write}");
        let parent_result = resolve_profile(None, Some(parent.clone().into()), &root, || {
            Ok(root.join("default"))
        })
        .err();
        let missing_result =
            resolve_profile(None, Some(parent.join("new-profile").into()), &root, || {
                Ok(root.join("default"))
            })
            .err();
        let child_result =
            resolve_profile(None, Some(existing_child.clone().into()), &root, || {
                Ok(root.join("default"))
            });
        fs::set_permissions(&parent, original).unwrap();
        let expected = (!can_write).then_some("SMA_PROFILE_DIR_NOT_WRITABLE");
        assert_eq!(parent_result.as_deref(), expected);
        assert_eq!(missing_result.as_deref(), expected);
        assert_eq!(child_result.unwrap().0, existing_child);
        assert!(!parent.join("new-profile").exists());
        assert!(!parent.join("logs").exists());
        assert!(!parent.join("configuration.sqlite3").exists());
        assert!(!parent.join("runtime-startup.json").exists());
        assert!(!root.join("default").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn startup_log_initialization_returns_filesystem_errors() {
        let root = fixture_root();
        let directory = root.join("profile");
        fs::create_dir(&directory).unwrap();
        let logs = directory.join("logs");
        fs::write(&logs, "unchanged fixture").unwrap();
        let resolved = resolve_profile(None, Some(directory.clone().into()), &root, || {
            Ok(root.join("default"))
        })
        .unwrap();
        let defaults = AppDefaults {
            backend_base_url: String::new(),
            external_io_enabled: false,
            configuration_source: "synthetic fixture".into(),
        };
        let result =
            std::panic::catch_unwind(|| crate::infrastructure::logging::init(&resolved, &defaults))
                .expect("log setup must return an error rather than panic");
        let error = result.err().expect("log setup must fail for a file");
        assert!(error
            .to_string()
            .contains("SMA_PROFILE_DIR_LOGGING_UNAVAILABLE"));
        assert_eq!(fs::read_to_string(&logs).unwrap(), "unchanged fixture");
        assert!(!directory.join("configuration.sqlite3").exists());
        assert!(!directory.join("runtime-startup.json").exists());
        assert!(!root.join("default").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn startup_path_is_independent_of_process_cwd() {
        const CHILD_ROOT: &str = "SMA007_CWD_TEST_ROOT";
        if let Some(root) = std::env::var_os(CHILD_ROOT) {
            let root = PathBuf::from(root);
            assert_eq!(profile(&root, None, None), root.join(".local/dev"));
            assert_eq!(
                profile(&root, Some(root.join("selected/config.env").into()), None),
                root.join("selected/.local/dev")
            );
            assert_eq!(
                profile(&root, None, Some("process".into())),
                root.join("process")
            );
            return;
        }
        let root = fixture_root();
        fs::create_dir_all(root.join("selected")).unwrap();
        fs::create_dir(root.join("different-cwd")).unwrap();
        fs::write(root.join(".env"), "SMA_PROFILE_DIR=.local/dev\n").unwrap();
        fs::write(
            root.join("selected/config.env"),
            "SMA_PROFILE_DIR=./.local/dev\n",
        )
        .unwrap();
        fs::write(root.join("different-cwd/.env"), "SMA_PROFILE_DIR=wrong\n").unwrap();
        for cwd in [&root, &root.join("different-cwd")] {
            let status = Command::new(std::env::current_exe().unwrap())
                .args([
                    "--exact",
                    "config::startup_path_tests::startup_path_is_independent_of_process_cwd",
                ])
                .env(CHILD_ROOT, &root)
                .current_dir(cwd)
                .status()
                .unwrap();
            assert!(status.success());
        }
        assert!(!root.join(".local").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn startup_path_keeps_http_and_backend_reader_precedence() {
        const CHILD_CASE: &str = "SMA007_DEFAULTS_TEST_CASE";
        if let Ok(case) = std::env::var(CHILD_CASE) {
            let defaults = load_defaults_from_env();
            match case.as_str() {
                "file" => {
                    assert!(!defaults.external_io_enabled);
                    assert_eq!(defaults.backend_base_url, "http://file.invalid");
                    assert!(require_external_io().is_err());
                }
                "process" => {
                    assert!(defaults.external_io_enabled);
                    assert_eq!(defaults.backend_base_url, "");
                    assert!(require_external_io().is_ok());
                }
                "process-off" | "empty-file" => {
                    assert!(!defaults.external_io_enabled);
                    assert_eq!(defaults.backend_base_url, "");
                    assert!(require_external_io().is_err());
                }
                _ => panic!("unexpected child case"),
            }
            return;
        }
        let root = fixture_root();
        let env = root.join("selected.env");
        fs::write(
            &env,
            "SMA_HTTP_ENABLED=true\nSMA_HTTP_ENABLED=false\nSMA_BACKEND_BASE_URL=http://file.invalid\n",
        )
        .unwrap();
        let enabled_env = root.join("enabled.env");
        fs::write(&enabled_env, "SMA_HTTP_ENABLED=true\n").unwrap();
        let empty_env = root.join("empty.env");
        fs::write(&empty_env, "").unwrap();
        fs::write(root.join(".env"), "SMA_HTTP_ENABLED=true\n").unwrap();
        for case in ["file", "process", "process-off", "empty-file"] {
            let mut child = Command::new(std::env::current_exe().unwrap());
            let selected = match case {
                "process-off" => &enabled_env,
                "empty-file" => &empty_env,
                _ => &env,
            };
            child.args(["--exact", "config::startup_path_tests::startup_path_keeps_http_and_backend_reader_precedence"])
                .env(CHILD_CASE, case)
                .env("SMA_ENV_FILE", selected)
                .env_remove("SMA_HTTP_ENABLED")
                .env_remove("SMA_BACKEND_BASE_URL");
            if case == "process" {
                child
                    .env("SMA_HTTP_ENABLED", "true")
                    .env("SMA_BACKEND_BASE_URL", "");
            }
            if case == "process-off" {
                child.env("SMA_HTTP_ENABLED", "false");
            }
            assert!(child.status().unwrap().success());
        }
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn startup_path_uses_one_root_for_storage_logs_and_preferences() {
        let root = fixture_root();
        fs::write(root.join(".env"), "SMA_PROFILE_DIR=./.local/dev\n").unwrap();
        let resolved = resolve_profile(None, None, &root, || Ok(root.join("default"))).unwrap();
        let expected_root = root.join(".local/dev");
        assert_eq!(
            resolved.database_path(),
            expected_root.join("configuration.sqlite3")
        );
        assert_eq!(resolved.logging_directory(), expected_root.join("logs"));
        assert_eq!(
            resolved.startup_preferences_path(),
            expected_root.join("runtime-startup.json")
        );

        let defaults = AppDefaults {
            backend_base_url: String::new(),
            external_io_enabled: false,
            configuration_source: "synthetic fixture".into(),
        };
        let guard = crate::infrastructure::logging::init(&resolved, &defaults).unwrap();
        let mut store = ConfigStore::open(&resolved.database_path()).unwrap();
        let snapshot = store
            .update(0, |old| {
                let mut next = old.clone();
                next.connection.host = "fixture.invalid".into();
                next.connection.port = 8080;
                Ok(next)
            })
            .unwrap();
        assert_eq!(snapshot.revision, 1);
        let mut preferences = runtime_startup::RuntimeStartupPreferences::default();
        preferences.runtime_auto_start.api_mapping_runtime.enabled = true;
        runtime_startup::save_to_path(&resolved.startup_preferences_path(), &preferences).unwrap();
        let preference_bytes = fs::read(resolved.startup_preferences_path()).unwrap();
        drop(store);
        drop(guard);

        let reopened = ConfigStore::open(&resolved.database_path())
            .unwrap()
            .load()
            .unwrap();
        assert_eq!(reopened, snapshot);
        assert_eq!(
            runtime_startup::load_from_path(&resolved.startup_preferences_path()).unwrap(),
            preferences
        );
        assert_eq!(
            fs::read(resolved.startup_preferences_path()).unwrap(),
            preference_bytes
        );
        assert!(fs::read_dir(resolved.logging_directory())
            .unwrap()
            .next()
            .is_some());
        let other = ConfigStore::open(&root.join("other/configuration.sqlite3"))
            .unwrap()
            .load()
            .unwrap();
        assert_eq!(other.revision, 0);
        assert_ne!(other.document.connection.host, "fixture.invalid");
        fs::remove_dir_all(root).unwrap();
    }
}
