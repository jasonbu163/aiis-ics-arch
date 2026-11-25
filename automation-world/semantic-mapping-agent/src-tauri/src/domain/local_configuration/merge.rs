//! SMA 配置交换：以稳定身份合并传入配置，再由完整图校验。
use super::*;

pub(super) fn merge(d: &mut ConfigurationDocument, raw: &Value) -> Result<(), String> {
    let patch = raw.as_object().ok_or("SMA_CONFIGURATION_IMPORT_INVALID")?;
    for key in patch.keys() {
        if !matches!(
            key.as_str(),
            "connection"
                | "httpSources"
                | "targetApis"
                | "mappingValueRules"
                | "mappings"
                | "sourceMetadata"
                | "runtimeLimits"
        ) {
            return Err(format!("SMA_CONFIGURATION_FIELD_UNKNOWN:{key}"));
        }
    }
    let items = |key: &str| {
        patch
            .get(key)
            .and_then(Value::as_array)
            .map_or(&[][..], Vec::as_slice)
    };
    super::secret_fields::check_exchange_payload(
        items("httpSources"),
        items("targetApis"),
        items("mappings"),
        &d.target_apis,
        items("mappingValueRules"),
    )?;
    if let Some(connection) = patch.get("connection") {
        d.connection = serde_json::from_value(connection.clone())
            .map_err(|_| "SMA_CONFIGURATION_CONNECTION_INVALID")?;
    }
    if let Some(limits) = patch.get("runtimeLimits") {
        d.runtime_limits =
            Some(serde_json::from_value(limits.clone()).map_err(|_| "SMA_HTTP_LIMITS_INVALID")?);
    }
    if let Some(metadata) = patch.get("sourceMetadata") {
        let incoming: Vec<SourceMetadata> = serde_json::from_value(metadata.clone())
            .map_err(|_| "SMA_CONFIGURATION_SOURCE_METADATA_INVALID")?;
        let mut seen = BTreeSet::new();
        for item in incoming {
            if !seen.insert((item.source_key.clone(), item.fact_name.clone())) {
                return Err(format!(
                    "SMA_CONFIGURATION_DUPLICATE_KEY:sourceMetadata:{}",
                    item.source_key
                ));
            }
            if let Some(old) = d
                .source_metadata
                .iter_mut()
                .find(|old| old.source_key == item.source_key && old.fact_name == item.fact_name)
            {
                *old = item;
            } else {
                d.source_metadata.push(item);
            }
        }
    }

    for resource in ["httpSources", "targetApis", "mappingValueRules", "mappings"] {
        let Some(raw) = patch.get(resource) else {
            continue;
        };
        let rows = raw
            .as_array()
            .ok_or_else(|| format!("SMA_CONFIGURATION_IMPORT_INVALID:{resource}"))?;
        let key_field = key_field(resource)?;
        let mut seen = BTreeSet::new();
        let mut ids = BTreeSet::new();
        for (index, row) in rows.iter().enumerate() {
            let key = text(row, key_field)
                .map_err(|_| format!("SMA_CONFIGURATION_KEY_INVALID:{resource}:{}", index + 1))?;
            if !seen.insert(key) || row["id"].as_str().is_some_and(|id| !ids.insert(id)) {
                return Err(format!("SMA_CONFIGURATION_DUPLICATE_KEY:{resource}:{key}"));
            }
            let incoming_id = row["id"].as_str().map(str::to_owned);
            let mut row = row.clone();
            let old = collection(d, resource)?
                .iter()
                .find(|item| item[key_field] == key)
                .cloned();
            if let Some(old) = &old {
                if !row["id"].is_null() && row["id"] != old["id"] {
                    return Err(format!("SMA_CONFIGURATION_ID_CONFLICT:{resource}:{key}"));
                }
                if resource == "targetApis" {
                    row["originType"] = old["originType"].clone();
                    row["originMaterialKey"] = old["originMaterialKey"].clone();
                }
            }
            if resource == "httpSources" {
                merge_points(old.as_ref(), &mut row, key)?;
            }
            super::transform::normalize(d, resource, &mut row, old.as_ref())
                .map_err(|code| format!("{code}:{resource}:{key}"))?;
            if old.is_none() {
                if let Some(id) = incoming_id {
                    row["id"] = json!(id);
                }
            }
            let items = collection_mut(d, resource)?;
            if let Some(position) = items.iter().position(|item| item[key_field] == key) {
                items[position] = row;
            } else {
                items.push(row);
            }
        }
    }
    Ok(())
}

fn merge_points(old: Option<&Value>, row: &mut Value, key: &str) -> Result<(), String> {
    let mut points = old
        .and_then(|row| row["points"].as_array())
        .cloned()
        .unwrap_or_default();
    let incoming = row["points"]
        .as_array()
        .ok_or_else(|| format!("SMA_HTTP_POINTS_INVALID:{key}"))?;
    let mut seen = BTreeSet::new();
    for point in incoming {
        let point_key =
            text(point, "pointKey").map_err(|_| format!("SMA_HTTP_POINT_INVALID:{key}"))?;
        if !seen.insert(point_key) {
            return Err(format!(
                "SMA_CONFIGURATION_DUPLICATE_KEY:httpPoints:{key}:{point_key}"
            ));
        }
        if let Some(index) = points.iter().position(|p| p["pointKey"] == point_key) {
            points[index] = point.clone();
        } else {
            points.push(point.clone());
        }
    }
    row["points"] = Value::Array(points);
    Ok(())
}
