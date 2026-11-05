//! SMA本地配置用例：同一串行服务协调CAS、运行准入、预览令牌及显式恢复。
use crate::{
    contracts::local_configuration::*,
    domain::{local_configuration as domain, runtime::ManagedRuntimeState},
    infrastructure::config_store::ConfigStore,
};
use serde_json::Value;
use std::{
    collections::BTreeMap,
    path::PathBuf,
    sync::{Mutex, MutexGuard},
};
struct Pending {
    intent: ChangeIntent,
    revision: u64,
    document: ConfigurationDocument,
}
struct Inner {
    store: Result<ConfigStore, String>,
    pending: BTreeMap<String, Pending>,
    sequence: u64,
}
pub struct LocalConfigurationService {
    inner: Mutex<Inner>,
}
impl LocalConfigurationService {
    pub fn new(path: Result<PathBuf, String>) -> Self {
        let store = path.and_then(|p| ConfigStore::open(&p));
        if let Err(code) = &store {
            tracing::warn!(event="sma_configuration_open",result="rejected",error_code=%code);
        }
        Self {
            inner: Mutex::new(Inner {
                store,
                pending: BTreeMap::new(),
                sequence: 0,
            }),
        }
    }
    fn lock(&self) -> Result<MutexGuard<'_, Inner>, String> {
        self.inner
            .lock()
            .map_err(|_| "SMA_CONFIGURATION_SERVICE_UNAVAILABLE".into())
    }
    pub fn load(&self) -> Result<ConfigurationSnapshot, String> {
        let mut inner = self.lock()?;
        store(&mut inner)?.load()
    }
    pub fn change(
        &self,
        expected: u64,
        intent: ChangeIntent,
        runtime: &ManagedRuntimeState,
    ) -> Result<ConfigurationSnapshot, String> {
        if matches!(intent.kind.as_str(), "import" | "restore" | "catalog") {
            return Err("SMA_CONFIGURATION_PREVIEW_REQUIRED".into());
        }
        let mut inner = self.lock()?;
        not_busy(runtime)?;
        let result = store(&mut inner)?.update(expected, |d| domain::transform(d, &intent));
        record("commit", expected, &result);
        result
    }
    pub fn preview(&self, expected: u64, intent: ChangeIntent) -> Result<ImportPreview, String> {
        if !matches!(intent.kind.as_str(), "import" | "restore" | "catalog") {
            return Err("SMA_CONFIGURATION_INTENT_INVALID".into());
        }
        let mut inner = self.lock()?;
        let snapshot = store(&mut inner)?.load()?;
        if snapshot.revision != expected {
            return Err("SMA_CONFIGURATION_CONFLICT".into());
        }
        let mut result = ImportPreview {
            token: String::new(),
            expected_revision: expected,
            created_keys: vec![],
            updated_keys: vec![],
            unchanged_keys: vec![],
            deleted_keys: vec![],
            errors: vec![],
        };
        match domain::transform(&snapshot.document, &intent) {
            Ok(document) => {
                let old = entities(&snapshot.document);
                let new = entities(&document);
                for (k, v) in &new {
                    match old.get(k) {
                        None => result.created_keys.push(k.clone()),
                        Some(e) if e == v => result.unchanged_keys.push(k.clone()),
                        _ => result.updated_keys.push(k.clone()),
                    }
                }
                for k in old.keys() {
                    if !new.contains_key(k) {
                        result.deleted_keys.push(k.clone());
                    }
                }
                inner.sequence += 1;
                result.token = format!("local-preview-{}", inner.sequence);
                if inner.pending.len() >= 8 {
                    inner.pending.clear();
                }
                inner.pending.insert(
                    result.token.clone(),
                    Pending {
                        intent,
                        revision: expected,
                        document,
                    },
                );
            }
            Err(error) => result.errors.push(ImportError {
                key: "configuration".into(),
                error_code: error,
            }),
        }
        Ok(result)
    }
    pub fn apply(
        &self,
        expected: u64,
        intent: ChangeIntent,
        token: &str,
        confirmed: bool,
        runtime: &ManagedRuntimeState,
    ) -> Result<ConfigurationSnapshot, String> {
        let mut inner = self.lock()?;
        not_busy(runtime)?;
        let p = inner
            .pending
            .get(token)
            .ok_or("SMA_CONFIGURATION_PREVIEW_REQUIRED")?;
        if p.revision != expected || p.intent != intent {
            return Err("SMA_CONFIGURATION_PREVIEW_CHANGED".into());
        }
        if intent.kind == "restore" && !confirmed {
            return Err("SMA_CONFIGURATION_RESTORE_CONFIRMATION_REQUIRED".into());
        }
        let document = p.document.clone();
        let result = store(&mut inner)?.update(expected, |_| Ok(document));
        record(
            if intent.kind == "restore" {
                "restore"
            } else {
                "import_apply"
            },
            expected,
            &result,
        );
        if result.is_ok() {
            inner.pending.remove(token);
        }
        result
    }
    pub fn export(&self) -> Result<String, String> {
        let s = self.load()?;
        domain::validate(&s.document)?;
        serde_json::to_string_pretty(&domain::backup(&s.document))
            .map_err(|_| "SMA_CONFIGURATION_INVALID".into())
    }
    pub fn saved_preview(&self, id: &str, expected: u64) -> Result<Value, String> {
        let s = self.load()?;
        if s.revision != expected {
            return Err("SMA_CONFIGURATION_CONFLICT".into());
        }
        domain::saved_preview(&s, id)
    }
    /// 正常应用唯一准入，拒绝发生在client构造、spawn或远端读取之前。
    pub fn admit_execution(&self) -> Result<(), String> {
        let _guard = self.lock()?;
        reject_execution()
    }
}
fn store(inner: &mut Inner) -> Result<&mut ConfigStore, String> {
    inner.store.as_mut().map_err(|e| e.clone())
}
fn not_busy(runtime: &ManagedRuntimeState) -> Result<(), String> {
    if matches!(
        runtime.snapshot().status.as_str(),
        "starting" | "running" | "paused" | "stopping"
    ) {
        tracing::warn!(
            event = "sma_configuration_commit",
            result = "rejected",
            error_code = "SMA_CONFIGURATION_RUNTIME_BUSY"
        );
        Err("SMA_CONFIGURATION_RUNTIME_BUSY".into())
    } else {
        Ok(())
    }
}
pub fn reject_execution() -> Result<(), String> {
    tracing::warn!(
        event = "sma_execution_admission",
        result = "rejected",
        error_code = "SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE"
    );
    Err("SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE".into())
}
fn record(action: &str, revision: u64, result: &Result<ConfigurationSnapshot, String>) {
    match result {
        Ok(s) => tracing::info!(
            event = "sma_configuration_write",
            action,
            revision = s.revision,
            result = "committed"
        ),
        Err(code) => {
            tracing::warn!(event="sma_configuration_write",action,revision,result="rejected",error_code=%code)
        }
    }
}
fn entities(d: &ConfigurationDocument) -> BTreeMap<String, Value> {
    let mut out = BTreeMap::new();
    out.insert(
        "connection".into(),
        serde_json::to_value(&d.connection).unwrap(),
    );
    out.insert("catalog".into(), serde_json::to_value(&d.catalog).unwrap());
    out.insert(
        "sourceMetadata".into(),
        serde_json::to_value(&d.source_metadata).unwrap(),
    );
    for r in ["materials", "targetApis", "mappingValueRules", "mappings"] {
        for v in domain::collection(d, r).unwrap() {
            out.insert(
                format!(
                    "{r}:{}",
                    v[domain::key_field(r).unwrap()].as_str().unwrap_or("?")
                ),
                v.clone(),
            );
        }
    }
    out
}
