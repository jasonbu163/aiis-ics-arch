//! 保存配置逐 PLC 导出：验证完整声明，预览绑定目录，不覆盖地原子发布。
use super::local_supervisor::LocalEngine;
use crate::domain::{
    local_configuration::{self, id, LocalResult, PointDisplayNames},
    local_runtime::ConfigurationSnapshot,
    local_sample::{digest, now},
    plc_catalog::{self, Catalog, CatalogDb, CatalogPlc, CatalogPoint, Connection, Export, Origin},
};
use serde::Deserialize;
use serde_json::{json, Value};
#[cfg(unix)]
use std::os::{
    fd::AsRawFd,
    unix::fs::{MetadataExt, OpenOptionsExt},
};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct StateRequest {
    pub state: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct PreviewRequest {
    pub state: String,
    pub plc_ids: Vec<String>,
    pub filenames: BTreeMap<String, String>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct TokenRequest {
    pub token: String,
}
struct Item {
    id: String,
    name: String,
    filename: String,
    bytes: Option<Vec<u8>>,
    sha: Option<String>,
    issues: Vec<Value>,
}
struct Directory {
    path: PathBuf,
    file: File,
    identity: (u64, u64),
    conflicts: BTreeMap<String, bool>,
}
struct Pending {
    snapshot: ConfigurationSnapshot,
    loaded: Option<String>,
    expires: Instant,
    items: Vec<Item>,
    directory: Option<Directory>,
}
#[derive(Default)]
pub(crate) struct CatalogExports {
    pending: BTreeMap<String, Pending>,
}

fn issue(code: &str, db: Option<&str>, point: Option<&str>) -> Value {
    json!({"code": code, "dbId": db, "pointId": point})
}

/// 校验完整文件名；单文件名、跨平台设备名及本应用私有来源前缀均不得绕过。
fn filename_error(filename: &str) -> Option<&'static str> {
    if filename.len() > 255 {
        return Some("catalog_filename_length");
    }
    if filename.chars().any(|c| {
        c.is_ascii_control() || matches!(c, '/' | '\\' | '<' | '>' | ':' | '"' | '|' | '?' | '*')
    }) {
        return Some("catalog_filename_characters");
    }
    if filename.is_empty() || filename.trim().is_empty() {
        return Some("catalog_filename_required");
    }
    if !filename.to_ascii_lowercase().ends_with(".json") {
        return Some("catalog_filename_extension");
    }
    let stem = &filename[..filename.len() - 5];
    if stem.trim().is_empty() {
        return Some("catalog_filename_required");
    }
    if stem.ends_with([' ', '.']) {
        return Some("catalog_filename_ending");
    }
    let device = stem
        .split('.')
        .next()
        .unwrap_or("")
        .trim_end_matches(' ')
        .to_ascii_uppercase();
    if matches!(
        device.as_str(),
        "CON"
            | "PRN"
            | "AUX"
            | "NUL"
            | "COM1"
            | "COM2"
            | "COM3"
            | "COM4"
            | "COM5"
            | "COM6"
            | "COM7"
            | "COM8"
            | "COM9"
            | "LPT1"
            | "LPT2"
            | "LPT3"
            | "LPT4"
            | "LPT5"
            | "LPT6"
            | "LPT7"
            | "LPT8"
            | "LPT9"
    ) || filename.starts_with(crate::domain::yaml_migration::PRIVATE_NAME)
        || filename.starts_with(crate::domain::local_runtime::STARTUP_PRIVATE_NAME)
    {
        return Some("catalog_filename_reserved");
    }
    None
}

/// 只从所选持久 payload 构建完整实例；每个错误指出 PLC、DB 或点的位置。
fn build(snapshot: &ConfigurationSnapshot, plc_id: &str) -> Result<Catalog, Vec<Value>> {
    let c = &snapshot.configuration;
    let Some(plc) = c.plcs.iter().find(|p| p.id == plc_id) else {
        return Err(vec![issue("catalog_plc_missing", None, None)]);
    };
    let mut issues = Vec::new();
    if !plc_catalog::canonical_id(&plc.id) {
        issues.push(issue("catalog_identity_conflict", None, None));
    }
    let dbs: Vec<_> = c.dbs.iter().filter(|d| d.plc_id == plc.id).collect();
    if dbs.is_empty() || dbs.len() > 32 {
        issues.push(issue("catalog_db_invalid", None, None));
    }
    if c.points
        .iter()
        .any(|p| p.plc_id == plc.id && !dbs.iter().any(|d| d.id == p.db_id))
    {
        issues.push(issue("catalog_binding_invalid", None, None));
    }
    if plc_catalog::verify_bindings(c).is_err() {
        issues.push(issue("catalog_binding_invalid", None, None));
    }
    let bound_count = dbs
        .iter()
        .filter(|d| c.catalog_bindings.iter().any(|b| b.local_db_id == d.id))
        .count();
    if bound_count != 0 && bound_count != dbs.len() {
        issues.push(issue("catalog_binding_invalid", None, None));
    }
    let mut origin = None;
    let mut output_dbs = Vec::new();
    let mut names = BTreeSet::new();
    for db in dbs {
        let binding = c.catalog_bindings.iter().find(|b| b.local_db_id == db.id);
        let Some(source) = c
            .sources
            .iter()
            .find(|s| s.id == db.source_id && s.plc_id == plc.id)
        else {
            issues.push(issue("catalog_source_invalid", Some(&db.id), None));
            continue;
        };
        if source.sha256 != digest(&source.content) || !db.complete {
            issues.push(issue("catalog_source_invalid", Some(&db.id), None));
        }
        let original = if binding.is_some() {
            match plc_catalog::parse(source.content.as_bytes()) {
                Ok((catalog, _, _)) => {
                    if origin.as_ref().is_some_and(|o| o != &catalog.origin) {
                        issues.push(issue("catalog_origin_conflict", Some(&db.id), None));
                    }
                    origin = Some(catalog.origin.clone());
                    Some(catalog)
                }
                Err(code) => {
                    issues.push(issue(&code, Some(&db.id), None));
                    None
                }
            }
        } else {
            let source_valid = db
                .import_binding
                .as_ref()
                .map(|b| {
                    b.lineage_id == source.lineage_id.as_deref().unwrap_or(&source.id)
                        && b.block_key.kind == "DATA_BLOCK"
                        && b.block_key.name == db.name
                        && b.udt_source_ids.iter().all(|id| {
                            c.sources.iter().any(|s| {
                                s.id == *id && s.plc_id == plc.id && s.sha256 == digest(&s.content)
                            })
                        })
                })
                .unwrap_or(
                    source.db_number == Some(db.number)
                        || source.name.ends_with(".yaml")
                        || source.name.ends_with(".yml"),
                );
            if !source_valid {
                issues.push(issue("catalog_source_invalid", Some(&db.id), None));
            }
            None
        };
        let source_db = binding.and_then(|b| {
            original
                .as_ref()?
                .dbs
                .iter()
                .find(|d| d.id == b.origin_db_id)
        });
        if binding.is_some() && source_db.is_none() {
            issues.push(issue("catalog_binding_invalid", Some(&db.id), None));
        }
        let mut points = Vec::new();
        let mut occupied = BTreeMap::<(u32, u8), String>::new();
        for point in c.points.iter().filter(|p| p.db_id == db.id) {
            let location = (Some(db.id.as_str()), Some(point.id.as_str()));
            if point.plc_id != plc.id
                || aiis_tia_import_core::validate_manual_name(&point.name).is_err()
                || !names.insert(point.name.clone())
            {
                issues.push(issue("catalog_point_invalid", location.0, location.1));
            }
            if binding.is_none()
                && !local_configuration::leaf_matches(
                    &db.tree,
                    &point.source_path,
                    &point.data_type,
                )
            {
                issues.push(issue("point_source_mismatch", location.0, location.1));
            }
            let Some(address) = point.address.as_ref() else {
                issues.push(issue("address_required", location.0, location.1));
                continue;
            };
            if !address.confirmed
                || address.reason.trim().is_empty()
                || !matches!(address.origin.as_str(), "manual" | "inferred" | "catalog")
                || (address.origin == "catalog" && binding.is_none())
            {
                issues.push(issue("address_invalid", location.0, location.1));
            }
            let Some(width) = local_configuration::width(&point.data_type) else {
                issues.push(issue("catalog_type_invalid", location.0, location.1));
                continue;
            };
            if point.data_type.starts_with("STRING[")
                && point.data_type != format!("STRING[{}]", width - 2)
            {
                issues.push(issue("catalog_type_invalid", location.0, location.1));
            }
            let valid_address = address
                .offset
                .checked_add(width)
                .is_some_and(|end| end <= db.length && end <= 65536)
                && if point.data_type == "BOOL" {
                    address.bit.is_some_and(|bit| bit <= 7)
                } else {
                    address.bit.is_none()
                };
            if !valid_address {
                issues.push(issue("catalog_address_invalid", location.0, location.1));
            } else {
                for byte in address.offset..address.offset + width {
                    for bit in 0..8 {
                        if point.data_type == "BOOL" && address.bit != Some(bit) {
                            continue;
                        }
                        if occupied.insert((byte, bit), point.id.clone()).is_some() {
                            issues.push(issue("catalog_address_overlap", location.0, location.1));
                        }
                    }
                }
            }
            let mapping = binding.and_then(|b| {
                b.point_mappings
                    .iter()
                    .find(|m| m.local_point_id == point.id)
            });
            let source_point = mapping.and_then(|m| {
                source_db?
                    .points
                    .iter()
                    .find(|p| p.id == m.catalog_point_id)
            });
            if binding.is_some() && source_point.is_none() {
                issues.push(issue("catalog_binding_invalid", location.0, location.1));
            }
            points.push(CatalogPoint {
                id: mapping
                    .map(|m| m.catalog_point_id.clone())
                    .unwrap_or_else(|| point.id.clone()),
                name: point.name.clone(),
                display_name: c.point_legacy_display_names.get(&point.id).cloned(),
                display_names: Some(
                    c.point_display_names
                        .get(&point.id)
                        .cloned()
                        .unwrap_or_else(PointDisplayNames::default),
                ),
                description: Some(point.comment.clone()),
                source_path: source_point
                    .map(|p| p.source_path.clone())
                    .unwrap_or_else(|| {
                        if point.source_path.is_empty() {
                            None
                        } else {
                            Some(point.source_path.clone())
                        }
                    }),
                data_type: point.data_type.clone(),
                byte_offset: address.offset,
                bit: address.bit,
                source_enabled: point.enabled,
            });
        }
        if points.is_empty() {
            issues.push(issue("catalog_db_invalid", Some(&db.id), None));
        }
        output_dbs.push(CatalogDb {
            id: binding
                .map(|b| b.origin_db_id.clone())
                .unwrap_or_else(|| db.id.clone()),
            name: db.name.clone(),
            number: db.number,
            size_bytes: db.length,
            source_enabled: None,
            points,
        });
    }
    let catalog = Catalog {
        format: "aiis.plc_points".into(),
        schema_version: 1,
        origin: origin.unwrap_or_else(|| Origin {
            kind: "data_acquisition_agent".into(),
            profile_id: snapshot.instance.clone(),
            plc_id: plc.id.clone(),
        }),
        export: Export {
            producer: "data_acquisition_agent".into(),
            profile_id: snapshot.instance.clone(),
            config_state: snapshot.state.clone(),
            revision_id: snapshot.revision.clone(),
            payload_sha256: snapshot.payload_sha256.clone(),
            exported_at: now(),
        },
        plc: CatalogPlc {
            name: plc.name.clone(),
            protocol: "s7".into(),
            connection: Connection {
                host: plc.host.clone(),
                port: plc.port,
                rack: plc.rack,
                slot: plc.slot,
                local_tsap: None,
                remote_tsap: None,
            },
        },
        dbs: output_dbs,
    };
    if let Err(code) = catalog.validate() {
        issues.push(issue(&code, None, None));
    }
    if issues.is_empty() {
        Ok(catalog)
    } else {
        Err(issues)
    }
}

impl LocalEngine {
    fn export_snapshot(&self, state: &str) -> LocalResult<ConfigurationSnapshot> {
        let state = state.to_string();
        self.storage
            .call(true, move |s| s.catalog_export_snapshot(&state))
    }
    pub fn catalog_export_inspect(&self, request: StateRequest) -> LocalResult<Value> {
        let _activation = self
            .activation
            .try_lock()
            .map_err(|_| "activation_pending")?;
        let _mutation = self
            .configuration_mutation
            .lock()
            .map_err(|_| "configuration_busy")?;
        let snapshot = self.export_snapshot(&request.state)?;
        let loaded = self
            .loaded
            .lock()
            .unwrap()
            .as_ref()
            .map(|v| v.revision.clone());
        let plcs: Vec<_> = snapshot.configuration.plcs.iter().map(|p| json!({"id":p.id,"name":p.name,"host":p.host,"port":p.port,"rack":p.rack,"slot":p.slot,"dbCount":snapshot.configuration.dbs.iter().filter(|d|d.plc_id==p.id).count(),"pointCount":snapshot.configuration.points.iter().filter(|v|v.plc_id==p.id).count()})).collect();
        Ok(
            json!({"state":snapshot.state,"revision":snapshot.revision,"payloadSha256":snapshot.payload_sha256,"active":snapshot.active,"loaded":loaded,"used":snapshot.used,"plcs":plcs}),
        )
    }
    pub fn catalog_export_preview(&self, request: PreviewRequest) -> LocalResult<Value> {
        let _activation = self
            .activation
            .try_lock()
            .map_err(|_| "activation_pending")?;
        let _mutation = self
            .configuration_mutation
            .lock()
            .map_err(|_| "configuration_busy")?;
        let ids: BTreeSet<_> = request.plc_ids.iter().collect();
        if ids.is_empty() || ids.len() != request.plc_ids.len() || ids.len() > 4 {
            return Err("catalog_selection".into());
        }
        if request.filenames.keys().any(|key| !ids.contains(key)) {
            return Err("catalog_selection".into());
        }
        let mut filename_errors = Vec::new();
        let mut counts = BTreeMap::<String, usize>::new();
        for plc_id in &request.plc_ids {
            let filename = request
                .filenames
                .get(plc_id)
                .map(String::as_str)
                .unwrap_or("");
            if let Some(code) = filename_error(filename) {
                filename_errors.push(json!({"plcId":plc_id,"code":code}));
            }
            *counts.entry(filename.to_lowercase()).or_default() += 1;
        }
        for plc_id in &request.plc_ids {
            if let Some(filename) = request.filenames.get(plc_id) {
                if counts.get(&filename.to_lowercase()).copied().unwrap_or(0) > 1 {
                    filename_errors
                        .push(json!({"plcId":plc_id,"code":"catalog_filename_duplicate"}));
                }
            }
        }
        if !filename_errors.is_empty() {
            return Ok(json!({"filenameErrors":filename_errors}));
        }
        let snapshot = self.export_snapshot(&request.state)?;
        let loaded = self
            .loaded
            .lock()
            .unwrap()
            .as_ref()
            .map(|v| v.revision.clone());
        let mut items = Vec::new();
        let mut rows = Vec::new();
        for plc_id in &request.plc_ids {
            let filename = request
                .filenames
                .get(plc_id)
                .expect("validated filename")
                .clone();
            let name = snapshot
                .configuration
                .plcs
                .iter()
                .find(|p| &p.id == plc_id)
                .map(|p| p.name.clone())
                .unwrap_or_else(|| plc_id.clone());
            let (document, mut issues) = match build(&snapshot, plc_id) {
                Ok(d) => (Some(d), vec![]),
                Err(e) => (None, e),
            };
            let bytes = if let Some(doc) = &document {
                let bytes = serde_json::to_vec_pretty(doc).map_err(|_| "encoding_failed")?;
                if let Err(code) = plc_catalog::parse(&bytes) {
                    issues.push(issue(&code, None, None));
                    None
                } else {
                    Some(bytes)
                }
            } else {
                None
            };
            let sha = bytes
                .as_ref()
                .map(|b| digest(std::str::from_utf8(b).expect("serialized JSON is UTF-8")));
            rows.push(json!({"plcId":plc_id,"name":name,"filename":filename,"document":document,"issues":issues,"fileSha256":sha,"byteCount":bytes.as_ref().map(Vec::len)}));
            items.push(Item {
                id: plc_id.clone(),
                name,
                filename,
                bytes,
                sha,
                issues,
            });
        }
        let token = id();
        let mut sessions = self.catalog_exports.lock().map_err(|_| "catalog_state")?;
        sessions
            .pending
            .retain(|_, pending| pending.expires > Instant::now());
        if sessions.pending.len() >= 8 {
            return Err("catalog_preview_capacity".into());
        }
        sessions.pending.insert(
            token.clone(),
            Pending {
                snapshot: snapshot.clone(),
                loaded: loaded.clone(),
                expires: Instant::now() + Duration::from_secs(300),
                items,
                directory: None,
            },
        );
        Ok(
            json!({"token":token,"state":snapshot.state,"revision":snapshot.revision,"payloadSha256":snapshot.payload_sha256,"active":snapshot.active,"loaded":loaded,"used":snapshot.used,"rows":rows}),
        )
    }
}

#[cfg(unix)]
fn directory(path: &Path) -> Result<Directory, String> {
    let path = fs::canonicalize(path).map_err(|_| "catalog_directory")?;
    let file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
        .open(&path)
        .map_err(|_| "catalog_directory")?;
    let metadata = file.metadata().map_err(|_| "catalog_directory")?;
    if !metadata.is_dir() {
        return Err("catalog_directory".into());
    }
    Ok(Directory {
        path,
        file,
        identity: (metadata.dev(), metadata.ino()),
        conflicts: BTreeMap::new(),
    })
}
#[cfg(not(unix))]
fn directory(_path: &Path) -> Result<Directory, String> {
    Err("catalog_platform_unsupported".into())
}
#[cfg(unix)]
fn directory_unchanged(dir: &Directory) -> bool {
    OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
        .open(&dir.path)
        .and_then(|f| f.metadata())
        .is_ok_and(|m| m.is_dir() && (m.dev(), m.ino()) == dir.identity)
}
#[cfg(not(unix))]
fn directory_unchanged(_dir: &Directory) -> bool {
    false
}
#[cfg(unix)]
fn exists(dir: &Directory, name: &str) -> Result<bool, String> {
    let name = std::ffi::CString::new(name).map_err(|_| "catalog_filename")?;
    let mut stat = std::mem::MaybeUninit::<libc::stat>::uninit();
    let result = unsafe {
        libc::fstatat(
            dir.file.as_raw_fd(),
            name.as_ptr(),
            stat.as_mut_ptr(),
            libc::AT_SYMLINK_NOFOLLOW,
        )
    };
    if result == 0 {
        Ok(true)
    } else if std::io::Error::last_os_error().raw_os_error() == Some(libc::ENOENT) {
        Ok(false)
    } else {
        Err("catalog_target_query".into())
    }
}
#[cfg(not(unix))]
fn exists(_dir: &Directory, _name: &str) -> Result<bool, String> {
    Err("catalog_platform_unsupported".into())
}
#[cfg(unix)]
fn link_failure(errno: Option<i32>) -> &'static str {
    if errno == Some(libc::EEXIST) {
        "catalog_target_changed"
    } else {
        "catalog_write"
    }
}
#[cfg(unix)]
fn write_new(dir: &Directory, filename: &str, bytes: &[u8]) -> Result<Option<String>, String> {
    use std::os::fd::FromRawFd;
    let tmp_name = format!(".daa019-{}.tmp", crate::domain::local_configuration::id());
    let tmp = std::ffi::CString::new(tmp_name.clone()).map_err(|_| "catalog_filename")?;
    let dest = std::ffi::CString::new(filename).map_err(|_| "catalog_filename")?;
    let fd = unsafe {
        libc::openat(
            dir.file.as_raw_fd(),
            tmp.as_ptr(),
            libc::O_CREAT | libc::O_EXCL | libc::O_NOFOLLOW | libc::O_CLOEXEC | libc::O_RDWR,
            0o600,
        )
    };
    if fd < 0 {
        return Err("catalog_temp_create".into());
    }
    let mut file = unsafe { File::from_raw_fd(fd) };
    let identity = file
        .metadata()
        .map_err(|_| "catalog_verify")
        .map(|m| (m.dev(), m.ino()))?;
    let same_file = |name: &std::ffi::CStr| {
        let mut stat = std::mem::MaybeUninit::<libc::stat>::uninit();
        if unsafe {
            libc::fstatat(
                dir.file.as_raw_fd(),
                name.as_ptr(),
                stat.as_mut_ptr(),
                libc::AT_SYMLINK_NOFOLLOW,
            )
        } != 0
        {
            return false;
        }
        let stat = unsafe { stat.assume_init() };
        (stat.st_dev as u64, stat.st_ino as u64) == identity
            && (stat.st_mode & libc::S_IFMT) == libc::S_IFREG
    };
    let result = (|| {
        file.write_all(bytes).map_err(|_| "catalog_write")?;
        file.sync_all().map_err(|_| "catalog_write")?;
        use std::io::Seek;
        file.rewind().map_err(|_| "catalog_verify")?;
        let mut check = Vec::new();
        file.read_to_end(&mut check).map_err(|_| "catalog_verify")?;
        if check != bytes || !same_file(&tmp) {
            return Err("catalog_verify");
        }
        if !directory_unchanged(dir) {
            return Err("catalog_directory_changed");
        }
        // linkat 的目标创建是排他原子操作：目标即使在最后一刻出现也绝不覆盖。
        if unsafe {
            libc::linkat(
                dir.file.as_raw_fd(),
                tmp.as_ptr(),
                dir.file.as_raw_fd(),
                dest.as_ptr(),
                0,
            )
        } != 0
        {
            return Err(link_failure(std::io::Error::last_os_error().raw_os_error()));
        }
        // 无法确认落盘后身份时保留对象并报告未知，不能删除可能已被换入的用户文件。
        if !same_file(&dest) || !directory_unchanged(dir) {
            return Err("catalog_write_result_unknown");
        }
        Ok(())
    })();
    let cleaned =
        same_file(&tmp) && unsafe { libc::unlinkat(dir.file.as_raw_fd(), tmp.as_ptr(), 0) } == 0;
    match (result, cleaned) {
        (Ok(()), true) => Ok(None),
        (Ok(()), false) => Ok(Some(tmp_name)),
        (Err(error), true) => Err(error.into()),
        (Err("catalog_write_result_unknown"), false) => Err("catalog_write_result_unknown".into()),
        (Err(_), false) => Err("catalog_temp_cleanup".into()),
    }
}

