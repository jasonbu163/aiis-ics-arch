//! Rust固定三API与有界HTTP adapter；禁止代理/redirect/cookie/自动retry，不提供任意URL执行。
use crate::domain::facts_canonical::Result;
use reqwest::{blocking::Client, redirect::Policy, Url};
use std::{io::Read, time::Duration};
pub(crate) const BATCHES: &str = "/api/v1/integration/plc-facts/batches";
pub(crate) const LATEST: &str = "/api/v1/integration/plc-facts/latest";
pub(crate) const HISTORY: &str = "/api/v1/integration/plc-facts/history";
pub(crate) use crate::domain::local_delivery::normalize_origin;
#[derive(Clone, Debug)]
pub(crate) struct Response {
    pub status: u16,
    pub media_type: String,
    pub retry_after: Option<String>,
    pub body: Vec<u8>,
}
pub(crate) trait Transport: Send + Sync {
    fn post(&self, origin: &str, body: &str) -> Result<Response>;
    fn get(&self, origin: &str, path: &str, query: &[(String, String)]) -> Result<Response>;
}
pub(crate) struct FactsHttp {
    client: Client,
}
impl FactsHttp {
    pub fn new() -> Result<Self> {
        let client = Client::builder()
            .connect_timeout(Duration::from_secs(3))
            .timeout(Duration::from_secs(15))
            .redirect(Policy::none())
            .no_proxy()
            .no_gzip()
            .no_brotli()
            .no_deflate()
            .no_zstd()
            .retry(reqwest::retry::never())
            .build()
            .map_err(|_| "http_initialization")?;
        Ok(Self { client })
    }
    fn read(mut response: reqwest::blocking::Response, limit: usize) -> Result<Response> {
        let status = response.status().as_u16();
        let media_type = response
            .headers()
            .get(reqwest::header::CONTENT_TYPE)
            .and_then(|v| v.to_str().ok())
            .unwrap_or("")
            .to_string();
        let retry_after = response
            .headers()
            .get(reqwest::header::RETRY_AFTER)
            .and_then(|v| v.to_str().ok())
            .filter(|s| s.len() <= 128)
            .map(str::to_string);
        let declared = response.content_length();
        let body = read_body(&mut response, declared, limit)?;
        Ok(Response {
            status,
            media_type,
            retry_after,
            body,
        })
    }
}
impl Transport for FactsHttp {
    fn post(&self, origin: &str, body: &str) -> Result<Response> {
        if body.len() > 4 * 1024 * 1024 {
            return Err("payload_too_large".into());
        }
        let origin = normalize_origin(origin)?;
        let response = self
            .client
            .post(format!("{origin}{BATCHES}"))
            .header(reqwest::header::CONTENT_TYPE, "application/json")
            .body(body.to_string())
            .send()
            .map_err(|_| "transport_unknown")?;
        Self::read(response, 8 * 1024 * 1024)
    }
    fn get(&self, origin: &str, path: &str, query: &[(String, String)]) -> Result<Response> {
        if ![LATEST, HISTORY].contains(&path)
            || query.len() > 12
            || query.iter().any(|(k, v)| k.len() > 32 || v.len() > 8192)
        {
            return Err("invalid_request".into());
        }
        let origin = normalize_origin(origin)?;
        let mut url = Url::parse(&format!("{origin}{path}")).map_err(|_| "invalid_target")?;
        url.query_pairs_mut()
            .extend_pairs(query.iter().map(|(k, v)| (k, v)));
        let response = self
            .client
            .get(url)
            .timeout(Duration::from_secs(8))
            .send()
            .map_err(|_| "transport_unknown")?;
        Self::read(response, 2 * 1024 * 1024)
    }
}
#[cfg(test)]
#[path = "facts_http_tests.rs"]
mod tests;

fn read_body(reader: &mut impl Read, declared: Option<u64>, limit: usize) -> Result<Vec<u8>> {
    if declared.map(|n| n > limit as u64).unwrap_or(false) {
        return Err("response_too_large".into());
    }
    let mut body = Vec::new();
    let mut buffer = [0u8; 16384];
    loop {
        let n = reader.read(&mut buffer).map_err(|_| "transport_unknown")?;
        if n == 0 {
            break;
        }
        if body.len() + n > limit {
            return Err("response_too_large".into());
        }
        body.extend_from_slice(&buffer[..n]);
    }
    if declared.map(|n| n != body.len() as u64).unwrap_or(false) {
        return Err("transport_unknown".into());
    }
    Ok(body)
}

