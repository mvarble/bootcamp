# Exercise templates

`just new <lang> <slug>` renders `common/quick/` and then `<lang>/quick/` into `<lang>/exercises/<slug>/`. `just deepen <path>` renders `common/deep/` and `<lang>/deep/` on top and edits a few wiring lines (listed below). The logic is in `scripts/exercise.py`.

## Rendering rules

- **Placeholders**, in both paths and contents:
  - `{{slug}}`: the exercise slug;
  - `{{pkg}}`: the slug with `_` for `-`, used as the Python import name and the Rust crate name;
  - `{{source}}`: `lc` or `cf`;
  - `{{url}}`;
  - `{{link}}`: the source as a Markdown link when a URL is known.
- **Variants:** a path component tagged `@lc` or `@cf` is rendered only for that source, with the tag removed. For example, `mine@cf.py` becomes `mine.py` for Codeforces exercises and is skipped for LeetCode ones. The source comes from the slug prefix (`cf1850a-…` → cf, anything else → lc) unless `--source` overrides it.
- **Generated files:** `new` also writes `.meta/exercise.toml` (via `scripts/meta.py`) and `.meta/stub.<ext>`, a copy of `mine`. `just revisit` resets `mine` to that copy, so after pasting the real signature into `mine`, run `just stub <path>` to refresh it. It refuses once `mine` no longer contains the not-implemented marker.

## One adapter per problem

Tests, stress, scale, and benches never call implementations directly. They go through `generate.*`, which you write per problem:

| | Python `generate.py` | Rust `src/generate.rs` | C++ `generate.hpp` |
|---|---|---|---|
| input/output types | (duck-typed) | `Input`, `Output` | `Input`, `Output` |
| random input | `generate(n, seed)` | `generate(n, seed)` | `generate(n, seed)` |
| call an impl | `call(module, x)` | `call!(module, x)` macro | `call<S>(x)` |
| scale sizes | `SCALE_SIZES` | `SCALE_SIZES` | `kScaleSizes` |

So an LC `Solution` stub can have any signature. Only `call` knows about it, and `deepen` never has to touch your files.

## Files and ownership

**Owned** files are mine: agents don't write them (AGENTS.md §1, enforced by `.claude/hooks/guard.ts`). All other files are **wiring**.

| | Python | Rust | C++ |
|---|---|---|---|
| owned | `README.md`, `src/<pkg>/{mine,brute,generate}.py`, `tests/test_cases.py`, cf: `src/<pkg>/shim.py` | `README.md`, `src/{mine,brute,generate}.rs`, `tests/cases/mod.rs`, cf: `src/shim.rs` | `README.md`, `{mine,brute,generate}.hpp`, `tests/cases.cpp`, cf: `shim.hpp` |
| per-impl test instantiation | `tests/conftest.py`: session-scoped fixture `impl`, parametrized over `mine` plus `reference` if that module exists | `tests/suite.rs`: `suite!(mine);` and deepen adds `suite!(reference);`. Your `tests/cases/mod.rs` defines `macro_rules! suite` | `impls.hpp`: `ImplTypes` + `kImplNames`, used by `TYPED_TEST_SUITE(Cases, …, ImplNames)` |
| stress | hypothesis over `(n, seed)`; `just stress` uses profile `stress` | proptest over `(n, seed)`; `just stress` sets `PROPTEST_CASES=5000` | seeded loop, ascending `n`; `just stress` sets `STRESS_ITERS=5000` |
| scale entrypoint | `python -m <pkg>.scale` | `cargo run --release -p <slug> --example scale` | `<slug>_scale` (release preset) |
| cf entry + samples | `__main__.py`, `tests/test_samples.py` | `src/main.rs`, `tests/samples.rs` | `main.cpp`, `tests/samples.cpp` |

`provided/` holds the verbatim function stub (`stub.<ext>`, never compiled) and the sample I/O (`samples.md` for LeetCode; `samples/N.in` and `samples/N.out` for Codeforces).

## Deep tier (`just deepen`)

| | adds | edits wiring |
|---|---|---|
| all | `analysis/README.md` | `tier = "deep"` in exercise.toml |
| Python | `src/<pkg>/reference.py` (`from .mine import *`), `tests/bench_impls.py` (pytest-benchmark) | none: conftest picks up `reference` |
| Rust | `src/reference.rs` (`pub use crate::mine::*`), `benches/impls.rs` (criterion) | `lib.rs`: `pub mod reference;` and `wire!(mine, reference, brute)`. `tests/suite.rs`: `suite!(reference);`. `Cargo.toml`: criterion dev-dependency and `[[bench]]` |
| C++ | `reference.hpp` (`struct Solution : mine::Solution {}`), `bench.cpp` (Google Benchmark) | `CMakeLists.txt`: `DEEP` flag. `impls.hpp`: include and list `reference::Solution` |

Until `/reference` writes a real one, `reference` is `mine` under another name. So everything builds, tests, and benchmarks over two implementations from the moment you deepen.
