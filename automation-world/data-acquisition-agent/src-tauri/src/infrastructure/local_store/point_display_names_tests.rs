//! DAA-018：配置级双语名称、旧请求与单次预览确认的隔离验证。
use super::{delivery_tests, source_import_tests, tests, *};
use crate::domain::{local_configuration::*, point_naming::*};
use serde_json::{json, Value};
use std::time::{Duration, Instant};

fn confirmation(input: NameRequest, preview: &NamePreview) -> NameConfirmation {
    NameConfirmation {
        input,
        preview_token: preview.preview_token.clone(),
        input_digest: preview.input_digest.clone(),
    }
}

fn save_names(
    e: &crate::services::local_supervisor::LocalEngine,
    point_id: &str,
    zh: &str,
    en: &str,
) -> crate::domain::local_runtime::ConfigurationView {
    let v = e.configuration().unwrap();
    let point = v.draft.points.iter().find(|p| p.id == point_id).unwrap();
    let request: NameRequest = serde_json::from_value(json!({"expectedEtag":v.etag,"plcId":point.plc_id,"pointIds":[point_id],"intent":"edit","patch":{"displayNames":{"zh-CN":zh,"en-US":en}}})).unwrap();
    let preview = e.preview_point_names(request.clone()).unwrap();
    assert!(preview.can_confirm);
    e.confirm_point_names(confirmation(request, &preview))
        .unwrap()
}

fn saved_state(e: &crate::services::local_supervisor::LocalEngine) -> Value {
    e.storage
        .call(true, |s| {
            Ok(json!({
                "draft_and_sources": source_import_tests::dump(&s.config, &["configuration_draft", "source_documents"]),
                "history": source_import_tests::protected(s),
                "delivery": source_import_tests::dump(&s.runtime, &["delivery_batches", "delivery_receipts"]),
            }))
        })
        .unwrap()
}

#[test]
fn point_display_names_plain_save_requires_preview_and_preserves_history() {
    let mut s = delivery_tests::legacy(3);
    let profile = s.dir.parent().unwrap().to_path_buf();
    let c = tests::configuration();
    let revision = tests::activated(&mut s, &c);
    s.commit_cycle(tests::cycle(&c, &revision)).unwrap();
    s.clean_exit().unwrap();
    drop(s);
    let e = source_import_tests::engine(&profile);
    let before = e.configuration().unwrap();
    let first = before.draft.points[0].id.clone();
    let second = before
        .draft
        .points
        .iter()
        .find(|p| p.plc_id != before.draft.points[0].plc_id)
        .unwrap()
        .id
        .clone();
    let state = saved_state(&e);

    // 产品 IPC 无预览同时新增两台 PLC 的合法名称必须拒绝。
    let mut added = before.draft.clone();
    for id in [&first, &second] {
        added.point_display_names.insert(
            id.clone(),
            PointDisplayNames {
                zh_cn: "禁止绕过".into(),
                en_us: "NO_PREVIEW".into(),
            },
        );
    }
    let result = crate::commands::local_acquisition::dispatch(
        e.clone(),
        "daa_save_draft",
        json!({"draft":added,"expectedEtag":before.etag}),
    );
    assert_eq!(result.unwrap_err(), "name_preview_required");
    assert_eq!(saved_state(&e), state);
    assert_eq!(e.configuration().unwrap().etag, before.etag);
    let mut added_empty = before.draft.clone();
    added_empty
        .point_display_names
        .insert(first.clone(), PointDisplayNames::default());
    assert_eq!(
        e.save(added_empty, before.etag.clone()).unwrap_err(),
        "name_preview_required"
    );
    assert_eq!(saved_state(&e), state);

    save_names(&e, &first, "中文", "English");
    let v = save_names(&e, &second, "另一台", "Other PLC");
    let state = saved_state(&e);
    let mut changed = v.draft.clone();
    changed.point_display_names.get_mut(&first).unwrap().en_us = "changed".into();
    let mut cleared_one = v.draft.clone();
    cleared_one
        .point_display_names
        .get_mut(&first)
        .unwrap()
        .zh_cn
        .clear();
    let mut cleared_both_values = v.draft.clone();
    *cleared_both_values
        .point_display_names
        .get_mut(&first)
        .unwrap() = PointDisplayNames::default();
    let mut cleared_both = v.draft.clone();
    cleared_both.point_display_names.remove(&first);
    for candidate in [changed, cleared_one, cleared_both_values, cleared_both] {
        assert_eq!(
            e.save(candidate, v.etag.clone()).unwrap_err(),
            "name_preview_required"
        );
        assert_eq!(saved_state(&e), state);
        assert_eq!(e.configuration().unwrap().etag, v.etag);
    }

    let mut deletion = v.draft.clone();
    let removed_plc = deletion
        .points
        .iter()
        .find(|p| p.id == first)
        .unwrap()
        .plc_id
        .clone();
    deletion.plcs.retain(|p| p.id != removed_plc);
    deletion.dbs.retain(|d| d.plc_id != removed_plc);
    deletion.points.retain(|p| p.plc_id != removed_plc);
    deletion.groups.retain(|g| g.plc_id != removed_plc);
    deletion.sources.retain(|s| s.plc_id != removed_plc);
    let mut tampered = deletion.clone();
    tampered.point_display_names.get_mut(&second).unwrap().en_us = "cross PLC tampering".into();
    assert_eq!(
        e.save(tampered, v.etag.clone()).unwrap_err(),
        "name_preview_required"
    );
    assert_eq!(saved_state(&e), state);
    assert_eq!(e.configuration().unwrap().etag, v.etag);
    // UI 已清理被删 PLC 的条目时也是合法删除。
    deletion.point_display_names.remove(&first);
    let saved = e.save(deletion, v.etag).unwrap();
    assert!(!saved.draft.point_display_names.contains_key(&first));
    assert_eq!(saved.draft.point_display_names[&second].en_us, "Other PLC");
    e.shutdown();
}

