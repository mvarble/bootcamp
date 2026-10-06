---
name: compare
description: "For a referenced exercise, generate figures and tables from .meta/bench/ and write analysis/comparison.md."
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(uv run scripts/bench_report.py *)
---

## Gate

```!
uv run scripts/meta.py gate compare
```

## Task

The exercise path is on the `exercise:` line in the gate output above.

1. Run `uv run scripts/bench_report.py <path>`. It regenerates `analysis/bench-tables.md` and `analysis/figures/*.png` from `.meta/bench/`.
2. Read `analysis/bench-tables.md`, mine, reference, `analysis/assessment.md`, and README.md.
3. Write `analysis/comparison.md` in **full prose**: paragraphs, not bullet dumps. Cover:
   - what the implementations do differently and why that should matter;
   - empirical scaling: the fitted slopes and whether they match the claimed complexity;
   - constant factors: means, confidence intervals, and ratios, and which differences are *claimable* (separated and beyond sd), noting any that are separated but not claimable;
   - whether any difference matters at the problem's real input sizes;
   - what I should take away.

   Embed the figures with `![…](figures/scaling.png)` and `![…](figures/constant-factor.png)` where present.
4. **Every number in the text must appear in `analysis/bench-tables.md`,** copied as written. Do not round differently, derive new numbers, or estimate. If a number you want is not there, say the data does not show it.

Do not change `exercise.toml` or any file outside `analysis/`.
