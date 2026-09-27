"""Random inputs, plus the adapter that tests, stress, scale, and benches call implementations through."""

import random

# Sizes for `just scale`; None uses the harness default (2^8 .. 2^17).
SCALE_SIZES = None


def generate(n: int, seed: int) -> list[int]:
    """A random non-empty list of length max(n, 1), deterministic in seed.

    Values are small so ties and all-negative runs are common.
    """
    rng = random.Random(seed)
    return [rng.randint(-10, 10) for _ in range(max(n, 1))]


def call(impl, x):
    """Run implementation module `impl` (mine, brute, reference) on input x."""
    return impl.Solution().maxSubArray(list(x))
