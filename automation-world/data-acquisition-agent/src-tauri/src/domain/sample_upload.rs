//! PLC facts v2 单 DB 样本构造和响应判断；不读写存储、不执行网络。
use super::{
    facts_canonical as pf, facts_wire,
    local_configuration::{width, Configuration, LocalResult},
    local_sample::{CycleManifest, SamplePayload},
};
use chrono::{DateTime, Datelike, Duration, FixedOffset, Months};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeSet;

pub(crate) const CONTRACT: &str = "plc-facts/v2";
pub(crate) const BODY_LIMIT: usize = 524_288;
pub(crate) const DEFAULT_PATH: &str = "/api/v1/integration/plc-facts/samples";

pub(crate) fn upload_origin(raw: &str) -> LocalResult<String> {
    if raw.len() > 2048
        || raw
            .split_once("://")
            .map(|(_, tail)| tail.split('/').next().unwrap_or("").contains('@'))
            .unwrap_or(true)
    {
        return Err("invalid_target".into());
    }
    super::local_delivery::normalize_origin(raw)
}

/// 将独立的 origin 和绝对路径组合，拒绝能改变 authority、携带查询或片段的输入。
pub(crate) fn target_url(origin: &str, path: &str) -> LocalResult<String> {
    let origin = upload_origin(origin)?;
    if !path.starts_with('/')
        || path.starts_with("//")
        || path.contains(['?', '#', '\\'])
        || path.chars().any(char::is_control)
        || path.trim() != path
        || path.len() > 2048
    {
        return Err("invalid_target".into());
    }
    let url = reqwest::Url::parse(&format!("{origin}{path}")).map_err(|_| "invalid_target")?;
    if url.origin().ascii_serialization() != origin
        || url.query().is_some()
        || url.fragment().is_some()
    {
        return Err("invalid_target".into());
    }
    Ok(url.to_string())
}

