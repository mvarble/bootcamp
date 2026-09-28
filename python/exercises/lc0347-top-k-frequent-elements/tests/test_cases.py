"""My tests: examples and edge cases chosen before coding, then stress against brute.

Every test taking `impl` runs once per implementation (see conftest.py).
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from lc0347_top_k_frequent_elements import brute
from lc0347_top_k_frequent_elements.generate import call, generate

EXAMPLES = [
    # (input, expected),
    (([1, 1, 1, 2, 2, 3], 2), [1, 2]),
    (([1], 1), [1]),
    (([1, 2, 1, 2, 1, 2, 3, 1, 3, 2], 2), [1, 2]),
]

EDGE_CASES = [
    # (input, expected),
]


@pytest.mark.parametrize(("x", "want"), EXAMPLES + EDGE_CASES)
def test_cases(impl, x, want):
    assert call(impl, x) == want


@given(n=st.integers(1, 64), seed=st.integers(0, 2**32 - 1))
def test_stress(impl, n, seed):
    x = generate(n, seed)
    assert call(impl, x) == call(brute, x)
