//! 正常IPC用例边界：版本复核、查询分页、控制/写入意图；不在Vue或Tauri命令里实现业务。
use crate::{
    app::App, config::workspace::*, domain::configuration::validate,
    services::configuration::SaveIntent,
};
use serde::Serialize;
use serde_json::{json, Value};
use std::sync::atomic::Ordering;
pub fn value<T: Serialize>(data: T) -> Result<Value, String> {
    serde_json::to_value(data).map_err(|_| "response_format".into())
}
pub fn mutation(app: &App, operation: &str) -> Result<(), String> {
    uuid::Uuid::parse_str(operation).map_err(|_| "operation_identity")?;
    if !app.accepting.load(Ordering::SeqCst) {
        return Err("application_closing".into());
    }
    Ok(())
}
pub fn configuration(app: &App, query: ConfigurationQuery) -> Result<Value, String> {
    let state = app.configuration.get()?;
    let workspace = match query.revision_id {
        Some(id) => app.configuration.store.revision(&id)?,
        None => state.workspace,
    };
    let issues = workspace
        .instances
        .iter()
        .flat_map(|i| crate::domain::layout::compile(i).err().unwrap_or_default())
        .collect::<Vec<_>>();
    Ok(
        json!({"etag":state.etag,"workspace":workspace,"latestRevision":state.latest_revision,"revisions":app.configuration.store.revisions(query.revision_offset)?,"selections":app.configuration.store.selections()?,"issues":issues}),
    )
}
pub fn snapshot(app: &App, query: SnapshotQuery) -> Result<Value, String> {
    if query.limit == 0 || query.limit > 100 {
        return Err("page_limit".into());
    }
    let mut snapshot = app.snapshot();
    if let Some(error) = snapshot.get("errorCode").and_then(Value::as_str) {
        return Err(error.to_owned());
    }
    if let Some(id) = query.instance_id {
        snapshot["values"] = app
            .instance(&id)?
            .context
            .owner
            .values(query.offset as usize, query.limit as usize);
    }
    Ok(snapshot)
}
pub fn save(app: &App, intent: SaveIntent) -> Result<Value, String> {
    validate(&intent.workspace)?;
    let (expected, candidate) = app.configuration.prepare(intent)?;
    let removed = app
        .instances
        .lock()
        .unwrap()
        .iter()
        .filter(|(id, _)| !candidate.instances.iter().any(|i| i.id == **id))
        .map(|(id, i)| (id.clone(), i.clone()))
        .collect::<Vec<_>>();
    // 只锁已stopped的删除目标控制序列，阻止保存期间start；stop始终绕过此锁。
    let controls = removed
        .iter()
        .map(|(_, i)| i.control.lock().unwrap())
        .collect::<Vec<_>>();
    if removed.iter().any(|(_, i)| !i.stopped()) {
        return Err("instance_delete_stop_required".into());
    }
    let saved = app.configuration.store.save(&expected, candidate.clone());
    let committed = match &saved {
        Ok(_) => true,
        Err(e) if e.contains("unknown") => {
            // 查询真实草稿后才按已发生的删除收尾，绝不把未知事务虚报为rollback。
            match app.configuration.get() {
                Ok(actual) => actual.workspace == candidate,
                Err(_) => false,
            }
        }
        Err(_) => false,
    };
    if saved
        .as_ref()
        .is_err_and(|e| matches!(e.as_str(), "save_receipt_unknown" | "save_commit_unknown"))
        && !committed
    {
        for (id, _) in &removed {
            app.load_errors
                .lock()
                .unwrap()
                .insert(id.clone(), "configuration_receipt_unknown".into());
        }
    }
    if committed {
        for (id, instance) in &removed {
            if instance.finish_shutdown() {
                app.instances.lock().unwrap().remove(id);
                app.load_errors.lock().unwrap().remove(id);
            } else {
                app.load_errors
                    .lock()
                    .unwrap()
                    .insert(id.clone(), "delete_cleanup_pending".into());
            }
        }
    }
    drop(controls);
    let mut result = value(saved?)?;
    result["cleanupPending"] = json!(removed
        .iter()
        .filter(|(id, _)| app.load_errors.lock().unwrap().contains_key(id))
        .map(|(id, _)| id.clone())
        .collect::<Vec<_>>());
    Ok(result)
}

