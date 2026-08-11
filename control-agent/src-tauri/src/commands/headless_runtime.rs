//! File Path: /control-agent/src-tauri/src/commands/headless_runtime.rs
//! Description: Standalone headless runtime command adapter
//! Main Features:
//!   - Runs the long-lived stdin/stdout JSON Lines command loop
//!   - Delegates all PLC lifecycle work to the shared collection supervisor
//!   - Provides EOF, shutdown and signal cleanup without starting Tauri

use std::io::{self, BufRead, Write};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{self, Receiver, Sender};
use std::thread;
use std::time::Duration;

use serde::Serialize;
use serde_json::{json, Value};

use crate::config::AgentConfig;
use crate::domain::headless_runtime::{HeadlessRuntimeRequest, HeadlessRuntimeResponse};
use crate::infrastructure::logging::{emit_startup_event, init_logging};
use crate::services::plc_collection;
use crate::services::plc_diagnostics;

enum HeadlessInput {
    Line(String),
    Eof,
}

static SHUTDOWN_SIGNAL_RECEIVED: AtomicBool = AtomicBool::new(false);

struct HeadlessDispatchResult {
    accepted: bool,
    status: String,
    payload: Value,
    error: Option<String>,
}

trait HeadlessRuntimeExecutor {
    fn dispatch(&self, action: &str, target: &str) -> HeadlessDispatchResult;
}

struct ProductionRuntimeExecutor;

fn serialize_payload<T: Serialize>(value: &T) -> Value {
    serde_json::to_value(value).unwrap_or_else(|_| {
        json!({
            "status": "failed",
            "message": "serialize_failed"
        })
    })
}

fn control_dispatch_result(
    result: crate::domain::plc_collection::PlcCollectionControlResult,
) -> HeadlessDispatchResult {
    let accepted = result.accepted;
    let status = result.status.clone();
    let error = (!accepted).then(|| result.message.clone());

    HeadlessDispatchResult {
        accepted,
        status,
        payload: serialize_payload(&result),
        error,
    }
}

impl HeadlessRuntimeExecutor for ProductionRuntimeExecutor {
    fn dispatch(&self, action: &str, target: &str) -> HeadlessDispatchResult {
        match action {
            "start" | "start_read" => {
                let result = match target {
                    "all" => plc_collection::start_plc_read_from_console(),
                    plc_key => {
                        plc_collection::start_plc_read_for_plc_from_console(plc_key.to_string())
                    }
                };
                control_dispatch_result(result)
            }
            "stop" | "stop_read" => {
                let result = match target {
                    "all" => plc_collection::stop_plc_read_from_console(),
                    plc_key => {
                        plc_collection::stop_plc_read_for_plc_from_console(plc_key.to_string())
                    }
                };
                control_dispatch_result(result)
            }
            "enable_persistence" => {
                let result = match target {
                    "all" => plc_collection::enable_plc_persistence_from_console(),
                    plc_key => plc_collection::enable_plc_persistence_for_plc_from_console(
                        plc_key.to_string(),
                    ),
                };
                control_dispatch_result(result)
            }
            "pause_persistence" => {
                let result = match target {
                    "all" => plc_collection::pause_plc_persistence_from_console(),
                    plc_key => plc_collection::pause_plc_persistence_for_plc_from_console(
                        plc_key.to_string(),
                    ),
                };
                control_dispatch_result(result)
            }
            "start_collection" => {
                let result = match target {
                    "all" => plc_collection::start_plc_collection_from_console(),
                    plc_key => plc_collection::start_plc_collection_for_plc_from_console(
                        plc_key.to_string(),
                    ),
                };
                control_dispatch_result(result)
            }
            "stop_collection" => {
                let result = match target {
                    "all" => plc_collection::stop_plc_collection_from_console(),
                    plc_key => plc_collection::stop_plc_collection_for_plc_from_console(
                        plc_key.to_string(),
                    ),
                };
                control_dispatch_result(result)
            }
            "sample" => {
                let result =
                    plc_diagnostics::read_plc_samples_once_for_plc_from_console(target.to_string());
                let status = if result.succeeded {
                    "succeeded"
                } else {
                    "failed"
                };
                let error =
                    (!result.error_message.is_empty()).then(|| result.error_message.clone());

                HeadlessDispatchResult {
                    accepted: true,
                    status: status.to_string(),
                    payload: serialize_payload(&result),
                    error,
                }
            }
            "status" => {
                let snapshot = plc_collection::read_plc_collection_status(&AgentConfig::load());

                HeadlessDispatchResult {
                    accepted: true,
                    status: snapshot.runtime_status.clone(),
                    payload: serialize_payload(&snapshot),
                    error: None,
                }
            }
            "shutdown" => {
                let result = plc_collection::stop_plc_read_from_console();
                let accepted = result.status != "failed";
                let status = result.status.clone();
                let error = (!accepted).then(|| result.message.clone());

                HeadlessDispatchResult {
                    accepted,
                    status,
                    payload: serialize_payload(&result),
                    error,
                }
            }
            _ => unreachable!("headless action must be validated before dispatch"),
        }
    }
}

