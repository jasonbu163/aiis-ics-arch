//! 两个固定YAML来源的有界读取、严格结构与全量停用候选转换；不导入未知值、不执行网络。
use crate::domain::{
    local_configuration::*,
    local_sample::{digest, encode},
    yaml_migration::*,
};
use serde::de::{DeserializeSeed, MapAccess, SeqAccess, Visitor};
use serde_yaml::{Mapping, Value};
use std::{
    cell::Cell,
    collections::{BTreeMap, BTreeSet},
    fs::{self, File, Metadata},
    io::Read,
    path::{Path, PathBuf},
};

struct Seed<'a> {
    depth: usize,
    nodes: &'a Cell<usize>,
}
impl<'de> DeserializeSeed<'de> for Seed<'_> {
    type Value = Value;
    fn deserialize<D: serde::Deserializer<'de>>(self, d: D) -> Result<Value, D::Error> {
        let n = self.nodes.get() + 1;
        self.nodes.set(n);
        if self.depth > 16 || n > 100000 {
            return Err(serde::de::Error::custom("yaml_structure_limit"));
        }
        d.deserialize_any(self)
    }
}
impl<'de> Visitor<'de> for Seed<'_> {
    type Value = Value;
    fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        f.write_str("bounded YAML")
    }
    fn visit_unit<E: serde::de::Error>(self) -> Result<Value, E> {
        Ok(Value::Null)
    }
    fn visit_bool<E: serde::de::Error>(self, v: bool) -> Result<Value, E> {
        Ok(Value::Bool(v))
    }
    fn visit_i64<E: serde::de::Error>(self, v: i64) -> Result<Value, E> {
        Ok(Value::Number(v.into()))
    }
    fn visit_u64<E: serde::de::Error>(self, v: u64) -> Result<Value, E> {
        Ok(Value::Number(v.into()))
    }
    fn visit_f64<E: serde::de::Error>(self, v: f64) -> Result<Value, E> {
        if !v.is_finite() {
            return Err(E::custom("yaml_number"));
        }
        Ok(Value::Number(v.into()))
    }
    fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Value, E> {
        Ok(Value::String(v.into()))
    }
    fn visit_string<E: serde::de::Error>(self, v: String) -> Result<Value, E> {
        Ok(Value::String(v))
    }
    fn visit_seq<A: SeqAccess<'de>>(self, mut a: A) -> Result<Value, A::Error> {
        let mut v = vec![];
        while let Some(x) = a.next_element_seed(Seed {
            depth: self.depth + 1,
            nodes: self.nodes,
        })? {
            v.push(x);
        }
        Ok(Value::Sequence(v))
    }
    fn visit_map<A: MapAccess<'de>>(self, mut a: A) -> Result<Value, A::Error> {
        let mut v = Mapping::new();
        while let Some(k) = a.next_key_seed(Seed {
            depth: self.depth + 1,
            nodes: self.nodes,
        })? {
            if !k.is_string() || v.contains_key(&k) {
                return Err(serde::de::Error::custom("yaml_duplicate_or_invalid_key"));
            }
            let x = a.next_value_seed(Seed {
                depth: self.depth + 1,
                nodes: self.nodes,
            })?;
            v.insert(k, x);
        }
        Ok(Value::Mapping(v))
    }
}
fn parse(text: &str) -> LocalResult<Value> {
    // Reject expansion/tag syntax before deserialization. Quoted scalar content is not syntax.
    for line in text.lines() {
        let mut quote = None;
        let mut escape = false;
        let mut prev = ' ';
        for ch in line.chars() {
            if let Some(q) = quote {
                if escape {
                    escape = false;
                } else if ch == '\\' && q == '"' {
                    escape = true;
                } else if ch == q {
                    quote = None;
                }
            } else if ch == '#' && (prev.is_whitespace() || prev == ' ') {
                break;
            } else if ch == '\'' || ch == '"' {
                quote = Some(ch);
            } else if matches!(ch, '&' | '*' | '!')
                && (prev.is_whitespace() || matches!(prev, ':' | '[' | ',' | '{' | '-'))
            {
                return Err("yaml_expansion_forbidden".into());
            }
            prev = ch;
        }
    }
    if text
        .lines()
        .all(|l| l.trim().is_empty() || l.trim_start().starts_with('#'))
    {
        return Ok(Value::Null);
    }
    let nodes = Cell::new(0);
    let mut docs = serde_yaml::Deserializer::from_str(text);
    let v = match docs.next() {
        Some(d) => Seed {
            depth: 0,
            nodes: &nodes,
        }
        .deserialize(d)
        .map_err(|_| "yaml_syntax_or_structure")?,
        None => Value::Null,
    };
    if docs.next().is_some() {
        return Err("yaml_multiple_documents".into());
    }
    Ok(v)
}
fn empty(v: &Value) -> bool {
    v.is_null()
        || v.as_mapping().map(|m| m.is_empty()).unwrap_or(false)
        || v.as_sequence().map(|s| s.is_empty()).unwrap_or(false)
}
fn mapping<'a>(v: &'a Value) -> LocalResult<&'a Mapping> {
    v.as_mapping().ok_or_else(|| "yaml_object_required".into())
}
fn get<'a>(m: &'a Mapping, k: &str) -> Option<&'a Value> {
    m.get(Value::String(k.into()))
}
fn string(m: &Mapping, k: &str, max: usize, required: bool) -> LocalResult<Option<String>> {
    match get(m, k) {
        None if !required => Ok(None),
        Some(Value::String(s)) if !s.is_empty() && s.len() <= max => Ok(Some(s.clone())),
        _ => Err("yaml_string_invalid".into()),
    }
}
fn number(m: &Mapping, k: &str, min: u64, max: u64, default: Option<u64>) -> LocalResult<u64> {
    match get(m, k) {
        None => default.ok_or_else(|| "yaml_number_required".into()),
        Some(v) => v
            .as_u64()
            .filter(|n| *n >= min && *n <= max)
            .ok_or_else(|| "yaml_number_invalid".into()),
    }
}
fn boolean(m: &Mapping, k: &str) -> LocalResult<()> {
    if let Some(v) = get(m, k) {
        if !v.is_bool() {
            return Err("yaml_boolean_invalid".into());
        }
    }
    Ok(())
}
fn sequence<'a>(m: &'a Mapping, k: &str) -> LocalResult<&'a [Value]> {
    match get(m, k) {
        None => Ok(&[]),
        Some(Value::Sequence(s)) => Ok(s),
        _ => Err("yaml_array_required".into()),
    }
}
fn unknown(m: &Mapping, keys: &[&str], path: &str, summary: &mut MigrationSummary) {
    for (i, k) in m.keys().enumerate() {
        if !keys.contains(&k.as_str().unwrap_or("")) {
            summary.diagnostic(
                "yaml_unknown_field_not_converted",
                &format!("{path}.field[{i}]"),
            );
        }
    }
}
fn project(m: &Mapping, keys: &[&str]) -> serde_json::Value {
    let mut out = serde_json::Map::new();
    for key in keys {
        if let Some(v) = get(m, key) {
            out.insert(
                (*key).into(),
                serde_json::to_value(v).unwrap_or(serde_json::Value::Null),
            );
        }
    }
    serde_json::Value::Object(out)
}
fn assign(ids: &mut BTreeMap<String, String>, path: &str) -> String {
    let v = id();
    ids.insert(path.into(), v.clone());
    v
}
struct ReadSource {
    info: SourceInfo,
    text: String,
    stamp: Option<Metadata>,
    path: PathBuf,
}
fn same(a: &Metadata, b: &Metadata) -> bool {
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        a.dev() == b.dev()
            && a.ino() == b.ino()
            && a.size() == b.size()
            && a.mtime() == b.mtime()
            && a.mtime_nsec() == b.mtime_nsec()
            && a.ctime() == b.ctime()
            && a.ctime_nsec() == b.ctime_nsec()
    }
    #[cfg(not(unix))]
    {
        a.len() == b.len()
            && a.modified().ok() == b.modified().ok()
            && a.created().ok() == b.created().ok()
    }
}
fn no_symlinks(p: &Path) -> LocalResult<()> {
    for a in p.ancestors() {
        if a.is_symlink() {
            return Err("yaml_symlink".into());
        }
    }
    Ok(())
}
fn read(path: &Path, kind: &str, origin: &str) -> Result<ReadSource, (SourceInfo, String)> {
    let mut info = SourceInfo {
        kind: kind.into(),
        path: path.to_string_lossy().into(),
        origin: origin.into(),
        bytes: None,
        sha256: None,
        hash_unavailable: None,
    };
    let result = (|| -> LocalResult<(String, Option<Metadata>)> {
        if path.to_string_lossy().contains("://") {
            return Err("yaml_locator_invalid".into());
        }
        no_symlinks(path)?;
        let before = match fs::symlink_metadata(path) {
            Ok(m) => m,
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok((String::new(), None)),
            Err(_) => return Err("yaml_read_failed".into()),
        };
        info.bytes = Some(before.len());
        if !before.is_file() {
            return Err("yaml_regular_file_required".into());
        }
        if before.len() > SOURCE_LIMIT as u64 {
            info.hash_unavailable = Some("source_limit".into());
            return Err("yaml_source_limit".into());
        }
        let mut f = File::open(path).map_err(|_| "yaml_read_failed")?;
        let opened = f.metadata().map_err(|_| "yaml_read_failed")?;
        if !same(&before, &opened) {
            return Err("yaml_source_changed".into());
        }
        let mut bytes = vec![];
        f.by_ref()
            .take((SOURCE_LIMIT + 1) as u64)
            .read_to_end(&mut bytes)
            .map_err(|_| "yaml_read_failed")?;
        if bytes.len() > SOURCE_LIMIT {
            info.hash_unavailable = Some("source_limit".into());
            return Err("yaml_source_limit".into());
        }
        let after = fs::symlink_metadata(path).map_err(|_| "yaml_source_changed")?;
        if !same(&before, &after)
            || !same(&before, &f.metadata().map_err(|_| "yaml_source_changed")?)
        {
            return Err("yaml_source_changed".into());
        }
        let text = String::from_utf8(bytes).map_err(|_| "yaml_utf8_required")?;
        info.sha256 = Some(digest(&text));
        Ok((text, Some(before)))
    })();
    match result {
        Ok((text, stamp)) => Ok(ReadSource {
            info,
            text,
            stamp,
            path: path.into(),
        }),
        Err(e) => Err((info, e)),
    }
}
fn unchanged(s: &ReadSource) -> LocalResult<()> {
    no_symlinks(&s.path)?;
    match (&s.stamp, fs::symlink_metadata(&s.path)) {
        (None, Err(e)) if e.kind() == std::io::ErrorKind::NotFound => Ok(()),
        (Some(a), Ok(b)) if same(a, &b) => Ok(()),
        _ => Err("yaml_source_changed".into()),
    }
}

