//! DS-005 合成目录：原文、身份映射、监听、确认、保存/重开及反例；不监听网络。
use ds_runtime::{
    app::App,
    domain::{
        configuration::{self, uuid},
        plc_catalog::{self, Target},
    },
    services::{
        catalog_export,
        catalog_import::{self, CancelIntent, ConfirmIntent, PreviewIntent},
        configuration::SaveIntent,
        layout::{self, LayoutIntent},
        naming::{self, NamesIntent},
    },
};
use serde_json::{json, Value};
use std::{fs, path::PathBuf};
fn root() -> PathBuf {
    let p = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("explicit synthetic root"))
        .join(uuid());
    fs::create_dir_all(&p).unwrap();
    p
}
fn document(producer: &str) -> Value {
    let mut d = json!({"format":"aiis.plc_points","schema_version":1,
      "origin":{"kind":"data_acquisition_agent","profile_id":uuid(),"plc_id":uuid()},
      "export":{"producer":producer,"profile_id":uuid(),"config_state":if producer=="device_simulator"{"saved_revision"}else{"saved_draft"},"revision_id":uuid(),"payload_sha256":"a".repeat(64),"exported_at":"2026-11-17T12:00:00+08:00"},
      "plc":{"name":"synthetic","protocol":"s7","connection":{"host":"192.0.2.1","port":102,"rack":0,"slot":1,"local_tsap":0x222,"remote_tsap":0x102}},
      "dbs":[{"id":uuid(),"name":"DB one","number":21,"size_bytes":8,"points":[
        {"id":uuid(),"name":"Ready","display_name":"x".repeat(256),"display_names":{"zh-CN":"就绪","en-US":"Ready"},"description":"独立说明","source_path":"payload.ready","data_type":"BOOL","byte_offset":0,"bit":0,"source_enabled":true},
        {"id":uuid(),"name":"Count","display_names":{"zh-CN":"","en-US":""},"data_type":"INT","byte_offset":2,"source_enabled":false},
        {"id":uuid(),"name":"Temp","data_type":"REAL","byte_offset":4,"source_enabled":true}]},
       {"id":uuid(),"name":"DB two","number":22,"size_bytes":2,"points":[{"id":uuid(),"name":"Other","data_type":"INT","byte_offset":0,"source_enabled":true}]}]});
    if producer == "device_simulator" {
        for db in d["dbs"].as_array_mut().unwrap() {
            db["source_enabled"] = json!(true);
        }
    }
    d
}
fn choose(app: &App, path: &std::path::Path) -> String {
    catalog_import::choose(app, path).unwrap()["fileToken"]
        .as_str()
        .unwrap()
        .into()
}
fn preview(
    app: &App,
    file: &str,
    port: u16,
) -> Result<ds_runtime::services::configuration::Preview, String> {
    catalog_import::preview(
        app,
        PreviewIntent {
            file_token: file.into(),
            expected_etag: app.configuration.get()?.etag,
            host: "127.0.0.1".into(),
            port,
            rack: 0,
            slot: 2,
            connection_confirmed: true,
        },
    )
}
fn confirm(
    app: &App,
    file: &str,
    p: &ds_runtime::services::configuration::Preview,
) -> Result<ds_runtime::infrastructure::config_store::SaveResult, String> {
    catalog_import::confirm(
        app,
        ConfirmIntent {
            file_token: file.into(),
            token: p.token.clone(),
            expected_etag: p.expected_etag.clone(),
            candidate_sha256: p.candidate_sha256.clone(),
        },
    )
}
fn finish(app: &App, p: &ds_runtime::services::configuration::Preview) {
    app.configuration
        .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
        .unwrap();
}
#[test]
fn both_producers_save_reopen_and_export_preserve_external_identities() {
    for producer in ["device_simulator", "data_acquisition_agent"] {
        let root = root();
        let path = root.join("source.json");
        let mut doc = document(producer);
        doc["dbs"][0]["points"][1]["source_path"] = json!("");
        let bytes = serde_json::to_vec_pretty(&doc).unwrap();
        fs::write(&path, &bytes).unwrap();
        let app = App::open(&root.join("profile")).unwrap();
        let file = choose(&app, &path);
        let p = preview(&app, &file, 32194).unwrap();
        assert_eq!(p.details["fileSha256"], configuration::hash_bytes(&bytes));
        let saved = confirm(&app, &file, &p).unwrap();
        let state = app.configuration.get().unwrap();
        let instance = &state.workspace.instances[0];
        let id = instance.id.clone();
        assert_eq!(state.etag, saved.etag);
        assert_eq!(state.workspace.source_versions[0].bytes, bytes);
        assert!(instance
            .dbs
            .iter()
            .all(|d| !d.enabled && d.points.iter().all(|p| !p.enabled)));
        assert_eq!(instance.calling_tsap, 0x222);
        assert_eq!(instance.called_tsap(), 0x102);
        let mut altered = state.workspace.clone();
        altered.instances[0].dbs[0].points[0].byte = Some(1);
        assert!(app
            .configuration
            .save(SaveIntent {
                expected_etag: state.etag.clone(),
                workspace: altered,
                confirm_points: vec![]
            })
            .is_err());
        let mut forged = state.workspace.clone();
        forged.instances[0].catalog.as_mut().unwrap().dbs[0].points[0].catalog_point_id = uuid();
        assert!(configuration::validate(&forged).is_err());
        let mut forged = state.workspace.clone();
        forged.source_versions[0].bytes.push(b' ');
        assert!(configuration::validate(&forged).is_err());
        let db_ids = instance
            .dbs
            .iter()
            .map(|d| d.id.clone())
            .collect::<Vec<_>>();
        for db_id in &db_ids {
            let current = app.configuration.get().unwrap();
            let p = layout::preview(
                &app.configuration,
                LayoutIntent {
                    expected_etag: current.etag,
                    instance_id: id.clone(),
                    db_id: db_id.clone(),
                    method: "manual".into(),
                    reason: "synthetic catalog review".into(),
                },
            )
            .unwrap();
            finish(&app, &p);
        }
        let current = app.configuration.get().unwrap();
        let ids = current.workspace.instances[0]
            .dbs
            .iter()
            .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
            .collect();
        let p = naming::preview(
            &app.configuration,
            NamesIntent {
                expected_etag: current.etag,
                instance_id: id.clone(),
                point_ids: ids,
                address_only: false,
            },
        )
        .unwrap();
        finish(&app, &p);
        let current = app.configuration.get().unwrap();
        let revision = app
            .configuration
            .store
            .publish(&current.etag)
            .unwrap()
            .revision_id
            .unwrap();
        assert!(app.shutdown());
        drop(app);
        let app = App::open(&root.join("profile")).unwrap();
        let saved = app
            .configuration
            .store
            .revision_snapshot(&revision)
            .unwrap();
        assert_eq!(saved.workspace.source_versions[0].bytes, bytes);
        let exported = catalog_export::preview(
            &app,
            catalog_export::PreviewIntent {
                revision_id: revision.clone(),
                filenames: [(id.clone(), format!("{id}.json"))].into(),
                targets: vec![Target {
                    instance_id: id,
                    host: "127.0.0.1".into(),
                    port: 32194,
                    rack: 0,
                    slot: 2,
                    connection_confirmed: true,
                    loaded_difference_confirmed: true,
                }],
            },
        )
        .unwrap();
        assert_eq!(exported["rows"][0]["issues"], json!([]));
        let result = &exported["rows"][0]["document"];
        assert_eq!(result["origin"], doc["origin"]);
        assert_eq!(result["export"]["producer"], "device_simulator");
        assert_eq!(result["export"]["revision_id"], revision);
        assert_eq!(
            result["export"]["payload_sha256"],
            configuration::hash_bytes(&saved.payload)
        );
        for n in 0..2 {
            assert_eq!(result["dbs"][n]["id"], doc["dbs"][n]["id"]);
            assert_eq!(result["dbs"][n]["source_enabled"], false);
            for m in 0..doc["dbs"][n]["points"].as_array().unwrap().len() {
                let out = &result["dbs"][n]["points"][m];
                let orig = &doc["dbs"][n]["points"][m];
                for k in ["id", "name", "data_type", "byte_offset"] {
                    assert_eq!(out[k], orig[k], "{k}");
                }
                assert_eq!(out["source_enabled"], false);
            }
        }
        assert_eq!(
            result["dbs"][0]["points"][0]["display_name"],
            "x".repeat(256)
        );
        assert_eq!(
            result["dbs"][0]["points"][0]["display_names"],
            doc["dbs"][0]["points"][0]["display_names"]
        );
        assert_eq!(result["dbs"][0]["points"][0]["description"], "独立说明");
        assert_eq!(
            result["dbs"][0]["points"][0]["source_path"],
            "payload.ready"
        );
        assert_eq!(result["dbs"][0]["points"][1]["source_path"], "");
        assert_eq!(result["dbs"][0]["points"][1]["description"], "");
        assert!(app.shutdown());
        fs::remove_dir_all(root).unwrap();
    }
}

