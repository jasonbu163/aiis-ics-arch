//! TIA有界词法、逐声明安全分界及完整树展开；不执行初值。
use crate::domain::local_configuration::*;
use std::collections::{BTreeMap, BTreeSet};
#[derive(Clone, Debug)]
pub(super) struct Token {
    value: String,
    line: usize,
    quoted: bool,
}
#[derive(Clone, Debug)]
pub(super) enum Type {
    Scalar(String),
    Reference(String),
    Struct(Vec<Field>),
    Array(i32, i32, Box<Type>),
}
#[derive(Clone, Debug)]
pub(super) struct Field {
    pub(super) name: String,
    kind: Type,
    line: usize,
    file: String,
    comment: String,
}
#[derive(Clone)]
pub(super) struct Block {
    pub(super) fields: Vec<Field>,
    pub(super) source: SourceDocument,
    pub(super) standard: bool,
}
pub(super) struct Parser {
    tokens: Vec<Token>,
    at: usize,
    file: String,
    path: Vec<String>,
    nesting: usize,
}
impl Parser {
    fn peek(&self, s: &str) -> bool {
        self.tokens
            .get(self.at)
            .map(|t| t.value.eq_ignore_ascii_case(s))
            .unwrap_or(false)
    }
    fn take(&mut self) -> LocalResult<Token> {
        let t = self.tokens.get(self.at).cloned().ok_or_else(|| {
            format!(
                "source_syntax:{}:{}",
                self.file,
                self.tokens.last().map(|t| t.line).unwrap_or(1)
            )
        })?;
        self.at += 1;
        Ok(t)
    }
    fn expect(&mut self, s: &str) -> LocalResult<()> {
        if !self.peek(s) {
            return Err(format!(
                "source_syntax:{}:{}:expected_{s}",
                self.file,
                self.tokens.get(self.at).map(|t| t.line).unwrap_or(1)
            ));
        }
        self.at += 1;
        Ok(())
    }
    fn kind(&mut self, in_array: bool) -> LocalResult<Type> {
        if self.peek("STRUCT") {
            if self.nesting >= 8 {
                return Err("expansion_depth".into());
            }
            self.at += 1;
            self.nesting += 1;
            let fields = self.fields("END_STRUCT")?;
            self.nesting -= 1;
            self.expect("END_STRUCT")?;
            return Ok(Type::Struct(fields));
        }
        if self.peek("ARRAY") {
            if in_array {
                return Err("nested_array".into());
            }
            self.at += 1;
            self.expect("[")?;
            let lo = self
                .take()?
                .value
                .parse::<i32>()
                .map_err(|_| "array_bounds")?;
            self.expect("..")?;
            let hi = self
                .take()?
                .value
                .parse::<i32>()
                .map_err(|_| "array_bounds")?;
            self.expect("]")?;
            self.expect("OF")?;
            if hi < lo || i64::from(hi) - i64::from(lo) + 1 > 1024 {
                return Err("array_limits".into());
            }
            let kind = self.kind(true)?;
            return Ok(Type::Array(lo, hi, Box::new(kind)));
        }
        let v = self.take()?.value;
        let u = v.to_ascii_uppercase();
        if u == "STRING" {
            self.expect("[")?;
            let n = self
                .take()?
                .value
                .parse::<u32>()
                .map_err(|_| "string_length")?;
            self.expect("]")?;
            let name = format!("STRING[{n}]");
            if width(&name).is_none() {
                return Err("string_length".into());
            }
            return Ok(Type::Scalar(name));
        }
        if width(&u).is_some() {
            return Ok(Type::Scalar(u));
        }
        if [
            "AT", "POINTER", "ANY", "VARIANT", "TIME", "DATE", "LREAL", "LINT", "ULINT", "WSTRING",
            "WCHAR", "S5TIME",
        ]
        .contains(&u.as_str())
            || u.starts_with("FB")
        {
            return Err(format!("unsupported_type:{u}"));
        }
        Ok(Type::Reference(v))
    }
    fn fields(&mut self, end: &str) -> LocalResult<Vec<Field>> {
        let mut out = vec![];
        let mut names = BTreeSet::new();
        while !self.peek(end) {
            let t = self.take()?;
            if t.value.starts_with("//") {
                continue;
            }
            if out.len() >= 4096
                || t.value.is_empty()
                || !names.insert(t.value.to_ascii_lowercase())
            {
                return Err("duplicate_or_excess_fields".into());
            }
            if self.peek("{") {
                self.at += 1;
                self.expect("S7_SetPoint")?;
                self.expect(":=")?;
                let v = self.take()?.value;
                if !v.eq_ignore_ascii_case("false") && !v.eq_ignore_ascii_case("true") {
                    return Err("field_attribute_value".into());
                }
                self.expect("}")?;
            }
            self.expect(":")?;
            self.path.push(t.value.clone());
            let kind = self.kind(false).map_err(|e| {
                if e.contains(":path=") {
                    e
                } else {
                    format!(
                        "{}:line={}:path={}",
                        e.split(':').next().unwrap_or("source_syntax"),
                        self.tokens.get(self.at).map(|t| t.line).unwrap_or(t.line),
                        self.path.join(".")
                    )
                }
            })?;
            self.path.pop();
            if self.peek(":=") {
                self.at += 1;
                while !self.peek(";") {
                    let init = self.take()?;
                    if init.value.eq_ignore_ascii_case(end) {
                        return Err("source_syntax".into());
                    }
                }
            }
            self.expect(";")?;
            let comment = if self
                .tokens
                .get(self.at)
                .map(|t| t.value.starts_with("//"))
                .unwrap_or(false)
            {
                self.take()?.value[2..].trim().into()
            } else {
                String::new()
            };
            out.push(Field {
                name: t.value,
                kind,
                line: t.line,
                file: self.file.clone(),
                comment,
            })
        }
        Ok(out)
    }
    fn blocks(&mut self, src: &SourceDocument) -> LocalResult<Vec<Block>> {
        let mut out = vec![];
        while self.at < self.tokens.len() {
            if self.peek(";") {
                self.at += 1;
                continue;
            }
            if self.tokens[self.at].value.starts_with("//") {
                self.at += 1;
                continue;
            }
            let db = self.peek("DATA_BLOCK");
            if !db && !self.peek("TYPE") {
                return Err(format!(
                    "source_syntax:{}:{}",
                    self.file, self.tokens[self.at].line
                ));
            }
            self.at += 1;
            let name = self.take()?;
            if !name.quoted && name.value.parse::<u32>().is_ok() {
                return Err("numeric_db_declaration".into());
            }
            let name = name.value;
            self.path.push(name.clone());
            let mut standard = !db;
            while !self.peek("STRUCT") && !self.peek("VAR") {
                if self.peek("{") {
                    self.at += 1;
                    self.expect("S7_Optimized_Access")?;
                    self.expect(":=")?;
                    let opt = self.take()?.value;
                    standard = opt.eq_ignore_ascii_case("FALSE");
                    self.expect("}")?;
                    if !standard {
                        return Err("optimized_access".into());
                    }
                } else if self.peek("NON_RETAIN") || self.peek("RETAIN") {
                    self.at += 1;
                } else if self
                    .tokens
                    .get(self.at)
                    .map(|t| t.value.starts_with("//"))
                    .unwrap_or(false)
                {
                    self.at += 1;
                } else if self.peek("VERSION") {
                    self.at += 1;
                    self.expect(":")?;
                    let v = self.take()?.value;
                    if v.parse::<f64>().is_err() {
                        return Err("source_version".into());
                    }
                } else if !db && self.peek(":") {
                    self.at += 1;
                } else {
                    return Err(format!(
                        "unsupported_header:{}:{}",
                        self.file,
                        self.tokens.get(self.at).map(|t| t.line).unwrap_or(1)
                    ));
                }
            }
            let var = self.peek("VAR");
            self.at += 1;
            let end = if var { "END_VAR" } else { "END_STRUCT" };
            let fields = self.fields(end)?;
            self.expect(end)?;
            if self.peek(";") {
                self.at += 1;
            }
            if db {
                if !standard {
                    return Err("optimized_access_unknown".into());
                }
                self.expect("BEGIN")?;
                while !self.peek("END_DATA_BLOCK") {
                    self.take()?;
                }
                self.expect("END_DATA_BLOCK")?;
            } else {
                self.expect("END_TYPE")?;
            }
            if self.peek(";") {
                self.at += 1;
            }
            out.push(Block {
                fields,
                source: src.clone(),
                standard,
            });
            self.path.pop();
        }
        Ok(out)
    }
}
fn lex(text: &str) -> LocalResult<Vec<Token>> {
    let mut chars = text.trim_start_matches('\u{feff}').chars().peekable();
    let mut line = 1;
    let mut out = vec![];
    while let Some(c) = chars.next() {
        if c == '\n' {
            line += 1;
            continue;
        }
        if c.is_whitespace() {
            continue;
        }
        let start = line;
        if c == '/' && chars.peek() == Some(&'/') {
            chars.next();
            let mut s = String::from("//");
            while let Some(c) = chars.peek() {
                if *c == '\n' {
                    break;
                }
                s.push(chars.next().unwrap())
            }
            out.push(Token {
                value: s,
                line: start,
                quoted: false,
            });
            continue;
        }
        if c == '(' && chars.peek() == Some(&'*') {
            chars.next();
            let mut closed = false;
            while let Some(c) = chars.next() {
                if c == '\n' {
                    line += 1
                }
                if c == '*' && chars.peek() == Some(&')') {
                    chars.next();
                    closed = true;
                    break;
                }
            }
            if !closed {
                return Err("unterminated_comment".into());
            }
            continue;
        }
        let mut s = String::new();
        if c == '"' || c == '\'' {
            let quote = c;
            let mut closed = false;
            while let Some(c) = chars.next() {
                if c == quote {
                    closed = true;
                    break;
                }
                if c == '\n' {
                    return Err("unterminated_string".into());
                }
                s.push(c)
            }
            if !closed {
                return Err("unterminated_string".into());
            }
        } else if c.is_alphanumeric() || c == '_' || c == '-' {
            s.push(c);
            while let Some(c) = chars.peek() {
                if c.is_alphanumeric() || *c == '_' {
                    s.push(chars.next().unwrap())
                } else if *c == '.' {
                    let mut copy = chars.clone();
                    copy.next();
                    if copy.peek().map(|c| c.is_ascii_digit()).unwrap_or(false) {
                        s.push(chars.next().unwrap())
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            }
        } else if c == '.' && chars.peek() == Some(&'.') {
            chars.next();
            s = "..".into()
        } else if c == ':' && chars.peek() == Some(&'=') {
            chars.next();
            s = ":=".into()
        } else if "[]{}:;,.".contains(c) {
            s.push(c)
        } else {
            return Err(format!("source_character:{line}"));
        }
        out.push(Token {
            value: s,
            line: start,
            quoted: c == '"' || c == '\'',
        });
        if out.len() > 100000 {
            return Err("source_limits".into());
        }
    }
    Ok(out)
}
pub(super) fn expand(
    fields: &[Field],
    prefix: &str,
    udts: &BTreeMap<String, Vec<Field>>,
    stack: &mut Vec<String>,
    depth: usize,
    in_array: bool,
    leaves: &mut Vec<(String, String, usize, String)>,
) -> Result<Vec<FieldNode>, Issue> {
    let mut out = vec![];
    for f in fields {
        let path = if prefix.is_empty() {
            f.name.clone()
        } else {
            format!("{prefix}.{}", f.name)
        };
        out.push(expand_kind(
            &f.kind, &f.name, &path, f.line, &f.file, &f.comment, udts, stack, depth, in_array,
            leaves,
        )?)
    }
    Ok(out)
}
fn expand_kind(
    t: &Type,
    name: &str,
    path: &str,
    line: usize,
    file: &str,
    comment: &str,
    udts: &BTreeMap<String, Vec<Field>>,
    stack: &mut Vec<String>,
    depth: usize,
    in_array: bool,
    leaves: &mut Vec<(String, String, usize, String)>,
) -> Result<FieldNode, Issue> {
    let failure = |code: &str| Issue {
        code: code.into(),
        path: path.into(),
        line,
        file: file.into(),
    };
    if depth > 8 || (depth == 8 && !matches!(t, Type::Scalar(_))) {
        return Err(failure("expansion_depth"));
    }
    let node_type;
    let (mut children, mut lower, mut upper) = (vec![], None, None);
    match t {
        Type::Scalar(t) => {
            node_type = t.clone();
            leaves.push((path.into(), t.clone(), line, comment.into()));
            if leaves.len() > 4096 {
                return Err(failure("leaf_limits"));
            }
        }
        Type::Struct(fs) => {
            node_type = "STRUCT".into();
            children = expand(fs, path, udts, stack, depth + 1, in_array, leaves)?
        }
        Type::Reference(r) => {
            if stack.contains(&r.to_ascii_lowercase()) {
                return Err(failure("udt_cycle"));
            }
            let fs = udts
                .get(&r.to_ascii_lowercase())
                .ok_or_else(|| failure("udt_missing"))?;
            stack.push(r.to_ascii_lowercase());
            node_type = r.clone();
            children = expand(fs, path, udts, stack, depth + 1, in_array, leaves)?;
            stack.pop();
        }
        Type::Array(lo, hi, kind) => {
            if in_array {
                return Err(failure("nested_array"));
            }
            node_type = "ARRAY".into();
            lower = Some(*lo);
            upper = Some(*hi);
            for n in *lo..=*hi {
                let p = format!("{path}[{n}]");
                children.push(expand_kind(
                    kind,
                    &format!("[{n}]"),
                    &p,
                    line,
                    file,
                    comment,
                    udts,
                    stack,
                    depth + 1,
                    true,
                    leaves,
                )?)
            }
        }
    }
    Ok(FieldNode {
        name: name.into(),
        path: path.into(),
        data_type: node_type,
        line,
        comment: comment.into(),
        lower,
        upper,
        children,
    })
}
#[derive(Clone)]
pub(super) struct Declaration {
    pub source: SourceDocument,
    pub name: String,
    pub db: bool,
    pub line: usize,
    pub block: Option<Block>,
    pub issues: Vec<Issue>,
}
pub(super) fn scan(src: &SourceDocument) -> LocalResult<Vec<Declaration>> {
    let tokens = lex(&src.content)?;
    let mut at = 0;
    let mut out = vec![];
    while at < tokens.len() {
        if tokens[at].value.starts_with("//") || tokens[at].value == ";" {
            at += 1;
            continue;
        }
        let db = tokens[at].value.eq_ignore_ascii_case("DATA_BLOCK") && !tokens[at].quoted;
        if !db && !(tokens[at].value.eq_ignore_ascii_case("TYPE") && !tokens[at].quoted) {
            return Err(format!("source_boundary:{}:{}", src.name, tokens[at].line));
        }
        let start = at;
        let name = tokens.get(at + 1).ok_or("source_boundary")?.value.clone();
        let line = tokens[at].line;
        at += 2;
        let end = if db { "END_DATA_BLOCK" } else { "END_TYPE" };
        while at < tokens.len()
            && !(tokens[at].value.eq_ignore_ascii_case(end) && !tokens[at].quoted)
        {
            if !tokens[at].quoted
                && ["DATA_BLOCK", "TYPE", "END_DATA_BLOCK", "END_TYPE"]
                    .iter()
                    .any(|v| tokens[at].value.eq_ignore_ascii_case(v))
            {
                return Err(format!("source_boundary:{}:{}", src.name, tokens[at].line));
            }
            at += 1;
        }
        if at == tokens.len() {
            return Err(format!("source_boundary:{}:{}", src.name, line));
        }
        at += 1;
        let mut parser = Parser {
            tokens: tokens[start..at].to_vec(),
            at: 0,
            file: src.name.clone(),
            path: vec![],
            nesting: 0,
        };
        let result = parser.blocks(src);
        let (block, issues) = match result {
            Ok(mut v) if v.len() == 1 => (v.pop(), vec![]),
            Ok(_) => return Err("source_boundary".into()),
            Err(e) => (
                None,
                vec![Issue {
                    code: e.split(':').next().unwrap_or("source_syntax").into(),
                    file: src.name.clone(),
                    line: parser.tokens.get(parser.at).map(|t| t.line).unwrap_or(line),
                    path: parser.path.join("."),
                }],
            ),
        };
        out.push(Declaration {
            source: src.clone(),
            name,
            db,
            line,
            block,
            issues,
        });
        if out.len() > 4096 {
            return Err("source_limits".into());
        }
    }
    if out.is_empty() {
        return Err("source_empty".into());
    }
    Ok(out)
}
pub(super) fn referenced(fields: &[Field], names: &mut BTreeSet<String>) {
    fn kind(t: &Type, names: &mut BTreeSet<String>) {
        match t {
            Type::Reference(r) => {
                names.insert(r.to_ascii_lowercase());
            }
            Type::Struct(fs) => referenced(fs, names),
            Type::Array(_, _, t) => kind(t, names),
            _ => {}
        }
    }
    for f in fields {
        kind(&f.kind, names);
    }
}
