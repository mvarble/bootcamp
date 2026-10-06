---
name: done
description: "Finish the active attempt: tests, stress, and scale, then record minutes and the revisit date."
argument-hint: "[minutes]"
arguments: [minutes]
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(just check *) Bash(just stress *) Bash(just scale *)
---

## Gate

```!
uv run scripts/meta.py gate done
```

## Task

The exercise path is on the `exercise:` line in the gate output above. Run these in order. **At the first failure, stop, report what failed, and change nothing.** Do not edit code or tests to make them pass; they are mine.

1. `just check <path>`: examples, edge cases, and light stress.
2. `just stress <path>`: heavy stress against brute.
3. `just scale <path>`: size sweep plus log-log fit. Keep the slope table for the report.
4. Run `uv run scripts/meta.py done`. The minutes I gave on invocation are `$minutes`: if that is a number, add `--minutes $minutes`; if it is empty, add nothing, and minutes default to the wall time since `started`.

Report in a few lines:
- minutes;
- `solved_cold`, which is true only with 0 hints;
- `revisit_on` and the interval: 14 days after a first solve, doubled after a cold re-solve, back to 14 otherwise;
- the slope table, with one sentence on whether `mine`'s slope matches the complexity claimed in README.md.

Suggest `/assess` next and `just index`.
