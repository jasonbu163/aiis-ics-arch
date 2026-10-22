//! 通用owner真实线程合同：完整触达拒绝、BOOL RMW、typed CAS、跨tick/重连/启停保值。
use ds_runtime::{
    domain::{
        configuration::*,
        layout,
        request::{Request, Source},
    },
    infrastructure::logging::Evidence,
    services::owner::Owner,
};
use serde_json::{json, Value};
use std::{sync::Arc, time::Duration};
fn point(name: &str, kind: &str, byte: u32, bit: Option<u8>, policy: Value) -> PointConfig {
    serde_json::from_value(json!({"id":uuid(),"name":name,"dataType":kind,"byte":byte,"bit":bit,"manual":true,"manualReason":"handwritten test layout","policy":policy})).unwrap()
}
fn compiled() -> Arc<layout::CompiledInstance> {
    let mut i:InstanceConfig=serde_json::from_value(json!({"id":uuid(),"name":"Independent","port":30102,"dbs":[{"id":uuid(),"name":"Mixed","number":73,"length":64,"manual":true}]})).unwrap();
    i.dbs[0].points = vec![
        point(
            "ClientBit",
            "BOOL",
            0,
            Some(0),
            json!({"owner":"client","clientWrite":true}),
        ),
        point(
            "UiBit",
            "BOOL",
            0,
            Some(1),
            json!({"owner":"ui","uiWrite":true}),
        ),
        point(
            "ClientUint",
            "UINT",
            4,
            None,
            json!({"owner":"client","clientWrite":true,"uiMaintenance":true}),
        ),
        point(
            "UiString",
            "STRING[8]",
            16,
            None,
            json!({"owner":"ui","uiWrite":true,"initial":"seed"}),
        ),
        point(
            "ClientReal",
            "REAL",
            28,
            None,
            json!({"owner":"client","clientWrite":true}),
        ),
        point(
            "RuleFixed",
            "DINT",
            32,
            None,
            json!({"mode":"fixed","owner":"rule","rule":{"kind":"fixed","fixedValue":7}}),
        ),
    ];
    let frozen = i.clone();
    for p in &mut i.dbs[0].points {
        let e = layout::effective_policy(&frozen, &frozen.dbs[0], p).unwrap();
        p.confirmations.initial = Some(layout::initial_signature(&p.data_type, &e).unwrap());
        p.confirmations.policy = Some(layout::policy_signature(&e));
    }
    let d = &mut i.dbs[0];
    d.address_confirmation = Some(AddressConfirmation {
        structure_sha256: layout::structure_signature(d),
        layout_sha256: layout::layout_signature(d),
        method: "manual".into(),
        reason: "handwritten".into(),
    });
    i.names_confirmation = Some(layout::names_signature(&i));
    Arc::new(layout::compile(&i).unwrap())
}
fn request(source: Source, start: usize, bytes: &[u8], bit: Option<u8>) -> Request {
    let mut r = Request {
        source,
        db: 73,
        start,
        size: bytes.len(),
        bit,
        ..Request::default()
    };
    r.data[..bytes.len()].copy_from_slice(bytes);
    r
}
fn read(owner: &Owner, start: usize, size: usize) -> Vec<u8> {
    let mut r = request(Source::Read, start, &vec![0; size], None);
    let (e, v) = owner.epoch_revision();
    r.epoch = e;
    r.revision = v;
    let result = owner.call(r);
    assert!(result.ok);
    result.data[..size].to_vec()
}
#[test]
fn whole_touched_range_atomicity_bool_rmw_and_rejected_memory_stability() {
    let config = compiled();
    let owner = Owner::new(config.clone(), uuid(), Evidence::default()).unwrap();
    assert!(owner.control("start", 0));
    assert!(owner.call(request(Source::Client, 0, &[1], Some(0))).ok);
    assert_eq!(read(&owner, 0, 1), [1]);
    let seq = owner.values(0, 100)["seq"].as_str().unwrap().to_owned();
    for r in [
        request(Source::Client, 0, &[0], None),
        request(Source::Client, 0, &[0, 0], None),
        request(Source::Client, 4, &[1], None),
        request(Source::Client, 28, &f32::NAN.to_be_bytes(), None),
        request(Source::Client, 63, &[1], None),
    ] {
        assert!(!owner.call(r).ok);
    }
    assert_eq!(owner.values(0, 100)["seq"], seq);
    assert_eq!(read(&owner, 0, 1), [1]);
    let ui = &config.dbs[&73].points[1];
    assert!(owner
        .write_point(
            &ui.config.id,
            &json!(true),
            &owner.loaded_revision(),
            1,
            0,
            false
        )
        .is_ok());
    assert_eq!(read(&owner, 0, 1), [3]);
    assert!(
        owner
            .call(request(Source::Client, 4, &[0x12, 0x34], None))
            .ok
    );
    assert!(!owner.call(request(Source::Client, 16, &[0; 10], None)).ok);
    assert_eq!(read(&owner, 4, 2), [0x12, 0x34]);
    owner.control("stop", 0);
    assert!(owner.shutdown());
}
#[test]
fn maintenance_cas_fixed_pause_reset_and_hold_survives_ticks_stop_start() {
    let config = compiled();
    let owner = Owner::new(config.clone(), uuid(), Evidence::default()).unwrap();
    owner.control("start", 0);
    let point = &config.dbs[&73].points[2];
    let revision = owner.loaded_revision();
    assert!(owner
        .write_point(&point.config.id, &json!(42), &revision, 1, 0, true)
        .is_ok());
    assert!(owner
        .write_point(&point.config.id, &json!(9), &revision, 1, 0, true)
        .is_err());
    assert!(owner.call(request(Source::Client, 4, &[0, 43], None)).ok);
    std::thread::sleep(Duration::from_millis(220));
    assert_eq!(read(&owner, 4, 2), [0, 43]);
    assert_eq!(read(&owner, 32, 4), [0, 0, 0, 7]);
    let fixed_id = &config.dbs[&73].points[5].config.id;
    let seq = owner.values(0, 100)["rows"]
        .as_array()
        .unwrap()
        .iter()
        .find(|p| p["pointId"] == *fixed_id)
        .unwrap()["pointSeq"]
        .clone();
    owner.control("pause", 0);
    assert!(owner
        .write_point(fixed_id, &json!(99), &revision, 1, 0, true)
        .is_err());
    std::thread::sleep(Duration::from_millis(120));
    assert_eq!(read(&owner, 32, 4), [0, 0, 0, 7]);
    owner.control("resume", 0);
    std::thread::sleep(Duration::from_millis(120));
    assert_eq!(
        owner.values(0, 100)["rows"]
            .as_array()
            .unwrap()
            .iter()
            .find(|p| p["pointId"] == *fixed_id)
            .unwrap()["pointSeq"],
        seq
    );
    owner.control("stop", 0);
    let captured = owner.capture().unwrap();
    assert_eq!(captured.values[&point.config.id], 43);
    owner.control("start", 0);
    assert_eq!(read(&owner, 4, 2), [0, 43]);
    owner.control("stop", 0);
    owner.control("reset", 0);
    let captured = owner.capture().unwrap();
    assert_eq!(captured.values[&point.config.id], 0);
    assert_eq!(captured.epoch, 2);
    assert_eq!(captured.simulated_ns, 0);
    assert!(owner.shutdown());
}

