---
name: due
description: "List exercises due for a spaced cold re-solve and suggest what to do first."
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(just due)
---

## Gate

```!
uv run scripts/meta.py gate due
```

## Due list

```!
just due
```

## Task

Summarize the due list above in a few lines:
- what is overdue (most overdue first);
- what is due today;
- what comes up this week.

Recommend one to start with, preferring the most overdue, and among equals the one whose interval is shortest (least consolidated). To start a re-solve: `just revisit <path>` then `/start <lang> <slug>`. Change nothing.
