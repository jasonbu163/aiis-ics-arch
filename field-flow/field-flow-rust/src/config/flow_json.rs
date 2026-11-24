//! 文件：src/config/flow_json.rs；严格预检并将四节点只读图编译为有类型的单轮配置。
use super::catalog;
use crate::{domain::valid_id, Result};
use reqwest::Url;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{
    collections::{HashMap, HashSet},
    path::Path,
};

#[derive(Debug, Clone)]
pub(crate) struct JsonFlow {
    pub id: String,
    pub revision: u64,
    pub interval_ms: u64,
    pub sha256: String,
    pub file: String,
    pub url: Url,
    pub source_id: String,
    pub max_age_ms: u64,
    pub expected: bool,
}

impl JsonFlow {
    pub fn file_summary(&self) -> Value {
        json!({"file": self.file, "flow_id": self.id, "revision": self.revision, "sha256": self.sha256})
    }
}

struct Endpoint {
    url: Url,
    source_id: String,
    max_age_ms: u64,
}

fn origin(input: &str) -> Result<Url> {
    let (scheme, authority) = input.split_once("://").ok_or("config_flow_url")?;
    let authority = authority.strip_suffix('/').unwrap_or(authority);
    if !matches!(scheme, "http" | "https")
        || authority.contains(['/', '\\', '@', '?', '#'])
        || authority.chars().any(char::is_whitespace)
        || authority.chars().any(char::is_control)
    {
        return Err("config_flow_url".into());
    }
    let url = Url::parse(input).map_err(|_| "config_flow_url")?;
    if url.host_str().is_none() || url.path() != "/" {
        return Err("config_flow_url".into());
    }
    Ok(url)
}

pub(crate) fn load(
    files: &Value,
    bindings: &Value,
    directory: &Path,
    ids: &mut HashSet<String>,
) -> Result<Vec<JsonFlow>> {
    catalog::check_path(directory)?;
    if !directory.is_dir() {
        return Err("config_flow_directory".into());
    }
    let mut endpoints = HashMap::new();
    for value in catalog::array(bindings, 1, 8)? {
        let binding = catalog::object(
            value,
            &["id", "base_url", "source_id", "input_max_age_ms"],
            &[],
        )?;
        let id = catalog::identifier(&binding["id"])?;
        let endpoint = Endpoint {
            url: origin(catalog::text(&binding["base_url"], 65536)?)?,
            source_id: catalog::identifier(&binding["source_id"])?.into(),
            max_age_ms: catalog::integer(&binding["input_max_age_ms"], 1, 60000)?,
        };
        if endpoints.insert(id, endpoint).is_some() {
            return Err("config_flow_duplicate_endpoint".into());
        }
    }
    let mut names = HashSet::new();
    let mut flows = Vec::new();
    for value in catalog::array(files, 1, 8)? {
        let name = value.as_str().ok_or("config_flow_filename")?;
        if !name.strip_suffix(".json").is_some_and(valid_id) {
            return Err("config_flow_filename".into());
        }
        if !names.insert(name) {
            return Err("config_duplicate_path".into());
        }
        let flow = (|| {
            let bytes = catalog::read_file(&directory.join(name), 65536)?;
            compile(name, &bytes, &endpoints)
        })()
        .map_err(|e| match e.split_once(':') {
            Some((key, path)) => format!("{key}:flow_files[{name}].{path}"),
            None => format!("{e}:flow_files[{name}]"),
        })?;
        if !ids.insert(flow.id.clone()) {
            return Err("config_duplicate_flow".into());
        }
        if ids.len() > 8 {
            return Err("config_flow_count".into());
        }
        flows.push(flow);
    }
    Ok(flows)
}

fn at<T>(result: Result<T>, path: &str) -> Result<T> {
    result.map_err(|error| format!("{error}:{path}"))
}

