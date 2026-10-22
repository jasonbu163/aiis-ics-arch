//! 文件：tests/s7_int_pdu.rs；固定payload及逐长度截断/字段拒绝，不替代真实协议gate。
use field_flow::infrastructure::s7_int_pdu::{encode, validate, Operation, Validated};
fn bytes(h: &str) -> Vec<u8> {
    (0..h.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&h[i..i + 2], 16).unwrap())
        .collect()
}
#[test]
fn fixed_requests_and_ints() {
    assert_eq!(
        encode(0x1234, 1, 4, Operation::Read).unwrap(),
        bytes("320100001234000e00000401120a10020002000184000020")
    );
    for v in [-32768, -1, 0, 42, 32767] {
        let b = encode(0x1234, 1, 4, Operation::Write(v)).unwrap();
        assert_eq!(b.len(), 30);
        assert_eq!(
            &b[..24],
            bytes("320100001234000e00060501120a10020002000184000020")
        );
        assert_eq!(&b[24..28], &[0, 4, 0, 16]);
        assert_eq!(&b[28..], &v.to_be_bytes());
    }
    assert!(encode(0, 1, 0, Operation::Read).is_err());
    assert!(encode(1, 0, 0, Operation::Read).is_err());
    assert!(encode(1, 1, 65535, Operation::Read).is_err());
}
#[test]
fn all_lengths_and_fields() {
    for (op, hex) in [
        (Operation::Read, "3203000012340002000600000401ff040010002a"),
        (Operation::Write(42), "3203000012340002000100000501ff"),
    ] {
        let good = bytes(hex);
        assert!(validate(&good, 0x1234, op).is_ok());
        for n in 0..good.len() {
            assert!(validate(&good[..n], 0x1234, op).is_err(), "truncated {n}");
        }
        let mut extra = good.clone();
        extra.push(0);
        assert!(validate(&extra, 0x1234, op).is_err());
        for n in 0..good.len() {
            if matches!(op, Operation::Read) && n >= 18 {
                continue;
            }
            let mut bad = good.clone();
            bad[n] ^= 1;
            assert!(validate(&bad, 0x1234, op).is_err(), "field {n}");
        }
        let mut huge = good.clone();
        huge.resize(4097, 0);
        assert!(validate(&huge, 0x1234, op).is_err());
    }
}
#[test]
fn typed_values() {
    let read = validate(
        &bytes("3203000000010002000600000401ff040010ffff"),
        1,
        Operation::Read,
    )
    .unwrap();
    match read {
        Validated::Read(r) => {
            assert_eq!(r.value(), -1);
            assert_eq!(r.reference(), 1)
        }
        _ => panic!(),
    }
    let ack = validate(
        &bytes("3203000000010002000100000501ff"),
        1,
        Operation::Write(42),
    )
    .unwrap();
    match ack {
        Validated::Write(r) => assert_eq!(r.reference(), 1),
        _ => panic!(),
    }
}
