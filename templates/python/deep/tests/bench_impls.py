"""Wiring (deep tier): constant-factor benchmarks, one per implementation and size.

Not collected by `just test`; run with `just bench <path>`, which writes raw
JSON (per-round stats, stddev, IQR) to .meta/bench/pytest-benchmark.json.
"""

import pytest

from {{pkg}}.generate import call, generate

BENCH_SIZES = [1_000, 100_000]


@pytest.mark.parametrize("n", BENCH_SIZES)
def test_bench(benchmark, impl, n):
    x = generate(n, 0)
    benchmark(call, impl, x)
