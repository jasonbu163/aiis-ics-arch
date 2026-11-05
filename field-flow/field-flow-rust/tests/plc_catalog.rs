//! 文件：tests/plc_catalog.rs；严格格式、路径、闭合字段、容量、CLI零副作用与最大日志行。
#![cfg(feature = "test-fixture")]
mod catalog_support;
use catalog_support::*;
use field_flow::{
    app::read_points::{Item, Observation},
    config::{catalog::Catalog, runtime_v2::Loaded},
    services::devices::PointSample,
};
use serde_json::{json, Value};
use std::{fs, path::Path};
#[test]
fn strict_catalog_and_cli() {
    let root = root("plc_catalog");
    let p = config(&root);
    let a = p.parent().unwrap().join("plcs/s7-a.json");
    let original = fs::read(&a).unwrap();
    let base: Value = serde_json::from_slice(&original).unwrap();
    assert!(Catalog::load(&a).unwrap().compatible);
    assert_eq!(Loaded::load(&p).unwrap().reads.len(), 1);
    let mut report = Vec::new();
    for (label, mutated) in [
        ("unknown", {
            let mut v = base.clone();
            v["typo"] = json!(1);
            v
        }),
        ("null_optional", {
            let mut v = base.clone();
            v["name"] = Value::Null;
            v
        }),
        ("float_integer", {
            let mut v = base.clone();
            v["schema_version"] = json!(1.0);
            v
        }),
        ("bool_integer", {
            let mut v = base.clone();
            v["connection"]["port"] = json!(true);
            v
        }),
        ("string_integer", {
            let mut v = base.clone();
            v["connection"]["port"] = json!("34102");
            v
        }),
        ("implicit_enabled", {
            let mut v = base.clone();
            v["dbs"][0]["enabled"] = json!("true");
            v
        }),
        ("overlap_disabled", {
            let mut v = base.clone();
            v["dbs"][0]["points"][1]["byte_offset"] = json!(1);
            v["dbs"][0]["points"][1]["enabled"] = json!(false);
            v
        }),
        ("duplicate_point", {
            let mut v = base.clone();
            v["dbs"][1]["points"][0]["id"] = json!("value");
            v
        }),
        ("non_int", {
            let mut v = base.clone();
            v["dbs"][0]["points"][0]["data_type"] = json!("BOOL");
            v
        }),
        ("bit", {
            let mut v = base.clone();
            v["dbs"][0]["points"][0]["bit"] = json!(0);
            v
        }),
        ("address", {
            let mut v = base.clone();
            v["dbs"][0]["points"][0]["byte_offset"] = json!(15);
            v
        }),
        ("foreign_protocol_field", {
            let mut v = base.clone();
            v["tables"] = json!([]);
            v
        }),
        ("host", {
            let mut v = base.clone();
            v["connection"]["host"] = json!("0.0.0.0");
            v
        }),
    ] {
        put(&a, &mutated);
        let out = cli(&["config", "validate", "--plc-file", a.to_str().unwrap()]);
        assert_eq!(out.status.code(), Some(2), "{label}");
        let v: Value = serde_json::from_slice(&out.stdout).unwrap();
        assert_eq!(v["format_valid"], false);
        report.push(json!({"label":label,"exit":out.status.code(),"report":v}));
    }
    for (label, bytes) in [
        (
            "duplicate_key",
            String::from_utf8(original.clone())
                .unwrap()
                .replacen("\"id\": \"s7_a\"", "\"id\":\"s7_a\",\"id\":\"other\"", 1)
                .into_bytes(),
        ),
        ("bom", [vec![0xef, 0xbb, 0xbf], original.clone()].concat()),
        (
            "integer_exponent",
            String::from_utf8(original.clone())
                .unwrap()
                .replacen("34102", "3.4102e4", 1)
                .into_bytes(),
        ),
        (
            "depth",
            format!("{}0{}", "[".repeat(18), "]".repeat(18)).into_bytes(),
        ),
        ("size", vec![b' '; 1048577]),
    ] {
        fs::write(&a, bytes).unwrap();
        assert!(Catalog::load(&a).is_err(), "{label}");
        report.push(json!({"label":label,"rejected":true}));
    }
    fs::write(&a, &original).unwrap();
    let main = value(&p);
    for bad in [
        "../s7-a.json",
        "/private/tmp/a.json",
        "plcs//s7-a.json",
        "./plcs/s7-a.json",
        "plcs/../s7-a.json",
        "plcs\\s7-a.json",
        "$ROOT/a.json",
        "~a.json",
        "https://a.json",
        "plcs/*.json",
        "",
    ] {
        let mut v = main.clone();
        v["plc_files"][0] = json!(bad);
        put(&p, &v);
        assert!(Loaded::load(&p).is_err(), "{bad}");
    }
    put(&p, &main);
    let link = p.parent().unwrap().join("plcs/link.json");
    std::os::unix::fs::symlink(&a, &link).unwrap();
    let mut v = main.clone();
    v["plc_files"][0] = json!("plcs/link.json");
    put(&p, &v);
    assert!(Loaded::load(&p).is_err());
    for k in [
        "plc_guard_get_int",
        "get_value_guard_int",
        "teaching01",
        "unknown",
    ] {
        let mut v = main.clone();
        v["flows"][0]["kind"] = json!(k);
        put(&p, &v);
        assert_eq!(
            Loaded::load(&p).unwrap_err(),
            "config_flow_kind_unsupported"
        );
    }
    put(&p, &main);
    let mut v = main.clone();
    v["plc_files"] = json!(["plcs/s7-a.json", "plcs/s7-a.json"]);
    put(&p, &v);
    assert!(Loaded::load(&p).is_err());
    for raw in [
        "schema_version: 2\nschema_version: 2\n",
        "schema_version: 2\nplc_files: &files []\nflows: *files\n",
        "schema_version: 2\n<<: {}\n",
    ] {
        fs::write(&p, raw).unwrap();
        assert!(Loaded::load(&p).is_err());
    }
    put(&p, &main);
    for label in [
        "dependency",
        "missing_point",
        "extra_plcs",
        "budgets",
        "flow_capacity",
    ] {
        let mut v = main.clone();
        match label {
            "dependency" => v["flows"][0]["device_ids"] = json!(["s7_a"]),
            "missing_point" => v["flows"][0]["reads"][0]["point_id"] = json!("missing"),
            "extra_plcs" => v["plcs"] = json!([]),
            "budgets" => v["plc_runtime"] = json!([]),
            _ => {
                let f = v["flows"][0].clone();
                v["flows"] = json!(vec![f; 9]);
            }
        }
        put(&p, &v);
        assert!(Loaded::load(&p).is_err(), "{label}");
    }
    put(&p, &main);
    let b = p.parent().unwrap().join("plcs/s7-b.json");
    let original_b = fs::read(&b).unwrap();
    for label in ["device_identity", "endpoint"] {
        let mut v: Value = serde_json::from_slice(&original_b).unwrap();
        if label == "device_identity" {
            v["id"] = json!("s7_a");
        } else {
            v["connection"]["port"] = json!(34102);
        }
        put(&b, &v);
        assert!(Loaded::load(&p).is_err());
    }
    fs::write(&b, &original_b).unwrap();
    let mut ds = base.clone();
    ds["source"] = json!({"kind":"device_simulator","export_mode":"saved_revision","instance_id":"s7_a","revision":{"id":"00000000-0000-0000-0000-000000000000","saved_seq":1,"payload_sha256":"0".repeat(64)},"exporter_version":"synthetic-shape-only","generated_at":"2026-11-04T12:00:00+08:00","runtime_observation":{"observed_at":"2026-11-04T12:00:01+08:00","selected_revision":null,"loaded_revision":null}});
    put(&a, &ds);
    assert!(Catalog::load(&a).is_ok());
    ds["source"]["generated_at"] = json!("2026-11-04T04:00:00Z");
    put(&a, &ds);
    assert!(Catalog::load(&a).is_err());
    let mut disabled = base.clone();
    disabled["dbs"][0]["enabled"] = json!(false);
    put(&a, &disabled);
    assert!(Loaded::load(&p).is_err());
    let mut too_many = base.clone();
    too_many["dbs"] = json!(vec![base["dbs"][0].clone(); 65]);
    put(&a, &too_many);
    assert!(Catalog::load(&a).is_err());
    too_many = base.clone();
    too_many["dbs"][0]["points"] = json!(vec![base["dbs"][0]["points"][0].clone(); 4097]);
    put(&a, &too_many);
    assert!(Catalog::load(&a).is_err());
    fs::write(&a, &original).unwrap();
    let out = std::process::Command::new(PRODUCT)
        .current_dir("/private/tmp")
        .args(["config", "validate", "--config", p.to_str().unwrap()])
        .output()
        .unwrap();
    assert!(out.status.success());
    let empty = root.join("empty");
    fs::create_dir(&empty).unwrap();
    for exe in [PRODUCT, FIXTURE] {
        for args in [vec![], vec!["--help"]] {
            let out = std::process::Command::new(exe)
                .current_dir(&empty)
                .args(args)
                .output()
                .unwrap();
            assert!(out.status.success());
            assert_eq!(fs::read_dir(&empty).unwrap().count(), 0);
        }
    }
    for lang in ["en-US", "zh-CN"] {
        let out = cli(&["--lang", lang, "--help"]);
        assert!(out.status.success());
        assert!(String::from_utf8(out.stdout)
            .unwrap()
            .contains("config validate"));
    }
    assert!(
        cli(&[
            "config",
            "validate",
            "--config",
            p.to_str().unwrap(),
            "--plc-file",
            a.to_str().unwrap()
        ])
        .status
        .code()
            == Some(2)
    );
    fs::write(
        root.join("negative-cases.json"),
        serde_json::to_vec_pretty(&report).unwrap(),
    )
    .unwrap();
}
#[test]
fn maximum_observation_and_structural_resource_vectors() {
    let root = root("observation_bounds");
    let snapshot = Observation {
        round_id: "9".repeat(64),
        status: "complete".into(),
        items: (0..16)
            .map(|_| Item {
                device_id: "d".repeat(64),
                point_id: "p".repeat(64),
                status: "success".into(),
                sample: Some(PointSample {
                    device_id: "d".repeat(64),
                    point_id: "p".repeat(64),
                    flow_id: "f".repeat(64),
                    request_id: "r".repeat(64),
                    generation: u64::MAX,
                    value: i16::MIN,
                    quality: "good".into(),
                    received_at: "2026-11-04T12:12:12.123+08:00".into(),
                }),
                error_key: None,
            })
            .collect(),
        completed_rounds: u64::MAX,
        successful_reads: u64::MAX,
        errors: u64::MAX,
    };
    let mut audit =
        field_flow::infrastructure::audit::Audit::open(&root, &"r".repeat(64), &"i".repeat(64))
            .unwrap();
    let chunks = field_flow::runtime::catalog::chunks(&"f".repeat(64), &snapshot);
    assert_eq!(chunks.len(), 4);
    for c in chunks {
        assert_eq!(c["items"].as_array().unwrap().len(), 4);
        audit.emit("points_health", c).unwrap();
    }
    let lines = fs::read_to_string(root.join("runtime.jsonl")).unwrap();
    assert!(lines.lines().all(|s| s.len() + 1 <= 4096));
    for raw in [
        r#"{"event":"health","context":"{\"had_forced_driver_stop\":true}"}"#,
        r#"{ "event": "health", "context": { "had_forced_driver_stop": true } }"#,
        r#"{"event":"forced_driver_stop"}"#,
        r#"{"context":{"error_key":"forced_driver_stop:connect"}}"#,
    ] {
        let p = root.join("vector.jsonl");
        fs::write(&p, raw).unwrap();
        assert!(forced(&events(&p)[0]));
    }
    for raw in [
        r#"{"event":"health","context":{"had_forced_driver_stop":false}}"#,
        r#"{"event":"health","context":{"had_forced_driver_stop":"true"}}"#,
    ] {
        assert!(!forced(&serde_json::from_str(raw).unwrap()));
    }
    assert!(!std::process::Command::new("false")
        .status()
        .unwrap()
        .success());
    for p in [
        "config/loopback.yaml",
        "config/basic02.yaml",
        "config/basic03.yaml",
    ] {
        field_flow::config::Config::load(Path::new(p)).unwrap();
    }
}

