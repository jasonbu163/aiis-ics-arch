//! DS-004 双语名称/描述、旧版本与重导的隔离合成配置合同测试。
use ds_runtime::{
    app::App,
    domain::configuration::{self, uuid, DisplayNames, PointConfig, Workspace},
    infrastructure::config_store::Store,
    services::{
        configuration::{Configuration, SaveIntent},
        layout::{self, LayoutIntent},
        naming::{self, NamesIntent},
        source_import::{self, BindingIntent, Declaration, ImportFile, ImportIntent},
    },
};
use serde_json::{json, Value};
use std::{fs, path::PathBuf, sync::Arc};

#[test]
#[ignore = "explicit synthetic compatibility probe"]
fn compatibility_probe() {
    let root = PathBuf::from(std::env::var_os("DS4_COMPAT_PROFILE").expect("explicit profile"));
    let mode = std::env::var("DS4_COMPAT_MODE").expect("explicit mode");
    let db = root.join("device-simulator-v1/config.sqlite");
    if mode == "create" || mode == "blank" {
        assert!(!root.exists());
        fs::create_dir_all(&root).unwrap();
        let store = Store::open(&root).unwrap();
        if mode == "blank" {
            store.shutdown().unwrap();
            return;
        }
        let state = store.load().unwrap();
        let workspace: Workspace = serde_json::from_value(serde_json::json!({
            "schemaVersion": 1,
            "instances": [{"id": uuid(), "name": "DS4 Synthetic", "port": 32194,
                "dbs": [{"id": uuid(), "name": "Synthetic DB", "number": 71, "length": 2, "manual": true,
                    "points": [{"id": uuid(), "name": "LegacyPoint", "displayName": "旧值 / legacy", "dataType": "INT", "byte": 0, "manual": true, "manualReason": "synthetic"}]}]}],
            "sourceVersions": []
        })).unwrap();
        let saved = store.save(&state.etag, workspace.clone()).unwrap();
        let revision = store.publish(&saved.etag).unwrap().revision_id.unwrap();
        store
            .select(&workspace.instances[0].id, &revision, None)
            .unwrap();
        store.shutdown().unwrap();
    } else {
        let before = fs::read(&db).expect("existing synthetic DB");
        match mode.as_str() {
            "old" => {
                let app = App::open(&root).unwrap();
                assert_eq!(
                    app.configuration.get().unwrap().workspace.instances[0].dbs[0].points[0]
                        .display_name,
                    "旧值 / legacy"
                );
                assert!(
                    app.configuration.get().unwrap().workspace.instances[0].dbs[0].points[0]
                        .display_names
                        .is_none()
                );
                assert!(
                    app.configuration.get().unwrap().workspace.instances[0].dbs[0].points[0]
                        .description
                        .is_none()
                );
                assert!(app.shutdown());
            }
            "upgrade" => {
                let app = App::open(&root).unwrap();
                let state = app.configuration.get().unwrap();
                let selections = app.configuration.store.selections().unwrap();
                let old_revision = app
                    .configuration
                    .store
                    .revision(&selections[0].revision_id)
                    .unwrap();
                let mut workspace = state.workspace;
                let point = &mut workspace.instances[0].dbs[0].points[0];
                point.display_names = Some(DisplayNames {
                    zh_cn: " 双语名 ".into(),
                    en_us: "".into(),
                });
                point.description = Some("Explicit description".into());
                app.configuration
                    .save(SaveIntent {
                        expected_etag: state.etag,
                        workspace,
                        confirm_points: vec![],
                    })
                    .unwrap();
                assert_eq!(
                    app.configuration
                        .store
                        .revision(&selections[0].revision_id)
                        .unwrap(),
                    old_revision
                );
                assert_eq!(
                    app.configuration.store.selections().unwrap()[0].selection_etag,
                    selections[0].selection_etag
                );
                assert!(app.shutdown());
            }
            "reject" => match App::open(&root) {
                Err(error) => assert_eq!(error, "storage_payload"),
                Ok(app) => {
                    app.shutdown();
                    panic!("old app accepted new payload")
                }
            },
            _ => panic!("unknown probe mode"),
        }
        if mode != "upgrade" {
            assert_eq!(fs::read(&db).unwrap(), before, "profile bytes changed");
        }
    }
}

