//! 基于已扫描AST解析UDT依赖：唯一匹配自动闭包，重名保留显式选择，缺失/循环提供字段定位。
use crate::{
    diagnostic,
    parser::{Field, Type},
    DeclarationRef, Diagnostic, SourceCatalog,
};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
pub struct UdtDependencyIssue {
    pub diagnostic: Diagnostic,
    pub type_name: String,
    pub candidates: Vec<DeclarationRef>,
}
#[derive(Clone, Debug, Default)]
pub struct UdtDependencyPlan {
    pub closure: Vec<DeclarationRef>,
    pub issues: Vec<UdtDependencyIssue>,
}

pub fn resolve_udt_dependencies(
    catalog: &SourceCatalog,
    db: &DeclarationRef,
    choices: &[DeclarationRef],
) -> Result<UdtDependencyPlan, Vec<Diagnostic>> {
    let get = |r: &DeclarationRef| {
        catalog
            .declarations
            .iter()
            .find(|(key, _)| key == r)
            .map(|(_, d)| d)
            .ok_or_else(|| vec![diagnostic("source_identity_conflict")])
    };
    let block = get(db)?;
    if !block.db {
        return Err(vec![diagnostic("source_mapping_invalid")]);
    }
    let block = block.block.as_ref().ok_or_else(|| block.issues.clone())?;
    let mut overrides = BTreeMap::new();
    for r in choices {
        let d = get(r)?;
        if d.db {
            return Err(vec![diagnostic("source_mapping_invalid")]);
        }
        if overrides
            .insert(d.name.to_ascii_lowercase(), r.clone())
            .is_some()
        {
            return Err(vec![diagnostic("duplicate_udt")]);
        }
    }
    let mut resolver = Resolver {
        catalog,
        overrides,
        plan: UdtDependencyPlan {
            closure: choices.to_vec(),
            issues: vec![],
        },
        visited: BTreeSet::new(),
        stack: vec![],
    };
    resolver.fields(&block.fields, "", 0);
    Ok(resolver.plan)
}

struct Resolver<'a> {
    catalog: &'a SourceCatalog,
    overrides: BTreeMap<String, DeclarationRef>,
    plan: UdtDependencyPlan,
    visited: BTreeSet<String>,
    stack: Vec<String>,
}
impl Resolver<'_> {
    fn fields(&mut self, fields: &[Field], prefix: &str, depth: usize) {
        for field in fields {
            let path = if prefix.is_empty() {
                field.name.clone()
            } else {
                format!("{prefix}.{}", field.name)
            };
            self.kind(&field.kind, &path, depth);
        }
    }
    fn issue(&mut self, code: &str, name: &str, path: &str, candidates: Vec<DeclarationRef>) {
        let mut diagnostic = diagnostic(code);
        diagnostic.path = path.into();
        self.plan.issues.push(UdtDependencyIssue {
            diagnostic,
            type_name: name.into(),
            candidates,
        });
    }
    fn kind(&mut self, kind: &Type, path: &str, depth: usize) {
        if depth > 8 {
            self.issue("expansion_depth", "", path, vec![]);
            return;
        }
        match kind {
            Type::Scalar(_) => {}
            Type::Struct(fields) => self.fields(fields, path, depth + 1),
            Type::Array(lower, _, inner) => {
                self.kind(inner, &format!("{path}[{lower}]"), depth + 1)
            }
            Type::Reference(name) => {
                let key = name.to_ascii_lowercase();
                if self.stack.contains(&key) {
                    self.issue("udt_cycle", name, path, vec![]);
                    return;
                }
                let candidates: Vec<_> = self
                    .catalog
                    .declarations
                    .iter()
                    .filter(|(_, d)| !d.db && d.name.eq_ignore_ascii_case(name))
                    .map(|(r, _)| r.clone())
                    .collect();
                let chosen = self
                    .overrides
                    .get(&key)
                    .cloned()
                    .or_else(|| (candidates.len() == 1).then(|| candidates[0].clone()));
                let Some(chosen) = chosen else {
                    self.issue(
                        if candidates.is_empty() {
                            "udt_missing"
                        } else {
                            "udt_ambiguous"
                        },
                        name,
                        path,
                        candidates,
                    );
                    return;
                };
                if !self.plan.closure.contains(&chosen) {
                    self.plan.closure.push(chosen.clone());
                }
                if !self.visited.insert(key.clone()) {
                    return;
                }
                let declaration = self
                    .catalog
                    .declarations
                    .iter()
                    .find(|(r, _)| *r == chosen)
                    .unwrap()
                    .1
                    .clone();
                if let Some(block) = declaration.block {
                    self.stack.push(key);
                    self.fields(&block.fields, path, depth + 1);
                    self.stack.pop();
                } else {
                    for problem in declaration.issues {
                        self.plan.issues.push(UdtDependencyIssue {
                            diagnostic: problem,
                            type_name: name.clone(),
                            candidates: vec![chosen.clone()],
                        });
                    }
                }
            }
        }
    }
}
