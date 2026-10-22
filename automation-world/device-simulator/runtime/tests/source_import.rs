//! DS重导消费者合同：稳定UUID、显式lineage、未选DB/旧UDT闭包保护、BEGIN初值不消费。
use ds_runtime::{
    domain::configuration::{self, InstanceConfig},
    infrastructure::config_store::Store,
    services::{
        configuration::{Configuration, SaveIntent},
        source_import::{self, BindingIntent, Declaration, ImportFile, ImportIntent},
    },
};
use serde_json::json;
use std::{path::PathBuf, sync::Arc};
fn source(changed: bool) -> Vec<u8> {
    format!("TYPE \"Unit\" STRUCT Value:INT; END_STRUCT; END_TYPE\nDATA_BLOCK \"One\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\nValue:{} := 4; {};\nEND_VAR\nBEGIN\nValue := 99;\nEND_DATA_BLOCK\nDATA_BLOCK \"Two\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\nUnit: \\\"Unit\\\";\nEND_VAR\nBEGIN\nEND_DATA_BLOCK",if changed{"DINT"}else{"INT"},if changed{"Added:BOOL"}else{"Removed:BOOL"}).replace("\\\"","\"").into_bytes()
}
fn binding(id: Option<String>, index: usize, number: u16) -> BindingIntent {
    BindingIntent {
        db_id: id,
        number,
        declaration: Declaration {
            input_id: "batch".into(),
            declaration_index: index,
        },
        udt_closure: if index == 2 {
            vec![Declaration {
                input_id: "batch".into(),
                declaration_index: 0,
            }]
        } else {
            vec![]
        },
    }
}
#[test]
fn explicit_reimport_preserves_unselected_identity_and_immutable_old_closure() {
    let p = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("owned root"))
        .join(configuration::uuid());
    let s = Configuration::new(Arc::new(Store::open(&p).unwrap()));
    let state = s.get().unwrap();
    let mut w = state.workspace;
    let id = configuration::uuid();
    w.instances.push(
        serde_json::from_value::<InstanceConfig>(json!({"id":id,"name":"Reimport","port":30102}))
            .unwrap(),
    );
    s.save(SaveIntent {
        expected_etag: state.etag,
        workspace: w,
        confirm_points: vec![],
    })
    .unwrap();
    let initial = source_import::preview(
        &s,
        ImportIntent {
            expected_etag: s.get().unwrap().etag,
            instance_id: id.clone(),
            files: vec![ImportFile {
                input_id: "batch".into(),
                name: "source.db".into(),
                bytes: source(false),
                lineage_id: None,
            }],
            bindings: vec![binding(None, 1, 73), binding(None, 2, 90)],
        },
    )
    .unwrap()
    .preview
    .unwrap();
    s.confirm(
        "import",
        &initial.token,
        &initial.expected_etag,
        &initial.candidate_sha256,
    )
    .unwrap();
    let old = s.get().unwrap();
    let db1 = &old.workspace.instances[0].dbs[0];
    let db2 = old.workspace.instances[0].dbs[1].clone();
    let point = db1
        .points
        .iter()
        .find(|p| p.source_path == "Value")
        .unwrap();
    let point_id = point.id.clone();
    assert!(point.policy.initial.is_none());
    let lineage = old.workspace.source_versions[0].lineage_id.clone();
    let db1_id = db1.id.clone();
    let same = source_import::preview(
        &s,
        ImportIntent {
            expected_etag: old.etag.clone(),
            instance_id: id.clone(),
            files: vec![ImportFile {
                input_id: "batch".into(),
                name: "source.db".into(),
                bytes: source(false),
                lineage_id: Some(lineage.clone()),
            }],
            bindings: vec![binding(Some(db1_id.clone()), 1, 73)],
        },
    )
    .unwrap()
    .preview
    .unwrap();
    assert_eq!(
        s.confirm(
            "import",
            &same.token,
            &same.expected_etag,
            &same.candidate_sha256
        )
        .unwrap()
        .result,
        "unchanged"
    );
    assert_eq!(s.get().unwrap().etag, old.etag);
    let next = source_import::preview(
        &s,
        ImportIntent {
            expected_etag: old.etag,
            instance_id: id.clone(),
            files: vec![ImportFile {
                input_id: "batch".into(),
                name: "source.db".into(),
                bytes: source(true),
                lineage_id: Some(lineage),
            }],
            bindings: vec![binding(Some(db1_id), 1, 73)],
        },
    )
    .unwrap()
    .preview
    .unwrap();
    assert!(next.details["changes"]
        .as_array()
        .unwrap()
        .iter()
        .any(|r| r["result"] == "deleted"));
    s.confirm(
        "import",
        &next.token,
        &next.expected_etag,
        &next.candidate_sha256,
    )
    .unwrap();
    let current = s.get().unwrap();
    assert_eq!(current.workspace.instances[0].dbs[1], db2);
    assert_eq!(current.workspace.source_versions.len(), 2);
    let changed = current.workspace.instances[0].dbs[0]
        .points
        .iter()
        .find(|p| p.source_path == "Value")
        .unwrap();
    assert_eq!(changed.id, point_id);
    assert_eq!(changed.data_type, "DINT");
    assert!(changed.confirmations.initial.is_none());
    assert!(changed.byte.is_none());
    assert!(current.workspace.instances[0].dbs[0]
        .address_confirmation
        .is_none());
    let mut tampered = current.workspace.clone();
    tampered.instances[0].dbs[0]
        .binding
        .as_mut()
        .unwrap()
        .tree
        .clear();
    assert_eq!(
        s.save(SaveIntent {
            expected_etag: current.etag.clone(),
            workspace: tampered,
            confirm_points: vec![]
        })
        .unwrap_err(),
        "derived_source_read_only"
    );
    let mut tampered = current.workspace;
    tampered.instances[0].dbs[0].points[0].data_type = "BYTE".into();
    assert_eq!(
        s.save(SaveIntent {
            expected_etag: current.etag,
            workspace: tampered,
            confirm_points: vec![]
        })
        .unwrap_err(),
        "derived_structure_read_only"
    );
    s.store.shutdown().unwrap();
}

