//! 薄组合根：DS自有store、通用UUID manager与同一Rust owner；默认空配置且永不自动监听。
use crate::{
    domain::{configuration::*, layout},
    infrastructure::{clock, config_store::Store, logging::Evidence},
    services::{
        configuration::Configuration,
        lifecycle::{Global, Instance},
        owner::Owner,
    },
};
use serde_json::{json, Value};
use std::{
    collections::BTreeMap,
    path::Path,
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    time::Duration,
};
pub struct App {
    pub configuration: Arc<Configuration>,
    pub events: Evidence,
    pub instances: Mutex<BTreeMap<String, Arc<Instance>>>,
    pub accepting: AtomicBool,
    pub global: Arc<Mutex<Global>>,
    pub load_errors: Mutex<BTreeMap<String, String>>,
}
impl App {
    pub fn open(profile: &Path) -> Result<Self, String> {
        Self::open_with_budget(
            profile,
            crate::services::lifecycle::HEADLESS_FIXED_THREADS,
            "headless",
        )
    }
    pub fn open_desktop(profile: &Path) -> Result<Self, String> {
        Self::open_with_budget(
            profile,
            crate::services::lifecycle::DESKTOP_FIXED_THREADS,
            "desktop",
        )
    }
    fn open_with_budget(profile: &Path, fixed_threads: usize, host: &str) -> Result<Self, String> {
        let abi = crate::infrastructure::native_ffi::probe()?;
        let store = Arc::new(Store::open(profile)?);
        let configuration = Arc::new(Configuration::new(store));
        let events = Evidence::default();
        events.put(json!({"event":"native_abi_validated","abi":abi,"nativeFeature":cfg!(feature="native-s7")}));
        let out = Self {
            configuration,
            events,
            accepting: AtomicBool::new(true),
            instances: Mutex::new(BTreeMap::new()),
            global: Arc::new(Mutex::new(Global {
                fixed_threads,
                ..Global::default()
            })),
            load_errors: Mutex::new(BTreeMap::new()),
        };
        out.events.put(json!({"event":"runtime_thread_budget","host":host,"fixedThreads":fixed_threads,"fixedIncludes":"main-process host/SQL/logging/resource/control; owners/listeners/reapers/TCP separate","externalWebKitXpcIncluded":false,"threadLimit":64}));
        for selection in out.configuration.store.selections()? {
            let workspace = out.configuration.store.revision(&selection.revision_id)?;
            let config = workspace
                .instances
                .into_iter()
                .find(|i| i.id == selection.instance_id)
                .ok_or("selected_instance_missing")?;
            match out.create_loaded(config, &selection.revision_id) {
                Ok(instance) => {
                    out.instances
                        .lock()
                        .unwrap()
                        .insert(selection.instance_id, instance);
                }
                Err(error) => {
                    out.load_errors
                        .lock()
                        .unwrap()
                        .insert(selection.instance_id, error);
                }
            }
        }
        Ok(out)
    }
    pub fn create_loaded(
        &self,
        config: InstanceConfig,
        revision: &str,
    ) -> Result<Arc<Instance>, String> {
        let compiled = Arc::new(layout::compile(&config).map_err(|issues| {
            format!(
                "configuration_blocked:{}",
                serde_json::to_string(&issues).unwrap()
            )
        })?);
        let current = self
            .instances
            .lock()
            .unwrap()
            .values()
            .map(|i| i.context.owner.compiled().allocation_upper)
            .sum::<usize>();
        // 全配置草稿/四个SQL等待、活动与构建image/快照及有界日志预留，不外推8×16连接容量。
        if current
            .saturating_add(compiled.allocation_upper)
            .saturating_add(288 * 1024 * 1024)
            > 512 * 1024 * 1024
        {
            return Err("runtime_capacity".into());
        }
        let owner = Owner::new(compiled, revision.into(), self.events.clone())?;
        match Instance::new(owner.clone(), self.global.clone()) {
            Ok(instance) => Ok(Arc::new(instance)),
            Err(e) => {
                owner.shutdown();
                Err(e)
            }
        }
    }
    pub fn instance(&self, id: &str) -> Result<Arc<Instance>, String> {
        self.instances
            .lock()
            .unwrap()
            .get(id)
            .cloned()
            .ok_or("instance_not_loaded".into())
    }
    pub fn snapshot(&self) -> Value {
        let configuration = match self.configuration.get() {
            Ok(value) => value,
            Err(error) => return json!({"errorCode":error,"stale":true}),
        };
        let selections = match self.configuration.store.selections() {
            Ok(v) => v,
            Err(error) => return json!({"errorCode":error,"stale":true}),
        };
        let instances = self.instances.lock().unwrap();
        let errors = self.load_errors.lock().unwrap();
        let rows=configuration.workspace.instances.iter().map(|config|{
            let selection=selections.iter().find(|s|s.instance_id==config.id);
            let mut value=instances.get(&config.id).map(|i|i.snapshot()).unwrap_or_else(||json!({"instanceId":config.id,"state":if errors.contains_key(&config.id){"load_failed"}else{"stopped"},"c":0,"h":0,"tcp":0,"closing":0,"epoch":"0","seq":"0","loadedRevision":null,"protocolWaiting":0,"ruleWaiting":0,"uiWaiting":0}));
            value["name"]=json!(config.name);value["endpoint"]=json!(format!("{}:{}",config.host,config.port));value["savedRevision"]=json!(configuration.latest_revision);value["selectedRevision"]=json!(selection.map(|s|&s.revision_id));value["errorCode"]=json!(errors.get(&config.id));value
        }).collect::<Vec<_>>();
        json!({"instances":rows,"etag":configuration.etag,"stale":false})
    }
    pub fn shutdown(&self) -> bool {
        self.accepting.store(false, Ordering::SeqCst);
        let deadline = clock::ns() + 4_000_000_000;
        let instances = self
            .instances
            .lock()
            .unwrap()
            .values()
            .cloned()
            .collect::<Vec<_>>();
        // 先全体封准入/请求stop，之后共用期限轮询，不能每个实例重新获得5秒。
        let mut requested = true;
        for instance in &instances {
            requested = instance.request_stop() && requested;
        }
        loop {
            let done = instances.iter().map(|i| i.poll_stop()).collect::<Vec<_>>();
            if done.iter().all(|v| *v) {
                break;
            }
            if clock::ns() >= deadline {
                self.events
                    .put(json!({"event":"shutdown_pending","joined":done}));
                return false;
            }
            std::thread::sleep(Duration::from_millis(2));
        }
        let mut joined = true;
        for instance in &instances {
            joined = instance.finish_shutdown() && joined;
        }
        let sql = self.configuration.store.shutdown().is_ok();
        self.events
            .put(json!({"event":"shutdown_joined","instances":joined,"sqliteClosed":sql}));
        requested && joined && sql
    }
    pub fn typed_snapshot(&self) -> Snapshot {
        self.snapshot()
    }
}
pub type Snapshot = Value;
pub type Event = Value;
pub fn command_event(command: &str) -> Event {
    json!({"event":"readonly_ipc","command":command})
}
