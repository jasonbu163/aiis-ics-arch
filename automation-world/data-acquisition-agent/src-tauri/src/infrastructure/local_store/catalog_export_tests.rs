//! DAA-019 隔离合成 profile：持久版本、完整点集和逐文件不覆盖导出。
use super::source_import_tests::{dump, engine, profile};
use super::sql_error;
use crate::{
    domain::local_configuration::PointDisplayNames,
    services::catalog_export::{CommitRequest, PreviewRequest},
};
use serde_json::{json, Value};

fn read_only_snapshot(e: &crate::services::local_supervisor::LocalEngine) -> Value {
    e.storage.call(true, |s| Ok(json!({
        "config":dump(&s.config, &["configuration_draft","source_documents","configuration_revisions","active_selection"]),
        "runtime":dump(&s.runtime, &["plc_sources","configuration_contexts","collection_cycles","samples","sample_delivery"])
    }))).unwrap()
}

#[test]
fn arch_plc_002_filename_binding_and_validation() {
    let root = profile("daa019-export-filenames");
    let e = engine(&root);
    let c = super::tests::configuration();
    let first = c.plcs[0].id.clone();
    let second = c.plcs[1].id.clone();
    let initial = e.configuration().unwrap();
    e.storage
        .call(false, move |s| s.save_draft(&c, &initial.etag))
        .unwrap();
    let request = |names: Vec<(String, String)>| PreviewRequest {
        state: "saved_draft".into(),
        plc_ids: vec![first.clone(), second.clone()],
        filenames: names.into_iter().collect(),
    };
    let duplicate = e
        .catalog_export_preview(request(vec![
            (first.clone(), "Test.json".into()),
            (second.clone(), "test.JSON".into()),
        ]))
        .unwrap();
    assert!(duplicate.get("token").is_none());
    assert_eq!(
        duplicate["filenameErrors"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|e| e["code"] == "catalog_filename_duplicate")
            .count(),
        2
    );
    let invalid = e
        .catalog_export_preview(request(vec![
            (first.clone(), "../bad.json".into()),
            (second.clone(), "other.json".into()),
        ]))
        .unwrap();
    assert!(invalid.get("token").is_none());
    assert_eq!(invalid["filenameErrors"][0]["plcId"], first);
    assert_eq!(
        invalid["filenameErrors"][0]["code"],
        "catalog_filename_characters"
    );
    let preview = e
        .catalog_export_preview(PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![first.clone()],
            filenames: [(first.clone(), "温度.json".into())].into_iter().collect(),
        })
        .unwrap();
    assert_eq!(preview["rows"][0]["filename"], "温度.json");
    let token = preview["token"].as_str().unwrap();
    let dir = root.join("named-output");
    std::fs::create_dir(&dir).unwrap();
    let folder = e.catalog_export_directory(token, &dir).unwrap();
    assert_eq!(folder["rows"][0]["filename"], "温度.json");
    let result = e
        .catalog_export_commit(CommitRequest {
            token: token.into(),
            confirm_targets: true,
        })
        .unwrap();
    assert_eq!(result["rows"][0]["result"], "written");
    let bytes = std::fs::read(dir.join("温度.json")).unwrap();
    let (_, _, sha) = crate::domain::plc_catalog::parse(&bytes).unwrap();
    assert_eq!(sha, preview["rows"][0]["fileSha256"]);
    assert_eq!(sha, result["rows"][0]["fileSha256"]);
    // 模拟选择器正在等待：先撤销旧目录授权，并发提交不得写入旧目录。
    let pending = e
        .catalog_export_preview(PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![first.clone()],
            filenames: [(first.clone(), "picker-open.json".into())]
                .into_iter()
                .collect(),
        })
        .unwrap();
    let token = pending["token"].as_str().unwrap();
    e.catalog_export_directory(token, &dir).unwrap();
    e.catalog_export_release_directory(token).unwrap();
    assert_eq!(
        e.catalog_export_commit(CommitRequest {
            token: token.into(),
            confirm_targets: true
        })
        .err()
        .as_deref(),
        Some("catalog_directory_required")
    );
    assert!(!dir.join("picker-open.json").exists());
    let again = e
        .catalog_export_preview(PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![first.clone()],
            filenames: [(first.clone(), "retry.json".into())].into_iter().collect(),
        })
        .unwrap();
    let token = again["token"].as_str().unwrap();
    e.catalog_export_directory(token, &dir).unwrap();
    assert!(e
        .catalog_export_directory(token, &root.join("missing-directory"))
        .is_err());
    assert_eq!(
        e.catalog_export_commit(CommitRequest {
            token: token.into(),
            confirm_targets: true
        })
        .err()
        .as_deref(),
        Some("catalog_directory_required")
    );
    assert!(!dir.join("retry.json").exists());
    e.shutdown();
}

