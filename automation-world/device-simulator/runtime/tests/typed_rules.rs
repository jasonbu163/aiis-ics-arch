//! 独立手写golden bytes及确定规则边界，不以encode自身生成期望。
use ds_runtime::domain::{
    rule::{evaluate, RuleKind, RuleSpec},
    typed_value::{decode, default_value, encode},
};
use serde_json::{json, Value};

#[test]
fn scalar_golden_and_rejections() {
    let vectors: Vec<(&str, Value, Vec<u8>)> = vec![
        ("BOOL", json!(true), vec![1]),
        ("BYTE", json!(255), vec![255]),
        ("USINT", json!(0), vec![0]),
        ("CHAR", json!("A"), vec![65]),
        ("CHAR", json!("\0"), vec![0]),
        ("WORD", json!(65535), vec![255, 255]),
        ("UINT", json!(256), vec![1, 0]),
        ("INT", json!(-32768), vec![128, 0]),
        ("INT", json!(-1), vec![255, 255]),
        ("DWORD", json!(4294967295_u64), vec![255; 4]),
        ("UDINT", json!(65536), vec![0, 1, 0, 0]),
        ("DINT", json!(-2147483648_i64), vec![128, 0, 0, 0]),
        ("REAL", json!(1.5), vec![63, 192, 0, 0]),
        ("STRING[1]", json!("A"), vec![1, 1, 65]),
        (
            "STRING[8]",
            json!("ABC"),
            vec![8, 3, 65, 66, 67, 0, 0, 0, 0, 0],
        ),
    ];
    for (kind, value, expected) in vectors {
        assert_eq!(encode(kind, &value).unwrap(), expected);
        assert_eq!(decode(kind, &expected).unwrap(), value);
    }
    for (kind, value) in [
        ("BOOL", json!(1)),
        ("BYTE", json!(-1)),
        ("USINT", json!(256)),
        ("INT", json!(-32769)),
        ("UINT", json!(65536)),
        ("DINT", json!(2147483648_i64)),
        ("UDINT", json!(4294967296_u64)),
        ("REAL", json!(1e100)),
        ("CHAR", json!("汉")),
        ("CHAR", json!("AB")),
        ("STRING[1]", json!("AA")),
        ("STRING[8]", json!("é")),
    ] {
        assert!(encode(kind, &value).is_err(), "{kind} {value}");
    }
    for kind in [
        "STRING[0]",
        "STRING[255]",
        "LREAL",
        "WSTRING[4]",
        "ARRAY",
        "DATE",
    ] {
        assert!(default_value(kind).is_err());
    }
    for bytes in [
        vec![0x7f, 0x80, 0, 0],
        vec![0xff, 0x80, 0, 0],
        vec![0x7f, 0xc0, 0, 1],
    ] {
        assert!(decode("REAL", &bytes).is_err());
    }
    assert!(decode("INT", &[0]).is_err());
    assert!(decode("BOOL", &[2]).is_err());
    for bytes in [
        vec![1, 0, 0],
        vec![8, 9, 0, 0, 0, 0, 0, 0, 0, 0],
        vec![8, 1, 255, 0, 0, 0, 0, 0, 0, 0],
        vec![8, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    ] {
        assert!(decode("STRING[8]", &bytes).is_err());
    }
    let full = "Z".repeat(254);
    let mut expected = vec![254, 254];
    expected.extend([90; 254]);
    assert_eq!(encode("STRING[254]", &json!(full)).unwrap(), expected);
    for kind in [
        "BOOL",
        "BYTE",
        "USINT",
        "CHAR",
        "WORD",
        "UINT",
        "INT",
        "DWORD",
        "UDINT",
        "DINT",
        "REAL",
        "STRING[1]",
        "STRING[254]",
    ] {
        let v = default_value(kind).unwrap();
        let b = encode(kind, &v).unwrap();
        assert_eq!(decode(kind, &b).unwrap(), v);
    }
}

fn rule(kind: RuleKind) -> RuleSpec {
    RuleSpec {
        kind,
        fixed_value: json!(7),
        min: -3.,
        max: 3.,
        period_ms: 1000,
        phase: 0.,
        seed: "test".into(),
        half_period_ms: 500,
    }
}
#[test]
fn deterministic_rules_two_cycles_floor_and_bounds() {
    let id = "00000000-0000-4000-8000-000000000001";
    let p = "00000000-0000-4000-8000-000000000002";
    let ramp = rule(RuleKind::Ramp);
    for (t, expected) in [
        (0, -3),
        (250_000_000, -2),
        (500_000_000, 0),
        (750_000_000, 1),
        (1_000_000_000, -3),
        (2_000_000_000, -3),
    ] {
        assert_eq!(
            decode("INT", &evaluate("INT", &ramp, id, p, t).unwrap()).unwrap(),
            json!(expected)
        );
    }
    let sine = rule(RuleKind::Sine);
    assert_eq!(
        decode(
            "REAL",
            &evaluate("REAL", &sine, id, p, 250_000_000).unwrap()
        )
        .unwrap(),
        json!(3.)
    );
    assert_eq!(
        evaluate("REAL", &sine, id, p, 0).unwrap(),
        evaluate("REAL", &sine, id, p, 1_000_000_000).unwrap()
    );
    let fixed = rule(RuleKind::Fixed);
    assert_eq!(evaluate("DINT", &fixed, id, p, 0).unwrap(), [0, 0, 0, 7]);
    assert_eq!(
        evaluate("DINT", &fixed, id, p, 2_000_000_000).unwrap(),
        [0, 0, 0, 7]
    );
    let toggle = rule(RuleKind::Toggle);
    assert_eq!(evaluate("BOOL", &toggle, id, p, 0).unwrap(), [0]);
    assert_eq!(evaluate("BOOL", &toggle, id, p, 500_000_000).unwrap(), [1]);
    assert_eq!(
        evaluate("BOOL", &toggle, id, p, 1_000_000_000).unwrap(),
        [0]
    );
    let random = rule(RuleKind::Random);
    for t in [0, 1_000_000_000, 2_000_000_000] {
        let a = evaluate("INT", &random, id, p, t).unwrap();
        assert_eq!(a, evaluate("INT", &random, id, p, t + 999_999_999).unwrap());
        let n = decode("INT", &a).unwrap().as_i64().unwrap();
        assert!((-3..=3).contains(&n));
    }
    let mut bad = rule(RuleKind::Ramp);
    bad.period_ms = 99;
    assert!(evaluate("INT", &bad, id, p, 0).is_err());
    bad.period_ms = 100;
    bad.min = -32769.;
    assert!(evaluate("INT", &bad, id, p, 0).is_err());
    assert!(evaluate("STRING[8]", &random, id, p, 0).is_err());
}

#[test]
fn full_handwritten_type_extremes_and_independent_random_messages() {
    let table: Value =
        serde_json::from_str(include_str!("../../tests/fixtures/typed-vectors.json")).unwrap();
    for row in table["vectors"].as_array().unwrap() {
        let kind = row["type"].as_str().unwrap();
        let expected = row["hex"]
            .as_str()
            .unwrap()
            .as_bytes()
            .chunks(2)
            .map(|pair| u8::from_str_radix(std::str::from_utf8(pair).unwrap(), 16).unwrap())
            .collect::<Vec<_>>();
        assert_eq!(encode(kind, &row["value"]).unwrap(), expected, "{kind}");
        if kind == "REAL" {
            assert_eq!(
                (decode(kind, &expected).unwrap().as_f64().unwrap() as f32).to_bits(),
                u32::from_be_bytes(expected.as_slice().try_into().unwrap())
            );
        } else {
            assert_eq!(decode(kind, &expected).unwrap(), row["value"], "{kind}");
        }
    }
    let table: Value =
        serde_json::from_str(include_str!("../../tests/fixtures/rules-vectors.json")).unwrap();
    let random = rule(RuleKind::Random);
    for row in table["random"].as_array().unwrap() {
        let time = row["bucket"].as_u64().unwrap() * 1_000_000_000;
        let bytes = evaluate(
            "INT",
            &random,
            table["instance"].as_str().unwrap(),
            table["point"].as_str().unwrap(),
            time,
        )
        .unwrap();
        assert_eq!(decode("INT", &bytes).unwrap(), row["intRangeMinus3To3"]);
        let bytes = evaluate(
            "REAL",
            &random,
            table["instance"].as_str().unwrap(),
            table["point"].as_str().unwrap(),
            time,
        )
        .unwrap();
        let expected = row["realRangeMinus3To3"].as_f64().unwrap() as f32;
        assert_eq!(bytes, expected.to_be_bytes());
    }
}

#[test]
fn real_rule_endpoints_match_finite_f32_codec_after_json_roundtrip() {
    use ds_runtime::domain::rule::{self, RuleSpec};
    let encoded = format!(
        "{{\"kind\":\"ramp\",\"min\":{},\"max\":{},\"periodMs\":1000}}",
        -(f32::MAX as f64),
        f32::MAX as f64
    );
    let r: RuleSpec = serde_json::from_str(&encoded).unwrap();
    assert!(ds_runtime::domain::typed_value::encode("REAL", &serde_json::json!(r.min)).is_ok());
    assert!(ds_runtime::domain::typed_value::encode("REAL", &serde_json::json!(r.max)).is_ok());
    rule::validate("REAL", &r).unwrap();
    let mut overflow = r;
    overflow.max = 1e40;
    assert_eq!(rule::validate("REAL", &overflow).unwrap_err(), "rule_range");
}
