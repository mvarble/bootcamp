//! Wiring: `cargo run --release -p example-max-subarray --example scale [-- OUT.jsonl]` times every implementation.

fn main() {
    harness::scaling::main(example_max_subarray::IMPLS, example_max_subarray::generate::generate, example_max_subarray::generate::SCALE_SIZES, env!("CARGO_MANIFEST_DIR"));
}
