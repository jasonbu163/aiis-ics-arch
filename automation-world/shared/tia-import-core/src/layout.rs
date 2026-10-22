//! V20标准word纯布局；不确认地址、不接触来源或SQLite。
use crate::model::*;
pub fn aligned(bits: u32) -> LocalResult<u32> {
    bits.checked_add(15)
        .map(|n| n / 16 * 16)
        .ok_or("layout_overflow".into())
}
pub fn layout_nodes(
    nodes: &[FieldNode],
    cursor: &mut u32,
    out: &mut Vec<(String, u32, Option<u8>)>,
    depth: usize,
) -> LocalResult<()> {
    if depth > 8 {
        return Err("expansion_depth".into());
    }
    for n in nodes {
        let result = (|| -> LocalResult<()> {
            if !n.children.is_empty() {
                *cursor = aligned(*cursor)?;
                if n.data_type == "ARRAY" {
                    let lo = n.lower.ok_or("array_bounds")?;
                    let hi = n.upper.ok_or("array_bounds")?;
                    let count = i64::from(hi) - i64::from(lo) + 1;
                    if !(1..=1024).contains(&count) || n.children.len() != count as usize {
                        return Err("array_bounds".into());
                    }
                    if has_array(&n.children) {
                        return Err("nested_array".into());
                    }
                }
                layout_nodes(&n.children, cursor, out, depth + 1)?;
                *cursor = aligned(*cursor)?;
            } else {
                if n.data_type.starts_with("STRING[")
                    || n.data_type == "ARRAY"
                    || n.data_type == "STRUCT"
                {
                    return Err("offset_inference_unsupported".into());
                }
                let width = width(&n.data_type).ok_or("unsupported_type")?;
                let (byte, bit) = if n.data_type == "BOOL" {
                    let at = (*cursor / 8, Some((*cursor % 8) as u8));
                    *cursor = cursor.checked_add(1).ok_or("layout_overflow")?;
                    at
                } else {
                    let mut byte = cursor.checked_add(7).ok_or("layout_overflow")? / 8;
                    if width >= 2 {
                        byte = byte.checked_add(1).ok_or("layout_overflow")? / 2 * 2;
                    }
                    *cursor = byte
                        .checked_add(width)
                        .and_then(|b| b.checked_mul(8))
                        .ok_or("layout_overflow")?;
                    (byte, None)
                };
                out.push((n.path.clone(), byte, bit));
            }
            if *cursor > 65536 * 8 {
                return Err("layout_overflow".into());
            }
            Ok(())
        })();
        result.map_err(|e| {
            format!(
                "{}:path={}:line={}",
                e.split(':').next().unwrap_or("layout_invalid"),
                n.path,
                n.line
            )
        })?;
    }
    Ok(())
}
fn has_array(nodes: &[FieldNode]) -> bool {
    nodes
        .iter()
        .any(|n| n.data_type == "ARRAY" || has_array(&n.children))
}

pub fn layout_standard(
    db: &ExpandedDb,
    _profile: LayoutProfile,
) -> Result<LayoutPlan, Vec<Diagnostic>> {
    if !db.standard {
        return Err(vec![diagnostic("optimized_access_unknown")]);
    }
    let mut cursor = 0;
    let mut rows = vec![];
    layout_nodes(&db.tree, &mut cursor, &mut rows, 0).map_err(|e| vec![diagnostic(&e)])?;
    let length = aligned(cursor).map_err(|e| vec![diagnostic(&e)])? / 8;
    if length == 0 || length > 65536 {
        return Err(vec![diagnostic("layout_db_length")]);
    }
    Ok(LayoutPlan {
        leaves: rows
            .into_iter()
            .map(|(path, byte, bit)| LayoutLeaf { path, byte, bit })
            .collect(),
        length,
    })
}
