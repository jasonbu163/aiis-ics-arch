//! DAA-017 合成 profile：目录原文、身份、预览 CAS、事务回滚及激活校验。
use super::source_import_tests::{dump, engine, profile, protected};
use super::*;
use crate::domain::local_configuration::{id, Group, Plc};
use crate::domain::point_naming::{NameConfirmation, NameRequest, PointPatch};
use crate::services::catalog_import::{CatalogConfirmation, CatalogRequest};
use crate::services::local_supervisor::LocalEngine;
use serde_json::json;

const FILE: &[u8] = include_bytes!("../../../../tests/fixtures/plc-catalog-v1.json");

fn request(e: &LocalEngine) -> CatalogRequest {
    CatalogRequest {
        bytes: FILE.to_vec(),
        filename: "synthetic-plc.json".into(),
        expected_etag: e.configuration().unwrap().etag,
        target: None,
        as_new_local_instance: false,
    }
}

fn confirm(
    e: &LocalEngine,
    input: CatalogRequest,
) -> crate::domain::local_runtime::ConfigurationView {
    let preview = e.preview_catalog(input.clone()).unwrap();
    e.confirm_catalog(CatalogConfirmation {
        input,
        preview_token: preview.preview_token,
    })
    .unwrap()
}

fn snapshot(e: &LocalEngine) -> serde_json::Value {
    e.storage
        .call(true, |s| {
            Ok(json!({
                "draft_and_sources": dump(&s.config, &["configuration_draft", "source_documents"]),
                "other": protected(s)
            }))
        })
        .unwrap()
}

#[test]
fn catalog_import_non_rfc_uuid_rejected_without_writes() {
    let p = profile("daa017-non-rfc-uuid");
    let e = engine(&p);
    let before = snapshot(&e);
    let mut input = request(&e);
    let etag = input.expected_etag.clone();
    let mut value: serde_json::Value = serde_json::from_slice(FILE).unwrap();
    value["dbs"][0]["points"][2]["id"] = json!("ca21fc06-a489-4948-03fc-08b8e798168e");
    input.bytes = serde_json::to_vec(&value).unwrap();
    assert_eq!(
        e.preview_catalog(input).err().as_deref(),
        Some("catalog_point_invalid")
    );
    assert_eq!(snapshot(&e), before);
    assert_eq!(e.configuration().unwrap().etag, etag);
    e.shutdown();
}

