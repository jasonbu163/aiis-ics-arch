//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/http_mapping/acceptance_tests.rs
//! Description: 通过应用的实际 HTTP／SQLite 服务验证多来源、失败、预览、收口和规模。

use std::time::{Duration, Instant};

use serde_json::{json, Value};

use super::{HttpMappingService, LocalConfigurationService};
use crate::{contracts::http_mapping::SourceState, services::http_scheduler::SchedulerSide};

#[path = "fixture.rs"]
mod fixture;
use fixture::*;

const H1_TIME: &str = "2026-11-20T13:05:10.000+08:00";
const H2_TIME: &str = "2026-11-20T13:06:20.000+08:00";
const B_TIME: &str = "2026-11-21T14:10:00.000+08:00";

fn acquisition_point(key: &str, kind: &str, at: &str) -> Value {
    let mut field = point(key, kind, at);
    field["selector"] = json!({ "path":"/data/points", "key":"/pointId", "value":if key == "observed" { "furnace" } else { key } });
    field["observedAtPath"] = json!("/observedAt");
    field["sampleIdPath"] = json!("/sampleId");
    field["qualityPath"] = json!("/quality");
    field["acceptedQuality"] = json!(["good"]);
    field
}

fn historical(id: &str, value: Value, at: &str, task_no: Value, quality: &str) -> Reply {
    let furnace =
        json!({"pointId":"furnace","value":value,"observedAt":at,"sampleId":id,"quality":"good"});
    let task =
        json!({"pointId":"task","value":task_no,"observedAt":at,"sampleId":id,"quality":quality});
    let mut fields = vec![furnace];
    if !task_no.is_null() {
        fields.push(task);
    }
    if id == "H2" {
        fields.reverse();
    }
    Reply::json(json!({"code":200,"data":{"sampleId":id,"points":fields}}))
}

fn seen(runtime: &HttpMappingService, key: &str) -> SourceState {
    runtime
        .latest()
        .unwrap()
        .into_iter()
        .find(|state| state.source_key == key)
        .unwrap()
}

