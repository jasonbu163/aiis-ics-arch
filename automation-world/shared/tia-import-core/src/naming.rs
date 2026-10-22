//! 单namespace确定命名：结构化原始段、全体flatten碰撞、一次地址兜底与最终冲突拒绝。
use crate::model::*;
use std::collections::{BTreeMap, BTreeSet};
pub const NAME_PROFILE: &str = "tia-point-name-v1";
#[derive(Clone, Debug, PartialEq)]
pub struct ConfirmedAddress {
    pub byte: u32,
    pub bit: Option<u8>,
}
#[derive(Clone, Debug)]
pub struct NameEntry {
    pub key: String,
    pub db_number: u16,
    pub path: Option<Vec<PathSegment>>,
    pub data_type: String,
    pub current_name: String,
    pub mutable: bool,
    pub address: Option<ConfirmedAddress>,
    pub manual_name: Option<String>,
    pub address_only: bool,
}
#[derive(Clone, Debug)]
pub struct NameBatch {
    pub profile: String,
    pub entries: Vec<NameEntry>,
}
#[derive(Clone, Debug, PartialEq)]
pub enum NameResolution {
    Resolved { name: String, mode: String },
    Pending,
}
#[derive(Clone, Debug)]
pub struct NameRow {
    pub key: String,
    pub resolution: NameResolution,
    pub reason: String,
}
#[derive(Clone, Debug)]
pub struct NamePlan {
    pub rows: Vec<NameRow>,
}
pub fn type_suffix(t: &str) -> Result<&'static str, String> {
    Ok(match t {
        "BOOL" => "Bool",
        "BYTE" => "Byte",
        "USINT" => "USInt",
        "CHAR" => "Char",
        "INT" => "Int",
        "UINT" => "UInt",
        "WORD" => "Word",
        "DINT" => "DInt",
        "UDINT" => "UDInt",
        "DWORD" => "DWord",
        "REAL" => "Real",
        _ if t.starts_with("STRING[") && width(t).is_some() => "String",
        _ => return Err("unsupported_type".into()),
    })
}
pub fn validate_manual_name(name: &str) -> Result<(), String> {
    let mut bytes = name.bytes();
    if name.is_empty()
        || name.len() > 100
        || !bytes
            .next()
            .map(|b| b.is_ascii_alphabetic() || b == b'_')
            .unwrap_or(false)
        || !bytes.all(|b| b.is_ascii_alphanumeric() || b == b'_')
    {
        return Err("point_name_invalid".into());
    }
    Ok(())
}
fn primary(e: &NameEntry) -> Option<String> {
    let path = e.path.as_ref()?;
    if path.is_empty() {
        return None;
    }
    let fields: Option<Vec<_>> = path
        .iter()
        .map(|s| match s {
            PathSegment::Field(v)
                if !v.is_empty() && v.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_') =>
            {
                Some(v.as_str())
            }
            _ => None,
        })
        .collect();
    let name = format!(
        "DB{}_{}_{}",
        e.db_number,
        fields?.join("_"),
        type_suffix(&e.data_type).ok()?
    );
    (name.len() <= 100).then_some(name)
}
fn address(e: &NameEntry) -> Result<NameResolution, String> {
    let Some(a) = &e.address else {
        return Ok(NameResolution::Pending);
    };
    if a.byte
        .checked_add(width(&e.data_type).ok_or("unsupported_type")?)
        .map(|v| v > 65536)
        .unwrap_or(true)
    {
        return Err("address_invalid".into());
    }
    let suffix = type_suffix(&e.data_type)?;
    let name = if e.data_type == "BOOL" {
        let bit = a.bit.filter(|b| *b < 8).ok_or("address_invalid")?;
        format!("DB{}_B{}_{}_Bool", e.db_number, a.byte, bit)
    } else {
        if a.bit.is_some() {
            return Err("address_invalid".into());
        }
        format!("DB{}_B{}_{}", e.db_number, a.byte, suffix)
    };
    Ok(NameResolution::Resolved {
        name,
        mode: "auto_address".into(),
    })
}
fn resolved_name(r: &NameResolution) -> Option<&str> {
    match r {
        NameResolution::Resolved { name, .. } => Some(name),
        _ => None,
    }
}
pub fn plan_names(batch: &NameBatch) -> Result<NamePlan, Vec<Diagnostic>> {
    let run = || -> Result<NamePlan, Diagnostic> {
        if batch.profile != NAME_PROFILE || batch.entries.len() > 4096 {
            return Err(diagnostic("point_name_profile"));
        }
        let mut keys = BTreeSet::new();
        let mut all: BTreeMap<String, BTreeSet<Vec<PathSegment>>> = BTreeMap::new();
        for e in &batch.entries {
            if e.db_number == 0 || !keys.insert(&e.key) {
                return Err(diagnostic("point_name_selection"));
            }
            type_suffix(&e.data_type).map_err(|e| diagnostic(&e))?;
            if let Some(name) = primary(e) {
                all.entry(name).or_default().insert(e.path.clone().unwrap());
            }
        }
        let mut entries: Vec<_> = batch.entries.iter().filter(|e| e.mutable).collect();
        entries.sort_by(|a, b| (a.db_number, &a.path, &a.key).cmp(&(b.db_number, &b.path, &b.key)));
        let mut rows = vec![];
        for e in &entries {
            let (resolution, reason) = if let Some(manual) = &e.manual_name {
                validate_manual_name(manual).map_err(|e| diagnostic(&e))?;
                (
                    NameResolution::Resolved {
                        name: manual.clone(),
                        mode: "manual".into(),
                    },
                    "manual".to_string(),
                )
            } else if e.address_only {
                (
                    address(e).map_err(|e| diagnostic(&e))?,
                    "address_required".into(),
                )
            } else if let Some(p) = primary(e) {
                if all.get(&p).map(|v| v.len() > 1).unwrap_or(false) {
                    (
                        address(e).map_err(|e| diagnostic(&e))?,
                        "flatten_collision".into(),
                    )
                } else {
                    (
                        NameResolution::Resolved {
                            name: p,
                            mode: "auto_path".into(),
                        },
                        "path".into(),
                    )
                }
            } else {
                (
                    address(e).map_err(|e| diagnostic(&e))?,
                    "address_required".into(),
                )
            };
            rows.push(NameRow {
                key: e.key.clone(),
                resolution,
                reason,
            });
        }
        let reserved: BTreeSet<_> = batch
            .entries
            .iter()
            .filter(|e| !e.mutable)
            .map(|e| e.current_name.as_str())
            .collect();
        let mut counts = BTreeMap::new();
        for row in &rows {
            if let Some(n) = resolved_name(&row.resolution) {
                *counts.entry(n.to_string()).or_insert(0) += 1;
            }
        }
        // Decide simultaneously from the first candidate set, never picking an input-order winner.
        for row in &mut rows {
            if let NameResolution::Resolved { name, mode } = &row.resolution {
                if mode == "auto_path"
                    && (reserved.contains(name.as_str())
                        || counts.get(name).copied().unwrap_or(0) > 1)
                {
                    let e = entries.iter().find(|e| e.key == row.key).unwrap();
                    row.resolution = address(e).map_err(|e| diagnostic(&e))?;
                    row.reason = "reserved_collision".into();
                }
            }
        }
        let mut names: BTreeMap<String, Vec<String>> = BTreeMap::new();
        for e in batch.entries.iter().filter(|e| !e.mutable) {
            names
                .entry(e.current_name.clone())
                .or_default()
                .push(e.key.clone());
        }
        for row in &rows {
            if let Some(n) = resolved_name(&row.resolution) {
                names.entry(n.into()).or_default().push(row.key.clone());
            }
        }
        let collisions: Vec<_> = names
            .into_iter()
            .filter(|(_, ks)| ks.len() > 1 && ks.iter().any(|k| rows.iter().any(|r| r.key == *k)))
            .collect();
        if !collisions.is_empty() {
            return Err(Diagnostic {
                code: "point_name_conflict".into(),
                path: collisions
                    .iter()
                    .map(|(n, ks)| format!("{}:{}", n, ks.join(",")))
                    .collect::<Vec<_>>()
                    .join(";"),
                line: 0,
                file: String::new(),
            });
        }
        Ok(NamePlan { rows })
    };
    run().map_err(|e| vec![e])
}
