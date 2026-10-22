//! DS运行时职责：Exactly 100 same-clock native points bracketed by Rust CLOCK_MONOTONIC reads.
#[test]
fn native_clock_is_in_rust_brackets() {
    let s = ds_runtime::infrastructure::native_ffi::clock_samples().unwrap();
    assert_eq!(s["count"], 100);
    assert_eq!(s["samples"].as_array().unwrap().len(), 100)
}
