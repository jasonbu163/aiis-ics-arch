//! 实际文件/rollback journal空间与保守页预算；不直接打开数据库文件，不删pending或journal。
use super::{sql_error, Stores};
use crate::domain::{local_configuration::LocalResult, local_runtime::Capacity};
use std::path::Path;
pub(crate) const MAX_CYCLE: u64 = 512 * 1024;
pub(crate) fn bytes(p: &Path) -> u64 {
    std::fs::metadata(p).map(|m| m.len()).unwrap_or(0)
}
pub(crate) fn log_bytes(dir: &Path) -> u64 {
    std::fs::read_dir(dir)
        .ok()
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .map(|e| bytes(&e.path()))
        .sum()
}
pub(crate) fn admit(c: &Capacity, quota: u64, recovering: bool) -> bool {
    if c.state == "unexpected_wal_material" {
        return false;
    }
    let used = c.main_bytes + c.journal_bytes;
    let water = if recovering { 70 } else { 90 };
    used < quota * water / 100
        && used.saturating_add(c.reserved_bytes) < quota * 90 / 100
        && c.free_bytes
            > 512 * 1024 * 1024
                + c.reserved_bytes
                + 2 * (c.config_bytes + c.config_journal_bytes)
                + 96 * 1024 * 1024
        && c.config_bytes + c.config_journal_bytes < 64 * 1024 * 1024
        && c.log_bytes <= 32 * 1024 * 1024
}
impl Stores {
    // Maintenance journals old pages too. Re-read physical/free-space facts at every write boundary;
    // retain the same conservative old-image, four-round and maintenance/system reserves as acquisition.
    pub(super) fn admit_maintenance(&self, quota: u64) -> LocalResult<()> {
        let current = self.capacity(quota)?;
        if admit(&current, quota, false) {
            Ok(())
        } else {
            Err("capacity_paused".into())
        }
    }
    pub fn capacity(&self, quota: u64) -> LocalResult<Capacity> {
        let p = self.dir.join("runtime.sqlite");
        let a = self.dir.join("config.sqlite");
        let page_count = self
            .runtime
            .query_row("PRAGMA page_count", [], |r| r.get::<_, u64>(0))
            .map_err(sql_error)?;
        let freelist_count = self
            .runtime
            .query_row("PRAGMA freelist_count", [], |r| r.get::<_, u64>(0))
            .map_err(sql_error)?;
        let mut sector = 65536u64;
        unsafe {
            let mut file: *mut rusqlite::ffi::sqlite3_file = std::ptr::null_mut();
            let result = rusqlite::ffi::sqlite3_file_control(
                self.runtime.handle(),
                b"main\0".as_ptr().cast(),
                rusqlite::ffi::SQLITE_FCNTL_FILE_POINTER,
                (&mut file as *mut *mut rusqlite::ffi::sqlite3_file).cast(),
            );
            if result == 0 && !file.is_null() && !(*file).pMethods.is_null() {
                if let Some(f) = (*(*file).pMethods).xSectorSize {
                    let s = f(file);
                    if s > 0 && s <= 65536 {
                        sector = s as u64;
                    }
                }
            }
        }
        let mut c = Capacity {
            main_bytes: bytes(&p),
            journal_bytes: bytes(&self.dir.join("runtime.sqlite-journal")),
            config_bytes: bytes(&a),
            config_journal_bytes: bytes(&self.dir.join("config.sqlite-journal")),
            log_bytes: log_bytes(&self.dir.join("logs")),
            free_bytes: fs2::available_space(&self.dir).map_err(|_| "space_meter_failed")?,
            quota_bytes: quota,
            page_count,
            freelist_count,
            busy_count: self.busy_count,
            ..Default::default()
        };
        #[cfg(test)]
        if let Some((free, main)) = &self.test_meter {
            c.free_bytes = free.load(std::sync::atomic::Ordering::SeqCst);
            c.main_bytes = main.load(std::sync::atomic::Ordering::SeqCst);
        }
        // Each old page is journaled at most once; allow one sector header per page plus record overhead.
        // Four maximum encoded cycles reserve 16x bytes for B-trees/index pages, plus 32MiB maintenance.
        c.reserved_bytes = page_count.saturating_mul(4096 + 8 + sector)
            + sector
            + 4 * MAX_CYCLE * 16
            + 32 * 1024 * 1024;
        if self.delivery_available()? {
            c.reserved_bytes = c.reserved_bytes.saturating_add(32 * 1024 * 1024);
            (
                c.delivery_request_bytes,
                c.delivery_receipt_bytes,
                c.delivery_metadata_bytes,
            ) = self.delivery_bytes()?;
        }
        // 辅助文件allocated计入runtime物理quota；256KiB子预算已经包含在原额外32MiB中。
        let (aux_logical, aux_allocated) = auxiliary_bytes(&self.dir)?;
        c.main_bytes = c.main_bytes.saturating_add(aux_allocated);
        if self.delivery_available()? {
            c.reserved_bytes = c.reserved_bytes.saturating_sub(aux_allocated);
        }
        c.delivery_metadata_bytes = c.delivery_metadata_bytes.saturating_add(aux_logical);
        c.pending_count = self
            .runtime
            .query_row(
                "SELECT count(*) FROM sample_delivery WHERE state='pending'",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        c.pending_bytes=self.runtime.query_row("SELECT coalesce(sum(samples.payload_bytes),0) FROM samples JOIN sample_delivery ON sample_delivery.sample_id=samples.id WHERE sample_delivery.state='pending'",[],|r|r.get(0)).map_err(sql_error)?;
        c.oldest_pending=self.runtime.query_row("SELECT min(samples.saved_at) FROM samples JOIN sample_delivery ON sample_delivery.sample_id=samples.id WHERE sample_delivery.state='pending'",[],|r|r.get(0)).map_err(sql_error)?;
        for base in [&p, &a] {
            for suffix in ["-wal", "-shm"] {
                let n = bytes(&std::path::PathBuf::from(format!(
                    "{}{suffix}",
                    base.display()
                )));
                if std::path::PathBuf::from(format!("{}{suffix}", base.display())).exists() {
                    c.journal_bytes += n;
                    c.state = "unexpected_wal_material".into();
                    c.admission = false;
                    return Ok(c);
                }
            }
        }
        c.admission = admit(&c, quota, false);
        c.state = if !c.admission {
            "capacity_paused"
        } else if c.main_bytes + c.journal_bytes >= quota * 80 / 100 {
            "warning"
        } else {
            "ready"
        }
        .into();
        Ok(c)
    }
}

use super::profile_contract::{Snapshot, AUX_BUDGET, CREDENTIAL, SENTINEL, STAGING};
#[cfg(unix)]
use std::os::unix::fs::MetadataExt;
/// 只用metadata计辅助文件；同inode安装双名字不重复算allocated，逻辑量仍逐名字计。
pub(super) fn auxiliary_bytes(dir: &Path) -> LocalResult<(u64, u64)> {
    let (mut logical, mut allocated) = (0, 0);
    let mut seen = std::collections::BTreeSet::new();
    for name in [CREDENTIAL, SENTINEL, STAGING] {
        let path = dir.join(name);
        let m = match std::fs::symlink_metadata(&path) {
            Ok(m) => m,
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => continue,
            Err(_) => return Err("profile_contract_invalid".into()),
        };
        if !m.is_file()
            || m.file_type().is_symlink()
            || m.len() > if name == SENTINEL { 8192 } else { 32768 }
        {
            return Err("profile_contract_invalid".into());
        }
        logical += m.len();
        let st = super::profile_contract::stat(&m);
        #[cfg(unix)]
        let blocks = m.blocks() * 512;
        #[cfg(not(unix))]
        let blocks = m.len();
        if seen.insert((st.identity.dev, st.identity.ino)) {
            allocated += blocks;
        }
    }
    if logical > 73728 || allocated > AUX_BUDGET {
        return Err("profile_initialization_capacity".into());
    }
    Ok((logical, allocated))
}
pub(super) fn physical_budget(s: &Snapshot) -> LocalResult<()> {
    // 256KiB辅助分配是32MiB ACK预留中的子预算。旧页另预留，不挪用普通90%门禁阻塞恢复。
    let pages = s
        .files
        .iter()
        .filter(|m| m.name.ends_with(".sqlite"))
        .map(|m| m.stat.len.div_ceil(4096))
        .sum::<u64>();
    let old = pages.saturating_mul(4096 + 8 + 65536) + 65536;
    let config = s
        .files
        .iter()
        .filter(|m| m.name.starts_with("config.sqlite"))
        .map(|m| m.stat.len)
        .sum::<u64>();
    let (_, allocated) = auxiliary_bytes(&s.store)?;
    let need = 512 * 1024 * 1024 + old + 96 * 1024 * 1024 - allocated
        + 96 * 1024 * 1024
        + config.saturating_mul(2);
    let free = fs2::available_space(s.store.parent().ok_or("profile_contract_invalid")?)
        .map_err(|_| "profile_space_meter")?;
    #[cfg(all(test, unix))]
    let free = super::profile_contract_tests::available_space(free);
    if free <= need {
        return Err("profile_initialization_capacity".into());
    }
    auxiliary_bytes(&s.store)?;
    Ok(())
}
