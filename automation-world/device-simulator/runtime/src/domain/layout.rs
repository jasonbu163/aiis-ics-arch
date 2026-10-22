//! 完整有界配置编译：稀疏bit区间coverage，不按每个DB byte复制版本元数据。
use super::{configuration::*, rule, typed_value};
use serde::Serialize;
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
pub struct Span {
    pub first: u32,
    pub end: u32,
    pub point: usize,
}
#[derive(Clone, Debug)]
pub struct CompiledPoint {
    pub config: super::configuration::PointConfig,
    pub byte: usize,
    pub bit: Option<u8>,
    pub width: usize,
    pub initial: Vec<u8>,
    pub policy: EffectivePolicy,
}
#[derive(Clone, Debug)]
pub struct CompiledDb {
    pub id: String,
    pub number: u16,
    pub length: usize,
    pub structure_sha256: String,
    pub layout_sha256: String,
    pub points: Vec<CompiledPoint>,
    pub coverage: Vec<Span>,
}
#[derive(Clone, Debug)]
pub struct CompiledInstance {
    pub config: InstanceConfig,
    pub dbs: BTreeMap<u16, CompiledDb>,
    pub point_index: BTreeMap<String, (u16, usize)>,
    pub rule_points: Vec<(u16, usize)>,
    pub allocation_upper: usize,
}
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Issue {
    pub code: String,
    pub instance_id: String,
    pub db_id: Option<String>,
    pub point_id: Option<String>,
}

pub fn structure_signature(db: &DbConfig) -> String {
    digest(&(
        db.id.as_str(),
        db.number,
        db.length,
        &db.binding,
        db.points
            .iter()
            .map(|p| (&p.id, &p.data_type, &p.source_path, &p.segments, p.manual))
            .collect::<Vec<_>>(),
    ))
}
pub fn layout_signature(db: &DbConfig) -> String {
    digest(&(
        structure_signature(db),
        db.points
            .iter()
            .map(|p| (&p.id, p.byte, p.bit))
            .collect::<Vec<_>>(),
    ))
}
pub fn names_signature(instance: &InstanceConfig) -> String {
    digest(
        &instance
            .dbs
            .iter()
            .flat_map(|db| {
                db.points.iter().map(move |p| {
                    (
                        db.number,
                        &p.id,
                        &p.name,
                        &p.data_type,
                        &p.segments,
                        p.byte,
                        p.bit,
                    )
                })
            })
            .collect::<Vec<_>>(),
    )
}
pub fn initial_signature(kind: &str, effective: &EffectivePolicy) -> Result<String, String> {
    Ok(digest(&(
        kind,
        typed_value::encode(kind, &effective.initial)?,
    )))
}
pub fn policy_signature(effective: &EffectivePolicy) -> String {
    digest(&(
        effective.mode,
        effective.owner,
        effective.client_read,
        effective.client_write,
        effective.ui_write,
        effective.ui_maintenance,
        &effective.rule,
    ))
}

