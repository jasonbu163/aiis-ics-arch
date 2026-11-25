//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/http_scheduler/tests.rs
//! Description: 用隔离请求验证独立停止、流量限制及 128 GET／384 POST 的线路规模。

use std::sync::atomic::{AtomicUsize, Ordering};

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use tokio::sync::Notify;

use super::*;

const LIMITS: SchedulerLimits = SchedulerLimits {
    concurrency: 2,
    queue: 2,
    per_target: 1,
};

async fn wait_until(condition: impl Fn() -> bool) {
    time::timeout(Duration::from_secs(3), async {
        while !condition() {
            time::sleep(Duration::from_millis(5)).await;
        }
    })
    .await
    .expect("scheduler did not reach expected state");
}

#[tokio::test]
async fn stopping_clears_queued_work_and_checks_transport_boundary() {
    let scheduler = HttpScheduler::default();
    let release = Arc::new(Notify::new());
    let entered = Arc::new(AtomicUsize::new(0));
    let network = Arc::new(AtomicUsize::new(0));
    scheduler.start(
        SchedulerSide::Get,
        || async {
            Ok(SchedulerBatch {
                limits: LIMITS,
                jobs: (0..5)
                    .map(|i| ScheduledJob {
                        key: i.to_string(),
                        target: None,
                        interval_ms: 30,
                    })
                    .collect(),
            })
        },
        {
            let release = release.clone();
            let entered = entered.clone();
            let network = network.clone();
            move |_, activity| {
                let release = release.clone();
                let entered = entered.clone();
                let network = network.clone();
                async move {
                    entered.fetch_add(1, Ordering::Relaxed);
                    release.notified().await;
                    if let Ok(_http) = activity.begin_http() {
                        network.fetch_add(1, Ordering::Relaxed);
                        JobResult::Completed
                    } else {
                        JobResult::Discarded
                    }
                }
            }
        },
    );
    wait_until(|| {
        entered.load(Ordering::Relaxed) == 2 && scheduler.status(SchedulerSide::Get).queued == 2
    })
    .await;
    let stopped = scheduler.stop(SchedulerSide::Get);
    assert_eq!(stopped.queued, 0);
    assert_eq!(stopped.discarded, 2);
    assert_eq!(stopped.phase, SchedulerPhase::Stopping);
    assert_eq!(stopped.in_flight, 0);
    release.notify_waiters();
    wait_until(|| scheduler.status(SchedulerSide::Get).phase == SchedulerPhase::Stopped).await;
    assert_eq!(network.load(Ordering::Relaxed), 0);
    assert_eq!(scheduler.status(SchedulerSide::Get).discarded, 4);
}

#[test]
fn direct_tests_share_caps_and_unknown_outcomes_release_the_slot() {
    let scheduler = HttpScheduler::default();
    let target = Some("sample-target".to_owned());
    let pending = scheduler
        .try_manual(
            SchedulerSide::Post,
            &LIMITS,
            "first".to_owned(),
            target.clone(),
        )
        .unwrap();
    assert!(scheduler
        .try_manual(
            SchedulerSide::Post,
            &LIMITS,
            "second".to_owned(),
            target.clone()
        )
        .is_err());
    let transport = pending.activity().begin_http().unwrap();
    assert_eq!(scheduler.status(SchedulerSide::Post).in_flight, 1);
    drop(transport);
    drop(pending);
    let second = scheduler
        .try_manual(SchedulerSide::Post, &LIMITS, "second".to_owned(), target)
        .unwrap();
    second.finish(JobResult::Blocked);
    let result = scheduler.status(SchedulerSide::Post);
    assert_eq!(result.unknown, 1);
    assert_eq!(result.blocked, 1);
    assert_eq!(result.peak_in_flight, 1);
    assert_eq!(result.in_flight, 0);
    assert_eq!(result.active, 0);
}

#[derive(Default, Clone, Copy, Debug, Serialize)]
struct Traffic {
    active: usize,
    peak: usize,
    completed: usize,
}

impl Traffic {
    fn enter(&mut self) {
        self.active += 1;
        self.peak = self.peak.max(self.active);
    }

    fn complete(&mut self) {
        self.active -= 1;
        self.completed += 1;
    }
}

#[derive(Default, Debug, Serialize)]
struct FixtureCounts {
    get: Traffic,
    post: Traffic,
    fast: Traffic,
    slow: Traffic,
}

impl FixtureCounts {
    fn lanes(&mut self, route: &str) -> (&mut Traffic, Option<&mut Traffic>) {
        match route {
            "/fast" => (&mut self.post, Some(&mut self.fast)),
            "/slow" => (&mut self.post, Some(&mut self.slow)),
            _ => (&mut self.get, None),
        }
    }
}

