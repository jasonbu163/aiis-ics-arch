//! 不可变来源/完整声明树DTO；结构化段独立保存，不拆点路径字符串还原身份。
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", content = "value", rename_all = "snake_case")]
pub enum PathSegment {
    Field(String),
    Index(i32),
}
impl From<&aiis_tia_import_core::PathSegment> for PathSegment {
    fn from(value: &aiis_tia_import_core::PathSegment) -> Self {
        match value {
            aiis_tia_import_core::PathSegment::Field(x) => Self::Field(x.clone()),
            aiis_tia_import_core::PathSegment::Index(x) => Self::Index(*x),
        }
    }
}
impl From<&PathSegment> for aiis_tia_import_core::PathSegment {
    fn from(value: &PathSegment) -> Self {
        match value {
            PathSegment::Field(x) => Self::Field(x.clone()),
            PathSegment::Index(x) => Self::Index(*x),
        }
    }
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct FieldNode {
    pub name: String,
    pub path: String,
    pub data_type: String,
    pub line: usize,
    pub comment: String,
    pub lower: Option<i32>,
    pub upper: Option<i32>,
    pub children: Vec<FieldNode>,
}
impl From<&aiis_tia_import_core::FieldNode> for FieldNode {
    fn from(n: &aiis_tia_import_core::FieldNode) -> Self {
        Self {
            name: n.name.clone(),
            path: n.path.clone(),
            data_type: n.data_type.clone(),
            line: n.line,
            comment: n.comment.clone(),
            lower: n.lower,
            upper: n.upper,
            children: n.children.iter().map(Self::from).collect(),
        }
    }
}
impl From<&FieldNode> for aiis_tia_import_core::FieldNode {
    fn from(n: &FieldNode) -> Self {
        Self {
            name: n.name.clone(),
            path: n.path.clone(),
            data_type: n.data_type.clone(),
            line: n.line,
            comment: n.comment.clone(),
            lower: n.lower,
            upper: n.upper,
            children: n.children.iter().map(Self::from).collect(),
        }
    }
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SourceVersion {
    pub version_id: String,
    pub lineage_id: String,
    pub blob_sha256: String,
    pub logical_name: String,
    pub import_profile: String,
    pub bytes: Vec<u8>,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct BoundDeclaration {
    pub version_id: String,
    pub declaration_index: usize,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SourceBinding {
    pub declaration: BoundDeclaration,
    pub udt_closure: Vec<BoundDeclaration>,
    pub standard: bool,
    pub tree: Vec<FieldNode>,
    pub structure_sha256: String,
}