#[test]
fn daa019_catalog_export_saved_sources_partial_conflicts_and_cas() {
    let root = profile("daa019-export");
    let e = engine(&root);
    let mut c = super::tests::configuration();
    let first = c.plcs[0].id.clone();
    let second = c.plcs[1].id.clone();
    let first_point = c
        .points
        .iter()
        .find(|p| p.plc_id == first)
        .unwrap()
        .id
        .clone();
    let second_point = c
        .points
        .iter()
        .find(|p| p.plc_id == second)
        .unwrap()
        .id
        .clone();
    c.points
        .iter_mut()
        .find(|p| p.id == first_point)
        .unwrap()
        .enabled = false;
    c.point_display_names.insert(
        first_point.clone(),
        PointDisplayNames {
            zh_cn: "温度 sentinel".into(),
            en_us: "".into(),
        },
    );
    c.points
        .iter_mut()
        .find(|p| p.id == first_point)
        .unwrap()
        .comment = "independent description".into();
    c.points
        .iter_mut()
        .find(|p| p.id == second_point)
        .unwrap()
        .address
        .as_mut()
        .unwrap()
        .confirmed = false;
    let initial = e.configuration().unwrap();
    let saved = e
        .storage
        .call(false, move |s| s.save_draft(&c, &initial.etag))
        .unwrap();
    let before = read_only_snapshot(&e);
    let preview = e
        .catalog_export_preview(PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![first.clone(), second.clone()],
            filenames: vec![first.clone(), second.clone()]
                .into_iter()
                .map(|id| (id.clone(), format!("{id}.json")))
                .collect(),
        })
        .unwrap();
    assert_eq!(preview["revision"], saved.etag);
    let valid = &preview["rows"][0];
    let invalid = &preview["rows"][1];
    assert_eq!(
        valid["document"]["origin"]["kind"],
        "data_acquisition_agent"
    );
    assert_eq!(
        valid["document"]["export"]["producer"],
        "data_acquisition_agent"
    );
    assert!(valid["document"]["dbs"][0].get("source_enabled").is_none());
    let points: Vec<_> = valid["document"]["dbs"]
        .as_array()
        .unwrap()
        .iter()
        .flat_map(|d| d["points"].as_array().unwrap())
        .collect();
    assert!(["BOOL", "INT", "REAL"]
        .iter()
        .all(|typ| points.iter().any(|p| p["data_type"] == *typ)));
    let first_point_json = points.iter().find(|p| p["id"] == first_point).unwrap();
    assert_eq!(first_point_json["source_enabled"], false);
    assert_eq!(first_point_json["display_names"]["zh-CN"], "温度 sentinel");
    assert_eq!(first_point_json["display_names"]["en-US"], "");
    assert_eq!(first_point_json["description"], "independent description");
    assert!(invalid["document"].is_null());
    assert!(invalid["issues"]
        .as_array()
        .unwrap()
        .iter()
        .any(|v| v["pointId"] == second_point));
    let dir = root.join("export");
    std::fs::create_dir(&dir).unwrap();
    let token = preview["token"].as_str().unwrap();
    e.catalog_export_directory(token, &dir).unwrap();
    let output = dir.join(format!("{first}.json"));
    std::fs::write(&output, b"existing").unwrap();
    let result = e
        .catalog_export_commit(CommitRequest {
            token: token.into(),
            confirm_targets: true,
        })
        .unwrap();
    assert_eq!(result["rows"][0]["result"], "failed");
    assert_eq!(result["rows"][0]["errorCode"], "catalog_target_changed");
    assert_eq!(result["rows"][1]["result"], "failed");
    assert_eq!(std::fs::read(&output).unwrap(), b"existing");
    assert_eq!(std::fs::read_dir(&dir).unwrap().count(), 1);
    let next = e
        .catalog_export_preview(PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![first.clone()],
            filenames: vec![first.clone()]
                .into_iter()
                .map(|id| (id.clone(), format!("{id}.json")))
                .collect(),
        })
        .unwrap();
    let dir2 = root.join("successful");
    std::fs::create_dir(&dir2).unwrap();
    let token = next["token"].as_str().unwrap();
    e.catalog_export_directory(token, &dir2).unwrap();
    let written = e
        .catalog_export_commit(CommitRequest {
            token: token.into(),
            confirm_targets: true,
        })
        .unwrap();
    assert_eq!(written["rows"][0]["result"], "written");
    let path = dir2.join(format!("{first}.json"));
    let bytes = std::fs::read(&path).unwrap();
    let (catalog, raw, sha) = crate::domain::plc_catalog::parse(&bytes).unwrap();
    assert_eq!(written["rows"][0]["fileSha256"], sha);
    assert_eq!(raw.as_bytes(), bytes);
    assert_eq!(catalog.export.revision_id, saved.etag);
    assert_eq!(catalog.export.payload_sha256, next["payloadSha256"]);
    assert_eq!(read_only_snapshot(&e), before);
    println!(
        "{}",
        json!({"event":"daa019_synthetic_export","path":path,"sha256":sha})
    );
    let stale = e
        .catalog_export_preview(PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![first.clone()],
            filenames: vec![first.clone()]
                .into_iter()
                .map(|id| (id.clone(), format!("{id}.json")))
                .collect(),
        })
        .unwrap();
    let dir3 = root.join("stale");
    std::fs::create_dir(&dir3).unwrap();
    let token = stale["token"].as_str().unwrap();
    e.catalog_export_directory(token, &dir3).unwrap();
    let mut changed = e.configuration().unwrap().draft;
    changed.storage.retention_days = 8;
    e.save(changed, saved.etag).unwrap();
    assert_eq!(
        e.catalog_export_commit(CommitRequest {
            token: token.into(),
            confirm_targets: true
        })
        .err()
        .as_deref(),
        Some("catalog_preview_stale")
    );
    assert_eq!(std::fs::read_dir(&dir3).unwrap().count(), 0);
    e.shutdown();
}

