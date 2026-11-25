//! SMA 完整归档与便携导入的凭据检查。旧配置本身可继续读取。
use super::*;

pub(super) fn check_exchange_payload(
    sources: &[Value],
    targets: &[Value],
    mappings: &[Value],
    existing_targets: &[Value],
    rules: &[Value],
) -> Result<(), String> {
    for source in sources {
        if has_url_credentials(&source["url"])
            || has_named_secret(&source["query"])
            || condition_has_secret(&source["responseCondition"], "path", "equals")
            || source["points"].as_array().is_some_and(|points| {
                points
                    .iter()
                    .any(|point| condition_has_secret(&point["selector"], "key", "value"))
            })
        {
            return Err(format!(
                "SMA_CONFIGURATION_EXPORT_CREDENTIALS:httpSources:{}",
                source["sourceKey"].as_str().unwrap_or("?")
            ));
        }
    }
    for target in targets {
        if has_url_credentials(&target["url"])
            || has_named_secret(&target["bodyTemplate"])
            || condition_has_secret(&target["receipt"], "path", "equals")
        {
            return Err(format!(
                "SMA_CONFIGURATION_EXPORT_CREDENTIALS:targetApis:{}",
                target["apiKey"].as_str().unwrap_or("?")
            ));
        }
    }
    for mapping in mappings {
        let target = targets
            .iter()
            .chain(existing_targets)
            .find(|target| target["apiKey"] == mapping["targetApiKey"]);
        let Some(bindings) = mapping["bindings"].as_object() else {
            continue;
        };
        for (key, binding) in bindings {
            let sensitive_parameter = target
                .and_then(|target| target["parameterSchema"].as_array())
                .is_some_and(|parameters| {
                    parameters.iter().any(|parameter| {
                        parameter["parameterKey"] == *key
                            && (parameter["name"].as_str().is_some_and(sensitive)
                                || parameter["jsonPath"].as_str().is_some_and(sensitive_path))
                    })
                });
            let sensitive_parameter =
                sensitive_parameter || key.split_once(':').is_some_and(|(_, key)| sensitive(key));
            if sensitive_parameter
                && binding["valueRuleKey"].as_str().is_some_and(|rule_key| {
                    rules.iter().any(|rule| {
                        rule["valueRuleKey"] == rule_key
                            && rule["values"]
                                .as_array()
                                .is_some_and(|values| !values.is_empty())
                    })
                })
            {
                return Err(format!(
                    "SMA_CONFIGURATION_EXPORT_CREDENTIALS:mappingValueRules:{}",
                    binding["valueRuleKey"].as_str().unwrap_or("?")
                ));
            }
            if binding["kind"] == "constant"
                && !binding["value"].is_null()
                && (sensitive_parameter || looks_like_secret(&binding["value"]))
            {
                return Err(format!(
                    "SMA_CONFIGURATION_EXPORT_CREDENTIALS:mappings:{}",
                    mapping["mappingKey"].as_str().unwrap_or("?")
                ));
            }
        }
    }
    for rule in rules {
        if rule["values"].as_array().is_some_and(|values| {
            !values.is_empty()
                && (rule["originFactName"].as_str().is_some_and(sensitive)
                    || values.iter().any(looks_like_secret))
        }) {
            return Err(format!(
                "SMA_CONFIGURATION_EXPORT_CREDENTIALS:mappingValueRules:{}",
                rule["valueRuleKey"].as_str().unwrap_or("?")
            ));
        }
    }
    Ok(())
}

pub fn check_full_export(document: &ConfigurationDocument) -> Result<(), String> {
    check_exchange_payload(
        &document.http_sources,
        &document.target_apis,
        &document.mappings,
        &[],
        &document.mapping_value_rules,
    )?;
    for source in &document.source_metadata {
        if has_url_credentials(&json!(source.source_locator)) {
            return Err(format!(
                "SMA_CONFIGURATION_EXPORT_CREDENTIALS:sourceMetadata:{}:{}",
                source.source_key, source.fact_name
            ));
        }
    }
    for material in document.catalog.iter().chain(&document.materials) {
        if openapi_url_has_credentials(&material["sourceLocator"])
            || has_named_secret(&material["bodyTemplate"])
            || has_named_secret(&material["jsonTemplate"])
            || operation_has_secret(&material["operationSnapshot"], false)
        {
            return Err("SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog".into());
        }
    }
    Ok(())
}

fn has_url_credentials(value: &Value) -> bool {
    value
        .as_str()
        .and_then(|url| reqwest::Url::parse(url).ok())
        .is_some_and(|url| url_has_credentials(&url))
}

fn openapi_url_has_credentials(value: &Value) -> bool {
    let Some(raw) = value.as_str() else {
        return false;
    };
    // 仅用占位基准解析相对引用。检查不读取或请求该 URL。
    let base = reqwest::Url::parse("https://openapi.invalid/").expect("static URL");
    base.join(raw).is_ok_and(|url| url_has_credentials(&url))
}

fn url_has_credentials(url: &reqwest::Url) -> bool {
    !url.username().is_empty()
        || url.password().is_some()
        || url
            .query_pairs()
            .any(|(key, value)| (sensitive(&key) && !value.is_empty()) || credential_text(&value))
}