pub(crate) fn run() -> i32 {
    let config = AgentConfig::load();
    let _logging_guards = init_logging(&config);
    emit_startup_event(&config);
    crate::autostart_plc_collection_loop_from_env();

    let (sender, receiver) = mpsc::channel();
    spawn_stdin_reader(sender.clone());
    install_signal_handler();

    tracing::info!(
        event = "plc_headless_runtime_started",
        process = "aiis-ics-control-agent-runtime",
        result = "accepted",
    );

    run_command_loop(receiver)
}

fn spawn_stdin_reader(sender: Sender<HeadlessInput>) {
    let spawn_result = thread::Builder::new()
        .name("plc-headless-stdin".to_string())
        .spawn(move || {
            let stdin = io::stdin();
            for line in stdin.lock().lines() {
                match line {
                    Ok(line) => {
                        if sender.send(HeadlessInput::Line(line)).is_err() {
                            return;
                        }
                    }
                    Err(error) => {
                        tracing::error!(
                            event = "plc_headless_stdin_failed",
                            error = %error,
                            result = "failed",
                        );
                        let _ = sender.send(HeadlessInput::Eof);
                        return;
                    }
                }
            }

            let _ = sender.send(HeadlessInput::Eof);
        });

    if let Err(error) = spawn_result {
        tracing::error!(
            event = "plc_headless_stdin_thread_failed",
            error = %error,
            result = "failed",
        );
    }
}

fn install_signal_handler() {
    #[cfg(unix)]
    unsafe {
        libc::signal(libc::SIGINT, handle_shutdown_signal as libc::sighandler_t);
        libc::signal(libc::SIGTERM, handle_shutdown_signal as libc::sighandler_t);
    }

    #[cfg(not(unix))]
    tracing::info!(
        event = "plc_headless_signal_handler_unavailable",
        result = "stdin_shutdown_available",
    );
}

fn run_command_loop(receiver: Receiver<HeadlessInput>) -> i32 {
    loop {
        if SHUTDOWN_SIGNAL_RECEIVED.swap(false, Ordering::SeqCst) {
            stop_all_for_shutdown("signal");
            return 0;
        }

        let input = match receiver.recv_timeout(Duration::from_millis(250)) {
            Ok(input) => input,
            Err(mpsc::RecvTimeoutError::Timeout) => continue,
            Err(mpsc::RecvTimeoutError::Disconnected) => {
                stop_all_for_shutdown("command_channel_closed");
                return 0;
            }
        };

        match input {
            HeadlessInput::Line(line) => {
                let (response, should_exit) = handle_line(&line);
                write_response(&response);
                if should_exit {
                    return 0;
                }
            }
            HeadlessInput::Eof => {
                write_shutdown_response("stdin_eof");
                return 0;
            }
        }
    }
}

