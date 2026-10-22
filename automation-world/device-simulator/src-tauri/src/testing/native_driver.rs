//! 固定原生DOM场景观察器；test_report只接收已知step，不接受JS/SQL/命令。
use ds_runtime::testing::hooks::Manifest;
use serde::{Deserialize, Serialize};
use std::{
    sync::Mutex,
    time::{Duration, Instant},
};
use tauri::Manager;
const SCRIPT: &str = include_str!("../../../tests/ui/native_driver.js");

#[derive(Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Report {
    scenario: String,
    step: String,
    status: String,
    details: Vec<String>,
}
pub struct TestState {
    pub manifest: Manifest,
    reports: Mutex<Vec<Report>>,
}
pub fn manifest() -> Result<Manifest, String> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    match args.as_slice() {
        [flag, path] if flag == "--ds-test-manifest" => {
            let value = Manifest::read(std::path::Path::new(path))?;
            if value.scenario.is_none() || value.workspace.is_some() {
                return Err("native_manifest_scenario".into());
            }
            Ok(value)
        }
        _ => Err("test build requires --ds-test-manifest <owned path>".into()),
    }
}
fn steps(scenario: &str) -> &'static [&'static str] {
    match scenario {
        "N1" => &[
            "ready",
            "ui_preferences",
            "instance_created",
            "import_cancelled",
            "import_confirmed",
            "layout_names_confirmed",
            "manual_point_confirmed",
            "policies_saved",
            "applied",
            "second_instance",
            "dirty_save_ready",
            "close_ready",
        ],
        "N2" => &[
            "ready",
            "reopened_stopped",
            "listener_started",
            "ordinary_write",
            "maintenance_write",
            "rules_observed",
            "selection_isolated",
            "snapshot_stale_ready",
            "snapshot_stale_observed",
            "snapshot_recovered",
            "close_ready",
        ],
        "N3" => &[
            "ready",
            "reopened_initial",
            "listener_started",
            "connection_closed",
            "dirty_cancel_ready",
            "dirty_cancelled",
            "close_ready",
        ],
        _ => &[],
    }
}
#[tauri::command]
pub fn ds_test_report(
    state: tauri::State<'_, TestState>,
    desktop: tauri::State<'_, crate::app::Desktop>,
    report: Report,
) -> Result<(), String> {
    let mut reports = state.reports.lock().map_err(|_| "test_report_lock")?;
    if report.scenario != state.manifest.scenario.as_deref().unwrap_or("")
        || report.details.len() > 20
        || report.details.iter().any(|s| s.len() > 1024)
        || reports.len() >= 64
        || !matches!(report.status.as_str(), "pass" | "fail")
    {
        return Err("test_report_bounds".into());
    }
    if report.status == "pass"
        && steps(&report.scenario).get(reports.len()) != Some(&report.step.as_str())
    {
        return Err("test_report_sequence".into());
    }
    if report.status == "fail" && report.step != "failed" {
        return Err("test_report_step".into());
    }
    let mut event = ds_runtime::services::queries::value(&report)?;
    event["event"] = "native_dom_step".into();
    event["sourceCandidate"] = state.manifest.source_candidate.as_str().into();
    desktop.runtime.events.put(event);
    reports.push(report);
    Ok(())
}
// 仅test-automation的macOS资源归属SPI；固定只读getter，不导出selector/控制入口。
// WebKit WKWebViewPrivate.h/WKWebView.mm；非公开稳定API，运行时不支持则明确unknown。
#[cfg(target_os = "macos")]
fn observe_webview_processes(window: &tauri::WebviewWindow, handle: &tauri::AppHandle) {
    let handle = handle.clone();
    let _ = window.with_webview(move |webview| {
        use std::ffi::{c_char, c_void};
        #[link(name = "objc")]
        extern "C" {
            fn sel_registerName(name: *const c_char) -> *mut c_void;
            fn objc_msgSend();
        }
        // Tauri schedules this closure on the main thread; the borrowed WKWebView
        // pointer and getter calls never escape this closure or alter process state.
        let object = webview.inner();
        let read_pid = |name: &'static [u8]| -> Option<i32> {
            if object.is_null() {
                return None;
            }
            unsafe {
                let selector = sel_registerName(name.as_ptr().cast());
                let responds = sel_registerName(b"respondsToSelector:\0".as_ptr().cast());
                let supported: unsafe extern "C" fn(*mut c_void, *mut c_void, *mut c_void) -> i8 =
                    std::mem::transmute(objc_msgSend as unsafe extern "C" fn());
                if supported(object, responds, selector) == 0 {
                    return None;
                }
                let get: unsafe extern "C" fn(*mut c_void, *mut c_void) -> i32 =
                    std::mem::transmute(objc_msgSend as unsafe extern "C" fn());
                Some(get(object, selector))
            }
        };
        let web = read_pid(b"_webProcessIdentifier\0");
        let gpu = read_pid(b"_gpuProcessIdentifier\0");
        let desktop = handle.state::<crate::app::Desktop>();
        let state = handle.state::<TestState>();
        #[derive(Serialize)]
        #[serde(rename_all = "camelCase")]
        struct ProcessObservation<'a> {
            event: &'a str,
            source_candidate: &'a str,
            web_process_id: Option<i32>,
            gpu_process_id: Option<i32>,
            web_selector_supported: bool,
            gpu_selector_supported: bool,
            attribution: &'a str,
            support_scope: &'a str,
        }
        if let Ok(event) = ds_runtime::services::queries::value(&ProcessObservation {
            event: "native_webview_processes",
            source_candidate: &state.manifest.source_candidate,
            web_process_id: web,
            gpu_process_id: gpu,
            web_selector_supported: web.is_some(),
            gpu_selector_supported: gpu.is_some(),
            attribution: "current real WKWebView fixed read-only Private SPI; main-thread borrow",
            support_scope:
                "test-only macOS respondsToSelector; not a public API or product dependency",
        }) {
            desktop.runtime.events.put(event);
        }
    });
}