#[test]
fn point_display_names_legacy_empty_entry_is_not_silently_rewritten() {
    let mut s = delivery_tests::legacy(3);
    let profile = s.dir.parent().unwrap().to_path_buf();
    let mut c = tests::configuration();
    let point = c.points[0].id.clone();
    c.point_display_names
        .insert(point.clone(), PointDisplayNames::default());
    tests::activated(&mut s, &c);
    s.clean_exit().unwrap();
    drop(s);
    let e = source_import_tests::engine(&profile);
    let v = e.configuration().unwrap();
    let before = saved_state(&e);
    let same = e.save(v.draft.clone(), v.etag.clone()).unwrap();
    assert_eq!(same.etag, v.etag);
    assert_eq!(saved_state(&e), before);
    let mut other_change = v.draft.clone();
    other_change.storage.retention_days = 8;
    let saved = e.save(other_change, v.etag).unwrap();
    assert_eq!(
        saved.draft.point_display_names[&point],
        PointDisplayNames::default()
    );
    let state = saved_state(&e);
    let mut removed = saved.draft.clone();
    removed.point_display_names.remove(&point);
    assert_eq!(
        e.save(removed, saved.etag.clone()).unwrap_err(),
        "name_preview_required"
    );
    assert_eq!(saved_state(&e), state);
    assert_eq!(e.configuration().unwrap().etag, saved.etag);
    e.shutdown();
}

