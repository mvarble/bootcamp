# bootcamp task runner. Exercise paths are <lang>/exercises/<slug>, relative to where you run just.

set shell := ["bash", "-euo", "pipefail", "-c"]

inv := invocation_directory()

# List recipes
default:
    @just --list --unsorted

# Scaffold an exercise (source from the lc/cf slug prefix; override with --source lc|cf; --url URL)
new lang slug *flags:
    uv run scripts/exercise.py new {{ lang }} {{ slug }} {{ flags }}

# Opt an exercise into the deep tier: reference.*, benchmarks, analysis/
[no-cd]
deepen path:
    uv run {{ justfile_directory() }}/scripts/exercise.py deepen {{ path }}

# Snapshot the current, still-unsolved mine as the stub that `revisit` resets to
[no-cd]
stub path:
    uv run {{ justfile_directory() }}/scripts/exercise.py stub {{ path }}

# Cold re-solve: archive mine to .meta/attempts/<date>, reset it to the stub, status attempting
[no-cd]
revisit path:
    uv run {{ justfile_directory() }}/scripts/exercise.py revisit {{ path }}

# Run a language workspace's tests: python | rust | cpp [preset=debug|asan|release]
test lang preset="debug":
    #!/usr/bin/env bash
    set -euo pipefail
    case "{{ lang }}" in
      python)
        cd python && uv run --all-packages pytest ;;
      rust)
        cd rust
        excludes=()
        if [[ "${SKIP_ATTEMPTING:-}" == 1 ]]; then
          for slug in $(uv run ../scripts/meta.py attempting rust); do excludes+=(--exclude "$slug"); done
        fi
        cargo test --workspace "${excludes[@]}" ;;
      cpp)
        cd cpp
        cmake --preset {{ preset }} > /dev/null
        cmake --build --preset {{ preset }}
        ctest --preset {{ preset }} ;;
      *)
        echo "unknown lang '{{ lang }}' (python | rust | cpp)" >&2; exit 2 ;;
    esac

# Tests for the harness itself: the pi extension and scripts
test-tooling:
    uv run --no-project --python 3.14 --with pytest==9.1.1 --with tomlkit==0.15.1 pytest -q scripts/tests
    node --test ".pi/extensions/bootcamp/tests/*.test.ts"

# Everything: all three workspaces plus tooling
test-all: (test "python") (test "rust") (test "cpp") test-tooling

# Test one exercise: examples, edge cases, light stress (and cf samples), for every impl
check path:
    #!/usr/bin/env bash
    set -euo pipefail
    source scripts/resolve.sh '{{ inv }}' '{{ path }}'
    case "$lang" in
      python)
        cd python && uv run --all-packages pytest "${rel#python/}/tests" -q ;;
      rust)
        cd rust && cargo test -q -p "$slug" ;;
      cpp)
        cd cpp
        cmake --preset debug > /dev/null
        cmake --build --preset debug --target "${slug}_tests"
        ctest --preset debug -R "^${slug}/" ;;
    esac

# Heavy stress run of one exercise: many more random (n, seed) cases against brute
stress path:
    #!/usr/bin/env bash
    set -euo pipefail
    source scripts/resolve.sh '{{ inv }}' '{{ path }}'
    case "$lang" in
      python)
        cd python && uv run --all-packages pytest "${rel#python/}/tests" -k stress --hypothesis-profile=stress -q ;;
      rust)
        cd rust && PROPTEST_CASES="${PROPTEST_CASES:-5000}" cargo test --release -q -p "$slug" --test suite stress ;;
      cpp)
        cd cpp
        cmake --preset debug > /dev/null
        cmake --build --preset debug --target "${slug}_tests"
        STRESS_ITERS="${STRESS_ITERS:-5000}" ctest --preset debug -R "^${slug}/.*\.Stress" ;;
    esac

# Empirical complexity: time each impl over a size sweep, append JSONL, fit log-log slopes
scale path:
    #!/usr/bin/env bash
    set -euo pipefail
    source scripts/resolve.sh '{{ inv }}' '{{ path }}'
    case "$lang" in
      python)
        (cd python && uv run --all-packages python -m "$pkg.scale") ;;
      rust)
        (cd rust && cargo run --release -q -p "$slug" --example scale) ;;
      cpp)
        (cd cpp && cmake --preset release > /dev/null && cmake --build --preset release --target "${slug}_scale" > /dev/null \
          && "build/release/exercises/$slug/${slug}_scale") ;;
    esac
    uv run scripts/scaling.py "$rel/.meta/bench/scaling.jsonl"

# Deep tier: constant-factor benchmarks per impl; raw output to .meta/bench/
bench path:
    #!/usr/bin/env bash
    set -euo pipefail
    source scripts/resolve.sh '{{ inv }}' '{{ path }}'
    [[ "$tier" == deep ]] || { echo "$rel is $tier tier; run: just deepen $rel" >&2; exit 2; }
    out="$PWD/$rel/.meta/bench"
    mkdir -p "$out"
    case "$lang" in
      python)
        cd python && uv run --all-packages pytest "${rel#python/}/tests/bench_impls.py" -q \
          --benchmark-only --benchmark-json="$out/pytest-benchmark.json" ;;
      rust)
        cd rust && CRITERION_HOME="$out/criterion" cargo bench -q -p "$slug" --bench impls ;;
      cpp)
        cd cpp && cmake --preset release > /dev/null && cmake --build --preset release --target "${slug}_bench" > /dev/null
        "build/release/exercises/$slug/${slug}_bench" --benchmark_repetitions=10 \
          --benchmark_out="$out/gbench.json" --benchmark_out_format=json ;;
    esac
    # The repo is public: drop hostname and absolute paths from the raw JSON.
    python3 "{{ justfile_directory() }}/scripts/scrub_bench.py" "$out/pytest-benchmark.json" "$out/gbench.json"

# Exercises due for a cold re-solve
due:
    uv run scripts/due.py

# Rebuild the exercise table in README.md
index:
    uv run scripts/index.py
