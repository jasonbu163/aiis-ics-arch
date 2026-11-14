//! HTTP目标guard纯验证；不bind、不创建客户端网络请求。
use super::*;
#[test]
fn exact_origins() {
    for input in ["http://example.invalid", "https://example.invalid:8443"] {
        assert_eq!(normalize_origin(input).unwrap(), input);
    }
    for input in [
        "file:///tmp/x",
        "https://user:pass@example.invalid",
        "https://example.invalid/x",
        "https://example.invalid?x=1",
        "https://example.invalid#x",
        " https://example.invalid",
    ] {
        assert!(normalize_origin(input).is_err());
    }
}

#[test]
fn v2_rejects_oversize_and_url_credentials_before_network() {
    let http = FactsHttp::new().unwrap();
    let oversized = "x".repeat(crate::domain::sample_upload::BODY_LIMIT + 1);
    assert_eq!(
        http.post_sample("http://127.0.0.1:1", &oversized)
            .unwrap_err(),
        "payload_too_large"
    );
    assert_eq!(
        http.post_sample("http://user:pass@127.0.0.1:1", "{}")
            .unwrap_err(),
        "invalid_target"
    );
}

#[test]
fn v2_loopback_posts_original_utf8_to_sample_path_without_bearer() {
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::time::Duration;
    let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
    let origin = format!("http://{}", listener.local_addr().unwrap());
    let worker = std::thread::spawn(move || {
        let mut seen = Vec::new();
        for index in 0..2 {
            let (mut stream, _) = listener.accept().unwrap();
            stream
                .set_read_timeout(Some(Duration::from_secs(5)))
                .unwrap();
            let mut bytes = Vec::new();
            let mut buffer = [0u8; 16384];
            let (head_end, length) = loop {
                let n = stream.read(&mut buffer).unwrap();
                assert!(n > 0);
                bytes.extend_from_slice(&buffer[..n]);
                if let Some(at) = bytes.windows(4).position(|w| w == b"\r\n\r\n") {
                    let head = std::str::from_utf8(&bytes[..at]).unwrap();
                    let length = head
                        .lines()
                        .find_map(|line| {
                            line.to_ascii_lowercase()
                                .strip_prefix("content-length:")
                                .map(|v| v.trim().parse::<usize>().unwrap())
                        })
                        .unwrap();
                    break (at + 4, length);
                }
            };
            while bytes.len() - head_end < length {
                let n = stream.read(&mut buffer).unwrap();
                assert!(n > 0);
                bytes.extend_from_slice(&buffer[..n]);
            }
            let head = std::str::from_utf8(&bytes[..head_end])
                .unwrap()
                .to_ascii_lowercase();
            let path = if index == 0 {
                "/api/v1/integration/plc-facts/samples"
            } else {
                "/compatible/samples"
            };
            assert!(head.starts_with(&format!("post {path} http/1.1\r\n")));
            assert!(head.contains("content-type: application/json\r\n"));
            assert!(head.contains("content-encoding: identity\r\n"));
            assert!(!head.contains("authorization:"));
            seen.push(bytes[head_end..head_end + length].to_vec());
            stream.write_all(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}").unwrap();
        }
        seen
    });
    let http = FactsHttp::new().unwrap();
    let utf8 = "{\"point\":\"炉温\",\"value\":820.5}";
    assert_eq!(
        http.post_sample(
            &format!("{origin}/api/v1/integration/plc-facts/samples"),
            utf8
        )
        .unwrap()
        .status,
        200
    );
    let exact = format!(
        "{{}}{}",
        " ".repeat(crate::domain::sample_upload::BODY_LIMIT - 2)
    );
    assert_eq!(
        http.post_sample(&format!("{origin}/compatible/samples"), &exact)
            .unwrap()
            .status,
        200
    );
    assert_eq!(
        http.post_sample(
            &format!("{origin}/compatible/samples"),
            &(exact.clone() + " ")
        )
        .unwrap_err(),
        "payload_too_large"
    );
    let seen = worker.join().unwrap();
    assert_eq!(seen[0], utf8.as_bytes());
    assert_eq!(seen[1], exact.as_bytes());
    assert_eq!(seen[1].len(), 524_288);
}