#[test]
fn yaml_scalar_boundaries_and_semantic_controls() {
    use field_flow::config::catalog::parse;
    let r = root("yaml_scalar_boundaries");
    let good = [
        "x: http://127.0.0.1:34880/it's\ny: 'http://127.0.0.1:34880/q?x=a & b/* !'\n",
        "x: http://127.0.0.1:34880/it\"s\ny: \"literal &anchor *alias !\"\n",
        "x: words with ' and \" inside plain scalars\ny: 'it''s & / * !'\n",
        "x: plain\n  continuation ' &anchor *alias\ny: ok\n",
        "x: |-\n  text ' \" &anchor *alias\ny: ok\n",
        "x: >2-\n  text ' \" &anchor *alias\ny: ok\n",
        "x: !!str 'literal &anchor *alias !'\ny: ok\n",
        "x: 'multiline\n  &anchor *alias'\ny: ok # ' \" &anchor *alias\n",
        "x: [http://host/it's, 'literal & / * !', {q: !!str 'v'}]\n",
    ];
    let mut vectors = Vec::new();
    for s in good {
        let control: serde_yaml::Value = serde_yaml::from_str(s).unwrap();
        let expected = serde_json::to_value(control).unwrap();
        assert_eq!(parse(s.as_bytes(), true).unwrap(), expected, "{s}");
        let serialized = serde_yaml::to_string(&expected).unwrap();
        assert_eq!(parse(serialized.as_bytes(), true).unwrap(), expected);
        vectors.push(json!({"yaml":s,"expected":expected,"outcome":"accepted"}));
    }
    let bad = [
        "x: http://host/it's\ny: &deps [one]\nz: *deps\n",
        "x: http://host/it\"s\ny: &deps [one]\nz: *deps\n",
        "x: 'it''s & text'\ny: &deps [one]\nz: *deps\n",
        "x: \"it\\\"s & text\"\ny: &deps [one]\nz: *deps\n",
        "x: words with ' and \" in plain\ny: &deps [one]\nz: *deps\n",
        "x: plain\n  continuation ' *literal\ny: &deps [one]\nz: *deps\n",
        "x: |-\n  &literal *literal ' \"\ny: &deps [one]\nz: *deps\n",
        "x: !!str \"literal & text\"\ny: !!seq &deps [one]\nz: *deps\n",
        "--- &document\nx: one\n",
        "x: plain # ' \"\ny: &deps [one]\nz: *deps\n",
    ];
    for s in bad {
        assert!(
            serde_yaml::from_str::<serde_yaml::Value>(s).is_ok(),
            "invalid test syntax: {s}"
        );
        assert_eq!(
            parse(s.as_bytes(), true).unwrap_err(),
            "config_yaml_alias",
            "{s}"
        );
        vectors.push(json!({"yaml":s,"outcome":"config_yaml_alias"}));
    }
    // Preserve the existing standard/custom tag boundary; no blanket tag ban is introduced.
    assert_eq!(
        parse(b"x: !!str value\n", true).unwrap(),
        json!({"x":"value"})
    );
    assert_eq!(
        parse(b"x: !custom value\n", true).unwrap_err(),
        "config_schema"
    );
    let path = config(&r);
    let main = std::fs::read_to_string(&path).unwrap();
    let header = main.split("flows:").next().unwrap();
    let tail = main.split("\nhttp:").nth(1).unwrap();
    let flows="flows:\n  - id: first\n    kind: demo01\n    business_name: first\n    interval_ms: 500\n    device_ids: [s7_a]\n    source_id: first_feed\n    get_url: http://127.0.0.1:34880/it's\n    input_max_age_ms: 10000\n    target: {device_id: s7_a, point_id: value}\n  - id: second\n    kind: demo01\n    business_name: second\n    interval_ms: 500\n    device_ids: [s7_a]\n    source_id: second_feed\n    get_url: 'http://127.0.0.1:34880/q?x=a & b/* !'\n    input_max_age_ms: 10000\n    target: {device_id: s7_a, point_id: result}";
    let valid = format!("{header}{flows}\nhttp:{tail}");
    std::fs::write(&path, &valid).unwrap();
    let plain = Loaded::load(&path).unwrap();
    let quoted = valid.replace(
        "get_url: http://127.0.0.1:34880/it's",
        "get_url: \"http://127.0.0.1:34880/it's\"",
    );
    std::fs::write(&path, &quoted).unwrap();
    let equivalent = Loaded::load(&path).unwrap();
    assert_eq!(
        serde_json::to_value(plain.config).unwrap(),
        serde_json::to_value(equivalent.config).unwrap()
    );
    let anchored = valid.replacen("device_ids: [s7_a]", "device_ids: &deps [s7_a]", 1);
    let anchored = anchored.replacen("device_ids: [s7_a]", "device_ids: *deps", 1);
    std::fs::write(&path, &anchored).unwrap();
    assert_eq!(Loaded::load(&path).unwrap_err(), "config_yaml_alias");
    let out = cli(&[
        "run",
        "--config",
        path.to_str().unwrap(),
        "--state-dir",
        r.join("absent-state").to_str().unwrap(),
    ]);
    assert_eq!(out.status.code(), Some(2));
    assert!(out.stdout.is_empty());
    assert!(!r.join("absent-state").exists());
    std::fs::write(
        r.join("vectors.json"),
        serde_json::to_vec_pretty(&vectors).unwrap(),
    )
    .unwrap();
}

