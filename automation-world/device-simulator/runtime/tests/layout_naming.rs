//! DS消费者用冻结v1 oracle检验真实服务，不修改或从被测输出生成期望。
use ds_runtime::{
    domain::configuration::{self, InstanceConfig},
    infrastructure::config_store::Store,
    services::{
        configuration::{Configuration, SaveIntent},
        layout::{self, LayoutIntent},
        naming::{self, NamesIntent},
        source_import::{self, BindingIntent, Declaration, ImportFile, ImportIntent},
    },
};
use serde_json::{json, Value};
use std::{path::PathBuf, sync::Arc};
fn service() -> (Configuration, String) {
    let p = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("owned root"))
        .join(configuration::uuid());
    let s = Configuration::new(Arc::new(Store::open(&p).unwrap()));
    let state = s.get().unwrap();
    let id = configuration::uuid();
    let mut w = state.workspace;
    w.instances.push(
        serde_json::from_value::<InstanceConfig>(json!({"id":id,"name":"Consumer","port":30102}))
            .unwrap(),
    );
    s.save(SaveIntent {
        expected_etag: state.etag,
        workspace: w,
        confirm_points: vec![],
    })
    .unwrap();
    (s, id)
}
fn confirm(s: &Configuration, p: ds_runtime::services::configuration::Preview) {
    s.confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
        .unwrap();
}
#[test]
fn all_four_layout_oracles_through_import_and_layout_service() {
    let oracle: Value = serde_json::from_slice(include_bytes!(
        "../../../shared/tia-import-core/fixtures/daa005-layout-oracle.json"
    ))
    .unwrap();
    for case in oracle["cases"].as_array().unwrap() {
        let (s, id) = service();
        let state = s.get().unwrap();
        let source=format!("TYPE \"OracleUnit\" STRUCT ready:BOOL; code:BYTE; count:INT; END_STRUCT; END_TYPE\nDATA_BLOCK \"{}\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\n{}\nEND_VAR\nBEGIN\nEND_DATA_BLOCK",case["name"].as_str().unwrap(),case["declarations"].as_str().unwrap());
        let p = source_import::preview(
            &s,
            ImportIntent {
                expected_etag: state.etag,
                instance_id: id.clone(),
                files: vec![ImportFile {
                    input_id: "source".into(),
                    name: "oracle.db".into(),
                    bytes: source.into_bytes(),
                    lineage_id: None,
                }],
                bindings: vec![BindingIntent {
                    db_id: None,
                    number: 73,
                    declaration: Declaration {
                        input_id: "source".into(),
                        declaration_index: 1,
                    },
                    udt_closure: vec![Declaration {
                        input_id: "source".into(),
                        declaration_index: 0,
                    }],
                }],
            },
        )
        .unwrap()
        .preview
        .unwrap();
        confirm(&s, p);
        let state = s.get().unwrap();
        let db = &state.workspace.instances[0].dbs[0];
        let p = layout::preview(
            &s,
            LayoutIntent {
                expected_etag: state.etag,
                instance_id: id,
                db_id: db.id.clone(),
                method: "standard".into(),
                reason: String::new(),
            },
        )
        .unwrap();
        let db = &p.workspace.instances[0].dbs[0];
        assert_eq!(db.length as u64, case["length"].as_u64().unwrap());
        assert_eq!(db.points.len(), case["leaves"].as_array().unwrap().len());
        for expected in case["leaves"].as_array().unwrap() {
            let point = db
                .points
                .iter()
                .find(|p| p.source_path == expected["path"].as_str().unwrap())
                .unwrap();
            assert_eq!(point.byte.map(u64::from), expected["byte"].as_u64());
            assert_eq!(point.bit.map(u64::from), expected["bit"].as_u64());
        }
        s.store.shutdown().unwrap();
    }
}
#[test]
fn names_v1_actual_batch_and_string_refusal() {
    let (s, id) = service();
    let state = s.get().unwrap();
    let p = source_import::preview(
        &s,
        ImportIntent {
            expected_etag: state.etag,
            instance_id: id.clone(),
            files: vec![
                ImportFile {
                    input_id: "db".into(),
                    name: "names.db".into(),
                    bytes: include_bytes!("../../../shared/tia-import-core/fixtures/names.db")
                        .to_vec(),
                    lineage_id: None,
                },
                ImportFile {
                    input_id: "udt".into(),
                    name: "names.udt".into(),
                    bytes: include_bytes!("../../../shared/tia-import-core/fixtures/names.udt")
                        .to_vec(),
                    lineage_id: None,
                },
            ],
            bindings: vec![
                BindingIntent {
                    db_id: None,
                    number: 28,
                    declaration: Declaration {
                        input_id: "db".into(),
                        declaration_index: 0,
                    },
                    udt_closure: vec![Declaration {
                        input_id: "udt".into(),
                        declaration_index: 0,
                    }],
                },
                BindingIntent {
                    db_id: None,
                    number: 60,
                    declaration: Declaration {
                        input_id: "db".into(),
                        declaration_index: 1,
                    },
                    udt_closure: vec![],
                },
            ],
        },
    )
    .unwrap()
    .preview
    .unwrap();
    confirm(&s, p);
    let state = s.get().unwrap();
    let db_id = state.workspace.instances[0].dbs[0].id.clone();
    let string_id = state.workspace.instances[0].dbs[1].id.clone();
    assert_eq!(
        layout::preview(
            &s,
            LayoutIntent {
                expected_etag: state.etag.clone(),
                instance_id: id.clone(),
                db_id: string_id,
                method: "standard".into(),
                reason: String::new()
            }
        )
        .err()
        .unwrap(),
        "string_layout_manual_required"
    );
    let p = layout::preview(
        &s,
        LayoutIntent {
            expected_etag: state.etag,
            instance_id: id.clone(),
            db_id,
            method: "standard".into(),
            reason: String::new(),
        },
    )
    .unwrap();
    confirm(&s, p);
    let state = s.get().unwrap();
    let points = state.workspace.instances[0].dbs[0]
        .points
        .iter()
        .map(|p| p.id.clone())
        .collect();
    let p = naming::preview(
        &s,
        NamesIntent {
            expected_etag: state.etag,
            instance_id: id,
            point_ids: points,
            address_only: false,
        },
    )
    .unwrap();
    let db = &p.workspace.instances[0].dbs[0];
    assert_eq!(
        db.points
            .iter()
            .find(|p| p.source_path == "ActTemp_Z1")
            .unwrap()
            .name,
        "DB28_ActTemp_Z1_Int"
    );
    assert_eq!(
        db.points
            .iter()
            .find(|p| p.source_path == "Driver_W.Unc_1.ActTemp")
            .unwrap()
            .name,
        "DB28_Driver_W_Unc_1_ActTemp_Int"
    );
    assert!(db
        .points
        .iter()
        .filter(|p| p.source_path.contains("items["))
        .all(|p| p.name.starts_with("DB28_B")));
    s.store.shutdown().unwrap();
}

