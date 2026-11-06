//! 上传单目标设置、独立CAS及稳定状态；不属于采集configuration/context。
use reqwest::Url;
use serde::{Deserialize, Serialize};
use serde_json::Value;
pub(crate) fn normalize_origin(raw: &str) -> Result<String> {
    let url = Url::parse(raw).map_err(|_| "invalid_target")?;
    if !["http", "https"].contains(&url.scheme())
        || url.host_str().is_none()
        || !url.username().is_empty()
        || url.password().is_some()
        || url.query().is_some()
        || url.fragment().is_some()
        || url.path() != "/"
        || raw.trim() != raw
    {
        return Err("invalid_target".into());
    }
    Ok(url.origin().ascii_serialization())
}

use super::facts_canonical::Result;
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct SourceAdoption {
    pub plc_id: String,
    pub source_generation: String,
    pub definition_set_digest: String,
    pub context_sha256: String,
    pub sequence_from: String,
    pub sequence_through: String,
    pub reference: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct DeliverySettings {
    pub schema_version: u32,
    pub settings_revision: String,
    pub target_id: Option<String>,
    pub origin: Option<String>,
    pub interval_seconds: u32,
    pub adoption_reference: String,
    pub contract_pins: Value,
    pub sources: Vec<SourceAdoption>,
}
impl Default for DeliverySettings {
    fn default() -> Self {
        Self {
            schema_version: 1,
            settings_revision: super::local_configuration::id(),
            target_id: None,
            origin: None,
            interval_seconds: 5,
            adoption_reference: String::new(),
            contract_pins: serde_json::json!({}),
            sources: vec![],
        }
    }
}
pub(crate) const CONTRACT_PINS: [(&str, &str); 3] = [
    (
        "openapiSha256",
        "bec51c468ff64a8d34dbb0a2faab2fda76d2b33769ee5ef066dc81e8bca274ee",
    ),
    (
        "schemaSha256",
        "60d0e285bebb1c6d24588f4d5f90e7bdd85ed0befdeab9d0b93445a94f45d4b3",
    ),
    (
        "vectorsSha256",
        "9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782",
    ),
];
impl DeliverySettings {
    pub fn validate(&self) -> Result<()> {
        if self.schema_version != 1
            || !(1..=3600).contains(&self.interval_seconds)
            || self.sources.len() > 4
            || self.adoption_reference.len() > 2048
            || serde_json::to_vec(self)
                .map_err(|_| "invalid_request")?
                .len()
                > 64 * 1024
        {
            return Err("invalid_settings".into());
        }
        match (&self.target_id, &self.origin) {
            (None, None) => {}
            (Some(id), Some(origin)) => {
                if CONTRACT_PINS
                    .iter()
                    .any(|(k, v)| self.contract_pins[*k] != *v)
                {
                    return Err("contract_pins_mismatch".into());
                }
                if !super::facts_wire::id(id) || normalize_origin(origin)? != *origin {
                    return Err("invalid_target".into());
                }
            }
            _ => return Err("invalid_target".into()),
        }
        let mut ids = std::collections::BTreeSet::new();
        for s in &self.sources {
            if !hash(&s.definition_set_digest)
                || !hash(&s.context_sha256)
                || !super::facts_wire::id(&s.plc_id)
                || !super::facts_wire::id(&s.source_generation)
                || !ids.insert(&s.plc_id)
                || s.reference.is_empty()
                || s.reference.len() > 2048
                || s.sequence_from
                    .parse::<i64>()
                    .ok()
                    .filter(|n| *n > 0 && n.to_string() == s.sequence_from)
                    .is_none()
                || s.sequence_through
                    .parse::<i64>()
                    .ok()
                    .filter(|n| {
                        *n >= s.sequence_from.parse().unwrap_or(i64::MAX)
                            && *n < i64::MAX
                            && n.to_string() == s.sequence_through
                    })
                    .is_none()
            {
                return Err("invalid_source_adoption".into());
            }
        }
        Ok(())
    }
}

macro_rules! dto {($name:ident {$($(#[$meta:meta])* $field:ident:$ty:ty),*$(,)?})=>{#[derive(Clone,Debug,Serialize,Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct $name{$($(#[$meta])* $field:$ty),*}}}
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
dto!(PartResult{sample_id:String,part:u32,parts:u32,source_sha256:String,content_digest:String,outcome:String,original_outcome:String,confirmation:String,source_sample_complete:bool,position:Position,latest_advanced_point_ids:Vec<String>,expires_at:String,value_readable:bool});
dto!(CycleResult {
    cycle_id: String,
    cycle_digest: String,
    complete: bool,
    quality_good: bool,
    received_parts: u32,
    expected_parts: u32
});
dto!(Receipt{contract_version:String,digest_profile:String,instance_id:String,batch_id:String,request_digest:String,receipt_id:String,status:String,persistence:String,new_facts_committed:bool,outcome:String,original_outcome:String,confirmation:String,#[serde(deserialize_with="required_nullable")]commit_serial:Option<String>,committed_at:String,proof_expires_at:String,results:Vec<PartResult>,cycles:Vec<CycleResult>});
dto!(Success {
    code: u16,
    message: String,
    data: Receipt
});
dto!(HistoricalProof {
    sample_id: String,
    part: u32,
    content_digest: String,
    source_sha256: String,
    position: Position,
    proof_expires_at: String
});
dto!(Diagnosis{sample_id:String,part:u32,diagnosis:String,historical_proof:Option<HistoricalProof>});
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct FailureData {
    contract_version: Option<String>,
    instance_id: Option<String>,
    batch_id: Option<String>,
    request_digest: Option<String>,
    receipt_id: Option<String>,
    recorded_at: Option<String>,
    persistence: String,
    new_facts_committed: Option<bool>,
    retryable: bool,
    retirement_allowed: bool,
    rejection_token: Option<String>,
    rejection_expires_at: Option<String>,
    #[serde(default)]
    diagnostics: Vec<Diagnosis>,
    requires_resync: Option<bool>,
    lost_from: Option<Position>,
    lost_through: Option<Position>,
    earliest_recoverable_cursor: Option<String>,
}
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Failure {
    code: u16,
    message: String,
    error_code: String,
    data: FailureData,
}
fn hash(s: &str) -> bool {
    s.strip_prefix("sha256:")
        .map(|h| {
            h.len() == 64
                && h.bytes()
                    .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
        })
        .unwrap_or(false)
}
pub(crate) fn valid_failure(v: &Value, status: u16) -> Result<()> {
    use super::facts_wire::{id, time};
    let f: Failure = serde_json::from_value(v.clone()).map_err(|_| "invalid_receipt")?;
    let statuses = [403, 409, 410, 413, 415, 422, 429, 503, 500];
    let errors = [
        "scope_rejected",
        "source_rejected",
        "batch_content_conflict",
        "sample_content_conflict",
        "cycle_content_conflict",
        "binding_conflict",
        "sample_expired",
        "proof_expired",
        "cursor_expired",
        "cursor_gap",
        "parent_proof_expired",
        "batch_admission_expired",
        "payload_too_large",
        "media_type",
        "invalid_request",
        "digest_mismatch",
        "cursor_mismatch",
        "busy",
        "not_ready",
        "unavailable",
        "commit_outcome_unknown",
        "clock_invalid",
        "capacity_exceeded",
        "internal_error",
    ];
    if !statuses.contains(&status)
        || f.code != status
        || f.message.len() > 4096
        || !f
            .error_code
            .strip_prefix("plc_facts.")
            .map(|s| errors.contains(&s))
            .unwrap_or(false)
    {
        return Err("invalid_receipt".into());
    }
    let d = &f.data;
    if !v["data"]
        .as_object()
        .map(|m| m.contains_key("newFactsCommitted"))
        .unwrap_or(false)
        || !(["none", "unknown", "rejection_recorded"].contains(&d.persistence.as_str()))
        || d.contract_version
            .as_deref()
            .map(|s| s != "plc-facts/v1")
            .unwrap_or(false)
        || d.instance_id.as_deref().map(|s| !id(s)).unwrap_or(false)
        || d.batch_id.as_deref().map(|s| !id(s)).unwrap_or(false)
        || d.request_digest
            .as_deref()
            .map(|s| !hash(s))
            .unwrap_or(false)
        || d.receipt_id
            .as_deref()
            .map(|s| uuid::Uuid::parse_str(s).is_err())
            .unwrap_or(false)
        || d.rejection_token
            .as_deref()
            .map(|s| s.is_empty() || s.len() > 16384)
            .unwrap_or(false)
        || d.earliest_recoverable_cursor
            .as_deref()
            .map(|s| s.len() > 8192)
            .unwrap_or(false)
    {
        return Err("invalid_receipt".into());
    }
    for t in [&d.recorded_at, &d.rejection_expires_at] {
        if let Some(t) = t {
            time(t)?;
        }
    }
    for p in [&d.lost_from, &d.lost_through] {
        if let Some(p) = p {
            if !serial(&p.commit_serial) || p.ordinal > 32 {
                return Err("invalid_receipt".into());
            }
        }
    }
    for diagnosis in &d.diagnostics {
        if !id(&diagnosis.sample_id)
            || !(1..=16).contains(&diagnosis.part)
            || ![
                "eligible",
                "duplicate_proven",
                "expired_unproven",
                "conflict",
                "source_rejected",
            ]
            .contains(&diagnosis.diagnosis.as_str())
        {
            return Err("invalid_receipt".into());
        }
        if let Some(p) = &diagnosis.historical_proof {
            if !id(&p.sample_id)
                || !(1..=16).contains(&p.part)
                || !hash(&p.content_digest)
                || !hash(&p.source_sha256)
                || !serial(&p.position.commit_serial)
                || p.position.ordinal == 0
                || p.position.ordinal > 32
            {
                return Err("invalid_receipt".into());
            }
            time(&p.proof_expires_at)?;
        }
    }
    if d.persistence == "rejection_recorded" {
        if ![403, 409, 410].contains(&status)
            || !d.retirement_allowed
            || d.new_facts_committed != Some(false)
            || d.retryable
            || d.requires_resync == Some(true)
        {
            return Err("invalid_receipt".into());
        }
    } else if d.retirement_allowed || d.new_facts_committed == Some(true) {
        return Err("invalid_receipt".into());
    }
    Ok(())
}
#[derive(Clone, Debug)]
pub(crate) enum Reply {
    Committed(Value),
    Rejected {
        envelope: Value,
        eligible: Vec<(String, u32)>,
    },
    Failure {
        state: String,
        error: String,
        delay: u32,
        pause: bool,
        protocol: bool,
    },
}
fn protocol() -> Reply {
    Reply::Failure {
        state: "unknown".into(),
        error: "invalid_receipt".into(),
        delay: 1,
        pause: false,
        protocol: true,
    }
}
fn serial(s: &str) -> bool {
    s.parse::<u64>()
        .map(|n| n > 0 && n.to_string() == s)
        .unwrap_or(false)
}
fn outcomes(s: &str) -> bool {
    ["created", "duplicate"].contains(&s)
}
pub(crate) fn verify_success(batch: &super::facts_wire::Batch, value: &Value) -> Result<()> {
    use super::facts_wire::{cycle_digest, time};
    let receipt: Success = serde_json::from_value(value.clone()).map_err(|_| "invalid_receipt")?;
    let d = &receipt.data;
    if receipt.code != 200
        || receipt.message != "success"
        || d.contract_version != "plc-facts/v1"
        || d.digest_profile != "pf-json/v1"
        || d.instance_id != batch.instance_id
        || d.batch_id != batch.batch_id
        || d.request_digest != batch.request_digest
        || d.status != "committed"
        || d.persistence != "committed"
        || d.confirmation != "facts_committed"
        || uuid::Uuid::parse_str(&d.receipt_id).is_err()
        || !outcomes(&d.outcome)
        || !outcomes(&d.original_outcome)
        || time(&d.proof_expires_at)? <= time(&d.committed_at)?
        || d.new_facts_committed != (d.outcome == "created")
        || d.commit_serial.as_deref().map(serial).unwrap_or(false) != d.new_facts_committed
    {
        return Err("invalid_receipt".into());
    }
    if d.results.len() != batch.samples.len() || d.cycles.len() != batch.cycles.len() {
        return Err("invalid_receipt".into());
    }
    let mut keys = std::collections::BTreeSet::new();
    let mut any_created = false;
    for r in &d.results {
        let p = batch
            .samples
            .iter()
            .find(|p| p.sample_id == r.sample_id && p.part == r.part)
            .ok_or("invalid_receipt")?;
        if !keys.insert((&r.sample_id, r.part))
            || r.parts != p.parts
            || r.source_sha256 != p.source_sha256
            || r.content_digest != p.content_digest
            || !outcomes(&r.outcome)
            || !outcomes(&r.original_outcome)
            || !serial(&r.position.commit_serial)
            || r.position.ordinal > 32
            || r.position.ordinal == 0
        {
            return Err("invalid_receipt".into());
        }
        // 单片永远完整；本事务新建且送齐所有片时也必然完整。重复回执保留首次缓存状态。
        let all_parts_sent = batch
            .samples
            .iter()
            .filter(|s| s.sample_id == p.sample_id)
            .count()
            == p.parts as usize;
        let cycle = d
            .cycles
            .iter()
            .find(|c| c.cycle_id == p.cycle_id)
            .ok_or("invalid_receipt")?;
        if (!r.source_sample_complete
            && (p.parts == 1
                || (r.confirmation == "created" && (all_parts_sent || cycle.complete))))
            || (r.source_sample_complete && cycle.received_parts < p.parts)
        {
            return Err("invalid_receipt".into());
        }
        time(&r.expires_at)?;
        let mut advanced = std::collections::BTreeSet::new();
        if r.latest_advanced_point_ids
            .iter()
            .any(|id| !p.point_ids.contains(id) || !advanced.insert(id))
        {
            return Err("invalid_receipt".into());
        }
        match r.confirmation.as_str() {
            "created" => {
                if r.outcome != "created"
                    || r.original_outcome != "created"
                    || !r.value_readable
                    || d.commit_serial.as_deref() != Some(&r.position.commit_serial)
                {
                    return Err("invalid_receipt".into());
                }
                any_created = true;
            }
            "duplicate" => {
                if r.outcome != "duplicate" || !r.value_readable {
                    return Err("invalid_receipt".into());
                }
            }
            "historical_committed" => {
                if r.outcome != "duplicate" || r.value_readable {
                    return Err("invalid_receipt".into());
                }
            }
            _ => return Err("invalid_receipt".into()),
        }
    }
    if any_created != d.new_facts_committed {
        return Err("invalid_receipt".into());
    }
    let mut cycles = std::collections::BTreeSet::new();
    for r in &d.cycles {
        let c = batch
            .cycles
            .iter()
            .find(|c| c.cycle_id == r.cycle_id)
            .ok_or("invalid_receipt")?;
        let expected = c
            .transport_manifest
            .iter()
            .map(|s| s.parts.len() as u32)
            .sum::<u32>();
        let sent = batch
            .samples
            .iter()
            .filter(|s| s.cycle_id == c.cycle_id)
            .count() as u32;
        if !cycles.insert(&r.cycle_id)
            || r.cycle_digest != cycle_digest(c)?
            || r.expected_parts != expected
            || r.received_parts > expected
            || r.received_parts < sent
            || r.complete != (r.received_parts == expected)
            || (r.quality_good
                && batch
                    .samples
                    .iter()
                    .filter(|p| p.cycle_id == c.cycle_id)
                    .any(|p| {
                        super::facts_canonical::parse(p.payload_utf8.as_bytes(), 512 * 1024)
                            .ok()
                            .and_then(|v| v["points"].as_object().cloned())
                            .map(|points| points.values().any(|v| v["quality"] != "good"))
                            .unwrap_or(true)
                    }))
        {
            return Err("invalid_receipt".into());
        }
    }
    Ok(())
}
pub(crate) fn classify(
    batch: &super::facts_wire::Batch,
    status: u16,
    media: &str,
    body: &[u8],
    retry_after: Option<&str>,
    attempt: u32,
    jitter: u32,
) -> Reply {
    use super::{
        facts_canonical as pf,
        facts_wire::{text, time, RECEIPT_MAX},
    };
    let delay = retry_delay(attempt, retry_after, jitter);
    if media.split(';').next().map(str::trim) != Some("application/json") {
        return protocol();
    }
    let value = match pf::parse(body, RECEIPT_MAX) {
        Ok(v) => v,
        Err(_) => return protocol(),
    };
    if status == 200 {
        return if verify_success(batch, &value).is_ok() {
            if text(&value["data"], "proofExpiresAt")
                .and_then(time)
                .map(|t| t <= chrono::Utc::now())
                .unwrap_or(true)
            {
                Reply::Failure {
                    state: "needs_review".into(),
                    error: "proof_expired".into(),
                    delay: 1,
                    pause: false,
                    protocol: false,
                }
            } else {
                Reply::Committed(value)
            }
        } else {
            protocol()
        };
    }
    if valid_failure(&value, status).is_err() {
        return protocol();
    }
    let d = &value["data"];
    let allowed = ["code", "message", "errorCode", "data"];
    if value
        .as_object()
        .map(|m| m.len() == 4 && allowed.iter().all(|k| m.contains_key(*k)))
        != Some(true)
        || value["code"].as_u64() != Some(status as u64)
        || !value["message"].is_string()
        || !d.is_object()
    {
        return protocol();
    }
    let error = match text(&value, "errorCode") {
        Ok(s) if s.len() <= 128 => s.rsplit('.').next().unwrap_or(s).to_string(),
        _ => return protocol(),
    };
    let persistence = match text(d, "persistence") {
        Ok(s) => s,
        Err(_) => return protocol(),
    };
    if persistence == "rejection_recorded" {
        if d["contractVersion"] != "plc-facts/v1"
            || d["instanceId"] != batch.instance_id
            || d["batchId"] != batch.batch_id
            || d["requestDigest"] != batch.request_digest
            || d["newFactsCommitted"] != false
            || d["retirementAllowed"] != true
            || !d["retryable"].is_boolean()
            || text(d, "receiptId")
                .map(|s| s.is_empty() || s.len() > 128)
                .unwrap_or(true)
            || text(d, "rejectionToken")
                .map(|s| s.is_empty() || s.len() > 16384)
                .unwrap_or(true)
        {
            return protocol();
        }
        let (recorded, expiry) = match (
            text(d, "recordedAt").and_then(time),
            text(d, "rejectionExpiresAt").and_then(time),
        ) {
            (Ok(a), Ok(b)) if a < b => (a, b),
            _ => return protocol(),
        };
        let _ = (recorded, expiry);
        let diagnostics = match d["diagnostics"].as_array() {
            Some(a) if a.len() == batch.samples.len() => a,
            _ => return protocol(),
        };
        let mut seen = std::collections::BTreeSet::new();
        let mut eligible = vec![];
        for diagnosis in diagnostics {
            let sid = match text(diagnosis, "sampleId") {
                Ok(s) => s,
                _ => return protocol(),
            };
            let part = match diagnosis["part"].as_u64() {
                Some(n) => n as u32,
                _ => return protocol(),
            };
            let p = match batch
                .samples
                .iter()
                .find(|p| p.sample_id == sid && p.part == part)
            {
                Some(p) => p,
                _ => return protocol(),
            };
            if !seen.insert((sid, part)) {
                return protocol();
            }
            match diagnosis["diagnosis"].as_str() {
                Some("eligible") => eligible.push((sid.into(), part)),
                Some("duplicate_proven") => {
                    let proof = &diagnosis["historicalProof"];
                    if proof["sampleId"] != sid
                        || proof["part"] != part
                        || proof["contentDigest"] != p.content_digest
                        || proof["sourceSha256"] != p.source_sha256
                        || text(proof, "proofExpiresAt").and_then(time).is_err()
                        || serde_json::from_value::<Position>(proof["position"].clone())
                            .map(|p| !serial(&p.commit_serial) || p.ordinal == 0 || p.ordinal > 32)
                            .unwrap_or(true)
                    {
                        return protocol();
                    }
                    eligible.push((sid.into(), part));
                }
                Some("expired_unproven" | "conflict" | "source_rejected") => {}
                _ => return protocol(),
            }
        }
        return Reply::Rejected {
            envelope: value,
            eligible,
        };
    }
    if !["none", "unknown"].contains(&persistence)
        || (persistence == "none" && d["newFactsCommitted"] != false)
        || d["retirementAllowed"] != false
        || !d["retryable"].is_boolean()
    {
        return protocol();
    }
    let (state, pause) = match (status, error.as_str(), persistence) {
        (_, _, "unknown") => ("unknown", false),
        (429, _, "none") => ("retry_wait", false),
        (503, "unavailable" | "capacity_exceeded" | "clock_invalid" | "not_ready", "none") => {
            ("retry_wait", false)
        }
        (403, "scope_rejected", _) => ("needs_review", true),
        (410, "proof_expired" | "parent_proof_expired", _) => ("needs_review", false),
        (410, _, _) => ("expired_unconfirmed", false),
        (403 | 409 | 413 | 415 | 422, _, _) => ("blocked", false),
        _ => ("unknown", false),
    };
    Reply::Failure {
        state: state.into(),
        error,
        delay,
        pause,
        protocol: false,
    }
}
pub(crate) fn retry_delay(attempt: u32, retry_after: Option<&str>, jitter: u32) -> u32 {
    if let Some(s) = retry_after {
        if let Ok(seconds) = s.parse::<u32>() {
            return seconds.clamp(1, 300);
        }
        if let Ok(at) = chrono::DateTime::parse_from_rfc2822(s) {
            let delta = at.timestamp() - chrono::Utc::now().timestamp();
            return delta.clamp(1, 300) as u32;
        }
    }
    let base = if attempt >= 6 {
        30
    } else {
        1u32 << attempt.saturating_sub(1)
    };
    base + (base * jitter.min(20)) / 100
}

/// 独立手工读取的一页；20页预算由明确继续操作重开，不保存SMA checkpoint。
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct ReadQuery {
    pub plc_id: String,
    pub mode: Option<String>,
    pub from: Option<String>,
    pub to: Option<String>,
    pub cursor: Option<String>,
    pub page: Option<u32>,
}
impl ReadQuery {
    pub fn parameters(&self) -> Result<(bool, String, bool, usize, Vec<(String, String)>)> {
        use super::facts_wire::{id, time, wire_time};
        if !id(&self.plc_id)
            || self.page.unwrap_or(1) == 0
            || self.page.unwrap_or(1) > 20
            || self
                .cursor
                .as_deref()
                .map(|s| s.is_empty() || s.len() > 8192)
                .unwrap_or(false)
        {
            return Err("query_limits".into());
        }
        let mode = self.mode.as_deref().unwrap_or("test");
        let latest = ["test", "latest"].contains(&mode);
        let original = mode == "original";
        let limit = if mode == "test" || original { 1 } else { 8 };
        let mut query = vec![
            ("plcId".into(), self.plc_id.clone()),
            ("limit".into(), limit.to_string()),
        ];
        let protocol = if latest {
            if self.from.is_some() || self.to.is_some() || (mode == "test" && self.cursor.is_some())
            {
                return Err("invalid_request".into());
            }
            if let Some(c) = &self.cursor {
                query.push(("pageCursor".into(), c.clone()));
            }
            "latest"
        } else if mode == "changes" {
            if self.from.is_some() || self.to.is_some() {
                return Err("invalid_request".into());
            }
            query.push(("mode".into(), "changes".into()));
            query.push(("view".into(), "projection".into()));
            query.push(if let Some(c) = &self.cursor {
                ("cursor".into(), c.clone())
            } else {
                ("start".into(), "earliest".into())
            });
            "changes"
        } else if ["range", "original"].contains(&mode) {
            let from = self.from.as_deref().ok_or("invalid_request")?;
            let to = self.to.as_deref().ok_or("invalid_request")?;
            if time(from)? >= time(to)? {
                return Err("query_limits".into());
            }
            query.extend([
                ("mode".into(), "range".into()),
                (
                    "view".into(),
                    if original { "original" } else { "projection" }.into(),
                ),
                ("from".into(), wire_time(from)?),
                ("to".into(), wire_time(to)?),
            ]);
            if let Some(c) = &self.cursor {
                query.push(("pageCursor".into(), c.clone()));
            }
            "range"
        } else {
            return Err("invalid_request".into());
        };
        Ok((latest, protocol.into(), original, limit, query))
    }
}
#[derive(Clone, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct Rotation {
    pub last_plc: String,
    pub groups: std::collections::BTreeMap<String, String>,
}
impl Rotation {
    pub fn decode(raw: &str) -> Self {
        serde_json::from_str(raw).unwrap_or_default()
    }
    pub fn advance(&mut self, plc: &str, group: &str) {
        self.last_plc = plc.into();
        self.groups.insert(plc.into(), group.into());
    }
    pub fn compare(&self, a: (&str, &str), b: (&str, &str)) -> std::cmp::Ordering {
        (a.0 <= self.last_plc.as_str())
            .cmp(&(b.0 <= self.last_plc.as_str()))
            .then(a.0.cmp(b.0))
            .then_with(|| {
                let last = self.groups.get(a.0).map(String::as_str).unwrap_or("");
                (a.1 <= last).cmp(&(b.1 <= last)).then(a.1.cmp(b.1))
            })
    }
}
