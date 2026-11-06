//! 固定plc-facts/v1载体、原轮校验、无损固定分片及域摘要；原UTF-8永不重编码。
use super::facts_canonical::{self as pf, Result};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
pub(crate) const REQUEST_MAX: usize = 4 * 1024 * 1024;
pub(crate) const RECEIPT_MAX: usize = 8 * 1024 * 1024;
macro_rules! wire {($name:ident {$($field:ident:$ty:ty),*$(,)?})=>{#[derive(Clone,Debug,Serialize,Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]pub(crate) struct $name{$(pub $field:$ty),*}}}
wire!(Parent {
    batch_id: String,
    request_digest: String,
    rejection_token: String
});
wire!(TransportPart{part:u32,point_ids:Vec<String>,content_digest:String});
wire!(TransportSample{sample_id:String,db_number:u16,source_sha256:String,parts:Vec<TransportPart>});
wire!(Cycle{cycle_id:String,manifest_utf8:String,manifest_sha256:String,context_utf8:String,context_sha256:String,transport_manifest:Vec<TransportSample>});
wire!(Part{sample_id:String,cycle_id:String,part:u32,parts:u32,point_ids:Vec<String>,payload_utf8:String,source_sha256:String,content_digest:String});
wire!(Batch{contract_version:String,source_profile:String,digest_profile:String,instance_id:String,batch_id:String,batch_created_at:String,request_digest:String,parent:Option<Parent>,cycles:Vec<Cycle>,samples:Vec<Part>});
#[derive(Clone, Debug)]
pub(crate) struct BuiltCycle {
    pub cycle: Cycle,
    pub parts: Vec<Part>,
    pub plc_id: String,
    pub group_id: String,
    pub source_seq: i64,
    pub definition_set_digest: String,
    pub source_generation: String,
}
pub(crate) fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v.get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| "invalid_source".into())
}
pub(crate) fn id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 128
        && value.trim() == value
        && !value.chars().any(|c| c < ' ' || c == '\u{7f}')
}
pub(crate) fn time(value: &str) -> Result<chrono::DateTime<chrono::FixedOffset>> {
    let bytes = value.as_bytes();
    if bytes.len() < 25 || bytes.len() > 35 || !value.ends_with("+08:00") {
        return Err("invalid_time".into());
    }
    for (index, &byte) in bytes[..19].iter().enumerate() {
        let valid = match index {
            4 | 7 => byte == b'-',
            10 => byte == b'T' || byte == b't',
            13 | 16 => byte == b':',
            _ => byte.is_ascii_digit(),
        };
        if !valid {
            return Err("invalid_time".into());
        }
    }
    let fraction = &bytes[19..bytes.len() - 6];
    if (!fraction.is_empty()
        && (fraction.len() < 2
            || fraction.len() > 10
            || fraction[0] != b'.'
            || !fraction[1..].iter().all(u8::is_ascii_digit)))
        || bytes[0] == b'0'
        || (bytes[17] - b'0') * 10 + bytes[18] - b'0' > 59
    {
        return Err("invalid_time".into());
    }
    chrono::DateTime::parse_from_rfc3339(value).map_err(|_| "invalid_time".into())
}
pub(crate) fn wire_time(value: &str) -> Result<String> {
    let at = time(value)?;
    Ok(at.format("%Y-%m-%dT%H:%M:%S%.9f%:z").to_string())
}
fn array<'a>(v: &'a Value, key: &str) -> Result<&'a Vec<Value>> {
    v[key].as_array().ok_or_else(|| "invalid_source".into())
}
fn keys_exact(v: &Value, keys: &[&str]) -> Result<()> {
    if v.as_object()
        .map(|m| m.len() == keys.len() && keys.iter().all(|k| m.contains_key(*k)))
        != Some(true)
    {
        return Err("invalid_source".into());
    }
    Ok(())
}
fn map_ids(v: &Value, key: &str) -> Result<BTreeMap<String, Value>> {
    let mut map = BTreeMap::new();
    for row in array(v, key)? {
        let k = text(row, "id")?;
        if !id(k) || map.insert(k.into(), row.clone()).is_some() {
            return Err("invalid_source".into());
        }
    }
    if map.len() > 4096 {
        return Err("payload_too_large".into());
    }
    Ok(map)
}
pub(crate) fn definition_object(d: &Value) -> Result<Value> {
    let mut out = serde_json::Map::new();
    for k in [
        "id",
        "plcId",
        "dbId",
        "sourcePath",
        "name",
        "nameMode",
        "dataType",
        "enabled",
        "groupId",
    ] {
        out.insert(k.into(), d.get(k).cloned().unwrap_or(Value::Null));
    }
    out.insert(
        "address".into(),
        if d["address"].is_null() {
            Value::Null
        } else {
            let a = &d["address"];
            json!({"offset":a["offset"],"bit":a["bit"],"confirmed":a["confirmed"]})
        },
    );
    Ok(Value::Object(out))
}
pub(crate) fn definitions(
    context: &Value,
    plc_id: &str,
) -> Result<(BTreeMap<String, (Value, u16, bool)>, String)> {
    if context["schemaVersion"] != 1 {
        return Err("invalid_source".into());
    }
    let plcs = map_ids(context, "plcs")?;
    let dbs = map_ids(context, "dbs")?;
    let groups = map_ids(context, "groups")?;
    let points = map_ids(context, "points")?;
    let plc = plcs.get(plc_id).ok_or("invalid_source")?;
    let enabled = plc["enabled"].as_bool().ok_or("invalid_source")?;
    let mut out = BTreeMap::new();
    let mut entries = vec![];
    for (pid, p) in points {
        if p["plcId"] != plc_id {
            continue;
        }
        let db = dbs.get(text(&p, "dbId")?).ok_or("invalid_source")?;
        let number = db["number"]
            .as_u64()
            .filter(|n| *n > 0 && *n <= 65535)
            .ok_or("invalid_source")? as u16;
        if db["plcId"] != plc_id {
            return Err("invalid_source".into());
        }
        let group = groups.get(p["groupId"].as_str().unwrap_or(""));
        let ge = match group {
            Some(g) => {
                if g["plcId"] != plc_id {
                    return Err("invalid_source".into());
                }
                g["enabled"].as_bool().ok_or("invalid_source")?
            }
            None => false,
        };
        definition_check(&p)?;
        let definition = pf::digest("definition", &definition_object(&p)?)?;
        entries.push(json!({"pointId":pid,"dbNumber":number,"groupEnabled":ge,"definitionDigest":definition}));
        out.insert(pid, (p, number, ge));
    }
    let digest = pf::digest(
        "definition-set",
        &json!({"plcId":plc_id,"plcEnabled":enabled,"points":entries}),
    )?;
    Ok((out, digest))
}
pub(crate) fn fixed_parts(points: &Value) -> Result<Vec<Vec<String>>> {
    let source = points.as_object().ok_or("invalid_source")?;
    let mut parts = vec![];
    let mut current = serde_json::Map::new();
    for (key, value) in source {
        current.insert(key.clone(), value.clone());
        if current.len() > 512 || pf::canonical(&Value::Object(current.clone()))?.len() > 128 * 1024
        {
            current.remove(key);
            if current.is_empty() {
                return Err("payload_too_large".into());
            }
            parts.push(current.keys().cloned().collect());
            current = serde_json::Map::new();
            current.insert(key.clone(), value.clone());
            if pf::canonical(&Value::Object(current.clone()))?.len() > 128 * 1024 {
                return Err("payload_too_large".into());
            }
        }
    }
    if !current.is_empty() {
        parts.push(current.keys().cloned().collect());
    }
    if parts.is_empty() || parts.len() > 16 {
        return Err("payload_too_large".into());
    }
    Ok(parts)
}
fn projection(p: &Value, part: u32, parts: u32, ids: &[String], sha: &str) -> Result<Value> {
    let mut out = p.as_object().ok_or("invalid_source")?.clone();
    out.remove("schemaVersion");
    let revision = out.remove("revision").ok_or("invalid_source")?;
    out.insert("configRevision".into(), revision);
    out.insert("sourceSha256".into(), json!(sha));
    out.insert("part".into(), json!(part));
    out.insert("parts".into(), json!(parts));
    for key in ["startedAt", "finishedAt", "savedAt"] {
        out.insert(key.into(), json!(wire_time(text(p, key)?)?));
    }
    let mut selected = serde_json::Map::new();
    for id in ids {
        let mut fact = p["points"][id].clone();
        fact["observedAt"] = json!(wire_time(text(&fact, "observedAt")?)?);
        selected.insert(id.clone(), fact);
    }
    out.insert("points".into(), Value::Object(selected));
    Ok(Value::Object(out))
}
fn definition_check(d: &Value) -> Result<()> {
    let mut keys = vec![
        "id",
        "plcId",
        "dbId",
        "sourcePath",
        "name",
        "dataType",
        "comment",
        "enabled",
        "groupId",
        "address",
    ];
    if d.get("nameMode").is_some() {
        keys.push("nameMode")
    }
    keys_exact(d, &keys)?;
    for key in ["id", "plcId", "dbId"] {
        if !id(text(d, key)?) {
            return Err("invalid_source".into());
        }
    }
    if !d["groupId"].is_null() && !d["groupId"].as_str().map(id).unwrap_or(false) {
        return Err("invalid_source".into());
    }
    if !d["enabled"].is_boolean() {
        return Err("invalid_source".into());
    }
    if !d["address"].is_null() {
        let a = &d["address"];
        keys_exact(a, &["offset", "bit", "confirmed", "origin", "reason"])?;
        if a["offset"].as_u64().filter(|n| *n <= 65535).is_none()
            || !a["confirmed"].is_boolean()
            || (!a["bit"].is_null() && a["bit"].as_u64().filter(|n| *n <= 7).is_none())
        {
            return Err("invalid_source".into());
        }
        text(a, "origin")?;
        text(a, "reason")?;
    }
    Ok(())
}
pub(crate) fn value_check(f: &Value) -> Result<()> {
    keys_exact(
        f,
        &["definition", "value", "observedAt", "quality", "reason"],
    )?;
    let d = &f["definition"];
    definition_check(d)?;
    let typ = text(d, "dataType")?;
    let value = &f["value"];
    for (key, max) in [("sourcePath", 2048), ("name", 512), ("comment", 4096)] {
        if text(d, key)?.len() > max {
            return Err("payload_too_large".into());
        }
    }
    if let Some(mode) = d.get("nameMode") {
        if !["pending", "auto_path", "auto_address", "manual"]
            .iter()
            .any(|s| mode == s)
        {
            return Err("invalid_source".into());
        }
    }
    let string_max = typ
        .strip_prefix("STRING[")
        .and_then(|x| x.strip_suffix(']'))
        .and_then(|x| x.parse::<usize>().ok())
        .filter(|n| *n > 0 && *n <= 254);
    let width = match typ {
        "BOOL" | "BYTE" | "USINT" | "CHAR" => Some(1),
        "INT" | "UINT" | "WORD" => Some(2),
        "DINT" | "UDINT" | "DWORD" | "REAL" => Some(4),
        _ => string_max.map(|n| n + 2),
    };
    let address = &d["address"];
    if !address.is_null() {
        let off = address["offset"].as_u64().ok_or("invalid_source")?;
        if off + width.unwrap_or(1) as u64 > 65536
            || (typ == "BOOL" && address["bit"].as_u64().filter(|n| *n <= 7).is_none())
            || (typ != "BOOL" && !address["bit"].is_null())
        {
            return Err("invalid_source".into());
        }
    }
    if f["quality"] == "bad" {
        let reason = text(f, "reason")?;
        if !value.is_null()
            || reason.is_empty()
            || reason.len() > 128
            || (width.is_none() && reason != "unsupported_type")
        {
            return Err("invalid_source".into());
        }
        return Ok(());
    }
    if f["quality"] != "good"
        || !f["reason"].is_null()
        || address["confirmed"] != true
        || width.is_none()
    {
        return Err("invalid_source".into());
    }
    let valid = match typ {
        "BOOL" => value.is_boolean(),
        "BYTE" | "USINT" => value.as_u64().map(|n| n <= 255).unwrap_or(false),
        "INT" => value
            .as_i64()
            .map(|n| (-32768..=32767).contains(&n))
            .unwrap_or(false),
        "UINT" | "WORD" => value.as_u64().map(|n| n <= 65535).unwrap_or(false),
        "DINT" => value
            .as_i64()
            .map(|n| (-2147483648..=2147483647).contains(&n))
            .unwrap_or(false),
        "UDINT" | "DWORD" => value.as_u64().map(|n| n <= 4294967295).unwrap_or(false),
        "REAL" => {
            if let Value::Number(n) = value {
                let n = pf::decimal(&n.to_string())?;
                let n = n.trim_start_matches('-');
                n == "0"
                    || (compare_decimal(n, "340282346638528860000000000000000000000") <= 0
                        && compare_decimal(
                            n,
                            "0.000000000000000000000000000000000000000000001401298464324817",
                        ) >= 0)
            } else {
                false
            }
        }
        _ => value
            .as_str()
            .map(|s| {
                s.is_ascii()
                    && if typ == "CHAR" {
                        s.len() == 1
                    } else {
                        s.len() <= string_max.unwrap_or(0)
                    }
            })
            .unwrap_or(false),
    };
    if valid {
        Ok(())
    } else {
        Err("invalid_source".into())
    }
}
fn compare_decimal(a: &str, b: &str) -> i8 {
    let mut a = a.split('.');
    let mut b = b.split('.');
    let ai = a.next().unwrap();
    let bi = b.next().unwrap();
    let integer = ai.len().cmp(&bi.len()).then(ai.cmp(bi));
    if !integer.is_eq() {
        return if integer.is_lt() { -1 } else { 1 };
    }
    let af = a.next().unwrap_or("");
    let bf = b.next().unwrap_or("");
    for i in 0..af.len().max(bf.len()) {
        let x = af.as_bytes().get(i).unwrap_or(&b'0');
        let y = bf.as_bytes().get(i).unwrap_or(&b'0');
        if x != y {
            return if x < y { -1 } else { 1 };
        }
    }
    0
}
pub(crate) fn build_cycle(
    instance: &str,
    manifest_raw: &str,
    manifest_sha: &str,
    context_raw: &str,
    context_sha: &str,
    payloads: &[(String, String)],
) -> Result<BuiltCycle> {
    if pf::sha(manifest_raw.as_bytes()) != format!("sha256:{manifest_sha}")
        || pf::sha(context_raw.as_bytes()) != format!("sha256:{context_sha}")
    {
        return Err("digest_mismatch".into());
    }
    let m = pf::parse(manifest_raw.as_bytes(), 128 * 1024)?;
    keys_exact(
        &m,
        &[
            "schemaVersion",
            "cycleId",
            "plcId",
            "sourceGeneration",
            "sourceSeq",
            "groupId",
            "revision",
            "startedAt",
            "finishedAt",
            "savedAt",
            "expectedPointIds",
            "reads",
            "samples",
        ],
    )?;
    for key in [
        "cycleId",
        "plcId",
        "sourceGeneration",
        "groupId",
        "revision",
    ] {
        if !id(text(&m, key)?) {
            return Err("invalid_source".into());
        }
    }
    let context = pf::parse(context_raw.as_bytes(), 1024 * 1024)?;
    let plc = text(&m, "plcId")?;
    let group = text(&m, "groupId")?;
    let cycle_id = text(&m, "cycleId")?;
    let generation = text(&m, "sourceGeneration")?;
    let seq = text(&m, "sourceSeq")?;
    let source_seq = seq.parse::<i64>().map_err(|_| "invalid_source")?;
    if source_seq <= 0
        || source_seq >= i64::MAX
        || source_seq.to_string() != seq
        || m["schemaVersion"] != 2
    {
        return Err("invalid_source".into());
    }
    if time(text(&m, "startedAt")?)? > time(text(&m, "finishedAt")?)?
        || time(text(&m, "finishedAt")?)? > time(text(&m, "savedAt")?)?
    {
        return Err("invalid_time".into());
    }
    let reads = array(&m, "reads")?;
    for r in reads {
        keys_exact(
            r,
            &[
                "dbNumber",
                "start",
                "size",
                "startedAt",
                "finishedAt",
                "durationMs",
                "quality",
            ],
        )?;
        let db = r["dbNumber"]
            .as_u64()
            .filter(|n| *n > 0 && *n <= 65535)
            .ok_or("invalid_source")?;
        let start = r["start"]
            .as_u64()
            .filter(|n| *n <= 65535)
            .ok_or("invalid_source")?;
        let size = r["size"]
            .as_u64()
            .filter(|n| *n > 0 && *n <= 65536)
            .ok_or("invalid_source")?;
        if start + size > 65536
            || r["durationMs"]
                .as_u64()
                .filter(|n| *n <= 9007199254740991)
                .is_none()
            || !["good", "bad"].iter().any(|s| r["quality"] == *s)
            || time(text(r, "startedAt")?)? < time(text(&m, "startedAt")?)?
            || time(text(r, "finishedAt")?)? > time(text(&m, "finishedAt")?)?
            || time(text(r, "startedAt")?)? > time(text(r, "finishedAt")?)?
            || db == 0
        {
            return Err("invalid_source".into());
        }
    }
    let (defs, definition_set_digest) = definitions(&context, plc)?;
    let expected = defs
        .iter()
        .filter(|(_, (d, _, ge))| *ge && d["enabled"] == true && d["groupId"] == group)
        .map(|(k, _)| k.clone())
        .collect::<BTreeSet<_>>();
    let original = array(&m, "expectedPointIds")?
        .iter()
        .map(|x| x.as_str().map(str::to_string).ok_or("invalid_source"))
        .collect::<std::result::Result<Vec<_>, _>>()?;
    if original.len() > 4096
        || original.len() != expected.len()
        || original.iter().cloned().collect::<BTreeSet<_>>() != expected
        || expected.is_empty()
    {
        return Err("invalid_source".into());
    }
    let samples = array(&m, "samples")?;
    if samples.len() > 128 || samples.len() != payloads.len() || samples.is_empty() {
        return Err("invalid_source".into());
    }
    for sample in samples {
        keys_exact(sample, &["sampleId", "dbNumber", "sha256"])?;
    }
    let mut transport = vec![];
    let mut parts = vec![];
    let mut covered = BTreeSet::new();
    let mut db_seen = BTreeSet::new();
    let mut sample_seen = BTreeSet::new();
    for (raw, hash) in payloads {
        if pf::sha(raw.as_bytes()) != format!("sha256:{hash}") {
            return Err("digest_mismatch".into());
        }
        let p = pf::parse(raw.as_bytes(), 512 * 1024)?;
        keys_exact(
            &p,
            &[
                "schemaVersion",
                "sampleId",
                "cycleId",
                "instanceId",
                "plcId",
                "sourceGeneration",
                "sourceSeq",
                "groupId",
                "revision",
                "dbNumber",
                "origin",
                "startedAt",
                "finishedAt",
                "savedAt",
                "points",
            ],
        )?;
        if !id(text(&p, "sampleId")?)
            || !id(text(&p, "instanceId")?)
            || text(&p, "origin")?.is_empty()
            || text(&p, "origin")?.len() > 64
        {
            return Err("invalid_source".into());
        }
        let sid = text(&p, "sampleId")?;
        if p["schemaVersion"] != 2
            || p["instanceId"] != instance
            || !sample_seen.insert(sid.to_string())
        {
            return Err("invalid_source".into());
        }
        for key in [
            "cycleId",
            "plcId",
            "sourceGeneration",
            "sourceSeq",
            "groupId",
            "revision",
            "startedAt",
            "finishedAt",
            "savedAt",
        ] {
            if p[key] != m[key] {
                return Err("invalid_source".into());
            }
        }
        let db = p["dbNumber"]
            .as_u64()
            .filter(|n| *n > 0 && *n <= 65535)
            .ok_or("invalid_source")? as u16;
        if !db_seen.insert(db)
            || !samples
                .iter()
                .any(|s| s["sampleId"] == sid && s["sha256"] == *hash && s["dbNumber"] == db)
        {
            return Err("invalid_source".into());
        }
        for (pid, f) in p["points"].as_object().ok_or("invalid_source")? {
            let (d, number, ge) = defs.get(pid).ok_or("invalid_source")?;
            if !*ge
                || *number != db
                || d["enabled"] != true
                || d["groupId"] != group
                || d != &f["definition"]
                || !covered.insert(pid.clone())
            {
                return Err("invalid_source".into());
            }
            value_check(f)?;
            let observed = time(text(f, "observedAt")?)?;
            if observed < time(text(&p, "startedAt")?)? || observed > time(text(&p, "finishedAt")?)?
            {
                return Err("invalid_time".into());
            }
        }
        let mut normalized_points = p["points"].clone();
        for fact in normalized_points
            .as_object_mut()
            .ok_or("invalid_source")?
            .values_mut()
        {
            fact["observedAt"] = json!(wire_time(text(fact, "observedAt")?)?);
        }
        let grouping = fixed_parts(&normalized_points)?;
        let count = grouping.len() as u32;
        let source_sha = format!("sha256:{hash}");
        let mut tp = vec![];
        for (i, ids) in grouping.into_iter().enumerate() {
            let part = i as u32 + 1;
            let digest = pf::digest(
                "sample-part",
                &projection(&p, part, count, &ids, &source_sha)?,
            )?;
            tp.push(TransportPart {
                part,
                point_ids: ids.clone(),
                content_digest: digest.clone(),
            });
            parts.push(Part {
                sample_id: sid.into(),
                cycle_id: cycle_id.into(),
                part,
                parts: count,
                point_ids: ids,
                payload_utf8: raw.clone(),
                source_sha256: source_sha.clone(),
                content_digest: digest,
            });
        }
        transport.push(TransportSample {
            sample_id: sid.into(),
            db_number: db,
            source_sha256: source_sha,
            parts: tp,
        });
    }
    if covered != expected {
        return Err("invalid_source".into());
    }
    transport.sort_by(|a, b| a.sample_id.as_bytes().cmp(b.sample_id.as_bytes()));
    parts.sort_by(|a, b| a.sample_id.cmp(&b.sample_id).then(a.part.cmp(&b.part)));
    Ok(BuiltCycle {
        cycle: Cycle {
            cycle_id: cycle_id.into(),
            manifest_utf8: manifest_raw.into(),
            manifest_sha256: format!("sha256:{manifest_sha}"),
            context_utf8: context_raw.into(),
            context_sha256: format!("sha256:{context_sha}"),
            transport_manifest: transport,
        },
        parts,
        plc_id: plc.into(),
        group_id: group.into(),
        source_seq,
        definition_set_digest,
        source_generation: generation.into(),
    })
}
pub(crate) fn cycle_digest(c: &Cycle) -> Result<String> {
    pf::digest(
        "cycle",
        &json!({"manifestSha256":c.manifest_sha256,"contextSha256":c.context_sha256,"transportManifest":c.transport_manifest}),
    )
}
impl Batch {
    pub fn new(
        instance: String,
        batch_id: String,
        at: String,
        cycles: Vec<Cycle>,
        samples: Vec<Part>,
        parent: Option<Parent>,
    ) -> Result<Self> {
        let mut batch = Self {
            contract_version: "plc-facts/v1".into(),
            source_profile: "daa-local/v2".into(),
            digest_profile: "pf-json/v1".into(),
            instance_id: instance,
            batch_id,
            batch_created_at: wire_time(&at)?,
            request_digest: String::new(),
            parent,
            cycles,
            samples,
        };
        batch.cycles.sort_by(|a, b| a.cycle_id.cmp(&b.cycle_id));
        batch
            .samples
            .sort_by(|a, b| a.sample_id.cmp(&b.sample_id).then(a.part.cmp(&b.part)));
        batch.request_digest = batch.digest()?;
        batch.bytes()?;
        Ok(batch)
    }
    pub fn digest(&self) -> Result<String> {
        let mut v = serde_json::to_value(self).map_err(|_| "encoding_failed")?;
        v.as_object_mut().unwrap().remove("requestDigest");
        v["batchCreatedAt"] = json!(wire_time(&self.batch_created_at)?);
        pf::digest("batch", &v)
    }
    pub fn bytes(&self) -> Result<String> {
        if self.cycles.is_empty()
            || self.cycles.len() > 16
            || self.samples.is_empty()
            || self.samples.len() > 32
        {
            return Err("payload_too_large".into());
        }
        let v = serde_json::to_value(self).map_err(|_| "encoding_failed")?;
        let bytes = pf::canonical(&v)?;
        if bytes.len() > REQUEST_MAX {
            return Err("payload_too_large".into());
        }
        String::from_utf8(bytes).map_err(|_| "encoding_failed".into())
    }
}
