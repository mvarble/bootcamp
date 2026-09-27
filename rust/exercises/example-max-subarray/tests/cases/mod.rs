//! My tests: examples and edge cases chosen before coding, then stress against brute.
//! `suite!(imp)` expands to one test module per implementation (see tests/suite.rs).

macro_rules! suite {
    ($imp:ident) => {
        mod $imp {
            use example_max_subarray::impls;
            use example_max_subarray::generate::{Input, Output, generate};
            use proptest::prelude::*;

            fn run(x: &Input) -> Output {
                impls::$imp(x)
            }

            fn check(cases: &[(Input, Output)]) {
                for (x, want) in cases {
                    assert_eq!(run(x), *want, "input: {x:?}");
                }
            }

            #[test]
            fn examples() {
                check(&[
                    (vec![-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
                    (vec![1], 1),
                    (vec![5, 4, -1, 7, 8], 23),
                ]);
            }

            #[test]
            fn edge_cases() {
                check(&[
                    (vec![-5], -5),
                    (vec![-3, -1, -2], -1),
                    (vec![0, 0, 0], 0),
                    (vec![2, 3, 4], 9),
                    (vec![4, -10, 1], 4),
                    (vec![1, -10, 4, 5], 9),
                ]);
            }

            proptest! {
                #[test]
                fn stress(n in 0usize..64, seed in any::<u64>()) {
                    let x = generate(n, seed);
                    prop_assert_eq!(run(&x), impls::brute(&x), "n={} seed={}", n, seed);
                }
            }
        }
    };
}
