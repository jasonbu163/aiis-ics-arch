//! 无I/O纯值对象：输入对应键、声明、完整树、结构化段和定位诊断。
pub type LocalResult<T> = Result<T, String>;
#[derive(Clone, Debug, PartialEq)]
pub struct SourceDocument {
    pub name: String,
    pub content: String,
}
#[derive(Clone, Debug, PartialEq)]
pub struct FieldNode {
    pub name: String,
    pub path: String,
    pub data_type: String,
    pub line: usize,
    pub comment: String,
    pub lower: Option<i32>,
    pub upper: Option<i32>,
    pub children: Vec<FieldNode>,
}
#[derive(Clone, Debug, PartialEq)]
pub struct Diagnostic {
    pub code: String,
    pub path: String,
    pub line: usize,
    pub file: String,
}
pub type Issue = Diagnostic;
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum PathSegment {
    Field(String),
    Index(i32),
}
#[derive(Clone, Debug)]
pub struct SourceInput {
    pub input_id: String,
    pub name: String,
    pub bytes: Vec<u8>,
}
#[derive(Clone, Copy, Debug)]
pub enum ImportProfile {
    TiaSubsetV1,
}
#[derive(Clone, Copy, Debug)]
pub enum LayoutProfile {
    SiemensStep7V20StandardWordV1,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DeclarationRef {
    pub input_id: String,
    pub declaration_index: usize,
}
#[derive(Clone)]
pub struct SourceCatalog {
    pub declarations: Vec<(DeclarationRef, crate::parser::Declaration)>,
}
#[derive(Clone, Debug)]
pub struct ExpandedLeaf {
    pub path: String,
    pub segments: Vec<PathSegment>,
    pub data_type: String,
    pub line: usize,
    pub comment: String,
}
#[derive(Clone, Debug)]
pub struct ExpandedDb {
    pub name: String,
    pub tree: Vec<FieldNode>,
    pub leaves: Vec<ExpandedLeaf>,
    pub standard: bool,
}
#[derive(Clone, Debug)]
pub struct LayoutLeaf {
    pub path: String,
    pub byte: u32,
    pub bit: Option<u8>,
}
#[derive(Clone, Debug)]
pub struct LayoutPlan {
    pub leaves: Vec<LayoutLeaf>,
    pub length: u32,
}
pub fn width(t: &str) -> Option<u32> {
    match t {
        "BOOL" | "BYTE" | "USINT" | "CHAR" => Some(1),
        "INT" | "UINT" | "WORD" => Some(2),
        "DINT" | "UDINT" | "DWORD" | "REAL" => Some(4),
        _ => t
            .strip_prefix("STRING[")
            .and_then(|s| s.strip_suffix(']'))
            .and_then(|s| s.parse::<u32>().ok())
            .filter(|n| (1..=254).contains(n))
            .map(|n| n + 2),
    }
}
pub fn diagnostic(code: &str) -> Diagnostic {
    Diagnostic {
        code: code.into(),
        path: String::new(),
        line: 0,
        file: String::new(),
    }
}
/// 段来自树节点名和ARRAY容器，绝不拆sourcePath字符串。
pub fn structured_leaves(tree: &[FieldNode]) -> Vec<ExpandedLeaf> {
    fn walk(nodes: &[FieldNode], prefix: &[PathSegment], array: bool, out: &mut Vec<ExpandedLeaf>) {
        for n in nodes {
            let mut segments = prefix.to_vec();
            if array {
                if let Some(i) = n
                    .name
                    .strip_prefix('[')
                    .and_then(|s| s.strip_suffix(']'))
                    .and_then(|s| s.parse::<i32>().ok())
                {
                    segments.push(PathSegment::Index(i))
                } else {
                    continue;
                }
            } else {
                segments.push(PathSegment::Field(n.name.clone()))
            }
            if n.children.is_empty() {
                out.push(ExpandedLeaf {
                    path: n.path.clone(),
                    segments,
                    data_type: n.data_type.clone(),
                    line: n.line,
                    comment: n.comment.clone(),
                })
            } else {
                walk(&n.children, &segments, n.data_type == "ARRAY", out)
            }
        }
    }
    let mut out = vec![];
    walk(tree, &[], false, &mut out);
    out
}
