//! Property test: Dsu agrees with a naive relabel-until-fixpoint oracle.

use algolib::Dsu;
use proptest::prelude::*;

fn naive_labels(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    let mut label: Vec<usize> = (0..n).collect();
    let mut changed = true;
    while changed {
        changed = false;
        for &(a, b) in edges {
            let lo = label[a].min(label[b]);
            for v in [a, b] {
                if label[v] != lo {
                    label[v] = lo;
                    changed = true;
                }
            }
        }
    }
    label
}

fn graph() -> impl Strategy<Value = (usize, Vec<(usize, usize)>)> {
    (1usize..30).prop_flat_map(|n| (Just(n), prop::collection::vec((0..n, 0..n), 0..60)))
}

proptest! {
    #[test]
    fn matches_naive_oracle((n, edges) in graph()) {
        let mut d = Dsu::new(n);
        for &(a, b) in &edges {
            d.union(a, b);
        }
        let label = naive_labels(n, &edges);
        for a in 0..n {
            for b in 0..n {
                prop_assert_eq!(d.same(a, b), label[a] == label[b]);
            }
            prop_assert_eq!(d.size(a), label.iter().filter(|&&l| l == label[a]).count());
        }
        let mut roots = label.clone();
        roots.sort_unstable();
        roots.dedup();
        prop_assert_eq!(d.components(), roots.len());
    }
}
