//! 九场景保值与真实selected重开：独立期望值，不依赖日志恢复或固定DB41/57。
use ds_runtime::{
    app::App,
    domain::{configuration::*, layout},
    infrastructure::logging::Evidence,
    services::{
        apply::{self, ApplyConfirmation, ApplyIntent},
        configuration::SaveIntent,
        layout::{self as layout_service, LayoutIntent},
        naming::{self, NamesIntent},
        owner::{Captured, Owner},
    },
};
use serde_json::json;
use std::{path::PathBuf, sync::Arc, time::Duration};
fn config() -> InstanceConfig {
    serde_json::from_value(json!({"id":uuid(),"name":"Retention","port":30102,"dbs":[{"id":uuid(),"name":"Primary","number":73,"length":16,"manual":true,"points":[{"id":uuid(),"name":"HoldValue","dataType":"UINT","byte":0,"manual":true,"manualReason":"explicit","policy":{"owner":"client","clientWrite":true,"uiMaintenance":true,"initial":5}},{"id":uuid(),"name":"FixedValue","dataType":"DINT","byte":4,"manual":true,"manualReason":"explicit","policy":{"mode":"fixed","owner":"rule","initial":0,"rule":{"kind":"fixed","fixedValue":7}}}]},{"id":uuid(),"name":"Independent","number":90,"length":8,"manual":true,"points":[{"id":uuid(),"name":"OtherHold","dataType":"UINT","byte":0,"manual":true,"manualReason":"explicit","policy":{"owner":"ui","uiWrite":true,"initial":8}}]}]})).unwrap()
}
fn confirmed(mut i: InstanceConfig) -> Arc<layout::CompiledInstance> {
    let frozen = i.clone();
    for d in &mut i.dbs {
        for p in &mut d.points {
            let old = frozen.dbs.iter().find(|v| v.id == d.id).unwrap();
            let e = layout::effective_policy(&frozen, old, p).unwrap();
            p.confirmations.initial = Some(layout::initial_signature(&p.data_type, &e).unwrap());
            p.confirmations.policy = Some(layout::policy_signature(&e));
        }
        d.address_confirmation = Some(AddressConfirmation {
            structure_sha256: layout::structure_signature(d),
            layout_sha256: layout::layout_signature(d),
            method: "manual".into(),
            reason: "explicit".into(),
        });
    }
    i.names_confirmation = Some(layout::names_signature(&i));
    Arc::new(layout::compile(&i).unwrap())
}
fn captured() -> (Arc<Owner>, Captured) {
    let config = confirmed(config());
    let owner = Owner::new(config.clone(), uuid(), Evidence::default()).unwrap();
    let hold = &config.config.dbs[0].points[0].id;
    let other = &config.config.dbs[1].points[0].id;
    owner.control("start", 0);
    owner
        .write_point(hold, &json!(44), &owner.loaded_revision(), 1, 0, true)
        .unwrap();
    owner
        .write_point(other, &json!(88), &owner.loaded_revision(), 1, 0, false)
        .unwrap();
    std::thread::sleep(Duration::from_millis(110));
    owner.control("stop", 0);
    let capture = owner.capture().unwrap();
    (owner, capture)
}
fn value(
    plan: &apply::Plan,
    compiled: &layout::CompiledInstance,
    db: u16,
    index: usize,
) -> serde_json::Value {
    plan.image
        .typed(db, index, &compiled.dbs[&db].points[index])
        .unwrap()
}
#[test]
fn nine_retention_scenarios_and_no_silent_fallback() {
    let (owner, old) = captured();
    assert_eq!(old.values[&old.config.config.dbs[0].points[0].id], 44);
    assert!(old.simulated_ns > 0);
    owner.control("start", 0);
    owner.control("stop", 0);
    assert_eq!(owner.capture().unwrap().values, old.values); // stop/start
    let mut rename = old.config.config.clone();
    rename.name = "Renamed".into();
    rename.max_connections = 8;
    rename.dbs[0].points[0].display_name = "display".into();
    let renamed = confirmed(rename);
    let p = apply::plan(&renamed, "new", Some(&old), false).unwrap();
    assert_eq!(value(&p, &renamed, 73, 0), 44);
    assert_eq!(value(&p, &renamed, 73, 1), 7);
    assert_eq!(p.simulated_ns, old.simulated_ns);
    let mut rules = old.config.config.clone();
    rules.dbs[0].points[1]
        .policy
        .rule
        .as_mut()
        .unwrap()
        .fixed_value = json!(9);
    let rules = confirmed(rules);
    let p = apply::plan(&rules, "new", Some(&old), false).unwrap();
    assert_eq!(value(&p, &rules, 73, 0), 44);
    assert_eq!(value(&p, &rules, 73, 1), 0);
    assert_eq!(p.simulated_ns, 0);
    let mut initial = old.config.config.clone();
    initial.dbs[0].points[0].policy.initial = Some(json!(10));
    let initial = confirmed(initial);
    let p = apply::plan(&initial, "new", Some(&old), false).unwrap();
    assert_eq!(value(&p, &initial, 73, 0), 10);
    assert_eq!(value(&p, &initial, 90, 0), 88);
    let mut policy = old.config.config.clone();
    let e = &mut policy.dbs[0].points[0].policy;
    e.owner = Some(WriteOwner::Ui);
    e.client_write = Some(false);
    e.ui_write = Some(true);
    e.ui_maintenance = Some(false);
    let policy = confirmed(policy);
    let p = apply::plan(&policy, "new", Some(&old), false).unwrap();
    assert_eq!(value(&p, &policy, 73, 0), 5);
    assert_eq!(value(&p, &policy, 90, 0), 88);
    let mut structural = old.config.config.clone();
    structural.dbs[0].number = 74;
    let structural = confirmed(structural);
    let p = apply::plan(&structural, "new", Some(&old), false).unwrap();
    assert_eq!(value(&p, &structural, 74, 0), 5);
    assert_eq!(value(&p, &structural, 90, 0), 88);
    let reset = apply::plan(&old.config, "old", Some(&old), true).unwrap();
    assert_eq!(value(&reset, &old.config, 73, 0), 5);
    assert_eq!(value(&reset, &old.config, 90, 0), 8);
    assert_eq!(reset.simulated_ns, 0); // rollback/default initialize_all
    let reopened = apply::plan(&old.config, "old", None, false).unwrap();
    assert_eq!(value(&reopened, &old.config, 73, 0), 5);
    assert_eq!(reopened.simulated_ns, 0); // process reopen
    let mut broken = old.clone();
    broken.values.remove(&old.config.config.dbs[0].points[0].id);
    assert!(
        matches!(apply::plan(&old.config,"new",Some(&broken),false),Err(e) if e=="preserve_value_missing")
    );
    assert_eq!(owner.capture().unwrap().values, old.values);
    broken
        .values
        .insert(old.config.config.dbs[0].points[0].id.clone(), json!(70000));
    assert!(
        matches!(apply::plan(&old.config,"new",Some(&broken),false),Err(e) if e=="preserve_encode_failed")
    );
    let explicit = apply::plan(&old.config, "new", Some(&broken), true).unwrap();
    assert_eq!(value(&explicit, &old.config, 73, 0), 5); // explicit alternative, never silent fallback
    let mut mixed = old.config.config.clone();
    mixed.dbs[0].length = 32;
    mixed.dbs[1].points[0].policy.initial = Some(json!(18));
    let mixed = confirmed(mixed);
    let mixed_plan = apply::plan(&mixed, "mixed", Some(&old), false).unwrap();
    assert_eq!(value(&mixed_plan, &mixed, 73, 0), 5);
    assert_eq!(value(&mixed_plan, &mixed, 90, 0), 18);
    assert_eq!(mixed_plan.simulated_ns, 0);
    owner.control("reset", 0);
    let reset = owner.capture().unwrap();
    assert_eq!(reset.values[&old.config.config.dbs[0].points[0].id], 5);
    assert_eq!(reset.epoch, 2);
    assert_eq!(reset.simulated_ns, 0);
    assert!(owner.shutdown());
}
#[test]
fn real_services_selected_reopen_idempotence_and_snapshot_generation_cas() {
    let root =
        PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("owned root")).join(uuid());
    let app = App::open(&root).unwrap();
    let i = config();
    let id = i.id.clone();
    let state = app.configuration.get().unwrap();
    let mut w = state.workspace;
    w.instances.push(i.clone());
    app.configuration
        .save(SaveIntent {
            expected_etag: state.etag,
            workspace: w,
            confirm_points: vec![],
        })
        .unwrap();
    for db in &i.dbs {
        let state = app.configuration.get().unwrap();
        let p = layout_service::preview(
            &app.configuration,
            LayoutIntent {
                expected_etag: state.etag,
                instance_id: id.clone(),
                db_id: db.id.clone(),
                method: "manual".into(),
                reason: "explicit synthetic addresses".into(),
            },
        )
        .unwrap();
        app.configuration
            .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
            .unwrap();
    }
    let state = app.configuration.get().unwrap();
    let point_ids = i
        .dbs
        .iter()
        .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
        .collect::<Vec<_>>();
    let p = naming::preview(
        &app.configuration,
        NamesIntent {
            expected_etag: state.etag,
            instance_id: id.clone(),
            point_ids: point_ids.clone(),
            address_only: false,
        },
    )
    .unwrap();
    app.configuration
        .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
        .unwrap();
    let state = app.configuration.get().unwrap();
    let saved = app
        .configuration
        .save(SaveIntent {
            expected_etag: state.etag,
            workspace: state.workspace,
            confirm_points: point_ids,
        })
        .unwrap();
    let revision = saved.revision_id.unwrap();
    let p = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: saved.etag.clone(),
            instance_id: id.clone(),
            revision_id: revision.clone(),
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    let impact = p.details["impactSha256"].as_str().unwrap().to_owned();
    apply::confirm(
        &app,
        ApplyConfirmation {
            expected_etag: p.expected_etag,
            instance_id: id.clone(),
            token: p.token,
            candidate_sha256: p.candidate_sha256,
            impact_sha256: impact,
        },
    )
    .unwrap();
    let instance = app.instance(&id).unwrap();
    assert!(instance.stopped());
    assert_eq!(
        instance.context.owner.capture().unwrap().values[&i.dbs[0].points[0].id],
        5
    );
    let p = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: saved.etag.clone(),
            instance_id: id.clone(),
            revision_id: revision.clone(),
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    instance.context.owner.control("start", 0);
    instance.context.owner.control("stop", 0);
    assert_eq!(
        apply::confirm(
            &app,
            ApplyConfirmation {
                expected_etag: p.expected_etag,
                instance_id: id.clone(),
                token: p.token,
                candidate_sha256: p.candidate_sha256,
                impact_sha256: p.details["impactSha256"].as_str().unwrap().into()
            }
        )
        .unwrap_err(),
        "apply_snapshot_stale"
    );
    let p = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: saved.etag,
            instance_id: id.clone(),
            revision_id: revision,
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    let result = apply::confirm(
        &app,
        ApplyConfirmation {
            expected_etag: p.expected_etag,
            instance_id: id.clone(),
            token: p.token,
            candidate_sha256: p.candidate_sha256,
            impact_sha256: p.details["impactSha256"].as_str().unwrap().into(),
        },
    )
    .unwrap();
    assert_eq!(result["result"], "already_loaded");
    assert_eq!(instance.context.owner.epoch_revision().0, 1);
    // stale保存和真实SQL写锁失败不能先关闭owner/删除manager或改变hold值。
    instance.context.owner.control("start", 0);
    let point = &i.dbs[0].points[0].id;
    instance
        .context
        .owner
        .write_point(
            point,
            &json!(44),
            &instance.context.owner.loaded_revision(),
            1,
            0,
            true,
        )
        .unwrap();
    instance.context.owner.control("stop", 0);
    let before = instance.context.owner.capture().unwrap();
    let current = app.configuration.get().unwrap();
    let mut deletion = current.workspace.clone();
    deletion.instances.clear();
    assert!(ds_runtime::services::queries::save(
        &app,
        SaveIntent {
            expected_etag: uuid(),
            workspace: deletion.clone(),
            confirm_points: vec![]
        }
    )
    .unwrap_err()
    .starts_with("etag_conflict:"));
    assert_eq!(
        app.instance(&id)
            .unwrap()
            .context
            .owner
            .capture()
            .unwrap()
            .values,
        before.values
    );
    let blocker = rusqlite::Connection::open(&app.configuration.store.path).unwrap();
    blocker.execute_batch("BEGIN IMMEDIATE").unwrap();
    assert!(ds_runtime::services::queries::save(
        &app,
        SaveIntent {
            expected_etag: current.etag.clone(),
            workspace: deletion,
            confirm_points: vec![]
        }
    )
    .is_err());
    blocker.execute_batch("ROLLBACK").unwrap();
    drop(blocker);
    assert_eq!(
        app.configuration.get().unwrap().workspace,
        current.workspace
    );
    assert_eq!(
        app.instance(&id)
            .unwrap()
            .context
            .owner
            .capture()
            .unwrap()
            .values,
        before.values
    );
    // 模拟换版持控制序列跨SQL：stop必须独立封准入/推进generation，不能等待此锁。
    instance.context.owner.control("start", 0);
    let guard = instance.control.lock().unwrap();
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::scope(|scope| {
        scope.spawn(|| {
            let result = ds_runtime::services::queries::control(
                &app,
                ds_runtime::config::workspace::ControlIntent {
                    instance_id: id.clone(),
                    command: "stop".into(),
                    expected_loaded_revision: instance.context.owner.loaded_revision(),
                    epoch: "1".into(),
                    discard_values: false,
                },
            );
            tx.send(result.is_ok()).unwrap();
        });
        let result = rx.recv_timeout(Duration::from_millis(250));
        drop(guard);
        assert_eq!(result.unwrap(), true);
    });
    assert!(app.shutdown());
    drop(instance);
    drop(app);
    let reopened = App::open(&root).unwrap();
    let instance = reopened.instance(&id).unwrap();
    assert!(instance.stopped());
    assert_eq!(
        instance.context.owner.capture().unwrap().values[&i.dbs[0].points[0].id],
        5
    );
    assert_eq!(instance.context.owner.capture().unwrap().simulated_ns, 0);
    let current = reopened.configuration.get().unwrap();
    let mut deletion = current.workspace;
    deletion.instances.clear();
    ds_runtime::services::queries::save(
        &reopened,
        SaveIntent {
            expected_etag: current.etag,
            workspace: deletion,
            confirm_points: vec![],
        },
    )
    .unwrap();
    assert!(reopened.instance(&id).is_err());
    assert!(reopened
        .configuration
        .store
        .selections()
        .unwrap()
        .is_empty());
    assert!(reopened.shutdown());
}

