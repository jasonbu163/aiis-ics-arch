//! ARCH-AW-009 合成 profile、原始点表和替身测试。没有网络套接字。
use super::*;
use crate::domain::{
    ca_catalog::Catalog,
    ca_flow::{checked_json, sha},
};
use crate::services::ca_workspace::{Binding, HttpBinding};
use std::{fs, path::PathBuf};

const DAA: &[u8] = include_bytes!("../fixtures/arch-aw-009/DAA-raw.json");
const DS: &[u8] = include_bytes!("../fixtures/arch-aw-009/DS-raw.json");
const FLOW: &[u8] =
    include_bytes!("../../../../../contracts/demands/ca-field-flow-v1/examples/status-gate.json");

struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let dir = std::env::temp_dir().join(format!("aw009-test-{}", Uuid::new_v4()));
        fs::create_dir(&dir).unwrap();
        Self(dir)
    }
    fn workspace(&self) -> Workspace {
        Workspace::open(self.0.clone(), true).unwrap()
    }
    fn file(&self, name: &str, raw: &[u8]) -> PathBuf {
        let p = self.0.join(name);
        fs::write(&p, raw).unwrap();
        p
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn catalog(ws: &Workspace, fixture: &Fixture, name: &str, raw: &[u8], alias: &str) -> Value {
    let path = fixture.file(name, raw);
    let p = ws.preview_catalog(path, raw).unwrap();
    let token = p["token"].as_str().unwrap();
    assert_eq!(p["file_sha256"], sha(raw));
    assert_eq!(ws.import_catalog(token, alias).unwrap()["id"], alias);
    p
}

fn prepare(ws: &Workspace, fixture: &Fixture) {
    let imported = catalog(ws, fixture, "ds.json", DS, "plc_line_a");
    let point_id = imported["catalog"]["dbs"][0]["points"][1]["id"]
        .as_str()
        .unwrap();
    ws.bind(Binding::Point {
        id: "plc_line_a".into(),
        point_id: point_id.into(),
        alias: "task_status".into(),
    })
    .unwrap();
    let target = serde_json::from_value(imported["catalog"]["plc"]["connection"].clone()).unwrap();
    ws.bind(Binding::Plc {
        id: "plc_line_a".into(),
        target,
    })
    .unwrap();
    ws.bind(Binding::Http {
        id: "backend_api".into(),
        target: HttpBinding {
            base_url: "https://fixture.invalid".into(),
            headers: BTreeMap::from([("Authorization".into(), "test-secret".into())]),
        },
    })
    .unwrap();
}

#[test]
fn original_catalogs_preview_commit_reopen_repeat_and_conflict() {
    let fixture = Fixture::new();
    let ws = fixture.workspace();
    let daa = catalog(&ws, &fixture, "daa.json", DAA, "daa");
    assert_eq!(
        daa["catalog"]["export"]["producer"],
        "data_acquisition_agent"
    );
    assert!(daa["catalog"]["dbs"][0].get("source_enabled").is_none());
    let ds = catalog(&ws, &fixture, "ds.json", DS, "ds");
    assert_eq!(ds["catalog"]["export"]["producer"], "device_simulator");
    assert_eq!(ds["catalog"]["dbs"][1]["source_enabled"], false);
    assert_eq!(
        ds["catalog"]["dbs"][0]["points"][2]["source_enabled"],
        false
    );
    assert!(ds["catalog"]["dbs"][0]["points"][0]["display_names"].is_object());
    let ws = fixture.workspace();
    assert_eq!(ws.snapshot().unwrap().catalogs[0].raw.as_bytes(), DAA);
    assert_eq!(ws.snapshot().unwrap().catalogs[1].raw.as_bytes(), DS);
    for (raw, name, alias) in [(DAA, "daa.json", "daa"), (DS, "ds.json", "ds")] {
        let p = ws.preview_catalog(fixture.0.join(name), raw).unwrap();
        assert_eq!(p["status"], "identical");
        assert_eq!(
            ws.import_catalog(p["token"].as_str().unwrap(), "other")
                .unwrap()["id"],
            alias
        );
    }
    let mut modified: Value = serde_json::from_slice(DS).unwrap();
    modified["dbs"][0]["points"][1]["display_name"] = json!("changed");
    let raw = serde_json::to_vec(&modified).unwrap();
    let path = fixture.file("changed.json", &raw);
    let p = ws.preview_catalog(path.clone(), &raw).unwrap();
    assert_eq!(p["status"], "changed");
    assert_eq!(p["diff"]["changed"].as_array().unwrap().len(), 1);
    assert_eq!(ws.snapshot().unwrap().catalogs.len(), 2);
    let p = ws.preview_catalog(path, &raw).unwrap();
    assert!(ws
        .import_catalog(p["token"].as_str().unwrap(), "ds")
        .is_err());
    assert_eq!(ws.snapshot().unwrap().catalogs.len(), 2);
    let p = catalog(&ws, &fixture, "changed.json", &raw, "ds_new");
    assert_eq!(p["status"], "changed");
    assert_eq!(ws.snapshot().unwrap().catalogs.len(), 3);
}
#[test]
fn malformed_catalogs_are_rejected_and_unsupported_tsap_is_retained() {
    let original: Value = serde_json::from_slice(DS).unwrap();
    for (path, value) in [
        ("/schema_version", json!(2)),
        ("/dbs/0/unknown", json!(0)),
        ("/dbs/0/points/0/bit", json!(8)),
        (
            "/dbs/0/points/1/id",
            original["dbs"][0]["points"][0]["id"].clone(),
        ),
        ("/dbs/0/points/1/byte_offset", json!(0)),
        ("/dbs/0/points/1/data_type", json!("STRING[255]")),
        ("/dbs/0/points/1/byte_offset", json!(65536)),
    ] {
        let mut copy = original.clone();
        if path.ends_with("/unknown") {
            copy["dbs"][0]["unknown"] = value;
        } else {
            *copy.pointer_mut(path).unwrap() = value;
        }
        assert!(
            Catalog::parse(&serde_json::to_vec(&copy).unwrap()).is_err(),
            "{path}"
        );
    }
    assert!(Catalog::parse(br#"{"format":"aiis.plc_points","format":"aiis.plc_points"}"#).is_err());
    let mut custom = original;
    custom["plc"]["connection"]["remote_tsap"] = json!(0x0202);
    let raw = serde_json::to_vec(&custom).unwrap();
    let fixture = Fixture::new();
    let ws = fixture.workspace();
    let p = catalog(&ws, &fixture, "tsap.json", &raw, "tsap");
    assert_eq!(p["catalog"]["plc"]["connection"]["remote_tsap"], 0x0202);
    let target = serde_json::from_value(p["catalog"]["plc"]["connection"].clone()).unwrap();
    assert!(ws
        .bind(Binding::Plc {
            id: "tsap".into(),
            target
        })
        .is_err());
}

#[test]
fn graph_validators_and_roundtrip() {
    let fixture = Fixture::new();
    let ws = fixture.workspace();
    prepare(&ws, &fixture);
    let doc: Document = checked_json(FLOW).unwrap();
    assert!(ws.validate(&doc).unwrap().is_empty());
    assert_eq!(
        doc.digest(),
        "a84851e3b56f08c566d19cc0ac08d0cc07289e17c5c286e2a3b51cf71c89368c"
    ); // updated from the candidate vector
    let saved = ws.save_flow(doc.clone(), 0).unwrap();
    let path = fixture.0.join("flow.json");
    let bytes = saved.bytes();
    assert_eq!(saved.file_sha256, sha(&bytes));
    crate::infrastructure::ca_store::atomic(&path, &bytes, false).unwrap();
    assert!(crate::infrastructure::ca_store::atomic(&path, b"changed", false).is_err());
    let p = ws.preview_flow(path, &bytes).unwrap();
    assert_eq!(p["status"], "identical");
    assert_eq!(
        ws.import_flow(p["token"].as_str().unwrap(), None)
            .unwrap()
            .document,
        doc
    );
    let mut moved = doc.clone();
    moved
        .layout
        .as_mut()
        .unwrap()
        .nodes
        .get_mut("read_status")
        .unwrap()
        .x += 1.;
    assert_eq!(doc.digest(), moved.digest());
    let new = ws.save_flow(moved, 1).unwrap();
    assert_ne!(saved.file_sha256, new.file_sha256);
    assert_eq!(ws.get_flow("status_gate", 1).unwrap().document, doc);
    let original: Value = serde_json::from_slice(FLOW).unwrap();
    for (p, v) in [
        ("/schema_version", json!(2)),
        ("/flow/nodes/0/version", json!(2)),
        ("/flow/edges/0/to_node_id", json!("missing")),
        ("/flow/edges/0/from_port", json!("true")),
        ("/flow/edges/2/to_node_id", json!("read_status")),
        ("/flow/edges/2/to_node_id", json!("end_false")),
        ("/flow/nodes/1/config/left/node_id", json!("get_info")),
        ("/flow/nodes/1/config/right/type", json!("boolean")),
        ("/flow/nodes/1/config/right/value", Value::Null),
    ] {
        let mut c = original.clone();
        *c.pointer_mut(p).unwrap() = v;
        let mutant: Document = serde_json::from_value(c).unwrap();
        assert!(!ws.validate(&mutant).unwrap().is_empty(), "{p}");
    }
}

fn intent(doc: &Document, index: usize, real: bool) -> Intent {
    Intent {
        flow_id: doc.flow.flow_id.clone(),
        revision: doc.flow.revision,
        node: doc.flow.nodes[index].clone(),
        document: doc.clone(),
        real,
        timeout_ms: 2100,
        inputs: BTreeMap::from([(
            "read_status.value".into(),
            Literal {
                kind: Kind::Int16,
                value: json!(1),
            },
        )]),
        sample: Some(Literal {
            kind: Kind::Int16,
            value: json!(-42),
        }),
        fake_outcome: None,
    }
}
fn once(ws: &Workspace, i: Intent) -> Value {
    let p = preview(ws, i).unwrap();
    let t = p["token"].as_str().unwrap();
    let result = run(ws, t, true).unwrap();
    assert!(run(ws, t, true).is_err());
    assert_eq!(result["actual_io"], false);
    result
}

#[test]
fn selected_node_simulation_fake_get_post_read_and_restart() {
    let fixture = Fixture::new();
    let ws = fixture.workspace();
    prepare(&ws, &fixture);
    let mut doc: Document = checked_json(FLOW).unwrap();
    let sim = once(&ws, intent(&doc, 0, false));
    assert_eq!(sim["output"]["value"], -42);
    let s7 = once(&ws, intent(&doc, 0, true));
    assert_eq!(s7["target"]["db"], 21);
    assert_eq!(s7["target"]["byte"], 2);
    assert_eq!(s7["output"]["value"], 1);
    assert_eq!(s7["output"]["quality"], "good");
    let result = once(&ws, intent(&doc, 2, true));
    assert_eq!(result["target"]["query"]["status"], 1);
    assert_eq!(result["timeout_ms"], 2100);
    assert_eq!(result["output"]["response"]["method"], "GET");
    let mut wrong = intent(&doc, 2, true);
    wrong.inputs.insert(
        "read_status.value".into(),
        Literal {
            kind: Kind::String,
            value: json!("1"),
        },
    );
    assert!(preview(&ws, wrong).is_err());
    if let NodeBody::Http(h) = &mut doc.flow.nodes[2].body {
        h.method = Method::Post;
        h.query.insert(
            "encoded".into(),
            Operand::Value(Literal {
                kind: Kind::String,
                value: json!("a/? &"),
            }),
        );
        h.body.insert("count".into(), h.query["status"].clone());
    }
    let p = preview(&ws, intent(&doc, 2, true)).unwrap();
    let token = p["token"].as_str().unwrap();
    let Pending::Test(ready) = ws.consume(token).unwrap() else {
        panic!("wrong token")
    };
    let Request::Http {
        url,
        method,
        headers,
        body,
    } = ready.request
    else {
        panic!("wrong request")
    };
    assert_eq!(method, Method::Post);
    assert_eq!(
        url.as_str(),
        "https://fixture.invalid/status?encoded=a%2F%3F+%26&status=1"
    );
    assert_eq!(ready.timeout, Duration::from_millis(2100));
    assert_eq!(headers["Authorization"], "test-secret");
    assert_eq!(body.unwrap()["count"], 1);
    assert!(!p.to_string().contains("test-secret"));
    let p = preview(&ws, intent(&doc, 2, true)).unwrap();
    assert!(run(&ws, p["token"].as_str().unwrap(), false).is_err());
    let post = once(&ws, intent(&doc, 2, true));
    assert_eq!(post["status"], "response_received");
    assert_eq!(post["output"]["response"]["body"]["count"], 1);
    let mut fail = intent(&doc, 2, true);
    fail.fake_outcome = Some(FakeOutcome::BeforeSend);
    assert_eq!(once(&ws, fail)["status"], "failed_before_send");
    let mut ambiguous = intent(&doc, 2, true);
    ambiguous.fake_outcome = Some(FakeOutcome::Unknown);
    let unknown = once(&ws, ambiguous);
    assert_eq!(unknown["status"], "unknown");
    let reopened = fixture.workspace();
    assert_eq!(reopened.snapshot().unwrap().tests.len(), 6);
    assert_eq!(
        reopened.snapshot().unwrap().tests.last().unwrap()["id"],
        unknown["id"]
    );
    assert_eq!(
        reopened.snapshot().unwrap().tests.last().unwrap()["status"],
        "unknown"
    );
}

#[test]
fn reconverging_branches_share_the_validator_and_node_test_input_rules() {
    use crate::domain::ca_flow::{Edge, Reference};
    let fixture = Fixture::new();
    let ws = fixture.workspace();
    prepare(&ws, &fixture);
    let mut doc: Document = checked_json(FLOW).unwrap();
    doc.layout = None;
    let downstream = "get_info";
    doc.flow.nodes.retain(|node| node.id != "end_false");
    doc.flow.edges[3].to_node_id = downstream.into();
    let NodeBody::Http(get) = &mut doc.flow.nodes[2].body else {
        panic!("sample GET");
    };
    get.query.insert(
        "matched".into(),
        Operand::Ref(Reference {
            node_id: "check_status".into(),
            field: "matched".into(),
        }),
    );
    assert!(ws.validate(&doc).unwrap().is_empty());
    let mut request = intent(&doc, 2, true);
    request.inputs.insert(
        "check_status.matched".into(),
        Literal {
            kind: Kind::Boolean,
            value: json!(true),
        },
    );
    let result = once(&ws, request);
    assert_eq!(
        result["target"]["query"],
        json!({"matched":true,"status":1})
    );

    let mut branch_only = doc.flow.nodes[2].clone();
    branch_only.id = "branch_only".into();
    doc.flow.nodes.push(branch_only);
    doc.flow.edges[3].to_node_id = "branch_only".into();
    doc.flow.edges.push(Edge {
        from_node_id: "branch_only".into(),
        from_port: "next".into(),
        to_node_id: downstream.into(),
    });
    assert!(ws.validate(&doc).unwrap().is_empty());

    let mut request = intent(&doc, 2, true);
    request.inputs.insert(
        "check_status.matched".into(),
        Literal {
            kind: Kind::String,
            value: json!("true"),
        },
    );
    assert_eq!(preview(&ws, request).unwrap_err(), "test_input_invalid");

    let NodeBody::Http(get) = &mut doc.flow.nodes[2].body else {
        panic!("sample GET");
    };
    get.query.insert(
        "conditional".into(),
        Operand::Ref(Reference {
            node_id: "branch_only".into(),
            field: "status".into(),
        }),
    );
    assert!(ws
        .validate(&doc)
        .unwrap()
        .iter()
        .any(|issue| issue.code == "invalid_config_or_reference"));
    let mut request = intent(&doc, 2, true);
    request.inputs.insert(
        "branch_only.status".into(),
        Literal {
            kind: Kind::Int16,
            value: json!(200),
        },
    );
    assert_eq!(preview(&ws, request).unwrap_err(), "test_reference_invalid");
}

#[test]
fn source_change_exposes_db_enabled_and_unknown_without_overwriting_catalog() {
    let fixture = Fixture::new();
    let ws = fixture.workspace();
    let source = catalog(&ws, &fixture, "original.json", DS, "original");
    let mut changed: Value = serde_json::from_slice(DS).unwrap();
    let db = changed["dbs"][0]["id"].clone();
    changed["dbs"][0]["source_enabled"] = json!(false);
    let raw = serde_json::to_vec(&changed).unwrap();
    let path = fixture.file("disabled.json", &raw);
    let preview = ws.preview_catalog(path, &raw).unwrap();
    assert_eq!(preview["status"], "changed");
    assert_eq!(preview["diff"]["changed"], json!([]));
    let delta = &preview["diff"]["db_changes"][0];
    assert_eq!(delta["id"], db);
    assert_eq!(delta["before"]["source_enabled"], true);
    assert_eq!(delta["after"]["source_enabled"], false);
    assert_eq!(ws.snapshot().unwrap().catalogs[0].raw.as_bytes(), DS);

    // An unchanged origin can be re-exported by DAA, which omits DB-level source facts.
    changed["export"]["producer"] = json!("data_acquisition_agent");
    changed["export"]["config_state"] = json!("active_revision");
    for db in changed["dbs"].as_array_mut().unwrap() {
        db.as_object_mut().unwrap().remove("source_enabled");
    }
    let raw = serde_json::to_vec(&changed).unwrap();
    let path = fixture.file("absent.json", &raw);
    let preview = ws.preview_catalog(path, &raw).unwrap();
    let delta = preview["diff"]["db_changes"]
        .as_array()
        .unwrap()
        .iter()
        .find(|item| item["before"]["source_enabled"] == false)
        .unwrap();
    assert!(delta["after"]["source_enabled"].is_null());
    assert!(delta["after"]["number"].is_u64()); // DB remains present.
    assert_eq!(
        ws.snapshot().unwrap().catalogs[0].file_sha256,
        source["file_sha256"]
    );
}
