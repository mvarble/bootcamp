//! Wiring: `cargo run --release -p {{slug}} --example scale [-- OUT.jsonl]` times every implementation.

fn main() {
    harness::scaling::main({{pkg}}::IMPLS, {{pkg}}::generate::generate, {{pkg}}::generate::SCALE_SIZES, env!("CARGO_MANIFEST_DIR"));
}
