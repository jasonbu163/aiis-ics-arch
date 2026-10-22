//! DS运行时职责：Owned request payload; no native borrowed pointers survive callback scope.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(i32)]
pub enum Source {
    Client = 0,
    Rule = 1,
    Ui = 2,
    Maintenance = 3,
    Initialize = 4,
    Reset = 5,
    Read = 6,
}
impl Source {
    pub fn from_i32(n: i32) -> Option<Self> {
        Some(match n {
            0 => Self::Client,
            1 => Self::Rule,
            2 => Self::Ui,
            3 => Self::Maintenance,
            4 => Self::Initialize,
            5 => Self::Reset,
            6 => Self::Read,
            _ => return None,
        })
    }
}
#[derive(Clone)]
pub struct Request {
    pub connection: u64,
    pub pdu: u64,
    pub epoch: u64,
    pub revision: u64,
    pub cas: u64,
    pub item: u32,
    pub db: i32,
    pub start: usize,
    pub size: usize,
    pub bit: Option<u8>,
    pub source: Source,
    pub data: [u8; 256],
    pub admitted: u64,
}
impl Default for Request {
    fn default() -> Self {
        Self {
            connection: 0,
            pdu: 0,
            epoch: 1,
            revision: 1,
            cas: 0,
            item: 0,
            db: 41,
            start: 0,
            size: 0,
            bit: None,
            source: Source::Client,
            data: [0; 256],
            admitted: 0,
        }
    }
}
