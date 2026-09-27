//! Wiring: the Codeforces-style entry point, `cargo run -p {{slug}} < input`.

use std::io::{self, Read, Write};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).expect("read stdin");
    io::stdout().write_all({{pkg}}::shim::run(&input).as_bytes()).expect("write stdout");
}
