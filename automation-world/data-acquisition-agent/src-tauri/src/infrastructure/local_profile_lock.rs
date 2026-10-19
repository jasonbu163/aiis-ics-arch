//! profile级独占OS锁：新旧模式/GUI/headless共用，不宣称跨profile或跨主机设备排他。
use crate::domain::local_configuration::LocalResult;
use fs2::FileExt;
use std::{
    fs::{File, OpenOptions},
    path::{Path, PathBuf},
};
pub(crate) struct ProfileLock {
    _file: File,
    pub profile: PathBuf,
}
impl ProfileLock {
    pub fn acquire(profile: &Path) -> LocalResult<Self> {
        if !profile.is_absolute() {
            return Err("profile_absolute_required".into());
        }
        if profile.is_symlink() {
            return Err("profile_symlink".into());
        }
        std::fs::create_dir_all(profile).map_err(|_| "profile_io")?;
        let path = profile.join(".daa-runtime.lock");
        if path.is_symlink() {
            return Err("profile_symlink".into());
        }
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(&path)
            .map_err(|_| "profile_io")?;
        file.try_lock_exclusive().map_err(|_| "profile_locked")?;
        Ok(Self {
            _file: file,
            profile: profile.to_path_buf(),
        })
    }
}