#[test]
fn ipc_receipts_distinguish_noop_selected_commit_and_unknown_from_normal_rejection() {
    use ds_runtime::config::workspace::{u64_value, ControlIntent, Operation, Response};
    for result in ["unchanged", "already_loaded"] {
        let r = Response::from_result(Ok(json!({"result":result,"committed":false})), true);
        assert_eq!(r.committed, Some(false));
        assert_eq!(r.receipt_state, "known");
    }
    let r=Response::from_result(Err("load_failed_after_selection_commit:{\"selectedRevision\":\"new-revision\",\"state\":\"load_failed\"}".into()),true);
    assert_eq!(r.error_code.as_deref(), Some("load_failed"));
    assert_eq!(r.committed, Some(true));
    assert_eq!(r.data.unwrap()["selectedRevision"], "new-revision");
    let r = Response::from_result(Err("selection_commit_unknown".into()), true);
    assert_eq!(r.committed, None);
    assert_eq!(r.receipt_state, "unknown");
    let r = Response::from_result(Err("optimized_access_unknown".into()), true);
    assert_eq!(r.committed, Some(false));
    assert_eq!(r.receipt_state, "known");
    assert!(serde_json::from_value::<Operation<ControlIntent>>(json!({"operationId":uuid(),"payload":{"instanceId":uuid(),"command":"stop","expectedLoadedRevision":uuid(),"epoch":"1","arbitrarySql":"delete"}})).is_err());
    assert!(u64_value("18446744073709551616").is_err());
    assert!(u64_value("1.5").is_err());
    assert_eq!(u64_value("9007199254740993").unwrap(), 9007199254740993);
}

