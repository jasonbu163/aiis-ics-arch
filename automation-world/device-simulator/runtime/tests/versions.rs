//! 合成profile验证草稿/版本、回退保留确认、批量原子删除、重复加载与预览保护；不监听S7。
use ds_runtime::{
    app::App,
    domain::configuration::{uuid, InstanceConfig, Workspace},
    services::{
        apply::{self, ApplyIntent},
        configuration::{Preview, SaveIntent},
        layout::{self, LayoutIntent},
        naming::{self, NamesIntent},
        versions::{self, CancelPreview, DeleteIntent, VersionConfirmation, VersionIntent},
    },
    testing::hooks,
};
use serde_json::json;
use std::path::PathBuf;
fn profile() -> PathBuf {
    PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("explicit owned profile root"))
        .join(uuid())
}
fn workspace() -> Workspace {
    let instances = (0..2)
        .map(|n| {
            serde_json::from_value::<InstanceConfig>(json!({
        "id":uuid(),"name":format!("Synthetic-{n}"),"port":30102+n,
        "dbs":[{"id":uuid(),"name":"Manual","number":31,"length":2,"manual":true,
        "points":[{"id":uuid(),"name":"Value","dataType":"INT","byte":0,"manual":true,
        "manualReason":"synthetic address","policy":{"initial":7,"owner":"ui","uiWrite":true}}]}]
    })).unwrap()
        })
        .collect();
    Workspace {
        instances,
        ..Workspace::default()
    }
}
fn save(app: &App, workspace: Workspace, confirm_points: Vec<String>) {
    app.configuration
        .save(SaveIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            workspace,
            confirm_points,
        })
        .unwrap();
}
fn ready(app: &App) {
    let w = workspace();
    save(app, w.clone(), vec![]);
    for i in &w.instances {
        let p = layout::preview(
            &app.configuration,
            LayoutIntent {
                expected_etag: app.configuration.get().unwrap().etag,
                instance_id: i.id.clone(),
                db_id: i.dbs[0].id.clone(),
                method: "manual".into(),
                reason: "synthetic address".into(),
            },
        )
        .unwrap();
        app.configuration
            .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
            .unwrap();
        let ids = i.dbs[0].points.iter().map(|p| p.id.clone()).collect();
        let p = naming::preview(
            &app.configuration,
            NamesIntent {
                expected_etag: app.configuration.get().unwrap().etag,
                instance_id: i.id.clone(),
                point_ids: ids,
                address_only: false,
            },
        )
        .unwrap();
        app.configuration
            .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)
            .unwrap();
        assert!(app
            .configuration
            .store
            .revision_catalog()
            .unwrap()
            .is_empty());
    }
    let w = app.configuration.get().unwrap().workspace;
    let ids = w
        .instances
        .iter()
        .flat_map(|i| &i.dbs)
        .flat_map(|d| &d.points)
        .map(|p| p.id.clone())
        .collect();
    save(app, w, ids);
    assert!(app
        .configuration
        .store
        .revision_catalog()
        .unwrap()
        .is_empty());
}
fn intent(app: &App, revision: Option<&str>) -> VersionIntent {
    VersionIntent {
        expected_etag: app.configuration.get().unwrap().etag,
        revision_id: revision.map(str::to_owned),
    }
}
fn confirm(
    app: &App,
    p: &Preview,
) -> Result<ds_runtime::infrastructure::config_store::SaveResult, String> {
    confirm_releasing(app, p, false)
}
fn deletion(app: &App, ids: &[String]) -> DeleteIntent {
    DeleteIntent {
        expected_etag: app.configuration.get().unwrap().etag,
        revision_ids: ids.to_vec(),
    }
}
fn confirm_releasing(
    app: &App,
    p: &Preview,
    release_rollback: bool,
) -> Result<ds_runtime::infrastructure::config_store::SaveResult, String> {
    versions::confirm(
        app,
        &p.kind,
        VersionConfirmation {
            expected_etag: p.expected_etag.clone(),
            token: p.token.clone(),
            candidate_sha256: p.candidate_sha256.clone(),
            release_rollback,
        },
    )
}
fn rename(app: &App, name: &str) {
    let mut w = app.configuration.get().unwrap().workspace;
    w.instances[0].name = name.into();
    save(app, w, vec![]);
}
fn cancel(app: &App, p: &Preview) {
    versions::cancel_preview(
        app,
        CancelPreview {
            token: p.token.clone(),
        },
    )
    .unwrap();
}
#[test]
fn draft_confirmations_reopen_and_explicit_deduplicated_versions() {
    let root = profile();
    let app = App::open(&root).unwrap();
    ready(&app);
    let before = app.configuration.get().unwrap();
    for _ in 0..3 {
        save(&app, before.workspace.clone(), vec![]);
    }
    assert!(app
        .configuration
        .store
        .revision_catalog()
        .unwrap()
        .is_empty());
    assert!(app.shutdown());
    let app = App::open(&root).unwrap();
    assert_eq!(app.configuration.get().unwrap().workspace, before.workspace);
    assert!(app.instances.lock().unwrap().is_empty());
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    assert!(app
        .configuration
        .store
        .revision_catalog()
        .unwrap()
        .is_empty());
    let published = confirm(&app, &p).unwrap();
    assert_eq!(published.result, "published");
    let old = app
        .configuration
        .store
        .revision(published.revision_id.as_ref().unwrap())
        .unwrap();
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    assert_eq!(p.details["unchanged"], true);
    assert_eq!(confirm(&app, &p).unwrap().result, "unchanged");
    assert_eq!(app.configuration.store.revision_catalog().unwrap().len(), 1);
    rename(&app, "Saved draft, not a version");
    assert_eq!(
        app.configuration
            .store
            .revision(published.revision_id.as_ref().unwrap())
            .unwrap(),
        old
    );
    let draft = app.configuration.get().unwrap().workspace;
    assert!(app.shutdown());
    let app = App::open(&root).unwrap();
    assert_eq!(app.configuration.get().unwrap().workspace, draft);
    assert_eq!(app.configuration.store.revision_catalog().unwrap().len(), 1);
    assert!(app.instances.lock().unwrap().is_empty());
    assert!(app.shutdown());
}
#[test]
fn protected_cross_instance_versions_retention_and_cancelled_or_stale_deletions() {
    let root = profile();
    let app = App::open(&root).unwrap();
    ready(&app);
    let ids = app
        .configuration
        .get()
        .unwrap()
        .workspace
        .instances
        .iter()
        .map(|i| i.id.clone())
        .collect::<Vec<_>>();
    let mut revisions = vec![];
    // 明确发布fixture历史；无启动/保存时裁剪，不触任何现有库。
    for n in 1..=14 {
        rename(&app, &format!("Version {n}"));
        revisions.push(
            app.configuration
                .store
                .publish(&app.configuration.get().unwrap().etag)
                .unwrap()
                .revision_id
                .unwrap(),
        );
    }
    hooks::apply_revision(&app, &ids[0], &revisions[0]).unwrap();
    hooks::apply_revision(&app, &ids[1], &revisions[1]).unwrap();
    for revision in [&revisions[2], &revisions[3]] {
        let selected = app
            .configuration
            .store
            .selections()
            .unwrap()
            .into_iter()
            .find(|s| s.instance_id == ids[1])
            .unwrap();
        app.configuration
            .store
            .select(&ids[1], revision, Some(selected.selection_etag))
            .unwrap();
    }
    let load = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            instance_id: ids[0].clone(),
            revision_id: revisions[4].clone(),
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    for n in [0, 1, 3, 4, 13] {
        assert!(
            matches!(versions::preview_delete(&app,deletion(&app,&[revisions[n].clone()])),Err(e) if e=="revision_protected")
        );
    }
    let rollback_only =
        versions::preview_delete(&app, deletion(&app, &[revisions[2].clone()])).unwrap();
    assert_eq!(
        rollback_only.details["rollbackReleases"]
            .as_array()
            .unwrap()
            .len(),
        1
    );
    cancel(&app, &rollback_only);
    let draft_before = app.configuration.get().unwrap().workspace;
    rename(&app, "Version 15");
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    assert_eq!(p.details["deleteRevisions"].as_array().unwrap().len(), 5);
    cancel(&app, &p);
    assert_eq!(
        app.configuration.store.revision_catalog().unwrap().len(),
        14
    );
    assert!(matches!(confirm(&app,&p),Err(e) if e=="preview_not_found"));
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    confirm(&app, &p).unwrap();
    let rows = app.configuration.store.revision_catalog().unwrap();
    assert_eq!(rows.len(), 10);
    for id in &revisions[..5] {
        assert!(app.configuration.store.revision(id).is_ok());
    }
    for id in &revisions[5..10] {
        assert!(app.configuration.store.revision(id).is_err());
    }
    assert_eq!(
        app.instance(&ids[0])
            .unwrap()
            .context
            .owner
            .loaded_revision(),
        revisions[0]
    );
    assert_eq!(
        app.instance(&ids[1])
            .unwrap()
            .context
            .owner
            .loaded_revision(),
        revisions[1]
    );
    assert_eq!(
        app.configuration.get().unwrap().workspace.instances[1],
        draft_before.instances[1]
    );
    cancel(&app, &load);
    let remove = versions::preview_delete(&app, deletion(&app, &[revisions[4].clone()])).unwrap();
    cancel(&app, &remove);
    assert!(app.configuration.store.revision(&revisions[4]).is_ok());
    let remove = versions::preview_delete(&app, deletion(&app, &[revisions[4].clone()])).unwrap();
    let changed_reference = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            instance_id: ids[0].clone(),
            revision_id: revisions[4].clone(),
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    assert!(matches!(confirm(&app,&remove),Err(e) if e=="revision_preview_stale"));
    assert!(app.configuration.store.revision(&revisions[4]).is_ok());
    cancel(&app, &changed_reference);
    cancel(&app, &remove);
    let remove = versions::preview_delete(&app, deletion(&app, &[revisions[4].clone()])).unwrap();
    confirm(&app, &remove).unwrap();
    assert!(app.configuration.store.revision(&revisions[4]).is_err());
    rename(&app, "Version 16");
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    assert_eq!(p.details["nextSavedSeq"], "16");
    confirm(&app, &p).unwrap();
    assert_eq!(
        app.configuration.store.revision_catalog().unwrap()[0].saved_seq,
        "16"
    );
    assert!(app.shutdown());
}
#[test]
fn publication_rollback_and_unknown_receipt_do_not_blindly_repeat() {
    let root = profile();
    let app = App::open(&root).unwrap();
    ready(&app);
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    app.configuration
        .store
        .test_fault("before_save_commit")
        .unwrap();
    assert!(matches!(confirm(&app,&p),Err(e) if e=="test_fault"));
    assert!(app
        .configuration
        .store
        .revision_catalog()
        .unwrap()
        .is_empty());
    app.configuration
        .store
        .test_fault("after_save_commit")
        .unwrap();
    assert!(matches!(confirm(&app,&p),Err(e) if e=="save_receipt_unknown"));
    assert_eq!(app.configuration.store.revision_catalog().unwrap().len(), 1);
    assert!(matches!(confirm(&app,&p),Err(e) if e=="revision_preview_stale"));
    cancel(&app, &p);
    let p = versions::preview_publish(&app, intent(&app, None)).unwrap();
    assert_eq!(p.details["unchanged"], true);
    confirm(&app, &p).unwrap();
    assert_eq!(app.configuration.store.revision_catalog().unwrap().len(), 1);
    assert!(app.shutdown());
}