#[test]
fn point_display_names_strict_map_and_optional_patch() {
    let mut c = tests::configuration();
    let point = c.points[0].id.clone();
    let old = serde_json::to_string(&c).unwrap();
    assert!(!old.contains("pointDisplayNames"));
    assert_eq!(serde_json::from_str::<Configuration>(&old).unwrap(), c);
    let mut value = serde_json::to_value(&c).unwrap();
    for bad in [
        json!(null),
        json!({point.clone(): null}),
        json!({point.clone(): {"zh-CN":"x"}}),
        json!({point.clone(): {"zh-CN":"x","en-US":null}}),
        json!({point.clone(): {"zh-CN":"x","en-US":"y","other":"z"}}),
        json!({point.clone(): {"zh-CN":"中".repeat(86),"en-US":"y"}}),
    ] {
        value["pointDisplayNames"] = bad;
        assert!(serde_json::from_value::<Configuration>(value.clone()).is_err());
    }
    let duplicate = format!("{{\"{point}\":{{\"zh-CN\":\"a\",\"en-US\":\"b\"}},\"{point}\":{{\"zh-CN\":\"c\",\"en-US\":\"d\"}}}}");
    let raw = old.replacen(
        "\"schemaVersion\":1",
        &format!("\"pointDisplayNames\":{duplicate},\"schemaVersion\":1"),
        1,
    );
    assert!(serde_json::from_str::<Configuration>(&raw).is_err());
    c.point_display_names.insert(
        point.clone(),
        PointDisplayNames {
            zh_cn: " 中 ".into(),
            en_us: " English ".into(),
        },
    );
    assert!(validate_display_names(&c).is_ok());
    assert_eq!(
        serde_json::from_str::<Configuration>(&serde_json::to_string(&c).unwrap()).unwrap(),
        c
    );
    c.point_display_names
        .insert(id(), PointDisplayNames::default());
    assert_eq!(
        validate_display_names(&c).unwrap_err(),
        "point_display_names_invalid"
    );
    let legacy: PointPatch = serde_json::from_value(json!({"name":"unchanged"})).unwrap();
    assert!(!serde_json::to_string(&legacy)
        .unwrap()
        .contains("displayNames"));
    for bad in [
        json!(null),
        json!({"zh-CN":"x"}),
        json!({"zh-CN":"x","en-US":"y","extra":"z"}),
        json!({"zh-CN":"x","en-US":2}),
        json!({"zh-CN":"中".repeat(86),"en-US":""}),
    ] {
        assert!(serde_json::from_value::<PointPatch>(json!({"displayNames":bad})).is_err());
    }
    assert!(serde_json::from_value::<PointPatch>(
        json!({"displayNames":{"zh-CN":"中".repeat(85),"en-US":"a".repeat(256)}})
    )
    .is_ok());
}

