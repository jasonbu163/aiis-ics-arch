//! SMA本地配置纯域：完整配置图校验与固定边界。
use super::*;
pub fn validate(d: &ConfigurationDocument) -> Result<(), String> {
    if !matches!(d.connection.scheme.as_str(), "http" | "https")
        || (d.connection.host.is_empty() != (d.connection.port == 0))
        || d.connection
            .host
            .chars()
            .any(|c| c.is_whitespace() || matches!(c, '/' | '@' | '?' | '#'))
    {
        return Err("SMA_CONFIGURATION_CONNECTION_INVALID".into());
    }
    for set in [
        &d.catalog,
        &d.materials,
        &d.target_apis,
        &d.mapping_value_rules,
        &d.mappings,
        &d.http_sources,
    ] {
        if set.len() > MAX_ITEMS {
            return Err("SMA_CONFIGURATION_LIMIT_EXCEEDED".into());
        }
    }
    if let Some(config) = &d.acquisition_loopback {
        crate::domain::acquisition::validate_config(config)?;
    }
    if d.source_metadata.len() > MAX_ITEMS
        || serde_json::to_vec_pretty(&backup(d))
            .map_err(|_| "SMA_CONFIGURATION_INVALID")?
            .len()
            > MAX_BYTES
    {
        return Err("SMA_CONFIGURATION_LIMIT_EXCEEDED".into());
    }
    for r in [
        "materials",
        "targetApis",
        "mappingValueRules",
        "mappings",
        "httpSources",
    ] {
        let k = key_field(r)?;
        let mut keys = BTreeSet::new();
        let mut ids = BTreeSet::new();
        for v in collection(d, r)? {
            if !v["rowVersion"].is_null() {
                return Err("SMA_CONFIGURATION_REMOTE_VERSION_FORBIDDEN".into());
            }
            if !valid_key(text(v, k)?)
                || !valid_key(text(v, "id")?)
                || !keys.insert(text(v, k)?)
                || !ids.insert(text(v, "id")?)
            {
                return Err(format!("SMA_CONFIGURATION_DUPLICATE_OR_INVALID_KEY:{r}"));
            }
        }
    }
    let mut catalog = BTreeSet::new();
    for op in &d.catalog {
        fields(
            op,
            &[
                "method",
                "path",
                "summary",
                "operationId",
                "operationSnapshot",
                "requestContract",
                "bodyTemplate",
                "normalizationStatus",
                "normalizationErrorCode",
                "jsonTemplate",
                "contentHash",
                "sourceLocator",
            ],
        )?;
        validate_operation(op, "method")?;
        if !catalog.insert((
            text(op, "sourceLocator")?,
            text(op, "method")?,
            text(op, "path")?,
        )) {
            return Err("SMA_CONFIGURATION_CATALOG_DUPLICATE".into());
        }
    }
    for m in &d.materials {
        fields(
            m,
            &[
                "id",
                "materialKey",
                "sourceType",
                "sourceLocator",
                "httpMethod",
                "path",
                "operationId",
                "name",
                "operationSnapshot",
                "requestContract",
                "bodyTemplate",
                "normalizationStatus",
                "normalizationErrorCode",
                "contentHash",
                "rowVersion",
                "createdAt",
                "updatedAt",
            ],
        )?;
        validate_operation(m, "httpMethod")?;
        if text(m, "sourceType")? != "openapi"
            || !catalog.contains(&(
                text(m, "sourceLocator")?,
                text(m, "httpMethod")?,
                text(m, "path")?,
            ))
        {
            return Err(format!(
                "SMA_CONFIGURATION_REFERENCE_MISSING:{}",
                text(m, "materialKey")?
            ));
        }
    }
    let mut metadata = BTreeMap::new();
    for m in &d.source_metadata {
        if !valid_key(&m.source_key)
            || !valid_key(&m.fact_name)
            || !typed(&m.data_type)
            || m.source_locator.trim().is_empty()
            || m.fact_kind
                .as_deref()
                .is_some_and(|s| !matches!(s, "current" | "incremental"))
            || metadata
                .insert((&m.source_key, &m.fact_name), &m.data_type)
                .is_some()
        {
            return Err("SMA_CONFIGURATION_SOURCE_METADATA_INVALID".into());
        }
    }
    let sources = crate::domain::http_mapping::validate_sources(&d.http_sources)?;
    for source in &sources {
        for point in &source.points {
            metadata.insert((&source.source_key, &point.point_key), &point.data_type);
        }
    }
    if let Some(limits) = &d.runtime_limits {
        crate::domain::http_mapping::validate_limits(limits)?;
    }
    let mut targets = BTreeMap::new();
    for v in &d.target_apis {
        fields(
            v,
            &[
                "id",
                "apiKey",
                "name",
                "httpMethod",
                "path",
                "url",
                "timeoutMs",
                "receipt",
                "schemaSource",
                "originType",
                "originMaterialKey",
                "operationId",
                "bodyTemplate",
                "parameterSchema",
                "idempotencySupported",
                "enabled",
                "rowVersion",
                "createdAt",
                "updatedAt",
            ],
        )?;
        let t: runtime::TargetApi =
            serde_json::from_value(v.clone()).map_err(|_| "SMA_CONFIGURATION_TARGET_INVALID")?;
        validate_target(&t)?;
        crate::domain::http_mapping::validate_target_options(v, &t)?;
        if v["idempotencySupported"].as_bool().is_none()
            || !matches!(text(v, "schemaSource")?, "manual" | "openapi")
        {
            return Err("SMA_CONFIGURATION_TARGET_INVALID".into());
        }
        match text(v, "originType")? {
            "api_material" => {
                let k = text(v, "originMaterialKey")?;
                if !d.materials.iter().any(|m| m["materialKey"] == k) {
                    return Err(format!(
                        "SMA_CONFIGURATION_REFERENCE_MISSING:{}:{k}",
                        t.api_key
                    ));
                }
            }
            "manual" if v["originMaterialKey"].is_null() => (),
            _ => return Err("SMA_CONFIGURATION_TARGET_ORIGIN_INVALID".into()),
        }
        targets.insert(t.api_key.clone(), t);
    }
    let mut rules = BTreeMap::new();
    for v in &d.mapping_value_rules {
        fields(
            v,
            &[
                "id",
                "valueRuleKey",
                "name",
                "dataType",
                "values",
                "originSourceKey",
                "originFactName",
                "enabled",
                "rowVersion",
                "createdAt",
                "updatedAt",
            ],
        )?;
        let r: runtime::ValueRule =
            serde_json::from_value(v.clone()).map_err(|_| "SMA_CONFIGURATION_RULE_INVALID")?;
        if !typed(&r.data_type)
            || r.values.iter().any(|v| !value_type(v, &r.data_type))
            || v["enabled"].as_bool().is_none()
            || text(v, "name")?.trim().is_empty()
            || v["originSourceKey"].is_null() != v["originFactName"].is_null()
        {
            return Err("SMA_CONFIGURATION_RULE_INVALID".into());
        }
        if let Some(k) = v["originSourceKey"].as_str() {
            if let Some(source) = sources.iter().find(|source| source.source_key == k) {
                let point = source
                    .points
                    .iter()
                    .find(|point| v["originFactName"] == point.point_key);
                if !point.is_some_and(|point| point.data_type == r.data_type) {
                    return Err(format!(
                        "SMA_CONFIGURATION_REFERENCE_MISSING:{}:{k}",
                        r.value_rule_key
                    ));
                }
            }
        }
        rules.insert(r.value_rule_key.clone(), (r, v["enabled"] == true));
    }
    for v in &d.mappings {
        fields(
            v,
            &[
                "id",
                "mappingKey",
                "name",
                "sourceKey",
                "targetApiKey",
                "targetApiId",
                "bindings",
                "intervalMs",
                "maxAgeMs",
                "enabled",
                "rowVersion",
                "createdAt",
                "updatedAt",
            ],
        )?;
        let m: runtime::MappingConfiguration =
            serde_json::from_value(v.clone()).map_err(|_| "SMA_CONFIGURATION_MAPPING_INVALID")?;
        let active_http = !v["maxAgeMs"].is_null();
        if active_http
            && !v["maxAgeMs"]
                .as_u64()
                .is_some_and(|ms| (1..=604_800_000).contains(&ms))
        {
            return Err(format!("SMA_HTTP_MAX_AGE_INVALID:{}", m.mapping_key));
        }
        let t = targets.get(&m.target_api_key).ok_or_else(|| {
            format!(
                "SMA_CONFIGURATION_REFERENCE_MISSING:{}:{}",
                m.mapping_key, m.target_api_key
            )
        })?;
        if (active_http && t.http_method != "POST")
            || m.target_api_id != t.id
            || m.name.trim().is_empty()
            || m.interval_ms == 0
            || m.interval_ms > 86_400_000
        {
            return Err("SMA_CONFIGURATION_MAPPING_INVALID".into());
        }
        if active_http {
            crate::domain::http_mapping::validate_wire_parameters(t)?;
        }
        for (k, b) in &m.bindings {
            fields(
                &v["bindings"][k],
                &["kind", "value", "sourceKey", "factName", "valueRuleKey"],
            )?;
            let p = t
                .parameter_schema
                .iter()
                .find(|p| &p.parameter_key == k)
                .ok_or_else(|| {
                    format!("SMA_CONFIGURATION_BINDING_INVALID:{}:{k}", m.mapping_key)
                })?;
            match b.kind.as_str() {
                "constant"
                    if b.source_key.is_none()
                        && b.fact_name.is_none()
                        && b.value
                            .as_ref()
                            .is_some_and(|v| value_type(v, &p.data_type)) =>
                {
                    ()
                }
                "fact"
                    if b.value.is_none()
                        && b.source_key.as_deref().is_some_and(valid_key)
                        && b.fact_name.as_deref().is_some_and(valid_key) =>
                {
                    if let Some(tp) = metadata.get(&(
                        b.source_key.as_ref().unwrap(),
                        b.fact_name.as_ref().unwrap(),
                    )) {
                        if !compatible(tp, &p.data_type) {
                            return Err(format!(
                                "SMA_CONFIGURATION_SOURCE_TYPE_INCOMPATIBLE:{}:{k}",
                                m.mapping_key
                            ));
                        }
                    }
                    if active_http
                        && !sources.iter().any(|s| {
                            Some(s.source_key.as_str()) == b.source_key.as_deref()
                                && s.points
                                    .iter()
                                    .any(|p| Some(p.point_key.as_str()) == b.fact_name.as_deref())
                        })
                    {
                        return Err(format!(
                            "SMA_CONFIGURATION_REFERENCE_MISSING:{}:{k}",
                            m.mapping_key
                        ));
                    }
                }
                _ => {
                    return Err(format!(
                        "SMA_CONFIGURATION_BINDING_INVALID:{}:{k}",
                        m.mapping_key
                    ))
                }
            }
            if let Some(key) = &b.value_rule_key {
                let (r, enabled) = rules.get(key).ok_or_else(|| {
                    format!(
                        "SMA_CONFIGURATION_REFERENCE_MISSING:{}:{key}",
                        m.mapping_key
                    )
                })?;
                if (active_http && !enabled)
                    || r.values.is_empty()
                    || r.data_type != p.data_type
                    || b.value
                        .as_ref()
                        .is_some_and(|v| !runtime::value_matches_rule(v, &r.values))
                {
                    return Err(format!(
                        "SMA_CONFIGURATION_RULE_INCOMPATIBLE:{}:{k}",
                        m.mapping_key
                    ));
                }
            }
        }
        if m.enabled
            && t.parameter_schema
                .iter()
                .any(|p| p.required && !m.bindings.contains_key(&p.parameter_key))
        {
            return Err(format!(
                "SMA_CONFIGURATION_REQUIRED_BINDING_MISSING:{}",
                m.mapping_key
            ));
        }
    }
    Ok(())
}
fn validate_operation(v: &Value, method: &str) -> Result<(), String> {
    if text(v, "sourceLocator")?.trim().is_empty()
        || !v["operationSnapshot"].is_object()
        || !matches!(text(v, "normalizationStatus")?, "ready" | "unsupported")
    {
        return Err("SMA_CONFIGURATION_MATERIAL_INVALID".into());
    }
    if v["normalizationStatus"] == "ready" {
        let parameters = serde_json::from_value(v["requestContract"].clone())
            .map_err(|_| "SMA_CONFIGURATION_MATERIAL_INVALID")?;
        validate_target(&runtime::TargetApi {
            id: "validation".into(),
            api_key: "validation".into(),
            name: "validation".into(),
            http_method: text(v, method)?.into(),
            path: text(v, "path")?.into(),
            body_template: v["bodyTemplate"].clone(),
            parameter_schema: parameters,
            enabled: true,
            row_version: None,
        })?
    }
    Ok(())
}
fn validate_target(t: &runtime::TargetApi) -> Result<(), String> {
    if t.name.trim().is_empty()
        || !matches!(
            t.http_method.as_str(),
            "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD" | "OPTIONS" | "TRACE"
        )
        || !t.path.starts_with('/')
        || t.path.starts_with("//")
        || t.path.contains(['?', '#'])
        || !t.body_template.is_object()
    {
        return Err("SMA_CONFIGURATION_TARGET_INVALID".into());
    }
    let mut keys = BTreeSet::new();
    let mut names = BTreeSet::new();
    for p in &t.parameter_schema {
        if !typed(&p.data_type)
            || !matches!(p.location.as_str(), "body" | "query" | "path" | "header")
            || p.name.trim().is_empty()
            || p.name.chars().any(char::is_control)
            || p.parameter_key != format!("{}:{}", p.location, p.name)
            || !keys.insert(&p.parameter_key)
            || (p.location == "path" && !p.required)
        {
            return Err("SMA_CONFIGURATION_PARAMETER_INVALID".into());
        }
        if p.location == "path" {
            names.insert(p.name.as_str());
        }
        if p.location == "body" {
            let mut node = &t.body_template;
            for part in p
                .json_path
                .as_deref()
                .ok_or("SMA_CONFIGURATION_PARAMETER_INVALID")?
                .split('.')
            {
                node = node
                    .get(part)
                    .ok_or("SMA_CONFIGURATION_PARAMETER_INVALID")?;
            }
            if node.is_array() || node.is_object() {
                return Err("SMA_CONFIGURATION_PARAMETER_INVALID".into());
            }
        }
    }
    let mut placeholders = BTreeSet::new();
    let mut rest = t.path.as_str();
    while let Some(i) = rest.find('{') {
        rest = &rest[i + 1..];
        let end = rest
            .find('}')
            .ok_or("SMA_CONFIGURATION_PARAMETER_INVALID")?;
        placeholders.insert(&rest[..end]);
        rest = &rest[end + 1..];
    }
    if placeholders != names {
        return Err("SMA_CONFIGURATION_PARAMETER_INVALID".into());
    }
    Ok(())
}
