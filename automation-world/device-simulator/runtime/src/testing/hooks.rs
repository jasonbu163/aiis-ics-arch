//! 显式owned测试输入与产品配置服务装配；不拥有image或另一套策略实现。
use crate::{
    app::App,
    domain::configuration::Workspace,
    services::{
        apply::{self, ApplyConfirmation, ApplyIntent},
        configuration::SaveIntent,
        layout::{self, LayoutIntent},
        naming::{self, NamesIntent},
    },
};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
pub fn encode<T: Serialize>(value: &T) -> Result<String, String> {
    serde_json::to_string(value).map_err(|_| "test_json_encode".into())
}

#[derive(Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Manifest {
    pub task_id: String,
    pub revision: String,
    pub role: String,
    pub run_id: String,
    pub source_candidate: String,
    pub owned_marker: String,
    pub profile_dir: PathBuf,
    pub workspace: Option<PathBuf>,
    pub allowed_ports: Vec<u16>,
    pub scenario: Option<String>,
}
impl Manifest {
    pub fn read(path: &Path) -> Result<Self, String> {
        let root = Path::new("/private/tmp/arch-aw-005-r5-exec");
        if !path.is_absolute()
            || path.is_symlink()
            || path
                .components()
                .any(|p| matches!(p, std::path::Component::ParentDir))
            || !path.starts_with(root.join("profile"))
        {
            return Err("test_manifest_path".into());
        }
        let mut current = Some(path);
        while let Some(p) = current {
            if p.is_symlink() {
                return Err("test_manifest_symlink".into());
            }
            current = p.parent();
        }
        let metadata = std::fs::metadata(path).map_err(|_| "test_manifest_missing")?;
        if metadata.len() > 16 * 1024 {
            return Err("test_manifest_capacity".into());
        }
        let manifest: Self =
            serde_json::from_slice(&std::fs::read(path).map_err(|_| "test_manifest_read")?)
                .map_err(|_| "test_manifest_format")?;
        if manifest.task_id != "ARCH-AW-005"
            || manifest.revision != "r5"
            || !matches!(manifest.role.as_str(), "dev" | "qa")
            || manifest.owned_marker != "ARCH-AW-005-r5-owned"
            || manifest.source_candidate.len() != 64
            || !manifest
                .source_candidate
                .bytes()
                .all(|b| b.is_ascii_hexdigit())
            || manifest.allowed_ports != [30102, 30103, 30104]
            || manifest.run_id.len() != manifest.role.len() + 5
            || !manifest.run_id.starts_with(&(manifest.role.clone() + "-"))
            || !manifest.run_id[manifest.role.len() + 1..]
                .bytes()
                .all(|b| b.is_ascii_digit())
        {
            return Err("test_manifest_identity".into());
        }
        let profile_root = root.join("profile").join(&manifest.role);
        if !path.starts_with(&profile_root) {
            return Err("test_manifest_role".into());
        }
        if !manifest.profile_dir.is_absolute()
            || !manifest.profile_dir.starts_with(&profile_root)
            || manifest
                .profile_dir
                .components()
                .any(|p| matches!(p, std::path::Component::ParentDir))
        {
            return Err("test_profile_path".into());
        }
        crate::config::profile::resolve(
            &manifest.profile_dir,
            Some(manifest.profile_dir.to_str().ok_or("test_profile_path")?),
        )?;
        if let Some(workspace) = &manifest.workspace {
            let fixtures = Path::new(env!("CARGO_MANIFEST_DIR"))
                .join("../tests/fixtures")
                .canonicalize()
                .map_err(|_| "test_fixture_missing")?;
            let canonical = workspace
                .canonicalize()
                .map_err(|_| "test_fixture_missing")?;
            if workspace.is_symlink()
                || canonical.parent() != Some(fixtures.as_path())
                || !matches!(
                    canonical.file_name().and_then(|s| s.to_str()),
                    Some("protocol-workspace.json" | "product-workspace.json")
                )
            {
                return Err("test_fixture_path".into());
            }
        }
        if manifest
            .scenario
            .as_deref()
            .is_some_and(|s| !matches!(s, "N1" | "N2" | "N3"))
        {
            return Err("test_scenario".into());
        }
        Ok(manifest)
    }
}