#[test]
fn point_display_names_preview_atomic_cas_and_old_requests() {
    let mut s = delivery_tests::legacy(3);
    let profile = s.dir.parent().unwrap().to_path_buf();
    let c = tests::configuration();
    let revision = tests::activated(&mut s, &c);
    s.commit_cycle(tests::cycle(&c, &revision)).unwrap();
    s.clean_exit().unwrap();
    drop(s);
    let e = source_import_tests::engine(&profile);
    let before = e.configuration().unwrap();
    let pid = before.draft.points[0].id.clone();
    let plc = before.draft.points[0].plc_id.clone();
    let original_other = before.draft.points[1].clone();
    let request: NameRequest = serde_json::from_value(json!({"expectedEtag":before.etag,"plcId":plc,"pointIds":[pid],"intent":"edit","patch":{"name":"Manual_DAA018","comment":"COMMENT_DAA018","displayNames":{"zh-CN":" 中文 ","en-US":" English "}}})).unwrap();
    let preview = e.preview_point_names(request.clone()).unwrap();
    assert!(preview.can_confirm);
    assert_eq!(e.configuration().unwrap().etag, request.expected_etag);
    let mut tampered = confirmation(request.clone(), &preview);
    tampered
        .input
        .patch
        .as_mut()
        .unwrap()
        .display_names
        .as_mut()
        .unwrap()
        .en_us = "tampered".into();
    assert!(e.confirm_point_names(tampered).is_err());
    assert_eq!(e.configuration().unwrap().etag, request.expected_etag);
    let preview = e.preview_point_names(request.clone()).unwrap();
    let mut forged = confirmation(request.clone(), &preview);
    forged.preview_token = id();
    assert!(e.confirm_point_names(forged).is_err());
    let preview = e.preview_point_names(request.clone()).unwrap();
    e.name_preview.lock().unwrap().as_mut().unwrap().created =
        Instant::now() - Duration::from_secs(301);
    assert!(e
        .confirm_point_names(confirmation(request.clone(), &preview))
        .is_err());
    let mut wrong_plc = request.clone();
    wrong_plc.plc_id = before.draft.plcs[1].id.clone();
    assert!(e.preview_point_names(wrong_plc).is_err());
    let preview = e.preview_point_names(request.clone()).unwrap();
    e.storage.call(false, |s| s.config.execute_batch("CREATE TEMP TABLE daa018_update_count(n INTEGER); CREATE TEMP TRIGGER daa018_count AFTER UPDATE ON main.configuration_draft BEGIN INSERT INTO daa018_update_count VALUES(1); END;").map_err(sql_error)).unwrap();
    let saved = e
        .confirm_point_names(confirmation(request.clone(), &preview))
        .unwrap();
    assert_ne!(saved.etag, request.expected_etag);
    assert_eq!(saved.draft.points[0].name, "Manual_DAA018");
    assert_eq!(saved.draft.points[0].comment, "COMMENT_DAA018");
    assert_eq!(saved.draft.points[1], original_other);
    assert_eq!(saved.draft.point_display_names[&pid].zh_cn, " 中文 ");
    assert_eq!(saved.draft.point_display_names[&pid].en_us, " English ");
    assert_eq!(
        e.storage
            .call(true, |s| s
                .config
                .query_row::<i64, _, _>("SELECT count(*) FROM daa018_update_count", [], |r| r
                    .get(0))
                .map_err(sql_error))
            .unwrap(),
        1
    );
    assert!(e
        .confirm_point_names(confirmation(request.clone(), &preview))
        .is_err());
    let legacy: NameRequest = serde_json::from_value(json!({"expectedEtag":saved.etag,"plcId":plc,"pointIds":[pid],"intent":"edit","patch":{"comment":"Legacy edit"}})).unwrap();
    assert!(!serde_json::to_string(&legacy)
        .unwrap()
        .contains("displayNames"));
    let p = e.preview_point_names(legacy.clone()).unwrap();
    let legacy_saved = e.confirm_point_names(confirmation(legacy, &p)).unwrap();
    assert_eq!(
        legacy_saved.draft.point_display_names[&pid].en_us,
        " English "
    );
    let mut direct = legacy_saved.draft.clone();
    direct.points[0].name = "Bypass".into();
    assert_eq!(
        e.save(direct, legacy_saved.etag.clone()).unwrap_err(),
        "name_preview_required"
    );
    let mut clear: Value = json!({"expectedEtag":legacy_saved.etag,"plcId":plc,"pointIds":[pid],"intent":"edit","patch":{"displayNames":{"zh-CN":"","en-US":" English "}}});
    let r: NameRequest = serde_json::from_value(clear.clone()).unwrap();
    let p = e.preview_point_names(r.clone()).unwrap();
    let one = e.confirm_point_names(confirmation(r, &p)).unwrap();
    assert_eq!(one.draft.point_display_names[&pid].zh_cn, "");
    assert_eq!(one.draft.point_display_names[&pid].en_us, " English ");
    clear["expectedEtag"] = json!(one.etag);
    clear["patch"]["displayNames"]["en-US"] = json!("");
    let r: NameRequest = serde_json::from_value(clear).unwrap();
    let p = e.preview_point_names(r.clone()).unwrap();
    let empty = e.confirm_point_names(confirmation(r, &p)).unwrap();
    assert!(!empty.draft.point_display_names.contains_key(&pid));
    e.shutdown();
}

