//! 无端口容量/manifest/层级边界；真实S7由正式19case和产品多DB用例独立取证。
use ds_runtime::domain::{configuration::*, layout};
use serde_json::json;

fn instance(dbs: usize, leaves: usize) -> InstanceConfig {
    let mut value: InstanceConfig = serde_json::from_value(
        json!({"id":uuid(),"name":"Boundary","host":"127.2.3.4","port":30102,"dbs":[]}),
    )
    .unwrap();
    for db in 0..dbs {
        let points:Vec<PointConfig>=(0..if db==0{leaves}else{1}).map(|index|serde_json::from_value(json!({"id":uuid(),"name":format!("D{db}Point{index}"),"dataType":"BOOL","byte":index/8,"bit":index%8,"manual":true,"manualReason":"independent boundary vector"})).unwrap()).collect();
        value.dbs.push(serde_json::from_value(json!({"id":uuid(),"name":format!("DB{db}"),"number":db+1,"length":65536,"manual":true,"points":points})).unwrap());
    }
    value
}
fn confirm(mut i: InstanceConfig) -> InstanceConfig {
    let snapshot = i.clone();
    for db in &mut i.dbs {
        let old = snapshot.dbs.iter().find(|d| d.id == db.id).unwrap();
        for p in &mut db.points {
            let policy = layout::effective_policy(&snapshot, old, p).unwrap();
            p.confirmations.initial =
                Some(layout::initial_signature(&p.data_type, &policy).unwrap());
            p.confirmations.policy = Some(layout::policy_signature(&policy));
        }
        db.address_confirmation = Some(AddressConfirmation {
            structure_sha256: layout::structure_signature(db),
            layout_sha256: layout::layout_signature(db),
            method: "manual".into(),
            reason: "explicit boundary fixture".into(),
        });
    }
    i.names_confirmation = Some(layout::names_signature(&i));
    i
}
#[test]
fn independent_topology_bounds_and_ipv4_loopback_not_fixed_ab() {
    let max = confirm(instance(32, 4096 - 31));
    let workspace = Workspace {
        schema_version: 1,
        instances: vec![max.clone()],
        source_versions: vec![],
    };
    validate(&workspace).unwrap();
    let compiled = layout::compile(&max).unwrap();
    assert_eq!(compiled.dbs.len(), 32);
    assert_eq!(compiled.point_index.len(), 4096);
    assert_eq!(
        compiled.dbs.values().map(|d| d.length).sum::<usize>(),
        32 * 65536
    );
    assert!(compiled.allocation_upper < 512 * 1024 * 1024);
    let mut too_many = workspace.clone();
    too_many.instances[0].dbs.push(instance(1, 1).dbs.remove(0));
    assert!(validate(&too_many).is_err());
    let mut too_many = workspace.clone();
    let mut point = too_many.instances[0].dbs[0].points[0].clone();
    point.id = uuid();
    point.name = "Additional".into();
    point.byte = Some(1000);
    too_many.instances[0].dbs[0].points.push(point);
    assert!(validate(&too_many).is_err());
    let mut small = Workspace::default();
    for n in 0..8 {
        let mut i = instance(1, 1);
        i.port = 30102 + n;
        small.instances.push(i);
    }
    validate(&small).unwrap();
    small.instances.push(instance(1, 1));
    assert!(validate(&small).is_err());
    for host in ["0.0.0.0", "128.0.0.1", "::1", "localhost", "127.999.1.1"] {
        let mut w = Workspace {
            schema_version: 1,
            instances: vec![instance(1, 1)],
            source_versions: vec![],
        };
        w.instances[0].host = host.into();
        assert!(validate(&w).is_err(), "{host}");
    }
    for (c, h) in [(1, 1), (16, 4), (64, 16)] {
        let mut w = Workspace {
            schema_version: 1,
            instances: vec![instance(1, 1)],
            source_versions: vec![],
        };
        w.instances[0].max_connections = c;
        w.instances[0].max_handshakes = h;
        validate(&w).unwrap();
    }
    for (c, h) in [(0, 1), (65, 1), (16, 0), (16, 17)] {
        let mut w = Workspace {
            schema_version: 1,
            instances: vec![instance(1, 1)],
            source_versions: vec![],
        };
        w.instances[0].max_connections = c;
        w.instances[0].max_handshakes = h;
        assert!(validate(&w).is_err());
    }
}
#[test]
fn full_namespace_disabled_pending_and_region_split_are_not_bypassed() {
    let mut i = instance(1, 2);
    i.dbs[0].points[1].name.clear();
    i.dbs[0].points[1].enabled = false;
    let i = confirm(i);
    assert!(layout::compile(&i).is_ok());
    let mut enabled = i.clone();
    enabled.dbs[0].points[1].enabled = true;
    assert!(layout::compile(&enabled)
        .unwrap_err()
        .iter()
        .any(|e| e.code == "point_name_invalid_or_duplicate"));
    let mut duplicate = i.clone();
    duplicate.dbs[0].points[1].name = duplicate.dbs[0].points[0].name.clone();
    let duplicate = confirm(duplicate);
    assert!(layout::compile(&duplicate)
        .unwrap_err()
        .iter()
        .any(|e| e.code == "point_name_invalid_or_duplicate"));
    let mut split = instance(1, 1);
    let point = &mut split.dbs[0].points[0];
    point.data_type = "DINT".into();
    point.bit = None;
    split.dbs[0].regions = vec![RegionPolicy {
        id: uuid(),
        first_bit: 0,
        bit_length: 8,
        policy: PolicyOverrides::default(),
    }];
    assert_eq!(
        layout::effective_policy(&split, &split.dbs[0], &split.dbs[0].points[0]).unwrap_err(),
        "policy_split_field"
    );
    let mut region = instance(1, 1);
    region.policy.owner = Some(WriteOwner::Client);
    region.policy.client_write = Some(true);
    region.dbs[0].policy.client_read = Some(false);
    region.dbs[0].regions = vec![RegionPolicy {
        id: uuid(),
        first_bit: 0,
        bit_length: 1,
        policy: PolicyOverrides {
            ui_maintenance: Some(true),
            ..Default::default()
        },
    }];
    region.dbs[0].points[0].policy.client_read = Some(true);
    let e = layout::effective_policy(&region, &region.dbs[0], &region.dbs[0].points[0]).unwrap();
    assert!(e.client_read && e.client_write && e.ui_maintenance);
    assert_eq!(e.inherited_from["client_read"], "point");
    assert!(e.inherited_from["ui_maintenance"].starts_with("region:"));
    assert_eq!(e.inherited_from["initial"], "default");
}
#[cfg(feature = "test-automation")]
#[test]
fn test_manifest_rejects_parent_escape_symlinks_and_role_mismatch_before_profile_open() {
    use ds_runtime::testing::hooks::Manifest;
    let escaped = std::path::Path::new("/private/tmp/arch-aw-005-r5-exec/profile/../outside.json");
    assert!(matches!(Manifest::read(escaped),Err(e)if e=="test_manifest_path"));
    let owned_root =
        std::path::PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").expect("owned test root"));
    let role = owned_root
        .strip_prefix("/private/tmp/arch-aw-005-r5-exec/profile")
        .expect("owned profile root")
        .components()
        .next()
        .and_then(|part| part.as_os_str().to_str())
        .expect("owned profile role");
    assert!(matches!(role, "dev" | "qa"));
    let opposite_role = if role == "dev" { "qa" } else { "dev" };
    let root = owned_root.join(uuid());
    std::fs::create_dir_all(&root).unwrap();
    let path = root.join("manifest.json");
    let mut value = json!({"taskId":"ARCH-AW-005","revision":"r5","role":role,"runId":format!("{role}-9999"),"sourceCandidate":"a".repeat(64),"ownedMarker":"ARCH-AW-005-r5-owned","profileDir":root,"workspace":null,"allowedPorts":[30102,30103,30104],"scenario":"N1"});
    std::fs::write(&path, value.to_string()).unwrap();
    assert!(Manifest::read(&path).is_ok());
    value["profileDir"] = json!(root.join("../foreign"));
    std::fs::write(&path, value.to_string()).unwrap();
    assert!(Manifest::read(&path).is_err());
    value["profileDir"] = json!(root);
    value["role"] = json!(opposite_role);
    value["runId"] = json!(format!("{opposite_role}-9999"));
    std::fs::write(&path, value.to_string()).unwrap();
    assert!(Manifest::read(&path).is_err());
    let link = root.join("link.json");
    std::os::unix::fs::symlink(&path, &link).unwrap();
    assert!(Manifest::read(&link).is_err());
    assert!(!root.join("device-simulator-v1").exists());
}

