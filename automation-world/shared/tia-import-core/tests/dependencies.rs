//! 手写UDT依赖图回归：唯一/嵌套/重名显式选择/缺失与循环，不依赖应用或文件系统。
use aiis_tia_import_core::*;
fn catalog(files: &[(&str, &str)]) -> SourceCatalog {
    scan_sources(
        &files
            .iter()
            .map(|(id, text)| SourceInput {
                input_id: (*id).into(),
                name: format!("{id}.db"),
                bytes: text.as_bytes().to_vec(),
            })
            .collect::<Vec<_>>(),
        ImportProfile::TiaSubsetV1,
    )
    .unwrap()
}
fn reference(c: &SourceCatalog, input: &str, name: &str) -> DeclarationRef {
    c.declarations
        .iter()
        .find(|(r, d)| r.input_id == input && d.name == name)
        .unwrap()
        .0
        .clone()
}
const DB: &str = "DATA_BLOCK \"Main\" { S7_Optimized_Access := 'FALSE' } VAR unit : \"Outer\"; END_VAR BEGIN END_DATA_BLOCK";
#[test]
fn unique_dependencies_include_nested_struct_and_array_but_not_unused_types() {
    let c = catalog(&[("main",DB),("types","TYPE \"Outer\" STRUCT nested:STRUCT values:ARRAY[2..3] OF \"Inner\"; END_STRUCT; END_STRUCT; END_TYPE TYPE \"Inner\" STRUCT value:INT; END_STRUCT; END_TYPE TYPE \"Unused\" STRUCT ignored:REAL; END_STRUCT; END_TYPE")]);
    let db = reference(&c, "main", "Main");
    let plan = resolve_udt_dependencies(&c, &db, &[]).unwrap();
    assert!(plan.issues.is_empty());
    assert_eq!(
        plan.closure,
        vec![
            reference(&c, "types", "Outer"),
            reference(&c, "types", "Inner")
        ]
    );
    let expanded = expand_db(&c, &db, &plan.closure).unwrap();
    assert_eq!(
        expanded
            .leaves
            .iter()
            .map(|l| l.path.as_str())
            .collect::<Vec<_>>(),
        vec!["unit.nested.values[2].value", "unit.nested.values[3].value"]
    );
}
#[test]
fn ambiguous_types_require_a_source_and_selected_branch_gets_its_nested_dependency() {
    let c=catalog(&[("main",DB),("first","TYPE \"Outer\" STRUCT a:INT; END_STRUCT; END_TYPE"),("second","TYPE \"Outer\" STRUCT b:\"Inner\"; END_STRUCT; END_TYPE TYPE \"Inner\" STRUCT value:REAL; END_STRUCT; END_TYPE")]);
    let db = reference(&c, "main", "Main");
    let plan = resolve_udt_dependencies(&c, &db, &[]).unwrap();
    assert!(plan.closure.is_empty());
    assert_eq!(plan.issues[0].diagnostic.code, "udt_ambiguous");
    assert_eq!(plan.issues[0].diagnostic.path, "unit");
    assert_eq!(plan.issues[0].candidates.len(), 2);
    let chosen = reference(&c, "second", "Outer");
    let plan = resolve_udt_dependencies(&c, &db, &[chosen.clone()]).unwrap();
    assert!(plan.issues.is_empty());
    assert_eq!(plan.closure, vec![chosen, reference(&c, "second", "Inner")]);
    assert_eq!(
        expand_db(&c, &db, &plan.closure).unwrap().leaves[0].path,
        "unit.b.value"
    );
    assert_eq!(
        resolve_udt_dependencies(
            &c,
            &db,
            &[
                reference(&c, "first", "Outer"),
                reference(&c, "second", "Outer")
            ]
        )
        .unwrap_err()[0]
            .code,
        "duplicate_udt"
    );
}
#[test]
fn missing_and_cyclic_types_are_diagnosed_without_guessing() {
    let c = catalog(&[
        ("main", DB),
        (
            "types",
            "TYPE \"Outer\" STRUCT value:\"Missing\"; END_STRUCT; END_TYPE",
        ),
    ]);
    let plan = resolve_udt_dependencies(&c, &reference(&c, "main", "Main"), &[]).unwrap();
    assert_eq!(plan.issues[0].diagnostic.code, "udt_missing");
    assert_eq!(plan.issues[0].diagnostic.path, "unit.value");
    assert_eq!(plan.issues[0].type_name, "Missing");
    let c=catalog(&[("main",DB),("types","TYPE \"Outer\" STRUCT nested:\"Inner\"; END_STRUCT; END_TYPE TYPE \"Inner\" STRUCT again:\"Outer\"; END_STRUCT; END_TYPE")]);
    let plan = resolve_udt_dependencies(&c, &reference(&c, "main", "Main"), &[]).unwrap();
    assert_eq!(plan.issues[0].diagnostic.code, "udt_cycle");
    assert_eq!(plan.issues[0].diagnostic.path, "unit.nested.again");
}
#[test]
fn matching_is_case_insensitive_and_invalid_explicit_id_is_rejected() {
    let c = catalog(&[
        ("main", DB),
        (
            "types",
            "TYPE \"outer\" STRUCT value:INT; END_STRUCT; END_TYPE",
        ),
    ]);
    let db = reference(&c, "main", "Main");
    let plan = resolve_udt_dependencies(&c, &db, &[]).unwrap();
    assert!(plan.issues.is_empty());
    assert_eq!(plan.closure.len(), 1);
    assert_eq!(
        resolve_udt_dependencies(
            &c,
            &db,
            &[DeclarationRef {
                input_id: "absent".into(),
                declaration_index: 0
            }]
        )
        .unwrap_err()[0]
            .code,
        "source_identity_conflict"
    );
}
