//! 每实例唯一可变DB image与逐点提交元数据；padding永远为零且没有逐bit版本副本。
use super::{
    layout::{CompiledInstance, CompiledPoint},
    request::Source,
    typed_value,
};
use crate::infrastructure::clock;
use std::collections::BTreeMap;
#[derive(Clone, Debug)]
pub struct PointState {
    pub seq: u64,
    pub source: Source,
    pub updated: u64,
}
#[derive(Clone, Debug)]
pub struct DbImage {
    pub bytes: Vec<u8>,
    pub points: Vec<PointState>,
}
pub struct Image {
    pub dbs: BTreeMap<u16, DbImage>,
    pub seq: u64,
    pub epoch: u64,
    pub revision: u64,
    pub loaded_revision: String,
}
impl Image {
    pub fn new(
        config: &CompiledInstance,
        epoch: u64,
        revision: u64,
        loaded_revision: String,
        source: Source,
    ) -> Self {
        let mut dbs = BTreeMap::new();
        let now = clock::ns();
        for (number, db) in &config.dbs {
            let mut image = DbImage {
                bytes: vec![0; db.length],
                points: vec![
                    PointState {
                        seq: 0,
                        source,
                        updated: now
                    };
                    db.points.len()
                ],
            };
            for point in &db.points {
                store_point(&mut image.bytes, point, &point.initial);
            }
            dbs.insert(*number, image);
        }
        Self {
            dbs,
            seq: 0,
            epoch,
            revision,
            loaded_revision,
        }
    }
    pub fn typed(
        &self,
        number: u16,
        index: usize,
        point: &CompiledPoint,
    ) -> Result<serde_json::Value, String> {
        let db = self.dbs.get(&number).ok_or("db_not_loaded")?;
        let _ = db.points.get(index).ok_or("point_not_loaded")?;
        if let Some(bit) = point.bit {
            typed_value::decode(
                &point.config.data_type,
                &[(db.bytes[point.byte] >> bit) & 1],
            )
        } else {
            typed_value::decode(
                &point.config.data_type,
                &db.bytes[point.byte..point.byte + point.width],
            )
        }
    }
}
pub fn store_point(bytes: &mut [u8], point: &CompiledPoint, value: &[u8]) {
    if let Some(bit) = point.bit {
        let mask = 1 << bit;
        bytes[point.byte] = (bytes[point.byte] & !mask) | if value[0] != 0 { mask } else { 0 };
    } else {
        bytes[point.byte..point.byte + point.width].copy_from_slice(value);
    }
}
pub fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}