fn operation_has_secret(value: &Value, inherited: bool) -> bool {
    match value {
        Value::Object(fields) => {
            let sensitive_context = inherited
                || fields
                    .get("name")
                    .and_then(Value::as_str)
                    .is_some_and(sensitive);
            fields.iter().any(|(key, value)| {
                // 这些容器的键是字段名，键本身不表示示例或默认值。
                if let (
                    "properties" | "patternProperties" | "headers" | "$defs" | "definitions"
                    | "dependentSchemas" | "dependencies" | "variables",
                    Value::Object(entries),
                ) = (key.as_str(), value)
                {
                    return entries.iter().any(|(name, entry)| {
                        operation_has_secret(entry, sensitive_context || sensitive(name))
                    });
                }
                let found = match key.as_str() {
                    "value" | "example" | "default" | "const" | "enum" => {
                        literal_has_secret(value, sensitive_context)
                    }
                    "examples" => examples_have_secret(value, sensitive_context),
                    "url" | "externalValue" | "$ref" | "$dynamicRef" | "$id" | "$schema"
                    | "operationRef" | "termsOfService" | "authorizationUrl" | "tokenUrl"
                    | "refreshUrl" | "openIdConnectUrl" | "jsonSchemaDialect" => {
                        openapi_url_has_credentials(value)
                    }
                    "discriminator" => value["mapping"]
                        .as_object()
                        .is_some_and(|mapping| mapping.values().any(openapi_url_has_credentials)),
                    _ => false,
                };
                found || operation_has_secret(value, sensitive_context || sensitive(key))
            })
        }
        Value::Array(items) => items
            .iter()
            .any(|item| operation_has_secret(item, inherited)),
        _ => looks_like_secret(value),
    }
}

fn literal_has_secret(value: &Value, sensitive_context: bool) -> bool {
    (sensitive_context && contains_literal(value)) || has_named_secret(value)
}

fn examples_have_secret(value: &Value, sensitive_context: bool) -> bool {
    // Parameter/Media Type maps contain Example Objects or references. Schema
    // examples are direct literals in an array.
    let Value::Object(examples) = value else {
        return literal_has_secret(value, sensitive_context);
    };
    examples.values().any(|example| match example {
        Value::Object(fields)
            if fields.keys().all(|key| {
                matches!(
                    key.as_str(),
                    "$ref" | "summary" | "description" | "value" | "externalValue"
                )
            }) =>
        {
            fields
                .get("value")
                .is_some_and(|value| literal_has_secret(value, sensitive_context))
                || fields
                    .get("externalValue")
                    .is_some_and(openapi_url_has_credentials)
        }
        _ => literal_has_secret(example, sensitive_context),
    })
}

fn contains_literal(value: &Value) -> bool {
    match value {
        Value::Null => false,
        Value::String(value) => !value.is_empty(),
        Value::Array(values) => values.iter().any(contains_literal),
        Value::Object(values) => values.values().any(contains_literal),
        _ => true,
    }
}

fn has_named_secret(value: &Value) -> bool {
    match value {
        Value::Object(values) => values
            .iter()
            .any(|(name, v)| (sensitive(name) && contains_literal(v)) || has_named_secret(v)),
        Value::Array(values) => values.iter().any(has_named_secret),
        _ => looks_like_secret(value),
    }
}

fn condition_has_secret(condition: &Value, field: &str, value_key: &str) -> bool {
    let value = &condition[value_key];
    (condition[field].as_str().is_some_and(sensitive_path) && contains_literal(value))
        || looks_like_secret(value)
}

fn sensitive_path(path: &str) -> bool {
    path.split(['.', '/', '[', ']']).any(sensitive)
}

fn sensitive(name: &str) -> bool {
    let compact = name
        .chars()
        .filter(char::is_ascii_alphanumeric)
        .flat_map(char::to_lowercase)
        .collect::<String>();
    matches!(compact.as_str(), "auth" | "pwd" | "sig" | "jwt")
        || [
            "authorization",
            "cookie",
            "password",
            "passwd",
            "passcode",
            "apikey",
            "accesskey",
            "privatekey",
            "clientkey",
            "token",
            "secret",
            "credential",
            "credentials",
            "signature",
            "sessionid",
            "assertion",
        ]
        .iter()
        .any(|suffix| compact.ends_with(suffix))
}

fn looks_like_secret(value: &Value) -> bool {
    value.as_str().is_some_and(credential_text)
}

fn credential_text(value: &str) -> bool {
    let lower = value.trim_start().to_ascii_lowercase();
    lower
        .split_once(char::is_whitespace)
        .is_some_and(|(scheme, rest)| {
            matches!(scheme, "bearer" | "basic" | "digest" | "aws4-hmac-sha256")
                && !rest.trim().is_empty()
        })
        || (value.starts_with("eyJ") && value.split('.').count() == 3)
        || [
            "ghp_",
            "gho_",
            "ghu_",
            "ghs_",
            "ghr_",
            "github_pat_",
            "sk-proj-",
            "sk-",
        ]
        .iter()
        .any(|prefix| {
            value.strip_prefix(prefix).is_some_and(|rest| {
                rest.len() >= 12
                    && rest
                        .bytes()
                        .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'-' | b'_'))
            })
        })
}
