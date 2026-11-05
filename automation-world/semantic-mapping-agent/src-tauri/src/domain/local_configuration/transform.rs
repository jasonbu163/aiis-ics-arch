//! SMA本地配置纯域：有限资源变更及来源身份正规化。
use super::*;
pub fn transform(
    old: &ConfigurationDocument,
    i: &ChangeIntent,
) -> Result<ConfigurationDocument, String> {
    if serde_json::to_vec(i)
        .map_err(|_| "SMA_CONFIGURATION_INVALID")?
        .len()
        > MAX_BYTES
    {
        return Err("SMA_CONFIGURATION_LIMIT_EXCEEDED".into());
    }
    let mut d = old.clone();
    match i.kind.as_str() {
        "connection" => {
            d.connection = serde_json::from_value(i.payload.clone())
                .map_err(|_| "SMA_CONFIGURATION_CONNECTION_INVALID")?
        }
        "metadata" => {
            d.source_metadata = serde_json::from_value(i.payload.clone())
                .map_err(|_| "SMA_CONFIGURATION_SOURCE_METADATA_INVALID")?
        }
        "catalog" => {
            d.catalog = serde_json::from_value(i.payload.clone())
                .map_err(|_| "SMA_CONFIGURATION_CATALOG_INVALID")?;
            if d.catalog.is_empty() {
                return Err("API_MATERIAL_CATALOG_EMPTY".into());
            }
        }
        "restore" => {
            let b: ConfigurationBackup = serde_json::from_value(i.payload.clone())
                .map_err(|_| "SMA_CONFIGURATION_BACKUP_INVALID")?;
            if b.format != FORMAT || b.schema_version != 1 {
                return Err("SMA_CONFIGURATION_BACKUP_UNSUPPORTED".into());
            }
            d = b.document;
        }
        "selection" => {
            let keys = i
                .payload
                .as_array()
                .ok_or("SMA_CONFIGURATION_SELECTION_INVALID")?;
            let selected: BTreeSet<_> = keys.iter().filter_map(Value::as_str).collect();
            if selected.len() != keys.len() {
                return Err("SMA_CONFIGURATION_SELECTION_INVALID".into());
            }
            let mut materials = vec![];
            for op in &d.catalog {
                let identity = format!("{} {}", text(op, "method")?, text(op, "path")?);
                if !selected.contains(identity.as_str()) {
                    continue;
                }
                let locator = text(op, "sourceLocator")?;
                let key = format!("material-{:016x}", hash(&format!("{locator}|{identity}")));
                let existing = old.materials.iter().find(|m| m["materialKey"] == key);
                let mut material = json!({"id":format!("materials:{key}"),"materialKey":key,"sourceType":"openapi","sourceLocator":locator,"httpMethod":op["method"],"path":op["path"],"operationId":op["operationId"],"name":op["summary"].as_str().or(op["operationId"].as_str()).unwrap_or(&identity),"operationSnapshot":op["operationSnapshot"],"requestContract":op["requestContract"],"bodyTemplate":op["bodyTemplate"],"normalizationStatus":op["normalizationStatus"],"normalizationErrorCode":op["normalizationErrorCode"],"contentHash":op["contentHash"],"rowVersion":null,"createdAt":crate::domain::runtime::business_now_string(),"updatedAt":crate::domain::runtime::business_now_string()});
                if let Some(e) = existing {
                    material["id"] = e["id"].clone();
                    material["createdAt"] = e["createdAt"].clone();
                    material["updatedAt"] = e["updatedAt"].clone();
                    if &material != e {
                        material["updatedAt"] =
                            json!(crate::domain::runtime::business_now_string());
                    }
                }
                materials.push(material);
            }
            if materials.len() != selected.len() {
                return Err("SMA_CONFIGURATION_SELECTION_INVALID".into());
            }
            d.materials = materials;
        }
        "loadMaterials" => {
            for key in i
                .payload
                .as_array()
                .ok_or("SMA_CONFIGURATION_SELECTION_INVALID")?
            {
                let m = d
                    .materials
                    .iter()
                    .find(|m| &m["materialKey"] == key)
                    .ok_or("SMA_CONFIGURATION_REFERENCE_MISSING")?;
                if m["normalizationStatus"] != "ready"
                    || d.target_apis.iter().any(|t| t["originMaterialKey"] == *key)
                {
                    continue;
                }
                let api_key = format!("api-{}", text(m, "materialKey")?);
                d.target_apis.push(json!({"id":format!("targetApis:{api_key}"),"apiKey":api_key,"name":m["name"],"httpMethod":m["httpMethod"],"path":m["path"],"schemaSource":"openapi","originType":"api_material","originMaterialKey":key,"operationId":m["operationId"],"bodyTemplate":m["bodyTemplate"],"parameterSchema":m["requestContract"],"idempotencySupported":false,"enabled":true,"rowVersion":null,"createdAt":crate::domain::runtime::business_now_string(),"updatedAt":crate::domain::runtime::business_now_string()}));
            }
        }
        "delete" => {
            let items = collection_mut(&mut d, &i.resource)?;
            let id = i.id.as_deref().ok_or("SMA_CONFIGURATION_ID_REQUIRED")?;
            let pos = items
                .iter()
                .position(|v| v["id"] == id)
                .ok_or("SMA_CONFIGURATION_NOT_FOUND")?;
            items.remove(pos);
        }
        "upsert" | "import" => {
            let key = key_field(&i.resource)?;
            let incoming = if i.kind == "import" {
                i.payload
                    .as_array()
                    .ok_or("SMA_CONFIGURATION_IMPORT_INVALID")?
                    .clone()
            } else {
                vec![i.payload.clone()]
            };
            let mut seen = BTreeSet::new();
            for mut item in incoming {
                if i.resource == "mappingValueRules" && item["valueRuleKey"].is_null() {
                    let source = text(&item, "originSourceKey")?;
                    let fact = text(&item, "originFactName")?;
                    item["valueRuleKey"] = json!(format!(
                        "fact-rule-{:016x}",
                        hash(&format!("{source}|{fact}"))
                    ));
                }
                let business_key = text(&item, key)?.to_string();
                if !valid_key(&business_key) || !seen.insert(business_key.clone()) {
                    return Err(format!("SMA_CONFIGURATION_DUPLICATE_KEY:{business_key}"));
                }
                let items = collection(&d, &i.resource)?;
                let existing = if i.kind == "upsert" {
                    i.id.as_deref()
                        .and_then(|id| items.iter().find(|v| v["id"] == id))
                } else {
                    items.iter().find(|v| v[key] == business_key)
                }
                .cloned();
                if i.kind == "upsert" && i.id.is_some() && existing.is_none() {
                    return Err("SMA_CONFIGURATION_NOT_FOUND".into());
                }
                if let Some(e) = &existing {
                    if e[key] != business_key {
                        return Err("SMA_CONFIGURATION_KEY_IMMUTABLE".into());
                    }
                    if i.resource == "targetApis" {
                        item["originType"] = e["originType"].clone();
                        item["originMaterialKey"] = e["originMaterialKey"].clone();
                    }
                    if i.resource == "mappingValueRules"
                        && (item["originSourceKey"] != e["originSourceKey"]
                            || item["originFactName"] != e["originFactName"])
                    {
                        return Err("SMA_CONFIGURATION_ORIGIN_IMMUTABLE".into());
                    }
                }
                normalize(&d, &i.resource, &mut item, existing.as_ref())?;
                let items = collection_mut(&mut d, &i.resource)?;
                if let Some(e) = existing {
                    let pos = items.iter().position(|v| v["id"] == e["id"]).unwrap();
                    items[pos] = item;
                } else {
                    items.push(item);
                }
            }
        }
        _ => return Err("SMA_CONFIGURATION_INTENT_INVALID".into()),
    }
    validate(&d)?;
    Ok(d)
}
fn normalize(
    d: &ConfigurationDocument,
    r: &str,
    v: &mut Value,
    old: Option<&Value>,
) -> Result<(), String> {
    let key = key_field(r)?;
    let id = format!("{r}:{}", text(v, key)?);
    v["id"] = old.map(|e| e["id"].clone()).unwrap_or(json!(id));
    v["rowVersion"] = Value::Null;
    v["createdAt"] = old
        .map(|e| e["createdAt"].clone())
        .unwrap_or(json!(crate::domain::runtime::business_now_string()));
    v["updatedAt"] = old
        .map(|e| e["updatedAt"].clone())
        .unwrap_or(v["createdAt"].clone());
    if r == "targetApis" {
        if v.get("httpMethod").is_none() {
            v["httpMethod"] = json!("POST");
        }
        if v.get("originType").is_none() {
            v["originType"] = json!("manual");
            v["originMaterialKey"] = Value::Null;
        }
    }
    if r == "mappings" {
        let t = d
            .target_apis
            .iter()
            .find(|t| t["apiKey"] == v["targetApiKey"])
            .ok_or("SMA_CONFIGURATION_REFERENCE_MISSING")?;
        v["targetApiId"] = t["id"].clone();
        let legacy = v["sourceKey"].as_str().map(str::to_owned);
        for b in v["bindings"]
            .as_object_mut()
            .ok_or("SMA_CONFIGURATION_BINDING_INVALID")?
            .values_mut()
        {
            if b["kind"] == "fact" {
                if let Some(s) = &legacy {
                    if b["sourceKey"].as_str().is_some_and(|bs| bs != s) {
                        return Err("SMA_CONFIGURATION_LEGACY_SOURCE_CONFLICT".into());
                    }
                    if b["sourceKey"].is_null() {
                        b["sourceKey"] = json!(s);
                    }
                }
            }
        }
        v["sourceKey"] = Value::Null;
    }
    if let Some(e) = old {
        if v != e {
            v["updatedAt"] = json!(crate::domain::runtime::business_now_string());
        }
    }
    Ok(())
}
fn hash(s: &str) -> u64 {
    s.bytes().fold(0xcbf29ce484222325, |h, b| {
        (h ^ u64::from(b)).wrapping_mul(0x100000001b3)
    })
}
