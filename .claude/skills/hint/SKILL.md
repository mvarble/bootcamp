---
name: hint
description: "Next graduated hint for the active exercise (nudge, then technique, then structural outline). Never code."
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(node .claude/hooks/main.ts lock *)
---

## Gate

```!
uv run scripts/meta.py gate hint && node .claude/hooks/main.ts lock ${CLAUDE_SESSION_ID}
```

## Task

Give exactly one hint, at the level named on the `next hint:` line in the gate output above.

- **Level 1 (nudge).** A question or observation that points at the property of the problem that matters. Name no technique and no data structure.
- **Level 2 (technique).** Name the technique or pattern (e.g. "prefix sums", "monotonic stack", "two pointers on a sorted array") and say in one or two sentences why it fits *this* problem. Give no steps.
- **Level 3 (structural outline).** The shape of the algorithm as 3-6 plain-language steps, plus the invariant that makes it correct. Still no code, no pseudocode, and none of their identifiers. If `analysis/hints.md` already has a level-3 hint, do not repeat it. Refine the step their current `mine` shows they are stuck on.

Use their `mine`, `brute`, and tests to aim at their actual gap. Never mention reference implementations, editorials, or the optimal complexity at level 1.

Record the hint with exactly one Bash call of this shape. The heredoc delimiter must be `EOF` on the first line and alone on the last line. Do not chain any other command; a guard blocks everything else, including reads, so this is the only tool call you may make:

    uv run scripts/meta.py record-hint --level N <<'EOF'
    HINT TEXT
    EOF

Then reply with the hint text and one line: `Recorded as hint <number> in analysis/hints.md.`
