//! DAA-006真实Engine/Stores定向证据；自有双库旧JSON、预览取消/CAS、模式保护及一次事务回滚。
use super::source_import_tests::{confirm, dump, engine, old_seed, profile, protected, req};
use super::*;
use crate::domain::{local_configuration::*, local_sample::digest, point_naming::*};
use crate::services::local_supervisor::LocalEngine;
use serde_json::{json, Value};
fn request(e: &LocalEngine, ids: Vec<String>) -> NameRequest {
    let v = e.configuration().unwrap();
    NameRequest {
        expected_etag: v.etag,
        plc_id: v.draft.plcs[0].id.clone(),
        point_ids: ids,
        intent: "generate".into(),
        patch: None,
    }
}
fn confirmed(r: NameRequest, p: &NamePreview) -> NameConfirmation {
    NameConfirmation {
        input: r,
        preview_token: p.preview_token.clone(),
        input_digest: p.input_digest.clone(),
    }
}
#[test]
fn old_json_selected_cancel_cas_modes_and_history_bytes() {
    let p = profile("daa006-names");
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let original = old_seed(&mut s, &p);
    let raw: String = s
        .config
        .query_row(
            "SELECT payload FROM configuration_draft WHERE id=1",
            [],
            |r| r.get(0),
        )
        .unwrap();
    assert!(!raw.contains("nameMode"));
    let before = protected(&s);
    let archive = dump(&s.config, &["source_documents"]);
    s.clean_exit().unwrap();
    drop(s);
    let e = engine(&p);
    let v = e.configuration().unwrap();
    assert_eq!(v.draft, original);
    assert_eq!(
        e.storage
            .call(true, |s| s
                .config
                .query_row(
                    "SELECT payload FROM configuration_draft WHERE id=1",
                    [],
                    |r| r.get::<_, String>(0)
                )
                .map_err(sql_error))
            .unwrap(),
        raw
    );
    let pid = v.draft.points[0].id.clone();
    let r = request(&e, vec![pid.clone()]);
    let pr = e.preview_point_names(r.clone()).unwrap();
    assert!(pr.can_confirm);
    assert_eq!(pr.rows[0].old_name, "User value");
    assert_eq!(pr.rows[0].proposed_name, "DB501_value_Word");
    assert_eq!(e.configuration().unwrap().etag, v.etag);
    // Cancel/reload zero writes and invalidates the cached token.
    crate::commands::local_acquisition::dispatch(e.clone(), "daa_get_configuration", json!({}))
        .unwrap();
    assert!(e.confirm_point_names(confirmed(r.clone(), &pr)).is_err());
    let pr = e.preview_point_names(r.clone()).unwrap();
    let mut bad = confirmed(r.clone(), &pr);
    bad.input_digest = "forged".into();
    assert!(e.confirm_point_names(bad).is_err());
    let pr = e.preview_point_names(r.clone()).unwrap();
    e.name_preview.lock().unwrap().as_mut().unwrap().created =
        std::time::Instant::now() - Duration::from_secs(301);
    assert!(e.confirm_point_names(confirmed(r.clone(), &pr)).is_err());
    let mut duplicate = r.clone();
    duplicate.point_ids.push(pid.clone());
    assert!(e.preview_point_names(duplicate).is_err());
    let mut mixed = r.clone();
    mixed.plc_id = v.draft.plcs[1].id.clone();
    assert!(e.preview_point_names(mixed).is_err());
    let pr = e.preview_point_names(r.clone()).unwrap();
    let mut unrelated = v.draft.clone();
    unrelated.storage.retention_days = 8;
    let unrelated = e.save(unrelated, v.etag.clone()).unwrap();
    assert!(e.confirm_point_names(confirmed(r, &pr)).is_err());
    assert_eq!(unrelated.draft.points, original.points);
    let r = request(&e, vec![pid.clone()]);
    let pr = e.preview_point_names(r.clone()).unwrap();
    let saved = e.confirm_point_names(confirmed(r.clone(), &pr)).unwrap();
    assert_eq!(saved.draft.points[0].id, pid);
    assert_eq!(saved.draft.points[0].name_mode, Some(NameMode::AutoPath));
    let mut expected = original.points[0].clone();
    expected.name = "DB501_value_Word".into();
    expected.name_mode = Some(NameMode::AutoPath);
    assert_eq!(saved.draft.points[0], expected);
    assert!(e.confirm_point_names(confirmed(r, &pr)).is_err());
    for mode in [None, Some(NameMode::Pending), Some(NameMode::AutoAddress)] {
        let mut forged = saved.draft.clone();
        forged.points[0].name_mode = mode;
        assert_eq!(
            e.save(forged, saved.etag.clone()).unwrap_err(),
            "name_preview_required"
        )
    }
    let mut forged = saved.draft.clone();
    forged.points[0].name = "DirectBypass".into();
    assert!(e.save(forged, saved.etag.clone()).is_err());
    // Unchanged explicit generation keeps ETag.
    let r = request(&e, vec![pid.clone()]);
    let pr = e.preview_point_names(r.clone()).unwrap();
    assert!(pr.unchanged);
    assert_eq!(
        e.confirm_point_names(confirmed(r, &pr)).unwrap().etag,
        saved.etag
    );
    let after = e
        .storage
        .call(true, |s| {
            Ok((protected(s), dump(&s.config, &["source_documents"])))
        })
        .unwrap();
    assert_eq!(after.0, before);
    assert_eq!(after.1, archive);
    e.shutdown();
    drop(e);
    let reopened = engine(&p);
    assert_eq!(reopened.configuration().unwrap().draft.points[0], expected);
    reopened.shutdown();
    drop(reopened);
    std::fs::write(p.join("daa006-evidence.json"),serde_json::to_vec_pretty(&json!({"rawBeforeSha":digest(&raw),"protectedBefore":before,"protectedAfter":after.0,"pointId":pid,"saved":saved.draft})).unwrap()).unwrap();
}
#[test]
fn shared_golden_offset_atomic_names_final_conflict_and_rollback() {
    let p = profile("daa006-offset");
    let e = engine(&p);
    let v = e.configuration().unwrap();
    let mut c = v.draft;
    let seed = profile("daa006-helper-seed");
    let mut s = Stores::open(&seed.join("local-acquisition-v1")).unwrap();
    let old = old_seed(&mut s, &seed);
    c.plcs = old.plcs.clone();
    s.clean_exit().unwrap();
    drop(s);
    let v = e.save(c, v.etag).unwrap();
    let docs = [
        (
            "names.db",
            include_str!("../../../../../shared/tia-import-core/fixtures/names.db"),
        ),
        (
            "names.udt",
            include_str!("../../../../../shared/tia-import-core/fixtures/names.udt"),
        ),
    ];
    let mut r = req(&v.draft, &v.etag, &docs);
    for m in &mut r.mappings {
        m.db_number = Some(match m.block_key.name.as_str() {
            "Names28" => 28,
            "Names60" => 60,
            _ => 47,
        })
    }
    let imported = confirm(&e, r);
    let c = imported.configuration;
    assert_eq!(
        c.points
            .iter()
            .find(|p| p.source_path == "ActTemp_Z1")
            .unwrap()
            .name,
        "DB28_ActTemp_Z1_Int"
    );
    assert!(c
        .points
        .iter()
        .filter(|p| p.source_path == "中文" || p.source_path.contains("items["))
        .all(|p| p.name.is_empty() && p.name_mode == Some(NameMode::Pending)));
    let db = c.dbs.iter().find(|d| d.number == 28).unwrap().id.clone();
    let rows = e
        .offsets_at(db.clone(), Some(imported.etag.clone()))
        .unwrap();
    assert!(rows.iter().filter(|r| r.proposed_name.is_some()).all(|r| !r
        .proposed_name
        .as_ref()
        .unwrap()
        .is_empty()));
    let before = e.configuration().unwrap();
    assert_eq!(before.draft, c);
    let v = e
        .confirm_offsets_at(
            db.clone(),
            rows.iter().map(|r| r.point_id.clone()).collect(),
            before.etag,
            Some(rows[0].layout_digest.clone()),
        )
        .unwrap();
    assert!(v
        .draft
        .points
        .iter()
        .filter(|p| p.db_id == db)
        .all(|p| !p.name.is_empty() && p.address.as_ref().unwrap().confirmed));
    let first = v
        .draft
        .points
        .iter()
        .find(|p| p.source_path == "ActTemp_Z1")
        .unwrap();
    let other = v
        .draft
        .points
        .iter()
        .find(|p| p.source_path == "1_Act")
        .unwrap();
    let mut r = request(&e, vec![first.id.clone()]);
    r.intent = "edit".into();
    r.patch = Some(serde_json::from_value(json!({"name":other.name})).unwrap());
    let pr = e.preview_point_names(r.clone()).unwrap();
    assert!(!pr.can_confirm);
    assert!(pr.readiness.iter().any(|i| i.code == "point_name_conflict"));
    assert!(e.confirm_point_names(confirmed(r, &pr)).is_err());
    assert_eq!(e.configuration().unwrap().etag, v.etag);
    // A manual edit and nullable group patch are one candidate, then a real SQLite abort rolls everything back.
    let mut r = request(&e, vec![first.id.clone()]);
    r.intent = "edit".into();
    r.patch = Some(
        serde_json::from_value(json!({"name":"Roll_Code","comment":"owned edit","groupId":null}))
            .unwrap(),
    );
    let pr = e.preview_point_names(r.clone()).unwrap();
    assert!(pr.can_confirm);
    let prior = e
        .storage
        .call(true, |s| {
            Ok(dump(
                &s.config,
                &["configuration_draft", "source_documents"],
            ))
        })
        .unwrap();
    e.storage.call(false,|s|{s.config.execute_batch("CREATE TEMP TRIGGER daa006_abort BEFORE UPDATE ON configuration_draft BEGIN SELECT RAISE(ABORT,'owned naming rollback'); END;").map_err(sql_error)}).unwrap();
    assert!(e.confirm_point_names(confirmed(r.clone(), &pr)).is_err());
    assert_eq!(
        e.storage
            .call(true, |s| Ok(dump(
                &s.config,
                &["configuration_draft", "source_documents"]
            )))
            .unwrap(),
        prior
    );
    e.storage
        .call(false, |s| {
            s.config
                .execute_batch("DROP TRIGGER daa006_abort")
                .map_err(sql_error)
        })
        .unwrap();
    let pr = e.preview_point_names(r.clone()).unwrap();
    let saved = e.confirm_point_names(confirmed(r, &pr)).unwrap();
    let edited = saved
        .draft
        .points
        .iter()
        .find(|p| p.id == first.id)
        .unwrap();
    assert_eq!(edited.name, "Roll_Code");
    assert_eq!(edited.name_mode, Some(NameMode::Manual));
    assert_eq!(edited.comment, "owned edit");
    // Legacy/new JSON and fixed golden table cross-consumed through existing serde.
    let golden: Value = serde_json::from_str(include_str!(
        "../../../../../shared/tia-import-core/fixtures/expected-v1.json"
    ))
    .unwrap();
    for case in golden["cases"].as_array().unwrap() {
        use aiis_tia_import_core::*;
        let segments = case["segments"]
            .as_array()
            .unwrap()
            .iter()
            .map(|s| {
                if let Some(v) = s.as_str() {
                    PathSegment::Field(v.into())
                } else {
                    PathSegment::Index(s.as_i64().unwrap() as i32)
                }
            })
            .collect();
        let a = case.get("address").map(|a| ConfirmedAddress {
            byte: a["offset"].as_u64().unwrap() as u32,
            bit: a["bit"].as_u64().map(|v| v as u8),
        });
        let result = plan_names(&NameBatch {
            profile: NAME_PROFILE.into(),
            entries: vec![NameEntry {
                key: case["key"].as_str().unwrap().into(),
                db_number: case["db"].as_u64().unwrap() as u16,
                path: Some(segments),
                data_type: case["type"].as_str().unwrap().into(),
                current_name: String::new(),
                mutable: true,
                address: a,
                manual_name: None,
                address_only: false,
            }],
        })
        .unwrap();
        let (name, mode) = match &result.rows[0].resolution {
            NameResolution::Pending => ("", "pending"),
            NameResolution::Resolved { name, mode } => (name.as_str(), mode.as_str()),
        };
        assert_eq!(name, case["name"]);
        assert_eq!(mode, case["mode"]);
    }
    e.shutdown();
}
/// Only an explicitly owned tmp destination may be seeded; no product seed endpoint exists.
#[test]
fn native_owned_legacy_seed() {
    let Some(path) = std::env::var_os("DAA006_NATIVE_SEED_ROOT") else {
        return;
    };
    let p = PathBuf::from(path);
    assert!(
        p.is_absolute() && p.starts_with("/private/tmp/daa-006-r3-execution-8knyrx3c/dev/native")
    );
    std::fs::create_dir_all(&p).unwrap();
    assert!(!p.join("local-acquisition-v1/config.sqlite").exists());
    let mut s = Stores::open(&p.join("local-acquisition-v1")).unwrap();
    let c = old_seed(&mut s, &p);
    let raw = dump(&s.config, &["configuration_draft", "source_documents"]);
    let history = protected(&s);
    s.clean_exit().unwrap();
    drop(s);
    std::fs::write(p.join("seed-checkpoint.json"),serde_json::to_vec_pretty(&json!({"configuration":c,"raw":raw,"protected":history,"connectionsReleased":true,"readAllowed":false})).unwrap()).unwrap();
}

