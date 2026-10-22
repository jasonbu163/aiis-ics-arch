//! DS运行时职责：Actual no-port int ABI and packed layout; rejects malformed whole-PDU before item dispatch.
use ds_runtime::infrastructure::native_ffi::{self, Callbacks, Descriptor, Tag};
#[test]
fn c_rust_layout_and_int_returns() {
    let a = native_ffi::probe().unwrap();
    assert_eq!(std::mem::size_of::<Tag>(), 20);
    assert_eq!(std::mem::align_of::<Tag>(), 1);
    assert_eq!(
        [
            std::mem::offset_of!(Tag, area),
            std::mem::offset_of!(Tag, db),
            std::mem::offset_of!(Tag, start),
            std::mem::offset_of!(Tag, count),
            std::mem::offset_of!(Tag, wordlen)
        ],
        [0, 4, 8, 12, 16]
    );
    assert_eq!(a.callbacks_size as usize, std::mem::size_of::<Callbacks>());
    assert_eq!((a.callback_zero, a.callback_nonzero), (0, 37));
    assert_eq!(std::mem::size_of::<Descriptor>(), 64)
}
#[test]
fn invalid_whole_request_never_admitted() {
    for b in [&[][..], &[0x32; 11][..], &[0x32; 481][..]] {
        assert!(native_ffi::parse_pdu(b).is_none())
    }
}