#[test]
fn point_display_names_reimport_conflict_and_plc_delete_preserve_identity() {
    let mut s = delivery_tests::legacy(3);
    let profile = s.dir.parent().unwrap().to_path_buf();
    let c = tests::configuration();
    tests::activated(&mut s, &c);
    s.clean_exit().unwrap();
    drop(s);
    let e = source_import_tests::engine(&profile);
    let v = e.configuration().unwrap();
    let first = v.draft.points[0].id.clone();
    let other = v
        .draft
        .points
        .iter()
        .find(|p| p.plc_id != v.draft.points[0].plc_id)
        .unwrap()
        .id
        .clone();
    save_names(&e, &first, "同一身份", "same identity");
    let v = save_names(&e, &other, "另一台", "other PLC");
    let db = v
        .draft
        .dbs
        .iter()
        .find(|d| d.id == v.draft.points[0].db_id)
        .unwrap();
    let source = v
        .draft
        .sources
        .iter()
        .find(|s| s.id == db.source_id)
        .unwrap();
    let req = source_import_tests::req(&v.draft, &v.etag, &[(&source.name, &source.content)]);
    let imported = source_import_tests::confirm(&e, req);
    assert_eq!(
        imported.configuration.point_display_names[&first].en_us,
        "same identity"
    );
    assert!(imported.configuration.points.iter().any(|p| p.id == first));
    let source_name = source.name.clone();
    let changed_source = source
        .content
        .replace("b1 : Bool;", "b1 : Bool; // DAA018 changed source\n");
    assert_ne!(changed_source, source.content);
    let v = e.configuration().unwrap();
    let changed = source_import_tests::req(&v.draft, &v.etag, &[(&source_name, &changed_source)]);
    let imported = source_import_tests::confirm(&e, changed);
    assert!(!imported.unchanged);
    assert!(imported.configuration.points.iter().any(|p| p.id == first));
    assert_eq!(
        imported.configuration.point_display_names[&first].en_us,
        "same identity"
    );
    let v = e.configuration().unwrap();
    let renamed = changed_source.replace("b0 : Bool;", "renamed : Bool;");
    let rejected = source_import_tests::req(&v.draft, &v.etag, &[(&source_name, &renamed)]);
    assert!(!e.import_selected(rejected).unwrap().can_confirm);
    assert_eq!(e.configuration().unwrap().draft, v.draft);
    let mut rebound = v.draft.clone();
    rebound
        .points
        .iter_mut()
        .find(|p| p.id == first)
        .unwrap()
        .id = id();
    assert!(e.save(rebound, v.etag.clone()).is_err());
    assert_eq!(e.configuration().unwrap().draft, v.draft);
    let request: NameRequest = serde_json::from_value(json!({"expectedEtag":v.etag,"plcId":v.draft.points[0].plc_id,"pointIds":[first],"intent":"edit","patch":{"displayNames":{"zh-CN":"conflict","en-US":"conflict"}}})).unwrap();
    let p = e.preview_point_names(request.clone()).unwrap();
    let mut concurrent = v.draft.clone();
    concurrent.storage.retention_days = 8;
    let v = e.save(concurrent, v.etag).unwrap();
    assert!(e.confirm_point_names(confirmation(request, &p)).is_err());
    assert_eq!(v.draft.point_display_names[&first].zh_cn, "同一身份");
    let mut deletion = v.draft.clone();
    let removed_plc = deletion
        .points
        .iter()
        .find(|p| p.id == first)
        .unwrap()
        .plc_id
        .clone();
    deletion.plcs.retain(|p| p.id != removed_plc);
    deletion.dbs.retain(|d| d.plc_id != removed_plc);
    deletion.points.retain(|p| p.plc_id != removed_plc);
    deletion.groups.retain(|g| g.plc_id != removed_plc);
    deletion.sources.retain(|s| s.plc_id != removed_plc);
    // 服务端清除所删 PLC 的旧映射；调用者无需手动清理，也不能清理其他 PLC。
    let saved = e.save(deletion, v.etag).unwrap();
    assert!(!saved.draft.point_display_names.contains_key(&first));
    assert_eq!(saved.draft.point_display_names[&other].en_us, "other PLC");
    e.shutdown();
}