#[test]
fn real_selection_install_failure_and_post_install_ack_loss_remain_distinct() {
    for point in [
        "before_select_commit",
        "after_select_commit",
        "before_install",
        "after_install",
    ] {
        let root = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").unwrap()).join(uuid());
        let app = App::open(&root).unwrap();
        let initial = config();
        let id = initial.id.clone();
        ds_runtime::testing::hooks::prepare_workspace(
            &app,
            Workspace {
                instances: vec![initial.clone()],
                source_versions: vec![],
                ..Workspace::default()
            },
        )
        .unwrap();
        let existing = app.instance(&id).unwrap();
        let before = existing.context.owner.capture().unwrap();
        let current = app.configuration.get().unwrap();
        let mut changed = current.workspace;
        changed.instances[0].name = "New revision".into();
        let saved = app
            .configuration
            .save(SaveIntent {
                expected_etag: current.etag,
                workspace: changed,
                confirm_points: vec![],
            })
            .unwrap();
        let revision = saved.revision_id.unwrap();
        let preview = apply::preview(
            &app,
            ApplyIntent {
                expected_etag: saved.etag,
                instance_id: id.clone(),
                revision_id: revision.clone(),
                retention: "preserve_compatible_hold".into(),
            },
        )
        .unwrap();
        app.configuration.store.test_fault(point).unwrap();
        let result = apply::confirm(
            &app,
            ApplyConfirmation {
                expected_etag: preview.expected_etag,
                instance_id: id.clone(),
                token: preview.token,
                candidate_sha256: preview.candidate_sha256,
                impact_sha256: preview.details["impactSha256"].as_str().unwrap().into(),
            },
        );
        let error = result.unwrap_err();
        let selected = app.configuration.store.selections().unwrap();
        let after = existing.context.owner.capture().unwrap();
        match point {
            "before_select_commit" => {
                assert_eq!(error, "test_fault");
                assert_eq!(selected[0].revision_id, before.loaded_revision);
                assert_eq!(after.epoch, before.epoch);
                assert_eq!(after.values, before.values);
                assert!(!app.load_errors.lock().unwrap().contains_key(&id));
            }
            "after_select_commit" => {
                assert_eq!(error, "selection_receipt_unknown");
                assert_eq!(selected[0].revision_id, revision);
                assert_eq!(after.loaded_revision, before.loaded_revision);
                assert_eq!(app.load_errors.lock().unwrap()[&id], "selection_unknown");
            }
            "before_install" => {
                assert!(error.starts_with("load_failed_after_selection_commit:"));
                assert_eq!(selected[0].revision_id, revision);
                assert_eq!(after.epoch, before.epoch);
                assert_eq!(after.values, before.values);
                assert_eq!(app.load_errors.lock().unwrap()[&id], "load_failed");
            }
            "after_install" => {
                assert_eq!(error, "apply_receipt_unknown");
                assert_eq!(after.loaded_revision, revision);
                assert_eq!(after.epoch, before.epoch + 1);
                assert!(!app.load_errors.lock().unwrap().contains_key(&id));
            }
            _ => unreachable!(),
        }
        if point == "after_select_commit" || point == "before_install" {
            let result = ds_runtime::services::queries::control(
                &app,
                ds_runtime::config::workspace::ControlIntent {
                    instance_id: id.clone(),
                    command: "start".into(),
                    expected_loaded_revision: before.loaded_revision.clone(),
                    epoch: before.epoch.to_string(),
                    discard_values: false,
                },
            );
            assert!(result.is_err()); // committed selection must not start the old diagnostic image
        }
        assert!(app.shutdown());
        drop(existing);
        drop(app);
        let reopened = App::open(&root).unwrap();
        let loaded = reopened.instance(&id).unwrap();
        assert!(loaded.stopped());
        assert_eq!(
            loaded.context.owner.loaded_revision(),
            selected[0].revision_id
        );
        assert_eq!(
            loaded.context.owner.capture().unwrap().values[&initial.dbs[0].points[0].id],
            5
        );
        assert!(reopened.shutdown());
    }
}

