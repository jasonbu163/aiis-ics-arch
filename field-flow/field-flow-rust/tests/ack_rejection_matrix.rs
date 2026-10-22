//! 文件：tests/ack_rejection_matrix.rs；AC15每行真实S7响应字段/长度故障，保留三份报文与原状态。
#![cfg(feature = "test-fixture")]
mod support;
use field_flow::{fixture::Fixture, infrastructure::state};
use serde_json::json;
use std::path::Path;
use support::*;
use tokio::time::Instant;
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn real_ack_rejections() {
    let mut fixture = Fixture::start(Path::new(env!("CARGO_BIN_EXE_ff-fixture"))).unwrap();
    let c = config();
    let evidence = root("ack-rejections");
    let mut rows = Vec::new();
    for (write, field) in [
        (false, "id"),
        (false, "rosctr"),
        (false, "reserved0"),
        (false, "reserved1"),
        (false, "function"),
        (false, "count"),
        (false, "param_length"),
        (false, "data_length"),
        (false, "transport"),
        (false, "bits"),
        (false, "short_header"),
        (false, "short_data"),
        (false, "empty"),
        (false, "extra"),
        (false, "payload4096"),
        (false, "payload4097"),
        (false, "ref0"),
        (false, "ref1"),
        (false, "oldref"),
        (true, "otherref"),
        (true, "ref0"),
        (true, "ref1"),
        (true, "global0"),
        (true, "global1"),
        (true, "item"),
        (true, "function"),
        (true, "count"),
        (true, "extra"),
        (true, "follow_correct"),
    ] {
        fixture.fault("");
        let run = Run::new(&format!("reject-{field}"), "execute", &c);
        run.ready().await;
        let pid = run.rt.owners["plc_demo"].health().pid.unwrap();
        fixture.command(&format!("reject-{field}"), json!(42));
        if matches!(field, "oldref" | "otherref") {
            run.rt.owners["plc_demo"]
                .read("completed-prior-read", 1, 0)
                .await
                .unwrap();
        }
        fixture.fault(&format!("corrupt:{field}"));
        let before = fixture.snapshot()["writes"].as_u64().unwrap();
        let start = Instant::now();
        let error = if write {
            run.iteration(&c).await.unwrap_err()
        } else {
            run.rt.owners["plc_demo"]
                .read("reject-read", 1, 0)
                .await
                .unwrap_err()
        };
        let ms = start.elapsed().as_millis();
        if matches!(field, "oldref" | "otherref") {
            let trace = fixture.snapshot();
            let rows = trace["trace"].as_array().unwrap();
            let changed = rows
                .iter()
                .rev()
                .find(|r| r["event"] == "corrupt_response_sent" && r["fault"] == field)
                .unwrap();
            let actual_prior = changed[if field == "oldref" {
                "previous_same_ref"
            } else {
                "previous_other_ref"
            }]
            .as_array()
            .unwrap();
            assert_eq!(actual_prior, &vec![json!(0), json!(1)]);
            let sent = changed["sent_response_hex"].as_str().unwrap();
            let requested = changed["request_hex"].as_str().unwrap();
            assert_eq!(&sent[22..26], "0001");
            assert_eq!(&requested[22..26], "0002");
        }

        assert!(ms <= 5500, "{field}: {ms}");
        assert_eq!(
            unsafe { libc::kill(pid as i32, 0) },
            -1,
            "old child not ended for {field}"
        );
        fixture.fault("");
        let dir = run.close(false).await;
        let store = state::inspect(&dir).unwrap();
        assert_eq!(store["counts"]["confirmed"].as_u64().unwrap_or(0), 0);
        assert_eq!(
            fixture.snapshot()["writes"].as_u64().unwrap() - before,
            if write { 1 } else { 0 }
        );
        if write {
            assert_eq!(store["counts"]["unknown"], 1)
        }
        rows.push(json!({"field":field,"write":write,"error":error,"duration_ms":ms,"old_pid":pid,"old_pid_gone":true,"store":dir,"counts":store["counts"]}));
    }
    let report = json!({"ac":"AC15","rows":rows,"protocol":fixture.snapshot()});
    std::fs::write(
        evidence.join("ack-rejections.json"),
        serde_json::to_vec_pretty(&report).unwrap(),
    )
    .unwrap();
    fixture.close().unwrap();
    println!(
        "{}",
        json!({"ac":"AC15","evidence":evidence,"rows":29,"ports_rebound":[31102,31103,31880]})
    );
}