#[cfg(unix)]
extern "C" fn handle_shutdown_signal(_signal: libc::c_int) {
    SHUTDOWN_SIGNAL_RECEIVED.store(true, Ordering::SeqCst);
}

fn handle_line(line: &str) -> (HeadlessRuntimeResponse, bool) {
    handle_line_with_executor(line, &ProductionRuntimeExecutor)
}

fn handle_line_with_executor<E: HeadlessRuntimeExecutor>(
    line: &str,
    executor: &E,
) -> (HeadlessRuntimeResponse, bool) {
    if line.trim().is_empty() {
        return (
            HeadlessRuntimeResponse::rejected(
                String::new(),
                "invalid".to_string(),
                "all".to_string(),
                "request must not be empty".to_string(),
            ),
            false,
        );
    }

    let request = match serde_json::from_str::<HeadlessRuntimeRequest>(line) {
        Ok(request) => request,
        Err(error) => {
            return (
                HeadlessRuntimeResponse::rejected(
                    String::new(),
                    "invalid".to_string(),
                    "all".to_string(),
                    format!("invalid JSON request: {error}"),
                ),
                false,
            )
        }
    };

    if request.request_id.trim().is_empty() {
        return (
            HeadlessRuntimeResponse::rejected(
                request.request_id,
                request.action,
                request.target.unwrap_or_else(|| "all".to_string()),
                "request_id must not be empty".to_string(),
            ),
            false,
        );
    }

    let action = request.action.trim().to_string();
    let target = request.target.clone().unwrap_or_else(|| "all".to_string());

    match action.as_str() {
        "start" | "stop" | "start_read" | "stop_read" | "enable_persistence"
        | "pause_persistence" | "start_collection" | "stop_collection" => {}
        "sample" => {
            if target == "all" {
                return (
                    HeadlessRuntimeResponse::rejected(
                        request.request_id,
                        action,
                        target,
                        "sample requires one plc_key target".to_string(),
                    ),
                    false,
                );
            }

            if let Err(error) = plc_collection::validate_plc_key(&target) {
                return (
                    HeadlessRuntimeResponse::rejected(request.request_id, action, target, error),
                    false,
                );
            }
        }
        "status" => {
            if target != "all" {
                return (
                    HeadlessRuntimeResponse::rejected(
                        request.request_id,
                        action,
                        target,
                        "status only accepts target=all or an omitted target".to_string(),
                    ),
                    false,
                );
            }
        }
        "shutdown" => {
            if target != "all" {
                return (
                    HeadlessRuntimeResponse::rejected(
                        request.request_id,
                        action,
                        target,
                        "shutdown only accepts target=all or an omitted target".to_string(),
                    ),
                    false,
                );
            }
        }
        _ => {
            return (
                HeadlessRuntimeResponse::rejected(
                    request.request_id,
                    action,
                    target,
                    "unknown action; expected start_read, stop_read, enable_persistence, pause_persistence, start_collection, stop_collection, sample, status or shutdown".to_string(),
                ),
                false,
            );
        }
    }

    let result = executor.dispatch(&action, &target);
    let should_exit = action == "shutdown";
    (
        HeadlessRuntimeResponse::result(
            request.request_id,
            action,
            target,
            result.accepted,
            result.status,
            result.payload,
            result.error,
        ),
        should_exit,
    )
}

fn write_response(response: &HeadlessRuntimeResponse) {
    let line = serde_json::to_string(response).unwrap_or_else(|_| {
        "{\"event\":\"ca_runtime_command_result\",\"accepted\":false,\"status\":\"failed\",\"error\":\"serialize_failed\"}".to_string()
    });
    println!("{line}");
    let _ = io::stdout().flush();
}