#[test]
fn archived_source_metadata_tamper_blocks_readback() {
    let root = root();
    let path = root.join("source.json");
    fs::write(
        &path,
        serde_json::to_vec(&document("data_acquisition_agent")).unwrap(),
    )
    .unwrap();
    let profile = root.join("profile");
    let app = App::open(&profile).unwrap();
    let file = choose(&app, &path);
    let p = preview(&app, &file, 32194).unwrap();
    confirm(&app, &file, &p).unwrap();
    assert!(app.shutdown());
    drop(app);
    let c = rusqlite::Connection::open(profile.join("device-simulator-v1/config.sqlite")).unwrap();
    assert_eq!(
        c.execute("UPDATE source_versions SET metadata=X'7B7D'", [])
            .unwrap(),
        1
    );
    drop(c);
    assert_eq!(App::open(&profile).err().unwrap(), "storage_reference");
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn parser_rejects_invalid_disabled_points_and_closed_format() {
    let d = document("data_acquisition_agent");
    let valid = serde_json::to_vec(&d).unwrap();
    assert!(plc_catalog::parse(&valid).is_ok());
    let mut bads = Vec::new();
    for (path, value) in [
        ("/dbs/0/points/1/data_type", json!("LREAL")),
        ("/dbs/0/points/1/byte_offset", json!(0)),
        ("/dbs/0/points/0/bit", json!(8)),
        ("/dbs/0/points/0/display_name", json!("x".repeat(257))),
        ("/dbs/0/points/0/display_names", Value::Null),
        ("/export/exported_at", json!("2026-02-30T12:00:00+08:00")),
        ("/plc/connection/remote_tsap", json!(0)),
    ] {
        let mut x = d.clone();
        *x.pointer_mut(path).unwrap() = value;
        bads.push(x);
    }
    let mut invalid_db_flag = d.clone();
    invalid_db_flag["dbs"][0]["source_enabled"] = json!(true);
    bads.push(invalid_db_flag);
    for x in bads {
        assert!(
            plc_catalog::parse(&serde_json::to_vec(&x).unwrap()).is_err(),
            "{x}"
        );
    }
    let text = String::from_utf8(valid).unwrap();
    assert!(plc_catalog::parse(
        text.replacen(
            "\"schema_version\":1",
            "\"schema_version\":1,\"schema_version\":1",
            1
        )
        .as_bytes()
    )
    .is_err());
    let mut ds = document("device_simulator");
    ds["dbs"][0]
        .as_object_mut()
        .unwrap()
        .remove("source_enabled");
    assert!(plc_catalog::parse(&serde_json::to_vec(&ds).unwrap()).is_err());
    assert!(plc_catalog::parse(&[0xef, 0xbb, 0xbf, b'{', b'}']).is_err());
}
#[test]
fn changed_file_cancel_conflict_stale_and_tsap_have_no_partial_write() {
    let root = root();
    let path = root.join("source.json");
    fs::write(
        &path,
        serde_json::to_vec(&document("data_acquisition_agent")).unwrap(),
    )
    .unwrap();
    let app = App::open(&root.join("profile")).unwrap();
    let before = app.configuration.get().unwrap();
    let file = choose(&app, &path);
    let p = preview(&app, &file, 32194).unwrap();
    fs::write(&path, b"{}").unwrap();
    assert_eq!(
        confirm(&app, &file, &p).unwrap_err(),
        "catalog_file_changed"
    );
    assert_eq!(app.configuration.get().unwrap().workspace, before.workspace);
    let mut doc = document("data_acquisition_agent");
    doc["plc"]["connection"]["remote_tsap"] = json!(0x1234);
    fs::write(&path, serde_json::to_vec(&doc).unwrap()).unwrap();
    let file = choose(&app, &path);
    assert_eq!(
        preview(&app, &file, 32194).err().unwrap(),
        "catalog_tsap_unrepresentable"
    );
    catalog_import::cancel(&app, CancelIntent { file_token: file }).unwrap();
    let doc = document("data_acquisition_agent");
    fs::write(&path, serde_json::to_vec(&doc).unwrap()).unwrap();
    let a = choose(&app, &path);
    let b = choose(&app, &path);
    let pa = preview(&app, &a, 32194).unwrap();
    let pb = preview(&app, &b, 32195).unwrap();
    confirm(&app, &a, &pa).unwrap();
    assert!(confirm(&app, &b, &pb)
        .unwrap_err()
        .starts_with("etag_conflict:"));
    let saved = app.configuration.get().unwrap();
    assert_eq!(saved.workspace.instances.len(), 1);
    assert_eq!(saved.workspace.source_versions.len(), 1);
    let c = choose(&app, &path);
    assert!(preview(&app, &c, 32195)
        .err()
        .unwrap()
        .contains("identity_conflict"));
    let mut other = document("data_acquisition_agent");
    other["plc"]["connection"]["remote_tsap"] = json!(0x102);
    fs::write(&path, serde_json::to_vec(&other).unwrap()).unwrap();
    let d = choose(&app, &path);
    assert_eq!(
        preview(&app, &d, 32194).err().unwrap(),
        "catalog_endpoint_conflict"
    );
    assert_eq!(app.configuration.get().unwrap().workspace, saved.workspace);
    assert!(app.shutdown());
    fs::remove_dir_all(root).unwrap();
}

#[cfg(feature = "test-automation")]
#[test]
fn injected_transaction_failure_or_unknown_receipt_never_creates_a_partial_catalog() {
    let root = root();
    let path = root.join("source.json");
    fs::write(
        &path,
        serde_json::to_vec(&document("data_acquisition_agent")).unwrap(),
    )
    .unwrap();
    let app = App::open(&root.join("profile")).unwrap();
    let before = app.configuration.get().unwrap();
    let file = choose(&app, &path);
    let p = preview(&app, &file, 32194).unwrap();
    app.configuration
        .store
        .test_fault("before_save_commit")
        .unwrap();
    assert_eq!(confirm(&app, &file, &p).unwrap_err(), "test_fault");
    let after = app.configuration.get().unwrap();
    assert_eq!(after.etag, before.etag);
    assert_eq!(after.workspace, before.workspace);
    catalog_import::cancel(&app, CancelIntent { file_token: file }).unwrap();
    let file = choose(&app, &path);
    let p = preview(&app, &file, 32194).unwrap();
    app.configuration
        .store
        .test_fault("after_save_commit")
        .unwrap();
    assert_eq!(
        confirm(&app, &file, &p).unwrap_err(),
        "save_receipt_unknown"
    );
    let after = app.configuration.get().unwrap();
    assert_eq!(after.workspace.instances.len(), 1);
    assert_eq!(after.workspace.source_versions.len(), 1);
    configuration::validate(&after.workspace).unwrap();
    assert!(app.shutdown());
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn complete_maximum_point_catalog_retains_one_source_and_all_mappings() {
    let root = root();
    let path = root.join("maximum.json");
    let mut d = document("data_acquisition_agent");
    let points=(0..4096).map(|n|json!({"id":uuid(),"name":format!("Point_{n}"),"data_type":"INT","byte_offset":n*2,"source_enabled":false})).collect::<Vec<_>>();
    d["dbs"] = json!([{"id":uuid(),"name":"Full","number":1,"size_bytes":8192,"points":points}]);
    let bytes = serde_json::to_vec(&d).unwrap();
    assert!(bytes.len() < 1024 * 1024);
    fs::write(&path, &bytes).unwrap();
    let app = App::open(&root.join("profile")).unwrap();
    let file = choose(&app, &path);
    let p = preview(&app, &file, 32194).unwrap();
    confirm(&app, &file, &p).unwrap();
    let saved = app.configuration.get().unwrap();
    assert_eq!(saved.workspace.source_versions.len(), 1);
    assert_eq!(saved.workspace.source_versions[0].bytes, bytes);
    assert_eq!(saved.workspace.instances[0].dbs[0].points.len(), 4096);
    assert_eq!(
        saved.workspace.instances[0].catalog.as_ref().unwrap().dbs[0]
            .points
            .len(),
        4096
    );
    let mut candidate = saved.workspace.clone();
    let instance = &mut candidate.instances[0];
    let db = &mut instance.dbs[0];
    db.address_confirmation = Some(configuration::AddressConfirmation {
        structure_sha256: ds_runtime::domain::layout::structure_signature(db),
        layout_sha256: ds_runtime::domain::layout::layout_signature(db),
        method: "manual".into(),
        reason: "synthetic maximum catalog".into(),
    });
    instance.names_confirmation = Some(ds_runtime::domain::layout::names_signature(instance));
    let id = instance.id.clone();
    let payload = serde_json::to_vec(&candidate).unwrap();
    let doc = plc_catalog::build(
        &candidate,
        &candidate.instances[0],
        &app.configuration.store.profile_id,
        &uuid(),
        &payload,
        "2026-11-17T12:00:00+08:00",
        &Target {
            instance_id: id,
            host: "127.0.0.1".into(),
            port: 32194,
            rack: 0,
            slot: 2,
            connection_confirmed: true,
            loaded_difference_confirmed: true,
        },
    )
    .unwrap();
    assert!(serde_json::to_vec_pretty(&doc).unwrap().len() > 1024 * 1024);
    let encoded = plc_catalog::encode_document(&doc).unwrap();
    assert!(encoded.len() <= 1024 * 1024);
    assert_eq!(
        plc_catalog::parse(&encoded).unwrap().dbs[0].points.len(),
        4096
    );
    let mut oversized = doc;
    let mut large_input = d;
    for point in oversized["dbs"][0]["points"]
        .as_array_mut()
        .unwrap()
        .iter_mut()
        .take(1000)
    {
        point["description"] = json!("x".repeat(400));
    }
    for point in large_input["dbs"][0]["points"]
        .as_array_mut()
        .unwrap()
        .iter_mut()
        .take(1000)
    {
        point["description"] = json!("x".repeat(400));
    }
    let large_input = serde_json::to_vec(&large_input).unwrap();
    assert!(large_input.len() <= 1024 * 1024);
    assert!(plc_catalog::parse(&large_input).is_ok());
    assert_eq!(
        plc_catalog::encode_document(&oversized).unwrap_err(),
        "catalog_capacity"
    );
    assert!(app.shutdown());
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn actual_daa_service_file_when_explicitly_supplied() {
    let Some(path) = std::env::var_os("DS005_DAA_EXPORT") else {
        return;
    };
    let expected = std::env::var("DS005_DAA_EXPORT_SHA256").expect("expected file SHA");
    let bytes = fs::read(&path).unwrap();
    assert_eq!(configuration::hash_bytes(&bytes), expected);
    let document = plc_catalog::parse(&bytes).unwrap();
    assert_eq!(document.export.producer, "data_acquisition_agent");
    let root = root();
    let app = App::open(&root.join("profile")).unwrap();
    let file = choose(&app, std::path::Path::new(&path));
    let before = app.configuration.get().unwrap();
    let p = catalog_import::preview(
        &app,
        PreviewIntent {
            file_token: file.clone(),
            expected_etag: before.etag,
            host: "127.0.0.1".into(),
            port: 32194,
            rack: document.plc.connection.rack,
            slot: document.plc.connection.slot,
            connection_confirmed: true,
        },
    )
    .unwrap();
    confirm(&app, &file, &p).unwrap();
    let state = app.configuration.get().unwrap();
    assert_eq!(state.workspace.source_versions[0].bytes, bytes);
    let instance = &state.workspace.instances[0];
    assert!(instance
        .dbs
        .iter()
        .all(|db| !db.enabled && db.points.iter().all(|p| !p.enabled)));
    let id = instance.id.clone();
    let dbs = instance
        .dbs
        .iter()
        .map(|d| d.id.clone())
        .collect::<Vec<_>>();
    for db_id in dbs {
        let state = app.configuration.get().unwrap();
        let p = layout::preview(
            &app.configuration,
            LayoutIntent {
                expected_etag: state.etag,
                instance_id: id.clone(),
                db_id,
                method: "manual".into(),
                reason: "review synthetic DAA catalog".into(),
            },
        )
        .unwrap();
        finish(&app, &p);
    }
    let state = app.configuration.get().unwrap();
    let point_ids = state.workspace.instances[0]
        .dbs
        .iter()
        .flat_map(|db| db.points.iter().map(|p| p.id.clone()))
        .collect();
    let p = naming::preview(
        &app.configuration,
        NamesIntent {
            expected_etag: state.etag,
            instance_id: id.clone(),
            point_ids,
            address_only: false,
        },
    )
    .unwrap();
    finish(&app, &p);
    let state = app.configuration.get().unwrap();
    let rev = app
        .configuration
        .store
        .publish(&state.etag)
        .unwrap()
        .revision_id
        .unwrap();
    assert!(app.shutdown());
    drop(app);
    let app = App::open(&root.join("profile")).unwrap();
    let saved = app.configuration.store.revision_snapshot(&rev).unwrap();
    assert_eq!(saved.workspace.source_versions[0].bytes, bytes);
    let output = catalog_export::preview(
        &app,
        catalog_export::PreviewIntent {
            revision_id: rev.clone(),
            filenames: [(id.clone(), format!("{id}.json"))].into(),
            targets: vec![Target {
                instance_id: id.clone(),
                host: "127.0.0.1".into(),
                port: 32194,
                rack: document.plc.connection.rack.into(),
                slot: document.plc.connection.slot.into(),
                connection_confirmed: true,
                loaded_difference_confirmed: true,
            }],
        },
    )
    .unwrap();
    assert_eq!(output["rows"][0]["issues"], json!([]));
    let token = output["token"].as_str().unwrap().to_string();
    let outdir = root.join("export");
    fs::create_dir(&outdir).unwrap();
    catalog_export::choose_directory(&app, &token, &outdir).unwrap();
    let written = catalog_export::commit(&app, catalog_export::TokenIntent { token }).unwrap();
    assert_eq!(written["rows"][0]["result"], "written");
    let actual_file = fs::read(outdir.join(format!("{id}.json"))).unwrap();
    assert_eq!(
        configuration::hash_bytes(&actual_file),
        written["rows"][0]["fileSha256"]
    );
    assert_eq!(
        serde_json::from_slice::<Value>(&actual_file).unwrap(),
        output["rows"][0]["document"]
    );
    let output = &output["rows"][0]["document"];
    let input: Value = serde_json::from_slice(&bytes).unwrap();
    assert_eq!(output["origin"], input["origin"]);
    assert_eq!(output["export"]["producer"], "device_simulator");
    assert_eq!(
        output["export"]["payload_sha256"],
        configuration::hash_bytes(&saved.payload)
    );
    for (out_db, in_db) in output["dbs"]
        .as_array()
        .unwrap()
        .iter()
        .zip(input["dbs"].as_array().unwrap())
    {
        for field in ["id", "name", "number", "size_bytes"] {
            assert_eq!(out_db[field], in_db[field]);
        }
        for (out, in_) in out_db["points"]
            .as_array()
            .unwrap()
            .iter()
            .zip(in_db["points"].as_array().unwrap())
        {
            for field in [
                "id",
                "name",
                "data_type",
                "byte_offset",
                "bit",
                "source_path",
                "display_name",
            ] {
                assert_eq!(out.get(field), in_.get(field), "{field}");
            }
            let empty = json!({"zh-CN":"","en-US":""});
            assert_eq!(
                out["display_names"],
                in_.get("display_names").unwrap_or(&empty).clone()
            );
            assert_eq!(
                out["description"].as_str().unwrap(),
                in_["description"].as_str().unwrap_or("")
            );
            assert_eq!(out["source_enabled"], false);
        }
    }
    assert_eq!(
        configuration::hash_bytes(&fs::read(&path).unwrap()),
        expected
    );
    assert!(app.shutdown());
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn oversized_complete_output_is_rejected_per_instance_without_overwrite() {
    let root = root();
    let path = root.join("large-daa.json");
    let mut input = document("data_acquisition_agent");
    let points = (0..4096).map(|n| {
        let mut point = json!({"id":uuid(),"name":format!("Point_{n}"),"data_type":"INT","byte_offset":n*2,"source_enabled":false});
        if n < 1000 { point["description"] = json!("x".repeat(400)); } point
    }).collect::<Vec<_>>();
    input["dbs"] =
        json!([{"id":uuid(),"name":"Full","number":1,"size_bytes":8192,"points":points}]);
    let bytes = serde_json::to_vec(&input).unwrap();
    assert!(bytes.len() < 1024 * 1024);
    assert!(plc_catalog::parse(&bytes).is_ok());
    fs::write(&path, &bytes).unwrap();
    let app = App::open(&root.join("profile")).unwrap();
    let file = choose(&app, &path);
    let p = preview(&app, &file, 32194).unwrap();
    // 受控测试装配同时包含已验证导入候选与第二实例；不通过 UI 伪造确认。
    let mut workspace = p.workspace.clone();
    let large = &mut workspace.instances[0];
    let large_id = large.id.clone();
    let db = &mut large.dbs[0];
    db.address_confirmation = Some(configuration::AddressConfirmation {
        structure_sha256: ds_runtime::domain::layout::structure_signature(db),
        layout_sha256: ds_runtime::domain::layout::layout_signature(db),
        method: "manual".into(),
        reason: "synthetic".into(),
    });
    large.names_confirmation = Some(ds_runtime::domain::layout::names_signature(large));
    let mut small:configuration::InstanceConfig=serde_json::from_value(json!({"id":uuid(),"name":"Small","port":32195,"dbs":[{"id":uuid(),"name":"DB","number":22,"length":2,"manual":true,"points":[{"id":uuid(),"name":"SmallPoint","dataType":"INT","byte":0,"manual":true}]}]})).unwrap();
    let small_id = small.id.clone();
    let db = &mut small.dbs[0];
    db.address_confirmation = Some(configuration::AddressConfirmation {
        structure_sha256: ds_runtime::domain::layout::structure_signature(db),
        layout_sha256: ds_runtime::domain::layout::layout_signature(db),
        method: "manual".into(),
        reason: "synthetic".into(),
    });
    small.names_confirmation = Some(ds_runtime::domain::layout::names_signature(&small));
    workspace.instances.push(small);
    let saved = app
        .configuration
        .store
        .save(&p.expected_etag, workspace)
        .unwrap();
    catalog_import::cancel(&app, CancelIntent { file_token: file }).unwrap();
    let rev = app
        .configuration
        .store
        .publish(&saved.etag)
        .unwrap()
        .revision_id
        .unwrap();
    let before = app.configuration.get().unwrap();
    let target = |id: String, port: u32| Target {
        instance_id: id,
        host: "127.0.0.1".into(),
        port,
        rack: 0,
        slot: 2,
        connection_confirmed: true,
        loaded_difference_confirmed: true,
    };
    let plan = catalog_export::preview(
        &app,
        catalog_export::PreviewIntent {
            revision_id: rev,
            filenames: [
                (large_id.clone(), format!("{large_id}.json")),
                (small_id.clone(), format!("{small_id}.json")),
            ]
            .into(),
            targets: vec![
                target(large_id.clone(), 32194),
                target(small_id.clone(), 32195),
            ],
        },
    )
    .unwrap();
    assert!(plan["rows"][0]["issues"]
        .as_array()
        .unwrap()
        .iter()
        .any(|i| i["code"] == "catalog_capacity"));
    assert_eq!(plan["rows"][1]["issues"], json!([]));
    let out = root.join("output");
    fs::create_dir(&out).unwrap();
    let protected = out.join(format!("{large_id}.json"));
    fs::write(&protected, b"existing-sentinel").unwrap();
    let token = plan["token"].as_str().unwrap().to_string();
    catalog_export::choose_directory(&app, &token, &out).unwrap();
    let result = catalog_export::commit(&app, catalog_export::TokenIntent { token }).unwrap();
    assert_eq!(result["rows"][0]["result"], "failed");
    assert_eq!(result["rows"][1]["result"], "written");
    assert_eq!(fs::read(protected).unwrap(), b"existing-sentinel");
    let valid = fs::read(out.join(format!("{small_id}.json"))).unwrap();
    assert!(plc_catalog::parse(&valid).is_ok());
    assert_eq!(app.configuration.get().unwrap().workspace, before.workspace);
    assert!(app.shutdown());
    fs::remove_dir_all(root).unwrap();
}
