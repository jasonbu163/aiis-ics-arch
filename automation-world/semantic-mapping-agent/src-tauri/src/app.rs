//! SMA装配：本地配置、只读事实和手工采集回环；自动投递准入关闭，无legacy SQL IPC。
use crate::commands::{
    acquisition, connection, file_export, local_configuration, mapping_runtime, runtimes,
};
use crate::services::mapping_runtime as mapping_service;
use tauri::webview::WebviewWindowBuilder;
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(crate::services::acquisition::AcquisitionSession::default())
        .setup(|app| {
            // 显式非法profile必须在日志/startup任何路径解析前失败，防止旧Option接口回落默认目录。
            let profile = crate::config::configuration_profile(app.handle())
                .map_err(|code| std::io::Error::new(std::io::ErrorKind::InvalidInput, code))?;
            let defaults = crate::config::load_defaults_from_env();
            let guard = crate::infrastructure::logging::init(&profile, &defaults)?;
            app.manage(guard);
            let database_path = Ok(profile.database_path());
            app.manage(profile);
            app.manage(
                crate::services::local_configuration::LocalConfigurationService::new(database_path),
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
            acquisition::save_acquisition_loopback,
            acquisition::acquisition_options,
            acquisition::acquisition_latest,
            acquisition::acquisition_history,
            acquisition::acquisition_sample,
            acquisition::acquisition_preview,
            acquisition::acquisition_test_push,
            acquisition::acquisition_forget_preview,
            acquisition::acquisition_readback,
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
