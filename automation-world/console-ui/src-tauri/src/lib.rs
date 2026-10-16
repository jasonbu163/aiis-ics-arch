//! Console UI 最薄桌面壳：创建窗口及事件循环，无业务命令、配置或外部连接。
use tauri::Manager;

pub fn run() {
    tracing_subscriber::fmt().json().with_target(false).init();
    tracing::info!(
        event = "cu_process_start",
        process = "aiis-aw-console-ui",
        result = "starting"
    );
    let app = tauri::Builder::default()
        .setup(|app| {
            let window = app.get_webview_window("main").expect("main window must exist");
            tracing::info!(event = "cu_window_created", window = "main", title = %window.title()?, result = "ready");
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building AIIS AW Console UI");
    app.run(|_, event| {
        if matches!(event, tauri::RunEvent::Ready) {
            tracing::info!(
                event = "cu_event_loop_ready",
                process = "aiis-aw-console-ui",
                result = "ready"
            );
        }
    });
}
