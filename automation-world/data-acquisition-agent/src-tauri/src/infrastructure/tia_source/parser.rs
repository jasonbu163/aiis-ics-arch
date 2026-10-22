//! 共享TIA纯解析的薄适配；DAA来源身份与不可变版本保持本地，不复制算法。
use crate::domain::local_configuration::*;
use aiis_tia_import_core as core;
pub(super) use core::parser::Field;
use std::collections::{BTreeMap, BTreeSet};
#[derive(Clone)]
pub(super) struct Block {
    pub fields: Vec<Field>,
    pub source: SourceDocument,
    pub standard: bool,
}
#[derive(Clone)]
pub(super) struct Declaration {
    pub source: SourceDocument,
    pub name: String,
    pub db: bool,
    pub line: usize,
    pub block: Option<Block>,
    pub issues: Vec<Issue>,
}
pub(crate) fn tree_from_core(nodes: &[core::FieldNode]) -> Vec<FieldNode> {
    nodes
        .iter()
        .map(|n| FieldNode {
            name: n.name.clone(),
            path: n.path.clone(),
            data_type: n.data_type.clone(),
            line: n.line,
            comment: n.comment.clone(),
            lower: n.lower,
            upper: n.upper,
            children: tree_from_core(&n.children),
        })
        .collect()
}
pub(crate) fn tree_to_core(nodes: &[FieldNode]) -> Vec<core::FieldNode> {
    nodes
        .iter()
        .map(|n| core::FieldNode {
            name: n.name.clone(),
            path: n.path.clone(),
            data_type: n.data_type.clone(),
            line: n.line,
            comment: n.comment.clone(),
            lower: n.lower,
            upper: n.upper,
            children: tree_to_core(&n.children),
        })
        .collect()
}
fn issue(i: core::Diagnostic) -> Issue {
    Issue {
        code: i.code,
        path: i.path,
        line: i.line,
        file: i.file,
    }
}
pub(super) fn scan(src: &SourceDocument) -> LocalResult<Vec<Declaration>> {
    core::parser::scan(&core::SourceDocument {
        name: src.name.clone(),
        content: src.content.clone(),
    })
    .map(|ds| {
        ds.into_iter()
            .map(|d| Declaration {
                source: src.clone(),
                name: d.name,
                db: d.db,
                line: d.line,
                block: d.block.map(|b| Block {
                    fields: b.fields,
                    source: src.clone(),
                    standard: b.standard,
                }),
                issues: d.issues.into_iter().map(issue).collect(),
            })
            .collect()
    })
}
pub(super) fn expand(
    fields: &[Field],
    prefix: &str,
    udts: &BTreeMap<String, Vec<Field>>,
    stack: &mut Vec<String>,
    depth: usize,
    in_array: bool,
    leaves: &mut Vec<(String, String, usize, String)>,
) -> Result<Vec<FieldNode>, Issue> {
    core::parser::expand(fields, prefix, udts, stack, depth, in_array, leaves)
        .map(|v| tree_from_core(&v))
        .map_err(issue)
}
pub(super) fn referenced(fields: &[Field], names: &mut BTreeSet<String>) {
    core::parser::referenced(fields, names)
}
