//! 手动采集回环用例，配置与本次会话临时样本完全分离。
use crate::{
    contracts::{
        acquisition::{LoopbackConfig, Point},
        local_configuration::ConfigurationSnapshot,
    },
    domain::acquisition::{self as domain, RESPONSE, TARGET},
    infrastructure::acquisition::{AcquisitionHttp, Failure},
    services::local_configuration::LocalConfigurationService,
};
use reqwest::Method;
use serde::{Deserialize, Serialize};
use serde_json::{json, value::RawValue, Map, Value};
use std::sync::{Mutex, MutexGuard};

const HISTORY: &str = "/api/v1/acquisition-data/history";

#[derive(Default)]
pub struct AcquisitionSession(Mutex<Memory>);
#[derive(Default)]
struct Memory {
    generation: u64,
    preview: Option<Preview>,
}
#[derive(Clone, Copy, PartialEq, Eq)]
enum SendState {
    Ready,
    InFlight,
    Unknown,
    Done,
    Rejected,
}
#[derive(Clone)]
struct Preview {
    id: String,
    sample_id: String,
    config: LoopbackConfig,
    revision: u64,
    base: String,
    bytes: Vec<u8>,
    sampled_at: String,
    state: SendState,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PreviewView {
    id: String,
    sample_id: String,
    url: String,
    body: String,
    sampled_at: String,
}

impl AcquisitionSession {
    fn lock(&self) -> Result<MutexGuard<'_, Memory>, Failure> {
        self.0
            .lock()
            .map_err(|_| Failure::local("SMA_ACQUISITION_SESSION_UNAVAILABLE"))
    }

    pub fn invalidate(&self) -> Result<(), Failure> {
        let mut memory = self.lock()?;
        memory.generation = memory.generation.wrapping_add(1);
        memory.preview = None;
        Ok(())
    }

    fn reserve(&self, id: &str, revision: u64) -> Result<Preview, Failure> {
        let mut memory = self.lock()?;
        let preview = memory
            .preview
            .as_mut()
            .filter(|item| {
                item.id == id
                    && item.revision == revision
                    && matches!(item.state, SendState::Ready | SendState::Unknown)
            })
            .ok_or_else(invalid_preview)?;
        preview.state = SendState::InFlight;
        Ok(preview.clone())
    }
}

fn invalid_preview() -> Failure {
    Failure::local("SMA_ACQUISITION_PREVIEW_INVALID")
}

pub fn base(snapshot: &ConfigurationSnapshot) -> Result<String, String> {
    let connection = &snapshot.document.connection;
    if connection.host.is_empty() {
        return Err("SMA_ACQUISITION_CONNECTION_INVALID".into());
    }
    let host = if connection.host.contains(':') && !connection.host.starts_with('[') {
        format!("[{}]", connection.host)
    } else {
        connection.host.clone()
    };
    Ok(format!(
        "{}://{}:{}",
        connection.scheme, host, connection.port
    ))
}

fn source_valid(plc: &str, db: u16) -> Result<(), Failure> {
    if !domain::identifier(plc) || db == 0 {
        return Err(Failure::local(domain::INVALID));
    }
    Ok(())
}
fn list(value: &Value) -> Result<&[Value], Failure> {
    value["items"]
        .as_array()
        .map(Vec::as_slice)
        .ok_or_else(|| Failure::local(RESPONSE))
}

pub async fn options(snapshot: &ConfigurationSnapshot) -> Result<Value, Failure> {
    let data = AcquisitionHttp::new(&base(snapshot)?)?
        .fetch(Method::GET, "/api/v1/acquisition-data/options", &[], None)
        .await?;
    for item in list(&data)? {
        if !item["plcId"].as_str().is_some_and(domain::identifier)
            || !item["dbNumbers"].as_array().is_some_and(|values| {
                values.iter().all(|db| {
                    db.as_u64()
                        .is_some_and(|number| (1..=65_535).contains(&number))
                })
            })
        {
            return Err(Failure::local(RESPONSE));
        }
    }
    Ok(data)
}

fn displayed_point(raw: &RawValue, point: &Point) -> Result<Value, Failure> {
    let mut item: Map<String, Value> =
        serde_json::from_str(raw.get()).map_err(|_| RESPONSE.to_string())?;
    // The IPC view uses exact printable text, since JavaScript numbers also normalize representations.
    item.remove("value");
    item.insert(
        "valueText".into(),
        Value::String(point.value.get().to_owned()),
    );
    Ok(Value::Object(item))
}

