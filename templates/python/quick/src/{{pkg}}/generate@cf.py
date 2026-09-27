"""Random inputs, plus the adapter that tests, stress, scale, and benches call implementations through."""

import random

# Sizes for `just scale`; None uses the harness default (2^8 .. 2^17).
SCALE_SIZES = None


def generate(n: int, seed: int) -> list[int]:
    """A random parsed input of size n, deterministic in seed."""
    rng = random.Random(seed)
    return [rng.randint(-100, 100) for _ in range(n)]


def call(impl, x):
    """Run implementation module `impl` (mine, brute, reference) on parsed input x."""
    return impl.solve(x)
