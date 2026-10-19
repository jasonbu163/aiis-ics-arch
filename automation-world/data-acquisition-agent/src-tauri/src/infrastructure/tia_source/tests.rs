//! DAA-005纯函数定向验证：手写公开期望、完整拒绝、版本闭包与保全差异。
use super::*;
use crate::domain::{local_configuration::*, local_sample::digest, source_import::*};
fn base() -> Configuration {
    let mut c = Configuration::default();
    for n in 1..=2 {
        c.plcs.push(Plc {
            id: id(),
            name: format!("Synthetic {n}"),
            enabled: false,
            host: format!("127.0.0.{n}"),
            port: 102,
            rack: 0,
            slot: 1,
            connect_timeout_ms: 1000,
            io_timeout_ms: 500,
            deadline_ms: 5000,
        });
    }
    c
}
fn request(c: &Configuration, docs: &[(&str, &str)]) -> ImportRequest {
    let sources: Vec<_> = docs
        .iter()
        .map(|(name, text)| SourceDocument {
            id: String::new(),
            name: (*name).into(),
            content: (*text).into(),
            sha256: digest(text),
            plc_id: c.plcs[0].id.clone(),
            db_number: None,
            diagnostics: vec![],
            lineage_id: None,
        })
        .collect();
    ImportRequest {
        raw_proofs: sources
            .iter()
            .map(|s| RawProof {
                sha256: s.sha256.clone(),
                bytes: s.content.len(),
            })
            .collect(),
        sources,
        expected_etag: "synthetic-etag".into(),
        confirm: false,
        stage: Some("preview".into()),
        target_plc_id: Some(c.plcs[0].id.clone()),
        mappings: vec![],
        preview_token: None,
    }
}
fn mapped(c: &Configuration, docs: &[(&str, &str)]) -> ImportRequest {
    let mut r = request(c, docs);
    let i = identify(c, &r).unwrap();
    r.mappings = i
        .blocks
        .into_iter()
        .filter(|b| b.block_key.kind == "DATA_BLOCK")
        .enumerate()
        .map(|(j, b)| BlockMapping {
            source_index: b.source_index,
            block_key: b.block_key,
            selected: true,
            db_number: Some(b.suggested_db_number.unwrap_or(501 + j as u16)),
            target_id: b.target_id,
        })
        .collect();
    r
}
const MULTI: &str = include_str!("../../../tests/fixtures/source-import-multi-db/multi.db");
const TYPES: &str = include_str!("../../../tests/fixtures/source-import-multi-db/types.udt");
fn one(fields: &str) -> String {
    format!("DATA_BLOCK \"One\" {{ S7_Optimized_Access := 'FALSE' }} VAR {fields} END_VAR BEGIN END_DATA_BLOCK")
}
#[test]
fn rework1_eight_container_boundary_inline_and_udt() {
    let c = base();
    for depth in [7, 8, 9] {
        let text = one(&format!(
            "{}leaf: BYTE;{}",
            "s: STRUCT ".repeat(depth),
            " END_STRUCT;".repeat(depth)
        ));
        let r = mapped(&c, &[("depth.db", &text)]);
        let i = identify(&c, &r).unwrap();
        let p = plan(&c, &r).unwrap();
        assert_eq!(p.can_confirm, depth <= 8, "depth={depth}: {:?}", p.issues);
        if depth <= 8 {
            assert_eq!(i.blocks[0].leaf_count, 1);
            let db = &p.configuration.dbs[0];
            let offsets =
                crate::infrastructure::plc_layout::preview(&p.configuration, &db.id).unwrap();
            assert_eq!(offsets.len(), 1);
            assert_eq!(offsets[0].proposed.offset, 0);
            assert_eq!(offsets[0].proposed.bit, None);
        } else {
            assert!(i.blocks[0]
                .issues
                .iter()
                .any(|i| i.code == "expansion_depth"));
            assert_eq!(p.configuration, c);
        }
    }
    let mut udts = "TYPE T0 STRUCT leaf: BYTE; END_STRUCT; END_TYPE\n".to_string();
    for level in 1..8 {
        udts.push_str(&format!(
            "TYPE T{level} STRUCT s: T{}; END_STRUCT; END_TYPE\n",
            level - 1
        ));
    }
    let r = mapped(&c, &[("depth.db", &one("s: T7;")), ("depth.udt", &udts)]);
    let p = plan(&c, &r).unwrap();
    assert!(p.can_confirm, "{:?}", p.issues);
    assert_eq!(p.configuration.points.len(), 1);
    assert_eq!(p.configuration.sources.len(), 2);
    assert_eq!(
        p.configuration.dbs[0]
            .import_binding
            .as_ref()
            .unwrap()
            .udt_source_ids
            .len(),
        1
    );
    crate::infrastructure::plc_layout::preview(&p.configuration, &p.configuration.dbs[0].id)
        .unwrap();
    let r = mapped(
        &p.configuration,
        &[("depth.db", &one("s: T7;")), ("depth.udt", &udts)],
    );
    let repeated = plan(&p.configuration, &r).unwrap();
    assert!(
        repeated.can_confirm && repeated.unchanged,
        "{:?}",
        repeated.issues
    );
    assert_eq!(repeated.configuration, p.configuration);
    let mut other = r.clone();
    other.target_plc_id = Some(c.plcs[1].id.clone());
    for source in &mut other.sources {
        source.plc_id = c.plcs[1].id.clone();
    }
    other.mappings[0].target_id = None;
    let second_plc = plan(&p.configuration, &other).unwrap();
    assert!(second_plc.can_confirm, "{:?}", second_plc.issues);
    assert_eq!(second_plc.configuration.sources.len(), 4);
    assert_eq!(second_plc.configuration.dbs[0], p.configuration.dbs[0]);
    for source in &p.configuration.sources {
        assert!(second_plc.configuration.sources.contains(source));
    }
    assert!(crate::infrastructure::plc_layout::preview(
        &second_plc.configuration,
        &second_plc.configuration.dbs[1].id
    )
    .is_ok());
    let duplicate = format!("{udts}\nTYPE T0 STRUCT other: WORD; END_STRUCT; END_TYPE");
    let r = mapped(
        &c,
        &[("depth.db", &one("s: T7;")), ("depth.udt", &duplicate)],
    );
    let rejected = plan(&c, &r).unwrap();
    assert!(!rejected.can_confirm);
    assert!(rejected.issues.iter().any(|i| i.code == "duplicate_udt"));
    assert_eq!(rejected.configuration, c);
    let mut empty = "TYPE T0 STRUCT END_STRUCT; END_TYPE\n".to_string();
    for level in 1..9 {
        empty.push_str(&format!(
            "TYPE T{level} STRUCT s: T{}; END_STRUCT; END_TYPE\n",
            level - 1
        ));
    }
    let r = mapped(
        &c,
        &[
            ("depth.db", &one("s: T8; tail: BYTE;")),
            ("depth.udt", &empty),
        ],
    );
    let rejected = plan(&c, &r).unwrap();
    assert!(!rejected.can_confirm);
    assert!(rejected.issues.iter().any(|i| i.code == "expansion_depth"));
    assert_eq!(rejected.configuration, c);
}
#[test]
fn rework1_field_diagnostics_keep_real_definition_location() {
    let c = base();
    let direct = "DATA_BLOCK \"Located\"\n{ S7_Optimized_Access := 'FALSE' }\nVAR\n  box: STRUCT\n    leaf: Missing;\n  END_STRUCT;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK";
    let db = "DATA_BLOCK \"Located\"\n{ S7_Optimized_Access := 'FALSE' }\nVAR\n  box: Outer;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK";
    let udt = "TYPE Outer\nSTRUCT\n  inner: Inner;\nEND_STRUCT;\nEND_TYPE\nTYPE Inner\nSTRUCT\n  leaf: Missing;\nEND_STRUCT;\nEND_TYPE";
    for (docs, file, line, path) in [
        (
            vec![("located.db", direct)],
            "located.db",
            5,
            "Located.box.leaf",
        ),
        (
            vec![("located.db", db), ("definition.udt", udt)],
            "definition.udt",
            8,
            "Located.box.inner.leaf",
        ),
    ] {
        let r = mapped(&c, &docs);
        let i = identify(&c, &r).unwrap();
        let p = plan(&c, &r).unwrap();
        assert!(!p.can_confirm);
        assert_eq!(p.configuration, c);
        assert_eq!(i.blocks[0].block_key.name, "Located");
        for issues in [&i.blocks[0].issues, &p.issues] {
            let issue = issues.iter().find(|i| i.code == "udt_missing").unwrap();
            assert_eq!((&*issue.file, issue.line, &*issue.path), (file, line, path));
        }
    }
    for (fields, definition, code, line, path) in [
        (
            "box: Loop;",
            "TYPE Loop\nSTRUCT\n  again: Loop;\nEND_STRUCT;\nEND_TYPE",
            "udt_cycle",
            3,
            "One.box.again",
        ),
        (
            "box: ARRAY[0..0] OF Unit;",
            "TYPE Unit\nSTRUCT\n  bytes: ARRAY[1..2] OF BYTE;\nEND_STRUCT;\nEND_TYPE",
            "nested_array",
            3,
            "One.box[0].bytes",
        ),
    ] {
        let text = one(fields);
        let r = mapped(&c, &[("located.db", &text), ("definition.udt", definition)]);
        let i = identify(&c, &r).unwrap();
        let p = plan(&c, &r).unwrap();
        assert!(!p.can_confirm);
        assert_eq!(p.configuration, c);
        for issues in [&i.blocks[0].issues, &p.issues] {
            let issue = issues.iter().find(|i| i.code == code).unwrap();
            assert_eq!(
                (&*issue.file, issue.line, &*issue.path),
                ("definition.udt", line, path)
            );
        }
    }
}
#[test]
fn public_six_db_three_type_structure_and_default_expected() {
    let c = base();
    let r = mapped(&c, &[("multi.db", MULTI), ("types.udt", TYPES)]);
    let i = identify(&c, &r).unwrap();
    assert_eq!((i.db_count, i.udt_count), (6, 3));
    assert!(i.blocks.iter().all(|b| b.issues.is_empty()));
    let p = plan(&c, &r).unwrap();
    assert!(p.can_confirm, "{:?}", p.issues);
    let expected: serde_json::Value = serde_json::from_str(include_str!(
        "../../../tests/fixtures/source-import-multi-db/expected.json"
    ))
    .unwrap();
    for db in &p.configuration.dbs {
        let got: Vec<_> = p
            .configuration
            .points
            .iter()
            .filter(|p| p.db_id == db.id)
            .map(|p| serde_json::json!([p.source_path, p.data_type]))
            .collect();
        assert_eq!(serde_json::json!(got), expected["blocks"][&db.name]);
        assert!(db.complete);
        assert!(p
            .configuration
            .points
            .iter()
            .filter(|p| p.db_id == db.id)
            .all(|p| !p.enabled && p.group_id.is_none() && p.address.is_none()));
    }
    assert_eq!(p.configuration.sources.len(), 2);
}
#[test]
fn byte_proof_bom_crlf_and_forgery() {
    let c = base();
    let text = format!(
        "\u{feff}{}",
        one("x: BOOL;\r\ny: WORD;").replace(" VAR ", "\r\nVAR\r\n")
    );
    let mut r = mapped(&c, &[("bom.db", &text)]);
    let p = plan(&c, &r).unwrap();
    assert!(p.can_confirm);
    assert_eq!(
        p.configuration.sources[0].content.as_bytes(),
        text.as_bytes()
    );
    assert_eq!(p.configuration.sources[0].sha256, digest(&text));
    r.raw_proofs[0].bytes -= 3;
    assert!(plan(&c, &r).is_err());
    r.raw_proofs[0].bytes += 3;
    r.raw_proofs[0].sha256 = digest("lossy replacement");
    assert!(identify(&c, &r).is_err());
}
#[test]
fn identifiable_bad_block_can_be_deselected_but_file_boundary_is_fatal() {
    let c = base();
    let text = format!(
        "{}\n{}",
        one("x: BOOL;"),
        one("x: POINTER;").replace("One", "Bad")
    );
    let mut r = mapped(&c, &[("partial.db", &text)]);
    let i = identify(&c, &r).unwrap();
    assert_eq!(i.db_count, 2);
    assert!(!i.blocks[1].issues.is_empty());
    assert!(!plan(&c, &r).unwrap().can_confirm);
    r.mappings[1].selected = false;
    assert!(plan(&c, &r).unwrap().can_confirm);
    for broken in [
        text.replace("END_DATA_BLOCK", ""),
        text + "\n\"unterminated",
        one("x: BOOL;") + " (*",
    ] {
        assert!(identify(&c, &request(&c, &[("bad.db", &broken)])).is_err());
    }
}
#[test]
fn syntax_dependency_limits_and_ambiguous_paths_fail_closed() {
    let c = base();
    for fields in [
        "x: ARRAY[0..1024] OF BOOL;",
        "x: ARRAY[2..1] OF BYTE;",
        "x: ARRAY[0..1,0..1] OF BYTE;",
        "x: ARRAY[0..1] OF ARRAY[0..1] OF BYTE;",
        "x { Unknown := 'false' }: BOOL;",
        "x { S7_SetPoint := 'other' }: BOOL;",
        "x: BOOL; X: BYTE;",
        "x: Missing;",
        "x: AT;",
        "\"a.b\": BYTE; a: STRUCT b: BYTE; END_STRUCT;",
    ] {
        let text = one(fields);
        let r = mapped(&c, &[("bad.db", &text)]);
        assert!(!plan(&c, &r).unwrap().can_confirm, "{fields}");
    }
    let text = one("x: Loop;");
    let types = "TYPE Loop STRUCT again: Loop; END_STRUCT; END_TYPE";
    let r = mapped(&c, &[("bad.db", &text), ("types.udt", types)]);
    assert!(!plan(&c, &r).unwrap().can_confirm);
    let deep = one(&format!(
        "{} x: BYTE; {}",
        "s: STRUCT ".repeat(10),
        " END_STRUCT;".repeat(10)
    ));
    assert!(
        !plan(&c, &mapped(&c, &[("deep.db", &deep)]))
            .unwrap()
            .can_confirm
    );
}
#[test]
fn number_target_and_legacy_rules() {
    let c = base();
    let mut r = mapped(&c, &[("multi.db", MULTI), ("types.udt", TYPES)]);
    r.mappings[1].db_number = r.mappings[0].db_number;
    assert!(!plan(&c, &r).unwrap().can_confirm);
    r.mappings[0].db_number = None;
    assert!(!plan(&c, &r).unwrap().can_confirm);
    assert!(legacy_import(&c, r.sources.clone()).is_err());
    let text = one("x: BOOL;");
    let mut src = request(&c, &[("one.db", &text)]).sources.remove(0);
    src.db_number = Some(12);
    let mut old = legacy_import(&c, vec![src]).unwrap().configuration;
    old.dbs[0].import_binding = None;
    old.sources[0].lineage_id = None;
    old.sources[0].db_number = Some(12);
    assert!(verify_db(&old, &old.dbs[0]).is_ok());
    let json = serde_json::to_string(&old).unwrap();
    assert!(!json.contains("importBinding"));
    assert!(!json.contains("lineageId"));
    let decoded: Configuration = serde_json::from_str(&json).unwrap();
    assert_eq!(decoded, old);
    let r = mapped(&old, &[("one.db", &text)]);
    assert_eq!(r.mappings[0].db_number, Some(12));
    let mut cross = r.clone();
    cross.mappings[0].target_id = Some(c.plcs[1].id.clone());
    assert!(!plan(&old, &cross).unwrap().can_confirm);
    let mut renumber = r;
    renumber.mappings[0].db_number = Some(13);
    assert!(!plan(&old, &renumber).unwrap().can_confirm);
}
#[test]
fn delta_preserves_configuration_and_blocks_deletion_rename() {
    let c = base();
    let text = one("x: BOOL; y: WORD;");
    let mut old = plan(&c, &mapped(&c, &[("one.db", &text)]))
        .unwrap()
        .configuration;
    old.groups.push(Group {
        id: id(),
        plc_id: old.plcs[0].id.clone(),
        name: "Synthetic group".into(),
        enabled: false,
        interval_ms: 500,
    });
    for p in &mut old.points {
        p.name = "User name".into();
        p.comment = "User annotation".into();
        p.group_id = Some(old.groups[0].id.clone());
        p.address = Some(Address {
            offset: 7,
            bit: if p.data_type == "BOOL" { Some(1) } else { None },
            confirmed: true,
            origin: "manual".into(),
            reason: "Keep my review".into(),
        });
    }
    let same = plan(&old, &mapped(&old, &[("one.db", &text)])).unwrap();
    assert!(same.unchanged);
    assert_eq!(old, same.configuration);
    for fields in [
        "x: BOOL; y: WORD; z: BYTE;",
        "x: BOOL; y: REAL;",
        "y: WORD; x: BOOL;",
    ] {
        let changed = one(fields);
        let mut r = mapped(&old, &[("one.db", &changed)]);
        r.mappings[0].target_id = Some(old.dbs[0].id.clone());
        r.mappings[0].db_number = Some(old.dbs[0].number);
        let p = plan(&old, &r).unwrap();
        assert!(p.can_confirm, "{:?}", p.issues);
        for prior in &old.points {
            let after = p
                .configuration
                .points
                .iter()
                .find(|p| p.id == prior.id)
                .unwrap();
            assert_eq!(after.name, prior.name);
            assert_eq!(after.comment, prior.comment);
            assert_eq!(after.group_id, prior.group_id);
            let a = after.address.as_ref().unwrap();
            assert_eq!(
                (a.offset, &a.reason),
                (7, &prior.address.as_ref().unwrap().reason)
            );
            assert!(!a.confirmed);
        }
        assert_eq!(p.deltas[0].invalidated_confirmations, 2);
    }
    for fields in ["x: BOOL;", "renamed: BOOL; y: WORD;"] {
        let mut r = mapped(&old, &[("one.db", &one(fields))]);
        r.mappings[0].target_id = Some(old.dbs[0].id.clone());
        r.mappings[0].db_number = Some(old.dbs[0].number);
        let p = plan(&old, &r).unwrap();
        assert!(!p.can_confirm);
        assert_eq!(p.configuration, old);
    }
    let renamed = text.replace("One", "Renamed");
    let mut r = mapped(&old, &[("one.db", &renamed)]);
    r.mappings[0].target_id = Some(old.dbs[0].id.clone());
    assert!(!plan(&old, &r).unwrap().can_confirm);
    let comments = text.replace("y: WORD;", "y: WORD; // changed comment\n");
    let mut r = mapped(&old, &[("one.db", &comments)]);
    r.mappings[0].target_id = Some(old.dbs[0].id.clone());
    let p = plan(&old, &r).unwrap();
    assert!(p.can_confirm);
    assert!(!p.deltas[0].layout_changed);
    assert!(p
        .configuration
        .points
        .iter()
        .all(|p| p.address.as_ref().unwrap().confirmed));
    assert_eq!(p.configuration.sources.len(), 2);
}
#[test]
fn shared_udt_only_selected_db_changes_and_sources_are_immutable() {
    let c = base();
    let old = plan(
        &c,
        &mapped(&c, &[("multi.db", MULTI), ("types.udt", TYPES)]),
    )
    .unwrap()
    .configuration;
    let new_types = TYPES.replace("value : REAL;", "value : DINT;");
    let mut r = mapped(&old, &[("multi.db", MULTI), ("types.udt", &new_types)]);
    for m in &mut r.mappings {
        m.selected = m.block_key.name == "Beta";
    }
    let p = plan(&old, &r).unwrap();
    assert!(p.can_confirm, "{:?}", p.issues);
    assert_eq!(p.configuration.sources.len(), 3);
    for db in old.dbs.iter().filter(|d| d.name != "Beta") {
        assert_eq!(
            p.configuration.dbs.iter().find(|d| d.id == db.id).unwrap(),
            db
        );
        assert_eq!(
            p.configuration
                .points
                .iter()
                .filter(|p| p.db_id == db.id)
                .collect::<Vec<_>>(),
            old.points
                .iter()
                .filter(|p| p.db_id == db.id)
                .collect::<Vec<_>>()
        );
        assert!(verify_db(&p.configuration, db).is_ok());
    }
    for s in &old.sources {
        assert!(p.configuration.sources.contains(s));
    }
    let beta = p
        .configuration
        .dbs
        .iter()
        .find(|d| d.name == "Beta")
        .unwrap();
    assert!(verify_db(&p.configuration, beta).is_ok());
}