#[test]
fn real_sql_and_same_owner_install_execute_retention_changes_and_rollback() {
    fn apply_saved(app: &App, id: &str, revision: &str) -> serde_json::Value {
        let state = app.configuration.get().unwrap();
        let p = apply::preview(
            app,
            ApplyIntent {
                expected_etag: state.etag,
                instance_id: id.into(),
                revision_id: revision.into(),
                retention: "preserve_compatible_hold".into(),
            },
        )
        .unwrap();
        let facts = p.details.clone();
        apply::confirm(
            app,
            ApplyConfirmation {
                expected_etag: p.expected_etag,
                instance_id: id.into(),
                token: p.token,
                candidate_sha256: p.candidate_sha256,
                impact_sha256: facts["impactSha256"].as_str().unwrap().into(),
            },
        )
        .unwrap();
        facts
    }
    fn confirm_current(app: &App, id: &str) -> String {
        let config = app
            .configuration
            .get()
            .unwrap()
            .workspace
            .instances
            .into_iter()
            .find(|i| i.id == id)
            .unwrap();
        for db in &config.dbs {
            let p = layout_service::preview(
                &app.configuration,
                LayoutIntent {
                    expected_etag: app.configuration.get().unwrap().etag,
                    instance_id: id.into(),
                    db_id: db.id.clone(),
                    method: "manual".into(),
                    reason: "explicit actual retention integration addresses".into(),
                },
            )
            .unwrap();
            app.configuration
                .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
                .unwrap();
        }
        let ids = config
            .dbs
            .iter()
            .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
            .collect::<Vec<_>>();
        let p = naming::preview(
            &app.configuration,
            NamesIntent {
                expected_etag: app.configuration.get().unwrap().etag,
                instance_id: id.into(),
                point_ids: ids.clone(),
                address_only: false,
            },
        )
        .unwrap();
        app.configuration
            .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
            .unwrap();
        let state = app.configuration.get().unwrap();
        app.configuration
            .save(SaveIntent {
                expected_etag: state.etag,
                workspace: state.workspace,
                confirm_points: ids,
            })
            .unwrap()
            .revision_id
            .unwrap()
    }
    for case in [
        "display",
        "rule",
        "initial",
        "policy",
        "structure",
        "mixed",
        "rollback",
    ] {
        let root = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").unwrap()).join(uuid());
        let app = App::open(&root).unwrap();
        let i = config();
        let id = i.id.clone();
        let hold = i.dbs[0].points[0].id.clone();
        let fixed = i.dbs[0].points[1].id.clone();
        let other = i.dbs[1].points[0].id.clone();
        ds_runtime::testing::hooks::prepare_workspace(
            &app,
            Workspace {
                instances: vec![i],
                ..Workspace::default()
            },
        )
        .unwrap();
        let instance = app.instance(&id).unwrap();
        let owner = &instance.context.owner;
        let original = owner.loaded_revision();
        owner.control("start", 0);
        owner
            .write_point(&hold, &json!(44), &original, 1, 0, true)
            .unwrap();
        owner
            .write_point(&other, &json!(88), &original, 1, 0, false)
            .unwrap();
        std::thread::sleep(Duration::from_millis(110));
        owner.control("stop", 0);
        let before = owner.capture().unwrap();
        assert_eq!(before.values[&fixed], 7);
        let state = app.configuration.get().unwrap();
        let mut changed = state.workspace;
        let changed_instance = &mut changed.instances[0];
        match case {
            "display" | "rollback" => {
                changed_instance.name = "Displayed new revision".into();
                changed_instance.max_connections = 8;
            }
            "rule" => {
                changed_instance.dbs[0].points[1]
                    .policy
                    .rule
                    .as_mut()
                    .unwrap()
                    .fixed_value = json!(9)
            }
            "initial" => changed_instance.dbs[0].points[0].policy.initial = Some(json!(10)),
            "policy" => {
                let p = &mut changed_instance.dbs[0].points[0].policy;
                p.owner = Some(WriteOwner::Ui);
                p.client_write = Some(false);
                p.ui_write = Some(true);
                p.ui_maintenance = Some(false);
            }
            "structure" | "mixed" => {
                changed_instance.dbs[0].number = 74;
                changed_instance.dbs[0].length = 32;
                if case == "mixed" {
                    let p = &mut changed_instance.dbs[1].points[0].policy;
                    p.owner = Some(WriteOwner::None);
                    p.ui_write = Some(false);
                }
            }
            _ => unreachable!(),
        }
        app.configuration
            .save(SaveIntent {
                expected_etag: state.etag,
                workspace: changed,
                confirm_points: vec![],
            })
            .unwrap();
        let revision = confirm_current(&app, &id);
        apply_saved(&app, &id, &revision);
        let mut expected_hold = if ["display", "rule", "rollback"].contains(&case) {
            44
        } else if case == "initial" {
            10
        } else {
            5
        };
        let mut expected_other = if case == "mixed" { 8 } else { 88 };
        let after = owner.capture().unwrap();
        assert_eq!(after.values[&hold], expected_hold, "{case}");
        assert_eq!(after.values[&other], expected_other, "{case}");
        assert_eq!(after.epoch, before.epoch + 1);
        assert!(instance.stopped());
        assert!(owner
            .write_point(&hold, &json!(99), &original, before.epoch, 0, true)
            .is_err());
        assert_eq!(owner.capture().unwrap().values, after.values); // old revision/epoch has zero mutation
        if case == "display" || case == "rollback" {
            assert_eq!(after.values[&fixed], 7);
            assert_eq!(after.simulated_ns, before.simulated_ns)
        } else {
            assert_eq!(after.values[&fixed], 0);
            assert_eq!(after.simulated_ns, 0)
        }
        let selected = app.configuration.store.selections().unwrap();
        assert_eq!(selected[0].revision_id, revision);
        if case == "rollback" {
            let facts = apply_saved(&app, &id, &original);
            assert_eq!(facts["rollback"], true);
            assert_eq!(facts["initializeAll"], true);
            expected_hold = 5;
            expected_other = 8;
            let rollback = owner.capture().unwrap();
            assert_eq!(rollback.values[&hold], expected_hold);
            assert_eq!(rollback.values[&other], expected_other);
            assert_eq!(rollback.simulated_ns, 0);
        }
        assert!(app.shutdown());
        drop(instance);
        drop(app);
        let reopened = App::open(&root).unwrap();
        let loaded = reopened.instance(&id).unwrap();
        let values = loaded.context.owner.capture().unwrap();
        assert!(loaded.stopped());
        assert_eq!(values.simulated_ns, 0);
        assert_eq!(values.values[&hold], if case == "initial" { 10 } else { 5 });
        assert_eq!(values.values[&other], 8);
        assert!(reopened.shutdown());
    }
}