#[test]
fn streamed_response_byte_bound_and_truncation() {
    let bytes = vec![b' '; 8 * 1024 * 1024];
    assert_eq!(
        read_body(
            &mut std::io::Cursor::new(&bytes),
            Some(bytes.len() as u64),
            8 * 1024 * 1024
        )
        .unwrap()
        .len(),
        bytes.len()
    );
    assert!(read_body(
        &mut std::io::Cursor::new(&bytes),
        Some(bytes.len() as u64 + 1),
        8 * 1024 * 1024
    )
    .is_err());
    assert!(read_body(&mut std::io::Cursor::new(&bytes), None, bytes.len() - 1).is_err());
    assert!(read_body(&mut std::io::Cursor::new(b"{}"), Some(3), 1024).is_err());
}

#[test]
fn read_out_modes_are_typed_and_never_acknowledge() {
    use serde_json::{json, Value};
    let coverage = json!({"complete":false,"meaning":"receipt_feed_only_not_source_completeness","unknownBeforeSerial":"0"});
    let base = json!({"contractVersion":"plc-facts/v1","digestProfile":"pf-json/v1","asOf":"2026-11-05T10:00:00.123456789+08:00","hasMore":false,"coverage":coverage,"items":[]});
    for mode in ["latest", "changes", "range"] {
        let mut data = base.clone();
        data["mode"] = json!(mode);
        if mode == "latest" {
            data["nextPageCursor"] = Value::Null;
            data["bindingRevision"] = json!("1");
        } else {
            data["snapshotHighSerial"] = json!("0");
            data["scannedThrough"] = json!({"commitSerial":"0","ordinal":0});
            data["scanBudgetReached"] = json!(false);
            if mode == "changes" {
                data["nextCursor"] = json!("opaque-test-cursor");
                data["baseline"] = Value::Null;
                data["omittedThrough"] = Value::Null;
            } else {
                data["nextPageCursor"] = Value::Null;
            }
        }
        let envelope = json!({"code":200,"message":"success","data":data});
        assert!(validate_read(&envelope, "plc-demo", mode, false, 8).is_ok());
        let mut bad = envelope.clone();
        bad["data"]["unexpected"] = json!(true);
        assert!(validate_read(&bad, "plc-demo", mode, false, 8).is_err());
        let mut bad = envelope.clone();
        bad["data"]["hasMore"] = json!("false");
        assert!(validate_read(&bad, "plc-demo", mode, false, 8).is_err());
        let mut bad = envelope.clone();
        bad["data"]["coverage"]["complete"] = json!(true);
        assert!(validate_read(&bad, "plc-demo", mode, false, 8).is_err());
    }
    let vectors: Value = serde_json::from_str(include_str!(
        "../../../../../contracts/published/http-api/plc-facts-v1/vectors.json"
    ))
    .unwrap();
    let sample = &vectors["request"]["samples"][0];
    let item = json!({"kind":"original","position":{"commitSerial":"1","ordinal":1},"instanceId":"daa-demo","plcId":"plc-demo","sampleId":"sample-demo","sourceSha256":sample["sourceSha256"],"payloadUtf8":sample["payloadUtf8"],"sourceSampleComplete":true,"expiresAt":"2027-02-04T10:00:00.123000000+08:00"});
    let mut data = base;
    data["mode"] = json!("range");
    data["items"] = json!([item]);
    data["snapshotHighSerial"] = json!("1");
    data["scannedThrough"] = json!({"commitSerial":"1","ordinal":1});
    data["scanBudgetReached"] = json!(false);
    data["nextPageCursor"] = Value::Null;
    let envelope = json!({"code":200,"message":"success","data":data});
    assert!(validate_read(&envelope, "plc-demo", "range", true, 1).is_ok());
    let mut bad = envelope.clone();
    bad["data"]["items"][0]["payloadUtf8"] = json!("{}");
    assert!(validate_read(&bad, "plc-demo", "range", true, 1).is_err());
    assert!(validate_read(&envelope, "plc-other", "range", true, 1).is_err());
}