pub fn prepare_workspace(app: &App, workspace: Workspace) -> Result<(), String> {
    if workspace
        .instances
        .iter()
        .any(|i| i.host != "127.0.0.1" || ![30102, 30103].contains(&i.port))
    {
        return Err("test_workspace_endpoint".into());
    }
    let current = app.configuration.get()?;
    if !current.workspace.instances.is_empty() || !current.workspace.source_versions.is_empty() {
        return Err("test_workspace_requires_empty_profile".into());
    }
    let instances = workspace.instances.clone();
    app.configuration.save(SaveIntent {
        expected_etag: current.etag,
        workspace,
        confirm_points: vec![],
    })?;
    for instance in &instances {
        for db in &instance.dbs {
            let state = app.configuration.get()?;
            let p = layout::preview(
                &app.configuration,
                LayoutIntent {
                    expected_etag: state.etag,
                    instance_id: instance.id.clone(),
                    db_id: db.id.clone(),
                    method: "manual".into(),
                    reason: "independent synthetic test addresses".into(),
                },
            )?;
            app.configuration
                .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)?;
        }
        let state = app.configuration.get()?;
        let p = naming::preview(
            &app.configuration,
            NamesIntent {
                expected_etag: state.etag,
                instance_id: instance.id.clone(),
                point_ids: instance
                    .dbs
                    .iter()
                    .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
                    .collect(),
                address_only: false,
            },
        )?;
        app.configuration
            .confirm(&p.kind, &p.token, &p.expected_etag, &p.candidate_sha256)?;
    }
    let state = app.configuration.get()?;
    let ids = state
        .workspace
        .instances
        .iter()
        .flat_map(|i| {
            i.dbs
                .iter()
                .flat_map(|d| d.points.iter().map(|p| p.id.clone()))
        })
        .collect();
    let saved = app.configuration.save(SaveIntent {
        expected_etag: state.etag,
        workspace: state.workspace,
        confirm_points: ids,
    })?;
    let revision = saved.revision_id.ok_or("test_revision_missing")?;
    for instance in instances {
        apply_revision(app, &instance.id, &revision)?;
    }
    Ok(())
}

pub fn apply_revision(app: &App, id: &str, revision: &str) -> Result<(), String> {
    let state = app.configuration.get()?;
    let p = apply::preview(
        app,
        ApplyIntent {
            expected_etag: state.etag,
            instance_id: id.into(),
            revision_id: revision.into(),
            retention: "preserve_compatible_hold".into(),
        },
    )?;
    apply::confirm(
        app,
        ApplyConfirmation {
            expected_etag: p.expected_etag,
            instance_id: id.into(),
            token: p.token,
            candidate_sha256: p.candidate_sha256,
            impact_sha256: p.details["impactSha256"]
                .as_str()
                .ok_or("test_impact_missing")?
                .into(),
        },
    )?;
    Ok(())
}

pub fn maintenance(app: &App, id: &str, enabled: bool) -> Result<(), String> {
    let instance = app.instance(id)?;
    if !instance.stopped() {
        return Err("instance_not_stopped".into());
    }
    let mut state = app.configuration.get()?;
    let config = state
        .workspace
        .instances
        .iter_mut()
        .find(|i| i.id == id)
        .ok_or("instance_not_found")?;
    let point = config
        .dbs
        .iter_mut()
        .find(|d| d.number == 41)
        .and_then(|d| d.points.iter_mut().find(|p| p.byte == Some(56)))
        .ok_or("point_not_found")?;
    point.policy.ui_maintenance = Some(enabled);
    let point_id = point.id.clone();
    let saved = app.configuration.save(SaveIntent {
        expected_etag: state.etag,
        workspace: state.workspace,
        confirm_points: vec![point_id],
    })?;
    apply_revision(app, id, &saved.revision_id.ok_or("test_revision_missing")?)
}

/// 固定产品拓扑回归动作：真实保存新revision并停机apply，不接受任意配置或SQL。
pub fn reconfigure(app: &App, id: &str) -> Result<(), String> {
    let mut state = app.configuration.get()?;
    let config = state
        .workspace
        .instances
        .iter_mut()
        .find(|i| i.id == id)
        .ok_or("instance_not_found")?;
    config.name = format!("{} revised", config.name);
    let saved = app.configuration.save(SaveIntent {
        expected_etag: state.etag,
        workspace: state.workspace,
        confirm_points: vec![],
    })?;
    apply_revision(app, id, &saved.revision_id.ok_or("test_revision_missing")?)
}