fn compile(file: &str, bytes: &[u8], endpoints: &HashMap<&str, Endpoint>) -> Result<JsonFlow> {
    let json = catalog::parse(bytes, false)?;
    let document = catalog::object(&json, &["format", "schema_version", "flow"], &["layout"])?;
    for (field, valid) in [
        ("format", document["format"] == "aiis.flow"),
        (
            "schema_version",
            document["schema_version"].as_u64() == Some(1),
        ),
    ] {
        if !valid {
            return Err(format!("config_flow_version:{field}"));
        }
    }
    let flow = catalog::object(
        &document["flow"],
        &[
            "flow_id",
            "revision",
            "trigger",
            "entry_node_id",
            "nodes",
            "edges",
        ],
        &[],
    )
    .map_err(|error| {
        if let Some(field) = ["entry_node_id", "edges"]
            .into_iter()
            .find(|field| document["flow"].is_object() && document["flow"].get(*field).is_none())
        {
            format!("{error}:flow.{field}")
        } else {
            format!("{error}:flow")
        }
    })?;
    let id = catalog::identifier(&flow["flow_id"])?;
    let revision = catalog::integer(&flow["revision"], 1, u64::MAX)?;
    let trigger = catalog::object(&flow["trigger"], &["type", "interval_ms"], &[])?;
    if trigger["type"] != "interval" {
        return Err("config_flow_trigger".into());
    }
    let interval_ms = catalog::integer(&trigger["interval_ms"], 100, 10000)?;
    let mut nodes = HashMap::new();
    for (index, value) in flow["nodes"]
        .as_array()
        .ok_or("config_flow_nodes:flow.nodes")?
        .iter()
        .enumerate()
    {
        let path = format!("flow.nodes[{index}]");
        let node = at(
            catalog::object(value, &["id", "type", "version", "config"], &[]),
            &path,
        )?;
        let node_id = at(catalog::identifier(&node["id"]), &format!("{path}.id"))?;
        if node["version"].as_u64() != Some(1) {
            return Err(format!(
                "config_flow_node_version:flow.nodes[{node_id}].version"
            ));
        }
        if !matches!(
            node["type"].as_str(),
            Some("http.request" | "condition.compare" | "end")
        ) {
            return Err(format!("config_flow_node_type:flow.nodes[{node_id}].type"));
        }
        if nodes.insert(node_id, node).is_some() {
            return Err(format!("config_flow_duplicate_node:{path}.id"));
        }
    }
    if nodes.len() != 4 {
        return Err("config_flow_nodes:flow.nodes".into());
    }
    if let Some(layout) = document.get("layout") {
        let layout = catalog::object(layout, &["nodes"], &[])?;
        for (key, value) in layout["nodes"].as_object().ok_or("config_flow_layout")? {
            let coords = catalog::object(value, &["x", "y"], &[])?;
            if !nodes.contains_key(key.as_str())
                || !coords
                    .values()
                    .all(|n| n.as_f64().is_some_and(f64::is_finite))
            {
                return Err("config_flow_layout".into());
            }
        }
    }

    let mut edges = HashMap::new();
    for (index, value) in at(catalog::array(&flow["edges"], 0, 3), "flow.edges")?
        .iter()
        .enumerate()
    {
        let path = format!("flow.edges[{index}]");
        let edge = at(
            catalog::object(value, &["from_node_id", "from_port", "to_node_id"], &[]),
            &path,
        )?;
        let from_path = format!("{path}.from_node_id");
        let from = at(catalog::identifier(&edge["from_node_id"]), &from_path)?;
        let source = nodes
            .get(from)
            .ok_or_else(|| format!("config_flow_edge:{from_path}"))?;
        let to_path = format!("{path}.to_node_id");
        let to = at(catalog::identifier(&edge["to_node_id"]), &to_path)?;
        if !nodes.contains_key(to) {
            return Err(format!("config_flow_edge:{to_path}"));
        }
        let port = edge["from_port"].as_str().unwrap_or_default();
        if !matches!(
            (source["type"].as_str(), port),
            (Some("http.request"), "next") | (Some("condition.compare"), "true" | "false")
        ) || edges.insert((from, port), (index, to)).is_some()
        {
            return Err(format!("config_flow_edge:{path}.from_port"));
        }
    }

    let entry = at(
        catalog::identifier(&flow["entry_node_id"]),
        "flow.entry_node_id",
    )?;
    let node_config = |node_id, kind: &str, path: &str| -> Result<&Value> {
        let node = nodes
            .get(node_id)
            .ok_or_else(|| format!("config_flow_node:{path}"))?;
        if node["type"] != kind {
            return Err(format!("config_flow_node_type:{path}"));
        }
        Ok(&node["config"])
    };
    let http_path = format!("flow.nodes[{entry}].config");
    let http = at(
        catalog::object(
            node_config(entry, "http.request", "flow.entry_node_id")?,
            &["endpoint_ref", "method", "path", "query"],
            &[],
        ),
        &http_path,
    )?;
    if http["method"] != "GET" {
        return Err(format!("config_flow_http:{http_path}.method"));
    }
    if !http["query"].as_object().is_some_and(|v| v.is_empty()) {
        return Err(format!("config_flow_http:{http_path}.query"));
    }
    let binding_path = format!("{http_path}.endpoint_ref");
    let endpoint = endpoints
        .get(at(
            catalog::identifier(&http["endpoint_ref"]),
            &binding_path,
        )?)
        .ok_or_else(|| format!("config_flow_endpoint:{binding_path}"))?;
    let path = at(
        catalog::text(&http["path"], 65536),
        &format!("{http_path}.path"),
    )?;
    if !path.starts_with('/')
        || path.contains("//")
        || path.contains("..")
        || path.contains(['\\', '%', '?', '#'])
        || path.chars().any(char::is_control)
    {
        return Err(format!("config_flow_path:{http_path}.path"));
    }
    let mut url = endpoint.url.clone();
    url.set_path(path);

    // Exactly three required edges and four distinct typed nodes prove reachability and termination.
    let edge = |from, port| {
        edges
            .get(&(from, port))
            .copied()
            .ok_or_else(|| format!("config_flow_edge:flow.nodes[{from}].outputs[{port}]"))
    };
    let (index, check) = edge(entry, "next")?;
    let check_path = format!("flow.nodes[{check}].config");
    let condition = at(
        catalog::object(
            node_config(
                check,
                "condition.compare",
                &format!("flow.edges[{index}].to_node_id"),
            )?,
            &["left", "op", "right"],
            &[],
        ),
        &check_path,
    )?;
    let left = at(
        catalog::object(&condition["left"], &["node_id", "field"], &[]),
        &format!("{check_path}.left"),
    )?;
    let right = at(
        catalog::object(&condition["right"], &["type", "value"], &[]),
        &format!("{check_path}.right"),
    )?;
    for (field, valid) in [
        ("op", condition["op"] == "eq"),
        ("left.node_id", left["node_id"] == entry),
        ("left.field", left["field"] == "ready"),
        ("right.type", right["type"] == "bool"),
    ] {
        if !valid {
            return Err(format!("config_flow_condition:{check_path}.{field}"));
        }
    }
    let expected = right["value"]
        .as_bool()
        .ok_or_else(|| format!("config_flow_condition:{check_path}.right.value"))?;
    let mut previous_terminal = None;
    for (port, result) in [("true", "matched"), ("false", "not_matched")] {
        let (index, terminal) = edge(check, port)?;
        let to_path = format!("flow.edges[{index}].to_node_id");
        if previous_terminal.replace(terminal) == Some(terminal) {
            return Err(format!("config_flow_terminal:{to_path}"));
        }
        let terminal_path = format!("flow.nodes[{terminal}].config");
        let config = at(
            catalog::object(node_config(terminal, "end", &to_path)?, &["result"], &[]),
            &terminal_path,
        )?;
        if config["result"] != result {
            return Err(format!("config_flow_terminal:{terminal_path}.result"));
        }
    }

    Ok(JsonFlow {
        id: id.into(),
        revision,
        interval_ms,
        file: file.into(),
        url,
        source_id: endpoint.source_id.clone(),
        max_age_ms: endpoint.max_age_ms,
        expected,
        sha256: format!("{:x}", Sha256::digest(bytes)),
    })
}