async fn sample_all(runtime: &HttpMappingService, keys: &[&str]) {
    let before: Vec<_> = keys
        .iter()
        .map(|key| seen(runtime, key).snapshot.map_or(0, |s| s.version))
        .collect();
    runtime.start(SchedulerSide::Get).unwrap();
    wait_for("all source snapshots published", || {
        keys.iter().zip(&before).all(|(key, old)| {
            seen(runtime, key)
                .snapshot
                .is_some_and(|s| s.version > *old)
        })
    })
    .await;
    stop(runtime, SchedulerSide::Get).await;
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn furnace_history_and_cross_source_bindings_share_manual_and_scheduled_payload() {
    let fixture = ServerFixture::start().await;
    let profile = Profile::new();
    let runtime = &profile.runtime;
    let history = "/api/v1/acquisition-data/history/probe";
    let performance = "/api/v1/production/performance";
    fixture.set(
        history,
        historical("H1", json!(820.5), H1_TIME, json!("h1-ordinary"), "good"),
    );
    fixture.set(
        "/independent-task",
        Reply::json(
            json!({"taskValue":"b-ordinary","label":"","observedAt":B_TIME,"sampleId":"B-1"}),
        ),
    );
    fixture.set("/boolean-source", Reply::json(json!({"ready":false})));
    fixture.set(
        performance,
        Reply::json(json!({"code":200,"data":{"planSync":{"status":"updated"}}})),
    );
    let mut aa = source(
        "history",
        &format!("{}{history}", fixture.base),
        vec![
            acquisition_point("furnace", "number", "/value"),
            acquisition_point("observed", "datetime", "/observedAt"),
            acquisition_point("task", "string", "/value"),
        ],
    );
    aa["responseCondition"] = json!({"path":"/code","equals":200});
    let mut b_task = point("task", "string", "/taskValue");
    b_task["observedAtPath"] = json!("/observedAt");
    b_task["sampleIdPath"] = json!("/sampleId");
    let bb = source(
        "task-other",
        &format!("{}/independent-task", fixture.base),
        vec![b_task, point("label", "string", "/label")],
    );
    let cc = source(
        "ready-source",
        &format!("{}/boolean-source", fixture.base),
        vec![
            point("ready", "boolean", "/ready"),
            point("optional", "integer", "/missing"),
        ],
    );
    let target = target(
        "performance",
        &format!("{}{performance}", fixture.base),
        json!({"items":{"furnace":null,"omit":"old-default"},"taskNo":null,"observedAt":null,"ready":null,"zero":null,"label":null}),
        vec![
            parameter("body:taskNo", "taskNo", "string", true),
            parameter("body:furnace", "items.furnace", "number", true),
            parameter("body:observed", "observedAt", "datetime", true),
            parameter("body:ready", "ready", "boolean", true),
            parameter("body:zero", "zero", "integer", true),
            parameter("body:label", "label", "string", true),
            parameter("body:omit", "items.omit", "integer", false),
        ],
    );
    let mut first = mapping(
        "furnace-to-performance",
        "performance",
        json!({
            "body:taskNo":fact("history", "task"), "body:furnace":fact("history", "furnace"),
            "body:observed":fact("history", "observed"), "body:ready":fact("ready-source", "ready"),
            "body:zero":fixed(json!(0)), "body:label":fact("task-other", "label"), "body:omit":fact("ready-source", "optional")
        }),
    );
    first["bindings"]["body:furnace"]["valueRuleKey"] = json!("furnace-values");
    let mut shared_rule_check = first.clone();
    shared_rule_check["mappingKey"] = json!("shared-rule-check");
    shared_rule_check["enabled"] = json!(false);
    let revision = profile.merge(json!({
        "httpSources":[aa,bb,cc], "targetApis":[target], "mappingValueRules":[{
            "valueRuleKey":"furnace-values", "name":"furnace-values", "dataType":"number", "values":[820.5,861.75],
            "originSourceKey":"history", "originFactName":"furnace", "enabled":true
        }], "mappings":[first.clone(), shared_rule_check]
    }));
    let mapping_id = "mappings:furnace-to-performance";
    assert_eq!(
        runtime.test_source("history").await.unwrap().http_status,
        Some(200)
    );
    assert_eq!(fixture.count("POST"), 0);
    assert!(seen(runtime, "history").snapshot.is_none());

    sample_all(runtime, &["history", "task-other", "ready-source"]).await;
    assert_eq!(fixture.count("POST"), 0);
    let preview = runtime.preview_mapping(mapping_id, revision).unwrap();
    let h1 = preview.request.as_ref().unwrap();
    assert_eq!(
        h1.body,
        json!({"taskNo":"h1-ordinary","items":{"furnace":820.5},"observedAt":H1_TIME,"ready":false,"zero":0,"label":""})
    );
    assert_eq!(preview.sources.len(), 3);
    let history_reference = preview
        .sources
        .iter()
        .find(|reference| reference.source_key == "history")
        .unwrap();
    assert!(
        history_reference
            .points
            .iter()
            .all(|p| p.sample_id.as_deref() == Some("H1")
                && p.observed_at.as_deref() == Some(H1_TIME))
    );
    assert_eq!(preview.diagnostics.len(), 1);
    let canceled = preview.token.as_deref().unwrap();
    runtime.cancel_post(canceled);
    assert!(runtime.confirm_post(canceled).await.is_err());
    assert_eq!(fixture.count("POST"), 0);

    let current = runtime.preview_mapping(mapping_id, revision).unwrap();
    let token = current.token.as_deref().unwrap();
    let (one, two) = tokio::join!(runtime.confirm_post(token), runtime.confirm_post(token));
    assert!(one.is_ok() ^ two.is_ok());
    let acknowledged = one.or(two).unwrap();
    assert_eq!(acknowledged.status, "succeeded");
    assert_eq!(
        acknowledged
            .response
            .unwrap()
            .pointer("/data/planSync/status"),
        Some(&json!("updated"))
    );
    assert_eq!(fixture.requests("POST")[0].body.as_ref(), Some(&h1.body));

    let earlier = runtime.preview_mapping(mapping_id, revision).unwrap();
    fixture.set(
        history,
        historical("H2", json!(861.75), H2_TIME, json!("h2-ordinary"), "good"),
    );
    sample_all(runtime, &["history"]).await;
    assert!(runtime
        .confirm_post(earlier.token.as_deref().unwrap())
        .await
        .is_err());
    assert_eq!(fixture.count("POST"), 1);
    let h2 = runtime.preview_mapping(mapping_id, revision).unwrap();
    assert_eq!(h2.request.as_ref().unwrap().body["taskNo"], "h2-ordinary");
    assert_eq!(h2.request.as_ref().unwrap().body["observedAt"], H2_TIME);
    assert_eq!(
        h2.request.as_ref().unwrap().body.pointer("/items/furnace"),
        Some(&json!(861.75))
    );

    first["bindings"]["body:taskNo"] = fact("task-other", "task");
    let revision = profile.update("mappings", mapping_id, first.clone());
    assert!(runtime
        .confirm_post(h2.token.as_deref().unwrap())
        .await
        .is_err());
    let independent = runtime.preview_mapping(mapping_id, revision).unwrap();
    let expected = independent.request.as_ref().unwrap().body.clone();
    assert_eq!(expected["taskNo"], "b-ordinary");
    assert_eq!(expected["observedAt"], H2_TIME);
    let b_tasks = &independent
        .sources
        .iter()
        .find(|s| s.source_key == "task-other")
        .unwrap()
        .points;
    assert!(b_tasks
        .iter()
        .any(|point| point.observed_at.as_deref() == Some(B_TIME)
            && point.sample_id.as_deref() == Some("B-1")));
    let gets = fixture.count("GET");
    runtime.start(SchedulerSide::Post).unwrap();
    wait_for("scheduled business result", || {
        runtime
            .status()
            .mappings
            .get(mapping_id)
            .is_some_and(|row| row.status == "succeeded" && row.run_id != acknowledged.run_id)
    })
    .await;
    stop(runtime, SchedulerSide::Post).await;
    assert_eq!(fixture.count("GET"), gets);
    assert_eq!(fixture.requests("POST")[1].body.as_ref(), Some(&expected));

    first["bindings"]["body:taskNo"] = fixed(json!("fixture-fixed"));
    let revision = profile.update("mappings", mapping_id, first.clone());
    let fixed = runtime.preview_mapping(mapping_id, revision).unwrap();
    assert_eq!(fixed.request.unwrap().body["taskNo"], "fixture-fixed");
    first["bindings"]["body:taskNo"] = fact("history", "task");
    let revision = profile.update("mappings", mapping_id, first);
    for (task, quality, reason) in [
        (Value::Null, "good", "SMA_HTTP_POINT_MISSING"),
        (json!("bad-task"), "bad", "SMA_HTTP_POINT_QUALITY_REJECTED"),
        (json!(42), "good", "SMA_HTTP_POINT_TYPE_INVALID"),
    ] {
        fixture.set(
            history,
            historical("H3", json!(861.75), H2_TIME, task, quality),
        );
        sample_all(runtime, &["history"]).await;
        let blocked = runtime.preview_mapping(mapping_id, revision).unwrap();
        assert!(blocked.request.is_none() && blocked.token.is_none());
        assert!(blocked
            .diagnostics
            .iter()
            .any(|d| d.parameter_key == "body:taskNo" && d.error_code == reason));
    }
    assert_eq!(fixture.count("POST"), 2);

    let reopened =
        HttpMappingService::new(LocalConfigurationService::new(Ok(profile.path.clone())));
    let snapshot = seen(&reopened, "history");
    assert!(snapshot.from_previous_session);
    assert_eq!(
        snapshot.snapshot.unwrap().points[0].observed_at.as_deref(),
        Some(H2_TIME)
    );
    assert!(reopened.status().mappings.is_empty());
    assert!(reopened.status().last_unknown.is_empty());
    assert_eq!(fixture.count("POST"), 2);
    let backup = profile.config.export().unwrap();
    assert!(
        !backup.contains("h1-ordinary")
            && !backup.contains("lastUnknown")
            && !backup.contains("\"snapshot\"")
    );
    assert_eq!(profile.revision(), revision);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn interleaved_http_generations_do_not_mix_latest_points() {
    let fixture = ServerFixture::start().await;
    let profile = Profile::new();
    let runtime = &profile.runtime;
    fixture.set("/generation", Reply::json(json!({"left":0,"right":1000})));
    fixture.set("/pairs", Reply::json(json!({"code":200})).slow(12));
    let mut definitions = source(
        "pair-source",
        &format!("{}/generation", fixture.base),
        vec![
            point("left", "integer", "/left"),
            point("right", "integer", "/right"),
        ],
    );
    definitions["intervalMs"] = json!(15);
    let dest = target(
        "pair-target",
        &format!("{}/pairs", fixture.base),
        json!({"left":null,"right":null}),
        vec![
            parameter("body:left", "left", "integer", true),
            parameter("body:right", "right", "integer", true),
        ],
    );
    let mut route = mapping(
        "pair",
        "pair-target",
        json!({"body:left":fact("pair-source","left"),"body:right":fact("pair-source","right")}),
    );
    route["intervalMs"] = json!(15);
    profile.merge(json!({"httpSources":[definitions],"targetApis":[dest],"mappings":[route]}));
    runtime.start(SchedulerSide::Get).unwrap();
    wait_for("initial whole snapshot", || {
        seen(runtime, "pair-source").snapshot.is_some()
    })
    .await;
    runtime.start(SchedulerSide::Post).unwrap();
    for version in 0..8 {
        fixture.set(
            "/generation",
            Reply::json(json!({"left":version,"right":1000+version})),
        );
        wait_for("next fixture generation appears in outgoing POST", || {
            fixture.requests("POST").iter().any(|request| {
                request
                    .body
                    .as_ref()
                    .is_some_and(|body| body["left"] == version)
            })
        })
        .await;
    }
    stop(runtime, SchedulerSide::Get).await;
    stop(runtime, SchedulerSide::Post).await;
    let requests = fixture.requests("POST");
    assert!(requests.len() >= 8);
    for request in requests {
        let body = request.body.unwrap();
        assert_eq!(
            body["right"].as_i64().unwrap() - body["left"].as_i64().unwrap(),
            1000
        );
    }
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn whole_get_failures_keep_commit_and_expired_values_never_enter_required_body() {
    let fixture = ServerFixture::start().await;
    let profile = Profile::new();
    let runtime = &profile.runtime;
    fixture.set("/source", Reply::json(json!({"pair":{"left":0,"right":0}})));
    let mut probes = source(
        "pair-source",
        &format!("{}/source", fixture.base),
        vec![
            point("left", "integer", "/left"),
            point("right", "integer", "/right"),
        ],
    );
    probes["responsePath"] = json!("/pair");
    let dest = target(
        "pair-target",
        &format!("{}/pair-target", fixture.base),
        json!({"left":null,"right":100}),
        vec![
            parameter("body:left", "left", "integer", true),
            parameter("body:right", "right", "integer", false),
        ],
    );
    let mut binding = mapping(
        "pair",
        "pair-target",
        json!({"body:left":fact("pair-source","left"),"body:right":fact("pair-source","right")}),
    );
    let revision = profile
        .merge(json!({"httpSources":[probes],"targetApis":[dest],"mappings":[binding.clone()]}));
    sample_all(runtime, &["pair-source"]).await;
    let before = seen(runtime, "pair-source").snapshot.unwrap();
    let db = rusqlite::Connection::open(&profile.path).unwrap();
    db.execute_batch("CREATE TRIGGER fault_probe BEFORE UPDATE ON http_source_latest BEGIN SELECT RAISE(ABORT,'fixture write failure'); END;").unwrap();
    for (reply, code) in [
        (Reply::new(200, ""), "SMA_HTTP_SOURCE_JSON_INVALID"),
        (Reply::new(503, "{}"), "SMA_HTTP_SOURCE_HTTP_FAILED"),
        (
            Reply::json(json!({"pair":{"left":1,"right":2}})).slow(300),
            "SMA_HTTP_TIMED_OUT",
        ),
        (
            Reply::json(json!({"invalid":"responsePath"})),
            "SMA_HTTP_SOURCE_RESPONSE_PATH_MISSING",
        ),
        (
            Reply::json(json!({"pair":{"left":1,"right":2}})),
            "SMA_CONFIGURATION_STORAGE_FAILED",
        ),
    ] {
        fixture.set("/source", reply);
        runtime.start(SchedulerSide::Get).unwrap();
        wait_for(code, || {
            seen(runtime, "pair-source").last_error_code.as_deref() == Some(code)
        })
        .await;
        stop(runtime, SchedulerSide::Get).await;
        let snapshot = seen(runtime, "pair-source").snapshot.unwrap();
        assert_eq!(
            serde_json::to_value(snapshot).unwrap(),
            serde_json::to_value(&before).unwrap()
        );
    }
    db.execute_batch("DROP TRIGGER fault_probe").unwrap();
    assert_eq!(fixture.count("POST"), 0);
    assert_eq!(profile.revision(), revision);
    assert_eq!(
        runtime
            .preview_mapping("mappings:pair", revision)
            .unwrap()
            .request
            .unwrap()
            .body,
        json!({"left":0,"right":0})
    );
    binding["maxAgeMs"] = json!(1);
    let revision = profile.update("mappings", "mappings:pair", binding.clone());
    tokio::time::sleep(Duration::from_millis(5)).await;
    let blocked = runtime.preview_mapping("mappings:pair", revision).unwrap();
    assert!(blocked.request.is_none());
    assert!(blocked
        .diagnostics
        .iter()
        .any(|d| d.error_code == "SMA_HTTP_SNAPSHOT_STALE" && d.parameter_key == "body:left"));
    binding["bindings"]["body:left"] = fixed(json!(0));
    let revision = profile.update("mappings", "mappings:pair", binding);
    let optional = runtime.preview_mapping("mappings:pair", revision).unwrap();
    assert_eq!(optional.request.unwrap().body, json!({"left":0}));
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn receipts_distinguish_business_rejection_transport_unknown_and_next_cycle() {
    let fixture = ServerFixture::start().await;
    let profile = Profile::new();
    let runtime = &profile.runtime;
    let dest = target(
        "receiver",
        &format!("{}/receive", fixture.base),
        json!({"v":null}),
        vec![parameter("body:v", "v", "integer", true)],
    );
    let mut route = mapping("ready", "receiver", json!({"body:v":fixed(json!(0))}));
    route["intervalMs"] = json!(450);
    let revision = profile.merge(json!({"targetApis":[dest],"mappings":[route]}));
    let mapping = "mappings:ready";
    for (reply, status, error) in [
        (Reply::new(500, "{}"), "failed", "SMA_HTTP_POST_HTTP_FAILED"),
        (
            Reply::json(json!({"code":409})),
            "failed",
            "SMA_HTTP_BUSINESS_REJECTED",
        ),
        (
            Reply::new(200, "unparseable"),
            "unknown",
            "SMA_HTTP_RECEIPT_INVALID",
        ),
        (
            Reply::json(json!({"code":200})).slow(300),
            "unknown",
            "SMA_HTTP_TIMED_OUT",
        ),
        (
            Reply::close_connection(),
            "unknown",
            "SMA_HTTP_TRANSPORT_INTERRUPTED",
        ),
    ] {
        fixture.set("/receive", reply);
        let count = fixture.count("POST");
        let preview = runtime.preview_mapping(mapping, revision).unwrap();
        let token = preview.token.as_deref().unwrap();
        let result = runtime.confirm_post(token).await.unwrap();
        assert_eq!(result.status, status);
        assert_eq!(result.error_code.as_deref(), Some(error));
        assert!(runtime.confirm_post(token).await.is_err());
        assert_eq!(fixture.count("POST"), count + 1);
    }
    let count = fixture.count("POST");
    let reopened =
        HttpMappingService::new(LocalConfigurationService::new(Ok(profile.path.clone())));
    tokio::time::sleep(Duration::from_millis(520)).await;
    assert_eq!(fixture.count("POST"), count);
    assert!(reopened.status().mappings.is_empty());

    runtime.start(SchedulerSide::Post).unwrap();
    let prior = runtime
        .status()
        .last_unknown
        .get(mapping)
        .unwrap()
        .run_id
        .clone();
    wait_for("first scheduled unknown", || {
        runtime
            .status()
            .last_unknown
            .get(mapping)
            .is_some_and(|r| r.run_id != prior)
    })
    .await;
    let unknown = runtime.status().last_unknown[mapping].run_id.clone();
    fixture.set("/receive", Reply::json(json!({"code":200})));
    wait_for("next scheduled response", || {
        runtime
            .status()
            .mappings
            .get(mapping)
            .is_some_and(|r| r.run_id != unknown && r.status == "succeeded")
    })
    .await;
    stop(runtime, SchedulerSide::Post).await;
    assert_eq!(runtime.status().last_unknown[mapping].run_id, unknown);
    assert_eq!(fixture.count("POST"), count + 2);
    assert!(fixture
        .requests("POST")
        .iter()
        .all(|request| request.body.as_ref() == Some(&json!({"v":0}))));
}

#[tokio::test(flavor = "multi_thread", worker_threads = 6)]
async fn measured_full_profile_with_128_gets_and_384_mappings() {
    let fixture = ServerFixture::start().await;
    let profile = Profile::new();
    let runtime = &profile.runtime;
    fixture.set("/source", Reply::json(json!({"val":2})).slow(18));
    fixture.set("/normal", Reply::json(json!({"code":200})).slow(18));
    fixture.set("/slow", Reply::json(json!({"code":200})).slow(115));
    let sources: Vec<_> = (0..128)
        .map(|index| {
            let mut definition = source(
                &format!("source-{index}"),
                &format!("{}/source", fixture.base),
                vec![point("value", "integer", "/val")],
            );
            definition["query"]["line"] = json!(index.to_string());
            definition["intervalMs"] = json!(210);
            definition["timeoutMs"] = json!(1_500);
            definition
        })
        .collect();
    let targets: Vec<_> = ["normal", "slow"]
        .iter()
        .map(|key| {
            let mut receiver = target(
                key,
                &format!("{}/{key}", fixture.base),
                json!({"v":null}),
                vec![parameter("body:v", "v", "integer", true)],
            );
            receiver["timeoutMs"] = json!(1_500);
            receiver
        })
        .collect();
    let mappings: Vec<_> = (0..384)
        .map(|index| {
            let mut line = mapping(
                &format!("line-{index}"),
                if index < 96 { "slow" } else { "normal" },
                json!({"body:v":fact("source-0","value")}),
            );
            line["intervalMs"] = json!(450);
            line
        })
        .collect();
    let revision = profile.merge(json!({"httpSources":sources,"targetApis":targets,"mappings":mappings,
        "runtimeLimits":{"getConcurrency":6,"getQueue":12,"postConcurrency":7,"postQueue":18,"perTargetConcurrency":3}}));
    runtime.start(SchedulerSide::Get).unwrap();
    runtime.start(SchedulerSide::Get).unwrap();
    wait_for("source available for volume check", || {
        seen(runtime, "source-0").snapshot.is_some()
    })
    .await;
    assert_eq!(fixture.count("POST"), 0);
    let baseline = runtime.status();
    let started = Instant::now();
    runtime.start(SchedulerSide::Post).unwrap();
    runtime.start(SchedulerSide::Post).unwrap();
    wait_for("all lanes progress", || {
        let (methods, paths) = fixture.traffic();
        methods.get("GET").is_some_and(|g| g.completed >= 5)
            && ["/normal", "/slow"].iter().all(|path| {
                paths
                    .get(*path)
                    .is_some_and(|counter| counter.completed >= 4)
            })
    })
    .await;
    tokio::time::sleep(Duration::from_secs(2)).await;
    let halfway = fixture.traffic().1["/normal"].completed;
    tokio::time::sleep(Duration::from_secs(2)).await;
    let elapsed = started.elapsed().as_secs_f64();
    let aggregate = runtime.status();
    let (methods, paths) = fixture.traffic();
    assert!((2..=6).contains(&methods["GET"].peak));
    assert!((2..=7).contains(&methods["POST"].peak));
    assert!((1..=3).contains(&paths["/normal"].peak));
    assert!((1..=3).contains(&paths["/slow"].peak));
    assert!(paths["/normal"].completed > halfway);
    assert!(
        (1..=12).contains(&aggregate.get.peak_queued)
            && (1..=18).contains(&aggregate.post.peak_queued)
    );
    assert!(aggregate.get.saturated > 0 && aggregate.post.saturated > 0);
    assert_eq!(aggregate.get.failed + aggregate.post.failed, 0);
    eprintln!(
        "{}",
        json!({"seconds":elapsed,"getRoutes":128,"mappings":384,"normalCompletedInFirstHalf":halfway,
        "fixtureMethods":methods,"fixturePaths":paths,"get":aggregate.get,"post":aggregate.post,
        "completedGetPerSecond":(aggregate.get.completed - baseline.get.completed) as f64 / elapsed,
        "completedPostPerSecond":(aggregate.post.completed - baseline.post.completed) as f64 / elapsed})
    );
    stop(runtime, SchedulerSide::Get).await;
    let gets = fixture.count("GET");
    let posts = fixture.count("POST");
    wait_for("reporting continues after collection stops", || {
        fixture.count("POST") > posts
    })
    .await;
    stop(runtime, SchedulerSide::Post).await;
    assert_eq!(fixture.count("GET"), gets);
    assert!(runtime.drained());
    assert_eq!(profile.revision(), revision);
}