#[test]
fn real_ds_consumer_rejects_unsupported_sources_and_requires_explicit_same_name_udt() {
    let root =
        PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").unwrap()).join(configuration::uuid());
    let service = Configuration::new(Arc::new(Store::open(&root).unwrap()));
    let id = configuration::uuid();
    let state = service.get().unwrap();
    let mut workspace = state.workspace;
    workspace.instances.push(
        serde_json::from_value(json!({"id":id,"name":"Source negatives","port":30102})).unwrap(),
    );
    service
        .save(SaveIntent {
            expected_etag: state.etag,
            workspace,
            confirm_points: vec![],
        })
        .unwrap();
    let source = |fields: &str, standard: bool| {
        format!("DATA_BLOCK \"Selected\"\n{{ S7_Optimized_Access := '{}' }}\nVAR\n{}\nEND_VAR\nBEGIN\nEND_DATA_BLOCK",if standard{"FALSE"}else{"TRUE"},fields)
    };
    let file = |input: &str, text: String| ImportFile {
        input_id: input.into(),
        name: format!("{input}.db"),
        bytes: text.into_bytes(),
        lineage_id: None,
    };
    let before = service.get().unwrap();
    let mut deep = String::new();
    for level in 0..10 {
        deep.push_str(&format!(
            "TYPE \"Level{level}\" STRUCT Next : {}; END_STRUCT; END_TYPE\n",
            if level == 9 {
                "INT".into()
            } else {
                format!("\"Level{}\"", level + 1)
            }
        ));
    }
    deep.push_str(&source("Value : \"Level0\";", true));
    for text in [
        deep,
        source("Value : \"Missing\";", true),
        source("Value : UNKNOWN_TYPE;", true),
        source("Value : ARRAY[0..1,0..1] OF INT;", true),
        source("Value : ARRAY[0..1024] OF INT;", true),
        format!(
            "TYPE \"Cycle\" STRUCT Next : \"Cycle\"; END_STRUCT; END_TYPE\n{}",
            source("Value : \"Cycle\";", true)
        ),
    ] {
        let files = vec![file("input", text)];
        let scanned = source_import::preview(
            &service,
            ImportIntent {
                expected_etag: before.etag.clone(),
                instance_id: id.clone(),
                files: files.clone(),
                bindings: vec![],
            },
        )
        .unwrap();
        let db = scanned
            .declarations
            .iter()
            .find(|d| d["db"] == true)
            .unwrap();
        let closure = scanned
            .declarations
            .iter()
            .filter(|d| d["db"] == false)
            .map(|d| Declaration {
                input_id: d["inputId"].as_str().unwrap().into(),
                declaration_index: d["declarationIndex"].as_u64().unwrap() as usize,
            })
            .collect();
        assert!(source_import::preview(
            &service,
            ImportIntent {
                expected_etag: before.etag.clone(),
                instance_id: id.clone(),
                files,
                bindings: vec![BindingIntent {
                    db_id: None,
                    number: 71,
                    declaration: Declaration {
                        input_id: "input".into(),
                        declaration_index: db["declarationIndex"].as_u64().unwrap() as usize
                    },
                    udt_closure: closure
                }]
            }
        )
        .is_err());
        assert_eq!(service.get().unwrap().workspace, before.workspace);
    }
    assert!(matches!(source_import::preview(&service, ImportIntent {
        expected_etag:before.etag.clone(),instance_id:id.clone(),
        files:vec![file("optimized",source("Value : INT;",false))],
        bindings:vec![BindingIntent{db_id:None,number:71,declaration:Declaration{input_id:"optimized".into(),declaration_index:0},udt_closure:vec![]}]
    }), Err(e) if e == "optimized_access"));
    let files = vec![
        file("main", source("UnitValue : \"Unit\";", true)),
        file(
            "first",
            "TYPE \"Unit\" STRUCT First : INT; END_STRUCT; END_TYPE".into(),
        ),
        file(
            "second",
            "TYPE \"Unit\" STRUCT Second : REAL; END_STRUCT; END_TYPE".into(),
        ),
    ];
    for (chosen, expected) in [("first", "UnitValue.First"), ("second", "UnitValue.Second")] {
        let preview = source_import::preview(
            &service,
            ImportIntent {
                expected_etag: before.etag.clone(),
                instance_id: id.clone(),
                files: files.clone(),
                bindings: vec![BindingIntent {
                    db_id: None,
                    number: 71,
                    declaration: Declaration {
                        input_id: "main".into(),
                        declaration_index: 0,
                    },
                    udt_closure: vec![Declaration {
                        input_id: chosen.into(),
                        declaration_index: 0,
                    }],
                }],
            },
        )
        .unwrap()
        .preview
        .unwrap();
        assert_eq!(
            preview.workspace.instances[0].dbs[0].points[0].source_path,
            expected
        );
        assert_eq!(preview.workspace.instances[0].dbs[0].points.len(), 1);
    }
    assert!(source_import::preview(
        &service,
        ImportIntent {
            expected_etag: before.etag.clone(),
            instance_id: id.clone(),
            files,
            bindings: vec![BindingIntent {
                db_id: None,
                number: 71,
                declaration: Declaration {
                    input_id: "main".into(),
                    declaration_index: 0
                },
                udt_closure: vec![
                    Declaration {
                        input_id: "first".into(),
                        declaration_index: 0
                    },
                    Declaration {
                        input_id: "second".into(),
                        declaration_index: 0
                    }
                ]
            }]
        }
    )
    .is_err());
    assert_eq!(service.get().unwrap().workspace, before.workspace);
    let oversized = ImportFile {
        input_id: "large".into(),
        name: "large.db".into(),
        bytes: vec![b' '; 1048577],
        lineage_id: None,
    };
    assert!(source_import::preview(
        &service,
        ImportIntent {
            expected_etag: before.etag,
            instance_id: id,
            files: vec![oversized],
            bindings: vec![]
        }
    )
    .is_err());
    let state = service.get().unwrap();
    let scan = |files: Vec<ImportFile>| {
        source_import::preview(
            &service,
            ImportIntent {
                expected_etag: state.etag.clone(),
                instance_id: state.workspace.instances[0].id.clone(),
                files,
                bindings: vec![],
            },
        )
    };
    let tiny = (0..128)
        .map(|n| file(&format!("tiny{n}"), source("Value : INT;", true)))
        .collect::<Vec<_>>();
    assert_eq!(scan(tiny.clone()).unwrap().declarations.len(), 128);
    let mut too_many = tiny;
    too_many.push(file("extra", source("Value : INT;", true)));
    assert!(scan(too_many).is_err());
    let mut padded = vec![b' '; 1048576];
    let declaration = source("Value : INT;", true).into_bytes();
    let tail = padded.len() - declaration.len();
    padded[tail..].copy_from_slice(&declaration);
    let exact = (0..4)
        .map(|n| ImportFile {
            input_id: format!("exact{n}"),
            name: format!("exact{n}.db"),
            bytes: padded.clone(),
            lineage_id: None,
        })
        .collect::<Vec<_>>();
    assert_eq!(scan(exact.clone()).unwrap().declarations.len(), 4);
    let mut over_batch = exact;
    over_batch.push(file("fifth", source("Value : INT;", true)));
    assert!(scan(over_batch).is_err());
    service.store.shutdown().unwrap();
}