#[test]
fn repeated_load_preserves_rollback_and_bulk_release_is_confirmed_atomic_and_durable() {
    let root = profile();
    let app = App::open(&root).unwrap();
    ready(&app);
    let ids: Vec<_> = app
        .configuration
        .get()
        .unwrap()
        .workspace
        .instances
        .iter()
        .map(|i| i.id.clone())
        .collect();
    let mut history = vec![];
    for n in 1..=4 {
        rename(&app, &format!("Synthetic version {n}"));
        history.push(
            app.configuration
                .store
                .publish(&app.configuration.get().unwrap().etag)
                .unwrap()
                .revision_id
                .unwrap(),
        );
    }
    for id in &ids {
        hooks::apply_revision(&app, id, &history[0]).unwrap();
        hooks::apply_revision(&app, id, &history[2]).unwrap();
        hooks::apply_revision(&app, id, &history[2]).unwrap();
    }
    let selections = app.configuration.store.selections().unwrap();
    assert!(selections.iter().all(
        |s| s.previous_revision_id.as_ref() == Some(&history[0]) && s.revision_id == history[2]
    ));
    let workspace = app.configuration.get().unwrap().workspace;
    let captures: Vec<_> = ids
        .iter()
        .map(|id| app.instance(id).unwrap().context.owner.capture().unwrap())
        .collect();
    let rows = versions::list(&app, 0).unwrap();
    assert_eq!(
        rows["rows"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["revisionId"] == history[0])
            .unwrap()["canDelete"],
        true
    );
    assert_eq!(
        rows["rows"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["revisionId"] == history[2])
            .unwrap()["canDelete"],
        false
    );
    let selected = [history[0].clone(), history[1].clone()];
    let p = versions::preview_delete(&app, deletion(&app, &selected)).unwrap();
    assert_eq!(p.details["deleteRevisions"].as_array().unwrap().len(), 2);
    assert_eq!(p.details["rollbackReleases"].as_array().unwrap().len(), 2);
    cancel(&app, &p);
    assert_eq!(
        serde_json::to_value(app.configuration.store.selections().unwrap()).unwrap(),
        serde_json::to_value(&selections).unwrap()
    );
    assert_eq!(app.configuration.store.revision_catalog().unwrap().len(), 4);
    let p = versions::preview_delete(&app, deletion(&app, &selected)).unwrap();
    assert!(matches!(confirm(&app,&p), Err(e) if e == "rollback_release_required"));
    app.configuration
        .store
        .test_fault("before_save_commit")
        .unwrap();
    assert!(matches!(confirm_releasing(&app,&p,true), Err(e) if e == "test_fault"));
    assert_eq!(
        serde_json::to_value(app.configuration.store.selections().unwrap()).unwrap(),
        serde_json::to_value(&selections).unwrap()
    );
    assert!(selected
        .iter()
        .all(|id| app.configuration.store.revision(id).is_ok()));
    app.configuration
        .store
        .test_fault("after_save_commit")
        .unwrap();
    assert!(matches!(confirm_releasing(&app,&p,true), Err(e) if e == "save_receipt_unknown"));
    assert!(selected
        .iter()
        .all(|id| app.configuration.store.revision(id).is_err()));
    assert!(app
        .configuration
        .store
        .selections()
        .unwrap()
        .iter()
        .all(|s| s.previous_revision_id.is_none() && s.revision_id == history[2]));
    assert!(matches!(confirm_releasing(&app,&p,true), Err(e) if e == "revision_preview_stale"));
    for (id, old) in ids.iter().zip(captures) {
        let current = app.instance(id).unwrap().context.owner.capture().unwrap();
        assert_eq!(
            (
                current.loaded_revision,
                current.epoch,
                current.seq,
                current.values
            ),
            (old.loaded_revision, old.epoch, old.seq, old.values)
        );
    }
    assert_eq!(app.configuration.get().unwrap().workspace, workspace);
    assert_eq!(
        app.configuration.store.revision_catalog().unwrap()[0].saved_seq,
        "4"
    );
    assert!(app.shutdown());
    let app = App::open(&root).unwrap();
    assert!(app
        .configuration
        .store
        .selections()
        .unwrap()
        .iter()
        .all(|s| s.previous_revision_id.is_none()));
    for id in &ids {
        assert!(app.instance(id).unwrap().stopped());
        assert_eq!(
            app.instance(id).unwrap().context.owner.loaded_revision(),
            history[2]
        );
    }
    assert!(app.shutdown());
}

