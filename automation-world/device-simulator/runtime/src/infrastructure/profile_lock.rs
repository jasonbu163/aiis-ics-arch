//! 独立DS profile的路径、容量与跨进程锁；绝不删除或修复未知库。
use fs2::FileExt;
use std::{
    fs::{self, File, OpenOptions},
    os::unix::fs::OpenOptionsExt,
    path::{Path, PathBuf},
};

pub struct ProfileLock {
    file: File,
    pub directory: PathBuf,
    pub database: PathBuf,
}
pub fn reject_symlinks(path: &Path) -> Result<(), String> {
    if !path.is_absolute() {
        return Err("profile_absolute_required".into());
    }
    for p in path.ancestors() {
        match fs::symlink_metadata(p) {
            Ok(m) if m.file_type().is_symlink() => return Err("profile_symlink".into()),
            Ok(_) => {}
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {}
            Err(_) => return Err("profile_unavailable".into()),
        }
    }
    Ok(())
}
impl ProfileLock {
    pub fn acquire(profile: &Path) -> Result<Self, String> {
        reject_symlinks(profile)?;
        fs::create_dir_all(profile).map_err(|_| "profile_unavailable")?;
        let directory = profile.join("device-simulator-v1");
        reject_symlinks(&directory)?;
        if directory.exists() {
            let entries = fs::read_dir(&directory)
                .map_err(|_| "profile_unavailable")?
                .collect::<Result<Vec<_>, _>>()
                .map_err(|_| "profile_unavailable")?;
            for entry in &entries {
                let name = entry.file_name();
                if !["config.sqlite", "config.sqlite-journal", ".ds-profile.lock"]
                    .iter()
                    .any(|known| name == *known)
                {
                    return Err(
                        if name == "config.sqlite-wal" || name == "config.sqlite-shm" {
                            "storage_unexpected_wal"
                        } else {
                            "profile_directory_unknown"
                        }
                        .into(),
                    );
                }
            }
            if !entries.is_empty() && !directory.join("config.sqlite").exists() {
                return Err("storage_incomplete".into());
            }
        }
        fs::create_dir_all(&directory).map_err(|_| "profile_unavailable")?;
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .mode(0o600)
            .custom_flags(libc::O_NOFOLLOW)
            .open(directory.join(".ds-profile.lock"))
            .map_err(|_| "profile_lock_unavailable")?;
        file.try_lock_exclusive().map_err(|_| "profile_in_use")?;
        let database = directory.join("config.sqlite");
        reject_symlinks(&database)?;
        for suffix in ["-wal", "-shm"] {
            let path = directory.join(format!("config.sqlite{suffix}"));
            reject_symlinks(&path)?;
            if path.exists() {
                return Err("storage_unexpected_wal".into());
            }
        }
        Ok(Self {
            file,
            directory,
            database,
        })
    }
    pub fn check_capacity(&self, pending: usize) -> Result<(), String> {
        let mut bytes = 0u64;
        for name in ["config.sqlite", "config.sqlite-journal"] {
            let p = self.directory.join(name);
            reject_symlinks(&p)?;
            if p.exists() {
                bytes = bytes
                    .checked_add(fs::metadata(p).map_err(|_| "storage_unavailable")?.len())
                    .ok_or("storage_capacity")?;
            }
        }
        if bytes
            .saturating_mul(2)
            .saturating_add((pending as u64).saturating_mul(2))
            > 128 * 1024 * 1024
        {
            return Err("storage_capacity".into());
        }
        let available = fs2::available_space(&self.directory).map_err(|_| "storage_unavailable")?;
        // 非默认测试故障仅替换一次容量观测值；走同一真实保存前门，不填满主机卷。
        #[cfg(feature = "test-automation")]
        let available = if super::config_store::test_checkpoint("insufficient_space").is_err() {
            0
        } else {
            available
        };
        if available < 512 * 1024 * 1024 {
            return Err("storage_free_space".into());
        }
        Ok(())
    }
}
impl Drop for ProfileLock {
    fn drop(&mut self) {
        let _ = FileExt::unlock(&self.file);
    }
}