fn owned_profile() -> PathBuf {
    PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("explicit owned test root"))
        .join(uuid())
}
fn fixture() -> Workspace {
    serde_json::from_value(json!({"schemaVersion":1,"instances":[
        {"id":uuid(),"name":"A","port":32194,"dbs":[{"id":uuid(),"name":"Manual","number":71,"length":4,"manual":true,"points":[
            {"id":uuid(),"name":"Stable","displayName":"legacy 无语言","dataType":"INT","byte":0,"manual":true,"manualReason":"synthetic"},
            {"id":uuid(),"name":"Other","dataType":"INT","byte":2,"manual":true,"manualReason":"synthetic"}
        ]}]},
        {"id":uuid(),"name":"B","port":32195,"dbs":[]}
    ],"sourceVersions":[]})).unwrap()
}
fn point_json() -> Value {
    json!({"id":uuid(),"name":"Stable","displayName":"legacy","dataType":"INT"})
}

#[test]
fn strict_optional_fields_reject_invalid_types_keys_and_byte_limits() {
    let base = point_json();
    let point: PointConfig = serde_json::from_value(base.clone()).unwrap();
    assert!(point.display_names.is_none() && point.description.is_none());
    assert!(serde_json::to_value(&point)
        .unwrap()
        .get("displayNames")
        .is_none());
    for bad in [
        json!(null),
        json!("text"),
        json!({}),
        json!({"zh-CN":"x"}),
        json!({"zh-CN":"x","en-US":null}),
        json!({"zh-CN":false,"en-US":""}),
        json!({"zh-CN":"x","en-US":"y","other":"z"}),
    ] {
        let mut value = base.clone();
        value["displayNames"] = bad;
        assert!(serde_json::from_value::<PointConfig>(value).is_err());
    }
    for bad in [json!(null), json!(1), json!([]), json!({})] {
        let mut value = base.clone();
        value["description"] = bad;
        assert!(serde_json::from_value::<PointConfig>(value).is_err());
    }
    let mut w = fixture();
    let p = &mut w.instances[0].dbs[0].points[0];
    p.display_names = Some(DisplayNames {
        zh_cn: "界".repeat(85) + "a",
        en_us: "  English  ".into(),
    });
    p.description = Some("字".repeat(166) + "ab");
    assert!(configuration::validate(&w).is_ok());
    let encoded = serde_json::to_vec(&w).unwrap();
    let decoded: Workspace = serde_json::from_slice(&encoded).unwrap();
    assert_eq!(decoded, w);
    w.instances[0].dbs[0].points[0]
        .display_names
        .as_mut()
        .unwrap()
        .zh_cn
        .push('a');
    assert_eq!(configuration::validate(&w).unwrap_err(), "point_parameters");
    w.instances[0].dbs[0].points[0]
        .display_names
        .as_mut()
        .unwrap()
        .zh_cn
        .clear();
    w.instances[0].dbs[0].points[0]
        .description
        .as_mut()
        .unwrap()
        .push('x');
    assert_eq!(configuration::validate(&w).unwrap_err(), "point_parameters");
}

