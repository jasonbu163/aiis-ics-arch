//! 文件：src/config/runtime_v2.rs；版本分派、v2闭合结构和只读点引用规范化；不更改旧typed身份。
use super::{
    catalog::{self, Catalog},
    Config, Flow, Http, Plc, Target,
};
use crate::Result;
use serde_json::{json, Value};
use std::{collections::HashSet, path::Path};
#[derive(Debug, Clone, serde::Serialize, PartialEq, Eq, Hash)]
pub struct PointRef {
    pub device_id: String,
    pub point_id: String,
}
#[derive(Debug, Clone)]
pub struct ReadFlow {
    pub id: String,
    pub business_name: String,
    pub interval_ms: u64,
    pub device_ids: Vec<String>,
    pub reads: Vec<PointRef>,
}
#[derive(Debug, Clone)]
pub struct Loaded {
    pub config: Config,
    pub catalogs: Vec<Catalog>,
    pub reads: Vec<ReadFlow>,
}
fn reference(v: &Value) -> Result<PointRef> {
    let m = catalog::object(v, &["device_id", "point_id"], &[])?;
    Ok(PointRef {
        device_id: catalog::identifier(&m["device_id"])?.into(),
        point_id: catalog::identifier(&m["point_id"])?.into(),
    })
}
impl Loaded {
    pub fn load(path: &Path) -> Result<Self> {
        let meta = std::fs::metadata(path).map_err(|_| "config_read")?;
        if !meta.is_file() {
            return Err("config_file".into());
        }
        if meta.len() > 65536 {
            return Err("config_size".into());
        }
        let file = std::fs::File::open(path).map_err(|_| "config_read")?;
        if file.metadata().map_err(|_| "config_read")?.len() > 65536 {
            return Err("config_size".into());
        }
        let mut bytes = Vec::new();
        use std::io::Read;
        file.take(65537)
            .read_to_end(&mut bytes)
            .map_err(|_| "config_read")?;
        if bytes.len() > 65536 {
            return Err("config_size".into());
        }
        #[derive(serde::Deserialize)]
        struct Version {
            schema_version: u64,
        }
        let version: Version = serde_yaml::from_slice(&bytes).map_err(|_| "config_schema")?;
        match Some(version.schema_version) {
            Some(1) => Ok(Self {
                config: Config::load(path)?,
                catalogs: vec![],
                reads: vec![],
            }),
            Some(2) => {
                catalog::check_path(path)?;
                Self::v2(path, &bytes)
            }
            _ => Err("config_version".into()),
        }
    }
    fn v2(path: &Path, b: &[u8]) -> Result<Self> {
        let v = catalog::parse(b, true)?;
        let m = catalog::object(
            &v,
            &[
                "schema_version",
                "instance_id",
                "plc_files",
                "plc_runtime",
                "flows",
                "http",
                "shutdown_timeout_ms",
            ],
            &[],
        )?;
        catalog::integer(&m["schema_version"], 2, 2)?;
        let instance_id = catalog::identifier(&m["instance_id"])?.to_string();
        let base = path.parent().unwrap_or(Path::new("."));
        let mut catalogs = Vec::new();
        let mut paths = HashSet::new();
        let mut ids = HashSet::new();
        let mut endpoints = std::collections::HashMap::new();
        let mut total = 0;
        for file in catalog::array(&m["plc_files"], 1, 4)? {
            let path = catalog::relative(base, catalog::text(file, 255)?)?;
            if !paths.insert(path.clone()) {
                return Err("config_duplicate_path".into());
            }
            let bytes = catalog::read_file(&path, 1048576)?;
            total += bytes.len();
            if total > 4194304 {
                return Err("config_size".into());
            }
            let c = Catalog::from_bytes(&path, &bytes)?;
            if !ids.insert(c.id.clone()) {
                return Err("config_duplicate_device".into());
            }
            if let Some(protocol) = endpoints.insert((c.host.clone(), c.port), c.protocol.clone()) {
                return Err(if protocol == "modbus_tcp" && c.protocol == "modbus_tcp" {
                    "shared_transport_unsupported"
                } else {
                    "config_duplicate_endpoint"
                }
                .into());
            }
            catalogs.push(c);
        }
        let mut plcs = Vec::new();
        let mut budgets = HashSet::new();
        let mut largest = 0;
        for p in catalog::array(&m["plc_runtime"], 1, 4)? {
            let p = catalog::object(
                p,
                &[
                    "device_id",
                    "connect_timeout_ms",
                    "io_timeout_ms",
                    "queue_capacity",
                    "queue_wait_ms",
                    "ready_wait_ms",
                ],
                &[],
            )?;
            let id = catalog::identifier(&p["device_id"])?;
            let c = catalogs
                .iter()
                .find(|c| c.id == id)
                .ok_or("config_device")?;
            if !budgets.insert(id.to_string()) {
                return Err("config_duplicate_device".into());
            }
            let connect = catalog::integer(&p["connect_timeout_ms"], 500, 3000)?;
            let io = catalog::integer(&p["io_timeout_ms"], 500, 5000)?;
            largest = largest.max(connect).max(io);
            plcs.push(Plc {
                id: id.into(),
                host: c.host.clone(),
                port: c.port,
                rack: c.rack,
                slot: c.slot,
                connect_timeout_ms: connect,
                io_timeout_ms: io,
                queue_capacity: catalog::integer(&p["queue_capacity"], 1, 16)? as usize,
                queue_wait_ms: catalog::integer(&p["queue_wait_ms"], 100, 5000)?,
                ready_wait_ms: catalog::integer(&p["ready_wait_ms"], 100, 5000)?,
            });
        }
        if budgets != ids {
            return Err("config_device".into());
        }
        let h = catalog::object(
            &m["http"],
            &[
                "connect_timeout_ms",
                "total_timeout_ms",
                "pool_wait_ms",
                "max_connections",
                "max_body_bytes",
            ],
            &[],
        )?;
        let http = Http {
            connect_timeout_ms: catalog::integer(&h["connect_timeout_ms"], 100, 1500)?,
            total_timeout_ms: catalog::integer(&h["total_timeout_ms"], 100, 5000)?,
            pool_wait_ms: catalog::integer(&h["pool_wait_ms"], 100, 1500)?,
            max_connections: catalog::integer(&h["max_connections"], 1, 8)? as usize,
            max_body_bytes: catalog::integer(&h["max_body_bytes"], 1, 4096)? as usize,
        };
        if http.connect_timeout_ms > http.total_timeout_ms
            || http.pool_wait_ms > http.total_timeout_ms
        {
            return Err("config_http".into());
        }
        let shutdown = catalog::integer(&m["shutdown_timeout_ms"], 5000, 20000)?;
        if shutdown < largest.max(http.total_timeout_ms) + 5500 {
            return Err("config_shutdown".into());
        }
        let mut flows = Vec::new();
        let mut reads = Vec::new();
        let mut flow_ids = HashSet::new();
        let mut targets = Vec::new();
        for f in catalog::array(&m["flows"], 1, 8)? {
            let kind = f["kind"].as_str().ok_or("config_flow_kind_unsupported")?;
            let common = ["id", "kind", "business_name", "interval_ms", "device_ids"];
            let mut required = common.to_vec();
            match kind {
                "demo01" => required.extend(["source_id", "get_url", "input_max_age_ms", "target"]),
                "read_points" => required.push("reads"),
                _ => return Err("config_flow_kind_unsupported".into()),
            }
            let f = catalog::object(f, &required, &[])?;
            let id = catalog::identifier(&f["id"])?.to_string();
            if !flow_ids.insert(id.clone()) {
                return Err("config_duplicate_flow".into());
            }
            let business = catalog::identifier(&f["business_name"])?.to_string();
            let interval = catalog::integer(&f["interval_ms"], 100, 10000)?;
            let mut deps = Vec::new();
            for d in catalog::array(&f["device_ids"], 1, 4)? {
                let id = catalog::identifier(d)?.to_string();
                if !ids.contains(&id) || deps.contains(&id) {
                    return Err("config_device".into());
                }
                deps.push(id);
            }
            let resolve = |r: &PointRef| -> Result<()> {
                if !deps.contains(&r.device_id) {
                    return Err("config_dependency".into());
                }
                let c = catalogs
                    .iter()
                    .find(|c| c.id == r.device_id)
                    .ok_or("config_device")?;
                if c.declared.get(&r.point_id) != Some(&true) {
                    return Err("config_point".into());
                }
                Ok(())
            };
            if kind == "read_points" {
                let mut refs = Vec::new();
                for r in catalog::array(&f["reads"], 1, 16)? {
                    let r = reference(r)?;
                    resolve(&r)?;
                    if refs.contains(&r) {
                        return Err("config_duplicate_read".into());
                    }
                    refs.push(r);
                }
                reads.push(ReadFlow {
                    id,
                    business_name: business,
                    interval_ms: interval,
                    device_ids: deps,
                    reads: refs,
                });
            } else {
                let r = reference(&f["target"])?;
                resolve(&r)?;
                let c = catalogs.iter().find(|c| c.id == r.device_id).unwrap();
                if c.protocol != "s7" {
                    return Err("config_point_protocol".into());
                }
                let p = c.point(&r.point_id)?;
                let source = catalog::identifier(&f["source_id"])?.to_string();
                let url = catalog::text(&f["get_url"], 65536)?.to_string();
                let u = reqwest::Url::parse(&url).map_err(|_| "config_url")?;
                if !matches!(u.scheme(), "http" | "https")
                    || u.host_str().is_none()
                    || !u.username().is_empty()
                    || u.password().is_some()
                    || u.fragment().is_some()
                {
                    return Err("config_url".into());
                }
                let key = (c.host.clone(), c.port, c.rack, c.slot, p.db);
                if targets
                    .iter()
                    .any(|(k, o): &((String, u16, u16, u16, u16), u32)| {
                        *k == key && p.offset < *o + 2 && *o < p.offset + 2
                    })
                {
                    return Err("config_overlap".into());
                }
                targets.push((key, p.offset));
                flows.push(Flow {
                    id,
                    kind: kind.into(),
                    business_name: business,
                    interval_ms: interval,
                    source_id: source,
                    get_url: url,
                    input_max_age_ms: catalog::integer(&f["input_max_age_ms"], 1, 60000)?,
                    target: Target {
                        plc_id: c.id.clone(),
                        db_number: p.db,
                        db_size_bytes: p.size,
                        byte_offset: p.offset,
                        data_type: "INT".into(),
                    },
                });
            }
        }
        Ok(Self {
            config: Config {
                schema_version: 1,
                instance_id,
                plcs,
                flows,
                http,
                shutdown_timeout_ms: shutdown,
            },
            catalogs,
            reads,
        })
    }
    pub fn capability(&self) -> Result<()> {
        if self.catalogs.iter().any(|c| c.protocol == "modbus_tcp") {
            return Err("unsupported_protocol".into());
        }
        for c in &self.catalogs {
            c.capability()?;
        }
        Ok(())
    }
    pub fn report(&self) -> Value {
        let issues: Vec<_> = self
            .catalogs
            .iter()
            .filter_map(|c| {
                c.capability()
                    .err()
                    .map(|e| json!({"error_key":e,"path":c.path}))
            })
            .collect();
        json!({"scope":if self.catalogs.is_empty(){"legacy_main"}else{"main"},"format_valid":true,"runtime_compatible":issues.is_empty(),"files":self.catalogs.iter().map(Catalog::file_summary).collect::<Vec<_>>(),"issues":issues,"issues_truncated":false})
    }
}
pub fn validate(path: &Path, single: bool) -> (Value, i32) {
    let result = if single {
        Catalog::load(path).map(|c|{let issues=c.capability().err().map(|e|vec![json!({"error_key":e,"path":"$.connection"})]).unwrap_or_default();json!({"scope":"plc_file","format_valid":true,"runtime_compatible":issues.is_empty(),"files":[c.file_summary()],"issues":issues,"issues_truncated":false})})
    } else {
        Loaded::load(path).map(|c| c.report())
    };
    match result {
        Ok(v) => (v, 0),
        Err(e) => (
            json!({"scope":if single{"plc_file"}else{"main"},"format_valid":false,"runtime_compatible":false,"files":[],"issues":[{"error_key":e,"path":"$"}],"issues_truncated":false}),
            2,
        ),
    }
}
