//! Wiring: every provided/samples/*.in through `shim::run`, compared token-by-token with the matching .out.

use std::fs;
use std::path::Path;

#[test]
fn samples() {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("provided/samples");
    let mut inputs: Vec<_> = fs::read_dir(&dir)
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|e| e == "in"))
        .collect();
    inputs.sort();
    for input in inputs {
        let want = fs::read_to_string(input.with_extension("out")).expect("matching .out file");
        let got = {{pkg}}::shim::run(&fs::read_to_string(&input).expect("read .in"));
        assert_eq!(
            got.split_whitespace().collect::<Vec<_>>(),
            want.split_whitespace().collect::<Vec<_>>(),
            "{}",
            input.display()
        );
    }
}
