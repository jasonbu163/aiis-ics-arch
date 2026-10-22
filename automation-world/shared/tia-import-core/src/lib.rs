//! AIIS无I/O TIA导入核心：有界扫描、显式闭包展开、标准布局及确定技术命名。
pub mod layout;
pub mod model;
pub mod naming;
pub mod parser;
pub use layout::layout_standard;
pub use model::*;
pub use naming::*;
pub const IMPORT_PROFILE: &str = "tia-subset-v1";
pub const LAYOUT_PROFILE: &str = "siemens-step7-v20-standard-word-v1";
use std::collections::{BTreeMap, BTreeSet};
pub fn scan_sources(
    inputs: &[SourceInput],
    _profile: ImportProfile,
) -> Result<SourceCatalog, Vec<Diagnostic>> {
    if inputs.is_empty()
        || inputs.len() > 128
        || inputs.iter().map(|i| i.bytes.len()).sum::<usize>() > 4 * 1024 * 1024
    {
        return Err(vec![diagnostic("source_limits")]);
    }
    let mut ids = BTreeSet::new();
    let mut declarations = vec![];
    for i in inputs {
        if i.bytes.len() > 1024 * 1024 || !ids.insert(i.input_id.clone()) {
            return Err(vec![diagnostic("source_limits")]);
        }
        let content = std::str::from_utf8(&i.bytes).map_err(|_| vec![diagnostic("source_utf8")])?;
        let source = SourceDocument {
            name: i.name.clone(),
            content: content.into(),
        };
        for (index, d) in parser::scan(&source)
            .map_err(|e| {
                vec![Diagnostic {
                    code: e,
                    path: String::new(),
                    line: 0,
                    file: i.name.clone(),
                }]
            })?
            .into_iter()
            .enumerate()
        {
            declarations.push((
                DeclarationRef {
                    input_id: i.input_id.clone(),
                    declaration_index: index,
                },
                d,
            ))
        }
    }
    Ok(SourceCatalog { declarations })
}
pub fn expand_db(
    catalog: &SourceCatalog,
    db: &DeclarationRef,
    udt_closure: &[DeclarationRef],
) -> Result<ExpandedDb, Vec<Diagnostic>> {
    let get = |r: &DeclarationRef| {
        catalog
            .declarations
            .iter()
            .find(|(key, _)| key == r)
            .map(|(_, d)| d)
            .ok_or_else(|| vec![diagnostic("source_identity_conflict")])
    };
    let d = get(db)?;
    if !d.db {
        return Err(vec![diagnostic("source_mapping_invalid")]);
    }
    let block = d.block.as_ref().ok_or_else(|| d.issues.clone())?;
    let mut types = BTreeMap::new();
    let mut seen = BTreeSet::new();
    for r in udt_closure {
        if !seen.insert((r.input_id.clone(), r.declaration_index)) {
            return Err(vec![diagnostic("duplicate_udt")]);
        }
        let t = get(r)?;
        if t.db {
            return Err(vec![diagnostic("source_mapping_invalid")]);
        }
        let b = t.block.as_ref().ok_or_else(|| t.issues.clone())?;
        if types
            .insert(t.name.to_ascii_lowercase(), b.fields.clone())
            .is_some()
        {
            return Err(vec![diagnostic("duplicate_udt")]);
        }
    }
    let tree = parser::expand(
        &block.fields,
        "",
        &types,
        &mut vec![],
        0,
        false,
        &mut vec![],
    )
    .map_err(|e| vec![e])?;
    let leaves = structured_leaves(&tree);
    let mut paths = BTreeSet::new();
    if leaves.is_empty()
        || leaves
            .iter()
            .any(|l| !paths.insert(l.path.to_ascii_lowercase()))
    {
        return Err(vec![diagnostic("source_path_collision")]);
    }
    Ok(ExpandedDb {
        name: d.name.clone(),
        tree,
        leaves,
        standard: block.standard,
    })
}
