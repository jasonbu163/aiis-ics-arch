//! 单调时钟组调度与完整读轮：独立周期、最早到期公平选择、错过tick不追读，deadline保留失败成员。
use crate::domain::{local_configuration::*, local_runtime::GroupState, local_sample::*};
use crate::infrastructure::{local_decode, managed_s7::Transport};
use serde_json::Value;
use std::{
    collections::BTreeMap,
    time::{Duration, Instant},
};
pub(crate) struct Schedule {
    pub group: Group,
    pub due: Instant,
    pub missed: u64,
    pub last_duration: u64,
}
pub(crate) fn schedules(c: &Configuration, plc: &str) -> Vec<Schedule> {
    c.groups
        .iter()
        .filter(|g| {
            g.plc_id == plc
                && g.enabled
                && c.points
                    .iter()
                    .any(|p| p.enabled && p.group_id.as_deref() == Some(&g.id))
        })
        .map(|g| Schedule {
            group: g.clone(),
            due: Instant::now(),
            missed: 0,
            last_duration: 0,
        })
        .collect()
}
pub(crate) fn due(groups: &[Schedule], now: Instant) -> Option<usize> {
    groups
        .iter()
        .enumerate()
        .filter(|(_, g)| g.due <= now)
        .min_by_key(|(i, g)| (g.due, *i))
        .map(|(i, _)| i)
}
pub(crate) fn finish(g: &mut Schedule, started: Instant, finished: Instant) {
    g.last_duration = finished.duration_since(started).as_millis() as u64;
    let step = Duration::from_millis(g.group.interval_ms);
    g.due += step;
    while g.due <= finished {
        let missed =
            finished.duration_since(g.due).as_millis() / u128::from(g.group.interval_ms) + 1;
        g.missed = g.missed.saturating_add(missed as u64);
        g.due += Duration::from_millis(g.group.interval_ms.saturating_mul(missed as u64));
    }
}
pub(crate) fn states(gs: &[Schedule]) -> Vec<GroupState> {
    gs.iter()
        .map(|g| GroupState {
            group_id: g.group.id.clone(),
            interval_ms: g.group.interval_ms,
            duration_ms: g.last_duration,
            missed_ticks: g.missed,
        })
        .collect()
}
pub(crate) fn collect(
    c: &Configuration,
    p: &Plc,
    g: &Group,
    revision: &str,
    transport: &mut dyn Transport,
    origin: &str,
) -> LocalResult<CycleInput> {
    let start = Instant::now();
    let started = now();
    let mut reads = vec![];
    let mut chunks: BTreeMap<u16, Vec<(u32, u32, Vec<u8>, String, String)>> = BTreeMap::new();
    let ranges = segments(c, g)?;
    for s in ranges {
        let t = Instant::now();
        let at = now();
        let result = if start.elapsed().as_millis() >= u128::from(p.deadline_ms) {
            Err("bad_timeout".into())
        } else {
            transport.read_bounded(
                s.db_number,
                s.start,
                s.size,
                Duration::from_millis(u64::from(p.deadline_ms)).saturating_sub(start.elapsed()),
            )
        };
        let result = if start.elapsed() >= Duration::from_millis(u64::from(p.deadline_ms)) {
            Err("bad_timeout".into())
        } else {
            result
        };
        let finish = now();
        let quality = if result.is_ok() {
            "good"
        } else if result
            .as_ref()
            .err()
            .map(|s| s == "bad_timeout")
            .unwrap_or(false)
        {
            "bad_timeout"
        } else {
            "bad_read"
        };
        reads.push(ReadTiming {
            db_number: s.db_number,
            start: s.start,
            size: s.size,
            started_at: at,
            finished_at: finish.clone(),
            duration_ms: t.elapsed().as_millis() as u64,
            quality: quality.into(),
        });
        chunks.entry(s.db_number).or_default().push((
            s.start,
            s.size,
            result.unwrap_or_default(),
            finish,
            quality.into(),
        ));
    }
    let mut points: BTreeMap<u16, BTreeMap<String, PointFact>> = BTreeMap::new();
    for point in c
        .points
        .iter()
        .filter(|x| x.enabled && x.group_id.as_deref() == Some(&g.id))
    {
        let d = c
            .dbs
            .iter()
            .find(|d| d.id == point.db_id)
            .ok_or("db_missing")?;
        let a = point.address.as_ref().ok_or("address_required")?;
        let n = width(&point.data_type).ok_or("unsupported_type")?;
        let mut b = Vec::new();
        let mut quality = "good".to_string();
        let mut observed = started.clone();
        for offset in a.offset..a.offset + n {
            let found = chunks.get(&d.number).and_then(|cs| {
                cs.iter()
                    .find(|(s, n, _, _, _)| offset >= *s && offset < *s + *n)
            });
            if let Some((s, _, data, at, q)) = found {
                observed = at.clone();
                if q != "good" {
                    quality = q.clone();
                    break;
                }
                if let Some(byte) = data.get((offset - s) as usize) {
                    b.push(*byte)
                } else {
                    quality = "bad_read".into();
                    break;
                }
            } else {
                quality = "bad_read".into();
                break;
            }
        }

        let (value, reason) = if quality != "good" {
            (Value::Null, Some(quality.clone()))
        } else {
            match local_decode::decode(point, &b) {
                Ok(v) => (v, None),
                Err(e) => {
                    quality = "bad_decode".into();
                    (Value::Null, Some(e))
                }
            }
        };
        points.entry(d.number).or_default().insert(
            point.id.clone(),
            PointFact {
                definition: point.clone(),
                value,
                observed_at: observed,
                quality,
                reason,
            },
        );
    }
    Ok(CycleInput {
        plc_id: p.id.clone(),
        group_id: g.id.clone(),
        revision: revision.into(),
        started_at: started,
        finished_at: now(),
        origin: origin.into(),
        points,
        reads,
    })
}
