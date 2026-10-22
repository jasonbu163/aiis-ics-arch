//! 停机换版：有界typed快照→锁外构建→控制代次复核→SQL selected CAS→同owner安装。
use crate::{
    app::App,
    domain::{
        configuration::*,
        image::{store_point, Image},
        layout::{self, CompiledInstance},
        request::Source,
        typed_value,
    },
    services::{configuration::Preview, owner::Captured},
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::sync::Arc;
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ApplyIntent {
    pub expected_etag: String,
    pub instance_id: String,
    pub revision_id: String,
    pub retention: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ApplyConfirmation {
    pub expected_etag: String,
    pub instance_id: String,
    pub token: String,
    pub candidate_sha256: String,
    pub impact_sha256: String,
}
pub struct Plan {
    pub image: Image,
    pub simulated_ns: u64,
    pub rows: Vec<Value>,
}
fn shape(db: &layout::CompiledDb) -> String {
    digest(&(
        db.number,
        db.length,
        db.points
            .iter()
            .map(|p| (&p.config.id, &p.config.data_type, p.byte, p.bit))
            .collect::<Vec<_>>(),
    ))
}
fn semantics(p: &layout::CompiledPoint) -> String {
    let e = &p.policy;
    digest(&(
        p.config.enabled,
        e.mode,
        e.owner,
        e.client_read,
        e.client_write,
        e.ui_write,
        e.ui_maintenance,
    ))
}
pub fn plan(
    config: &CompiledInstance,
    revision: &str,
    old: Option<&Captured>,
    initialize: bool,
) -> Result<Plan, String> {
    let mut image = Image::new(
        config,
        old.map_or(1, |o| o.epoch + 1),
        1,
        revision.into(),
        Source::Initialize,
    );
    let mut reset_rules = initialize || old.is_none();
    let mut changed_dbs = std::collections::BTreeSet::new();
    if let Some(old) = old {
        for (number, db) in &config.dbs {
            if old
                .config
                .dbs
                .get(number)
                .is_none_or(|p| p.id != db.id || shape(p) != shape(db))
            {
                changed_dbs.insert(*number);
                reset_rules = true
            }
        }
        if old.config.dbs.keys().any(|n| !config.dbs.contains_key(n)) {
            reset_rules = true
        }
        for db in config.dbs.values() {
            for p in &db.points {
                if let Some((old_number, old_index)) = old.config.point_index.get(&p.config.id) {
                    let before = &old.config.dbs[old_number].points[*old_index];
                    if before.initial != p.initial
                        || semantics(before) != semantics(p)
                        || before.policy.rule != p.policy.rule
                    {
                        reset_rules = true
                    }
                }
            }
        }
    }
    let mut rows = vec![];
    for (number, db) in &config.dbs {
        for p in &db.points {
            let previous = old.and_then(|o| {
                o.config
                    .point_index
                    .get(&p.config.id)
                    .map(|(n, index)| (&o.config.dbs[n].points[*index], o))
            });
            let compatible = previous.is_some_and(|(before, _)| {
                before.initial == p.initial
                    && semantics(before) == semantics(p)
                    && before.config.data_type == p.config.data_type
            });
            let preserve = !initialize
                && !changed_dbs.contains(number)
                && compatible
                && (!reset_rules || p.policy.mode == Mode::Hold);
            if preserve {
                let (_, old) = previous.unwrap();
                let value = old
                    .values
                    .get(&p.config.id)
                    .ok_or("preserve_value_missing")?;
                let bytes = typed_value::encode(&p.config.data_type, value)
                    .map_err(|_| "preserve_encode_failed")?;
                store_point(&mut image.dbs.get_mut(number).unwrap().bytes, p, &bytes);
            }
            rows.push(json!({"pointId":p.config.id,"dbId":db.id,"action":if preserve{"preserve"}else{"initialize"},"reason":if initialize{"initialize_all"}else if changed_dbs.contains(number){"db_structure"}else if !compatible{"point_semantics"}else if reset_rules && p.policy.mode!=Mode::Hold{"rule_clock_reset"}else{"compatible"}}));
        }
    }
    if let Some(old) = old {
        for id in old
            .config
            .point_index
            .keys()
            .filter(|id| !config.point_index.contains_key(*id))
        {
            rows.push(json!({"pointId":id,"action":"remove"}));
        }
    }
    Ok(Plan {
        image,
        simulated_ns: if reset_rules {
            0
        } else {
            old.map_or(0, |o| o.simulated_ns)
        },
        rows,
    })
}
fn snapshot_key(old: Option<&Captured>) -> Value {
    old.map(|o|json!({"epoch":o.epoch.to_string(),"seq":o.seq.to_string(),"generation":o.generation.to_string(),"simulatedNs":o.simulated_ns.to_string(),"valuesSha256":digest(&o.values),"loadedRevision":o.loaded_revision})).unwrap_or(Value::Null)
}
pub fn preview(app: &App, intent: ApplyIntent) -> Result<Preview, String> {
    if !["preserve_compatible_hold", "initialize_all"].contains(&intent.retention.as_str()) {
        return Err("retention_mode".into());
    }
    let workspace = app.configuration.store.revision(&intent.revision_id)?;
    let config = workspace
        .instances
        .iter()
        .find(|i| i.id == intent.instance_id)
        .ok_or("instance_not_found")?;
    let compiled = layout::compile(config).map_err(|issues| {
        format!(
            "configuration_blocked:{}",
            serde_json::to_string(&issues).unwrap()
        )
    })?;
    let allocated = app
        .instances
        .lock()
        .unwrap()
        .values()
        .map(|i| i.context.owner.compiled().allocation_upper)
        .sum::<usize>();
    if allocated
        .saturating_add(compiled.allocation_upper)
        .saturating_add(288 * 1024 * 1024)
        > 512 * 1024 * 1024
    {
        return Err("runtime_capacity".into());
    }
    let selected = app
        .configuration
        .store
        .selections()?
        .into_iter()
        .find(|s| s.instance_id == intent.instance_id);
    let rollback = if let Some(s) = &selected {
        app.configuration.store.revision_seq(&intent.revision_id)?
            < app.configuration.store.revision_seq(&s.revision_id)?
    } else {
        false
    };
    let old = match app.instance(&intent.instance_id) {
        Ok(i) => {
            if !i.stopped() {
                return Err("instance_not_stopped".into());
            }
            Some(i.context.owner.capture()?)
        }
        Err(_) => None,
    };
    let initialize = intent.retention == "initialize_all" || rollback;
    let built = plan(&compiled, &intent.revision_id, old.as_ref(), initialize)?;
    let key = snapshot_key(old.as_ref());
    let impact = digest(&(&built.rows, &key, &intent.revision_id, initialize));
    app.configuration.preview("apply",&intent.expected_etag,workspace,json!({"instanceId":intent.instance_id,"revisionId":intent.revision_id,"retention":intent.retention,"initializeAll":initialize,"rollback":rollback,"expectedSelectionEtag":selected.map(|s|s.selection_etag),"snapshot":key,"impactSha256":impact,"rows":built.rows,"ruleTimeNs":built.simulated_ns.to_string()}))
}
pub fn confirm(app: &App, intent: ApplyConfirmation) -> Result<Value, String> {
    let (workspace, details) = app.configuration.pending_candidate(
        "apply",
        &intent.token,
        &intent.expected_etag,
        &intent.candidate_sha256,
    )?;
    if details["instanceId"] != intent.instance_id
        || details["impactSha256"] != intent.impact_sha256
    {
        return Err("apply_confirmation".into());
    }
    if app.configuration.get()?.etag != intent.expected_etag {
        return Err("apply_preview_stale".into());
    }
    let revision = details["revisionId"].as_str().ok_or("apply_confirmation")?;
    let config = workspace
        .instances
        .iter()
        .find(|i| i.id == intent.instance_id)
        .ok_or("instance_not_found")?
        .clone();
    let compiled = Arc::new(layout::compile(&config).map_err(|_| "configuration_blocked")?);
    let existing = app.instance(&intent.instance_id).ok();
    let _control = existing.as_ref().map(|i| i.control.lock().unwrap());
    let old = match &existing {
        Some(i) => {
            if !i.stopped() {
                return Err("instance_not_stopped".into());
            }
            Some(i.context.owner.capture()?)
        }
        None => None,
    };
    if snapshot_key(old.as_ref()) != details["snapshot"] {
        return Err("apply_snapshot_stale".into());
    }
    let selected = app
        .configuration
        .store
        .selections()?
        .into_iter()
        .find(|s| s.instance_id == intent.instance_id);
    if selected.as_ref().is_some_and(|s| s.revision_id == revision)
        && old.as_ref().is_some_and(|o| {
            o.loaded_revision == revision && digest(&o.config.config) == digest(&config)
        })
    {
        app.configuration.finish_preview(&intent.token);
        return Ok(json!({"result":"already_loaded","committed":false,"receiptState":"known"}));
    }
    let built = plan(
        &compiled,
        revision,
        old.as_ref(),
        details["initializeAll"]
            .as_bool()
            .ok_or("apply_confirmation")?,
    )?;
    let expected = details["expectedSelectionEtag"].as_str().map(str::to_owned);
    if selected.as_ref().map(|s| s.selection_etag.clone()) != expected {
        return Err("selection_conflict".into());
    }
    let selection_changed = !selected.as_ref().is_some_and(|s| s.revision_id == revision);
    if selection_changed {
        if let Err(error) = app
            .configuration
            .store
            .select(&intent.instance_id, revision, expected)
        {
            if matches!(
                error.as_str(),
                "selection_receipt_unknown" | "selection_commit_unknown"
            ) {
                app.load_errors
                    .lock()
                    .unwrap()
                    .insert(intent.instance_id.clone(), "selection_unknown".into());
            }
            return Err(error);
        }
    }
    #[cfg(feature = "test-automation")]
    let install_fault = app.configuration.store.test_checkpoint("before_install");
    #[cfg(not(feature = "test-automation"))]
    let install_fault: Result<(), String> = Ok(());
    let installed = if let Err(error) = install_fault {
        Err(error)
    } else if let Some(existing) = &existing {
        let result = existing.context.owner.install(
            old.as_ref().unwrap(),
            compiled,
            built.image,
            built.simulated_ns,
        );
        if result.is_ok() {
            existing.refresh_limits();
        }
        result
    } else {
        match app.create_loaded(config, revision) {
            Ok(instance) => {
                app.instances
                    .lock()
                    .unwrap()
                    .insert(intent.instance_id.clone(), instance);
                Ok(())
            }
            Err(e) => Err(e),
        }
    };
    if let Err(error) = installed {
        app.load_errors
            .lock()
            .unwrap()
            .insert(intent.instance_id.clone(), "load_failed".into());
        app.events
            .put(json!({"event":"load_failed","instance":intent.instance_id,"error":error}));
        return Err(format!(
            "{}:{}",
            if selection_changed {
                "load_failed_after_selection_commit"
            } else {
                "load_failed"
            },
            json!({"selectedRevision":revision,"instanceId":intent.instance_id,"state":"load_failed","oldImageDiagnosticOnly":true})
        ));
    }
    app.load_errors.lock().unwrap().remove(&intent.instance_id);
    app.configuration.finish_preview(&intent.token);
    app.events
        .put(json!({"event":"apply_installed","instance":intent.instance_id,"revision":revision}));
    #[cfg(feature = "test-automation")]
    app.configuration
        .store
        .test_checkpoint("after_install")
        .map_err(|_| "apply_receipt_unknown")?;
    Ok(json!({"result":"loaded","committed":true,"receiptState":"known","loadedRevision":revision}))
}
