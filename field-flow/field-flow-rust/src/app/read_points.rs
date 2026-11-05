//! 文件：src/app/read_points.rs；按引用顺序执行单轮只读；首错结束，未读项不拼接旧样本。
use crate::{
    config::runtime_v2::ReadFlow,
    domain::id,
    services::devices::{Devices, PointSample},
    Result,
};
use std::sync::{Arc, Mutex};
#[derive(Debug, Clone, serde::Serialize)]
pub struct Item {
    pub device_id: String,
    pub point_id: String,
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sample: Option<PointSample>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error_key: Option<String>,
}
#[derive(Debug, Clone, Default, serde::Serialize)]
pub struct Observation {
    pub round_id: String,
    pub status: String,
    pub items: Vec<Item>,
    pub completed_rounds: u64,
    pub successful_reads: u64,
    pub errors: u64,
}
pub type Snapshot = Arc<Mutex<Observation>>;
pub async fn iteration(f: &ReadFlow, devices: &Devices, snapshot: &Snapshot) -> Result<()> {
    {
        let mut s = snapshot.lock().unwrap();
        s.round_id = id();
        s.status = "in_progress".into();
        s.items = f
            .reads
            .iter()
            .map(|r| Item {
                device_id: r.device_id.clone(),
                point_id: r.point_id.clone(),
                status: "not_attempted".into(),
                sample: None,
                error_key: None,
            })
            .collect();
    }
    for (at, r) in f.reads.iter().enumerate() {
        let result = match devices.get(&r.device_id) {
            Ok(d) => d.read(&r.point_id).await,
            Err(e) => Err(e),
        };
        let mut s = snapshot.lock().unwrap();
        match result {
            Ok(sample) => {
                s.successful_reads = s.successful_reads.saturating_add(1);
                s.items[at].status = "success".into();
                s.items[at].sample = Some(sample);
            }
            Err(e) => {
                s.status = if e == "canceled" {
                    "canceled"
                } else {
                    "failed"
                }
                .into();
                s.errors = s.errors.saturating_add(1);
                s.items[at].status = "error".into();
                s.items[at].error_key = Some(
                    e.chars()
                        .filter(|c| c.is_ascii_alphanumeric() || *c == '_')
                        .take(64)
                        .collect(),
                );
                return Err(e);
            }
        }
    }
    let mut s = snapshot.lock().unwrap();
    s.status = "complete".into();
    s.completed_rounds = s.completed_rounds.saturating_add(1);
    Ok(())
}
