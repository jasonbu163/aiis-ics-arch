//! 文件：tests/cli_contract.rs；CLI无参/双语、严格配置和显式schema的低影响边界检查。
use field_flow::{
    config::Config,
    domain::{now_ms, Clock, Input},
    infrastructure::state,
};
use serde_json::{json, Value};
use std::{path::Path, process::Command};
fn config() -> Config {
    Config::load(Path::new("config/loopback.yaml")).unwrap()
}
#[test]
fn cli_and_schema() {
    let base = std::env::temp_dir().join(format!("ff-001-r1-r3-cli-{}", field_flow::domain::id()));
    std::fs::create_dir(&base).unwrap();
    let exe = env!("CARGO_BIN_EXE_field-flow");
    for lang in ["en-US", "zh-CN"] {
        for flags in [vec!["--lang", lang], vec!["--lang", lang, "--help"]] {
            let out = Command::new(exe)
                .args(flags)
                .current_dir(&base)
                .output()
                .unwrap();
            assert!(out.status.success());
            assert!(!out.stdout.is_empty());
            assert_eq!(std::fs::read_dir(&base).unwrap().count(), 0);
        }
    }
    for flags in [
        vec!["bad"],
        vec!["--lang", "invalid"],
        vec!["run"],
        vec!["state", "init"],
    ] {
        assert_eq!(
            Command::new(exe)
                .args(flags)
                .current_dir(&base)
                .output()
                .unwrap()
                .status
                .code(),
            Some(2)
        );
        assert_eq!(std::fs::read_dir(&base).unwrap().count(), 0);
    }
    let dir = base.join("state");
    state::init(&dir, "execute", "test").unwrap();
    assert!(state::init(&dir, "execute", "test").is_err());
    assert!(state::State::open(&dir, "dry_run", "test", "run").is_err());
    let c = rusqlite::Connection::open(dir.join("state.sqlite")).unwrap();
    c.execute("UPDATE store_meta SET schema_version=99", [])
        .unwrap();
    assert!(state::State::open(&dir, "execute", "test", "run").is_err());
    drop(c);
    let missing = base.join("missing");
    assert!(state::State::open(&missing, "execute", "test", "run").is_err());
    assert!(!missing.exists());
    let en: Value = serde_json::from_str(include_str!("../locales/en-US.json")).unwrap();
    let zh: Value = serde_json::from_str(include_str!("../locales/zh-CN.json")).unwrap();
    assert_eq!(
        en.as_object().unwrap().keys().collect::<Vec<_>>(),
        zh.as_object().unwrap().keys().collect::<Vec<_>>()
    );
}
#[test]
fn strict_config() {
    let c = config();
    for mutate in 0..12 {
        let mut x = c.clone();
        match mutate {
            0 => x.schema_version = 2,
            1 => x.plcs.push(x.plcs[0].clone()),
            2 => x.flows.push(x.flows[0].clone()),
            3 => x.flows[0].target.byte_offset = 15,
            4 => x.flows[0].target.data_type = "REAL".into(),
            5 => x.flows[0].kind = "demo02".into(),
            6 => x.plcs[0].host = "localhost".into(),
            7 => x.plcs[0].io_timeout_ms = 5001,
            8 => x.shutdown_timeout_ms = 5000,
            9 => x.http.total_timeout_ms = 100,
            10 => x.plcs[0].queue_capacity = 17,
            _ => x.flows[0].target.db_number = 0,
        }
        assert!(x.validate().is_err(), "config mutation {mutate}");
    }
    let original = std::fs::read_to_string("config/loopback.yaml").unwrap();
    for altered in [
        original.clone() + "unexpected: 1\n",
        original.replace("port: 31102", "port: '31102'"),
        original.replace("schema_version: 1", ""),
    ] {
        assert!(serde_yaml::from_str::<Config>(&altered).is_err());
    }
}
#[test]
fn strict_values_times_and_clock() {
    let c = config();
    let f = &c.flows[0];
    let p = &c.plcs[0];
    let now = now_ms();
    for v in [
        json!(32768),
        json!(-32769),
        json!(true),
        json!(1.0),
        json!("1"),
    ] {
        let input = json!({"schema_version":1,"source_id":f.source_id,"ready":true,"command_id":"test","value":v,"issued_at_ms":now,"expires_at_ms":now+1000});
        assert!(serde_json::from_value::<Input>(input).is_err());
    }
    for (issued, expires) in [
        (now - 20000, now + 1000),
        (now + 5000, now + 6000),
        (now, now + 60001),
        (now - 1000, now - 1),
    ] {
        let input:Input=serde_json::from_value(json!({"schema_version":1,"source_id":f.source_id,"ready":true,"command_id":"test","value":42,"issued_at_ms":issued,"expires_at_ms":expires})).unwrap();
        assert!(input.intent(f, p).is_err());
    }
    let mut clock = Clock::default();
    assert_eq!(clock.check(now_ms() - 2000).unwrap_err(), "clock_invalid");
    assert!(clock.check(now_ms()).is_err());
}
