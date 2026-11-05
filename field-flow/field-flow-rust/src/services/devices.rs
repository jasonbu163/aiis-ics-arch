//! 文件：src/services/devices.rs；flow绑定的只读设备子集，复用原Owner队列，不暴露物理地址或writer。
use crate::{
    config::{catalog::Catalog, runtime_v2::ReadFlow},
    runtime::Owner,
    Result,
};
use std::collections::HashMap;
#[derive(Clone)]
pub struct Devices {
    devices: HashMap<String, Device>,
}
#[derive(Clone)]
pub struct Device {
    device_id: String,
    flow_id: String,
    owner: Owner,
    points: HashMap<String, (u16, u32)>,
}
#[derive(Debug, Clone, serde::Serialize)]
pub struct PointSample {
    pub device_id: String,
    pub point_id: String,
    pub flow_id: String,
    pub request_id: String,
    pub generation: u64,
    pub value: i16,
    pub quality: String,
    pub received_at: String,
}
fn shanghai_offset() -> chrono::FixedOffset {
    chrono::FixedOffset::east_opt(28800).unwrap()
}
pub fn local_time() -> String {
    chrono::Utc::now()
        .with_timezone(&shanghai_offset())
        .to_rfc3339_opts(chrono::SecondsFormat::Millis, false)
}
impl Devices {
    pub(crate) fn bind(
        f: &ReadFlow,
        catalogs: &[Catalog],
        owners: &HashMap<String, Owner>,
    ) -> Result<Self> {
        let mut devices = HashMap::new();
        for id in &f.device_ids {
            let c = catalogs
                .iter()
                .find(|c| &c.id == id)
                .ok_or("config_device")?;
            let owner = owners.get(id).ok_or("config_device")?.clone();
            devices.insert(
                id.clone(),
                Device {
                    device_id: id.clone(),
                    flow_id: f.id.clone(),
                    owner,
                    points: c
                        .points
                        .iter()
                        .filter(|p| p.enabled)
                        .map(|p| (p.id.clone(), (p.db, p.offset)))
                        .collect(),
                },
            );
        }
        Ok(Self { devices })
    }
    pub fn get(&self, id: &str) -> Result<&Device> {
        self.devices.get(id).ok_or("device_not_allowed".into())
    }
}
impl Device {
    pub async fn read(&self, point_id: &str) -> Result<PointSample> {
        let (db, offset) = self.points.get(point_id).ok_or("point_not_allowed")?;
        let s = self.owner.read(&self.flow_id, *db, *offset).await?;
        Ok(PointSample {
            device_id: self.owner_id(),
            point_id: point_id.into(),
            flow_id: s.flow_id,
            request_id: s.request_id,
            generation: s.generation,
            value: s.value,
            quality: s.quality,
            received_at: chrono::DateTime::from_timestamp_millis(s.sampled_at_ms)
                .ok_or("sample_time")?
                .with_timezone(&shanghai_offset())
                .to_rfc3339_opts(chrono::SecondsFormat::Millis, false),
        })
    }
    fn owner_id(&self) -> String {
        self.device_id.clone()
    }
}