#[test]
fn history_partial_all_good_is_independent_of_completeness() {
    use crate::domain::{facts_canonical as pf, facts_wire::*};
    use serde_json::{json, Value};
    let vectors: Value = serde_json::from_str(include_str!(
        "../../../../../contracts/published/http-api/plc-facts-v1/vectors.json"
    ))
    .unwrap();
    let batch: Batch =
        serde_json::from_value(vectors["fixtures"]["partialFragment"].clone()).unwrap();
    let part = &batch.samples[0];
    let mut projection = pf::parse(part.payload_utf8.as_bytes(), 512 * 1024).unwrap();
    let map = projection.as_object_mut().unwrap();
    map.remove("schemaVersion");
    let revision = map.remove("revision").unwrap();
    map.insert("configRevision".into(), revision);
    for (key, value) in [
        ("sourceSha256", json!(part.source_sha256)),
        ("part", json!(part.part)),
        ("parts", json!(part.parts)),
        ("expiresAt", json!("2027-02-04T10:00:00.123000000+08:00")),
    ] {
        projection[key] = value;
    }
    for key in ["startedAt", "finishedAt", "savedAt"] {
        projection[key] = json!(wire_time(projection[key].as_str().unwrap()).unwrap());
    }
    let selected = part
        .point_ids
        .iter()
        .map(|id| {
            let mut fact = projection["points"][id].clone();
            fact["observedAt"] = json!(wire_time(fact["observedAt"].as_str().unwrap()).unwrap());
            (id.clone(), fact)
        })
        .collect::<serde_json::Map<_, _>>();
    projection["points"] = Value::Object(selected);
    let mut envelope = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v1","digestProfile":"pf-json/v1","asOf":"2026-11-05T10:00:00.123456789+08:00","hasMore":false,"coverage":{"complete":false,"meaning":"receipt_feed_only_not_source_completeness","unknownBeforeSerial":"0"},"mode":"range","items":[{"kind":"fact","position":{"commitSerial":"7","ordinal":1},"sourceSha256":part.source_sha256,"contentDigest":part.content_digest,"projectionDigest":pf::digest("query-projection",&projection).unwrap(),"projection":projection,"cycle":{"cycleId":part.cycle_id,"cycleDigest":cycle_digest(&batch.cycles[0]).unwrap(),"complete":false,"qualityGood":true,"receivedParts":1,"expectedParts":2}}],"nextPageCursor":null,"snapshotHighSerial":"7","scannedThrough":{"commitSerial":"7","ordinal":1},"scanBudgetReached":false}});
    assert!(validate_read(&envelope, "plc-demo", "range", false, 8).is_ok());
    envelope["data"]["items"][0]["cycle"]["complete"] = json!(true);
    assert!(validate_read(&envelope, "plc-demo", "range", false, 8).is_err());
    envelope["data"]["items"][0]["cycle"]["receivedParts"] = json!(2);
    assert!(validate_read(&envelope, "plc-demo", "range", false, 8).is_ok());
    envelope["data"]["items"][0]["cycle"]["receivedParts"] = json!(3);
    assert!(validate_read(&envelope, "plc-demo", "range", false, 8).is_err());
    let item = &mut envelope["data"]["items"][0];
    item["cycle"]["receivedParts"] = json!(1);
    item["cycle"]["complete"] = json!(false);
    let first = item["projection"]["points"]
        .as_object_mut()
        .unwrap()
        .values_mut()
        .next()
        .unwrap();
    first["quality"] = json!("bad");
    first["value"] = Value::Null;
    first["reason"] = json!("synthetic_read_failure");
    item["projectionDigest"] = json!(pf::digest("query-projection", &item["projection"]).unwrap());
    assert!(validate_read(&envelope, "plc-demo", "range", false, 8).is_err());
    envelope["data"]["items"][0]["cycle"]["qualityGood"] = json!(false);
    assert!(validate_read(&envelope, "plc-demo", "range", false, 8).is_ok());
}