async fn fixture() -> (
    String,
    Arc<Mutex<FixtureCounts>>,
    tokio::task::JoinHandle<()>,
) {
    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = format!("http://{}", listener.local_addr().unwrap());
    let counts = Arc::new(Mutex::new(FixtureCounts::default()));
    let shared_counts = counts.clone();
    let task = tokio::spawn(async move {
        while let Ok((mut socket, _)) = listener.accept().await {
            let counts = shared_counts.clone();
            tokio::spawn(async move {
                let mut headers = Vec::new();
                let mut piece = [0; 1024];
                while !headers.windows(4).any(|window| window == b"\r\n\r\n") {
                    let Ok(size) = socket.read(&mut piece).await else {
                        return;
                    };
                    if size == 0 || headers.len() > 4096 {
                        return;
                    }
                    headers.extend_from_slice(&piece[..size]);
                }
                let headers = String::from_utf8_lossy(&headers);
                let route = headers.split_whitespace().nth(1).unwrap_or("/get");
                {
                    let mut counts = counts.lock().unwrap();
                    let (side, target) = counts.lanes(route);
                    side.enter();
                    if let Some(target) = target {
                        target.enter();
                    }
                }
                let delay = if route == "/slow" { 80 } else { 14 };
                time::sleep(Duration::from_millis(delay)).await;
                {
                    let mut counts = counts.lock().unwrap();
                    let (side, target) = counts.lanes(route);
                    side.complete();
                    if let Some(target) = target {
                        target.complete();
                    }
                }
                let _ = socket
                    .write_all(
                        b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}",
                    )
                    .await;
            });
        }
    });
    (address, counts, task)
}

fn start_load_lane(
    scheduler: &HttpScheduler,
    side: SchedulerSide,
    address: &str,
    sources: usize,
    limits: SchedulerLimits,
) {
    let jobs: Vec<_> = (0..sources)
        .map(|i| ScheduledJob {
            key: i.to_string(),
            target: (side == SchedulerSide::Post)
                .then(|| if i < sources / 4 { "/slow" } else { "/fast" }.to_owned()),
            interval_ms: 180,
        })
        .collect();
    let address = address.to_owned();
    let client = reqwest::Client::builder()
        .no_proxy()
        .timeout(Duration::from_secs(2))
        .build()
        .unwrap();
    scheduler.start(
        side,
        move || {
            let jobs = jobs.clone();
            async move { Ok(SchedulerBatch { limits, jobs }) }
        },
        move |job, activity| {
            let url = format!("{address}{}", job.target.as_deref().unwrap_or("/get"));
            let request = match side {
                SchedulerSide::Get => client.get(url),
                SchedulerSide::Post => client.post(url),
            };
            async move {
                let Ok(_transport) = activity.begin_http() else {
                    return JobResult::Discarded;
                };
                match request.send().await {
                    Ok(response) => match response.bytes().await {
                        Ok(_) => JobResult::Completed,
                        Err(_) => JobResult::Failed,
                    },
                    Err(error) if error.is_timeout() => JobResult::TimedOut,
                    Err(_) => JobResult::Failed,
                }
            }
        },
    );
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn measured_isolated_scheduler_load() {
    let (address, counts, fixture) = fixture().await;
    let scheduler = HttpScheduler::default();
    let get_limits = SchedulerLimits {
        concurrency: 6,
        queue: 12,
        per_target: 6,
    };
    let post_limits = SchedulerLimits {
        concurrency: 7,
        queue: 18,
        per_target: 3,
    };
    let started = Instant::now();
    start_load_lane(&scheduler, SchedulerSide::Get, &address, 128, get_limits);
    start_load_lane(&scheduler, SchedulerSide::Post, &address, 384, post_limits);
    wait_until(|| {
        let counts = counts.lock().unwrap();
        counts.get.completed >= 3 && counts.fast.completed >= 3 && counts.slow.completed >= 3
    })
    .await;
    time::sleep(Duration::from_millis(1_200)).await;
    let halfway = counts.lock().unwrap().fast.completed;
    time::sleep(Duration::from_millis(1_200)).await;
    let window = started.elapsed().as_secs_f64();
    let get_window = scheduler.status(SchedulerSide::Get);
    let post_window = scheduler.status(SchedulerSide::Post);
    {
        let counts = counts.lock().unwrap();
        assert!((2..=get_limits.concurrency).contains(&counts.get.peak));
        assert!((2..=post_limits.concurrency).contains(&counts.post.peak));
        assert!((1..=post_limits.per_target).contains(&counts.fast.peak));
        assert!((1..=post_limits.per_target).contains(&counts.slow.peak));
        assert!(counts.fast.completed > halfway);
        eprintln!(
            "{}",
            serde_json::json!({
                "seconds": window,
                "getRoutes": 128,
                "postRoutes": 384,
                "observedByFixture": &*counts,
                "getPerSecond": get_window.completed as f64 / window,
                "postPerSecond": post_window.completed as f64 / window,
                "getScheduler": &get_window,
                "postScheduler": &post_window,
            })
        );
    }
    assert!((1..=get_limits.queue).contains(&get_window.peak_queued));
    assert!((1..=post_limits.queue).contains(&post_window.peak_queued));
    assert!(get_window.saturated > 0 && post_window.saturated > 0);
    assert_eq!(get_window.failed + post_window.failed, 0);

    scheduler.stop(SchedulerSide::Get);
    wait_until(|| scheduler.status(SchedulerSide::Get).phase == SchedulerPhase::Stopped).await;
    let (get_done, post_done) = {
        let counts = counts.lock().unwrap();
        (counts.get.completed, counts.post.completed)
    };
    wait_until(|| counts.lock().unwrap().post.completed > post_done).await;
    assert_eq!(counts.lock().unwrap().get.completed, get_done);
    assert_eq!(
        scheduler.status(SchedulerSide::Post).phase,
        SchedulerPhase::Running
    );
    scheduler.stop_all();
    wait_until(|| scheduler.status(SchedulerSide::Post).phase == SchedulerPhase::Stopped).await;
    fixture.abort();
}