#[cfg(all(test, unix))]
mod tests {
    use super::{filename_error, link_failure};
    #[test]
    fn exclusive_link_distinguishes_conflict_from_other_write_errors() {
        assert_eq!(link_failure(Some(libc::EEXIST)), "catalog_target_changed");
        assert_eq!(link_failure(Some(libc::EPERM)), "catalog_write");
        assert_eq!(link_failure(Some(libc::EIO)), "catalog_write");
        assert_eq!(link_failure(None), "catalog_write");
    }
    #[test]
    fn exported_filename_is_safe_and_compatible_with_import() {
        for name in ["温度.json", "A.JSON", "station.1.json"] {
            assert_eq!(filename_error(name), None, "{name}");
        }
        for (name, code) in [
            ("", "catalog_filename_required"),
            (".json", "catalog_filename_required"),
            ("file", "catalog_filename_extension"),
            ("x .json", "catalog_filename_ending"),
            ("x..json", "catalog_filename_ending"),
            ("../x.json", "catalog_filename_characters"),
            ("a\\b.json", "catalog_filename_characters"),
            ("a\u{7f}.json", "catalog_filename_characters"),
            ("CON.json", "catalog_filename_reserved"),
            ("com1.other.JSON", "catalog_filename_reserved"),
            (
                "__daa_yaml_migration_v1__foo.json",
                "catalog_filename_reserved",
            ),
            (
                "__daa_startup_settings_v1__foo.json",
                "catalog_filename_reserved",
            ),
        ] {
            assert_eq!(filename_error(name), Some(code), "{name}");
        }
        assert_eq!(
            filename_error(&format!("{}.json", "界".repeat(84))),
            Some("catalog_filename_length")
        );
    }
}
#[cfg(not(unix))]
fn write_new(_dir: &Directory, _id: &str, _bytes: &[u8]) -> Result<Option<String>, String> {
    Err("catalog_platform_unsupported".into())
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct CommitRequest {
    pub token: String,
    pub confirm_targets: bool,
}
impl LocalEngine {
    /// 原生选择器开启前先撤销旧目录；内容预览令牌仍可用于新的目录选择。
    pub fn catalog_export_release_directory(&self, token: &str) -> LocalResult<()> {
        let mut sessions = self.catalog_exports.lock().map_err(|_| "catalog_state")?;
        let pending = sessions
            .pending
            .get_mut(token)
            .ok_or("catalog_preview_stale")?;
        if pending.expires <= Instant::now() {
            sessions.pending.remove(token);
            return Err("catalog_preview_stale".into());
        }
        pending.directory = None;
        Ok(())
    }

    /// 目录路径只来自原生选择器，前端只能持有短期令牌。
    pub fn catalog_export_directory(&self, token: &str, path: &Path) -> LocalResult<Value> {
        let mut sessions = self.catalog_exports.lock().map_err(|_| "catalog_state")?;
        let pending = sessions
            .pending
            .get_mut(token)
            .ok_or("catalog_preview_stale")?;
        if pending.expires <= Instant::now() {
            sessions.pending.remove(token);
            return Err("catalog_preview_stale".into());
        }
        // 重选失败也撤销旧目录，不能用同一预览意外提交到上一次选择的位置。
        pending.directory = None;
        let mut dir = directory(path)?;
        if !directory_unchanged(&dir) {
            return Err("catalog_directory_changed".into());
        }
        let mut rows = Vec::new();
        for item in &pending.items {
            let filename = &item.filename;
            let conflict = exists(&dir, filename)?;
            dir.conflicts.insert(item.id.clone(), conflict);
            rows.push(json!({"plcId":item.id,"name":item.name,"filename":filename,"conflict":conflict,"valid":item.bytes.is_some()}));
        }
        pending.directory = Some(dir);
        Ok(json!({"rows":rows}))
    }
    pub fn catalog_export_cancel(&self, request: TokenRequest) -> LocalResult<Value> {
        self.catalog_exports
            .lock()
            .map_err(|_| "catalog_state")?
            .pending
            .remove(&request.token);
        Ok(json!({"result":"cancelled"}))
    }
    pub fn catalog_export_commit(&self, request: CommitRequest) -> LocalResult<Value> {
        if !request.confirm_targets {
            return Err("catalog_target_confirmation".into());
        }
        let _activation = self
            .activation
            .try_lock()
            .map_err(|_| "activation_pending")?;
        let _mutation = self
            .configuration_mutation
            .lock()
            .map_err(|_| "configuration_busy")?;
        let pending = self
            .catalog_exports
            .lock()
            .map_err(|_| "catalog_state")?
            .pending
            .remove(&request.token)
            .ok_or("catalog_preview_stale")?;
        if pending.expires <= Instant::now() {
            return Err("catalog_preview_stale".into());
        }
        let dir = pending.directory.ok_or("catalog_directory_required")?;
        let current = self.export_snapshot(&pending.snapshot.state)?;
        let loaded = self
            .loaded
            .lock()
            .unwrap()
            .as_ref()
            .map(|v| v.revision.clone());
        if current.revision != pending.snapshot.revision
            || current.payload_sha256 != pending.snapshot.payload_sha256
            || current.active != pending.snapshot.active
            || current.used != pending.snapshot.used
            || loaded != pending.loaded
            || !directory_unchanged(&dir)
        {
            return Err("catalog_preview_stale".into());
        }
        let mut rows = Vec::new();
        for item in pending.items {
            let outcome = if item.bytes.is_none() {
                Err("catalog_validation".into())
            } else if dir.conflicts.get(&item.id) != Some(&false) {
                Err("catalog_target_exists".into())
            } else {
                write_new(&dir, &item.filename, item.bytes.as_ref().unwrap())
            };
            let success = outcome.is_ok();
            let code = outcome.as_ref().err();
            rows.push(json!({"plcId":item.id,"name":item.name,"filename":item.filename,"result":if success {"written"} else if code.is_some_and(|c|c == "catalog_write_result_unknown") {"unknown"} else {"failed"},"errorCode":code,"cleanupPending":outcome.ok().flatten(),"fileSha256":if success {item.sha} else {None},"issues":item.issues}));
        }
        let written = rows.iter().filter(|row| row["result"] == "written").count();
        let unknown = rows.iter().any(|row| row["result"] == "unknown");
        Ok(json!({"rows":rows,"committed":if unknown {None} else {Some(written > 0)}}))
    }
}