#[test]
fn catalog_import_single_transaction_preserves_existing_and_activation() {
    let p = profile("daa017-import");
    let e = engine(&p);
    let initial = e.configuration().unwrap();
    let mut existing = initial.draft;
    existing.plcs.push(Plc {
        id: id(),
        name: "Existing".into(),
        enabled: false,
        host: "127.0.0.2".into(),
        port: 102,
        rack: 0,
        slot: 1,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    });
    let before = e.save(existing, initial.etag).unwrap();
    let unchanged = snapshot(&e);
    let input = request(&e);
    let preview = e.preview_catalog(input.clone()).unwrap();
    crate::commands::local_acquisition::dispatch(e.clone(), "daa_cancel_catalog", json!({}))
        .unwrap();
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: input.clone(),
            preview_token: preview.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), unchanged);
    let preview = e.preview_catalog(input.clone()).unwrap();
    assert_eq!(snapshot(&e), unchanged);
    assert_eq!(preview.catalog.dbs.len(), 2);
    let saved = e
        .confirm_catalog(CatalogConfirmation {
            input: input.clone(),
            preview_token: preview.preview_token,
        })
        .unwrap();
    assert_eq!(saved.active, before.active);
    assert_eq!(saved.draft.plcs[0], before.draft.plcs[0]);
    assert!(!saved.draft.plcs[1].enabled);
    assert_eq!(saved.draft.sources.len(), 1);
    assert_eq!(saved.draft.sources[0].content.as_bytes(), FILE);
    assert_eq!(saved.draft.catalog_bindings.len(), 2);
    assert_eq!(
        saved.draft.catalog_bindings[0].source_id,
        saved.draft.catalog_bindings[1].source_id
    );
    assert!(saved
        .draft
        .points
        .iter()
        .all(|p| !p.enabled && p.group_id.is_none()));
    assert_eq!(
        saved
            .draft
            .point_legacy_display_names
            .values()
            .next()
            .unwrap(),
        "未标记"
    );
    assert_eq!(saved.draft.points[0].comment, "独立说明");
    assert!(saved.issues.is_empty(), "{:?}", saved.issues);
    assert!(e.preview_catalog(request(&e)).is_err());

    let mut configured = saved.draft.clone();
    let plc_id = configured.plcs[1].id.clone();
    configured.plcs[1].enabled = true;
    let group_id = id();
    configured.groups.push(Group {
        id: group_id.clone(),
        plc_id: plc_id.clone(),
        name: "Owned group".into(),
        enabled: true,
        interval_ms: 1000,
    });
    for point in configured
        .points
        .iter_mut()
        .filter(|p| p.db_id == configured.dbs[0].id)
    {
        point.group_id = Some(group_id.clone());
        point.enabled = true;
    }
    let configured = e.save(configured, saved.etag).unwrap();
    assert!(configured.issues.is_empty(), "{:?}", configured.issues);
    e.activate(configured.etag.clone(), configured.active.clone(), false)
        .unwrap();
    assert_eq!(
        e.configuration().unwrap().draft.plcs[0],
        before.draft.plcs[0]
    );
    e.shutdown();
    drop(e);
    let reopened = engine(&p);
    let current = reopened.configuration().unwrap();
    assert_eq!(current.draft.plcs[0], before.draft.plcs[0]);
    assert!(current.issues.is_empty());
    let mut removed = current.draft.clone();
    let removed_plc = removed.plcs[1].id.clone();
    removed.plcs.retain(|p| p.id != removed_plc);
    removed.dbs.retain(|d| d.plc_id != removed_plc);
    removed.points.retain(|point| point.plc_id != removed_plc);
    removed.groups.retain(|group| group.plc_id != removed_plc);
    removed
        .sources
        .retain(|source| source.plc_id != removed_plc);
    let removed = reopened.save(removed, current.etag).unwrap();
    let mut collision: serde_json::Value = serde_json::from_slice(FILE).unwrap();
    collision["origin"]["profile_id"] = json!(id());
    collision["origin"]["plc_id"] = json!(id());
    collision["export"]["profile_id"] = json!(id());
    let mut retry = request(&reopened);
    retry.bytes = serde_json::to_vec(&collision).unwrap();
    assert!(reopened.preview_catalog(retry).is_err());
    assert_eq!(reopened.configuration().unwrap().etag, removed.etag);
    reopened.shutdown();
}

#[test]
fn catalog_import_conflicts_and_failed_transaction_preserve_draft_and_archive() {
    let p = profile("daa017-conflicts");
    let e = engine(&p);
    let before = snapshot(&e);
    let input = request(&e);
    let instance = e.storage.call(true, |s| Ok(s.instance.clone())).unwrap();
    let mut bad_identity: serde_json::Value = serde_json::from_slice(FILE).unwrap();
    bad_identity["origin"]["plc_id"] = json!(instance);
    let mut conflict = input.clone();
    conflict.bytes = serde_json::to_vec(&bad_identity).unwrap();
    assert_eq!(
        e.preview_catalog(conflict).err().as_deref(),
        Some("catalog_identity_conflict")
    );
    assert_eq!(snapshot(&e), before);
    let preview = e.preview_catalog(input.clone()).unwrap();
    let mut changed = input.clone();
    changed.bytes.push(b' ');
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: changed,
            preview_token: preview.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let preview = e.preview_catalog(input.clone()).unwrap();
    let mut changed_target = input.clone();
    changed_target.target = Some(crate::domain::plc_catalog::Connection {
        host: "127.0.0.1".into(),
        port: 31282,
        rack: 0,
        slot: 1,
        local_tsap: None,
        remote_tsap: None,
    });
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: changed_target,
            preview_token: preview.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let preview = e.preview_catalog(input.clone()).unwrap();
    e.catalog_preview.lock().unwrap().as_mut().unwrap().created =
        std::time::Instant::now() - std::time::Duration::from_secs(301);
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: input.clone(),
            preview_token: preview.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let _preview = e.preview_catalog(input.clone()).unwrap();
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: input.clone(),
            preview_token: id()
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let preview = e.preview_catalog(input.clone()).unwrap();
    let mut changed = e.configuration().unwrap().draft;
    changed.storage.retention_days = 8;
    let changed = e.save(changed, input.expected_etag.clone()).unwrap();
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: input.clone(),
            preview_token: preview.preview_token
        })
        .is_err());
    let before_failure = snapshot(&e);
    let next = request(&e);
    let preview = e.preview_catalog(next.clone()).unwrap();
    e.storage.call(false, |s| s.config.execute_batch("CREATE TEMP TRIGGER daa017_abort BEFORE INSERT ON source_documents BEGIN SELECT RAISE(ABORT,'synthetic failure'); END;").map_err(sql_error)).unwrap();
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input: next,
            preview_token: preview.preview_token
        })
        .is_err());
    e.storage
        .call(false, |s| {
            s.config
                .execute_batch("DROP TRIGGER daa017_abort;")
                .map_err(sql_error)
        })
        .unwrap();
    assert_eq!(snapshot(&e), before_failure);
    assert_eq!(e.configuration().unwrap().etag, changed.etag);
    e.shutdown();
}

