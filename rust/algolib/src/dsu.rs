//! Disjoint-set union (union-find).

/// Disjoint-set union over `0..n` with path halving and union by size.
///
/// `find`/`union` run in amortized O(α(n)).
#[derive(Clone, Debug)]
pub struct Dsu {
    parent: Vec<usize>,
    size: Vec<usize>,
    components: usize,
}

impl Dsu {
    pub fn new(n: usize) -> Self {
        Self { parent: (0..n).collect(), size: vec![1; n], components: n }
    }

    pub fn len(&self) -> usize {
        self.parent.len()
    }

    pub fn is_empty(&self) -> bool {
        self.parent.is_empty()
    }

    /// Number of disjoint sets.
    pub fn components(&self) -> usize {
        self.components
    }

    pub fn find(&mut self, mut x: usize) -> usize {
        while self.parent[x] != x {
            self.parent[x] = self.parent[self.parent[x]];
            x = self.parent[x];
        }
        x
    }

    /// Merges the sets of `a` and `b`. Returns `false` if they were already joined.
    pub fn union(&mut self, a: usize, b: usize) -> bool {
        let (mut ra, mut rb) = (self.find(a), self.find(b));
        if ra == rb {
            return false;
        }
        if self.size[ra] < self.size[rb] {
            std::mem::swap(&mut ra, &mut rb);
        }
        self.parent[rb] = ra;
        self.size[ra] += self.size[rb];
        self.components -= 1;
        true
    }

    pub fn same(&mut self, a: usize, b: usize) -> bool {
        self.find(a) == self.find(b)
    }

    /// Size of the set containing `x`.
    pub fn size(&mut self, x: usize) -> usize {
        let r = self.find(x);
        self.size[r]
    }
}

#[cfg(test)]
mod tests {
    use super::Dsu;

    #[test]
    fn starts_as_singletons() {
        let mut d = Dsu::new(4);
        assert_eq!(d.len(), 4);
        assert_eq!(d.components(), 4);
        assert!((0..4).all(|i| d.find(i) == i && d.size(i) == 1));
    }

    #[test]
    fn union_and_queries() {
        let mut d = Dsu::new(6);
        assert!(d.union(0, 1));
        assert!(d.union(1, 2));
        assert!(!d.union(0, 2));
        assert!(d.same(0, 2));
        assert!(!d.same(0, 3));
        assert_eq!(d.size(2), 3);
        assert_eq!(d.components(), 4);
    }

    #[test]
    fn self_union_is_noop() {
        let mut d = Dsu::new(2);
        assert!(!d.union(1, 1));
        assert_eq!(d.components(), 2);
    }

    #[test]
    fn empty() {
        let d = Dsu::new(0);
        assert!(d.is_empty());
        assert_eq!(d.components(), 0);
    }
}