#[test]
fn bulk_delete_rejects_protected_invalid_or_newly_referenced_items_without_partial_changes() {
    let root = profile();
    let app = App::open(&root).unwrap();
    ready(&app);
    let ids: Vec<_> = app
        .configuration
        .get()
        .unwrap()
        .workspace
        .instances
        .iter()
        .map(|i| i.id.clone())
        .collect();
    let mut history = vec![];
    for n in 1..=5 {
        rename(&app, &format!("Synthetic version {n}"));
        history.push(
            app.configuration
                .store
                .publish(&app.configuration.get().unwrap().etag)
                .unwrap()
                .revision_id
                .unwrap(),
        );
    }
    hooks::apply_revision(&app, &ids[0], &history[1]).unwrap();
    hooks::apply_revision(&app, &ids[1], &history[0]).unwrap();
    hooks::apply_revision(&app, &ids[1], &history[2]).unwrap();
    let before = serde_json::to_value(app.configuration.store.selections().unwrap()).unwrap();
    for protected in [&history[1], &history[2], &history[4]] {
        assert!(
            matches!(versions::preview_delete(&app,deletion(&app,&[history[0].clone(), protected.clone()])), Err(e) if e == "revision_protected")
        );
    }
    for invalid in [
        vec![],
        vec![history[0].clone(), history[0].clone()],
        (0..101).map(|_| uuid()).collect(),
    ] {
        assert!(
            matches!(versions::preview_delete(&app,deletion(&app,&invalid)), Err(e) if e == "revision_selection")
        );
    }
    assert!(
        matches!(versions::preview_delete(&app,deletion(&app,&[uuid()])), Err(e) if e == "revision_not_found")
    );
    let remove = versions::preview_delete(
        &app,
        deletion(&app, &[history[0].clone(), history[3].clone()]),
    )
    .unwrap();
    let load = apply::preview(
        &app,
        ApplyIntent {
            expected_etag: app.configuration.get().unwrap().etag,
            instance_id: ids[0].clone(),
            revision_id: history[3].clone(),
            retention: "preserve_compatible_hold".into(),
        },
    )
    .unwrap();
    assert_eq!(
        versions::list(&app, 0).unwrap()["rows"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["revisionId"] == history[3])
            .unwrap()["canDelete"],
        false
    );
    assert!(
        matches!(confirm_releasing(&app,&remove,true), Err(e) if e == "revision_preview_stale")
    );
    assert_eq!(app.configuration.store.revision_catalog().unwrap().len(), 5);
    assert_eq!(
        serde_json::to_value(app.configuration.store.selections().unwrap()).unwrap(),
        before
    );
    cancel(&app, &load);
    assert_eq!(
        versions::list(&app, 0).unwrap()["rows"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["revisionId"] == history[3])
            .unwrap()["canDelete"],
        true
    );
    cancel(&app, &remove);
    assert!(app.shutdown());
}
