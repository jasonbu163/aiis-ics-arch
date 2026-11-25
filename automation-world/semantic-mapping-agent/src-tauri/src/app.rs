//! SMA 装配：本地配置、只读事实及经显式启动的 HTTP 映射。
use crate::commands::{
    acquisition, connection, file_export, http_mapping, local_configuration, mapping_runtime,
    runtimes,
};
use crate::services::{
    http_mapping::HttpMappingService, local_configuration::LocalConfigurationService,
    mapping_runtime as mapping_service,
};
use std::{
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
    time::Duration,
};
use tauri::webview::WebviewWindowBuilder;
pub fn run() {
    let allow_exit = Arc::new(AtomicBool::new(false));
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
            let configuration = LocalConfigurationService::new(database_path);
            app.manage(HttpMappingService::new(configuration.clone()));
            app.manage(configuration);
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
            acquisition::acquisition_options,
            acquisition::acquisition_latest,
            acquisition::acquisition_history,
            acquisition::acquisition_sample,
            acquisition::acquisition_forget_preview,
            local_configuration::load_local_configuration,
            local_configuration::change_local_configuration,
            local_configuration::preview_local_configuration,
            local_configuration::apply_local_configuration,
            local_configuration::export_local_configuration,
            local_configuration::preview_saved_local_mapping,
            http_mapping::sma_test_source,
            http_mapping::sma_latest_sources,
            http_mapping::sma_preview_mapping,
            http_mapping::sma_preview_target,
            http_mapping::sma_confirm_post,
            http_mapping::sma_cancel_post,
            http_mapping::sma_runtime_status,
            http_mapping::sma_start_runtime,
            http_mapping::sma_stop_runtime,
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
        .build(tauri::generate_context!())
        .expect("failed to build AIIS Semantic Mapping Agent")
        .run(move |app, event| {
            if let tauri::RunEvent::ExitRequested { api, code, .. } = event {
                if allow_exit.load(Ordering::Acquire) {
                    return;
                }
                let Some(runtime) = app.try_state::<HttpMappingService>() else {
                    return;
                };
                let first = runtime.begin_shutdown();
                if runtime.drained() {
                    return;
                }
                api.prevent_exit();
                if first {
                    let app = app.clone();
                    let runtime = runtime.inner().clone();
                    let allow_exit = allow_exit.clone();
                    tauri::async_runtime::spawn(async move {
                        let _ = tokio::time::timeout(Duration::from_secs(62), async {
                            while !runtime.drained() {
                                tokio::time::sleep(Duration::from_millis(25)).await;
                            }
                        })
                        .await;
                        // 传输最多 60 秒；超出关停上限时允许这次内部退出请求。
                        allow_exit.store(true, Ordering::Release);
                        app.exit(code.unwrap_or(0));
                    });
                }
            }
        });
}
use tauri::Manager;
