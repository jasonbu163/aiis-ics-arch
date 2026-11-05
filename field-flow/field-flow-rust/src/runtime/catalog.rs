//! 文件：src/runtime/catalog.rs；v2只读流装配及5秒分块观察，生命周期复用原Runtime。
use super::{FlowHealth, Runtime};
use crate::{
    app::read_points::{self, Observation, Snapshot},
    config::runtime_v2::Loaded,
    domain::now_ms,
    services::devices::{local_time, Devices},
    Result,
};
use serde_json::{json, Value};
use std::{
    sync::{atomic::Ordering, Arc, Mutex},
    time::Duration,
};
impl Runtime {
    pub async fn launch_catalog(&mut self, loaded: &Loaded) -> Result<()> {
        self.launch_flows(&loaded.config)?;
        for c in &loaded.catalogs {
            self.state
                .log("plc_catalog_loaded", c.file_summary())
                .await?;
        }
        for f in loaded.reads.clone() {
            let devices = Devices::bind(&f, &loaded.catalogs, &self.owners)?;
            let snapshot: Snapshot = Arc::new(Mutex::new(Observation::default()));
            self.points.insert(f.id.clone(), snapshot.clone());
            let stop = self.stop.clone();
            let health = self.flows.clone();
            let state = self.state.clone();
            health.lock().unwrap().insert(
                f.id.clone(),
                FlowHealth {
                    state: "starting".into(),
                    last_iteration_ms: None,
                    last_success_ms: None,
                    consecutive_errors: 0,
                    iterations: 0,
                    in_flight: 0,
                },
            );
            self.flow_tasks.push(tokio::spawn(async move {
                loop {if stop.stopped.load(Ordering::Acquire){break;}
                    {let mut h=health.lock().unwrap();let h=h.get_mut(&f.id).unwrap();h.in_flight=1;h.last_iteration_ms=Some(now_ms());h.iterations=h.iterations.saturating_add(1);}
                    let result=read_points::iteration(&f,&devices,&snapshot).await;let mut event=None;
                    {let mut h=health.lock().unwrap();let h=h.get_mut(&f.id).unwrap();h.in_flight=0;match result{Ok(())=>{h.state="running".into();h.last_success_ms=Some(now_ms());h.consecutive_errors=0;},Err(e)=>{h.state="recovering".into();h.consecutive_errors=h.consecutive_errors.saturating_add(1);if h.consecutive_errors==1{event=Some(e);}}}}
                    if let Some(e)=event{let _=state.log("flow_health",json!({"flow_id":f.id,"error_key":e,"state":"recovering"})).await;}
                    tokio::select!{_=stop.wait()=>break,_=tokio::time::sleep(Duration::from_millis(f.interval_ms))=>{}}
                }
                let mut s=snapshot.lock().unwrap();if s.status=="in_progress"{s.status="canceled".into();}drop(s);health.lock().unwrap().get_mut(&f.id).unwrap().state="stopped".into();
            }));
        }
        Ok(())
    }
    pub fn points_snapshot(&self, flow: &str) -> Option<Observation> {
        self.points.get(flow).map(|s| s.lock().unwrap().clone())
    }
    pub async fn points_health(&self) -> Result<()> {
        for (flow, s) in &self.points {
            let s = s.lock().unwrap().clone();
            for context in chunks(flow, &s) {
                self.state.log("points_health", context).await?;
            }
        }
        Ok(())
    }
}
pub fn chunks(flow: &str, s: &Observation) -> Vec<Value> {
    if s.round_id.is_empty() {
        return Vec::new();
    }
    let count = s.items.len().div_ceil(4).max(1);
    (0..count).map(|i|json!({"flow_id":flow,"round_id":s.round_id,"status":s.status,"observed_at":local_time(),"chunk_index":i,"chunk_count":count,"completed_rounds":s.completed_rounds,"successful_reads":s.successful_reads,"errors":s.errors,"items":s.items.iter().skip(i*4).take(4).collect::<Vec<_>>()})).collect()
}