fn write_shutdown_response(reason: &str) {
    let result = plc_collection::stop_plc_read_from_console();
    tracing::info!(
        event = "plc_headless_runtime_shutdown",
        reason,
        status = %result.status,
        affected_plc_keys = ?result.affected_plc_keys,
        result = "complete",
    );

    let accepted = result.status != "failed";
    let status = result.status.clone();
    let error = (!accepted).then(|| result.message.clone());
    let payload = serde_json::to_value(&result).unwrap_or_else(|_| {
        json!({
            "status": "failed",
            "message": "serialize_failed"
        })
    });
    let response = HeadlessRuntimeResponse::result(
        String::new(),
        "shutdown".to_string(),
        "all".to_string(),
        accepted,
        status,
        payload,
        error,
    );
    write_response(&response);
}

fn stop_all_for_shutdown(reason: &str) {
    let result = plc_collection::stop_plc_read_from_console();
    tracing::info!(
        event = "plc_headless_runtime_shutdown",
        reason,
        status = %result.status,
        affected_plc_keys = ?result.affected_plc_keys,
        result = "complete",
    );
}

#[cfg(test)]
mod tests {
    use std::collections::HashSet;
    use std::sync::Mutex;

    use serde_json::json;

    use super::{
        handle_line, handle_line_with_executor, HeadlessDispatchResult, HeadlessRuntimeExecutor,
    };

    #[derive(Default)]
    struct RecordingExecutor {
        calls: Mutex<Vec<String>>,
        started: Mutex<HashSet<String>>,
        stopped: Mutex<HashSet<String>>,
    }

    impl RecordingExecutor {
        fn calls(&self) -> Vec<String> {
            self.calls.lock().unwrap().clone()
        }
    }

    impl HeadlessRuntimeExecutor for RecordingExecutor {
        fn dispatch(&self, action: &str, target: &str) -> HeadlessDispatchResult {
            self.calls
                .lock()
                .unwrap()
                .push(format!("{action}:{target}"));

            let (accepted, status) = match action {
                "start" | "start_read" | "start_collection" => {
                    let accepted = self.started.lock().unwrap().insert(target.to_string());
                    (
                        accepted,
                        if accepted {
                            "started"
                        } else {
                            "already_running"
                        },
                    )
                }
                "stop" | "stop_read" | "stop_collection" => {
                    let accepted = self.stopped.lock().unwrap().insert(target.to_string());
                    (accepted, if accepted { "stopped" } else { "not_running" })
                }
                "enable_persistence" => (true, "enabled"),
                "pause_persistence" => (true, "paused"),
                "status" => (true, "all_good"),
                "shutdown" => (true, "stopped"),
                "sample" => (true, "succeeded"),
                _ => unreachable!("test executor receives validated actions only"),
            };

            HeadlessDispatchResult {
                accepted,
                status: status.to_string(),
                payload: json!({"action": action, "target": target}),
                error: (!accepted).then(|| status.to_string()),
            }
        }
    }

    #[test]
    fn malformed_json_is_rejected_without_exit() {
        let (response, should_exit) = handle_line("not-json");

        assert!(!response.accepted);
        assert_eq!(response.status, "rejected");
        assert!(!should_exit);
    }

    #[test]
    fn unknown_action_is_rejected_without_dispatch() {
        let executor = RecordingExecutor::default();
        let (response, should_exit) = handle_line_with_executor(
            r#"{"request_id":"unknown","action":"restart","target":"all"}"#,
            &executor,
        );

        assert!(!response.accepted);
        assert!(response.error.unwrap().contains("unknown action"));
        assert!(!should_exit);
        assert!(executor.calls().is_empty());
    }

    #[test]
    fn all_and_targeted_control_dispatch_use_requested_targets() {
        let executor = RecordingExecutor::default();
        let (all_response, all_exit) = handle_line_with_executor(
            r#"{"request_id":"start-all","action":"start","target":"all"}"#,
            &executor,
        );
        let (target_response, target_exit) = handle_line_with_executor(
            r#"{"request_id":"stop-one","action":"stop","target":"PLC_1"}"#,
            &executor,
        );

        assert!(all_response.accepted);
        assert_eq!(all_response.status, "started");
        assert!(!all_exit);
        assert!(target_response.accepted);
        assert_eq!(target_response.status, "stopped");
        assert!(!target_exit);
        assert_eq!(executor.calls(), vec!["start:all", "stop:PLC_1"]);
    }

