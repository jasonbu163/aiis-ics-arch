//! Versioned flow JSON, canonical semantic digest, graph and operand validation.
use serde::{de, Deserialize, Serialize};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::fmt;

pub(crate) const MAX_JSON: usize = 1024 * 1024;
pub(crate) fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub(crate) fn id(s: &str) -> bool {
    let mut bytes = s.bytes();
    s.len() <= 100
        && bytes
            .next()
            .is_some_and(|c| c.is_ascii_alphabetic() || c == b'_')
        && bytes.all(|c| c.is_ascii_alphanumeric() || matches!(c, b'_' | b'-'))
}

struct Checked(Value);
impl<'de> Deserialize<'de> for Checked {
    fn deserialize<D: de::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        struct Strict;
        impl<'de> de::Visitor<'de> for Strict {
            type Value = Checked;
            fn expecting(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                f.write_str("JSON with unique object keys")
            }
            fn visit_bool<E: de::Error>(self, v: bool) -> Result<Checked, E> {
                Ok(Checked(v.into()))
            }
            fn visit_i64<E: de::Error>(self, v: i64) -> Result<Checked, E> {
                Ok(Checked(v.into()))
            }
            fn visit_u64<E: de::Error>(self, v: u64) -> Result<Checked, E> {
                Ok(Checked(v.into()))
            }
            fn visit_f64<E: de::Error>(self, v: f64) -> Result<Checked, E> {
                Ok(Checked(v.into()))
            }
            fn visit_str<E: de::Error>(self, v: &str) -> Result<Checked, E> {
                Ok(Checked(v.into()))
            }
            fn visit_unit<E: de::Error>(self) -> Result<Checked, E> {
                Ok(Checked(Value::Null))
            }
            fn visit_seq<A: de::SeqAccess<'de>>(self, mut a: A) -> Result<Checked, A::Error> {
                let mut v = Vec::new();
                while let Some(Checked(n)) = a.next_element()? {
                    v.push(n);
                }
                Ok(Checked(v.into()))
            }
            fn visit_map<M: de::MapAccess<'de>>(self, mut m: M) -> Result<Checked, M::Error> {
                let mut v = Map::new();
                while let Some((key, Checked(n))) = m.next_entry::<String, Checked>()? {
                    if v.insert(key, n).is_some() {
                        return Err(de::Error::custom("duplicate_key"));
                    }
                }
                Ok(Checked(v.into()))
            }
        }
        d.deserialize_any(Strict)
    }
}
pub(crate) fn checked_json<T: de::DeserializeOwned>(raw: &[u8]) -> Result<T, String> {
    if raw.is_empty() || raw.len() > MAX_JSON {
        return Err("invalid_size".into());
    }
    let parsed =
        serde_json::from_slice::<Checked>(raw).map_err(|e| format!("invalid_json: {e}"))?;
    fn depth(v: &Value, n: usize) -> bool {
        n <= 16
            && match v {
                Value::Object(m) => m.values().all(|v| depth(v, n + 1)),
                Value::Array(a) => a.iter().all(|v| depth(v, n + 1)),
                _ => true,
            }
    }
    if !depth(&parsed.0, 0) {
        return Err("invalid_depth".into());
    }
    // Decode the original bytes to preserve source coordinates in parser errors.
    serde_json::from_slice(raw).map_err(|e| format!("invalid_schema: {e}"))
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Document {
    pub format: String,
    pub schema_version: u32,
    pub flow: Flow,
    #[serde(
        default,
        deserialize_with = "present_layout",
        skip_serializing_if = "Option::is_none"
    )]
    pub layout: Option<Layout>,
}
fn present_layout<'de, D: de::Deserializer<'de>>(d: D) -> Result<Option<Layout>, D::Error> {
    Layout::deserialize(d).map(Some)
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Flow {
    pub flow_id: String,
    pub revision: u32,
    pub trigger: Trigger,
    pub entry_node_id: String,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Trigger {
    #[serde(rename = "type")]
    pub kind: String,
    pub interval_ms: u32,
}
#[derive(Debug, Clone, PartialEq, Serialize)]
pub(crate) struct Node {
    pub id: String,
    pub version: u32,
    #[serde(flatten)]
    pub body: NodeBody,
}
impl<'de> Deserialize<'de> for Node {
    fn deserialize<D: de::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Wire {
            id: String,
            version: u32,
            #[serde(rename = "type")]
            kind: String,
            config: Value,
        }
        let w = Wire::deserialize(d)?;
        let body =
            serde_json::from_value(serde_json::json!({ "type": w.kind, "config": w.config }))
                .map_err(de::Error::custom)?;
        Ok(Self {
            id: w.id,
            version: w.version,
            body,
        })
    }
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "type", content = "config", deny_unknown_fields)]
pub(crate) enum NodeBody {
    #[serde(rename = "plc.read")]
    Read(PlcRead),
    #[serde(rename = "plc.write")]
    Write(PlcWrite),
    #[serde(rename = "condition.compare")]
    Compare(Compare),
    #[serde(rename = "http.request")]
    Http(Http),
    #[serde(rename = "end")]
    End(End),
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct PlcRead {
    pub plc_ref: String,
    pub point_ref: String,
    pub value_type: Kind,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct PlcWrite {
    pub plc_ref: String,
    pub point_ref: String,
    pub value_type: Kind,
    pub value: Operand,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Compare {
    pub left: Operand,
    pub op: Operator,
    pub right: Literal,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum Operator {
    Eq,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Http {
    pub endpoint_ref: String,
    pub method: Method,
    pub path: String,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub query: BTreeMap<String, Operand>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub body: BTreeMap<String, Operand>,
}
#[derive(Debug, Copy, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub(crate) enum Method {
    Get,
    Post,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct End {
    pub result: EndResult,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum EndResult {
    Matched,
    NotMatched,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(untagged)]
pub(crate) enum Operand {
    Ref(Reference),
    Value(Literal),
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Reference {
    pub node_id: String,
    pub field: String,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Literal {
    #[serde(rename = "type")]
    pub kind: Kind,
    pub value: Value,
}
#[derive(Debug, Copy, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum Kind {
    Int16,
    Boolean,
    String,
    Real,
}
impl Kind {
    pub fn valid(self, value: &Value) -> bool {
        match self {
            Self::Int16 => value.as_i64().is_some_and(|n| i16::try_from(n).is_ok()),
            Self::Boolean => value.is_boolean(),
            Self::String => value.as_str().is_some_and(|s| s.len() <= 4096),
            Self::Real => value.as_f64().is_some_and(|n| n.is_finite()),
        }
    }
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Edge {
    pub from_node_id: String,
    pub from_port: String,
    pub to_node_id: String,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Layout {
    pub nodes: BTreeMap<String, Position>,
}
#[derive(Debug, Copy, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Position {
    pub x: f64,
    pub y: f64,
}
#[derive(Debug, Serialize)]
pub(crate) struct Issue {
    pub code: &'static str,
    pub node_id: Option<String>,
}

impl NodeBody {
    pub fn ports(&self) -> &[&'static str] {
        match self {
            Self::Compare(_) => &["true", "false"],
            Self::End(_) => &[],
            _ => &["next"],
        }
    }
    pub fn output(&self, field: &str) -> Option<Kind> {
        match (self, field) {
            (Self::Read(p), "value") => Some(p.value_type),
            (Self::Compare(_), "matched") => Some(Kind::Boolean),
            (Self::Http(_), "status") => Some(Kind::Int16),
            _ => None,
        }
    }
}

pub(crate) fn valid_path(s: &str) -> bool {
    s.starts_with('/')
        && !s.starts_with("//")
        && s.len() <= 1024
        && !s.contains(['\\', '?', '#'])
        && !s.chars().any(char::is_control)
}

/// 统计每条到达路径都经过的上游节点。校验与单节点测试使用相同的端口和路径规则。
struct FlowLinks<'a> {
    incoming: BTreeMap<&'a str, Vec<&'a str>>,
    outgoing: BTreeMap<&'a str, Vec<&'a str>>,
    degrees: BTreeMap<&'a str, usize>,
}
impl<'a> FlowLinks<'a> {
    fn new(nodes: &BTreeMap<&'a str, &NodeBody>) -> Self {
        Self {
            incoming: BTreeMap::new(),
            outgoing: BTreeMap::new(),
            degrees: nodes.keys().map(|&id| (id, 0)).collect(),
        }
    }
    fn add(&mut self, edge: &'a Edge) {
        let from = edge.from_node_id.as_str();
        let to = edge.to_node_id.as_str();
        self.incoming.entry(to).or_default().push(from);
        self.outgoing.entry(from).or_default().push(to);
        *self.degrees.get_mut(to).expect("verified endpoint") += 1;
    }
    fn roots(&self) -> VecDeque<&'a str> {
        self.degrees
            .iter()
            .filter_map(|(&id, &count)| (count == 0).then_some(id))
            .collect()
    }
    fn guaranteed_upstream(mut self) -> BTreeMap<&'a str, BTreeSet<&'a str>> {
        let mut roots = self.roots();
        let mut dominates = BTreeMap::<&'a str, BTreeSet<&'a str>>::new();
        while let Some(n) = roots.pop_front() {
            let mut inherited: Option<BTreeSet<_>> = None;
            for parent in self.incoming.get(n).into_iter().flatten() {
                let mut set = dominates[parent].clone();
                set.insert(*parent);
                inherited = Some(match inherited {
                    None => set,
                    Some(existing) => existing.intersection(&set).copied().collect(),
                });
            }
            dominates.insert(n, inherited.unwrap_or_default());
            for to in self.outgoing.get(n).into_iter().flatten() {
                let d = self.degrees.get_mut(to).expect("verified endpoint");
                *d -= 1;
                if *d == 0 {
                    roots.push_back(to);
                }
            }
        }
        dominates
    }
}
fn valid_edge(nodes: &BTreeMap<&str, &NodeBody>, edge: &Edge) -> bool {
    nodes.contains_key(edge.to_node_id.as_str())
        && nodes
            .get(edge.from_node_id.as_str())
            .is_some_and(|node| node.ports().contains(&edge.from_port.as_str()))
}
impl Flow {
    pub fn guaranteed_upstream_nodes(&self, target: &str) -> BTreeMap<&str, &NodeBody> {
        let nodes: BTreeMap<_, _> = self
            .nodes
            .iter()
            .map(|node| (node.id.as_str(), &node.body))
            .collect();
        let mut links = FlowLinks::new(&nodes);
        for edge in self.edges.iter().filter(|edge| valid_edge(&nodes, edge)) {
            links.add(edge);
        }
        links
            .guaranteed_upstream()
            .remove(target)
            .into_iter()
            .flatten()
            .map(|id| (id, nodes[id]))
            .collect()
    }
}

impl Document {
    pub fn digest(&self) -> String {
        let mut flow = self.flow.clone();
        flow.nodes.sort_by(|a, b| a.id.cmp(&b.id));
        flow.edges.sort_by(|a, b| {
            (&a.from_node_id, &a.from_port, &a.to_node_id).cmp(&(
                &b.from_node_id,
                &b.from_port,
                &b.to_node_id,
            ))
        });
        let mut canonical = serde_json::to_value(flow).expect("typed flow can be serialized");
        canonical
            .as_object_mut()
            .expect("flow map")
            .remove("revision");
        sha(&serde_json::to_vec(&canonical).expect("JSON value can be serialized"))
    }

    pub fn validate(&self) -> Vec<Issue> {
        let mut problems = Vec::new();
        let mut issue = |code, node: Option<&str>| {
            problems.push(Issue {
                code,
                node_id: node.map(str::to_owned),
            })
        };
        let f = &self.flow;
        if self.format != "aiis.flow" || self.schema_version != 1 {
            issue("flow_version", None);
        }
        if !id(&f.flow_id)
            || f.revision == 0
            || f.trigger.kind != "interval"
            || f.trigger.interval_ms == 0
        {
            issue("flow_header", None);
        }
        if f.nodes.is_empty()
            || f.nodes.len() > 256
            || f.edges.len() > 512
            || serde_json::to_vec_pretty(self).map_or(true, |bytes| bytes.len() > MAX_JSON)
        {
            issue("flow_capacity", None);
            return problems;
        }

        let mut nodes = BTreeMap::new();
        for n in &f.nodes {
            if !id(&n.id) || n.version != 1 || nodes.insert(n.id.as_str(), &n.body).is_some() {
                issue("node_identity_version", Some(&n.id));
            }
        }
        if self.layout.as_ref().is_some_and(|layout| {
            layout.nodes.iter().any(|(key, p)| {
                !nodes.contains_key(key.as_str())
                    || !p.x.is_finite()
                    || !p.y.is_finite()
                    || p.x.abs() > 100_000.0
                    || p.y.abs() > 100_000.0
            })
        }) {
            issue("invalid_layout", None);
        }
        let mut outgoing = BTreeMap::<&str, BTreeSet<&str>>::new();
        let mut links = FlowLinks::new(&nodes);
        for e in &f.edges {
            let from = e.from_node_id.as_str();
            let port = e.from_port.as_str();
            if !valid_edge(&nodes, e) {
                issue("edge_endpoint_or_port", Some(from));
                continue;
            }
            if !outgoing.entry(from).or_default().insert(port) {
                issue("duplicate_port", Some(from));
            }
            links.add(e);
        }
        let roots = links.roots();
        if roots.len() != 1 || roots.front().copied() != Some(f.entry_node_id.as_str()) {
            issue("invalid_entry_or_unreachable", None);
        }
        for (&key, body) in &nodes {
            if outgoing.get(key).map_or(0, BTreeSet::len) != body.ports().len() {
                issue("incomplete_ports", Some(key));
            }
        }
        let dominates = links.guaranteed_upstream();
        if dominates.len() != nodes.len() {
            issue("cycle", None);
        }
        for (&n, body) in &nodes {
            let operand = |op: &Operand, expected: Option<Kind>| {
                let kind = match op {
                    Operand::Value(lit) => lit.kind.valid(&lit.value).then_some(lit.kind),
                    Operand::Ref(r) => dominates
                        .get(n)
                        .filter(|d| d.contains(r.node_id.as_str()))
                        .and_then(|_| nodes.get(r.node_id.as_str()))
                        .and_then(|node| node.output(&r.field)),
                };
                kind.is_some() && expected.is_none_or(|need| kind == Some(need))
            };
            let configured = match body {
                NodeBody::Read(p) => id(&p.plc_ref) && id(&p.point_ref),
                NodeBody::Write(p) => {
                    id(&p.plc_ref) && id(&p.point_ref) && operand(&p.value, Some(p.value_type))
                }
                NodeBody::Compare(c) => {
                    operand(&c.left, Some(c.right.kind)) && c.right.kind.valid(&c.right.value)
                }
                NodeBody::Http(h) => {
                    id(&h.endpoint_ref)
                        && valid_path(&h.path)
                        && (h.method == Method::Post || h.body.is_empty())
                        && h.query.len() <= 64
                        && h.body.len() <= 64
                        && h.query
                            .iter()
                            .chain(&h.body)
                            .all(|(k, v)| !k.is_empty() && k.len() <= 100 && operand(v, None))
                }
                NodeBody::End(_) => true,
            };
            if !configured {
                issue("invalid_config_or_reference", Some(n));
            }
        }
        problems
    }
}
