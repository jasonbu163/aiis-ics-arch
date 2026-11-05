//! 工作区版本发布/批量删除：区分使用保护和可确认放弃的回退保留，复核全部实例/预览引用。
use crate::{
    app::App,
    domain::configuration::digest,
    infrastructure::config_store::{
        RevisionInfo, RollbackRelease, SaveResult, Selection, Snapshot,
    },
    services::configuration::Preview,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

const RECENT_VERSIONS: usize = 5;
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct VersionIntent {
    pub expected_etag: String,
    pub revision_id: Option<String>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct DeleteIntent {
    pub expected_etag: String,
    pub revision_ids: Vec<String>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct VersionConfirmation {
    pub expected_etag: String,
    pub token: String,
    pub candidate_sha256: String,
    #[serde(default)]
    pub release_rollback: bool,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CancelPreview {
    pub token: String,
}
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Reference {
    pub reason: String,
    pub instance_id: Option<String>,
}
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct VersionRow {
    #[serde(flatten)]
    pub revision: RevisionInfo,
    pub protection: Vec<Reference>,
    pub can_delete: bool,
}
struct State {
    draft: Snapshot,
    rows: Vec<VersionRow>,
    selections: Vec<Selection>,
}
impl State {
    fn fingerprint(&self) -> String {
        digest(&(&self.draft.etag, &self.rows, &self.selections))
    }
    fn protected(&self, publish: bool) -> Vec<String> {
        self.rows
            .iter()
            .filter(|r| {
                if publish {
                    !r.protection.is_empty()
                } else {
                    !r.can_delete
                }
            })
            .map(|r| r.revision.revision_id.clone())
            .collect()
    }
}
fn state(app: &App) -> Result<State, String> {
    let draft = app.configuration.get()?;
    let selections = app.configuration.store.selections()?;
    let loaded = app
        .instances
        .lock()
        .unwrap()
        .iter()
        .map(|(id, i)| (id.clone(), i.context.owner.loaded_revision()))
        .collect::<Vec<_>>();
    let previews = app.configuration.revision_previews();
    let rows = app
        .configuration
        .store
        .revision_catalog()?
        .into_iter()
        .map(|revision| {
            let mut protection = vec![];
            let mut add = |reason: &str, instance_id: Option<String>| {
                protection.push(Reference {
                    reason: reason.into(),
                    instance_id,
                })
            };
            if draft.latest_revision.as_ref() == Some(&revision.revision_id) {
                add("latest", None);
            }
            for s in &selections {
                if s.revision_id == revision.revision_id {
                    add("selected", Some(s.instance_id.clone()));
                }
                if s.previous_revision_id.as_ref() == Some(&revision.revision_id) {
                    add("previous", Some(s.instance_id.clone()));
                }
            }
            for (id, version) in &loaded {
                if *version == revision.revision_id {
                    add("loaded", Some(id.clone()));
                }
            }
            for (version, id) in &previews {
                if *version == revision.revision_id {
                    add("preview", Some(id.clone()));
                }
            }
            VersionRow {
                can_delete: protection.iter().all(|p| p.reason == "previous"),
                revision,
                protection,
            }
        })
        .collect();
    Ok(State {
        draft,
        rows,
        selections,
    })
}
pub fn list(app: &App, offset: u32) -> Result<Value, String> {
    let _control = app.revision_control.lock().unwrap();
    let state = state(app)?;
    Ok(
        json!({"rows":state.rows.iter().skip(offset as usize).take(100).collect::<Vec<_>>(),"total":state.rows.len()}),
    )
}
pub fn preview_publish(app: &App, intent: VersionIntent) -> Result<Preview, String> {
    let _control = app.revision_control.lock().unwrap();
    if intent.revision_id.is_some() {
        return Err("revision_selection".into());
    }
    let state = state(app)?;
    let unchanged = match &state.draft.latest_revision {
        Some(id) => app.configuration.store.revision(id)? == state.draft.workspace,
        None => false,
    };
    // 新版占一个名额；只在明确发布的确认事务内清理，启动/保存草稿都不裁剪。
    let remove: Vec<_> = state
        .rows
        .iter()
        .skip(RECENT_VERSIONS - 1)
        .filter(|r| !unchanged && r.protection.is_empty())
        .map(|r| r.revision.clone())
        .collect();
    let seq = state
        .rows
        .first()
        .map(|r| r.revision.saved_seq.parse::<u64>().unwrap_or(0))
        .unwrap_or(0);
    let details = json!({"fingerprint":state.fingerprint(),"unchanged":unchanged,
        "nextSavedSeq":(if unchanged { seq } else { seq + 1 }).to_string(),
        "deleteRevisions":remove,"rollbackReleases":[],"retainRecent":RECENT_VERSIONS});
    app.configuration.preview(
        "publish_revision",
        &intent.expected_etag,
        state.draft.workspace,
        details,
    )
}
pub fn preview_delete(app: &App, intent: DeleteIntent) -> Result<Preview, String> {
    let _control = app.revision_control.lock().unwrap();
    let state = state(app)?;
    let ids: std::collections::BTreeSet<_> = intent.revision_ids.iter().cloned().collect();
    if ids.is_empty() || ids.len() > 100 || ids.len() != intent.revision_ids.len() {
        return Err("revision_selection".into());
    }
    for id in &ids {
        let row = state
            .rows
            .iter()
            .find(|r| &r.revision.revision_id == id)
            .ok_or("revision_not_found")?;
        if !row.can_delete {
            return Err("revision_protected".into());
        }
    }
    let remove: Vec<_> = state
        .rows
        .iter()
        .filter(|r| ids.contains(&r.revision.revision_id))
        .map(|r| &r.revision)
        .collect();
    let releases: Vec<_> = state
        .selections
        .iter()
        .filter_map(|s| {
            s.previous_revision_id
                .as_ref()
                .filter(|id| ids.contains(*id))
                .map(|id| RollbackRelease {
                    instance_id: s.instance_id.clone(),
                    revision_id: id.clone(),
                    selection_etag: s.selection_etag.clone(),
                })
        })
        .collect();
    let details = json!({"fingerprint":state.fingerprint(),"deleteRevisions":remove,"rollbackReleases":releases,"retainRecent":RECENT_VERSIONS});
    app.configuration.preview(
        "delete_revisions",
        &intent.expected_etag,
        state.draft.workspace,
        details,
    )
}
pub fn confirm(app: &App, kind: &str, intent: VersionConfirmation) -> Result<SaveResult, String> {
    let _control = app.revision_control.lock().unwrap();
    if !["publish_revision", "delete_revisions"].contains(&kind) {
        return Err("revision_selection".into());
    }
    let (_, details) = app.configuration.pending_candidate(
        kind,
        &intent.token,
        &intent.expected_etag,
        &intent.candidate_sha256,
    )?;
    let state = state(app)?;
    if state.fingerprint() != details["fingerprint"].as_str().unwrap_or("") {
        return Err("revision_preview_stale".into());
    }
    let remove: Vec<RevisionInfo> = serde_json::from_value(details["deleteRevisions"].clone())
        .map_err(|_| "revision_selection")?;
    let releases: Vec<RollbackRelease> =
        serde_json::from_value(details["rollbackReleases"].clone())
            .map_err(|_| "revision_selection")?;
    if !releases.is_empty() && !intent.release_rollback {
        return Err("rollback_release_required".into());
    }
    if kind == "publish_revision" && intent.release_rollback {
        return Err("revision_selection".into());
    }
    let saved = app.configuration.store.revise(
        &intent.expected_etag,
        kind == "publish_revision",
        remove.iter().map(|r| r.revision_id.clone()).collect(),
        state.protected(kind == "publish_revision"),
        releases.clone(),
    )?;
    app.configuration.finish_preview(&intent.token);
    app.events.put(json!({"event":"configuration_versions_committed","action":kind,"result":saved.result,"revision":saved.revision_id,"deletedCount":remove.len(),"releasedRollbackCount":releases.len()}));
    Ok(saved)
}
pub fn cancel_preview(app: &App, intent: CancelPreview) -> Result<Value, String> {
    let _control = app.revision_control.lock().unwrap();
    app.configuration.finish_preview(&intent.token);
    Ok(json!({"result":"cancelled","committed":false}))
}
