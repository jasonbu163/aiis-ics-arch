//! 本地只读快照/有界历史/原包/日志，不访问PLC、旧数据库或Backend health。
use super::local_supervisor::LocalEngine;
use crate::domain::{local_configuration::LocalResult, local_runtime::HistoryQuery};
use serde_json::{json, Value};
impl LocalEngine {
    pub fn snapshot(&self) -> LocalResult<Value> {
        let mut cache = self.cached_snapshot.lock().unwrap();
        if let Some((at, value)) = &*cache {
            if at.elapsed() < std::time::Duration::from_secs(1) {
                return Ok(value.clone());
            }
        }
        let configuration = self.configuration()?;
        let capacity = self.capacity()?;
        let mut states = self
            .states
            .lock()
            .unwrap()
            .values()
            .cloned()
            .collect::<Vec<_>>();
        for state in &mut states {
            if let Err(error) = self.log.health() {
                state.admission = "storage_fault".into();
                state.error = Some(error);
            }
            if self
                .active_io
                .lock()
                .unwrap()
                .get(&state.plc_id)
                .map(|(start, deadline)| start.elapsed().as_millis() > u128::from(*deadline))
                .unwrap_or(false)
            {
                state.phase = "driver_unresponsive".into();
                state.admission = "stopping".into();
                state.error = Some("driver_unresponsive".into());
            }
        }
        let operations = self
            .operations
            .lock()
            .unwrap()
            .iter()
            .cloned()
            .collect::<Vec<_>>();
        let value = json!({"schemaVersion":1,"mode":"local_sqlite","origin":if self.bootstrap.validation{"fixture"}else{"local"},"generatedAt":crate::domain::local_sample::now(),"configuration":configuration,"plcs":states,"capacity":capacity,"operations":operations});
        *cache = Some((std::time::Instant::now(), value.clone()));
        Ok(value)
    }
    pub fn history(&self, q: HistoryQuery) -> LocalResult<Value> {
        self.storage.call(true, move |s| s.history(q))
    }
    #[cfg(test)]
    pub fn sample(&self, id: String) -> LocalResult<Value> {
        self.storage.call(true, move |s| s.sample(&id))
    }
    pub fn sample_chunk(&self, id: String, offset: usize) -> LocalResult<Value> {
        self.storage
            .call(true, move |s| s.sample_chunk(&id, offset))
    }
    pub fn logs(&self, cursor: i64, limit: u32) -> LocalResult<Value> {
        self.log.health()?;
        self.storage.call(true, move |s| s.logs(cursor, limit))
    }
}