pub fn install(
    host: &mut tauri::App,
    manifest: Manifest,
) -> Result<(), Box<dyn std::error::Error>> {
    if host.config().identifier != "com.aiis.aw.devicesimulator.validation" {
        return Err("test identity must be validation".into());
    }
    let scenario = manifest.scenario.clone().ok_or("test scenario missing")?;
    let payload = ds_runtime::testing::hooks::encode(&scenario)?;
    host.manage(TestState {
        manifest,
        reports: Mutex::new(vec![]),
    });
    let handle = host.handle().clone();
    std::thread::Builder::new()
        .name("ds-native-dom-driver".into())
        .spawn(move || {
            let Some(window) = handle.get_webview_window("main") else {
                return;
            };
            let _ = window.set_size(tauri::LogicalSize::new(960.0, 640.0));
            std::thread::sleep(Duration::from_millis(500));
            if let Err(error) =
                window.eval(format!("window.__DS_TEST_SCENARIO__={payload};\n{SCRIPT}"))
            {
                let state = handle.state::<crate::app::Desktop>();
                let mut event = ds_runtime::app::command_event("native_driver");
                event["event"] = "native_driver_eval_failed".into();
                event["error"] = error.to_string().into();
                state.runtime.events.put(event);
                return;
            }
            let deadline = Instant::now() + Duration::from_secs(240);
            let mut cancel_requested = false;
            let mut next_process_observation = Instant::now();
            while Instant::now() < deadline {
                #[cfg(target_os = "macos")]
                if Instant::now() >= next_process_observation {
                    next_process_observation = Instant::now() + Duration::from_secs(1);
                    observe_webview_processes(&window, &handle);
                }
                let state = handle.state::<TestState>();
                let reports = state.reports.lock().unwrap();
                if reports.iter().any(|r| r.status == "fail") {
                    return;
                }
                let cancel = reports.iter().any(|r| r.step == "dirty_cancel_ready");
                let close = reports.iter().any(|r| r.step == "close_ready");
                drop(reports);
                if cancel && !cancel_requested {
                    cancel_requested = true;
                    let _ = window.close();
                }
                if close {
                    let _ = window.close();
                    return;
                }
                std::thread::sleep(Duration::from_millis(10));
            }
            let state = handle.state::<crate::app::Desktop>();
            let mut event = ds_runtime::app::command_event("native_driver");
            event["event"] = "native_driver_timeout".into();
            state.runtime.events.put(event);
        })?;
    Ok(())
}
