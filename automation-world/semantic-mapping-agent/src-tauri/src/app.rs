//! SMA composition root: retained HTTP mapping/Simulation only, no legacy SQL IPC.
use crate::commands::{connection, file_export, mapping_runtime, runtimes};
use crate::services::{mapping_runtime as mapping_service, simulation};
use tauri::webview::WebviewWindowBuilder;
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let guard = crate::infrastructure::logging::init(app.handle())?;
            app.manage(guard);
            let window = app
                .config()
                .app
                .windows
                .first()
                .expect("missing SMA window");
            WebviewWindowBuilder::from_config(app.handle(), window)?.build()?;
            Ok(())
        })
        .manage(simulation::state::CollectionFactSimulationRuntimeState::default())
        .manage(mapping_service::ApiFirstMappingRuntimeState::default())
        .invoke_handler(tauri::generate_handler![
            connection::load_app_defaults,
            connection::check_external_io,
            file_export::save_collection_fact_file,
            mapping_runtime::run_mapping_manual_once,
            mapping_runtime::load_runtime_startup_preferences,
            mapping_runtime::save_runtime_startup_preferences,
            runtimes::start_collection_fact_simulation_runtime,
            runtimes::pause_collection_fact_simulation_runtime,
            runtimes::resume_collection_fact_simulation_runtime,
            runtimes::stop_collection_fact_simulation_runtime,
            runtimes::get_collection_fact_simulation_runtime,
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