#[test]
fn explicit_save_reopen_cas_and_history_remain_isolated() {
    let root = owned_profile();
    let service = Configuration::new(Arc::new(Store::open(&root).unwrap()));
    let initial = service.get().unwrap();
    let mut w = fixture();
    let saved = service
        .save(SaveIntent {
            expected_etag: initial.etag,
            workspace: w.clone(),
            confirm_points: vec![],
        })
        .unwrap();
    let old_revision = service
        .store
        .publish(&saved.etag)
        .unwrap()
        .revision_id
        .unwrap();
    let selection = service
        .store
        .select(&w.instances[0].id, &old_revision, None)
        .unwrap();
    let db = rusqlite::Connection::open(&service.store.path).unwrap();
    let historical: (Vec<u8>, String) = db
        .query_row(
            "SELECT payload,sha256 FROM configuration_revisions WHERE revision_id=?1",
            [&old_revision],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .unwrap();
    drop(db);
    let other_point = w.instances[0].dbs[0].points[1].clone();
    let other_instance = w.instances[1].clone();
    let p = &mut w.instances[0].dbs[0].points[0];
    p.display_names = Some(DisplayNames {
        zh_cn: " 温度🌡 ".into(),
        en_us: "".into(),
    });
    p.description = Some(" 独立说明 ".into());
    let saved_new = service
        .save(SaveIntent {
            expected_etag: saved.etag.clone(),
            workspace: w.clone(),
            confirm_points: vec![],
        })
        .unwrap();
    assert!(service
        .save(SaveIntent {
            expected_etag: saved.etag,
            workspace: fixture(),
            confirm_points: vec![]
        })
        .unwrap_err()
        .starts_with("etag_conflict:"));
    assert_eq!(service.get().unwrap().workspace, w);
    assert_eq!(
        w.instances[0].dbs[0].points[0].display_name,
        "legacy 无语言"
    );
    assert_eq!(w.instances[0].dbs[0].points[0].name, "Stable");
    assert_eq!(w.instances[0].dbs[0].points[1], other_point);
    assert_eq!(w.instances[1], other_instance);
    assert_eq!(
        service.store.selections().unwrap()[0].selection_etag,
        selection.selection_etag
    );
    let new_revision = service
        .store
        .publish(&saved_new.etag)
        .unwrap()
        .revision_id
        .unwrap();
    assert_ne!(old_revision, new_revision);
    assert!(
        service.store.revision(&old_revision).unwrap().instances[0].dbs[0].points[0]
            .display_names
            .is_none()
    );
    let db = rusqlite::Connection::open(&service.store.path).unwrap();
    let still: (Vec<u8>, String) = db
        .query_row(
            "SELECT payload,sha256 FROM configuration_revisions WHERE revision_id=?1",
            [&old_revision],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .unwrap();
    assert_eq!(still, historical);
    drop(db);
    service.store.shutdown().unwrap();
    drop(service);
    let reopened = Store::open(&root).unwrap();
    assert_eq!(reopened.load().unwrap().workspace, w);
    assert_eq!(reopened.selections().unwrap()[0].revision_id, old_revision);
    let mut cleared = w;
    let p = &mut cleared.instances[0].dbs[0].points[0];
    p.display_names.as_mut().unwrap().en_us = "English".into();
    p.display_names.as_mut().unwrap().zh_cn.clear();
    p.description = None;
    let etag = reopened.load().unwrap().etag;
    reopened.save(&etag, cleared.clone()).unwrap();
    assert_eq!(reopened.load().unwrap().workspace, cleared);
    reopened.shutdown().unwrap();
}

#[test]
fn tia_reimport_retains_only_matching_ids_and_previews_do_not_overwrite() {
    let root = owned_profile();
    let service = Configuration::new(Arc::new(Store::open(&root).unwrap()));
    let initial = service.get().unwrap();
    let mut w = fixture();
    let other = w.instances.pop().unwrap();
    w.instances[0].dbs.clear();
    let instance = w.instances[0].id.clone();
    w.instances.push(other.clone());
    service
        .save(SaveIntent {
            expected_etag: initial.etag,
            workspace: w,
            confirm_points: vec![],
        })
        .unwrap();
    let source = |changed: bool| {
        format!("DATA_BLOCK \"Synthetic\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\nValue : {}; // source comment\n{} : BOOL;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK\n", if changed { "DINT" } else { "INT" }, if changed { "Added" } else { "Removed" }).into_bytes()
    };
    let request =
        |etag: String, db_id: Option<String>, lineage_id: Option<String>, changed| ImportIntent {
            expected_etag: etag,
            instance_id: instance.clone(),
            files: vec![ImportFile {
                input_id: "synthetic".into(),
                name: "synthetic.db".into(),
                bytes: source(changed),
                lineage_id,
            }],
            bindings: vec![BindingIntent {
                db_id,
                number: 71,
                declaration: Declaration {
                    input_id: "synthetic".into(),
                    declaration_index: 0,
                },
                udt_closure: vec![],
            }],
        };
    let first = source_import::preview(
        &service,
        request(service.get().unwrap().etag, None, None, false),
    )
    .unwrap()
    .preview
    .unwrap();
    let p = &first.workspace.instances[0].dbs[0].points[0];
    assert_eq!(p.display_name, "source comment");
    assert!(p.display_names.is_none() && p.description.is_none());
    service
        .confirm(
            "import",
            &first.token,
            &first.expected_etag,
            &first.candidate_sha256,
        )
        .unwrap();
    let state = service.get().unwrap();
    let db_id = state.workspace.instances[0].dbs[0].id.clone();
    let lineage = state.workspace.source_versions[0].lineage_id.clone();
    let source_before = state.workspace.source_versions[0].clone();
    let mut w = state.workspace;
    let p = &mut w.instances[0].dbs[0].points[0];
    let point_id = p.id.clone();
    p.display_name = "hand edited legacy".into();
    p.display_names = Some(DisplayNames {
        zh_cn: "甲".into(),
        en_us: " A ".into(),
    });
    p.description = Some("explicit TIA description".into());
    service
        .save(SaveIntent {
            expected_etag: state.etag,
            workspace: w,
            confirm_points: vec![],
        })
        .unwrap();
    let state = service.get().unwrap();
    let layout = layout::preview(
        &service,
        LayoutIntent {
            expected_etag: state.etag.clone(),
            instance_id: instance.clone(),
            db_id: db_id.clone(),
            method: "standard".into(),
            reason: "".into(),
        },
    )
    .unwrap();
    assert_eq!(
        layout.workspace.instances[0].dbs[0].points[0]
            .description
            .as_deref(),
        Some("explicit TIA description")
    );
    assert_eq!(service.get().unwrap().etag, state.etag);
    service
        .confirm(
            "layout",
            &layout.token,
            &layout.expected_etag,
            &layout.candidate_sha256,
        )
        .unwrap();
    let state = service.get().unwrap();
    let point_ids = state.workspace.instances[0].dbs[0]
        .points
        .iter()
        .map(|p| p.id.clone())
        .collect();
    let names = naming::preview(
        &service,
        NamesIntent {
            expected_etag: state.etag.clone(),
            instance_id: instance.clone(),
            point_ids,
            address_only: false,
        },
    )
    .unwrap();
    assert_eq!(
        names.workspace.instances[0].dbs[0].points[0]
            .display_names
            .as_ref()
            .unwrap()
            .zh_cn,
        "甲"
    );
    service
        .confirm(
            "names",
            &names.token,
            &names.expected_etag,
            &names.candidate_sha256,
        )
        .unwrap();
    let before = service.get().unwrap();
    let preview = source_import::preview(
        &service,
        request(
            before.etag.clone(),
            Some(db_id.clone()),
            Some(lineage.clone()),
            true,
        ),
    )
    .unwrap()
    .preview
    .unwrap();
    let changed = &preview.workspace.instances[0].dbs[0].points;
    assert_eq!(changed[0].id, point_id);
    assert_eq!(changed[0].display_name, "hand edited legacy");
    assert_eq!(changed[0].display_names.as_ref().unwrap().en_us, " A ");
    assert_eq!(
        changed[0].description.as_deref(),
        Some("explicit TIA description")
    );
    assert!(changed[1].display_names.is_none() && changed[1].description.is_none());
    assert_ne!(
        changed[1].id,
        before.workspace.instances[0].dbs[0].points[1].id
    );
    assert_eq!(service.get().unwrap().workspace, before.workspace);
    service.finish_preview(&preview.token);
    assert!(service
        .confirm(
            "import",
            &preview.token,
            &preview.expected_etag,
            &preview.candidate_sha256
        )
        .is_err());
    assert_eq!(service.get().unwrap().etag, before.etag);
    let stale = source_import::preview(
        &service,
        request(
            before.etag.clone(),
            Some(db_id.clone()),
            Some(lineage.clone()),
            true,
        ),
    )
    .unwrap()
    .preview
    .unwrap();
    let mut concurrent = before.workspace;
    concurrent.instances[0].dbs[0].points[0].description = Some("concurrent".into());
    service
        .save(SaveIntent {
            expected_etag: before.etag,
            workspace: concurrent,
            confirm_points: vec![],
        })
        .unwrap();
    assert!(service
        .confirm(
            "import",
            &stale.token,
            &stale.expected_etag,
            &stale.candidate_sha256
        )
        .unwrap_err()
        .starts_with("etag_conflict:"));
    let current = service.get().unwrap();
    let next = source_import::preview(
        &service,
        request(current.etag, Some(db_id), Some(lineage), true),
    )
    .unwrap()
    .preview
    .unwrap();
    service
        .confirm(
            "import",
            &next.token,
            &next.expected_etag,
            &next.candidate_sha256,
        )
        .unwrap();
    let final_state = service.get().unwrap();
    let retained = &final_state.workspace.instances[0].dbs[0].points[0];
    assert_eq!(retained.id, point_id);
    assert_eq!(retained.description.as_deref(), Some("concurrent"));
    assert_eq!(retained.display_names.as_ref().unwrap().zh_cn, "甲");
    assert_eq!(final_state.workspace.instances[1], other);
    assert!(final_state
        .workspace
        .source_versions
        .contains(&source_before));
    service.store.shutdown().unwrap();
}

#[cfg(feature = "test-automation")]
#[test]
fn committed_save_receipt_fault_emits_real_readback_for_ui_reconciliation() {
    use ds_runtime::{
        config::workspace::{ConfigurationQuery, Response},
        services::queries,
    };
    let root = owned_profile();
    let app = App::open(&root).unwrap();
    let before = queries::configuration(&app, ConfigurationQuery::default()).unwrap();
    let mut workspace = fixture();
    workspace.instances[0].dbs[0].points[0].display_names = Some(DisplayNames {
        zh_cn: "故障注入".into(),
        en_us: "Synthetic fault".into(),
    });
    workspace.instances[0].dbs[0].points[0].description = Some("explicit".into());
    app.configuration
        .store
        .test_fault("after_save_commit")
        .unwrap();
    let result = queries::save(
        &app,
        SaveIntent {
            expected_etag: before["etag"].as_str().unwrap().into(),
            workspace: workspace.clone(),
            confirm_points: vec![],
        },
    );
    let response = serde_json::to_value(Response::from_result(result, true)).unwrap();
    assert_eq!(response["result"], "unknown");
    assert_eq!(response["errorCode"], "save_receipt_unknown");
    assert!(response["committed"].is_null());
    let saved = queries::configuration(&app, ConfigurationQuery::default()).unwrap();
    assert_ne!(saved["etag"], before["etag"]);
    assert_eq!(saved["workspace"], serde_json::to_value(workspace).unwrap());
    println!(
        "DS4_F1_FAULT_EVIDENCE:{}",
        json!({"before":before,"response":response,"saved":saved})
    );
    assert!(app.shutdown());
}

#[cfg(feature = "test-automation")]
#[test]
fn submitted_confirmations_are_recomputed_before_the_unknown_receipt() {
    use ds_runtime::{config::workspace::ConfigurationQuery, services::queries};
    let root = owned_profile();
    let app = App::open(&root).unwrap();
    let initial = app.configuration.get().unwrap();
    let mut workspace = fixture();
    workspace.instances[0].dbs[0].length = 8;
    app.configuration
        .save(SaveIntent {
            expected_etag: initial.etag,
            workspace: workspace.clone(),
            confirm_points: vec![],
        })
        .unwrap();
    let instance_id = workspace.instances[0].id.clone();
    let db_id = workspace.instances[0].dbs[0].id.clone();
    let point_id = workspace.instances[0].dbs[0].points[0].id.clone();
    let preview = layout::preview(
        &app.configuration,
        LayoutIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            instance_id: instance_id.clone(),
            db_id,
            method: "manual".into(),
            reason: "synthetic".into(),
        },
    )
    .unwrap();
    app.configuration
        .confirm(
            &preview.kind,
            &preview.token,
            &preview.expected_etag,
            &preview.candidate_sha256,
        )
        .unwrap();
    let preview = naming::preview(
        &app.configuration,
        NamesIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            instance_id,
            point_ids: vec![point_id.clone()],
            address_only: false,
        },
    )
    .unwrap();
    app.configuration
        .confirm(
            &preview.kind,
            &preview.token,
            &preview.expected_etag,
            &preview.candidate_sha256,
        )
        .unwrap();
    let before = app.configuration.get().unwrap();
    assert!(before.workspace.instances[0].names_confirmation.is_some());
    assert!(before.workspace.instances[0].dbs[0]
        .address_confirmation
        .is_some());
    workspace = before.workspace.clone();
    let point = &mut workspace.instances[0].dbs[0].points[0];
    point.name = "ChangedName".into();
    point.byte = Some(4);
    point.display_names = Some(DisplayNames {
        zh_cn: "中文".into(),
        en_us: "English".into(),
    });
    point.description = Some("explicit".into());
    let submitted = workspace.clone();
    app.configuration
        .store
        .test_fault("after_save_commit")
        .unwrap();
    let result = queries::save(
        &app,
        SaveIntent {
            expected_etag: before.etag.clone(),
            workspace,
            confirm_points: vec![point_id],
        },
    );
    assert!(matches!(result, Err(e) if e == "save_receipt_unknown"));
    // 同一个 Store 的成功 Load 在已排队的 Save job 后执行；不是历史操作成功回执。
    let saved = queries::configuration(&app, ConfigurationQuery::default()).unwrap();
    let actual: Workspace = serde_json::from_value(saved["workspace"].clone()).unwrap();
    assert_ne!(saved["etag"], before.etag);
    assert_ne!(actual, submitted);
    assert!(actual.instances[0].names_confirmation.is_none());
    assert!(actual.instances[0].dbs[0].address_confirmation.is_none());
    let point = &actual.instances[0].dbs[0].points[0];
    assert!(point.confirmations.initial.is_some() && point.confirmations.policy.is_some());
    assert_eq!(point.display_names.as_ref().unwrap().zh_cn, "中文");
    assert_eq!(point.display_names.as_ref().unwrap().en_us, "English");
    assert_eq!(point.description.as_deref(), Some("explicit"));
    println!(
        "DS4_R2_CONFIRM_EVIDENCE:{}",
        json!({"beforeEtag":before.etag,"savedEtag":saved["etag"],"submitted":submitted,"saved":actual})
    );
    assert!(app.shutdown());
}