pub(crate) fn normalize_target(raw: &str) -> LocalResult<String> {
    if raw.len() > 4096
        || raw.trim() != raw
        || raw.contains('\\')
        || raw.chars().any(char::is_control)
        || raw
            .split_once("://")
            .map(|(_, tail)| tail.split('/').next().unwrap_or("").contains('@'))
            .unwrap_or(true)
    {
        return Err("invalid_target".into());
    }
    let url = reqwest::Url::parse(raw).map_err(|_| "invalid_target")?;
    if !["http", "https"].contains(&url.scheme())
        || url.host_str().is_none()
        || !url.username().is_empty()
        || url.password().is_some()
        || url.query().is_some()
        || url.fragment().is_some()
    {
        return Err("invalid_target".into());
    }
    target_url(&url.origin().ascii_serialization(), url.path())
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Settings {
    pub schema_version: u32,
    pub settings_revision: String,
    pub origin: Option<String>,
    pub path: String,
    pub interval_seconds: u32,
    pub identity_mode: String,
    pub bindings: Vec<ReportingBinding>,
    pub disabled_local_plcs: Vec<String>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct ReportingBinding {
    pub local_plc_id: String,
    pub instance_id: String,
    pub plc_id: String,
    pub source_generation: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ReportingIdentity {
    pub instance_id: String,
    pub plc_id: String,
    pub source_generation: String,
}
impl Settings {
    pub fn target(&self) -> LocalResult<Option<String>> {
        match &self.origin {
            Some(origin) => Ok(Some(target_url(origin, &self.path)?)),
            None => {
                target_url("http://example.invalid", &self.path)?;
                Ok(None)
            }
        }
    }
    pub fn validate(&self) -> LocalResult<()> {
        let mut local = BTreeSet::new();
        let mut remote = BTreeSet::new();
        let mut disabled = BTreeSet::new();
        if self.schema_version != 1
            || !super::local_configuration::valid_id(&self.settings_revision)
            || !(1..=3600).contains(&self.interval_seconds)
            || self
                .origin
                .as_ref()
                .map(|o| upload_origin(o).as_deref() != Ok(o.as_str()))
                .unwrap_or(false)
            || self.target().is_err()
            || self.identity_mode != "per_plc"
            || self.bindings.len() > 128
            || self.disabled_local_plcs.len() > 128
            || self
                .disabled_local_plcs
                .iter()
                .any(|id| !super::local_configuration::valid_id(id) || !disabled.insert(id))
            || self.bindings.iter().any(|b| {
                !super::local_configuration::valid_id(&b.local_plc_id)
                    || !facts_wire::id(&b.instance_id)
                    || !facts_wire::id(&b.plc_id)
                    || !facts_wire::id(&b.source_generation)
                    || !local.insert(&b.local_plc_id)
                    || !remote.insert(&b.plc_id)
            })
        {
            return Err("invalid_settings".into());
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Binding {
    pub instance_id: String,
    pub plc_id: String,
    pub db_number: u16,
    pub source_generation: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Point<'a> {
    point_id: &'a str,
    name: &'a str,
    data_type: &'a str,
    value: &'a Value,
    quality: &'static str,
    observed_at: &'a str,
    reason: Option<&'a str>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Sample<'a> {
    contract_version: &'static str,
    instance_id: &'a str,
    sample_id: &'a str,
    plc_id: &'a str,
    db_number: u16,
    group_id: &'a str,
    config_revision: &'a str,
    source_generation: &'a str,
    source_seq: &'a str,
    points: Vec<Point<'a>>,
}

/// 接收已从原字节解析且 SHA 已验证的三个对象；只按当时的不可变配置和 manifest 证明完整性。
#[cfg(test)]
pub(crate) fn build(
    sample: &SamplePayload,
    sample_sha: &str,
    manifest: &CycleManifest,
    config: &Configuration,
    instance: &str,
) -> LocalResult<String> {
    build_with_identity(sample, sample_sha, manifest, config, instance, None)
}

pub(crate) fn build_with_identity(
    sample: &SamplePayload,
    sample_sha: &str,
    manifest: &CycleManifest,
    config: &Configuration,
    instance: &str,
    reporting: Option<&ReportingIdentity>,
) -> LocalResult<String> {
    if sample.schema_version != 2
        || manifest.schema_version != 2
        || sample.instance_id != instance
        || sample.cycle_id != manifest.cycle_id
        || sample.plc_id != manifest.plc_id
        || sample.source_generation != manifest.source_generation
        || sample.source_seq != manifest.source_seq
        || sample.group_id != manifest.group_id
        || sample.revision != manifest.revision
        || sample.started_at != manifest.started_at
        || sample.finished_at != manifest.finished_at
        || sample.saved_at != manifest.saved_at
        || sample.db_number == 0
    {
        return Err("sample_context_mismatch".into());
    }
    for value in [
        instance,
        &sample.sample_id,
        &sample.plc_id,
        &sample.group_id,
        &sample.revision,
        &sample.source_generation,
    ] {
        if !facts_wire::id(value) {
            return Err("sample_identity_invalid".into());
        }
    }
    if let Some(source) = reporting {
        if [
            &source.instance_id,
            &source.plc_id,
            &source.source_generation,
        ]
        .iter()
        .any(|v| !facts_wire::id(v))
        {
            return Err("sample_identity_invalid".into());
        }
    }
    if sample
        .source_seq
        .parse::<i64>()
        .ok()
        .filter(|n| *n > 0 && *n < i64::MAX && n.to_string() == sample.source_seq)
        .is_none()
    {
        return Err("sample_identity_invalid".into());
    }
    let started = facts_wire::time(&sample.started_at)?;
    let finished = facts_wire::time(&sample.finished_at)?;
    if started > finished || finished > facts_wire::time(&sample.saved_at)? {
        return Err("sample_time_invalid".into());
    }
    if !config
        .plcs
        .iter()
        .any(|p| p.id == sample.plc_id && p.enabled)
        || !config
            .groups
            .iter()
            .any(|g| g.id == sample.group_id && g.plc_id == sample.plc_id && g.enabled)
    {
        return Err("sample_context_mismatch".into());
    }
    let dbs: Vec<_> = config
        .dbs
        .iter()
        .filter(|d| d.plc_id == sample.plc_id && d.number == sample.db_number)
        .collect();
    if dbs.len() != 1 {
        return Err("sample_context_mismatch".into());
    }
    let db = dbs[0];
    let group_points: Vec<_> = config
        .points
        .iter()
        .filter(|p| {
            p.enabled
                && p.plc_id == sample.plc_id
                && p.group_id.as_deref() == Some(&sample.group_id)
        })
        .collect();
    let all_group: BTreeSet<_> = group_points.iter().map(|p| p.id.as_str()).collect();
    let manifest_points: BTreeSet<_> = manifest
        .expected_point_ids
        .iter()
        .map(String::as_str)
        .collect();
    if all_group.len() != group_points.len()
        || manifest_points.len() != manifest.expected_point_ids.len()
        || all_group != manifest_points
    {
        return Err("sample_incomplete".into());
    }
    let db_points: Vec<_> = config
        .points
        .iter()
        .filter(|p| p.enabled && p.plc_id == sample.plc_id && p.db_id == db.id)
        .collect();
    let expected: BTreeSet<_> = db_points.iter().map(|p| p.id.as_str()).collect();
    let actual: BTreeSet<_> = sample.points.keys().map(String::as_str).collect();
    if db_points.is_empty()
        || db_points.len() > 512
        || expected.len() != db_points.len()
        || expected != actual
        || db_points
            .iter()
            .any(|p| p.group_id.as_deref() != Some(&sample.group_id))
    {
        return Err("sample_incomplete".into());
    }
    let mut member_ids = BTreeSet::new();
    let mut member_dbs = BTreeSet::new();
    if manifest
        .samples
        .iter()
        .any(|m| !member_ids.insert(&m.sample_id) || !member_dbs.insert(m.db_number))
        || !manifest.samples.iter().any(|m| {
            m.sample_id == sample.sample_id
                && m.db_number == sample.db_number
                && m.sha256 == sample_sha
        })
    {
        return Err("sample_manifest_mismatch".into());
    }
    let mut points = Vec::with_capacity(sample.points.len());
    for (id, fact) in &sample.points {
        if !facts_wire::id(id)
            || fact.definition.id != *id
            || !db_points.iter().any(|p| **p == fact.definition)
            || fact.definition.name.len() > 100
            || width(&fact.definition.data_type).is_none()
        {
            return Err("sample_point_invalid".into());
        }
        let at = wire_time(&fact.observed_at)?;
        if at < started || at > finished {
            return Err("sample_time_invalid".into());
        }
        // 本地保存细分错误质量；v2 使用 bad，同时保留原具体原因。
        let quality = match fact.quality.as_str() {
            "good" => "good",
            "bad" | "bad_read" | "bad_timeout" | "bad_decode" => "bad",
            _ => return Err("sample_point_invalid".into()),
        };
        let mut value = serde_json::to_value(fact).map_err(|_| "encoding_failed")?;
        value["quality"] = Value::String(quality.into());
        facts_wire::value_check(&value).map_err(|_| "sample_point_invalid")?;
        points.push(Point {
            point_id: id,
            name: &fact.definition.name,
            data_type: &fact.definition.data_type,
            value: &fact.value,
            quality,
            observed_at: &fact.observed_at,
            reason: fact.reason.as_deref(),
        });
    }
    let body = serde_json::to_string(&Sample {
        contract_version: CONTRACT,
        instance_id: reporting
            .map(|s| s.instance_id.as_str())
            .unwrap_or(instance),
        sample_id: &sample.sample_id,
        plc_id: reporting
            .map(|s| s.plc_id.as_str())
            .unwrap_or(&sample.plc_id),
        db_number: sample.db_number,
        group_id: &sample.group_id,
        config_revision: &sample.revision,
        source_generation: reporting
            .map(|s| s.source_generation.as_str())
            .unwrap_or(&sample.source_generation),
        source_seq: &sample.source_seq,
        points,
    })
    .map_err(|_| "encoding_failed")?;
    if body.len() > BODY_LIMIT {
        return Err("sample_body_too_large".into());
    }
    Ok(body)
}

fn wire_time(raw: &str) -> LocalResult<DateTime<FixedOffset>> {
    let bytes = raw.as_bytes();
    if bytes.get(10) != Some(&b'T')
        || !raw.ends_with("+08:00")
        || !(25..=32).contains(&bytes.len())
        || (bytes.len() > 25 && (bytes[19] != b'.' || bytes[20..bytes.len() - 6].len() > 6))
    {
        return Err("sample_time_invalid".into());
    }
    let at = facts_wire::time(raw).map_err(|_| "sample_time_invalid")?;
    if at.year() < 1000 {
        return Err("sample_time_invalid".into());
    }
    Ok(at)
}

pub(crate) fn deadline(sample: &SamplePayload) -> LocalResult<DateTime<FixedOffset>> {
    sample
        .points
        .values()
        .map(|p| {
            wire_time(&p.observed_at)?
                .checked_add_months(Months::new(3))
                .and_then(|t| t.checked_sub_signed(Duration::hours(24)))
                .ok_or_else(|| "sample_time_invalid".into())
        })
        .collect::<LocalResult<Vec<_>>>()?
        .into_iter()
        .min()
        .ok_or_else(|| "sample_incomplete".into())
}

#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Reply {
    Committed,
    Retry(&'static str),
    SourceBlocked,
    NeedsProcessing(&'static str),
    TargetMismatch,
}

fn json_media(raw: &str) -> bool {
    let mut parts = raw.split(';');
    if !parts
        .next()
        .unwrap_or("")
        .trim()
        .eq_ignore_ascii_case("application/json")
    {
        return false;
    }
    let mut charset = false;
    for part in parts {
        let Some((key, value)) = part.trim().split_once('=') else {
            return false;
        };
        if charset
            || !key.trim().eq_ignore_ascii_case("charset")
            || !value.trim().trim_matches('"').eq_ignore_ascii_case("utf-8")
        {
            return false;
        }
        charset = true;
    }
    true
}

/// 只有同一冻结样本的严格成功信封能返回 Committed；错误或非合同响应永不生成 ACK。
pub(crate) fn classify(
    status: u16,
    media: &str,
    body: &[u8],
    instance: &str,
    sample: &str,
) -> Reply {
    if matches!(status, 301..=308 | 401 | 404 | 405) {
        return Reply::TargetMismatch;
    }
    if !json_media(media) {
        return Reply::Retry("invalid_response");
    }
    let value = match pf::parse(body, 64 * 1024) {
        Ok(v) => v,
        Err(_) => return Reply::Retry("invalid_response"),
    };
    if status == 200 {
        let data = &value["data"];
        return if value["code"] == 200
            && value["message"] == "success"
            && data["contractVersion"] == CONTRACT
            && data["instanceId"] == instance
            && data["sampleId"] == sample
            && data["status"] == "committed"
            && (data["outcome"] == "created" || data["outcome"] == "duplicate")
        {
            Reply::Committed
        } else {
            Reply::Retry("invalid_receipt")
        };
    }
    let code = value["errorCode"].as_str().unwrap_or("");
    if value["code"].as_u64() != Some(status.into()) || value["data"] != Value::Null {
        return Reply::Retry("invalid_response");
    }
    match (status, code) {
        (403, "plc_facts_v2.scope_rejected") => Reply::SourceBlocked,
        (409, "plc_facts_v2.sample_content_conflict") => {
            Reply::NeedsProcessing("sample_content_conflict")
        }
        (410, "plc_facts_v2.expired_unconfirmed") => Reply::NeedsProcessing("expired_unconfirmed"),
        (413, "plc_facts_v2.payload_too_large") => Reply::NeedsProcessing("payload_too_large"),
        (415, "plc_facts_v2.media_type") => Reply::NeedsProcessing("media_type"),
        (422, "plc_facts_v2.invalid_request") => Reply::NeedsProcessing("invalid_request"),
        (503, "plc_facts_v2.not_ready") => Reply::Retry("not_ready"),
        (503, "plc_facts_v2.commit_outcome_unknown") => Reply::Retry("commit_outcome_unknown"),
        _ => Reply::Retry("invalid_response"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::{
        local_configuration::{Address, Db, Group, Plc, Point as Definition},
        local_sample::{ManifestSample, PointFact},
    };
    use serde_json::json;
    use std::collections::BTreeMap;

    #[test]
    fn configurable_url_preserves_origin_and_rejects_authority_or_query_injection() {
        assert_eq!(
            target_url("http://127.0.0.1:8000", DEFAULT_PATH).unwrap(),
            "http://127.0.0.1:8000/api/v1/integration/plc-facts/samples"
        );
        assert_eq!(
            target_url("https://example.invalid:8443", "/proxy/v2/samples").unwrap(),
            "https://example.invalid:8443/proxy/v2/samples"
        );
        for path in [
            "//other.invalid/x",
            "/\\other.invalid/x",
            "/samples?x=1",
            "/samples#fragment",
            "samples",
            "/samples\n",
        ] {
            assert!(
                target_url("http://example.invalid:8000", path).is_err(),
                "{path:?}"
            );
        }
        for origin in [
            "http://user:pass@example.invalid",
            "http://@example.invalid",
            "http://example.invalid/path",
            "file:///tmp/file",
            "http://example.invalid?q=1",
        ] {
            assert!(target_url(origin, DEFAULT_PATH).is_err(), "{origin}");
        }
        assert!(normalize_target("http://user@example.invalid/x").is_err());
    }

    fn two_db_fixture() -> (Configuration, CycleManifest, SamplePayload, SamplePayload) {
        let at = "2026-11-10T10:00:02.123+08:00";
        let mut config = Configuration::default();
        config.plcs.push(Plc {
            id: "plc".into(),
            name: "PLC".into(),
            enabled: true,
            host: "127.0.0.1".into(),
            port: 102,
            rack: 0,
            slot: 1,
            connect_timeout_ms: 1000,
            io_timeout_ms: 500,
            deadline_ms: 5000,
        });
        config.groups.push(Group {
            id: "group".into(),
            plc_id: "plc".into(),
            name: "group".into(),
            enabled: true,
            interval_ms: 1000,
        });
        let mut samples = Vec::new();
        for (number, count) in [(1, 400), (2, 512)] {
            let db = format!("db{number}");
            config.dbs.push(Db {
                id: db.clone(),
                plc_id: "plc".into(),
                source_id: "source".into(),
                name: db.clone(),
                number,
                length: 4096,
                complete: true,
                flat: true,
                tree: vec![],
                import_binding: None,
            });
            let mut points = BTreeMap::new();
            for index in 0..count {
                let id = format!("{db}-{index:03}");
                let definition = Definition {
                    id: id.clone(),
                    plc_id: "plc".into(),
                    db_id: db.clone(),
                    source_path: id.clone(),
                    name: id.clone(),
                    name_mode: None,
                    data_type: "REAL".into(),
                    comment: String::new(),
                    enabled: true,
                    group_id: Some("group".into()),
                    address: Some(Address {
                        offset: index * 4,
                        bit: None,
                        confirmed: true,
                        origin: "manual".into(),
                        reason: "test".into(),
                    }),
                };
                config.points.push(definition.clone());
                points.insert(
                    id,
                    PointFact {
                        definition,
                        value: if index == 0 {
                            Value::Null
                        } else {
                            json!(820.5)
                        },
                        observed_at: at.into(),
                        quality: if index == 0 { "bad_timeout" } else { "good" }.into(),
                        reason: (index == 0).then(|| "bad_timeout".into()),
                    },
                );
            }
            samples.push(SamplePayload {
                schema_version: 2,
                sample_id: format!("sample-{number}"),
                cycle_id: "cycle".into(),
                instance_id: "instance".into(),
                plc_id: "plc".into(),
                source_generation: "generation".into(),
                source_seq: "102".into(),
                group_id: "group".into(),
                revision: "revision".into(),
                db_number: number,
                origin: "fixture".into(),
                started_at: at.into(),
                finished_at: at.into(),
                saved_at: at.into(),
                points,
            });
        }
        let manifest = CycleManifest {
            schema_version: 2,
            cycle_id: "cycle".into(),
            plc_id: "plc".into(),
            source_generation: "generation".into(),
            source_seq: "102".into(),
            group_id: "group".into(),
            revision: "revision".into(),
            started_at: at.into(),
            finished_at: at.into(),
            saved_at: at.into(),
            expected_point_ids: config.points.iter().map(|p| p.id.clone()).collect(),
            samples: samples
                .iter()
                .map(|s| ManifestSample {
                    sample_id: s.sample_id.clone(),
                    db_number: s.db_number,
                    sha256: format!("hash-{}", s.db_number),
                })
                .collect(),
            reads: vec![],
        };
        (config, manifest, samples.remove(0), samples.remove(0))
    }

    #[test]
    fn separate_complete_db_samples_keep_original_values_and_failed_reason() {
        let (mut config, manifest, first, second) = two_db_fixture();
        for (sample, hash, count) in [(&first, "hash-1", 400), (&second, "hash-2", 512)] {
            let body = build(sample, hash, &manifest, &config, "instance").unwrap();
            let parsed: Value = serde_json::from_str(&body).unwrap();
            assert_eq!(parsed["points"].as_array().unwrap().len(), count);
            assert_eq!(parsed["sampleId"], sample.sample_id);
            assert_eq!(parsed["sourceSeq"], "102");
            assert_eq!(parsed["points"][0]["quality"], "bad");
            assert_eq!(parsed["points"][0]["value"], Value::Null);
            assert_eq!(parsed["points"][0]["reason"], "bad_timeout");
            assert_eq!(parsed["points"][1]["value"], json!(820.5));
            assert_eq!(
                parsed["points"][1]["observedAt"],
                "2026-11-10T10:00:02.123+08:00"
            );
            assert!(parsed.get("sourceType").is_none());
        }
        config.points[0].group_id = Some("other".into());
        assert!(build(&first, "hash-1", &manifest, &config, "instance").is_err());
        let mut incomplete = second.clone();
        incomplete.points.pop_first();
        assert_eq!(
            build(&incomplete, "hash-2", &manifest, &config, "instance").unwrap_err(),
            "sample_incomplete"
        );
        assert_eq!(
            deadline(&first).unwrap().to_rfc3339(),
            "2027-02-09T10:00:02.123+08:00"
        );
    }

    #[test]
    fn runtime4_preflight_retains_old_profile_limits() {
        let (mut config, _, _, _) = two_db_fixture();
        let codes = |version| {
            crate::domain::local_configuration::validate_for_runtime(&config, version)
                .into_iter()
                .map(|i| i.code)
                .collect::<Vec<_>>()
        };
        assert!(codes(3).contains(&"group_limits".to_string()));
        assert!(!codes(4).iter().any(|c| [
            "group_limits",
            "db_point_limits",
            "db_group_conflict",
            "read_budget",
            "encoding_budget"
        ]
        .contains(&c.as_str())));
        let mut extra = config.points.last().unwrap().clone();
        extra.id = "db2-extra".into();
        extra.address.as_mut().unwrap().offset += 4;
        config.points.push(extra);
        let issues = crate::domain::local_configuration::validate_for_runtime(&config, 4);
        assert!(issues.iter().any(|i| i.code == "db_point_limits"));
        config.points.pop();
        config.points[0].group_id = Some("other".into());
        let issues = crate::domain::local_configuration::validate_for_runtime(&config, 4);
        assert!(issues.iter().any(|i| i.code == "db_group_conflict"));
    }

    #[test]
    fn receipt_identity_and_contract_are_required() {
        let mut receipt = json!({"code":200,"message":"success","data":{"contractVersion":CONTRACT,"instanceId":"instance","sampleId":"sample","status":"committed","outcome":"created"}});
        let check = |v: &Value| {
            classify(
                200,
                "application/json; charset=utf-8",
                v.to_string().as_bytes(),
                "instance",
                "sample",
            )
        };
        assert_eq!(check(&receipt), Reply::Committed);
        receipt["data"]["outcome"] = json!("duplicate");
        assert_eq!(check(&receipt), Reply::Committed);
        receipt["data"]["sampleId"] = json!("other");
        assert_eq!(check(&receipt), Reply::Retry("invalid_receipt"));
        assert_eq!(
            classify(200, "text/html", b"{}", "instance", "sample"),
            Reply::Retry("invalid_response")
        );
        assert_eq!(
            classify(404, "text/html", b"", "instance", "sample"),
            Reply::TargetMismatch
        );
    }

    #[test]
    fn errors_do_not_confirm_and_retain_their_distinct_actions() {
        let response = |status: u16, error: &str| {
            json!({"code":status,"message":error,"data":null,"errorCode":error}).to_string()
        };
        for (status, code, expected) in [
            (403, "plc_facts_v2.scope_rejected", Reply::SourceBlocked),
            (
                409,
                "plc_facts_v2.sample_content_conflict",
                Reply::NeedsProcessing("sample_content_conflict"),
            ),
            (
                410,
                "plc_facts_v2.expired_unconfirmed",
                Reply::NeedsProcessing("expired_unconfirmed"),
            ),
            (
                413,
                "plc_facts_v2.payload_too_large",
                Reply::NeedsProcessing("payload_too_large"),
            ),
            (
                415,
                "plc_facts_v2.media_type",
                Reply::NeedsProcessing("media_type"),
            ),
            (
                422,
                "plc_facts_v2.invalid_request",
                Reply::NeedsProcessing("invalid_request"),
            ),
            (503, "plc_facts_v2.not_ready", Reply::Retry("not_ready")),
            (
                503,
                "plc_facts_v2.commit_outcome_unknown",
                Reply::Retry("commit_outcome_unknown"),
            ),
        ] {
            assert_eq!(
                classify(
                    status,
                    "application/json",
                    response(status, code).as_bytes(),
                    "instance",
                    "sample"
                ),
                expected
            );
        }
    }

    #[test]
    fn timestamp_precision_is_preserved_and_bounded() {
        assert!(wire_time("2026-01-31T12:34:56.123456+08:00").is_ok());
        assert!(wire_time("2026-01-31T12:34:56.1234567+08:00").is_err());
        assert!(wire_time("2026-01-31t12:34:56+08:00").is_err());
        let at = wire_time("2026-01-31T12:34:56.123456+08:00").unwrap();
        assert_eq!(
            at.checked_add_months(Months::new(3))
                .unwrap()
                .checked_sub_signed(Duration::hours(24))
                .unwrap()
                .to_rfc3339(),
            "2026-04-29T12:34:56.123456+08:00"
        );
    }
}
