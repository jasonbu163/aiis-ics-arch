//! TIA源导入入口：安全分界解析与显式所选delta；不重解析/替换未选来源。
mod parser;
mod reconcile;
#[cfg(test)]
mod tests;
pub(crate) use crate::domain::source_import::ImportPreview;
pub(crate) use reconcile::{identify, legacy_import, plan, verify_db};
// 旧单DB纯函数调用保持兼容；多DB必须使用显式映射。
#[cfg(test)]
pub(crate) use reconcile::legacy_import as import;