#[cfg(feature = "test-automation")]
#[test]
fn service_unknown_then_same_store_load_has_an_explicit_ordering_barrier() {
    use ds_runtime::services::queries;
    use std::{sync::mpsc, time::Duration};
    let root = owned_profile();
    let app = Arc::new(App::open(&root).unwrap());
    let before = app.configuration.get().unwrap();
    let workspace = fixture();
    app.configuration
        .store
        .test_fault("after_save_commit")
        .unwrap();
    let (start_tx, start_rx) = mpsc::channel();
    let (done_tx, done_rx) = mpsc::channel();
    let worker = app.clone();
    let expected = before.etag.clone();
    let submitted = workspace.clone();
    let thread = std::thread::spawn(move || {
        start_rx.recv().unwrap();
        let result = queries::save(
            &worker,
            SaveIntent {
                expected_etag: expected,
                workspace: submitted,
                confirm_points: vec![],
            },
        );
        done_tx.send(result).unwrap();
    });
    start_tx.send(()).unwrap();
    let receipt = done_rx.recv_timeout(Duration::from_secs(15)).unwrap();
    assert!(matches!(receipt, Err(e) if e == "save_receipt_unknown"));
    thread.join().unwrap();
    let same_profile = app.configuration.store.profile_id.clone();
    let loaded = app.configuration.get().unwrap();
    assert_ne!(loaded.etag, before.etag);
    assert_eq!(loaded.workspace, workspace);
    println!("DS4_R2_FIFO_EVIDENCE:receipt=save_receipt_unknown later_load=true same_profile={same_profile} before_etag={} loaded_etag={}", before.etag, loaded.etag);
    assert!(app.shutdown());
}

