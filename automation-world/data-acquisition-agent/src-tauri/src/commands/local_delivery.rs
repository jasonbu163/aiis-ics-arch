//! 投递具名IPC薄adapter；严格DTO、固定能力门禁，无任意URL/SQL/文件/人工ACK。
use super::local_acquisition::{LocalFailure, LocalState};
use crate::{
    domain::{
        local_configuration::{valid_id, LocalResult},
        sample_upload::{Binding, Settings},
    },
    services::local_supervisor::LocalEngine,
};
use serde::Deserialize;
use serde_json::Value;
use std::sync::Arc;
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Empty {}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Save {
    settings: Settings,
    expected_revision: String,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Control {
    action: String,
    #[serde(rename = "settingsRevision")]
    settings_revision: Option<String>,
    sources: Option<Vec<Binding>>,
    #[serde(rename = "sampleId")]
    sample_id: Option<String>,
    #[serde(rename = "oldUrl")]
    old_url: Option<String>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct List {
    cursor: Option<i64>,
    limit: Option<u32>,
    kind: Option<String>,
    state: Option<String>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct BatchId {
    batch_id: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct CycleId {
    cycle_id: String,
}

fn parse<T: serde::de::DeserializeOwned>(v: Value) -> LocalResult<T> {
    serde_json::from_value(v).map_err(|_| "invalid_request".into())
}
pub(crate) fn dispatch(
    engine: Arc<LocalEngine>,
    command: &str,
    request: Value,
) -> LocalResult<Value> {
    if serde_json::to_vec(&request)
        .map_err(|_| "invalid_request")?
        .len()
        > 64 * 1024
    {
        return Err("request_limits".into());
    }
    match command {
        "daa_get_delivery_settings" => {
            let _: Empty = parse(request)?;
            serde_json::to_value(engine.sample_upload_settings()?)
                .map_err(|_| "encoding_failed".into())
        }
        "daa_save_delivery_settings" => {
            let r: Save = parse(request)?;
            if !valid_id(&r.expected_revision) {
                return Err("invalid_request".into());
            }
            serde_json::to_value(
                engine.save_sample_upload_settings(r.settings, r.expected_revision)?,
            )
            .map_err(|_| "encoding_failed".into())
        }
        "daa_get_delivery_snapshot" => {
            let _: Empty = parse(request)?;
            engine.delivery_snapshot()
        }
        "daa_set_delivery" => {
            let control: Control = parse(request)?;
            if control.action == "rebind" {
                let sample = control.sample_id.ok_or("invalid_request")?;
                if !valid_id(&sample) {
                    return Err("invalid_request".into());
                }
                return engine.rebind_sample_upload(
                    sample,
                    control.old_url.ok_or("invalid_request")?,
                    control.settings_revision.ok_or("invalid_request")?,
                    control.sources.ok_or("invalid_request")?,
                );
            }
            if control.sample_id.is_some() || control.old_url.is_some() {
                return Err("invalid_request".into());
            }
            engine.set_delivery(&control.action, control.settings_revision, control.sources)
        }
        "daa_list_deliveries" => {
            let r: List = parse(request)?;
            if r.kind
                .as_deref()
                .map(|k| !["batches", "events"].contains(&k))
                .unwrap_or(false)
            {
                return Err("invalid_request".into());
            }
            engine.storage.call(true, move |s| {
                if r.kind.as_deref() == Some("events") {
                    s.delivery_events(r.cursor, r.limit.unwrap_or(20))
                } else if s.runtime_version()? == 4 {
                    s.list_sample_uploads(r.cursor, r.limit.unwrap_or(20), r.state.as_deref())
                } else {
                    s.list_deliveries(r.cursor, r.limit.unwrap_or(20))
                }
            })
        }
        "daa_get_delivery" => {
            let r: BatchId = parse(request)?;
            if !valid_id(&r.batch_id) {
                return Err("invalid_request".into());
            }
            engine.storage.call(true, move |s| {
                if s.runtime_version()? == 4 {
                    s.get_sample_upload(&r.batch_id)
                } else {
                    s.get_delivery(&r.batch_id)
                }
            })
        }
        "daa_preview_delivery" => {
            let r: CycleId = parse(request)?;
            if !valid_id(&r.cycle_id) {
                return Err("invalid_request".into());
            }
            Err("legacy_delivery_read_only".into())
        }
        "daa_test_facts_endpoint" => Err("legacy_delivery_read_only".into()),
        "daa_get_facts_source_material" => {
            let _: Empty = parse(request)?;
            if engine.delivery_available()? {
                engine.sample_upload_sources()
            } else {
                engine.storage.call(true, |s| s.facts_source_material())
            }
        }
        _ => Err("unknown_delivery_command".into()),
    }
}
macro_rules! command {
    ($name:ident) => {
        #[tauri::command]
        pub(crate) async fn $name(
            state: tauri::State<'_, LocalState>,
            request: Value,
        ) -> Result<Value, LocalFailure> {
            super::local_acquisition::invoke(state, stringify!($name), request).await
        }
    };
}
command!(daa_get_delivery_settings);
command!(daa_save_delivery_settings);
command!(daa_get_delivery_snapshot);
command!(daa_set_delivery);
command!(daa_preview_delivery);
command!(daa_test_facts_endpoint);
command!(daa_list_deliveries);
command!(daa_get_delivery);
command!(daa_get_facts_source_material);
