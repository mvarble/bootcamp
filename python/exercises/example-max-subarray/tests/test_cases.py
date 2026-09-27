"""My tests: examples and edge cases chosen before coding, then stress against brute.

Every test taking `impl` runs once per implementation (see conftest.py).
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from example_max_subarray import brute
from example_max_subarray.generate import call, generate

EXAMPLES = [
    ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
    ([1], 1),
    ([5, 4, -1, 7, 8], 23),
]

EDGE_CASES = [
    ([-5], -5),  # single negative
    ([-3, -1, -2], -1),  # all negative: best single element, not 0
    ([0, 0, 0], 0),
    ([2, 3, 4], 9),  # whole array
    ([4, -10, 1], 4),  # prefix
    ([1, -10, 4, 5], 9),  # suffix
]


@pytest.mark.parametrize(("x", "want"), EXAMPLES + EDGE_CASES)
def test_cases(impl, x, want):
    assert call(impl, x) == want


@given(n=st.integers(0, 64), seed=st.integers(0, 2**32 - 1))
def test_stress(impl, n, seed):
    x = generate(n, seed)
    assert call(impl, x) == call(brute, x)