// 固定ReadOut闭包在adapter边界严格解码；读取只能返回诊断，不能产生可靠ACK。
mod read_contract {
    use super::*;
    use serde::Deserialize;
    use serde_json::Value;
    use std::collections::BTreeMap;
    macro_rules! dto {($name:ident {$($(#[$meta:meta])* $field:ident:$ty:ty),*$(,)?})=>{#[derive(Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct $name{$($(#[$meta])* $field:$ty),*}}}
    fn required_nullable<'de, D, T>(d: D) -> std::result::Result<Option<T>, D::Error>
    where
        D: serde::Deserializer<'de>,
        T: Deserialize<'de>,
    {
        Option::deserialize(d)
    }
    dto!(Position {
        commit_serial: String,
        ordinal: u32
    });
    dto!(Coverage {
        complete: bool,
        meaning: String,
        unknown_before_serial: String
    });
    dto!(Source {
        instance_id: String,
        source_generation: String,
        source_seq: String,
        config_revision: String,
        definition_digest: String,
        sample_id: String,
        part: u32,
        cycle_id: String,
        group_id: String
    });
    dto!(Fact{definition:Value,value:Value,observed_at:String,quality:String,#[serde(deserialize_with="required_nullable")]reason:Option<String>});
    dto!(LatestPoint{definition:Value,value:Value,observed_at:String,quality:String,#[serde(deserialize_with="required_nullable")]reason:Option<String>,expires_at:String,source:Source});
    dto!(LatestDb{plc_id:String,db_number:u16,points:BTreeMap<String,LatestPoint>});
    macro_rules! page {($name:ident {$($(#[$meta:meta])* $field:ident:$ty:ty),*$(,)?})=>{#[derive(Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct $name{contract_version:String,digest_profile:String,as_of:String,has_more:bool,coverage:Coverage,mode:String,$($(#[$meta])* $field:$ty),*}}}
    page!(Latest{items:Vec<LatestDb>,#[serde(deserialize_with="required_nullable")]next_page_cursor:Option<String>,binding_revision:String});
    page!(Changes{items:Vec<Value>,next_cursor:String,snapshot_high_serial:String,scanned_through:Position,scan_budget_reached:bool,#[serde(deserialize_with="required_nullable")]baseline:Option<String>,omitted_through:Option<String>});
    page!(Range{items:Vec<Value>,#[serde(deserialize_with="required_nullable")]next_page_cursor:Option<String>,snapshot_high_serial:String,scanned_through:Position,scan_budget_reached:bool});
    dto!(Projection{source_sha256:String,sample_id:String,cycle_id:String,instance_id:String,plc_id:String,source_generation:String,source_seq:String,group_id:String,config_revision:String,db_number:u16,origin:String,started_at:String,finished_at:String,saved_at:String,part:u32,parts:u32,points:BTreeMap<String,Fact>,expires_at:String});
    dto!(Cycle {
        cycle_id: String,
        cycle_digest: String,
        complete: bool,
        quality_good: bool,
        received_parts: u32,
        expected_parts: u32
    });
    dto!(FactItem {
        kind: String,
        position: Position,
        source_sha256: String,
        content_digest: String,
        projection_digest: String,
        projection: Projection,
        cycle: Cycle
    });
    dto!(Gap{kind:String,position:Position,reason:String,instance_id:String,plc_id:String,source_generation:String,source_seq:String,cycle_id:String,sample_id:String,part:u32,point_ids:Vec<String>,source_sha256:String,content_digest:String,observed_from:String,observed_to:String,expired_at:String});
    dto!(Original {
        kind: String,
        position: Position,
        instance_id: String,
        plc_id: String,
        sample_id: String,
        source_sha256: String,
        payload_utf8: String,
        source_sample_complete: bool,
        expires_at: String
    });
    fn id(s: &str) -> Result<()> {
        if crate::domain::facts_wire::id(s) {
            Ok(())
        } else {
            Err("invalid_read_response".into())
        }
    }
    fn hash(s: &str) -> Result<()> {
        if s.strip_prefix("sha256:")
            .map(|s| {
                s.len() == 64
                    && s.bytes()
                        .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
            })
            .unwrap_or(false)
        {
            Ok(())
        } else {
            Err("invalid_read_response".into())
        }
    }
    fn serial(s: &str, zero: bool) -> Result<()> {
        if s.parse::<u64>()
            .map(|n| (zero || n > 0) && n.to_string() == s)
            .unwrap_or(false)
        {
            Ok(())
        } else {
            Err("invalid_read_response".into())
        }
    }
    fn position(p: &Position) -> Result<()> {
        serial(&p.commit_serial, true)?;
        if p.ordinal > 32 {
            return Err("invalid_read_response".into());
        }
        Ok(())
    }
    fn base(contract: &str, digest: &str, at: &str, c: &Coverage) -> Result<()> {
        if contract != "plc-facts/v1"
            || digest != "pf-json/v1"
            || c.complete
            || c.meaning != "receipt_feed_only_not_source_completeness"
        {
            return Err("invalid_read_response".into());
        }
        crate::domain::facts_wire::time(at)?;
        serial(&c.unknown_before_serial, true)
    }
    fn fact(f: &Fact, pid: &str, plc: &str) -> Result<()> {
        use serde_json::json;
        crate::domain::facts_wire::value_check(
            &json!({"definition":f.definition,"value":f.value,"observedAt":f.observed_at,"quality":f.quality,"reason":f.reason}),
        )?;
        if f.definition["id"] != pid || f.definition["plcId"] != plc {
            return Err("invalid_read_response".into());
        }
        crate::domain::facts_wire::time(&f.observed_at)?;
        Ok(())
    }
    fn token(token: Option<&str>) -> Result<()> {
        if token
            .map(|t| t.is_empty() || t.len() > 8192)
            .unwrap_or(false)
        {
            return Err("invalid_read_response".into());
        }
        Ok(())
    }
    fn item(v: &Value, plc: &str, original: bool) -> Result<bool> {
        use crate::domain::{
            facts_canonical as pf,
            facts_wire::{text, time},
        };
        match v["kind"].as_str() {
            Some("fact") if !original => {
                let x: FactItem =
                    serde_json::from_value(v.clone()).map_err(|_| "invalid_read_response")?;
                if x.kind != "fact"
                    || x.projection.plc_id != plc
                    || x.cycle.cycle_id != x.projection.cycle_id
                    || x.cycle.received_parts > x.cycle.expected_parts
                    || x.cycle.complete != (x.cycle.received_parts == x.cycle.expected_parts)
                    || (x.cycle.quality_good
                        && x.projection.points.values().any(|f| f.quality != "good"))
                {
                    return Err("invalid_read_response".into());
                }
                position(&x.position)?;
                hash(&x.source_sha256)?;
                hash(&x.content_digest)?;
                hash(&x.projection_digest)?;
                hash(&x.cycle.cycle_digest)?;
                let p = &x.projection;
                for s in [
                    &p.sample_id,
                    &p.cycle_id,
                    &p.instance_id,
                    &p.plc_id,
                    &p.source_generation,
                    &p.group_id,
                    &p.config_revision,
                ] {
                    id(s)?;
                }
                serial(&p.source_seq, false)?;
                if p.db_number == 0
                    || p.part == 0
                    || p.parts > 16
                    || p.part > p.parts
                    || p.points.is_empty()
                    || p.points.len() > 512
                    || p.origin.is_empty()
                    || p.origin.len() > 64
                    || p.source_sha256 != x.source_sha256
                    || time(&p.started_at)? > time(&p.finished_at)?
                    || time(&p.finished_at)? > time(&p.saved_at)?
                {
                    return Err("invalid_read_response".into());
                }
                time(&p.expires_at)?;
                for (pid, f) in &p.points {
                    fact(f, pid, plc)?;
                }
                if pf::digest("query-projection", &v["projection"])? != x.projection_digest {
                    return Err("invalid_read_response".into());
                }
                Ok(false)
            }
            Some("gap") => {
                let x: Gap =
                    serde_json::from_value(v.clone()).map_err(|_| "invalid_read_response")?;
                if x.kind != "gap"
                    || x.plc_id != plc
                    || !["raw_expired", "raw_unavailable"].contains(&x.reason.as_str())
                    || x.part == 0
                    || x.part > 16
                    || x.point_ids.len() > 512
                {
                    return Err("invalid_read_response".into());
                }
                for s in [
                    &x.instance_id,
                    &x.plc_id,
                    &x.source_generation,
                    &x.cycle_id,
                    &x.sample_id,
                ] {
                    id(s)?;
                }
                for s in &x.point_ids {
                    id(s)?;
                }
                serial(&x.source_seq, false)?;
                position(&x.position)?;
                hash(&x.source_sha256)?;
                hash(&x.content_digest)?;
                if time(&x.observed_from)? > time(&x.observed_to)? {
                    return Err("invalid_read_response".into());
                }
                time(&x.expired_at)?;
                Ok(true)
            }
            Some("original") if original => {
                let x: Original =
                    serde_json::from_value(v.clone()).map_err(|_| "invalid_read_response")?;
                if x.kind != "original"
                    || x.plc_id != plc
                    || !x.source_sample_complete
                    || pf::sha(x.payload_utf8.as_bytes()) != x.source_sha256
                {
                    return Err("invalid_read_response".into());
                }
                position(&x.position)?;
                for s in [&x.instance_id, &x.plc_id, &x.sample_id] {
                    id(s)?;
                }
                hash(&x.source_sha256)?;
                time(&x.expires_at)?;
                let payload = pf::parse(x.payload_utf8.as_bytes(), 512 * 1024)?;
                if text(&payload, "sampleId")? != x.sample_id
                    || payload["instanceId"] != x.instance_id
                    || payload["plcId"] != plc
                {
                    return Err("invalid_read_response".into());
                }
                Ok(false)
            }
            _ => Err("invalid_read_response".into()),
        }
    }
    pub(super) fn validate(
        value: &Value,
        plc: &str,
        mode: &str,
        original: bool,
        limit: usize,
    ) -> Result<(Option<String>, bool, bool)> {
        use crate::domain::facts_canonical as pf;
        let envelope = value.as_object().ok_or("invalid_read_response")?;
        if envelope.len() != 3 || value["code"] != 200 || value["message"] != "success" {
            return Err("invalid_read_response".into());
        }
        let d = &value["data"];
        if d["mode"] != mode {
            return Err("invalid_read_response".into());
        }
        let mut gap = false;
        match mode {
            "latest" => {
                let p: Latest =
                    serde_json::from_value(d.clone()).map_err(|_| "invalid_read_response")?;
                base(
                    &p.contract_version,
                    &p.digest_profile,
                    &p.as_of,
                    &p.coverage,
                )?;
                if p.mode != "latest" {
                    return Err("invalid_read_response".into());
                }
                serial(&p.binding_revision, false)?;
                token(p.next_page_cursor.as_deref())?;
                if p.has_more != p.next_page_cursor.is_some() {
                    return Err("invalid_read_response".into());
                }
                let mut count = 0;
                for db in &p.items {
                    if db.plc_id != plc || db.db_number == 0 {
                        return Err("invalid_read_response".into());
                    }
                    for (pid, f) in &db.points {
                        count += 1;
                        fact(
                            &Fact {
                                definition: f.definition.clone(),
                                value: f.value.clone(),
                                observed_at: f.observed_at.clone(),
                                quality: f.quality.clone(),
                                reason: f.reason.clone(),
                            },
                            pid,
                            plc,
                        )?;
                        crate::domain::facts_wire::time(&f.expires_at)?;
                        let r = &f.source;
                        for s in [
                            &r.instance_id,
                            &r.source_generation,
                            &r.config_revision,
                            &r.sample_id,
                            &r.cycle_id,
                            &r.group_id,
                        ] {
                            id(s)?;
                        }
                        serial(&r.source_seq, false)?;
                        hash(&r.definition_digest)?;
                        if r.part == 0
                            || r.part > 16
                            || pf::digest(
                                "definition",
                                &crate::domain::facts_wire::definition_object(&f.definition)?,
                            )? != r.definition_digest
                        {
                            return Err("invalid_read_response".into());
                        }
                    }
                }
                if count > limit {
                    return Err("invalid_read_response".into());
                }
                Ok((p.next_page_cursor, p.has_more, false))
            }
            "changes" => {
                let p: Changes =
                    serde_json::from_value(d.clone()).map_err(|_| "invalid_read_response")?;
                base(
                    &p.contract_version,
                    &p.digest_profile,
                    &p.as_of,
                    &p.coverage,
                )?;
                if p.mode != "changes"
                    || p.items.len() > limit
                    || p.baseline
                        .as_deref()
                        .map(|s| s != "explicit_tail")
                        .unwrap_or(false)
                {
                    return Err("invalid_read_response".into());
                }
                serial(&p.snapshot_high_serial, true)?;
                position(&p.scanned_through)?;
                token(Some(&p.next_cursor))?;
                if let Some(s) = &p.omitted_through {
                    serial(s, true)?;
                }
                for v in &p.items {
                    gap |= item(v, plc, false)?;
                }
                Ok((
                    Some(p.next_cursor),
                    p.has_more || p.scan_budget_reached,
                    gap,
                ))
            }
            "range" => {
                let p: Range =
                    serde_json::from_value(d.clone()).map_err(|_| "invalid_read_response")?;
                base(
                    &p.contract_version,
                    &p.digest_profile,
                    &p.as_of,
                    &p.coverage,
                )?;
                if p.mode != "range" || p.items.len() > limit {
                    return Err("invalid_read_response".into());
                }
                serial(&p.snapshot_high_serial, true)?;
                position(&p.scanned_through)?;
                token(p.next_page_cursor.as_deref())?;
                if p.has_more != p.next_page_cursor.is_some() {
                    return Err("invalid_read_response".into());
                }
                for v in &p.items {
                    gap |= item(v, plc, original)?;
                }
                Ok((p.next_page_cursor, p.has_more || p.scan_budget_reached, gap))
            }
            _ => Err("invalid_read_response".into()),
        }
    }
}
pub(crate) fn validate_read(
    value: &serde_json::Value,
    plc: &str,
    mode: &str,
    original: bool,
    limit: usize,
) -> Result<(Option<String>, bool, bool)> {
    read_contract::validate(value, plc, mode, original, limit)
}
