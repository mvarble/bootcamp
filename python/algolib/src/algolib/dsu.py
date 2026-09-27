"""Disjoint-set union (union-find)."""


class DSU:
    """Disjoint-set union over 0..n-1 with path halving and union by size.

    find/union run in amortized O(alpha(n)).
    """

    __slots__ = ("_parent", "_size", "components")

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._parent = list(range(n))
        self._size = [1] * n
        self.components = n

    def __len__(self) -> int:
        return len(self._parent)

    def find(self, x: int) -> int:
        parent = self._parent
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        """Merge the sets of a and b. Returns False if they were already joined."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self._size[ra] < self._size[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        self._size[ra] += self._size[rb]
        self.components -= 1
        return True

    def same(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def size(self, x: int) -> int:
        """Size of the set containing x."""
        return self._size[self.find(x)]