#[test]
fn yaml_line_breaks_and_quoted_flow_keys() {
    use field_flow::config::catalog::parse;
    let r = root("yaml_line_breaks_and_flow_keys");
    let mut vectors = Vec::new();
    let line_breaks = [
        ("lf", "\n"),
        ("crlf", "\r\n"),
        ("cr", "\r"),
        ("nel", "\u{85}"),
        ("ls", "\u{2028}"),
        ("ps", "\u{2029}"),
    ];
    // Exercise line state in comments, plain/quoted continuations and both block styles.
    // Compare each original source with the real parser: LS/PS scalar folding can differ
    // from LF, so the scanner must not normalize the value passed to deserialization.
    let literals = [
        "# comment ' \" & *\nx: http://host/it's:a&b*c!\ny: ok\n",
        "x: plain\n  continuation ' &literal *literal !\ny: ok\n",
        "x: 'quoted\n  &literal *literal !'\ny: ok\n",
        "x: \"quoted\n  &literal *literal !\"\ny: ok\n",
        "x: |-\n  &literal *literal ' \"\ny: ok\n",
        "x: >2-\n  &literal *literal ' \"\ny: ok\n",
        "x: {\"a\":\"literal & * !\", 'b':http://host/it's:a&b*c!}\n",
    ];
    for (name, lb) in line_breaks {
        for source in literals {
            let source = source.replace('\n', lb);
            let ast: serde_yaml::Value = serde_yaml::from_str(&source).unwrap();
            let expected = serde_json::to_value(ast).unwrap();
            assert_eq!(
                parse(source.as_bytes(), true).unwrap(),
                expected,
                "{name}: {source}"
            );
            vectors
                .push(json!({"family":name,"source":source,"ast":expected,"outcome":"accepted"}));
        }
        for prefix in literals.iter().take(6) {
            let source = format!("{prefix}a: &deps [one]\nb: *deps\n").replace('\n', lb);
            let ast: serde_yaml::Value = serde_yaml::from_str(&source).unwrap();
            assert_eq!(ast["a"], ast["b"]);
            assert_eq!(
                parse(source.as_bytes(), true).unwrap_err(),
                "config_yaml_alias",
                "{name}: {source}"
            );
            vectors.push(json!({"family":name,"source":source,"ast":serde_json::to_value(ast).unwrap(),"outcome":"config_yaml_alias"}));
        }
    }
    for (source, literal) in [
        (
            "x: {\"a\":&b [one], \"c\":*b}\n",
            "x: {\"a\":[one], \"c\":[one]}\n",
        ),
        ("x: {'a':&b [one], 'c':*b}\n", "x: {'a':[one], 'c':[one]}\n"),
        (
            "x: {\"a\": &b [one], \"c\": *b}\n",
            "x: {\"a\": [one], \"c\": [one]}\n",
        ),
        (
            "\"a\": &b [one]\n\"c\": *b\n",
            "\"a\": [one]\n\"c\": [one]\n",
        ),
    ] {
        let alias_ast: serde_yaml::Value = serde_yaml::from_str(source).unwrap();
        let literal_ast: serde_yaml::Value = serde_yaml::from_str(literal).unwrap();
        assert_eq!(alias_ast, literal_ast);
        assert_eq!(
            parse(source.as_bytes(), true).unwrap_err(),
            "config_yaml_alias"
        );
        assert_eq!(
            parse(literal.as_bytes(), true).unwrap(),
            serde_json::to_value(literal_ast).unwrap()
        );
        vectors.push(json!({"source":source,"literal":literal,"ast":serde_json::to_value(alias_ast).unwrap(),"outcome":"config_yaml_alias"}));
    }
    // Full typed configurations prove that legal syntax is retained, not merely scanned.
    let path = config(&r);
    let main = std::fs::read_to_string(&path).unwrap();
    let baseline = serde_json::to_value(Loaded::load(&path).unwrap().config).unwrap();
    let anchored = main
        .replacen(
            "device_ids: [s7_a, s7_b]",
            "device_ids: &deps [s7_a, s7_b]",
            1,
        )
        .replacen("device_ids: [s7_a]", "device_ids: *deps", 1);
    let anchored_ast: serde_yaml::Value = serde_yaml::from_str(&anchored).unwrap();
    let flow_ast = serde_json::to_value(anchored_ast).unwrap();
    let flow_literal = serde_json::to_string(&flow_ast).unwrap();
    let flow_alias = flow_literal
        .replacen(
            "\"device_ids\":[\"s7_a\",\"s7_b\"]",
            "\"device_ids\":&deps [s7_a,s7_b]",
            1,
        )
        .replacen(
            "\"device_ids\":[\"s7_a\",\"s7_b\"]",
            "\"device_ids\":*deps",
            1,
        );
    assert_eq!(
        serde_yaml::from_str::<serde_yaml::Value>(&flow_alias).unwrap(),
        serde_yaml::from_str::<serde_yaml::Value>(&flow_literal).unwrap()
    );
    std::fs::write(&path, &flow_literal).unwrap();
    let flow_baseline = serde_json::to_value(Loaded::load(&path).unwrap().config).unwrap();
    for (name, lb) in line_breaks {
        let source = format!("# source comment\n{main}").replace('\n', lb);
        std::fs::write(&path, &source).unwrap();
        assert_eq!(
            serde_json::to_value(Loaded::load(&path).unwrap().config).unwrap(),
            baseline
        );
        let alias = format!("# source comment\n{anchored}").replace('\n', lb);
        assert_eq!(
            serde_yaml::from_str::<serde_yaml::Value>(&alias).unwrap(),
            serde_yaml::from_str::<serde_yaml::Value>(&anchored).unwrap()
        );
        std::fs::write(&path, &alias).unwrap();
        assert_eq!(
            Loaded::load(&path).unwrap_err(),
            "config_yaml_alias",
            "{name}"
        );
        vectors.push(json!({"family":name,"full_config":source,"alias_config":alias,"outcome":"typed_equal_and_alias_rejected"}));
    }
    std::fs::write(&path, &flow_alias).unwrap();
    assert_eq!(Loaded::load(&path).unwrap_err(), "config_yaml_alias");
    let out = cli(&[
        "run",
        "--config",
        path.to_str().unwrap(),
        "--state-dir",
        r.join("absent-state").to_str().unwrap(),
    ]);
    assert_eq!(out.status.code(), Some(2));
    assert!(out.stdout.is_empty());
    assert!(!r.join("absent-state").exists());
    // Preserve the standard/custom-tag boundary with adjacent quoted flow keys as well.
    assert_eq!(
        parse(b"{\"x\":!!str 'literal & * !'}", true).unwrap(),
        json!({"x":"literal & * !"})
    );
    assert_eq!(
        parse(b"{\"x\":!custom value}", true).unwrap_err(),
        "config_schema"
    );
    std::fs::write(&path, &flow_literal).unwrap();
    assert_eq!(
        serde_json::to_value(Loaded::load(&path).unwrap().config).unwrap(),
        flow_baseline
    );
    std::fs::write(
        r.join("vectors.json"),
        serde_json::to_vec_pretty(&vectors).unwrap(),
    )
    .unwrap();
}
