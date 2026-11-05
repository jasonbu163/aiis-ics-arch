//! SMA本地配置纯域：同一已保存修订的无网络映射预览。
use super::*;
pub fn saved_preview(s: &ConfigurationSnapshot, id: &str) -> Result<Value, String> {
    let v = s
        .document
        .mappings
        .iter()
        .find(|m| m["id"] == id)
        .ok_or("SMA_CONFIGURATION_NOT_FOUND")?;
    let target = s
        .document
        .target_apis
        .iter()
        .find(|t| t["apiKey"] == v["targetApiKey"])
        .ok_or("SMA_CONFIGURATION_REFERENCE_MISSING")?;
    let mut m: runtime::MappingConfiguration =
        serde_json::from_value(v.clone()).map_err(|_| "SMA_CONFIGURATION_MAPPING_INVALID")?;
    let mut t: runtime::TargetApi =
        serde_json::from_value(target.clone()).map_err(|_| "SMA_CONFIGURATION_TARGET_INVALID")?;
    // 仅为已接受纯算法的内存适配；不保存或伪称Backend rowVersion/claim。
    m.row_version = Some(format!("local:{}", s.revision));
    t.row_version = m.row_version.clone();
    m.enabled = true;
    t.enabled = true;
    let rules = s
        .document
        .mapping_value_rules
        .iter()
        .map(|v| {
            serde_json::from_value(v.clone())
                .map_err(|_| "SMA_CONFIGURATION_RULE_INVALID".to_string())
        })
        .collect::<Result<Vec<runtime::ValueRule>, _>>()?;
    let snapshot = runtime::MappingRuntimeSnapshot {
        snapshot_id: String::new(),
        mapping: m,
        target_api: t,
        facts: vec![],
        value_rules: rules,
    };
    let e = runtime::evaluate_snapshot(&snapshot)?;
    let request=e.request.map(|r|json!({"method":r.method,"path":r.path,"pathParameters":r.path_parameters,"query":r.query,"headers":r.headers,"body":r.body}));
    let sources:Vec<_>=snapshot.mapping.bindings.values().filter(|b|b.kind=="fact").map(|b|json!({"sourceKey":b.source_key,"factName":b.fact_name,"metadata":s.document.source_metadata.iter().find(|meta|Some(&meta.source_key)==b.source_key.as_ref()&&Some(&meta.fact_name)==b.fact_name.as_ref()),"status":if s.document.source_metadata.iter().any(|meta|Some(&meta.source_key)==b.source_key.as_ref()&&Some(&meta.fact_name)==b.fact_name.as_ref()){"metadata_only"}else{"unverified"}})).collect();
    Ok(
        json!({"mappingKey":snapshot.mapping.mapping_key,"revision":s.revision,"request":request,"diagnostics":e.diagnostics,"resolvedParameterKeys":e.resolved_parameter_keys,"sourceReferences":sources,"deliveryAvailable":false}),
    )
}