#[test]
fn daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt() {
    use crate::domain::{local_configuration::id, sample_upload::ReportingBinding};
    use crate::infrastructure::facts_http::Response;
    use crate::services::catalog_import::{CatalogConfirmation, CatalogRequest};
    let root = profile("daa019-isolation");
    let e = engine(&root);
    let c = super::tests::configuration();
    let old_plc = c.plcs[0].id.clone();
    let initial = e.configuration().unwrap();
    let saved = e
        .storage
        .call(false, {
            let c = c.clone();
            move |s| s.save_draft(&c, &initial.etag)
        })
        .unwrap();
    let activation = e
        .activate(saved.etag.clone(), saved.active.clone(), false)
        .unwrap();
    let revision = activation["active"].as_str().unwrap().to_string();
    let old_id = old_plc.clone();
    let cycle_config = c.clone();
    let cycle_revision = revision.clone();
    e.storage.call(false, move |s| {
        let generation: String = s.runtime.query_row("SELECT generation FROM plc_sources WHERE plc_id=?1", [&old_id], |r|r.get(0)).map_err(sql_error)?;
        let mut settings = s.sample_upload_settings()?; let etag = settings.settings_revision.clone();
        settings.origin = Some("http://fixture.invalid".into());
        settings.bindings.push(ReportingBinding { local_plc_id:old_id.clone(), instance_id:s.instance.clone(), plc_id:id(), source_generation:generation });
        let settings = s.save_sample_upload_settings(settings, etag)?;
        s.commit_cycle(super::tests::cycle(&cycle_config, &cycle_revision))?;
        s.commit_cycle(super::tests::cycle(&cycle_config, &cycle_revision))?;
        let bindings = s.sample_upload_bindings()?; let target = settings.target()?.unwrap();
        let frozen = s.next_sample_upload(&target, &bindings, false)?.unwrap();
        let attempt = s.mark_sample_upload_attempt(&frozen)?;
        let receipt = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":frozen.instance_id,"sampleId":frozen.sample_id,"status":"committed","outcome":"created"}});
        s.record_sample_upload_response(&frozen, Ok(Response {status:200,media_type:"application/json".into(),retry_after:None,body:serde_json::to_vec(&receipt).unwrap()}), attempt)?;
        s.next_sample_upload(&target, &bindings, false)?.unwrap();
        Ok(())
    }).unwrap();
    let mut changed = e.configuration().unwrap().draft;
    changed.plcs[0].name = "changed saved draft".into();
    let changed = e.save(changed, saved.etag).unwrap();
    let preview = e
        .catalog_export_preview(PreviewRequest {
            state: "active_revision".into(),
            plc_ids: vec![old_plc.clone()],
            filenames: vec![old_plc.clone()]
                .into_iter()
                .map(|id| (id.clone(), format!("{id}.json")))
                .collect(),
        })
        .unwrap();
    assert_eq!(preview["revision"], revision);
    assert_eq!(
        preview["rows"][0]["document"]["plc"]["name"],
        c.plcs[0].name
    );
    assert_ne!(
        preview["rows"][0]["document"]["plc"]["name"],
        changed.draft.plcs[0].name
    );
    let dir = root.join("active-export");
    std::fs::create_dir(&dir).unwrap();
    let token = preview["token"].as_str().unwrap();
    e.catalog_export_directory(token, &dir).unwrap();
    e.catalog_export_commit(CommitRequest {
        token: token.into(),
        confirm_targets: true,
    })
    .unwrap();
    let bytes = std::fs::read(dir.join(format!("{old_plc}.json"))).unwrap();
    let mut removed = changed.draft;
    removed.plcs.retain(|p| p.id != old_plc);
    removed.dbs.retain(|db| db.plc_id != old_plc);
    removed.points.retain(|p| p.plc_id != old_plc);
    removed.groups.retain(|g| g.plc_id != old_plc);
    removed.sources.retain(|s| s.plc_id != old_plc);
    let removed = e.save(removed, changed.etag).unwrap();
    e.activate(removed.etag.clone(), removed.active.clone(), false)
        .unwrap();
    let history = e.storage.call(true, |s| Ok(json!({"plc":dump(&s.runtime,&["plc_sources","reporting_bindings","reporting_generations","reporting_cycles","collection_cycles","samples","sample_delivery","sample_uploads","sample_upload_attempts"]),"archives":dump(&s.config,&["source_documents","configuration_revisions"])}))).unwrap();
    let input = CatalogRequest {
        bytes,
        filename: "old.json".into(),
        expected_etag: e.configuration().unwrap().etag,
        target: None,
        as_new_local_instance: true,
    };
    let preview = e.preview_catalog(input.clone()).unwrap();
    assert!(preview.history_conflict);
    let new_plc = preview.local_plc_id.clone();
    assert_ne!(new_plc, old_plc);
    let imported = e
        .confirm_catalog(CatalogConfirmation {
            input,
            preview_token: preview.preview_token,
        })
        .unwrap();
    assert_eq!(
        imported.imported_local_plc_id.as_deref(),
        Some(new_plc.as_str())
    );
    let after = e.storage.call(true, {let new_plc = new_plc.clone(); move |s| {
        let rows: i64 = s.runtime.query_row("SELECT count(*) FROM plc_sources WHERE plc_id=?1", [&new_plc], |r|r.get(0)).map_err(sql_error)?;
        assert_eq!(rows, 0);
        assert!(!s.sample_upload_settings()?.bindings.iter().any(|b|b.local_plc_id==new_plc));
        Ok(json!({"plc":dump(&s.runtime,&["plc_sources","reporting_bindings","reporting_generations","reporting_cycles","collection_cycles","samples","sample_delivery","sample_uploads","sample_upload_attempts"]),"archives":dump(&s.config,&["source_documents","configuration_revisions"])}))
    }}).unwrap();
    assert_eq!(after["plc"], history["plc"]);
    assert_eq!(
        after["archives"]["configuration_revisions"],
        history["archives"]["configuration_revisions"]
    );
    assert_eq!(
        after["archives"]["source_documents"]
            .as_array()
            .unwrap()
            .len(),
        history["archives"]["source_documents"]
            .as_array()
            .unwrap()
            .len()
            + 1
    );
    assert!(imported
        .draft
        .points
        .iter()
        .filter(|p| p.plc_id == new_plc)
        .all(|p| !p.enabled && p.group_id.is_none()));
    assert!(
        !imported
            .draft
            .plcs
            .iter()
            .find(|p| p.id == new_plc)
            .unwrap()
            .enabled
    );
    e.shutdown();
}
