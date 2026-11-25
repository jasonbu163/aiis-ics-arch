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
    sync::{Arc, Mutex, MutexGuard},
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
#[derive(Clone)]
pub struct LocalConfigurationService {
    inner: Arc<Mutex<Inner>>,
}
impl LocalConfigurationService {
    pub fn new(path: Result<PathBuf, String>) -> Self {
        let store = path.and_then(|p| ConfigStore::open(&p));
        if let Err(code) = &store {
            tracing::warn!(event="sma_configuration_open",result="rejected",error_code=%code);
        }
        Self {
            inner: Arc::new(Mutex::new(Inner {
                store,
                pending: BTreeMap::new(),
                sequence: 0,
            })),
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
        if matches!(
            intent.kind.as_str(),
            "import" | "restore" | "catalog" | "merge"
        ) {
            return Err("SMA_CONFIGURATION_PREVIEW_REQUIRED".into());
        }
        let mut inner = self.lock()?;
        not_busy(runtime)?;
        let result = store(&mut inner)?.update(expected, |d| domain::transform(d, &intent));
        record("commit", expected, &result);
        result
    }
    pub fn preview(&self, expected: u64, intent: ChangeIntent) -> Result<ImportPreview, String> {
        if !matches!(
            intent.kind.as_str(),
            "import" | "restore" | "catalog" | "merge"
        ) {
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
            conflict_keys: vec![],
        };
        match domain::transform(&snapshot.document, &intent) {
            Ok(document) => {
                let old = entities(&snapshot.document);
                let new = entities(&document);
                let selected = (intent.kind == "merge").then(|| merge_keys(&intent.payload));
                for (k, v) in &new {
                    if selected.as_ref().is_some_and(|keys| !keys.contains(k)) {
                        continue;
                    }
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
            Err(error) => {
                let key = error
                    .split_once(':')
                    .map_or("configuration", |(_, key)| key);
                result.conflict_keys.push(key.into());
                result.errors.push(ImportError {
                    key: key.into(),
                    error_code: error,
                });
            }
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
        if !confirmed {
            match intent.kind.as_str() {
                "restore" => return Err("SMA_CONFIGURATION_RESTORE_CONFIRMATION_REQUIRED".into()),
                "merge" => return Err("SMA_CONFIGURATION_MERGE_CONFIRMATION_REQUIRED".into()),
                _ => (),
            }
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
        domain::check_full_export(&s.document)?;
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
    for r in [
        "materials",
        "targetApis",
        "mappingValueRules",
        "mappings",
        "httpSources",
    ] {
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
    for source in &d.http_sources {
        if let (Some(key), Some(points)) =
            (source["sourceKey"].as_str(), source["points"].as_array())
        {
            for point in points {
                if let Some(point_key) = point["pointKey"].as_str() {
                    out.insert(format!("httpPoints:{key}:{point_key}"), point.clone());
                }
            }
        }
    }
    if let Some(limits) = &d.runtime_limits {
        out.insert(
            "runtimeLimits".into(),
            serde_json::to_value(limits).unwrap(),
        );
    }
    if let Some(acquisition) = &d.acquisition_loopback {
        out.insert(
            "acquisitionLoopback".into(),
            serde_json::to_value(acquisition).unwrap(),
        );
    }
    out
}

fn merge_keys(payload: &Value) -> std::collections::BTreeSet<String> {
    let Some(patch) = payload.as_object() else {
        return Default::default();
    };
    let mut keys = std::collections::BTreeSet::new();
    for (resource, value) in patch {
        if let (Ok(field), Some(rows)) = (domain::key_field(resource), value.as_array()) {
            for row in rows {
                let Some(id) = row[field].as_str() else {
                    continue;
                };
                keys.insert(format!("{resource}:{id}"));
                if resource == "httpSources" {
                    if let Some(points) = row["points"].as_array() {
                        for point in points.iter().filter_map(|p| p["pointKey"].as_str()) {
                            keys.insert(format!("httpPoints:{id}:{point}"));
                        }
                    }
                }
            }
        } else {
            keys.insert(resource.to_string());
        }
    }
    keys
}

impl LocalConfigurationService {
    pub fn save_acquisition_loopback(
        &self,
        expected: u64,
        config: crate::contracts::acquisition::LoopbackConfig,
    ) -> Result<ConfigurationSnapshot, String> {
        let mut inner = self.lock()?;
        let result = store(&mut inner)?.update(expected, |current| {
            crate::domain::acquisition::require_material(current, &config.material_key)?;
            let mut next = current.clone();
            next.acquisition_loopback = Some(config);
            Ok(next)
        });
        record("acquisition_configuration", expected, &result);
        result
    }
}

impl LocalConfigurationService {
    pub fn with_http_snapshots(
        &self,
        keys: impl FnOnce(&ConfigurationDocument) -> Vec<String>,
    ) -> Result<
        (
            ConfigurationSnapshot,
            Vec<crate::contracts::http_mapping::SourceSnapshot>,
        ),
        String,
    > {
        let mut inner = self.lock()?;
        store(&mut inner)?.with_http_snapshots(keys)
    }

    pub fn publish_http_snapshot(
        &self,
        definition: &Value,
        collected_at: String,
        points: Vec<crate::contracts::http_mapping::PointReading>,
    ) -> Result<crate::contracts::http_mapping::SourceSnapshot, String> {
        let mut inner = self.lock()?;
        store(&mut inner)?.publish_http_snapshot(definition, collected_at, points)
    }
}

#[cfg(test)]
mod http_exchange_tests {
    use super::*;
    use serde_json::json;

    struct Fixture(std::path::PathBuf);

    impl Fixture {
        fn new() -> Self {
            let root = std::env::temp_dir()
                .canonicalize()
                .unwrap()
                .join(format!("sma-r3-exchange-{}", uuid::Uuid::new_v4()));
            std::fs::create_dir(&root).unwrap();
            Self(root)
        }

        fn config(&self) -> LocalConfigurationService {
            LocalConfigurationService::new(Ok(self.0.join("configuration.sqlite3")))
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            std::fs::remove_dir_all(&self.0).unwrap();
        }
    }

    fn merge(payload: Value) -> ChangeIntent {
        ChangeIntent {
            kind: "merge".into(),
            resource: "configuration".into(),
            id: None,
            payload,
        }
    }

    fn source(point_key: &str) -> Value {
        json!({
            "id": "legacy-custom-source-id", "sourceKey": "furnace",
            "name": "Furnace", "url": "http://127.0.0.1:9/acquisition",
            "intervalMs": 1000, "timeoutMs": 500, "enabled": false,
            "points": [{ "pointKey": point_key, "name": point_key, "dataType": "number", "path": "/temperature" }]
        })
    }

    #[test]
    fn portable_merge_preserves_stable_ids_selected_point_changes_and_revision() {
        let profile = Fixture::new();
        let config = profile.config();
        let idle = ManagedRuntimeState::new("portable-exchange");
        let first = merge(json!({"httpSources": [source("primary")]}));
        let preview = config.preview(0, first.clone()).unwrap();
        assert_eq!(
            preview.created_keys,
            ["httpPoints:furnace:primary", "httpSources:furnace"]
        );
        assert_eq!(config.load().unwrap().revision, 0);
        assert_eq!(
            config
                .apply(0, first.clone(), &preview.token, false, &idle)
                .unwrap_err(),
            "SMA_CONFIGURATION_MERGE_CONFIRMATION_REQUIRED"
        );
        config.apply(0, first, &preview.token, true, &idle).unwrap();

        let mut patch_source = source("backup");
        patch_source["points"][0]["dataType"] = json!("boolean");
        let patch = merge(json!({"httpSources":[patch_source]}));
        let preview = config.preview(1, patch.clone()).unwrap();
        assert_eq!(preview.created_keys, ["httpPoints:furnace:backup"]);
        assert_eq!(preview.updated_keys, ["httpSources:furnace"]);
        assert!(preview.unchanged_keys.is_empty());
        let result = config
            .apply(1, patch.clone(), &preview.token, true, &idle)
            .unwrap();
        assert_eq!(
            result.document.http_sources[0]["id"],
            "legacy-custom-source-id"
        );
        assert_eq!(
            result.document.http_sources[0]["points"]
                .as_array()
                .unwrap()
                .len(),
            2
        );
        assert_eq!(profile.config().load().unwrap(), result);
        let unchanged = config.preview(2, patch.clone()).unwrap();
        assert_eq!(
            unchanged.unchanged_keys,
            ["httpPoints:furnace:backup", "httpSources:furnace"]
        );
        let connection = ChangeIntent {
            kind: "connection".into(),
            resource: "connection".into(),
            id: None,
            payload: json!({"scheme":"http","host":"127.0.0.1","port":9}),
        };
        let persisted = config.change(2, connection, &idle).unwrap();
        assert_eq!(
            config
                .apply(2, patch, &unchanged.token, true, &idle)
                .unwrap_err(),
            "SMA_CONFIGURATION_CONFLICT"
        );
        assert_eq!(profile.config().load().unwrap(), persisted);

        let duplicate = config
            .preview(3, merge(json!({"httpSources":[source("a"),source("b")]})))
            .unwrap();
        assert_eq!(duplicate.conflict_keys, ["httpSources:furnace"]);
        let mut wrong_identity = source("a");
        wrong_identity["id"] = json!("different-stable-id");
        let conflict = config
            .preview(3, merge(json!({"httpSources":[wrong_identity]})))
            .unwrap();
        assert_eq!(conflict.conflict_keys, ["httpSources:furnace"]);
        assert_eq!(profile.config().load().unwrap(), persisted);
    }

    #[test]
    fn credentials_are_rejected_in_portable_merge_and_complete_archive() {
        let profile = Fixture::new();
        let config = profile.config();
        let idle = ManagedRuntimeState::new("portable-exchange");
        let mut row = source("primary");
        row["query"] = json!({"access_token":"fixture-placeholder"});
        let rejected = config
            .preview(0, merge(json!({"httpSources":[row.clone()]})))
            .unwrap();
        assert_eq!(rejected.conflict_keys, ["httpSources:furnace"]);
        assert_eq!(config.load().unwrap().revision, 0);

        let upsert = ChangeIntent {
            kind: "upsert".into(),
            resource: "httpSources".into(),
            id: None,
            payload: row,
        };
        assert_eq!(config.change(0, upsert, &idle).unwrap().revision, 1);
        assert_eq!(
            config.export().unwrap_err(),
            "SMA_CONFIGURATION_EXPORT_CREDENTIALS:httpSources:furnace"
        );
        assert_eq!(profile.config().load().unwrap().revision, 1);
    }

    fn apply_catalog(
        config: &LocalConfigurationService,
        operation: Value,
    ) -> ConfigurationSnapshot {
        let intent = ChangeIntent {
            kind: "catalog".into(),
            resource: "catalog".into(),
            id: None,
            payload: json!([{
                "method": "GET", "path": "/fixture", "summary": "Fixture",
                "operationId": "fixture-get", "operationSnapshot": operation,
                "requestContract": [], "bodyTemplate": {}, "normalizationStatus": "ready",
                "normalizationErrorCode": null, "jsonTemplate": "{}",
                "contentHash": "fixture", "sourceLocator": "file:fixture.json"
            }]),
        };
        let preview = config.preview(0, intent.clone()).unwrap();
        assert!(preview.errors.is_empty());
        config
            .apply(
                0,
                intent,
                &preview.token,
                false,
                &ManagedRuntimeState::new("catalog-archive"),
            )
            .unwrap()
    }

    #[test]
    fn catalog_sensitive_parameter_literals_block_complete_archive() {
        let cases = [
            (
                "header example",
                json!({"in":"header","name":"X-API-Key","schema":{"type":"string"},"example":"FIXTURE_DUMMY"}),
            ),
            (
                "query example",
                json!({"in":"query","name":"access_token","schema":{"type":"string"},"example":"FIXTURE_DUMMY"}),
            ),
            (
                "scalar default",
                json!({"in":"header","name":"X-API-Key","schema":{"type":"string","default":"FIXTURE_DUMMY"}}),
            ),
            (
                "nested schema default",
                json!({"in":"query","name":"credential","schema":{"type":"object","properties":{"value":{"type":"string","default":"FIXTURE_DUMMY"}}}}),
            ),
            (
                "nested schema examples",
                json!({"in":"query","name":"credential","schema":{"type":"array","items":{"type":"string","examples":["FIXTURE_DUMMY"]}}}),
            ),
            (
                "named example",
                json!({"in":"header","name":"X-API-Key","schema":{"type":"string"},"examples":{"sample":{"value":"FIXTURE_DUMMY"}}}),
            ),
        ];
        for (case, parameter) in cases {
            let profile = Fixture::new();
            let config = profile.config();
            let saved = apply_catalog(&config, json!({"parameters": [parameter]}));
            assert_eq!(
                config.export().err().as_deref(),
                Some("SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog"),
                "{case}"
            );
            assert_eq!(profile.config().load().unwrap(), saved, "{case}");
        }

        for media_type in [
            json!({"example":{"apiKey":"FIXTURE_DUMMY"}}),
            json!({"examples":{"sample":{"value":{"apiKey":"FIXTURE_DUMMY"}}}}),
        ] {
            let profile = Fixture::new();
            let config = profile.config();
            let saved = apply_catalog(
                &config,
                json!({
                    "responses":{"200":{"content":{"application/json":media_type}}}
                }),
            );
            assert_eq!(
                config.export().err().as_deref(),
                Some("SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog")
            );
            assert_eq!(profile.config().load().unwrap(), saved);
        }
    }

    #[test]
    fn catalog_credential_schema_literals_and_urls_block_complete_archive() {
        let cases = [
            (
                "header enum",
                json!({"parameters":[{"in":"header","name":"X-API-Key","schema":{"type":"string","enum":["FIXTURE_DUMMY"]}}]}),
            ),
            (
                "query const",
                json!({"parameters":[{"in":"query","name":"access_token","schema":{"type":"string","const":"FIXTURE_DUMMY"}}]}),
            ),
            (
                "request property enum",
                json!({"requestBody":{"content":{"application/json":{"schema":{"type":"object","properties":{"apiKey":{"type":"string","enum":["FIXTURE_DUMMY"]}}}}}}}),
            ),
            (
                "response property const",
                json!({"responses":{"200":{"description":"ok","content":{"application/json":{"schema":{"type":"object","properties":{"password":{"type":"string","const":"FIXTURE_DUMMY"}}}}}}}}),
            ),
            (
                "nested object const",
                json!({"requestBody":{"content":{"application/json":{"schema":{"type":"object","const":{"nested":{"password":"FIXTURE_DUMMY"}}}}}}}),
            ),
            (
                "server URL",
                json!({"servers":[{"url":"https://fixture.invalid/base?api_key=FIXTURE_DUMMY"}]}),
            ),
            (
                "scheme-relative authority",
                json!({"servers":[{"url":"//fixture-user:FIXTURE_DUMMY@fixture.invalid/base"}]}),
            ),
            (
                "relative reference",
                json!({"parameters":[{"$ref":"../fixture.json?%61ccess_token=FIXTURE_DUMMY#/components/parameters/Page"}]}),
            ),
            (
                "relative external example",
                json!({"parameters":[{"in":"query","name":"page","schema":{"type":"integer"},"examples":{"fixture":{"externalValue":"./sample.json?signature=FIXTURE_DUMMY"}}}]}),
            ),
            (
                "OpenAPI Link operationRef",
                json!({"responses":{"200":{"description":"ok","links":{"next":{"operationRef":"?api_key=FIXTURE_DUMMY#/paths/~1next/get"}}}}}),
            ),
            (
                "OAuth token URL",
                json!({"components":{"securitySchemes":{"oauth":{"type":"oauth2","flows":{"clientCredentials":{"tokenUrl":"/tokens?client_secret=FIXTURE_DUMMY","scopes":{}}}}}}}),
            ),
            (
                "URL query bearer literal",
                json!({"externalDocs":{"url":"https://fixture.invalid/docs?marker=Bearer%20FIXTURE_DUMMY"}}),
            ),
            (
                "discriminator target reference",
                json!({"components":{"schemas":{"Fixture":{"discriminator":{"propertyName":"kind","mapping":{"foo":"./schema.json?api_key=FIXTURE_DUMMY"}}}}}}),
            ),
        ];
        for (case, operation) in cases {
            let profile = Fixture::new();
            let config = profile.config();
            let saved = apply_catalog(&config, operation);
            assert_eq!(
                config.export().err().as_deref(),
                Some("SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog"),
                "{case}"
            );
            assert_eq!(profile.config().load().unwrap(), saved, "{case}");
        }
    }

    #[test]
    fn catalog_declarations_and_benign_examples_archive_and_restore() {
        let profile = Fixture::new();
        let config = profile.config();
        let saved = apply_catalog(
            &config,
            json!({
                "parameters": [
                    {"in":"query","name":"page","schema":{"type":"integer","default":1,"enum":[1,2,3]},"example":2},
                    {"in":"query","name":"status","schema":{"type":"string","const":"ready"}},
                    {"in":"header","name":"X-API-Key","schema":{"type":"string"},"examples":{"reference":{"$ref":"#/components/examples/runtimeCredential"},"descriptionOnly":{"summary":"Supplied at runtime"}}},
                    {"in":"query","name":"credential","schema":{"type":"object","properties":{"value":{"type":"string"},"default":{"type":"boolean"}}}}
                ],
                "servers":[{"url":"https://fixture.invalid/base?region={region}","variables":{"region":{"default":"test","enum":["test","sample"]}}},{"url":"/another/base"}],
                "externalDocs":{"url":"./guide.html?lang=en#overview"},
                "responses":{"200":{"description":"ok","links":{"next":{"operationRef":"./fixture.json?version=1#/paths/~1next/get"}}}},
                "security": [{"apiKey": []}],
                "components": {"securitySchemes":{"apiKey":{"type":"apiKey","in":"header","name":"X-API-Key"}}}
            }),
        );
        let export = config.export().unwrap();
        let backup: ConfigurationBackup = serde_json::from_str(&export).unwrap();
        assert_eq!(backup.schema_version, 1);
        assert_eq!(backup.document, saved.document);

        let restored_profile = Fixture::new();
        let restored_config = restored_profile.config();
        let intent = ChangeIntent {
            kind: "restore".into(),
            resource: "configuration".into(),
            id: None,
            payload: serde_json::from_str(&export).unwrap(),
        };
        let preview = restored_config.preview(0, intent.clone()).unwrap();
        assert!(preview.errors.is_empty());
        restored_config
            .apply(
                0,
                intent,
                &preview.token,
                true,
                &ManagedRuntimeState::new("catalog-archive"),
            )
            .unwrap();
        assert_eq!(
            restored_profile.config().load().unwrap().document,
            saved.document
        );
    }
}