#[test]
fn complete_expected_v1_naming_through_ds_single_instance_namespace() {
    let expected: Value = serde_json::from_slice(include_bytes!(
        "../../../shared/tia-import-core/fixtures/expected-v1.json"
    ))
    .unwrap();
    // 每行是独立向量（含同一路径的未确认/已确认两种输入），不能把不同前置条件合成一个namespace。
    for case in expected["cases"].as_array().unwrap() {
        let (s, id) = service();
        let state = s.get().unwrap();
        let mut w = state.workspace;
        let point_id = configuration::uuid();
        let db_id = configuration::uuid();
        let segments = case["segments"]
            .as_array()
            .unwrap()
            .iter()
            .map(|s| {
                if let Some(field) = s.as_str() {
                    json!({"kind":"field","value":field})
                } else {
                    json!({"kind":"index","value":s.as_i64().unwrap()})
                }
            })
            .collect::<Vec<_>>();
        let byte = case["address"]["offset"].as_u64();
        let bit = case["address"]["bit"].as_u64();
        w.instances[0].dbs.push(serde_json::from_value(json!({"id":db_id,"name":"IndependentVector","number":case["db"],"length":8192,"manual":true,"points":[{"id":point_id,"name":"","dataType":case["type"],"byte":byte,"bit":bit,"segments":segments,"manual":false,"manualReason":"independent v1 input"}]})).unwrap());
        s.save(SaveIntent {
            expected_etag: state.etag,
            workspace: w,
            confirm_points: vec![],
        })
        .unwrap();
        if byte.is_some() {
            let p = layout::preview(
                &s,
                LayoutIntent {
                    expected_etag: s.get().unwrap().etag,
                    instance_id: id.clone(),
                    db_id,
                    method: "manual".into(),
                    reason: "independent v1 input".into(),
                },
            )
            .unwrap();
            confirm(&s, p);
        }
        let p = naming::preview(
            &s,
            NamesIntent {
                expected_etag: s.get().unwrap().etag,
                instance_id: id,
                point_ids: vec![point_id],
                address_only: false,
            },
        )
        .unwrap();
        assert_eq!(
            p.workspace.instances[0].dbs[0].points[0].name,
            case["name"].as_str().unwrap(),
            "{}",
            case["key"]
        );
        if case["mode"] == "pending" {
            assert!(p.workspace.instances[0].names_confirmation.is_none());
        }
        s.store.shutdown().unwrap();
    }
}