#[test]
fn physical_reimport_requires_new_point_confirmation_before_real_apply() {
    use ds_runtime::{
        app::App,
        domain::layout as compiled,
        services::{
            apply::{self, ApplyConfirmation, ApplyIntent},
            configuration::Preview,
            layout::{self, LayoutIntent},
            naming::{self, NamesIntent},
        },
    };
    fn confirm(app: &App, p: Preview) {
        app.configuration
            .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
            .unwrap();
    }
    fn prove_layout_and_names(app: &App, id: &str, db: &str) {
        confirm(
            app,
            layout::preview(
                &app.configuration,
                LayoutIntent {
                    expected_etag: app.configuration.get().unwrap().etag,
                    instance_id: id.into(),
                    db_id: db.into(),
                    method: "standard".into(),
                    reason: String::new(),
                },
            )
            .unwrap(),
        );
        let s = app.configuration.get().unwrap();
        let point_ids = s.workspace.instances[0]
            .dbs
            .iter()
            .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
            .collect();
        confirm(
            app,
            naming::preview(
                &app.configuration,
                NamesIntent {
                    expected_etag: s.etag,
                    instance_id: id.into(),
                    point_ids,
                    address_only: false,
                },
            )
            .unwrap(),
        );
    }
    fn confirm_points(app: &App) {
        let s = app.configuration.get().unwrap();
        let ids = s.workspace.instances[0]
            .dbs
            .iter()
            .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
            .collect();
        app.configuration
            .save(SaveIntent {
                expected_etag: s.etag,
                workspace: s.workspace,
                confirm_points: ids,
            })
            .unwrap();
    }
    fn apply_intent(app: &App, id: &str) -> ApplyIntent {
        let s = app.configuration.get().unwrap();
        ApplyIntent {
            expected_etag: s.etag,
            instance_id: id.into(),
            revision_id: s.latest_revision.unwrap(),
            retention: "preserve_compatible_hold".into(),
        }
    }
    fn apply_latest(app: &App, id: &str) {
        let p = apply::preview(app, apply_intent(app, id)).unwrap();
        let r = apply::confirm(
            app,
            ApplyConfirmation {
                expected_etag: p.expected_etag,
                instance_id: id.into(),
                token: p.token,
                candidate_sha256: p.candidate_sha256,
                impact_sha256: p.details["impactSha256"].as_str().unwrap().into(),
            },
        )
        .unwrap();
        assert_eq!(r["result"], "loaded");
    }
    let root = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("owned root"))
        .join(configuration::uuid());
    let app = App::open(&root).unwrap();
    let id = configuration::uuid();
    let s = app.configuration.get().unwrap();
    let mut w = s.workspace;
    w.instances.push(
        serde_json::from_value::<InstanceConfig>(
            json!({"id":id,"name":"Confirmation regression","port":30102}),
        )
        .unwrap(),
    );
    app.configuration
        .save(SaveIntent {
            expected_etag: s.etag,
            workspace: w,
            confirm_points: vec![],
        })
        .unwrap();
    let text = |extra: &str| {
        format!("DATA_BLOCK \"One\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\nValue:INT; {extra}\nEND_VAR\nBEGIN\nEND_DATA_BLOCK\nDATA_BLOCK \"Two\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVAR\nOther:INT;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK\n").into_bytes()
    };
    let import = |db: Option<String>, number, lineage, bytes, both| {
        source_import::preview(
            &app.configuration,
            ImportIntent {
                expected_etag: app.configuration.get().unwrap().etag,
                instance_id: id.clone(),
                files: vec![ImportFile {
                    input_id: "batch".into(),
                    name: "confirmation.db".into(),
                    bytes,
                    lineage_id: lineage,
                }],
                bindings: if both {
                    vec![binding(db, 0, number), binding(None, 1, 90)]
                } else {
                    vec![binding(db, 0, number)]
                },
            },
        )
        .unwrap()
        .preview
        .unwrap()
    };
    confirm(&app, import(None, 71, None, text(""), true));
    let s = app.configuration.get().unwrap();
    let db = s.workspace.instances[0].dbs[0].id.clone();
    let other_id = s.workspace.instances[0].dbs[1].id.clone();
    prove_layout_and_names(&app, &id, &db);
    prove_layout_and_names(&app, &id, &other_id);
    confirm_points(&app);
    apply_latest(&app, &id);
    let before = app.configuration.get().unwrap();
    let baseline = before.workspace.instances[0].dbs[0].clone();
    let other = before.workspace.instances[0].dbs[1].clone();
    let lineage = before.workspace.source_versions[0].lineage_id.clone();
    // Ordinary saves use the same physical gate; display-only edits remain compatible.
    for change in ["number", "length", "address", "display"] {
        let mut w = before.workspace.clone();
        let d = &mut w.instances[0].dbs[0];
        match change {
            "number" => d.number = 72,
            "length" => d.length += 2,
            "address" => {
                d.length += 2;
                d.points[0].byte = Some(2)
            }
            _ => d.points[0].name.push_str("Display"),
        }
        let (_, prepared) = app
            .configuration
            .prepare(SaveIntent {
                expected_etag: before.etag.clone(),
                workspace: w,
                confirm_points: vec![],
            })
            .unwrap();
        let confirmations = &prepared.instances[0].dbs[0].points[0].confirmations;
        assert_eq!(
            confirmations.initial.is_some(),
            change == "display",
            "{change}"
        );
        assert_eq!(
            confirmations.policy.is_some(),
            change == "display",
            "{change}"
        );
        assert_eq!(prepared.instances[0].dbs[1], other);
    }
    // Exact F3: same bytes/lineage/point UUID, only the target DB number changes.
    let p = import(Some(db.clone()), 72, Some(lineage.clone()), text(""), false);
    assert_eq!(
        p.workspace.instances[0].dbs[0].points[0].id,
        baseline.points[0].id
    );
    assert_eq!(
        p.workspace.instances[0].dbs[0].points[0].policy,
        baseline.points[0].policy
    );
    assert!(p.workspace.instances[0].dbs[0].points[0]
        .confirmations
        .initial
        .is_none());
    assert!(p.workspace.instances[0].dbs[0].points[0]
        .confirmations
        .policy
        .is_none());
    assert_eq!(p.workspace.instances[0].dbs[1], other);
    confirm(&app, p);
    prove_layout_and_names(&app, &id, &db);
    assert!(compiled::compile(&app.configuration.get().unwrap().workspace.instances[0]).is_err());
    assert!(apply::preview(&app, apply_intent(&app, &id)).is_err());
    assert!(app
        .instance(&id)
        .unwrap()
        .context
        .owner
        .compiled()
        .dbs
        .contains_key(&71));
    confirm_points(&app);
    apply_latest(&app, &id);
    assert!(app
        .instance(&id)
        .unwrap()
        .context
        .owner
        .compiled()
        .dbs
        .contains_key(&72));
    // A new structural leaf invalidates retained points too; an identical reimport does not.
    let stable = app.configuration.get().unwrap();
    let same = import(Some(db.clone()), 72, Some(lineage.clone()), text(""), false);
    assert_eq!(same.workspace, stable.workspace);
    confirm(&app, same);
    let p = import(
        Some(db.clone()),
        72,
        Some(lineage),
        text("Added:BOOL;"),
        false,
    );
    assert_eq!(
        p.workspace.instances[0].dbs[0].points[0].id,
        baseline.points[0].id
    );
    assert!(p.workspace.instances[0].dbs[0].points.iter().all(|p| p
        .confirmations
        .initial
        .is_none()
        && p.confirmations.policy.is_none()));
    assert_eq!(p.workspace.instances[0].dbs[1], other);
    confirm(&app, p);
    prove_layout_and_names(&app, &id, &db);
    assert!(compiled::compile(&app.configuration.get().unwrap().workspace.instances[0]).is_err());
    confirm_points(&app);
    apply_latest(&app, &id);
    // 已确认的历史revision仍可回滚；它不继承当前draft的新地址上下文。
    let s = app.configuration.get().unwrap();
    let p = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: s.etag,
            instance_id: id.clone(),
            revision_id: before.latest_revision.unwrap(),
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    apply::confirm(
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
    assert!(app
        .instance(&id)
        .unwrap()
        .context
        .owner
        .compiled()
        .dbs
        .contains_key(&71));
    assert!(app.shutdown());
}
