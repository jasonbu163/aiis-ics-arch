//! 正常产品路径：Tauri独立app_local_data_dir或显式绝对DS_PROFILE_DIR，无G0环境键。
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
    let explicit = std::env::var("DS_PROFILE_DIR").ok();
    let profile = ds_runtime::config::profile::resolve(default, explicit.as_deref())?;
    Ok(Bootstrap {
        product: "AIIS Device Simulator".into(),
        version: "0.1.0".into(),
        profile_dir: profile.display().to_string(),
        native_enabled: cfg!(feature = "native-s7"),
        schema_version: 1,
        webview_store_id: String::new(),
    })
}
