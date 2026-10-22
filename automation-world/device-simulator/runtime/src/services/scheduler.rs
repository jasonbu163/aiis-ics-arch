//! DS运行时职责：Three class round robin; protocol class selects one item per connection turn.
use std::collections::VecDeque;
pub fn class(mask: u8, next: &mut usize) -> Option<usize> {
    for i in 0..3 {
        let c = (*next + i) % 3;
        if mask & (1 << c) != 0 {
            *next = (c + 1) % 3;
            return Some(c);
        }
    }
    None
}
pub fn connection<T>(q: &mut VecDeque<T>, last: &mut u64, id: impl Fn(&T) -> u64) -> Option<T> {
    let index = q
        .iter()
        .enumerate()
        .filter(|(_, v)| id(v) > *last)
        .min_by_key(|(_, v)| id(v))
        .map(|(i, _)| i)
        .or_else(|| {
            q.iter()
                .enumerate()
                .min_by_key(|(_, v)| id(v))
                .map(|(i, _)| i)
        })?;
    let v = q.remove(index)?;
    *last = id(&v);
    Some(v)
}