#[test]
fn pending_admission_explicit_manual_and_address_mode_transitions() {
    let p = profile("daa006-states");
    let e = engine(&p);
    let v = e.configuration().unwrap();
    let mut s =
        Stores::open(&profile("daa006-states-helper").join("local-acquisition-v1")).unwrap();
    let owned = s.dir.parent().unwrap().to_path_buf();
    let old = old_seed(&mut s, &owned);
    let mut c = v.draft;
    c.plcs = old.plcs;
    s.clean_exit().unwrap();
    drop(s);
    let v = e.save(c, v.etag).unwrap();
    let text="DATA_BLOCK \"State\" { S7_Optimized_Access := 'FALSE' } VAR \"中文\":INT; normal:INT; END_VAR BEGIN END_DATA_BLOCK";
    let r = req(&v.draft, &v.etag, &[("state.db", text)]);
    let imported = confirm(&e, r);
    let chinese = imported
        .configuration
        .points
        .iter()
        .find(|p| p.source_path == "中文")
        .unwrap();
    let normal = imported
        .configuration
        .points
        .iter()
        .find(|p| p.source_path == "normal")
        .unwrap();
    assert_eq!(chinese.name_mode, Some(NameMode::Pending));
    assert!(validate(&imported.configuration)
        .iter()
        .all(|i| i.code != "point_name_pending"));
    let mut enabled = imported.configuration.clone();
    enabled
        .points
        .iter_mut()
        .find(|p| p.id == chinese.id)
        .unwrap()
        .enabled = true;
    assert!(validate(&enabled)
        .iter()
        .any(|i| i.code == "point_name_pending" && i.path == chinese.id));
    let r = request(&e, vec![chinese.id.clone()]);
    let preview = e.preview_point_names(r.clone()).unwrap();
    assert!(!preview.can_confirm);
    assert!(e.confirm_point_names(confirmed(r, &preview)).is_err());
    let mut r = request(&e, vec![chinese.id.clone()]);
    r.intent = "edit".into();
    r.patch=Some(serde_json::from_value(json!({"address":{"offset":0,"bit":null,"confirmed":true,"origin":"manual","reason":"owned reviewed"}})).unwrap());
    let preview = e.preview_point_names(r.clone()).unwrap();
    assert!(preview.can_confirm);
    assert_eq!(preview.rows[0].proposed_mode, Some(NameMode::AutoAddress));
    let saved = e.confirm_point_names(confirmed(r, &preview)).unwrap();
    assert_eq!(
        saved
            .draft
            .points
            .iter()
            .find(|p| p.id == chinese.id)
            .unwrap()
            .name,
        "DB501_B0_Int"
    );
    let mut r = request(&e, vec![chinese.id.clone()]);
    r.intent = "edit".into();
    r.patch=Some(serde_json::from_value(json!({"address":{"offset":2,"bit":null,"confirmed":false,"origin":"manual","reason":"new unconfirmed"}})).unwrap());
    let preview = e.preview_point_names(r.clone()).unwrap();
    assert_eq!(preview.rows[0].proposed_mode, Some(NameMode::Pending));
    assert!(preview.can_confirm);
    e.confirm_point_names(confirmed(r, &preview)).unwrap();
    let mut r = request(&e, vec![normal.id.clone()]);
    r.intent = "edit".into();
    r.patch = Some(serde_json::from_value(json!({"name":"Roll_Code"})).unwrap());
    let preview = e.preview_point_names(r.clone()).unwrap();
    e.confirm_point_names(confirmed(r, &preview)).unwrap();
    let mut r = request(&e, vec![normal.id.clone()]);
    r.intent = "edit".into();
    r.patch=Some(serde_json::from_value(json!({"address":{"offset":10,"bit":null,"confirmed":true,"origin":"manual","reason":"manual retained"}})).unwrap());
    let preview = e.preview_point_names(r.clone()).unwrap();
    assert_eq!(preview.rows[0].proposed_name, "Roll_Code");
    assert_eq!(preview.rows[0].proposed_mode, Some(NameMode::Manual));
    e.confirm_point_names(confirmed(r, &preview)).unwrap();
    // Missing and explicit-null patches have different input semantics and digests.
    let missing: PointPatch = serde_json::from_value(json!({"name":"X"})).unwrap();
    let null: PointPatch = serde_json::from_value(json!({"name":"X","groupId":null})).unwrap();
    assert_ne!(
        serde_json::to_string(&missing).unwrap(),
        serde_json::to_string(&null).unwrap()
    );
    e.shutdown();
}