#[test]
fn point_display_names_only_does_not_regenerate_an_unconfirmed_auto_name() {
    let mut s = delivery_tests::legacy(3);
    let profile = s.dir.parent().unwrap().to_path_buf();
    let mut c = tests::configuration();
    c.points[0].name = "DB1_B0_0_Bool".into();
    c.points[0].name_mode = Some(NameMode::AutoAddress);
    c.points[0].enabled = false;
    c.points[0].address.as_mut().unwrap().confirmed = false;
    tests::activated(&mut s, &c);
    s.clean_exit().unwrap();
    drop(s);
    let e = source_import_tests::engine(&profile);
    let v = e.configuration().unwrap();
    let point = v.draft.points[0].clone();
    // 缺少新字段的旧请求仍按原有规则重新计算未确认的自动地址名。
    let legacy: NameRequest = serde_json::from_value(json!({"expectedEtag":v.etag,"plcId":point.plc_id,"pointIds":[point.id],"intent":"edit","patch":{"comment":"legacy"}})).unwrap();
    let old_preview = e.preview_point_names(legacy).unwrap();
    assert_eq!(old_preview.rows[0].proposed_name, "");
    assert_eq!(old_preview.rows[0].proposed_mode, Some(NameMode::Pending));
    let r: NameRequest = serde_json::from_value(json!({"expectedEtag":v.etag,"plcId":point.plc_id,"pointIds":[point.id],"intent":"edit","patch":{"displayNames":{"zh-CN":"显示","en-US":"Label"}}})).unwrap();
    let p = e.preview_point_names(r.clone()).unwrap();
    assert!(p.can_confirm);
    let saved = e.confirm_point_names(confirmation(r, &p)).unwrap();
    assert_eq!(saved.draft.points[0], point);
    e.shutdown();
}

#[test]
fn point_display_names_configuration_capacity_rejects_without_partial_write() {
    use crate::domain::local_sample::{digest, encode};
    let mut s = delivery_tests::legacy(3);
    let mut c = tests::configuration();
    let source = c.sources[0].clone();
    for n in 0..15 {
        let mut extra = source.clone();
        extra.id = id();
        extra.name = format!("synthetic-capacity-{n}.db");
        extra.content = "x".repeat(1024 * 1024 - 1);
        extra.sha256 = digest(&extra.content);
        c.sources.push(extra);
    }
    let mut extra = source;
    extra.id = id();
    extra.name = "synthetic-capacity-final.db".into();
    extra.content.clear();
    extra.sha256 = digest(&extra.content);
    c.sources.push(extra);
    let base = encode(&c).unwrap().len();
    let remaining = 16 * 1024 * 1024 - 8192 - base;
    assert!(remaining < 1024 * 1024);
    let last = c.sources.last_mut().unwrap();
    last.content = "x".repeat(remaining);
    last.sha256 = digest(&last.content);
    assert!(encode(&c).unwrap().len() < 16 * 1024 * 1024);
    for p in &c.points {
        c.point_display_names.insert(
            p.id.clone(),
            PointDisplayNames {
                zh_cn: "a".repeat(256),
                en_us: "b".repeat(256),
            },
        );
    }
    assert!(encode(&c).unwrap().len() > 16 * 1024 * 1024);
    let v = s.configuration().unwrap();
    let before = source_import_tests::dump(
        &s.config,
        &[
            "configuration_draft",
            "source_documents",
            "configuration_revisions",
        ],
    );
    assert_eq!(
        s.save_draft(&c, &v.etag).unwrap_err(),
        "configuration_limits"
    );
    assert_eq!(
        before,
        source_import_tests::dump(
            &s.config,
            &[
                "configuration_draft",
                "source_documents",
                "configuration_revisions"
            ]
        )
    );
    s.clean_exit().unwrap();
}
