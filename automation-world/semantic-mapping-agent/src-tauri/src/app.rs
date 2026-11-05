//! SMA装配：本地配置服务与只读事实；正常投递准入关闭，无legacy SQL IPC。
use crate::commands::{connection, file_export, local_configuration, mapping_runtime, runtimes};
use crate::services::mapping_runtime as mapping_service;
use tauri::webview::WebviewWindowBuilder;
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            // 显式非法profile必须在日志/startup任何路径解析前失败，防止旧Option接口回落默认目录。
            let profile = crate::config::configuration_profile(app.handle())
                .map_err(|code| std::io::Error::new(std::io::ErrorKind::InvalidInput, code))?;
            let guard = crate::infrastructure::logging::init(app.handle())?;
            app.manage(guard);
            let profile = Ok(profile.join("configuration.sqlite3"));
            app.manage(
                crate::services::local_configuration::LocalConfigurationService::new(profile),
            );
            let window = app
                .config()
                .app
                .windows
                .first()
                .expect("missing SMA window");
            WebviewWindowBuilder::from_config(app.handle(), window)?.build()?;
            Ok(())
        })
        .manage(mapping_service::ApiFirstMappingRuntimeState::default())
        .invoke_handler(tauri::generate_handler![
            local_configuration::load_local_configuration,
            local_configuration::change_local_configuration,
            local_configuration::preview_local_configuration,
            local_configuration::apply_local_configuration,
            local_configuration::export_local_configuration,
            local_configuration::preview_saved_local_mapping,
            connection::load_app_defaults,
            connection::check_external_io,
            file_export::save_collection_fact_file,
            mapping_runtime::run_mapping_manual_once,
            mapping_runtime::load_runtime_startup_preferences,
            mapping_runtime::save_runtime_startup_preferences,
            runtimes::start_api_first_mapping_runtime,
            runtimes::pause_api_first_mapping_runtime,
            runtimes::resume_api_first_mapping_runtime,
            runtimes::stop_api_first_mapping_runtime,
            runtimes::get_api_first_mapping_runtime,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run AIIS Semantic Mapping Agent");
}
use tauri::Manager;