pub fn effective_policy(
    instance: &InstanceConfig,
    db: &DbConfig,
    point: &PointConfig,
) -> Result<EffectivePolicy, String> {
    let mut effective = EffectivePolicy::new(&point.data_type)?;
    effective.overlay(&instance.policy, "instance");
    effective.overlay(&db.policy, "db");
    if let Some(byte) = point.byte {
        let begin = byte
            .checked_mul(8)
            .and_then(|v| v.checked_add(point.bit.unwrap_or(0) as u32))
            .ok_or("address_invalid")?;
        let end = begin
            .checked_add(if point.data_type == "BOOL" {
                1
            } else {
                typed_value::width(&point.data_type)? as u32 * 8
            })
            .ok_or("address_invalid")?;
        for region in &db.regions {
            let region_end = region
                .first_bit
                .checked_add(region.bit_length)
                .ok_or("policy_region")?;
            if begin < region_end && end > region.first_bit {
                if begin < region.first_bit || end > region_end {
                    return Err("policy_split_field".into());
                }
                effective.overlay(&region.policy, &format!("region:{}", region.id));
            }
        }
    }
    effective.overlay(&point.policy, "point");
    if effective.mode == Mode::Hold {
        if effective.owner == WriteOwner::Rule {
            return Err("policy_owner".into());
        }
        effective.rule = None;
    } else {
        if effective.owner != WriteOwner::Rule
            || effective.client_write
            || effective.ui_write
            || effective.ui_maintenance
        {
            return Err("policy_owner".into());
        }
        let spec = effective.rule.as_ref().ok_or("rule_missing")?;
        let kind = match effective.mode {
            Mode::Fixed => rule::RuleKind::Fixed,
            Mode::Ramp => rule::RuleKind::Ramp,
            Mode::Sine => rule::RuleKind::Sine,
            Mode::Random => rule::RuleKind::Random,
            Mode::Toggle => rule::RuleKind::Toggle,
            _ => unreachable!(),
        };
        if spec.kind != kind {
            return Err("rule_mode".into());
        }
        rule::validate(&point.data_type, spec)?;
    }
    if effective.client_write && effective.owner != WriteOwner::Client
        || effective.ui_write && effective.owner != WriteOwner::Ui
        || effective.ui_maintenance
            && !matches!(effective.owner, WriteOwner::Client | WriteOwner::None)
    {
        return Err("policy_owner".into());
    }
    typed_value::encode(&point.data_type, &effective.initial)?;
    Ok(effective)
}