fn version(
    instance: &crate::services::lifecycle::Instance,
    revision: &str,
    epoch: &str,
) -> Result<(), String> {
    if instance.context.owner.loaded_revision() != revision
        || instance.context.owner.epoch_revision().0 != u64_value(epoch)?
    {
        return Err("loaded_revision_or_epoch_conflict".into());
    }
    Ok(())
}
pub fn control(app: &App, intent: ControlIntent) -> Result<Value, String> {
    let instance = app.instance(&intent.instance_id)?;
    if intent.command == "stop" {
        // stop封准入和generation变更不排在apply/SQL控制序列后；已提交selected若安装失效按load_failed记录。
        version(&instance, &intent.expected_loaded_revision, &intent.epoch)?;
        if !instance.stop() {
            return Err("stop_pending".into());
        }
        return Ok(json!({"result":"completed","instance":instance.snapshot()}));
    }
    let _control = instance.control.lock().unwrap();
    version(&instance, &intent.expected_loaded_revision, &intent.epoch)?;
    if intent.command == "start"
        && app
            .load_errors
            .lock()
            .unwrap()
            .contains_key(&intent.instance_id)
    {
        return Err("instance_load_failed".into());
    }
    let ok = match intent.command.as_str() {
        "start" => instance.start(),
        "stop" => instance.stop(),
        "pause" | "resume" => instance.context.owner.control(&intent.command, 0),
        "reset" => {
            if !intent.discard_values {
                return Err("reset_confirmation_required".into());
            }
            instance.stopped() && instance.context.owner.control("reset", 0)
        }
        _ => return Err("control_command".into()),
    };
    if !ok {
        return Err(if intent.command == "stop" {
            "stop_pending"
        } else {
            "control_rejected"
        }
        .into());
    }
    Ok(json!({"result":"completed","instance":instance.snapshot()}))
}
pub fn write(app: &App, intent: WriteIntent) -> Result<Value, String> {
    let instance = app.instance(&intent.instance_id)?;
    let _control = instance.control.lock().unwrap();
    let maintenance = matches!(intent.source, WriteKind::Maintenance);
    if maintenance && !intent.confirmed {
        return Err("maintenance_confirmation_required".into());
    }
    if app
        .load_errors
        .lock()
        .unwrap()
        .contains_key(&intent.instance_id)
    {
        return Err("instance_load_failed".into());
    }
    let result = instance.context.owner.write_point(
        &intent.point_id,
        &intent.value,
        &intent.expected_loaded_revision,
        u64_value(&intent.epoch)?,
        u64_value(&intent.point_seq)?,
        maintenance,
    )?;
    Ok(
        json!({"result":"written","seq":result.seq.to_string(),"maintenance":maintenance,"clientMayOverwrite":maintenance}),
    )
}
pub fn close_connection(app: &App, intent: CloseIntent) -> Result<Value, String> {
    if !intent.confirmed {
        return Err("connection_close_confirmation_required".into());
    }
    let instance = app.instance(&intent.instance_id)?;
    let _control = instance.control.lock().unwrap();
    version(&instance, &intent.expected_loaded_revision, &intent.epoch)?;
    if !instance.close(u64_value(&intent.connection_id)?) {
        return Err("connection_close_pending".into());
    }
    Ok(json!({"result":"closing","connectionId":intent.connection_id}))
}
pub fn logs(app: &App, query: LogsQuery) -> Result<Value, String> {
    if query.limit == 0 || query.limit > 100 || query.event.as_ref().is_some_and(|e| e.len() > 100)
    {
        return Err("page_limit".into());
    }
    let mut data = app.events.query(
        query.offset as usize,
        query.limit as usize,
        query.event.as_deref(),
    );
    data["configurationPath"] = json!(app.configuration.store.path);
    data["storageBytes"] = json!(std::fs::metadata(&app.configuration.store.path)
        .map(|m| m.len())
        .ok()
        .map(|n| n.to_string()));
    Ok(data)
}