    #[test]
    fn duplicate_start_and_stop_dispatch_return_idempotent_statuses() {
        let executor = RecordingExecutor::default();
        let (first_start, _) = handle_line_with_executor(
            r#"{"request_id":"start-1","action":"start","target":"PLC_1"}"#,
            &executor,
        );
        let (second_start, _) = handle_line_with_executor(
            r#"{"request_id":"start-2","action":"start","target":"PLC_1"}"#,
            &executor,
        );
        let (first_stop, _) = handle_line_with_executor(
            r#"{"request_id":"stop-1","action":"stop","target":"PLC_1"}"#,
            &executor,
        );
        let (second_stop, _) = handle_line_with_executor(
            r#"{"request_id":"stop-2","action":"stop","target":"PLC_1"}"#,
            &executor,
        );

        assert!(first_start.accepted);
        assert_eq!(second_start.status, "already_running");
        assert!(!second_start.accepted);
        assert!(first_stop.accepted);
        assert_eq!(second_stop.status, "not_running");
        assert!(!second_stop.accepted);
    }

    #[test]
    fn status_defaults_to_all_and_shutdown_dispatch_exits() {
        let executor = RecordingExecutor::default();
        let (status_response, status_exit) =
            handle_line_with_executor(r#"{"request_id":"status","action":"status"}"#, &executor);
        let (shutdown_response, shutdown_exit) = handle_line_with_executor(
            r#"{"request_id":"shutdown","action":"shutdown"}"#,
            &executor,
        );

        assert!(status_response.accepted);
        assert_eq!(status_response.target, "all");
        assert!(!status_exit);
        assert!(shutdown_response.accepted);
        assert!(shutdown_exit);
        assert_eq!(executor.calls(), vec!["status:all", "shutdown:all"]);
    }

    #[test]
    fn default_gates_block_unknown_plc_without_starting_a_worker() {
        let (response, should_exit) = handle_line(
            r#"{"request_id":"unknown-plc","action":"start","target":"PLC_DOES_NOT_EXIST"}"#,
        );

        assert!(!response.accepted);
        assert_eq!(response.status, "blocked");
        assert!(response.error.unwrap().contains("blocked_by_runtime_gates"));
        assert!(!should_exit);
    }

    #[test]
    fn sample_requires_a_single_plc_target() {
        let (response, should_exit) =
            handle_line(r#"{"request_id":"sample-all","action":"sample","target":"all"}"#);

        assert!(!response.accepted);
        assert!(response.error.unwrap().contains("one plc_key"));
        assert!(!should_exit);
    }

    #[test]
    fn shutdown_rejects_non_all_target() {
        let (response, should_exit) =
            handle_line(r#"{"request_id":"shutdown-one","action":"shutdown","target":"PLC_1"}"#);

        assert!(!response.accepted);
        assert!(response.error.unwrap().contains("target=all"));
        assert!(!should_exit);
    }

    #[test]
    fn new_read_and_persistence_actions_accept_all_or_targeted_plc() {
        let executor = RecordingExecutor::default();
        let (read_response, _) = handle_line_with_executor(
            r#"{"request_id":"read","action":"start_read","target":"PLC_1"}"#,
            &executor,
        );
        let (write_response, _) = handle_line_with_executor(
            r#"{"request_id":"write","action":"enable_persistence","target":"PLC_1"}"#,
            &executor,
        );
        let (pause_response, _) = handle_line_with_executor(
            r#"{"request_id":"pause","action":"pause_persistence","target":"all"}"#,
            &executor,
        );

        assert!(read_response.accepted);
        assert!(write_response.accepted);
        assert!(pause_response.accepted);
        assert_eq!(
            executor.calls(),
            vec![
                "start_read:PLC_1",
                "enable_persistence:PLC_1",
                "pause_persistence:all"
            ]
        );
    }
}
