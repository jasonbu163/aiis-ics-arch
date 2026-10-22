//! 文件：src/infrastructure/s7_int_pdu.rs；唯一单item/2字节DB INT的S7 payload codec，连接由原库负责。
use crate::Result;
use serde::{Deserialize, Serialize};
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Operation {
    Read,
    Write(i16),
}
impl Operation {
    fn function(self) -> u8 {
        if matches!(self, Self::Read) {
            4
        } else {
            5
        }
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidatedWriteAck {
    reference: u16,
}
impl ValidatedWriteAck {
    pub fn reference(&self) -> u16 {
        self.reference
    }
}
#[derive(Debug)]
pub struct ValidatedRead {
    value: i16,
    reference: u16,
}
impl ValidatedRead {
    pub fn value(&self) -> i16 {
        self.value
    }
    pub fn reference(&self) -> u16 {
        self.reference
    }
}
#[derive(Debug)]
pub enum Validated {
    Read(ValidatedRead),
    Write(ValidatedWriteAck),
}
pub fn encode(reference: u16, db: u16, offset: u32, op: Operation) -> Result<Vec<u8>> {
    if reference == 0 || db == 0 || offset > 65534 {
        return Err("s7_request_range".into());
    }
    let data_len = if matches!(op, Operation::Read) { 0 } else { 6 };
    let mut b = vec![0x32, 1, 0, 0];
    b.extend(reference.to_be_bytes());
    b.extend([
        0,
        14,
        0,
        data_len,
        op.function(),
        1,
        0x12,
        0x0a,
        0x10,
        2,
        0,
        2,
    ]);
    b.extend(db.to_be_bytes());
    b.push(0x84);
    let bits = (offset * 8).to_be_bytes();
    b.extend(&bits[1..]);
    if let Operation::Write(value) = op {
        b.extend([0, 4, 0, 16]);
        b.extend(value.to_be_bytes());
    }
    Ok(b)
}
pub fn validate(b: &[u8], reference: u16, op: Operation) -> Result<Validated> {
    if b.len() < 12 || b.len() > 4096 || b[0] != 0x32 || b[1] != 3 || b[2..4] != [0, 0] {
        return Err("s7_invalid_response".into());
    }
    if b[4..6] != reference.to_be_bytes() {
        return Err("s7_reference_mismatch".into());
    }
    if b[10..12] != [0, 0] {
        return Err("s7_remote_error".into());
    }
    let length = if matches!(op, Operation::Read) {
        20
    } else {
        15
    };
    let data_len = length - 14;
    if b.len() != length
        || b[6..8] != [0, 2]
        || u16::from_be_bytes([b[8], b[9]]) as usize != data_len
        || b[12] != op.function()
        || b[13] != 1
    {
        return Err("s7_invalid_response".into());
    }
    if b[14] != 0xff {
        return Err("s7_remote_error".into());
    }
    if matches!(op, Operation::Read) {
        if b[15..18] != [4, 0, 16] {
            return Err("s7_invalid_response".into());
        }
        Ok(Validated::Read(ValidatedRead {
            value: i16::from_be_bytes([b[18], b[19]]),
            reference,
        }))
    } else {
        Ok(Validated::Write(ValidatedWriteAck { reference }))
    }
}
pub struct Session {
    next: u32,
}
impl Default for Session {
    fn default() -> Self {
        Self { next: 1 }
    }
}
impl Session {
    #[cfg(feature = "test-fixture")]
    pub fn test_near_end() -> Self {
        Self { next: 65534 }
    }
    pub fn exhausted(&self) -> bool {
        self.next >= 65535
    }
    pub fn exchange(
        &mut self,
        client: &rust_snap7::S7Client,
        db: u16,
        offset: u32,
        op: Operation,
    ) -> Result<Validated> {
        if self.exhausted() {
            return Err("s7_session_retired".into());
        }
        let reference = self.next as u16;
        self.next += 1;
        let request = encode(reference, db, offset, op)?;
        let mut buffer = [0u8; 4096];
        buffer[..request.len()].copy_from_slice(&request);
        let mut size = request.len() as i32;
        client
            .iso_exchange_buffer(&mut buffer, &mut size)
            .map_err(|_| "plc_io")?;
        if size < 0 || size as usize > buffer.len() {
            return Err("s7_invalid_response".into());
        }
        validate(&buffer[..size as usize], reference, op)
    }
}
