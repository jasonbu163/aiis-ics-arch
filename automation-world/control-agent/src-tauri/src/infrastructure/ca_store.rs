//! Atomic persistence and user-selected file I/O for the new CA namespace.
use crate::domain::ca_flow::MAX_JSON;
use serde::{de::DeserializeOwned, Serialize};
use std::{
    fs,
    fs::OpenOptions,
    io::{Read, Write},
    path::Path,
};
use uuid::Uuid;

pub(crate) fn read_bytes(path: &Path, limit: usize) -> Result<Vec<u8>, String> {
    let file = fs::File::open(path).map_err(|_| "file_open")?;
    if !file.metadata().map_err(|_| "file_open")?.is_file() {
        return Err("file_open".into());
    }
    let mut bytes = Vec::new();
    file.take(limit as u64 + 1)
        .read_to_end(&mut bytes)
        .map_err(|_| "file_read")?;
    if bytes.len() > limit {
        return Err("file_too_large".into());
    }
    Ok(bytes)
}
pub(crate) fn load<T: Default + DeserializeOwned>(path: &Path) -> Result<T, String> {
    if !path.try_exists().map_err(|_| "store_read")? {
        return Ok(T::default());
    }
    serde_json::from_slice(&read_bytes(path, 32 * MAX_JSON)?).map_err(|_| "store_invalid".into())
}
pub(crate) fn save<T: Serialize>(path: &Path, value: &T) -> Result<(), String> {
    let bytes = serde_json::to_vec(value).map_err(|_| "store_encode")?;
    if bytes.len() > 32 * MAX_JSON {
        return Err("store_capacity".into());
    }
    let parent = path.parent().ok_or("store_path_invalid")?;
    fs::create_dir_all(parent).map_err(|_| "store_directory")?;
    atomic(path, &bytes, true)
}
pub(crate) fn atomic(path: &Path, bytes: &[u8], replace: bool) -> Result<(), String> {
    let dir = path.parent().ok_or("file_path")?;
    let tmp = dir.join(format!(".ca-{}.tmp", Uuid::new_v4()));
    let mut opts = OpenOptions::new();
    opts.create_new(true).write(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        opts.mode(0o600);
    }
    let mut f = opts.open(&tmp).map_err(|_| "file_write")?;
    let result = (|| {
        f.write_all(bytes)
            .and_then(|_| f.sync_all())
            .map_err(|_| "file_write")?;
        drop(f);
        if replace {
            fs::rename(&tmp, path).map_err(|_| "file_commit")?;
        } else {
            // A link is an atomic, no-replace publication in the chosen directory.
            fs::hard_link(&tmp, path).map_err(|e| {
                if e.kind() == std::io::ErrorKind::AlreadyExists {
                    "file_exists"
                } else {
                    "file_commit"
                }
            })?;
        }
        Ok(())
    })();
    let _ = fs::remove_file(&tmp);
    result
}
