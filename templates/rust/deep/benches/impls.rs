//! Wiring (deep tier): criterion benchmarks, one per implementation and size.
//! `just bench <path>` sets CRITERION_HOME so raw estimates land in .meta/bench/criterion/.

use std::hint::black_box;

use criterion::{BenchmarkId, Criterion, criterion_group, criterion_main};

const BENCH_SIZES: &[usize] = &[1_000, 100_000];

fn impls(c: &mut Criterion) {
    let mut group = c.benchmark_group("impls");
    for &n in BENCH_SIZES {
        let x = {{pkg}}::generate::generate(n, 0);
        for &(name, f) in {{pkg}}::IMPLS.iter().filter(|(name, _)| *name != "brute") {
            group.bench_with_input(BenchmarkId::new(name, n), &x, |b, x| b.iter(|| f(black_box(x))));
        }
    }
    group.finish();
}

criterion_group!(benches, impls);
criterion_main!(benches);
