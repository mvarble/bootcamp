import pytest
from hypothesis import given
from hypothesis import strategies as st

from algolib import DSU


def test_starts_as_singletons():
    d = DSU(4)
    assert len(d) == 4
    assert d.components == 4
    assert all(d.find(i) == i and d.size(i) == 1 for i in range(4))


def test_union_and_queries():
    d = DSU(6)
    assert d.union(0, 1)
    assert d.union(1, 2)
    assert not d.union(0, 2)
    assert d.same(0, 2)
    assert not d.same(0, 3)
    assert d.size(2) == 3
    assert d.components == 4


def test_self_union_is_noop():
    d = DSU(2)
    assert not d.union(1, 1)
    assert d.components == 2


def test_empty():
    d = DSU(0)
    assert len(d) == 0
    assert d.components == 0


def test_negative_size_rejected():
    with pytest.raises(ValueError):
        DSU(-1)


def naive_labels(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """Oracle: relabel until fixpoint (O(n * |edges|))."""
    label = list(range(n))
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            lo = min(label[a], label[b])
            for v in (a, b):
                if label[v] != lo:
                    label[v] = lo
                    changed = True
    return label


@st.composite
def graphs(draw):
    n = draw(st.integers(1, 30))
    edge = st.tuples(st.integers(0, n - 1), st.integers(0, n - 1))
    return n, draw(st.lists(edge, max_size=60))


@given(graphs())
def test_matches_naive_oracle(graph):
    n, edges = graph
    d = DSU(n)
    for a, b in edges:
        d.union(a, b)
    label = naive_labels(n, edges)
    for a in range(n):
        for b in range(n):
            assert d.same(a, b) == (label[a] == label[b])
    assert d.components == len(set(label))
    for a in range(n):
        assert d.size(a) == label.count(label[a])
