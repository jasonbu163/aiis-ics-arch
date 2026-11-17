//! DS-003 合成 profile：保存版本、停用点、目录冲突和只读导出证据。
use ds_runtime::{
    app::App,
    domain::{
        configuration::{self, uuid, Workspace},
        layout,
        plc_catalog::{self, Target},
    },
    services::catalog_export::{self, PreviewIntent, RevisionIntent, TokenIntent},
};
use serde_json::{json, Value};
use std::{fs, path::PathBuf};

fn root() -> PathBuf {
    let root =
        PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("explicit synthetic test root"))
            .join(uuid());
    fs::create_dir_all(&root).unwrap();
    root
}
fn fixture() -> Workspace {
    let mut workspace: Workspace = serde_json::from_value(json!({"schemaVersion":1,"sourceVersions":[],"instances":[
        {"id":uuid(),"name":"DS003 synthetic","host":"127.0.0.1","port":32194,"dbs":[
            {"id":uuid(),"name":"DB one","number":21,"length":24,"manual":true,"enabled":true,"points":[
                {"id":uuid(),"name":"Ready","displayName":"旧名称","displayNames":{"zh-CN":"就绪","en-US":"Ready"},"description":"独立描述","dataType":"BOOL","byte":0,"bit":1,"manual":true},
                {"id":uuid(),"name":"Count","dataType":"INT","byte":2,"manual":true},
                {"id":uuid(),"name":"Temperature","displayNames":{"zh-CN":"温度","en-US":""},"dataType":"REAL","byte":4,"manual":true,"enabled":false},
                {"id":uuid(),"name":"Text","dataType":"STRING[10]","byte":8,"manual":true}
            ]},
            {"id":uuid(),"name":"Disabled DB","number":22,"length":2,"manual":true,"enabled":false,"points":[
                {"id":uuid(),"name":"DisabledDbPoint","dataType":"INT","byte":0,"manual":true,"enabled":false}
            ]}
        ]},
        {"id":uuid(),"name":"Second synthetic","port":32195,"dbs":[{"id":uuid(),"name":"DB two","number":23,"length":2,"manual":true,"points":[{"id":uuid(),"name":"Other","dataType":"INT","byte":0,"manual":true}]}]}
    ]})).unwrap();
    for instance in &mut workspace.instances {
        for db in &mut instance.dbs {
            db.address_confirmation = Some(configuration::AddressConfirmation {
                structure_sha256: layout::structure_signature(db),
                layout_sha256: layout::layout_signature(db),
                method: "manual".into(),
                reason: "synthetic".into(),
            });
        }
        instance.names_confirmation = Some(layout::names_signature(instance));
    }
    workspace
}
fn target(id: &str) -> Target {
    Target {
        instance_id: id.into(),
        host: "127.0.0.1".into(),
        port: 32194,
        rack: 0,
        slot: 1,
        connection_confirmed: true,
        loaded_difference_confirmed: true,
    }
}
fn setup() -> (PathBuf, App, Workspace, String) {
    let root = root();
    let app = App::open(&root).unwrap();
    let workspace = fixture();
    let draft = app.configuration.store.load().unwrap();
    let saved = app
        .configuration
        .store
        .save(&draft.etag, workspace.clone())
        .unwrap();
    let revision = app
        .configuration
        .store
        .publish(&saved.etag)
        .unwrap()
        .revision_id
        .unwrap();
    (root, app, workspace, revision)
}
fn prepare(app: &App, revision: &str, targets: Vec<Target>) -> Value {
    catalog_export::preview(
        app,
        PreviewIntent {
            revision_id: revision.into(),
            targets,
        },
    )
    .unwrap()
}
fn token(value: &Value) -> String {
    value["token"].as_str().unwrap().into()
}
fn teardown(root: PathBuf, app: App) {
    assert!(app.shutdown());
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn complete_saved_revision_includes_disabled_points_metadata_and_original_digest() {
    let (root, app, workspace, revision) = setup();
    let instance = &workspace.instances[0];
    let original = app
        .configuration
        .store
        .revision_snapshot(&revision)
        .unwrap();
    let before = app.configuration.store.load().unwrap();
    let selections = app.configuration.store.selections().unwrap();
    let mut changed = before.workspace.clone();
    changed.instances[0].name = "unsaved later draft".into();
    app.configuration
        .store
        .save(&before.etag, changed.clone())
        .unwrap();
    let after_save = app.configuration.store.load().unwrap();
    let facts = catalog_export::inspect(
        &app,
        RevisionIntent {
            revision_id: revision.clone(),
        },
    )
    .unwrap();
    assert_eq!(facts["instances"][0]["name"], "DS003 synthetic");
    assert!(facts["instances"][0]["loadedRevision"].is_null());
    let preview = prepare(&app, &revision, vec![target(&instance.id)]);
    let row = &preview["rows"][0];
    assert_eq!(row["issues"], json!([]));
    let doc = &row["document"];
    assert_eq!(doc["format"], "aiis.plc_points");
    assert_eq!(
        doc["export"]["payload_sha256"],
        configuration::hash_bytes(&original.payload)
    );
    assert_eq!(doc["export"]["revision_id"], revision);
    assert_eq!(doc["plc"]["name"], "DS003 synthetic");
    assert_eq!(doc["dbs"][0]["points"].as_array().unwrap().len(), 4);
    assert_eq!(doc["dbs"][1]["source_enabled"], false);
    assert_eq!(doc["dbs"][1]["points"][0]["source_enabled"], false);
    assert_eq!(doc["dbs"][0]["points"][0]["display_name"], "旧名称");
    assert_eq!(
        doc["dbs"][0]["points"][0]["display_names"]["en-US"],
        "Ready"
    );
    assert_eq!(doc["dbs"][0]["points"][0]["description"], "独立描述");
    assert_eq!(
        doc["dbs"][0]["points"][1]["display_names"],
        json!({"zh-CN":"","en-US":""})
    );
    assert_eq!(doc["dbs"][0]["points"][1]["description"], "");
    assert!(doc["dbs"][0]["points"][1].get("bit").is_none());
    assert!(doc.to_string().find("policy").is_none());
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    catalog_export::choose_directory(&app, &token(&preview), &out).unwrap();
    let result = catalog_export::commit(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    assert_eq!(result["rows"][0]["result"], "written");
    assert_eq!(result["committed"], true);
    let bytes = fs::read(out.join(format!("{}.json", instance.id))).unwrap();
    assert_eq!(
        configuration::hash_bytes(&bytes),
        result["rows"][0]["fileSha256"].as_str().unwrap()
    );
    assert_eq!(serde_json::from_slice::<Value>(&bytes).unwrap(), *doc);
    assert_eq!(
        app.configuration.store.load().unwrap().workspace,
        after_save.workspace
    );
    assert_eq!(
        app.configuration.store.selections().unwrap().len(),
        selections.len()
    );
    assert_eq!(
        app.configuration
            .store
            .revision_snapshot(&revision)
            .unwrap()
            .payload,
        original.payload
    );
    teardown(root, app);
}
#[test]
fn disabled_overlap_bad_connection_and_unconfirmed_loaded_are_located() {
    let (root, app, mut workspace, revision) = setup();
    let i = &mut workspace.instances[0];
    i.dbs[1].points[0].byte = Some(99);
    let snap = app
        .configuration
        .store
        .revision_snapshot(&revision)
        .unwrap();
    let issues = plc_catalog::build(
        &workspace,
        &workspace.instances[0],
        &app.configuration.store.profile_id,
        &revision,
        &snap.payload,
        "2026-11-17T09:00:00+08:00",
        &target(&workspace.instances[0].id),
    )
    .unwrap_err();
    assert!(issues.iter().any(|v| v.code == "catalog_address"
        && v.point_id.as_deref() == Some(workspace.instances[0].dbs[1].points[0].id.as_str())));
    let mut bad = target(&workspace.instances[0].id);
    bad.host = "0.0.0.0".into();
    bad.loaded_difference_confirmed = false;
    let preview = prepare(
        &app,
        &revision,
        vec![bad, target(&workspace.instances[1].id)],
    );
    let issues = preview["rows"][0]["issues"].as_array().unwrap();
    assert!(issues.iter().any(|v| v["code"] == "catalog_connection"));
    assert!(issues
        .iter()
        .any(|v| v["code"] == "catalog_loaded_confirmation"));
    assert!(preview["rows"][1]["document"].is_object());
    catalog_export::cancel(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    teardown(root, app);
}
#[test]
fn existing_and_concurrently_created_targets_are_never_overwritten() {
    let (root, app, workspace, revision) = setup();
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    let id = &workspace.instances[0].id;
    let dest = out.join(format!("{id}.json"));
    fs::write(&dest, b"user original").unwrap();
    let preview = prepare(&app, &revision, vec![target(id)]);
    let directory = catalog_export::choose_directory(&app, &token(&preview), &out).unwrap();
    assert_eq!(directory["rows"][0]["conflict"], true);
    let result = catalog_export::commit(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    assert_eq!(result["rows"][0]["errorCode"], "catalog_target_exists");
    assert_eq!(result["committed"], false);
    assert_eq!(fs::read(&dest).unwrap(), b"user original");
    fs::remove_file(&dest).unwrap();
    let next = prepare(&app, &revision, vec![target(id)]);
    catalog_export::choose_directory(&app, &token(&next), &out).unwrap();
    fs::write(&dest, b"concurrent file").unwrap();
    let result = catalog_export::commit(
        &app,
        TokenIntent {
            token: token(&next),
        },
    )
    .unwrap();
    assert_eq!(result["rows"][0]["errorCode"], "catalog_target_changed");
    assert_eq!(result["committed"], false);
    assert_eq!(fs::read(&dest).unwrap(), b"concurrent file");
    assert_eq!(fs::read_dir(&out).unwrap().count(), 1);
    teardown(root, app);
}
#[test]
fn tsap_and_string_contract_reject_unsupported_values_without_fallback() {
    let (root, app, workspace, revision) = setup();
    let mut nondefault = target(&workspace.instances[0].id);
    nondefault.slot = 2;
    let preview = prepare(&app, &revision, vec![nondefault]);
    assert_eq!(preview["rows"][0]["nonDefaultTsap"], true);
    assert_eq!(
        preview["rows"][0]["document"]["plc"]["connection"]["remote_tsap"],
        257
    );
    let mut invalid = workspace.clone();
    invalid.instances[0].dbs[0].points[3].data_type = "STRING[010]".into();
    let snap = app
        .configuration
        .store
        .revision_snapshot(&revision)
        .unwrap();
    let issues = plc_catalog::build(
        &invalid,
        &invalid.instances[0],
        &app.configuration.store.profile_id,
        &revision,
        &snap.payload,
        "2026-11-17T09:00:00+08:00",
        &target(&workspace.instances[0].id),
    )
    .unwrap_err();
    assert!(issues.iter().any(|v| v.code == "catalog_type"));
    catalog_export::cancel(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    teardown(root, app);
}
#[test]
fn removed_revision_and_replaced_directory_invalidate_preview() {
    let (root, app, workspace, revision) = setup();
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    let p = prepare(&app, &revision, vec![target(&workspace.instances[0].id)]);
    catalog_export::choose_directory(&app, &token(&p), &out).unwrap();
    let moved = root.join("moved");
    fs::rename(&out, &moved).unwrap();
    fs::create_dir(&out).unwrap();
    assert_eq!(
        catalog_export::commit(&app, TokenIntent { token: token(&p) }).unwrap_err(),
        "catalog_preview_stale"
    );
    assert_eq!(fs::read_dir(&out).unwrap().count(), 0);
    assert_eq!(fs::read_dir(&moved).unwrap().count(), 0);
    let p = prepare(&app, &revision, vec![target(&workspace.instances[0].id)]);
    catalog_export::choose_directory(&app, &token(&p), &out).unwrap();
    let current = app.configuration.store.load().unwrap();
    let mut next = current.workspace;
    next.instances[0].name = "later".into();
    let saved = app.configuration.store.save(&current.etag, next).unwrap();
    app.configuration.store.publish(&saved.etag).unwrap();
    let current = app.configuration.store.load().unwrap();
    let deletion = ds_runtime::services::versions::preview_delete(
        &app,
        ds_runtime::services::versions::DeleteIntent {
            expected_etag: current.etag.clone(),
            revision_ids: vec![revision.clone()],
        },
    )
    .unwrap();
    ds_runtime::services::versions::confirm(
        &app,
        "delete_revisions",
        ds_runtime::services::versions::VersionConfirmation {
            expected_etag: current.etag,
            token: deletion.token,
            candidate_sha256: deletion.candidate_sha256,
            release_rollback: false,
        },
    )
    .unwrap();
    assert_eq!(
        catalog_export::commit(&app, TokenIntent { token: token(&p) }).unwrap_err(),
        "revision_not_found"
    );
    assert_eq!(fs::read_dir(&out).unwrap().count(), 0);
    teardown(root, app);
}
#[test]
fn duplicate_confirmation_cannot_write_twice() {
    let (root, app, workspace, revision) = setup();
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    let p = prepare(&app, &revision, vec![target(&workspace.instances[0].id)]);
    catalog_export::choose_directory(&app, &token(&p), &out).unwrap();
    let ticket = token(&p);
    std::thread::scope(|scope| {
        let a = scope.spawn(|| {
            catalog_export::commit(
                &app,
                TokenIntent {
                    token: ticket.clone(),
                },
            )
        });
        let b = scope.spawn(|| {
            catalog_export::commit(
                &app,
                TokenIntent {
                    token: ticket.clone(),
                },
            )
        });
        let results = [a.join().unwrap(), b.join().unwrap()];
        assert_eq!(results.iter().filter(|r| r.is_ok()).count(), 1);
        assert_eq!(
            results
                .iter()
                .filter(|r| r.as_ref().is_err_and(|e| e == "catalog_preview_stale"))
                .count(),
            1
        );
    });
    assert_eq!(fs::read_dir(&out).unwrap().count(), 1);
    teardown(root, app);
}
#[cfg(unix)]
#[test]
fn symlink_target_is_a_conflict_and_referent_is_preserved() {
    use std::os::unix::fs::symlink;
    let (root, app, workspace, revision) = setup();
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    let referent = root.join("unrelated");
    fs::write(&referent, b"untouched").unwrap();
    let id = &workspace.instances[0].id;
    let dest = out.join(format!("{id}.json"));
    symlink(&referent, &dest).unwrap();
    let p = prepare(&app, &revision, vec![target(id)]);
    let state = catalog_export::choose_directory(&app, &token(&p), &out).unwrap();
    assert_eq!(state["rows"][0]["conflict"], true);
    let result = catalog_export::commit(&app, TokenIntent { token: token(&p) }).unwrap();
    assert_eq!(result["rows"][0]["errorCode"], "catalog_target_exists");
    assert_eq!(fs::read(referent).unwrap(), b"untouched");
    assert!(fs::symlink_metadata(dest).unwrap().file_type().is_symlink());
    teardown(root, app);
}
#[test]
fn imported_tia_paths_and_explicit_description_are_not_inferred() {
    use ds_runtime::services::{
        configuration::SaveIntent,
        layout::{self, LayoutIntent},
        naming::{self, NamesIntent},
        source_import::{self, BindingIntent, Declaration, ImportFile, ImportIntent},
    };
    let root = root();
    let app = App::open(&root).unwrap();
    let id = uuid();
    let initial = app.configuration.get().unwrap();
    let mut workspace = initial.workspace;
    workspace.instances.push(
        serde_json::from_value(json!({"id":id,"name":"TIA synthetic","port":32194})).unwrap(),
    );
    app.configuration
        .save(SaveIntent {
            expected_etag: initial.etag,
            workspace,
            confirm_points: vec![],
        })
        .unwrap();
    let source=b"DATA_BLOCK \"Synthetic\"\n{ S7_Optimized_Access := 'FALSE' }\nVAR\nReady:BOOL;\nCount:INT;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK".to_vec();
    let imported = source_import::preview(
        &app.configuration,
        ImportIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            instance_id: id.clone(),
            files: vec![ImportFile {
                input_id: "synthetic".into(),
                name: "synthetic.db".into(),
                bytes: source,
                lineage_id: None,
            }],
            bindings: vec![BindingIntent {
                db_id: None,
                number: 31,
                declaration: Declaration {
                    input_id: "synthetic".into(),
                    declaration_index: 0,
                },
                udt_closure: vec![],
            }],
        },
    )
    .unwrap()
    .preview
    .unwrap();
    app.configuration
        .confirm(
            &imported.kind,
            &imported.token,
            &imported.expected_etag,
            &imported.candidate_sha256,
        )
        .unwrap();
    let state = app.configuration.get().unwrap();
    let db_id = state.workspace.instances[0].dbs[0].id.clone();
    let layout = layout::preview(
        &app.configuration,
        LayoutIntent {
            expected_etag: state.etag,
            instance_id: id.clone(),
            db_id,
            method: "standard".into(),
            reason: String::new(),
        },
    )
    .unwrap();
    app.configuration
        .confirm(
            &layout.kind,
            &layout.token,
            &layout.expected_etag,
            &layout.candidate_sha256,
        )
        .unwrap();
    let state = app.configuration.get().unwrap();
    let ids = state.workspace.instances[0].dbs[0]
        .points
        .iter()
        .map(|p| p.id.clone())
        .collect();
    let names = naming::preview(
        &app.configuration,
        NamesIntent {
            expected_etag: state.etag,
            instance_id: id.clone(),
            point_ids: ids,
            address_only: false,
        },
    )
    .unwrap();
    app.configuration
        .confirm(
            &names.kind,
            &names.token,
            &names.expected_etag,
            &names.candidate_sha256,
        )
        .unwrap();
    let state = app.configuration.get().unwrap();
    let mut workspace = state.workspace;
    workspace.instances[0].dbs[0].points[1].description = Some("independent note".into());
    let saved = app
        .configuration
        .save(SaveIntent {
            expected_etag: state.etag,
            workspace,
            confirm_points: vec![],
        })
        .unwrap();
    let revision = app
        .configuration
        .store
        .publish(&saved.etag)
        .unwrap()
        .revision_id
        .unwrap();
    let preview = prepare(&app, &revision, vec![target(&id)]);
    let points = preview["rows"][0]["document"]["dbs"][0]["points"]
        .as_array()
        .unwrap();
    assert_eq!(points[0]["source_path"], "Ready");
    assert_eq!(points[1]["source_path"], "Count");
    assert_eq!(points[0]["description"], "");
    assert_eq!(points[1]["description"], "independent note");
    catalog_export::cancel(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    teardown(root, app);
}
#[test]
fn invalid_endpoint_numbers_are_reported_per_instance_without_valid_fallback() {
    let (root, app, workspace, revision) = setup();
    let ids = [
        workspace.instances[0].id.clone(),
        workspace.instances[1].id.clone(),
    ];
    let valid = |id: &str| json!({"instanceId":id,"host":"127.0.0.1","port":32194,"rack":0,"slot":1,"connectionConfirmed":true,"loadedDifferenceConfirmed":true});
    for field in ["port", "rack", "slot"] {
        for bad in [
            Value::Null,
            json!(1.0),
            json!(1.5),
            json!(-1),
            json!("1"),
            json!(true),
        ] {
            let mut first = valid(&ids[0]);
            first[field] = bad;
            let intent: PreviewIntent = serde_json::from_value(
                json!({"revisionId":revision,"targets":[first,valid(&ids[1])]}),
            )
            .unwrap();
            let preview = catalog_export::preview(&app, intent).unwrap();
            assert!(
                preview["rows"][0]["issues"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .any(|v| v["code"] == "catalog_connection"),
                "{field}"
            );
            assert!(preview["rows"][0]["document"].is_null());
            assert!(preview["rows"][1]["document"].is_object());
            catalog_export::cancel(
                &app,
                TokenIntent {
                    token: token(&preview),
                },
            )
            .unwrap();
        }
        let mut missing = valid(&ids[0]);
        missing.as_object_mut().unwrap().remove(field);
        let intent: PreviewIntent = serde_json::from_value(
            json!({"revisionId":revision,"targets":[missing,valid(&ids[1])]}),
        )
        .unwrap();
        let preview = catalog_export::preview(&app, intent).unwrap();
        assert!(preview["rows"][0]["issues"]
            .as_array()
            .unwrap()
            .iter()
            .any(|v| v["code"] == "catalog_connection"));
        catalog_export::cancel(
            &app,
            TokenIntent {
                token: token(&preview),
            },
        )
        .unwrap();
    }
    let mut invalid = valid(&ids[0]);
    invalid["port"] = Value::Null;
    let intent: PreviewIntent =
        serde_json::from_value(json!({"revisionId":revision,"targets":[invalid,valid(&ids[1])]}))
            .unwrap();
    let preview = catalog_export::preview(&app, intent).unwrap();
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    catalog_export::choose_directory(&app, &token(&preview), &out).unwrap();
    let result = catalog_export::commit(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    assert_eq!(result["rows"][0]["result"], "failed");
    assert_eq!(result["rows"][1]["result"], "written");
    assert_eq!(result["committed"], true);
    assert!(!out.join(format!("{}.json", ids[0])).exists());
    assert!(out.join(format!("{}.json", ids[1])).exists());
    teardown(root, app);
}

#[test]
fn qa1_f01_non_rfc_saved_point_blocks_only_its_instance() {
    let (root, app, mut workspace, _) = setup();
    println!("owned_profile={}", root.display());
    let invalid = "55555555-5555-4555-0555-555555555555";
    let instance = &mut workspace.instances[0];
    let db = &mut instance.dbs[1];
    db.points[0].id = invalid.into();
    db.address_confirmation = Some(configuration::AddressConfirmation {
        structure_sha256: layout::structure_signature(db),
        layout_sha256: layout::layout_signature(db),
        method: "manual".into(),
        reason: "synthetic QA1-F01".into(),
    });
    instance.names_confirmation = Some(layout::names_signature(instance));
    let invalid_instance = workspace.instances[0].id.clone();
    let invalid_db = workspace.instances[0].dbs[1].id.clone();
    let valid_instance = workspace.instances[1].id.clone();
    let before = app.configuration.store.load().unwrap();
    let saved = app
        .configuration
        .store
        .save(&before.etag, workspace)
        .unwrap();
    let revision = app
        .configuration
        .store
        .publish(&saved.etag)
        .unwrap()
        .revision_id
        .unwrap();
    let source = app
        .configuration
        .store
        .revision_snapshot(&revision)
        .unwrap();
    assert_eq!(source.workspace.instances[0].dbs[1].points[0].id, invalid);
    let preview = prepare(
        &app,
        &revision,
        vec![target(&invalid_instance), target(&valid_instance)],
    );
    assert!(preview["rows"][0]["issues"]
        .as_array()
        .unwrap()
        .iter()
        .any(|issue| issue["code"] == "catalog_identity"
            && issue["dbId"] == invalid_db
            && issue["pointId"] == invalid));
    assert!(preview["rows"][0]["document"].is_null());
    assert!(preview["rows"][1]["document"].is_object());
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    catalog_export::choose_directory(&app, &token(&preview), &out).unwrap();
    let receipt = catalog_export::commit(
        &app,
        TokenIntent {
            token: token(&preview),
        },
    )
    .unwrap();
    assert_eq!(receipt["rows"][0]["result"], "failed");
    assert_eq!(receipt["rows"][1]["result"], "written");
    assert!(!out.join(format!("{invalid_instance}.json")).exists());
    assert!(out.join(format!("{valid_instance}.json")).is_file());
    assert_eq!(
        app.configuration
            .store
            .revision_snapshot(&revision)
            .unwrap()
            .payload,
        source.payload
    );
    teardown(root, app);
}

#[test]
fn catalog_requires_canonical_rfc_v4_for_every_identity_role() {
    let workspace = fixture();
    let source = serde_json::to_vec(&workspace).unwrap();
    let good_profile = uuid();
    let good_revision = uuid();
    let timestamp = "2026-11-17T09:00:00+08:00";
    for variant in ['8', '9', 'a', 'b'] {
        let valid = format!("55555555-5555-4555-{variant}555-555555555555");
        assert!(plc_catalog::build(
            &workspace,
            &workspace.instances[0],
            &valid,
            &good_revision,
            &source,
            timestamp,
            &target(&workspace.instances[0].id)
        )
        .is_ok());
    }
    for invalid in [
        "55555555-5555-4555-0555-555555555555", // NCS
        "55555555-5555-4555-c555-555555555555", // Microsoft
        "55555555-5555-4555-e555-555555555555", // future
        "55555555-5555-1555-8555-555555555555", // wrong version
        "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA", // noncanonical uppercase
        "55555555555545558555555555555555",     // noncanonical compact form
    ] {
        for (profile, revision) in [
            (invalid, good_revision.as_str()),
            (good_profile.as_str(), invalid),
        ] {
            let issues = plc_catalog::build(
                &workspace,
                &workspace.instances[0],
                profile,
                revision,
                &source,
                timestamp,
                &target(&workspace.instances[0].id),
            )
            .unwrap_err();
            assert!(
                issues.iter().any(|issue| issue.code == "catalog_identity"),
                "{invalid}"
            );
        }
        for role in ["instance", "db", "point"] {
            let mut candidate = workspace.clone();
            let instance = &mut candidate.instances[0];
            match role {
                "instance" => instance.id = invalid.into(),
                "db" => instance.dbs[0].id = invalid.into(),
                "point" => instance.dbs[0].points[0].id = invalid.into(),
                _ => unreachable!(),
            }
            let issues = plc_catalog::build(
                &candidate,
                &candidate.instances[0],
                &good_profile,
                &good_revision,
                &source,
                timestamp,
                &target(&candidate.instances[0].id),
            )
            .unwrap_err();
            let code = if role == "db" {
                "catalog_db_invalid"
            } else {
                "catalog_identity"
            };
            assert!(
                issues.iter().any(|issue| issue.code == code),
                "{role}: {invalid}"
            );
        }
    }
}
