//! 先行手写oracle逐叶对照及完整拒绝/原子人工保护，不以待测算法生成期望。
use super::*;
use crate::{
    domain::{local_sample::digest, source_import::*},
    infrastructure::tia_source,
};
fn config() -> Configuration {
    let mut c = Configuration::default();
    let plc = id();
    c.plcs.push(Plc {
        id: plc.clone(),
        name: "Oracle".into(),
        enabled: false,
        host: "127.0.0.1".into(),
        port: 102,
        rack: 0,
        slot: 1,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    });
    let text = include_str!("../../../tests/fixtures/source-import-multi-db/layout.db");
    let s = SourceDocument {
        id: String::new(),
        name: "layout.db".into(),
        content: text.into(),
        sha256: digest(text),
        plc_id: plc.clone(),
        db_number: None,
        diagnostics: vec![],
        lineage_id: None,
    };
    let mut r = ImportRequest {
        sources: vec![s],
        expected_etag: String::new(),
        confirm: false,
        stage: None,
        target_plc_id: Some(plc),
        mappings: vec![],
        preview_token: None,
        raw_proofs: vec![],
    };
    r.mappings = tia_source::identify(&c, &r)
        .unwrap()
        .blocks
        .into_iter()
        .filter(|b| b.block_key.kind == "DATA_BLOCK")
        .enumerate()
        .map(|(n, b)| BlockMapping {
            source_index: b.source_index,
            block_key: b.block_key,
            selected: true,
            db_number: Some(701 + n as u16),
            target_id: None,
        })
        .collect();
    let p = tia_source::plan(&c, &r).unwrap();
    assert!(p.can_confirm, "{:?}", p.issues);
    p.configuration
}
#[test]
fn prior_oracle_all_leaf_offsets_lengths_and_strides() {
    let c = config();
    let oracle: serde_json::Value = serde_json::from_str(include_str!(
        "../../../tests/fixtures/source-import-multi-db/layout-oracle.json"
    ))
    .unwrap();
    for case in oracle["cases"].as_array().unwrap() {
        let db = c
            .dbs
            .iter()
            .find(|d| d.name == case["name"].as_str().unwrap())
            .unwrap();
        let got = preview(&c, &db.id).unwrap();
        assert_eq!(got.len(), case["leaves"].as_array().unwrap().len());
        for (exp, row) in case["leaves"].as_array().unwrap().iter().zip(&got) {
            let point = c.points.iter().find(|p| p.id == row.point_id).unwrap();
            assert_eq!(
                serde_json::json!({"path":point.source_path,"byte":row.proposed.offset,"bit":row.proposed.bit}),
                *exp
            );
            assert_eq!(row.db_length as u64, case["length"].as_u64().unwrap());
            assert!(!row.proposed.confirmed);
        }
        assert!(c.points.iter().all(|p| p.address.is_none()));
    }
}
#[test]
fn whole_db_refusal_bounds_proof_and_manual_atomicity() {
    let mut c = config();
    let db = c
        .dbs
        .iter()
        .find(|d| d.name == "Nested")
        .unwrap()
        .id
        .clone();
    let offsets = preview(&c, &db).unwrap();
    let first = offsets[0].point_id.clone();
    let second = offsets[1].point_id.clone();
    c.points
        .iter_mut()
        .find(|p| p.id == second)
        .unwrap()
        .address = Some(Address {
        offset: 100,
        bit: Some(1),
        confirmed: false,
        origin: "manual".into(),
        reason: "manual kept".into(),
    });
    let before = c.clone();
    assert!(confirm(&mut c, &db, &[first.clone(), second]).is_err());
    assert_eq!(before, c);
    assert!(confirm(&mut c, &db, &[first.clone(), first]).is_err());
    assert_eq!(before, c);
    let xs = preview(&c, &db).unwrap();
    assert!(xs.iter().any(|x| x.manual_conflict));
    let ids = xs
        .iter()
        .filter(|x| !x.protected_manual)
        .map(|x| x.point_id.clone())
        .collect::<Vec<_>>();
    confirm(&mut c, &db, &ids).unwrap();
    assert_eq!(c.dbs.iter().find(|d| d.id == db).unwrap().length, 65536);
    assert!(c.points.iter().filter(|p| ids.contains(&p.id)).all(|p| p
        .address
        .as_ref()
        .unwrap()
        .confirmed));
    assert_eq!(
        c.points
            .iter()
            .find(|p| p
                .address
                .as_ref()
                .map(|a| a.origin == "manual")
                .unwrap_or(false))
            .unwrap()
            .address
            .as_ref()
            .unwrap()
            .reason,
        "manual kept"
    );
    let mut bad = config();
    bad.dbs[0].length = 1;
    assert!(preview(&bad, &bad.dbs[0].id).is_err());
    let mut bad = config();
    bad.sources[0].content.push(' ');
    assert!(preview(&bad, &bad.dbs[0].id).is_err());
    let mut bad = config();
    bad.dbs[0].tree[0].data_type = "REAL".into();
    assert!(preview(&bad, &bad.dbs[0].id).is_err());
    let c = config();
    let mut cursor = u32::MAX;
    assert!(layout(&c.dbs[0].tree, &mut cursor, &mut vec![], 0).is_err());
}
#[test]
fn string_optimized_missing_profile_never_partial_layout() {
    for fields in ["x: STRING[8]; y: WORD;", "x: Missing; y: WORD;"] {
        let mut c = config();
        let text=format!("DATA_BLOCK \"Bad\" {{ S7_Optimized_Access := 'FALSE' }} VAR {fields} END_VAR BEGIN END_DATA_BLOCK");
        let s = SourceDocument {
            id: String::new(),
            name: "bad.db".into(),
            content: text,
            sha256: String::new(),
            plc_id: c.plcs[0].id.clone(),
            db_number: Some(8),
            diagnostics: vec![],
            lineage_id: None,
        };
        let p = tia_source::import(&c, vec![s]).unwrap();
        if p.can_confirm {
            c = p.configuration;
            let db = c.dbs.iter().find(|d| d.name == "Bad").unwrap();
            assert!(preview(&c, &db.id).is_err());
        } else {
            assert!(!p.issues.is_empty());
        }
    }
    let mut c = config();
    c.sources[0].content = c.sources[0].content.replace("'FALSE'", "'TRUE'");
    c.sources[0].sha256 = digest(&c.sources[0].content);
    assert!(preview(&c, &c.dbs[0].id).is_err());
}
