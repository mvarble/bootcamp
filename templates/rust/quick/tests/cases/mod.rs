//! My tests: examples and edge cases chosen before coding, then stress against brute.
//! `suite!(imp)` expands to one test module per implementation (see tests/suite.rs).

macro_rules! suite {
    ($imp:ident) => {
        mod $imp {
            use proptest::prelude::*;
            use {{pkg}}::generate::{Input, Output, generate};
            use {{pkg}}::impls;

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
                    // (input, expected),
                ]);
            }

            #[test]
            fn edge_cases() {
                check(&[
                    // (input, expected),
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
