//! 独立消费者合同：手写期望、结构段、完整布局与确定namespace；仅Rust标准库。
use aiis_tia_import_core::*;
fn e(key: &str, path: Vec<PathSegment>, typ: &str) -> NameEntry {
    NameEntry {
        key: key.into(),
        db_number: 28,
        path: Some(path),
        data_type: typ.into(),
        current_name: String::new(),
        mutable: true,
        address: None,
        manual_name: None,
        address_only: false,
    }
}
fn fields(v: &[&str]) -> Vec<PathSegment> {
    v.iter().map(|s| PathSegment::Field((*s).into())).collect()
}
fn names(es: Vec<NameEntry>) -> Result<NamePlan, Vec<Diagnostic>> {
    plan_names(&NameBatch {
        profile: NAME_PROFILE.into(),
        entries: es,
    })
}
fn name(p: &NamePlan, i: usize) -> (&str, &str) {
    match &p.rows[i].resolution {
        NameResolution::Resolved { name, mode } => (name, mode),
        _ => ("", "pending"),
    }
}
#[test]
fn fixed_suffix_and_boundaries() {
    for (t, s) in [
        ("BOOL", "Bool"),
        ("BYTE", "Byte"),
        ("USINT", "USInt"),
        ("CHAR", "Char"),
        ("INT", "Int"),
        ("UINT", "UInt"),
        ("WORD", "Word"),
        ("DINT", "DInt"),
        ("UDINT", "UDInt"),
        ("DWORD", "DWord"),
        ("REAL", "Real"),
        ("STRING[20]", "String"),
    ] {
        let p = names(vec![e(t, fields(&["Value"]), t)]).unwrap();
        assert_eq!(
            name(&p, 0),
            (format!("DB28_Value_{s}").as_str(), "auto_path")
        );
    }
    for n in [92, 93] {
        let mut x = e("bound", fields(&[&"a".repeat(n)]), "INT");
        x.db_number = 1;
        let p = names(vec![x]).unwrap();
        assert_eq!(name(&p, 0).1, if n == 92 { "auto_path" } else { "pending" });
        if n == 92 {
            assert_eq!(name(&p, 0).0.len(), 100)
        }
    }
    assert!(type_suffix("TIME").is_err());
    assert!(type_suffix("STRING[0]").is_err());
    for n in ["Roll_Code", "_a", "A1"] {
        validate_manual_name(n).unwrap()
    }
    for n in ["", "1A", "中文", "a-b"] {
        assert!(validate_manual_name(n).is_err())
    }
}
#[test]
fn namespace_simultaneous_fallback_order_and_final_rejection() {
    let mut a = e("a", fields(&["A_B", "C"]), "INT");
    let mut b = e("b", fields(&["A", "B_C"]), "INT");
    a.address = Some(ConfirmedAddress { byte: 0, bit: None });
    b.address = Some(ConfirmedAddress { byte: 2, bit: None });
    let p = names(vec![a.clone(), b.clone()]).unwrap();
    let reverse = names(vec![b.clone(), a.clone()]).unwrap();
    assert_eq!(
        p.rows
            .iter()
            .map(|r| (&r.key, &r.resolution))
            .collect::<Vec<_>>(),
        reverse
            .rows
            .iter()
            .map(|r| (&r.key, &r.resolution))
            .collect::<Vec<_>>()
    );
    assert_eq!(name(&p, 0).0, "DB28_B2_Int");
    assert_eq!(name(&p, 1).0, "DB28_B0_Int");
    b.address = Some(ConfirmedAddress { byte: 0, bit: None });
    assert_eq!(
        names(vec![a.clone(), b]).unwrap_err()[0].code,
        "point_name_conflict"
    );
    let mut r = e("reserved", fields(&["other"]), "INT");
    r.mutable = false;
    r.current_name = "DB28_Value_Int".into();
    let mut x = e("x", fields(&["Value"]), "INT");
    x.address = Some(ConfirmedAddress { byte: 0, bit: None });
    assert_eq!(
        name(&names(vec![x.clone(), r.clone()]).unwrap(), 0).0,
        "DB28_B0_Int"
    );
    r.current_name = "DB28_B0_Int".into();
    let mut r2 = r.clone();
    r2.key = "r2".into();
    r2.current_name = "DB28_Value_Int".into();
    assert!(names(vec![x, r, r2]).is_err());
}
#[test]
fn address_requirements_and_structured_path() {
    for path in [
        fields(&["中文"]),
        fields(&["a.b"]),
        vec![
            PathSegment::Field("items".into()),
            PathSegment::Index(-1),
            PathSegment::Field("Value".into()),
        ],
    ] {
        let mut x = e("a", path, "BOOL");
        assert_eq!(name(&names(vec![x.clone()]).unwrap(), 0).1, "pending");
        x.address = Some(ConfirmedAddress {
            byte: 12,
            bit: Some(0),
        });
        assert_eq!(
            name(&names(vec![x.clone()]).unwrap(), 0).0,
            "DB28_B12_0_Bool"
        );
        x.address.as_mut().unwrap().bit = Some(8);
        assert!(names(vec![x]).is_err());
    }
}
#[test]
fn independent_scan_expand_layout_consumer() {
    let inputs = [
        SourceInput {
            input_id: "db".into(),
            name: "names.db".into(),
            bytes: include_bytes!("../fixtures/names.db").to_vec(),
        },
        SourceInput {
            input_id: "udt".into(),
            name: "names.udt".into(),
            bytes: include_bytes!("../fixtures/names.udt").to_vec(),
        },
    ];
    let c = scan_sources(&inputs, ImportProfile::TiaSubsetV1).unwrap();
    let closure: Vec<_> = c
        .declarations
        .iter()
        .filter(|(_, d)| !d.db)
        .map(|(r, _)| r.clone())
        .collect();
    let r = &c
        .declarations
        .iter()
        .find(|(_, d)| d.name == "Names28")
        .unwrap()
        .0;
    let db = expand_db(&c, r, &closure).unwrap();
    assert!(db.leaves.iter().any(|l| l.segments == fields(&["a.b"])));
    assert!(db
        .leaves
        .iter()
        .any(|l| l.segments.contains(&PathSegment::Index(-1))));
    let p = layout_standard(&db, LayoutProfile::SiemensStep7V20StandardWordV1).unwrap();
    assert_eq!(p.leaves.len(), 9);
    let r = &c
        .declarations
        .iter()
        .find(|(_, d)| d.name == "Names60")
        .unwrap()
        .0;
    assert!(layout_standard(
        &expand_db(&c, r, &[]).unwrap(),
        LayoutProfile::SiemensStep7V20StandardWordV1
    )
    .is_err());
    assert!(scan_sources(
        &[SourceInput {
            input_id: "bad".into(),
            name: "bad.db".into(),
            bytes: vec![255]
        }],
        ImportProfile::TiaSubsetV1
    )
    .is_err());
}