#[test]
#[cfg(feature = "test-automation")]
fn migrated_protocol_snapshot_and_resource_consumers_have_real_typed_fields_without_listener() {
    use ds_runtime::{app::App, infrastructure::resource_sample, testing::hooks};
    let root =
        std::path::PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("owned test root"))
            .join(format!("snapshot-contract-{}", uuid()));
    std::fs::create_dir_all(&root).unwrap();
    let app = App::open(&root).unwrap();
    let workspace: Workspace =
        serde_json::from_str(include_str!("../../tests/fixtures/protocol-workspace.json")).unwrap();
    hooks::prepare_workspace(&app, workspace.clone()).unwrap();
    for config in &workspace.instances {
        let instance = app.instance(&config.id).unwrap();
        // 与stdio测试宿主相同的真实合成：唯一owner快照+同实例transport快照。
        let mut snapshot = instance.context.owner.test_snapshot();
        for (key, value) in instance.context.snapshot().as_object().unwrap() {
            snapshot[key] = value.clone();
        }
        for key in [
            "epoch",
            "revision",
            "seq",
            "tick",
            "next_tick_ns",
            "protocol_waiting",
            "rule_waiting",
            "ui_waiting",
            "c",
            "h",
            "tcp",
            "reserved_bytes",
            "config_c",
            "config_h",
            "accepted_tcp",
            "closing",
        ] {
            assert!(
                snapshot[key].as_u64().is_some(),
                "numeric snapshot field {key}"
            );
        }
        assert_eq!(snapshot["running"], false);
        for key in [
            "protocol_waiting",
            "rule_waiting",
            "ui_waiting",
            "c",
            "h",
            "tcp",
            "reserved_bytes",
        ] {
            assert_eq!(snapshot[key], 0);
        }
        assert_eq!(snapshot["image"].as_str().unwrap().len(), 2048);
        assert_eq!(snapshot["marker"].as_str().unwrap().len(), 128);
        assert_eq!(snapshot["points"].as_array().unwrap().len(), 63);
        assert!(snapshot["connections"].as_array().unwrap().is_empty());
        for point in snapshot["points"].as_array().unwrap() {
            for key in ["db", "bit_address", "last_seq", "source", "updated_at"] {
                assert!(point[key].as_u64().is_some(), "numeric point field {key}");
            }
            assert!(point["id"].as_str().is_some());
        }
        for number in ["41", "57"] {
            let db = &snapshot["dbs"][number];
            assert!(db["bytes"].as_str().is_some() && db["sha256"].as_str().unwrap().len() == 64);
            assert!(db["points"].is_array());
        }
    }
    let emitted = Evidence::default();
    emitted.put(resource_sample::sample()); // 正常路径由Evidence加同源clock字段。
    let actual = emitted.take().pop().unwrap();
    for key in ["rss", "fd", "mach_ports", "threads", "monotonic_ns"] {
        assert!(
            actual[key].as_u64().is_some(),
            "actual resource field {key}"
        );
    }
    assert!(actual["cpu_seconds"].as_f64().is_some());
    assert!(app.shutdown());
}