#[test]
fn host_thread_reservations_and_exhaustion_reject_before_worker_allocation() {
    use ds_runtime::{
        app::App,
        services::lifecycle::{DESKTOP_FIXED_THREADS, HEADLESS_FIXED_THREADS},
        testing::hooks,
    };
    use std::path::PathBuf;
    use std::sync::atomic::Ordering;
    assert_eq!(HEADLESS_FIXED_THREADS, 12);
    assert_eq!(DESKTOP_FIXED_THREADS, 40);
    let root = PathBuf::from(std::env::var_os("DS_TEST_RUN_ROOT").unwrap()).join(uuid());
    let app = App::open_desktop(&root).unwrap();
    assert_eq!(app.global.lock().unwrap().fixed_threads, 40);
    let fixture: Workspace =
        serde_json::from_str(include_str!("../../tests/fixtures/product-workspace.json")).unwrap();
    hooks::prepare_workspace(
        &app,
        Workspace {
            instances: vec![fixture.instances[0].clone()],
            ..Workspace::default()
        },
    )
    .unwrap();
    let instance = app.instance(&fixture.instances[0].id).unwrap();
    // Deterministic admission-only exhaustion: no socket, listener or native worker is created.
    app.global.lock().unwrap().fixed_threads = 62;
    instance.context.gate.store(true, Ordering::SeqCst);
    let token = instance
        .context
        .reserve()
        .expect("one remaining thread credit");
    assert!(instance.context.reserve().is_none());
    assert_eq!(app.global.lock().unwrap().tcp, 1);
    instance.context.cancel(token);
    assert_eq!(app.global.lock().unwrap().tcp, 0);
    instance.context.gate.store(false, Ordering::SeqCst);
    app.global.lock().unwrap().fixed_threads = 40;
    assert!(instance.stopped());
    assert!(app.shutdown());
    let root = root.with_file_name(uuid());
    let headless = App::open(&root).unwrap();
    assert_eq!(headless.global.lock().unwrap().fixed_threads, 12);
    assert!(headless.shutdown());
}