#[test]
#[ignore = "subprocess helper for task-owned profile lock test"]
fn ds4_profile_hold_probe() {
    use std::io::{self, Write};
    let path = PathBuf::from(std::env::var_os("DS4_HOLD_PROFILE").expect("owned profile"));
    let store = Store::open(&path).unwrap();
    println!("DS4_PROFILE_READY:{}", store.profile_id);
    io::stdout().flush().unwrap();
    let mut line = String::new();
    io::stdin().read_line(&mut line).unwrap();
    assert_eq!(line.trim(), "close");
    store.shutdown().unwrap();
}

#[test]
fn synthetic_reopen_requires_process_exit_lock_release_and_same_identity() {
    use std::{
        io::{BufRead, BufReader, Write},
        process::{Command, Stdio},
        sync::mpsc,
        time::Duration,
    };
    let root = owned_profile();
    let mut child = Command::new(std::env::current_exe().unwrap())
        .args([
            "--ignored",
            "--exact",
            "ds4_profile_hold_probe",
            "--nocapture",
        ])
        .env("DS4_HOLD_PROFILE", &root)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let output = child.stdout.take().unwrap();
    let (tx, rx) = mpsc::channel();
    let reader = std::thread::spawn(move || {
        for line in BufReader::new(output).lines().map_while(Result::ok) {
            if let Some(id) = line.split("DS4_PROFILE_READY:").nth(1) {
                let _ = tx.send(id.to_string());
            }
        }
    });
    let identity = rx
        .recv_timeout(Duration::from_secs(15))
        .expect("child profile identity");
    assert!(child.try_wait().unwrap().is_none());
    assert!(matches!(Store::open(&root), Err(e) if e == "profile_in_use"));
    writeln!(child.stdin.take().unwrap(), "close").unwrap();
    assert!(child.wait().unwrap().success());
    reader.join().unwrap();
    let reopened = Store::open(&root).unwrap();
    assert_eq!(reopened.profile_id, identity);
    assert_ne!(reopened.profile_id, uuid());
    assert!(reopened.load().is_ok());
    println!("DS4_REOPEN_EVIDENCE:old_exited=true lock_reacquired=true same_profile={identity}");
    reopened.shutdown().unwrap();
}

