//! 非默认debug JSON Lines验证adapter，与原生IPC调用同一service；没有ACK/SQL/外部transport入口。
use crate::{config::local_bootstrap, services::local_recovery};
use serde_json::{json, Value};
use std::io::{BufRead, Write};
pub(crate) fn run(mut args: Vec<String>) -> i32 {
    if args.is_empty() {
        println!("DAA local validation (debug fixture only): --env-file <absolute> --profile-dir <absolute owned tmp> --fixture-file <absolute>");
        return 0;
    }
    args.insert(0, "--daa-local-validation".into());
    let result = local_bootstrap::load(args).and_then(local_recovery::open);
    let engine = match result {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{}", json!({"errorCode":e}));
            return 2;
        }
    };
    for line in std::io::stdin().lock().lines() {
        let result = (|| {
            let line = line.map_err(|_| "input_io")?;
            if line.len() > 16 * 1024 * 1024 {
                return Err("request_limits".to_string());
            }
            let v: Value = serde_json::from_str(&line).map_err(|_| "invalid_request")?;
            let command = v["command"].as_str().ok_or("invalid_request")?;
            if command == "shutdown" {
                return Ok(json!({"shutdown":true}));
            }
            super::local_acquisition::dispatch(
                engine.clone(),
                command,
                v.get("request").cloned().unwrap_or(json!({})),
            )
        })();
        let shutdown = result
            .as_ref()
            .ok()
            .map(|v| v["shutdown"] == true)
            .unwrap_or(false);
        let response = match result {
            Ok(v) => json!({"event":"validation_response","result":v}),
            Err(e) => {
                let f = super::local_acquisition::failure(&engine, e);
                json!({"event":"validation_response","errorCode":f.error_code,"currentEtag":f.current_etag,"currentActiveRevision":f.current_active_revision})
            }
        };
        println!("{response}");
        let _ = std::io::stdout().flush();
        if shutdown {
            break;
        }
    }
    engine.shutdown();
    0
}