pub(crate) fn discover(paths: &MigrationPaths) -> Candidate {
    let mut candidate = Candidate {
        configuration: Configuration::default(),
        receipt: Receipt {
            yaml_migration_version: 1,
            summary: MigrationSummary::state("failed"),
            archive: serde_json::json!({}),
            ids: BTreeMap::new(),
        },
    };
    candidate.receipt.summary.attempt_id = Some(id());
    let result = (|| -> LocalResult<()> {
        let mut sources = vec![];
        for (p, k, o) in [
            (&paths.points, "points", &paths.points_origin),
            (&paths.policy, "policy", &paths.policy_origin),
        ] {
            match read(p, k, o) {
                Ok(s) => {
                    candidate.receipt.summary.sources.push(s.info.clone());
                    sources.push(s)
                }
                Err((i, e)) => {
                    candidate.receipt.summary.sources.push(i);
                    return Err(e);
                }
            }
        }
        let points = parse(&sources[0].text)?;
        let policy = parse(&sources[1].text)?;
        convert(&points, &policy, &mut candidate)?;
        // The pair must represent the same discovery interval, including missing-source facts.
        for s in &sources {
            unchanged(s)?;
        }
        Ok(())
    })();
    if let Err(e) = result {
        candidate.configuration = Configuration::default();
        candidate.receipt.archive = serde_json::json!({});
        candidate.receipt.ids.clear();
        candidate.receipt.summary.status = "failed".into();
        candidate.receipt.summary.error_code = Some(e.clone());
        candidate.receipt.summary.diagnostic(&e, "sources");
    }
    candidate.receipt.summary.retry_allowed = retryable(&candidate.receipt.summary.status);
    candidate
}
fn convert(points: &Value, policy: &Value, out: &mut Candidate) -> LocalResult<()> {
    let mut archive = serde_json::Map::new();
    let c = &mut out.configuration;
    let r = &mut out.receipt;
    if !empty(points) {
        let plcs = mapping(points)?;
        r.summary.counts.plcs = plcs.len();
        if plcs.len() > 4 {
            return Err("yaml_plc_limit".into());
        }
        let mut archived = serde_json::Map::new();
        let mut endpoints = BTreeSet::new();
        for (pi, (key, value)) in plcs.iter().enumerate() {
            let key = key
                .as_str()
                .filter(|s| !s.is_empty() && s.len() <= 100)
                .ok_or("yaml_plc_key_invalid")?;
            let path = format!("plcs[{pi}]");
            let m = mapping(value)?;
            unknown(
                m,
                &[
                    "ip",
                    "port",
                    "rack",
                    "slot",
                    "point_count",
                    "groups",
                    "enabled",
                ],
                &path,
                &mut r.summary,
            );
            boolean(m, "enabled")?;
            let host = string(m, "ip", 100, false)?.unwrap_or_default();
            if host.parse::<std::net::Ipv4Addr>().is_err() {
                r.summary.diagnostic("yaml_address_requires_review", &path);
            }
            for k in ["port", "rack", "slot"] {
                if get(m, k).is_none() {
                    r.summary
                        .diagnostic("yaml_default_requires_review", &format!("{path}.{k}"));
                }
            }
            let plc = Plc {
                id: assign(&mut r.ids, &path),
                name: key.into(),
                enabled: false,
                host,
                port: number(m, "port", 1, 65535, Some(102))? as u16,
                rack: number(m, "rack", 0, 7, Some(0))? as u8,
                slot: number(m, "slot", 0, 31, Some(1))? as u8,
                connect_timeout_ms: 1000,
                io_timeout_ms: 500,
                deadline_ms: 5000,
            };
            if !plc.host.is_empty() && !endpoints.insert(plc.endpoint()) {
                return Err("yaml_duplicate_endpoint".into());
            }
            let source_id = assign(&mut r.ids, &format!("{path}.source"));
            let mut source = project(m, &["ip", "port", "rack", "slot", "point_count", "enabled"]);
            let mut ag = vec![];
            let gs = sequence(m, "groups")?;
            if gs.len() > 8 {
                return Err("yaml_group_limit".into());
            }
            let mut names = BTreeSet::new();
            let mut dbs: BTreeMap<u16, String> = BTreeMap::new();
            let mut plc_points = 0;
            let mut semantic_points = BTreeSet::new();
            for (gi, g) in gs.iter().enumerate() {
                let gp = format!("{path}.groups[{gi}]");
                let g = mapping(g)?;
                unknown(
                    g,
                    &[
                        "name",
                        "db_number",
                        "start",
                        "size",
                        "point_count",
                        "points",
                        "enabled",
                    ],
                    &gp,
                    &mut r.summary,
                );
                boolean(g, "enabled")?;
                let name = string(g, "name", 100, true)?.unwrap();
                let num = number(g, "db_number", 1, 65535, None)? as u16;
                if !names.insert((name.clone(), num)) {
                    return Err("yaml_duplicate_group".into());
                }
                let start = number(g, "start", 0, 65535, None)? as u32;
                let size = number(g, "size", 1, 65536, None)? as u32;
                if start + size > 65536 {
                    return Err("yaml_window_invalid".into());
                }
                let gid = assign(&mut r.ids, &gp);
                c.groups.push(Group {
                    id: gid.clone(),
                    plc_id: plc.id.clone(),
                    name,
                    enabled: false,
                    interval_ms: 1000,
                });
                r.summary.counts.groups += 1;
                let dbid = if let Some(db) = dbs.get(&num) {
                    db.clone()
                } else {
                    let db = assign(&mut r.ids, &format!("{path}.db[{num}]"));
                    dbs.insert(num, db.clone());
                    c.dbs.push(Db {
                        id: db.clone(),
                        plc_id: plc.id.clone(),
                        source_id: source_id.clone(),
                        name: format!("LegacyDB{num}"),
                        number: num,
                        length: 1,
                        complete: false,
                        flat: false,
                        tree: vec![],
                        import_binding: None,
                    });
                    db
                };
                if dbs.len() > 32 {
                    return Err("yaml_db_limit".into());
                }
                let ps = sequence(g, "points")?;
                let mut point_names = BTreeSet::new();
                let mut aps = vec![];
                for (pni, p) in ps.iter().enumerate() {
                    let pp = format!("{gp}.points[{pni}]");
                    let p = mapping(p)?;
                    unknown(
                        p,
                        &[
                            "name",
                            "source_name",
                            "type",
                            "offset",
                            "bit",
                            "length",
                            "desc",
                            "readable",
                            "writable",
                            "enabled",
                            "tia_accessible",
                            "tia_writable",
                        ],
                        &pp,
                        &mut r.summary,
                    );
                    for k in [
                        "readable",
                        "writable",
                        "enabled",
                        "tia_accessible",
                        "tia_writable",
                    ] {
                        boolean(p, k)?;
                    }
                    let name = string(p, "name", 100, true)?.unwrap();
                    if !point_names.insert(name.clone()) {
                        return Err("yaml_duplicate_point".into());
                    }
                    string(p, "source_name", 500, false)?;
                    let typ = string(p, "type", 100, true)?.unwrap();
                    let typ = typ.to_ascii_uppercase();
                    let len = if get(p, "length").is_some() {
                        Some(number(p, "length", 1, 65536, None)?)
                    } else {
                        None
                    };
                    let data_type = if typ == "STRING" {
                        match len {
                            Some(n) if n >= 3 && n <= 256 => format!("STRING[{}]", n - 2),
                            _ => typ,
                        }
                    } else {
                        typ
                    };
                    if width(&data_type).is_none() {
                        r.summary.diagnostic("yaml_unsupported_type_preserved", &pp);
                    }
                    let offset = number(p, "offset", 0, 65535, None)? as u32;
                    let bit = if get(p, "bit").is_some() {
                        Some(number(p, "bit", 0, 7, None)? as u8)
                    } else {
                        None
                    };
                    if (data_type == "BOOL" && bit.is_none())
                        || (data_type != "BOOL" && bit.is_some())
                    {
                        return Err("yaml_bit_invalid".into());
                    }
                    if !semantic_points.insert((
                        num,
                        name.clone(),
                        data_type.clone(),
                        offset,
                        bit,
                        len,
                    )) {
                        return Err("yaml_duplicate_semantic_point".into());
                    }
                    let w = width(&data_type).unwrap_or(len.unwrap_or(1) as u32);
                    if offset.checked_add(w).filter(|e| *e <= 65536).is_none() {
                        return Err("yaml_offset_invalid".into());
                    }
                    if offset < start || offset + w > start + size {
                        r.summary.diagnostic("yaml_window_mismatch", &pp);
                    }
                    c.points.push(Point {
                        id: assign(&mut r.ids, &pp),
                        plc_id: plc.id.clone(),
                        db_id: dbid.clone(),
                        source_path: format!("legacy/{gi}/{pni}/{name}"),
                        name,
                        data_type,
                        comment: string(p, "desc", 500, false)?.unwrap_or_default(),
                        enabled: false,
                        group_id: Some(gid.clone()),
                        address: Some(Address {
                            offset,
                            bit,
                            confirmed: false,
                            origin: "legacy_yaml".into(),
                            reason: "legacy_source_requires_review".into(),
                        }),
                    });
                    let db = c.dbs.iter_mut().find(|d| d.id == dbid).unwrap();
                    db.length = db.length.max(offset + w);
                    aps.push(project(
                        p,
                        &[
                            "name",
                            "source_name",
                            "type",
                            "offset",
                            "bit",
                            "length",
                            "desc",
                            "readable",
                            "writable",
                            "enabled",
                            "tia_accessible",
                            "tia_writable",
                        ],
                    ));
                }
                plc_points += ps.len();
                r.summary.counts.points += ps.len();
                if plc_points > 4096 {
                    return Err("yaml_point_limit".into());
                }
                if get(g, "point_count").is_some()
                    && number(g, "point_count", 0, u32::MAX as u64, None)? != ps.len() as u64
                {
                    r.summary.diagnostic("yaml_count_mismatch", &gp);
                }
                let mut a = project(
                    g,
                    &[
                        "name",
                        "db_number",
                        "start",
                        "size",
                        "point_count",
                        "enabled",
                    ],
                );
                a["points"] = aps.into();
                ag.push(a);
            }
            if get(m, "point_count").is_some()
                && number(m, "point_count", 0, u32::MAX as u64, None)? != plc_points as u64
            {
                r.summary.diagnostic("yaml_count_mismatch", &path);
            }
            r.summary.diagnostic("legacy_source_requires_review", &path);
            source["groups"] = ag.into();
            source["legacyPlcKey"] = key.into();
            source["originalSha256"] =
                serde_json::to_value(r.summary.sources.first().and_then(|s| s.sha256.clone()))
                    .unwrap();
            let content = encode(&source)?;
            if content.len() > SOURCE_LIMIT {
                return Err("yaml_projection_limit".into());
            }
            c.sources.push(SourceDocument {
                id: source_id,
                name: format!("legacy-{pi}.yaml"),
                sha256: digest(&content),
                content,
                plc_id: plc.id.clone(),
                db_number: None,
                diagnostics: vec![issue("legacy_source_requires_review", &path)],
                lineage_id: None,
            });
            archived.insert(key.into(), source);
            c.plcs.push(plc);
        }
        r.summary.counts.dbs = c.dbs.len();
        archive.insert("points".into(), archived.into());
    }
    if !empty(policy) {
        let root = mapping(policy)?;
        r.summary.counts.policy_plcs = root.len();
        if root.len() > 4 {
            return Err("yaml_policy_limit".into());
        }
        let mut archived = serde_json::Map::new();
        for (pi, (key, v)) in root.iter().enumerate() {
            let key = key
                .as_str()
                .filter(|s| !s.is_empty() && s.len() <= 100)
                .ok_or("yaml_policy_key")?;
            let m = mapping(v)?;
            let path = format!("policy[{pi}]");
            unknown(
                m,
                &["snapshot_policy_version", "groups"],
                &path,
                &mut r.summary,
            );
            number(m, "snapshot_policy_version", 2, 2, None)?;
            let gs = sequence(m, "groups")?;
            if gs.len() > 8 {
                return Err("yaml_policy_limit".into());
            }
            let mut ag = vec![];
            let mut seen = BTreeSet::new();
            for (gi, g) in gs.iter().enumerate() {
                let gp = format!("{path}.groups[{gi}]");
                let m = mapping(g)?;
                unknown(
                    m,
                    &["name", "group_name", "db_number", "points"],
                    &gp,
                    &mut r.summary,
                );
                let n = string(m, "name", 100, false)?;
                let alias = string(m, "group_name", 100, false)?;
                if n.is_some() && alias.is_some() && n != alias {
                    return Err("yaml_policy_group_ambiguous".into());
                }
                let name = n.or(alias).ok_or("yaml_policy_group_required")?;
                let db = number(m, "db_number", 1, 65535, None)?;
                if !seen.insert((name.clone(), db)) {
                    return Err("yaml_policy_group_duplicate".into());
                }
                let mut aps = vec![];
                let mut names = BTreeSet::new();
                for (ni, p) in sequence(m, "points")?.iter().enumerate() {
                    let pp = format!("{gp}.points[{ni}]");
                    let m = mapping(p)?;
                    unknown(
                        m,
                        &["name", "raw_enabled", "raw_policy", "latest_enabled"],
                        &pp,
                        &mut r.summary,
                    );
                    let name = string(m, "name", 100, true)?.unwrap();
                    if !names.insert(name.clone()) {
                        return Err("yaml_policy_point_duplicate".into());
                    }
                    for k in ["raw_enabled", "latest_enabled"] {
                        boolean(m, k)?;
                        if get(m, k).is_none() {
                            r.summary
                                .diagnostic("yaml_policy_missing_legacy_fields", &pp);
                        }
                    }
                    if let Some(rp) = string(m, "raw_policy", 30, false)? {
                        if !["every_sample", "on_change", "hourly"].contains(&rp.as_str()) {
                            return Err("yaml_policy_invalid".into());
                        }
                    } else {
                        r.summary
                            .diagnostic("yaml_policy_missing_legacy_fields", &pp);
                    }
                    let group_name = string(mapping(g)?, "name", 100, false)?
                        .or(string(mapping(g)?, "group_name", 100, false)?)
                        .unwrap();
                    let exact = c
                        .plcs
                        .iter()
                        .find(|p| p.name == key)
                        .map(|plc| {
                            c.points
                                .iter()
                                .filter(|p| {
                                    p.plc_id == plc.id
                                        && p.name == name
                                        && c.dbs
                                            .iter()
                                            .any(|d| d.id == p.db_id && d.number == db as u16)
                                        && c.groups.iter().any(|g| {
                                            Some(&g.id) == p.group_id.as_ref()
                                                && g.name == group_name
                                        })
                                })
                                .count()
                        })
                        .unwrap_or(0);
                    if exact > 1 {
                        return Err("yaml_policy_mapping_ambiguous".into());
                    }
                    let mut a =
                        project(m, &["name", "raw_enabled", "raw_policy", "latest_enabled"]);
                    a["match"] = if exact == 1 { "matched" } else { "unmatched" }.into();
                    if exact == 0 {
                        r.summary.diagnostic("yaml_policy_unmatched", &pp);
                    }
                    aps.push(a);
                    r.summary.counts.policy_points += 1;
                    if r.summary.counts.policy_points > 16384 {
                        return Err("yaml_policy_limit".into());
                    }
                }
                let mut a = project(m, &["name", "group_name", "db_number"]);
                a["points"] = aps.into();
                ag.push(a);
                r.summary.counts.policy_groups += 1;
            }
            archived.insert(
                key.into(),
                serde_json::json!({"snapshot_policy_version":2,"groups":ag}),
            );
        }
        archive.insert("retiredPolicy".into(), archived.into());
        r.summary.diagnostic("yaml_policy_archived_only", "policy");
    }
    r.archive = archive.into();
    r.summary.status = if !c.plcs.is_empty() {
        if r.summary.diagnostic_total > 0 {
            "imported_with_diagnostics"
        } else {
            "imported"
        }
    } else if !empty(policy) {
        "archived_policy_only"
    } else {
        "skipped_empty"
    }
    .into();
    if encode(c)?.len() > 16 * 1024 * 1024 || encode(r)?.len() > RECEIPT_LIMIT {
        return Err("yaml_receipt_limit".into());
    }
    Ok(())
}
#[cfg(test)]
#[path = "yaml_migration_tests.rs"]
pub(crate) mod tests;
