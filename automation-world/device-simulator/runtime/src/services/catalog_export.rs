//! 逐 PLC 保存版本导出：有界预览、原生选择目录绑定与不覆盖的原子创建。
use crate::{
    app::App,
    domain::{
        configuration::{hash_bytes, uuid},
        plc_catalog::{self, Target},
    },
    infrastructure::clock,
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
pub struct RevisionIntent {
    pub revision_id: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PreviewIntent {
    pub revision_id: String,
    pub targets: Vec<Target>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct TokenIntent {
    pub token: String,
}

struct Item {
    id: String,
    bytes: Option<Vec<u8>>,
    sha: Option<String>,
    issues: Vec<plc_catalog::Issue>,
    selected: Option<String>,
    loaded: Option<String>,
}
struct Directory {
    path: PathBuf,
    file: File,
    identity: (u64, u64),
    conflicts: BTreeMap<String, bool>,
}
struct Pending {
    revision: String,
    payload_sha: String,
    expires: Instant,
    items: Vec<Item>,
    directory: Option<Directory>,
}
#[derive(Default)]
pub struct CatalogExports {
    pending: BTreeMap<String, Pending>,
}

fn instance_facts(app: &App, id: &str) -> Result<(Option<String>, Option<String>), String> {
    let selected = app
        .configuration
        .store
        .selections()?
        .into_iter()
        .find(|s| s.instance_id == id)
        .map(|s| s.revision_id);
    let loaded = app
        .instances
        .lock()
        .map_err(|_| "catalog_state")?
        .get(id)
        .map(|i| i.context.owner.loaded_revision());
    Ok((selected, loaded))
}
pub fn inspect(app: &App, intent: RevisionIntent) -> Result<Value, String> {
    let _guard = app.revision_control.lock().map_err(|_| "catalog_state")?;
    let source = app
        .configuration
        .store
        .revision_snapshot(&intent.revision_id)?;
    let mut instances = Vec::new();
    for i in &source.workspace.instances {
        let (selected, loaded) = instance_facts(app, &i.id)?;
        instances.push(
            json!({"instanceId":i.id,"name":i.name,"host":i.host,"port":i.port,
            "rack":i.rack,"slot":i.slot,"localTsap":i.calling_tsap,"remoteTsap":i.called_tsap(),
            "selectedRevision":selected,"loadedRevision":loaded,"dbCount":i.dbs.len(),
            "pointCount":i.dbs.iter().map(|d| d.points.len()).sum::<usize>()}),
        );
    }
    Ok(json!({"revision":source.revision,"instances":instances}))
}
pub fn preview(app: &App, intent: PreviewIntent) -> Result<Value, String> {
    let _guard = app.revision_control.lock().map_err(|_| "catalog_state")?;
    let ids = intent
        .targets
        .iter()
        .map(|t| &t.instance_id)
        .collect::<BTreeSet<_>>();
    if ids.len() != intent.targets.len() || ids.is_empty() || ids.len() > 8 {
        return Err("catalog_selection".into());
    }
    let source = app
        .configuration
        .store
        .revision_snapshot(&intent.revision_id)?;
    let time = clock::calendar_timestamp().ok_or("catalog_clock")?;
    let mut items = Vec::new();
    let mut rows = Vec::new();
    for target in &intent.targets {
        let i = source
            .workspace
            .instances
            .iter()
            .find(|i| i.id == target.instance_id)
            .ok_or("catalog_instance_missing")?;
        let (selected, loaded) = instance_facts(app, &i.id)?;
        let difference = loaded.as_deref() != Some(intent.revision_id.as_str());
        let mut issues = Vec::new();
        if difference && !target.loaded_difference_confirmed {
            issues.push(plc_catalog::Issue {
                code: "catalog_loaded_confirmation".into(),
                db_id: None,
                point_id: None,
            });
        }
        let document = match plc_catalog::build(
            &source.workspace,
            i,
            &app.configuration.store.profile_id,
            &intent.revision_id,
            &source.payload,
            &time,
            target,
        ) {
            Ok(doc) => Some(doc),
            Err(mut errors) => {
                issues.append(&mut errors);
                None
            }
        };
        let bytes = if issues.is_empty() {
            document
                .as_ref()
                .map(|d| serde_json::to_vec_pretty(d).expect("JSON value serializes"))
        } else {
            None
        };
        let sha = bytes.as_ref().map(|v| hash_bytes(v));
        let details = i.dbs.iter().map(|db| json!({"id":db.id,"name":db.name,"number":db.number,"length":db.length,"enabled":db.enabled,
            "points":db.points.iter().map(|p| json!({"id":p.id,"name":p.name,"displayName":p.display_name,
                "displayNames":p.display_names,"description":p.description,"dataType":p.data_type,"sourcePath":p.source_path,
                "byte":p.byte,"bit":p.bit,"enabled":p.enabled})).collect::<Vec<_>>() })).collect::<Vec<_>>();
        rows.push(json!({"instanceId":i.id,"name":i.name,"selectedRevision":selected,"loadedRevision":loaded,
            "loadedDiffers":difference,"loopback":target.host.parse::<std::net::Ipv4Addr>().is_ok_and(|v|v.is_loopback()),
            "localTsap":i.calling_tsap,"remoteTsap":i.called_tsap(),
            "nonDefaultTsap":i.calling_tsap != 0x100 || u64::from(i.called_tsap()) != 0x100 + u64::from(target.rack) * 32 + u64::from(target.slot),
            "dbCount":i.dbs.len(),"pointCount":i.dbs.iter().map(|d|d.points.len()).sum::<usize>(),
            "dbs":details,"document":document,"issues":issues,"byteCount":bytes.as_ref().map(Vec::len),"fileSha256":sha}));
        items.push(Item {
            id: i.id.clone(),
            bytes,
            sha,
            issues,
            selected,
            loaded,
        });
    }
    let token = uuid();
    let mut sessions = app.catalog_exports.lock().map_err(|_| "catalog_state")?;
    sessions.pending.retain(|_, p| p.expires > Instant::now());
    if sessions.pending.len() >= 8 {
        return Err("catalog_preview_capacity".into());
    }
    sessions.pending.insert(
        token.clone(),
        Pending {
            revision: intent.revision_id,
            payload_sha: source.revision.sha256.clone(),
            expires: Instant::now() + Duration::from_secs(300),
            items,
            directory: None,
        },
    );
    Ok(json!({"token":token,"revision":source.revision,"rows":rows}))
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
/// 只由原生选择器传入路径；IPC 不接收任何前端路径。
pub fn choose_directory(app: &App, token: &str, path: &Path) -> Result<Value, String> {
    let mut dir = directory(path)?;
    let mut sessions = app.catalog_exports.lock().map_err(|_| "catalog_state")?;
    let pending = sessions
        .pending
        .get_mut(token)
        .ok_or("catalog_preview_stale")?;
    if pending.expires <= Instant::now() {
        sessions.pending.remove(token);
        return Err("catalog_preview_stale".into());
    }
    if !directory_unchanged(&dir) {
        return Err("catalog_directory_changed".into());
    }
    let mut rows = Vec::new();
    for item in &pending.items {
        let name = format!("{}.json", item.id);
        let conflict = exists(&dir, &name)?;
        dir.conflicts.insert(item.id.clone(), conflict);
        rows.push(json!({"instanceId":item.id,"filename":name,"conflict":conflict,"valid":item.bytes.is_some()}));
    }
    pending.directory = Some(dir);
    Ok(json!({"rows":rows}))
}
pub fn cancel(app: &App, intent: TokenIntent) -> Result<Value, String> {
    app.catalog_exports
        .lock()
        .map_err(|_| "catalog_state")?
        .pending
        .remove(&intent.token);
    Ok(json!({"result":"cancelled","committed":false}))
}
#[cfg(unix)]
fn write_new(dir: &Directory, id: &str, bytes: &[u8]) -> Result<Option<String>, String> {
    use std::os::fd::FromRawFd;
    let tmp_name = format!(".ds003-{}.tmp", uuid());
    let tmp = std::ffi::CString::new(tmp_name.clone()).map_err(|_| "catalog_filename")?;
    let dest = std::ffi::CString::new(format!("{id}.json")).map_err(|_| "catalog_filename")?;
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
    use super::link_failure;
    #[test]
    fn exclusive_link_distinguishes_conflict_from_other_write_errors() {
        assert_eq!(link_failure(Some(libc::EEXIST)), "catalog_target_changed");
        assert_eq!(link_failure(Some(libc::EPERM)), "catalog_write");
        assert_eq!(link_failure(Some(libc::EIO)), "catalog_write");
        assert_eq!(link_failure(None), "catalog_write");
    }
}
#[cfg(not(unix))]
fn write_new(_dir: &Directory, _id: &str, _bytes: &[u8]) -> Result<Option<String>, String> {
    Err("catalog_platform_unsupported".into())
}
pub fn commit(app: &App, intent: TokenIntent) -> Result<Value, String> {
    let _guard = app.revision_control.lock().map_err(|_| "catalog_state")?;
    let pending = app
        .catalog_exports
        .lock()
        .map_err(|_| "catalog_state")?
        .pending
        .remove(&intent.token)
        .ok_or("catalog_preview_stale")?;
    if pending.expires <= Instant::now() {
        return Err("catalog_preview_stale".into());
    }
    let dir = pending.directory.ok_or("catalog_directory_required")?;
    let source = app
        .configuration
        .store
        .revision_snapshot(&pending.revision)?;
    if source.revision.sha256 != pending.payload_sha || !directory_unchanged(&dir) {
        return Err("catalog_preview_stale".into());
    }
    // 所有可能失败的版本状态读取必须先于第一份文件写入，避免中途失败掩盖已写入结果。
    let facts = pending
        .items
        .iter()
        .map(|item| instance_facts(app, &item.id))
        .collect::<Result<Vec<_>, _>>()?;
    let mut rows = Vec::new();
    for (item, (selected, loaded)) in pending.items.into_iter().zip(facts) {
        let outcome = if selected != item.selected || loaded != item.loaded {
            Err("catalog_version_state_changed".into())
        } else if item.bytes.is_none() {
            Err("catalog_validation".into())
        } else if dir.conflicts.get(&item.id) != Some(&false) {
            Err("catalog_target_exists".into())
        } else {
            write_new(&dir, &item.id, item.bytes.as_ref().unwrap())
        };
        let success = outcome.is_ok();
        let code = outcome.as_ref().err();
        rows.push(json!({"instanceId":item.id,"filename":format!("{}.json",item.id),"result":if success {"written"} else if code.is_some_and(|c|c == "catalog_write_result_unknown") {"unknown"} else {"failed"},"errorCode":code,"cleanupPending":outcome.ok().flatten(),"fileSha256":if success {item.sha} else {None},"issues":item.issues}));
    }
    let written = rows.iter().filter(|r| r["result"] == "written").count();
    let unknown = rows.iter().any(|r| r["result"] == "unknown");
    app.events.put(json!({"event":"catalog_export_completed","revision":pending.revision,"written":written,"unknown":unknown,"total":rows.len()}));
    Ok(json!({"rows":rows,"committed":if unknown {None} else {Some(written > 0)}}))
}
