//! Random inputs, plus the adapter that tests, stress, scale, and benches call implementations through.

use rand::{RngExt, SeedableRng, rngs::StdRng};

pub type Input = Vec<i32>;
pub type Output = i32;

/// Sizes for `just scale`; empty uses the harness default (2^10 ..= 2^22).
pub const SCALE_SIZES: &[usize] = &[];

/// A random input of size `n`, deterministic in `seed`.
pub fn generate(n: usize, seed: u64) -> Input {
    let mut rng = StdRng::seed_from_u64(seed);
    (0..n).map(|_| rng.random_range(-100..=100)).collect()
}

/// How to run implementation module `$imp` (mine, brute, reference) on `$x: &Input`.
macro_rules! call {
    ($imp:ident, $x:expr) => {
        crate::$imp::Solution::solve($x.clone())
    };
}
pub(crate) use call;
