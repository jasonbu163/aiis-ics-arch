//! 固定provider向量与独立十进制/深度反例；不调用网络或打开数据库。
use super::*;
use crate::domain::facts_wire::*;
use std::str::FromStr;
fn vectors() -> Value {
    serde_json::from_str(include_str!(
        "../../../../../contracts/published/http-api/plc-facts-v1/vectors.json"
    ))
    .unwrap()
}
#[test]
fn lexical_numbers_and_controls() {
    for (input, expected) in [
        (r#"{"n":-0.00e+3}"#, r#"{"n":0}"#),
        (
            r#"{"n":1.2300000000000000000000000000000000000001e-2}"#,
            r#"{"n":0.012300000000000000000000000000000000000001}"#,
        ),
        (
            r#"{"x":"\n\t\u0000\"\\中文"}"#,
            r#"{"x":"\u000a\u0009\u0000\"\\中文"}"#,
        ),
    ] {
        assert_eq!(
            String::from_utf8(canonical(&parse(input.as_bytes(), 4096).unwrap()).unwrap()).unwrap(),
            expected
        );
    }
}
#[test]
fn reject_and_depth() {
    for raw in [
        r#"{"a":1,"a":2}"#,
        r#"{"x":NaN}"#,
        r#"{"x":"\ud800"}"#,
        "\u{feff}{}",
        r#"{"n":1e1001}"#,
    ] {
        assert!(parse(raw.as_bytes(), 4096).is_err(), "{raw}");
    }
    let allowed = format!("{}0{}", "{\"a\":".repeat(20), "}".repeat(20));
    assert!(parse(allowed.as_bytes(), 4096).is_ok());
    let denied = format!("{}0{}", "{\"a\":".repeat(21), "}".repeat(21));
    assert!(parse(denied.as_bytes(), 4096).is_err());
}
fn rebuild(v: &Value) {
    let b: Batch = serde_json::from_value(v.clone()).unwrap();
    assert_eq!(
        b.digest().unwrap(),
        b.request_digest,
        "{}",
        b.bytes().unwrap()
    );
    for c in &b.cycles {
        let payloads = b
            .samples
            .iter()
            .filter(|p| p.cycle_id == c.cycle_id)
            .map(|p| {
                (
                    p.sample_id.clone(),
                    (
                        p.payload_utf8.clone(),
                        p.source_sha256.trim_start_matches("sha256:").into(),
                    ),
                )
            })
            .collect::<std::collections::BTreeMap<_, _>>()
            .into_values()
            .collect::<Vec<_>>();
        let built = build_cycle(
            &b.instance_id,
            &c.manifest_utf8,
            c.manifest_sha256.trim_start_matches("sha256:"),
            &c.context_utf8,
            c.context_sha256.trim_start_matches("sha256:"),
            &payloads,
        )
        .unwrap();
        assert!(
            serde_json::to_value(&built.cycle).unwrap() == serde_json::to_value(c).unwrap(),
            "cycle {} transport mismatch",
            c.cycle_id
        );
        for p in &b.samples {
            if p.cycle_id == c.cycle_id {
                assert!(built
                    .parts
                    .iter()
                    .any(|x| serde_json::to_value(x).unwrap() == serde_json::to_value(p).unwrap()));
            }
        }
    }
}
#[test]
fn provider_fixed_vectors() {
    let v = vectors();
    for basic in v["basics"].as_array().unwrap() {
        let raw = basic["bytes"].as_str().unwrap();
        assert_eq!(
            sha(raw.as_bytes()).trim_start_matches("sha256:"),
            basic["sha256"].as_str().unwrap()
        );
        assert_eq!(
            canonical(&parse(raw.as_bytes(), 4096).unwrap()).unwrap(),
            raw.as_bytes()
        );
    }
    rebuild(&v["request"]);
    for (name, b) in v["fixtures"].as_object().unwrap() {
        if name != "partialFragment" {
            rebuild(b)
        } else {
            let batch: Batch = serde_json::from_value(b.clone()).unwrap();
            assert_eq!(batch.digest().unwrap(), batch.request_digest);
        }
    }
    let b: Batch = serde_json::from_value(v["request"].clone()).unwrap();
    let mut original = serde_json::to_value(&b).unwrap();
    original.as_object_mut().unwrap().remove("requestDigest");
    original["batchCreatedAt"] = serde_json::json!(wire_time(&b.batch_created_at).unwrap());
    assert_eq!(
        String::from_utf8(canonical(&original).unwrap()).unwrap(),
        v["canonicalRequestUtf8"]
    );
    assert_eq!(
        cycle_digest(&b.cycles[0]).unwrap(),
        v["expected"]["cycleDigest"]
    );
    let context = parse(b.cycles[0].context_utf8.as_bytes(), 1024 * 1024).unwrap();
    let (defs, ds) = definitions(&context, "plc-demo").unwrap();
    assert_eq!(ds, v["expected"]["definitionSetDigest"]);
    assert_eq!(
        digest(
            "definition",
            &definition_object(&defs["point_x"].0).unwrap()
        )
        .unwrap(),
        v["expected"]["definitionDigest"]
    );
}

#[test]
fn exact_real_bounds_and_fixed_partition_budgets() {
    let v = vectors();
    let b: Batch = serde_json::from_value(v["request"].clone()).unwrap();
    let p = parse(b.samples[0].payload_utf8.as_bytes(), 512 * 1024).unwrap();
    let mut f = p["points"]["point_x"].clone();
    f["definition"]["dataType"] = serde_json::json!("REAL");
    for (token, valid) in [
        ("0", true),
        ("1.401298464324817e-45", true),
        ("3.4028234663852886e38", true),
        ("1.401298464324816e-45", false),
        ("3.4028234663852887e38", false),
    ] {
        f["value"] = Value::Number(serde_json::Number::from_str(token).unwrap());
        assert_eq!(value_check(&f).is_ok(), valid, "{token}");
    }
    let points = Value::Object(
        (0..513)
            .map(|n| (format!("p{n:04}"), Value::Null))
            .collect(),
    );
    let parts = fixed_parts(&points).unwrap();
    assert_eq!(parts.iter().map(Vec::len).collect::<Vec<_>>(), [512, 1]);
    let points = serde_json::json!({"a":"x".repeat(128*1024)});
    assert!(fixed_parts(&points).is_err());
    let token = format!("{{\"n\":{}}}", "9".repeat(257));
    assert!(parse(token.as_bytes(), 4096).is_err());
}
#[test]
fn wire_time_rejects_fraction_truncation_and_leap_seconds() {
    for t in [
        "2026-11-05T10:00:00.1234567890+08:00",
        "2026-11-05T10:00:60.000+08:00",
        "0001-01-01T00:00:00.000+08:00",
    ] {
        assert!(time(t).is_err(), "{t}");
    }
    assert_eq!(
        wire_time("2026-11-05T10:00:00.123456789+08:00").unwrap(),
        "2026-11-05T10:00:00.123456789+08:00"
    );
}