#[test]
fn catalog_import_prevents_tampering_and_reimport_after_removal() {
    let p = profile("daa017-integrity");
    let e = engine(&p);
    let saved = confirm(&e, request(&e));
    let baseline = snapshot(&e);
    let source_sha = saved.draft.sources[0].sha256.clone();
    let original = saved.draft.sources[0].content.clone();
    e.storage
        .call(false, move |s| {
            s.config
                .execute(
                    "UPDATE source_documents SET content='tampered' WHERE sha256=?1",
                    [&source_sha],
                )
                .map_err(sql_error)?;
            assert!(s.configuration().is_err());
            s.config
                .execute(
                    "UPDATE source_documents SET content=?1 WHERE sha256=?2",
                    rusqlite::params![original, source_sha],
                )
                .map_err(sql_error)?;
            Ok(())
        })
        .unwrap();
    assert_eq!(snapshot(&e), baseline);
    for change in 0..9 {
        let mut bad = saved.draft.clone();
        match change {
            0 => bad.points[0].name = "Altered".into(),
            1 => bad.points[0].data_type = "INT".into(),
            2 => bad.points[0].address.as_mut().unwrap().offset = 4,
            3 => bad.catalog_bindings[0].source_sha256 = "0".repeat(64),
            4 => bad.catalog_bindings[0]
                .point_mappings
                .pop()
                .map(|_| ())
                .unwrap(),
            5 => {
                bad.catalog_bindings[0].origin_db_id = bad.catalog_bindings[1].origin_db_id.clone()
            }
            6 => bad.dbs[0].number += 1,
            7 => bad.point_legacy_display_names.clear(),
            _ => bad.plcs[0].host = "0.0.0.0".into(),
        }
        assert!(e.save(bad, saved.etag.clone()).is_err(), "{change}");
        assert_eq!(snapshot(&e), baseline);
    }
    let mut removed = saved.draft.clone();
    removed.plcs.clear();
    removed.dbs.clear();
    removed.points.clear();
    removed.sources.clear();
    let removed = e.save(removed, saved.etag).unwrap();
    assert!(removed.draft.catalog_bindings.is_empty());
    assert!(removed.draft.point_legacy_display_names.is_empty());
    let after = snapshot(&e);
    let input = request(&e);
    let preview = e.preview_catalog(input.clone()).unwrap();
    assert!(preview.history_conflict);
    assert!(e
        .confirm_catalog(CatalogConfirmation {
            input,
            preview_token: preview.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), after);
    let mut same_origin: serde_json::Value = serde_json::from_slice(FILE).unwrap();
    same_origin["dbs"][0]["points"][0]["description"] = json!("changed file");
    let mut retry = request(&e);
    retry.bytes = serde_json::to_vec(&same_origin).unwrap();
    assert!(e.preview_catalog(retry).unwrap().history_conflict);
    assert_eq!(snapshot(&e), after);
    e.shutdown();
}

#[test]
fn daa019_history_requires_choice_and_separates_local_identities() {
    let p = profile("daa019-history");
    let e = engine(&p);
    let saved = confirm(&e, request(&e));
    let old_plc = saved.draft.plcs[0].id.clone();
    let old_dbs: Vec<_> = saved.draft.dbs.iter().map(|d| d.id.clone()).collect();
    let old_points: Vec<_> = saved.draft.points.iter().map(|p| p.id.clone()).collect();
    let old_archive = e
        .storage
        .call(true, |s| Ok(dump(&s.config, &["source_documents"])))
        .unwrap();
    e.activate(saved.etag.clone(), saved.active.clone(), false)
        .unwrap();
    let active = e.configuration().unwrap();
    let mut removed = active.draft.clone();
    removed.plcs.clear();
    removed.dbs.clear();
    removed.points.clear();
    removed.sources.clear();
    let removed = e.save(removed, active.etag).unwrap();
    let before = snapshot(&e);
    assert_eq!(
        e.preview_catalog(request(&e)).err().as_deref(),
        Some("catalog_origin_conflict")
    );
    assert_eq!(snapshot(&e), before);
    e.activate(removed.etag.clone(), removed.active.clone(), false)
        .unwrap();
    let before = snapshot(&e);
    let input = request(&e);
    let preview = e.preview_catalog(input.clone()).unwrap();
    assert!(preview.history_conflict);
    assert_ne!(preview.local_plc_id, old_plc);
    assert_eq!(
        e.confirm_catalog(CatalogConfirmation {
            input: input.clone(),
            preview_token: preview.preview_token
        })
        .err()
        .as_deref(),
        Some("catalog_history_choice_required")
    );
    assert_eq!(snapshot(&e), before);
    let mut chosen = input;
    chosen.as_new_local_instance = true;
    let preview = e.preview_catalog(chosen.clone()).unwrap();
    let new_plc = preview.local_plc_id.clone();
    let result = e
        .confirm_catalog(CatalogConfirmation {
            input: chosen,
            preview_token: preview.preview_token,
        })
        .unwrap();
    assert_eq!(
        result.imported_local_plc_id.as_deref(),
        Some(new_plc.as_str())
    );
    assert_eq!(result.draft.plcs[0].id, new_plc);
    assert!(result.draft.dbs.iter().all(|d| !old_dbs.contains(&d.id)));
    assert!(result
        .draft
        .points
        .iter()
        .all(|point| !old_points.contains(&point.id)
            && !point.enabled
            && point.group_id.is_none()));
    assert!(!result.draft.plcs[0].enabled);
    let export = e
        .catalog_export_preview(crate::services::catalog_export::PreviewRequest {
            state: "saved_draft".into(),
            plc_ids: vec![new_plc.clone()],
            filenames: vec![new_plc.clone()]
                .into_iter()
                .map(|id| (id.clone(), format!("{id}.json")))
                .collect(),
        })
        .unwrap();
    let document = &export["rows"][0]["document"];
    let input: serde_json::Value = serde_json::from_slice(FILE).unwrap();
    assert_eq!(document["origin"], input["origin"]);
    assert_eq!(document["export"]["producer"], "data_acquisition_agent");
    for (db, original) in document["dbs"]
        .as_array()
        .unwrap()
        .iter()
        .zip(input["dbs"].as_array().unwrap())
    {
        assert_eq!(db["id"], original["id"]);
        assert!(db.get("source_enabled").is_none());
        for (point, original_point) in db["points"]
            .as_array()
            .unwrap()
            .iter()
            .zip(original["points"].as_array().unwrap())
        {
            assert_eq!(point["id"], original_point["id"]);
            assert_eq!(point["name"], original_point["name"]);
            assert_eq!(point["data_type"], original_point["data_type"]);
            assert_eq!(point["byte_offset"], original_point["byte_offset"]);
            assert_eq!(point["source_enabled"], false);
        }
    }
    assert_eq!(
        e.storage
            .call(true, |s| Ok(dump(&s.config, &["source_documents"])))
            .unwrap(),
        old_archive
    );
    let count: i64 = e
        .storage
        .call(true, move |s| {
            s.runtime
                .query_row(
                    "SELECT count(*) FROM plc_sources WHERE plc_id=?1",
                    [&new_plc],
                    |r| r.get(0),
                )
                .map_err(sql_error)
        })
        .unwrap();
    assert_eq!(count, 0);
    e.shutdown();
    drop(e);
    let reopened = engine(&p);
    assert_eq!(
        reopened
            .configuration()
            .unwrap()
            .draft
            .catalog_bindings
            .len(),
        2
    );
    reopened.shutdown();
}

#[test]
fn daa019_archive_referenced_by_runtime_context_survives_revision_pruning() {
    let p = profile("daa019-pruned-archive");
    let e = engine(&p);
    let saved = confirm(&e, request(&e));
    let archive = e
        .storage
        .call(true, |s| Ok(dump(&s.config, &["source_documents"])))
        .unwrap();
    let activated = e
        .activate(saved.etag.clone(), saved.active.clone(), false)
        .unwrap();
    let old_revision = activated["active"].as_str().unwrap().to_string();
    let active = e.configuration().unwrap();
    let mut removed = active.draft;
    removed.plcs.clear();
    removed.dbs.clear();
    removed.points.clear();
    removed.sources.clear();
    let removed = e.save(removed, active.etag).unwrap();
    e.activate(removed.etag, removed.active, false).unwrap();
    for n in 0..10 {
        let view = e.configuration().unwrap();
        let mut draft = view.draft;
        draft.storage.retention_days = if n % 2 == 0 { 8 } else { 7 };
        let saved = e.save(draft, view.etag).unwrap();
        e.activate(saved.etag, saved.active, false).unwrap();
    }
    e.storage
        .call(true, move |s| {
            let old_in_config: bool = s
                .config
                .query_row(
                    "SELECT EXISTS(SELECT 1 FROM configuration_revisions WHERE id=?1)",
                    [&old_revision],
                    |r| r.get(0),
                )
                .map_err(sql_error)?;
            let context: bool = s
                .runtime
                .query_row(
                    "SELECT EXISTS(SELECT 1 FROM configuration_contexts WHERE revision=?1)",
                    [&old_revision],
                    |r| r.get(0),
                )
                .map_err(sql_error)?;
            assert!(!old_in_config && context);
            assert_eq!(dump(&s.config, &["source_documents"]), archive);
            Ok(())
        })
        .unwrap();
    let mut input = request(&e);
    input.as_new_local_instance = true;
    let preview = e.preview_catalog(input.clone()).unwrap();
    assert!(preview.history_conflict);
    e.confirm_catalog(CatalogConfirmation {
        input,
        preview_token: preview.preview_token,
    })
    .unwrap();
    e.shutdown();
    drop(e);
    let reopened = engine(&p);
    assert_eq!(
        reopened
            .configuration()
            .unwrap()
            .draft
            .catalog_bindings
            .len(),
        2
    );
    reopened.shutdown();
}

#[test]
fn daa019_local_plc_history_references_block_reuse_for_supported_runtime_schemas() {
    use std::collections::BTreeSet;
    for version in [2, 3, 4] {
        for extended in [false, true] {
            if version != 4 && extended {
                continue;
            }
            let runtime = rusqlite::Connection::open_in_memory().unwrap();
            // 仅在此隔离损坏夹具中关闭外键，验证不一致引用仍会阻断导入。
            runtime.pragma_update(None, "foreign_keys", false).unwrap();
            let ddl = match version {
                2 => super::schema::runtime_sql(),
                3 => super::schema::runtime_v3_sql(),
                4 if extended => super::schema::runtime_v4_switches_sql(),
                _ => super::schema::runtime_v4_sql(),
            };
            runtime.execute_batch(&ddl).unwrap();
            runtime
                .pragma_update(None, "user_version", version)
                .unwrap();
            let plc = id();
            let cycle_plc = id();
            let sample_plc = id();
            runtime
                .execute(
                    "INSERT INTO plc_sources VALUES(?1,?2,1)",
                    rusqlite::params![plc, id()],
                )
                .unwrap();
            let context = id();
            let cycle = id();
            let group = id();
            runtime
                .execute(
                    "INSERT INTO configuration_contexts VALUES(?1,1,'{}','test')",
                    [&context],
                )
                .unwrap();
            runtime.execute("INSERT INTO collection_cycles VALUES(?1,?2,?3,1,?4,?5,'a','b','c','good','{}','test',1)", rusqlite::params![cycle,cycle_plc,id(),group,context]).unwrap();
            runtime.execute("INSERT INTO samples(id,cycle_id,db_number,plc_id,group_id,source_seq,revision,quality,saved_at,schema_version,payload,sha256,payload_bytes) VALUES(?1,?2,1,?3,?4,1,?5,'good','c',2,'{}','test',2)", rusqlite::params![id(),cycle,sample_plc,group,context]).unwrap();
            for local in [&plc, &cycle_plc, &sample_plc] {
                assert!(super::configuration::runtime_local_identity_conflict(
                    &runtime,
                    &BTreeSet::from([local.clone()])
                )
                .unwrap());
            }
            assert!(!super::configuration::runtime_local_identity_conflict(
                &runtime,
                &BTreeSet::from([id()])
            )
            .unwrap());
            if extended {
                for table in [
                    "reporting_bindings",
                    "reporting_generations",
                    "reporting_disabled",
                ] {
                    let local = id();
                    match table {
                        "reporting_bindings" => runtime
                            .execute(
                                "INSERT INTO reporting_bindings VALUES(?1,?2,?3)",
                                rusqlite::params![local, id(), id()],
                            )
                            .unwrap(),
                        "reporting_generations" => runtime
                            .execute(
                                "INSERT INTO reporting_generations VALUES(?1,?2,?3,?4,?5)",
                                rusqlite::params![id(), id(), id(), local, id()],
                            )
                            .unwrap(),
                        _ => runtime
                            .execute("INSERT INTO reporting_disabled VALUES(?1)", [&local])
                            .unwrap(),
                    };
                    assert!(
                        super::configuration::runtime_local_identity_conflict(
                            &runtime,
                            &BTreeSet::from([local])
                        )
                        .unwrap(),
                        "{table}"
                    );
                }
            }
            runtime.execute_batch("DROP TABLE samples").unwrap();
            assert!(super::configuration::runtime_local_identity_conflict(
                &runtime,
                &BTreeSet::from([id()])
            )
            .is_err());
        }
    }
}

#[test]
fn daa019_corrupt_historical_context_rejects_reimport_without_writes() {
    let p = profile("daa019-corrupt-context");
    let e = engine(&p);
    let saved = confirm(&e, request(&e));
    let activated = e.activate(saved.etag, saved.active, false).unwrap();
    let revision = activated["active"].as_str().unwrap().to_string();
    let view = e.configuration().unwrap();
    let mut removed = view.draft;
    removed.plcs.clear();
    removed.dbs.clear();
    removed.points.clear();
    removed.sources.clear();
    let removed = e.save(removed, view.etag).unwrap();
    e.activate(removed.etag, removed.active, false).unwrap();
    let old_sha: String = e
        .storage
        .call(false, {
            let revision = revision.clone();
            move |s| {
                let sha = s
                    .runtime
                    .query_row(
                        "SELECT sha256 FROM configuration_contexts WHERE revision=?1",
                        [&revision],
                        |r| r.get(0),
                    )
                    .map_err(sql_error)?;
                s.runtime
                    .execute(
                        "UPDATE configuration_contexts SET sha256=?1 WHERE revision=?2",
                        rusqlite::params!["0".repeat(64), revision],
                    )
                    .map_err(sql_error)?;
                Ok(sha)
            }
        })
        .unwrap();
    let before = snapshot(&e);
    let mut input = request(&e);
    input.as_new_local_instance = true;
    assert_eq!(
        e.preview_catalog(input).err().as_deref(),
        Some("configuration_corrupt")
    );
    assert_eq!(snapshot(&e), before);
    e.storage
        .call(false, move |s| {
            s.runtime
                .execute(
                    "UPDATE configuration_contexts SET sha256=?1 WHERE revision=?2",
                    rusqlite::params![old_sha, revision],
                )
                .map_err(sql_error)?;
            Ok(())
        })
        .unwrap();
    e.shutdown();
}

#[test]
fn daa019_missing_historical_catalog_archive_rejects_reimport_without_writes() {
    let p = profile("daa019-missing-archive");
    let e = engine(&p);
    let saved = confirm(&e, request(&e));
    let sha = saved.draft.sources[0].sha256.clone();
    e.activate(saved.etag, saved.active, false).unwrap();
    let view = e.configuration().unwrap();
    let mut removed = view.draft;
    removed.plcs.clear();
    removed.dbs.clear();
    removed.points.clear();
    removed.sources.clear();
    let removed = e.save(removed, view.etag).unwrap();
    e.activate(removed.etag, removed.active, false).unwrap();
    // 只在本测试的隔离 SQLite 制造缺失归档，确认导入不能悄悄重建或覆盖它。
    e.storage
        .call(false, move |s| {
            s.config
                .execute("DELETE FROM source_documents WHERE sha256=?1", [&sha])
                .map_err(sql_error)?;
            Ok(())
        })
        .unwrap();
    let before = snapshot(&e);
    let mut input = request(&e);
    input.as_new_local_instance = true;
    assert_eq!(
        e.preview_catalog(input).err().as_deref(),
        Some("catalog_source_invalid")
    );
    assert_eq!(snapshot(&e), before);
    e.shutdown();
}

#[test]
fn catalog_import_existing_name_preview_accepts_user_fields_and_rejects_overrides() {
    let p = profile("daa017-point-edit");
    let e = engine(&p);
    let saved = confirm(&e, request(&e));
    let mut draft = saved.draft.clone();
    let point = draft.points[0].clone();
    let group_id = id();
    draft.groups.push(Group {
        id: group_id.clone(),
        plc_id: point.plc_id.clone(),
        name: "Test group".into(),
        enabled: true,
        interval_ms: 1000,
    });
    let saved = e.save(draft, saved.etag).unwrap();
    let archive = e
        .storage
        .call(true, |s| Ok(dump(&s.config, &["source_documents"])))
        .unwrap();
    let input = NameRequest {
        expected_etag: saved.etag.clone(),
        plc_id: point.plc_id.clone(),
        point_ids: vec![point.id.clone()],
        intent: "edit".into(),
        patch: Some(PointPatch {
            name: Some(point.name.clone()),
            comment: Some("人工注释".into()),
            enabled: Some(true),
            group_id: Some(Some(group_id)),
            address: Some(point.address.clone()),
            display_names: Some(crate::domain::local_configuration::PointDisplayNames {
                zh_cn: "中文新名".into(),
                en_us: "English sentinel".into(),
            }),
        }),
    };
    let before = snapshot(&e);
    for field in 0..4 {
        let mut bad = input.clone();
        let patch = bad.patch.as_mut().unwrap();
        match field {
            0 => patch.name = Some("ChangedName".into()),
            1 => patch.address = Some(None),
            2 => patch.address.as_mut().unwrap().as_mut().unwrap().offset += 1,
            _ => patch.address.as_mut().unwrap().as_mut().unwrap().reason = "other".into(),
        }
        assert!(e.preview_point_names(bad).is_err());
        assert_eq!(snapshot(&e), before);
    }
    let mut generate = input.clone();
    generate.intent = "generate".into();
    generate.patch = None;
    assert!(e.preview_point_names(generate).is_err());
    let first = e.preview_point_names(input.clone()).unwrap();
    assert!(first.can_confirm, "{:?}", first.readiness);
    assert!(e
        .confirm_point_names(NameConfirmation {
            input: input.clone(),
            input_digest: first.input_digest.clone(),
            preview_token: id()
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let second = e.preview_point_names(input.clone()).unwrap();
    assert!(e
        .confirm_point_names(NameConfirmation {
            input: input.clone(),
            input_digest: "forged".into(),
            preview_token: second.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let second = e.preview_point_names(input.clone()).unwrap();
    e.name_preview.lock().unwrap().as_mut().unwrap().created =
        std::time::Instant::now() - std::time::Duration::from_secs(301);
    assert!(e
        .confirm_point_names(NameConfirmation {
            input: input.clone(),
            input_digest: second.input_digest,
            preview_token: second.preview_token
        })
        .is_err());
    assert_eq!(snapshot(&e), before);
    let preview = e.preview_point_names(input.clone()).unwrap();
    let updated = e
        .confirm_point_names(NameConfirmation {
            input,
            input_digest: preview.input_digest,
            preview_token: preview.preview_token,
        })
        .unwrap();
    assert_eq!(updated.draft.points[0].name, point.name);
    assert_eq!(updated.draft.points[0].address, point.address);
    assert_eq!(updated.draft.points[0].comment, "人工注释");
    assert!(updated.draft.points[0].enabled);
    assert_eq!(
        updated.draft.point_display_names[&point.id].en_us,
        "English sentinel"
    );
    assert_eq!(
        archive,
        e.storage
            .call(true, |s| Ok(dump(&s.config, &["source_documents"])))
            .unwrap()
    );
    e.shutdown();
}
