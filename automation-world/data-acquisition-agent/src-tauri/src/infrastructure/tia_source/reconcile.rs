//! 显式选择的保全式来源版本/闭包与草稿差异；身份不由文件名或DB数字猜测。
use super::parser::{self, Block, Declaration};
use crate::domain::{
    local_configuration::*,
    local_sample::{digest, encode},
    source_import::*,
};
use std::collections::{BTreeMap, BTreeSet};
fn key(d: &Declaration) -> BlockKey {
    BlockKey {
        kind: if d.db { "DATA_BLOCK" } else { "TYPE" }.into(),
        name: d.name.clone(),
    }
}
fn diagnostic(code: &str, d: &Declaration) -> Issue {
    Issue {
        code: code.split(':').next().unwrap_or(code).into(),
        path: d.name.clone(),
        line: d.line,
        file: d.source.name.clone(),
    }
}
// 展开字段定位保持结构化；普通映射错误仍使用声明定位。
enum ImportFailure {
    Code(String),
    Field(Issue),
}
impl From<String> for ImportFailure {
    fn from(code: String) -> Self {
        Self::Code(code)
    }
}
impl From<&str> for ImportFailure {
    fn from(code: &str) -> Self {
        Self::Code(code.into())
    }
}
impl From<Issue> for ImportFailure {
    fn from(issue: Issue) -> Self {
        Self::Field(issue)
    }
}
impl ImportFailure {
    fn diagnostic(self, d: &Declaration) -> Issue {
        match self {
            Self::Code(code) => diagnostic(&code, d),
            Self::Field(issue) => block_diagnostic(issue, d),
        }
    }
    fn code(self) -> String {
        match self {
            Self::Code(code) => code,
            Self::Field(issue) => issue.code,
        }
    }
}
fn block_diagnostic(mut issue: Issue, d: &Declaration) -> Issue {
    issue.path = if issue.path.is_empty() {
        d.name.clone()
    } else {
        format!("{}.{}", d.name, issue.path)
    };
    issue
}
fn sources(c: &Configuration, r: &ImportRequest) -> LocalResult<Vec<SourceDocument>> {
    if r.sources.is_empty()
        || r.sources.len() > 128
        || r.sources.iter().map(|s| s.content.len()).sum::<usize>() > 4 * 1024 * 1024
    {
        return Err("source_limits".into());
    }
    if r.stage.is_some() && r.raw_proofs.len() != r.sources.len() {
        return Err("source_bytes_required".into());
    }
    let plc = r.target_plc_id.as_deref();
    let mut out = vec![];
    for (i, src) in r.sources.iter().enumerate() {
        if src.content.len() > 1024 * 1024
            || src.name.len() > 255
            || ![".db", ".udt"].iter().any(|x| src.name.ends_with(x))
            || src
                .name
                .starts_with(crate::domain::yaml_migration::PRIVATE_NAME)
        {
            return Err("source_limits".into());
        }
        if !c.plcs.iter().any(|p| p.id == src.plc_id)
            || plc.map(|p| p != src.plc_id).unwrap_or(false)
        {
            return Err("plc_missing".into());
        }
        let h = digest(&src.content);
        if (!src.sha256.is_empty() && src.sha256 != h)
            || r.raw_proofs
                .get(i)
                .map(|p| p.bytes != src.content.len() || p.sha256 != h)
                .unwrap_or(false)
        {
            return Err("source_hash_mismatch".into());
        }
        if !src.id.is_empty()
            && !c.sources.iter().any(|s| {
                s.id == src.id
                    && s.content == src.content
                    && s.sha256 == h
                    && s.plc_id == src.plc_id
                    && s.name == src.name
            })
        {
            return Err("source_identity_conflict".into());
        }
        if src.lineage_id.is_some() {
            return Err("source_identity_conflict".into());
        }
        let mut s = src.clone();
        s.sha256 = h;
        s.diagnostics.clear();
        s.db_number = None;
        s.lineage_id = None;
        out.push(s);
    }
    Ok(out)
}
fn scans(srcs: &[SourceDocument]) -> LocalResult<Vec<Vec<Declaration>>> {
    srcs.iter().map(parser::scan).collect()
}
fn leaf_comment<'a>(nodes: &'a [FieldNode], path: &str) -> Option<&'a str> {
    for n in nodes {
        if n.children.is_empty() && n.path == path {
            return Some(&n.comment);
        }
        if let Some(v) = leaf_comment(&n.children, path) {
            return Some(v);
        }
    }
    None
}
fn semantic(nodes: &[FieldNode]) -> serde_json::Value {
    serde_json::Value::Array(
        nodes
            .iter()
            .map(|n| {
                serde_json::json!([
                    n.name,
                    n.path,
                    n.data_type,
                    n.lower,
                    n.upper,
                    semantic(&n.children)
                ])
            })
            .collect(),
    )
}
fn expand(
    b: &Block,
    types: &BTreeMap<String, Block>,
) -> Result<(Vec<FieldNode>, Vec<(String, String, usize, String)>), ImportFailure> {
    let mut ps = vec![];
    let fs = types
        .iter()
        .map(|(k, b)| (k.clone(), b.fields.clone()))
        .collect();
    let tree = parser::expand(&b.fields, "", &fs, &mut vec![], 0, false, &mut ps)?;
    let mut paths = BTreeSet::new();
    if ps.is_empty() || ps.iter().any(|p| !paths.insert(p.0.to_ascii_lowercase())) {
        return Err("source_path_collision".into());
    }
    Ok((tree, ps))
}
// Reprove original immutable source, complete structure and exact block/number relation.
pub(crate) fn verify_db(c: &Configuration, db: &Db) -> LocalResult<()> {
    let src = c
        .sources
        .iter()
        .find(|s| s.id == db.source_id && s.plc_id == db.plc_id)
        .ok_or("source_identity_conflict")?;
    if src.sha256 != digest(&src.content) || !db.complete {
        return Err("incomplete_source".into());
    }
    let ds = parser::scan(src)?;
    let candidates: Vec<_> = ds.iter().filter(|d| d.db).collect();
    let b = if let Some(binding) = &db.import_binding {
        if binding.block_key.kind != "DATA_BLOCK"
            || binding.block_key.name != db.name
            || binding.lineage_id != src.lineage_id.as_deref().unwrap_or(&src.id)
        {
            return Err("source_identity_conflict".into());
        }
        let found: Vec<_> = candidates
            .into_iter()
            .filter(|d| d.name == binding.block_key.name)
            .collect();
        if found.len() != 1 {
            return Err("source_identity_conflict".into());
        }
        found[0]
    } else {
        if candidates.len() != 1
            || candidates[0].name != db.name
            || src.db_number != Some(db.number)
        {
            return Err("source_identity_conflict".into());
        }
        candidates[0]
    };
    let block = b.block.as_ref().ok_or("incomplete_source")?;
    if !block.standard {
        return Err("optimized_access_unknown".into());
    }
    let mut types = BTreeMap::new();
    for s in c.sources.iter().filter(|s| {
        s.plc_id == db.plc_id
            && match &db.import_binding {
                Some(v) => v.udt_source_ids.contains(&s.id),
                None => s.name.ends_with(".udt") || s.id == src.id,
            }
    }) {
        if digest(&s.content) != s.sha256 {
            return Err("source_hash_mismatch".into());
        }
        for d in parser::scan(s)? {
            if !d.db {
                let b = d.block.ok_or("incomplete_source")?;
                if types.insert(d.name.to_ascii_lowercase(), b).is_some() {
                    return Err("duplicate_udt".into());
                }
            }
        }
    }
    let (tree, ps) = expand(block, &types).map_err(ImportFailure::code)?;
    if semantic(&tree) != semantic(&db.tree) {
        return Err("source_derived_conflict".into());
    }
    let old: Vec<_> = c.points.iter().filter(|p| p.db_id == db.id).collect();
    if old.len() != ps.len()
        || ps.iter().any(|(p, t, _, _)| {
            old.iter()
                .filter(|v| v.source_path == *p && v.data_type == *t && v.plc_id == db.plc_id)
                .count()
                != 1
        })
    {
        return Err("point_source_mismatch".into());
    }
    Ok(())
}
fn suggestion<'a>(c: &'a Configuration, src: &SourceDocument, d: &Declaration) -> Option<&'a Db> {
    let found: Vec<_> = c
        .dbs
        .iter()
        .filter(|db| {
            db.plc_id == src.plc_id
                && db.name == d.name
                && c.sources.iter().any(|s| {
                    s.id == db.source_id
                        && s.name == src.name
                        && s.sha256 == src.sha256
                        && s.content == src.content
                })
                && verify_db(c, db).is_ok()
        })
        .collect();
    if found.len() == 1 {
        Some(found[0])
    } else {
        None
    }
}
fn new_types(ds: &[Vec<Declaration>]) -> LocalResult<BTreeMap<String, Block>> {
    let mut types = BTreeMap::new();
    for d in ds.iter().flatten().filter(|d| !d.db) {
        if let Some(b) = &d.block {
            if types
                .insert(d.name.to_ascii_lowercase(), b.clone())
                .is_some()
            {
                return Err("duplicate_udt".into());
            }
        }
    }
    Ok(types)
}
pub(crate) fn identify(c: &Configuration, r: &ImportRequest) -> LocalResult<Identification> {
    let ss = sources(c, r)?;
    let ds = scans(&ss)?;
    let types = new_types(&ds);
    let mut blocks = vec![];
    let mut db_count = 0;
    let mut udt_count = 0;
    for (i, items) in ds.iter().enumerate() {
        for d in items {
            if d.db {
                db_count += 1
            } else {
                udt_count += 1
            }
            let mut issues = d.issues.clone();
            let mut count = 0;
            if d.db {
                if let Some(b) = &d.block {
                    match types
                        .as_ref()
                        .map_err(|e| ImportFailure::Code(e.clone()))
                        .and_then(|t| expand(b, t))
                    {
                        Ok((_, ps)) => count = ps.len(),
                        Err(e) => issues.push(e.diagnostic(d)),
                    }
                }
            }
            let old = if d.db { suggestion(c, &ss[i], d) } else { None };
            blocks.push(IdentifiedBlock {
                source_index: i,
                block_key: key(d),
                file: ss[i].name.clone(),
                line: d.line,
                leaf_count: count,
                issues,
                suggested_db_number: old.map(|v| v.number),
                target_id: old.map(|v| v.id.clone()),
            });
        }
    }
    Ok(Identification {
        blocks,
        file_count: ss.len(),
        db_count,
        udt_count,
    })
}
fn version(c: &Configuration, src: &SourceDocument, lineage: Option<&str>) -> SourceDocument {
    if let Some(s) = c.sources.iter().find(|s| {
        s.plc_id == src.plc_id
            && s.name == src.name
            && s.sha256 == src.sha256
            && s.content == src.content
            && lineage
                .map(|l| l == s.lineage_id.as_deref().unwrap_or(&s.id))
                .unwrap_or(true)
    }) {
        return s.clone();
    }
    let mut s = src.clone();
    s.id = id();
    s.lineage_id = Some(lineage.map(str::to_owned).unwrap_or_else(|| s.id.clone()));
    s.db_number = None;
    s
}
fn closure(
    b: &Block,
    types: &BTreeMap<String, Block>,
    visiting: &mut BTreeSet<String>,
    done: &mut BTreeSet<String>,
    out: &mut Vec<SourceDocument>,
) -> LocalResult<()> {
    let mut refs = BTreeSet::new();
    parser::referenced(&b.fields, &mut refs);
    for name in refs {
        if done.contains(&name) {
            continue;
        }
        if !visiting.insert(name.clone()) {
            return Err("udt_cycle".into());
        }
        let t = types.get(&name).ok_or("udt_missing")?;
        closure(t, types, visiting, done, out)?;
        visiting.remove(&name);
        done.insert(name);
        if !out.iter().any(|s| s.id == t.source.id) {
            out.push(t.source.clone());
        }
    }
    Ok(())
}
fn old_types(c: &Configuration, old: Option<&Db>) -> LocalResult<BTreeMap<String, Block>> {
    let mut out = BTreeMap::new();
    if let Some(db) = old {
        for s in c.sources.iter().filter(|s| {
            s.plc_id == db.plc_id
                && db
                    .import_binding
                    .as_ref()
                    .map(|b| b.udt_source_ids.contains(&s.id))
                    .unwrap_or(s.name.ends_with(".udt"))
        }) {
            for d in parser::scan(s)?.into_iter().filter(|d| !d.db) {
                let b = d.block.ok_or("incomplete_source")?;
                if out.insert(d.name.to_ascii_lowercase(), b).is_some() {
                    return Err("duplicate_udt".into());
                }
            }
        }
    }
    Ok(out)
}
pub(crate) fn plan(c: &Configuration, r: &ImportRequest) -> LocalResult<ImportPreview> {
    let ss = sources(c, r)?;
    let ds = scans(&ss)?;
    if r.mappings.len() > 128 {
        return Err("source_limits".into());
    }
    let mut next = c.clone();
    let mut renamed = BTreeSet::new();
    let mut issues = vec![];
    let mut deltas = vec![];
    let mut changes = vec![];
    let mut selected = BTreeSet::new();
    let mut numbers = BTreeSet::new();
    let mut targets = BTreeSet::new();
    let mut source_lineages: BTreeMap<usize, String> = BTreeMap::new();
    for m in r.mappings.iter().filter(|m| m.selected) {
        if let Some(target) = &m.target_id {
            if let Some(db) = c.dbs.iter().find(|d| d.id == *target) {
                if let Some(src) = c.sources.iter().find(|s| s.id == db.source_id) {
                    let lineage = src.lineage_id.as_deref().unwrap_or(&src.id);
                    if source_lineages
                        .get(&m.source_index)
                        .map(|s| s != lineage)
                        .unwrap_or(false)
                    {
                        return Err("source_identity_conflict".into());
                    }
                    source_lineages.insert(m.source_index, lineage.into());
                }
            }
        }
    }
    for m in r.mappings.iter().filter(|m| m.selected) {
        let d = ds
            .get(m.source_index)
            .and_then(|v| v.iter().find(|d| key(d) == m.block_key && d.db))
            .ok_or("source_mapping_invalid")?;
        if d.block.is_none() {
            issues.extend(d.issues.clone());
            continue;
        }
        if !selected.insert((m.source_index, d.name.clone())) {
            return Err("source_mapping_duplicate".into());
        }
        let result = (|| -> Result<(), ImportFailure> {
            if ds
                .iter()
                .flatten()
                .filter(|x| x.db && x.name.eq_ignore_ascii_case(&d.name))
                .count()
                != 1
            {
                return Err("duplicate_db_declaration".into());
            }
            let number = m.db_number.filter(|n| *n > 0).ok_or("db_number_required")?;
            if !numbers.insert((d.source.plc_id.clone(), number)) {
                return Err("duplicate_db_number".into());
            }
            let old = if let Some(target) = &m.target_id {
                let db = c
                    .dbs
                    .iter()
                    .find(|db| db.id == *target && db.plc_id == d.source.plc_id)
                    .ok_or("source_identity_conflict")?;
                verify_db(c, db)?;
                if db.name != d.name {
                    return Err("block_rename_blocked".into());
                }
                if db.number != number {
                    return Err("db_renumber_blocked".into());
                }
                if !targets.insert(db.id.clone()) {
                    return Err("source_mapping_duplicate".into());
                }
                Some(db)
            } else {
                None
            };
            if c.dbs.iter().any(|db| {
                db.plc_id == d.source.plc_id
                    && db.number == number
                    && old.map(|o| o.id != db.id).unwrap_or(true)
            }) {
                return Err("db_number_occupied".into());
            }
            // A known name from the same explicit logical source cannot be silently cloned/renamed.
            if old.is_none() && suggestion(c, &ss[m.source_index], d).is_some() {
                return Err("source_target_required".into());
            }
            let b = d.block.as_ref().ok_or_else(|| {
                d.issues
                    .first()
                    .map(|i| i.code.clone())
                    .unwrap_or("incomplete_source".into())
            })?;
            let lineage = source_lineages.get(&m.source_index).map(String::as_str);

            let src = version(&next, &ss[m.source_index], lineage);
            // Each target gets only its frozen old dependency closure plus explicitly selected new definitions.
            let mut types = old_types(c, old)?;
            for definition in ds.iter().flatten().filter(|d| !d.db && d.block.is_none()) {
                types.remove(&definition.name.to_ascii_lowercase());
            }
            let incoming = new_types(&ds)?;
            // 同一待导入文档的多个TYPE共用一个具体版本，闭包仍只保存实际依赖。
            let mut planned_versions: Vec<SourceDocument> = vec![];
            for (name, mut tb) in incoming {
                let previous = types
                    .get(&name)
                    .map(|b| b.source.lineage_id.as_deref().unwrap_or(&b.source.id));
                tb.source = if tb.source.plc_id == src.plc_id
                    && tb.source.name == src.name
                    && tb.source.sha256 == src.sha256
                    && tb.source.content == src.content
                {
                    src.clone()
                } else if let Some(version) = planned_versions.iter().find(|s| {
                    s.plc_id == tb.source.plc_id
                        && s.name == tb.source.name
                        && s.sha256 == tb.source.sha256
                        && s.content == tb.source.content
                        && previous
                            .map(|l| l == s.lineage_id.as_deref().unwrap_or(&s.id))
                            .unwrap_or(true)
                }) {
                    version.clone()
                } else {
                    version(&next, &tb.source, previous)
                };
                if !planned_versions.iter().any(|s| s.id == tb.source.id) {
                    planned_versions.push(tb.source.clone());
                }
                types.insert(name, tb);
            }
            let (tree, ps) = expand(b, &types)?;
            let mut dependencies = vec![];
            closure(
                b,
                &types,
                &mut BTreeSet::new(),
                &mut BTreeSet::new(),
                &mut dependencies,
            )?;
            let db_id = old.map(|d| d.id.clone()).unwrap_or_else(id);
            let oldps: Vec<_> = c.points.iter().filter(|p| p.db_id == db_id).collect();
            let removed: Vec<_> = oldps
                .iter()
                .filter(|p| !ps.iter().any(|v| v.0 == p.source_path))
                .map(|p| p.source_path.clone())
                .collect();
            if !removed.is_empty() {
                issues.extend(removed.iter().map(|p| Issue {
                    code: "leaf_removal_blocked".into(),
                    path: p.clone(),
                    file: d.source.name.clone(),
                    line: d.line,
                }));
                return Err("leaf_removal_blocked".into());
            }
            let layout_changed = old
                .map(|d| semantic(&d.tree) != semantic(&tree))
                .unwrap_or(false);
            let mut delta = DbDelta {
                db_id: db_id.clone(),
                block_name: d.name.clone(),
                number,
                status: if old.is_some() { "updated" } else { "added" }.into(),
                added_paths: vec![],
                type_changed_paths: vec![],
                removed_paths: removed,
                layout_changed,
                comments_changed: false,
                preserved_points: oldps.len(),
                preserved_manual: oldps
                    .iter()
                    .filter(|p| {
                        p.address
                            .as_ref()
                            .map(|a| a.origin == "manual")
                            .unwrap_or(false)
                    })
                    .count(),
                invalidated_confirmations: 0,
                isolated_udt_versions: old.is_some()
                    && !dependencies.is_empty()
                    && c.dbs
                        .iter()
                        .any(|d| d.id != db_id && d.plc_id == b.source.plc_id),
            };
            for (path, typ, _, comment) in ps {
                if let Some(p) = next
                    .points
                    .iter_mut()
                    .find(|p| p.db_id == db_id && p.source_path == path)
                {
                    if p.data_type != typ {
                        delta.type_changed_paths.push(path.clone());
                    }
                    let prior_source_comment = old.and_then(|d| leaf_comment(&d.tree, &path));
                    if prior_source_comment != Some(comment.as_str()) {
                        delta.comments_changed = true;
                    }
                    if p.name_mode.is_some()
                        && !matches!(
                            p.name_mode,
                            Some(crate::domain::point_naming::NameMode::Manual)
                        )
                        && (p.data_type != typ
                            || (layout_changed
                                && matches!(
                                    p.name_mode,
                                    Some(crate::domain::point_naming::NameMode::AutoAddress)
                                        | Some(crate::domain::point_naming::NameMode::Pending)
                                )))
                    {
                        renamed.insert(p.id.clone());
                    }
                    p.data_type = typ;
                    if prior_source_comment == Some(p.comment.as_str()) {
                        p.comment = comment;
                    }
                    if layout_changed {
                        if let Some(a) = &mut p.address {
                            if a.confirmed {
                                delta.invalidated_confirmations += 1;
                            }
                            a.confirmed = false;
                        }
                    }
                } else {
                    delta.added_paths.push(path.clone());
                    let point_id = id();
                    renamed.insert(point_id.clone());
                    next.points.push(Point {
                        name_mode: Some(crate::domain::point_naming::NameMode::Pending),
                        id: point_id,
                        plc_id: b.source.plc_id.clone(),
                        db_id: db_id.clone(),
                        source_path: path.clone(),
                        name: String::new(),
                        data_type: typ,
                        comment,
                        enabled: false,
                        group_id: None,
                        address: None,
                    });
                }
            }
            let mut depids: Vec<_> = dependencies.iter().map(|s| s.id.clone()).collect();
            depids.sort();
            depids.dedup();
            let db = Db {
                id: db_id.clone(),
                plc_id: src.plc_id.clone(),
                source_id: src.id.clone(),
                name: d.name.clone(),
                number,
                length: old.map(|d| d.length).unwrap_or(65536),
                complete: true,
                flat: tree
                    .iter()
                    .all(|n| n.children.is_empty() && !n.data_type.starts_with("STRING[")),
                tree,
                import_binding: Some(ImportBinding {
                    block_key: key(d),
                    lineage_id: src.lineage_id.as_deref().unwrap_or(&src.id).into(),
                    udt_source_ids: depids,
                }),
            };
            if let Some(existing) = next.dbs.iter_mut().find(|d| d.id == db_id) {
                *existing = db;
            } else {
                next.dbs.push(db);
            }
            for source in std::iter::once(src).chain(dependencies) {
                if !next.sources.iter().any(|s| s.id == source.id) {
                    next.sources.push(source);
                }
            }
            changes.push(format!(
                "{}:{}",
                if layout_changed {
                    "structure_changed"
                } else {
                    &delta.status
                },
                db_id
            ));
            deltas.push(delta);
            Ok(())
        })();
        if let Err(e) = result {
            issues.push(e.diagnostic(d));
        }
    }
    if !r.mappings.iter().any(|m| m.selected) {
        return Err("source_selection_required".into());
    }
    if next.sources.len() > 128
        || next.plcs.iter().any(|p| {
            next.dbs.iter().filter(|d| d.plc_id == p.id).count() > 32
                || next.points.iter().filter(|d| d.plc_id == p.id).count() > 4096
        })
        || encode(&next)?.len() > 16 * 1024 * 1024
    {
        issues.push(issue("configuration_limits", ""));
    }
    let proven = next
        .dbs
        .iter()
        .filter(|d| verify_db(&next, d).is_ok())
        .map(|d| d.id.clone())
        .collect();
    if let Err(es) =
        crate::domain::point_naming::generated(&mut next, &renamed, &proven, None, true)
    {
        issues.extend(es)
    }
    // Existing activation/readiness issues remain advisory. Structural/identity limits are fatal.
    for i in validate(&next) {
        if [
            "configuration_limits",
            "plc_limits",
            "source_invalid",
            "db_invalid",
            "duplicate_or_invalid_id",
            "point_invalid",
        ]
        .contains(&i.code.as_str())
        {
            issues.push(i);
        }
    }
    let name_changes = next
        .points
        .iter()
        .filter(|p| renamed.contains(&p.id))
        .map(|p| {
            let mut empty = p.clone();
            empty.name = String::new();
            empty.name_mode = None;
            crate::domain::point_naming::change(
                c.points.iter().find(|old| old.id == p.id).unwrap_or(&empty),
                p,
                if p.name_mode == Some(crate::domain::point_naming::NameMode::Pending) {
                    "address_required"
                } else {
                    "path"
                },
            )
        })
        .collect();
    let readiness = validate(&next);
    let can_confirm = issues.is_empty();
    if !can_confirm {
        next = c.clone();
    }
    let unchanged = can_confirm && next == *c;
    Ok(ImportPreview {
        configuration: next,
        changes,
        issues,
        readiness,
        deltas,
        name_changes,
        can_confirm,
        unchanged,
        preview_token: None,
        input_digest: String::new(),
        etag: r.expected_etag.clone(),
    })
}
pub(crate) fn legacy_import(
    c: &Configuration,
    sources: Vec<SourceDocument>,
) -> LocalResult<ImportPreview> {
    let mut r = ImportRequest {
        sources,
        expected_etag: String::new(),
        confirm: false,
        stage: None,
        target_plc_id: None,
        mappings: vec![],
        preview_token: None,
        raw_proofs: vec![],
    };
    let ident = identify(c, &r)?;
    for (i, s) in r.sources.iter().enumerate() {
        let dbs: Vec<_> = ident
            .blocks
            .iter()
            .filter(|d| d.source_index == i && d.block_key.kind == "DATA_BLOCK")
            .collect();
        if dbs.len() > 1 {
            return Err("multi_db_mapping_required".into());
        }
        for b in dbs {
            r.mappings.push(BlockMapping {
                source_index: i,
                block_key: b.block_key.clone(),
                selected: true,
                db_number: s.db_number,
                target_id: b.target_id.clone(),
            });
        }
    }
    plan(c, &r)
}
