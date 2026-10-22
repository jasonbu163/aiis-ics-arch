//! 原始协议地址/完整触达coverage/类型及每来源准入；所有检查在唯一提交前完成。
use super::{
    configuration::{Mode, WriteOwner},
    image::Image,
    layout::{CompiledDb, CompiledInstance},
    request::{Request, Source},
    typed_value,
};
pub struct Access {
    pub db: u16,
    pub begin: usize,
    pub end: usize,
    pub points: Vec<usize>,
}
fn range(r: &Request, db: &CompiledDb) -> Option<(usize, usize, u32, u32)> {
    if r.size == 0 || r.size > 256 {
        return None;
    }
    let begin = if r.bit.is_some() {
        r.start / 8
    } else {
        r.start
    };
    let end = begin.checked_add(if r.bit.is_some() { 1 } else { r.size })?;
    if end > db.length || r.bit.is_some() && r.size != 1 {
        return None;
    }
    let first = if r.bit.is_some() {
        u32::try_from(r.start).ok()?
    } else {
        u32::try_from(begin.checked_mul(8)?).ok()?
    };
    let last = if r.bit.is_some() {
        first.checked_add(1)?
    } else {
        u32::try_from(end.checked_mul(8)?).ok()?
    };
    Some((begin, end, first, last))
}
pub fn validate(r: &Request, image: &Image, config: &CompiledInstance) -> Option<Access> {
    let number = u16::try_from(r.db).ok()?;
    let db = config.dbs.get(&number)?;
    let mem = image.dbs.get(&number)?;
    let (begin, end, first, last) = range(r, db)?;
    if r.source == Source::Read {
        for span in db
            .coverage
            .iter()
            .filter(|s| s.first < last && s.end > first)
        {
            let p = &db.points[span.point];
            if !p.config.enabled || !p.policy.client_read {
                return None;
            }
        }
        return Some(Access {
            db: number,
            begin,
            end,
            points: vec![],
        });
    }
    if r.bit.is_some() && r.data[0] > 1 {
        return None;
    }
    // 严格按不重叠coverage前进，同一span只访问一次；最多256×8个索引，避免树节点临时分配。
    let mut points = Vec::new();
    let mut bit = first;
    while bit < last {
        let index = db.point_at(bit)?;
        let point = &db.points[index];
        if !point.config.enabled {
            return None;
        }
        let allowed = match r.source {
            Source::Client => {
                point.policy.mode == Mode::Hold
                    && point.policy.owner == WriteOwner::Client
                    && point.policy.client_write
            }
            Source::Ui => {
                point.policy.mode == Mode::Hold
                    && point.policy.owner == WriteOwner::Ui
                    && point.policy.ui_write
            }
            Source::Maintenance => {
                point.policy.mode == Mode::Hold
                    && matches!(point.policy.owner, WriteOwner::Client | WriteOwner::None)
                    && point.policy.ui_maintenance
            }
            Source::Rule => {
                point.policy.mode != Mode::Hold && point.policy.owner == WriteOwner::Rule
            }
            Source::Initialize => true,
            _ => false,
        };
        if !allowed {
            return None;
        }
        let point_first = point.byte as u32 * 8 + point.bit.unwrap_or(0) as u32;
        let point_last = point_first
            + if point.bit.is_some() {
                1
            } else {
                point.width as u32 * 8
            };
        if point.bit.is_none() {
            if r.bit.is_some() || first > point_first || last < point_last {
                return None;
            }
            let at = point.byte.checked_sub(begin)?;
            typed_value::decode(&point.config.data_type, r.data.get(at..at + point.width)?).ok()?;
        }
        points.push(index);
        bit = point_last.min(last);
    }
    if matches!(r.source, Source::Ui | Source::Maintenance) {
        if points.len() != 1 {
            return None;
        }
        let index = *points.first()?;
        let p = &db.points[index];
        if first != p.byte as u32 * 8 + p.bit.unwrap_or(0) as u32
            || last - first
                != if p.bit.is_some() {
                    1
                } else {
                    p.width as u32 * 8
                }
            || mem.points[index].seq != r.cas
        {
            return None;
        }
    }
    Some(Access {
        db: number,
        begin,
        end,
        points,
    })
}
