//! 正常产品profile解析：只读可选DS覆盖；默认路径由同一Tauri app_local_data_dir调用提供。
use std::path::{Path, PathBuf};
pub fn resolve(default: &Path, explicit: Option<&str>) -> Result<PathBuf, String> {
    let path = explicit
        .map(PathBuf::from)
        .unwrap_or_else(|| default.to_path_buf());
    if !path.is_absolute()
        || path
            .components()
            .any(|c| matches!(c, std::path::Component::ParentDir))
    {
        return Err("profile_absolute_required".into());
    }
    crate::infrastructure::profile_lock::reject_symlinks(&path)?;
    Ok(path)
}

pub fn webview_store_id(profile_id: &str) -> Result<[u8; 16], String> {
    let id = uuid::Uuid::parse_str(profile_id).map_err(|_| "profile_identity")?;
    if id.is_nil() {
        return Err("profile_identity".into());
    }
    Ok(*id.as_bytes())
}