pub fn compile(instance: &InstanceConfig) -> Result<CompiledInstance, Vec<Issue>> {
    let mut issues = vec![];
    let mut add = |code: &str, db: Option<&DbConfig>, p: Option<&PointConfig>| {
        issues.push(Issue {
            code: code.into(),
            instance_id: instance.id.clone(),
            db_id: db.map(|d| d.id.clone()),
            point_id: p.map(|p| p.id.clone()),
        })
    };
    if instance.dbs.iter().all(|db| !db.enabled) || instance.dbs.is_empty() {
        add("instance_unconfigured", None, None);
    }
    if instance.names_confirmation.as_ref() != Some(&names_signature(instance)) {
        add("names_unconfirmed", None, None);
    }
    let mut dbs = BTreeMap::new();
    let mut point_index = BTreeMap::new();
    let mut rule_points = vec![];
    let mut names = BTreeSet::new();
    // Budget includes candidate/image/snapshot copies, structured config and per-point state;
    // native protocol reservations/threads are separately bounded by transport admission.
    let mut allocation_upper = serde_json::to_vec(instance)
        .map(|x| x.len() * 4)
        .unwrap_or(usize::MAX / 2);
    for db in &instance.dbs {
        for p in &db.points {
            if (db.enabled
                && p.enabled
                && aiis_tia_import_core::validate_manual_name(&p.name).is_err())
                || (!p.name.is_empty() && !names.insert(p.name.clone()))
            {
                add("point_name_invalid_or_duplicate", Some(db), Some(p));
            }
        }
        if !db.enabled {
            continue;
        }
        let structure = structure_signature(db);
        let layout = layout_signature(db);
        if db.binding.as_ref().is_some_and(|b| !b.standard) {
            add("source_optimized", Some(db), None);
        }
        if db
            .address_confirmation
            .as_ref()
            .is_none_or(|c| c.structure_sha256 != structure || c.layout_sha256 != layout)
        {
            add("layout_unconfirmed", Some(db), None);
        }
        if let Some(binding) = &db.binding {
            let tree = binding
                .tree
                .iter()
                .map(aiis_tia_import_core::FieldNode::from)
                .collect::<Vec<_>>();
            let leaves = aiis_tia_import_core::structured_leaves(&tree);
            if leaves.len() != db.points.len()
                || leaves.iter().any(|l| {
                    !db.points.iter().any(|p| {
                        p.source_path == l.path
                            && p.data_type == l.data_type
                            && p.segments
                                == l.segments
                                    .iter()
                                    .map(super::source::PathSegment::from)
                                    .collect::<Vec<_>>()
                    })
                })
            {
                add("structure_incomplete", Some(db), None);
            }
        }
        if db.points.is_empty() {
            add("structure_incomplete", Some(db), None);
        }
        let mut regions = db.regions.iter().collect::<Vec<_>>();
        regions.sort_by_key(|x| x.first_bit);
        if regions.windows(2).any(|w| {
            w[0].first_bit
                .checked_add(w[0].bit_length)
                .is_none_or(|end| end > w[1].first_bit)
        }) {
            add("policy_region_overlap", Some(db), None);
        }
        let mut points = vec![];
        let mut coverage = vec![];
        for p in &db.points {
            let width = match typed_value::width(&p.data_type) {
                Ok(w) => w,
                Err(e) => {
                    add(&e, Some(db), Some(p));
                    continue;
                }
            };
            let Some(byte) = p.byte else {
                add("address_unconfirmed", Some(db), Some(p));
                continue;
            };
            if p.data_type == "BOOL" && p.bit.is_none()
                || p.data_type != "BOOL" && p.bit.is_some()
                || byte
                    .checked_add(width as u32)
                    .is_none_or(|end| end > db.length)
            {
                add("address_invalid", Some(db), Some(p));
                continue;
            }
            let effective = match effective_policy(instance, db, p) {
                Ok(v) => v,
                Err(e) => {
                    add(&e, Some(db), Some(p));
                    continue;
                }
            };
            if p.confirmations.initial.as_ref()
                != initial_signature(&p.data_type, &effective).ok().as_ref()
            {
                add("initial_unconfirmed", Some(db), Some(p));
            }
            if p.confirmations.policy.as_ref() != Some(&policy_signature(&effective)) {
                add("policy_unconfirmed", Some(db), Some(p));
            }
            let index = points.len();
            let first = byte * 8 + p.bit.unwrap_or(0) as u32;
            let end = first
                + if p.data_type == "BOOL" {
                    1
                } else {
                    width as u32 * 8
                };
            coverage.push(Span {
                first,
                end,
                point: index,
            });
            point_index.insert(p.id.clone(), (db.number, index));
            if p.enabled && effective.mode != Mode::Hold {
                rule_points.push((db.number, index));
            }
            points.push(CompiledPoint {
                config: p.clone(),
                byte: byte as usize,
                bit: p.bit,
                width,
                initial: typed_value::encode(&p.data_type, &effective.initial).unwrap(),
                policy: effective,
            });
        }
        coverage.sort_by_key(|s| s.first);
        if coverage.windows(2).any(|w| w[0].end > w[1].first) {
            add("layout_overlap", Some(db), None);
        }
        allocation_upper = allocation_upper
            .saturating_add(db.length as usize * 3)
            .saturating_add(
                points.len() * (std::mem::size_of::<CompiledPoint>() + 128)
                    + coverage.capacity() * std::mem::size_of::<Span>(),
            );
        dbs.insert(
            db.number,
            CompiledDb {
                id: db.id.clone(),
                number: db.number,
                length: db.length as usize,
                structure_sha256: structure,
                layout_sha256: layout,
                points,
                coverage,
            },
        );
    }
    if allocation_upper > 512 * 1024 * 1024 {
        add("runtime_capacity", None, None);
    }
    if !issues.is_empty() {
        return Err(issues);
    }
    Ok(CompiledInstance {
        config: instance.clone(),
        dbs,
        point_index,
        rule_points,
        allocation_upper,
    })
}

impl CompiledDb {
    pub fn point_at(&self, bit: u32) -> Option<usize> {
        let at = self
            .coverage
            .partition_point(|span| span.first <= bit)
            .checked_sub(1)?;
        let span = &self.coverage[at];
        (bit < span.end).then_some(span.point)
    }
}