pub async fn latest(
    snapshot: &ConfigurationSnapshot,
    key: &str,
    plc: &str,
    db: u16,
    selected: &[String],
) -> Result<Value, Failure> {
    domain::require_material(&snapshot.document, key)?;
    source_valid(plc, db)?;
    if selected.iter().any(|point| !domain::identifier(point)) {
        return Err(Failure::local(domain::INVALID));
    }
    #[derive(Deserialize)]
    struct Latest {
        items: Vec<Box<RawValue>>,
    }
    let data = AcquisitionHttp::new(&base(snapshot)?)?
        .fetch_raw(
            Method::GET,
            domain::LATEST,
            &[("plcId", plc), ("dbNumber", &db.to_string())],
            None,
        )
        .await?;
    let latest: Latest = serde_json::from_str(data.get()).map_err(|_| Failure::local(RESPONSE))?;
    let points = domain::point_data(&latest.items)?;
    let matching: Vec<_> = latest
        .items
        .iter()
        .zip(&points)
        .filter(|(_, point)| selected.is_empty() || selected.contains(&point.point_id))
        .map(|(raw, point)| displayed_point(raw, point))
        .collect::<Result<_, _>>()?;
    let absent: Vec<_> = selected
        .iter()
        .filter(|id| !matching.iter().any(|point| point["pointId"] == **id))
        .collect();
    Ok(json!({"items":matching, "missingPointIds":absent}))
}

pub async fn history(
    snapshot: &ConfigurationSnapshot,
    key: &str,
    plc: &str,
    db: u16,
    from: &str,
    to: &str,
    page: u32,
) -> Result<Value, Failure> {
    domain::require_material(&snapshot.document, key)?;
    source_valid(plc, db)?;
    let (start, end) = (domain::timestamp(from)?, domain::timestamp(to)?);
    if start >= end || end - start > chrono::Duration::days(7) || page == 0 {
        return Err(Failure::local("SMA_ACQUISITION_HISTORY_RANGE_INVALID"));
    }
    fetch_history(
        &AcquisitionHttp::new(&base(snapshot)?)?,
        plc,
        db,
        from,
        to,
        page,
    )
    .await
}

async fn fetch_history(
    http: &AcquisitionHttp,
    plc: &str,
    db: u16,
    from: &str,
    to: &str,
    page: u32,
) -> Result<Value, Failure> {
    let result = http
        .fetch(
            Method::GET,
            HISTORY,
            &[
                ("plcId", plc),
                ("dbNumber", &db.to_string()),
                ("from", from),
                ("to", to),
                ("page", &page.to_string()),
            ],
            None,
        )
        .await?;
    list(&result)?;
    if result["page"] != page
        || result["totalPages"].as_u64().is_none()
        || result["total"].as_u64().is_none()
    {
        return Err(Failure::local(RESPONSE));
    }
    Ok(result)
}

async fn detail(
    http: &AcquisitionHttp,
    history_id: &str,
    plc: &str,
    db: u16,
) -> Result<(Value, Vec<Point>), Failure> {
    if !history_id.parse::<u64>().is_ok_and(|id| id > 0)
        || !history_id.bytes().all(|byte| byte.is_ascii_digit())
    {
        return Err(Failure::local(domain::INVALID));
    }
    #[derive(Deserialize)]
    struct Detail {
        points: Vec<Box<RawValue>>,
        #[serde(flatten)]
        summary: Map<String, Value>,
    }
    let raw = http
        .fetch_raw(Method::GET, &format!("{HISTORY}/{history_id}"), &[], None)
        .await?;
    let detail: Detail = serde_json::from_str(raw.get()).map_err(|_| Failure::local(RESPONSE))?;
    let mut data = Value::Object(detail.summary);
    if data["id"] != history_id
        || data["plcId"] != plc
        || data["dbNumber"] != db
        || !data["sampleId"].as_str().is_some_and(domain::identifier)
        || domain::timestamp(data["sampledAt"].as_str().unwrap_or_default()).is_err()
    {
        return Err(Failure::local(RESPONSE));
    }
    let points = domain::point_data(&detail.points)?;
    if points.is_empty() {
        return Err(Failure::local("SMA_ACQUISITION_EMPTY"));
    }
    data["points"] = Value::Array(
        detail
            .points
            .iter()
            .zip(&points)
            .map(|(raw, point)| displayed_point(raw, point))
            .collect::<Result<_, _>>()?,
    );
    Ok((data, points))
}

pub async fn sample(
    snapshot: &ConfigurationSnapshot,
    key: &str,
    history_id: &str,
    plc: &str,
    db: u16,
) -> Result<Value, Failure> {
    domain::require_material(&snapshot.document, key)?;
    source_valid(plc, db)?;
    detail(
        &AcquisitionHttp::new(&base(snapshot)?)?,
        history_id,
        plc,
        db,
    )
    .await
    .map(|(data, _)| data)
}

