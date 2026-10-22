//! DS运行时职责：One deterministic item result; committed-with-lost-ack is an external unknown result.
#[derive(Clone)]
pub struct ItemResult {
    pub ok: bool,
    pub seq: u64,
    pub data: [u8; 256],
}
impl Default for ItemResult {
    fn default() -> Self {
        Self {
            ok: false,
            seq: 0,
            data: [0; 256],
        }
    }
}
