---
name: reference
description: "Deep tier: write reference.*, run the same tests and benchmarks over mine and reference, report measurable differences."
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(just check *) Bash(just stress *) Bash(just scale *) Bash(just bench *) Bash(uv run scripts/bench_report.py *)
---

## Gate

```!
uv run scripts/meta.py gate reference
```

## Task

The exercise path is on the `exercise:` line in the gate output above.

1. Run `just check <path>`. **My tests must pass before you write anything.** If they fail, stop and report.
2. Read README.md, mine, brute, generate, my tests, and `analysis/` (especially `assessment.md`).
3. Write the reference implementation in the exercise's existing `reference.*`, with the same interface as mine:
   - Python: `src/<pkg>/reference.py`;
   - Rust: `src/reference.rs`;
   - C++: `reference.hpp`, `namespace reference { struct Solution … }`, keeping it a distinct type.

   It may be asymptotically better, or the same idea with a better constant factor. If you conclude there is **no meaningful improvement**, leave `reference.*` re-exporting mine and say so. That is a valid outcome.
4. Never edit README.md, mine, brute, generate, or my tests. If you think a case is missing, add it to `analysis/proposed-tests.md` as input, expected output, and why it matters.
5. Run `just check <path>` and `just stress <path>`. The suite is instantiated for mine and reference, so both must pass.
6. Run `just scale <path>`, `just bench <path>`, then `uv run scripts/bench_report.py <path>`.
7. **Speedup claims.** Claim a speedup only where `analysis/bench-tables.md` marks the pair *claimable*: 95% CIs separated **and** the difference beyond the larger per-call standard deviation. Otherwise write "no measurable difference". Quote the numbers from that file.
8. Run `uv run scripts/meta.py set-status referenced`.

Report: what reference does differently, the slope comparison, and the claimable / not-claimable verdicts.