pub async fn preview(
    session: &AcquisitionSession,
    local: &LocalConfigurationService,
    history_id: &str,
    source_seq: &str,
    revision: u64,
) -> Result<PreviewView, Failure> {
    let snapshot = local.load()?;
    if revision != snapshot.revision {
        return Err(Failure::local("SMA_CONFIGURATION_CONFLICT"));
    }
    let config = snapshot
        .document
        .acquisition_loopback
        .as_ref()
        .ok_or_else(|| Failure::local("SMA_ACQUISITION_CONFIGURATION_REQUIRED"))?;
    domain::require_material(&snapshot.document, &config.material_key)?;
    if !domain::sequence(source_seq) {
        return Err(Failure::local("SMA_ACQUISITION_SEQUENCE_INVALID"));
    }
    let generation = {
        let mut memory = session.lock()?;
        memory.preview = None;
        memory.generation = memory.generation.wrapping_add(1);
        memory.generation
    };
    let base = base(&snapshot)?;
    let (_, points) = detail(
        &AcquisitionHttp::new(&base)?,
        history_id,
        &config.plc_id,
        config.db_number,
    )
    .await?;
    let sample_id = uuid::Uuid::new_v4().to_string();
    let domain::MappedSample {
        bytes: body,
        sampled_at,
    } = domain::body(config, points, &sample_id, source_seq)?;
    if local.load()?.revision != revision {
        return Err(Failure::local("SMA_CONFIGURATION_CONFLICT"));
    }
    let mut memory = session.lock()?;
    if generation != memory.generation {
        return Err(invalid_preview());
    }
    let id = uuid::Uuid::new_v4().to_string();
    let view = PreviewView {
        id: id.clone(),
        sample_id: sample_id.clone(),
        url: format!("{base}{TARGET}"),
        body: String::from_utf8(body.clone()).map_err(|_| Failure::local(RESPONSE))?,
        sampled_at: sampled_at.clone(),
    };
    memory.preview = Some(Preview {
        id,
        revision,
        sample_id,
        config: config.clone(),
        base,
        bytes: body,
        sampled_at,
        state: SendState::Ready,
    });
    Ok(view)
}

pub async fn push(
    session: &AcquisitionSession,
    local: &LocalConfigurationService,
    id: &str,
) -> Result<Value, Failure> {
    crate::config::require_external_io()?;
    let snapshot = local.load()?;
    let item = session.reserve(id, snapshot.revision)?;
    let result = async {
        let receipt = AcquisitionHttp::new(&item.base)?
            .fetch(Method::POST, TARGET, &[], Some(item.bytes.clone()))
            .await?;
        if receipt["contractVersion"] != "plc-facts/v2"
            || receipt["instanceId"] != item.config.target.instance_id
            || receipt["sampleId"] != item.sample_id
            || receipt["status"] != "committed"
            || !matches!(receipt["outcome"].as_str(), Some("created" | "duplicate"))
        {
            return Err(Failure {
                code: "SMA_ACQUISITION_RECEIPT_MISMATCH".into(),
                status: Some(200),
                unknown: true,
            });
        }
        Ok(json!({"httpStatus":200, "receipt":receipt}))
    }
    .await;
    if let Some(current) = session
        .lock()?
        .preview
        .as_mut()
        .filter(|preview| preview.id == id)
    {
        current.state = match &result {
            Ok(_) => SendState::Done,
            Err(error) if error.unknown => SendState::Unknown,
            Err(_) => SendState::Rejected,
        };
    }
    result
}

pub async fn readback(
    session: &AcquisitionSession,
    local: &LocalConfigurationService,
    id: &str,
) -> Result<Value, Failure> {
    let revision = local.load()?.revision;
    let item = session
        .lock()?
        .preview
        .as_ref()
        .filter(|item| {
            item.id == id
                && item.revision == revision
                && matches!(item.state, SendState::Unknown | SendState::Done)
        })
        .cloned()
        .ok_or_else(invalid_preview)?;
    let time = domain::timestamp(&item.sampled_at)?;
    let from =
        (time - chrono::Duration::seconds(1)).to_rfc3339_opts(chrono::SecondsFormat::Micros, false);
    let to =
        (time + chrono::Duration::seconds(1)).to_rfc3339_opts(chrono::SecondsFormat::Micros, false);
    let http = AcquisitionHttp::new(&item.base)?;
    let target = &item.config.target;
    let mut page = 1;
    loop {
        let query =
            fetch_history(&http, &target.plc_id, target.db_number, &from, &to, page).await?;
        if let Some(row) = list(&query)?.iter().find(|row| {
            row["sampleId"] == item.sample_id && row["instanceId"] == target.instance_id
        }) {
            let history_id = row["id"].as_str().ok_or_else(|| Failure::local(RESPONSE))?;
            let (data, _) = detail(&http, history_id, &target.plc_id, target.db_number).await?;
            if data["sampleId"] != item.sample_id || data["instanceId"] != target.instance_id {
                return Err(Failure::local(RESPONSE));
            }
            return Ok(data);
        }
        if u64::from(page) >= query["totalPages"].as_u64().unwrap_or_default() {
            return Ok(Value::Null);
        }
        page = page
            .checked_add(1)
            .ok_or_else(|| Failure::local(RESPONSE))?;
    }
}
