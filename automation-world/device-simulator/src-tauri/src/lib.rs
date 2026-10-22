//! 原生薄壳：正常DS profile+16白名单IPC；dirty确认后走真实Window.close与有界shutdown。
mod app;
mod commands;
mod config;
#[cfg(feature = "test-automation")]
mod testing;
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc, Mutex,
};
use tauri::{Emitter, Listener, Manager};
pub fn run() {
    #[cfg(feature = "test-automation")]
    let test_manifest = match testing::native_driver::manifest() {
        Ok(value) => {
            std::env::set_var("DS_PROFILE_DIR", &value.profile_dir);
            value
        }
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2)
        }
    };
    tauri::Builder::default()
        .setup(move |host| {
            let default = host.path().app_local_data_dir()?;
            let mut bootstrap = config::bootstrap::load(&default).map_err(std::io::Error::other)?;
            let runtime = Arc::new(
                ds_runtime::app::App::open_desktop(std::path::Path::new(&bootstrap.profile_dir))
                    .map_err(std::io::Error::other)?,
            );
            let logs = ds_runtime::infrastructure::logging::start_sink(
                runtime.events.clone(),
                std::path::Path::new(&bootstrap.profile_dir),
            )
            .map_err(std::io::Error::other)?;
            let data_store = ds_runtime::config::profile::webview_store_id(
                &runtime.configuration.store.profile_id,
            )
            .map_err(std::io::Error::other)?;
            bootstrap.webview_store_id = runtime.configuration.store.profile_id.clone();
            let mut opened = ds_runtime::app::command_event("startup");
            opened["event"] = "profile_open".into();
            opened["webviewStoreId"] = bootstrap.webview_store_id.as_str().into();
            opened["configurationPath"] = runtime
                .configuration
                .store
                .path
                .display()
                .to_string()
                .into();
            runtime.events.put(opened);
            host.manage(app::Desktop {
                bootstrap,
                runtime,
                logs: Mutex::new(Some(logs)),
                close_approved: AtomicBool::new(false),
            });
            let window = host
                .config()
                .app
                .windows
                .first()
                .ok_or("DS main window configuration missing")?
                .clone();
            tauri::WebviewWindowBuilder::from_config(host, &window)?
                .data_store_identifier(data_store)
                .build()?;
            let handle = host.handle().clone();
            host.listen("ds-close-decision", move |event| {
                // 只接受正常关闭决定；不执行前端提供的JS/命令/路径。
                if event.payload() == "\"close\"" {
                    let state = handle.state::<app::Desktop>();
                    state.close_approved.store(true, Ordering::SeqCst);
                    native_event(&state.runtime, "desktop_close_confirmed");
                    if let Some(window) = handle.get_webview_window("main") {
                        let _ = window.close();
                    }
                }
            });
            #[cfg(feature = "test-automation")]
            testing::native_driver::install(host, test_manifest.clone())?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::runtime::ds_get_bootstrap,
            commands::runtime::ds_get_runtime_snapshot,
            commands::configuration::ds_get_configuration,
            commands::configuration::ds_save_configuration,
            commands::import::ds_preview_import,
            commands::import::ds_confirm_import,
            commands::import::ds_preview_layout,
            commands::import::ds_confirm_layout,
            commands::import::ds_preview_names,
            commands::import::ds_confirm_names,
            commands::configuration::ds_preview_apply,
            commands::configuration::ds_apply_revision,
            commands::runtime::ds_control_instance,
            commands::runtime::ds_write_point,
            commands::runtime::ds_close_connection,
            commands::queries::ds_query_logs,
            #[cfg(feature = "test-automation")]
            testing::native_driver::ds_test_report
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                let state = window.state::<app::Desktop>();
                native_event(&state.runtime, "desktop_window_close_requested");
                if !state.close_approved.load(Ordering::SeqCst) {
                    api.prevent_close();
                    let _ = window.emit("ds-close-request", ());
                }
            }
        })
        .build(tauri::generate_context!())
        .expect("DS native application")
        .run(|host, event| match event {
            tauri::RunEvent::ExitRequested { api, .. } => {
                let state = host.state::<app::Desktop>();
                native_event(&state.runtime, "desktop_exit_requested");
                if !state.close_approved.load(Ordering::SeqCst) {
                    api.prevent_exit();
                    let _ = host.emit("ds-close-request", ());
                } else if state.runtime.shutdown() {
                    native_event(&state.runtime, "desktop_shutdown_joined");
                } else {
                    api.prevent_exit();
                    native_event(&state.runtime, "desktop_shutdown_pending");
                }
            }
            tauri::RunEvent::Exit => {
                let state = host.state::<app::Desktop>();
                native_event(&state.runtime, "desktop_exit");
                state.stop_logs();
            }
            _ => {}
        });
}
fn native_event(runtime: &ds_runtime::app::App, name: &str) {
    let mut event = ds_runtime::app::command_event("native_exit");
    event["event"] = name.into();
    runtime.events.put(event);
}
