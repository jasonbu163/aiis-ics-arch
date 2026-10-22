//! 原字节多文件扫描/显式声明闭包/结构化身份继承；BEGIN及:=初值一律不消费。
use super::configuration::{Configuration, Preview};
use crate::domain::{configuration::*, source::*};
use aiis_tia_import_core as core;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ImportFile {
    pub input_id: String,
    pub name: String,
    pub bytes: Vec<u8>,
    pub lineage_id: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Declaration {
    pub input_id: String,
    pub declaration_index: usize,
}
impl Declaration {
    fn core(&self) -> core::DeclarationRef {
        core::DeclarationRef {
            input_id: self.input_id.clone(),
            declaration_index: self.declaration_index,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct BindingIntent {
    pub db_id: Option<String>,
    pub number: u16,
    pub declaration: Declaration,
    #[serde(default)]
    pub udt_closure: Vec<Declaration>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ImportIntent {
    pub expected_etag: String,
    pub instance_id: String,
    pub files: Vec<ImportFile>,
    pub bindings: Vec<BindingIntent>,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ImportPreview {
    pub declarations: Vec<Value>,
    pub preview: Option<Preview>,
    pub initializer_notice: bool,
}
fn diagnostic(e: Vec<core::Diagnostic>) -> String {
    e.first()
        .map(|e| e.code.clone())
        .unwrap_or("source_invalid".into())
}
pub fn preview(service: &Configuration, intent: ImportIntent) -> Result<ImportPreview, String> {
    let mut state = service.get()?;
    if state.etag != intent.expected_etag {
        return Err(format!("etag_conflict:{}", state.etag));
    }
    if !state
        .workspace
        .instances
        .iter()
        .any(|i| i.id == intent.instance_id)
    {
        return Err("instance_not_found".into());
    }
    if intent.files.iter().any(|f| {
        f.name.len() > 100
            || f.name.is_empty()
            || f.name.contains('/')
            || f.name.contains('\\')
            || !["db", "udt"]
                .iter()
                .any(|ext| f.name.to_lowercase().ends_with(&format!(".{ext}")))
    }) {
        return Err("source_filename".into());
    }
    let inputs = intent
        .files
        .iter()
        .map(|f| core::SourceInput {
            input_id: f.input_id.clone(),
            name: f.name.clone(),
            bytes: f.bytes.clone(),
        })
        .collect::<Vec<_>>();
    // 每一预览批次只扫描一次，声明索引只在本catalog内使用。
    let catalog =
        core::scan_sources(&inputs, core::ImportProfile::TiaSubsetV1).map_err(diagnostic)?;
    let declarations=catalog.declarations.iter().map(|(r,d)|json!({"inputId":r.input_id,"declarationIndex":r.declaration_index,"name":d.name,"db":d.db,"issues":d.issues.iter().map(|e|e.code.clone()).collect::<Vec<_>>()})).collect();
    if intent.bindings.is_empty() {
        return Ok(ImportPreview {
            declarations,
            preview: None,
            initializer_notice: true,
        });
    }
    if intent.bindings.len() > 32 {
        return Err("db_capacity".into());
    }
    let mut versions = BTreeMap::new();
    for file in &intent.files {
        let hash = hash_bytes(&file.bytes);
        let lineage = match &file.lineage_id {
            Some(id) => {
                if uuid::Uuid::parse_str(id).is_err()
                    || !state
                        .workspace
                        .source_versions
                        .iter()
                        .any(|s| s.lineage_id == *id)
                {
                    return Err("source_lineage_selection".into());
                }
                id.clone()
            }
            None => uuid(),
        };
        let version = state
            .workspace
            .source_versions
            .iter()
            .find(|s| {
                s.lineage_id == lineage && s.blob_sha256 == hash && s.logical_name == file.name
            })
            .cloned()
            .unwrap_or_else(|| SourceVersion {
                version_id: uuid(),
                lineage_id: lineage,
                blob_sha256: hash,
                logical_name: file.name.clone(),
                import_profile: core::IMPORT_PROFILE.into(),
                bytes: file.bytes.clone(),
            });
        versions.insert(file.input_id.clone(), version);
    }
    let i = state
        .workspace
        .instances
        .iter_mut()
        .find(|i| i.id == intent.instance_id)
        .unwrap();
    let mut selected = BTreeSet::new();
    let mut changes = vec![];
    for binding in &intent.bindings {
        if binding.number == 0 {
            return Err("db_parameters".into());
        }
        let expanded = core::expand_db(
            &catalog,
            &binding.declaration.core(),
            &binding
                .udt_closure
                .iter()
                .map(Declaration::core)
                .collect::<Vec<_>>(),
        )
        .map_err(diagnostic)?;
        let reference = |r: &Declaration| -> Result<BoundDeclaration, String> {
            Ok(BoundDeclaration {
                version_id: versions
                    .get(&r.input_id)
                    .ok_or("source_mapping_invalid")?
                    .version_id
                    .clone(),
                declaration_index: r.declaration_index,
            })
        };
        let source = SourceBinding {
            declaration: reference(&binding.declaration)?,
            udt_closure: binding
                .udt_closure
                .iter()
                .map(reference)
                .collect::<Result<_, _>>()?,
            standard: expanded.standard,
            tree: expanded.tree.iter().map(FieldNode::from).collect(),
            structure_sha256: digest(
                &expanded
                    .tree
                    .iter()
                    .map(FieldNode::from)
                    .collect::<Vec<_>>(),
            ),
        };
        let old = match &binding.db_id {
            Some(id) => Some(
                i.dbs
                    .iter()
                    .find(|d| d.id == *id)
                    .cloned()
                    .ok_or("db_not_found")?,
            ),
            None => None,
        };
        let id = old.as_ref().map(|d| d.id.clone()).unwrap_or_else(uuid);
        if !selected.insert(id.clone()) {
            return Err("db_selection_duplicate".into());
        }
        if old
            .as_ref()
            .is_some_and(|d| d.number == binding.number && d.binding.as_ref() == Some(&source))
        {
            changes.push(json!({"dbId":id,"result":"unchanged"}));
            continue;
        }
        changes.push(json!({"dbId":id,"result":if old.is_some(){"updated_db"}else{"added_db"},"dbNumberBefore":old.as_ref().map(|d|d.number),"dbNumberAfter":binding.number,"nameBefore":old.as_ref().map(|d|d.name.clone()),"nameAfter":expanded.name,"lengthBefore":old.as_ref().map(|d|d.length),"lengthAfter":old.as_ref().map(|d|d.length).unwrap_or(1)}));
        let mut points = vec![];
        for leaf in &expanded.leaves {
            let segments = leaf
                .segments
                .iter()
                .map(PathSegment::from)
                .collect::<Vec<_>>();
            let previous = old
                .as_ref()
                .and_then(|d| d.points.iter().find(|p| p.segments == segments));
            let mut point = previous.cloned().unwrap_or_else(|| PointConfig {
                id: uuid(),
                name: String::new(),
                display_name: leaf.comment.clone(),
                data_type: leaf.data_type.clone(),
                enabled: true,
                source_path: leaf.path.clone(),
                segments: segments.clone(),
                byte: None,
                bit: None,
                manual_reason: String::new(),
                manual: false,
                policy: Default::default(),
                confirmations: Default::default(),
            });
            if point.data_type != leaf.data_type {
                point.confirmations = Default::default();
                point.byte = None;
                point.bit = None;
            }
            point.data_type = leaf.data_type.clone();
            point.source_path = leaf.path.clone();
            point.segments = segments;
            changes.push(json!({"dbId":id,"pointId":point.id,"path":point.source_path,"result":if previous.is_some(){"retained_identity"}else{"added"},"typeChanged":previous.is_some_and(|p|p.data_type!=point.data_type),"typeBefore":previous.map(|p|p.data_type.clone()),"typeAfter":point.data_type,"byteBefore":previous.and_then(|p|p.byte),"bitBefore":previous.and_then(|p|p.bit),"byteAfter":point.byte,"bitAfter":point.bit}));
            points.push(point);
        }
        if let Some(old) = &old {
            for deleted in old
                .points
                .iter()
                .filter(|p| !points.iter().any(|n| n.id == p.id))
            {
                changes.push(json!({"dbId":id,"pointId":deleted.id,"path":deleted.source_path,"result":"deleted"}));
            }
        }
        let db = DbConfig {
            id: id.clone(),
            name: expanded.name,
            number: binding.number,
            length: old.as_ref().map(|d| d.length).unwrap_or(1),
            enabled: old.as_ref().is_none_or(|d| d.enabled),
            manual: false,
            binding: Some(source),
            points,
            policy: old.as_ref().map(|d| d.policy.clone()).unwrap_or_default(),
            regions: old.as_ref().map(|d| d.regions.clone()).unwrap_or_default(),
            address_confirmation: None,
        };
        if let Some(at) = i.dbs.iter().position(|d| d.id == id) {
            i.dbs[at] = db
        } else {
            i.dbs.push(db)
        }
        i.names_confirmation = None;
    }
    let used: BTreeSet<_> = i
        .dbs
        .iter()
        .filter_map(|d| d.binding.as_ref())
        .flat_map(|b| std::iter::once(&b.declaration).chain(&b.udt_closure))
        .map(|r| r.version_id.clone())
        .collect();
    for version in versions
        .into_values()
        .filter(|v| used.contains(&v.version_id))
    {
        if !state
            .workspace
            .source_versions
            .iter()
            .any(|v| v.version_id == version.version_id)
        {
            state.workspace.source_versions.push(version)
        }
    }
    let result = service.preview(
        "import",
        &intent.expected_etag,
        state.workspace,
        json!({"changes":changes,"initializersImported":false,"notice":"tia_initializers_ignored"}),
    )?;
    Ok(ImportPreview {
        declarations,
        preview: Some(result),
        initializer_notice: true,
    })
}