#[test]
fn synthetic_maximum_fields_and_capacity_rejections_preserve_the_original() {
    use ds_runtime::services::queries;
    let root = owned_profile();
    let app = App::open(&root).unwrap();
    let before = app.configuration.get().unwrap();
    let mut workspace: Workspace = serde_json::from_value(json!({"schemaVersion":1,"instances":[{
        "id":uuid(),"name":"Capacity","port":32196,"dbs":[{"id":uuid(),"name":"Synthetic","number":71,"length":65536,"manual":true,
            "points":[{"id":uuid(),"name":"P0","dataType":"INT","displayNames":{"zh-CN":"甲".repeat(85)+"a","en-US":"e".repeat(256)},"description":"d".repeat(500)}]}]
    }],"sourceVersions":[]})).unwrap();
    let point = workspace.instances[0].dbs[0].points[0].clone();
    workspace.instances[0].dbs[0].points = (0..4096)
        .map(|n| {
            let mut p = point.clone();
            p.id = uuid();
            p.name = format!("P{n}");
            p
        })
        .collect();
    let bytes = serde_json::to_vec(&workspace).unwrap().len();
    assert!(bytes < 16 * 1024 * 1024);
    configuration::validate(&workspace).unwrap();
    let mut too_many = workspace.clone();
    too_many.instances[0].dbs[0].points.push(point);
    assert_eq!(
        queries::save(
            &app,
            SaveIntent {
                expected_etag: before.etag.clone(),
                workspace: too_many,
                confirm_points: vec![]
            }
        )
        .unwrap_err(),
        "point_capacity"
    );
    let mut too_large = workspace.clone();
    too_large.instances.push(workspace.instances[0].clone());
    too_large.instances.push(workspace.instances[0].clone());
    assert!(serde_json::to_vec(&too_large).unwrap().len() > 16 * 1024 * 1024);
    assert_eq!(
        queries::save(
            &app,
            SaveIntent {
                expected_etag: before.etag.clone(),
                workspace: too_large,
                confirm_points: vec![]
            }
        )
        .unwrap_err(),
        "configuration_capacity"
    );
    let unchanged = app.configuration.get().unwrap();
    assert_eq!(unchanged.etag, before.etag);
    assert_eq!(unchanged.workspace, before.workspace);
    let result = queries::save(
        &app,
        SaveIntent {
            expected_etag: before.etag.clone(),
            workspace: workspace.clone(),
            confirm_points: vec![],
        },
    );
    assert!(
        result.is_ok()
            || matches!(&result, Err(e) if e == "save_receipt_unknown" || e == "save_commit_unknown")
    );
    let actual = app.configuration.get().unwrap();
    let committed = actual.workspace == workspace;
    if result.is_ok() {
        assert!(committed);
    }
    println!(
        "DS4_R2_CAPACITY_EVIDENCE:bytes={bytes} result={result:?} committed={committed} etag={}",
        actual.etag
    );
    assert!(app.shutdown());
}
