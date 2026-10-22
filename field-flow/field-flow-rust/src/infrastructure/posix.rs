//! 文件：src/infrastructure/posix.rs；实例锁、短临界区开始闸门与磁盘容量。
use crate::Result;
use std::{
    fs::{File, OpenOptions},
    io,
    os::{
        fd::{AsRawFd, RawFd},
        unix::fs::OpenOptionsExt,
    },
    path::{Path, PathBuf},
    time::{Duration, Instant},
};
pub struct InstanceLock(pub File);
impl InstanceLock {
    pub fn acquire(dir: &Path) -> Result<Self> {
        let f = OpenOptions::new()
            .read(true)
            .write(true)
            .custom_flags(libc::O_NOFOLLOW)
            .open(dir.join("instance.lock"))
            .map_err(|_| "state_lock")?;
        if unsafe { libc::flock(f.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } != 0 {
            return Err("state_in_use".into());
        }
        Ok(Self(f))
    }
}
pub struct Gate {
    file: File,
    pub path: PathBuf,
}
impl Gate {
    pub fn create(path: PathBuf) -> Result<Self> {
        let f = OpenOptions::new()
            .read(true)
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&path)
            .map_err(|_| "gate_create")?;
        f.set_len(1).map_err(|_| "gate_create")?;
        Ok(Self { file: f, path })
    }
    pub fn open(path: PathBuf) -> Result<Self> {
        Ok(Self {
            file: OpenOptions::new()
                .read(true)
                .write(true)
                .custom_flags(libc::O_NOFOLLOW)
                .open(&path)
                .map_err(|_| "gate_open")?,
            path,
        })
    }
    pub fn with<T>(&self, fun: impl FnOnce(bool) -> Result<T>) -> Result<T> {
        let start = Instant::now();
        loop {
            if unsafe { libc::flock(self.file.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } == 0 {
                break;
            }
            if start.elapsed() > Duration::from_millis(100) {
                return Err("gate_busy".into());
            }
            std::thread::sleep(Duration::from_millis(1));
        }
        let mut b = 0u8;
        let n = unsafe { libc::pread(self.file.as_raw_fd(), (&mut b as *mut u8).cast(), 1, 0) };
        let result = if n == 1 {
            fun(b != 0)
        } else {
            Err("gate_read".into())
        };
        unsafe { libc::flock(self.file.as_raw_fd(), libc::LOCK_UN) };
        result
    }
    pub fn close(&self) -> Result<()> {
        self.with(|_| {
            let b = 1u8;
            if unsafe { libc::pwrite(self.file.as_raw_fd(), (&b as *const u8).cast(), 1, 0) } != 1 {
                return Err("gate_write".into());
            }
            Ok(())
        })
    }
}
impl Drop for Gate {
    fn drop(&mut self) { /* path由实例退出后显式回收，不误删child仍使用的gate */
    }
}
pub fn disk_available(path: &Path) -> Result<u64> {
    use std::ffi::CString;
    use std::os::unix::ffi::OsStrExt;
    let c = CString::new(path.as_os_str().as_bytes()).map_err(|_| "state_path")?;
    let mut s = std::mem::MaybeUninit::<libc::statvfs>::uninit();
    if unsafe { libc::statvfs(c.as_ptr(), s.as_mut_ptr()) } != 0 {
        return Err("disk_stat".into());
    }
    let s = unsafe { s.assume_init() };
    Ok(s.f_bavail as u64 * s.f_frsize as u64)
}
pub fn socket_bounds(fd: RawFd) -> io::Result<()> {
    for option in [libc::SO_SNDBUF, libc::SO_RCVBUF] {
        let size: libc::c_int = 4096;
        let r = unsafe {
            libc::setsockopt(
                fd,
                libc::SOL_SOCKET,
                option,
                (&size as *const libc::c_int).cast(),
                std::mem::size_of_val(&size) as _,
            )
        };
        if r != 0 {
            return Err(io::Error::last_os_error());
        }
    }
    Ok(())
}
